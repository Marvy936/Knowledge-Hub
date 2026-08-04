#!/usr/bin/env python3
"""Temporary closeout helper for Section 20 chapters 13-16."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs/20-llm-and-genai-engineering/README.md"
ROADMAP = ROOT / "ROADMAP.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_exact(
    SECTION,
    "12. [Model selection a capability/cost trade-offs](model-selection-capability-cost-tradeoffs.md)\n",
    "12. [Model selection a capability/cost trade-offs](model-selection-capability-cost-tradeoffs.md)\n"
    "13. [Model version pinning a compatibility](model-version-pinning-compatibility.md)\n"
    "14. [Retrieval-Augmented Generation architecture](retrieval-augmented-generation-architecture.md)\n"
    "15. [Chunking, metadata a document processing](chunking-metadata-document-processing.md)\n"
    "16. [Vector stores a indexing](vector-stores-indexing.md)\n",
)

for planned in (
    "13. Model version pinning a compatibility\n",
    "14. Retrieval-Augmented Generation architecture\n",
    "15. Chunking, metadata a document processing\n",
    "16. Vector stores a indexing\n",
):
    replace_exact(SECTION, planned, "")

old_state = (
    "Aktuálny authoritative stav sekcie je **12/37 · In progress**. Tretí authoritative blok aktivuje kapitoly 9–12 a incident `GENAI-SUPPORT-03`. "
    "Prompt-decomposition kapitola oddeľuje explicitný task graph, typed intermediate artifacts, evidence-linked decision records a checkpoint recovery od raw chain-of-thought textu, ktorý nie je authority ani automaticky faithful explanation. "
    "Structured Outputs kapitola rozlišuje plain JSON, JSON mode, strict schema conformance, semantic/domain validation, authority read-back, refusal/incomplete handling, streaming a schema evolution. "
    "Function/tool-calling kapitola modeluje návrh tool callu, strict arguments, principal/tenant authorization, business preconditions, idempotency, unknown-outcome read-before-retry, bounded tool results a journey acceptance. "
    "Model-selection kapitola používa workload segmentation, capability matrix, task-specific evals, schema/tool compatibility, data governance, latency/capacity, routing/fallback a total cost per accepted outcome namiesto samotnej ceny tokenu. "
    "Kapitoly 9–12 sú pripravené na repository closeout; reálne reasoning executions, strict-schema provider parity, tool side effects, model canary a business outcomes neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 13–16: model version pinning, RAG architecture, chunking/document processing a vector stores/indexing.\n"
)
new_state = (
    "Aktuálny authoritative stav sekcie je **16/37 · In progress**. Štvrtý authoritative blok aktivuje kapitoly 13–16 a incident `GENAI-SUPPORT-04`. "
    "Model-versioning kapitola oddeľuje family, mutable alias, pinned snapshot, regional deployment, provider API/SDK a celý dependent application release manifest; pinning znižuje jednu os variability, ale nie je determinism ani outcome guarantee. "
    "RAG architecture kapitola modeluje authoritative source, ingestion, corpus/index generation, query transformation, access-controlled retrieval, filtering/reranking, context assembly, grounded generation, citation support a no-answer/conflict states ako jeden evidence path. "
    "Chunking kapitola zavádza source snapshot, parser/OCR/normalizer/chunker generation, stable chunk identity, layout/table preservation, metadata provenance, ACL inheritance a update/delete lifecycle. "
    "Vector-store kapitola oddeľuje compatible embedding space, metric, exact baseline, ANN index a search parameters, metadata filtering, multi-tenant isolation, re-embedding migration, alias promotion a exact-versus-ANN recall. "
    "Kapitoly 13–16 prešli repository closeout; reálna provider migration, corpus ingestion, parser/OCR execution, index build, retrieval traffic a business outcome neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 17–20: retrieval/hybrid search/reranking, context assembly/citation grounding, RAG evaluation/diagnostics a fine-tuning/instruction/preference tuning.\n"
)
replace_exact(SECTION, old_state, new_state)

roadmap_replacements = {
    "- [ ] Model version pinning a compatibility": "- [x] [Model version pinning a compatibility](docs/20-llm-and-genai-engineering/model-version-pinning-compatibility.md)",
    "- [ ] Retrieval-Augmented Generation architecture": "- [x] [Retrieval-Augmented Generation architecture](docs/20-llm-and-genai-engineering/retrieval-augmented-generation-architecture.md)",
    "- [ ] Chunking, metadata a document processing": "- [x] [Chunking, metadata a document processing](docs/20-llm-and-genai-engineering/chunking-metadata-document-processing.md)",
    "- [ ] Vector stores a indexing": "- [x] [Vector stores a indexing](docs/20-llm-and-genai-engineering/vector-stores-indexing.md)",
}
for old, new in roadmap_replacements.items():
    replace_exact(ROADMAP, old, new)

old_row = "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering | 12/37 authoritative drafting | In progress | 2026-08-03 | Tretí authoritative blok aktivuje kapitoly 9–12 a incident `GENAI-SUPPORT-03`. Decomposition kapitola definuje task graph, typed intermediate artifacts, bounded reasoning exposure, evidence-linked rationale, checkpointing a first-divergence recovery bez použitia raw chain of thought ako authority. Structured Outputs kapitola oddeľuje JSON syntax, strict schema subset, semantic/domain validation, refusal/incomplete states, streaming commit, schema compatibility a security sinks. Function/tool-calling kapitola zavádza versioned tool catalog, strict arguments, server-side authorization, side-effect classes, idempotency, unknown-outcome read-back, result trust a tool-loop limits. Model-selection kapitola viaže workload segments, capability matrix, evals, schema/tool parity, governance, latency/capacity, routing/fallback a total cost per accepted outcome do controlled promotion modelu. Reálne reasoning execution, provider schema parity, tool side effects, model routing canary a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
new_row = "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering | 16/37 authoritative drafting | In progress | 2026-08-04 | Štvrtý authoritative blok aktivuje kapitoly 13–16 a incident `GENAI-SUPPORT-04`. Model-versioning kapitola definuje model family/alias/snapshot/deployment identity, provider API a SDK compatibility, dependent release manifest, behavioral eval, deprecation, migration a full-release rollback. RAG architecture kapitola zavádza versioned source/corpus/index/query/retrieval/context/generator subject, authority a access boundaries, dense/sparse/hybrid stages, conflict/no-answer states, claim-level citation support a stage-level diagnostics. Chunking kapitola pokrýva immutable acquisition, layout parsing, OCR uncertainty, normalization, structure-aware a parent-child segmentation, stable chunk/source mapping, metadata provenance, ACL inheritance, updates a deletion. Vector-store kapitola oddeľuje compatible vector space, metric, exact baseline, ANN recall, HNSW/IVF/quantization trade-offs, filters, tenant isolation, build/mutation/re-embedding lifecycle a alias/replica generation. Reálna provider migration, ingestion, parser/OCR execution, embedding/index build, retrieval traffic, access-control exercise a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
replace_exact(LEDGER, old_row, new_row)

print("Section 20 block 13-16 closeout synchronization complete.")
