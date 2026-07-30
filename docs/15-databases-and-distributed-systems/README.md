# Databases and Distributed Systems

Táto sekcia vysvetľuje, ako navrhovať, prevádzkovať a diagnostikovať stateful a distributed systémy podľa explicitných business invariantov, transaction boundaries, consistency semantics, communication contracts a failure modelov. Začína výberom databázového modelu, pokračuje transactions, indexes, locks, migrations, replication a recovery a následne rozširuje model na service boundaries, synchronous/asynchronous communication, messaging, discovery, API routing, caching, CAP, consistency, consensus, retries, rate limiting, idempotency a backpressure.

Databáza, broker, gateway ani cache tu nie sú iba infrastructure APIs. Každý z nich rozhoduje o authoritative alebo derived state-e, visibility, ordering, concurrency, durability, routing, recovery a dôkazoch potrebných na rozlíšenie committed, accepted, delivered, stale, duplicated, lost alebo unknown outcomes.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [Testing and Software Quality](../04-testing-and-quality/README.md),
- [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md),
- [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md),
- [Kubernetes](../09-kubernetes/README.md),
- [Cloud and AWS](../11-cloud-and-aws/README.md),
- [Observability](../12-observability/README.md),
- [Security and Identity](../13-security-and-identity/README.md),
- [SRE and Operations](../14-sre-and-operations/README.md).

## Authoritative poradie — aktívne kapitoly

1. [Relational vs. non-relational databases](relational-vs-non-relational-databases.md)
2. [Transactions a ACID](transactions-and-acid.md)
3. [Indexy, locks a migrations](indexes-locks-and-migrations.md)
4. [Replication a high availability](replication-and-high-availability.md)
5. [Backups a point-in-time recovery](backups-and-point-in-time-recovery.md)
6. [Connection pooling](connection-pooling.md)
7. [PostgreSQL, MySQL a Redis](postgresql-mysql-and-redis.md)
8. [Monolith, modular monolith a microservices](monolith-modular-monolith-and-microservices.md)
9. [Synchronous vs. asynchronous communication](synchronous-vs-asynchronous-communication.md)
10. [Message queues a event-driven architecture](message-queues-and-event-driven-architecture.md)
11. [Service discovery a API gateway](service-discovery-and-api-gateway.md)
12. [Caching](caching.md)
13. [CAP theorem](cap-theorem.md)
14. [Consistency models](consistency-models.md)
15. [Leader election a consensus](leader-election-and-consensus.md)
16. [Retry, timeout a circuit breaker](retry-timeout-and-circuit-breaker.md)
17. [Rate limiting](rate-limiting.md)
18. [Idempotency a backpressure](idempotency-and-backpressure.md)

Aktuálny authoritative stav sekcie je **18/18 · Ready for user review**.

## Completion state

Všetkých 18 authoritative kapitol bolo po pôvodnom authoring passe kompletne znovu spracovaných v piatich prose-first strict blokoch. Každá kapitola má explicitný subject/generation/evidence model, connected failure a vysvetlené positive, recovery, overload alebo forbidden acceptance paths; per-file gate vykazuje nulové critical, high a medium learning-depth findings. Authoritative ordering, navigation, glossary a päť incidentov `DB-PAY-56` až `DB-PAY-60` zostávajú zachované. Sekcia je pripravená na používateľskú kontrolu; nie je tým automaticky používateľsky schválená, Accepted, Verified ani Stable.

## Connected learning scenarios

### `DB-PAY-56` — authority, transaction, migration a failover consistency

Atlas Payments release `payments 8.0` zaviedol read-friendly document aggregate a migration `merchant_operation_id` nad približne `780 miliónmi` PostgreSQL rows.

Intended business transition:

```text
merchant operation
→ authoritative settlement intent
→ durable outbox event
→ acknowledgement
→ broker/provider execution
→ final settlement state
→ derived merchant projection
```

Skutočný write path:

```text
PostgreSQL settlement INSERT
→ autocommit
→ document UPSERT
→ PostgreSQL outbox INSERT
→ autocommit
→ HTTP 202
```

Súčasne bežal backfill bez supporting partial indexu. Batch transactions trvali 4 až 11 minút, WAL generation vzrástla `6.4×` a async standby replay lag dosiahol `94 s`.

O `10:14 UTC` AZ network failure oddelila primary od časti application/control plane-u. Failover o `10:19 UTC` promoted standby bez exact acknowledged-position verdictu. Old primary nebola effective fence-nutá a prijímala časť writes ďalších `93 s`.

```text
business invariant a authority
→ rozdelený authoritative state
→ autocommit split settlement/outbox
→ incomplete acknowledged intents
→ unindexed backfill a long transactions
→ lock/WAL/replication amplification
→ async promotion bez acknowledged-position gate-u
→ old-writer fencing failure
→ divergent histories a stale projections
→ evidence-based reconciliation
```

Potvrdené dôsledky:

- `286` merchant operations vyžadovalo reconciliation;
- `37` client-acknowledged intents nebolo na promoted history;
- časť operations existovala iba ako settlement row bez outbox eventu;
- document projection zobrazovala `accepted` state bez executable authoritative intentu;
- provider ledger bol potrebný na odlíšenie `never-sent`, `sent-unknown` a `completed` cohorts.

Causal boundaries:

- **Trigger:** AZ network failure počas migration loadu.
- **Data-model root cause:** jeden settlement invariant bol rozdelený medzi dve independently committed authoritative stores.
- **Transaction root cause:** settlement a outbox nevznikali v jednej database transaction.
- **Migration root cause:** current-scale backfill nemal supporting access path, bounded transaction duration ani DDL lock gate.
- **HA root cause:** promotion eligibility nebola viazaná na acknowledged business position a effective old-writer fencing.
- **Amplifiers:** retry load, invalid index existence-only check, stale projection, async lag a pomalá client convergence.

Recovery používa jednu authoritative PostgreSQL history, exact operation cohorts, provider-ledger reconciliation, atomic settlement + outbox transaction, rebuild document projection z durable streamu, safe indexed migration, lag/position-aware promotion, writer epochs a second-operation/batch/failover validation.

### `DB-PAY-57` — recovery, pooling, product roles a architecture boundaries

Atlas Payments release `payments 8.1` rozdelil settlement flow medzi viac services a troch data products:

```text
settlement-api
→ merchant-policy-service / MySQL
→ idempotency-service / Redis
→ ledger-service / PostgreSQL
→ provider-execution-service
→ projection-service
```

Fleet 96 Podov používal pool max 40, teda teoreticky `3 840` PostgreSQL clients proti približne 585 application slots. Network flap a reconnect storm dosiahli `12 400 attempts/min`. Emergency PgBouncer transaction pooling znížil server sessions, ale aplikácia používala session-local tenant context, temporary tables a session assumptions, ktoré transaction pooling negarantuje.

Incorrect operations bolo potrebné obnoviť k targetu `11:46:11 UTC`, ale PostgreSQL WAL archive mal medzeru:

```text
last continuous WAL: 11:40:59 UTC
missing interval:     11:41:00–11:56:59 UTC
next segment:         11:57:00 UTC
requested target:     11:46:11 UTC
```

PostgreSQL, MySQL, Redis a provider nemali spoločný atomic recovery point. Restore preto použil starší clean point a rekonštrukciu post-point operations z outbox, binlogs, API evidence a provider ledgeru.

```text
premature service extraction
→ synchronous distributed chain
→ fleet connection multiplication
→ emergency transaction pooling
→ session-state leakage/missing context
→ stale policy a cache authority inversion
→ provider unknown outcomes
→ no common recovery point
→ evidence-backed reconstruction
```

Redesign používa:

- modular settlement command core s atomic PostgreSQL settlement + idempotency + outbox transition;
- MySQL ako authority pre versioned merchant policy;
- Redis iba ako rebuildable cache/admission/dedupe accelerator;
- provider execution a projections ako separate services s vlastným scale/failure modelom;
- fleet-wide connection budget a transaction-pooling-compatible application contract;
- tested WAL/binlog archive continuity a cross-store recovery checkpoint.

### `DB-PAY-58` — communication, messaging, routing a cache coherence

Release `payments 8.2` migroval provider execution z legacy synchronous request pathu na durable asynchronous flow.

Intended v8.2 path:

```text
merchant request
→ API gateway
→ settlement command core
→ PostgreSQL transaction: settlement + outbox
→ HTTP 202 + operation_id
→ Kafka settlement.commands.v3
→ provider worker
→ provider
→ durable final result
```

Legacy v8.1 path stále čakal na provider response. Gateway a Kubernetes Service používali broad route/selector a miešali oba contracts:

```text
legacy Pods: app=settlement-api, version=8.1
new Pods:    app=settlement-api, version=8.2
Service:     selector app=settlement-api
```

Provider p95 latency stúpla z `420 ms` na `2.4 s`, kým public deadline zostal `900 ms`. Počas 31 minút:

- `18 420` requests prišlo do gatewaya;
- `31 %` trafficu skončilo na legacy synchronous cohort-e;
- `2 906` calls timeoutlo a clients vytvorili `4 118` retry attempts;
- `206` logical attempts zasiahlo dve contract generations;
- `43` duplicate provider attempts vyžadovalo reconciliation.

Async producer používal durable outbox, idempotent producer a `acks=all`, ale consumers mali auto-commit offsets pred provider effectom. Po OOM killoch:

- `611` records malo committed offsets bez durable resultu;
- `84` operations nemalo provider attempt ani final state;
- retry path použil iný partition key a `19` histories malo zmenené ordering;
- broad replay nebol safe bez provider evidence.

Merchant policy cache používala mutable key `policy:{merchant_id}` bez generation. Invalidation consumer zdieľal unsafe auto-commit pattern a offset commitol pred effective delete-om:

- `1 206` settlements použilo stale policy počas 17 minút;
- `74` operations smerovalo na starý provider route;
- cache hit ratio zostal `97.8 %`;
- Redis dedupe miss bol nesprávne interpretovaný ako authoritative operation absence.

Causal boundaries:

- **Communication root cause:** mixed immediate-result contract pod jedným endpointom a jedným client retry modelom.
- **Messaging root cause:** consumer offset postupoval pred durable provider/business outcome-om.
- **Discovery/gateway root cause:** Service a route nemali contract-generation eligibility; discovery publikovala správny inventory podľa nesprávne širokého selectoru.
- **Cache root cause:** unversioned mutable entry závislá iba od invalidation eventu acknowledged pred effective mutation.
- **Cache authority inversion:** absence evictable Redis keyu rozhodovala o authoritative retry.

Authoritative redesign:

```text
POST /v2/settlements
→ exact async-v2 gateway route
→ settlement-command-v2 Service/endpoints only
→ atomic settlement + outbox commit
→ 202 + stable operation/status resource
→ manual consumer acknowledgement after durable provider result
→ versioned policy cache generation
→ authority lookup on cache miss/error
→ final completion and reconciliation evidence
```


### `DB-PAY-59` — partition, consistency, consensus a resilience amplification

Release `payments 8.3` presunul provider-route control a reconciliation leadership do päťčlenného consensus clusteru:

```text
Region A: 3 voting members
Region B: 2 voting members
quorum:   3
```

Provider `P1` začal prevažne timeoutovať. Majority Region A commitla route generation `912`, ktorá presmerovala new settlements na `P2`. Deväťminútový network partition oddelil Region B.

Region B nemohol získať linearizable current route bez quorum, ale application wrapper použil member-local serializable read a desaťminútovú cache generation `911`. Stale route preto autorizovala side-effecting provider attempts, hoci consensus cluster mal jednu správnu majority history.

```text
quorum commits route generation 912
→ minority Region B reads generation 911 locally
→ stale route used as current authority
→ provider P1 timeout
→ blind multi-layer retries
→ unknown outcomes a attempt amplification
```

Reconciliation scheduler používal etcd election lease `15 s`. Old leader epoch `51` po strate lease pokračoval ďalších `42 s`, pretože worker držal process-local `isLeader=true` a provider boundary nekontrolovala fencing epoch. Region A už pritom zvolil current leader epoch `52`.

Retry composition:

```text
merchant SDK:    1 + 2 retries
API gateway:     1 + 1 retry
provider client: 1 + 2 retries
maximum:         18 physical attempts / logical operation
```

Breaker bol local v každom zo `72` worker Podov, počítal iba HTTP `5xx` a ignoroval timeouts. Za deväť minút:

- `24 600` logical settlement operations vytvorilo `68 240` provider attempts (`2.77×` amplification);
- `3 842` Region B operations načítalo stale route generation `911`;
- `1 126` attempts smerovalo na `P1` po commitnutí generation `912`;
- `1 384` operations skončilo ako `sent-unknown`;
- `74` operations dostalo attempts z leader epochs `51` aj `52`;
- `27` duplicate physical provider attempts vyžadovalo reconciliation;
- provider idempotency zabránila duplicate financial effects.

Causal boundaries:

- **CAP root cause:** current-route operation nemala explicitný partition contract; minority availability bola použitá pre side effect vyžadujúci current authority.
- **Consistency root cause:** interné `strong` neznamenalo pomenovaný model, revision evidence ani minimum generation; history porušila linearizable a monotonic-read expectations.
- **Consensus/leadership root cause:** election fungovala správne, ale application leadership nebola priebežne guardovaná a external mutation nemala fencing token.
- **Resilience root cause:** timeouty, retries a breaker scopes nemali jeden logical-operation/deadline/retry-budget contract.
- **Amplifiers:** stale cache, 60-sekundový batch, per-Pod breaker, timeouty mimo failure countera, nested retries a shared resource pools.

Authoritative redesign:

```text
current provider-route side effect
→ linearizable read + minimum generation
→ settlement persists used revision/generation
→ quorum uncertainty = explicit refusal/defer

reconciliation worker
→ current election leader key
→ short bounded work unit
→ monotonically increasing fencing epoch
→ destination rejects stale epoch

provider execution
→ one retry owner
→ propagated deadline / async acceptance split
→ stable provider idempotency key
→ aggregate retry budget
→ provider+Region circuit breaker
→ provider lookup before unknown retry
```

Partition heal a recovery porovnávajú consensus revision/term, loaded route generations, leader epochs, logical operation/attempt trees a provider ledger. Replicas converging na majority history nie je closure, kým external attempts a unknown outcomes nie sú reconciled.

### `DB-PAY-60` — fair admission, stable operation identity a bounded flow

Release `payments 8.4` otvoril partnerom bulk replay po 47-minútovom provider outage-i. Gateway fleet mal `80` Podov a každý Pod vlastný token bucket:

```text
sustained per Pod:       450 requests/s
burst per Pod:           900 requests
fleet sustained:         36 000 requests/s
fleet immediate burst:   72 000 requests
```

Safe downstream envelope providera P2 bol približne `6 500 attempts/s` a `1 200` in-flight attempts. Limiter počítal raw HTTP attempts, nemal global/provider/tenant hierarchy a nerozlišoval expensive create od status alebo reconciliation requestu.

Počas 14 minút:

- partner replay dosiahol `21 600 requests/s` pri približne `3 200 requests/s` normal trafficu;
- gateway prijala `6.9 milióna` requests;
- jeden partner spotreboval `71 %` admitted create capacity;
- `429` responses nemali `Retry-After` a SDK retryovala po fixných `100 ms`;
- HTTP-attempt amplification dosiahla `2.4×`;
- oldest provider command dosiahol age `54 minút`.

Idempotency registry bola mimo authoritative settlement transaction:

```text
SELECT key
→ generate new operation_id
→ commit settlement + outbox
→ autocommit key mapping
```

Key nemal semantic payload fingerprint, cleanup ho mazal `20 minút` po `first_seen` aj pri non-terminal operation a provider key sa odvodzoval z internal `operation_id`.

Dôsledky:

- `12 480` duplicate submissions použilo rovnaké business operation IDs;
- `1 906` retries prišlo po registry expiry;
- `143` concurrent duplicate pairs prešlo check-before-insert race-om;
- vzniklo `83` duplicate authoritative operations;
- provider potvrdil `31` duplicate effects;
- `29` effects bolo automaticky reversed a `2` vyžadovali manuálnu remediation.

Provider fleet mal `48` worker Podov, každý s async limitom `2 000`, teda theoretical fleet in-flight `96 000`. Kafka consumer polloval do prakticky unbounded executor queue a partitions pause-ol až pri heap utilization nad `85 %`; po rebalance sa pause state neobnovil.

```text
Kafka backlog:              2.7 milióna commands
oldest command:             54 minút
queued executor tasks:      približne 348 000
worker OOM kills:           17
provider-pool wait p99:     11.2 s
safe provider in-flight:    1 200
```

Causal boundaries:

- **Rate-limiting root cause:** process-local request counter bez fleet, tenant, operation-cost a downstream-provider envelope-u.
- **Idempotency root cause:** claim nebol atomic s authoritative operation, nemal semantic fingerprint a expiroval pred terminal/reconciliation lifecycle-om.
- **Backpressure root cause:** API admission, consumer polling a executor submission neboli riadené downstream completion credits; buffers a in-flight concurrency boli rádovo väčšie než safe envelope.
- **Amplifiers:** autoscale, fixed-delay client retry, shared create/status budget, short key retention, provider key podľa attempt-derived operation ID, rebalance pause loss a immediate retry flow.

Authoritative redesign:

```text
global/provider/tenant/operation-class admission
→ provider P2 rate 5 800/s + hard in-flight 1 200
→ reserved status/cancellation/reconciliation capacity
→ atomic PostgreSQL idempotency claim + settlement + outbox
→ semantic fingerprint a stable business/provider identity
→ durable status/result reuse for duplicate requests
→ bounded consumer credits, poll a executor queues
→ pause/resume re-derived after rebalance
→ backlog-age-driven admission and delayed retry
→ provider lookup/reconciliation before unknown retry
→ bounded drain and second-overload validation
```

Final recovery vytvorila operation-equivalence groups podľa tenant, business operation ID a semantic payloadu, porovnala ich s provider ledgerom, zastavila duplicate attempts, vykonala reversals a drainovala oldest safe work pod hard provider credits. Pokles queue depth nebol považovaný za closure bez final business reconciliation.

## Cieľ zvládnutia prvého bloku

### Relational vs. non-relational databases

- definovať exact database-selection subject;
- identifikovať authoritative facts, aggregates, relationships a invarianty;
- rozlíšiť relational a hlavné non-relational models;
- odlíšiť normalized authority od denormalized projection;
- navrhovať query-first aj invariant-first;
- rozlíšiť polyglot persistence od dual authority.

### Transactions a ACID

- definovať transaction subject, read/write set a acknowledgement boundary;
- vysvetliť ACID, MVCC, isolation anomalies a concurrency controls;
- diagnostikovať waits, blockers, deadlocks a serialization failures;
- rozlíšiť committed, aborted a unknown outcomes;
- používať stable idempotency a transactional outbox;
- overiť skutočnú ORM/autocommit runtime boundary.

### Indexy, locks a migrations

- definovať exact query/index/migration subject a scale;
- vysvetliť planner, selectivity a access paths;
- navrhovať multicolumn, partial, unique a specialized indexes;
- vytvoriť lock graph a nájsť root blocker;
- používať expand–backfill–switch–contract;
- navrhnúť resumable, idempotent a conflict-safe backfill.

### Replication a high availability

- rozlíšiť physical/logical a synchronous/asynchronous replication;
- rozlíšiť receive, flush, replay a visible positions;
- mapovať commit acknowledgement na business RPO;
- diagnostikovať replication lag;
- definovať promotion eligibility, writer fencing a client convergence;
- reconciliovať failover unknown outcomes a overiť failback.

## Cieľ zvládnutia druhého bloku

### Backups a point-in-time recovery

- definovať protected consistency group a clean recovery point;
- rozlíšiť logical/physical backup, replication a archive;
- vysvetliť base backup + WAL/binlog PITR;
- overiť archive continuity, keys, isolated restore a timelines;
- rekonštruovať post-point operations a business outcome.

### Connection pooling

- odvodiť fleet-wide demand a database connection envelope;
- rozlíšiť application, session, transaction a statement pooling;
- overiť session-state/prepared/temp-object compatibility;
- navrhnúť queues, timeouts, admin reserve a reconnect budget;
- diagnostikovať pool wait oddelene od query latency.

### PostgreSQL, MySQL a Redis

- pomenovať product-specific authority/derived role;
- rozlišovať WAL, binlog, RDB/AOF a replication semantics;
- odlíšiť relational transaction od Redis command transaction;
- zabrániť cache authority inversion;
- korelovať cross-product versions a recovery evidence.

### Monolith, modular monolith a microservices

- odvodiť architecture z capability/invariant/change boundaries;
- rozlíšiť module, service, deployment, data a failure boundary;
- identifikovať distributed monolith a hidden shared-database coupling;
- nahradiť local transaction explicitným workflowom iba tam, kde to benefit obháji;
- testovať extraction, dual-run, retirement a second-change/failure outcome.

## Cieľ zvládnutia tretieho bloku

### Synchronous vs. asynchronous communication

- oddeliť wait semantics od transportu;
- definovať immediate a final outcome;
- navrhnúť deadline propagation, cancellation a unknown-outcome contract;
- rozlíšiť command, event a query;
- vytvoriť durable acceptance a status/result visibility;
- overiť retries, delayed completion a second attempt.

### Message queues a event-driven architecture

- definovať producer/broker/consumer acknowledgement boundaries;
- rozlíšiť queue, partitioned log a integration event;
- používať transactional outbox a stable event identity;
- scope-ovať at-most/at-least/exactly-once claims;
- navrhnúť partitioning, ordering, consumer ownership a in-flight limits;
- overiť retry, DLQ, replay a external-effect reconciliation.

### Service discovery a API gateway

- odlíšiť logical service a endpoint identity;
- analyzovať DNS, Service, EndpointSlice a dataplane generations;
- overiť route match/precedence a effective resolved route graph;
- viazať backend eligibility na contract generation a capability readiness;
- zahrnúť connection drain a gateway retry do correctness modelu.

### Caching

- definovať cache authority boundary, key a variant dimensions;
- odlíšiť TTL, freshness, validation, eviction a absence;
- navrhnúť version-aware fill a invalidation;
- zabrániť stampede, hot-key a negative-cache failure-om;
- inventarizovať multi-level caches a safe fallback;
- overiť delayed invalidation, failover, eviction a second read.


## Cieľ zvládnutia štvrtého bloku

### CAP theorem

- používať presné definície consistency, availability a partition;
- odmietnuť slogan `pick two` a rozhodovať per operation;
- rozlíšiť quorum-side progress, minority refusal a mergeable local progress;
- definovať stale-read allowed use, generation bound a heal reconciliation;
- mapovať partition decision na business invariant a external effect.

### Consistency models

- rozlíšiť linearizable, sequential, serializable, strict-serializable, causal a eventual histories;
- oddeliť transaction isolation od distributed consistency;
- navrhnúť bounded staleness, read-your-writes a monotonic session guarantees;
- používať revision/generation tokens a explicitný conflict model;
- overiť replicas, projections, caches, failover a second-client histories.

### Leader election a consensus

- odvodiť quorum a failure tolerance z membershipu;
- rozlíšiť proposal, replicated, committed, applied a visible state;
- chápať term, election timeout, lease a membership reconfiguration;
- viazať application leadership na current leader key a fencing epoch;
- testovať stale leader, minority partition, process pause a second election.

### Retry, timeout a circuit breaker

- rozlíšiť deadline, attempt timeout, failure a unknown outcome;
- určiť jedného retry ownera a stable operation/attempt identity;
- používať remaining budget, aggregate retry budget, backoff a jitter;
- navrhovať breaker scope/signals a bounded Half-Open probes;
- overiť retry storm, lost response, recovery a duplicate-effect forbidden outcome.

## Cieľ zvládnutia piateho bloku

### Rate limiting

- definovať exact admission subject, key, units, cost, scope a generation;
- rozlíšiť rate, quota, concurrency, burst a downstream capacity envelope;
- vysvetliť fixed/sliding windows, token/leaky bucket a distributed counters;
- odvodiť hierarchical global/provider/tenant/operation-class fairness;
- vytvoriť truthful `429`, `Retry-After`, priority a recovery-reserve contract;
- overiť autoscale, one-tenant flood, burst, counter failure a retry storm.

### Idempotency a backpressure

- definovať key scope, semantic fingerprint a atomic claim;
- modelovať accepted, processing, completed, failed-final a reconciliation-required states;
- zachovať stable operation identity cez outbox, broker, consumer a provider;
- odvodiť retention z retry, backlog, replay a reconciliation window-u;
- inventarizovať a hard-boundovať queues, buffers, pools a in-flight work;
- prenášať downstream credits cez poll/pause/executor/admission boundaries;
- overiť concurrent duplicate, lost response, rebalance, sustained overload a bounded drain.

## Dominantný model sekcie

```text
business capability a stateful/distributed operation
→ exact authoritative, communication alebo derived subject
→ invariant, consistency, availability a latency objectives
→ data/transaction/service/message/route/cache topology
→ concurrency, replication, partition, consistency, consensus, delivery, routing, cache, resilience, admission, idempotency a backpressure mechanisms
→ observed current generation and effective state
→ bounded write/read/partition/leadership/route/retry/admission/flow/recovery decision
→ business outcome and reconciliation
→ migration/failover/replay/second-operation closure
```

Každá komplexná kapitola musí rozlišovať:

- authoritative, derived a cached state;
- logical operation od physical attemptu;
- immediate acceptance od final completion;
- transaction commit od client acknowledgementu;
- producer/broker/consumer acknowledgement boundaries;
- received, durable, applied a visible state;
- declared route/selector od effective selected backendu;
- cache hit/miss od freshness a business existence;
- quorum/current authority od member-local alebo cached state;
- consensus leader od process-local leadership a fenced mutation;
- deadline/timeout od failure a unknown outcome;
- logical operation od nested physical retry tree a aggregate budget;
- configured local limit od effective fleet/global admission;
- rate/quota policy od current downstream backpressure;
- idempotency key od semantic operation equivalence;
- queue depth od queue age, deadlines a drain capacity;
- accepted durable work od completed/reconciled business effect;
- technical availability od business correctness;
- trigger, root cause a causal amplifier;
- containment, reconciliation a authoritative recovery;
- configured object od valid/effective runtime mechanismu;
- first success od concurrent, second-operation a second-failure validation.

## Finálny section-level consistency gate

Sekcia prešla finálnym gate-om nad celým authoritative poradím:

```text
data model a authority
→ transaction a physical access/concurrency
→ replication, backup a recovery
→ connection/product/architecture boundaries
→ synchronous/asynchronous communication
→ durable messaging, routing a cache coherence
→ partition a consistency model
→ consensus, leadership a resilience
→ fair admission, idempotency a bounded flow
→ business reconciliation a lifecycle closure
```

Overené bolo:

- presné poradie všetkých 18 kapitol podľa `ROADMAP.md`;
- päť connected incidentov `DB-PAY-56` až `DB-PAY-60` s oddelenými trigger, root-cause a amplifier boundaries;
- jednotná operation identity od client intentu cez transaction/outbox/message/provider až po final result;
- rozlíšenie authoritative, derived a cached state-u;
- rozlíšenie commit, acknowledgement, delivery, apply, visibility a completion boundaries;
- prepojenie consistency, availability, leadership, retries, rate limits, idempotency a backpressure s business invariantom;
- recovery cez reconciliation, fencing, replay/restore, bounded drain a second-operation/second-failure tests;
- glossary fragments `15a`–`15e`, generated `GLOSSARY.md`, roadmap a navigation chain;
- prázdne `DOCUMENTATION-AUDIT.md` a `documentation-audit.json` failure artifacts po finálnej synchronizácii;
- current primary-source semantics pre PostgreSQL, MySQL, Redis, Kafka, RabbitMQ, etcd, Kubernetes, HTTP, gRPC a Reactive Streams.

Stav **Ready for user review** znamená dokončené authoritative drafting a repository-level consistency gate. Neznamená automatické používateľské schválenie, produkčnú certifikáciu ani stav Verified alebo Stable.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Relational vs. non-relational databases | Learning | L2 |
| Transactions a ACID | Learning | L2 |
| Indexy, locks a migrations | Learning | L2 |
| Replication a high availability | Learning | L2 |
| Backups a point-in-time recovery | Learning | L2 |
| Connection pooling | Learning | L2 |
| PostgreSQL, MySQL a Redis | Learning | L2 |
| Monolith, modular monolith a microservices | Learning | L2 |
| Synchronous vs. asynchronous communication | Learning | L2 |
| Message queues a event-driven architecture | Learning | L2 |
| Service discovery a API gateway | Learning | L2 |
| Caching | Learning | L2 |
| CAP theorem | Learning | L2 |
| Consistency models | Learning | L2 |
| Leader election a consensus | Learning | L2 |
| Retry, timeout a circuit breaker | Learning | L2 |
| Rate limiting | Learning | L2 |
| Idempotency a backpressure | Learning | L2 |

Sekcia je **18/18 · Ready for user review**. Všetky authoritative kapitoly, connected scenarios, navigation, glossary a audit gates sú dokončené; stav neznamená automatické používateľské schválenie.
