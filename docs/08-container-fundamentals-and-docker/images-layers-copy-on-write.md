# Images, layers a copy-on-write

Container image je immutable content graph zložený z metadata a ordered filesystem changesets. Runtime z tohto graphu vytvorí read-only snapshot a nad neho pridá writable state konkrétnej container instance.

Dominantný lifecycle:

```text
source a pinned build inputs
→ ordered filesystem changesets
→ content-addressed image manifest/config
→ registry a local content cache
→ unpacked read-only snapshot
→ per-container writable layer
→ merged filesystem reads/writes/deletes
→ explicit persistence handoff
→ replacement, reference tracking a garbage collection
```

Tento model vysvetľuje naraz:

- prečo viac containers zdieľa image bytes;
- prečo prvý write do lower-layer file-u môže byť drahý;
- prečo neskoršie `rm` neodstráni secret zo staršieho layeru;
- prečo runtime mutation nie je súčasť image identity;
- prečo dáta vo writable layeri zaniknú pri replacement-e;
- prečo delete tagu nemusí okamžite uvoľniť disk.

## 1. Atlas image a runtime-state subject

Atlas Payments release `3.13.0` používa platform manifest `MAMD313`:

```text
image config: CAMD313
layer B17: base userspace
layer R22: language/runtime dependencies
layer D31: application dependency artifacts
layer A44: application binary and static assets
layer C09: default configuration metadata
```

Runtime container `AP-313-07` pridá:

```text
snapshot/rootfs: SNAP-771
writable layer: UPPER-771
runtime config generation: C44
persistent business data: managed PostgreSQL DB17
cache path: /var/cache/atlas → bounded ephemeral volume
upload path: object storage
/tmp: tmpfs
```

Úspešný outcome:

```text
manifest a ordered layers zodpovedajú schválenému image subjectu
+ unpacked rootfs je integrity-verified
+ runtime mutations sú iba v explicitne ephemeral paths
+ business data má external persistent owner
+ replacement container reprodukuje application state z image + runtime config
+ secrets nie sú v žiadnom image layeri ani build metadata
+ GC neodstráni referenced content a odstráni skutočne orphaned content
```

## 2. Image, snapshot a container sú odlišné subjects

### Image subject

Content-addressed artifact:

```text
manifest
→ config
→ ordered layer descriptors
```

### Local snapshot subject

Runtime-specific unpacked representation image layers:

```text
verified blobs
→ decompression
→ apply changesets
→ snapshot/snapshot-chain identity
```

### Container runtime subject

```text
read-only snapshot
+ writable upper layer
+ mounts/volumes/tmpfs
+ process/network/security config
→ running container instance
```

Image digest preto neidentifikuje runtime writable state, mounted secrets ani external volumes.

## 3. Filesystem layer ako changeset

Layer nie je plný filesystem. Reprezentuje rozdiel oproti predchádzajúcemu view:

- added files/directories;
- modified file content;
- metadata changes;
- ownership a permissions;
- links;
- whiteouts pre deletion;
- opaque-directory semantics podľa format contractu.

Ordered application:

```text
B17
→ apply R22
→ apply D31
→ apply A44
→ apply C09
→ final image rootfs view
```

Poradie je súčasť identity. Rovnaké layer blobs v inom poradí môžu vytvoriť iný filesystem a manifest.

## 4. Content-addressed storage

Descriptor digest viaže exact bytes. Registry a runtime môžu deduplikovať shared content:

```text
Image X ─┐
         ├→ shared layer B17
Image Y ─┘
```

Výhody:

- integrity verification;
- immutable references;
- deduplication;
- cache reuse;
- promotion exact contentu;
- reference-based GC.

Content digest nehovorí, či layer je bezpečný, podporovaný alebo pochádza z trusted build-u. To rieši provenance, policy, scan a release evidence.

## 5. Merged filesystem view

Overlay/snapshot implementation prezentuje processu jeden path tree z viacerých vrstiev.

Zjednodušený lookup:

```text
read /app/config.yml
→ pozri writable upper layer
→ ak path nie je prítomný, hľadaj v najvyššom lower layeri
→ pokračuj smerom k base layeru
→ rešpektuj whiteout/opaque markers
```

Pri overlay-style modeli sa často rozlišuje:

- `lowerdir` — read-only layer/snapshot chain;
- `upperdir` — per-container writable state;
- `workdir` — interná filesystem operation state;
- `merged` — view pre container process.

Konkrétna implementácia môže byť overlayfs, native snapshotter, block-based snapshotter alebo platform-specific model. Semantic contract je dôležitejší než názov drivera.

## 6. Copy-on-write a copy-up

Read lower-layer file-u môže byť zdieľaný. Pri prvom write runtime nemôže meniť immutable lower content:

```text
open lower file for write
→ copy-up file/metadata do upper layeru
→ vykonaj mutation nad upper copy
→ ďalšie reads vidia upper version
```

Dôsledky:

- prvý write môže mať vyššiu latency;
- veľký file sa môže skopírovať celý aj pri malej zmene podľa filesystem semantics;
- upper-layer disk usage môže prudko narásť;
- zdieľaný page cache a storage behavior závisí od implementation;
- runtime mutation zostáva lokálna konkrétnej instance.

Database alebo write-heavy workload vo writable layeri môže trpieť performance a recovery problémami aj vtedy, keď technicky funguje.

## 7. Metadata copy-up

Zmena ownershipu, mode, xattr alebo inej metadata môže tiež vyvolať copy-up podľa implementation.

```text
chmod/chown lower file
→ upper representation vznikne
→ container už používa private copy
```

Pri diagnostike disk growth nestačí hľadať iba explicitné application writes. Package manager, permission-fixing init script alebo log rotation môže modifikovať veľké množstvo lower paths.

## 8. Deletion a whiteouts

Immutable lower file sa fyzicky neodstráni z historického layeru. Novšia vrstva vytvorí marker, ktorý ho skryje v merged view.

```text
layer N: /root/token.txt exists
layer N+1: whiteout /root/token.txt
merged view: file absent
historical layer N: bytes stále existujú
```

Preto:

```dockerfile
RUN copy-secret
RUN use-secret && rm secret
```

môže zachovať secret v prvom layeri. Bezpečný build používa secret mount, ktorý nevstupuje do layer changesetu, a po exposure credential rotuje.

## 9. Opaque directories

Ak novšia vrstva nahradí celý directory view, opaque marker môže skryť children z lower layers. To ovplyvňuje:

- extraction semantics;
- diff/forensics;
- migration medzi snapshotters;
- image-size interpretation;
- unexpected missing files.

Consumer musí aplikovať OCI changeset semantics, nie iba naivne rozbaliť tar archívy do jedného directory bez whiteout handlingu.

## 10. Build instruction a layer boundary

Build engine vytvára cache a filesystem transitions podľa instruction graphu. Nie každá instruction musí vytvoriť non-empty filesystem layer, ale každá môže meniť image config alebo history.

Dôležitý model:

```text
build instruction
+ current rootfs/config state
+ resolved inputs
→ successor filesystem/config state
→ cache record a artifact evidence
```

Layer boundary ovplyvňuje:

- čo zostane v history;
- čo je zdieľateľné;
- cache invalidation;
- secret exposure;
- final size;
- forensic reconstruction.

## 11. Layer ordering a cache chain

Stabilné inputs sa často spracujú skôr než volatile source:

```text
base digest
→ package metadata/lock files
→ dependency install
→ application source
→ build artifact
```

Ak sa `COPY . .` vykoná pred dependency install, zmena jedného source file-u invaliduje celý downstream dependency layer.

Optimalizácia však nesmie meniť correctness. Layer ordering musí stále zachovať:

- exact dependency inputs;
- complete source/artifact handoff;
- security updates;
- clean-build reproducibility;
- final runtime content.

## 12. Cache nie je source of truth

Build cache je memoizácia predchádzajúcej transition, nie autoritatívny dependency store ani dôkaz správnosti.

Riziká:

- mutable package indexes;
- unpinned base tag;
- stale external download;
- cache key bez hidden inputu;
- cross-branch alebo cross-tenant poisoning;
- platform-specific record reuse;
- secret-bearing cache export;
- local cache maskujúca missing dependency.

Dôveryhodný build potrebuje clean-room alebo controlled-cache verification:

```text
exact source + locks + base digest + toolchain
→ build bez correctness dependence na local cache
→ compare expected artifact/runtime outcome
```

## 13. Image config a history nie sú filesystem oracle

Image config/history pomáhajú vysvetliť build, ale nemusia úplne ukázať:

- obsah každého layeru;
- files odstránené neskôr;
- secret v tar/xattr;
- generated package content;
- final effective runtime mounts;
- provenance skutočného source-u.

Forensics používa kombináciu:

```text
manifest/config/history
+ exact layer extraction
+ merged rootfs analysis
+ SBOM
+ provenance
+ runtime writable diff
```

## 14. Writable container layer

Upper layer zachytáva runtime rootfs mutations:

- application-generated files;
- package install vykonaný za behu;
- logs bez external sinku;
- caches;
- downloaded plugins;
- attacker changes;
- permission fixes;
- temporary files.

Je typicky viazaná na container instance. Restart tej istej instance ju môže zachovať podľa platformy, ale remove/recreate ju spravidla stratí.

Preto runtime identity potrebuje rozlišovať:

```text
restart existing instance
≠ replace with new instance from image
```

## 15. Persistence classification

Každý writable path má dostať triedu:

### Ephemeral

Môže zaniknúť pri replacement-e:

- `/tmp`;
- rebuildable cache;
- transient sockets;
- scratch workspace.

### Persistent business state

Musí mať external owner:

- database records;
- uploads;
- durable queues;
- audit trail;
- customer-generated content.

### Configuration/secret state

Má byť znovu injektovateľný z versionovaného alebo secret-management source-u, nie manuálne zachovaný z old containeru.

### Incident evidence

Logs, traces a relevant runtime metadata sa musia exportovať pred zánikom instance.

## 16. Volumes a mounts obchádzajú image layer model

Mounted path prekryje image content na rovnakom destination path-e:

```text
image obsahuje /var/lib/atlas/default.db
→ volume mount na /var/lib/atlas
→ process vidí volume content
→ image file je obscured
```

Volume alebo bind mount má vlastný lifecycle, ownership, backup, security label a performance model. Image digest neidentifikuje mounted content.

To je dôvod, prečo „funguje v image inspection, chýba v runtime“ môže byť mount-obscuring problém, nie broken layer.

## 17. Read-only root filesystem

Read-only rootfs zabraňuje writes do root snapshotu/writable layeru podľa runtime implementation a policy.

Výhody:

- odhaľuje implicitné write assumptions;
- znižuje persistence runtime mutation a malware;
- približuje runtime k immutable artifactu;
- zjednodušuje diff a recovery model.

Workload potrebuje explicitné writable paths s:

- ownerom;
- size limitom;
- persistence class;
- cleanup policy;
- permissions/labels;
- backup podľa potreby.

## 18. Runtime mutation a snowflake container

Interactive package install alebo hot edit:

```text
image MAMD313
+ local upper-layer mutation P1
→ effective runtime ≠ declared artifact
```

Dôsledky:

- replacement odstráni opravu;
- ďalšia instance ju nemá;
- image scan/SBOM ju nemusí vidieť;
- incident evidence je viazaná na jednu instance;
- rollout je nekonzistentný.

Recovery path je rebuild successor image-u a redeploy, nie export náhodného upper layeru ako neauditovaný nový baseline.

## 19. Layer size a effective disk usage

Rozlišuj:

```text
compressed registry transfer size
uncompressed layer size
shared local content size
snapshot filesystem usage
per-container upper usage
volume usage
build cache
metadata/inodes
```

CLI „image size“ nemusí byť množstvo disku uvoľnené pri deletion. Shared layer zostane, ak ho používa iný manifest, snapshot alebo build cache.

## 20. Reference graph a garbage collection

GC nemá začínať od tagov, ale od reachable content graphu:

```text
retained manifests/indexes
→ referenced config/layer blobs
→ running/stopped container snapshots
→ leases/pins
→ build cache records
→ related artifacts podľa policy
```

Safe GC lifecycle:

```text
mark retained roots
→ traverse references
→ protect active uploads/leases
→ identify unreachable content
→ delete according to retention
→ verify runtime/recovery invariants
```

Race medzi pull/create a GC môže poškodiť runtime, ak implementation nemá správne leases/fencing.

## 21. Base image ako inherited supply chain

Base layer chain prináša:

- userspace packages;
- libc a loader;
- CA certificates;
- timezone data;
- users/groups;
- package metadata;
- vulnerabilities;
- support lifecycle.

Tag base image-u je mutable input. Reproducible subject používa digest a explicitnú update policy.

Menší image môže znížiť surface a transfer, ale nie je automaticky bezpečnejší. Chýbajúce CA, user data alebo observability môžu spôsobiť runtime alebo incident-response failure.

## 22. Scratch a distroless runtime

Minimal runtime musí explicitne obsahovať alebo externým contractom poskytovať:

- executable/interpreter;
- dynamic libraries;
- CA certificates;
- timezone/locale podľa potreby;
- user/group identity metadata;
- DNS/runtime dependencies;
- debugging strategy.

Debugging nemusí znamenať shell v production image. Môže používať ephemeral debug workload, host tools, core dumps podľa policy alebo observability endpoints.

## 23. Multi-stage handoff

Multi-stage build oddeľuje build rootfs od final runtime rootfs:

```text
builder stage
→ compile/test artifact
→ narrow verified copy
→ final runtime stage
```

Narrow handoff znižuje pravdepodobnosť, že final image obsahuje:

- compiler/toolchain;
- source tree;
- package cache;
- credentials;
- test outputs;
- unrelated build dependencies.

Final image provenance musí stále dokazovať, že copied artifact pochádza z testovaného graphu.

## 24. Worked failure: secret bol odstránený, ale stále bol v image

Build vykonal:

```dockerfile
COPY .npmrc /root/.npmrc
RUN npm ci
RUN rm /root/.npmrc
```

Mechanizmus:

```text
COPY vytvorí layer s plaintext tokenom
→ npm install použije token
→ neskorší layer pridá whiteout
→ merged view token neukazuje
→ starší layer bytes zostávajú pullnuteľné
```

Required response:

- credential okamžite revoke/rotate;
- odstrániť secret z build contextu a history;
- rebuildnúť image z clean graphu so secret mountom;
- verify všetky layers a metadata;
- redeploy successor digest;
- riešiť registry retention/history podľa incident policy.

## 25. Worked failure: malá runtime zmena skopírovala veľký lower file

Atlas process aktualizoval jeden field v 4 GiB local database file uloženom v image lower layeri.

```text
first write
→ copy-up celého file-u podľa storage semantics
→ upper usage narastie o približne 4 GiB
→ write latency a node disk pressure
```

Image nemá obsahovať mutable production database. Dáta patria do explicitného persistent storage s vhodným filesystem a backup modelom.

## 26. Worked failure: replacement odstránil pending state

Worker ukladal durable retry ledger do `/var/lib/atlas/retry.db` vo writable layeri.

```text
container healthy
→ node drain/replacement
→ old upper layer deleted
→ successor container starts from clean image
→ retry identity a pending work zmiznú
```

Chyba nie je v CoW. Je v nesprávnej persistence classification. Recovery potrebuje business reconciliation a external durable ledger.

## 27. Worked failure: delete tagu neuvoľnil disk

Operator odstránil `payments:3.12.0`, ale bytes zostali.

Possible references:

- iný tag/index odkazuje na rovnaké manifests;
- running/stopped container má snapshot lease;
- build cache používa layers;
- retention drží untagged manifest;
- related artifact graph alebo replication policy drží subject;
- GC ešte neprebehlo.

Tag je pointer, nie storage allocation unit.

## 28. Worked failure: cache maskovala missing build input

Lokálny build prešiel, pretože dependency layer bol v cache. Clean CI worker zlyhal, lebo private package už nebolo dostupné a lock/artifact mirror contract bol neúplný.

```text
cache hit preskočí network resolution
→ local build green
→ clean build potrebuje chýbajúci external input
→ reproducibility claim zlyhá
```

Cache nesmie byť jediná kópia release dependency.

## 29. Causal troubleshooting walkthrough: scanner stále nachádza zrušený secret

Tím odstránil secret zo source-u aj final merged filesystemu, ale scanner stále reportuje token v image digest-e.

### 1. Zafixuj image a scan subject

Zaznamenaj:

- source/build revision a build context inventory;
- exact manifest/config/layer digests;
- base image digest;
- build args, secret mounts a provenance;
- scanner version, scope a finding location;
- registry/source/cache copies;
- successor vs. old deployment digests;
- credential revocation status.

### 2. Súťažiace hypotézy

1. Secret zostal v staršom filesystem layeri a je iba whiteoutnutý.
2. Secret je v image config/history/build argument metadata.
3. Secret je v archive/package/cache file-e vo final layeri.
4. Base image už obsahovala matching value alebo test fixture.
5. Build context zahŕňal editor backup, `.env` alebo Git history artifact.
6. Scanner analyzuje starý digest alebo registry mirror cache.
7. Multi-platform index obsahuje neopravený variant.
8. Related SBOM/provenance artifact obsahuje sensitive value.
9. Finding je false positive alebo secret-like test data.
10. Runtime upper layer alebo volume, nie image, obsahuje secret.

### 3. Diskriminačné observation points

- inspect index a všetky platform manifests;
- extract/search každý exact layer, vrátane deleted paths;
- inspect config/history a annotations;
- inventory build context a final filesystem archives;
- compare scanner subject digest a deployment digest;
- inspect base image chain;
- inspect referrer artifacts podľa access policy;
- separate image, runtime upper a mounted-volume scans;
- provider audit potvrdzujúci revocation.

### 4. Containment

Považuj credential za kompromitovaný, obmedz pull/deploy old digestu a zachovaj incident evidence. Samotné „scanner finding možno zmizne po GC“ nie je containment.

### 5. Recovery

- historical layer → clean rebuild bez secretu a bez reuse kontaminovaného stage/layeru;
- metadata → odstráň sensitive build args/annotations a rebuild;
- archived file/build context → zúž context a `.dockerignore`, odstráň artifact;
- base image → vyber fixed base digest;
- platform gap → rebuild všetky required variants a successor index;
- stale scan subject → oprav correlation a rescan exact running manifests;
- runtime/volume exposure → rotate secret a oprav runtime injection/cleanup path;
- false positive → dokumentuj subject-bound suppression bez zobrazenia secretu.

### 6. Over pôvodný outcome

Potvrď revocation starej hodnoty, layer-by-layer clean successor image, complete platform inventory, trusted provenance, exact production redeploy a absence secretu v image, runtime logs/artifacts a persistent mounts podľa scope-u.

### 7. Posuň control skôr

Pridaj build-context allowlist, secret mounts, layer-aware scanning pred publication, multi-platform completeness, source-to-deployed-digest correlation a mandatory credential revocation workflow.

## 30. Referenčné pravidlá

- Image, unpacked snapshot a runtime container sú odlišné subjects.
- Layer je ordered filesystem changeset, nie celý filesystem.
- Digest umožňuje integrity a deduplication, nie trust verdict.
- Merged read používa najvyššiu visible path verziu a rešpektuje whiteouts.
- First write do lower file-u môže vyvolať copy-up a veľký disk/latency cost.
- Deletion v novšom layeri neodstráni bytes zo staršieho layeru.
- Build cache je performance optimization, nie source of truth.
- Image history nie je úplný filesystem alebo security audit.
- Writable layer je per-instance runtime state, nie durable business storage.
- Mount môže prekryť image content a má vlastný lifecycle.
- Read-only rootfs potrebuje explicitné writable-path contracts.
- Runtime mutation vytvára snowflake container mimo image identity.
- Tag deletion nie je blob deletion; GC sleduje reference graph.
- Secret exposure v layeri vyžaduje clean rebuild aj credential revocation.

## 31. Kontrolné otázky

1. Ako sa líši image subject, snapshot subject a container runtime subject?
2. Prečo poradie filesystem changesets ovplyvňuje final rootfs?
3. Ako funguje merged lookup a copy-up?
4. Prečo metadata operation môže zvýšiť upper-layer usage?
5. Ako whiteout skryje, ale neodstráni lower bytes?
6. Prečo cache nemôže byť jediný dependency source?
7. Ktoré writable paths môžu byť ephemeral a ktoré potrebujú external ownera?
8. Ako volume mount môže skryť image content?
9. Prečo delete tagu nemusí uvoľniť disk?
10. Aké observation points potvrdia secret v layeri, metadata, runtime upper alebo volume?

## Glossary impact

Relevantné pojmy: image content subject, snapshot subject, writable-layer subject, filesystem changeset, ordered layer chain, merged filesystem lookup, copy-on-write, copy-up, metadata copy-up, whiteout, opaque directory, build transition, cache correctness boundary, runtime mutation, snowflake container, persistence classification, mount obscuring, reference graph, snapshot lease a layer-aware secret incident.

## Oficiálna dokumentácia

- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [Docker storage drivers](https://docs.docker.com/engine/storage/drivers/)
- [Images and layers](https://docs.docker.com/get-started/docker-concepts/building-images/understanding-image-layers/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OCI image a runtime standards](oci-image-runtime-standards.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Registries →](registries.md)
<!-- KNOWLEDGE-NAVIGATION:END -->