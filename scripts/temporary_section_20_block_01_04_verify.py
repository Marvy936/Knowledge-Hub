#!/usr/bin/env python3
"""Verify Section 20 chapters 1-4 have no critical/high audit entries."""

from pathlib import Path

FILES = [
    "generative-ai-foundation-model-llm.md",
    "transformer-architecture-practical.md",
    "tokens-tokenization-context-window.md",
    "embeddings-semantic-similarity.md",
]

audit = Path("DOCUMENTATION-AUDIT.md").read_text(encoding="utf-8")
critical_high = audit.split("## Critical and high findings", 1)[1].split(
    "## All findings by rule", 1
)[0]
remaining = []
for name in FILES:
    marker = f"### `docs/20-llm-and-genai-engineering/{name}`"
    if marker not in critical_high:
        continue
    remaining.append(name)
    details = critical_high.split(marker, 1)[1].split("\n### `", 1)[0]
    print(f"\n{marker}{details}\n")

if remaining:
    raise SystemExit(f"Section 20 block 1-4 critical/high findings remain: {remaining}")

print("Section 20 block 1-4 has no critical/high audit entries.")
