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
    "backup-restore-realm-import-export-disaster-recovery.md",
    "upgrades-migration-guides-rollback-boundaries.md",
    "custom-providers-spi-extension-lifecycle.md",
    "securing-apis-microservices-mcp-servers.md",
]

BLOCK_ARTICLES = {
    "keycloak-performance-sizing-load-testing.md": [
        "password-based logins", "150 %", "1250 mb", "agroal_awaiting_count", "time_wait", "cold", "failover", "kc-pay-81"
    ],
    "keycloak-troubleshooting.md": [
        "competing hypotheses", "authoritative read-back", "invalid_client", "jwks", "agroal_awaiting_count", "operator", "mcp", "kc-pay-82"
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
    text = validate_article(SECTION / name, minimum_words=2600, minimum_fences=14)
    lowered = text.lower()
    missing_concepts = [concept for concept in concepts if concept not in lowered]
    if missing_concepts:
        raise RuntimeError(f"{name} is missing required Keycloak concepts: {missing_concepts}")
    missing_groups = [group for group in SEMANTIC_GROUPS if not any(token in lowered for token in group)]
    if missing_groups:
        raise RuntimeError(f"{name} lacks subject/evidence/recovery/acceptance language: {missing_groups}")

readme = README.read_text(encoding="utf-8")

active_marker = "28. [Securing APIs, microservices a MCP servers cez Keycloak](securing-apis-microservices-mcp-servers.md)\n"
active_extension = """28. [Securing APIs, microservices a MCP servers cez Keycloak](securing-apis-microservices-mcp-servers.md)
29. [Keycloak performance, sizing a load testing](keycloak-performance-sizing-load-testing.md)
30. [Keycloak troubleshooting](keycloak-troubleshooting.md)
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
    "Aktuálny authoritative stav sekcie je **30/30 · Ready for user review**. Všetkých tridsať authoritative kapitol prešlo preserve-first chapter inventory a nový blok 29–30 strict substantial-prose, executable/model-surface a subject/evidence/recovery/acceptance gate-om. Sekcia pokrýva kompletný Keycloak lifecycle od realm/client/user/session a OIDC/SAML cez token projection, authentication, MFA, federation, Authorization Services, administration, observability, themes, hostname/TLS, database/cache/Operator/HA, DR/upgrades/SPIs, API/MCP enforcement až po performance a evidence-first troubleshooting. Repository validation nepredstavuje runtime `Verified`, production `Stable` ani user `Accepted`; reálne Keycloak deploymenty, dependencies, failover, backup/restore, load tests a business journeys zostávajú samostatnou acceptance hranicou."
)
readme = readme.replace(state_lines[0], new_state, 1)

planned_block = """## Plánované pokračovanie

29. Keycloak performance, sizing a load testing  
30. Keycloak troubleshooting

"""
readme = readme.replace(planned_block, "")

scenario_marker = "\n## Dominantný model sekcie\n"
scenario = """### `KC-PAY-81` a `KC-PAY-82` — false capacity verdict a restart-driven troubleshooting

Záverečný blok spája capacity a incident reasoning. Atlas dimenzoval cluster podľa aggregate RPS z warm refresh-only testu, ignoroval password hashing, cold cache po rollout-e, concurrently used client cardinality, database pool amplification a load-generator `TIME_WAIT` limit. Production spike preto vyvolal CPU throttling, database reads, HPA scale-out a ďalšie connection pressure, hoci pôvodný benchmark vyzeral stabilne.

Následný login-loop incident mal viac nezávislých príčin: jedna proxy cohort posielala wrong forwarded port, successor theme používala predecessor WebAuthn JavaScript, BFF zmenil cookie domain a API token mapper zmenil claim type. Restart všetkých Pods dočasne presunul traffic a vymazal authentication-session/cache evidence, preto bol restart nesprávne označený za recovery.

```text
aggregate warm-only benchmark bez generator proof
+ missing failure/cold-state headroom
+ generic browser symptom cez viac authority layers
+ restart before evidence/read-back
→ false capacity a root-cause verdict
→ recurring overload alebo identity journey failure
```

Final model začína workload mixom, SLO, datasetom a exact release/topology generation, meria Keycloak/JVM/database/cache/load-generator saturation a testuje spike, soak a failure recovery. Troubleshooting začína exact subjectom, layer mapou, competing hypotheses a read-only evidence; mutation je bounded, authoritative read-back oddeľuje configured/loaded/live/business state a closure vyžaduje positive, recovery, forbidden a second-journey testy bez restart workaroundu.
"""
if "### `KC-PAY-81` a `KC-PAY-82`" not in readme:
    if scenario_marker not in readme:
        raise RuntimeError("Expected Section 17 dominant-model marker not found")
    readme = readme.replace(scenario_marker, "\n" + scenario.rstrip() + "\n" + scenario_marker, 1)

learning_extension = """

### Keycloak performance, sizing a load testing

- odvodiť capacity z exact password, refresh, client-credentials a ďalšieho journey mixu, nie aggregate HTTP RPS;
- používať current official CPU/memory/database čísla iba ako starting model a potvrdiť ich vlastným testom;
- fixovať hashing, JDK/CPU architecture, dataset, sessions/caches, database, topology, providers a load-generator generation;
- rozpočítať CPU headroom, container heap/non-heap memory, global database pool a cache cardinality;
- rozlíšiť cold, warming, steady, rolling, spike, stress, soak a failure phases;
- dokázať, že load generator doručil intended arrival rate bez CPU, ports alebo `TIME_WAIT` saturation;
- korelovať Keycloak, JVM, Agroal, cache/JGroups, database, load-balancer a generator metrics;
- meniť jednu axis, rerun-nuť identical workload a overiť survivor capacity aj second steady phase.

### Keycloak troubleshooting

- definovať exact deployment/realm/client/user/workload/session/token/request/business subject a affected population;
- mapovať symptom cez DNS/TLS, proxy/hostname, process, DB/cache/dependencies, realm/flow, protocol/token, API authorization a business layer;
- vytvoriť competing hypotheses s evidence, ktoré ich môže potvrdiť aj vyvrátiť;
- zachovať first-response evidence pred restartom, cache clearom alebo broad mutation;
- odlíšiť configured, loaded, live a business-effective state cez authoritative read-back;
- diagnostikovať OIDC/SAML, sessions, MFA/passkeys, required actions, brokering, LDAP, DB/cache/Operator, performance, providers, API/MCP a restore/upgrade paths;
- používať bounded containment a one-axis repair namiesto security-weakening workaroundov;
- uzavrieť incident positive, recovery, forbidden a second node/proxy/client/session/operation testom a postmortemom.

## Section completion boundary

Section 17 je dokumentačne uzavretá až po chapter-by-chapter inventory 30/30, synchronizovanom README/ROADMAP/glossary/navigation/ledger/audite a nulovej Section 17 critical/high queue. Tento gate overuje connected prose, executable examples, exact identity/authority/evidence/recovery boundaries a preserve-first consistency. Nevykonáva živý Keycloak cluster, database, LDAP/AD, IdP, SMTP, Infinispan, Operator, proxy, certificates, MCP clients/servers, load generators ani business applications. Preto je výsledok `Ready for user review`, nie runtime `Verified`, production `Stable` alebo user `Accepted`.
"""
if "### Keycloak performance, sizing a load testing" not in readme:
    readme = readme.rstrip() + learning_extension + "\n"

README.write_text(readme.rstrip() + "\n", encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `17-keycloak-and-identity-platform`",
    "| `17-keycloak-and-identity-platform` — Keycloak and Identity Platform | 30/30 authoritative drafting and section closeout | Ready for user review | 2026-08-02 | Všetkých 30 authoritative kapitol je aktívnych a chapter-by-chapter inventory je uzavretý. Finálny blok 29–30 pridáva journey-based performance sizing a reproducible load testing: official CPU/memory/database starting points, password hashing, container heap/non-heap, cache/client cardinality, global DB pool, thread/load-shedding, HPA, deterministic datasets, Keycloak Benchmark/Gatling, load-generator capacity, cold/warm/spike/stress/soak/failure phases, cross-layer metrics, one-axis tuning a survivor-capacity acceptance; a kompletný evidence-first troubleshooting lifecycle od DNS/TLS/proxy/hostname cez process/Operator, database/cache/cluster, OIDC/SAML/sessions/MFA/required actions/brokering/LDAP, tokens/JWKS/API/MCP, providers/themes/performance až po restore/upgrade. Connected incidents `KC-PAY-81` a `KC-PAY-82` spájajú false warm-only capacity verdict, generator saturation, multi-layer login loop a restart-driven evidence loss. Kapitoly 1–28 prešli preserve/executable checkom, kapitoly 29–30 strict domain, substantial prose, executable/model surface a subject/evidence/recovery/acceptance gate-om. README ordering, learning goals, ROADMAP, navigation, glossary a full audit sú synchronizované; Section 17 má nulovú critical/high queue. Reálne Keycloak deploymenty, load tests, dependencies, failover a business journeys neboli vykonané, preto je sekcia Ready for user review, nie runtime Verified, Stable alebo Accepted. |",
)

print("Keycloak chapters 29-30 passed the final gate and Section 17 was closed at 30/30 Ready for user review.")
