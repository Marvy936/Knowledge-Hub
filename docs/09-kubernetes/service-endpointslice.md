# Service a EndpointSlice

Kubernetes Service je stabilný network contract nad meniacu sa množinou backendov. EndpointSlice je verzovaný backend inventory, ktorý prepája Service selector alebo explicitného ownera s konkrétnymi addresses, ports, conditions a topology metadata. Ani jeden objekt sám nie je application process; request musí prejsť DNS, node dataplane, endpoint selection, backend socket a reverse path.

Dominantný lifecycle:

```text
client communication intent a Service contract
→ Service UID, generation, VIP a port identity
→ selector alebo explicitný endpoint ownership
→ Pod inventory, readiness a endpoint classification
→ EndpointSlice cohort generation
→ node dataplane programming
→ DNS alebo direct Service address lookup
→ endpoint selection, forwarding a NAT/state
→ backend socket a application processing
→ reverse path a response
→ drain, replacement, propagation a business verification
```

Kapitola používa Atlas Payments. Service `payments-api` v namespace `production` prijíma TCP traffic na porte 8443 a smeruje ho na accepted Pods release 4.2.0. Klientský request má operation ID `pay-8842`. Cieľom nie je iba „Service existuje“, ale:

```text
accepted client
→ správny Service contract
→ správna EndpointSlice cohorta
→ správny Pod UID a image/config generation
→ presne jeden payment authorization
→ korektná response a audit
```

## 1. Service subject musí zahŕňať viac než meno

Pri diagnostike fixuj:

```text
cluster a namespace
Service name a UID
metadata.generation a resourceVersion
Service type, ClusterIP/clusterIPs a IP family
port name, protocol, port a targetPort
selector alebo selectorless ownership
traffic policies a session affinity
EndpointSlice names, resourceVersions a managed-by owner
endpoint targetRef UIDs, addresses, ports a conditions
client Pod UID a Node
node dataplane implementation/generation
backend Pod UID, Node, imageID a listen socket
request/connection tuple a business operation ID
```

Rovnaké Service meno po delete/create môže mať inú UID, ClusterIP a controller lifecycle. Rovnaká Pod IP môže neskôr patriť inému Pod UID.

## 2. Service je contract, nie backend inventory

Service definuje stabilnú identity a port semantics:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: payments-api
  namespace: production
spec:
  selector:
    app.kubernetes.io/name: payments-api
    release.atlas.example/generation: "42"
  ports:
    - name: https
      protocol: TCP
      port: 8443
      targetPort: https
```

Service selector vyberá Pods podľa labels. Nevyberá Deployment ani ReplicaSet. Preto selector musí byť navrhnutý ako traffic ownership contract, nie iba ako pohodlné `app=payments`.

## 3. EndpointSlice cohort je effective backend state

Pre selector-based Service control plane vytvára EndpointSlices z matching Podov.

```text
Service selector S42
→ Pod UID inventory
→ address family + port/protocol grouping
→ EndpointSlice cohort ES42
```

Pre jeden Service môže existovať viac slices. Full backend set je union všetkých slices označených `kubernetes.io/service-name=<service>`.

Endpoint identity zahŕňa:

- address;
- targetRef UID, ak je dostupný;
- port/protocol;
- `ready`, `serving` a `terminating` conditions;
- Node a zone metadata;
- slice owner/managed-by generation.

Slice name nie je stabilná backend identity.

## 4. Readiness, serving a termination sú odlišné states

Request path rozlišuje:

```text
Pod exists
container Running
Pod Ready
endpoint serving
endpoint terminating
endpoint ready for ordinary traffic
node dataplane processed update
existing connection still alive
```

Asynchrónnosť medzi týmito stavmi je súčasť control loopu. `Ready=False` na Pode neznamená, že všetky existujúce connections okamžite skončili. `terminating=true` neznamená, že process už neobsluhuje žiadny request.

## 5. Named `targetPort` je cross-revision contract

Service môže používať:

```yaml
ports:
  - name: https
    port: 8443
    targetPort: https
```

Každá accepted Pod revision musí deklarovať a reálne otvoriť pomenovaný port `https`. Named target port umožňuje rozdielne numeric ports medzi revisions, ale iba ak každý backend spĺňa rovnaký logical contract.

Failure boundary:

```text
Pod label match
+ Pod Ready
+ named port chýba alebo smeruje na nesprávny socket
→ endpoint cohort neobsahuje použiteľný port alebo traffic zlyhá
```

`containerPort` metadata neotvorí socket. Listen state musí overiť application/runtime observation.

## 6. ClusterIP request journey

ClusterIP je virtual Service address, nie interface s proxy processom.

```text
client Pod P17 na Node N3
→ DNS payments-api.production.svc...
→ ClusterIP 10.96.42.17:8443
→ node Service dataplane generation DP88
→ endpoint selection z ES42
→ Pod P52 10.244.8.31:9443
→ application process
→ response cez conntrack/NAT/reverse path
```

Dataplane môže používať kube-proxy alebo inú implementation. Diagnostika sa musí prispôsobiť effective implementation, nie predpokladanému iptables modelu.

## 7. DNS success a Service success sú odlišné

Bežný Service DNS record typicky vracia ClusterIP. DNS nevie, či:

- EndpointSlice cohort je prázdna;
- targetPort je správny;
- node dataplane je aktuálny;
- NetworkPolicy povoľuje flow;
- backend process počúva;
- business operation je korektná.

Preto:

```text
DNS answer success
≠ endpoint availability
≠ packet forwarding
≠ application correctness
```

## 8. Headless Service mení selection ownera

Headless Service s `clusterIP: None` typicky publikuje endpoint addresses cez DNS namiesto jednej VIP.

```text
DNS
→ viac endpoint addresses
→ client-side selection, cache a failover
```

To je vhodné pre peer discovery alebo StatefulSet identity, ale selection responsibility sa presúva na klienta. DNS poradie nie je leader election ani health-aware durable load balancer.

## 9. Selectorless Service a explicitné ownership

Service bez selectoru môže reprezentovať external alebo operator-managed backend.

```text
Service UID S-EXT
→ EndpointSlice managed-by platform.example.com
→ external backend identity DB-PROD-7
```

Custom controller musí vlastniť:

- endpoint discovery;
- addresses a ports;
- conditions;
- lifecycle a cleanup;
- stale backend removal;
- audit correlation.

Needituj controller-managed slices ručne. Pri custom slices používaj jednoznačný `endpointslice.kubernetes.io/managed-by` a Service label.

## 10. Service types sú exposure transitions

### ClusterIP

Cluster-internal virtual identity. Neznamená security, encryption ani tenant isolation.

### NodePort

Publikuje Service port cez Node addresses. Mení host exposure, firewall surface, source-IP behavior a capacity model.

### LoadBalancer

Vytvára desired external exposure, ktoré musí reconciliovať cloud alebo platform controller.

```text
Service generation
→ LB controller request
→ external LB resource
→ listener/health-check generation
→ NodePort alebo direct endpoint integration
→ Service/EndpointSlice cohort
```

External address v `status` nie je end-to-end acceptance verdict.

### ExternalName

Poskytuje DNS alias. Nevytvára L4 proxy ani EndpointSlice backend cohort. TLS hostname a application protocol musia zodpovedať aliasu.

## 11. Internal a external traffic policy

Traffic policy mení eligible endpoint set a packet semantics.

Pri `Local` policy môže Node bez local ready endpointu traffic dropnúť alebo neposkytnúť rovnakú availability ako cluster-wide routing.

Service acceptance preto potrebuje:

```text
Node inventory
local endpoint coverage
external LB node selection
source-IP requirement
fallback behavior
zone/failure-domain distribution
```

`Local` nie je automaticky „rýchlejšie“. Je to locality a source-path contract s availability trade-offom.

## 12. Topology a traffic distribution

EndpointSlice nesie Node/zone metadata a môže niesť routing hints. Effective behavior závisí od Service fields, controller/dataplane supportu, endpoint distribution a cluster version.

Cieľom môže byť:

- preferovať same-zone endpoint;
- znížiť cross-zone traffic;
- zachovať fallback pri výpadku;
- nepreťažiť jednu zónu.

Topology hint nepreukazuje, že client request skutočne zostal v zóne. Overuj per-zone flows a backend cohort metrics.

## 13. Dual-stack je dvojitý path contract

IPv4 a IPv6 majú samostatné address subjects a EndpointSlices.

```text
Service clusterIPs
→ IPv4 cohort
→ IPv6 cohort
→ client resolver/address selection
→ family-specific dataplane a backend socket
```

A/AAAA records, CNI routes, NetworkPolicy, application listen addresses a upstream firewalls musia byť konzistentné. Funkčný IPv4 request nepreukazuje IPv6 acceptance.

## 14. Session affinity a persistent connections

`ClientIP` affinity je temporary selection state, nie durable session store. NAT môže zdieľať source IP a replacement endpoint affinity zruší.

Aj bez affinity môžu keep-alive, HTTP/2 alebo gRPC connections držať klienta na starej Pod generation dlho po zmene EndpointSlice.

Rollout verification preto testuje:

- fresh DNS lookup, ak je relevantný;
- fresh connection;
- existujúcu connection počas drainu;
- request distribution podľa Pod UID/revision;
- session/data correctness.

## 15. Endpoint drain a connection lifecycle

Bezpečný Pod removal:

```text
readiness alebo custom drain state False
→ EndpointSlice condition transition
→ node/LB dataplane propagation
→ nové connections prestanú smerovať na Pod
→ existujúce connections sa drainujú
→ process dokončí in-flight work
→ termination
```

`preStop` bez readiness removal a propagation budgetu môže iba oddialiť ukončenie, nie zabrániť novému trafficu.

Service nedokáže vrátiť request, ktorý už backend prijal. Non-idempotent operation potrebuje application-level idempotency a graceful termination.

## 16. Service nie je security boundary

Reachability abstraction nenahrádza:

- NetworkPolicy alebo dataplane policy;
- TLS/mTLS;
- application authentication/authorization;
- firewall/source range policy;
- ServiceAccount/RBAC controls nad Service a EndpointSlice mutation;
- controller trust.

Actor, ktorý môže zmeniť Service selector alebo custom EndpointSlice, môže presmerovať traffic na svoj backend. To je routing authority a potenciálny credential/data interception path.

## 17. Worked failure: široký selector zaradil debug Pod

Service vyberal iba `app=payments`. Debug Pod mal rovnaký label, ale iný image a nemal správne auth middleware.

```text
broad selector
→ debug Pod sa dostane do EndpointSlice cohorty
→ časť trafficu ide na debug backend
→ replica counts a Service status vyzerajú zdravo
```

Recovery vyžadovala:

- zúžiť traffic labels na owner a release cohort;
- odstrániť debug endpoint z dataplane;
- auditovať requests, ktoré naň smerovali;
- overiť forbidden endpoint membership test.

## 18. Worked failure: named port mismatch počas rollout-u

New Pods boli Ready, ale pomenovaný port `https` smeroval na 9444, zatiaľ čo process počúval na 9443.

Kubernetes readiness testovala iný port cez explicitnú probe. Endpointy preto vyzerali ready, no Service traffic zlyhával.

Fix spojil named port, readiness a application listen contract do jedného runtime testu.

## 19. Worked failure: `externalTrafficPolicy: Local` bez coverage

External load balancer posielal traffic na všetky Nodes. Dva Nodes nemali local Payments endpoint.

```text
LB Node selection
+ Local policy
+ no local endpoint
→ drop/timeout na časti requests
```

Cluster-wide endpoint count bol zdravý. Root cause bola intersection Node cohorty a local endpoint cohorty.

## 20. Worked failure: terminating endpoint stále dostával requests

Readiness sa odstránila, ale:

- LB health interval bol 30 sekúnd;
- node dataplane propagation mala oneskorenie;
- klient držal HTTP/2 connection;
- application `preStop` iba sleepoval.

Výsledkom boli requests na terminating Pod a duplicate payment retry. Recovery musela riešiť edge, Service aj application connection lifecycle.

## 21. Causal troubleshooting walkthrough: Pod IP funguje, ClusterIP zlyháva iba z jedného Node-u

Symptóm:

```text
client Pods na N1 a N2 úspešné
client Pod P17 na N3 dostáva timeout na Service ClusterIP
priame spojenie z P17 na backend Pod IP funguje
DNS vracia správny ClusterIP
EndpointSlices obsahujú ready backends
```

### 1. Zafixuj flow subject

```text
client Pod UID P17, Node N3 a network namespace
source IP/port
Service UID S42, ClusterIP, protocol a port
Service generation a traffic policy
EndpointSlice cohort ES42 a resourceVersions
selected/eligible endpoint UIDs a addresses
backend targetPort a listen socket
node dataplane implementation a generation DP88
NetworkPolicy generation
request ID pay-8842
```

### 2. Konkurenčné hypotézy

1. N3 má stale alebo chýbajúce Service dataplane rules;
2. `internalTrafficPolicy: Local` nemá local endpoint na N3;
3. targetPort/endpoint port je nesprávny;
4. EndpointSlice watch na N3 dataplane zaostáva;
5. conntrack/NAT state na N3 je vyčerpaný alebo stale;
6. NetworkPolicy rozlišuje Service-translated a direct path;
7. dual-stack/address-family selection je rozdielna;
8. Node firewall alebo route blokuje VIP path;
9. client používa stale persistent connection;
10. direct Pod test obchádza inú application/TLS identity boundary.

### 3. Diskriminačné observation points

- porovnaj fresh connection z rovnakého client namespace-u na N1/N2/N3;
- over Service fields a local traffic policy;
- spoj všetky EndpointSlices do jednej cohorty a skontroluj targetRef UIDs;
- over backend socket na resolved targetPort;
- sleduj packet pred Service translation, po selection a na backend Node-e;
- porovnaj dataplane program state/generation medzi Nodes;
- skontroluj conntrack saturation a drops;
- over IPv4/IPv6 family použitú klientom;
- porovnaj NetworkPolicy verdict na actual tuple;
- skontroluj terminating/stale endpoint entries.

### 4. Containment

- cordon alebo vyraď N3 z client/external trafficu, ak failure ohrozuje request correctness;
- zachovaj dataplane a conntrack evidence pred restartom;
- nemaž Service ani všetky EndpointSlices;
- nevypínaj NetworkPolicy cluster-wide;
- neprepínaj traffic na hard-coded Pod IPs;
- obmedz retries pri non-idempotent requests.

### 5. Authoritative recovery

Podľa findingu:

- obnov node dataplane agent a watch state;
- oprav Local policy/LB node coverage;
- oprav targetPort a rollout-ni new Pod generation;
- vyčisti iba preukázateľne stale conntrack/dataplane state podľa runbooku;
- oprav family-specific CNI/firewall path;
- odstráň stale custom endpoint cez jeho owner controller.

### 6. Over pôvodný outcome

Potvrď:

- S42 a ES42 tvoria správny endpoint inventory;
- N1, N2 aj N3 majú rovnakú accepted dataplane generation;
- fresh request z každého Node cohortu dosiahne accepted Pod UID;
- terminating alebo debug UIDs nie sú v ordinary traffic cohort-e;
- IPv4 aj IPv6 prejdú, ak sú podporované;
- pay-8842 je autorizovaný presne raz;
- backend response a downstream audit sedia;
- ďalší Pod rollout a drain nemenia výsledok.

### 7. Posuň control skôr

Pridaj:

- selector ownership test;
- Service-to-Pod named-port contract test;
- EndpointSlice cohort telemetry s targetRef UID/revision;
- per-Node Service canary;
- Local policy coverage preflight;
- dual-stack path test;
- endpoint drain propagation budget;
- synthetic business request cez Service pred old Pod termination;
- alert na dataplane generation skew medzi Nodes.

## 22. Observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Contract | Service UID/generation | type, VIPs, selector, ports, policies |
| Backend intent | selector/owner | labels, managed-by, external discovery |
| Endpoint state | EndpointSlice cohort | targetRef UID, address, port, conditions, zone |
| Pod | backend Pod UID | readiness, image/config, Node, listen socket |
| Client | client Pod/Node | resolver, source tuple, family, connection state |
| Dataplane | Node generation | Service rules/maps, watch lag, drops, conntrack |
| Policy | actual translated flow | NetworkPolicy/firewall verdict, source identity |
| External exposure | LB/NodePort subject | node coverage, health, source ranges |
| Drain | endpoint/connection generation | terminating, propagation, keep-alive, grace |
| Business | request/operation ID | accepted backend, response, exactly-once invariant |

## 23. Referenčné príkazy

```bash
kubectl get service payments-api -n production -o yaml
kubectl get endpointslice -n production \
  -l kubernetes.io/service-name=payments-api -o yaml
kubectl get pods -n production -l '<service-selector>' -o wide
kubectl get pod <pod> -n production -o yaml
kubectl get networkpolicy -n production -o yaml
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Node dataplane observations závisia od implementation. Najprv identifikuj, či cluster používa kube-proxy, eBPF/CNI dataplane alebo inú platformovú vrstvu.

## 24. Referenčné pravidlá

- Service selector vyberá Pods, nie controllers.
- Service object a EndpointSlice cohort sú odlišné generations.
- Full endpoint inventory môže byť rozdelený do viacerých slices.
- Pod Ready, endpoint serving a endpoint terminating sú odlišné states.
- Named targetPort je cross-revision runtime contract.
- ClusterIP je virtual dataplane address, nie proxy process.
- DNS success nepreukazuje Service forwarding ani backend correctness.
- Headless Service presúva selection zodpovednosť na clienta.
- `Local` traffic policy potrebuje local endpoint coverage.
- External address v Service status nie je end-to-end verdict.
- Existing connections môžu prežiť endpoint removal.
- Service nie je security policy.
- Recovery musí overiť actual backend UID aj business outcome.

## 25. Kontrolné otázky

1. Aký lifecycle spája Service contract s verified application response?
2. Prečo Service selector nevyberá Deployment?
3. Ako vytvoríš full backend inventory z EndpointSlices?
4. Ako sa líšia `ready`, `serving` a `terminating`?
5. Prečo named targetPort patrí do rollout contractu?
6. Čo ClusterIP dataplane robí s packetom?
7. Prečo direct Pod IP test nepreukazuje Service path?
8. Aké riziko má Local traffic policy bez Node coverage?
9. Prečo endpoint removal neukončí všetky connections?
10. Čo musí Service acceptance verdict overiť?

## Glossary impact

Relevantné pojmy: Service lifecycle subject, Service contract generation, endpoint-cohort subject, EndpointSlice ownership generation, endpoint target identity, endpoint condition lifecycle, named-port contract, Service dataplane generation, client-Service flow subject, local-endpoint coverage, external exposure subject, endpoint-drain generation, Service observation matrix a Service acceptance verdict.

## Oficiálna dokumentácia

- [Service](https://kubernetes.io/docs/concepts/services-networking/service/)
- [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)
- [Virtual IPs and Service Proxies](https://kubernetes.io/docs/reference/networking/virtual-ips/)
- [Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: ServiceAccount](serviceaccount.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ingress a Gateway API →](ingress-gateway-api.md)
<!-- KNOWLEDGE-NAVIGATION:END -->