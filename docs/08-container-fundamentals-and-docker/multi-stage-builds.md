# Multi-stage builds

Multi-stage build umožňuje použiť jeden Dockerfile na viac oddelených prostredí. Build stage môže obsahovať compiler, package manager, test tools a source code. Final runtime stage môže dostať iba výsledný binary, certificate bundle alebo ďalšie úzko vybrané artifacts.

Hlavný prínos nie je iba menší image. Stage graph oddeľuje zodpovednosti a trust boundaries. Test environment nemusí byť production runtime. Debug tools nemusia byť v release image-i. Build secrets alebo private dependencies sa nemajú preniesť do final stage-u. Zároveň však multi-stage syntax sama nezaručuje, že testy prebehli alebo že final artifact pochádza z testovaného graphu.

Budeme skladať `payments-api` cez stages `source`, `test`, `build`, `debug` a `runtime`.

## 1. Každý `FROM` začína nový stage

```dockerfile
FROM golang:1.25-alpine AS source
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY cmd ./cmd
```

Stage `source` obsahuje toolchain, dependencies a source. Nasledujúce stages môžu z neho dediť:

```dockerfile
FROM source AS test
RUN go test ./...

FROM source AS build
RUN CGO_ENABLED=0 go build -o /out/payments-api ./cmd/payments-api
```

Oba stages majú spoločného parenta, ale jeden nie je automaticky závislý od druhého.

```text
source
├── test
└── build
```

Ak final stage kopíruje iba z `build`, target `runtime` nemusí nikdy vykonať `test`.

## 2. Stage graph nie je lineárny shell script

Dockerfile sa číta zhora nadol, ale BuildKit odvodí graph dependencies. Pri príkaze:

```bash
docker buildx build --target runtime .
```

vykoná iba stages a nodes potrebné pre `runtime`. Sibling `test` môže zostať nevykonaný.

Preto má CI explicitný test verdict:

```bash
docker buildx build \
  --target test \
  --output=type=cacheonly \
  --progress=plain \
  .
```

A samostatný runtime build:

```bash
docker buildx build \
  --target runtime \
  --tag atlas/payments-api:1.0.0 \
  --load \
  .
```

Oba buildy musia používať rovnaký source, Dockerfile, bases, build args a relevantný builder trust domain. Inak PASS test targetu nemusí patriť artifactu, ktorý sa publikuje.

## 3. Prenos artifacts cez `COPY --from`

Final stage nezačne ako continuation build stage-u. Má vlastný base image a dostane iba explicitne skopírované paths:

```dockerfile
FROM gcr.io/distroless/static-debian12:nonroot AS runtime

COPY --from=build --chown=65532:65532 \
  /out/payments-api \
  /usr/local/bin/payments-api
```

Compiler, source tree a Go module cache zostanú mimo final runtime filesystemu. To znižuje image size a post-compromise tool surface.

Prenos však musí zachovať všetky runtime dependencies. Pri statickom Go binary môže stačiť jeden súbor. Dynamicky linkovaný binary potrebuje loader a shared libraries. Chýbajúca dependency sa často prejaví ako `no such file or directory`, hoci executable path existuje.

Debug stage môže skontrolovať binary:

```dockerfile
FROM alpine:3.22 AS inspect
COPY --from=build /out/payments-api /tmp/payments-api
RUN file /tmp/payments-api \
    && ldd /tmp/payments-api || true
```

`ldd` nad nedôveryhodným binary môže mať bezpečnostné riziká podľa implementácie. V trusted build-e používaj vhodné static inspection tools.

## 4. Build stage a runtime stage majú iné security požiadavky

Build stage potrebuje compiler, package repositories a často širší network access. Runtime stage má byť úzky a bez build credentials.

```text
build stage
→ source, compiler, dependency access, cache, tests

runtime stage
→ binary, runtime libraries, non-root user, metadata
```

Secret mount v build stage-i sa nesmie skopírovať do `/out`. Final stage síce nemá priamy prístup k build secret mountu, ale build script môže secret vložiť do binary, configu alebo generated file-u. Multi-stage boundary preto znižuje accidental inclusion, nie malicious producer risk.

## 5. Použitie externého image alebo contextu ako source

`COPY --from` nemusí odkazovať iba na stage name. Môže použiť image reference:

```dockerfile
COPY --from=busybox:1.36.1@sha256:<digest> \
  /bin/busybox \
  /usr/local/bin/busybox
```

Takýto source je ďalší supply-chain input a má byť digest-pinned.

Named context možno pomenovať podobne:

```bash
docker buildx build \
  --build-context company_certs=./certs \
  .
```

Dockerfile:

```dockerfile
COPY --from=company_certs /ca.pem /etc/ssl/certs/company-ca.pem
```

Stage, image source a named context môžu mať kolidujúce mená. Naming má byť jednoznačný a review musí vedieť, odkiaľ artifact pochádza.

## 6. Debug stage bez znečistenia production image-u

Production distroless image nemá shell, `curl`, `ss` ani package manager. To je často správne. Pre local debugging možno vytvoriť samostatný target:

```dockerfile
FROM alpine:3.22 AS debug
RUN apk add --no-cache ca-certificates curl bind-tools iproute2
COPY --from=build /out/payments-api /usr/local/bin/payments-api
ENTRYPOINT ["/usr/local/bin/payments-api"]
CMD ["serve"]
```

Build:

```bash
docker buildx build --target debug -t atlas/payments-api:debug --load .
```

Release pipeline publikuje iba `runtime` target. Debug image má iný digest, package inventory a security posture. Nesmie byť omylom promovovaný do production pod rovnakým tagom.

## 7. Artifact stage pre CI output

Niekedy chceme z build graphu exportovať binary alebo test report bez vytvorenia runtime image-u.

```dockerfile
FROM scratch AS artifact
COPY --from=build /out/payments-api /payments-api
```

Export:

```bash
docker buildx build \
  --target artifact \
  --output type=local,dest=./dist \
  .
```

`./dist/payments-api` vznikne na client side podľa exporter semantics. Tento artifact musí byť viazaný na rovnaký build subject ako final image. Ak pipeline buildne binary samostatne a runtime image neskôr znovu kompiluje, vznikajú dva artifacty s potenciálne odlišnými inputs.

## 8. Build once a prenes presný output

Dôveryhodnejší model je kompilovať jeden output a použiť ho pre testovanie aj final image, pokiaľ test typ dovoľuje.

```text
source
→ compile artifact A
→ static alebo artifact test nad A
→ COPY A do runtime
→ publish image obsahujúci A
```

Unit testy nad source graphom môžu stále bežať samostatne. Dôležité je, aby release image neobsahoval binary vytvorený iným neskorším buildom bez rovnakej evidence.

Pri Go možno vytvoriť build stage a testovať binary v integration stage:

```dockerfile
FROM build AS smoke
RUN /out/payments-api version
```

Final runtime kopíruje rovnaký `/out/payments-api` z `build`.

## 9. Platform-specific stages

BuildKit poskytuje automatic platform args ako `BUILDPLATFORM`, `TARGETPLATFORM`, `TARGETOS` a `TARGETARCH` v podporovanom kontexte.

```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.25-alpine AS build
ARG TARGETOS
ARG TARGETARCH

RUN CGO_ENABLED=0 \
    GOOS="$TARGETOS" \
    GOARCH="$TARGETARCH" \
    go build -o /out/payments-api ./cmd/payments-api
```

Compiler beží na build platforme a vytvára target binary. Final stage sa vytvára pre target platformu.

Pri CGO alebo native libraries môže cross-compilation vyžadovať cross toolchain alebo native build node. Platform label v manifest-e nesmie byť iba deklarácia; binary a libraries musia byť s platformou kompatibilné.

## 10. Stage pinning a update lifecycle

Každý `FROM` je build input. Build a runtime bases môžu mať odlišný update cadence.

```dockerfile
ARG GO_IMAGE=golang:1.25-alpine@sha256:<go-digest>
ARG RUNTIME_IMAGE=gcr.io/distroless/static-debian12:nonroot@sha256:<runtime-digest>
```

Zmena build base môže zmeniť compiler output bez zmeny runtime packages. Zmena runtime base môže opraviť certificate bundle alebo libc bez zmeny binary. Obe zmeny vytvárajú nový application image digest a potrebujú testy.

## 11. Stage-specific cache

Stages môžu zdieľať parent cache. `test` a `build` reuse-nu dependency download a source copy, ale majú samostatné downstream nodes.

```text
source dependencies → cached raz
├── test command result
└── build command result
```

To zrýchľuje CI. Zároveň nesmie byť test PASS odvodený iba z cached resultu vytvoreného nedôveryhodným jobom. Cache producer trust a subject identity zostávajú relevantné.

## 12. Target selection v development a CI

Jeden Dockerfile môže podporovať viac účelov:

```text
test
→ CI unit test verdict

debug
→ local interactive diagnosis

artifact
→ binary export

runtime
→ production image
```

Každý pipeline job musí explicitne uviesť target. Default posledný stage môže byť zmenený pri refactore a ticho zmeniť output, ak automation používa iba `docker build .`.

```bash
docker buildx build --target runtime .
```

je čitateľnejší release contract.

## 13. Incident: production dostala debug image

Team pridal `debug` stage za `runtime` a lokálne build commands nepoužívali `--target`. Posledný stage sa stal default outputom. CI pushla image s shellom, package managerom a network tools.

```text
Dockerfile refactor
→ debug stage je posledný
→ implicitný default target sa zmení
→ release image obsahuje debug packages
```

Image fungoval a testy prešli, preto si nikto okamžite nevšimol širší attack surface.

Oprava nastavila explicitný `--target runtime`, policy skontrolovala final image user a package inventory a debug publication používala samostatné repository a retention.

## 14. Incident: final binary nebol ten, ktorý prešiel testom

Pipeline spustila `--target test` nad commitom C1. Medzi jobmi sa mutable branch ref posunul na C2. Runtime build checkoutol branch znova a vytvoril image z C2.

```text
test subject C1 → PASS
runtime subject C2 → publish
```

Multi-stage Dockerfile bol správny, ale pipeline subject nebol immutable. Oprava používala exact commit SHA a odovzdávala source a Dockerfile digest medzi jobs. Final image labels a provenance uvádzali C1/C2 mismatch a policy publication odmietla.

## 15. Incident: minimal runtime nemal CA certificates

Statický Go binary úspešne štartoval v `scratch` image-i. HTTPS call na payment provider však zlyhal, pretože image nemal CA certificate bundle.

```text
binary je statický
→ process start prejde
→ DNS a TCP prejdú
→ TLS trust store chýba
→ x509 unknown authority
```

Oprava skopírovala certificate bundle z trusted stage-u alebo použila distroless static image s potrebným runtime contentom. Acceptance test zahŕňal outbound TLS k test endpointu, nie iba local `/healthz`.

## 16. Praktický graph pre `payments-api`

```dockerfile
# syntax=docker/dockerfile:1

FROM golang:1.25-alpine@sha256:<digest> AS source
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod,sharing=locked go mod download
COPY cmd ./cmd

FROM source AS test
RUN --mount=type=cache,target=/go/pkg/mod,sharing=locked \
    --mount=type=cache,target=/root/.cache/go-build,sharing=locked \
    go test ./...

FROM source AS build
ARG TARGETOS
ARG TARGETARCH
RUN --mount=type=cache,target=/go/pkg/mod,sharing=locked \
    --mount=type=cache,target=/root/.cache/go-build,sharing=locked \
    CGO_ENABLED=0 GOOS="$TARGETOS" GOARCH="$TARGETARCH" \
    go build -trimpath -o /out/payments-api ./cmd/payments-api

FROM alpine:3.22 AS debug
RUN apk add --no-cache ca-certificates curl iproute2
COPY --from=build /out/payments-api /usr/local/bin/payments-api
ENTRYPOINT ["/usr/local/bin/payments-api"]
CMD ["serve"]

FROM gcr.io/distroless/static-debian12:nonroot@sha256:<digest> AS runtime
COPY --from=build --chown=65532:65532 \
  /out/payments-api /usr/local/bin/payments-api
USER 65532:65532
ENTRYPOINT ["/usr/local/bin/payments-api"]
CMD ["serve"]
```

Graph je jasný, ale pipeline musí stále explicitne vykonať `test` a publikovať `runtime`.

## Čo si z kapitoly odniesť

Multi-stage build oddeľuje build, test, debug, artifact a runtime prostredia. Final image dostane iba artifacts explicitne prenesené cez `COPY --from`. To znižuje size a runtime tool surface.

Stages tvoria graph, nie povinnú lineárnu sekvenciu. Sibling test stage sa pri runtime targete nemusí vykonať. Target má byť v automation explicitný. Build a runtime bases, platform args, cache a artifact transfer patria do release identity. Minimal image musí stále obsahovať všetky runtime dependencies a testovaný binary musí byť ten istý artifact, ktorý sa publikuje.

## Primárne zdroje

- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Multi-platform builds](https://docs.docker.com/build/building/multi-platform/)
- [Build exporters](https://docs.docker.com/build/exporters/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Build context a layer cache](build-context-layer-cache.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Volumes a bind mounts →](volumes-bind-mounts.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
