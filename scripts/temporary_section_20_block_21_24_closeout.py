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

print("Synchronized Section 20 chapters 21-24 README, ROADMAP and review ledger.")
