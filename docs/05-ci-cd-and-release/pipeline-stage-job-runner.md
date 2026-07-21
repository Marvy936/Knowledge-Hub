# Pipeline, stage, job a runner

CI/CD platformy používajú podobné stavebné prvky, aj keď ich názvy a presná syntax sa líšia. Základným cieľom je premeniť deklarovaný workflow na izolované execution units s explicitnými dependencies, vstupmi, výstupmi a failure semantics.

## 1. Základná hierarchia

Typický model:

```text
pipeline
├── stage: verify
│   ├── job: lint
│   └── job: unit-tests
├── stage: build
│   └── job: build-artifact
└── stage: deploy
    └── job: deploy-staging
```

Význam:

- **pipeline** reprezentuje jeden workflow run viazaný na commit, tag, merge request, schedule alebo inú udalosť,
- **stage** je logická skupina jobs s podobným účelom alebo poradie medzi širšími fázami,
- **job** je najmenšia samostatne plánovaná execution unit,
- **runner** je agent alebo execution capacity, ktorá job skutočne vykoná.

Názvy nie sú univerzálne. Niektoré platformy používajú `workflow`, `step`, `task`, `agent`, `executor` alebo `worker`. Dôležitý je mechanizmus, nie terminológia konkrétneho produktu.

## 2. Pipeline ako instance workflowu

Pipeline nie je iba YAML súbor. YAML alebo iná konfigurácia definuje workflow template; konkrétna pipeline je jeho runtime inštancia s vlastným:

- commit SHA,
- event payloadom,
- actor identity,
- premennými,
- permissions,
- timestamps,
- jobs a ich stavmi,
- artifacts a reports,
- deployment records.

Dva runs rovnakej definície môžu mať odlišný výsledok pre rozdielne inputs, runner image, dependency state alebo environment.

## 3. Stage model

V jednoduchom stage modeli platí:

```text
všetky jobs v stage N musia skončiť
→ môže začať stage N+1
```

Výhody:

- ľahko sa číta,
- poskytuje jasné broad phases,
- prirodzene podporuje paralelizáciu jobs v jednej stage.

Nevýhody:

- môže vytvoriť zbytočné barriers,
- jeden pomalý job blokuje všetky jobs ďalšej stage,
- nevyjadruje presné dependencies medzi jednotlivými jobs.

## 4. DAG execution

Moderné pipeline používajú Directed Acyclic Graph:

```text
lint ───────────────┐
                    ├─> package
unit-tests ─────────┘      │
                           ├─> deploy-staging
integration-tests ─────────┘
```

Job sa spustí, keď sú dokončené jeho explicitné dependencies, nie nutne celá predchádzajúca stage.

DAG skracuje critical path, ale zvyšuje potrebu presne definovať:

- dependency edges,
- artifacts potrebné medzi jobs,
- failure propagation,
- optional dependencies,
- fan-out a fan-in body.

## 5. Job ako execution contract

Dobrý job má explicitne definované:

- image alebo runtime,
- commands alebo steps,
- required inputs,
- dependencies,
- environment variables,
- permissions,
- network access,
- timeout,
- retry policy,
- artifacts a reports,
- success/failure criteria.

Príklad abstraktného jobu:

```yaml
unit_tests:
  image: python:3.12
  needs: [lint]
  script:
    - python -m pip install --require-hashes -r requirements.txt
    - pytest --junitxml=reports/unit.xml
  artifacts:
    when: always
    paths:
      - reports/unit.xml
  timeout: 10m
```

Konkrétna syntax sa líši podľa platformy.

## 6. Steps v jobe

Steps jedného jobu typicky zdieľajú:

- filesystem workspace,
- environment,
- process namespace alebo container,
- credentials pridelené jobu.

Samostatné jobs tieto resources štandardne nezdieľajú. Prenos medzi jobs musí byť explicitný cez artifacts, cache, registry alebo externý service.

Rozdelenie na steps je vhodné pre sekvenčné operácie v jednej trust boundary. Rozdelenie na jobs je vhodné, keď potrebuješ:

- paralelizáciu,
- odlišný runtime,
- odlišné permissions,
- samostatný timeout,
- izoláciu failures,
- samostatné artifacts.

## 7. Runner

Runner prijme job od CI control plane a vykoná ho prostredníctvom konkrétneho executor modelu.

Runner môže byť:

- platformou hostovaný a ephemeral,
- self-hosted,
- statický host,
- ephemeral VM,
- container,
- Kubernetes pod,
- autoscalovaný worker pool.

Runner nie je iba výkonová kapacita. Je to významná security boundary, pretože job môže mať prístup k:

- source code,
- CI tokenom,
- secrets,
- artifact registries,
- cloud credentials,
- interným sieťam,
- deployment endpointom.

## 8. Hosted vs. self-hosted runners

### Hosted runner

Výhody:

- jednoduchá správa,
- typicky čisté ephemeral prostredie,
- automatické patchovanie,
- elastická kapacita.

Nevýhody:

- obmedzené images a hardware,
- sieťová vzdialenosť,
- cena pri veľkom workload-e,
- komplikovanejší prístup do private networks.

### Self-hosted runner

Výhody:

- vlastný hardware a tooling,
- private-network access,
- špeciálne devices alebo licenses,
- optimalizované caches.

Riziká:

- persistence medzi jobs,
- secret leakage,
- nepatchovaný host,
- privilege escalation,
- cross-project contamination,
- capacity bottleneck.

Self-hosted runner pre nedôveryhodné pull requests musí mať veľmi prísnu izoláciu alebo sa nemá používať vôbec.

## 9. Executor

Runner môže používať executor:

- shell na host OS,
- Docker/container,
- virtual machine,
- Kubernetes,
- custom remote execution backend.

Shell executor poskytuje slabšiu izoláciu. Container izoluje filesystem a procesy, ale zdieľa kernel. VM poskytuje silnejšiu boundary za cenu vyššieho startup času.

## 10. Runner labels a scheduling

Jobs môžu požadovať capabilities:

```text
linux
windows
arm64
gpu
trusted-deploy
private-network
```

Scheduler vyberie kompatibilný runner. Labels však nesmú byť jediným security mechanizmom. Dôležité sú aj:

- oddelené runner pools,
- network segmentation,
- identity a permissions,
- protected branch/environment rules,
- ephemeral execution.

## 11. Checkout a workspace

Pred jobom platforma typicky:

1. pripraví workspace,
2. načíta repository,
3. checkoutne commit alebo synthetic merge commit,
4. nastaví metadata a credentials,
5. spustí steps.

Treba rozlišovať:

- branch tip,
- merge request source SHA,
- merge result SHA,
- tag SHA,
- shallow clone,
- submodules,
- Git LFS.

Testovanie iba source branch nemusí odhaliť konflikt alebo integráciu so súčasným main.

## 12. Service containers a dependencies

Job môže potrebovať databázu, broker alebo cache:

```yaml
services:
  - postgres:17
  - redis:8
```

Service lifecycle musí riešiť:

- readiness, nie iba process start,
- health checks,
- deterministic seed,
- ports a DNS names,
- cleanup,
- log collection,
- version pinning.

Fixed sleep nie je readiness check.

## 13. Failure semantics

Job môže skončiť ako:

- success,
- failed,
- canceled,
- timed out,
- skipped,
- manual/waiting,
- allowed failure.

Pipeline musí presne definovať, ktoré failures:

- blokujú downstream,
- sú advisory,
- povoľujú cleanup jobs,
- spúšťajú rollback alebo notification.

`allow_failure` bez ownershipu môže premeniť reálny gate na dekoráciu.

## 14. Cleanup a always-run jobs

Cleanup musí bežať aj pri failure alebo cancel:

- odstrániť ephemeral environment,
- revoke credentials,
- uvoľniť lock,
- uploadnúť logs a reports,
- ukončiť traffic experiment.

Cleanup má byť idempotentný a tolerantný voči čiastočne vytvorenému stavu.

## 15. Timeouts

Timeout patrí na viac úrovní:

- command timeout,
- job timeout,
- pipeline timeout,
- deployment wait timeout,
- approval expiry.

Bez timeoutu môže job držať runner, lock alebo deployment environment neobmedzene dlho.

Timeout musí viesť k diagnostickému dôkazu, nie iba k ukončeniu procesu.

## 16. Retry

Retry je vhodný iba pre identifikovanú transient failure class, napríklad:

- runner provisioning failure,
- krátkodobý registry timeout,
- dočasný network transport error.

Retry nie je vhodný na maskovanie:

- flaky tests,
- deterministického compilation failure,
- authentication error,
- invalid configuration.

Sleduj first-attempt result aj konečný result.

## 17. Concurrency a cancellation

Pri novom commite môže starý pipeline run stratiť hodnotu. CI platforma môže:

- zrušiť superseded run,
- ponechať iba najnovší run pre branch,
- serializovať deployment jobs,
- limitovať paralelné jobs per project alebo runner pool.

Cancellation šetrí capacity, ale nesmie prerušiť nebezpečnú mutation bez cleanupu.

## 18. Resource requests a limity

Runner workload potrebuje CPU, memory, disk, network a niekedy GPU. Chýbajúce limity vedú k noisy-neighbor problémom; príliš nízke limity vytvárajú nestabilné buildy.

Sleduj:

- queue time,
- startup time,
- execution time,
- CPU throttling,
- memory OOM,
- disk pressure,
- cache download/upload čas.

## 19. Reports vs. artifacts

Report je štruktúrovaný výstup interpretovaný platformou, napríklad:

- JUnit test report,
- coverage report,
- SAST result,
- dependency scan,
- deployment metadata.

Artifact je uložený súbor alebo bundle. Jeden output môže byť oboje, ale platformové správanie sa líši.

## 20. Trust boundaries medzi jobs

Rozdelenie pipeline na jobs umožňuje oddeliť permissions:

```text
build job
- read source
- write artifact

security verification job
- read artifact
- no production access

deploy job
- read verified artifact
- scoped environment credential
```

Jedna privileged job s buildom, testom a deployom spája príliš veľa práv a zvyšuje blast radius.

## 21. Observability pipeline

Minimálne sleduj:

- pipeline success rate,
- first-attempt success rate,
- duration a p95 duration,
- queue time,
- runner utilization,
- flaky job rate,
- retry rate,
- cancellation rate,
- failure distribution podľa stage/job,
- artifact upload failures.

Pipeline je produkčný systém pre delivery a potrebuje vlastnú observability.

## 22. Troubleshooting

### Job čaká v queue

Over:

- dostupnosť compatible runnera,
- labels/tags,
- concurrency limit,
- protected-runner pravidlá,
- autoscaler,
- organization quota.

### Job funguje lokálne, nie v CI

Porovnaj:

- runtime image,
- architecture,
- environment variables,
- filesystem case sensitivity,
- working directory,
- network access,
- clock/timezone,
- dependency versions,
- resource limits.

### Downstream job nevidí súbor

Workspace sa medzi jobs automaticky nezdieľa. Over artifact declaration, upload, dependency a download path.

### Pipeline je pomalá

Zmeraj critical path. Neoptimalizuj súčet všetkých job durations, ale najdlhšiu dependency cestu od triggeru po výsledok.

## 23. Časté omyly

### „Stage a job sú to isté“

Stage je logická alebo ordering vrstva; job je plánovaná execution unit.

### „Runner je iba server s agentom“

Runner je security, isolation a capacity boundary.

### „Viac paralelizácie vždy zrýchli pipeline“

Môže zvýšiť queueing, contention, API throttling a artifact overhead.

### „Allowed failure je vyriešený problém“

Iba mení rozhodovaciu policy. Failure musí zostať viditeľný a vlastnený.

## 24. Kontrolné otázky

1. Aký je rozdiel medzi pipeline, stage, job, step, runner a executorom?
2. Kedy stage barrier zbytočne predlžuje critical path?
3. Čo musí obsahovať job execution contract?
4. Aké riziká má self-hosted shell runner?
5. Prečo sa workspace medzi jobs nemá považovať za zdieľaný?
6. Ako oddelíš build a deployment trust boundary?
7. Kedy je retry legitímny a kedy maskuje chybu?
8. Ako navrhneš cleanup pri cancel alebo timeout-e?
9. Aké metriky odhalia runner capacity bottleneck?
10. Prečo je synthetic merge commit dôležitý pre merge request validation?

## Glossary impact

Relevantné pojmy: pipeline, stage, job, step, runner, executor, DAG, critical path, runner pool, service container, synthetic merge commit, allowed failure, pipeline queue time a job timeout.
