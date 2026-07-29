# Databases and Distributed Systems — recovery, pooling, products a architecture lifecycles

## Database recovery subject

Exact engine/cluster, protected data a consistency group, acknowledgement boundary, base backup, change-log interval, timeline/position, schema, key/access generation, recovery target, objectives a post-point recovery scope. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Protected consistency group — database recovery

Súbor databázových a external facts, ktoré sa musia obnoviť alebo reconciliovať spolu, aby business invariant zostal platný. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Logical backup

Engine-aware logical export schemas, objects a rows určený na portable alebo selected-object restore; nie je physical base backupom pre WAL/redo replay. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Physical backup

Kópia engine storage generation vytvorená cez consistency-aware backup alebo snapshot protocol a viazaná na engine/version/storage/log semantics. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Base backup

Physical starting state, od ktorého možno replaynuť kontinuálny WAL alebo iný change log do recovery targetu. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Continuous log archive

Durable, ordered a čitateľný archív WAL, binary-log alebo ekvivalentných change records potrebných na incremental alebo point-in-time recovery. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## WAL continuity

Dôkaz, že od required base-backup position po target nechýba žiadny PostgreSQL WAL segment ani timeline metadata potrebná na replay. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Binary-log continuity

Dôkaz, že MySQL binary-log files/events, positions alebo GTID intervaly od full backupu po target tvoria complete recovery sequence. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Recovery target — database

Exact time, named point, LSN, transaction, binlog position, GTID alebo business event boundary, na ktorom má recovery replay skončiť. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Recovery timeline — database

Versionovaná log history vytvorená po recovery/promotion, ktorá odlišuje nový write branch od pôvodnej alebo predchádzajúcich recovery histories. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Clean recovery point — database

Recovery candidate pred alebo mimo corruption interval, ktorý je log-complete, decryptable, schema-compatible a business-valid pre daný protected subject. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Archive read-back

Independent overenie, že archived backup/log object existuje, je čitateľný, má správny checksum/identity a možno ho retrieve-nuť cez reálny restore path. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Restore generation — database

Immutable subject konkrétneho restore pokusu: source manifest, target environment, engine/schema/application versions, recovered position/timeline a validation evidence. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Cross-store recovery checkpoint

Versionovaný correlation point medzi authoritative positions alebo event IDs viacerých stores a external systems, používaný na business-consistent recovery a reconciliation. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Post-point divergence

Operations a state transitions, ktoré vznikli po selected recovery point-e a musia byť replaynuté, merge-nuté, compensated alebo reconciled. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Backup/PITR acceptance verdict

Dôkaz, že base backup, log continuity, keys/access, target selection, isolated restore, validation, reconciliation, promotion/fencing a second restore spĺňajú business RPO/RTO a forbidden scenarios. Pozri [Backups a point-in-time recovery](../docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md).

## Connection-pooling subject

Exact application fleet, pooler/client generations, endpoint/role, min/max connections, pooling mode, session requirements, database envelope, timeouts, queue a failover behavior. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Application connection pool

Client-side cache a admission mechanism, ktorý reuses database connections a riadi checkout, active/idle count, timeouts a cleanup v jednom application process-e. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Server connection envelope

Nameraný počet open a active database server connections, ktorý workload bezpečne unesie pri normal, burst, failover a recovery conditions po odpočítaní reserved capacity. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Session pooling

Pool mode, v ktorom server connection zostáva priradená clientovi až do client disconnectu a zachováva server-session affinity. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Transaction pooling

Pool mode, v ktorom sa server connection uvoľní po transaction a ďalšia transaction rovnakého clienta môže použiť inú server session. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Statement pooling

Pool mode, v ktorom sa server connection uvoľní po jednom statemente a multi-statement transactions nie sú podporované. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Pool multiplication

Fleet-wide násobenie connection demandu cez počet services, replicas, processes, users/databases a per-instance pool maxima. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Pool queue

Fronta application requests alebo client sessions čakajúcich na reusable server connection; jej latency je samostatná od query execution latency. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Checkout wait

Čas od požiadania o connection po jej pridelenie z poolu, meraný ako distribution a porovnávaný s request deadline-om. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Minimum-idle storm

Súbežné vytváranie veľkého množstva idle connections po scale-out-e, restart-e alebo failover-e v dôsledku vysokého minimum pool size bez jitter/admission budgetu. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Session-state compatibility

Verdict, či tenant context, temporary objects, prepared statements, advisory locks, role/search path a ďalší connection-local state fungujú s konkrétnym pooling mode-om. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Connection reset contract

Pravidlá rollbacku, resetu alebo discardu connection pred reuse, vrátane failed transaction, role, session parameters, temp objects, locks a protocol state-u. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Broken-connection discard

Odstránenie connection z poolu po network/protocol/transaction ambiguity namiesto jej vrátenia ďalšiemu borrowerovi. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Administrative connection reserve

Connection slots, identity a route vyhradené pre incident inspection, fencing, recovery a administratívne operations pri application saturation. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Reconnect storm

Súbežná vlna connection handshakes a retries po failure/restart/failover-e, ktorá môže preťažiť nový primary alebo pooler skôr než business workload. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Pooling acceptance verdict

Dôkaz, že fleet connection demand, database envelope, pooling mode, session hygiene, queues/timeouts, admin reserve, failover a second-client/burst tests vytvárajú bounded a correct outcome. Pozri [Connection pooling](../docs/15-databases-and-distributed-systems/connection-pooling.md).

## Product-role subject — database

Exact business/data role, authority classification, invariant, access pattern, durability, consistency, scale, recovery a operational ownership priradené konkrétnemu database produktu. Pozri [PostgreSQL, MySQL a Redis](../docs/15-databases-and-distributed-systems/postgresql-mysql-and-redis.md).

## PostgreSQL authority role

Použitie PostgreSQL ako authoritative relational boundary s MVCC, constraints, WAL, transactions a recovery contractom pre konkrétne business facts. Pozri [PostgreSQL, MySQL a Redis](../docs/15-databases-and-distributed-systems/postgresql-mysql-and-redis.md).

## InnoDB transaction role

Použitie MySQL/InnoDB ako authoritative relational boundary s MVCC, locks, redo/undo, binary log a engine-specific durability/recovery semantics. Pozri [PostgreSQL, MySQL a Redis](../docs/15-databases-and-distributed-systems/postgresql-mysql-and-redis.md).

## Redis data-structure role

Použitie Redis keys a native data structures pre cache, counters, ranking, streams, coordination alebo low-latency state podľa explicitných TTL, persistence, replication a authority semantics. Pozri [PostgreSQL, MySQL a Redis](../docs/15-databases-and-distributed-systems/postgresql-mysql-and-redis.md).

## Cache authority inversion

Failure mode, pri ktorom cache hit/miss/TTL alebo eviction začne rozhodovať o authoritative business existencii alebo external side effecte namiesto zrýchľovania authority lookupu. Pozri [PostgreSQL, MySQL a Redis](../docs/15-databases-and-distributed-systems/postgresql-mysql-and-redis.md).

## RDB snapshot — Redis

Point-in-time persistence súbor Redis datasetu vytváraný podľa configured snapshot policy. Pozri [PostgreSQL, MySQL a Redis](../docs/15-databases-and-distributed-systems/postgresql-mysql-and-redis.md).

## Append Only File — Redis

Persistence log Redis write operations, ktorý možno replaynuť pri štarte; durability window závisí od configured fsync policy. Pozri [PostgreSQL, MySQL a Redis](../docs/15-databases-and-distributed-systems/postgresql-mysql-and-redis.md).

## Derived-key absence

Redis/cache miss, ktorý znamená iba neprítomnosť derived evidence v current cache generation, nie automaticky neprítomnosť authoritative business operation. Pozri [PostgreSQL, MySQL a Redis](../docs/15-databases-and-distributed-systems/postgresql-mysql-and-redis.md).

## Policy generation identity

Immutable version alebo effective-interval identity merchant/provider policy uložená spolu s business decisionom, aby sa dal outcome reprodukovať a reconciliovať. Pozri [PostgreSQL, MySQL a Redis](../docs/15-databases-and-distributed-systems/postgresql-mysql-and-redis.md).

## Cross-product reconciliation

Correlation PostgreSQL, MySQL, Redis, event a external-provider evidence podľa stable business operation identity na určenie authoritative outcome-u. Pozri [PostgreSQL, MySQL a Redis](../docs/15-databases-and-distributed-systems/postgresql-mysql-and-redis.md).

## Product-selection acceptance verdict

Dôkaz, že product roles, authority, transactions, durability, recovery, cache semantics, cross-product identity a failure tests zodpovedajú workloadu bez dual authority. Pozri [PostgreSQL, MySQL a Redis](../docs/15-databases-and-distributed-systems/postgresql-mysql-and-redis.md).

## Architecture subject — application boundaries

Exact capabilities, invariant/data ownership, source/build/deployment/process boundaries, communication, transactions, scale, ownership, operations a migration generation analyzovanej architecture. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Monolith

Application buildovaná a deployovaná ako jeden významný artifact alebo runtime unit; môže byť dobre modularizovaná alebo silno previazaná. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Modular monolith

Jeden deployment/process boundary s explicitnými internal module APIs, private implementation/data access a enforced dependency/ownership pravidlami. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Microservice

Independently deployable service vlastniaci coherent business capability, contract, runtime failure boundary a authoritative data/workflow responsibilities. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Module boundary

In-process contract oddeľujúci public capability od private modelu, dependencies a data accessu v modular monolith-e. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Service boundary

Remote runtime a ownership boundary s explicitným API/event contractom, independent deploymentom, local state/transaction a failure/recovery semantics. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Deployment boundary

Najmenší subject, ktorý možno release-nuť, rollback-nuť alebo promote-nuť nezávisle s vlastnou compatibility a evidence generáciou. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Failure boundary — application architecture

Rozsah process/resource/dependency failure-u, ktorý má byť izolovaný od ostatných capabilities a pre ktorý existuje independent recovery contract. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Database per service

Exclusive authority nad data capability cez service contract; môže byť realizovaná samostatným serverom, database alebo enforced schema/role boundary. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Distributed monolith

Systém s viacerými remote deployments, ktorý stále vyžaduje synchronized releases, shared data access alebo tightly coupled runtime availability, a preto nesie distributed cost bez autonomy. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Local transaction boundary

Data a invariant scope, ktorý možno atomicky commitnúť v jednom service/database authority bez remote distributed workflowu. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Cross-service workflow

Versionovaný state machine koordinujúci local commits, durable events, retries, compensation a reconciliation naprieč service boundaries. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Saga alebo process manager

Mechanizmus, ktorý sleduje multi-step business workflow naprieč services a riadi next action, timeout, retry, compensation a terminal verdict. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Strangler extraction

Incremental migration, pri ktorej bounded operation/cohort prechádza na nový service, outcomes sa porovnávajú a starý path sa po acceptance retire-nuje. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Branch by abstraction

Migration pattern, pri ktorom callers používajú stabilnú abstraction a implementation sa postupne nahrádza bez permanentného dual write-u. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Architecture benefit verdict

Evidence-backed porovnanie intended independent deployment/scale/failure/ownership benefitu s effective coordination, platform, reliability a recovery costom. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).

## Architecture acceptance verdict

Dôkaz, že capability/invariant boundaries, authority, transactions, communication, compatibility, scale, failure isolation, operations, migration a second-change/failure tests tvoria udržateľný outcome. Pozri [Monolith, modular monolith a microservices](../docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md).
