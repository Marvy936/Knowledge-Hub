# Indexy, locks a migrations

Index, lock a schema migration nie sú tri oddelené prevádzkové témy. Index určuje access path a cenu čítania aj zápisu. Access path ovplyvňuje počet navštívených rows, pages a lockov. Migration mení schema, constraints, indexy alebo samotné dáta počas concurrent production trafficu. Bez spoločného modelu môže korektný DDL statement vytvoriť lock queue, retry amplification, WAL pressure, replication lag alebo nekompatibilitu medzi application generations.

```text
business query alebo schema-change intent
→ exact table/index/migration subject
→ current data distribution a workload
→ planner a effective access path
→ transaction a lock footprint
→ compatibility protocol medzi application generations
→ bounded backfill alebo DDL execution
→ catalog, planner, replica a runtime convergence
→ business validation a old-path retirement
→ second-batch, rollback a failover test
```

Kapitola preto neposudzuje index podľa toho, či v catalogu existuje, ani migration podľa toho, či command skončil s exit code `0`. Autoritatívny verdict vzniká až vtedy, keď je intended access path skutočne použitý, constraint chráni business invariant, mixed-version traffic zostáva kompatibilný a rollout prejde aj pri restart-e, lag-u a opakovanom batchi.

## 1. Exact subject a authority

Tvrdenie `pridáme index na merchant_operation_id` nehovorí, na aký workload, scale a invariant sa zmena viaže. Exact subject musí pomenovať database cluster a engine generation, schema a table identity, počet rows a distribúciu dát, dominantné queries, current plans a statistics, existujúce indexes a constraints, write rate, transaction duration, replica topology, migration artifact, application generations a failure contract.

Pre `DB-PAY-56` bol subject:

```text
table: settlement_attempt
rows: približne 780 miliónov
change: doplniť merchant_operation_id a enforce-nuť uniqueness
read key: merchant_id + merchant_operation_id
historical cohort: merchant_operation_id IS NULL
traffic: približne 4 000 writes/s a 12 000 reads/s
migration generations: application 7.25 + 8.0
replication: primary + asynchronous standby
business invariant: jedna merchant operation nesmie vytvoriť viac settlementov
```

Autoritou pre uniqueness nie je migration dashboard ani application-level `SELECT then INSERT`. Autoritou je validný database constraint alebo iný concurrency-safe mechanizmus nad presne definovaným cohortom. Autoritou pre dokončenie backfillu nie je počet spracovaných batchov, ale nulový remaining-invalid cohort, compatible application behavior a constraint/catalog read-back.

## 2. Access path mení celý runtime mechanizmus

Index je samostatná data structure, ktorá mapuje indexed values na candidate rows alebo tuple locations. Planner však nemusí index použiť. Rozhoduje podľa predicates, ordering, statistics, selectivity, data correlation, cost modelu, parameter values a dostupnosti konkrétneho indexu.

```text
query text + parameter cohort
→ current statistics
→ cardinality a selectivity estimate
→ candidate access paths
→ chosen plan
→ visited rows/pages
→ lock a buffer footprint
→ latency a concurrent queueing
```

Pre query `WHERE merchant_id = ? ORDER BY created_at DESC LIMIT 50` môže byť vhodný B-tree `(merchant_id, created_at DESC)`, pretože filter aj order začínajú stabilným merchant prefixom. Rovnaký index však nie je automaticky vhodný pre global query iba podľa `created_at`. Multicolumn poradie je súčasť contractu, nie syntaktický detail.

B-tree podporuje equality, range a ordering patterns. Inverted index je vhodný pre full-text, arrays alebo contained document values. BRIN alebo podobný block-range summary môže byť efektívny pri veľmi veľkej physically correlated table, ale nenahrádza selective lookup index. Typ indexu sa vyberá podľa operators, distribution a query pathu.

Index zároveň zvyšuje cenu writes. Každý insert, delete alebo update indexed hodnoty môže meniť viac structures, generovať WAL/redo, zaťažovať cache, vacuum a replication. Preto `pridať index na každý filter` môže zrýchliť izolovaný read test, ale znížiť write throughput a predĺžiť failover alebo restore.

## 3. Uniqueness a constraints sú concurrency controls

Application check typu:

```text
SELECT operation WHERE business_key = X
→ nič sa nenašlo
→ INSERT
```

nie je bezpečný pri concurrency. Dve transactions môžu prečítať rovnaký absent state a obe pokračovať. Unique constraint rozhoduje konflikt na authoritative write boundary. Application potom musí rozlíšiť nový success, existing idempotent outcome, skutočný conflict a unknown commit result.

Partial unique index môže chrániť invariant iba v určitom state-e, napríklad najviac jednu `active` operation. Predicate však musí presne zodpovedať business semantics. Ak application a database používajú odlišné definície `active`, constraint môže povoliť forbidden duplicate alebo blokovať legitímny transition.

Constraint rollout je compatibility protocol. Najprv treba zabrániť novým invalid writes, potom opraviť historical cohort, overiť nulové violations a až následne aktivovať finálnu authoritative enforcement. `Index existuje` nie je dostatočné: môže byť invalid, neunique, nepoužitý plannerom alebo vytvorený nad neúplným cohortom.

## 4. Locks, waits a DDL boundary

Lock chráni row, table, index alebo schema metadata počas concurrent operations. Dôležitý nie je iba názov lock mode-u, ale holder, waiter, root blocker, transaction age a compatibility s ostatnými operations. Krátky SQL statement môže zostať súčasťou dlhej open transaction a držať lock výrazne dlhšie než samotná execution.

```text
weak alebo missing access path
→ large candidate scan
→ veľa navštívených rows/pages
→ širší lock a snapshot footprint
→ dlhšia transaction
→ waiters a timeouty
→ retries
→ ešte väčší load
```

Lock wait nie je automaticky deadlock. Deadlock vyžaduje cycle, napríklad T1 drží A a čaká na B, zatiaľ čo T2 drží B a čaká na A. Databáza jednu transaction abortne, ale application musí retryovať celú business transition bezpečne a idempotentne.

DDL môže potrebovať metadata alebo table lock. Exact behavior závisí od engine-u, statementu, table size, default value, validation mode a online/concurrent option. Online DDL neznamená zero lock ani zero load. Môže čakať na staré transactions, generovať veľký I/O a WAL, zaťažiť replicas alebo po zlyhaní ponechať partial artifact.

PostgreSQL `CREATE INDEX CONCURRENTLY` znižuje blocking bežných writes, ale vykonáva viac fáz, čaká na relevantné transactions a po failure môže ponechať invalid index. Acceptance preto musí overiť catalog validity, uniqueness, planner use a production effect.

## 5. Migration ako versionovaný protocol

Bezpečná migration prepája database a viac application generations cez fázy `expand → backfill → switch → contract`. Expand pridá backward-compatible schema a tolerant readers/writers. Backfill transformuje historical state cez stable cursor, malé transactions, conditional writes a resumability. Switch presunie authoritative reads/writes až po reconciliation. Contract odstráni old paths a aktivuje finálne constraints.

```text
expand schema
→ deploy tolerant generations
→ bounded idempotent backfill
→ catch-up a reconciliation
→ read/write switch
→ constraint proof
→ contract old schema
→ retire old application a migration path
```

Backfill nesmie prepisovať novší live state stale hodnotou. Safe mechanizmus používa immutable source fields, row version alebo state predicate, stable keyset cursor a conflict cohort. Batch sa považuje za dokončený až po authoritative cursor commit-e a row-level outcome evidence; progress counter v samostatnej cache nestačí.

Každá fáza potrebuje abort criteria. Lock wait, OLTP latency, WAL generation, replica lag, pool waiters, vacuum pressure alebo error-budget burn môžu migration zastaviť skôr, než sa zmení na incident. Pause musí zachovať exact cursor a umožniť bezpečný resume alebo rollback.

## 6. Worked incident `DB-PAY-56`

Migration pridávala `merchant_operation_id` do `settlement_attempt` s približne `780 miliónmi` rows. Plán používal batch `25 000` rows, potom unique index a `NOT NULL` constraint. Historical cohort sa vyberal podľa `merchant_operation_id IS NULL ORDER BY created_at`, ale supporting partial index neexistoval.

Každý batch opakovane scanoval veľkú časť table. Transactions trvali 4 až 11 minút, držali rows a old snapshots a vytvorili tento chain:

```text
scan-heavy backfill
→ lock waits a pool waiters
→ timeout retries
→ WAL generation 6.4× baseline
→ standby replay lag 94 s
→ vacuum/version pressure
→ application p95 nad 8 s
```

Operator následne spustil štandardný `CREATE UNIQUE INDEX`. Statement čakal za long transaction a po získaní locku zablokoval writers. Po cancel-e zostala request queue a replication backlog. Neskorší concurrent build zlyhal na historical duplicates a ponechal invalid index artifact, no deployment automation kontrolovala iba index name.

Triggerom následného failover incidentu bola AZ network failure. Migration nebola jedinou root cause, ale zväčšila apply lag a uncertainty promotion candidate-u. Primary migration root cause bol chýbajúci current-scale access path, bounded transaction model a catalog/effectiveness gate. Existence-only check zamenil partial artifact za enforcement.

## 7. Evidence, containment a authoritative recovery

Pri migration latency treba rozlíšiť CPU alebo storage saturation, plan regression, lock queue, pool starvation, vacuum/version retention, WAL/replication pressure, index build load a retry amplification. Rozhodujúca evidence chain je:

```text
migration generation + batch identity
→ current query plan a estimated/actual rows
→ active transaction age
→ lock graph a root blocker
→ table/index catalog validity
→ WAL, receive, flush a replay positions
→ pool waiters a application retries
→ remaining-invalid cohort
→ business SLI
```

Containment najprv zastaví nové batchy a retry amplification, zachová plans, locks, cursors a catalog evidence a chráni OLTP admission. Náhodné ukončenie sessions môže spustiť veľký rollback alebo stratiť informáciu, ktoré rows sa commitli.

Authoritative recovery vytvorí supporting partial index bezpečným postupom, overí planner use, zmenší batch a použije stable keyset cursor s conditional update. Historical duplicates sa odstránia podľa exact manifestu. Unique constraint sa aktivuje až po zero-violation proofe. Potom nasleduje second batch, pause/resume, rollback/restart a failover-under-load test.

## 8. Acceptance paths

**Positive path** začína reprezentatívnym production-scale cohortom. Intended index je validný a planner ho používa, batches majú bounded duration, old aj new application generation sú kompatibilné a constraint odmietne concurrent duplicate. Business latency, WAL a replica lag zostanú v guardraile.

**Recovery path** úmyselne preruší batch po committed cursor-e, reštartuje worker a pokračuje bez skipped alebo double-transformed rows. Zlyhaný concurrent index build zostane rozpoznaný ako invalid a automation ho nesmie označiť za complete.

**Failure path** prekročí lock, WAL alebo lag threshold. Migration sa bezpečne pozastaví, zachová exact state a OLTP pokračuje bez unbounded retry stormu.

**Forbidden path** skúša stale backfill overwrite, duplicate business key, broad blocking DDL, index-name-only acceptance a contract phase pri stále aktívnom old writerovi. Všetky musia byť odmietnuté alebo rollbacknuté bez porušenia business invariant-u.

**Second-operation path** opakuje migration na ďalšom tenant/cohort partitione a počas controlled failover-u. Tým sa overí, že úspech nebol závislý od jedného data distributionu alebo jedného primary timeline-u.

## 9. Troubleshooting a anti-patterny

Diagnostika má ísť od exact query a migration generation cez planner, statistics, lock graph, transaction age, cursor a catalog state až k replication a business outcome-u. `Database je pomalá` nie je diagnóza; treba určiť, či čas trávi execution, lock wait, pool acquisition, rollback, replica apply alebo retries.

Najčastejšie anti-patterny sú index na každý filter, unbounded single-statement backfill, DDL v peak-u podľa predpokladanej krátkej execution, blind kill root blockera, progress counter bez reconciliation a acceptance podľa existencie artifactu. Všetky zamieňajú intermediate observation za effective business control.

## 10. Kontrolné otázky

1. Ako access path ovplyvňuje lock a replication footprint?
2. Prečo unique constraint rieši concurrency lepšie než `SELECT then INSERT`?
3. Kedy môže planner ignorovať existujúci index?
4. Prečo online alebo concurrent DDL nie je bezrizikový?
5. Ako funguje `expand → backfill → switch → contract`?
6. Ako backfill zabráni stale overwrite-u?
7. Ktoré evidence odlišujú lock queue od CPU alebo pool starvation?
8. Prečo invalid index artifact nesmie prejsť existence-only gate-om?
9. Ako migration prispela k incidentu `DB-PAY-56`?
10. Čo musia overiť recovery a forbidden paths?

## Glossary impact

Relevantné pojmy: index subject, effective access path, query selectivity, plan generation, multicolumn index, partial index, write amplification, authoritative constraint, lock graph, root blocker, DDL lock, migration generation, expand–backfill–switch–contract, stable cursor, stale backfill overwrite, catalog validity, migration abort criterion a second-batch validation.

## Primárne zdroje

- [PostgreSQL Documentation — Index Types](https://www.postgresql.org/docs/current/indexes-types.html)
- [PostgreSQL Documentation — Multicolumn Indexes](https://www.postgresql.org/docs/current/indexes-multicolumn.html)
- [PostgreSQL Documentation — CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html)
- [PostgreSQL Documentation — Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html)
- [MySQL 8.4 Reference Manual — InnoDB Online DDL Operations](https://dev.mysql.com/doc/refman/8.4/en/innodb-online-ddl-operations.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Transactions a ACID](transactions-and-acid.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Replication a high availability →](replication-and-high-availability.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
