# Praktický Docker projekt od prázdneho adresára po overený Compose runtime

Táto kapitola materializuje pojmy z predchádzajúcich Docker kapitol do jedného malého, ale reálneho projektu. Cieľom nie je iba skopírovať Dockerfile alebo spustiť niekoľko `docker` príkazov. Pri každom súbore a príkaze si vysvetlíme, aký vstup vytvára, čo Docker alebo BuildKit z tohto vstupu zostaví, čo sa neskôr zmení pri vytvorení containeru a čo daný zelený výsledok ešte nedokazuje.

Budeme kontajnerizovať jednoduchú HTTP službu `payments-api`. Aplikácia poskytne health, readiness a version endpoint, prijme malý payment záznam a uloží ho do súboru. Práve zápis do súboru nám umožní prakticky ukázať rozdiel medzi image filesystemom, zapisovateľnou vrstvou containeru a named volume-om.

Výsledný tok bude:

```text
application source a test
→ build context a .dockerignore
→ multi-stage Dockerfile
→ samostatný test target
→ runtime image
→ image metadata a filesystem inspection
→ container create a effective runtime configuration
→ process, health, port a volume verification
→ Compose resolved model
→ recreate a persistence test
→ zámerne chybný network bind
→ diagnostika a oprava
→ multi-platform publication a digest read-back
→ cleanup
```

## 1. Vytvorenie adresárovej štruktúry

Najprv vytvor pracovný adresár:

```bash
mkdir -p atlas-payments-docker/cmd/payments-api
cd atlas-payments-docker
```

Výsledná štruktúra bude:

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

Tento adresár ešte nie je image ani container. Je to iba source tree. Výsledný image bude závisieť od obsahu build contextu, Dockerfile-u, base images, build arguments, buildera, platformy a cache. Container následne pridá ďalšie runtime vstupy, napríklad environment variables, mounts, network, port publishing, resource limits a security options.

## 2. `go.mod`: identita aplikácie

Vytvor `go.mod`:

```go
module example.com/atlas/payments-api

go 1.25
```

Module path identifikuje Go modul. Riadok `go 1.25` určuje language a module semantics, ktoré projekt očakáva. Neprikazuje Dockeru konkrétny compiler image; ten neskôr určíme samostatne v Dockerfile-i.

## 3. `main.go`: minimálny runtime contract

Vytvor `cmd/payments-api/main.go`:

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

    file, err := os.OpenFile(
        app.dataPath,
        os.O_CREATE|os.O_APPEND|os.O_WRONLY,
        0o640,
    )
    if err != nil {
        return fmt.Errorf("open data file: %w", err)
    }

    return file.Close()
}

func (app application) appendPayment(value payment) error {
    if strings.TrimSpace(value.ID) == "" {
        return errors.New("payment id is required")
    }
    if value.Amount <= 0 {
        return errors.New("payment amount must be positive")
    }
    if len(value.Currency) != 3 {
        return errors.New("currency must use a three-letter code")
    }

    file, err := os.OpenFile(
        app.dataPath,
        os.O_CREATE|os.O_APPEND|os.O_WRONLY,
        0o640,
    )
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

func (app application) routes() http.Handler {
    mux := http.NewServeMux()

    mux.HandleFunc("GET /healthz", func(writer http.ResponseWriter, _ *http.Request) {
        writer.Header().Set("Content-Type", "application/json")
        _, _ = writer.Write([]byte(`{"status":"alive"}`))
    })

    mux.HandleFunc("GET /readyz", func(writer http.ResponseWriter, _ *http.Request) {
        if err := app.ensureWritableDataPath(); err != nil {
            http.Error(writer, err.Error(), http.StatusServiceUnavailable)
            return
        }

        writer.Header().Set("Content-Type", "application/json")
        _, _ = writer.Write([]byte(`{"status":"ready"}`))
    })

    mux.HandleFunc("GET /version", func(writer http.ResponseWriter, _ *http.Request) {
        writer.Header().Set("Content-Type", "application/json")
        _ = json.NewEncoder(writer).Encode(map[string]string{
            "service":           "payments-api",
            "version":           version,
            "commit":            commit,
            "config_generation": app.configGeneration,
        })
    })

    mux.HandleFunc("POST /payments", func(writer http.ResponseWriter, request *http.Request) {
        defer request.Body.Close()

        var value payment
        decoder := json.NewDecoder(
            http.MaxBytesReader(writer, request.Body, 64*1024),
        )
        decoder.DisallowUnknownFields()

        if err := decoder.Decode(&value); err != nil {
            http.Error(writer, "invalid payment payload", http.StatusBadRequest)
            return
        }

        if err := app.appendPayment(value); err != nil {
            http.Error(writer, err.Error(), http.StatusUnprocessableEntity)
            return
        }

        writer.Header().Set("Content-Type", "application/json")
        writer.WriteHeader(http.StatusCreated)
        _ = json.NewEncoder(writer).Encode(value)
    })

    mux.HandleFunc("GET /payments/{id}", func(writer http.ResponseWriter, request *http.Request) {
        value, found, err := app.findPayment(request.PathValue("id"))
        if err != nil {
            http.Error(writer, err.Error(), http.StatusInternalServerError)
            return
        }
        if !found {
            http.NotFound(writer, request)
            return
        }

        writer.Header().Set("Content-Type", "application/json")
        _ = json.NewEncoder(writer).Encode(value)
    })

    return mux
}

func runServer() error {
    listenAddress := environment("LISTEN_ADDRESS", ":8080")
    dataPath := environment(
        "DATA_PATH",
        "/var/lib/atlas-payments/payments.jsonl",
    )
    configGeneration := environment("CONFIG_GENERATION", "local")

    app := application{
        dataPath:         dataPath,
        configGeneration: configGeneration,
    }

    if err := app.ensureWritableDataPath(); err != nil {
        return err
    }

    server := &http.Server{
        Addr:              listenAddress,
        Handler:           app.routes(),
        ReadHeaderTimeout: 5 * time.Second,
    }

    signalContext, stop := signal.NotifyContext(
        context.Background(),
        syscall.SIGTERM,
        syscall.SIGINT,
    )
    defer stop()

    serverErrors := make(chan error, 1)

    go func() {
        log.Printf(
            "starting payments-api version=%s commit=%s address=%s data=%s config=%s",
            version,
            commit,
            listenAddress,
            dataPath,
            configGeneration,
        )

        err := server.ListenAndServe()
        if err != nil && !errors.Is(err, http.ErrServerClosed) {
            serverErrors <- err
            return
        }
        serverErrors <- nil
    }()

    select {
    case err := <-serverErrors:
        return err
    case <-signalContext.Done():
        shutdownContext, cancel := context.WithTimeout(
            context.Background(),
            10*time.Second,
        )
        defer cancel()

        return server.Shutdown(shutdownContext)
    }
}

func runHealthcheck() error {
    url := environment(
        "HEALTHCHECK_URL",
        "http://127.0.0.1:8080/readyz",
    )

    client := &http.Client{Timeout: 2 * time.Second}
    response, err := client.Get(url)
    if err != nil {
        return err
    }
    defer response.Body.Close()

    if response.StatusCode != http.StatusOK {
        return fmt.Errorf("health endpoint returned %s", response.Status)
    }

    return nil
}

func main() {
    command := "serve"
    if len(os.Args) > 1 {
        command = os.Args[1]
    }

    var err error

    switch command {
    case "serve":
        err = runServer()
    case "healthcheck":
        err = runHealthcheck()
    case "version":
        err = json.NewEncoder(os.Stdout).Encode(map[string]string{
            "service": "payments-api",
            "version": version,
            "commit":  commit,
        })
    default:
        err = fmt.Errorf("unknown command %q", command)
    }

    if err != nil {
        log.Fatal(err)
    }
}
```

Aplikácia je zámerne malá, ale ukazuje niekoľko dôležitých runtime vlastností.

`LISTEN_ADDRESS` určuje, na ktorom interface a porte proces počúva. Hodnota `:8080` znamená port `8080` na všetkých dostupných adresách v network namespace-e procesu. Neskôr zámerne nastavíme `127.0.0.1:8080` a ukážeme, prečo môže byť container healthy, ale host port nedostupný.

`DATA_PATH` určuje persistentný súbor. Readiness endpoint sa nepýta iba na to, či process žije. Pokúsi sa otvoriť data path na zápis. Ak volume nemá správne permissions alebo chýba writable mount, `/readyz` vráti HTTP `503`.

`CONFIG_GENERATION` nám umožní overiť, ktorú runtime konfiguráciu proces skutočne načítal. Samotná environment hodnota v `docker inspect` ešte nepreukazuje, že ju aplikácia použila. `/version` preto vracia application-loaded hodnotu.

Signal handling je súčasťou container lifecycle-u. Keď Docker pošle `SIGTERM`, aplikácia použije bounded graceful shutdown namiesto okamžitého ukončenia procesu.

## 4. `main_test.go`: overenie aplikačného contractu

Vytvor `cmd/payments-api/main_test.go`:

```go
package main

import (
    "net/http"
    "net/http/httptest"
    "path/filepath"
    "strings"
    "testing"
)

func TestPaymentWriteAndRead(t *testing.T) {
    t.Parallel()

    app := application{
        dataPath:         filepath.Join(t.TempDir(), "payments.jsonl"),
        configGeneration: "test-1",
    }

    server := httptest.NewServer(app.routes())
    t.Cleanup(server.Close)

    requestBody := `{"id":"pay-100","amount":1250,"currency":"EUR"}`

    response, err := http.Post(
        server.URL+"/payments",
        "application/json",
        strings.NewReader(requestBody),
    )
    if err != nil {
        t.Fatalf("create payment: %v", err)
    }
    defer response.Body.Close()

    if response.StatusCode != http.StatusCreated {
        t.Fatalf(
            "unexpected create status: got %d want %d",
            response.StatusCode,
            http.StatusCreated,
        )
    }

    getResponse, err := http.Get(server.URL + "/payments/pay-100")
    if err != nil {
        t.Fatalf("read payment: %v", err)
    }
    defer getResponse.Body.Close()

    if getResponse.StatusCode != http.StatusOK {
        t.Fatalf(
            "unexpected read status: got %d want %d",
            getResponse.StatusCode,
            http.StatusOK,
        )
    }
}

func TestRejectsInvalidAmount(t *testing.T) {
    t.Parallel()

    app := application{
        dataPath:         filepath.Join(t.TempDir(), "payments.jsonl"),
        configGeneration: "test-1",
    }

    server := httptest.NewServer(app.routes())
    t.Cleanup(server.Close)

    requestBody := `{"id":"pay-invalid","amount":0,"currency":"EUR"}`

    response, err := http.Post(
        server.URL+"/payments",
        "application/json",
        strings.NewReader(requestBody),
    )
    if err != nil {
        t.Fatalf("create invalid payment: %v", err)
    }
    defer response.Body.Close()

    if response.StatusCode != http.StatusUnprocessableEntity {
        t.Fatalf(
            "unexpected status: got %d want %d",
            response.StatusCode,
            http.StatusUnprocessableEntity,
        )
    }
}
```

Prvý test overuje základný write/read contract. Druhý test je forbidden path: nulová suma nesmie byť prijatá.

Spusť testy lokálne, ak máš Go toolchain:

```bash
go test ./...
```

Očakávaný výsledok:

```text
ok  example.com/atlas/payments-api/cmd/payments-api  ...
```

Tento výsledok dokazuje, že testované Go funkcie prešli v lokálnom toolchaine a prostredí. Nedokazuje, že rovnaké testy neskôr vykoná Docker build, že final image obsahuje správny binary alebo že volume a network runtime budú fungovať.

## 5. Lokálne spustenie pred kontajnerizáciou

Vytvor lokálny data adresár:

```bash
mkdir -p .local/data
```

Spusť aplikáciu:

```bash
LISTEN_ADDRESS=127.0.0.1:8080 \
DATA_PATH="$PWD/.local/data/payments.jsonl" \
CONFIG_GENERATION=local-1 \
go run ./cmd/payments-api
```

V druhom termináli:

```bash
curl --fail --silent http://127.0.0.1:8080/healthz
curl --fail --silent http://127.0.0.1:8080/readyz
curl --fail --silent http://127.0.0.1:8080/version | jq .
```

Očakávané odpovede:

```json
{"status":"alive"}
```

```json
{"status":"ready"}
```

```json
{
  "commit": "unknown",
  "config_generation": "local-1",
  "service": "payments-api",
  "version": "dev"
}
```

Lokálne spustenie potvrdzuje aplikačný contract bez Docker vrstvy. Keď neskôr rovnaká aplikácia zlyhá iba v containere, získame prvý diskriminačný bod: problém môže byť v image build-e alebo runtime konfigurácii, nie nevyhnutne v samotnom handleri.

## 6. `.dockerignore`: kontrola build contextu

Vytvor `.dockerignore`:

```dockerignore
.git
.gitignore
.env
.env.*
.local/
coverage/
dist/
tmp/
*.log
*.pem
*.key
compose.override.yaml
```

Keď spustíš:

```bash
docker buildx build .
```

bodka označuje build context. Docker klient alebo BuildKit odošle builderu súbory patriace do contextu, po aplikovaní `.dockerignore`.

Bez ignore súboru by sa do contextu mohli dostať Git history, lokálne dáta, test reports, logy, privátne keys alebo `.env` súbor. Context by bol väčší, zmeny nepodstatných súborov by mohli invalidovať cache a `COPY . .` by mohol nechtiac vložiť lokálne dáta do image layeru.

Skontroluj veľkosť contextu počas plain-progress buildu:

```bash
docker buildx build \
  --progress=plain \
  --target test \
  --output=type=cacheonly \
  .
```

V logu hľadaj krok podobný:

```text
transferring context: ...
```

Prenesená veľkosť sama nepreukazuje správny inventory. `.dockerignore` nie je bezpečnostná hranica proti škodlivému Dockerfile-u ani proti build commandu, ktorý si secret stiahne zo siete.

## 7. `Dockerfile`: celý build graph

Vytvor `Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1

ARG GO_IMAGE=golang:1.25-alpine@sha256:<verified-go-image-digest>
ARG RUNTIME_IMAGE=gcr.io/distroless/static-debian12:nonroot@sha256:<verified-runtime-image-digest>

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
    GOOS=${TARGETOS} \
    GOARCH=${TARGETARCH} \
    go build \
      -trimpath \
      -ldflags="-s -w -X main.version=${VERSION} -X main.commit=${VCS_REF}" \
      -o /out/payments-api \
      ./cmd/payments-api

FROM ${RUNTIME_IMAGE} AS runtime

ARG VERSION
ARG VCS_REF

LABEL org.opencontainers.image.title="Atlas Payments API" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}"

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

Dockerfile treba čítať po stages a po závislostiach, nie ako jeden vždy lineárny shell script:

```text
source
├── test
└── build
    └── runtime
```

Final target `runtime` závisí od `build`, ale nie od sibling stage-u `test`. To znamená, že úspešný build runtime image-u automaticky nedokazuje vykonanie testov. Test stage preto spustíme samostatne.

### `# syntax=docker/dockerfile:1`

Parser directive určuje Dockerfile frontend. Umožňuje používať moderné funkcie, napríklad `RUN --mount=type=cache`. Musí byť na začiatku súboru.

### Global `ARG` a `FROM`

Global arguments sú dostupné pre `FROM`, preto môžeme riadiť base images bez prepísania Dockerfile-u. Base reference obsahuje čitateľný tag aj digest. Tag vysvetľuje zámer človeku, digest určuje konkrétny manifest.

Placeholder `<verified-...-digest>` musíš pri reálnom použití nahradiť digestom schváleného image-u.

Global `ARG` nie je automaticky dostupný v ďalších instructions stage-u. Preto `VERSION` a `VCS_REF` deklarujeme znova v `build` aj `runtime` stage-i.

### Oddelené kopírovanie dependencies a source

```dockerfile
COPY go.mod ./
RUN ... go mod download
COPY cmd ./cmd
```

Dependency metadata sa kopíruje pred source kódom. Zmena `main.go` preto nemusí invalidovať dependency-download layer. Keby sme použili `COPY . .` hneď na začiatku, takmer každá source zmena by zneplatnila viac cache krokov.

### Cache mounts

Cache mount zrýchľuje opakované buildy. Jeho obsah sa nestane automaticky final image layerom a build musí vedieť fungovať aj po vymazaní cache. `sharing=locked` koordinuje paralelných writers, ale samo osebe nerobí cache dôveryhodnou.

### `CGO_ENABLED=0`

Statický Go binary znižuje závislosť od libc a dynamic loadera vo final image-i. Stále musí zodpovedať cieľovej OS a CPU architecture.

### `COPY --from=build`

Final stage nekopíruje compiler, source ani test toolchain. Preberá iba výsledný binary.

### `USER 65532:65532`

Aplikácia beží ako non-root user. Každý writable mount preto musí byť kompatibilný s UID/GID `65532`. Samotné `USER` v image-i nevyrieši permissions existujúceho volume-u.

### Exec-form `ENTRYPOINT` a `CMD`

Výsledný default command je:

```text
/usr/local/bin/payments-api serve
```

Exec form nevkladá medzi Docker a aplikáciu implicitný shell. Aplikačný binary sa stane PID 1 a priamo prijíma signals.

### `EXPOSE`

`EXPOSE 8080` dokumentuje container port. Nevytvára host listener. Port sa publikuje až cez runtime configuration.

## 8. Samostatné vykonanie test stage-u

Najprv vytvor alebo vyber Buildx builder:

```bash
docker buildx create \
  --name atlas-builder \
  --driver docker-container \
  --use

docker buildx inspect --bootstrap
```

Builder name nie je iba kozmetický. Určuje BuildKit daemon, jeho cache, driver, nodes, platforms a trust boundary.

Spusť test target:

```bash
docker buildx build \
  --builder atlas-builder \
  --target test \
  --platform linux/amd64 \
  --progress=plain \
  --output=type=cacheonly \
  .
```

Očakávaj úspešný krok `go test ./...`. Tento výsledok dokazuje, že BuildKit vykonal graph potrebný pre target `test` a že test command skončil exit code `0`. Nedokazuje final runtime image, druhú platformu ani produkčný volume/network contract.

Zámerne spusti test po dočasnej zmene očakávaného statusu v `main_test.go`. Build musí skončiť non-zero. Potom test vráť. Takto overíš, že test failure nie je interpretovaný ako zelený výsledok.

## 9. Zostavenie lokálneho runtime image-u

Nastav build metadata:

```bash
VERSION=1.0.0
VCS_REF="$(git rev-parse --short=12 HEAD 2>/dev/null || printf 'local')"
IMAGE="atlas/payments-api:${VERSION}-local"
```

Zostav runtime target pre lokálnu platformu:

```bash
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

`--load` vloží single-platform výsledok do image store-u aktuálneho Docker Engine-u. Nie je určený na uloženie multi-platform indexu.

Over, že image existuje:

```bash
docker image ls "$IMAGE"
```

Výstup s repository, tagom a image ID dokazuje lokálnu prítomnosť image-u. Tag je mutable pointer. Image ID je lokálna content identity image configu, nie automaticky registry digest.

## 10. Image metadata a build history

Ulož inspect výstup:

```bash
mkdir -p evidence

docker image inspect "$IMAGE" \
  > evidence/image-inspect.json
```

Vyber relevantné fields:

```bash
jq '.[0] | {
  Id,
  RepoTags,
  RepoDigests,
  Architecture,
  Os,
  Config: {
    User: .Config.User,
    Entrypoint: .Config.Entrypoint,
    Cmd: .Config.Cmd,
    Env: .Config.Env,
    WorkingDir: .Config.WorkingDir,
    ExposedPorts: .Config.ExposedPorts,
    Healthcheck: .Config.Healthcheck,
    Labels: .Config.Labels
  }
}' evidence/image-inspect.json
```

Očakávaj najmä non-root user, exec-form entrypoint, default command, working directory a `linux/amd64` platformu.

`docker image inspect` dokazuje image metadata uloženú v tomto Engine store-i. Container runtime môže `User`, `Entrypoint`, `Cmd` alebo environment prepísať.

Pozri image history:

```bash
docker image history \
  --no-trunc \
  "$IMAGE"
```

History pomáha odhaliť zbytočné package installation, secrets vložené cez command text alebo nečakané veľké layers. History sama nepreukazuje contents všetkých layerov.

## 11. Overenie final filesystemu bez spustenia servera

Vytvor dočasný container object:

```bash
image_check_container="$(docker create "$IMAGE")"
```

Exportuj root filesystem:

```bash
docker export "$image_check_container" \
  | tar -tf - \
  > evidence/rootfs-files.txt
```

Over prítomnosť binary:

```bash
grep -Fx 'usr/local/bin/payments-api' \
  evidence/rootfs-files.txt
```

Odstráň dočasný object:

```bash
docker rm "$image_check_container"
```

Tento test preukazuje prítomnosť pathu vo výslednom root filesysteme. Neoveruje executable permissions, CPU architecture, runtime mounts ani schopnosť procesu štartovať.

Binary contract over bez spustenia servera:

```bash
docker run --rm "$IMAGE" version | jq .
```

Command používa image `ENTRYPOINT` a nahrádza default `CMD ["serve"]` argumentom `version`.

## 12. Vytvorenie networku a named volume-u

Vytvor user-defined bridge network:

```bash
docker network create atlas-payments-net
```

Vytvor named volume:

```bash
docker volume create atlas-payments-data
```

Inspect:

```bash
docker network inspect atlas-payments-net | jq '.[0] | {
  Name,
  Driver,
  Internal,
  IPAM
}'

docker volume inspect atlas-payments-data | jq '.[0] | {
  Name,
  Driver,
  Mountpoint,
  Scope
}'
```

Network a volume sú samostatné Docker objects s vlastným lifecycle-om. Odstránenie containeru ich automaticky nemusí odstrániť.

Volume je nový a jeho root directory môže vlastniť root. Aplikácia bude bežať ako UID `65532`, preto volume pripravíme bounded initializerom:

```bash
docker run --rm \
  --user 0:0 \
  --mount type=volume,source=atlas-payments-data,target=/data \
  busybox:1.36.1@sha256:<verified-busybox-digest> \
  sh -ec 'mkdir -p /data && chown 65532:65532 /data'
```

Initializer beží ako root iba kvôli ownership transition. Produkčná implementácia musí presne vedieť, ktorý component vlastní initialization a migration.

## 13. `docker create`: runtime konfigurácia pred štartom

Vytvor container bez spustenia procesu:

```bash
docker create \
  --name atlas-payments-api \
  --network atlas-payments-net \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --cap-drop ALL \
  --security-opt no-new-privileges=true \
  --memory 128m \
  --cpus 0.50 \
  --pids-limit 100 \
  --mount type=volume,source=atlas-payments-data,target=/var/lib/atlas-payments \
  --publish 127.0.0.1:18080:8080 \
  --env CONFIG_GENERATION=manual-1 \
  "$IMAGE"
```

Týmto vznikol container object, ale aplikácia ešte nebeží.

Ulož effective configuration:

```bash
docker inspect atlas-payments-api \
  > evidence/container-before-start.json
```

Skontroluj ju:

```bash
jq '.[0] | {
  Image,
  Config: {
    User: .Config.User,
    Entrypoint: .Config.Entrypoint,
    Cmd: .Config.Cmd,
    Env: .Config.Env
  },
  HostConfig: {
    ReadonlyRootfs: .HostConfig.ReadonlyRootfs,
    CapDrop: .HostConfig.CapDrop,
    SecurityOpt: .HostConfig.SecurityOpt,
    Memory: .HostConfig.Memory,
    NanoCpus: .HostConfig.NanoCpus,
    PidsLimit: .HostConfig.PidsLimit
  },
  Mounts,
  Ports: .NetworkSettings.Ports
}' evidence/container-before-start.json
```

Tu už nepozeráme iba image defaults. Vidíme effective container configuration po aplikovaní runtime options.

## 14. Spustenie containeru a PID 1

Spusť container:

```bash
docker start atlas-payments-api
```

Pozri process a logs:

```bash
docker ps --all \
  --filter name=atlas-payments-api

docker logs --timestamps atlas-payments-api

docker top atlas-payments-api \
  -eo pid,ppid,user,args
```

Očakávaj process `/usr/local/bin/payments-api serve`. Aplikačný binary má byť hlavný PID 1 v containere. Exec-form `ENTRYPOINT` nevytvoril shell wrapper.

`docker start` success preukazuje, že Engine prijal start request. Process môže krátko nato exitnúť. Preto vždy čítaj aj `.State`, logs a health.

## 15. Process state a Docker health

Sleduj health:

```bash
for attempt in $(seq 1 30); do
  state="$(
    docker inspect atlas-payments-api \
      --format '{{.State.Status}}'
  )"
  health="$(
    docker inspect atlas-payments-api \
      --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}'
  )"

  printf 'attempt=%s state=%s health=%s\n' \
    "$attempt" \
    "$state" \
    "$health"

  [ "$health" = "healthy" ] && break
  sleep 1
done
```

Pozri health history:

```bash
docker inspect atlas-payments-api \
  --format '{{json .State.Health.Log}}' \
  | jq 'map({
      Start,
      End,
      ExitCode,
      Output
    })'
```

Healthcheck spúšťa application binary, ktorý volá `http://127.0.0.1:8080/readyz`. Readiness zároveň overuje write access k data pathu.

`healthy` preto dokazuje local container network path a writable application data path. Neoveruje host port, service discovery ani konkrétny business POST/GET.

## 16. Host port a loaded configuration

Over host path:

```bash
curl --fail --silent --show-error \
  http://127.0.0.1:18080/version \
  | jq .
```

Očakávaj `service=payments-api`, `version=1.0.0` a `config_generation=manual-1`.

Request prešiel cez host loopback, Docker port publishing, container network namespace a application listener. Hodnota `manual-1` je process-loaded konfigurácia, nie iba hodnota z inspect metadata.

## 17. Business write/read a named-volume persistence

Vytvor payment:

```bash
curl --fail --silent --show-error \
  --request POST \
  --header 'Content-Type: application/json' \
  --data '{"id":"pay-100","amount":1250,"currency":"EUR"}' \
  http://127.0.0.1:18080/payments \
  | jq .
```

Prečítaj ho:

```bash
curl --fail --silent --show-error \
  http://127.0.0.1:18080/payments/pay-100 \
  | jq -e '
      .id == "pay-100"
      and .amount == 1250
      and .currency == "EUR"
    '
```

Odstráň iba container:

```bash
docker rm --force atlas-payments-api
```

Volume stále existuje:

```bash
docker volume inspect atlas-payments-data
```

Vytvor novú container generation s rovnakým volume-om a `CONFIG_GENERATION=manual-2`, spusti ju a znovu načítaj `pay-100`.

Týmto preukážeš persistence cez container replacement na rovnakom Docker hoste a v rovnakom named volume subjecte. Nepreukazuje to backup, restore, stratu hosta, corruption recovery ani concurrent-writer fencing.

## 18. Graceful stop a jeho hranice

Zastav aplikáciu:

```bash
docker stop \
  --time 15 \
  atlas-payments-api
```

Over exit:

```bash
docker inspect atlas-payments-api \
  --format 'status={{.State.Status}} exit={{.State.ExitCode}} finished={{.State.FinishedAt}}'
```

Docker poslal `SIGTERM` podľa `STOPSIGNAL`. Aplikácia vykonala bounded HTTP shutdown. Exit code `0` však automaticky nedokazuje, že každý in-flight business side effect bol dokončený alebo kompenzovaný.

Znovu spusti container pre ďalšie kroky:

```bash
docker start atlas-payments-api
```

## 19. `env.example`: Compose inputs

Vytvor `env.example`:

```dotenv
PAYMENTS_IMAGE=atlas/payments-api:1.0.0-local
CONFIG_GENERATION=compose-1
HOST_PORT=18080
```

Skopíruj ho do lokálneho `.env`:

```bash
cp env.example .env
```

`.env` nepatrí do image ani do Git repository, ak obsahuje lokálne alebo citlivé hodnoty. Compose ho používa na interpolation source modelu. Citlivé credentials potrebujú samostatný secret lifecycle.

## 20. `compose.yaml`: celý lokálny application model

Vytvor `compose.yaml`:

```yaml
name: atlas-payments

services:
  init-data:
    image: busybox:1.36.1@sha256:<verified-busybox-digest>
    user: "0:0"
    entrypoint:
      - /bin/sh
      - -ec
    command:
      - |
        mkdir -p /data
        chown 65532:65532 /data
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
    environment:
      CONFIG_GENERATION: ${CONFIG_GENERATION:?CONFIG_GENERATION is required}
      LISTEN_ADDRESS: :8080
      DATA_PATH: /var/lib/atlas-payments/payments.jsonl
      HEALTHCHECK_URL: http://127.0.0.1:8080/readyz
    read_only: true
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=16m
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    pids_limit: 100
    mem_limit: 128m
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
        published: ${HOST_PORT:-18080}
        host_ip: 127.0.0.1
        protocol: tcp
    healthcheck:
      test:
        - CMD
        - /usr/local/bin/payments-api
        - healthcheck
      interval: 10s
      timeout: 3s
      start_period: 5s
      retries: 3
    restart: unless-stopped

  verifier:
    image: busybox:1.36.1@sha256:<verified-busybox-digest>
    profiles:
      - verify
    depends_on:
      api:
        condition: service_healthy
    command:
      - sh
      - -ec
      - |
        payload="$$(wget -qO- http://payments-api:8080/version)"
        printf '%s\n' "$$payload"
        printf '%s\n' "$$payload" \
          | grep -F '"service":"payments-api"'
        printf '%s\n' "$$payload" \
          | grep -F '"config_generation":"${CONFIG_GENERATION}"'
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

`init-data` pripraví ownership volume-u a skončí. `service_completed_successfully` je ordering contract, nie nepretržitý control loop.

`api.image` používa required interpolation. Chýbajúca alebo prázdna hodnota má spôsobiť chybu namiesto tichého použitia nečakaného image-u.

Root filesystem je read-only. Zapisovateľné sú iba `/tmp` ako tmpfs a `/var/lib/atlas-payments` ako named volume.

`backend` je user-defined internal network. Services na ňom používajú Compose DNS. `internal: true` nie je kompletná host firewall ani supply-chain politika.

Dvojité `$$payload` spôsobí, že Compose odovzdá literal `$payload` shellu vo verifier containere namiesto vlastnej interpolation.

## 21. Resolved Compose model pred mutáciou

Najprv skontroluj environment použitý na interpolation:

```bash
docker compose \
  --env-file .env \
  config \
  --environment
```

Vyrenderuj celý model:

```bash
docker compose \
  --env-file .env \
  config \
  > evidence/compose-resolved.yaml
```

Pozri služby, images, networks a volumes:

```bash
docker compose --env-file .env config --services
docker compose --env-file .env config --images
docker compose --env-file .env config --networks
docker compose --env-file .env config --volumes
```

Over invariants cez `yq`:

```bash
yq -e '
  .services.api.read_only == true
  and .services.api.privileged != true
  and .services.api.cap_drop == ["ALL"]
  and .services.api.ports[0].host_ip == "127.0.0.1"
  and .services.api.volumes[0].target == "/var/lib/atlas-payments"
' evidence/compose-resolved.yaml
```

`docker compose config` dokazuje resolved model po interpolation a normalizácii. Nevytvára containers, network ani volume.

## 22. Prechod z ručného lifecycle-u na Compose

Pred Compose runom odstráň ručne vytvorený container, aby nekolidoval na host porte alebo mene:

```bash
docker rm --force atlas-payments-api
```

Named volume ponecháme. Compose deklaruje volume s explicitným menom `atlas-payments-data`, preto prevezme rovnaký data subject.

## 23. Spustenie Compose stacku

Spusť služby:

```bash
docker compose \
  --env-file .env \
  up \
  --detach \
  --wait \
  --wait-timeout 120 \
  --remove-orphans
```

`--detach` nechá services bežať na pozadí. `--wait` čaká, kým services dosiahnu running alebo healthy stav podľa modelu. `--wait-timeout` ohraničuje čakanie.

Pozri výsledný stav:

```bash
docker compose --env-file .env ps --all
docker compose --env-file .env images
docker compose --env-file .env top
docker compose --env-file .env logs --timestamps --no-color
```

Úspešný `compose up --wait` dokazuje bounded Compose startup verdict. Ešte nepreukazuje host request, DNS path verifiera ani persistence po recreate.

## 24. Overenie troch network paths

Docker health path používa container-local loopback. Compose DNS path overíš verifier profile-om:

```bash
docker compose \
  --env-file .env \
  --profile verify \
  run \
  --rm \
  --no-deps \
  verifier
```

Host-published path:

```bash
curl --fail --silent --show-error \
  http://127.0.0.1:18080/version \
  | jq .
```

Tri paths sú:

```text
Docker healthcheck
→ local container loopback

verifier
→ Compose DNS a backend network

host curl
→ host port publishing
```

Jeden zelený path nenahrádza ostatné.

## 25. Compose business test a persistence

Vytvor ďalší payment:

```bash
curl --fail --silent --show-error \
  --request POST \
  --header 'Content-Type: application/json' \
  --data '{"id":"pay-compose-1","amount":900,"currency":"EUR"}' \
  http://127.0.0.1:18080/payments \
  | jq .
```

Over ho:

```bash
curl --fail --silent --show-error \
  http://127.0.0.1:18080/payments/pay-compose-1 \
  | jq -e '.id == "pay-compose-1"'
```

Získaj current container ID, vykonaj `--force-recreate` API služby a over, že nový ID je odlišný, ale payment zostal čitateľný.

Týmto sa oddeľuje service/container generation od volume generation.

## 26. Druhý nezmenený Compose run

Spusti rovnaký desired model ešte raz a porovnaj ID pred a po:

```bash
before_id="$(docker compose --env-file .env ps -q api)"

docker compose \
  --env-file .env \
  up \
  --detach \
  --wait \
  --wait-timeout 120

after_id="$(docker compose --env-file .env ps -q api)"

test "$before_id" = "$after_id"
```

Rovnaký ID znamená, že Compose pri tomto konkrétnom druhom rune nerozhodol o recreate služby. Nie je to dôkaz nepretržitého reconciliation.

## 27. Configuration change a controlled recreate

Zmeň `.env`:

```dotenv
PAYMENTS_IMAGE=atlas/payments-api:1.0.0-local
CONFIG_GENERATION=compose-2
HOST_PORT=18080
```

Vyrenderuj nový model a porovnaj ho s pôvodným:

```bash
docker compose --env-file .env config \
  > evidence/compose-resolved-2.yaml

diff -u \
  evidence/compose-resolved.yaml \
  evidence/compose-resolved-2.yaml
```

Aplikuj zmenu a over nový container ID:

```bash
old_id="$(docker compose --env-file .env ps -q api)"

docker compose \
  --env-file .env \
  up \
  --detach \
  --wait \
  --wait-timeout 120

new_id="$(docker compose --env-file .env ps -q api)"

test "$old_id" != "$new_id"
```

Over loaded generation a persistentný payment:

```bash
curl --fail --silent http://127.0.0.1:18080/version \
  | jq -e '.config_generation == "compose-2"'

curl --fail --silent http://127.0.0.1:18080/payments/pay-compose-1 \
  | jq -e '.id == "pay-compose-1"'
```

## 28. Zámerne chybný bind address

Vytvor `compose.broken-bind.yaml`:

```yaml
services:
  api:
    environment:
      LISTEN_ADDRESS: 127.0.0.1:8080
```

Aplikuj base file spolu s override:

```bash
docker compose \
  --env-file .env \
  -f compose.yaml \
  -f compose.broken-bind.yaml \
  up \
  --detach \
  --wait \
  --wait-timeout 120
```

Healthcheck môže zostať zelený, pretože beží v rovnakom container network namespace-e a volá `127.0.0.1:8080`.

Host request však zlyhá:

```bash
curl --fail --silent --show-error \
  http://127.0.0.1:18080/version
```

Verifier cez service DNS tiež zlyhá.

Failure chain:

```text
process počúva na container loopbacku
→ local Docker healthcheck prejde
→ network alias smeruje na container interface IP
→ process na tejto IP nepočúva
→ Compose DNS path zlyhá
→ host-published path zlyhá
```

Toto nie je nevyhnutne Docker NAT chyba. Port publishing môže správne smerovať na container IP a port, ale na cieľovej adrese nie je listener.

## 29. Diagnostika chybného bindu

Najprv zachovaj evidence:

```bash
docker compose \
  --env-file .env \
  -f compose.yaml \
  -f compose.broken-bind.yaml \
  ps --all

docker compose \
  --env-file .env \
  -f compose.yaml \
  -f compose.broken-bind.yaml \
  logs --timestamps --no-color api \
  > evidence/broken-bind-api.log

broken_id="$(
  docker compose \
    --env-file .env \
    -f compose.yaml \
    -f compose.broken-bind.yaml \
    ps -q api
)"

docker inspect "$broken_id" \
  > evidence/broken-bind-container.json
```

Over environment:

```bash
jq -r '
  .[0].Config.Env[]
  | select(startswith("LISTEN_ADDRESS="))
' evidence/broken-bind-container.json
```

Over health a port mapping:

```bash
docker inspect "$broken_id" \
  --format '{{json .State.Health}}' \
  | jq .

docker inspect "$broken_id" \
  --format '{{json .NetworkSettings.Ports}}' \
  | jq .
```

Port mapping môže byť správny a health zelený. Rozhodujúca informácia je bind address procesu.

Keďže distroless image nemá shell ani `ss`, nepokúšaj sa do bežiaceho production containeru inštalovať debug tools. Použi logs, effective environment, application telemetry alebo controlled debug workload.

## 30. Oprava bindu a overenie recovery

Odstráň broken override z invocation a aplikuj iba authoritative Compose model:

```bash
docker compose \
  --env-file .env \
  -f compose.yaml \
  up \
  --detach \
  --wait \
  --wait-timeout 120
```

Over health, verifier, host path a pôvodný payment. Recovery nie je uzavretá iba tým, že container je znovu healthy. Musí prejsť aj path, ktorý pôvodne zlyhával, a persistentný business údaj.

## 31. Druhý failure path: volume permissions

Zastav stack bez odstránenia volume-u:

```bash
docker compose --env-file .env down
```

Zámerne zmeň ownera volume-u na root:

```bash
docker run --rm \
  --user 0:0 \
  --mount type=volume,source=atlas-payments-data,target=/data \
  busybox:1.36.1@sha256:<verified-busybox-digest> \
  sh -ec 'chown 0:0 /data && chmod 700 /data'
```

Spusť API bez initializeru:

```bash
broken_volume_id="$(
  docker compose \
    --env-file .env \
    run \
    --detach \
    --no-deps \
    api
)"
```

Pozri stav a logs:

```bash
docker inspect "$broken_volume_id" \
  --format '{{json .State}}' \
  | jq .

docker logs "$broken_volume_id"
```

Očakávaj permission-related chybu pri otvorení data pathu.

Odstráň one-off container a oprav authoritative flow spustením celého modelu vrátane `init-data`:

```bash
docker rm --force "$broken_volume_id"

docker compose \
  --env-file .env \
  up \
  --detach \
  --wait \
  --wait-timeout 120
```

Potom znovu over POST/GET. Failure path ukazuje, že non-root image a named volume musia zdieľať explicitný UID/GID contract.

## 32. Multi-platform build a registry publication

Lokálny `--load` build obsahoval iba jednu platformu. Release pre `linux/amd64` a `linux/arm64` publikuj do registry:

```bash
IMAGE_REF="registry.example.com/atlas/payments-api:1.0.0"

docker buildx build \
  --builder atlas-builder \
  --target runtime \
  --platform linux/amd64,linux/arm64 \
  --build-arg VERSION=1.0.0 \
  --build-arg VCS_REF="$VCS_REF" \
  --tag "$IMAGE_REF" \
  --provenance=mode=max \
  --sbom=true \
  --push \
  .
```

`--push` publikuje výsledok do registry. Pri multi-platform build-e vznikne image index, ktorý odkazuje na platform-specific manifests.

Read-back:

```bash
docker buildx imagetools inspect "$IMAGE_REF"

docker buildx imagetools inspect \
  "$IMAGE_REF" \
  --raw \
  > evidence/image-index.json
```

Zobraz platform inventory:

```bash
jq -r '
  .manifests[]
  | [
      .platform.os,
      .platform.architecture,
      .digest
    ]
  | @tsv
' evidence/image-index.json
```

Očakávaj `linux/amd64` a `linux/arm64` manifests. Tag `1.0.0` je stále pointer. Release manifest má zachovať index digest a runtime má používať digest reference:

```text
registry.example.com/atlas/payments-api@sha256:<index-digest>
```

Index digest identifikuje platform selection graph. Konkrétny runtime neskôr vyberie platform-specific manifest.

## 33. Digest-pinned Compose consumption

Po publication-e nastav v `.env`:

```dotenv
PAYMENTS_IMAGE=registry.example.com/atlas/payments-api@sha256:<index-digest>
CONFIG_GENERATION=compose-3
HOST_PORT=18080
```

Znovu vyrenderuj Compose model a over immutable reference:

```bash
docker compose --env-file .env config \
  > evidence/compose-digest-pinned.yaml

yq -e '
  .services.api.image
  == "registry.example.com/atlas/payments-api@sha256:<index-digest>"
' evidence/compose-digest-pinned.yaml
```

`docker compose pull` a `docker compose up` potom pracujú s immutable index reference. Stále treba overiť, ktorý platform manifest zvolil konkrétny host.

## 34. Troubleshooting flow podľa vrstiev

Pri Docker incidente nezačni automaticky `docker restart` alebo `docker system prune`.

Postupuj:

```text
docker client a context
→ daemon/API
→ image reference a platform resolution
→ container create configuration
→ OCI runtime a process start
→ PID 1, exit a health
→ mounts a filesystem permissions
→ listener, network a port publishing
→ cgroups, seccomp a LSM
→ application a business outcome
```

Základný evidence pack:

```bash
docker context show
docker version
docker info

docker image inspect "$IMAGE" \
  > evidence/incident-image.json

docker compose --env-file .env ps --all
docker compose --env-file .env logs --timestamps --no-color \
  > evidence/incident-compose.log

docker inspect "$(docker compose --env-file .env ps -q api)" \
  > evidence/incident-container.json

docker volume inspect atlas-payments-data \
  > evidence/incident-volume.json

docker system df -v \
  > evidence/incident-system-df.txt
```

Každý deštruktívny krok môže odstrániť evidence. Restart zmení process state, recreate zmení container ID, `rm` odstráni inspect object a `prune` môže odstrániť images, cache, networks alebo volumes.

## 35. Cleanup bez náhodnej straty dát

Najprv odstráň Compose containers a network:

```bash
docker compose \
  --env-file .env \
  down \
  --remove-orphans
```

Named volume zostane, pokiaľ nepoužiješ `--volumes` alebo ho neodstrániš samostatne.

Over:

```bash
docker volume inspect atlas-payments-data
```

Keď už dáta nepotrebuješ a máš potvrdený cleanup scope:

```bash
docker volume rm atlas-payments-data
```

Odstráň lokálny image:

```bash
docker image rm "$IMAGE"
```

Odstráň builder iba vtedy, keď nechceš zachovať jeho cache a state:

```bash
docker buildx rm atlas-builder
```

Odstránenie buildera nie je to isté ako odstránenie images z Docker Engine-u alebo registry artifacts.

## 36. Čo má čitateľ po cvičení vedieť vysvetliť

Po prejdení kapitoly má byť zrejmé, prečo Dockerfile, BuildKit graph, image config, image manifest, image index, local image ID, registry digest, container object, process, volume a Compose project nie sú jedna identita.

Čitateľ má vedieť vysvetliť, čo konkrétne dokazujú:

```text
go test
docker buildx build --target test
docker buildx build --load
docker image inspect
docker export
docker create
docker inspect
docker start
Docker HEALTHCHECK
host curl
Compose verifier
POST/GET po recreate
docker compose config
docker compose up --wait
imagetools inspect
```

Zároveň má vedieť diagnostikovať rozdiel medzi build-context problémom, test stage-om, ktorý sa nevykonal, chybným final image-om, architecture alebo loader problémom, process crashom, healthy processom s chybným network bindom, volume permission problémom, host port collision, Compose interpolation chybou, mutable tag driftom a persistentným business failure-om.

## Oficiálna dokumentácia

- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [BuildKit](https://docs.docker.com/build/buildkit/)
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [`docker buildx build`](https://docs.docker.com/reference/cli/docker/buildx/build/)
- [Running containers](https://docs.docker.com/engine/containers/run/)
- [Docker storage volumes](https://docs.docker.com/engine/storage/volumes/)
- [Docker networking](https://docs.docker.com/engine/network/)
- [Compose services](https://docs.docker.com/reference/compose-file/services/)
- [`docker compose config`](https://docs.docker.com/reference/cli/docker/compose/config/)
- [`docker compose up`](https://docs.docker.com/reference/cli/docker/compose/up/)
- [`docker compose down`](https://docs.docker.com/reference/cli/docker/compose/down/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: BuildKit a Buildx](buildkit-buildx.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Docker troubleshooting →](docker-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->