from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "17-keycloak-and-identity-platform"
README = SECTION / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"

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


def replace_prefixed_line(path: Path, prefix: str, replacement: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [index for index, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one line starting with {prefix!r} in {path}, found {len(matches)}")
    lines[matches[0]] = replacement
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


for name, tokens in ACTIVE_ARTICLES.items():
    path = SECTION / name
    if not path.exists():
        raise RuntimeError(f"Missing authoritative chapter: {name}")
    text = path.read_text(encoding="utf-8")
    words = len(text.split())
    if words < 1100:
        raise RuntimeError(f"{name} is unexpectedly short: {words} words")
    if text.count("```") < 6:
        raise RuntimeError(f"{name} lacks sufficient executable/model examples")
    lowered = text.lower()
    missing = [token for token in tokens if token.lower() not in lowered]
    if missing:
        raise RuntimeError(f"{name} is missing required Keycloak concepts: {missing}")
    semantic_groups = [
        ("subject", "identity", "generation"),
        ("evidence", "dôkaz", "preukazuje", "ukazuje", "potvrdzuje"),
        ("recovery", "obnova", "náprava", "revocation"),
        ("acceptance", "positive path", "forbidden path", "zakázan"),
    ]
    missing_groups = [group for group in semantic_groups if not any(token in lowered for token in group)]
    if missing_groups:
        raise RuntimeError(f"{name} lacks subject/evidence/recovery/acceptance language: {missing_groups}")

readme = README.read_text(encoding="utf-8")

active_marker = "4. [SAML clients, metadata, assertions a bindings](saml-clients-metadata-assertions-bindings.md)\n"
active_extension = """4. [SAML clients, metadata, assertions a bindings](saml-clients-metadata-assertions-bindings.md)
5. [Tokens, claims, protocol mappers a client scopes](tokens-claims-protocol-mappers-client-scopes.md)
6. [Public, confidential a bearer-only client model](public-confidential-and-bearer-only-clients.md)
7. [Service accounts a machine-to-machine authentication](service-accounts-and-machine-to-machine-authentication.md)
8. [Authentication flows, executions a required actions](authentication-flows-executions-and-required-actions.md)
"""
if active_extension not in readme:
    if active_marker not in readme:
        raise RuntimeError("Expected Section 17 active-order marker not found")
    readme = readme.replace(active_marker, active_extension, 1)

readme = readme.replace(
    "Aktuálny authoritative stav sekcie je **4/30 · In progress**.",
    "Aktuálny authoritative stav sekcie je **8/30 · In progress**. Kapitoly 1–8 tvoria prvý kompletný identity, protocol, token-projection, client-capability, machine-identity a authentication-transaction blok. Sekcia zatiaľ nie je `Ready for user review`; ďalší blok začína MFA, credential recovery, brokering a federation lifecycle-om.",
)

planned_lines = """5. Tokens, claims, protocol mappers a client scopes  
6. Public, confidential a bearer-only client model  
7. Service accounts a machine-to-machine authentication  
8. Authentication flows, executions a required actions  
"""
readme = readme.replace(planned_lines, "")

scenario_marker = "\n## Dominantný model sekcie\n"
scenario = """
### `KC-PAY-66` — broad token projection, mixed-purpose client a bypassed step-up

Atlas použil client `settlement-ops` súčasne pre desktop CLI, browser administration aj Kubernetes batch workload. Client mal zapnuté Standard Flow, Direct Access Grants a Service Accounts, používal shared secret distribuovaný aj v CLI a zostal na `Full Scope Allowed`. Shared default client scope publikoval expanded realm roles, broad internal audience a custom claim `permissions`; dedicated mapper browser clienta zapisoval ten istý claim inou semantics.

Service-account user zdedil composite `settlement-operator`, ktorý zahŕňal reconcile aj export actions. Browser flow obsahoval WebAuthn execution, ale validná Cookie `ALTERNATIVE` uspokojila remembered-SSO path bez fresh step-up. `CONFIGURE_TOTP` bol označený ako default required action, no existujúcim users nebol spätne priradený. Legacy CLI použil Direct Access Grant, takže Browser flow a jeho WebAuthn branch sa nevykonali vôbec.

```text
mixed browser, native a machine responsibility
→ one confidential client a shared credential
→ broad role-scope a claim projection
→ remembered SSO alebo Direct Grant path
→ valid token bez intended fresh authentication
→ role-only API authorization
→ privileged reconciliation alebo export operation
→ secret rotation bez already-issued-token closure
```

Redesign rozdelí browser, native, machine a resource-server responsibilities do samostatných clients. Token projection používa dedicated/default/optional scopes s jedným ownerom claims, explicitný role-scope intersection a service-specific audience. Machine workload používa workload-bound confidential authentication, browser client má versionovaný step-up flow override, Direct Access Grant je zakázaný, existing users dostanú staged required-action assignment a downstream APIs validujú issuer, audience, caller, token type, tenant, resource a action. Recovery uzatvára old credential, stale token, remembered SSO, fresh login, second client, second token a second operation paths.
"""
if scenario.strip() not in readme:
    if scenario_marker not in readme:
        raise RuntimeError("Expected Section 17 scenario insertion marker not found")
    readme = readme.replace(scenario_marker, "\n" + scenario.strip() + "\n" + scenario_marker, 1)

learning_extension = """

### Tokens, claims, protocol mappers a client scopes

- definovať exact token-projection subject vrátane realm, client, session, requested scopes, mapper, role graph a signing-key generation;
- rozlíšiť access token, ID token, refresh token a UserInfo consumer contract;
- odlíšiť OAuth scope string, Keycloak client scope object a Authorization Services scope;
- vysvetliť default, optional a dedicated client scopes a ich blast radius;
- navrhnúť role scope mappings a vypnutie `Full Scope Allowed` bez straty intended role projection;
- používať protocol mappers ako explicitnú assertion authority s jediným ownerom claimu a stabilným JSON type-om;
- vysvetliť `aud`, `azp`, `scope`, realm/client roles a local resource permission;
- overiť stale token, key rotation, wrong audience, wrong client, second token a second operation.

### Public, confidential a bearer-only client model

- viazať client model na runtime architecture a schopnosť chrániť credential, nie na UI label;
- vysvetliť aktuálny `Client authentication` ON/OFF model a historické bearer-only terminology;
- oddeliť browser/native public clients, server-side confidential clients a resource-server responsibility;
- navrhnúť exact enabled-grant a endpoint capability matrix pre každý client;
- zakázať shared mixed-purpose clients, secrets v public binaries a nepotrebné Direct Access Grants;
- porovnať secret, private-key JWT, mTLS a workload-bound authentication;
- overiť redirect, PKCE, client authentication, audience, token storage a wrong-runtime paths;
- vykonať second-instance, old-credential, stolen-token a adjacent-client negative tests.

### Service accounts a machine-to-machine authentication

- definovať exact service-account subject vrátane client internal ID, linked service-account usera, credential, role-scope a workload generation;
- vysvetliť client-credentials grant bez human browser/MFA lifecycle-u;
- preukázať intersection service-account roles a client/client-scope role scope mappings;
- navrhnúť explicitné resource-server client roles a service-specific audience;
- oddeliť credential rotation od already-issued-token descendants;
- porovnať client secret, private-key JWT, mTLS a federovanú workload identity;
- viazať token na caller client, tenant, resource, action a durable operation ID;
- overiť old credential, wrong audience, wrong tenant, stale token, retry a second-operation behavior.

### Authentication flows, executions a required actions

- definovať exact authentication transaction vrátane realm/client flow bindingu, execution graphu, authentication session a existing user session;
- vysvetliť `REQUIRED`, `ALTERNATIVE`, `CONDITIONAL` a `DISABLED` semantics spolu s priority a subflow levelom;
- rozlíšiť fresh login, remembered SSO Cookie path, client-specific step-up a insufficient authentication level;
- vysvetliť, prečo Browser MFA automaticky nechráni Direct Access Grant;
- kopírovať a versionovať flows, používať client overrides a staged promotion;
- rozlíšiť enabled/default/per-user required action a Application-Initiated Action;
- sledovať action-token issue, authoritative user mutation a session/token descendants;
- overiť fresh, remembered, missing-credential, expired-link, replay, second-user a second-client paths.
"""
if "### Tokens, claims, protocol mappers a client scopes" not in readme:
    readme = readme.rstrip() + learning_extension + "\n"

README.write_text(readme.rstrip() + "\n", encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `17-keycloak-and-identity-platform`",
    "| `17-keycloak-and-identity-platform` — Keycloak and Identity Platform | 8/30 authoritative drafting | In progress | 2026-08-01 | Prvých osem authoritative kapitol je aktívnych. Pôvodný blok 1–4 pokrýva deployment/realm/client/session responsibility, core object model, OIDC redirect/PKCE a SAML metadata/assertion/binding lifecycle. Blok 5–8 je uzavretý ako jedna strict generation: token types, default/optional/dedicated client scopes, role scope mappings, protocol mappers, audience a stale-token behavior; public/confidential/bearer-only capability model; service-account user, client-credentials role intersection, workload authentication a credential descendants; authentication-flow bindings, execution requirements, remembered SSO, Direct Grant a required-action lifecycle. Connected incident `KC-PAY-66` spája broad claim projection, mixed-purpose client, preprivilegovaný service account, remembered-SSO/Direct-Grant bypass a incomplete token/session closure. Všetkých 8 aktívnych kapitol prešlo substantial prose, executable example, subject/evidence/recovery/acceptance gate-om. Navigation, glossary a full audit sú synchronizované. Sekcia zostáva In progress; ďalší blok začína MFA/WebAuthn/passkeys, password/brute-force/account recovery, identity brokering a LDAP/AD federation. |",
)

print("Keycloak block 05-08 passed the 8-chapter gate and was activated in README and ledger.")
