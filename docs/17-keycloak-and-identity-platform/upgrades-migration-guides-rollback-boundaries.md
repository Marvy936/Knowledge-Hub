# Upgrades, migration guides a rollback boundaries

Keycloak upgrade nie je iba zmena container tagu. Nová server generation môže zmeniť database schema, default configuration, cache model, protocol behavior, Admin Console, themes, SPIs, provider dependencies, feature lifecycle, metrics a client-library expectations. Úspešný Pod rollout preto nepreukazuje compatible identity service. Upgrade closure vyžaduje exact predecessor/successor inventory, migration-guide review cez každú preskočenú verziu, schema ownership, extension rebuild, supported mixed-version boundary, protocol/business acceptance a vopred definovaný rollback alebo forward-fix path.

Najnebezpečnejší upgrade je ten, ktorý vyzerá reverzibilne. Ak successor automaticky migruje schema a začne zapisovať nové rows/columns alebo semantics, rollback image-u na predecessor môže byť unsupported aj vtedy, keď Kubernetes vie Deployment okamžite vrátiť. Ak custom provider používa internal API alebo copied theme template, binary môže štartovať, no login, mapper alebo Admin REST behavior sa rozbije až na konkrétnej journey.

## 1. Dominantný release-to-stable-generation lifecycle

```text
business a security release intent
→ exact predecessor inventory
→ migration guide review pre každú version boundary
→ successor image/provider/theme/client-library build
→ database/schema a feature compatibility plan
→ backup/restore a rollback decision
→ canary alebo maintenance deployment
→ schema migration a mixed-version window
→ protocol, session, admin, extension a business acceptance
→ full rollout
→ predecessor retirement
→ second rollout/failover a post-upgrade monitoring
```

Každá fáza má vlastný authority. Registry image existence nepreukazuje provider registry alebo build-time options. Migration SQL apply nepreukazuje application compatibility. `Ready` Pod nepreukazuje login, refresh, broker, LDAP, SAML, passkey alebo Admin API. Successful first request nepreukazuje mixed-node cache invalidation, rolling restart ani session continuity.

## 2. Exact upgrade subject

```yaml
upgradeSubject:
  source:
    keycloakVersion: 26.6.2
    imageDigest: sha256:1bc2...
    schemaVersion: kc-schema-26.6.2
    deploymentGeneration: kc-release-51
    providerSetHash: sha256:19ad...
    themeSetHash: sha256:77cc...
    enabledFeatures: [persistent-user-sessions, organization]
    disabledFeatures: []
  target:
    keycloakVersion: 26.7.0
    imageDigest: sha256:6a91...
    schemaVersion: kc-schema-26.7
    deploymentGeneration: kc-release-52
    providerSetHash: sha256:93ef...
    themeSetHash: sha256:bb18...
    enabledFeatures: [persistent-user-sessions, organization]
    previewFeatures: []
  migration:
    reviewedVersions: [26.6.2, 26.7.0]
    migrationGuideRevision: 2026-07-09
    strategy: validate-plus-controlled-sql
    sqlArtifactHash: sha256:8f2d...
    databaseBackupId: kc-db-snap-20260802T061500Z
  rollout:
    model: single-cluster-multi-az
    compatibilityWindow: patch-only-reviewed
    canaryRealm: atlas-upgrade-canary
    rolloutRunId: release-2026-08-02-52
  clients:
    adminClientVersion: 26.0.8
    authorizationClientVersion: 26.0.8
    policyEnforcerVersion: 26.0.8
```

Bez predecessor provider/theme hashes sa upgrade drift nedá oddeliť od server change-u. Bez reviewed version chain sa preskočená breaking change prehliadne. Bez schema artifact/strategy nevieme, kto mutoval database. Bez feature inventory môže upgrade zapnúť default alebo odstrániť deprecated capability. Bez client-library inventory sa server-side success zamieňa s consumer compatibility.

## 3. Migration guide je povinný input

Migration changes obsahujú breaking, notable, deprecated a removed behaviors pre jednotlivé releases. Pri skoku cez viac versions sa reviewuje každá medziverzia v poradí.

```text
current 25.0.x
→ review 25.0 → 25.1 ... → 26.0 → ... → 26.7
→ classify every relevant change
→ owner, remediation a test
```

Release notes highlighty nie sú úplný migration contract. Search podľa používaných features, SPIs, configuration options, DB vendor, themes, OIDC/SAML behavior, metrics a adapters.

Migration ledger:

```yaml
- change: transaction setup timeout option replacement
  affected: import/export/schema migration automation
  owner: identity-platform
  action: replace deprecated SPI option
  evidence: config-diff-311
- change: USER_ENTITY timestamp columns
  affected: custom reporting provider
  owner: identity-integrations
  action: validate NULL legacy rows
  evidence: integration-test-884
```

## 4. Patch, minor a major version risk

Semantic version číslo samo neurčuje zero-downtime compatibility. Patch môže obsahovať migration alebo security behavior change; minor/major môže meniť schema, internal APIs a defaults. Official migration guide a supported upgrade path sú authority.

```text
patch update
→ často rolling-compatible, ale musí byť explicitne potvrdené

minor/major update
→ vyššie schema/provider/theme/protocol risk
→ maintenance alebo constrained mixed-version window
```

Nikdy nepredpokladaj arbitrary skip alebo downgrade. Upgrade rehearsal používa production-like data volume a extensions.

## 5. Immutable successor image

Nová distribution sa neprepisuje in-place. Buildni nový immutable image:

```Dockerfile
FROM quay.io/keycloak/keycloak:26.7.0 AS builder
ENV KC_DB=postgres
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true
COPY --chown=keycloak:keycloak providers/ /opt/keycloak/providers/
COPY --chown=keycloak:keycloak themes/ /opt/keycloak/themes/
RUN /opt/keycloak/bin/kc.sh build

FROM quay.io/keycloak/keycloak:26.7.0
COPY --from=builder /opt/keycloak/ /opt/keycloak/
ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
```

Pin base digest a record provider/dependency/theme hashes. `providers/` and `themes/` z predecessor installation sa nemajú slepo kopírovať bez compatibility rebuild/review. `conf/` sa prenáša cez reviewed desired state; custom `cache-ispn.xml` sa re-aplikuje na nový shipped baseline alebo nahradí supported options.

## 6. Configuration diff

Configuration options môžu byť renamed, deprecated, removed alebo zmeniť default. Canonical plan porovná:

```text
source kc.conf/CR/env/CLI
→ normalized effective options
→ successor option catalog
→ added/removed/changed/defaulted values
```

Nevaliduj iba startup absence of errors. Read-back discovery, hostname, cache mode, metrics, health, cookie/header a database behavior. Unknown option má byť failure, nie silent ignore.

## 7. Feature lifecycle

Keycloak features môžu byť default, preview, experimental, deprecated alebo removed. Feature name/version je súčasť server generation.

```bash
bin/kc.sh build \
  --features=persistent-user-sessions,organization \
  --features-disabled=some-deprecated-feature
```

Preview feature upgrade môže mať breaking state/config changes. Produkcia nemá implicitne zdediť novo default-enabled feature bez acceptance. Removal potrebuje data/config cleanup a consumer migration pred upgrade.

## 8. Database migration ownership

Upgrade môže vyžadovať schema migration. Zvoľ jediného writera:

```text
backup a restore rehearsal
→ generate/review SQL cez manual strategy
→ stop incompatible writers alebo isolate migration
→ apply SQL with migration account
→ runtime Pods start s validate
```

```bash
bin/kc.sh start \
  --spi-connections-jpa--quarkus--migration-strategy=manual \
  --spi-connections-jpa--quarkus--initialize-empty=false \
  --spi-connections-jpa--quarkus--migration-export=/tmp/keycloak-26.7.sql
```

Automatic update môže byť supported, ale stále potrebuje ownership, timeout a rollback plan. Large table index creation môže byť skipped a SQL logged for manual execution podľa migration change; startup green bez indexu môže mať performance risk.

## 9. Transaction setup timeout

Schema migration, import a export môžu používať dlhší setup transaction timeout než normal requests. Aktuálne releases majú explicitný `transaction-setup-timeout`; predecessor SPI lock option môže byť nahradený.

```bash
bin/kc.sh start \
  --transaction-default-timeout=PT5M \
  --transaction-setup-timeout=PT30M
```

Zvýšenie timeoutu nerieši blocking lock alebo wrong migration plan. Sleduj database locks, progress a stop condition. Orchestrátor startup probe musí tolerovať planned duration bez restart loopu.

## 10. Mixed-version window

Rolling upgrade dočasne vytvára source a target Pods nad shared database/cache. Tento window je bezpečný iba ak version pair a schema sú compatible.

```text
predecessor Pods
+ successor canary Pod
→ shared DB/cache
→ only supported operations počas windowu
→ complete rollout promptne
```

Nenechávaj mixed versions dlhodobo. Admin/config mutations sa môžu freeze-nuť počas windowu. Cache marshalling, provider behavior a feature defaults musia byť compatible.

## 11. Canary stratégia

Canary Pod v jednom clusteri môže zdieľať database a cache, takže nie je izolovaný od schema mutation. Safer options:

```text
restored production-like DB clone
→ full rehearsal

isolated canary realm/client on successor environment
→ protocol tests

supported rolling canary in production
→ only after schema compatibility proven
```

Canary traffic musí pokryť real journeys a extensions. Health-only canary je nedostatočný.

## 12. Acceptance inventory

Minimálne journeys:

```text
local password + MFA/passkey login
remembered SSO a step-up
OIDC code+PKCE, refresh, logout, revocation
SAML SP/IdP initiated podľa contractu
identity brokering a account linking
LDAP/AD credential + group/role sync
service account client credentials
Authorization Services/token exchange
Admin Console a Admin REST automation
email required actions
offline token
custom provider/theme/REST endpoint
metrics/events/audit
node failover a cache invalidation
```

Každý test fixuje realm/client/user/workload/resource generation a positive/forbidden outcome.

## 13. Themes a Admin/Account consoles

Built-in templates/resources sa môžu meniť. Custom copied templates sa diffujú proti successor baseline. Account/Admin Console version môže meniť frontend behavior a custom extensions.

```text
list overridden templates/resources
→ compare source and target built-ins
→ port upstream security/accessibility/protocol changes
→ rebuild theme
→ all-locale/browser journey test
```

Visual screenshot alone nepreukazuje form action, passkey, CSP alebo required-action success.

## 14. Custom providers a internal APIs

Provider JARs sa rebuildnú proti target Keycloak dependencies. Internal/private APIs nemajú stable compatibility guarantee. Single classloader znamená dependency conflict risk.

```text
compile against target BOM/APIs
→ unit/integration test
→ build optimized image
→ provider registry read-back
→ lifecycle/failure/security test
```

Provider startup success nepreukazuje transaction, cache, concurrency alebo upgrade-state behavior. Chapter 27 rozoberá extension lifecycle detailne.

## 15. Adapters a client libraries

Server, Admin client, Authorization client a Policy Enforcer libraries sa versionujú separately. Latest client library býva compatible s latest server, ale application upgrade má vlastný release/test.

```text
server upgrade
→ protocol backward compatibility test
→ adapter/client library upgrade
→ application regression
```

Legacy adapters môžu byť deprecated/removed. FAPI/OAuth profiles vyžadujú client-side validations, ktoré server adapter automaticky nepridá.

## 16. Protocol a key continuity

Upgrade nesmie náhodne zmeniť issuer, hostname, realm keys alebo metadata. JWKS môže obsahovať predecessor/successor signing keys podľa planned rotation, ale upgrade samotný nie je dôvod na key reset.

```bash
curl -fsS https://sso.atlas.example/realms/atlas-prod/.well-known/openid-configuration | jq .issuer
curl -fsS https://sso.atlas.example/realms/atlas-prod/protocol/openid-connect/certs | jq '.keys[] | {kid,kty,alg,use}'
```

Compare SAML metadata/entityID/certificates a OIDC discovery/JWKS before/after. Existing access/refresh/offline tokens sa testujú podľa compatibility objective.

## 17. Session continuity

Persistent sessions môžu prežiť Pod rollout a načítať sa z database, ale upgrade môže meniť cache/session serialization alebo protocol behavior. Testuj:

```text
login before upgrade
→ refresh during mixed window
→ API request after successor rollout
→ logout/revocation

in-progress authentication/required action
→ Pod rollout/failover
→ expected restart alebo continuation podľa contractu
```

Session continuity nie je automaticky required pri major upgrade; ak sa plánuje forced logout, komunikuj a testuj explicitne.

## 18. Multi-cluster upgrade

V multi-cluster topology sa version skew riadi official HA upgrade guide. Major/minor upgrade môže vyžadovať, aby traffic obsluhovala iba jedna site a ostatné boli offlined, potom sa promptne upgrade-nu všetky sites.

```text
fence site B
→ upgrade/verify site A + shared schema
→ upgrade site B
→ resync/cache/site checks
→ restore traffic
```

V1 external Infinispan a v2 preview database/outbox majú odlišný upgrade behavior. Neaplikuj single-cluster rolling assumptions na multi-cluster.

## 19. Rollback axes

Rollback má viac osí:

```text
server binary/image
schema
provider/theme artifact
configuration/features
realm/client data
sessions/tokens
client applications/libraries
```

Vrátenie image-u bez schema rollbacku je možné iba pri documented backward compatibility. Schema restore vracia database čas a môže stratiť post-backup writes. Provider rollback môže byť incompatible s successor data. Realm restore môže reaktivovať revoked token/session state.

Rollback plan musí uviesť, ktoré osi sa vracajú a ktoré sa forward-fixujú.

## 20. Roll-forward

Pri irreversible schema migration je často bezpečnejší forward fix:

```text
freeze risky mutations
→ deploy corrected successor build/config
→ apply additive repair migration
→ reconcile affected objects/sessions
```

Live manual patch bez source/commit a second rollout vytvára undocumented generation. Emergency fix sa musí premeniť na immutable artifact a re-run-nuť.

## 21. Rollback decision point

Pred rolloutom definuj stop conditions:

```text
schema migration failure before commit
provider startup/class conflict
login/refresh failure rate threshold
issuer/metadata drift
DB/cache saturation
business authorization regression
```

A decision deadline:

```text
before successor writes irreversible data
→ binary rollback possible

after irreversible migration/new writes
→ forward fix alebo coordinated restore
```

Bez decision pointu tím skúša náhodné rollbacky počas incidentu.

## 22. Backup a restore rehearsal

Upgrade backup je použiteľný iba ak restore bol otestovaný s predecessor image a database version. Pred upgrade zachovaj PITR point, realm export ako supplemental artifact, image/provider/theme/config digests a migration SQL.

Restore rehearsal meria actual time a zahŕňa admin access, keys, sessions a business journeys. Snapshot creation alone nie je rollback evidence.

## 23. Deprecation a removal inventory

Automatizovane hľadaj:

```text
startup deprecation warnings
removed/unknown CLI options
preview/deprecated features
legacy adapters
custom provider internal packages
copied theme templates
Admin REST fields/endpoints
metrics/log names used by dashboards
```

Warning backlog má ownera a deadline pred release, kde sa feature odstráni. Ignorované warnings menia upgrade na emergency migration.

## 24. Incident `KC-PAY-78`

Atlas prešiel z predecessor release na 26.7 rolling updateom. Prvý successor Pod automaticky migroval schema. Tím videl Ready condition a pokračoval. Custom Event Listener bol skompilovaný proti internému API a pri prvom Admin Evente vyhodil `NoSuchMethodError`; audit delivery sa zastavila.

Custom login theme kopírovala starý WebAuthn template a passkey users zlyhali. Staršie Pods zostali v trafficu niekoľko hodín a používali predecessor mapper/cache assumptions. Pri rollbacku sa vrátil iba image, nie schema ani provider data. Predecessor server štartoval, ale Admin Console a group queries zlyhávali.

```text
health-only canary
+ automatic irreversible schema change
+ untested provider/theme compatibility
+ partial image-only rollback
→ apparently successful rollout, unsafe mixed generation
```

Recovery použila forward-fixed provider/theme image, dokončila rollout a reconciled affected audit gap. Ďalší upgrade používa migration ledger, restored-DB rehearsal, manual/validate schema ownership, full journey matrix, bounded mixed window a rollback-axis decision record.

## 25. Evidence-preserving containment a recovery

Zachovaj source/target image and build digests, migration guides/ledger, schema SQL/version/locks, database backup ID, provider/theme source and binary hashes, effective configuration/features, Pod cohorts, events/logs/metrics, protocol artifacts, session/token samples a client-library versions.

Containment freeze-ne admin/import/config mutations, odoberie failing cohort z trafficu a chráni backup. Recovery zvolí supported binary rollback, coordinated restore alebo immutable forward fix. Manuálne DB edits bez vendor/Keycloak-supported plan sú forbidden.

## 26. Acceptance matrix

Positive:

```text
successor rehearsal a canary
→ schema/build/provider/theme compatible
→ full journey matrix succeeds
→ bounded rollout completes
```

Recovery:

```text
stop condition triggered
→ decision point
→ supported rollback/restore alebo forward fix
→ data/session/business reconciliation
```

Forbidden:

```text
upgrade bez complete migration-guide chain
→ release gate rejects

custom provider/theme copied bez target rebuild/diff
→ supply-chain gate rejects

image-only rollback po irreversible schema migration
→ runbook rejects

long-lived mixed major/minor versions
→ deployment gate rejects
```

Second-rollout test reštartuje/replaces all Pods z immutable target image. Second-site test overí failover a resync po upgrade. Second-journey test používa existing pre-upgrade session/token aj fresh login.

## Kontrolné otázky

- Ktoré exact source a target server/schema/provider/theme/config generations meníme?
- Boli reviewované migration changes pre každú preskočenú verziu?
- Kto je jediný schema migration writer a kedy sa predecessor writers zastavia?
- Je mixed-version window explicitne supported a časovo bounded?
- Boli provider JARs rebuildnuté a copied templates diffnuté proti targetu?
- Ktoré features sú default, preview, deprecated alebo removed?
- Čo sa deje s existing sessions, tokens, keys a metadata?
- Ktoré rollback axes sú reversible a dokedy?
- Máme restore-tested backup a forward-fix plan?
- Prešli full journey, failover, second-rollout a pre-existing-session testy?

## Primárne zdroje

- [Keycloak — Upgrading Guide](https://www.keycloak.org/docs/latest/upgrading/)
- [Keycloak — Migration Changes](https://www.keycloak.org/docs/latest/upgrading/)
- [Keycloak — Configuring the database](https://www.keycloak.org/server/db)
- [Keycloak — Configuring distributed caches](https://www.keycloak.org/server/caching)
- [Keycloak — Configuring providers](https://www.keycloak.org/server/configuration-provider)
- [Keycloak — Multi-cluster upgrades](https://www.keycloak.org/high-availability/multi-cluster-v2/upgrades)
