# Neural network fundamentals

Neural network je parametrická composition vrstiev, ktoré opakovane aplikujú affine alebo iné transformations a nonlinear activations. Training upravuje weights tak, aby znižoval loss na training data. Hĺbka a šírka dávajú modelu capacity vytvárať komplexné representations, ale nevytvárajú automatickú generalizáciu, reasoning ani správny business outcome. Architecture, initialization, activations, normalization, optimization, data scale a serving runtime tvoria jednu model generation.

V incidente `ML-PAY-85` Atlas nasadil malú dense network ako „modernú“ alternatívu k logistic baseline a tree boosting. Candidate mal viac hidden layers, ale first version používala lineárne activations, takže composition bola stále ekvivalentná jednému linear transformu. Druhá verzia s ReLU mala high capacity, no input scaling a batch normalization state sa líšili medzi training a serving. Checkpoint bez optimizer/config lineage bol označený iba ako `nn-v2`. Táto kapitola oddeľuje architecture graph, trainable state a inference behavior.

## 1. Dominantný neural-network lifecycle

Neural lifecycle začína input/output contractom, pokračuje graphom layers a parameters, initialization, forward pass, loss, gradient computation a optimizer updates. Training mode môže meniť dropout alebo normalization behavior; export vytvorí inference artifact; serving musí loadnúť exact graph, weights, preprocessing a mode.

```text
input schema + target
→ layer graph a tensor shapes
→ parameter initialization
→ forward pass
→ loss
→ backward/automatic differentiation
→ optimizer state update
→ checkpoint
→ inference export
→ serving runtime + business policy
```

Checkpoint weights nie sú kompletná identity, ak architecture/config alebo preprocessing nie sú pinned. Resume training navyše potrebuje optimizer state a step counters; inference ich typicky nepotrebuje.

## 2. Exact neural model subject

Neural model identity musí pokryť graph aj všetok state, ktorý mení forward alebo training behavior. Architecture určuje tensor transitions, checkpoint nesie trainable a non-trainable layer state, optimizer a global step určujú resume trajectory a export/runtime určujú skutočný inference graph. Názov `nn-v2` ani samotný weights file preto nestačí na reprodukciu alebo rollback.

Nasledujúci subject fixuje input schema, layer graph, initialization, loss, optimizer, batching, seeds, checkpoint a serving export. Tým umožňuje rozlíšiť complete training continuation od weights-only warm startu a training checkpoint od production artifactu, ktorý musí prejsť signature a output-parity read-backom.

```yaml
model_subject: ML-PAY-DNN-2026-08-v2
input_schema: risk-dense-v8
framework: keras/tensorflow
architecture:
  - input: 128
  - dense: {units: 256, activation: relu}
  - dropout: {rate: 0.2}
  - dense: {units: 64, activation: relu}
  - dense: {units: 1, activation: sigmoid}
initializer: glorot_uniform
loss: binary_crossentropy
optimizer: adam
learning_rate: 0.001
batch_size: 1024
epochs_max: 100
early_stopping: validation-pr-v3
random_seeds: {python: 17, numpy: 17, tensorflow: 17}
preprocessing_digest: sha256:18a2...71c9
checkpoint_digest: sha256:92f1...bc18
export_digest: sha256:ef20...119a
serving_runtime: tensorflow-serving:release-2026-07
```

Subject oddeľuje training checkpoint od exported inference artifactu. Conversion, graph optimization alebo quantization môže zmeniť outputs a vytvoriť successor generation.

## 3. Neuron a affine transformation

Dense neuron vypočíta weighted sum inputs plus bias a aplikuje activation:

```text
z = wᵀx + b
a = φ(z)
```

Layer s viacerými units používa matrix:

```text
Z = XW + b
A = φ(Z)
```

Weights `W` a bias `b` sú trainable variables. Input batch dimension nie je parameter count. Dense layer so 128 inputs a 256 units má `128×256 + 256` parameters.

```python
import keras
from keras import layers

layer = layers.Dense(256, activation="relu")
```

Layer sa často buildne pri prvom inpute alebo s explicitným input shape. Shape mismatch je contract failure, nie automatic adaptation.

## 4. Prečo je nonlinearity potrebná

Composition iba lineárnych/affine layers bez nonlinear activation sa dá zlúčiť do jedného affine transformu:

```text
W₂(W₁x + b₁) + b₂
= (W₂W₁)x + (W₂b₁ + b₂)
```

Pridanie layers bez nonlinearity preto nezvyšuje functional class nad linear model. Activations ako ReLU, sigmoid, tanh, GELU alebo softmax zavádzajú nelinearitu a odlišné gradient/output properties.

First Atlas network mala three Dense layers s default linear activation. Vyzerala deep v diagram-e, ale function zostala lineárna. Parameterization mohla zmeniť optimization, nie representational boundary intended by tímom.

## 5. ReLU, sigmoid, tanh a softmax

ReLU:

```text
ReLU(z) = max(0, z)
```

Je jednoduchá a často udržiava gradients lepšie než saturating sigmoid/tanh v positive region. Negative units môžu zostať inactive („dead ReLU“) podľa initialization/learning rate.

Sigmoid mapuje scalar na `(0,1)` a často sa používa pre binary output probability parameter:

```text
σ(z) = 1 / (1 + e⁻ᶻ)
```

Tanh mapuje na `(-1,1)` a softmax normalizuje vector logits na class distribution:

```text
softmax(z_i) = exp(z_i) / Σ_j exp(z_j)
```

Activation choice musí zodpovedať output/loss contractu. Softmax s mutually exclusive classes, independent sigmoid outputs s multilabel taskom. Wrong pairing môže trainovať numericky, ale s nesprávnou semantics.

## 6. Layers ako representations

Hidden layer outputs sú learned representations. Early layers môžu zachytiť jednoduchšie patterns a later layers combinations, ale interpretation závisí od architecture a modality. Dense tabular network neobjaví automaticky stable domain concepts.

```text
raw encoded features
→ hidden representation h1
→ hidden representation h2
→ output logit/probability
```

Representation dimension je design choice. Bottleneck môže regularizovať/compressovať; wider layers zvýšia capacity a memory. Hidden activation nie je authoritative feature without validation.

Embeddings, convolution, recurrent/attention layers majú specialized inductive biases, ktoré budú rozvinuté v neskorších LLM/GenAI témach. Fundamentals zostávajú tensor shape, parameters, forward path a gradients.

## 7. Sequential, Functional a subclassed models

Keras `Sequential` je vhodný pre plain stack, kde každá layer má jeden input a output. Functional API podporuje multiple inputs/outputs, shared layers, residual a branch topologies. Subclassing umožňuje custom control, ale komplikuje serialization a static inspection.

```python
model = keras.Sequential([
    keras.Input(shape=(128,)),
    layers.Dense(256, activation="relu"),
    layers.Dense(64, activation="relu"),
    layers.Dense(1, activation="sigmoid"),
])
```

Architecture representation je súčasť supply chain. Custom layer code je executable trusted code a musí byť versionovaný, testovaný a bezpečne loadovaný.

Sequential nie je „jednoduchší model“ v statistical sense; môže mať veľa layers/parameters. Je iba topology API constraint.

## 8. Parameter count, memory a compute

Trainable parameters určujú časť capacity a memory. Training potrebuje weights, gradients a optimizer states; Adam typicky drží additional moment estimates, takže memory môže byť viacnásobok raw weights. Activations pre backward pass tiež spotrebujú memory podľa batch size a architecture.

```text
parameter memory
+ gradient memory
+ optimizer state
+ activation memory
+ framework/runtime overhead
```

Inference často nepotrebuje gradients/optimizer, ale batching, intermediate activations a multiple replicas still matter. Parameter count sám neurčuje latency; operation types, shape, hardware utilization a input pipeline sú dôležité.

Artifact size a loaded process RSS nie sú rovnaká veličina.

## 9. Forward pass a logits

Forward pass aplikuje layers na input a vytvorí output. Pre classification je často numericky stabilnejšie outputnúť logits a použiť loss configured `from_logits=True` než explicitný sigmoid/softmax pred lossom.

```python
model = keras.Sequential([
    keras.Input(shape=(128,)),
    layers.Dense(128, activation="relu"),
    layers.Dense(1),  # logit
])
```

```python
loss = keras.losses.BinaryCrossentropy(from_logits=True)
```

Inference consumer musí vedieť, či output je logit alebo probability. Aplikovať sigmoid dvakrát je serving bug. Export signature a schema musia explicitne pomenovať output semantics.

## 10. Backpropagation a automatic differentiation

Backpropagation používa chain rule na výpočet gradientu lossu podľa každého parameteru. Framework zaznamená operations v forward pass-e a propaguje gradients dozadu.

```text
x → layer1 → layer2 → output → loss
    ← ∂L/∂W1 ← ∂L/∂W2 ←
```

```python
import tensorflow as tf

with tf.GradientTape() as tape:
    logits = model(x_batch, training=True)
    loss_value = loss_fn(y_batch, logits)
gradients = tape.gradient(loss_value, model.trainable_variables)
optimizer.apply_gradients(zip(gradients, model.trainable_variables))
```

Gradient computation preukazuje local derivative pre batch/current parameters. Nezaručuje good optimization landscape, generalization alebo business alignment.

Disconnected variable môže mať `None` gradient. NaN/Inf gradient signalizuje numeric/data/architecture problem.

## 11. Initialization

Weights sa initialize-nú pred trainingom. All-zero weights v symmetric hidden units zabránia differentiation units; random initialization breaks symmetry. Xavier/Glorot a He initializations škálujú variance podľa fan-in/out a activation assumptions.

Initialization ovplyvňuje signal/gradient scale a reproducibility. Rovnaký seed nemusí zaručiť bit-identical training naprieč hardware, library versions alebo parallel kernels.

Bias initialization môže reflect base rate pre imbalanced classification a zrýchliť early training, ale musí byť computed z training data only.

## 12. Vanishing a exploding gradients

Pri deep composition môžu derivatives opakovane zmenšovať alebo zväčšovať gradient. Vanishing gradients spomaľujú learning early layers; exploding gradients spôsobujú instability/NaN.

```text
∂L/∂W_early = product mnohých Jacobians
```

Activation, initialization, normalization, residual connections, gradient clipping a optimizer settings pomáhajú. „Loss klesá“ nevylučuje, že niektoré layers sa neučia; gradient norms a activation distributions poskytujú evidence.

Gradient clipping je containment pre update magnitude, nie oprava wrong data/loss.

## 13. Batch size a stochastic gradients

Mini-batch training odhaduje full-data gradient z subsetu. Small batches majú noisy gradients a nižšiu memory; large batches využijú hardware, ale menia optimization dynamics a learning-rate scaling.

```text
training samples
→ shuffle/order policy
→ batches
→ gradient per batch
→ optimizer update
```

Batch composition môže porušiť group/time weighting alebo rare-class representation. Class-balanced sampler mení effective training distribution a probability calibration.

Final partial batch, distributed replicas a gradient accumulation ovplyvňujú effective batch size. Manifest musí uvádzať global batch, not only per-device batch.

## 14. Epoch, step a checkpoint

Step je optimizer update, epoch približne pass cez training dataset. Pri streaming, resampling alebo distributed pipeline nemusí epoch znamenať exact one observation per sample.

Checkpoint môže obsahovať weights only alebo training state vrátane optimizer, epoch/step a metrics. Resume weights-only s fresh optimizer nie je exact continuation.

```text
checkpoint-0042:
model weights + optimizer slots + global step + RNG/input state?
```

Reproducible resume vyžaduje aj data order/shuffle and preprocessing state. Inference export je separate artifact optimized pre serving signatures.

## 15. Training mode oproti inference mode

Niektoré layers sa správajú odlišne podľa `training` flagu. Dropout randomly zeroes activations during training but is disabled/inverted appropriately in inference. Batch normalization uses batch statistics during training and moving statistics during inference.

```python
training_output = model(x, training=True)
inference_output = model(x, training=False)
```

Serving accidentally in training mode môže vytvárať nondeterministic alebo batch-dependent predictions. Training evaluation accidentally in inference/training mode môže byť inconsistent.

Mode je runtime state and must be tested in exported artifact, not assumed from code.

## 16. Dropout

Dropout je regularization, ktorá počas trainingu náhodne maskuje activations. Znižuje co-adaptation a môže improve generalization. Rate `0.2` znamená masking probability podľa framework semantics, nie retain probability v každej API.

```python
layers.Dropout(0.2)
```

Dropout changes optimization and uncertainty methods; it is not same as feature missingness. Monte Carlo dropout at inference je separate designed procedure, not default serving behavior.

Wrong training flag v serving je critical because output changes per request/batch.

## 17. Batch normalization

Batch normalization normalizes intermediate activations using batch statistics during training and moving averages during inference, with learned scale/shift. Moving statistics are non-trainable state updated during fit.

Small/nonrepresentative batches, distributed aggregation and training-serving mode can affect results. Export must include moving means/variances. Recompute or reset them without weights creates incompatible state.

For tabular data, batch norm is not automatically superior to input scaling or layer normalization; compare on valid protocol.

## 18. Overparameterization a generalization

Neural network môže mať viac parameters než training samples and still generalize under certain data/optimization/regularization regimes. Parameter count alone does not determine overfitting. However, high capacity increases potential memorization, instability and serving cost.

Train/validation curves, subgroup/time tests, ablations and baseline comparison are needed. Near-zero training loss with poor validation suggests overfit, but shared leakage can make both look good.

Regularization, data augmentation, early stopping and architecture constraints are tools, not substitutes for data correctness.

## 19. Architecture search a validation feedback

Choosing layer count, units, activations, dropout and normalization is hyperparameter selection. Repeated architecture experiments can overfit validation. Test remains untouched.

```text
architecture candidates
→ fit on train
→ select on validation/CV
→ lock
→ final test
```

Automated architecture search expands search space and computational cost. Each trial needs lineage and budget; best observed validation score has selection bias.

Simpler baseline remains required to justify complexity.

## 20. Serialization a export

Keras model saving can preserve architecture/config and weights, with optimizer optionally for training continuation. Custom objects require code/config. Export for serving may produce SavedModel or another format/signature.

```python
model.save("risk_model.keras")
```

Artifact loading untrusted serialized executable content is supply-chain risk. Digest, signer, provenance and allowed custom objects are needed. Library compatibility must be tested.

Export transformations (graph freezing, optimization, mixed precision, quantization) require prediction parity tolerance and performance evaluation.

## 21. Serving batching a state isolation

Neural inference often benefits from batching, but batch wait increases latency and batch-dependent layers must be in inference mode. Dynamic shapes can trigger retracing/compilation or inefficient kernels.

Requests from multiple tenants may share batch compute but must not share data-visible state, logs or explanations. Model itself is typically stateless during inference; accidental mutable caches or online learning require stronger isolation and versioning.

Warm-up requests, model load and first compilation create cold latency. Readiness must reflect loaded usable model, not only process start.

## 22. Neural network interpretability

Weights across hidden layers are not directly interpretable like simple coefficients. Attribution methods, saliency, integrated gradients or perturbation can provide local evidence, but depend on baseline, correlations and model behavior. They do not prove causality or faithful natural-language explanation by default.

For tabular risk, compare neural attributions with domain features, cohort stability and counterfactual constraints. Generated explanation must be separated from model-local attribution.

Interpretability requirement may favor simpler model if performance gain is marginal.

## 23. Worked incident `ML-PAY-85`

Atlas neural candidate v1:

```python
model = keras.Sequential([
    layers.Dense(128),
    layers.Dense(64),
    layers.Dense(1),
])
```

Bez nonlinear activations bol graph equivalent to one affine transformation, hoci mal more parameters. V2 pridala ReLU, dropout a batch normalization. Training score improved, no serving wrapper loaded weights into architecture without batch-normalization moving state from correct checkpoint and accidentally called model with `training=True` in one canary route.

Input preprocessing model očekával standardized 128-dimensional vector, ale one-hot vocabulary update vytvoril 133 features. Wrapper truncated/padded instead of rejecting schema mismatch. Endpoint shape remained accepted and predictions shifted.

```text
architecture/config mismatch
+ incomplete checkpoint state
+ wrong inference mode
+ input-schema coercion
= valid tensor, invalid model generation
```

## 24. Evidence-preserving containment a recovery

Tím zachoval architecture config, weights/checkpoints, optimizer state, seeds, training curves, gradient/activation diagnostics, preprocessing schema, export signatures a canary outputs. Neural route was disabled; logistic baseline remained serving.

Recovery rebuilt one immutable artifact with input signature, preprocessing digest, architecture, all layer state and inference mode tests. Parity compared training-runtime inference and exported serving outputs on golden/shadow samples. Shape mismatch now failed closed.

```text
pinned graph + complete weights/state
→ export
→ signature/schema validation
→ inference-mode parity
→ load/latency test
→ shadow business evaluation
```

Neural candidate had to show incremental value over logistic and boosting after serving cost and calibration.

## 25. Acceptance contract

Positive path preukazuje exact layer graph/shapes, parameter count, activations, initialization, complete checkpoint/export, inference mode and input/output semantics. Training evidence includes finite loss/gradients, convergence and valid split curves.

Recovery allows rollback exact export and compatible preprocessing/policy. Resume training must distinguish weights-only from complete optimizer/state continuation.

Forbidden paths:

```text
stack linear layers sa vydáva za nonlinear deep model
checkpoint weights sa loadnú do different graph/state
serving uses training=True unintentionally
input vectors are truncated/padded to hide schema mismatch
NaN/None gradients or non-convergence are ignored
parameter count is treated as capability proof
neural output is accepted without calibration/policy/business evidence
```

Second-export test loads artifact in fresh process and compares signature/output tolerance. Second-cohort test checks calibration, cold-start/out-of-range behavior, p99 latency, batching, fallback and business top-K outcome.

## Kontrolné otázky

1. Akú computation vykonáva dense neuron a layer?
2. Prečo multiple linear layers without activations remain linear?
3. Aké output semantics majú ReLU, sigmoid a softmax?
4. Čo hidden representation môže a nemôže dokazovať?
5. Kedy je Keras Sequential model vhodný?
6. Čo tvorí training memory okrem weights?
7. Aký je rozdiel medzi logit a probability?
8. Ako backpropagation používa chain rule?
9. Prečo initialization breaks symmetry?
10. Čo sú vanishing a exploding gradients?
11. Ako effective batch size ovplyvňuje training?
12. Čo odlišuje step, epoch, checkpoint a inference export?
13. Ktoré layers menia správanie podľa training/inference mode?
14. Ako dropout a batch normalization fungujú?
15. Prečo parameter count sám neurčuje overfitting ani capability?
16. Ako architecture search kontaminuje validation?
17. Aké supply-chain risks má serialization/custom objects?
18. Prečo batching a readiness patria k serving contractu?
19. Čo pokazilo neural candidate v `ML-PAY-85`?
20. Aké positive, recovery, forbidden a second-export testy uzatvárajú neural-network contract?

## Glossary impact

Relevantné pojmy: neural network, neuron, dense layer, affine transform, activation, ReLU, sigmoid, tanh, softmax, hidden representation, tensor shape, parameter count, forward pass, logit, backpropagation, automatic differentiation, initialization, vanishing/exploding gradient, mini-batch, epoch, step, checkpoint, training/inference mode, dropout, batch normalization, serialization/export a neural-network acceptance contract.

## Primárne zdroje

- [TensorFlow — Keras high-level API](https://www.tensorflow.org/guide/keras)
- [TensorFlow — The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)
- [TensorFlow — Functional API](https://www.tensorflow.org/guide/keras/functional_api)
- [TensorFlow — Modules, layers and models](https://www.tensorflow.org/guide/intro_to_modules)
- [TensorFlow — `tf.GradientTape`](https://www.tensorflow.org/api_docs/python/tf/GradientTape)
- [TensorFlow — Save, serialize and export models](https://www.tensorflow.org/guide/keras/serialization_and_saving)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Decision trees, random forests a gradient boosting](decision-trees-random-forests-gradient-boosting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Loss functions a optimization →](loss-functions-optimization.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
