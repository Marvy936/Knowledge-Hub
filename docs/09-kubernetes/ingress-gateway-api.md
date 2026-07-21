# Ingress a Gateway API

Ingress a Gateway API deklarujú pravidlá pre smerovanie trafficu k Kubernetes Services. Samotný API objekt neposkytuje dataplane. Potrebuje controller a konkrétnu implementation, ktorá vytvorí alebo nakonfiguruje load balancer, reverse proxy, cloud routing alebo iný network dataplane.

Ingress je stabilný, jednoduchší HTTP/HTTPS routing API. Gateway API je novší, role-oriented a rozšíriteľnejší model pre north-south, east-west a service-mesh routing. Kubernetes projekt pre nové funkcionality odporúča Gateway API; Ingress zostáva podporovaným stabilným API, ale jeho feature model je zámerne obmedzený.

## 1. Vrstvy problému

Rozlišuj:

```text
DNS
→ external/internal load balancer address
→ Ingress/Gateway dataplane
→ routing rule
→ Kubernetes Service
→ EndpointSlice
→ Ready Pod
→ application listen socket
```

Funkčný Ingress alebo Gateway status nepreukazuje, že každá downstream vrstva funguje.

## 2. Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
  namespace: production
spec:
  ingressClassName: nginx
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web
                port:
                  name: http
```

Ingress definuje:

- host rules,
- HTTP paths,
- backend Services,
- voliteľné TLS references,
- class/controller selection.

Ingress typicky nerieši ľubovoľné TCP/UDP routing bez implementation-specific rozšírení.

## 3. Ingress controller

Ingress resource je iba desired configuration. Controller:

1. sleduje Ingress, IngressClass, Services, EndpointSlices a Secrets,
2. validuje alebo interpretuje pravidlá,
3. konfiguruje dataplane,
4. aktualizuje status a Events,
5. spravuje external resources podľa implementation.

Bez controlleru zostane Ingress iba API objektom bez traffic efektu.

V clustri môže byť viac controllerov. `ingressClassName` musí jednoznačne vybrať správny IngressClass/controller.

## 4. IngressClass

```yaml
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: nginx
spec:
  controller: k8s.io/ingress-nginx
```

IngressClass identifikuje controller implementation a môže odkazovať na controller-specific parameters.

Riziká:

- chýbajúca alebo nesprávna class,
- viac default classes,
- controller sleduje iba vybrané namespaces,
- class parameter resource chýba alebo je neplatný,
- migration medzi controllermi mení semantics annotations a defaults.

## 5. Path types

Ingress podporuje path types:

- `Exact`,
- `Prefix`,
- `ImplementationSpecific`.

`ImplementationSpecific` presúva význam na controller a znižuje portability. Pri `Prefix` a `Exact` stále over normalizáciu URL, trailing slash, percent encoding a precedence podľa implementation a API pravidiel.

Routing testuj na konkrétnych edge cases, nie iba na `/`.

## 6. Default backend

Ingress môže mať default backend pre requests, ktoré nezodpovedajú pravidlám.

```yaml
spec:
  defaultBackend:
    service:
      name: default-backend
      port:
        number: 8080
```

Default backend má mať explicitný security a observability contract. Nemá nevedomky sprístupniť interný admin endpoint alebo vracať citlivé debug informácie.

## 7. TLS

```yaml
spec:
  tls:
    - hosts:
        - app.example.com
      secretName: app-example-com-tls
```

TLS Secret musí existovať v príslušnom namespace podľa Ingress API/controller semantics a obsahovať správny certificate/key pair.

Over:

- SAN hostname,
- chain a trust,
- expiry,
- SNI routing,
- minimum TLS version a ciphers podľa controller policy,
- certificate rotation a reload,
- redirect HTTP → HTTPS,
- backend TLS, ak sa traffic re-encryptuje.

TLS termination na edge nerieši automaticky encryption medzi controllerom a backend Service.

## 8. Annotations

Ingress často používa controller-specific annotations pre:

- rewrites,
- authentication,
- rate limits,
- timeouts,
- body size,
- TLS behavior,
- load-balancer features.

Annotations sú neštandardné API extensions. Riziká:

- vendor/controller lock-in,
- zmena semantics pri upgrade,
- stringly typed configuration,
- injection alebo privilege escalation cez nebezpečné directives,
- rozdiel medzi accepted objectom a reálne aplikovanou konfiguráciou.

Používaj admission policy a approved annotation allowlist.

## 9. Limity Ingress modelu

Ingress má jednoduchý model, ale slabšie vyjadruje:

- oddelenie platform a application ownershipu,
- cross-namespace references,
- traffic splitting,
- header/query matching,
- viac protocol families,
- explicitný attachment lifecycle,
- portable status conditions.

Tieto oblasti rieši Gateway API systematickejšie.

## 10. Gateway API resources

Základný model:

```text
GatewayClass
→ Gateway
→ HTTPRoute / GRPCRoute / TLSRoute / TCPRoute / UDPRoute
→ Service backend
```

### GatewayClass

Cluster-scoped class spravovaná konkrétnym controllerom.

### Gateway

Konkrétna infraštruktúrna traffic entry point definujúca listeners, addresses, TLS a allowed Routes.

### Route

Application routing policy pripojená ku Gateway listeneru alebo inému podporovanému parentu.

Gateway API oddeľuje role:

- infrastructure provider/controller owner,
- cluster/platform operator,
- application developer.

## 11. GatewayClass

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: managed-gateway
spec:
  controllerName: example.net/gateway-controller
```

GatewayClass status ukazuje, či ju controller prijal. Samotná existencia CRD a objektu neznamená, že controller beží alebo class je podporovaná.

## 12. Gateway

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: public
  namespace: infrastructure
spec:
  gatewayClassName: managed-gateway
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      hostname: "*.example.com"
      tls:
        mode: Terminate
        certificateRefs:
          - kind: Secret
            name: wildcard-example-com
      allowedRoutes:
        namespaces:
          from: Selector
          selector:
            matchLabels:
              gateway-access: public
```

Gateway listener definuje:

- protocol a port,
- hostname scope,
- TLS mode/certificates,
- ktoré Routes sa môžu pripojiť,
- status conditions.

Platform team môže vlastniť Gateway, zatiaľ čo application teams vlastnia Routes vo svojich namespaces.

## 13. HTTPRoute

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: web
  namespace: production
spec:
  parentRefs:
    - name: public
      namespace: infrastructure
      sectionName: https
  hostnames:
    - app.example.com
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: web-v1
          port: 80
          weight: 90
        - name: web-v2
          port: 80
          weight: 10
```

HTTPRoute môže podľa supported feature setu vyjadriť:

- host/path/header/query matching,
- weighted backends,
- redirects a rewrites,
- request/response header modifiers,
- traffic policy extensions,
- route attachment status.

Controller nemusí podporovať všetky extended features. Over GatewayClass conformance a Route conditions.

## 14. Route attachment

Route sa nestane aktívnou iba preto, že obsahuje `parentRefs`.

Musí platiť:

- parent Gateway existuje,
- listener povoľuje namespace a Route kind,
- hostname/protocol sú kompatibilné,
- controller Route prijal,
- backend references sú resolvable,
- cross-namespace references majú povolenie.

Sleduj conditions ako:

- `Accepted`,
- `ResolvedRefs`,
- `Programmed` alebo implementation-specific relevantné conditions na parent resource.

## 15. ReferenceGrant

Cross-namespace backend alebo Secret reference potrebuje explicitný trust contract.

```yaml
apiVersion: gateway.networking.k8s.io/v1beta1
kind: ReferenceGrant
metadata:
  name: allow-web-route
  namespace: shared-services
spec:
  from:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      namespace: production
  to:
    - group: ""
      kind: Service
      name: shared-api
```

ReferenceGrant vytvára povolenie v namespace referencovaného objektu. Consumer namespace si nemôže jednostranne udeliť prístup k cudziemu Service alebo Secretu.

Použitá API verzia závisí od nainštalovanej verzie Gateway API CRDs; vždy kontroluj discovery a release compatibility.

## 16. Gateway API nie je automaticky súčasťou clusteru

Gateway API resources sú distribuované ako samostatné CRDs a potrebujú kompatibilný controller.

Pred použitím over:

```bash
kubectl api-resources | grep gateway
kubectl get gatewayclass
kubectl get crd | grep gateway.networking.k8s.io
```

Kubernetes upgrade automaticky nemusí upgradovať Gateway API CRDs alebo controller. Ich lifecycle, conversion a compatibility sú samostatná platformová zodpovednosť.

## 17. Ingress vs. Gateway API

| Oblasť | Ingress | Gateway API |
|---|---|---|
| Základný model | jeden routing resource | class, gateway a routes |
| HTTP routing | áno | áno, expresívnejšie |
| Role separation | obmedzené | explicitné |
| Cross-namespace | obmedzené/controller-specific | controlled cez attachment/ReferenceGrant |
| Traffic splitting | typicky annotation-specific | portable backend weights |
| Protocols | hlavne HTTP/HTTPS | viac Route kinds |
| Extensibility | annotations | typed API + policy/extension model |
| Installation | built-in stable API | samostatné CRDs + controller |

Voľba závisí od platform supportu, portability, migration nákladov a required features.

## 18. External DNS a certificates

Ingress/Gateway status môže publikovať address, ale DNS record môže spravovať:

- platform operator,
- external-dns controller,
- cloud integration,
- samostatný IaC pipeline.

Certificate môže spravovať:

- cert-manager,
- cloud certificate service,
- internal PKI,
- manuálny Secret workflow.

Routing, DNS a certificate lifecycle sú tri odlišné control loops. Incident diagnostikuj podľa ownera každého stavu.

## 19. Traffic policies

Routing layer potrebuje explicitné defaults pre:

- connection a request timeouty,
- retries,
- maximum body/header size,
- rate limiting,
- load-balancing policy,
- source IP a proxy protocol,
- forwarded headers,
- WebSocket/gRPC support,
- backend TLS a certificate validation.

Neobmedzené retries môžu znásobiť load. Príliš dlhé timeouty zadržia connections a capacity. Policy musí zodpovedať application SLO a idempotency.

## 20. Security

Chráň:

- právo vytvárať Ingress/Routes,
- annotations a filters schopné meniť proxy configuration,
- Gateway listeners a addresses,
- TLS Secrets a certificateRefs,
- cross-namespace ReferenceGrants,
- controller ServiceAccount a cloud credentials,
- admin/debug endpoints controllera,
- source ranges a firewall.

Route author nesmie automaticky získavať možnosť referencovať ľubovoľný backend alebo certificate v inom namespace.

## 21. Observability

```bash
kubectl get ingress -A
kubectl describe ingress web -n production
kubectl get ingressclass
kubectl get gatewayclass
kubectl get gateway -A
kubectl get httproute -A
kubectl describe httproute web -n production
kubectl get service,endpointslice -n production
```

Sleduj:

- object generation a observed status,
- Accepted/ResolvedRefs/Programmed conditions,
- assigned address,
- controller logs a metrics,
- generated cloud/load-balancer resource,
- TLS handshake/certificate,
- backend Service EndpointSlices,
- application response a latency.

## 22. Troubleshooting

### Object existuje, ale address chýba

Over controller, class, permissions, cloud quota/subnets, GatewayClass acceptance a Events.

### Ingress vracia default backend alebo 404

Over Host header, pathType/path, controller class, rule precedence, rewrite annotations a resolved controller configuration.

### Gateway Route nie je `Accepted`

Over parentRefs, listener section, allowedRoutes, namespace selector, hostname/protocol compatibility a controller support.

### `ResolvedRefs=False`

Over backend Service, port, TLS Secret, ReferenceGrant, namespace a supported kind/group.

### TLS certificate je nesprávny

Over SNI hostname, listener/Ingress host, Secret reference, certificate chain, controller reload a default certificate fallback.

### Edge odpovedá 502/503

Routing dataplane beží, backend zlyháva. Over Service, EndpointSlices, readiness, targetPort, NetworkPolicy a application listen socket.

### Funguje priamo cez Service, ale nie cez Gateway/Ingress

Over route matching, backend protocol, Host header, TLS termination/re-encryption, timeouty, rewrite a controller network access.

## 23. Anti-patterny

### Ingress bez controllera

API objekt nevytvorí dataplane.

### Kritická logika v neštandardných annotations bez testov

Upgrade controllera môže zmeniť semantics.

### Jedna shared Gateway bez allowedRoutes boundary

Každý namespace môže ovplyvniť spoločný edge routing.

### Cross-namespace backend bez ReferenceGrant ownershipu

Porušuje provider namespace trust boundary.

### TLS termination považovaná za end-to-end encryption

Backend traffic môže zostať plaintext.

### Automatické retries pre ne-idempotentné requests

Môžu zdvojiť side effects.

### DNS, load balancer a Route spravované bez jasného ownera

Failure zostane medzi control loops bez zodpovednosti.

## 24. Kontrolné otázky

1. Prečo Ingress object bez controllera nefunguje?
2. Akú úlohu má IngressClass?
3. Aké sú Ingress path types?
4. Prečo Kubernetes odporúča Gateway API pre nové routing capabilities?
5. Ako sa líši GatewayClass, Gateway a HTTPRoute?
6. Čo znamenajú Route conditions `Accepted` a `ResolvedRefs`?
7. Načo slúži ReferenceGrant?
8. Prečo Gateway API potrebuje samostatné CRDs a controller?
9. Ako odlíšiš edge routing problém od Service/backend problému?
10. Ktoré traffic policy defaults treba definovať produkčne?

## Glossary impact

Relevantné pojmy: Ingress, Ingress controller, IngressClass, pathType, default backend, Gateway API, GatewayClass, Gateway, listener, HTTPRoute, parentRef, backendRef, allowedRoutes, ReferenceGrant, route attachment, Accepted condition, ResolvedRefs condition, traffic splitting, TLS termination a backend re-encryption.

## Oficiálna dokumentácia

- [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [Ingress Controllers](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/)
- [Gateway API](https://kubernetes.io/docs/concepts/services-networking/gateway/)
- [Gateway API documentation](https://gateway-api.sigs.k8s.io/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Service a EndpointSlice](service-endpointslice.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Cluster DNS →](cluster-dns.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
