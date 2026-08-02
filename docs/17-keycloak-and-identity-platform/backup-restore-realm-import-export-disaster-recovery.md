# Backup, restore, realm import/export a disaster recovery

Keycloak disaster recovery nezačína príkazom `kc.sh export`. Authoritative production state je rozdelený medzi databázu, realm signing a encryption keys uložené v nej, persistent sessions, external identity stores, provider/theme/image artifacts, runtime configuration, TLS a trust materials, DNS/load-balancer routes a downstream application sessions. Realm export zachytí veľkú časť realm configuration a users podľa zvolenej stratégie, ale nezahŕňa user/admin events, persisted sessions, workflow state ani revoked tokens. Preto je vhodný ako migration/configuration artifact alebo doplnkový logical backup, nie ako jediný DR mechanismus.

DR verdict musí definovať presný recovery point a recovery target. Obnova databázy do stavu T-15 minút môže vrátiť deleted client secret, starú role mapping alebo znovu aktivovať session, ktorú incident response medzitým revoked. Obnova realm JSON nad running clusterom môže vytvoriť stale caches. Zelený login po restore nepreukazuje správne keys, offline sessions, broker links, LDAP mappings, audit continuity ani business authorization.

## 1. Dominantný backup-to-business-recovery lifecycle

```text
business continuity objective
→ exact protected-state inventory a RPO/RTO
→ consistent database backup/PITR generation
→ immutable runtime/config/provider/theme/secret artifacts
→ optional realm export generation a documented exclusions
→ encrypted offsite retention a restore test
→ disaster declaration a target isolation
→ database/infrastructure restore
→ Keycloak image/config/schema compatibility
→ DNS/LB/TLS route activation
→ session/token/client/application reconciliation
→ protocol a business acceptance
→ failback a second-restore test
```

Každá šípka má vlastný owner a proof boundary. Snapshot completion nepreukazuje decryptability. Database restore success nepreukazuje schema compatibility s selected Keycloak image. Realm import exit code `0` nepreukazuje, že every user file bol načítaný alebo že caches sú clean. Login success nepreukazuje refresh/offline token, SAML metadata, signing-key continuity ani admin recovery.

## 2. Exact recovery subject

```yaml
recoverySubject:
  source:
    keycloakVersion: 26.7.0
    imageDigest: sha256:6a91...
    deploymentGeneration: kc-2026-08-02-28
    realm: atlas-prod
    databaseClusterId: atlas-keycloak-db-7
    databaseSchema: identity
    databaseWriterGeneration: db-writer-92
    schemaVersion: kc-schema-26.7
  backup:
    snapshotId: kc-db-snap-20260802T061500Z
    backupType: full-plus-wal-pitr
    transactionConsistentAt: 2026-08-02T06:15:00Z
    encrypted: true
    encryptionKeyGeneration: backup-kms-18
    checksum: sha256:84b2...
    retentionClass: monthly-12
  realmExport:
    artifact: atlas-prod-export-20260802.tar.zst
    exportMode: directory
    usersStrategy: different_files
    usersPerFile: 1000
    checksum: sha256:33ce...
    allNodesStopped: true
    documentedExclusions:
      - user-and-admin-events
      - persisted-sessions
      - workflow-state
      - revoked-tokens
  target:
    environment: dr-atlas-20260802
    clusterUid: 4d20...
    databaseClusterId: atlas-keycloak-db-dr-11
    canonicalHostname: https://sso-dr.atlas.example
  objectives:
    rpo: PT15M
    rto: PT2H
  exercise:
    restoreRunId: dr-test-2026-08-02-04
```

Bez transaction-consistent timestampu je RPO iba názov snapshotu. Bez image/schema generation sa restore môže spustiť na nekompatibilnej binary. Bez exclusions sa realm export nesprávne považuje za session/audit backup. Bez isolated target identity hrozí, že test restore pošle emaily, broker callbacks alebo Admin Events do production dependencies.

## 3. Chránený state inventory

Minimálny inventory:

```text
database data a WAL/redo logs
Keycloak image digest a optimized build
providers/themes a dependency digests
kc.conf, Operator CR, Secrets references a route manifests
TLS certificates/private keys a outbound truststores
realm signing/encryption key state v database
external LDAP/AD/IdP configuration a owners
SMTP/DNS/load-balancer configuration
backup encryption keys a restore credentials
application client secrets/private keys mimo Keycloak
runbooks, RPO/RTO a last restore evidence
```

Nie všetko sa má kopírovať rovnakým spôsobom. Runtime Secrets sa majú obnoviť zo secret managera podľa successor generation, nie z plaintext exportu. External LDAP users sa neobnovujú z Keycloak realm exportu, ak directory zostáva authority. Downstream application sessions môžu vyžadovať forced reauthentication po DR.

## 4. Database backup je primárny durable backup

Keycloak databáza obsahuje authoritative realm/client/user configuration, credentials metadata, keys, consents, persistent regular/offline sessions a migration metadata podľa version/features. Backup musí byť transactionally consistent a zahŕňať WAL/redo pre PITR.

```text
full snapshot
+ WAL/redo stream
→ restore do exact transaction timestampu
→ verify schema/version a data checks
```

Encryption musí pokryť data files, WAL/redo aj backup artifacts. Storage encryption bez access-control, KMS audit a deletion protection nestačí. Backup account nemá byť Keycloak runtime account.

Managed database snapshot alebo native backup tool musí mať documented consistency. Filesystem copy bez database-coordinated consistency môže byť nepoužiteľná.

## 5. RPO a časová konzistencia

RPO sa meria proti last durable application commit, nie proti upload timestampu backup file-u. Pri PITR treba zohľadniť:

```text
snapshot checkpoint
WAL archival lag
cross-region copy lag
KMS/key availability
restore catalog freshness
```

Ak database, Secret manager a DNS configuration obnovuješ z odlišných časov, môže vzniknúť cross-system inconsistency. Napríklad database obsahuje successor client secret generation, ale DR secret store má predecessor. Recovery manifest musí explicitne zvoliť coordinated generations alebo vykonať rotáciu po restore.

## 6. Realm CLI export

CLI export je server launch, ktorý načíta database state, zapíše JSON a skončí. All Keycloak nodes majú byť zastavené, aby počas exportu nevznikali concurrent realm/user modifications.

```bash
bin/kc.sh export --optimized \
  --realm atlas-prod \
  --dir /backup/keycloak/atlas-prod-20260802 \
  --users different_files \
  --users-per-file 1000
```

Directory mode je vhodnejší pre large user populations. Single-file export môže spotrebovať veľa memory; pri viac než približne 50 000 users official guide odporúča directory export.

File naming je contract:

```text
atlas-prod-realm.json
atlas-prod-users-0.json
atlas-prod-users-1.json
atlas-prod-federated-users-0.json
```

Nesprávny názov môže spôsobiť, že user files sa neimportujú. Export success musí zahŕňať file inventory, counts, sizes, checksums, JSON validation a source realm/database generation.

## 7. Realm export exclusions

Realm export nie je complete backup. Nezahŕňa:

```text
user events
admin events
persisted sessions
workflow state
revoked tokens
```

Okrem toho external systems zostávajú mimo artifactu: LDAP/AD authoritative records, external IdP keys/tokens, downstream application sessions, audit archive, certificates a secret manager data.

Ak DR požaduje session continuity alebo audit preservation, použije database backup a external audit backup. Realm export môže poslúžiť na rebuilding configuration do clean realm-u, no security descendants treba riešiť separately.

## 8. Export build-time a runtime side effects

`import` a `export` commands potrebujú database options. Ak nepoužiješ `--optimized`, command môže implicitne rebuild-nuť optimized server pri zmene build-time options. Spustenie z rovnakého mutable installation directory ako running server môže zmeniť next-start artifact.

```text
immutable export Job image
→ same optimized build digest ako source server
→ runtime DB options only
→ isolated filesystem/output volume
```

Export sa nemá spúšťať v live server Pod-e. Použi controlled Job alebo maintenance environment s read/write podľa commandu, rovnakým image digestom a bez listener ports conflictu.

## 9. Realm CLI import

```bash
bin/kc.sh import --optimized \
  --dir /restore/atlas-prod-20260802 \
  --override=false
```

Default `override` môže byť `true`, preto production recovery musí explicitne zvoliť semantics. Pri override musia byť všetky Keycloak nodes stopped. Import command sa nepripája do cache clusteru; overwrite realm-u pri running nodes vedie k inconsistent/stale caches.

```text
stop/fence all target nodes
→ verify target DB/schema
→ import
→ authoritative object/user count read-back
→ start fresh cluster generation
→ cache/session/protocol acceptance
```

Existing realm skip/overwrite nie je merge strategy. Partial desired-state updates patria do Admin REST/GitOps automation s object-level planom.

## 10. Startup import

```bash
bin/kc.sh start --import-realm
```

Startup import číta `.json` files z `data/import`; subdirectories ignoruje. Existing realms sa preskočia, aby restart neprepísal state. Server sa plne nespustí, kým import neskončí.

Tento model je vhodný pre first bootstrap alebo ephemeral test environment, nie continuous realm reconciliation. ConfigMap s realm JSON nie je authoritative production backup bez secrets, users, sessions a object IDs/generations.

## 11. Admin Console partial export/import

Admin Console partial export beží online a môže exportovať selected realm settings/resources, ale nie users. Sensitive values ako passwords/client secrets sú maskované `*`. Artifact `realm-export.json` nie je vhodný ako backup alebo server-to-server transfer proof.

Partial import umožňuje `Fail`, `Skip` alebo `Overwrite` pre existing resources. Online operation môže dočasne zaťažiť server pri large groups/roles/clients. Každý object potrebuje count/read-back a Admin Event correlation.

```text
partial export
→ administrative convenience/review artifact
≠ full backup
```

## 12. Environment placeholders v import files

Realm JSON môže obsahovať `${ENV_VAR}` placeholders. Import nemá obmedzenie na to, ktoré environment variables možno referencovať. To je powerful, ale môže neúmyselne vložiť sensitive environment values do realm attributes alebo export logs.

```json
{
  "realm": "${REALM_NAME}",
  "smtpServer": {
    "host": "${SMTP_HOST}"
  }
}
```

CI má allowlist-nuť placeholders, kontrolovať unresolved variables a zakázať generic secret names. Imported resolved values sa read-backnú bez zapisovania secrets do logs.

## 13. Restore target isolation

DR test alebo restore environment nesmie automaticky komunikovať s production clients a users.

```text
blocked outbound SMTP
non-production DNS/hostname
broker/LDAP read-only alebo test endpoints
no production webhook/event listener delivery
separate client redirects
restricted admin network
```

Ak restore používa production database snapshot, obsahuje production users, emails, client secrets a keys. Access je production-sensitive. Test operators a automation majú least privilege a audit.

## 14. Signing keys, issuer a tokens po restore

Database restore obnoví realm keys podľa backup pointu. Token vydaný po backup time môže mať signing key/session/revocation state, ktorý restored server nepozná. Token vydaný pred backup môže znovu vyzerať validný, ak revocation nastala po backup point-e.

```text
restore to T-15m
→ realm/session/revocation clock moves backward
→ evaluate all issued token descendants
→ force not-before/session revocation alebo rotate keys podľa incident scope-u
```

Canonical issuer musí byť rovnaký iba pri planned failover/DR. Test environment používa oddelený hostname a nesmie byť accepted production resource servers.

## 15. Admin access recovery

Po restore môže byť admin locked alebo MFA dependency unavailable. Keycloak poskytuje temporary admin recovery.

Všetky nodes musia byť stopped pred dedicated command:

```bash
export PASS_VAR="$(secret-tool-read temp-keycloak-admin)"

bin/kc.sh bootstrap-admin user --optimized \
  --username dr-temp-admin \
  --password:env PASS_VAR \
  --no-prompt
```

Alebo temporary service account:

```bash
export SECRET_VAR="$(secret-tool-read temp-keycloak-admin-service)"

bin/kc.sh bootstrap-admin service --optimized \
  --client-id dr-temp-admin-service \
  --client-secret:env SECRET_VAR \
  --no-prompt
```

Temporary account existuje iba na recovery a musí byť explicitne odstránený. Creation success nepreukazuje cleanup. Zachovaj actor, time, target DB/realm, operations a deletion evidence.

## 16. Infrastructure a runtime restore

Database bez matching runtime nestačí. Obnov:

```text
Keycloak image/provider/theme digests
Operator CR alebo deployment manifests
Secrets/truststores/TLS generations
hostname/proxy routes
cache/cluster configuration
monitoring/audit integration
```

Runtime image musí byť schema-compatible. Custom provider môže mať vlastné tables/config a migration. External Infinispan state sa spravidla nereplikuje z database backupu; session/cache model určuje, čo sa rebuildne.

## 17. Backup integrity a retention

Každý artifact má checksum, encryption key, immutability/retention lock, deletion policy a restore catalog. Backup bez testovaného decrypt key je nepoužiteľný. KMS key deletion alebo region outage môže zablokovať restore.

```text
backup write
→ checksum
→ encryption
→ immutable retention
→ offsite/cross-account copy
→ periodic restore
→ expiry/deletion approval
```

Retention musí spĺňať legal/privacy requirements. Dlhé backup retention môže uchovávať deleted users a credentials; restore process potrebuje post-restore reconciliation s authoritative deletion/legal state.

## 18. Restore validation ladder

```text
artifact checksum/decryption
→ database engine restore
→ schema/version integrity
→ Keycloak startup/readiness
→ realm/client/user/key counts
→ OIDC discovery/JWKS a SAML metadata
→ login, MFA, broker, LDAP, refresh/offline token
→ admin mutation a audit event
→ downstream API/business operation
→ second restart/failover
```

Každý level dokazuje iba svoj outcome. SQL row count nepokryje mapper semantics. Login nepokryje offline tokens. API `200` nepokryje tenant/resource authorization.

## 19. Failback

DR site failback potrebuje source-of-truth decision. Po DR activation vzniknú nové writes, sessions a admin changes. Nemožno jednoducho obnoviť old primary snapshot a prepnúť DNS.

```text
freeze alebo replicate DR writes
→ reconcile database/config/secret generations
→ restore/upgrade primary
→ protocol/business canary
→ controlled traffic switch
→ retain rollback window
```

Ak architecture nemá supported reverse replication, failback môže byť nový migration/restore exercise s downtime. RPO/RTO pre failback sa dokumentuje separately.

## 20. Incident `KC-PAY-77`

Atlas považoval nightly realm export za complete backup. Export bežal popri aktívnych Pods a zachytil realm/client configuration, ale nie persisted sessions, events ani revoked tokens. Pri database corruption obnovili clean database a importovali JSON s `--override=true`, zatiaľ čo jedna stale Keycloak site zostala running.

Users sa vedeli prihlásiť, preto tím označil recovery za úspešnú. Offline sessions chýbali, SAML signing-key generation sa líšila od partner metadata, temporary admin zostal aktívny a restored revocation state opäť akceptovala token kompromitovaný pred incidentom. Email listener poslal reset messages production users z test restore-u.

```text
logical export treated as full backup
+ live import/cache inconsistency
+ missing token/session/audit descendants
+ non-isolated restore target
→ green login, ale unsafe recovery
```

Recovery prešla na encrypted database PITR plus immutable runtime/secret artifacts. Realm export zostal doplnkovým migration artifactom s exclusions manifestom. Restore environment blokuje SMTP/webhooks, všetky nodes sa fence-nú pred import/restore a acceptance zahŕňa keys, sessions, revocation, audit, external dependencies a temporary-admin deletion.

## 21. Evidence-preserving containment a recovery

Zachovaj corrupt/source database identifiers, backup/PITR catalog, WAL lag, checksums/encryption key generations, realm export inventory/counts/exclusions, image/provider/theme/config/Secret digests, DNS/LB/TLS state, keys/sessions/token evidence, restore commands/logs a every temporary admin operation.

Containment zastaví writes, fence-ne stale sites, izoluje restore target a chráni backup artifacts. Recovery zvolí exact point, obnoví compatible runtime, reconciles cross-system generations a vykoná full validation ladder. Backup sa neprepíše ani nemaže počas incidentu.

## 22. Acceptance matrix

Positive:

```text
scheduled backup/export
→ checksum/encryption/retention
→ isolated restore
→ protocol a business journeys succeed
```

Recovery:

```text
database/site loss
→ restore within RPO/RTO
→ keys/config/sessions podľa contractu
→ controlled route activation a failback
```

Forbidden:

```text
realm export označený ako complete session/audit backup
→ DR review rejects

import override pri running target clusteri
→ runbook/admission gate rejects

temporary admin po recovery
→ cleanup gate fails

restore test sends production email/webhook
→ network isolation rejects
```

Second-restore test používa iný backup generation a iný operator. Second-failure test reštartne/failoverne restored cluster pred acceptance closure.

## Kontrolné otázky

- Čo je authoritative backup: database, realm export alebo oba s rôznymi účelmi?
- Ktoré state types realm export explicitne nezahŕňa?
- Boli všetky nodes stopped pre consistent export a override import?
- Aký exact transaction timestamp, schema a image generation obnovujeme?
- Sú backup, WAL/redo a encryption keys dostupné mimo failure domainu?
- Je restore target izolovaný od production SMTP, callbacks a routes?
- Čo sa stane s tokens, sessions a revocation po point-in-time rollbacku?
- Bol temporary admin odstránený a auditovaný?
- Prešli checksum, schema, keys, login, MFA, broker, LDAP, refresh/offline token, audit, business a second-restart testy?

## Primárne zdroje

- [Keycloak — Importing and exporting realms](https://www.keycloak.org/server/importExport)
- [Keycloak — Configuring the database](https://www.keycloak.org/server/db)
- [Keycloak — Bootstrapping and recovering an admin account](https://www.keycloak.org/server/bootstrap-admin-recovery)
- [Keycloak — High availability overview](https://www.keycloak.org/high-availability/introduction)
- [Keycloak — Upgrading Guide](https://www.keycloak.org/docs/latest/upgrading/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: High availability, multi-AZ a multi-cluster trade-offs](high-availability-multi-az-multi-cluster-trade-offs.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Upgrades, migration guides a rollback boundaries →](upgrades-migration-guides-rollback-boundaries.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
