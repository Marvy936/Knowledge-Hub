# Reproducibility a random seeds

Random seed nie je kompletný reproducibility contract. Seed inicializuje jeden alebo viac pseudo-random number generators, ale výsledok môže stále závisieť od dataset orderu, split indices, parallel scheduling, hardware, library/kernel version, floating-point reduction order, nondeterministic GPU operation, environment variable, cache, retry a mutable external data. Naopak bitwise-identický training run nie je vždy správny cieľ: production model-building procedure môže byť stochastic a acceptance potrebuje dokazovať bounded alebo statistical stability naprieč seeds, nie iba opakovanie jedného priaznivého runu.

Incident `ML-PAY-88` uzavrel blok v Atlas Payments. Experiment manifest obsahoval `seed: 42`, no Python, NumPy Generator, scikit splittery, sampler, estimator a PyTorch DataLoader používali odlišné RNG streams. HPO trial retry obnovil model weights, ale nie optimizer, scheduler ani RNG state. GPU training používal nondeterministic operations a cuDNN benchmarking. Dataset query nemala stable ordering a po backfille labelov rovnaký manifest path vracal iné rows. Tím preto nedokázal rozlíšiť očakávanú stochastic variance od lineage a resume bugov. Kapitola definuje reproducibility ako exact subject, environment a execution procedure s explicitnou toleranciou.

## 1. Dominantný reproducibility lifecycle

Reproducibility začína definíciou požadovanej úrovne identity. Potom sa zamrazia data, code, configuration, dependencies, hardware/runtime a random streams. Run uloží artifacts a complete state. Re-execution sa porovná podľa bitwise, numerical, metric alebo decision tolerance.

```text
reproducibility objective a tolerance
→ exact data/code/config/environment/hardware subject
→ RNG inventory a seed derivation
→ deterministic alebo bounded-stochastic execution policy
→ checkpoints, logs, predictions a artifacts
→ repeat/resume/cross-environment comparison
→ diagnose lineage, RNG, numerical a scheduler hypotheses
→ correction a successor run
→ second-operation a multi-seed acceptance
```

„Same seed“ bez exact data a software generation je slabší dôkaz než immutable dataset manifest bez seed-u. Obe vrstvy sú potrebné pre stochastic training.

## 2. Úrovne reproducibility

Reproducibility sa deklaruje podľa use case-u:

- bitwise reproducibility — outputs sú byte-for-byte identické v constrained environment;
- numerical reproducibility — tensors/predictions sa zhodujú v definovanej absolute/relative tolerance;
- metric reproducibility — evaluation metrics zostávajú v tolerancii, hoci weights alebo predictions sa mierne líšia;
- decision reproducibility — promotion, threshold alebo business verdict zostáva rovnaký;
- statistical reproducibility — distribution výsledkov naprieč independent seeds/environments je kompatibilná;
- procedural reproducibility — iný operátor dokáže z manifests a code zopakovať lifecycle a získať accepted outcome.

Bitwise identity môže byť nereálna medzi CPU/GPU, hardware generations alebo library releases. Statistical reproducibility môže byť nedostatočná pre forensic resume test, kde sa očakáva exact continuation. Contract preto nie je jeden global boolean.

## 3. Exact run subject

Run manifest identifikuje všetky mutable inputs a execution boundaries.

```yaml
run_subject: ML-PAY-REPRO-2026-08-v6
data:
  manifest: eu-cnp-train-2026w10-w27-v7
  content_digest: sha256:be12...c881
  row_order: stable_hash_operation_id
code:
  commit: 7af30d1
  dirty: false
configuration:
  digest: sha256:f1a7...902d
environment:
  container_digest: sha256:9d34...118e
  python: 3.13.5
  numpy: 2.3.1
  scikit_learn: 1.9.0
  pytorch: 2.13.0
hardware:
  accelerator: NVIDIA-H100-SXM
  driver: 590.44
  cuda: 13.1
randomness:
  root_seed: 20260803
  derivation: hkdf-context-v2
  streams: [split, sampler, initialization, dataloader, augmentation]
determinism:
  required: numerical
  tolerance:
    prediction_atol: 1.0e-6
    prediction_rtol: 1.0e-5
```

Version values sú ilustratívny manifest, nie odporúčanie na konkrétny stack. Autoritatívne sú exact values použité v reálnom rune a ich digests.

## 4. Pseudo-random generators a streams

Pseudo-random generator vytvára deterministickú sequence zo state. Seed inicializuje state, ale každý draw ho posunie. Zmena call orderu, worker countu alebo conditional branchu preto zmení nasledujúce values.

```text
seed → RNG state_0
random draw → value_1 + state_1
random draw → value_2 + state_2
```

Jeden global RNG stream prepája nesúvisiace components. Pridanie debug sample-u môže zmeniť model initialization alebo split. Robustnejší pattern odvodzuje independent named streams z root seed-u.

```python
from numpy.random import SeedSequence, default_rng

root = SeedSequence(20260803)
split_ss, sampler_ss, augmentation_ss = root.spawn(3)

split_rng = default_rng(split_ss)
sampler_rng = default_rng(sampler_ss)
augmentation_rng = default_rng(augmentation_ss)
```

Manifest uloží derivation context a child identifiers. Samotný integer list bez mappingu nevysvetľuje, ktorý component seed použil.

## 5. Python a NumPy randomness

Python standard library a NumPy majú samostatné RNGs. Legacy `numpy.random.seed()` ovplyvňuje global singleton; moderný `Generator` má vlastný state.

```python
import random
import numpy as np

random.seed(20260803)
legacy_numpy_seed = 20260803
np.random.seed(legacy_numpy_seed)

rng = np.random.default_rng(20260803)
```

Seed global singletonu neovplyvní independent `Generator` vytvorený inde. Library môže prijímať integer, `RandomState` alebo `Generator` podľa API. Wrapper nesmie predpokladať jeden universal seed propagation mechanism.

Hash-based data structures a Python hash randomization môžu meniť iteration order v niektorých workflows. Reproducible pipeline používa explicitné sorting a stable serialization, nie incidental dictionary/set order assumptions.

## 6. scikit-learn `random_state` semantics

Scikit-learn estimators a splitters často prijímajú `random_state`. Integer spravidla umožní reprodukovať call behavior tým, že object pri fit/split začne z rovnakého seed-u. Shared `RandomState` instance sa môže spotrebúvať a interactions medzi objects závisia od call orderu.

```python
from sklearn.model_selection import StratifiedGroupKFold

splitter = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=20260803,
)
```

`random_state=None` používa framework/global randomness a výsledok môže závisieť od external state. Pre model evaluation je zároveň užitočné testovať viac seeds, pretože jeden integer fixuje iba jednu stochastic realization.

Splitter seed, estimator seed, sampler seed a permutation-importance seed majú odlišný purpose. Kopírovať `42` všade môže nechcene synchronizovať streams a znižuje auditovateľnosť. Named derived seeds sú presnejšie.

## 7. Dataset identity a stable ordering

Rovnaký SQL query text nemusí vrátiť rovnaký dataset. Source tables sa menia, late labels dozrievajú a query bez `ORDER BY` nemá guaranteed row order. Random split nad index positions sa potom zmení aj pri rovnakom seed-e.

```text
query definition
+ source snapshot/as-of time
+ selected IDs
+ content digest
+ stable order
= dataset generation
```

Dataset manifest uchováva row IDs, source versions, extraction time, filters, label maturity a feature schema. Stable hash sort alebo explicitný key order predchádza split/sampling. Duplicate IDs a tie handling sú deterministicky definované.

Content digest sa počíta nad canonical representation. Compression metadata alebo non-canonical floating serialization nemajú meniť logical dataset identity.

## 8. Split a sampling reproducibility

Split indices sú artifact, nie iba result seed-u. Library upgrade, row filtering alebo group-order change môže pri rovnakom seed-e vytvoriť iné folds.

```python
fold_assignment.to_parquet("folds-v6.parquet", index=False)
```

Sampler membership, bootstrap counts, oversampled/synthetic lineage a augmentation parameters sa ukladajú. Synthetic sample sa mapuje na source neighbors a RNG state/procedure. Test set sa neobnovuje náhodným splitom pri každom rune; jeho identity je locked.

## 9. PyTorch seed inventory

PyTorch má vlastný RNG a operations môžu používať randomness interne. `torch.manual_seed()` inicializuje PyTorch RNG pre CPU a CUDA devices podľa current API semantics, ale neovplyvní Python, NumPy Generator ani external libraries.

```python
import torch

torch.manual_seed(20260803)
```

CUDA, distributed training, DataLoader workers a augmentations potrebujú explicitný plan. RNG states sa pri checkpoint-resume ukladajú, nie iba original seed.

```python
checkpoint["rng_state"] = {
    "python": random.getstate(),
    "numpy_global": np.random.get_state(),
    "torch_cpu": torch.get_rng_state(),
    "torch_cuda": torch.cuda.get_rng_state_all(),
}
```

Ak application používa NumPy `Generator`, jeho `bit_generator.state` sa uloží samostatne.

## 10. DataLoader workers

Multi-process DataLoader reseeduje workers podľa svojho algorithmu. Reproducible augmentations potrebujú worker initialization a explicitný generator.

```python
import random
import numpy as np
import torch
from torch.utils.data import DataLoader


def seed_worker(worker_id: int) -> None:
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)


generator = torch.Generator()
generator.manual_seed(20260803)

loader = DataLoader(
    dataset,
    batch_size=256,
    shuffle=True,
    num_workers=4,
    worker_init_fn=seed_worker,
    generator=generator,
)
```

Changing `num_workers`, prefetching, persistent workers alebo exception/retry behavior môže meniť sample/augmentation order. Exact DataLoader config patrí do manifestu.

## 11. Nondeterministic algorithms

Niektoré parallel CPU/GPU algorithms používajú atomic updates alebo execution order, ktorý vedie k nondeterministic floating results. PyTorch poskytuje `torch.use_deterministic_algorithms()` na výber deterministic implementations alebo fail, ak dostupné nie sú.

```python
import torch

torch.use_deterministic_algorithms(True, warn_only=False)
```

Táto setting sama nestačí na complete reproducibility. Data, RNGs, environment a other libraries zostávajú relevantné. Deterministic implementation môže byť pomalšia alebo spotrebovať viac memory. `warn_only=True` iba upozorní a nepresadí fail-closed determinism.

Acceptance musí uviesť, či nondeterministic operations sú forbidden, warning alebo bounded. Silent fallback je audit failure.

## 12. cuDNN benchmarking a determinism

CUDA convolution benchmarking môže pri novom input shape vyskúšať viac algorithms a vybrať fastest. Benchmark noise a hardware môžu viesť k inému výberu. Vypnutie benchmarkingu stabilizuje selection, ale vybraný algorithm môže stále byť nondeterministic.

```python
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True
```

`torch.backends.cudnn.deterministic` sa týka konkrétnych cuDNN operations; širší `torch.use_deterministic_algorithms(True)` pokrýva viac operations. Settings sa nezamieňajú. Current hardware/library docs sú authority pre supported behavior.

## 13. Floating-point a reduction order

Floating-point addition nie je asociatívna. Parallel reduction, thread count, distributed all-reduce alebo fused kernel môže meniť order a tým low-order bits.

```text
(a + b) + c ≠ a + (b + c)
```

Small numerical difference sa môže počas nonlinear optimization amplifikovať do odlišných weights. To neznamená automaticky bug, ale procedure potrebuje tolerance a multi-seed stability. Mixed precision, TF32, compiler optimization a kernel fusion patria do environment/config manifestu.

Bitwise comparison across hardware je preto často nesprávny acceptance. Predictions a business metrics môžu mať tighter practical tolerance než weights.

## 14. Parallelism a scheduler effects

Parallel HPO, CV, data preprocessing a training môžu meniť task order, resource contention a timeout outcomes. Nested parallelism môže viesť k OOM alebo different candidate completion setu.

```yaml
execution:
  hpo_workers: 8
  cv_jobs: 4
  estimator_threads: 2
  dataloader_workers: 4
  timeout_seconds: 3600
  retry_policy: exact_resume_or_new_attempt
```

Asynchronous model-based HPO môže navrhovať candidates podľa poradia dokončených trials; rovnaký root seed s iným scheduler timingom preto vytvorí inú search trajectory. Reproducibility contract musí rozlišovať deterministic trial definitions od deterministic global search order.

## 15. Distributed training

Distributed data-parallel training potrebuje exact world size, rank mapping, sampler epoch, collective backend a checkpoint semantics. Zmena world size mení batch composition a optimization trajectory.

```text
global batch = per_device_batch × world_size × accumulation_steps
```

DistributedSampler potrebuje consistent seed a `set_epoch(epoch)` pre intended reshuffling. Resume uloží epoch/step, sampler state a consumed samples. Elastic restart bez data-position authority môže samples zopakovať alebo preskočiť.

All-reduce order a hardware topology môžu meniť numerics. Statistical acceptance môže byť vhodnejšia než bitwise identity, ale duplicate/missing sample processing je correctness failure, nie harmless variance.

## 16. Checkpoint a exact resume

Training checkpoint pre exact resume obsahuje viac než model weights:

```yaml
checkpoint:
  model_state: present
  optimizer_state: present
  scheduler_state: present
  gradient_scaler_state: present
  rng_states: present
  dataloader_sampler_state: present
  epoch_and_global_step: present
  consumed_sample_position: present
  config_and_code_digest: present
```

Weights-only checkpoint je vhodný pre inference alebo transfer, nie exact continuation. Resume po loading weights s fresh optimizerom vytvorí successor training trajectory. Ak sa stále označuje rovnakým run ID, lineage je chybná.

Atomic write a checksum bránia partial checkpointu. Retry používa attempt ID; pôvodný failed attempt zostáva auditovateľný.

## 17. Environment a dependency pinning

Lockfile alebo container tag nie je dostatočný, ak tag je mutable alebo native libraries nie sú captured. Reproducibility manifest používa image digest, package lock, driver/runtime versions, OS/kernel a relevantné environment variables.

```text
source commit
→ dependency lock
→ built image digest
→ runtime driver/hardware
→ executed command/config
```

Rebuild z rovnakého Dockerfile môže po čase stiahnuť iné base layers alebo packages bez pinned digest/version. Build provenance a artifact registry retention patria do evidence.

## 18. Code a configuration identity

Git commit identifikuje tracked code, ale dirty working tree, untracked files, generated code, notebook state alebo remote config môžu meniť execution.

```yaml
code_state:
  commit: 7af30d1
  dirty: false
  submodules: pinned
  generated_files_digest: sha256:...
config_sources:
  - repo_yaml_digest
  - environment_overlay_digest
  - secret_version_ids
```

Secrets sa nelogujú plaintext, ale ich version/identity môže byť relevantná, napríklad external API endpoint alebo credential scope. Feature flags a service responses sú external dependencies a potrebujú snapshot/mock alebo explicitný non-reproducible boundary.

## 19. Statistical stability naprieč seeds

Jeden fixed seed môže náhodne zvýhodniť candidate. Model selection a acceptance preto môžu používať predeclared seed set a distribution metrics.

```yaml
seed_stability:
  seeds: [11, 23, 37, 53, 71]
  primary_metric:
    mean_min: 0.421
    worst_seed_min: 0.395
    standard_deviation_max: 0.018
  cohort_guards:
    campaign_recall_worst_seed_min: 0.35
```

Seeds nie sú substitutes za independent data windows. Repeated seeds na rovnakom dataset-e odhadujú optimization/sampling variance, nie population shift. Search nesmie skúšať desiatky seeds a reportovať iba best.

## 20. Reproducibility test matrix

Testy sa rozdelia podľa otázky:

```text
same process, same environment, same inputs
→ exact/numerical rerun

checkpoint resume vs uninterrupted run
→ trajectory equivalence

same procedure, multiple seeds
→ statistical stability

same artifact, different serving replicas
→ inference consistency

same procedure, new environment/library
→ portability and regression
```

Každý test má allowed differences. Inference artifact môže vyžadovať bitwise CPU identity alebo bounded GPU tolerance. Training across release upgrade môže vyžadovať metric/decision equivalence, nie weight identity.

## 21. Worked incident `ML-PAY-88`

Atlas experiment reportoval `seed=42`, ale splitter dostal integer, estimator používal default `None`, oversampler vlastný `RandomState`, NumPy augmentation `default_rng()` bez seed-u a PyTorch DataLoader workers dedili neauditované states. Dataset export nemal snapshot ani stable ordering.

Po preemption-e retry načítal model weights a epoch number, ale optimizer momentum, learning-rate schedule, gradient scaler, RNG a sampler position začali odznova. Dashboard spojil attempts pod jeden run ID.

```text
same displayed seed
+ mutable row order
+ incomplete RNG inventory
+ nondeterministic kernels
+ weights-only resume
→ different trajectory with hidden lineage break
```

Rozdiel v candidate metric bol najprv pripísaný „GPU randomness“. Exact sample audit však ukázal duplicated batches po resume a zmenu labels po backfille. Root cause bol composite data/state identity failure, nie iba nondeterministic floating-point.

## 22. Competing failure hypotheses

Reproducibility incident sa diagnostikuje od najvyššej identity vrstvy po numerical details. Najprv sa porovnajú data IDs/digests, code/config/environment, checkpoint state a executed sample sequence; až potom seeds a kernels.

- mutable data generation — rovnaký path/query vrátil iné rows, labels alebo order;
- code/config drift — commit, dirty files, environment overlay alebo feature flag sa zmenil;
- incomplete RNG seeding — Python, NumPy, framework, workers alebo augmentation nemajú controlled stream;
- RNG consumption-order drift — call order, worker count alebo conditional path posunul stream;
- split/sampler regeneration — fold alebo sample membership nebolo uložené a zmenilo sa;
- nondeterministic operation — parallel/GPU kernel vracia odlišné numerics pri rovnakých inputs;
- floating reduction drift — thread/world-size/backend zmenil arithmetic order;
- incomplete checkpoint — optimizer, scheduler, scaler, RNG alebo data position chýba;
- retry identity collapse — nový attempt prepísal alebo sa zlúčil s pôvodným runom;
- parallel search-order drift — async HPO dostal iné completed observations a navrhol iné trials;
- environment mismatch — image, driver, library alebo hardware generation sa zmenila;
- best-seed selection — report vybral priaznivý run a skryl distribution variance.

Ak input IDs a sample order sa líšia, GPU determinism nie je prvá hypothesis. Ak uninterrupted a resumed run divergujú presne po checkpoint boundary, incomplete resume state je silnejšia. Ak same artifact dáva odlišné inference na rovnakom hardware, serving/kernel path sa izoluje od training variance.

## 23. Evidence-preserving containment a recovery

Containment zmrazí promotion a zachová všetky attempts, manifests, logs, checkpoints a environment metadata. Nevykonáva sa „rerun until pass“ s prepísaním failed evidence.

```text
freeze verdict
→ preserve attempt-specific artifacts
→ compare data/code/config/environment identities
→ reconstruct sample and RNG state
→ isolate exact resume and kernel behavior
→ run controlled reproducibility matrix
→ correct manifests/checkpoints/settings
→ create successor run generation
→ multi-seed and second-operation acceptance
```

Ak dataset bol mutable, dependent evaluations sú invalid bez ohľadu na metric similarity. Ak nondeterminism je accepted, tolerance sa zdokumentuje a testuje. Ak deterministic mode spôsobí unacceptable performance, risk owner rozhodne medzi bounded stochasticity, alternative operation a compute costom.

## 24. Acceptance contract

Positive acceptance identifikuje reproducibility level, exact data/code/config/environment/hardware, RNG streams, determinism settings, split/sampler artifacts, checkpoint completeness a comparison tolerance. Multi-seed distribution a independent data evidence sú oddelené.

Recovery acceptance preukazuje exact alebo bounded rerun, uninterrupted-vs-resume behavior a attempt lineage. Forbidden paths zahŕňajú jediný global seed ako complete proof, mutable image tag/dataset path, query bez stable snapshot/order, weights-only checkpoint označený exact resume, ignored nondeterministic warnings, best-seed reporting, NaN/failed retry overwrite a bitwise requirement bez fixed platform scope.

Second-operation test opakuje run v rovnakom constrained environmente. Resume test porovná uninterrupted a checkpoint-restored trajectory. Cross-environment test deklaruje expected tolerance. Multi-seed test overí mean, dispersion a worst-case guards.

```yaml
acceptance:
  exact_subject_and_environment: passed
  rng_inventory_and_seed_derivation: passed
  split_sampler_and_data_order: passed
  checkpoint_resume_state: passed
  deterministic_or_bounded_policy: passed
  multi_seed_stability: passed
  second_operation: passed
```

## Kontrolné otázky

1. Prečo random seed nie je kompletný reproducibility contract?
2. Ako sa líši bitwise, numerical, metric, decision a statistical reproducibility?
3. Prečo independent RNG streams znižujú coupling?
4. Aký je rozdiel medzi NumPy global seed a `Generator` state?
5. Ako integer a shared RNG object menia `random_state` behavior?
6. Prečo dataset row order ovplyvňuje split aj pri rovnakom seed-e?
7. Prečo sa fold indices a sampler membership ukladajú ako artifacts?
8. Ktoré RNG states potrebuje PyTorch checkpoint?
9. Ako DataLoader workers dostávajú seeds?
10. Čo presadzuje `torch.use_deterministic_algorithms()` a čo nerieši?
11. Aký je rozdiel medzi cuDNN benchmarking a deterministic operation?
12. Prečo floating-point reduction order môže zmeniť training trajectory?
13. Ako parallel HPO mení search reproducibility?
14. Čo musí obsahovať exact-resume checkpoint?
15. Prečo immutable image digest a dataset manifest sú dôležitejšie než tag/path?
16. Ako multi-seed stability dopĺňa, ale nenahrádza independent data window?
17. Čo pokazilo lifecycle v `ML-PAY-88`?
18. Aké positive, recovery, forbidden, resume a multi-seed testy uzatvárajú reproducibility contract?

## Glossary impact

Relevantné pojmy: reproducibility, repeatability, bitwise reproducibility, numerical reproducibility, metric reproducibility, decision reproducibility, statistical reproducibility, procedural reproducibility, pseudo-random number generator, RNG state, seed sequence, independent random stream, `random_state`, stable row ordering, deterministic algorithm, nondeterministic operation, cuDNN benchmarking, floating-point reduction, distributed sampler, exact resume, checkpoint state, environment pinning, image digest, attempt identity, multi-seed stability a reproducibility acceptance contract.

## Primárne zdroje

- [PyTorch — Reproducibility](https://docs.pytorch.org/docs/stable/notes/randomness.html)
- [PyTorch — `torch.use_deterministic_algorithms`](https://docs.pytorch.org/docs/stable/generated/torch.use_deterministic_algorithms.html)
- [scikit-learn — Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html)
- [scikit-learn — Glossary: `random_state`](https://scikit-learn.org/stable/glossary.html#term-random_state)
- [NumPy — Random sampling](https://numpy.org/doc/stable/reference/random/index.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Data quality, bias a responsible AI](data-quality-bias-responsible-ai.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
