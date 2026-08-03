# MLOps platform architecture

MLOps platforma nie je jeden produkt ani jeden centrálny dashboard. Je to sústava control planes, data planes, stores, identities a governance boundaries, ktoré musia zachovať presnú lineage od source a datasetu až po production action a mature outcome. Architektúra je správna iba vtedy, keď sa dá pre každú operáciu určiť authoritative subject, vlastník, mutation path, read-back a recovery procedure bez závislosti od osobnej pamäte alebo jedného vendor UI.

V incidente `MLOPS-PAY-98` organizácia prevádzkovala GitHub CI, Kubeflow Pipelines, Kubeflow Trainer, MLflow Registry, KServe, Feast a SageMaker v dvoch accountoch. Každý subsystém bol lokálne funkčný, ale platforma nemala jednotný release manifest ani event identity. KFP vytvorila candidate, Registry alias sa presunul, KServe načítal starú feature generation a cloud fallback endpoint používal iný image digest. Monitoring spájal requesty iba podľa model name. Pri incidente nebolo možné určiť prvú odchýlku ani bezpečne rollbacknúť celý composite release. Problém nebol nedostatok nástrojov, ale chýbajúca architektonická authority.

## 1. Business capability pred produktmi

Architektúra začína požadovanou capability, nie zoznamom produktov. Platforma má umožniť napríklad reprodukovateľne vytvoriť candidate, bezpečne ho validovať, kontrolovane ho nasadiť, preukázať loaded state, sledovať outcome a obnoviť known-good generation.

```text
source a data change
→ validated build
→ immutable candidate
→ evaluation a governance verdict
→ release composition
→ deployment a actual exposure
→ monitoring a ground truth
→ rollback, retraining alebo retirement
```

Každý box môže implementovať open-source, cloud alebo interný systém. Nahradenie produktu je prijateľné iba vtedy, ak zostanú zachované contracts, identities a evidence.

## 2. Domény a bounded contexts

Praktická platforma sa rozdeľuje na bounded contexts s jasným ownershipom:

- source a CI authority,
- data a feature authority,
- pipeline a training orchestration,
- tracking, artifact a Registry authority,
- evaluation a governance,
- release a deployment control,
- online, batch a streaming inference,
- observability, feedback a cost,
- security, privacy a supply chain,
- backup, recovery a retirement.

Hranica nie je iba organizačná. Každý context vlastní konkrétne objects a nesmie implicitne prepisovať authority iného contextu. Registry napríklad eviduje candidate/version a promotion control, ale serving platforma vlastní loaded runtime a traffic. Feature store vlastní feature definitions a values, nie business label.

## 3. Control planes a data planes

Control plane prijíma intent a reconciliuje resources. Data plane vykonáva training, storage, inference alebo event processing. Ich evidence sa nesmie zlúčiť.

```text
Git / API intent
→ control-plane object
→ resolved workload alebo resource
→ loaded data-plane generation
→ exercised operation
→ business effect
```

KFP run phase, Trainer status, KServe condition alebo SageMaker resource status sú control-plane alebo orchestration evidence. Dôkaz loaded modelu, spracovaných samples, actual request exposure a downstream action patrí do data plane.

Platforma musí vedieť čítať oba smery. Desired state bez loaded read-back vedie k falošnej istote; data-plane telemetry bez source lineage vedie k nevysvetliteľnému incidentu.

## 4. Authoritative stores

Rôzne stores majú rôznu authority:

| Store | Authoritative obsah |
|---|---|
| Git | reviewed declarative source, policy a release intent |
| object store | immutable datasets, artifacts, checkpoints a evidence bundles |
| tracking backend | runs, parameters, metrics a lineage metadata |
| model registry | candidate/version metadata a promotion controls |
| feature registry/store | feature definitions, offline/online materialization state |
| Kubernetes/AWS API | desired a resolved runtime resources |
| observability backend | metrics, logs, traces a event-time operational evidence |
| audit store | approvals, waivers, signatures a decision chain |

Kópia alebo cache nie je automaticky authority. Každý consumer musí vedieť, z ktorého store číta, akú generation očakáva a ako overí freshness a digest.

## 5. Globálna subject identity

Najdôležitejší cross-platform object je immutable release manifest. Spája všetky generácie, ktoré môžu ovplyvniť behavior.

```yaml
release_id: fraud-2026-08-03.18
source_commit: 8c1e4c7
pipeline_ir_digest: sha256:...
dataset_digest: sha256:...
feature_definition_digest: sha256:...
model_artifact_digest: sha256:...
runtime_image_digest: sha256:...
evaluation_bundle_digest: sha256:...
policy_generation: fraud-promotion-v9
deployment_profile: fraud-serving-standard-v6
monitoring_generation: fraud-monitor-v12
```

Manifest nie je iba report po deployi. Je vstupom promotion, deploymentu, telemetry correlation a rollbacku. Mutable aliases alebo resource names sa ukladajú iba ako control pointers spolu s resolved immutable identities.

Každá operation má correlation ID a idempotency key. Cross-system event nesie subject digest, actor, source event a expected target state.

## 6. Event-driven integrácia bez straty authority

MLOps platformy často spájajú webhooks, queues, controllers a scheduled jobs. Event oznamuje, že sa niečo stalo; nie je automaticky dôkazom potreby mutation.

```text
source event
→ authenticated ingestion
→ deduplication
→ subject resolution
→ policy decision
→ idempotent operation
→ target read-back
→ completion event
```

Delivery môže byť at-least-once. Consumer preto deduplikuje podľa stable event/subject identity a pri unknown outcome používa read-before-retry. Event payload s mutable `latest` pointerom sa pred rozhodnutím rozlíši na immutable generation.

## 7. Identity, tenancy a trust zones

Human user, CI workload, training job, serving runtime a monitoring collector sú rozdielne principals. Platforma používa workload identity, krátkodobé credentials a capability-specific roles. Dataset read, Registry write, deployment mutation a production trace read sa nezdružujú do jednej service account.

Tenant boundary zahŕňa namespace/account/project, network, encryption key, artifact prefix, metadata visibility a quota. UI filter nie je isolation. Shared controllers a cluster-wide Runtimes sú high-blast-radius authority a potrebujú prísnejší change control.

Trust zones typicky oddeľujú developer environment, build plane, training plane, registry/evidence plane a production serving. Promotion medzi zones je explicitný transfer s integrity a authorization verification.

## 8. Platform APIs a paved roads

Platform team poskytuje paved-road interfaces, ktoré znižujú počet implicitných rozhodnutí. Môže ísť o pipeline component templates, TrainJob Runtimes, release schema, KServe serving profiles alebo cloud deployment modules.

Paved road nesmie skryť authority. User musí vedieť, aký resolved manifest vznikol, ktoré defaults sa aplikovali a ako ich versionovať. Template name bez versiony je mutable dependency.

Escape hatch je možný, ale mení risk class a vyžaduje extra evidence. Platforma nesmie predstierať podporu pre custom path, ktorý nemá monitoring, backup alebo recovery.

## 9. Build, train a serve planes

Build plane vytvára signed images, dependencies a provenance. Training plane spracúva datasets, distributed workloads a checkpoints. Serve plane načítava modely a obsluhuje traffic. Oddelenie znižuje blast radius a umožňuje odlišné capacity/security policies.

Artifact prechod medzi planes používa immutable store a manifest. Training environment nesmie pushnúť neoverený image priamo do production. Serving runtime nesmie sťahovať arbitrary code z experiment notebooku.

GPU pools môžu byť oddelené podľa training a serving latency requirements. Scheduler, quotas a autoscaling policies sú platform objects a ich generácie patria do subjectu.

## 10. Metadata a lineage plane

Metadata plane spája runs, artifacts, releases, deployments, requests a outcomes. Nemusí fyzicky obsahovať všetky bytes, ale musí uchovávať URI, digest, type, generation a relation.

Lineage graph je užitočný iba vtedy, ak edges vznikajú z authoritative operations. Manual tag „trained_from=data-v2“ bez digestu a enforcementu je slabý údaj. Platforma validuje required lineage fields pri publication a promotion.

Cross-vendor lineage sa často udržiava vo vlastnom release/evidence schema, pretože MLflow, KFP, Kubernetes a SageMaker používajú rozdielne object models.

## 11. Observability a feedback architecture

Operational telemetry musí byť korelovateľná s release manifestom a actual exposure. Metrics používajú bounded labels, traces/logs nesú request-level identity a audit/evidence store uchováva long-lived decision artifacts.

Feedback path od prediction po label je samostatná data pipeline s event-time joins, maturity a coverage. Nezdieľa automaticky rovnaký retention alebo privacy model ako request logs.

Monitoring platformy sledujú aj vlastnú health: dropped traces, delayed metrics, missing capture, failed joins a stale baselines. Absencia alarmu pri nefunkčnej telemetry nie je healthy model.

## 12. Governance ako runtime capability

Governance nie je PDF pred release. Policy-as-code, approvals, waivers, intended-use constraints a runtime conformity sa integrujú do change pathu. Human approval sa viaže na immutable decision subject a evidence bundle.

Runtime guard môže kontrolovať signed image, allowed model format, tenant, resource profile alebo approved release ID. Waiver má scope, owner, reason, compensating controls a expiry. Po expiry platforma zablokuje ďalšie mutations alebo vyžaduje reapproval.

## 13. Availability, backup a disaster recovery

Každý authoritative store má RPO/RTO a restore dependency. Registry bez object-store artifacts nie je obnoviteľná. KFP metadata bez pipeline rootu je neúplná. Feature online store môže byť znovu materializovateľný iba pri zachovanom offline source a watermarkoch.

DR architecture definuje poradie obnovy:

```text
identity a keys
→ source/config/policies
→ metadata a artifact stores
→ orchestration control planes
→ registry a feature services
→ serving control plane
→ workloads a traffic
→ monitoring a feedback
```

Failover do iného clusteru alebo Regionu je nová runtime generation. DNS alebo endpoint switch sa overuje actual trafficom a loaded fingerprintom.

## 14. Build versus buy a hybrid architecture

Managed služba znižuje operational burden, ale nemení potrebu lineage, read-back a portability decisions. Open-source stack zvyšuje control, no prenáša backup, upgrades, multi-tenancy a reliability na platform team.

Hybrid architecture je oprávnená, ak má jasnú authority. KFP môže orchestrate-nuť SageMaker jobs, MLflow môže evidovať model a KServe ho servovať. Každý bridge však pridáva unknown-outcome, identity a compatibility boundary.

Výber produktu sa hodnotí podľa capability, failure modelu, data sovereignty, ecosystemu, costu, staffing a exit strategy. Feature checklist bez recovery drillov je nedostatočný.

## 15. Platform SLO a product model

Platforma je interný produkt. SLO sa viažu na user journeys: compile a submit pipeline, start training, publish candidate, deploy release, query evidence a rollback. Availability jedného API nevystihuje end-to-end success.

Meria sa lead time, queue time, failed/duplicate operations, reproducibility rate, restore success, policy violations, cost a toil. Adoption sa nesmie zvyšovať tým, že platforma skryje errors alebo obíde controls.

## 16. Failure hypotheses a architecture review

Ak lineage chýba, príčinou môže byť chýbajúci contract, bridge, identity propagation alebo metadata loss. Ak rollback nevie obnoviť behavior, composite release bol neúplný. Ak dva systémy tvrdia rozdielny current model, chýba authoritative pointer alebo read-back reconciliation.

Architecture review prechádza jednu konkrétnu journey a incident, nie iba box diagram. Pre každý transition sa pýta: kto vlastní subject, čo je mutation, kde je durable evidence, čo sa stane pri timeout-e, ako sa retry deduplikuje a ako sa obnoví known-good state.

## 17. Acceptance

Pozitívna acceptance vyžaduje jasné bounded contexts, immutable release identity, oddelené control/data planes, least-privilege identities, idempotent events, authoritative stores, cross-platform lineage, monitoring coverage a tested recovery. Recovery acceptance vyžaduje restore/failover drill a druhú operation bez duplicate side effects.

Forbidden acceptance je diagram produktov, zelené statusy jednotlivých služieb, central dashboard bez source identity alebo managed-service SLA ako dôkaz business journey. Second-operation test zopakuje candidate-to-deployment journey s rovnakým subjectom. Všetky pure operations musia byť reprodukovateľné a mutation operations no-op alebo deterministicky reconciled.
