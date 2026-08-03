# Classification metrics

Classification metric nie je univerzálne číslo kvality modelu. Je to funkcia nad presne určeným evaluation datasetom, label generation, prediction artifactom, decision thresholdom, class semantics a aggregation policy. Rovnaký model môže mať vysokú accuracy, slabý recall pre kritickú triedu, dobrý ROC AUC a zároveň nepoužiteľný top-K outcome pri obmedzenej kapacite operátorov. Dôveryhodná evaluácia preto nezačína výberom obľúbenej metriky, ale business rozhodnutím, ktoré má prediction podporiť, a dôsledkami false positive a false negative chýb.

Incident `ML-PAY-87` vznikol pri Atlas Payments risk modeli. Produkčný dashboard hlásil `99.4 % accuracy`, pretože iba približne 0.5 % operácií malo mature positive label. Model však pri thresholde `0.5` zachytil menej než tretinu skutočne obnoviteľných strát. Iný report ukázal ROC AUC `0.96`, ale analytický tím mohol denne preskúmať iba 2 500 operácií a v tomto top-K sa dominantná hodnota sústreďovala v jednom známom merchant cohort-e. Weighted F1 prekryl nulový recall pre nový campaign cohort a average precision sa porovnávala medzi datasetmi s odlišnou prevalence. Kapitola preto oddeľuje score, probability, class decision, ranking a business action ako rôzne subjects.

## 1. Dominantný classification-evaluation lifecycle

Classification evaluation má lifecycle od target conceptu až po business consequence. Najprv sa uzamkne populácia a label maturity, potom sa načíta exact model artifact a vytvoria sa raw scores alebo probabilities. Decision policy z nich vytvorí classes, top-K queue alebo abstention. Až potom sa počítajú confusion-derived, ranking, probability a business metrics po relevantných slices.

```text
business decision a error cost
→ exact population, observation unit a mature label generation
→ exact model/preprocessing artifact
→ raw score, decision_function alebo probability
→ threshold/top-K/abstention policy
→ predicted class a downstream action
→ confusion, ranking, probability a cohort metrics
→ uncertainty a competing hypotheses
→ promotion, threshold recovery alebo rejection
→ second-cohort business acceptance
```

Tento chain zabraňuje tomu, aby sa threshold-dependent F1 porovnával s threshold-free ROC AUC ako keby merali rovnakú vec. Zároveň oddeľuje model discrimination od policy, ktorá rozhoduje, koľko prípadov sa reálne eskaluje.

## 2. Exact evaluation subject

Každý report musí identifikovať rovnakú evaluation generation. Bez nej nemožno zistiť, či rozdiel metrík vznikol modelom, datasetom, label maturity, thresholdom alebo aggregation policy.

```yaml
evaluation_subject: ML-PAY-CLS-EVAL-2026-08-v4
model_artifact:
  run_id: ML-PAY-HPO-2026-08-v6
  digest: sha256:8b7c...91d2
  feature_schema: risk-v9
population:
  dataset_manifest: eu-cnp-mature-2026w27-w30-v3
  observation_unit: payment_operation_id
  label_maturity_days: 21
  positive_class: recoverable_loss
predictions:
  raw_artifact: s3://ml-evals/87/predictions.parquet
  value: positive_class_probability
policy:
  threshold: 0.183
  daily_capacity: 2500
aggregation:
  averaging: macro_and_per_class
  sample_weight: recoverable_loss_eur
slices:
  - country
  - merchant_novelty
  - campaign_traffic
  - model_score_decile
```

Model digest sám neidentifikuje verdict. Threshold, positive-class meaning, sample weights a dataset manifest sú samostatné mutable inputs. Report bez nich je iba číslo bez reprodukovateľného subjectu.

## 3. Score, probability, class a action

Classifier môže emitovať raw decision score, estimated probability alebo priamo class label. Tieto outputs majú odlišné semantics. Monotonic transformation score-u môže zachovať ranking a ROC AUC, ale zmeniť probability calibration, log loss a threshold `0.5` decision.

```python
scores = model.decision_function(X_eval)
probabilities = model.predict_proba(X_eval)[:, positive_index]
classes = probabilities >= selected_threshold
priority = probabilities.argsort()[::-1][:daily_capacity]
```

`predict()` používa model-specific default decision rule. Úspešný call nepreukazuje, že default threshold reprezentuje business cost alebo operational capacity. Evaluation musí uložiť raw prediction artifact, aby bolo možné oddelene znovu vypočítať threshold a ranking metrics bez opakovania inference.

## 4. Confusion matrix ako count authority

Pre binary classification confusion matrix rozdeľuje evaluation population na true positive, false positive, false negative a true negative. Tieto counts sú základom threshold-dependent metrík a musia byť viazané na konkrétny threshold, positive class a sample population.

```text
                 predicted positive   predicted negative
actual positive          TP                  FN
actual negative          FP                  TN
```

Confusion matrix v sample counts a confusion matrix vo weighted business value nie sú rovnaké. Jeden false negative s vysokou stratou môže byť ekonomicky dôležitejší než stovky malých prípadov. Preto sa popri unweighted counts môže vypočítať aj cost-weighted outcome, ale weights nesmú spätne meniť význam labelu.

```python
from sklearn.metrics import confusion_matrix

counts = confusion_matrix(y_true, y_pred, labels=[0, 1])
weighted = confusion_matrix(
    y_true,
    y_pred,
    labels=[0, 1],
    sample_weight=recoverable_loss_eur,
)
```

## 5. Accuracy, error rate a balanced accuracy

Accuracy je podiel správnych class decisions. Je zmysluplná iba vtedy, keď má každá pozorovaná chyba približne rovnakú hodnotu a class prevalence v evaluation datasete reprezentuje produkčný scenár. Pri raritnej positive class môže trivial classifier dosiahnuť vysokú accuracy tým, že vždy predikuje negative.

```text
accuracy = (TP + TN) / (TP + TN + FP + FN)
error rate = 1 - accuracy
```

Balanced accuracy pri binary alebo multiclass úlohe priemeruje recall jednotlivých tried, takže majoritná trieda nemôže sama dominovať výsledku. Ani balanced accuracy však nezachytáva cost asymmetry, ranking quality alebo probability calibration. Je to lepší class-balance summary, nie automatický business objective.

## 6. Precision, recall, specificity a negative predictive value

Precision odpovedá, aký podiel predicted positives je skutočne positive. Recall alebo sensitivity odpovedá, aký podiel actual positives model zachytil. Specificity meria podiel správne odmietnutých negatives a negative predictive value opisuje spoľahlivosť predicted negative decisions.

```text
precision = TP / (TP + FP)
recall    = TP / (TP + FN)
specificity = TN / (TN + FP)
NPV = TN / (TN + FN)
```

Precision závisí od prevalence. Rovnaká conditional score behavior môže pri zmene base rate viesť k inej precision. Recall je voči jednoduchému prior shiftu stabilnejší iba za podmienky, že conditional distributions a threshold behavior zostali rovnaké. Report musí preto uviesť class support a cohort/time slice, nie iba percento.

V Atlas incidente vysoká precision v known-merchant cohort-e nekompenzovala nízky recall v campaign traffic. Aggregate metric prekryla presne tú populáciu, pre ktorú bol model nasadený.

## 7. F1 a všeobecný F-beta score

F1 je harmonický priemer precision a recall. Penalizuje situáciu, keď je jedna z nich veľmi nízka, ale implicitne im dáva rovnakú váhu a ignoruje true negatives.

```text
F1 = 2 × precision × recall / (precision + recall)
```

F-beta umožňuje zvýrazniť recall pri `beta > 1` alebo precision pri `beta < 1`. Výber beta musí vychádzať z decision costu, nie z toho, ktorá hodnota vyprodukuje lepší report.

```python
from sklearn.metrics import fbeta_score

f2 = fbeta_score(y_true, y_pred, beta=2.0, pos_label=1)
```

F-score je threshold-dependent a môže mať viac lokálnych maxím. Threshold vybraný na rovnakom datasete, na ktorom sa reportuje finálny F-score, spotrebúva evaluation evidence a vytvára optimistic selection bias.

## 8. ROC curve a ROC AUC

ROC curve mení threshold a zobrazuje true-positive rate proti false-positive rate. ROC AUC možno interpretovať ako ranking discrimination: pravdepodobnosť, že náhodný positive sample dostane vyšší score než náhodný negative sample, pri štandardných assumptions a tie handlingu.

```python
from sklearn.metrics import roc_curve, roc_auc_score

fpr, tpr, thresholds = roc_curve(y_true, y_score, pos_label=1)
auc = roc_auc_score(y_true, y_score)
```

ROC AUC nepoužíva jeden production threshold a môže pôsobiť optimisticky pri extrémnej imbalance, pretože veľký počet true negatives drží false-positive rate nízky aj pri absolútne vysokom počte false positives. Partial AUC cez deklarovaný `max_fpr` môže byť relevantnejší, ak business toleruje iba úzky false-positive region. Ani partial AUC však nenahrádza konkrétny capacity alebo cost verdict.

ROC AUC je invariantná voči monotonic transformation score-u, takže nepreukazuje calibrated probabilities. Dva modely s rovnakým AUC môžu mať výrazne odlišný log loss a threshold behavior.

## 9. Precision-recall curve a average precision

Precision-recall curve ukazuje trade-off medzi precision a recall pri meniacom sa thresholde. Pri raritnej positive class je často informatívnejšia než ROC curve, pretože priamo zobrazuje kvalitu predicted-positive population.

```python
from sklearn.metrics import precision_recall_curve, average_precision_score

precision, recall, thresholds = precision_recall_curve(y_true, y_score)
ap = average_precision_score(y_true, y_score)
```

Average precision sumarizuje precision ako funkciu recallu podľa definície implementácie. Nie je to jednoduchá trapezoidálna plocha každej PR vizualizácie a nemá sa nejasne označovať ako univerzálne „PR AUC“. Baseline AP súvisí s positive prevalence, preto porovnanie AP medzi datasetmi s inou class balance potrebuje explicitný kontext alebo reweighting experiment.

Pre Atlas bolo dôležitejšie `precision@2500`, `recall@2500` a captured recoverable loss v daily queue než AP cez celý threshold range. AP zostala model-level ranking summary, nie operational acceptance.

## 10. Log loss a probability quality

Log loss používa predicted probabilities a silno penalizuje confident wrong predictions. Pri binary classification ide o priemernú negative log-likelihood; pri multiclass o zodpovedajúcu cross-entropy.

```python
from sklearn.metrics import log_loss

loss = log_loss(y_true, y_proba, labels=[0, 1])
```

Log loss potrebuje probability-like input v správnom class orderi. Raw logits alebo decision scores sa nesmú poslať do API ako probabilities. Nižší log loss znamená lepší probabilistic fit podľa tejto scoring rule, ale sám neurčuje threshold, top-K capacity ani fairness guardrails.

Extrémne confident errors môžu dominovať lossu. To je zamýšľaná vlastnosť, nie dôvod na odstránenie problematických samples bez label audit-u. Detailná calibration a uncertainty analýza patrí do samostatnej kapitoly 21.

## 11. Multiclass confusion a averaging

Pri multiclass úlohe sa per-class precision, recall a F-score počítajú one-vs-rest. Výsledok sa potom môže agregovať viacerými spôsobmi:

- `macro` — neweighted priemer per-class metrík, ktorý dáva každej triede rovnaký hlas;
- `weighted` — priemer vážený class supportom, ktorý môže prekryť slabú minoritnú triedu;
- `micro` — agreguje TP/FP/FN counts pred výpočtom a zvýrazňuje sample-level majoritný outcome;
- per-class report — zachováva presný failure mode a nemá sa nahradiť iba jedným priemerom.

Tieto averages nie sú kozmetické presentation options. Menia otázku, na ktorú metric odpovedá. Production gate má spravidla kombinovať global summary s mandatory per-class a cohort floors.

```python
from sklearn.metrics import precision_recall_fscore_support

per_class = precision_recall_fscore_support(
    y_true,
    y_pred,
    labels=class_order,
    average=None,
    zero_division=0,
)
macro_f1 = precision_recall_fscore_support(
    y_true,
    y_pred,
    labels=class_order,
    average="macro",
    zero_division=0,
)[2]
```

`zero_division=0` zabráni runtime warningu alebo undefined value, ale neodstraňuje failure. Trieda bez predicted positives musí byť v report-e označená ako coverage incident, nie ticho interpretovaná ako normálna nula.

## 12. Multilabel metrics a sample identity

V multilabel classification môže jeden sample niesť viac labels. Subset accuracy vyžaduje presnú zhodu celého label setu a býva veľmi prísna. Hamming loss hodnotí jednotlivé label decisions, zatiaľ čo sample-averaged precision/recall agregujú najprv na úrovni sample.

```text
sample A actual:    {fraud, account_takeover}
sample A predicted: {fraud}
```

Tento sample je pre subset accuracy nesprávny, ale per-label fraud decision je správny. Výber metriky musí zodpovedať tomu, či downstream action pracuje s celým label setom alebo samostatnými labels. Každý label môže mať vlastný threshold a support, čo vytvára policy generation, ktorú treba versionovať.

## 13. Top-K, lift a capacity-constrained metrics

Keď operátor alebo systém dokáže konať iba nad K prípadmi, threshold-free globálne metriky nestačia. Evaluation musí zoradiť exact score artifact, definovať tie-breaking a potom merať precision@K, recall@K, captured value@K, lift oproti random alebo baseline policy a cohort coverage v queue.

```python
import numpy as np

order = np.argsort(-y_score, kind="stable")
top = order[:2500]
precision_at_k = y_true[top].mean()
captured_loss_at_k = recoverable_loss_eur[top][y_true[top] == 1].sum()
```

Stable sort a operation ID tie-breaker sú dôležité pre reprodukovateľnosť. Optimalizovať iba captured monetary value môže vytlačiť nízkovýnosné, ale regulačne povinné cohorts, preto sa používajú guardrails alebo constrained allocation.

## 14. Sample weights, support a denominator integrity

`sample_weight` mení contribution jednotlivých samples. Môže reprezentovať population reweighting, business value alebo survey design, ale tieto účely sa nesmú miešať v jednom neoznačenom vektore. Weighted metric musí reportovať weighted aj raw support, aby bolo jasné, či gain nevznikol cez niekoľko extrémnych observations.

```yaml
metric_variant:
  name: recall
  sample_weight: none
  denominator: mature_positive_operations

business_variant:
  name: captured_recoverable_loss
  weight_column: recoverable_loss_eur
  denominator: total_mature_recoverable_loss_eur
```

Missing labels, filtered samples a unknown outcomes menia denominator. Evaluation pipeline musí uviesť počty od raw population cez eligibility, feature availability, inference success až po mature labeled set. Metric nad preživšími successful predictions nepreukazuje end-to-end model coverage.

## 15. Uncertainty, slices a paired comparison

Point estimate bez variability môže preceňovať malý gain. Confidence interval alebo bootstrap musí rešpektovať nezávislú jednotku: pri viacerých retry attempts alebo operáciách jedného merchantu sa resampluje group, nie jednotlivé riadky. Time-dependent data potrebuje blocked alebo temporal comparison.

Pri porovnaní dvoch modelov sa používajú paired predictions na rovnakých samples. Rozdiel metric sa bootstrapuje ako paired difference; dva nezávislé intervaly sú menej citlivý dôkaz. Aggregate gain sa vždy rozloží podľa mandatory cohorts a threshold/capacity regionu.

```text
same evaluation operations
→ score from candidate A and B
→ identical policy generation
→ paired metric differences
→ grouped/time-aware uncertainty
→ cohort and failure review
```

## 16. Metric selection ako decision contract

Metric portfolio sa odvodzuje od action semantics. Medical screening alebo security detection môže požadovať recall floor a následne minimalizovať false positives. Capacity queue potrebuje precision/recall/value at K. Automated denial môže vyžadovať calibration, strict false-positive limits, explainability a cohort guardrails. Multiclass routing potrebuje per-class recall a confusion between specific costly pairs.

Jedna primary selection metric môže riadiť experiment, ale promotion gate potrebuje guardrails. Je chybou po výsledkoch vybrať metriku, na ktorej candidate vyzerá najlepšie; metric contract sa uzamyká pred untouched test evaluation.

## 17. Worked incident `ML-PAY-87`

Atlas report skombinoval štyri nekompatibilné verdicts. Accuracy používala threshold `0.5`, ROC AUC raw scores, average precision dataset s oversampled positives a weighted F1 triedy vážené supportom. Business queue však vyberala top 2 500 operations po ďalšom merchant-priority booste. Žiadna metrika teda nehodnotila skutočný production decision path.

```text
model probability
→ hidden merchant boost
→ top-2500 queue
→ analyst action
→ recovered loss
```

Known merchants dominovali positive labels aj monetary weights. Campaign cohort mal recall `0.08`, ale weighted F1 zostal vysoký. Časť high-score predictions nemala mature labels a bola z reportu odstránená, takže denominator ignoroval serving coverage failure.

Root cause nebola „zlá accuracy“ sama osebe. Root cause bol neidentifikovaný evaluation subject, zmiešané populations, rozdielna policy medzi reportom a produkciou a aggregate-only acceptance.

## 18. Competing failure hypotheses

Pri zhoršenej classification metrike treba pred mutáciou rozlíšiť aspoň tieto mechanisms:

- label-generation failure — positive labels sú oneskorené, neúplné alebo zmenili definíciu;
- population shift — prevalence alebo conditional feature distribution sa zmenila v čase či cohort-e;
- ranking regression — positive samples dostávajú nižší relative score aj bez zmeny calibration;
- calibration regression — ranking zostal podobný, ale probabilities a threshold semantics sa posunuli;
- policy regression — model artifact je rovnaký, no threshold, top-K alebo downstream boost sa zmenil;
- coverage failure — inference errors alebo missing features odstránili ťažké samples z denominatora;
- aggregation masking — macro, weighted alebo micro average prekrýva povinnú triedu alebo cohort;
- implementation mismatch — class order, positive label, score column alebo tie-breaking sa interpretujú nesprávne.

Každá hypotéza predpovedá iný evidence pattern. Stabilný ROC AUC so zhoršeným log loss podporuje calibration hypothesis; stabilné raw predictions s inou confusion matrix ukazujú policy zmenu; zhoršenie iba po zahrnutí failed inference rows odhaľuje coverage problém.

## 19. Evidence-preserving containment a recovery

Containment zmrazí promotion a zachová raw prediction artifact, model digest, dataset manifest, label snapshot, threshold/policy config a report code SHA. Produkčný model sa nemení iba preto, že jeden dashboard klesol. Najprv sa reprodukujú counts a metrics z immutable artifactu a porovnajú sa s production queue generation.

```text
freeze candidate promotion
→ preserve predictions, labels, policy a report code
→ reconcile population/denominators
→ recompute per-class, threshold-free, threshold a top-K metrics
→ slice by time/cohort/coverage
→ test competing hypotheses
→ correct evaluation alebo create successor model/policy
→ independent acceptance
```

Ak bol chybný iba report, recovery opraví evaluation pipeline a historický verdict označí ako invalid. Ak bol chybný threshold, vznikne successor policy generation bez premenovania modelu. Ak model reálne regresoval, rollback zostáva na predchádzajúcom approved artifacte a nový training run dostane vlastnú lineage.

## 20. Acceptance contract

Positive acceptance preukazuje exact model, population, label maturity, class order, raw prediction type, threshold alebo top-K policy, averaging, support a mandatory cohorts. Report obsahuje confusion counts, relevantné ranking/probability metrics, business outcome proxy a uncertainty.

Recovery acceptance reprodukuje opravený report z immutable predictions a dokazuje, že production policy používa rovnakú generation. Forbidden paths zahŕňajú threshold tuning na untouched teste, porovnanie AP cez neporovnateľnú prevalence bez vysvetlenia, weighted average bez per-class floor, odstránenie inference failures z denominatora a zamieňanie ROC AUC za probability calibration.

Second-cohort test používa novšie mature labels a rovnaký locked metric/policy contract. Second-operation test znovu vypočíta report z toho istého prediction artifactu a musí vytvoriť identické counts, class ordering, thresholds, top-K membership a zaokrúhľovanie okrem explicitne povolenej numerickej tolerancie.

```yaml
acceptance:
  exact_subject: passed
  prediction_artifact_reproducible: passed
  per_class_and_cohort_floors: passed
  top_k_business_guardrail: passed
  coverage_denominator_complete: passed
  untouched_test_not_reused_for_tuning: passed
  second_cohort: passed
```

## Kontrolné otázky

1. Prečo accuracy môže byť pri raritnej positive class zavádzajúca?
2. Aký je rozdiel medzi raw score, probability, predicted class a business action?
3. Čo presne dokazujú precision, recall, specificity a NPV?
4. Prečo F1 nie je automatický business objective?
5. Kedy je ROC AUC menej informatívna než precision-recall analýza?
6. Prečo average precision nemožno bez kontextu porovnávať medzi populáciami s inou prevalence?
7. Čo log loss meria a čo neurčuje?
8. Ako sa macro, weighted a micro averaging líšia?
9. Prečo `zero_division=0` neuzatvára coverage failure?
10. Ako sa multilabel subset accuracy líši od Hamming-like evaluation?
11. Kedy treba používať top-K a captured-value metrics?
12. Ako sample weights menia interpretation metricu?
13. Prečo sa inference failures musia zahrnúť do denominator lineage?
14. Ako paired comparison zlepšuje dôkaz oproti dvom nezávislým score reportom?
15. Čo pokazilo evaluation lifecycle v `ML-PAY-87`?
16. Aké positive, recovery, forbidden a second-cohort testy uzatvárajú classification evaluation?

## Glossary impact

Relevantné pojmy: classification evaluation subject, positive class, raw score, decision function, probability, threshold, top-K policy, confusion matrix, true positive, false positive, false negative, true negative, accuracy, balanced accuracy, precision, recall, sensitivity, specificity, negative predictive value, F1, F-beta, ROC curve, ROC AUC, partial AUC, precision-recall curve, average precision, log loss, class support, macro/micro/weighted averaging, multilabel classification, subset accuracy, Hamming loss, precision@K, recall@K, lift, sample weight, denominator lineage, paired comparison a classification acceptance contract.

## Primárne zdroje

- [scikit-learn — Metrics and scoring: classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics)
- [scikit-learn — `precision_recall_fscore_support`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html)
- [scikit-learn — `roc_auc_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html)
- [scikit-learn — `precision_recall_curve`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_curve.html)
- [scikit-learn — `average_precision_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
- [scikit-learn — `log_loss`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.log_loss.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Hyperparameters a hyperparameter optimization](hyperparameters-hyperparameter-optimization.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Regression metrics →](regression-metrics.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
