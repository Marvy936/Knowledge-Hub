# Environment variables a health checks

Container image má zostať rovnaký naprieč prostrediami, zatiaľ čo runtime configuration sa dodáva pri vytvorení containeru. Environment variables sú jeden z najbežnejších configuration kanálov. Health check je samostatný runtime contract, ktorým Docker periodicky overuje, či process poskytuje očakávanú základnú schopnosť. Ani jeden mechanizmus nie je automaticky vhodný pre secrets, service discovery alebo plnohodnotné production readiness rozhodovanie.

## 1. Build-time a runtime configuration

Rozlišuj:

- `ARG` — build-time parameter,
- Dockerfile `ENV` — default environment uložené v image configuration,
- `docker run --env` alebo `--env-file` — runtime override,
- Compose interpolation — zostavenie Compose modelu,
- Compose `environment` a `env_file` — environment odovzdané procesu v containeri,
- mounted configuration file,
- runtime secret provider alebo workload identity.

Rovnaký názov môže existovať v niekoľkých vrstvách. Bez explicitného ownershipu je ťažké určiť výslednú hodnotu.

## 2. Dockerfile `ENV`

```dockerfile
ENV APP_PORT=8080
ENV APP_MODE=production
```

Hodnoty:

- sú súčasťou image configuration,
- dedia ich neskoršie build stages, pokiaľ ich nezmeníš,
- dostane ich runtime container ako defaults,
- možno ich prepísať pri vytvorení containeru,
- môžu byť viditeľné cez image/container inspection.

Do `ENV` nepatria reálne passwords, API tokens ani private keys.

## 3. Runtime environment cez CLI

Explicitná hodnota:

```bash
docker run --env APP_MODE=staging example:1
```

Prenesenie hodnoty z client shellu:

```bash
export APP_MODE=staging
docker run --env APP_MODE example:1
```

Environment file:

```text
APP_MODE=staging
APP_PORT=8080
```

```bash
docker run --env-file runtime.env example:1
```

Environment file má byť:

- mimo image-u,
- mimo Git repository, ak obsahuje citlivé hodnoty,
- s kontrolovanými permissions,
- versionovaný iba pri necitlivej configuration,
- validovaný pred deploymentom.

## 4. Unset, empty a missing values

Tieto stavy nie sú rovnaké:

```text
VARIABLE nie je definovaná
VARIABLE=
VARIABLE=explicit-value
```

Application musí mať jasný contract:

- ktoré hodnoty sú required,
- ktoré majú bezpečný default,
- či empty string znamená validnú hodnotu alebo chybu,
- ako sa validuje type, range a format,
- či zlyhá fast pri neplatnej konfigurácii.

Tiché použitie nebezpečného defaultu je horšie než explicitný startup failure.

## 5. Compose interpolation vs. container environment

Compose interpolation nahrádza `${VARIABLE}` pri vytváraní výsledného Compose modelu:

```yaml
services:
  app:
    image: example:${IMAGE_TAG}
    ports:
      - "${HOST_PORT}:8080"
```

To neznamená, že `IMAGE_TAG` alebo `HOST_PORT` automaticky existujú vo vnútri containeru.

Container environment sa deklaruje samostatne:

```yaml
services:
  app:
    image: example:${IMAGE_TAG}
    environment:
      APP_MODE: ${APP_MODE}
      APP_PORT: "8080"
```

Resolved model over:

```bash
docker compose config
docker compose config --environment
```

Pred produkčným deploymentom archivuj alebo porovnaj resolved configuration bez secrets.

## 6. Compose `environment`

Mapping forma:

```yaml
services:
  app:
    environment:
      APP_MODE: production
      APP_DEBUG: "false"
```

List forma:

```yaml
services:
  app:
    environment:
      - APP_MODE=production
      - APP_DEBUG=false
```

Mapping je zvyčajne čitateľnejší. Pri booleans a číslach používaj quotes, ak application očakáva string a YAML typing by mohol zmeniť interpretáciu.

## 7. Compose `env_file`

```yaml
services:
  app:
    env_file:
      - ./config/common.env
      - ./config/production.env
```

Neskorší source môže prepísať skorší podľa Compose semantics. `environment` má typicky vyššiu prioritu než hodnoty z `env_file`.

`env_file` pre runtime environment nepleť s project `.env` file používaným pre Compose interpolation.

Prakticky môžu existovať dva odlišné súbory:

```text
.env                         # Compose interpolation
config/application.env       # environment procesu v containeri
```

## 8. Precedence

Výsledná runtime hodnota môže pochádzať z:

1. explicitného CLI override,
2. Compose `environment`,
3. Compose `env_file`,
4. image `ENV`,
5. application defaultu.

Presné Compose precedence pravidlá závisia aj od toho, či hodnota vzniká interpolation alebo explicitným literalom. Preto sa nespoliehaj na pamäť; over resolved model a runtime environment.

```bash
docker compose config
docker compose run --rm app env
```

Pri druhom príkaze zabráň vypísaniu secrets do CI logu.

## 9. Environment variables a secrets

Environment variables môžu uniknúť cez:

- `docker inspect`,
- process inspection,
- crash dump,
- debug endpoint,
- child process,
- application log,
- CI output,
- support bundle.

Pre citlivé hodnoty preferuj:

- secret manager,
- workload identity,
- short-lived token,
- mounted file s úzkymi permissions,
- tmpfs alebo memory-backed delivery podľa threat modelu.

Environment variable môže byť akceptovateľná pri vedomom riziku, ale nie je automaticky secret-safe.

## 10. Configuration validation

Application má pri štarte validovať:

- required variables,
- allowed enum values,
- numeric ranges,
- URL a address format,
- file existence a permissions,
- vzájomné constraints,
- deprecated names,
- neznáme alebo conflict hodnoty podľa policy.

Príklad startup contractu:

```text
APP_PORT: integer 1–65535
APP_MODE: development | staging | production
DATABASE_URL: required v staging/production
TLS_CERT_PATH a TLS_KEY_PATH: musia existovať spolu
```

Validation error má pomenovať configuration field, nie vypísať secret value.

## 11. Runtime reload vs. recreate

Environment procesu sa po jeho spustení bežne nemení. Zmena runtime environment preto typicky vyžaduje:

1. vytvoriť nový container configuration,
2. zastaviť alebo nahradiť starú inštanciu,
3. spustiť novú inštanciu,
4. overiť health a application behavior.

Ak application potrebuje dynamic configuration, použi explicitný reload alebo configuration service contract. Nečakaj, že zmena host `.env` súboru automaticky zmení už bežiaci process.

## 12. Health status model

Container môže byť z pohľadu healthchecku:

- `starting`,
- `healthy`,
- `unhealthy`,
- bez healthchecku.

Process state a health state sú odlišné:

```text
container running + healthy
container running + unhealthy
container exited
```

`running` znamená, že PID 1 žije. Neznamená to, že application prijíma requests alebo má dostupnú dependency.

## 13. Dockerfile `HEALTHCHECK`

Exec forma:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD ["/usr/local/bin/healthcheck"]
```

Shell forma:

```dockerfile
HEALTHCHECK CMD curl --fail http://127.0.0.1:8080/health || exit 1
```

Exec forma odstraňuje implicitný shell a býva predvídateľnejšia. Healthcheck executable musí byť súčasťou image-u a musí fungovať pod runtime userom.

## 14. Healthcheck exit status

Health command používa exit code:

- `0` — success/healthy,
- `1` — failure/unhealthy,
- `2` — rezervovaný význam; nepoužívaj ako bežný stav.

Output commandu sa môže uložiť do health history a zobraziť cez inspection. Nevypisuj doň credentials alebo response bodies s citlivými dátami.

## 15. Timing parameters

Dôležité parametre:

- `interval` — čas medzi kontrolami,
- `timeout` — maximálny čas jednej kontroly,
- `retries` — počet po sebe idúcich failures pred `unhealthy`,
- `start_period` — warm-up obdobie pre startup failures,
- `start_interval` — interval počas startup obdobia, ak ho daná verzia podporuje.

Nastavenie musí vychádzať z reálneho startup a response-time profilu.

Príliš agresívny healthcheck spôsobuje false failures a load. Príliš pomalý odďaľuje detection.

## 16. Čo healthcheck overovať

Dobrý container healthcheck overuje lacnú, lokálne relevantnú schopnosť, napríklad:

- process odpovedá na local endpoint,
- event loop nie je zaseknutý,
- required local file/socket je použiteľný,
- application vie vykonať minimálnu internú operáciu.

Nemal by bez rozmyslu overovať celý external dependency graph. Ak healthcheck aplikácie zlyhá vždy pri výpadku vzdialenej analytickej služby, platforma môže zbytočne reštartovať zdravý process a zhoršiť incident.

## 17. Liveness, readiness a startup

Docker Engine má jeden všeobecný health status, nie plný Kubernetes model samostatných liveness, readiness a startup probes.

Preto odlišuj koncepty:

- **liveness** — process je schopný pokračovať,
- **readiness** — inštancia má prijímať traffic,
- **startup** — application ešte inicializuje,
- **dependency health** — external service je dostupná.

Jeden Docker healthcheck môže reprezentovať iba vedome zvolenú časť tohto contractu.

## 18. Compose healthcheck

Compose môže image healthcheck doplniť alebo prepísať:

```yaml
services:
  app:
    image: example:1
    healthcheck:
      test: ["CMD", "/usr/local/bin/healthcheck"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 20s
```

Image healthcheck možno podľa potreby vypnúť:

```yaml
services:
  app:
    healthcheck:
      disable: true
```

Vypnutie musí mať odôvodnenie; inak sa stráca runtime evidence.

## 19. `depends_on` a health

Compose môže čakať na zdravú dependency:

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:17
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 20
```

Toto rieši startup ordering v Compose lifecycle. Nerieši trvalú dostupnosť dependency po štarte. Application stále potrebuje:

- connection retry,
- timeout,
- backoff,
- circuit breaker alebo graceful degradation podľa use case,
- reconnect po dependency replacement-e.

## 20. Healthcheck a restart policy

Docker health status sám osebe všeobecne neznamená automatický restart unhealthy containeru v standalone Engine modeli. Restart policy sa typicky viaže na process exit, nie priamo na health status.

Ak požaduješ automatickú remediation, potrebuješ explicitný orchestrator alebo controller behavior. Externý script, ktorý bez limitu reštartuje každý unhealthy container, môže vytvoriť restart storm.

## 21. Healthcheck dependencies v image

Ak healthcheck používa `curl`, `wget`, shell alebo database client, tieto tools musia byť v image. To môže zväčšiť attack surface.

Alternatívy:

- application binary s `healthcheck` subcommandom,
- minimalistický statický helper,
- built-in TCP/HTTP probe v orchestration vrstve,
- external monitoring oddelený od image-u.

Nekopíruj celý debugging toolchain iba kvôli jednej kontrole.

## 22. Observability

Health history:

```bash
docker inspect --format '{{json .State.Health}}' <container>
```

Status:

```bash
docker ps
docker inspect <container>
docker events --filter container=<container>
```

Healthcheck dopĺňa, ale nenahrádza:

- application logs,
- metrics,
- traces,
- external synthetic checks,
- user-facing SLI.

Internal healthy status nepreukazuje, že service je dostupná z reálnej client path.

## 23. Anti-patterny

### Secret v image `ENV`

Zostáva v image metadata a môže byť viditeľný inspectionom.

### Rovnaký názov definovaný v piatich sources

Výsledná hodnota je ťažko vysvetliteľná a review nevidí reálny runtime config.

### Healthcheck iba `pgrep process`

Overí existenciu procesu, nie schopnosť obslúžiť request.

### Healthcheck volá vzdialenú dependency bez timeoutu

Check sa zasekne alebo označí application za unhealthy kvôli cudziemu incidentu.

### `depends_on` považovaný za permanentný dependency manager

Rieši create/start ordering, nie celý runtime recovery lifecycle.

### Healthcheck vypisuje response body

Môže uložiť secrets alebo osobné dáta do inspectovateľnej history.

### Zmena `.env` bez recreate

Bežiaci process zostáva so starým environmentom.

## 24. Troubleshooting

### Application používa inú hodnotu než očakávaš

Over:

```bash
docker compose config
docker inspect <container>
docker exec <container> env
```

Pri secrets nepoužívaj neobmedzený výpis do logu.

### Variable je prázdna

Rozlíš missing shell variable, interpolation warning, empty assignment, `env_file`, Compose override a image default.

### Container zostáva `starting`

Over `start_period`, duration checku, timeout, executable, permissions a application startup time.

### Container je `unhealthy`, ale endpoint funguje

Over network namespace, `localhost`, command path, shell quoting, authentication, expected status code a timeout.

### Healthcheck funguje manuálne ako root, ale nie automaticky

Automatický check beží v container context-e s runtime userom, environmentom, PATH a filesystem permissions.

### Dependency je healthy, application sa aj tak nepripojí

Over credentials, database name/schema, DNS cache, connection pool, TLS, application retry a semantic readiness dependency.

## 25. Kontrolné otázky

1. Aký je rozdiel medzi `ARG`, Dockerfile `ENV` a runtime environment?
2. Ako sa líši Compose interpolation od environmentu procesu?
3. Prečo environment variables nie sú ideálny secret channel?
4. Ako overíš výsledný Compose model?
5. Prečo zmena `.env` neovplyvní už spustený process?
6. Aký je rozdiel medzi process state a health state?
7. Čo znamenajú exit codes healthchecku?
8. Ako sa líši liveness, readiness a startup?
9. Čo `depends_on: condition: service_healthy` rieši a čo nerieši?
10. Prečo unhealthy status automaticky nemusí reštartovať container?

## Glossary impact

Relevantné pojmy: runtime configuration, Compose interpolation, container environment, environment precedence, required configuration, Docker healthcheck, health status, start period, liveness, readiness, startup health, health history a configuration recreate.

## Oficiálna dokumentácia

- [Dockerfile `ENV` a `HEALTHCHECK`](https://docs.docker.com/reference/dockerfile/)
- [Environment variables in Compose](https://docs.docker.com/compose/how-tos/environment-variables/)
- [Environment variable precedence](https://docs.docker.com/compose/how-tos/environment-variables/envvars-precedence/)
- [Compose service healthcheck](https://docs.docker.com/reference/compose-file/services/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Docker networks a port publishing](docker-networks-port-publishing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Docker Compose →](docker-compose.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
