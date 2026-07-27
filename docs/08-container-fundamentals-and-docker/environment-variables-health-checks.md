# Environment variables a health checks

Environment variables a health checks riešia dve odlišné runtime otázky:

1. **S akou effective configuration process skutočne vznikol a čo načítal?**
2. **Akú schopnosť process v danom čase preukázal a z ktorého observation pointu?**

Ani resolved Compose YAML, ani status `healthy` samy osebe nepreukazujú správny production outcome.

Dominantný lifecycle:

```text
configuration intent a schema
→ source inventory a precedence
→ resolved configuration subject
→ container create snapshot
→ startup validation a secret/identity resolution
→ process-loaded effective state
→ health-probe subject a execution
→ health history a readiness decision
→ external/client-path verification
→ configuration rotation, recreate, rollback alebo recovery
```

Configuration a health evidence musia patriť rovnakému container, image, project a runtime generation.

## 1. Atlas scenár

Atlas Payments release používa:

```text
image digest: payments-api@sha256:I44
Compose project: atlas-payments-prod
container generation: CG-203
configuration schema: CFG-v9
configuration epoch: CE-118
secret epoch: SE-52
expected DB target: payments-prod-db:5432
runtime mode: production
process-loaded configuration digest: RC-118
healthcheck version: HC-v4
health generation: HG-992
```

Configuration sources:

```text
image ENV defaults
compose.production.yaml
env_file: config/production.env
CI-provided interpolation values
runtime secret file
application defaults
```

Úspešný outcome:

- všetky required fields prejdú schema validation;
- process načíta production DB identity, nie iba syntakticky validnú URL;
- secrets majú správnu epoch a nie sú vypísané do evidence;
- healthcheck overí lacnú lokálnu schopnosť procesu;
- external synthetic request overí skutočný client path;
- zmena configuration vytvorí novú container/process generation;
- rollback vie obnoviť kompatibilný config aj secret subject.

## 2. Configuration subject

Rekonštruovateľný subject obsahuje:

```text
image digest a image ENV defaults
Compose files/includes/overrides a digests
project directory a project name
interpolation environment source
runtime env_file sources a digests
explicit service environment
CLI overrides
mounted config/secret identities a epochs
application schema/default version
container ID a creation time
process-loaded config digest/epoch
```

Bez source inventory môže rovnaký názov `DATABASE_URL` pochádzať z piatich vrstiev a reviewer nevie, ktorá hodnota vyhrala.

## 3. Build-time a runtime configuration

Rozlišuj:

```text
Dockerfile ARG
→ build execution input; nie runtime config ani secret mechanism

Dockerfile ENV
→ default uložený v image configuration

Compose interpolation
→ tvorí resolved Compose model

Compose environment/env_file
→ vstup do container process environmentu

mounted config/secret
→ filesystem-based runtime input

application default
→ interný fallback, často posledná precedence vrstva
```

Hodnota použitá na interpolation sa automaticky nestáva environmentom procesu:

```yaml
services:
  api:
    image: payments-api:${IMAGE_TAG}
    ports:
      - "${HOST_PORT}:8080"
```

`IMAGE_TAG` a `HOST_PORT` formujú model. Do procesu vstúpia iba vtedy, ak sú samostatne deklarované v `environment` alebo inom runtime kanáli.

## 4. Source precedence a provenance

Effective value nie je iba výsledný string. Potrebuje provenance:

```text
field name
source layer a path
source generation/digest
precedence reason
sensitive marker
default/null/empty semantics
validation verdict
```

Compose precedence môže zahŕňať explicitné CLI values, interpolated `environment`, literal `environment`, `env_file`, image `ENV` a application defaults. Presný resolved model over nástrojom, nie pamäťou:

```bash
docker compose config
docker compose config --environment
```

Resolved output môže obsahovať secrets. Pre evidence publikuj redacted manifest s názvami, source identities, epochs a hashes, nie plaintext values.

## 5. Missing, empty, default a invalid

Tieto states sú odlišné:

```text
FIELD nie je definovaný
FIELD=
FIELD=explicit-value
FIELD používa application default
FIELD je syntakticky prítomný, ale semanticky nesprávny
```

Schema musí definovať:

- required/optional;
- type a range;
- allowed enum;
- empty/null semantics;
- cross-field constraints;
- environment-specific restrictions;
- deprecated aliases;
- fail-open alebo fail-closed behavior.

Production application nemá potichu prejsť na `localhost`, staging endpoint alebo debug mode pri missing required value.

## 6. Startup validation

Process má pred readiness validovať napríklad:

```text
APP_MODE == production
APP_PORT je integer 1–65535
DATABASE_URL patrí expected environmentu
TLS_CERT_PATH a TLS_KEY_PATH existujú spolu
secret epoch nie je expirovaná
mounted file owner/mode je prijateľný
žiadne conflict alebo deprecated fields
```

Validation error má pomenovať field a reason bez vypísania secretu. Invalid configuration je configuration verdict, nie dôvod na nekonečný restart loop.

## 7. Process environment je create-time snapshot

Container process dostane environment pri create/start. Zmena `.env`, shell variable alebo env file na hoste bežne nezmení už bežiaci process:

```text
host source sa zmení
→ existujúci container config zostáva rovnaký
→ process environment zostáva rovnaký
→ iba nový create/recreate môže dostať novú hodnotu
```

Preto configuration rollout potrebuje:

```text
new resolved subject
→ compare s active container subjectom
→ create/recreate
→ startup validation
→ process-loaded verification
→ health/readiness
→ traffic acceptance
→ retirement starej generation
```

## 8. Secret delivery boundary

Environment values môžu uniknúť cez:

- container inspection;
- process/proc inspection;
- child processes;
- crash dumps;
- debug endpoints;
- application logs;
- CI output/support bundles;
- healthcheck output.

Preferuj short-lived workload identity alebo mounted secret s úzkym scope-om, ak platforma a threat model dovoľujú. Názov `secret` alebo env file mimo Git-u automaticky nerieši rotation, revocation, audit ani plaintext exposure.

Secret evidence má používať logical ID a epoch:

```text
payments-db-password / SE-52 / loaded=true / plaintext omitted
```

## 9. Process-loaded effective state

Container inspection ukazuje create configuration, nie nevyhnutne to, čo application reálne načítala. Application môže:

- ignorovať field;
- čítať iný config file;
- použiť interný default;
- načítať stale cached value;
- zlyhať pri secret resolution a pokračovať v degraded režime;
- reloadnúť config neskôr.

Silnejší verifier publikuje non-secret runtime identity:

```text
configuration epoch
database logical target
enabled feature-set digest
secret epoch
loaded-at timestamp
application version
```

To odlišuje **declared**, **container-configured** a **process-loaded** state.

## 10. Health subject

Healthcheck subject obsahuje:

```text
container ID/generation a image digest
healthcheck source a version
command/exec form
runtime UID/GID, environment a PATH
working directory a filesystem dependencies
network namespace a target endpoint
interval/timeout/retries/start period
output-redaction contract
health history timestamps/verdicts
```

Manuálny command spustený ako root v interactive shelli nie je rovnaký subject ako automatický healthcheck pod runtime userom.

## 11. Process state, health a readiness

```text
created
running
starting
healthy
unhealthy
exited
ready pre traffic
business-correct
```

Sú to odlišné axes. `running` znamená, že PID 1 žije. Docker `healthy` znamená, že zvolený command opakovane vrátil success podľa timing policy. Ani jedno automaticky neznamená, že reálny klient úspešne dokončí payment request.

## 12. Liveness, readiness, startup a dependency health

Koncepty:

- **liveness** — process dokáže pokračovať;
- **startup** — inicializácia ešte prebieha alebo skončila;
- **readiness** — instance má prijímať traffic;
- **dependency health** — vzdialená služba odpovedá;
- **business correctness** — kritický user outcome funguje.

Standalone Docker health status je jeden channel. Preto vedome vyber, ktorú schopnosť reprezentuje, a zvyšné oracles rieš deployment/controller/external monitoring vrstvou.

## 13. Healthcheck command a runtime context

Exec forma:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD ["/usr/local/bin/payments-api", "healthcheck"]
```

Health executable musí:

- existovať v final image;
- fungovať pod runtime userom;
- mať bounded timeout;
- nevyžadovať secret output;
- vracať truthful exit status;
- nezaťažovať application neprimerane.

Shell forma pridáva shell parsing, PATH a quoting boundary. Celý debug toolchain nepridávaj iba kvôli healthchecku.

## 14. Timing a hysterézia

Parametre:

```text
interval
timeout
retries
start_period
start_interval, ak je podporovaný
```

Musia vychádzať z reálneho startup a response-time distribution. Príliš agresívna probe vytvorí false unhealthy a load. Príliš voľná odďaľuje detection.

Health transition je hysterézny state machine, nie jeden request:

```text
starting
→ success → healthy
→ consecutive failures → unhealthy
→ later success → healthy
```

## 15. Čo má healthcheck overovať

Dobrý local check overuje lacnú schopnosť, ktorú application vlastní:

- event loop/worker reaguje;
- local HTTP/socket endpoint odpovedá;
- required local config bol načítaný;
- process vie vykonať malú internú operáciu.

Nepripájaj bez rozmyslu celý vzdialený dependency graph. Ak analytická služba zlyhá a healthcheck označí API za dead, automatizácia môže reštartovať zdravé instances a zosilniť incident.

## 16. Health output ako exposure path

Docker uchováva health history a output inspectom. Probe nesmie vypísať:

- authorization headers;
- connection strings;
- response bodies s osobnými dátami;
- secret values;
- rozsiahle debug dumps.

Výstup má byť krátky, redacted a diagnosticky užitočný, napríklad error code a non-secret dependency ID.

## 17. Compose `depends_on`

```yaml
services:
  api:
    depends_on:
      db:
        condition: service_healthy
```

Toto riadi startup ordering podľa observed condition. Nerieši:

- permanentnú availability DB;
- reconnect po replacement-e;
- runtime network partition;
- retry/backoff;
- transaction semantics;
- application graceful degradation.

Application musí dependency failure zvládať aj po úspešnom štarte.

## 18. Health a restart policy

Standalone Docker restart policy sa typicky viaže na process exit, nie priamo na `unhealthy`. Externý watchdog, ktorý bez limitu reštartuje unhealthy containers, môže vytvoriť restart storm.

Remediation policy potrebuje:

```text
health subject a confidence
failure class
restart budget/backoff
stateful-side-effect risk
traffic drain
post-restart verification
escalation threshold
```

## 19. External verification

Local healthcheck dopĺňajú:

- application metrics/logs/traces;
- reverse-proxy/backend eligibility;
- external synthetic request;
- user-facing SLI;
- dependency-specific telemetry;
- exact deployed/configuration correlation.

Local `healthy` pri blocked host port alebo wrong DNS nie je service success. External check zase nemá automaticky určovať liveness, ak failure leží v upstream proxy.

## 20. Worked failure: stale shell override poslal production API na staging DB

Pipeline shell mal exportované:

```text
DATABASE_URL=postgres://staging-db/payments
```

Compose model obsahoval:

```yaml
environment:
  DATABASE_URL: ${DATABASE_URL}
```

Production env file mal správnu hodnotu, ale explicitná interpolation z CI shellu vytvorila effective staging URL.

```text
reviewer číta production.env
→ pipeline shell má vyššie použitý source
→ resolved Compose model obsahuje staging
→ container validuje iba URL syntax
→ healthcheck overí local HTTP endpoint
→ release je healthy, ale zapisuje do staging DB
```

Recovery:

1. zastav writes a traffic;
2. potvrď process-loaded DB logical identity a audit writes;
3. odstráň ambient shell source;
4. vyžaduj environment allowlist a production target assertion;
5. recreate container s novou configuration generation;
6. reconcile wrong-environment records;
7. over business transaction a DB audit.

## 21. Worked failure: `.env` sa zmenil, container ostal na starej secret epoch

Operator aktualizoval env file na `SE-52`, ale neurobil recreate. Existujúci container vytvorený s `SE-51` pokračoval v prevádzke.

```text
source file generation sa zmení
→ container create config sa nemení
→ process environment sa nemení
→ secret provider revoke-ne SE-51
→ application začne zlyhávať
```

Oprava je explicitný configuration rollout a loaded-epoch verifier, nie restart náhodného procesu bez kontroly subjectu.

## 22. Worked failure: dependency-coupled health vytvoril restart storm

API healthcheck volal vzdialenú analytics service bez timeoutu. Pri jej incidente checks timeoutovali, watchdog reštartoval všetky API containers a nové instances súčasne otvárali DB/cache connections.

```text
cudzia dependency zlyhá
→ local liveness je označená ako unhealthy
→ broad restart remediation
→ connection storm
→ API incident sa rozšíri
```

Healthcheck má rozlišovať local liveness od optional dependency statusu. Dependency evidence patrí do telemetry/readiness/degradation policy s bounded remediation.

## 23. Causal walkthrough: container je healthy, ale používa nesprávnu configuration

### Symptóm

Atlas API má Docker status `healthy`, no produkčné requests používajú staging feature flags a DB endpoint.

### Zafixuj subject

```text
image digest a image ENV
Compose file/include/override digests
project a CLI command
interpolation environment generation
env_file a mounted config identities
container ID/create time
redacted effective value provenance
process-loaded config/secret epoch
healthcheck version/history
business request a downstream audit
```

### Competing hypotheses

1. CI shell override vyhral nad production env file;
2. Compose interpolation a runtime environment boli zamenené;
3. override file prepísal `environment`;
4. container nebol recreated po zmene source-u;
5. image `ENV` alebo application default sa použil pri empty value;
6. process číta iný mounted config path;
7. secret/config service vrátila stale generation;
8. healthcheck overuje iba PID/local endpoint;
9. inspectuje sa iný project/container;
10. application reloadla časť, ale nie celý config subject.

### Discriminating observation points

- exact `docker compose ... config` s rovnakými files/project/env;
- redacted source/preference manifest;
- container inspect create configuration;
- process-loaded non-secret config endpoint/log;
- mount IDs a config checksums;
- container creation time vs. source modification time;
- health command a history;
- DB/feature-service audit podľa workload identity;
- Engine events a recreate timeline.

### Containment

Odstráň instance z trafficu a zastav side-effect writes. Nevypisuj celý environment do incident logu. Zachovaj redacted provenance a downstream audit.

### Recovery

- wrong precedence → odstráň ambient source a explicitne definuj ownera;
- empty/default fallback → fail-fast schema a production constraints;
- stale container → create new generation, nie iba edit source;
- wrong mount → oprav source/destination contract;
- stale external config → refresh/rotate generation a audit identity;
- shallow health → doplň loaded-config assertion a external business oracle.

### Over pôvodný outcome

Potvrď expected configuration a secret epoch, production downstream identities, successful business transaction a forbidden staging access. Health aj external verification musia patriť novej container generation.

### Posuň control skôr

Pridaj immutable/redacted configuration manifest, ambient-variable denylist, environment identity assertions, recreate-on-subject-change, process-loaded config endpoint a subject-bound health/external evidence.

## 24. Referenčný source a health katalóg

| Mechanizmus | Fáza | Hlavná failure boundary |
|---|---|---|
| Dockerfile `ARG` | build | cache/history/log exposure |
| Image `ENV` | artifact default | stale alebo secret metadata |
| Compose interpolation | model resolution | ambient shell/source precedence |
| `environment` / `env_file` | container create | override, empty/default ambiguity |
| Mounted config | runtime filesystem | wrong source/path/permissions/reload |
| Secret provider/file | runtime identity | exposure, stale epoch, revocation |
| Docker healthcheck | runtime observation | shallow oracle, wrong context/timing |
| External synthetic | client-path observation | upstream failure misclassified as liveness |

## 25. Praktické controls

- definuj typed configuration schema a owners;
- udržuj source/provenance inventory;
- eliminuj ambient production overrides;
- rozlišuj missing, empty a default;
- publikuj redacted effective configuration manifest;
- over process-loaded config a secret epochs;
- recreate pri create-time configuration zmene;
- nepoužívaj environment ako default secret channel;
- viaž health evidence na container generation;
- oddeľ liveness, readiness, startup a dependency health;
- udržuj probe lacnú, bounded a redacted;
- overuj critical outcome z external client pathu;
- implementuj dependency retry/reconnect mimo `depends_on`;
- obmedz remediation/restart budget.

## 26. Kontrolné otázky

1. Ako sa líši interpolation od environmentu procesu?
2. Čo tvorí resolved configuration subject?
3. Prečo výsledný string bez provenance nestačí?
4. Ako sa líši missing, empty a application default?
5. Prečo zmena env file-u neovplyvní existujúci process?
6. Čo odlišuje declared, container-configured a process-loaded state?
7. Čo tvorí healthcheck subject?
8. Ako sa líši liveness, readiness, startup a dependency health?
9. Prečo `healthy` nepreukazuje správny production DB target?
10. Aké observation points odhalia stale container alebo ambient override?

## Glossary impact

Relevantné pojmy: runtime configuration subject, configuration source provenance, redacted effective configuration manifest, process-loaded configuration, configuration epoch, configuration recreate boundary, healthcheck subject, health generation, health remediation budget, dependency-coupled health failure a subject-bound runtime verification.

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
