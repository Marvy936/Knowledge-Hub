# Cross-validation

Cross-validation nie je spôsob, ako z jedného datasetu vytvoriť viac nezávislých testov. Je to resampling procedure, ktorá opakovane fituje celý training pipeline na rôznych training subsets a meria ho na zodpovedajúcich validation subsets. Výsledok odhaduje výkon model-building procedure pre deklarovanú population a split mechanism, nie výkon jedného konkrétneho final refit artifactu. Ak split ignoruje entity, time, site alebo dependency boundaries, viac foldov iba presnejšie zmeria leakage.

`ML-PAY-87` uzatvára štvrtá vetva incidentu. Atlas použil `cv=5`, čo pre classifier vytvorilo stratified folds, ale rovnaké merchant IDs a campaign bursts zostali v train aj validation. Preprocessing a oversampling boli vykonané pred `cross_validate`, takže validation rows ovplyvnili scaler, feature selection a synthetic samples. HPO report priemeroval folds, no jeden fold bez nového campaign cohortu dominoval výberu a threshold bol následne tuned na out-of-fold predictions vytvorených inou preprocessing generation. Tím označil výsledok za „5 independent tests“, hoci všetky folds zdieľali rovnaký dataset, labels a experimentálne rozhodnutia. Kapitola preto definuje cross-validation ako exact procedure subject s explicitnou dependency a selection boundary.

## 1. Dominantný cross-validation lifecycle

Cross-validation začína deployment scenárom a statistical unit, nie integerom `5`. Splitter generuje train/validation indices podľa class, group, time alebo custom constraints. V každom folde sa od nuly fituje preprocessing, sampling, feature selection a estimator iba na fold training data. Predictions a metrics sa ukladajú s fold identity. Fold distribution informuje selection, ale locked procedure sa nakoniec refituje a akceptuje na independent test alebo future window.

```text
deployment scenario a independent unit
→ exact dataset, labels, groups/time a split generation
→ fold train/validation indices
→ fit complete pipeline on fold train only
→ predict fold validation
→ per-fold predictions, metrics, fit time a failures
→ aggregate distribution a competing hypotheses
→ model/hyperparameter/threshold selection
→ locked final refit
→ untouched test alebo future-window acceptance
```

Cross-validation preto zahŕňa viac model artifacts. `best_estimator_` po refite nie je žiadny z fold modelov a fold score nepreukazuje final artifact correctness.

## 2. Exact cross-validation subject

Reprodukovateľný CV report identifikuje dataset manifest, splitter class/config, group/time fields, complete pipeline generation, metrics a resource behavior. `cv=5` nie je dostatočný contract, pretože framework môže vybrať odlišný default podľa estimator type a targetu.

```yaml
cv_subject: ML-PAY-CV-2026-08-v6
dataset:
  manifest: eu-cnp-mature-2026w10-w28-v5
  observation_unit: payment_operation_id
  label_generation: recoverable-loss-21d-v4
splitter:
  class: StratifiedGroupKFold
  n_splits: 5
  shuffle: true
  random_state: 17
  group_key: merchant_id
pipeline:
  preprocessing: risk-v9
  feature_selection: mutual-info-fold-local-v2
  sampler: random-undersample-fold-local-v3
  estimator: hist-gradient-boosting-v6
scoring:
  - average_precision
  - neg_log_loss
  - recall_at_capacity
artifacts:
  fold_indices: s3://ml-evals/87/folds-v6.parquet
  out_of_fold_predictions: s3://ml-evals/87/oof-v6.parquet
resources:
  n_jobs: 4
  failure_policy: fail_closed
```

Fold indices sú authoritative artifact. Random seed bez uložených indices nemusí zabezpečiť rovnaké splitovanie po zmene row orderu, library version alebo filtering.

## 3. Čo cross-validation odhaduje

Každý fold trénuje procedure na približne `(K-1)/K` dát a validuje na zvyšnej časti. Fold scores sú korelované, pretože training sets sa prekrývajú a zdieľajú rovnaký source dataset. Priemer a standard deviation sú descriptive summaries tejto konkrétnej CV procedure, nie automaticky klasický confidence interval nad nezávislými experimentmi.

```text
fold 1 model != fold 2 model != final refit model
fold validation samples sa neprekrývajú v bežnom KFold
fold training samples sa výrazne prekrývajú
```

CV odhaduje procedure behavior pod zvoleným splitterom. Ak production trénuje na staršom čase a predikuje budúcnosť, random KFold odhaduje inú úlohu než temporal split. Ak production musí generalizovať na nového merchantu, row-wise split odhaduje known-merchant interpolation.

## 4. KFold

`KFold` rozdelí samples na K foldov bez použitia labels. Pri `shuffle=False` závisí rozdelenie od row orderu. Ak data sú zoradené podľa time, class alebo source, folds môžu byť systematicky neporovnateľné.

```python
from sklearn.model_selection import KFold

cv = KFold(
    n_splits=5,
    shuffle=True,
    random_state=17,
)
```

KFold je vhodný iba vtedy, keď row-level exchangeability približne zodpovedá deployment scenáru a neexistujú relevantné group/time dependencies. Shuffle nevyrieši duplicate entities; iba ich náhodne rozptýli medzi folds.

Pri malom datasete väčšie K používa viac training data v každom folde, ale zvyšuje compute a môže zväčšiť variability malých validation folds. Leave-one-out je extrém a nie je automaticky najpresnejšia voľba.

## 5. StratifiedKFold

`StratifiedKFold` sa snaží zachovať class proportions v každom folde. Stabilizuje classification metrics a znižuje riziko foldu bez minority class.

```python
from sklearn.model_selection import StratifiedKFold

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=17,
)
```

Stratification rieši engineering constraint class counts, nie statistical independence. Rovnaký user, patient, host alebo merchant môže zostať v train aj validation. Zároveň môže zmenšiť observed fold-to-fold variability rarity, hoci production windows majú reálne kolísajúcu prevalence.

Multilabel alebo continuous target stratification potrebuje custom approach a môže vytvoriť sparse strata. Discretizovať regression target iba kvôli stratification mení split procedure a musí byť zdokumentované.

## 6. GroupKFold

`GroupKFold` drží všetky samples jednej group v jednom validation folde. Je vhodný, keď observations v rámci entity zdieľajú latent information a production musí generalizovať na unseen groups.

```python
from sklearn.model_selection import GroupKFold

cv = GroupKFold(n_splits=5)
for train_idx, valid_idx in cv.split(X, y, groups=merchant_id):
    assert set(merchant_id[train_idx]).isdisjoint(merchant_id[valid_idx])
```

Počet groups, ich veľkosť a class composition obmedzujú možné splits. Jeden veľký merchant môže dominovať foldu a vytvoriť vysokú variance; to môže byť pravdivý deployment risk, nie dôvod group boundary odstrániť. Fold report musí uviesť group counts a largest-group contribution.

Group identity sa musí definovať na úrovni skutočnej dependency. Groupovať podľa accountu nepomôže, ak viac accounts patrí rovnakému customerovi alebo device clusteru.

## 7. StratifiedGroupKFold

`StratifiedGroupKFold` kombinuje non-overlapping groups so snahou približne zachovať class distribution. Constraints môžu byť konfliktne a perfect stratification nie je vždy možná.

```python
from sklearn.model_selection import StratifiedGroupKFold

cv = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=17,
)
```

Je vhodný pri imbalanced labels a entity dependencies, ale stále odhaduje unseen-group scenario iba pre groups podobné tým v datasete. Nové geography alebo future campaigns môžu vyžadovať additional holdout.

Audit uloží fold-level class counts aj group counts. Ak splitter vytvorí fold s nedostatočným positive supportom, verdict môže byť insufficient evidence; forbidden riešenie je presúvať rows ručne bez versionovanej split generation.

## 8. TimeSeriesSplit a temporal evaluation

`TimeSeriesSplit` zachováva time order: training precedes validation a successive training sets sa rozširujú. Parameter `gap` môže oddeliť training end od validation start a znížiť leakage cez lag, delayed labels alebo operational overlap.

```python
from sklearn.model_selection import TimeSeriesSplit

cv = TimeSeriesSplit(
    n_splits=5,
    test_size=14 * daily_rows,
    gap=2 * daily_rows,
    max_train_size=180 * daily_rows,
)
```

Current implementation predpokladá equally spaced samples pre porovnateľné duration metrics. Pri event data s rôznym počtom rows za deň je často lepší custom timestamp splitter, ktorý pracuje s calendar boundaries, nie row counts.

Temporal split musí rešpektovať feature event time, label maturity a embargo. Training row s eventom pred cutoffom môže mať label, ktorý dozrel až po validation period, a tým leakovať future outcome. Exact inclusion policy potrebuje as-of join a maturity boundary.

## 9. Rolling, expanding a blocked windows

Expanding window pridáva všetku históriu; rolling window drží fixnú recent history; blocked evaluation používa disjoint periods. Každý pattern odhaduje inú retraining policy.

```text
expanding:
train [1..t1] → validate [t1+1..t2]
train [1..t2] → validate [t2+1..t3]

rolling:
train [t0..t1] → validate [t1+1..t2]
train [t1..t2] → validate [t2+1..t3]
```

Expanding window môže zvýhodniť stabilné long-term patterns, rolling window reaguje na drift, ale zahadzuje staršiu rare evidence. CV procedure má kopírovať intended production training horizon a cadence. Inak hyperparameters optimalizujú neexistujúci operating model.

## 10. ShuffleSplit a repeated splits

`ShuffleSplit` alebo stratified variant umožňuje opakované random train/validation partitions s explicitnou veľkosťou. Repeated K-fold používa viac randomizations a odhaduje sensitivity na split composition.

```python
from sklearn.model_selection import RepeatedStratifiedKFold

cv = RepeatedStratifiedKFold(
    n_splits=5,
    n_repeats=3,
    random_state=17,
)
```

Viac repeats zvyšuje compute a počet pohľadov na rovnaký dataset, ale nevytvára nové population evidence. Pri repeated model selection rastie riziko validation overfit. Groups a time dependencies zostávajú hard constraints; random repeats ich nesmú porušiť.

## 11. PredefinedSplit a external fold authority

Niekedy fold assignment vzniká mimo scikit-learn: podľa site, region, challenge protocol, policy rollout alebo presného historical splitu. `PredefinedSplit` umožní použiť uložený fold vector.

```python
from sklearn.model_selection import PredefinedSplit

cv = PredefinedSplit(test_fold=fold_assignment)
```

`-1` môže označiť samples, ktoré zostávajú vždy v trainingu podľa API contractu. Takéto privileged rows musia mať business dôvod; inak znižujú nezávislosť. External split artifact sa versionuje spolu s datasetom a kontroluje na duplicate IDs, coverage a disjointness.

## 12. Pipeline fit boundary

Každý fitted transform musí vzniknúť vo vnútri fold training domain. Zahŕňa imputation, scaling, encoding, dimensionality reduction, target encoding, feature selection, resampling a model fit.

```python
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ("preprocess", preprocessor),
    ("select", selector),
    ("model", estimator),
])
```

Calling `fit_transform` na celom datasete pred CV je leakage aj vtedy, keď transform nepoužíva explicitne target. Global mean, vocabulary, category inventory alebo feature variance obsahujú validation population information. Target-aware transforms sú ešte citlivejšie.

Cache v pipeline môže zlepšiť výkon, ale cache key musí zahŕňať fold training inputs a parameters. Shared mutable cache bez exact identity môže vrátiť fitted state z iného foldu.

## 13. `cross_validate` a multi-metric evidence

`cross_validate` dokáže vrátiť viac metrics, fit/score times a podľa konfigurácie estimators alebo indices. Report musí zachovať per-fold values; iba mean string v CI logu nestačí.

```python
from sklearn.model_selection import cross_validate

result = cross_validate(
    pipeline,
    X,
    y,
    groups=merchant_id,
    cv=cv,
    scoring={
        "ap": "average_precision",
        "log_loss": "neg_log_loss",
    },
    return_train_score=True,
    return_indices=True,
    error_score="raise",
    n_jobs=4,
)
```

Presný signature a metadata routing sa overuje proti pinned version. `error_score="raise"` je vhodný pre authoritative validation, pretože failed fold nemá byť ticho nahradený NaN a ignorovaný v priemere. Train scores môžu pomôcť generalization diagnosis, ale zvyšujú compute a neslúžia ako acceptance.

## 14. Out-of-fold predictions

Out-of-fold prediction pre sample vzniká z modelu, ktorý tento sample nemal vo fold trainingu. OOF artifact umožňuje aggregate metric, calibration alebo threshold analysis v training domain.

```python
from sklearn.model_selection import cross_val_predict

oof_proba = cross_val_predict(
    pipeline,
    X,
    y,
    groups=merchant_id,
    cv=cv,
    method="predict_proba",
    n_jobs=4,
)[:, 1]
```

OOF predictions nie sú predictions jedného deployable modelu. Každý sample môže byť scored iným fold modelom. Aggregate metric z `cross_val_predict` nemusí zodpovedať average fold metric, najmä pri unequal fold sizes alebo non-decomposable metrics. OOF artifact musí niesť fold ID a pipeline generation.

Použiť OOF predictions na threshold selection môže byť validná training-domain strategy, ale final model sa potom refituje na všetkých training data a untouched test hodnotí celý locked procedure vrátane threshold rule.

## 15. Hyperparameter search a CV reuse

Grid/random/model-based search používa CV score na výber hyperparameters. Keď sa porovná veľa candidates, best CV score je optimistický voči selection process. Rovnaké folds môžu zlepšiť paired comparability, ale opakované manuálne rozhodnutia spotrebúvajú validation evidence.

```text
candidate configs
→ same fold generation
→ fold metrics
→ aggregate objective and guards
→ selected configuration
→ refit
```

Search space, sampler, budget, folds a scorer tvoria jeden HPO subject. Zmeniť folds po pohľade na results môže byť legitímna correction iba s invalidation a successor generation, nie hidden retry.

## 16. Nested cross-validation

Nested CV oddeľuje inner model selection od outer performance estimation. Každý outer fold spustí vlastný inner search iba nad outer-training data; selected inner procedure sa hodnotí na outer validation.

```text
outer train
  → inner folds
  → hyperparameter/threshold selection
  → refit on outer train
outer validation
  → unbiased-like estimate of full selection procedure
```

Nested CV je compute-intensive a stále závisí od correct outer splitter. Outer fold results odhadujú selection procedure, nie final production artifact. Po nested analysis sa configuration strategy refituje na full training domain a independent future/test acceptance môže byť stále potrebná, najmä pri high-stakes deployment.

Použiť rovnaký outer validation na ďalšie manuálne tuning decisions zničí nested boundary.

## 17. Multiple metrics a selection rule

Cross-validation často reportuje viac metrics, ale refit selection potrebuje explicitnú primary scorer alebo callable rule. Candidate s najlepším average primary metric môže porušiť cohort floor, resource budget alebo fold stability.

```yaml
selection:
  primary: mean_average_precision
  constraints:
    min_campaign_recall_each_fold: 0.35
    max_fit_time_p95_seconds: 900
    failed_folds: 0
  tie_breaker:
    - lower_model_size
    - lower_fold_variance
```

Averaging guardrail across folds môže skryť jeden catastrophic fold. Mandatory constraints sa kontrolujú per-fold alebo per-scenario. Rule sa uzamyká pred search results, aby sa nestala post-hoc preferenciou.

## 18. Fold aggregation a unequal sizes

Simple mean fold metrics dáva každému foldu rovnakú váhu. Aggregate metric z concatenated OOF predictions dáva každému sample contribution. Pri unequal fold sizes alebo non-linear metrics môžu byť výsledky odlišné.

```text
mean(per_fold_metric)
≠ metric(concatenated_oof_predictions)
```

Obe summaries môžu byť užitočné, ale musia byť pomenované. Group or time folds často majú rozdielne sizes zámerne. Weighted average podľa sample count môže znovu umožniť veľkému easy foldu prekryť kritický deployment scenario.

Report preto obsahuje fold table, OOF aggregate, support, groups/time range a worst-fold guardrail.

## 19. Variance, uncertainty a correlated folds

Standard deviation fold scores opisuje spread, ale folds nie sú independent repeated production deployments. Na confidence interval treba zvážiť dependency structure, grouped/time bootstrap alebo repeated external periods. CV nemá magicky odstrániť dataset uncertainty.

Model comparison sa robí paired na rovnakých folds. Rozdiel per-fold metrics je informatívnejší než dve unrelated CV runs. Pri malom počte folds je inferencia slabá a practical significance zostáva dôležitejšia než jeden p-value.

```text
same folds
→ baseline and candidate predictions
→ paired fold and OOF differences
→ cohort/time analysis
→ uncertainty compatible with independent unit
```

## 20. Parallel execution a resource semantics

`n_jobs` paralelizuje fold/candidate fits, ale mení resource pressure a môže odhaliť memory amplification. Päť foldov × desať candidates × threaded estimator môže vytvoriť nested parallelism a OOM.

```yaml
execution:
  outer_jobs: 4
  estimator_threads: 2
  memory_limit_gib: 32
  timeout_per_fit_seconds: 1800
  failed_fit_policy: fail_closed
```

Fit time je súčasť experiment evidence. Candidate, ktorý prejde iba pri cache alebo resource oversubscription odlišnej od production training platform, nemusí byť reproducible. Random-number streams v parallel execution sa musia seedovať podľa framework semantics; rovnaký global seed nemusí znamenať identický floating-point trajectory.

## 21. Failure handling a partial folds

Fold môže zlyhať pre invalid hyperparameter, missing class, numerical error, timeout alebo infrastructure incident. Tiché `NaN` a následný `nanmean` môžu zvýhodniť fragile candidate.

```text
all planned fold IDs
→ started fits
→ succeeded/failed/timed-out
→ metrics only for valid predictions
→ candidate validity rule
```

Authoritative gate spravidla vyžaduje zero unexplained failed folds. Expected invalid combinations sa majú odstrániť zo search space-u alebo explicitne klasifikovať. Retrying unknown-outcome fit potrebuje attempt identity a nesmie prepísať pôvodné logs/artifacts.

## 22. Final refit a independent acceptance

Po selection sa locked pipeline refituje na všetkých allowed training data. Tento artifact má iný training sample count a fit trajectory než fold models. Jeho digest, preprocessing state a runtime behavior treba validovať samostatne.

```text
selected procedure
→ full training-domain refit
→ immutable artifact and preprocessing state
→ inference compatibility tests
→ untouched test/future window
→ business and operational acceptance
```

CV mean sa nesmie kopírovať ako metric final artifactu. Untouched test hodnotí selection + refit procedure raz. Ak výsledok vedie k ďalšiemu tuning cycle, test sa stal development evidence a ďalšia final acceptance potrebuje novú independent generation.

## 23. Worked incident `ML-PAY-87`

Atlas `cv=5` vytvoril `StratifiedKFold`, pretože estimator bol classifier. Row order bol náhodný, ale operations rovnakého merchantu a retry chainu sa rozdelili medzi folds. Pred CV sa na celom datasete fitol target encoder a feature selector; RandomOverSampler následne vytvoril duplicate positives ešte pred splitom.

```text
global preprocessing + global oversampling
→ row-wise stratified folds
→ shared merchants/duplicates
→ optimistic fold scores
```

OOF predictions boli neskôr použité na threshold selection, ale pochádzali zo staršej pipeline generation než HPO-selected model. Fold metrics sa priemerovali bez supportu a failed fold pre campaign cohort bol nahradený NaN. Dashboard zobrazil mean z remaining folds a označil ho za päť independent tests.

Po zavedení grouped-temporal splitu, fold-local pipeline a fail-closed behavior average precision klesla, no výsledok konečne reprezentoval unseen-merchant/future scenario. Root cause bol nesprávny CV estimand a fit boundary, nie „príliš prísny splitter“.

## 24. Competing failure hypotheses

Prekvapivo dobrý alebo nestabilný CV výsledok môže byť vlastnosťou model-building procedure, ale rovnako môže vzniknúť chybným estimandom, splitom, fit boundary, fold aggregation alebo execution policy. Diagnostika preto nezačína zmenou `random_state`; najprv overí exact fold indices, ID/group disjointness, time order, label maturity, fold-local fitted state, všetky planned fold statuses a OOF artifact generation.

Každá hypotéza musí meniť inú časť evidence. Entity leakage sa prejaví shared groups alebo near-duplicates naprieč folds; preprocessing leakage zmizne po presunutí fitu do pipeline pri rovnakých indices; aggregation masking sa ukáže v fold table oproti OOF aggregate; failed-fit masking zmení candidate ranking po fail-closed pravidle. Deployment mismatch môže prežiť všetky technické checks, ale zlyhá na future/unseen-group windowe. Pred novým CV runom treba rozlíšiť tieto mechanisms:

- row-order artifact — non-shuffled KFold kopíruje source ordering;
- entity leakage — dependent groups sa rozdelili medzi train a validation;
- temporal leakage — future observations, labels alebo feature state vstúpili do trainingu;
- preprocessing leakage — fitted transforms videli validation rows;
- resampling leakage — duplicates alebo synthetic points prešli naprieč folds;
- fold-support failure — niektorý fold nemá relevantnú class/cohort evidence;
- aggregation masking — mean prekrýva catastrophic fold alebo unequal sizes;
- selection overfit — priveľa candidates a manuálnych iterácií spotrebovalo folds;
- OOF generation mismatch — predictions pochádzajú z inej pipeline/split generation;
- failed-fit masking — NaN/ignored folds zvýhodnili fragile candidate;
- resource nondeterminism — parallelism, cache alebo timeout zmenili candidate set;
- deployment mismatch — splitter odhaduje known-entity/random scenario namiesto future/unseen scenario.

Každá hypothesis má iný evidence pattern. Near-duplicate IDs medzi train/validation dokazujú split failure; stabilné fold indices s rozdielom po pipeline move ukazujú preprocessing leakage; zhoršenie iba v future foldoch podporuje temporal shift namiesto generic variance.

## 25. Evidence-preserving containment a recovery

Containment zastaví promotion a zachová dataset manifest, fold indices, groups/timestamps, pipeline code, fitted fold artifacts, predictions, metrics, failed-fit logs a resource config. Nie je správne iba zmeniť `random_state` a vybrať priaznivejší výsledok.

```text
freeze selection and refit
→ preserve fold assignment and per-fold artifacts
→ validate ID disjointness, time order and label maturity
→ reconstruct fold-local fit boundary
→ reconcile all planned/succeeded/failed folds
→ recompute per-fold and OOF metrics
→ test competing hypotheses
→ create successor CV generation
→ independent refit/test acceptance
```

Ak bol splitter nesprávny, dependent HPO, threshold a model verdicts sa označia invalid. Recovery nevydáva corrected mean nad pôvodnými leaked predictions, ale opakuje entire procedure s novým split subjectom.

## 26. Acceptance contract

Positive acceptance identifikuje deployment scenario, independent unit, dataset/label generation, splitter class/config, exact fold indices, complete fold-local pipeline, metrics, aggregation, failure policy a resources. Každý planned fold má predictions, support a status; group/time invariants sú machine-checked.

Recovery acceptance preukazuje, že successor split odstránil leakage a dependent selection/refit artifacts majú novú lineage. Forbidden paths zahŕňajú global preprocessing alebo resampling pred CV, row-wise split pri entity dependency, future-to-past training, ignorované failed folds, označenie folds za independent tests, threshold/HPO tuning na outer acceptance data a kopírovanie CV mean ako final artifact metric.

Second-operation test znovu generuje fold indices a CV run z rovnakých manifests a musí zachovať membership, pipeline parameters, planned fold count a metrics v declared stochastic tolerance. Second-window test používa novšiu temporal alebo unseen-group population a overuje, že selected procedure generalizuje mimo pôvodného resampling universe.

```yaml
acceptance:
  deployment_aligned_splitter: passed
  exact_fold_indices_preserved: passed
  fold_local_pipeline: passed
  all_planned_folds_accounted_for: passed
  per_fold_and_oof_evidence: passed
  independent_refit_test: passed
  second_window: passed
```

## Kontrolné otázky

1. Čo cross-validation odhaduje a čo nepreukazuje?
2. Prečo folds nie sú nezávislé testy?
3. Kedy je KFold vhodný a čo shuffle nevyrieši?
4. Prečo stratification rieši engineering problém, nie dependency boundary?
5. Ako GroupKFold mení deployment question?
6. Kedy použiť StratifiedGroupKFold?
7. Aké assumptions a hranice má TimeSeriesSplit?
8. Ako sa expanding a rolling windows líšia?
9. Prečo repeated CV nevytvára novú population evidence?
10. Kedy je PredefinedSplit autoritatívny?
11. Prečo preprocessing, feature selection a resampling musia byť fold-local?
12. Aký je rozdiel medzi average fold metric a metric nad OOF predictions?
13. Čo OOF prediction reprezentuje a prečo nejde o jeden deployable model?
14. Ako nested CV oddeľuje selection od estimation?
15. Prečo failed folds nesmú byť ticho ignorované?
16. Ako parallel execution mení resource a reproducibility contract?
17. Prečo final refit potrebuje samostatný artifact a test evidence?
18. Čo pokazilo cross-validation lifecycle v `ML-PAY-87`?
19. Aké positive, recovery, forbidden a second-window testy uzatvárajú CV contract?

## Glossary impact

Relevantné pojmy: cross-validation, resampling procedure, fold, splitter, KFold, StratifiedKFold, GroupKFold, StratifiedGroupKFold, TimeSeriesSplit, rolling window, expanding window, ShuffleSplit, repeated cross-validation, PredefinedSplit, fold-local pipeline, out-of-fold prediction, cross-validation aggregation, nested cross-validation, inner fold, outer fold, selection bias, failed fit, final refit, deployment-aligned evaluation a cross-validation acceptance contract.

## Primárne zdroje

- [scikit-learn — Cross-validation: evaluating estimator performance](https://scikit-learn.org/stable/modules/cross_validation.html)
- [scikit-learn — `KFold`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.KFold.html)
- [scikit-learn — `StratifiedKFold`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html)
- [scikit-learn — `GroupKFold`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html)
- [scikit-learn — `StratifiedGroupKFold`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html)
- [scikit-learn — `TimeSeriesSplit`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [scikit-learn — `cross_validate`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.cross_validate.html)
- [scikit-learn — Nested versus non-nested cross-validation](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Imbalanced datasets a threshold selection](imbalanced-datasets-threshold-selection.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
