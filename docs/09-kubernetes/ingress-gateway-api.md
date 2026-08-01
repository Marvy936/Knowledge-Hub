# Ingress a Gateway API

Ingress a Gateway API opisujú north–south routing do Kubernetes služieb. Nevytvárajú dataplane samy. Controller musí sledovať API objekty, nakonfigurovať load balancer alebo proxy a zapísať status. DNS, TLS certificates, cloud firewall, Service, EndpointSlice a backend Pods zostávajú samostatnými vrstvami.

Pre `payments-api` chce platforma publikovať `https://payments.atlas.example/api`. Klientský request prejde cez DNS, external load balancer, Gateway alebo Ingress listener, route matching, Service `payments-api`, EndpointSlice a Pod socket. Zelený Route status nepreukazuje celý tento reťazec.

## Ingress ako starší spoločný model

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: payments-api
  namespace: production
spec:
  ingressClassName: public-nginx
  tls:
    - hosts:
        - payments.atlas.example
      secretName: payments-tls
  rules:
    - host: payments.atlas.example
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: payments-api
                port:
                  name: http
```

IngressClass vyberá controller. Bez fungujúceho controllera zostane Ingress iba desired object. Controller-specific annotations rozširujú správanie, ale znižujú portability a musia byť súčasťou reviewovaného contractu.

```bash
kubectl get ingressclass
kubectl get ingress payments-api -n production -o yaml
```

Status môže obsahovať external address, no DNS alebo listener ešte nemusia byť pripravené.

## Path matching

`pathType` mení matching semantics. `Exact` vyžaduje presnú cestu. `Prefix` matchuje po path segmentoch podľa Kubernetes contractu. `ImplementationSpecific` necháva časť správania controlleru.

Broad prefix pred špecifickejšou cestou, rewrite annotation alebo regex extension môže poslať request do nesprávnej služby. Pri incidente vždy porovnaj source API objekt s resolved controller konfiguráciou alebo statusom, ak ho implementácia poskytuje.

## TLS termination

TLS Secret typicky obsahuje certificate a private key:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: payments-tls
  namespace: production
type: kubernetes.io/tls
```

Ingress controller musí Secret načítať a priradiť správnemu hostu. Certificate existence v API nepreukazuje, že proxy načítala novú generation alebo že klient dostáva správny chain.

```bash
openssl s_client -connect payments.atlas.example:443 \
  -servername payments.atlas.example </dev/null
```

Tento test číta skutočný edge certificate. Neoveruje backend request.

## Gateway API rozdeľuje responsibilities

Gateway API oddeľuje infrastructure ownera, cluster operatora a application route ownera. GatewayClass vyberá implementáciu. Gateway definuje listeners a infrastructure attachment. HTTPRoute alebo iný Route typ definuje routing k backends.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: public
  namespace: edge-system
spec:
  gatewayClassName: atlas-public
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      hostname: "*.atlas.example"
      tls:
        mode: Terminate
        certificateRefs:
          - kind: Secret
            name: wildcard-atlas-tls
      allowedRoutes:
        namespaces:
          from: Selector
          selector:
            matchLabels:
              edge-access: public
```

Application namespace vytvorí route:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: payments-api
  namespace: production
spec:
  parentRefs:
    - name: public
      namespace: edge-system
      sectionName: https
  hostnames:
    - payments.atlas.example
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api
      backendRefs:
        - name: payments-api
          port: 80
```

Tento model umožňuje platforme vlastniť Gateway a aplikácii Route bez práva meniť celý shared listener.

## Attachment a status conditions

HTTPRoute musí byť prijatá parent Gatewayom a references musia byť resolved.

```bash
kubectl get httproute payments-api -n production -o yaml
```

Conditions môžu ukazovať `Accepted`, `ResolvedRefs` alebo implementačne relevantné reasons. Condition treba čítať spolu s `observedGeneration`.

`Accepted=True` znamená, že controller route prijal do svojho modelu. Neznamená, že DNS ukazuje na správnu adresu, certificate je dôveryhodný alebo backend Service má ready endpoints.

## Cross-namespace references

Gateway API používa explicitný `ReferenceGrant` pre vybrané cross-namespace references. To zabraňuje tomu, aby route v jednom namespace svojvoľne odkazovala na Secret alebo Service v inom namespace.

```yaml
apiVersion: gateway.networking.k8s.io/v1beta1
kind: ReferenceGrant
metadata:
  name: allow-edge-gateway
  namespace: production
spec:
  from:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      namespace: edge-system
  to:
    - group: ""
      kind: Service
```

Presná API verzia a podporované Route types závisia od cieľového clusteru a implementácie. Contract treba overiť cez discovery a controller documentation.

## Request path po vrstvách

Pri externom 502 alebo timeout-e rozdeľ cestu:

```text
DNS A/AAAA/CNAME
→ client TLS handshake
→ external load balancer
→ Gateway/Ingress listener
→ host/path match
→ backend Service a port
→ EndpointSlice
→ Pod IP a application socket
→ dependency
→ response a reverse path
```

Praktické observation points:

```bash
dig payments.atlas.example
curl -vk https://payments.atlas.example/api/readyz
kubectl get gateway -n edge-system public -o yaml
kubectl get httproute -n production payments-api -o yaml
kubectl get service,endpointslices -n production
```

Controlled debug Pod môže testovať Service priamo. Ak Service path funguje a external edge nie, application nie je prvá failure boundary.

## Controller identity a resolved configuration

Ingress alebo Gateway controller je bežiaci workload s vlastným image, config, RBAC a cloud identity. API object môže byť validný, ale controller ho nemusí sledovať pre nesprávnu class, namespace selector alebo leader-election problém.

```bash
kubectl get pods -n <controller-namespace> -o wide
kubectl logs -n <controller-namespace> deployment/<controller-name>
```

Controller logs sú užitočné, ale nemajú byť jediným dôkazom. Status conditions, cloud resource read-back a actual request test sú rovnako dôležité.

## Backend protocol a health checks

Edge proxy môže hovoriť ku Service cez HTTP, HTTPS, HTTP/2 alebo implementation-specific protocol. Nesprávna backend protocol annotation môže vytvoriť 502, hoci Pod odpovedá pri priamom HTTP teste.

External load balancer health check path môže byť odlišná od Kubernetes readiness. Backend môže byť Ready v Kubernetes, ale external LB ho považuje za unhealthy pre zlý port, Host header alebo path.

## Header a proxy trust

Proxy môže pridávať `Forwarded` alebo `X-Forwarded-*` headers. Aplikácia ich smie dôverovať iba od známej proxy boundary. Slepo prijatý client-supplied `X-Forwarded-Proto` alebo host môže ovplyvniť redirect, secure-cookie alebo audit behavior.

Source IP preservation závisí od load balancer modelu, proxy protocolu a traffic policy. Application nemá robiť authorization iba podľa client IP bez overeného trust chainu.

## Timeouts, retries a duplicate side effects

Ingress alebo Gateway proxy môže mať connect, request a idle timeouts. Niektoré implementácie retryujú vybrané failures. Pri payment POST môže retry po unknown outcome vytvoriť duplicate authorization, ak aplikácia nemá idempotency key.

Edge retry policy je availability control, nie exactly-once guarantee. Business API musí byť bezpečné voči opakovaniu alebo vedieť reconcile-nuť výsledok.

## Canary a traffic splitting

Gateway API alebo controller extensions môžu rozdeliť traffic medzi backends. Percentuálny weight opisuje routing intent, nie presný počet requestov v malom okne. Sticky sessions, retries a connection reuse môžu meniť pozorovaný podiel.

Canary verdict potrebuje koreláciu:

```text
route generation
→ backend Service/Deployment revision
→ request cohort
→ technical a business metrics
→ abort alebo promotion
```

## Incident: Route bola Accepted, ale vracala 404

HTTPRoute mala `Accepted=True` a `ResolvedRefs=True`. Listener hostname bol `*.atlas.example`, route hostname správny. Request `/api/payments` však skončil na default backende.

Controller resolved path podľa segmentového `PathPrefix`, ale route mala value `/api/` a implementation normalizovala trailing slash odlišne od očakávania v použitom extension filteri. Oprava zjednotila path contract a pridala external route test pre exact paths.

## Incident: nový TLS Secret sa nepoužil

Cert-manager vytvoril nový Secret generation. Gateway object referencoval rovnaké stabilné meno a status bol zelený, no controller nedostal watch event pre RBAC chybu po upgrade-e. Edge stále podával starý expirovaný certificate.

Kubernetes Secret bol správny. Oprava obnovila controller RBAC/watch, reloadla konfiguráciu kontrolovaným rolloutom a overila actual certificate fingerprint z internetu.

## Incident: Service fungovala, external traffic nie

Direct Service a Pod tests boli úspešné. External requests timeoutovali iba z IPv6 klientov. DNS publikoval A aj AAAA, ale load balancer listener bol pripravený iba pre IPv4 a firewall nepovoľoval IPv6 path.

Ingress YAML ani Pod readiness neboli root cause. Recovery opravila dual-stack edge contract a testovala A aj AAAA cohorts.

## Model, ktorý si treba odniesť

Ingress a Gateway API opisujú routing intent. Controller ho musí prijať, vyrenderovať do dataplane-u a pripojiť k external infrastructure. Úspešná condition je iba jedna vrstva. Skutočný verdict spája DNS, TLS, listener, route match, Service, EndpointSlice, Pod socket, dependency a business response.

## Referencie

- [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [Ingress Controllers](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/)
- [Gateway API](https://gateway-api.sigs.k8s.io/)
- [Gateway API Concepts](https://gateway-api.sigs.k8s.io/concepts/api-overview/)
