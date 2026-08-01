# Dockerfile

Dockerfile je versionovaný build program. Neopisuje iba výsledný filesystem; určuje, ktoré inputs sa načítajú, v akom poradí sa vykonajú build operácie, ako sa vytvorí stage graph a aké runtime defaults sa zapíšu do image configu.

Dockerfile však nie je deployment manifest. Neurčuje konečný host port, production secret, network policy, resource limity ani to, či aplikácia bude po štarte ready. Jeho úlohou je vytvoriť reprodukovateľný aplikačný artifact s úzkym a zrozumiteľným runtime contractom.

Budeme postupne skladať Dockerfile pre `payments-api`. Aplikácia je napísaná v Go, testy sa majú vykonať v samostatnom stage-i a final image má obsahovať iba statický binary a minimum runtime metadata.

## Rýchla orientácia v Dockerfile instructions

Nasledujúca tabuľka slúži ako mapa celej Dockerfile syntaxe. Detailné správanie, scope, cache a runtime dôsledky jednotlivých instructions vysvetľujú nasledujúce časti kapitoly.

| Instruction | Kedy pôsobí | Čo robí | Dôležitá hranica alebo typická chyba |
|---|---|---|---|
| `FROM` | build | Začína nový build stage z base image-u, predchádzajúceho stage-u alebo `scratch`. | Tag nie je immutable identity; stage sa nemusí vykonať, ak neleží v dependency graph-e zvoleného targetu. |
| `ARG` | build | Deklaruje build-time parameter a voliteľný default. | Nie je runtime environment; nie je vhodný na secrets a scope pred `FROM` sa automaticky neprenáša do stage-u. |
| `ENV` | build metadata a runtime default | Zapíše environment premennú pre ďalšie build instructions a do image configu. | Runtime ju môže prepísať; secret zostáva viditeľný v image alebo container metadata. |
| `LABEL` | build metadata | Pridáva key-value metadata, napríklad OCI title, source, version alebo revision. | Label nie je cryptographic provenance a jeho hodnotu môže producer uviesť nesprávne. |
| `RUN` | build | Vykoná command v aktuálnom stage-i a uloží filesystem/config changes do build resultu. | Nezamieňať s runtime `CMD`; shell a exec form majú odlišnú expansion, signal a quoting semantics. |
| `COPY` | build | Kopíruje files alebo directories z build/named contextu či iného stage-u. | Source je obmedzený contextom a `.dockerignore`; `--from` prenáša artifact, nie celý runtime state stage-u. |
| `ADD` | build | Kopíruje podobne ako `COPY`, navyše má širšie semantics, napríklad lokálne tar extraction a podporované remote/Git sources. | Pre obyčajné local files je transparentnejší `COPY`; implicitné rozbalenie alebo remote input môže skryť build contract. |
| `WORKDIR` | build metadata a runtime default | Nastaví pracovný adresár pre nasledujúce `RUN`, `COPY`, `ADD`, `CMD` a `ENTRYPOINT`. | Relative paths sa skladajú s predchádzajúcim `WORKDIR`; implicitný directory z base image-u môže byť prekvapivý. |
| `USER` | build metadata a runtime default | Nastaví default UID/GID pre nasledujúce build kroky a runtime process. | Runtime môže usera prepísať; numeric UID bez potrebných permissions alebo home/passwd contractu môže aplikáciu rozbiť. |
| `SHELL` | build metadata | Mení default shell používaný shell-form instructions v aktuálnom stage-i. | Ovplyvňuje parsing, flags a error semantics ďalších `RUN`, `CMD` a `ENTRYPOINT` shell forms. |
| `EXPOSE` | image metadata | Dokumentuje port a protocol, na ktorom má application počúvať. | Nevytvára host port, listener, route ani firewall rule. |
| `VOLUME` | image metadata a runtime mount intent | Označuje path ako volume mount point. | Nevlastní konkrétny production volume ani backup; neskoršie build changes pod mount pathom môžu mať prekvapivé semantics. |
| `STOPSIGNAL` | image runtime default | Nastaví default signal pre stop lifecycle containeru. | Nezaručuje graceful shutdown; PID 1 a application musia signal spracovať v dostupnom grace period. |
| `HEALTHCHECK` | image runtime default | Definuje command a timing pre Docker health state. | Health nie je automaticky service reachability ani business correctness a runtime ho môže prepísať alebo vypnúť. |
| `ENTRYPOINT` | image runtime default | Určuje hlavný executable alebo shell command containeru. | Exec form poskytuje priame argv a signal semantics; `--entrypoint` ho môže runtime prepísať. |
| `CMD` | image runtime default | Určuje default command alebo default arguments pre `ENTRYPOINT`. | Pri `docker run IMAGE ...` sa typicky nahrádza; nevykonáva sa počas buildu. |
| `ONBUILD` | deferred build | Uloží trigger, ktorý sa vykoná, keď je image použitý ako base v inom Dockerfile-i. | Side effect je odložený do child buildu, preto musí byť úzky a predvídateľný; nesmie používať zakázané nested instructions. |
| `MAINTAINER` | image metadata, deprecated | Historicky zapisoval autora image-u. | Je deprecated; používaj OCI-compatible `LABEL`, napríklad `org.opencontainers.image.authors`. |
| `# syntax=...` | parser/build frontend | Vyberá Dockerfile frontend a dostupnú syntax. | Nie je bežný comment, ak je v úvodnej parser-directive pozícii; zmena frontendu môže zmeniť build semantics. |
| `# escape=...` | parser | Mení escape character, najmä pri Windows Dockerfiles. | Ovplyvňuje line continuation a parsing celého súboru. |
| `# check=...` | build checks | Konfiguruje Dockerfile build checks podporované frontendom. | Je to policy nad authoringom, nie runtime kontrola image-u alebo containeru. |

## 1. Parser directive a syntax frontend

Dockerfile môže začínať parser directive:

```dockerfile
# syntax=docker/dockerfile:1
```

BuildKit podľa nej resolve-ne Dockerfile frontend a dostupnú syntax. Novšie features, napríklad `RUN --mount`, závisia od frontend contractu.

Directive nie je obyčajný komentár, ak sa nachádza v správnej úvodnej pozícii. Release pipeline má zachovať effective frontend identity, pretože zmena frontendu môže zmeniť parsing alebo build semantics bez zmeny aplikačného source-u.

## 2. `ARG` pred `FROM` a base image

Global build arguments možno deklarovať pred prvým `FROM` a použiť v base reference:

```dockerfile
ARG GO_IMAGE=golang:1.25-alpine@sha256:<build-base-digest>
ARG RUNTIME_IMAGE=gcr.io/distroless/static-debian12:nonroot@sha256:<runtime-base-digest>

FROM ${GO_IMAGE} AS source
```

Tag pomáha človeku rozpoznať verziu a variant. Digest určuje konkrétny manifest. Pipeline môže argument prepísať:

```bash
docker buildx build \
  --build-arg GO_IMAGE="registry.example.com/base/go@sha256:<digest>" \
  .
```

Review Dockerfile-u preto samo nepreukazuje, ktorý base image sa použil. Effective build arguments patria do provenance alebo build manifestu.

Global `ARG` má osobitný scope. Ak sa jeho hodnota potrebuje neskôr v stage-i, argument sa v stage-i znovu deklaruje.

## 3. `FROM` vytvára stage graph

Každý `FROM` začína nový stage. Stage môže mať meno:

```dockerfile
FROM ${GO_IMAGE} AS source
```

Neskorší stage môže kopírovať artifacts:

```dockerfile
COPY --from=build /out/payments-api /usr/local/bin/payments-api
```

Stage nie je automaticky vykonaný iba preto, že je v Dockerfile-i. BuildKit vykonáva graph potrebný pre zvolený target. Ak `test` a `build` sú sibling stages a final `runtime` závisí iba od `build`, build runtime targetu nemusí vykonať test stage.

```text
source
├── test
└── build
    └── runtime
```

Preto sa test target spúšťa samostatne alebo sa release graph navrhne tak, aby required artifact jednoznačne závisel od testovaného outputu.

## 4. `WORKDIR` vytvára stabilný build context vo stage-i

```dockerfile
WORKDIR /src
```

Nastaví working directory pre nasledujúce `RUN`, `COPY`, `CMD` a ďalšie instructions v danom stage-i. Ak path neexistuje, builder ho vytvorí.

Explicitný absolute path je čitateľnejší než séria `RUN cd /src && ...`. Stav working directory sa stáva súčasťou stage semantics.

Vo final image-i môže byť iný working directory:

```dockerfile
WORKDIR /home/nonroot
```

Runtime aplikácia potom nemá náhodne závisieť od `/src`, ktorý vo final stage-i vôbec nemusí existovať.

## 5. `COPY` a build context

`COPY` načíta files z build contextu alebo named contextu a pridá ich do stage filesystemu.

```dockerfile
COPY go.mod go.sum ./
```

Source paths sa interpretujú voči rootu build contextu, nie voči umiestneniu Dockerfile-u podľa ľudskej intuície. Files vylúčené `.dockerignore` nie sú dostupné pre bežné `COPY` z primary contextu.

Neskôr:

```dockerfile
COPY cmd ./cmd
```

Oddeľuje dependency metadata od application source-u a zlepšuje cache reuse.

`COPY --chown` nastaví ownership počas pridania súboru:

```dockerfile
COPY --from=build --chown=65532:65532 \
  /out/payments-api \
  /usr/local/bin/payments-api
```

To je lepšie než samostatný `RUN chown`, ktorý vytvára ďalší filesystem changeset a môže dočasne ukladať nesprávne ownership metadata.

## 6. `ADD` používaj iba pri potrebnej semantics

`ADD` má širšie správanie než `COPY`, napríklad automatické rozbalenie lokálnych tar archives a podľa syntax verzie podporu ďalších source typov. Táto pohodlnosť môže zakryť, čo build robí.

Pre obyčajné local files používaj `COPY`. `ADD` má zmysel, keď explicitne potrebuješ jeho semantics a vieš ju vysvetliť.

Remote download je často lepšie vykonať cez `RUN` s checksum verifikáciou, aby bol network a integrity contract viditeľný:

```dockerfile
ARG TOOL_SHA256
RUN wget -O /tmp/tool.tgz https://example.invalid/tool.tgz \
    && echo "$TOOL_SHA256  /tmp/tool.tgz" | sha256sum -c - \
    && tar -xzf /tmp/tool.tgz -C /usr/local/bin \
    && rm /tmp/tool.tgz
```

## 7. `RUN` mení build filesystem

Shell form:

```dockerfile
RUN go test ./...
```

na Linux stage-i typicky používa shell. Exec form umožňuje explicitnejšiu argv semantics:

```dockerfile
RUN ["go", "test", "./..."]
```

Pri dlhších package install krokoch je dôležité spojiť update, install a cleanup do jedného instruction, aby cache nepoužila stale repository metadata a temporary files nezostali v layer.

Debian-like príklad:

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
```

Alpine:

```dockerfile
RUN apk add --no-cache ca-certificates
```

Package install stále závisí od repository generation. Reprodukovateľnosť potrebuje pinned package alebo snapshot repository podľa požadovanej úrovne assurance.

## 8. BuildKit mounts

Cache mount zrýchľuje dependency a compiler cache bez automatického pridania cache obsahu do final layer:

```dockerfile
RUN --mount=type=cache,target=/go/pkg/mod,sharing=locked \
    --mount=type=cache,target=/root/.cache/go-build,sharing=locked \
    go test ./...
```

Build musí fungovať aj s prázdnou cache. Cache nie je deklarovaný source artifact ani correctness authority.

Secret mount:

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci
```

SSH mount môže dočasne forwardovať SSH agent pre private repository access. Každý takýto mount rozširuje build trust boundary a musí byť povolený iba trusted jobom.

## 9. `ARG` a `ENV` majú odlišný lifecycle

`ARG` je build-time input. Nie je automaticky runtime environment, hoci jeho hodnota sa môže dostať do layer history, commands alebo explicitného `ENV`.

```dockerfile
ARG VERSION
ARG VCS_REF
```

`ENV` zapisuje default do image configu:

```dockerfile
ENV LISTEN_ADDRESS=:8080 \
    LOG_LEVEL=info
```

Runtime môže `ENV` prepísať:

```bash
docker run --env LOG_LEVEL=debug IMAGE
```

Secrets sa nemajú ukladať do `ARG` alebo `ENV`, pretože môžu byť viditeľné v image metadata, history alebo runtime inspect.

## 10. Build metadata cez `LABEL`

OCI annotations môžu niesť source, version a revision metadata:

```dockerfile
ARG VERSION
ARG VCS_REF

LABEL org.opencontainers.image.title="Atlas Payments API" \
      org.opencontainers.image.version="$VERSION" \
      org.opencontainers.image.revision="$VCS_REF" \
      org.opencontainers.image.source="https://github.com/example/atlas-payments"
```

Keďže `ARG` scope sa resetuje pri novom `FROM`, `VERSION` a `VCS_REF` sa musia vo final stage-i znovu deklarovať.

Labels sú metadata, nie cryptographic provenance. Hodnota revision môže byť nesprávna, ak ju producer dodal ručne. Trusted pipeline ju získava z checkout state-u a viaže na build evidence.

## 11. `USER` ako runtime default

```dockerfile
USER 65532:65532
```

nastaví default usera pre nasledujúce build instructions a runtime process podľa pozície. Vo final stage-i ho zvyčajne nastavíme až po skopírovaní binary a príprave filesystem permissions.

Numeric UID/GID funguje aj bez `/etc/passwd`. Aplikácia však môže očakávať home directory alebo username lookup; minimal image contract treba otestovať.

Runtime môže usera prepísať, preto audit číta image aj container:

```bash
docker image inspect IMAGE --format '{{.Config.User}}'
docker inspect CONTAINER --format '{{.Config.User}}'
```

## 12. `EXPOSE` je metadata

```dockerfile
EXPOSE 8080
```

hovorí, že aplikácia očakáva traffic na porte `8080`. Nevytvára host listener ani firewall rule.

Host publishing sa nastaví runtime:

```bash
docker run -p 127.0.0.1:18080:8080 IMAGE
```

Aplikácia zároveň musí na `8080` skutočne počúvať na vhodnej adrese. `EXPOSE` nemá enforcement ani health semantics.

## 13. `HEALTHCHECK`

Image môže definovať default healthcheck:

```dockerfile
HEALTHCHECK \
  --interval=10s \
  --timeout=3s \
  --start-period=5s \
  --retries=3 \
  CMD ["/usr/local/bin/payments-api", "healthcheck"]
```

Exec form nevyžaduje shell. Application binary môže zavolať local readiness endpoint a vrátiť non-zero exit code pri chybe.

Healthcheck by mal byť krátky, deterministic a bezpečný pri opakovaní. Nemá vykonávať drahú business transakciu ani meniť state bez idempotency.

Runtime alebo Compose môže image healthcheck prepísať alebo vypnúť. Image definition preto nie je effective proof.

## 14. `ENTRYPOINT` a `CMD`

Exec-form entrypoint:

```dockerfile
ENTRYPOINT ["/usr/local/bin/payments-api"]
CMD ["serve"]
```

vytvorí default argv:

```text
/usr/local/bin/payments-api serve
```

Pri `docker run IMAGE version` runtime arguments nahradia `CMD`:

```text
/usr/local/bin/payments-api version
```

`--entrypoint` môže prepísať aj entrypoint.

Shell form:

```dockerfile
ENTRYPOINT /usr/local/bin/payments-api serve
```

typicky spustí shell ako PID 1. Signal forwarding a argument semantics sú menej priame. Pre jednu hlavnú aplikáciu je exec form bezpečnejšia a čitateľnejšia.

## 15. `STOPSIGNAL`

```dockerfile
STOPSIGNAL SIGTERM
```

určuje default signal použitý pri stop lifecycle. Aplikácia ho musí spracovať. Samotná deklarácia negarantuje graceful shutdown.

Test:

```bash
docker stop --time 15 payments-api
docker inspect payments-api \
  --format 'exit={{.State.ExitCode}} finished={{.State.FinishedAt}}'
```

Aplikačný acceptance test má navyše overiť, že in-flight operácia nezostala v nekonzistentnom stave.

## 16. Kompletný multi-stage Dockerfile

```dockerfile
# syntax=docker/dockerfile:1

ARG GO_IMAGE=golang:1.25-alpine@sha256:<build-base-digest>
ARG RUNTIME_IMAGE=gcr.io/distroless/static-debian12:nonroot@sha256:<runtime-base-digest>

FROM ${GO_IMAGE} AS source
WORKDIR /src

COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod,sharing=locked \
    go mod download

COPY cmd ./cmd

FROM source AS test
RUN --mount=type=cache,target=/go/pkg/mod,sharing=locked \
    --mount=type=cache,target=/root/.cache/go-build,sharing=locked \
    go test ./...

FROM source AS build
ARG TARGETOS
ARG TARGETARCH
ARG VERSION
ARG VCS_REF

RUN --mount=type=cache,target=/go/pkg/mod,sharing=locked \
    --mount=type=cache,target=/root/.cache/go-build,sharing=locked \
    CGO_ENABLED=0 GOOS="$TARGETOS" GOARCH="$TARGETARCH" \
    go build \
      -trimpath \
      -ldflags="-s -w -X main.version=$VERSION -X main.commit=$VCS_REF" \
      -o /out/payments-api \
      ./cmd/payments-api

FROM ${RUNTIME_IMAGE} AS runtime
ARG VERSION
ARG VCS_REF

LABEL org.opencontainers.image.title="Atlas Payments API" \
      org.opencontainers.image.version="$VERSION" \
      org.opencontainers.image.revision="$VCS_REF"

WORKDIR /home/nonroot
COPY --from=build --chown=65532:65532 \
  /out/payments-api \
  /usr/local/bin/payments-api

USER 65532:65532
ENV LISTEN_ADDRESS=:8080 \
    DATA_PATH=/var/lib/atlas-payments/payments.jsonl

EXPOSE 8080
STOPSIGNAL SIGTERM

HEALTHCHECK \
  --interval=10s \
  --timeout=3s \
  --start-period=5s \
  --retries=3 \
  CMD ["/usr/local/bin/payments-api", "healthcheck"]

ENTRYPOINT ["/usr/local/bin/payments-api"]
CMD ["serve"]
```

Tento Dockerfile vytvára úzky runtime image, ale sám nepreukazuje, že `test` stage bol vykonaný, že digest-pinned bases existujú, že runtime volume má správny ownership ani že host publishing funguje.

## 17. Lint, build a inspect

Static kontrola môže zachytiť syntax a vybrané best practices:

```bash
docker buildx build --check .
```

Podpora konkrétnych checks závisí od Buildx a frontendu.

Test target:

```bash
docker buildx build \
  --target test \
  --output=type=cacheonly \
  --progress=plain \
  .
```

Runtime image:

```bash
docker buildx build \
  --target runtime \
  --build-arg VERSION=1.0.0 \
  --build-arg VCS_REF="$(git rev-parse --short=12 HEAD)" \
  --tag atlas/payments-api:1.0.0 \
  --load \
  .
```

Inspect:

```bash
docker image inspect atlas/payments-api:1.0.0 \
  --format '{{json .Config}}' | jq .
```

Každý krok má inú hranicu: check je static, test target vykoná konkrétny graph, runtime build vytvorí image a inspect číta final metadata. Ani jeden sám nepreukazuje production behavior.

## 18. Incident: test stage existoval, ale nikdy nebežal

Team pridal `FROM source AS test` a `RUN go test ./...`. CI však buildovala iba final runtime target:

```bash
docker buildx build --target runtime --push .
```

Keďže runtime stage závisel od `build`, nie od sibling `test`, BuildKit test stage nevykonal. Pipeline bola zelená a image obsahoval regression.

Oprava pridala samostatný required test build s `--target test` a uložila subject identity source-u, Dockerfile-u, base images a buildera. Release build sa spustil iba po PASS rovnakého input subjectu.

## 19. Incident: `false` configuration sa zmenila na default

Entrypoint wrapper používal shell expansion:

```sh
LEGACY_ENABLED="${LEGACY_ENABLED:-true}"
```

V deployment-e bola premenná explicitne prázdna alebo nesprávne serializovaná. Shell použil `true`, hoci owner očakával disabled behavior.

Dockerfile a runtime configuration začali rozlišovať missing, empty a explicitnú hodnotu. Application parser validoval iba `true` alebo `false` a `/version` publikoval loaded configuration generation bez secretov.

## Čo si z kapitoly odniesť

Dockerfile je build program a stage graph. `FROM`, `COPY` a `RUN` tvoria filesystem a build dependencies. `USER`, `ENV`, `ENTRYPOINT`, `CMD`, `HEALTHCHECK` a labels zapisujú runtime defaults a metadata.

Poradie instructions ovplyvňuje cache. `ARG` a `ENV` majú iný lifecycle. `EXPOSE` nepublikuje port a healthcheck nie je business acceptance. Multi-stage Dockerfile môže obsahovať test stage, ktorý final target nevykoná. Preto sa build graph, final image config a runtime behavior overujú samostatne.

## Primárne zdroje

- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Dockerfile best practices](https://docs.docker.com/build/building/best-practices/)
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Build secrets](https://docs.docker.com/build/building/secrets/)
- [Build checks](https://docs.docker.com/build/checks/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Docker architecture](docker-architecture.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Build context a layer cache →](build-context-layer-cache.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
