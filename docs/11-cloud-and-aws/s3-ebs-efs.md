# S3, EBS a EFS

Amazon S3, Amazon EBS a Amazon EFS nie sú tri cenové varianty jedného disku. Každá služba realizuje iný data contract:

```text
S3  = object identity a API operation
EBS = zonálny block device a filesystem/database nad ním
EFS = zdieľaný NFS namespace a concurrent file operations
```

Správna storage voľba preto nezačína otázkou „koľko GiB potrebujeme“, ale otázkami: čo je authoritative data unit, ako sa zapisuje, kto ju zdieľa, kedy je commitnutá, akú consistency očakáva application, v ktorom failure domain-e existuje, ako sa chráni, ako sa obnoví a čím sa dokáže business použiteľnosť po restore.

Dominantný lifecycle:

```text
business data intent
→ data classification a authoritative owner
→ object / block / shared-file contract
→ exact storage identity a generation
→ write, flush alebo commit boundary
→ read/share/concurrency semantics
→ authorization a encryption path
→ durability, replication alebo snapshot state
→ retention a deletion lifecycle
→ restore/failover realization
→ application a business validation
→ old generation retirement a recovery closure
```

„Data existujú“ nie je acceptance verdict. S3 object môže mať nesprávnu current version, EBS volume môže byť `available`, ale výkonovo neinicializovaný, a EFS mount môže uspieť, hoci application nemá POSIX write permission.

## 1. Exact storage subject

Atlas Payments používa storage subject `DATA-PAY-42` pre payment `P-884`:

```text
business transaction = P-884
business owner = Atlas Payments
classification = confidential financial record
retention = 7 years podľa governed policy

S3 object contract:
  bucket = atlas-payments-evidence-prod
  key = receipts/2026/07/28/P-884.json
  version ID = VER-P884-7
  checksum = SHA256-...
  KMS key generation = KMS-DATA-11
  Object Lock retention generation = RET-9
  replication rule generation = REP-14

EBS block contract:
  workload = reconciliation-indexer-01
  volume = vol-recon-42
  AZ = eu-central-1a
  volume generation = EBS-22
  filesystem UUID = FS-8F2
  snapshot set = SNAP-20260728-04
  application checkpoint = IDX-LSN-991

EFS shared-file contract:
  filesystem = fs-pay-reports-17
  resilience = Regional
  access point = fsap-report-writers
  root path = /payment-reports
  enforced POSIX identity = uid/gid 2001
  mount-target generation = MT-12
  replication generation = EFS-REP-6

business outcomes =
  receipt version is immutable, retrievable and attributable
  reconciliation index can be restored within RTO with correct checkpoint
  report workers share only the governed POSIX namespace

forbidden outcomes =
  mutable key silently changes evidence identity
  S3 replication failure is mistaken for protected copy
  crash-consistent EBS snapshot is called application-consistent without proof
  restored EBS volume enters traffic before full-performance readiness
  EFS client escapes access-point root or writes as unintended UID
  backup job success is accepted without restore and business validation
```

Každý incident musí zachovať exact bucket/key/version, volume/snapshot/filesystem UUID, EFS filesystem/access-point/mount target, KMS key, policy generation, application checkpoint a timeline. Storage service name bez data identity je príliš široký incident subject.

## 2. Výber podľa data semantics

| Otázka | S3 | EBS | EFS |
|---|---|---|---|
| Authoritative unit | object + key + optional version ID | blocks; vyššiu štruktúru vytvára filesystem/database | file/directory v shared namespace |
| Access boundary | HTTP API/SDK | attached block device | NFS mount |
| Scope | bucket/object service v Regioni; vybrané classes môžu mať odlišný zonálny model | volume v jednej AZ | Regional alebo One Zone filesystem |
| Sharing | mnoho clients cez API | typicky single writer; Multi-Attach iba s cluster-aware software | mnoho concurrent NFS clients |
| Commit oracle | úspešná object operation + exact version/checksum | application commit/fsync + filesystem/block semantics | application close/fsync/locking + NFS/filesystem semantics |
| Recovery primitive | version, replication, Object Lock, backup | snapshot, copy, restore volume | AWS Backup, replication, file restore |
| Typický use case | artifacts, receipts, logs, media, backup, data lake | boot, database, transactional single-node filesystem | shared content, home/workspace, multi-instance POSIX files |

Ak application vyžaduje atomic directory rename, POSIX locks a random in-place writes, general-purpose S3 bucket nie je filesystem. Ak application vyžaduje zdieľané writes z viacerých AZs, zonálny EBS volume nie je správny default. Ak data sú immutable objects doručované cez CDN, EFS pridáva filesystem a network lifecycle bez potrebnej hodnoty.

## 3. S3 object lifecycle

S3 bucket obsahuje objects identifikované key. Object subject zahŕňa body, metadata, tags, checksum, encryption, retention a pri versioningu version ID.

```text
producer intent
→ bucket, key a write preconditions
→ authorization/KMS
→ PutObject alebo multipart upload
→ operation success
→ exact version ID/checksum
→ event/manifest publication
→ readers a downstream processing
→ lifecycle/replication/retention
→ restore alebo governed deletion
```

Bucket name je globálne unikátny v partition, ale bucket configuration a object service sú viazané na Region. Key je case-sensitive string; konzolové „folders“ sú prefix presentation, nie POSIX directories.

## 4. S3 consistency a multi-object publication

S3 poskytuje strong read-after-write consistency pre object writes/deletes a listing v general service contracte. To znamená, že úspešne zapísaný object môže byť následne čítaný a listovaný bez historického eventual-consistency workaroundu.

Neznamená to:

- multi-object ACID transaction;
- referential integrity medzi manifestom a data objects;
- atomic rename všeobecného object prefixu;
- synchronous cross-Region replication;
- ochranu pred logicky chybným overwrite;
- application-level exactly-once event consumption.

Konzistentný release alebo evidence set používa immutable keys a manifest:

```text
write immutable objects
→ verify checksum/version IDs
→ write immutable manifest generation
→ atomically change small pointer podľa application contractu
→ readers bind to manifest generation
```

General-purpose bucket rename typicky znamená copy + delete podľa client/workflow. S3 Express One Zone directory buckets podporujú `RenameObject`, ktorý atomicky premenuje object v rámci directory bucketu bez presunu dát. Táto capability sa nesmie zovšeobecniť na všetky S3 buckets ani na multi-object transaction.

## 5. S3 version identity

Versioning zachováva viac versions rovnakého key. Delete current key typicky vytvorí delete marker; staršie versions zostanú dostupné, kým ich neodstráni lifecycle alebo explicitná operation.

```text
logical key = receipts/.../P-884.json
current version = VER-P884-7
previous version = VER-P884-6
possible delete marker = DEL-3
```

Reader používajúci iba key prijíma current-version semantics. Audit alebo deterministic consumer má používať version ID/checksum/manifest. Versioning je recovery primitive, nie immutable backup: principal s permission odstrániť versions, lifecycle policy alebo account compromise môže recovery body zničiť.

Recovery po accidental delete musí identifikovať, či treba odstrániť delete marker, skopírovať staršiu version na novú current version alebo čítať konkrétny version ID. „Object sa znovu objavil“ nestačí; treba overiť správny obsah, metadata, retention a downstream references.

## 6. Object Lock a retention

S3 Object Lock poskytuje WORM retention pre konkrétnu object version:

- governance mode umožňuje oprávnenému principalu bypass podľa policy;
- compliance mode má prísnejší immutable contract počas retention;
- legal hold je samostatný hold state bez pevného expiry;
- retention period určuje `retain-until` boundary.

Object Lock nechráni logical key pred vznikom novej version alebo delete markeru; chránená version však zostáva zachovaná. Application môže stále čítať nesprávnu current version, ak reader nie je viazaný na evidence generation.

Compliance retention je governance rozhodnutie s costom a právnym dopadom. Chybne dlhá retention sa nedá „jednoducho opraviť“ administrátorským zásahom. Policy rollout potrebuje test bucket, ownership, deletion simulation a KMS/key-lifecycle alignment.

## 7. S3 replication nie je okamžitý commit

Same-Region Replication a Cross-Region Replication kopírujú eligible versions asynchrónne podľa rules. Replication contract obsahuje:

```text
source version ID
→ rule/filter eligibility
→ replication IAM role
→ source decrypt permission
→ destination bucket/KMS policy
→ destination write
→ replication status
→ lag/backlog/error evidence
```

Source `PutObject=200` neznamená, že replica už existuje. Object-level replication status môže byť pending, completed alebo failed. Failed KMS/policy path môže nechať source healthy a recovery copy neúplnú.

Replication môže preniesť corruption alebo malicious write. Ransomware/deletion protection preto kombinuje versioning, Object Lock, oddelený account, restricted delete permissions, backup a restore tests. Bi-directional replication a Multi-Region failover majú vlastné conflict/ownership semantics a vyžadujú explicitný write-authority model.

## 8. S3 storage classes a lifecycle

Storage class je latency, resilience, minimum-duration a retrieval-cost contract, nie iba cena za GiB. Classes zahŕňajú Standard, Intelligent-Tiering, infrequent-access variants, Glacier retrieval tiers a S3 Express One Zone pre špecifické low-latency zonálne use cases.

Lifecycle rules môžu transitionovať current/noncurrent versions, expire objects, odstraňovať noncurrent versions, delete markers a incomplete multipart uploads. Pri versioned bucket-e expiration current objectu typicky vytvorí delete marker; neodstráni automaticky všetky versions.

Safe lifecycle change:

```text
object/version inventory
→ access a restore requirement
→ replication/Object Lock/legal-hold state
→ transition/expiration simulation
→ minimum-duration a retrieval-cost model
→ canary prefix
→ positive restore test
→ broader policy
→ deletion evidence
```

Lifecycle completion nepreukazuje backup. Môže naopak odstrániť recovery versions podľa presne nakonfigurovanej policy.

## 9. S3 authorization, encryption a network path

S3 request verdict môže zahŕňať IAM identity policy, bucket policy, access-point policy, SCP/RCP, Block Public Access, Object Ownership, VPC endpoint policy, ACL legacy behavior a KMS policy/grant.

```text
caller/session
→ exact action
→ bucket alebo object ARN
→ request context/network endpoint
→ S3 policy graph
→ KMS encrypt/decrypt path
→ object operation
```

`ListBucket` používa bucket resource a prefix conditions; `GetObject` používa object ARN. Broad admin test môže maskovať application role, endpoint alebo KMS failure.

Bucket-owner-enforced Object Ownership a policy-based access znižujú ACL complexity. Block Public Access je guardrail, nie dôkaz private business isolation. Authorized destructive API call zostáva autorizovaný, ak version/retention/backup controls chýbajú.

Gateway VPC endpoint môže odstrániť NAT dependency pre supported VPC traffic, ale route a endpoint policy sa stávajú ďalším pathom. Interface endpoint/access point/Multi-Region Access Point menia DNS, policy a source context; treba ich zahrnúť do exact request subjectu.

## 10. Multipart, events a idempotency

Multipart upload umožňuje paralelné parts a retry. Object nie je publikovaný ako complete object, kým `CompleteMultipartUpload` neuspeje. Abandoned uploads spotrebúvajú storage; lifecycle abort policy patrí do cost baseline-u.

S3 event consumer musí tolerovať duplicate delivery, retry, ordering hranice a partial failure. Consumer identity používa bucket, key, version ID, event/sequencer údaje podľa event contractu a vlastný idempotency ledger.

```text
object version committed
→ event delivered možno viackrát
→ consumer deduplicates exact version
→ business processing
→ durable acknowledgement
```

Key-only deduplication je chybná, ak rovnaký key môže mať viac versions. Event notification nie je distributed transaction s downstream database.

## 11. Connected S3 failure — správny key, nesprávna evidence version

### Symptóm

Audit reader načíta `receipts/2026/07/28/P-884.json`, ale checksum sa nezhoduje s payment ledgerom. Bucket versioning aj Object Lock sú enabled a replication dashboard je prevažne zelený.

### Competing hypotheses

1. Producer zapísal nesprávny payload.
2. Reader používa wrong bucket/account/Region.
3. Mutable key bol overwrite-nutý novou current version.
4. Delete marker alebo restore workflow zmenil current semantics.
5. KMS/decryption transformuje alebo blokuje content.
6. Replication destination zaostáva alebo má failed version.
7. Cache/proxy vracia starú representation.
8. Event consumer spracoval duplicate alebo inú version.
9. Manifest odkazuje na key bez version ID.

### Discriminating observations

| Observation | Rozlišuje |
|---|---|
| `HeadObject/GetObject` s exact version ID | current-key drift od immutable version integrity |
| version inventory a timestamps | overwrite/delete-marker/restore sequence |
| checksums a producer transaction ID | producer corruption od reader selection |
| CloudTrail data event | kto vytvoril každú version/delete marker |
| replication status per version | source correctness od incomplete recovery copy |
| manifest generation | key-only reference od version-bound publication |
| consumer idempotency ledger | duplicate delivery od wrong object selection |

### Finding

Recovery script po accidental delete odstránil delete marker a následne skopíroval starú `VER-P884-6` na rovnaký key. Tým vytvoril novú current version s historickým payloadom. Object Lock zachoval všetky versions správne, ale reader a manifest používali iba key, nie version ID. Recovery primitive fungoval; publication contract bol nejednoznačný.

### Recovery a acceptance

- zachovať version inventory, CloudTrail a manifest evidence;
- zastaviť consumers viazané iba na current key;
- vybrať authoritative `VER-P884-7` podľa payment ledgeru a checksumu;
- publikovať nový immutable manifest s version ID/checksumom;
- spracovať exact version idempotentne a reconciliovať downstream;
- overiť replica status tej istej version;
- forbidden test: historická/new wrong version nesmie byť prijatá ako P-884 evidence;
- zmeniť restore runbook tak, aby obnovoval explicitnú generation, nie „najviditeľnejší key“.

## 12. EBS block lifecycle

EBS volume poskytuje zonálny block device. AWS spravuje volume service, ale partition table, filesystem, database layout, flush, consistency a mount lifecycle zostávajú customer/application responsibility.

```text
volume create/restore v exact AZ
→ attach k compatible instance
→ device/NVMe identification
→ partition/filesystem alebo database layout
→ mount podľa UUID
→ application writes/fsync/checkpoint
→ detach/modify/snapshot
→ restore a initialization
→ filesystem/application validation
```

Volume musí byť v rovnakej AZ ako attached EC2 instance. Multi-AZ recovery vytvára nový volume zo snapshotu alebo iného replication/backup workflowu v cieľovej AZ; pôvodný volume sa „nepresunie“ ako shared regional disk.

## 13. Device identity a mount

Console block-device name nemusí byť guest OS device name, najmä pri Nitro/NVMe. Persistent mount používa filesystem UUID/label a validovaný device mapping.

Safe first-use workflow:

```text
attach
→ identify exact volume serial/device
→ inspect existing signatures
→ partition only when intended
→ create filesystem only for empty volume
→ mount
→ verify owner/options/capacity
→ persist `/etc/fstab` by UUID
```

Automatické `mkfs` na „novom device path-e“ môže zničiť restored data, ak path ordering sa zmenil. Clone môže obsahovať duplicate filesystem UUID; mount automation musí rozlišovať origin a clone identities.

Pred detachom sa zastavia writes, flushnú buffers, filesystem sa unmountne a application checkpoint sa zachová. Force detach je containment nástroj s corruption/concurrent-writer rizikom, nie bežný migration step.

## 14. EBS performance envelope

Volume performance závisí od volume type, provisioned IOPS/throughput, I/O size, queue depth, latency, initialization a EC2 instance EBS bandwidth/limits.

```text
application I/O pattern
→ filesystem/database scheduling
→ guest block queue
→ volume IOPS/throughput envelope
→ instance EBS bandwidth
→ observed latency a business throughput
```

`gp3` umožňuje nastavovať size, IOPS a throughput relatívne nezávislo v service limits. `gp2` viaže časť performance/burst modelu na size. `io1/io2` cielia provisioned-IOPS workloads; HDD variants slúžia najmä sekvenčnému throughputu a nie sú boot volumes.

Provisioned 20 000 IOPS nepomôže, ak instance limit, single-threaded application, small queue alebo throughput cap blokuje path. Vysoký `DiskQueueDepth` môže byť príčina alebo dôsledok; koreluje sa s latency, I/O size, throughput a query/application trace.

## 15. Elastic Volumes

Podporovaný EBS volume možno za behu meniť v dimensions ako size, type, IOPS alebo throughput. Control-plane modification však nemení automaticky partition a filesystem visible size.

```text
ModifyVolume accepted
→ volume modification state
→ OS sees larger block device
→ partition resize podľa layoutu
→ filesystem resize
→ application capacity verification
```

Volume nemožno rovnakým spôsobom zmenšiť. Zmenšenie typicky znamená nový smaller volume, filesystem/data migration, validation a cutover. Increase bez filesystem step-u vytvorí false-green: AWS ukazuje väčší volume, application stále hlási starú kapacitu.

## 16. Snapshots a consistency

EBS snapshot je point-in-time block snapshot volume-u. Snapshot service dokáže obnoviť blocks, ale nevie automaticky, či vyššia application transakcia bola v konzistentnom bode.

- crash-consistent snapshot zodpovedá náhlej strate napájania v capture momente;
- application-consistent snapshot používa flush/quiesce/database checkpoint alebo engine-native workflow;
- multi-volume application potrebuje coordinated logical moment naprieč volumes.

```text
pause alebo coordinate writes
→ flush filesystem/database buffers
→ capture application checkpoint/LSN
→ create coordinated snapshot set
→ resume writes
→ record release/schema/KMS metadata
```

Snapshot `completed` dokazuje durable snapshot creation, nie boot, mount, recovery, schema compatibility ani business usability. Restore test je samostatný experiment.

Snapshots sú regional recovery resources a možno ich kopírovať/share-ovať podľa encryption a permissions. Cross-account/Region recovery potrebuje snapshot permission, customer-managed KMS policy/grant a reconstructed network/application dependencies.

## 17. Restore initialization a time-to-performance

Volume vytvorený zo snapshotu môže načítavať blocks pri prvom access-e. Control-plane state `available` preto neznamená plnú predvídateľnú read latency.

Možnosti:

- manual pre-read/initialization;
- Fast Snapshot Restore enabled pre konkrétny snapshot–AZ contract;
- EBS Provisioned Rate for Volume Initialization pri podporovanom create-volume workflowe.

Provisioned initialization rate a FSR majú service limits, cost a unsupported environments/copy caveats. Ak sa explicitne nastaví initialization rate, restore používa tento contract namiesto predpokladu, že FSR automaticky vyhrá.

Recovery RTO obsahuje:

```text
snapshot discovery
+ volume creation
+ block initialization strategy
+ attach/mount/fsck/recovery
+ application warmup
+ data/business validation
→ usable recovery time
```

## 18. Encryption a KMS dependency

EBS encryption chráni data at rest, snapshots a supported instance-volume path. KMS key lifecycle ovplyvňuje launch, restore, snapshot copy, ASG replacement a cross-account recovery.

`CreateVolume` alebo EC2 launch môže zlyhať, hoci snapshot permission je správna, ak principal/service nemá KMS grant alebo key je disabled/pending deletion. Recovery inventory musí uchovávať key ARN, policy generation, grant model a destination-account strategy.

Encryption neoveruje filesystem identity ani application correctness. Principal s block accessom cez authorized instance môže data logicky poškodiť.

## 19. Multi-Attach a fencing

EBS Multi-Attach umožňuje podporovaným Provisioned IOPS volumes pripojenie k viacerým compatible instances v rovnakej AZ. Nezmení bežný filesystem na cluster filesystem.

Concurrent writers potrebujú:

```text
cluster-aware filesystem/application
+ distributed locking
+ membership/quorum
+ fencing
+ failure recovery
```

Bez fencing môže partitioned node pokračovať v writes a poškodiť shared blocks. ext4/xfs mounted read-write na viacerých independent hosts bez cluster contractu je corruption design.

## 20. Connected EBS failure — volume `available`, RTO nesplnené

### Symptóm

Po strate reconciliation hostu automation vytvorí `vol-recon-restore-43` zo snapshotu `SNAP-20260728-04`. Volume je `available`, attach a mount uspejú a application health endpoint vracia `200`. Pri production query však p95 latency stúpne z 40 ms na 18 s a queue backlog rastie.

### Competing hypotheses

1. Snapshot obsahuje inconsistent filesystem/index.
2. Wrong snapshot/checkpoint bol obnovený.
3. Volume type/IOPS/throughput sa líši od source.
4. EC2 instance má nižší EBS bandwidth.
5. Restored blocks sú lazy-initialized.
6. Filesystem recovery alebo errors blokujú I/O.
7. Application cache je cold.
8. Query/index regression nie je storage problém.
9. KMS/decrypt path pridáva chybu alebo blok.
10. Health endpoint netestuje production access pattern.

### Discriminating observations

| Observation | Rozlišuje |
|---|---|
| snapshot ID + application LSN/checkpoint | wrong restore point od performance issue |
| source/restore volume and instance limits | configuration drift od initialization |
| initialization progress/type | cold blocks od provisioned full-performance pathu |
| per-block first-read vs repeated-read latency | lazy loading od persistent bottlenecku |
| `iostat`, queue, throughput a EBS metrics | block path od application compute |
| filesystem/database recovery logs | crash consistency od clean checkpoint |
| realistic query canary | shallow health od usable service |

### Finding

Automation zachovala volume type a checkpoint, ale pred incidentom nebol pre snapshot/AZ enabled FSR ani v restore requeste provisioned initialization rate. Health endpoint čítal malý hot metadata set; production reconciliation scan čítal mnoho cold blocks a spúšťal on-demand initialization. Restore bol funkčne mountnuteľný, ale nebol performance-ready a deklarované RTO meralo iba `volume=available`.

### Recovery a acceptance

- zachovať initialization, volume, instance a query evidence;
- obmedziť production traffic a retry/backlog amplification;
- prečítať/inicializovať required data range alebo vytvoriť nový volume s approved initialization rate;
- overiť application checkpoint a index integrity;
- spustiť production-representative query benchmark pred registration;
- zmeniť recovery plan na `time-to-full-performance`, nie `time-to-attach`;
- pre critical snapshots preflightovať FSR alebo provisioned-rate capacity/cost;
- forbidden test: cold/unvalidated volume nesmie vstúpiť do serving cohortu.

## 21. EFS shared-file lifecycle

EFS poskytuje managed NFS filesystem s shared namespace. Regional EFS redundantly stores data across Availability Zones v Regioni; One Zone používa odlišný zonálny resilience/cost contract.

```text
filesystem generation
→ mount targets v client VPC/AZs
→ DNS a network path
→ TLS/IAM client authorization
→ access-point identity/root
→ NFS mount
→ POSIX lookup/locking/read/write
→ backup/replication
→ failover/remount/restore
```

Mount target je ENI/network endpoint, nie kópia filesystem data. Regional design typicky vytvorí mount target v každej používanej AZ, aby clients používali zonálne vhodný path. Chýbajúci mount target môže vytvoriť mount failure alebo cross-AZ dependency podľa DNS/network contextu.

## 22. Mount path a authorization layers

Successful EFS use vyžaduje viac nezávislých gates:

```text
filesystem DNS
→ selected mount-target IP
→ route
→ SG TCP/2049
→ NACL return path
→ NFS client/mount helper
→ TLS in transit
→ IAM filesystem policy/client action
→ access point
→ POSIX UID/GID/mode/ACL
→ application operation
```

Timeout zvyčajne leží v DNS/network/SG/NACL alebo unreachable mount targete. `access denied by server` môže byť IAM/filesystem/access-point contract. `Permission denied` po úspešnom mount-e je často POSIX identity/mode. Tieto failures sa neopravujú jednou broad SG rule.

## 23. Access points a identity enforcement

EFS access point vytvára application-specific root path a môže enforce-nuť POSIX UID/GID pre operations. Client process môže lokálne bežať pod iným UID, ale EFS nahradí effective identity hodnotou access pointu podľa configuration.

```text
application IAM role
→ allowed ClientMount/ClientWrite through exact access point
→ enforced uid/gid 2001
→ root /payment-reports
→ POSIX permissions within namespace
```

Access point znižuje coupling na host UID a obmedzí namespace entry, ale nie je jediná security boundary. Filesystem policy, client IAM, SG, mount options a POSIX permissions musia byť konzistentné. Root squash/IAM root-access semantics a container user mapping treba testovať konkrétne.

## 24. Concurrent writes a file semantics

EFS poskytuje shared filesystem semantics, ale application stále vlastní locking, atomic file publication a conflict handling. Viacerí writers zapisujúci rovnaký report bez advisory/mandatory coordination môžu vytvoriť last-writer alebo partial-content problém podľa write patternu.

Safe publication pattern môže byť:

```text
write unique temporary file
→ fsync/close
→ validate checksum
→ atomic filesystem rename v rovnakom filesystem namespace
→ readers open final name
```

Tento pattern je file contract; nemožno ho preniesť na general S3 key bez analýzy. NFS close-to-open/cache semantics a client mount options ovplyvňujú visibility a locking; benchmark a correctness test musia používať rovnaký client/version/mount model ako production.

## 25. EFS performance a throughput

Performance závisí od throughput mode, performance mode, storage class, file size, metadata frequency, concurrency, NFS/client version a mount options.

```text
many tiny serial metadata operations
≠
few large parallel sequential reads
```

Bursting, Provisioned a Elastic throughput riešia odlišný demand model. Elastic throughput môže prispôsobiť throughput workloadu v service limits; neodstráni application serialization, directory contention alebo single-thread bottleneck.

Metrics sa korelujú s percent I/O limit, throughput, client connections, storage classes, mount logs a application latency. Benchmark generujúci veľké files nevysvetlí production workload s miliónmi tiny stat/rename operations.

## 26. EFS lifecycle, backup a replication

Lifecycle management môže presúvať cold data do infrequent-access alebo archive tiers podľa policy a current service supportu. Retrieval latency/cost sa stáva súčasťou application scan a backup behavioru.

AWS Backup poskytuje point-in-time recovery workflow. EFS replication asynchrónne synchronizuje source do destination filesystemu v rovnakom alebo inom Regioni/account modeli. Replication lag/status a KMS/IAM role sú recovery dependencies.

Failover na replica nie je iba DNS flip:

```text
verify replica status/RPO
→ stop alebo fence source writes
→ delete/change replication configuration podľa service workflowu
→ destination becomes writable
→ create/verify mount targets, SG, access points a DNS
→ remount clients
→ business validation
→ later re-establish reverse replication for failback
```

Pri failback initial sync a direction reversal majú vlastný čas a data-authority contract. Dva writable independent filesystems bez reconciliation nie sú automaticky bidirectional consistency.

## 27. Connected EFS failure — mount uspeje, writers nemajú správnu identity

### Symptóm

Po migrácii report workers na nový access point sa EFS mount cez TLS podarí vo všetkých AZs. Read operations fungujú, ale vytvorenie reportu končí `Permission denied`. SG, NACL a mount targets sú healthy.

### Competing hypotheses

1. Wrong filesystem alebo DNS answer.
2. Client nepoužíva intended access point.
3. IAM role nemá `ClientWrite`.
4. Filesystem policy denyuje role/access point.
5. Access point enforce-uje iný UID/GID než directory owner.
6. Root directory nebola vytvorená s expected ownership/mode.
7. Mount je read-only.
8. POSIX ACL alebo file mode blokuje write.
9. Container user namespace mení visible UID.
10. Stale mount používa old access-point generation.

### Discriminating observations

| Observation | Rozlišuje |
|---|---|
| mounted filesystem ID/access-point ARN/options | wrong mount generation od POSIX failure |
| successful TCP/TLS/NFS mount | network path od operation authorization |
| CloudTrail/IAM/filesystem policy | ClientMount/ClientWrite denial od POSIX denial |
| `id`, `stat`, ACL a effective enforced UID | local user od EFS operation identity |
| access-point root creation config | missing/wrong owner od existing directory drift |
| controlled create as exact worker role | broad admin success od application contract |

### Finding

Access point `fsap-report-writers` enforce-oval UID/GID `2001`, ale `/payment-reports` už existoval z predchádzajúcej generation s ownerom `1000:1000` a mode `0750`. Root creation settings sa aplikujú pri vytvorení chýbajúceho rootu; neprepisujú ownership existujúceho directory. Mount a read boli povolené, no POSIX write verdict správne zlyhal.

### Recovery a acceptance

- zachovať mount, policy, access-point a inode ownership evidence;
- nezväčšovať SG ani nepovoľovať `ClientRootAccess` bez potreby;
- určiť authoritative UID/GID a vykonať controlled ownership/mode migration;
- verify-nuť exact worker role cez access point v každej AZ;
- overiť atomic report publication a concurrent-writer behavior;
- forbidden test: iná application role/access point nemôže čítať ani zapisovať report namespace;
- pridať preflight, ktorý porovná root directory ownership s access-point generation.

## 28. Unified backup a recovery model

Backup primitive sa líši podľa storage contractu:

```text
S3:
version/object lock/replication/backup
→ select exact version
→ restore/publish manifest
→ consumer validation

EBS:
application checkpoint + snapshot set
→ create initialized volume in target AZ
→ mount/recover
→ realistic performance/business validation

EFS:
backup alebo replica
→ filesystem/access-point/mount-target reconstruction
→ permissions/remount
→ file and concurrency validation
```

Common recovery dependencies:

- KMS keys a grants;
- account/Region/AZ capacity;
- IAM/resource policies;
- DNS/network paths;
- application release/schema compatibility;
- retention and legal constraints;
- business reconciliation.

Backup job `Completed` je input do restore experimentu, nie recovery verdict. RPO sa meria posledným použiteľným business checkpointom, RTO časom po validated service, nie creation state-om storage resource-u.

## 29. Observability map

| Service | Configuration evidence | Runtime evidence | Business evidence |
|---|---|---|---|
| S3 | bucket/versioning/lifecycle/replication/Object Lock/policies | request metrics, CloudTrail data events, replication status, inventory | exact version/checksum processed once |
| EBS | volume type/size/IOPS/throughput/AZ/KMS/snapshot | attach state, initialization, IOPS/latency/queue, OS device/filesystem logs | restored checkpoint and production-pattern latency |
| EFS | filesystem class, mount targets, SG, policy, access points, replication | client connections, throughput/I/O limit, mount helper/NFS/POSIX logs | shared file correctness, isolation and recovery usability |

Storage metrics bez subject identity môžu agregovať healthy a failing cohorts. Snapshot count bez restore age/performance nevysvetľuje RTO. S3 bytes bez version count a lifecycle state maskujú retention cost.

## 30. Cost model ako lifecycle dôsledok

### S3

Cost tvoria stored bytes podľa class, requests, retrieval, minimum duration, lifecycle transitions, replication/transfer, versions, inventory/logging a abandoned multipart parts. Immutable versioning zlepšuje recovery, ale bez noncurrent lifecycle rastie cost.

### EBS

Cost tvoria provisioned GiB, IOPS/throughput, snapshots, cross-Region copy, FSR/provisioned initialization a unattached volumes. Overprovisioning môže byť recovery headroom; waste je capacity bez ownera a acceptance requirementu.

### EFS

Cost tvoria stored bytes/classes, throughput mode, access/retrieval, cross-AZ path, backups a replication. Shared filesystem znižuje duplicate file copies, ale metadata-heavy access a retained cold data môžu byť drahšie než object model.

Najnižšia cena za GiB nie je storage decision. Retrieval delay môže porušiť RTO, One Zone môže porušiť failure objective a lacný block volume môže porušiť latency budget.

## 31. Anti-patterny odvodené z contractov

- **S3 key považovaný za immutable evidence identity** — overwrite/current-version semantics menia obsah.
- **S3 používané ako POSIX filesystem bez analýzy** — rename, locking a in-place writes majú iný model.
- **Strong consistency považovaná za multi-object transaction** — manifest a objects môžu byť logicky rozídené.
- **Versioning považovaný za immutable backup** — versions možno odstrániť policy alebo privileged principalom.
- **Replication success odvodený zo source PUT** — asynchronous destination môže byť pending/failed.
- **Lifecycle považovaný za backup** — lifecycle je retention/deletion automation.
- **EBS snapshot bez application checkpointu** — block state nemusí byť business-consistent.
- **`volume=available` považované za RTO** — cold initialization a application recovery zostávajú.
- **EBS volume považovaný za Multi-AZ disk** — volume je zonálny.
- **Multi-Attach bez fencing** — concurrent writers môžu corrupt-nuť blocks.
- **Device path použitý ako stable volume identity** — NVMe ordering sa môže meniť.
- **EFS mount success považovaný za write authorization** — IAM/access-point/POSIX gates zostávajú.
- **Access point považovaný za jedinú isolation vrstvu** — network, IAM a POSIX policy musia sedieť.
- **EFS One Zone pre critical Multi-AZ workload bez DR** — cost choice mení failure contract.
- **Backup bez restore/business testu** — recovery point a usability nie sú dokázané.

## 32. Kontrolné otázky

1. Prečo S3, EBS a EFS nie sú zameniteľné storage tiers?
2. Čo je authoritative identity S3 objectu pri enabled versioningu?
3. Čo strong S3 consistency poskytuje a čo neposkytuje?
4. Kde je `RenameObject` podporovaný a prečo to nie je general S3 filesystem semantics?
5. Prečo Object Lock chráni version, ale nie automaticky správnu current representation?
6. Ako odlíšiš source PUT success od replication acceptance?
7. Čo je application-consistent EBS snapshot?
8. Prečo restored EBS volume môže byť `available`, ale nie performance-ready?
9. Kedy Multi-Attach vyžaduje fencing?
10. Ktoré vrstvy rozhodujú o EFS write operation po úspešnom mount-e?
11. Ako access point mení POSIX identity?
12. Čo musí obsahovať EFS failover a failback contract?
13. Ako sa meria storage RTO a RPO na business úrovni?
14. Aké positive a forbidden tests uzatvoria restore pre každý storage model?

## Glossary impact

Táto kapitola zavádza alebo spresňuje pojmy: storage subject, object-generation identity, current-version semantics, version-bound manifest, object retention generation, replication acceptance, block commit boundary, application-consistent snapshot set, volume initialization readiness, time-to-full-performance, shared-file namespace, access-point identity enforcement, mount authorization chain, filesystem publication contract a storage recovery acceptance verdict.

## Oficiálna dokumentácia

- [What is Amazon S3?](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)
- [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [S3 Replication](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html)
- [Renaming objects in directory buckets](https://docs.aws.amazon.com/AmazonS3/latest/userguide/directory-buckets-objects-rename.html)
- [Amazon EBS volumes and snapshots](https://docs.aws.amazon.com/ebs/latest/userguide/what-is-ebs.html)
- [EBS volume types](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html)
- [Initialize Amazon EBS volumes](https://docs.aws.amazon.com/ebs/latest/userguide/initalize-volume.html)
- [EBS fast snapshot restore](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-fast-snapshot-restore.html)
- [EBS Multi-Attach](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volumes-multi.html)
- [What is Amazon EFS?](https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html)
- [EFS performance](https://docs.aws.amazon.com/efs/latest/ug/performance.html)
- [EFS access points](https://docs.aws.amazon.com/efs/latest/ug/efs-access-points.html)
- [Replicating EFS file systems](https://docs.aws.amazon.com/efs/latest/ug/efs-replication.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Elastic Load Balancing](elastic-load-balancing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: RDS →](rds.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
