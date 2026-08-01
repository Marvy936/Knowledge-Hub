from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "17-keycloak-and-identity-platform"
README = SECTION / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
AUDIT = ROOT / "DOCUMENTATION-AUDIT.md"
REPORT = SECTION / "SECTION-17-BLOCK-05-08-FINALIZATION.md"

failures: list[str] = []

readme = README.read_text(encoding="utf-8")
ledger = LEDGER.read_text(encoding="utf-8")
audit = AUDIT.read_text(encoding="utf-8")

required_readme = [
    "Aktuálny authoritative stav sekcie je **8/30 · In progress**",
    "5. [Tokens, claims, protocol mappers a client scopes](tokens-claims-protocol-mappers-client-scopes.md)",
    "6. [Public, confidential a bearer-only client model](public-confidential-and-bearer-only-clients.md)",
    "7. [Service accounts a machine-to-machine authentication](service-accounts-and-machine-to-machine-authentication.md)",
    "8. [Authentication flows, executions a required actions](authentication-flows-executions-and-required-actions.md)",
    "### `KC-PAY-66`",
    "### Tokens, claims, protocol mappers a client scopes",
    "### Authentication flows, executions a required actions",
]
for marker in required_readme:
    if marker not in readme:
        failures.append(f"README missing: {marker}")

if "| `17-keycloak-and-identity-platform` — Keycloak and Identity Platform | 8/30 authoritative drafting | In progress |" not in ledger:
    failures.append("Central review ledger is not at 8/30 In progress")

for name in (
    "tokens-claims-protocol-mappers-client-scopes.md",
    "public-confidential-and-bearer-only-clients.md",
    "service-accounts-and-machine-to-machine-authentication.md",
    "authentication-flows-executions-and-required-actions.md",
):
    path = SECTION / name
    if not path.exists():
        failures.append(f"Missing chapter: {name}")
        continue
    text = path.read_text(encoding="utf-8")
    if "<!-- KNOWLEDGE-NAVIGATION:START -->" not in text:
        failures.append(f"Navigation footer missing: {name}")

if "### `docs/17-keycloak-and-identity-platform/" in audit:
    failures.append("Section 17 still appears in the critical/high learning-depth review queue")

lines = [
    "# Temporary Section 17 block 05–08 finalization",
    "",
    "> Branch-only gate report. Removed automatically on PASS.",
    "",
]
if failures:
    lines.append("FAIL")
    lines.append("")
    for failure in failures:
        lines.append(f"- {failure}")
else:
    lines.append("PASS")
    lines.append("")
    lines.append("README, ledger, navigation and audit gates passed for Keycloak chapters 05–08.")

REPORT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
print(f"Section 17 block finalization: {'FAIL' if failures else 'PASS'} ({len(failures)} issue(s)).")
