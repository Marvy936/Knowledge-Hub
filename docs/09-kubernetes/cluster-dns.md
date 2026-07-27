# Cluster DNS

Cluster DNS je resolver a discovery control chain medzi application lookup intentom a adresou, ktorú klient následne použije. Kubelet vytvára Pod resolver configuration, cluster DNS Service smeruje query na CoreDNS alebo inú implementation, DNS server sleduje Kubernetes API alebo forwarduje upstream a odpoveď prechádza viacerými cache vrstvami. Úspešný lookup však stále nepreukazuje funkčný Service dataplane ani application outcome.

Dominantný lifecycle:

```text
application lookup intent a exact query name/type
→ Pod UID, namespace, dnsPolicy a generated resolv.conf
→ search-domain a ndots expansion
→ NodeLocal alebo direct cluster-DNS path
→ kube-dns Service a EndpointSlice cohort
→ CoreDNS instance a loaded Corefile generation
→ Kubernetes API watch alebo upstream forwarding
→ response, TTL alebo negative result
→ node/runtime/application cache
→ address selection a fresh connection
→ Service/EndpointSlice alebo external path
→ verified application request
```

Kapitola používa Atlas Payments. Pod `payments-api` potrebuje resolve-nuť:

```text
ledger-db.production.svc.cluster.local
vault.prod.example
```

Prvé meno je cluster-local Service discovery. Druhé je external/split-horizon name forwardované upstream. Acceptance vyžaduje nielen správne DNS answers, ale aj fresh connection a úspešný payment request.

## 1. DNS subject musí byť presný

Pri incidentoch fixuj:

```text
cluster domain a DNS implementation
Pod UID, namespace, Node a network namespace
dnsPolicy a dnsConfig
actual /etc/resolv.conf generation
exact query string, trailing dot a record type
search expansion attempts a ndots
NodeLocal DNSCache instance/generation, ak existuje
kube-dns Service UID/ClusterIP a EndpointSlice cohort
CoreDNS Pod UID, image a loaded Corefile hash
Kubernetes API watch/resource generation alebo upstream resolver
response code, answer, authority, TTL a latency
application/runtime cache generation
selected address a subsequent connection subject
business request/operation ID
```

`nslookup web` a `dig web.production.svc.cluster.local.` nie sú rovnaký query subject.

## 2. Pod resolver configuration vzniká pri Pod lifecycle-e

Kubelet vytvára resolver config podľa:

- cluster DNS Service addresses;
- cluster domain;
- Pod namespace;
- `dnsPolicy`;
- `dnsConfig`;
- Node resolver configuration;
- runtime/OS resolver limits.

Typický Pod:

```text
nameserver 10.96.0.10
search production.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

Source Pod spec, kubelet configuration a actual `/etc/resolv.conf` sú odlišné states. Diagnostikuj actual file v affected Pode.

## 3. DNS policies menia upstream a search contract

### `ClusterFirst`

Cluster-local queries smerujú na cluster DNS; ostatné sa typicky forwardujú upstream.

### `Default`

Pod používa Node resolver model podľa kubelet/platform semantics.

### `ClusterFirstWithHostNet`

Host-network Pod si zachová cluster DNS behavior.

### `None`

Workload owner definuje nameservers/search/options cez `dnsConfig`.

`dnsPolicy: None` je ownership transfer. Platform už neposkytuje bežný service-discovery contract automaticky.

## 4. Search expansion a `ndots`

Resolver môže krátke alebo neabsolútne meno skúšať s viacerými suffixmi.

Query:

```text
vault.prod.example
```

môže pri vysokom `ndots` viesť k pokusom:

```text
vault.prod.example.production.svc.cluster.local
vault.prod.example.svc.cluster.local
vault.prod.example.cluster.local
vault.prod.example
```

Dôsledky:

- viac queries;
- negative-cache load;
- vyššia latency;
- väčší dopad packet lossu;
- možný namespace/search collision;
- odlišné behavior medzi runtime knižnicami.

Absolute FQDN s trailing dot obchádza search expansion, ak to resolver/library podporuje podľa očakávania.

## 5. Service DNS generation

Pre ClusterIP Service:

```text
payments-api.production.svc.<cluster-domain>
→ Service ClusterIP
```

DNS server sleduje Service API state. Backend Pods nie sú priamo v bežnej ClusterIP A/AAAA odpovedi; endpoint selection vykonáva Service dataplane.

Preto DNS record môže byť validný aj keď Service nemá ready EndpointSlices.

## 6. Headless Service discovery

Headless Service typicky publikuje endpoint addresses namiesto jednej ClusterIP.

```text
ledger-db.production.svc...
→ 10.244.1.20
→ 10.244.2.31
→ 10.244.3.44
```

Client preberá:

- address selection;
- multi-answer behavior;
- TTL/cache;
- failover;
- connection pooling;
- role/membership validation.

DNS answer order nie je leader-election ani quorum contract. Stabilné StatefulSet hostname nie je stabilný Pod UID ani fencing token.

## 7. SRV records sú port discovery contract

Named Service port môže mať SRV record:

```text
_grpc._tcp.payments-api.production.svc.cluster.local
```

SRV poskytuje target a port metadata. Application ho musí explicitne používať. Bežný HTTP client automaticky neprepne na SRV discovery iba preto, že record existuje.

## 8. CoreDNS Kubernetes watch path

CoreDNS Kubernetes plugin typicky sleduje Services, EndpointSlices, Pods alebo Namespaces podľa configuration.

```text
API watch/list
→ internal DNS object cache
→ authoritative cluster-local answer
```

Failure boundaries:

- RBAC/list-watch zlyhanie;
- API connectivity;
- stale informer/cache;
- nesprávny cluster domain;
- Corefile syntax alebo plugin order;
- partial CoreDNS rollout;
- negative cache po oneskorenej object observation.

`CoreDNS Pod Ready` nepreukazuje, že loaded data generation obsahuje najnovší Service.

## 9. kube-dns Service path

Pods typicky neposielajú query priamo na konkrétny CoreDNS Pod. Používajú Service ClusterIP, často s názvom `kube-dns`.

```text
Pod resolver
→ kube-dns ClusterIP:53
→ node Service dataplane
→ CoreDNS EndpointSlice backend
```

DNS failure môže teda patriť do Service dataplane, EndpointSlice alebo NetworkPolicy boundary, aj keď CoreDNS application je zdravá.

## 10. NodeLocal DNSCache pridáva node-specific generation

Pri NodeLocal DNSCache:

```text
Pod
→ local DNS IP/agent na Node-e
→ local cache
→ cluster DNS alebo upstream
```

Výhody zahŕňajú nižšiu latency a menší UDP/conntrack pressure. Zároveň vzniká:

- per-Node config drift;
- per-Node cache state;
- local bind/routing boundary;
- ďalší DaemonSet lifecycle;
- failure iba na jednom Node-e.

DNS observation musí potvrdiť effective path v konkrétnom clustri.

## 11. Upstream forwarding je samostatný dependency graph

External/split DNS:

```text
CoreDNS forward/stubDomains
→ Node alebo explicitný upstream resolver
→ corporate/cloud authoritative chain
→ response
```

Failure boundaries:

- Node `/etc/resolv.conf` ukazuje na local stub loop;
- corporate resolver je nedostupný;
- split-horizon zone smeruje nesprávne;
- firewall/NetworkPolicy blokuje UDP/TCP 53;
- upstream rate limit;
- DNSSEC/EDNS/fragmentation;
- clock alebo trust issue pri encrypted upstream implementation;
- partial CoreDNS config rollout.

Cluster-local names môžu fungovať, zatiaľ čo external names zlyhávajú, a naopak.

## 12. UDP, truncation a TCP fallback

DNS často začína cez UDP. Pri truncated alebo veľkej odpovedi klient môže prejsť na TCP.

```text
UDP query
→ TC bit alebo response-size limit
→ TCP/53 connection
→ full answer
```

Povolený iba UDP/53 vytvára symptom „malé answers fungujú, veľké timeoutujú“. MTU, fragmentation, EDNS a middlebox behavior patria do rovnakého path subjectu.

## 13. Cache je viacvrstvový state

Cache môže existovať v:

```text
application/library
runtime/libc
local DNS agent
CoreDNS
upstream recursive resolver
client-side connection pool
```

Rozlišuj:

- positive cache;
- negative cache/NXDOMAIN;
- TTL expiry;
- serve-stale behavior podľa implementation;
- existing connection bez nového lookupu;
- process, ktorý cacheuje navždy.

Po DNS zmene testuj fresh lookup aj fresh connection. Starý HTTP/gRPC pool môže obísť nový DNS result.

## 14. NXDOMAIN je výsledok s lifecycle-om

NXDOMAIN po query môže byť správny pre observation time T1. Ak Service vznikne v T2, negative cache môže starý verdict držať do expiry.

```text
query pred create
→ NXDOMAIN cache
→ Service create
→ API/CoreDNS už current
→ client/local cache stále vracia NXDOMAIN
```

Random CoreDNS restart môže zmazať jednu cache vrstvu, ale nie application, NodeLocal ani upstream cache. Recovery musí identifikovať cache ownera.

## 15. DNS answer a application connection

Pre ClusterIP Service:

```text
DNS answer
→ Service VIP
→ node dataplane
→ EndpointSlice
→ backend socket
```

Pre external host:

```text
DNS answer
→ external address
→ route/firewall/TLS
→ service
```

Ak meno resolve-ne, ale connection zlyhá, DNS vrstva môže byť už úspešná. Pokračuj na actual selected address a connection path.

## 16. Resolver library behavior

Application runtime môže:

- cacheovať dlhšie než DNS TTL;
- ignorovať viac answers;
- preferovať IPv6 a pomaly fallbackovať na IPv4;
- nepodporovať SRV;
- používať vlastný async resolver;
- meniť retry/timeouts;
- nečítať zmenený `/etc/resolv.conf` počas process lifecycle-u.

DNS acceptance sa preto testuje v rovnakom runtime/library path-e ako production application, nie iba cez `dig`.

## 17. Corefile je versionovaný platform configuration subject

Corefile určuje plugin chain, cache, forwarding, rewrites, logging a reload behavior.

```text
source Corefile generation
→ ConfigMap object
→ CoreDNS Pod delivery
→ process-loaded config hash
→ readiness
→ query behavior
```

ConfigMap update nepreukazuje, že všetky CoreDNS Pods načítali rovnakú configuration. Použi validation, rollout/reload evidence a per-Pod loaded hash.

## 18. `systemd-resolved` forwarding loop

Node `/etc/resolv.conf` môže ukazovať na local stub, ktorý nie je vhodný ako CoreDNS upstream.

Loop:

```text
CoreDNS
→ Node stub
→ cluster DNS Service
→ CoreDNS
```

Symptómy môžu byť timeouty, `SERVFAIL`, vysoká query rate a self-amplification. Over actual symlink target a kubelet/CoreDNS upstream file; neopravuj to zmenou application FQDN.

## 19. DNS security boundary

DNS nie je authentication ani authorization.

Riziká:

- kompromitovaný DNS server alebo upstream;
- Service/EndpointSlice mutation meniaca answer alebo downstream path;
- exfiltration cez query names;
- citlivé names v logs;
- search-path collision;
- spoofing pri plaintext DNS path;
- broad CoreDNS ServiceAccount/RBAC;
- untrusted Corefile plugin/config mutation.

Application musí po resolve overiť server identity cez TLS/mTLS alebo iný protocol contract.

## 20. Worked failure: krátke meno zlyhá, FQDN funguje

Pod mal `dnsPolicy: None` a custom search list bez `production.svc.cluster.local`.

```text
query ledger-db
→ search list bez namespace suffixu
→ NXDOMAIN

query ledger-db.production.svc.cluster.local.
→ authoritative answer
```

CoreDNS bolo zdravé. Finding bol v Pod resolver generation, nie v DNS serveri.

## 21. Worked failure: nový Service, stale negative cache

Application sa pokúsila resolve-nuť `risk-api` pred jeho vytvorením. JVM resolver držal NXDOMAIN dlhšie než CoreDNS negative TTL.

Service aj CoreDNS watch boli current, ale application process stále zlyhával. Recovery vyžadovala process/runtime cache policy a controlled reconnect, nie CoreDNS restart.

## 22. Worked failure: external DNS zlyháva, cluster-local funguje

CoreDNS Kubernetes plugin odpovedal správne, ale forward plugin smeroval na Node stub, ktorý vytvoril loop.

```text
cluster-local query
→ kubernetes plugin
→ success

external query
→ forward
→ Node stub
→ cluster DNS
→ loop/SERVFAIL
```

Rozdelenie query namespaces bolo diskriminačný dôkaz.

## 23. Worked failure: DNS iba na jednom Node-e

Node N9 mal NodeLocal DNSCache s old Corefile a stale upstream address. Pody na iných Nodes používali current generation.

Cluster-wide CoreDNS metrics vyzerali zdravo. Per-Node resolver path a local agent hash odhalili drift.

## 24. Worked failure: UDP funguje, TCP fallback blokovaný

Malé A records fungovali. Veľká TXT/DNSSEC odpoveď bola truncated a TCP/53 blokovala NetworkPolicy.

Symptóm sa javil domain-specific. Packet observation ukázal UDP response s truncation a chýbajúci TCP handshake.

## 25. Causal troubleshooting walkthrough: intermittent NXDOMAIN a timeout iba na jednom Node-e

Symptóm:

```text
Payments Pods na N1/N2 fungujú
Pod P52 na N3 občas dostane NXDOMAIN pre ledger-db
občas timeout pre vault.prod.example
restart P52 dočasne pomôže
Service a external DNS existujú
```

### 1. Zafixuj resolver a query subject

```text
Pod UID P52, Node N3, namespace a creation time
dnsPolicy/dnsConfig a actual resolv.conf
exact query names, trailing dot a A/AAAA/SRV type
search expansion sequence a ndots
NodeLocal DNSCache Pod UID/config hash na N3
kube-dns Service UID a EndpointSlice cohort
CoreDNS Pod/config generations
Kubernetes Service UID/resourceVersion
upstream resolver address/generation
response code, TTL, latency a packet tuple
application runtime/cache a fresh-connection behavior
operation ID pay-8842
```

### 2. Konkurenčné hypotézy

1. NodeLocal DNSCache na N3 má stale config/cache;
2. N3 kubelet generuje nesprávny `resolv.conf`;
3. CNI/Service dataplane z N3 stráca DNS packets;
4. NetworkPolicy blokuje TCP fallback alebo časť DNS pathu;
5. CoreDNS cohort je mixed a LB selection koreluje s failure;
6. CoreDNS API watch zaostáva pre Service record;
7. upstream forwarding zlyháva iba cez N3 local agent;
8. application negative cache prežíva DNS recovery;
9. ndots/search expansion vytvára query amplification a timeout;
10. IPv6 preference vyberá nefunkčnú family.

### 3. Diskriminačné observation points

- porovnaj actual `/etc/resolv.conf` na P52 a healthy Pode;
- testuj absolute FQDN a short name oddelene;
- testuj cluster-local a external query oddelene;
- identifikuj DNS server IP, na ktorý packet skutočne ide;
- porovnaj NodeLocal agent UID/config hash/cache metrics medzi Nodes;
- sleduj UDP query/response a prípadný TCP fallback;
- dotazuj konkrétnu CoreDNS repliku na oddelenie Service LB pathu;
- skontroluj CoreDNS Kubernetes watch a upstream latency;
- porovnaj fresh diagnostic process s long-lived application;
- testuj A a AAAA selection a následnú connection.

### 4. Containment

- cordon N3 pre nové application Pods, ak resolver path je nebezpečný;
- zachovaj resolv.conf, local-agent config/cache metrics a packet evidence;
- nereštartuj všetky CoreDNS a NodeLocal Pods naraz;
- nehardcoduj Service ClusterIP alebo external IP do application configu;
- obmedz retry/query amplification;
- pri NXDOMAIN nevytváraj broad search-domain workaround.

### 5. Authoritative recovery

Pri stale NodeLocal generation:

1. oprav source configuration alebo rollout ownership;
2. nahraj reviewed generation na N3;
3. over local bind, upstream a cache state;
4. testuj internal aj external queries;
5. uncordon N3 až po resolver a application canary;
6. dokonči fleet rollout a odstráň stale generations.

Iné findings oprav v kubelet resolver, CoreDNS, NetworkPolicy, upstream alebo application cache boundary.

### 6. Over pôvodný outcome

Potvrď:

- P52 replacement má accepted resolver generation;
- short a FQDN query majú očakávané semantics;
- `ledger-db` answer patrí current Service/endpoint generation;
- `vault.prod.example` používa correct split-horizon/upstream answer;
- UDP aj TCP fallback prejdú;
- A/AAAA behavior zodpovedá supported family contractu;
- fresh connection dosiahne správny Service/external endpoint;
- pay-8842 prejde presne raz;
- negative/stale cache sa neobjaví pri ďalšom Service rollout-e.

### 7. Posuň control skôr

Pridaj:

- per-Pod resolver-generation inventory;
- per-Node DNS canary pre internal/external/FQDN/short/TCP tests;
- loaded Corefile hash telemetry;
- NodeLocal fleet drift alert;
- ndots/query-amplification budget;
- application resolver/cache integration test;
- Kubernetes API watch freshness metric;
- upstream/split-DNS synthetic;
- DNS-to-fresh-connection business synthetic.

## 26. Observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Intent | lookup subject | exact name, absolute/relative, type, expected owner |
| Pod | resolver generation | UID, namespace, dnsPolicy/config, resolv.conf |
| Expansion | search/ndots attempts | query sequence, latency, NXDOMAINs |
| Node-local | Node DNS generation | agent UID/config, cache, bind, upstream |
| DNS Service | kube-dns Service/EndpointSlices | VIP, ready CoreDNS cohort, dataplane path |
| CoreDNS | Pod + loaded Corefile | plugin chain, watch state, cache, errors |
| Kubernetes data | Service/EndpointSlice generation | API visibility, cluster domain, records |
| Upstream | forwarding subject | resolver, split zone, latency, UDP/TCP |
| Cache | runtime/cache generation | TTL, negative state, process lifetime |
| Connection | selected address/path | family, socket, Service/LB/backend |
| Business | request/operation ID | correct dependency, response, no duplicate |

## 27. Referenčné príkazy

```bash
kubectl get service kube-dns -n kube-system -o yaml
kubectl get endpointslice -n kube-system \
  -l kubernetes.io/service-name=kube-dns -o yaml
kubectl get pods -n kube-system -l k8s-app=kube-dns -o wide
kubectl get configmap coredns -n kube-system -o yaml
kubectl logs -n kube-system deployment/coredns
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Z affected Podu alebo schváleného diagnostic Podu:

```bash
cat /etc/resolv.conf
getent hosts ledger-db
nslookup ledger-db.production.svc.cluster.local
dig A ledger-db.production.svc.cluster.local.
dig AAAA ledger-db.production.svc.cluster.local.
dig SRV _grpc._tcp.payments-api.production.svc.cluster.local.
```

Použi rovnaký runtime resolver path ako application, keď je library-specific cache alebo address selection relevantná.

## 28. Referenčné pravidlá

- Pod DNS configuration je generated runtime state.
- Short name a FQDN sú odlišné query subjects.
- `ndots` a search list môžu násobiť queries.
- ClusterIP Service DNS vracia VIP, nie backend health.
- Headless Service presúva selection na clienta.
- CoreDNS readiness nepreukazuje current API data ani loaded config na celej cohorte.
- kube-dns je Service path a môže zlyhať v node dataplane.
- NodeLocal DNSCache pridáva per-Node failure domain.
- Cluster-local a upstream forwarding sú odlišné paths.
- DNS potrebuje UDP aj TCP podľa response behavioru.
- Negative cache môže prežiť object create alebo recovery.
- Fresh lookup bez fresh connection nepreukazuje application transition.
- DNS nie je server authentication.
- Recovery musí overiť lookup, selected address, connection a business outcome.

## 29. Kontrolné otázky

1. Aký lifecycle spája application lookup s verified requestom?
2. Ktoré inputs vytvárajú Pod `/etc/resolv.conf`?
3. Ako sa líšia short name, relative name a absolute FQDN?
4. Prečo `ndots` môže vytvoriť query amplification?
5. Ako sa líši ClusterIP a headless DNS answer?
6. Prečo CoreDNS Pod Ready nemusí znamenať current Service record?
7. Aký failure domain pridáva NodeLocal DNSCache?
8. Prečo treba testovať UDP aj TCP/53?
9. Ako odlíšiš DNS cache od Service/connectivity failure?
10. Čo musí DNS acceptance verdict overiť?

## Glossary impact

Relevantné pojmy: DNS lookup lifecycle subject, Pod resolver generation, query expansion subject, cluster-DNS Service subject, CoreDNS loaded configuration, Kubernetes DNS watch generation, NodeLocal DNS generation, upstream forwarding subject, negative-cache generation, DNS answer subject, resolver-library cache subject, fresh-connection verdict, DNS observation matrix a DNS acceptance verdict.

## Oficiálna dokumentácia

- [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [Configure DNS for a Cluster](https://kubernetes.io/docs/tasks/access-application-cluster/configure-dns-cluster/)
- [Debugging DNS Resolution](https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/)
- [Using CoreDNS for Service Discovery](https://kubernetes.io/docs/tasks/administer-cluster/coredns/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ingress a Gateway API](ingress-gateway-api.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CNI a NetworkPolicy →](cni-networkpolicy.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
