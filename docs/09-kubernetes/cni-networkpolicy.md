# CNI a NetworkPolicy

Kubernetes definuje očakávaný Pod network model, ale packet path nevytvára samotný API server. Container runtime zavolá CNI implementáciu, tá pridelí Podu network identity a zrealizuje connectivity. NetworkPolicy následne deklaruje, ktoré konkrétne flows majú byť povolené. API object, CNI operácia, IP allocation, policy realization a reálny packet verdict sú odlišné subjects.

Táto kapitola používa jeden dominantný lifecycle:

```text
communication intent a allowed-flow contract
→ admitted Pod a sandbox identity
→ CNI ADD a IPAM allocation
→ interface, route, tunnel alebo eBPF realization
→ source a destination policy selection
→ enforcement-point programming
→ packet a reverse-path verdict
→ application identity a business outcome
→ CNI DEL, IP release a policy cleanup
```

Ak sa tento chain rozdelí iba na „CNI funguje/nefunguje“ alebo „policy povoľuje/nepovoľuje“, diagnostika začne meniť nesprávnu vrstvu.

## 1. Atlas Payments flow subject

Atlas Payments API spracúva autorizáciu `pay-8842` a potrebuje:

```text
source Pod: payments-api P53
source namespace: production
source ServiceAccount: payments-api
source Node: N7
destination Service: ledger-db:5432
destination Pod: ledger-db-1 PDB1
destination Node: N9
protocol: TCP
business invariant: payment sa autorizuje presne raz
forbidden outcome: žiadny debug alebo staging Pod nesmie volať ledger-db
```

Network intent je:

```text
payments-api → ledger-db TCP/5432: allow
payments-api → cluster DNS UDP/TCP 53: allow
iné production Pods → ledger-db TCP/5432: deny
staging namespace → production ledger-db: deny
```

Flow subject preto nie je iba dvojica IP adries. Potrebuje minimálne:

```text
cluster a network implementation generation
source Pod UID, namespace, labels, ServiceAccount a Node
source sandbox/container ID, netns, interface a Pod IP allocation
destination Service UID alebo direct endpoint UID
destination Pod UID, labels, Node a listen socket
protocol, source/destination port a direction
pre-NAT a post-NAT tuple podľa observation pointu
matching NetworkPolicy UIDs/generations
effective policy/program generation na oboch Nodes
connection/conntrack generation a operation ID
```

## 2. Od Pod objectu po network sandbox

Scheduler pridelí Pod P53 na N7. Kubelet požiada container runtime o vytvorenie Pod sandboxu. Runtime vytvorí network namespace a zavolá CNI `ADD` s identitou konkrétneho sandboxu.

```text
Pod P53 bound na N7
→ runtime sandbox S53
→ network namespace NS53
→ CNI ADD(containerID=S53, netns=NS53, ifName=eth0)
→ IPAM lease L53
→ Pod IP 10.42.7.53
→ veth/interface, routes a policy metadata
→ sandbox pripravený pre containers
```

Kubernetes Pod UID, runtime sandbox ID, network namespace inode, interface index a IPAM lease nie sú zameniteľné. Pod môže dostať nový sandbox po recreation; rovnaký workload label pritom neznamená rovnakú network identity.

### CNI je contract, nie jeden daemon

Reálna implementácia môže zahŕňať:

- CNI binaries a configuration na Node filesysteme;
- per-Node agent;
- cluster controller alebo operator;
- IPAM datastore alebo cloud subnet integration;
- routed, overlay alebo cloud-native dataplane;
- Service proxying;
- NetworkPolicy compiler a enforcement;
- flow logs, health a reconciliation state.

Úspešný CNI binary call preto nepreukazuje, že všetky routes, tunnel peers, policy maps alebo remote Nodes používajú rovnakú generation.

## 3. IPAM a network identity

IPAM musí prideliť jedinečnú adresu a zachovať správny allocation lifecycle:

```text
pool alebo PodCIDR generation
→ allocation request pre sandbox S53
→ lease L53
→ address 10.42.7.53
→ route/neighbor/dataplane publication
→ active use
→ CNI DEL
→ lease release a stale-state cleanup
```

Failure hranice:

- pool je vyčerpaný;
- dva Nodes používajú prekrývajúce sa CIDRs;
- Node zanikol bez `DEL` a lease ostala stale;
- datastore zapísal allocation, ale response sa stratila;
- retry vytvoril duplicate alebo conflicting allocation;
- IP bola uvoľnená skôr, než zmizli routes, policy state a staré connections.

Pod status s IP adresou nepreukazuje jedinečnosť, reachability ani správnu return route.

## 4. Dataplane realization

CNI implementation môže používať routed Pod CIDRs, overlay tunnel, cloud interfaces, bridge/veth, eBPF alebo kombináciu mechanizmov.

### Routed model

```text
source Pod route
→ source Node routing
→ upstream alebo direct node route k destination PodCIDR
→ destination Node
→ destination veth/Pod
```

Failure boundary je route publication, return route, cloud firewall alebo stale neighbor state.

### Overlay model

```text
inner packet: 10.42.7.53 → 10.42.9.11
→ encapsulation na N7
→ underlay N7 → N9
→ decapsulation na N9
→ destination Pod
```

Failure boundary je tunnel peer, underlay reachability, encapsulation state alebo efektívna MTU.

### CNI chaining

Ak chain pozostáva z connectivity, port-mapping, tuning a bandwidth pluginu, každý krok môže vytvoriť state. Partial failure po vytvorení veth a IP lease, ale pred policy alebo bandwidth krokom, potrebuje reverse-order cleanup. Blind retry bez reconciliation môže ponechať duplicate interface, route alebo lease.

## 5. NetworkPolicy intent a effective enforcement

NetworkPolicy je namespaced API object. Vyberá destination Pods pre ingress alebo source Pods pre egress. Traffic je povolený iba vtedy, keď pre každý izolovaný smer patrí do unionu všetkých matching allow rules.

```text
source Pod egress isolation?
→ ak áno, flow musí povoliť aspoň jedna matching egress policy

destination Pod ingress isolation?
→ ak áno, flow musí povoliť aspoň jedna matching ingress policy

obe rozhodnutia allow
→ packet môže pokračovať
```

Policy order neexistuje. Štandardný NetworkPolicy model nemá všeobecnú prioritu ani explicitné deny rule; deny je neprítomnosť povolenia pre izolovaný smer.

### API object nie je enforcement

```text
NetworkPolicy generation NP17
→ CNI controller/watch
→ selector a peer resolution
→ per-Node effective policy program EP17
→ packet observation v enforcement pointe
→ allow/drop verdict
```

Policy môže existovať v API, ale nemať efekt, ak implementation NetworkPolicy nepodporuje, agent nepozoroval current generation alebo konkrétny traffic obchádza očakávaný enforcement point.

## 6. Selector semantics sú security semantics

Policy peer s `namespaceSelector` a `podSelector` v jednej položke typicky znamená AND:

```yaml
from:
  - namespaceSelector:
      matchLabels:
        environment: production
    podSelector:
      matchLabels:
        access: ledger
```

Dve samostatné položky znamenajú alternatívy:

```yaml
from:
  - namespaceSelector:
      matchLabels:
        environment: production
  - podSelector:
      matchLabels:
        access: ledger
```

Druhá verzia môže povoliť všetky Pods z production namespaces **alebo** všetky lokálne Pods s labelom `access=ledger`. YAML indentation teda môže zmeniť authorization graph.

Labels používané na security rozhodnutie musia mať dôveryhodného ownera. Ak application tím môže ľubovoľne pridať label, ktorý policy považuje za identity, môže si sám udeliť network access.

## 7. Service, NAT a policy observation point

Klient typicky volá Service VIP, ale destination Pod dostane packet po Service translation:

```text
client tuple: 10.42.7.53:41230 → 10.96.20.40:5432
→ Service dataplane vyberie endpoint
backend tuple: 10.42.7.53:41230 → 10.42.9.11:5432
→ NetworkPolicy enforcement podľa implementation
```

Pri NodePort, LoadBalancer, SNAT, masquerade alebo `externalTrafficPolicy` môže enforcement point vidieť inú source/destination IP než manifest author očakáva. `ipBlock` preto neposudzuj bez určenia pre/post-NAT observation pointu.

Direct Pod IP test obchádza Service selection a translation. Môže potvrdiť backend socket a časť Pod networku, ale nepreukazuje Service ani policy path používaný klientom.

## 8. Default deny a platform dependencies

Default deny je bezpečný iba s inventárom všetkých potrebných flows. Payments potrebuje okrem ledger DB aj:

- DNS cez reálny kube-dns alebo NodeLocal DNS path;
- metrics alebo telemetry endpointy;
- workload identity/token exchange;
- certificate/secret provider;
- prípadné control-plane alebo metadata endpoints;
- graceful shutdown a health dependencies.

Pri DNS musí policy pokrývať reálnu destination identity a podľa odpovede UDP aj TCP 53. Policy skopírovaná z clusteru bez NodeLocal DNSCache môže v clustri s node-local resolverom blokovať nesprávnu adresu.

## 9. Existing connections a revocation

Policy generation NP18 môže zakázať nové flows, ale už existujúce spojenie môže prežiť podľa dataplane a conntrack semantics.

```text
NP17 allow
→ connection C77 established
→ NP18 deny
→ nové SYN packets drop
→ C77 môže pokračovať
```

Security revocation preto môže potrebovať:

- explicitné ukončenie sessions alebo conntrack state-u;
- credential/certificate rotation;
- application-level authorization revocation;
- overenie nového aj existujúceho flow.

NetworkPolicy nie je authentication ani encryption. Povolený packet stále potrebuje TLS/mTLS a application authorization.

## 10. Worked failure: default deny odstavilo DNS iba na niektorých Nodes

Platform zaviedla default-deny egress a povolila traffic na kube-dns Service IP. Pods na bežných Nodes fungovali, ale Pods na N7 a N8 dostávali DNS timeout.

Mechanizmus:

```text
N7/N8 používali NodeLocal DNSCache
→ Pod resolv.conf smeroval na node-local IP
→ policy povoľovala iba central kube-dns VIP
→ query bola dropnutá pred NodeLocal agentom
→ application nevedela resolve-nuť ledger-db
```

Policy object bol syntakticky správny. Chybný bol effective flow inventory. Recovery doplnila explicitný NodeLocal DNS path pre UDP/TCP 53 a canary testovala short name, FQDN aj TCP fallback z každej node pool generation.

## 11. Worked failure: policy existovala, ale jeden Node ju nevynucoval

NetworkPolicy NP22 zakazovala debug Podom prístup k ledger-db. Test na N9 bol správne blokovaný, ale debug Pod na N11 sa pripojil.

```text
API object NP22 current
→ controller compiled EP22
→ N9 loaded EP22
→ N11 agent po upgrade ostal na EP21
→ packet na N11 prešiel
```

`kubectl get networkpolicy` neukázal rozdiel. Rozhodujúce boli per-Node loaded-policy generation, flow verdict log a packet capture v enforcement pointe. Recovery vyradila N11 z workloadov, obnovila agent reconciliation a overila forbidden flow pred uncordon.

## 12. Worked failure: same-Node funguje, cross-Node zlyháva

Payments Pod na N7 komunikoval s test backendom na N7, ale nie s ledger-db na N9.

```text
same-Node path nepoužil tunnel
→ test prešiel
cross-Node packet sa encapsuloval
→ underlay MTU nepodporila veľký packet
→ malé SYN/ACK alebo malé requests prešli
→ väčšie TLS/application records zlyhali
```

Policy nebola root cause. Packet-size a pre/post-encapsulation observations odlíšili MTU/tunnel failure od L3/L4 deny.

## 13. Worked failure: selector indentation rozšírila access

Reviewer očakával „Pods s `access=ledger` v namespace označenom `environment=production`“. Manifest však obsahoval dve peer položky.

Dôsledok:

```text
namespace selector OR pod selector
→ všetky Pods v production namespaces boli povolené
→ unrelated reporting Pod získal DB reachability
```

Fix opravil peer structure, zaviedol policy-as-code test na allowed aj forbidden identities a chránil namespace/workload labels admission policy.

## 14. Causal troubleshooting walkthrough: payment flow zlyháva iba z N7

Symptóm:

```text
payments-api P53 na N7
→ ledger-db Service resolve funguje
→ direct aj Service TCP connect timeoutuje
→ rovnaká release cohorta na N6 funguje
→ ledger-db PDB1 je Ready
```

### 1. Zafixuj subject a outcome

Zaznamenaj:

```text
cluster/network implementation a version
time window a operation pay-8842
source Pod UID, sandbox ID, Node UID, IP/lease a labels
source egress policy UIDs/generations
destination Service UID/VIP/port a EndpointSlice target UID
destination Pod UID, Node, IP a ingress policy generations
pre/post-NAT tuple a enforcement points
per-Node CNI agent, route/tunnel a effective-policy generations
conntrack/connection generation
```

Pôvodný outcome: autorizácia musí prejsť presne raz. Forbidden outcome: debug/staging identity zostane blokovaná.

### 2. Vytvor competing hypotheses

| Hypotéza | Diskriminačný dôkaz |
|---|---|
| source Pod sandbox/route je chybný | source netns route, interface, neighbor a packet egress |
| IPAM lease je duplicate alebo stale | allocation datastore, ARP/neighbor conflict, reverse ownership |
| N7 tunnel/underlay zlyháva | encapsulated packet, peer health, MTU a return path |
| source egress policy dropuje | matching policies a source enforcement verdict |
| destination ingress policy dropuje | destination enforcement verdict a selected identity |
| Service translation je chybná | direct endpoint vs. VIP a pre/post-NAT trace |
| stale conntrack state smeruje zle | new 5-tuple oproti existing connection state |
| backend nepočúva alebo application odmieta | packet arrival, SYN response, TLS/application logs |

### 3. Pozoruj flow na hraniciach

```text
application connect call
→ source socket a netns
→ source veth/host boundary
→ source policy enforcement
→ Service translation alebo direct route
→ overlay/routed underlay
→ destination Node enforcement
→ destination veth/socket
→ reverse path
```

Nespoliehaj sa iba na `ping`: ICMP môže mať inú policy aj path než TCP/5432.

### 4. Containment

- zastav rollout policy/CNI zmien;
- presuň alebo odober N7 cohort z payment trafficu bez zmazania evidence;
- zachovaj CNI agent logs, maps/rules, routes, tunnel a IPAM state;
- nevytváraj temporary allow-all policy;
- nereštartuj celý CNI fleet;
- nereplayuj payment bez idempotency lookupu.

### 5. Authoritative recovery

Finding bol stale route/tunnel generation na N7 po partial agent upgrade. Policy verdicty boli allow, ale return route na N7 smerovala do starého tunnel peeru.

Recovery:

1. cordon N7 a drain application cohortu podľa availability budgetu;
2. reconcile-ni agent, routes a tunnel peer na reviewed generation;
3. odstráň iba potvrdený stale state;
4. spusti per-Node direct, Service, DNS a policy canary;
5. vráť N7 do scheduling poolu až po accepted capability verdict.

### 6. Over pôvodný a forbidden outcome

Potvrď:

- P53 replacement má jedinečnú IPAM lease a správne routes;
- direct Pod aj Service path prejdú v oboch smeroch;
- source egress a destination ingress verdict patria current policy generations;
- DNS funguje cez UDP aj TCP fallback;
- payment `pay-8842` má presne jeden accepted downstream result;
- debug a staging Pods sú stále blokované;
- nový flow aj nový connection po revokácii používajú current state;
- rovnaký canary prejde na každom Node poole.

### 7. Posuň control skôr

Pridaj:

- versionovaný per-Node CNI/dataplane inventory;
- IPAM uniqueness a stale-lease reconciliation test;
- policy compile/load generation telemetry;
- allowed aj forbidden flow conformance matrix;
- same-Node, cross-Node, Service, direct, DNS a TCP-fallback canaries;
- MTU test pre maximálny očakávaný packet;
- admission ownership pre security labels;
- policy revocation test existujúcich connections;
- bounded CNI rollout rings a automatic cordon pri capability failure.

## 15. Observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Intent | allowed-flow contract | owner, source/destination identities, protocol, forbidden flows |
| Pod network | Pod UID + sandbox/netns | Node, interface, route, runtime state |
| IPAM | lease/allocation subject | pool/CIDR, owner, uniqueness, release state |
| Dataplane | Node generation | route, tunnel, eBPF/rules, MTU, peer health |
| Service | VIP a endpoint target UID | pre/post-NAT tuple, selected backend |
| Policy selection | NetworkPolicy UIDs/generations | selected Pods, peers, ports, isolation directions |
| Enforcement | per-Node effective program | loaded generation, allow/drop verdict, observation point |
| Connection | 5-tuple/conntrack generation | established/new flow, NAT a reverse path |
| Application | TLS/principal/request | listener, authn/authz, operation ID |
| Business | payment result | exactly-once result a forbidden-access proof |
| Cleanup | CNI DEL/IP release | interface, route, lease, policy a session cleanup |

## 16. Referenčné príkazy

```bash
kubectl get pod -A -o wide
kubectl get pod <pod> -n <namespace> -o yaml
kubectl get networkpolicy -A -o yaml
kubectl get namespace --show-labels
kubectl get endpointslice -A -o yaml
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Node-level evidence závisí od implementácie. Môže zahŕňať CNI agent status, IPAM allocations, routes, interfaces, tunnel peers, nftables/iptables/IPVS state, eBPF maps, flow verdict logs a packet captures.

## 17. Referenčné pravidlá

- CNI `ADD` realizuje network sandbox; Pod object sám interface nevytvorí.
- Pod UID, sandbox ID, netns, interface a IPAM lease sú odlišné subjects.
- Pod IP neprináša automaticky reachability ani policy correctness.
- NetworkPolicy API potrebuje implementáciu, ktorá policy reálne vynucuje.
- Egress source a ingress destination sa vyhodnocujú samostatne.
- Matching policies sa skladajú aditívne; rule order neexistuje.
- Selector structure a label ownership sú security contract.
- Service VIP a backend tuple môžu byť v rôznych observation points odlišné.
- NetworkPolicy je L3/L4 filtering, nie workload authentication ani encryption.
- Existing connection môže prežiť policy mutation.
- Same-Node success nepreukazuje cross-Node tunnel alebo route.
- Recovery musí overiť actual packet verdict, reverse path, application identity a business outcome.

## 18. Kontrolné otázky

1. Aký lifecycle spája Pod communication intent s verified application requestom?
2. Ako sa líšia Pod UID, sandbox ID, netns a IPAM lease?
3. Ktorý state vytvára CNI `ADD` a čo musí odstrániť `DEL`?
4. Prečo API NetworkPolicy nepreukazuje effective enforcement?
5. Ako sa skladajú source egress a destination ingress decisions?
6. Ako YAML peer structure mení AND/OR semantics?
7. Prečo musíš poznať pre/post-NAT observation point?
8. Ako odlíšiš CNI route/tunnel failure od policy dropu?
9. Prečo policy revocation nemusí ukončiť existing connection?
10. Čo musí network acceptance verdict overiť?

## Glossary impact

Relevantné pojmy: Pod network realization subject, CNI operation subject, CNI chain generation, IPAM allocation subject, Pod network identity, routed a overlay dataplane generation, flow subject, policy selection subject, effective NetworkPolicy generation, enforcement-point verdict, pre/post-NAT flow identity, policy revocation generation, network observation matrix a network acceptance verdict.

## Oficiálna dokumentácia

- [Services, load balancing and networking](https://kubernetes.io/docs/concepts/services-networking/)
- [Cluster networking](https://kubernetes.io/docs/concepts/cluster-administration/networking/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Declare Network Policy](https://kubernetes.io/docs/tasks/administer-cluster/declare-network-policy/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cluster DNS](cluster-dns.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Volumes, PV, PVC a StorageClass →](volumes-pv-pvc-storageclass.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
