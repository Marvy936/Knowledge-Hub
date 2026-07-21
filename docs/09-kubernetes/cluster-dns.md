# Cluster DNS

Cluster DNS poskytuje service discovery pre Kubernetes Services a vybrané Pod identity. Kubelet konfiguruje DNS resolver v Pode a cluster DNS add-on, typicky CoreDNS, odpovedá na cluster-local mená alebo forwarduje external queries upstream resolverom. DNS vytvára stabilné mená, ale negarantuje readiness backendu, funkčný Service dataplane ani dostupnosť aplikácie.

## 1. Mentálny model

Zjednodušený request flow:

```text
application resolver
→ /etc/resolv.conf v Pode
→ cluster DNS Service IP
→ CoreDNS replicas
→ kubernetes plugin alebo upstream DNS
→ odpoveď a cache
```

Pri Service requeste pokračuje flow:

```text
DNS meno
→ Service ClusterIP alebo headless endpoint addresses
→ Service dataplane
→ EndpointSlice backend
→ Pod application
```

DNS a Service forwarding sú samostatné vrstvy.

## 2. Cluster DNS add-on

Cluster DNS je add-on, nie súčasť `kube-apiserver` procesu. Bežne pozostáva z:

- CoreDNS Deploymentu,
- Service typu ClusterIP, často pomenovaného `kube-dns`,
- ConfigMapu s Corefile configuration,
- ServiceAccount/RBAC,
- autoscaling a monitoring podľa platformy.

Ak API funguje, ale CoreDNS Pods alebo DNS Service zlyhajú, workloads nemusia resolve-nuť Service names ani external domains.

## 3. Service DNS names

Service `web` v namespace `production` má typické meno:

```text
web.production.svc.cluster.local
```

Časti:

```text
<service>.<namespace>.svc.<cluster-domain>
```

Cluster domain nemusí byť `cluster.local`; závisí od cluster konfigurácie.

Pod v rovnakom namespace môže používať krátke meno:

```text
web
```

Pod v inom namespace typicky používa:

```text
web.production
```

alebo plné FQDN.

## 4. Search domains a `ndots`

Typický `/etc/resolv.conf` v Pode:

```text
nameserver 10.96.0.10
search production.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

Resolver môže neplné meno skúšať s viacerými search suffixes.

Príklad query:

```text
api.example.com
```

Pri vysokom `ndots` môže resolver najprv skúšať viac cluster-local variantov a až potom absolute meno. To zvyšuje:

- počet DNS queries,
- latency pri negatívnych odpovediach,
- CoreDNS load,
- vplyv packet lossu.

Plné absolute meno s trailing dot môže obísť search expansion:

```text
api.example.com.
```

Application/library behavior však over v konkrétnom runtime.

## 5. ClusterIP Service records

Bežný Service dostane A a/alebo AAAA record, ktorý resolve-ne na Service ClusterIP/clusterIPs.

```text
web.production.svc.cluster.local
→ 10.96.120.15
```

DNS nevracia priamo Pod IPs pre bežný ClusterIP Service. Backend selection vykonáva Service dataplane podľa EndpointSlices.

## 6. Headless Service records

Headless Service má:

```yaml
spec:
  clusterIP: None
```

Jeho DNS record typicky vracia IP adresy ready endpointov namiesto jednej ClusterIP.

```text
database.production.svc.cluster.local
→ 10.244.1.20
→ 10.244.2.31
```

Client nesie väčšiu zodpovednosť za:

- address selection,
- connection pooling,
- failover,
- TTL/cache behavior,
- multiple A/AAAA answers.

Poradie DNS answers nie je garantovaný load-balancing alebo leader-election contract.

## 7. SRV records

Named Service ports môžu vytvoriť SRV records.

Service port:

```yaml
ports:
  - name: grpc
    protocol: TCP
    port: 9090
```

Query:

```text
_grpc._tcp.web.production.svc.cluster.local
```

SRV odpoveď obsahuje target name a port. Pri headless Service môže smerovať na jednotlivé Pod hostnames.

Application musí SRV lookup explicitne podporovať; bežný HTTP client ho nemusí používať automaticky.

## 8. Pod hostname a subdomain

Pod môže definovať:

```yaml
spec:
  hostname: db-0
  subdomain: database
```

Ak existuje headless Service `database` v rovnakom namespace, cluster DNS môže publikovať FQDN:

```text
db-0.database.production.svc.cluster.local
```

StatefulSet používa podobný model na stabilné per-ordinal DNS identity.

Stabilné DNS meno neznamená stabilný Pod UID alebo process. Po replacement-e môže rovnaké logical meno smerovať na nový Pod.

## 9. Pod DNS policy

### `ClusterFirst`

Default pre bežné Pods. Cluster-local queries rieši cluster DNS a ostatné sa forwardujú upstream.

```yaml
spec:
  dnsPolicy: ClusterFirst
```

### `Default`

Pod zdedí resolver model Node-u podľa kubelet/platform semantics.

### `ClusterFirstWithHostNet`

Používa sa pri `hostNetwork: true`, ak Pod stále potrebuje cluster DNS behavior.

```yaml
spec:
  hostNetwork: true
  dnsPolicy: ClusterFirstWithHostNet
```

### `None`

Pod ignoruje štandardné DNS nastavenie a používa explicitný `dnsConfig`.

```yaml
spec:
  dnsPolicy: None
  dnsConfig:
    nameservers:
      - 192.0.2.53
    searches:
      - example.internal
```

`None` prenáša plnú zodpovednosť za resolver configuration na workload ownera.

## 10. `dnsConfig`

`dnsConfig` môže doplniť:

- nameservers,
- search domains,
- resolver options.

```yaml
spec:
  dnsConfig:
    options:
      - name: ndots
        value: "2"
```

Zmena `ndots` môže znížiť query amplification, ale môže zmeniť resolution semantics pre krátke mená. Testuj:

- same-namespace Service names,
- cross-namespace names,
- external domains,
- trailing-dot behavior,
- library-specific resolver caching.

## 11. CoreDNS a Kubernetes plugin

CoreDNS typicky používa `kubernetes` plugin na sledovanie Services, EndpointSlices, Pods alebo Namespaces podľa configuration.

Corefile môže obsahovať napríklad:

```text
.:53 {
    errors
    health
    ready
    kubernetes cluster.local in-addr.arpa ip6.arpa
    forward . /etc/resolv.conf
    cache 30
    loop
    reload
    loadbalance
}
```

Význam configuration závisí od plugin verzie a platformy. Corefile je production configuration s rollout, validation a rollback požiadavkami.

## 12. Upstream forwarding

External queries CoreDNS forwarduje upstream resolverom.

Failure vrstvy:

- nesprávny upstream v Node `/etc/resolv.conf`,
- systemd-resolved stub loop,
- nedostupný corporate/VPN DNS,
- firewall alebo NetworkPolicy blokuje UDP/TCP 53,
- DNSSEC/EDNS/fragmentation problémy,
- split-horizon domain routing,
- upstream rate limiting.

Cluster-local mená môžu fungovať, zatiaľ čo external resolution zlyháva, alebo naopak.

## 13. UDP a TCP

DNS bežne používa UDP, ale pri veľkej alebo truncated odpovedi môže klient retryovať cez TCP.

Firewall a NetworkPolicy musia podľa potreby povoliť:

- UDP/53,
- TCP/53.

Symptóm „malé DNS odpovede fungujú, veľké nie“ môže súvisieť s:

- blokovaným TCP fallbackom,
- MTU/fragmentation,
- EDNS behavior,
- starým resolverom alebo libc implementáciou.

## 14. Caching

Caching existuje na viacerých vrstvách:

- application/library,
- libc/runtime,
- local caching agent,
- CoreDNS cache,
- upstream resolver.

Dôsledky:

- DNS zmena sa neprejaví okamžite,
- negative cache môže predĺžiť NXDOMAIN incident,
- dlhé persistent connections obídu nové DNS lookupy,
- TTL nie je garancia okamžitého connection failoveru.

Pri diagnostike testuj nový lookup aj nový connection, nie iba existujúci process pool.

## 15. NodeLocal DNSCache

Niektoré clustre používajú NodeLocal DNSCache. Pod query smeruje na local node agent, ktorý cache-uje a forwarduje do cluster DNS.

Výhody:

- nižšia latency,
- menej conntrack/UDP pressure,
- lokálne caching,
- izolovanejší failure behavior.

Riziká:

- DaemonSet/node-local agent failure,
- rozdielna configuration medzi Nodes,
- local bind/IP rules,
- ďalšia cache vrstva,
- problém iba na konkrétnych Nodes.

Over reálnu cluster implementation; nepredpokladaj, že každý cluster používa rovnaký DNS datapath.

## 16. DNS a readiness

DNS record pre bežný Service smeruje na ClusterIP bez ohľadu na počet backendov. Ak Service nemá ready EndpointSlices:

- DNS stále môže úspešne vrátiť ClusterIP,
- connection môže timeoutovať alebo byť odmietnutá podľa dataplane,
- problém nie je DNS.

Pri headless Service DNS answers typicky viac súvisia s endpoint readiness, ale publication policy môže zmeniť `publishNotReadyAddresses`.

## 17. DNS security

Riziká:

- DNS spoofing alebo kompromitovaný cluster DNS,
- exfiltrácia cez DNS queries,
- citlivé mená v query logs,
- broad ability meniť Services/EndpointSlices,
- malicious namespace/service names ovplyvňujúce search resolution,
- upstream poisoning alebo nesprávny split DNS,
- plaintext DNS bez aplikačnej identity.

DNS nie je authentication. Aj po správnom resolve musí application používať TLS/mTLS a overiť server identity.

## 18. Observability

```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl get service -n kube-system kube-dns
kubectl get endpointslice -n kube-system \
  -l kubernetes.io/service-name=kube-dns
kubectl logs -n kube-system deployment/coredns
kubectl get configmap -n kube-system coredns -o yaml
```

Z test Podu:

```bash
cat /etc/resolv.conf
getent hosts web
nslookup web.production.svc.cluster.local
dig A web.production.svc.cluster.local
dig SRV _grpc._tcp.web.production.svc.cluster.local
```

Tools nemusia byť v minimal image. Použi schválený diagnostic Pod alebo ephemeral container.

## 19. Systematický troubleshooting

### Krátke meno zlyhá, FQDN funguje

Over Pod namespace, search list, `ndots`, `dnsPolicy` a `dnsConfig`.

### Cluster-local mená fungujú, external domains zlyhávajú

Over CoreDNS forward plugin, upstream resolver, Node `/etc/resolv.conf`, firewall, VPN/split DNS a CoreDNS logs.

### External mená fungujú, Service names zlyhávajú

Over Kubernetes plugin, API watch/RBAC, Service object, cluster domain a CoreDNS readiness.

### DNS funguje iba na niektorých Nodes

Over NodeLocal DNSCache, kubelet `resolvConf`, node firewall/routes, CNI a per-node agent logs.

### DNS timeoutuje pod loadom

Over CoreDNS CPU/memory, replica count, query rate, cache hit ratio, conntrack, packet loss, upstream latency a autoscaling.

### NXDOMAIN po vytvorení Service

Over namespace/name, Service existence, CoreDNS API watch, negative cache a či query používa správny cluster domain.

### Meno sa resolve-ne, ale application sa nepripojí

Pokračuj na Service, EndpointSlice, NetworkPolicy, targetPort a application listen socket. DNS vrstva už prešla.

### Veľké odpovede zlyhávajú

Over TCP/53 fallback, MTU, fragmentation, EDNS a resolver implementation.

## 20. `systemd-resolved` a Node resolver

Na niektorých Linux distribúciách `/etc/resolv.conf` smeruje na local stub. Nesprávny kubelet `resolvConf` môže vytvoriť forwarding loop:

```text
CoreDNS
→ Node stub resolver
→ cluster DNS
→ CoreDNS
```

Over:

```bash
readlink -f /etc/resolv.conf
cat /run/systemd/resolve/resolv.conf
```

Kubelet musí používať správny upstream resolver file podľa distribúcie a cluster bootstrap nástroja.

## 21. Resolver limits

Host a container runtime môžu mať limity na:

- počet `nameserver` entries,
- počet search domains,
- celkovú dĺžku search line,
- retries/timeouts,
- hostname/FQDN dĺžku,
- response size a TCP fallback.

Kubernetes/kubelet môže zlučovať Node a cluster DNS configuration. Pri prekročení limitu sleduj Pod Events a výsledný `/etc/resolv.conf`.

## 22. Anti-patterny

### Hard-coded Service ClusterIP

Obchádza DNS identity a komplikuje migration/restore.

### FQDN všade bez pochopenia namespace boundary

Znižuje portability medzi namespaces a prostrediami.

### Krátke external meno s vysokým `ndots`

Vytvára viac negatívnych cluster-local queries.

### DNS ako health check backendu

Úspešný lookup nepreukazuje ready endpoints ani application health.

### Povolený iba UDP/53

TCP fallback môže zlyhať.

### Ručná editácia CoreDNS bez validation a rollbacku

Môže odstaviť service discovery pre celý cluster.

### Application cacheuje DNS navždy

Po backend alebo Service zmene používa stale address.

### Debugging iba cez `ping`

ICMP nemusí byť povolené a neoveruje Service port/protocol.

## 23. Kontrolné otázky

1. Akú úlohu má kubelet pri Pod DNS configuration?
2. Ako vyzerá FQDN Service-u?
3. Ako sa líši DNS record ClusterIP a headless Service-u?
4. Načo slúžia search domains a `ndots`?
5. Kedy vznikajú SRV records?
6. Aký je rozdiel medzi `ClusterFirst`, `Default`, `ClusterFirstWithHostNet` a `None`?
7. Prečo treba povoliť UDP aj TCP port 53?
8. Ako odlíšiš cluster-local a upstream DNS failure?
9. Prečo DNS success nepreukazuje fungujúcu application?
10. Ako diagnostikuješ DNS problém iba na jednom Node-e?

## Glossary impact

Relevantné pojmy: cluster DNS, CoreDNS, cluster domain, Service FQDN, DNS search domain, `ndots`, ClusterIP DNS record, headless Service DNS, SRV record, Pod hostname/subdomain, DNS policy, `dnsConfig`, upstream forwarding, negative caching, NodeLocal DNSCache, DNS TCP fallback a resolver forwarding loop.

## Oficiálna dokumentácia

- [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [Configure DNS for a Cluster](https://kubernetes.io/docs/tasks/access-application-cluster/configure-dns-cluster/)
- [Debugging DNS Resolution](https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/)
- [Customizing DNS Service](https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/)
