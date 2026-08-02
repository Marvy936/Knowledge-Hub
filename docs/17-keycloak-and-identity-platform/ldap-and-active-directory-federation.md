# LDAP a Active Directory federation

Keycloak LDAP/Active Directory federation nie je jednorazový import používateľov. Je to runtime user-storage boundary, v ktorej Keycloak rozhoduje, ktoré identity a attributes číta z external directory, ktoré lokálne cachuje alebo importuje, kde validuje password, kam zapisuje zmeny, ako mapuje groups/roles a čo sa stane pri výpadku directory alebo pri konflikte s local userom. Rovnaký login môže použiť local Keycloak usera, imported LDAP proxy usera alebo non-imported federated usera podľa provider priority a storage lookup pathu.

Najčastejší omyl je považovať imported user record v Keycloak database za authoritative identity. Pri LDAP federation Keycloak password neimportuje; credential validation zostáva na LDAP/AD serveri. Imported local record je proxy/cache a miesto pre Keycloak-specific metadata podľa mapper a storage mode-u. Ak sa directory user zmaže, disable-ne alebo presunie, local record a active sessions nemusia okamžite zmiznúť bez sync, cache invalidation a session/revocation lifecycle-u.

## 1. Dominantný directory-to-session lifecycle

```text
login alebo user lookup
→ exact realm a LDAP provider generation
→ provider priority a user-storage resolution
→ LDAP connection, bind a search
→ external DN/objectGUID/entryUUID identity
→ mapper projection do Keycloak user modelu
→ import alebo non-import storage mode
→ password validation na LDAP/AD
→ Keycloak authentication/user/client session
→ token alebo assertion
→ directory change, sync, cache invalidation a session closure
```

Directory availability, identity lookup, attribute mapping, credential validation a local session sú odlišné states. Úspešný Admin Console connection test nepreukazuje user search, password bind, group mapper, writable attribute ani downstream authorization. Úspešný login nepreukazuje, že directory disable alebo group removal sa okamžite prejaví vo všetkých sessions a tokens.

## 2. Exact LDAP federation subject

```yaml
ldapFederationSubject:
  keycloak:
    deploymentGeneration: kc-2026-08-02-21
    realm: atlas-prod
    issuer: https://sso.atlas.example/realms/atlas-prod
  provider:
    componentId: 3ce8...
    name: corp-ad
    configurationRevision: ldap-73
    vendor: ad
    priority: 0
    enabled: true
    connectionUrl: ldaps://dc01.corp.example:636
    usersDn: OU=People,DC=corp,DC=example
    bindDn: CN=svc-keycloak,OU=Service Accounts,DC=corp,DC=example
    bindCredentialGeneration: vault-ldap-19
    editMode: READ_ONLY
    importUsers: true
    syncRegistrations: false
    usernameLdapAttribute: sAMAccountName
    rdnLdapAttribute: cn
    uuidLdapAttribute: objectGUID
    userObjectClasses: [person, organizationalPerson, user]
    searchScope: subtree
    pagination: true
    connectionPooling: true
    cachePolicy: DEFAULT
  user:
    ldapDn: CN=Alice Payments,OU=People,DC=corp,DC=example
    externalId: objectGUID:3f2a...
    keycloakStorageId: f:3ce8...:3f2a...
    importedLocalUserId: 1d86...
  mapperRevision: ldap-mappers-42
  sync:
    fullSyncGeneration: sync-2026-08-02-01
    changedUsersSince: 2026-08-01T00:00:00Z
```

Provider display name nie je stable identity. Component ID vstupuje do federated storage ID a môže ovplyvniť WebAuthn user-handle dĺžku. Delete/recreate provider môže zmeniť component ID, storage IDs, mapper links a imported-user associations aj pri rovnakom name a URL.

## 3. Connection, bind a search boundaries

Connection test typicky overí network/TLS a bind credential. User lookup navyše potrebuje správny Users DN, object classes, username attribute, search scope, filters a permissions. Password validation môže použiť odlišný bind path ako service-account search.

```text
LDAPS TCP/TLS success
→ bind DN authentication
→ base DN search
→ user entry resolution
→ attribute read
→ user credential bind/validation
```

Každý transition potrebuje samostatný read-back. `Test connection` success nepreukazuje `Test authentication`, group search ani user password bind. Firewall alebo truststore zmena môže poškodiť iba jeden domain controller alebo node cohort.

## 4. TLS, truststore a Active Directory specifics

Production federation používa LDAPS alebo StartTLS podľa approved directory designu. Keycloak musí dôverovať issuing CA a validovať hostname/certificate chain. Vypnutie trust validation alebo použitie plaintext LDAP vystavuje bind credential a password validation MITM riziku.

Active Directory často používa `sAMAccountName`, `userPrincipalName`, `objectGUID`, `memberOf`, paged results a vendor-specific account controls. `objectGUID` je binary identifier a mapper/provider ho musí normalizovať stabilne. DN sa mení pri move/rename, preto nemá byť jediným stable external ID.

Multi-domain alebo Global Catalog design mení search base, attributes a group resolution. Global Catalog nemusí obsahovať všetky attributes. Exact endpoint a directory topology patria do subjectu.

## 5. Import Users ON

Pri `Import Users=ON` Keycloak vytvorí local database record pri prvom lookup/login alebo sync. Record umožňuje ukladať Keycloak-specific metadata a efektívnejšie používať features, ktoré external store nepodporuje. User však zostáva federated a pri lookup-e môže Keycloak overovať existenciu v LDAP a dekorovať model mappermi.

```text
LDAP entry E1
→ first lookup/login
→ local imported user U1
→ federationLink/provider component
→ LDAP-backed attributes + local metadata
```

Import nie je snapshot authority. Password sa neimportuje. Unfiltered Admin API searches nad imported users môžu vyvolať LDAP lookup pre každý result a vytvoriť N+1 load. Large population potrebuje bounded filters a performance test.

## 6. Import Users OFF

Pri `Import Users=OFF` LDAP priamo backing-uje common user model bez persistent local user copy. Keycloak nemôže uložiť arbitrary local user-profile metadata, ak nie je mapované do LDAP. Niektoré features nemusia fungovať, ak directory model neposkytuje potrebné fields.

Non-import mode znižuje local copies a sync potrebu, ale zvyšuje runtime dependency na directory. Directory outage môže ovplyvniť user lookup aj administration. Role/group metadata sa môže ukladať alebo mapovať iba podľa provider/mappers semantics; nemožno predpokladať local write.

Storage mode sa má rozhodnúť pri vytvorení provider generation. Neskoré prepnutie Import Users alebo Edit Mode nemení automaticky už vytvorené mapper configurations.

## 7. Edit Mode: READ_ONLY, WRITABLE a UNSYNCED

`READ_ONLY` znamená, že Keycloak nemá zapisovať mapped user data do LDAP cez provider. Admin/user update môže zlyhať alebo sa obmedziť na local metadata podľa mapper storage.

`WRITABLE` povoľuje supported writes do directory. Keycloak service account potrebuje presné LDAP ACL. Write success v Keycloak-e musí byť read-backnutý z directory a ďalšieho loginu.

`UNSYNCED` typicky umožňuje uložiť user changes lokálne bez zápisu do LDAP pre imported users. Tým vznikajú dve authority vrstvy. Mapper môže čítať local database namiesto LDAP. Directory admin potom zmení attribute, ale Keycloak môže ďalej používať local override.

```text
LDAP authoritative department=finance
+ UNSYNCED local department=payments
→ effective value závisí od mapper configuration
```

Edit Mode label sám nestačí; každý mapper má read/write/import behavior, ktorý treba overiť.

## 8. Sync Registrations

`Sync Registrations=ON` znamená, že nový user vytvorený cez Keycloak môže byť vytvorený v LDAP. To premieňa Keycloak registration/Admin API na directory provisioning authority.

Production design potrebuje DN/RDN construction, required attributes, object classes, password write policy, duplicate handling a rollback. Partial outcome môže vytvoriť LDAP entry bez complete Keycloak metadata alebo naopak. Self-registration do corporate AD je typicky zakázaná.

`Sync Registrations=OFF` neznamená, že provider je úplne read-only; WRITABLE mapper môže stále meniť existing users.

## 9. Provider priority a user collision

Keycloak user lookup iteruje local storage a federation providers podľa modelu/priority. Dvaja providers môžu nájsť rovnaký username alebo email. Collision resolution nesmie byť náhodná.

```text
username alice
→ local user?
→ provider priority 0 corp-ad?
→ provider priority 1 partner-ldap?
```

Stable identity je provider component + external UUID, nie username. Migration medzi providers potrebuje explicitný account-link/session strategy. Reordering priority môže zmeniť, ktorý account sa autentizuje bez zmeny login inputu.

## 10. Password validation a credential authority

Keycloak nikdy neimportuje LDAP password. Pri login-e deleguje validation directory provideru. Password policy a lockout môžu byť na AD/LDAP strane; Keycloak brute-force detection môže pridať ďalšiu vrstvu.

```text
Keycloak login attempt
→ user resolved to LDAP provider
→ LDAP password validation/bind
→ directory account state
→ Keycloak brute-force/session logic
```

AD account disabled, locked, expired password alebo logon restriction môžu mať podobný Keycloak symptom. Admin Console user `enabled=true` nepreukazuje directory account eligibility.

Password reset cez Keycloak funguje iba ak provider/edit mode a directory permissions podporujú write. Inak má recovery smerovať na directory-owned workflow.

## 11. LDAP mappers

Mappers prekladajú LDAP attributes a relationships do Keycloak user modelu. User Attribute mapper, Full Name mapper, Group mapper, Role mapper, Hardcoded mapper a MSAD account-control mapper majú rozdielne authority a sync behavior.

Mapper contract:

```text
LDAP attribute alebo relationship
→ mapper component ID a configuration
→ import/read/write direction
→ Keycloak property/attribute/group/role
→ token/client-scope projection
```

`memberOf` alebo group search môže vytvoriť nested group graph. Active Directory transitive groups a LDAP nested groups nemajú jednotnú semantics. Privilege mapper potrebuje expected group population, recursion, DN normalization a removal test.

## 12. Group a role federation

LDAP group mapper môže importovať alebo mapovať directory groups na Keycloak groups. Role mapper môže mapovať directory roles na realm/client roles podľa designu. Organizational group nie je automaticky permission role.

```text
AD group CN=Settlement-Approvers
→ Keycloak group /corp/settlement-approvers
→ explicit client-role mapping settlement-api.approve
```

Pri removal z AD musí Keycloak effective group/role zmiznúť podľa sync/cache/session contractu. Existing access token môže privilege niesť do expiry. Full sync success nepreukazuje current token revocation.

## 13. Full sync a changed-users sync

Full sync prejde provider population a importuje/aktualizuje users podľa mapper semantics. Changed-users sync používa provider timestamp/change tracking a nemusí zachytiť všetky typy zmien podľa directory capabilities.

```bash
kcadm.sh create "user-storage/${PROVIDER_ID}/sync?action=triggerFullSync" \
  -r atlas-prod

kcadm.sh create "user-storage/${PROVIDER_ID}/sync?action=triggerChangedUsersSync" \
  -r atlas-prod
```

API response alebo sync counters preukazujú spracovanie provider operation, nie correctness každej identity. Acceptance používa named fixtures: create, rename, move, disable, attribute change, group add/remove a delete.

Scheduled periodic sync má overlap/concurrency, duration, failure alert a high-watermark contract. Full sync počas peak load môže preťažiť directory aj Keycloak database.

## 14. Delete missing users a stale records

Directory delete nemusí automaticky odstrániť imported Keycloak user podľa sync/configuration. Stale local record môže zostať pre sessions, audit alebo metadata. Delete policy potrebuje distinguish permanent deletion, temporary directory outage a move/rename.

Hard delete local user môže zničiť audit/federated links a pri neskoršom reimporte vytvoriť nový local user ID. Disable/tombstone môže byť bezpečnejší podľa compliance. Sessions a tokens sa riešia samostatne.

## 15. Cache policy

User storage cache znižuje LDAP load. Policy môže byť DEFAULT, EVICT_DAILY, EVICT_WEEKLY, MAX_LIFESPAN alebo NO_CACHE podľa Keycloak capabilities/configuration. Cache TTL vytvára revocation latency pre attribute/account changes.

```text
LDAP disabled user at 10:00
→ cached user/credential lookup
→ next login/session behavior do invalidation/expiry
```

Cache neznamená, že password validation sa vždy vykoná lokálne; exact provider path treba overiť. Admin-triggered cache clear môže zvýšiť LDAP load a nie je session revocation.

## 16. Connection pooling, failover a referrals

LDAP connection pooling znižuje setup cost, ale stale connections, certificate rotation a directory failover potrebujú test. Multiple LDAP URLs, DNS/load balancer alebo AD site-aware routing menia failure semantics.

Referrals môžu presmerovať search do iného servera/domainu. Automatic referral following rozširuje trust a credential exposure. Explicitne definuj, či sú referrals ignorované, followed alebo unsupported.

Timeouty majú byť bounded. Long LDAP timeout môže vyčerpať Keycloak request threads a zmeniť directory incident na identity-platform outage.

## 17. Kerberos/SPNEGO a AD

Keycloak môže kombinovať LDAP user data s Kerberos/SPNEGO authentication. Kerberos principal mapping, keytab, realm, DNS/SPN a browser negotiation tvoria samostatný trust chain.

Kerberos success identifikuje principal, ktorý sa musí správne mapovať na LDAP/Keycloak usera. Username normalization alebo multiple domains môžu linknúť wrong account. Fallback na password form musí mať explicitnú policy a assurance semantics.

## 18. Vault a bind credentials

LDAP bind credential je high-impact secret. Nemá byť plaintext v repository alebo environment dump-e. Keycloak Vault expression môže odkazovať na external secret source podľa deployment configuration.

Credential rotation lifecycle:

```text
successor bind account/password
→ secret source update
→ Keycloak loaded generation
→ connection/authentication tests
→ predecessor credential disable
```

Update secret source bez Keycloak reload/restart/read-back nemusí zmeniť active connection pool. Rotation acceptance testuje nový connection aj user lookup/password validation.

## 19. WebAuthn a federated storage IDs

WebAuthn user handle má limit 64 bajtov. Federated user storage ID môže mať formu `f:<provider-id>:<external-user-id>`. Dlhý provider component ID alebo external ID môže limit prekročiť.

Pred passkey rolloutom pre LDAP users zmeraj actual storage IDs. Provider delete/recreate môže zmeniť prefix a rozbiť identity continuity. Táto boundary spája federation design s MFA kapitolou.

## 20. Connected incident `KC-PAY-70`

Atlas používal AD provider `corp-ad` s Import Users ON, UNSYNCED edit mode a Group mapperom. Local administrator zmenil imported user attribute `tenant_id` na `orion`; mapper v UNSYNCED mode čítal local hodnotu. AD tím usera presunul a odstránil zo `Settlement-Approvers`, ale Keycloak cache a periodic sync ešte neprebehli.

User mal active session a access token s client role `settlement-api.approve`. AD account bol neskôr disable-nutý. Old Keycloak session a application session však pokračovali.

```text
AD group removal + account disable
→ stale imported/local mapper state
→ cached effective group/tenant
→ existing Keycloak session/token
→ privileged application operation
```

Recovery zaviedla READ_ONLY authority pre security attributes, explicitný group-to-client-role mapping, short cache/reconciliation SLA, named-fixture changed/full sync tests, session revocation pri leaver evente a API-side current workforce/tenant policy pre high-risk operations.

## 21. Evidence-preserving containment a recovery

Zachovaj provider component/config export, connection endpoint/certificate generation, bind credential generation bez secretu, LDAP DN a stable UUID, Keycloak storage/local user IDs, mapper configurations, sync run IDs/counters, cache policy, login events, sessions/tokens a business operations.

Containment môže disable-nuť provider alebo user, zablokovať high-risk operations a revoke-nuť sessions. Provider-wide disable má veľký blast radius. Recovery opraví mapper/edit/storage authority, vykoná bounded sync, overí directory read-back a uzavrie sessions/tokens/application state.

## 22. Positive, recovery a forbidden acceptance

Positive path:

```text
AD user fixture
→ exact provider resolution
→ LDAP password validation
→ intended attributes/groups
→ minimal client roles
→ protected operation succeeds
```

Forbidden paths:

```text
disabled/locked AD account
→ fresh login rejects

removed AD group
→ after bounded sync/cache SLA new token lacks role

wrong provider with same username
→ no accidental account resolution

READ_ONLY attribute update cez Keycloak
→ rejects

old bind credential po rotation
→ rejects

LDAP outage
→ bounded failure bez wrong local fallback identity
```

Second-login test po directory mutation, second-node test, full/changed sync fixtures, cache-expiry test, provider-priority collision test a session-descendant test uzatvárajú acceptance.

## 23. Troubleshooting a anti-patterny

Pri login failure oddeľ network/TLS, bind, search, user resolution, directory account state, password validation, Keycloak brute-force state, mapper exception a session creation. Pri stale attribute sleduj Import Users, Edit Mode, mapper read direction, sync mode/run, cache a token issuance time.

Anti-patterny sú: `imported user = local authority`, `Keycloak importuje LDAP password`, `connection test = login works`, `UNSYNCED = harmless cache`, `provider name = stable identity`, `full sync = sessions revoked`, `cache clear = leaver closure`, `AD group = automatická realm role`, `user enabled v Keycloak = AD account active`, `delete/recreate provider bez identity impact` a `bind secret rotation = loaded connections používajú successor`.

## 24. Kontrolné otázky

- Ktorý exact provider component/configuration a directory endpoint sa používa?
- Je user imported alebo non-imported a kto vlastní každý attribute?
- Aký Edit Mode a mapper direction platí?
- Kde sa validuje password a kde sa aplikuje lockout?
- Ako sa riešia username collisions a provider priority?
- Ktoré groups/roles sú security-significant a ako sa odoberajú?
- Aký je sync a cache revocation SLA?
- Čo sa stane pri LDAP outage, move, rename, disable a delete?
- Ako sa rotuje bind credential a overí loaded connection?
- Prešli second-login, second-node, wrong-provider, group-removal, disabled-user a old-session paths?

## Glossary impact

Relevantné pojmy: Keycloak user storage federation, LDAP provider component, federation link, storage ID, Import Users, Edit Mode READ_ONLY/WRITABLE/UNSYNCED, Sync Registrations, LDAP mapper, full sync, changed-users sync, cache policy, LDAP bind credential, objectGUID/entryUUID, provider priority, directory credential authority a federation revocation SLA.

## Primárne zdroje

- [Keycloak — Server Administration Guide: LDAP and Active Directory](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak — Server Developer Guide: User Storage SPI](https://www.keycloak.org/docs/latest/server_development/)
- [Keycloak — Vault configuration](https://www.keycloak.org/server/vault)
- [Microsoft — Active Directory Technical Specification](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Identity brokering](identity-brokering.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: User storage, synchronization a cache semantics →](user-storage-synchronization-and-cache-semantics.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
