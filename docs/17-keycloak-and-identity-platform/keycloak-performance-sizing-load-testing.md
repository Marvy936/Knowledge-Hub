# Keycloak performance, sizing a load testing

Keycloak sizing nie je výber počtu Pods podľa celkového HTTP RPS. Rozhodujúci je workload mix: password validations spotrebúvajú CPU podľa hashing algoritmu a strength, client-credentials requests často vytvárajú nové TLS connections, refresh requests kombinujú session a database state, Authorization Services pridávajú policy evaluation a external LDAP/IdP alebo custom providers pridávajú vlastnú latency. Rovnakých 1 000 requests za sekundu môže byť ľahký cached discovery traffic alebo neudržateľný password-login peak.

Performance verdict preto musí fixovať exact release, JVM/CPU architecture, hashing policy, dataset cardinality, session/cache state, database, network, topology, extensions a test-generator capacity. Zelený priemer nepreukazuje tail latency, survivor capacity ani stabilitu po cache-cold restart-e. Oficiálne sizing čísla sú počiatočný model získaný na konkrétnej referenčnej architektúre; production capacity musí potvrdiť vlastný reproducible load test.

## 1. Dominantný demand-to-capacity lifecycle

```text
business journeys a SLO
→ exact request mix, dataset a concurrency model
→ Keycloak/JVM/image/config generation
→ CPU, memory, thread, pool a cache budget
→ database IOPS/CPU/connections a network capacity
→ load-generator capacity a test topology
→ warm-up, steady, spike, soak, stress a failure phases
→ latency/error/saturation a business outcomes
→ bottleneck hypothesis a bounded change
→ comparative rerun a survivor-capacity acceptance
```

Každá šípka má vlastný proof boundary. Predicted RPS nepreukazuje measured throughput. Pod CPU pod 70 % nepreukazuje absence database waits. Low median latency nepreukazuje P99 alebo timeout tails. Successful normal-load run nepreukazuje zone-loss behavior. Load test môže „nájsť limit“ load generátora, ephemeral ports alebo client TLS setupu namiesto Keycloaku.

## 2. Exact performance subject

```yaml
performanceSubject:
  keycloak:
    version: 26.7.0
    imageDigest: sha256:7c21...
    optimizedBuildGeneration: kc-build-49
    configurationHash: sha256:81fa...
    providerSetHash: sha256:b2ce...
    topology: single-cluster-multi-az
    replicas: 3
  runtime:
    jdk: OpenJDK 25
    cpuArchitecture: arm64
    cpuRequestPerPod: "4"
    cpuLimitPerPod: "10"
    memoryRequestPerPod: 2500Mi
    memoryLimitPerPod: 3200Mi
    heapPolicy: container-default-70-percent
  security:
    passwordAlgorithm: argon2
    hashingStrength: "memory=7168KiB,iterations=5,parallelism=1"
    tlsTermination: passthrough
  dataset:
    realms: 10
    users: 1000000
    clients: 20000
    groups: 5000
    activeSessions: 250000
    concurrentlyUsedClients: 4000
  database:
    engine: aurora-postgresql
    instanceGeneration: db-r8g-8xlarge-17
    poolMaxPerPod: 60
    globalPoolCeiling: 180
  workload:
    passwordLoginsPerSecond: 45
    refreshRequestsPerSecond: 360
    clientCredentialsPerSecond: 360
    logoutRequestsPerSecond: 5
    duration: PT60M
    concurrency: 12000
  test:
    benchmarkRelease: keycloak-benchmark-26.7-compatible
    scenarioRevision: perf-92
    loadGeneratorNodes: 4
    networkProfile: same-region-2ms-p99
    runId: perf-2026-08-02-29
```

Bez dataset a concurrent-client cardinality sa cache/database behavior nedá reprodukovať. Bez hashing policy sa password workload nedá porovnať. Bez architecture a JDK/CPU type-u sa per-core throughput prenáša medzi neporovnateľnými systems. Bez load-generator identity sa client-side limit zamieňa za server saturation.

## 3. Začni business journey mixom

Namiesto jedného RPS čísla vytvor journey inventory:

```text
password login + MFA/passkey
cookie SSO login
refresh token
client credentials
authorization-code exchange
logout a revocation
introspection/UserInfo
Authorization Services permission/RPT
identity brokering
LDAP credential/group lookup
Admin REST mutation/read-back
email required action
MCP/API token issuance a downstream validation
```

Každá journey má inú CPU, database, cache a external-dependency stopu. Percentá a arrival pattern sa odvodia z production metrics a forecastu, nie z rovnomerného syntetického mixu. Login storms po incidentoch alebo pracovnej zmene majú spike profile; refresh má periodický pattern podľa token TTL.

## 4. SLO a acceptance pred testom

Definuj:

```yaml
slo:
  authorizationCodeLogin:
    p95: 750ms
    p99: 1500ms
    successRate: 99.95%
  refreshToken:
    p95: 250ms
    p99: 600ms
    successRate: 99.99%
  clientCredentials:
    p95: 200ms
    p99: 500ms
    successRate: 99.99%
  availabilityAfterOneZoneLoss:
    recoveryTime: 120s
    sustainedCriticalLoadPercent: 100
```

Max throughput bez SLO iba ukazuje bod collapse-u. Test success vyžaduje latency, errors, correctness, resource headroom a downstream business outcome. Expected authentication rejects sa oddeľujú od server errors.

## 5. Oficiálny CPU starting model

Aktuálny Keycloak sizing guide uvádza ako orientačný starting point na referenčnej konfigurácii:

```text
15 password-based logins/s
→ približne 1 vCPU pre cluster

120 client-credential grants/s
→ približne 1 vCPU pre cluster

120 refresh-token requests/s
→ približne 1 vCPU pre cluster
```

Tieto rates sa nesčítavajú vždy mechanicky; mixed workload sa musí zmerať. Password validation je primárne hashing CPU. Client credentials v referenčnom teste spotrebúvali veľa CPU na nové TLS connections. CPU architecture môže meniť non-password throughput; password hashing môže škálovať odlišne.

Guide odporúča približne 150 % extra CPU headroom nad vypočítaný request, aby zostala kapacita na spikes, startup a failover. To znamená napríklad request 4 vCPU a limit približne 10 vCPU, nie cieľ trvalo používať 100 % limitu. CPU throttling v testoch významne znižoval performance.

## 6. Password hashing ako security-performance contract

```text
stronger Argon2/PBKDF2 policy
→ viac CPU/memory per validation
→ nižší credential-cracking risk
→ nižší login throughput per core
```

Nikdy neznižuj hashing strength iba preto, aby benchmark prešiel. Najprv oddeľ cached SSO, password login a brute-force traffic, pridaj CPU, load shedding a capacity. Test dataset musí mať hashes vytvorené rovnakým algoritmom/strength ako production.

Metric `keycloak_credentials_password_hashing_validations_total` pomáha odhadnúť skutočný password-validation rate a obsahuje realm, algorithm, hashing strength a outcome tags. User-event `login` zahŕňa aj cookie logins, preto je iba aproximácia password demandu.

## 7. Memory starting model

Oficiálny single-cluster guide uvádza približne 1 250 MB base memory per Pod vrátane realm caches a 10 000 cached sessions v referenčnom scenári. Container-aware Keycloak/JVM používa približne 70 % memory limitu pre heap a ráta približne 300 MB non-heap overheadu.

Orientačný výpočet:

```text
expected total memory = 1250 MB
non-heap reserve = 300 MB
heap fraction = 0.70

memory limit ≈ (1250 - 300) / 0.70
≈ 1357 MB
```

Toto nie je universal minimum. Providers, themes, caches, active sessions, thread stacks, TLS buffers, JIT/code cache a native libraries menia footprint. Kubernetes request má pokryť stable expected use; limit musí ponechať startup/rebalance/headroom bez OOMKill.

## 8. Heap, non-heap a container limit

Sleduj:

```text
heap used/committed/max
old-generation occupancy
allocation rate
GC pause/frequency
metaspace a code cache
thread count/stack memory
direct/native buffers
container working set a RSS
OOMKilled/restart history
```

Low heap after full GC s high RSS môže znamenať native/non-heap pressure. Zvýšenie limitu bez heap dumpu môže iba oddialiť leak. Heap dump obsahuje credentials/session/PII a musí byť chránený ako sensitive incident artifact.

## 9. Cache cardinality a cold state

Warm caches znižujú database reads, ale test len po dlhom warm-up-e podhodnotí startup/failover load. Po Pod restart-e sa caches plnia znova.

Pri viac než približne 2 500 súčasne používaných clients nemusia default caches 10 000 entries držať všetky relevantné client/user data. Current guide odporúča ako starting point:

```text
users cache size
→ 2 × concurrently used clients

realms cache size
→ 4 × concurrently used clients
```

Názvy cache sú historicky neintuitívne, preto zmenu potvrdzuj cez hit ratio a database reads. Väčší cache count zvyšuje memory a warm-up/rebalance cost. Testuj cold, warming a steady state.

## 10. Persistent sessions a database demand

Default persistent sessions zapisujú session state do databázy. Referenčný Aurora PostgreSQL multi-AZ model uvádza približne na každých 100 login/logout/refresh requests/s:

```text
~1400 Write IOPS
~0.35 až 0.7 database vCPU
```

Rozsah CPU závisí od saturation a latency objective. Vyššia CPU saturation môže znížiť CPU per request, ale zvýšiť response time. Hodnoty neplatia automaticky pre inú database, storage, session model alebo query plan.

Sleduj writer/replica CPU, write/read IOPS, commit latency, locks, buffer/cache hit, WAL, connection count a failover. Keycloak metrics bez database telemetry nedokážu určiť bottleneck.

## 11. Global connection budget

```text
replicas × db-pool-max-size
+ migration/monitoring/failover reserve
≤ database connection budget
```

Vyšší pool nie je automatická oprava. Metric `agroal_awaiting_count` ukazuje threads čakajúce na connection; `agroal_active_count` a `agroal_available_count` ukazujú used/idle. Ak zvýšenie poolu overloadne DB, latency sa zhorší. Alternatívou je znížiť HTTP worker concurrency, zvýšiť cache hit ratio, optimalizovať database alebo scale DB.

## 12. HTTP a executor thread pools

Keycloak requesty a blocking probes používa Quarkus executor pool s default maximum typicky 50 alebo viac threads podľa CPU. Viac threads než database connections môže vytvoriť queue na pool-e a memory/CPU overhead.

```text
HTTP/executor concurrency
→ bounded podľa CPU, DB pool a latency
→ load shedding pred unbounded queue
```

`http-max-queued-requests` môže odmietnuť overload bounded `503` namiesto zvyšovania latency do timeoutov. `http-pool-max-threads` sa mení iba po evidence, nie podľa core countu naslepo.

JGroups communications môžu na OpenJDK 21+ pri aspoň štyroch cores benefitovať z virtual threads; aktuálny guide preferuje OpenJDK 25 alebo novší pre najlepší behavior. Target JDK sa pin-ne a benchmarkuje.

## 13. Horizontal scaling trade-off

Additional Pods môžu zvyšovať throughput približne lineárne, kým bottleneck neprejde na database, cache, load balancer alebo external dependency. Každý Pod pridáva:

```text
DB pool ceiling
cache member a state transfer
JVM base memory
startup/warm-up cost
TLS/listener capacity
```

Viac Pods môže znižovať efficiency per request. Multi-cluster pridáva cross-site/database operations. Scale-out test musí porovnať 1→2→3→N Pods pri rovnakom total load-e a pri load-e proportional to replicas.

## 14. HPA

Operator `Keycloak` CR môže byť HPA target:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: atlas-keycloak
  namespace: identity-prod
spec:
  scaleTargetRef:
    apiVersion: k8s.keycloak.org/v2beta1
    kind: Keycloak
    name: atlas-keycloak
  minReplicas: 3
  maxReplicas: 9
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

CPU scaling reaguje až po demand-e a startup nie je instant. Min replicas a headroom musia zvládnuť spikes do readiness. Memory-based HPA sa pri persistent sessions alebo remote Infinispan všeobecne neodporúča ako primary response; memory issue sa má diagnostikovať a request/limit/cache upraviť.

Max replicas sa overí proti global DB pool, cache topology a survivor capacity. Scale-down musí rešpektovať stabilization, draining a cache rebalance.

## 15. Load-test dataset

Dataset musí reprezentovať cardinality a distribution:

```text
realms a realm sizes
users, groups a group depth
clients a concurrently used clients
roles/composites/scopes/mappers
sessions/offline sessions
LDAP/broker links
Authorization Services resources/policies
provider/theme variants
```

Jeden realm s desiatimi users nepokryje million-user query plans alebo cache churn. Dataset provider z Keycloak Benchmark je test-only a jeho endpoints nie sú secured; nikdy ho neinštaluj do production.

Dataset seed má deterministic IDs/distribution a cleanup. Generovanie datasetu nesmie byť zahrnuté do measured workload phase, pokiaľ testuješ import/provisioning.

## 16. Keycloak Benchmark

Keycloak Benchmark project poskytuje Gatling scenarios, provisioning a observability. Release benchmark binary má zodpovedať target Keycloak release; `main` môže cieliť nightly versions.

Príklad:

```bash
./kcb.sh \
  --scenario=keycloak.scenario.authentication.AuthorizationCode \
  --server-url=https://sso-perf.atlas.example \
  --realm-name=perf-realm
```

Incremental mode môže hľadať maximum successful workload po warm-up-e a postupných increments. Maximum je relevantné iba pri definovaných SLO a bez load-generator saturation.

## 17. Load-generator capacity

Pri viac než približne 300 new users/s voči remote instance môže jeden generator stallnúť pre veľa connections v `TIME_WAIT`. Rozdeľ load across nodes alebo použi Ansible/EC2/equivalent setup.

Sleduj generator:

```text
CPU/memory/GC
ephemeral ports a TIME_WAIT
DNS/TLS handshake latency
network bandwidth/loss
open file descriptors
scheduler lag a failed injections
```

Server nemôže byť vyhlásený za limit, ak generator nedodáva planned arrival rate. Closed-model virtual users môžu pri server slowdown-e znížiť arrival rate; open model lepšie reprezentuje externý demand, ale môže prudko overloadnúť systém.

## 18. Test phases

Jeden dlhý load run nevie oddeliť scenario correctness, JIT/cache warm-up, steady-state capacity, overload behavior, leak risk a recovery. Fázy preto menia presne jednu vlastnosť testu a majú vlastné SLO, stop conditions a evidence window. Až ich spojenie ukáže, či systém zvláda normálny demand, prudkú zmenu aj návrat do stabilného stavu.

```text
smoke
→ scenario correctness pri malom load-e

warm-up
→ JIT, pools, TLS, caches

steady load
→ SLO pri expected traffic

spike
→ náhly login/refresh burst

stress
→ nájsť saturation a graceful degradation

soak
→ leak, cache growth, pool churn, token/session accumulation

failure/chaos
→ Pod/node/AZ/DB/dependency failure pod loadom

recovery
→ warm-up, backlog drain a second steady phase
```

Každá fáza má start/end timestamps, immutable config a expected assertions. Nemixuj tuning change uprostred runu bez novej generation identity.

## 19. Warm versus cold tests

Warm a cold state reprezentujú odlišné production moments. Warm run meria stabilized JIT, pools a caches, kým cold alebo mixed rollout ukazuje startup, database reload, cache fill a temporary cohort asymmetry. Capacity plan musí prijať oba outcomes, pretože incident alebo deploy môže presunúť celý traffic na cold successor.

```text
cold start
→ fresh Pods/JIT/caches/pools

warm steady
→ stable caches/JIT/connections

rolling restart
→ mixed cold/warm cohort

full restart
→ all caches/JVM cold, persistent sessions in DB
```

Production incidenty a deployments často prebiehajú v cold/mixed state, preto warm-only benchmark nie je capacity proof. Cold state môže zvýšiť DB IOPS a latency niekoľkonásobne podľa datasetu.

## 20. Password, M2M a refresh separation

Run isolated scenarios first to kalibrovať resource slope, potom realistic mix:

```text
password-only
→ hashing CPU

client-credentials-only
→ token construction + TLS/client behavior

refresh-only
→ session/DB/token generation

mixed
→ contention a shared limits
```

Ak isolated slopes vyzerajú zdravo a mix zlyhá, hľadaj shared thread/DB/cache/TLS bottleneck. Percentile porovnanie per journey je povinné.

## 21. External dependencies

LDAP, identity broker, SMTP, KMS/secret store, external Infinispan a remote policy/API calls majú vlastnú capacity a latency. Stub môže byť vhodný na Keycloak core baseline; production-like dependency test je potrebný na end-to-end capacity.

```text
core benchmark s deterministic stub
→ isolate Keycloak

integration benchmark s real dependency profile
→ measure full journey
```

Nevydávaj core-only result za end-to-end SLO. Timeout/retry môže amplifikovať load na dependency.

## 22. Custom providers a themes

Event listeners, mappers, authenticators, User Storage, REST endpoints a FreeMarker themes môžu meniť CPU, memory, transaction a external calls. Test target image musí obsahovať production provider set.

Provider benchmark zahŕňa dependency outage/backpressure, not only success. Unbounded queue môže vyzerať rýchlo krátko a potom spôsobiť OOM počas soak-u.

## 23. Metrics a correlation

Minimálny set:

```text
HTTP request duration/count/status
user-event rates a errors
password hashing validations
JVM heap/GC/threads/CPU
container CPU throttling/RSS/restarts
Agroal active/available/awaiting
cache hit/miss/entries/invalidations/topology
JGroups/cluster members/rebalance
DB CPU/IOPS/latency/connections/locks
load balancer latency/errors
load-generator delivered rate/errors
```

Metric names a labels sa pin-nú k Keycloak version. Event counters sú instance-local a resetnú sa po restart-e; aggregate queries musia zohľadniť Pod population a resets.

## 24. Bottleneck signatures

Bottleneck sa neurčuje podľa najvyššej jednej metriky, ale podľa spoločného patternu medzi arrival rate, latency, queues a resource saturation. Rovnaká high latency môže vzniknúť hashing CPU, database waitom, cache churnom alebo load-generator limitom. Signatures sú preto hypothesis shortcuts, ktoré sa musia potvrdiť one-axis comparative experimentom.

```text
CPU near limit + throttling + low DB wait
→ Keycloak/hash/crypto/provider CPU bottleneck

agroal_awaiting > 0 + DB not saturated
→ pool/thread mismatch alebo too-small pool

agroal_awaiting > 0 + DB saturated
→ DB/cache/query bottleneck; larger pool may worsen

low users/realms cache hit + high DB reads
→ cache cardinality/size or churn

high GC + rising old gen after full GC
→ heap pressure/leak/cache/session growth

low server utilization + generator TIME_WAIT/CPU
→ load-generator bottleneck
```

Hypothesis sa potvrdí comparative testom po jednej bounded zmene.

## 25. Change-one-axis discipline

Tuning je experiment s kauzálnou hypotézou. Ak sa súčasne zmení CPU, pool, cache a replicas, výsledok nedokáže priradiť improvement ani regression konkrétnemu mechanismu a nový limit zostane neznámy. One-axis rerun zachováva dataset, workload, topology a SLO, aby sa dala zmena reprodukovať alebo bezpečne vrátiť.

```text
baseline run
→ one config/resource change
→ same dataset/workload/topology
→ rerun
→ compare SLO and saturation
```

Súčasné zvýšenie CPU, poolu, cache a replicas znemožní attribution. Každá zmena má expected mechanism a forbidden regression. Tuning bez second runu nie je evidence.

## 26. Failover performance

HA test pod loadom:

```text
steady critical load
→ kill Pod/node alebo lose AZ
→ detection/routing
→ cache/DB recovery
→ surviving capacity
→ SLO degradation window
→ second steady phase
```

Survivor musí zvládnuť defined failure load, nie iba vrátiť health `UP`. Sleduj connection storms, cache warm-up, DB failover, queue drain a client retries. Retry without jitter môže vytvoriť thundering herd.

## 27. Soak a state growth

Soak trvá dostatočne dlho na token/session/connection/cache cycles. Sleduj:

```text
active a offline sessions
session cleanup jobs
cache entry plateau
database table/index growth
heap after full GC
thread/file descriptor growth
event-listener buffers
log/audit volume
```

Stable one-hour test nemusí odhaliť daily cleanup alebo offline-session retention. Test clock/token TTL môže byť skrátený v isolated environment-e, ale behavior musí zostať reprezentatívny.

## 28. Security počas performance testu

Performance environment môže obsahovať synthetic credentials, tokens a large user datasets. Load scripts/logs/reports nesmú ukladať production secrets alebo raw tokens. Dataset provider a open registration endpoints sú test-only a network-isolated.

Neoslabuj TLS, hashing, MFA, authorization alebo audit iba kvôli benchmarku, pokiaľ ide o explicitný component baseline. Výsledok sa potom nesmie aplikovať na production secured path bez adjustment.

## 29. Incident `KC-PAY-81`

Atlas sizing použil aggregate 600 RPS z health dashboardu a nasadil tri Pods po 2 vCPU. Test obsahoval iba refresh requests po dlhom warm-up-e. Production Monday peak však priniesol 60 password logins/s, 400 client-credentials/s, cold caches po rollout-e a 4 000 concurrently used clients.

CPU throttling predĺžil password hashing, `realms/users` cache churn zvýšil DB reads a autoscaler pridal Pods, čím global pool ceiling prekročil database limit. Jediný Gatling node nedokázal pri stress test-e udržať arrival rate pre `TIME_WAIT`, preto predchádzajúci benchmark nesprávne označil server za stabilný.

```text
aggregate RPS bez journey mixu
+ warm-only small dataset
+ missing CPU headroom
+ HPA bez DB/cache budgetu
+ saturated load generator
→ false capacity verdict
```

Recovery vytvorila journey-based sizing, 150 % CPU headroom, cold/warm/failover phases, client-cardinality cache test, global pool budget a distributed load generators. Acceptance zahŕňala zone-loss survivor load a second steady phase.

## 30. Evidence-preserving tuning a recovery

Zachovaj image/config/provider/theme digests, dataset seed/hash, workload/scenario revision, generator versions/nodes, exact timestamps, SLO, all server/DB/cache/generator metrics, Kubernetes events, failures a every tuning change.

Pri overload-e najprv chráň system load sheddingom a bounded retries. Nemeň súčasne pool, threads, CPU a replicas. Recovery change sa overí rovnakým scenario a následne realistic mix/failure testom.

## 31. Acceptance matrix

Positive:

```text
expected mix + production-like dataset
→ SLO met
→ no hidden saturation
→ business operations correct
```

Recovery:

```text
spike/failure/rolling restart
→ bounded degradation
→ survivor capacity
→ backlog/caches recover
→ second steady phase meets SLO
```

Forbidden:

```text
benchmark bez generator-capacity proof
→ performance review rejects

hashing/TLS/authz oslabené bez explicitného baseline labelu
→ security gate rejects

HPA max replicas prekračujú DB pool/cache capacity
→ capacity gate rejects

warm-only average-latency result označený production capacity
→ acceptance rejects
```

Second-architecture test porovná CPU architecture/JDK alebo topology pri rovnakom workload-e. Second-run reprodukuje baseline v tolerancii a potvrdí, že improvement nie je noise.

## Kontrolné otázky

- Aký exact request/journey mix a arrival pattern testujeme?
- Aký hashing, TLS, provider, dataset, cache/session a database model používame?
- Sú CPU/memory čísla iba official starting point alebo vlastne meraná capacity?
- Má každý Pod a cluster dostatočný CPU headroom pre startup a failure?
- Aký je global DB pool ceiling pri max replicas?
- Pokrýva dataset concurrent clients, users, groups a sessions?
- Testujeme cold, warm, rolling, soak, spike a failover state?
- Dokáže load generator doručiť planned arrival rate bez TIME_WAIT/CPU/port bottlenecku?
- Korelujeme Keycloak, JVM, DB, cache, LB a generator metrics?
- Meníme jednu axis a robíme comparative second run?
- Zvládne surviving topology celý defined critical load?

## Primárne zdroje

- [Keycloak — Concepts for sizing CPU and memory resources](https://www.keycloak.org/high-availability/single-cluster/concepts-memory-and-cpu-sizing)
- [Keycloak — Scaling](https://www.keycloak.org/getting-started/getting-started-scaling-and-tuning)
- [Keycloak — Concepts for database connection pools](https://www.keycloak.org/high-availability/single-cluster/concepts-database-connections)
- [Keycloak — Concepts for configuring thread pools](https://www.keycloak.org/high-availability/single-cluster/concepts-threads)
- [Keycloak Benchmark](https://www.keycloak.org/keycloak-benchmark/)
- [Keycloak Benchmark — Running benchmarks](https://www.keycloak.org/keycloak-benchmark/benchmark-guide/latest/run/)
- [Keycloak — Troubleshooting using metrics](https://www.keycloak.org/observability/metrics-for-troubleshooting)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Securing APIs, microservices a MCP servers cez Keycloak](securing-apis-microservices-mcp-servers.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Keycloak troubleshooting →](keycloak-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
