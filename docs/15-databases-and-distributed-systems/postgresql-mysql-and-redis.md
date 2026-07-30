# PostgreSQL, MySQL a Redis

PostgreSQL, MySQL a Redis nie sú tri úrovne jednej databázovej maturity škály. PostgreSQL a MySQL sú relational database systems s transactions, constraints, SQL, logs a durable recovery mechanizmami. Redis je in-memory data-structure server s odlišným command, TTL, eviction, persistence, replication a failover contractom. Správny výber preto nezačína názvom produktu, ale presným business factom, jeho authority rolou a failure outcome-om, ktorý musí systém udržať.

```text
business fact a operation
→ authoritative / derived / ephemeral role
→ invariant, query a transaction boundary
→ durability, consistency a recovery objective
→ product-specific mechanism fit
→ schema/index alebo key/data-structure realization
→ acknowledgement a failure semantics
→ operational evidence a reconciliation
→ cache-loss, failover a restore validation
```

`Redis je rýchly`, `PostgreSQL je source of truth` alebo `MySQL je jednoduchší` nie sú architecture decisions. Každé tvrdenie musí byť naviazané na konkrétnu operation, data generation a acceptance contract.

## 1. Product-role subject a authority map

Exact product-role subject uvádza business capability a facts, ich authoritative alebo derived classification, transaction boundary, query a relationship requirements, latency a throughput objectives, volume a retention, acknowledgement a durability semantics, stale-read tolerance, partitioning, backup/PITR alebo rebuild path a operational ownership.

Atlas Payments používa produkty takto:

```text
PostgreSQL
  authority: settlement operation + outbox + reconciliation
  invariant: one merchant operation → at most one executable intent
  recovery: base backup + WAL PITR + provider reconciliation

MySQL
  authority: versioned merchant/provider policy
  invariant: one active policy generation per effective interval
  recovery: full backup + binlog/GTID replay

Redis
  role: bounded cache, admission counters, short-lived dedupe acceleration
  authority: none for final provider or settlement outcome
  recovery: rebuild from durable authority and events
```

Authority je property konkrétneho factu, nie produktu ako celku. PostgreSQL môže byť authoritative pre settlement a zároveň obsahovať rebuildable projection. Redis môže byť authoritative pre zámerne ephemeral rate-limit counter, ale nie automaticky pre irreversible payment decision. Jeden fact nesmie mať dvoch nezávislých writers len preto, že platforma používa polyglot persistence.

## 2. PostgreSQL mechanismus a vhodná rola

PostgreSQL realizuje relational state cez tables, keys, constraints, MVCC, locks, query planner, indexes a WAL. Dominantný write path je:

```text
client transaction
→ parse/rewrite/plan
→ MVCC snapshot + locks
→ heap/index mutations
→ constraints a triggers
→ WAL generation
→ commit/durability boundary
→ visibility
→ replication/archive/recovery
```

Je silný, keď correctness závisí od relational identity, uniqueness, referential integrity, predicate alebo multi-row transitions. Foreign keys, `CHECK`, unique a exclusion constraints, partial/expression indexes, rich SQL, JSONB a extensions umožňujú kombinovať invariant-heavy authority s rôznymi query patterns.

Táto sila však nevytvára správnosť automaticky. Dlhé transactions zadržiavajú old row versions a môžu zvyšovať vacuum, WAL a replication pressure. DDL a row locks môžu blokovať workload. Nesprávna transaction boundary rozdelí settlement a outbox aj v PostgreSQL. Stale statistics alebo skew môžu vytvoriť zlý plan. Product fit preto zahŕňa schema, transactions, maintenance a recovery, nie iba feature list.

## 3. MySQL/InnoDB mechanismus a vhodná rola

MySQL treba posudzovať cez konkrétny storage engine a server generation. Pri critical OLTP je typickým subjectom InnoDB, ktorý kombinuje MVCC, locks, buffer pool, undo/redo, constraints, crash recovery a coordination s binary logom.

```text
client transaction
→ optimizer/executor
→ InnoDB snapshot a locks
→ page/undo/redo mutations
→ constraints
→ commit + binary-log coordination
→ replication/PITR visibility
```

MySQL je silný relational owner pre veľké množstvo transactional use cases. InnoDB poskytuje durable transactions, row-level locking a recovery; binary log podporuje replication a PITR; GTID dáva operation identity pre topology a recovery; Group Replication alebo InnoDB Cluster môžu tvoriť HA mechanizmus.

Correctness však závisí od exact configuration. Storage engine, SQL modes, collation a case behavior, implicit conversions, DDL algorithm/lock, binlog format a filters, flush policy, replication mode a timestamp semantics môžu meniť outcome. PostgreSQL a MySQL sa preto nemajú porovnávať sloganom `correct vs fast`; obe platformy potrebujú explicitný invariant, transaction, acknowledgement a recovery contract.

## 4. Redis mechanismus a vhodná rola

Redis modeluje state cez keys a native data structures: strings, hashes, lists, sets, sorted sets, streams a ďalšie capabilities podľa distribution. Operation začína key identity a data-type command semantics, nie SQL query plannerom.

```text
client command
→ key/slot routing
→ in-memory data-structure operation
→ optional replication stream
→ optional AOF/RDB persistence
→ acknowledgement
→ failover/restart semantics
```

Redis je prirodzený fit pre bounded cache, TTL-native ephemeral state, counters, rate limiting, leaderboards, session acceleration, short-lived dedupe, streams alebo coordination, keď sú presne známe safety a liveness assumptions. Direct key access a atomic server-side operation môžu poskytovať veľmi nízku latency.

Redis však nie je automaticky nedurable ani automaticky durable. RDB vytvára snapshots, AOF zaznamenáva commands a ich combination mení restart a loss window. Replication je typicky asynchronous. `MULTI/EXEC` vykoná queued commands bez interleavingu, ale nerobí relational rollback; `WATCH` poskytuje optimistic conflict check. Eviction a expiry môžu byť intended lifecycle alebo correctness failure. Cluster slot topology ovplyvňuje multi-key atomicity. Acknowledgement preto musí byť mapované na persistence, replication a failover scenario.

## 5. Transactions, queries a modeling boundary

PostgreSQL a MySQL vedia chrániť multi-row a multi-table invariant v jednej local transaction:

```text
BEGIN
→ verify operation identity
→ insert settlement
→ insert outbox
→ record policy generation
→ COMMIT
```

Redis vie atomicky vykonať command alebo bounded command group, no nemá rovnaký relational constraint a rollback model. Otázka `podporuje produkt transactions?` je nedostatočná. Treba vedieť read/write set, conflicts, required rollback alebo compensation, durability po acknowledgement-e, cluster boundary a unknown-outcome retry semantics.

Relational schema je vhodná pre relationships, joins, set-based operations a declarative constraints. Redis schema začína keyom, slotom, data type-om, TTL, eviction a access patternom. Secondary access paths sa často realizujú ďalšími structures, ktoré treba aktualizovať atomicky alebo reconciliovať. Hot keys, large values, unbounded cardinality a O(N) commands môžu zmeniť low-latency design na latency incident.

JSON column v PostgreSQL/MySQL ani Redis hash neodstraňuje potrebu schema governance. Typ produktu nemení business fact na schemaless; iba presúva miesto, kde sa schema a invariant vynucujú.

## 6. Durability, replication a recovery podľa role

PostgreSQL acknowledgement závisí od WAL flush, storage a synchronous/asynchronous replication policy. MySQL acknowledgement závisí od InnoDB redo/flush, binary-log coordination, storage a replication policy. Redis acknowledgement závisí od persistence mode-u, fsync policy, replication a failover behavior. V každom produkte platí:

```text
write success
≠ write prežije každý failure
≠ replica obsahuje acknowledged position
≠ logical corruption je recoverable
≠ clients smerujú na správneho writera
```

Recovery sa musí prispôsobiť data role. PostgreSQL authority potrebuje base backup, WAL continuity, clean target a reconciliation. MySQL authority potrebuje full backup, binlog/GTID continuity a exact stop position. Redis cache možno flushnúť a rebuildnúť; Redis state použitý ako authority potrebuje explicitný RDB/AOF, replication, restore a data-loss contract. Replication nenahrádza historical recovery v žiadnom z produktov.

Operational evidence je tiež product-specific. PostgreSQL potrebuje transaction/lock/wait, backend, WAL/archive, vacuum a replication positions. MySQL potrebuje InnoDB transactions/locks, buffer pool, redo, binlog a applier state, Performance Schema a DDL evidence. Redis potrebuje memory/fragmentation, eviction/expiry, latency/slow log, clients/buffers, AOF/RDB, replication offsets, hot/big keys a cluster slots. Jedna cross-product `database CPU` metrika je slabý verdict.

## 7. Connected incident `DB-PAY-57`

Architecture používala PostgreSQL ako settlement/outbox authority, MySQL ako merchant-policy authority a Redis ako 24-hodinový dedupe accelerator. Effective gateway behavior však Redis key existence považoval za final proof, či provider operation existuje.

Po pooling/session-state failure-i vyžadovalo `214` operations policy verification a `31` použilo nesprávnu routing-policy generation. Počas incidentu Redis failover stratil časť recent keys, pretože replication bola asynchronous a AOF používal `everysec` semantics. Gateway interpretoval cache miss ako business absence a zopakoval provider call bez PostgreSQL alebo provider read-backu.

```text
214 operations: policy verification required
31 operations: wrong policy generation
19 operations: provider result unknown
68 Redis keys: absent po failover/restart window
7 provider attempts: duplicate
0 confirmed duplicate settlements po provider reconciliation
```

Nula confirmed duplicate settlements nebola dôkazom správneho Redis designu. Provider idempotency a reconciliation zabránili final duplicate effectu. Root cause bola product-role inversion: rebuildable state rozhodovalo o authoritative external action. Druhý problém bol, že settlement record neuchovával exact MySQL policy generation použitú pri decision-e.

## 8. Redesign a acceptance paths

Redesign uložil authoritative operation ID, settlement, outbox, exact policy generation a reconciliation state v PostgreSQL transaction boundary. MySQL zostal ownerom immutable/versioned policy generations. Redis sa vrátil k derived cache a admission role; jeho failure môže zvýšiť latency alebo database load, ale nesmie zmeniť correctness.

Retry path je:

```text
Redis hit
→ fast duplicate suppression

Redis miss
→ PostgreSQL operation lookup
→ provider idempotency lookup pri unknown outcome
→ až potom bounded create/retry decision
```

**Positive path** preukáže správnu PostgreSQL settlement transition, exact MySQL policy generation a Redis acceleration bez authority inversion.

**Recovery path** stratí Redis cache alebo vykoná failover; application rebuildne keys, zvýši controlled load na authority a zachová rovnaký business outcome.

**Failure path** pri unavailable MySQL policy authority alebo unknown provider result zastaví alebo prejde do explicitného pending/reconciliation state-u. Nesmie vybrať stale policy ani retryovať podľa cache missu.

**Forbidden path** odmietne dva authoritative writers, cache absence ako operation absence, eviction/TTL meniace final state, Redis failover spúšťajúci duplicate external effect a product-generic acknowledgement claim bez current configuration evidence.

Acceptance vyžaduje second operation, Redis loss, PostgreSQL/MySQL failover, restore a stale-policy test. Product sa prijíma pre konkrétnu rolu, nie ako všeobecne `správna databáza`.

## 9. Troubleshooting a anti-patterny

Pri stale, missing alebo duplicate outcome-e sa najprv určí exact business operation a authority per fact. Potom sa koreluje PostgreSQL transaction/WAL evidence, MySQL transaction/binlog/policy generation, Redis key/type/TTL/persistence/replication state a external provider ledger. Cache alebo projection evidence sa musí označiť ako derived; až potom možno rozhodovať o retry, rebuild alebo reconciliation.

Najčastejšie anti-patterny sú PostgreSQL na všetko bez workload analýzy, MySQL redukovaný na „jednoduchší PostgreSQL“, Redis automaticky označený za cache alebo naopak source of truth, cache miss interpretovaný ako business absence, benchmark bez failure/recovery modelu a rovnaký key/value interface považovaný za rovnakú durability semantics.

## 10. Kontrolné otázky

1. Čo tvorí exact product-role subject?
2. Pre ktoré facts je PostgreSQL v Atlas Payments authoritative?
3. Ktoré InnoDB a binary-log boundaries treba pri MySQL pomenovať?
4. Ako Redis command, TTL, eviction a persistence menia correctness?
5. Prečo `MULTI/EXEC` nie je rovnaký model ako relational transaction?
6. Ako sa product acknowledgement mapuje na durability a failover?
7. Prečo cache miss nesmie znamenať operation absence?
8. Ako exact policy generation podporuje reconciliation?
9. Prečo nula duplicate settlements nepotvrdila správnosť Redis authority designu?
10. Ktoré positive, recovery, failure a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: product-role subject, PostgreSQL authority role, InnoDB transaction role, Redis data-structure role, cache authority inversion, persistence mode, RDB snapshot, Append Only File, binary-log recovery, WAL recovery, product-specific acknowledgement, derived-key absence, policy generation identity, cross-product reconciliation a product-selection acceptance verdict.

## Primárne zdroje

- [PostgreSQL 18 Documentation](https://www.postgresql.org/docs/current/)
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
