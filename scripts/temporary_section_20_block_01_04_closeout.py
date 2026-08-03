#!/usr/bin/env python3
"""Temporary closeout helper for Section 20 chapters 1-4."""

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


section = ROOT / "docs/20-llm-and-genai-engineering"
readme = section / "README.md"
text = readme.read_text(encoding="utf-8")
planned_header = "## Plánované authoritative poradie"
active_block = """## Authoritative poradie — aktívne kapitoly

1. [Generative AI, foundation model a large language model](generative-ai-foundation-model-llm.md)
2. [Transformer architecture na praktickej úrovni](transformer-architecture-practical.md)
3. [Tokens, tokenization a context window](tokens-tokenization-context-window.md)
4. [Embeddings a semantic similarity](embeddings-semantic-similarity.md)

## Plánované authoritative poradie"""
if active_block not in text:
    if text.count(planned_header) != 1:
        raise SystemExit("Section 20 README: planned inventory header is not unique")
    text = text.replace(planned_header, active_block, 1)

for planned in (
    "1. Generative AI, foundation model a large language model\n",
    "2. Transformer architecture na praktickej úrovni\n",
    "3. Tokens, tokenization a context window\n",
    "4. Embeddings a semantic similarity\n",
):
    if planned in text:
        text = text.replace(planned, "", 1)

lines = text.splitlines()
status_prefix = "Aktuálny authoritative stav sekcie je **"
status_line = (
    "Aktuálny authoritative stav sekcie je **4/37 · In progress**. Prvý authoritative blok aktivuje kapitoly 1–4 a incident `GENAI-SUPPORT-01`. "
    "Základná kapitola oddeľuje generative AI, foundation model, LLM a celú application chain a viaže model snapshot, tokenizer, prompt, retrieval, tools, policy a evals do exact request subjectu. "
    "Transformer kapitola vysvetľuje encoder/decoder families, token embeddings, positional information, Q/K/V self-attention, masks, feed-forward a residual blocks, logits, autoregressive generation, prefill/decode a KV cache. "
    "Tokenization kapitola viaže vocabulary, subword segmentation, special tokens, chat serialization, total context budget, truncation priority, segment manifest, finish reason a token/cost telemetry. "
    "Embeddings kapitola oddeľuje vectors, pooling, normalization, cosine/dot-product compatibility, similarity/relevance/identity, ANN index generation, multilingual evaluation, reindexing a access boundaries. "
    "Kapitoly 1–4 prešli substantial prose, executable/model surface a subject/evidence/failure/recovery/acceptance gate-om. Reálna inference, provider snapshot verification, tokenizer parity, embedding index build a business outcome neboli vykonané; sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 5–8: inference parameters/sampling, prompt roles, zero/one/few-shot prompting a prompt templates/versioning."
)
indices = [index for index, line in enumerate(lines) if line.startswith(status_prefix)]
if len(indices) != 1:
    raise SystemExit(f"Section 20 README: expected one status paragraph, found {len(indices)}")
lines[indices[0]] = status_line
readme.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

roadmap = ROOT / "ROADMAP.md"
replacements = {
    "- [ ] Generative AI, foundation model a large language model":
        "- [x] [Generative AI, foundation model a large language model](docs/20-llm-and-genai-engineering/generative-ai-foundation-model-llm.md)",
    "- [ ] Transformer architecture na praktickej úrovni":
        "- [x] [Transformer architecture na praktickej úrovni](docs/20-llm-and-genai-engineering/transformer-architecture-practical.md)",
    "- [ ] Tokens, tokenization a context window":
        "- [x] [Tokens, tokenization a context window](docs/20-llm-and-genai-engineering/tokens-tokenization-context-window.md)",
    "- [ ] Embeddings a semantic similarity":
        "- [x] [Embeddings a semantic similarity](docs/20-llm-and-genai-engineering/embeddings-semantic-similarity.md)",
}
for old, new in replacements.items():
    replace_once_or_present(roadmap, old, new)

review = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
review_lines = review.read_text(encoding="utf-8").splitlines()
prefix = "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering |"
new_line = (
    "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering | "
    "4/37 authoritative drafting | In progress | 2026-08-03 | "
    "Prvý authoritative blok aktivuje kapitoly 1–4 a incident `GENAI-SUPPORT-01`. "
    "Generative/foundation/LLM kapitola oddeľuje model class od application chainu, pretraining/adaptation/inference, probabilistic output, exact model/tokenizer/prompt/retrieval/tool/policy subject a model/application/business eval boundaries. "
    "Transformer kapitola vysvetľuje encoder/decoder families, hidden-state flow, Q/K/V attention, masks, multi-head behavior, FFN/residual/norm, logits, prefill/decode, KV cache, long-context a runtime boundaries. "
    "Tokenization kapitola pokrýva vocabulary/subword methods, multilingual/code token cost, special/chat serialization, total context budget, priority truncation, tokenizer-aware counting, padding, segment manifests, output limits a security flooding. "
    "Embeddings kapitola viaže model/tokenizer/pooling/normalization/metric/index generation, oddeľuje similarity/relevance/identity a pokrýva ANN recall, multilingual/domain eval, reindexing, privacy a retrieval acceptance. "
    "Reálne inference/index operations a business outcomes neboli vykonané; sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
indices = [index for index, line in enumerate(review_lines) if line.startswith(prefix)]
if len(indices) != 1:
    raise SystemExit(
        f"DOCUMENTATION-REVIEW-STATUS.md: expected one Section 20 row, found {len(indices)}"
    )
review_lines[indices[0]] = new_line
review.write_text("\n".join(review_lines) + "\n", encoding="utf-8", newline="\n")

print("Section 20 block 1-4 status files updated.")
