# Docker Compose

Docker Compose je application-model a bounded reconciliation nástroj nad Docker Engine. Nevykonáva iba „spustenie YAML“. Najprv skladá sources, interpolation, includes a overrides do **resolved modelu**, potom tento model aplikuje pod konkrétnou **project identity** na containers, networks, volumes a ďalšie objects.

Dominantný lifecycle:

```text
application intent a source inventory
→ interpolation, include, extends a merge
→ resolved Compose model subject
→ project a Docker context identity
→ resource ownership a destructive-scope plan
→ image pull/build eligibility
→ create/recreate a startup ordering
→ service health, readiness a one-shot verdicts
→ application/business verification
→ bounded update reconciliation
→ down, orphan handling, retention a cleanup
```

Compose command success nie je automaticky application success. Rovnako `down` nemusí byť harmless cleanup: pri nesprávnom projekte alebo `-v` môže odstrániť authoritative state.

## 1. Atlas scenár

Atlas Payments stack:

```text
Compose source revision: CP-44
Compose plugin version: 2.x subject CV-18
Docker context/daemon: prod-engine-01
project name: atlas-payments-prod
resolved model digest: CM-118
application release: payments-api@sha256:I44
configuration epoch: CE-118
frontend network: atlas-payments-prod_frontend
backend network: atlas-payments-prod_backend
external volume: atlas-payments-prod-ledger
migration ID: M27
expected services: proxy, api, db, migrate
project generation: PG-203
```

Úspešný deployment:

```text
resolved model je policy-valid
→ exact images sú pullable a verified
→ external resources prejdú preflightom
→ migration M27 skončí práve raz
→ db je semanticky ready
→ api načíta CE-118 a dosiahne readiness
→ proxy/client path prejde
→ project resource inventory zodpovedá modelu
→ staré/orphan resources sú bezpečne retired
```

## 2. Compose source subject

Source inventory zahŕňa:

```text
base compose file a digest
override files a poradie
include/extends sources a immutable identity
project directory
interpolation environment a `.env` identity
CLI options a profiles
Compose version/features
Docker context/daemon
image/build references
external resource contracts
```

Review jedného `compose.yaml` nestačí, ak production command pridáva ďalšie files alebo profiles.

## 3. Resolved model

Compose najprv vytvorí effective model:

```text
sources
+ interpolation
+ merge/override rules
+ profiles
+ includes/extends
→ resolved services, networks, volumes, configs a secrets
```

Over:

```bash
docker compose \
  -f compose.yaml \
  -f compose.production.yaml \
  --project-name atlas-payments-prod \
  config
```

Resolved model subject má obsahovať digest a non-secret summary:

- service/image digests;
- commands/entrypoints;
- ports a host bind addresses;
- mounts a external resource names;
- networks a aliases;
- environment source provenance;
- healthchecks a dependencies;
- security/resource settings;
- profiles a replicas;
- orphan/destructive policy.

## 4. Merge a override semantics

Nie všetky fields sa skladajú rovnako. Mappings môžu merge-nuť, sequences sa môžu appendovať alebo mať špeciálne semantics a fields ako `command`, `entrypoint` či `healthcheck.test` sa typicky nahrádzajú.

Príklad nebezpečného override-u:

```yaml
services:
  db:
    ports:
      - "5432:5432"
    volumes:
      - ./debug-data:/var/lib/postgresql/data
```

Top-level production file môže vyzerať bezpečne, ale resolved model publikuje DB a mení data source. Policy musí vyhodnocovať resolved model, nie fragmenty.

## 5. Project identity

Project identity ovplyvňuje generated names, labels a lifecycle scope:

```text
<project>_<service>_<replica>
<project>_default
<project>_<volume-key>
```

Project name môže pochádzať z CLI, top-level `name`, environmentu alebo directory. V automation ho nastav explicitne:

```bash
docker compose --project-name "pr-${CI_PIPELINE_ID}" up -d
```

Project collision môže spôsobiť, že dva pipelines alebo environments vytvárajú, recreatujú alebo mažú rovnaké resources.

## 6. Service nie je container

Service je desired runtime definition. Container je konkrétna Engine object instance z tejto definition.

```text
service api
→ container generation api-1 / ID C203
→ task/process PID 1822
→ health generation HG-992
```

Pri update môže Compose container nahradiť. Persistent data, service DNS identity a external clients musia replacement tolerovať.

## 7. Image a build boundary

Production model má preferovať vopred vytvorený exact artifact:

```yaml
services:
  api:
    image: registry.example.com/atlas/payments-api@sha256:I44
```

`build:` na runtime hoste rozširuje deployment subject o source context, builder, cache a credentials. To obchádza artifact promotion, ak production host vytvorí nový image z mutable source.

Ak sú `build` aj `image`, over command a pull/build policy. Názov tagu nepreukazuje, ktorý digest bol vytvorený alebo spustený.

## 8. Resource ownership plan

Každý top-level object potrebuje ownera:

| Resource | Compose ownership | Preflight/cleanup dôsledok |
|---|---|---|
| Project network | Compose-managed | môže sa vytvoriť/odstrániť s projectom |
| Project volume | Compose-managed | `down -v` ho môže odstrániť |
| External volume | iný owner | Compose ho nemá vytvoriť ani zmazať |
| External network | iný owner | treba overiť environment a policy |
| Bind mount | daemon-host owner | path, permissions a data identity mimo Compose |
| Image digest | registry/release owner | Compose ho konzumuje, nemá ho mutovať |

`external: true` nie je iba syntax; je ownership transfer.

## 9. Create a update reconciliation

`docker compose up` typicky:

```text
read resolved model
→ identify project resources podľa labels/names
→ pull/build podľa policy
→ create missing networks/volumes
→ create alebo recreate changed containers
→ start podľa dependency conditions
→ podľa options čakať na health
→ report command verdict
```

Compose nie je nepretržitý control loop. Po skončení commandu nemusí korigovať manual drift, host failure alebo neskoršiu dependency outage.

## 10. Recreate decision a change subject

Container môže byť recreated pri zmene image/configuration. Recreate subject má zahŕňať:

- old/new container config hash;
- image digest;
- environment/config epoch;
- mounts/networks;
- command/entrypoint;
- security/resource options;
- project generation;
- persistent-state compatibility.

Zmena mutable tagu nemusí byť zrejmá bez pull policy a digest correlation. Preferuj exact digest a explicitný rollout.

## 11. Startup ordering nie je runtime dependency management

Krátke `depends_on` riadi ordering. Dlhá forma môže čakať na:

- `service_started`;
- `service_healthy`;
- `service_completed_successfully`.

To nerieši neskorší restart DB, connection loss ani application retry. `depends_on` je create/start transition, nie permanentný service manager.

## 12. One-shot service a migration verdict

```yaml
services:
  migrate:
    image: payments-api@sha256:I44
    command: ["migrate", "M27"]

  api:
    image: payments-api@sha256:I44
    depends_on:
      migrate:
        condition: service_completed_successfully
```

Migration potrebuje:

```text
stable migration ID
single-writer lock/ledger
old/new schema compatibility
structured success/failure result
unknown-outcome reconciliation
rerun/recovery semantics
```

Compose ordering nie je distributed lock. Paralelné projects môžu spustiť rovnakú migration súčasne.

## 13. Health, wait a application acceptance

`up --wait` alebo health conditions môžu potvrdiť Compose health states. Acceptance však potrebuje aj:

- expected service/container inventory;
- process-loaded configuration;
- external/client-path test;
- data identity a migration epoch;
- forbidden exposure test;
- exact image digest correlation.

Green `docker compose ps` nepreukazuje business transaction.

## 14. Networks a publication v resolved modeli

```yaml
services:
  proxy:
    ports:
      - "127.0.0.1:18080:8080"
    networks: [frontend]

  api:
    networks: [frontend, backend]

  db:
    networks: [backend]

networks:
  frontend:
  backend:
    internal: true
```

Segmentation má nasledovať communication graph. `ports` vytvára host publication; `expose` nie. Interná communication používa service DNS a container port.

## 15. Volumes, bindy a destructive scope

```yaml
services:
  db:
    volumes:
      - type: volume
        source: ledger-data
        target: /var/lib/postgresql/data

volumes:
  ledger-data:
    external: true
    name: atlas-payments-prod-ledger
```

Pre external data vykonaj preflight. Pre project-managed volume musí cleanup policy explicitne rozhodnúť, či je ephemeral alebo authoritative.

```bash
docker compose down -v
```

je destructive operation nad project-owned volumes, nie bežný univerzálny cleanup.

## 16. Profiles

Profiles menia active service inventory:

```yaml
services:
  debug:
    profiles: [debug]
```

Debug/admin profile môže zaviesť broad port, host mount alebo privileged mode. Deployment subject musí zaznamenať active profiles a policy ich musí kontrolovať.

Core service nemá byť skrytá za profilom, ktorý sa ľahko zabudne aktivovať.

## 17. Include a extends trust boundary

Transitive model môže priniesť:

- mutable image/build source;
- host root/socket mount;
- devices alebo privileged mode;
- broad ports;
- external volumes/networks;
- command/entrypoint override;
- secret/env sources.

Compose file je privilegovaná executable configuration. Nedôveryhodný model nespúšťaj na produkčnom alebo developer hoste s citlivými credentials bez full resolved audit-u.

## 18. Scaling boundary

```bash
docker compose up -d --scale worker=3
```

Scaling potrebuje:

- žiadny fixed `container_name`;
- collision-free port model;
- stateless alebo explicitne partitioned state;
- concurrency-safe jobs;
- discovery/load balancing;
- replica-level health a capacity evidence.

Compose scaling nie je multi-node scheduler ani HA control plane.

## 19. Orphans a rename migration

Orphan je project resource bez zodpovedajúcej service v aktuálnom modeli. `--remove-orphans` môže byť správny cleanup, ale najprv odlíš:

- service rename bez migration;
- old release potrebný na rollback;
- one-shot job s incident logs;
- manuálny diagnostic workload;
- stale unauthorized resource.

Removal má byť subject-bound retirement verdict, nie slepá hygiene operácia.

## 20. Worked failure: CI pipelines zdieľali project a zmazali si resources

Dve pipelines spustili:

```bash
docker compose --project-name atlas-ci up -d
```

Prvá testovala commit A, druhá commit B. Obe menili rovnaké containers, network a volume. Pipeline A na konci vykonala `down -v`.

```text
project identity collision
→ resource labels/names sú rovnaké
→ pipeline B recreatuje A containers
→ A tests bežia nad mixed release
→ A cleanup odstráni B containers a volume
```

Riešenie:

- collision-safe project name per pipeline;
- immutable image subjects;
- ephemeral volume labels/retention;
- cleanup iba vlastného project subjectu;
- cross-project collision assertion pred `up`.

## 21. Worked failure: production override publikoval DB a zmenil data source

Base file definoval internal DB bez ports a external production volume. Debug override pridal:

```yaml
services:
  db:
    ports:
      - "5432:5432"
    volumes:
      - ./debug-db:/var/lib/postgresql/data
```

Production command omylom načítal debug override.

```text
review base file je safe
→ override merge zmení publication a mount
→ relative bind sa resolve-ne na production daemon hoste
→ DB štartuje nad prázdnym debug directory
→ port je vystavený na všetkých interfaces
```

Containment zahŕňa zastavenie writes/trafficu, uzavretie portu, identifikáciu oboch data subjects a audit external accessu. Root control je resolved-model policy.

## 22. Worked failure: migration prebehla dvakrát

Dva Compose projects spustili one-shot `migrate` s `service_completed_successfully`. Migration script nemal ledger ani lock a vytvoril duplicate billing records.

```text
každý project má vlastné ordering
→ oba vidia migrate ako svoj prerequisite
→ Compose nemá cross-project lock
→ side effect sa vykoná dvakrát
```

Oprava je stable migration identity, database lock/ledger, unknown-outcome reconciliation a business invariant verification.

## 23. Causal walkthrough: `compose up` je green, ale aplikácia používa nesprávny stack

### Symptóm

Deployment command skončí úspešne. API je healthy, ale používa staging DB a client sa pripája na starý proxy container.

### Zafixuj Compose subject

```text
Docker context/daemon
Compose version
files/includes/overrides a poradie
active profiles
interpolation environment
resolved model digest
project name/directory
service image digests
container IDs/config hashes
network/volume physical identities
configuration/data/migration epochs
health a client-path evidence
```

### Competing hypotheses

1. aktívny Docker context smeruje na iný daemon;
2. project name je odlišný a vytvoril paralelný stack;
3. override/include zmenil DB env alebo volume;
4. mutable tag/local image spustil starý digest;
5. existujúci container nebol recreated;
6. proxy port patrí orphan/starej service;
7. external volume/network smeruje na staging;
8. healthcheck je shallow;
9. `depends_on` potvrdil iba startup, nie semantic readiness;
10. DNS/client cache smeruje na starú endpoint generation.

### Discriminating observation points

- `docker context show` a daemon identity;
- exact deployment command history;
- `docker compose ... config` pre rovnaký source environment;
- project labels a `docker compose ls/ps/images`;
- container inspect image/config hash/mounts/networks;
- Engine events create/recreate/remove timeline;
- data-ID/configuration/migration markers;
- port owner a packet/client path;
- process-loaded downstream identities;
- external transaction a DB audit.

### Containment

Zastav writes a traffic cutover. Nevykonávaj `down -v` ani `--remove-orphans`, kým nie je známy project/data ownership. Zachovaj resolved model a object inventory.

### Recovery

- wrong context → prepnúť na explicitný trusted daemon a auditovať zasiahnutý host;
- wrong project → identifikovať oba stacks a vykonať controlled traffic/data recovery;
- bad override → opraviť source inventory a policy, potom recreate;
- stale image → pull exact digest a over provenance;
- stale container → bounded recreate s data compatibility preflightom;
- wrong external resource → opraviť mapping po data-ID/environment kontrole;
- orphan proxy → drain/remove podľa endpoint generation;
- shallow health → doplniť semantic readiness a external verification.

### Over pôvodný outcome

Potvrď exact project/container/image subjects, production data/config epochs, expected service/network/volume inventory a end-to-end payment transaction. Forbidden staging access a broad ports musia byť absent.

### Posuň control skôr

Pridaj immutable Compose source manifest, explicitný context/project, resolved-model digest a policy, resource-owner inventory, exact image digests, preflight external resources a subject-bound acceptance/cleanup gates.

## 24. CI/deployment flow

```text
validate source syntax
→ resolve exact model
→ redact a archive model subject
→ policy nad ports/mounts/security/images
→ assert context/project uniqueness
→ preflight external resources
→ pull exact images
→ apply `up`
→ wait na bounded health/one-shot verdicts
→ integration/business tests
→ collect evidence
→ cleanup iba owned ephemeral resources
```

Pri failure zachovaj `ps`, logs, inspect, events, resolved model a data identity evidence pred cleanupom.

## 25. Referenčný object katalóg

| Compose koncept | Effective identity | Hlavná failure boundary |
|---|---|---|
| Source set | files/includes/overrides/profiles | hidden transitive config |
| Resolved model | canonical model digest | review fragmentu namiesto reality |
| Project | name + daemon/context | collision alebo parallel stack |
| Service | resolved runtime definition | service ≠ container generation |
| Container | Engine ID/config hash/image digest | stale/mixed instance |
| Managed volume/network | project-labeled object | destructive cleanup |
| External resource | explicit external name/owner | wrong environment/compatibility |
| One-shot service | command + operation ID/result | duplicate/unknown side effect |
| Orphan | project resource outside model | unsafe removal alebo stale exposure |

## 26. Praktické controls

- pinuj Compose version/features;
- explicitne definuj Docker context a project name;
- inventarizuj všetky files/includes/overrides/profiles;
- vyhodnocuj canonical resolved model;
- používaj exact image digests v deployment modeli;
- zakáž production build z mutable runtime-host source-u;
- policy-checkuj ports, mounts, devices, privileged a socket access;
- preflightuj external resources a data identity;
- daj migrations stable ID a external concurrency control;
- viaž health a tests na container/project generation;
- používaj unique project names v CI;
- chráň `down -v`, prune a orphan removal;
- oddeľ development/debug profiles od production;
- overuj client path aj forbidden exposure.

## 27. Kontrolné otázky

1. Prečo review top-level Compose file-u nestačí?
2. Čo tvorí resolved Compose model subject?
3. Ako project name ovplyvňuje resource identity a cleanup scope?
4. Ako sa líši service od container generation?
5. Prečo `up` nie je continuous reconciliation controller?
6. Čo `depends_on` rieši a čo nerieši?
7. Prečo one-shot migration potrebuje lock/ledger mimo Compose ordering-u?
8. Ako `external: true` mení ownership?
9. Prečo `down -v` a `--remove-orphans` potrebujú inventory?
10. Aké dôkazy odlíšia wrong context, wrong project, bad override a stale container?

## Glossary impact

Relevantné pojmy: Compose source subject, resolved Compose model subject, Compose project generation, Compose resource ownership plan, Compose reconcile operation, Compose container generation, external resource preflight, one-shot operation subject, Compose destructive scope, project collision incident, Compose acceptance subject a resolved-model policy.

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
