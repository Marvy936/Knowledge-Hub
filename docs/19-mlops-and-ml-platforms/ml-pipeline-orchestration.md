# ML pipeline orchestration

ML pipeline orchestration nie je iba spustenie niekoľkých Python skriptov v správnom poradí. Je to systém, ktorý pre presne identifikovaný pipeline definition a vstupy vytvorí konkrétny run, koordinuje task attempts, prenáša parametre a artifacts, uplatňuje retries, cache a failure policy a nakoniec poskytne dôkaz, čo sa skutočne vykonalo. Orchestrátor nevlastní pravdivosť datasetu ani kvalitu modelu; vlastní prechod medzi deklarovaným workflowom a pozorovateľnou execution history.

Pre DevOps a platform rolu je zásadné odlíšiť päť rôznych subjectov: source definíciu pipeline, compiled intermediate representation, pipeline run, jednotlivý task attempt a výsledný artifact. Zelený run môže obsahovať cache hits zo staršej generácie. Neúspešný task môže mať úspešný retry, ktorý znovu vykoná externý side effect. Rovnaký source commit môže vytvoriť odlišný compiled graph, ak sa zmení SDK, base image alebo component resolution.

Atlas Payments pokračuje incidentom `MLOPS-PAY-92`. Tím zmenil feature transformáciu a spustil training pipeline. Orchestrátor označil run ako úspešný, pretože preprocessing task použil cache a training task dokončil. Cache key však nezahŕňal image digest ani semantic version transformácie. Pipeline preto spojila nový training code so starým transformed datasetom. Následný promotion task po timeout-e zopakoval Registry mutation a prepísal alias na iný model version, než ktorý bol uvedený v pôvodnom run summary.

## 1. Dominantný orchestration lifecycle

Pipeline začína deklarovaným contractom, nie kliknutím na tlačidlo Run. Contract určuje vstupy, component interfaces, control dependencies, artifact flow, execution environment a side-effect policy. Compiler z neho vytvorí platform-specific IR. Backend až následne vytvorí run a task attempts.

```text
pipeline source + component definitions
→ resolved dependencies a container digests
→ compiled IR
→ submitted run + immutable parameters
→ scheduled task attempts
→ parameter a artifact handoff
→ cache/retry/condition decisions
→ output artifacts a metadata
→ run verdict
→ downstream promotion alebo explicitné zastavenie
```

Každá šípka má inú authority. Git je authority pre reviewed source. Compiled IR je authority pre graph, ktorý bol odovzdaný backendu. Backend metadata je authority pre vytvorené attempts a ich status. Artifact store je authority pre bytes. Registry alebo deployment system je authority pre neskorší side effect. UI summary nie je univerzálna authority pre všetky vrstvy.

## 2. Exact pipeline subject

Tvrdenie „spustili sme pipeline v4“ je nedostatočné. Exact subject potrebuje source commit, compiler a SDK generation, compiled IR digest, component image digests, parameter values, dataset a feature identities, run ID, service account, cache policy a side-effect ownership.

```yaml
pipeline_subject: MLOPS-PAY-TRAIN-2026-08-03-r17
source_commit: 36042cccbf9c0786e833955c090d848993117754
pipeline_entrypoint: pipelines/risk_training.py
sdk: kfp==2.15.0
compiler_image: registry.example/ml/kfp-compiler@sha256:2d1a...90ef
compiled_ir_digest: sha256:672a...a103
pipeline_root: s3://ml-pipelines/risk/r17/
parameters:
  dataset_manifest: sha256:39bd...ee02
  feature_service: risk_v7
  training_image: registry.example/ml/train@sha256:8aac...f701
  seed: 3719
run_id: 8fc5a55d-8d9b-4a59-a64d-47df8bc76bb8
service_account: ml-pipeline-risk
cache_policy: explicit-per-task-v2
promotion_mode: approval-required
```

Manifest oddeľuje reusable definition od jednej execution. Ak run používa mutable tag, neurčitý dataset path alebo default service account, subject nie je uzavretý. Taký run môže byť užitočný pre exploration, ale nesmie byť promotion authority.

## 3. Pipeline, component, task a attempt

Pipeline je logický graph. Component je reusable interface s deklarovanými inputs, outputs a implementation. Task je použitie componentu v konkrétnom graph-e. Attempt je jedno runtime vykonanie tasku. Retry preto nevytvára nový logický task, ale nový attempt s vlastným start time, Pod identity, logs a outcome.

Toto rozlíšenie je dôležité pri diagnostike. Keď task `publish_model` skončí ako successful po retry, treba vedieť, či prvý attempt nevykonal Registry mutation a iba stratil response. Druhý attempt môže vytvoriť duplicate version alebo posunúť alias druhýkrát. Task-level success bez attempt-level reconciliation zakryje unknown outcome.

```text
pipeline run R17
└── task publish_model
    ├── attempt 1: timeout po request-e, outcome unknown
    └── attempt 2: success, ale side effect môže byť duplicate
```

Orchestrátor musí preto rozlišovať pure computation od external mutation. Transformácia datasetu môže byť bezpečne opakovaná, ak output path je content-addressed. Promotion, ticket creation alebo notification potrebuje operation ID, conditional write alebo read-before-retry.

## 4. Control flow a data flow

Control dependency hovorí, že task B sa môže začať až po určitom stave tasku A. Data dependency hovorí, že B spotrebuje presný output A. Tieto väzby sa často prekrývajú, ale nie sú totožné. Task môže čakať na validation verdict ako parameter, zatiaľ čo dataset artifact číta z immutable URI. Iný task môže byť control successor bez spotreby artifactu.

Silný pipeline contract prenáša malé hodnoty ako typed parameters a veľké dáta ako versionované artifacts. Prenášanie path stringu bez manifestu vytvára hidden dependency: downstream task nevie, či path stále ukazuje na rovnaký obsah. Prenášanie celého datasetu cez metadata backend zase vytvára nevhodnú coupling a kapacitný problém.

```python
from kfp import dsl
from kfp.dsl import Dataset, Input, Model, Output

@dsl.component(base_image="python:3.12-slim@sha256:...")
def train(
    dataset: Input[Dataset],
    model: Output[Model],
    seed: int,
) -> str:
    # Component zapisuje model bytes do model.path a vracia malý run summary.
    ...
```

Component interface musí uvádzať semantics, nie iba typ. `Dataset` bez observation unit, event-time boundary, schema a label maturity zostáva príliš neurčitý. Type system orchestrátora pomáha s handoffom, ale nenahrádza domain contract.

## 5. Compilation a resolved graph

Source pipeline je často dynamický Python program. Compiler ho prevedie na IR YAML alebo iný deklaratívny graph, ktorý backend dokáže interpretovať. Authoritative review preto musí zahŕňať aj compiled output. Zmena SDK môže zmeniť generated task names, executor spec, default caching alebo serialization bez zmeny business logiky.

```bash
python -m pipelines.compile \
  --output dist/risk-training.yaml
sha256sum dist/risk-training.yaml
```

CI má porovnať generated IR s očakávaným diffom a zakázať mutable component images. Server-side acceptance následne overí, či backend prijal práve tento IR digest. Source review bez resolved graphu je podobný Helm reviewu bez renderu: neukazuje presný objekt, ktorý control plane spracuje.

## 6. Caching nie je iba optimalizácia

Kubeflow Pipelines môže reuse-nuť output component execution, keď vyhodnotí rovnaké inputs a parameters a output je stále dostupný. Cache zrýchľuje runs, ale zároveň mení execution semantics: task nemusí vôbec spustiť nový container. Preto cache hit nie je nový computation proof.

Cache key musí reprezentovať všetko, čo mení output. Ak component používa container image tag `latest`, neversionovaný SQL view, environment variable alebo external API, deklarované inputs nie sú úplné. KFP môže oprávnene považovať task za rovnaký, hoci hidden dependency sa zmenila.

```python
transform_task = transform(
    dataset=validated.output,
    transform_version="risk-transform-v7",
)
transform_task.set_caching_options(enable_caching=True)

publish_task = publish_model(model=train_task.outputs["model"])
publish_task.set_caching_options(enable_caching=False)
```

Caching patrí iba na deterministic tasky s complete input closure a durable outputs. Validation task závislý od current policy alebo external blacklistu môže potrebovať cache vypnúť alebo policy generation pridať ako explicitný input. Side-effect task sa z cache nesmie javiť ako potvrdenie, že side effect stále existuje.

## 7. Retries, timeouts a idempotency

Retry policy musí vychádzať z failure semantics. Process exit pred vytvorením outputu je iný prípad než timeout po odoslaní requestu do Registry. Pri prvom je opakovanie typicky bezpečné. Pri druhom je outcome unknown a retry bez read-backu môže vytvoriť duplicitný alebo protichodný stav.

```yaml
operation_id: MLOPS-PAY-92-PROMOTE-R17
expected_registry_alias_generation: 41
requested_target_model_version: 128
```

Promotion endpoint má vykonať conditional mutation iba vtedy, keď alias stále ukazuje na očakávanú generation. Po timeout-e task najprv načíta alias history a model version tags. Ak operation ID už existuje, vráti pôvodný výsledok. Ak stav konfliktuje, task skončí ako blocked, nie ako automatický retry.

Timeout zároveň neurčuje, že computation zlyhal. Training Pod môže pokračovať po strate klientského spojenia. Orchestrátor musí korelovať task attempt s workload UID a neskôr prečítať jeho finálny stav. Blind resubmission môže spustiť druhý drahý training run.

## 8. Conditions, loops a exit handling

Conditional branch je policy boundary. `if metric > threshold` nestačí, pokiaľ metric nemá dataset, evaluator, confidence a guardrail identity. Branch decision sa musí uložiť ako artifact alebo metadata record, aby bolo možné vysvetliť, prečo promotion path vznikol.

Loops vytvárajú viac task subjects, napríklad jednu evaluation pre každý segment. Každá iteration potrebuje stabilný key. Index `0`, `1`, `2` nie je stabilný, ak sa zmení ordering segmentov. Použitie `segment_id` umožní koreláciu a selective retry.

Exit handler sa vykoná aj pri upstream failure, ale nie je magická transakcia. Môže uvoľniť lease, označiť run ako aborted a odoslať notifikáciu. Nemôže automaticky vrátiť externý systém do pôvodného stavu, ak task už vykonal nezvratný side effect. Compensation musí byť explicitná a idempotentná.

## 9. Scheduling, resources a isolation

Orchestrátor odovzdáva tasky scheduleru, ale resource request nie je garancia výkonu. CPU, memory, GPU, node selector, topology a priority ovplyvňujú queueing a placement. Run status `Pending` môže znamenať nedostatok GPU, nesplniteľnú affinity, quota alebo image pull failure. Orchestration diagnosis preto pokračuje do Kubernetes Events a workload statusu.

Service account a namespace určujú access boundary. Preprocessing task potrebuje read dataset a write transformed artifact. Promotion task potrebuje Registry mutation, ale nemá automaticky dostať production deployment credentials. Rozdelenie taskov umožňuje least privilege a oddelené approval gates.

## 10. Backfill, recurring runs a parameter time

Recurring run nevytvára automaticky správny historical backfill. Pipeline musí rozlišovať scheduling time, logical data interval a event-time cutoff. Ak daily run o polnoci spracúva predchádzajúci deň, parameter musí explicitne niesť interval. Použitie `now()` vo vnútri componentu znemožňuje reprodukciu.

```yaml
logical_interval:
  start: 2026-08-02T00:00:00Z
  end_exclusive: 2026-08-03T00:00:00Z
label_cutoff: 2026-09-02T00:00:00Z
```

Backfill nad intervalmi má stabilné operation IDs a output locations. Druhé spustenie rovnakého intervalu buď vytvorí rovnaký content digest, alebo explicitne novú correction generation. Nemá potichu prepísať pôvodný snapshot.

## 11. Evidence hierarchy

Configured evidence je source pipeline. Resolved evidence je compiled IR a pinned component graph. Loaded evidence je backend run spec a vytvorené workload UIDs. Exercised evidence sú task attempts, logs, output manifests a cache decisions. Outcome evidence je validný model candidate alebo iný downstream artifact a až neskôr production business result.

```bash
# Source a compiled subject
git rev-parse HEAD
sha256sum dist/risk-training.yaml

# Run a task execution
kfp run get --run-id "$RUN_ID"
kubectl get pods -n ml-runs -l pipelines.kubeflow.org/runid="$RUN_ID" -o wide

# Artifact read-back z fresh identity
aws s3api head-object --bucket ml-pipelines --key "$ARTIFACT_KEY"
```

Žiadny jeden command nepreukazuje celý chain. KFP UI môže potvrdiť task status a artifact metadata, ale object-store checksum sa číta z artifact authority. Kubernetes Pod status potvrdí container execution, nie model quality.

## 12. Competing failure hypotheses

Pri zlom pipeline outcome sa najprv hľadá first divergence. Definition hypothesis predpokladá chybný source alebo parameter. Compilation hypothesis predpokladá, že resolved graph nezodpovedá source intentu. Scheduling hypothesis predpokladá, že intended task sa nespustil v správnom environment-e. Cache hypothesis predpokladá reuse starého outputu. Artifact hypothesis predpokladá chýbajúce alebo poškodené bytes. Side-effect hypothesis predpokladá unknown alebo duplicate external mutation.

Každá hypotéza má odlišný dôkaz. Source a IR diff falsifikuje compilation problém. Task metadata a cache indicator ukážu reuse. Pod UID, image ID a env snapshot overia loaded generation. Manifest a checksum overia artifact. Registry audit history a operation ID rozhodnú o side effectu. Retraining pred týmto rozlíšením iba vytvorí ďalšiu generáciu a zhorší atribúciu.

## 13. Recovery model

Containment zastaví promotion a ďalšie recurring runs, ale zachová run metadata, Pods, logs a artifacts. Recovery potom vytvorí corrected pipeline generation s úplnými cache inputs, conditional Registry write a immutable outputs. Starý run sa nemení; zostáva evidence.

Component recovery dokazuje, že opravený task vytvorí správny output. Journey recovery spustí pipeline od immutable datasetu po candidate package a overí každý handoff. Business recovery príde až po samostatnom model delivery a produkčnom outcome-e. Orchestrator green je iba stredná vrstva.

Second-operation test znovu spustí rovnaký logical interval. Deterministic tasks majú potvrdený cache hit alebo rovnaký digest. Side-effect task vykoná no-op cez operation ID. Forbidden test overí, že mutable tag, neversionovaný dataset a broad production credential sú odmietnuté.

## 14. Anti-patterny

Pipeline, ktorá iba volá jeden monolitický training script, skrýva data, validation, training a publication boundaries. Naopak, extrémne jemný graph vytvára vysokú orchestration overhead a krehké handoffs. Granularita má sledovať ownership, retry, caching a evidence boundaries.

Ďalším anti-patternom je považovať run success za release approval. Orchestrátor môže potvrdiť execution, no promotion gate potrebuje evaluation, lineage, package a policy evidence. Rovnako nebezpečný je cache enabled by default bez complete dependency modelu; zrýchlenie potom zakrýva stale computation.

## 15. Praktický acceptance contract

Pozitívny test vytvorí run z pinned IR, datasetu a images, overí task attempts, manifests a candidate identity. Forbidden test odmietne mutable inputs, cache na side-effect tasku a promotion bez approval. Recovery test simuluje timeout po Registry request-e a potvrdí read-before-retry. Adjacent test spustí inú dataset generation bez cross-run cache collision.

Acceptance sa uzavrie až vtedy, keď druhé spustenie rovnakého subjectu neprodukuje duplicate side effect, každý output má traversable lineage a compiled graph sa dá reprodukovať z repository inputs. To je orchestration correctness; model correctness a production value zostávajú ďalšie dôkazné vrstvy.

## Primárne zdroje

- [Kubeflow Pipelines — Pipeline concepts](https://www.kubeflow.org/docs/components/pipelines/concepts/pipeline/)
- [Kubeflow Pipelines — Caching](https://www.kubeflow.org/docs/components/pipelines/user-guides/core-functions/caching/)
- [Kubeflow Pipelines — ML Metadata](https://www.kubeflow.org/docs/components/pipelines/concepts/metadata/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Feature stores a online/offline consistency](feature-stores-online-offline-consistency.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Training pipelines a distributed training →](training-pipelines-distributed-training.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
