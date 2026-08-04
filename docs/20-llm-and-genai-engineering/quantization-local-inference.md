# Quantization a local inference

Quantization reprezentuje model weights, activations alebo KV cache v nižšej precision, aby sa znížila memory, storage, bandwidth alebo compute cost. Local inference znamená, že organizácia prevádzkuje model vo vlastnom runtime alebo infra boundary namiesto vzdialeného managed endpointu. Tieto dve rozhodnutia sa často kombinujú, ale nie sú totožné: model môže byť quantized v cloude a local model môže bežať v BF16 alebo FP16.

V incidente `GENAI-SUPPORT-06` tím exportoval support model do 4-bit formátu, pretože sa zmestil na dostupnú GPU. Loader vypísal úspešné načítanie a jednoduchý prompt vyzeral správne. Produkčný workload však používal dlhý context, strict JSON a tool arguments. Quantized candidate mal vyššiu invalid-schema rate, častejšie zamieňal policy identifiers a pri určitých layer outliers vytváral nestabilné výsledky. Navyše runtime načítal community artifact bez overenia base revision a chat template. Root cause bolo zamieňanie memory fit a smoke outputu za behavior, security a operational parity.

## 1. Business outcome a proof boundary

Quantization je optimalizácia reprezentácie. Jej cieľom môže byť:

```text
model sa zmestí do device memory
nižšia latency alebo vyšší throughput
nižší storage a transfer cost
lokálna alebo edge prevádzka
```

Žiadny z týchto cieľov automaticky nepreukazuje zachovanú quality. Produkčný verdict vyžaduje exact quantized artifact, runtime/hardware subject, workload eval a outcome telemetry.

## 2. Exact quantization subject

„4-bit model“ je neúplná identita. Manifest musí zachytiť:

```yaml
quantized_release:
  release_id: support-local-int4-v6
  base_model:
    repository: internal/support-7b
    revision: 6f1a9d2
    weights_digest: sha256:1c90...
    tokenizer_digest: sha256:ab72...
    chat_template_digest: sha256:7ee4...
  quantization:
    method: gptq
    weight_bits: 4
    activation_dtype: bf16
    group_size: 128
    symmetric: true
    calibration_dataset: support-calibration-2026-08-04
    excluded_modules: [lm_head]
  artifact_digest: sha256:fe81...
  runtime: local-engine-v14
  kernel_backend: cuda-13.0
  hardware: rtx-class-8gb
  eval_suite: support-local-parity-v9
```

Format name, bit width a file extension samy osebe neurčujú quantization semantics.

## 3. Precision vrstvy

Model execution používa viac precision vrstiev:

```text
weight storage precision
activation/compute precision
accumulation precision
KV cache precision
optimizer state precision pri trainingu
```

INT4 weights môžu byť počas matmul dequantized do FP16/BF16 compute. Preto „4-bit inference“ neznamená, že celý computation graph pracuje v štyroch bitoch. Memory a quality sa analyzujú per component.

## 4. Static a dynamic quantization

Static quantization používa vopred vypočítané scales alebo calibration evidence. Dynamic quantization môže určovať niektoré scales počas runtime. Weight-only quantization komprimuje weights, kým activation quantization zasahuje aj intermediate values.

Každá kombinácia má iné kernel requirements a quality trade-offs. Platforma nepoužíva všeobecný claim „INT8 je presnejší než INT4“ bez konkrétneho method, modelu a workloadu.

## 5. Post-training quantization

Post-training quantization, PTQ, transformuje už vytrénovaný model bez plného retrainingu. Methods ako GPTQ alebo AWQ používajú calibration alebo activation-aware heuristics na minimalizáciu quantization error.

```text
pinned full-precision base
→ representative calibration data
→ quantizer configuration
→ layer/block transformation
→ quantized artifact
→ parity eval
```

Calibration dataset nemusí byť training dataset, ale musí reprezentovať activation distributions produkčného workloadu. Generický text môže byť slabý calibration subject pre code, multilingual alebo tool-heavy workload.

## 6. Quantization-aware training a QLoRA

Quantization-aware training simuluje alebo zahŕňa quantization effects počas trainingu. QLoRA je iný pattern: frozen 4-bit base sa používa pri PEFT trainingu a trainable sú LoRA parameters.

```text
QLoRA training artifact
≠ automaticky final merged INT4 serving artifact
```

Po merge alebo exporte môže vzniknúť nová quantization error. Finálny serving artifact sa preto znovu evaluačne validuje.

## 7. Scaling, zero point a group size

Uniform quantization približne mapuje real values na discrete levels pomocou scale a prípadne zero point. Per-tensor quantization používa jednu konfiguráciu pre celý tensor, per-channel alebo grouped quantization jemnejšie prispôsobuje rozsahy.

Menší group size môže zlepšiť fidelity, ale zvýši metadata a kernel overhead. Symmetric a asymmetric quantization majú odlišný mapping. Tieto parametre musia byť v manifeste a nie iba implicitne ukryté v exporter verzii.

## 8. Outliers a citlivé moduly

Niektoré activation alebo weight values sú outliers a nízka precision ich môže poškodiť disproporčne. Hybrid methods ponechávajú časť computation vo vyššej precision alebo vynechávajú citlivé modules.

```yaml
quantization_policy:
  default_weights: int4
  compute_dtype: bf16
  keep_high_precision:
    - lm_head
    - router_gate
  outlier_threshold: 6.0
```

Threshold a excluded modules sa určujú meraním. Copy-paste config z iného modelu nie je authoritative optimization.

## 9. Artifact formats

Lokálny ecosystem používa rôzne formats a runtimes. Format môže ukladať quantized tensors, tokenizer, metadata a architecture config, no feature support sa líši.

```text
artifact format
→ čo je uložené

runtime loader
→ čo vie interpretovať

kernel backend
→ čo vie efektívne vykonať
```

Súbor, ktorý loader otvorí, nemusí podporovať model architecture, multimodal components, adapters, tool template alebo rope scaling správne. Compatibility sa testuje, nepredpokladá.

## 10. Local inference architecture

Local serving path typicky obsahuje:

```text
model registry
→ artifact download/verification
→ tokenizer/template load
→ runtime engine
→ accelerator kernels
→ scheduler a memory manager
→ API compatibility layer
→ application validators
```

„Lokálne“ neznamená automaticky offline, private alebo secure. Runtime môže sťahovať artifacts, telemetry, remote code alebo external tokenizers. Network egress, dependencies a model license sa explicitne kontrolujú.

## 11. Hardware fit

Hrubý weight-memory odhad:

```text
weight bytes ≈ parameter_count × bits_per_weight / 8
```

Tento odhad ignoruje quantization metadata, unquantized layers, runtime buffers, KV cache, activations a allocator fragmentation. Model s vypočítanými 3,5 GB weights nemusí bezpečne fungovať na 4 GB device.

Device fit sa overuje na exact context, batch a output profile. Loader success iba preukazuje initial allocation.

## 12. CPU, GPU a heterogeneous offload

Local runtime môže používať CPU-only inference, GPU acceleration alebo rozdeliť layers medzi CPU a GPU. Offload umožní načítať väčší model, ale PCIe alebo memory transfer môže zhoršiť latency.

```yaml
placement:
  gpu_layers: 28
  cpu_layers: 4
  pinned_host_memory: true
  tensor_parallel: 1
```

`device_map="auto"` je heuristic, nie production capacity plan. Effective placement sa read-backne a benchmarkuje.

## 13. Example: explicit 4-bit load

Príklad ukazuje, ktoré parameters musia byť explicitné:

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

model_id = "internal/support-7b"
revision = "6f1a9d2"

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)

tokenizer = AutoTokenizer.from_pretrained(
    model_id,
    revision=revision,
    trust_remote_code=False,
)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    revision=revision,
    quantization_config=quant_config,
    device_map={"": 0},
    trust_remote_code=False,
)

print(model.get_memory_footprint())
```

Tento kód je load test, nie quality acceptance. Production manifest navyše pinne package/container, CUDA/kernel a artifact digests.

## 14. Tokenizer a template parity

Lokálny model môže byť distribuovaný bez correct chat template alebo s odlišnou tokenizer revision. Raw text concatenation potom produkuje iný input než referenčný runtime.

Parity test porovná:

```text
same conversation object
→ rendered template
→ token IDs
→ special-token boundaries
→ truncation
```

Ak sa local a reference serialization líšia, output comparison nemeria iba quantization.

## 15. Determinism a kernels

Greedy decoding znižuje sampling variability, ale GPU kernels, fused operations, reduced precision a parallel execution môžu stále meniť numerické results. Malá logit zmena môže zmeniť token a následne celý autoregressive suffix.

Preto parity nie je definovaná iba token-identical outputom. Používa task correctness, schema adherence, safety, retrieval/tool behavior a distribution metrics. Token equality môže byť užitočný diagnostic na malom deterministic sete.

## 16. Workload parity eval

Quantized candidate sa porovnáva s pinned reference release na rovnakých cases:

```yaml
segments:
  - short_classification
  - long_policy_context
  - multilingual
  - strict_json
  - tool_arguments
  - ambiguous_escalation
metrics:
  - accepted_case_rate
  - exact_field_accuracy
  - schema_failure_rate
  - citation_support_rate
  - unsafe_action_rate
  - p50_p95_latency
  - peak_memory
  - energy_or_compute_cost
```

Average benchmark score bez kritických segments môže zakryť, že INT4 zlyháva práve na policy identifiers.

## 17. Perplexity a application quality

Perplexity alebo reconstruction error môže diagnostikovať globálnu degradation, ale nie je application acceptance. Malý average loss difference môže skrývať veľký error na rare tokens, numbers, code alebo structured fields.

Application eval je rozhodujúci. Perplexity a layer error slúžia na lokalizáciu quantization damage a výber excluded modules.

## 18. Context a KV cache

Weight quantization rieši iba časť memory. KV cache rastie s batchom a sequence length a môže dominovať pri dlhom context serving.

```text
quantized weights fit
+ long context KV cache does not fit
= runtime OOM napriek úspešnému loadu
```

Niektoré runtimes podporujú KV-cache quantization, ale to je ďalšia approximation layer a potrebuje samostatný quality/latency eval.

## 19. Throughput a kernel support

Nižší bit width nemusí byť rýchlejší, ak hardware nemá vhodné kernels, dequantization overhead je vysoký alebo workload je memory/CPU-bound iným spôsobom.

Benchmarkuje sa exact runtime, kernel, batch a sequence distribution. Notebook claim z iného GPU nie je capacity evidence.

```text
prefill tokens/s
decode tokens/s
time to first token
inter-token latency
requests/s pri SLO
```

Peak throughput bez p95/p99 latency a queue behavior je neúplný.

## 20. Model license a use rights

Local artifact môže mať license constraints na commercial use, redistribution, derivative models alebo specific scale. Adapter a merged/quantized derivative môžu podliehať base license.

Registry preto eviduje license, source, approved use a redistribution boundary. Verejne stiahnuteľný model nie je automaticky open-source ani produkčne použiteľný.

## 21. Supply-chain a remote code

Community model repositories môžu obsahovať custom Python code, tokenizer files a conversion scripts. Production pipeline nepoužíva mutable branch ani neoverený executable loader.

```text
approved source
→ immutable revision
→ malware/license scan
→ digest verification
→ offline conversion sandbox
→ signed internal artifact
```

`trust_remote_code=True` môže byť nevyhnutné pre niektoré architectures, ale potom ide o explicitne reviewnutý code artifact, nie implicitný download pri štarte servera.

## 22. Data privacy a local boundary

Local inference môže znížiť external data exposure, ale stále potrebuje access controls, encryption, log minimization, memory isolation a secure deletion. GPU memory, swap, crash dumps a prompt caches môžu obsahovať sensitive data.

Local endpoint na `0.0.0.0` bez authentication je security regression, nie private deployment. Network, process a tenant boundaries sa testujú.

## 23. Release build a reproducibility

Quantized artifact sa vytvára v controlled build:

```text
pinned base bytes
→ pinned quantizer/container
→ calibration dataset generation
→ quantization config
→ deterministic alebo evidence-recorded build
→ artifact digest
→ compatibility/eval report
```

Artifact sa nepregeneruje pod rovnakým tagom. Ak exporter alebo kernels zmenia bytes, vzniká nový release.

## 24. Deployment a rollout

Deployment používa warm-up na reálnych sequence profiles, memory headroom a health checks, ktoré overujú viac než TCP readiness.

```text
artifact loaded
→ tokenizer/template verified
→ representative warm-up
→ peak-memory check
→ contract smoke cases
→ bounded canary
→ delayed outcome
```

Canary route sa porovnáva s reference modelom a má okamžitý rollback. Write tools ostávajú pod rovnakou authorization vrstvou bez ohľadu na local/cloud model.

## 25. Observability

Runtime trace obsahuje base a quantized artifact digest, method/config, runtime/container, kernel backend, device model, placement, context/batch, prompt/RAG/adapter release, latency, memory, validation a outcome.

Node-level metrics zahŕňajú GPU memory allocated/reserved, utilization, power, temperature, OOM/restart, queue a cache pressure. High utilization sama osebe neznamená efektívny serving.

## 26. Failure hypotheses

Pri quality regresii sa skúma:

- wrong base revision/tokenizer/template,
- quantization method a calibration mismatch,
- citlivé layers quantized príliš agresívne,
- unsupported alebo fallback kernels,
- adapter merge order,
- context/truncation difference,
- runtime sampling defaults,
- corrupt alebo untrusted artifact.

Pri latency alebo OOM probléme sa oddelí weight memory, KV cache, activations, fragmentation, offload transfer, queue a thermal/power throttling.

## 27. Containment

Containment odpojí quantized route a vráti known-good full-precision alebo menej agresívny release. Zachová exact artifact, runtime logs, hardware subject a failing cases.

Pri supply-chain incidente sa zablokuje artifact digest, revokuje registry release a vyšetrí build host aj runtime. Pri privacy incidente sa izoluje node a spracujú memory/log artifacts podľa incident policy.

## 28. Recovery

Recovery môže zmeniť bit width, group size, calibration set, excluded modules, runtime/kernel alebo hardware placement. Každá zmena vytvára nový immutable artifact.

Po offline parity teste nasleduje representative warm-up, memory stress, canary a second-operation test na odlišnom sequence/tool/schema profile. Recovery sa neuzavrie iba tým, že model znovu „odpovedá“.

## 29. Acceptance

Pozitívna acceptance vyžaduje pinned base/tokenizer/template, explicitnú quantization configuration, governed calibration, signed immutable artifact, runtime/hardware compatibility, workload parity a adjacent eval, memory/latency test pri reálnom profile, secure local boundary, controlled rollout a outcome observability.

Recovery acceptance vyžaduje identifikovanú degradation vrstvu, known-good rollback, nový artifact digest, replay, stress/canary a druhý odlišný production journey.

Forbidden acceptance je „zmestí sa do VRAM“, loader success, jeden plynulý prompt, generic benchmark bez workload segments, bit width bez method/config identity, mutable community artifact, `trust_remote_code` bez review alebo tvrdenie, že local inference automaticky garantuje privacy.
