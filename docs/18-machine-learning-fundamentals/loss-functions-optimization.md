# Loss functions a optimization

Loss function prevádza prediction a target na training signal. Optimizer používa gradients tohto signalu na zmenu model parameters. Ani loss, ani optimizer však nie sú business objective samy osebe. Model môže úspešne minimalizovať binary cross-entropy a pritom zhoršiť captured loss v top `2 500` operations, fairness konkrétneho cohortu, calibration alebo serving latency. Training preto potrebuje explicitný reťazec od per-sample lossu cez reduction, regularization, gradients, optimizer state a convergence až po validation a production acceptance.

Incident `ML-PAY-85` pokračoval pri Atlas neural candidate. Model outputoval sigmoid probability, ale training configuration používala `BinaryCrossentropy(from_logits=True)`, takže loss interpretoval probability ako unbounded logit. Iný experiment aplikoval sigmoid aj v model-i aj v custom loss-e. Tím zvýšil learning rate, aby zrýchlil training, no gradients začali oscilovať a mixed-precision run produkoval `NaN`. Po preempted jobe sa obnovili iba weights bez Adam momentov a learning-rate schedule step-u. Training loss po resume klesal, ale top-K business metric a calibration sa zhoršili. Táto kapitola fixuje exact optimization subject a dôkaznú hranicu.

## 1. Dominantný objective-to-update lifecycle

Optimization začína output a target semantics. Loss vypočíta per-sample penalty alebo structured objective. Sample/class weights a reduction vytvoria batch scalar. Regularization pridá penalty na parameters alebo activations. Automatic differentiation vypočíta gradients a optimizer transformuje gradients spolu so svojím stateom na parameter update. Validation a business metrics následne hodnotia, či znižovanie training objective-u vytvára desired generalization.

```text
model output semantics + target
→ per-example loss
→ sample/class weighting
→ reduction over batch/distribution
→ regularization terms
→ scalar training objective
→ gradients
→ clipping/scaling/aggregation
→ optimizer state transition
→ updated parameters
→ validation/business evidence
```

Každá vrstva môže zmeniť effective objective. Rovnaký loss class s inou reduction, weights alebo batch composition nie je rovnaký training experiment. Rovnaké weights po resume s prázdnym optimizer stateom nie sú pokračovaním tej istej optimization trajectory.

## 2. Exact optimization subject

Optimization manifest musí spojiť model output, target, loss configuration, reduction, weighting, optimizer, learning-rate schedule, gradient controls, numeric precision, batch semantics, checkpoint state a validation authority. Bez tohto subjectu sa „Adam + BCE“ nedá reprodukovať ani bezpečne resume-núť.

```yaml
optimization_subject: ML-PAY-OPT-2026-08-v3
model_subject: ML-PAY-DNN-2026-08-v2
output:
  name: loss_logit
  shape: [batch, 1]
  semantics: unbounded binary logit
target:
  name: confirmed_loss_within_30d
  values: [0, 1]
loss:
  type: BinaryCrossentropy
  from_logits: true
  label_smoothing: 0.0
  reduction: sum_over_batch_size
weights:
  class_weight: null
  sample_weight: recoverable_amount_policy-v2
regularization:
  kernel_l2: 0.0001
optimizer:
  type: AdamW
  learning_rate: cosine-warmup-v2
  beta_1: 0.9
  beta_2: 0.999
  epsilon: 1.0e-7
  weight_decay: 0.0001
gradients:
  global_clipnorm: 1.0
precision:
  policy: mixed_float16
  loss_scaling: dynamic
batch:
  per_replica: 256
  replicas: 4
  accumulation_steps: 2
  global_effective: 2048
checkpoint:
  includes: [model, optimizer_slots, global_step, schedule_state]
validation_subject: SPLIT-ML-PAY-84-v3/validation
```

Manifest vysvetľuje, čo exact scalar optimizer minimalizuje a ako sa update vytvára. Business top-K metric zostáva samostatným validation verdictom a nesmie byť odvodená iba z decreasing training loss.

## 3. Loss ako surrogate objective

Training loss je computational objective chosen to make parameters learnable. Často je differentiable surrogate pre desired decision. Binary cross-entropy optimalizuje probabilistic classification fit, nie priamo analyst capacity alebo captured recoverable loss. Mean squared error penalizuje squared numeric errors, nie service-level cost každej chyby.

```text
business objective:
maximize recoverable loss captured in top 2500 reviews/day

training surrogate:
weighted binary cross-entropy over operation labels
```

Surrogate môže byť vhodná, ak improvements korelujú s business outcome and downstream policy is validated. Táto relationship sa musí empiricky preukázať na validation/test and production shadow data. Optimization success means lower defined objective for observed data; it does not mean the business problem is solved.

## 4. Per-example loss a reduction

Loss API môže vracať per-example values alebo reduced scalar. Optimizer potrebuje scalar alebo explicitne aggregated gradients. Reduction semantics matter especially with variable batch sizes, sample weights and distributed training.

```python
import tensorflow as tf

loss_fn = tf.keras.losses.BinaryCrossentropy(
    from_logits=True,
    reduction="none",
)
per_example = loss_fn(y_true, logits)
weighted = per_example * sample_weight
objective = tf.reduce_sum(weighted) / tf.reduce_sum(sample_weight)
```

`mean(per_example * weight)` a `sum(weighted) / sum(weight)` are not generally identical. The first scales with average weight; the second normalizes by total weight. Framework built-in reduction has exact documented semantics that must be pinned and tested.

In distributed training, per-replica loss scaling must produce a global objective independent of replica count when intended. A bug can effectively multiply learning rate by number of replicas.

## 5. Regression losses: MSE, MAE a Huber

Mean squared error:

```text
MSE = (1/n) Σ (yᵢ - ŷᵢ)²
```

Squared penalty emphasizes large residuals and has smooth gradient. It can be sensitive to outliers and heavy-tailed targets. Root mean squared error changes reporting unit but minimizing RMSE or MSE yields same ordering for fixed data; gradient implementations typically optimize MSE.

Mean absolute error:

```text
MAE = (1/n) Σ |yᵢ - ŷᵢ|
```

MAE is more robust to large residuals but is non-differentiable exactly at zero; frameworks use a valid subgradient. It estimates conditional median under common assumptions, while MSE relates to conditional mean.

Huber loss combines quadratic behavior near zero and linear behavior for large residuals:

```text
Lδ(a) = 0.5 a²                   if |a| <= δ
      = δ(|a| - 0.5δ)            otherwise
```

`δ` controls transition and is a hyperparameter tied to target scale. Standardizing target changes the practical meaning of `δ`. Loss choice must reflect target distribution and error consequences, not generic robustness branding.

## 6. Quantile loss

Quantile or pinball loss estimates conditional quantiles. For quantile `τ`, underprediction and overprediction have asymmetric slopes.

```text
Lτ(y, ŷ) = τ(y-ŷ)       if y >= ŷ
         = (τ-1)(y-ŷ)   otherwise
```

A `0.9` quantile model can estimate an upper conditional level useful for capacity or risk bounds. It is not a calibrated probability that target exceeds arbitrary threshold without further assumptions. Multiple quantiles can cross and may require constraints or post-processing.

Atlas could use quantile regression for review duration or recoverable amount uncertainty, but top-K policy must state which quantile and why. Quantile loss improvement is not automatically better mean estimate.

## 7. Binary cross-entropy

Binary cross-entropy for probability `p` and label `y ∈ {0,1}` is:

```text
BCE = -[y log(p) + (1-y) log(1-p)]
```

For logits `z`, numerically stable implementations combine sigmoid and cross-entropy without explicitly computing extreme probabilities. Therefore `from_logits=True` requires unbounded logits, while `from_logits=False` requires values interpreted as probabilities.

```python
logit_model = tf.keras.Sequential([
    tf.keras.layers.Dense(1),
])
loss_fn = tf.keras.losses.BinaryCrossentropy(from_logits=True)
```

Alternative:

```python
probability_model = tf.keras.Sequential([
    tf.keras.layers.Dense(1, activation="sigmoid"),
])
loss_fn = tf.keras.losses.BinaryCrossentropy(from_logits=False)
```

Both are valid when paired correctly. Sigmoid output with `from_logits=True` or applying sigmoid again in custom loss changes objective and gradients. Output signature must distinguish logit from probability.

## 8. Multiclass cross-entropy

For mutually exclusive classes, softmax cross-entropy compares logits/probabilities with one-hot or sparse class target. Class order is part of schema.

```python
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(
    from_logits=True,
)
```

Sparse target uses integer class IDs; categorical target uses one-hot/distribution vectors. Passing sparse IDs to categorical loss may fail shape validation or produce wrong semantics after accidental broadcasting/encoding.

Multilabel problems usually use independent sigmoid/BCE outputs, not softmax, because classes are not mutually exclusive. Wrong output/loss pairing can train without obvious infrastructure failure while imposing incorrect probability constraints.

## 9. Numerical stability

Directly computing `log(sigmoid(z))` for large magnitude logits can underflow or overflow. Stable fused losses use algebraic transformations. Clipping probabilities can prevent `log(0)` but changes gradients and may hide invalid outputs.

```text
very negative z for positive label
→ large finite stable loss
not NaN/Inf from naive exp/log
```

Floating-point precision, mixed precision and reduction size affect stability. Use framework-provided fused losses and monitor non-finite loss/gradients. A finite scalar does not prove correct semantics; wrong `from_logits` can remain finite.

## 10. Label smoothing

Label smoothing replaces hard targets with softened values, for example positive `1` becomes `1-ε` and negative `0` receives some mass. It can reduce overconfidence and act as regularization, but changes probability target and calibration.

```python
loss_fn = tf.keras.losses.BinaryCrossentropy(
    from_logits=True,
    label_smoothing=0.02,
)
```

Smoothing parameter is part of objective generation. It is not a substitute for noisy-label analysis. In rare-event risk, smoothing may harm tail discrimination or calibration; evaluate against same business metrics.

## 11. Class imbalance, class weights a focal behavior

Rare positive classes can contribute little to average loss. Class/sample weighting increases their objective contribution. This changes effective training distribution and raw probability calibration.

```python
class_weight = {0: 1.0, 1: 25.0}
model.fit(X_train, y_train, class_weight=class_weight)
```

Weights should derive from explicit objective/cost or sampling correction, not only inverse frequency by habit. Focal loss downweights easy examples and focuses on hard/misclassified cases, but adds hyperparameters and can distort calibration. It is a candidate surrogate, not universal imbalance solution.

Threshold, ranking and calibration still require representative validation population. A weighted training loss cannot be compared numerically to unweighted loss without context.

## 12. Empirical risk a regularization

Empirical risk is average/reduced loss over training observations. Regularization adds constraints or penalties to parameters/activations to control capacity or encode preference.

```text
objective = empirical_loss + λ × regularization_penalty
```

Keras layers can add kernel regularizers. Total `model.losses` may contain regularization terms separate from primary loss. Custom training loop must add them explicitly.

```python
with tf.GradientTape() as tape:
    logits = model(x_batch, training=True)
    data_loss = loss_fn(y_batch, logits)
    reg_loss = tf.add_n(model.losses) if model.losses else 0.0
    total_loss = data_loss + reg_loss
```

Forgetting regularization in custom loop creates different objective from `model.fit`. Report data and regularization losses separately to diagnose whether total decrease reflects fit or shrinking weights.

## 13. Gradient descent

Gradient descent updates parameters opposite gradient direction:

```text
θ_(t+1) = θ_t - η ∇θ L(θ_t)
```

`η` is learning rate. Full-batch gradient uses all training samples per update; stochastic gradient uses one sample; mini-batch SGD uses subset. In modern ML, „SGD“ often means mini-batch updates.

Gradient is local slope of defined objective at current parameters/batch. It does not guarantee global optimum in non-convex neural network. Optimization path depends on initialization, batch order, learning rate and optimizer state.

## 14. Mini-batch stochastic optimization

Mini-batches reduce memory and provide noisy gradient estimates. Noise can help exploration but also instability. Batch composition affects class/group representation and effective weights.

```text
shuffle/sampler
→ batch B_t
→ loss L_Bt
→ gradient estimate
→ update
```

Data loader must prevent forbidden sample duplication or target-dependent sampling outside declared policy. Distributed replicas compute local gradients that are aggregated; global batch size equals per-replica batch × replicas × accumulation steps under simple synchronous semantics.

Changing batch size often requires retuning learning rate and regularization. Same epoch count with different batch size means different number of optimizer updates.

## 15. Learning rate

Learning rate controls update scale. Too high can overshoot, oscillate or diverge; too low can stall or require excessive compute. Good value depends on scaling, loss curvature, optimizer, batch size and model architecture.

```text
high η:
fast early movement → instability/NaN/poor minimum risk

low η:
stable small updates → slow convergence/undertraining risk
```

Training and validation curves, gradient norms and parameter-update norms provide evidence. One learning rate cannot be copied blindly across optimizer or batch changes.

Chapter 13 will deepen learning-rate schedules and convergence; here learning rate is fixed as part of optimizer transition contract.

## 16. Momentum a SGD

Momentum accumulates velocity from past gradients:

```text
v_t = μ v_(t-1) + g_t
θ_(t+1) = θ_t - η v_t
```

It can smooth noisy directions and accelerate along consistent gradients. Optimizer state `v_t` matters for resume. Resetting momentum changes trajectory even from same weights.

```python
optimizer = tf.keras.optimizers.SGD(
    learning_rate=0.01,
    momentum=0.9,
    nesterov=True,
)
```

Nesterov variant evaluates/look-ahead-like gradient differently. Exact framework implementation and parameters belong to manifest.

## 17. Adam

Adam maintains exponential moving averages of gradients and squared gradients, producing adaptive per-parameter updates with bias correction.

```text
m_t = β₁ m_(t-1) + (1-β₁) g_t
v_t = β₂ v_(t-1) + (1-β₂) g_t²
```

Update uses `m_t / (sqrt(v_t) + ε)` plus learning rate, subject to implementation details. Adam often trains quickly with limited tuning, but does not guarantee best generalization or calibration.

```python
optimizer = tf.keras.optimizers.Adam(
    learning_rate=1e-3,
    beta_1=0.9,
    beta_2=0.999,
    epsilon=1e-7,
)
```

Moment slots and iteration count are optimizer state. Resume weights with new Adam resets adaptive history and schedule position.

## 18. AdamW a weight decay

AdamW decouples weight decay from gradient of loss-based L2 penalty. Decoupled decay scales parameters separately from adaptive gradient update. It is not always equivalent to adding L2 regularizer to loss under adaptive optimizers.

```python
optimizer = tf.keras.optimizers.AdamW(
    learning_rate=1e-3,
    weight_decay=1e-4,
)
```

Which variables receive decay matters; biases and normalization parameters are often excluded in some training recipes, but API/default behavior must be explicit. Applying both layer L2 and AdamW decay may double-regularize unintentionally.

Weight decay is optimizer/config generation and must be included in comparisons.

## 19. Optimizer state and checkpoint resume

Complete training checkpoint includes model weights, optimizer slot variables, global iteration, learning-rate schedule state and sometimes random/data iterator state. Weights-only checkpoint supports inference or warm start, not exact continuation.

```python
checkpoint = tf.train.Checkpoint(
    model=model,
    optimizer=optimizer,
)
checkpoint.write("ckpt/step-42000")
```

After restore, verify optimizer iterations, learning rate and representative prediction/loss. A successful file load may skip unmatched variables; strict restore assertions are needed where supported.

Preemption recovery acceptance distinguishes exact resume, warm start and fresh retrain. They have different experiment identity.

## 20. Learning-rate schedules a warmup

Schedule changes learning rate by optimizer step or epoch: piecewise decay, cosine, exponential, plateau-based, one-cycle or warmup. Warmup starts low and increases to reduce early instability, especially with large batches or deep models.

```text
step 0..1000: linear warmup
step 1001..N: cosine decay
```

Schedule state depends on global step. Reset step on resume repeats warmup or returns to high learning rate. Changing steps per epoch changes epoch-based schedule semantics.

Plateau scheduler monitors validation metric and is part of selection feedback. It must use allowed validation data and record patience/min_delta.

## 21. Gradient clipping

Clipping bounds gradient values or norm before update. Global norm clipping preserves direction while scaling all gradients when norm exceeds threshold.

```python
optimizer = tf.keras.optimizers.Adam(
    learning_rate=1e-3,
    global_clipnorm=1.0,
)
```

Clipping can contain exploding gradients and stabilize training, but persistent clipping may signal wrong scaling, architecture or learning rate. Monitor pre/post clipping norm and fraction clipped.

Value clipping changes components independently and can distort direction. Threshold is hyperparameter tied to model/gradient scale.

## 22. Mixed precision a loss scaling

Mixed precision uses lower-precision compute/storage for speed and memory while retaining selected variables/operations at higher precision. Small gradients can underflow in float16. Loss scaling multiplies loss before gradient computation and unscales gradients afterward.

```text
scaled_loss = loss × scale
scaled_gradients = ∂scaled_loss/∂θ
unscaled_gradients = scaled_gradients / scale
```

Dynamic loss scaling adjusts scale when non-finite gradients occur. Overflow skip behavior, scale state and hardware/framework versions belong to training evidence. Mixed precision can change numeric trajectory and reproducibility.

Final output/loss layers may need float32 for stability. Parity tolerance is required for exported inference.

## 23. NaN/Inf diagnosis

Non-finite loss or gradients can originate from invalid input, wrong domain, overflow, divide-by-zero, extreme logits, high learning rate, unstable custom loss or precision issues. Immediate retry without preserving batch/input/state loses evidence.

```text
first non-finite step
→ preserve checkpoint before step
→ batch/sample IDs and feature ranges
→ per-component losses
→ logits/activations/gradient norms
→ optimizer learning rate/state
```

Containment stops promotion and may reduce learning rate or disable mixed precision only after hypothesis evidence. Skipping bad batches silently changes training population and can hide data corruption.

TensorFlow numerics checks and finite assertions help localize first invalid operation, but can add cost.

## 24. Gradient accumulation

Accumulation sums gradients over multiple micro-batches before optimizer update, approximating larger batch under certain conditions.

```text
for k micro-batches:
  accumulate gradients
then:
  average/sum according to contract
  one optimizer update
```

Dropout, batch normalization, loss reduction, sample weights and schedule step semantics can make accumulated training differ from one true large batch. Optimizer iteration should advance per effective update, not necessarily per micro-batch.

Manifest records per-replica batch, replicas, accumulation steps and global effective batch. Changing any affects objective scale and schedule.

## 25. Convergence diagnostics

Convergence is not simply „loss decreased“. Track training and validation loss, task/business metrics, gradient/update norms, learning rate, non-finite counts, clipped fraction, parameter norms and wall-clock/steps.

```text
training loss ↓, validation loss ↑
→ overfitting or shift

training loss flat, gradient norm ~0
→ saturation, dead units, low LR or disconnected path

loss oscillates, gradient/update norm high
→ excessive LR, bad scaling or unstable batch
```

Plateau may be acceptable if validation/business metric stabilizes and further compute has low value. Absolute convergence proof is rare for non-convex neural optimization; use declared stopping rules and evidence.

## 26. Early stopping

Early stopping monitors validation metric and stops after no sufficient improvement. It is regularization/model selection, not training-set optimization.

```python
callback = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=8,
    min_delta=1e-4,
    restore_best_weights=True,
)
```

Validation split must respect group/time boundary. `restore_best_weights=True` restores model weights but optimizer state may correspond to later step depending on workflow; exporting after early stopping is fine for inference, but exact resume requires consistent checkpoint.

Monitoring `val_loss` may select different epoch than business top-K metric. Selection metric must reflect intended outcome and calibration trade-offs.

## 27. Training loss, validation metric a business metric

A model can lower BCE while ranking top-K worsens if improvements occur in easy majority cases. It can improve AUC while calibration worsens. Multi-metric report separates objective from acceptance.

```text
training:
weighted BCE

validation model metrics:
log loss, PR AUC, calibration

business metrics:
captured recoverable loss at K
analyst capacity/friction
cohort constraints
```

No single metric should be implicitly authoritative. Promotion criteria define required and guardrail metrics and allowable trade-offs before test evaluation.

## 28. Custom training loop boundary

`model.fit` handles many details consistently. Custom loop is needed for specialized objectives or updates, but then developer owns regularization inclusion, training mode, reduction, distributed scaling, metrics, checkpointing and callbacks.

```python
with tf.GradientTape() as tape:
    logits = model(x, training=True)
    per_example = loss_fn(y, logits)
    data_loss = tf.reduce_mean(per_example)
    reg_loss = tf.add_n(model.losses) if model.losses else 0.0
    total_loss = data_loss + reg_loss

grads = tape.gradient(total_loss, model.trainable_variables)
optimizer.apply_gradients(zip(grads, model.trainable_variables))
```

This example omits distributed scaling, sample weights and finite checks; production loop must implement exact contract. Comparing custom loop with built-in fit requires controlled parity test.

## 29. Distributed optimization

Synchronous data parallel training replicates model, computes gradients on per-replica batches and aggregates before one logical update. Effective objective scaling and batch size must be correct.

```text
replica gradients
→ all-reduce aggregation
→ global optimizer update
```

Worker restart, partial failure, stale gradients and checkpoint authority depend on distribution strategy. A chief or coordinated checkpoint writer must avoid multiple inconsistent artifacts.

Throughput scaling does not guarantee same optimization trajectory. Large global batch and fewer updates per epoch require learning-rate/schedule retuning and generalization evaluation.

## 30. Worked incident `ML-PAY-85`

Atlas candidate combined five defects:

1. Sigmoid output with `from_logits=True` compressed inputs to the loss and produced wrong gradients without immediate exception.
2. A custom experiment applied sigmoid again before BCE, further flattening confident outputs.
3. Learning rate increased from `1e-3` to `2e-2` for a large-batch run; loss oscillated and mixed precision produced intermittent non-finite gradients.
4. Preemption restore loaded only model weights; Adam moments, iteration and cosine schedule state reset, repeating warmup and changing trajectory.
5. Early stopping monitored validation BCE, while production decision depended on captured recoverable loss at top K and calibration.

```text
lower reported training loss
≠ correct loss semantics
≠ exact resume
≠ better top-K business outcome
```

A dashboard averaged only successful batches; steps skipped for non-finite gradients were hidden. The checkpoint named `best` referred to lowest BCE, not approved business metric. The team initially blamed neural architecture, but the primary root cause was objective/optimizer state mismatch.

## 31. Evidence-preserving containment a recovery

Tím stopped automatic promotion and preserved the first bad batch IDs, raw logits, per-example/data/regularization losses, gradient norms, loss-scale state, optimizer slots, global step, learning rate and checkpoints before/after resume. Serving remained on approved boosting/logistic fallback.

Recovery created tests for output/loss pairing and finite gradients. Complete checkpoints included model and optimizer. Resume verification asserted matched objects and exact step/schedule. Mixed precision run used dynamic loss scaling with non-finite counters visible. Early stopping selected a declared validation objective, while promotion required calibration and top-K business guardrails.

```text
validate output/loss contract
→ train finite baseline in float32
→ introduce optimizer/schedule
→ verify complete checkpoint resume
→ enable mixed precision with parity
→ compare validation + business metrics
→ export locked artifact
```

Old contaminated runs remained in experiment history with invalid/diagnostic status.

## 32. Acceptance contract

Positive path preukazuje exact output/target/loss semantics, reduction and weights, regularization, finite gradients, optimizer and schedule state, batch/global update semantics, convergence and independent validation/business metrics.

Recovery path distinguishes exact resume, warm start and retrain. Complete checkpoint must restore optimizer slots, step and schedule or explicitly create successor run identity. Non-finite event must preserve evidence and stop/contain rather than silently skip indefinitely.

Forbidden paths:

```text
sigmoid probability is passed to from_logits=True loss
double sigmoid/softmax changes objective silently
test/business metric drives iterative training while called untouched
regularization term is omitted in custom loop
optimizer state/schedule step is lost but run is called resumed
mixed-precision non-finite batches are hidden
learning-rate or batch-size change lacks new generation
decreasing training loss is treated as production acceptance
```

Second-resume test trains N steps, checkpoints, restores in fresh process and compares next learning rate, optimizer state and update/prediction tolerance with uninterrupted control. Second-cohort test confirms calibration, top-K business metric and guardrails on newer mature data despite continued loss improvement.

## Kontrolné otázky

1. Prečo training loss nie je business objective?
2. Ako per-example loss, sample weights a reduction vytvoria scalar objective?
3. Ako sa MSE, MAE a Huber líšia?
4. Čo quantile loss odhaduje?
5. Aký je correct pairing logits/probabilities a binary cross-entropy?
6. Ako sa multiclass softmax a multilabel sigmoid objective líšia?
7. Prečo fused cross-entropy zlepšuje numerical stability?
8. Ako label smoothing mení target semantics?
9. Čo class weights a focal behavior robia s calibration?
10. Ako regularization vstupuje do total lossu?
11. Čo updateuje gradient descent a čo learning rate riadi?
12. Ako mini-batch a global effective batch menia trajectory?
13. Aký state drží momentum a Adam?
14. Čím sa AdamW weight decay líši od L2 loss penalty?
15. Prečo weights-only restore nie je exact resume?
16. Ako schedule a warmup závisia od global step-u?
17. Čo gradient clipping môže a nemôže opraviť?
18. Prečo mixed precision potrebuje loss scaling?
19. Ako diagnostikovať prvý NaN/Inf step?
20. Kedy gradient accumulation nie je exact large batch?
21. Prečo decreasing train loss nestačí ako convergence verdict?
22. Ako early stopping využíva validation authority?
23. Čo musí custom loop implementovať okrem `GradientTape`?
24. Ako distributed replicas menia objective scaling?
25. Čo pokazilo optimization lifecycle v `ML-PAY-85`?
26. Aké positive, recovery, forbidden a second-resume testy uzatvárajú optimization contract?

## Glossary impact

Relevantné pojmy: loss function, surrogate objective, per-example loss, reduction, sample/class weight, MSE, MAE, Huber loss, quantile/pinball loss, binary/multiclass cross-entropy, logit, numerical stability, label smoothing, focal loss, empirical risk, regularization term, gradient descent, mini-batch SGD, learning rate, momentum, Adam, AdamW, optimizer state, learning-rate schedule, warmup, gradient clipping, mixed precision, loss scaling, gradient accumulation, convergence, early stopping, custom training loop, distributed optimization a optimization acceptance contract.

## Primárne zdroje

- [TensorFlow — Keras losses](https://www.tensorflow.org/api_docs/python/tf/keras/losses)
- [TensorFlow — Keras optimizers](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers)
- [TensorFlow — Adam](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/Adam)
- [TensorFlow — AdamW](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/AdamW)
- [TensorFlow — `tf.GradientTape`](https://www.tensorflow.org/api_docs/python/tf/GradientTape)
- [TensorFlow — Training and evaluation with built-in methods](https://www.tensorflow.org/guide/keras/training_with_built_in_methods)
- [TensorFlow — Mixed precision](https://www.tensorflow.org/guide/mixed_precision)
- [TensorFlow — Training checkpoints](https://www.tensorflow.org/guide/checkpoint)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Neural network fundamentals](neural-network-fundamentals.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
