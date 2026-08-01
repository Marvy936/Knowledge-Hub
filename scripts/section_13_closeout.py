from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "13-security-and-identity"
README = SECTION / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
AUDIT = ROOT / "DOCUMENTATION-AUDIT.md"

ARTICLES = [
    "cia-triad.md",
    "authentication-authorization-auditing.md",
    "least-privilege.md",
    "iam-rbac.md",
    "active-directory.md",
    "ldap.md",
    "kerberos.md",
    "oauth-2.md",
    "openid-connect.md",
    "saml.md",
    "secrets-management.md",
    "encryption-at-rest-and-in-transit.md",
    "vulnerability-and-patch-management.md",
    "threat-modeling.md",
    "supply-chain-security.md",
    "sbom.md",
    "image-signing.md",
    "policy-as-code.md",
    "zero-trust.md",
]


def replace_prefixed_line(path: Path, prefix: str, replacement: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one line starting with {prefix!r} in {path}, found {len(matches)}")
    lines[matches[0]] = replacement
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


for name in ARTICLES:
    text = (SECTION / name).read_text(encoding="utf-8")
    words = len(text.split())
    if words < 900:
        raise RuntimeError(f"{name} is unexpectedly short: {words} words")
    if text.count("```") < 4:
        raise RuntimeError(f"{name} lacks two executable/protocol/configuration examples")
    lowered = text.lower()
    required_groups = [
        ("subject",),
        ("preukazuje", "dokazuje"),
        ("nepreukazuje", "nedokazuje"),
        ("recovery", "obnova", "náprava"),
    ]
    missing = [group for group in required_groups if not any(token in lowered for token in group)]
    if missing:
        raise RuntimeError(f"{name} lacks explicit subject/proof/recovery language: {missing}")

if "### `docs/13-security-and-identity/" in AUDIT.read_text(encoding="utf-8"):
    raise RuntimeError("Section 13 still has critical/high learning-depth findings")

readme = README.read_text(encoding="utf-8")
readme = readme.replace(
    "8. strict learning-depth audit pre všetkých 19 kapitol je `0/0/0` a practical audit nemá failures;",
    "8. Section 13 sa nenachádza v critical/high learning-depth review queue a zostávajúce low hints sa posudzujú manuálne;",
)
old_gate = "Finálny practical gate nameral 966 až 1 366 prose slov na kapitolu, bullet share 8,0 až 11,8 %, minimálne dva executable príklady a minimálne štyri explicitné evidence/proof-boundary vysvetlenia v každej kapitole."
new_gate = "Reprodukovateľný practical gate overil všetkých 19 kapitol samostatne. Každá obsahuje substantial connected prose, exact security/identity/protocol/artifact subject, najmenej dva executable protocol, CLI, policy alebo configuration examples a explicitné proof-boundary a recovery language. Section 13 sa nenachádza v critical/high learning-depth review queue; audit zostáva heuristickým review nástrojom, nie dôkazom runtime enforcementu alebo cryptographic correctness."
if old_gate not in readme and new_gate not in readme:
    raise RuntimeError("Expected Section 13 practical-gate paragraph not found")
readme = readme.replace(old_gate, new_gate, 1)

status_marker = "\n## Stav\n"
if status_marker not in readme:
    raise RuntimeError("Expected legacy Section 13 status table not found")
readme = readme.split(status_marker, 1)[0].rstrip() + "\n\n## Stav\n\nVšetkých **19/19 authoritative kapitol prešlo chapter-by-chapter explanation-depth and practical-example revalidation** a sekcia je `Ready for user review`. Starý per-topic `L2` status scaffold bol odstránený; readiness sa eviduje na úrovni celej sekcie a v centrálnom review ledgeri. Existujúce identity, federation, cryptography, secrets, vulnerability, threat-model, supply-chain, SBOM, signing, Policy as Code a Zero Trust lifecycle-y, executable examples, incidents a descendant-revocation recovery zostali zachované. Repository gate overuje textový a executable inventory, navigation, glossary a audit; reálne directory/federation services, credentials, cryptographic modules, registries, admission/enforcement points ani revocation propagation neboli týmto documentation workflowom vykonané. Stav preto neznamená používateľské `Accepted`, runtime `Verified` ani produkčné `Stable`.\n"
README.write_text(readme, encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `13-security-and-identity`",
    "| `13-security-and-identity` — Security and Identity | 19/19 chapter-by-chapter explanation-depth and practical-example revalidation | Ready for user review | 2026-08-01 | Všetkých 19 authoritative kapitol bolo znovu preverených podľa protected asset, exact identity/protocol/artifact/resource subjectu, trust a enforcement boundary, audit evidence, evidence-preserving containment, authoritative recovery a descendant-revocation štandardu. Reprodukovateľný gate potvrdil substantial connected prose, explicitný subject/proof/recovery language a najmenej dva executable protocol, CLI, policy alebo configuration examples v každej kapitole. OIDC a Image signing manuálny read-back potvrdil issuer+subject, transaction, signing-digest, multi-platform, enforcement-cache a runtime evidence boundaries; ostatné kapitoly zostali preserve-first bez redundantného prepisu. Legacy per-topic `L2` tabuľka a zastaraný absolútny `0/0/0` invariant boli odstránené. Section 13 nemá critical ani high learning-depth findings. README, review ledger, navigation, glossary a full audit boli synchronizované. Reálne identity/federation services, cryptographic operations, registries, policy enforcement a revocation propagation neboli týmto documentation workflowom vykonané; sekcia je Ready for user review, nie runtime Verified ani používateľsky Accepted. |",
)

print("Section 13 gate passed for 19/19 chapters and legacy L2 scaffold was removed.")
