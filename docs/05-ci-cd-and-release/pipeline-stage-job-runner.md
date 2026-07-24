# Pipeline, stage, job a runner

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

CI/CD platforma premieňa versionovanú workflow definíciu na konkrétne runtime execution units. Základné pojmy opisujú odlišné vrstvy:

- **Pipeline —** jedna runtime inštancia celého workflowu viazaná na udalosť a presné vstupy.
- **Stage —** logická fáza alebo široká ordering barrier medzi skupinami jobs.
- **Job —** samostatne plánovaná execution unit s vlastným runtime, permissions, timeoutom a výsledkom.
- **Step —** sekvenčná operácia v rámci jedného jobu a spoločného execution contextu.
- **Runner —** agent alebo worker, ktorý prijíma a vykonáva job.
- **Executor —** konkrétny mechanizmus, ktorým runner job izoluje a spúšťa, napríklad shell, container, VM alebo Kubernetes pod.

Typická hierarchia:

```text
pipeline run
├── stage: verify
│   ├── job: lint
│   └── job: unit-tests
├── stage: package
│   └── job: build-artifact
└── stage: deploy
    └── job: deploy-staging
```

Názvy sa medzi platformami líšia. Dôležitý je execution a trust model, nie syntax konkrétneho produktu.

## 2. Workflow definícia verzus pipeline instance

YAML, DSL alebo API objekt typicky definuje **workflow template**. Konkrétna pipeline je jeho runtime inštancia s vlastnou identitou a stavom.

Pipeline instance zahŕňa:

- source commit, tag alebo synthetic merge SHA,
- trigger event a payload,
- actor alebo workload identity,
- workflow/template version,
- vstupné parametre a variables,
- permissions a secret scopes,
- vytvorený DAG,
- jobs, attempts a timestamps,
- artifacts, reports a deployment records,
- policy a approval decisions.

Dva runs rovnakej YAML definície môžu mať odlišný výsledok, ak sa zmení runner image, external dependency, cache, environment, secret version alebo event payload. Preto pipeline provenance musí obsahovať aj runtime inputs, nielen repository commit.

## 3. Pipeline lifecycle

Pipeline typicky prechádza stavmi:

```text
created
→ evaluated/compiled
→ queued
→ running
→ waiting/manual podľa policy
→ success / failed / canceled / timed-out / incomplete
→ artifacts retained alebo cleanup
```

Pred spustením jobs platforma často:

1. načíta workflow definíciu,
2. vyhodnotí conditions a matrix,
3. vytvorí DAG,
4. určí permissions a environments,
5. naplánuje jobs na compatible runners,
6. agreguje výsledky do pipeline verdictu.

Chyba pri parsovaní alebo DAG evaluation je pipeline failure aj bez spustenia jediného jobu.

## 4. Stage model

Stage je široká logická fáza. V jednoduchom modeli:

```text
všetky required jobs v stage N skončia
→ môže začať stage N+1
```

Výhody:

- workflow sa ľahko číta,
- broad phases majú jasný účel,
- jobs v jednej stage sa prirodzene paralelizujú,
- promotion boundaries sú viditeľné.

Nevýhody:

- stage vytvára barrier aj medzi nezávislými jobs,
- jeden pomalý job môže blokovať celý nasledujúci krok,
- skutočné dependencies sa stratia v hrubom poradí,
- critical path sa zbytočne predlžuje.

Stage má význam pre ľudskú čitateľnosť a policy, ale nemá nahrádzať presný dependency graph.

## 5. DAG execution

Directed Acyclic Graph vyjadruje explicitné dependencies medzi jobs:

```text
lint ────────────────┐
                      ├─> package ──> deploy-staging
unit-tests ──────────┘        ▲
                               │
integration-tests ─────────────┘
```

Job sa spustí po dokončení svojich required predecessors, nie nutne po celej predchádzajúcej stage.

DAG musí definovať:

- required a optional dependency edges,
- artifact a report flow,
- failure propagation,
- fan-out a fan-in,
- conditions pri skipped/canceled jobe,
- cleanup edges,
- environment locks a serialization.

Chýbajúci edge môže vytvoriť race alebo spustiť downstream job bez potrebného artifactu. Zbytočný edge predlžuje critical path.

## 6. Critical path

Critical path je najdlhšia dependency cesta od triggeru po required pipeline verdict alebo produkčný deployment.

Príklad:

```text
job A: 2 min → job C: 8 min → job E: 3 min = 13 min
job B: 5 min → job D: 2 min               = 7 min
```

Optimalizovať súčet všetkých job durations môže byť bezvýznamné. Skrátenie jobu mimo critical path nemusí skrátiť pipeline.

Critical path ovplyvňuje:

- stage barriers,
- runner queue time,
- artifact transfer,
- startup a service readiness,
- shard imbalance,
- fan-in čakanie,
- manuálne approvals.

## 7. Job ako execution contract

Job je najmenšia samostatne plánovaná jednotka. Dobrý job explicitne deklaruje:

- runtime image, OS a architecture,
- commands alebo steps,
- source checkout model,
- required inputs a dependencies,
- variables a secret references,
- filesystem a network access,
- identity a permissions,
- CPU, memory, disk a special capabilities,
- timeout a retry policy,
- artifacts a reports,
- conditions a success criteria,
- cleanup a cancellation behavior.

Abstraktný príklad:

```yaml
unit_tests:
  image: python:3.12@sha256:...
  needs: [lint]
  permissions:
    contents: read
  script:
    - python -m pip install --require-hashes -r requirements.txt
    - pytest --junitxml=reports/unit.xml
  artifacts:
    when: always
    paths:
      - reports/unit.xml
  timeout: 10m
```

Konkrétna syntax sa líši, ale execution contract ostáva.

## 8. Steps v jobe

Steps jedného jobu typicky zdieľajú:

- workspace,
- environment variables,
- process/container alebo VM context,
- network namespace,
- credentials pridelené jobu,
- aktuálny working directory.

Preto step nemá byť považovaný za samostatnú security boundary.

Rozdelenie na steps je vhodné pre:

- sekvenčný setup, execute a report flow,
- lepšiu čitateľnosť logu,
- post-step cleanup,
- zdieľanie jedného runtime a workspace.

Rozdelenie na samostatné jobs je vhodné, keď potrebuješ:

- paralelizáciu,
- odlišný runtime alebo architecture,
- odlišné permissions,
- samostatný timeout a retry,
- izoláciu failures,
- samostatné artifacts,
- environment alebo approval boundary.

## 9. Runner a control plane

CI control plane prijme pipeline, vytvorí jobs a priradí ich runners. Runner:

1. získa job lease alebo assignment,
2. pripraví executor environment,
3. načíta source a inputs,
4. poskytne scoped credentials,
5. spustí steps,
6. streamuje logs a status,
7. uploadne artifacts/reports,
8. vykoná cleanup,
9. odošle konečný verdict.

Runner je významná trust boundary, pretože môže mať prístup k source, tokenom, registries, cloud APIs a interným sieťam.

## 10. Runner verzus executor

Runner je agent a scheduling endpoint. Executor určuje izoláciu jobu.

### Shell executor

Spúšťa commands priamo na host OS.

- nízky startup overhead,
- jednoduchý prístup k lokálnym tools a devices,
- slabá izolácia,
- vysoké persistence a cross-job riziko.

### Container executor

Spúšťa job v containere.

- reprodukovateľnejší userspace,
- izolovaný filesystem a processes,
- zdieľaný kernel,
- riziko privileged socketov alebo host mounts.

### Virtual machine executor

Každý job alebo runner používa VM.

- silnejšia izolácia,
- vhodné pre untrusted code alebo citlivé jobs,
- vyšší startup a infra cost.

### Kubernetes executor

Job sa spúšťa v pode.

- elastické scheduling a resource limits,
- network/policy integrácia,
- závislosť od cluster control plane,
- potreba správnej namespace, service account a pod-security izolácie.

Executor choice musí zodpovedať trust levelu, nie iba výkonu.

## 11. Hosted verzus self-hosted runners

### Hosted runners

Výhody:

- typicky ephemeral čisté prostredie,
- správa patchov a capacity platformou,
- jednoduché škálovanie,
- menšie persistence riziko.

Limity:

- obmedzený hardware a images,
- vzdialenosť od private dependencies,
- quotas a cena,
- menšia kontrola nad network a caching.

### Self-hosted runners

Výhody:

- private-network access,
- vlastný hardware, licenses alebo GPU,
- optimalizované images a caches,
- kontrola nad performance profilom.

Riziká:

- zvyškový workspace a processes,
- credential leakage,
- host compromise a persistence,
- nepatchovaný toolchain,
- cross-project contamination,
- capacity bottleneck,
- príliš široký interný network access.

Untrusted pull-request code nemá bežať na persistent privileged runneri bez silnej sandbox boundary.

## 12. Runner pools, labels a scheduling

Jobs deklarujú capabilities, napríklad:

```text
linux
windows
arm64
gpu
trusted-build
protected-deploy
private-network
```

Scheduler vyberá kompatibilný runner podľa labels, capacity a policy.

Labels nie sú dostatočná security control. Bezpečný model používa:

- oddelené runner pools,
- network segmentation,
- workload identity,
- protected refs a environments,
- ephemeral execution,
- namespace/account separation,
- concurrency a quota controls.

Nesprávny label môže viesť k nekonečnému queue alebo k spusteniu jobu na príliš privilegovanom runneri.

## 13. Checkout a source identity

Pipeline musí presne vedieť, čo runner checkoutol:

- branch tip,
- pull-request source SHA,
- synthetic merge SHA,
- merge-queue candidate,
- tag alebo detached commit,
- shallow clone depth,
- submodules,
- Git LFS objects.

Shallow clone môže chýbať merge base alebo tags potrebné pre versioning. Submodule alebo LFS fetch môže používať samostatné credentials a failure semantics.

Testovanie source branch namiesto merge resultu môže dať zelený výsledok pre stav, ktorý sa nikdy neintegruje.

## 14. Workspace lifecycle

Workspace môže byť:

- nový pre každý job,
- znovu použitý na persistent runneri,
- volume mount medzi steps,
- cacheovaný alebo snapshotovaný.

Bezpečný lifecycle:

```text
create clean workspace
→ checkout presného source
→ execute
→ upload explicit outputs
→ revoke credentials
→ remove workspace a temporary state
```

Riziká zdieľaného workspace:

- stale build outputs,
- test-order alebo branch contamination,
- secrets v config files,
- malicious symlinks,
- nesprávne permissions,
- nereprodukovateľný incremental build.

## 15. Prenos dát medzi jobs

Samostatné jobs štandardne nezdieľajú filesystem ani process state. Prenos musí byť explicitný.

Mechanizmy:

- **Artifact —** immutable alebo retention-bound output určený ďalšiemu jobu alebo používateľovi.
- **Registry —** package, image alebo bundle s digestom a provenance.
- **Cache —** optimalizačný stav, ktorý nesmie byť source of truth.
- **Report —** štruktúrovaný výstup interpretovaný CI platformou.
- **External state service —** databáza, object storage alebo environment s vlastným lifecycle.

Downstream job musí overiť artifact identity a integritu. Názov súboru alebo mutable tag nestačí.

## 16. Reports verzus artifacts

Report má machine-readable semantics pre platformu:

- JUnit test report,
- coverage report,
- SAST/SCA findings,
- dependency scan,
- deployment record,
- performance result.

Artifact je uložený súbor alebo bundle:

- binary,
- container/image reference,
- logs,
- screenshots,
- rendered manifests,
- debug dump.

Jeden output môže byť oboje. Platforma však môže report agregovať do verdictu, zatiaľ čo artifact iba uchová na diagnostiku.

Chýbajúci report po úspešnom command exit code môže znamenať incomplete evidence.

## 17. Service containers a test dependencies

Job môže spustiť databázu, broker alebo cache ako service:

```yaml
services:
  - postgres:17@sha256:...
  - redis:8@sha256:...
```

Lifecycle musí riešiť:

- version pinning,
- network identity a ports,
- functional readiness,
- deterministic seed a migrations,
- credentials,
- logs a metrics,
- resource limits,
- cleanup.

Process start nie je readiness. Fixed sleep je slabý synchronization mechanizmus; používaj condition-based probe s deadline a diagnostikou.

## 18. Permissions a secret scope

Každý job má dostať minimálne práva potrebné pre svoj účel.

Príklad trust separation:

```text
verify job
- read source
- no production secrets

build job
- read source/dependencies
- write artifact registry path

security verification
- read artifact
- write report
- no deployment access

deploy job
- read verified artifact
- scoped target-environment identity
```

Jedna job kombinujúca untrusted build, signing a production deploy má príliš veľký blast radius.

Preferuj short-lived workload identity pred dlhodobými static credentials.

## 19. Job status a pipeline verdict

Job môže skončiť ako:

- success,
- failed,
- canceled,
- timed out,
- skipped,
- waiting/manual,
- allowed/advisory failure,
- infrastructure failure,
- incomplete.

Pipeline musí definovať, ako sa každý stav propaguje downstream.

Príklady:

- failed required test blokuje package;
- canceled superseded build nemá byť product failure;
- allowed security finding zostáva viditeľný, ale neblokuje;
- cleanup sa spustí aj po cancel alebo failure;
- incomplete shard blokuje aggregate verdict;
- manual approval môže expirovať.

`allow_failure` bez ownera, expiry a reporting-u mení gate na dekoráciu.

## 20. Timeouts

Timeout patrí na viac vrstiev:

- command alebo step timeout,
- service readiness timeout,
- job timeout,
- pipeline timeout,
- deployment rollout timeout,
- approval expiry,
- artifact upload timeout.

Timeout musí byť spojený s:

- ukončením child processes,
- uploadom dostupných logs a reports,
- cleanupom temporary resources,
- uvoľnením locku,
- správnou failure klasifikáciou.

Samotné zabitie procesu bez evidence vytvára ťažko diagnostikovateľný failure.

## 21. Retry a attempts

Retry je vhodný iba pre identifikovanú transient failure class:

- runner provisioning timeout,
- krátky registry transport failure,
- dočasná network chyba,
- API throttling s definovaným backoffom.

Retry nie je vhodný na:

- compile error,
- invalid config,
- authentication/authorization failure,
- deterministic test failure,
- neznámu flaky chybu bez evidencie.

Sleduj first-attempt aj final result. Každý attempt musí mať vlastné logs a identitu. Retry mutation jobu vyžaduje idempotency alebo reconciliation.

## 22. Cancellation a superseded runs

Nový commit môže znížiť hodnotu starého runu. Platforma môže cancelovať superseded pipelines, aby šetrila capacity a skracovala queue.

Cancellation je bezpečná pri read-only verification. Pri mutation jobs musí riešiť:

- partial deployment,
- environment lock,
- cloud resource provisioning,
- traffic experiment,
- schema migration,
- signing alebo publication.

Cancel signal má spustiť cleanup alebo nechať kritickú atomic operation bezpečne dokončiť. Nekontrolované killnutie deploymentu môže byť horšie než jeho dokončenie.

## 23. Concurrency a environment locks

Niektoré jobs sa môžu paralelizovať; iné musia byť serializované.

Použitie locks/concurrency groups:

- jeden deployment do environmentu naraz,
- jedna schema migration,
- jeden release publication job pre verziu,
- obmedzený počet jobs proti shared sandboxu,
- replacement starého deployment runu novším.

Lock musí mať:

- owner/job identity,
- timeout alebo lease,
- cleanup pri cancel/failure,
- ochranu pred stale lockom,
- jasnú queue policy.

## 24. Matrix, sharding a fan-in

Matrix vytvára viac job variants, napríklad:

```text
OS: linux, windows
runtime: 3.11, 3.12
architecture: amd64, arm64
```

Sharding rozdeľuje veľkú test suite na paralelné časti.

Agregácia musí overiť:

- očakávaný počet shards,
- unique shard identity,
- report completeness,
- duplicate alebo missing results,
- rovnaký source/artifact,
- failure jednotlivého variantu.

Zelené existujúce shardy nesmú zakryť shard, ktorý sa nikdy nespustil alebo neuploadol report.

## 25. Cleanup a always-run jobs

Cleanup musí fungovať po success, failure, timeout aj cancellation.

Úlohy:

- odstrániť ephemeral environment,
- revoke credentials,
- uvoľniť lock a quota,
- zastaviť service containers,
- uploadnúť logs a reports,
- ukončiť traffic experiment,
- odstrániť temporary secrets a workspace.

Cleanup má byť idempotentný a tolerantný k partial state. Cleanup failure musí byť viditeľný, pretože môže ovplyvniť ďalšie runs, bezpečnosť alebo náklady.

## 26. Capacity a resource model

Runner pool potrebuje CPU, memory, disk, network a niekedy GPU alebo licensed tools.

Sleduj:

- queue time podľa label/pool,
- startup a provisioning time,
- runner utilization,
- CPU throttling a OOM,
- disk pressure,
- artifact/cache transfer,
- noisy-neighbor behavior,
- autoscaler lag,
- organization alebo provider quotas.

Príliš nízke limits vytvárajú flaky performance. Chýbajúce limits umožnia jednému jobu poškodiť celý pool.

## 27. Pipeline observability

Pipeline je produkčný systém pre delivery.

Minimálne metrics:

- pipeline a job success podľa failure class,
- queue time a p95 duration,
- critical-path duration,
- first-attempt success,
- retry a flaky rate,
- cancellation/superseded rate,
- runner utilization a provisioning errors,
- cache/artifact upload failures,
- incomplete report rate,
- cleanup failure rate,
- environment lock wait time.

Logs a traces majú prepájať pipeline, job, attempt, runner a artifact identity.

## 28. Diagnostický postup

### Job čaká v queue

Over:

- required labels a capabilities,
- dostupnosť runner poolu,
- protected-runner policy,
- concurrency limit a environment lock,
- autoscaler a provisioning errors,
- organization quotas.

### Job funguje lokálne, nie v CI

Porovnaj:

- runtime image a architecture,
- environment variables a secrets,
- working directory a filesystem case sensitivity,
- network/DNS/proxy access,
- timezone a locale,
- dependency/tool versions,
- resource limits,
- checkout depth a source SHA.

### Downstream job nevidí output

Over:

- artifact declaration a upload status,
- retention a permissions,
- dependency edge,
- digest a download path,
- či output nebol iba v workspace predchádzajúceho jobu.

### Pipeline je pomalá

Zmeraj:

- queue verzus execution čas,
- critical path,
- stage barriers,
- shard imbalance,
- artifact transfer,
- service startup,
- runner contention.

## 29. Typické anti-patterny

### Pipeline a YAML sú to isté

YAML je definícia; runtime pipeline má konkrétne inputs, permissions, jobs a evidence.

### Stage a job sú to isté

Stage je logická/barrier vrstva; job je samostatne schedulovaná execution unit.

### Runner je iba server

Je zároveň trust, isolation a capacity boundary.

### Steps ako security isolation

Steps jedného jobu typicky zdieľajú credentials a workspace.

### Workspace medzi jobs je automaticky spoločný

Prenos musí byť explicitný cez artifact, registry alebo external state.

### Viac paralelizácie vždy zrýchli pipeline

Môže zvýšiť queueing, contention, quotas a fan-in overhead.

### Retry každého failure

Maskuje deterministic chyby a mutation partial state.

### Allowed failure ako vyriešený problém

Mení verdict policy, nie root cause alebo ownership.

### Persistent privileged runner pre všetky projekty

Zvyšuje cross-project a credential blast radius.

## 30. Praktický rozhodovací rámec

1. Čo je pipeline template a čo runtime instance?
2. Ktoré dependencies vyžadujú stage barrier a ktoré iba DAG edge?
3. Aký je critical path?
4. Čo patrí do jedného jobu a čo potrebuje samostatnú trust boundary?
5. Aký executor zodpovedá trust levelu?
6. Aké source SHA a checkout semantics job používa?
7. Ako sa outputs prenášajú a overujú medzi jobs?
8. Aké permissions a network access má každý job?
9. Ako sa klasifikujú skipped, canceled, incomplete a allowed failures?
10. Ktoré retries sú bezpečné?
11. Ako funguje cancel, cleanup a stale-lock recovery?
12. Ako sa agregujú matrix/shard výsledky?
13. Aká runner capacity a telemetry je potrebná?

## 31. Kontrolný checklist

- pipeline instance má explicitný source a workflow version;
- DAG neobsahuje zbytočné barriers ani chýbajúce edges;
- jobs deklarujú runtime, inputs, permissions a timeout;
- steps nezískavajú falošný status izolácie;
- executor zodpovedá trust a isolation požiadavke;
- untrusted jobs nepoužívajú privileged persistent runners;
- checkout používa správny candidate SHA;
- outputs sa prenášajú explicitne a s integrity kontrolou;
- cache nie je source of truth;
- services majú functional readiness;
- secret scopes sú minimálne;
- incomplete report nie je success;
- retry je viazaný na transient failure class;
- cancel a timeout spúšťajú bezpečný cleanup;
- environment mutations sú serializované;
- matrix/shards majú completeness check;
- runner pool má limity, autoscaling a observability.

## 32. Kontrolné otázky

1. Aký je rozdiel medzi workflow definíciou a pipeline instance?
2. Čo odlišuje pipeline, stage, job, step, runner a executor?
3. Kedy stage barrier zbytočne predlžuje critical path?
4. Aké informácie tvorí job execution contract?
5. Prečo steps nie sú samostatná security boundary?
6. Aké rozdiely majú shell, container, VM a Kubernetes executor?
7. Aké riziká má self-hosted persistent runner?
8. Prečo labels nestačia ako security mechanizmus?
9. Prečo musí byť checkout SHA explicitné?
10. Ako sa prenášajú dáta medzi jobs?
11. Aký je rozdiel medzi reportom, artifactom a cache?
12. Prečo process start nie je service readiness?
13. Ako sa oddeľujú build a deploy permissions?
14. Kedy je retry legitímny?
15. Prečo cancellation potrebuje mutation-aware cleanup?
16. Ako matrix alebo sharding môže vytvoriť false green?
17. Ktoré metrics odhalia runner capacity bottleneck?

## Summary

Pipeline je runtime inštancia versionovaného workflowu; stage organizuje broad phases, job je samostatná execution a trust unit, step zdieľa job context, runner job prijíma a executor určuje jeho izoláciu. Dôveryhodný pipeline model používa explicitný DAG, presný source SHA, scoped permissions, immutable artifact transfer, úplné reporty, bezpečné timeout/retry/cancel semantics a idempotentný cleanup. Runner pool je produkčný security a capacity systém a potrebuje vlastnú observability.

## Glossary impact

Relevantné pojmy: pipeline, workflow instance, stage, job, step, runner, executor, DAG, critical path, runner pool, runner label, workspace, service container, artifact, report, matrix, shard, fan-in, allowed failure, job attempt, pipeline queue time a cleanup job.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Continuous Deployment](continuous-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Trigger, artifact a cache →](trigger-artifact-cache.md)
<!-- KNOWLEDGE-NAVIGATION:END -->