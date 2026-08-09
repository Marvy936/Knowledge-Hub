# Live controlled retraining runtime gate

Tento gate vykonáva existujúci approval-bound controlled-retraining executor proti reálnemu lokálnemu MLflow Tracking/Registry providerovi. Nevytvára druhý retraining algoritmus a neobchádza proposal/approval contracts.

Authoritative source:

```text
labs/mlops/scripts/run_registry_gate.sh
→ labs/mlops/scripts/run_live_retraining_runtime.py
→ labs/mlops/scripts/run_monitoring_drift.py
→ labs/mlops/scripts/approve_retraining.py
→ labs/mlops/scripts/run_controlled_retraining.py
```

Dedicated workflow:

```text
.github/workflows/mlops-live-retraining-runtime.yml
```

## Lifecycle

Baseline najprv vytvorí existujúci Registry gate:

```text
exact Git subject
→ deterministic ML training
→ accepted candidate
→ SQLite-backed MLflow Tracking/Registry
→ registered model version 1
→ champion alias → version 1
→ artifact checksum/read-back
→ provider stop
```

Live retraining driver potom preberie exact baseline candidate, Registry evidence, database a artifact store.

### Monitoring a drift

Gate vytvorí 200 deterministic synthetic monitoring records, z nich baseline profile a druhú window po `inject_drift(mode="shift")`.

Používa rovnaké thresholdy ako runtime driver:

```text
minimum successful events = 100
numeric PSI              = 0.20
categorical TVD          = 0.15
prediction-rate delta    = 0.10
maximum error rate       = 0.05
```

Source test pinne, že tento exact corpus a threshold generation vedú na:

```text
drift_detected
→ approval_required
```

Monitoring events sú syntetické evidence inputs. Gate ich neprezentuje ako production telemetry.

### Approval boundary

Driver najprv zavolá approval CLI s nesprávnym `expected_proposal_id`.

Očakávanie:

```text
exit 2
→ status=refused
→ žiadny approval artifact
```

Až potom vytvorí samostatný exact approval viazaný na:

- `retraining_proposal_id`,
- `drift_report_id`,
- current deployment ID,
- current model SHA-256,
- policy generation,
- approver identity label,
- approval generation,
- `authorized_action=start_controlled_retraining`.

Approval CLI summary musí pinovať rovnaký `retraining_approval_id` ako uložený artifact.

### Fresh retraining dataset

Runtime nemusí riskovať náhodnú zmenu acceptance metrics úplne novým synthetic seedom. Namiesto toho odvodí fresh deterministic snapshot z byte-verified baseline CSV:

```text
exact baseline 1200-row dataset
→ preserve all existing rows
→ copy one valid row
→ assign next unique customer_id
→ 1201-row retraining snapshot
→ new dataset SHA-256
```

Tým je dataset subject nový, ale distribúcia zostáva prakticky rovnaká. Training používa canonical ML seed `20260805`; nový operation subject vzniká cez fresh dataset SHA a approval/proposal lineage, nie umelou zmenou random seeda.

### Live provider execution

Driver odmietne non-loopback Tracking URI aj port, ktorý už používa cudzí proces. Potom spustí nový MLflow server nad baseline:

- existing SQLite metadata DB,
- existing filesystem artifact store,
- loopback-only endpoint.

Pred retrainingom prečíta:

```text
champion alias → baseline numeric Registry version
```

Controlled executor dostane:

- exact approval,
- exact proposal a drift report,
- exact current deployment,
- fresh dataset SHA,
- exact source revision,
- `registry_alias=champion`,
- `promotion_alias=champion`,
- durable operation/state paths.

Úspešný operation musí vytvoriť:

```text
new training manifest
→ new candidate
→ new MLflow Registry version
→ champion alias → new numeric version
→ exact Registry artifact read-back
→ local promotion release
→ completed durable state
```

## Provider read-back

Po completed operation gate overí nezávisle od CLI summary:

- Registry version inventory narástol presne o jednu version,
- nový version nie je baseline version,
- `champion` alias ukazuje na nový exact version,
- model-version tags pinujú nový candidate, source revision a model SHA,
- existujúci `registry-verify` prejde nad novým `registry-evidence.json`,
- model sa načíta cez exact `models:/<name>/<version>` URI,
- exact model vykoná prediction smoke test.

Mutable alias sa teda používa ako control-plane pointer, ale evidence zároveň zaznamenáva numeric exact URI/version.

## Replay bez duplicate side effectu

Po úspechu sa ten istý controlled-retraining command spustí druhýkrát s rovnakými authoritative subjects.

Musí nastať:

```text
status=already_completed
→ rovnaký state_id
→ nezmenený Registry version inventory
→ champion stále ukazuje na rovnakú novú version
→ žiadna tretia Registry version
```

To je live-provider idempotency/read-back dôkaz pre completed replay.

## Cleanup evidence

Driver vždy stopne MLflow process. Až po stopnutí provider procesu zaznamená:

- SQLite DB SHA-256,
- MLflow server-log SHA-256,
- `provider_stopped=true`.

Workflow následne odstráni celý disposable Registry/retraining runtime aj virtual environment a až potom doplní:

```text
workflow_cleanup_verified=true
```

Canonical evidence JSON zostáva mimo disposable runtime rootu, následne sa uploadne ako Actions artifact. `always()` cleanup ešte raz ukončí prípadný MLflow process a odstráni runtime/venv paths.

## Evidence subject

Canonical evidence obsahuje minimálne:

- exact Git SHA,
- baseline candidate/model/dataset/Registry version,
- baseline current-deployment ID,
- baseline a window monitoring IDs,
- drift report a proposal IDs,
- forged approval refusal,
- exact approval ID,
- controlled operation/state IDs,
- fresh dataset SHA a row count,
- new candidate/model/release IDs,
- new Registry version,
- champion alias read-back,
- exact-version model-load result,
- completed replay result,
- SQLite/log hashes po provider stop-e,
- provider/workflow cleanup flags,
- canonical evidence ID.

## Proof boundary

Successful gate preukáže live local:

```text
synthetic drift evidence
→ exact proposal
→ explicit approval
→ Machine Learning retraining
→ SQLite-backed MLflow Registry side effect
→ new numeric version
→ alias read-back
→ exact model load
→ completed replay without duplicate Registry side effect
→ provider + filesystem cleanup
```

Nepreukáže:

- production telemetry,
- production business drift,
- cryptographic external approver identity,
- production traffic switch,
- actual current-deployment container image,
- post-retraining container build/deploy/canary,
- remote OCI Registry,
- Kubernetes/cloud rollout,
- HA alebo disaster recovery.

Current deployment image v tomto gate je explicitne označený ako control-plane-only subject. Post-retraining image/deployment/canary musí byť preukázaný samostatným chain gate-om.

Kým dedicated workflow nevytvorí successful exact-revision run, tento gate je `Implemented`, nie `Runtime verified`.
