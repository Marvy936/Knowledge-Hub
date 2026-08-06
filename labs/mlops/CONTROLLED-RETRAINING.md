# Controlled retraining executor

Táto vrstva premieňa exact human approval na jednu bounded retraining operáciu. Approval sám training nespúšťa. Executor pred prvým side effectom znovu overí approval, proposal, drift report, current deployment, current model, nový dataset snapshot a Registry/promotion konfiguráciu.

```text
canonical drift report
+ canonical retraining proposal
+ exact human approval
+ current deployment read-back
+ new dataset snapshot
+ source revision a seed
→ controlled operation ID
→ durable phase state
→ deterministic training
→ training-manifest read-back
→ evaluation a candidate
→ exact Registry version a artifact read-back
→ compare-before-promote
→ completed state alebo explicit recovery
```

## Operation subject

`operation_id` je canonical SHA-256 nad:

- retraining approval, proposal a drift report IDs,
- current deployment, candidate a model identities,
- novým dataset name, generation, size a SHA-256,
- source revision a seed,
- evaluation policy generation,
- Tracking URI, experiment, model name a Registry alias,
- sample-request SHA-256,
- promotion alias a expected current candidate ID.

Workspace paths nie sú súčasťou identity. Rovnaké authoritative inputs preto vytvoria rovnaký operation ID aj v inom pracovnom adresári.

Executor odmietne dataset s rovnakým SHA-256 ako dataset current deploymentu. Tento Practical v1 flow vyžaduje nový retraining snapshot; vedomý code-only retraining patrí do inej explicitnej policy generation.

## Authorization read-back

Pred execution sa opakovane validuje:

- approval je canonical a autorizuje `start_controlled_retraining`,
- proposal je canonical a viazaný na `drift_detected`,
- drift report je canonical a semantically valid,
- approval a proposal odkazujú na exact drift report,
- approval, proposal a report odkazujú na current deployment,
- approval a proposal pinujú current model SHA-256,
- current deployment sa od approval momentu nezmenil,
- operation plan pinne tie isté subjects.

Zmena deployment generation, modelu alebo dataset bytes po approval vedie k refusal pred trainingom.

## Durable state machine

State používa fázy:

```text
planned
→ training_started
→ training_completed
→ candidate_recorded
→ registry_recorded
→ promotion_started
→ completed
```

Expected failure vytvorí `failed` state s bounded error summary. Každý state obsahuje:

- exact operation ID,
- attempt number,
- previous state ID,
- phase,
- read-back artifact identities,
- canonical state ID.

Artifact identities zahŕňajú training-manifest file digest, model SHA-256, evaluation-file digest, candidate ID, Registry evidence ID, numeric Registry version, release ID a alias-state file digest.

## Read-before-retry

Ak state už existuje, executor ho najprv prečíta.

- `completed` sa iba znovu overí; training, Registry ani promotion sa neopakujú.
- neukončený state bez explicitného expected state ID sa odmietne,
- recovery vyžaduje exact current state ID,
- stale recovery subject sa odmietne bez zmeny state-u,
- recovery rekonštruuje najvyšší bezpečný checkpoint z actual files,
- partial alebo orphaned outputs, ktoré nemožno jednoznačne priradiť, vyžadujú manual reconciliation.

Ak pád nastal po hotovom trainingu, recovery validuje manifest, dataset, model bytes a source revision a pokračuje z `training_completed`. Ak Registry evidence už existuje a sedí s candidate/model/source subjectom, Registry side effect sa neopakuje.

## Concurrency

Vedľa state súboru vzniká exclusive lock. Druhý súbežný executor sa odmietne. Lock nepredstavuje distributed coordination; contract je určený pre jeden authoritative local runner alebo pre externý orchestrátor, ktorý garantuje single-writer execution.

## Training a lineage

Production adapter volá Machine Learning flagship `train_and_package` s exact seedom a dočasne nastaví `GITHUB_SHA` na source revision operation subjectu.

Po trainingu executor prečíta späť:

- `artifact/manifest.json`,
- `artifact/model.joblib`,
- dataset SHA-256,
- model SHA-256,
- source revision,
- threshold a acceptance gates,
- selected model a runtime versions.

Evaluation vznikne cez existujúci `evaluation-from-training` contract. Candidate sa vytvorí až po úspešnom lineage read-backu.

## Registry a promotion

Registry adapter musí vrátiť canonical evidence pre exact candidate, source revision a model SHA-256. Executor odmietne:

- evidence pre iný candidate,
- inú source revision,
- iný downloaded artifact digest,
- alias, ktorý sa neresolvoval na zaznamenanú numeric version,
- parity failure.

Promotion používa existujúci compare-before-promote contract. Alias-state musí pred operáciou ukazovať na candidate current deploymentu. Stale alias nevytvorí release.

Po explicitnej oprave alias state-u môže recovery pokračovať z `registry_recorded` bez opakovania trainingu alebo registrácie.

## Executable driver

```bash
python labs/mlops/scripts/run_controlled_retraining.py \
  --approval labs/mlops/.runtime/retraining-approval.json \
  --proposal labs/mlops/.runtime/retraining-proposal.json \
  --drift-report labs/mlops/.runtime/drift.json \
  --current-deployment labs/mlops/.runtime/current-deployment.json \
  --dataset labs/mlops/.runtime/retraining.csv \
  --dataset-name churn-retraining \
  --dataset-generation 2026-08-06 \
  --sample-request labs/machine-learning/data/sample-request.json \
  --source-revision <exact-git-sha> \
  --seed 20260806 \
  --tracking-uri http://127.0.0.1:5057 \
  --experiment-name knowledge-hub-controlled-retraining \
  --model-name KnowledgeHubChurn \
  --registry-alias candidate \
  --promotion-alias champion \
  --alias-state labs/mlops/.runtime/alias-state.json \
  --output-dir labs/mlops/.runtime/controlled-retraining \
  --operation-output labs/mlops/.runtime/retraining-operation.json \
  --state labs/mlops/.runtime/retraining-state.json
```

Recovery pridá:

```bash
--recover-expected-state-id <exact-current-state-id>
```

Operation output sa nevymení za iný subject. Ak súbor už existuje, musí byť byte-semanticky rovnaký ako novo odvodený operation plan.

## Overená source hranica

Izolovaný executor contract prešiel:

- Python `compileall`,
- **12/12 pytest cases**.

Testy pokrývajú canonical operation identity, nový dataset gate, full training→candidate→Registry→promotion flow s fake adapters, completed-operation replay bez side effects, explicit recovery, training checkpoint read-back, Registry checkpoint recovery, stale alias recovery, wrong Registry candidate, current-deployment mutation, completed-output tampering a CLI recovery-contract exposure.

## Neoverená hranica

Táto source vrstva ešte nepreukazuje:

- live deterministic ML training v rovnakom rune,
- živý MLflow server a nový numeric Registry version,
- actual second-operation replay po process restart-e,
- crash počas remote Registry mutation,
- distributed locking,
- external approval identity,
- container build alebo deployment novej generácie,
- canary promotion po retrainingu,
- business outcome.

GitHub Actions runtime closeout zostáva blokovaný issue #151. Practical v1 retraining checkbox ostáva otvorený do exact live runu s Registry read-backom, second-operation testom a následným serving/canary evidence.
