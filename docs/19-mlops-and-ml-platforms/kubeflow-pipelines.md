# Kubeflow Pipelines

Kubeflow Pipelines nie je iba grafická obrazovka nad sériou Kubernetes Podov. Je to compiler a orchestration control plane, ktorý z Python DSL vytvorí prenosný pipeline contract, odošle ho backendu a následne eviduje runs, task executions, parameters, artifacts a metadata. Produkčná hodnota nevzniká tým, že pipeline skončí ako `Succeeded`, ale tým, že presne identifikovaný graph spracuje presne identifikované vstupy, vytvorí overiteľné outputs a nespôsobí skryté alebo duplicitné side effects.

V incidente `MLOPS-PAY-97` tím prekompiloval fraud-training pipeline po zmene component image, ale zachoval rovnaký human-readable pipeline name. KFP cache znovu použila preprocessing output, pretože declared inputs a parameters sa nezmenili, hoci image obsahoval novú normalizáciu a external lookup table sa medzitým prepísala. Training task vytvoril model, Registry step po timeout-e zopakoval mutation a serving pipeline následne načítala dve rozdielne model versions. UI ukázalo zelený run, ale neexistoval jednotný immutable subject od source graphu cez compiled IR až po artifact a external mutation.

## 1. Presný pipeline subject

Pipeline subject musí oddeľovať authoring source, compiled representation, runtime parameters, component implementations a external generations. Rovnaký Python function name alebo rovnaký pipeline display name nie je dostatočná identity.

```yaml
pipeline_subject:
  source_commit: 8c1e4c7
  sdk_lock_digest: sha256:kfp-lock...
  compiled_ir_digest: sha256:pipeline-ir...
  pipeline_root: s3://ml-platform/pipelines/fraud/2026-08-03/
  parameters:
    data_snapshot: fraud-events-2026-07-31
    feature_generation: fraud-features-v14
  components:
    preprocess_image: registry.example/preprocess@sha256:...
    train_image: registry.example/train@sha256:...
    evaluate_image: registry.example/evaluate@sha256:...
  external_policies:
    promotion_policy: fraud-promotion-v9
    registry_target: fraud-prod
```

Source commit vysvetľuje authoring intent. Compiled IR digest vysvetľuje graph, interfaces a execution configuration, ktorú backend skutočne prijal. Component image digest viaže executable implementation. Pipeline root určuje authority pre artifacts. External policy generation viaže mutations, ktoré nie sú čistou funkciou component inputs.

## 2. DSL, component a pipeline graph

KFP Python SDK používa components ako opakovateľné execution units a pipelines ako kompozíciu týchto units do DAG-u. Component interface musí explicitne rozlišovať malé parameters od veľkých artifacts. Parameter je hodnota prenášaná cez execution metadata; artifact je objekt s URI, typom a metadata, ktorého bytes žijú v object store alebo inom artifact backend-e.

```python
from kfp import dsl

@dsl.component(
    base_image="python:3.12-slim",
    packages_to_install=["pandas==2.3.1"],
)
def validate_dataset(
    source_uri: str,
    expected_schema_digest: str,
    report: dsl.Output[dsl.Artifact],
):
    from pathlib import Path
    import json

    result = {
        "source_uri": source_uri,
        "schema_digest": expected_schema_digest,
        "status": "validated",
    }
    Path(report.path).write_text(json.dumps(result), encoding="utf-8")

@dsl.pipeline(name="fraud-training")
def fraud_training(
    source_uri: str,
    schema_digest: str,
):
    validation = validate_dataset(
        source_uri=source_uri,
        expected_schema_digest=schema_digest,
    )
    validation.set_caching_options(enable_caching=False)
```

Lightweight component môže byť vhodný pre malý deterministic helper. Produkčný component s native libraries, custom certificates, GPU runtime alebo supply-chain requirements sa spravidla balí do vlastného image. `packages_to_install` je pohodlné authoring rozhranie, nie náhrada za reproducible production image.

## 3. Compile boundary a IR YAML

KFP compiler vytvára IR YAML, serialized `PipelineSpec`. IR je authoritative handoff medzi authoring environmentom a backendom. Compile success overí syntax, graph a static type compatibility, ale neoverí, že image existuje, service account má prístup, artifact store je dostupný alebo component produkuje business-correct output.

```python
from kfp import compiler

compiler.Compiler().compile(
    pipeline_func=fraud_training,
    package_path="fraud-training.yaml",
)
```

CI uloží IR YAML ako immutable artifact, vypočíta digest a vykoná semantic diff proti schválenému baseline-u. Review nesleduje iba textový Python diff. Zmena image digestu, resource requests, cache policy, retry policy, service accountu, pipeline rootu alebo component interface môže zmeniť runtime behavior aj pri malom source diff-e.

Aktuálny KFP podporuje aj Kubernetes Native API mode, v ktorom compiler môže vytvoriť `Pipeline` a `PipelineVersion` custom resources. Tento formát je iná deployment surface. Platforma musí pinovať, či používa portable IR submission alebo native Kubernetes manifests; ich object lifecycle, GitOps integrácia a backend compatibility sa nesmú miešať implicitne.

## 4. Run, task a attempt

Pipeline definition nie je pipeline run. Run viaže compiled subject, parameters, identity a časový interval. Task je logical node graphu. Attempt je konkrétne execution skúšanie po retry alebo reschedule. Jeden task môže mať viac attempts a iba jeden accepted output.

```text
pipeline source
→ compiled IR
→ submitted run
→ logical task
→ execution attempt
→ artifact alebo external side effect
→ metadata a acceptance
```

Retry-safe task potrebuje idempotency key odvodený od run/task subjectu. Ak task zapisuje do Registry, databázy alebo queue, orchestration retry nesmie automaticky vytvoriť druhý side effect. Pri timeout-e sa najprv číta authoritative external state a až potom sa rozhoduje o retry.

## 5. Caching semantics

KFP caching je štandardne zapnuté a môže znovu použiť outputs component execution pri rovnakých declared inputs a parameters, ak sú outputs stále dostupné. Cache hit neznamená, že business meaning zostal rovnaký. Hidden dependency, mutable container tag, external table bez versiony, current-time lookup alebo environment variable mimo subjectu robia cache key neúplným.

Bezpečný cacheable component je referenčne transparentný vzhľadom na deklarovaný subject:

```text
declared inputs + immutable implementation + pinned environment
→ deterministic output identity
```

Cache sa vypína pre tasky s external mutation, current-state query, nondeterminism alebo incomplete dependency declaration.

```python
register_task = register_model(...)
register_task.set_caching_options(enable_caching=False)
```

Platforma eviduje, či output vznikol novým execution alebo cache reuse. Acceptance zahŕňa otvorenie artifactu z fresh worker-a bez lokálnej cache a kontrolu jeho digestu, schema a lineage.

## 6. Pipeline root, artifacts a metadata

Pipeline root je namespace pre runtime artifacts. Object-store prefix bez retention, encryption, tenant isolation a cleanup policy nie je produkčný artifact contract. Artifact URI musí byť immutable alebo content-addressed; prepisovanie `latest/model.pkl` ničí reprodukovateľnosť.

ML Metadata eviduje executions, artifacts, contexts a events. Metadata však nie sú artifact bytes. Úspešný metadata record nepreukazuje, že object existuje, je čitateľný, kompletný alebo má očakávaný digest. Backup musí chrániť backend metadata aj object store a restore drill musí obnoviť väzbu medzi nimi.

## 7. Multi-user isolation a identity

KFP v multi-user prostredí musí viazať namespace/profile, service account, artifact credentials a backend authorization. UI visibility nie je security boundary. Component Pod nesmie zdediť široké credentials iba preto, že pipeline potrebuje jeden privileged step.

Každý task dostane najmenšiu potrebnú identity. Dataset read, image pull, Registry write a deployment mutation sú rozdielne capabilities. Secrets sa neposielajú ako pipeline parameters ani nelogujú do metadata. Workload identity alebo krátkodobé credentials sú preferované pred statickými keys.

## 8. Resources, retries a control flow

CPU, memory, GPU, node placement a timeout patria do compiled execution subjectu. Resource request ovplyvňuje scheduling aj výslednú performance. Retry policy sa nastavuje podľa failure class: transient network failure môže byť retryable, invalid schema alebo failed validation nie.

Conditional a loop control flow zvyšujú expressiveness, ale komplikujú acceptance. Každá branch musí mať explicitný output contract. Skipped task nie je successful validation. Dynamic iteration potrebuje bounded cardinality a deterministic item identity, inak sa incident nedá rekonštruovať.

## 9. Praktický submission a read-back

Pipeline sa submituje z CI alebo release controlleru s immutable IR a parameter manifestom. Human notebook submission môže byť povolené pre experiment, ale nie ako jediný production change path.

```python
from kfp.client import Client

client = Client(host="https://kfp.example.internal")
run = client.create_run_from_pipeline_package(
    pipeline_file="fraud-training.yaml",
    arguments={
        "source_uri": "s3://datasets/fraud/2026-07-31/",
        "schema_digest": "sha256:schema...",
    },
    run_name="fraud-training-2026-08-03.1",
    experiment_name="fraud-prod-candidates",
    enable_caching=True,
)

print(run.run_id)
```

Po submit-e sa číta run detail z backendu a kontroluje pipeline version/digest, parameters, namespace a identity. Po dokončení sa nečíta iba phase. Kontrolujú sa task attempts, cache states, output artifacts, digests, validation verdict a external mutations.

## 10. Failure hypotheses

Zelený run s nesprávnym modelom môže vzniknúť z cache key gapu, mutable inputu, wrong pipeline version, prepisovaného pipeline rootu, dataset interval chyby alebo silent fallbacku. Chýbajúci artifact môže byť object-store permission, upload failure, cleanup race alebo metadata-only success. Duplicate Registry version môže byť retry po unknown outcome.

Troubleshooting začína exact run ID a compiled digestom. Následne sa porovná graph, parameters, component images, attempts, cache evidence a external read-back. Re-run s novým IR alebo zmenenými inputs je nový subject, nie reprodukcia pôvodného incidentu.

## 11. Recovery a acceptance

Containment môže vypnúť recurring run, zablokovať promotion task, deaktivovať cache pre podozrivý component a zmraziť mutable external source. Recovery znovu zostaví pipeline z pinned source a dependencies, skompiluje IR, spustí ju nad immutable snapshotom a reconciliuje nejasné external side effects.

Pozitívna acceptance vyžaduje pinned IR digest, immutable component images, explicitné inputs, valid artifact reads, task/attempt evidence, cache provenance a read-back každej mutation. Recovery acceptance vyžaduje fresh-run parity, žiadny duplicate side effect a second-operation test. Forbidden acceptance je zelený graph v UI, samotný compile success, cache hit bez dependency proof alebo run phase bez overenia artifacts a business resultu.

Second-operation test opakovane submitne rovnaký immutable subject. Pure tasks môžu bezpečne použiť rovnaké cache outputs; mutation tasks musia byť no-op alebo deterministicky reconciled. Ak druhý run vytvorí nový model version, prepíše artifact alebo zmení verdict bez novej generation, pipeline nie je idempotentná ani reprodukovateľná.
