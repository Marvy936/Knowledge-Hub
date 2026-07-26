# Pipeline, stage, job a runner

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

CI/CD platforma premieňa versionovanú workflow definíciu na konkrétny runtime execution graph. Pipeline, stage, job, step, runner a executor nie sú synonymá; každý pojem označuje inú vrstvu ordering-u, izolácie, trustu, capacity a evidence.

```text
trigger a workflow revision
→ pipeline instance a evaluated DAG
→ schedulované jobs
→ runner/executor contexts
→ explicitný artifact a report flow
→ fan-in verdict
→ mutation/cleanup transitions
→ retained evidence
```

Dôležitý nie je názov v konkrétnej platforme, ale runtime contract: čo sa spustí, s akými inputs a permissions, na akom runneri, v akom poradí a ako sa výsledok stane autoritatívnym verdictom.

## 1. Cieľ kapitoly

Nosný model kapitoly je pipeline-execution lifecycle:

```text
event a source identity
→ workflow parse/evaluation
→ DAG, matrix a policy expansion
→ job execution contracts
→ runner scheduling a executor isolation
→ explicitný data/evidence transfer
→ failure/cancel/retry semantics
→ complete fan-in verdict
→ mutation-aware cleanup
→ pipeline telemetry a learning
```

Pipeline YAML je iba deklarácia. Runtime pipeline má vlastnú identity, state, attempts, permissions, artifacts a environment effects.

## 2. Nosný scenár: Atlas Orders 3.10.0 pipeline

Atlas pipeline reaguje na merge-queue candidate:

```text
candidate C
→ compile workflow W
→ lint/type/static jobs
→ unit shards
→ PostgreSQL/event integration
→ build images A a B
→ contract/security verification
→ package promotion evidence E
→ deploy staging
→ smoke a operational validation
```

Pipeline používa:

- untrusted verification pool pre pull requests;
- trusted ephemeral build pool;
- protected staging deployment pool;
- PostgreSQL a broker service dependencies;
- explicitné image digests a reports;
- environment lock pre staging;
- cleanup aj pri cancellation.

Každá chyba v DAG edge, runner policy alebo artifact flow môže vytvoriť false green aj pri správnych testoch.

## 3. Pojmy ako vrstvy runtime modelu

- **Workflow definition** — versionovaný template alebo program vytvárajúci execution graph.
- **Pipeline instance** — konkrétny run viazaný na event, candidate, workflow revision a inputs.
- **Stage** — široká logická fáza alebo barrier medzi skupinami jobs.
- **Job** — samostatne plánovaná execution, trust a failure unit.
- **Step** — sekvenčná operácia zdieľajúca job context.
- **Runner** — agent alebo worker prijímajúci job assignment.
- **Executor** — mechanizmus izolácie a spustenia, napríklad shell, container, VM alebo Kubernetes pod.

```text
pipeline
└─ evaluated DAG
   ├─ job on runner/executor
   │  └─ sequential steps
   ├─ parallel jobs
   └─ fan-in/decision jobs
```

## 4. Pipeline instance a provenance

Atlas pipeline identity zahŕňa:

- trigger event a payload;
- source, target a synthetic candidate SHA;
- workflow/template revision;
- actor alebo workload identity;
- inputs, variables a policy decisions;
- evaluated DAG a matrix variants;
- runner images a executor types;
- jobs, attempts a timestamps;
- artifacts, reports a deployment records.

Dva runs rovnakého YAML môžu mať iný outcome kvôli runner image, cache, secret version, external dependency alebo event payloadu. Pipeline provenance preto obsahuje runtime inputs, nie iba repository commit.

## 5. Parse, evaluate a compile fáza

Pred spustením jobs platforma:

```text
načíta workflow definition
→ overí syntax a schema
→ vyhodnotí conditions a dynamic includes
→ expanduje matrix
→ zostaví DAG
→ určí environments a permissions
→ vytvorí schedulovateľné jobs
```

Chyba v tejto fáze je pipeline failure, hoci sa nespustil žiadny runner. Dynamická condition môže tiež nečakane vynechať required control; preto expected-control manifest a policy nepatria iba do finálneho jobu.

## 6. Stage a DAG

Stage poskytuje čitateľnú broad phase:

```text
verify → package → deploy
```

Hrubý barrier však môže blokovať nezávislú prácu. Presný DAG vyjadruje skutočné dependencies:

```text
lint ───────────────┐
                     ├─> build A/B ──> artifact verify ──> deploy staging
unit shards ────────┘          ▲
                               │
contract/integration ──────────┘
```

DAG edge znamená viac než ordering. Môže niesť:

- required predecessor verdict;
- artifact/report dependency;
- permission alebo environment boundary;
- failure propagation;
- cleanup a lock lifecycle.

Chýbajúci edge vytvára race. Zbytočný edge predlžuje critical path.

## 7. Critical path

Critical path je najdlhšia dependency cesta od triggeru po required verdict alebo deployment.

```text
queue 2m + integration 9m + build 5m + verify 3m = 19m
lint 1m + unit 4m                            = 5m
```

Skrátenie lint jobu o 30 sekúnd nezmení 19-minútový verdict. Atlas sleduje:

- runner queue a startup;
- stage barriers;
- shard imbalance;
- service readiness;
- artifact transfer;
- fan-in čakanie;
- environment locks.

Viac paralelizácie môže zvýšiť contention, quotas a transfer overhead.

## 8. Job ako execution contract

Job explicitne deklaruje:

```text
source/candidate identity
+ runtime image, OS a architecture
+ commands/steps
+ inputs a predecessor artifacts
+ permissions a network scope
+ variables a secret references
+ CPU/memory/disk limits
+ timeout, retry a cancellation policy
+ reports/artifacts
+ success a cleanup semantics
```

Atlas `integration-postgres` job napríklad používa pinovaný image, reálny PostgreSQL service, read-only source token, žiadne deployment credentials, JUnit report a 15-minútový timeout.

Job je správna boundary, keď je potrebná samostatná izolácia, permission scope, runtime, retry, timeout alebo parallel scheduling.

## 9. Steps zdieľajú job context

Steps typicky zdieľajú:

- workspace a filesystem;
- environment variables;
- job credentials;
- process/container/VM context;
- network namespace;
- working directory.

Preto step nie je samostatná security boundary. Ak Atlas build step dostane registry write token, ďalší step v rovnakom jobe ho môže potenciálne použiť.

Steps sú vhodné pre sekvenčné `setup → execute → report → cleanup` v jednom trust contexte. Rozdielne permissions alebo isolation vyžadujú samostatný job.

## 10. Runner a control plane

Control plane vytvára jobs a prideľuje ich compatible runnerom. Runner:

```text
získa assignment/lease
→ pripraví executor
→ načíta source a explicitné inputs
→ získa scoped credentials
→ spustí steps
→ streamuje logs/status
→ uploadne artifacts a reports
→ vykoná cleanup
→ odošle final job verdict
```

Runner je security a capacity boundary. Môže mať source, registry, cloud API alebo internal-network access.

## 11. Executor choice

### Shell executor

- nízky startup overhead;
- priamy host access;
- slabá izolácia a vysoké persistence riziko.

### Container executor

- reprodukovateľnejší userspace;
- oddelený filesystem/process namespace;
- zdieľaný kernel a riziko privileged mounts/socketov.

### VM executor

- silnejšia izolácia;
- vhodný pre untrusted code alebo citlivý build;
- vyšší startup a infra cost.

### Kubernetes executor

- elastické scheduling a resource controls;
- integrácia s namespace, service account a network policy;
- závislosť od cluster control plane a správnej pod-security konfigurácie.

Executor sa volí podľa trustu, workloadu a failure blast radiusu, nie iba ceny.

## 12. Runner pools a scheduling policy

Atlas oddeľuje pools:

```text
pr-untrusted
trusted-build
private-integration
protected-staging-deploy
```

Job capability labels ako `linux`, `arm64` alebo `private-network` pomáhajú scheduling-u, ale samy nie sú security control. Bezpečnosť vytvárajú oddelené pools, protected refs/environments, workload identity, network segmentation a ephemeral execution.

Nesprávny label môže spôsobiť nekonečnú queue alebo spustiť job na príliš privilegovanom runneri.

## 13. Source checkout identity

Job musí vedieť, čo presne checkoutol:

- source branch SHA;
- synthetic merge alebo merge-queue candidate;
- shallow/full history;
- submodules a LFS objects;
- tags a merge base podľa potreby.

Shallow clone môže rozbiť diff coverage, semantic versioning alebo merge-base selection. Test source branchu namiesto candidate tree môže vytvoriť green pre stav, ktorý sa nikdy neintegruje.

## 14. Workspace lifecycle

Bezpečný workspace:

```text
create clean
→ checkout exact candidate
→ execute
→ upload explicit outputs
→ revoke credentials
→ remove workspace a temporary state
```

Persistent workspace môže zachovať stale outputs, secrets, malicious symlinks alebo branch contamination. Downstream job sa nesmie spoliehať na implicitný filesystem predchádzajúceho jobu.

## 15. Explicitný prenos dát

Medzi jobs sa prenáša iba deklarovaný stav:

- **artifact** — retention-bound file alebo bundle;
- **registry object** — package/image s digestom a provenance;
- **report** — machine-readable evidence pre platform verdict;
- **cache** — non-authoritative optimization;
- **external state** — environment alebo service s vlastným lifecycle.

Downstream job overí identity a integrity. Mutable tag alebo rovnaký filename nestačí.

Report môže ovplyvniť verdict; artifact môže byť iba diagnostický. Command exit 0 bez required reportu môže znamenať incomplete evidence.

## 16. Service dependencies a readiness

Atlas integration job spúšťa PostgreSQL a broker service. Contract obsahuje:

- pinované versions;
- network identity a ports;
- credentials;
- migrations a deterministic seed;
- resource limits;
- logs a metrics;
- functional readiness probe;
- cleanup.

Process start nie je readiness. Fixed sleep môže byť zbytočne dlhý alebo príliš krátky. Condition-based probe čaká na schopnosť vykonať relevantnú operáciu a pri timeout-e zachová posledný observed state.

## 17. Permission flow

Atlas rozdeľuje:

```text
verify job
→ read source, no sensitive secrets

build job
→ read dependencies, write candidate registry namespace

verification/signing job
→ read immutable digest, write attestation

deploy job
→ read verified artifact, scoped staging identity
```

Jeden job kombinujúci untrusted source execution, signing a production deployment má neprijateľný blast radius. Preferované sú short-lived workload identities pred statickými credentials.

## 18. Job status a verdict propagation

Job states môžu byť:

- success;
- failed;
- canceled alebo superseded;
- timed out;
- skipped by evaluated policy;
- waiting/manual;
- advisory/allowed failure;
- infrastructure/tool failure;
- incomplete.

DAG musí definovať propagáciu:

```text
required test failed → package blocked
missing shard/report → aggregate incomplete
superseded verification → canceled, nie product failure
cleanup → runs after success/failure/cancel
advisory finding → visible, ale neblokuje podľa policy
```

`allow_failure` bez ownera, expiry a reporting-u mení control na dekoráciu.

## 19. Timeout, retry a cancellation

Timeout existuje na command, readiness, job, pipeline, deployment, approval a upload vrstve. Má spustiť:

- ukončenie child processes;
- upload dostupných logs/reports;
- credential revoke;
- lock/resource cleanup;
- správnu failure klasifikáciu.

Retry je povolený iba pre identifikovanú transient class a zachová attempts. Mutation job potrebuje idempotency alebo reconciliation.

Cancellation je bezpečná pri read-only verification. Pri migrácii, deploymente, signing alebo publication musí riešiť partial state a kritickú atomic operáciu.

## 20. Concurrency a locks

Atlas serializuje:

- deployment do rovnakého environmentu;
- schema migration;
- publication rovnakej release version;
- shared performance environment.

Lock má identity ownera, lease/timeout, stale-lock recovery a cleanup pri cancel/failure. Nekontrolovaný stale lock môže zastaviť celý delivery flow; chýbajúci lock môže vytvoriť súbežné mutations.

## 21. Matrix, sharding a fan-in

Atlas unit tests bežia v ôsmich shardoch. Aggregate job pozná expected manifest:

```text
candidate C
expected shards 0..7
→ received reports
→ verify unique identities a same source/tool config
→ fail/incomplete pri missing alebo duplicate shard
→ aggregate verdict
```

Zelených sedem existujúcich shardov nesmie zakryť ôsmy, ktorý sa nikdy nenaplánoval alebo neuploadol report.

Matrix navyše overuje OS/runtime/architecture variants; každý variant je samostatný job verdict.

## 22. Cleanup ako required transition

Cleanup prebieha po success, failure, timeout aj cancellation:

- odstráni ephemeral environment;
- revoke-ne credentials;
- uvoľní environment lock;
- zastaví services;
- uploadne evidence;
- odstráni temporary secrets/workspace;
- ukončí traffic experiment.

Cleanup je idempotentný a partial-state aware. Jeho failure je samostatný viditeľný outcome, pretože môže ovplyvniť ďalšie runs, security aj cost.

## 23. Worked failure: chýbajúci DAG edge nasadil stale artifact

Atlas `deploy-staging` job deklaroval dependency iba na `unit-tests`, nie na `build-images` a `artifact-verify`:

```text
unit tests green
→ deploy job sa spustil skôr
→ mutable staging tag stále ukazoval na digest z predchádzajúceho runu
→ smoke testoval starý artifact
→ current pipeline dostala green staging verdict
→ nový digest nikdy nebol nasadený ani validovaný
```

### Root cause

Stage názvy vytvárali vizuálny dojem poradia, ale runtime DAG nemal required artifact edge ani digest handoff. Mutable tag maskoval nesprávny input.

### Náprava

- explicitný `needs` chain build → verify → deploy;
- deploy input je digest artifact, nie tag;
- deployment record overí candidate/digest;
- fan-in blokuje pri missing predecessor evidence;
- DAG contract test kontroluje required edges.

## 24. Worked failure: untrusted PR získal privileged runner

Self-hosted runner mal labels `linux`, `docker`, `private-network`, `deploy`. PR job požadoval iba `linux` a scheduler ho pridelil tomuto hostu:

```text
untrusted PR script
→ persistent privileged runner
→ mounted Docker socket a cached registry credentials
→ attacker vytvoril host container
→ prečítal token z predchádzajúceho deploy jobu
```

### Root cause

Labels sa považovali za security boundary. Verification a deploy workload zdieľali persistent host, workspace, network a credential residue.

### Náprava

- fyzicky/logicky oddelené pools;
- untrusted PRs iba na ephemeral sandboxed executors;
- protected runner policy a no-secrets default;
- short-lived scoped identity;
- zákaz privileged socketov a host mounts;
- cleanup/credential revocation a runner attestation;
- audit scheduling decisions.

## 25. Pipeline observability

Atlas sleduje:

- pipeline/job verdict podľa failure class;
- queue time podľa runner poolu;
- critical-path duration;
- first-attempt a retry rate;
- canceled/superseded execution;
- runner provisioning/OOM/throttling;
- missing report a artifact-transfer rate;
- environment lock wait;
- cleanup failures;
- source/candidate/artifact identity v logs a traces.

Pipeline je produkčný systém pre delivery a potrebuje ownera, capacity plán a incident response.

## 26. Diagnostický postup

Pri pipeline failure:

1. Potvrď event, source/target/candidate a workflow revision.
2. Skontroluj parse/evaluation result, matrix a created DAG.
3. Nájdite required predecessor a artifact/report edges.
4. Over runner pool, labels, trust policy, queue a executor.
5. Porovnaj runtime image, architecture, resources, network a credentials.
6. Potvrď checkout depth, submodules, LFS a source SHA.
7. Skontroluj workspace cleanliness a cache assumptions.
8. Over service readiness, logs a resource limits.
9. Klasifikuj failure, timeout, cancel, retry a incomplete semantics.
10. Potvrď expected shard/matrix manifest a fan-in.
11. Over cleanup, locks a partial mutation state.
12. Oprav runtime contract alebo DAG a potvrď first-attempt nový run.

## 27. Referenčné pravidlá

- Workflow definition nie je runtime pipeline instance.
- Stage je broad barrier; DAG vyjadruje presné dependencies.
- Job je execution, trust, permission a failure boundary.
- Steps jedného jobu zdieľajú context a credentials.
- Runner je security aj capacity boundary; executor určuje izoláciu.
- Labels samy nestačia na security separation.
- Checkout identity musí byť explicitná.
- Prenos medzi jobs je explicitný a integrity-checked.
- Cache nie je authoritative output.
- Process start nie je functional readiness.
- Missing report alebo shard je incomplete, nie pass.
- Retry a cancel rešpektujú mutation state.
- Locks majú lease a cleanup.
- Cleanup je required, auditovaný outcome.

## 28. Časté omyly

### „Pipeline a YAML sú to isté“

YAML je template; runtime run má konkrétne inputs, graph, permissions a state.

### „Stage garantuje správny artifact flow“

Bez explicitného DAG edge môže downstream job začať s nesprávnym alebo chýbajúcim outputom.

### „Steps sú izolované“

Typicky zdieľajú workspace, network a job credentials.

### „Runner je iba server“

Je trust, isolation, scheduling a capacity boundary.

### „Zelené shardy znamenajú complete suite“

Treba poznať expected manifest a zachytiť shard, ktorý nevznikol.

### „Cancel je bezpečný kill“

Mutation môže zostať partial a vyžadovať reconciliation alebo cleanup.

## 29. Zhrnutie

Dôveryhodný Atlas pipeline runtime je:

```text
versioned workflow + trigger
→ evaluated DAG a explicitné identities
→ isolated jobs na správnych runner pools
→ scoped permissions a deterministic inputs
→ immutable artifact/report flow
→ complete fan-in verdict
→ mutation-aware retry/cancel
→ idempotent cleanup
→ telemetry a runtime learning
```

Pipeline model prepája CI/CD logiku s reálnym execution a trust systémom. Správna syntax bez správnych dependencies, runner boundaries a evidence aggregation môže stále vytvoriť false green alebo security incident.

## 30. Kontrolné otázky

1. Aký je rozdiel medzi workflow definition a pipeline instance?
2. Ako sa líšia stage, job, step, runner a executor?
3. Prečo DAG edge vyjadruje viac než ordering?
4. Ako critical path ovplyvňujú queue, readiness a artifact transfer?
5. Čo tvorí job execution contract?
6. Prečo steps nie sú security boundary?
7. Ako sa volí executor podľa trust levelu?
8. Prečo runner labels nestačia na izoláciu?
9. Ako sa prenášajú artifacts a reports medzi jobs?
10. Prečo process start nie je readiness?
11. Ako expected shard manifest zabraňuje false green?
12. Ako chýbajúci DAG edge nasadil stale Atlas artifact?
13. Ako untrusted PR získal privileged runner?
14. Prečo cleanup patrí do pipeline verdictu?

## Glossary impact

Relevantné pojmy: workflow definition, pipeline instance, pipeline, stage, DAG, critical path, job, step, runner, executor, runner pool, execution contract, workspace lifecycle, service container, report, artifact transfer, matrix, shard, fan-in, environment lock, job attempt, incomplete verdict a cleanup transition.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Continuous Deployment](continuous-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Trigger, artifact a cache →](trigger-artifact-cache.md)
<!-- KNOWLEDGE-NAVIGATION:END -->