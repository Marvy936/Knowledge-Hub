# MLflow experiment tracking a Model Registry

MLflow Tracking a Model Registry tvoria control a evidence vrstvu pre runs, logged models, artifacts, versions, tags a aliases. Nevykonávajú automaticky správny training, validation ani deployment. Produkčný workflow musí preto ukázať, ako sa dataset, run, logged model, registered version, immutable release a loaded runtime prepájajú a kde sa končí authority MLflow servera.

V incidente `MLOPS-PAY-96` data scientist našiel najlepší run v UI a zaregistroval model priamo pod produkčným názvom. Alias `champion` sa presunul, ale deployment si alias resolvoval až pri štarte jednotlivých replík. Jedna replika načítala novú version, ostatné zostali na starej. Run navyše logoval dataset URL bez immutable snapshotu. MLflow metadata boli konzistentné, no produkčný composite generation a dataset lineage neboli.

## 1. Architecture a stores

Tracking Server poskytuje API a UI. Backend store drží run, experiment, metric, parameter, tag a Registry metadata. Artifact store drží model bytes, plots, tables a ďalšie súbory. Database-backed backend je potrebný pre plný self-hosted Registry workflow; artifact credentials a access pattern závisia od server configuration.

```text
client
→ Tracking Server API
→ backend store: metadata
→ artifact store: bytes
→ Model Registry: names, versions, aliases, tags
```

Backend backup bez artifact store nie je restore. Artifact store bez backendu stráca run/Registry graph. DR test musí obnoviť obidve vrstvy a overiť model load.

Self-hosted server používa authentication, TLS/reverse proxy, authorization, network policy, secret management a database/object-store backup. Lokálny `mlruns` quickstart nie je produkčná architecture.

## 2. Secure a pinned environment

Praktický lab pinne MLflow a dependencies. `pip install mlflow` bez version/hash je vhodný iba na disposable exploration. Secure install môže používať hash-checking a trusted upload cutoff.

```bash
python -m venv .venv
source .venv/bin/activate

pip install pip-tools
pip-compile --generate-hashes \
  --output-file requirements.txt requirements.in
pip install --require-hashes --only-binary :all: -r requirements.txt
```

`requirements.in` obsahuje auditovanú exact MLflow version. Container image sa pinne digestom a jeho provenance sa verifikuje podľa supply-chain policy.

Client explicitne nastaví tracking a Registry URI. Environment variables nesmú uniknúť do run params alebo notebook outputu.

```bash
export MLFLOW_TRACKING_URI=https://mlflow.example.com
export MLFLOW_REGISTRY_URI=https://mlflow.example.com
```

## 3. Experiment, run a dataset lineage

Experiment združuje runs pre konkrétny task alebo lifecycle boundary. Run je execution record. Dataset input je samostatný subject a loguje sa cez dataset API, no source URI musí ukazovať na immutable alebo resolvable snapshot.

```python
import mlflow
import mlflow.data
import pandas as pd

mlflow.set_tracking_uri("https://mlflow.example.com")
mlflow.set_registry_uri("https://mlflow.example.com")
mlflow.set_experiment("/fraud/training")

train_df = pd.read_parquet(
    "s3://ml-data/fraud/snapshots/2026-07-31/data.parquet"
)

training_data = mlflow.data.from_pandas(
    train_df,
    source="s3://ml-data/fraud/snapshots/2026-07-31/manifest.json",
    name="fraud-train-2026-07-31",
    targets="label",
)

with mlflow.start_run(run_name="fraud-xgb-candidate") as run:
    mlflow.log_input(training_data, context="training")
    mlflow.log_params({
        "source_commit": "5e3a...",
        "pipeline_generation": "fraud-train-v19",
        "feature_generation": "fraud-offline-v12",
        "runtime_image_digest": "sha256:train...",
    })
```

`source` string nie je automaticky checksum verification. Pipeline musí samostatne validovať manifest digest a uložiť ho ako immutable tag/param alebo artifact.

Parameters sú typicky immutable within run semantics; tags sú mutable metadata a nemajú nahrádzať immutable identity. Metric history môže mať viac krokov a timestamps. Promotion gate musí používať explicitný evaluation artifact/verdict, nie náhodne poslednú metric value z UI.

## 4. Logging modelu a complete package

Model sa loguje cez flavor API so signature, input example a locked environment. Return value/logged-model identity sa zachytí pre ďalší krok. Exact syntax sa môže líšiť podľa flavor a MLflow version; repository pin chráni API contract.

```python
from mlflow.models import infer_signature
import mlflow.sklearn

signature = infer_signature(X_train, model.predict(X_train.head(20)))

model_info = mlflow.sklearn.log_model(
    sk_model=model,
    name="fraud-model",
    signature=signature,
    input_example=X_train.head(5),
    pip_requirements="requirements.txt",
)

mlflow.set_tag("candidate_model_uri", model_info.model_uri)
```

MLflow 3 používa Logged Models ako first-class identity oddelene od runu. Starší `runs:/<run_id>/<artifact_path>` URI môže byť stále dostupný podľa workflowu, no nový design má preferovať explicitný model ID/URI a nesmie zamieňať run status s model readiness.

Po logovaní sa model načíta z fresh environmentu a vykoná smoke/parity test. UI artifact existence nie je dôkaz loadability.

## 5. Evaluation evidence pred registráciou

Registrácia nie je validation. Candidate sa najprv evaluuje na versioned dataset a výsledky sa logujú ako artifacts/metrics s presným evaluator a policy generation. Gate môže vytvoriť signed evidence bundle.

```python
evaluation = mlflow.models.evaluate(
    model=model_info.model_uri,
    data=eval_df,
    targets="label",
    model_type="classifier",
)

mlflow.log_dict(
    {
        "candidate_model_uri": model_info.model_uri,
        "evaluation_dataset": "fraud-eval-2026-07-31",
        "policy_generation": "fraud-promotion-v9",
        "metrics": evaluation.metrics,
    },
    "promotion/evaluation-manifest.json",
)
```

Aggregate metrics sa dopĺňajú segmenty, calibration, robustness, package load a capacity evidence. MLflow evaluator output je evidence, nie business approval.

## 6. Registrácia a exact read-back

Model version sa vytvorí až po gate. `mlflow.register_model()` môže byť asynchronous relative to artifact copying/backend work podľa implementation; workflow musí čítať výslednú version a status.

```python
import mlflow
from mlflow import MlflowClient

client = MlflowClient()

registered = mlflow.register_model(
    model_uri=model_info.model_uri,
    name="fraud-prod",
)

version = client.get_model_version(
    name="fraud-prod",
    version=registered.version,
)

assert version.source
client.set_model_version_tag(
    name="fraud-prod",
    version=version.version,
    key="evaluation_bundle_digest",
    value="sha256:eval...",
)
client.set_model_version_tag(
    name="fraud-prod",
    version=version.version,
    key="release_candidate",
    value="fraud-serving-2026-08-03.5",
)
```

Read-back overí source/model ID, run linkage, tags a artifact digest z authoritative manifestu. Registry version number je unique v registered model name, nie global digest.

Unknown outcome pri register alebo tag mutation sa rieši read-before-retry. Slepý retry môže vytvoriť ďalšiu version.

## 7. Aliases, tags a promotion

Alias je mutable named reference na konkrétnu model version. Je vhodný ako control-plane pointer, nie ako immutable deployment identity. Fixed stages sú deprecated v prospech aliases, tags a environment separation.

```python
client.set_registered_model_alias(
    name="fraud-prod",
    alias="candidate",
    version=version.version,
)

candidate = client.get_model_version_by_alias(
    name="fraud-prod",
    alias="candidate",
)

assert str(candidate.version) == str(version.version)
```

Promotion workflow po approvals môže compare-and-set semantics implementovať aplikačne: najprv prečíta current alias, overí expected previous version a až potom ho zmení. MLflow alias API samo nemusí vyjadrovať celý business transaction.

```python
current = client.get_model_version_by_alias("fraud-prod", "champion")
if str(current.version) != expected_previous_version:
    raise RuntimeError("Champion moved; reconcile before promotion")

client.set_registered_model_alias(
    "fraud-prod", "champion", version.version
)
```

Po mutation sa alias znovu prečíta a decision event sa uloží. Deployment resolver premení alias na exact version a package digest a vytvorí immutable release manifest. Pody nemajú každý nezávisle resolveovať mutable alias počas rollout-u.

## 8. Environment separation

Development, staging a production môžu používať oddelené registered model names alebo Registry instances podľa governance a permissions. Environment-specific model name znižuje riziko, že development actor zmení production alias.

Kopírovanie/promoting medzi environments musí zachovať model digest, lineage a evidence. Nová production version môže mať iné číslo než staging version; identity preto nesmie byť iba version integer.

RBAC oddeľuje read experiment, create run, log artifact, create version, set alias a delete. Basic auth alebo managed service permissions sa testujú negatívnymi cases.

## 9. Search, discovery a leaderboard boundary

`mlflow.search_runs()` a `mlflow.search_logged_models()` umožňujú discovery podľa metrics, params a tags. Search result nie je deterministic promotion verdict, ak metrics pochádzajú z rôznych datasets alebo evaluators.

Leaderboard query musí filtrovať exact evaluation dataset a policy generation. Ak model nemá required evidence, nepatrí do candidate setu. Search syntax a ordering sa pinne/testuje, pretože implicitný missing-value behavior môže meniť poradie.

UI je vhodné na exploration a review, ale authoritative promotion workflow používa API, stored manifest a audit event. Manuálne kliknutie bez decision ID vytvára evidence gap.

## 10. Artifact download, load a serving smoke test

Pred deploymentom sa exact version načíta z Registry a artifact store cez rovnakú identity, ktorú release manifest neskôr pinne. Tento krok overí client permissions, artifact availability, package load a základnú inference parity, ale ešte nie produkčný traffic ani business workflow.

```python
model_uri = f"models:/fraud-prod/{version.version}"
loaded = mlflow.pyfunc.load_model(model_uri)
predictions = loaded.predict(smoke_df)
```

Tento test overí client access a package load v konkrétnom environmentu. Neoverí production concurrency, feature service ani business policy. Výsledok sa loguje do release evidence.

Lokálny server je vhodný na package/protocol smoke test:

```bash
mlflow models serve \
  -m "models:/fraud-prod/184" \
  -p 5000 \
  --env-manager virtualenv

curl http://127.0.0.1:5000/invocations \
  -H 'Content-Type: application/json' \
  --data '{"dataframe_split":{"columns":["f1","f2"],"data":[[1.0,2.0]]}}'
```

Container sa môže vytvoriť cez `mlflow models build-docker`, no output image sa následne digest-pinne, skenuje, podpisuje a testuje. MLflow command success nie je supply-chain acceptance.

## 11. Failure hypotheses a troubleshooting

Ak run nie je viditeľný, skúma sa tracking URI, experiment, authentication, async logging a backend. Ak metadata existujú, ale artifact load zlyhá, skúma sa artifact URI, credentials, server proxy mode a object-store bytes. Ak Registry API nefunguje, skúma sa database-backed backend a permissions. Ak alias ukazuje správne, ale produkcia používa starý model, problém je deployment resolution alebo loaded runtime, nie Registry metadata.

Praktický read-back používa API a CLI, nie screenshot:

```python
run = client.get_run(run_id)
model_version = client.get_model_version("fraud-prod", "184")
champion = client.get_model_version_by_alias("fraud-prod", "champion")
```

Pred restartom servera sa zachytí backend connectivity, artifact access a request/error logs. Restart môže maskovať pool alebo credential problém bez vysvetlenia.

## 12. Backup, restore a acceptance

Backup zahŕňa database/backend, artifact store, authentication config, trusted roots a operational manifests. Restore test načíta run, dataset input, logged model, registered version, alias a model artifact, potom vykoná smoke inference.

Pozitívna acceptance vyžaduje pinned client/server version, immutable dataset reference, explicit run/model identity, complete package, evaluation evidence, exact registered version, alias read-back a immutable deployment resolution. Recovery acceptance vyžaduje restore oboch stores a druhú register/load operáciu. Forbidden acceptance je „run je zelený“, UI model card, alias alebo Registry version bez artifact digest a loaded-runtime proof.

Second-operation test zopakuje logging alebo promotion s rovnakým subjectom. Idempotentný workflow rozpozná existujúci model/evidence alebo vytvorí jasne novú generation; nesmie potichu vytvoriť duplicate version po unknown outcome.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: ML supply-chain security](ml-supply-chain-security.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: MLflow evaluation, tracing a deployment →](mlflow-evaluation-tracing-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
