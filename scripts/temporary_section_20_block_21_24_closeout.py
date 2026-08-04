#!/usr/bin/env python3
"""Temporary closeout helper for Section 20 chapters 21-24."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs/20-llm-and-genai-engineering"


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# Targeted prose remediation from the first strict learning-depth closeout.
replace_exact(
    SECTION / "peft-adapters-lora.md",
    """## 24. Failure hypotheses

Pri regresii sa skúma:

- wrong base snapshot alebo tokenizer,
- target module mismatch,
- adapter config/weights mismatch,
- stale alebo biased training data,
- overfitting a hyperparameters,
- wrong chat template alebo loss mask,
- unintended adapter composition,
- merge alebo quantization error,
- replica s neaktuálnym adapterom,
- cache reuse naprieč incompatible adapter generation.

First-divergence analysis začína od composed release identity, nie od všeobecného tvrdenia „LoRA nefunguje“.
""",
    """## 24. Failure hypotheses

Pri regresii sa najprv rekonštruuje composed release, pretože rovnaký adapter digest môže mať odlišný effective behavior nad iným base snapshotom, tokenizerom, chat template alebo target-module mappingom. Shape-compatible load preto nevylučuje identity defect; read-back base a adapter digests, rendered token boundaries a matched modules určí, či sa chyba objavila ešte pred inference.

Ak identity sedí, ďalšia vetva skúma training subject. Stale alebo biased dáta, chybná loss mask, agresívny rank či learning rate a overfitting môžu zlepšiť training metric, ale zhoršiť policy conflicts, structured output alebo adjacent capabilities. Dataset lineage, split, checkpoint metrics a paired eval s base release rozlišujú training defect od application-layer problému.

Serving vetva následne overuje unintended adapter composition, nesprávny merge alebo quantization order, repliku s neaktuálnym adapterom a cache reuse naprieč incompatible adapter generations. First-divergence analysis teda nezačína všeobecným tvrdením „LoRA nefunguje“, ale porovnaním requested, loaded a exercised base/adapter generation a prvého requestu, pri ktorom sa ich behavior rozišiel.
""",
)

replace_exact(
    SECTION / "quantization-local-inference.md",
    """Quantized candidate sa porovnáva s pinned reference release na rovnakých cases:

```yaml
""",
    """Quantized candidate sa porovnáva s pinned reference release na rovnakých cases. Porovnanie musí zachovať rovnaký tokenizer, chat template, prompt/RAG release, decoding policy a output validator, inak sa quantization effect zmieša s inou zmenou application contractu. Segmentovaný verdict ukazuje, či memory alebo latency gain nebol kúpený regresiou na číslach, identifiers, dlhom kontexte, strict schema alebo tool arguments.

```yaml
""",
)

replace_exact(
    SECTION / "quantization-local-inference.md",
    """## 26. Failure hypotheses

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
""",
    """## 26. Failure hypotheses

Quality regresia sa najprv rozdelí na identity, transformation a execution hypotheses. Identity vetva overuje base revision, tokenizer, chat template a prípadný adapter/merge order; transformation vetva porovnáva quantization method, calibration generation, group/scaling parameters a modules ponechané vo vyššej precision. Tým sa odlíši artifact vytvorený z nesprávneho subjectu od korektného subjectu poškodeného príliš agresívnou approximation.

Execution vetva kontroluje, či runtime skutočne použil očakávané kernels a compute dtype alebo potichu prešiel na fallback, či context/truncation a sampling defaults zodpovedajú reference release a či artifact digest a loader provenance ostali dôveryhodné. Layer-error, deterministic probe a workload-segment replay lokalizujú prvý rozdiel skôr než tím zmení ďalší quantization parameter.

Pri latency alebo OOM probléme sa samostatne vyčísli weight memory, KV cache, activations, allocator fragmentation, CPU/GPU offload transfer, queue a thermal alebo power throttling. Tento rozklad zabraňuje nesprávnemu záveru, že ďalšie zníženie bit width vyrieši incident, ktorý v skutočnosti vzniká z dlhého contextu, unsupported kernelu alebo preťaženého scheduleru.
""",
)

replace_exact(
    SECTION / "gpu-memory-batching-serving-performance.md",
    """## 2. Exact serving subject

Performance result je platný iba pre konkrétny subject:

```yaml
""",
    """## 2. Exact serving subject

Performance result je platný iba pre konkrétny subject. Model a runtime určujú kernel a memory behavior, kým scheduler, token limits, adapter mix, cache policy a workload distribution určujú, aký work sa v rovnakom čase nachádza na zariadení. Benchmark bez týchto identities sa nedá porovnať s produkciou ani reprodukovať po upgrade.

```yaml
""",
)

replace_exact(
    SECTION / "gpu-memory-batching-serving-performance.md",
    """## 30. Observability

Serving telemetry zahŕňa:

```text
""",
    """## 30. Observability

Serving telemetry musí spojiť arrival, scheduler a accelerator evidence s konkrétnym modelovým a business requestom. Samotná GPU utilization nevysvetľuje, či worker produktívne dekóduje, čaká na communication, blokuje sa na KV capacity alebo iba spracúva requesty, ktoré neskôr zlyhajú validation. Stage timestamps a generation identities preto umožňujú nájsť prvú divergence medzi prijatím requestu, prefillom, decode, tool/validation pathom a accepted outcome.

Serving telemetry zahŕňa:

```text
""",
)

replace_exact(
    SECTION / "prompt-semantic-response-caching.md",
    """## 2. Tri odlišné cache contracts

```text
""",
    """## 2. Tri odlišné cache contracts

Cache vrstvy sa rozlišujú podľa toho, čo presne sa reuse-uje a ktorý computation alebo business contract sa tým preskakuje. Prefix cache zachováva iba modelový medzivýpočet, semantic cache robí approximate rozhodnutie o ekvivalencii requestov a response cache vracia už vytvorený application result. Čím viac vrstiev sa preskočí, tým silnejší musí byť key, authorization, freshness a validation gate.

```text
""",
)

replace_exact(
    SECTION / "prompt-semantic-response-caching.md",
    """## 3. Exact cache subject

Cache entry manifest obsahuje:

```yaml
""",
    """## 3. Exact cache subject

Cache entry manifest identifikuje nielen uložené bytes, ale aj podmienky, za ktorých je ich reuse semanticky a bezpečnostne platný. Model, adapter, prompt, tools, corpus, locale a authorization scope patria do subjectu, pretože zmena ktorejkoľvek z týchto vrstiev môže pri rovnakom user texte vytvoriť iný správny výsledok. Entry age a TTL dopĺňajú generation identity, ale nenahrádzajú ju.

Cache entry manifest obsahuje:

```yaml
""",
)

readme = SECTION / "README.md"
text = readme.read_text(encoding="utf-8")
active_anchor = "20. [Fine-tuning, instruction tuning a preference tuning](fine-tuning-instruction-preference-tuning.md)\n"
active_addition = active_anchor + (
    "21. [PEFT, adapters a LoRA](peft-adapters-lora.md)\n"
    "22. [Quantization a local inference](quantization-local-inference.md)\n"
    "23. [GPU memory, batching a serving performance](gpu-memory-batching-serving-performance.md)\n"
    "24. [Prompt caching, semantic caching a response caching](prompt-semantic-response-caching.md)\n"
)
if active_anchor not in text:
    raise SystemExit("Section 20 active-list anchor not found")
text = text.replace(active_anchor, active_addition, 1)
for planned in (
    "21. PEFT, adapters a LoRA\n",
    "22. Quantization a local inference\n",
    "23. GPU memory, batching a serving performance\n",
    "24. Prompt caching, semantic caching a response caching\n",
):
    if planned not in text:
        raise SystemExit(f"Planned README entry not found: {planned.strip()}")
    text = text.replace(planned, "", 1)
status_marker = "## Stav\n\n"
if status_marker not in text:
    raise SystemExit("Section 20 status marker not found")
status = (
    "Aktuálny authoritative stav sekcie je **24/37 · In progress**. Šiesty authoritative blok aktivuje kapitoly 21–24 a incident `GENAI-SUPPORT-06`. "
    "PEFT kapitola oddeľuje base model, tokenizer/chat template, adapter config/weights, target modules, training data a composed serving release; vysvetľuje LoRA low-rank delta, QLoRA boundary, multi-adapter routing, merge/hot-swap, tenant isolation a behavior compatibility. "
    "Quantization kapitola modeluje weight/activation/compute/KV precision, PTQ/calibration, outliers, artifact/runtime/kernel/hardware identity, local serving a supply-chain/privacy boundary a oddeľuje memory fit od workload parity. "
    "Serving-performance kapitola rozkladá weights, KV cache, activations, paging, prefill/decode, static a continuous batching, admission/backpressure, fairness, parallelism, TTFT/ITL/end-to-end latency, open-loop capacity, autoscaling a OOM recovery. "
    "Caching kapitola striktne oddeľuje prefix/KV compute reuse, approximate semantic result reuse a exact response reuse a vyžaduje model/adapter/prompt/corpus/security-scoped keys, authorization pred lookupom, freshness/invalidation, atomic publish, privacy, false-hit telemetry a forbidden-hit tests. "
    "Kapitoly 21–24 sú pripravené na repository closeout; reálny adapter training, quantized export/inference, GPU load test, provider/self-hosted prompt cache, semantic/response cache traffic a business outcome neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 25–28: LLM gateways/routing/fallback/rate limiting, Prompt Registry, LLM evaluation datasets/graders a human evaluation/expert feedback.\n"
)
text = text.split(status_marker, 1)[0] + status_marker + status
readme.write_text(text, encoding="utf-8")

roadmap = ROOT / "ROADMAP.md"
for title, target in (
    ("PEFT, adapters a LoRA", "peft-adapters-lora.md"),
    ("Quantization a local inference", "quantization-local-inference.md"),
    ("GPU memory, batching a serving performance", "gpu-memory-batching-serving-performance.md"),
    ("Prompt caching, semantic caching a response caching", "prompt-semantic-response-caching.md"),
):
    replace_exact(
        roadmap,
        f"- [ ] {title}",
        f"- [x] [{title}](docs/20-llm-and-genai-engineering/{target})",
    )

ledger = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
replacement = (
    "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering | 24/37 authoritative drafting | In progress | 2026-08-04 | "
    "Šiesty authoritative blok aktivuje kapitoly 21–24 a incident `GENAI-SUPPORT-06`. PEFT kapitola pinne base weights, tokenizer/chat template a LoRA/adapter artifact, vysvetľuje low-rank update, target modules, QLoRA boundary, composition, merge/hot-swap, multi-tenant isolation a composed-release read-back. Quantization kapitola rozlišuje weight, activation, compute a KV precision; PTQ/calibration, outliers, formats, runtime/kernels/hardware, local security a workload parity. Serving kapitola modeluje weight/KV/activation memory, paged allocation, prefill/decode, static/continuous batching, admission/backpressure/fairness, parallelism, TTFT/ITL/end-to-end SLO, open-loop capacity, autoscaling a OOM recovery. Caching kapitola oddeľuje prompt/prefix compute reuse, approximate semantic reuse a exact response reuse; vyžaduje dependency- a authorization-scoped keys, tenant isolation, versioned invalidation, atomic complete-response publish, privacy, poisoning/stampede controls a false-hit/business outcome metrics. Reálny adapter training, quantized build/inference, GPU load/overload/failure test, cache traffic a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
found = False
for index, line in enumerate(lines):
    if line.startswith("| `20-llm-and-genai-engineering`"):
        lines[index] = replacement
        found = True
        break
if not found:
    raise SystemExit("Section 20 ledger row not found")
ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("Remediated and synchronized Section 20 chapters 21-24.")
