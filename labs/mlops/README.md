# MLOps flagship project

Tento lab implementuje praktický lifecycle sekcie 19 po samostatných trust a evidence vrstvách. Každá vrstva má vlastný authoritative subject, refusal paths a proof boundary.

```text
trusted dataset a ML training artifact
→ immutable dataset snapshot
→ training-derived evaluation
→ accepted candidate
→ MLflow Tracking a database-backed Registry
→ exact registered version a artifact read-back
→ immutable release a deployment subject
→ identity-bound HTTP serving
→ deterministic canary a rollback evidence
→ aggregate monitoring a semantic drift report
→ exact human approval
→ controlled retraining operation
```

## Aktuálne implementované vrstvy

### Promotion foundation

- workspace-independent dataset a candidate identities,
- canonical JSON fingerprints,
- strict candidate a alias-state contracts,
- compare-before-promote,
- stale promotion refusal,
- immutable release manifest.

### Training lineage

- evaluation odvodená z exact ML training manifestu,
- dataset a model byte read-back,
- source revision binding,
- acceptance-gate validation,
- dummy-baseline refusal.

Detail: [`TRAINING-LINEAGE.md`](TRAINING-LINEAGE.md)

### Tracking, Registry a artifact read-back

- loopback MLflow server contract,
- SQLite metadata backend,
- oddelený proxied filesystem artifact destination,
- run params, metrics, tags a candidate evidence,
- registered model version a mutable alias read-back,
- source artifact download a SHA-256 porovnanie,
- exact numeric Registry URI,
- prediction parity,
- restart verification contract.

Detail: [`RUNTIME-EVIDENCE.md`](RUNTIME-EVIDENCE.md)

### Serving, container runtime, canary a rollback

- immutable deployment manifest,
- exact Registry version a model digest,
- image digest binding,
- non-root FastAPI/Uvicorn serving source,
- strict HTTP request schema,
- readiness response s deployment identity,
- deterministic routing state,
- source-level traffic medzi dvoma loopback Uvicorn generations,
- canary evidence s identity mismatch detection,
- explicit `no_data`, `insufficient_evidence`, `continue` a `rollback`,
- rollback na exact previous deployment subject,
- executable container runtime driver `scripts/run_containerized_inference_runtime.py`, ktorý nad artifacts z authoritative Registry gate-u buildne `Dockerfile.serving`, resolvuje local content-addressed Docker image ID, vytvorí immutable deployment subject, spustí image podľa exact ID a vykoná live loopback HTTP readiness/inference,
- explicitný non-root read-back `uid=10001`, read-only serving mounts, extra-field HTTP refusal a startup refusal pri nesprávnom runtime image digest,
- dedicated hosted workflow `.github/workflows/mlops-containerized-inference-runtime.yml`, ktorý po úspešnom execution musí zachovať canonical JSON evidence a cleanup read-back.

Existencia drivera a workflowu je source-level `Implemented`. Kým nevznikne exact successful workflow/runtime record, neznamená to `Runtime verified` ani OCI Registry/Kubernetes deployment.

Detaily:

- [`SERVING-CANARY-ROLLBACK.md`](SERVING-CANARY-ROLLBACK.md)
- [`CONTAINER-SERVING.md`](CONTAINER-SERVING.md)
- [`LIVE-CANARY.md`](LIVE-CANARY.md)

### Monitoring, drift a approval

- aggregate feature, prediction, latency a error profiles bez raw record retention,
- numeric PSI a categorical TVD,
- semantic profile a drift-report validation,
- deterministic status precedence,
- control/shift drift injection,
- exact retraining proposal,
- human approval viazané na proposal aj canonical drift report.

Detail: [`MONITORING-DRIFT-RETRAINING.md`](MONITORING-DRIFT-RETRAINING.md)

### Controlled retraining executor a live-provider gate

Source executor obsahuje:

- canonical operation ID,
- approval/report/proposal/current-deployment read-back,
- nový dataset snapshot gate,
- single-writer lock,
- durable phase state,
- read-before-retry,
- checkpoint recovery,
- deterministic training adapter,
- training-manifest, candidate a Registry read-back,
- compare-before-promote,
- completed-operation replay bez opakovania side effects.

Nad tým existuje executable live runtime driver `scripts/run_live_retraining_runtime.py` a dedicated hosted workflow `.github/workflows/mlops-live-retraining-runtime.yml`.

Gate zámerne skladá existujúce authoritative vrstvy:

```text
run_registry_gate.sh
→ baseline Registry version + champion alias
→ deterministic drift window
→ retraining proposal
→ forged proposal approval refusal
→ exact human-style approval artifact
→ fresh deterministic 1201-row dataset snapshot
→ run_controlled_retraining.py
→ new live MLflow Registry version
→ champion alias read-back
→ exact models:/name/version load
→ completed replay
→ unchanged version inventory after replay
→ provider + filesystem cleanup
```

Monitoring events sú synthetic. Training a MLflow Registry side effects sú live local-provider operations. Current deployment image v tomto gate je iba explicitný control-plane subject; post-retraining container/deployment/canary runtime je samostatná ďalšia vrstva.

Detaily:

- [`CONTROLLED-RETRAINING.md`](CONTROLLED-RETRAINING.md)
- [`LIVE-CONTROLLED-RETRAINING.md`](LIVE-CONTROLLED-RETRAINING.md)

## Stav dôkazov

`Implemented` neznamená automaticky `Runtime verified`.

Source-level vrstvy majú oddelené exact-source test evidence a executable hosted runtime harnesses pre containerized inference aj live controlled retraining. Central GitHub Actions closeout však zostáva otvorený kvôli issue #151: matching MLOps PR a push events nevytvárajú connector-readable workflow runy.

Lab preto netvrdí:

- úspešný živý end-to-end controlled retraining run na authoritative revision,
- úspešný actual Docker image build/container HTTP run na authoritative revision,
- OCI Registry manifest/digest alebo vzdialený image pull,
- platform load-balancer traffic switch,
- production telemetry alebo reálny časový drift,
- external cryptographic approval identity,
- post-retraining container/canary read-back,
- HA, backup/restore alebo disaster recovery,
- production readiness alebo business outcome.

Autoritatívny status: [`../../PRACTICAL-STATUS.md`](../../PRACTICAL-STATUS.md)

## Inštalácia

Foundation a pure contract tests:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "labs/mlops[dev]"
pytest labs/mlops/tests -q
```

Registry a controlled retraining potrebujú aj Machine Learning flagship a MLflow extras:

```bash
python -m pip install -e "labs/machine-learning"
python -m pip install -e "labs/mlops[dev,registry]"
```

Serving source potrebuje serving extra:

```bash
python -m pip install -e "labs/mlops[dev,serving]"
```

Container runtime gate potrebuje lokálny Docker engine a combined ML/MLOps environment s `registry` aj `serving` extras. Dedicated hosted workflow pripravuje Registry subjects existujúcim `run_registry_gate.sh` a až potom volá container driver; driver preto netrénuje ani neregistruje druhú paralelnú implementáciu.

Live controlled-retraining gate potrebuje ML + `mlops[dev,registry,serving]`. Baseline MLflow database/artifact store vytvorí existujúci Registry gate; live driver potom provider znovu otvorí na loopbacku, vykoná approval-bound retraining a provider po evidence read-backu stopne.

PowerShell aktivácia:

```powershell
.venv\Scripts\Activate.ps1
```

## Lokálny MLflow server contract

```bash
mkdir -p labs/mlops/.runtime/mlartifacts

mlflow server \
  --host 127.0.0.1 \
  --port 5057 \
  --backend-store-uri "sqlite:///$(pwd)/labs/mlops/.runtime/mlflow.db" \
  --artifacts-destination "file://$(pwd)/labs/mlops/.runtime/mlartifacts" \
  --allowed-hosts "127.0.0.1:*,localhost:*"
```

Server je development-only. Nemá vzdialený access, TLS, multi-user authorization ani production durability.

## Training-derived candidate

Static sample evaluation nie je authoritative retraining vstup. Evaluation sa vytvára z exact training manifestu:

```bash
python -m mlops_lab evaluation-from-training \
  --training-manifest labs/machine-learning/.runtime/artifact/manifest.json \
  --dataset labs/machine-learning/.runtime/data/customers.csv \
  --model labs/machine-learning/.runtime/artifact/model.joblib \
  --source-revision <exact-git-sha> \
  --policy-generation ml-training-manifest-v1 \
  --output labs/mlops/.runtime/evaluation.json
```

Až potom vznikne candidate:

```bash
python -m mlops_lab candidate \
  --dataset-manifest labs/mlops/.runtime/dataset-manifest.json \
  --model labs/machine-learning/.runtime/artifact/model.joblib \
  --evaluation labs/mlops/.runtime/evaluation.json \
  --source-revision <exact-git-sha> \
  --output labs/mlops/.runtime/candidate.json
```

## Registry identity

Registry evidence a deployment používajú numeric URI:

```text
models:/KnowledgeHubChurn/1
```

Alias URI ako `models:/KnowledgeHubChurn@champion` je mutable control-plane reference. Historický release, deployment, rollback ani retraining operation ho nesmú používať ako immutable subject.

## Controlled retraining

Monitoring driver najprv vytvorí drift report a proposal. Samostatný approval driver vytvorí approval artifact. Až potom môže `run_controlled_retraining.py` odvodiť operation ID a vykonať training→Registry→promotion lifecycle.

Presný command a recovery semantics sú v [`CONTROLLED-RETRAINING.md`](CONTROLLED-RETRAINING.md). Live provider acceptance a replay semantics sú v [`LIVE-CONTROLLED-RETRAINING.md`](LIVE-CONTROLLED-RETRAINING.md).

## Cleanup

```bash
rm -rf labs/mlops/.runtime
rm -rf labs/machine-learning/.runtime
```

PowerShell:

```powershell
Remove-Item -Recurse -Force labs/mlops/.runtime
Remove-Item -Recurse -Force labs/machine-learning/.runtime
```

Cleanup je dokončený až po read-backu, že runtime paths neexistujú.
