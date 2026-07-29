# Service discovery a API gateway

Service discovery a API gateway riešia odlišné vrstvy jedného request pathu. Discovery odpovedá, **ktoré runtime endpoints aktuálne reprezentujú logical service**. API gateway rozhoduje, **ktorý external request patrí ku ktorému API contractu, policy a backend generation**. Ani jedna vrstva automaticky negarantuje, že vybraný endpoint je kompatibilný, ready pre konkrétnu operation alebo schopný dokončiť business outcome.

```text
client operation a API contract
→ exact route/discovery subject
→ gateway listener, identity a policy
→ route match a backend reference
→ service identity a discovery lookup
→ endpoint inventory/generation
→ health, readiness, locality a capacity eligibility
→ connection a request forwarding
→ response/outcome
→ drain, rollout a second-request validation
```

## 1. Exact route a discovery subject

Tvrdenie `DNS funguje` alebo `gateway routuje na Service` je príliš slabé. Subject má uvádzať:

- client operation a API version;
- hostname, port, protocol a TLS identity;
- gateway/listener/route generation;
- path, method, headers a priority match;
- authentication, authorization a rate-limit policy;
- logical backend service a contract generation;
- namespace/region/cluster;
- discovery mechanism a cache generation;
- endpoint identity, readiness, locality a capacity;
- connection reuse/drain semantics;
- timeout/retry policy;
- response a business verification.

Príklad:

```text
operation: POST /v2/settlements
host: api.atlas.example
route generation: settlement-v2-202-contract-r17
backend contract: settlement-command-v2
Service selector: app=settlement-command, contract-generation=v2
eligible endpoints: ready v8.2 Pods only
response: 202 after durable settlement/outbox commit
```

## 2. Service identity nie je endpoint identity

Logical service môže zostať stabilná, kým endpoints vznikajú a zanikajú.

```text
logical service name
→ discovery record/Service object
→ EndpointSlice alebo registry inventory
→ endpoint IP/port/generation
→ connection
```

Service identity má reprezentovať capability contract, nie iba spoločný label. Ak rovnaký Service selector zahrnie v1 a v2 backendy s odlišným acknowledgement contractom, discovery funguje technicky správne, ale service contract je neplatný.

## 3. Discovery mechanizmy

### Client-side discovery

Client získa endpoint inventory a sám vyberá backend.

Výhody:

- locality/capacity-aware selection;
- menej proxy hops;
- direct per-endpoint telemetry.

Náklady:

- každý client potrebuje discovery, load-balancing a refresh logic;
- stale caches a rozdielne client generations;
- rollout a failover convergence závisia od všetkých clients.

### Server-side discovery

Client volá stable proxy/load balancer/virtual IP a infraštruktúra vyberá endpoint.

Výhody:

- centralizované routing a policy;
- jednoduchší clients;
- bounded convergence point.

Náklady:

- ďalší data-path component;
- proxy capacity a health model;
- config/endpoint convergence stále nie je okamžitá.

### DNS discovery

DNS poskytuje service name-to-address mapping s TTL a resolver caches. DNS success neoveruje application readiness ani API compatibility. Clients môžu používať starý answer až do expiry alebo dlhšie podľa connection reuse-u.

## 4. Kubernetes Service a EndpointSlice

Kubernetes Service typicky poskytuje stable logical identity a virtual address. EndpointSlices reprezentujú aktuálne backend endpoints.

```text
Pod labels/readiness
→ Service selector
→ EndpointSlice generation
→ DNS alebo ClusterIP
→ kube-proxy/eBPF/proxy dataplane
→ selected Pod
```

Treba rozlíšiť:

- Pod existuje;
- Pod je Ready;
- endpoint je publikovaný;
- dataplane má aktuálnu generation;
- existing connection stále smeruje na old endpoint;
- selected Pod podporuje požadovaný API contract;
- request dosiahne correct business outcome.

Headless Service môže cez DNS vracať priamo Pod addresses. To presúva selection a refresh semantics na clienta.

## 5. Readiness a health

Health má byť capability-specific.

### Liveness

Má process reštartovať?

### Readiness

Má endpoint prijímať nový traffic pre konkrétny contract?

### Startup

Je initialization ešte legitímne incomplete?

Generic `/healthz=200` môže byť zelené, hoci:

- schema migration nie je kompatibilná;
- policy/cache generation chýba;
- provider credentials nie sú loaded;
- outbox publication stojí;
- endpoint podporuje iba v1 contract;
- backlog alebo dependency capacity prekročili safe hranicu.

Readiness nemá byť závislá od každej transient dependency tak, že incident vytvorí restart/routing storm. Má reprezentovať bezpečnú eligibility pre new work.

## 6. API gateway responsibilities

Gateway môže vykonávať:

- TLS termination a client identity;
- authentication/authorization;
- routing a version selection;
- request/response transformation;
- rate limiting a quotas;
- body/size/schema validation;
- timeout/retry policy;
- observability/correlation;
- edge caching;
- canary/traffic splitting.

Gateway nie je business transaction coordinator. Nemá vlastným retryom nevedomky opakovať non-idempotent operation. Nemá tiež interpretovať backend `200/202` bez znalosti route contractu.

## 7. Route matching a precedence

Route selection môže závisieť od:

- host;
- path prefix/exact match;
- HTTP method;
- headers;
- query parameters;
- protocol;
- route priority;
- weighted backend split.

Broad higher-priority rule môže shadowovať specific v2 route.

```text
/v2/settlements + header X-Contract: async-v2
→ intended route R17

broad / route R3 with higher precedence
→ legacy backend
```

Validation musí overiť effective resolved route graph, nie iba existenciu deklarovanej route.

## 8. Contract generation a backend eligibility

Deployment generation, API version a business contract nie sú to isté.

Endpoint eligibility má zahŕňať:

- artifact/release generation;
- supported API/schema generations;
- loaded config/policy generation;
- data migration compatibility;
- required credentials/dependencies;
- readiness for exact operation;
- capacity/drain state.

Service selector iba podľa `app=settlement-api` je nedostatočný, ak v1 a v2 používajú odlišné acknowledgement semantics.

## 9. Connection reuse a draining

Aj po odstránení endpointu z discovery môžu existovať:

- keep-alive HTTP connections;
- HTTP/2 multiplexed streams;
- gRPC channels;
- connection pool entries;
- DNS cache entries;
- sidecar/upstream clusters so stale configom.

Drain lifecycle:

```text
mark endpoint not eligible for new work
→ publish updated discovery state
→ wait for dataplane/client convergence
→ reject or finish bounded in-flight work
→ close old connections
→ terminate process
```

`Pod deleted` nie je dôkaz, že všetok traffic prestal používať old generation.

## 10. Discovery freshness a convergence

Treba merať:

- registry/controller update latency;
- EndpointSlice generation age;
- DNS TTL a resolver behavior;
- proxy config version;
- endpoint add/remove propagation;
- client connection age;
- stale-route request rate;
- failover convergence.

Control plane green neznamená, že každý dataplane/client používa current generation.

## 11. Load balancing a locality

Selection môže používať:

- round robin;
- least requests/connections;
- consistent hashing;
- random/power-of-two choices;
- locality/zone preference;
- weighted rollout;
- priority failover.

Algorithm musí zodpovedať connection/request modelu. Least connections môže zavádzať pri HTTP/2 multiplexingu. Consistent hashing potrebuje stabilný a správny key. Locality preference nesmie smerovať na incompatible alebo capacity-exhausted cohort.

## 12. Timeouts a retries v gatewayi

Gateway retry je safe iba ak:

- operation je idempotentná alebo má stable idempotency key;
- timeout/failure klasifikácia je správna;
- original attempt outcome je známy alebo reconcileable;
- retry budget je bounded;
- deadline zostáva dostatočný;
- retry nesmeruje na incompatible generation.

Retry na `POST /settlements` po upstream timeout-e môže duplikovať provider side effect, ak upstream už commitol alebo odoslal operation.

## 13. API gateway vs. service mesh

Gateway typicky rieši north-south API boundary. Service mesh typicky rieši east-west service communication, identity, policy a telemetry. Funkcie sa môžu prekrývať.

Ani jedna vrstva nemá skryť application contract:

- idempotency;
- transaction boundary;
- acknowledgement semantics;
- schema compatibility;
- business authorization;
- final outcome.

## 14. Worked incident `DB-PAY-58`

Rollout settlement v8.2 mal vytvoriť nový asynchronous contract. Kubernetes deploymenty používali:

```text
legacy Pods: app=settlement-api, version=8.1
new Pods:    app=settlement-api, version=8.2
Service:     selector app=settlement-api
```

Gateway route `POST /v2/settlements` odkazovala na tento spoločný Service. Specific route vyžadujúca header `X-Settlement-Contract: async-v2` mala nižšiu prioritu než broad path route `/v2/*`.

Effective flow:

```text
v2 client
→ gateway broad route
→ shared Service
→ EndpointSlices with v8.1 + v8.2
→ random backend contract
```

Evidence počas 31-minútového incidentu:

- `31 %` requests dosiahlo legacy v8.1 backend;
- oba cohorts mali `/healthz=200` a Kubernetes Ready;
- EndpointSlices boli current podľa selectoru;
- gateway config bola loaded presne podľa deklarovanej, ale nesprávnej precedence;
- v8.1 odpovedala `200` po provider calle, v8.2 `202` po durable intent commit-e;
- gateway retryovala niektoré upstream resets na druhý endpoint;
- 206 requestov zasiahlo dve contract generations v rámci jedného logical attemptu;
- old HTTP/2 connections posielali requests na v8.1 ešte `74 s` po oprave selectoru.

### Discovery/gateway root cause

Primary root cause bol **logical Service a gateway route bez explicitnej contract-generation eligibility**. Discovery nebola stale; správne publikovala všetky Pods matching nesprávne široký selector. Gateway nebola down; správne aplikovala nesprávnu route precedence.

Causal amplifiers:

- generic readiness bez contract canary;
- shared service name pre incompatible acknowledgement semantics;
- gateway retry na ambiguous POST outcome;
- connection draining bez protocol-aware evidence;
- dashboard agregujúci všetky backends pod jeden service label.

## 15. Evidence-preserving containment

```text
freeze gateway/Service/deployment changes
→ snapshot Gateway/Route/Service/EndpointSlice generations
→ preserve per-request selected backend generation
→ disable gateway retries for settlement POST
→ create exact v2 Service selector
→ mark legacy endpoints ineligible for v2
→ drain old connections
→ reconcile mixed-generation requests
```

## 16. Authoritative redesign

```text
Service settlement-command-v2
selector:
  app=settlement-command
  contract-generation=v2

Gateway route:
  host=api.atlas.example
  path=/v2/settlements
  method=POST
  required contract=async-v2
  backend=settlement-command-v2
  retry=disabled for ambiguous upstream outcome
```

Readiness v2 overuje:

- artifact a contract generation;
- PostgreSQL schema compatibility;
- loaded policy/config generation;
- atomic settlement/outbox canary;
- status resource availability;
- provider path nie je required pre acceptance readiness.

Rollout používa shadow route evaluation, route-table read-back, bounded cohort, per-generation metrics a connection drain verification.

## 17. Route/discovery acceptance verdict

Design je prijatý, keď:

- exact API operation, route a service contract generation sú explicitné;
- route precedence a effective resolved graph sú overené;
- authentication/authorization/rate-limit policies patria správnemu route subjectu;
- Service/registry identity reprezentuje compatible capability;
- endpoint inventory obsahuje generation, readiness, locality a capacity;
- discovery/control-plane update je overený v dataplane/client read-backu;
- health/readiness zodpovedá exact operation;
- connection reuse a draining sú zahrnuté v convergence modeli;
- gateway timeout/retry neporušuje idempotency a unknown-outcome semantics;
- rollout/failover oddeľuje incompatible generations;
- per-request evidence ukazuje selected backend;
- second request, old connection, endpoint removal, gateway reload a regional failover tests prejdú;
- forbidden mixed-contract, stale-writer a shadowed-route outcomes zlyhajú.

## 18. Troubleshooting flow

```text
wrong backend, intermittent contract alebo stale route
→ exact client operation a route generation
→ gateway listener/match/precedence
→ backend reference/service identity
→ discovery/EndpointSlice inventory
→ endpoint generation/readiness/capacity
→ proxy/dataplane loaded config
→ DNS/connection/cache age
→ selected backend per request
→ response/business contract
→ drain/failover/second-request validation
```

## 19. Anti-patterny

### DNS resolveuje, discovery funguje

Address môže byť stale, incompatible alebo application-unready.

### Service selector podľa app labelu stačí

Môže miešať contract generations.

### Ready Pod podporuje všetky routes

Readiness môže byť príliš generic.

### Gateway config bola accepted

Accepted/deployed nie je effective correct route verdict.

### Oprava selectoru odstráni traffic okamžite

Existing connections môžu pokračovať.

### Retry na inom backend-e zvýši availability

Pri non-idempotent unknown outcome-e môže duplikovať effect.

### Gateway je business orchestration layer

Routing/policy nenahrádza authoritative workflow state.

### Service mesh vyrieši compatibility

Transport identity a retries neoverujú semantic contract.

## 20. Kontrolné otázky

1. Čo tvorí exact route/discovery subject?
2. Ako sa service identity líši od endpoint identity?
3. Ako client-side a server-side discovery menia responsibility?
4. Čo Kubernetes Service a EndpointSlice reprezentujú?
5. Prečo generic readiness nestačí?
6. Ako route matching a precedence fungujú?
7. Prečo API version nie je automaticky deployment generation?
8. Ako connection reuse ovplyvňuje draining?
9. Kedy je gateway retry bezpečný?
10. Prečo discovery v `DB-PAY-58` nebola technicky stale?
11. Ako odlíšiť declared od effective route graphu?
12. Čo musí overiť route/discovery acceptance verdict?

## Glossary impact

Relevantné pojmy: route/discovery subject, logical service identity, endpoint identity, client-side discovery, server-side discovery, discovery generation, EndpointSlice generation, contract-generation eligibility, route precedence, resolved route graph, capability readiness, endpoint draining, connection convergence, stale-route request, gateway retry boundary, selected-backend evidence a route/discovery acceptance verdict.

## Primárne zdroje

- [Kubernetes — Service](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Kubernetes — DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [Kubernetes — Gateway API](https://gateway-api.sigs.k8s.io/)
- [Envoy — Service discovery](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/operations/dynamic_configuration)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Message queues a event-driven architecture](message-queues-and-event-driven-architecture.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Caching →](caching.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
