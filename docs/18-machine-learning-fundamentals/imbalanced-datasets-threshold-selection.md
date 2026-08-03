# Imbalanced datasets a threshold selection

Class imbalance znamená, že classes nemajú v relevantnej populácii rovnakú prevalence alebo rovnaký operational význam. Nie je to automaticky chyba datasetu a nevyrieši sa mechanickým „vybalansovaním“ classes. Pri fraud, incident, failure alebo medical úlohách je raritná positive class často presným obrazom reality. Skutočný problém vzniká vtedy, keď training objective, split, metric, probability interpretation alebo decision policy nerešpektujú base rate, error costs a kapacitu downstream systému.

Threshold selection je samostatná decision vrstva nad model score alebo probability. Model sa môže zlepšiť bez zmeny threshold policy a threshold sa môže zmeniť bez retrainingu modelu. Ak sa tieto dve generácie zamieňajú, tím nevie, či production outcome ovplyvnila discrimination, calibration, prevalence, capacity alebo policy mutation.

V `ML-PAY-87` Atlas vytvoril 50/50 training dataset cez random undersampling negatives, použil class weights aj oversampling a potom interpretoval raw `predict_proba` ako production probability. Threshold `0.5` bol zvolený podľa training-balanced prevalence. Neskôr sa threshold optimalizoval na tom istom validation datasete, ktorý riadil hyperparameter search, a production queue ešte aplikovala fixed top-K capacity. Offline recall stúpol, ale false-positive volume prekročil analytickú kapacitu a hidden queue truncation znížila effective recall. Kapitola preto spája population prior, sampling, objective, probability, threshold a action capacity do jedného auditovateľného lifecycle-u.

## 1. Dominantný imbalance-to-decision lifecycle

Imbalance sa rieši od intended production population, nie od počtu riadkov v náhodnom training extracte. Najprv sa určí observation unit, base rate a mature labels. Split zachová group/time boundaries. Training procedure môže použiť weighting alebo resampling, ale evaluation sa vykonáva na representative alebo explicitne reweighted population. Raw model output sa následne kalibruje alebo interpretuje podľa svojho contractu a samostatná policy vyberie threshold, top-K alebo abstention.

```text
production population a action cost
→ exact observation unit, label maturity a prevalence
→ group/time-safe train/validation/test split
→ training-only weighting alebo resampling
→ fitted model a raw score generation
→ representative validation predictions
→ metric, cost, capacity a calibration evidence
→ threshold/top-K/abstention policy generation
→ production action a queue behavior
→ drift, recovery a second-window acceptance
```

Tento chain oddeľuje data-level technique od decision-level policy. Oversampling môže zmeniť optimization trajectory, ale nepreukazuje, že `0.5` je správny production threshold ani že predicted probabilities reprezentujú original prevalence.

## 2. Exact imbalance a policy subject

Dôveryhodný experiment identifikuje original population, sampled training population a decision policy oddelene. Jedno pole `class_balance: 50/50` nestačí, pretože nehovorí, či ide o reality, training transform alebo evaluation reweighting.

```yaml
imbalance_subject: ML-PAY-IMB-2026-08-v4
population:
  source_manifest: eu-cnp-mature-2026w20-w30-v3
  observation_unit: payment_operation_id
  positive_class: recoverable_loss
  natural_prevalence: 0.0053
split:
  generation: grouped-temporal-v4
  group_key: merchant_id
  test_window: 2026w29-w30
training:
  sampler: random_undersample_negative
  sampling_strategy: 0.20
  class_weight: null
  pipeline_fit_scope: train_fold_only
model:
  artifact_digest: sha256:43a0...bc11
  output: uncalibrated_score
policy:
  generation: ML-PAY-THRESHOLD-2026-08-v7
  rule: top_k_with_minimum_score
  daily_capacity: 2500
  minimum_score: 0.172
  tie_breaker: payment_operation_id
acceptance:
  primary: captured_recoverable_loss_at_2500
  guards: [precision_at_2500, campaign_recall, queue_overflow_rate]
```

Sampler, class weight a threshold sú samostatné mutable inputs. Zmena jedného z nich vytvára successor generation aj vtedy, keď model family zostane rovnaká.

## 3. Natural prevalence a sampled prevalence

Natural prevalence je podiel positive observations v intended population podľa exact label contractu. Sampled prevalence je podiel v datasete po filtering, undersampling, oversampling alebo case-control sampling. Tieto hodnoty sa môžu zámerne líšiť.

```text
production: 0.53 % positive
training after undersampling: 20 % positive
validation/test: representative 0.52–0.55 % positive
```

Vyšší positive share môže zlepšiť optimization efficiency a zabezpečiť dostatok minority examples v batches. Zároveň mení empirical class prior, takže raw outputs nemusia byť calibrated pre production prior. Evaluation na balanced test sete by navyše vytvorila nerealistickú precision a action volume.

Prevalence sa reportuje po raw extraction, eligibility filters, label maturity, feature availability a successful inference. Každý filter môže selektívne odstrániť positives a vytvoriť skrytú imbalance zmenu.

## 4. Imbalance nie je jediná minority difficulty

Dve úlohy s rovnakou prevalence môžu mať úplne odlišnú náročnosť. Minority class môže byť dobre separable alebo prekrývajúca sa s majority class. Labels môžu byť noisy, positives heterogénne a niektoré minority subtypes úplne chýbať.

```text
class frequency
≠ class overlap
≠ label quality
≠ subgroup coverage
≠ decision cost
```

Pred voľbou technique sa analyzuje feature support, nearest-neighbor overlap, cohort counts, label maturity a error concentration. Viac syntetických alebo duplicitných samples nevytvorí informáciu pre missing subtype. Data acquisition, target redesign alebo segmented policy môžu byť relevantnejšie než resampling.

## 5. Stratification a jej hranice

Stratified split sa snaží zachovať class proportions v jednotlivých folds alebo partitions. To znižuje engineering problém foldov bez positives a stabilizuje metrics. Nezaručuje však statistical independence a nesmie porušiť group alebo time boundary.

```python
from sklearn.model_selection import StratifiedGroupKFold

cv = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=17,
)
for train_idx, valid_idx in cv.split(X, y, groups=merchant_id):
    ...
```

Ak rovnaký merchant vystupuje v train aj validation, samotná label stratification nezabráni entity leakage. Pri temporal deployment scenári môže random stratification trénovať na future patterns. Split authority má prioritu pred dokonalým vyrovnaním class counts; niektoré validné folds môžu mať prirodzene odlišnú prevalence.

## 6. Class weights a sample weights

Class weighting mení training objective tak, aby errors minority class mali vyššiu contribution. Pri binary loss sa často používa weight inversely related to class frequency alebo business cost. Weight však nie je nový sample ani nový label; mení gradient/objective.

```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(
    class_weight={0: 1.0, 1: 12.0},
    max_iter=2000,
)
```

`class_weight="balanced"` používa framework-specific formula založenú na observed training frequencies. Táto default formula nie je automaticky business-optimal a mení sa s sampled population. Ak sa zároveň použije oversampling a class weights, minority examples môžu byť efektívne zvýraznené dvakrát.

Sample weights umožňujú per-observation contribution, napríklad inverse sampling probability alebo business exposure. Population-correction weights a cost weights majú odlišný účel a nemajú sa zlúčiť bez explicitného estimandu.

## 7. Random undersampling

Undersampling odstráni časť majority examples. Znižuje compute a môže vyrovnať gradient contribution, ale zahadzuje informácie o majority diversity a hard negatives.

```text
all training negatives
→ deterministic sampling frame
→ retain all positives
→ sample subset of negatives
→ fit model
```

Sampler musí bežať iba nad training foldom a používať reproducible seed alebo stable hash. Ak sa undersampling vykoná pred splitom, duplicate/entity relationships a selection process môžu uniknúť do validation. Evaluation zostáva na natural alebo explicitne reweighted population.

Hard-negative mining môže byť účinnejší než uniform random removal, ale vytvára iterative selection procedure. Mining model, candidate pool a rounds patria do lineage a nesmú spotrebovať untouched test labels.

## 8. Random oversampling

Oversampling opakuje minority observations alebo vyberá minority samples s replacementom. Zachováva existujúce examples, ale nevytvára novú independent informáciu. Duplicitné rows zvyšujú effective weight a môžu podporiť memorization.

```python
from imblearn.over_sampling import RandomOverSampler
from imblearn.pipeline import Pipeline

pipeline = Pipeline([
    ("preprocess", preprocessor),
    ("resample", RandomOverSampler(random_state=17)),
    ("model", classifier),
])
```

Použitie pipeline je dôležité, aby resampling prebehol samostatne vo vnútri každého training foldu. Oversamplovať celý dataset pred cross-validation vytvára duplicates naprieč train a validation a dramaticky nadhodnocuje generalization.

## 9. Synthetic oversampling a SMOTE-like assumptions

SMOTE-like methods vytvárajú synthetic minority points interpoláciou medzi neighbors. Môžu rozšíriť local support, ale predpokladajú, že interpolation v feature space reprezentuje validný sample a že neighborhood nie je prekrývaný majority class alebo categorical constraints.

```text
minority point A + minority neighbor B
→ interpolated synthetic feature vector
→ assumed minority label
```

One-hot categorical combinations, temporal/event features, identifiers alebo constrained physical values môžu vytvoriť nemožné samples. Synthetic point nemá real-world observation ID ani nový ground truth. Method, feature representation, neighborhood, sampling strategy a random state patria do training generation.

Synthetic oversampling nie je vhodná náhrada za chýbajúce minority cohorty alebo label audit. Je to inductive bias, ktorý sa musí validovať na untouched representative data.

## 10. Data-level techniques a pipeline boundary

Preprocessing, feature selection a resampling musia byť fitted iba na training portion každého fold-u. Správny order závisí od method assumptions. Imputation a scaling môžu byť potrebné pred distance-based synthetic sampling, ale ich fit state nesmie vidieť validation data.

```text
fold train raw
→ fit imputer/encoder/scaler on fold train
→ transform fold train
→ fit sampler on transformed fold train
→ fit estimator

fold validation raw
→ transform through fold-fitted preprocessors
→ no resampling
→ predict and evaluate natural prevalence
```

Samplovať validation alebo test set kvôli „rovnakému balance“ mení estimand. Ak business chce metric pre hypothetical prevalence, používa sa explicitné reweighting alebo scenario analysis popri natural-population reporte.

## 11. Ensemble a algorithm-level alternatives

Niektoré algorithms podporujú class weights, balanced bootstrap alebo focal-like objectives. Tree ensembles môžu upraviť sampling per tree; boosting môže používať weighted loss; neural models môžu používať class/sample weights alebo focal loss.

Technique sa vyberá podľa optimization behavior a data constraints. Neexistuje pravidlo, že combined oversampling + class weights + threshold tuning je lepšie. Každý mechanism môže meniť ranking, calibration a variance. Controlled comparison fixuje split, features, budget a policy evaluation.

## 12. Metric portfolio pre imbalanced classification

Accuracy býva pri raritnej triede slabý primary signal. Report spravidla potrebuje per-class recall/precision, precision-recall curve, average precision, confusion counts pri production policy a capacity/cost metrics.

```yaml
metrics:
  model_level:
    - average_precision
    - roc_auc
    - log_loss
  policy_level:
    - precision_at_2500
    - recall_at_2500
    - false_positives_per_day
    - captured_recoverable_loss_at_2500
  guards:
    - campaign_recall
    - new_merchant_precision
    - inference_coverage
```

ROC AUC môže zostať useful discrimination evidence, ale veľký majority denominator môže prekryť operational false-positive count. Average precision závisí od prevalence. Preto sa každá metric interpretuje s supportom a action volume.

## 13. Threshold ako samostatný policy artifact

Threshold mapuje score alebo probability na class decision. Default `0.5` má zmysel iba pri konkrétnom probability a cost contracte; nie je property binary classification samotnej.

```python
score = model.predict_proba(X)[:, 1]
y_pred = score >= 0.183
```

Threshold generation identifikuje model artifact, validation prediction artifact, objective/cost function, constraints a selection method. Zmena threshold-u môže meniť precision, recall a queue volume bez zmeny ROC AUC alebo model digest.

```yaml
threshold_policy:
  id: ML-PAY-THRESHOLD-2026-08-v7
  model_digest: sha256:43a0...bc11
  source_predictions: validation-oof-v5.parquet
  objective: maximize_captured_loss
  constraints:
    false_positives_per_day_max: 2200
    campaign_recall_min: 0.45
  selected_threshold: 0.183
```

## 14. Threshold tuning bez evaluation leakage

Threshold sa nesmie vybrať na untouched test sete. Ak hyperparameters aj threshold používajú rovnaký validation signal opakovane, celý selection procedure môže overfitovať validation. Možnosti zahŕňajú oddelený threshold-tuning split, nested CV alebo out-of-fold predictions z training domain.

Current scikit-learn poskytuje `TunedThresholdClassifierCV`, ktorý post-tunes decision threshold cez cross-validation podľa zvoleného scoreru. Tool nemení potrebu správneho splitteru a independent acceptance.

```python
from sklearn.model_selection import TunedThresholdClassifierCV

thresholded = TunedThresholdClassifierCV(
    estimator=base_classifier,
    scoring="f1",
    cv=group_aware_cv,
)
thresholded.fit(X_train, y_train, groups=merchant_id_train)
```

Presný metadata-routing a `groups` support závisí od current API/configuration, preto production code musí byť overený proti pinned scikit-learn version. Conceptual boundary zostáva: fit/tune authority je training domain; untouched test iba akceptuje locked procedure.

## 15. Cost-sensitive threshold

Ak sú false-positive a false-negative costs známe alebo modelované, threshold sa môže vyberať minimalizáciou expected cost. Costs však často závisia od amount, cohort, capacity a downstream response, nie iba od class pair.

```text
expected cost(t) =
  FP_count(t) × cost_FP
+ FN_count(t) × cost_FN
+ review_volume(t) × review_cost
- recovered_value(t)
```

Static scalar cost matrix je approximation. Sensitivity analysis má ukázať, ako threshold reaguje na uncertain costs a prevalence. Policy nesmie používať budúci realized outcome, ktorý pri decision time nebol známy.

## 16. Capacity-constrained top-K policy

Keď downstream tím zvládne fixný počet cases, top-K selection môže byť autoritatívnejšia než scalar threshold. Daily volume však kolíše a score ties môžu meniť membership.

```text
eligible daily operations
→ score descending
→ minimum safety score
→ stable tie-breaker
→ first K operations
→ queue admission
```

Threshold + K hybrid odmietne low-confidence cases aj pri voľnej kapacite a zároveň chráni overload. Acceptance meria queue overflow, dropped-above-threshold count, age, cohort allocation a realized action rate. Offline top-K nad celým mesačným datasetom nemusí reprezentovať daily batching; evaluation musí simulovať production cadence.

## 17. Threshold, calibration a prevalence shift

Ak output je calibrated probability pre určitú population, threshold môže mať cost interpretation. Resampling, prior shift alebo calibration drift túto interpretation menia. Monotonic score môže stále dobre rankovať a pritom threshold volume výrazne zlyhať.

Prior correction alebo recalibration potrebuje explicitný model a valid assumptions. Blindly posunúť threshold podľa current positive rate môže vytvoriť feedback loop, pretože labels prichádzajú iba pre reviewed cases. Detailná calibration metodika patrí do kapitoly 21, ale threshold lifecycle už musí uchovávať calibration generation a population.

## 18. Multiclass a multilabel imbalance

Multiclass imbalance vyžaduje per-class metrics a policy pre one-vs-rest alebo joint class decision. Class weights môžu meniť boundaries medzi všetkými classes. Macro average zvýrazní minority classes, ale nezaručí minimum pre kritickú class.

V multilabel úlohe má každý label vlastnú prevalence, score distribution a často vlastný threshold. Joint capacity alebo incompatible actions môžu vyžadovať resolver nad per-label decisions.

```yaml
label_policies:
  fraud:
    threshold: 0.17
  account_takeover:
    threshold: 0.08
  policy_abuse:
    threshold: 0.31
resolver:
  max_actions_per_operation: 1
  priority: [account_takeover, fraud, policy_abuse]
```

Threshold vector a resolver sú jeden composite policy subject. Per-label tuning bez joint business simulation môže prekročiť shared capacity.

## 19. Feedback loops a selective labels

Threshold určuje, ktoré cases dostanú investigation, a tým aj ktoré cases získajú kvalitný ground truth. Zvýšenie threshold-u môže znížiť false positives, ale zároveň odstrániť evidence o lower-score positives. Offline retraining potom vidí selectively labeled population.

```text
model score
→ threshold/queue
→ investigated cases
→ observed labels
→ next training dataset
```

Random exploration, delayed external outcomes, inverse-propensity methods alebo audit samples môžu zmierniť selection bias. Exploration musí mať bezpečnostné a business boundaries. Bez feedback lineage sa apparent precision improvement môže skladať iba z užšieho reviewed population.

## 20. Worked incident `ML-PAY-87`

Atlas vytvoril balanced training extract a logoval iba field `class_balance=1:1`. Nebolo viditeľné, že negatives boli undersampled pred group splitom a rovnaké merchant bursts sa dostali do train aj validation. Neskôr sa použil RandomOverSampler vo vnútri notebooku a `class_weight="balanced"` v estimator-e, čo minority contribution zvýšilo viacerými mechanizmami.

Raw probabilities sa reportovali ako expected fraud probability, hoci training prior bol umelo zmenený a calibration nebola vykonaná na natural validation population. Threshold `0.5` produkoval príliš málo alerts, preto tím zvolil threshold maximalizujúci F2 na validation sete. Production však používala top 2 500 queue a extra merchant boost.

```text
balanced sampled training
→ weighted + oversampled objective
→ uncalibrated output
→ F2-selected threshold
→ hidden merchant boost
→ daily top-K truncation
```

Offline F2 sa zlepšil, ale cases nad thresholdom prekračovali capacity. Queue truncation preferentially zahodila late-day campaign traffic a effective campaign recall klesol. Root cause bol nesynchronizovaný training prior, probability claim a production policy, nie samotná rarity positives.

## 21. Competing failure hypotheses

Pri zlyhaní imbalanced classifiera alebo threshold policy treba rozlíšiť:

- label/prevalence drift — mature positive rate alebo class definition sa zmenila;
- split leakage — duplicates, groups alebo time relations prešli medzi partitions;
- double weighting — resampling, class weights a sample weights násobia minority contribution neplánovane;
- synthetic invalidity — generated points porušujú feature/domain constraints;
- ranking failure — minority cases dostávajú nižšie scores aj na natural population;
- calibration/prior failure — ranking je stabilný, ale probabilities alebo action volume sú nesprávne;
- threshold overfit — policy bola vybraná na opakovane spotrebovanej validation evidence;
- capacity mismatch — threshold acceptance ignoruje daily queue truncation alebo service rate;
- feedback bias — labels existujú prevažne pre predchádzajúcou policy vybrané cases;
- denominator failure — inference errors alebo unmatured labels sú ticho odstránené.

Každá hypothesis predpovedá inú stopu. Stabilný AP s prudkou zmenou predicted-positive volume podporuje threshold/calibration issue. Veľký CV gain, ktorý zmizne po group-aware pipeline resamplingu, podporuje leakage. Queue drop rate pri stabilných offline confusion counts ukazuje operational capacity mismatch.

## 22. Evidence-preserving containment a recovery

Containment zastaví promotion modelu alebo threshold policy, zachová original a sampled row IDs, sampler state, class/sample weights, raw scores, calibration artifact, threshold config a production queue logs. Approved model/policy zostáva aktívny, pokiaľ incident nevyžaduje bezpečnostné obmedzenie.

```text
freeze model and policy promotion
→ preserve natural and sampled populations
→ reconstruct fold-local preprocessing/resampling
→ recompute scores on representative data
→ separate ranking, calibration, threshold and queue evidence
→ test competing hypotheses
→ create corrected sampler/model/policy generation
→ independent-window and live-capacity acceptance
```

Ak bola chyba iba v threshold policy, netreba predstierať nový model artifact. Ak sampler leakoval, všetky dependent trials a threshold evaluations sa označia invalid. Recovery nevykonáva random resampling historického test setu, ale vytvorí successor experiment s novou independent acceptance boundary.

## 23. Acceptance contract

Positive acceptance identifikuje natural prevalence, sampled training prevalence, exact split, fold-local sampler, weighting, model output semantics, calibration state, threshold/top-K generation a downstream capacity. Evaluation obsahuje representative confusion counts, PR/ranking metrics, queue volume, mandatory cohort floors a coverage denominator.

Recovery acceptance reprodukuje sample membership a policy decision z immutable manifests. Forbidden paths zahŕňajú resampling validation/test setu, oversampling pred cross-validation, súčasné nezdokumentované weighting mechanisms, interpretáciu resampled outputu ako production probability, threshold tuning na untouched teste, offline monthly top-K bez daily simulation a odstránenie queue drops z recall denominatora.

Second-window test používa novšie mature natural-prevalence data s locked procedure. Second-operation test znovu aplikuje sampler, model a policy na tie isté manifests a overí deterministic membership, raw scores v tolerancii, selected threshold, daily queue composition a tie-breaking.

```yaml
acceptance:
  natural_and_sampled_prevalence_recorded: passed
  fold_local_sampler: passed
  model_and_policy_generations_separate: passed
  representative_metrics_and_queue_simulation: passed
  mandatory_cohort_floors: passed
  second_window: passed
```

## Kontrolné otázky

1. Prečo class imbalance nie je automaticky data-quality chyba?
2. Aký je rozdiel medzi natural a sampled prevalence?
3. Prečo stratification nenahrádza group/time-safe split?
4. Ako class weights menia objective a čím sa líšia od resampling-u?
5. Aké informácie zahadzuje random undersampling?
6. Prečo random oversampling nevytvára novú independent evidence?
7. Aké assumptions má SMOTE-like interpolation?
8. Prečo sampler musí byť vo vnútri CV pipeline?
9. Ktoré metrics sú užitočné pri raritnej positive class a prečo jeden metric nestačí?
10. Prečo threshold `0.5` nie je univerzálny?
11. Ako sa threshold tuning môže preučiť na validation data?
12. Kedy je top-K policy vhodnejšia než scalar threshold?
13. Ako prevalence a calibration ovplyvňujú action volume?
14. Prečo multilabel thresholds tvoria composite policy?
15. Ako threshold vytvára selective-label feedback loop?
16. Čo pokazilo lifecycle v `ML-PAY-87`?
17. Aké positive, recovery, forbidden a second-window testy uzatvárajú imbalance a policy contract?

## Glossary impact

Relevantné pojmy: class imbalance, natural prevalence, sampled prevalence, minority class, majority class, stratification, class weight, sample weight, random undersampling, hard-negative mining, random oversampling, synthetic oversampling, SMOTE, fold-local resampling, balanced ensemble, threshold policy, threshold tuning, cost-sensitive decision, top-K policy, queue capacity, prior shift, selective labels, exploration sample, denominator lineage a imbalance acceptance contract.

## Primárne zdroje

- [scikit-learn — Tuning the decision threshold for class prediction](https://scikit-learn.org/stable/modules/classification_threshold.html)
- [scikit-learn — `TunedThresholdClassifierCV`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TunedThresholdClassifierCV.html)
- [scikit-learn — Classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics)
- [scikit-learn — `StratifiedGroupKFold`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html)
- [imbalanced-learn — User guide and API](https://imbalanced-learn.org/stable/user_guide.html)
- [imbalanced-learn — Pipeline](https://imbalanced-learn.org/stable/references/generated/imblearn.pipeline.Pipeline.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Regression metrics](regression-metrics.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Cross-validation →](cross-validation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
