# Build context a layer cache

Docker build nepracuje iba s Dockerfile. Potrebuje aj **build context**: množinu files a metadata dostupných builderu. Spôsob výberu contextu, poradie instructions a cache keys zásadne ovplyvňujú build performance, reproducibility, security aj výslednú veľkosť image-u.

## 1. Build context

Bežný príkaz:

```bash
docker build -t example:dev .
```

Bodka určuje current directory ako build context. Dockerfile môže cez `COPY` alebo `ADD` pristupovať iba k contentu v povolených contextoch, nie k ľubovoľnému host filesystemu.

Context môže byť:

- local directory,
- local tar archive,
- Git repository,
- remote tarball,
- stdin bez filesystem contextu,
- named context.

## 2. Context root a Dockerfile path

Dockerfile nemusí byť v root-e contextu:

```bash
docker build -f docker/production.Dockerfile .
```

Tu:

- Dockerfile je `docker/production.Dockerfile`,
- build context je stále `.`.

`COPY` paths sú vyhodnocované voči context rootu, nie voči directory Dockerfile-u.

## 3. Prečo veľký context škodí

Príliš široký context môže obsahovať:

- `.git` history,
- test artifacts,
- local dependencies,
- build outputs,
- secrets a `.env` files,
- IDE metadata,
- logs a dumps,
- inú application source tree.

Dôsledky:

- pomalší transfer alebo hashing,
- väčší cache invalidation scope,
- riziko neúmyselného `COPY`,
- secret leakage do buildera,
- nepresná provenance.

Context má byť minimálny, ale musí obsahovať všetky deklarované build inputs.

## 4. `.dockerignore`

`.dockerignore` filtruje files odoslané do build contextu.

Príklad:

```text
.git
.env
*.log
node_modules
coverage
build
*.pem
```

Dôležité:

- `.dockerignore` nie je secret manager,
- file už commitnutý v repository zostáva v Git history,
- patterns musia byť testované,
- príliš široké pravidlo môže odstrániť potrebný source,
- exceptions sa zapisujú cez `!pattern`.

Príklad:

```text
*.md
!README.md
```

## 5. Named contexts

BuildKit umožňuje pridať viac explicitne pomenovaných contexts:

```bash
docker buildx build \
  --build-context docs=./documentation \
  --build-context base=docker-image://alpine:3.21 \
  .
```

Dockerfile môže named context použiť podobne ako stage:

```dockerfile
COPY --from=docs / /usr/share/doc/example
```

Named contexts znižujú potrebu rozširovať default context a umožňujú explicitnejší supply-chain contract.

## 6. Git context

Remote Git context môže buildnúť konkrétny repository ref. Pre reprodukovateľnosť potrebuješ:

- commit SHA alebo immutable tag policy,
- kontrolu submodules,
- autentifikáciu bez secret leakage,
- overenie source identity,
- zachovanie commit metadata v provenance.

Mutable branch `main` nie je immutable build input.

## 7. Cache model

Builder môže znovu použiť výsledok predchádzajúcej instruction, keď sa zhoduje jej cache key a relevantné inputs.

Cache key môže závisieť napríklad od:

- instruction textu,
- parent stage/layer state,
- copied file contentu a metadata,
- build args,
- mount options,
- base image identity,
- frontend a platform configuration.

Cache nie je iba „layer s rovnakým poradím“. Moderný BuildKit používa graph-based execution a content-derived metadata.

## 8. Cache invalidation

Príklad zlého poradia:

```dockerfile
COPY . .
RUN npm ci
```

Každá zmena source file-u invaliduje dependency install.

Lepšie:

```dockerfile
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

Dependency layer sa invaliduje iba pri zmene dependency manifestu alebo relevantného build inputu.

Všeobecné pravidlo:

```text
stabilné a drahé kroky skôr
často meniace sa kroky neskôr
```

Nesmie to však narušiť correctness alebo secret boundary.

## 9. `RUN` cache

Builder typicky nevie, či remote package repository zmenilo obsah, iba z textu commandu.

```dockerfile
RUN apt-get update && apt-get install -y curl
```

Pri nezmenenej instruction môže byť použitá cache. Preto:

- používaj explicitný update policy,
- pravidelne rebuildni image,
- používaj controlled base image update,
- podľa potreby invaliduj konkrétny stage,
- nespoliehaj sa na `--no-cache` ako jediný security update proces.

## 10. `COPY` cache

`COPY` cache závisí od source contentu a metadata. Zmeny mimo copied paths nemusia invalidovať instruction.

Preto je výhodné kopírovať dependency manifests oddelene od zvyšku source-u.

Riziká:

- generated timestamps,
- nečakané file permissions,
- case-sensitive rozdiely,
- `.dockerignore` zmena,
- symlink behavior,
- line-ending transformations.

## 11. Cache mounts

BuildKit cache mount:

```dockerfile
RUN --mount=type=cache,target=/root/.cache/go-build \
    go build ./...
```

Alebo package cache:

```dockerfile
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y gcc
```

Cache mount:

- zrýchľuje build,
- nie je súčasťou výslednej image layer podľa bežného použitia,
- môže byť odstránený garbage collectionom,
- nesmie byť correctness dependency,
- potrebuje správny concurrency mode.

Build musí fungovať aj s prázdnou cache.

## 12. Bind mount v build-e

```dockerfile
RUN --mount=type=bind,source=.,target=/src,ro \
    make -C /src
```

Bind mount sprístupní context alebo iný source počas instruction bez automatického skopírovania všetkého do layer.

Writes do default read-only mountu nie sú povolené; pri writable variante sa nemusia stať súčasťou výslednej layer. Výsledné artifacts musíš explicitne uložiť na layer filesystem alebo skopírovať zo stage.

## 13. Secret a SSH mounts

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci
```

```dockerfile
RUN --mount=type=ssh \
    git clone git@github.com:example/private-repo.git
```

Tieto mounts znižujú riziko uloženia credentials do image layers alebo build args. Stále musíš kontrolovať:

- command output,
- package-manager config copy,
- generated files,
- cache content,
- remote dependency trust.

## 14. External cache

CI builders často nemajú stabilný local cache. BuildKit môže exportovať/importovať cache napríklad do:

- registry,
- local directory,
- CI cache backendu,
- inline image metadata podľa režimu.

Príklad:

```bash
docker buildx build \
  --cache-from type=registry,ref=registry.example.com/example/cache:main \
  --cache-to type=registry,ref=registry.example.com/example/cache:main,mode=max \
  -t registry.example.com/example/app:${GIT_SHA} \
  --push .
```

Cache artifact nie je production image a potrebuje vlastnú:

- access policy,
- retention,
- namespace isolation,
- poisoning threat model.

## 15. Cache poisoning

Nedôveryhodný actor môže ovplyvniť shared cache tak, aby privileged build použil podvrhnutý result.

Riziko rastie pri:

- shared cache medzi fork PR a protected branch,
- mutable cache refs,
- širokom registry write access-e,
- nesprávnom key namespace,
- používaní cache ako correctness source.

Ochrana:

- oddeľ trust domains,
- fork cache používaj iba read-only alebo izolovane,
- privileged release build nepoužíva untrusted write cache,
- zachovaj provenance a rebuild capability,
- pinuj external executable inputs.

## 16. Layer cache vs. package cache

### Layer/instruction cache

Znovu používa celý výsledok build graph node-u.

### Cache mount

Zachová pomocné dáta pre nový execution instruction.

Príklad:

- layer cache môže preskočiť celé `go build`,
- cache mount umožní `go build` znovu prebehnúť rýchlejšie s cached objects.

Tieto mechanizmy riešia odlišné problémy.

## 17. Multi-platform cache

Cache musí rozlišovať platform-relevantné inputs:

- `TARGETPLATFORM`,
- `BUILDPLATFORM`,
- architecture-specific toolchain,
- native dependencies,
- emulation vs. native builder.

Cache result pre `linux/amd64` nemusí byť validný pre `linux/arm64`.

## 18. Reproducibility vs. cache

Cache môže skryť nedeterministický build. Preto release workflow potrebuje občas:

- clean-room rebuild,
- comparison výsledných digests,
- provenance kontrolu,
- base/dependency refresh,
- explicitný cache bypass pre relevantný stage.

`--no-cache` nepinuje remote dependencies a samo osebe negarantuje reproducibility.

## 19. Build performance observability

Sleduj:

- context size,
- context transfer time,
- cache hit rate,
- duration per stage,
- external download time,
- cache export/import size,
- final image size,
- changed layers medzi releases,
- builder CPU/memory/disk pressure.

BuildKit progress output:

```bash
docker buildx build --progress=plain .
```

## 20. Anti-patterny

### Context je celý monorepo bez `.dockerignore`

Zvyšuje transfer, invalidáciu a secret exposure.

### `COPY . .` pred dependency install

Každá source zmena invaliduje drahý dependency layer.

### Cache ako povinný source artifacts

Po garbage collectione build zlyhá alebo vytvorí iný výsledok.

### Shared writable cache medzi untrusted a release builds

Vzniká cache-poisoning path.

### Secret uložený do package-manager cache

Secret mount nezabráni tomu, aby si ho tool skopíroval inde.

### `--no-cache` ako security patch stratégia

Nezaručuje nové ani dôveryhodné remote inputs.

## 21. Troubleshooting

### Build odosiela stovky MB contextu

Over context root a `.dockerignore`. Skontroluj `.git`, dependencies, artifacts a dumps.

### Cache sa neočakávane invaliduje

Over zmenené copied files, build args, base digest, permissions, frontend version a platform.

### Cache sa neočakávane používa

Over mutable remote dependencies a explicitne invaliduj konkrétny stage alebo zmeň controlled cache-busting input.

### CI nemá cache hit

Over cache export po úspešnom build-e, registry auth, ref naming, platform, builder driver a retention.

### Release image sa líši pri rovnakom commite

Porovnaj base digest, package indexes, timestamps, architecture, generated files, toolchain a build arguments.

## 22. Kontrolné otázky

1. Čo je build context?
2. Voči čomu sa vyhodnocuje source path v `COPY`?
3. Čo `.dockerignore` rieši a čo nerieši?
4. Prečo záleží na poradí Dockerfile instructions?
5. Aký je rozdiel medzi layer cache a cache mountom?
6. Prečo build musí fungovať s prázdnou cache?
7. Ako vzniká cache poisoning?
8. Prečo `--no-cache` negarantuje reprodukovateľnosť?
9. Ako named contexts zlepšujú build boundary?
10. Ktoré metriky pomáhajú diagnostikovať pomalý build?

## Glossary impact

Relevantné pojmy: build context, context root, `.dockerignore`, named context, Git build context, build cache, cache key, cache invalidation, cache mount, build bind mount, secret mount, SSH mount, external cache, cache poisoning a clean-room rebuild.

## Oficiálna dokumentácia

- [Build context](https://docs.docker.com/build/concepts/context/)
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Using the build cache](https://docs.docker.com/get-started/docker-concepts/building-images/using-the-build-cache/)
- [Build cache optimization](https://docs.docker.com/build/cache/optimize/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Dockerfile](dockerfile.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Multi-stage builds →](multi-stage-builds.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
