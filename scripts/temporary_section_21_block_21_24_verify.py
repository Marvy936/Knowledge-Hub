#!/usr/bin/env python3
"""Verify Section 21 chapters 21-24 have no critical/high audit entries."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "docs/21-ai-agents-and-intelligent-automation/cost-latency-token-budgets.md",
    "docs/21-ai-agents-and-intelligent-automation/agent-reliability-fallback-kill-switch.md",
    "docs/21-ai-agents-and-intelligent-automation/multi-tenant-isolation.md",
    "docs/21-ai-agents-and-intelligent-automation/agent-governance-audit.md",
}

for target in TARGETS:
    if not (ROOT / target).is_file():
        raise SystemExit(f"Missing target chapter: {target}")

readme = (ROOT / "docs/21-ai-agents-and-intelligent-automation/README.md").read_text(encoding="utf-8")
if "**24/62 · In progress**" not in readme:
    raise SystemExit("Section 21 README status is not 24/62 · In progress")
for target in TARGETS:
    name = Path(target).name
    if f"]({name})" not in readme:
        raise SystemExit(f"Section 21 README does not link {name}")

data = json.loads((ROOT / "documentation-audit.json").read_text(encoding="utf-8"))
all_findings = data.get("findings", []) if isinstance(data, dict) else []
findings = []
for finding in all_findings:
    if not isinstance(finding, dict):
        continue
    if finding.get("path") not in TARGETS:
        continue
    if str(finding.get("severity", "")).lower() in {"critical", "high"}:
        findings.append(finding)

if findings:
    print(f"Section 21 block 21-24 critical/high findings remain: {len(findings)}")
    for finding in findings:
        severity = str(finding.get("severity", "unknown")).upper()
        path = finding.get("path", "unknown")
        line = finding.get("line", "?")
        rule = finding.get("rule", "unknown-rule")
        section = finding.get("section", "unknown section")
        detail = finding.get("detail", "")
        print(f"- **{severity}** `{path}` line {line}, `{rule}` — **{section}**: {detail}")
        print(f"  raw={json.dumps(finding, ensure_ascii=False, sort_keys=True)}")
    raise SystemExit(1)

print("Section 21 chapters 21-24 have no critical/high learning-depth findings.")
