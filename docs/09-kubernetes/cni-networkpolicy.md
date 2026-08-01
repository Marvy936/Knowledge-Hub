# CNI a NetworkPolicy

Kubernetes deklaruje, že Pod má dostať network identity a že Pods majú vedieť komunikovať podľa cluster networking modelu. Konkrétny dataplane vytvára CNI implementácia. Pri vytvorení Pod sandboxu pridelí IP, pripojí interface, nastaví routes a podľa pluginu pripraví overlay, routing, eBPF maps alebo ďalší host state. NetworkPolicy potom opisuje povolené ingress a egress flows, ale enforcement vykonáva CNI alebo iný policy engine.

Pre `payments-api` potrebujeme tri povolené cesty: edge proxy na port 8080, aplikácia do databázovej proxy na 5432 a DNS. Všetky ostatné ingress a egress paths majú byť blokované. Zelený Pod status nestačí; musíme overiť allowed aj forbidden flows z konkrétnych source a destination Podov.

## Kubernetes network model

Základný model predpokladá, že každý Pod má vlastnú IP a Pods sa môžu navzájom adresovať bez application-visible NAT-u v rámci podporovanej cluster architektúry. Host-network a platform extensions môžu boundary meniť.

```text
source process
→ source Pod network namespace
→ veth alebo iný attachment
→ source Node dataplane
→ route, tunnel alebo direct routing
→ destination Node dataplane
→ destination Pod interface
→ destination socket
→ reverse path
```

Service pridáva ďalšiu translation vrstvu pred endpointom. CNI a Service dataplane môžu byť implementované rovnakým produktom, ale konceptuálne sú odlišné.

## CNI ADD a DEL lifecycle

Keď runtime vytvorí Pod sandbox, invokuje CNI ADD s network namespace a Pod metadata. Plugin pridelí IP a nakonfiguruje dataplane. Pri odstránení sandboxu invokuje DEL.

Unknown alebo partial outcome môže ponechať IPAM allocation, interface alebo policy state. Blind ručné mazanie súborov z CNI state directory môže uvoľniť IP, ktorú stále používa živý sandbox.

Pri `FailedCreatePodSandBox` zachovaj Pod UID, sandbox attempt, Node, CNI logs a IPAM state skôr, než reštartuješ runtime.

## Pod CIDR, routes a overlay

Niektoré clustre prideľujú Node-u Pod CIDR a routujú ho priamo. Iné encapsulujú traffic cez VXLAN, Geneve alebo iný tunnel. Cloud integrácie môžu programovať VPC routes alebo virtual interfaces.

Pri cross-Node failure porovnaj:

```text
source Pod IP a Node
source route/tunnel state
destination Pod IP a Node
MTU
host firewall/eBPF policy
reverse route
```

Same-Node success nevylučuje cross-Node tunnel alebo route problém.

## MTU

Overlay pridáva headers a znižuje použiteľnú MTU. Ak Pod interface používa príliš veľkú MTU, malé packets môžu fungovať a väčšie TLS alebo gRPC payloady sa stratia.

Príznaky zahŕňajú úspešný TCP handshake, ale timeout pri väčšom prenose. Diagnostika používa controlled payload sizes a packet capture podľa platformy. Plošné zníženie MTU bez určenia pathu môže maskovať inú chybu.

## NetworkPolicy selection

Policy sa aplikuje na Pods vybrané `podSelector`-om v namespace policy objektu.

Default deny:

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

Po výbere Podu pre ingress alebo egress isolation sú povolené iba flows zodpovedajúce union všetkých relevantných policies. Policies sa bežne nespracúvajú ako ordered firewall rules s prvým matchom; výsledok je aditívne povolenie.

## Povolenie edge ingressu

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: payments-api-ingress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: payments-api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: edge-system
          podSelector:
            matchLabels:
              app: public-gateway
      ports:
        - protocol: TCP
          port: 8080
```

Kombinácia `namespaceSelector` a `podSelector` v jednom peer elemente znamená Pods s daným labelom v namespaces spĺňajúcich selector. Dva samostatné peer elements by znamenali union širších skupín.

Namespace labels musia byť chránené. Ak tenant môže svojvoľne pridať label `edge-access=public`, môže obísť zamýšľanú boundary.

## Povolenie databázového egressu

Egress policy sa vyhodnocuje pre source Pods vybrané `podSelectorom`; destination namespace a Pod selectory následne určujú, ku ktorým endpointom a portom smie traffic odísť. Povolenie databázy preto musí viazať source workload identity, destination namespace identity, database Pod labels, protokol a port. Samotný DNS názov nie je NetworkPolicy subject.

Po aplikovaní treba overiť allowed flow z konkrétneho `payments-api` Pod UID a forbidden flow z neoznačeného Podu alebo na susedný port. Ak databáza stojí mimo Pod networku, treba samostatne modelovať `ipBlock`, NAT a provider implementation; YAML acceptance bez dataplane testu nepreukazuje effective egress.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: payments-api-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: payments-api
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: data-system
          podSelector:
            matchLabels:
              app: postgres-proxy
      ports:
        - protocol: TCP
          port: 5432
```

Ak databáza leží mimo clusteru, `ipBlock` môže byť použiteľný, ale treba rozumieť, či policy engine vidí pre-NAT alebo post-NAT adresu. Cloud load balancer a SNAT môžu meniť source/destination identity.

## DNS egress

Default-deny egress musí povoľovať DNS k actual resolver pathu a často UDP aj TCP 53.

```yaml
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

Tento príklad nemusí zodpovedať NodeLocal DNSCache, kde destination môže byť local IP a nie CoreDNS Pod. Policy sa musí navrhnúť podľa actual architecture.

## NetworkPolicy nemá deny logiku pre všetko

Core API NetworkPolicy rieši L3/L4 Pod traffic podľa podporovaných selectors a IP blocks. Nevyjadruje HTTP paths, DNS names, TLS identities alebo explicitné deny priority. Niektoré CNI produkty pridávajú vlastné CRDs pre L7 alebo global policy; tie sú implementation-specific.

NetworkPolicy tiež nechráni automaticky hostNetwork traffic, Node-local services alebo cloud control-plane paths rovnako vo všetkých implementáciách. Capability treba overiť v cieľovej platforme.

## Egress cez Service

Aplikácia môže volať Service ClusterIP, ale policy engine môže enforcement vyhodnocovať voči endpoint Pod IP alebo pre-NAT Service IP podľa implementácie. Pri policy incidente sa nespoliehaj iba na URL. Zachovaj actual flow tuple pred a po Service translatione.

## Readiness a policy rollout

NetworkPolicy sa môže aplikovať skôr alebo neskôr než application Pod startup podľa controller a dataplane convergence. Pod môže byť Running, ale critical egress ešte nefunguje. Readiness môže zachytiť potrebný dependency path, ale nemá otvárať broad policy ako fallback.

Pri rollout-e policy je bezpečnejší postup:

```text
inventory current flows
→ vytvor explicitné allow policies
→ over allowed a forbidden testy
→ až potom zaveď default deny
→ sleduj affected cohorts
```

Plošné zapnutie default deny bez DNS, metrics, secret alebo control paths môže vyradiť celý namespace.

## Testovanie z controlled Pods

```bash
kubectl run net-debug -n production --rm -it --restart=Never \
  --image=nicolaka/netshoot -- sh
```

Debug Pod musí mať labels a ServiceAccount zodpovedajúce testovanej source identity. Inak testuje inú policy množinu než `payments-api`.

Povolené testy:

```bash
nc -vz postgres-proxy.data-system.svc 5432
curl -fsS http://payments-api.production.svc/readyz
```

Zakázané testy musia explicitne zlyhať, napríklad connection k neautorizovanému namespace-u. Timeout sám nepreukazuje policy deny; route alebo listener môže byť tiež chybný. CNI policy observability alebo packet trace pomôže určiť verdict.

## CNI a Node generation

CNI agent často beží ako DaemonSet a používa host privileges. Nový Node image môže zmeniť kernel, sysctls, nftables backend, cgroup mode alebo required modules. Agent process môže byť Ready, ale dataplane initialization partial.

Node capability canary má overiť:

```text
Pod creation a IPAM
same-Node Pod traffic
cross-Node Pod traffic
Service ClusterIP
DNS
allowed NetworkPolicy flow
forbidden NetworkPolicy flow
MTU-sized payload
```

Až potom má Node vstúpiť do bežného workload poolu.

## Incident: policy vyzerala správne, no povoľovala celý namespace

Autor zamýšľal povoliť iba `public-gateway` Pods v `edge-system`, ale YAML obsahoval dva samostatné peer entries: jeden `namespaceSelector` a druhý `podSelector`. Výsledkom bola union: všetky Pods v edge-system plus všetky Pods s labelom `public-gateway` v production namespace.

Oprava spojila oba selectors do jedného peer objektu a pridala forbidden tests z neautorizovaného Podu. Skorší control je policy unit test nad presnými source/destination identities.

## Incident: NetworkPolicy blokovala iba veľké DNS odpovede

Policy povoľovala UDP/53, nie TCP/53. Bežné Service lookups fungovali, ale veľká external odpoveď bola truncovaná a resolver retryol cez TCP. Aplikácia hlásila intermittent timeouty.

Oprava doplnila TCP k actual DNS destination. Recovery overila malé aj veľké queries a zároveň potvrdila, že direct external DNS zostáva blokované.

## Incident: iba cross-Node traffic zlyhával

Pods na rovnakom Node-e komunikovali. Cross-Node requesty cez overlay timeoutovali. NetworkPolicy observability ukazovala allow verdict. Packet capture odhalil, že nový Node pool mal vyššiu Pod MTU než tunnel path.

Root cause nebola policy. Oprava zladila Node/CNI MTU v immutable image a nahradila affected Nodes. Policy allowed/forbidden tests sa zopakovali po replacement-e.

## Model, ktorý si treba odniesť

CNI vytvára Pod network a host dataplane. NetworkPolicy vyjadruje povolené L3/L4 flows pre vybrané Pods, ale enforcement a observability závisia od implementácie. Pri incidente sleduj exact source/destination Pod UIDs, Nodes, IPs, ports, pre/post-NAT tuple, policy selection a packet path. Vždy over povolené aj zakázané outcomes.

## Referencie

- [Cluster Networking](https://kubernetes.io/docs/concepts/cluster-administration/networking/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [CNI Specification](https://www.cni.dev/docs/spec/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cluster DNS](cluster-dns.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Volumes, PV, PVC a StorageClass →](volumes-pv-pvc-storageclass.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
