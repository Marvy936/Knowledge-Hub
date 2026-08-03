# Overfitting, underfitting, bias a variance

Overfitting a underfitting opisujú relationship medzi fitted modelom, training evidence a generalization na relevantnú unseen population. Bias a variance sú analytické pojmy, ktoré pomáhajú rozlíšiť systematickú chybu model class/procedure od citlivosti na konkrétny training sample. Tieto terms sa nesmú redukovať na slogan „train score high, test score low“. Shared leakage môže urobiť train aj validation score vysoké; distribution shift môže zhoršiť validation bez klasického variance problemu; noisy labels môžu obmedziť achievable performance aj pri správnej capacity.

Incident `ML-PAY-86` pokračoval tým, že Atlas označil logistic baseline za underfit podľa lower training AUC a neural model za overfit podľa validation gapu. Comparison však používala iné feature sets a neural validation obsahovala campaign cohort absent v trainingu. Deep model zároveň memorized merchant IDs a random seeds menili top-K order. Tím chcel pridať ešte väčšiu sieť, hoci dominantný problem bol variance, population mismatch a label noise. Táto kapitola fixuje generalization diagnosis ako exact subject.

## 1. Dominantný generalization lifecycle

Generalization analysis začína fixed task, data generation a split. Candidate procedures sa fitujú na training samples; performance sa meria na training, validation, resamples, cohorts a time windows. Learning curves a seed/fold variability oddeľujú capacity/data effects. Diagnosis vedie k data, representation, regularization, model alebo evaluation change a končí independent test/business acceptance.

```text
task + population + split
→ model class/procedure + capacity
→ fit on training sample
→ train error
→ validation error by fold/time/cohort
→ learning/validation curves + variance
→ hypothesis: underfit/overfit/shift/noise/bug
→ bounded change
→ independent acceptance
```

Overfitting je property procedure relative to data and evaluation scenario, not permanent label model family. Same neural architecture may underfit huge complex task or overfit small dataset.

## 2. Exact generalization subject

Generalization verdict má význam iba pre presne identifikovanú kombináciu tasku, population, splitu, feature/model procedure, regularization a evaluation cohorts. Manifest nižšie preto nie je administratívna metadata: určuje, ktoré training a validation výsledky možno porovnať a ktoré patria k inej experimentálnej generácii. Bez tohto contractu sa rozdiel skóre môže nesprávne pripísať capacity alebo variance, hoci sa medzi runmi zmenili dáta, features alebo policy.

```yaml
generalization_subject: ML-PAY-GEN-2026-08-v2
task: operation-level loss-risk ranking
population: EU card-not-present operations
split: SPLIT-ML-PAY-84-v3
candidate_procedure:
  feature_schema: risk-v8
  model_family: dense-neural-network
  capacity: 410k_parameters
  regularization: dropout-0.2+l2-1e-4
  optimization: ML-PAY-GD-2026-08-v2
training_samples: 8.4m
validation_samples: 1.2m
cohorts:
  - known_merchants
  - unseen_merchants
  - campaign_traffic
metrics:
  train: [log_loss, average_precision]
  validation: [log_loss, average_precision, captured_loss_at_2500]
repeats:
  seeds: [17, 23, 41, 59, 71]
```

Subject prevents comparison of „train vs validation“ across different feature, label or policy generations. Capacity and regularization belong to procedure identity. Cohort/time metrics distinguish generic gap from localized shift.

## 3. Underfitting

Underfitting occurs when procedure cannot capture useful relationship or optimization fails to fit it sufficiently. Typical evidence: high training error and similarly high validation error relative to achievable baseline/business needs. Causes include insufficient features/capacity, excessive regularization, poor objective, short/failed optimization or noisy/incorrect targets.

```text
train error high
validation error high and similar
→ high-bias/underfit hypothesis
```

This pattern is not proof. If labels are random/noisy or features unavailable, no model can fit meaningful signal. If training pipeline bug freezes weights, architecture capacity is not root cause.

Remedies are hypothesis-specific: improve data/target/features, reduce regularization, increase capacity, optimize longer/better or change formulation. Simply larger model may fit leakage/noise.

## 4. Overfitting

Overfitting occurs when procedure fits idiosyncrasies/noise of training sample that do not generalize. Evidence often includes very low training error, higher validation error, unstable predictions across folds/seeds or complex behavior in low-support regions.

```text
train error continues ↓
validation error stops improving then ↑
→ overfitting after best checkpoint
```

Overfitting can occur at feature selection, preprocessing, hyperparameter search and human iteration level, not only model weights. Repeated validation optimization overfits selection process.

Leakage can mimic good generalization, so absence of gap does not prove no overfit. Correct independent split is prerequisite.

## 5. Bias as systematic approximation/procedure error

Bias in bias-variance framing is expected difference between learned prediction and true target function across possible training samples, under assumptions. High bias means procedure systematically misses structure. A linear model for strongly nonlinear relation may have approximation bias; wrong target or missing feature introduces broader system bias.

Bias here is not social/fairness bias, though systems can have both. Terminology must state context.

```text
many training samples
→ fitted models all make similar systematic error
→ high bias
```

Observed residual/cohort patterns support hypothesis but true function is unknown. Bias is conceptual decomposition, not directly measured from one dataset.

## 6. Variance as training-sample sensitivity

Variance describes how fitted prediction changes across possible training samples. High-capacity model may learn different rules from small perturbations. Estimate through cross-validation, bootstrap, repeated seeds/time windows or influence diagnostics.

```text
same procedure
+ slightly different train sample/seed
→ materially different predictions/top-K order
```

Random seed variance may include initialization/optimization noise, while fold variance includes data composition. Separate sources where possible. Stable aggregate metric can hide unstable individual decisions.

## 7. Bias-variance-noise decomposition

For squared-error regression under standard setup, expected prediction error can be decomposed conceptually into squared bias, variance and irreducible noise:

```text
expected error = bias² + variance + irreducible noise
```

This exact formula does not transfer unchanged to every classification/ranking metric. It remains mental model: increasing capacity often lowers approximation bias and raises variance; more representative data often lowers variance; label/process noise sets floor.

Irreducible noise relative to available information is not excuse to ignore measurement improvements. What appears irreducible may be missing feature or inconsistent label process.

## 8. Model capacity

Capacity is ability to represent complex functions. For trees: depth/leaves; linear models: features/interactions and regularization; neural networks: architecture/parameters. Capacity is effective, not just raw parameter count: strong regularization, optimization or data can limit use.

```text
low capacity → possible high bias
high capacity + limited data → possible high variance
```

Capacity selection uses validation curves and business constraints. Maximum expressive power is not target.

## 9. Training size a learning curves

Learning curve plots train and validation score versus number of training samples. It helps distinguish data-limited variance from capacity-limited bias.

```python
from sklearn.model_selection import learning_curve

train_sizes, train_scores, valid_scores = learning_curve(
    estimator,
    X,
    y,
    groups=merchant_ids,
    cv=group_cv,
    scoring="average_precision",
    train_sizes=[0.1, 0.25, 0.5, 0.75, 1.0],
    n_jobs=-1,
)
```

If train score high, validation lower but improving with more data, more representative data may help. If both plateau low and close, capacity/features/objective may limit. Curves require same correct split logic at each size; random subset may alter time/cohort distribution.

## 10. Validation curves

Validation curve varies one hyperparameter, such as tree depth or regularization, and reports train/validation scores.

```python
from sklearn.model_selection import validation_curve

train_scores, valid_scores = validation_curve(
    estimator,
    X,
    y,
    param_name="max_depth",
    param_range=[2, 4, 6, 10, None],
    cv=group_cv,
    scoring="average_precision",
)
```

Low depth may underfit; high depth may increase train score and gap. One-dimensional curve ignores interactions with other hyperparameters and search selection bias.

## 11. Approximation, estimation a optimization error

Observed error nie je jedna homogénna veličina. Diagnostika musí určiť, či limit vzniká v reprezentácii model class, v konečnom a noisy training sample, v samotnom optimization procedure alebo v evaluation contracte. Každý typ chyby predpovedá iný evidence pattern a vyžaduje inú zmenu; bez tohto rozdelenia tím ľahko zvýši capacity, predĺži training alebo pridá dáta bez zásahu do skutočnej príčiny.

- approximation error — model class nedokáže reprezentovať požadovanú funkciu ani pri ideálnom fitnutí v rámci danej class;
- estimation error — finite alebo noisy data spôsobia, že fitted function sa odlišuje od najlepšej funkcie dostupnej v zvolenej class;
- optimization error — training procedure nenašla dostatočne dobré parameters pre deklarovaný empirical objective;
- evaluation error — metric, split alebo implementation neodhaduje scenár, podľa ktorého sa bude rozhodovať v produkcii.

Increasing model capacity môže znížiť approximation error, ale zároveň zvýšiť estimation variance. Training longer rieši iba optimization error a nepomôže pri wrong targete, leakage alebo chybnom splite. Taxonómia preto viaže každú remediation na falzifikovateľnú hypotézu namiesto náhodného tuningu.

## 12. Label noise

Labels may be incorrect, ambiguous, delayed or proxy. High-capacity models can eventually memorize random labels, lowering train loss while validation/business quality degrades.

```text
clean pattern learned early
→ later epochs fit inconsistent/noisy labels
```

Early stopping/regularization may help, but root solution can be label audit, adjudication, uncertainty or robust objective. Noise may be cohort-dependent and create fairness issues.

## 13. Distribution shift oproti overfitting

Validation gap can arise because validation population differs legitimately from training: new campaign, country, policy or adversary. Calling it overfit may lead to regularization when need is data coverage/retraining/segmented policy.

```text
train: normal months
validation: campaign month
```

Use cohort/time breakdown, feature distributions and support coverage. Model may generalize well in-distribution and fail OOD. Acceptance should include intended future scenarios.

## 14. Leakage and duplicate effects

Leakage can reduce train-validation gap artificially. Duplicates/related samples make high-variance memorization look like generalization. Before bias-variance diagnosis verify split/group/time integrity and preprocessing fit boundary.

```text
high train + high validation score
can still mean shared entity leakage
```

`ML-PAY-84` boundaries remain prerequisites for `ML-PAY-86` capacity analysis.

## 15. Seed and fold stability

Train multiple seeds and folds; compare metric distribution and individual predictions/ranks.

```json
{
  "validation_ap_mean": 0.312,
  "validation_ap_std": 0.018,
  "top2500_jaccard_mean": 0.71,
  "captured_loss_std_pct": 9.4
}
```

Top-K Jaccard instability may matter operationally even if AP stable. Report best/mean/worst, not only best seed. Selecting best seed is hyperparameter optimization and biases estimate.

## 16. Cohort-specific under/overfit

Model can underfit one cohort and overfit another. Known merchants may be memorized while unseen merchants have high bias. Rare classes may have high variance.

```text
known merchant: train/val strong
unseen merchant: both weak
campaign cohort: val unstable
```

Aggregate metrics weight majority. Define required cohorts, minimum support and guardrails. Different fallback or model may be needed, but complexity must be governed.

## 17. Feature count and dimensionality

Many features relative to effective independent samples increase variance, especially high-cardinality sparse data. Regularized linear models can handle high dimensions but selection/stability matter. Neural/tree models can memorize IDs.

Effective sample size may be far lower than row count due to groups/retries/time correlation. `84M` attempts are not `84M` independent operations.

## 18. Data augmentation

Augmentation creates transformed training samples that preserve label semantics, common in image/audio/text. It can reduce variance and encode invariances, but invalid augmentation introduces label noise or unrealistic data.

Augmented relatives must stay within same split. Augmentation policy/version belongs training generation. It does not increase independent real-world coverage equally.

## 19. Ensembling and variance

Averaging diverse models can reduce variance. Random forests use this mechanism. Neural ensembles across seeds/folds may improve stability/calibration but multiply serving cost.

```text
ensemble benefit requires errors not perfectly correlated
```

Ensemble selection must use validation, and final acceptance covers aggregate artifact membership, weights, latency and fallback. It does not fix common bias/leakage.

## 20. Double descent boundary

Modern high-capacity models can show non-classical curves where test error worsens near interpolation then improves with further capacity/training. This does not invalidate bias-variance reasoning; it warns that simple monotonic capacity story may be incomplete.

Do not use double descent as excuse to skip controlled curves. Empirical evidence on exact task still decides.

## 21. Operational overfitting

System can overfit offline metric while harming operations: complex model increases latency, retries, analyst load or brittle dependencies. Business acceptance includes serving and workflow.

```text
+0.5% AP
-30% throughput
+2x missing-feature fallbacks
→ possibly worse system
```

Model selection must optimize declared multi-layer outcome, not leaderboard only.

## 22. Worked incident `ML-PAY-86`

Atlas results:

```text
logistic: train AP 0.28, validation AP 0.27
boosting: train AP 0.48, validation AP 0.34
neural:   train AP 0.62, validation AP 0.33
```

Tím called logistic underfit and neural overfit. But neural used merchant IDs absent in logistic, campaign cohort dominated validation and random seed changed top-2500 membership. Boosting/neural validation on normal cohort was `0.38`, campaign `0.19`. Label audit found inconsistent outcomes in campaign flow.

Learning curve showed logistic both scores improving little with data (representation bias); neural gap narrowed with more operation-level data but remained high for unseen merchants (memorization). Larger neural model increased train score, not business metric.

## 23. Evidence-preserving containment a recovery

Tím preserved per-seed/fold artifacts, curves, predictions, cohort membership, labels and feature schemas. Model promotion stopped.

Recovery used controlled same-feature comparisons, separate known/unseen/campaign cohorts, learning/validation curves and label audit. Merchant IDs were removed; regularization/early stopping were tuned on validation, not test. A boosting candidate with slightly lower headline AP but lower variance and better top-K stability was preferred.

```text
verify split/leakage
→ decompose cohorts
→ learning/validation curves
→ seed/fold stability
→ label audit
→ bounded capacity/regularization change
→ independent acceptance
```

## 24. Acceptance contract

Positive path preukazuje correct split, same comparison inputs, train/validation/cohort metrics, learning/validation curves and seed/fold stability. Diagnosis distinguishes approximation, estimation, optimization, noise and shift.

Recovery changes one hypothesis axis where possible and preserves baseline. More data/model/regularization must have evidence.

Forbidden paths:

```text
train-validation gap alone proves overfitting
low train score automatically means insufficient model size
leakage-free assumption is skipped
best seed is reported as expected performance
aggregate metric hides failing required cohort
validation shift is mislabeled as variance without distribution evidence
more parameters are added without learning-curve evidence
training metric gain overrides operational/business regression
```

Second-seed/fold test confirms stability; second-time/cohort test confirms generalization and fallback on newer data.

## Kontrolné otázky

1. Čo underfitting a overfitting opisujú?
2. Ako bias v bias-variance framing differs from fairness bias?
3. Čo variance znamená?
4. Aká je conceptual bias²+variance+noise decomposition?
5. Čo model capacity zahŕňa?
6. Ako learning curve distinguishes data-limited vs capacity-limited?
7. Čo validation curve shows?
8. Ako approximation, estimation, optimization a evaluation error differ?
9. Ako label noise interacts with capacity?
10. Prečo distribution shift is not automatically overfitting?
11. Ako leakage hides variance?
12. Prečo metrics across seeds are insufficient without decision stability?
13. Ako cohort-specific over/underfit arises?
14. Čo effective sample size means with groups?
15. Ako augmentation and ensembling affect variance?
16. Čo operational overfitting means?
17. Čo revealed root causes in `ML-PAY-86`?
18. Aké positive, recovery, forbidden and second-cohort tests close generalization contract?

## Glossary impact

Relevantné pojmy: underfitting, overfitting, generalization gap, bias, variance, irreducible noise, model capacity, learning curve, validation curve, approximation/estimation/optimization/evaluation error, label noise, distribution shift, seed/fold stability, cohort-specific generalization, effective sample size, augmentation, ensembling, double descent, operational overfitting a generalization acceptance contract.

## Primárne zdroje

- [scikit-learn — Validation curves and learning curves](https://scikit-learn.org/stable/modules/learning_curve.html)
- [scikit-learn — Underfitting vs. overfitting example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_underfitting_overfitting.html)
- [TensorFlow — Overfit and underfit tutorial](https://www.tensorflow.org/tutorials/keras/overfit_and_underfit)
- [scikit-learn — Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [scikit-learn — Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Gradient descent, learning rate a convergence](gradient-descent-learning-rate-convergence.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Regularization a early stopping →](regularization-early-stopping.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
