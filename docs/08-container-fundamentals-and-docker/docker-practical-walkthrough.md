# Praktický Docker projekt od prázdneho adresára po overený Compose runtime

Predchádzajúce kapitoly rozdelili Docker na samostatné mechanizmy: build context, Dockerfile graph, image layers, registry digest, container create configuration, namespaces, volumes, networks, environment a health. V tejto kapitole ich spojíme do jedného projektu a budeme sledovať, ako sa obyčajný source tree postupne mení na testovaný image a napokon na overenú Compose application.

Cieľom nie je vytvoriť produkčný payment systém. Potrebujeme malú aplikáciu s dostatočne bohatým runtime contractom, aby sme mohli pozorovať všetky podstatné Docker hranice. `payments-api` preto poskytne health, readiness a version endpoint, prijme jednoduchý payment záznam a uloží ho do súboru. Súbor nám umožní overiť volume persistence. Version endpoint ukáže, ktorý build a configuration generation process skutočne načítal. Readiness skontroluje, či je data path zapisovateľný.

Na konci nebudeme mať iba zelený `docker compose up`. Budeme vedieť preukázať, ktorý source a Dockerfile vytvorili image, či sa test stage skutočne vykonal, aký user a command sú v image-i, akú effective konfiguráciu dostal container, či funguje local health, service DNS aj host port, či business údaj prežije recreate a ako sa diagnostikuje zámerne vložená network a volume chyba.

## 1. Pracovný adresár

Vytvor nový projekt:

```bash
mkdir -p atlas-payments-docker/cmd/payments-api
cd atlas-payments-docker
```

Budeme postupne vytvárať túto štruktúru:

```text
atlas-payments-docker/
├── .dockerignore
├── Dockerfile
├── compose.yaml
├── compose.broken-bind.yaml
├── env.example
├── go.mod
└── cmd/
    └── payments-api/
        ├── main.go
        └── main_test.go
```

V tejto chvíli neexistuje image ani container. Existuje iba source tree. Image vznikne až z konkrétneho build contextu, Dockerfile-u, base images, build arguments, buildera a platformy. Container neskôr pridá ďalšiu vrstvu vstupov: environment, mounts, network, ports, limits a security options.

## 2. Minimálna aplikácia

Vytvor `go.mod`:

```go
module example.com/atlas/payments-api

go 1.25
```

Module file je build input. Go verzia vyjadruje očakávané language a module semantics, ale konkrétny compiler image určí až Dockerfile.

Teraz vytvor `cmd/payments-api/main.go`:

```go
package main

import (
    "bufio"
    "context"
    "encoding/json"
    "errors"
    "fmt"
    "log"
    "net/http"
    "os"
    "os/signal"
    "path/filepath"
    "strings"
    "syscall"
    "time"
)

var (
    version = "dev"
    commit  = "unknown"
)

type application struct {
    dataPath         string
    configGeneration string
}

type payment struct {
    ID       string `json:"id"`
    Amount   int64  `json:"amount"`
    Currency string `json:"currency"`
}

func environment(name, fallback string) string {
    value := strings.TrimSpace(os.Getenv(name))
    if value == "" {
        return fallback
    }
    return value
}

func (app application) ensureWritableDataPath() error {
    directory := filepath.Dir(app.dataPath)
    if err := os.MkdirAll(directory, 0o750); err != nil {
        return fmt.Errorf("create data directory: %w", err)
    }

    file, err := os.OpenFile(app.dataPath, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o640)
    if err != nil {
        return fmt.Errorf("open data file: %w", err)
    }
    return file.Close()
}

func (app application) appendPayment(value payment) error {
    value.ID = strings.TrimSpace(value.ID)
    value.Currency = strings.ToUpper(strings.TrimSpace(value.Currency))

    if value.ID == "" {
        return errors.New("payment id is required")
    }
    if value.Amount <= 0 {
        return errors.New("payment amount must be positive")
    }
    if len(value.Currency) != 3 {
        return errors.New("currency must use a three-letter code")
    }

    file, err := os.OpenFile(app.dataPath, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o640)
    if err != nil {
        return fmt.Errorf("open data file: %w", err)
    }
    defer file.Close()

    if err := json.NewEncoder(file).Encode(value); err != nil {
        return fmt.Errorf("append payment: %w", err)
    }
    if err := file.Sync(); err != nil {
        return fmt.Errorf("sync payment data: %w", err)
    }
    return nil
}

func (app application) findPayment(id string) (payment, bool, error) {
    file, err := os.Open(app.dataPath)
    if errors.Is(err, os.ErrNotExist) {
        return payment{}, false, nil
    }
    if err != nil {
        return payment{}, false, fmt.Errorf("open data file: %w", err)
    }
    defer file.Close()

    scanner := bufio.NewScanner(file)
    for scanner.Scan() {
        var value payment
        if err := json.Unmarshal(scanner.Bytes(), &value); err != nil {
            return payment{}, false, fmt.Errorf("decode persisted payment: %w", err)
        }
        if value.ID == id {
            return value, true, nil
        }
    }
    if err := scanner.Err(); err != nil {
        return payment{}, false, fmt.Errorf("scan data file: %w", err)
    }
    return payment{}, false, nil
}

func writeJSON(writer http.ResponseWriter, status int, value any) {
    writer.Header().Set("Content-Type", "application/json")
    writer.WriteHeader(status)
    _ = json.NewEncoder(writer).Encode(value)
}

func (app application) routes() http.Handler {
    mux := http.NewServeMux()

    mux.HandleFunc("GET /healthz", func(writer http.ResponseWriter, _ *http.Request) {
        writeJSON(writer, http.StatusOK, map[string]string{"status": "alive"})
    })

    mux.HandleFunc("GET /readyz", func(writer http.ResponseWriter, _ *http.Request) {
        if err := app.ensureWritableDataPath(); err != nil {
            writeJSON(writer, http.StatusServiceUnavailable, map[string]string{
                "status": "not-ready",
                "error":  err.Error(),
            })
            return
        }
        writeJSON(writer, http.StatusOK, map[string]string{"status": "ready"})
    })

    mux.HandleFunc("GET /version", func(writer http.ResponseWriter, _ *http.Request) {
        writeJSON(writer, http.StatusOK, map[string]string{
            "service":           "payments-api",
            "version":           version,
            "commit":            commit,
            "config_generation": app.configGeneration,
        })
    })

    mux.HandleFunc("POST /payments", func(writer http.ResponseWriter, request *http.Request) {
        defer request.Body.Close()

        var value payment
        decoder := json.NewDecoder(http.MaxBytesReader(writer, request.Body, 1<<20))
        decoder.DisallowUnknownFields()
        if err := decoder.Decode(&value); err != nil {
            writeJSON(writer, http.StatusBadRequest, map[string]string{"error": err.Error()})
            return
        }
        if err := app.appendPayment(value); err != nil {
            writeJSON(writer, http.StatusBadRequest, map[string]string{"error": err.Error()})
            return
        }
        writeJSON(writer, http.StatusCreated, value)
    })

    mux.HandleFunc("GET /payments/{id}", func(writer http.ResponseWriter, request *http.Request) {
        value, found, err := app.findPayment(request.PathValue("id"))
        if err != nil {
            writeJSON(writer, http.StatusInternalServerError, map[string]string{"error": err.Error()})
            return
        }
        if !found {
            writeJSON(writer, http.StatusNotFound, map[string]string{"error": "payment not found"})
            return
        }
        writeJSON(writer, http.StatusOK, value)
    })

    return mux
}

func healthcheck() error {
    url := environment("HEALTHCHECK_URL", "http://127.0.0.1:8080/readyz")
    client := http.Client{Timeout: 2 * time.Second}

    response, err := client.Get(url)
    if err != nil {
        return fmt.Errorf("health request: %w", err)
    }
    defer response.Body.Close()

    if response.StatusCode != http.StatusOK {
        return fmt.Errorf("health status: %s", response.Status)
    }
    return nil
}

func serve() error {
    app := application{
        dataPath:         environment("DATA_PATH", "/var/lib/atlas-payments/payments.jsonl"),
        configGeneration: environment("CONFIG_GENERATION", "local-default"),
    }

    server := &http.Server{
        Addr:              environment("LISTEN_ADDRESS", ":8080"),
        Handler:           app.routes(),
        ReadHeaderTimeout: 5 * time.Second,
        ReadTimeout:       10 * time.Second,
        WriteTimeout:      10 * time.Second,
        IdleTimeout:       60 * time.Second,
    }

    signals := make(chan os.Signal, 1)
    signal.Notify(signals, syscall.SIGINT, syscall.SIGTERM)

    go func() {
        <-signals
        context, cancel := context.WithTimeout(context.Background(), 10*time.Second)
        defer cancel()
        if err := server.Shutdown(context); err != nil {
            log.Printf("graceful shutdown failed: %v", err)
        }
    }()

    log.Printf(
        "starting service=payments-api version=%s commit=%s config_generation=%s address=%s",
        version,
        commit,
        app.configGeneration,
        server.Addr,
    )

    err := server.ListenAndServe()
    if errors.Is(err, http.ErrServerClosed) {
        return nil
    }
    return err
}

func main() {
    command := "serve"
    if len(os.Args) > 1 {
        command = os.Args[1]
    }

    var err error
    switch command {
    case "serve":
        err = serve()
    case "healthcheck":
        err = healthcheck()
    case "version":
        fmt.Printf("service=payments-api version=%s commit=%s\n", version, commit)
    default:
        err = fmt.Errorf("unknown command %q", command)
    }

    if err != nil {
        log.Fatal(err)
    }
}
```

Aplikácia vedome obsahuje viac runtime vlastností. Hlavný process zostáva v foregrounde a priamo spracuje `SIGTERM`, takže je vhodný ako PID 1. Healthcheck používa rovnaký binary; final image nepotrebuje shell ani `curl`. Readiness skutočne otvorí data file, takže odhalí volume permission problém, ktorý obyčajný process health nevidí. `file.Sync()` dáva lepšiu durability hranicu než samotný buffered encode, hoci konečný outcome stále závisí od filesystemu a storage backendu.

## 3. Test pred containerizáciou

Vytvor `cmd/payments-api/main_test.go`:

```go
package main

import (
    "path/filepath"
    "testing"
)

func TestPaymentRoundTrip(t *testing.T) {
    app := application{
        dataPath:         filepath.Join(t.TempDir(), "payments.jsonl"),
        configGeneration: "test",
    }

    expected := payment{
        ID:       "pay-100",
        Amount:   1250,
        Currency: "eur",
    }

    if err := app.appendPayment(expected); err != nil {
        t.Fatalf("append payment: %v", err)
    }

    actual, found, err := app.findPayment("pay-100")
    if err != nil {
        t.Fatalf("find payment: %v", err)
    }
    if !found {
        t.Fatal("payment was not found")
    }
    if actual.ID != "pay-100" || actual.Amount != 1250 || actual.Currency != "EUR" {
        t.Fatalf("unexpected payment: %#v", actual)
    }
}

func TestRejectsNonPositiveAmount(t *testing.T) {
    app := application{
        dataPath: filepath.Join(t.TempDir(), "payments.jsonl"),
    }

    err := app.appendPayment(payment{
        ID:       "pay-invalid",
        Amount:   0,
        Currency: "EUR",
    })
    if err == nil {
        t.Fatal("expected non-positive amount to be rejected")
    }
}
```

Prvý test overuje persistovaný round trip, nie iba jednu helper funkciu. Druhý je forbidden-path test: neplatná suma nesmie byť zapísaná.

Ak máš lokálne Go 1.25, spusti:

```bash
gofmt -w cmd/payments-api/main.go cmd/payments-api/main_test.go
go test ./...
```

Očakávaný výsledok:

```text
ok  example.com/atlas/payments-api/cmd/payments-api
```

Tento test preukazuje aplikačnú logiku na hostiteľskom Go toolchaine. Neoveruje Docker build, final image, non-root permissions ani network path. Práve preto test neskôr zopakujeme v BuildKit stage-i.

## 4. Build context a `.dockerignore`

Vytvor `.dockerignore`:

```dockerignore
.git
.gitignore
.env
.env.*
!.env.example
coverage/
dist/
evidence/
backups/
tmp/
*.log
*.pem
*.key
compose.override.yaml
```

Build context má obsahovať source potrebný pre build, nie celý pracovný adresár. `.git`, runtime environment, evidence, backups a private keys do primary contextu nepatria. Ignore file znižuje transfer aj accidental cache invalidation.

Stále nejde o bezpečnostnú sandbox hranicu. Dockerfile môže používať sieť alebo secret mounts a build program môže vytvoriť citlivý output. `.dockerignore` rieši iba inventory primary context files.

## 5. Multi-stage Dockerfile

Vytvor `Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1

ARG GO_IMAGE=golang:1.25-alpine@sha256:<verified-build-base-digest>
ARG RUNTIME_IMAGE=gcr.io/distroless/static-debian12:nonroot@sha256:<verified-runtime-base-digest>

FROM ${GO_IMAGE} AS source
WORKDIR /src

COPY go.mod ./
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
    CGO_ENABLED=0 \
    GOOS="$TARGETOS" \
    GOARCH="$TARGETARCH" \
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
    DATA_PATH=/var/lib/atlas-payments/payments.jsonl \
    HEALTHCHECK_URL=http://127.0.0.1:8080/readyz

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

Stage `source` pripraví dependencies a source. `test` a `build` sú dve samostatné vetvy. `runtime` závisí iba od `build`, takže final build nemusí vykonať test stage. Toto je dôvod, prečo sa test target spustí explicitne.

Final stage obsahuje iba binary a runtime metadata. Build toolchain a source v ňom nie sú. `USER` nastaví non-root default. Exec-form `ENTRYPOINT` zabezpečí, že aplikácia bude PID 1 bez implicitného shellu. `EXPOSE` iba dokumentuje port; host publication vytvoríme až pri runtime.

Placeholder digesty musia byť nahradené reálnymi schválenými digestmi. Bez toho príklad nie je vykonateľný proti registry.

## 6. Builder a test graph

Vytvor pomenovaný builder:

```bash
docker buildx create \
  --name atlas-builder \
  --driver docker-container \
  --use

docker buildx inspect atlas-builder --bootstrap
```

Zachovaj jeho identity:

```bash
mkdir -p evidence
docker buildx inspect atlas-builder --bootstrap \
  > evidence/builder.txt
```

Spusti test target:

```bash
docker buildx build \
  --builder atlas-builder \
  --target test \
  --platform linux/amd64 \
  --progress=plain \
  --output=type=cacheonly \
  . 2>&1 | tee evidence/test-build.log
```

Exit code `0` znamená, že graph potrebný pre target `test` dokončil svoje commands. Neznamená, že runtime image existuje. Log zároveň ukáže, či boli nodes vykonané alebo cached.

Pre clean kontrolu:

```bash
docker buildx build \
  --builder atlas-builder \
  --no-cache \
  --target test \
  --platform linux/amd64 \
  --progress=plain \
  --output=type=cacheonly \
  .
```

No-cache run odhaľuje hidden dependency na instruction cache. Stále môže používať network dependencies a cache mounts podľa build modelu; úplne izolovaný clean-room test môže vyžadovať nový builder a oddelené cache namespaces.

## 7. Lokálny runtime image

Vytvor single-platform image a načítaj ho do local Engine-u:

```bash
VERSION=1.0.0
VCS_REF="$(git rev-parse --short=12 HEAD)"
IMAGE="atlas/payments-api:${VERSION}-local"

docker buildx build \
  --builder atlas-builder \
  --target runtime \
  --platform linux/amd64 \
  --build-arg VERSION="$VERSION" \
  --build-arg VCS_REF="$VCS_REF" \
  --tag "$IMAGE" \
  --load \
  .
```

`--load` je vhodný pre local single-platform test. Nie je to production registry publication.

Image metadata:

```bash
docker image inspect "$IMAGE" > evidence/image-inspect.json

jq '.[0].Config | {
  User,
  Entrypoint,
  Cmd,
  Env,
  WorkingDir,
  ExposedPorts,
  Healthcheck,
  Labels
}' evidence/image-inspect.json
```

Očakávame non-root usera, binary entrypoint, command `serve`, port `8080`, healthcheck a build labels. Inspect dokazuje image config, nie effective container overrides.

Spusti version command bez servera:

```bash
docker run --rm "$IMAGE" version
```

Očakávaný výstup obsahuje `version=1.0.0` a aktuálny commit. Tým overíme, že build arguments vstúpili do binary. Stále sme netestovali server, volume ani port.

## 8. Image filesystem

Vytvor dočasný container bez štartu:

```bash
image_container="$(docker create "$IMAGE")"
docker export "$image_container" | tar -tf - \
  > evidence/rootfs-files.txt
docker rm "$image_container"
```

Over binary path:

```bash
grep -Fx 'usr/local/bin/payments-api' evidence/rootfs-files.txt
```

Tento read-back dokazuje, že path je vo výslednom image filesysteme. Neoveruje executable architecture, dynamic loader, mount obscuring ani process permissions.

## 9. Network a volume pred containerom

Vytvor runtime resources:

```bash
docker network create atlas-payments-net
docker volume create atlas-payments-data
```

Priprav volume ownership pre UID `65532`:

```bash
docker run --rm \
  --user 0:0 \
  --mount type=volume,source=atlas-payments-data,target=/data \
  busybox:1.36.1@sha256:<verified-busybox-digest> \
  sh -ec 'mkdir -p /data && chown 65532:65532 /data && chmod 0750 /data'
```

Initializer je samostatná privileged operation. Application image zostáva non-root. V produkčnom modeli má initializer kontrolovať schema a ownership idempotentne, nie slepo vykonávať recursive chown nad neznámym datasetom.

## 10. Container najprv vytvor, až potom spusti

```bash
docker create \
  --name atlas-payments-api \
  --network atlas-payments-net \
  --user 65532:65532 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --cap-drop ALL \
  --security-opt no-new-privileges=true \
  --memory 256m \
  --cpus 0.50 \
  --pids-limit 128 \
  --mount type=volume,source=atlas-payments-data,target=/var/lib/atlas-payments \
  --publish 127.0.0.1:18080:8080 \
  --env CONFIG_GENERATION=manual-1 \
  "$IMAGE"
```

Container je v stave `created`. Pred process mutation skontroluj effective config:

```bash
docker inspect atlas-payments-api \
  > evidence/container-before-start.json

jq '.[0] | {
  Image,
  User: .Config.User,
  Entrypoint: .Config.Entrypoint,
  Cmd: .Config.Cmd,
  Env: .Config.Env,
  ReadonlyRootfs: .HostConfig.ReadonlyRootfs,
  CapDrop: .HostConfig.CapDrop,
  SecurityOpt: .HostConfig.SecurityOpt,
  Memory: .HostConfig.Memory,
  NanoCpus: .HostConfig.NanoCpus,
  PidsLimit: .HostConfig.PidsLimit,
  Mounts,
  Ports: .NetworkSettings.Ports
}' evidence/container-before-start.json
```

Takto oddelíme chybu v create configuration od chyby pri process štarte.

## 11. Start, health a PID 1

Spusti container:

```bash
docker start atlas-payments-api
```

Pozri process a logs:

```bash
docker ps --all --filter name=atlas-payments-api
docker logs --timestamps atlas-payments-api
docker top atlas-payments-api -eo pid,ppid,user,args
```

Aplikácia má byť hlavný PID 1 v namespace-e a bežať ako UID `65532`.

Počkaj na health:

```bash
for attempt in $(seq 1 30); do
  state="$(docker inspect atlas-payments-api --format '{{.State.Status}}')"
  health="$(docker inspect atlas-payments-api --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}')"
  printf 'attempt=%s state=%s health=%s\n' "$attempt" "$state" "$health"
  [ "$health" = healthy ] && break
  sleep 1
done
```

Health history:

```bash
docker inspect atlas-payments-api \
  --format '{{json .State.Health.Log}}' | jq .
```

Healthcheck volá local readiness endpoint. Preukazuje process, local network namespace a writable data path. Ešte nepreukazuje host publication ani service DNS.

## 12. Host-published path a loaded configuration

```bash
curl -fsS http://127.0.0.1:18080/version | jq .
```

Očakávané relevantné polia:

```json
{
  "service": "payments-api",
  "version": "1.0.0",
  "config_generation": "manual-1"
}
```

Tento request prešiel host loopbackom, Docker port publishing dataplane-om, container interface-om a application listenerom. `/version` navyše potvrdil loaded generation.

## 13. Business zápis do volume-u

```bash
curl -fsS \
  --request POST \
  --header 'Content-Type: application/json' \
  --data '{"id":"pay-100","amount":1250,"currency":"EUR"}' \
  http://127.0.0.1:18080/payments \
  | jq .
```

Prečítaj údaj:

```bash
curl -fsS \
  http://127.0.0.1:18080/payments/pay-100 \
  | jq -e '.id == "pay-100" and .amount == 1250 and .currency == "EUR"'
```

Tým sme prešli application validation, file write, sync a read. Neoverili sme backup, host loss ani concurrent-writer semantics.

## 14. Graceful stop

```bash
docker stop --time 15 atlas-payments-api

docker inspect atlas-payments-api \
  --format 'status={{.State.Status}} exit={{.State.ExitCode}} finished={{.State.FinishedAt}}'
```

Aplikácia má skončiť exit code `0`. Znovu ju spusti:

```bash
docker start atlas-payments-api
```

Stop testuje signal a process lifecycle. Pri reálnych payment operáciách by bolo potrebné overiť aj in-flight request behavior a idempotency.

## 15. Persistence cez container replacement

Odstráň container, nie volume:

```bash
docker rm --force atlas-payments-api
```

Volume stále existuje:

```bash
docker volume inspect atlas-payments-data
```

Vytvor rovnaký container znovu s generation `manual-2`, rovnakou network a rovnakým volume. Môžeš zopakovať predchádzajúci `docker create` príkaz so zmenenou environment hodnotou, potom `docker start`.

Po healthy stave:

```bash
curl -fsS http://127.0.0.1:18080/version \
  | jq -e '.config_generation == "manual-2"'

curl -fsS http://127.0.0.1:18080/payments/pay-100 \
  | jq -e '.id == "pay-100"'
```

Nový container ID a nová config generation používajú rovnaký data subject. To je presný dôkaz, že payment prežil container replacement na tom istom hoste.

## 16. Compose environment

Vytvor `env.example`:

```dotenv
PAYMENTS_IMAGE=atlas/payments-api:1.0.0-local
CONFIG_GENERATION=compose-1
LOG_LEVEL=info
HOST_PORT=18080
```

Pre local run:

```bash
cp env.example .env
```

`.env` je zámerne v `.dockerignore` a nemá obsahovať production secrets.

## 17. Compose model

Vytvor `compose.yaml`:

```yaml
name: atlas-payments

services:
  init-data:
    image: busybox:1.36.1@sha256:<verified-busybox-digest>
    user: "0:0"
    entrypoint: ["/bin/sh", "-ec"]
    command:
      - |
        mkdir -p /data
        chown 65532:65532 /data
        chmod 0750 /data
    volumes:
      - type: volume
        source: payments-data
        target: /data
    restart: "no"

  api:
    image: ${PAYMENTS_IMAGE:?PAYMENTS_IMAGE is required}
    depends_on:
      init-data:
        condition: service_completed_successfully
    user: "65532:65532"
    environment:
      LISTEN_ADDRESS: :8080
      LOG_LEVEL: ${LOG_LEVEL:-info}
      CONFIG_GENERATION: ${CONFIG_GENERATION:?CONFIG_GENERATION is required}
      DATA_PATH: /var/lib/atlas-payments/payments.jsonl
      HEALTHCHECK_URL: http://127.0.0.1:8080/readyz
    read_only: true
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=16m
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    pids_limit: 128
    mem_limit: 256m
    cpus: 0.50
    stop_grace_period: 15s
    volumes:
      - type: volume
        source: payments-data
        target: /var/lib/atlas-payments
    networks:
      backend:
        aliases:
          - payments-api
    ports:
      - target: 8080
        published: "${HOST_PORT:-18080}"
        host_ip: 127.0.0.1
        protocol: tcp
    healthcheck:
      test: ["CMD", "/usr/local/bin/payments-api", "healthcheck"]
      interval: 10s
      timeout: 3s
      start_period: 5s
      retries: 3
    restart: unless-stopped

  verifier:
    image: curlimages/curl:8.10.1@sha256:<verified-curl-digest>
    profiles:
      - verify
    depends_on:
      api:
        condition: service_healthy
    entrypoint: ["curl"]
    command: ["-fsS", "http://payments-api:8080/version"]
    networks:
      - backend
    restart: "no"

networks:
  backend:
    internal: true

volumes:
  payments-data:
    name: atlas-payments-data
```

Compose prevezme už existujúci named volume, pretože top-level volume má explicitné Engine meno. `init-data` sa postará o ownership a skončí. API sa spustí po jeho úspechu. Verifier je voliteľný profile a čaká na healthy API.

## 18. Resolved model pred mutation

Najprv odstráň ručne vytvorený container, aby nekolidoval na host porte:

```bash
docker rm --force atlas-payments-api 2>/dev/null || true
```

Zobraz interpolation environment:

```bash
docker compose --env-file .env config --environment
```

Vytvor resolved model:

```bash
docker compose --env-file .env config \
  > evidence/compose-resolved.yaml
```

Over podstatné invariants:

```bash
yq -e '
  .services.api.read_only == true
  and .services.api.privileged != true
  and .services.api.cap_drop == ["ALL"]
  and .services.api.ports[0].host_ip == "127.0.0.1"
  and .services.api.volumes[0].target == "/var/lib/atlas-payments"
' evidence/compose-resolved.yaml
```

`config` nevolá Docker Engine mutation. Dokazuje iba resolved Compose model pre zadané files, environment a Compose verziu.

## 19. Spustenie Compose application

```bash
docker compose --env-file .env up \
  --detach \
  --wait \
  --wait-timeout 120 \
  --remove-orphans
```

Po úspechu:

```bash
docker compose --env-file .env ps --all
docker compose --env-file .env images
docker compose --env-file .env top
docker compose --env-file .env logs --timestamps --no-color \
  > evidence/compose.log
```

`up --wait` je infrastructure verdict. Teraz overíme tri samostatné request paths.

Local Docker health už sleduje Engine. Service DNS cesta:

```bash
docker compose --env-file .env \
  --profile verify \
  run --rm --no-deps verifier
```

Host publication:

```bash
curl -fsS http://127.0.0.1:18080/version | jq .
```

Business path:

```bash
curl -fsS \
  --request POST \
  --header 'Content-Type: application/json' \
  --data '{"id":"pay-compose-1","amount":900,"currency":"EUR"}' \
  http://127.0.0.1:18080/payments | jq .
```

## 20. No-op reconciliation a recreate

Zachovaj container ID:

```bash
before_id="$(docker compose --env-file .env ps -q api)"

docker compose --env-file .env up \
  --detach \
  --wait \
  --wait-timeout 120

after_id="$(docker compose --env-file .env ps -q api)"
test "$before_id" = "$after_id"
```

Rovnaký ID znamená, že Compose pri tomto nezmenenom modeli API nerecreatlo. Neznamená to, že Compose bude nepretržite opravovať neskorší drift.

Teraz zmeň `.env`:

```dotenv
CONFIG_GENERATION=compose-2
```

Aplikuj model:

```bash
docker compose --env-file .env up \
  --detach \
  --wait \
  --wait-timeout 120
```

Nový container ID je očakávaný. Over loaded generation aj starý payment:

```bash
curl -fsS http://127.0.0.1:18080/version \
  | jq -e '.config_generation == "compose-2"'

curl -fsS http://127.0.0.1:18080/payments/pay-compose-1 \
  | jq -e '.id == "pay-compose-1"'
```

## 21. Zámerne chybný bind

Vytvor `compose.broken-bind.yaml`:

```yaml
services:
  api:
    environment:
      LISTEN_ADDRESS: 127.0.0.1:8080
```

Aplikuj combined model:

```bash
docker compose \
  --env-file .env \
  -f compose.yaml \
  -f compose.broken-bind.yaml \
  up --detach --wait --wait-timeout 120
```

Výsledok je poučný. Local healthcheck používa `127.0.0.1`, takže môže zostať zelený. Verifier cez service DNS a host curl však zlyhajú, pretože process nepočúva na container `eth0` address.

Zachovaj evidence:

```bash
broken_id="$(docker compose \
  --env-file .env \
  -f compose.yaml \
  -f compose.broken-bind.yaml \
  ps -q api)"

docker inspect "$broken_id" \
  > evidence/broken-bind-container.json

docker compose \
  --env-file .env \
  -f compose.yaml \
  -f compose.broken-bind.yaml \
  logs --timestamps --no-color api \
  > evidence/broken-bind.log
```

Over effective environment a health:

```bash
jq -r '.[0].Config.Env[] | select(startswith("LISTEN_ADDRESS="))' \
  evidence/broken-bind-container.json

docker inspect "$broken_id" \
  --format '{{json .State.Health}}' | jq .
```

Oprava nie je ďalší port. Odstráň override a aplikuj authoritative model:

```bash
docker compose --env-file .env -f compose.yaml \
  up --detach --wait --wait-timeout 120
```

Potom zopakuj verifier, host request a payment read.

## 22. Zámerne chybný volume ownership

Zastav application bez odstránenia volume-u:

```bash
docker compose --env-file .env down
```

Zmeň root directory na root-only:

```bash
docker run --rm \
  --user 0:0 \
  --mount type=volume,source=atlas-payments-data,target=/data \
  busybox:1.36.1@sha256:<verified-busybox-digest> \
  sh -ec 'chown 0:0 /data && chmod 0700 /data'
```

Spusti one-off API bez initializeru:

```bash
broken_volume_id="$(docker compose --env-file .env \
  run --detach --no-deps api)"
```

Pozri stav a logs:

```bash
docker inspect "$broken_volume_id" \
  --format '{{json .State}}' | jq .
docker logs "$broken_volume_id"
```

Readiness alebo startup má ukázať permission failure. Odstráň one-off container a spusti celý Compose model vrátane initializeru:

```bash
docker rm --force "$broken_volume_id"
docker compose --env-file .env up \
  --detach --wait --wait-timeout 120
```

Recovery sa uzavrie až po POST/GET a persistence kontrole.

## 23. Multi-platform publication

Produkčný image nepublikuj cez local `--load`:

```bash
IMAGE_REF="registry.example.com/atlas/payments-api:1.0.0"

docker buildx build \
  --builder atlas-builder \
  --target runtime \
  --platform linux/amd64,linux/arm64 \
  --build-arg VERSION=1.0.0 \
  --build-arg VCS_REF="$VCS_REF" \
  --provenance=mode=max \
  --sbom=true \
  --metadata-file evidence/build-metadata.json \
  --tag "$IMAGE_REF" \
  --push \
  .
```

Read-back:

```bash
docker buildx imagetools inspect "$IMAGE_REF"
docker buildx imagetools inspect "$IMAGE_REF" --raw \
  > evidence/image-index.json
```

Platform inventory:

```bash
jq -r '.manifests[] | [.platform.os,.platform.architecture,.digest] | @tsv' \
  evidence/image-index.json
```

Očakávame amd64 aj arm64. Tag zostáva pointer. Produkčné `.env` alebo release manifest má používať:

```dotenv
PAYMENTS_IMAGE=registry.example.com/atlas/payments-api@sha256:<index-digest>
```

## 24. Cleanup bez straty dát

Zastav Compose resources, ale ponechaj named volume:

```bash
docker compose --env-file .env down --remove-orphans
```

Over:

```bash
docker volume inspect atlas-payments-data
```

Až keď už data nepotrebuješ a máš správny backup alebo ide o čisto cvičné dáta:

```bash
docker volume rm atlas-payments-data
docker network rm atlas-payments-net 2>/dev/null || true
docker buildx rm atlas-builder
```

`docker system prune` ani `docker compose down --volumes` nepoužívaj ako mechanický záver bez inventory. Môžu odstrániť data alebo incident evidence, ktoré majú dlhší lifecycle než aktuálny project.

## 25. Čo tento projekt preukázal

Začali sme source tree-om a unit testom. BuildKit explicitne vykonal test target a samostatne vytvoril runtime image. Image inspect potvrdil metadata a export rootfs potvrdil binary path. Pred process startom sme skontrolovali container create configuration. Potom sme oddelene overili local health, host publication, service DNS a business write/read.

Named volume prežil ručný container replacement aj Compose recreate. Druhý nezmenený `up` zachoval container ID, zatiaľ čo configuration change vytvorila novú generation. Broken bind ukázal, že local health môže byť zelený pri nefunkčnej external network ceste. Volume incident ukázal, že non-root user a persistentný filesystem potrebujú spoločný UID/GID contract.

Multi-platform publication napokon vytvorila registry image index a platform manifests, ktoré sa musia read-backnúť a spotrebovať digestom. Žiadny jednotlivý zelený príkaz by sám nepreukázal celý tento chain.

## Primárne zdroje

- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [BuildKit](https://docs.docker.com/build/buildkit/)
- [`docker buildx build`](https://docs.docker.com/reference/cli/docker/buildx/build/)
- [Running containers](https://docs.docker.com/engine/containers/run/)
- [Volumes](https://docs.docker.com/engine/storage/volumes/)
- [Port publishing](https://docs.docker.com/engine/network/port-publishing/)
- [Compose Specification](https://docs.docker.com/reference/compose-file/)
- [`docker compose config`](https://docs.docker.com/reference/cli/docker/compose/config/)
- [`docker compose up`](https://docs.docker.com/reference/cli/docker/compose/up/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: BuildKit a Buildx](buildkit-buildx.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Docker troubleshooting →](docker-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
