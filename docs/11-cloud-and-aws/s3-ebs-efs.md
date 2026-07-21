# S3, EBS a EFS

Amazon S3, Amazon EBS a Amazon EFS riešia odlišné storage contracts. Nie sú to tri cenové varianty rovnakého disku.

```text
S3  → object storage cez API
EBS → zonálny block storage pre compute instance
EFS → managed shared NFS filesystem
```

Výber musí vychádzať z access patternu, consistency, latency, sharing, durability, failure domainu, backupu, recovery a cost modelu.

## 1. Porovnávací mentálny model

| Vlastnosť | S3 | EBS | EFS |
|---|---|---|---|
| Storage model | object | block | file/NFS |
| Access | HTTP API/SDK | block device | filesystem mount |
| Scope | regional bucket/object service | volume v jednej AZ | Regional alebo One Zone file system |
| Sharing | veľa clients cez API | typicky jedna instance; obmedzený Multi-Attach | veľa NFS clients |
| Typický workload | artifacts, logs, backups, static data | OS, database volume, transactional filesystem | shared content, home directories, multi-instance files |
| Resize | object-by-object | volume size/performance modification | automatická kapacita |
| Backup model | versioning/replication/Object Lock/AWS Backup | snapshots/AWS Backup | AWS Backup/replication podľa návrhu |

Filesystem semantics nemožno automaticky očakávať od S3. S3 object key nie je POSIX inode a rename môže znamenať copy/delete operation podľa klienta.

## 2. Amazon S3

S3 ukladá objects do buckets.

Object obsahuje:

- key,
- data,
- metadata,
- tags,
- version ID pri versioningu,
- encryption a retention attributes.

Bucket je regional resource, hoci bucket name je globálne unikátny v príslušnej partition.

S3 je vhodné pre:

- build artifacts,
- logs a telemetry archives,
- backups,
- static web assets,
- data lakes,
- media,
- configuration artifacts,
- cross-account data exchange.

## 3. S3 consistency

S3 poskytuje strong read-after-write consistency pre object PUT, overwrite, delete a list operations v podporovanom modely služby.

To neznamená:

- multi-object transaction,
- atomic directory rename,
- application-level referential integrity,
- automatickú consistency medzi Regionmi pri asynchronous replication,
- ochranu pred chybným overwrite/deletion.

Pre publish workflow používaj immutable object keys alebo versioned manifest pointer, ak viac objektov musí tvoriť konzistentný release.

## 4. S3 storage classes

Storage class vyberaj podľa access frequency, retrieval latency, minimum storage duration a retrieval cost.

Kategórie zahŕňajú:

- S3 Standard,
- S3 Intelligent-Tiering,
- S3 Standard-IA,
- S3 One Zone-IA,
- S3 Glacier Instant Retrieval,
- S3 Glacier Flexible Retrieval,
- S3 Glacier Deep Archive,
- S3 Express One Zone pre špecifické low-latency use cases.

Všetky classes nie sú vhodné pre rovnaký recovery objective. Archive class môže mať retrieval delay a poplatky. One Zone class má odlišný resilience contract než multi-AZ classes.

Nespoliehaj sa na názov „archive“. Over:

- retrieval time,
- minimum duration,
- object-size overhead,
- request/retrieval fees,
- lifecycle transition rules,
- service quotas a Region support.

## 5. S3 Lifecycle

Lifecycle rules môžu:

- transitionovať current alebo noncurrent versions,
- expire current objects,
- odstrániť noncurrent versions,
- odstrániť expired delete markers,
- abortovať incomplete multipart uploads.

Versioned bucket má odlišné expiration semantics: expiration current version typicky vytvorí delete marker a staršie versions zostávajú, kým ich neodstráni samostatná noncurrent-version policy.

Pred lifecycle rolloutom modeluj:

- current a noncurrent object count,
- Object Lock,
- legal hold,
- replication status,
- restore requirements,
- minimum-duration charges.

Lifecycle nie je backup verification.

## 6. S3 Versioning

Versioning zachováva viac versions rovnakého key a pomáha pri accidental overwrite alebo delete.

Delete vo versioning-enabled buckete typicky vytvorí delete marker. Predchádzajúca object version zostane dostupná.

Riziká:

- každá version zvyšuje storage cost,
- compromised principal môže mať permission odstrániť versions,
- lifecycle môže noncurrent versions odstrániť,
- versioning nepokrýva celý account/Region compromise,
- application môže stále čítať chybnú current version.

Versioning je recovery primitive, nie kompletný immutable backup model.

## 7. S3 Replication

Replication môže kopírovať objects:

- v rovnakom Regioni — SRR,
- medzi Regionmi — CRR,
- do jedného alebo viacerých destination buckets podľa rules.

Replication je asynchronous. Sleduj replication status, failed replication a backlog.

Vyžaduje:

- versioning,
- IAM replication role,
- destination bucket policy,
- KMS permissions pri encrypted objects,
- explicitný handling existing objects podľa zvoleného mechanizmu.

Replication môže preniesť logical corruption alebo malicious write. Pre ransomware/deletion scenár kombinuj versioning, Object Lock, oddelený account a restrictive delete permissions.

## 8. S3 Object Lock

Object Lock poskytuje WORM retention pre konkrétne object versions.

Mechanizmy:

- retention period,
- legal hold,
- governance mode,
- compliance mode.

Object Lock chráni konkrétnu version. Nová version alebo delete marker môže stále vzniknúť podľa operation, pričom chránená version zostáva zachovaná.

Compliance mode navrhuj opatrne; retention nemožno jednoducho obísť ani administrátorom. Chybná retention môže vytvoriť dlhodobý cost a data-governance problém.

## 9. S3 encryption

Možnosti zahŕňajú:

- SSE-S3,
- SSE-KMS,
- DSSE-KMS podľa požiadaviek,
- client-side encryption,
- SSE-C pri špecifických use cases.

Pri SSE-KMS potrebuje request access aj ku KMS key. `AccessDenied` môže pochádzať z:

- IAM,
- bucket policy,
- access point policy,
- SCP/RCP,
- VPC endpoint policy,
- KMS key policy/grant,
- encryption context.

Bucket encryption nezabezpečuje application-level field separation ani ochranu pred autorizovaným destructive API callom.

## 10. S3 access control

Vrstvy:

- IAM identity policy,
- bucket policy,
- access point policy,
- ACL pri legacy use cases,
- S3 Block Public Access,
- Object Ownership,
- VPC endpoint policy,
- KMS policy.

Preferuj bucket-owner-enforced Object Ownership a policy-based access namiesto ACLs, ak use case nevyžaduje inak.

S3 Block Public Access je guardrail proti public exposure, ale musí byť vyhodnotený na account aj bucket úrovni.

## 11. S3 network access

Prístup môže ísť cez:

- public regional endpoint,
- gateway VPC endpoint,
- interface endpoint podľa use case,
- access point alebo Multi-Region Access Point,
- CloudFront origin path.

Gateway endpoint môže znížiť NAT dependency pre workloads vo VPC. Endpoint route a endpoint policy však môžu spôsobiť `AccessDenied` alebo chýbajúci path.

## 12. S3 multipart uploads

Veľké objects sa typicky uploadujú multipart spôsobom.

Výhody:

- parallel upload,
- retry jednotlivých parts,
- vyššia throughput.

Riziko: nedokončené multipart uploads spotrebúvajú storage. Lifecycle rule na abort incomplete uploads patrí do cost baseline-u.

## 13. S3 events a notifications

S3 môže publikovať events do podporovaných destinations, napríklad EventBridge, SNS, SQS alebo Lambda podľa konfigurácie.

Event-driven consumer musí tolerovať:

- duplicate delivery,
- retry,
- ordering hranice,
- partial failure,
- object visibility a version identity.

Používaj bucket, key, version ID, sequencer/event ID podľa dostupného contractu a idempotentné spracovanie.

## 14. Amazon EBS

EBS poskytuje durable block device pre EC2.

Kľúčové vlastnosti:

- volume je v jednej Availability Zone,
- instance a volume musia byť v rovnakej AZ,
- volume prežíva nezávisle od running instance podľa lifecycle nastavenia,
- filesystem a partition spravuje zákazník,
- performance závisí od volume type aj EC2 EBS bandwidth.

EBS je vhodné pre:

- boot/root volumes,
- databases,
- transactional filesystems,
- low-latency block workloads,
- persistent single-node application data.

## 15. EBS volume types

### General purpose SSD

- `gp3` — IOPS a throughput sa nastavujú nezávislejšie od size,
- `gp2` — performance a burst model je viac previazaný so size.

### Provisioned IOPS SSD

- `io2`, `io1` podľa supported generation/use case,
- kritické IOPS/latency workloady,
- Multi-Attach iba pri podporovaných typoch a konfiguráciách.

### HDD

- `st1` — throughput-optimized sequential workloads,
- `sc1` — cold, infrequently accessed sequential data.

HDD EBS nepoužívaj ako boot volume.

Pri sizingu rozlišuj:

- IOPS,
- throughput,
- I/O size,
- queue depth,
- latency,
- burst credits,
- EC2 instance EBS limit.

Provisioned 20 000 IOPS nepomôže, ak instance family povoľuje menší EBS throughput.

## 16. EBS attachment a filesystem

Po attachi block device ešte nemusí obsahovať filesystem.

Workflow:

```text
attach volume
→ identifikuj device
→ partition podľa potreby
→ create filesystem
→ mount
→ persistent /etc/fstab podľa UUID
```

Pred detachom:

- zastav writes,
- flush buffers,
- unmount filesystem,
- over application shutdown.

Force detach môže viesť k filesystem corruption alebo concurrent writer.

## 17. EBS Multi-Attach

Multi-Attach umožňuje vybraným Provisioned IOPS volumes pripojenie k viacerým podporovaným instances v rovnakej AZ.

Nie je to automatický shared filesystem.

Application/filesystem musí podporovať:

- cluster-aware locking,
- fencing,
- concurrent writers,
- failure recovery.

Bežný ext4/xfs filesystem bez cluster orchestration sa nemá mountovať read-write na viac instances.

## 18. EBS snapshots

EBS snapshot zachytáva point-in-time block state volume-u.

Snapshots sú incremental z pohľadu uložených zmien, ale každý snapshot možno použiť ako samostatný restore point podľa služby.

Snapshot consistency:

- crash-consistent pri nekordinovanom block capture,
- application-consistent po flush/quiesce alebo database-native coordination.

Multi-volume application potrebuje coordinated snapshot alebo backup service/workflow, inak volumes môžu reprezentovať odlišný logical moment.

Snapshots sú regional resources s možnosťou copy/share podľa permissions a encryption modelu.

## 19. EBS restore a initialization

Volume vytvorený zo snapshotu môže načítavať blocks lazy pri prvom access-e. Počas initialization môže mať vyššiu latency.

Možnosti:

- manuálny pre-read/inicializácia,
- Fast Snapshot Restore pre konkrétny snapshot-AZ pár,
- provisioned initialization rate podľa podporovanej feature.

Fast Snapshot Restore má samostatný cost a musí byť explicitne enabled pre snapshot a AZ. Nová snapshot copy nezdedí automaticky FSR enablement.

Restore test musí merať aj time-to-full-performance, nie iba `volume=available`.

## 20. Elastic Volumes

Podporované volumes možno meniť za behu:

- size,
- type,
- IOPS,
- throughput.

Po zväčšení volume musíš podľa OS/filesystemu rozšíriť partition a filesystem. AWS control-plane modification sama nezväčší filesystem visible capacity.

Volume sa nedá zmenšiť priamo rovnakým spôsobom; typický workflow je nový menší volume a data migration.

## 21. EBS encryption

EBS encryption chráni data at rest, data medzi instance a volume a snapshots v supported modely.

KMS permissions ovplyvňujú:

- launch encrypted volume,
- snapshot copy,
- cross-account share,
- ASG launch,
- backup restore.

ASG môže zlyhávať na KMS key policy aj keď EC2 launch permission vyzerá správne.

## 22. Amazon EFS

EFS poskytuje managed NFS filesystem pre Linux a podporované compute integrations.

Vlastnosti:

- shared file namespace,
- concurrent mount z mnohých clients,
- POSIX permissions,
- automatický rast a pokles billed storage,
- Regional alebo One Zone resilience model,
- mount targets vo VPC.

Use cases:

- shared application content,
- web content,
- home directories,
- container shared volumes,
- build/workspace data,
- workloads vyžadujúce POSIX file semantics.

## 23. EFS mount targets

Client vo VPC pristupuje k EFS cez mount target ENI.

Odporúčaný Regional design:

- mount target v každej používanej AZ,
- DNS resolution na zonálne vhodný mount target,
- Security Group povoľujúca NFS TCP/2049 z client SG,
- subnet IP capacity,
- redundant clients.

Mount target je network path, nie kópia filesystem dát. Chýbajúci mount target v AZ môže vytvoriť cross-AZ path alebo mount failure podľa DNS/network modelu.

## 24. EFS performance a throughput

Výkon ovplyvňujú:

- performance mode,
- throughput mode,
- file-size a metadata pattern,
- počet clients a threads,
- mount options,
- NFS/client version,
- storage class a access pattern.

Throughput modes môžu zahŕňať:

- Bursting,
- Provisioned,
- Elastic.

Malé serial metadata operations sa správajú inak než paralelné veľké sequential reads. Benchmark musí napodobniť production access pattern.

## 25. EFS lifecycle a storage classes

EFS lifecycle management môže presúvať infrequently accessed data do nižších storage tiers podľa policy.

Trade-offy:

- nižší storage cost,
- access/retrieval cost,
- first-byte latency rozdiely,
- backup a scan behavior.

One Zone EFS má nižší cost, ale iný failure-domain contract. Kritický multi-AZ workload nemá automaticky používať One Zone iba kvôli cene.

## 26. EFS access points

Access point vytvára application-specific entry path a POSIX identity contract.

Použitie:

- oddelenie applications,
- enforced UID/GID,
- root directory,
- container integrations.

Access point nie je plnohodnotný security isolation boundary bez správnych IAM, network a filesystem permissions.

## 27. EFS encryption a IAM

EFS môže používať encryption at rest a TLS in transit cez supported mount helper.

Authorization môže kombinovať:

- network Security Groups,
- filesystem policy/IAM authorization,
- access point,
- POSIX permissions.

Mount success ešte neznamená write permission. Diagnostika musí oddeliť DNS/network/TLS/IAM/POSIX vrstvy.

## 28. Storage selection patterns

### Artifact repository

S3: immutable versioned objects, lifecycle, replication.

### EC2 database volume

EBS: gp3/io2 podľa IOPS a latency; snapshots a application-consistent backup.

### Shared web assets pre viac EC2 instances

EFS, ak application vyžaduje shared POSIX writes. Pre immutable static delivery môže byť lepší S3 + CloudFront.

### Container state

- ephemeral local pre scratch,
- EBS pre zonálny single-writer block,
- EFS pre shared NFS,
- S3 pre object data.

## 29. Backup a recovery

### S3

- versioning,
- Object Lock,
- replication,
- AWS Backup,
- cross-account controls,
- restore/version selection.

### EBS

- snapshots,
- AWS Backup,
- cross-Region/account copy,
- volume initialization,
- filesystem/application validation.

### EFS

- AWS Backup,
- replication podľa požiadaviek,
- file-level restore,
- mount-target/network reconstruction.

Backup úspech nie je restore úspech. Testuj application usability, permissions, KMS, DNS/mount a performance after restore.

## 30. Observability

### S3

- CloudTrail data events podľa requirements,
- server access logs alebo CloudTrail,
- Storage Lens,
- replication metrics,
- request/error metrics,
- inventory,
- lifecycle/object count.

### EBS

- volume IOPS/throughput/queue/latency-related metrics,
- burst balance pri relevantných typoch,
- instance EBS limits,
- attachment state,
- snapshot events.

### EFS

- throughput a I/O metrics,
- percent I/O limit,
- client connections,
- storage bytes/classes,
- mount helper/client logs.

## 31. Troubleshooting S3 `AccessDenied`

Postup:

```text
caller/account/Region endpoint
→ action a bucket/object ARN
→ IAM allow/deny
→ bucket/access-point policy
→ Block Public Access/Object Ownership
→ VPC endpoint policy
→ KMS key policy/grant
→ Object Lock/retention
```

Rozlišuj bucket ARN:

```text
arn:aws:s3:::bucket
```

a object ARN:

```text
arn:aws:s3:::bucket/prefix/*
```

`ListBucket` používa bucket resource; `GetObject` object resource.

## 32. Troubleshooting S3 chýbajúceho objektu

Over:

- presný key a case,
- URL encoding,
- current version/delete marker,
- replication destination,
- lifecycle expiration,
- prefix/account/Region,
- application cache,
- event processing delay.

S3 nemá skutočné directories; console folder je key-prefix presentation.

## 33. Troubleshooting EBS latency

Over:

- volume type a provisioned IOPS/throughput,
- EC2 EBS bandwidth,
- I/O size a queue depth,
- burst balance,
- snapshot initialization,
- filesystem/device errors,
- application fsync pattern,
- CloudWatch metrics a OS tools.

Príklady:

```bash
iostat -xz 1
lsblk -f
nvme list
sudo dmesg -T | tail
```

## 34. Troubleshooting EBS attach/mount

Over:

- rovnaká AZ,
- attachment state,
- device/NVMe mapping,
- filesystem UUID,
- duplicate filesystem UUID po clone,
- `/etc/fstab` a `nofail`,
- KMS permissions,
- existing attachment/Multi-Attach,
- filesystem corruption.

Nikdy nespúšťaj repair tool na mounted read-write filesystem bez príslušného runbooku.

## 35. Troubleshooting EFS mount

Postup:

```text
filesystem a mount target existuje?
→ DNS resolution?
→ route/VPC connectivity?
→ SG TCP/2049?
→ NACL return path?
→ mount helper/NFS package?
→ TLS/IAM authorization?
→ POSIX permissions?
```

Symptómy:

- timeout — network/SG/NACL/DNS,
- access denied — IAM/filesystem policy/access point,
- permission denied po mount-e — POSIX UID/GID/mode,
- nízky výkon — throughput mode, serialization, metadata contention, cross-AZ path.

## 36. Cost model

### S3

- stored bytes podľa class,
- requests,
- retrieval,
- minimum duration,
- lifecycle transitions,
- replication/data transfer,
- versions,
- unfinished multipart uploads.

### EBS

- provisioned GiB,
- IOPS/throughput podľa type,
- snapshots,
- FSR alebo initialization features,
- unattached volumes.

### EFS

- stored bytes podľa class,
- throughput mode/provisioned throughput,
- access/retrieval,
- cross-AZ data path,
- backups.

Najčastejší waste: unattached EBS volumes, stale snapshots, nekontrolované S3 versions a EFS cold data bez lifecycle policy.

## 37. SOA-C03 mapovanie

- **Domain 1** — storage metrics, access logs, EBS/EFS performance troubleshooting,
- **Domain 2** — versioning, replication, snapshots, backups, restore a multi-AZ storage choices,
- **Domain 3** — lifecycle policies, automated backups, volume modification a provisioning,
- **Domain 4** — encryption, KMS, bucket/filesystem policies, Object Lock a access controls,
- **Domain 5** — S3 endpoints, EFS mount targets, Security Groups a network path.

Praktické drilly:

- S3 version restore po delete marker,
- SSE-KMS `AccessDenied`,
- replication failure pre destination/KMS policy,
- EBS volume vytvorený v zlej AZ,
- filesystem nerozšírený po Elastic Volumes modification,
- EBS restore latency pre uninitialized blocks,
- EFS mount timeout pre SG alebo chýbajúci mount target.

## 38. Anti-patterny

### S3 používané ako POSIX filesystem bez analýzy

Rename, locking a small-file semantics sa líšia.

### Versioning považovaný za immutable backup

Privilegovaný principal alebo lifecycle môže versions odstrániť.

### EBS snapshot bez database coordination

Restore môže byť crash-consistent, ale nie business-consistent.

### EBS volume ako multi-AZ storage

Volume je zonálny; snapshot/replication/recovery musí riešiť presun.

### Multi-Attach bez fencing

Hrozí filesystem alebo database corruption.

### EFS One Zone pre kritický multi-AZ workload bez DR

Znižuje failure isolation.

### Storage class vybraná iba podľa ceny za GiB

Ignoruje request, retrieval, latency a minimum duration.

## 39. Kontrolné otázky

1. Ako sa líši object, block a file storage?
2. Prečo S3 Versioning nie je kompletný backup?
3. Ako Lifecycle pracuje s current a noncurrent versions?
4. Čo chráni Object Lock?
5. Prečo EBS volume musí byť v rovnakej AZ ako instance?
6. Ako sa líši EBS snapshot crash consistency a application consistency?
7. Prečo volume zo snapshotu môže mať prvotnú latency?
8. Kedy použiť EFS namiesto S3?
9. Ktoré vrstvy preveríš pri EFS mount timeout-e?
10. Ako vyberieš medzi gp3, io2, st1 a EFS/S3?

## Glossary impact

Relevantné pojmy: Amazon S3, S3 bucket, object key, S3 storage class, S3 Lifecycle, S3 Versioning, delete marker, S3 Replication, S3 Object Lock, governance mode, compliance mode, multipart upload, Amazon EBS, EBS volume, EBS snapshot, volume initialization, Fast Snapshot Restore, Elastic Volumes, EBS Multi-Attach, Amazon EFS, EFS mount target, EFS access point, throughput mode a application-consistent snapshot.

## Oficiálna dokumentácia

- [Amazon S3 User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- [S3 storage classes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html)
- [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)
- [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [Amazon EBS User Guide](https://docs.aws.amazon.com/ebs/latest/userguide/what-is-ebs.html)
- [EBS volume types](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html)
- [Initialize EBS volumes](https://docs.aws.amazon.com/ebs/latest/userguide/initalize-volume.html)
- [Amazon EFS User Guide](https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html)
- [Amazon EFS performance](https://docs.aws.amazon.com/efs/latest/ug/performance.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Elastic Load Balancing](elastic-load-balancing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: RDS →](rds.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
