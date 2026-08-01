# Cluster DNS

Kubernetes DNS prepája stabilné Service a Pod identities s meniacimi sa IP adresami. Keď `payments-api` volá databázovú proxy alebo keď iný workload volá Service `payments-api`, application resolver vytvorí query podľa mena, Pod `resolv.conf`, search domains a `ndots`. Query potom prejde cez cluster DNS Service k DNS serveru a prípadne ďalej k upstream resolverom.

DNS incident preto nie je iba otázka „beží CoreDNS?“. Rovnaký názov sa môže rozšíriť na iné FQDN podľa namespace, query môže ísť najprv cez niekoľko search suffixov, UDP response môže byť truncovaný a retryovaný cez TCP, cache môže držať starý alebo negatívny výsledok a Node-local dataplane môže byť chybný iba na jednej Node generation.

## Service DNS meno

Service `payments-api` v namespace `production` dostane meno:

```text
payments-api.production.svc.cluster.local
```

Z Podu v rovnakom namespace môže fungovať krátke meno:

```text
payments-api
```

Z iného namespace je bezpečnejšie použiť aspoň:

```text
payments-api.production
```

Plný cluster FQDN odstraňuje časť nejednoznačnosti, ale cluster domain nemusí byť vždy `cluster.local`. Aplikácia nemá hardcodovať doménu bez platform contractu.

## Čo vidí Pod resolver

```bash
kubectl exec -n production <pod-name> -- cat /etc/resolv.conf
```

Typický obsah môže vyzerať:

```text
nameserver 10.96.0.10
search production.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

`nameserver` smeruje na cluster DNS Service alebo Node-local cache podľa architektúry. Search list umožňuje krátke mená. `ndots:5` znamená, že meno s menej než piatimi bodkami sa najprv skúša s search suffixmi, až potom ako absolútne meno.

Pri externom mene `api.partner.example` môže resolver vytvoriť viac interných queries pred konečnou query. To zvyšuje latency a load, najmä pri chýbajúcich menách alebo vysokom QPS.

## DNS policy a config

Bežný Pod používa:

```yaml
spec:
  dnsPolicy: ClusterFirst
```

Pod s `hostNetwork: true` môže potrebovať `ClusterFirstWithHostNet`, ak má stále používať cluster DNS semantics.

Vlastné nastavenia:

```yaml
spec:
  dnsConfig:
    options:
      - name: ndots
        value: "2"
```

Zmena `ndots` má cluster-wide a application-specific trade-offs. Nižšia hodnota môže znížiť search queries pre external FQDN-like mená, ale zmeniť resolution krátkych names. Nemá sa aplikovať plošne bez merania.

## CoreDNS a Kubernetes plugin

CoreDNS typicky sleduje Services, EndpointSlices a Pods cez Kubernetes API a odpovedá pre cluster zones. Jeho ConfigMap definuje plugins, forwarding, caching, logging a health.

```bash
kubectl get deployment,service,configmap -n kube-system \
  -l k8s-app=kube-dns
```

Label a názvy sa môžu líšiť podľa distribúcie. Over actual cluster objects.

CoreDNS Pod môže byť Ready, ale mať stale informer cache, upstream timeout alebo vysokú CPU throttling. Cluster DNS Service môže mať správne endpoints, no Service dataplane na jednom Node-e môže byť chybný.

## Service a headless responses

ClusterIP Service DNS typicky vracia Service ClusterIP. Headless Service vracia endpoint addresses podľa records a readiness semantics.

```bash
kubectl run dns-debug --rm -it --restart=Never \
  --image=busybox:1.36 -n production -- nslookup payments-api
```

BusyBox resolver tools majú obmedzenia. Pre detailnú diagnostiku je vhodný image s `dig`:

```bash
dig payments-api.production.svc.cluster.local A
dig payments-api.production.svc.cluster.local AAAA
```

DNS odpoveď pre Service nepreukazuje funkčný backend. A record môže byť správny, ale Service path alebo application port zlyhávať.

## Pod records a StatefulSet

StatefulSet s headless Service poskytuje stabilné per-Pod names, napríklad:

```text
settlement-ledger-0.settlement-ledger.production.svc.cluster.local
```

Record identifikuje ordinal endpoint. Neznamená, že člen je leader, caught up alebo ready pre write traffic. Aplikácia musí riešiť role a membership.

Pod hostname/subdomain records závisia od Pod specu, Service a readiness publication policy. Pri očakávaní konkrétnych A/AAAA records čítaj actual EndpointSlice a DNS odpoveď.

## SRV records

Named Service ports môžu vytvoriť SRV records:

```text
_http._tcp.payments-api.production.svc.cluster.local
```

SRV odpoveď môže obsahovať port a target name. Klientská knižnica však musí SRV podporovať. Väčšina jednoduchých HTTP klientov používa A/AAAA resolution a port z URL.

## Cache a TTL

CoreDNS aj application resolver môžu cache-ovať positive a negative responses. Po zmene Service alebo EndpointSlice môže existovať krátke convergence okno.

JVM, Go, glibc, musl a language-specific resolvers majú odlišné cache a retry správanie. Aplikácia, ktorá resolve-ne hostname iba pri štarte a drží jednu IP navždy, obchádza dynamický Service model.

Pri incidentoch zachovaj:

```text
query name a type
source Pod UID a Node
resolver config
response code, answer a TTL
timestamp
CoreDNS instance
upstream resolver path
application cache behavior
```

## UDP, truncation a TCP fallback

DNS bežne používa UDP. Väčšie responses môžu byť truncované a klient má retryovať cez TCP. Firewall alebo NetworkPolicy, ktorá povoľuje iba UDP/53, môže spôsobovať intermittent failures pri väčších odpovediach.

Testuj oba protokoly:

```bash
dig payments-api.production.svc.cluster.local A
dig +tcp payments-api.production.svc.cluster.local A
```

EDNS0, MTU a fragmentácia môžu ovplyvniť UDP path. DNS failure pri veľkých external responses nemusí postihovať malé Service records.

## Upstream DNS

Queries mimo cluster zones CoreDNS typicky forwarduje podľa konfigurácie. Upstream môže byť node `/etc/resolv.conf`, cloud resolver alebo explicitná adresa.

Loop vznikne, ak CoreDNS forwarduje na resolver, ktorý query pošle späť do cluster DNS. Ďalšie problémy zahŕňajú split-horizon zones, DNSSEC, rate limiting a nedostupný upstream iba z niektorých Nodes.

```bash
kubectl get configmap -n kube-system coredns -o yaml
```

Needituj CoreDNS config počas incidentu bez preserved current generation a rollback planu. Jedna globálna zmena môže zasiahnuť celý cluster.

## NodeLocal DNSCache

Niektoré clustre používajú NodeLocal DNSCache. Pod query ide na local listener a ten cache-uje alebo forwarduje do cluster DNS.

Výhody zahŕňajú nižšiu latency a menej conntrack pressure. Nová failure boundary je však per-Node agent. Ak DNS zlyháva iba na jednom Node pool-e, porovnávaj local DNS DaemonSet, listener, config a upstream path.

## NetworkPolicy pre DNS

Default-deny egress policy musí povoliť DNS k správnemu destination a protokolu. Ak cluster používa NodeLocal DNS IP mimo bežného DNS Service selectoru, stará policy môže po platform zmene blokovať queries.

Povolenie všetkého UDP/53 do celého internetu je zbytočne široké. Policy má zodpovedať actual DNS architecture a povoľovať aj TCP fallback.

## Diagnostický postup

Pri `no such host` alebo timeout-e nezačni restartom CoreDNS. Najprv fixuj exact query a source Pod.

```bash
kubectl get pod -n production <pod-name> -o wide
kubectl exec -n production <pod-name> -- cat /etc/resolv.conf
```

Potom testuj:

```text
krátke meno
namespace-qualified meno
plné FQDN
A a AAAA
UDP a TCP
cluster Service meno
external meno
rovnaký test z affected a unaffected Node-u
```

Čítaj DNS Service a endpoints:

```bash
kubectl get service -n kube-system kube-dns -o yaml
kubectl get endpointslices -n kube-system \
  -l kubernetes.io/service-name=kube-dns -o yaml
```

Názov Service môže byť odlišný podľa distribúcie.

## Incident: external API malo vysokú latency bez DNS errors

`payments-api` volala `risk.partner.example`. Meno obsahovalo dve bodky a Pod mal `ndots:5`. Resolver pred external query skúšal viac interných search variants. Negatívne odpovede mali vysokú latency pre preťažený CoreDNS a každý request vytvoril niekoľko queries.

Application metrics ukazovali dependency latency, nie explicitné DNS failures. Oprava použila absolútne FQDN s trailing dot podľa klientského contractu a znížila zbytočné lookups cez connection reuse. Skorší control je DNS query telemetry a resolver-aware performance test.

## Incident: DNS fungovalo cez UDP, nie cez TCP

Malé Service queries fungovali. Veľká external TXT odpoveď bola truncovaná, klient retryol cez TCP a NetworkPolicy TCP/53 blokovala. Aplikácia hlásila intermittent resolver timeout.

Oprava doplnila presný TCP aj UDP egress k DNS destination. Recovery overila `dig` aj `dig +tcp` z affected Podu a forbidden external DNS flows zostali blokované.

## Incident: iba nový Node pool nevedel resolve-nuť mená

CoreDNS Deployment a Service boli zdravé. Pods na starých Nodes fungovali. Nová NodeLocal DNSCache revision počúvala na inej local IP, ale kubelet `clusterDNS` stále vkladal starú adresu do `resolv.conf`.

Root cause bol Node image/kubelet configuration contract, nie CoreDNS. Containment cordonovalo novú cohortu a replacement image zladil kubelet aj DaemonSet konfiguráciu.

## Model, ktorý si treba odniesť

Cluster DNS je query path cez Pod resolver config, search/ndots, cluster DNS Service, CoreDNS alebo NodeLocal cache, Kubernetes records, upstream resolver a application cache. Zelený DNS Pod alebo správny A record nepreukazuje celý request. Diagnostika musí fixovať exact query, source Pod/Node, protocol, response a TTL.

## Referencie

- [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [Customizing DNS Service](https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/)
- [Using NodeLocal DNSCache](https://kubernetes.io/docs/tasks/administer-cluster/nodelocaldns/)
