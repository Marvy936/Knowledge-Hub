# PostgreSQL, MySQL a Redis

PostgreSQL, MySQL a Redis nie sú tri stupne jednej databázovej škály. PostgreSQL a MySQL sú relational database management systems s transactions, constraints, SQL a durable storage modelom. Redis je in-memory data-structure server s odlišným command, persistence, replication a failure contractom. Výber produktu musí vychádzať z authoritative facts, invariantov, access patterns, latency, durability, recovery a operational capability, nie z nálepiek `SQL`, `NoSQL`, `rýchle` alebo `cloud-native`.

```text
business capability a data role
→ exact product-selection subject
→ authoritative/derived/ephemeral classification
→ invariant, query a transaction requirements
→ durability/replication/recovery objectives
→ concurrency, scale a latency profile
→ PostgreSQL/MySQL/Redis mechanism fit
→ schema/index/key/persistence realization
→ operational ownership a evidence
→ failure/recovery/business validation
```

## 1. Exact product-role subject

Tvrdenie `použijeme Redis na výkon` alebo `PostgreSQL je source of truth` je príliš všeobecné. Subject musí uviesť:

- business capability a exact facts;
- authoritative, derived, cached, ephemeral alebo coordination role;
- transaction a invariant boundary;
- required query shapes a relationship model;
- write/read concurrency;
- latency a throughput objectives;
- data volume, growth a retention;
- durability a acknowledged-write semantics;
- consistency a stale-read tolerance;
- partitioning/sharding requirements;
- backup, PITR a reconciliation path;
- team/platform operational capability;
- migration a exit strategy;
- allowed aj forbidden failure outcomes.

Príklad:

```text
PostgreSQL:
  authority: settlement + outbox + idempotency operation
  invariant: one merchant operation → one executable settlement intent
  recovery: base backup + WAL PITR + provider reconciliation

MySQL:
  authority: merchant policy and provider configuration
  invariant: one active policy generation per merchant/provider/effective interval
  recovery: full backup + binlog/GTID replay

Redis:
  role: bounded cache, rate-limit counters, short-lived dedupe acceleration
  authority: none for acknowledged settlement completion
  recovery: rebuild from authoritative stores/events
```

## 2. PostgreSQL mental model

PostgreSQL je extensible relational database s MVCC, SQL, constraints, rich index types, WAL-based durability/recovery a širokým object modelom.

Dominantný write lifecycle:

```text
client transaction
→ parse/rewrite/plan
→ MVCC snapshot a locks
→ heap/index changes
→ constraints/triggers
→ WAL records
→ commit record + durability policy
→ visibility podľa transaction/isolation
→ replication/archive/recovery chain
```

Typické strengths:

- complex relational invariants;
- foreign keys, unique/exclusion/check constraints;
- advanced SQL, CTE, window functions a rich joins;
- MVCC a multiple isolation levels;
- JSON/JSONB spolu s relational modelom;
- partial, expression, covering a specialized indexes;
- extensions a custom types/operators;
- physical/logical replication;
- base backup + WAL PITR;
- transactional DDL pre veľkú časť schema operations.

Strength neznamená automatickú správnosť. PostgreSQL môže mať:

- dlhé transactions zadržiavajúce old row versions;
- vacuum/bloat pressure;
- lock a DDL blocking;
- connection/process overhead;
- hot rows/index pages;
- replication lag;
- nesprávne query plans pre stale statistics alebo skew;
- application invariants, ktoré constraints nepokrývajú.

## 3. MySQL mental model

MySQL je relational database platforma; pri moderných transactional workloads sa typicky používa InnoDB storage engine. Mechanizmus treba analyzovať cez konkrétny engine a server generation, nie všeobecné tvrdenie `MySQL robí X`.

Dominantný InnoDB lifecycle:

```text
client transaction
→ parser/optimizer/executor
→ InnoDB MVCC a locks
→ buffer pool/page changes
→ undo/redo
→ constraints a commit
→ binary log coordination
→ replication/PITR visibility
```

Typické strengths:

- mature relational transactions a indexing;
- široký ecosystem a operational familiarity;
- InnoDB buffer pool, MVCC, row locking a crash recovery;
- binary log pre replication a PITR;
- GTID-based replication identity;
- Group Replication/InnoDB Cluster options;
- practical compatibility s veľkým množstvom frameworks a managed services.

Product-specific caveats:

- storage engine mení transaction, locking a durability semantics;
- SQL modes a collation/case behavior môžu meniť correctness;
- DDL behavior a online-algorithm support závisia od operation/version;
- replication filter/binlog format ovplyvňujú recovery a replicas;
- `max_connections` a one-thread-per-connection default môžu vytvoriť overload;
- timestamps/timezones a implicit conversions potrebujú explicitný contract;
- optimizer/index behavior treba merať na current data distribution.

PostgreSQL a MySQL sa nemajú porovnávať sloganom `PostgreSQL je correct, MySQL je fast`. Obe platformy vedia bezpečne prevádzkovať critical relational workloads, ak exact engine, configuration, schema, transaction, replication a recovery semantics spĺňajú požadovaný contract.

## 4. Redis mental model

Redis je server natívnych data structures. Operations typicky pracujú nad keyom a data-type-specific commands:

- strings;
- hashes;
- lists;
- sets a sorted sets;
- streams;
- bitmaps/bitfields;
- geospatial, probabilistic, time-series, JSON, vector a ďalšie specialized structures podľa distribution/modules.

Dominantný command lifecycle:

```text
client connection
→ command parsing a key routing
→ single-threaded/main execution path pre data operation
→ in-memory mutation
→ replication stream
→ optional AOF/RDB persistence
→ acknowledgement
→ replica/failover/restart behavior
```

Redis je silný pre:

- bounded cache;
- counters a rate limiting;
- leaderboards a sorted-set ranking;
- ephemeral session data;
- short-lived dedupe acceleration;
- streams/queues s explicitným delivery contractom;
- coordination primitives, keď sú safety/liveness assumptions správne;
- low-latency data-structure operations.

Redis nie je automaticky non-durable. Poskytuje:

- RDB point-in-time snapshots;
- AOF write log;
- kombináciu RDB + AOF;
- no-persistence mode pre cache use cases;
- asynchronous replication a HA layers;
- transactions cez `MULTI`/`EXEC` a optimistic locking cez `WATCH`.

Tieto mechanizmy majú iné guarantees než relational transaction system:

- Redis transaction serializuje queued commands, ale neposkytuje rollback vykonaných commands;
- multi-key atomicity môže byť ovplyvnená cluster slot topology;
- replication je defaultne asynchronous;
- `WAIT` znižuje risk write loss, ale samo nevytvára strongly consistent CP database;
- eviction/expiry môže byť intended data lifecycle alebo correctness failure;
- persistence policy určuje acknowledged-write loss window;
- failover a client retry môžu vytvoriť duplicate/unknown outcomes.

## 5. Transactions a invariant boundaries

### PostgreSQL/MySQL

Relational transaction môže atomicky chrániť viac rows/tables v jednom database authority boundary:

```text
BEGIN
→ validate merchant operation
→ insert settlement
→ insert outbox
→ update balance/reservation
→ COMMIT
```

Constraints a isolation dopĺňajú application logic.

### Redis

Redis command môže byť atomic nad server execution boundary. `MULTI`/`EXEC` vykoná skupinu commands sekvenčne bez interleavingu; `WATCH` poskytuje optimistic check-and-set. To však nie je ekvivalent arbitrary relational transaction s rollbackom, foreign keys, query predicates a durable external workflow semantics.

Otázka nie je `podporuje transactions?`, ale:

- čo je exact read/write set;
- aké conflicts treba detegovať;
- či rollback alebo compensation je potrebná;
- aký durability outcome nasleduje po acknowledgement-e;
- či keys sú na jednej execution/cluster boundary;
- ako sa rieši unknown outcome a retry.

## 6. Data modeling

### PostgreSQL/MySQL

Relational schema prirodzene modeluje:

- entities a identities;
- relationships;
- normalization;
- referential integrity;
- joins a ad hoc queries;
- set-based transitions;
- constraints.

Obe platformy podporujú aj semi-structured JSON use cases, ale JSON column neodstraňuje potrebu schema, indexing a invariant governance.

### Redis

Redis model začína access patternom a data structure:

```text
operation
→ key identity a slot
→ data type
→ atomic command/Lua/function/transaction boundary
→ TTL/eviction/persistence
→ replication/failover
```

Unbounded key cardinality, large values, hot keys a O(N) commands môžu poškodiť latency a memory. Key naming je súčasť partitioning, multi-tenancy, observability a deletion lifecycle-u.

## 7. Indexing a query model

PostgreSQL a MySQL používajú optimizer a indexes na získanie rows podľa predicates/order/joinov. Index selection závisí od:

- operators;
- column order;
- selectivity a distribution;
- covering needs;
- write cost;
- query plan;
- statistics;
- engine-specific behavior.

Redis lookup je často direct key access alebo data-structure operation. Secondary indexy sa modelujú explicitnými structures alebo specialized capabilities. To môže byť veľmi rýchle, ale application musí udržiavať consistency medzi primary key a secondary structures alebo použiť atomic server-side mechanismus.

`Redis nemá SQL query planner` nie je slabina pri exact key lookup-e. Je to zásadná hranica pri ad hoc relational query requirements.

## 8. Durability a acknowledgement

### PostgreSQL

Durability závisí od WAL/commit configuration, storage, synchronous replication policy a recovery chain. Client acknowledgement musí byť mapované na commit/WAL position a failure scenario.

### MySQL

Durability závisí od InnoDB redo/flush semantics, binary-log coordination, storage a replication policy. Binlog je dôležitý pre replication aj PITR.

### Redis

Durability závisí od persistence mode-u:

- no persistence;
- periodic RDB snapshots;
- AOF s configured fsync policy;
- RDB + AOF.

`SET` success neznamená univerzálne `write prežije každý failover`. Persistence a replication configuration, acknowledgement requirements a failover model musia byť explicitné.

## 9. Replication a high availability

### PostgreSQL

- physical streaming replication;
- logical replication/publications/subscriptions;
- synchronous/asynchronous commit options;
- external promotion/orchestration a fencing;
- WAL archive/PITR.

### MySQL

- binary-log-based replication;
- GTID identity;
- source/replica topologies;
- Group Replication/InnoDB Cluster;
- MySQL Router/client convergence;
- binlog-based PITR.

### Redis

- asynchronous primary/replica replication;
- Sentinel alebo Cluster pre HA/topology;
- partial/full resynchronization;
- optional `WAIT` acknowledgement;
- AOF/RDB persistence independent from pure replication.

Vo všetkých troch produktoch platí:

```text
replica exists
≠ acknowledged write prežije every failure
≠ logical corruption je recoverable
≠ clients konvergovali na correct writer
```

## 10. Backup a recovery

| Produkt | Typical recovery building blocks |
|---|---|
| PostgreSQL | logical dump, physical/base backup, WAL archive, PITR, timelines |
| MySQL | logical/physical full backup, binary logs, positions/GTID, PITR |
| Redis | RDB, AOF, replica/cluster-specific recovery, application rebuild |

Recovery design má vychádzať z data role. Cache možno flushnúť a rebuildnúť. Authoritative settlement ledger potrebuje clean point, zero/explicit data-loss contract a business reconciliation.

## 11. Operational model

### PostgreSQL signals

- transactions, locks a wait events;
- connection/backend count;
- buffer/cache a I/O;
- checkpoints/WAL/archive;
- vacuum, dead tuples a bloat;
- replication positions/lag;
- query plans/statistics;
- backup/restore evidence.

### MySQL signals

- connections/threads;
- InnoDB transactions/locks;
- buffer pool a redo;
- binary logs/replication appliers;
- query plans/performance schema;
- DDL state;
- backup/binlog continuity.

### Redis signals

- memory fragmentation a eviction;
- command latency a slow log;
- clients/buffers;
- keyspace hit/miss/expiry;
- persistence forks/AOF rewrite;
- replication offsets/lag;
- hot keys/big keys;
- cluster slots/failover.

Cross-product dashboard s jednou metrikou `database CPU` je nedostatočný.

## 12. Product role matrix

| Requirement | PostgreSQL | MySQL | Redis |
|---|---|---|---|
| complex relational invariants | strong fit | strong fit s exact engine/config | weak/general mismatch |
| ad hoc SQL/joins | strong fit | strong fit | not primary model |
| key-based low-latency cache | possible, not specialized | possible, not specialized | strong fit |
| TTL/expiry-native ephemeral state | limited/general SQL mechanisms | limited/general SQL mechanisms | strong fit |
| durable multi-table transaction | strong fit | strong fit with InnoDB | different command/transaction model |
| WAL/binlog PITR | WAL-based | binary-log-based | AOF/RDB, not equivalent PITR semantics |
| rich data structures | via schema/extensions | via schema/features | native core strength |
| authoritative financial ledger | common fit with controls | common fit with controls | only with deliberately proven custom contract; usually poor default |

Matrix nie je benchmark ani automatic verdict. Exact workload a team capability rozhodujú.

## 13. Connected incident `DB-PAY-57`

Architecture používala:

```text
PostgreSQL ledger-service
  authority: settlement/outbox

MySQL merchant-policy-service
  authority: provider route + fee/risk policy generation

Redis idempotency-service
  intended role: 24 h dedupe acceleration
  actual use: gateway treated key existence as final operation authority
```

Po pooling/session-state failure začalo `214` operations vyžadovať policy verification. Redis failover počas incidentu stratil časť recent keys, pretože replication bola asynchronous a AOF používal `everysec` semantics. Gateway po missing key opakoval provider call bez PostgreSQL/provider read-backu.

Observed cohort:

```text
214 operations: policy verification required
31 operations: wrong routing-policy generation used
19 operations: provider result unknown after timeout
68 Redis dedupe keys absent after failover/restart window
7 duplicate provider attempts
0 confirmed duplicate settlements after provider idempotency reconciliation
```

Nula confirmed duplicate settlements bola výsledkom provider idempotency a reconciliation, nie dôkazom, že Redis authority design bol správny.

### Causal boundaries

- **Trigger:** pool/session failure a Redis failover počas response.
- **Product-role root cause:** rebuildable Redis dedupe state bolo použité ako authoritative proof, či provider operation môže byť zopakovaná.
- **Policy-consistency root cause:** settlement neukladal exact MySQL policy generation použitú pri decision-e.
- **Amplifiers:** independent clocks, asynchronous replication, cache-key TTL, retry bez PostgreSQL/provider evidence a product-generic monitoring.

## 14. Evidence-preserving containment

```text
freeze provider retries
→ preserve PostgreSQL transactions/outbox
→ preserve MySQL binlogs/policy generations
→ preserve Redis AOF/RDB/replication offsets/config
→ query provider idempotency ledger
→ classify operations by exact product evidence
→ stop treating cache absence as business absence
```

## 15. Authoritative redesign

Nové ownership:

```text
PostgreSQL:
  authoritative operation ID
  settlement + outbox atomic transaction
  exact policy generation used
  final/reconciliation state

MySQL:
  authoritative merchant policy generations
  immutable effective intervals/version IDs

Redis:
  derived cache and admission acceleration
  rebuildable keys
  no authority to decide duplicate external effect
```

Retry decision:

```text
Redis hit
→ fast duplicate suppression

Redis miss
→ PostgreSQL operation lookup
→ provider idempotency lookup if outcome unknown
→ only then create/retry bounded operation
```

Redis failure môže zvýšiť latency/load, ale nesmie zmeniť correctness.

## 16. Product-selection acceptance verdict

Product/role design je prijatý, keď:

- každý business fact má jedného authoritative ownera;
- product semantics zodpovedajú invariant/query/latency requirements;
- transaction a command boundaries sú explicitné;
- PostgreSQL/MySQL engine-specific assumptions sú current a testované;
- Redis TTL, eviction, persistence, replication a cluster semantics sú súčasť contractu;
- derived/cache absence sa nezamieňa s business absence;
- acknowledgement je mapované na durability/failover evidence;
- backup/PITR/rebuild path zodpovedá data role;
- cross-product event/version identity umožňuje reconciliation;
- operational signals sú product-specific aj business-level;
- wrong-product-role a stale/failed-store scenarios majú safe outcome;
- second operation, failover, restore a cache-loss tests prejdú.

## 17. Troubleshooting cross-product incidentu

```text
incorrect/stale/duplicate outcome
→ exact business operation
→ authoritative owner per fact
→ PostgreSQL transaction/WAL evidence
→ MySQL transaction/binlog/policy generation
→ Redis key/type/TTL/persistence/replication evidence
→ cache/derived vs authority classification
→ external provider evidence
→ retry/unknown outcome path
→ recovery/rebuild/reconciliation
→ product-role redesign
```

## 18. Anti-patterny

### PostgreSQL na všetko, lebo je powerful

Môže zbytočne niesť ephemeral/high-churn use cases, ale často je stále lepší než neodôvodnená polyglot zložitosť.

### MySQL je iba jednoduchší PostgreSQL

Ignoruje InnoDB, binary log, GTID, optimizer, SQL mode a product-specific operations.

### Redis je databáza, teda je source of truth

Data structure server môže byť durable, ale authority potrebuje explicitný persistence/replication/recovery contract.

### Redis je iba cache

Ignoruje streams, transactions, persistence a coordination use cases; rovnako nesprávne ako používať ho bez guarantees analýzy.

### Cache miss znamená operation neexistuje

Cache je incomplete/evictable/expiring derived evidence.

### Rovnaký key/value model = rovnaké semantics

Acknowledgement, durability, ordering, cluster a recovery sa líšia.

### Vyberieme podľa benchmarku

Benchmark bez current workload, data distribution, failure a recovery modelu je slabý dôkaz.

## 19. Kontrolné otázky

1. Ako sa PostgreSQL, MySQL a Redis kategorizujú?
2. Čo tvorí exact product-role subject?
3. Ktoré PostgreSQL mechanisms sú dôležité pre relational authority?
4. Prečo treba pri MySQL pomenovať storage engine a binlog semantics?
5. Ako Redis data structures menia data modeling?
6. Ako sa Redis transactions líšia od relational transactions?
7. Ako RDB, AOF a no-persistence menia Redis durability?
8. Prečo replication nie je rovnaká v troch produktoch?
9. Kedy je Redis dobrý dedupe accelerator, ale zlý final authority?
10. Ako exact policy generation pomáha v `DB-PAY-57`?
11. Aké evidence treba korelovať pri cross-product incidente?
12. Čo musí overiť product-selection acceptance verdict?

## Glossary impact

Relevantné pojmy: product-role subject, PostgreSQL authority role, InnoDB transaction role, Redis data-structure role, cache authority inversion, persistence mode, RDB snapshot, Append Only File, binary-log recovery, WAL recovery, product-specific acknowledgement, derived-key absence, policy generation identity, cross-product reconciliation a product-selection acceptance verdict.

## Primárne zdroje

- [PostgreSQL Documentation](https://www.postgresql.org/docs/current/)
- [MySQL 8.4 Reference Manual](https://dev.mysql.com/doc/refman/8.4/en/)
- [Redis Documentation — Data types](https://redis.io/docs/latest/develop/data-types/)
- [Redis Documentation — Transactions](https://redis.io/docs/latest/develop/using-commands/transactions/)
- [Redis Documentation — Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Redis Documentation — Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Connection pooling](connection-pooling.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Monolith, modular monolith a microservices →](monolith-modular-monolith-and-microservices.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
