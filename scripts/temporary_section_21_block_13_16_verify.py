#!/usr/bin/env python3
"""Verify Section 21 chapters 13-16 have no critical/high audit entries."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "documentation-audit.json"
TARGETS = {
    "docs/21-ai-agents-and-intelligent-automation/agent-identity-authentication-authorization.md",
    "docs/21-ai-agents-and-intelligent-automation/least-privilege-tools-credentials.md",
    "docs/21-ai-agents-and-intelligent-automation/sandboxing-code-execution.md",
    "docs/21-ai-agents-and-intelligent-automation/prompt-injection-tools-retrieved-content.md",
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
    print(f"Section 21 block 13-16 critical/high findings remain: {len(remaining)}")
    for finding in remaining:
        detail = finding.get("message") or finding.get("description") or finding.get("detail") or ""
        section = finding.get("section") or finding.get("heading") or "unknown section"
        print(
            f"- **{str(finding.get('severity', '')).upper()}** "
            f"`{finding.get('path') or finding.get('file')}` "
            f"line {finding.get('line', '?')}, `{finding.get('rule', 'unknown')}` — "
            f"**{section}**: {detail}"
        )
        print(f"  raw={json.dumps(finding, ensure_ascii=False, sort_keys=True)}")
    raise SystemExit(1)

print("Section 21 chapters 13-16 have no critical/high audit findings.")
