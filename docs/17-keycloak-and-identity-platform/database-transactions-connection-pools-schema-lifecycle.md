# Database, transactions, connection pools a schema lifecycle

Keycloak database nie je iba persistence layer pre users a realms. Je authoritative store pre realm/client/user configuration, credentials metadata, consents, offline sessions, persistent regular sessions, cluster discovery records, migration metadata a ďalšie identity state podľa enabled features a version generation. Každý login, token refresh, admin mutation alebo session revocation môže kombinovať database transaction, cache invalidation a external effect. Zelený SQL connection test preto nepreukazuje, že schema je compatible, pool má kapacitu, transaction sa commitla alebo cache a session descendants už vidia successor state.

Najčastejší production incident vzniká pri nejasnom ownership-e schema migration. Nový Keycloak Pod začne automatickú migráciu počas mixed-version rollout-u, zatiaľ čo staršie Pods pokračujú v requestoch proti meniacej sa schema. Druhý častý incident je pool amplification: každý Pod má max pool 100, autoscaler zvýši replicas a súčet connection limitov prekročí database capacity. Jednotlivý Pod vyzerá healthy, ale login requests čakajú na connection alebo database odmieta sessions.

## 1. Dominantný request-to-durable-state lifecycle

```text
identity alebo administration operation
→ exact Keycloak version/image/configuration generation
→ datasource URL/schema/credential/TLS resolution
→ connection acquisition z Pod-local poolu
→ database transaction a lock/constraint behavior
→ durable commit alebo rollback/unknown outcome
→ cache invalidation alebo session-cache update
→ protocol response
→ downstream application/business operation
→ read-back, second operation a recovery closure
```

Každá vrstva môže zlyhať samostatne. Connection acquisition success nepreukazuje commit. HTTP timeout nepreukazuje rollback, pretože database commit mohol nastať pred stratou response. Database row update nepreukazuje invalidáciu stale realm/client cache na všetkých nodes. Readiness môže zostať down počas migration a liveness/startup môžu byť up, aby orchestrátor server zbytočne nereštartoval.

## 2. Exact database subject

```yaml
databaseSubject:
  keycloak:
    version: 26.7.0
    imageDigest: sha256:6a91...
    buildGeneration: kc-build-41
    deploymentGeneration: kc-2026-08-02-24
    podUid: 18ac...
  datasource:
    vendor: postgres
    jdbcUrl: jdbc:postgresql://keycloak-db.cluster-7.internal:5432/keycloak
    database: keycloak
    schema: identity
    writerEndpointGeneration: db-writer-92
    tlsMode: verify-server
    truststoreGeneration: db-trust-19
    credentialGeneration: db-user-34
  pool:
    initialSize: 10
    minSize: 20
    maxSizePerPod: 60
    maxLifetime: PT50M
    replicaCount: 6
    totalConfiguredCeiling: 360
  schema:
    currentVersion: kc-schema-26.7
    migrationStrategy: validate
    migrationArtifactHash: sha256:8f2d...
    migrationOwner: keycloak-schema-job-2026-08-02
  operation:
    realm: atlas-prod
    type: client-update
    operationId: admin-op-8812
    transactionId: tx-55f1...
```

Bez writer endpoint generation sa failover nedá spojiť s connection errors. Bez schema/version a migration ownera sa mixed Pod behavior iba háda. Bez total configured pool ceiling sa per-Pod max interpretuje izolovane. Bez operation ID nemožno bezpečne rozhodnúť, či timeout-nutú Admin REST mutation zopakovať.

## 3. Supported database a driver generation

Production používa explicitný supported database vendor a version. `dev-file` nie je production datastore. Database driver je súčasť image/build generation; pri vendorovi, ktorý potrebuje externé JDBC JARs, sa driver pridá do `providers/` a image sa optimalizovane prebuduje.

```Dockerfile
FROM quay.io/keycloak/keycloak:26.7.0 AS builder
ENV KC_DB=oracle
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true
COPY --chown=keycloak:keycloak ojdbc17.jar /opt/keycloak/providers/ojdbc17.jar
RUN /opt/keycloak/bin/kc.sh build

FROM quay.io/keycloak/keycloak:26.7.0
COPY --from=builder /opt/keycloak/ /opt/keycloak/
ENTRYPOINT ["/opt/keycloak/bin/kc.sh", "start", "--optimized"]
```

Image build preukazuje intended driver artifact placement. Nepreukazuje runtime database compatibility ani driver/JDK behavior. Acceptance fixuje driver JAR digest, Keycloak image digest, vendor/version a TLS/authentication mode.

## 4. Datasource configuration a exact target

```bash
bin/kc.sh start --optimized \
  --db=postgres \
  --db-url='jdbc:postgresql://keycloak-db.cluster-7.internal:5432/keycloak' \
  --db-schema=identity \
  --db-username=keycloak_runtime \
  --db-password="${KC_DB_PASSWORD}" \
  --db-tls-mode=verify-server \
  --db-tls-trust-store-file=/etc/keycloak/db/db-trust.p12
```

Database host alias musí identifikovať intended writer/failover contract. Schema name je samostatný namespace; rovnaká database môže obsahovať viac schemas, ale zdieľanie vyžaduje oddelené users, grants a migration ownership. Omyl v `db-schema` môže spustiť initialization do empty namespace alebo čítať starú environment generation.

Database credential má least privilege podľa runtime a migration modelu. Runtime account nemusí mať DDL, ak migration vykonáva oddelený owner/job. Migration account nemá byť trvalo dostupný server Pods.

## 5. Password literal a secret delivery

Ak database password obsahuje `$` alebo `${...}`, configuration expansion môže hodnotu zmeniť. Keycloak podporuje `KCRAW_` prefix pre literal values, napríklad `KCRAW_DB_PASSWORD`. Bezpečnejší deployment používa Secret file alebo operator secret reference a eviduje exact secret generation.

```text
secret manager generation
→ Kubernetes Secret/version
→ Pod mount alebo environment
→ Keycloak configuration resolution
→ JDBC authentication
```

Úspešné prihlásenie do databázy nepreukazuje, že password rotation je uzavretá na všetkých Pods. Over predecessor credential retirement a successor connection po rollout-e.

## 6. Connection pool ako Pod-local capacity

`db-pool-initial-size`, `db-pool-min-size` a `db-pool-max-size` riadia pool každého Keycloak processu. Default max môže byť 100, čo pri mnohých replicas vytvorí vysoký teoretický ceiling.

```text
6 Pods × max pool 60
= 360 možných Keycloak connections
+ migration/admin/monitoring/failover reserve
≤ database connection budget
```

Pool sizing nevychádza iba z CPU countu. Zohľadňuje request concurrency, transaction latency, long-running admin operations, login peaks, database failover a reserved capacity. Príliš malý pool vytvorí acquisition wait. Príliš veľký pool prenesie queue do database a zhorší lock/cache/CPU pressure.

```bash
bin/kc.sh start \
  --db-pool-initial-size=10 \
  --db-pool-min-size=20 \
  --db-pool-max-size=60 \
  --db-pool-max-lifetime=PT50M
```

Initial/min/max configuration je intended ceiling. Runtime acceptance potrebuje pool active/available/pending metrics, database connection count a request latency.

## 7. Connection lifetime a server timeout

Database alebo network môže ukončiť idle/old connection. Pool max lifetime má byť kratší než server-side timeout. Pri MySQL/MariaDB má Keycloak default zvolený pod typickým `wait_timeout`, ale custom database timeout vyžaduje zosúladenie.

```text
database wait_timeout = 60 min
→ pool max lifetime = 50–55 min
→ pool retire connection pred serverom
```

Inak sa stale connection vráti requestu a zlyhá až pri použití. Keepalive nie je náhrada lifecycle contractu. Failover proxy môže mať vlastný idle timeout.

## 8. Pool metrics a saturation diagnosis

Database incident musí odlíšiť:

```text
connection acquisition wait
→ pool exhausted alebo database connect slow

active connections near max
→ request concurrency/slow transactions

low active, high DB latency
→ database execution/storage/lock issue

connection creation failures
→ DNS/TLS/auth/failover issue
```

Keycloak metrics a database metrics sa korelujú per Pod a across deployment. Aggregate pool max bez replica countu je zavádzajúci. Pod restart resetuje process-local metrics.

## 9. Transaction boundaries

Keycloak request môže vykonať viac reads/writes v jednej transaction a následne vytvoriť event, cache invalidation alebo external response. Database constraint a lock sú authoritative pre durable state; cache je derived/accelerating state.

```text
Admin REST update client
→ acquire connection
→ load current representation
→ authorize actor
→ write rows
→ commit
→ invalidate client/realm cache
→ return 204
```

Ak response zmizne po commit-e, outcome je unknown pre caller, nie automaticky failed. Pred retry sa vykoná GET read-back podľa internal UUID a expected generation/hash. Blind PUT môže prepísať concurrent change.

## 10. XA a external effects

`transaction-xa-enabled` alebo Operator `spec.transaction.xaEnabled` rieši database transaction capabilities, nie distributed transaction s emailom, Kafka auditom, external IdP alebo business API. External effects potrebujú idempotency/outbox/reconciliation.

```text
DB commit success
+ event listener broker timeout
→ identity state changed, audit delivery unknown
```

Rollback database nevráti odoslaný email. Security-sensitive flows preto evidujú descendant/external effect separately.

## 11. Schema lifecycle

Schema má predecessor a successor generation:

```text
backup a compatibility assessment
→ migration owner election
→ migration plan/SQL artifact
→ maintenance alebo supported rollout boundary
→ DDL/data migration
→ schema version/read-back
→ server compatibility validation
→ traffic admission
→ rollback alebo forward-fix boundary
```

Default automatic update je pohodlný, ale ownership musí byť jednoznačný. Viac Pods môže štartovať súčasne; migration locking koordinuje proces, no startup storm a timeouty stále ovplyvnia availability. Production môže použiť `validate` pre runtime Pods a samostatný controlled migration step.

## 12. Migration strategy

JPA provider podporuje `update`, `manual` a `validate`:

```bash
# Vygenerovať SQL bez automatickej mutation
bin/kc.sh start \
  --spi-connections-jpa--quarkus--migration-strategy=manual \
  --spi-connections-jpa--quarkus--initialize-empty=false \
  --spi-connections-jpa--quarkus--migration-export=/tmp/keycloak-migration.sql
```

`manual` export vytvorí SQL artifact podľa server/schema inputs. Nepreukazuje, že SQL bolo reviewed alebo aplikované. `validate` odmietne incompatible schema bez mutation. `update` automaticky aplikuje migration; production použitie potrebuje backup, rollout a version compatibility plan.

Migration SQL môže byť vendor-specific a environment-specific. Artifact digest, generated Keycloak version, database vendor/version a target schema patria do approval evidence.

## 13. Startup, readiness a long migration

Pri dlhej migration môže startup/liveness signalizovať, že process žije, zatiaľ čo readiness zostáva down do dokončenia initialization. To zabraňuje orchestrátoru zabíjať process kvôli dlhému štartu, no traffic nesmie vstúpiť pred schema compatibility.

```text
process started
→ /health/started UP podľa initialization stage
→ migration running
→ /health/ready DOWN
→ migration complete a runtime initialized
→ /health/ready UP
```

Probe timeouts a Kubernetes startupProbe musia byť dlhšie než worst-case migration alebo musí migration prebehnúť oddelene. Neustále restarty môžu migration predlžovať alebo zanechať unknown state.

## 14. Mixed-version compatibility

Patch rolling update môže mať podporovanú compatibility boundary podľa release guide; major/minor upgrade často mení schema a vyžaduje presný postup. Nesmie sa predpokladať, že N a N+1 môžu ľubovoľne zapisovať súčasne.

```text
old Pods writing predecessor assumptions
+ new Pod migrates schema
→ possible incompatible data/DDL behavior
```

Upgrade kapitola neskôr rieši release-specific postup. Database kapitola vyžaduje, aby migration plan explicitne uviedol allowed concurrent versions a rollback boundary. DDL, ktoré odstraňuje column/table, môže znemožniť rollback binary.

## 15. Backup a rollback boundary

Backup pred migration musí byť transactionally consistent a restore-tested. Snapshot existence nepreukazuje RPO/RTO ani schopnosť vrátiť external/session descendants. Po migration a nových writes môže restore schema backupu stratiť novšie identity changes.

Rollback options:

```text
binary rollback bez schema rollback
→ iba ak predecessor binary je compatible so successor schema

schema restore
→ vracia database generation a môže stratiť post-backup writes

forward fix
→ nový migration artifact opraví successor state
```

Decision sa robí pred release, nie počas incidentu.

## 16. Read replicas a writer failover

Keycloak potrebuje authoritative writer. Read replica routing nesmie posielať transaction reads na stale replica spôsobom, ktorý poruší read-your-write alebo session semantics. Managed database cluster endpoint musí mať documented failover behavior, DNS TTL a connection reset contract.

```text
writer failure
→ managed DB promotes successor
→ existing JDBC connections fail
→ pool discards/recreates
→ transactions retry iba ak operation outcome je známy/idempotentný
```

Blind application retry po connection reset môže duplikovať admin/import/business effect. Read-back podľa operation ID a target object generation je potrebný.

## 17. Database TLS a mTLS

`db-tls-mode=verify-server` zapína encryption a server identity validation podľa driver supportu. Truststore obsahuje server/CA trust. mTLS client keystore obsahuje Keycloak database client private key/certificate.

```bash
bin/kc.sh start \
  --db-tls-mode=verify-server \
  --db-tls-trust-store-file=/etc/keycloak/db/trust.p12 \
  --db-mtls-key-store-file=/etc/keycloak/db/client.p12 \
  --db-mtls-key-store-password="${KC_DB_MTLS_KEY_STORE_PASSWORD}"
```

TLS success nepreukazuje correct database/schema. DNS target, certificate SAN, database identity a query read-back musia súhlasiť.

## 18. Incident `KC-PAY-73`

Atlas nasadil Keycloak 26.7 cez osem Pods. Každý mal default max pool 100, takže theoretical ceiling bol 800 connections pri database limite 500. Autoscaler počas login peak-u vytvoril ďalšie Pods; database odmietala connections a readiness oscilovala.

Súčasne prvý nový Pod spustil automatic schema update. Staršie Pods zostali v trafficu a písali podľa predecessor assumptions. Jeden Admin REST request timeout-ol po database failover; automation ho zopakovala bez read-backu a prepísala concurrent client change.

```text
replica scaling × per-Pod pool max
→ database connection exhaustion

mixed version + automatic schema mutation
→ uncertain compatibility window

failover timeout + blind retry
→ duplicate/overwritten administrative state
```

Recovery znížila per-Pod pool a zaviedla global connection budget, oddelila migration job/account, runtime Pods spúšťala s `validate`, zastavila predecessor writers počas incompatible migration a pridala operation ID + GET/hash read-back pred retry.

## 19. Evidence-preserving containment a recovery

Zachovaj image/driver digests, Keycloak/database versions, JDBC URL hash, database/schema/user identity, credential/trust generations, pool configuration a runtime metrics per Pod, database connection/lock/slow-query evidence, migration logs/SQL hash/version table, backup snapshot ID, failover timeline a affected operation IDs.

Containment môže zastaviť autoscaling, odobrať traffic mixed-version Pods, zablokovať admin/import mutations a rezervovať connections pre recovery. Recovery obnoví pool budget, writer endpoint, schema compatibility a cache/session convergence. Až potom sa vykoná fresh login, refresh, admin update a second no-op.

## 20. Acceptance matrix

Positive:

```text
fresh login/admin mutation
→ connection acquired
→ transaction committed
→ cache invalidated
→ read-back a downstream operation succeed
```

Recovery:

```text
writer failover alebo pool saturation
→ bounded failures
→ connections recreated
→ unknown operations reconciled
→ second operation succeeds once
```

Forbidden:

```text
runtime account attempts DDL
→ database denies

wrong schema/database endpoint
→ startup/target guard rejects

incompatible predecessor Pod po migration
→ traffic/deployment policy rejects
```

Second-migration test obnoví production-like backup do isolated environmentu a aplikuje rovnaký artifact. Second-scale test overí global connection budget pri max replicas a database failover.

## Kontrolné otázky

- Ktorý exact database, schema, writer endpoint a migration generation používame?
- Ktorý account vlastní runtime DML a ktorý migration DDL?
- Aký je súčet pool maxima pri max replica count a recovery reserve?
- Je pool lifetime kratší než database/network timeout?
- Čo znamená timeout pre transaction outcome a ako sa vykoná read-back?
- Ktoré server versions smú súčasne zapisovať do danej schema generation?
- Je migration automatic, manual alebo validate a kto je jediný writer?
- Máme restore-tested backup a vopred definovaný binary/schema rollback boundary?
- Prešli failover, saturation, wrong-schema, mixed-version, unknown-outcome a second-migration testy?

## Primárne zdroje

- [Keycloak — Configuring the database](https://www.keycloak.org/server/db)
- [Keycloak — Configuring Keycloak for production](https://www.keycloak.org/server/configuration-production)
- [Keycloak — Database connection pool concepts](https://www.keycloak.org/high-availability/concepts-database-connections)
- [Keycloak — Upgrading Guide](https://www.keycloak.org/docs/latest/upgrading/)
- [Keycloak — Supported configurations](https://www.keycloak.org/server/supported-configurations)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: TLS, truststores, cookies, headers a production hardening](tls-truststores-cookies-headers-production-hardening.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Infinispan caches, clustering a session behavior →](infinispan-caches-clustering-session-behavior.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
