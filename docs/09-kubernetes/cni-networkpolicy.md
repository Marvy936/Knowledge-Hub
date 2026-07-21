# CNI a NetworkPolicy

Kubernetes definuje sieťový model, ale neposkytuje jednu povinnú implementáciu Pod networku. Kubelet a container runtime používajú **Container Network Interface (CNI)** pluginy na vytvorenie a odstránenie Pod network interface-u. **NetworkPolicy** je namespaced API pre deklarovanie povoleného ingress a egress trafficu; pravidlá reálne vynucuje iba network implementation, ktorá NetworkPolicy podporuje.

## 1. Kubernetes network model

Základné očakávania Kubernetes sú:

- každý Pod dostane vlastnú IP adresu,
- containers v jednom Pode zdieľajú network namespace a komunikujú cez `localhost`,
- Pods majú vedieť komunikovať naprieč Nodes bez application-level NAT medzi Pod IP adresami,
- agents na Node-e vedia komunikovať s Podmi na danom Node-e,
- Service networking je samostatná virtual-service vrstva nad Pod networkom.

Konkrétna implementation môže používať:

- routed Pod CIDRs,
- overlay/tunnel,
- cloud-native interfaces,
- eBPF dataplane,
- Linux bridge a veth,
- kombináciu viacerých mechanizmov.

## 2. CNI contract

CNI je specification a plugin contract, nie jeden daemon ani jeden vendor produkt.

Pri vytváraní Pod sandboxu runtime typicky:

1. vytvorí network namespace,
2. zavolá CNI `ADD`,
3. odovzdá container ID, namespace path, interface name a configuration,
4. plugin vytvorí interface a pripojí ho k dataplane,
5. IPAM pridelí adresu,
6. plugin nastaví routes, gateway a prípadné policy metadata,
7. runtime spustí containers v pripravenom sandboxe.

Pri odstránení sandboxu volá CNI `DEL` a implementation uvoľní interface, IP a ďalší state.

## 3. CNI plugins a node agent

Reálna CNI platforma často obsahuje:

- CNI binaries na Node filesysteme,
- configuration files v runtime CNI directory,
- DaemonSet agent na každom Node-e,
- control-plane controller alebo operator,
- IP address management,
- route, tunnel alebo eBPF programy,
- NetworkPolicy enforcement,
- observability a flow logs.

Pod môže zostať v `ContainerCreating`, ak CNI binary existuje, ale agent, IPAM, route controller alebo datastore nie je funkčný.

## 4. Pod CIDR a IPAM

IPAM musí zabezpečiť jedinečné Pod IP adresy a správny lifecycle ich pridelenia.

Modely:

- per-Node Pod CIDR,
- centralizovaný IP pool,
- cloud subnet IP allocation,
- secondary interfaces,
- dual-stack IPv4/IPv6 pools.

Riziká:

- vyčerpanie poolu,
- prekrývajúce sa CIDRs,
- stale leases po Node failure,
- nedostupný IPAM datastore,
- nesprávne routes po presune workloadu,
- rozdielna kapacita IP adries medzi Nodes.

## 5. Overlay a routed networking

### Overlay

Pod traffic je zapuzdrený do tunela medzi Nodes.

Výhody:

- menšia závislosť od upstream route konfigurácie,
- jednoduchšie izolované Pod CIDRs.

Nevýhody:

- encapsulation overhead,
- nižšia efektívna MTU,
- komplikovanejšia packet capture,
- tunnel state a failure modes.

### Routed model

Upstream alebo node routing pozná Pod CIDRs bez overlay encapsulation.

Výhody:

- jednoduchší packet format,
- často lepší výkon a source-IP visibility.

Nevýhody:

- route scale a propagation,
- závislosť od cloud/network integrácie,
- širšia exposure Pod address space-u.

## 6. CNI chaining

Viac CNI plugins môže byť spojených do jedného zoznamu:

- hlavný plugin vytvorí connectivity,
- ďalší pridá port mapping,
- bandwidth control,
- tuning alebo policy integration.

Poradie a rollback semantics sú dôležité. Partial failure po vytvorení interface-u, ale pred dokončením chainu môže zanechať stale network state.

## 7. NetworkPolicy model

NetworkPolicy vyberá Pods cez `podSelector` a určuje povolený traffic podľa:

- smeru ingress alebo egress,
- peer Pod selectors,
- namespace selectors,
- IP blocks,
- ports a protocols.

Príklad default deny pre ingress aj egress:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

Prázdny selector vyberie všetky Pody v danom namespace.

## 8. Izolovaný a neizolovaný Pod

Bez matching NetworkPolicy je Pod pre daný smer typicky neizolovaný.

Keď aspoň jedna policy vyberie Pod pre ingress:

- Pod je ingress-isolated,
- povolený ingress je union všetkých matching ingress pravidiel.

Rovnako pre egress.

NetworkPolicies sú **aditívne**. Poradie pravidiel neexistuje a policy nemá explicitné deny pravidlo; deny vzniká tým, že traffic nie je zahrnutý v žiadnom povolení.

## 9. Obe strany komunikácie

Aby bol traffic povolený, musí ho dovoliť:

- egress policy source Podu, ak je source egress-isolated,
- ingress policy destination Podu, ak je destination ingress-isolated.

Povolenie iba na jednej strane nestačí, ak je druhá strana izolovaná.

## 10. `podSelector` a `namespaceSelector`

Povolenie z konkrétneho namespace a konkrétnych Podov:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-clients
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              environment: production
          podSelector:
            matchLabels:
              access: api
      ports:
        - protocol: TCP
          port: 8080
```

Keď sú `namespaceSelector` a `podSelector` v jednej peer položke, obvykle ide o logické AND. Dve samostatné peer položky predstavujú alternatívne zdroje.

YAML odsadenie preto mení security semantics.

## 11. Namespace identity

Namespace label `kubernetes.io/metadata.name` umožňuje vybrať konkrétny namespace bez vlastného duplicate labelu:

```yaml
namespaceSelector:
  matchLabels:
    kubernetes.io/metadata.name: monitoring
```

Pre multi-tenant policy však často potrebuješ stabilné organizačné labels spravované admission policy, nie voľne modifikovateľné application tímom.

## 12. `ipBlock`

```yaml
egress:
  - to:
      - ipBlock:
          cidr: 10.20.0.0/16
          except:
            - 10.20.5.0/24
    ports:
      - protocol: TCP
        port: 443
```

`ipBlock` je určený najmä pre IP rozsahy mimo cluster Pod identity modelu.

Caveat:

- NAT môže zmeniť source alebo destination IP pred alebo po policy enforcemente,
- behavior pri Service, NodePort, LoadBalancer a externalTrafficPolicy závisí od dataplane,
- Pod IP rozsahy sa spravidla lepšie vyjadrujú selectors.

## 13. Ports a protocols

NetworkPolicy môže filtrovať TCP, UDP a podľa podpory platformy SCTP.

```yaml
ports:
  - protocol: TCP
    port: 5432
```

Named ports môžu zvýšiť portability, ale implementation musí správne resolve-nuť meno vo vybraných Pods.

NetworkPolicy je primárne L3/L4 model. HTTP paths, methods, identities alebo TLS principals vyžadujú L7 policy, service mesh, gateway alebo application authorization.

## 14. DNS pri default-deny egress

Po zavedení default-deny egress môže prestať fungovať DNS.

Potrebuješ explicitne povoliť traffic na cluster DNS podľa reálneho datapathu:

- UDP/53,
- TCP/53 pre fallback,
- DNS Service/Pod selectors alebo presný IP model,
- prípadne NodeLocal DNSCache adresu a node-local path.

Nepreberaj policy z iného clusteru bez overenia DNS implementation.

## 15. Service a NetworkPolicy

Service selector a EndpointSlice určujú backendy. NetworkPolicy rozhoduje, či je packet k Podu povolený.

Funkčný Service objekt nepreukazuje:

- povolený source egress,
- povolený destination ingress,
- correct Node/dataplane policy state,
- application listen socket.

Pri incidente rozdeľ:

```text
DNS
→ Service/EndpointSlice
→ Service dataplane
→ CNI routing
→ NetworkPolicy
→ Pod socket
```

## 16. Existujúce connections

Keď sa policy alebo matching labels zmenia počas existujúceho connectionu, správanie už nadviazaného flow môže byť implementation-dependent.

Pre bezpečnostne kritickú revokáciu:

- over dataplane semantics,
- prípadne ukonči existujúce sessions,
- rotuj credentials,
- nespoliehaj sa iba na nový NetworkPolicy object.

## 17. Čo štandardná NetworkPolicy nerieši

Štandardný API model nevyjadruje všetky možné požiadavky, napríklad:

- explicitné deny s prioritou,
- FQDN/domain egress,
- HTTP path/method policy,
- TLS workload identity,
- rate limiting,
- global/cluster-wide policy,
- service-account-based peer identity,
- detailed logging action.

Niektoré CNI implementácie poskytujú vendor-specific CRDs. Tie zvyšujú capabilities, ale znižujú portability a vyžadujú vlastný upgrade/policy contract.

## 18. Host traffic a `hostNetwork`

Traffic medzi Podmi a hostom alebo Node-local processes môže mať špeciálne semantics.

`hostNetwork: true` Pod:

- zdieľa Node network namespace,
- nepoužíva bežnú Pod IP boundary,
- môže obchádzať alebo meniť spôsob policy enforcementu podľa implementation.

Rovnako over traffic k:

- kubeletu,
- metadata service,
- node-local DNS,
- host ports,
- runtime alebo CSI sockets.

## 19. Encryption

NetworkPolicy je authorization/filtering mechanizmus, nie encryption.

Pod-to-Pod traffic môže zostať plaintext. Encryption potrebuje:

- application TLS/mTLS,
- mesh dataplane,
- CNI-level wire encryption,
- IPsec/WireGuard alebo cloud-network encryption podľa platformy.

Over, či encryption pokrýva Node-to-Node, same-Node, host traffic a external egress.

## 20. Observability

Základné API evidence:

```bash
kubectl get networkpolicy -A
kubectl describe networkpolicy -n production allow-api-clients
kubectl get pod -n production --show-labels
kubectl get namespace --show-labels
kubectl get endpointslice -n production
```

Node/dataplane evidence závisí od CNI:

- agent status a logs,
- IPAM allocations,
- routes a interfaces,
- eBPF maps alebo firewall rules,
- policy realization status,
- dropped-flow logs,
- tunnel health a MTU.

## 21. Troubleshooting

### `FailedCreatePodSandBox`

Over:

- CNI configuration a binaries,
- node agent readiness,
- IPAM capacity,
- route/tunnel state,
- permissions a mounted CNI directories,
- runtime logs,
- stale namespace/interface state.

### Pod dostal IP, ale nevie komunikovať

Over:

1. route na source Node-e,
2. return route,
3. overlay/tunnel health,
4. MTU,
5. NetworkPolicy na oboch stranách,
6. host firewall/security groups,
7. application listen address.

### Policy nemá efekt

Over, či CNI NetworkPolicy podporuje a či policy vyberá očakávané Pody. Samotné prijatie API objektu negarantuje enforcement.

### Po default-deny nefunguje DNS

Over UDP aj TCP 53, CoreDNS alebo NodeLocal DNSCache path a selectors/IPs.

### Funguje same-Node, nie cross-Node

Silný signál route, tunnel, MTU, cloud firewall alebo node-to-node dataplane problému.

## 22. Anti-patterny

### NetworkPolicy bez podporujúceho dataplane

Objekty existujú, ale traffic zostáva nefiltrovaný.

### Jedna obrovská allow-all policy

Formálne existuje policy, ale nevytvára reálnu segmentation.

### Default deny bez DNS a platform dependencies

Workloads stratia service discovery alebo potrebné control-plane integrations.

### Selektory ovládané nedôveryhodným workload ownerom

Team môže pridať label a získať network access.

### IP allowlist pre dynamické Pody

IP lifecycle a NAT robia policy krehkou.

### NetworkPolicy považovaná za autentifikáciu

Povolený packet nie je overená application identity.

## 23. Kontrolné otázky

1. Akú úlohu má CNI pri vytvorení Pod sandboxu?
2. Aký je rozdiel medzi overlay a routed Pod networkom?
3. Kedy sa Pod stáva ingress alebo egress isolated?
4. Prečo sú NetworkPolicies aditívne?
5. Prečo musí traffic povoliť source egress aj destination ingress?
6. Aký je rozdiel medzi `podSelector`, `namespaceSelector` a `ipBlock`?
7. Prečo default-deny egress často rozbije DNS?
8. Čo štandardná NetworkPolicy nevie vyjadriť?
9. Prečo policy enforcement neznamená encryption?
10. Ako odlíšiš CNI connectivity failure od NetworkPolicy denial?

## Glossary impact

Relevantné pojmy: CNI, CNI `ADD`/`DEL`, IPAM, Pod CIDR, overlay network, routed Pod network, CNI chaining, NetworkPolicy, ingress-isolated Pod, egress-isolated Pod, additive policy, default deny, policy peer, `ipBlock`, policy enforcement point a flow log.

## Oficiálna dokumentácia

- [Cluster networking](https://kubernetes.io/docs/concepts/cluster-administration/networking/)
- [Network plugins](https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/network-plugins/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Declare Network Policy](https://kubernetes.io/docs/tasks/administer-cluster/declare-network-policy/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cluster DNS](cluster-dns.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Volumes, PV, PVC a StorageClass →](volumes-pv-pvc-storageclass.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
