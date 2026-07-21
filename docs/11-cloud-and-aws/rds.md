# Amazon RDS

Amazon Relational Database Service je managed relational database platforma. AWS spravuje časť infrastructure a database lifecycle-u, ale zákazník stále vlastní schema, queries, indexing, connection behavior, data classification, access, backup requirements, recovery testy a application compatibility.

RDS nie je „databáza bez prevádzky“. Je to presunutá responsibility boundary.

## 1. Mentálny model

```text
application
→ DNS endpoint
→ network a TLS
→ database listener
→ DB engine
→ storage a transaction log
```

Riadiaca vrstva zahŕňa:

- DB instance alebo DB cluster,
- engine/version,
- instance class,
- storage,
- subnet group,
- Security Groups,
- parameter a option groups,
- backups a snapshots,
- maintenance,
- monitoring a events.

Pri incidente oddeľ:

- AWS control-plane state,
- network path,
- authentication/authorization,
- database engine state,
- query/workload behavior,
- storage/replication,
- application connection handling.

## 2. Supported engines a service variants

RDS podporuje viac relational engines podľa aktuálnej Region/version availability, napríklad:

- PostgreSQL,
- MySQL,
- MariaDB,
- Oracle,
- Microsoft SQL Server,
- Db2,
- ďalšie engine-specific variants podľa AWS ponuky.

Amazon Aurora je relational managed service kompatibilný s vybranými MySQL/PostgreSQL interfaces, ale má odlišný storage, replication a cluster model. Aurora patrí do samostatnej hlbšej témy, hoci veľa operational princípov je spoločných.

RDS Custom poskytuje väčšiu OS/database kontrolu pre vybrané engines, ale posúva viac responsibility späť na zákazníka.

## 3. DB instance

DB instance je isolated database environment s konkrétnou:

- instance class,
- engine/version,
- storage configuration,
- VPC/subnet placement,
- parameter/option groups,
- backup/maintenance policy.

Instance class ovplyvňuje:

- vCPU,
- memory,
- network bandwidth,
- EBS/storage bandwidth,
- maximum connection a cache behavior nepriamo cez engine.

Vertical scaling môže vyžadovať reboot alebo failover podľa modification a deployment modelu.

## 4. DB subnet group

DB subnet group je kolekcia subnets, ktoré môže RDS použiť pre database placement.

Production návrh typicky obsahuje subnets vo viacerých Availability Zones.

RDS DB instance nemá patriť do public subnetu iba preto, že application nevie správne routovať private traffic. Preferuj private addressing a explicitnú application/admin access cestu.

Over:

- subnet free IP capacity,
- route tables,
- Security Groups,
- NACLs,
- DNS resolution,
- Multi-AZ coverage.

## 5. Endpoint a DNS

Application sa pripája cez RDS endpoint.

Pri failover-e sa endpoint nemení logicky, ale DNS mapping sa presmeruje na nový primary/writer.

Application musí:

- používať DNS name, nie cached IP,
- mať rozumný DNS TTL/cache behavior,
- reconnectovať po broken connection,
- používať bounded retries a backoff,
- znovu vytvoriť transaction podľa idempotency contractu.

Connection pool môže držať stale connections aj po DNS zmene. Failover test musí overiť pool recovery, nie iba console stav `available`.

## 6. Single-AZ

Single-AZ deployment používa jednu active DB instance v jednej AZ.

Vhodné môže byť pre:

- development,
- noncritical workload,
- cost-sensitive environment s akceptovaným recovery time.

Riziká:

- host/AZ failure vyžaduje recovery,
- maintenance môže znamenať downtime,
- vyšší RTO než Multi-AZ,
- backup restore nie je okamžitý failover.

## 7. Multi-AZ DB instance deployment

Klasický Multi-AZ DB instance model má primary a synchronous standby v inej AZ.

Standby:

- poskytuje failover support,
- neobsluhuje read traffic,
- je spravovaný RDS.

Použitie:

- high availability,
- planned maintenance resilience,
- host/storage/AZ failure recovery.

Multi-AZ standby nie je read-scaling solution.

Failover môže nastať pri:

- host impairment,
- network loss,
- storage failure,
- maintenance,
- customer-triggered reboot/failover,
- configuration modification podľa operation.

## 8. Multi-AZ DB cluster deployment

Multi-AZ DB cluster používa writer a dve readable DB instances v troch AZ pri podporovaných engines/configurations.

Vlastnosti:

- writer endpoint,
- reader endpoint,
- readable standbys,
- rýchlejší failover target model než klasický single-standby pattern v typických podmienkach,
- odlišné instance/storage requirements a cost.

Nezamieňaj Multi-AZ DB cluster s Aurora clusterom; ide o odlišné produkty a architecture contracts.

## 9. Read replicas

Read replica používa asynchronous replication zo source database.

Use cases:

- read scaling,
- reporting,
- geograficky bližšie reads,
- migration,
- DR primitive pri promotion workflowu.

Read replica nie je automaticky HA standby primary database.

Riziká:

- replication lag,
- stale reads,
- replay error,
- source load,
- promotion mení topology a recovery contract,
- application musí vedieť oddeliť read/write endpoints.

Monitoring lag je business consistency requirement, nie iba infrastructure metric.

## 10. Multi-AZ vs read replica

| Vlastnosť | Multi-AZ standby | Read replica |
|---|---|---|
| Primárny účel | HA/failover | read scaling/DR primitive |
| Replication | synchronous alebo managed HA model podľa deploymentu | asynchronous |
| Read traffic | nie pri klasickom standby; áno pri Multi-AZ DB cluster readers | áno |
| Automatic failover target | áno | typicky nie ako bežný source failover mechanismus |
| Stale reads | nie pre primary endpoint semantics | možné podľa lag |

Správny návrh môže používať obe vrstvy.

## 11. Automated backups

Automated backups poskytujú point-in-time recovery v rámci configured retention a engine capabilities.

Obsahujú:

- periodic storage snapshots,
- transaction logs potrebné pre PITR,
- retention-managed recovery window.

Over:

- retention period,
- earliest/latest restorable time,
- backup window,
- storage impact,
- encryption,
- Region/account recovery requirements,
- deletion behavior.

PITR vytvára novú DB instance/cluster. Neprepíše existujúcu database „na mieste“.

## 12. Manual snapshots

Manual snapshot zostáva, kým ho explicitne neodstrániš podľa policy.

Použitie:

- release checkpoint,
- long-term retention,
- migration,
- cross-Region/account copy,
- isolated restore test.

Snapshot obsahuje database storage state, nie automaticky všetky surrounding dependencies:

- users/secrets mimo DB,
- DNS/application config,
- Security Groups,
- parameter groups,
- IAM roles,
- external object storage,
- downstream systems.

## 13. Backup consistency

RDS koordinuje engine/storage backup podľa service behavioru, ale application business consistency môže vyžadovať ďalšie kroky.

Príklady:

- coordinated snapshot s external object store,
- pause alebo checkpoint queue consumers,
- capture schema migration version,
- preserve encryption keys a secrets,
- document application release compatibility.

Database restore sám neobnoví distributed business transaction naprieč ďalšími services.

## 14. Storage

RDS storage options závisia od engine a deployment modelu.

Dimensions:

- allocated storage,
- storage type,
- provisioned IOPS,
- throughput,
- storage autoscaling,
- maximum storage threshold.

Storage autoscaling zvyšuje allocated storage pri nedostatku capacity podľa service rules. Nezmenšuje ju automaticky a nevyrieši zlý query/index alebo transaction-log growth model.

Storage full môže zablokovať writes, maintenance alebo replication. Alarmuj s headroomom, nie až pri 100 %.

## 15. Parameter groups

DB parameter group definuje engine configuration.

Parameters môžu byť:

- dynamic,
- static/pending reboot,
- engine/version specific.

Zmena custom parameter group nemusí ovplyvniť všetky instances okamžite.

Pred zmenou:

- over parameter scope a units,
- testuj na rovnakom engine version,
- zachovaj previous group/version,
- sleduj `pending-reboot`,
- vyhodnoť memory/connection dopad.

## 16. Option groups

Option groups povoľujú engine-specific features pre vybrané engines.

Option môže:

- vyžadovať restart,
- vytvoriť network/security dependency,
- byť permanentná alebo ťažko odstrániteľná,
- meniť licensing/cost.

Používaj engine-specific dokumentáciu.

## 17. Maintenance a upgrades

RDS vykonáva service maintenance a umožňuje engine upgrades podľa support policy.

Rozlišuj:

- minor version upgrade,
- major version upgrade,
- OS/platform maintenance,
- certificate rotation,
- parameter/option changes,
- instance/storage modification.

Maintenance window je preferovaný čas, nie absolútna garancia, že urgentná security alebo retirement action nikdy nenastane mimo neho.

Pred upgrade-om:

- over extension/plugin compatibility,
- parameter groups,
- application drivers,
- deprecated features,
- read replicas,
- backup/snapshot,
- rollback alebo restore path,
- downtime/failover behavior.

## 18. Blue/green deployments

RDS Blue/Green Deployments pri podporovaných engines a configurations vytvára synchronizované staging environment pre zmenu a controlled switchover.

Vhodné pre:

- major/minor upgrades,
- parameter changes,
- schema/application validation,
- reduced-downtime cutover.

Nie je to automatická business rollback garancia. Po writes do green environmentu môže návrat na blue vyžadovať data reconciliation.

Over current engine/Region limitations.

## 19. Encryption at rest

RDS encryption používa KMS key pre storage, snapshots, backups a replicas podľa service modelu.

Dôležité:

- encryption sa typicky volí pri creation,
- encrypted snapshot copy môže použiť iný key,
- cross-account restore potrebuje snapshot a KMS permissions,
- key disable/deletion môže znemožniť database access alebo recovery,
- AWS-managed a customer-managed keys majú odlišný governance model.

KMS key je súčasť recovery dependency graphu.

## 20. Encryption in transit

Používaj TLS a over server certificate.

Application musí mať:

- aktuálny RDS CA bundle/trust,
- hostname verification,
- driver podporujúci TLS policy,
- certificate rotation process.

`sslmode=require` bez identity verification môže byť slabší contract než full certificate/hostname validation podľa drivera.

## 21. Authentication

Možnosti závisia od engine:

- database-native users/passwords,
- IAM database authentication,
- Kerberos/Directory integration pri podporovaných use cases,
- Secrets Manager rotation.

IAM DB auth používa krátkodobý token, ale database authorization stále riadi database account/privileges.

Nepoužívaj master user ako application runtime identity.

## 22. Secrets rotation

Rotation musí koordinovať:

- database credential change,
- secret version stages,
- connection-pool refresh,
- application retry,
- rollback/failure handling.

Chybná rotation môže vytvoriť split state: database má nové heslo, application číta starú secret version.

Testuj rotation ako workflow, nie iba Lambda success status.

## 23. RDS Proxy a connection pooling

RDS Proxy alebo application pool môže znížiť connection churn a chrániť database pri bursty/serverless clients.

Trade-offy:

- additional cost,
- transaction/session pinning,
- authentication integration,
- failure behavior,
- observability layer navyše.

Connection proxy nevyrieši pomalé queries ani príliš vysokú concurrent transaction demand bez capacity planningu.

## 24. Connections

Database connection limit závisí od engine, instance memory a configuration.

Monitoruj:

- current connections,
- active vs idle,
- connection creation rate,
- pool size per application instance,
- transaction duration,
- lock wait,
- failover reconnect storm.

Príklad nebezpečného scalingu:

```text
100 application instances × pool 100
= až 10 000 DB connections
```

Auto Scaling application môže preťažiť database aj pri nízkej CPU.

## 25. Query performance

Infrastructure scaling nenahrádza database engineering.

Analyzuj:

- slow queries,
- indexes,
- execution plans,
- locks/deadlocks,
- transaction duration,
- buffer/cache hit,
- temp/sort usage,
- I/O latency,
- vacuum/maintenance podľa engine,
- replication lag.

Vertical scale môže dočasne maskovať regresiu.

## 26. Monitoring vrstvy

### CloudWatch metrics

Napríklad:

- CPUUtilization,
- FreeableMemory,
- FreeStorageSpace,
- DatabaseConnections,
- Read/WriteIOPS,
- Read/WriteLatency,
- DiskQueueDepth,
- ReplicaLag,
- Network throughput.

### Enhanced Monitoring

Poskytuje OS-level metrics z managed host perspective podľa configured interval a permissions.

### Database performance telemetry

Performance Insights alebo aktuálne database observability capabilities poskytujú query/load dimensions podľa engine/service version.

### Logs

Export engine logs do CloudWatch Logs podľa supportu:

- error,
- slow query,
- general/audit,
- PostgreSQL logs,
- agent/upgrade logs podľa engine.

### Events

RDS events signalizujú failover, backup, maintenance, restart, storage a configuration zmeny.

## 27. Event subscriptions

Event subscriptions môžu publikovať notifications pre:

- DB instance,
- cluster,
- snapshot,
- parameter/security group,
- failover/maintenance categories.

Event nie je vždy alarm. Koreluj s metrics, CloudTrail a application impactom.

## 28. High availability test

Kontrolovaný failover test má overiť:

- DNS refresh,
- connection pool recovery,
- transaction retry,
- application health,
- monitoring/alerting,
- event delivery,
- replica/read routing,
- recovery time.

Failover počas nízkeho trafficu bez application telemetry nepreukazuje production readiness.

## 29. Disaster recovery

Možnosti:

- snapshot copy do iného Regionu/accountu,
- cross-Region read replica pri podporovanom engine,
- AWS Backup copy,
- logical dumps/engine-native backup,
- pilot-light/warm-standby application environment.

DR potrebuje:

- KMS keys,
- subnet/security reconstruction,
- parameter/option groups,
- secrets,
- DNS cutover,
- application config,
- runbook a restore test.

Multi-AZ nie je cross-Region DR.

## 30. Deletion protection a final snapshot

Deletion protection znižuje riziko accidental delete cez API/console.

Pri delete operation over:

- final snapshot,
- automated-backup retention,
- read replicas,
- cross-Region dependencies,
- secrets a DNS,
- compliance retention,
- KMS key lifecycle.

Deletion protection nie je ochrana pred authorized data corruption alebo `DROP TABLE`.

## 31. Troubleshooting connection timeout

Postup:

```text
endpoint/port/Region
→ DNS resolution
→ client route
→ DB subnet/route
→ Security Group source
→ NACL return path
→ DB status/listener
→ TLS/authentication
```

Typické príčiny:

- application SG nie je povolená v DB SG,
- wrong VPC/peering/TGW route,
- private endpoint z internetu,
- NACL blokuje return traffic,
- DNS cached old address počas failover,
- DB modifying/rebooting,
- connection limit/backlog.

## 32. Troubleshooting authentication failure

Rozlišuj:

- network connection funguje, ale credentials sú zlé,
- database user nemá privilege,
- IAM token expired alebo wrong Region/hostname,
- TLS requirement,
- Secrets Manager rotation mismatch,
- database account locked/expired,
- proxy auth configuration.

Test administratívnym superuserom môže maskovať application privilege problém.

## 33. Troubleshooting high CPU

Postup:

- koreluj DB load a queries,
- over connection count,
- slow/expensive plans,
- locks a retries,
- maintenance tasks,
- replica lag,
- application release,
- instance class saturation.

Nezvyšuj instance class skôr, než zachováš query evidence. Scale-up môže zmeniť symptom a stratiť root cause.

## 34. Troubleshooting high I/O latency

Over:

- storage type/IOPS/throughput,
- queue depth,
- read/write mix,
- large scans,
- checkpoints/flush,
- backup window,
- storage full/headroom,
- instance EBS/network capacity,
- burst behavior.

Query plan alebo missing index môže byť primárnou príčinou infrastructure metricu.

## 35. Troubleshooting replica lag

Over:

- write volume,
- long transactions,
- replica compute/storage capacity,
- network/Region latency,
- replication errors,
- read workload na replica,
- engine-specific apply threads,
- maintenance/reboot.

Application musí definovať maximum tolerované stale read. `ReplicaLag=30s` je business problém iba podľa konkrétneho use case.

## 36. Troubleshooting failover

Zachovaj:

- RDS events,
- old/new AZ,
- DNS resolution timeline,
- application connection errors,
- pool/retry behavior,
- transaction failures,
- failover duration,
- replica/standby state.

Po failover-e over business writes a idempotency, nie iba TCP connection.

## 37. Troubleshooting storage full

Immediate actions závisia od engine a safety:

- zastaviť nekontrolovaný growth,
- zvýšiť storage/max threshold,
- odstrániť bezpečne nepotrebné data/logs podľa engine,
- optimalizovať retention,
- obnoviť service headroom.

Nemaž database files priamo. Managed host/filesystem nie je customer-administered storage.

## 38. Cost model

Cost drivers:

- instance hours,
- Multi-AZ/reader instances,
- allocated storage,
- provisioned IOPS/throughput,
- backup storage nad included allowance,
- snapshot copy/data transfer,
- Enhanced Monitoring/logs,
- RDS Proxy,
- licenses,
- cross-Region replication.

Right-sizing musí brať do úvahy failover capacity a peak, nie iba priemernú CPU.

## 39. SOA-C03 mapovanie

- **Domain 1** — RDS metrics, logs, events, query/performance diagnosis,
- **Domain 2** — Multi-AZ, backups, PITR, read replicas a DR,
- **Domain 3** — parameter groups, maintenance, upgrades, blue/green, automated provisioning,
- **Domain 4** — KMS, TLS, IAM DB auth, Secrets Manager a least privilege,
- **Domain 5** — subnet groups, Security Groups, DNS endpoints a connectivity.

Praktické drilly:

- SG blokuje application,
- failover a stale connection pool,
- storage autoscaling max threshold,
- read-replica lag,
- KMS-denied snapshot restore,
- secret rotation mismatch,
- parameter change pending reboot.

## 40. Anti-patterny

### Multi-AZ považované za read scaling

Klasický standby neobsluhuje reads.

### Read replica považovaná za synchronous failover

Replication lag a promotion sú odlišné od Multi-AZ HA.

### Endpoint IP uložená v configuration

Failover mení DNS mapping.

### Master user ako application account

Zväčšuje blast radius.

### Backup bez restore testu

RPO/RTO a dependency completeness nie sú overené.

### Maximum connection pool na každej auto-scaled instance

Preťaží database pri scale-out-e.

### Scale-up namiesto query analýzy

Maskuje regressions a zvyšuje cost.

### Multi-AZ považované za DR

Nepokrýva Region, logical corruption ani account compromise.

## 41. Kontrolné otázky

1. Aký je rozdiel medzi Single-AZ, Multi-AZ DB instance a Multi-AZ DB cluster?
2. Ako sa líši Multi-AZ standby a read replica?
3. Ako funguje endpoint počas failover-u?
4. Čo poskytujú automated backups a PITR?
5. Prečo snapshot nie je celý application recovery plan?
6. Aký je rozdiel medzi parameter a option group?
7. Ktoré layers preveríš pri connection timeout-e?
8. Ako application pool ovplyvní failover a scaling?
9. Prečo storage autoscaling nevyrieši query regression?
10. Čo musí obsahovať cross-Region RDS DR test?

## Glossary impact

Relevantné pojmy: Amazon RDS, DB instance, DB subnet group, RDS endpoint, Single-AZ, Multi-AZ DB instance deployment, Multi-AZ DB cluster, standby replica, read replica, replication lag, automated backup, point-in-time recovery, DB snapshot, parameter group, option group, storage autoscaling, RDS failover, IAM database authentication, RDS Proxy a Blue/Green Deployment.

## Oficiálna dokumentácia

- [Amazon RDS User Guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html)
- [Multi-AZ deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html)
- [Multi-AZ DB instance deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html)
- [Read replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html)
- [Backups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html)
- [Monitoring Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Monitoring.html)
- [RDS security](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.html)
