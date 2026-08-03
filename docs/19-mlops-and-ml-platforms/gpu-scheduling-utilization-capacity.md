# GPU scheduling, utilization a capacity

GPU platforma premieňa heterogénne akcelerátory na schedulovateľnú kapacitu, no Kubernetes samotný nevie, či model potrebuje celý device, MIG slice, time-sliced access alebo konkrétnu topology. Vysoká GPU utilization preto nie je automaticky dôkazom dobrej kapacity. Workload môže mať plný device a stále nedodržať deadline, alebo môže vykazovať nízke využitie preto, že čaká na features, CPU preprocessing či sieť.

V incidente `MLOPS-PAY-94` sa online inference presunula z izolovaného GPU profilu na time-slicing, aby sa zvýšilo vykázané využitie. Scheduler úspešne pridelil virtuálne GPU replicas, ale time-slicing neposkytoval memory ani fault isolation. Susedný batch workload zvýšil memory pressure a tail latency. Dashboard ukazoval priemernú utilization, no nie queue age, memory high-water mark ani deadline success. Oprava preto vyžadovala obnoviť exact resource class, isolation policy a request-level capacity evidence.

## 1. Device lifecycle a authority

GPU lifecycle zahŕňa fyzický device, driver, container runtime integration, Kubernetes device plugin, node labels, advertised extended resource, scheduler binding, device injection a runtime initialization. NVIDIA GPU Operator môže spravovať driver, Container Toolkit, device plugin, GPU Feature Discovery, MIG Manager a DCGM monitoring, ale každá vrstva má vlastný observed state.

```text
physical GPU
→ driver a runtime
→ device plugin advertisement
→ node allocatable resource
→ scheduler binding
→ device injection
→ accelerator initialization
→ model allocation
→ useful inference alebo training work
```

`Pod Running` potvrdzuje iba scheduling a container start. Nepotvrdzuje CUDA compatibility, úspešný model allocation, správnu topology ani užitočný throughput. Authoritative capacity preto prechádza od Kubernetes API cez runtime a DCGM telemetry až po workload a business metrics.

Resource subject musí viazať node-pool generation, GPU model a memory, driver/runtime version, device-plugin configuration, sharing mode, MIG profile a workload class. Generic label `gpu=true` nie je reprodukovateľný capacity contract.

## 2. Kubernetes extended resources

Device plugin publikuje GPU ako extended resource, typicky `nvidia.com/gpu` alebo resource name odvodený od MIG profilu. Workload žiada integer quantity. Scheduler pridelí Pod iba vtedy, keď node reportuje dostatočný allocatable resource a spĺňa affinity, taints, quota a topology constraints.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: model-gpu-smoke
  namespace: ml-prod
spec:
  restartPolicy: Never
  nodeSelector:
    accelerator.example.com/class: a100-mig-2g
  tolerations:
    - key: nvidia.com/gpu
      operator: Exists
      effect: NoSchedule
  containers:
    - name: smoke
      image: registry.example.com/model-server@sha256:8ab1...
      resources:
        requests:
          cpu: "2"
          memory: 6Gi
        limits:
          cpu: "4"
          memory: 8Gi
          nvidia.com/mig-2g.20gb: 1
```

Exact resource name závisí od device-plugin a MIG strategy. Scheduler nepozná business význam profilu. Platforma preto definuje resource classes a admission policy, ktoré viažu workload na podporovaný device, memory headroom, topology a isolation level.

Read-back používa node a Pod observed state:

```bash
kubectl get nodes -L nvidia.com/gpu.product,nvidia.com/mig.strategy
kubectl describe node <gpu-node>
kubectl -n ml-prod describe pod model-gpu-smoke
```

`Allocated resources` je scheduler pohľad. Fyzickú a runtime realitu dopĺňa DCGM a workload telemetry.

## 3. Exclusive GPU, MIG a time-slicing

Exclusive GPU poskytuje celý device jednému workloadu. Je vhodný pre veľké modely, latency-sensitive serving alebo training, ktorý využíva väčšinu kapacity. Nevýhodou môže byť nízka utilization pri malých alebo bursty workloadom.

MIG rozdeľuje podporovaný GPU na hardvérovo izolované instances s definovaným memory a compute profilom. Zlepšuje memory a fault isolation, ale profily sú diskrétne. Cluster môže mať voľnú celkovú kapacitu a zároveň nemať voľný požadovaný profil.

Time-slicing vytvorí viac schedulovateľných replicas nad jedným fyzickým GPU. Procesy sa striedajú v čase, ale nezískajú memory ani fault isolation. Požiadavka na viac time-sliced replicas negarantuje proporcionálne viac compute. Tento režim je vhodný iba pre workloady, ktoré akceptujú interference a majú vlastné latency a memory guardrails.

```yaml
gpu_class: a100-online-v3
physical_model: A100-80GB
sharing:
  mode: MIG
  profile: 2g.20gb
isolation:
  memory: hardware
  fault: hardware-instance
admission:
  workload_class: online-inference
  max_model_memory_gib: 14
  latency_slo_ms: 120
```

Zmena sharing mode mení capacity generation. Historický load test z exclusive alebo MIG profilu nie je authoritative pre time-sliced runtime.

## 4. Utilization, useful throughput a memory

GPU utilization vyjadruje aktivitu device počas meraného intervalu, nie počet úspešných business operácií. Capacity view preto kombinuje useful throughput, queue age, deadline success, compute utilization, memory high-water mark, batch size, input shape, sharing profile, error count a cost na úspešnú operáciu.

Pre training sa pridáva samples alebo tokens per second, step time, data-loader wait, collective time a checkpoint overhead. Pre serving sa pridáva batch wait, model compute, time-to-first-response a fallback rate. Vysoká utilization s rastúcou queue znamená saturáciu alebo interference; nízka utilization s rastúcou queue môže znamenať bottleneck mimo GPU.

DCGM Exporter sprístupňuje GPU telemetry v Prometheus formáte. Exporter a DCGM musia používať podporovanú verziu a metric labels musia zachovať stabilnú node, GPU/MIG, resource-class a release identity. Pri time-slicingu môže byť workload attribution obmedzená; tento blind spot patrí do risk acceptance.

GPU memory budget zahŕňa weights, runtime workspace, activations alebo KV cache, batching buffers a allocator reserve. Idle memory po warmup nie je peak requirement. Load test musí pokryť reprezentatívne input shapes a concurrency. Runtime readiness nesmie byť true pred úspešným allocation a warmup.

## 5. Fragmentation, queueing a autoscaling

Fragmentation vzniká, keď voľné resources nie sú na rovnakom node, v správnom MIG profile alebo s požadovanou topology. Celkový počet voľných GPU preto nestačí. Scheduler events a exact allocatable resource names majú vyššiu diagnostickú hodnotu.

Bin packing zvyšuje utilization, ale môže zhoršiť blast radius a interference. Spread zvyšuje isolation, no môže blokovať veľké distributed jobs. Online serving, development, batch inference a training potrebujú odlišnú priority, preemption a queue policy.

Pod autoscaler mení desired replicas; cluster autoscaler pridáva nodes. GPU node provisioning zahŕňa driver, device plugin, labels, prípadnú MIG konfiguráciu a model warmup. Traffic s krátkym deadline preto potrebuje warm reserve alebo preprovisioning. Scale-down musí rešpektovať checkpointing trainingu, draining servingu a minimálnu ready kapacitu.

```text
installed physical capacity
→ healthy advertised capacity
→ allocatable capacity
→ admitted workload capacity
→ ready runtime capacity
→ exercised useful capacity
```

Rozdiel medzi advertised a exercised capacity odhaľuje driver chyby, cold initialization, fragmentation a interference.

## 6. Failure hypotheses a recovery

Pri Pending podoch sa skúma resource-name mismatch, MIG profile, taint, affinity, quota, device-plugin health a node lifecycle. Pri nízkom throughput a vysokej utilization sa skúma batch policy, compute saturation a sharing interference. Pri nízkej utilization a rastúcej queue sa skúma feature/input bottleneck, CPU preprocessing alebo nesprávna metric attribution. Pri OOM sa skúma peak memory podľa input a concurrency, nie iba model size.

Containment môže oddeliť online workload od batch tenantov, vrátiť službu z time-slicingu na MIG/exclusive profil, znížiť concurrency alebo zastaviť admission nových training jobs. Pred reštartom sa zachytí node/resource state, device-plugin evidence, GPU telemetry, Pod events a loaded release.

Pozitívna acceptance vyžaduje deklarovaný resource class, úspešný GPU smoke test na každej ready replike, memory headroom a load test tail latency aj useful throughput. Recovery acceptance vyžaduje overiť isolation mode a ďalší workload po oprave. Forbidden acceptance je cluster-wide utilization, `Pod Running` alebo allocatable count bez request a outcome evidence.

Second-operation test spustí ďalší Pod alebo model load rovnakého profilu. Ak prvá operácia zanechala fragmentovaný layout alebo neobnoviteľný device state, druhá operácia problém odhalí. Stabilná GPU platforma musí reprodukovať pridelenie a výkon bez manuálneho čistenia node.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Model serving a autoscaling](model-serving-autoscaling.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Model monitoring →](model-monitoring.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
