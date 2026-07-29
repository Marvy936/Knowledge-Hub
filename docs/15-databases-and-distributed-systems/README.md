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

Aktuálny authoritative stav sekcie je **12/18 · In progress**.

## Plánované pokračovanie

Authoritative poradie bude pokračovať bez zmeny roadmapy:

13. CAP theorem
14. Consistency models
15. Leader election a consensus
16. Retry, timeout a circuit breaker
17. Rate limiting
18. Idempotency a backpressure

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

## Dominantný model sekcie

```text
business capability a stateful/distributed operation
→ exact authoritative, communication alebo derived subject
→ invariant, consistency, availability a latency objectives
→ data/transaction/service/message/route/cache topology
→ concurrency, replication, delivery, routing a coherence mechanisms
→ observed current generation and effective state
→ bounded write/read/route/retry/recovery decision
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
- technical availability od business correctness;
- trigger, root cause a causal amplifier;
- containment, reconciliation a authoritative recovery;
- configured object od valid/effective runtime mechanismu;
- first success od concurrent, second-operation a second-failure validation.

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
| CAP theorem | Not Started | L0 |
| Consistency models | Not Started | L0 |
| Leader election a consensus | Not Started | L0 |
| Retry, timeout a circuit breaker | Not Started | L0 |
| Rate limiting | Not Started | L0 |
| Idempotency a backpressure | Not Started | L0 |

Sekcia zostáva **In progress**. Stav **Ready for user review** možno použiť až po vytvorení všetkých 18 authoritative kapitol, overení navigation chainu, glossary, audit artifacts a finálnom section-level consistency passe.
