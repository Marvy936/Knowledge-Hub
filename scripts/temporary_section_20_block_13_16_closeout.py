#!/usr/bin/env python3
"""Temporary closeout helper for Section 20 chapters 13-16."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs/20-llm-and-genai-engineering/README.md"
ROADMAP = ROOT / "ROADMAP.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
MODEL_VERSION = ROOT / "docs/20-llm-and-genai-engineering/model-version-pinning-compatibility.md"
RAG = ROOT / "docs/20-llm-and-genai-engineering/retrieval-augmented-generation-architecture.md"
CHUNKING = ROOT / "docs/20-llm-and-genai-engineering/chunking-metadata-document-processing.md"
VECTOR = ROOT / "docs/20-llm-and-genai-engineering/vector-stores-indexing.md"


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_exact(
    MODEL_VERSION,
    "Aj pri rovnakom snapshot-e sa môžu meniť:\n\n"
    "- provider runtime, batching a numerical execution,\n"
    "- safety a abuse filters,\n"
    "- API serialization alebo SDK behavior,\n"
    "- prompt, examples a decoding parameters,\n"
    "- retrieval corpus, chunking a index,\n"
    "- tool implementation a authoritative data,\n"
    "- application postprocessing.\n\n"
    "Preto sa pinning používa ako súčasť release manifestu, nie ako samostatný acceptance dôkaz.\n",
    "Aj pri rovnakom snapshot-e môže provider meniť runtime scheduling, batching alebo numerical execution. Tieto zmeny môžu ovplyvniť latency a pri stochastickom decodingu aj konkrétny output, hoci modelová identity zostáva rovnaká. Safety a abuse filters môžu navyše rozhodnúť, či request prejde, bude odmietnutý alebo dostane odlišný response envelope.\n\n"
    "Application vrstva má vlastné nezávislé generácie. SDK alebo API serialization môžu zmeniť request shape; prompt, examples a decoding parameters menia behavior; retrieval corpus, chunking a index menia dostupné evidence; tool implementation a authoritative data menia side effect; postprocessing môže zmeniť alebo zahodiť správny model output. Rovnaký pinned model preto neznamená rovnaký end-to-end request subject.\n\n"
    "Pinning sa používa ako jedna položka release manifestu, nie ako samostatný acceptance dôkaz. Jeho úlohou je zmenšiť search space pri reprodukcii a migrácii, zatiaľ čo zvyšné závislosti musia mať vlastnú identity, compatibility a read-back.\n",
)
replace_exact(
    MODEL_VERSION,
    "## 5. Versioned release manifest\n\nModel sa propaguje spolu so závislosťami:\n",
    "## 5. Versioned release manifest\n\nModel sa propaguje spolu so závislosťami, pretože production behavior vzniká až z ich resolved kombinácie. Manifest vytvára immutable alebo časovo presnú boundary, ktorú možno použiť pri evale, canary, incidente aj rollbacku. Bez nej sa zmena modelu mieša so zmenou promptu, retrievalu alebo tool contractu a výsledok sa nedá korektne priradiť jednej príčine.\n\nManifest zároveň definuje promotion unit. Release sa nepovažuje za nasadený iba preto, že provider prijal model string; platforma musí vedieť prečítať späť, ktoré components boli pre request skutočne resolved.\n\nPríklad manifestu:\n",
)
replace_exact(
    RAG,
    "## 3. Exact RAG subject\n\nRequest trace potrebuje rozbaliteľný manifest:\n",
    "## 3. Exact RAG subject\n\nRAG request je composite subject. Rovnaká user otázka môže dostať iný evidence set po zmene parsera, embedding modelu, index generation, filters alebo rerankera, aj keď generator model a prompt zostanú rovnaké. Incident a eval preto musia vedieť rekonštruovať každú resolved generation, nie iba finálnu odpoveď.\n\nManifest slúži aj ako boundary pre cache, rollout a rollback. Ak dva requesty nemajú rovnaký corpus/index/retrieval/context subject, nemožno ich považovať za čistý model A/B test. Request trace preto potrebuje rozbaliteľný manifest:\n",
)
replace_exact(
    RAG,
    "## 18. Containment a recovery\n\nContainment môže vypnúť affected corpus alias, prepnúť na known-good index generation, obmedziť workload na read-only lookup alebo vynútiť escalation pri insufficient evidence.\n\nRecovery postup:\n",
    "## 18. Containment a recovery\n\nContainment znižuje business a security dopad skôr, než je potvrdený root cause. Môže vypnúť affected corpus alias, prepnúť na known-good index generation, obmedziť workload na read-only lookup alebo vynútiť escalation pri insufficient evidence. Voľba containmentu sa viaže na prvý podozrivý stage; plošné vypnutie generatora nepomôže, ak unauthorized dokument už uniká v retrieval výsledkoch.\n\nRecovery obnovuje celý evidence path, nie iba jeden component. Known-good index sa najprv read-backne, potom sa replayom overí source authority, ingestion, exact a ANN retrieval, filters, reranking, context a generation. Až po bounded canary a druhej odlišnej query sa potvrdzuje, že oprava nie je iba sample-specific.\n\nRecovery postup:\n",
)
replace_exact(
    CHUNKING,
    "## 1. Processing subject a generation\n\nKaždý derived document a chunk musí byť spätne dohľadateľný:\n",
    "## 1. Processing subject a generation\n\nDocument-processing output je derived artifact, ktorého význam závisí od source snapshotu a každej transformačnej generácie. Rovnaký source file môže po zmene layout parsera alebo chunkera vytvoriť odlišné boundaries, metadata a embeddings, preto sa výsledok nesmie identifikovať iba source názvom.\n\nSpätná dohľadateľnosť umožňuje vysvetliť, prečo sa konkrétny chunk dostal do indexu, znovu ho vytvoriť a odstrániť všetky jeho derivácie pri update alebo revoke. Každý derived document a chunk preto musí niesť processing subject:\n",
)
replace_exact(
    CHUNKING,
    "## 7. Chunking strategies\n\n### Fixed-size chunking\n",
    "## 7. Chunking strategies\n\nChunking strategy určuje retrieval unit a tým aj to, aký evidence fragment môže retriever nájsť a generator interpretovať. Výber sa robí podľa document structure, typických queries, požadovanej citation granularity a context budgetu; samotný priemerný počet tokenov nie je dostatočný návrhový parameter.\n\nStratégie sa často kombinujú. Pipeline môže najprv zachovať sections a tables, potom použiť tokenový limit vnútri veľkého semantic blocku a nakoniec vytvoriť parent-child mapping. Každá kombinácia je versioned policy a testuje sa na retrieval cases, pretože vizuálne pekný chunk nemusí zachovať rozhodujúcu podmienku.\n\n### Fixed-size chunking\n",
)
replace_exact(
    VECTOR,
    "## 21. Containment a recovery\n\nContainment môže prepnúť na exact search pre kritický menší corpus, zvýšiť ANN search breadth, vrátiť known-good index alias alebo vypnúť affected tenant/language route.\n\nRecovery:\n",
    "## 21. Containment a recovery\n\nContainment sa vyberá podľa toho, či je podozrivý embedding space, ANN structure, filtering alebo alias/replica generation. Pre kritický menší corpus možno dočasne prepnúť na exact search, pri izolovanom ANN recall probléme zvýšiť search breadth, pri chybnej generácii vrátiť known-good alias a pri možnom cross-tenant úniku vypnúť affected route úplne.\n\nRecovery musí porovnať rovnakú query, vectors, metric a filters cez exact aj approximate path. Rebuild sa nepovýši iba po úspešnom create-index jobe; musí prejsť recall, latency, ACL, deletion a replica-generation gates a následne second-query testom.\n\nRecovery:\n",
)

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
