# Databases — model, transaction, migration a replication lifecycles

## Acknowledged-write RPO

Recovery Point Objective vyjadrený voči business operations, ktoré už systém callerovi potvrdil; commit a replication policy musí preukázať, ktoré z nich prežijú konkrétny failure. Pozri [Replikácia a high availability](../docs/15-databases-and-distributed-systems/replication-and-high-availability.md).

## Aggregate boundary

Množina facts a state transitions, ktoré sa typicky čítajú a menia spolu a pre ktoré má byť jasná atomicity a invariant boundary. Pozri [Relational vs. non-relational databases](../docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md).

## Asynchronous replication

Replication policy, pri ktorej primary môže potvrdiť commit pred required acknowledgementom replica-y; znižuje write latency coupling, ale môže vytvoriť non-zero RPO pri permanentnej strate primary. Pozri [Replikácia a high availability](../docs/15-databases-and-distributed-systems/replication-and-high-availability.md).

## Autocommit

Connection alebo framework behavior, pri ktorom každý SQL statement tvorí samostatnú transaction, ak application explicitne nezačne širšiu transaction. Pozri [Transactions a ACID](../docs/15-databases-and-distributed-systems/transactions-and-acid.md).

## Authoritative fact

Business fact, ktorého konkrétny store a state transition rozhodujú o pravde systému; derived projections, caches a search indexes ho môžu kopírovať, ale nesmú nevedome vytvoriť druhú authority. Pozri [Relational vs. non-relational databases](../docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md).

## Covering index

Index obsahujúci key a ďalšie columns potrebné pre query tak, aby engine mohol obmedziť alebo vynechať access k base table podľa visibility a product semantics. Pozri [Indexy, locks a migrácie](../docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md).

## Database-model acceptance verdict

Dôkaz, že authoritative facts, aggregates, relationships, invarianty, access patterns, transaction/consistency semantics, partitioning, derived stores, migration a recovery tvoria správny allowed aj forbidden business outcome. Pozri [Relational vs. non-relational databases](../docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md).

## Database-selection subject

Exact business capability, authoritative facts, invariants, entities/aggregates, access patterns, transaction scope, scale, consistency, failure a recovery requirements hodnotené pri výbere databázového modelu. Pozri [Relational vs. non-relational databases](../docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md).

## Derived data store

Store vytvorený z authoritative change streamu alebo rebuild procesu pre read, search, cache či analytical workload; potrebuje lineage, freshness, completeness a recovery contract. Pozri [Relational vs. non-relational databases](../docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md).

## Dual authority

Failure-prone stav, keď dva stores alebo writers môžu nezávisle meniť rovnaký business fact bez jedného authoritative transition a reconciliation contractu. Pozri [Relational vs. non-relational databases](../docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md).

## DDL lock

Lock alebo metadata-serialization boundary vyžadovaná schema operation, ktorá môže čakať za existujúcimi transactions alebo blokovať ďalšie reads/writes podľa engine-u a statementu. Pozri [Indexy, locks a migrácie](../docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md).

## Estimate-vs-actual verdict

Porovnanie planner estimate-u cardinality/costu s reálne spracovanými rows, časom, buffers a outputom, používané na diagnostiku nesprávneho access pathu. Pozri [Indexy, locks a migrácie](../docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md).

## Expand–backfill–switch–contract

Phased schema/data migration protocol: pridať kompatibilný model, bezpečne doplniť historical state, prepnúť current readers/writers po reconciliation a až potom odstrániť starý contract. Pozri [Indexy, locks a migrácie](../docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md).

## Failback generation

Versionovaný plan a state transition, ktorým sa authoritative workload vracia alebo presúva z recovery writer-a na novú steady-state topology po vyriešení divergence, capacity a dependency podmienok. Pozri [Replikácia a high availability](../docs/15-databases-and-distributed-systems/replication-and-high-availability.md).

## Hot partition

Partition alebo shard, ktorého key distribution sústreďuje neprimeraný traffic, storage alebo contention a porušuje predpoklad rovnomerného horizontal scale-u. Pozri [Relational vs. non-relational databases](../docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md).

## Index/lock/migration acceptance verdict

Dôkaz, že query plan, index validity/use, lock behavior, migration phases, backfill correctness, application compatibility, replication/vacuum guardrails a rollback/restart outcomes prešli v current scale-i. Pozri [Indexy, locks a migrácie](../docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md).

## Index subject

Exact database/table/index/query generation, data distribution, workload, statistics, lock a migration scope analyzovaného access pathu. Pozri [Indexy, locks a migrácie](../docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md).

## Invariant boundary

Rozsah records, documents, services alebo external operations, ktoré musia spoločne zachovať konkrétne business pravidlo. Pozri [Relational vs. non-relational databases](../docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md).

## Invariant-first model

Data-design postup začínajúci business constraints, concurrency a atomic transition requirements pred optimalizáciou physical queries. Pozri [Relational vs. non-relational databases](../docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md).

## Lock graph

Directed graph transactions/sessions a lock dependencies používaný na rozlíšenie holders, waiters, root blockerov a deadlock cycles. Pozri [Indexy, locks a migrácie](../docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md).

## Logical replication

Replication changes na logical row/event úrovni, ktorá môže byť selective a vhodná pre migrations alebo downstream consumers, ale potrebuje explicitný DDL, ordering, conflict a completeness contract. Pozri [Replikácia a high availability](../docs/15-databases-and-distributed-systems/replication-and-high-availability.md).

## Lost update

Concurrency anomaly, pri ktorej neskorší write založený na stale read-e prepíše committed zmenu inej transaction bez conflict verdictu. Pozri [Transactions a ACID](../docs/15-databases-and-distributed-systems/transactions-and-acid.md).

## Migration generation

Exact version schema artifactu, backfill code-u, cursor/state-u, application compatibility a effective constraints/indexes tvoriaca jednu database migration. Pozri [Indexy, locks a migrácie](../docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md).

## MVCC — Multi-Version Concurrency Control

Concurrency mechanism používajúci versions records a transaction snapshots na oddelenie visibility readers/writers; neodstraňuje write conflicts, locks, long-transaction pressure ani serialization retry. Pozri [Transactions a ACID](../docs/15-databases-and-distributed-systems/transactions-and-acid.md).

## Optimistic concurrency

Concurrency model, v ktorom writer mutuje iba vtedy, keď row/version/state stále zodpovedá observed precondition; zero affected rows znamená conflict alebo stale plan. Pozri [Transactions a ACID](../docs/15-databases-and-distributed-systems/transactions-and-acid.md).

## Partial index

Index obsahujúci iba rows spĺňajúce definovaný predicate, vhodný pre bounded active/missing cohort, ak query predicate a business semantics presne zodpovedajú jeho scope-u. Pozri [Indexy, locks a migrácie](../docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md).

## Physical replication

Engine/storage-level replication write-ahead alebo physical changes poskytujúca high-fidelity standby, ale kopírujúca aj logical corruption a často viazaná na užšiu version compatibility. Pozri [Replikácia a high availability](../docs/15-databases-and-distributed-systems/replication-and-high-availability.md).

## Polyglot persistence

Zámerné použitie viacerých databázových technológií s explicitne odlišnými authoritative alebo derived roles, ownershipom, lineage a recovery contractom. Pozri [Relational vs. non-relational databases](../docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md).

## Promotion eligibility

Verdict, že konkrétna replica má compatible generation, required data position, acceptable RPO gap, healthy recovery state, access, capacity a fencing path na prevzatie authoritative writer role. Pozri [Replikácia a high availability](../docs/15-databases-and-distributed-systems/replication-and-high-availability.md).

## Query-first model

Data-design postup začínajúci dominantnými predicates, ordering, pagination, fan-out a latency/freshness requirements, následne vyvažovaný invariant a write modelom. Pozri [Relational vs. non-relational databases](../docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md).

## Receive/flush/replay lag

Oddelené replication gaps medzi logom odoslaným primary, prijatým replica-ou, durably uloženým a aplikovaným/query-visible state-om. Pozri [Replikácia a high availability](../docs/15-databases-and-distributed-systems/replication-and-high-availability.md).

## Relational model

Data model založený na relations, rows, columns, keys, constraints a declarative queries, prirodzene vhodný pre invariant-heavy facts a relationships, ale stále vyžadujúci správnu transaction a physical design boundary. Pozri [Relational vs. non-relational databases](../docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md).

## Replication/HA acceptance verdict

Dôkaz, že replication positions, commit policy, lag, reads, promotion, fencing, client convergence, reconciliation, backup a failback spĺňajú scenario-specific availability, durability, RPO a RTO. Pozri [Replikácia a high availability](../docs/15-databases-and-distributed-systems/replication-and-high-availability.md).

## Replication subject

Exact authoritative data set, primary/replica/timeline generations, replication mechanism, positions, commit policy, read routing, failure, promotion, fencing a recovery scope. Pozri [Replikácia a high availability](../docs/15-databases-and-distributed-systems/replication-and-high-availability.md).

## Root blocker

Session alebo transaction na začiatku lock-wait chainu, ktorej held lock alebo open transaction nepriamo blokuje ďalšie work. Pozri [Indexy, locks a migrácie](../docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md).

## Serialization failure

Databázou vrátený abort, keď concurrent transaction nemožno bezpečne potvrdiť podľa requested serializable/consistency modelu; application má retryovať celú logical transaction. Pozri [Transactions a ACID](../docs/15-databases-and-distributed-systems/transactions-and-acid.md).

## Shard key

Field alebo composite identity určujúca partition placement a routing distributed data; ovplyvňuje locality, balancing, hot partitions, cross-shard queries a transaction scope. Pozri [Relational vs. non-relational databases](../docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md).

## Split brain

Failure state, v ktorom viac nodes alebo partitions súčasne prijíma authoritative writes bez jedného leadership/fencing verdictu a vytvára divergentné histories. Pozri [Replikácia a high availability](../docs/15-databases-and-distributed-systems/replication-and-high-availability.md).

## Stable backfill cursor

Monotonic alebo otherwise resumable position používaná na deterministic bounded batch selection bez repeated broad scans a bez nejasného restart pointu. Pozri [Indexy, locks a migrácie](../docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md).

## Stale backfill overwrite

Failure, pri ktorom backfill vypočíta value zo starého snapshotu a neskôr prepíše novší live state bez version/current-state predicate-u. Pozri [Indexy, locks a migrácie](../docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md).

## Synchronous replication

Replication policy, pri ktorej commit čaká na configured replica/quorum acknowledgement stage; posilňuje acknowledged-write durability za cenu latency a availability coupling. Pozri [Replikácia a high availability](../docs/15-databases-and-distributed-systems/replication-and-high-availability.md).

## Transaction acceptance verdict

Dôkaz, že exact business transition, read/write set, constraints, isolation, locks/conflicts, commit/acknowledgement, idempotency, external workflow a concurrent/second-operation outcomes tvoria správny state transition. Pozri [Transactions a ACID](../docs/15-databases-and-distributed-systems/transactions-and-acid.md).

## Transaction acknowledgement boundary

Moment, po ktorom caller oprávnene považuje logical operation za committed alebo prijatú; musí byť mapovaný na local durability, replication a retry/unknown-outcome semantics. Pozri [Transactions a ACID](../docs/15-databases-and-distributed-systems/transactions-and-acid.md).

## Transaction subject

Exact business operation, database/topology generation, read/write set, preconditions, invarianty, isolation, locks, commit, acknowledgement, retry a external-effect scope jednej transaction. Pozri [Transactions a ACID](../docs/15-databases-and-distributed-systems/transactions-and-acid.md).

## Transaction snapshot

Visibility view určujúci, ktoré committed row versions transaction alebo statement vidí podľa MVCC a isolation levelu. Pozri [Transactions a ACID](../docs/15-databases-and-distributed-systems/transactions-and-acid.md).

## Unknown commit outcome

Stav, keď client nedostal authoritative response a nevie, či database alebo external operation commitla; bezpečné riešenie vyžaduje stable identity, idempotency a reconciliation. Pozri [Transactions a ACID](../docs/15-databases-and-distributed-systems/transactions-and-acid.md).

## Write amplification — database

Dodatočné index, WAL/redo, replication, vacuum/compaction a storage operations vyvolané jedným logical write-om. Pozri [Indexy, locks a migrácie](../docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md).

## Write skew

Isolation anomaly, pri ktorej concurrent transactions menia odlišné rows na základe spoločnej precondition a spolu porušia invariant bez direct write/write conflictu. Pozri [Transactions a ACID](../docs/15-databases-and-distributed-systems/transactions-and-acid.md).

## Writer epoch

Monotonic leadership generation pripojená k write authorization alebo records/events, ktorá pomáha odmietnuť stale writer-a po failover-e. Pozri [Replikácia a high availability](../docs/15-databases-and-distributed-systems/replication-and-high-availability.md).

## Writer fencing

Mechanizmus, ktorý preukázateľne zabráni old alebo stale primary-u prijímať authoritative writes pred alebo počas promotion novej writer generation. Pozri [Replikácia a high availability](../docs/15-databases-and-distributed-systems/replication-and-high-availability.md).