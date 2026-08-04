#!/usr/bin/env python3
"""Temporary closeout helper for Section 20 chapters 17-20."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs/20-llm-and-genai-engineering/README.md"
ROADMAP = ROOT / "ROADMAP.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old[:160]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_exact(
    SECTION,
    "16. [Vector stores a indexing](vector-stores-indexing.md)\n",
    "16. [Vector stores a indexing](vector-stores-indexing.md)\n"
    "17. [Retrieval, hybrid search a reranking](retrieval-hybrid-search-reranking.md)\n"
    "18. [Context assembly a citation grounding](context-assembly-citation-grounding.md)\n"
    "19. [RAG evaluation a retrieval diagnostics](rag-evaluation-retrieval-diagnostics.md)\n"
    "20. [Fine-tuning, instruction tuning a preference tuning](fine-tuning-instruction-preference-tuning.md)\n",
)

for planned in (
    "17. Retrieval, hybrid search a reranking\n",
    "18. Context assembly a citation grounding\n",
    "19. RAG evaluation a retrieval diagnostics\n",
    "20. Fine-tuning, instruction tuning a preference tuning\n",
):
    replace_exact(SECTION, planned, "")

old_state = (
    "Aktuálny authoritative stav sekcie je **16/37 · In progress**. Štvrtý authoritative blok aktivuje kapitoly 13–16 a incident `GENAI-SUPPORT-04`. "
    "Model-versioning kapitola oddeľuje family, mutable alias, pinned snapshot, regional deployment, provider API/SDK a celý dependent application release manifest; pinning znižuje jednu os variability, ale nie je determinism ani outcome guarantee. "
    "RAG architecture kapitola modeluje authoritative source, ingestion, corpus/index generation, query transformation, access-controlled retrieval, filtering/reranking, context assembly, grounded generation, citation support a no-answer/conflict states ako jeden evidence path. "
    "Chunking kapitola zavádza source snapshot, parser/OCR/normalizer/chunker generation, stable chunk identity, layout/table preservation, metadata provenance, ACL inheritance a update/delete lifecycle. "
    "Vector-store kapitola oddeľuje compatible embedding space, metric, exact baseline, ANN index a search parameters, metadata filtering, multi-tenant isolation, re-embedding migration, alias promotion a exact-versus-ANN recall. "
    "Kapitoly 13–16 prešli repository closeout; reálna provider migration, corpus ingestion, parser/OCR execution, index build, retrieval traffic a business outcome neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 17–20: retrieval/hybrid search/reranking, context assembly/citation grounding, RAG evaluation/diagnostics a fine-tuning/instruction/preference tuning.\n"
)
new_state = (
    "Aktuálny authoritative stav sekcie je **20/37 · In progress**. Piaty authoritative blok aktivuje kapitoly 17–20 a incident `GENAI-SUPPORT-05`. "
    "Retrieval kapitola oddeľuje query planning, sparse/dense/structured candidate generation, authorization filtering, rank fusion, deduplication, cross-encoder reranking, evidence coverage a sufficient-evidence verdict. "
    "Context-assembly kapitola modeluje tokenizer-aware budget, authority a facet coverage, version-aware deduplication, semantic-safe truncation, conflict resolution, stable citation labels, claim-level support a provisional-versus-committed streaming boundary. "
    "RAG-evaluation kapitola zavádza versioned case a judgment subject, retrieval/context/answer/citation/security metrics, leakage-safe splits, calibrated model graders, human adjudication, ablations, stage traces a offline-to-online promotion evidence. "
    "Fine-tuning kapitola oddeľuje SFT a instruction tuning, preference data, RLHF, DPO a grader-driven optimization od retrieval, authorization a mutable knowledge; vyžaduje governed data, reproducible lineage, adjacent capability evals, privacy gates a full-release rollout/rollback. "
    "Kapitoly 17–20 prešli repository closeout; reálny retrieval/reranking traffic, context generation, expert eval, training job, deployment canary a business outcome neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 21–24: PEFT/adapters/LoRA, quantization/local inference, GPU memory/batching/serving performance a prompt/semantic/response caching.\n"
)
replace_exact(SECTION, old_state, new_state)

roadmap_replacements = {
    "- [ ] Retrieval, hybrid search a reranking": "- [x] [Retrieval, hybrid search a reranking](docs/20-llm-and-genai-engineering/retrieval-hybrid-search-reranking.md)",
    "- [ ] Context assembly a citation grounding": "- [x] [Context assembly a citation grounding](docs/20-llm-and-genai-engineering/context-assembly-citation-grounding.md)",
    "- [ ] RAG evaluation a retrieval diagnostics": "- [x] [RAG evaluation a retrieval diagnostics](docs/20-llm-and-genai-engineering/rag-evaluation-retrieval-diagnostics.md)",
    "- [ ] Fine-tuning, instruction tuning a preference tuning": "- [x] [Fine-tuning, instruction tuning a preference tuning](docs/20-llm-and-genai-engineering/fine-tuning-instruction-preference-tuning.md)",
}
for old, new in roadmap_replacements.items():
    replace_exact(ROADMAP, old, new)

old_row = "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering | 16/37 authoritative drafting | In progress | 2026-08-04 | Štvrtý authoritative blok aktivuje kapitoly 13–16 a incident `GENAI-SUPPORT-04`. Model-versioning kapitola definuje model family/alias/snapshot/deployment identity, provider API a SDK compatibility, dependent release manifest, behavioral eval, deprecation, migration a full-release rollback. RAG architecture kapitola zavádza versioned source/corpus/index/query/retrieval/context/generator subject, authority a access boundaries, dense/sparse/hybrid stages, conflict/no-answer states, claim-level citation support a stage-level diagnostics. Chunking kapitola pokrýva immutable acquisition, layout parsing, OCR uncertainty, normalization, structure-aware a parent-child segmentation, stable chunk/source mapping, metadata provenance, ACL inheritance, updates a deletion. Vector-store kapitola oddeľuje compatible vector space, metric, exact baseline, ANN recall, HNSW/IVF/quantization trade-offs, filters, tenant isolation, build/mutation/re-embedding lifecycle a alias/replica generation. Reálna provider migration, ingestion, parser/OCR execution, embedding/index build, retrieval traffic, access-control exercise a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
new_row = "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering | 20/37 authoritative drafting | In progress | 2026-08-04 | Piaty authoritative blok aktivuje kapitoly 17–20 a incident `GENAI-SUPPORT-05`. Retrieval kapitola definuje exact query/retriever/fusion/reranker subject, sparse/dense/structured branches, mandatory filters, RRF a calibrated score semantics, hard negatives, coverage, thresholds, stage traces a first-divergence recovery. Context-assembly kapitola zavádza evidence candidate contract, trust boundary, tokenizer budget, facet-aware packing, version-aware dedup, parent-child expansion, semantic truncation, compression provenance, conflict resolution, citation labels, claim-level grounding a streaming commit. RAG-evaluation kapitola rozkladá versioned dataset/judgments/splits a retrieval, context, answer, faithfulness, citation, no-answer, security, judge-calibration, human, ablation, online a statistical verdicty. Fine-tuning kapitola oddeľuje behavior adaptation od current knowledge a deterministic authority, pokrýva SFT/instruction tuning, preferences, RLHF, DPO, grader-driven training, data governance, preprocessing, PEFT boundary, leakage, memorization, lineage a controlled rollout. Reálny retrieval/reranking traffic, context generation, expert eval, fine-tuning job, deployment canary a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
replace_exact(LEDGER, old_row, new_row)

print("Section 20 block 17-20 closeout synchronization complete.")
