# MLOps flagship project

Tento lab implementuje praktický lifecycle sekcie 19 po vrstvách. Prvý blok vytvoril deterministic dataset, candidate a promotion contract. Druhý blok pridáva lokálny MLflow Tracking Server, database-backed Model Registry, oddelený artifact store a exact-version read-back.

```text
source dataset a trusted model artifact
→ immutable dataset snapshot
→ accepted candidate manifest
→ MLflow run a logged model
→ registered model version
→ mutable alias read-back
→ original artifact download a SHA-256 verification
→ exact-version model load a prediction parity test
→ immutable registry evidence
```

## Implementovaná hranica

Aktuálne sú implementované:

- SHA-256 identita datasetu a zdrojového model artifactu,
- canonical JSON fingerprints,
- strict schema validation pre dataset, evaluation, candidate, alias state a registry evidence,
- workspace-independent candidate identity bez lokálneho filesystem pathu,
- compare-before-promote a stale-promotion refusal,
- immutable release manifest pre downstream serving,
- lokálny MLflow server s SQLite metadata backendom,
- samostatný proxied filesystem artifact destination,
- run params, metrics, tags a candidate evidence logované do MLflow,
- registered model version a model-version tags,
- mutable alias read-back,
- stiahnutie pôvodného `model.joblib` cez tracking server a porovnanie SHA-256,
- načítanie exact registered version URI,
- prediction parity medzi dôveryhodným source artifactom a Registry version,
- fresh-process verification po reštarte MLflow servera,
- deterministic registry evidence ID,
- unit refusal tests a permanent CI runtime path.

Zatiaľ nie sú implementované ani deklarované ako overené:

- containerized inference service,
- image digest a release-manifest pinning,
- canary traffic medzi dvoma serving generations,
- rollback nasadenej generácie,
- production metrics a explicitný no-data state,
- drift injection a controlled retraining,
- production authentication, authorization, HA alebo backup/restore.

## Dve odlišné storage vrstvy

MLflow metadata backend a artifact store nie sú tá istá vec.

```text
SQLite backend
→ experiments, runs, params, metrics, tags, registered models, versions a aliases

artifact destination
→ model files, candidate JSON, sample request a source model bytes
```

Lokálny lab používa SQLite, pretože Model Registry vyžaduje database-backed store. Artifact bytes sú uložené v samostatnom directory a klient ich uploaduje aj sťahuje cez MLflow server. Zelený test preto musí preukázať existenciu databázy aj artifact files; samotný úspešný API response nestačí.

## Inštalácia

Foundation-only tests:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "labs/mlops[dev]"
pytest labs/mlops/tests -q
```

Registry round-trip potrebuje aj existujúci Machine Learning flagship a MLflow extras:

```bash
python -m pip install -e "labs/machine-learning"
python -m pip install -e "labs/mlops[dev,registry]"
```

PowerShell aktivácia:

```powershell
.venv\Scripts\Activate.ps1
```

## Príprava ML artifactu

Z koreňa repozitára:

```bash
python -m ml_lab generate-data \
  --output labs/machine-learning/.runtime/data/customers.csv \
  --rows 1200 \
  --seed 20260805

python -m ml_lab train \
  --input labs/machine-learning/.runtime/data/customers.csv \
  --output-dir labs/machine-learning/.runtime/artifact \
  --seed 20260805
```

Výsledný `model.joblib` je trusted local artifact iba v rámci kontrolovaného training runu. `joblib` používa pickle semantics. Registry command ho načíta až po tom, ako candidate manifest potvrdí jeho byte size a SHA-256.

## Dataset snapshot a candidate

```bash
python -m mlops_lab snapshot \
  --dataset labs/machine-learning/.runtime/data/customers.csv \
  --output labs/mlops/.runtime/dataset-manifest.json \
  --dataset-name churn-training \
  --generation churn-data-2026-08-06

python -m mlops_lab candidate \
  --dataset-manifest labs/mlops/.runtime/dataset-manifest.json \
  --model labs/machine-learning/.runtime/artifact/model.joblib \
  --evaluation labs/mlops/data/sample-evaluation.json \
  --source-revision local-dev \
  --output labs/mlops/.runtime/candidate.json
```

Candidate identity závisí od dataset generation a digestu, model size a digestu, evaluation bundle a source revision. Mutable timestamp, lokálna cesta ani názov workspace nie sú súčasťou identity.

## Lokálny MLflow server

Príklad používa loopback endpoint, SQLite backend a oddelený artifact directory:

```bash
mkdir -p labs/mlops/.runtime/mlartifacts

mlflow server \
  --host 127.0.0.1 \
  --port 5057 \
  --backend-store-uri "sqlite:///$(pwd)/labs/mlops/.runtime/mlflow.db" \
  --artifacts-destination "file://$(pwd)/labs/mlops/.runtime/mlartifacts" \
  --allowed-hosts "127.0.0.1:*,localhost:*"
```

Server je development-only. Nie je nakonfigurovaný pre vzdialený access, TLS, multi-user authorization alebo production durability.

## Registry round-trip

V druhom termináli:

```bash
python -m mlops_lab registry-roundtrip \
  --candidate labs/mlops/.runtime/candidate.json \
  --model labs/machine-learning/.runtime/artifact/model.joblib \
  --sample-request labs/machine-learning/data/sample-request.json \
  --tracking-uri http://127.0.0.1:5057 \
  --experiment-name knowledge-hub-mlops-local \
  --model-name KnowledgeHubChurn \
  --alias champion \
  --download-dir labs/mlops/.runtime/downloaded \
  --output labs/mlops/.runtime/registry-evidence.json
```

Command vykoná tieto hard checks:

```text
candidate model digest == local model bytes
→ run tags a model-version tags sa zhodujú
→ Registry version má source run lineage
→ alias read-back ukazuje na vytvorenú version
→ source/model.joblib sa stiahne cez server
→ downloaded SHA-256 == candidate model SHA-256
→ models:/KnowledgeHubChurn/<version> sa načíta
→ source a Registry prediction sa zhodujú
```

Registry evidence obsahuje exact URI vo forme:

```text
models:/KnowledgeHubChurn/1
```

Alias URI `models:/KnowledgeHubChurn@champion` je zámerne mutable control-plane reference. Evidence ho nesmie používať ako immutable deployment subject.

## Fresh-process verification

Po ukončení a opätovnom spustení servera nad rovnakou databázou a artifact directory:

```bash
python -m mlops_lab registry-verify \
  --evidence labs/mlops/.runtime/registry-evidence.json \
  --sample-request labs/machine-learning/data/sample-request.json \
  --tracking-uri http://127.0.0.1:5057
```

Verification načíta iba exact version URI zaznamenané v evidence. Nevykonáva nové alias resolution. Tým sa oddeľuje historický deployment subject od aktuálnej mutable hodnoty aliasu.

## Local promotion contract

Registry alias nenahrádza compare-before-promote contract. Lokálny release manifest sa vytvára samostatne:

```bash
python -m mlops_lab promote \
  --candidate labs/mlops/.runtime/candidate.json \
  --alias-state labs/mlops/.runtime/registry-aliases.json \
  --alias champion \
  --expected-current none \
  --release-output labs/mlops/.runtime/release.json
```

Downstream serving bude v ďalšom bloku pinovať immutable release manifest, exact Registry version a model digest. Pri štarte každej repliky sa nesmie znovu resolvovať mutable alias.

## CI execution profile

Permanentný workflow používa Linux X64 self-hosted runner iba pre kód z rovnakého repozitára. Checkout neukladá Git credentials. Runtime job má iba `contents: read`; push-only status publisher má `statuses: write`, nevykonáva checkout a nespúšťa PR kód.

Registry gate:

1. vytvorí deterministic ML artifact,
2. vytvorí candidate,
3. spustí loopback MLflow server,
4. vykoná Registry a artifact round-trip,
5. overí exact version,
6. reštartuje server,
7. zopakuje exact-version verification,
8. overí SQLite DB aj artifact directory,
9. odstráni celý virtual environment a runtime state.

## Acceptance hranica

Úspešný registry run preukazuje:

- database-backed local Model Registry,
- run a model-version lineage read-back,
- oddelený local artifact store,
- source artifact byte integrity po download-e,
- exact registered version loadability v rovnakom resolved runtime,
- prediction parity a persistence po reštarte servera.

Nepreukazuje fresh dependency reconstruction na inom OS, production serving, canary outcome, drift, business impact, HA, disaster recovery ani production security.

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
