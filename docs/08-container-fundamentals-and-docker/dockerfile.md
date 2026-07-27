# Dockerfile

Dockerfile je versionovaný build program. Z deklarovaných a externých inputs vytvorí stage graph, filesystem changesets a image runtime metadata. Nie je to deployment manifest ani záruka, že výsledný workload bude správne fungovať v produkcii.

Dominantný model kapitoly je:

```text
build intent a immutable input inventory
→ Dockerfile frontend a parse
→ stage graph
→ instruction execution
→ filesystem a image-config transitions
→ final image subject
→ build/policy evidence
→ runtime-contract test
→ publication a update lifecycle
```

Instruction katalóg má význam iba v tomto modeli. Každá instruction buď vytvára nový stage, mení build filesystem, alebo zapisuje metadata, ktoré neskôr ovplyvnia runtime process.

## 1. Atlas Payments Dockerfile ako jeden program

Atlas Payments publikuje release `R42` pre `linux/amd64` a `linux/arm64`.

Build subject obsahuje:

- source commit `C42`,
- Dockerfile digest,
- Dockerfile frontend identity,
- build context inventory,
- base image digests,
- dependency lock files,
- target platform,
- build args a secret references,
- builder/BuildKit identity,
- selected final target,
- expected runtime user, command, port a writable paths.

Výsledný image subject obsahuje:

- image index alebo platform manifest digest,
- image config digest,
- ordered layer digests,
- effective `ENTRYPOINT`, `CMD`, `USER`, `ENV`, labels a health metadata,
- provenance a test/policy evidence.

„Rovnaký Dockerfile“ nestačí. Ak sa zmení base tag, remote package repository, frontend alebo build context, mení sa aj program input a potenciálne výsledný artifact.

## 2. Parse a stage graph

Dockerfile frontend interpretuje syntax a vytvára build graph.

```dockerfile
# syntax=docker/dockerfile:1
```

Každý `FROM` vytvára stage:

```dockerfile
FROM golang:1.24 AS build
FROM gcr.io/distroless/static-debian12:nonroot AS runtime
```

Stage identity je súčasť build graphu. Pomenované stages sú stabilnejšie než numerické odkazy:

```dockerfile
COPY --from=build /out/payments-api /usr/local/bin/payments-api
```

Frontend identity je build dependency. Novšia alebo iná syntax implementácia môže zmeniť dostupné features, validation alebo graph behavior, preto musí byť zahrnutá do provenance a update policy.

## 3. `FROM`: prvý supply-chain a runtime contract

`FROM` určuje parent filesystem a metadata jedného stage-u.

```dockerfile
FROM debian:bookworm-slim@sha256:<digest>
```

Tag je discovery/version label. Digest je konkrétna content identity.

### Failure boundary: mutable base po approval

Security review schváli build nad jedným `debian:bookworm-slim`, no neskorší release build resolveuje rovnaký tag na iný digest. Source commit aj Dockerfile sú rovnaké, ale:

- package inventory sa zmení,
- runtime libraries sa môžu zmeniť,
- scan evidence už nepatrí k novému image-u,
- výsledný manifest má iný subject.

Digest pinning tento race odstráni, ale vytvára povinnosť pravidelného a reviewovaného update workflowu. Pin bez aktualizácie iba konzervuje starý base.

## 4. Build-time filesystem transitions

### `WORKDIR`

```dockerfile
WORKDIR /src
```

Mení working-directory context pre nasledujúce instructions a podľa final configu môže nastaviť runtime default.

### `COPY`

```dockerfile
COPY go.mod go.sum ./
COPY --chown=65532:65532 /out/payments-api /usr/local/bin/payments-api
```

`COPY` prenáša content z povoleného contextu, named contextu, image-u alebo stage-u. Source identity, file metadata, ownership a target path sú súčasťou build contractu.

### `ADD`

`ADD` má širšie semantics, napríklad automatic local tar extraction alebo podporované remote/Git sources podľa frontend feature-u. Pre bežný local copy preferuj `COPY`, aby bol transition explicitnejší.

### `RUN`

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
```

`RUN` vykonáva build-time process a vytvára nový filesystem result. Nevytvára budúci runtime process.

Spájanie package index refreshu a install operácie v jednej instruction zabraňuje jednoduchému reuse starého index layeru oddelene od install kroku. Stále však treba riešiť mutable repository inputs a rebuild/update policy.

## 5. Image config transitions

Nie všetky instructions vytvárajú významný filesystem changeset. Niektoré zapisujú runtime metadata do image configu.

### `ENV` a `ARG`

```dockerfile
ARG APP_VERSION
ENV APP_ENV=production
```

- `ARG` je build-time input;
- `ENV` sa stáva image/runtime metadata.

Ani jedno nie je bezpečný secret transport.

`ARG` môže ovplyvniť:

- build history,
- command output,
- cache keys,
- generated files.

`ENV` môže byť viditeľné v image configu, runtime inspecte, process environment a dumpoch.

### `USER`

```dockerfile
USER 65532:65532
```

Definuje default runtime credentials. Je to iba jedna vrstva effective runtime policy; runtime môže hodnotu prepísať a mounted paths musia mať kompatibilný ownership/LSM contract.

### `EXPOSE`

```dockerfile
EXPOSE 8080
```

Je metadata o očakávanom container porte. Nevytvára host listener, port-forwarding ani firewall allow.

### `VOLUME`

```dockerfile
VOLUME ["/data"]
```

Deklaruje mount-point metadata. Neurčuje production data identity, backend, access mode, backup, fencing ani restore policy. Stateful storage contract patrí predovšetkým do runtime/orchestration vrstvy.

## 6. `ENTRYPOINT`, `CMD` a process contract

Exec forma:

```dockerfile
ENTRYPOINT ["/usr/local/bin/payments-api"]
CMD ["serve", "--port", "8080"]
```

Výsledný process argument model je približne:

```text
ENTRYPOINT + CMD/default runtime arguments
```

Runtime arguments typicky nahradia `CMD`. Explicitný entrypoint override môže nahradiť aj `ENTRYPOINT`.

Shell forma:

```dockerfile
CMD payments-api serve
```

môže vytvoriť shell ako PID 1. To mení:

- signal delivery,
- argument expansion,
- exit-code propagation,
- zombie reaping,
- graceful shutdown.

Wrapper musí pri bežnom handoffe použiť `exec`:

```sh
#!/bin/sh
set -eu
exec /usr/local/bin/payments-api "$@"
```

## 7. Runtime readiness metadata

### `HEALTHCHECK`

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD ["/usr/local/bin/payments-health"]
```

Healthcheck má testovať schopnosť relevantnú pre runtime contract. `pgrep` alebo existencia PID môže potvrdiť liveness, nie readiness či business correctness.

Image healthcheck je default metadata. Runtime alebo Compose ho môže prepísať alebo ignorovať.

### `STOPSIGNAL`

```dockerfile
STOPSIGNAL SIGTERM
```

Definuje preferovaný termination signal. Úspešné graceful shutdown stále potrebuje:

- správny PID 1,
- application handler,
- child-process propagation,
- dostatočný runtime stop timeout,
- overenie, že request drain a state flush prebehli.

## 8. Build secrets: neviditeľný mount nie je úplné riešenie

Použi BuildKit secret mount:

```dockerfile
RUN --mount=type=secret,id=repo_token \
    TOKEN="$(cat /run/secrets/repo_token)" \
    && fetch-private-dependency "$TOKEN"
```

Secret mount sa štandardne nestane súčasťou výsledného layeru. Secret však môže stále uniknúť cez:

- stdout/stderr,
- tool config alebo generated file,
- copied artifact directory,
- package/build cache,
- crash dump,
- provenance alebo metadata pri nesprávnom použití.

### Failure boundary: `ARG TOKEN` a false cleanup

Build použije:

```dockerfile
ARG TOKEN
RUN fetch-private-dependency "$TOKEN"
RUN rm -f /tmp/token
```

Odstránenie file-u v neskoršej instruction neodstráni bytes ani metadata zo staršieho immutable layeru, history alebo cache. Incident recovery vyžaduje:

1. revoke/rotate credential,
2. odstrániť secret zo source a build pathu,
3. zneplatniť kompromitovaný cache/artifact graph,
4. rebuildnúť z čistého subjectu,
5. overiť všetky platform variants,
6. auditovať použitie credentialu.

## 9. Ownership, permissions a read-only runtime

Build typicky beží s vysokými oprávneniami vo stage-i, ale final runtime by mal mať explicitný identity contract.

```dockerfile
COPY --from=build --chown=65532:65532 \
  /out/payments-api /usr/local/bin/payments-api
USER 65532:65532
```

Výsledný image musí definovať:

- executable a shared-library permissions,
- readable configuration paths,
- writable runtime paths,
- stable numeric UID/GID,
- behavior pri read-only root filesysteme,
- compatibility s volume a user-namespace mappingom.

`chmod -R 777` neopravil identity model. Iba rozšíril write authority.

## 10. Base, packages a external downloads

Každý external download je build dependency.

Bezpečnejší contract zahŕňa:

- approved source,
- immutable version alebo snapshot podľa update modelu,
- checksum/signature verification,
- TLS a repository trust,
- dependency lock,
- explicitnú architecture/platform,
- update a deprecation ownera.

Anti-pattern:

```dockerfile
RUN curl -fsSL https://example.invalid/install.sh | sh
```

Source sa môže zmeniť bez zmeny Dockerfile-u a okamžite sa vykonáva s build-stage authority.

Package pins a floating ranges majú odlišný trade-off:

- úplne mutable latest znižuje reproducibility;
- exact pin bez update automation vytvára security backlog;
- správny model kombinuje controlled immutable subject s pravidelným update workflowom.

## 11. Deterministický artifact a provenance

Image výsledok ovplyvňujú:

- source a context content,
- Dockerfile/frontend,
- base digests,
- external repositories a downloads,
- lock files,
- build args a platform,
- clocks, generated timestamps a locale,
- toolchain/compiler,
- builder a cache inputs,
- selected final target.

Build evidence musí odpovedať:

```text
ktorý source
+ ktoré inputs
+ ktorý builder/frontend
+ ktorý stage/target
+ ktorá platforma
→ ktorý image digest
```

Reproducibility nie je iba cache hit. Cache môže vrátiť rovnaký starý result aj vtedy, keď remote mutable input už mal byť aktualizovaný.

## 12. Causal walkthrough: running container, green health a nefunkčný shutdown

### Symptóm

Release `R42` sa spustí. Docker reportuje `running` a healthcheck je green, ale API po strate database connection vracia chyby. Pri rollout replacement-e container ignoruje `SIGTERM` a musí byť killnutý.

### Competing hypotheses

1. runtime prepísal `ENTRYPOINT` alebo `CMD`;
2. shell forma vytvorila shell PID 1;
3. wrapper nepoužil `exec`;
4. `STOPSIGNAL` nezodpovedá application handleru;
5. healthcheck overuje iba existenciu processu;
6. image neobsahuje správny readiness helper;
7. stop timeout je kratší než application drain;
8. problém je mimo image-u v orchestrator policy.

### Discriminating observation points

Najprv potvrď image a runtime subject:

```bash
docker image inspect <digest>
docker inspect <container>
```

Porovnaj:

- image `Entrypoint`, `Cmd`, `Healthcheck` a `StopSignal`,
- runtime overrides,
- process tree a PID 1,
- signal delivery a exit timeline,
- healthcheck command/output,
- listener a dependency readiness,
- application shutdown logs.

### Finding

Dockerfile používal:

```dockerfile
CMD payments-api serve
HEALTHCHECK CMD pgrep payments-api
```

Shell bol PID 1 a neposlal termination signal child procesu. Healthcheck ostal green, pretože process existoval, hoci database dependency a request path nefungovali.

### Recovery

1. zastav rollout a obmedz traffic na zdravé instances;
2. rebuildni image s exec-form `ENTRYPOINT`/`CMD`;
3. pridaj readiness check nad relevantným dependency/request outcome-om;
4. nastav a otestuj zodpovedajúci stop signal a grace period;
5. over signal, request drain, exit code a replacement;
6. publikuj nový digest a nekoriguj live container ručne.

### Skoršie controls

- Dockerfile lint pre shell-form runtime command,
- image-config contract assertions,
- production-like readiness test,
- termination integration test,
- policy vyžadujúca non-root a explicitný final target,
- runtime evidence viazaná na exact image digest.

## 13. Worked failure boundaries

### `COPY` nenájde file

Mechanizmus:

```text
context root alebo ignore rule
→ file nie je v builder input inventory
→ COPY source resolution zlyhá
```

Over context root, `.dockerignore`, case sensitivity, symlink a Dockerfile path. Source path sa nevyhodnocuje voči directory Dockerfile-u, ale voči contextu alebo explicitnému source stage/contextu.

### `no such file or directory`, hoci binary existuje

Path môže existovať, ale kernel nevie načítať:

- dynamic linker,
- interpreter zo shebang-u,
- správnu architecture,
- required shared library.

Filesystem existence a executable runtime compatibility sú odlišné.

### Non-root nevie zapisovať

Over:

- effective runtime UID/GID,
- file ownership v image,
- mount source identity,
- user namespace mapping,
- Unix ACL/mode,
- SELinux/AppArmor,
- read-only root/mount policy.

Nemeň image na root alebo `777` bez identifikácie konkrétneho denied objectu a operation.

### Security rebuild stále obsahuje starý vulnerable package

Možné príčiny:

- nezmenený pinned base digest,
- `RUN` instruction obnovená z cache,
- mutable repository snapshot nebol refreshnutý,
- scanner analyzuje iný platform manifest,
- release publishuje starý target/digest.

Tento failure sa detailnejšie rieši v nasledujúcej kapitole o contextoch a cache.

## 14. Referenčný instruction katalóg

| Instruction | Hlavný build/runtime efekt | Kľúčová failure boundary |
|---|---|---|
| `FROM` | vytvorí stage a parent subject | mutable alebo unsupported base |
| `WORKDIR` | mení working-directory context | neexistujúci/neprístupný runtime path |
| `COPY` | prenesie declared content/metadata | wrong context, broad copy, ownership |
| `ADD` | širší source/extraction transition | hidden remote/extraction semantics |
| `RUN` | vykoná build process a uloží result | mutable remote input, stale cache, secret output |
| `ARG` | build-time value | history/cache/log exposure |
| `ENV` | image/runtime metadata | secret/config drift |
| `USER` | default runtime credentials | mount/permission incompatibility |
| `ENTRYPOINT` | base executable | override a PID 1 behavior |
| `CMD` | default command/arguments | shell form a runtime replacement |
| `EXPOSE` | port metadata | false assumption o publication/firewall |
| `VOLUME` | mount-point metadata | implicit anonymous data lifecycle |
| `HEALTHCHECK` | default health command | shallow oracle a false green |
| `STOPSIGNAL` | preferred termination signal | handler/grace-period mismatch |
| `LABEL` | artifact metadata | nondeterministic alebo sensitive metadata |

Katalóg sumarizuje semantics. Bez dominantného build-to-runtime modelu však nevysvetlí výsledný artifact ani failure.

## 15. Reference Dockerfile

```dockerfile
# syntax=docker/dockerfile:1

FROM --platform=$BUILDPLATFORM golang:1.24@sha256:<build-digest> AS build
ARG TARGETOS TARGETARCH
WORKDIR /src

COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

COPY cmd ./cmd
COPY internal ./internal
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH \
    go build -trimpath -o /out/payments-api ./cmd/payments-api

FROM gcr.io/distroless/static-debian12:nonroot@sha256:<runtime-digest> AS runtime
COPY --from=build --chown=65532:65532 \
  /out/payments-api /usr/local/bin/payments-api
USER 65532:65532
EXPOSE 8080
STOPSIGNAL SIGTERM
ENTRYPOINT ["/usr/local/bin/payments-api"]
CMD ["serve", "--port", "8080"]
```

Aj tento Dockerfile potrebuje mimo samotného textu:

- immutable dependency a context subject,
- test stage alebo external test evidence,
- provenance a SBOM,
- multi-platform validation,
- production-like readiness a termination test,
- runtime configuration, identity, network a storage policy.

## 16. Praktické controls

- pinuj base a external image subjects a automatizuj ich update;
- používaj narrow build contexts a `COPY` paths;
- používaj BuildKit secret/SSH mounts, nie `ARG` alebo `ENV` secrets;
- oddeľ build toolchain od final runtime stage;
- používaj exec-form runtime command;
- definuj numeric non-root identity a explicitné writable paths;
- testuj image config aj effective runtime overrides;
- viaž scan, SBOM, provenance a runtime test na exact digest;
- zakáž publication debug/build targetu pod production reference;
- pri incidente rebuildni clean artifact; neopravuj live container.

## 17. Kontrolné otázky

1. Prečo Dockerfile predstavuje program a nie iba zoznam instructions?
2. Čo patrí do immutable build input inventory?
3. Ako `FROM` ovplyvňuje supply chain aj runtime compatibility?
4. Aký je rozdiel medzi filesystem a image-config transitionom?
5. Prečo `ARG` a `ENV` nie sú secret mechanisms?
6. Ako `ENTRYPOINT` a `CMD` vytvoria runtime process contract?
7. Prečo healthcheck môže byť green pri nefunkčnej aplikácii?
8. Prečo zmazanie secretu v neskoršej instruction nestačí?
9. Ako sa odlišuje image default od effective runtime configuration?
10. Ktoré dôkazy spájajú source a final image digest?

## Glossary impact

Relevantné pojmy: Dockerfile program subject, immutable build input inventory, Dockerfile frontend identity, stage graph, filesystem transition, image-config transition, runtime process contract, effective image metadata, build secret path, image-config contract test a clean image rebuild.

## Oficiálna dokumentácia

- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Dockerfile overview](https://docs.docker.com/build/concepts/dockerfile/)
- [Building best practices](https://docs.docker.com/build/building/best-practices/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Docker architecture](docker-architecture.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Build context a layer cache →](build-context-layer-cache.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
