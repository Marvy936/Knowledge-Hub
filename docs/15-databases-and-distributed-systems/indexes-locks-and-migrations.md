# Indexy, locks a migrácie

Index, lock a schema migration nie sú tri oddelené témy. Index mení access path a write cost. Access path ovplyvňuje, koľko rows a pages transaction navštívi a uzamkne. Migration mení schema, indexes, constraints alebo dáta počas concurrent production trafficu. Bez spoločného modelu môže správna DDL zmena vytvoriť lock queue, replication lag alebo neúplný rollout.

```text
business query alebo schema intent
→ exact table/index/migration subject
→ current data distribution a workload
→ query plan a access path
→ lock a version-retention footprint
→ migration generation a compatibility phases
→ bounded execution
→ effective schema/index/constraint state
→ application a replica convergence
→ business a rollback validation
```

## 1. Exact index/lock/migration subject

Subject má uvádzať:

- database, cluster, schema a table identity;
- engine/version a topology generation;
- row count, table/index size a growth;
- query predicates, joins, ordering a limit;
- current query plan a statistics generation;
- existing indexes a constraints;
- concurrent read/write workload;
- transaction duration a lock modes;
- migration artifact a phase;
- application versions, replicas a consumers;
- timeout, abort, rollback a recovery contract;
- allowed a forbidden business outcomes.

Príklad:

```text
table: settlement_attempt
rows: 780 million
change: add merchant_operation_id and enforce uniqueness
read pattern: merchant_id + merchant_operation_id
backfill cohort: merchant_operation_id IS NULL
traffic: 4 000 writes/s, 12 000 reads/s
topology: primary + async standby
application generations: 7.25 and 8.0 during rollout
```

## 2. Čo index robí

Index je samostatná data structure, ktorá mapuje indexed keys na row alebo tuple locations. Databáza môže namiesto full scan-u použiť index na obmedzenie candidate setu.

```text
query predicate/order
→ planner estimates
→ candidate access paths
→ index scan alebo table scan
→ row visibility a filters
→ result
```

Index nie je automaticky použitý. Planner môže zvoliť scan, ak:

- query vracia veľkú časť table;
- statistics odhadujú nízku selectivity;
- predicate nezodpovedá index expression/order;
- type cast alebo function bráni použitiu;
- table je malá;
- index je invalid alebo unavailable;
- random I/O cost prevyšuje sequential scan;
- ordering/join strategy preferuje iný plan.

## 3. B-tree a ďalšie index families

### B-tree

Bežný default pre equality, range, ordering a prefix multicolumn patterns.

```text
ordered key space
→ tree traversal
→ leaf range
→ row references
```

### Hash

Optimalizovaný najmä pre equality operations. Product-specific durability, concurrency a operator support treba overiť.

### Inverted index

Mapuje terms alebo contained values na documents/rows. Používa sa pre full-text, arrays alebo document fields podľa engine-u.

### Spatial alebo generalized indexes

Podporujú geometry, ranges, nearest-neighbor alebo custom operator classes.

### BRIN alebo block-range summary

Malý summary index môže byť vhodný pre veľmi veľké physically correlated tables. Nie je náhradou selective B-tree pre arbitrary lookup.

Index type sa vyberá podľa operators, data distribution a query pathu, nie podľa názvu column type-u.

## 4. Multicolumn index

Poradie columns určuje, ktoré predicates a ordering možno efektívne využiť.

Príklad:

```sql
CREATE INDEX idx_settlement_merchant_created
ON settlement (merchant_id, created_at DESC);
```

Pri query:

```sql
WHERE merchant_id = $1
ORDER BY created_at DESC
LIMIT 50
```

môže index podporiť filter aj order. Rovnaký index nemusí byť ideálny pre global query iba podľa `created_at`.

Hodnotiť treba:

- equality predicates;
- range predicate;
- ordering;
- selectivity;
- prefix usage;
- included/covering columns;
- write amplification;
- duplicate/redundant indexes.

## 5. Unique index a constraint

Unique index môže byť physical enforcement mechanizmus uniqueness invariant-u. Application-level `SELECT then INSERT` nie je bezpečný pri concurrency:

```text
T1 SELECT: not found
T2 SELECT: not found
T1 INSERT
T2 INSERT
```

Unique constraint rozhodne konflikt autoritatívne. Application musí spracovať success, conflict a unknown outcome podľa business keyu.

Partial unique index môže enforce-nuť invariant iba pre konkrétny state cohort, napríklad jeden active operation. Predicate musí presne zodpovedať business semantics a migration phases.

## 6. Index cost

Index urýchľuje niektoré reads, ale pridáva:

- storage;
- memory/cache pressure;
- write amplification;
- WAL/redo volume;
- vacuum/maintenance work;
- build/rebuild time;
- replication traffic;
- schema-change complexity.

Každý `INSERT`, `UPDATE` indexed column alebo `DELETE` môže meniť viac index structures. Nadbytočný index môže znížiť write throughput a predĺžiť recovery bez relevantného read benefitu.

## 7. Statistics a plan generation

Planner rozhoduje z estimates. Stale alebo nepresné statistics môžu viesť k zlému join orderu alebo scan choice.

```text
current data distribution
→ collected statistics
→ cardinality/selectivity estimate
→ cost model
→ chosen plan
→ actual rows/time/buffers
→ estimate-vs-actual verdict
```

Diagnostika porovnáva estimated a actual rows, nie iba total duration. Parameter values, data skew, prepared-plan behavior a correlation môžu spôsobiť rozdiel medzi cohorts.

## 8. Locks

Lock chráni concurrent access k row, table, index alebo schema metadata. Lock mode a compatibility určujú, kto môže pokračovať.

Dôležité rozlíšenia:

- granted vs. waiting lock;
- row-level vs. table/schema lock;
- lock holder vs. root blocker;
- wait duration vs. transaction age;
- blocking chain vs. deadlock cycle;
- application lock vs. database lock;
- advisory lock vs. enforced data lock.

Transaction zvyčajne drží acquired locks do commit/rollback-u. Krátky statement v dlhej transaction preto môže blokovať dlho po dokončení samotného SQL.

## 9. Lock amplification cez access path

Query bez suitable indexu môže navštíviť veľa rows, aj keď zmení malý batch.

```sql
UPDATE settlement_attempt
SET merchant_operation_id = legacy_operation_id
WHERE merchant_operation_id IS NULL
  AND created_at < $cutoff
LIMIT ...
```

SQL dialect a batching pattern sa líšia, ale mechanizmus zostáva:

```text
weak predicate access path
→ large scan
→ many visited/locked rows alebo pages
→ longer transaction
→ concurrent waiters
→ queueing a timeout retries
→ more load
```

Supporting partial index môže zmenšiť candidate scan:

```sql
CREATE INDEX ...
ON settlement_attempt (created_at, id)
WHERE merchant_operation_id IS NULL;
```

Index však treba vytvoriť bezpečne a overiť jeho effective použitie.

## 10. DDL locks

Schema changes môžu vyžadovať metadata alebo table locks. Exact behavior závisí od engine-u, statementu, table size, default value, validation a online/concurrent option.

Pred production DDL treba poznať:

- required lock mode;
- či lock acquisition čaká za starými transactions;
- či statement blokuje reads alebo writes;
- či rewrituje table;
- WAL/redo a replication impact;
- rollback behavior;
- cancellation safety;
- partial/invalid artifact state;
- compatibility s old/new application generation.

Krátka DDL operácia môže čakať dlho na lock a po získaní blokovať celý queue.

## 11. Concurrent/online index build

PostgreSQL `CREATE INDEX CONCURRENTLY` umožňuje build bez blokovania bežných writes, ale vykonáva viac práce, čaká na relevantné transactions a má caveats. Nemôže bežať v bežnom transaction blocku a po failure môže zostať invalid index, ktorý treba explicitne diagnostikovať.

`CONCURRENTLY` preto nie je synonymum pre:

- instant;
- zero load;
- zero lock;
- automatic retry;
- valid index po každom failure-i;
- vhodné execution počas ľubovoľného peak-u.

Acceptance vyžaduje catalog state, validity, planner use a production metrics.

## 12. Schema migration ako compatibility protocol

Bezpečná migration nie je jeden DDL statement. Je to protocol medzi database a viacerými application generations.

### Expand

- pridať backward-compatible schema;
- vytvoriť nové nullable columns/tables/indexes;
- nasadiť tolerant readers;
- začať bounded dual-read/dual-write iba s explicitným ownerom.

### Backfill

- stable ordering a cursor;
- bounded batch size;
- resumability;
- current-row/version predicate;
- replication/lock/WAL guardrails;
- correctness a progress evidence.

### Switch

- shadow compare alebo read switch;
- current application generations používajú nový model;
- constraint validation;
- reconciliation.

### Contract

- odstrániť old writers/readers;
- enforce-nuť final constraints;
- dropnúť obsolete columns/indexes;
- retire migration code a compatibility path.

```text
expand
→ tolerant deployment
→ bounded backfill
→ reconcile
→ read/write switch
→ constraint proof
→ contract
→ old-generation retirement
```

## 13. Backfill correctness

Backfill musí rozlíšiť historical missing state od rows, ktoré live writer práve zmenil.

Nebezpečný model:

```text
read old row
→ compute transformed value
→ live writer updates newer state
→ backfill writes stale computed value
```

Bezpečnejšie mechanizmy:

- conditional update na old version/state;
- immutable source fields;
- change capture a catch-up;
- per-row version;
- stable cursor;
- idempotent transformation;
- conflict/retry cohort;
- final full reconciliation.

## 14. Constraint validation

Veľká table môže dostať constraint v phases, ak engine podporuje oddelenie definition a validation. Cieľom je:

1. zabrániť novým invalid writes;
2. backfillnúť historical rows;
3. overiť complete cohort;
4. validovať authoritative constraint;
5. odstrániť application-only guard.

`Backfill completed` metric nestačí. Potrebný je zero-invalid-row query, constraint catalog state a forbidden-write test.

## 15. Migration observability

Sleduj:

- rows remaining a verified rate;
- batch latency a errors;
- lock waits a blocker age;
- active/idle-in-transaction sessions;
- query-plan changes;
- buffer/cache pressure;
- WAL/redo generation;
- replication lag;
- vacuum/garbage-collection lag;
- application latency/error rate;
- constraint/index validity;
- data reconciliation differences.

Progress bez reliability guardrails môže iba rýchlejšie poškodzovať production.

## 16. Worked incident `DB-PAY-56`

Migration pridávala `merchant_operation_id` do `settlement_attempt` s približne `780 miliónmi` rows.

Execution plan:

```text
1. add nullable column
2. deploy application 8.0
3. backfill 25 000 rows per transaction
4. build unique index
5. mark column NOT NULL
```

Skutočný backfill vyberal rows podľa:

```text
merchant_operation_id IS NULL
ORDER BY created_at
```

Supporting partial index neexistoval. Každý batch preto opakovane scanoval veľkú časť table. Batch transactions trvali 4 až 11 minút a držali row locks aj old snapshots.

Dôsledky:

- OLTP lock waits vzrástli z milisekúnd na desiatky sekúnd;
- connection pool sa naplnil waiters;
- timeout retries zvýšili write load;
- WAL generation vzrástla 6.4×;
- async standby lag dosiahol 94 sekúnd;
- autovacuum nemohlo efektívne retire-nuť old versions;
- application p95 prekročilo 8 sekúnd.

Operator následne spustil štandardný `CREATE UNIQUE INDEX` namiesto approved concurrent variantu. Statement čakal za long transaction a po získaní locku zablokoval writers. Bol cancelnutý, ale incident už mal veľký request queue a replication backlog.

Neskôr `CREATE UNIQUE INDEX CONCURRENTLY` zlyhal na historical duplicates a zanechal invalid index artifact. Deployment automation kontrolovala iba existenciu index name-u, nie validity a uniqueness acceptance.

### Root causes

- migration nebola modelovaná podľa current table scale a workloadu;
- backfill nemal supporting access path a bounded transaction duration;
- DDL lock mode nebol súčasťou execution gate-u;
- index acceptance kontrolovala existence, nie valid/effective state;
- duplicate cleanup a uniqueness proof nepredchádzali constraint activation.

## 17. Competing hypotheses a discriminating evidence

Pri migration latency treba odlíšiť:

1. CPU alebo storage saturation;
2. query-plan regression;
3. lock queue;
4. connection pool starvation;
5. replication slot/WAL retention;
6. vacuum/version pressure;
7. index build load;
8. DDL waiting/holding lock;
9. application retry amplification.

Evidence chain:

```text
migration generation a batch ID
→ active transactions a age
→ lock graph/root blocker
→ EXPLAIN estimated vs actual plan
→ table/index statistics a validity
→ WAL/replication positions
→ vacuum/version-retention state
→ pool waiters/timeouts/retries
→ application business SLI
```

## 18. Evidence-preserving containment

```text
pause new migration batches
→ cancel iba identifikovaný safe statement, nie náhodné sessions
→ zachovať plans, locks, catalog a replication evidence
→ stop retry amplification
→ znížiť batch concurrency
→ chrániť OLTP admission
→ inventory partial/invalid index a backfill state
→ overiť exact last committed cursor
```

Killing root blocker bez pochopenia transaction outcome môže vytvoriť rollback storm alebo unknown batch state.

## 19. Authoritative remediation

1. vytvoriť supporting partial index bezpečným online/concurrent postupom;
2. overiť index validity a planner use;
3. zmeniť backfill na stable keyset cursor a menšie transactions;
4. používať conditional idempotent updates;
5. zaviesť lock, WAL, lag a OLTP latency abort criteria;
6. inventory a odstrániť historical duplicates cez exact manifest;
7. buildnúť unique index a overiť uniqueness;
8. attachnúť/enforce-nuť constraint podľa engine-safe protocolu;
9. overiť old/new application compatibility;
10. vykonať second batch, failover a rollback/restart test.

## 20. Index/lock/migration acceptance verdict

Zmena je prijatá, keď:

- exact query/schema subject a data scale sú známe;
- intended index zodpovedá predicates, ordering a distribution;
- estimate-vs-actual plan je overený;
- read benefit prevyšuje write/storage/maintenance cost;
- lock modes a blocker behavior sú rehearsed;
- transactions a batches majú bounded duration;
- migration používa expand/backfill/switch/contract protocol;
- old/new application generations sú kompatibilné;
- backfill je idempotentný, resumable a conflict-safe;
- index/constraint sú validné a effective, nie iba present;
- replication, vacuum a capacity guardrails prešli;
- rollback/restart a second-batch test prešli;
- forbidden duplicate, stale overwrite a broad-lock outcomes zlyhajú.

## 21. Troubleshooting flow

```text
query alebo migration degradation
→ exact query/schema/index generation
→ current plan a statistics
→ estimated vs actual rows
→ index eligibility/validity
→ transaction age a lock graph
→ batch cursor a affected manifest
→ WAL/replication/vacuum pressure
→ application retry a business impact
→ bounded pause/cancel/remediation
→ plan, constraint a second-batch verification
```

## 22. Anti-patterny

### Index na každý filter

Zvyšuje write a maintenance cost a môže byť redundantný.

### Index existuje, teda sa používa

Môže byť invalid, unsuitable alebo planner zvolí iný path.

### Online DDL znamená bez rizika

Stále používa resources, waits a metadata locks.

### Backfill jedným UPDATE

Unbounded transaction zvyšuje locks, WAL, rollback a replication risk.

### Batch progress = correctness

Rows môžu byť stale-overwritten, skipped alebo double-processed.

### DDL v peak-u, lebo statement je krátky

Lock acquisition a table rewrite behavior sú dôležitejšie než text statementu.

### Killni blocker

Bez outcome a rollback modelu môže situáciu zhoršiť.

## 23. Kontrolné otázky

1. Čo tvorí exact index/lock/migration subject?
2. Prečo planner nemusí index použiť?
3. Ako sa B-tree a inverted index líšia?
4. Prečo záleží na poradí multicolumn indexu?
5. Ako unique constraint rieši concurrency race?
6. Aký je write cost indexu?
7. Ako access path ovplyvňuje lock footprint?
8. Čo treba vedieť pred DDL v production?
9. Aké caveats má concurrent index build?
10. Ako expand/backfill/switch/contract funguje?
11. Prečo backfill poškodil `DB-PAY-56`?
12. Čo overuje index/lock/migration acceptance verdict?

## Glossary impact

Relevantné pojmy: index subject, access path, query selectivity, multicolumn index, partial index, covering index, write amplification, plan generation, estimate-vs-actual verdict, lock graph, root blocker, DDL lock, migration generation, expand–backfill–switch–contract, stable cursor, stale backfill overwrite, constraint validation a index/lock/migration acceptance verdict.

## Primárne zdroje

- [PostgreSQL Documentation — Index Types](https://www.postgresql.org/docs/current/indexes-types.html)
- [PostgreSQL Documentation — Multicolumn Indexes](https://www.postgresql.org/docs/current/indexes-multicolumn.html)
- [PostgreSQL Documentation — CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html)
- [PostgreSQL Documentation — Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Transactions a ACID](transactions-and-acid.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Replikácia a high availability →](replication-and-high-availability.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
