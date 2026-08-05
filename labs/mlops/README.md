# MLOps and ML Platforms flagship lab

Tento projekt rozširuje syntetický classification workflow zo Section 18 o skutočný lokálny MLOps control plane. Používa MLflow Tracking a Model Registry nad SQLite backendom, lokálny artifact store, immutable JSON manifests, model aliases, FastAPI serving contract, deterministic drift, controlled retraining, canary evaluation a alias-based rollback.

```text
Git/source revision + dataset SHA
→ schema a leakage validation
→ train/validation/test experiment runs
→ MLflow tracking + skops model artifacts
→ registered model versions
→ candidate alias + promotion request digest
→ explicit approval + champion alias read-back
→ HTTP serving smoke test
→ current-data monitoring + PSI drift signal
→ retraining + new candidate version
→ deterministic 90/10 canary evidence
→ approved promotion
→ rollback na previous champion
```

Projekt nevyžaduje cloud, Kubernetes ani externú databázu. SQLite a filesystem sú vhodné iba pre izolovaný lab a solo development; nepredstavujú odporúčanú shared production platformu.

## Workspace state

Každý run používa explicitný workspace, napríklad `labs/mlops/.runtime`:

```text
.runtime/
├── mlflow.db
├── artifacts/
├── data/
│   ├── baseline.csv
│   └── current.csv
├── requests/
├── reports/
├── releases/
└── rollback/
```

`mlflow.db` vlastní tracking metadata, experiment runs, registered model versions, aliases a tags. Model artifacts sú uložené pod `artifacts/`. JSON request/report/release súbory dopĺňajú MLflow state o repository-readable approval, canary a recovery evidence. Každý takýto dokument má canonical SHA-256 digest; zmena payloadu po schválení je odmietnutá.

## Inštalácia

Z koreňa repozitára:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "labs/machine-learning[dev]" -e "labs/mlops[dev]"
```

PowerShell aktivácia:

```powershell
.venv\Scripts\Activate.ps1
```

## Kompletný lifecycle

### 1. Baseline training a candidate request

```bash
python -m mlops_lab bootstrap \
  --workspace labs/mlops/.runtime \
  --rows 1200 \
  --seed 20260805
```

Command vytvorí a validuje baseline dataset, založí MLflow experiment, fitne kandidátov, zapíše params/metrics/lineage artifacts, zaregistruje logistic regression a random forest ako samostatné model versions a priradí najlepšej prijatej verzii alias `candidate`. Výstup obsahuje promotion request path a digest.

### 2. Explicitná prvá promotion

```bash
python -m mlops_lab promote \
  --workspace labs/mlops/.runtime \
  --request labs/mlops/.runtime/requests/bootstrap-promotion.json \
  --approver local-operator
```

Prvá promotion nepotrebuje canary voči neexistujúcemu incumbentovi. Command overí request digest, model version tags a candidate alias, potom nastaví `champion`, prečíta ho späť z Registry a vytvorí release manifest.

### 3. Serving contract

```bash
python -m mlops_lab serve-smoke \
  --workspace labs/mlops/.runtime
```

FastAPI `TestClient` vykoná `/health` a `/predict` proti modelu načítanému cez `models:/knowledge-hub-churn@champion`. Test preukazuje HTTP schema, registry alias resolution, model signature a prediction path v jednom procese. Nevykonáva sieťový load balancer ani production container runtime.

Pre manuálny server:

```bash
export MLOPS_WORKSPACE="$PWD/labs/mlops/.runtime"
uvicorn mlops_lab.service:app --factory --host 127.0.0.1 --port 8080
```

Repository obsahuje aj `Dockerfile`. Image potrebuje workspace mount s `mlflow.db` a artifacts; samotný úspešný image build nepreukazuje, že správny registry alias alebo model generation bol načítaný.

### 4. Drift signal

```bash
python -m mlops_lab monitor \
  --workspace labs/mlops/.runtime \
  --rows 1200 \
  --seed 20260806
```

Monitor vytvorí deterministický shifted current dataset, validuje ho, vypočíta PSI pre numerické features, načíta champion a zaznamená prediction-rate zmenu. Retraining trigger vznikne iba pri prekročení explicitného PSI threshold-u; samotný drift alert ešte nie je promotion authority.

### 5. Controlled retraining

```bash
python -m mlops_lab retrain \
  --workspace labs/mlops/.runtime \
  --drift-report labs/mlops/.runtime/reports/drift.json \
  --seed 20260807
```

Command odmietne report bez platného digestu, `triggered=true` alebo matching current dataset SHA. Úspešný retraining vytvorí nové MLflow runs a registered versions a nastaví prijatú verziu ako nový `candidate`; `champion` zatiaľ nemení.

### 6. Canary evidence

```bash
python -m mlops_lab canary \
  --workspace labs/mlops/.runtime \
  --request labs/mlops/.runtime/requests/retrain-promotion.json \
  --drift-report labs/mlops/.runtime/reports/drift.json
```

Canary načíta `champion` aj exact candidate version, vykoná oba modely nad current datasetom a vytvorí deterministické 90/10 routing counts. Gate kontroluje candidate F1/recall, maximálnu quality regression a bounded disagreement. Report obsahuje versions, dataset SHA a digest.

### 7. Promotion a rollback

```bash
python -m mlops_lab promote \
  --workspace labs/mlops/.runtime \
  --request labs/mlops/.runtime/requests/retrain-promotion.json \
  --canary-report labs/mlops/.runtime/reports/canary.json \
  --approver local-operator

python -m mlops_lab rollback \
  --workspace labs/mlops/.runtime \
  --release labs/mlops/.runtime/releases/release-v4.json \
  --approver incident-commander
```

Promotion prečíta nový `champion` alias späť a release manifest zachová previous champion version. Rollback odmietne stale release, pri ktorom current champion už nezodpovedá promoted version; pri úspechu reassignuje alias na previous version a vykoná inference read-back.

## Testy

```bash
pytest labs/mlops/tests -q
```

Test suite pokrýva canonical digest tamper refusal, PSI behavior, kompletný bootstrap → promotion → serving → drift → retraining → canary → promotion → rollback lifecycle a stale/forbidden transitions.

## Security a proof boundary

Modely sa logujú cez MLflow scikit-learn flavor so `skops` serialization, explicitným input example a signature. Registry alias je mutable deployment reference; immutable evidence preto vždy zachováva exact model version, run ID, dataset SHA, source revision a request/report digest.

Úspešný lab preukazuje lokálny MLOps state machine a skutočné MLflow API transitions na konkrétnom resolved runtime. Nepreukazuje multi-user authorization, remote artifact-store consistency, HA tracking server, Kubernetes rollout, production traffic, delayed ground truth, reálny business impact ani disaster recovery externých platformových komponentov.

## Cleanup

```bash
rm -rf labs/mlops/.runtime
```

Cleanup je hotový až po potvrdení, že workspace neexistuje. Git source, tests a dokumentácia zostávajú nezmenené.
