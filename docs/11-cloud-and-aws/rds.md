# Amazon RDS

Amazon Relational Database Service (RDS) presúva časť database infrastructure a lifecycle responsibility na AWS, ale neodstraňuje database engineering. AWS spravuje host, vybrané storage/replication mechanizmy, backups, maintenance orchestration a failover podľa deployment modelu. Zákazník stále vlastní schema, transaction semantics, queries, indexes, users/privileges, connection pools, retry/idempotency, data classification, compatibility, recovery objectives a business validation.

RDS preto nie je „databáza bez prevádzky“. Je to managed control plane nad stále kritickým stateful data plane-om.

Dominantný lifecycle:

```text
business transaction intent
→ exact database release a endpoint subject
→ DNS, network a TLS connection
→ authentication a database authorization
→ session a transaction begin
→ reads/locks/writes/log records
→ commit alebo rollback outcome
→ synchronous HA a asynchronous read/DR replication
→ application acknowledgement
→ health, failover, scale alebo upgrade transition
→ backup/PITR/restore realization
→ data a business reconciliation
→ old topology/generation retirement
```

Najnebezpečnejší stav nie je vždy jednoznačné `connection failed`. Je ním **unknown commit outcome**: application odošle commit, writer ho durable vykoná, ale connection sa preruší pred potvrdením. Slepý retry potom môže vytvoriť duplicate payment aj keď RDS failover fungoval presne podľa service contractu.

## 1. Exact database subject

Atlas Payments používa database subject `DB-PAY-42`:

```text
account = 100000000042
Region = eu-central-1
engine = PostgreSQL-compatible RDS deployment
engine generation = PG-16-GEN-7

deployment model = Multi-AZ DB cluster
cluster = db-pay-prod-17
writer endpoint = db-pay-prod.cluster-xyz.eu-central-1.rds.amazonaws.com
reader endpoint = db-pay-prod.cluster-ro-xyz.eu-central-1.rds.amazonaws.com
writer instance = db-pay-prod-a / AZ-a
readers = db-pay-prod-b / AZ-b, db-pay-prod-c / AZ-c

DB subnet group generation = DBSUB-12
DB Security Group generation = SG-DB-14
parameter group generation = PGPAR-21
certificate/trust generation = RDS-CA-8
KMS key generation = KMS-DB-11
secret generation = SEC-DB-34
schema generation = SCHEMA-215

application fleet = payments-api release 7.15.0
connection path = application pool → RDS Proxy generation PROXY-9 → writer endpoint
transaction = payment P-884
idempotency key = pay-P884

business outcome =
  payment authorization and ledger row commit exactly once

forbidden outcomes =
  read-after-write routed to stale replica when consistency is required
  retry duplicates a committed payment after lost response
  failover is declared successful only because console says Available
  backup is accepted without restore and schema/business validation
  upgrade cutover leaves blue and green writable without authority
  application uses master user or hard-coded endpoint IP
```

Incident evidence musí obsahovať endpoint hostname a resolved IP timeline, actual writer/reader identities, engine/schema/parameter generation, session/transaction ID, application idempotency key, RDS events, connection-pool/proxy state, query/lock evidence, commit acknowledgement a business ledger result.

## 2. Connection path má viac nezávislých gates

Application request prejde cez:

```text
endpoint DNS
→ client route a database subnet path
→ DB Security Group/NACL
→ TLS handshake a hostname validation
→ authentication
→ database role/privileges
→ connection/session limits
→ transaction/query execution
→ commit/response
```

Symptómy zužujú failure boundary:

- timeout môže byť DNS, route, SG/NACL, failover, connection saturation alebo listener backlog;
- TLS error dokazuje, že transport sa dostal ďalej, ale trust/protocol contract zlyhal;
- password/token failure znamená, že network/listener pravdepodobne fungujú;
- `permission denied` je database authorization, nie Security Group;
- slow query alebo lock wait nie je automaticky storage/instance shortage.

Administratívny test z bastionu ako master user môže maskovať application role, proxy, secret, endpoint aj network context. Test sa vykonáva s exact production identity a pathom.

## 3. Endpoint je logical identity nad meniacim sa writerom

RDS endpoint je DNS name, ktorý service mapuje na current database resource. Pri Multi-AZ failover-e sa logical endpoint zachová, ale DNS mapping sa zmení na nový primary/writer.

Application musí:

```text
používať hostname, nie uloženú IP
→ rešpektovať primeraný DNS cache/TTL model
→ detegovať broken existing connections
→ vytvoriť nové connections
→ znovu autentizovať
→ bezpečne rozhodnúť o incomplete transaction
```

Connection pool môže držať stale sockets aj po DNS zmene. DNS refresh bez pool eviction nepomôže. Opačne, agresívne reconnectovanie všetkých application instances môže po failover-e vytvoriť connection storm a spomaliť recovery.

Writer endpoint sa používa pre writes a consistency-sensitive reads. Reader endpoint rozdeľuje connections medzi readable replicas podľa service semantics; nie je transaction-level guarantee čerstvosti. Application musí explicitne rozhodnúť, ktoré reads tolerujú replication lag.

## 4. Deployment model určuje HA a read contract

### Single-AZ

Jedna active DB instance v jednej AZ. Je vhodná iba keď workload akceptuje host/AZ/maintenance downtime a recovery z backupu alebo replacementu. Backup nie je okamžitý failover.

### Multi-AZ DB instance deployment

Klasický model používa primary a synchronously maintained standby v inej AZ. Standby je failover resource a typicky neobsluhuje application reads. Pri failure alebo podporovanej maintenance operation RDS presmeruje endpoint na standby.

```text
primary writer
→ synchronous standby state
→ failure detection
→ standby promotion
→ endpoint DNS change
→ application reconnect
```

Multi-AZ standby rieši availability, nie read scaling ani cross-Region DR.

### Multi-AZ DB cluster

Pri podporovaných engines/configurations používa writer a dve readable DB instances v troch AZs. Poskytuje writer a reader endpoint, readable standbys a odlišný failover/performance/cost model než single-standby deployment.

```text
writer in AZ-a
+ readable candidates in AZ-b/c
→ failure detection
→ eligible reader promotion
→ writer endpoint remap
→ remaining cluster topology recovery
```

Failover duration závisí aj od database activity, crash recovery a replica state. „Tri instances“ neznamenajú, že application connection pool a transaction retry sú pripravené.

### Aurora a RDS Custom

Aurora používa odlišný cluster/storage/replication architecture a nemožno naň mechanicky preniesť všetky RDS DB instance assumptions. RDS Custom vracia zákazníkovi väčšiu OS/database kontrolu a tým aj väčšiu operational responsibility. Táto kapitola používa common RDS principles a vždy vyžaduje engine/deployment-specific dokumentáciu.

## 5. Read replicas sú asynchronous data products

Read replica prijíma changes zo source asynchrónne. Je vhodná na read scaling, reporting, geografické reads, migration a niektoré DR promotion workflows.

```text
source commit
→ replication stream/log
→ network/queue
→ replica apply
→ read visibility
```

Replica lag znamená, že `SELECT` môže vrátiť starší state. Business tolerance sa líši:

- produktový katalóg môže tolerovať sekundy;
- stav práve vykonanej platby často nie;
- reporting môže tolerovať minúty, ale nie chýbajúci audit interval.

Read replica nie je automatický synchronous failover writer. Promotion mení topology, endpoint, data authority a často preruší pôvodnú replication relation. DR runbook musí definovať RPO, writer fencing, application cutover a failback/reconciliation.

## 6. Multi-AZ, read scaling a DR sú tri osi

| Požiadavka | Typický mechanismus | Čo sám nerieši |
|---|---|---|
| AZ/high-availability failover | Multi-AZ DB instance alebo Multi-AZ DB cluster | Region loss, logical corruption, account compromise |
| Read scaling | readable Multi-AZ cluster instances alebo read replicas | write HA semantics a fresh read guarantee |
| Point-in-time recovery | automated backups + transaction logs | okamžitý in-place rollback |
| Cross-Region DR | snapshot/backup copy, cross-Region replica alebo engine-specific strategy | application/network/DNS readiness |
| Low-downtime upgrade | Blue/Green Deployment pri supported model-e | business rollback po green writes |

„Máme Multi-AZ“ preto nie je odpoveď na RPO po `DROP TABLE`, ransomware credential misuse alebo Region-wide incident.

## 7. Transaction commit a unknown outcome

Relational transaction vytvára atomic engine-level boundary pre zahrnuté database changes. Application-level operation však môže zasahovať aj payment provider, queue, S3 receipt alebo downstream event.

```text
BEGIN
→ validate idempotency key
→ write payment/ledger/outbox
→ COMMIT sent
→ writer durably commits
→ acknowledgement returned
```

Ak connection zlyhá medzi durable commitom a acknowledgementom, client nevie, či commit prešiel. Bez idempotency/reconciliation:

```text
timeout
→ retry whole operation
→ second provider authorization alebo second ledger insert
→ duplicate side effect
```

Bezpečný pattern používa unique idempotency constraint, transactional outbox, provider request ID a read/reconcile pred retryom. RDS high availability znižuje infrastructure downtime, ale exactly-once business outcome musí navrhnúť application.

## 8. Connection pools a RDS Proxy

Každá application instance s vlastným veľkým poolom násobí total database connections:

```text
12 instances × pool 100 = 1 200 possible connections
24 instances po scale-out-e × 100 = 2 400
```

Database môže mať nízku CPU a zlyhávať na connection memory, process/thread limit, lock contention alebo authentication churn.

Application pool musí definovať:

- minimum/maximum per instance;
- connection lifetime a validation;
- idle timeout;
- acquisition timeout;
- failover eviction/reconnect;
- transaction/session state reset;
- total fleet budget.

RDS Proxy môže multiplexovať a zdieľať database connections, znížiť connection churn a pomôcť bursty/serverless clients. Pridáva však ďalšiu identity, endpoint, metric, cost a failure boundary. Session/transaction features môžu pin-nuť client k backend connection a znižovať multiplexing. Proxy neopraví slow query ani nekonečnú concurrent transaction demand.

Blue/Green a Proxy interaction má service-specific workflow; topology sa musí overiť pri vytvorení aj switchover-e, nie predpokladať podľa názvu endpointu.

## 9. Authentication a runtime identity

Možnosti závisia od engine a deploymentu:

- database-native user/password;
- IAM database authentication;
- Secrets Manager-managed credentials/rotation;
- directory/Kerberos integrations pri supported use cases.

IAM DB authentication vytvára krátkodobý authentication token, ale database role a grants stále rozhodujú authorization. Application nemá používať master user; runtime identity má iba required schema/actions.

TLS contract obsahuje current RDS CA bundle, hostname verification, driver support a certificate rotation. Nastavenie typu `require encryption` bez server identity validation môže byť slabšie než full trust/hostname verification.

## 10. Secret rotation je distributed state transition

Credential rotation mení database aj consumers:

```text
new database credential prepared
→ new secret version/stage
→ application/proxy obtains new value
→ new connections authenticate
→ old connections drain
→ old credential revoked
→ verification a cleanup
```

Failure môže vytvoriť split state: DB očakáva nové heslo, application číta starú version; alebo oba credentials zostanú platné bez expiry. Rotation Lambda success nepreukazuje, že application pool obnovil connections a starý credential je revoked.

Safe test používa exact application role, new connection, expected SQL privilege a forbidden privilege. Rollback musí rešpektovať, či database credential change už prebehla a ktoré clients držia staré sessions.

## 11. Subnet, Security Group a private access

DB subnet group poskytuje candidate subnets/AZs pre RDS placement a failover. Production potrebuje free IP headroom vo všetkých relevantných AZs, correct routes, DNS a SG/NACL path.

Database nemá byť public iba preto, že application/admin connectivity nie je navrhnutá. Bežný contract:

```text
application SG
→ DB SG TCP engine-port
→ private RDS endpoint
```

Admin access ide cez controlled bastion, SSM/port-forwarding, VPN alebo iný approved path. Public accessibility, subnet route a SG allow sú samostatné podmienky; flag sám nevytvorí ani neodstráni celý internet path.

## 12. Storage a capacity envelope

RDS storage options sa líšia podľa engine/deployment modelu. Capacity zahŕňa allocated storage, storage type, IOPS, throughput, transaction-log growth a instance storage/network bandwidth.

Storage autoscaling môže zvýšiť allocated storage do configured maximum. Nezmenšuje storage a neopraví:

- missing index/full table scans;
- long transactions zadržiavajúce logs/vacuum;
- runaway audit/temp data;
- zle nastavenú retention;
- instance I/O bandwidth limit.

Alarm musí používať headroom a growth rate. Pri 100 % full môže engine stratiť schopnosť writes, maintenance aj replication. Pri incident-e sa database files na managed hoste nemažú ručne; používa sa engine/service-safe remediation.

## 13. Query, lock a memory model

Infrastructure metrics sú následky workloadu. Query lifecycle:

```text
parse/plan
→ acquire locks/snapshot
→ read pages/index
→ compute/sort/temp
→ write/log/flush
→ commit
```

High CPU môže byť expensive plan, connection storm, vacuum/maintenance alebo retry amplification. High I/O latency môže byť storage cap, large scans, checkpoints alebo cold cache. Low CPU s vysokou latency môže znamenať lock wait alebo external I/O.

Pred scale-upom zachovaj query text/fingerprint, execution plan, wait events, locks, transaction duration, buffer/cache behavior a release timeline. Vertical scaling môže odstrániť symptom a zároveň zničiť discriminating evidence.

Read replica lag sa analyzuje cez source write volume, long transactions, apply capacity, network latency, replica read load a engine errors. Metric sa interpretuje cez business stale-read budget.

## 14. Parameter a option generation

Parameter group je versionovaný engine configuration input. Parameters môžu byť dynamic alebo vyžadovať reboot. Console association neznamená, že static parameter je runtime effective; sleduj pending-reboot a actual engine value.

Option groups pri vybraných engines aktivujú engine-specific features, ktoré môžu vytvoriť network, restart, licensing alebo irreversible compatibility constraints.

Safe change:

```text
engine/version-specific parameter intent
→ units/scope/default comparison
→ memory/connection/performance model
→ test on equivalent topology
→ new group generation
→ canary/apply/reboot or failover
→ runtime effective-value verification
→ query/business validation
```

Ručná zmena shared parameter group môže ovplyvniť viac DB resources. Immutable/new group generation zlepšuje rollback a provenance.

## 15. Automated backups, snapshots a PITR

Automated backups kombinujú snapshots a transaction logs tak, aby umožnili point-in-time recovery v retention window podľa engine/service contractu.

PITR vytvorí nový DB instance/cluster:

```text
select exact restore timestamp
→ restore base state + logs
→ create new DB resource
→ attach parameter/subnet/SG/KMS dependencies
→ verify schema/data
→ application reconciliation
→ controlled DNS/config cutover
```

PITR nie je in-place rewind. Existing broken database zostáva samostatný subject, kým ju operator explicitne neodstráni.

Manual snapshot je durable restore point s explicitným retention lifecycle-om. Snapshot nezahŕňa automaticky application secrets, DNS, SG, parameter/option groups, IAM roles, external S3 objects, queues ani release compatibility.

Backup consistency na business úrovni môže vyžadovať coordinated checkpoint s outbox/queue/external provider state. Database restore sám nevráti distributed transaction do jedného konzistentného momentu.

## 16. Restore acceptance

Restore experiment meria viac než `DB available`:

```text
backup/snapshot selection
→ KMS and permissions
→ resource creation
→ parameter/extension/schema compatibility
→ network/TLS/secret path
→ engine recovery
→ data checksum/count/invariants
→ read/write canary
→ application release compatibility
→ performance warmup
→ RPO/RTO verdict
```

Positive test overí payment lookup, idempotent write a outbox processing. Forbidden test overí, že old credential, public path, wrong schema writer alebo stale replica nemôže byť accepted production path.

Restore do isolated environment znižuje riziko, že test consumer odošle reálne emails/payments/events. Egress a credentials musia byť fenced.

## 17. Blue/Green Deployment

RDS Blue/Green Deployment pri supported engines/configurations vytvára synchronized green staging topology pre upgrades alebo configuration changes a poskytuje controlled switchover.

```text
blue production subject
→ green topology creation/synchronization
→ engine/parameter/schema/application validation
→ switchover preconditions
→ bounded write pause/cutover
→ endpoint/resource transition
→ application reconnect
→ green business acceptance
```

Blue/Green znižuje cutover downtime; nie je complete rollback. Po green writes sa blue neaktualizuje automaticky ako authoritative mirror pre arbitrary business changes. Návrat môže vyžadovať data reconciliation alebo nový forward recovery.

Schema migration musí byť kompatibilná s blue/green replication a application mixed-version window. Unsupported DDL, replication lag alebo long-running transaction môže blokovať/oddialiť switchover.

RDS Proxy a smart-driver support existujú v current service model-e, ale exact topology/limitations sa overujú pre engine a deployment. External dependencies, DNS caches a application pools stále potrebujú cutover test.

## 18. Maintenance a engine upgrades

Maintenance môže zahŕňať OS/platform patch, certificate rotation, instance/storage modification, minor alebo major engine upgrade. Maintenance window je scheduling preference, nie garancia, že urgentný service/security event nikdy nevznikne mimo nej.

Upgrade inventory:

- drivers a TLS trust;
- extensions/plugins/options;
- parameter families;
- deprecated behavior;
- schema/query compatibility;
- read replicas a replication;
- backup/restore path;
- downtime/failover;
- observability and rollback eligibility.

Major upgrade mení data/engine compatibility. Snapshot restore môže vrátiť starý resource, ale application/data writes po cutover-e môžu znemožniť jednoduchý reverse switch.

## 19. Encryption a key lifecycle

RDS encryption používa KMS pre storage, snapshots, backups a replicas podľa service modelu. KMS key je recovery dependency:

```text
DB encrypted under key generation K
→ automated backup/snapshot encrypted
→ copy/restore requires K or approved destination key
→ key disabled/deleted
→ production alebo recovery becomes inaccessible
```

Customer-managed key zlepšuje governance, cross-account control a audit, ale pridáva policy/grant/rotation/deletion lifecycle. Key deletion schedule musí byť blokovaný recovery-retention a legal requirements.

Encryption at rest nechráni pred authorized SQL corruption alebo overprivileged application. TLS zase chráni transport, nie correctness query.

## 20. Monitoring a evidence

| Vrstva | Evidence | Rozlišuje |
|---|---|---|
| Control plane | RDS events, CloudTrail, pending modifications | service transition od application symptomu |
| DNS/network | endpoint answers, Flow Logs, SG/NACL | failover mapping od path deny |
| Connection | connections, proxy metrics, auth logs | pool storm od engine query failure |
| Engine | logs, wait events, locks, plans | CPU/I/O symptom od workload cause |
| Storage/replication | free space, IOPS/latency, replica lag | capacity od consistency delay |
| Backup | restorable window, snapshot/KMS/status | backup existence od usable restore |
| Business | idempotency ledger, payment/outbox state | connection recovery od exactly-once outcome |

Enhanced Monitoring poskytuje OS-level perspective managed hostu podľa configuration. Database performance telemetry/Performance Insights capabilities poskytujú query/load dimensions podľa current engine/service supportu. Žiadna jedna metric neuzatvára transaction incident.

## 21. Connected failure — failover úspešný, payment outcome neznámy

### Symptóm

Po impairment-e writer instance RDS Multi-AZ DB cluster automaticky promovuje reader v AZ-b. RDS event a console ukazujú cluster `available`. Payments API má 90-sekundový spike `connection reset`/timeoutov. Po recovery business reconciliation nájde dve autorizácie pre payment `P-884`, ale iba jeden client request.

### Competing hypotheses

1. Failover trval dlhšie než application timeout.
2. DNS cache stále ukazovala old writer IP.
3. Existing pool connections neboli evicted.
4. RDS Proxy neprepol backend alebo sessions boli pinned.
5. New writer nebol ready alebo mal replication lag.
6. Transaction `P-884` rollbackla a retry bol legitímny.
7. Transaction commitla, ale acknowledgement sa stratilo.
8. Application retry nepoužil idempotency key/unique constraint.
9. External payment provider bol volaný mimo database transaction bez reconciliation.
10. Reader endpoint bol omylom použitý pre write/read-after-write.
11. Secret/TLS change blokovala nové connections.
12. Duplicate pochádza z queue redelivery, nie failoveru.

### Discriminating observations

| Observation | Čo rozlišuje |
|---|---|
| RDS event, old/new writer a DNS timeline | service failover od stale client state |
| pool/proxy backend connection IDs | DNS refresh od pinned/stale sessions |
| database transaction/audit log a unique key | rollback od durable first commit |
| provider request IDs | database duplicate od external duplicate call |
| API trace with idempotency key | client retry od queue redelivery |
| outbox/ledger state | committed transaction od lost acknowledgement |
| working fresh connection vs old pool socket | writer readiness od pool recovery |
| connection/CPU/lock metrics | reconnection storm od query bottleneck |

### Finding

Writer durable commitol ledger/outbox pre `P-884`, ale connection sa resetla pred commit acknowledgement. API layer klasifikovala timeout ako „transaction failed“ a retry-la celý workflow bez stable provider idempotency key. Database unique constraint chránila iba interný ledger insert; external provider authorization bol vykonaný pred constraint reconciliation a dostal nový request ID. RDS failover, DNS mapping aj writer promotion fungovali. Correctness failure vznikol v unknown-outcome a retry contracte.

### Evidence-preserving containment

- pozastaviť automatické retries pre affected unknown-outcome cohort;
- zachovať old/new writer events, DB logs, pool/proxy metrics, API traces a provider IDs;
- nezvyšovať SG alebo connection limits bez dôkazu;
- obmedziť reconnect storm cez backoff/jitter a connection budget;
- identifikovať payment operations bez durable client acknowledgement;
- nevykonávať manuálny replay pred reconciliation.

### Authoritative recovery

1. Reconciliovať `P-884` proti database ledgeru, outboxu a provideru.
2. Stornovať/kompenzovať duplicate provider authorization podľa business policy.
3. Zaviesť end-to-end stable idempotency key do provider requestu aj DB unique constraintu.
4. Pri timeout-e po commit boundary najprv query-nuť operation status, nie slepo replayovať.
5. Nastaviť pool validation/connection lifetime a failover-aware eviction.
6. Zaviesť bounded exponential backoff s jitterom a total retry budgetom.
7. Spustiť controlled failover test s in-flight transactions a exact telemetry.
8. Overiť reader/write endpoint separation a forbidden stale-read journey.

### Acceptance verdict

Failover je prijatý až keď:

- writer endpoint a fresh connections prejdú na promoted writer;
- stale pool sockets sa evictnú bez connection stormu;
- in-flight transaction s lost acknowledgement skončí jedným reconciled business outcome-om;
- payment idempotency funguje naprieč DB aj providerom;
- application obnoví SLO v measured RTO;
- read-after-write request nepoužije lagging replica;
- old writer/endpoint IP/master credential zostanú forbidden;
- failover event, alarm a runbook vytvoria dostatok evidence pre rozhodnutie.

## 22. Troubleshooting podľa boundary

### Connection timeout

```text
exact endpoint/port/Region
→ DNS answer a cache
→ route/subnet/TGW/peering
→ DB SG source
→ NACL return
→ RDS state/failover
→ connection/proxy saturation
```

### Authentication/authorization

```text
TLS trust/hostname
→ secret version alebo IAM token scope/expiry
→ database user existence
→ role/schema/table privileges
→ proxy auth mapping
```

### High latency/CPU/I/O

```text
query fingerprints a release timeline
→ waits/locks/connections
→ execution plans/indexes
→ buffer/temp/checkpoint behavior
→ storage and instance envelope
→ business throughput
```

### Replica lag/stale read

```text
source commit rate/long transactions
→ replication transport/apply
→ replica capacity and read load
→ endpoint routing
→ business freshness requirement
```

### Storage full

```text
growth source and rate
→ logs/temp/tables/indexes/transactions
→ autoscaling max and service state
→ safe engine cleanup/capacity increase
→ recurrence retention/query control
```

### Backup/restore

```text
exact restore timestamp/snapshot
→ KMS/permissions
→ new resource creation
→ schema/config/network/secret
→ data invariants
→ business canary and performance
→ cutover/fencing
```

## 23. Cost a architecture trade-off

Cost drivers zahŕňajú DB instances/readers, Multi-AZ topology, storage, IOPS/throughput, backup overage, snapshots/copies, cross-Region replication, RDS Proxy, Enhanced Monitoring/logs a commercial licenses.

Single-AZ šetrí standby/cluster capacity za vyšší outage/recovery risk. Multi-AZ cluster môže zlepšiť readable capacity a failover options, ale pridáva instances a topology complexity. Read replica znižuje read pressure, no pridáva stale-read a promotion lifecycle. Proxy môže znížiť connection churn, ale nie query demand a pridáva cost/pinning.

Right-sizing používa peak a failover capacity, memory/cache/connection behavior a successful transactions per cost, nie iba priemernú CPU.

## 24. Anti-patterny odvodené z lifecycle-u

- **Endpoint IP v configuration** — failover mení DNS mapping.
- **Console `Available` považované za application recovery** — pool, transaction a business state zostávajú.
- **Multi-AZ standby považovaný za read scaling** — classical standby reads neobsluhuje.
- **Read replica považovaná za synchronous writer failover** — lag/promotion menia consistency a authority.
- **Multi-AZ považované za DR** — nepokrýva Region/logical/account failure.
- **Retry každého timeoutu ako rollbacku** — commit outcome môže byť unknown.
- **Idempotency iba v jednej database tabuľke** — external provider side effect zostáva duplicate-prone.
- **Maximum pool na každej auto-scaled instance** — scale-out vytvorí connection storm.
- **Master user ako runtime identity** — zväčšuje blast radius.
- **Rotation Lambda success považovaný za credential closure** — consumers a old credential nemusia byť converged.
- **Storage autoscaling považované za query fix** — growth/scan/transaction príčina zostáva.
- **Scale-up pred query evidence** — symptom zmizne a root cause sa stratí.
- **Snapshot považovaný za application recovery** — dependencies/schema/business consistency chýbajú.
- **Blue/Green považované za automatický rollback** — green writes vytvoria data divergence.
- **Backup bez isolated restore testu** — RPO/RTO a usability nie sú overené.

## 25. Kontrolné otázky

1. Ktoré responsibilities AWS preberá v RDS a ktoré zostávajú application/database tímu?
2. Ako sa líši Single-AZ, Multi-AZ DB instance a Multi-AZ DB cluster?
3. Prečo read replica nie je automatický HA standby writer?
4. Ako endpoint/DNS a connection pool spolu ovplyvňujú failover?
5. Čo je unknown commit outcome?
6. Prečo idempotency musí pokryť aj external provider side effect?
7. Kedy RDS Proxy pomáha a kedy session pinning znižuje jeho efekt?
8. Ako sa rotation credentialu mení na distributed workflow?
9. Čo storage autoscaling vyrieši a čo nevyrieši?
10. Prečo backup/PITR vytvára nový resource namiesto in-place rewind?
11. Čo musí preukázať Blue/Green switchover?
12. Ako odlíšiš query regression od infrastructure shortage?
13. Ktoré positive a forbidden tests patria do restore acceptance?
14. Aký business verdict uzatvára Multi-AZ failover test?

## Glossary impact

Táto kapitola zavádza alebo spresňuje pojmy: database subject, writer-generation identity, endpoint remap, connection-pool failover, unknown commit outcome, business idempotency boundary, HA replication contract, readable-replica freshness contract, promotion authority, database restore generation, Blue/Green switchover subject, transaction reconciliation a database recovery acceptance verdict.

## Oficiálna dokumentácia

- [What is Amazon RDS?](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html)
- [Multi-AZ deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html)
- [Multi-AZ DB cluster deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html)
- [Failover for Multi-AZ DB instances](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.Failover.html)
- [Failover for Multi-AZ DB clusters](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts-failover.html)
- [Read replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html)
- [Automated backups and PITR](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html)
- [Blue/Green Deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/blue-green-deployments.html)
- [Amazon RDS Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html)
- [Monitoring Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Monitoring.html)
- [Security in Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: S3, EBS a EFS](s3-ebs-efs.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Route 53 a CloudFront →](route53-cloudfront.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
