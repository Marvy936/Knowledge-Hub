#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one marker in {path}: count={count} marker={old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


root_readme = ROOT / "README.md"
replace_once(
    root_readme,
    "17. [GitOps and Platform Engineering](docs/16-gitops-and-platform-engineering/README.md)\n",
    "17. [GitOps and Platform Engineering](docs/16-gitops-and-platform-engineering/README.md)\n"
    "18. [Keycloak and Identity Platform](docs/17-keycloak-and-identity-platform/README.md)\n",
)
replace_once(
    root_readme,
    "Všetky hlavné domény aktuálnej roadmapy sú aktívne. Budúce identity, ML, LLM a agentické oblasti sú predbežne rozpracované v [FUTURE-IDENTITY-AI-ROADMAP.md](FUTURE-IDENTITY-AI-ROADMAP.md).",
    "Hlavná roadmapa pokračuje aktívnou sekciou Keycloak and Identity Platform. Budúce ML, MLOps, LLM a agentické oblasti zostávajú rozpracované v [FUTURE-IDENTITY-AI-ROADMAP.md](FUTURE-IDENTITY-AI-ROADMAP.md).",
)

roadmap = ROOT / "ROADMAP.md"
roadmap_text = roadmap.read_text(encoding="utf-8").rstrip() + "\n"
if "### Keycloak and Identity Platform" in roadmap_text:
    raise SystemExit("Keycloak roadmap section already exists")
keycloak_roadmap = r'''

## Fáza 6 — Identity platformy

### Keycloak and Identity Platform

- [x] [Keycloak architecture a responsibility boundary](docs/17-keycloak-and-identity-platform/keycloak-architecture-and-responsibility-boundary.md)
- [x] [Realm, client, user, group, role a session](docs/17-keycloak-and-identity-platform/realm-client-user-group-role-session.md)
- [x] [OIDC clients, redirect URIs, scopes a PKCE](docs/17-keycloak-and-identity-platform/oidc-clients-redirect-uris-scopes-pkce.md)
- [x] [SAML clients, metadata, assertions a bindings](docs/17-keycloak-and-identity-platform/saml-clients-metadata-assertions-bindings.md)
- [ ] Tokens, claims, protocol mappers a client scopes
- [ ] Public, confidential a bearer-only client model
- [ ] Service accounts a machine-to-machine authentication
- [ ] Authentication flows, executions a required actions
- [ ] MFA, WebAuthn, passkeys a step-up authentication
- [ ] Password policies, brute-force protection a account recovery
- [ ] Identity brokering
- [ ] LDAP a Active Directory federation
- [ ] User storage, synchronization a cache semantics
- [ ] Authorization Services, resources, scopes, policies a permissions
- [ ] Token exchange, impersonation a delegated access
- [ ] Admin Console, Admin REST API a automation
- [ ] Events, audit, metrics a observability
- [ ] Themes, email templates a localization
- [ ] Keycloak server configuration, hostname a reverse proxy
- [ ] TLS, truststores, cookies, headers a production hardening
- [ ] Database, transactions, connection pools a schema lifecycle
- [ ] Infinispan caches, clustering a session behavior
- [ ] Keycloak Operator a Kubernetes deployment
- [ ] High availability, multi-AZ a multi-cluster trade-offs
- [ ] Backup, restore, realm import/export a disaster recovery
- [ ] Upgrades, migration guides a rollback boundaries
- [ ] Custom providers, SPI a extension lifecycle
- [ ] Securing APIs, microservices a MCP servers cez Keycloak
- [ ] Keycloak performance, sizing a load testing
- [ ] Keycloak troubleshooting
'''
roadmap.write_text(roadmap_text + keycloak_roadmap.lstrip("\n"), encoding="utf-8", newline="\n")

future = ROOT / "FUTURE-IDENTITY-AI-ROADMAP.md"
replace_once(
    future,
    "Tento dokument plánuje budúce sekcie Knowledge Hubu, ktoré sa začnú spracúvať až po dokončení aktuálnej hlavnej roadmapy. Neaktivuje nové dokumentačné sekcie a nemení súčasné učebné poradie.",
    "Tento dokument pôvodne plánoval identity, ML, LLM a agentické sekcie po dokončení základnej roadmapy. Sekcia Keycloak and Identity Platform je od 30. júla 2026 aktivovaná v hlavnom poradí; dokument naďalej plánuje jej zostávajúce bloky a budúce ML, MLOps, LLM a agentické sekcie.",
)
replace_once(
    future,
    "existujúca roadmapa\n→ Keycloak and Identity Platform\n→ Machine Learning Fundamentals",
    "existujúca roadmapa\n→ Keycloak and Identity Platform — aktívna sekcia 17\n→ Machine Learning Fundamentals",
)
replace_once(
    future,
    "## Keycloak and Identity Platform\n\nPredbežný priečinok:",
    "## Keycloak and Identity Platform\n\n> Stav: aktívna sekcia [`docs/17-keycloak-and-identity-platform/`](docs/17-keycloak-and-identity-platform/README.md), prvý authoritative blok 4/30 je spracovaný.\n\nAktívny priečinok:",
)

ledger = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
ledger_text = ledger.read_text(encoding="utf-8")
marker = "\n## Section-level completion criteria\n"
if marker not in ledger_text:
    raise SystemExit("Review ledger completion marker missing")
row = (
    "| `17-keycloak-and-identity-platform` — Keycloak and Identity Platform | 4/30 authoritative drafting | In progress | 2026-07-30 | "
    "Prvý strict blok bol vytvorený od nuly okolo connected incidentu `KC-PAY-65`. `Keycloak architecture a responsibility boundary` používa `business identity/access intent → public hostname/proxy → deployment/server generation → realm/client/flow → identity source → authentication/user/client session → token/assertion → local application session → resource authorization → revocation closure`. `Realm, client, user, group, role a session` oddeľuje realm/client/user identity, group inheritance, realm/client/composite role graph, client-scope projection a session descendants. `OIDC clients` používa exact client registration, redirect/web-origin boundary, state/nonce/PKCE, client scopes, mappers, `Full Scope Allowed`, audience a logout acceptance matrix. `SAML clients` používa metadata/entity/ACS/binding/key generation, SP-initiated transaction, signed assertion, mapper authority, local session a rollover/logout verification. Incident ukazuje contractor-a v child group, ktorý zdedil parent realm role `settlement-admin`; oba clients ju publikovali pre `Full Scope Allowed`, OIDC wildcard redirect bez required PKCE umožnil code theft a SAML IdP-initiated shared ACS vytvoril privileged local session. Realm sign-out nezrušil už vydaný access token ani downstream SAML session. Redesign používa client roles, explicitné role scopes, exact redirects, PKCE S256, SP-initiated privileged SAML, allowlisted mappers, resource authorization a complete descendant revocation. Sekcia zostáva In progress; ďalší blok začne tokens/claims/mappers/client scopes. |\n"
)
ledger.write_text(ledger_text.replace(marker, "\n" + row + marker, 1), encoding="utf-8", newline="\n")

subprocess.run(["python", "scripts/update_glossary.py", "--write"], cwd=ROOT, check=True)
subprocess.run(["python", "scripts/update_navigation.py", "--write"], cwd=ROOT, check=True)
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
    raise SystemExit("Audit inventory does not contain all Keycloak block files")
for entry in rows:
    print(
        f"AUDIT {entry['path']}: words={entry['words']} critical={entry['critical']} "
        f"high={entry['high']} medium={entry['medium']} low={entry['low']} grade={entry['grade']}"
    )

for path in [
    ROOT / "scripts/integrate_keycloak_block1.py",
    ROOT / ".github/workflows/keycloak-block1-integration.yml",
]:
    path.unlink(missing_ok=True)
