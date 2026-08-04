#!/usr/bin/env python3
"""Verify Section 20 chapters 21-24 have no critical/high audit entries."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs/20-llm-and-genai-engineering"
FILES = [
    "peft-adapters-lora.md",
    "quantization-local-inference.md",
    "gpu-memory-batching-serving-performance.md",
    "prompt-semantic-response-caching.md",
]

for name in FILES:
    path = SECTION / name
    if not path.is_file():
        raise SystemExit(f"Missing Section 20 block 21-24 chapter: {path}")

readme = (SECTION / "README.md").read_text(encoding="utf-8")
if "**24/37 · In progress**" not in readme:
    raise SystemExit("Section 20 README is not synchronized to 24/37 · In progress")

for name in FILES:
    if f"]({name})" not in readme:
        raise SystemExit(f"Section 20 README does not activate {name}")

audit = (ROOT / "DOCUMENTATION-AUDIT.md").read_text(encoding="utf-8")
try:
    critical_high = audit.split("## Critical and high findings", 1)[1].split(
        "## All findings by rule", 1
    )[0]
except IndexError as exc:
    raise SystemExit("Unexpected DOCUMENTATION-AUDIT.md structure") from exc

remaining = []
for name in FILES:
    marker = f"### `docs/20-llm-and-genai-engineering/{name}`"
    if marker not in critical_high:
        continue
    remaining.append(name)
    details = critical_high.split(marker, 1)[1].split("\n### `", 1)[0]
    print(f"\n{marker}{details}\n")

if remaining:
    raise SystemExit(
        f"Section 20 block 21-24 critical/high findings remain: {remaining}"
    )

print("Section 20 block 21-24 is active and has no critical/high audit entries.")
