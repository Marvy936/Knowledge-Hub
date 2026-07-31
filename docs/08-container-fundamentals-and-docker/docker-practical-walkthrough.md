# Praktický Docker release od source zmeny po overený runtime

Docker sa najlepšie chápe vtedy, keď sa image build, registry publication a container runtime neštudujú ako tri oddelené zoznamy príkazov. Sú to nadväzujúce state transitions nad rôznymi objektmi. Dockerfile opisuje build program. BuildKit z neho a z build contextu vytvorí image artifact. Registry uchová manifesty a blobs pod digestmi. Docker Engine z konkrétneho image-u a runtime konfigurácie vytvorí container object a napokon kernel-backed process.

Táto kapitola preto nie je laboratórium, v ktorom budeme po riadkoch programovať ukážkovú aplikáciu. Aplikácia `payments-api` už existuje a má známy contract: počúva na porte `8080`, poskytuje `/healthz`, `/readyz` a `/version`, zapisuje payment záznamy do `/var/lib/atlas-payments/payments.jsonl` a pri ukončení korektne spracuje `SIGTERM`. Na tomto jednom workload-e prejdeme celý Docker lifecycle a pri každom kroku oddelíme deklaráciu, resolved build alebo runtime model, skutočnú mutation a nezávislé overenie výsledku.

## 1. Dominantný source-to-runtime model

Docker release sa má čítať ako jeden reťazec identity a execution hraníc:

```text
source revision a application contract
→ build context a .dockerignore
→ Dockerfile frontend a stage graph
→ test stage a platform-specific build
→ final image config, layers a manifest
→ registry publication pod immutable digestom
→ Docker context a Engine identity
→ container create configuration
→ mounts, network, cgroups a security policy
→ PID 1 a application startup
→ health, loaded configuration a business outcome
→ replacement, persistence a cleanup
```

Každý krok odpovedá na inú otázku. Úspešný `docker buildx build` preukazuje, že builder dokončil reachable build graph a export. Nezaručuje, že test stage bol súčasťou tohto graphu. Image digest identifikuje artifact, ale nepreukazuje jeho správne spustenie. `docker ps` preukazuje Engine process state, nie aplikačnú readiness. Docker healthcheck môže byť zelený, hoci published port, persistentný zápis alebo používateľský request path nefungujú.

Najčastejší Docker omyl preto nie je nesprávny príkaz. Je to zámena vrstiev:

```text
Dockerfile source
≠ vykonaný BuildKit graph
≠ exportovaný image
≠ registry digest
≠ container configuration
≠ bežiaci process
≠ zdravá služba
≠ správny business outcome
```

## 2. Konkrétny release subject

Atlas Payments vydáva verziu `4.6.0`. Release má bežať na `linux/amd64` a `linux/arm64`, v lokálnom Compose prostredí aj neskôr v Kubernetes. Produkčný image musí byť immutable, non-root a bez compiler toolchainu. Root filesystem má byť read-only; zapisovateľný zostane iba explicitný data volume a malý `tmpfs` pre dočasné súbory.

Presne identifikovaný release obsahuje:

```yaml
release:
  service: payments-api
  version: 4.6.0
  sourceSha: 7a9f2c1
  dockerfileSha256: sha256:dockerfile460
  contextInventorySha256: sha256:context460
  dockerfileFrontend: docker/dockerfile:1
  buildkitVersion: v0.26.2
  buildxVersion: v0.29.1
  targetPlatforms:
    - linux/amd64
    - linux/arm64
  baseImages:
    build: golang:1.25.1-alpine@sha256:<verified-build-base-digest>
    runtime: gcr.io/distroless/static-debian12:nonroot@sha256:<verified-runtime-base-digest>
  imageRepository: registry.example.com/atlas/payments-api
  expectedRuntime:
    user: "65532:65532"
    entrypoint: /usr/local/bin/payments-api
    port: 8080
    dataPath: /var/lib/atlas-payments/payments.jsonl
    configGeneration: cfg-460-01
```

Tento manifest nie je dekoratívna metadata. Umožňuje rozlíšiť dva buildy rovnakého Git commitu, ktoré použili inú base image, inú platformu, iný builder alebo iný context. Bez tejto identity sa incident redukuje na nepresnú vetu „Docker image 4.6.0 nefunguje“.

## 3. Repository a application contract

Repository obsahuje iba súbory, ktoré patria build programu a lokálnemu runtime modelu:

```text
atlas-payments/
├── .dockerignore
├── Dockerfile
├── compose.yaml
├── go.mod
├── go.sum
├── cmd/
│   └── payments-api/
│       ├── main.go
│       └── main_test.go
└── scripts/
    ├── verify-image.sh
    ├── verify-runtime.sh
    └── verify-compose.sh
```

Docker nepotrebuje rozumieť business implementácii. Potrebuje však stabilný build contract. Test binary musí skončiť non-zero pri chybe. Finálny binary musí podporovať:

```text
payments-api serve
payments-api healthcheck
payments-api version
```

`serve` spúšťa HTTP server. `healthcheck` volá lokálny readiness endpoint a vracia vhodný exit code pre Docker `HEALTHCHECK`. `version` vypíše build version, commit a očakávané runtime metadata. Takýto contract umožňuje overovať image aj bez shellu, `curl` alebo package managera vo final stage-i.

## 4. Build context je vstup, nie celý pracovný adresár

Keď spustíme:

```bash
docker buildx build .
```

bodka neurčuje iba cestu k Dockerfile-u. Určuje build context. Docker klient alebo BuildKit frontend z neho zostaví inventory súborov dostupných pre `COPY` a ďalšie context operations. Nechcený súbor v contexte môže:

- zmeniť cache key;
- zväčšiť prenášaný context;
- skončiť v image layeri pri širokom `COPY . .`;
- sprístupniť secret build procesu;
- vytvoriť nereprodukovateľný rozdiel medzi lokálnym a CI buildom.

Pre tento projekt použijeme:

```dockerignore
.git
.gitignore
.env
.env.*
!.env.example
coverage/
dist/
tmp/
*.log
*.pem
*.key
compose.override.yaml
```

`.dockerignore` nie je bezpečnostná hranica proti škodlivému build programu. Dockerfile stále vykonáva repository-controlled commands a builder môže mať network alebo credential access. Ignore file iba obmedzuje primary context inventory.

Pred release buildom je vhodné zachovať jeho identity:

```bash
git rev-parse HEAD > evidence/source-sha.txt
sha256sum Dockerfile .dockerignore go.mod go.sum > evidence/build-inputs.sha256
find cmd -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  > evidence/source-files.sha256
```

Tieto checksumy preukazujú obsah vybraných lokálnych vstupov. Nepreukazujú base image, remote package repository ani skutočne vykonaný BuildKit graph.

## 5. Dockerfile ako build program

Použijeme multi-stage Dockerfile:

```dockerfile
# syntax=docker/dockerfile:1

ARG GO_IMAGE=golang:1.25.1-alpine@sha256:<verified-build-base-digest>
ARG RUNTIME_IMAGE=gcr.io/distroless/static-debian12:nonroot@sha256:<verified-runtime-base-digest>

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
    CGO_ENABLED=0 \
    GOOS=${TARGETOS} \
    GOARCH=${TARGETARCH} \
    go build \
      -trimpath \
      -ldflags="-s -w -X main.version=${VERSION} -X main.commit=${VCS_REF}" \
      -o /out/payments-api \
      ./cmd/payments-api

FROM ${RUNTIME_IMAGE} AS runtime

LABEL org.opencontainers.image.title="Atlas Payments API" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}"

WORKDIR /home/nonroot
COPY --from=build --chown=65532:65532 /out/payments-api /usr/local/bin/payments-api

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

Tento Dockerfile treba čítať ako graph, nie ako shell script vykonávaný vždy zhora nadol. `source` pripraví dependencies a source. `test` a `build` sú dve vetvy z rovnakého parent stage-u. `runtime` kopíruje binary iba z `build`. Z toho vyplýva dôležitá hranica: build final targetu `runtime` nemusí automaticky vykonať sibling stage `test`.

```text
source
├── test
└── build
    └── runtime
```

Test stage preto musí mať samostatný required verdict alebo musí byť release graph zostavený tak, aby final artifact preukázateľne závisel od testovaného outputu.

## 6. `FROM` a base image identity

Obe base images sú uvedené digestom. Tag `golang:1.25.1-alpine` pomáha človeku pochopiť intent; digest určuje konkrétny registry manifest. Bez digestu môže neskorší build rovnakého Dockerfile-u načítať iné bytes.

Digest pinning však nie je patching stratégia. Ak runtime base obsahuje zraniteľnosť, pinned image sa sám neopraví. Potrebujeme versionovaný update flow:

```text
nový base digest
→ nový build subject
→ test a scan
→ nový application image digest
→ promotion
→ replacement starého runtime-u
```

Použitie `ARG` pred `FROM` umožňuje base references meniť pri controlled build requeste. Release pipeline musí výsledné effective values uložiť; inak review Dockerfile-u nepreukazuje, ktoré base images boli naozaj použité.

## 7. Dependency cache nesmie byť correctness dependency

BuildKit cache mount:

```dockerfile
RUN --mount=type=cache,target=/go/pkg/mod,sharing=locked \
    go mod download
```

zrýchľuje opakované buildy, ale jeho obsah sa nestane automaticky image layerom. Cache môže byť prázdna alebo môže byť garbage-collected. Build preto musí fungovať aj bez nej.

`sharing=locked` serializuje writers pre rovnaký cache mount. Nezaručuje dôveryhodnosť jeho obsahu. Release builder nesmie importovať writeable cache z nedôveryhodných fork pipelines bez samostatného trust modelu.

Clean-room kontrola:

```bash
docker buildx build \
  --no-cache \
  --target test \
  --progress=plain \
  --output=type=cacheonly \
  .
```

No-cache build preukazuje, že test stage nepotreboval instruction cache. Nepreukazuje absenciu network mutability alebo package-repository driftu.

## 8. Samostatný test verdict

Test stage spustíme explicitne:

```bash
docker buildx build \
  --builder atlas-release \
  --target test \
  --platform linux/amd64 \
  --progress=plain \
  --output=type=cacheonly \
  . 2>&1 | tee evidence/test-build.log
```

Pri Go unit testoch nemusí byť cieľová platforma podstatná, ale presná platforma a builder stále patria do execution subjectu. Exit code `0` dokazuje, že reachable graph k targetu `test` dokončil commands. Nezaručuje, že neskorší final build použije totožný source, Dockerfile, base images alebo cache trust domain.

Pipeline preto uloží spoločný manifest:

```json
{
  "sourceSha": "7a9f2c1",
  "dockerfileSha256": "sha256:dockerfile460",
  "testTarget": "test",
  "builder": "atlas-release",
  "platform": "linux/amd64",
  "result": "PASS"
}
```

Validný JSON nie je dôkaz pravdivosti. Producer musí byť trusted pipeline a hodnoty musia pochádzať z runtime read-backov, nie z ručne zadaných variables.

## 9. Final image build

Lokálny single-platform image vytvoríme oddelene:

```bash
VERSION=4.6.0
VCS_REF="$(git rev-parse --short=12 HEAD)"
IMAGE="atlas/payments-api:${VERSION}-local"

docker buildx build \
  --builder atlas-release \
  --target runtime \
  --platform linux/amd64 \
  --build-arg VERSION="$VERSION" \
  --build-arg VCS_REF="$VCS_REF" \
  --tag "$IMAGE" \
  --provenance=false \
  --load \
  .
```

`--load` exportuje single-platform výsledok do image store-u aktuálneho Docker Engine-u. Nie je vhodným modelom pre multi-platform release index. `--provenance=false` je tu iba lokálne zjednodušenie; release publication neskôr attestations zapne.

Po build-e zachováme observed identity:

```bash
docker image inspect "$IMAGE" \
  --format '{{.Id}} {{json .RepoTags}} {{json .RepoDigests}}'
```

Lokálny image ID identifikuje config object v konkrétnom image store-i. `RepoDigests` môže byť prázdne, kým image nebol pullnutý alebo pushnutý pod registry reference. Lokálny tag je mutable pointer.

## 10. Image config a filesystem contract

Image metadata skontrolujeme bez spustenia procesu:

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

Očakávame:

```json
{
  "User": "65532:65532",
  "Entrypoint": ["/usr/local/bin/payments-api"],
  "Cmd": ["serve"],
  "WorkingDir": "/home/nonroot"
}
```

Image config je default runtime contract. `docker run --user`, `--entrypoint`, `--env` alebo Compose môže tieto hodnoty prepísať. Preto image inspect nie je effective runtime proof.

Filesystem obsah overíme cez dočasný container object:

```bash
container_id="$(docker create "$IMAGE")"
docker export "$container_id" | tar -tf - > evidence/rootfs-files.txt
docker rm "$container_id"

grep -Fx 'usr/local/bin/payments-api' evidence/rootfs-files.txt
```

Tento read-back dokazuje prítomnosť pathu vo výslednom root filesysteme. Nedokazuje architektúru binary, dynamic loader compatibility, permissions v effective mount namespace ani schopnosť procesu štartovať.

## 11. Container create subject

Container nie je iba image plus meno. Engine vytvorí nový object z image configu a runtime overrides. Pre lokálny test použijeme user-defined network, named volume a explicitné security/resource options:

```bash
docker network create atlas-payments-net
docker volume create atlas-payments-data

docker run --rm \
  --user 0:0 \
  --mount type=volume,source=atlas-payments-data,target=/data \
  "$RUNTIME_IMAGE" \
  sh -c 'mkdir -p /data && chown -R 65532:65532 /data'

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
  --env CONFIG_GENERATION=cfg-460-01 \
  "$IMAGE"
```

Initializer je samostatný privileged transition nad volume. Runtime application zostáva non-root. V produkcii má mať volume initialization explicitného ownera a idempotentný contract; náhodné `chown -R` nad veľkým datasetom môže byť pomalé alebo nebezpečné.

`docker create` vytvorí Engine object, ale nespustí process. To umožňuje skontrolovať effective configuration pred mutation:

```bash
docker inspect atlas-payments-api > evidence/container-before-start.json

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

## 12. Start, PID 1 a signal boundary

Process spustíme až po preflight-e:

```bash
docker start atlas-payments-api
```

Engine request success znamená, že create/start lifecycle nevrátil okamžitú chybu. Process môže o sekundu neskôr exitnúť. Sleduj:

```bash
docker ps --all --filter name=atlas-payments-api
docker inspect atlas-payments-api --format '{{json .State}}' | jq .
docker logs --timestamps atlas-payments-api
docker top atlas-payments-api -eo pid,ppid,user,args
```

Aplikácia má byť PID 1. Exec-form `ENTRYPOINT` znamená, že medzi runtime a aplikáciou nie je implicitný shell. `STOPSIGNAL SIGTERM` určuje default signal pri stop operácii. Aplikácia však musí signal skutočne spracovať.

Graceful stop overíme:

```bash
docker stop --time 15 atlas-payments-api

docker inspect atlas-payments-api \
  --format 'status={{.State.Status}} exit={{.State.ExitCode}} finished={{.State.FinishedAt}}'
```

Exit code `0` po stop-e je dobrý process-level dôkaz. Nepreukazuje, že všetky in-flight payment operations boli bezpečne dokončené alebo kompenzované.

Container znovu spustíme:

```bash
docker start atlas-payments-api
```

## 13. Health je samostatný stav

Docker udržiava process state a health state oddelene. Process môže byť `running`, kým health je `starting` alebo `unhealthy`.

```bash
for attempt in $(seq 1 30); do
  state="$(docker inspect atlas-payments-api --format '{{.State.Status}}')"
  health="$(docker inspect atlas-payments-api --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}')"
  printf 'attempt=%s state=%s health=%s\n' "$attempt" "$state" "$health"
  [ "$health" = "healthy" ] && break
  sleep 1
done
```

Health history:

```bash
docker inspect atlas-payments-api \
  --format '{{json .State.Health.Log}}' \
  | jq 'map({Start, End, ExitCode, Output})'
```

V tomto image-i healthcheck volá application binary, ktorý testuje `http://127.0.0.1:8080/readyz`. Zelený health teda preukazuje local namespace path a application readiness oracle. Neoveruje host NAT, user-defined network DNS ani business write.

## 14. Port publishing a bind address

`EXPOSE 8080` v Dockerfile je metadata. Host listener vznikol až runtime optionom:

```text
127.0.0.1:18080 na Docker hoste
→ port publishing/NAT
→ container IP:8080
→ process listener :8080
```

Over host path:

```bash
curl --fail --silent --show-error \
  http://127.0.0.1:18080/version \
  | jq .
```

Očakávaný payload:

```json
{
  "service": "payments-api",
  "version": "4.6.0",
  "commit": "7a9f2c1",
  "config_generation": "cfg-460-01"
}
```

Týmto spájame image build metadata s process-loaded konfiguráciou. Stále nepreukazujeme persistentný zápis ani dostupnosť z iného hosta. Listener je zámerne viazaný iba na host loopback.

Typická chyba vznikne, keď proces v containere počúva na `127.0.0.1:8080` namiesto `0.0.0.0:8080` alebo `:8080`:

```text
healthcheck vo vnútri containeru prejde
→ published port smeruje na container interface
→ process počúva iba na container loopbacku
→ host request dostane connection failure
```

Fix nie je publikovať viac portov. Application listener musí zodpovedať network contractu.

## 15. Named volume a data identity

Container writable layer je viazaný na container generation. Payment data patria named volume-u `atlas-payments-data`.

Vytvor business záznam:

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
  | jq -e '.id == "pay-100" and .amount == 1250 and .currency == "EUR"'
```

Potom odstráň iba container object:

```bash
docker rm --force atlas-payments-api
```

Volume stále existuje:

```bash
docker volume inspect atlas-payments-data
```

Po vytvorení novej container generation s rovnakým volume sa payment musí dať znovu načítať. Tento test preukazuje persistence cez container replacement na tom istom Docker hoste a v tom istom volume subjecte. Neoveruje backup, restore, host loss, corruption recovery ani concurrent-writer fencing.

## 16. Compose ako resolved application model

Ručný `docker create` je vhodný na pochopenie vrstiev, ale opakovateľný lokálny stack zapíšeme do `compose.yaml`:

```yaml
name: atlas-payments

services:
  init-data:
    image: gcr.io/distroless/static-debian12:nonroot@sha256:<verified-runtime-base-digest>
    user: "0:0"
    entrypoint: ["/busybox/sh", "-ec"]
    command:
      - |
        mkdir -p /data
        chown -R 65532:65532 /data
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
      test: ["CMD", "/usr/local/bin/payments-api", "healthcheck"]
      interval: 10s
      timeout: 3s
      start_period: 5s
      retries: 3
    restart: unless-stopped

  verifier:
    image: busybox:1.36.1@sha256:<verified-busybox-digest>
    profiles: ["verify"]
    depends_on:
      api:
        condition: service_healthy
    command:
      - sh
      - -ec
      - |
        payload="$$(wget -qO- http://payments-api:8080/version)"
        printf '%s\n' "$$payload"
        printf '%s\n' "$$payload" | grep -F '"service":"payments-api"'
        printf '%s\n' "$$payload" | grep -F '"config_generation":"${CONFIG_GENERATION}"'
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

Compose source ešte nie je effective model. Premenné, selected files, profiles, project name a Compose version môžu výsledok zmeniť. Dvojité `$$payload` je zámerné: Compose odovzdá `$payload` shellu v containere namiesto vlastnej interpolation.

`depends_on` riadi create/start ordering. `service_completed_successfully` čaká na úspešný one-shot initializer. `service_healthy` čaká na Docker health verdict API služby. Ani jedna podmienka neposkytuje nepretržitú runtime dependency recovery.

## 17. Resolved Compose model pred mutation

Environment:

```dotenv
PAYMENTS_IMAGE=atlas/payments-api:4.6.0-local
CONFIG_GENERATION=cfg-460-01
HOST_PORT=18080
```

Resolved model vytvoríme bez spustenia containers:

```bash
docker compose \
  --env-file .env \
  config \
  > evidence/compose-resolved.yaml
```

Skontroluj relevantné invariants:

```bash
yq -e '.services.api.read_only == true' evidence/compose-resolved.yaml
yq -e '.services.api.privileged != true' evidence/compose-resolved.yaml
yq -e '.services.api.cap_drop == ["ALL"]' evidence/compose-resolved.yaml
yq -e '.services.api.ports[0].host_ip == "127.0.0.1"' evidence/compose-resolved.yaml
yq -e '.services.api.volumes[0].target == "/var/lib/atlas-payments"' evidence/compose-resolved.yaml
```

`docker compose config` preukazuje, ako Compose spojil source files, interpolation a model semantics. Nepreukazuje image pull, Engine mutation ani runtime enforcement.

Project identity treba nastaviť explicitne v automation:

```bash
export COMPOSE_PROJECT_NAME=atlas-payments-dev
```

Project name ovplyvňuje labels, generated resource names a cleanup scope. Dva pipelines s rovnakým project name môžu recreatovať alebo odstrániť navzájom svoje resources.

## 18. Compose create a runtime verification

Stack spustíme bounded commandom:

```bash
docker compose \
  --env-file .env \
  up \
  --detach \
  --wait \
  --wait-timeout 120 \
  --remove-orphans
```

Compose môže vytvoriť sieť, volume, one-shot initializer a API container. `--wait` čaká, kým services dosiahnu running alebo healthy stav podľa modelu. Výsledok stále nie je business acceptance.

Engine objects:

```bash
docker compose --env-file .env ps --all
docker compose --env-file .env images
docker compose --env-file .env top
docker compose --env-file .env logs --timestamps --no-color > evidence/compose.log
```

Service DNS path overíme verifier profile-om:

```bash
docker compose \
  --env-file .env \
  --profile verify \
  run --rm verifier
```

Host path a business persistence overíme samostatne:

```bash
curl --fail --silent http://127.0.0.1:18080/version | jq .

curl --fail --silent \
  --request POST \
  --header 'Content-Type: application/json' \
  --data '{"id":"pay-compose-1","amount":900,"currency":"EUR"}' \
  http://127.0.0.1:18080/payments \
  | jq .
```

Tri kontroly testujú tri paths:

```text
Docker healthcheck
→ local container namespace

verifier service
→ Compose DNS a backend network

host curl
→ published host port

POST/GET
→ application a volume-backed business path
```

## 19. Druhé reconciliation a controlled recreate

Najprv spusti rovnaký model druhýkrát:

```bash
before_id="$(docker compose --env-file .env ps -q api)"

docker compose --env-file .env up --detach --wait --wait-timeout 120

after_id="$(docker compose --env-file .env ps -q api)"
test "$before_id" = "$after_id"
```

Rovnaký container ID preukazuje, že Compose pri tomto druhom rune nerozhodol o recreate API containeru. Neznamená to, že Compose je nepretržitý control loop alebo že neskorší manual drift opraví automaticky.

Potom zmeň configuration generation:

```dotenv
CONFIG_GENERATION=cfg-460-02
```

Aplikuj model:

```bash
docker compose --env-file .env up --detach --wait --wait-timeout 120
```

Nový container ID je očakávaný, pretože effective environment sa zmenil. Volume identity ostáva rovnaká. Over:

```bash
curl --fail --silent http://127.0.0.1:18080/version \
  | jq -e '.config_generation == "cfg-460-02"'

curl --fail --silent http://127.0.0.1:18080/payments/pay-compose-1 \
  | jq -e '.id == "pay-compose-1"'
```

Týmto oddeľujeme replacement runtime generation od persistence generation.

## 20. Multi-platform registry publication

Produkčný release nevytvoríme cez `--load`. Buildx publikuje image index pre obe platformy:

```bash
IMAGE_REF="registry.example.com/atlas/payments-api:4.6.0"

docker buildx build \
  --builder atlas-release \
  --target runtime \
  --platform linux/amd64,linux/arm64 \
  --build-arg VERSION=4.6.0 \
  --build-arg VCS_REF="$(git rev-parse --short=12 HEAD)" \
  --tag "$IMAGE_REF" \
  --provenance=mode=max \
  --sbom=true \
  --push \
  .
```

Build success preukazuje exporter completion, ale registry response môže mať unknown outcome pri timeout-e. Preto digest read-backujeme:

```bash
docker buildx imagetools inspect "$IMAGE_REF"
docker buildx imagetools inspect "$IMAGE_REF" --raw > evidence/image-index.json
```

Platform inventory:

```bash
jq -r '.manifests[] | [.platform.os, .platform.architecture, .digest] | @tsv' \
  evidence/image-index.json
```

Očakávame presne:

```text
linux  amd64  sha256:<amd64-manifest>
linux  arm64  sha256:<arm64-manifest>
```

Tag `4.6.0` ostáva mutable pointer, pokiaľ registry policy nezakazuje prepis. Release manifest preto uloží index digest a production používa digest reference:

```text
registry.example.com/atlas/payments-api@sha256:<index-digest>
```

Index digest identifikuje platform selection graph. Konkrétny node nakoniec stiahne platform manifest a config/layers pod ďalšími digestmi. Pri incidente treba rozlišovať index a platform-specific artifact.

## 21. Connected incident `CTR-PAY-81`

Atlas vydal `payments-api 4.6.0`. Unit-test job spustil target `test`, ale release build používal iný shared builder a mutable build cache. Image bol publikovaný pod tagom `4.6.0`, scanner overil aktuálny amd64 manifest a deployment configuration odkazovala iba na tag.

Po publication-e automatický rebuild rovnaký tag prepísal. Nový arm64 manifest vznikol z iného runtime base digestu. Zároveň Compose smoke environment kontroloval iba `/healthz`, ktorý neoveroval zápis do volume. Produkčný arm64 node stiahol nový platform manifest, process sa spustil a health zostal zelený. Prvý payment write však zlyhal na `permission denied`, pretože nový runtime user mal iný UID než owner persistentného mountu.

Failure chain bol:

```text
test target na builderi B1
→ final release build na builderi B2
→ tag 4.6.0 publikovaný ako index D1
→ scan iba amd64 manifestu z D1
→ automatický rebuild prepísal tag na index D2
→ arm64 node stiahol manifest z D2
→ process a /healthz boli zelené
→ mounted data path vlastnil starý UID
→ payment write zlyhal
```

Žiadna jednotlivá Docker operácia nebola nutne chybná. Chýbal spoločný release subject a complete evidence:

- test a release build nemali preukázaný rovnaký graph/input subject;
- scanner nepokrýval celý platform inventory;
- production konzumovala mutable tag;
- health oracle nekontroloval required write capability;
- volume ownership nebol súčasťou runtime compatibility contractu.

## 22. Diagnostika od identity, nie od restartu

Pri symptóme „container je healthy, ale payment write zlyháva“ najprv zachovaj:

```bash
docker inspect atlas-payments-api > incident/container-inspect.json
docker image inspect "$(docker inspect atlas-payments-api --format '{{.Image}}')" \
  > incident/image-inspect.json
docker logs --timestamps atlas-payments-api > incident/container.log 2>&1
docker events --since 30m --until 0s > incident/events.log
docker volume inspect atlas-payments-data > incident/volume-inspect.json
docker network inspect atlas-payments-net > incident/network-inspect.json
docker system df -v > incident/system-df.txt
```

Potom stabilizuj presný subject:

```text
Docker context a daemon identity
container ID a create timestamp
image ID a registry index/platform digest
effective user a security options
mount source, destination a mode
volume owner a data generation
process state, exit/health history
host kernel/cgroup/LSM generation
release, configuration a secret generation
```

Competing hypotheses:

```text
H1: application beží pod nesprávnym UID/GID
H2: volume path má nesprávny ownership alebo mode
H3: read-only root filesystem zakryl chýbajúci writable path
H4: bind mount alebo volume zakryl image directory
H5: SELinux/AppArmor odmieta write
H6: disk alebo inode capacity je vyčerpaná
H7: application používa iný DATA_PATH
H8: verifier testuje inú container/image generation
```

Discriminating observations:

```bash
docker inspect atlas-payments-api --format '{{.Config.User}}'
docker inspect atlas-payments-api --format '{{json .Mounts}}' | jq .
docker exec atlas-payments-api /usr/local/bin/payments-api version
docker exec atlas-payments-api /usr/local/bin/payments-api healthcheck
docker stats --no-stream atlas-payments-api
```

Distroless image nemusí obsahovať `sh`, `ls`, `id` ani `stat`. To nie je dôvod meniť production container ručnou inštaláciou nástrojov. Použi debug image v rovnakom namespace/mount kontexte alebo controlled reproduction s rovnakými runtime options.

## 23. Containment a recovery

Pri incidente `CTR-PAY-81` containment zastaví ďalší pull mutable tagu a zachová registry manifests, builder records, scan reports a affected volume identities. Runtime s chybným manifestom sa nevyrieši slepým `docker restart`, pretože restart znovu používa rovnaký container config a image.

Recovery:

```text
zastaviť tag mutation a promotion
→ identifikovať D1, D2 a affected platform manifests
→ potvrdiť expected runtime UID a volume owner
→ vytvoriť nový immutable build subject
→ spustiť test target a runtime write test pre obe platformy
→ publikovať nový index digest D3
→ scan/SBOM/provenance viazať na D3 a oba manifests
→ inicializovať alebo migrovať volume ownership bounded operáciou
→ nahradiť containers digestom D3
→ overiť health, version, POST/GET a persistence po recreate
→ zablokovať mutable production references
```

Ak publication request timeoutne, najprv read-backni registry tag/digest. Automatický push retry môže byť bezpečný pre content-addressed blobs, ale tag mutation a release records stále potrebujú known outcome.

## 24. Kedy je Docker release prijatý

Release môžeme považovať za overený iba vtedy, keď vieme preukázať:

```text
source, Dockerfile, context a base images tvoria jeden build subject
+ test stage bol skutočne vykonaný
+ final image pochádza zo schváleného source/build subjectu
+ index obsahuje presne očakávané platform manifests
+ scan, SBOM a provenance patria publikovanému digestu
+ runtime používa digest, nie mutable tag
+ effective container config zachováva non-root a hardening policy
+ PID 1 správne spracuje stop signal
+ local health, service-DNS a host-port paths prejdú
+ process načítal očakávanú configuration generation
+ business write/read prejde
+ dáta prežijú container alebo Compose recreate
+ forbidden privileged, host-socket a broad-bind paths sú odmietnuté
```

Zelený container bez týchto väzieb je iba process status.

## 25. Anti-patterny

### Jeden obrovský tutorial namiesto mechanizmu

Kapitola, ktorá programuje celú aplikáciu, môže zakryť Docker lifecycle pod detailmi cudzieho jazyka. Docker walkthrough má ukázať build, image, runtime a verification boundaries. Aplikačný source má byť iba natoľko podrobný, aby bol jeho runtime contract jasný.

### Test stage existuje, preto testy určite bežali

Multi-stage Dockerfile je graph. Sibling `test` stage nie je automaticky dependency final `runtime` targetu.

### Tag je verzia artifactu

Tag je repository pointer. Digest identifikuje manifest content.

### `docker ps` je health proof

Running znamená, že hlavný process ešte neexitol. Neznamená readiness ani business correctness.

### `EXPOSE` publikuje port

`EXPOSE` je metadata. Host listener vytvára runtime port publishing.

### Volume automaticky vyrieši persistence

Volume oddeľuje data lifecycle od container writable layeru. Nevyrieši ownership, backup, restore, corruption, fencing ani host loss.

### Restart opraví image alebo configuration

Restart používa rovnaký container object. Zmena image alebo environmentu vyžaduje recreate/replacement.

### Debug priamo v production containeri

Ručná inštalácia tools alebo editácia filesystemu vytvára container drift a ničí reprodukovateľnosť. Zachovaj evidence a oprav versionovaný build alebo runtime model.

## 26. Praktický troubleshooting flow

Pri Docker probléme postupuj po vrstvách:

```text
client command a Docker context
→ daemon/API availability
→ image reference a platform resolution
→ container create configuration
→ OCI runtime/process start
→ PID 1 a exit/health state
→ mounts a filesystem permissions
→ network namespace, listener a publishing
→ cgroup/LSM/kernel enforcement
→ application a business outcome
```

Prvé otázky nie sú „mám restartovať Docker?“ ale:

```text
Ktorý daemon som oslovil?
Ktorý image digest a platform manifest sa použil?
Aká je effective container konfigurácia?
Kde je prvý layer, na ktorom desired a observed state prestali súhlasiť?
```

Až potom má zmysel rozhodnúť, či treba rebuild, recreate, volume repair, network correction, host remediation alebo application fix.

## Primárne zdroje

- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [BuildKit](https://docs.docker.com/build/buildkit/)
- [Buildx build](https://docs.docker.com/reference/cli/docker/buildx/build/)
- [Running containers](https://docs.docker.com/engine/containers/run/)
- [Resource constraints](https://docs.docker.com/engine/containers/resource_constraints/)
- [Compose file reference](https://docs.docker.com/reference/compose-file/)
- [Compose `config`](https://docs.docker.com/reference/cli/docker/compose/config/)
- [Compose `up`](https://docs.docker.com/reference/cli/docker/compose/up/)
- [Compose `down`](https://docs.docker.com/reference/cli/docker/compose/down/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: BuildKit a Buildx](buildkit-buildx.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Docker troubleshooting →](docker-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->