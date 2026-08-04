#!/usr/bin/env python3
"""Verify Section 21 chapters 5-8 have no critical/high audit entries."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "documentation-audit.json"
TARGETS = {
    "docs/21-ai-agents-and-intelligent-automation/short-term-state-long-term-external-memory.md",
    "docs/21-ai-agents-and-intelligent-automation/single-agent-multi-agent-architecture.md",
    "docs/21-ai-agents-and-intelligent-automation/supervisor-router-specialist-patterns.md",
    "docs/21-ai-agents-and-intelligent-automation/human-in-the-loop-approval-gates.md",
}

payload = json.loads(AUDIT.read_text(encoding="utf-8"))
file_paths = {
    item.get("path") or item.get("file")
    for item in payload.get("files", [])
    if isinstance(item, dict)
}
missing = sorted(TARGETS - file_paths)
if missing:
    raise SystemExit(f"Section 21 target files missing from audit: {missing}")

remaining = []
for finding in payload.get("findings", []):
    if not isinstance(finding, dict):
        continue
    path = finding.get("path") or finding.get("file")
    severity = str(finding.get("severity", "")).lower()
    if path in TARGETS and severity in {"critical", "high"}:
        remaining.append(finding)

if remaining:
    print(f"Section 21 block 5-8 critical/high findings remain: {len(remaining)}")
    for finding in remaining:
        path = finding.get("path") or finding.get("file") or "unknown-path"
        heading = (
            finding.get("heading")
            or finding.get("section")
            or finding.get("title")
            or finding.get("context")
            or "unknown-heading"
        )
        detail = (
            finding.get("message")
            or finding.get("description")
            or finding.get("detail")
            or finding.get("reason")
            or ""
        )
        print(
            f"- **{str(finding.get('severity', '')).upper()}** "
            f"`{path}` line {finding.get('line', '?')}, "
            f"`{finding.get('rule', 'unknown')}` — **{heading}**: {detail}"
        )
        print("  raw=" + json.dumps(finding, ensure_ascii=False, sort_keys=True))
    raise SystemExit(1)

print("Section 21 chapters 5-8 have no critical/high audit findings.")
