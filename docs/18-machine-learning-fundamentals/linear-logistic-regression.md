# Linear a logistic regression

Linear a logistic regression patria medzi najdôležitejšie baselines, pretože ich model form je explicitný, training je relatívne lacný a failure behavior sa dá analyzovať cez features, coefficients, residuals, probabilities a regularization. Ich jednoduchosť však neznamená automatickú interpretovateľnosť ani correctness. Coefficient závisí od feature unit, preprocessing, collinearity, regularization a target definition; logistic output závisí od link function, calibration a decision threshold. Model môže byť technicky lineárny a celý application decision vysoko nelineárny kvôli feature engineeringu a post-processing policy.

Incident `ML-PAY-85` vznikol, keď Atlas porovnával interpretable logistic baseline, tree ensemble a malú neural network pre operation-risk model. Logistic model bol prezentovaný ako vysvetliteľný, no coefficients sa čítali bez scalingu a pri silne correlated features. `C` regularization sa zmenila medzi experimentom a final fitom, probability sa používala ako top-K utility a class threshold sa považoval za súčasť modelu, hoci žil v queue service. Tento chapter fixuje exact linear-model subject ešte pred porovnaním complex candidates.

## 1. Dominantný linear-model lifecycle

Linear model začína numeric representation a target semantics. Training optimalizuje coefficients podľa lossu a regularization. Fitted parameters vytvoria raw prediction alebo logit; link function môže vytvoriť probability; calibration a threshold/policy vytvoria action. Každý transition má samostatnú generation a evidence.

```text
feature schema, scaling a interactions
→ target a sample weights
→ linear/logistic objective + regularization
→ solver a convergence
→ coef_ + intercept_
→ raw value alebo logit
→ probability/link
→ threshold/ranking policy
→ business action a outcome
```

Coefficient read-back preukazuje fitted parameter v konkrétnom representation space. Nepreukazuje causal effect, independent importance ani stability pri zmenenom datasete.

## 2. Exact linear-model subject

Linear-model manifest musí zviazať representation, objective a downstream decision, pretože samotné coefficients nemajú význam bez feature units, preprocessing, regularization a output interpretation. Rovnaký estimator class môže vytvoriť odlišné fitted functions pri zmene scaleru, class weights alebo `C`; rovnaká fitted function môže vytvoriť odlišné business actions pri zmene calibration alebo threshold/ranking policy.

Nasledujúci subject preto oddeľuje, čo optimizer fituje, čo calibration mení a čo application policy vykonáva. Pri incidente umožňuje porovnať requested experiment, final refit, loaded artifact a active queue policy bez zjednodušenia všetkých vrstiev na názov „logistic regression“.

```yaml
model_subject: ML-PAY-LR-2026-08-v3
task: binary classification
target: confirmed_loss_within_30d
feature_schema: risk-linear-v6
preprocessing_digest: sha256:18a2...71c9
estimator: sklearn.linear_model.LogisticRegression
solver: lbfgs
penalty: l2
C: 0.1
class_weight: balanced
max_iter: 2000
fit_population: SPLIT-ML-PAY-84-v3/train
calibration: isotonic-v2
threshold_policy: top-2500-expected-loss-v4
artifact_digest: sha256:7f9c...8e11
```

Model subject oddeľuje estimator parameters od calibration a action policy. `C=0.1` patrí fitted objective; top-K policy nie. Rovnaké coefficients s inou calibration alebo thresholdom vytvoria inú system generation.

## 3. Linear regression model form

Linear regression predikuje numeric target ako intercept plus vážený súčet features:

```text
ŷ = w₀ + w₁x₁ + ... + wₚxₚ
```

`w_j` je zmena prediction pri jednotkovej zmene `x_j`, ak ostatné represented features zostanú fixed. Táto podmienka je modelová, nie automaticky realizovateľný causal intervention. Ak features sú correlated alebo derived z rovnakého source, „ostatné fixed“ nemusí byť business-plausible.

Scikit-learn `LinearRegression` pri ordinary least squares minimalizuje residual sum of squares:

```text
min_w ||Xw - y||²₂
```

```python
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X_train, y_train)
prediction = model.predict(X_test)
```

Fitted `coef_` a `intercept_` závisia od output unit targetu a input units. Target v cents vytvorí coefficients stokrát väčšie než target v euros, ak ostatné ostane rovnaké.

## 4. Residuals a error structure

Residual je `y - ŷ`. Aggregate loss sumarizuje errors, ale residual diagnostics skúmajú systematic patterns, variance, tails a cohorts.

```text
residual = actual - prediction
```

Ak residuals rastú s predicted value, error variance nie je constant. Ak model systematicky podhodnocuje high-loss operations, low average error môže maskovať critical tail. Time, merchant cohort alebo currency residual plots môžu ukázať missing nonlinearity alebo distribution shift.

Residual nie je pure noise. Obsahuje irreducible uncertainty, measurement/label error, omitted variables, wrong functional form a data bugs. Pridať complexity má zmysel až po diagnosis.

## 5. Basis functions a lineárnosť v parameters

Linear model môže byť nelineárny voči raw inputu, ak preprocessing vytvorí polynomial, spline, log alebo interaction features. Stále je lineárny vo fitted coefficients.

```text
ŷ = w₀ + w₁x + w₂x²
```

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge

model = make_pipeline(
    PolynomialFeatures(degree=2, include_bias=False),
    Ridge(alpha=1.0),
)
```

Taký model môže zachytiť curvature, ale coefficient interpretation patrí transformed basis, nie raw feature samotnej. Polynomial expansion zvyšuje dimensionality a collinearity; regularization a scaling sú často potrebné.

## 6. Logistic regression je classifier

Logistic regression modeluje log-odds class probability ako lineárnu kombináciu features. Pre binary classification:

```text
z = w₀ + wᵀx
p(y=1|x) = 1 / (1 + e⁻ᶻ)
log(p / (1-p)) = z
```

Napriek názvu ide v ML nomenklatúre o classification model. `predict_proba` vracia estimated probabilities podľa fitted logistic modelu; `predict` aplikuje class decision rule.

```python
from sklearn.linear_model import LogisticRegression

classifier = LogisticRegression(
    penalty="l2",
    C=0.1,
    solver="lbfgs",
    max_iter=2000,
)
classifier.fit(X_train, y_train)
probability = classifier.predict_proba(X_test)[:, 1]
```

Lineárnosť je v log-odds, nie v probability. Unit change feature má multiplicative effect na odds `exp(w_j)` pri fixed ostatných features, ale causal interpretácia stále neplatí automaticky.

## 7. Binary, multinomial a one-vs-rest formulations

Binary logistic regression má dve classes. Multiclass problem možno riešiť multinomial objective alebo one-vs-rest classifiers. Output semantics a normalization sa líšia.

```text
multinomial:
one shared objective across classes

one-vs-rest:
independent class-vs-rest models
```

Model manifest musí uviesť formulation, class order a labels. Probability array column `1` nie je self-describing. Class vocabulary a mapping sú schema generation.

Multilabel problem nie je rovnaký ako multiclass: sample môže mať viac simultaneous labels a často používa independent binary outputs alebo iný structured objective.

## 8. Loss a maximum likelihood boundary

Ordinary least squares súvisí s squared error objective. Logistic regression typicky optimalizuje log loss/negative log-likelihood plus regularization. Loss určuje, ktoré errors menia coefficients a ako confidence ovplyvňuje penalty.

```text
binary log loss per sample:
-[y log(p) + (1-y) log(1-p)]
```

Confident wrong prediction má veľkú penalty. Loss je training objective, nie business cost. False positive analyst friction a false negative loss nemusia byť symetricky reprezentované. Sample/class weights alebo downstream threshold môžu približovať business asymmetry, ale vyžadujú explicitný contract.

## 9. Feature scaling a coefficient units

Coefficient magnitude nemožno porovnávať medzi features s odlišnými units bez kontextu. Jednotková zmena `amount_eur` a `decline_rate` znamená úplne inú praktickú zmenu.

```text
w_amount = 0.001 per EUR
w_decline_rate = 2.0 per full ratio unit
```

Scaling môže zjednotiť numerical optimization a regularization effect. Po standardization coefficient reprezentuje zmenu pri jednej training-standard-deviation transformed unit. To zlepšuje porovnateľnosť, ale stále závisí od correlation a fitted scaler generation.

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

pipeline = make_pipeline(
    StandardScaler(),
    LogisticRegression(C=0.1, max_iter=2000),
)
```

Intercept a coefficients musia byť interpretované spolu s preprocessing. Raw `coef_` bez output feature names je nebezpečný.

## 10. Collinearity a coefficient instability

Ak features sú silne correlated alebo linearly dependent, viac coefficient combinations môže poskytovať podobné predictions. OLS coefficients môžu mať high variance; logistic coefficients môžu byť unstable. Small data changes alebo regularization môžu meniť sign/magnitude.

```text
amount_eur
amount_minor = amount_eur * 100
```

Zahrnúť obe features vytvára exact dependence. Menej očividné sú overlapping velocity windows alebo related ratios. Predictions môžu zostať stable, zatiaľ čo individual coefficient interpretation sa mení.

Variance inflation a condition diagnostics pomáhajú, ale operationally treba feature rationale, stability naprieč folds/time a grouped interpretation. „Coefficient je nula“ neznamená universal irrelevance pri regularized correlated set-e.

## 11. Ridge, Lasso a Elastic Net

Regularization pridáva penalty na coefficient size, čím riadi variance a complexity.

Ridge/L2:

```text
loss + α ||w||²₂
```

Lasso/L1:

```text
loss + α ||w||₁
```

Elastic Net kombinuje L1 a L2. Ridge typicky shrinkuje correlated coefficients; Lasso môže vytvoriť exact zeros a implicitnú selection, ale pri correlated features môže vybrať jednu arbitrárne.

V scikit-learn `Ridge` používa `alpha`, zatiaľ čo `LogisticRegression` používa inverse regularization strength `C`: menšie `C` znamená silnejšiu regularization. Tieto parameters sa nesmú zamieňať.

```python
from sklearn.linear_model import Ridge, Lasso

ridge = Ridge(alpha=10.0)
lasso = Lasso(alpha=0.01)
```

Regularization hyperparameter sa vyberá validation/CV, nie testom. Scaling ovplyvňuje penalty across features.

## 12. Class weights a sample weights

Weights menia contribution samples/classes do objective-u. `class_weight="balanced"` reweightuje classes podľa frequency, ale nevytvára automaticky calibrated probabilities pre production prevalence.

```python
classifier = LogisticRegression(
    class_weight="balanced",
    C=0.1,
    max_iter=2000,
)
```

Sample weights môžu reprezentovať exposure, importance alebo correction sampling policy. Musia mať unit a source. Duplikovať row a weightovať row nie je vždy numericky identické pri regularization/solver details.

Weighted loss optimalizuje zvolenú training objective. Threshold a calibration musia byť hodnotené na representative unweighted/appropriately weighted population podľa intended outcome.

## 13. Separation a convergence

Pri complete alebo quasi-complete separation môže feature dokonale oddeliť classes v training data. Unregularized logistic coefficients môžu rásť bez finite optimum. Separation môže byť legitimate small-data pattern alebo leakage feature.

```text
post_review_flag = 1 iba pre positives
→ perfect separation
→ likely leakage
```

Solver convergence warning nie je kozmetika. Môže signalizovať insufficient iterations, bad scaling, ill-conditioning, separation alebo incompatible solver/penalty. Zvýšiť `max_iter` bez diagnosis môže iba oddialiť warning.

Manifest/report má uchovať solver, iterations, convergence status a warnings. Candidate s failed convergence nemá byť promoted len preto, že `.predict_proba()` funguje.

## 14. Calibration a logistic probability

Logistic model môže produkovať reasonably calibrated probabilities, ak model form a data assumptions sú vhodné, ale nie je to garancia. Regularization, class weighting, sampling, shift a misspecification môžu calibration zhoršiť.

Calibration porovnáva predicted probability s observed frequency. Calibration layer sa fituje na separate validation data alebo cross-validated procedure, nie na test.

```text
among cases predicted near 0.8
→ approximately 80 % positives?
```

AUC-like ranking metric môže byť dobrá pri zlej calibration. Top-K ranking možno stále funguje, ale expected-loss formula vyžaduje probability semantics. Calibration artifact a method sú successor generation.

## 15. Threshold nie je parameter logistic estimatoru

Model output probability/score sa mení na class/action cez threshold. Default `0.5` je implementation convenience, nie universal optimum. Business capacity, costs a prevalence určujú policy.

```text
p >= 0.5 → model class

business:
top 2500 by expected utility → manual review
```

Threshold môže byť global, cohort-specific alebo capacity-derived. Cohort thresholds môžu vytvárať fairness, complexity a monitoring risks. Policy owner musí byť explicitný.

Changing threshold does not retrain coefficients, but changes confusion matrix, queue size and outcomes. Audit musí versionovať oba.

## 16. Coefficient interpretation

Pre linear regression, coefficient je conditional model slope v target units per feature unit. Pre logistic regression, `exp(w_j)` je conditional odds ratio pre unit increase, given represented other features fixed. Pri standardized, one-hot alebo interaction features sa interpretation mení.

```python
import numpy as np

odds_ratios = np.exp(classifier.coef_[0])
```

Large coefficient môže odrážať rare category, scaling alebo separation. Small coefficient pri large-range feature môže mať large practical effect. Coefficients nie sú feature importance across arbitrary preprocessing.

Causal claim vyžaduje causal design a assumptions mimo predictive model. Prediction model coefficient môže zachytiť confounding, selection a proxy relationships.

## 17. Prediction intervals a uncertainty

Plain scikit-learn `LinearRegression.predict` vracia point predictions, nie automatic prediction intervals. Statistical interval estimation vyžaduje assumptions alebo separate methods. Logistic probability tiež neobsahuje model epistemic uncertainty.

Bootstrap, Bayesian models, quantile regression alebo conformal methods môžu pridať uncertainty evidence, ale ich coverage platí pre defined assumptions/population. One decimal probability nie je complete confidence statement.

Operational fallback môže používať out-of-range/low-support cohorts alebo ensemble disagreement ako risk signal, nie iba raw probability.

## 18. Baseline role

Linear/logistic model je silný baseline, pretože poskytuje transparentný feature-to-output path, fast iteration a often good tabular performance. Complex model musí preukázať incremental value nad baseline na same split, features alebo controlled differences.

```text
constant/dummy baseline
→ regularized linear/logistic baseline
→ tree ensemble
→ neural candidate
```

Ak neural model prekoná logistic iba v contaminated split-e, complexity nemá evidence. Ak tree model gain pochádza z unavailable feature, algorithm comparison je invalid.

Baseline tiež poskytuje fallback pri serving outage complex modelu, ak feature compatibility a policy sú schválené.

## 19. Worked incident `ML-PAY-85`

Atlas logistic baseline používal standardized numerical features, one-hot categories a L2 regularization. Notebook report ukázal coefficient `merchant_decline_rate_1h = 2.9` a tím ho označil za „najdôležitejší causal driver“. Feature však bola correlated s retry count a new-device interaction. Pri inom `C` sa coefficient rozdelil medzi correlated features a sign jednej interaction sa zmenil.

Training používal `class_weight="balanced"`, ale probabilities sa bez calibration vložili do expected-loss formula. Queue service následne aplikoval hidden threshold a arrival-time tie-breaking. Final refit omylom použil default `C=1.0` namiesto selected `0.1`; artifact metadata zaznamenala iba model family.

Evidence ukázal:

```text
same code family
≠ same objective/regularization generation

coefficient magnitude
≠ causal importance

weighted training probability
≠ production-calibrated probability

model output
≠ queue action policy
```

## 20. Evidence-preserving containment a recovery

Tím zachoval feature names/order, scaler state, coefficients, intercept, solver status, selected hyperparameters, class/sample weights, calibration artifact a queue policy. Automatic promotion sa zastavil a fallback používal posledný approved logistic pipeline.

Recovery vytvorila immutable pipeline manifest a porovnala candidate/refit parameters. Coefficient report používal original units aj standardized units, fold/time stability a correlated groups. Calibration sa fitla na validation cohort a top-K policy zostala separate artifact.

```text
fit candidate on train
→ select C/features on validation
→ final refit according to declared procedure
→ calibrate according to declared validation split
→ test locked pipeline
→ shadow queue
```

Model registry read-back overil loaded coefficients, preprocessing digest, calibration a threshold policy.

## 21. Acceptance contract

Positive path musí preukázať exact feature/preprocessing schema, objective, regularization, solver convergence, fitted coefficients, calibration a downstream policy. Offline metrics sa reportujú s residual/cohort alebo probability/calibration evidence.

Recovery path musí umožniť rollback compatible pipeline + calibration + policy generations. Coefficient alebo threshold change bez artifact lineage je forbidden.

Forbidden paths:

```text
coefficient sa vydáva za causal effect bez causal designu
magnitudes sa porovnávajú naprieč units bez scaling contextu
regularization hyperparameter sa stratí pri final refit-e
solver warning sa ignoruje
class-weighted raw probability sa vydáva za calibrated production risk
threshold sa zamieňa s model weights
model family name sa vydáva za exact artifact identity
```

Second-fit test na pinned data/seed overí coefficients, convergence a prediction tolerance. Second-cohort test overí calibration, residuals, class/action policy a stable fallback na newer mature period.

## Kontrolné otázky

1. Aký model form má linear regression?
2. Čo ordinary least squares minimalizuje?
3. Prečo residual analysis dopĺňa aggregate loss?
4. Ako môže byť model lineárny v parameters a nelineárny v raw inpute?
5. Prečo logistic regression je classifier?
6. Čo je logit a sigmoid link?
7. Ako sa multinomial a one-vs-rest formulation líšia?
8. Prečo training loss nie je business cost?
9. Ako feature units a scaling menia coefficients?
10. Čo collinearity robí coefficient stability?
11. Ako Ridge, Lasso a Elastic Net regularizujú model?
12. Prečo menšie `C` v logistic regression znamená silnejšiu regularization?
13. Ako class weights ovplyvňujú probability semantics?
14. Čo signalizuje separation alebo non-convergence?
15. Prečo logistic probability nemusí byť calibrated?
16. Prečo threshold nie je universal model parameter?
17. Čo coefficient môže a nemôže dokazovať?
18. Prečo baseline zostáva dôležitá pri complex models?
19. Aké positive, recovery, forbidden a second-fit testy uzatvárajú linear-model contract?

## Glossary impact

Relevantné pojmy: linear regression, ordinary least squares, coefficient, intercept, residual, basis function, logistic regression, logit, sigmoid, odds, odds ratio, multinomial, one-vs-rest, log loss, scaling, collinearity, Ridge/L2, Lasso/L1, Elastic Net, class weight, sample weight, separation, solver convergence, calibration, threshold a linear-model acceptance contract.

## Primárne zdroje

- [scikit-learn — Linear Models](https://scikit-learn.org/stable/modules/linear_model.html)
- [scikit-learn — `LinearRegression`](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
- [scikit-learn — `LogisticRegression`](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)
- [scikit-learn — `Ridge`](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html)
- [scikit-learn — Probability calibration](https://scikit-learn.org/stable/modules/calibration.html)
- [scikit-learn — Tuning the decision threshold](https://scikit-learn.org/stable/modules/classification_threshold.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Data leakage a train-serving skew](data-leakage-train-serving-skew.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Decision trees, random forests a gradient boosting →](decision-trees-random-forests-gradient-boosting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
