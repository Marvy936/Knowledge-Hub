# Docker Compose

Docker Compose opisuje multi-container application model v deklaratívnom `compose.yaml`. Definuje services, networks, volumes, configs, secrets a ich vzťahy. Compose nie je Kubernetes orchestrator ani image build systém sám osebe; je to application-model a lifecycle nástroj, ktorý používa Docker Engine a BuildKit capabilities.

## 1. Compose application model

Základný súbor:

```yaml
services:
  app:
    image: example:1
    ports:
      - "127.0.0.1:8080:8080"
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

Top-level model môže obsahovať najmä:

- `services`,
- `networks`,
- `volumes`,
- `configs`,
- `secrets`,
- `name`,
- `include` podľa podporovaného Compose workflowu.

Service nie je konkrétny container. Je to požadovaná definícia, z ktorej Compose vytvorí jednu alebo viac runtime inštancií podľa commandu a platform capabilities.

## 2. Compose V2 CLI

Moderný príkaz používa Docker CLI plugin:

```bash
docker compose version
docker compose up -d
```

Legacy standalone binary používal zápis:

```bash
docker-compose
```

Pri dokumentácii a automation preferuj `docker compose`. Zaznamenaj Compose version, pretože nové attributes nemusia fungovať v staršom plugine alebo na odlišnej platforme.

## 3. Compose project

Compose zoskupuje resources do **projectu**.

Project identity ovplyvňuje názvy:

- containers,
- default networku,
- named resources bez explicitného external mena,
- labels,
- lifecycle commandov.

Project name môže pochádzať napríklad z:

- CLI `--project-name`,
- environmentu,
- top-level `name`,
- project directory.

V CI vždy nastav stabilný, collision-safe project name:

```bash
docker compose --project-name "pr-${CI_PIPELINE_ID}" up -d
```

Inak paralelné pipeline môžu meniť rovnaké resources.

## 4. Service definition

Service môže definovať:

- `image` alebo `build`,
- `command` a `entrypoint`,
- `environment` a `env_file`,
- `ports`, `expose`,
- `networks`,
- `volumes`,
- `healthcheck`,
- `depends_on`,
- `restart`,
- `user`, `working_dir`,
- resource a security options,
- profiles,
- labels,
- configs a secrets.

Service-level options sú runtime contract. Image musí zostať použiteľný aj mimo konkrétneho Compose file-u, pokiaľ architektúra nehovorí inak.

## 5. `image` a `build`

Použitie existujúceho artifactu:

```yaml
services:
  app:
    image: registry.example.com/example/app@sha256:...
```

Local build:

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    image: example/app:dev
```

Ak sú uvedené `build` aj `image`, Compose build môže výsledok označiť daným image menom. Pull/build behavior závisí aj od commandu a `pull_policy`.

Production deployment má preferovať vopred vytvorený, testovaný a digestom identifikovaný artifact namiesto build-u priamo na production hoste.

## 6. Commands a image defaults

Compose môže prepísať image metadata:

```yaml
services:
  app:
    command: ["serve", "--port", "8080"]
    entrypoint: ["/usr/local/bin/example"]
```

Rozlišuj:

- Dockerfile `ENTRYPOINT`,
- Dockerfile `CMD`,
- Compose `entrypoint`,
- Compose `command`.

Príliš veľa environment-specific command overrides znamená, že image runtime contract nie je stabilný.

## 7. Networks

Compose štandardne vytvorí project default network. Services v nej môžu komunikovať podľa service name.

```yaml
services:
  app:
    networks: [frontend, backend]

  db:
    networks: [backend]

networks:
  frontend:
  backend:
    internal: true
```

Princípy:

- segmentuj podľa communication graphu,
- nepoužívaj host-published ports pre internú komunikáciu,
- service name je logical discovery identity,
- explicitne kontroluj external network ownership,
- nepripájaj každú service do každej network.

## 8. Ports a `expose`

```yaml
services:
  app:
    ports:
      - "127.0.0.1:8080:8080"
```

Publikuje host port.

```yaml
services:
  app:
    expose:
      - "8080"
```

Dokumentuje/internalizuje container port v application modeli, ale samo osebe nevytvára host publishing.

Pre backend služby bez external clients často nepotrebuješ `ports`.

## 9. Volumes

```yaml
services:
  db:
    image: postgres:17
    volumes:
      - type: volume
        source: db-data
        target: /var/lib/postgresql/data

volumes:
  db-data:
```

Top-level volume deklaruje object. Service mount deklaruje použitie.

External volume:

```yaml
volumes:
  db-data:
    external: true
    name: production-db-data
```

Compose potom nepreberá plný lifecycle ownership. Deployment musí overiť existenciu, schema, permissions a backup.

## 10. Bind mounts

```yaml
services:
  app:
    volumes:
      - type: bind
        source: ./config/app.yaml
        target: /etc/example/app.yaml
        read_only: true
```

Relative source sa vyhodnocuje podľa Compose project/file modelu. Pri remote daemon-e alebo CI workspace môže host path znamenať niečo iné, než operator očakáva.

Production bind mounts používaj úzko a explicitne.

## 11. Configs a secrets

Compose model podporuje `configs` a `secrets`, ale runtime semantics závisia od použitej platformy a deployment režimu.

Príklad:

```yaml
services:
  app:
    configs:
      - source: app-config
        target: /etc/example/app.yaml
    secrets:
      - db-password

configs:
  app-config:
    file: ./config/app.yaml

secrets:
  db-password:
    file: ./secrets/db-password.txt
```

Lokálny file source stále potrebuje:

- bezpečný storage,
- permissions,
- rotation,
- cleanup,
- ochranu CI logs a artifacts.

Názov `secrets` sám osebe negarantuje enterprise secret-manager vlastnosti.

## 12. `depends_on`

Krátka forma:

```yaml
services:
  app:
    depends_on:
      - db
```

Vyjadruje startup/shutdown dependency order, nie application readiness.

Dlhá forma:

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy
        required: true
```

Podporované conditions zahŕňajú podľa Compose modelu:

- `service_started`,
- `service_healthy`,
- `service_completed_successfully`.

Application musí aj po štarte zvládať dependency restart, network partition a transient failure.

## 13. One-shot services

Database migration alebo initialization možno modelovať ako service:

```yaml
services:
  migrate:
    image: example:1
    command: ["migrate"]

  app:
    image: example:1
    depends_on:
      migrate:
        condition: service_completed_successfully
```

Migration potrebuje:

- idempotenciu alebo ledger,
- single-run concurrency control,
- failure evidence,
- compatibility s old/new application version,
- jasný rerun a recovery postup.

Compose ordering nie je distributed lock.

## 14. Healthchecks

```yaml
services:
  db:
    image: postgres:17
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 20
      start_period: 10s
```

Compose healthcheck môže prepísať image default. Pri merge viacerých files sa `healthcheck.test` správa ako override, nie ako zoznam na append.

## 15. Restart policy

```yaml
services:
  app:
    restart: unless-stopped
```

Standalone Engine restart policies sa viažu najmä na process exit a daemon lifecycle. Nezamieňaj ich s orchestration deployment policy, replica managementom alebo automatickým restartom na základe health statusu.

Restart môže skryť crash loop. Sleduj restart count, exit code a logs.

## 16. Environment a interpolation

```yaml
services:
  app:
    image: example:${IMAGE_TAG:?IMAGE_TAG is required}
    environment:
      APP_MODE: ${APP_MODE:-development}
```

Používaj required/default syntax zámerne. Pred spustením:

```bash
docker compose config
docker compose config --environment
```

Resolved output môže obsahovať citlivé hodnoty; riadne ho rediguj.

## 17. Profiles

```yaml
services:
  app:
    image: example:1

  debug:
    image: example-debug:1
    profiles: [debug]
```

Spustenie:

```bash
docker compose --profile debug up
```

Profiles sú vhodné pre optional development/test tools. Core services, bez ktorých application model nedáva zmysel, nemajú byť skryté za nejasným profilom.

## 18. Multiple Compose files

```bash
docker compose \
  -f compose.yaml \
  -f compose.production.yaml \
  config
```

Files sa merge-nú podľa Compose rules. Nie všetky fields sa správajú rovnako:

- mappings sa môžu merge-núť,
- sequences sa môžu appendovať alebo mať special semantics,
- `command`, `entrypoint` a `healthcheck.test` sa typicky override-nú,
- relative paths môžu byť vyhodnotené voči base file/project modelu.

Vždy kontroluj resolved `config`, nie iba jednotlivé fragments.

## 19. `include` a `extends`

### `include`

Importuje celý Compose application model alebo submodel z ďalšieho source-u podľa podporovanej Compose Specification.

### `extends`

Odvodzuje service configuration z inej service definition.

Riziká:

- transitive host mounts,
- privileged settings,
- remote mutable sources,
- nečakané networks/volumes,
- skrytý command alebo image override.

Compose file je executable infrastructure configuration. Audituj celý resolved dependency graph, nie iba top-level file.

## 20. Lifecycle commands

### Vytvorenie a spustenie

```bash
docker compose up -d
```

### Stav

```bash
docker compose ps
docker compose top
docker compose images
```

### Logs

```bash
docker compose logs -f --tail=200
```

### Jednorazový command

```bash
docker compose run --rm app migrate
```

### Command v existujúcom containeri

```bash
docker compose exec app sh
```

### Zastavenie a odstránenie

```bash
docker compose down
```

### Odstránenie aj volumes

```bash
docker compose down -v
```

Posledný command môže zmazať persistentné dáta. Nepoužívaj ho bez ownership a backup kontroly.

## 21. `up` reconciliation

Pri `docker compose up` Compose porovnáva application model s existujúcimi project resources a podľa potreby:

- vytvorí chýbajúce containers,
- nahradí containers pri configuration/image zmene,
- vytvorí networks/volumes podľa ownershipu,
- ponechá alebo odstráni orphan resources podľa options.

Compose nie je nepretržitý reconciliation controller. Po skončení commandu typicky neudržiava desired state proti všetkým budúcim zmenám.

## 22. Scaling

```bash
docker compose up -d --scale worker=3
```

Viac replicas vyžaduje:

- žiadne fixed `container_name`,
- žiadny collision host port pre každú repliku,
- stateless alebo správne shardovaný state,
- load-balancing/discovery model,
- concurrency-safe jobs,
- external health a capacity observability.

Compose scaling nie je náhrada za cluster scheduler.

## 23. `container_name`

```yaml
services:
  app:
    container_name: fixed-app
```

Tento attribute často znižuje Compose project isolation a bráni scale-outu. Preferuj project-generated container names a service DNS identity.

Použi fixné meno iba pri presnom external integration requirement-e.

## 24. Resource limits a security

Service môže deklarovať podľa podporovaného runtime modelu:

- CPU a memory limits,
- `user`,
- `read_only`,
- `cap_drop`,
- `security_opt`,
- `tmpfs`,
- `pids_limit`,
- devices,
- privileged mode.

Security baseline:

```yaml
services:
  app:
    image: example@sha256:...
    user: "10001:10001"
    read_only: true
    cap_drop: [ALL]
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp
```

Presné fields a support over podľa Compose/Engine verzie.

## 25. Development watch a bind-mount model

Development Compose môže používať:

- source bind mounts,
- hot reload,
- debug profile,
- build watch/sync capabilities podľa Compose verzie.

Production model má zostať artifact-based. Nevynášaj development host mounts, source code a debugger do production override-u.

## 26. External resources

`external: true` znamená, že resource lifecycle vlastní iný systém.

Pred deploymentom over:

- existence,
- správny environment/account,
- permissions,
- labels/ownership,
- compatibility,
- cleanup zodpovednosť.

Compose `down` external resource typicky neodstráni, čo je správne iba pri jasnom ownership contracte.

## 27. Orphans

Orphan container je project resource zo staršej Compose konfigurácie, ktorý už nemá service v aktuálnom modeli.

```bash
docker compose up -d --remove-orphans
```

Pred removalom over, či nejde o:

- rename service bez migration,
- one-shot job s potrebnými logs,
- manually attached diagnostic container,
- starú verziu potrebnú na rollback.

## 28. CI workflow

Odporúčaný test flow:

1. `docker compose config --quiet`,
2. overiť resolved model a policy,
3. build/pull immutable images,
4. unikátny project name,
5. `up -d --wait` alebo explicitné health čakanie podľa verzie,
6. integration/smoke tests,
7. zhromaždiť `ps`, logs, inspect a events pri failure,
8. `down --remove-orphans`,
9. volume cleanup iba pre ephemeral test data.

Cleanup sa musí vykonať aj po zlyhaní pipeline.

## 29. Trust model

Nedôveryhodný Compose file môže:

- spustiť privileged container,
- mountnúť host root alebo Docker socket,
- pripojiť devices,
- publikovať ports,
- buildnúť nedôveryhodný Dockerfile,
- načítať remote includes,
- exfiltrovať environment a credentials.

Nespúšťaj cudzí Compose model na privilegovanom Docker hoste bez auditu. `docker compose config` pomáha vidieť resolved model, ale nenahrádza source a image trust verification.

## 30. Anti-patterny

### Compose ako production cluster orchestrator bez limitov

Nemá automaticky multi-node scheduling, robustný reconciliation a HA control plane.

### `container_name` pre každú service

Spôsobuje collisions a blokuje scaling.

### Všetky ports publikované na `0.0.0.0`

Zväčšuje exposure bez potreby.

### `depends_on` považovaný za aplikačný retry model

Po štarte dependency môže kedykoľvek zlyhať.

### Secrets commitnuté v `.env`

Private repository nie je secret manager.

### `docker compose down -v` ako bežný cleanup

Môže zmazať authoritative state.

### Production build cez mutable source na runtime hoste

Obchádza artifact promotion a provenance.

### Review iba top-level file-u

`include`, `extends` alebo override môže zaviesť privileged configuration.

## 31. Troubleshooting

### Compose používa iný project než očakávaš

Over:

```bash
docker compose ls
docker compose config
docker compose --project-name expected ps
```

### Service name sa nedá resolve-nuť

Over spoločnú network, service health, aliases a project isolation.

### `depends_on` nezabránil startup failure

Použi `service_healthy` a implementuj application retry. `service_started` neznamená readiness.

### Override file vytvoril neočakávaný model

Spusť celý `docker compose -f ... config` a skontroluj ports, mounts, command, healthcheck, networks a images.

### Volume dáta zmizli

Over project name, volume name, `external`, anonymous volumes a použitie `down -v`.

### Zmena image sa neprejavila

Over tag mutability, pull policy, local image, digest a recreate. Preferuj immutable digest/reference.

### Service je healthy, ale client ju nedosiahne

Over published port, bind address, network path a external synthetic check.

## 32. Kontrolné otázky

1. Čo predstavuje Compose project?
2. Aký je rozdiel medzi service a containerom?
3. Kedy použiť `image` a kedy `build`?
4. Ako sa líši `ports` a `expose`?
5. Čo `depends_on` rieši a čo nerieši?
6. Prečo kontrolovať `docker compose config`?
7. Aké riziká prinášajú multiple files, `include` a `extends`?
8. Prečo `container_name` komplikuje scaling?
9. Čo znamená `external: true` pri resource?
10. Prečo je Compose file privilegovaná executable configuration?

## Glossary impact

Relevantné pojmy: Docker Compose, Compose Specification, Compose project, Compose service, project name, default network, Compose interpolation, Compose profile, Compose merge, Compose include, Compose extends, external resource, orphan container, one-shot service, resolved Compose model a Compose trust model.

## Oficiálna dokumentácia

- [Docker Compose](https://docs.docker.com/compose/)
- [Compose file reference](https://docs.docker.com/reference/compose-file/)
- [Services top-level element](https://docs.docker.com/reference/compose-file/services/)
- [Startup order](https://docs.docker.com/compose/how-tos/startup-order/)
- [Compose trust model](https://docs.docker.com/compose/trust-model/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Environment variables a health checks](environment-variables-health-checks.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: BuildKit a Buildx →](buildkit-buildx.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
