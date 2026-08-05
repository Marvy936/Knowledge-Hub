# Self-hosting s PostgreSQL

Self-hosted n8n s PostgreSQL nie je iba aplikácia pripojená k externej databáze. PostgreSQL uchováva workflow definitions, credentials v šifrovanej podobe, users, projects, executions, settings a ďalší control-plane aj execution state. Dostupnosť a obnoviteľnosť platformy preto závisí od spoločného lifecycle n8n release, databázovej schema, encryption key, storage a external dependencies.

Táto kapitola otvára incident `AGENT-N8N-09`. Operations tím zvýšil počet workerov zo štyroch na šestnásť, pretože rástla Redis queue. Každý nový proces však otvoril vlastný database pool a súčet main, webhook a worker connections prekročil PostgreSQL `max_connections`. UI zostalo krátko dostupné, no workers strácali readiness, executions ostávali v nejednoznačnom stave a ďalšie scale-out iba zrýchľovalo zlyhanie.

Nosný self-hosting lifecycle je:

```text
business workload a recovery objective
→ exact n8n, PostgreSQL a schema generation
→ network, TLS, identity a database authority
→ connection a transaction budget
→ migration a release ordering
→ execution persistence a storage dependencies
→ backup, WAL/PITR a encryption-key evidence
→ isolated restore a application read-back
→ representative a second-workflow acceptance
```

## 1. Prečo PostgreSQL

SQLite je vhodný pre jednoduchú lokálnu alebo malú single-process inštaláciu, pretože minimalizuje počet komponentov. Distribuovaný alebo rastúci self-hosted deployment však potrebuje databázu dostupnú viacerým procesom, riadené connections, samostatný backup lifecycle a prevádzkovú observability.

n8n podporuje PostgreSQL a odporúča aktívne udržiavanú verziu. Queue mode nad SQLite nie je podporovaný distribuovaný model, pretože workers potrebujú spoločný databázový authority point.

## 2. Databáza ako authority

PostgreSQL je authoritative store pre stav, ktorý n8n potrebuje opakovane načítať a zdieľať medzi procesmi. Redis v queue mode prenáša execution work a completion notifications, ale nenahrádza workflow, credential ani execution persistence v databáze.

Toto rozdelenie je dôležité pri recovery. Obnovený Redis bez správnej databázy nevytvorí konzistentnú platformu a obnovená databáza bez reconciliation nemusí vysvetliť external side effects vykonané pred incidentom.

## 3. Exact deployment subject

Prevádzkový subject zahŕňa n8n image digest, n8n version, database engine a major version, schema/migration generation, configuration digest, encryption key generation, enabled nodes, execution mode a storage mode. Názov služby `n8n-production` nie je dostatočná identita.

Incident review porovnáva intended, deployed, connected a exercised subject. Rovnaký application image nad inou schema alebo s iným key môže mať úplne odlišné správanie.

## 4. PostgreSQL version policy

Používa sa iba PostgreSQL major version, ktorú upstream stále udržiava a ktorú deployment platforma podporuje. Major upgrade mení server behavior, extensions, planner a recovery procedures, preto sa neposudzuje ako bežný patch rollout.

Patch updates sa tiež testujú, ale majú menší compatibility scope. Version policy obsahuje ownera, end-of-support date, upgrade window a rollback alebo restore path.

## 5. Database configuration

n8n vyberá PostgreSQL cez `DB_TYPE=postgresdb` a potrebuje host, port, database, user, password a schema. Tieto values tvoria connection subject a musia byť rovnaké pre main, workers a webhook processors v rovnakom deployment scope.

Configuration sa načítava z environmentu alebo podporovaného file-based secret modelu. Runtime read-back overí skutočný server, database a schema, nie iba hodnoty v manifest-e.

## 6. Samostatná database a schema

Produkčný n8n má vlastnú database alebo minimálne jasne vlastnenú schema s explicitnými privileges. Znižuje sa tým riziko name collision, neúmyselného cross-application accessu a nejasného backup scope.

Schema prefix alebo custom schema nie je tenant isolation. Všetky workflows v jednej n8n instance stále zdieľajú application authority podľa n8n project a credential modelu.

## 7. Database user

Runtime user potrebuje permissions, ktoré n8n vyžaduje na čítanie, zápis a schema migrations. Nemá byť PostgreSQL superuser ani všeobecný administratívny účet.

Migration potreby sa musia zladiť s least privilege. Ak organizácia oddeľuje runtime a migration identity, rollout musí podporovať toto rozdelenie a preukázať, že aplikácia po migrácii funguje bez elevated rights.

## 8. TLS a server identity

TLS chráni database traffic pred odpočúvaním a modifikáciou. Dôležitá je aj validácia server certificate, pretože šifrované spojenie k nesprávnemu serveru stále porušuje authority boundary.

CA, client certificate a private key majú vlastný rotation lifecycle. Nastavenie, ktoré vypne certificate verification, môže pomôcť diagnostike, ale nie je prijateľný production end state bez explicitnej výnimky.

## 9. Network boundary

PostgreSQL port je dostupný iba n8n workloadom, database administration a schváleným monitoring komponentom. Public exposure alebo široký cluster-wide access zvyšuje blast radius uniknutého passwordu.

Network policy sa kombinuje s PostgreSQL authentication a TLS. Žiadna jednotlivá vrstva nepreukazuje, že request pochádza z intended workloadu.

## 10. Encryption key dependency

Credential values sú uložené šifrovane a všetky n8n procesy, ktoré ich používajú, potrebujú compatible `N8N_ENCRYPTION_KEY`. Database backup bez key môže obsahovať workflowy a execution metadata, ale nemusí obnoviť použiteľné credentials.

Key je preto samostatný recovery artifact s prísnejším accessom. Backup evidence uvádza key generation, nie plaintext value.

## 11. Connection lifecycle

Každý n8n process otvára database connections podľa svojho runtime a pool configuration. Connection nie je bezplatná; server pre ňu rezervuje resources a príliš veľa súčasných sessions zvyšuje memory, scheduling a lock pressure.

Scale-out workerov preto násobí connection demand. Capacity model musí počítať main, webhook processors, workers, migrations, monitoring, backup a emergency administration.

## 12. Connection budget

Connection budget je explicitná rovnica, nie odhad podľa počtu Podov. Použiteľný budget je menší než `max_connections`, pretože časť slots zostáva pre database operations a incident recovery.

Príklad modelu:

```text
usable_connections
= max_connections
- reserved_admin
- backup_and_monitoring
- migration_headroom

application_demand
= main_processes × pool_per_main
+ webhook_processes × pool_per_webhook
+ workers × pool_per_worker
```

Scale-out je povolený iba vtedy, keď application demand zostáva pod budgetom aj počas rollout overlapu.

## 13. Pool multiplication

Pool size nastavený na desať môže pôsobiť nízko pri jednom procese, ale dvadsať workerov vytvorí teoretický demand dvesto connections ešte pred main a webhook vrstvou. Autoscaler, ktorý sleduje iba queue depth, tento coupling nevidí.

Worker concurrency a database pool nie sú rovnaká hodnota. Jeden execution môže držať connection iba časť svojho lifecycle, no peak a transaction behavior sa merajú pod representative loadom.

## 14. Connection proxy

Externý pooler môže znížiť počet server-side connections, ale zavádza nový protocol a transaction boundary. Jeho mode, prepared statements, session state, TLS, health a failover behavior musia byť kompatibilné s n8n a používaným driverom.

Pooler sa nepridáva iba preto, aby zakryl neobmedzený worker count. Najprv sa opraví connection budget, concurrency a workload profile.

## 15. Transactions a atomicity

n8n používa databázové transactions na konzistentné mutations svojho interného state. Databázový commit však nie je distribuovaná transaction s external API, emailom alebo cloud resource mutation.

Po timeout-e môže byť interný alebo external outcome neznámy. Recovery číta n8n execution state, provider state a idempotency ledger pred ďalším pokusom.

## 16. Schema migrations

Nová n8n verzia môže priniesť database migrations. Migration mení shared authority a musí byť viazaná na exact release, backup a compatibility plan.

Viac procesov sa nespúšťa nekontrolovane proti starej schema. Rollout stanoví, ktorý component vykoná migration, kedy môžu nastúpiť workers a či je downgrade po zmene schema vôbec podporovaný.

## 17. Migration locks

DDL môže čakať na locks alebo blokovať concurrent operations. Malý staging dataset nemusí odhaliť duration a lock behavior produkčnej tabuľky s veľkou execution históriou.

Pre-upgrade test používa realistický objem a sleduje `pg_stat_activity`, `pg_locks`, transaction age a application error rate. Timeout nie je dôkaz, že migration sa necommitla.

## 18. Mixed-version deployment

Main, workers, webhook processors a task runners majú používať compatible, typicky rovnakú n8n version. Dlhý mixed-version interval môže spájať nový schema alebo message contract so starým runtime.

Rolling rollout preto potrebuje compatibility statement a krátke bounded overlap okno. Pri nejasnej compatibility sa používa stop-the-world alebo blue/green postup s explicitným cutoverom.

## 19. Database high availability

Managed alebo self-operated PostgreSQL môže mať standby a failover. HA znižuje infrastructure downtime, ale neprináša automaticky nulové RPO, nulové connection interruption ani application correctness.

n8n processes musia reconnectnúť k novému primary a in-flight operations sa reconciliujú. DNS alebo proxy failover status nie je business recovery proof.

## 20. Replica lag

Asynchronous replica môže byť pozadu. Routing application reads na repliku bez explicitnej n8n podpory môže vrátiť stale workflow, credential alebo execution state a porušiť read-after-write assumptions.

Replicas sa používajú podľa podporovaného database architecture, primárne pre recovery alebo approved observability. Application read/write split sa nevymýšľa mimo product contractu.

## 21. Storage a IOPS

Database latency ovplyvňuje workflow loading, execution persistence, credentials, queue coordination aj UI. CPU môže byť nízke, zatiaľ čo storage latency alebo WAL flush limituje throughput.

Sizing sleduje transactions, fsync latency, IOPS, working set, checkpoints, WAL growth a table/index bloat. Scale test musí obsahovať actual persistence settings.

## 22. Execution-data growth

Ukladanie úspešných executions, node progressu a veľkých payloadov môže rýchlo zväčšiť databázu. Rast zvyšuje backup time, restore time, index size a migration risk.

Retention sa navrhuje podľa debugging, audit, privacy a recovery potrieb. „Uchovať všetko“ nie je bezpečný default bez capacity a data-governance analýzy.

## 23. Vacuum a bloat

Updates a deletions vytvárajú dead tuples, ktoré PostgreSQL priebežne spracúva autovacuum. Execution pruning môže generovať výrazný delete workload a dočasne zvýšiť WAL a I/O.

Sleduje sa dead-tuple ratio, autovacuum progress, transaction age a table growth. Ručný `VACUUM FULL` je disruptive zásah a nepoužíva sa ako prvá reakcia bez impact plánu.

## 24. Long-running transactions

Dlhá transaction môže držať row versions, locks a brániť cleanupu. V n8n incidente môže pochádzať z migration, administratívneho query alebo zlyhaného application pathu.

Evidence kombinuje `pg_stat_activity`, lock graph, query age a n8n execution timeline. Process sa neukončí naslepo, ak nie je známy transaction outcome a owner.

## 25. Backup scope

Database backup musí pokryť všetky n8n tables a schema metadata pre exact point in time. Samotný SQL dump však neobsahuje encryption key, binary objects mimo database, Redis state, deployment manifests ani external provider resources.

Recovery inventory preto rozlišuje database, secret/key, binary storage, source-control artifacts a infrastructure configuration. Každá vrstva má vlastný owner a retention.

## 26. Logical backup

`pg_dump` alebo ekvivalentný managed-service export poskytuje logický obraz database. Je prenosný medzi kompatibilnými versions a užitočný pre menšie datasets alebo selected restores.

Logical backup môže byť pomalší pri veľkom execution store a jeho existencia nepreukazuje restore duration. Test sa vykoná na reálnom objeme a s kontrolou permissions, extensions a schema ownership.

## 27. Physical backup a PITR

Base backup s kontinuálnym WAL archívom umožňuje point-in-time recovery podľa PostgreSQL modelu. RPO závisí od úplnosti WAL chainu a RTO od schopnosti obnoviť base backup, replaynúť WAL a znovu pripojiť application.

PITR neobnovuje automaticky súbory konfigurácie mimo database ani external binary storage. Recovery point sa musí korelovať s týmito artifacts.

## 28. Restore drill

Restore drill vytvorí isolated PostgreSQL, obnoví database, dodá correct encryption key a spustí compatible n8n version bez production triggers. Najprv sa vykonajú read-only checks a až potom sandbox side-effect test.

Drill meria čas, manuálne kroky, chýbajúce artifacts a data loss. Backup sa označí ako použiteľný až po tomto read-backu.

## 29. RPO a RTO

RPO určuje prijateľnú stratu committed database changes. RTO určuje čas do obnovy usable automation capability, nie iba čas do štartu PostgreSQL procesu.

Application RTO zahŕňa credentials, workflows, publication state, binary data, workers, webhooks a external reconciliation. Database green je iba component recovery.

## 30. Database monitoring

Sledujú sa active a waiting sessions, connection utilization, transaction latency, locks, deadlocks, cache hit, WAL rate, checkpoints, storage latency, replication lag, table growth a backup freshness. Každý signal má ownera a threshold naviazaný na user outcome.

Queue backlog bez database metrics môže viesť k nesprávnemu scale-outu. Correlation medzi execution IDs, worker generation a database events určuje first divergence.

## 31. Shared incident `AGENT-N8N-09`

Queue waiting rástla po veľkom webhook importe. Autoscaler pridal dvanásť workerov, každý s vlastným poolom, a PostgreSQL odmietol nové sessions. Niektoré workers prešli liveness, ale readiness zlyhávala na database connection.

Operations tím pridal ďalšie replicas, čím ešte zvýšil connection pressure. Redis bol dostupný, takže broker health vyzeral pozitívne, no workers nedokázali načítať workflow a zapísať completion state.

## 32. Competing failure hypotheses

Prvá hypotéza je nedostatok worker CPU, druhá Redis latency, tretia PostgreSQL connection exhaustion, štvrtá lock alebo migration contention a piata storage latency. Všetky môžu vytvoriť queue backlog, ale vyžadujú odlišný zásah.

Evidence porovná queue age, worker readiness, database sessions, lock graph, I/O a execution timeline. Scale-out je experiment až po potvrdení, že downstream authority má headroom.

## 33. Evidence preservation

Zachová sa n8n release a config digest, process inventory, pool settings, worker concurrency, `max_connections`, `pg_stat_activity`, `pg_locks`, Redis queue metrics, failed execution IDs a deployment events. Snapshot má timestamp a source identity.

Pred reštartom sa zaznamenajú unknown external outcomes. Process restart môže odstrániť useful in-memory context, ale nesmie odložiť safety containment.

## 34. Containment

Autoscaling sa pozastaví, worker count sa zníži na known-safe connection budget a nové non-critical triggers sa obmedzia. Reserved database access ostane dostupný incident tímu.

Long-running alebo blocking sessions sa ukončia iba po owner a outcome review. Queue sa nedrainuje bulk retryom, kým nie sú známe per-operation idempotency states.

## 35. Recovery

Recovery nastaví explicitný pool a concurrency budget, opraví autoscaling signals a preukáže reconnect všetkých process roles. Database backup a encryption-key inventory sa aktualizujú a restore drill sa zopakuje.

Representative executions sa púšťajú po malých cohorts. Queue age, database saturation a external outcome sa musia súčasne vrátiť do accepted range.

## 36. Positive acceptance

Main, webhook a worker processes používajú intended database, schema, TLS a encryption key. Connection demand zostáva pod budgetom pri steady state, rollout overlap aj failure test-e.

Workflow sa vykoná, uloží completion state a authoritative external read-back potvrdí outcome. Database monitoring ukazuje expected sessions a žiadne skryté lock waits.

## 37. Forbidden acceptance

Deployment nie je prijatý iba preto, že UI sa otvorí alebo PostgreSQL odpovie na TCP port. Neprípustný je superuser runtime, vypnutá TLS validation, neobmedzené pools, untested migration alebo backup bez key a restore evidence.

Queue backlog sa nesmie riešiť automatickým scale-outom bez database a storage headroom. Component health nenahrádza end-to-end proof.

## 38. Recovery acceptance

Failover alebo restore drill obnoví exact database point, compatible n8n version a credential decryption v isolated environment. RPO a RTO sa merajú od incident triggeru po usable representative workflow.

Unknown executions sa klasifikujú a provider side effects reconciliujú. Recovery sa neuzavrie iba spustením nového primary.

## 39. Second-workflow acceptance

Druhý workflow s odlišným payloadom, credentialom a execution duration prejde rovnakým restored alebo failover pathom. Overí sa, že database connection budget nie je optimalizovaný iba pre jeden krátky canary.

Test zároveň potvrdí project a tenant boundaries. Obnovená database nesmie mapovať workflow na nesprávny credential alebo environment endpoint.

## 40. Praktický configuration manifest

Manifest spája application a database generation bez secret values. Používa sa pri review, incident response aj restore.

```yaml
n8n_database_subject:
  n8n_image: docker.n8n.io/n8nio/n8n@sha256:...
  n8n_version: 2.x
  database_engine: postgresql
  database_major: 18
  database: n8n
  schema: n8n
  tls_verify: true
  encryption_key_generation: key-2026-08
  process_budget:
    main: 1
    webhook: 2
    workers: 8
    pool_per_process: 5
  backup:
    base_backup: backup-2026-08-05
    wal_archive: continuous
    last_restore_drill: 2026-08-01
```

## 41. Praktické diagnostic queries

Queries slúžia na read-only diagnosis a musia sa spúšťať so scoped accountom. Výstup sa koreluje s application timeline, nie interpretuje izolovane.

```sql
SELECT state, wait_event_type, wait_event, count(*)
FROM pg_stat_activity
WHERE datname = 'n8n'
GROUP BY state, wait_event_type, wait_event
ORDER BY count(*) DESC;

SELECT pid, usename, state, now() - xact_start AS transaction_age, query
FROM pg_stat_activity
WHERE datname = 'n8n' AND xact_start IS NOT NULL
ORDER BY xact_start;
```

## 42. Prevádzkové metriky

Sledujú sa connection utilization, rejected connections, pool wait, transaction latency, lock waits, deadlocks, WAL/archive lag, storage growth, pruning duration, backup age, restore-drill age a n8n execution persistence errors. Metriky sa segmentujú podľa process role a release generation.

Nízke CPU pri vysokom queue age nie je automaticky worker shortage. Database wait a connection pressure môžu byť skutočný bottleneck.

## 43. Primárne zdroje

- [n8n Docs — Choose n8n's database](https://docs.n8n.io/deploy/host-n8n/configure-n8n/choose-n8ns-database/)
- [n8n Docs — Database environment variables](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables/database/)
- [n8n Docs — Enable queue mode](https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode/)
- [PostgreSQL — Connections and authentication](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [PostgreSQL — Monitoring database activity](https://www.postgresql.org/docs/current/monitoring.html)
- [PostgreSQL — Backup and restore](https://www.postgresql.org/docs/current/backup.html)
- [PostgreSQL — Continuous archiving and point-in-time recovery](https://www.postgresql.org/docs/current/continuous-archiving.html)

## 44. Zhrnutie

PostgreSQL je shared state authority self-hosted n8n platformy. Bez explicitného connection budgetu, migration ordering, encryption-key recovery a restore proof môže scale-out alebo upgrade znížiť dostupnosť namiesto jej zvýšenia.

Accepted deployment spája database health s execution a business outcome. Backup, failover a queue metrics sú iba čiastkové evidence, kým representative a druhý workflow neprejdú celým obnoveným lifecycle.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Source control a environments](source-control-environments.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Queue mode, Redis, workers a scaling →](queue-mode-redis-workers-scaling.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
