# Amazon SageMaker a cloud MLOps mapping

Amazon SageMaker AI poskytuje managed služby pre experiments, pipelines, training, registry, deployment, monitoring a MLOps automation. Managed však neznamená automaticky authoritative. Každá AWS resource musí byť namapovaná na rovnaké subjects, evidence a acceptance boundaries ako platform-neutral MLOps model: exact data/code/environment/model generation, control-plane mutation, data-plane read-back a business outcome.

V incidente `MLOPS-PAY-97` tím mapoval KFP run priamo na SageMaker Pipeline execution a KServe `InferenceService` na SageMaker Endpoint. Pipeline execution uspela, Model Package dostal `Approved` a endpoint update skončil `InService`. Napriek tomu processing step čítal mutable S3 prefix, training image používal tag, production variant načítal starší Model Package a Model Monitor baseline vznikol z inej feature generation. Dashboard označil cloud migration za úspešnú, hoci neexistoval jednotný release manifest ani parity evidence medzi Kubernetes a AWS implementations.

## 1. Mapping, nie premenovanie

Cloud mapping musí zachovať semantics, nie iba nájsť podobne pomenovaný produkt.

| Platform-neutral subject | SageMaker AI a AWS mapping |
|---|---|
| experiment/run | SageMaker Experiments trial/run metadata |
| pipeline definition/run | SageMaker Pipelines definition a execution |
| training operation | SageMaker Training Job |
| model candidate/version | Model Package v Model Package Group |
| approval control | Model Approval Status a vlastná governance evidence |
| immutable artifacts | S3 object versions/digests, ECR image digest |
| online deployment | Model, Endpoint Configuration, Endpoint/Production Variant |
| batch inference | Batch Transform alebo pipeline processing path |
| monitoring | Model Monitor schedules/results, CloudWatch metrics/logs |
| lineage | SageMaker Lineage a vlastný release manifest |
| CI/CD template | SageMaker Projects plus CodePipeline/CodeBuild alebo vlastný GitOps flow |

Žiadna bunka nie je úplná sama osebe. Napríklad Model Package môže evidovať model artifact, ale serving behavior závisí aj od inference image, environment, endpoint config, instance type, feature path a routing.

## 2. Account, Region a identity boundary

AWS account a Region sú súčasť subjectu. Rovnaký resource name v inom account-e alebo Region-e je iný object a môže mať inú KMS key, VPC, IAM policy a artifact copy. ARN sa používa ako control-plane identity, no immutable artifact identity potrebuje aj S3 version/digest a ECR image digest.

Execution role sa navrhuje per workload alebo per capability. Training read, model registry write, endpoint update a monitoring read nie sú jedna široká role. Cross-account promotion používa explicitné resource policies, artifact replication a KMS grants; `sts:AssumeRole` success nie je dôkaz, že target načítal správne bytes.

## 3. SageMaker Pipelines

SageMaker Pipelines automatizujú model-building workflow od processing/training po evaluation a registration. Pipeline definition a execution sú rozdielne subjects. Definition JSON, SDK lock, parameters a referenced images/scripts sa versionujú.

```python
from sagemaker.workflow.pipeline import Pipeline

pipeline = Pipeline(
    name="fraud-training",
    parameters=[
        data_snapshot_param,
        model_approval_status_param,
    ],
    steps=[
        preprocess_step,
        train_step,
        evaluate_step,
        condition_step,
    ],
    sagemaker_session=pipeline_session,
)

definition = pipeline.definition()
```

Definition sa uloží a hashne v CI. Step cache sa používa iba pri complete dependency subjecte. Processing input `s3://bucket/data/latest/` alebo image tag `:latest` ruší reprodukovateľnosť, aj keď Pipeline execution ARN zostáva evidovaný.

Execution status `Succeeded` znamená úspešné orchestration steps, nie automaticky valid model. Evaluation output, condition decision, Model Package ARN a external side effects sa čítajú samostatne.

## 4. Training Jobs

Training Job subject zahŕňa algorithm/inference image digest, source bundle, hyperparameters, input channels, instance type/count, distribution config, networking, checkpoint path a output S3 location. Job name bez Describe response snapshotu nestačí.

Managed training vytvára ephemeral infrastructure, ale framework stále zodpovedá za data sharding, checkpoint completeness a metric correctness. Spot interruption alebo warm pool môžu zmeniť attempt lifecycle. Resume path sa testuje a viaže na committed checkpoint.

`Completed` training job nepreukazuje, že `model.tar.gz` je správny alebo bezpečne načítateľný. Pipeline overí output artifact digest, package load a evaluation.

## 5. Experiments a lineage

SageMaker Experiments a Lineage môžu spájať runs, artifacts a actions. Sú užitočné pre traceability, ale nenahrádzajú immutable release manifest. Metadata môže byť neúplná, late alebo mutable tags môžu meniť interpretáciu.

Platforma loguje source commit, dataset S3 version/digest, image digest, Pipeline execution ARN, Training Job ARN, Model Package ARN/version a evaluation verdict. Lineage query sa porovná s actual deployed Endpoint Configuration.

## 6. Model Registry

Model Registry organizuje Model Package Groups a ich versions. Model Package môže niesť metrics, lineage, model card metadata a approval status. `Approved` je control-plane property, nie loaded-runtime evidence.

```text
Model Package Group
→ Model Package version
→ approval a metadata
→ deployable Model/Endpoint Configuration
→ Endpoint update
→ production variant loaded state
```

Promotion policy kontroluje exact Model Package ARN, model data URL/version, inference image digest a evaluation evidence. Cross-account copy alebo share vytvára nový authority context; source approval sa nesmie ticho dediť bez target verification.

## 7. Model, Endpoint Configuration a Endpoint

SageMaker hosting oddeľuje `Model`, immutable-style `EndpointConfig` a mutable `Endpoint`, ktorý môže byť aktualizovaný na novú konfiguráciu. Produkčný release subject viaže všetky tri a actual production variants.

Endpoint status `InService` nepreukazuje model-level readiness ani business correctness. Po update sa vykoná describe/read-back, overia sa variant weights a instance counts, potom synthetic request s response release identity. CloudWatch metrics a data capture potvrdia actual exposure.

Blue/green alebo canary mechanizmus má vlastné guardrails a rollback. Configured variant weight nie je actual outcome denominator. Client retries, shadow tests a async/batch modes sa oddeľujú.

## 8. Batch a asynchronous paths

Batch Transform, asynchronous inference a real-time endpoint majú odlišný operation subject. Batch viaže input manifest, interval, output prefix a idempotency. Async path viaže queue/object request a completion notification. Real-time viaže request deadline a routing variant.

Rovnaký Model Package môže mať odlišné preprocessing, timeout a result semantics. Cross-mode parity sa testuje nad spoločným golden datasetom, nie predpokladá z model identity.

## 9. Model Monitor

Model Monitor môže sledovať data quality, model quality, bias drift a feature attribution drift podľa user-defined baselines a thresholds. Monitoring schedule success neznamená, že population je complete alebo labels mature.

Baseline subject zahŕňa dataset snapshot, feature generation, schema/statistics constraints a evaluation time. Monitoring output v S3 sa viaže na Endpoint/variant/release a event-time interval. Alert je hypothesis evidence; retraining alebo rollback vyžaduje competing-hypothesis analysis.

Model-quality monitoring s ground truthom musí riešiť label delay, joins a coverage. Data capture disabled alebo sampled requesty vytvárajú monitoring blind spot, ktorý má vlastný alert.

## 10. Projects a CI/CD

SageMaker Projects poskytujú templates pre MLOps automation a môžu vytvoriť CodePipeline, CodeBuild a repositories. Template je bootstrap a governance surface, nie automatický proof bezpečného CI/CD.

Generated roles, buckets, encryption, branch controls, build images a artifact policies sa auditujú. Template version sa pinne; upgrade je platform change. Organization môže namiesto Projects používať existujúci GitHub/GitLab a deployment controller, ak zachová equivalent evidence.

## 11. Storage, encryption a network

S3 artifact buckets používajú versioning, lifecycle, encryption a deny policies proti nešifrovanému alebo neautorizovanému write. ECR images sa referencujú digestom. KMS key policy a grants sú súčasť access pathu. VPC-only training/hosting mení network dependencies pre S3, ECR, STS, CloudWatch a external features.

Network isolation môže znížiť egress risk, ale môže tiež zablokovať required dependencies. Success control plane call neznamená, že workload mal data-plane connectivity. Logs a VPC endpoint metrics sa zahrnú do diagnosis.

## 12. Observability a cost

CloudWatch metrics/logs, EventBridge events, CloudTrail a SageMaker resource descriptions poskytujú rôzne evidence. CloudTrail ukáže API mutation, nie model bytes loaded. Endpoint invocation metrics ukážu service behavior, nie mature business outcome. Data capture môže podporiť monitoring, ale nesmie porušiť privacy policy.

Cost sa mapuje podľa training jobs, processing, endpoints, storage a monitoring. Allocated cloud spend sa delí useful training stepmi, deadline-successful inference a mature outcomes, nie iba počtom API calls. Idle endpoint a failed pipeline retries majú byť viditeľné.

## 13. Kubernetes a SageMaker hybrid mapping

AWS dokumentácia podporuje SageMaker Operators for Kubernetes a SageMaker components pre Kubeflow Pipelines. Hybrid orchestration vytvára dve control planes: Kubernetes/KFP a SageMaker. KFP task success môže znamenať iba úspešné vytvorenie SageMaker jobu, nie jeho terminal a output acceptance, ak connector contract nie je správne nastavený.

Každý external job používa ARN ako read-back key. Retry po timeout-e najprv vykoná Describe/ListTags a porovná client token/subject. Artifacts sa prenášajú cez explicitný S3 contract a KFP metadata eviduje ARN aj output digest.

## 14. Failure hypotheses

Pipeline `Succeeded` s nesprávnym modelom môže byť mutable S3 input, stale step cache, wrong execution parameters alebo condition logic. Model Package `Approved`, ale endpoint starý, môže byť failed deployment pipeline, wrong account/Region, stale EndpointConfig alebo partial variant update. Model Monitor alert môže byť data drift, capture gap, baseline mismatch alebo feature pipeline change.

Troubleshooting začína account, Region, ARNs a release manifestom. Porovná sa Pipeline execution, Training Job, S3 object versions, Model Package, EndpointConfig, variants, CloudWatch a actual inference response. Console screenshot bez exact identifiers je slabé evidence.

## 15. Recovery a acceptance

Containment zastaví pipeline triggers alebo endpoint rollout, zachová CloudTrail/CloudWatch a zmrazí mutable S3 prefixes. Recovery vytvorí nový deployment z known-good Model Package, image digest a EndpointConfig, vykoná update, read-back, synthetic test a bounded traffic verification. Monitoring baseline sa obnoví iba vtedy, ak bol chybný; nemá sa prepisovať tak, aby incident zmizol.

Pozitívna acceptance vyžaduje immutable S3/ECR inputs, exact Pipeline/Training/Model Package/Endpoint identities, approval evidence, loaded data-plane test, monitoring coverage a business outcome. Forbidden acceptance je `Succeeded`, `Approved` alebo `InService` bez artifact a runtime read-back.

Second-operation test znovu spustí rovnaký immutable pipeline subject alebo no-op deploy. Step cache musí byť vysvetliteľná, duplicate Model Packages a endpoint mutations sa nesmú vytvoriť pri unknown-outcome retry a cloud mapping musí zachovať rovnaké lineage a acceptance semantics ako Kubernetes implementation.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: KServe alebo ekvivalentný Kubernetes model serving](kserve-kubernetes-model-serving.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
