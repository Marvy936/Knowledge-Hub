# Docker Compose

Docker Compose nie je iba skratka pre niekoľko `docker run` príkazov. Je to application model a bounded reconciliation nástroj nad Docker Engine. Načíta jeden alebo viac Compose files, vyrieši environment interpolation, profiles, includes alebo overrides, vytvorí resolved model a pod konkrétnou project identity z neho vytvorí containers, networks, volumes, configs a secrets podľa podporovanej platformy.

Najdôležitejšia hranica je medzi source YAML a effective runtime-om. `compose.yaml` je authoring input. `docker compose config` ukáže resolved model. `docker compose up` požiada Engine o mutation. `docker inspect`, network a volume inspect ukážu effective objects. Health a business testy až napokon ukážu, či application funguje.

Budeme skladať project `atlas-payments` so službami `init-data`, `api` a voliteľným `verifier`.

## 1. Project identity

Compose zoskupuje resources pod project name. Project identity ovplyvňuje labels a generated names containers, networks a volumes.

Project možno nastaviť priamo v modeli:

```yaml
name: atlas-payments
```

alebo cez CLI:

```bash
docker compose --project-name atlas-payments-dev up -d
```

Ak project name nie je explicitný, Compose ho odvodí podľa svojich pravidiel, napríklad z directory alebo environmentu. Dve CI jobs s rovnakým project name môžu navzájom recreatovať alebo odstrániť resources. Zmena project name môže vytvoriť nový default network a nové project-scoped volumes.

Pred mutation:

```bash
docker compose ls
docker compose --project-name atlas-payments-dev config
```

Project name preto patrí do exact run subjectu rovnako ako Compose files a environment inputs.

## 2. Minimálny Compose model

```yaml
name: atlas-payments

services:
  api:
    image: atlas/payments-api:1.0.0
    ports:
      - "127.0.0.1:18080:8080"
```

Spustenie:

```bash
docker compose up --detach
```

Compose vytvorí project network a container pre service `api`. Service je modelová jednotka, container je konkrétna runtime instance. Pri scale môže jedna service vytvoriť viac containers.

```bash
docker compose ps --all
docker compose images
docker compose top
```

`up` nie je nepretržitý control loop ako Kubernetes controller. Compose aplikuje model pri konkrétnej operácii. Manual drift po skončení commandu nemusí automaticky opravovať.

## 3. Interpolation pred modelom

Compose nahrádza `${...}` expressions ešte pred vytvorením containeru:

```yaml
services:
  api:
    image: ${PAYMENTS_IMAGE:?PAYMENTS_IMAGE is required}
    environment:
      LOG_LEVEL: ${LOG_LEVEL:-info}
```

Environment file:

```dotenv
PAYMENTS_IMAGE=atlas/payments-api:1.0.0
LOG_LEVEL=debug
```

Resolved environment:

```bash
docker compose --env-file .env config --environment
```

Resolved model:

```bash
docker compose --env-file .env config > compose-resolved.yaml
```

Shell environment, `.env`, `--env-file` a ďalšie sources majú precedence rules. Source YAML preto nemusí obsahovať hodnotu, ktorú container dostane.

Required syntax zabráni tichému fallbacku. Default syntax je vhodná iba pre bezpečné hodnoty. Image identity alebo production credential nemajú ticho prejsť na `latest` alebo development default.

## 4. Service image a build

Service môže používať už existujúci image:

```yaml
services:
  api:
    image: registry.example.com/atlas/payments-api@sha256:<digest>
```

Alebo build model:

```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: runtime
      args:
        VERSION: "1.0.0"
    image: atlas/payments-api:1.0.0-local
```

`build` opisuje, ako image vytvoriť. `image` určuje meno pre výsledok alebo image použité pri runtime podľa Compose operation a pull/build options.

Production-like flow často buildne artifact v CI, publikuje digest a Compose iba konzumuje immutable reference. Local development môže používať `build`.

```bash
docker compose build --progress=plain
docker compose up --build --detach
```

`--build` neznamená automaticky clean build ani publication do registry. Používa configured builder a cache.

## 5. Celý `payments-api` model

Compose model skladá viac runtime subjects do jedného application graphu. `init-data` vlastní jednorazovú prípravu volume permissions a `api` vlastní application process a health contract. Networks, volumes, environment interpolation, image references a dependency conditions sa resolve-nú pred Engine mutation, preto sa musí najprv čítať výsledok `docker compose config`, nie iba source YAML.

Nasledujúci model oddeľuje privileged initializer od non-root aplikácie, persistent data od read-only root filesystemu a host publication od internal service DNS. `depends_on` určuje startup ordering, nie business readiness celej application. Acceptance preto pokračuje cez container identities, runtime image digests, health, service-to-service request, host-published request a volume persistence po replacement-e.

```yaml
name: atlas-payments

services:
  init-data:
    image: busybox:1.36.1@sha256:<busybox-digest>
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
        published: "18080"
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
    image: curlimages/curl:8.10.1@sha256:<curl-digest>
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

Model oddeľuje one-shot initialization, long-running API a test service. Root filesystem API je read-only, volume má explicitnú identity a host port je viazaný iba na loopback.

## 6. `depends_on` je startup coordination

Short syntax:

```yaml
depends_on:
  - database
```

zabezpečí create/start ordering, ale nečaká automaticky na application readiness.

Long syntax podporuje conditions:

```yaml
depends_on:
  init-data:
    condition: service_completed_successfully
```

API sa vytvorí po úspešnom skončení initializeru.

```yaml
depends_on:
  api:
    condition: service_healthy
```

Verifier čaká na Docker health verdict API.

Tieto conditions neriešia dlhodobú dependency resilience. Ak database neskôr vypadne, Compose automaticky nemusí reštartovať consumers alebo riadiť reconnect. Application potrebuje retry, timeout a recovery contract.

## 7. One-shot services

Migration, initialization alebo verification service má skončiť a vrátiť pravdivý exit code.

```yaml
restart: "no"
```

je dôležité, aby runtime policy neopakovala neúspešnú non-idempotentnú operáciu bez kontroly.

Initializer má byť idempotentný. `mkdir -p`, kontrola schema version a bounded ownership zmena sú bezpečnejšie než slepý destructive reset.

`service_completed_successfully` preukazuje exit code one-shot containeru. Neoveruje, že všetky externé side effects sú complete alebo že output patrí správnemu volume-u. Logs a business read-back zostávajú potrebné.

## 8. Networks

Explicitná user-defined network:

```yaml
networks:
  backend:
    internal: true
```

Služby pripojené do `backend` používajú Compose DNS. Service `api` je dostupná ako `api` a cez alias `payments-api`.

```bash
docker compose run --rm --no-deps verifier
```

Verifier testuje service DNS a bridge path. Host curl testuje inú cestu:

```bash
curl -fsS http://127.0.0.1:18080/version
```

`internal: true` obmedzí external connectivity cez danú network podľa driver semantics. Ak API potrebuje database mimo network, môže byť potrebná ďalšia network alebo iný model. Multi-network service potrebuje explicitnú route a exposure analýzu.

## 9. Volumes

Top-level volume:

```yaml
volumes:
  payments-data:
    name: atlas-payments-data
```

má explicitné Engine meno. Compose project rename nevytvorí nový volume.

Ak volume spravuje iný systém:

```yaml
volumes:
  payments-data:
    external: true
    name: atlas-payments-data
```

Compose očakáva jeho existenciu a nevlastní create lifecycle.

Mount v service:

```yaml
volumes:
  - type: volume
    source: payments-data
    target: /var/lib/atlas-payments
```

Resolved model treba skontrolovať pred `up`, pretože nesprávny source name môže pripojiť prázdny alebo staging volume.

## 10. Configs a secrets

Compose model podporuje top-level `configs` a `secrets`. Konkrétna implementation a ochrana sa líšia medzi local Compose a orchestrator platforms.

Príklad config file-u:

```yaml
services:
  api:
    configs:
      - source: payments-config
        target: /etc/atlas/config.yaml

configs:
  payments-config:
    file: ./config.yaml
```

Secret:

```yaml
services:
  api:
    secrets:
      - database_password

secrets:
  database_password:
    file: ./secrets/database_password.txt
```

Aplikácia číta `/run/secrets/database_password` podľa default semantics alebo explicit targetu.

Local file-backed secret stále existuje na host filesysteme. Compose YAML abstrakcia ho automaticky nezašifruje ani nerotuje. Source file permissions a secret distribution zostávajú kritické.

## 11. Profiles

Profiles umožnia zapnúť voliteľné services:

```yaml
profiles:
  - verify
```

Bežný `up` verifier nespustí. Test:

```bash
docker compose --profile verify run --rm verifier
```

Resolved profiles:

```bash
docker compose config --profiles
```

Dôležité required checks nemajú byť iba v profile, ktorý CI zabudne aktivovať. Expected service a evidence inventory musí uviesť, ktoré profiles patria konkrétnemu runu.

## 12. Multiple files a override

Compose môže spojiť viac files:

```bash
docker compose \
  -f compose.yaml \
  -f compose.dev.yaml \
  config
```

Override môže zmeniť image, environment, ports, mounts alebo security options. Merge semantics nie sú obyčajné textové prepisovanie a líšia sa podľa field typu.

Príklad development override:

```yaml
services:
  api:
    environment:
      LOG_LEVEL: debug
    ports:
      - "127.0.0.1:28080:8080"
```

Pred mutation vždy kontroluj combined resolved model. Review iba base file-u nepreukazuje effective runtime.

## 13. `include` a modularizácia

Moderná Compose Specification podporuje `include` pre skladanie application modelov podľa podporovanej Compose verzie.

```yaml
include:
  - infra/observability.yaml
```

Included model prináša vlastné services, networks alebo volumes. Remote alebo external include rozširuje supply-chain boundary. Jeho content má byť versionovaný a reviewnutý.

Pri incident analýze zachovaj všetky source files a Compose version. Rovnaký top-level file môže resolve-nuť inak, ak included content alebo tool semantics zmenili generation.

## 14. `docker compose config`

Najdôležitejší preflight command:

```bash
docker compose --env-file .env config > compose-resolved.yaml
```

Ďalšie pohľady:

```bash
docker compose config --services
docker compose config --images
docker compose config --networks
docker compose config --volumes
docker compose config --profiles
```

Resolved YAML možno kontrolovať policy nástrojom:

```bash
yq -e '
  .services.api.read_only == true
  and .services.api.privileged != true
  and .services.api.cap_drop == ["ALL"]
  and .services.api.ports[0].host_ip == "127.0.0.1"
' compose-resolved.yaml
```

Config success dokazuje parsing, interpolation a model normalization. Neoveruje image pull, Engine capabilities, host paths ani runtime health.

## 15. `up` ako bounded reconciliation

```bash
docker compose up \
  --detach \
  --wait \
  --wait-timeout 120 \
  --remove-orphans
```

Compose porovná model s project resources a podľa potreby vytvorí, spustí alebo recreatne containers. `--remove-orphans` odstráni project containers pre services, ktoré už v aktuálnom modeli nie sú.

`--wait` čaká na running alebo healthy stav. Pri timeout-e môže byť výsledok partial: niektoré resources vznikli, iné zlyhali. Pred retry najprv `ps`, logs a inspect.

```bash
docker compose ps --all
docker compose logs --timestamps --no-color
```

## 16. Kedy Compose recreatne container

Ak sa zmení effective service configuration alebo image, Compose môže vytvoriť nový container. Environment, mounts, ports, security options a image reference sú create-time state a nemožno ich všetky zmeniť in-place.

No-op kontrola:

```bash
before="$(docker compose ps -q api)"
docker compose up -d --wait
after="$(docker compose ps -q api)"
test "$before" = "$after"
```

Zmena `CONFIG_GENERATION`:

```dotenv
CONFIG_GENERATION=cfg-101
```

ďalší `up` má vytvoriť nový container ID. Volume identity zostáva rovnaká a `/version` má ukázať novú generation.

## 17. `restart` vs `up`

```bash
docker compose restart api
```

reštartuje existujúci container. Neaplikuje nové environment values alebo nový image do create configuration.

```bash
docker compose up -d api
```

vykoná reconciliation a pri zmene modelu recreatne service.

Táto hranica je rovnaká ako pri plain Docker: restart nie je deployment novej configuration generation.

## 18. Scale

```bash
docker compose up -d --scale api=3
```

vytvorí viac container instances jednej service, pokiaľ model nemá konfliktné pevné container name alebo host port publication.

Fixed host port `18080` nemožno jednoducho prideliť trom containers na rovnakom host IP. Scale-out service zvyčajne komunikuje cez internal network a external reverse proxy alebo používa allocated ports.

Shared volume s viacerými replicas je bezpečný iba vtedy, keď application podporuje multi-writer semantics.

## 19. Logs, exec a run

Logs projectu:

```bash
docker compose logs -f --timestamps api
```

Exec v existing containere:

```bash
docker compose exec api /usr/local/bin/payments-api version
```

One-off container zo service modelu:

```bash
docker compose run --rm --no-deps api version
```

`run` vytvorí nový container a môže mať odlišné port publication behavior alebo dependency lifecycle. Nie je to totožné s exec do serving instance.

Pri debug-u vedz, či pozoruješ active service container alebo novú one-off generation.

## 20. `down` a cleanup

```bash
docker compose down --remove-orphans
```

odstráni project containers a networks. Named volumes štandardne ponechá.

```bash
docker compose down --volumes
```

odstráni aj volumes vlastnené modelom podľa semantics. To je data-destructive.

Images možno odstraňovať ďalšími options, ale cleanup nemá byť súčasťou recovery bez evidence inventory. Incident container, logs a writable layer sa majú zachovať pred `down`.

## 21. Incident: override odstránil security hardening

Base file definoval:

```yaml
read_only: true
cap_drop: [ALL]
```

Development override chcel pridať debug tool, ale prepísal service širším blokom a nastavil `privileged: true`. Rovnakú file kombináciu omylom použila staging pipeline.

Review base file-u vyzeral bezpečne. `docker compose config` by ukázal privileged effective model.

Oprava pridala resolved-model policy gate, oddelila debug service do profile-u a staging pipeline používala explicitný allowlist Compose files.

## 22. Incident: project collision odstránila cudziu službu

Dve CI jobs bežali v rovnakom directory name a Compose odvodil rovnaký project name. Job B spustil nový model s `--remove-orphans` a odstránil verifier container jobu A.

Oprava nastavila unique project name z pipeline ID:

```bash
export COMPOSE_PROJECT_NAME="atlas-payments-${CI_PIPELINE_ID}"
```

Cleanup používal rovnakú exact identity. Shared external volumes dostali samostatný owner a neboli project-scoped.

## 23. Systematický Compose troubleshooting

Pri chybe postupuj cez vrstvy:

```text
source files a Compose version
→ interpolation environment
→ resolved model
→ project identity
→ Engine objects a labels
→ container create/start
→ health
→ network, volume a business outcome
```

Evidence:

```bash
docker compose version
docker compose config --environment
docker compose config > compose-resolved.yaml
docker compose ps --all
docker compose images
docker compose logs --timestamps --no-color
docker inspect "$(docker compose ps -q api)"
```

Nerob okamžite `down -v` alebo `up --force-recreate`. Mohol by si zničiť volume alebo pôvodný container evidence.

## Čo si z kapitoly odniesť

Compose source YAML nie je effective runtime. Interpolation, multiple files, profiles, includes a project name vytvoria resolved model. `docker compose config` je preflight, `up` je bounded reconciliation a `inspect` je runtime read-back.

Service, container, network a volume majú rozdielne identity. `depends_on` rieši startup coordination, nie dlhodobú resilience. Restart neaplikuje novú create configuration. Named volumes štandardne prežijú `down`, ale `down --volumes` ich odstráni. Dôveryhodný Compose workflow kontroluje resolved model, exact project identity, runtime health a business outcome.

## Primárne zdroje

- [Compose Specification](https://docs.docker.com/reference/compose-file/)
- [Compose services](https://docs.docker.com/reference/compose-file/services/)
- [Compose networks](https://docs.docker.com/reference/compose-file/networks/)
- [Compose volumes](https://docs.docker.com/reference/compose-file/volumes/)
- [Compose environment variables](https://docs.docker.com/compose/how-tos/environment-variables/)
- [`docker compose config`](https://docs.docker.com/reference/cli/docker/compose/config/)
- [`docker compose up`](https://docs.docker.com/reference/cli/docker/compose/up/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Environment variables a health checks](environment-variables-health-checks.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: BuildKit a Buildx →](buildkit-buildx.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
