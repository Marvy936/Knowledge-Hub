# BuildKit a Buildx

BuildKit je execution backend, ktorý prekladá build program na dependency graph, vykonáva jeho nodes a exportuje výsledné artifacts. Buildx je Docker CLI vrstva, ktorá vyberá a spravuje BuildKit builder instances, nodes, drivers, platforms, caches a exporters. Ich spoločným výsledkom nemá byť iba „úspešný build“, ale presne identifikovaný, overiteľný a reprodukovateľne vysvetliteľný release artifact.

Dominantný model kapitoly je:

```text
release intent a expected evidence inventory
→ immutable build subject
→ builder trust domain a node/platform selection
→ frontend translation na build graph
→ per-node execution a cache decisions
→ secrets, SSH a entitlement boundaries
→ per-platform artifacts a tests
→ exporter, registry graph a attestations
→ read-back a runtime verification
→ promotion, retention, recovery a builder retirement
```

Tento lifecycle spája builder topology, multi-platform builds, cache, outputs, attestations aj troubleshooting. Samotné `docker buildx build` success nestačí. Musíš vedieť, čo sa buildovalo, kde, s akými inputs, aký graph sa vykonal, ktoré nodes a caches ovplyvnili výsledok, čo bolo exportované a či evidence patrí presne k publikovanému digestu.

## 1. Atlas release subject

Atlas Payments vydáva verziu `3.10.0` pre:

```text
linux/amd64
linux/arm64
```

Release contract vyžaduje:

- source commit `C310`;
- pinned Dockerfile frontend;
- pinned base image subjects;
- dependency locks a package repository snapshot;
- exact BuildKit a Buildx versions;
- native amd64 a arm64 runtime test;
- image index s oboma platform manifests;
- SBOM a provenance viazané na release subject;
- signature a policy verdict;
- read-back z production registry;
- zachovaný rollback digest a build evidence.

Build command je iba jedna mutation v tomto lifecycle-e:

```bash
docker buildx build \
  --builder atlas-release \
  --platform linux/amd64,linux/arm64 \
  --tag registry.example.com/atlas/payments:3.10.0 \
  --tag registry.example.com/atlas/payments:${GIT_SHA} \
  --provenance=true \
  --sbom=true \
  --push .
```

Pred jeho spustením musí existovať **build subject**. Po skončení musí existovať **publication a evidence verdict**.

## 2. Immutable build subject

Build subject identifikuje všetko, čo môže zmeniť graph alebo jeho výsledok:

```text
source repository + commit + submodules
Dockerfile + frontend digest/version
primary a named contexts
expected context inventory a ignore rules
base/external image digests
dependency locks a repository snapshots
build args a non-secret parameters
secret/SSH reference identities
BUILDPLATFORM a TARGETPLATFORM inventory
selected target/stage DAG
builder instance, nodes, driver a BuildKit config
cache import subjects a trust domains
exporter destinations a release purpose
```

Rovnaký Git commit nie je automaticky rovnaký build subject. Zmena frontendu, builder configuration, package repository snapshotu, platform node-u alebo external cache môže zmeniť final digest bez zmeny source tree.

### Príčina → mechanizmus → dôsledok

```text
builder image sa aktualizuje mimo release manifestu
→ zmení sa BuildKit worker, snapshotter alebo compression behavior
→ rovnaký source vytvorí iný graph result alebo provenance
→ release nie je vysvetliteľný iba commitom
```

Preto release evidence musí zaznamenať builder identity, nie iba `git rev-parse HEAD`.

## 3. Buildx request a builder selection

Buildx vytvára request a smeruje ho na selected builder:

```text
CLI context
→ Buildx builder selection
→ driver
→ builder instance
→ eligible node
→ BuildKit worker
```

Výber môže pochádzať z:

- explicitného `--builder`;
- environmentu `BUILDX_BUILDER`;
- aktuálne selected buildera;
- Docker contextu;
- CI wrappera alebo reusable jobu.

Pred release buildom over:

```bash
docker context show
docker buildx ls
docker buildx inspect atlas-release --bootstrap
docker version
docker buildx version
```

Builder identity musí zahŕňať minimálne:

- meno a purpose;
- driver;
- nodes a endpoints;
- BuildKit version/config digest;
- supported platforms;
- worker/snapshotter details;
- cache a registry endpoints;
- tenant/trust classification;
- credentials a entitlement policy.

### Failure boundary: wrong builder

Developer predtým používal local `desktop-linux` builder. CI job neuviedol `--builder` a inherited environment smeroval release request na shared development builder.

```text
release source je správny
→ wrong builder má odlišný frontend cache a credentials
→ build reuse-ne development cache
→ provenance ukazuje iný worker a final digest sa líši
```

Fix nie je iba „spustiť build znova“. Najprv treba zneplatniť release verdict, identifikovať artifacts vytvorené nesprávnym builderom a rebuildnúť ich v správnom trust domain-e.

## 4. Builder trust domain

Builder vykonáva repository-controlled code a môže dostať:

- source a private dependencies;
- build secrets alebo SSH agent;
- registry write credentials;
- shared cache read/write access;
- signing alebo attestation identity;
- host networking alebo insecure entitlements;
- filesystem a compute resources.

Preto oddeľ minimálne:

```text
untrusted fork/PR builders
protected branch builders
release builders
signing/promotion identities
```

Untrusted build nesmie zapisovať do release cache, production repository ani subject-bound evidence namespace-u.

### Failure boundary: cache poisoning

Fork PR mal write access na `registry.example.com/cache/payments:main`. Release builder neskôr importoval ten istý cache subject.

```text
untrusted node publikuje podvrhnutý cached result
→ release graph nájde technicky validný cache key
→ reused result obíde očakávanú trusted execution
→ final image obsahuje bytes, ktoré release pipeline priamo nevytvorila
```

Cache key validity a cache trust sú dve odlišné rozhodnutia. Correctness vyžaduje oboje.

## 5. Frontend a graph translation

Dockerfile frontend prekladá Dockerfile na interný dependency graph, často označovaný ako LLB.

```dockerfile
# syntax=docker/dockerfile:1@sha256:<frontend-digest>
```

Graph obsahuje:

- source/context nodes;
- image source nodes;
- filesystem operations;
- execution nodes;
- mount dependencies;
- stage a target edges;
- platform-specific branches;
- exporter roots.

BuildKit nevykonáva Dockerfile iba ako lineárny shell script:

- nepoužitý stage nemusí byť vykonaný;
- nezávislé nodes môžu bežať paralelne;
- selected target obmedzuje reachable graph;
- cache hit môže execution preskočiť;
- multi-platform request vytvorí platform-specific branches;
- exporter určuje, ktorý result sa stane externým artifactom.

### Failure boundary: test stage existuje, ale nie je v executed graph-e

```dockerfile
FROM build AS unit-test
RUN go test ./...

FROM runtime-base AS runtime
COPY --from=build /out/payments-api /usr/local/bin/payments-api
```

Release target bol `runtime`. `unit-test` nebol ancestor targetu a pipeline ho nebuildovala samostatne.

```text
test stage je v Dockerfile
→ nie je reachable z selected targetu
→ BuildKit ho preskočí
→ build success sa mylne interpretuje ako test pass
```

Expected evidence inventory musí vyžadovať samostatný subject-bound test verdict.

## 6. Node scheduling a platform identity

Builder môže mať viac nodes:

```text
atlas-release
├─ node-amd64
└─ node-arm64
```

Pre každý platform branch zaznamenaj:

- target OS/architecture/variant;
- selected node a native/emulated/cross-compile mode;
- worker a kernel/runtime identity;
- base platform manifest;
- platform-specific cache sources;
- produced manifest digest;
- platform-specific tests a verdicty.

### Emulation

QEMU/binfmt môže spustiť target binaries na inom hoste. Je užitočná pre build operations, ale nie je plnou náhradou native runtime testu.

### Native nodes

Native nodes poskytujú realistickejšie execution a výkon, no môžu mať drift:

- iný kernel;
- inú BuildKit verziu;
- odlišný package mirror;
- rozdielne CPU features;
- inú cache history;
- rozdielne credentials alebo network path.

### Cross-compilation

Cross-compilation oddeľuje build platformu od target platformy:

```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.24 AS build
ARG TARGETOS TARGETARCH
RUN GOOS=$TARGETOS GOARCH=$TARGETARCH \
    go build -trimpath -o /out/payments ./cmd/payments
```

Stále treba overiť runtime dependency closure, native libraries, CGO, certificates, loader a target runtime behavior.

## 7. Cache decision lifecycle

Pre každý graph node BuildKit rozhoduje:

```text
node subject
→ cache key
→ eligible cache sources
→ trust/freshness policy
→ hit alebo miss
→ reused result alebo bounded execution
→ result export/retention
```

Dôležité identity:

- node key;
- platform;
- source cache ref;
- writer trust domain;
- reused result digest;
- creation/freshness generation;
- cache export destination;
- retention a GC lease.

Príklad registry cache:

```bash
docker buildx build \
  --cache-from type=registry,ref=registry.example.com/atlas/cache/payments:main \
  --cache-to type=registry,ref=registry.example.com/atlas/cache/payments:main,mode=max \
  --platform linux/amd64,linux/arm64 \
  --push .
```

### Cache freshness gap

Package install node môže mať validný cache key, hoci remote repository odvtedy vydal security update.

```text
instruction a local inputs sú rovnaké
→ cache key sa nemení
→ remote mutable repository sa nečíta
→ security rebuild reuse-ne starý package result
```

`--no-cache` vynúti execution, ale nevytvorí reproducibility. Potrebuješ controlled dependency refresh, pinned snapshot alebo explicitnú freshness generation.

### Clean build ako control

Clean build má overiť, že build nemá skrytú correctness dependency na cache. Ak po prune zlyhá, prune neporušil correctness; odhalil neúplný input contract.

## 8. Secrets, SSH a entitlements

Build secret mount poskytuje secret iba konkrétnemu execution node-u:

```bash
docker buildx build \
  --secret id=repo_token,src=./repo-token.txt .
```

```dockerfile
RUN --mount=type=secret,id=repo_token \
    token="$(cat /run/secrets/repo_token)" \
    && fetch-private-dependency "$token"
```

Secret mount nezaručuje, že secret nemôže uniknúť. Node ho môže zapísať do:

- generated artifactu;
- package-manager configu;
- cache mountu;
- stdout/stderr;
- test reportu;
- source mapy;
- provenance parameters;
- final image metadata.

SSH forwarding podobne neposiela private key ako file, ale nedôveryhodný build code môže používať agent authority.

Entitlements ako host networking alebo insecure security mode menia sandbox contract. Musia byť:

- explicitné v requeste;
- povolené iba na určenom builderi;
- viazané na exact build subject;
- auditované;
- zakázané pre untrusted source;
- odstránené po migrácii use case-u.

### Failure boundary: secret v generated outpute

Build stage použil secret mount správne, ale frontend tool vytvoril `.env.production` v `/app/dist`. Final stage vykonal narrow `COPY --from=build /app/dist`.

```text
secret mount nie je v layeri priamo
→ build code odvodí secret-bearing output
→ output je považovaný za release artifact
→ final image a cache obsahujú secret
```

Recovery zahŕňa revocation, cache quarantine, clean graph rebuild a audit použitia credentialu.

## 9. Exporter je súčasť correctness

Build result môže skončiť v:

- registry;
- local Docker image store;
- OCI layout/tar;
- local filesystem;
- BuildKit cache;
- viacnásobných outputs.

```bash
# Single-platform local test
docker buildx build --load -t atlas/payments:dev .

# Multi-platform release
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --push \
  -t registry.example.com/atlas/payments:3.10.0 .
```

Úspešný graph execution bez požadovaného exporteru nie je úspešný release.

### Failure boundary: build success, artifact neexistuje

Release job skončil `0`, ale používal `docker-container` driver bez `--push`, `--load` alebo explicitného outputu.

```text
graph result vznikne
→ zostane iba v builder cache
→ pipeline označí release za publikovaný
→ deployment nevie pullnuť očakávaný digest
```

Acceptance musí zahŕňať registry read-back a complete artifact graph verification.

## 10. Multi-platform publication subject

Multi-platform release typicky vytvorí:

```text
image index digest
├─ linux/amd64 manifest digest
│  ├─ config
│  └─ layers
└─ linux/arm64 manifest digest
   ├─ config
   └─ layers
```

Release evidence musí rozlišovať:

- index subject;
- platform manifest subjects;
- per-platform SBOM/provenance podľa modelu;
- runtime tests per platform;
- signature/policy scope;
- registry read-back generation.

Tag je mutable pointer. Index digest je immutable subject, ale platform-specific runtime verdict musí byť viazaný na manifest, ktorý node reálne pullne.

## 11. Attestations a evidence binding

BuildKit/Buildx môže vytvoriť provenance a SBOM:

```bash
docker buildx build \
  --provenance=true \
  --sbom=true \
  --push .
```

Evidence je použiteľná iba keď:

- subject digest je presný;
- expected platform inventory je úplný;
- producer/builder identity je dôveryhodná;
- source a inputs zodpovedajú release contractu;
- evidence prežila promotion/mirroring;
- policy engine ju reálne vyhodnotil;
- missing evidence nie je interpretovaná ako pass;
- runtime/deployment korelácia ukazuje rovnaký digest.

SBOM nepreukazuje, že image je bezpečný. Provenance nepreukazuje, že builder nebol kompromitovaný. Obe sú evidence inputs do širšieho verdictu.

## 12. Build once a promotion

Správny release flow:

```text
build exact source/input subject
→ export immutable index a manifests
→ read-back z registry
→ test exact platform digests
→ vytvoriť a overiť evidence
→ podpísať/policy-approve subject
→ promovovať rovnaký digest
→ deploy a korelovať runtime subject
```

Rebuild v každom environment-e vytvára nový build subject, aj keď source commit zostal rovnaký.

## 13. Builder capacity, retention a GC

Builder má vlastný state lifecycle:

- content store;
- snapshots;
- cache records;
- active build leases;
- temporary exports;
- node disks;
- registry caches;
- logs a traces.

```bash
docker buildx du
docker buildx prune
```

GC policy musí chrániť active builds a potrebné cache subjects, ale build correctness nesmie závisieť od ich večnej existencie.

### Failure boundary: disk full počas exportu

Build nodes dokončili compilation, no builder disk sa zaplnil počas compression/exportu. Časť registry blobs bola uploadnutá, index nebol publikovaný a client connection sa stratila.

Toto je **unknown publication outcome**. Pred retry treba overiť:

- existenciu tagu a digestu;
- reachable manifests/blobs;
- active/incomplete uploads;
- cache result identity;
- attestation subjects;
- či retry prepíše mutable tag alebo vytvorí duplicitné evidence.

Blind retry môže zmiešať graph generations.

## 14. Worked failure: arm64 manifest je green, ale runtime padá

Atlas release `3.10.0` bol publikovaný pre amd64 aj arm64. CI bolo green. Na arm64 node workload skončil `exec format error` a následne pri ďalšom pokuse `no such file or directory`.

### Zafixuj subject

```text
source commit a immutable input inventory
Dockerfile/frontend digest
selected builder a node inventory
BuildKit/Buildx versions
index digest
amd64 a arm64 manifest digest
per-platform config/layers
cache import decisions
build/test mode: native, emulated alebo cross-compiled
runtime node/kernel/architecture
exact command a loader/library evidence
SBOM/provenance/test report subjects
```

### Competing hypotheses

1. arm64 branch použil amd64 binary;
2. index odkazuje na nesprávny platform manifest;
3. cross-compilation nastavila `TARGETARCH`, ale final stage skopíroval iný artifact;
4. CGO alebo native library ostala amd64;
5. cache result bol nesprávne reuse-nutý medzi platforms;
6. shebang/interpreter alebo dynamic loader v final image chýba;
7. emulated test prešiel, native runtime odhalil CPU/kernel edge case;
8. arm64 test report patrí k inému digestu;
9. registry mirror poskytol stale index generation;
10. deployment vybral iný tag digest než release evidence.

### Discriminating observation points

- `docker buildx inspect --bootstrap` a per-node platforms;
- plain progress s platform/node/cache metadata;
- index a platform manifests z registry read-backu;
- binary `file`, `readelf`, loader a shared-library inspection;
- final image config a runtime dependency closure;
- per-platform SBOM a provenance subject;
- test report artifact/manifest binding;
- native arm64 pull a runtime smoke test;
- deployed digest a mirror generation.

### Containment

Zastav promotion a arm64 rollout. Quarantine-ni affected index/tag bez odstránenia evidence. Zachovaj builder logs, cache refs, manifests a failed runtime instance. Ak amd64 subject je nezávisle validný, môže zostať nasadený iba podľa explicitnej platform policy.

### Recovery

- wrong binary/transfer → oprav stage artifact identity a rebuildni oba platform branches;
- cache cross-contamination → oddel platform keys/subjects a clean rebuild;
- missing loader/library → oprav runtime dependency closure;
- stale mirror/index → obnov replication generation a pinni digest;
- evidence mismatch → zruš verdict a vytvor nové subject-bound testy;
- emulation gap → pridaj native arm64 runtime gate.

Publikuj nový index digest; neopravuj existujúci immutable subject v runtime.

### Over pôvodný outcome

Na oboch platformách potvrď:

- pull exact platform manifestu;
- startup a signal contract;
- health a readiness;
- payment business transaction;
- correct SBOM/provenance/test linkage;
- absence starého failed digestu v deployment inventory.

### Posuň control skôr

Pridaj platform manifest inventory, native runtime gates, artifact lineage assertions, cache platform partitioning, registry read-back a deployment digest correlation.

## 15. Referenčný builder katalóg

| Driver/model | Execution boundary | Typické použitie | Hlavná failure boundary |
|---|---|---|---|
| `docker` | Engine-integrated BuildKit | local/simpler builds | obmedzené exporter/cache semantics |
| `docker-container` | samostatný builder container | CI/release builder | output nie je automaticky local |
| `kubernetes` | cluster builder nodes | elastický/native multi-platform pool | tenancy, storage a node drift |
| `remote` | external BuildKit endpoint | central builder service | transport identity a lifecycle ownership |
| managed/cloud | vendor trust domain | shared/native capacity | source/secrets/evidence residency a trust |

Katalóg nevyberá správny builder. Rozhodujú release purpose, trust domain, platform evidence, output contract a recovery model.

## 16. Praktické controls

- explicitne definuj immutable build subject;
- pinuj frontend, bases, dependencies a builder versions/config;
- používaj named release builder a overuj context;
- oddeľ untrusted, protected a release trust domains;
- rozdeľ cache read/write policy podľa trustu a platformy;
- udržuj expected stage a evidence inventory;
- používaj secret/SSH mounts, ale audituj generated outputs;
- povoľuj entitlements iba subject-bound a časovo obmedzene;
- vyžaduj explicitný exporter a registry read-back;
- viaž tests, SBOM, provenance a signature na exact index/manifest subjects;
- vykonávaj native runtime verification pre podporované platforms;
- promovuj rovnaký digest namiesto rebuild-u;
- sleduj queue, node resources, cache, disk, export a registry latency;
- chráň active leases a rollback evidence pri GC;
- udržuj clean-build a builder-recovery postup.

## 17. Kontrolné otázky

1. Ako sa líši Buildx request, builder instance, node a BuildKit worker?
2. Čo tvorí immutable build subject?
3. Prečo technicky validný cache hit nemusí byť dôveryhodný ani fresh?
4. Ako selected target určuje executed stage graph?
5. Prečo emulovaný test nenahrádza native runtime verdict?
6. Čo musí evidence obsahovať pri multi-platform indexe?
7. Prečo build success bez exporteru nie je release success?
8. Ako môže secret mount napriek tomu viesť k secret leakage?
9. Čo treba overiť po unknown publication outcome?
10. Prečo sa má promovovať digest namiesto rebuild-u v každom prostredí?

## Glossary impact

Relevantné pojmy: BuildKit release subject, builder trust domain, builder node subject, graph execution subject, platform branch subject, cache trust and freshness verdict, BuildKit entitlement subject, exporter contract, unknown publication outcome, per-platform evidence inventory, native runtime gate, builder state lifecycle a build publication acceptance.

## Oficiálna dokumentácia

- [BuildKit](https://docs.docker.com/build/buildkit/)
- [Builders](https://docs.docker.com/build/builders/)
- [Build drivers](https://docs.docker.com/build/builders/drivers/)
- [Multi-platform builds](https://docs.docker.com/build/building/multi-platform/)
- [Buildx CLI](https://docs.docker.com/reference/cli/docker/buildx/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Docker Compose](docker-compose.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Praktický Docker projekt od Dockerfile-u po overený Compose runtime →](docker-practical-walkthrough.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
