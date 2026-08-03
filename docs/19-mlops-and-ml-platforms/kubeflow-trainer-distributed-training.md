# Kubeflow Trainer a distributed training

Kubeflow Trainer V2 je Kubernetes-native platforma pre distribuovaný tréning a fine-tuning. Jeho hlavné authority surfaces sú `TrainJob`, Training Runtime a framework-level distributed program. Platforma nerobí chybný tréning správnym: pripraví worker topology, runtime a orchestration, ale dataset partitioning, random seeds, collective semantics, checkpoint completeness a model-quality acceptance zostávajú zodpovednosťou workloadu.

V incidente `MLOPS-PAY-97` KFP odoslala nový `TrainJob` so štyrmi GPU nodes. Platform administrator medzitým patchol shared Runtime a zmenil launcher environment aj checkpoint mount. Job skončil `Succeeded`, no každý worker čítal prekrývajúci sa dataset shard a checkpoint obsahoval iba model weights, nie optimizer, scheduler, sampler epoch ani RNG state. Po node failure sa „resume“ spustil s inou world size a vytvoril nereprodukovateľný candidate. Príčina nebola iba v PyTorch kóde ani iba v Kubernetes: chýbal immutable subject spájajúci TrainJob, Runtime, worker group, data partition a checkpoint generation.

## 1. TrainJob subject a Runtime authority

TrainJob opisuje konkrétnu training operation. Runtime je platformou spravovaný template a policy boundary, ktorý určuje launcher, images, distributed configuration, volumes a ďalšie defaults. Referencia na Runtime name bez generation alebo resolved manifestu nie je reproducible input.

```yaml
training_subject:
  train_job: fraud-train-2026-08-03.4
  runtime_name: torch-distributed
  runtime_generation: "17"
  source_commit: 8c1e4c7
  training_image: registry.example/train@sha256:...
  dataset_snapshot: fraud-train-2026-07-31
  feature_generation: fraud-features-v14
  nodes: 4
  devices_per_node: 1
  global_batch_size: 512
  checkpoint_generation: fraud-ckpt-v4
```

Platforma pri submit-e uloží requested TrainJob aj controller-resolved workload. Runtime mutation po submit-e nesmie spätne meniť identitu už schváleného operation.

## 2. Kubeflow Trainer V2, nie legacy Training Operator

Aktuálny smer dokumentácie používa Trainer V2 s `TrainJob` a Runtimes. Legacy Training Operator V1 používal framework-specific CRDs ako `PyTorchJob`, `TFJob` alebo `MPIJob`; tie patria do migration a compatibility contextu, nie ako primárny model novej kapitoly.

Trainer V2 oddeľuje practitioner API od administrator-managed Runtime. Practitioner dodáva training function alebo custom trainer configuration. Administrator spravuje Runtime, scheduling integrácie, images, storage a policy. Toto rozdelenie znižuje opakovanie YAML-u, ale zvyšuje dôležitosť Runtime versioning a change control.

## 3. Praktický TrainJob cez Python SDK

Aktuálny SDK môže spustiť custom PyTorch training function cez `TrainerClient` a `CustomTrainer`. Exact package version sa pinne v lockfile; príklad je interface pattern, nie slepý copy-paste contract pre každú release.

```python
from kubeflow.trainer import TrainerClient, CustomTrainer

def train_pytorch():
    import os
    import torch
    import torch.distributed as dist
    from torch.nn.parallel import DistributedDataParallel
    from torch.utils.data import DataLoader, DistributedSampler

    backend = "nccl" if torch.cuda.is_available() else "gloo"
    dist.init_process_group(backend=backend)

    local_rank = int(os.environ["LOCAL_RANK"])
    device = torch.device(f"cuda:{local_rank}")
    model = build_model().to(device)
    model = DistributedDataParallel(model, device_ids=[local_rank])

    dataset = load_versioned_dataset()
    sampler = DistributedSampler(
        dataset,
        num_replicas=dist.get_world_size(),
        rank=dist.get_rank(),
        shuffle=True,
    )
    loader = DataLoader(dataset, sampler=sampler, batch_size=128)

    for epoch in range(10):
        sampler.set_epoch(epoch)
        train_one_epoch(model, loader, device)

    save_complete_checkpoint(model, dist.get_rank())
    dist.destroy_process_group()

client = TrainerClient()
job_id = client.train(
    trainer=CustomTrainer(
        func=train_pytorch,
        num_nodes=4,
        resources_per_node={
            "cpu": 4,
            "memory": "24Gi",
            "gpu": 1,
        },
    )
)
print(job_id)
```

`num_nodes=4` nepreukazuje štyri usable GPU workers. Acceptance číta job steps, Pod placement, allocated devices, process-group world size a framework logs.

## 4. Rank, local rank a world size

Distributed program musí rozlišovať global rank, local rank a world size. Global rank identifikuje process v celom worker groupe. Local rank identifikuje process na node a typicky mapuje GPU. World size je počet participating processes v aktuálnej collective generation.

Nesprávne použitie local ranku ako global identity spôsobí duplicate writes alebo duplicate dataset shards. Artifact zapisuje iba určený coordinator rank alebo používa distributed-safe shard/manifest protocol. Každý worker loguje job ID, restart generation, rank, world size, dataset shard a checkpoint generation.

## 5. Dataset partitioning a global batch

`DistributedSampler` rozdeľuje sample indices medzi replicas, ale aplikácia musí volať `set_epoch()` pri shuffle, aby všetky procesy použili koordinovanú novú permutation. Streaming dataset potrebuje vlastný deterministic partition contract podľa shard/offset identity.

Global batch nie je automaticky local batch:

```text
global batch
= per-process batch
× number of data-parallel processes
× gradient accumulation steps
```

Zmena world size bez úpravy learning-rate, scheduleru alebo accumulation mení optimization semantics. Elastic resume preto nie je iba scheduling event; môže vytvoriť novú training generation.

## 6. Collectives a failure model

DDP synchronizuje gradients cez collectives. Jeden slow alebo failed rank môže zablokovať celý group. Pod readiness neznamená, že NCCL/Gloo collective funguje. Preflight test overuje DNS, ports, network policy, device visibility, shared storage a malý collective.

Timeout sa klasifikuje: networking, topology, GPU fault, OOM, data loader stall alebo divergent code path. Blind retry môže opakovať deterministickú chybu a spotrebovať GPU capacity. Attempt evidence zachytí first failing rank a stderr ešte pred cleanupom.

## 7. Runtime, JobSet a scheduling

Trainer sa integruje s Kubernetes ecosystemom pre coordinated jobs, napríklad JobSet, Kueue alebo inými schedulermi. Pending TrainJob môže znamenať queue policy, quota, topology constraint, chýbajúci GPU resource alebo unschedulable gang, nie controller failure.

Admission do queue nie je training success. Scheduler reservation, Pod binding, device allocation, process-group initialization a first useful step sú samostatné milestones. Platforma meria queue time, startup time, data warmup a useful GPU training time oddelene.

Runtime môže obsahovať patches pre volumes, environment, sidecars alebo scheduler integration. Patches sú executable authority a musia mať review, schema validation a resolved manifest evidence.

## 8. Checkpoint completeness

Production checkpoint nie je iba `state_dict()` modelu. Resume-equivalent checkpoint typicky zahŕňa model weights, optimizer state, scheduler/scaler state, current epoch a global step, sampler/data cursor, RNG states, framework a code generation, world-size/topology metadata a dataset/feature snapshot identity.

Checkpoint publication používa staging path, checksums a atomic committed manifest. Coordinator nesmie označiť checkpoint ako complete pred dokončením všetkých shardov. Restore test načíta checkpoint v čistom environment-e a vykoná ďalšie training steps alebo deterministic evaluation.

## 9. Elasticity a restart generation

Elastic worker replacement môže obnoviť dostupnosť, ale každá zmena membership vytvára novú process-group generation. Framework musí vedieť, či pokračuje od posledného committed checkpointu alebo opakuje časť práce. Side effects ako metric logging, artifact upload alebo dataset offset commits musia byť idempotentné podľa job a restart generation.

Weights-only resume po zmene world size môže vyzerať funkčne, ale nie je reprodukcia. Ak platforma povoľuje elasticity, acceptance policy explicitne definuje tolerované topology changes a parity expectations.

## 10. Metrics a model acceptance

Trainer job status `Succeeded` znamená, že orchestrated workload dosiahol úspešný terminal condition. Neznamená to, že loss je finite, dataset bol správny, model package vznikol alebo candidate prešiel evaluation. Framework logs a training metrics sa viažu na immutable subject a prenášajú do tracking systému.

NaN loss, zero samples, duplicate shards alebo fallback CPU training môžu stále skončiť bez Kubernetes erroru. Training wrapper preto failne job pri invariant violation a vytvorí explicitný result class.

## 11. Security a multi-tenancy

Training code spracúva citlivé datasets a často má prístup k drahým GPU a artifact stores. Runtime service account nesmie byť cluster-admin. Dataset read, checkpoint write a Registry publication používajú oddelené identities alebo steps. User-provided code sa neberie ako trusted iba preto, že beží cez managed Runtime.

Images sú pinned digestom, signed a scanned. Init containers a distributed cache sú tiež súčasť trust boundary. Secrets sa nemajú objaviť v function serialization, environment dumpoch ani logs.

## 12. Failure hypotheses a recovery

Ak job zostane Pending, kontroluje sa queue/admission, quotas, node labels, taints, topology a GPU allocatable. Ak Pods bežia, ale training nezačne, skúma sa runtime resolution, launcher, rendezvous, network a data access. Ak model quality klesne, porovná sa data partition, global batch, world size, seeds, code, checkpoint a feature generation.

Containment zastaví retries, uchová failed Pods/logs a zmrazí Runtime mutation. Recovery vytvorí nový TrainJob z pinned Runtime generation, načíta posledný complete checkpoint alebo začne čistý run nad immutable datasetom a vykoná distributed preflight.

## 13. Acceptance

Pozitívna acceptance vyžaduje exact TrainJob a resolved Runtime, správnu worker/device topology, non-overlapping data partition, valid collectives, complete checkpoint, model artifact digest a downstream evaluation. Recovery acceptance vyžaduje čistý restore, ďalší committed checkpoint a parity v počte processed samples a metrics.

Forbidden acceptance je `Succeeded` status, všetky Pods `Completed`, viditeľné GPU requesty alebo existujúci weights file bez optimizer/sampler/RNG state. Second-operation test spustí rovnaký immutable subject druhýkrát alebo resume z committed checkpointu. Rozdiely musia byť vysvetliteľné povolenou stochasticitou; duplicate samples, artifacts alebo Registry mutations znamenajú chybnú idempotency alebo lineage.
