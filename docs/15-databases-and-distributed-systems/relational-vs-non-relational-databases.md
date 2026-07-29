# Relational vs. non-relational databases

Voľba databázy nie je súťaž medzi `SQL` a `NoSQL`. Je to rozhodnutie, kde budú uložené authoritative business facts, aké invarianty musí systém chrániť, aké query a access patterns potrebuje, ako bude meniť schema a ako sa bude správať pri concurrency, partition, failover-e a recovery.

```text
business capability a authoritative facts
→ exact data subject a invarianty
→ entity/aggregate/relationship boundaries
→ read a write access patterns
→ transaction a consistency requirements
→ scale, locality a failure model
→ relational alebo non-relational fit
→ physical model a indexes
→ effective runtime behavior
→ migration, recovery a second-operation validation
```

Databázový model je súčasť business correctness contractu. Nesprávne umiestnená autorita môže vytvoriť dual writes, nejasnú transaction boundary a data reconciliation, aj keď všetky jednotlivé databázy technicky fungujú.

## 1. Exact database-selection subject

Tvrdenie `potrebujeme NoSQL kvôli škálovaniu` je nedostatočné. Selection subject má uvádzať:

- business capability a critical user journeys;
- authoritative facts a ich ownera;
- invarianty, ktoré nesmú byť porušené;
- entity, aggregate a relationship boundaries;
- dominantné read/write patterns;
- expected volume, throughput, latency a growth;
- hot-key, tenant a locality distribution;
- transaction scope;
- požadovanú consistency a staleness tolerance;
- availability, durability, RPO a RTO;
- schema-evolution a migration model;
- operational skill, tooling a support constraints.

Príklad:

```text
capability: merchant settlement execution
authoritative facts: settlement intent, provider operation, final state
invarianty:
  one merchant operation maps to at most one settlement
  acknowledged intent is never lost
  provider submission is not duplicated
read patterns:
  lookup by merchant + operation ID
  list recent settlements by merchant
write pattern:
  create intent + durable outbox event
transaction scope:
  settlement row + outbox row
consistency:
  current authoritative write state
projection tolerance:
  merchant dashboard may lag 5 seconds
```

Tento subject prirodzene oddeľuje invariant-heavy write model od denormalizovanej read projection.

## 2. Relational model

Relational database reprezentuje dáta cez relations, rows, columns, keys a constraints. Jej hlavná sila nie je iba SQL syntax, ale schopnosť explicitne modelovať:

- identity cez primary a candidate keys;
- referential integrity cez foreign keys;
- uniqueness a domain constraints;
- multi-row transactions;
- joins a ad hoc relational queries;
- declarative query optimization;
- schema a constraint evolution.

Príklad logického modelu:

```text
merchant
  1 ─── N settlement

settlement
  1 ─── N settlement_attempt
  1 ─── 1 outbox_event pre create transition
```

Relational model je silný, keď business correctness závisí od vzťahov alebo invariantov naprieč viacerými records. Normalizácia pomáha odstrániť nežiaduce duplicity authoritative facts, ale nie je absolútny cieľ. Read-optimized tables, materialized views alebo projections môžu byť zámerne denormalizované.

## 3. Non-relational model nie je jedna kategória

`NoSQL` zahŕňa viac odlišných modelov.

### Key-value

```text
key → opaque alebo semi-structured value
```

Vhodné pre cache, sessions, counters, leases a jednoduchý state lookup. Critical otázky sú key design, atomic operations, TTL, eviction, persistence a hot-key distribution.

### Document

```text
aggregate identity → nested document
```

Vhodné, keď sa súvisiace dáta typicky čítajú a menia ako jeden aggregate. Embedded model môže znížiť joins a network round trips. Ak sa jeden invariant často rozprestiera cez viac documents, aplikácia potrebuje multi-document transaction, redesign aggregate boundary alebo explicitnú eventual-consistency workflow.

### Wide-column

```text
partition key + clustering order → sparse ordered rows
```

Vhodné pre vysoký distributed throughput a query-first modelovanie. Partition key rozhoduje o locality, balancing a hot partitions. Ad hoc joins a globálne invarianty bývajú obmedzenejšie alebo drahšie.

### Graph

```text
vertices + edges + properties
```

Vhodné pre relationship traversal, path finding, dependency alebo fraud graphy. Nie každý connected dataset potrebuje graph database; rozhodujú dominantné traversal patterns a ich hĺbka.

### Search a analytical engines

Inverted-index alebo columnar analytical systémy sú optimalizované pre full-text, aggregation a scan workloads. Často sú odvodeným evidence alebo query store-om, nie authoritative transactional ledgerom.

## 4. Aggregate a invariant boundary

Najdôležitejšia modelovacia otázka je:

> Ktoré facts musia prejsť z jedného validného state-u do druhého atomicky?

Príklad settlement transition:

```text
merchant operation does not exist
→ settlement intent created
→ outbox event created
→ acknowledgement returned
```

Ak `settlement` a `outbox` patria do jednej correctness boundary, model má podporiť jednu atomic transition alebo iný mechanizmus s ekvivalentným dôkazom. Uložiť ich do dvoch nezávislých databases a označiť oba writes za `eventually consistent` nemení business invariant na eventual invariant.

Eventual consistency je vhodná pre odvodené views, search indexes, recommendations alebo analytics, ak:

- authority je explicitná;
- propagation má identity a checkpoint;
- stale semantics sú prijateľné;
- missing/duplicate/reordered updates sú riešené;
- reconciliation existuje;
- user outcome nerozbije invariant.

## 5. Normalization a denormalization

Normalization znižuje update anomalies tým, že authoritative fact má jedno logické miesto. Denormalization kopíruje alebo predpočíta facts pre konkrétny access pattern.

```text
authoritative normalized write model
→ committed change/event
→ asynchronous projection
→ denormalized read model
→ freshness a correctness verification
```

Denormalization potrebuje:

- source-of-truth identity;
- projection generation;
- ordering a idempotency semantics;
- backfill/rebuild path;
- lag a completeness SLI;
- user-visible stale behavior;
- reconciliation.

Ak dve stores možno nezávisle editovať a obe sa nazývajú source of truth, vzniká dual authority, nie polyglot persistence.

## 6. Query-first a invariant-first návrh

Model sa má hodnotiť z oboch smerov.

### Query-first

- ktoré exact queries dominujú;
- ktoré predicates, ordering a pagination sa používajú;
- koľko rows/documents/partitions sa dotkne jedna operation;
- aký je fan-out;
- aká latency a freshness sú potrebné.

### Invariant-first

- ktoré writes musia byť atomic;
- ktoré uniqueness a relationship constraints sú required;
- aké concurrent transitions sú možné;
- kto rozhoduje o final state;
- čo musí prežiť crash a failover;
- ako sa unknown outcome reconciliuje.

Optimalizovať iba query bez write invariants môže vytvoriť rýchly, ale nesprávny systém. Optimalizovať iba normálnu formu bez access patterns môže vytvoriť korektný, ale neprevádzkovateľný systém.

## 7. Consistency a transaction semantics

Relational databáza automaticky neznamená serializovateľné správanie a non-relational databáza automaticky neznamená absenciu transactions. Treba overiť konkrétny product, topology a operation contract:

- atomicity jednej row alebo document operation;
- multi-record alebo multi-document transactions;
- isolation level;
- read a write concern;
- leader/follower alebo quorum semantics;
- replica staleness;
- conflict resolution;
- retry a unknown-commit behavior.

MongoDB napríklad poskytuje atomic single-document operations a podporuje multi-document transactions v replica setoch a sharded clusters; dokumentový model však stále odporúča navrhnúť aggregate boundaries tak, aby zbytočné distributed transactions neboli default. PostgreSQL poskytuje multi-row transactions, constraints a viac isolation úrovní, no aplikácia stále musí správne určiť transaction boundary a retry semantics.

## 8. Scale a partitioning

`Horizontálne škáluje` nie je úplný verdict. Distribution vyžaduje:

```text
logical data subject
→ partition/shard key
→ placement a replication
→ request routing
→ single-partition alebo cross-partition operation
→ rebalance/failure behavior
→ consistency a recovery
```

Dôležité otázky:

- je traffic rovnomerne rozdelený;
- existujú hot tenants alebo hot keys;
- vyžadujú queries scatter-gather;
- prechádzajú transactions cez partitions;
- ako sa mení shard key;
- čo sa stane pri rebalancing-u;
- ako sa obnovuje partial alebo corrupted shard;
- kto vlastní global uniqueness.

Jeden veľký správne navrhnutý relational cluster môže byť jednoduchší a spoľahlivejší než predčasne sharded systém. Naopak, workload s prirodzene partition-local operations môže profitovať z distributed non-relational modelu.

## 9. Polyglot persistence

Polyglot persistence je legitímna, keď každá store má explicitnú rolu:

| Store | Authority | Typický účel |
|---|---|---|
| relational OLTP | authoritative transactions a invariants | settlement ledger |
| document projection | odvodený aggregate view | merchant detail screen |
| key-value | disposable alebo reconstructable runtime state | cache, session, limiter |
| search engine | odvodený search index | full-text a filtering |
| analytical warehouse | odvodené historical facts | reporting a forecasting |

Každý odvodený store potrebuje lineage, freshness, rebuild a retirement contract. `Máme microservices, preto každá service potrebuje inú databázu` nie je technické odôvodnenie.

## 10. Worked incident `DB-PAY-56`

Atlas Payments pripravoval release `payments 8.0`. Tím chcel zjednodušiť merchant reads a postupne presunúť settlement state z PostgreSQL do document store-u.

Nový write path:

```text
merchant request
→ insert PostgreSQL settlement_intent
→ COMMIT autocommit statement
→ upsert document settlement aggregate
→ insert PostgreSQL outbox_event
→ HTTP 202
```

Document obsahoval settlement status, merchant metadata, provider attempt a dashboard fields. PostgreSQL stále obsahovala provider ledger references a outbox. Oba stores boli v návrhu označené ako authoritative pre časť rovnakého settlement lifecycle-u.

Počas migration backfill-u sa zvýšila database latency a o `10:14 UTC` nastal AZ network failure. Application process po prvom PostgreSQL commite stratil connection. Retry vytvoril document aggregate, ale outbox insert neprebehol. Niektoré requests preto mali:

```text
PostgreSQL settlement_intent: exists
document aggregate: exists alebo retried
PostgreSQL outbox_event: missing
provider operation: absent
HTTP outcome: unknown alebo 202 z retried pathu
```

O `10:19 UTC` bol promoted async standby, ktorý navyše nemal poslednú časť WAL. Read API začalo preferovať document store a zobrazovalo časť settlements ako `accepted`, hoci neexistoval executable outbox intent.

### Trigger, root cause a amplifiers

- **Trigger:** AZ network failure počas migration loadu.
- **Primary design root cause:** jeden settlement invariant bol rozdelený medzi dve independently committed authoritative stores.
- **Transaction root cause:** settlement a outbox nevznikali v jednej atomic database transaction.
- **Migration amplifier:** unindexed backfill a dlhé transactions zvýšili lock waits a replication lag.
- **HA amplifier:** async promotion bez acknowledgement/RPO contractu a bez complete writer fencing.
- **Read-model amplifier:** document projection bola použitá ako authority bez lineage/freshness verdictu.

Výber document database sám osebe nebol chyba. Chyba bola použiť read-friendly document aggregate ako druhú authority pre invariant, ktorý sa stále realizoval cez relational ledger a outbox.

## 11. Competing hypotheses a discriminating evidence

Pri symptóme `accepted settlement sa nevykonal` treba odlíšiť:

1. request nevstúpil do systému;
2. PostgreSQL intent necommitol;
3. commitol, ale response sa stratila;
4. document projection chýba alebo je stale;
5. outbox event nevznikol;
6. outbox existuje, ale nebol publishnutý;
7. standby promotion stratila acknowledged write;
8. provider prijal operation, ale callback chýba;
9. query číta nesprávny store alebo replica generation.

Evidence chain:

```text
merchant operation ID
→ API request/attempt IDs
→ PostgreSQL transaction/WAL/LSN evidence
→ settlement a outbox rows
→ document version/change-stream checkpoint
→ broker message/offset
→ provider idempotency ledger
→ failover timeline a promoted LSN
→ read-route a projection generation
```

## 12. Evidence-preserving containment

```text
zastaviť rollout a schema/backfill changes
→ zachovať primary/standby WAL, transaction a failover evidence
→ fence old a new writers
→ zastaviť automatic replay bez classification
→ inventory settlement/outbox/document/provider cohorts
→ označiť document projection non-authoritative
→ obmedziť new admission alebo prejsť na durable degraded mode
→ vytvoriť reconciliation manifest
```

Broad delete, blind replay alebo prepis projection state-u môže odstrániť dôkaz a vytvoriť duplicate provider operations.

## 13. Authoritative recovery

1. obnoviť PostgreSQL ako jedinú authority pre settlement transition;
2. klasifikovať operations na `never-committed`, `intent-only`, `outbox-ready`, `sent-unknown` a `completed`;
3. doplniť missing outbox events iba pre exact `intent-only` manifest;
4. overiť provider ledger pred každým replayom;
5. rebuildnúť document projection z authoritative committed streamu;
6. zaviesť atomic `settlement + outbox` transaction;
7. definovať acknowledged-write replication contract;
8. opraviť migration a index strategy;
9. vykonať failover a second-operation test;
10. odstrániť dual-authority write path.

## 14. Database-model acceptance verdict

Model je prijatý, keď:

- authoritative facts a owners sú explicitné;
- entity, aggregate a relationship boundaries zodpovedajú invariants;
- critical transition má enforceable transaction/consistency contract;
- read a write patterns majú podporovaný access path;
- partition/shard key a hot-key risk sú vyhodnotené;
- denormalized copies majú lineage, lag a rebuild path;
- žiadne dva stores nie sú nevedome dual authority;
- retries, unknown outcomes a reconciliation sú definované;
- HA, backup a recovery chránia business facts, nie iba bytes;
- migration prejde current-scale load a failure testom;
- allowed, forbidden a second-operation outcomes prejdú.

## 15. Troubleshooting flow

```text
data inconsistency alebo missing business outcome
→ exact operation, entity/aggregate a authority
→ expected invariant a transaction boundary
→ current write/read routes
→ committed state v každom store
→ projection lineage a checkpoint
→ concurrency/retry/failover timeline
→ replication a migration generation
→ competing data-model hypotheses
→ bounded reconciliation
→ original a forbidden business validation
```

## 16. Anti-patterny

### SQL vs. NoSQL podľa popularity

Ignoruje invarianty, access patterns a operations.

### Schema-less znamená bez schema governance

Schema sa iba presunie do producers, consumers, indexes a validation code-u.

### Jeden aggregate document obsahuje všetko

Veľké contention, write amplification a unbounded growth môžu zničiť výhodu document locality.

### Každá microservice musí mať inú technológiu

Zvyšuje operational a recovery surface bez preukázaného benefitu.

### Eventual consistency opraví dual write

Bez authority, durable eventu, idempotency a reconciliation iba pomenúva divergence.

### Read replica alebo cache je source of truth

Odvodený a stale state sa nesmie použiť na authoritative transition bez explicitného contractu.

## 17. Kontrolné otázky

1. Čo tvorí exact database-selection subject?
2. Kedy je relational model prirodzený pre invarianty?
3. Ako sa key-value, document, wide-column a graph modely líšia?
4. Čo je aggregate boundary?
5. Ako normalization a denormalization súvisia s authority?
6. Kedy je eventual consistency prijateľná?
7. Prečo NoSQL neznamená absenciu transactions?
8. Čo musí obsahovať shard-key verdict?
9. Ako sa polyglot persistence líši od dual authority?
10. Prečo document store nebol sám osebe root cause `DB-PAY-56`?
11. Aký evidence chain odlíši projection lag od strateného authoritative intentu?
12. Čo musí overiť database-model acceptance verdict?

## Glossary impact

Relevantné pojmy: database-selection subject, authoritative fact, relational model, non-relational model, aggregate boundary, invariant boundary, normalization, denormalization, derived data store, dual authority, polyglot persistence, shard key, hot partition, query-first model, invariant-first model a database-model acceptance verdict.

## Primárne zdroje

- [PostgreSQL Documentation — SQL Language](https://www.postgresql.org/docs/current/sql.html)
- [PostgreSQL Documentation — Transactions](https://www.postgresql.org/docs/current/transactions.html)
- [MongoDB Manual — Data Modeling](https://www.mongodb.com/docs/manual/data-modeling/)
- [MongoDB Manual — Transactions](https://www.mongodb.com/docs/manual/core/transactions/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[↑ Obsah sekcie](README.md)
<!-- KNOWLEDGE-NAVIGATION:END -->