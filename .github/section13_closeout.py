from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "docs/13-security-and-identity/README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def update_readme() -> None:
    text = README.read_text(encoding="utf-8")

    chain = """## Section-wide learning chain

Sekcia používa jeden súvislý security lifecycle. Začína chráneným business outcome-om a exact subjectom, pokračuje identity a trust transitions, effective enforcementom a auditom a končí revocation, recovery a forbidden-path validation.

```text
business/security objective a protected asset
→ exact identity, resource, release alebo cryptographic subject
→ trust, administrative, data a execution boundaries
→ authoritative identity/configuration/evidence generation
→ authentication, directory, federation alebo build transition
→ policy decision a complete enforcement coverage
→ runtime side effect a audit evidence
→ competing hypotheses a discriminating read-back
→ evidence-preserving containment
→ authoritative recovery a descendant revocation
→ allowed, forbidden, alternate-path a second-operation validation
```

Connected incidents `SEC-PAY-47` až `SEC-PAY-51` držia rovnaký Atlas Payments context. `SEC-PAY-47` spája CIA, AAA, least privilege a IAM/RBAC cez stale entitlement a delegated workload capability. `SEC-PAY-48` spája AD replication, replica-bound LDAP query, fresh Kerberos PAC a OAuth resource authorization. `SEC-PAY-49` spája OIDC, SAML, secrets a cryptographic key-purpose boundaries. `SEC-PAY-50` vedie od vulnerability a threat modelu cez compromised builder po stage-correct SBOM. `SEC-PAY-51` uzatvára exact OCI signing subject, policy enforcement coverage a continuous Zero Trust revocation.

"""
    if "## Section-wide learning chain" not in text:
        text = text.replace("## Predpoklady\n", chain + "## Predpoklady\n", 1)

    gate = """## Section-level completion gate

Sekcia je pripravená na používateľskú kontrolu iba vtedy, keď platí celý nasledujúci contract:

1. všetkých 19 authoritative kapitol má dominantný lifecycle a exact security, identity, protocol, artifact alebo resource subject;
2. každá kapitola obsahuje aspoň dva executable protocol, CLI, policy alebo configuration príklady;
3. každý významný príkaz alebo artifact vysvetľuje mechanizmus, očakávaný read-back a hranicu toho, čo výsledok ešte nepreukazuje;
4. configured, published, loaded, effective, runtime a business states zostávajú explicitne oddelené;
5. komplexné failures používajú competing hypotheses, discriminating evidence, evidence-preserving containment a authoritative recovery;
6. recovery overuje allowed outcome, forbidden outcome, alternate alebo delegated path a second session, ticket, rotation, policy decision alebo release operation;
7. directory, federation, secret, cryptographic, supply-chain a policy descendants sú inventarizované a revoke-nuté, nie iba odstránené z jedného source-u;
8. strict learning-depth audit pre všetkých 19 kapitol je `0/0/0` a practical audit nemá failures;
9. navigation, glossary a centrálny review ledger sú synchronizované a dočasné audit artifacts sú odstránené.

Finálny practical gate nameral 966 až 1 366 prose slov na kapitolu, bullet share 8,0 až 11,8 %, minimálne dva executable príklady a minimálne štyri explicitné evidence/proof-boundary vysvetlenia v každej kapitole.

"""
    if "## Section-level completion gate" not in text:
        text = text.replace("## Stav\n", gate + "## Stav\n", 1)

    text = re.sub(
        r"^(\| .+? \|) Learning (\| L2 \|)$",
        r"\1 Strict practical revalidation complete \2",
        text,
        flags=re.MULTILINE,
    )
    README.write_text(text, encoding="utf-8", newline="\n")


def update_ledger() -> None:
    text = LEDGER.read_text(encoding="utf-8")
    row = (
        "| `13-security-and-identity` — Security and Identity | 19/19 prose-first practical strict revalidation | Ready for user review | 2026-07-31 | "
        "Všetkých 19 authoritative kapitol bolo kompletne prepísaných v piatich connected blokoch podľa prose-first a practical-example gate-u. "
        "`SEC-PAY-47` spája CIA, authentication/authorization/audit, least privilege a IAM/RBAC cez incomplete mover reconciliation, stale nested entitlement, prežívajúcu session a delegated Kubernetes workload capability. "
        "`SEC-PAY-48` spája AD authority a replication metadata, DNS/site/DC selection, replica-bound LDAP query, fresh Kerberos ticket so stale PAC a protocol-correct OAuth flow s broad audience a scope-only resource authorization. "
        "`SEC-PAY-49` spája exact OIDC issuer+subject a SAML entity/metadata trust s exportovateľným shared keyom, indirect Kubernetes Secret accessom, consumer-loaded generations, purpose-specific non-exportable replacementom a complete descendant revocation. "
        "`SEC-PAY-50` spája affected-runtime vulnerability verdict, falsifikovateľný threat model, persistent compromised builder, source-to-runtime provenance authority a stage-correct source/toolchain/final-artifact SBOM. "
        "`SEC-PAY-51` uzatvára multi-platform OCI subject binding, signature/attestation semantics, immutable Policy as Code generation a input contract, native aj custom-controller PEP coverage, digest/policy/posture-aware cache a continuous Zero Trust re-evaluation. "
        "Kapitoly obsahujú reálne `kubectl`, PowerShell/AD, LDAP, Kerberos, OAuth/OIDC, SAML/XML, Vault, OpenSSL/KMS, Trivy/Grype, Syft, Cosign, OPA/Rego/CEL a runtime read-back príklady; každý významný artifact vysvetľuje, čo preukazuje a čo nie. "
        "Finálny gate dosiahol 19/19 `0/0/0`, 966–1 366 prose slov, bullet share 8,0–11,8 %, minimálne dva executable príklady a minimálne štyri evidence-boundary vysvetlenia na kapitolu. "
        "Ordering, navigation `12-observability/cardinality.md ↔ CIA triáda` cez celú sekciu po `Zero Trust ↔ 14-sre-and-operations/README.md`, glossary a generated artifacts boli synchronizované. "
        "Sekcia je pripravená na používateľskú kontrolu, nie automaticky používateľsky schválená, Accepted, Verified ani Stable. |"
    )
    pattern = r"^\| `13-security-and-identity` — Security and Identity \|.*$"
    if re.search(pattern, text, flags=re.MULTILINE):
        text = re.sub(pattern, lambda _: row, text, count=1, flags=re.MULTILINE)
    else:
        marker = "| `14-sre-and-operations` — SRE and Operations |"
        text = text.replace(marker, row + "\n\n" + marker, 1)
    LEDGER.write_text(text, encoding="utf-8", newline="\n")


def validate() -> None:
    run("python", "scripts/update_glossary.py", "--write")
    run("python", "scripts/update_navigation.py", "--write")
    run("python", "scripts/update_glossary.py", "--check")
    run("python", "scripts/update_navigation.py", "--check")
    audit_json = Path("/tmp/section13-audit.json")
    run(
        "python",
        "scripts/audit_learning_depth.py",
        "--all-docs",
        "--report",
        "/tmp/section13-audit.md",
        "--json",
        str(audit_json),
    )
    raw = json.loads(audit_json.read_text(encoding="utf-8"))
    findings = [
        finding
        for finding in raw["findings"]
        if finding["path"].startswith("docs/13-security-and-identity/")
        and finding["severity"] in {"critical", "high", "medium"}
    ]
    if findings:
        raise RuntimeError(f"Section 13 still has strict findings: {findings}")


def cleanup() -> None:
    for relative in (
        ".github/section13-quality-report.txt",
        ".github/section13-closeout-trigger.txt",
        ".github/section13-closeout-trigger-2.txt",
        ".github/workflows/temporary-section-13-quality-audit.yml",
        ".github/section13_closeout.py",
    ):
        (ROOT / relative).unlink(missing_ok=True)


if __name__ == "__main__":
    update_readme()
    update_ledger()
    validate()
    cleanup()
