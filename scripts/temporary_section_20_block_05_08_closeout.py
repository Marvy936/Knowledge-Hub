#!/usr/bin/env python3
"""Temporary closeout helper for Section 20 chapters 5-8."""

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


roadmap = ROOT / "ROADMAP.md"
replacements = {
    "- [ ] Inference parameters, sampling a determinism":
        "- [x] [Inference parameters, sampling a determinism](docs/20-llm-and-genai-engineering/inference-parameters-sampling-determinism.md)",
    "- [ ] Prompt roles, instructions, context a examples":
        "- [x] [Prompt roles, instructions, context a examples](docs/20-llm-and-genai-engineering/prompt-roles-instructions-context-examples.md)",
    "- [ ] Zero-shot, one-shot a few-shot prompting":
        "- [x] [Zero-shot, one-shot a few-shot prompting](docs/20-llm-and-genai-engineering/zero-one-few-shot-prompting.md)",
    "- [ ] Prompt templates, variables a versioning":
        "- [x] [Prompt templates, variables a versioning](docs/20-llm-and-genai-engineering/prompt-templates-variables-versioning.md)",
}
for old, new in replacements.items():
    replace_once_or_present(roadmap, old, new)

review = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = review.read_text(encoding="utf-8").splitlines()
prefix = "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering |"
new_line = (
    "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering | "
    "8/37 authoritative drafting | In progress | 2026-08-03 | "
    "Druhý authoritative blok aktivuje kapitoly 5–8 a incident `GENAI-SUPPORT-02`. "
    "Inference kapitola viaže exact model/tokenizer/prompt subject na greedy a sampled decoding, temperature, top-k/top-p, penalties, stopping, output budget, seed, provider translation, runtime/batch generation a repeated-run acceptance a oddeľuje reproducibility od correctness. "
    "Prompt-role kapitola klasifikuje trusted instructions, user goal, retrieved context, assistant history, examples a tool outputs a odmieta provider role ako bezpečnostný sandbox bez trust modelu a downstream authorization. "
    "Zero/one/few-shot kapitola versionuje example set, provenance, labels, segmenty, ordering, dynamic selection, context budget, leakage a paired evals. "
    "Prompt-template kapitola viaže template, typed variables, strict rendering, trust-aware interpolation, branches, content digest, registry promotion, compatibility, cache, canary a rollback do prompt release lifecycle. "
    "Kapitoly 5–8 prešli repository prose/executable/subject/evidence/failure/recovery/acceptance kontrolami. Reálna inference, provider parity, adversarial prompt execution, Registry mutation a business outcome neboli vykonané; sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
matching = [index for index, line in enumerate(lines) if line.startswith(prefix)]
if len(matching) != 1:
    raise SystemExit(
        f"DOCUMENTATION-REVIEW-STATUS.md: expected one Section 20 row, found {len(matching)}"
    )
lines[matching[0]] = new_line
review.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

print("Section 20 block 05-08 status files updated.")
