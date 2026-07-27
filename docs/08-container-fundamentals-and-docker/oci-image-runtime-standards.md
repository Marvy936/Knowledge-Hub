# OCI image a runtime standards

Open Container Initiative (OCI) nedefinuje jeden container produkt. Definuje oddelené interoperability contracts pre tri rôzne transitions:

- **Image Specification** — ako sa popíše content-addressed image graph;
- **Distribution Specification** — ako sa manifests a blobs publikujú a získavajú cez registry API;
- **Runtime Specification** — ako sa prepared root filesystem a runtime configuration zmenia na izolovaný process lifecycle.

Dominantný end-to-end model:

```text
source a build subject
→ OCI image graph
→ registry publication
→ immutable reference a platform selection
→ trust/referrer verification
→ pull a content validation
→ unpacked snapshot/rootfs
→ generated OCI runtime bundle
→ low-level runtime create/start
→ process a deployment evidence
```

„OCI-compatible“ na jednej hranici negarantuje úspech na všetkých ďalších hraniciach. Registry môže artifact uložiť, hoci neobsahuje správnu platformu. Runtime môže bundle spustiť, hoci application nie je ready. Digest môže dokazovať content identity, ale nie dôveryhodnosť autora.

## 1. Atlas OCI release subject

Atlas Payments release `3.13.0` publikuje multi-platform image:

```text
repository: registry.atlas.example/payments
human tag: 3.13.0
image index digest: IDX313
linux/amd64 manifest: MAMD313
linux/arm64 manifest: MARM313
amd64 config descriptor: CAMD313
arm64 config descriptor: CARM313
amd64 layer descriptors: L-A1, L-A2, L-A3
arm64 layer descriptors: L-R1, L-R2, L-R3
SBOM subject: IDX313
signature/provenance subject: IDX313
builder subject: BUILD-882
source revision: S417
```

Production deployment na `linux/amd64` node musí dokázať:

```text
approved index IDX313
→ selected manifest MAMD313
→ verified descriptors a blobs
→ trusted signature/provenance pre správny subject
→ unpacked rootfs z MAMD313
→ runtime bundle RB-991
→ process subject AP-313-07
→ deployment record obsahuje IDX313 aj MAMD313
```

Index digest a platform manifest digest majú odlišný význam. Jeden identifikuje platform inventory; druhý konkrétny runnable variant.

## 2. Špecifikácie ako oddelené contracts

### OCI Image Specification

Definuje content graph:

```text
image index, ak je multi-platform
→ platform manifest
→ image configuration
→ ordered filesystem layer descriptors
```

### OCI Distribution Specification

Definuje registry interactions pre:

- blob upload/download;
- manifest push/pull;
- tag resolution;
- content existence a upload sessions;
- repository scoping;
- related artifact discovery podľa podporovaného referrer modelu.

### OCI Runtime Specification

Definuje runtime bundle a low-level lifecycle:

```text
bundle directory
├── config.json
└── rootfs/

create
→ created
→ start
→ running
→ signal/exit
→ stopped
→ delete
```

Container engine alebo orchestrator spája contracts, ale pridáva vlastné networking, snapshots, metadata, restart, sandbox a scheduling behavior.

## 3. Descriptor ako graph edge

OCI descriptor neobsahuje samotný content. Popisuje edge na content:

```text
mediaType
digest
size
optional platform
optional annotations
optional URLs alebo artifact metadata podľa contextu
```

Consumer vykoná:

```text
read descriptor
→ fetch bytes
→ over size a digest
→ interpretuj podľa mediaType
```

Digest chráni content identity a integrity počas prenosu. Media type hovorí, akú semantic formu bytes majú.

Ak registry vráti bytes s iným digestom alebo size, consumer ich musí odmietnuť. Ak media type nie je podporovaný, content môže byť kryptograficky správny a stále nepoužiteľný.

## 4. Tag, digest a resolution subject

Tag je mutable pointer:

```text
payments:3.13.0
→ dnes IDX313
→ po prepísaní môže ukazovať na IDX314
```

Digest reference je immutable content identity:

```text
payments@sha256:IDX313
```

Bezpečný deployment subject zaznamenáva:

```text
registry/repository identity
tag iba ako human context
resolved index alebo manifest digest
resolution time
client/platform selection
trust-policy verdict
```

Approval nad tagom, ktorý sa pred deployom znova resolve-ne bez immutability controlu, nemusí schváliť skutočne spustený content.

## 5. Image index a platform selection

Image index odkazuje na manifests pre platform variants:

```text
IDX313
├── MAMD313: os=linux, architecture=amd64
└── MARM313: os=linux, architecture=arm64, variant=v8
```

Pull client vyberá variant podľa:

- operating system;
- architecture;
- architecture variant;
- explicitného platform override-u;
- client/runtime implementation.

Platform match nie je úplný application compatibility contract. Manifest `linux/amd64` môže stále vyžadovať:

- novší kernel;
- konkrétny CPU instruction set;
- glibc alebo other runtime assumptions;
- device;
- seccomp/LSM allowance;
- filesystem feature.

## 6. Platform manifest

Platform manifest spája:

```text
one image config descriptor
+ ordered filesystem layer descriptors
```

Manifest digest identifikuje presnú kombináciu configu a layer references. Zmena poradia layers alebo config descriptoru mení manifest digest.

Production record by mal zachovať platform manifest, pretože:

- vulnerability evidence môže byť platform-specific;
- amd64 a arm64 variants môžu obsahovať iné packages;
- runtime reálne unpackuje konkrétny manifest, nie abstraktný tag;
- incident response potrebuje presný content inventory.

## 7. Image configuration

Image config obsahuje runtime defaults a filesystem-chain metadata:

- OS a architecture;
- environment defaults;
- entrypoint a command;
- working directory;
- user;
- labels;
- exposed-port metadata;
- rootfs diff IDs;
- build history.

Config nie je deployment runtime config. Engine ho kombinuje s CLI/orchestrator overrides, mounts, secrets, network a security policy.

```text
image config defaults
+ deployment overrides
+ platform policy
→ generated runtime config.json
```

Preto image `USER 10001` môže byť runtime override-nutý na UID 0. Image metadata nie je jediný effective-state oracle.

## 8. Layers, blob digest a diff ID

Filesystem layer je changeset. Distribution pracuje typicky s compressed blobom:

```text
compressed bytes
→ distribution digest
```

Po decompressii vznikne uncompressed changeset:

```text
uncompressed tar stream
→ diff ID
```

Rovnaký filesystem changeset môže mať odlišné compressed blobs pri inom compression formáte alebo encodingu. Preto:

```text
blob digest ≠ automaticky diff ID
```

Image config `rootfs.diff_ids` viaže ordered uncompressed changesets. Manifest viaže distribuované compressed layer blobs.

## 9. Image ako content-addressed graph

Image nie je jeden opaque tar file:

```text
index descriptor
→ manifest descriptor
→ config descriptor
→ layer descriptors
```

Výhody graph modelu:

- deduplication shared blobs;
- integrity verification;
- platform inventory;
- immutable promotion;
- attachment related artifacts;
- independent caching a transfer.

Failure jednej graph edge je lokalizovateľný:

- missing manifest;
- unsupported media type;
- missing layer blob;
- digest mismatch;
- config/layer chain mismatch;
- wrong platform descriptor.

## 10. Registry publication lifecycle

Atlas publication:

```text
build exact variants
→ calculate descriptors/digests
→ upload missing blobs
→ push platform manifests
→ push image index IDX313
→ attach signature, provenance a SBOM
→ verify registry read-back
→ publish immutable release record
```

Blob existence neznamená, že manifest je publikovaný. Manifest push success neznamená, že related artifacts sú discoverable. Tag update neznamená, že downstream cache prestala používať starý digest.

Post-publication verification má čítať artifact z registry cez rovnaký trust a API path ako consumer.

## 11. Registry authorization boundary

Distribution API authorization sa často líši podľa operation:

- pull blob/manifest;
- push blob;
- push/delete manifest;
- mutate tag;
- mount blob medzi repositories;
- read related artifacts;
- garbage collection/admin operations.

Identity, ktorá smie pullovať production image, nemusí smieť prepísať tag alebo mazať manifest. Repository scope je súčasť artifact identity a access boundary.

Cross-repository copy nesmie predpokladať, že digest alebo referrer graph sa automaticky zachová bez verification.

## 12. Trust artifacts a subject binding

OCI distribution model môže ukladať:

- signatures;
- provenance attestations;
- SBOM;
- vulnerability reports;
- policy bundles;
- non-image artifacts.

Related artifact musí byť viazaný na presný subject digest:

```text
signature/provenance/SBOM
→ subject IDX313 alebo MAMD313
```

Rozhodnutie, či signovať index alebo platform manifest, ovplyvňuje trust semantics. Index signature môže pokrývať platform inventory. Platform signature môže explicitne pokrývať konkrétny variant. Policy musí povedať, čo požaduje.

Digest sám nedokazuje:

- kto content vytvoril;
- z akého source-u;
- že build bol trusted;
- že scan bol complete;
- že artifact je schválený pre production.

## 13. Pull a local content verification

Consumer lifecycle:

```text
resolve immutable subject
→ fetch index/manifest
→ select platform
→ verify trust policy
→ fetch config a layers
→ verify digest/size/media types
→ cache content
→ unpack snapshot/rootfs
```

Cache hit nesmie obísť digest alebo trust semantics. Local bytes musia zodpovedať descriptoru a deployment recordu.

Pull success znamená, že distribution a content verification prešli. Neznamená, že unpack, runtime bundle alebo application start uspejú.

## 14. Unpack a snapshot transition

Engine alebo high-level runtime zmení layers na root filesystem snapshot:

```text
fetch ordered layers
→ decompress
→ verify diff chain podľa implementation
→ apply filesystem changesets/whiteouts
→ create snapshot/rootfs
→ attach writable layer pri runtime
```

Failure môže vzniknúť pri:

- corrupt layer;
- unsupported compression;
- invalid tar/path semantics;
- insufficient disk/inodes;
- snapshotter/kernel incompatibility;
- ownership/xattr/LSM handling;
- platform filesystem assumptions.

Distribution success preto nie je unpack success.

## 15. Runtime bundle generation

OCI runtime bundle obsahuje:

```text
rootfs/
config.json
```

`config.json` opisuje napríklad:

- process arguments a environment;
- cwd a user;
- root filesystem;
- mounts;
- namespaces;
- capabilities;
- resources;
- hostname;
- hooks;
- platform-specific security controls.

Engine syntetizuje bundle z image configu a runtime/deployment policy. Bundle subject má obsahovať image manifest, runtime overrides, mount/network references, security profile a generated config digest.

## 16. Low-level runtime lifecycle

Low-level runtime pracuje s bundle a container ID:

```text
create
→ priprav isolation a process state bez spustenia user processu

start
→ spusti user process

state
→ vráti runtime identity a status

kill
→ doručí signal

delete
→ odstráni stopped runtime state
```

Vyššia vrstva rieši image management, networking, snapshots, restart policy a orchestration. OCI Runtime Specification neštandardizuje celý Docker alebo Kubernetes behavior.

## 17. Runtime hooks

Hooks sú host-side extension body spustené v definovaných lifecycle fázach. Môžu konfigurovať networking, devices alebo policy, ale predstavujú privileged executable supply chain.

Hook contract potrebuje:

```text
executable digest a owner
invocation phase
host/namespace context
input environment
privileges
bounded timeout
failure semantics
audit evidence
```

Nedôveryhodný image alebo runtime input nesmie svojvoľne určovať privileged host hook.

## 18. Deployment evidence

Dôveryhodný deployment record má spájať:

```text
source/build subject
index digest
platform manifest digest
config/layer graph
signature/provenance/SBOM verdict
registry/repository
node platform
runtime bundle/config digest
container/process identity
runtime/application verification
```

Bez platform manifestu incident nevie presne určiť packages. Bez bundle subjectu nevie dokázať effective user, capabilities alebo mounts. Bez runtime oracle nevie, či application skutočne fungovala.

## 19. Worked failure: tag sa zmenil medzi approval a deployom

Security review schválil `payments:3.13.0`, ktorý vtedy ukazoval na `IDX313`. Release pipeline neskôr znova resolve-la tag po jeho prepísaní na `IDX314`.

```text
approval je viazaný na mutable tag
→ tag sa zmení
→ deploy pullne nový index
→ spustený content nemá schválenú evidence
```

Recovery je containment deploymentu, identifikácia reálneho platform manifestu, trust/scan verification a redeploy exact approved digestu. Skorší control je subject-bound approval a immutable tag policy.

## 20. Worked failure: multi-platform tag nemal arm64 variant

Index obsahoval iba `linux/amd64`, ale release metadata tvrdili „multi-platform“.

```text
amd64 test prejde
→ tag/index sa publikuje
→ arm64 node resolve-ne platform
→ no matching manifest
```

Expected platform inventory musí byť vopred definovaný a post-publish overený:

```text
expected: linux/amd64 + linux/arm64/v8
actual: linux/amd64
→ incomplete publication, nie success
```

## 21. Worked failure: registry copy stratila signatures a SBOM

Promotion workflow kopíroval iba index, manifests a layer blobs do production registry. Referrer artifacts neboli prenesené.

```text
runnable image digest existuje v destination
→ trust metadata graph chýba
→ runtime pull uspeje
→ production policy nemá required provenance/SBOM evidence
```

Copy success musí porovnať complete expected artifact graph, nie iba runnable manifests.

## 22. Worked failure: index digest sa zamieňal s platform digestom

Vulnerability scanner skenoval amd64 manifest `MAMD313`, ale deployment record obsahoval iba `IDX313`. Incident query nenašla zraniteľný digest medzi running containers.

```text
scan subject = platform manifest
→ deployment subject = index
→ correlation nemá explicitný edge
→ vulnerable runtime sa javí ako nezasiahnutý
```

Record musí zachovať index-to-selected-manifest relationship.

## 23. Worked failure: registry prijala image, runtime ju nespustil

Manifest a blobs boli validné OCI content, ale config deklaroval `linux/amd64` binary používajúci CPU instruction nepodporovanú node-om.

```text
registry overí storage/content contract
→ pull a digest verification prejde
→ runtime exec binary
→ CPU/kernel platform contract zlyhá
```

OCI distribution compliance negarantuje application/platform compatibility.

## 24. Causal troubleshooting walkthrough: registry image prijme, runtime skončí pred process startom

Atlas push je green. Node pullne image, ale container zostane v create error a user process sa nespustí.

### 1. Zafixuj artifact-to-runtime subject

Zaznamenaj:

- registry a repository;
- tag resolution result;
- index a selected platform manifest digest;
- config/layer descriptors, sizes a media types;
- signature/referrer verdict;
- node OS/architecture/variant a kernel/runtime/snapshotter;
- unpacked snapshot ID;
- generated bundle/config digest;
- low-level runtime error a lifecycle state;
- host storage, xattr, LSM a audit evidence.

### 2. Súťažiace hypotézy

1. Client vybral nesprávny platform manifest.
2. Index neobsahuje required variant.
3. Runtime nepodporuje layer compression alebo media type.
4. Blob je missing/corrupt napriek stale registry metadata.
5. Snapshotter nevie aplikovať layer ownership/xattrs/whiteouts.
6. Node nemá disk/inodes.
7. Generated bundle obsahuje invalid mount alebo namespace config.
8. Seccomp/LSM/hook zlyhá počas create.
9. Config entrypoint alebo working directory path chýba.
10. Binary architecture/libc/kernel feature je incompatible.
11. Related trust artifact chýba a policy blokuje create.
12. Image je validná, ale vyšší engine record/cache je stale.

### 3. Diskriminačné observation points

- inspect index a platform descriptors;
- verify exact blob fetch, size a digest;
- inspect media types a compression;
- unpack/snapshotter events a filesystem evidence;
- node disk/inode/overlay capability;
- generated `config.json` a bundle rootfs;
- runtime hook, seccomp a LSM audit logs;
- exact executable format/interpreter/dependencies;
- trust-policy subject a referrer inventory;
- low-level runtime state vs. engine status.

### 4. Containment

Pozastav rollout a zachovaj exact registry subject, local content store, failed snapshot/bundle metadata a node logs. Neprepínaj na mutable `latest` ani nevypínaj trust/security policy.

### 5. Recovery

- platform inventory gap → rebuild/publish required variant a successor index;
- media/compression mismatch → publish podporovaný format alebo upgrade runtime po testovaní;
- corrupt/missing content → republish z trusted build subjectu a verify read-back;
- snapshotter/storage gap → oprav node/runtime capability alebo presuň workload;
- invalid bundle → oprav engine/deployment runtime config;
- LSM/hook denial → uprav narrow policy/executable contract;
- missing executable/interpreter → oprav image build;
- CPU/kernel incompatibility → publish compatible variant a rozšír platform metadata/policy;
- trust graph gap → prenes/rebuildni subject-bound artifacts pred deployom.

### 6. Over pôvodný outcome

Exact selected manifest musí prejsť pull, digest verification, trust policy, unpack, runtime create/start, application readiness, termination a deployment-record correlation na reprezentatívnej platforme.

### 7. Posuň control skôr

Pridaj expected platform/artifact graph gate, clean-node pull/unpack test, generated-bundle inspection a runtime compatibility matrix pred publication/promotion.

## 25. Čo OCI negarantuje

OCI compliance sama negarantuje:

- application compatibility s host kernelom/CPU;
- rovnaký network alebo storage model;
- rovnaké security defaults;
- rovnakú restart policy;
- rovnaký hook behavior;
- support všetkých optional media types/compressions;
- dôveryhodný source alebo builder;
- complete SBOM/vulnerability evidence;
- application readiness.

Interoperability contract je úmyselne užší než celý platform behavior.

## 26. Referenčné pravidlá

- OCI Image, Distribution a Runtime Specification pokrývajú odlišné transitions.
- Descriptor je content edge definovaný media type, digestom a size.
- Tag je mutable pointer; digest je content identity.
- Index digest a selected platform manifest digest majú odlišný význam.
- Platform match OS/architecture nie je celý compatibility contract.
- Manifest odkazuje na config a ordered distributed layer blobs.
- Blob digest a uncompressed diff ID nie sú automaticky rovnaké.
- Registry publication success nie je complete artifact-graph verification.
- Related signatures/SBOM/provenance musia byť viazané na presný subject.
- Pull success nie je unpack alebo runtime success.
- Image config defaults nie sú effective runtime `config.json`.
- Low-level runtime neimplementuje celý engine/orchestrator lifecycle.
- OCI digest dokazuje content identity, nie autora, bezpečnosť alebo readiness.

## 27. Kontrolné otázky

1. Aké transitions pokrývajú tri hlavné OCI specifications?
2. Čo identifikuje descriptor a ako sa content overí?
3. Ako sa líši tag, index digest a platform manifest digest?
4. Čo obsahuje platform manifest a čo image config?
5. Ako sa líši distribution blob digest a diff ID?
6. Ako sa image graph zmení na runtime bundle?
7. Čo robí low-level runtime a čo pridáva container engine?
8. Prečo registry acceptance negarantuje runtime compatibility?
9. Ako sa related signatures a SBOM viažu na subject?
10. Aké observation points lokalizujú failure medzi distribution, unpack a runtime create boundary?

## Glossary impact

Relevantné pojmy: OCI release subject, artifact-to-process supply chain, OCI descriptor, platform inventory, image index digest, selected platform manifest, image configuration subject, distribution blob digest, diff ID, complete artifact graph, subject-bound referrer, pull verification boundary, unpack/snapshot transition, runtime bundle subject, low-level runtime lifecycle a OCI compatibility boundary.

## Oficiálna dokumentácia

- [Open Container Initiative](https://opencontainers.org/)
- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec)
- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Namespaces, cgroups a capabilities](namespaces-cgroups-capabilities.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Images, layers a copy-on-write →](images-layers-copy-on-write.md)
<!-- KNOWLEDGE-NAVIGATION:END -->