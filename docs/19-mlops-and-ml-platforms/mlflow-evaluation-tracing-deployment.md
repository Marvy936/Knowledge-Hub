# MLflow evaluation, tracing a deployment

MLflow poskytuje viac samostatných surface pre classic ML evaluation, GenAI/agent evaluation, tracing a model deployment. Tieto surface sa nesmú zmiešať do jedného neurčitého „MLflow eval“. Classic ML používa `mlflow.models.evaluate()` a `EvaluationMetric`; GenAI evaluation používa `mlflow.genai.evaluate()` a `Scorer`; tracing je orientované na execution spans a production requests. Ich objects a acceptance semantics nie sú interoperabilné.

V incidente `MLOPS-PAY-96` tím použil classic classifier evaluation na model package, GenAI trace scorer na vysvetľovací assistant a lokálny MLflow server na serving smoke test. V dashboarde sa všetky výsledky označili ako `quality_passed`. Promotion následne ignorovala, že classifier threshold validation zlyhala v jednom segmente, trace dataset bol sampled iba zo successful requests a local server bežal s iným worker/concurrency profilom než produkcia. Root cause bola strata subjectu a authority medzi evaluation, trace a deployment evidence.

## 1. Rozdelenie surface a authority

Classic evaluation hodnotí prediktívny model alebo predictions nad datasetom. GenAI evaluation hodnotí outputy alebo traces pomocou code-based či model-based scorers podľa svojho API. Tracing zachytáva execution flow, latency, inputs, outputs a metadata. Deployment vytvára runnable server/image/target.

```text
classic model evaluation
→ metric/result artifacts
→ validation verdict

GenAI/agent traces
→ spans a request evidence
→ scorers a assessments

MLflow model package
→ local server alebo container
→ external production deployment
```

Žiadny surface automaticky nepreukazuje mature business outcome. Promotion policy musí určiť, ktoré evidence objects sú required pre konkrétny system type.

## 2. Classic ML evaluation subject

Evaluation manifest viaže candidate, dataset, targets, evaluator configuration, baseline a threshold policy. Rovnaký model nad iným snapshotom je iný evaluation subject.

```yaml
evaluation_id: fraud-eval-2026-08-03.8
system_type: predictive-classifier
candidate_uri: models:/fraud-prod/184
dataset: fraud-eval-2026-07-31
dataset_digest: sha256:eval-data...
targets: label
model_type: classifier
evaluator_generation: mlflow-classic-v6
baseline_uri: models:/fraud-prod/181
threshold_policy: fraud-promotion-v9
segments:
  - channel
  - region
```

`mlflow.models.evaluate()` môže generovať metrics, plots, tables a artifacts. Built-in output sa dopĺňa domain metrics a segment tables, ak rozhodnutie nie je zachytené aggregate metrikou.

```python
import mlflow

candidate_result = mlflow.models.evaluate(
    model="models:/fraud-prod/184",
    data=eval_df,
    targets="label",
    model_type="classifier",
)

baseline_result = mlflow.models.evaluate(
    model="models:/fraud-prod/181",
    data=eval_df,
    targets="label",
    model_type="classifier",
)
```

Eval data sa versionuje a loguje ako dataset input. DataFrame v notebook memory bez snapshotu a digestu nie je reprodukovateľný evidence subject.

## 3. Validation thresholds

Od MLflow 2.18 je validation oddelená od evaluate a používa `mlflow.validate_evaluation_results()`. Threshold môže byť absolútny alebo porovnávací podľa podporovaného `MetricThreshold` contractu. Exact API sa pinne MLflow versionou.

```python
from mlflow.models import MetricThreshold

thresholds = {
    "f1_score": MetricThreshold(
        threshold=0.82,
        greater_is_better=True,
    ),
    "log_loss": MetricThreshold(
        threshold=0.45,
        greater_is_better=False,
    ),
}

mlflow.validate_evaluation_results(
    candidate_result=candidate_result,
    baseline_result=baseline_result,
    validation_thresholds=thresholds,
)
```

Validation exception je machine-readable gate input, nie automatická production decision. Segment, calibration, fairness, robustness, capacity a governance evidence môžu gate zablokovať aj pri úspešných aggregate thresholds.

Threshold names musia presne zodpovedať result metrics. Missing metric nesmie byť ticho považovaná za pass. Policy wrapper zachytí candidate/baseline result IDs, threshold generation a exception detail do immutable verdict artifactu.

## 4. Custom metrics a evaluator code

Custom metric nesie domain logic a preto je executable authority. Jeho source commit, dependencies a tests patria do evaluation subjectu. Metric, ktorá pristupuje k external service, potrebuje timeout, caching/idempotency a versioned dependency.

Classic `EvaluationMetric` a GenAI `Scorer` sú rozdielne abstractions. Nesmú sa navzájom posielať do opačného API. Migrácia medzi legacy LLM metrics a novým GenAI evaluation musí mať parity report.

Custom metric output obsahuje definition, unit, denominator a missing-data behavior. Názov `business_score` bez týchto údajov je auditne nepoužiteľný.

## 5. GenAI evaluation a trace datasets

GenAI evaluation používa `mlflow.genai.evaluate()` a `Scorer` objects. Dataset môže obsahovať inputs, expectations, pre-generated outputs alebo traces. Model-based judge prináša vlastný model/version, prompt/rubric, sampling a nondeterminism; tieto sú súčasť evaluation generation.

Production traces môžu byť vyhľadané, anotované ground truthom a opakovane hodnotené. Reuse znižuje inference cost, ale trace selection musí zachovať population a failure classes. Export iba successful traces vytvára optimistický dataset.

```text
eligible production requests
→ sampled traces
→ redaction a consent/privacy policy
→ annotation/expectations
→ scorer generation
→ evaluation result
```

Automatická evaluation v produkcii môže byť diagnostický monitoring. Ak používa LLM judge, treba sledovať judge failures, cost, latency, coverage a calibration proti human labels. Judge score nie je automatický ground truth.

## 6. Tracing model a instrumentation

Trace obsahuje root request a spans pre interné operácie. Pre LLM/agent systémy môže zachytiť model calls, retrieval, tools a postprocessing. MLflow tracing je OpenTelemetry-compatible, no konkrétne semantic attributes a export path musia byť versioned.

Manual instrumentation môže používať decorator:

```python
import mlflow

@mlflow.trace
def retrieve_and_score(query: str):
    documents = retrieve(query)
    return score(query, documents)
```

Auto-tracing znižuje implementačné úsilie, ale nevie automaticky určiť privacy a business boundaries. Input/output capture sa rediguje alebo vypína pre citlivé spans. PII redaction sa testuje negatívnymi examples; configuration flag nie je dôkaz.

Trace ID patrí do logs/evidence, nie ako unbounded Prometheus label. Sampling policy musí zachovať errors, fallback a tail latency; inak bude trace population selektívna.

## 7. Production tracing reliability

Production tracing môže používať async logging a sampling, aby neblokovalo request path. To vytvára delivery gap: request môže uspieť, ale trace sa stratí pri crashi alebo queue overflow. Monitoring sleduje enqueued, exported, dropped a rejected traces.

MLflow production tracing SDK má menšiu dependency footprint než full package; environment nemá obsahovať konfliktnú kombináciu oboch packages podľa support guidance. Package/version sa pinne v release manifest.

Trace backend potrebuje production-grade database, retention, access control a storage sizing. Traces môžu obsahovať citlivé inputs a tool outputs, takže privacy policy je prísnejšia než pri aggregate metrics.

## 8. Evaluating production traces

Trace evaluation začína explicitným query a snapshotom. Search filter, time range, release/model ID, trace status a sampling generation sa logujú. Retrieved collection sa uloží ako immutable evaluation dataset alebo manifest.

Scorers hodnotia napríklad correctness, safety, groundedness, latency alebo tool behavior. Každý scorer má unit, rubric, version a failure handling. Ak judge timeoutne, result class je `not_evaluated`, nie nula ani pass.

Comparison candidate vs baseline potrebuje rovnaké inputs/traces alebo stable experiment assignment. Dve nezávislé production windows môžu zamieňať traffic mix a seasonality za model difference.

## 9. Deployment smoke test

MLflow local serving overí package, dependency environment, inference server protocol a sample request. Neoverí production ingress, autoscaling, GPU profile ani downstream action.

```bash
mlflow models serve \
  -m "models:/fraud-prod/184" \
  -p 5000 \
  --env-manager virtualenv

curl http://127.0.0.1:5000/invocations \
  -H 'Content-Type: application/json' \
  --data '{"dataframe_split":{"columns":["f1","f2"],"data":[[1.0,2.0]]}}'
```

Server má health/version endpointy podľa inference server specification, ale readiness wrapper musí navyše overiť model load a application warmup. HTTP 200 na `/health` nie je business acceptance.

## 10. Docker build a supply-chain handoff

`mlflow models build-docker` vytvorí image so serving entrypointom. Model URI sa pred buildom rozlíši na immutable model/version a artifact digest. Mutable alias sa nepoužíva ako jediný build input.

```bash
mlflow models build-docker \
  --model-uri "models:/fraud-prod/184" \
  --name "fraud-mlflow:184"
```

Výsledný image sa skenuje, vytvorí sa SBOM/provenance, image sa podpíše a pushne pod digest. Build command success nepotvrdzuje, že base image a dependencies boli trusted. Production deployment manifest viaže image digest aj model package digest.

Generic image s modelom mountovaným za runtime mení trust boundary: admission overí image, ale init/runtime musí overiť mounted model digest.

## 11. Deployment target a external control plane

MLflow deployment toolset môže pracovať s lokálnym serverom a plugins/targets. Produkčný target má vlastnú authority pre rollout, autoscaling, traffic, readiness a rollback. MLflow Registry alias alebo deployment record nepreukazuje, čo všetky repliky načítali.

Deployment adapter musí byť idempotentný a request-correlated. Unknown outcome sa rieši read-before-retry na targete. Release event obsahuje MLflow model identity, image digest, target object generation a loaded fingerprint.

```text
MLflow candidate/version
→ immutable release manifest
→ deployment target desired state
→ resolved workload
→ loaded runtime
→ synthetic request
→ bounded traffic
→ production evidence
```

## 12. Linking traces, models a releases

MLflow 3 Logged Models a active-model/tracing patterns môžu spájať traces s model identity, najmä pri agents/LLM applications. Pre traditional serving môže platforma explicitne logovať release/model tags do trace contextu. Mutable tag nie je dostačujúca identity; uloží sa model ID/version/digest.

Correlation umožní query: ktoré traces vznikli z modelu, release a scorer generation? Bez tejto väzby sa production trace evaluation nedá použiť na promotion alebo RCA.

External model reprezentácia môže evidovať model mimo MLflow artifact storage. Neznamená to, že MLflow overuje external bytes; platforma musí zachovať external digest a authority.

## 13. Failure hypotheses a troubleshooting

Ak evaluation chýba metrics, skúma sa model type, targets, schema, evaluator config a failed artifacts. Ak validation neočakávane passne, skúma sa metric name, direction, missing behavior a baseline result. Ak traces chýbajú, skúma sa instrumentation, sampling, async queue, exporter, authentication a backend. Ak local serve funguje a produkcia nie, rozdiel je v image, resources, features, network alebo target control plane.

Classic a GenAI API confusion sa diagnostikuje podľa imported objectov a docs pre pinned version. „MLflow evaluate nefunguje“ je príliš široká hypotéza.

Pred rerunom sa zachytí evaluation/trace query manifest a server logs. Rerun na zmenenom dataset alebo scorer generation nie je retry rovnakého subjectu.

## 14. Recovery a acceptance

Component recovery potvrdzuje tracking/evaluation API, trace export, model load a deployment adapter. Journey recovery potvrdzuje request → trace → scorer/evaluation → release evidence a serving request. Business recovery sleduje correct action a mature outcome.

Pozitívna acceptance vyžaduje oddelené classic/GenAI subjects, versioned datasets a evaluators/scorers, explicit validation verdict, trace coverage/privacy controls, immutable model/image resolution a target data-plane verification. Recovery acceptance vyžaduje backfill alebo označenie lost traces, repeatable evaluation a second deployment operation. Forbidden acceptance je spoločný `quality_passed` tag, judge score bez population, local serve success ako production proof alebo Registry alias bez loaded-runtime evidence.

Second-operation test znovu evaluuje uložený dataset/traces a vykoná no-op alebo ďalší deployment s rovnakým immutable release. Ak výsledky závisia od mutable scorer, alias, sampled query alebo local cache, workflow nie je reprodukovateľný.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: MLflow experiment tracking a Model Registry](mlflow-experiment-tracking-model-registry.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Kubeflow Pipelines →](kubeflow-pipelines.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
