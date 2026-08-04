#!/usr/bin/env python3
"""Verify Section 20 chapters 29-32 have no critical/high audit entries."""

import json
from collections import defaultdict
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
audited = {
    Path(entry.get("path", "")).name
    for entry in payload.get("files", [])
    if Path(entry.get("path", "")).name in TARGETS
}
missing = TARGETS - audited
if missing:
    raise SystemExit(f"Target files missing from audit: {sorted(missing)}")

remaining: dict[str, list[dict]] = defaultdict(list)
for finding in payload.get("findings", []):
    filename = Path(finding.get("path", "")).name
    if filename not in TARGETS:
        continue
    if finding.get("severity") in {"critical", "high"}:
        remaining[filename].append(finding)

if remaining:
    print(f"Section 20 block 29-32 critical/high findings remain: {sorted(remaining)}")
    for filename, findings in sorted(remaining.items()):
        print(f"\n### `{filename}`")
        for finding in findings:
            print(
                f"- **{finding.get('severity', '').upper()}** line "
                f"{finding.get('line', '?')}, `{finding.get('rule', '?')}` — "
                f"**{finding.get('section', '?')}**: {finding.get('detail', '')}"
            )
    raise SystemExit(1)

print("Section 20 block 29-32 has no critical/high learning-depth findings.")
