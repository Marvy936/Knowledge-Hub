# MLOps flagship runtime evidence

> **Evidence status: Runtime verified for the bounded Practical v1 local profile**

Tento dokument je authoritative runtime-evidence contract pre celý Practical v1 MLOps lifecycle. Required vrstvy boli vykonané v canonical combined release baseline na `789b5038b81b9342b1aef57b809bd3b67202ebde` (release-evidence run `31542501346`) vrátane local MLflow/Registry provider read-backu, containerized inference, canary/rollback, drift/retraining, post-retraining handoff a cleanupu. Stav je bounded na deklarovaný local/hosted v1 profile a neznamená production platform readiness.

## Evidence layers

MLOps runtime sa nesmie zredukovať na jediný zelený pytest job. Required proof je rozdelený na navzájom odlišné layers:

```text
training + promotion identity
→ Tracking/Registry + artifact read-back
→ immutable serving subject
→ live inference + canary/rollback
→ monitoring + drift decision
→ exact human approval
→ controlled retraining + new Registry version
→ post-retraining deployment/canary handoff
→ cleanup/read-back
```

Úspech jednej vrstvy automaticky nepreukazuje ďalšiu.

## Authoritative execution subject

Každý runtime record musí pinovať:

- exact Git SHA,
- Python version,
- resolved package versions,
- runner/environment identity,
- workflow/run alebo equivalent execution ID,
- exact input artifact identities,
- exact output identities,
- cleanup/read-back result,
- explicit proof boundary.

Repository obsahuje MLOps-specific workflows aj spoločný release lifecycle. GitHub Actions blocker #151 je uzavretý; canonical runtime evidence je viazaná na executed baseline `789b5038b81b9342b1aef57b809bd3b67202ebde` a ďalší final tag subject musí znovu prejsť exact-head release gate-om.

## 1. Training lineage and promotion foundation

Required chain:

```text
Machine Learning training manifest
→ exact dataset/model identities
→ evaluation bundle
→ accepted candidate
→ compare-before-promote
→ immutable release manifest
→ alias-state mutation
→ stale second promotion refusal
```

Evidence musí preukázať:

- dataset SHA-256 a exact source/training subject,
- packaged model SHA-256,
- candidate ID nezávislý od workspace pathu,
- evaluation odvodenú z exact ML training manifestu,
- accepted status a canonical candidate ID,
- release ID a exact model identity,
- alias-state before/after read-back,
- refusal stale `expected-current` promotionu,
- neprítomnosť neautorizovaného `stale-release.json` alebo podobného partial artifactu.

Forbidden matrix musí odmietnuť tampered candidate, neakceptovanú evaluation, mismatched training lineage, workspace-dependent identity a invalid alias-state schema.

## 2. Tracking, Registry and artifact read-back

Registry gate musí vykonať skutočný database-backed provider lifecycle:

```text
trusted deterministic model artifact
→ candidate digest verification pred deserializáciou
→ loopback MLflow Tracking Server
→ SQLite metadata backend
→ oddelený artifact destination
→ run params/metrics/tags
→ logged model
→ registered model version
→ model-version tags
→ alias mutation
→ API read-back
→ artifact download cez tracking server
→ SHA-256 parity
→ exact models:/<name>/<version> load
→ prediction parity
→ server restart
→ repeated exact-version read-back/load
```

Required evidence:

- Python a MLflow version,
- backend/store locations v disposable runtime,
- experiment ID, run ID a logged model ID,
- registered model name a exact numeric version,
- immutable Registry URI `models:/<name>/<version>`,
- alias a resolved version pri danom rune,
- candidate/source/model identity tags prečítané späť z runu aj model version,
- original/downloaded model SHA-256,
- source/Registry prediction parity,
- evidence ID,
- SQLite/artifact existence pred cleanupom,
- repeated verification po MLflow server reštarte.

Mutable alias URI nie je deployment identity. Runtime deployment subject musí pinovať exact numeric version a model digest.

## 3. Immutable serving subject and container evidence

Source-level Dockerfile/FastAPI contract nie je container runtime evidence. Serving gate musí preukázať:

```text
exact promoted model version
+ exact model digest
+ exact source revision
→ image build
→ immutable image identity/digest
→ non-root container
→ exact model artifact mount/read-back
→ live inference request
→ response identity validation
```

Required evidence:

- image build subject a immutable digest/ID,
- non-root UID/read-back,
- exact deployed release/model/image IDs,
- mounted model artifact SHA-256 alebo equivalent byte identity,
- service liveness/readiness distinction,
- strict request-schema refusal,
- at least one real HTTP inference request,
- response viazanú na deployment/release/model/image subject,
- container stop/remove cleanup.

Samotný Dockerfile source test ani loopback Uvicorn process mimo image nestačí na uzavretie containerized-serving gate-u.

## 4. Canary and rollback evidence

Canary gate musí preukázať dve samostatné generations a deterministic traffic routing:

```text
stable generation A
+ candidate generation B
→ exact routing policy
→ live HTTP request set
→ per-generation evidence
→ no_data | insufficient_evidence | healthy/failed decision
→ promotion alebo exact rollback
→ control-plane read-back
```

Required evidence:

- deployment IDs oboch generations,
- routing generation/policy ID,
- deterministic request-to-generation mapping,
- HTTP request/response evidence pre oba subjects,
- metrics/counts viazané na exact generations,
- explicitný `no_data` a `insufficient_evidence` behavior,
- rollback decision viazaný na exact failed candidate/deployment subject,
- post-rollback stable-state read-back.

Canary success nesmie byť odvodený iba z toho, že oba procesy odpovedajú `200`.

## 5. Monitoring and drift evidence

Monitoring gate používa aggregate telemetry bez potreby raw request retention.

Required evidence:

- exact baseline subject,
- exact monitoring-window subject,
- numeric PSI,
- categorical TVD,
- prediction-rate delta,
- latency a error evidence,
- explicit states `stable`, `no_data`, `insufficient_evidence`, `operational_failure`, `drift_detected`,
- deterministic control a shifted drift injection,
- canonical drift-report identity.

No-data alebo operational-failure stav sa nesmie reinterpretovať ako „model je zdravý“.

## 6. Approval-gated controlled retraining

Drift report sám o sebe nesmie spustiť mutation authority. Required chain:

```text
validated drift report
→ canonical retraining proposal
→ exact proposal ID
→ separate human approval
→ approval/proposal read-back
→ operation ID
→ read-before-retry
→ training execution
→ new candidate
→ Registry write
→ exact new model version
→ compare-before-promote
→ alias/promotion read-back
```

Required evidence:

- before Registry version,
- drift/report/proposal IDs,
- exact approval subject a validity,
- operation/checkpoint IDs,
- no duplicate side effect pri replay/recovery,
- new candidate/model digest,
- after Registry version odlišnú od before version,
- exact new immutable Registry URI,
- promotion decision/read-back,
- refusal tampered proposal/report/stale approval,
- unknown-outcome handling pri nejednoznačnom Registry/provider result-e.

Zelené isolated executor unit tests nie sú live provider retraining evidence; provider lifecycle musí reálne vytvoriť a prečítať novú Registry version.

## 7. Post-retraining deployment handoff

Finálny MLOps Practical v1 chain musí spojiť retraining output s deployment subjectom, nie iba dokázať vrstvy oddelene.

Required identity chain:

```text
completed retraining operation
→ promoted new Registry version
→ exact live-tested image identity
→ immutable deployment subject
→ canary subject
→ rollback/promote decision subject
```

Evidence musí potvrdiť, že:

- deployment používa práve novú promoted Registry version,
- deployment image identity je exact image použitá v serving runtime gate-e alebo immutable equivalent,
- canary referencuje exact deployment ID,
- rollback/promote rozhodnutie referencuje exact canary/deployment subject,
- žiadny mutable alias sa nere-resolví ako runtime deployment identity.

## Required failure and recovery evidence

MLOps runtime musí fail-closed pokryť minimálne:

- tampered source/model/candidate bytes,
- wrong training lineage,
- alias/version mismatch,
- artifact checksum mismatch,
- wrong model source run/tags,
- prediction parity failure,
- stale deployment/canary subject,
- missing telemetry/no-data,
- operational monitoring failure,
- tampered drift report/proposal,
- missing/stale approval,
- provider unknown outcome,
- recovery/replay bez duplicate Registry/promotion side effectu,
- stale compare-before-promote subject.

## Cleanup evidence

Cleanup sa musí vykonať aj po failure branchi a musí odstrániť/read-backnúť non-existence podľa použitého gate-u:

- MLflow process/server,
- SQLite database,
- artifact destination/downloads,
- generated dataset/model/candidate/release files,
- monitoring/drift/retraining runtime,
- serving containers/images, ak boli vytvorené ako disposable test artifacts,
- canary runtime processes/state,
- virtual environment alebo runner-temp dependency surface, ak je súčasťou contractu,
- všetok disposable `.runtime` state.

Tracked worktree nesmie byť po cleanup-e zmenený a nový runtime artifact nesmie zostať v repository checkout-e.

## Evidence record

Finálny MLOps closeout môže byť jeden chained run alebo viac immutable runov, ak sú ich identities explicitne prepojené. Súhrnný record musí uviesť:

- exact Git SHA(s),
- workflow/run/job IDs,
- resolved dependency/provider versions,
- training/candidate/release identities,
- Registry run/model/version/artifact identities,
- serving image/deployment identities,
- canary/rollback subjects,
- monitoring/drift/proposal/approval identities,
- retraining operation a before/after Registry versions,
- post-retraining deployment chain,
- cleanup read-back,
- explicit proof boundary.

## Proof boundary

Úspešný Practical v1 MLOps evidence set preukáže bounded local/hosted lifecycle od exact ML artifactu cez Registry, immutable serving, canary/rollback, drift a approval-gated retraining až po deployment handoff pre novú model version.

Nepreukáže automaticky:

- production Kubernetes/cloud ingress alebo autoscaling,
- remote object-store durability,
- multi-user MLflow auth/authorization,
- HA/backup/restore/disaster recovery,
- production business KPI impact,
- production readiness.

Required bounded-local evidence records existujú; production/cloud proof boundaries uvedené vyššie zostávajú mimo Practical v1 claimu.
