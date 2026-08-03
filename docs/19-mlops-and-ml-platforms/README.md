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

## Plánované authoritative poradie

Nasledujúci inventory je schválený plán sekcie. Položka sa zmení na aktívny Markdown link až v pracovnom bloku, ktorý vytvorí a validuje príslušnú kapitolu. Tým sa plánovaný obsah nezamieňa za hotovú dokumentáciu.

9. ML pipeline orchestration
10. Training pipelines a distributed training
11. CI pre ML code, data a pipelines
12. Continuous Delivery pre modely
13. Continuous Training a retraining triggers
14. Model validation a promotion gates
15. Batch, online a streaming inference
16. Shadow, canary a A/B model deployment
17. Model serving a autoscaling
18. GPU scheduling, utilization a capacity
19. Model monitoring
20. Data drift, concept drift a prediction drift
21. Performance, latency, throughput a cost monitoring
22. Feedback loops a ground-truth delay
23. Model rollback a recovery
24. Governance, approvals a audit
25. Privacy, security a adversarial ML
26. ML supply-chain security
27. MLflow experiment tracking a Model Registry
28. MLflow evaluation, tracing a deployment
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

Aktuálny authoritative stav sekcie je **8/34 · In progress**. Druhý blok rozširuje lifecycle od experiment metadata k durable artifact bytes, complete model package, governed Registry promotion a exact online feature values. Incident `MLOPS-PAY-91` spája partial multi-file upload zakrytý local cache, neúplné dependency inference, mutable Registry alias použitý ako runtime identity a stale online features po chybnom materialization watermarku. Kapitoly oddeľujú backend store od artifact store, package digest od serving image, Registry version/alias od loaded modelu a feature definition od request-correlated online value. Ďalší authoritative blok sú kapitoly 9–12: ML pipeline orchestration, training pipelines a distributed training, CI pre ML a Continuous Delivery pre modely. Sekcia nie je runtime `Verified`, production `Stable` ani user `Accepted`.
