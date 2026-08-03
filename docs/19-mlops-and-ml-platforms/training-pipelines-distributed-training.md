# Training pipelines a distributed training

Training pipeline riadi vznik fitted modelu od immutable vstupov po checkpoint, evaluation a candidate package. Distributed training rozdeľuje jednu training computation medzi viac procesov, zariadení alebo uzlov. Tieto dve vrstvy sa prekrývajú, ale nie sú totožné: orchestrátor vytvára a sleduje training job; framework koordinuje workers, ranks, collectives, gradients a checkpoint state vo vnútri jobu.

Pre platform rolu je kritické odlíšiť job od worker procesu, rank od Podu, world size od počtu dostupných GPU a training completion od použiteľného checkpointu. Kubernetes Job môže byť `Complete`, hoci iba chief worker zapísal neúplný checkpoint. Distributed job môže visieť, pretože jeden rank skončil pred collective. Elastic restart môže vytvoriť novú worker group s iným world size, čo mení sampler, batch semantics a optimization trajectory.

Incident `MLOPS-PAY-92` pokračuje tým, že Atlas presunul risk model zo single-GPU trainingu na štyri GPU. Každý worker načítal dataset bez správneho `DistributedSampler`, takže všetky ranks spracovali rovnaké samples. Reportovaný global batch size bol štvornásobný, ale effective unique batch zostal pôvodný. Po zlyhaní ranku 2 `torchrun` reštartoval worker group z checkpointu, ktorý obsahoval model weights, no nie optimizer, scheduler, scaler, RNG ani sampler progress. Job dokončil a uložil model, ale trajectory už nezodpovedala experiment recordu.

## 1. Dominantný training lifecycle

Training subject musí byť uzavretý pred alokáciou GPU. Vstupom je dataset snapshot, split membership, code a environment, model architecture, objective, optimizer, precision, distributed strategy, world-size policy a checkpoint contract. Výstupom nie sú iba weights, ale complete candidate package a evidence.

```text
immutable dataset + split
→ resolved code/config/environment
→ training job generation
→ worker-group rendezvous
→ distributed data assignment
→ forward/backward computation
→ gradient alebo parameter synchronization
→ optimizer/scheduler update
→ complete checkpoint
→ evaluation a package
→ training-run verdict
```

Ak niektorá z identít zostane implicitná, successful job nie je reprodukovateľný. Rovnaký container digest s iným GPU countom, world size, mixed precision alebo communication backendom môže vytvoriť inú trajectory a performance profile.

## 2. Exact distributed-training subject

Manifest musí rozlišovať orchestration identity od framework identity. `TrainJob` alebo Kubernetes workload určuje runtime objecty. `torchrun` vytvára local worker procesy, ranks a rendezvous group. PyTorch DDP následne synchronizuje gradients v process group.

```yaml
training_subject: MLOPS-PAY-DDP-2026-08-r22
dataset_manifest: sha256:39bd...ee02
split_manifest: sha256:2c44...d101
source_commit: 13ad5d5fc5a5c98f60f11a339f86f35e02762ff6
training_image: registry.example/ml/train@sha256:5f7a...91d2
framework: pytorch-2.13
strategy: distributed-data-parallel
nodes: 2
processes_per_node: 4
world_size_policy: fixed-8
backend: nccl
global_batch_size: 2048
per_rank_batch_size: 256
gradient_accumulation_steps: 1
precision: bf16
seed: 3719
checkpoint_contract: complete-v4
rendezvous_id: MLOPS-PAY-DDP-2026-08-r22
```

Manifest musí uviesť aj expected hardware class, pretože kernel selection, memory limits a performance môžu ovplyvniť výsledok. Hardware identity nie je iba capacity detail; môže byť súčasťou reproducibility boundary.

## 3. Single-process, data parallel a model parallel

Single-process training vlastní celý model aj optimizer state v jednom procese. Data parallel replikuje model na workers a rozdeľuje input samples. Po backward pass sa gradients synchronizujú, aby každý worker vykonal ekvivalentný update. Model parallel rozdeľuje samotný model alebo jeho tensors/stages, pretože sa nezmestí do jedného zariadenia alebo potrebuje inú compute topology.

DDP je synchronous data-parallel model. Každý process má model replica a typicky jednu GPU. DDP automaticky synchronizuje gradients cez process group, ale nerozdeľuje input. Training code musí použiť sampler alebo inú partitioning stratégiu. Bez nej workers môžu spracovať duplicity.

```python
import os
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler

rank = int(os.environ["RANK"])
local_rank = int(os.environ["LOCAL_RANK"])
world_size = int(os.environ["WORLD_SIZE"])

torch.cuda.set_device(local_rank)
dist.init_process_group(backend="nccl")

sampler = DistributedSampler(
    dataset,
    num_replicas=world_size,
    rank=rank,
    shuffle=True,
    drop_last=False,
)
loader = DataLoader(dataset, sampler=sampler, batch_size=256)
model = DDP(model.to(local_rank), device_ids=[local_rank])
```

Každá epoch musí zavolať `sampler.set_epoch(epoch)`, aby shuffle používal deterministic, ale epoch-specific ordering. Inak workers opakujú rovnaké ordering patterns a experiment môže mať inú statistical behavior než intended run.

## 4. Rank, local rank, world size a worker group

Global rank identifikuje process v process group. Local rank identifikuje process na jednom node. World size je počet participants v group. Tieto hodnoty patria ku konkrétnej worker-group generation, nie k večnej identite jobu.

Pri fixed membership jobe zlyhanie jedného workeru typicky zruší celý attempt. Pri elastic trainingu sa workers môžu reštartovať a znovu rendezvous-nuť. Rank assignments sa môžu zmeniť a pri scale-up/scale-down aj world size. Code preto nesmie viazať durable state na rank 0 bez generation a ownership semantics.

`rank == 0` sa často používa na logging a checkpoint publication. To je koordinácia, nie durable election. Po reštarte môže byť rank 0 iný process. Checkpoint path potrebuje atomic publication a manifest, aby nový chief vedel, ktorý checkpoint je complete.

## 5. `torchrun` a rendezvous

`torchrun` spúšťa distributed worker procesy a nastavuje environment variables pre ranks a world. Multi-node job potrebuje rendezvous ID, backend a endpoint. Rendezvous zhromaždí participants a vytvorí konzistentnú worker group.

```bash
torchrun \
  --nnodes=2 \
  --nproc-per-node=4 \
  --rdzv-id=MLOPS-PAY-DDP-2026-08-r22 \
  --rdzv-backend=c10d \
  --rdzv-endpoint=trainer-rdzv.ml.svc:29400 \
  train.py --config /etc/train/resolved.yaml
```

Rendezvous success preukazuje iba zostavenie group. Nepreukazuje, že workers načítali rovnaký dataset manifest, model initialization alebo checkpoint. Training script musí po initialization vykonať cross-rank assertions a zlyhať, ak sa digests alebo config fingerprints líšia.

```python
local_fingerprint = resolved_manifest_sha256()
values = [None for _ in range(world_size)]
dist.all_gather_object(values, local_fingerprint)
if len(set(values)) != 1:
    raise RuntimeError(f"Worker manifest mismatch: {values}")
```

## 6. Gradient synchronization a collective failure

DDP synchronizuje gradient buckets cez collectives. Collective očakáva participation všetkých ranks v rovnakom poradí. Ak jeden worker preskočí backward branch alebo skončí, ostatné ranks môžu visieť v all-reduce. Symptom je často GPU utilization blízka nule a process bez progress, nie explicitný exception na každom node.

Control-flow divergence môže vzniknúť pri data-dependent branchi, uneven inputs alebo nesprávnom exception handlingu. Timeout na process group je containment, nie root-cause fix. Diagnostics musí zachytiť last completed step, rank-specific logs, stack traces, NCCL errors, network counters a worker-group identity pred restartom.

```text
rank 0: waiting all-reduce bucket 31
rank 1: waiting all-reduce bucket 31
rank 2: exited on corrupted batch 8821
rank 3: waiting all-reduce bucket 31
```

Restart bez preservation stratí first divergence. Orchestrátor má najprv uložiť per-rank failure artifacts a až potom spustiť nový attempt.

## 7. Global batch, learning rate a equivalence

Global batch pri synchronous data parallel sa typicky vypočíta ako:

```text
global batch
= per-rank batch
× world size
× gradient accumulation steps
```

Zmena world size preto mení optimization semantics, ak sa neupraví per-rank batch, accumulation alebo learning-rate policy. Throughput improvement nie je automaticky training equivalence. Rovnaký počet epochs pri inom world size môže znamenať iný počet optimizer steps.

Acceptance manifest musí zaznamenať samples seen, unique samples, optimizer steps, skipped steps pri mixed precision a effective learning-rate schedule. Epoch count sám nestačí. Pri uneven dataset size môže `drop_last`, sampler padding alebo last partial batch zmeniť exposure niektorých samples.

## 8. Checkpoint ako kompletný resume subject

Weights-only checkpoint umožní inference alebo warm start, ale neumožní exact resume optimizer trajectory. Complete resume checkpoint potrebuje model, optimizer, scheduler, mixed-precision scaler, RNG states, epoch/step, sampler alebo dataloader progress, gradient-accumulation position a relevantný distributed topology contract.

```python
checkpoint = {
    "model": unwrap(model).state_dict(),
    "optimizer": optimizer.state_dict(),
    "scheduler": scheduler.state_dict(),
    "scaler": scaler.state_dict(),
    "epoch": epoch,
    "global_step": global_step,
    "python_rng": random.getstate(),
    "numpy_rng": np.random.get_state(),
    "torch_rng": torch.get_rng_state(),
    "cuda_rng": torch.cuda.get_rng_state_all(),
    "world_size": dist.get_world_size(),
    "dataset_manifest": DATASET_DIGEST,
    "resolved_config": RESOLVED_CONFIG_DIGEST,
}
```

Publication má byť atomic: workers najprv zapíšu temporary objects, chief vytvorí canonical manifest až po kontrole všetkých shards a checksumov. Presence pathu `checkpoint.pt` nie je complete proof.

Pri sharded checkpointoch musí manifest uviesť shard count, ownership, topology a restore requirements. Garbage collection nesmie odstrániť shard, na ktorý odkazuje promoted model alebo active resume operation.

## 9. Elastic restart a recovery semantics

Elasticity rieši worker failure a dynamickú membership, ale môže zmeniť computation. Reštart worker group z complete checkpointu je nová execution generation. Ak world size zostáva fixed, cieľom môže byť equivalent continuation. Ak world size zmení, system musí explicitne určiť, či je trajectory akceptovateľná alebo sa run označí ako non-comparable.

Recovery record obsahuje checkpoint digest, old a new worker-group generation, old a new world size, resumed global step a any altered hyperparameters. Experiment tracker nesmie prezentovať pre-restart a post-restart segments ako jeden neurčitý run bez lineage.

Unknown outcome vzniká aj pri checkpoint upload timeoute. Pred ďalším uploadom sa prečíta manifest a checksums. Blind overwrite môže nahradiť complete checkpoint partial generation.

## 10. Kubeflow Trainer V2 boundary

Kubeflow Trainer V2 poskytuje Kubernetes-native `TrainJob` a runtime model pre distributed training. Platform administrator vlastní `ClusterTrainingRuntime` alebo namespaced runtime, images, policies a resource integration. Practitioner vytvára `TrainJob` cez SDK alebo API. Trainer nastaví distributed environment a spustí framework-specific processes, ale training algorithm a checkpoint correctness zostávajú zodpovednosťou training code.

```python
from kubeflow.trainer import TrainerClient
from kubeflow.trainer.types import Trainer

client = TrainerClient()
client.train(
    trainer=Trainer(
        func=train_func,
        num_nodes=2,
        resources_per_node={"gpu": 4},
    ),
    runtime="torch-distributed",
)
```

Príklad je model surface, nie univerzálny production manifest. Reálny deployment musí pinovať runtime generation, container digest, dataset access, node/GPU constraints, service account a output root. Trainer status potvrdí orchestration outcome, nie complete model acceptance.

Starý Training Operator V1 je legacy smer. Nová dokumentácia má používať Trainer V2 ako primárny model a V1 spomínať iba pri migrácii alebo existujúcej platforme.

## 11. Resource a network dependencies

Distributed training pridáva synchronized failure domain. Jeden pomalý worker spomaľuje všetkých. GPU compute, host CPU, memory, local storage, dataset throughput a interconnect sú súčasťou jednej critical path. High GPU allocation bez dostatočného input pipeline môže viesť k nízkej utilization.

Chapter o GPU scheduling bude neskôr riešiť capacity detailne. Tu je hranica taká, že job manifest musí uviesť resource topology a training evidence musí odlíšiť compute time, data wait, collective time a checkpoint time. Bez toho sa scale-out rozhodnutie robí naslepo.

## 12. CI a pre-production testovanie training jobu

Full distributed run je drahý a nepatrí do každého PR. CI však môže overiť training function na CPU alebo jednej GPU, distributed initialization na dvoch local processes, sampler partitioning, one-step gradient parity, checkpoint save/restore a failure injection.

```bash
torchrun --standalone --nnodes=1 --nproc-per-node=2 \
  tests/distributed_smoke.py \
  --dataset tests/fixtures/tiny-dataset.manifest.json \
  --steps 3
```

Smoke test má potvrdiť, že každý sample má expected ownership, gradients sa synchronizujú, checkpoint sa dá načítať fresh procesom a druhý resume pokračuje z intended step. Nemá predstierať production convergence.

## 13. Evidence hierarchy

Configured evidence je TrainJob, runtime a resolved training config. Loaded evidence je worker group, image IDs, ranks, world size a process-group initialization. Exercised evidence sú per-rank steps, collectives, samples seen, optimizer updates a checkpoint manifests. Candidate evidence je evaluation a package. Business evidence vzniká až po model delivery.

```bash
kubectl get trainjob -n ml-training risk-r22 -o yaml
kubectl get pods -n ml-training -l trainer.kubeflow.org/trainjob-name=risk-r22 -o wide
kubectl logs -n ml-training risk-r22-node-0 --all-containers
```

Pod `Running` nepreukazuje progress. TrainJob `Succeeded` nepreukazuje complete checkpoint. Object-store path nepreukazuje content integrity. Každá vrstva potrebuje vlastný read-back.

## 14. Competing failure hypotheses

Pri zlom alebo nereprodukovateľnom model candidate sa rozlišuje data-partition hypothesis, initialization/config mismatch, communication failure, straggler/resource problem, checkpoint/resume divergence a evaluation mismatch. Duplicated samples sa prejavia overlapom per-rank sample IDs. Communication failure sa prejaví rank-specific first errorom a ostatnými ranks waiting v collective. Resume divergence sa potvrdí chýbajúcim optimizer/RNG stateom alebo rozdielnym step fingerprintom.

Model-quality symptom sa nesmie automaticky pripísať distributed strategy. Najprv sa overí, či single-process baseline s rovnakým global batch a steps vytvára accepted result. Potom sa porovnajú step-level losses, gradient norms a checkpoint fingerprints. Jedna zmena naraz zachová atribúciu.

## 15. Recovery a acceptance

Containment zastaví promotion candidate a zachová per-rank evidence. Recovery obnoví job z posledného complete checkpointu alebo spustí nový subject, ak equivalence nie je preukázaná. Partial checkpoint sa nepoužije iba preto, že je najnovší.

Pozitívny acceptance test potvrdí unique data partition, expected global batch, synchronized updates, complete checkpoint a fresh-process restore. Forbidden test odmietne mismatched dataset digest, world-size change bez policy a weights-only resume prezentovaný ako exact continuation. Failure test ukončí jeden rank a overí preservation, worker-group generation a bounded restart. Second-operation test načíta final package na oddelenom inference workerovi.

Training pipeline je uzavretá, keď sa dá vysvetliť každý optimizer step, checkpoint a worker-group transition dostatočne na reprodukciu alebo bezpečné odmietnutie. Zelený distributed job bez tejto evidence je iba execution status.

## Primárne zdroje

- [PyTorch — DistributedDataParallel](https://docs.pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html)
- [PyTorch — torchrun](https://docs.pytorch.org/docs/stable/elastic/run)
- [Kubeflow Trainer — Overview](https://www.kubeflow.org/docs/components/trainer/overview/)
- [Kubeflow Trainer — Getting started](https://www.kubeflow.org/docs/components/trainer/getting-started/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: ML pipeline orchestration](ml-pipeline-orchestration.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CI pre ML code, data a pipelines →](ci-for-ml-code-data-pipelines.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
