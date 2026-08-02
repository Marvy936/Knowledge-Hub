from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "17-keycloak-and-identity-platform"
README = SECTION / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"

BLOCK_ARTICLES = {
    "mfa-webauthn-passkeys-step-up-authentication.md": [
        "WebAuthn", "passkey", "recovery code", "step-up", "ACR", "RP ID"
    ],
    "password-policies-brute-force-protection-account-recovery.md": [
        "password policy", "brute-force", "Reset Credentials", "action token", "offline token"
    ],
    "identity-brokering.md": [
        "First Broker Login", "Trust Email", "AutoLink", "Store Tokens", "Post Login Flow"
    ],
    "ldap-active-directory-federation.md": [
        "Import Users", "READ_ONLY", "WRITABLE", "UNSYNCED", "objectGUID", "changed-users sync"
    ],
}

SEMANTIC_GROUPS = [
    ("subject", "identity", "generation"),
    ("evidence", "dôkaz", "preukazuje", "ukazuje", "potvrdzuje", "verdict"),
    ("recovery", "obnova", "náprava", "revocation"),
    ("acceptance", "positive path", "forbidden path", "zakázan", "prijatie", "akcept"),
]


def replace_prefixed_line(path: Path, prefix: str, replacement: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [index for index, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one line starting with {prefix!r} in {path}, found {len(matches)}")
    lines[matches[0]] = replacement
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


for name, concepts in BLOCK_ARTICLES.items():
    path = SECTION / name
    if not path.exists():
        raise RuntimeError(f"Missing authoritative chapter: {name}")
    text = path.read_text(encoding="utf-8")
    words = len(text.split())
    fences = text.count("```")
    if words < 1600:
        raise RuntimeError(f"{name} is unexpectedly short: {words}<1600 words")
    if fences < 8:
        raise RuntimeError(f"{name} has insufficient executable/model surface: {fences}<8 fences")
    lowered = text.lower()
    missing_concepts = [concept for concept in concepts if concept.lower() not in lowered]
    if missing_concepts:
        raise RuntimeError(f"{name} is missing required Keycloak concepts: {missing_concepts}")
    missing_groups = [group for group in SEMANTIC_GROUPS if not any(token in lowered for token in group)]
    if missing_groups:
        raise RuntimeError(f"{name} lacks subject/evidence/recovery/acceptance language: {missing_groups}")

readme = README.read_text(encoding="utf-8")

active_marker = "8. [Authentication flows, executions a required actions](authentication-flows-executions-and-required-actions.md)\n"
active_extension = """8. [Authentication flows, executions a required actions](authentication-flows-executions-and-required-actions.md)
9. [MFA, WebAuthn, passkeys a step-up authentication](mfa-webauthn-passkeys-step-up-authentication.md)
10. [Password policies, brute-force protection a account recovery](password-policies-brute-force-protection-account-recovery.md)
11. [Identity brokering](identity-brokering.md)
12. [LDAP a Active Directory federation](ldap-active-directory-federation.md)
"""
if active_extension not in readme:
    if active_marker not in readme:
        raise RuntimeError("Expected Section 17 active-order marker not found")
    readme = readme.replace(active_marker, active_extension, 1)

old_state = "Aktuálny authoritative stav sekcie je **8/30 · In progress**. Kapitoly 1–8 tvoria prvý kompletný identity, protocol, token-projection, client-capability, machine-identity a authentication-transaction blok. Sekcia zatiaľ nie je `Ready for user review`; ďalší blok začína MFA, credential recovery, brokering a federation lifecycle-om."
new_state = "Aktuálny authoritative stav sekcie je **12/30 · In progress**. Kapitoly 1–12 teraz pokrývajú Keycloak deployment a core identity model, OIDC/SAML clients, token projection, client a machine capabilities, authentication flows, MFA/passkeys/step-up, password a recovery controls, identity brokering a LDAP/Active Directory federation. Sekcia zatiaľ nie je `Ready for user review`; ďalší blok začína user-storage/cache semantics, Authorization Services, token exchange/delegated access a Admin API automation."
if old_state not in readme and new_state not in readme:
    raise RuntimeError("Expected Section 17 8/30 state paragraph not found")
readme = readme.replace(old_state, new_state, 1)

planned_lines = """9. MFA, WebAuthn, passkeys a step-up authentication  
10. Password policies, brute-force protection a account recovery  
11. Identity brokering  
12. LDAP a Active Directory federation  
"""
readme = readme.replace(planned_lines, "")

scenario_marker = "\n## Dominantný model sekcie\n"
scenario = """### `KC-PAY-67` — assurance downgrade, mailbox recovery, unsafe broker link a stale directory privilege

Atlas zaviedol passkeys pre privileged settlement clienta, ale ACR `gold` bol omylom namapovaný na nízku authentication level. Remembered brokered SSO session preto získala `acr=gold` bez fresh WebAuthn challenge. Recovery flow dôveroval verified emailu synchronizovanému z workforce directory; kompromitovaná alebo recyklovaná mailbox adresa mohla dokončiť password reset a pridať nový passkey.

Partner OIDC provider mal `Trust Email`, `FORCE` mappers a unsafe AutoLink. Nový upstream subject s recyklovaným emailom sa spojil so starým local userom. Súčasne Active Directory changed-users sync nezachytil intended nested-group removal a Keycloak cache/local group mapping ponechali privilege. Password alebo credential reset nezrušil offline token ani local application session.

```text
stale alebo low-assurance upstream/directory identity state
→ incorrect ACR/LoA alebo mapper/sync result
→ unsafe local account link alebo credential recovery
→ stale Keycloak group/role/session descendants
→ protocol-valid privileged token
→ settlement export alebo administration operation
```

Redesign viaže passkeys na exact RP/origin, required user verification a correct ACR-to-LoA mapping; credential management a recovery vyžadujú adequate current assurance a complete session/token closure. Broker linking používa stable external issuer+subject a verified existing-account proof namiesto email AutoLinku. LDAP federation používa stable `objectGUID`, explicitný mapper ownership, full/changed sync evidence, cache invalidation, local emergency admin a fresh-login/offboarding tests. Recovery uzatvára old credential, old broker subject, stale group mapping, offline/application sessions a second-login paths.
"""
if "### `KC-PAY-67`" not in readme:
    if scenario_marker not in readme:
        raise RuntimeError("Expected Section 17 scenario insertion marker not found")
    readme = readme.replace(scenario_marker, "\n" + scenario.rstrip() + "\n" + scenario_marker, 1)

learning_extension = """

### MFA, WebAuthn, passkeys a step-up authentication

- rozlíšiť TOTP/HOTP, WebAuthn druhý faktor, passwordless a loginless discoverable passkey;
- definovať exact RP ID, origin, credential, policy, flow, user-session a client subject;
- vysvetliť WebAuthn registration a authentication ceremony vrátane challenge, signature, user presence a user verification;
- navrhnúť passkey mediation, fallback a recovery bez silent assurance downgrade-u;
- rozlíšiť attestation, AAGUID, authenticator class a privacy/usability trade-off;
- mapovať OIDC ACR alebo SAML authentication context na skutočne dosiahnutú Keycloak LoA;
- chrániť add/delete credential operations current step-upom a auditom;
- overiť wrong origin/RP, UV=false, stale SSO, used recovery code, second client a second-login paths.

### Password policies, brute-force protection a account recovery

- definovať password credential ownera, realm policy, hashing generation a LDAP/external boundary;
- vysvetliť composition rules, password history/expiry a migration existujúcich credentials;
- modelovať brute-force failure state, quick-login threshold, temporary/permanent/mixed lockout a DoS consequence;
- používať Attack Detection read-back a controlled unlock namiesto restartu alebo bulk clear-u;
- vysvetliť Reset Credentials flow, action-token issue/delivery/replay a account-enumeration boundary;
- oddeliť password mutation od Keycloak, offline-token a application-session descendants;
- navrhnúť mailbox/helpdesk recovery s adequate identity proofom;
- overiť old password, expired/replayed link, lockout DoS, old token a second-login paths.

### Identity brokering

- definovať exact external IdP alias/configuration, issuer/entity, external subject, local user a federated-link subject;
- vysvetliť OIDC/SAML upstream validation a oddeliť ju od local account correlation;
- navrhnúť First Broker Login create/link/verify flow bez unsafe AutoLinku;
- používať `Trust Email` iba ako explicitnú delegáciu email-verification authority, nie person identity;
- rozlíšiť IMPORT/FORCE/INHERIT mapper sync modes a ich stale/overwrite behavior;
- minimalizovať stored upstream token custody a read-token permission;
- vynútiť Post Login Flow step-up pre insufficient upstream assurance;
- overiť same-email/different-subject, wrong issuer, stale link, unlink/relogin a stored-token paths.

### LDAP a Active Directory federation

- definovať exact provider, directory namespace, secure connection, bind credential, stable UUID, mapper a sync generation;
- rozlíšiť Import Users ON/OFF a local versus transient user-state consequences;
- vysvetliť READ_ONLY, WRITABLE a UNSYNCED field/password ownership;
- používať multiple LDAP URLs ako sequential replica failover, nie identity-provider load balancing;
- modelovať on-demand, full a changed-users sync vrátane missed deletion/group-change risks;
- vysvetliť LDAP mappers, AD `objectGUID`, `sAMAccountName`, UPN, nested groups a account-control semantics;
- oddeliť directory disable/password state, Keycloak cache/session a token descendants;
- overiť first-server-down, wrong UUID, provider failure, removed group, local emergency admin a leaver paths.
"""
if "### MFA, WebAuthn, passkeys a step-up authentication" not in readme:
    readme = readme.rstrip() + learning_extension + "\n"

README.write_text(readme.rstrip() + "\n", encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `17-keycloak-and-identity-platform`",
    "| `17-keycloak-and-identity-platform` — Keycloak and Identity Platform | 12/30 authoritative drafting | In progress | 2026-08-02 | Dvanásť authoritative kapitol je aktívnych. Blok 9–12 uzatvára MFA/TOTP/WebAuthn/passkey credential lifecycle, ACR-to-LoA step-up a recovery-code paths; password-policy/hash authority, brute-force state machine, reset action tokens a complete session descendants; identity brokering od upstream protocol validation cez First/Post Broker Login, Trust Email, mapper sync a secure account linking; a LDAP/Active Directory federation cez secure provider connection, stable UUID, Import Users/Edit Mode ownership, mapper graph, full/changed sync, replica failover, cache a leaver closure. Connected incident `KC-PAY-67` spája incorrect assurance mapping, mailbox recovery, recycled-email AutoLink, stale AD group mapping a retained offline/application sessions. Všetky štyri nové kapitoly prešli substantial prose, executable/model surface a subject/evidence/recovery/acceptance gate-om; README ordering, learning goals, ROADMAP, navigation, glossary fragment a full audit sú synchronizované. Sekcia zostáva In progress; ďalší blok 13–16 bude user storage/cache semantics, Authorization Services, token exchange/delegated access a Admin Console/Admin REST automation. |",
)

print("Keycloak block 09-12 passed strict validation and Section 17 advanced to 12/30.")
