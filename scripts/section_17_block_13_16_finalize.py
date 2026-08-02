from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "17-keycloak-and-identity-platform"
README = SECTION / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"

BLOCK_ARTICLES = {
    "user-storage-synchronization-cache-semantics.md": [
        "User Storage SPI", "ImportedUserValidation", "ImportSynchronization", "OnUserCache", "CachedUserModel"
    ],
    "authorization-services-resources-scopes-policies-permissions.md": [
        "Policy Decision Point", "Policy Enforcement Point", "permission ticket", "RPT", "Protection API"
    ],
    "token-exchange-impersonation-delegated-access.md": [
        "Standard Token Exchange V2", "Legacy Token Exchange V1", "JWT Authorization Grant", "impersonation", "actor"
    ],
    "admin-console-admin-rest-api-automation.md": [
        "Admin REST API", "realm-management", "Fine-Grained Admin Permissions", "internal client UUID", "partial import"
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

active_marker = "12. [LDAP a Active Directory federation](ldap-active-directory-federation.md)\n"
active_extension = """12. [LDAP a Active Directory federation](ldap-active-directory-federation.md)
13. [User storage, synchronization a cache semantics](user-storage-synchronization-cache-semantics.md)
14. [Authorization Services, resources, scopes, policies a permissions](authorization-services-resources-scopes-policies-permissions.md)
15. [Token exchange, impersonation a delegated access](token-exchange-impersonation-delegated-access.md)
16. [Admin Console, Admin REST API a automation](admin-console-admin-rest-api-automation.md)
"""
if active_extension not in readme:
    if active_marker not in readme:
        raise RuntimeError("Expected Section 17 active-order marker not found")
    readme = readme.replace(active_marker, active_extension, 1)

old_state = "Aktuálny authoritative stav sekcie je **12/30 · In progress**. Kapitoly 1–12 teraz pokrývajú Keycloak deployment a core identity model, OIDC/SAML clients, token projection, client a machine capabilities, authentication flows, MFA/passkeys/step-up, password a recovery controls, identity brokering a LDAP/Active Directory federation. Sekcia zatiaľ nie je `Ready for user review`; ďalší blok začína user-storage/cache semantics, Authorization Services, token exchange/delegated access a Admin API automation."
new_state = "Aktuálny authoritative stav sekcie je **16/30 · In progress**. Kapitoly 1–16 teraz pokrývajú identity/protocol/authentication/federation lifecycle-y aj user-storage/cache authority, fine-grained Authorization Services, supported token exchange/delegation boundaries a bezpečnú Admin Console/Admin REST automation. Sekcia zatiaľ nie je `Ready for user review`; ďalší blok začína events/observability, themes/localization, server hostname/reverse-proxy configuration a TLS/cookie/header hardening."
if old_state not in readme and new_state not in readme:
    raise RuntimeError("Expected Section 17 12/30 state paragraph not found")
readme = readme.replace(old_state, new_state, 1)

planned_lines = """13. User storage, synchronization a cache semantics  
14. Authorization Services, resources, scopes, policies a permissions  
15. Token exchange, impersonation a delegated access  
16. Admin Console, Admin REST API a automation  
"""
readme = readme.replace(planned_lines, "")

scenario_marker = "\n## Dominantný model sekcie\n"
scenario = """### `KC-PAY-68` — stale user-storage cache, broad authorization, exchange amplification a wrong-target automation

Atlas custom User Storage SPI provider čítal workforce identity z HR databázy a entitlement revision z oddelenej policy služby. `OnUserCache` uložil `settlement.export=true` na tridsať minút, no external mover event nevyslal Keycloak invalidation. Active user session a token preto niesli predecessor entitlement aj po authoritative removal.

Authorization Services permission pre export používala `AFFIRMATIVE` strategy nad broad role, same-tenant a fresh-authentication policies. Broad role sama vytvorila grant, zatiaľ čo PEP cache key neobsahoval tenant, resource ID ani policy generation. `settlement-orchestrator` následne exchange-nul frontend token na `settlement-api` token s broad default scopes a API ignorovalo actor/requester context.

Configuration controller sa autentizoval broad master-realm adminom. Target realm a client resolve-nul iba podľa names, po timeout-e slepo retryol mutation a potom spustil partial import do druhého realm-u. Stage aj production skončili v odlišnej partial generation, zatiaľ čo Admin Event bez representation nevysvetlil final state.

```text
stale external identity/cache/session generation
→ broad PDP strategy a incomplete PEP cache key
→ overprivileged exchange successor token
→ broad administrative actor a ambiguous target
→ timeout, blind retry a partial import
→ mixed client/policy/runtime generations
→ cross-tenant alebo duplicate settlement operation
```

Redesign pridáva authoritative external-change invalidation a bounded user cache, exact resource/scope a `UNANIMOUS` authorization graph, actor-aware target-specific exchange a operation idempotency. Administration používa scoped service account, expected realm/internal IDs, canonical plan s predecessor hashom, read-back po unknown outcome a second no-op. Recovery uzatvára provider code/config, cache, sessions/tokens, Authorization Services decisions/RPT, exchange descendants, Admin Events a business operations.
"""
if "### `KC-PAY-68`" not in readme:
    if scenario_marker not in readme:
        raise RuntimeError("Expected Section 17 scenario insertion marker not found")
    readme = readme.replace(scenario_marker, "\n" + scenario.rstrip() + "\n" + scenario_marker, 1)

learning_extension = """

### User storage, synchronization a cache semantics

- definovať exact provider component, deployed SPI JAR, external user, local/imported user a cache generation;
- rozlíšiť User Storage SPI capability interfaces a neinferovať query/write capability zo successful loginu;
- vysvetliť non-import adapter a import strategy vrátane federated supplemental state-u;
- používať `ImportedUserValidation` a `ImportSynchronization` s explicitnou cache/timestamp/deletion boundary;
- vysvetliť local invalidation cache, cache policies, `OnUserCache` a custom cached metadata;
- rolloutovať provider code/config ako pinned generation naprieč všetkými nodes;
- zachovať local emergency admin pri external-provider outage;
- overiť duplicate user, provider failure, stale cache, mixed generation, session/token a second-login paths.

### Authorization Services, resources, scopes, policies a permissions

- definovať exact resource-server client, resource ID, authorization scope, permission, policy graph a request context;
- rozlíšiť PAP, PDP, PEP a PIP a overiť application-side enforcement;
- odlíšiť OAuth scope, Keycloak client scope a Authorization Services scope;
- navrhnúť reusable role/group/time/context policies a resource/scope permissions;
- vysvetliť UNANIMOUS, AFFIRMATIVE a CONSENSUS decision strategies vrátane bypass risku;
- používať Protection API/PAT, permission tickets a RPT s explicitným custody a revocation contractom;
- verziovať export/import authorization graph a decision/PEP cache key;
- overiť wrong tenant, adjacent resource, missing context, stale RPT, PDP outage a second-request paths.

### Token exchange, impersonation a delegated access

- rozlíšiť podporovaný Standard Token Exchange V2 od deprecated Legacy V1;
- definovať requester client, subject token, target audience, requested scope a successor-token generation;
- vynútiť requester audience/capability a target least-privilege projection;
- oddeliť external-to-internal JWT Authorization Grant a internal-to-external broker token retrieval;
- rozlíšiť user subject, acting client/actor, audience a delegated permission;
- nepoužívať legacy impersonation ako default production delegation model;
- modelovať access/refresh exchange descendants a retry/business-operation idempotency;
- overiť wrong requester, wrong realm/target, excess scope, stale descendant a duplicate exchange paths.

### Admin Console, Admin REST API a automation

- definovať exact actor/authentication realm, target realm/internal ID, resource UUID a predecessor generation;
- rozlíšiť master admin, realm-management built-ins a Fine-Grained Admin Permissions;
- navrhnúť scoped service-account automation bez broad `realm-admin` a s workload-bound credentialom;
- bezpečne používať `kcadm.sh`, interné UUIDs, pagination a permission-complete inventory;
- vytvoriť canonical desired-state plan, stale-plan refusal, mutation read-back a second no-op;
- interpretovať endpoint-specific `201/204/409`, timeout a unknown outcome bez blind retry;
- reconciliovať partial import a bulk per-item results namiesto predpokladu global transactionu;
- korelovať Admin Events, target representation, runtime/session a business evidence;
- overiť wrong realm, wrong UUID, forbidden adjacent operation, timeout recovery a delete/recreate identity paths.
"""
if "### User storage, synchronization a cache semantics" not in readme:
    readme = readme.rstrip() + learning_extension + "\n"

README.write_text(readme.rstrip() + "\n", encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `17-keycloak-and-identity-platform`",
    "| `17-keycloak-and-identity-platform` — Keycloak and Identity Platform | 16/30 authoritative drafting | In progress | 2026-08-02 | Šestnásť authoritative kapitol je aktívnych. Blok 13–16 uzatvára User Storage SPI capability, import/non-import, synchronization, provider-code generation a user-cache invalidation semantics; Authorization Services resource/scope/policy/permission graph, PAP/PDP/PEP/PIP, UMA/PAT/RPT a enforcement cache; podporovaný Standard Token Exchange V2, deprecated Legacy V1, JWT Authorization Grant, actor/subject/delegation a token descendants; a Admin Console/Admin REST automation cez scoped actor, target realm/internal IDs, FGAP, canonical plan, endpoint-specific mutation semantics, Admin Events, partial import, recovery a second no-op. Connected incident `KC-PAY-68` spája stale custom cache, broad AFFIRMATIVE policy, incomplete PEP cache key, overprivileged exchange a wrong-realm blind administrative retry. Všetky štyri nové kapitoly prešli substantial prose, executable/model surface a subject/evidence/recovery/acceptance gate-om; README ordering, learning goals, ROADMAP, navigation, glossary fragment a full audit sú synchronizované. Sekcia zostáva In progress; ďalší blok 17–20 bude events/observability, themes/email/localization, server hostname/reverse-proxy configuration a TLS/truststore/cookie/header hardening. |",
)

print("Keycloak block 13-16 passed strict validation and Section 17 advanced to 16/30.")
