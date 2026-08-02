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
]

BLOCK_ARTICLES = {
    "database-transactions-connection-pools-schema-lifecycle.md": [
        "connection pool", "migration strategy", "validate", "manual", "schema", "unknown outcome", "kc-pay-73"
    ],
    "infinispan-caches-clustering-session-behavior.md": [
        "persistent sessions", "volatile sessions", "jdbc-ping", "topology", "invalidation", "stateless", "kc-pay-74"
    ],
    "keycloak-operator-kubernetes-deployment.md": [
        "custom resource", "additionaloptions", "spec.env", "observed generation", "managed", "operator", "kc-pay-75"
    ],
    "high-availability-multi-az-multi-cluster-trade-offs.md": [
        "multi-cluster v1", "multi-cluster v2", "preview", "/lb-check", "fencing", "rpo", "rto", "kc-pay-76"
    ],
}

SEMANTIC_GROUPS = [
    ("subject", "identity", "generation"),
    ("evidence", "dôkaz", "preukazuje", "ukazuje", "potvrdzuje", "verdict"),
    ("recovery", "obnova", "náprava", "revocation", "containment", "failback"),
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
    text = validate_article(SECTION / name, minimum_words=1800, minimum_fences=10)
    lowered = text.lower()
    missing_concepts = [concept for concept in concepts if concept not in lowered]
    if missing_concepts:
        raise RuntimeError(f"{name} is missing required Keycloak concepts: {missing_concepts}")
    missing_groups = [group for group in SEMANTIC_GROUPS if not any(token in lowered for token in group)]
    if missing_groups:
        raise RuntimeError(f"{name} lacks subject/evidence/recovery/acceptance language: {missing_groups}")

readme = README.read_text(encoding="utf-8")

active_marker = "20. [TLS, truststores, cookies, headers a production hardening](tls-truststores-cookies-headers-production-hardening.md)\n"
active_extension = """20. [TLS, truststores, cookies, headers a production hardening](tls-truststores-cookies-headers-production-hardening.md)
21. [Database, transactions, connection pools a schema lifecycle](database-transactions-connection-pools-schema-lifecycle.md)
22. [Infinispan caches, clustering a session behavior](infinispan-caches-clustering-session-behavior.md)
23. [Keycloak Operator a Kubernetes deployment](keycloak-operator-kubernetes-deployment.md)
24. [High availability, multi-AZ a multi-cluster trade-offs](high-availability-multi-az-multi-cluster-trade-offs.md)
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
    "Aktuálny authoritative stav sekcie je **24/30 · In progress**. Kapitoly 1–24 teraz pokrývajú identity, protocol, authentication, federation, authorization, administration a edge hardening lifecycle-y aj database transaction/schema authority, Infinispan cache a persistent/volatile session semantics, Operator/Kubernetes reconciliation a supported multi-AZ/multi-cluster HA trade-offs. Sekcia zatiaľ nie je `Ready for user review`; ďalší blok začína backup/restore/import-export disaster recovery, upgrades a rollback boundaries, custom providers/SPI lifecycle a securing APIs, microservices a MCP servers."
)
readme = readme.replace(state_lines[0], new_state, 1)

planned_lines = """21. Database, transactions, connection pools a schema lifecycle  
22. Infinispan caches, clustering a session behavior  
23. Keycloak Operator a Kubernetes deployment  
24. High availability, multi-AZ a multi-cluster trade-offs  
"""
readme = readme.replace(planned_lines, "")

scenario_marker = "\n## Dominantný model sekcie\n"
scenario = """### `KC-PAY-73` až `KC-PAY-76` — schema, cache, controller a site authority collapse

Platform blok rozširuje connected settlement incident o durable state a availability. Autoscaler násobil per-Pod database pool ceiling nad writer capacity, zatiaľ čo nový Pod automaticky migroval schema počas mixed-version trafficu. Timeout-nutá Admin REST mutation bola bez authoritative read-backu zopakovaná a prepísala concurrent client generation.

Jeden Pod používal local cache, ďalšie dva rozdielne cluster names nad rovnakou database. Persistent sessions sa po failoveri načítali, ale realm/client invalidácie zostali rozdelené a jeden node vydával predecessor claims. GitOps zároveň vlastnil `Keycloak` CR aj Operator-managed workload; manuálne/env patch-e oscilovali pri reconcile a management TLS skryté iba v custom image rozbilo Operator probes.

Dve sites boli označené ako active-active HA, no global load balancer sledoval iba HTTP readiness. Pri cross-site Infinispan partition obe sites pokračovali v trafficu bez fencing-u a survivor nemal kapacitu pre celý peak load.

```text
ambiguous schema/pool authority
+ split cache/session topology
+ multiple writers na Operator-managed state
+ HTTP-only site health bez fencing/capacity reserve
→ durable, cached, reconciled a serving generations sa rozídu
→ duplicate mutation, stale entitlement alebo failed site recovery
```

Recovery zavádza jediného migration writera a global pool budget, exact cache/session authority a cluster-view gate, GitOps ownership iba CR plus Operator ownership descendants a failure-specific fencing, capacity, RPO/RTO a failback acceptance. Closure vyžaduje second migration, second invalidation, second reconcile a second-site failure testy.
"""
if "### `KC-PAY-73` až `KC-PAY-76`" not in readme:
    if scenario_marker not in readme:
        raise RuntimeError("Expected Section 17 dominant-model marker not found")
    readme = readme.replace(scenario_marker, "\n" + scenario.rstrip() + "\n" + scenario_marker, 1)

learning_extension = """

### Database, transactions, connection pools a schema lifecycle

- definovať exact database, schema, writer endpoint, credential, truststore a migration generation;
- rozpočítať global connection budget ako per-Pod maximum krát max replicas plus recovery reserve;
- odlíšiť connection acquisition, transaction commit, cache invalidation a response delivery;
- riešiť timeout ako unknown outcome cez operation ID a authoritative read-back pred retry;
- oddeliť runtime DML account od migration DDL ownershipu;
- vysvetliť `update`, `manual` a `validate` migration stratégie a readiness počas migration;
- navrhnúť mixed-version, backup, binary/schema rollback a writer-failover boundaries;
- overiť saturation, wrong schema, failover, unknown outcome a second-migration paths.

### Infinispan caches, clustering a session behavior

- mapovať realms/users/authorization, sessions, offline sessions, authentication sessions, action tokens, login failures a work cache na ich authority;
- rozlíšiť default persistent sessions od volatile cache-authoritative sessions;
- vysvetliť preview stateless mode bez zamieňania za supported production default;
- identifikovať exact cluster, view, topology, owner, site/rack/machine a database generation;
- používať `jdbc-ping` discovery a overiť transport reachability aj expected member view;
- chápať affinity ako optimization, nie durability mechanismus;
- overiť invalidation medzi nodes bez restart workaroundu;
- testovať eviction, node/full-cluster restart, split cluster, offline token a second-session behavior.

### Keycloak Operator a Kubernetes deployment

- definovať exact Operator, CRD, `Keycloak` CR, image, Secret a managed-workload generation;
- rozlíšiť first-class CR fields, `additionalOptions` a raw `spec.env`;
- používať immutable optimized custom image s build provenance;
- zachovať single-writer model: GitOps vlastní CR, Operator owns descendants;
- čítať spec generation, observed generation, conditions a workload revision ako oddelené states;
- navrhnúť public/admin/management route isolation mimo default ingress limitov;
- zosúladiť scheduling/resources/HPA s cache topology a database pool budgetom;
- overiť Secret rotation, Pod/zone loss, Operator upgrade, drift a second-reconcile paths.

### High availability, multi-AZ a multi-cluster trade-offs

- pomenovať exact architecture: multi-node, multi-AZ single cluster, supported v1 alebo preview v2;
- viazať HA na database, cache/session, load balancer, DNS/TLS, dependencies a survivor capacity;
- udržať low-latency synchronous replication a merať tail latency, nie iba average RTT;
- vysvetliť v1 external Infinispan cross-site, site offlining/resync a two-site boundary;
- označiť v2/stateless ako preview a zahrnúť vyššiu database CPU/IOPS/latency;
- rozlíšiť active-active a active-passive traffic, fencing a authoritative-site decision;
- merať `/lb-check`, synthetic protocol a business canary ako layered evidence;
- overiť RPO/RTO, failover, survivor load, failback, upgrade a second-failure paths.
"""
if "### Database, transactions, connection pools a schema lifecycle" not in readme:
    readme = readme.rstrip() + learning_extension + "\n"

README.write_text(readme.rstrip() + "\n", encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `17-keycloak-and-identity-platform`",
    "| `17-keycloak-and-identity-platform` — Keycloak and Identity Platform | 24/30 authoritative drafting | In progress | 2026-08-02 | Dvadsaťštyri authoritative kapitol je aktívnych. Blok 21–24 uzatvára database/schema/writer identity, Pod-local pool a global connection budget, transaction unknown outcome, JPA migration `update/manual/validate`, mixed-version a backup/rollback boundary; Infinispan entity/session/authentication/action/brute-force/work caches, persistent versus volatile sessions, `jdbc-ping`, cluster/view/topology/owner identity, affinity, invalidation, external cache a preview stateless mode; Keycloak Operator/CRD/CR reconciliation, first-class fields versus `additionalOptions`/`spec.env`, immutable custom image, Secret rollout, managed-resource single writer, scheduling/probes/routes/HPA a Operator upgrade; a multi-node, multi-AZ single-cluster, supported two-site multi-cluster v1 a preview multi-cluster v2 architecture, synchronous database/cache state, `/lb-check`, capacity, fencing, RPO/RTO, failover/resync/failback a upgrade boundaries. Connected incidents `KC-PAY-73` až `KC-PAY-76` spájajú pool amplification, mixed schema writers, split cache topology, Operator/GitOps ownership conflict a HTTP-only site health bez fencing alebo survivor capacity. Kapitoly 1–20 prešli preserve/executable checkom a blok 21–24 strict concept, substantial prose, executable/model surface a subject/evidence/recovery/acceptance gate-om. README ordering, learning goals, ROADMAP, navigation, glossary a full audit sú synchronizované. Sekcia zostáva In progress; ďalší blok 25–28 bude backup/restore/import-export disaster recovery, upgrades/migration/rollback, custom providers/SPI a securing APIs/microservices/MCP servers. Reálne database migrations, cache clusters, Operator reconciliation, site failures a business traffic neboli týmto documentation workflowom vykonané. |",
)

print("Keycloak block 21-24 passed the 24-chapter gate and was activated in README and ledger.")
