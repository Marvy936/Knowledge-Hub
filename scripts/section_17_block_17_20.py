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
]

BLOCK_ARTICLES = {
    "events-audit-metrics-observability.md": [
        "user events", "admin events", "event listener", "metrics", "management interface", "cardinality", "kc-pay-69"
    ],
    "themes-email-templates-localization.md": [
        "freemarker", "parent", "email theme", "action token", "localization", "placeholder", "kc-pay-70"
    ],
    "keycloak-server-configuration-hostname-reverse-proxy.md": [
        "hostname-admin", "hostname-backchannel", "proxy-headers", "proxy-trusted-addresses", "management", "proxy protocol", "kc-pay-71"
    ],
    "tls-truststores-cookies-headers-production-hardening.md": [
        "truststore", "secure", "httponly", "samesite", "content-security-policy", "certificate rotation", "kc-pay-72"
    ],
}

SEMANTIC_GROUPS = [
    ("subject", "identity", "generation"),
    ("evidence", "dôkaz", "preukazuje", "ukazuje", "potvrdzuje", "verdict"),
    ("recovery", "obnova", "náprava", "revocation", "containment"),
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
    text = validate_article(SECTION / name, minimum_words=1500, minimum_fences=8)
    lowered = text.lower()
    missing_concepts = [concept for concept in concepts if concept not in lowered]
    if missing_concepts:
        raise RuntimeError(f"{name} is missing required Keycloak concepts: {missing_concepts}")
    missing_groups = [group for group in SEMANTIC_GROUPS if not any(token in lowered for token in group)]
    if missing_groups:
        raise RuntimeError(f"{name} lacks subject/evidence/recovery/acceptance language: {missing_groups}")

readme = README.read_text(encoding="utf-8")

active_marker = "16. [Admin Console, Admin REST API a automation](admin-console-admin-rest-api-automation.md)\n"
active_extension = """16. [Admin Console, Admin REST API a automation](admin-console-admin-rest-api-automation.md)
17. [Events, audit, metrics a observability](events-audit-metrics-observability.md)
18. [Themes, email templates a localization](themes-email-templates-localization.md)
19. [Keycloak server configuration, hostname a reverse proxy](keycloak-server-configuration-hostname-reverse-proxy.md)
20. [TLS, truststores, cookies, headers a production hardening](tls-truststores-cookies-headers-production-hardening.md)
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
    "Aktuálny authoritative stav sekcie je **20/30 · In progress**. Kapitoly 1–20 teraz pokrývajú identity, protocol, authentication, federation, authorization a administration lifecycle-y aj operational evidence, theme/email/localization artifacts, canonical hostname a reverse-proxy authority a inbound/outbound TLS, browser-session a HTTP hardening. Sekcia zatiaľ nie je `Ready for user review`; ďalší blok začína database/schema lifecycle-om, Infinispan clusteringom, Keycloak Operatorom a high-availability topology." 
)
readme = readme.replace(state_lines[0], new_state, 1)

planned_lines = """17. Events, audit, metrics a observability  
18. Themes, email templates a localization  
19. Keycloak server configuration, hostname a reverse proxy  
20. TLS, truststores, cookies, headers a production hardening  
"""
readme = readme.replace(planned_lines, "")

scenario_marker = "\n## Dominantný model sekcie\n"
scenario = """### `KC-PAY-69` až `KC-PAY-72` — incomplete evidence, stale UI artifact a broken network trust

Operational blok rozširuje connected settlement incident o štyri vrstvy. Jeden Pod po reštarte resetoval event counters a druhý prestal byť scrapovaný, zatiaľ čo custom event listener strácal Admin Events pri broker backpressure. Dashboard preto vyzeral zdravo, hoci audit population bola neúplná. Custom theme zároveň kopírovala predecessor passkey template, hardcodovala starý hostname do HTML emailu a mala rozdielnu expiry semantics medzi locales.

Server nemal explicitnú frontend hostname authority, dôveroval broad VPC proxy range-u a verejný ingress publikoval aj `/admin/`. Spoofed forwarding headers ovplyvnili action-link origin a nesprávny forwarded port rozbil callbacks. Re-encrypt backend navyše validoval broad corporate CA bez exact hostname/SNI contractu; outbound truststore dôveroval širšej CA hierarchy než potrebovali konkrétne IdP/LDAP dependencies. Proxy kvôli theme compatibility oslabila CSP a scheme trust ovplyvnil cookie behavior.

```text
partial events/metrics population
+ stale theme/email/localization generation
+ dynamic hostname a broad proxy trust
+ broad TLS CA/header/cookie policy
→ protocol-valid, ale neúplne pozorovaný a nesprávne ohraničený identity journey
→ misleading incident verdict alebo session compromise path
```

Recovery uzatvára source-generated, delivered, durable a queryable evidence; immutable minimal theme s locale/action-link acceptance; explicitný hostname, admin/management route isolation a exact trusted proxy sources; a service-specific TLS/SNI/truststore, cookie a security-header policy. Closure vyžaduje second-node, second-locale, second-proxy, second-certificate a second-session testy.
"""
if "### `KC-PAY-69` až `KC-PAY-72`" not in readme:
    if scenario_marker not in readme:
        raise RuntimeError("Expected Section 17 dominant-model marker not found")
    readme = readme.replace(scenario_marker, "\n" + scenario.rstrip() + "\n" + scenario_marker, 1)

learning_extension = """

### Events, audit, metrics a observability

- rozlíšiť User Events, Admin Events, server/access logs, metrics, health a traces podľa ich proof boundary;
- definovať exact deployment/node/realm/client/session/request a evidence-generation subject;
- sledovať source generation, listener delivery, durable storage a queryability ako samostatné states;
- vysvetliť event-listener loss, duplicate, ordering a backpressure semantics;
- agregovať instance-local event counters so scrape-population a restart evidence;
- riadiť metric label cardinality a chrániť management interface na porte 9000;
- korelovať identity journey s downstream business operation bez logovania secrets;
- overiť missing-node, restart, listener outage, wrong-target a second-operation paths.

### Themes, email templates a localization

- považovať theme JAR/FreeMarker za trusted runtime artifact s digestom a parent generation;
- preferovať minimal CSS/message override pred kopírovaním built-in templates;
- zachovať login action URL, transaction context, WebAuthn a required-action contract;
- generovať email action URLs z canonical hostname bez tracking alebo hardcoded redirectu;
- vysvetliť locale precedence, realm overrides a message-bundle fallback;
- validovať placeholder parity, UTF-8, HTML escaping a security semantics vo všetkých locales;
- testovať accessibility, browser/passkey matrix a upstream-template upgrade diff;
- uzavrieť stale server/browser/CDN cache cez immutable rollout a second-locale journey.

### Keycloak server configuration, hostname a reverse proxy

- určiť configuration-source precedence a build-time/runtime generation;
- používať explicitný hostname ako issuer, endpoint a action-link authority;
- oddeliť `hostname-admin` URL generation od skutočného network isolationu;
- navrhnúť frontend, backchannel a admin route contract;
- porovnať re-encrypt, edge a passthrough termination modes;
- dôverovať Forwarded/X-Forwarded headers iba od exact proxy source cohortu;
- chrániť management interface, direct listeners a public endpoint allowlist;
- overiť spoofed-header, wrong-port, direct-service, proxy-failover a second-Pod paths.

### TLS, truststores, cookies, headers a production hardening

- rozlíšiť inbound server certificate/private key, outbound CA truststore a client-authentication keystore;
- validovať complete chain, hostname/SNI, protocols, ciphers a key/certificate pairing;
- vykonať predecessor/successor certificate a truststore rotation s wire read-backom;
- udržať service-specific outbound trust a exact DNS/hostname validation;
- vysvetliť Secure, HttpOnly, SameSite, Path a Domain cookie behavior cez proxy topology;
- riadiť CSP, HSTS, frame, content-type a referrer policy bez conflicting proxy rewrites;
- oddeliť TLS rotation od Keycloak session, token a application descendants;
- overiť wrong-host, expired, untrusted-CA, spoofed-certificate-header, direct-backend a second-session paths.
"""
if "### Events, audit, metrics a observability" not in readme:
    readme = readme.rstrip() + learning_extension + "\n"

README.write_text(readme.rstrip() + "\n", encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `17-keycloak-and-identity-platform`",
    "| `17-keycloak-and-identity-platform` — Keycloak and Identity Platform | 20/30 authoritative drafting | In progress | 2026-08-02 | Dvadsať authoritative kapitol je aktívnych. Blok 17–20 uzatvára User/Admin Events, Event Listener SPI, logs, instance-local event metrics, management health/metrics a trace/business correlation; trusted theme JAR/FreeMarker, inheritance, action-link email templates, localization precedence, placeholder parity a upgrade drift; configuration-source precedence, build/runtime generation, hostname v2, frontend/backchannel/admin authority, reverse-proxy modes, trusted forwarding headers, route allowlist a management isolation; a inbound TLS certificate/key, outbound truststore, backend SNI, certificate rotation, browser cookies, CSP/HSTS/related headers a session/token descendants. Connected incidents `KC-PAY-69` až `KC-PAY-72` spájajú partial telemetry population, lost audit delivery, stale passkey/email theme, spoofed proxy authority, public admin exposure, broad CA trust a weakened browser hardening. Kapitoly 1–16 prešli preserve/executable checkom a blok 17–20 strict concept, substantial prose, executable/model surface a subject/evidence/recovery/acceptance gate-om. README ordering, learning goals, ROADMAP, navigation, glossary a full audit sú synchronizované. Sekcia zostáva In progress; ďalší blok 21–24 bude database/transactions/pools/schema lifecycle, Infinispan clustering/session behavior, Keycloak Operator/Kubernetes a HA multi-AZ/multi-cluster topology. Reálne telemetry pipelines, themes, proxies, certificates, external dependencies, browsers a sessions neboli týmto documentation workflowom vykonané. |",
)

print("Keycloak block 17-20 passed the 20-chapter gate and was activated in README and ledger.")
