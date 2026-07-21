# Dockerfile

Dockerfile je versionovaný build program, ktorý opisuje, ako z build contextu a base image vznikne container image. Nie je to deployment manifest ani runtime orchestration súbor. Jeho primárnym výsledkom je immutable image artifact s filesystem layers a runtime metadata.

## 1. Build model

Docker build spracuje:

- Dockerfile frontend syntax,
- build context,
- base image references,
- build arguments a secrets,
- jednotlivé instructions,
- cache metadata,
- výsledný image config a layers.

Zjednodušený flow:

```text
Dockerfile + build context + external images/secrets
                     ↓
                 BuildKit
                     ↓
            image layers + config
                     ↓
              OCI image artifact
```

## 2. Parser directive

Moderný Dockerfile môže začínať syntax directive:

```dockerfile
# syntax=docker/dockerfile:1
```

Directive vyberá Dockerfile frontend a jeho feature set. Pinning konkrétnej major/minor verzie môže zlepšiť reprodukovateľnosť, ale vyžaduje plán aktualizácie.

## 3. `FROM`

`FROM` vytvára build stage:

```dockerfile
FROM debian:bookworm-slim
```

Pre reprodukovateľnejšiu build identity môže byť base image pinovaný digestom:

```dockerfile
FROM debian:bookworm-slim@sha256:<digest>
```

Tag vyjadruje ľudsky spravovanú verziu; digest identifikuje konkrétny manifest. Digest pinning potrebuje automatizovaný update workflow, inak image prestane prijímať security fixes.

## 4. `WORKDIR`

`WORKDIR` nastavuje working directory pre nasledujúce instructions a runtime default:

```dockerfile
WORKDIR /app
```

Preferuj ho pred sériou `RUN cd /app && ...`, pretože zlepšuje čitateľnosť a metadata výsledného image-u.

## 5. `COPY` a `ADD`

### `COPY`

Kopíruje files alebo directories z build contextu, stage, named contextu alebo image-u:

```dockerfile
COPY package.json package-lock.json ./
COPY --from=build /src/bin/app /usr/local/bin/app
```

### `ADD`

Má širšie semantics, napríklad podporu niektorých remote sources alebo automatického rozbalenia local tar archívu. Používaj ho iba vtedy, keď túto funkcionalitu zámerne potrebuješ.

Pre bežné lokálne files preferuj `COPY`.

## 6. `RUN`

`RUN` vykonáva build-time command:

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
```

Dôležité je vykonať update a install v rovnakej instruction, aby cache neobnovila starý package index oddelene od install kroku.

`RUN` vytvára build output, nie runtime process.

## 7. Shell a exec forma

Shell forma:

```dockerfile
RUN echo hello
CMD python app.py
```

Exec JSON forma:

```dockerfile
RUN ["/bin/sh", "-c", "echo hello"]
CMD ["python", "app.py"]
```

Pri runtime `CMD` a `ENTRYPOINT` je exec forma spravidla bezpečnejšia pre signal forwarding a argument handling, pretože nevkladá implicitný shell ako PID 1.

## 8. `ENTRYPOINT` a `CMD`

### `ENTRYPOINT`

Definuje základný executable:

```dockerfile
ENTRYPOINT ["/usr/local/bin/example"]
```

### `CMD`

Definuje default command alebo default arguments:

```dockerfile
CMD ["serve", "--port", "8080"]
```

Spolu:

```dockerfile
ENTRYPOINT ["/usr/local/bin/example"]
CMD ["serve", "--port", "8080"]
```

Runtime arguments môžu nahradiť `CMD`, zatiaľ čo `ENTRYPOINT` zostáva, pokiaľ ho operator explicitne neprepíše.

## 9. PID 1 a signals

Runtime command musí:

- prijímať termination signal,
- ukončiť child processes,
- reaping zombie processes podľa potreby,
- dokončiť graceful shutdown v timeout limite.

Shell wrapper bez `exec` môže signal zachytiť a neposlať application procesu:

```sh
#!/bin/sh
exec /usr/local/bin/example "$@"
```

`exec` nahradí shell application procesom.

## 10. `ENV` a `ARG`

### `ARG`

Build-time input:

```dockerfile
ARG APP_VERSION
RUN echo "$APP_VERSION"
```

### `ENV`

Image/runtime environment metadata:

```dockerfile
ENV APP_ENV=production
```

`ARG` nie je secret mechanism. Jeho hodnota môže ovplyvniť cache, logs alebo image history. Secrets používaj cez BuildKit secret mounts.

`ENV` zostáva vo výslednom image configu a môže ovplyvniť runtime.

## 11. Build secrets

Nepoužívaj:

```dockerfile
ARG TOKEN
RUN curl -H "Authorization: Bearer $TOKEN" ...
```

Preferuj:

```dockerfile
RUN --mount=type=secret,id=repo_token \
    TOKEN="$(cat /run/secrets/repo_token)" \
    && fetch-private-dependency "$TOKEN"
```

Secret mount nie je súčasťou výslednej layer, ale build command a tool output stále musia zabrániť jeho zapísaniu do files alebo logs.

## 12. `USER`

Nastav runtime identity:

```dockerfile
RUN useradd --system --uid 10001 --create-home app
USER 10001:10001
```

Používanie numeric UID/GID znižuje ambiguity medzi image a host identity mappingom.

Non-root nie je úplná security boundary, ale je dôležitý defense-in-depth control.

## 13. File ownership a permissions

Namiesto následného `chown` môžeš použiť:

```dockerfile
COPY --chown=10001:10001 app /app
```

Permissions definuj explicitne tam, kde sú súčasťou runtime contractu:

```dockerfile
COPY --chmod=0555 entrypoint.sh /usr/local/bin/entrypoint
```

Citlivé configuration files nesmú byť world-readable iba preto, že build beží ako root.

## 14. `EXPOSE`

```dockerfile
EXPOSE 8080
```

`EXPOSE` dokumentuje očakávaný container port v image metadata. Neotvára firewall a nepublikuje port na hoste.

Port je dostupný podľa runtime network a port-publishing configuration.

## 15. `VOLUME`

```dockerfile
VOLUME ["/data"]
```

Deklaruje mount point metadata, ale:

- nevytvára production backup policy,
- neurčuje konkrétny named volume,
- neurčuje access mode alebo storage class,
- môže komplikovať build/runtime expectations.

V orchestration prostredí je storage contract často vhodnejšie deklarovať mimo image-u.

## 16. `HEALTHCHECK`

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD ["/usr/local/bin/healthcheck"]
```

Healthcheck má overovať relevantnú schopnosť procesu, nie iba existenciu PID. Nemal by však vykonávať drahý end-to-end test každých pár sekúnd.

Image healthcheck môže runtime alebo Compose prepísať.

## 17. `STOPSIGNAL`

```dockerfile
STOPSIGNAL SIGTERM
```

Definuje preferovaný termination signal. Application musí mať zodpovedajúci handler a orchestrator musí poskytnúť dostatočný shutdown grace period.

## 18. Labels a metadata

```dockerfile
LABEL org.opencontainers.image.source="https://example.invalid/repository"
LABEL org.opencontainers.image.revision="$VCS_REF"
```

Labels môžu publikovať:

- source repository,
- revision,
- version,
- licenses,
- vendor,
- documentation.

Metadata musí byť deterministická a nesmie obsahovať secrets.

## 19. Base image výber

Posudzuj:

- support a update cadence,
- package ecosystem,
- CVE response,
- architecture support,
- libc a runtime compatibility,
- CA certificates/timezone/data requirements,
- debugging potreby,
- image provenance.

Najmenší image nie je automaticky najbezpečnejší. Minimalita znižuje attack surface, ale nesmie odstrániť runtime dependencies alebo operability.

## 20. Package installation

Zásady:

- inštaluj iba runtime dependencies,
- neponechávaj package cache,
- používaj version ranges alebo pins podľa update policy,
- nekombinuj neoverené repositories,
- oddeľ build toolchain do build stage,
- over signatures/checksums externých downloads.

Exact package pin bez update automation môže vytvoriť stale security backlog. Floating latest verzia zas znižuje reproducibility.

## 21. Determinism a reproducibility

Build ovplyvňujú:

- base image digest,
- build context content,
- package repositories,
- clocks/timestamps,
- architecture,
- compiler/toolchain versions,
- network-fetched artifacts,
- build args a secrets,
- frontend/BuildKit version.

Reproducible build neznamená iba „rovnaký Dockerfile“. Potrebuje kontrolované inputs a provenance.

## 22. Example

```dockerfile
# syntax=docker/dockerfile:1
FROM golang:1.24 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download
COPY . .
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build -trimpath -o /out/example ./cmd/example

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build --chown=65532:65532 /out/example /usr/local/bin/example
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/example"]
```

Tento príklad oddeľuje build toolchain od runtime image-u a používa cache mounts, ale stále potrebuje:

- pinning a update policy pre base images,
- dependency scanning,
- provenance,
- runtime config a secrets mimo image-u,
- health/recovery model.

## 23. Linting a policy

Dockerfile kontroluj cez:

- parser/build validation,
- linting,
- policy rules,
- image scanning,
- SBOM/provenance kontrolu,
- runtime smoke test.

Príklady policy:

- zakázaný `latest` v production,
- povinný non-root `USER`,
- zákaz plaintext secrets,
- approved base registries,
- required labels,
- maximum age base image-u,
- zákaz broad `chmod 777`.

## 24. Anti-patterny

### Secret cez `ARG` alebo `ENV`

Môže skončiť v metadata, history, cache alebo logs.

### `curl ... | sh`

Neoverený remote content sa vykoná počas build-u.

### Jedna obrovská runtime image s compilerom a package managerom

Zvyšuje veľkosť a attack surface.

### Shell-form entrypoint bez signal handlingu

Graceful shutdown môže zlyhať.

### `EXPOSE` považovaný za security control

Port nie je týmto instruction publikovaný ani chránený.

### `chmod -R 777`

Maskuje ownership problém a zvyšuje write exposure.

### Ručná runtime oprava containeru

Zmena nie je vo Dockerfile a po replacement-e zmizne.

## 25. Troubleshooting

### `COPY` nenájde file

Over build context root, `.dockerignore`, source path a case sensitivity.

### Runtime command sa nespustí

Over exec format, architecture, executable bit, shebang, dynamic linker a `ENTRYPOINT`/`CMD` kombináciu.

### Container sa nevie graceful ukončiť

Over PID 1, shell wrapper, `exec`, signal, stop timeout a application handler.

### Image obsahuje secret aj po zmazaní v ďalšej layer

Secret zostal v staršej immutable layer. Odstráň ho z build history, rotuj credential a rebuildni od čistého source-u.

### Package build je nedeterministický

Over mutable repositories, base tag, lock files, architecture a network-fetched dependencies.

## 26. Kontrolné otázky

1. Čo je výsledkom Dockerfile build-u?
2. Aký je rozdiel medzi `RUN`, `CMD` a `ENTRYPOINT`?
3. Prečo je exec forma vhodná pre runtime command?
4. Aký je rozdiel medzi `ARG` a `ENV`?
5. Prečo `ARG` nie je secret mechanism?
6. Čo `EXPOSE` reálne robí?
7. Ako `USER` ovplyvňuje runtime security?
8. Prečo sa package update a install často spájajú do jednej instruction?
9. Prečo zmazanie secretu v neskoršej layer nestačí?
10. Ktoré inputs treba kontrolovať pre reprodukovateľný build?

## Glossary impact

Relevantné pojmy: Dockerfile, Dockerfile frontend, build instruction, base image, build stage, `FROM`, `RUN`, `COPY`, `ADD`, `ENTRYPOINT`, `CMD`, `ARG`, `ENV`, `USER`, `EXPOSE`, `HEALTHCHECK`, build secret a image runtime metadata.

## Oficiálna dokumentácia

- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Dockerfile overview](https://docs.docker.com/build/concepts/dockerfile/)
- [Building best practices](https://docs.docker.com/build/building/best-practices/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Docker architecture](docker-architecture.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Build context a layer cache →](build-context-layer-cache.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
