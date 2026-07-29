# Databases and Distributed Systems

Táto sekcia vysvetľuje, ako navrhovať, prevádzkovať a diagnostikovať stateful systémy podľa explicitných business invariantov, transaction boundaries, consistency semantics a failure modelov. Začína výberom databázového modelu, pokračuje transactions, indexes, locks, migrations, replication a recovery a následne rozširuje model na connection admission, product-specific semantics, architecture boundaries, distributed communication, caching, consensus, retries, rate limiting, idempotency a backpressure.

Databáza tu nie je iba persistence API. Je to systém, ktorý rozhoduje o authoritative state-e, visibility, concurrency, durability, recovery a dôkazoch potrebných na rozlíšenie committed, aborted, stale, duplicated, lost alebo unknown outcomes. Distributed architecture zároveň určuje, kde tieto rozhodnutia vznikajú, kto ich vlastní a ako sa obnovujú po partial failure-i.

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

Aktuálny authoritative stav sekcie je **8/18 · In progress**.

## Plánované pokračovanie

Authoritative poradie bude pokračovať bez zmeny roadmapy:

9. Synchronous vs. asynchronous communication
10. Message queues a event-driven architecture
11. Service discovery a API gateway
12. Caching
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
→ nevhodne rozdelený authoritative state
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
- **Amplifiers:** retry load, invalid index existence-only check, stale read projection, async lag a pomalá client convergence.

Recovery používa:

```text
fence all writers
→ preserve transaction/WAL/timeline/migration evidence
→ establish one authoritative PostgreSQL history
→ classify exact operation cohorts
→ query provider idempotency ledger
→ replay iba never-sent exact manifest
→ reconcile sent-unknown/completed outcomes
→ atomic settlement + outbox transaction
→ rebuild document projection from durable stream
→ safe indexed migration
→ lag/position-aware promotion and writer epochs
→ second-operation, second-batch and second-failover validation
```

### `DB-PAY-57` — recovery, pooling, product roles a architecture boundaries

Release `payments 8.1` rozdelil modular settlement flow na samostatné runtime services:

```text
settlement-api
→ merchant-policy-service / MySQL
→ idempotency-service / Redis
→ ledger-service / PostgreSQL
→ provider-execution-service
→ projection-service
```

Po end-of-month scale-out-e bežalo `96` settlement Podov. Každý mal application pool `40` a `minimumIdle 20`, teda teoreticky `3 840` connections a `1 920` immediate idle/warmup attempts proti PostgreSQL application envelope-u približne `585` connections.

O `11:38 UTC` network flap spustil reconnect storm:

```text
server connections: 587
active queries: 164
idle connections: 271
idle in transaction: 83
pool checkout p99: 8.7 s
connect attempts: 12 400/min
```

Emergency change aktivovala PgBouncer transaction pooling so 120 server connections. Application však nastavovala `app.tenant_id` pri physical session initialization a používala temporary table `pending_settlement_batch`. Ďalšia transaction nemusela dostať rovnakú server session.

Od `11:46:12 UTC` vznikali missing/stale policy contexts a retry amplification. Incident vyžadoval:

- policy verification pre `214` operations;
- provider routing verification pre `31` operations;
- reconciliation `19` sent-unknown operations;
- classification `68` missing Redis dedupe keys po failover/restart window;
- provider evidence pre `7` duplicate attempts;
- nulové potvrdené duplicate settlements až po provider-idempotency reconciliation.

Tím chcel PostgreSQL obnoviť na `11:46:11 UTC`, no recovery chain mal gap:

```text
base backup: 00:00 UTC — success
last continuous WAL: 11:40:59 UTC
missing WAL: 11:41:00–11:56:59 UTC
next available WAL: 11:57:00 UTC
requested target: 11:46:11 UTC — unreachable
```

MySQL policy store mal vlastný binlog coordinate, Redis vlastný AOF/replication state a provider external ledger. Neexistoval versionovaný cross-store checkpoint.

Connected chain:

```text
premature service extraction
→ distributed settlement invariant a recovery ownership
→ fleet-wide pool multiplication
→ reconnect storm
→ incompatible transaction pooling
→ session tenant/temp-state failure
→ stale/missing policy generation
→ Redis cache authority inversion
→ provider retry/unknown outcomes
→ replicated logical corruption
→ incomplete WAL chain
→ isolated restore + cross-product reconciliation
```

Causal boundaries:

- **Trigger:** network flap počas scale-out-u.
- **Pooling root cause:** per-Pod pools neboli odvodené z fleet-wide database envelope-u a transaction pooling nezodpovedalo session-state contractu.
- **Product-role root cause:** Redis cache/dedupe absence rozhodovala o authoritative retry namiesto PostgreSQL/provider evidence.
- **Recovery root cause:** backup control overoval job/upload activity, nie durable WAL continuity, target reachability a restore.
- **Architecture root cause:** service extraction rozdelila invariant, product roles a operational/recovery ownership skôr než boli boundaries a contracts pripravené.
- **Amplifiers:** high minimum idle, synchronized reconnect, retries bez shared budgetu, async replication, chýbajúca policy-generation identity a green front-door dashboards.

Authoritative redesign:

```text
modular settlement command core
→ atomic PostgreSQL settlement + idempotency + outbox
→ exact MySQL merchant-policy generation stored with decision
→ durable event
→ independent provider-execution service
→ rebuildable projection service
→ Redis iba cache/admission/dedupe accelerator
→ fleet-wide connection + retry budget
→ WAL/binlog/provider cross-store recovery manifest
→ second-burst, second-client, restore and partial-failure validation
```

## Cieľ zvládnutia prvého bloku

### Relational vs. non-relational databases

- definovať exact database-selection subject;
- identifikovať authoritative facts, aggregates, relationships a invarianty;
- rozlíšiť relational, key-value, document, wide-column, graph, search a analytical models;
- odlíšiť normalization od denormalized derived projection;
- navrhovať query-first aj invariant-first;
- posúdiť transaction, consistency, partition a hot-key requirements;
- rozlíšiť polyglot persistence od dual authority;
- overiť model cez migration, recovery a second-operation outcomes.

### Transactions a ACID

- definovať transaction subject, read/write set a acknowledgement boundary;
- vysvetliť atomicity, consistency, isolation a durability;
- rozlíšiť dirty/non-repeatable/phantom reads, lost update a write skew;
- chápať MVCC, pessimistic a optimistic concurrency;
- diagnostikovať waits, blockers, deadlocks a serialization failures;
- rozlíšiť committed, aborted a unknown outcomes;
- používať stable idempotency a transactional outbox pre external workflows;
- overiť skutočnú ORM/autocommit runtime boundary.

### Indexy, locks a migrations

- definovať exact query/index/migration subject a scale;
- vysvetliť planner, selectivity a access paths;
- navrhovať B-tree, multicolumn, partial, unique a specialized indexes podľa operators a distribution;
- merať read benefit proti write/storage/WAL costu;
- vytvoriť lock graph a nájsť root blocker;
- poznať DDL a concurrent/online-build caveats;
- používať expand–backfill–switch–contract protocol;
- navrhnúť resumable, idempotent a conflict-safe backfill;
- overiť valid/effective index a constraint state.

### Replication a high availability

- definovať replication topology, commit policy a recovery objectives;
- rozlíšiť physical a logical replication;
- rozlíšiť sent, receive, flush, replay a visible positions;
- mapovať synchronous/asynchronous semantics na business RPO a latency;
- diagnostikovať generation, transfer a apply lag;
- navrhovať bounded-staleness read routing;
- definovať promotion eligibility a recovery authority;
- používať writer fencing, epochs a split-brain prevention;
- zahrnúť DNS/proxy/pool convergence do RTO;
- reconciliovať failover unknown outcomes a overiť failback.

## Cieľ zvládnutia druhého bloku

### Backups a point-in-time recovery

- definovať protected subject, consistency group a acknowledgement boundary;
- rozlíšiť logical/physical backup, snapshot, replication a archive;
- vysvetliť PostgreSQL base backup + WAL a MySQL full backup + binary-log PITR;
- overovať log continuity, source identity, checksums, keys a retention;
- vybrať clean recovery point a exact target/timeline;
- vykonať isolated restore a engine/schema/data/application/business validation;
- spracovať post-point divergence a cross-store reconciliation;
- preukázať alternate-target a second-responder restore.

### Connection pooling

- definovať fleet/pooler/database pooling subject;
- odvodiť total connection demand z replicas, min/max pools a workload classes;
- rozlíšiť application pool, shared pooler a server thread/execution pool;
- rozlíšiť session, transaction a statement pooling;
- odhaliť session-state, temporary-table, prepared-statement a advisory-lock incompatibility;
- merať pool queue, checkout wait, active/idle/idle-in-transaction a database waits;
- navrhnúť bounded timeouts, admission, reset/discard a admin reserve;
- overiť reconnect storm, failover a second-client state-isolation scenarios.

### PostgreSQL, MySQL a Redis

- priradiť product role podľa authority, invariantov, queries, latency, durability a recovery;
- vysvetliť PostgreSQL MVCC/WAL/constraints a MySQL InnoDB/redo/binlog/GTID boundaries;
- modelovať Redis data structures, MULTI/EXEC/WATCH, TTL/eviction, RDB/AOF a async replication;
- rozlíšiť relational transaction od Redis command/transaction modelu;
- neinterpretovať cache miss ako business absence;
- mapovať acknowledgement na product-specific durability/failover semantics;
- navrhnúť cross-product stable identity a reconciliation;
- overiť cache loss, replica failover, restore a second-operation outcome.

### Monolith, modular monolith a microservices

- definovať source/build/deploy/process/data/transaction/ownership boundaries;
- rozlíšiť monolith od modular monolithu a microservices;
- odvodiť module/service boundary z capability, invariantov a data authority;
- rozpoznať distributed monolith a shared-database coupling;
- navrhnúť local transaction alebo durable cross-service workflow;
- započítať connection/retry/telemetry/platform multiplication;
- preukázať independent compatibility, scale a failure isolation;
- používať modularize-first, strangler alebo branch-by-abstraction migration;
- porovnať intended architecture benefit s effective operational costom.

## Dominantný model sekcie

```text
business capability a stateful/distributed operation
→ exact authoritative data a architecture subject
→ invariant, consistency, durability a availability objectives
→ data/transaction/service/communication topology
→ concurrency, pooling, replication a failure mechanisms
→ observed current generation and effective state
→ bounded write/read/recovery/architecture decision
→ business outcome and reconciliation
→ migration/failover/restore/second-operation closure
```

Každá komplexná kapitola musí rozlišovať:

- authoritative, derived, cached a ephemeral state;
- logical operation od physical attemptu;
- transaction commit od client acknowledgementu;
- received, durable, applied a visible replica/log state;
- connection count od useful execution concurrency;
- database product od product role;
- module/service boundary od repository alebo Pod countu;
- technical data presence od business correctness;
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
| Synchronous vs. asynchronous communication | Not Started | L0 |
| Message queues a event-driven architecture | Not Started | L0 |
| Service discovery a API gateway | Not Started | L0 |
| Caching | Not Started | L0 |
| CAP theorem | Not Started | L0 |
| Consistency models | Not Started | L0 |
| Leader election a consensus | Not Started | L0 |
| Retry, timeout a circuit breaker | Not Started | L0 |
| Rate limiting | Not Started | L0 |
| Idempotency a backpressure | Not Started | L0 |

Sekcia zostáva **In progress**. Stav **Ready for user review** možno použiť až po vytvorení všetkých 18 authoritative kapitol, overení navigation chainu, glossary, audit artifacts a finálnom section-level consistency passe.
