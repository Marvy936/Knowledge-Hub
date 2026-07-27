# Multi-stage builds

Multi-stage build používa viac `FROM` instructions a vytvára directed acyclic graph stages. Každý stage má vlastný filesystem a metadata state. Final image vznikne iba z vybraného targetu a z artifacts, ktoré doň boli explicitne prenesené.

Dominantný model kapitoly je:

```text
release intent a target/platform inventory
→ immutable stage inputs
→ stage DAG
→ build, test a analysis nodes
→ artifact identity a lineage
→ narrow cross-stage transfer
→ final runtime assembly
→ target/platform publication
→ evidence binding
→ runtime verification, update a recovery
```

Hodnota multi-stage build-u nie je iba menší image. Hlavný prínos je explicitný artifact-lineage contract medzi toolchainom, testami a production runtime artifactom.

## 1. Atlas stage DAG

Atlas Payments používa tento logical graph:

```text
source C42
  ├─ deps
  │    └─ build
  │         ├─ unit-test
  │         ├─ integration-test
  │         ├─ sbom
  │         └─ runtime
  └─ policy-data
```

Release subject musí určiť:

- source commit,
- Dockerfile/frontend,
- base digests per stage,
- stage names a selected target,
- dependency a toolchain inputs,
- expected test/analysis stages,
- artifact digest prenášaný medzi stages,
- target platform,
- final image digest,
- evidence dokazujúcu, že publikovaný artifact pochádza z testovaného graphu.

Dockerfile môže obsahovať test stage, ktorý sa nikdy nevykonal. Samotná existencia stage-u nie je evidence.

## 2. Stage je build-state boundary

Každý `FROM` vytvorí nový stage:

```dockerfile
FROM golang:1.24 AS build
FROM gcr.io/distroless/static-debian12:nonroot AS runtime
```

Stage má vlastné:

- parent image subject,
- filesystem state,
- environment a working directory,
- build args v relevantnom scope,
- executed instructions,
- cache graph,
- artifacts a metadata.

Pomenované stages sú stabilnejšie než numerické indexy:

```dockerfile
COPY --from=build /out/payments-api /usr/local/bin/payments-api
```

Ak sa poradie stages zmení, name-based dependency zostáva čitateľná a explicitná.

## 3. Build a final runtime stage majú odlišnú authority

Build stage môže obsahovať:

- compiler a SDK,
- source code,
- headers,
- package manager,
- test tools,
- temporary credentials a caches,
- debug tooling.

Final runtime stage má obsahovať iba runtime-required content a metadata:

- executable/application files,
- required shared libraries,
- certificates, timezone/NSS data podľa potreby,
- explicitnú non-root identity,
- runtime configuration defaults,
- health helper, ak je opodstatnený.

Táto separácia znižuje:

- artifact size,
- attack surface,
- runtime mutation paths,
- source/toolchain exposure.

Nezaručuje však automaticky, že final artifact neobsahuje secret alebo že runtime dependencies sú úplné. To závisí od cross-stage transfer contractu.

## 4. Narrow artifact transfer

Správny transfer pomenúva konkrétny output:

```dockerfile
COPY --from=build \
  /out/payments-api \
  /usr/local/bin/payments-api
```

Rizikový transfer:

```dockerfile
COPY --from=build / /
```

môže preniesť:

- toolchain,
- source,
- credentials a package config,
- caches,
- test artifacts,
- temporary files,
- build-only permissions a users.

Narrow transfer potrebuje artifact identity. Nestačí, že path existuje. Release má vedieť, ktorý source, toolchain a stage operation vytvorili bytes kopírované do final stage-u.

## 5. Test stage a graph reachability

Príklad:

```dockerfile
FROM build AS unit-test
RUN go test ./...

FROM runtime-base AS runtime
COPY --from=build /out/payments-api /usr/local/bin/payments-api
```

`runtime` závisí od `build`, ale nie od `unit-test`. Pri:

```bash
docker build --target runtime .
```

builder nemusí vykonať `unit-test`, pretože test stage nie je ancestor final targetu.

To nie je bug buildera. Je to property stage DAG-u.

Existujú dva bezpečné modely:

### Explicitný pipeline evidence model

```text
build exact unit-test target
→ uložiť subject-bound test result
→ build exact runtime target z rovnakého source/input subjectu
→ policy overí subject väzbu
```

### Graph-gated artifact model

Final artifact assembly závisí od node-u alebo artifactu, ktorý vznikne až po úspešnom teste. Tento model musí byť navrhnutý tak, aby test marker nebol falošnou náhradou reálneho artifact lineage.

V oboch prípadoch je rozhodujúca väzba medzi tested subjectom a published digestom.

## 6. Target selection je release decision

Konkrétny stage možno buildnúť:

```bash
docker build --target development -t payments:dev .
docker build --target runtime -t payments:release .
```

Targets môžu reprezentovať:

- development image,
- test executor,
- debug environment,
- artifact export,
- production runtime,
- platform-specific branch.

### Failure boundary: debug target publikovaný ako production

Pipeline použije default final stage po refaktoringu, no Dockerfile teraz končí stage-om `debug`. Image obsahuje shell, package manager, source a elevated user.

Build aj push uspejú. Failure je v target identity a publication policy.

Control:

```text
release manifest
→ required target name
→ expected final base/user/content invariants
→ image inspection
→ publication
```

Production pipeline nemá odvodzovať target iba z toho, ktorý stage je posledný v súbore.

## 7. Artifact stage a multiple outputs

Minimalistický artifact stage:

```dockerfile
FROM scratch AS artifact
COPY --from=build /out/ /out/
```

môže byť exportovaný:

```bash
docker buildx build \
  --target artifact \
  --output type=local,dest=./dist \
  .
```

Jeden graph môže produkovať:

- runtime image,
- binaries,
- packages,
- test report,
- SBOM,
- provenance materials.

Každý output má vlastný subject. Binary exportovaný do local directory a binary skopírovaný do final image-u musia byť korelovateľné; rovnaký filename nie je dôkaz rovnakých bytes.

## 8. Secrets neostávajú automaticky v build stage-i

Nesprávny predpoklad:

```text
secret je iba v build stage
→ final image je bezpečný
```

Secret môže prejsť boundary cez:

- broad `COPY --from`,
- generated config,
- compiled bundle alebo source map,
- binary string/resource,
- cache export,
- test/log artifact,
- package manager metadata,
- provenance pri nesprávnom redaction modeli.

Bezpečnejší model:

```text
secret mount
→ bounded command
→ explicit output inventory
→ secret scan outputu
→ narrow COPY
→ final image scan
→ credential revocation pri leakage
```

Multi-stage build zmenšuje transfer surface. Nenahrádza end-to-end secret lifecycle.

## 9. Runtime dependency closure

Minimalistický final stage musí obsahovať všetko, čo process reálne potrebuje.

Pre binary over:

```bash
file ./payments-api
ldd ./payments-api
```

Runtime closure môže zahŕňať:

- dynamic linker,
- shared libraries,
- CA certificates,
- DNS/NSS configuration,
- timezone/locale data,
- user/group metadata,
- writable directories,
- helper binaries,
- architecture-specific files.

### Failure boundary: file existuje, process hlási `no such file or directory`

Executable path existuje, ale ELF interpreter alebo shebang interpreter chýba vo final stage-i. Kernel nevie process načítať a surface error vyzerá ako missing file.

Mechanizmus:

```text
narrow COPY prenesie executable
→ runtime closure je neúplná
→ exec loader nevie nájsť interpreter
→ process nevznikne
```

Recovery je doplniť deklarovanú runtime dependency alebo vytvoriť skutočne static artifact, nie kopírovať celý build filesystem.

## 10. Distroless a `scratch`

Distroless/minimal image môže odstrániť shell a package manager. `scratch` nemá parent userspace content.

Výhody:

- menší content graph,
- menší attack surface,
- menej runtime mutation možností.

Trade-off:

- všetky runtime dependencies musia byť explicitné,
- interactive debugging nie je default,
- observability a forensic tooling musí byť externé,
- certificates, DNS, timezone a user metadata sa ľahko vynechajú.

Operability sa rieši napríklad:

- structured logs/metrics/traces,
- debug variantom viazaným na rovnaký source,
- ephemeral debug toolingom,
- host/platform-level observation,
- reproducible support workflowom.

Production image nemusí obsahovať permanentný shell iba preto, aby bolo možné incident riešiť.

## 11. Shared base stage a dependency divergence

```dockerfile
FROM python:3.13-slim AS base
WORKDIR /app

FROM base AS test
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY . .
RUN pytest

FROM base AS runtime
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
```

Shared base znižuje duplicitu. Test a runtime stage však môžu mať odlišné dependency graphs.

Test pass nemusí dokazovať runtime closure, ak:

- dev dependency poskytla library chýbajúcu v production requirements,
- test stage použil iný system package,
- runtime stage resolveoval inú mutable version,
- test bežal na build platforme a runtime je iná platforma.

Evidence musí zahŕňať final-stage smoke/integration test, nie iba test v bohatšom build environment-e.

## 12. Multi-platform stage DAG

```dockerfile
# syntax=docker/dockerfile:1
FROM --platform=$BUILDPLATFORM golang:1.24 AS build
ARG TARGETOS TARGETARCH
RUN GOOS=$TARGETOS GOARCH=$TARGETARCH \
    go build -o /out/payments-api ./cmd/payments-api

FROM gcr.io/distroless/static-debian12:nonroot AS runtime
COPY --from=build /out/payments-api /usr/local/bin/payments-api
```

Rozlišuj:

- `BUILDPLATFORM` — kde beží build toolchain,
- `TARGETPLATFORM` — platforma final image-u,
- `TARGETOS`, `TARGETARCH`, variant — parameters výsledného artifactu.

Cross-compilation môže vytvoriť správny target binary bez emulácie. Native dependencies, CGO, generated code alebo tests však môžu vyžadovať target-compatible execution.

### Failure boundary: amd64 test evidence, arm64 untested artifact

Pipeline testuje amd64 target a následne publikuje multi-platform index. Arm64 stage použije odlišný compiler path alebo native dependency a zlyhá až na arm64 node.

Policy musí vyžadovať evidence per expected platform manifest, nie iba pre index tag.

## 13. Stage cache a artifact identity

Každý stage node môže mať cache hit alebo execution. Cache reuse je bezpečné iba vtedy, keď:

- key reprezentuje relevantné inputs,
- cache source patrí do správneho trust domainu,
- reused artifact identity je korelovateľná,
- security/freshness workflow nevyžaduje nový input subject.

Rizikový scenár:

```text
test stage execution nad source C42
→ runtime stage reuse starého artifact node-u z C41
→ final image publish
```

Správne navrhnutý dependency graph by zmenu relevantného source-u zahrnul do build node key. Ak artifact prichádza z external location alebo undeclared cache pathu, graph môže túto väzbu stratiť.

## 14. Rebase a stage reuse

BuildKit môže pri vhodnom graph-e reuseovať layers alebo vytvoriť nový manifest bez plnej recompilácie.

Rebase alebo base replacement stále mení release subject a vyžaduje:

- nový base digest,
- final image digest,
- vulnerability a policy evidence,
- runtime compatibility test,
- platform coverage,
- provenance,
- rollback/support decision.

„Application binary sa nezmenil“ neznamená, že runtime artifact je ekvivalentný. Userspace libraries, certificates, package inventory a metadata sa mohli zmeniť.

## 15. Causal walkthrough: Dockerfile má test stage, produkcia obsahuje regresiu

### Symptóm

Release `R42` prejde pipeline a je publikovaný. V produkcii sa objaví regresia, ktorú existujúci unit test spoľahlivo zachytáva. Tím tvrdí, že test sa nachádza priamo v Dockerfile-i.

### Competing hypotheses

1. test stage sa nevykonal;
2. test report patrí inému source commit-u;
3. runtime target bol zostavený z iného build subjectu;
4. publikovaný target je `debug` alebo iný stage;
5. cache vrátila artifact bez relevantnej source dependency;
6. test bežal iba pre inú platformu;
7. final image tag smeruje na starý digest;
8. test bol flaky alebo chybne vyhodnotený.

### Discriminating observation points

Zaznamenaj:

```text
source commit
Dockerfile/frontend
selected test target
selected release target
platform
stage graph
cache outcomes
binary/artifact digest
final image digest
test report subject
published/deployed digest
```

Over pipeline commands:

```bash
docker buildx build --target unit-test ...
docker buildx build --target runtime --push ...
```

Preskúmaj stage dependency graph a provenance. Zisti, či `unit-test` je ancestor `runtime` alebo či pipeline vykonala samostatný subject-bound test krok.

### Finding

Dockerfile obsahoval:

```dockerfile
FROM build AS unit-test
RUN go test ./...

FROM runtime-base AS runtime
COPY --from=build /out/payments-api /usr/local/bin/payments-api
```

Pipeline buildovala iba target `runtime`. Stage `unit-test` nebol reachable z final targetu a nikdy sa nevykonal.

### Containment a recovery

1. zastav rollout a vráť traffic na posledný validný digest;
2. buildni exact test target pre rovnaký source/input/platform subject;
3. oprav regresiu;
4. znovu vytvor test a runtime evidence;
5. viaž test verdict na binary/final digest;
6. over production-like runtime behavior;
7. publikuj nový immutable digest.

### Skoršie controls

- expected stage-evidence inventory,
- explicitný `--target` pre test aj release,
- deny pri missing test report subjecte,
- policy nad selected final targetom,
- provenance dokazujúca stage/artifact lineage,
- per-platform evidence,
- test final runtime image-u, nie iba build stage-u.

## 16. Causal walkthrough: final image obsahuje secret

### Symptóm

Final runtime image je malý a distroless, ale secret scanner nájde registry token v static web bundle-i.

### Hypotheses

- secret bol v build arg/environment,
- secret mount content sa skopíroval,
- frontend build embedol environment do bundle-u,
- broad `COPY --from` preniesol config/cache,
- scanner analyzuje starý digest,
- secret je vo source map-e alebo generated metadata.

### Finding

Build stage používal secret mount, ale frontend command zapísal token do generated `.env.production`, ktorý bol následne zahrnutý v `/app/dist`. Narrow `COPY --from=build /app/dist ...` bol syntakticky správny, no output inventory bol kompromitovaný.

Recovery:

1. revoke token,
2. quarantine affected platform manifests a caches,
3. odstráň secret z generated output pathu,
4. rebuildni clean graph,
5. skenuj stage output aj final image,
6. audituj použitie tokenu.

Multi-stage boundary fungovala presne podľa deklarovaného transferu; problém bol v nesprávne klasifikovanom artifacte.

## 17. Referenčné stage patterns

### Dependencies → build → runtime

```dockerfile
FROM node:22 AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

FROM deps AS build
COPY . .
RUN npm run build

FROM nginx:alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
```

### Build → test → runtime evidence

```dockerfile
FROM build AS unit-test
RUN go test ./...

FROM scratch AS artifact
COPY --from=build /out/payments-api /out/payments-api

FROM runtime-base AS runtime
COPY --from=artifact /out/payments-api /usr/local/bin/payments-api
```

Tento graph stále potrebuje pipeline, ktorá vykoná `unit-test` a overí, že report patrí k rovnakému artifact subjectu. `artifact` stage sám test nevynucuje.

### Development target

```dockerfile
FROM build AS development
RUN install-debug-tools
CMD ["development-server"]
```

Development target má byť oddelený publication policy a nikdy nesmie dostať production reference iba na základe filename/tag konvencie.

## 18. Praktické controls

- pomenúvaj stages podľa capability, nie podľa náhodného poradia;
- explicitne definuj release target;
- udržuj expected stage/evidence inventory;
- viaž test report na source, platform, artifact a final digest;
- používaj narrow `COPY --from` a skenuj prenášané outputy;
- validuj runtime dependency closure v final stage-i;
- testuj final image s production-like UID, filesystemom a platformou;
- oddeľ development/debug publication boundary;
- pinuj external images používané v `FROM` aj `COPY --from`;
- pri rebase vytvor nové security a runtime evidence.

## 19. Kontrolné otázky

1. Prečo je multi-stage Dockerfile DAG a nie iba lineárny zoznam stages?
2. Čo tvorí stage identity?
3. Prečo existence test stage-u nedokazuje, že test prebehol?
4. Ako sa viaže test evidence na publikovaný final digest?
5. Prečo narrow `COPY --from` znižuje, ale neodstraňuje secret risk?
6. Čo tvorí runtime dependency closure?
7. Prečo `scratch` binary môže hlásiť `no such file or directory`?
8. Ako target selection ovplyvňuje production security?
9. Prečo multi-platform index potrebuje evidence per platform manifest?
10. Čo treba znovu overiť pri rebase final image-u?

## Glossary impact

Relevantné pojmy: stage DAG subject, selected build target, expected stage evidence inventory, artifact lineage, cross-stage transfer contract, runtime dependency closure, subject-bound test stage, target publication policy, per-platform stage evidence, final-image runtime test a stage-output secret incident.

## Oficiálna dokumentácia

- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Dockerfile `COPY --from`](https://docs.docker.com/reference/dockerfile/#copy---from)
- [Building best practices](https://docs.docker.com/build/building/best-practices/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Build context a layer cache](build-context-layer-cache.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Volumes a bind mounts →](volumes-bind-mounts.md)
<!-- KNOWLEDGE-NAVIGATION:END -->