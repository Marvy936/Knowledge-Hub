# Regularization a early stopping

Regularization mení training procedure tak, aby model neoptimalizoval iba fit na observed training samples, ale preferoval jednoduchšie, stabilnejšie alebo inak constrained solutions. Early stopping používa validation evidence na výber training step-u skôr, než model pokračuje v prispôsobovaní sa training noise. Obe techniky môžu zlepšiť generalization, ale nevyriešia leakage, wrong target, missing population coverage ani serving skew. Ich strength, scope a checkpoint semantics musia byť explicitné.

Incident `ML-PAY-86` pokračoval pri Atlas neural candidate. Tím súčasne pridal layer L2, AdamW weight decay, dropout, batch normalization a early stopping, potom pripísal celý gain „regularization“. Custom loop však omitoval `model.losses`, takže layer L2 sa v jednom run-e nepoužila. AdamW decay zasahoval aj variables, ktoré experiment owner nechcel decayovať. Early stopping obnovil best weights, ale registry publikovala last optimizer state a iný export. Regularization generation bola nejasná a recovery nebola reprodukovateľná.

## 1. Dominantný regularization lifecycle

Regularization začína overfitting hypothesis a exact capacity/data contextom. Zvolená penalty, stochastic transformation alebo stopping rule sa zapojí do objective/training graphu. Strength sa vyberá na validation/CV, final artifact sa vytvorí podľa deklarovaného refit/checkpoint procedure a independent test/business evidence overí gain a guardrails.

```text
generalization diagnosis
→ regularization candidate + scope
→ training objective/graph change
→ train fit
→ validation selection
→ selected strength/checkpoint
→ final artifact/export
→ test/business evidence
→ monitoring a recovery
```

Regularization nie je one-dimensional knob. Multiple techniques interact; controlled experiment musí zaznamenať full combination.

## 2. Exact regularization subject

Regularization subject musí zachytiť všetky mechanizmy, ktoré menia objective, update alebo selected checkpoint, nie iba jeden spoločný názov experimentu. Manifest preto oddeľuje parameter penalties, optimizer decay, stochastic layers, data transformations a stopping policy vrátane scope-u a selection authority. Dve konfigurácie s rovnakým číselným koeficientom nie sú ekvivalentné, ak zasahujú iné variables alebo vstupujú do training lifecycle iným spôsobom.

```yaml
regularization_subject: ML-PAY-REG-2026-08-v3
model_subject: ML-PAY-DNN-2026-08-v2
parameter_penalties:
  kernel_l2: 0.0001
  bias_l2: 0.0
optimizer_decay:
  type: AdamW
  weight_decay: 0.0001
  exclusions: [bias, batch_normalization_scale, batch_normalization_offset]
stochastic:
  dropout:
    hidden_1: 0.2
    hidden_2: 0.1
data:
  augmentation: none
stopping:
  monitor: validation_captured_loss_at_2500
  mode: max
  patience: 8
  min_delta: 0.002
  restore_best_weights: true
checkpoint_authority: complete-checkpoint-at-best-step
selection_subject: grouped-temporal-validation-v3
```

Manifest oddeľuje loss penalty od decoupled optimizer decay a training-time stochastic layers od checkpoint selection. Rovnaký numeric `0.0001` v L2 a AdamW neznamená rovnakú update semantics.

## 3. L2 regularization

L2 penalty pridáva squared parameter norm k data loss:

```text
L_total = L_data + λ Σ_j w_j²
```

Gradient penalty shrinkuje large weights. V linear models ide o Ridge-like regularization; v neural layers kernel regularizer pridáva term do `model.losses`.

```python
import tensorflow as tf

layer = tf.keras.layers.Dense(
    128,
    activation="relu",
    kernel_regularizer=tf.keras.regularizers.L2(1e-4),
)
```

Custom loop musí regularization loss pridať. Scope matters: kernel, bias, embedding alebo normalization variables. Penalizing all variables indiscriminately may harm.

L2 strength interacts with feature scale and dataset/batch reduction. If data loss reduction changes, same λ has different relative weight.

## 4. L1 a sparsity

L1 penalty:

```text
L_total = L_data + λ Σ_j |w_j|
```

encourages exact/near zeros and can create sparse solutions, especially in linear models. With correlated features selection may be unstable. Sparse weights do not guarantee cheaper inference unless storage/runtime exploits sparsity.

```python
kernel_regularizer=tf.keras.regularizers.L1(1e-5)
```

L1 is non-differentiable at zero but subgradient/proximal methods handle it. Neural weight sparsity can require pruning/fine-tuning/export support.

## 5. Elastic Net

Elastic Net combines L1 and L2, balancing sparsity and grouped shrinkage.

```text
L_total = L_data + λ₁||w||₁ + λ₂||w||²₂
```

In scikit-learn linear estimators parameters may be `alpha` and `l1_ratio`, with estimator-specific scaling. Exact API semantics must be pinned.

Elastic Net is hyperparameter family, not single setting. Selection belongs CV/validation and final coefficients need stability analysis.

## 6. Weight decay oproti L2

For plain SGD under some conditions, L2 penalty and multiplicative weight decay can be equivalent. For adaptive optimizers, decoupled weight decay (AdamW) is distinct from L2 gradient penalty because adaptive preconditioning transforms loss gradients.

```text
L2:
add λw to gradient then optimizer transforms it

AdamW:
optimizer gradient update + separate parameter decay
```

Using both layer L2 and AdamW may be intentional or accidental double regularization. Manifest and ablation decide. Optimizer exclusions may need custom policy.

## 7. Constraints

Hard constraints project or clip parameters to allowed set, e.g. max norm or non-negative weights.

```python
layer = tf.keras.layers.Dense(
    64,
    kernel_constraint=tf.keras.constraints.MaxNorm(max_value=3.0),
)
```

Constraint runs after update according to framework. It is not same as soft penalty. Constraint can encode stability but may interfere with optimizer moments; optimizer still remembers pre-projection dynamics.

Monotonic tree constraints are analogous model-structure guardrails, but do not replace business policy.

## 8. Dropout

Dropout randomly masks activations during training and disables masking during inference.

```python
x = tf.keras.layers.Dropout(0.2)(x)
```

It creates stochastic ensemble-like training and discourages fragile co-adaptation. Too high rate can underfit. Dropout rate and layer placement matter.

Training/inference mode is critical. Serving with dropout active makes outputs stochastic and incompatible. Evaluation callbacks must run inference mode.

Dropout is not missing-data simulation unless explicitly designed; random activation masks differ from business feature outages.

## 9. Noise injection

Noise can be added to inputs, activations, gradients or parameters to improve robustness/regularization. Noise distribution/scale must reflect intended invariance and not corrupt labels.

```python
x = tf.keras.layers.GaussianNoise(stddev=0.01)(x)
```

Layer typically acts only during training. Noise can mimic sensor variation but inappropriate noise on categorical/monetary features creates invalid samples.

Differential privacy noise has separate privacy accounting and should not be conflated with generic regularization.

## 10. Data augmentation

Augmentation transforms training samples while preserving target semantics: crop/flip images, audio perturbation, text operations or domain-specific transformations. For payments, arbitrary amount/country changes may change label and are unsafe.

Augmentation policy is versioned and applied only within training split. Augmented relatives remain same group. Validation/test remain natural unless specific robustness set is separate.

Gain should be evaluated by relevant invariance/robustness cohorts. More synthetic rows do not equal more independent information.

## 11. Batch normalization as implicit regularization

Batch normalization can add stochasticity through batch statistics and improve optimization. It is not primarily a universal regularizer and has training/inference state. Effect changes with batch size and distributed strategy.

Moving statistics are model state, not regularization config alone. Comparing dropout/BN variants requires complete checkpoint/export parity.

## 12. Early stopping mechanism

Early stopping monitors validation metric after evaluations. When no sufficient improvement for patience, training stops; selected weights may be best or last according to configuration.

```python
callback = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss",
    mode="min",
    patience=8,
    min_delta=1e-4,
    restore_best_weights=True,
)
```

Patience counts evaluation events, not universally epochs. Evaluation frequency and metric noise change behavior. Warm-up/start epoch may prevent stopping before meaningful learning.

## 13. Early stopping as implicit regularization

In iterative models, later steps can fit finer/noisier directions. Stopping early limits effective complexity. It resembles regularization but strength depends on trajectory, optimizer and data order.

Two runs stopped at epoch 20 with different learning rates are not equally regularized. Selected global step and path matter.

Early stopping consumes validation feedback. Repeated changes based on same validation can overfit selection process.

## 14. Monitor selection

Monitoring training loss does not regularize generalization. Validation loss is common, but business metric may differ. Monitoring noisy top-K metric can select unstable checkpoint; monitoring smooth BCE may choose worse business checkpoint.

Use one declared selection metric and guardrails. Multi-objective policy may reject checkpoint even if primary improves.

```yaml
primary: validation_average_precision
required_guardrails:
  calibration_error: <= 0.03
  captured_loss_at_2500: no_regression
  campaign_cohort_recall: >= 0.60
```

Test set must not monitor stopping.

## 15. Patience a min_delta

Patience tolerates temporary/noisy plateau. `min_delta` defines meaningful improvement. Too small tracks noise and prolongs; too large stops real gradual progress.

Scale depends metric. `0.001` AP and `1000` euro captured-loss units differ. Relative delta may be needed but framework behavior exact.

Estimate metric variance to choose settings. One noisy positive batch should not reset patience unpredictably.

## 16. Restore best weights and optimizer mismatch

`restore_best_weights=True` restores model weights from best epoch in memory, but optimizer state may remain from stop epoch. For inference export only weights/model state may suffice. For resume training this mismatch is not exact trajectory.

Safer pattern: checkpoint complete model+optimizer at each improvement and restore exact selected checkpoint for resume. Registry distinguishes inference export from resumable checkpoint.

```text
best inference weights
≠ complete best training checkpoint unless stored so
```

## 17. Cross-validation and regularization selection

L1/L2 strength, dropout, depth, early-stopping rule and augmentation are hyperparameters selected using validation/CV. Pipeline must fit regularization-dependent transforms per fold.

Nested evaluation may estimate whole selection procedure. Search space and trials influence overfitting to CV. Stability across folds/seeds matters.

## 18. Regularization curves

Validation curve over `alpha`, `C`, dropout or tree depth shows underfit-to-overfit transition.

```text
strong regularization:
train low, validation low → underfit

moderate:
validation best

weak:
train high, gap grows → overfit
```

This ideal pattern may be noisy/nonmonotonic. Other hyperparameters interact. Plot train and validation, not validation only.

## 19. Regularization and calibration

Regularization changes score distribution and probability calibration. Strong shrinkage can reduce extreme logits; class weights/dropout/early stopping also affect. Recalibrate after selecting final model/procedure using allowed data.

Calibration layer can overfit; it is separate artifact. Do not tune regularization on test calibration.

## 20. Regularization and fairness/cohorts

Aggregate generalization gain can harm rare cohort if regularization removes features needed for it. Conversely, reducing memorization may improve unseen groups. Evaluate required cohorts and error disparities.

Protected/proxy constraints require responsible-AI analysis; generic L2 does not guarantee fairness.

## 21. Regularization and serving cost

L1 sparsity may not reduce latency automatically. Dropout inactive at inference adds no mask cost but architecture remains. Smaller/pruned models can reduce cost; early stopping changes weights, not graph size.

Regularization selection should include serving metrics only where technique changes artifact/runtime. Do not claim cost gain from lower coefficient magnitude.

## 22. Worked incident `ML-PAY-86`

Atlas experiment matrix mixed:

```text
run A: layer L2 + Adam
run B: AdamW + dropout
run C: layer L2 + AdamW + dropout + BN + early stopping
```

Custom loop for C calculated only data loss and omitted `model.losses`; layer L2 existed in config but not objective. AdamW decay applied broadly. Early stopping monitored validation BCE and restored weights, but registry packaged last checkpoint from stop epoch. Resume used last optimizer state with best weights, creating hybrid trajectory.

The team reported „regularization improved AP 3%“ without ablation or exact artifact. Campaign cohort worsened because early-stopping metric favored majority. Dropout was accidentally active in one evaluation helper.

## 23. Evidence-preserving containment a recovery

Tím preserved configs, per-component losses, optimizer decay settings, dropout/BN modes, callback history, best/last checkpoints and exports. Candidate promotion stopped.

Recovery built controlled ablations from same initialization/data. Custom loop added regularization loss and tests. AdamW exclusions were explicit. Complete checkpoints were written on improvement. Primary/guardrail metrics included campaign cohort.

```text
baseline
→ +L2
→ +dropout
→ AdamW alternative
→ early stopping
→ controlled combinations
→ independent test/business acceptance
```

Final artifact read-back matched selected complete checkpoint and inference mode.

## 24. Acceptance contract

Positive path preukazuje regularization type, strength, variable/layer scope, objective inclusion, training-only behavior, validation selection and selected complete checkpoint/export. Gain is measured against same baseline and cohorts.

Recovery allows exact selected checkpoint restore or compatible baseline rollback. Configuration that is present but not executed is forbidden.

Forbidden paths:

```text
layer regularizer exists but custom loop omits model.losses
L2 and AdamW are treated as identical or doubled unknowingly
dropout/noise active during serving unintentionally
early stopping monitors test set
best weights are paired with incompatible last optimizer state and called exact resume
patience/min_delta/frequency are missing from generation
aggregate gain hides required-cohort regression
regularization is claimed to fix leakage or wrong target
```

Second-resume/export test verifies complete selected state and inference parity. Second-cohort test checks stability/generalization and fallback.

## Kontrolné otázky

1. Čo regularization mení?
2. Ako L2, L1 a Elastic Net differ?
3. Prečo same λ depends on loss reduction/feature scale?
4. Čím AdamW decay differs from L2 loss penalty?
5. Čo constraints do after update?
6. Ako dropout works in training vs inference?
7. Kedy noise/augmentation is invalid?
8. Prečo batch normalization is not simple universal regularizer?
9. Ako early stopping selects checkpoint?
10. Prečo early stopping is implicit regularization?
11. Ako monitor, patience and min_delta affect selection?
12. Čo `restore_best_weights` may not restore?
13. Ako CV/nested evaluation applies to regularization?
14. Čo regularization curve diagnoses?
15. Ako regularization affects calibration and cohorts?
16. Prečo sparsity does not automatically reduce serving cost?
17. Čo failed in `ML-PAY-86` regularization experiment?
18. Aké positive, recovery, forbidden and second-export tests close regularization contract?

## Glossary impact

Relevantné pojmy: regularization, L1/L2, Elastic Net, weight decay, AdamW, constraint, dropout, noise injection, data augmentation, implicit regularization, early stopping, monitor, patience, min_delta, best weights, complete checkpoint, ablation, regularization curve a regularization acceptance contract.

## Primárne zdroje

- [scikit-learn — Linear Models and regularization](https://scikit-learn.org/stable/modules/linear_model.html)
- [TensorFlow — Overfit and underfit tutorial](https://www.tensorflow.org/tutorials/keras/overfit_and_underfit)
- [TensorFlow — Keras regularizers](https://www.tensorflow.org/api_docs/python/tf/keras/regularizers)
- [TensorFlow — Dropout](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dropout)
- [TensorFlow — EarlyStopping](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/EarlyStopping)
- [TensorFlow — AdamW](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/AdamW)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Overfitting, underfitting, bias a variance](overfitting-underfitting-bias-variance.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Hyperparameters a hyperparameter optimization →](hyperparameters-hyperparameter-optimization.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
