# Ingress a Gateway API

Ingress a Gateway API deklarujú protocol-aware routing intent. API object však neprijíma client connection. Effective request path vznikne až vtedy, keď správny controller prijme object generation, vyrieši references a ownership, naprogramuje konkrétny dataplane, zverejní address, TLS identity a route a následne traffic prejde cez Service a EndpointSlice k application procesu.

Dominantný lifecycle:

```text
external alebo internal route intent a ownership inventory
→ IngressClass alebo GatewayClass/controller selection
→ admitted Ingress/Gateway/Route generations
→ parent attachment, listener a reference authorization
→ controller reconciliation a resolved configuration
→ programmed dataplane generation
→ address, DNS a certificate control loops
→ listener, TLS a route-match decision
→ Service a EndpointSlice backend path
→ application response a business verification
→ exposure transition, rollback/recovery a cleanup
```

Kapitola používa Atlas Payments. Verejný hostname `pay.example.com` smeruje cez shared platform Gateway na Service `payments-api`. Platform team vlastní Gateway a certificate. Payments team vlastní HTTPRoute. Request `pay-8842` musí:

```text
resolve-nuť správny edge address
→ overiť TLS identity pay.example.com
→ pripojiť sa k accepted listeneru
→ matchnúť presnú Route generation
→ smerovať na accepted Service/EndpointSlice cohortu
→ autorizovať payment presne raz
```

## 1. Route subject musí prepojiť viac control loops

Pri diagnostike fixuj:

```text
cluster a environment
Ingress/Gateway/Route names, UIDs a generations
class/controller identity a version
Gateway parent UID, listener section a address
Route parentRefs, hostnames, matches, filters a backendRefs
AllowedRoutes a ReferenceGrant generations
Accepted, ResolvedRefs a Programmed conditions s observedGeneration
controller-generated dataplane configuration/hash
edge instance/LB generation a cohort
DNS record generation a TTL
TLS certificate identity, serial a expiry
backend Service UID a EndpointSlice cohort
client request host, path, method, SNI a operation ID
```

Samotný object name alebo `status.address` nestačí na identifikáciu effective route.

## 2. Ingress je stabilný, ale zmrazený API model

Ingress poskytuje jednoduchý HTTP/HTTPS routing contract:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: payments
  namespace: production
spec:
  ingressClassName: public-nginx
  rules:
    - host: pay.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: payments-api
                port:
                  name: https
```

Kubernetes projekt odporúča Gateway API pre nové routing capabilities. Ingress zostáva podporovaný stable API, ale jeho feature model sa ďalej nerozširuje. Controller-specific annotations preto často nesú význam, ktorý API schema nevyjadruje.

## 3. IngressClass a controller selection

Ingress object bez správneho controllera je iba stored intent.

```text
Ingress generation I42
→ ingressClassName public-nginx
→ IngressClass controller string
→ controller watch/admission scope
→ generated proxy/LB config
```

Failure boundaries:

- class chýba;
- class ukazuje na iný controller;
- viac default classes vytvára ambiguity;
- controller nesleduje namespace;
- controller ServiceAccount nemá read/write permissions;
- class parameters sú neplatné;
- migration medzi controllermi mení annotation semantics.

## 4. Ingress path a host matching je request decision

Route acceptance test musí obsahovať actual request fields:

```text
Host/SNI
HTTP method
normalized path
query a headers, ak implementation používa extensions
pathType a rule precedence
rewrite result
backend protocol
```

Test iba na `/` nepreukazuje behavior pre trailing slash, encoded path, overlapping Prefix/Exact rules alebo default backend.

`ImplementationSpecific` presúva semantics na controller. Je to portability a upgrade boundary.

## 5. Gateway API role model

Gateway API rozdeľuje ownership:

```text
GatewayClass
→ controller/provider capability

Gateway
→ platform-owned listener, address a TLS boundary

HTTPRoute/GRPCRoute/...
→ application-owned routing policy
```

Toto oddelenie umožňuje, aby platform team vlastnil shared edge a application team pripojil iba povolené Routes.

## 6. GatewayClass je capability contract

GatewayClass určuje controller implementation.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: managed-public
spec:
  controllerName: edge.atlas.example/gateway-controller
```

Class existence nepreukazuje:

- že controller beží;
- že class bola accepted;
- že požadované features sú podporované;
- že CRD/controller versions sú kompatibilné;
- že cloud credentials a quota sú funkčné.

## 7. Gateway listener je exposure a trust boundary

Platform Gateway:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: public
  namespace: edge-system
spec:
  gatewayClassName: managed-public
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
              edge.atlas.example/public: "true"
```

Listener contract zahŕňa:

- address a port;
- protocol;
- hostname scope;
- TLS mode a certificate ownership;
- allowed Route kinds a namespaces;
- attached Route inventory;
- programmed dataplane generation.

Broad `allowedRoutes` je routing delegation, nie convenience.

## 8. Route attachment je obojstranné rozhodnutie

HTTPRoute:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: payments
  namespace: production
spec:
  parentRefs:
    - name: public
      namespace: edge-system
      sectionName: https
  hostnames:
    - pay.example.com
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: payments-api
          port: 8443
```

Route sa nepripojí iba preto, že obsahuje `parentRefs`. Musí platiť:

```text
parent exists
+ listener section exists
+ listener povoľuje Route namespace/kind
+ hostname/protocol intersection je platná
+ controller Route akceptuje
+ backend references sa vyriešia
+ cross-namespace trust je povolený
```

## 9. Conditions sú subject-bound evidence

Sleduj conditions spolu s `observedGeneration` a parent identity.

Typické otázky:

- `Accepted`: prijal controller Route pre konkrétny parent/listener?
- `ResolvedRefs`: sú backend, certificate a ďalšie references platné a autorizované?
- `Programmed`: bola desired configuration prenesená do dataplane podľa implementation semantics?

Green condition pre starú generation alebo iný parent nie je acceptance evidence pre current route.

## 10. ReferenceGrant je provider-owned trust

Cross-namespace reference musí povoliť namespace referencovaného objektu.

```text
consumer Route v production
→ chce backend Service v shared-services
→ ReferenceGrant v shared-services
→ provider namespace povoľuje presný from/to contract
```

Consumer si nemôže jednostranne udeliť prístup k cudziemu Service alebo Secretu.

Trust inventory musí obsahovať:

- source group/kind/namespace;
- target group/kind/name;
- owner a expiry/review;
- routes, ktoré permission reálne používajú;
- cleanup po migration.

## 11. Controller reconciliation a dataplane generation

Controller typicky sleduje:

```text
Ingress/Gateway/Routes
Classes a parameters
Services a EndpointSlices
Secrets/certificates
ReferenceGrants/policies
cloud/load-balancer resources
```

Z týchto inputs vytvára resolved configuration a aplikuje ju na dataplane.

Rozlišuj:

```text
API object accepted
controller reconcile success
dataplane config generated
dataplane instances loaded config
address/LB ready
client request matched config
```

Controller status môže byť green, zatiaľ čo časť proxy pods alebo LB targets používa starú generation.

## 12. Address, DNS a route sú samostatné control loops

External exposure:

```text
Gateway/Ingress status address
→ external-dns alebo IaC DNS record
→ recursive/cache propagation
→ client resolver
→ LB address
→ programmed dataplane
```

Failure môže byť:

- route current, DNS stale;
- DNS current, LB provisioning incomplete;
- LB current, controller dataplane stale;
- edge current, backend Service broken.

Každá vrstva potrebuje vlastného ownera a generation correlation.

## 13. TLS je identity a reload lifecycle

TLS acceptance zahŕňa:

```text
SNI/hostname
→ listener/Ingress host match
→ certificate reference
→ certificate/key pair
→ SAN a chain validation
→ edge instance loaded serial
→ protocol/cipher policy
→ optional backend re-encryption identity
```

TLS Secret update nepreukazuje, že každá edge instance načítala nový certificate. Edge termination tiež nepreukazuje encryption k backendu.

Default certificate fallback môže vytvoriť „TLS funguje“, ale s nesprávnou identity.

## 14. Rule conflict a precedence

Shared edge môže obsahovať viac Routes pre overlapping host/path space.

Conflict subject:

```text
listener UID/section
hostname
path/match specificity
Route creation/priority semantics
controller conflict policy
accepted winner/loser conditions
```

Manual inspection jedného Route objektu nestačí. Potrebuješ full attached-route inventory a resolved dataplane configuration.

## 15. Backend reference nie je backend health

`ResolvedRefs=True` znamená, že reference bola vyriešená podľa API/controller rules. Neznamená:

- Service má ready EndpointSlices;
- targetPort je správny;
- NetworkPolicy povoľuje controller-to-backend flow;
- application počúva;
- protocol medzi edge a backendom sedí;
- payment operation je korektná.

Routing troubleshooting pokračuje do Service a EndpointSlice lifecycle-u.

## 16. Traffic splitting je exposure decision

Weighted backends:

```yaml
backendRefs:
  - name: payments-v1
    port: 8443
    weight: 90
  - name: payments-v2
    port: 8443
    weight: 10
```

Weights sú desired traffic intent. Acceptance potrebuje actual request distribution podľa route generation a backend Pod/revision identity.

Nízky weight neznamená nízky risk, ak:

- cohort nie je reprezentatívna;
- retries znásobujú requests;
- sticky sessions menia distribution;
- backend v2 zapisuje nekompatibilné dáta;
- metrics nie sú rozdelené podľa revision.

## 17. Retries, timeouty a non-idempotent operations

Edge retry môže zmeniť jeden client request na viac backend attempts.

```text
client POST pay-8842
→ edge odošle attempt A
→ backend commitne payment
→ response sa stratí
→ edge retry attempt B
→ duplicate side effect bez idempotency
```

Timeout/retry policy musí byť viazaná na method, protocol a application idempotency contract. „Znížiť 503“ nie je dostatočný dôvod na globálne retries.

## 18. Ingress annotations a extension policy

Annotations môžu meniť:

- rewrites;
- auth;
- snippets/directives;
- timeouts/retries;
- body limits;
- backend protocol;
- header trust;
- source ranges.

Sú stringly typed a controller-specific. Nebezpečná annotation môže meniť shared proxy configuration alebo otvoriť privilege escalation path.

Použi:

- approved allowlist;
- schema/admission validation;
- controller-version compatibility tests;
- resolved-config diff;
- migration inventory.

## 19. Security a delegation graph

Edge routing authority zahŕňa:

```text
create/update Ingress/Routes
+ attach k shared Gateway
+ AllowedRoutes namespace labels
+ ReferenceGrants
+ backend Service mutation
+ TLS Secret/certificate access
+ controller ServiceAccount/cloud credentials
+ annotation/filter authority
+ DNS mutation
```

Route author nemá automaticky vlastniť listener, certificate alebo ľubovoľný backend. Platform owner nemá meniť application routing bez auditovanej generation transition.

## 20. Worked failure: wrong class, object bez effectu

Ingress existoval a mal správne rules, ale `ingressClassName` odkazoval na class, ktorú žiadny controller nesledoval.

```text
API create success
→ object visible
→ žiadny controller owner
→ žiadny dataplane config
→ address chýba alebo zostane stale
```

Recovery opravila class selection a pridala admission policy, ktorá povoľuje iba installed/accepted classes.

## 21. Worked failure: Route accepted, ale nebola programmed na všetkých edge instances

Controller status ukazoval accepted generation R52. Po rolling update-e controllera však časť proxy replicas používala config R51.

```text
controller reconcile success
→ partial dataplane reload
→ mixed edge cohort
→ časť requests ide podľa old route
```

Fix vyžadoval per-instance config generation telemetry a rollout gate, nie zmenu Route objectu.

## 22. Worked failure: široké `allowedRoutes`

Shared public Gateway povoľovala Routes zo všetkých namespaces. Test namespace pripojil Route pre `pay.example.com` s overlapping path.

Podľa conflict semantics začala časť trafficu končiť na test backende.

Recovery:

- zúžila namespace selector;
- odstránila unauthorized Route attachment;
- auditovala full host/path inventory;
- overila forbidden attachment test;
- rotovala credentialy, ak test backend prijal production headers/tokens.

## 23. Worked failure: TLS Secret current, edge serial stale

Cert-manager vytvoril nový certificate, Secret bol aktualizovaný, ale jedna edge instance nereloadla config.

Clienti podľa LB selection dostávali striedavo nový a expirovaný certificate. Secret resourceVersion preto nebol sufficient evidence. Potrebná bola per-instance loaded certificate serial telemetry.

## 24. Worked failure: edge retry vytvoril duplicate payment

Gateway policy retryovala POST pri upstream timeout-e. Backend prvý attempt commitol, ale response sa stratila.

Recovery nebola iba vypnutie retry. Bolo potrebné:

- reconciliovať operation ID;
- kompenzovať duplicate authorization;
- pridať idempotency key;
- zúžiť retry policy;
- overiť lost-response integration test.

## 25. Causal troubleshooting walkthrough: external `503`, direct Service request funguje

Symptóm:

```text
pay.example.com vracia 503 približne na 40 % requests
direct request z diagnostic Podu na payments-api Service je úspešný
HTTPRoute R52 má Accepted=True a ResolvedRefs=True
Gateway má address
```

### 1. Zafixuj route a request subject

```text
client source/cohort
DNS answer a TTL
SNI, Host, method, path a operation ID
Gateway UID/generation, listener section a address
HTTPRoute UID/generation a parent status
AllowedRoutes/ReferenceGrant generations
controller identity/version
resolved config hash R52
edge instance/LB target generation
certificate serial
backend Service UID a EndpointSlice cohort
```

### 2. Konkurenčné hypotézy

1. časť edge instances má stale config R51;
2. Route nie je attached k listeneru, ktorý traffic reálne prijíma;
3. conflicting Route vyhráva na časti dataplane;
4. LB stále posiela traffic na old controller cohort;
5. TLS/SNI alebo Host mismatch vedie na default route;
6. backend protocol/re-encryption config je nesprávny;
7. controller-to-Service NetworkPolicy zlyháva iba z časti edge Pods;
8. timeout/retry policy vyčerpáva upstream capacity;
9. DNS vracia starú aj novú LB address;
10. Service direct test používa iný port/protocol/host contract.

### 3. Diskriminačné observation points

- koreluj failed response s edge instance/LB targetom a config hashom;
- porovnaj Route conditions pre current observedGeneration a správny parent;
- získaj full attached-route host/path inventory;
- over actual resolved config na každej edge instance;
- testuj exact SNI, Host, method a path;
- porovnaj certificate serial podľa connection;
- sleduj upstream target Service/Pod UID a backend protocol;
- porovnaj NetworkPolicy flow z každej edge cohorty;
- skontroluj DNS answers, TTL a old address inventory;
- odlíš edge-generated 503 od application-generated response.

### 4. Containment

- zastav ďalšie route/controller/LB zmeny;
- odober stale edge cohort z LB, ak je identifikovaná;
- zachovaj config dumps/hashes, conditions a request traces;
- nereštartuj všetky controllery súčasne;
- nevytváraj broad ReferenceGrant alebo default backend bypass;
- vypni riskantné retries pre non-idempotent operations;
- zachovaj direct Service path iba ako diagnostiku, nie public workaround.

### 5. Authoritative recovery

Pri mixed dataplane generation:

1. oprav controller rollout/reload mechanismus;
2. nahraj reviewed config R52 na bounded edge cohort;
3. over listener, certificate a route table;
4. vráť cohort do LB až po external synthetic;
5. odstráň old config/address inventory;
6. dokonči controller rollout po failure-domainoch.

Iné findings sa opravujú v ich authoritative ownerovi: DNS, Gateway attachment, ReferenceGrant, TLS, Service alebo NetworkPolicy.

### 6. Over pôvodný a forbidden outcome

Potvrď:

- DNS vracia iba accepted edge addresses;
- každá active edge instance používa config R52;
- Gateway listener používa správny certificate serial;
- HTTPRoute R52 je attached k správnemu parent/listeneru;
- unauthorized/overlapping Route nie je effective;
- request cez každú edge cohortu smeruje na accepted Service/Pod UID;
- pay-8842 je autorizovaný presne raz;
- direct aj public path majú korektnú TLS/application identity;
- rollback Route generation je stále explicitne eligible alebo bezpečne vyradená.

### 7. Posuň control skôr

Pridaj:

- class/controller existence admission;
- route attachment a ReferenceGrant tests;
- resolved-config diff a per-instance generation telemetry;
- host/path conflict inventory;
- DNS/LB/address generation correlation;
- certificate loaded-serial gate;
- edge-to-Service synthetic podľa exact protocol;
- retry/idempotency policy test;
- Gateway cohort rollout po failure-domainoch;
- forbidden route/namespace attachment tests.

## 26. Observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Intent | route/exposure contract | owner, host/path, protocol, risk, backend |
| Class | IngressClass/GatewayClass | controller, acceptance, feature support |
| Parent | Gateway UID/listener | address, protocol, hostname, allowedRoutes |
| Attachment | Route UID/generation | parentRefs, Accepted, ResolvedRefs, conflicts |
| Trust | ReferenceGrant/policy | from/to scope, owner, expiry |
| Controller | reconcile/config subject | observed generation, config hash, errors |
| Dataplane | edge instance/LB cohort | loaded generation, listener, route table |
| TLS | certificate subject | SAN, serial, expiry, loaded instances |
| DNS/address | record/LB generation | answers, TTL, target inventory |
| Backend | Service/EndpointSlice cohort | target UID, port, readiness, policy path |
| Business | request/operation ID | correct route/backend, response, no duplicate |

## 27. Referenčné príkazy

```bash
kubectl get ingress,ingressclass -A
kubectl describe ingress <name> -n <namespace>
kubectl get gatewayclass
kubectl get gateway -A -o yaml
kubectl get httproute -A -o yaml
kubectl get referencegrant -A -o yaml
kubectl get service,endpointslice -n <namespace> -o yaml
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Controller-specific resolved configuration a per-instance loaded generation sú často dôležitejšie než samotný API object dump.

## 28. Referenčné pravidlá

- Ingress/Gateway API object nie je dataplane.
- Ingress API je stable, ale zmrazený; nové capabilities smerujú do Gateway API.
- Class selection určuje controller ownership.
- Route attachment je obojstranný parent/listener decision.
- Conditions musia patriť current generation a správnemu parentu.
- ReferenceGrant vlastní provider namespace.
- Controller success nepreukazuje, že všetky dataplane instances načítali config.
- Address, DNS, certificate a route sú samostatné control loops.
- `ResolvedRefs=True` nepreukazuje backend health.
- TLS Secret update nepreukazuje loaded certificate serial.
- Edge retries môžu duplikovať non-idempotent side effects.
- Route mutation je traffic authority a security boundary.
- Recovery musí overiť actual edge cohort, backend UID a business outcome.

## 29. Kontrolné otázky

1. Aký lifecycle spája Route intent s verified external requestom?
2. Prečo Ingress bez controllera nemá traffic effect?
3. Ako sa líšia GatewayClass, Gateway a Route ownership?
4. Čo musí platiť pre Route attachment?
5. Prečo conditions bez observedGeneration nestačia?
6. Kto vlastní ReferenceGrant?
7. Ako odlíšiš controller reconcile od dataplane loadu?
8. Prečo Gateway status address nepreukazuje DNS ani client reachability?
9. Ako edge retry mení exactly-once risk?
10. Čo musí edge routing acceptance verdict overiť?

## Glossary impact

Relevantné pojmy: edge route lifecycle subject, class-controller ownership, Gateway listener subject, route attachment subject, route parent generation, ReferenceGrant trust subject, resolved route configuration, programmed dataplane generation, edge cohort subject, DNS-address generation, loaded certificate subject, route conflict inventory, edge retry subject, edge observation matrix a routing acceptance verdict.

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
