#!/usr/bin/env python3
"""Verify final Section 20 chapter 37 has no critical/high audit entries."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "documentation-audit.json"
TARGET = "llm-application-troubleshooting.md"

payload = json.loads(AUDIT.read_text(encoding="utf-8"))
audited = {
    Path(entry.get("path", "")).name
    for entry in payload.get("files", [])
}
if TARGET not in audited:
    raise SystemExit(f"Target file missing from audit: {TARGET}")

remaining = [
    finding
    for finding in payload.get("findings", [])
    if Path(finding.get("path", "")).name == TARGET
    and finding.get("severity") in {"critical", "high"}
]

if remaining:
    print(f"Section 20 chapter 37 critical/high findings remain: {len(remaining)}")
    for finding in remaining:
        print(
            f"- **{finding.get('severity', '').upper()}** line "
            f"{finding.get('line', '?')}, `{finding.get('rule', '?')}` — "
            f"**{finding.get('section', '?')}**: {finding.get('detail', '')}"
        )
    raise SystemExit(1)

print("Section 20 chapter 37 has no critical/high learning-depth findings.")
