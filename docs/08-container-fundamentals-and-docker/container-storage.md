# Container storage

Container storage je lifecycle dát oddelený od lifecycle-u replaceable processu. Container môže byť stateful, ale image, writable layer, mounted storage, backup a restore musia mať samostatnú identity, ownership a failure boundary.

Dominantný model:

```text
data intent a durability/consistency contract
→ persistent data identity a authoritative writer
→ storage class/backend/topology selection
→ provision, attach a mount
→ UID/GID/LSM/mount-policy transition
→ initialize alebo recover
→ application read/write a flush semantics
→ snapshot/backup evidence
→ detach, fencing, replacement a reattach
→ restore verification, retention a retirement
```

Volume, bind mount alebo snapshot nie sú samy osebe durability guarantee. Úspech znamená, že správny workload používa správnu data identity, s podporovanými access semantics, a dáta možno obnoviť do overeného application outcome-u.

## 1. Atlas data subject

Atlas Payments worker používa persistentný retry ledger:

```text
logical data ID: atlas-payments/prod/retry-ledger
data generation: DL-203
owner: Payments Platform
writer identity: worker-primary-07
storage object: vol-atlas-retry-22
backend: regional block storage
zone: eu-central-1a
filesystem UUID: FS-882
mount source: /dev/disk/by-uuid/FS-882
container target: /var/lib/atlas/retry
access mode: single writer
backup policy: hourly incremental + daily application checkpoint
RPO: 1 hour
RTO: 2 hours
encryption key generation: K17
last verified restore: RESTORE-119
```

Image digest alebo container ID nie je data identity. Replacement container musí explicitne získať `DL-203`, nie „nejaký volume s podobným názvom“.

## 2. Storage state classes

Každý writable path klasifikuj:

### Immutable image content

Application binary, libraries a defaults. Mení sa rebuildom image-u.

### Ephemeral runtime state

Rebuildable cache, temporary files, sockets alebo scratch. Môže zaniknúť s containerom.

### Persistent application state

Business records, uploads, ledger, database files, durable queue alebo recovery checkpoint. Musí mať external ownera a recovery contract.

### External service state

Managed database, object storage alebo queue. Nie je v container filesysteme, ale stále potrebuje identity, backup a compatibility model.

### Secret material

Temporary credential file alebo key. Môže byť mounted, no nesmie sa automaticky stať durable data alebo backup obsahom.

Nejasná classification je hlavný zdroj straty dát a uncontrolled persistence.

## 3. Writable layer

Per-container writable layer je runtime subject:

```text
image snapshot
→ container upper layer
→ mutations
→ deleted with container/snapshot lifecycle
```

Je vhodná pre explicitne disposable state. Nie je vhodná ako jediný owner:

- database dát;
- uploads;
- audit logs;
- job výsledkov;
- retry ledgeru;
- encryption keys;
- migration checkpoints.

Restart processu môže writable layer zachovať, zatiaľ čo remove/recreate ju odstráni. „Prežilo restart“ preto neznamená persistentné.

## 4. Volume subject

Runtime-managed volume má lifecycle oddelený od containeru, ale contract musí zahŕňať:

```text
logical data ID
runtime volume ID/name
backend object ID
filesystem UUID alebo object prefix
topology/access mode
owner a writer lease
encryption key
backup/restore policy
retention/deletion protection
```

Volume automaticky negarantuje remote durability, replication, backup, encryption, multi-host attachment ani application-consistent snapshot.

Anonymous volume bez inventory môže prežiť container a stať sa orphanom, alebo sa pri novom deployment-e nepripojí správny object.

## 5. Bind mount subject

Bind mount sprístupní host path:

```text
host path + mount namespace + flags
→ container target path
```

Silno viaže workload na:

- node identity;
- path existence a symlink resolution;
- host UID/GID/ACL;
- SELinux/AppArmor labels;
- mount propagation;
- filesystem a backup policy;
- host replacement lifecycle.

Bind mount development source-u a produkčný persistent host path sú odlišné risk models. Mount host rootu alebo runtime socketu je security-boundary zmena, nie storage convenience.

## 6. Tmpfs a memory-backed state

Tmpfs je vhodný pre temporary sensitive files, sockets alebo scratch:

```text
mount create
→ memory-backed writes
→ memory accounting/swap behavior
→ teardown destroys state
```

Potrebuje:

- size limit;
- UID/GID/mode;
- memory/cgroup accounting;
- swap/confidentiality policy;
- cleanup expectation;
- behavior pri OOM.

Tmpfs môže vyčerpať memory boundary a nie je automaticky „secret-safe“, ak application hodnotu kopíruje do logu alebo dumpu.

## 7. Provision a topology

Storage backend musí zodpovedať workload topology:

- local disk — nízka latency, node affinity a host-failure risk;
- block storage — attach/detach, zone a single/multi-attach contract;
- network filesystem — shared access, network/locking/cache semantics;
- object storage — key/object API, nie POSIX filesystem;
- managed database/service — external lifecycle a protocol consistency.

Selection questions:

```text
required durability a availability
read/write access mode
latency, IOPS a throughput
filesystem/API semantics
zone/region mobility
backup/restore capabilities
encryption a key ownership
cost/capacity growth
```

„Dá sa mountnúť“ neznamená, že application podporuje backend semantics.

## 8. Attach, mount a namespace transition

Block storage lifecycle:

```text
backend volume available
→ attach to exact node
→ device identity appears
→ filesystem recognized
→ mount with expected flags
→ bind into container namespace
→ application opens correct path
```

Každý krok má samostatný failure verdict. Mount target môže navyše prekryť image directory a skryť default content.

Observation subject:

- backend volume/attachment ID;
- node a device path;
- filesystem UUID/type;
- host mount ID/options;
- container mount namespace a target;
- source/target inode/device identity;
- open-file/process inventory.

## 9. UID, GID a object authorization

Access verdict môže závisieť od:

```text
process effective UID/GID/groups
→ user namespace mapping
→ filesystem owner/mode/ACL
→ network filesystem identity mapping
→ mount flags
→ SELinux/AppArmor object policy
```

Container UID 0 môže mapovať na unprivileged host UID. Numeric ownership contract musí prežiť:

- image upgrade;
- node replacement;
- backup/restore;
- rootless/rootful migration;
- network filesystem export rules.

Recursive `chown` veľkého volume pri každom startup-e je availability a race risk.

## 10. Mount policy

Relevantné flags:

- read-only;
- `noexec`;
- `nosuid`;
- `nodev`;
- propagation;
- recursive read-only;
- filesystem-specific consistency/cache options.

Read-only target nezaručuje, že process nemá iný writable alias k rovnakým dátam. Audituj celý mount graph.

Propagation môže preniesť mount event medzi hostom a containerom a musí byť explicitne zdôvodnená.

## 11. Persistent data identity

Stateful workload potrebuje oddeliť:

```text
container/process identity
persistent data identity
service/network identity
writer lease/epoch
encryption identity
backup/recovery identity
```

Správny image nad nesprávnym production/staging volume je data incident, aj keď mount aj process start prešli.

Preflight má overiť data marker alebo metadata bez nekontrolovanej mutation:

```text
logical environment
application/schema generation
filesystem/backend identity
writer lease
restore lineage
```

## 12. Initialization

Initialization môže zahŕňať filesystem format, directory layout, ownership, schema migration, seed alebo encryption setup.

Safe lifecycle:

```text
identify blank/existing subject
→ acquire initialization/writer lock
→ validate version and environment
→ apply ledgered transition
→ commit completion marker after success
→ verify application invariant
→ release lock
```

Marker vytvorený pred dokončením operácie môže zakryť partial state. Dva containers inicializujúce rovnaký volume môžu corruptnúť data alebo vytvoriť divergent schema.

## 13. Single-writer a fencing

`single writer` je runtime safety contract, nie iba storage-driver label.

Pri failover-e:

```text
old writer loses authority
→ fencing confirms no more writes
→ storage detach/lease expires
→ new writer attaches
→ filesystem/application recovery
→ new writer epoch becomes active
```

Network partition môže nechať old container živý aj po controller rozhodnutí. Bez fencing-u môžu oba writers zapisovať na shared block/filesystem a spôsobiť corruption.

Fencing môže používať attachment exclusivity, lease epoch, storage reservation, node power fencing alebo application consensus podľa systému.

## 14. Multi-reader/multi-writer semantics

Schopnosť backendu pripojiť storage viacerým clients nepreukazuje bezpečnosť application.

Treba poznať:

- filesystem cluster awareness;
- locking model;
- cache coherence;
- append/rename/fsync semantics;
- application concurrency protocol;
- split-brain recovery.

Databázové files na arbitrary shared filesysteme sú nebezpečné bez vendor-supported modelu.

## 15. Object storage boundary

Object storage používa:

```text
bucket/container
+ object key/version
+ API operation
+ consistency/retention policy
```

Nie je POSIX filesystem. Rename môže byť copy+delete, directory môže byť prefix a file lock nemusí existovať.

Filesystem gateway môže skryť semantic gap, no neodstráni ho. Application musí byť navrhnutá pre object API alebo explicitne testovaný adapter contract.

## 16. Runtime write a durability

Application success musí byť definovaný voči persistence semantics:

```text
application buffer
→ syscall/write
→ filesystem/page cache
→ device/backend acknowledgement
→ replication/commit semantics
```

`write()` success nemusí znamenať durable data po node failure. Database alebo ledger potrebuje podporovaný fsync/transaction protocol a backend, ktorý tieto semantics rešpektuje.

## 17. Capacity a pressure

Storage subject zahŕňa:

- bytes a quota;
- inodes;
- IOPS/throughput;
- latency a queue depth;
- burst credits;
- snapshot/backup space;
- temp/migration/compaction headroom;
- filesystem reserved space.

Disk full môže súčasne zablokovať data write, WAL/checkpoint, logs a clean shutdown. Inode exhaustion môže nastať pri dostatku voľných bytes.

## 18. Logs a runtime artifacts

Logs nemajú zostať iba vo writable layeri. Output lifecycle:

```text
process stdout/stderr alebo file
→ runtime/collector
→ external sink
→ retention/index/access
```

File logging potrebuje rotation, quota a behavior pri collector/sink outage. Unbounded logs môžu vyčerpať node filesystem a zasiahnuť nesúvisiace containers.

## 19. Snapshot subject

Snapshot subject obsahuje:

```text
source data ID/generation
snapshot mechanism
consistency method
application version/schema
write freeze/checkpoint
storage/backend generation
encryption key reference
timestamp a integrity metadata
```

Snapshot môže byť iba crash-consistent. Ak application drží buffered alebo multi-volume transaction state, storage snapshot bez quiesce nemusí byť validný recovery point.

Snapshot v rovnakom account/region/key failure domain-e nie je samostatný disaster-recovery backup.

## 20. Backup lifecycle

```text
select recovery unit
→ quiesce/checkpoint/export
→ create immutable backup
→ verify integrity a completeness
→ encrypt and replicate to required failure domain
→ catalog lineage/retention
→ restore test
→ application-level validation
```

Backup musí zahrnúť potrebné metadata, schema/application compatibility, permissions/labels a key references.

„Backup job green“ môže znamenať iba successful API call, nie restorable business state.

## 21. Restore subject

Restore test:

```text
select backup lineage
→ provision clean target storage
→ retrieve/decrypt
→ restore bytes/objects
→ reapply ownership/labels
→ attach/mount under controlled identity
→ run application recovery
→ validate data and business invariant
→ measure RPO/RTO
→ cleanup and publish verdict
```

Restore do existujúceho production volume bez isolation môže zničiť current state. Test potrebuje čistý target a explicitnú data identity.

## 22. Encryption a key lifecycle

Rozlišuj:

- backend encryption at rest;
- transport encryption;
- filesystem encryption;
- application/field encryption;
- key wrapping a rotation;
- runtime decryption identity.

Mounted encrypted volume poskytuje plaintext oprávnenému processu. Encryption at rest nechráni pred compromised workloadom s mount accessom.

Backup je nepoužiteľný, ak key material alebo recovery access zanikol. Key rotation musí zachovať decryptability retained backups podľa policy.

## 23. Detach, replacement a retirement

Safe replacement:

```text
drain/quiesce writer
→ flush/checkpoint
→ revoke old writer lease
→ verify no open writes
→ unmount/detach
→ attach to new authorized node
→ mount and recover
→ verify application outcome
```

Deletion volume-u potrebuje:

- owner approval;
- active attachment/writer check;
- backup/retention check;
- environment/data marker;
- reversible grace period podľa risku;
- audit.

Container deletion a data deletion sú samostatné operations.

## 24. Worked failure: dáta zmizli po replacement-e

Retry ledger bol zapisovaný do `/var/lib/atlas/retry` vo writable layeri.

```text
container restart zachová upper layer
→ tím považuje path za persistentný
→ rollout remove/create vytvorí nový upper layer
→ retry ledger zmizne
→ payments sa spracujú duplicitne
```

Root cause je nesprávna data classification a chýbajúci persistent data subject. Recovery potrebuje business reconciliation, nie iba nový volume.

## 25. Worked failure: správny image, nesprávny volume

Production container dostal staging volume s rovnakým directory layoutom.

```text
mount succeeds
→ schema version je compatible
→ application starts healthy
→ production endpoint spracúva staging records
```

Mount success a schema compatibility neoverujú environment/data identity. Preflight musí kontrolovať immutable environment marker, data lineage a approved mapping.

## 26. Worked failure: dva writers po node partition

Old node stratil control-plane connectivity, ale pokračoval v zápise na network storage. Controller spustil replacement writer na inom node-e.

```text
controller považuje old writer za dead
→ old writer má stále storage access
→ new writer dostane rovnaké dáta
→ concurrent writes corruptnú ledger
```

Health timeout nie je fencing. Recovery: zastaviť oboch writers, zachovať evidence, obnoviť z validného transaction/backup pointu, reconcile business operations a zaviesť storage/application writer epoch.

## 27. Worked failure: snapshot bol green, restore neštartoval

Cloud snapshot sa vytvoril počas database write burstu bez checkpointu. Restore filesystem mountol, ale database recovery našla nekonzistentné multi-file state.

```text
storage API snapshot succeeded
→ crash-consistent bytes existujú
→ application consistency contract nebol splnený
→ restore application invariant zlyhá
```

Backup verdict musí obsahovať successful clean restore a data validation, nie iba snapshot ID.

## 28. Worked failure: volume prázdny po mountnutí

Image obsahovala default data v `/var/lib/atlas`. Empty volume sa mountol na rovnaký target a prekryl image directory.

```text
image path contains files
→ mount creates new lookup root at target
→ lower image files sú skryté
→ application vidí empty directory
```

Initialization má vedome kopírovať/seedovať data s ledgerom, nie predpokladať merge image a volume contentu.

## 29. Causal troubleshooting walkthrough: po failover-e sa objavujú corrupted records

Atlas primary container zlyhal. Replacement je healthy, ale retry ledger obsahuje duplicate a poškodené entries.

### 1. Zafixuj data a writer subject

Zaznamenaj:

- logical data ID a generation;
- backend volume/filesystem ID;
- old/new node a attachment timeline;
- old/new writer identity/epoch;
- mount/device/namespace identity;
- flush/checkpoint a detach evidence;
- storage/network events;
- application transaction/ledger checksums;
- backup/snapshot lineage.

### 2. Súťažiace hypotézy

1. Old writer pokračoval po partitione.
2. Storage umožnila multi-attach bez fencing-u.
3. New writer pripojil nesprávny volume alebo restore generation.
4. Filesystem recovery po unclean detach bola neúplná.
5. Backend/network cache alebo locking semantics nie sú podporované.
6. Application replay nie je idempotentný.
7. Snapshot/restore bol crash-consistent, ale nie application-consistent.
8. Encryption/key alebo partial read vyzerá ako corruption.
9. Disk-full/IO error spôsobil partial record.
10. Corruption vznikla skôr a failover ju iba odhalil.

### 3. Diskriminačné observation points

- backend attachment a reservation/lease history;
- node/process liveness a write audit;
- writer epoch v records;
- filesystem journal/check output podľa support modelu;
- device/volume UUID a environment marker;
- application transaction log sequence;
- storage latency/error/capacity events;
- backup/snapshot timestamp a consistency method;
- checksums a corruption boundary.

### 4. Containment

Zastav všetkých writers a odober volume z trafficu. Nevynucuj nový mount na ďalšom node-e. Zachovaj snapshots, journals, logs a attachment metadata.

### 5. Recovery

- split writer → fence old identity a vyber last valid transaction point;
- wrong volume/generation → pripoj správny subject read-only a audituj exposure;
- filesystem issue → použite podporovaný recovery postup nad kópiou;
- application replay → deduplicate/compensate podľa business ledgeru;
- invalid snapshot → obnov last verified application-consistent backup;
- capacity/I/O → odstráň root cause pred resume.

### 6. Over pôvodný outcome

Potvrď jednu active writer epoch, validný filesystem/application ledger, business reconciliation, durable new writes, restart/failover test a successful fresh backup/restore.

### 7. Posuň control skôr

Pridaj writer fencing gate, data-ID preflight, attachment audit, application checkpointed backups, periodic restore test a failover chaos test s business invariantom.

## 30. Referenčné pravidlá

- Container/process identity a persistent data identity sú odlišné.
- Writable layer je ephemeral per-instance state.
- Volume je storage object, nie automatická durability alebo backup guarantee.
- Bind mount prenáša host path, identity a security coupling.
- Tmpfs potrebuje memory a confidentiality contract.
- Mount success neoveruje správnu data/environment identity.
- UID/GID, user namespace, ACL a LSM tvoria combined access verdict.
- Mount môže prekryť image content.
- Multi-attach capability nie je application multi-writer safety.
- Failover bez fencing-u môže vytvoriť split writer.
- Object storage nie je POSIX filesystem.
- Write acknowledgement a durable commit sú odlišné.
- Snapshot nie je automaticky application-consistent backup.
- Backup je potvrdený až clean restore a business validationom.
- Encryption at rest nechráni mounted plaintext pred workloadom.
- Container deletion a data deletion sú oddelené lifecycles.

## 31. Kontrolné otázky

1. Čo tvorí persistent data subject?
2. Ako sa líši writable layer, volume a bind mount?
3. Prečo mount success nedokazuje správnu data identity?
4. Ako user namespace a LSM menia storage access verdict?
5. Prečo volume multi-attach neznamená safe multi-writer?
6. Čo je writer fencing a prečo health timeout nestačí?
7. Ako mount obscuring skryje image data?
8. Ako sa líši crash-consistent snapshot a application-consistent backup?
9. Čo musí overiť clean restore test?
10. Aké observation points lokalizujú corruption po failover-e?

## Glossary impact

Relevantné pojmy: persistent data subject, storage attachment subject, data generation, writer identity, writer epoch, storage fencing verdict, mount-namespace subject, mount obscuring, storage access verdict, application durability boundary, checkpointed backup subject, clean restore verdict, backup lineage, split-writer incident, data-ID preflight a storage retirement subject.

## Oficiálna dokumentácia

- [Docker storage overview](https://docs.docker.com/engine/storage/)
- [Docker volumes](https://docs.docker.com/engine/storage/volumes/)
- [Docker bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)
- [Docker tmpfs mounts](https://docs.docker.com/engine/storage/tmpfs/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Container networking](container-networking.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Container security →](container-security.md)
<!-- KNOWLEDGE-NAVIGATION:END -->