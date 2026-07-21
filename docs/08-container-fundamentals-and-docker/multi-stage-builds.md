# Multi-stage builds

Multi-stage build používa viac `FROM` instructions v jednom Dockerfile. Každý stage má vlastný filesystem a build graph. Výsledný runtime image môže skopírovať iba potrebné artifacts z build alebo test stages a nemusí obsahovať compiler, source code, package manager ani dočasné credentials.

## 1. Základný model

```dockerfile
FROM golang:1.24 AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /out/example ./cmd/example

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/example /usr/local/bin/example
ENTRYPOINT ["/usr/local/bin/example"]
```

Prvý stage obsahuje toolchain. Druhý stage obsahuje iba runtime artifact a metadata.

## 2. Stage identity

Stage môže byť pomenovaný:

```dockerfile
FROM node:22 AS dependencies
FROM node:22 AS test
FROM nginx:alpine AS runtime
```

Referencie podľa mena sú stabilnejšie než numerické indexy:

```dockerfile
COPY --from=dependencies /app/node_modules /app/node_modules
```

Premiestnenie stages potom nezmení význam odkazu.

## 3. Build stage vs. final stage

### Build stage

Môže obsahovať:

- compiler,
- SDK,
- headers,
- package manager,
- source code,
- tests,
- debug tools,
- temporary cache a secrets.

### Final stage

Má obsahovať iba:

- runtime executable alebo application files,
- potrebné shared libraries,
- CA certificates/timezone data podľa potreby,
- non-root identity,
- runtime metadata,
- healthcheck helper, ak je opodstatnený.

Menší final image znižuje transfer a attack surface, ale musí zostať operovateľný.

## 4. Copy medzi stages

```dockerfile
COPY --from=build /out/example /usr/local/bin/example
```

Source path je vyhodnotený od rootu source stage filesystemu.

Môžeš kopírovať aj z external image:

```dockerfile
COPY --from=busybox:1.37 /bin/busybox /usr/local/bin/busybox
```

External image reference je supply-chain dependency a potrebuje pinning/update policy.

## 5. Shared base stage

```dockerfile
FROM python:3.13-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1

FROM base AS test
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY . .
RUN pytest

FROM base AS runtime
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
CMD ["python", "-m", "src.app"]
```

Shared base znižuje duplicitu, ale neznamená, že test a runtime dependency graph sú automaticky rovnaké. Runtime stage musí používať production lock/requirements contract.

## 6. Targeted builds

Konkrétny stage možno buildnúť cez:

```bash
docker build --target test -t example:test .
```

Použitie:

- development image,
- test execution,
- debugging stage,
- artifact export,
- platform-specific branch.

Release pipeline musí explicitne určiť final target a nesmie omylom publikovať debug alebo build stage.

## 7. Test stage

```dockerfile
FROM build AS unit-test
RUN go test ./...
```

Test stage môže zlyhaním zastaviť build. Dôležité však je, či je test stage súčasťou dependency graphu final targetu alebo ho pipeline explicitne buildne.

Ak final stage nemá dependency na `unit-test`, builder ho nemusí vykonať:

```bash
docker build --target unit-test .
docker build --target runtime .
```

Pipeline musí mať jasný evidence flow medzi testovaným commitom/artifactom a publikovaným final image-om.

## 8. Artifact stage

Minimalistický stage môže slúžiť na export artifacts:

```dockerfile
FROM scratch AS artifact
COPY --from=build /out/ /out/
```

BuildKit môže output exportovať do local directory:

```bash
docker buildx build --target artifact --output type=local,dest=./dist .
```

Takto môže jeden build graph produkovať image aj samostatné binaries, SBOM alebo packages. Každý output potrebuje provenance.

## 9. Dependencies a cache

Dobre navrhnutý multi-stage build oddeľuje:

1. dependency metadata,
2. dependency download,
3. source copy,
4. compile/test,
5. runtime assembly.

Príklad:

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

Source change neinvaliduje dependency stage, pokiaľ sa dependency manifests nezmenia.

## 10. Secrets v multi-stage build-e

Nesprávny predpoklad: „Secret je v build stage, takže sa nemôže dostať do final image-u.“

Riziká:

- secret sa skopíruje s artifact directory,
- build output ho embedne do binary/bundle,
- command ho zapíše do logs,
- cache/export zachová secret file,
- `COPY --from=build / /` prenesie celý filesystem.

Používaj secret mounts a explicitné narrow `COPY --from` paths. Po build-e skenuj final artifact aj build logs.

## 11. Static a dynamic binaries

Pri kopírovaní binary do minimalistického final stage over:

- architecture,
- dynamic linker,
- required shared libraries,
- CA certificates,
- DNS resolver behavior,
- timezone/locale data,
- user/group files,
- writable paths.

Diagnostika:

```bash
file ./example
ldd ./example
```

`FROM scratch` funguje iba pre workload s kompletne vyriešenými runtime dependencies.

## 12. Distroless a minimal images

Distroless/minimal runtime môže odstrániť shell a package manager.

Výhody:

- menší attack surface,
- menší image,
- menej runtime mutation paths.

Nevýhody:

- zložitejšie interactive debugging,
- potrebné external observability a ephemeral debug tooling,
- missing CA/timezone/NSS dependencies sa diagnostikujú ťažšie.

Debugging by nemal vyžadovať permanentný shell v production image. Môže používať debug variant, sidecar/ephemeral container alebo host-level tooling podľa platformy.

## 13. Development target

```dockerfile
FROM base AS development
RUN install-debug-tools
CMD ["development-server"]
```

Development stage môže mať:

- hot reload,
- debugger,
- source bind mount contract,
- test tools.

Nikdy ho nepublikuj pod production tagom. Pipeline policy má overovať final target a image contents.

## 14. Multi-platform build

```dockerfile
# syntax=docker/dockerfile:1
FROM --platform=$BUILDPLATFORM golang:1.24 AS build
ARG TARGETOS TARGETARCH
RUN GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o /out/example ./cmd/example

FROM alpine:3.21
COPY --from=build /out/example /usr/local/bin/example
```

`BUILDPLATFORM` je platforma buildera; `TARGETPLATFORM`/`TARGETOS`/`TARGETARCH` opisujú výsledný image target.

Cross-compilation, emulation a native builders majú odlišné performance a compatibility riziká.

## 15. Rebase a stage reuse

Moderný BuildKit môže pri vhodnom graph-e znovu použiť layers alebo vytvoriť nový manifest bez plného rebuild-u. To však nemení požiadavku overiť:

- nový base digest,
- runtime compatibility,
- security scan,
- smoke/integration test,
- provenance výsledného image-u.

Rebase nie je iba metadata operácia z pohľadu risku.

## 16. Failure boundaries

### Build stage prejde, final stage zlyhá

Chýba artifact, runtime dependency, permission alebo platform compatibility.

### Test stage prejde, ale nebol viazaný na release

Pipeline mohla publikovať iný graph alebo target.

### Final image beží lokálne, ale nie v production

Rozdiel môže byť v architecture, read-only filesysteme, UID, certificates, network alebo mounted config.

### Cache použije starý artifact

Over stage inputs, copied paths a external cache trust.

## 17. Anti-patterny

### `COPY --from=build / /`

Prenesie toolchain, caches, source a potenciálne secrets.

### Final stage je rovnaký ako build stage

Multi-stage build neprináša isolation ani minimalizáciu.

### Test stage existuje, ale pipeline ho nikdy nebuildne

Falošný pocit quality gate.

### Debug stage publikovaný ako production

Obsahuje zbytočné tools a širšie privileges.

### `scratch` bez kontroly runtime dependencies

Binary zlyhá na dynamic linker, DNS alebo CA certificates.

### Mutable external image v `COPY --from`

Build input sa mení bez zmeny Dockerfile-u.

## 18. Troubleshooting

### `COPY --from` nenájde file

Over source stage name, absolute path, build output a conditional target behavior.

### Runtime hlási `no such file or directory`, hoci binary existuje

Často chýba dynamic linker alebo interpreter uvedený v shebang-u.

### Final image je stále veľký

Over copied directories, base image, duplicate dependencies, package cache a image history.

### Test stage sa nespustil

Over final target dependency graph alebo explicitný `--target test` pipeline krok.

### Multi-platform binary má `exec format error`

Over target architecture, cross-compilation variables, emulation a platform manifest.

## 19. Kontrolné otázky

1. Čo vytvára každý `FROM` v Dockerfile?
2. Prečo sú pomenované stages vhodnejšie než číselné indexy?
3. Ako multi-stage build znižuje final image attack surface?
4. Prečo secret v build stage stále môže uniknúť?
5. Kedy sa test stage nemusí automaticky vykonať?
6. Čo musí obsahovať minimalistický runtime image pre dynamic binary?
7. Aký je rozdiel medzi development a production targetom?
8. Ako sa používajú `BUILDPLATFORM` a `TARGETPLATFORM`?
9. Prečo `FROM scratch` nie je univerzálne riešenie?
10. Ako dokážeš preukázať, že publikovaný image pochádza z testovaného graphu?

## Glossary impact

Relevantné pojmy: multi-stage build, build stage, final stage, named stage, build target, test stage, artifact stage, development target, distroless image, scratch image, cross-compilation, `BUILDPLATFORM`, `TARGETPLATFORM` a narrow artifact copy.

## Oficiálna dokumentácia

- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Dockerfile `COPY --from`](https://docs.docker.com/reference/dockerfile/#copy---from)
- [Building best practices](https://docs.docker.com/build/building/best-practices/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Build context a layer cache](build-context-layer-cache.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Volumes a bind mounts →](volumes-bind-mounts.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
