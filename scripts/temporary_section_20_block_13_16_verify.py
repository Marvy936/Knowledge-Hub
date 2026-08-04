#!/usr/bin/env python3
"""Verify Section 20 chapters 13-16 have no critical/high audit entries."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
audit = (ROOT / "DOCUMENTATION-AUDIT.md").read_text(encoding="utf-8")
critical_high = audit.split("## Critical and high findings", 1)[1].split(
    "## All findings by rule", 1
)[0]
files = [
    "model-version-pinning-compatibility.md",
    "retrieval-augmented-generation-architecture.md",
    "chunking-metadata-document-processing.md",
    "vector-stores-indexing.md",
]
remaining = []
for name in files:
    marker = f"### `docs/20-llm-and-genai-engineering/{name}`"
    if marker not in critical_high:
        continue
    remaining.append(name)
    details = critical_high.split(marker, 1)[1].split("\n### `", 1)[0]
    print(f"\n{marker}{details}\n")
if remaining:
    raise SystemExit(
        f"Section 20 block 13-16 critical/high findings remain: {remaining}"
    )
print("Section 20 block 13-16 has no critical/high audit entries.")
