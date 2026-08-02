# Gradient descent, learning rate a convergence

Gradient descent nie je dôkaz, že model „našiel správne riešenie“. Je to family iterative optimization methods, ktoré menia parameters podľa local gradientu zvoleného objective-u. Learning rate určuje scale update-u a convergence criteria rozhodujú, kedy training prestane. Pri convex problem-e môže byť analysis silnejšia; pri neural network je landscape non-convex, stochastic a dependent na initialization, batch order, optimizer state a numeric runtime. Znižovanie training lossu preto musí byť oddelené od generalization a business acceptance.

Incident `ML-PAY-86` vznikol pri Atlas successor modeli. Jeden experiment bežal presne `50` epochs a bol označený ako converged, hoci learning rate bol príliš nízky a gradient updates prakticky zamrzli. Druhý experiment použil high rate, osciloval medzi valleys a early stopping vybral náhodne dobrý epoch. Tretí resume-nul training s resetnutým schedule stepom. Dashboard porovnával epoch count namiesto optimizer updates, global batch a actual learning-rate trajectory. Táto kapitola fixuje optimization trajectory ako exact subject.

## 1. Dominantný convergence lifecycle

Convergence analysis začína objective-om, data/batch sequence a initial parameters. Každý step vypočíta loss a gradient, optimizer vytvorí update a schedule určí learning rate. Monitoring porovnáva training aj validation metrics, gradient/update norms, parameter state a wall-clock/resource cost. Stopping rule vytvorí selected checkpoint; test a business evidence sa vykonajú až nad locked artifactom.

```text
objective + initialization + data order
→ batch at global step t
→ forward loss
→ gradient estimate
→ optimizer transform/state
→ learning rate η_t
→ parameter update
→ train/validation diagnostics
→ stopping/checkpoint selection
→ independent acceptance
```

Epoch je reporting unit, nie universal optimization state. Global step, number of samples seen, effective batch, schedule position a optimizer slots určujú trajectory presnejšie.

## 2. Exact optimization-trajectory subject

Trajectory manifest musí zviazať initial model, objective, batch semantics, optimizer state, schedule a stopping authority. Rovnaká architecture a rovnaký počet epochs môžu viesť k inému výsledku pri inom global batchi, seed-e, shuffle orderi alebo resume state-e. Bez týchto identities sa training run nedá reprodukovať ani porovnať.

```yaml
trajectory_subject: ML-PAY-GD-2026-08-v2
model_subject: ML-PAY-DNN-2026-08-v2
objective: OPT-2026-08-v3
initialization_checkpoint: init-sha256:7a12...
optimizer: AdamW
schedule:
  type: cosine_decay_with_warmup
  warmup_steps: 2000
  total_steps: 100000
  initial_learning_rate: 0.001
batch:
  per_replica: 256
  replicas: 4
  accumulation_steps: 2
  effective_global_batch: 2048
data_order:
  sampler: grouped-shuffle-v2
  seed: 17
stopping:
  monitored: validation_average_precision
  mode: max
  patience_evaluations: 8
  min_delta: 0.0005
checkpoint_selection: best_validation_metric
resume_state:
  includes: [weights, optimizer_slots, global_step, schedule_state]
```

Manifest umožňuje rozlíšiť dva runs s rovnakou architecture a final step countom, ale inou initialization, batch sequence alebo learning-rate path. „50 epochs“ bez sample inventory a global steps nie je exact trajectory.

## 3. Full-batch gradient descent

Pre objective `L(θ)` full-batch gradient descent computes gradient nad celým training setom a update:

```text
θ_(t+1) = θ_t - η_t ∇L(θ_t)
```

Pri smooth convex objective a vhodnom learning rate môže algorithm konvergovať k global optimum. Pri large datasets je full gradient expensive a jeden update môže trvať dlho. Deterministic full-batch run stále závisí od numeric precision a linear algebra implementation.

Full-batch loss decrease is easier to interpret than noisy minibatch loss, but generalization remains separate. Exact minimization empirical risk can overfit.

## 4. Stochastic a mini-batch gradient descent

Stochastic gradient používa one sample; mini-batch gradient average/sum subset. Gradient is estimate of full gradient:

```text
g_t ≈ ∇L(θ_t)
θ_(t+1) = θ_t - η_t g_t
```

Noise depends on batch size, sampling and data heterogeneity. Small batch creates more updates per epoch and noisy trajectory; large batch reduces variance and may need learning-rate adjustment. „Epoch 10“ means different update count across batch sizes.

```python
steps_per_epoch = ceil(n_train_samples / effective_batch_size)
total_updates = epochs * steps_per_epoch
```

Distributed drop/repeat, filtering and class-balanced samplers can make samples-seen differ from nominal dataset size. Log actual counts.

## 5. Gradient direction a update direction

Optimizer may transform raw gradient through momentum, adaptive scaling, clipping or weight decay. Actual parameter update is not simply `-ηg` for Adam/AdamW.

```text
raw gradient g_t
→ clipping
→ moments/preconditioner
→ weight decay
→ update Δθ_t
```

Monitor both gradient norm and update norm. Small gradient with large adaptive update or large gradient clipped to stable update have different diagnosis. Ratio `||Δθ|| / ||θ||` can reveal frozen or explosive layers, but threshold is model-dependent.

## 6. Learning rate as step-size policy

Learning rate controls how far optimizer moves along transformed direction. Too high may overshoot, oscillate or diverge. Too low may converge slowly or stall in flat/saturated region.

```text
loss ↓ smoothly + validation improves
→ plausible useful rate

loss oscillates/non-finite
→ rate too high, bad scaling or unstable objective

loss almost flat + tiny updates
→ rate too low, dead gradients or plateau
```

Learning rate interacts with batch size, normalization, optimizer and loss scale. Copying `1e-3` from another model is not evidence.

## 7. Constant, decay a adaptive schedules

Constant schedule keeps `η_t` fixed. Step, exponential, polynomial, inverse-time and cosine schedules reduce rate over time. Warmup increases rate from low initial value. Plateau-based callbacks react to validation metric.

```python
import tensorflow as tf

schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=1e-3,
    decay_steps=10000,
    decay_rate=0.9,
    staircase=False,
)
optimizer = tf.keras.optimizers.Adam(schedule)
```

Schedule argument typically consumes optimizer iteration. Reset iteration on resume repeats schedule phase. Epoch-based callback depends on steps/epoch and can behave differently after dataset or batch changes.

Schedule is serialized state/config and must be read-back from loaded optimizer.

## 8. Warmup

Warmup limits early updates while weights, normalization state and optimizer moments are uncalibrated. It is common with large batches/deep models. Too long warmup wastes steps; too short may destabilize.

```text
η_t = η_target × t / warmup_steps, for t <= warmup_steps
```

Warmup count is global optimizer steps, not necessarily batches read when accumulation is used. Resume after warmup with reset global step can dangerously repeat schedule phase.

## 9. Learning-rate range experiments

A range test gradually increases rate over short run and observes loss behavior to identify useful scale. It is diagnostic, not final validation.

```text
very low rate → little progress
useful region → rapid loss decrease
high rate → loss instability/divergence
```

Result depends on initialization, batch, optimizer and selected data slice. Reusing same validation/test to choose rate repeatedly creates selection bias.

## 10. Convex convergence oproti non-convex trainingu

Linear regression with convex objective has no spurious local minima under standard conditions; logistic with convex regularized objective also has stronger guarantees. Neural networks are non-convex and have saddle points, flat directions and many equivalent parameterizations.

Convergence in neural training usually means practical stopping: objective/validation no longer improves materially, updates are small/stable or compute budget exhausted. It does not prove global optimum.

```text
optimizer stopped improving
≠ best possible model
≠ generalization accepted
≠ business outcome accepted
```

## 11. Training-loss convergence

Training loss curve can be noisy. Use smoothed windows while preserving raw values. A plateau may mean optimum for current representation, insufficient learning rate, saturated activations, regularization balance or data pipeline issue.

```text
train loss plateau + high bias on validation
→ add features/capacity/change optimization/data
not automatically train longer
```

Loss value across different objectives/weights/reductions is not directly comparable.

## 12. Validation convergence

Validation metric often improves then degrades as overfitting increases. Early stopping selects a checkpoint according to monitored metric. Evaluation cadence matters: patience of 8 epochs vs 8,000 steps is different.

```text
train loss continues ↓
validation loss bottoms then ↑
→ overfitting after selected point
```

Noisy validation with few positives can produce accidental best epoch. Use confidence/stability, larger or grouped/time-aware validation and minimum delta.

## 13. Gradient norms

Per-layer/global gradient norms reveal exploding, vanishing or disconnected paths.

```python
with tf.GradientTape() as tape:
    logits = model(x, training=True)
    loss = loss_fn(y, logits)
grads = tape.gradient(loss, model.trainable_variables)
global_norm = tf.linalg.global_norm([g for g in grads if g is not None])
```

`None` means no differentiable dependency. Zero may be legitimate or dead/saturated. Large norm can be clipped but persistent spikes require root-cause analysis.

## 14. Update-to-weight ratio

Parameter update norm relative to weight norm helps identify too-small/large steps.

```text
ratio_l = ||ΔW_l|| / (||W_l|| + ε)
```

Very high ratio indicates destructive updates; very low may indicate frozen layer or tiny effective rate. There is no universal acceptable number.

## 15. Loss landscape diagnostics

Saddle/plateau, sharp/flat minima and curvature are conceptual tools. Hessian or approximations can analyze curvature but are expensive. Practical signals include sensitivity to learning rate, seed, perturbation and batch.

Different parameter points can represent same function due to symmetries. Parameter distance does not equal prediction distance.

## 16. Oscillation a divergence

Oscillation appears when updates overshoot narrow curvature or momentum persists. Divergence shows rapidly increasing/non-finite loss/weights.

```text
stop at first evidence
preserve pre-failure checkpoint + batch IDs + LR + norms
verify inputs/loss
reduce LR or correct scaling
resume as new run identity
```

Blind retry may hit same batch/state. Skipping non-finite step can hide corruption.

## 17. Plateau diagnosis

Plateau hypotheses include learning rate too small after decay, insufficient representation, vanishing gradients, repeated data, frozen parameters, dominant regularization or noisy validation. Discriminating evidence includes current LR, update norms, trainable flags, samples seen and data/reg loss components.

## 18. Early stopping a checkpoint authority

```python
callback = tf.keras.callbacks.EarlyStopping(
    monitor="val_average_precision",
    mode="max",
    patience=8,
    min_delta=5e-4,
    restore_best_weights=True,
)
```

Best weights may not include optimizer state from best step. For inference export this can be fine; for exact continuation use complete checkpoint captured at selected step. Validation data must respect group/time boundary.

## 19. Convergence tolerance v scikit-learn

Iterative estimators use `tol`, `max_iter`, early stopping and iteration counts with estimator-specific semantics. `max_iter` reached warning means stopping budget exhausted, not convergence.

```python
from sklearn.linear_model import SGDClassifier

model = SGDClassifier(
    loss="log_loss",
    learning_rate="optimal",
    early_stopping=True,
    validation_fraction=0.1,
    n_iter_no_change=8,
    tol=1e-4,
    random_state=17,
)
```

Internal validation fraction may violate group/time boundaries. Read `n_iter_`, warnings and score curves if available.

## 20. Compute budget a convergence

Training may stop because compute/time/cost budget ends. This is budget exhaustion, not convergence.

```yaml
stop_reason: budget_exhausted
steps_completed: 72000
planned_steps: 100000
best_validation_step: 68120
```

Comparing candidates with unequal budgets can favor fast-converging models unfairly.

## 21. Reproducibility a nondeterminism

Seeds control some initialization/shuffling, but parallel kernels, distributed reduction order and hardware can be nondeterministic. Convergence acceptance should define metric/output tolerance and seed variability.

Multiple seeds estimate training variance. Store environment, devices, libraries, determinism flags and data order.

## 22. Continual/incremental learning

Estimators with `partial_fit` update over streams. Convergence concept changes because distribution may drift.

```python
model.partial_fit(X_batch, y_batch, classes=[0, 1])
```

Order matters. Replaying batch after uncertain outcome can double-update; operation IDs/idempotency ledger are needed.

## 23. Worked incident `ML-PAY-86`

Atlas compared three runs:

```text
A: 50 epochs, batch 256, constant LR 1e-5
B: 20 epochs, batch 4096, LR 2e-2 + momentum
C: resume B checkpoint weights only, cosine schedule reset
```

Run A was called converged because it reached 50 epochs; update norms showed almost no movement. Run B had fewer epochs but fewer optimizer updates and oscillating validation metric; smoothing hid spikes. Run C repeated warmup and reset Adam moments, so it was a new trajectory despite same run ID.

Early stopping used random validation rows and selected one noisy high-AP epoch. Best validation loss and best top-K metric occurred at different steps. Registry stored only final weights, not selected checkpoint reason or optimizer state.

## 24. Evidence-preserving containment a recovery

Tím froze runs and preserved raw/smoothed curves, global steps, samples seen, LR per step, gradient/update norms, optimizer/checkpoint state and stop reasons. No run was called converged until diagnostics were classified.

Recovery standardized effective batch and schedule budget for controlled comparisons, used grouped-temporal validation and stored complete checkpoints. Run manifest recorded stop reason: converged-by-rule, early-stopped, failed-nonfinite or budget-exhausted.

```text
controlled initialization/data/batch
→ LR range diagnostic
→ declared schedule
→ monitor raw loss/norms
→ grouped validation
→ selected complete checkpoint
→ independent test/business acceptance
```

## 25. Acceptance contract

Positive path preukazuje exact objective, initialization, data order, global batch, optimizer/schedule, finite gradients/updates, stopping rule and selected checkpoint. Validation/business metrics must support stopping decision.

Recovery distinguishes exact resume from new trajectory. Stop reason must be truthful.

Forbidden paths:

```text
epoch count alone is called convergence
max_iter exhaustion is called optimum
smoothed curve hides non-finite/oscillating raw steps
LR/batch/schedule changes keep same run generation
weights-only restore is called exact resume
random internal validation violates group/time split
best training loss is treated as best business checkpoint
budget exhaustion is hidden as convergence
```

Second-resume test compares uninterrupted vs restored next updates within tolerance. Second-seed/cohort test checks convergence stability, selected step, calibration and business metric.

## Kontrolné otázky

1. Čo gradient descent updateuje?
2. Ako mini-batch gradient súvisí s full gradientom?
3. Prečo epoch nie je universal trajectory identity?
4. Ako optimizer transformuje raw gradient?
5. Čo learning rate riadi a s čím interaguje?
6. Aké schedule families a warmup existujú?
7. Čo learning-rate range experiment preukazuje?
8. Ako sa convex a non-convex convergence líšia?
9. Čo training-loss plateau môže znamenať?
10. Ako validation curve indikuje overfitting?
11. Čo gradient a update norms diagnostikujú?
12. Ako sa oscillation, divergence a plateau líšia?
13. Čo EarlyStopping vyberá a čo nemusí obnoviť?
14. Prečo scikit-learn `max_iter` warning nie je kozmetika?
15. Ako compute budget mení stop reason?
16. Prečo seed nezaručí bitovú reprodukovateľnosť?
17. Aké idempotency riziko má `partial_fit`?
18. Čo bolo nepravdivé v convergence verdicte `ML-PAY-86`?
19. Aké positive, recovery, forbidden a second-resume tests uzatvárajú trajectory contract?

## Glossary impact

Relevantné pojmy: full-batch/stochastic/mini-batch gradient descent, gradient estimate, parameter update, learning rate, schedule, warmup, global step, effective batch, convex/non-convex convergence, gradient norm, update-to-weight ratio, oscillation, divergence, plateau, stopping criterion, early stopping, tolerance, budget exhaustion, exact resume, nondeterminism, incremental learning a convergence acceptance contract.

## Primárne zdroje

- [scikit-learn — Stochastic Gradient Descent](https://scikit-learn.org/stable/modules/sgd.html)
- [scikit-learn — `SGDClassifier`](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html)
- [scikit-learn — Validation and learning curves](https://scikit-learn.org/stable/modules/learning_curve.html)
- [TensorFlow — LearningRateSchedule](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/schedules/LearningRateSchedule)
- [TensorFlow — ExponentialDecay](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/schedules/ExponentialDecay)
- [TensorFlow — EarlyStopping](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/EarlyStopping)
- [TensorFlow — Training and evaluation](https://www.tensorflow.org/guide/keras/training_with_built_in_methods)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Loss functions a optimization](loss-functions-optimization.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Overfitting, underfitting, bias a variance →](overfitting-underfitting-bias-variance.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
