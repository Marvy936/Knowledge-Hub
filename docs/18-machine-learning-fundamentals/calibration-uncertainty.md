# Calibration a uncertainty

Model score, predicted probability a uncertainty estimate nie sú synonymá. Ranking score môže správne zoradiť cases bez toho, aby hodnota `0.8` znamenala približne osemdesiatpercentnú frekvenciu udalosti. Calibrated probability môže byť spoľahlivá pre jednu population a time window, no zlyhať po prevalence alebo conditional shift-e. Úzky prediction interval môže byť numericky reprodukovateľný a pritom nemať deklarované coverage na novom cohort-e. Dôveryhodný uncertainty lifecycle preto identifikuje, aký typ outputu vznikol, na akej evidence bol fitted, aký event alebo target opisuje a akú decision authority downstream systém z neho odvodzuje.

Incident `ML-PAY-88` vznikol pri Atlas Payments risk platforme. Fraud classifier mal stabilný ranking a ROC AUC, ale dashboard zobrazoval raw tree-ensemble probabilities ako absolútne riziko. Kalibrátor bol fitted na predictions z rovnakých rows, na ktorých sa fitoval classifier, a reliability diagram používal päť uniform bins, z ktorých tri zostali takmer prázdne. Global expected calibration error vyzeral nízko, no campaign traffic bol výrazne overconfident. Reserve-sizing model zároveň publikoval p95 prediction ako „95 % confidence interval“, hoci išlo o samostatný conditional quantile bez lower boundu a bez coverage testu. Tím preto zamieňal discrimination, calibration, interval coverage, epistemic uncertainty a business confidence.

## 1. Dominantný calibration a uncertainty lifecycle

Calibration nie je dekorácia po trainingu. Vzniká ako samostatná fitted transformácia alebo ako property probabilistic modelu a potrebuje vlastnú split, artifact a acceptance lineage. Uncertainty output sa potom interpretuje iba v rámci deklarovaného population a decision contractu.

```text
business event, target a action cost
→ exact model output semantics
→ independent calibration alebo uncertainty-fit evidence
→ fitted model + calibrator/interval procedure generation
→ probability, quantile, interval alebo abstention output
→ reliability, proper-score, coverage a sharpness evaluation
→ cohort/time/OOD stress tests
→ threshold, reserve alebo human-review action
→ drift, containment a recalibration/retraining recovery
→ second-window acceptance
```

Tento chain oddeľuje tri otázky. Discrimination sa pýta, či model zoradí observations. Calibration sa pýta, či numeric probabilities zodpovedajú observed frequencies. Uncertainty sa pýta, aký rozsah alebo confidence má prediction za deklarovaných assumptions. Business policy sa pýta, čo sa má s outputom urobiť.

## 2. Exact calibration subject

Calibration verdict musí identifikovať base estimator, raw response, calibration method, split a target event. Bez týchto polí nemožno rozlíšiť zmenu classifiera od zmeny calibratora alebo population.

```yaml
calibration_subject: ML-PAY-CAL-2026-08-v5
base_model:
  run_id: ML-PAY-HPO-2026-08-v8
  digest: sha256:1f92...b0c4
  response: decision_function
population:
  dataset_manifest: eu-cnp-mature-2026w21-w30-v4
  observation_unit: payment_operation_id
  positive_event: recoverable_loss_within_21d
split:
  generation: grouped-temporal-calibration-v3
  base_fit_window: 2026w10-w24
  calibration_window: 2026w25-w27
  acceptance_window: 2026w28-w30
calibrator:
  method: sigmoid
  artifact_digest: sha256:8a17...71e3
  class_order: [no_loss, recoverable_loss]
evaluation:
  bins: [quantile_10, uniform_20]
  proper_scores: [log_loss, brier_score]
  mandatory_slices: [campaign_traffic, new_merchant, country]
```

Base-model digest a calibrator digest tvoria composite inference subject. Zmeniť calibration method alebo calibration population bez nového artifact ID je rovnaká lineage chyba ako prepísať model weights.

## 3. Ranking score oproti probability

Mnohé classifiers produkujú decision score alebo margin. Jeho poradie môže byť informatívne, ale scale nemá automatický probability význam. Aj `predict_proba` je iba output podľa training objective a estimator assumptions; názov API nepreukazuje empirical calibration na intended population.

```python
raw_score = classifier.decision_function(X_eval)
raw_probability = classifier.predict_proba(X_eval)[:, positive_index]
```

Monotonic transformácia zachová ranking a ROC AUC, ale zmení log loss, Brier score a threshold semantics. Preto sa raw score artifact zachováva oddelene od calibrated probability artifactu. Downstream komponent nesmie neoznačene kombinovať score z jednej generation s thresholdom fitovaným na inej probability scale.

## 4. Empirical calibration a reliability diagram

Binary reliability diagram rozdelí predicted probabilities do bins a porovná mean predicted probability s observed positive frequency. Ideálny calibrated model leží približne na diagonále, ale finite sample variability, binning a label delay vytvárajú neistotu.

```python
from sklearn.calibration import calibration_curve

fraction_positive, mean_predicted = calibration_curve(
    y_true,
    y_probability,
    pos_label=1,
    n_bins=10,
    strategy="quantile",
)
```

`strategy="uniform"` rozdeľuje interval `[0, 1]` na rovnako široké bins; `quantile` sa snaží vložiť podobný počet samples do každého binu. Empty uniform bins sa nevracajú, preto počet points nemusí byť `n_bins`. Viac bins zvyšuje rozlíšenie, ale znižuje support v každom bode.

Reliability diagram bez histogramu predicted probabilities je neúplný. Model môže vyzerať dobre calibrated iba preto, že takmer všetky predictions sú blízko base rate a high-risk region nemá evidence. Report preto uvádza bin counts, confidence intervals alebo bootstrap variability a mandatory cohorts.

## 5. Calibration error summaries a ich hranice

Expected calibration error-like summaries vážia absolute bin gap podľa supportu. Sú citlivé na počet bins, boundaries a sample composition. Dva modely môžu zmeniť ordering iba kvôli binningu a aggregate ECE môže prekryť kritický high-risk region.

```text
bin gap_b = |observed_frequency_b - mean_probability_b|
ECE = sum_b (support_b / total_support) × gap_b
```

ECE nie je strictly proper scoring rule a nemá sa používať ako jediný model-selection objective. Report musí uložiť exact implementation, binning strategy a empty-bin behavior. Adaptive alebo classwise variants odpovedajú na iné otázky a nesmú zdieľať rovnaký metric name.

Maximum calibration error zvýrazní najhorší bin, ale je nestabilný pri malom supporte. Calibration slope a intercept môžu odhaliť global overconfidence alebo offset, no nezachytia local nonlinearity. V praxi sa používa portfolio vizualizácie, proper scores, region-specific gaps a business action simulation.

## 6. Brier score a log loss

Brier score pre binary event je mean squared difference medzi probability a observed outcome. Log loss penalizuje confident wrong predictions výraznejšie. Obe sú proper scoring rules pre probabilistic predictions, takže odmeňujú pravdivé probability estimates v expectation za príslušných assumptions.

```python
from sklearn.metrics import brier_score_loss, log_loss

brier = brier_score_loss(
    y_true,
    y_probability,
    pos_label=1,
)
logloss = log_loss(
    y_true,
    probability_matrix,
    labels=class_order,
)
```

Nižší Brier score alebo log loss nemusí znamenať lepšiu calibration vo všetkých regiónoch, pretože score zároveň odráža resolution/discrimination a irreducible outcome uncertainty. Model, ktorý predikuje prevažne base rate, môže byť calibration-like stabilný, ale málo useful. Preto sa proper score interpretuje spolu s rankingom, reliability a business utility.

Current scikit-learn `brier_score_loss` podporuje binary aj multiclass probability shapes a explicitný class-label contract. Class column order musí byť uložený; numericky validná matrix s nesprávnym mappingom vytvorí presvedčivý, ale falošný verdict.

## 7. Sigmoid calibration

Sigmoid alebo Platt-like calibration fituje parametrické monotonic mapping medzi raw response a probability. Má nízku variance a môže fungovať pri menšom calibration sete, ale obmedzený shape nemusí opraviť komplexnú local miscalibration.

```text
raw response f(x)
→ fit parameters A, B
→ probability = sigmoid(A × f(x) + B)
```

Mapping sa fituje na predictions pre samples, ktoré base classifier nepoužil na fit. Ak classifier videl rovnaké rows, jeho in-sample scores sú príliš optimistické a calibrator sa môže stať overconfident. Group a temporal boundaries ostávajú rovnaké ako pri model evaluation.

Sigmoid calibration zachováva score ordering pri monotonic mappingu, ale threshold numeric value sa zmení. Threshold policy sa preto musí refitovať alebo revalidovať nad calibrated outputom, nie preniesť z raw scale.

## 8. Isotonic calibration

Isotonic regression fituje non-decreasing piecewise-constant mapping. Je flexibilnejšia než sigmoid, ale potrebuje viac calibration data a môže overfitovať sparse regions.

```python
from sklearn.calibration import CalibratedClassifierCV

calibrated = CalibratedClassifierCV(
    estimator=base_classifier,
    method="isotonic",
    cv=precomputed_group_time_splits,
    ensemble="auto",
)
calibrated.fit(X_train, y_train)
```

Isotonic mapping môže vytvoriť ties a tým mierne zmeniť ranking metrics. Flexibilný fit na malom high-risk sample môže produkovať extrémne steps. Acceptance preto porovnáva multiple windows, bin support a stability voči resamplingu.

Voľba isotonic nesmie vzniknúť až po pohľade na untouched test. Calibration method je hyperparameter/procedure decision a spotrebúva training-domain evidence.

## 9. Temperature scaling a multiclass calibration

Temperature scaling upravuje logits jedným positive temperature parametrom pred softmax. Pri multiclass outpute zachováva argmax ordering medzi classes pre sample, ale mení confidence concentration.

```text
calibrated_probability_k = softmax(logit_k / T)
```

`T > 1` typicky zjemňuje overconfident distribution; `T < 1` ju zaostruje. Jeden scalar nemôže opraviť class-specific alebo local miscalibration, no má nízku complexity a prirodzene zachová sum-to-one multiclass probabilities.

Current scikit-learn calibration API zahŕňa `method="temperature"`. Sigmoid a isotonic sa pri multiclass rozširujú one-vs-rest kalibráciou a následnou normalizáciou, čo má odlišné semantics. Method, logits/probability input a class order patria do artifact manifestu.

## 10. Cross-validated calibration a ensemble semantics

`CalibratedClassifierCV` používa cross-validation, aby calibrator dostal out-of-fold-like predictions namiesto in-sample outputs. Presný deployed artifact závisí od `ensemble` behavior. Ensemble variant môže obsahovať viac classifier-calibrator pairs; non-ensemble variant môže znížiť model size a latency.

```python
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedGroupKFold

splitter = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=29,
)
calibration_splits = list(
    splitter.split(X_train, y_train, groups=merchant_id_train)
)

model = CalibratedClassifierCV(
    estimator=base_pipeline,
    method="sigmoid",
    cv=calibration_splits,
    ensemble="auto",
)
model.fit(X_train, y_train)
```

Precomputed indices zachovávajú group boundary bez tvrdenia, že calibrator automaticky rozumie business entity. Pri temporal use case sa použijú forward splits alebo samostatný calibration window. Fold modely, calibrators a final composite digest sa musia dať inventarizovať a serializovať.

## 11. Calibration already-fitted modelu

Already-fitted estimator možno kalibrovať iba na disjoint data. Current scikit-learn používa `FrozenEstimator`, pričom zodpovednosť za disjointness zostáva na používateľovi.

```python
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator

frozen = FrozenEstimator(fitted_classifier)
calibrated = CalibratedClassifierCV(
    estimator=frozen,
    method="sigmoid",
)
calibrated.fit(X_calibration, y_calibration)
```

Tento pattern je vhodný, keď base artifact je immutable a calibration je samostatná successor policy/model vrstva. Je nebezpečný, ak calibration dataset prekrýva original training rows alebo vznikol selection cez test evidence. Manifest preto obsahuje row/group/time disjointness proof.

## 12. Prevalence a prior shift

Calibration je population-dependent. Pri zmene event prevalence sa predicted probabilities môžu stať miscalibrated aj pri podobnom ranking-u. Jednoduchá prior correction vyžaduje assumptions o stabilite class-conditional score distributions; v reálnom systéme sa často menia aj tie.

```text
stable rank discrimination
+ changed prevalence
→ changed positive predictive probability
→ threshold volume drift
```

Observed prevalence môže byť oneskorená alebo selective, pretože iba reviewed cases získajú labels. Blind online recalibration na immature labels vytvára feedback loop. Recalibration cadence sa viaže na mature outcome window, cohort coverage a minimum support.

Calibration drift sa monitoruje oddelene od data drift. Zmena feature distribution nepreukazuje probability miscalibration a stabilný feature drift metric nepreukazuje calibration stability.

## 13. Aleatoric a epistemic uncertainty

Aleatoric uncertainty opisuje variabilitu inherentnú v outcome pri dostupných informáciách, napríklad rovnaký observed feature state vedie k rôznym outcomes. Epistemic uncertainty opisuje neistotu modelu alebo knowledge z nedostatku relevantných dát, model assumptions alebo out-of-distribution inputov.

```text
aleatoric: outcome variability conditional on available evidence
epistemic: uncertainty about fitted function/procedure in poorly supported regions
```

Rozdelenie nie je vždy jednoznačne identifikovateľné z jedného modelu. Softmax entropy ani variance ensemble predictions nie sú universal epistemic truth. Output musí byť pomenovaný podľa procedure, napríklad `ensemble_probability_std`, nie genericky `model_confidence`.

Viac dát podobného typu môže znížiť epistemic uncertainty, ale nezmizne inherentný label noise. Zmena target definition alebo richer features môže znížiť observed aleatoric component, preto oba pojmy závisia od information setu.

## 14. Prediction intervals a quantiles

Regression point prediction nevyjadruje rozsah možných outcomes. Quantile model môže produkovať lower a upper conditional quantiles; interval medzi nimi sa interpretuje iba podľa trained quantile levels a empirical coverage.

```python
lower = quantile_model_05.predict(X_eval)
median = quantile_model_50.predict(X_eval)
upper = quantile_model_95.predict(X_eval)
interval = (lower, upper)
```

Interval `[q05, q95]` cieli približne na 90 % conditional alebo marginal coverage podľa model/procedure assumptions, nie 95 %. Samotný p95 point nie je confidence interval. Quantile crossing (`q05 > q50` alebo `q50 > q95`) je validity failure.

Coverage bez sharpness je triviálne splniteľná veľmi širokým intervalom. Sharp interval bez coverage je nebezpečný. Report preto obsahuje coverage, width distribution, tail/cohort slices a interval failure direction.

## 15. Conformal prediction ako procedure-level uncertainty

Conformal methods používajú calibration residuals alebo nonconformity scores na vytvorenie prediction sets/intervals s finite-sample marginal coverage za exchangeability-like assumptions. Coverage guarantee sa viaže na exact procedure a population, nie na každý individual sample alebo arbitrary subgroup.

```text
proper training data
→ fit base model
calibration data
→ compute nonconformity scores
→ select empirical quantile
new sample
→ create set/interval from model output + quantile
```

Group, time alebo covariate shift môže porušiť assumptions. Mondrian/group-conditional variants potrebujú dostatok supportu. Conformal set size je operational signal: prudký rast môže indikovať shift alebo slabú informatívnosť, ale nie automaticky root cause.

Kapitola nepovažuje conformal output za magickú certifikáciu. Calibration data, score function, alpha, tie handling a exchangeability boundary sú exact subject.

## 16. Ensembles a stochastic uncertainty proxies

Deep ensembles alebo repeated stochastic fits môžu merať variation predictions naprieč model instances. Variation závisí od initialization, data resampling, hyperparameters a optimization stochasticity. Ak všetky models zdieľajú rovnaký bias alebo missing cohort, nízka variance neznamená istotu.

```yaml
ensemble_uncertainty:
  members: 5
  data_generation: same_train_manifest_bootstrap_v2
  seeds: [11, 23, 37, 53, 71]
  output:
    mean_probability: true
    std_probability: true
```

Monte Carlo dropout alebo test-time stochastic methods majú vlastné theoretical a implementation assumptions. Production inference musí explicitne zapnúť intended stochastic behavior a zaznamenať počet samples. Nondeterministický bug nesmie byť premenovaný na uncertainty estimate.

## 17. Out-of-distribution a abstention

Uncertainty proxy môže pomôcť pri abstention, ale high confidence na OOD inpute je možná. OOD detection preto potrebuje samostatný subject, reference population a metric. Feature-distance, density, ensemble disagreement a softmax confidence merajú odlišné signals.

```text
input eligibility
→ OOD/novelty signals
→ model prediction + uncertainty
→ policy:
   accept automatically
   route to human review
   request more data
   reject as unsupported
```

Abstention mení denominator a business throughput. Reporting performance iba na accepted samples môže vyzerať lepšie tým, že systém odmieta ťažké cohorts. Acceptance obsahuje coverage/action rate, selective risk, cohort abstention a fallback outcome.

## 18. Uncertainty a decision policy

Probability a interval sa stávajú užitočnými až cez policy. Reserve sizing môže používať upper quantile; human review môže prioritizovať expected loss × uncertainty; automated action môže vyžadovať probability floor a low-OOD risk.

```yaml
decision_policy:
  auto_approve:
    max_loss_probability: 0.01
    max_ood_score: 0.12
  human_review:
    condition: probability_between_0_01_and_0_35_or_high_uncertainty
  block:
    min_loss_probability: 0.35
```

Policy objective musí rozlišovať expected risk a uncertainty. High predicted risk s low uncertainty a medium risk s high uncertainty môžu vyžadovať iný action. Kombinácia cez nezdokumentovaný heuristic vytvára nový model-like decision subject.

## 19. Worked incident `ML-PAY-88`

Atlas classifier bol fitted na w10–w27 a calibrator následne dostal predictions z tých istých rows. Reliability diagram preto meral in-sample confidence. Uniform bins obsahovali tisíce cases okolo `0.01`, ale high-risk bins mali desiatky samples. Aggregate ECE dominoval low-risk region a zakryl campaign overconfidence.

```text
same rows fit classifier
→ optimistic in-sample scores
→ fit isotonic calibrator
→ sparse high-risk steps
→ global ECE appears low
→ campaign threshold overload
```

Reserve model publikoval `q95` ako „95 % confidence interval“. Dashboard neukazoval lower bound, empirical coverage ani width. V new-merchant cohort-e observed target prekročil q95 v 19 % cases. Tím napriek tomu považoval interval za formálnu 95-percentnú garanciu.

Root cause nebol iba zlý calibrator. Incident spojil overlapping fit/calibration evidence, weak bin diagnostics, population shift, nepresný názov uncertainty outputu a policy, ktorá zamieňala probability s confidence.

## 20. Competing failure hypotheses

Calibration alebo uncertainty incident sa diagnostikuje podľa vrstvy, v ktorej sa evidence rozchádza. Najprv sa porovná raw response, calibrator mapping, class order, population/label maturity, bin support, interval procedure a downstream policy. Každá hypotéza musí predpovedať odlišný signal.

- in-sample calibration leakage — calibrator videl responses z rows použitých na base fit a produkuje overconfident mapping;
- sparse-bin artefact — global gap je stabilný, no high-risk bins majú nízky support a širokú uncertainty;
- prior/prevalence shift — ranking ostáva približne stabilný, ale probability frequencies a action volume sa posunú;
- conditional shift — calibration sa zhorší iba v konkrétnych cohorts alebo score regions;
- class-order bug — probability columns sú priradené nesprávnym labels a proper scores prudko zlyhajú;
- calibrator overfit — isotonic mapping alebo flexible procedure je nestabilná medzi resamples/windows;
- interval mislabeling — quantile alebo ensemble spread sa prezentuje ako coverage guarantee, ktorú procedure neposkytuje;
- coverage failure — empirical interval/set coverage klesne pod locked target na representative population;
- sharpness collapse — coverage ostáva vysoká iba vďaka príliš širokým intervals alebo sets;
- OOD overconfidence — novelty cohort má high confidence, ale zlé outcomes a nízku abstention;
- selective-evaluation bias — report zahŕňa iba accepted/reviewed cases a ignoruje abstained population;
- stale policy — threshold alebo reserve rule bola fitovaná na predchádzajúcu probability/interval generation.

Stabilný raw score ranking so zhoršeným Brier/log loss podporuje calibration alebo prior hypothesis. Identické probabilities a iná action volume ukazujú policy alebo population-size zmenu. Coverage pokles iba po time cutoff podporuje shift, nie generic implementation bug.

## 21. Evidence-preserving containment a recovery

Containment zmrazí promotion base modelu, calibratora aj dependent policy. Zachová raw responses, probability matrices, calibration folds/window, labels, reliability bins, interval outputs, OOD signals a action logs.

```text
freeze composite model/policy promotion
→ preserve raw and calibrated artifacts
→ verify row/group/time disjointness
→ recompute proper scores, reliability and coverage
→ inspect cohorts, bins, OOD and selective denominators
→ falsify competing hypotheses
→ recalibrate, redesign interval procedure or retrain
→ issue successor artifact/policy generations
→ independent-window acceptance
```

Ak base ranking zostal validný a zlyhal iba calibrator, recovery môže vytvoriť nový calibration artifact bez predstierania nového base modelu. Ak calibration data leakovali, dependent thresholds a business simulations sú invalid. Ak coverage zlyhala pre shift, samotné rozšírenie intervalov môže chrániť krátkodobú policy, ale nenahrádza root-cause retraining alebo data acquisition.

## 22. Acceptance contract

Positive acceptance identifikuje exact event/target, base response, calibration/uncertainty procedure, disjoint fit evidence, population, class order, bins, proper scores, coverage, sharpness a downstream policy. Mandatory cohorts majú minimum support a explicitný „insufficient evidence“ stav.

Recovery acceptance reprodukuje composite artifact z manifests a preukazuje, že recalibration alebo interval correction zlepšila locked metrics na independent windowe. Forbidden paths zahŕňajú fitting calibratora na base-training predictions, ECE bez bin definition/supportu, threshold reuse po scale zmene, označenie q95 ako 95 % interval, evaluation iba na accepted cases, hidden class renormalization a tvrdenie, že seed variance je kompletná epistemic uncertainty.

Second-window test používa novšie mature labels/targets a rovnaký locked procedure. Second-operation test znovu vytvorí raw response, calibration transformáciu, probability/interval artifact a policy decisions s identickým class orderom, folds/window manifestom a toleranciou.

```yaml
acceptance:
  base_and_calibration_lineage: passed
  fit_calibration_disjointness: passed
  proper_scores_and_reliability: passed
  interval_coverage_and_sharpness: passed
  cohort_ood_and_abstention_guards: passed
  policy_generation_aligned: passed
  second_window: passed
```

## Kontrolné otázky

1. Aký je rozdiel medzi ranking score a calibrated probability?
2. Prečo názov `predict_proba` sám nepreukazuje calibration?
3. Ako uniform a quantile reliability bins menia evidence?
4. Prečo ECE nie je dostatočný samostatný acceptance metric?
5. Čo Brier score a log loss merajú a čo neizolujú?
6. Kedy zvoliť sigmoid, isotonic alebo temperature scaling?
7. Prečo calibration data musia byť oddelené od base-model fit evidence?
8. Ako `CalibratedClassifierCV` mení deployed artifact semantics?
9. Prečo prior shift môže pokaziť probability bez veľkého ranking regression?
10. Aký je rozdiel medzi aleatoric a epistemic uncertainty?
11. Prečo p95 point prediction nie je 95 % confidence interval?
12. Ako coverage a sharpness tvoria spoločný interval verdict?
13. Aké assumptions obmedzujú conformal prediction?
14. Prečo ensemble disagreement nie je universal uncertainty truth?
15. Ako abstention mení denominator a business outcome?
16. Čo pokazilo lifecycle v `ML-PAY-88`?
17. Aké positive, recovery, forbidden a second-window testy uzatvárajú calibration a uncertainty contract?

## Glossary impact

Relevantné pojmy: calibration, calibrated probability, raw score, reliability diagram, calibration bin, expected calibration error, maximum calibration error, calibration slope, Brier score, log loss, proper scoring rule, resolution, sigmoid calibration, isotonic calibration, temperature scaling, `CalibratedClassifierCV`, `FrozenEstimator`, prevalence shift, aleatoric uncertainty, epistemic uncertainty, prediction interval, quantile interval, coverage, sharpness, conformal prediction, nonconformity score, ensemble disagreement, out-of-distribution input, abstention, selective risk a calibration acceptance contract.

## Primárne zdroje

- [scikit-learn — Probability calibration](https://scikit-learn.org/stable/modules/calibration.html)
- [scikit-learn — `CalibratedClassifierCV`](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html)
- [scikit-learn — `calibration_curve`](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.calibration_curve.html)
- [scikit-learn — `brier_score_loss`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html)
- [scikit-learn — Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html)
