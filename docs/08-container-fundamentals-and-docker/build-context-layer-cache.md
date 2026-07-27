# Build context a layer cache

Docker build nevykonáva Dockerfile nad celým host filesystemom. Builder dostane explicitný context alebo viac named contexts, vytvorí input inventory, odvodí build graph a pre každý node rozhodne, či použije dôveryhodný cached result alebo vykoná novú operáciu.

Dominantný model kapitoly je:

```text
immutable build subject
→ context sources a exclusion rules
→ normalized input inventory
→ stage/node dependency graph
→ cache-key derivation
→ trusted cache lookup
→ cache hit alebo bounded execution
→ result a cache export
→ final artifact/provenance verification
→ retention, clean-room rebuild a GC
```

Cache je optimalizácia výsledkov už definovaného build contractu. Nesmie byť skrytým zdrojom correctness, identity ani bezpečnostných aktualizácií.

## 1. Atlas build subject

Atlas Payments release `R42` používa:

```text
source commit: C42
Dockerfile: docker/payments.Dockerfile
primary context: repository root at C42
named context docs: documentation commit D17
base image digest: B9
platform: linux/amd64
release target: runtime
builder: buildkit cluster BK7
external cache: registry cache subject RC-main-884
```

Build subject musí identifikovať nielen source commit, ale aj:

- context root a context type,
- effective `.dockerignore` rules,
- named/Git/image contexts,
- Dockerfile a frontend,
- base/external image digests,
- build args a target platform,
- cache import subjects a trust domain,
- remote dependency snapshots alebo lock contract,
- selected stage/target.

Ak niektorý významný input chýba z identity alebo cache dependency modelu, build môže byť rýchly a zároveň nesprávny.

## 2. Context je security a correctness boundary

Príkaz:

```bash
docker build -f docker/payments.Dockerfile .
```

znamená:

```text
Dockerfile path = docker/payments.Dockerfile
context root = current directory
```

`COPY` source paths sa vyhodnocujú voči context rootu, nie voči directory Dockerfile-u.

Builder štandardne nemá čítať ľubovoľný host path mimo povolených contexts. To vytvára dôležitú boundary:

```text
host filesystem
→ selected context inventory
→ builder-visible files
→ files skutočne použité build graphom
→ content vo výslednom artifacte
```

Tieto množiny nie sú totožné. Secret môže byť odoslaný builderu, aj keď ho žiadny `COPY` neprenesie do final image-u. Tým sa stále rozšíri builder trust a incident scope.

## 3. `.dockerignore` ako input-filter contract

Príklad:

```text
.git
.env
*.pem
node_modules
coverage
build
*.log
```

`.dockerignore` znižuje:

- context transfer a hashing,
- cache invalidation surface,
- accidental copy risk,
- builder-visible secret surface,
- nepresnú provenance.

Nie je to secret manager ani náhrada source hygiene. File môže zostať:

- v Git history,
- v inom named contexte,
- v CI artifacte,
- v build cache,
- na builder workeri.

### Failure boundary: ignore rule odstráni required migration

Rule:

```text
migrations/
```

bola pridaná kvôli lokálnym test artifacts, ale zároveň odstránila production SQL migrations z contextu. `COPY . .` prešla, build aj smoke test boli green, no final image nedokázal vykonať database upgrade.

Mechanizmus:

```text
broad ignore rule
→ required file nie je v input inventory
→ COPY ho nemôže preniesť
→ final artifact je neúplný
→ failure sa prejaví až pri runtime workflowe
```

Kontrola musí validovať expected context inventory, nie iba úspech build-u.

## 4. Context typy a immutable identity

Context môže byť napríklad:

- local directory,
- local tar archive,
- Git repository/ref,
- remote tarball,
- stdin,
- named context,
- image context.

Git branch `main` nie je immutable build input. Reprodukovateľnejší Git context potrebuje:

- exact commit SHA,
- submodule identity,
- source authentication bez leakage,
- expected repository/ref verification,
- commit metadata v provenance.

Named contexts umožňujú zmenšiť primary context a explicitne pomenovať dependencies:

```bash
docker buildx build \
  --build-context docs=./documentation \
  --build-context policy=docker-image://registry.atlas.example/policy@sha256:abc... \
  .
```

Dockerfile ich môže používať podobne ako stage:

```dockerfile
COPY --from=docs / /usr/share/doc/payments
```

Každý named context musí mať vlastnú immutable identity a trust policy.

## 5. Cache node nie je iba „starý layer“

Moderný BuildKit modeluje build ako graph operations. Cache key môže závisieť od:

- instruction a frontend semantics,
- parent node/result identity,
- copied file contentu a metadata,
- mount configuration,
- build args,
- base image a platformy,
- source/named context identity,
- relevantných execution options.

Ak sa key zhoduje a cache source je dôveryhodný, builder môže použiť predchádzajúci result bez opakovania execution.

To vedie k trom odlišným otázkam:

1. **Je cache hit technicky validný podľa key?**
2. **Je cache source dôveryhodný pre tento build?**
3. **Je cache key úplným modelom všetkých correctness a freshness inputs?**

Technicky validný hit môže byť bezpečnostne alebo produktovo zastaraný, ak build step číta mutable remote state, ktoré nie je reprezentované immutable inputom.

## 6. Poradie instructions ako dependency model

Neefektívne:

```dockerfile
COPY . .
RUN npm ci
```

Každá source zmena mení broad `COPY` result a invaliduje dependency install.

Lepšie:

```dockerfile
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

Graph teraz vyjadruje:

```text
dependency manifests
→ dependency install
→ application source
→ build/test
```

Všeobecné pravidlo:

```text
stabilnejšie a drahé declared inputs skôr
→ často meniace sa inputs neskôr
```

Optimalizácia nesmie vynechať skrytý input. Ak dependency install reálne používa ďalší config, certificate alebo workspace file, musí byť zahrnutý do node dependency subjectu.

## 7. Mutable remote inputs a stale `RUN` result

Instruction:

```dockerfile
RUN apt-get update && apt-get install -y libexample
```

obsahuje text commandu, ale remote repository state sa môže meniť bez zmeny Dockerfile-u. Pri cache hit-e sa command nevykoná a remote update sa vôbec nepozoruje.

Pri cache miss-e sa command vykoná, ale výsledok môže byť odlišný v rôznych časoch, ak package version alebo repository snapshot nie sú kontrolované.

Preto treba rozlišovať:

- **reproducibility** — rovnaký immutable input subject dá rovnaký výsledok;
- **freshness/update** — workflow zámerne vytvorí nový input subject;
- **cache reuse** — optimalizácia už zvoleného subjectu.

`--no-cache` iba núti execution graphu. Nepinuje remote packages, neoveruje ich trust a negarantuje rovnaký výsledok.

## 8. Cache mounts: performance state, nie build truth

```dockerfile
RUN --mount=type=cache,target=/root/.cache/go-build \
    go build ./...
```

Cache mount poskytuje pomocný mutable storage pre command, zatiaľ čo instruction result vzniká znovu.

Musí platiť:

```text
empty cache
→ build je pomalší
→ výsledný correctness contract zostáva rovnaký
```

Ak build bez cache nevie obnoviť required artifact alebo dependency, cache sa stala nezdokumentovaným source-of-truth.

Concurrency behavior je tiež contract:

```dockerfile
RUN --mount=type=cache,target=/var/lib/apt,sharing=locked \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update && apt-get install -y gcc
```

Nesprávne shared state môže viesť ku corruption alebo nondeterministic resultom.

## 9. Secret, SSH a bind mounts

### Secret mount

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci
```

### SSH mount

```dockerfile
RUN --mount=type=ssh \
    git clone git@github.com:atlas/private-module.git
```

### Bind mount

```dockerfile
RUN --mount=type=bind,source=.,target=/src,ro \
    make -C /src
```

Tieto mounts oddeľujú execution-time access od automatického uloženia mount contentu do layeru. Nezaručujú však, že command:

- nevypíše secret,
- nevytvorí credential file v layer filesysteme,
- nezapíše citlivé dáta do cache,
- nevloží secret do binary alebo bundle,
- správne deklaruje všetky relevantné inputs.

Výsledný artifact a cache/export treba analyzovať nezávisle od mount type-u.

## 10. External cache ako samostatný supply-chain artifact

CI často importuje cache z registry:

```bash
docker buildx build \
  --cache-from type=registry,ref=registry.atlas.example/cache/payments:main \
  --cache-to type=registry,ref=registry.atlas.example/cache/payments:main,mode=max \
  --push \
  -t registry.atlas.example/payments/api:${GIT_SHA} \
  .
```

Cache subject potrebuje:

- namespace a ownera,
- writer/read identities,
- source branch/trust domain,
- platform a builder compatibility,
- retention a GC policy,
- provenance alebo audit podľa rizika,
- poisoning response.

Production image a external cache sú odlišné artifacts. Cache nesmie dostať production dôveru iba preto, že je uložená v rovnakej registry.

## 11. Cache poisoning a trust-domain separation

Rizikový model:

```text
untrusted fork build
→ write do shared cache refu
→ protected release importuje cache
→ reuse podvrhnutého resultu
→ trusted image publication
```

Riziko rastie pri:

- mutable shared cache references,
- broad registry write permission,
- spoločnom namespace pre forks a protected branches,
- absent provenance/audit,
- cache používanom ako jediný source required artifactu.

Controls:

- oddeľ writable cache trust domains,
- untrusted cache nepoužívaj ako authoritative input protected release-u,
- používaj read-only alebo isolated fork cache,
- viaž cache subject na repository, branch/trust class, platform a builder,
- zachovaj clean rebuild capability,
- over final artifact nezávislými tests/policy.

## 12. Multi-platform cache

Cache pre `linux/amd64` nemusí byť validná pre `linux/arm64`.

Platform-relevantné inputs zahŕňajú:

- `BUILDPLATFORM`,
- `TARGETPLATFORM`,
- `TARGETOS`, `TARGETARCH`,
- native toolchain a system libraries,
- emulation/native builder mode,
- architecture-specific generated artifacts.

Ak cache subject neoddeľuje platformy správne, môže final image obsahovať nesprávny executable a zlyhať `exec format error` až pri runtime.

## 13. Causal walkthrough: security rebuild stále obsahuje zraniteľnú knižnicu

### Symptóm

Vulnerability team očakáva, že rebuild `R42-security1` načíta opravenú `libexample`. Pipeline prebehne rýchlo a green, ale SBOM final image-u stále obsahuje vulnerable version.

### Competing hypotheses

1. base image digest stále obsahuje starú knižnicu;
2. package install node bol cache hit;
3. package repository ešte neposkytuje fix;
4. Dockerfile pinuje vulnerable version;
5. external cache bol podvrhnutý alebo nesprávne namespaced;
6. scanner analyzuje starý digest;
7. release tag smeruje na starý image;
8. fix existuje iba pre inú platform variantu.

### Discriminating observation points

Zachovaj exact subjects:

```text
source commit
Dockerfile/frontend
base digest
platform
cache-from refs
final digest
scanner/SBOM subject
```

Spusť plain progress:

```bash
docker buildx build --progress=plain ...
```

Porovnaj:

- ktorý node bol `CACHED`,
- base a final manifest digest,
- cache source/ref a platform,
- effective package pin/lock,
- repository snapshot alebo package metadata,
- SBOM package origin,
- deployment/tag correlation.

### Finding

`RUN apt-get update && apt-get install libexample` bol obnovený z external cache, preto sa remote repository vôbec nečítalo. Workflow vytvoril nový release label, ale nevytvoril nový immutable dependency subject ani zámernú invalidáciu security-sensitive node-u.

### Containment a recovery

1. zablokuj publication/deployment vulnerable digestu;
2. potvrď dostupnosť a identity opravenej package version;
3. vytvor nový controlled dependency/base input subject;
4. invaliduj iba relevantný stage/node alebo vykonaj trusted clean build;
5. nepouži cache z nedôveryhodného subjectu;
6. vygeneruj nový SBOM/scan pre každý platform manifest;
7. over runtime smoke a exact deployed digest.

### Skoršie controls

- explicitný base/dependency update workflow,
- immutable repository snapshot alebo lock podľa ecosystemu,
- security rebuild epoch viazaný na reviewed input change,
- subject-bound cache inventory,
- expected SBOM delta assertion,
- clean-room rebuild sampling,
- deny, ak scanner analyzuje iný digest než release.

## 14. Causal walkthrough: rovnaký commit, rozdielny image

### Symptóm

Dva builders vytvoria z commitu `C42` odlišné final digests.

### Hypotheses

- odlišný base tag resolution,
- iný Git submodule alebo named context,
- mutable package repository,
- odlišná target platforma,
- generated timestamp alebo locale,
- odlišný frontend/toolchain,
- iný `.dockerignore`/context root,
- cache result z iného trust domainu.

### Dôkazný postup

Porovnaj build subjects, nie iba Dockerfile text:

```text
source/context inventory
frontend
base digests
args/platform
named contexts
external dependency snapshots
cache import subjects
builder/toolchain
final manifests/config/layers
```

Recovery je odstránenie neidentifikovaného alebo mutable inputu. Nútenie rovnakého digestu bez pochopenia príčiny by iba skrylo provenance gap.

## 15. Build observability

Sleduj:

- context size a file count,
- excluded/expected input inventory,
- context transfer a hashing time,
- duration a cache outcome per node,
- cache source a export result,
- external download time,
- builder CPU, memory, disk a inode pressure,
- output/image size,
- changed manifests/layers medzi releases,
- clean-room digest comparison,
- cache retention a GC events.

BuildKit progress je execution trace, nie úplná provenance. Potrebuje doplniť immutable input a artifact subjects.

## 16. Referenčný cache katalóg

| Mechanizmus | Čo reuseuje alebo sprístupňuje | Nesmie sa stať |
|---|---|---|
| Instruction/layer cache | celý predchádzajúci graph-node result | skrytý freshness policy |
| Cache mount | mutable pomocné dáta pre nový execution | jediný source required artifactu |
| Bind mount | context/source počas instruction | implicitný undeclared output path |
| Secret mount | krátkodobý secret počas instruction | secret v layer/log/cache |
| SSH mount | forwarded SSH agent/socket | neauditovaný mutable source |
| Registry cache export | zdieľané build graph results | cross-trust poisoning path |
| Inline cache | cache metadata spojená s image | production attestation replacement |
| Clean-room build | nový build bez reuse relevantnej cache | jednorazový rituál bez input porovnania |

## 17. Praktické controls

- definuj minimálny, ale úplný context inventory;
- testuj `.dockerignore` proti expected files;
- pinuj Git/named/image context subjects;
- kopíruj dependency manifests pred application source iba ak sú všetky inputs explicitné;
- build musí byť correct s prázdnou cache;
- oddeľ cache trust domains a write permissions;
- zaznamenávaj cache import/export subjects v provenance;
- nevydávaj cache hit za security update;
- porovnávaj SBOM a digests pri controlled rebuildoch;
- chráň cache, builder a registry cleanup vlastnými retention rules.

## 18. Kontrolné otázky

1. Aký je rozdiel medzi host filesystemom, contextom a files použitými build graphom?
2. Prečo `.dockerignore` nie je secret manager?
3. Čo musí obsahovať context subject?
4. Prečo technicky validný cache hit nemusí byť freshness-correct?
5. Aký je rozdiel medzi instruction cache a cache mountom?
6. Prečo build musí fungovať s prázdnou cache?
7. Ako vzniká cache poisoning medzi fork a release buildom?
8. Prečo `--no-cache` negarantuje reproducibility ani security update?
9. Ktoré inputs musia byť platform-specific?
10. Ako diagnostikuješ rozdielne digests z rovnakého source commit-u?

## Glossary impact

Relevantné pojmy: build context subject, expected context inventory, effective ignore rules, named context subject, build graph node subject, cache decision subject, external cache trust domain, cache freshness gap, cache poisoning path, controlled dependency refresh, clean-room build evidence a cache retention subject.

## Oficiálna dokumentácia

- [Build context](https://docs.docker.com/build/concepts/context/)
- [Using the build cache](https://docs.docker.com/get-started/docker-concepts/building-images/using-the-build-cache/)
- [Build cache optimization](https://docs.docker.com/build/cache/optimize/)
- [Cache storage backends](https://docs.docker.com/build/cache/backends/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Dockerfile](dockerfile.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Multi-stage builds →](multi-stage-builds.md)
<!-- KNOWLEDGE-NAVIGATION:END -->