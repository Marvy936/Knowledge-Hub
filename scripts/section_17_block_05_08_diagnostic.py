from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "17-keycloak-and-identity-platform"
REPORT = SECTION / "SECTION-17-BLOCK-05-08-GATE.md"

ACTIVE_ARTICLES = {
    "keycloak-architecture-and-responsibility-boundary.md": ["deploymentGeneration", "subject", "recovery"],
    "realm-client-user-group-role-session.md": ["realm", "client", "user session", "subject"],
    "oidc-clients-redirect-uris-scopes-pkce.md": ["PKCE", "redirect", "client scope", "subject"],
    "saml-clients-metadata-assertions-bindings.md": ["AuthnRequest", "Assertion", "ACS", "subject"],
    "tokens-claims-protocol-mappers-client-scopes.md": ["protocol mapper", "default client scope", "optional client scope", "audience", "Full Scope Allowed"],
    "public-confidential-and-bearer-only-clients.md": ["Client authentication", "public", "confidential", "bearer-only", "Direct Access Grant"],
    "service-accounts-and-machine-to-machine-authentication.md": ["client_credentials", "service-account user", "role-scope", "audience", "credential rotation"],
    "authentication-flows-executions-and-required-actions.md": ["REQUIRED", "ALTERNATIVE", "CONDITIONAL", "Direct Access Grant", "required action", "flow override"],
}

SEMANTIC_GROUPS = [
    ("subject", "identity", "generation"),
    ("evidence", "dôkaz", "preukazuje", "ukazuje", "potvrdzuje"),
    ("recovery", "obnova", "náprava", "revocation"),
    ("acceptance", "positive path", "forbidden path", "zakázan"),
]

rows = []
failures = []
for name, tokens in ACTIVE_ARTICLES.items():
    path = SECTION / name
    if not path.exists():
        rows.append((name, 0, 0, "missing file", "FAIL"))
        failures.append(f"{name}: missing file")
        continue
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    words = len(text.split())
    fences = text.count("```")
    missing_tokens = [token for token in tokens if token.lower() not in lowered]
    missing_groups = ["/".join(group) for group in SEMANTIC_GROUPS if not any(token in lowered for token in group)]
    reasons = []
    if words < 1100:
        reasons.append(f"words {words}<1100")
    if fences < 6:
        reasons.append(f"fences {fences}<6")
    if missing_tokens:
        reasons.append("tokens: " + ", ".join(missing_tokens))
    if missing_groups:
        reasons.append("semantic groups: " + "; ".join(missing_groups))
    status = "FAIL" if reasons else "PASS"
    if reasons:
        failures.append(f"{name}: {' | '.join(reasons)}")
    rows.append((name, words, fences, "<br>".join(reasons) if reasons else "—", status))

lines = [
    "# Temporary Section 17 block 05–08 gate diagnostic",
    "",
    "> Branch-only diagnostic. It does not activate README or ledger state and must be removed before merge.",
    "",
    "| Chapter | Words | Code fences | Missing requirements | Result |",
    "|---|---:|---:|---|---|",
]
for name, words, fences, reason, status in rows:
    lines.append(f"| `{name}` | {words} | {fences} | {reason} | **{status}** |")

lines.extend(["", "## Verdict", ""])
if failures:
    lines.append(f"Gate is **not ready**. Failures: {len(failures)}.")
    lines.append("")
    for failure in failures:
        lines.append(f"- {failure}")
else:
    lines.append("Gate is **ready** for README/ledger activation.")

REPORT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
print(f"Wrote {REPORT.relative_to(ROOT)} with {len(failures)} failure(s).")
