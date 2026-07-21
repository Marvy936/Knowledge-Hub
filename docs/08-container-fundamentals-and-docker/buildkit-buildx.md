# BuildKit a Buildx

BuildKit je moderný build backend pre container images a ďalšie build outputs. Buildx je Docker CLI plugin, ktorý spravuje BuildKit builders a sprístupňuje pokročilé capabilities ako multi-platform builds, viac exporterov, external cache, attestations a distribuované builder topológie. `docker build`, Buildx a BuildKit nie sú synonymá: CLI odošle build request vybranému builderu, ktorého backend vykoná build graph.

## 1. Základný model

```text
Dockerfile / frontend
        ↓
      Buildx CLI
        ↓
 selected builder instance
        ↓
      BuildKit daemon
        ↓
 build graph execution
        ↓
 image / registry / local / OCI / cache outputs
```

BuildKit môže:

- vykonávať nezávislé graph nodes paralelne,
- preniesť iba potrebnú časť contextu,
- preskočiť nepoužité stages,
- používať content-aware cache,
- mountovať secrets, SSH agents a caches bez zámerného uloženia do final layer,
- exportovať viac typov outputs,
- vytvárať multi-platform image indexes,
- generovať provenance a SBOM attestations podľa configuration.

## 2. Frontend a build graph

Dockerfile frontend preloží Dockerfile do interného build graphu, často označovaného ako LLB model.

```dockerfile
# syntax=docker/dockerfile:1
```

Frontend určuje syntax a semantics dostupných instructions. BuildKit potom vykonáva graph podľa dependencies, nie iba ako jednoduchý lineárny shell script.

Dôsledky:

- nepoužitý stage nemusí byť vykonaný,
- nezávislé stages môžu bežať paralelne,
- cache key vychádza z operation a relevantných inputs,
- secret mount nemusí byť súčasťou filesystem outputu.

## 3. Buildx

Základné príkazy:

```bash
docker buildx version
docker buildx ls
docker buildx inspect
docker buildx build .
```

Buildx spravuje:

- builder instances,
- builder nodes,
- drivers,
- target platforms,
- BuildKit configuration,
- output a cache backends.

Aktívny builder môže byť odlišný od default buildera používaného bežným Docker workflowom.

## 4. Builder instance

Builder je logical Buildx object s jedným alebo viacerými nodes.

```bash
docker buildx create --name release-builder --use
docker buildx inspect --bootstrap
```

Builder metadata zahŕňa:

- driver,
- endpoint alebo nodes,
- BuildKit status a version,
- podporované platforms,
- configuration a driver options.

Pred release buildom zaznamenaj:

```bash
docker buildx inspect --bootstrap
docker version
docker buildx version
```

## 5. Build drivers

Driver určuje, kde a ako BuildKit backend beží.

### `docker`

Používa BuildKit integrovaný do Docker Engine-u.

Výhody:

- jednoduchý default,
- output je typicky ľahko dostupný v local image store,
- bez samostatného builder containeru.

Obmedzenia:

- menšia konfigurovateľnosť BuildKit daemon-u,
- nie všetky cache/export capabilities sú dostupné rovnako ako pri samostatných drivers.

### `docker-container`

BuildKit beží v samostatnom Docker containeri.

Výhody:

- izolovanejšia builder instance,
- explicitná BuildKit verzia/configuration,
- širšie cache/export možnosti,
- multi-node builder topology.

Výsledok sa bez `--load` nemusí automaticky objaviť v local Docker image store.

### `kubernetes`

BuildKit nodes bežia v Kubernetes workloadoch.

Použitie:

- elastickejší CI build pool,
- native multi-architecture nodes,
- persistent cache podľa storage modelu,
- resource requests/limits a scheduling.

Potrebuje cluster security, tenancy, network a cache isolation model.

### `remote`

Buildx sa pripája na existujúci remote BuildKit daemon.

Potrebuje:

- silnú transport authentication,
- tenant isolation,
- version compatibility,
- external lifecycle ownership,
- audit a capacity controls.

### Cloud/managed builder

Managed service môže poskytovať shared cache a native platform nodes. Posudzuj data residency, source/secrets exposure, provenance, pricing a vendor trust.

## 6. Builder node

Jeden builder môže mať viac nodes:

```text
release-builder
├─ node-amd64
└─ node-arm64
```

Nodes môžu poskytovať native execution pre rôzne architectures. Scheduler vyberá node podľa target platform a capability.

Viac nodes vyžaduje:

- konzistentné frontend/BuildKit versions,
- zdieľaný alebo prenosný cache model,
- rovnaký registry a secret access contract,
- observability per node,
- capacity a failure handling.

## 7. Output model

Build nemusí skončiť iba local image-om.

### Registry output

```bash
docker buildx build \
  --tag registry.example.com/example/app:${GIT_SHA} \
  --push .
```

### Local Docker image store

```bash
docker buildx build --load -t example:dev .
```

`--load` je vhodné najmä pre single-platform local testing. Multi-platform image index sa typicky publikuje do registry alebo compatible image store-u.

### Local filesystem output

```bash
docker buildx build \
  --target artifact \
  --output type=local,dest=./dist .
```

### OCI alebo tar output

Použiteľné pre air-gapped transfer, artifact inspection alebo ďalší supply-chain workflow.

Output musí mať explicitnú identity a retention. Úspešný build bez požadovaného exporteru môže skončiť iba v builder cache.

## 8. Multi-platform build

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag registry.example.com/example/app:${GIT_SHA} \
  --push .
```

Výsledkom je typicky image index odkazujúci na platform-specific manifests.

Tri hlavné stratégie:

1. emulation,
2. viac native builder nodes,
3. cross-compilation.

## 9. Emulation

QEMU user-mode emulation môže spustiť target-architecture binaries na inom build hoste.

Výhody:

- jednoduchšie použitie existujúceho Dockerfile-u,
- bez vlastného native node-u pre každú platformu.

Nevýhody:

- nižší výkon pri compilation/compression,
- odlišné edge-case behavior,
- potreba správne zaregistrovaných binfmt handlers,
- test pod emuláciou nie je plná náhrada native runtime testu.

## 10. Native nodes

Native build na `amd64` a `arm64` nodes poskytuje realistickejší execution a lepší výkon.

Riziká:

- drift toolchainu medzi nodes,
- odlišné kernel/platform capabilities,
- cache fragmentation,
- node availability,
- credential distribution.

Builder bootstrap má overiť podporované platforms a health všetkých nodes.

## 11. Cross-compilation

Dockerfile môže používať automatic platform arguments:

```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.24 AS build
ARG TARGETOS TARGETARCH
RUN GOOS=$TARGETOS GOARCH=$TARGETARCH \
    go build -o /out/example ./cmd/example

FROM alpine:3.21
COPY --from=build /out/example /usr/local/bin/example
```

Cross-compilation funguje dobre pri toolchainoch, ktoré ju podporujú. Stále potrebuješ:

- target runtime dependencies,
- architecture-specific tests,
- správny CGO/native-library model,
- výsledný platform manifest.

## 12. Cache exporters a importers

Príklad registry cache:

```bash
docker buildx build \
  --cache-from type=registry,ref=registry.example.com/example/cache:main \
  --cache-to type=registry,ref=registry.example.com/example/cache:main,mode=max \
  --tag registry.example.com/example/app:${GIT_SHA} \
  --push .
```

Možné cache backends závisia od drivera a BuildKit configuration.

Cache potrebuje:

- oddelenie trust domains,
- scoped read/write credentials,
- immutable alebo kontrolované refs,
- retention a garbage collection,
- capacity monitoring,
- fallback na clean build.

## 13. Inline vs. registry cache

### Inline cache

Cache metadata sa pridá k image outputu podľa podporovaného režimu. Je jednoduchšia, ale nemusí zachovať maximálny interný graph.

### Samostatná registry cache

Cache je samostatný artifact/ref a môže používať širší `mode=max` graph.

Production image a cache artifact majú odlišnú retention a trust policy.

## 14. Secrets

CLI secret:

```bash
docker buildx build \
  --secret id=repo_token,src=./repo-token.txt .
```

Dockerfile:

```dockerfile
RUN --mount=type=secret,id=repo_token \
    TOKEN="$(cat /run/secrets/repo_token)" \
    && fetch-dependency "$TOKEN"
```

Environment source možno použiť podľa Buildx secret syntax a podporovanej verzie.

Secret nesmie skončiť v:

- copied output directory,
- package-manager config,
- build logs,
- test reports,
- cache mount,
- provenance parameters,
- final image metadata.

## 15. SSH forwarding

```bash
docker buildx build --ssh default .
```

```dockerfile
RUN --mount=type=ssh git clone git@github.com:example/private.git
```

Build používa forwarded agent/socket bez kopírovania private key do image. Over host-key verification a nedovoľ nedôveryhodnému Dockerfile-u používať privilegovaný SSH agent.

## 16. Attestations

BuildKit/Buildx môže vytvárať attestations ako:

- build provenance,
- SBOM.

Príklad:

```bash
docker buildx build \
  --provenance=true \
  --sbom=true \
  --tag registry.example.com/example/app:${GIT_SHA} \
  --push .
```

Attestation musí byť:

- viazaná na správny subject digest,
- zachovaná pri promotion/mirroringu,
- podpísaná alebo overiteľná podľa supply-chain modelu,
- kontrolovaná policy engine-om,
- zbavená citlivých build arguments.

SBOM ani provenance samy osebe nepreukazujú bezpečnosť.

## 17. Reproducibility

BuildKit zlepšuje deterministický graph a cache, ale výsledok stále ovplyvňujú:

- mutable base tags,
- package repositories,
- network downloads,
- timestamps,
- platform/toolchain,
- frontend a BuildKit version,
- build args,
- generated metadata.

Release workflow potrebuje immutable inputs, provenance a občasný independent rebuild.

## 18. Entitlements

Niektoré build operations vyžadujú širšie capabilities, napríklad host networking alebo insecure security mode podľa BuildKit configuration.

Tieto entitlements:

- rozširujú build sandbox,
- musia byť povolené daemonom aj requestom,
- nesmú byť defaultom pre nedôveryhodné builds,
- potrebujú audit a izolovaný builder pool.

Build je execution of repository-controlled code. Builder je security-sensitive workload.

## 19. Rootless BuildKit

Rootless BuildKit znižuje host root exposure využitím user namespaces a rootless runtime mechanizmov.

Limity môžu zahŕňať:

- snapshotter/filesystem požiadavky,
- networking,
- cgroups,
- performance,
- privileged build features.

Rootless nie je náhradou tenant isolation pri vykonávaní nedôveryhodného code-u.

## 20. BuildKit configuration

Samostatný builder môže používať BuildKit daemon configuration pre:

- registry mirrors a certificates,
- garbage collection,
- worker backends,
- network mode,
- debug/logging,
- parallelism,
- insecure entitlements,
- cache retention.

Configuration je súčasťou build provenance a platform ownershipu. Zmena builder configu môže zmeniť výsledok alebo performance bez zmeny repository.

## 21. Garbage collection

Builder cache spotrebúva významný disk.

```bash
docker buildx du
docker buildx prune
```

GC policy má rozlišovať:

- recent active cache,
- large unused records,
- shared release cache,
- per-project/tenant quotas,
- disk emergency threshold.

Manuálny agresívny prune môže zvýšiť build times, ale nesmie porušiť correctness. Ak poruší, build mal skrytú cache dependency.

## 22. Build observability

```bash
docker buildx build --progress=plain .
docker buildx inspect --bootstrap
docker buildx du
```

Sleduj:

- queue time,
- duration per graph node,
- context transfer,
- cache hits/misses,
- remote fetch latency,
- CPU/memory/disk per builder node,
- cache import/export duration,
- output push time,
- failures podľa platformy,
- BuildKit daemon logs.

## 23. CI trust boundaries

Oddeľ minimálne:

- untrusted pull-request builders,
- protected branch builders,
- release/signing builders,
- production registry credentials.

Untrusted build nemá mať write access k release cache refu, signing identity ani production registry namespace.

Preferuj ephemeral builder workers alebo čistiteľný workspace pri nedôveryhodnom source.

## 24. Build once a promotion

Release pipeline má:

1. buildnúť konkrétny commit,
2. otestovať výsledný digest/platform manifests,
3. vytvoriť provenance/SBOM,
4. podpísať alebo policy-overiť artifact,
5. promovovať ten istý digest,
6. nerekonštruovať image osobitne v každom environment-e.

Rebuild v production mení toolchain, network a cache context a porušuje artifact promotion model.

## 25. Anti-patterny

### `--load` pri multi-platform release a očakávanie plného indexu

Local image store nemusí reprezentovať registry multi-platform output podľa očakávania.

### Jeden shared builder pre fork PR aj release signing

Spája nedôveryhodný code, cache a credentials.

### Cache bez namespace/trust isolation

Umožňuje poisoning alebo data leakage.

### Mutable builder image/config bez auditu

Výsledok sa mení bez repository change.

### Emulovaný build považovaný za native runtime test

Emulation nemusí zachytiť všetky platform-specific chyby.

### Secrets cez build args

Môžu uniknúť do metadata, history alebo provenance.

### Build úspešný, ale bez exporteru

Výsledok zostal iba v cache a nie je release artifactom.

### `prune -a` ako rutinná oprava

Maskuje capacity a retention problém.

## 26. Troubleshooting

### Buildx používa iný builder

Over:

```bash
docker buildx ls
docker buildx inspect
echo "$BUILDX_BUILDER"
```

### Image po build-e nie je v `docker images`

Použitý driver/output ho neimportoval do local image store-u. Použi `--load` pre vhodný single-platform local build alebo `--push`/explicitný exporter.

### Multi-platform build zlyhá s `exec format error`

Over emulation registration, target platform, `FROM --platform`, cross-compilation a native dependency.

### Cache sa neimportuje

Over driver support, registry auth, cache ref, media type, platform a retention/GC.

### Builder je veľmi pomalý

Rozlíš context transfer, emulation, cache miss, network download, CPU/memory limit, disk I/O a registry push.

### BuildKit disk je plný

Použi `buildx du`, skontroluj GC policy, active builds a cache ownership. Pred prune zachovaj diagnostické dáta.

### Provenance obsahuje neočakávané hodnoty

Over build args, frontend, source metadata a attestation mode; secrets nesmú byť v arguments alebo labels.

## 27. Kontrolné otázky

1. Aký je rozdiel medzi BuildKit a Buildx?
2. Čo je builder instance a builder node?
3. Ako sa líšia `docker` a `docker-container` drivers?
4. Aký je rozdiel medzi `--load` a `--push`?
5. Ktoré tri stratégie existujú pre multi-platform build?
6. Prečo emulation nenahrádza native runtime test?
7. Ako sa odlišuje production image a build cache artifact?
8. Aké riziká majú build secrets a SSH forwarding?
9. Čo poskytuje provenance a SBOM?
10. Prečo treba oddeliť untrusted a release builders?

## Glossary impact

Relevantné pojmy: BuildKit, Buildx, build frontend, LLB, builder instance, builder node, build driver, Docker driver, Docker container driver, Kubernetes builder driver, remote builder, build exporter, `--load`, `--push`, multi-platform build, emulation, native builder, cross-compilation, cache exporter, build attestation a builder trust domain.

## Oficiálna dokumentácia

- [BuildKit](https://docs.docker.com/build/buildkit/)
- [Builders](https://docs.docker.com/build/builders/)
- [Build drivers](https://docs.docker.com/build/builders/drivers/)
- [Multi-platform builds](https://docs.docker.com/build/building/multi-platform/)
- [Buildx CLI](https://docs.docker.com/reference/cli/docker/buildx/)
