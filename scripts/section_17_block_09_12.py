from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "17-keycloak-and-identity-platform"
README = SECTION / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
AUDIT = ROOT / "DOCUMENTATION-AUDIT.md"

BASELINE = [
    "keycloak-architecture-and-responsibility-boundary.md",
    "realm-client-user-group-role-session.md",
    "oidc-clients-redirect-uris-scopes-pkce.md",
    "saml-clients-metadata-assertions-bindings.md",
    "tokens-claims-protocol-mappers-client-scopes.md",
    "public-confidential-and-bearer-only-clients.md",
    "service-accounts-and-machine-to-machine-authentication.md",
    "authentication-flows-executions-and-required-actions.md",
]

BLOCK = {
    "mfa-webauthn-passkeys-and-step-up-authentication.md": [
        "webauthn", "passkey", "discoverable credential", "user verification", "acr", "step-up"
    ],
    "password-policies-brute-force-protection-and-account-recovery.md": [
        "password policy", "brute-force", "attack-detection", "reset credentials", "action token", "session"
    ],
    "identity-brokering.md": [
        "first broker login", "trust email", "sync mode", "federated", "post login", "account linking"
    ],
    "ldap-and-active-directory-federation.md": [
        "import users", "edit mode", "ldap", "active directory", "full sync", "cache"
    ],
}

SEMANTIC_GROUPS = [
    ("subject", "identity", "generation"),
    ("evidence", "dôkaz", "preukazuje", "ukazuje", "potvrdzuje", "verdict"),
    ("recovery", "obnova", "náprava", "revocation"),
    ("acceptance", "positive path", "forbidden path", "zakázan", "akcept"),
]


def validate(path: Path, minimum_words: int, minimum_fences: int) -> str:
    if not path.exists():
        raise RuntimeError(f"Missing authoritative chapter: {path.name}")
    text = path.read_text(encoding="utf-8")
    words = len(text.split())
    fences = text.count("```")
    if words < minimum_words:
        raise RuntimeError(f"{path.name} is unexpectedly short: {words}<{minimum_words}")
    if fences < minimum_fences:
        raise RuntimeError(f"{path.name} lacks executable/model surface: {fences}<{minimum_fences}")
    return text


def replace_prefixed_line(path: Path, prefix: str, replacement: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one {prefix!r} line in {path}, found {len(matches)}")
    lines[matches[0]] = replacement
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


for name in BASELINE:
    validate(SECTION / name, 850, 4)

for name, concepts in BLOCK.items():
    text = validate(SECTION / name, 1200, 6)
    lowered = text.lower()
    missing = [concept for concept in concepts if concept not in lowered]
    if missing:
        raise RuntimeError(f"{name} missing concepts: {missing}")
    missing_groups = [group for group in SEMANTIC_GROUPS if not any(token in lowered for token in group)]
    if missing_groups:
        raise RuntimeError(f"{name} missing semantic groups: {missing_groups}")
    if "<!-- KNOWLEDGE-NAVIGATION:START -->" not in text:
        raise RuntimeError(f"{name} missing navigation footer")

readme = README.read_text(encoding="utf-8")
active_marker = "8. [Authentication flows, executions a required actions](authentication-flows-executions-and-required-actions.md)\n"
active_extension = """8. [Authentication flows, executions a required actions](authentication-flows-executions-and-required-actions.md)
9. [MFA, WebAuthn, passkeys a step-up authentication](mfa-webauthn-passkeys-and-step-up-authentication.md)
10. [Password policies, brute-force protection a account recovery](password-policies-brute-force-protection-and-account-recovery.md)
11. [Identity brokering](identity-brokering.md)
12. [LDAP a Active Directory federation](ldap-and-active-directory-federation.md)
"""
if active_extension not in readme:
    if active_marker not in readme:
        raise RuntimeError("Active-order marker for chapter 8 not found")
    readme = readme.replace(active_marker, active_extension, 1)

old_state = "Aktuálny authoritative stav sekcie je **8/30 · In progress**. Kapitoly 1–8 tvoria prvý kompletný identity, protocol, token-projection, client-capability, machine-identity a authentication-transaction blok. Sekcia zatiaľ nie je `Ready for user review`; ďalší blok začína MFA, credential recovery, brokering a federation lifecycle-om."
new_state = "Aktuálny authoritative stav sekcie je **12/30 · In progress**. Kapitoly 1–12 pokrývajú core Keycloak architecture, OIDC/SAML clients, token projection, client capability, machine identity, authentication flows, MFA/passkeys, credential recovery, identity brokering a LDAP/Active Directory federation. Sekcia zatiaľ nie je `Ready for user review`; ďalší blok začína user-storage synchronization/cache, Authorization Services, delegated access a Admin API automation."
if old_state not in readme and new_state not in readme:
    raise RuntimeError("Expected 8/30 state paragraph not found")
readme = readme.replace(old_state, new_state, 1)

planned = """9. MFA, WebAuthn, passkeys a step-up authentication  
10. Password policies, brute-force protection a account recovery  
11. Identity brokering  
12. LDAP a Active Directory federation  
"""
readme = readme.replace(planned, "")

scenario_marker = "\n## Dominantný model sekcie\n"
scenario = """### `KC-PAY-67` až `KC-PAY-70` — assurance, recovery, broker linking a directory-revocation chain

Druhý strict blok rozširuje pôvodný identity incident o štyri navzájom súvisiace failure domains. `KC-PAY-67` ukazuje, že registered passkey nepreukazuje passkey použitie v current transaction; remembered SSO bez minimum ACR umožnil privileged operation pri nižšom assurance. `KC-PAY-68` ukazuje, že password reset a old-password rejection neodstránili refresh token ani local application session. `KC-PAY-69` spája valid external OIDC response, `Trust Email`, unsafe account auto-linking a FORCE mapper s prevzatím existujúceho local accountu. `KC-PAY-70` ukazuje stale imported LDAP/group/cache state a active sessions po AD group removal a account disable.

```text
credential alebo external-directory change
→ Keycloak policy/flow/provider generation
→ authentication alebo federation transaction
→ local user/session/token state
→ downstream authorization
→ stale credential, link, cache alebo session descendant
→ continued protected operation
```

Redesign viaže assurance na current `acr/auth_time` a protected operation; recovery uzatvára sessions/tokens/applications; broker linking používa stable issuer+subject a verified local account proof; LDAP security attributes majú explicitnú directory authority, sync/cache SLA a leaver-session closure.
"""
if "### `KC-PAY-67` až `KC-PAY-70`" not in readme:
    if scenario_marker not in readme:
        raise RuntimeError("Scenario insertion marker not found")
    readme = readme.replace(scenario_marker, "\n" + scenario.rstrip() + "\n" + scenario_marker, 1)

learning = """

### MFA, WebAuthn, passkeys a step-up authentication

- rozlíšiť OTP, WebAuthn 2FA, WebAuthn Passwordless a passkey credential;
- navrhnúť exact RP ID/origin, discoverable-credential, user-verification, attestation a AAGUID policy;
- odlíšiť credential registration od použitia v current transaction;
- vysvetliť passkey mediation, fallback a recovery-code assurance;
- viazať client minimum LoA/ACR, `max_age`, `auth_time` a protected operation;
- overiť fresh, remembered, wrong-origin, UV-absent, recovery a second-device paths.

### Password policies, brute-force protection a account recovery

- odlíšiť write-time password policy, hashing authority a online brute-force state;
- rozlíšiť Keycloak-local a LDAP/AD credential authority;
- vysvetliť attack-detection status, quick-login controls a safe counter reset;
- sledovať Reset Credentials flow, action token, redirect a force-login boundary;
- uzatvoriť Keycloak, refresh/offline a application-session descendants;
- overiť old password, expired/replayed link, wrong redirect, old session a federated-user paths.

### Identity brokering

- definovať exact provider alias/configuration, external issuer+subject, broker transaction a local federated link;
- rozlíšiť external response validation od local account creation/linking;
- navrhnúť safe First Broker Login a Post Login flows;
- vysvetliť `Trust Email`, account linking, stored tokens a logout boundaries;
- používať mapper `IMPORT/FORCE/LEGACY/INHERIT` podľa attribute authority;
- overiť same-email second-provider, wrong tenant, claim removal, link/unlink a second-login paths.

### LDAP a Active Directory federation

- definovať provider component, directory endpoint, stable external ID a Keycloak storage/local user identity;
- rozlíšiť Import Users ON/OFF a Edit Mode READ_ONLY/WRITABLE/UNSYNCED;
- vysvetliť, že LDAP password sa neimportuje a directory zostáva credential authority;
- navrhnúť mapper, group/role, full/changed sync a cache-revocation contract;
- overiť provider priority, collision, bind rotation, outage, move/rename, disable/delete a stale-session behavior;
- preflightovať federated storage-ID dĺžku pre WebAuthn user handles.
"""
if "### MFA, WebAuthn, passkeys a step-up authentication" not in readme:
    readme = readme.rstrip() + learning + "\n"

README.write_text(readme.rstrip() + "\n", encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `17-keycloak-and-identity-platform`",
    "| `17-keycloak-and-identity-platform` — Keycloak and Identity Platform | 12/30 authoritative drafting | In progress | 2026-08-02 | Prvých 12 authoritative kapitol je aktívnych. Blok 9–12 uzatvára MFA/WebAuthn/passkey registration a current-transaction assurance, password/brute-force/reset recovery a session descendants, external OIDC/SAML identity brokering a account-link authority a LDAP/Active Directory storage/import/edit/sync/cache lifecycle. Incidenty `KC-PAY-67` až `KC-PAY-70` dokazujú rozdiel medzi credential existence a current use, password mutation a descendant revocation, valid external response a správny local account a directory disable/group removal a effective session/token denial. Baseline 1–8 prešiel preserve gate; nový blok 9–12 strict concept, executable-surface, subject/evidence/recovery/acceptance a navigation gate-om. README, ledger, glossary, navigation a audit sú synchronizované. Sekcia zostáva In progress; ďalší blok je 13–16: user-storage synchronization/cache, Authorization Services, token exchange/impersonation/delegated access a Admin Console/Admin REST API automation. |",
)

print("Keycloak block 09-12 validated and activated at 12/30.")
