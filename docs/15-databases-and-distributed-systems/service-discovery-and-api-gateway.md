# Service discovery a API gateway

Service discovery a API gateway riešia odlišné časti jedného request pathu. Discovery určuje, ktoré runtime endpoints aktuálne reprezentujú logical service. Gateway určuje, ktorý external request patrí ku ktorému API contractu, policy a backend generation. Obe vrstvy môžu byť technicky healthy a zároveň posielať request na nekompatibilný backend.

```text
client operation a API contract
→ exact gateway/route generation
→ listener, match, policy a precedence
→ backend logical-service identity
→ discovery source a endpoint inventory
→ generation/readiness/capacity eligibility
→ dataplane selection a connection reuse
→ backend acknowledgement contract
→ business outcome a per-request evidence
→ old-connection, mixed-generation a failover validation
```

`DNS resolveuje`, `Service má endpoints` alebo `Gateway config accepted` sú iba intermediate observations. Correct verdict vzniká až vtedy, keď konkrétny request použije správny contract generation a dosiahne správnu business boundary.

## 1. Route/discovery subject a authority

Exact subject musí pomenovať client operation a API version, hostname, port, protocol a TLS identity, gateway/listener/route generation, host/path/method/header match a precedence, authentication/authorization/rate-limit policy, backend capability a contract generation, cluster/namespace, discovery mechanism, endpoint inventory, readiness/capacity, connection drain, timeout/retry a expected acknowledgement.

Pre Atlas Payments:

```text
operation: POST /v2/settlements
host: api.atlas.example
route generation: settlement-v2-r17
backend contract: settlement-command-v2
service selector:
  app=settlement-command
  contract-generation=v2
eligible endpoint:
  artifact 8.2 + schema/config compatible + Ready for async-v2
response:
  202 až po atomic settlement + outbox commit-e
```

Logical service identity má reprezentovať capability contract. Endpoint identity reprezentuje konkrétny Pod, process alebo instance. Stabilný service name môže smerovať na dynamický inventory, ale iba compatible endpoints smú patriť do jedného contractu.

## 2. Discovery a Kubernetes effective state

Client-side discovery dáva endpoint inventory clientovi, ktorý sám vykonáva selection a refresh. Poskytuje locality a direct telemetry, ale každý client musí správne riešiť stale cache, balancing a rollout convergence. Server-side discovery používa proxy, virtual IP alebo load balancer; clients sú jednoduchšie, no proxy config a dataplane convergence zostávajú samostatné failure boundaries.

DNS poskytuje name-to-address mapping s TTL a resolver caches. Successful lookup neoveruje application readiness, API version ani current connection target. Existing connection môže používať old endpoint ešte po zmene DNS alebo registry.

V Kubernetes typický chain vyzerá:

```text
Pod labels + readiness
→ Service selector
→ EndpointSlice inventory
→ ClusterIP/DNS/proxy dataplane
→ selected Pod
```

Treba rozlíšiť, či Pod existuje, je Ready, endpoint je publikovaný, dataplane načítal current inventory, connection stále nepoužíva old endpoint a vybraný Pod podporuje požadovaný contract. EndpointSlice môže byť úplne current vzhľadom na nesprávne široký selector. To nie je stale discovery; je to nesprávna service identity.

## 3. Gateway route graph a policy binding

Gateway môže terminovať TLS, autentifikovať clienta, aplikovať authorization, quotas, request validation, observability a vybrať backend. Nie je business transaction coordinator a nemá skryť acknowledgement, idempotency alebo final-state semantics backendu.

Route selection môže závisieť od hostname, exact/prefix pathu, method, headers, query a priority. Effective route graph vzniká až po precedence a policy attachment resolution:

```text
POST /v2/settlements + async-v2 header
→ intended specific route R17

broad /v2/* route s vyššou prioritou
→ legacy route R3
```

Existencia deklarovanej route neznamená, že ju request vyberie. Validation musí poslať representative positive aj negative requests a zaznamenať resolved route, attached policies a backend reference. Gateway API oddelenie infrastructure a application roles pomáha iba vtedy, keď cross-namespace references, listeners a route attachment zostávajú explicitne autorizované.

Authentication, authorization a rate limit musia byť viazané na rovnaký route subject ako backend contract. Policy pripojená k broad route môže neúmyselne obísť alebo zdvojiť controls specific route-u.

## 4. Endpoint eligibility, readiness a draining

Deployment generation, API version a business contract nie sú synonymá. Endpoint eligibility zahŕňa artifact, supported schema/API generation, loaded config/policy, data migration compatibility, credentials, capacity a drain state.

Generic `/healthz=200` môže potvrdiť iba liveness. Capability readiness pre settlement acceptance musí overiť, že endpoint vie vykonať atomic settlement/outbox canary, používa current schema/policy generation a poskytuje status resource. Provider availability nemusí byť podmienkou acceptance readiness, pretože provider execution je deferred; jej zahrnutie by pri provider incidente odstránilo všetky command endpoints a vytvorilo routing storm.

Drain je lifecycle, nie delete operácia:

```text
endpoint ineligible for new work
→ updated EndpointSlice/proxy generation
→ dataplane a client convergence
→ bounded in-flight completion alebo rejection
→ old HTTP/2/gRPC connections closed
→ process termination
```

HTTP keep-alive, HTTP/2 streams, gRPC channels, DNS caches a sidecar upstream clusters môžu smerovať na old generation po odstránení endpointu. `Pod deleted` preto nie je proof complete drain-u.

## 5. Timeouts, retries a selected-backend evidence

Gateway timeout musí rešpektovať end-to-end deadline. Retry je safe iba pri idempotentnej operation alebo stable idempotency keyi, známej failure classification, bounded attempt budgete a compatible backend generation.

Upstream reset po `POST /settlements` môže nastať po database commite. Retry na druhý backend môže vytvoriť duplicate physical attempt alebo preskočiť z async contractu na legacy sync path. Pri ambiguous outcome-e gateway retry nemá robiť; client alebo service workflow musí queryovať stable operation identity.

Každý request potrebuje evidence: route generation, selected backend contract/artifact, endpoint identity, retry attempt, response boundary a operation ID. Agregovaná `service=settlement-api` metrika zakryje mixed cohorts.

Convergence sa meria cez registry/controller update latency, EndpointSlice generation age, proxy loaded config, DNS/connection age, endpoint add/remove propagation a stale-route request rate. Control plane green nie je dataplane verdict.

## 6. Connected incident `DB-PAY-58`

Rollout v8.2 používal tieto labels:

```text
legacy Pods: app=settlement-api, version=8.1
new Pods:    app=settlement-api, version=8.2
Service:     selector app=settlement-api
```

Gateway route `POST /v2/settlements` smerovala na spoločný Service. Specific async-v2 header route mala nižšiu prioritu než broad `/v2/*` route. EndpointSlices správne obsahovali obe generations.

Za 31 minút `31 %` requests dosiahlo legacy backend. Obe cohorts mali `/healthz=200` a Kubernetes Ready. Gateway načítala presne deklarovanú, ale nesprávnu precedence. Legacy backend vracal `200` po provider calle, v8.2 vracal `202` po durable intent commite. Gateway retryovala niektoré upstream resets na druhý endpoint; `206` logical attempts zasiahlo dve contract generations. Old HTTP/2 connections posielali traffic na v8.1 ešte `74 s` po oprave selectoru.

Root cause bol logical Service a gateway route bez explicitnej contract-generation eligibility. Discovery nebola stale a gateway nebola down; oba mechanisms správne realizovali nesprávny desired state. Generic readiness, ambiguous POST retry, protocol-unaware draining a aggregated metrics incident zosilnili.

## 7. Redesign a acceptance paths

Redesign zaviedol samostatný `settlement-command-v2` Service so selectorom `contract-generation=v2`. Gateway route má exact host, path, method a async-v2 contract, explicitný backend a vypnutý retry pri ambiguous upstream outcome-e. Rollout používa shadow route evaluation, effective route-table read-back, bounded cohort, per-generation metrics a drain verification.

**Positive path** pošle v2 request, zaznamená intended route R17, v2 endpoint a `202` až po durable commit-e.

**Recovery path** odstráni endpoint, reloadne gateway alebo vykoná failover. Current clients konvergujú, old connections sa drainujú a accepted operations zostávajú queryable bez mixed-generation retryu.

**Failure path** pri absent compatible endpointoch alebo invalid route attachmentu explicitne odmietne new work; nesmeruje ho na generic fallback s odlišným contractom.

**Forbidden path** odmietne broad selector miešajúci generations, shadowed route, generic readiness ako capability proof, gateway retry ambiguous POST-u, stale-writer endpoint a policy attached k nesprávnemu route subjectu.

Acceptance zahŕňa second request cez old connection, endpoint removal, gateway reload, partial rollout, DNS/cache convergence a regional failover.

## 8. Troubleshooting a anti-patterny

Diagnostika ide od exact client operation a route generation cez listener/match/precedence, policy attachment, backend reference, Service a EndpointSlice inventory, endpoint generation/readiness, proxy loaded state, DNS/connection age a per-request selected backend až po acknowledgement a business outcome.

Najčastejšie anti-patterny sú `DNS resolveuje = discovery funguje`, Service selector iba podľa `app`, Ready Pod považovaný za compatible pre všetky routes, accepted gateway config považovaná za correct effective graph, selector fix považovaný za okamžitý drain, retry na inom backend-e vydávaný za availability a gateway alebo mesh považované za náhradu business workflowu.

## 9. Kontrolné otázky

1. Čo tvorí exact route/discovery subject?
2. Ako sa logical service identity líši od endpoint identity?
3. Čo reprezentuje Kubernetes Service a čo EndpointSlice?
4. Prečo current EndpointSlice môže stále predstavovať nesprávny contract?
5. Ako route precedence vytvára effective graph?
6. Čo musí capability readiness overiť?
7. Prečo endpoint removal neukončí existing connections okamžite?
8. Kedy je gateway retry bezpečný?
9. Prečo discovery v `DB-PAY-58` nebola stale?
10. Ktoré positive, recovery, failure a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: route/discovery subject, logical service identity, endpoint identity, client-side discovery, server-side discovery, discovery generation, EndpointSlice generation, contract-generation eligibility, route precedence, resolved route graph, capability readiness, endpoint draining, connection convergence, stale-route request, gateway retry boundary, selected-backend evidence a route/discovery acceptance verdict.

## Primárne zdroje

- [Kubernetes — Service](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Kubernetes — EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)
- [Kubernetes — DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io/)
- [Envoy — Dynamic configuration](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/operations/dynamic_configuration)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Message queues a event-driven architecture](message-queues-and-event-driven-architecture.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Caching →](caching.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
