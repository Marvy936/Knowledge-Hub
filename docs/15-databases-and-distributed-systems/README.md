# Databases and Distributed Systems

Táto sekcia vysvetľuje, ako navrhovať, prevádzkovať a diagnostikovať stateful systémy podľa explicitných business invariantov, transaction boundaries, consistency semantics a failure modelov. Začína výberom databázového modelu, pokračuje transactions, indexes, locks, migrations, replication a recovery a neskôr rozširuje model na distributed communication, caching, consensus, retries, rate limiting, idempotency a backpressure.

Databáza tu nie je iba persistence API. Je to systém, ktorý rozhoduje o authoritative state-e, visibility, concurrency, durability, recovery a dôkazoch potrebných na rozlíšenie committed, aborted, stale, duplicated, lost alebo unknown outcomes.

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
3. [Indexy, locks a migrácie](indexes-locks-and-migrations.md)
4. [Replikácia a high availability](replication-and-high-availability.md)

Aktuálny authoritative stav sekcie je **4/18 · In progress**.

## Plánované pokračovanie

Authoritative poradie bude pokračovať bez zmeny roadmapy:

5. Backups a point-in-time recovery
6. Connection pooling
7. PostgreSQL, MySQL a Redis
8. Monolith, modular monolith a microservices
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

## Connected learning scenario

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

Incident vytvára chain:

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

### Causal boundaries

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

### Indexy, locks a migrácie

- definovať exact query/index/migration subject a scale;
- vysvetliť planner, selectivity a access paths;
- navrhovať B-tree, multicolumn, partial, unique a specialized indexes podľa operators a distribution;
- merať read benefit proti write/storage/WAL costu;
- vytvoriť lock graph a nájsť root blocker;
- poznať DDL a concurrent/online-build caveats;
- používať expand–backfill–switch–contract protocol;
- navrhnúť resumable, idempotent a conflict-safe backfill;
- overiť valid/effective index a constraint state.

### Replikácia a high availability

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

## Dominantný model sekcie

```text
business capability a stateful operation
→ exact authoritative data/distributed subject
→ invariant, consistency a availability objectives
→ data/transaction/communication topology
→ concurrency, replication a failure mechanisms
→ observed current generation and effective state
→ bounded write/read/recovery decision
→ business outcome and reconciliation
→ migration/failover/second-operation closure
```

Každá komplexná kapitola musí rozlišovať:

- authoritative, derived a cached state;
- logical operation od physical attemptu;
- transaction commit od client acknowledgementu;
- received, durable, applied a visible replica state;
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
| Indexy, locks a migrácie | Learning | L2 |
| Replikácia a high availability | Learning | L2 |
| Backups a point-in-time recovery | Not Started | L0 |
| Connection pooling | Not Started | L0 |
| PostgreSQL, MySQL a Redis | Not Started | L0 |
| Monolith, modular monolith a microservices | Not Started | L0 |
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