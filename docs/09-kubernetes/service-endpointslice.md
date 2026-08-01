# Service a EndpointSlice

Pod IP je runtime identita jednej Pod generation. Pri replacement-e sa môže zmeniť. Service poskytuje stabilný názov a virtual adresu nad dynamickou skupinou backendov. EndpointSlice potom materializuje konkrétne IP adresy, porty a readiness conditions, ktoré Service dataplane môže používať.

Pri `payments-api` klient neposiela request na jeden Pod name. Používa Service `payments-api.production.svc`. Selector vyberie Pods s labelom `app=payments-api`, EndpointSlice controller publikuje ich endpoints a per-Node dataplane presmeruje packet na jeden vhodný Pod.

## Service je stabilný frontend contract

```yaml
apiVersion: v1
kind: Service
metadata:
  name: payments-api
  namespace: production
spec:
  selector:
    app: payments-api
  ports:
    - name: http
      port: 80
      targetPort: http
  type: ClusterIP
```

`port: 80` je Service port. `targetPort: http` sa mapuje na named container port backend Podu. `clusterIP` pridelí API server podľa cluster configuration.

Service object neotvára process socket. Ak backend aplikácia nepočúva na resolved target porte alebo počúva iba na Pod loopbacku, packet path zlyhá aj pri správnom Service YAML.

## Selector a backend membership

Service selector vytvára dynamickú množinu Podov:

```bash
kubectl get pods -n production -l app=payments-api --show-labels
```

Readiness ovplyvňuje, či endpoint dostane serving/ready condition podľa controller semantics. Nesprávny label môže pridať debug alebo staging Pod. Chýbajúci label môže odpojiť zdravú repliku.

Service selector nepracuje s Deployment owner graphom. Pod s rovnakými labels môže byť vybraný aj bez očakávaného ReplicaSet ownera. Preto pri incidente kontroluj aj Pod UID, ownerReference a image digest.

## EndpointSlice ako konkrétny backend inventory

```bash
kubectl get endpointslices -n production \
  -l kubernetes.io/service-name=payments-api -o yaml
```

EndpointSlice môže obsahovať:

```yaml
endpoints:
  - addresses:
      - 10.42.3.17
    conditions:
      ready: true
      serving: true
      terminating: false
    targetRef:
      kind: Pod
      namespace: production
      name: payments-api-7d6f9d8b7b-k4m2p
      uid: <pod-uid>
ports:
  - name: http
    port: 8080
    protocol: TCP
```

`targetRef.uid` umožňuje priradiť endpoint ku konkrétnemu Pod lifetime-u. IP adresa samotná sa môže neskôr znovu použiť.

EndpointSlice je control-plane inventory. Per-Node dataplane ho ešte musí spracovať. Zelený EndpointSlice preto nepreukazuje, že packet translation na každom Node-e je správna.

## Named ports a rollout compatibility

Service môže odkazovať na named `targetPort`. Old a new Pod revision potom môžu používať rovnaký názov portu, aj keď sa numeric port zmení.

```yaml
ports:
  - name: http
    containerPort: 8080
```

Počas rolling update-u však musí každý backend zodpovedať Service contractu. Ak nová revision premenovala port z `http` na `web`, EndpointSlice môže pre časť Podov chýbať správny port alebo Service path zlyhá.

## ClusterIP dataplane

ClusterIP nie je fyzická interface na každom Node-e v jednoduchom zmysle. Service implementation programuje packet translation cez kube-proxy alebo alternatívny dataplane, napríklad eBPF.

```text
client Pod
→ DNS vyrieši Service ClusterIP
→ packet na ClusterIP:80
→ per-Node Service dataplane vyberie endpoint
→ destination Pod IP:8080
→ application response
```

Pri timeout-e testuj vrstvy oddelene:

```bash
# DNS
getent hosts payments-api.production.svc.cluster.local

# Service path
curl -fsS http://payments-api.production.svc/readyz

# Direct Pod path z controlled debug Podu
curl -fsS http://<pod-ip>:8080/readyz
```

Direct Pod IP fungujúca pri zlyhávajúcom ClusterIP presúva hypotézu na Service translation, policy alebo return path. Neznamená automaticky kube-proxy bug; selector, endpoint port alebo source-specific policy môžu byť stále chybné.

## Headless Service

Headless Service používa:

```yaml
spec:
  clusterIP: None
```

DNS potom publikuje backend adresy namiesto jednej virtual ClusterIP podľa Service a EndpointSlice semantics. Používa sa pri StatefulSet discovery alebo client-side load balancing.

Headless Service neposkytuje automatickú leader selection ani connection balancing. Klient musí správne interpretovať viac adries, readiness a DNS caching.

## Service bez selectoru

Service môže existovať bez selectoru a backends sa môžu definovať cez EndpointSlice spravovaný iným controllerom alebo operátorom.

Taký model je vhodný pre external alebo migration endpointy, ale ownership je odlišný. Ručne vytvorený EndpointSlice potrebuje správny label `kubernetes.io/service-name`, porty a lifecycle. API server môže chrániť proxying na niektoré endpoint typy z bezpečnostných dôvodov.

## NodePort

```yaml
spec:
  type: NodePort
```

NodePort sprístupní Service na porte z prideleného rozsahu na Nodes podľa implementation a traffic policy. Neznamená, že cloud firewall, host firewall alebo external route povoľuje prístup.

```bash
kubectl get service payments-api -n production \
  -o custom-columns='CLUSTER_IP:.spec.clusterIP,NODE_PORT:.spec.ports[0].nodePort'
```

NodePort exposure treba kontrolovať cez bind addresses, security groups a source ranges platformy. Nie je to automaticky bezpečný internet endpoint.

## LoadBalancer

Service typu LoadBalancer požiada cloud alebo iného controllera o external load balancer:

```yaml
spec:
  type: LoadBalancer
```

`status.loadBalancer.ingress` ukazuje controller observation, nie kompletnú edge readiness. External listener, health checks, routes, firewall a DNS majú vlastný state.

`loadBalancerClass` môže vybrať konkrétnu implementáciu podľa platformy. Annotations sú controller-specific contract a musia byť versionované a validované.

## Traffic policies

`externalTrafficPolicy` a `internalTrafficPolicy` ovplyvňujú, či traffic môže ísť na cluster-wide alebo node-local endpoints podľa podporovaných semantics.

`Local` môže zachovať source IP a znížiť hop, ale Node bez local ready endpointu nemusí obslúžiť traffic. External load balancer health check musí zodpovedať tejto topológii.

Topology-aware routing alebo traffic distribution features závisia od Kubernetes verzie a implementácie. Pri ich použití over reálny EndpointSlice hints/state a fallback správanie.

## Session affinity

Service môže používať client IP session affinity. Nie je to application session correctness ani durable stickiness. NAT, proxies, client population a backend replacement môžu zmeniť mapping.

State, ktorý vyžaduje stabilné priradenie, má mať explicitný external store alebo protocol, nie závisieť iba od Service affinity.

## Terminating endpoints a graceful drain

Pri termination sa Pod readiness a EndpointSlice conditions menia. Dataplane a external load balancer potrebujú čas na convergence, zatiaľ čo application dokončuje in-flight requests.

```text
Pod deletionTimestamp
→ endpoint terminating/ready transition
→ nové connections sa prestanú posielať
→ staré connections dobehnú
→ process skončí
```

Ak aplikácia ukončí listener okamžite po SIGTERM, môže prerušiť requests, ktoré už boli nasmerované. Ak zostane Ready príliš dlho, môže prijímať nové requests počas shutdownu.

## Incident: Service existuje, ale nemá endpoints

```bash
kubectl get service payments-api -n production -o yaml
kubectl get endpointslices -n production \
  -l kubernetes.io/service-name=payments-api
```

Service mala selector `app=payment-api`, zatiaľ čo Pods používali `app=payments-api`. ClusterIP a DNS boli správne, ale backend inventory bol prázdny.

Oprava zmenila versionovaný Service selector. Recovery overila EndpointSlice targetRef UIDs, Service request a forbidden selection debug Podov.

## Incident: EndpointSlice je správny, jeden Node timeoutuje

Pods, Service aj EndpointSlices boli rovnaké. Requesty z Podov na starých Nodes fungovali, z nového Node poolu zlyhávali. Direct Pod IP aj ClusterIP z nových Nodes mali odlišné výsledky podľa flow.

Root cause bola partial Service dataplane inicializácia na novej Node image. Control-plane objects boli správne. Containment cordonovalo novú cohortu a oprava nahradila Nodes po capability canary.

## Incident: rollout poslal traffic na debug Pod

Debug Pod mal label `app=payments-api` a jednoduchý HTTP server na rovnakom named porte. Service ho zaradila do EndpointSlice, hoci nepatril Deploymentu. Časť payment requestov dostala nesprávnu odpoveď.

Oprava zaviedla presnejší selector, oddelený debug namespace a admission policy pre chránené application labels. Overenie zahŕňalo owner UID každého endpointu.

## Model, ktorý si treba odniesť

Service poskytuje stabilný frontend contract. EndpointSlice materializuje konkrétne backend identities a conditions. Per-Node dataplane potom realizuje packet translation. Úspech každej vrstvy treba overiť samostatne: selector, EndpointSlice, Pod socket, Service path, external load balancer a business request.

## Referencie

- [Services, Load Balancing, and Networking](https://kubernetes.io/docs/concepts/services-networking/service/)
- [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)
- [Virtual IPs and Service Proxies](https://kubernetes.io/docs/reference/networking/virtual-ips/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: ServiceAccount](serviceaccount.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ingress a Gateway API →](ingress-gateway-api.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
