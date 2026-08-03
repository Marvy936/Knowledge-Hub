# Regression metrics

Regression metric hodnotí numerickú prediction voči numerickému targetu, ale samotný názov `MAE`, `RMSE` alebo `R²` ešte neurčuje, či verdict zodpovedá business rozhodnutiu. Význam chyby závisí od jednotky targetu, transformácie, horizontu, conditional distribution, sample weights, multioutput aggregation a asymetrie nákladov. Model s nižším priemerným errorom môže byť horší v high-value taili, systematicky podhodnocovať kapacitu počas špičky alebo vytvárať nepoužiteľné quantiles, hoci globálny `R²` vyzerá lepšie.

`ML-PAY-87` pokračoval druhou vetvou incidentu. Atlas predikoval recoverable loss a potrebný investigation time. Candidate znížil RMSE na globálnom teste, ale použil log-transformed target a report späť transformoval iba point predictions bez correction pre conditional mean. High-loss operácie boli podhodnotené, MAPE explodovala pri near-zero cases a weighted multioutput average zakryl výrazné zhoršenie investigation-time targetu. HPO navyše vyberalo model podľa negated scoreru, ktorý tím v dashboarde interpretoval ako kladnú loss. Kapitola preto viaže každý regression verdict na exact target, scale, loss direction a operational consequence.

## 1. Dominantný regression-evaluation lifecycle

Regression evaluation začína definíciou numerického targetu a času, ku ktorému má byť známy. Exact model artifact vytvorí point, interval alebo quantile predictions. Evaluation pipeline zachová units a transformations, vypočíta residuals, scale-dependent a relative metrics, rozdelí výsledky podľa target range a cohorts a až potom prepojí error distribution s business costom.

```text
business quantity a decision horizon
→ exact target definition, unit, maturity a transformation
→ exact model/preprocessing artifact
→ point, quantile alebo distribution prediction
→ inverse transformation a clipping policy
→ residual artifact
→ global, tail, cohort a business-weighted metrics
→ uncertainty a competing hypotheses
→ promotion, policy correction alebo rejection
→ second-window acceptance
```

Tento lifecycle oddeľuje model error od postprocessing erroru. Ak sa target trénuje v log scale, metric v log scale a metric v pôvodných eurách odpovedajú na odlišné otázky a obe musia identifikovať svoju generation.

## 2. Exact regression-evaluation subject

Report musí uložiť nielen dataset a model digest, ale aj target units, transformation, prediction semantics a aggregation. Inak sa napríklad RMSE v eurách môže porovnať s RMSE v log-eurách alebo point forecast s conditional quantile bez viditeľnej chyby v pipeline.

```yaml
evaluation_subject: ML-PAY-REG-EVAL-2026-08-v5
model_artifact:
  run_id: ML-PAY-REG-HPO-2026-08-v4
  digest: sha256:41fd...a880
population:
  dataset_manifest: recovery-cases-mature-2026w20-w30-v2
  observation_unit: payment_operation_id
  target_maturity_days: 45
targets:
  recoverable_loss_eur:
    prediction: conditional_mean
    train_transform: log1p
    report_unit: EUR
  investigation_minutes:
    prediction: conditional_median
    train_transform: none
    report_unit: minute
postprocessing:
  inverse_transform: expm1
  negative_clip: 0.0
aggregation:
  multioutput: raw_values
  sample_weight: none
slices:
  - target_decile
  - country
  - merchant_novelty
  - campaign_traffic
```

`conditional_mean`, `median` a `quantile_0.95` nie sú zameniteľné outputs. Rovnaká numeric value môže mať inú statistical authority podľa training objective a intended use.

## 3. Residual ako základný evidence artifact

Residual je rozdiel medzi observed targetom a prediction. Pri konvencii `residual = y_true - y_pred` kladná hodnota znamená underprediction a záporná overprediction. Nie všetky nástroje používajú rovnakú orientáciu, preto ju report musí uviesť.

```python
residual = y_true - y_pred
absolute_error = abs(residual)
squared_error = residual ** 2
```

Aggregate metric komprimuje residual distribution. Dôveryhodný report preto zachováva per-sample predictions, residuals, target values a cohort keys. Residual-vs-prediction, residual-vs-time a target-decile slices môžu odhaliť heteroscedasticity, saturation, clipping alebo systematický bias, ktorý jeden priemer skryje.

## 4. Mean absolute error

Mean absolute error je priemer absolútnych residuals a zostáva v jednotke targetu.

```text
MAE = mean(|y_true - y_pred|)
```

MAE dáva lineárnu váhu veľkým chybám a je robustnejšia voči extrémom než MSE. Optimal point prediction pre absolute-error objective súvisí s conditional median, nie automaticky s conditional mean. Preto model trénovaný na MAE-like objective môže byť vhodný pre median decision, ale nemusí minimalizovať total monetary squared alebo asymmetric cost.

```python
from sklearn.metrics import mean_absolute_error

mae_eur = mean_absolute_error(y_true_eur, y_pred_eur)
```

MAE `120 EUR` je interpretovateľná iba s target distribution a business tolerance. Rovnaká MAE môže vzniknúť z mnohých malých chýb alebo z malej skupiny kritických underpredictions.

## 5. Mean squared error a root mean squared error

MSE priemeruje squared residuals, takže veľké chyby majú kvadraticky vyššiu contribution. RMSE je square root MSE a vracia výsledok do pôvodnej target unit.

```text
MSE  = mean((y_true - y_pred)²)
RMSE = sqrt(MSE)
```

MSE je vhodná, keď veľké errors majú disproporčne vyšší cost alebo keď zodpovedá training/probabilistic assumption. Je však citlivá na outliers, label corruption a tail composition. RMSE sa nemá interpretovať ako „typická absolútna chyba“ bez pohľadu na distribution.

```python
from sklearn.metrics import mean_squared_error

mse = mean_squared_error(y_true, y_pred)
rmse = mse ** 0.5
```

Verzia scikit-learn API a použitá funkcia musia byť explicitné; evaluation code nemá spoliehať na zastaraný parameter, ak current API poskytuje samostatný root-mean-squared-error surface.

## 6. Median absolute error a robustný center

Median absolute error je median per-sample absolute errors. Silne odoláva malej skupine extrémov a môže dobre opisovať „typický“ case.

```python
from sklearn.metrics import median_absolute_error

median_ae = median_absolute_error(y_true, y_pred)
```

Práve robustnosť však môže skryť kritický tail. Model s výbornou median error a katastrofickými high-value misses nemá prejsť bez tail guardrails. Median absolute error preto patrí vedľa MAE/RMSE a high-quantile absolute error, nie namiesto nich.

## 7. R-squared a baseline-relative evidence

`R²` porovnáva squared error modelu s constant baseline založenou na mean targete evaluation population.

```text
R² = 1 - sum((y_true - y_pred)²) / sum((y_true - mean(y_true))²)
```

Hodnota `1` znamená perfect predictions na danom datasete. `0` znamená výkon na úrovni constant mean baseline a negative value znamená horší squared-error outcome než táto baseline. `R²` nie je percento správnosti ani podiel jednotlivých predictions, ktoré model „vysvetlil“.

```python
from sklearn.metrics import r2_score

r2 = r2_score(y_true, y_pred)
```

Pri nearly constant targete môže byť denominator veľmi malý a verdict nestabilný. Pri time shift-e sa baseline mean mení s evaluation windowom, takže porovnávanie `R²` medzi populáciami potrebuje raw error a target variance context. Multioutput aggregation môže navyše vážiť targets uniformne alebo podľa variance; táto voľba mení otázku.

## 8. Explained variance a mean bias

Explained variance hodnotí variance residualov voči variance targetu, ale na rozdiel od `R²` nemusí rovnako penalizovať systematický offset. Model, ktorý je konzistentne posunutý, môže mať dobrú explained variance a pritom neprijateľný mean error.

```python
import numpy as np
from sklearn.metrics import explained_variance_score

mean_error = np.mean(y_pred - y_true)
explained = explained_variance_score(y_true, y_pred)
```

Preto sa spolu reportujú mean signed error, residual quantiles a baseline-relative score. Systematické underprediction kapacity je operational incident aj vtedy, keď model dobre zachytáva relative fluctuations.

## 9. Percentage errors a denominator failure

MAPE priemeruje absolute percentage error. Je intuitívna iba vtedy, keď target má zmysluplný ratio scale a denominator nie je nula ani near-zero.

```text
absolute percentage error = |y_true - y_pred| / |y_true|
```

Pri `y_true ≈ 0` môže metric explodovať a niekoľko cases ovládne report. Záporné targets alebo targets prechádzajúce nulou komplikujú interpretáciu. Implementácie môžu používať epsilon-like ochranu, ale výsledok zostáva veľmi veľký, nie automaticky business-relevant.

Symmetric MAPE má vlastné denominator a edge-case problémy a nie je univerzálnou opravou. Pre Atlas investigation minutes boli near-zero cases validné automaticky uzavreté operácie; MAPE preto merala hlavne denominator artefact. Absolútna chyba a service-level threshold boli vhodnejšie.

## 10. Logarithmic errors

Mean squared logarithmic error porovnáva `log(1 + y)` a vyžaduje non-negative targets a predictions. Znižuje relative impact veľmi veľkých absolute differences a môže zodpovedať multiplicative error modelu.

```python
from sklearn.metrics import mean_squared_log_error

msle = mean_squared_log_error(y_true_nonnegative, y_pred_nonnegative)
```

Clipping negative predictions na nulu pred MSLE je policy mutation, ktorú treba reportovať. Dobrý MSLE nepreukazuje dobrý absolute-EUR outcome. Ak model trénuje na `log1p(target)`, naive `expm1(prediction)` typicky reprezentuje transformovaný conditional center a nemusí byť unbiased estimate pôvodného conditional mean. Postprocessing contract musí zodpovedať intended statistic.

## 11. Poisson, Gamma a Tweedie deviance

Deviance metrics vychádzajú z distributional assumptions a môžu byť vhodné pre non-negative skewed targets. Poisson deviance sa používa pre count-like alebo rate-like outcomes s príslušnými domain constraints; Gamma deviance pre strictly positive continuous targets; Tweedie deviance pokrýva širšiu family podľa power parameteru.

```python
from sklearn.metrics import mean_poisson_deviance, mean_gamma_deviance

poisson_dev = mean_poisson_deviance(y_true_count, y_pred_positive)
gamma_dev = mean_gamma_deviance(y_true_positive, y_pred_positive)
```

API úspech nepreukazuje správnu distributional assumption. Invalid zero/negative predictions, exposure differences a target definition musia byť vyriešené pred metric callom. Deviance sa porovnáva s relevantnou null baseline a business slices.

## 12. Quantile prediction a pinball loss

Quantile regression nepredikuje jeden universal point, ale conditional quantile. Pinball loss je asymmetric: underprediction a overprediction majú váhy podľa `alpha`. Pri `alpha=0.5` súvisí s median absolute objective; pri `alpha=0.95` vyberá 95. conditional quantile.

```python
from sklearn.metrics import mean_pinball_loss

p50_loss = mean_pinball_loss(y_true, q50_pred, alpha=0.50)
p95_loss = mean_pinball_loss(y_true, q95_pred, alpha=0.95)
```

Porovnávať p95 prediction cez MAE proti observed values odpovedá inej otázke než pinball loss. Quantile crossing, napríklad `q95 < q50`, je samostatný validity failure. Coverage a interval width budú detailnejšie patriť do calibration/uncertainty kapitoly, ale už regression report musí identifikovať quantile level.

## 13. D-squared scores

`D²` family vyjadruje fraction of deviance alebo loss explained relative to constant baseline pre zvolený loss. `D²` pinball score napríklad porovnáva quantile model s empirical constant quantile baseline. Rovnako ako `R²` môže byť negative a nie je square nejakej korelácie.

```python
from sklearn.metrics import d2_pinball_score

score = d2_pinball_score(y_true, q95_pred, alpha=0.95)
```

Výhodou je baseline-relative interpretation zladená s non-MSE objective. Nevýhodou je, že business stakeholders môžu metric nesprávne čítať ako percent accuracy. Report musí uvádzať raw loss aj baseline subject.

## 14. Multioutput regression a aggregation

Pri viacerých targets musí byť jasné, či sa metrics vracajú per-output alebo agregujú. Uniform average dáva každému outputu rovnakú váhu bez ohľadu na units a business value. Variance-weighted alebo custom weights zavádzajú inú policy.

```python
from sklearn.metrics import mean_absolute_error

per_target_mae = mean_absolute_error(
    y_true_multi,
    y_pred_multi,
    multioutput="raw_values",
)
weighted_mae = mean_absolute_error(
    y_true_multi,
    y_pred_multi,
    multioutput=[0.8, 0.2],
)
```

Pred agregáciou je často potrebná normalizácia business toleranciou, nie target standard deviation použitou počas trainingu. V Atlas incidente globálny weighted score zlepšil recoverable-loss output a prekryl zhoršenie investigation-time SLO. Per-target gates by to odmietli.

## 15. Sample weights, exposure a business cost

Sample weights môžu reprezentovať exposure, population correction alebo business priority. Každý účel vytvára iný estimand. Weight podľa transaction amount môže zmeniť MAE na value-weighted error, ale neznamená to automaticky total-loss objective, ak target už s amountom koreluje.

```yaml
metric_variants:
  - name: mae_unweighted
    sample_weight: none
  - name: mae_population_reweighted
    sample_weight: inverse_sampling_probability
  - name: underprediction_cost_eur
    function: asymmetric_business_cost_v3
```

Custom cost function môže penalizovať underprediction viac než overprediction alebo používať piecewise SLO. Musí byť versionovaná a testovaná na representative examples. Generic scorer a business cost sa reportujú oddelene, aby bolo viditeľné, či gain pochádza z data fitu alebo policy weights.

## 16. Tail, cohort a temporal evaluation

Global MAE/RMSE môže byť stabilná, zatiaľ čo error rastie v high-target decile, nových merchants alebo špičkovej prevádzke. Evaluation preto obsahuje target bins definované bez future leakage, domain cohorts a time windows.

```text
all samples
→ target deciles and operational cohorts
→ MAE/RMSE/mean signed error per slice
→ high-quantile absolute error
→ worst-supported mandatory cohort
→ temporal drift
```

Slice s malým supportom potrebuje uncertainty a minimum support policy. Tiché odstránenie slice kvôli nestabilite je forbidden; správny verdict môže byť „insufficient evidence“.

## 17. Scorer direction a model-selection boundary

V scikit-learn scoring API sa losses často vystavujú ako negated scorers, napríklad `neg_mean_absolute_error`, pretože selection machinery maximalizuje score. Hodnota `-120` znamená MAE `120`, nie lepší kladný error.

```python
from sklearn.model_selection import cross_validate

result = cross_validate(
    estimator,
    X,
    y,
    scoring={
        "mae": "neg_mean_absolute_error",
        "r2": "r2",
    },
    cv=cv,
)
mae_per_fold = -result["test_mae"]
```

Dashboard musí explicitne invertovať direction a pomenovať unit. Model selection score nie je automatically test acceptance a fold average nie je final refit artifact metric.

## 18. Paired comparison a uncertainty

Candidate a baseline sa vyhodnocujú na rovnakých samples a residual difference sa analyzuje paired spôsobom. Grouped bootstrap alebo time blocks rešpektujú závislosť. Pre heavy-tailed target sa reportuje distribution rozdielu, nie iba asymptotic interval nad mean.

```text
same operation IDs
→ baseline residual and candidate residual
→ paired absolute/squared/cost difference
→ grouped or temporal resampling
→ global and tail confidence interval
```

Malý RMSE gain môže byť spôsobený jedným extrémnym sample. Paired residual review ukáže, ktoré cases sa zlepšili a ktoré sa zhoršili. Acceptance potrebuje practical significance, nie iba statistical non-zero difference.

## 19. Worked incident `ML-PAY-87`

Atlas HPO optimalizovalo `neg_root_mean_squared_error` na log-transformed targete, ale dashboard odstránil minus sign a labeloval výsledok ako „RMSE EUR“. Candidate vyzeral lepšie, hoci score bolo v log unit. Po `expm1` sa high-loss tail systematicky podhodnocoval a negative outputs sa pred metric výpočtom clipovali na nulu bez lineage.

Druhý output, investigation minutes, sa agregoval uniform average po predchádzajúcej standardizácii, no production report použil raw units a custom weights. Model-selection a acceptance metrics teda nehodnotili rovnakú procedure.

```text
training target: log1p(EUR)
selection score: negative RMSE in log scale
report label: RMSE EUR
postprocessing: expm1 + hidden clip
business use: reserve sizing in EUR
```

Global RMSE v eurách zlepšilo niekoľko extreme recoveries, ale p95 underprediction a campaign cohort sa zhoršili. Root cause bol multi-layer metric identity failure, nie samotná voľba RMSE.

## 20. Competing failure hypotheses

Regression verdict môže zmeniť target pipeline, unit conversion, postprocessing alebo aggregation bez toho, aby sa zmenil fitted estimator. Prvý diagnostický krok preto porovná raw targets a predictions v training/report scale, inverse-transform output, clipping/rounding policy, residual distribution a per-output/per-cohort denominators. Až potom sa rozhoduje, či ide o model regression, evaluation bug alebo population shift.

Každá hypotéza musí vysvetliť konkrétny residual pattern. Tail-composition shift typicky zmení RMSE viac než MAE; unit alebo transform mismatch posunie široké spektrum errors systematicky; postprocessing regression vytvorí rozdiel medzi raw a served predictions; multioutput masking ukáže zhoršenie v per-target reporte pri stabilnom aggregate score. Pred retrainingom sa preto rozlišujú tieto mechanisms:

- target-definition drift — maturity, currency conversion alebo inclusion rules sa zmenili;
- unit/transform mismatch — metric sa počíta v log scale, normalized scale alebo nesprávnej mene;
- postprocessing regression — inverse transform, clipping alebo rounding zmenili predictions;
- tail-composition shift — niekoľko high-value samples zmenilo MSE/RMSE bez broad regression;
- systematic bias — mean signed error ukazuje stabilné underprediction alebo overprediction;
- heteroscedasticity — error variance rastie s prediction/target levelom alebo cohortom;
- multioutput masking — aggregate gain prekrýva zhoršenie povinného targetu;
- coverage failure — failed predictions sa odstránili z population;
- scorer-direction bug — negated loss sa interpretovala alebo zoradila opačne;
- baseline mismatch — `R²` alebo `D²` sa porovnáva medzi inými evaluation populations.

Každá hypotéza má odlišný dôkaz. Stabilné residuals pred postprocessingom a zhoršené residuals po ňom ukazujú policy bug. Zmena iba RMSE pri stabilnej MAE podporuje tail/outlier hypothesis. Zhoršenie všetkých metrics po currency conversion naznačuje unit generation.

## 21. Evidence-preserving containment a recovery

Containment zachová raw target snapshot, predictions pred aj po postprocessingu, transformations, units, sample weights a metric code SHA. Candidate promotion sa zastaví, ale approved production artifact sa nemení bez business evidence.

```text
freeze verdict and promotion
→ preserve targets, raw predictions and postprocessing
→ validate units, maturity and coverage
→ recompute residuals and per-target metrics
→ inspect tail, cohorts and scorer direction
→ falsify competing hypotheses
→ correct report/policy or create successor model
→ independent-window acceptance
```

Ak bol chybný report label, historický evaluation run sa označí invalid a metric sa znovu vytvorí z immutable artifacts. Ak sa mení postprocessing, vznikne nová policy generation. Ak sa retrainuje model, test evidence sa nesmie recyklovať ako tuning feedback.

## 22. Acceptance contract

Positive acceptance identifikuje exact target semantics, units, maturity, transform, prediction statistic, postprocessing, model digest, population a aggregation. Obsahuje per-target MAE/RMSE alebo relevantný loss, mean signed error, tail/cohort metrics, baseline-relative score a business-cost guardrails.

Recovery acceptance reprodukuje metrics z uloženého residual artifactu a overuje unit/transform round trip. Forbidden paths zahŕňajú označenie log-scale RMSE ako EUR, MAPE pri near-zero targete bez denominator analýzy, aggregation bez per-output floors, skryté clipping, odstránenie failed inference rows a interpretáciu negative scoreru opačným smerom.

Second-window test používa novšie mature targets s locked metric contractom. Second-operation test opakovane vytvorí predictions, inverse transform a residual artifact a musí zachovať sample IDs, units, counts, per-output ordering a metrics v deklarovanej tolerancii.

```yaml
acceptance:
  target_and_unit_contract: passed
  raw_and_postprocessed_predictions_preserved: passed
  per_output_and_tail_guards: passed
  scorer_direction_verified: passed
  coverage_denominator_complete: passed
  second_window: passed
```

## Kontrolné otázky

1. Prečo MAE, RMSE a `R²` neodpovedajú na rovnakú otázku?
2. Čo znamená znamienko residualu v zvolenej konvencii?
3. Kedy je MAE vhodnejšia než MSE a čo môže skryť?
4. Prečo RMSE nie je automaticky typická absolute error?
5. Ako interpretovať negative `R²`?
6. Prečo explained variance môže prekryť systematický offset?
7. Čo zlyháva pri MAPE a near-zero targets?
8. Kedy je MSLE zmysluplná a aké domain constraints vyžaduje?
9. Ako Poisson/Gamma/Tweedie deviance súvisia s target assumptions?
10. Prečo quantile prediction potrebuje pinball loss s rovnakým alpha?
11. Čo znamená negative `D²` score?
12. Ako multioutput aggregation môže prekryť regression incident?
13. Prečo sample weight potrebuje explicitný estimand?
14. Ako sa negated scorers používajú v model selection?
15. Čo pokazilo regression evaluation v `ML-PAY-87`?
16. Aké positive, recovery, forbidden a second-window testy uzatvárajú regression verdict?

## Glossary impact

Relevantné pojmy: regression evaluation subject, target unit, target maturity, point prediction, conditional mean, conditional median, quantile prediction, residual, signed error, absolute error, squared error, MAE, MSE, RMSE, median absolute error, R-squared, explained variance, MAPE, MSLE, Poisson deviance, Gamma deviance, Tweedie deviance, pinball loss, D-squared score, multioutput aggregation, exposure weight, asymmetric business cost, tail metric, scorer direction a regression acceptance contract.

## Primárne zdroje

- [scikit-learn — Metrics and scoring: regression metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics)
- [scikit-learn — `mean_absolute_error`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_error.html)
- [scikit-learn — `mean_squared_error`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_squared_error.html)
- [scikit-learn — `r2_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html)
- [scikit-learn — `mean_pinball_loss`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_pinball_loss.html)
- [scikit-learn — `d2_pinball_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.d2_pinball_score.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Classification metrics](classification-metrics.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Imbalanced datasets a threshold selection →](imbalanced-datasets-threshold-selection.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
