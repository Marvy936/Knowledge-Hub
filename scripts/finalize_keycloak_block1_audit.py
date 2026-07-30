#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]

subprocess.run(["python", "scripts/update_glossary.py", "--check"], cwd=ROOT, check=True)
subprocess.run(["python", "scripts/update_navigation.py", "--check"], cwd=ROOT, check=True)
subprocess.run(["python", "scripts/audit_learning_depth.py", "--all-docs"], cwd=ROOT, check=True)
subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)

audit = json.loads((ROOT / "documentation-audit.json").read_text(encoding="utf-8"))
paths = {
    "docs/17-keycloak-and-identity-platform/keycloak-architecture-and-responsibility-boundary.md",
    "docs/17-keycloak-and-identity-platform/realm-client-user-group-role-session.md",
    "docs/17-keycloak-and-identity-platform/oidc-clients-redirect-uris-scopes-pkce.md",
    "docs/17-keycloak-and-identity-platform/saml-clients-metadata-assertions-bindings.md",
}
rows = [entry for entry in audit.get("files", []) if entry.get("path") in paths]
if {entry.get("path") for entry in rows} != paths:
    raise SystemExit("Incomplete Keycloak audit inventory")
if any("trigger" in entry.get("path", "") and "keycloak" in entry.get("path", "") for entry in audit.get("files", [])):
    raise SystemExit("Stale Keycloak trigger is still present in audit inventory")
for entry in rows:
    print(f"AUDIT {entry['path']}: words={entry['words']} critical={entry['critical']} high={entry['high']} medium={entry['medium']} low={entry['low']} grade={entry['grade']}")
    if entry["critical"] or entry["high"] or entry["medium"]:
        raise SystemExit(f"Strict Keycloak depth gate failed: {entry['path']}")

for path in [
    ROOT / "scripts/finalize_keycloak_block1_audit.py",
    ROOT / ".github/workflows/keycloak-block1-finalize.yml",
    ROOT / ".keycloak-block1-finalize-trigger",
]:
    path.unlink(missing_ok=True)
