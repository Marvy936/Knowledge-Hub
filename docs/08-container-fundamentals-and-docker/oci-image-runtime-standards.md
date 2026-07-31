# OCI image a runtime standards

Open Container Initiative (OCI) nedefinuje jeden container produkt. Definuje oddelené interoperability contracts pre content graph, registry distribution a low-level runtime lifecycle. Image Specification opisuje indexy, manifests, configuration a filesystem layers. Distribution Specification opisuje, ako sa manifests a blobs publikujú a získavajú cez registry API. Runtime Specification opisuje, ako prepared root filesystem a `config.json` vytvoria process v izolovanom runtime state-e. Docker, containerd alebo Kubernetes tieto contracts skladajú a pridávajú vlastné snapshots, networking, metadata, restart a orchestration semantics.

Kapitola pokračuje incidentom `CTR-PAY-80`. Atlas Payments publikuje tag `payments:10.4` ako multi-platform image. Index obsahuje amd64 aj arm64 descriptors, ale arm64 manifest odkazuje na starší binary. Security evidence je viazaná iba na index digest, zatiaľ čo vulnerability scan analyzoval amd64 platform manifest. Produkčný arm64 node teda spustí iný content, než aký testy a scan reálne overili.

## 1. Dominantný source-to-process lifecycle

```text
source a trusted build subject
→ OCI image index/manifest/config/layer graph
→ registry publication a immutable digest
→ signature/provenance/SBOM subject binding
→ pull a platform selection
→ descriptor/blob integrity verification
→ unpacked snapshot/rootfs
→ generated OCI runtime bundle
→ create/start process
→ runtime a business verification
```

„OCI-compatible“ na jednej hranici nepreukazuje úspech ďalšej. Registry môže uložiť validný manifest, ktorý nemá required platform. Pull môže uspieť, ale unpack zlyhá na disk/inode/snapshotter limite. Low-level runtime môže process spustiť, ale application nemusí byť ready.

## 2. Exact OCI release subject

```yaml
ociReleaseSubject:
  repository: registry.example/atlas/payments
  humanTag: 10.4.0
  imageIndexDigest: sha256:index104
  expectedPlatforms:
    linux/amd64:
      manifestDigest: sha256:amd104
      configDigest: sha256:cfg-amd104
    linux/arm64/v8:
      manifestDigest: sha256:arm104
      configDigest: sha256:cfg-arm104
  sourceRevision: 8f41a2c
  builder:
    id: buildkit-prod-07
    buildGraphDigest: sha256:llb104
  evidence:
    provenanceSubject: sha256:index104
    sbomSubjects:
      - sha256:amd104
      - sha256:arm104
    scanSubjects:
      - sha256:amd104
      - sha256:arm104
  registryGeneration: prod-registry-eu/replica-7
```

Production runtime record navyše zachová selected platform manifest:

```yaml
runtimeImageSelection:
  requestedReference: registry.example/atlas/payments@sha256:index104
  nodePlatform: linux/arm64/v8
  selectedManifest: sha256:arm104
  localImageId: sha256:cfg-arm104
```

Index digest a platform manifest digest majú rozdielny význam. Index identifikuje platform inventory; manifest konkrétnu runnable variantu.

## 3. OCI Image Specification graph

OCI image graph:

```text
image index (optional pri single-platform)
→ platform manifest
→ one image config descriptor
→ ordered filesystem layer descriptors
```

OCI Image Specification štandardizuje descriptor-based, content-addressed graph a image layout. citeturn888444search27turn888444search26

Descriptor obsahuje najmä:

```text
mediaType
digest
size
optional platform
optional annotations
```

Consumer:

```text
read descriptor
→ fetch bytes
→ verify size/digest
→ interpret according to mediaType
```

Digest preukazuje content identity a integritu bytes. Nepreukazuje autora, trusted build, security approval ani runtime compatibility.

## 4. Tag verzus digest

Tag je mutable repository pointer:

```text
payments:10.4.0
→ dnes sha256:index104
→ zajtra môže ukazovať na sha256:index105
```

Digest reference je immutable content identity:

```text
registry.example/atlas/payments@sha256:index104
```

Practical inspection:

```bash
docker buildx imagetools inspect \
  registry.example/atlas/payments:10.4.0

docker buildx imagetools inspect \
  registry.example/atlas/payments@sha256:index104 \
  --raw > index.json

jq -r '.manifests[] | [.platform.os,.platform.architecture,(.platform.variant // ""),.digest] | @tsv' index.json
```

Raw index preukazuje descriptors v registry response pre exact digest. Nepreukazuje, že all blobs existujú, signatures sú validné alebo tag stále ukazuje na tento index.

## 5. Platform selection

OCI platform fields typicky zahŕňajú:

```text
os
architecture
variant
optional os.version/os.features
```

Multi-platform index:

```text
sha256:index104
├── linux/amd64      → sha256:amd104
└── linux/arm64/v8   → sha256:arm104
```

Engine vyberá variant podľa node/client platform alebo explicitného override-u. Docker multi-platform docs popisujú index/list, ktorý odkazuje na platform-specific manifests. citeturn888444search7turn888444search20

Platform match však nepreukazuje:

- required CPU instruction set;
- minimum kernel version;
- dynamic-linker/libc compatibility;
- required devices;
- seccomp/LSM allowance;
- filesystem/runtime features.

## 6. Platform manifest

Manifest spája:

```text
one image config descriptor
+ ordered layer descriptors
```

Manifest digest sa zmení, ak sa zmení config, layer descriptor alebo poradie. Platform-specific SBOM a vulnerability evidence sa preto často viažu práve na manifest digest.

Practical:

```bash
docker buildx imagetools inspect \
  registry.example/atlas/payments@sha256:arm104 \
  --raw > arm64-manifest.json

jq '{config, layers}' arm64-manifest.json
```

Výstup preukazuje descriptor graph platform manifestu, nie obsah packages bez stiahnutia/analýzy configu/layers.

## 7. Image configuration

Image config môže obsahovať:

- OS/architecture;
- environment defaults;
- entrypoint a command;
- working directory;
- user;
- labels;
- exposed-port metadata;
- rootfs diff IDs;
- build history.

Practical local read-back:

```bash
docker image inspect \
  registry.example/atlas/payments@sha256:arm104 \
  --format '{{json .Config}}' | jq .
```

Image config je default contract. Runtime môže override-nuť user, command, environment, mounts a security policy. `USER 10001` v image preto nepreukazuje effective runtime UID.

## 8. Layers, blob digest a diff ID

Registry distribuuje compressed layer blobs:

```text
compressed bytes
→ descriptor digest
```

Image config `rootfs.diff_ids` identifikuje uncompressed changesets. Rovnaký uncompressed filesystem change môže mať iný compressed digest pri inom compression encodingu.

```text
compressed distribution digest
≠ uncompressed diff ID
```

Ordered layers vytvoria filesystem result cez additions, modifications a whiteouts. Image nie je jeden tarball, ale graph, čo umožňuje deduplication a independent caching.

## 9. OCI Distribution Specification

Distribution Specification štandardizuje registry API pre blob/manifest operations a repository-scoped content transfer. citeturn888444search29turn888444search25

Publication lifecycle:

```text
upload missing blobs
→ push platform manifests
→ push image index
→ attach signature/provenance/SBOM artifacts
→ registry read-back
→ immutable release record
```

Blob existence nepreukazuje, že manifest je publikovaný. Manifest push nepreukazuje complete referrer/evidence graph. Tag update nepreukazuje downstream cache invalidation.

## 10. Registry authorization

Oddelené capabilities:

```text
pull manifest/blob
push blob
push or overwrite manifest/tag
delete manifest
cross-repository blob mount
read related/referrer artifacts
admin/garbage collection
```

Runtime identity má typicky read-only pull scope. Release publisher smie zapisovať release repository, ale nemá registry-admin deletion capability. Tag mutation je kritická authorization boundary, pretože mení human reference bez zmeny consumer configuration.

## 11. Trust artifacts a subject binding

Signature, provenance, SBOM a vulnerability report musia uvádzať exact subject digest.

```text
index signature
→ schvaľuje platform inventory/index content

platform SBOM/scan
→ opisuje konkrétnu runnable variantu
```

Policy môže požadovať:

```text
trusted index signature
+ provenance for index/build graph
+ SBOM and scan for every required platform manifest
```

Digest sám nepreukazuje trusted publisher. Signature bez identity/policy verification takisto nestačí.

## 12. Complete platform evidence inventory

```yaml
expectedPlatformEvidence:
  linux/amd64:
    manifest: sha256:amd104
    sbom: present-valid
    vulnerabilityScan: present-valid
    runtimeTest: passed
  linux/arm64/v8:
    manifest: sha256:arm104
    sbom: present-valid
    vulnerabilityScan: present-valid
    runtimeTest: passed
```

Chýbajúci arm64 test nie je „amd64 pass“. Je to `INCOMPLETE_PLATFORM_EVIDENCE`.

## 13. Pull lifecycle

```text
resolve exact digest
→ fetch index/manifest
→ select platform
→ verify trust policy
→ fetch config/layers
→ verify descriptor size/digest
→ cache content
→ unpack snapshot
```

Pull success znamená, že distribution/content path bol úspešný pre selected subject. Neznamená application start ani readiness.

```bash
docker pull --platform linux/arm64 \
  registry.example/atlas/payments@sha256:index104

docker image inspect \
  registry.example/atlas/payments@sha256:index104 \
  --format 'Id={{.Id}} RepoDigests={{json .RepoDigests}} Os={{.Os}} Arch={{.Architecture}}'
```

Local image metadata preukazuje daemon-stored image/config subject. Nepreukazuje registry tag state alebo trust policy verdict, pokiaľ nie je uložený v separate evidence.

## 14. Unpack a snapshot

Engine/containerd snapshotter aplikuje ordered filesystem changesets:

```text
fetch/decompress layers
→ validate/apply tar entries and whiteouts
→ construct committed snapshot
→ create active writable snapshot for container
```

Failure boundaries:

- missing/corrupt blob;
- unsupported media/compression;
- disk/inode exhaustion;
- xattr/ownership/LSM failure;
- snapshotter/kernel incompatibility;
- malicious/invalid path semantics.

Nové Docker Engine inštalácie môžu používať containerd image store a snapshotters; klasický Docker storage-driver view preto nie je univerzálny pre každú current installation. citeturn888444search23turn888444search0

## 15. OCI Runtime Specification bundle

Runtime bundle:

```text
bundle/
├── config.json
└── rootfs/
```

`config.json` modeluje process, rootfs, mounts, namespaces, resources, capabilities, hostname, hooks a platform-specific security settings. OCI Runtime Specification definuje low-level create/start/state/kill/delete lifecycle a bundle contract. citeturn888444search28turn888444search30

Engine vytvorí runtime config z:

```text
image config defaults
+ docker run/Compose/orchestrator overrides
+ host/runtime policy
+ resolved mounts/network/resources
→ OCI config.json
```

Bundle/config subject je preto potrebný na vysvetlenie effective runtime, nie iba image digest.

## 16. Low-level runtime lifecycle

```text
create
→ isolation/rootfs/process state prepared, user process not yet running

start
→ execute user process

state
→ runtime status/PID/bundle identity

kill
→ deliver signal

delete
→ remove stopped runtime state
```

Docker daemon, containerd a shim pridávajú lifecycle management okolo low-level runtime. OCI runtime compliance neštandardizuje Docker restart policy, bridge networking, volumes alebo healthchecks.

## 17. Runtime hooks

Hooks sú privileged host-side extension points. Potrebujú exact executable digest, phase, timeout, privileges, input and failure semantics. Image-supplied alebo untrusted runtime input nesmie svojvoľne vyberať host-level hook.

Hook failure môže zanechať partial host/network/device state, hoci user process nezačal. Recovery musí poznať hook subject a cleanup contract.

## 18. Worked incident `CTR-PAY-80`: arm64 drift

Release index:

```text
amd64 → current binary S104
arm64 → stale binary S103
```

Build pipeline testovala a skenovala iba amd64, ale podpísala index.

```text
index signature valid
→ arm64 descriptor je autenticky súčasť indexu
→ nepreukazuje, že arm64 content je správny/testovaný
→ arm64 node spustí stale settlement logic
```

Recovery:

1. stop/pause arm64 rollout;
2. inventory running selected manifests;
3. correlate platform-specific tests/SBOM/scans;
4. rebuild both variants from one source subject;
5. publish new index digest;
6. verify every expected platform;
7. redeploy by digest;
8. test second pull/run on both architectures.

## 19. Worked incident: tag changed after approval

Approval referenced `payments:10.4.0`. Tag moved from `index104` to `index105` before deployment.

```text
human tag approval
→ mutable resolution later
→ different bytes run
```

Fix is approval and deployment bound to digest. Tag remains human metadata.

## 20. Worked incident: registry copy lost referrers

Promotion copied runnable index/manifests/blobs but not SBOM/provenance/signatures.

```text
destination pull succeeds
→ evidence graph incomplete
→ production policy cannot prove required artifacts
```

Promotion verifies complete expected graph in destination, not only image digest availability.

## 21. Worked incident: index-only correlation hid vulnerability

Scanner finding subject: `sha256:arm104`. Runtime inventory stored only `sha256:index104`. Incident query failed to match.

Record must store:

```text
requested index
→ selected platform manifest
→ image config/local snapshot
→ container ID
```

## 22. Competing hypotheses pri `no matching manifest`

```text
H1: index lacks platform descriptor
H2: architecture variant mismatch
H3: tag points to different index
H4: registry mirror is stale/incomplete
H5: client requested explicit wrong --platform
H6: media type unsupported by client
H7: authentication hides repository/manifest access
```

Evidence:

```bash
docker context show
docker version
docker buildx imagetools inspect reference --raw
curl/registry API logs podľa controlled auth path
docker info
```

Raw index tests H1/H2, digest resolution H3/H4, command/config H5, client version/media type H6 and registry auth audit H7.

## 23. Acceptance a forbidden paths

```text
release is digest-bound
+ expected platform inventory equals actual index
+ every platform has valid SBOM/scan/runtime test
+ signatures/provenance bind to required subjects
+ registry destination contains complete evidence graph
+ pull records selected platform manifest
+ runtime bundle/effective config is auditable
+ mutable tag approval path is rejected
+ missing-platform publication is rejected
+ second pull/run on every platform selects same digest and passes
```

## 24. Kontrolné otázky

1. Aké tri contracts OCI oddeľuje?
2. Čo descriptor preukazuje?
3. Aký rozdiel je medzi tagom, index digestom a platform manifest digestom?
4. Čo image config obsahuje a čo nepreukazuje?
5. Ako sa blob digest líši od diff ID?
6. Čo Distribution Specification štandardizuje?
7. Prečo runnable image copy nemusí preniesť trust evidence?
8. Čo pull success preukazuje a čo nie?
9. Ako unpack/snapshot failure vznikne po successful pull-e?
10. Čo tvorí OCI runtime bundle?
11. Prečo OCI runtime compliance nie je Docker feature compliance?
12. Ako sa testuje forbidden mutable-tag a incomplete-platform path?

## Glossary impact

Relevantné pojmy: OCI, Image Specification, Distribution Specification, Runtime Specification, descriptor, tag, digest, image index, platform manifest, image config, layer blob, diff ID, referrer artifact, registry publication, platform selection, snapshot, runtime bundle, config.json, low-level runtime a runtime hook.

## Primárne zdroje

- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)
- [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec)
- [Docker multi-platform builds](https://docs.docker.com/build/building/multi-platform/)

<!-- KNOWLEDGE-NAVIGATION:START -->
[← Predchádzajúca: Namespaces, cgroups a capabilities](namespaces-cgroups-capabilities.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Images, layers a copy-on-write →](images-layers-copy-on-write.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
