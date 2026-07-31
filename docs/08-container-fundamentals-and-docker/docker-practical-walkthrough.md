# Praktický Docker projekt od Dockerfile-u po overený Compose runtime

Táto kapitola skladá hlavné concepts sekcie Container Fundamentals and Docker do jedného malého, ale uceleného projektu. Vytvoríme HTTP službu `payments-api`, zostavíme ju cez multi-stage Dockerfile, otestujeme BuildKit graph, vytvoríme lokálny aj multi-platform release image, spustíme container s obmedzenými privileges, pripojíme named volume, publikujeme port iba na loopback, poskladáme Compose project a overíme process, health, network, data aj business outcome.

Nejde o katalóg príkazov. Celý walkthrough sleduje jeden subject:

```text
versionovaný source a Dockerfile
→ build context inventory
→ Dockerfile frontend a stage graph
→ test a platform-specific build
→ image config, layers a digest
→ constrained container create/start
→ mounts, namespace, network a PID 1
→ health a loaded configuration
→ Compose resolved model a project identity
→ data-persistence a service-discovery verification
→ immutable registry publication
→ second run, update a recovery closure
```

Každý zelený krok má inú dôkazovú hranicu. `docker build` nepreukazuje, že test stage bol vykonaný. Image digest nepreukazuje runtime zdravie. `docker ps` nepreukazuje application readiness. Docker healthcheck nepreukazuje business correctness. `docker compose up --wait` nepreukazuje, že persistentné dáta prežijú recreate. Preto budeme pri každom kroku hovoriť, čo príkaz preukazuje a čo ešte nie.

## 1. Výsledná štruktúra projektu

Vytvor adresáre:

```bash
mkdir -p atlas-payments-docker/cmd/payments-api
mkdir -p atlas-payments-docker/scripts
cd atlas-payments-docker
```

Výsledná štruktúra bude:

```text
atlas-payments-docker/
├── .dockerignore
├── Dockerfile
├── compose.yaml
├── env.example
├── go.mod
├── cmd/
│   └── payments-api/
│       ├── main.go
│       └── main_test.go
└── scripts/
    ├── verify-image.sh
    ├── verify-compose.sh
    └── inspect-runtime.sh
```

Tento source tree ešte nie je image ani container. Exact build subject vznikne až kombináciou:

```text
source commit
+ Dockerfile a frontend identity
+ context inventory a .dockerignore
+ base-image subjects
+ build args
+ target stage
+ target platform
+ builder/BuildKit identity
+ cache inputs
+ exporter
```

Runtime subject navyše pridá image digest, Docker context a daemon, container config, user, capabilities, cgroup limits, mounts, networks, environment a konkrétnu process generation.

## 2. `go.mod`: minimálny application contract

Vytvor `go.mod`:

```go
module example.com/atlas/payments-api

go 1.24
```

Aplikácia nepoužíva externé Go modules. To zjednodušuje walkthrough, ale nemení hlavný supply-chain model. Pri reálnych dependencies musí byť `go.mod`, `go.sum`, proxy alebo repository snapshot a dependency policy súčasťou build subjectu.

## 3. Aplikácia: process, health, readiness a persistentný business údaj

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

func requiredEnvironment(name string) (string, error) {
    value, exists := os.LookupEnv(name)
    if !exists || strings.TrimSpace(value) == "" {
        return "", fmt.Errorf("required environment variable %s is missing or empty", name)
    }
    return value, nil
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
    if strings.TrimSpace(value.ID) == "" {
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

    encoder := json.NewEncoder(file)
    if err := encoder.Encode(value); err != nil {
        return fmt.Errorf("append payment: %w", err)
    }
    return file.Sync()
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
            "hostname":          hostname(),
        })
    })

    mux.HandleFunc("POST /payments", func(writer http.ResponseWriter, request *http.Request) {
        defer request.Body.Close()

        var value payment
        decoder := json.NewDecoder(http.MaxBytesReader(writer, request.Body, 64*1024))
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

func hostname() string {
    value, err := os.Hostname()
    if err != nil {
        return "unknown"
    }
    return value
}

func serve() error {
    configGeneration, err := requiredEnvironment("CONFIG_GENERATION")
    if err != nil {
        return err
    }

    listenAddress := os.Getenv("LISTEN_ADDRESS")
    if listenAddress == "" {
        listenAddress = ":8080"
    }

    dataPath := os.Getenv("DATA_PATH")
    if dataPath == "" {
        dataPath = "/var/lib/atlas-payments/payments.jsonl"
    }

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
        ReadTimeout:       10 * time.Second,
        WriteTimeout:      10 * time.Second,
        IdleTimeout:       60 * time.Second,
    }

    signals := make(chan os.Signal, 1)
    signal.Notify(signals, syscall.SIGINT, syscall.SIGTERM)

    go func() {
        received := <-signals
        log.Printf("received signal %s; beginning graceful shutdown", received)

        context, cancel := context.WithTimeout(context.Background(), 10*time.Second)
        defer cancel()

        if err := server.Shutdown(context); err != nil {
            log.Printf("graceful shutdown failed: %v", err)
        }
    }()

    log.Printf(
        "starting payments-api version=%s commit=%s config_generation=%s address=%s data_path=%s",
        version,
        commit,
        configGeneration,
        listenAddress,
        dataPath,
    )

    err = server.ListenAndServe()
    if errors.Is(err, http.ErrServerClosed) {
        return nil
    }
    return err
}

func healthcheck() error {
    endpoint := os.Getenv("HEALTHCHECK_URL")
    if endpoint == "" {
        endpoint = "http://127.0.0.1:8080/readyz"
    }

    client := http.Client{Timeout: 2 * time.Second}
    response, err := client.Get(endpoint)
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
        err = serve()
    case "healthcheck":
        err = healthcheck()
    default:
        err = fmt.Errorf("unknown command %q", command)
    }

    if err != nil {
        log.Fatal(err)
    }
}
```

Dôležité runtime vlastnosti:

- aplikácia ostáva PID 1, takže priamo prijíma `SIGTERM`;
- shutdown používa bounded desaťsekundový context;
- `/healthz` testuje iba živý process;
- `/readyz` testuje, či process dokáže používať zapisovateľný data path;
- `/version` publikuje build a configuration generation;
- POST zapisuje business údaj a vykoná `fsync` cez `file.Sync()`;
- GET overuje, že údaj možno po neskoršom recreate znovu načítať.

Ani úspešný `file.Sync()` nie je databázová transakcia ani cross-host durability. Pre walkthrough však vytvára konkrétny persistentný outcome, ktorý vieme overiť oddelene od lifecycle-u containeru.

## 4. Unit test

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

func TestPaymentRoundTrip(t *testing.T) {
    t.Parallel()

    app := application{
        dataPath:         filepath.Join(t.TempDir(), "payments.jsonl"),
        configGeneration: "test-generation",
    }

    createRequest := httptest.NewRequest(
        http.MethodPost,
        "/payments",
        strings.NewReader(`{"id":"pay-100","amount":1250,"currency":"EUR"}`),
    )
    createResponse := httptest.NewRecorder()
    app.routes().ServeHTTP(createResponse, createRequest)

    if createResponse.Code != http.StatusCreated {
        t.Fatalf("expected create status %d, got %d: %s", http.StatusCreated, createResponse.Code, createResponse.Body.String())
    }

    readRequest := httptest.NewRequest(http.MethodGet, "/payments/pay-100", nil)
    readResponse := httptest.NewRecorder()
    app.routes().ServeHTTP(readResponse, readRequest)

    if readResponse.Code != http.StatusOK {
        t.Fatalf("expected read status %d, got %d: %s", http.StatusOK, readResponse.Code, readResponse.Body.String())
    }
    if !strings.Contains(readResponse.Body.String(), `"id":"pay-100"`) {
        t.Fatalf("response does not contain persisted payment: %s", readResponse.Body.String())
    }
}

func TestRejectsNonPositiveAmount(t *testing.T) {
    t.Parallel()

    app := application{
        dataPath:         filepath.Join(t.TempDir(), "payments.jsonl"),
        configGeneration: "test-generation",
    }

    request := httptest.NewRequest(
        http.MethodPost,
        "/payments",
        strings.NewReader(`{"id":"pay-invalid","amount":0,"currency":"EUR"}`),
    )
    response := httptest.NewRecorder()
    app.routes().ServeHTTP(response, request)

    if response.Code != http.StatusUnprocessableEntity {
        t.Fatalf("expected status %d, got %d", http.StatusUnprocessableEntity, response.Code)
    }
}
```

Happy-path test preukazuje zápis a následné načítanie cez application handler. Forbidden test preukazuje, že nulová suma je skutočne odmietnutá. Ani jeden test nepreukazuje container user, volume permissions, signal handling alebo network path.

## 5. `.dockerignore`: build-context boundary

Vytvor `.dockerignore`:

```dockerignore
.git
.gitignore
.env
.env.*
!env.example

*.log
*.tmp
coverage/
dist/

payments-data/
secrets/

Dockerfile*
compose*.yaml
README.md
```

Posledné tri patterns sú pedagogická voľba: Dockerfile a Compose model nepotrebujeme kopírovať do image filesystemu. Dockerfile sa stále používa ako build definition; `.dockerignore` iba obmedzí files dostupné `COPY` instructions.

Skontroluj context inventory ešte pred buildom:

```bash
find . -type f -print | sort
```

V reálnom CI vytvor explicitný manifest a porovnaj ho s policy. `.dockerignore` znižuje riziko, že do build contextu vstúpi `.git`, `.env`, local secret alebo veľký data adresár. Nezaručuje, že povolené files neobsahujú secret.

## 6. Multi-stage Dockerfile

Vytvor `Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1

ARG GO_IMAGE=golang:1.24-alpine
ARG RUNTIME_IMAGE=gcr.io/distroless/static-debian12:nonroot

FROM ${GO_IMAGE} AS source
WORKDIR /src

COPY go.mod ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

COPY cmd ./cmd

FROM source AS test
RUN --mount=type=cache,target=/root/.cache/go-build \
    go test ./...

FROM source AS build
ARG TARGETOS
ARG TARGETARCH
ARG VERSION=dev
ARG VCS_REF=unknown

RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 \
    GOOS=${TARGETOS:-linux} \
    GOARCH=${TARGETARCH:-amd64} \
    go build \
      -trimpath \
      -ldflags "-s -w -X main.version=${VERSION} -X main.commit=${VCS_REF}" \
      -o /out/payments-api \
      ./cmd/payments-api

FROM ${RUNTIME_IMAGE} AS runtime

COPY --from=build --chown=65532:65532 \
    /out/payments-api \
    /usr/local/bin/payments-api

USER 65532:65532
WORKDIR /home/nonroot

ENV LISTEN_ADDRESS=:8080 \
    DATA_PATH=/var/lib/atlas-payments/payments.jsonl \
    HEALTHCHECK_URL=http://127.0.0.1:8080/readyz

EXPOSE 8080

HEALTHCHECK \
  --interval=10s \
  --timeout=3s \
  --start-period=5s \
  --retries=3 \
  CMD ["/usr/local/bin/payments-api", "healthcheck"]

ENTRYPOINT ["/usr/local/bin/payments-api"]
CMD ["serve"]
```

### Čo jednotlivé stages znamenajú

```text
source
→ načíta build inputs a zdrojový kód

test
→ vykoná Go tests nad source stage

build
→ vytvorí platform-specific statický binary artifact

runtime
→ obsahuje iba runtime binary a image metadata
```

Final runtime image neobsahuje Go compiler ani source tree. To zmenšuje attack surface, ale nepreukazuje, že final stage pochádza z testovaného graphu. Release workflow musí explicitne vykonať `test` target a až následne `runtime` target nad rovnakým source subjectom.

### Base image tags verzus digesty

Ukážka používa čitateľné tags. Pred produkčným použitím ich nahraď schválenými digest references, napríklad:

```dockerfile
ARG GO_IMAGE=golang:1.24-alpine@sha256:<verified-builder-manifest-digest>
ARG RUNTIME_IMAGE=gcr.io/distroless/static-debian12:nonroot@sha256:<verified-runtime-manifest-digest>
```

Tag je mutable discovery pointer. Digest identifikuje konkrétny manifest. Digest pinning však nenahrádza pravidelný update a vulnerability-remediation lifecycle.

## 7. Overenie Docker contextu, buildera a toolchainu

Pred buildom:

```bash
docker context show
docker version
docker buildx version
docker buildx ls
docker buildx inspect --bootstrap
```

Tieto outputs preukazujú, ktorý CLI context a builder sú aktuálne selected, aký driver používajú a ktoré platforms worker deklaruje. Nepreukazujú, že builder je dôveryhodný, čistý alebo že cache pochádza zo schváleného trust domainu.

Build subject si môžeš zachytiť:

```bash
git rev-parse HEAD
sha256sum Dockerfile .dockerignore go.mod
find cmd -type f -print0 | sort -z | xargs -0 sha256sum
```

Na Windows PowerShell môžeš použiť:

```powershell
Get-FileHash Dockerfile, .dockerignore, go.mod -Algorithm SHA256
Get-ChildItem cmd -Recurse -File |
    Sort-Object FullName |
    Get-FileHash -Algorithm SHA256
```

## 8. Vykonanie test stage-u

Spusti test stage priamo:

```bash
docker buildx build \
  --target test \
  --progress=plain \
  --output=type=cacheonly \
  .
```

Očakávaná relevantná časť outputu:

```text
# ... RUN go test ./...
# ... DONE
```

`--output=type=cacheonly` znamená, že výsledkom nie je runtime image exportovaný do Docker Engine alebo registry. Build preukazuje, že reachable graph pre target `test` skončil úspešne. Nepreukazuje final image, platform-specific runtime ani to, že neskorší release build použije rovnaký source a base-image subject.

Zámerne rozbi test, napríklad zmeň expected HTTP status. Test target musí zlyhať. Tento forbidden experiment overuje, že pipeline skutočne vykonáva test stage a nereportuje pass iba preto, že stage existuje v Dockerfile.

## 9. Lokálny single-platform runtime build

Pre lokálny runtime test vytvor image pre platformu aktuálneho Engine-u:

```bash
VERSION=1.0.0
VCS_REF="$(git rev-parse --short=12 HEAD)"

DOCKER_BUILDKIT=1 docker buildx build \
  --target runtime \
  --platform linux/amd64 \
  --build-arg VERSION="$VERSION" \
  --build-arg VCS_REF="$VCS_REF" \
  --tag atlas/payments-api:${VERSION}-local \
  --load \
  .
```

`--load` importuje single-platform result do selected Docker Engine image store. Pri multi-platform requeste sa typicky používa registry exporter cez `--push`; classic local image store nemusí vedieť načítať celý multi-platform index.

Získaj local image ID a repo digest:

```bash
docker image inspect atlas/payments-api:${VERSION}-local \
  --format '{{json .Id}} {{json .RepoDigests}}'
```

Local image ID identifikuje image config v danom Engine store. Repo digest môže byť prázdny, kým image nebol pullnutý alebo pushnutý pod registry repository subjectom.

## 10. Image config, history a filesystem contract

Skontroluj effective runtime metadata:

```bash
docker image inspect atlas/payments-api:${VERSION}-local \
  --format '{{json .Config}}' |
  jq '{User,Entrypoint,Cmd,Env,ExposedPorts,Healthcheck,WorkingDir}'
```

Očakávaj približne:

```json
{
  "User": "65532:65532",
  "Entrypoint": ["/usr/local/bin/payments-api"],
  "Cmd": ["serve"],
  "ExposedPorts": {"8080/tcp": {}},
  "WorkingDir": "/home/nonroot"
}
```

Tento read-back preukazuje image config. Runtime môže `USER`, command, environment, healthcheck alebo mounts prepísať.

Pozri history:

```bash
docker history \
  --no-trunc \
  atlas/payments-api:${VERSION}-local
```

History pomáha odhaliť instructions a veľké layers. Nie je kompletný provenance alebo secret scanner. Build secret sa môže dostať do generated file-u aj vtedy, keď command text secret priamo neukazuje.

Exportuj a skontroluj obsah image-u bez spustenia:

```bash
container_id="$(docker create atlas/payments-api:${VERSION}-local)"
docker export "$container_id" | tar -tf - | sort | head -100
docker rm "$container_id"
```

Tento príkaz ukazuje merged root filesystem konkrétneho created containeru. Nepreukazuje runtime mounts, writable-layer changes ani obsah image manifest attestations.

## 11. Prvý constrained `docker run`

Vytvor named volume:

```bash
docker volume create atlas-payments-data
```

Named volume na Linux Engine typicky vznikne s root-owned root directory. Aplikácia používa UID/GID `65532`, preto pred prvým runom nastav ownership cez bounded initializer:

```bash
docker run --rm \
  --mount type=volume,source=atlas-payments-data,target=/data \
  busybox:1.36.1 \
  sh -ec 'mkdir -p /data && chown -R 65532:65532 /data'
```

Initializer mení iba obsah named volume-u pripojeného na `/data`. Stále je to privileged mutation vzhľadom na dáta a musí používať schválený image subject. V produkcii môže volume ownership pripraviť storage provisioner alebo init workflow.

Spusti aplikáciu:

```bash
docker run --detach \
  --name atlas-payments-api \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --cap-drop ALL \
  --security-opt no-new-privileges=true \
  --memory 128m \
  --cpus 0.50 \
  --pids-limit 100 \
  --mount type=volume,source=atlas-payments-data,target=/var/lib/atlas-payments \
  --publish 127.0.0.1:18080:8080 \
  --env CONFIG_GENERATION=cfg-1 \
  atlas/payments-api:${VERSION}-local
```

### Čo runtime flags robia

```text
--read-only
→ image root filesystem sa mountne read-only

--tmpfs /tmp
→ explicitne poskytne ephemeral writable path

--cap-drop ALL
→ odoberie default Linux capabilities

no-new-privileges
→ process a descendants nemajú cez execve získať nové privileges

--memory, --cpus, --pids-limit
→ vytvoria cgroup resource boundary podľa podpory hosta

named volume
→ dáta majú lifecycle oddelený od container writable layeru

127.0.0.1:18080:8080
→ host listener je dostupný iba cez loopback adresu hosta
```

Runtime command success preukazuje, že Docker Engine prijal create/start request. Nepreukazuje health, loaded generation, volume zápis ani dostupnosť z očakávaného client pathu.

## 12. Container state, PID 1 a effective runtime config

```bash
docker container inspect atlas-payments-api > container-inspect.json

jq '.[0] | {
  Id,
  Image,
  Path,
  Args,
  State,
  Config: {
    User: .Config.User,
    Env: .Config.Env,
    Entrypoint: .Config.Entrypoint,
    Cmd: .Config.Cmd,
    Healthcheck: .Config.Healthcheck
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
  NetworkSettings: .NetworkSettings.Ports
}' container-inspect.json
```

Inspect je authoritative pre Docker Engine object configuration a observed state v čase requestu. Nepreukazuje, že kernel enforcement je bez chyby alebo že process skutočne načítal každú environment hodnotu.

Over PID 1:

```bash
docker top atlas-payments-api -eo pid,ppid,user,args
```

Očakávaj application binary ako jediný hlavný process. Ak by shell wrapper zostal PID 1 bez `exec`, signal a exit-code semantics by boli odlišné.

## 13. Healthcheck a jeho hranica

Sleduj health:

```bash
for attempt in $(seq 1 30); do
  status="$(docker inspect atlas-payments-api --format '{{.State.Health.Status}}')"
  printf 'attempt=%s health=%s\n' "$attempt" "$status"
  [ "$status" = "healthy" ] && break
  sleep 1
done
```

Pozri posledné checks:

```bash
docker inspect atlas-payments-api \
  --format '{{json .State.Health.Log}}' |
  jq 'map({Start,End,ExitCode,Output})'
```

`healthy` preukazuje, že application binary vo vnútri container namespace-u dokázal zavolať `/readyz` a dostať HTTP 200 v rámci health policy. Neoveruje host port, service discovery, persisted business údaj ani external klienta.

## 14. Host-port a configuration-generation read-back

```bash
curl --fail --silent --show-error \
  http://127.0.0.1:18080/version |
  jq .
```

Očakávaj:

```json
{
  "service": "payments-api",
  "version": "1.0.0",
  "commit": "<current-short-commit>",
  "config_generation": "cfg-1",
  "hostname": "<container-hostname>"
}
```

Tento request prejde host loopback listenerom, Docker port-publishing pathom, container network namespace-om a application socketom. Nepreukazuje dostupnosť z iného hosta, pretože listener je zámerne bindnutý na `127.0.0.1`.

Skontroluj published port:

```bash
docker port atlas-payments-api
```

`EXPOSE 8080` v image by sám host port nevytvoril. Publishing vznikol až runtime flagom.

## 15. Business write/read a persistentný outcome

Vytvor payment:

```bash
curl --fail --silent --show-error \
  --request POST \
  --header 'Content-Type: application/json' \
  --data '{"id":"pay-100","amount":1250,"currency":"EUR"}' \
  http://127.0.0.1:18080/payments |
  jq .
```

Načítaj ho:

```bash
curl --fail --silent --show-error \
  http://127.0.0.1:18080/payments/pay-100 |
  jq .
```

Táto dvojica preukazuje application-level write/read cez publikovaný port a aktuálny process. Stále nepreukazuje, že dáta prežijú replacement containeru.

Pozri volume mount identity:

```bash
docker volume inspect atlas-payments-data | jq .
```

Volume inspect preukazuje Docker volume object, driver, labels a host mountpoint pri lokálnom Engine-i. Neznamená application-consistent backup ani portability na iný host.

## 16. Recreate bez straty dát

Odstráň iba container:

```bash
docker rm --force atlas-payments-api
```

Volume zostáva:

```bash
docker volume ls --filter name=atlas-payments-data
```

Spusti novú container generation s rovnakým image-om a volume-om:

```bash
docker run --detach \
  --name atlas-payments-api \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --cap-drop ALL \
  --security-opt no-new-privileges=true \
  --memory 128m \
  --cpus 0.50 \
  --pids-limit 100 \
  --mount type=volume,source=atlas-payments-data,target=/var/lib/atlas-payments \
  --publish 127.0.0.1:18080:8080 \
  --env CONFIG_GENERATION=cfg-1 \
  atlas/payments-api:${VERSION}-local
```

Po health transition znovu načítaj:

```bash
curl --fail --silent \
  http://127.0.0.1:18080/payments/pay-100 |
  jq -e '.id == "pay-100" and .amount == 1250 and .currency == "EUR"'
```

Exit code `0` preukazuje, že konkrétny business údaj prežil container replacement v rovnakom Docker volume subjecte. Nepreukazuje backup/restore, host failure alebo concurrent-writer safety.

## 17. Graceful stop a signal behavior

Sleduj logs v samostatnom shelli:

```bash
docker logs --follow atlas-payments-api
```

Potom:

```bash
docker stop --time 15 atlas-payments-api
```

Očakávaj log:

```text
received signal terminated; beginning graceful shutdown
```

A state:

```bash
docker inspect atlas-payments-api \
  --format 'status={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}'
```

Expected:

```text
status=exited exit=0 oom=false
```

Tento test preukazuje signal delivery a bounded shutdown pre konkrétnu container generation bez aktívneho request loadu. Nepreukazuje drain behavior pod production trafficom ani dokončenie všetkých in-flight writes.

## 18. `env.example`: interpolation inputs bez secretov

Vytvor `env.example`:

```dotenv
COMPOSE_PROJECT_NAME=atlas-payments-dev
PAYMENTS_IMAGE=atlas/payments-api:1.0.0-local
CONFIG_GENERATION=cfg-compose-1
HOST_PORT=18080
```

Skopíruj ho pre lokálny run:

```bash
cp env.example .env
```

`.env` je Compose CLI interpolation source. Nie je automaticky bezpečný secret store a podľa `.dockerignore` ani nemá vstúpiť do build contextu.

## 19. Kompletný `compose.yaml`

Vytvor `compose.yaml`:

```yaml
name: ${COMPOSE_PROJECT_NAME:-atlas-payments-dev}

services:
  init-data:
    image: busybox:1.36.1
    command:
      - sh
      - -ec
      - |
        mkdir -p /data
        chown -R 65532:65532 /data
    user: "0:0"
    restart: "no"
    volumes:
      - type: volume
        source: payments-data
        target: /data
    networks:
      - backend

  api:
    image: ${PAYMENTS_IMAGE:?PAYMENTS_IMAGE must identify the runtime image}
    build:
      context: .
      dockerfile: Dockerfile
      target: runtime
      args:
        VERSION: ${APP_VERSION:-1.0.0}
        VCS_REF: ${VCS_REF:-local}
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
    restart: unless-stopped
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
      test: ["CMD", "/usr/local/bin/payments-api", "healthcheck"]
      interval: 10s
      timeout: 3s
      start_period: 5s
      retries: 3

  verifier:
    image: busybox:1.36.1
    profiles: ["verify"]
    depends_on:
      api:
        condition: service_healthy
    command:
      - sh
      - -ec
      - |
        payload="$(wget -qO- http://payments-api:8080/version)"
        printf '%s\n' "$payload"
        printf '%s\n' "$payload" | grep -F '"service":"payments-api"'
        printf '%s\n' "$payload" | grep -F '"config_generation":"${CONFIG_GENERATION}"'
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

### Prečo sú tu dva lifecycle owners

`api` container je Compose-managed a môže byť recreated. Volume má explicitné meno `atlas-payments-data`, takže jeho data identity nie je odvodená iba z aktuálneho project name-u. Compose ho však stále pozná ako declared volume a `docker compose down --volumes` ho môže odstrániť. Produkčný data volume môže byť vhodné označiť `external: true` a spravovať samostatným ownerom.

### `depends_on` hranica

`service_completed_successfully` zabezpečí, že `init-data` skončí exit code `0` pred vytvorením dependent service. `service_healthy` pri verifieri čaká na Docker health verdict API služby. Tieto podmienky riadia create/start ordering; neposkytujú nepretržitú dependency resilience po štarte.

## 20. Resolved Compose model

Pred mutation nastav inputs:

```bash
export APP_VERSION=1.0.0
export VCS_REF="$(git rev-parse --short=12 HEAD)"
```

Zobraz interpolation environment:

```bash
docker compose --env-file .env config --environment
```

Vyrenderuj canonical model:

```bash
docker compose --env-file .env config > compose.resolved.yaml
```

Získaj inventories:

```bash
docker compose --env-file .env config --services
docker compose --env-file .env config --images
docker compose --env-file .env config --networks
docker compose --env-file .env config --volumes
docker compose --env-file .env config --profiles
```

`docker compose config` merge-ne a resolve-ne Compose model, interpolation a short syntax. Je to výrazne silnejší review subject než samotný source fragment. Stále nepreukazuje, že images existujú, ports sú voľné alebo runtime mutation uspeje.

Kontroluj explicitné forbidden hodnoty:

```bash
yq -e '.services.api.privileged != true' compose.resolved.yaml
yq -e '.services.api.read_only == true' compose.resolved.yaml
yq -e '.services.api.ports[0].host_ip == "127.0.0.1"' compose.resolved.yaml
yq -e '.services.api.volumes[0].type == "volume"' compose.resolved.yaml
```

Policy musí čítať resolved model. Bezpečný base file môže byť neskôr prepísaný override súborom alebo environment interpolation.

## 21. Compose dry-run a resource plan

Aktuálny Compose CLI podporuje dry-run pre mnohé commands:

```bash
docker compose \
  --env-file .env \
  --dry-run \
  up --build --wait --wait-timeout 120
```

Dry-run ukazuje plánované Engine operations bez vykonania podporovaných mutations. Je to prediction, nie transakčný plán ani záruka, že race, pull alebo create operation neskôr uspeje.

Pred prvým `up` zaznamenaj current resources:

```bash
docker ps --all --filter label=com.docker.compose.project=atlas-payments-dev
docker network ls --filter label=com.docker.compose.project=atlas-payments-dev
docker volume ls --filter name=atlas-payments-data
```

Tým oddelíš pre-existing resources od výsledku nového project reconciliation.

## 22. Compose build a bounded startup

Spusti:

```bash
docker compose \
  --env-file .env \
  up \
  --build \
  --wait \
  --wait-timeout 120 \
  --remove-orphans
```

`--wait` čaká, kým services dosiahnu running alebo healthy podľa dostupného health modelu. `--remove-orphans` môže zmazať staré containers s rovnakou project identity, ktoré už nie sú v modelu. Preto project name a orphan policy patria do destructive-scope reviewu.

Skontroluj project:

```bash
docker compose --env-file .env ps --all
docker compose --env-file .env images
docker compose --env-file .env top
docker compose --env-file .env logs --no-color --timestamps api
```

Compose command success preukazuje, že requested reconciliation skončil podľa Compose/Engine verdictu. Nepreukazuje business write/read ani persistence po recreate.

## 23. Service discovery vo vnútri user-defined networku

Spusti verifier profile:

```bash
docker compose \
  --env-file .env \
  --profile verify \
  run --rm verifier
```

Verifier používa DNS alias `payments-api` v networku `backend`. Nepoužíva host published port. Tým testuje:

```text
verifier network namespace
→ embedded DNS/service alias
→ api container IP
→ container port 8080
→ application /version
```

Neoveruje host NAT/publishing path. Ten overuje samostatný `curl 127.0.0.1:18080`.

Pozri network object:

```bash
docker network inspect atlas-payments-dev_backend | jq .
```

Network inspect ukazuje attached endpoints, aliases a IPAM state v čase requestu. Nezaručuje packet delivery pri firewall, MTU alebo conntrack probléme.

## 24. Compose business a persistence test

Vytvor druhý payment:

```bash
curl --fail --silent \
  --request POST \
  --header 'Content-Type: application/json' \
  --data '{"id":"pay-compose-1","amount":9900,"currency":"EUR"}' \
  http://127.0.0.1:18080/payments |
  jq .
```

Recreate-ni iba API container:

```bash
docker compose --env-file .env up \
  --detach \
  --no-deps \
  --force-recreate \
  api
```

Po health transition:

```bash
curl --fail --silent \
  http://127.0.0.1:18080/payments/pay-compose-1 |
  jq -e '.id == "pay-compose-1" and .amount == 9900'
```

Toto preukazuje, že Compose service replacement zachoval declared named volume a business údaj. Neoveruje host-loss recovery ani volume backup.

## 25. Runtime hardening read-back

Vytvor `scripts/inspect-runtime.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

container_id="$(docker compose --env-file .env ps -q api)"
test -n "$container_id"

docker inspect "$container_id" |
jq -e '.[0]
  | .Config.User == "65532:65532"
  and .HostConfig.ReadonlyRootfs == true
  and (.HostConfig.CapDrop | index("ALL") != null)
  and (.HostConfig.SecurityOpt | index("no-new-privileges:true") != null)
  and .HostConfig.PidsLimit == 100
  and .HostConfig.Memory == 134217728
  and (.NetworkSettings.Ports["8080/tcp"][0].HostIp == "127.0.0.1")
'
```

Nastav executable bit:

```bash
chmod +x scripts/inspect-runtime.sh
./scripts/inspect-runtime.sh
```

Tento script overuje effective Engine configuration, nie iba Compose source. Nepreukazuje kernel-level enforcement ani host security posture.

## 26. Kompletný Compose verifier

Vytvor `scripts/verify-compose.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

compose=(docker compose --env-file .env)

"${compose[@]}" config --quiet
"${compose[@]}" ps --status running --services | grep -Fx api

container_id="$("${compose[@]}" ps -q api)"
test -n "$container_id"

test "$(docker inspect "$container_id" --format '{{.State.Health.Status}}')" = healthy

version_payload="$(curl --fail --silent http://127.0.0.1:18080/version)"
printf '%s\n' "$version_payload" | jq -e '
  .service == "payments-api"
  and .config_generation == "cfg-compose-1"
'

curl --fail --silent \
  http://127.0.0.1:18080/payments/pay-compose-1 |
  jq -e '.id == "pay-compose-1"'

"${compose[@]}" --profile verify run --rm verifier

./scripts/inspect-runtime.sh
```

Tento script spája configured, effective, health, network a business evidence. Stále nie je production SLO test ani backup/restore test.

## 27. Second `compose up` ako reconciliation test

Zachyť container ID a start time:

```bash
before_id="$(docker compose --env-file .env ps -q api)"
before_started="$(docker inspect "$before_id" --format '{{.State.StartedAt}}')"
```

Spusti rovnaký command druhýkrát:

```bash
docker compose --env-file .env up --wait --wait-timeout 120
```

Porovnaj:

```bash
after_id="$(docker compose --env-file .env ps -q api)"
after_started="$(docker inspect "$after_id" --format '{{.State.StartedAt}}')"

printf 'before_id=%s after_id=%s\n' "$before_id" "$after_id"
printf 'before_started=%s after_started=%s\n' "$before_started" "$after_started"

test "$before_id" = "$after_id"
```

Rovnaký ID preukazuje, že Compose pri nezmenenom resolved model-e container nerecreate-ol. Neznamená, že neskorší manual drift alebo mutable image tag nebude problém.

## 28. Controlled configuration update

Zmeň `.env`:

```dotenv
CONFIG_GENERATION=cfg-compose-2
```

Pred mutation zobraz nový resolved model a service hash:

```bash
docker compose --env-file .env config --hash api
docker compose --env-file .env config > compose.resolved.cfg-2.yaml
```

Aplikuj update:

```bash
docker compose --env-file .env up --wait --wait-timeout 120
```

Compose má recreate-nuť API container, pretože effective environment sa zmenil. Volume ostane.

Over:

```bash
curl --fail --silent http://127.0.0.1:18080/version |
  jq -e '.config_generation == "cfg-compose-2"'

curl --fail --silent http://127.0.0.1:18080/payments/pay-compose-1 |
  jq -e '.id == "pay-compose-1"'
```

Tým oddelíš configuration generation transition od data lifecycle-u.

## 29. Multi-platform release build a registry publication

Lokálny Engine testoval jednu platformu. Release build vytvorí `linux/amd64` a `linux/arm64` image graph:

```bash
REGISTRY=registry.example.com
REPOSITORY=atlas/payments-api
VERSION=1.0.0
VCS_REF="$(git rev-parse HEAD)"

IMAGE_REF="${REGISTRY}/${REPOSITORY}:${VERSION}"

docker buildx build \
  --builder atlas-release \
  --target runtime \
  --platform linux/amd64,linux/arm64 \
  --build-arg VERSION="$VERSION" \
  --build-arg VCS_REF="$VCS_REF" \
  --tag "$IMAGE_REF" \
  --provenance=mode=max \
  --sbom=true \
  --push \
  .
```

`--push` exportuje result do registry. `--provenance` a `--sbom` pridajú attestations podľa builder a registry supportu. Build success nepreukazuje, že registry read-back obsahuje obe platformy a správne attestations.

Read-back:

```bash
docker buildx imagetools inspect "$IMAGE_REF"
```

Získaj immutable digest:

```bash
INDEX_DIGEST="$(docker buildx imagetools inspect "$IMAGE_REF" --format '{{json .Manifest}}' | jq -r '.digest')"
printf 'index_digest=%s\n' "$INDEX_DIGEST"
```

Presný format outputu závisí od Buildx version; release script musí mať testovaný parser a zlyhať pri nečakanom schema-e.

Over platform inventory:

```bash
docker buildx imagetools inspect "$IMAGE_REF" --raw |
jq -e '
  [.manifests[].platform | (.os + "/" + .architecture)]
  | sort
  == ["linux/amd64", "linux/arm64"]
'
```

Tento gate preukazuje descriptors pre obe platforms v indexe. Nepreukazuje, že binary v každom manifeste je spustiteľný. Potrebuješ native alebo dôveryhodný platform runtime test.

## 30. Digest-pinned consumption

Production Compose input nemá používať mutable tag:

```bash
export PAYMENTS_IMAGE="${REGISTRY}/${REPOSITORY}@${INDEX_DIGEST}"
export CONFIG_GENERATION=cfg-release-1
export COMPOSE_PROJECT_NAME=atlas-payments-release
```

Skontroluj resolved image:

```bash
docker compose config --images
```

Potom:

```bash
docker compose pull api
docker compose up --no-build --wait --wait-timeout 120
```

`--no-build` zabraňuje runtime hostu vytvoriť iný artifact z local source. `pull` a `up` musia používať exact digest subject.

Live digest read-back:

```bash
container_id="$(docker compose ps -q api)"
image_id="$(docker inspect "$container_id" --format '{{.Image}}')"
docker image inspect "$image_id" --format '{{json .RepoDigests}}'
```

Production acceptance musí korelovať expected registry digest s live image objectom, nie iba s Compose source alebo tagom.

## 31. `scripts/verify-image.sh`

Vytvor:

```bash
#!/usr/bin/env bash
set -euo pipefail

image_ref="${1:?usage: verify-image.sh IMAGE_REFERENCE}"
expected_user="65532:65532"

config="$(docker image inspect "$image_ref" --format '{{json .Config}}')"

printf '%s\n' "$config" |
jq -e --arg expected_user "$expected_user" '
  .User == $expected_user
  and .Entrypoint == ["/usr/local/bin/payments-api"]
  and .Cmd == ["serve"]
  and .WorkingDir == "/home/nonroot"
  and .ExposedPorts["8080/tcp"] == {}
  and .Healthcheck.Test == ["CMD", "/usr/local/bin/payments-api", "healthcheck"]
'

if docker history --no-trunc "$image_ref" | grep -E '(PASSWORD|TOKEN|SECRET|PRIVATE KEY)'; then
  echo "potential secret-like value found in image history" >&2
  exit 1
fi
```

History regex je sanity check, nie kompletný secret scan. False positives aj false negatives sú možné.

## 32. Build cache correctness a clean-room kontrola

Warm-cache build:

```bash
docker buildx build \
  --target test \
  --progress=plain \
  --output=type=cacheonly \
  .
```

Clean-room build bez importovanej cache:

```bash
docker buildx build \
  --target test \
  --no-cache \
  --progress=plain \
  --output=type=cacheonly \
  .
```

Oba musia prejsť. `--no-cache` obchádza bežný instruction cache reuse, ale stále môže používať mutable network dependencies, base resolution alebo BuildKit-internal content stores. Reproducibility vyžaduje viac než jeden flag.

Pri external cache oddeľ:

```text
untrusted PR cache
protected branch cache
release cache
```

Untrusted job nesmie zapisovať do cache subjectu, ktorý release builder importuje ako trusted result bez ďalšej validácie.

## 33. Failure walkthrough: aplikácia počúva iba na loopbacku containeru

Zmeň:

```dotenv
LISTEN_ADDRESS=127.0.0.1:8080
```

V container network namespace-e bude `/readyz` fungovať, pretože healthcheck používa `127.0.0.1`. Host published port však môže zlyhať, pretože NAT smeruje na container IP a process nepočúva na nej.

Symptómy:

```text
container running
health=healthy
curl z hosta zlyhá
```

Diagnostika:

```bash
docker exec atlas-payments-api /usr/local/bin/payments-api healthcheck
docker port atlas-payments-api
docker inspect atlas-payments-api --format '{{json .NetworkSettings.Networks}}'
```

Distroless image nemá `ss`; použi host/nsenter tooling iba s primeranými privileges alebo spusti debug variant v rovnakom network namespace-e:

```bash
docker run --rm \
  --network container:atlas-payments-api \
  busybox:1.36.1 \
  wget -qO- http://127.0.0.1:8080/version
```

Root cause je bind-address mismatch, nie port-publishing syntax.

## 34. Failure walkthrough: volume ownership

Ak vynecháš initializer, API ako UID `65532` môže zlyhať:

```text
open data file: permission denied
```

Container môže okamžite exitnúť alebo healthcheck zostať unhealthy.

Dôkazy:

```bash
docker compose ps --all
docker compose logs api
docker inspect "$(docker compose ps -q api)" --format '{{json .State}}'
```

Recovery:

```text
zastaviť opakovaný restart loop
→ potvrdiť volume identity
→ skontrolovať ownership na volume mount-e
→ vykonať bounded ownership migration
→ znovu spustiť rovnaký image
→ overiť business data a second run
```

Neopravuj problém spustením celej aplikácie ako root, ak root privilege nie je súčasťou runtime contractu.

## 35. Failure walkthrough: mount obscuring

Bind mount:

```bash
docker run --rm \
  --mount type=bind,source="$PWD/empty",target=/usr/local/bin \
  atlas/payments-api:${VERSION}-local
```

zakryje `/usr/local/bin/payments-api` z image filesystemu. Runtime môže skončiť s `no such file or directory`.

Mount nevymenil image layers; iba zmenil effective mount view containeru. `docker image inspect` bude stále vyzerať správne. Musíš kontrolovať `docker container inspect .Mounts`.

## 36. Failure walkthrough: health je zelený, business write zlyháva

Ak `/healthz` testuje iba process a Docker healthcheck smeruje naň, container môže byť `healthy`, hoci named volume je read-only alebo plný.

```text
GET /healthz → 200
POST /payments → 500/422
```

Preto walkthrough používa `/readyz`, ktorý overuje writable data path. Ani readiness však nemusí overiť disk durability, quota alebo konkrétny business invariant. Finálny verifier musí vykonať actual write/read.

## 37. Failure walkthrough: mutable tag po scan-e

Pipeline skenuje:

```text
registry.example.com/atlas/payments-api:1.0.0 → digest D1
```

Neskôr tag ukazuje na D2. Compose source stále obsahuje `:1.0.0`.

```text
scan evidence patrí D1
→ runtime pullne D2
→ deployment je technicky zelený
→ production artifact nemá scan verdict
```

Recovery:

```text
contain deployment
→ read-back live digest
→ porovnať so scan/provenance subjectom
→ zneplatniť tag-only approval
→ deploynúť exact schválený digest
→ overiť runtime a business outcome
```

## 38. Failure walkthrough: OOM a cgroup evidence

Zníž memory limit pod reálnu potrebu alebo spusti záťaž. Container môže skončiť:

```text
exit=137
oom=true
```

Over:

```bash
docker inspect atlas-payments-api \
  --format 'exit={{.State.ExitCode}} oom={{.State.OOMKilled}} error={{.State.Error}}'

docker events --since 10m --filter container=atlas-payments-api
```

Exit `137` sám osebe nepreukazuje cgroup OOM; môže vzniknúť aj zo `SIGKILL`. Kombinuj Engine state, cgroup/host kernel logs a workload telemetry.

## 39. Failure walkthrough: wrong platform alebo loader

Pri pull/run môže vzniknúť:

```text
no matching manifest for linux/arm64
exec format error
no such file or directory
```

Hypotézy:

```text
H1: image index nemá target platform
H2: descriptor má nesprávnu platform metadata
H3: binary architecture nezodpovedá platforme
H4: dynamic loader alebo shared library chýba
H5: entrypoint path je zakrytý mountom
```

Dôkazy:

```bash
docker buildx imagetools inspect "$IMAGE_REF"
docker image inspect "$IMAGE_REF" --format '{{.Architecture}}/{{.Os}}'
docker inspect <container> --format '{{json .Mounts}}'
```

Pri statickom Go binary a distroless static image znižujeme loader risk, ale platform-specific runtime test zostáva potrebný.

## 40. Troubleshooting decision chain

Keď používateľ hlási „Docker aplikácia nejde“, nezačínaj `docker restart` alebo `docker system prune`. Stabilizuj subject:

```text
Docker context a daemon
container/project identity
image digest a platform
create-time config
current process/exit/health state
mount/data identity
network endpoint a flow
host resource/kernel state
business request
```

Potom formuluj competing hypotheses:

```text
H1 client smeruje na nesprávny Docker context
H2 image pull/build vytvoril nesprávny digest alebo platformu
H3 container create config je stale
H4 PID 1 exitol alebo nereaguje na signals
H5 cgroup OOM/PID/CPU limit blokuje workload
H6 read-only root alebo volume permissions blokujú zápis
H7 process počúva na nesprávnej adrese/porte
H8 bridge/NAT/firewall/MTU/DNS path zlyháva
H9 health oracle je slabší než business outcome
H10 host disk/inodes alebo daemon state sú vyčerpané
```

Discriminating commands:

```bash
docker context show
docker version
docker compose config
docker compose ps --all
docker inspect <container>
docker logs <container>
docker events --since 30m
docker stats --no-stream
docker system df -v
docker network inspect <network>
docker volume inspect <volume>
```

Každý command má konkrétny observation point. Žiadny jednotlivý output nevysvetľuje celý incident.

## 41. Evidence-preserving containment

Pred restart/delete/prune zachovaj:

```bash
mkdir -p incident-evidence

docker inspect atlas-payments-api \
  > incident-evidence/container-inspect.json

docker logs --timestamps atlas-payments-api \
  > incident-evidence/container.log 2>&1

docker events --since 30m --until 0s \
  > incident-evidence/docker-events.log

docker network inspect atlas-payments-dev_backend \
  > incident-evidence/network.json

docker volume inspect atlas-payments-data \
  > incident-evidence/volume.json

docker system df -v \
  > incident-evidence/system-df.txt
```

Ak container stále obsluhuje časť trafficu alebo drží jedinú kópiu dát vo writable layeri, containment musí najprv riešiť exposure a data preservation. Slepé `rm -f` môže odstrániť posledný observation point.

## 42. Bezpečný cleanup

Zastav a odstráň Compose containers a project network, ale zachovaj named volume:

```bash
docker compose --env-file .env down --remove-orphans
```

Default `down` odstráni project containers a networks, no named volume deklarovaný v modeli zostáva, pokiaľ nepoužiješ `--volumes`.

Over:

```bash
docker volume inspect atlas-payments-data
```

Destructive cleanup dát musí byť samostatné rozhodnutie:

```bash
docker volume rm atlas-payments-data
```

Pred tým exportuj alebo zálohuj údaje podľa data policy. `docker system prune -a --volumes` je široký host-level garbage-collection zásah a nepatrí do bežného troubleshooting postupu bez resource inventory a ownership reviewu.

## 43. GitLab pipeline pre Docker release

Referenčný pipeline skeleton:

```yaml
stages:
  - validate
  - test
  - build
  - verify
  - publish

variables:
  IMAGE_REPOSITORY: "$CI_REGISTRY_IMAGE/payments-api"
  BUILDX_BUILDER: atlas-release

validate_source:
  stage: validate
  image: golang:1.24-alpine@sha256:<verified-go-image-digest>
  script:
    - test -z "$(gofmt -l cmd)"
    - go test ./...
    - sha256sum Dockerfile .dockerignore go.mod

container_test_stage:
  stage: test
  tags: [buildkit-untrusted]
  script:
    - docker buildx build --target test --output=type=cacheonly --progress=plain .

build_local_runtime_test:
  stage: verify
  tags: [buildkit-protected]
  script:
    - docker buildx build --target runtime --platform linux/amd64 --load --tag atlas/payments-api:ci-test .
    - ./scripts/verify-image.sh atlas/payments-api:ci-test
    - docker compose --env-file ci.env up --wait --wait-timeout 120
    - ./scripts/verify-compose.sh
  after_script:
    - docker compose --env-file ci.env down --remove-orphans

publish_release:
  stage: publish
  tags: [buildkit-release]
  rules:
    - if: '$CI_COMMIT_TAG =~ /^v[0-9]+\.[0-9]+\.[0-9]+$/'
  script:
    - docker login --username "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY" <<<"$CI_REGISTRY_PASSWORD"
    - docker buildx inspect "$BUILDX_BUILDER" --bootstrap
    - docker buildx build
        --builder "$BUILDX_BUILDER"
        --target runtime
        --platform linux/amd64,linux/arm64
        --build-arg VERSION="${CI_COMMIT_TAG#v}"
        --build-arg VCS_REF="$CI_COMMIT_SHA"
        --tag "$IMAGE_REPOSITORY:$CI_COMMIT_TAG"
        --provenance=mode=max
        --sbom=true
        --push
        .
    - docker buildx imagetools inspect "$IMAGE_REPOSITORY:$CI_COMMIT_TAG"
```

Pipeline musí navyše zachytiť digest do immutable release manifestu a oddeliť registry login od untrusted test jobov. Plaintext Docker socket na shared runneri je privileged platform capability; job s jeho prístupom môže ovládať daemon a často aj host.

## 44. Acceptance matrix

Walkthrough je dokončený iba vtedy, keď vieš preukázať:

```text
SOURCE A BUILD
[ ] context inventory neobsahuje .git, .env, secrets ani data
[ ] builder, Dockerfile frontend, base images a platform sú identifikované
[ ] test target je skutočne vykonaný a forbidden test zlyhá
[ ] runtime image je multi-stage a neobsahuje compiler/source
[ ] image config má non-root user, exec entrypoint a healthcheck
[ ] local single-platform runtime test prejde
[ ] release index obsahuje amd64 aj arm64 descriptors
[ ] registry digest, SBOM a provenance patria rovnakému release subjectu

RUNTIME
[ ] container používa exact image subject
[ ] root filesystem je read-only a explicitné writable paths sú známe
[ ] capabilities, no-new-privileges, memory, CPU a PID limits sú effective
[ ] PID 1 prijíma SIGTERM a skončí exit 0
[ ] healthcheck prejde
[ ] host loopback published port prejde
[ ] container-network DNS alias prejde
[ ] loaded config generation zodpovedá expected generation

DATA A RECONCILIATION
[ ] business POST/GET prejde
[ ] údaj prežije container recreate
[ ] volume identity a ownership sú explicitné
[ ] druhý compose up nerecreate-ne nezmenený service
[ ] configuration update recreate-ne service, ale zachová dáta
[ ] down bez --volumes zachová data volume
[ ] destructive volume cleanup je samostatne autorizovaný

FAILURE A RECOVERY
[ ] loopback bind mismatch je odlíšený od port publishingu
[ ] mount obscuring je odlíšený od chybného image-u
[ ] volume permission failure nevedie k runtime-as-root workaroundu
[ ] green health bez business write je detegovaný
[ ] mutable tag nevie obísť digest-bound evidence
[ ] OOM, platform a loader hypotheses majú diskriminačné dôkazy
[ ] evidence sa zachová pred restart/delete/prune
[ ] recovery overí pôvodný, forbidden aj second-operation outcome
```

## 45. Ako máš tento walkthrough čítať

Jednotlivé príkazy nie sú cieľ. Predstavujú observation alebo mutation points v jednom lifecycle-e:

```text
Dockerfile
→ build program

docker buildx build
→ graph execution a exporter request

image inspect
→ image metadata read-back

docker run / compose up
→ Engine object creation a process start

container inspect
→ effective create-time/runtime state

healthcheck
→ bounded internal oracle

curl cez host a service DNS
→ dve rozdielne network paths

POST/GET po recreate
→ business a persistence oracle

imagetools inspect
→ registry index/platform inventory

second up
→ Compose reconciliation/idempotency evidence
```

Takto sa Docker neučí ako séria príkazov `build`, `run`, `ps` a `rm`. Učí sa ako prechod od source a build graphu cez immutable artifact a kernel-backed runtime boundaries až po overený process, network, data a business outcome.

## Primárne zdroje

- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Docker build overview](https://docs.docker.com/build/concepts/overview/)
- [Buildx build reference](https://docs.docker.com/reference/cli/docker/buildx/build/)
- [Build attestations](https://docs.docker.com/build/metadata/attestations/)
- [Docker container run](https://docs.docker.com/reference/cli/docker/container/run/)
- [Docker storage](https://docs.docker.com/engine/storage/)
- [Docker volumes](https://docs.docker.com/engine/storage/volumes/)
- [Docker networking](https://docs.docker.com/engine/network/)
- [Compose file reference](https://docs.docker.com/reference/compose-file/)
- [Compose services](https://docs.docker.com/reference/compose-file/services/)
- [Compose config](https://docs.docker.com/reference/cli/docker/compose/config/)
- [Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [Compose down](https://docs.docker.com/reference/cli/docker/compose/down/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: BuildKit a Buildx](buildkit-buildx.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Docker troubleshooting →](docker-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
