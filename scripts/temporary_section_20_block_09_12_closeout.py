#!/usr/bin/env python3
"""Temporary closeout helper for Section 20 chapters 9-12."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once_or_present(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{path.relative_to(ROOT)}: expected one replacement target, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


section_readme = ROOT / "docs/20-llm-and-genai-engineering/README.md"
text = section_readme.read_text(encoding="utf-8")
active_anchor = "8. [Prompt templates, variables a versioning](prompt-templates-variables-versioning.md)"
active_block = (
    active_anchor
    + "\n9. [Prompt decomposition a chain-of-thought boundaries](prompt-decomposition-chain-of-thought-boundaries.md)"
    + "\n10. [Structured Outputs a schema validation](structured-outputs-schema-validation.md)"
    + "\n11. [Function calling a tool calling](function-calling-tool-calling.md)"
    + "\n12. [Model selection a capability/cost trade-offs](model-selection-capability-cost-tradeoffs.md)"
)
if active_block not in text:
    if text.count(active_anchor) != 1:
        raise SystemExit("Section README: active chapter 8 anchor is not unique")
    text = text.replace(active_anchor, active_block, 1)

for planned in [
    "9. Prompt decomposition a chain-of-thought boundaries\n",
    "10. Structured Outputs a schema validation\n",
    "11. Function calling a tool calling\n",
    "12. Model selection a capability/cost trade-offs\n",
]:
    text = text.replace(planned, "", 1)

lines = text.splitlines()
status_prefix = "Aktuálny authoritative stav sekcie je **"
status_line = (
    "Aktuálny authoritative stav sekcie je **12/37 · In progress**. "
    "Tretí authoritative blok aktivuje kapitoly 9–12 a incident `GENAI-SUPPORT-03`. "
    "Prompt-decomposition kapitola oddeľuje explicitný task graph, typed intermediate artifacts, evidence-linked decision records a checkpoint recovery od raw chain-of-thought textu, ktorý nie je authority ani automaticky faithful explanation. "
    "Structured Outputs kapitola rozlišuje plain JSON, JSON mode, strict schema conformance, semantic/domain validation, authority read-back, refusal/incomplete handling, streaming a schema evolution. "
    "Function/tool-calling kapitola modeluje návrh tool callu, strict arguments, principal/tenant authorization, business preconditions, idempotency, unknown-outcome read-before-retry, bounded tool results a journey acceptance. "
    "Model-selection kapitola používa workload segmentation, capability matrix, task-specific evals, schema/tool compatibility, data governance, latency/capacity, routing/fallback a total cost per accepted outcome namiesto samotnej ceny tokenu. "
    "Kapitoly 9–12 sú pripravené na repository closeout; reálne reasoning executions, strict-schema provider parity, tool side effects, model canary a business outcomes neboli vykonané. Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 13–16: model version pinning, RAG architecture, chunking/document processing a vector stores/indexing."
)
matching = [index for index, line in enumerate(lines) if line.startswith(status_prefix)]
if len(matching) != 1:
    raise SystemExit(f"Section README: expected one status paragraph, found {len(matching)}")
lines[matching[0]] = status_line
section_readme.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

roadmap = ROOT / "ROADMAP.md"
for old, new in [
    (
        "- [ ] Prompt decomposition a chain-of-thought boundaries",
        "- [x] [Prompt decomposition a chain-of-thought boundaries](docs/20-llm-and-genai-engineering/prompt-decomposition-chain-of-thought-boundaries.md)",
    ),
    (
        "- [ ] Structured Outputs a schema validation",
        "- [x] [Structured Outputs a schema validation](docs/20-llm-and-genai-engineering/structured-outputs-schema-validation.md)",
    ),
    (
        "- [ ] Function calling a tool calling",
        "- [x] [Function calling a tool calling](docs/20-llm-and-genai-engineering/function-calling-tool-calling.md)",
    ),
    (
        "- [ ] Model selection a capability/cost trade-offs",
        "- [x] [Model selection a capability/cost trade-offs](docs/20-llm-and-genai-engineering/model-selection-capability-cost-tradeoffs.md)",
    ),
]:
    replace_once_or_present(roadmap, old, new)

review = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
review_lines = review.read_text(encoding="utf-8").splitlines()
prefix = "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering |"
new_line = (
    "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering | "
    "12/37 authoritative drafting | In progress | 2026-08-03 | "
    "Tretí authoritative blok aktivuje kapitoly 9–12 a incident `GENAI-SUPPORT-03`. "
    "Decomposition kapitola definuje task graph, typed intermediate artifacts, bounded reasoning exposure, evidence-linked rationale, checkpointing a first-divergence recovery bez použitia raw chain of thought ako authority. "
    "Structured Outputs kapitola oddeľuje JSON syntax, strict schema subset, semantic/domain validation, refusal/incomplete states, streaming commit, schema compatibility a security sinks. "
    "Function/tool-calling kapitola zavádza versioned tool catalog, strict arguments, server-side authorization, side-effect classes, idempotency, unknown-outcome read-back, result trust a tool-loop limits. "
    "Model-selection kapitola viaže workload segments, capability matrix, evals, schema/tool parity, governance, latency/capacity, routing/fallback a total cost per accepted outcome do controlled promotion modelu. "
    "Reálne reasoning execution, provider schema parity, tool side effects, model routing canary a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
indices = [index for index, line in enumerate(review_lines) if line.startswith(prefix)]
if len(indices) != 1:
    raise SystemExit(
        f"DOCUMENTATION-REVIEW-STATUS.md: expected one Section 20 row, found {len(indices)}"
    )
review_lines[indices[0]] = new_line
review.write_text("\n".join(review_lines) + "\n", encoding="utf-8", newline="\n")

print("Section 20 block 09-12 status files updated.")
