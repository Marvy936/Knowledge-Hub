# Service a EndpointSlice

Kubernetes Service poskytuje stabilnú logical network identity pre meniacu sa množinu backendov. EndpointSlice reprezentuje konkrétne backend endpointy, ktoré Service aktuálne môže používať. Service nie je process ani proxy Pod; je API contract, ktorý cluster DNS a Service dataplane implementujú pomocou virtuálnej IP, routingu, load balancing-u alebo external integration.

## 1. Problém dynamických Podov

Pods sa vytvárajú, zanikajú a menia IP. Klient nemá poznať:

- konkrétne Pod mená,
- aktuálny replica count,
- Node placement,
- rollout revision,
- Pod IP lifecycle.

Service poskytuje stabilné:

- meno,
- DNS record,
- port contract,
- virtual IP alebo external exposure model,
- selector-based backend discovery.

## 2. Základný Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: production
spec:
  selector:
    app: web
  ports:
    - name: http
      protocol: TCP
      port: 80
      targetPort: http
```

Relevantné polia:

- `selector` — vyberá backend Pods podľa labels,
- `port` — port Service contractu,
- `targetPort` — backend port alebo pomenovaný container port,
- `protocol` — TCP, UDP alebo SCTP podľa podpory,
- `type` — exposure model,
- `clusterIP` a IP-family fields,
- traffic policy a session-affinity options.

Service selector nevyberá Deployment ani ReplicaSet. Vyberá Pods podľa aktuálnych labels.

## 3. Named `targetPort`

Pod template:

```yaml
ports:
  - name: http
    containerPort: 8080
```

Service:

```yaml
ports:
  - name: http
    port: 80
    targetPort: http
```

Named target port umožňuje, aby rôzne Pod revisions používali odlišné numeric ports pri zachovaní rovnakého logical mena. Počas mixed-version rollout-u musí každý backend poskytovať rovnaký pomenovaný port contract.

`containerPort` je metadata a dokumentácia; application stále musí reálne počúvať na danom socket-e.

## 4. EndpointSlice controller

Pre selector-based Service control plane typicky vytvorí jeden alebo viac EndpointSlice objektov.

```yaml
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  labels:
    kubernetes.io/service-name: web
addressType: IPv4
ports:
  - name: http
    protocol: TCP
    port: 8080
endpoints:
  - addresses: ["10.244.2.17"]
    conditions:
      ready: true
    nodeName: worker-2
    zone: eu-central-1a
```

EndpointSlice obsahuje:

- address type,
- endpoint addresses,
- port/protocol kombináciu,
- readiness/serving/terminating conditions,
- Node a zone metadata,
- ownership/managed-by metadata.

Pre jeden Service môže existovať viac slices. Nesmieš predpokladať 1:1 mapping alebo stabilné meno slice-u.

## 5. Readiness a endpoints

Pod readiness ovplyvňuje, či má byť endpoint bežne použitý na Service traffic.

Dôležité rozlíšenie:

- Pod existuje,
- container beží,
- Pod je Ready,
- EndpointSlice endpoint je ready/serving/terminating,
- Service dataplane už spracoval zmenu,
- client connection už bola presmerovaná.

Tieto stavy sa menia asynchrónne. Krátke propagation okno je súčasťou eventual consistency.

`publishNotReadyAddresses` môže publikovať aj not-ready endpoints, napríklad pre špecifický peer discovery model. Nie je to všeobecná oprava zlej readiness probe.

## 6. Service types

### ClusterIP

Defaultný typ. Poskytuje virtual IP dostupnú v cluster networku.

```yaml
spec:
  type: ClusterIP
```

### NodePort

Otvorí pridelený port na Nodes a smeruje ho na Service backendy.

```yaml
spec:
  type: NodePort
```

NodePort zväčšuje host exposure a potrebuje firewall, source-IP a traffic-policy analýzu.

### LoadBalancer

Žiada cloud controller alebo inú implementation o external load balancer.

```yaml
spec:
  type: LoadBalancer
```

Service object sám nevytvorí load balancer bez podporovanej integrácie. Sleduj status conditions/events a external controller.

### ExternalName

```yaml
spec:
  type: ExternalName
  externalName: database.example.com
```

Vytvára DNS alias semantics, nie L4 proxy. Nemá selector ani bežné EndpointSlices. TLS hostname a application protocol musia zodpovedať aliasovaniu.

## 7. Headless Service

```yaml
spec:
  clusterIP: None
  selector:
    app: database
```

Headless Service neposkytuje jednu virtual ClusterIP. DNS typicky vracia priamo backend addresses.

Použitie:

- StatefulSet stable identities,
- peer discovery,
- application-side load balancing,
- priame spojenie na konkrétne replicas.

Headless Service neznamená automaticky zdravý cluster database protocol. Client musí zvládnuť viac answers, readiness, failover a connection lifecycle.

## 8. Service bez selectoru

Service môže reprezentovať backend mimo Pod selector modelu.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-db
spec:
  ports:
    - name: postgres
      port: 5432
      targetPort: 5432
```

EndpointSlices potom spravuje iný controller alebo operator:

```yaml
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: external-db-1
  labels:
    kubernetes.io/service-name: external-db
    endpointslice.kubernetes.io/managed-by: platform.example.com
addressType: IPv4
ports:
  - name: postgres
    protocol: TCP
    port: 5432
endpoints:
  - addresses: ["192.0.2.20"]
```

Needituj EndpointSlices spravované Kubernetes controllerom. Pri vlastných slices nastav jednoznačný managed-by ownership a lifecycle.

## 9. ClusterIP dataplane

Service ClusterIP typicky nie je interface s processom, ktorý na nej počúva. Je virtual address implementovaná dataplane mechanizmom, napríklad:

- kube-proxy s iptables,
- IPVS,
- nftables podľa platformy/verzie,
- eBPF alebo iná CNI-integrated implementation.

Zjednodušený flow:

```text
client Pod
→ Service ClusterIP:port
→ node Service dataplane
→ selected EndpointSlice backend
→ Pod IP:targetPort
```

DNS resolution a packet forwarding sú samostatné vrstvy. DNS môže fungovať, ale Service dataplane alebo backend môže zlyhávať.

## 10. Session affinity

```yaml
spec:
  sessionAffinity: ClientIP
```

Client-IP affinity môže smerovať klienta na rovnaký backend v rámci timeoutu, ale:

- nie je durable session store,
- NAT môže zdieľať jednu source IP medzi klientmi,
- backend replacement affinity zruší,
- traffic distribution môže byť nevyvážená.

State má byť mimo ephemeral Podu alebo replikovaný podľa application modelu.

## 11. Internal a external traffic policy

Traffic policies môžu ovplyvniť, či sa preferujú iba node-local endpoints alebo cluster-wide backends.

Trade-offy:

- source IP preservation,
- extra network hop,
- load distribution,
- dostupnosť pri Node bez local endpointu,
- topology imbalance.

`Local` policy nie je automatická latency optimalizácia. Môže spôsobiť drop alebo nerovnomerné rozdelenie, ak external load balancer posiela traffic na Nodes bez ready local backendu.

## 12. Topology-aware routing

EndpointSlice môže niesť zone/topology informácie a platforma môže preferovať topology-local traffic.

Ciele:

- znížiť cross-zone latency a cost,
- zachovať locality,
- zároveň neohroziť availability.

Potrebuješ:

- dostatok ready endpoints v každej zóne,
- správne Node zone labels,
- kompatibilnú Service/dataplane implementation,
- metrics pre imbalance a fallback.

## 13. Dual-stack

Service môže používať IPv4, IPv6 alebo dual-stack podľa cluster configuration.

Relevantné fields:

- `ipFamilies`,
- `ipFamilyPolicy`,
- `clusterIPs`,
- EndpointSlice `addressType`.

Jedna EndpointSlice obsahuje jeden address type. Dual-stack Service preto potrebuje samostatné IPv4 a IPv6 slices.

Application a probes musia počúvať na správnych address families. DNS A/AAAA success neznamená, že client network path podporuje obe.

## 14. LoadBalancer lifecycle

Pri `type: LoadBalancer` sleduj viac vrstiev:

```text
Service spec
→ cloud/load-balancer controller
→ external LB resource
→ health-check / NodePort / direct-Pod integration
→ Service or EndpointSlice backends
```

Failure môže byť v:

- cloud credentials/permissions,
- subnet alebo quota,
- controller reconciliation,
- load balancer health checks,
- firewall/security groups,
- source ranges,
- NodePort/dataplane,
- Pod readiness.

External IP v `status` nepreukazuje end-to-end dostupnosť.

## 15. Deletion a connection behavior

Pri Pod termination:

1. Pod readiness/terminating state sa zmení.
2. EndpointSlice controller aktualizuje endpoint conditions.
3. Service dataplane spracuje zmenu.
4. Existujúce connections môžu pokračovať podľa protocol/NAT state-u.
5. Application potrebuje connection draining a grace period.

Service nedokáže vrátiť už odoslaný request. Rollout safety závisí od readiness, endpoint propagation, termination grace a application protocolu.

## 16. Security

Service nie je security policy. Poskytuje reachability abstraction.

Použi samostatne:

- NetworkPolicy alebo dataplane policy,
- TLS/mTLS,
- authentication/authorization,
- firewall/security groups,
- private/public load balancer controls,
- least-privilege controller credentials.

ClusterIP „internal“ neznamená automaticky dôveryhodný alebo šifrovaný traffic.

## 17. Observability

```bash
kubectl get service web -n production -o wide
kubectl describe service web -n production
kubectl get endpointslice -n production \
  -l kubernetes.io/service-name=web -o wide
kubectl get pod -n production -l app=web -o wide
kubectl get pod <pod> -o jsonpath='{.status.conditions}'
```

Overuj:

- selector a Pod labels,
- Service port/targetPort,
- EndpointSlice addresses a conditions,
- Pod readiness,
- application listen sockets,
- dataplane implementation/logs,
- DNS record,
- Node/firewall route.

## 18. Systematický troubleshooting

### Service nemá EndpointSlices alebo sú prázdne

Over selector, Pod labels, namespace, EndpointSlice controller a či ide o selectorless Service.

### Endpointy existujú, ale nie sú ready

Over Pod readiness probes, readiness gates, container status a `publishNotReadyAddresses` zámer.

### DNS meno sa resolve-ne, spojenie timeoutuje

DNS funguje. Over ClusterIP route/dataplane, NetworkPolicy, targetPort, application bind address a backend readiness.

### Priame Pod IP funguje, Service nie

Over Service port mapping, kube-proxy/alternate dataplane, ClusterIP allocation, session/traffic policy a node firewall.

### Service funguje iba z niektorých Nodes

Over node-local dataplane, CNI routes, conntrack, local traffic policy, EndpointSlice sync a Node conditions.

### LoadBalancer má external IP, ale health check je down

Over health-check path/port, NodePort alebo direct endpoint mode, source firewall a readiness.

### Po rollout-e prichádzajú chyby na terminating Pods

Over readiness removal latency, `preStop`, application draining, termination grace, keep-alive connections a load balancer health intervals.

## 19. Anti-patterny

### Service selector príliš všeobecný

Vyberie unrelated alebo staré rollout Pods.

### Ručná editácia controller-managed EndpointSlice

Controller zmenu prepíše a vzniká ownership conflict.

### Používanie Pod IP ako configuration

Obchádza stable discovery a zlyhá pri replacement-e.

### NodePort na všetkých Nodes bez firewall analýzy

Zväčšuje attack surface.

### `externalTrafficPolicy: Local` bez local endpoint coverage

Traffic môže byť zahadzovaný alebo výrazne nevyvážený.

### Service ako security boundary

Bez NetworkPolicy a application security ostáva backend dostupný každému, kto má network path.

### Headless Service považovaný za load balancer

DNS vracia endpoint set; client nesie selection/failover zodpovednosť.

## 20. Kontrolné otázky

1. Aký problém rieši Kubernetes Service?
2. Ako Service selector súvisí s EndpointSlices?
3. Aký je rozdiel medzi `port` a `targetPort`?
4. Prečo je named target port užitočný počas rollout-u?
5. Ako sa líši ClusterIP, NodePort, LoadBalancer a ExternalName?
6. Čo poskytuje headless Service?
7. Prečo DNS success nepreukazuje funkčný Service dataplane?
8. Aké endpoint conditions sú relevantné pri termination?
9. Prečo sa pri jednom Service môže vytvoriť viac EndpointSlices?
10. Ako diagnostikuješ Service bez funkčných backendov?

## Glossary impact

Relevantné pojmy: Kubernetes Service, Service selector, ClusterIP, NodePort, LoadBalancer Service, ExternalName, headless Service, Service port, targetPort, EndpointSlice, endpoint readiness, selectorless Service, Service dataplane, internal/external traffic policy, session affinity, topology-aware routing a dual-stack Service.

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
