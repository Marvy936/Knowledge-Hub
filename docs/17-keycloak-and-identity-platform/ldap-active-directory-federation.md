# LDAP a Active Directory federation

Keycloak LDAP alebo Active Directory federation nie je jednorazový import users. Je to runtime user-storage provider, ktorý spája directory connection, bind identity, search namespace, stable LDAP identifier, attribute a group/role mappers, local import/cache state, password-validation authority, synchronization jobs a Keycloak sessions. Rovnaký username môže existovať lokálne aj vo viacerých providers; provider priority a lookup path preto rozhodujú, ktorý identity subject sa skutočne načíta.

Najčastejší omyl je považovať úspešný full sync za dôkaz, že login, group authorization a offboarding fungujú. Full sync môže vytvoriť local users, ale password sa nikdy neimportuje; login stále závisí od LDAP availability. Changed-users sync môže vynechať deletion alebo zmenu, ktorú directory modification timestamp nereprezentuje podľa očakávania. Imported user môže mať stale group mapping, ale existujúca Keycloak alebo application session zostane aktívna aj po directory disable. Directory federation acceptance preto sleduje source entry, local representation, mapper/sync generation, credential validation a descendants oddelene.

## 1. Dominantný directory-entry-to-session lifecycle

```text
directory identity a attribute authority
→ exact Keycloak LDAP provider generation
→ secure connection a bind identity
→ user DN/search filter a stable UUID lookup
→ Import Users on-demand/full/changed sync alebo non-import runtime model
→ LDAP mapper projection do common user model
→ local Keycloak user/storage ID a cache
→ password bind alebo alternative authentication
→ Keycloak user/client session
→ token/assertion claims a downstream authorization
→ directory change, sync/cache invalidation, session revocation a second-login validation
```

Každá šípka má vlastný writer a failure mode. Directory môže byť authoritative pre `mail`, ale Keycloak UNSYNCED mapper používa local value. Sync môže aktualizovať attribute, ale protocol mapper stále číta starý custom attribute. LDAP account môže byť disabled, no local imported user zostane visible. Provider lookup môže zlyhať a Keycloak neprejde na ďalší configured provider, pretože duplicate usernames/emails by mohli načítať nesprávneho človeka.

## 2. Exact LDAP provider subject

```yaml
ldapFederationSubject:
  keycloak:
    deploymentGeneration: kc-2026-08-02-09
    realm: atlas-prod
    realmRevision: realm-304
  provider:
    name: workforce-ad
    componentId: 9f66...
    providerRevision: ldap-58
    enabled: true
    priority: 0
    vendor: ad
    connectionUrls:
      - ldaps://dc1.corp.example:636
      - ldaps://dc2.corp.example:636
    connectionTimeoutMs: 3000
    truststoreGeneration: trust-17
    bindDn: CN=svc-keycloak,OU=Service Accounts,DC=corp,DC=example
    bindCredentialGeneration: vault-42
    usersDn: OU=People,DC=corp,DC=example
    searchScope: subtree
    customUserFilter: '(&(objectClass=user)(employeeType=active))'
    usernameLdapAttribute: sAMAccountName
    rdnLdapAttribute: cn
    uuidLdapAttribute: objectGUID
    userObjectClasses: [person, organizationalPerson, user]
    importUsers: true
    editMode: READ_ONLY
    syncRegistrations: false
    cachePolicy: DEFAULT
    removeInvalidUsersDuringSearches: false
    enableLdapPasswordPolicy: true
  mappers:
    revision: ldap-mappers-33
    coreAttributes: [username, email, firstName, lastName]
    groups: ad-groups-v4
    enabledState: msad-account-v3
  synchronization:
    lastFullSync: 2026-08-01T01:00:00Z
    lastChangedSync: 2026-08-02T05:55:00Z
    changedSyncGeneration: sync-771
  user:
    ldapDn: CN=Dana Settlement,OU=People,DC=corp,DC=example
    ldapUuid: 748c...
    keycloakUserId: f:9f66...:748c...
    localRevision: user-911
```

Provider display name, username alebo DN nie sú dostatočný identity subject. DN a `cn` sa môžu zmeniť pri move/rename. Stable link používa `entryUUID`, AD `objectGUID` alebo iný provider-specific unique identifier, ktorý musí zostať konzistentný naprieč LDAP replicas.

## 3. Connection, TLS a bind identity

LDAP connection URL určuje directory endpoint a transport. Production používa LDAPS alebo StartTLS podľa podporovaného deployment contractu. Keycloak musí dôverovať directory certificate chain cez svoj truststore; deprecated `Use Truststore SPI` sa spravidla necháva na `Always`.

```text
Keycloak node
→ DNS a TCP connection
→ TLS handshake a certificate verification
→ LDAP bind identity
→ search alebo password bind
→ LDAP result
```

`Test connection` preukazuje network/TLS endpoint reachability z konkrétneho Keycloak node/runtime. `Test authentication` preukazuje bind credential voči vybranému serveru. Ani jedno nepreukazuje user search/filter, replica consistency, mapper semantics ani failover po už vytvorenom connectione.

Bind account má minimal search/read a podľa WRITABLE/Sync Registrations aj presné write permissions. Broad directory administrator credential v Keycloak configuration rozširuje compromise blast radius. Rotation potrebuje overlap alebo koordinovaný update všetkých Keycloak generations a second-bind test.

## 4. Multiple LDAP URLs: sequential failover, nie load balancing

Connection URL môže obsahovať space-separated URLs:

```text
ldaps://dc1.corp.example:636 ldaps://dc2.corp.example:636
```

JNDI skúša endpoints zľava doprava. Použije prvý reachable server. Je to connection-time sequential failover, nie round-robin load balancing. Ak established connection zlyhá počas operation, current operation môže zlyhať; nový connection znova prejde URL list.

Všetky URLs musia smerovať na replicas rovnakého directory namespace-u a entries musia mať rovnaký unique ID. Dva nezávislé LDAP servers s rovnakými usernames, ale odlišnými `entryUUID/objectGUID`, vytvoria pri failoveri identity drift, duplicate imports alebo authentication failure.

Connection timeout sa násobí počtom nedostupných endpoints. Silent firewall drop môže predĺžiť login o celý timeout pre každý URL. Clean TCP refusal failoveruje rýchlejšie. Acceptance zahŕňa first-server down, mid-operation failure, second replica read, stable UUID a návrat predecessor servera.

## 5. User search namespace a identity attributes

`Users DN`, search scope a custom filter určujú directory population. `subtree` môže zahrnúť viac organizational units; `one-level` iba direct children. Príliš široký base/filter zvyšuje sync a accidental-import blast radius. Príliš úzky filter môže vynechať movers alebo newly activated users.

```text
Users DN
+ search scope
+ object classes
+ custom LDAP filter
→ candidate entries
→ username/UUID/RDN mapping
→ Keycloak user subjects
```

Username LDAP attribute je login/display identifier. RDN attribute určuje entry naming pri creation/move. UUID attribute drží stable identity. V Active Directory je typický `sAMAccountName` username a `objectGUID` stable identifier; `userPrincipalName` môže slúžiť ako alternate login, ale jeho suffix a case semantics musia byť explicitné.

Keycloak local storage typicky normalizuje username/email na lowercase pri Import Users. Pri Import Users off môže LDAP query zachovať case-sensitive hodnoty, no nie všetky Keycloak features s nimi fungujú spoľahlivo. Odporúčaný contract je case-insensitive unique login namespace.

## 6. Import Users ON

Pri Import Users ON Keycloak vytvorí local representation pri prvom login-e, admin searchi alebo syncu. Local record nesie storage-provider link a Keycloak-specific data, zatiaľ čo LDAP mappers môžu pri fetchi znovu čítať directory values.

```text
LDAP entry E-77
→ first query/login/full sync
→ local imported user U-911
→ storage provider ID + external UUID
→ local roles/credentials/session metadata podľa mapper/storage modelu
```

Výhoda je dostupnosť Keycloak features a efektívne local joins pre session/role/profile data. Nevýhoda je duplicated identity state a sync/cache complexity. Unfiltered Admin Console search môže pre každý imported user vykonať LDAP validation/search a výrazne zaťažiť directory.

Password sa neimportuje. Successful sync nevytvorí local password. Login používa LDAP password validation, pokiaľ edit mode/UNSYNCED alebo iný credential provider nevytvoril local credential path.

## 7. Import Users OFF

Pri Import Users OFF LDAP provider dynamicky reprezentuje users bez persistentnej local copy common user state-u. Keycloak features vyžadujúce local per-user data môžu byť obmedzené. Nemapované attributes, local metadata, disable flag, groups alebo roles nemožno uložiť, ak ich nepodporuje LDAP mapper/provider.

```text
login alebo user query
→ LDAP provider lookup
→ transient common user model
→ mapped LDAP attributes/groups/roles
→ Keycloak session
```

Directory outage má okamžitý dopad aj na user lookup. Cache môže dočasne maskovať read path, ale password validation a missing data stále závisia od provider behavioru. Acceptance musí testovať unsupported local mutation a nesmie predpokladať, že Admin REST write sa uložil.

## 8. Edit modes: READ_ONLY, WRITABLE a UNSYNCED

**READ_ONLY** zakazuje update mapped username/email/name/attributes a password cez Keycloak. Directory zostáva authority.

**WRITABLE** zapisuje supported attribute a password changes do LDAP. Bind account a directory schema/policy musia write povoliť.

**UNSYNCED** ukladá zmeny locally v Keycloak DB, hoci LDAP je read-only alebo sa má zachovať directory data. To vytvára deliberate divergence: LDAP a Keycloak majú odlišných writerov pre rovnaký logical field podľa mapper configuration.

```text
LDAP mail=dana@corp.example
+ UNSYNCED local mail=dana.private@example.net
→ mapper/provider configuration rozhodne effective Keycloak value
```

Pri vytvorení provideru Keycloak generuje initial mappers podľa vendor, edit mode a Import Users. Neskoršia zmena edit mode alebo import switchu automaticky neprestaví mapper configuration. Migration preto auditne diffuje každý mapper; samotná zmena top-level selectu nestačí.

## 9. Sync Registrations a user creation

`Sync Registrations` umožní, aby new user vytvorený cez Keycloak bol zapísaný do LDAP. Vyžaduje WRITABLE provider, object classes, RDN, required attributes, creation DN a bind permissions. Relative User Creation DN môže oddeliť creation OU od search base.

```text
Keycloak user creation request
→ provider priority/selection
→ LDAP DN construction
→ LDAP add operation
→ stable UUID read-back
→ local imported representation
```

Ak je configured viac providers, priority a creation capability určujú target. User creation nesmie hádať provider podľa email domainu bez explicitnej platform policy. Second-run/read-back overí exact LDAP DN, UUID a local link.

## 10. Password validation a password update

Keycloak nikdy neimportuje LDAP password. Pri login-e validuje credential proti LDAP/AD, typicky user bindom alebo provider-specific operation. Password candidate prechádza Keycloak runtime, preto transport k directory musí byť chránený TLS a plaintext nesmie ísť do logs/traces.

Pri WRITABLE update Keycloak posiela password update directory serveru; directory vykoná vlastný hashing/storage. Keycloak realm password policy a LDAP policy sa môžu líšiť. `Enable LDAP password policy` môže reagovať na directory signal, že password musí byť zmenené, a pridať `UPDATE_PASSWORD`; Active Directory používa MSAD account mapper a vlastné account-control semantics.

UNSYNCED môže vytvoriť local password, čím sa password authority rozdelí od LDAP. Táto konfigurácia musí byť intentional a testovať, či directory disable alebo password change stále blokujú intended login.

## 11. Full sync, changed-users sync a on-demand import

Full sync iteruje celú LDAP population a vytvára/aktualizuje imported users. Changed-users sync spracúva entries vytvorené alebo zmenené od `lastSync` podľa provider/directory modification attribute. On-demand import nastáva pri login-e alebo query.

Odporúčaný bootstrap je initial full sync a potom periodic changed sync. Full sync je drahší, ale zachytí drift, ktorý changed timestamp alebo filter missed. Changed sync nemusí reprezentovať deletions, group membership changes alebo server clock/replication anomalies podľa directory behavioru.

```text
sync operation ID S-771
+ provider component ID
+ sync type full/changed
+ predecessor lastSync
→ searched LDAP population
→ added/updated/failed counts
→ successor lastSync
→ sampled entry/local read-back
```

Green job nepreukazuje complete population, ak search filter alebo base je wrong. Acceptance porovná expected population, exact stable IDs, movers/leavers, group membership, disabled accounts a failed entries.

## 12. Admin REST sync a connection tests

Provider component inventory:

```bash
kcadm.sh get components \
  -r atlas-prod \
  -q type=org.keycloak.storage.UserStorageProvider \
  | jq '[.[] | {id,name,providerId,parentId,config}]'
```

Manual full alebo changed sync používa component ID a provider sync action podľa Admin REST representation:

```bash
PROVIDER_ID='9f66...'

curl --fail --silent --show-error \
  --request POST \
  --header "Authorization: Bearer ${ADMIN_TOKEN}" \
  "https://sso-admin.atlas.example/admin/realms/atlas-prod/user-storage/${PROVIDER_ID}/sync?action=triggerFullSync" \
  | jq .
```

Connection/authentication tests overujú uloženú candidate configuration, ale ich exact REST payload sa viaže na Keycloak version. Automation má používať current Admin REST contract a uložiť sanitized request/config hash. Test result nie je runtime sync alebo user-login evidence.

Independent directory observation:

```bash
ldapsearch \
  -H 'ldaps://dc1.corp.example:636' \
  -D 'CN=svc-keycloak,OU=Service Accounts,DC=corp,DC=example' \
  -W \
  -b 'OU=People,DC=corp,DC=example' \
  '(&(objectClass=user)(sAMAccountName=dana.settlement))' \
  distinguishedName objectGUID sAMAccountName userPrincipalName mail memberOf userAccountControl pwdLastSet modifyTimestamp
```

`ldapsearch` preukazuje directory state z konkrétneho endpointu s konkrétnym bind actorom. Nepreukazuje, čo Keycloak cache alebo local import práve používa.

## 13. LDAP mappers ako ownership graph

LDAP mappers sa spúšťajú pri login-e, initial registration/importe a Admin Console query. Initial provider creation pridáva core mappers; ďalšie mappers môžu mapovať attributes, full name, groups, roles, hardcoded data alebo MSAD account state.

**User Attribute Mapper** mapuje jeden LDAP attribute na Keycloak property/attribute a definuje read/write/always-read/import behavior.

**FullName Mapper** rozkladá alebo skladá `cn` a first/last name. Pri AD creation a `cn` ako RDN musí fallback a password-change behavior sedieť, inak môže vzniknúť opakovaný forced-password-change loop.

**Group/Role LDAP Mapper** prepája LDAP groups/roles s Keycloak groups/roles. Membership retrieval mode, group DN, member attribute, membership type a sync direction určujú blast radius.

**MSAD User Account Mapper** interpretuje AD account disabled, password expired a related account-control state.

Mapper overlap je risk. Dva mappers zapisujúce rovnaký Keycloak field s odlišnou read/write strategy vytvárajú nondeterministic alebo stale effective value. Inventory musí mať jedného ownera pre každý security-relevant field.

## 14. Active Directory-specific identity a account state

Active Directory používa `objectGUID` ako stable unique ID, `sAMAccountName` ako tradičný login, `userPrincipalName` ako UPN a `userAccountControl`/password metadata pre account state. DN sa mení pri move, `cn` pri rename; nesmú byť stable linkom.

AD group membership môže byť nested a large. LDAP group mapper musí explicitne definovať membership recursion/strategy a token projection nemá bez limitu publikovať celý graph. Domain controllers majú replikáciu a eventual consistency; password alebo group change môže byť okamžite viditeľný iba na jednom DC. Sequential URL failover môže preto zmeniť observed generation.

Disabled alebo locked AD account nie je totožný s Keycloak brute-force state. Admin musí čítať directory account state aj Keycloak attack-detection/session state. Enable LDAP password policy podporuje prompting pri directory „must change password“ signal-e, ale nejde o úplnú abstrakciu všetkých AD password controls.

## 15. Provider priority, duplicates a failure behavior

Keycloak hľadá local DB a configured storage providers podľa lookup semantics/priority. Ak high-priority provider pri lookupu zlyhá, Keycloak operation zruší; automaticky neprejde na ďalší provider. Dôvodom je bezpečnosť: ďalší provider môže obsahovať duplicate username/email pre iného človeka.

```text
lookup username dana.settlement
→ local/import link alebo provider P1
→ P1 network failure
→ login/query fails
≠ silent fallback to P2 dana.settlement
```

Pre availability sa používajú replicas v jednom providerovi, nie independent providers ako identity failover. V realm-e má zostať local emergency administrator s strong credential/MFA, ktorý nevyžaduje LDAP lookup a umožní provider disable alebo recovery.

Provider disable preskočí provider pri nových lookups. Imported users môžu zostať locally visible read-only podľa configuration, ale password validation a mapper decoration môžu stále zlyhať alebo byť unavailable. Emergency procedure sa testuje vopred.

## 16. Cache a loaded effective state

Keycloak user cache znižuje LDAP reads. Cache policy a invalidation určujú, ako dlho sa directory attribute alebo existence drift môže maskovať. Full/changed sync, admin mutation alebo cache clear môžu invalidovať entries, ale active sessions/token claims sú ďalšie snapshots.

```text
LDAP entry generation D2
→ cache ešte D1
→ imported local state L1/L2 podľa mappera
→ active user session S1
→ access token T1
```

Directory disable nemusí okamžite zneplatniť T1. Recovery potrebuje cache invalidation/read-back, session revocation a resource-server token policy. Restart všetkých nodes nie je náhrada za presný cache/session contract.

## 17. Deletion, invalid users a unlink semantics

Ak LDAP entry zmizne, `Remove invalid users during searches` môže pri lookupu odstrániť local imported user, ak nie je cached. Ak je disabled, stale local record môže zostať read-only a disabled. Sync/deletion behavior sa musí testovať na exact version a mapper configuration.

Delete local federated user môže odstrániť local representation/link, nie nevyhnutne LDAP entry v READ_ONLY mode. Pri WRITABLE/Sync Registrations môže deletion direction závisieť od provider operation. Destructive lifecycle má explicitný owner a backup/audit.

Leaver closure zahŕňa directory disable/delete, changed/full sync, cache, Keycloak user/session state, offline tokens, broker links a application sessions. Jediný „user absent in Admin Console“ nie je dôkaz.

## 18. Connected incident `KC-PAY-67` — stale AD membership a recycled broker link

Atlas mal READ_ONLY AD provider `workforce-ad` s Import Users ON, changed-users sync každých päť minút a group mapper pre nested group `Settlement-Admins`. Privileged user Dana bola presunutá do inej OU a odstránená z group. AD replikácia aktualizovala user entry `modifyTimestamp`, ale nested membership change nebola zachytená changed-users syncom podľa očakávania. Keycloak cache a local group mapping zostali stale.

Dana zároveň mala linked partner broker identity podľa emailu. Po offboardingu bola mailbox adresa recyklovaná a unsafe broker AutoLink pripojil nový external subject k stale local imported userovi. Existing Keycloak sessions a access tokeny neboli revoke-nuté.

```text
AD group removal/move
→ changed sync neaktualizuje intended nested mapping
→ stale local group/client role
→ recycled email broker AutoLink
→ new external subject dostane old local user
→ valid privileged token
→ settlement export
```

## 19. Evidence-preserving containment a recovery

Zachovaj provider component/config hash, connection URLs a selected endpoint, bind credential generation, LDAP entry DN/UUID/modifyTimestamp/account state, mapper IDs, sync operation IDs/results, lastSync, local user storage ID, cache/session state, broker links, token IDs a downstream requests. Bind password, user password a full tokens sa neukladajú do incident reportu.

Containment disable-ne high-risk client/operations, revoke-ne sessions a podľa potreby provider alebo broker path. Recovery opraví authoritative AD membership/account, spustí targeted/full sync, overí stable UUID a mapper output, invaliduje cache, odstráni unsafe broker link, obnoví owner mapping a testuje fresh login. Emergency local admin vykonáva recovery bez závislosti od failed LDAP provideru.

## 20. Positive, recovery a forbidden acceptance

Directory acceptance musí odlíšiť správny LDAP entry/provider/UUID mapping od cached, imported a session snapshots. Positive path overuje intended login a role projection, recovery path dokazuje sync/cache/session convergence a forbidden paths testujú disabled users, removed groups, wrong replicas, provider failures a unsupported writes bez identity substitution.

Positive path:

```text
active AD user + intended group
→ secure LDAP lookup/password validation
→ correct imported/transient user
→ mapper assigns exact Keycloak group/role
→ intended login a operation succeeds
```

Recovery path:

```text
provider/mapper/sync drift
→ directory a local evidence preserved
→ successor config alebo directory state corrected
→ full/targeted sync + cache invalidation
→ old sessions revoked
→ fresh login gets successor claims
```

Forbidden paths:

```text
disabled AD user
→ login rejected aj keď local imported record existuje

removed privileged group membership
→ fresh token bez role; old token/session podľa incident policy rejected

first LDAP URL down
→ second replica used s rovnakým objectGUID

independent second LDAP s rovnakým username, iným UUID
→ configuration rejected; no identity failover

high-priority provider lookup failure
→ operation fails; no silent next-provider user substitution

READ_ONLY mapped attribute update cez Admin API
→ reject/no authoritative mutation

UNSYNCED local override po deliberate LDAP change
→ drift visible a governed, nie ticho považovaný za LDAP truth
```

## 21. Troubleshooting

Pri login failure postupuj connection/TLS/bind → user search/filter → stable UUID/provider link → password bind/account state → mapper/cache → flow/session. Pri missing userovi porovnaj Users DN, scope, custom filter, object classes, case normalization, provider priority a import/cache state.

Pri stale role/group porovnaj LDAP membership na konkrétnych replicas, mapper configuration, nested-membership strategy, full/changed sync result, local user groups/roles, cache a actual token. Pri slow Admin search skontroluj unfiltered imported-user enumeration a per-user LDAP validation.

Pri failover teste zaznamenaj endpoint, timing a UUID. „Login fungoval“ bez dôkazu, ktorý replica endpoint odpovedal, nepreukazuje failover. Pri directory outage používaj local emergency admin; nevytváraj duplicate emergency user v druhom providerovi.

## 22. Kontrolné otázky

- Ktorý provider component, directory namespace a stable LDAP UUID je authoritative?
- Sú všetky connection URLs replicas rovnakého directory a zachovávajú UUID?
- Je Import Users ON alebo OFF a ktoré features/local metadata to mení?
- Ktorý Edit Mode a mapper vlastní každý security-relevant field?
- Kde sa validuje a ukladá password?
- Čo full a changed sync zachytia a čo môžu vynechať?
- Ako sa nested AD groups, disabled state a password-expiry signal mapujú?
- Čo sa stane pri provider failure, cache hit a directory deletion?
- Existuje testovaný local emergency administrator?
- Prešli first-server-down, wrong UUID, disabled user, removed group, stale token, second login a leaver paths?

## Glossary impact

Relevantné pojmy: Keycloak user federation, LDAP storage provider, Import Users, imported user, non-import storage mode, READ_ONLY, WRITABLE, UNSYNCED, Sync Registrations, Users DN, LDAP search scope, custom user filter, UUID LDAP attribute, objectGUID, LDAP mapper, MSAD User Account Mapper, full sync, changed-users sync, sequential LDAP failover, provider priority, local emergency admin, LDAP password validation a federated-user cache/session descendants.

## Primárne zdroje

- [Keycloak — Server Administration Guide: User storage federation, LDAP and Active Directory](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak — Admin REST API](https://www.keycloak.org/docs-api/latest/rest-api/index.html)
- [RFC 4511 — Lightweight Directory Access Protocol](https://www.rfc-editor.org/rfc/rfc4511.html)
- [Microsoft — Active Directory schema and objectGUID](https://learn.microsoft.com/windows/win32/ad/active-directory-schema)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Identity brokering](identity-brokering.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: User storage, synchronization a cache semantics →](user-storage-synchronization-cache-semantics.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
