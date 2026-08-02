from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "17-keycloak-and-identity-platform"
README = SECTION / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"

BASELINE_ARTICLES = [
    "keycloak-architecture-and-responsibility-boundary.md",
    "realm-client-user-group-role-session.md",
    "oidc-clients-redirect-uris-scopes-pkce.md",
    "saml-clients-metadata-assertions-bindings.md",
    "tokens-claims-protocol-mappers-client-scopes.md",
    "public-confidential-and-bearer-only-clients.md",
    "service-accounts-and-machine-to-machine-authentication.md",
    "authentication-flows-executions-and-required-actions.md",
    "mfa-webauthn-passkeys-step-up-authentication.md",
    "password-policies-brute-force-protection-account-recovery.md",
    "identity-brokering.md",
    "ldap-active-directory-federation.md",
    "user-storage-synchronization-cache-semantics.md",
    "authorization-services-resources-scopes-policies-permissions.md",
    "token-exchange-impersonation-delegated-access.md",
    "admin-console-admin-rest-api-automation.md",
    "events-audit-metrics-observability.md",
    "themes-email-templates-localization.md",
    "keycloak-server-configuration-hostname-reverse-proxy.md",
    "tls-truststores-cookies-headers-production-hardening.md",
    "database-transactions-connection-pools-schema-lifecycle.md",
    "infinispan-caches-clustering-session-behavior.md",
    "keycloak-operator-kubernetes-deployment.md",
    "high-availability-multi-az-multi-cluster-trade-offs.md",
]

BLOCK_ARTICLES = {
    "backup-restore-realm-import-export-disaster-recovery.md": [
        "pitr", "realm export", "persisted sessions", "všetky nodes", "override", "bootstrap-admin", "kc-pay-77"
    ],
    "upgrades-migration-guides-rollback-boundaries.md": [
        "migration guide", "mixed-version", "schema", "provider", "theme", "rollback axes", "kc-pay-78"
    ],
    "custom-providers-spi-extension-lifecycle.md": [
        "no sandbox", "single classloader", "providerfactory", "meta-inf/services", "transaction", "custom rest", "kc-pay-79"
    ],
    "securing-apis-microservices-mcp-servers.md": [
        "token type", "audience", "azp", "local authorization", "rfc 8707", "2025-03-26", "partially supported", "cimd", "kc-pay-80"
    ],
}

SEMANTIC_GROUPS = [
    ("subject", "identity", "generation"),
    ("evidence", "dôkaz", "preukazuje", "ukazuje", "potvrdzuje", "verdict"),
    ("recovery", "obnova", "náprava", "revocation", "containment", "restore", "rollback"),
    ("acceptance", "positive", "forbidden", "zakázan", "second-"),
]


def validate_article(path: Path, *, minimum_words: int, minimum_fences: int) -> str:
    if not path.exists():
        raise RuntimeError(f"Missing authoritative chapter: {path.name}")
    text = path.read_text(encoding="utf-8")
    words = len(text.split())
    fences = text.count("```")
    if words < minimum_words:
        raise RuntimeError(f"{path.name} is unexpectedly short: {words}<{minimum_words} words")
    if fences < minimum_fences:
        raise RuntimeError(f"{path.name} has insufficient executable/model surface: {fences}<{minimum_fences} fences")
    return text


def replace_prefixed_line(path: Path, prefix: str, replacement: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [index for index, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one line starting with {prefix!r} in {path}, found {len(matches)}")
    lines[matches[0]] = replacement
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


for name in BASELINE_ARTICLES:
    validate_article(SECTION / name, minimum_words=850, minimum_fences=4)

for name, concepts in BLOCK_ARTICLES.items():
    text = validate_article(SECTION / name, minimum_words=1900, minimum_fences=10)
    lowered = text.lower()
    missing_concepts = [concept for concept in concepts if concept not in lowered]
    if missing_concepts:
        raise RuntimeError(f"{name} is missing required Keycloak concepts: {missing_concepts}")
    missing_groups = [group for group in SEMANTIC_GROUPS if not any(token in lowered for token in group)]
    if missing_groups:
        raise RuntimeError(f"{name} lacks subject/evidence/recovery/acceptance language: {missing_groups}")

readme = README.read_text(encoding="utf-8")

active_marker = "24. [High availability, multi-AZ a multi-cluster trade-offs](high-availability-multi-az-multi-cluster-trade-offs.md)\n"
active_extension = """24. [High availability, multi-AZ a multi-cluster trade-offs](high-availability-multi-az-multi-cluster-trade-offs.md)
25. [Backup, restore, realm import/export a disaster recovery](backup-restore-realm-import-export-disaster-recovery.md)
26. [Upgrades, migration guides a rollback boundaries](upgrades-migration-guides-rollback-boundaries.md)
27. [Custom providers, SPI a extension lifecycle](custom-providers-spi-extension-lifecycle.md)
28. [Securing APIs, microservices a MCP servers cez Keycloak](securing-apis-microservices-mcp-servers.md)
"""
if active_extension not in readme:
    if active_marker not in readme:
        raise RuntimeError("Expected Section 17 active-order marker not found")
    readme = readme.replace(active_marker, active_extension, 1)

state_prefix = "Aktuálny authoritative stav sekcie je **"
state_lines = [line for line in readme.splitlines() if line.startswith(state_prefix)]
if len(state_lines) != 1:
    raise RuntimeError(f"Expected one Section 17 state paragraph, found {len(state_lines)}")
new_state = (
    "Aktuálny authoritative stav sekcie je **28/30 · In progress**. Kapitoly 1–28 teraz pokrývajú identity, protocol, authentication, federation, authorization, administration, edge hardening, database/cache/Operator/HA lifecycle-y aj database/PITR a realm-export recovery, version/schema/provider/theme upgrade a rollback boundaries, trusted custom SPI lifecycle a resource-server/API/microservice/MCP enforcement. Sekcia zatiaľ nie je `Ready for user review`; posledný blok tvorí performance, sizing a load testing spolu s end-to-end Keycloak troubleshootingom."
)
readme = readme.replace(state_lines[0], new_state, 1)

planned_lines = """25. Backup, restore, realm import/export a disaster recovery  
26. Upgrades, migration guides a rollback boundaries  
27. Custom providers, SPI a extension lifecycle  
28. Securing APIs, microservices a MCP servers cez Keycloak  
"""
readme = readme.replace(planned_lines, "")

scenario_marker = "\n## Dominantný model sekcie\n"
scenario = """### `KC-PAY-77` až `KC-PAY-80` — incomplete recovery, upgrade, extension a resource-server authority

Final platform-security blok rozširuje connected settlement incident o recovery a consumer boundaries. Atlas považoval realm export za kompletný backup, importoval ho nad stale running clusterom a po point-in-time návrate database znovu prijal predecessor session/revocation state. Upgrade potom zmenil schema, provider API a passkey theme, ale rollback vrátil iba image. Custom provider bežal bez sandboxu v shared classloaderi, držal unbounded queue a publikoval custom REST endpoint bez explicitnej audience a admin permission policy.

Na resource-server strane gateway validoval iba JWT signature a expiry, API dôverovalo spoofable identity headeru a role-only policy neviazala tenant/resource. MCP server akceptoval broad `mcp:tools` scope bez exact audience a tool policy a bol nesprávne označený ako plne compliant s MCP 2025-11-25, hoci Keycloak 26.7 nespracúva RFC 8707 `resource` parameter.

```text
logical export treated as full DR
+ partial binary-only rollback
+ privileged unsandboxed provider without lifecycle controls
+ signature-only API/MCP enforcement
→ recovered alebo upgraded Keycloak vyzerá green
→ session, extension alebo downstream authorization zostáva unsafe
```

Recovery používa database/PITR plus immutable runtime artifacts a isolated restore; explicitný migration-guide/schema/provider/theme a rollback-axis contract; signed, rebuilt, bounded a authorized SPI artifacts; a per-service issuer/token-type/audience/caller plus local tenant/resource/action enforcement. MCP novšie profiles zostávajú označené ako partial workaround, kým authorization server neposkytne native RFC 8707 semantics. Closure vyžaduje second restore, second rollout, second provider version a cross-service/cross-tenant/MCP negative tests.
"""
if "### `KC-PAY-77` až `KC-PAY-80`" not in readme:
    if scenario_marker not in readme:
        raise RuntimeError("Expected Section 17 dominant-model marker not found")
    readme = readme.replace(scenario_marker, "\n" + scenario.rstrip() + "\n" + scenario_marker, 1)

learning_extension = """

### Backup, restore, realm import/export a disaster recovery

- rozlíšiť transaction-consistent database/PITR backup, realm CLI export a Admin Console partial export;
- evidovať export exclusions vrátane events, persisted sessions, workflow state a revoked tokens;
- zastaviť všetky nodes pre consistent export a override import a používať isolated immutable Job image;
- definovať exact backup timestamp, schema/image/secret/key generation, encryption a retention;
- izolovať restore od production SMTP, callbacks, routes a external effects;
- reconciliovať signing keys, sessions, offline tokens, revocation a downstream application sessions po point-in-time návrate;
- používať temporary admin iba ako auditovaný bounded recovery mechanismus a následne ho odstrániť;
- overiť checksum, decrypt, schema, protocol, business, failback a second-restore paths.

### Upgrades, migration guides a rollback boundaries

- inventarizovať predecessor a successor server, schema, provider, theme, feature, configuration a client-library generations;
- reviewovať migration guide pre každú preskočenú version boundary;
- buildnúť nový immutable optimized image namiesto in-place upgrade-u;
- určiť jediného schema writera, bounded mixed-version window a transaction setup timeout;
- rebuildnúť custom providers a diffnúť copied themes proti successor baseline-u;
- testovať existing sessions, tokens, metadata, failover a full protocol/business journey matrix;
- rozlíšiť binary, schema, provider/theme, configuration, realm data a client rollback axes;
- zvoliť supported rollback/restore alebo immutable forward fix pred irreversible decision pointom.

### Custom providers, SPI a extension lifecycle

- považovať provider JAR za fully trusted server code bez sandboxu a so shared classloaderom;
- fixovať exact SPI/provider ID, Keycloak target, source, dependency, descriptor, registry a image generation;
- správne oddeliť ProviderFactory shared lifecycle od request/session-scoped Provider state;
- registrovať services cez `META-INF/services` a buildnúť optimized immutable image;
- navrhnúť transaction, rollback a external-effect delivery/idempotency semantics;
- explicitne chrániť custom REST endpoints, JPA schema, User Storage, authenticators a token mappers;
- riadiť dependency conflicts, threads/queues, redaction, supply chain, upgrade a uninstall;
- overiť concurrency, backpressure, node failure, second transaction a target-next-version behavior.

### Securing APIs, microservices a MCP servers cez Keycloak

- validovať access-token issuer, signature, time, token type, audience a caller/`azp` v každom resource serveri;
- odmietnuť ID/refresh tokens a dokončiť tenant/resource/action authorization lokálne;
- rozlíšiť gateway coarse enforcement od service PEP a blokovať spoofed/direct paths;
- navrhnúť bounded JWKS refresh, introspection, revocation freshness a sender constraints;
- používať service-specific M2M audiences a narrowed token exchange s actor contextom;
- mapovať MCP protected-resource metadata, PKCE, registration a exact tool/resource/prompt policy;
- uvádzať MCP 2025-03-26 ako supported a 2025-06-18/2025-11-25 iba ako partial bez RFC 8707 Resource Indicators;
- chrániť CIMD/DCR metadata fetch pred SSRF a overiť cross-service, cross-tenant a duplicate-tool paths.
"""
if "### Backup, restore, realm import/export a disaster recovery" not in readme:
    readme = readme.rstrip() + learning_extension + "\n"

README.write_text(readme.rstrip() + "\n", encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `17-keycloak-and-identity-platform`",
    "| `17-keycloak-and-identity-platform` — Keycloak and Identity Platform | 28/30 authoritative drafting | In progress | 2026-08-02 | Dvadsaťosem authoritative kapitol je aktívnych. Blok 25–28 uzatvára transaction-consistent database/PITR backup, realm CLI export/import exclusions a all-nodes-stopped consistency, partial online export/import, isolated restore, keys/sessions/revocation reconciliation a temporary-admin cleanup; migration-guide chain, immutable successor image, schema ownership, bounded mixed-version window, feature/provider/theme/client compatibility a multidimensional rollback/forward-fix boundaries; fully trusted unsandboxed SPI/provider lifecycle so shared classloaderom, ProviderFactory/request scope, service-loader registration, transaction/external-effect behavior, custom REST/JPA/storage/authenticator/mapper/event-listener security, supply chain a upgrade/uninstall; a resource-server/API/microservice/MCP enforcement cez issuer/signature/time/token-type/audience/caller validation, local tenant/resource/action policy, gateway/service split, M2M/delegation a exact MCP profile status, RFC 8707 gap, Audience-mapper workaround, CIMD/DCR/SSRF a tool-level authorization. Connected incidents `KC-PAY-77` až `KC-PAY-80` spájajú incomplete logical backup, unsafe point-in-time descendants, partial image-only rollback, provider classloader/endpoint failures a signature-only API/MCP authorization. Kapitoly 1–24 prešli preserve/executable checkom a blok 25–28 strict concept, substantial prose, executable/model surface a subject/evidence/recovery/acceptance gate-om. README ordering, learning goals, ROADMAP, navigation, glossary a full audit sú synchronizované. Sekcia zostáva In progress; posledný blok 29–30 bude performance/sizing/load testing a Keycloak troubleshooting. Reálne backupy/restores, migrations, provider binaries, APIs, MCP clients/servers a business operations neboli týmto documentation workflowom vykonané. |",
)

print("Keycloak block 25-28 passed the 28-chapter gate and was activated in README and ledger.")
