# Environment variables a health checks

Environment variables a health checks riešia dve odlišné otázky. Environment určuje, s akou konfiguráciou process vznikne. Healthcheck pravidelne hodnotí vybranú runtime podmienku po štarte. Zelený health status však nepreukazuje, že process načítal správnu konfiguráciu, a správne environment values nepreukazujú, že aplikácia je pripravená obsluhovať requesty.

Budeme sledovať `payments-api` s konfiguráciou:

```text
LISTEN_ADDRESS=:8080
LOG_LEVEL=info
CONFIG_GENERATION=cfg-100
DATA_PATH=/var/lib/atlas-payments/payments.jsonl
```

Aplikácia poskytuje `/healthz`, `/readyz` a `/version`. `/healthz` potvrdzuje, že process žije. `/readyz` overuje, že aplikácia vie používať required data path. `/version` ukáže release a loaded configuration generation.

## 1. Image `ENV` je iba default

Dockerfile môže definovať:

```dockerfile
ENV LISTEN_ADDRESS=:8080 \
    LOG_LEVEL=info \
    DATA_PATH=/var/lib/atlas-payments/payments.jsonl
```

Tieto hodnoty sa zapíšu do image configu:

```bash
docker image inspect IMAGE \
  --format '{{json .Config.Env}}' | jq .
```

Pri container create ich runtime môže prepísať:

```bash
docker run --rm \
  --env LOG_LEVEL=debug \
  IMAGE
```

Image metadata preto nie je dôkaz effective container environmentu. Ten čítame z konkrétneho container objectu:

```bash
docker inspect CONTAINER \
  --format '{{json .Config.Env}}' | jq .
```

Ani inspect však nepreukazuje, že aplikácia hodnotu úspešne parse-nula alebo použila. Process mohol invalidnú hodnotu ignorovať a použiť interný default.

## 2. Missing, empty a explicitná hodnota

Configuration parser musí rozlišovať tri stavy:

```text
premenná chýba
premenná existuje, ale je prázdna
premenná má explicitnú hodnotu
```

Shell expansion:

```sh
value="${LOG_LEVEL:-info}"
```

použije `info` pri missing aj empty hodnote. Variant:

```sh
value="${LOG_LEVEL-info}"
```

použije default iba pri missing hodnote.

Tento rozdiel je kritický pri boolean alebo security configuration. Prázdna hodnota nemá byť automaticky interpretovaná ako `true` ani `false` bez explicitného contractu.

Aplikácia má validovať povolené hodnoty pri štarte:

```text
LOG_LEVEL ∈ debug, info, warn, error
```

Pri `LOG_LEVEL=verbose-ish` je bezpečnejšie skončiť s jasnou chybou než ticho použiť iný režim.

## 3. `--env` a host environment

Príkaz:

```bash
docker run --env LOG_LEVEL IMAGE
```

prevezme hodnotu `LOG_LEVEL` z environmentu Docker CLI procesu. To môže vytvoriť hidden input.

```bash
export LOG_LEVEL=debug
docker run --env LOG_LEVEL IMAGE
```

Na inom termináli alebo runneri môže byť hodnota iná alebo missing. Pre release automation je explicitnejšie:

```bash
docker run --env LOG_LEVEL=debug IMAGE
```

alebo versionovaný, nesenzitívny environment file s evidence o použitom contente.

## 4. Environment file

Docker CLI:

```bash
docker run --env-file ./payments.env IMAGE
```

Príklad `payments.env`:

```dotenv
LISTEN_ADDRESS=:8080
LOG_LEVEL=info
CONFIG_GENERATION=cfg-100
DATA_PATH=/var/lib/atlas-payments/payments.jsonl
```

Environment file sa nesmie automaticky považovať za bezpečný secret store. Môže skončiť v repository, backupoch, shell history alebo incident bundle-i. Files s credentials potrebujú permissions, secret management a rotation lifecycle.

Pred spustením možno zachovať checksum nesenzitívneho config artifactu:

```bash
sha256sum payments.env
```

Checksum nepreukazuje význam hodnôt, ale umožňuje korelovať runtime s exact file generation.

## 5. Compose interpolation nie je container environment

Compose používa environment na interpoláciu vlastného YAML modelu:

```yaml
services:
  api:
    image: ${PAYMENTS_IMAGE:?PAYMENTS_IMAGE is required}
    environment:
      LOG_LEVEL: ${LOG_LEVEL:-info}
```

`PAYMENTS_IMAGE` a `LOG_LEVEL` sa najprv použijú pri Compose model resolution. Až výsledná hodnota pod `services.api.environment` sa stane container environmentom.

Pozri interpolation inputs:

```bash
docker compose --env-file .env config --environment
```

A resolved model:

```bash
docker compose --env-file .env config > compose-resolved.yaml
```

`.env`, shell environment, `--env-file`, Compose `environment`, service `env_file` a CLI overrides majú precedence rules. Pri incidente sa neháda podľa source file-u; číta sa resolved model a container inspect.

## 6. Required interpolation

Compose podporuje required syntax:

```yaml
image: ${PAYMENTS_IMAGE:?PAYMENTS_IMAGE must be set}
```

Chýbajúca alebo prázdna hodnota spôsobí chybu ešte pred container mutation. To je lepšie než tichý fallback na `latest` alebo prázdny string.

Default syntax:

```yaml
LOG_LEVEL: ${LOG_LEVEL:-info}
```

je vhodná iba vtedy, keď je default bezpečný a zamýšľaný. Production secrets, image references a environment identity často majú byť required.

## 7. Secrets v environment variables

Environment values sú viditeľné cez:

```bash
docker inspect CONTAINER
```

A často aj cez process environment vo vnútri namespace-u. Crash dump, debug endpoint alebo broad host access ich môže odhaliť.

Pre citlivé credentials je vhodnejší mounted secret file alebo runtime identity:

```text
/run/secrets/database_password
```

Aplikácia načíta file s úzkymi permissions. Secret file však stále existuje v process mount namespace-e. Potrebujeme rotation, access control a zákaz logovania.

Pri lokálnom Compose možno použiť `secrets` model podľa platform capabilities. Compose local secrets nemusia poskytovať rovnakú ochranu ako orchestrator secret store; treba rozumieť implementácii.

## 8. Loaded configuration generation

Container environment ukazuje, čo Engine odovzdal procesu. Application telemetry má ukázať, čo process skutočne načítal.

`/version` môže bezpečne vrátiť:

```json
{
  "service": "payments-api",
  "version": "1.0.0",
  "commit": "7a9f2c1",
  "config_generation": "cfg-100"
}
```

Endpoint nesmie vracať secrets. Generation môže byť version string alebo hash nesenzitívnych configuration inputs.

Po recreate:

```bash
curl -fsS http://127.0.0.1:18080/version | jq .
```

porovná desired generation s loaded generation. Zelený rollout bez tejto kontroly môže spustiť starú config alebo process, ktorý zmenu neaplikoval.

## 9. Process state a health state

Docker Engine sleduje hlavný process. Ak process existuje, container môže byť `running`. Healthcheck pridáva samostatný stav:

```text
none
starting
healthy
unhealthy
```

Inspect:

```bash
docker inspect CONTAINER \
  --format '{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}'
```

Process môže byť running a unhealthy. Môže byť healthy podľa plytkého oracle-u a zároveň zlyhávať pri business requeste.

## 10. Dockerfile healthcheck

```dockerfile
HEALTHCHECK \
  --interval=10s \
  --timeout=3s \
  --start-period=5s \
  --retries=3 \
  CMD ["/usr/local/bin/payments-api", "healthcheck"]
```

`interval` určuje frekvenciu. `timeout` ohraničuje jeden check. `start-period` poskytuje bootstrap okno, počas ktorého failures nemajú rovnaký účinok na health verdict podľa Docker semantics. `retries` určuje počet consecutive failures pred unhealthy stavom.

Health command musí skončiť exit code `0` pri úspechu a non-zero pri chybe. Output sa uloží do bounded health history:

```bash
docker inspect CONTAINER \
  --format '{{json .State.Health.Log}}' | jq .
```

## 11. Shell form a exec form

Compose alebo Dockerfile healthcheck môže používať shell:

```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:8080/readyz || exit 1"]
```

To vyžaduje shell a `curl` v image-i. Distroless image ich nemusí mať.

Exec form:

```yaml
healthcheck:
  test: ["CMD", "/usr/local/bin/payments-api", "healthcheck"]
```

spustí application binary priamo. Tým sa health contract stane súčasťou aplikácie a minimal runtime nepotrebuje extra tools.

## 12. Liveness, readiness a startup nie sú jedna otázka

Docker Engine má jeden health status model, ale aplikácia môže interné endpoints rozdeliť významovo.

`/healthz` odpovedá, či process žije a vie obslúžiť základný request. `/readyz` odpovedá, či má byť service zaradená do trafficu. Startup check môže mať dlhšie bootstrap tolerancie.

V plain Docker prostredí healthcheck často používa readiness-like oracle, aby Compose `service_healthy` čakalo na použiteľnú službu. Restart policy však Docker health status automaticky nemusí interpretovať ako dôvod na restart. Unhealthy container môže zostať running.

Orchestrátory ako Kubernetes majú samostatné liveness, readiness a startup probes. Koncepty sa nemajú mechanicky zlievať s Docker healthcheckom.

## 13. Čo má readiness testovať

Readiness má overovať required preconditions pre traffic, ale nemá vytvárať drahé alebo nebezpečné side effects pri každom intervale.

Pre `payments-api` môže overiť:

```text
HTTP server event loop funguje
required configuration je validná
payment data path je zapisovateľný
kritický dependency pool je inicializovaný
```

Pri database dependency treba opatrnosť. Ak všetky replicas pri krátkom DB probléme okamžite prestanú byť ready, môže to byť správne alebo môže vzniknúť úplný outage podľa service contractu. Health design má zohľadniť degraded mode a dependency retry model.

## 14. Healthcheck musí mať bounded cost

Check spúšťaný každých pár sekúnd na stovkách containers môže vytvoriť značný traffic. Ak vykonáva databázový write, môže znečistiť business data a zhoršiť incident.

Bezpečný check je krátky, má timeout a používa minimum resources. Ak testuje write permission, môže vytvoriť a odstrániť malý temp file v určenom path-e bez konfliktu s business data.

Application má odlíšiť health traffic v telemetry, ale nemá ho úplne skryť; spike latency health endpointu môže byť diagnosticky cenný.

## 15. Compose `depends_on` a health

Long syntax:

```yaml
services:
  api:
    depends_on:
      init-data:
        condition: service_completed_successfully

  verifier:
    depends_on:
      api:
        condition: service_healthy
```

Compose vytvorí `api` až po úspešnom one-shot initializeri a verifier až po healthy API podľa podporovanej Compose semantics.

Toto je startup ordering. Ak API o desať minút neskôr ochorie, Compose automaticky nemusí reštartovať verifier ani riadiť distributed recovery. Aplikácie stále potrebujú reconnect a retry behavior.

## 16. `docker compose up --wait`

```bash
docker compose up \
  --detach \
  --wait \
  --wait-timeout 120
```

Compose čaká, kým services dosiahnu running alebo healthy stav podľa modelu. Úspešný command je bounded infrastructure verdict. Neoveruje host-published request, business write/read ani persistence po recreate, ak tieto testy nie sú samostatne vykonané.

Po `up --wait` preto nasleduje:

```bash
curl -fsS http://127.0.0.1:18080/version | jq .
curl -fsS -X POST ... /payments
curl -fsS ... /payments/pay-100
```

## 17. Incident: container bol healthy so starou konfiguráciou

Deployment zmenil `CONFIG_GENERATION` z `cfg-100` na `cfg-101`. Operator vykonal `docker restart`, nie recreate. Rovnaký container object dostal rovnaké environment values z create času.

Healthcheck testoval iba `/readyz`, ktorá zostala zelená. Team predpokladal, že nová config je active.

`docker inspect` aj `/version` ukázali `cfg-100`. Oprava vytvorila nový container z nového effective modelu a deployment automation začala porovnávať loaded generation. Restart sa prestal používať na configuration rollout.

## 18. Incident: healthcheck spôsobil database overload

Readiness endpoint vykonával plnú transakciu a complex query. Pri 200 containers a intervale 5 sekúnd vzniklo 40 transactions za sekundu iba z health checks. Po database spomalení checks timeoutovali, Compose a external automation začali opakovane recreatovať services a tlak sa zvýšil.

Containment zastavil auto-remediation a znížil health frequency. Trvalá oprava rozdelila local process health od bounded dependency readiness a použila lightweight database connection/ping contract. Business canary sa spúšťal menej často samostatnou automation.

## 19. Diagnostika configuration alebo health problému

Zachovaj source, resolved a loaded vrstvy:

```bash
# image defaults
docker image inspect IMAGE --format '{{json .Config.Env}}' | jq .

# effective create environment
docker inspect CONTAINER --format '{{json .Config.Env}}' | jq .

# health definition a state
docker inspect CONTAINER \
  --format '{{json .Config.Healthcheck}} {{json .State.Health}}' | jq -s .

# application loaded state
curl -fsS http://127.0.0.1:18080/version | jq .
```

Pri Compose pridaj `docker compose config --environment` a resolved YAML. Hľadaj prvú vrstvu, kde desired hodnota prestala súhlasiť s observed state-om.

## Čo si z kapitoly odniesť

Image `ENV` je default, container environment je create-time configuration a loaded application configuration je ďalšia vrstva. Missing, empty a explicitné hodnoty musia mať jasnú semantics. Secrets v environment variables sú ľahko inspectovateľné a potrebujú opatrný lifecycle.

Docker process state a health state sú oddelené. Healthcheck má bounded cost a jasný oracle. Local health nepreukazuje external path ani business outcome. Compose `service_healthy` a `up --wait` riešia startup coordination, nie dlhodobú resilience. Configuration rollout sa overuje loaded generation a vyžaduje recreate, ak sa environment containeru zmenil.

## Primárne zdroje

- [Dockerfile `ENV` and `HEALTHCHECK`](https://docs.docker.com/reference/dockerfile/)
- [Docker run environment](https://docs.docker.com/engine/containers/run/#environment-variables)
- [Compose environment variables](https://docs.docker.com/compose/how-tos/environment-variables/)
- [Compose service healthcheck](https://docs.docker.com/reference/compose-file/services/#healthcheck)
- [Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/)
- [Compose `up`](https://docs.docker.com/reference/cli/docker/compose/up/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Docker networks a port publishing](docker-networks-port-publishing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Docker Compose →](docker-compose.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
