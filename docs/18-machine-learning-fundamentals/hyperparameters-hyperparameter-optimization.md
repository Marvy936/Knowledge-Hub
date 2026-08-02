# Hyperparameters a hyperparameter optimization

Hyperparameter nie je parameter, ktorý model odhadne gradientom alebo iným fit mechanizmom z training samples. Je to vstup do training procedure, modelovej kapacity, regularizácie, preprocessing pipeline, search algoritmu alebo deployment contractu, ktorý musí byť zvolený mimo samotného fitu. Počet stromov, maximálna hĺbka, learning rate, batch size, strength regularizácie, architektúra siete, tokenizer alebo decision threshold môžu všetky ovplyvniť výsledok, ale nepatria automaticky do jednej optimization vrstvy. Niektoré určujú model family, iné resource cost, ďalšie menia evaluation alebo business policy. Hyperparameter optimization preto nie je „nájdi najvyššie score“. Je to riadený experiment nad presne definovaným search space-om, objective-om, data splitom, budgetom a selection rule, ktorý vytvorí kandidáta pre nezávislé overenie.

Incident `ML-PAY-86` vyvrcholil pri automatizovanom searchi Atlas modelu. Tím spustil stovky trialov nad rovnakým validation setom, nechal search meniť preprocessing, learning rate, architecture aj classification threshold a potom publikoval trial s najvyšším validation F1. Failed trialy sa zapisovali ako nulové score, pruned trialy ako úspešné lacné experimenty a resume po výpadku znovu použil rovnaké trial numbers s iným code commitom. Dashboard nevedel odlíšiť search objective od final acceptance, trial budget od model training budgetu ani selected configuration od refitovaného artifactu. Výsledok bol reprodukovateľný iba názvom experimentu, nie jeho generáciou.

## 1. Dominantný hyperparameter-search lifecycle

Search začína fixovaným business taskom, training/evaluation protocolom a model pipeline. Search space definuje povolené konfigurácie a podmienky medzi nimi. Search algorithm navrhuje trial, training runner ho vykoná nad prideleným resource budgetom a evaluator vráti objective aj guardrail metrics. Trial ledger uchová configured, started, completed, pruned a failed states. Selection rule vyberie configuration; až potom sa vykoná deklarovaný refit a nezávislá test/business acceptance.

```text
business task + data contract
→ fixed split/evaluation protocol
→ search space + constraints
→ sampler alebo scheduler navrhne trial
→ training s prideleným budgetom
→ intermediate evidence
→ complete / prune / fail verdict
→ objective + guardrails
→ selected configuration
→ deterministic refit
→ independent test a business acceptance
```

Search result je experimentálny verdict nad konkrétnym protocolom. Nie je automaticky produkčný model artifact a už vôbec nie dôkaz, že produkčná politika alebo latency/cost boundary je prijateľná.

## 2. Exact search subject

Každý search musí mať manifest, ktorý zviaže code, data, feature pipeline, split generation, search space, sampler, pruner, objective, budget a runtime image. Bez tejto identity sa rovnaký názov study môže po resume zmeniť na inú experimentálnu populáciu.

```yaml
search_subject: ML-PAY-HPO-2026-08-v1
code_commit: 6e13b91
container_digest: sha256:47a1...
dataset_snapshot: atlas-payments-2026-07-31
feature_contract: fraud-features-v12
split_generation: grouped-time-split-v3
model_family: histogram-gradient-boosting
search_space_version: hgb-space-v4
sampler:
  type: randomized
  seed: 481516
pruner:
  type: successive-halving
  minimum_resource: 10000-samples
objective:
  metric: validation_pr_auc
  direction: maximize
guardrails:
  p95_inference_ms: "<= 25"
  model_size_mb: "<= 180"
  merchant_recall_min: ">= 0.72"
max_trials: 120
max_wall_clock_hours: 8
trial_failure_policy: exclude-and-report
refit_rule: full-training-set-with-selected-hyperparameters
```

`search_space_version` je rovnako dôležitý ako code commit. Pridanie nového rozsahu, zmena distribúcie alebo podmienenej vetvy mení experiment, aj keď study name zostane rovnaký.

## 3. Parameter, hyperparameter a policy parameter

Fitted parameter vzniká počas `fit`: coefficient, tree split, leaf value, embedding weight alebo batch-normalization running state. Hyperparameter určuje, ako fit prebehne alebo akú hypothesis class môže vytvoriť. Policy parameter mení rozhodnutie nad outputom, napríklad threshold, top-K alebo review capacity. Tieto vrstvy možno optimalizovať spolu iba vtedy, keď objective a acceptance presne modelujú ich spoločný business effect.

```text
training data
→ fit procedure configured hyperparameters
→ fitted model parameters
→ prediction score
→ policy parameter, napríklad threshold
→ business action
```

Ak search optimalizuje threshold na tom istom validation sete ako model hyperparameters, každý trial spotrebúva ďalšiu časť validation information. Final test musí zostať mimo tohto loopu.

## 4. Search space ako kontrakt

Search space nie je iba zoznam hodnôt. Definuje typ, rozsah, scale, podmienky, zakázané kombinácie a resource dôsledky. Learning rate sa často vzorkuje logaritmicky, pretože rozdiel medzi `1e-4` a `1e-3` má podobný násobkový význam ako medzi `1e-3` a `1e-2`. Tree depth je diskrétna. Architecture môže mať podmienené branches.

```python
space = {
    "learning_rate": LogUniform(1e-4, 1e-1),
    "max_depth": Integer(3, 12),
    "l2_regularization": LogUniform(1e-8, 10.0),
    "max_leaf_nodes": Integer(15, 255),
}
```

Podmienený search musí zabrániť nezmyselným konfiguráciám:

```python
if trial.suggest_categorical("model_family", ["linear", "tree"]) == "linear":
    alpha = trial.suggest_float("alpha", 1e-6, 10.0, log=True)
else:
    depth = trial.suggest_int("max_depth", 3, 12)
```

Search space má byť preskúmateľný pred spustením. Neobmedzené kombinácie môžu vytvoriť GPU OOM, extrémnu latency alebo modely, ktoré nikdy nebudú deploynuteľné.

## 5. Grid, random a model-based search

Grid search vyhodnotí kartézsky súčin explicitných hodnôt. Je vhodný pre malý diskrétny priestor alebo finálny lokálny sweep, ale rastie exponenciálne s počtom dimensions. Random search vzorkuje pevný počet konfigurácií z distribúcií a často efektívnejšie pokryje dimensions, keď iba niektoré hyperparameters dominujú výsledku. Model-based alebo Bayesian samplers používajú históriu trialov na návrh ďalších kandidátov, no ich proposals závisia od completed/pruned/failed evidence a sampler generation.

```python
from sklearn.model_selection import RandomizedSearchCV

search = RandomizedSearchCV(
    estimator=pipeline,
    param_distributions=space,
    n_iter=80,
    scoring="average_precision",
    cv=grouped_time_cv,
    random_state=481516,
    refit=True,
    error_score="raise",
)
search.fit(X_train, y_train, groups=merchant_groups)
```

`best_score_` je priemerný cross-validation verdict podľa definovaného scoringu. Neznamená untouched test performance a `best_estimator_` je refitovaný podľa semantics konkrétneho nástroja, ktoré treba explicitne poznať.

## 6. Objective a multi-objective trade-off

Single objective zjednodušuje selection, ale môže skryť latency, memory, fairness alebo operational cost. Weighted scalar objective je použiteľný iba vtedy, keď weights reprezentujú schválený trade-off. Inak treba pracovať s constraints alebo Pareto frontierom.

```text
maximize PR-AUC
subject to:
  p95 latency <= 25 ms
  model size <= 180 MB
  recall for protected merchant cohort >= 0.72
```

Candidate s najvyšším aggregate score môže byť zakázaný pre kritický cohort. Guardrail failure sa nesmie „spriemerovať“ s dobrým objective score.

## 7. Cross-validation a nested evaluation boundary

Hyperparameter tuning je model selection. Ak sa rovnaké folds použijú na selection aj na odhad generalization bez outer boundary, výsledok je optimistický. Nested cross-validation používa inner loop na tuning a outer loop na odhad performance celej selection procedure.

```text
outer training fold
→ inner hyperparameter search
→ selected configuration
→ fit na outer training fold
→ evaluate na outer holdout
→ repeat across outer folds
```

Nested CV nie je vždy nutná pre produkčný workflow s dostatočným validation a untouched test setom, ale boundary musí byť explicitná. Group, time a entity constraints platia aj vo vnútri searchu; bežný random K-fold môže znovu zaviesť leakage, ktorú hlavný split odstránil.

## 8. Resource budget a fidelity

Trial resource môže byť počet samples, epochs, trees, wall-clock, GPU-seconds alebo resolution. Multi-fidelity search najprv vyhodnocuje veľa kandidátov lacno a postupne prideľuje viac resource tým perspektívnym. Low-fidelity ranking však nemusí zachovať poradie pri full budgete.

```text
120 candidates × 10 % samples
→ 40 candidates × 30 % samples
→ 12 candidates × 100 % samples
→ final refit selected configuration
```

Successive halving alebo pruning šetrí compute, ale mení selection procedure. Minimum resource musí byť dostatočný na rozlíšenie kandidátov; inak systém odstráni slow-starting modely skôr, než sa prejavia.

## 9. Pruning nie je failure

Pruned trial bol zámerne ukončený na základe intermediate evidence a pruner policy. Failed trial skončil neplánovane pre exception, OOM, NaN alebo infrastructure fault. Completed trial dosiahol deklarovaný budget. Tieto stavy sa nesmú agregovať do jedného priemerného score.

```json
{
  "trial_id": 47,
  "state": "PRUNED",
  "resource_used": {"epochs": 8, "gpu_seconds": 912},
  "last_intermediate_metric": 0.413,
  "pruner_generation": "median-pruner-v2",
  "reason": "below promotion threshold at step 8"
}
```

Pruned trial neposkytuje full-budget comparison. Failed trial s `score=0` môže skresliť sampler a zakryť systematický bug v určitej časti space-u.

## 10. Parallelism a scheduler bias

Pri paralelnom HPO návrhy vznikajú z neúplnej histórie, pretože niektoré trialy ešte bežia. Asynchronous scheduler môže preferovať krátke trialy a penalizovať pomalšie konfigurácie. Shared storage, locking, duplicate trial reservation a seed semantics musia byť explicitné.

```text
sampler state
→ reserve unique trial ID
→ immutable configuration
→ worker lease
→ heartbeat
→ result commit alebo stale-lease recovery
```

Blind retry nesmie vytvoriť druhý trial s rovnakým ID a odlišnou configuration. Unknown outcome po network timeout-e sa najprv rieši read-backom study storage.

## 11. Reproducibility a resume

Reprodukcia vyžaduje viac než random seed. Treba zachovať search space, sampler/pruner state, completed trial ledger, code/environment, split indices a objective implementation. Resume je bezpečný iba vtedy, keď noví workers používajú kompatibilnú generáciu.

```yaml
resume_contract:
  expected_search_subject: ML-PAY-HPO-2026-08-v1
  expected_storage_schema: opt-study-v3
  expected_code_commit: 6e13b91
  allow_new_trials: true
  allow_recompute_completed_trial: false
  allow_search_space_change: false
```

Ak sa search space alebo objective mení, má vzniknúť nová study generation alebo explicitná migration, nie tichý resume.

## 12. Refit a selected artifact

Search vyberá configuration; produkčný artifact často vznikne samostatným refitom na training plus validation dátach. Tento refit môže mať iný sample count a training trajectory než trial, preto musí mať vlastný artifact digest a evidence.

```text
selected trial configuration
→ locked preprocessing + hyperparameters
→ refit dataset manifest
→ fresh fit
→ artifact digest
→ untouched test
→ deployment candidate
```

Nie je správne označiť trial checkpoint za finálny artifact bez deklarácie. Rovnako sa nesmie po pozretí test výsledku vrátiť do searchu bez vytvorenia novej evaluation generation.

## 13. Failure hypotheses

Pri sklamaní searchu treba odlíšiť aspoň tieto hypotézy:

- search space neobsahuje použiteľnú konfiguráciu;
- objective nereprezentuje business outcome;
- split alebo CV porušuje time/entity boundary;
- sampler nemal dostatočný budget;
- pruner odstránil kandidátov príliš skoro;
- trial failures systematicky zasahujú určitú časť space-u;
- parallel scheduler zvýhodňuje krátke trialy;
- selected configuration bola refitovaná iným pipeline contractom;
- validation set bol opakovaným tuningom preťažený;
- apparent gain je seed alebo fold variance.

Každá hypotéza musí predpovedať odlišný evidence pattern. Viac trialov samo osebe nevyrieši zlý objective alebo leakage.

## 14. Containment a recovery

Pri nekonzistentnej study sa zastaví scheduling nových trialov, zachová sa storage snapshot a exportuje sa trial ledger. Najprv sa rozdelia completed, pruned, failed a running leases. Potom sa overí code/search-space/objective generation a rozhodne sa, či je resume autoritatívny alebo treba novú study.

```text
freeze scheduler
→ snapshot study storage
→ reconcile trial states a leases
→ identify last compatible generation
→ invalidate incompatible trials
→ resume alebo create successor study
→ deterministic refit
→ independent acceptance
```

Recovery nesmie prepisovať historické trial configuration ani ich výsledky. Opravený trial je nový attempt alebo nový trial s explicitnou lineage.

## 15. Acceptance matrix

Positive acceptance vyžaduje, aby selected configuration prešla refitom, untouched testom, cohort guardrails a resource constraints. Recovery acceptance overí resume alebo successor study bez duplicate/rewritten trialov. Forbidden path musí odmietnuť test-set tuning, incompatible resume, deploy candidate nad failed/pruned trialom a configuration mimo approved constraints. Second-operation test spustí opakovaný search alebo refit s rovnakým manifestom a vysvetlí povolenú variabilitu.

```yaml
acceptance:
  positive:
    selected_config_refit: passed
    untouched_test: passed
    latency_and_size_guardrails: passed
  recovery:
    duplicate_trial_ids: 0
    incompatible_generation_trials_used: 0
  forbidden:
    test_set_in_objective_loop: rejected
    pruned_trial_promoted: rejected
    failed_trial_promoted: rejected
  second_operation:
    manifest_equal: true
    score_within_declared_variance_band: true
```

## 16. Praktický minimálny checklist

Pred searchom musí byť fixovaný task, split, objective, guardrails, budget a search-space owner. Počas searchu sa sledujú state counts, failure clusters, resource consumption a intermediate evidence. Po searchi sa nevytvára produkčný verdict z `best_score_`; vykoná sa selection read-back, deterministic refit, untouched test a business-level approval.

```bash
python export_study.py \
  --study ML-PAY-HPO-2026-08-v1 \
  --include-configurations \
  --include-intermediate-values \
  --include-system-attributes \
  --output study-export.json

python verify_hpo_lineage.py \
  --manifest hpo-manifest.yaml \
  --study-export study-export.json \
  --selected-artifact model-card.json
```

Úspešný export preukazuje dostupnosť study metadata, nie správnosť objective-u alebo produkčnú kvalitu modelu. Tie zostávajú samostatnou acceptance hranicou.

## Zhrnutie

Hyperparameter optimization je experimentálna selection procedure nad presným search subjectom. Grid, random, model-based sampling a multi-fidelity pruning majú odlišné cost a bias boundaries. Trial states, parallel scheduling, resume a refit musia byť reprodukovateľné. Validation alebo cross-validation score vyberá kandidáta; untouched test a business evidence rozhodujú, či sa selected artifact môže použiť. Najvyššie score bez lineage, guardrails a independent acceptance je iba najlepší záznam v nejasnom experimente, nie autoritatívny production model.

## Primárne zdroje

- scikit-learn, *Tuning the hyper-parameters of an estimator* a model-selection dokumentácia.
- scikit-learn, *Nested versus non-nested cross-validation*.
- Optuna, sampler a pruning dokumentácia pre current stable release.
