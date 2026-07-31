# Images, layers a copy-on-write

Container image je immutable content graph z ordered filesystem changesets a image metadata. Runtime z tohto graphu vytvorí read-only snapshot a nad neho pridá writable state konkrétnej container instance. Merged filesystem, ktorý process vidí, preto nevystihuje, kde bytes fyzicky vznikli, či zostávajú v staršom layer blob-e, či ich prekryl mount alebo či zaniknú pri recreate. Copy-on-write je storage optimization a runtime mutation model, nie persistence alebo secret-deletion guarantee.

Kapitola uzatvára incident `CTR-PAY-80`. Atlas build najprv skopíruje package-manager token, stiahne dependencies a v ďalšom Dockerfile kroku token odstráni. Final merged image token neukazuje, ale starší layer ho stále obsahuje. Runtime zároveň zapisuje reconciliation ledger do writable layeru. Pri node replacement-e sa ledger stratí, zatiaľ čo secret blob ostáva dostupný v registry/cache. Jedna chyba teda prežila delete a druhá neprežila recreate.

## 1. Dominantný source-to-runtime-filesystem lifecycle

```text
source, base digest a build inputs
→ ordered build filesystem/config transitions
→ content-addressed config a layer descriptors
→ registry/local content store
→ unpacked committed snapshot chain
→ per-container active writable snapshot
→ merged reads, copy-up, writes a whiteouts
→ explicit volume/tmpfs/persistent-data handoff
→ replacement, evidence capture a garbage collection
```

## 2. Exact image a runtime storage subject

```yaml
filesystemSubject:
  image:
    platformManifest: sha256:amd104
    configDigest: sha256:cfg104
    layers:
      - sha256:base17
      - sha256:runtime22
      - sha256:deps31
      - sha256:app44
  localStore:
    engineHost: worker-node-17
    imageStoreMode: containerd-snapshotter
    snapshotter: overlayfs
    committedSnapshot: snap-771
  container:
    id: 2d9f...
    writableSnapshot: active-902
    readOnlyRootfs: true
  mounts:
    - destination: /tmp
      type: tmpfs
    - destination: /var/cache/atlas
      type: volume
      source: atlas-cache-10-4
  persistentBusinessData:
    owner: managed-postgresql/db17
```

Image digest neidentifikuje writable layer, volumes, bind mounts ani tmpfs content.

## 3. Layer je changeset

Layer nie je celý filesystem. Obsahuje additions, modifications, metadata changes, links a deletion markers oproti previous view.

```text
layer B17: base userspace
→ layer R22: runtime libraries
→ layer D31: dependencies
→ layer A44: application binary
→ final merged image rootfs
```

Poradie je súčasť identity. Rovnaké blobs v inom poradí môžu vytvoriť iný rootfs a manifest digest.

## 4. Compressed blob digest verzus diff ID

Registry descriptor typicky identifikuje compressed layer bytes. Image config `rootfs.diff_ids` identifikuje uncompressed changesets.

```text
compressed tar+compression bytes
→ distribution digest

decompressed tar stream
→ diff ID
```

Rovnaký uncompressed changeset môže mať odlišný distribution digest pri inom compression encodingu. Forensics musí vedieť, ktorú identity porovnáva.

## 5. Content-addressed deduplication

```text
Image X ─┐
         ├→ shared base layer B17
Image Y ─┘
```

Content addressing umožňuje integrity verification, deduplication, immutable references a reference-aware garbage collection. Digest však nepreukazuje bezpečnosť alebo trusted origin.

Deletion jedného tagu nemusí uvoľniť layer, ak ho stále referencuje iný manifest, running/stopped snapshot, lease alebo build cache.

## 6. Merged filesystem view

Overlay/snapshot model processu prezentuje jeden path tree:

```text
read path
→ active writable layer
→ highest lower layer containing path
→ older layers
→ respect whiteout/opaque markers
```

Konkrétna implementation môže používať overlayfs snapshotter, klasický `overlay2`, block snapshot alebo platform-specific driver. Docker dokumentácia rozlišuje storage drivers a containerd snapshotters; current installation sa preto diagnostikuje cez `docker info`, nie podľa historického predpokladu. citeturn888444search0turn888444search23

```bash
docker info --format '{{json .DriverStatus}}'
docker info | grep -E 'Storage Driver|containerd image store'
```

Output preukazuje daemon-reported storage implementation, nie complete filesystem health.

## 7. Copy-up pri prvom write

Lower layer je immutable. Pri write do lower file-u runtime vytvorí upper copy:

```text
open lower /app/data.bin for write
→ copy-up content/metadata
→ mutate upper copy
→ subsequent reads see upper version
```

Dôsledky:

- prvý write môže byť drahý;
- veľký file sa môže copy-upnúť celý;
- upper disk usage môže prudko rásť;
- runtime state je private pre container instance;
- write-heavy database vo writable layeri má zlý performance/recovery model.

Aj `chmod`, `chown` alebo xattr change môže vyvolať metadata/full copy-up podľa implementation.

## 8. Whiteouts a delete illusion

Ak lower layer obsahuje `/root/token`, neskorší layer ho nemôže z historical contentu vymazať. Vytvorí deletion marker:

```text
layer N: token bytes exist
layer N+1: whiteout hides path
merged rootfs: token absent
historical blob N: token bytes remain
```

Rizikový Dockerfile:

```dockerfile
COPY package-token /run/package-token
RUN install-dependencies --token-file /run/package-token
RUN rm -f /run/package-token
```

Token je v `COPY` layeri. Bezpečný BuildKit secret mount nevkladá secret do layer changesetu:

```dockerfile
# syntax=docker/dockerfile:1
RUN --mount=type=secret,id=package_token \
    install-dependencies --token-file /run/secrets/package_token
```

Ak secret už vstúpil do build contextu/layeru/cache/logu, treba ho rotovať. Rebuild s `rm` starý credential nerevokuje.

## 9. Opaque directories

Opaque marker môže skryť lower-directory children. Naivné rozbalenie všetkých tarov bez OCI whiteout semantics nevytvorí správny final rootfs. To je relevantné pri custom scanners, archive exporte a snapshot migration.

## 10. Dockerfile instruction a successor state

Build instruction vytvára filesystem a/alebo image-config transition:

```text
prior rootfs/config
+ instruction
+ resolved inputs
→ successor rootfs/config
→ cache record
```

`ENV`, `USER`, `ENTRYPOINT` môžu meniť config bez veľkého filesystem layeru. `RUN`, `COPY`, `ADD` typicky menia rootfs. Build history nie je complete oracle pre obsah layers alebo secrets.

## 11. Layer ordering a cache reuse

Efficient deterministic pattern:

```dockerfile
COPY package-lock.json package.json ./
RUN npm ci --omit=dev
COPY src/ ./src/
RUN npm run build
```

Lockfiles sa menia menej často než source, takže dependency cache sa znovu použije. Correctness však vyžaduje, aby cache key pokrýval všetky relevantné inputs. Hidden environment, mutable package index alebo undeclared generated file môže vytvoriť stale artifact.

Cache miss má znížiť výkon, nie zmeniť výsledok. Controlled no-cache rebuild overuje clean-room correctness:

```bash
docker buildx build --no-cache --pull \
  --platform linux/amd64 \
  --tag atlas/payments:clean-test .
```

`--no-cache` ignoruje instruction cache, ale network dependencies môžu byť stále mutable. Reproducibility potrebuje pinned inputs a local/verified dependency sources.

## 12. Runtime writable layer

Writable snapshot môže obsahovať:

- logs;
- temporary files;
- package install/hotfix;
- application cache;
- downloaded plugins;
- attacker artifacts;
- business data omylom.

```bash
docker diff atlas-payments
```

Output ukáže added/changed/deleted paths podľa Docker diff modelu. Nepreukazuje bytes, process-open deleted files, mounted volume changes ani all xattr/metadata semantics.

Restart existing container môže writable layer zachovať. `docker rm` a recreate z image ju odstránia.

## 13. Path classification

Každý writable path:

### Ephemeral

Môže zaniknúť:

```text
/tmp
bounded scratch
rebuildable cache
```

### Persistent business data

Má external identity, backup a restore:

```text
database
uploads
durable queue
audit records
```

### Reproducible configuration/secret

Musí byť znovu injektovateľný z versionovaného config alebo secret authority.

### Incident evidence

Musí byť exportované mimo disposable instance pred delete.

## 14. Mount obscuring

Mount na destination prekryje image content:

```text
image: /var/lib/atlas/default.db exists
volume mounted at /var/lib/atlas
process sees volume content, image file hidden
```

„File je v image inspect/exporte, ale runtime ho nevidí“ môže byť mount issue, nie broken layer.

```bash
docker inspect atlas-payments --format '{{json .Mounts}}' | jq .
container_pid="$(docker inspect -f '{{.State.Pid}}' atlas-payments)"
nsenter -t "$container_pid" -m findmnt -R /var/lib/atlas
```

## 15. Read-only root filesystem

```bash
docker run --read-only \
  --tmpfs /tmp:size=128m,mode=1777 \
  --mount type=volume,src=atlas-cache,dst=/var/cache/atlas \
  registry.example/atlas/payments@sha256:amd104
```

Read-only rootfs znižuje implicitné runtime mutations. Nepreukazuje, že mounts sú read-only, volume neobsahuje executable malware alebo application nepotrebuje unmodeled writable path.

## 16. Snowflake container

```bash
docker exec atlas-payments sh -c 'apk add curl && vi /app/config'
```

Effective runtime sa odchýli od image digestu. Replacement fix stratí, druhá replica ho nemá a image SBOM/scan ho nevidia.

Authoritative recovery:

```text
capture evidence
→ source/Dockerfile/config fix
→ rebuild/test/scan/sign
→ publish new digest
→ recreate
→ verify second instance
```

`docker commit` môže byť forensic snapshot, ale nie automaticky trusted release artifact.

## 17. Image size verzus disk reclaim

Rozlišuj:

```text
compressed registry size
uncompressed content size
shared layer bytes
committed snapshot usage
active writable usage
volume usage
build cache
metadata/inodes
```

```bash
docker system df -v
docker ps --size
df -h
df -i
```

CLI estimates a filesystem metrics testujú rozdielne subjects. `docker system df` nemusí presne predpovedať reclaim pri current leases/shared snapshots.

## 18. Reference graph a GC

Safe GC:

```text
retained image/index manifests
→ referenced config/layer blobs
→ container snapshots
→ leases/pins
→ build cache records
→ related artifacts podľa policy
→ identify unreachable content
→ delete with fencing
```

`docker system prune` je destructive policy, nie diagnosis. Pred incidentným prune zachovaj images, containers, snapshots a build-cache evidence.

## 19. Base image inheritance

Base digest prináša packages, libc/loader, CA certificates, users/groups, timezone data a vulnerabilities. Mutable base tag znamená, že rovnaký Dockerfile commit môže vytvoriť nový image.

```dockerfile
FROM debian:bookworm@sha256:exact-base
```

Digest pinning poskytuje reproducibility, ale security updates sa neobjavia samé. Dependency automation musí vedome navrhnúť nový digest a spustiť testy.

## 20. Minimal images

Scratch/distroless znižujú runtime content, ale musia explicitne riešiť:

- dynamic libraries/interpreter;
- CA certs;
- timezone/locale;
- user identity files;
- DNS/runtime dependencies;
- debugging/evidence strategy.

Menšia size nie je automaticky menší effective attack surface, ak container beží privileged alebo mountuje host socket.

## 21. Worked incident `CTR-PAY-80`: secret removed but retained

```text
COPY token creates layer L1
→ dependency install creates L2
→ rm token creates whiteout L3
→ merged view clean
→ registry blob L1 still contains credential
```

Recovery:

1. revoke token;
2. remove it from build context/history;
3. rebuild with secret mount;
4. publish new digest;
5. remove/expire affected registry/cache artifacts podľa policy;
6. scan layer archives a build logs;
7. test forbidden secret-in-layer fixture.

## 22. Worked incident: reconciliation ledger lost

Application zapisovala pending external settlement IDs do `/var/lib/atlas/pending` v writable layeri.

```text
container replace
→ upper snapshot deleted
→ external provider side effects remain
→ local reconciliation knowledge lost
```

Recovery rekonštruuje ledger z authoritative database/events/provider query a vykoná idempotentnú reconciliation. Path sa presunie do durable owned store.

## 23. Worked incident: disk growth after chmod

Startup script recursive `chown -R` nad veľkou lower-layer directory vyvolal copy-up množstva files. Application nič explicitne nezapisovala, ale upper usage explodovala.

Evidence:

- `docker diff`/snapshot usage;
- process audit;
- layer directory size;
- startup script;
- storage driver metrics.

Fix nastaví ownership pri build-e cez `COPY --chown` alebo správne volume permissions.

## 24. Competing hypotheses pri missing file

```text
H1: file nikdy nebol v selected platform manifest-e
H2: later whiteout/opaque directory ho skryla
H3: mount obscures path
H4: runtime mutation removed it
H5: wrong working directory/path
H6: UID/LSM makes it inaccessible, nie missing
H7: pull/unpack snapshot incomplete/corrupt
```

Evidence:

```bash
docker image inspect exact-digest
docker history --no-trunc exact-digest
docker inspect container
docker diff container
nsenter -t "$container_pid" -m findmnt -R /target
```

Layer extraction/content analysis testuje H1/H2, mounts H3, diff H4, process/config H5, permissions/audit H6 and snapshot/daemon errors H7.

## 25. Acceptance a forbidden paths

```text
image/layer/snapshot/writable/volume identities sú oddelené
+ secrets nevstupujú do build context/layers/cache
+ runtime rootfs is read-only where feasible
+ writable paths have explicit classes and limits
+ business data survive recreate through external owner
+ no interactive snowflake mutation is required
+ base image is digest-pinned with update lifecycle
+ GC preserves referenced runtime/evidence content
+ secret-delete fixture still detects historical layer
+ second container reproduces same app state without old upper layer
```

## 26. Kontrolné otázky

1. Prečo layer nie je full filesystem?
2. Ako sa distribution digest líši od diff ID?
3. Čo copy-up znamená pre performance a disk?
4. Prečo `rm` v neskoršom layeri neodstráni secret?
5. Čo `docker diff` preukazuje a čo nie?
6. Ako mount obscures image content?
7. Prečo writable layer nie je business storage?
8. Čo read-only rootfs chráni a čo nechráni?
9. Prečo snowflake hotfix nie je release?
10. Prečo tag deletion nemusí reclaim-nuť layer bytes?
11. Ako base digest pinning súvisí so security updates?
12. Ako sa testuje forbidden secret layer a second-container persistence path?

## Glossary impact

Relevantné pojmy: image layer, changeset, descriptor digest, diff ID, content-addressed storage, merged filesystem, copy-on-write, copy-up, whiteout, opaque directory, snapshotter, committed snapshot, active writable layer, mount obscuring, read-only rootfs, snowflake container, build cache a garbage collection.

## Primárne zdroje

- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [Docker storage drivers](https://docs.docker.com/engine/storage/drivers/)
- [Docker OverlayFS storage driver](https://docs.docker.com/engine/storage/drivers/overlayfs-driver/)
- [Docker volumes](https://docs.docker.com/engine/storage/volumes/)

<!-- KNOWLEDGE-NAVIGATION:START -->
[← Predchádzajúca: OCI image a runtime standards](oci-image-runtime-standards.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Registries →](registries.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
