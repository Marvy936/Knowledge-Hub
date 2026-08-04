#!/usr/bin/env python3
"""Verify Section 20 chapters 29-32 have no critical/high audit entries."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "documentation-audit.json"
TARGETS = {
    "tracing-token-usage-cost-observability.md",
    "hallucination-faithfulness-factuality.md",
    "prompt-injection-indirect-prompt-injection.md",
    "data-exfiltration-tool-abuse-excessive-agency.md",
}

payload = json.loads(AUDIT.read_text(encoding="utf-8"))
remaining: dict[str, list[dict]] = {}

for entry in payload.get("files", []):
    path = Path(entry.get("path", ""))
    if path.name not in TARGETS:
        continue
    findings = [
        finding
        for finding in entry.get("findings", [])
        if finding.get("severity") in {"critical", "high"}
    ]
    if findings:
        remaining[path.name] = findings

if remaining:
    print(f"Section 20 block 29-32 critical/high findings remain: {sorted(remaining)}")
    for filename, findings in remaining.items():
        print(f"\n### `{filename}`")
        for finding in findings:
            print(
                f"- **{finding.get('severity', '').upper()}** line "
                f"{finding.get('line', '?')}, `{finding.get('rule', '?')}` — "
                f"**{finding.get('heading', '?')}**: {finding.get('message', '')}"
            )
    raise SystemExit(1)

missing = TARGETS - {
    Path(entry.get("path", "")).name
    for entry in payload.get("files", [])
}
if missing:
    raise SystemExit(f"Target files missing from audit: {sorted(missing)}")

print("Section 20 block 29-32 has no critical/high learning-depth findings.")
