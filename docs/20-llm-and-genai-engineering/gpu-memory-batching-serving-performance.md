# GPU memory, batching a serving performance

LLM serving performance vzniká interakciou model weights, attention/KV cache, request scheduleru, batching policy, kernels, accelerator topology, sequence lengths a service-level objectives. Jedno číslo `tokens/s` necharakterizuje production system. Rovnaký server môže mať vysoký offline throughput a neprijateľný time-to-first-token, queue delay alebo out-of-memory rate pri reálnom mixe krátkych a dlhých requestov.

V incidente `GENAI-SUPPORT-06` tím zvýšil maximum batch size a zapol continuous batching, aby zlepšil throughput. Benchmark s krátkymi promptmi ukázal výrazný gain. Produkčný traffic však obsahoval dlhé RAG contexty, viac LoRA adapters a dlhé tool-generated outputs. KV cache zaplnila GPU, scheduler začal odkladať nové prefills a niektoré workers skončili OOM. Retry traffic ešte zvýšil queue. Dashboard naďalej ukazoval vysoké aggregate tokens/s, no p95 time-to-first-token a ticket-resolution latency prekročili SLO. Root cause bolo optimalizovanie peak throughputu bez memory modelu, workload distribution, admission control a tail-latency acceptance.

## 1. Business outcome a serving contract

Serving sa navrhuje od user journey a SLO:

```text
request arrival
→ admission a queue
→ prefill
→ decode a tools
→ validated output
→ business outcome
```

Model server success sa nemeria iba tým, že vygeneruje tokens. Dôležité sú accepted requests, latency distribution, reliability, cost, quality a downstream completion.

```yaml
serving_slo:
  workload: support-assistant
  availability: 99.9%
  p95_time_to_first_token_ms: 1200
  p95_inter_token_latency_ms: 80
  p95_end_to_end_ms: 9000
  schema_success_rate: 99.5%
  oom_rate: 0
  overload_behavior: explicit_429
```

## 2. Exact serving subject

Performance result je platný iba pre konkrétny subject:

```yaml
serving_subject:
  model_release: support-local-int4-v6
  adapter_generation: refund-lora-v7
  runtime: vllm-like-engine-v14
  container_digest: sha256:9f11...
  gpu_type: accelerator-24gb
  gpu_count: 2
  tensor_parallel: 2
  data_parallel: 1
  max_model_len: 32768
  kv_cache_dtype: fp16
  scheduler_policy: continuous-v5
  max_batched_tokens: 32768
  max_sequences: 64
  prefix_cache: enabled
  workload_generation: support-traffic-2026-08-04
```

Zmena runtime, kernel, model, adapter, context limit alebo scheduler config vytvára nový benchmark subject.

## 3. GPU memory vrstvy

Peak GPU memory typicky zahŕňa:

```text
model weights
+ KV cache
+ activations a temporary tensors
+ CUDA graphs alebo compiled buffers
+ communication buffers
+ runtime allocator reserve/fragmentation
+ adapters a prefix cache
```

Framework metric `allocated` nemusí zahŕňať celý reserved pool. Device metric a runtime allocator telemetry sa interpretujú spolu.

## 4. Weight memory

Hrubý estimate:

```text
weight memory ≈ parameter_count × bytes_per_weight
```

FP16/BF16 používajú približne dva bytes na parameter, FP32 štyri a quantized formats menej, ale pridávajú scales, zero points a unquantized modules. Tensor parallelism rozdeľuje časť weights medzi GPUs, no môže duplikovať embeddings, heads alebo buffers podľa architecture/runtime.

Weight fit je statická podmienka. Po načítaní modelu musí zostať headroom pre KV cache a transient allocations.

## 5. Prefill a decode

Autoregressive inference má dve odlišné fázy:

```text
prefill
→ spracuje celý input prompt a vytvorí prvé KV states
→ compute-heavy, paralelný cez tokens

decode
→ generuje ďalšie tokens po jednom
→ opakovane číta KV cache
→ často memory-bandwidth a latency sensitive
```

Dlhé RAG prompty zvyšujú prefill cost. Dlhé outputs predlžujú decode a držia KV blocks dlhšie. Jedno aggregate `tokens/s` môže miešať dva odlišné bottlenecks.

## 6. KV cache

KV cache uchováva key/value states pre predchádzajúce tokens v každej relevantnej layer. Jej veľkosť rastie približne lineárne s počtom aktívnych tokenov, layers, KV heads, head dimension a bytes per element.

Zjednodušený estimate:

```text
KV bytes ≈
2 × layers × active_tokens × kv_heads × head_dim × bytes_per_element
```

Faktor `2` reprezentuje keys a values. Architecture s grouped-query alebo multi-query attention môže mať menej KV heads než attention heads. Runtime layout, alignment a paging pridávajú overhead.

## 7. Sequence length a concurrency

Concurrency nie je iba počet requests. Memory pressure závisí od súčtu aktívnych prompt a generated tokens.

```text
10 requests × 1k tokens
≠
10 requests × 32k tokens
```

Capacity model používa workload distribution: prompt percentiles, output percentiles, tool-loop count, cancellation rate a adapter mix. Maximum context limit sa neplánuje ako priemerný request.

## 8. Static batching

Static batching čaká na skupinu requests a spracuje ich spolu. Padding k najdlhšej sequence môže plytvať compute a zvyšovať latency krátkych requests.

Je vhodný pre offline alebo homogeneous workloads, kde je acceptable čakať na batch window. Pri interactive traffic potrebuje bounded wait a length-aware grouping.

```yaml
static_batch:
  max_batch_size: 32
  max_wait_ms: 25
  length_buckets: [512, 2048, 8192]
```

Batch size bez token budgetu je nebezpečný pri variabilných sequences.

## 9. Continuous batching

Continuous batching pridáva nové requests, keď iné dokončia decode, namiesto čakania na celý batch. Zlepšuje utilization pri rôznych output lengths.

Scheduler však musí rozhodovať medzi novými prefills a decode steps existujúcich sequences. Agresívne prefills môžu zhoršiť inter-token latency; decode priority môže vyhladovať nové requests a zvýšiť TTFT.

```text
scheduler objective
≠ maximum GPU utilization

scheduler objective
= SLO-aware allocation medzi prefill, decode a memory
```

## 10. Paged KV memory

PagedAttention-style runtimes rozdeľujú KV cache do blocks podobných virtual-memory pages. Tým znižujú fragmentation a umožňujú flexibilnejšie prideľovanie sequences.

```text
logical token positions
→ mapping na physical KV blocks
→ share/copy-on-write podľa runtime
```

Paging zlepšuje memory utilization, ale nevytvára nekonečnú memory. Pri vyčerpaní blocks musí scheduler rejectnúť, preemptnúť, swapnúť alebo čakať. Každá stratégia má latency a reliability dôsledky.

## 11. Fragmentation a allocator behavior

Memory môže byť teoreticky voľná, ale nedostupná pre požadovanú contiguous allocation alebo runtime reserve. Paged KV rieši konkrétnu fragmentáciu KV cache; activations a kernels môžu stále potrebovať veľké buffers.

Monitoring odlišuje:

```text
weights
KV blocks used/free
framework allocated
framework reserved
GPU device used
largest transient allocation
```

OOM bez rastu request countu môže vzniknúť z dlhších contexts, compilation, adapter loading alebo memory leak.

## 12. Admission control

Server nemá prijať neobmedzené work. Admission policy odhaduje token a memory cost pred execution:

```text
authenticated request
→ input size a route
→ estimated prefill/KV cost
→ tenant quota a priority
→ admit, queue alebo explicit reject
```

Explicitné `429` alebo overload response je bezpečnejšie než timeout po desiatkach sekúnd alebo worker crash. High-risk requests môžu mať rezervovanú capacity.

## 13. Queueing a backpressure

Queue length sama osebe nehovorí, ako dlho request čaká. Sleduje sa queue time distribution a token-weighted backlog.

```text
queued_work ≈
Σ estimated_prefill_tokens + estimated_decode_tokens
```

Backpressure sa prenáša na gateway a upstream callers. Blind retry bez jitter/idempotency vytvára retry storm. Timeout budget sa delí medzi queue, inference, tools a downstream validation.

## 14. Scheduling fairness

Shortest-job-first môže zlepšiť average latency, ale vyhladovať long-context requests. FIFO môže zablokovať krátke requests za jedným veľkým prefillom. Tenant-blind scheduler môže umožniť noisy neighborovi spotrebovať všetky KV blocks.

Production policy kombinuje priority, aging, token budgets a tenant quotas. Fairness sa evaluačne testuje na mixed workload, nie iba deklaruje v configu.

## 15. Batch limits

Relevantné limits sú:

```text
max active sequences
max batched input tokens
max total active tokens
max sequence length
max prefill chunk
max adapter set
```

`max_batch_size=64` bez `max_batched_tokens` môže pri 32k prompts spôsobiť extrémny prefill. Token-based limit je presnejší, ale stále potrebuje memory calibration.

## 16. Chunked prefill

Chunked prefill rozdelí dlhý prompt na menšie segments, aby neblokoval decode traffic a nevyžadoval obrovský transient batch.

Trade-off zahŕňa viac scheduler steps a možný overhead. Config sa optimalizuje proti TTFT, inter-token latency a throughput pre mixed lengths.

```yaml
prefill_policy:
  chunking: enabled
  max_chunk_tokens: 2048
  decode_priority_budget_ms: 50
```

Exact semantics závisia od runtime; názov feature nie je cross-engine contract.

## 17. Prefix/KV reuse

Ak requests zdieľajú identický token prefix a effective model state, runtime môže reuse-nuť precomputed KV blocks. To znižuje prefill compute, ale cache entries musia byť scoped podľa model, adapter, tokenizer/template a security boundary.

Prefix caching nešetrí decode nových tokens a nemení answer semantics. Cache hit sa meria v reused tokens/blocks, nie iba boolean request hit.

## 18. Adapter serving

Multi-LoRA serving môže držať viac adapters v GPU/CPU memory a prepínať ich per request. Adapter load, eviction a kernel support ovplyvňujú latency.

KV cache vytvorená pod jedným effective adapterom sa nesmie reuse-nuť pod iným, pokiaľ runtime explicitne nepreukazuje compatibility. Adapter identity je súčasť cache key a serving trace.

## 19. Parallelism

Tensor parallelism rozdeľuje jednotlivé layers/tensors medzi GPUs a vyžaduje communication pri každom relevantnom step. Pipeline parallelism rozdeľuje layer groups a môže vytvárať bubbles. Data parallelism replikuje model a rozdeľuje requests.

```text
tensor parallel
→ väčší model fit, vyššia interconnect citlivosť

data parallel
→ vyššia request throughput, celý model per replica

pipeline parallel
→ layer partition, scheduling complexity
```

Viac GPUs nezaručuje lineárny speedup. Topology, NVLink/PCIe/network a batch size určujú communication overhead.

## 20. Speculative decoding

Speculative decoding používa draft model alebo mechanizmus na návrh viacerých tokens, ktoré target model overí. Môže zlepšiť decode throughput, ak acceptance rate a overhead sú priaznivé.

Je to nový serving subject: draft model/version, tokenization compatibility, speculation length a verification algorithm. Quality má zostať podľa target distribution pri korektnom algoritme, no latency benefit sa meria na workloadu. Feature môže interagovať s prefix caching a batching.

## 21. Quantized KV cache a weights

Weight quantization uvoľní memory pre KV cache, ale môže zmeniť kernels a throughput. KV quantization znižuje per-token memory, no môže ovplyvniť attention quality.

Každá precision layer sa pinne:

```yaml
precision:
  weights: int4-gptq
  activations: bf16
  accumulation: fp32-selected
  kv_cache: fp8
```

Memory gain sa hodnotí spolu s target a long-context quality evalom.

## 22. Time-to-first-token

TTFT zahŕňa gateway, queue, tokenization, prefill a prvý decode step. Vysoký TTFT môže vzniknúť aj pri rýchlom decode.

```text
TTFT =
network/gateway
+ queue
+ tokenization/serialization
+ prefill
+ first decode
```

Sleduje sa per prompt-length bucket a tenant priority. Aggregate p95 bez length segmentation je ťažko diagnostikovateľný.

## 23. Inter-token latency a generation speed

Inter-token latency, ITL, charakterizuje streaming cadence po prvom tokene. Používateľ môže tolerovať vyšší TTFT pri analytickom tasku, ale nie nepravidelné dlhé pauzy počas streamu.

Decode tokens/s per request a aggregate tokens/s sú rozdielne metrics. Batching môže zvýšiť aggregate throughput a súčasne spomaliť každý jednotlivý stream.

## 24. End-to-end latency

Model server latency nie je celý product journey. Retrieval, tool calls, schema repair, retries a business API read-back môžu dominovať.

```text
request latency
→ retrieval
→ model prefill/decode
→ tools
→ validation
→ authoritative read-back
```

Serving optimization sa spája s accepted outcome. Rýchly invalid output, ktorý vyvolá retry, zhoršuje total latency aj cost.

## 25. Benchmark dataset

Benchmark traffic reprezentuje production distributions:

```yaml
workload_mix:
  prompt_tokens:
    p50: 1800
    p95: 12000
    p99: 28000
  output_tokens:
    p50: 220
    p95: 1100
  adapters:
    general: 0.65
    refund: 0.25
    multilingual: 0.10
  arrival:
    steady_rps: 8
    burst_rps: 24
```

Synthetic fixed-length prompts sú microbenchmark. Capacity verdict potrebuje open-loop arrival test, burst, cancellation, timeout a retry behavior.

## 26. Open-loop a closed-loop load

Closed-loop client čaká na response pred ďalším requestom; pri spomalení automaticky znižuje offered load a môže skryť overload. Open-loop generator udržiava plánovanú arrival rate a ukáže queue collapse.

Production capacity test používa kontrolovaný open-loop profile s bezpečnými limits. Sleduje sa bod, kde SLO začína zlyhávať, nie iba maximum pred crashom.

## 27. Warm-up a compilation

Prvý request môže platiť model load, kernel compilation, CUDA graph capture alebo cache initialization. Benchmark oddelí cold start a steady state.

Autoscaling potrebuje cold-start SLO. Replica označená ready pred warm-up môže poslať prvých userov na extrémne pomalý path.

```text
process ready
≠ model loaded
≠ kernels warm
≠ representative context capacity ready
```

## 28. Autoscaling

GPU serving scaling signal nemá byť iba utilization. Pri plnom KV cache môže compute utilization klesnúť, zatiaľ čo queue rastie. Vhodné signals zahŕňajú token backlog, queue age, active KV blocks, SLO burn a admission rejects.

Scale-out latency a model artifact size vyžadujú headroom. Autoscaler, ktorý reaguje až po p95 breach, môže byť príliš pomalý pre burst traffic.

## 29. Fault domains a recovery

Worker crash môže zrušiť in-flight generations. Gateway potrebuje idempotent retry policy a musí rozlišovať read-only generation od tool side effectu. Streaming partial output sa nesmie automaticky commitnúť ako business result.

Multi-GPU replica môže zlyhať ako celok pri jednom device/process fault. Fault domain sa modeluje podľa tensor-parallel group, node a zone.

## 30. Observability

Serving telemetry zahŕňa:

```text
arrival rate a admitted/rejected
queue length, token backlog a queue age
active sequences a active tokens
KV blocks used/free
time to first token
inter-token latency
prefill/decode tokens per second
batch sizes a scheduler preemptions
GPU memory/utilization/power
timeouts, OOM, restarts
model/adapter/cache generation
validated outcome
```

Metrics sa segmentujú podľa model, adapter, prompt length, output length, tenant/risk route a hardware pool.

## 31. Capacity planning

Safe capacity je maximum offered load, pri ktorom všetky required SLO a reliability gates ostávajú splnené s rezervou.

```text
benchmark saturation point
− failure/headroom reserve
− workload forecast uncertainty
= deployable capacity
```

Headroom pokrýva traffic burst, longer-than-observed outputs, replica loss a rollout overlap. Peak tokens/s pri nulovej rezerve nie je deployable capacity.

## 32. Failure hypotheses

Pri latency regressione sa skúma queue, prompt/output mix, prefill/decode balance, batch/token limits, cache hit rate, adapter churn, communication, thermal throttling a tool dependencies.

Pri OOM sa odlíši weight load, KV growth, transient allocation, fragmentation, prefix/adapter cache, runtime leak a replica config drift. Pri throughput poklese sa kontrolujú kernel fallback, smaller effective batches, arrival starvation a network/interconnect.

## 33. Containment

Containment môže znížiť max context/output, max batched tokens alebo concurrency, vypnúť problematický cache/adapter path, presunúť long-context workload do oddeleného poolu alebo aktivovať explicitný overload response.

Config change sa pinuje ako nová serving generation. OOM loop sa nerieši nekonečným process restartom bez admission zmeny.

## 34. Recovery

Recovery identifikuje first divergent resource alebo scheduler behavior, obnoví known-good serving release a replayne mixed workload. Potom nasleduje bounded canary pri reálnom arrival profile.

Second-operation test zahŕňa iný prompt-length bucket, adapter a burst condition. Recovery acceptance potrebuje aj business journey, nie iba stabilný GPU process.

## 35. Acceptance

Pozitívna acceptance vyžaduje exact serving subject, explicitný memory model, token-aware admission, SLO-aware batching/scheduling, representative open-loop benchmark, cold aj steady-state test, failure/headroom reserve, model/adapter/cache isolation, operational telemetry a accepted-outcome väzbu.

Recovery acceptance vyžaduje identifikovaný bottleneck, known-good rollback, mixed workload replay, burst/failure test, canary a druhú odlišnú journey po obnovení.

Forbidden acceptance je peak tokens/s bez latency distribution, loader fit ako capacity proof, maximum batch size bez token budgetu, GPU utilization ako jediný autoscaling signal, continuous batching ako automatická SLO výhra alebo worker readiness pred model warm-upom.
