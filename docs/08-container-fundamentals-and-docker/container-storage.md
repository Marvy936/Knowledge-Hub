# Container storage

Container storage musí oddeliť image content, runtime writable layer a dáta, ktoré majú prežiť replacement. Container môže byť stateful, ale persistence, identity, consistency, backup a recovery nesmú byť implicitne viazané na existenciu jednej runtime inštancie.

## 1. Tri storage kategórie

Pri container workload-e rozlišuj:

1. **image layers** — immutable application a userspace content,
2. **writable container layer** — ephemeral runtime mutations,
3. **external alebo mounted storage** — dáta s explicitným lifecycle.

Ich ownership, backup a performance model sú odlišné.

## 2. Writable layer

Writable layer je vhodná pre:

- temporary files,
- disposable cache,
- runtime metadata obnoviteľné po štarte,
- krátkodobý scratch space.

Nie je vhodná ako jediná kópia:

- databázových dát,
- uploads,
- audit logs,
- encryption keys,
- job výsledkov,
- recovery checkpoints.

Pri odstránení containeru môže writable layer zmiznúť. Pri novom image deployment-e sa vytvorí nová runtime instance.

## 3. Volume

Volume je runtime-managed storage object s lifecycle oddeleným od konkrétneho containeru. Runtime typicky spravuje jeho location a mount integration.

Výhody:

- jednoduchšia persistence než writable layer,
- oddelený lifecycle,
- možnosť backupu alebo migration podľa drivera,
- explicitné pripojenie k viacerým containers podľa access modelu.

Volume však automaticky negarantuje:

- remote durability,
- replication,
- backup,
- encryption,
- multi-host portability,
- application-consistent snapshot.

## 4. Bind mount

Bind mount sprístupní existujúci host path do containeru.

Príklad konceptu:

```text
host /srv/app/config
→ container /etc/app
```

Výhody:

- priamy access k host files,
- vhodné pre development source mount,
- jednoduchá integrácia s existujúcim host storage.

Riziká:

- tight coupling na host path a permissions,
- host filesystem exposure,
- portability problems,
- SELinux/AppArmor labeling,
- neúmyselný writable access,
- symlink a path traversal riziká,
- host replacement bez dátovej migrácie.

## 5. tmpfs

`tmpfs` drží dáta v memory-backed filesysteme, prípadne s možným swap behaviorom podľa host konfigurácie.

Vhodné pre:

- temporary sensitive data,
- runtime sockets,
- rýchly scratch space,
- files, ktoré nemajú prežiť restart.

Potrebné controls:

- size limit,
- memory accounting,
- permissions,
- cleanup expectations,
- OOM impact.

Tmpfs nie je trvalé úložisko a spotreba môže ovplyvniť memory limit workloadu alebo hosta.

## 6. Mount options

Bezpečnosť a behavior ovplyvňujú mount flags:

- read-only,
- `noexec`,
- `nosuid`,
- `nodev`,
- propagation,
- recursive read-only behavior,
- filesystem-specific options.

Read-only mount znižuje mutation surface, ale application môže stále zapisovať cez iný mount alebo API. Security model musí kontrolovať celý path graph.

## 7. Ownership a permissions

Container process používa UID/GID, ktoré sa aplikujú na mounted filesystem. Problémy vznikajú pri:

- numeric UID mismatch,
- user namespace remapping,
- NFS root squashing,
- host-created files,
- shared volume medzi images s odlišným user modelom,
- init process meniaci ownership pri každom štarte.

Preferuj stabilné numeric identity contracty a priprav storage permissions mimo kritického application startup pathu.

## 8. User namespaces a storage

Pri user namespace remapping môže container UID 0 mapovať na vysoký host UID. Host path musí byť prístupný mapped identity.

Riziká:

- `chown` veľkého stromu pri migrácii,
- nekompatibilný network filesystem,
- multiple remapping ranges,
- backup tool zachovávajúci neočakávané numeric IDs.

Over restore na cieľovom hoste s rovnakým mapping modelom.

## 9. SELinux labels

Na SELinux hoste nestačia Unix permissions. Bind mount alebo volume potrebuje správny security context.

Chybný label sa môže prejaviť ako `Permission denied`, aj keď UID/GID a mode bits vyzerajú správne.

Nepoužívaj globálne vypnutie SELinux. Uprav label/mount integration a over audit denials.

## 10. Storage driver vs. volume driver

Rozlišuj:

- **image/storage driver alebo snapshotter** — spravuje image layers a writable snapshots,
- **volume driver/plugin** — pripája persistent storage,
- **filesystem/storage backend** — reálny local, block, network alebo cloud storage.

Performance problém „Docker storage“ môže byť v ktorejkoľvek vrstve.

## 11. Local storage

Local disk môže poskytovať nízku latency, ale viaže dáta na host.

Potrebný lifecycle:

- scheduling/placement constraint,
- host failure recovery,
- backup,
- disk replacement,
- capacity monitoring,
- cleanup orphaned volumes.

Container replacement na rovnakom hoste nie je to isté ako host failure recovery.

## 12. Network filesystem

NFS, SMB alebo distribuovaný filesystem umožňuje multi-host access, ale prináša:

- network latency,
- server availability dependency,
- locking a cache semantics,
- UID/GID mapping,
- stale mounts,
- split-brain alebo consistency trade-offy,
- mount timeout behavior.

Application musí podporovať dané filesystem semantics. Databáza navrhnutá pre local POSIX disk nemusí byť bezpečná na ľubovoľnom network filesysteme.

## 13. Block storage

Block device alebo cloud volume môže poskytovať filesystem alebo raw block access.

Over:

- attach/detach lifecycle,
- single-writer/multi-attach capabilities,
- fencing,
- filesystem mount state,
- zone/region constraints,
- snapshot consistency,
- encryption keys,
- performance class a burst limits.

Súbežné pripojenie bez cluster-aware filesystemu môže poškodiť dáta.

## 14. Object storage

Object storage nie je POSIX filesystem. Je vhodný pre:

- uploads,
- artifacts,
- backups,
- logs,
- immutable blobs.

Application musí používať object API semantics: keys, versions, eventual/defined consistency model, multipart uploads, retention a lifecycle rules.

Mountovanie object storage ako filesystem môže skryť semantic rozdiely a vytvoriť nečakané rename, locking alebo durability behavior.

## 15. Access modes

Pri návrhu definuj:

- single reader/writer,
- multiple readers,
- multiple writers,
- read-only replicas,
- writer fencing,
- topology constraints.

„Volume sa dá pripojiť k dvom containers“ neznamená, že application alebo filesystem bezpečne podporuje concurrent writers.

## 16. Stateful application identity

Stateful workload potrebuje oddeliť:

- process/container identity,
- persistent data identity,
- network/service identity,
- encryption identity,
- backup/recovery identity.

Container môže byť nahradený bez zmeny data identity. Naopak, omylom pripojený volume z iného environmentu môže spustiť správny image nad nesprávnymi dátami.

## 17. Initialization

Storage initialization môže zahŕňať:

- filesystem format,
- directory layout,
- ownership,
- schema migration,
- seed data,
- encryption setup.

Musí byť:

- idempotentná alebo ledger-based,
- concurrency-safe,
- versionovaná,
- obnoviteľná po partial failure,
- oddelená od bežného application startupu podľa rizika.

Dva containers súčasne inicializujúce rovnaké dáta môžu vytvoriť race.

## 18. Backup

Backup má zachytiť potrebný recovery unit:

- volume/filesystem data,
- database-consistent state,
- metadata a configuration,
- encryption keys alebo key references,
- application/version compatibility,
- ownership a permissions.

Filesystem snapshot bez application quiesce alebo databázového consistency mechanizmu môže byť crash-consistent, nie application-consistent.

## 19. Restore

Restore test musí overiť:

1. artifact dostupnosť,
2. checksum/integritu,
3. decryption,
4. filesystem/volume creation,
5. permissions a labels,
6. application compatibility,
7. data validation,
8. RPO/RTO,
9. cleanup a incident evidence.

Backup bez pravidelného restore testu je iba nepotvrdená hypotéza.

## 20. Snapshot

Snapshot môže byť:

- copy-on-write storage snapshot,
- filesystem snapshot,
- cloud block snapshot,
- database-native snapshot.

Snapshot nie je automaticky backup. Môže zostať v rovnakom failure domain-e, závisieť od rovnakého accountu/kľúča alebo nezachytávať application consistency.

## 21. Encryption

Rozlišuj:

- encryption at rest backendu,
- filesystem-level encryption,
- application-level encryption,
- transport encryption pri network storage,
- key management a rotation.

Encrypted volume pripojený kompromitovanému containeru poskytuje plaintext cez mount. Encryption at rest nechráni runtime access.

## 22. Capacity

Storage limit musí pokrývať:

- persistent data,
- temporary files,
- logs,
- compaction,
- migrations,
- backup staging,
- filesystem reserved space,
- snapshots.

Disk-full failure môže zabrániť application write, database checkpointu, logovaniu aj clean shutdownu.

Sleduj bytes, inodes, quota, latency, IOPS a throughput.

## 23. Logging

Application logs nemajú zostať iba vo writable layeri. Preferuj stdout/stderr collection alebo explicitný external log sink.

Pri file loggingu definuj:

- rotation,
- retention,
- ownership,
- disk quota,
- collector behavior,
- failure pri nedostupnom sinku.

Unbounded log file môže vyčerpať writable layer alebo host filesystem.

## 24. Secret storage

Secret môže byť pripojený ako temporary file alebo tmpfs mount. Potrebné controls:

- least privilege,
- mode/ownership,
- rotation behavior,
- žiadny copy do image alebo persistent volume,
- redaction,
- cleanup po termination.

Application môže secret skopírovať do config, dumpu alebo logu; mount mechanismus sám nezaručuje end-to-end confidentiality.

## 25. Troubleshooting

### `Permission denied` na mounted path

Over UID/GID, user namespace mapping, mode bits, ACL, SELinux/AppArmor, mount flags a network filesystem export policy.

### Dáta zmizli po `docker rm`

Boli vo writable layeri alebo anonymous storage bez správneho lifecycle/backup modelu.

### Volume je pripojený, ale application vidí prázdny directory

Over source volume identity, mount target, initialization order, host path, environment a či mount nezakryl image directory s pôvodným obsahom.

### Vysoká latency

Rozlišuj application fsync pattern, filesystem, volume driver, network, backend throttling, queue depth a host I/O pressure.

### Volume nejde odpojiť

Process drží open files, mount namespace stále existuje, filesystem je busy alebo storage backend čaká na fencing/detach.

## 26. Kontrolné otázky

1. Aký je rozdiel medzi writable layerom, volume a bind mountom?
2. Kedy použiť tmpfs?
3. Ako user namespaces ovplyvnia permissions?
4. Prečo volume neznamená automaticky backup?
5. Aké riziká má host-local storage?
6. Prečo object storage nie je POSIX filesystem?
7. Čo znamená single-writer contract?
8. Aký je rozdiel medzi crash-consistent a application-consistent backupom?
9. Prečo snapshot nemusí byť backup?
10. Ako disk-full ovplyvní container workload?

## Glossary impact

Relevantné pojmy: container volume, bind mount, tmpfs mount, storage driver, snapshotter, volume driver, persistent data identity, local persistent storage, network filesystem, block storage, object storage, single-writer storage, application-consistent backup, crash-consistent snapshot, restore test, storage fencing a inode exhaustion.

## Oficiálna dokumentácia

- [Docker storage overview](https://docs.docker.com/engine/storage/)
- [Docker volumes](https://docs.docker.com/engine/storage/volumes/)
- [Docker bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)
- [Docker tmpfs mounts](https://docs.docker.com/engine/storage/tmpfs/)
