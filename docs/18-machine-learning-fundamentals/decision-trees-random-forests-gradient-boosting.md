# Decision trees, random forests a gradient boosting

Decision tree vytvára piecewise decision function rozdeľovaním feature space cez sekvenčné rules. Random forest priemeruje alebo hlasuje naprieč mnohými randomized trees, aby znížil variance. Gradient boosting buduje trees sekvenčne tak, aby každý nový learner opravoval residual alebo gradient predchádzajúceho ensemble. Tieto model families dokážu zachytiť nonlinearities a interactions bez explicitného polynomial expansionu, ale ich mechanics, overfitting, calibration, latency a interpretability sa zásadne líšia.

V incidente `ML-PAY-85` Atlas tree candidate vyzeral lepšie než logistic baseline. Single tree dosiahol takmer perfect training score, random forest stabilizoval majority cohorts a histogram gradient boosting získal najlepší top-K offline result. Tím však porovnával models s inými missing-value handling, class weights a feature subsets. Tree importance zvýhodnila high-cardinality merchant-derived fields a boosted model používal deep leaves s malým supportom. „Trees vyhrali“ nebolo exact verdict, kým sa nezafixoval ensemble subject a business evaluation.

## 1. Dominantný tree-ensemble lifecycle

Tree model sa učí partition rules z training data. Ensemble potom kombinuje multiple trees podľa bagging alebo boosting mechanismu. Output môže byť value, class vote, score alebo probability. Hyperparameters riadia capacity, randomization, shrinkage a stopping; downstream calibration a threshold zostávajú separate.

```text
feature schema + target/weights
→ split criterion a tree-growth constraints
→ individual tree partitions
→ bagged alebo boosted ensemble construction
→ fitted tree structures
→ aggregate raw output/probability
→ calibration/threshold/ranking policy
→ business action a outcome
```

Tree diagram je read-back learned rules, nie source-code truth. Rules sú validné iba pre exact preprocessing, category representation, missing handling a artifact generation.

## 2. Exact tree-ensemble subject

```yaml
model_subject: ML-PAY-HGB-2026-08-v2
task: binary classification
feature_schema: risk-tree-v7
estimator: HistGradientBoostingClassifier
loss: log_loss
learning_rate: 0.05
max_iter: 300
max_leaf_nodes: 31
max_depth: null
min_samples_leaf: 50
l2_regularization: 1.0
early_stopping: true
validation_fraction: 0.1
random_state: 17
fit_population: SPLIT-ML-PAY-84-v3/train
artifact_digest: sha256:61c8...20ad
calibration: isotonic-v2
policy: top-2500-expected-loss-v4
```

Subject fixuje growth a ensemble process. „Gradient boosting“ bez learning rate, iteration count, leaf constraints, loss a early-stopping data nemá reprodukovateľný meaning. Random forest subject by namiesto toho fixoval number of trees, bootstrap, feature subsampling, depth/leaves a random seeds.

## 3. Decision tree partition mechanism

At each node, tree algorithm vyberá feature a threshold/category split, ktorý podľa criterion zlepší purity alebo zníži loss. Samples pokračujú do child nodes až po leaf, ktorá nesie prediction statistics.

```text
amount_minor <= 12000?
├── yes: merchant_age_days <= 7?
│   ├── yes → leaf A
│   └── no  → leaf B
└── no: decline_rate_1h <= 0.25?
    ├── yes → leaf C
    └── no  → leaf D
```

Classification criterion môže používať Gini impurity alebo entropy/log loss; regression často squared error alebo absolute-error-like criteria. Local split improvement neoptimalizuje priamo final business metric.

Tree prediction je piecewise constant v leaves. Small input change cez threshold môže vytvoriť discontinuous output. Ties, float precision a category encoding ovplyvňujú path.

## 4. Tree capacity a overfitting

Unconstrained tree môže grow until leaves sú pure alebo príliš malé. Taký tree memorizes noise, IDs alebo rare combinations a má high variance. Capacity controls zahŕňajú `max_depth`, `max_leaf_nodes`, `min_samples_split`, `min_samples_leaf`, `max_features` a pruning.

```python
from sklearn.tree import DecisionTreeClassifier

model = DecisionTreeClassifier(
    max_depth=6,
    min_samples_leaf=100,
    class_weight="balanced",
    random_state=17,
)
```

Depth nie je jediná complexity measure. Balanced depth-6 tree a highly unbalanced tree môžu mať inú leaf support. Minimum leaf samples treba interpretovať vzhľadom na weights/groups a rare classes.

Training purity nie je acceptance. Validation/group/time stability a leaf support na production cohorts sú rozhodujúce.

## 5. Pruning a cost-complexity

Pre-pruning obmedzuje growth počas fitu. Post-pruning odstráni branches podľa complexity penalty alebo validation evidence. Minimal cost-complexity pruning používa parameter `ccp_alpha` na trade-off impurity a leaf count.

```text
pruned objective ≈ training impurity + α × number_of_leaves
```

Pruning path sa fituje na train a `alpha` sa vyberá validation/CV. Prune podľa testu kontaminuje acceptance. Simpler tree môže mať lower variance a lepšiu explainability, ale nie automaticky calibrated output.

Pruned artifact je distinct generation; visualizácia pre unpruned candidate nepopisuje loaded model.

## 6. Decision path a leaf identity

Pre konkrétny sample možno read-backnúť sequence nodes a final leaf. Toto je model-local explanation: ukazuje, ktoré learned rules sample prešiel. Nepreukazuje causal dôvod ani global feature effect.

```python
leaf_id = model.apply(X_sample)
path = model.decision_path(X_sample)
```

Leaf support, class counts a weighted probability pomáhajú interpretovať confidence. Leaf s dvoma weighted samples je fragile, aj keď probability je 1.0. Production telemetry nemá logovať sensitive full feature vectors bez policy; môže logovať model/leaf IDs a bounded explanation data.

## 7. Random forest ako bagged randomized trees

Random forest fituje many trees na bootstrap samples a pri každom split-e zvažuje random subset features. Predictions sa priemerujú alebo hlasujú. Randomization znižuje correlation medzi trees a averaging znižuje variance oproti single tree.

```python
from sklearn.ensemble import RandomForestClassifier

forest = RandomForestClassifier(
    n_estimators=500,
    max_depth=None,
    min_samples_leaf=20,
    max_features="sqrt",
    bootstrap=True,
    class_weight="balanced_subsample",
    random_state=17,
    n_jobs=-1,
)
```

Každý tree môže byť deep, ale ensemble generalization závisí od tree strength, correlation a data. More trees typicky stabilizujú estimate, no zvyšujú fit/inference cost a artifact size. Neopravujú leakage ani wrong target.

## 8. Bootstrap a out-of-bag evidence

Bootstrap sample vyberá training observations s replacement; časť rows ostáva pre daný tree out-of-bag (OOB). OOB predictions agregujú trees, ktoré daný sample nevideli, a poskytujú internal estimate.

```text
training sample i
→ excluded from subset of trees
→ predict i using only those trees
→ OOB estimate
```

OOB nie je universal replacement test setu. Bootstrap rows môžu zdieľať group/entity information s OOB sample, time ordering sa nerešpektuje a preprocessing fitnutý pred forest môže leaknúť. OOB evidence platí iba pre sampling assumptions.

Group/time deployment potrebuje corresponding external evaluation.

## 9. Random forest probabilities a calibration

Forest classification probability často priemeruje leaf class probabilities naprieč trees. Deep leaves a class weights ovplyvňujú output. Averaging znižuje variance, ale probability nemusí byť calibrated.

Class weighting mení fitted impurity/leaf statistics. `balanced_subsample` computes weights per bootstrap sample; semantics sa líšia od global weights. Probability calibration sa hodnotí na representative held-out data.

Forest ranking môže byť silný aj pri imperfect calibration. Expected-value formula však potrebuje calibrated probability alebo explicitne označený score.

## 10. Extra Trees a randomization boundary

Extremely randomized trees pridávajú random thresholds/splits, nie iba feature/bootstrap randomization. Vyššia randomization môže znížiť variance a zvýšiť bias. Exact ensemble family a parameters musia byť manifestované; „randomized trees“ nie je jeden algorithm.

Comparison musí používať same data, task a policy. Faster training alebo better score na one split nemusí generalizovať.

## 11. Gradient boosting ako stage-wise additive model

Gradient boosting buduje additive model sekvenčne. Každý nový weak learner sa fituje na direction, ktorá znižuje current loss — intuitívne opravuje errors predchádzajúceho ensemble.

```text
F₀(x) = initial prediction
F₁(x) = F₀(x) + η h₁(x)
F₂(x) = F₁(x) + η h₂(x)
...
F_M(x) = F_(M-1)(x) + η h_M(x)
```

`η` je learning rate/shrinkage. Small learning rate často vyžaduje viac stages. Trees sú typicky shallow/limited weak learners, ale high capacity combination môže stále overfitnúť.

Boosting nie je averaging independent trees. Trees sú dependent na current ensemble residual/gradient a order/stage count patrí artifact identity.

## 12. Gradient boosting loss a residual correction

Pre squared-error regression sa new tree môže fitovať na residuals. Pre differentiable loss všeobecne sa fituje negative gradient/pseudo-residuals.

```text
residual_m ≈ - ∂L(y, F(x)) / ∂F(x)
```

Loss function definuje correction signal. Classification log loss, quantile loss alebo robust losses vytvárajú different ensemble. Business metric nemusí byť differentiable training loss; validation stále hodnotí required outcome.

Sample weights a missing values menia gradients/splits. Exact implementation matters.

## 13. Learning rate, stages a overfitting

Learning rate a number of estimators/stages sú coupled hyperparameters. High rate + many stages môže overfit alebo diverge; low rate + few stages underfit.

```python
from sklearn.ensemble import GradientBoostingClassifier

model = GradientBoostingClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=3,
    min_samples_leaf=50,
    random_state=17,
)
```

Early stopping monitoruje validation loss a zastaví stages. Validation subset a patience/tolerance sú selection state. Ak internal random validation poruší group/time rules, early stopping leakne alebo vyberie nereálny iteration count.

Chosen stage count sa zaznamená a final refit procedure musí byť explicitná.

## 14. Histogram-based gradient boosting

Histogram gradient boosting binuje continuous feature values a hľadá splits nad bins, čo znižuje computational cost a môže podporovať missing values a large datasets efektívnejšie. Binning thresholds sú fitted state.

```python
from sklearn.ensemble import HistGradientBoostingClassifier

model = HistGradientBoostingClassifier(
    learning_rate=0.05,
    max_iter=300,
    max_leaf_nodes=31,
    min_samples_leaf=50,
    l2_regularization=1.0,
    random_state=17,
)
```

Histogram approximation môže meniť exact thresholds oproti traditional tree. `max_bins`, categorical support, monotonic constraints a missing routing patria generation. Benchmark musí zahŕňať fit/inference memory/latency, nie iba score.

## 15. Missing values v trees

Niektoré tree implementations podporujú missing values native a naučia routing alebo používajú default direction. Iné vyžadujú imputation. „Trees zvládnu missing“ nie je universal.

Native missing routing sa učí z training missing patterns. Ak production missingness znamená outage a training missing znamenalo new merchant, learned direction môže byť unsafe. Missing indicator/fallback a monitoring zostávajú needed.

Pipeline musí testovať all-missing feature, unseen category, sparse/dense input a schema mismatch according to chosen estimator.

## 16. Categorical features

Trees môžu pracovať s one-hot/ordinal encoding alebo native categorical split support podľa implementation. Ordinal codes môžu vytvoriť artificial ordering pre standard numeric tree. One-hot high cardinality zvyšuje dimensions a split opportunities.

Native categorical handling stále potrebuje category vocabulary, unknown/missing semantics a version compatibility. Category target statistics môžu leaknúť, ak computed unsafely.

Exact docs/implementation version treba overiť pri deployment-e; model artifact a serving runtime musia supportovať same categorical semantics.

## 17. Feature importance caveats

Impurity-based importance sumarizuje split improvements across trees. Môže favorizovať high-cardinality alebo continuous features s mnohými split opportunities. Correlated features si importance rozdelia alebo jedna dominuje.

Permutation importance meria score drop pri permutovaní feature na evaluation data, ale breaks correlations a závisí od metric/population. SHAP alebo local explanation methods majú vlastné assumptions a computational cost.

```text
feature importance
≠ causal effect
≠ fairness proof
≠ stability proof
```

Importance report musí uviesť model/data generation, method, held-out population a uncertainty/stability. High merchant ID importance môže signalizovať memorization.

## 18. Monotonic constraints

Niektoré boosting implementations podporujú monotonic constraints: prediction sa má s feature meniť iba jedným direction. Môžu encode domain guardrail, napríklad higher verified positive risk evidence nemá znižovať risk score, ale relation musí byť skutočne defensible.

Constraint sa aplikuje v model representation, nie automaticky business feature raw meaning. Correlated features a interactions môžu vytvoriť non-obvious global behavior. Constraint môže znížiť performance alebo zlepšiť robustness.

Manifest musí zaznamenať constraint vector/map a output feature order. Wrong mapping je critical bug.

## 19. Tree ensemble serving characteristics

Single tree inference je sequence comparisons, forest multiple trees a boosted ensemble stage sequence. Latency závisí od tree count, depth/leaves, implementation, batching a hardware. Artifact size a cache behavior môžu byť material.

```text
forest latency ≈ trees × average path cost / parallelism
boosting latency ≈ sequential stages × path cost
```

Formula je intuition, nie exact performance model. Load test must measure p50/p95/p99, throughput, memory, cold load a survivor capacity. Optimization/quantization/export môže zmeniť numeric output a artifact generation.

## 20. Robustness a out-of-range behavior

Trees extrapolate poorly outside training ranges: new extreme follows existing thresholds to a leaf and receives constant-like prediction. Linear regression extrapolates linearly, čo môže byť tiež wrong, ale behavior je different.

```text
training amount max = 100k
serving amount = 10M
→ tree routes to existing extreme leaf
```

Range monitoring and out-of-distribution fallback are required. Forest agreement alebo leaf support can signal uncertainty but are not calibrated confidence by default.

Adversarial feature manipulation near thresholds can flip paths. Sensitive action needs robust policy/human boundary.

## 21. Model comparison discipline

Compare linear, forest and boosting candidates on same split, preprocessing availability, feature schema, label, metric and policy. Trees may need different scaling but should not silently receive future or unavailable features.

```text
controlled constants:
dataset/split/target/business evaluation

allowed candidate differences:
model-specific preprocessing + estimator parameters
```

Report incremental gain, calibration, latency, memory, stability, interpretability, fallback and operational cost. Best offline metric is not automatically best production choice.

## 22. Worked incident `ML-PAY-85`

Atlas single tree grew deep until most leaves were nearly pure. Training AUC approached 1.0; time-test performance dropped. Random forest improved stability but impurity importance ranked hashed merchant ID and high-cardinality device fields above domain aggregates. Boosting achieved best captured loss at K, yet selected leaves with very small weighted support for rare campaign cohorts.

Internal early stopping used a random fraction of training rows, breaking merchant/time grouping. Missing values offline were imputed, while candidate HistGradientBoosting experiment used native missing routing. Probability outputs were compared without calibration and final queue policy differed.

```text
same headline: tree models
actual differences:
feature sets + missing semantics + CV/early-stopping split
+ class weights + calibration + policy
```

The initial „boosting wins“ verdict conflated algorithm gain with evaluation and pipeline differences.

## 23. Evidence-preserving containment a recovery

Tím zachoval tree structures, leaf support, bootstrap/OOB metadata, stage count, early-stopping history, feature importance reports, predictions a serving latency. Automatic promotion stopped.

Recovery rebuilt controlled candidates on same point-in-time features and grouped-temporal split. Internal early stopping used an allowed validation window. High-cardinality identity features were removed or separately evaluated for known/cold-start scenarios. Probabilities were calibrated on same protocol.

```text
logistic baseline
single constrained tree
random forest
histogram gradient boosting
→ same business top-K acceptance
```

Selected boosting artifact recorded binning, leaves, stage count, missing routing, constraints and runtime. Approved logistic pipeline remained fallback.

## 24. Acceptance contract

Single-tree positive path preukazuje growth/pruning parameters, leaf support, stable decision paths and generalization. Forest acceptance adds bootstrap/feature randomization, tree count, variance/stability and probability calibration. Boosting acceptance adds loss, learning rate, stages, early-stopping data and sequential artifact integrity.

Recovery must allow compatible fallback/rollback with feature and policy generations. Tree visualization or importance from wrong artifact is forbidden evidence.

Forbidden paths:

```text
pure training leaves sa vydávajú za generalization
OOB score nahrádza group/time test bez assumptions
high-cardinality impurity importance sa vydáva za truth
internal early stopping poruší split boundary
native/imputed missing semantics sa porovnávajú ako same pipeline
boosting score sa vydáva za calibrated probability
more trees/stages sa pridávajú bez latency/capacity evidence
```

Second-fit test checks reproducibility/tolerance given random seeds and parallelism. Second-cohort test checks leaf support, calibration, cold-start, out-of-range behavior, latency and fallback.

## Kontrolné otázky

1. Ako decision tree partitionuje feature space?
2. Čo split criterion optimalizuje a čo nie?
3. Ako depth, leaves a minimum samples riadia capacity?
4. Čo je pruning a `ccp_alpha`?
5. Čo decision path a leaf support preukazuje?
6. Ako random forest používa bootstrap a feature randomization?
7. Prečo OOB nie je universal test set?
8. Ako forest vytvára probability a prečo calibration nie je guaranteed?
9. Čím Extra Trees pridávajú randomization?
10. Ako gradient boosting buduje additive model?
11. Čo sú pseudo-residuals/negative gradients?
12. Ako learning rate súvisí s stage countom?
13. Aké riziko má early stopping validation split?
14. Čo histogram boosting binuje a prečo?
15. Prečo missing/categorical support závisí od implementation?
16. Aké biases má impurity feature importance?
17. Čo monotonic constraint môže a nemôže garantovať?
18. Ako trees behavior outside training range?
19. Prečo `ML-PAY-85` algorithm comparison nebol controlled?
20. Aké positive, recovery, forbidden a second-cohort tests uzatvárajú tree-ensemble contract?

## Glossary impact

Relevantné pojmy: decision tree, node, split, threshold, impurity, leaf, decision path, pre/post-pruning, cost-complexity, bootstrap, bagging, random forest, OOB estimate, feature subsampling, Extra Trees, gradient boosting, additive model, pseudo-residual, learning rate, stage, early stopping, histogram binning, native missing handling, impurity importance, permutation importance, monotonic constraint a tree-ensemble acceptance contract.

## Primárne zdroje

- [scikit-learn — Decision Trees](https://scikit-learn.org/stable/modules/tree.html)
- [scikit-learn — Ensembles: gradient boosting and random forests](https://scikit-learn.org/1.9/modules/ensemble.html)
- [scikit-learn — `DecisionTreeClassifier`](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html)
- [scikit-learn — `RandomForestClassifier`](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
- [scikit-learn — `HistGradientBoostingClassifier`](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingClassifier.html)
- [scikit-learn — Permutation feature importance](https://scikit-learn.org/stable/modules/permutation_importance.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Linear a logistic regression](linear-logistic-regression.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Neural network fundamentals →](neural-network-fundamentals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
