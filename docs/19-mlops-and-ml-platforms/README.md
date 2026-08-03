# MLOps and ML Platforms

Sekcia sleduje ML systém ako lifecycle dát, kódu, environmentu, experimentu, modelu, feature pipeline, deploymentu a produkčného feedbacku. Každý promotion alebo rollback musí byť viazaný na presný model artifact, dataset a feature generation, serving runtime, evaluation evidence a business acceptance.

## Predpoklady

Odporúčané predchádzajúce oblasti:

- Machine Learning Fundamentals
- CI/CD and Release Engineering
- Kubernetes
- Observability
- GitOps and Platform Engineering

## Authoritative poradie — aktívne kapitoly

1. [ML lifecycle a rozdiel medzi DevOps a MLOps](ml-lifecycle-devops-vs-mlops.md)
2. [Data, code, environment a model lineage](data-code-environment-model-lineage.md)
3. [Dataset versioning](dataset-versioning.md)
4. [Experiment tracking](experiment-tracking.md)
5. [Artifact stores](artifact-stores.md)
6. [Model packaging a reproducible environments](model-packaging-reproducible-environments.md)
7. [Model Registry, versions, stages a aliases](model-registry-versions-stages-aliases.md)
8. [Feature stores a online/offline consistency](feature-stores-online-offline-consistency.md)
9. [ML pipeline orchestration](ml-pipeline-orchestration.md)
10. [Training pipelines a distributed training](training-pipelines-distributed-training.md)
11. [CI pre ML code, data a pipelines](ci-for-ml-code-data-pipelines.md)
12. [Continuous Delivery pre modely](continuous-delivery-for-models.md)
13. [Continuous Training a retraining triggers](continuous-training-retraining-triggers.md)
14. [Model validation a promotion gates](model-validation-promotion-gates.md)
15. [Batch, online a streaming inference](batch-online-streaming-inference.md)
16. [Shadow, canary a A/B model deployment](shadow-canary-ab-model-deployment.md)
17. [Model serving a autoscaling](model-serving-autoscaling.md)
18. [GPU scheduling, utilization a capacity](gpu-scheduling-utilization-capacity.md)
19. [Model monitoring](model-monitoring.md)
20. [Data drift, concept drift a prediction drift](data-drift-concept-drift-prediction-drift.md)
21. [Performance, latency, throughput a cost monitoring](performance-latency-throughput-cost-monitoring.md)
22. [Feedback loops a ground-truth delay](feedback-loops-ground-truth-delay.md)
23. [Model rollback a recovery](model-rollback-recovery.md)
24. [Governance, approvals a audit](governance-approvals-audit.md)
25. [Privacy, security a adversarial ML](privacy-security-adversarial-ml.md)
26. [ML supply-chain security](ml-supply-chain-security.md)
27. [MLflow experiment tracking a Model Registry](mlflow-experiment-tracking-model-registry.md)
28. [MLflow evaluation, tracing a deployment](mlflow-evaluation-tracing-deployment.md)

## Plánované authoritative poradie

Nasledujúci inventory je schválený plán sekcie. Položka sa zmení na aktívny Markdown link až v pracovnom bloku, ktorý vytvorí a validuje príslušnú kapitolu. Tým sa plánovaný obsah nezamieňa za hotovú dokumentáciu.

29. Kubeflow Pipelines
30. Kubeflow Trainer a distributed training
31. KServe alebo ekvivalentný Kubernetes model serving
32. Amazon SageMaker a cloud MLOps mapping
33. MLOps platform architecture
34. MLOps troubleshooting

## Authoring a evidence štandard

Každá kapitola používa rovnaký prose-first štandard ako predchádzajúce sekcie:

```text
business alebo user outcome
→ exact data/model/prompt/agent subject a generation
→ authority, trust a ownership boundary
→ internal lifecycle alebo mutation path
→ authoritative read-back a proof boundary
→ failure a competing hypotheses
→ containment a recovery
→ positive, forbidden a second-operation acceptance
```

Rýchlo sa meniace produkty, API a protokoly sa pri každom bloku znovu overujú proti aktuálnym primárnym zdrojom. Dokumentácia nesmie zamieňať offline eval, control-plane status alebo úspešný tool call za produkčný business outcome.

## Praktická vrstva

Nosný end-to-end smer sekcie:

```text
Git + dataset version → pipeline validation → train a evaluate → MLflow tracking → registry promotion → containerized serving → canary deployment → monitoring a drift signal → controlled retraining
```

Samostatné laby a troubleshooting drilly sa aktivujú až po dostatočnom koncepčnom základe. Dokumentačný workflow môže overiť súbory, príkazy a konzistenciu modelu, ale nepreukazuje vykonanie tréningu, inference, agentického side effectu ani produkčného outcome-u.

## Stav

Aktuálny authoritative stav sekcie je **28/34 · In progress**. Siedmy blok uzatvára security-to-MLflow implementation chain. Privacy/security kapitola viaže threat actor, lifecycle capability, data minimization, membership/inversion/extraction risk, evasion, poisoning/backdoor, serialization, endpoint abuse, privacy-safe telemetry a red-team/recovery evidence; supply-chain kapitola vytvára trust graph od source a datasetu cez locked dependencies, trusted builder, SLSA provenance, SBOM/model/data manifests a Sigstore attestations až po admission a runtime loaded fingerprint; MLflow tracking/Registry kapitola implementuje database/artifact-store architecture, secure pinned environment, dataset inputs, runs, Logged Models, version/tag/alias read-back, environment separation, smoke serving a restore; evaluation/tracing/deployment kapitola oddeľuje classic ML evaluation a `MetricThreshold` validation od GenAI `Scorer`/trace evaluation a od production target authority. Incident `MLOPS-PAY-96` spája adaptívne endpoint probing, untrusted feedback, mutable build inputs, neúplnú image/model provenance, alias-driven mixed runtime a zlúčenie nekompatibilných MLflow quality surfaces do jedného `quality_passed` verdictu. Ďalší authoritative blok sú kapitoly 29–32: Kubeflow Pipelines, Kubeflow Trainer, KServe a Amazon SageMaker cloud mapping. Sekcia nie je runtime `Verified`, production `Stable` ani user `Accepted`.
