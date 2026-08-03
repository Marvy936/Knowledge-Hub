#!/usr/bin/env python3
"""Verify that final Section 19 chapters have no critical/high audit entries."""

from pathlib import Path

FILES = [
    "mlops-platform-architecture.md",
    "mlops-troubleshooting.md",
]

audit = Path("DOCUMENTATION-AUDIT.md").read_text(encoding="utf-8")
critical_high = audit.split("## Critical and high findings", 1)[1].split(
    "## All findings by rule", 1
)[0]
remaining = []
for name in FILES:
    marker = f"### `docs/19-mlops-and-ml-platforms/{name}`"
    if marker not in critical_high:
        continue
    remaining.append(name)
    details = critical_high.split(marker, 1)[1].split("\n### `", 1)[0]
    print(f"\n{marker}{details}\n")

if remaining:
    raise SystemExit(
        f"Section 19 final block critical/high findings remain: {remaining}"
    )

print("Section 19 final block has no critical/high audit entries.")
