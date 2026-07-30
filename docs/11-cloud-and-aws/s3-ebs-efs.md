# S3, EBS a EFS

Amazon S3, Amazon EBS a Amazon EFS nie sú tri cenové varianty jedného disku. Každá služba realizuje iný data contract. S3 pracuje s objectom identifikovaným bucketom, keyom a pri versioningu version ID. EBS poskytuje zonálny block device, nad ktorým filesystem alebo database vytvára vyššiu štruktúru. EFS poskytuje shared NFS namespace pre viac clients.

```text
S3  → object API a immutable/versioned representations
EBS → block device, filesystem/database a explicit attach/mount lifecycle
EFS → shared file namespace, mount targets a POSIX operations
```

Správna voľba začína otázkami: čo je authoritative data unit, kto zapisuje, ako vzniká commit, aké sharing a consistency semantics application očakáva, v ktorom failure domain-e data existujú a ako sa po restore dokáže business použiteľnosť.

## 1. Exact storage subject

Atlas Payments používa storage subject `DATA-PAY-42` pre payment `P-884`.

S3 receipt je bucket `atlas-payments-evidence-prod`, key `receipts/2026/07/28/P-884.json`, version `VER-P884-7`, checksum `SHA256-...`, KMS generation `KMS-DATA-11` a retention generation `RET-9`.

EBS volume `vol-recon-42` v `eu-central-1a` používa filesystem UUID `FS-8F2`, snapshot set `SNAP-20260728-04` a application checkpoint `IDX-LSN-991`.

EFS filesystem `fs-pay-reports-17` používa Regional resilience, access point `fsap-report-writers`, root `/payment-reports`, enforced UID/GID `2001` a mount-target generation `MT-12`.

Forbidden outcomes sú key-only evidence identity, snapshot označený za application-consistent bez checkpointu, restored EBS volume vložený do trafficu pred performance readiness a EFS access mimo governed namespace.

## 2. Výber podľa access semantics

S3 je vhodný pre immutable artifacts, receipts, logs, media, backup a data-lake objects. Application používa HTTP API a každá operation pracuje s celým objectom alebo podporovaným multipart/range modelom. General-purpose bucket nie je POSIX filesystem.

EBS je vhodný pre boot volumes, databases a transactional filesystems pripojené k jednej compute identity alebo cluster-aware software-u. Volume patrí do jednej AZ.

EFS je vhodný, keď viac instances alebo Pods potrebuje spoločný POSIX-like file namespace. Shared filesystem neodstraňuje application locking, atomic publication ani conflict handling.

## 3. S3 object identity a strong consistency

General-purpose S3 poskytuje strong read-after-write consistency pre úspešné object writes/deletes a listing. To neznamená multi-object ACID transaction, atomic rename celého prefixu, synchronous replication ani ochranu pred logicky chybným overwrite.

Object publication lifecycle:

```text
producer payload
→ bucket, key and write preconditions
→ authorization and KMS
→ PutObject or multipart completion
→ exact version ID and checksum
→ immutable manifest publication
→ downstream consumer
→ retention, replication and recovery
```

Praktický upload s checksumom:

```bash
CHECKSUM=$(openssl dgst -sha256 -binary P-884.json | openssl base64 -A)

aws s3api put-object \
  --bucket atlas-payments-evidence-prod \
  --key receipts/2026/07/28/P-884.json \
  --body P-884.json \
  --checksum-algorithm SHA256 \
  --checksum-sha256 "$CHECKSUM" \
  --server-side-encryption aws:kms \
  --ssekms-key-id arn:aws:kms:eu-central-1:100000000042:key/key-data-11 \
  --metadata payment-id=P-884,producer-generation=PAY-7.18.0
```

Response obsahuje `VersionId`, ETag a checksum podľa operation. `200` preukazuje committed object operation pre exact request. NePreukazuje, že manifest alebo cross-Region replica už existuje.

Read-back:

```bash
aws s3api head-object \
  --bucket atlas-payments-evidence-prod \
  --key receipts/2026/07/28/P-884.json \
  --version-id "$VERSION_ID"
```

Audit consumer má používať version ID a checksum, nie iba current key.

## 4. Versioning a current-key ambiguity

Versioning uchováva viac versions rovnakého key. Delete current key typicky vytvorí delete marker. Reader bez `versionId` používa current-version semantics.

```bash
aws s3api list-object-versions \
  --bucket atlas-payments-evidence-prod \
  --prefix receipts/2026/07/28/P-884.json \
  --query '{Versions:Versions[].{VersionId:VersionId,Latest:IsLatest,Time:LastModified,Size:Size},DeleteMarkers:DeleteMarkers}'
```

Restore previous version sa často realizuje copy operation, ktorá vytvorí novú current version:

```bash
aws s3api copy-object \
  --bucket atlas-payments-evidence-prod \
  --key receipts/2026/07/28/P-884.json \
  --copy-source 'atlas-payments-evidence-prod/receipts/2026/07/28/P-884.json?versionId=VER-P884-7'
```

Tento command nemení historickú version na current pointer; vytvorí ďalšiu version s copied contentom. Recovery manifest musí zaznamenať novú version ID a checksum.

## 5. Object Lock, replication a lifecycle

Object Lock chráni konkrétnu version retention alebo legal holdom. Governance mode môže za určitých permissions umožniť bypass; compliance mode má prísnejšiu retention boundary. Object Lock nechráni logical key pred vznikom novej version, preto reader stále potrebuje version-bound evidence.

Replication je asynchronous. Source `PutObject` nepreukazuje destination copy. Object-level status:

```bash
aws s3api head-object \
  --bucket atlas-payments-evidence-prod \
  --key receipts/2026/07/28/P-884.json \
  --version-id "$VERSION_ID" \
  --query '{VersionId:VersionId,Replication:ReplicationStatus,ObjectLockMode:ObjectLockMode,RetainUntil:ObjectLockRetainUntilDate}'
```

Lifecycle môže transitionovať alebo expire current a noncurrent versions a odstrániť incomplete multipart uploads. Nie je backup. Chybná lifecycle rule môže odstrániť recovery history presne podľa configuration.

## 6. S3 manifest pattern

Multi-object evidence set sa publikuje cez immutable objects a manifest:

```json
{
  "manifestGeneration": "RM-PAY-81",
  "paymentId": "P-884",
  "objects": [
    {
      "bucket": "atlas-payments-evidence-prod",
      "key": "receipts/2026/07/28/P-884.json",
      "versionId": "VER-P884-7",
      "sha256": "..."
    }
  ]
}
```

Producer najprv zapíše objects, overí checksums a až potom immutable manifest. Consumer binduje exact generation. General S3 prefix rename sa typicky realizuje copy + delete; `RenameObject` je samostatná atomic capability directory buckets používajúcich S3 Express One Zone a nemožno ju zovšeobecniť na všetky buckets.

## 7. S3 worked incident: správny key, nesprávna evidence version

Recovery script po accidental delete odstránil delete marker a skopíroval historickú `VER-P884-6` na rovnaký key. Vznikla nová current version s old payloadom. Object Lock zachoval všetky versions správne, no reader a manifest používali iba key.

Evidence z `list-object-versions`, checksums a CloudTrail data events ukázala sequence. Recovery vybrala authoritative `VER-P884-7`, publikovala nový immutable manifest s version ID/checksumom a idempotentne spracovala exact version. Forbidden test overil, že old version nemôže byť prijatá ako P-884 evidence.

## 8. EBS volume ako zonálny block device

EBS volume patrí do jednej AZ. Filesystem, database layout, flush a application consistency vlastní customer.

```text
create or restore volume in exact AZ
→ attach to compatible instance
→ identify NVMe/device mapping
→ inspect signatures
→ mount by UUID
→ application writes and fsync/checkpoint
→ snapshot
→ restore and initialize
→ filesystem/application validation
```

Volume sa nepresúva do druhej AZ ako shared disk. Multi-AZ recovery vytvorí nový volume zo snapshotu alebo application replication.

## 9. Praktické vytvorenie a pripojenie EBS

```bash
aws ec2 create-volume \
  --region eu-central-1 \
  --availability-zone eu-central-1a \
  --volume-type gp3 \
  --size 100 \
  --iops 6000 \
  --throughput 250 \
  --encrypted \
  --kms-key-id arn:aws:kms:eu-central-1:100000000042:key/key-ebs-11 \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=vol-recon-42},{Key=Generation,Value=EBS-22}]'
```

Attach:

```bash
aws ec2 attach-volume \
  --region eu-central-1 \
  --volume-id vol-0recon42 \
  --instance-id i-0reconhost \
  --device /dev/sdf
```

Na Nitro instance môže guest vidieť NVMe name namiesto `/dev/sdf`. Identifikuj volume serial:

```bash
lsblk -o NAME,SIZE,FSTYPE,UUID,MOUNTPOINTS,SERIAL
sudo nvme id-ctrl /dev/nvme1n1 | grep -i sn
sudo blkid
```

Pred `mkfs` musí byť preukázané, že device je nový a bez intended filesystemu. Automatický format podľa device ordering môže zničiť restored data.

Nový empty volume:

```bash
sudo mkfs.xfs /dev/nvme1n1
sudo mkdir -p /srv/reconciliation
UUID=$(sudo blkid -s UUID -o value /dev/nvme1n1)
echo "UUID=$UUID /srv/reconciliation xfs defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo mount -a
findmnt /srv/reconciliation
```

`findmnt` preukazuje mount source/options. NePreukazuje application checkpoint alebo backup.

## 10. EBS performance envelope

Volume performance závisí od type, IOPS, throughput, I/O size, queue depth, initialization a instance EBS bandwidth. Provisioned 6 000 IOPS nepomôže, ak instance limit alebo single-threaded application blokuje path.

```bash
iostat -xz 1
lsblk -o NAME,SIZE,ROTA,FSTYPE,MOUNTPOINTS
```

CloudWatch metrics sa korelujú s OS queue/latency a application query. High queue depth môže byť symptom veľkého scan-u, nie dôkaz „pomalého EBS“.

## 11. Snapshot a application consistency

EBS snapshot je point-in-time block snapshot. Service nevie automaticky, či database transaction alebo multi-volume state je v application-consistent bode.

Safe checkpoint:

```text
pause or coordinate writes
→ database/filesystem checkpoint
→ flush buffers
→ record application LSN/generation
→ create snapshot set
→ resume writes
→ publish recovery manifest
```

Snapshot command:

```bash
aws ec2 create-snapshot \
  --region eu-central-1 \
  --volume-id vol-0recon42 \
  --description 'IDX-LSN-991 application checkpoint' \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Checkpoint,Value=IDX-LSN-991},{Key=Generation,Value=SNAP-20260728-04}]'
```

Snapshot `completed` preukazuje durable block snapshot creation, nie mount, database recovery alebo business usability.

## 12. Restore initialization a time-to-performance

Volume vytvorený zo snapshotu môže mať zvýšenú first-read latency, kým blocks nie sú initialized. RTO preto meria time-to-full-performance, nie iba `volume=available`.

Create volume s provisioned initialization rate:

```bash
aws ec2 create-volume \
  --region eu-central-1 \
  --availability-zone eu-central-1a \
  --snapshot-id snap-0recon04 \
  --volume-type gp3 \
  --size 100 \
  --iops 6000 \
  --throughput 250 \
  --volume-initialization-rate 200 \
  --encrypted \
  --kms-key-id arn:aws:kms:eu-central-1:100000000042:key/key-ebs-11
```

Current EBS supports a requested initialization rate from 100 to 300 MiB/s for supported snapshot-based create-volume workflows. If both provisioned initialization rate and Fast Snapshot Restore are applicable, the requested rate is used. Empty volumes do not need initialization.

Initialization read-back:

```bash
aws ec2 describe-volumes \
  --volume-ids vol-0restore42 \
  --region eu-central-1 \
  --query 'Volumes[0].{State:State,Type:VolumeType,Iops:Iops,Throughput:Throughput,Initialization:InitializationRate}'
```

Actual fields and status detail are also available through current volume initialization monitoring APIs/events. Application benchmark remains required.

## 13. EBS worked incident: `available`, ale RTO nesplnené

Automation obnovila `vol-recon-restore-43` zo snapshotu `SNAP-20260728-04`. Volume bolo `available`, attach/mount prešli a shallow health vrátil 200. Production reconciliation query však mala p95 18 sekúnd namiesto 40 ms.

Checkpoint aj volume type boli správne. Restore nepoužil FSR ani provisioned initialization rate. Health čítal malý metadata set, kým production scan čítal cold blocks a spúšťal on-demand initialization.

Recovery obmedzila traffic, inicializovala required dataset alebo vytvorila nový volume s approved rate a vykonala production-representative benchmark. RTO sa zmenilo z `time-to-attach` na `time-to-full-performance`.

## 14. EFS shared namespace

EFS poskytuje managed NFS filesystem. Regional filesystem uchováva data across AZs v Regione; One Zone má odlišný zonálny resilience contract. Mount target je network endpoint, nie data replica.

```text
filesystem
→ mount target in client AZ
→ DNS and route
→ SG/NACL TCP 2049
→ TLS/IAM client authorization
→ access point
→ POSIX identity and permissions
→ file operation
```

Timeout typicky leží v DNS/network/SG/NACL. `Permission denied` po úspešnom mount-e je často POSIX alebo access-point identity problem.

## 15. EFS a access point v Terraform-e

```hcl
resource "aws_efs_file_system" "reports" {
  encrypted        = true
  kms_key_id       = aws_kms_key.efs.arn
  performance_mode = "generalPurpose"
  throughput_mode  = "elastic"

  tags = {
    Name       = "fs-pay-reports-17"
    Generation = "EFS-PAY-17"
  }
}

resource "aws_efs_mount_target" "reports" {
  for_each = aws_subnet.application

  file_system_id  = aws_efs_file_system.reports.id
  subnet_id       = each.value.id
  security_groups = [aws_security_group.efs.id]
}

resource "aws_efs_access_point" "report_writers" {
  file_system_id = aws_efs_file_system.reports.id

  posix_user {
    uid = 2001
    gid = 2001
  }

  root_directory {
    path = "/payment-reports"

    creation_info {
      owner_uid   = 2001
      owner_gid   = 2001
      permissions = "0750"
    }
  }

  tags = {
    Name = "fsap-report-writers"
  }
}
```

`creation_info` sa použije pri vytvorení chýbajúceho root directory. NePrepisuje ownership existujúceho pathu.

## 16. EFS mount a identity verification

```bash
sudo mkdir -p /mnt/payment-reports

sudo mount -t efs \
  -o tls,iam,accesspoint=fsap-0reportwriters \
  fs-0payreports:/ \
  /mnt/payment-reports

findmnt /mnt/payment-reports
stat -c '%u:%g %a %n' /mnt/payment-reports
sudo -u '#2001' touch /mnt/payment-reports/canary.txt
```

Mount success preukazuje DNS/network/NFS/TLS a časť IAM pathu. `touch` testuje effective POSIX write identity. Business publication musí ešte overiť atomic rename, checksum a reader visibility.

Safe file publication:

```bash
printf '%s\n' '{"paymentId":"P-884"}' > /mnt/payment-reports/.P-884.tmp
sync /mnt/payment-reports/.P-884.tmp
sha256sum /mnt/payment-reports/.P-884.tmp
mv /mnt/payment-reports/.P-884.tmp /mnt/payment-reports/P-884.json
```

Rename v rovnakom filesystem namespace je file-level publication pattern. NePrenáša sa automaticky na general S3 object semantics.

## 17. EFS replication a failover

EFS replication asynchronously copies data/metadata to destination filesystem. Destination je počas replication read-only podľa service workflowu. Replication status a `LastReplicatedTimestamp` sú RPO evidence, nie instant failover.

```bash
aws efs describe-replication-configurations \
  --file-system-id fs-0payreports \
  --region eu-central-1
```

Failover zahŕňa verification replica pointu, fencing source writers, service-specific replication transition, destination mount targets/SG/access points/DNS, remount clients a business validation. Failback potrebuje reverse replication alebo explicitnú data authority migration.

## 18. EFS worked incident: mount funguje, writers nemajú identity

Po migrácii na access point sa EFS mount podaril vo všetkých AZs a reads fungovali, ale write vracal `Permission denied`. Access point enforce-oval UID/GID 2001. Root `/payment-reports` však existoval z old generation s ownerom `1000:1000` a mode `0750`. Creation settings existujúci directory neopravili.

Recovery zachovala mount/policy/inode evidence, vykonala controlled ownership migration a testovala exact worker role v každej AZ. Forbidden test overil, že iná application role/access point namespace nemôže zapisovať.

## 19. Unified recovery verdict

S3 recovery vyberá exact object version a manifest. EBS recovery vyberá checkpointed snapshot, initialized volume a application benchmark. EFS recovery obnovuje filesystem, access points, mount targets, permissions a concurrent-writer semantics.

```text
storage recovery primitive
→ exact data generation
→ KMS and authorization
→ network or attach/mount path
→ application compatibility
→ positive read/write test
→ performance and business validation
→ forbidden old/wrong generation test
```

Backup job `Completed` je input do restore experimentu, nie recovery verdict.

## Kontrolné otázky

1. Prečo S3, EBS a EFS nie sú zameniteľné?
2. Čo identifikuje S3 evidence object pri versioningu?
3. Čo strong S3 consistency neposkytuje?
4. Prečo Object Lock nechráni automaticky správnu current representation?
5. Ako odlíšiš source PUT od replication acceptance?
6. Prečo EBS snapshot potrebuje application checkpoint?
7. Čo znamená time-to-full-performance po restore?
8. Prečo device path nie je stable EBS identity?
9. Ktoré gates rozhodujú o EFS write po úspešnom mount-e?
10. Čo musí obsahovať service-specific restore acceptance?

## Oficiálna dokumentácia

- [Amazon S3 User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/)
- [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)
- [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [S3 Replication](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html)
- [Amazon EBS](https://docs.aws.amazon.com/ebs/latest/userguide/what-is-ebs.html)
- [Initialize EBS volumes](https://docs.aws.amazon.com/ebs/latest/userguide/initalize-volume.html)
- [Fast Snapshot Restore](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-fast-snapshot-restore.html)
- [Amazon EFS](https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html)
- [EFS access points](https://docs.aws.amazon.com/efs/latest/ug/efs-access-points.html)
- [EFS replication](https://docs.aws.amazon.com/efs/latest/ug/efs-replication.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Elastic Load Balancing](elastic-load-balancing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Amazon RDS →](rds.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
