# User storage, synchronization a cache semantics

Keycloak user storage nie je iba otázka, kde sa nachádza tabuľka `USER_ENTITY`. Realm môže používať local database, LDAP/Active Directory a viac custom User Storage SPI providers, pričom každý provider implementuje len určité capabilities: lookup, query, registration, credential validation/update, bulk operations alebo synchronization. Keycloak všetky sources prekladá do spoločného `UserModel`, ale to neznamená, že každý field, credential alebo role má rovnakého writer-a a rovnakú freshness.

Cache ďalej oddeľuje authoritative source od loaded state-u. User objekt načítaný podľa ID, username alebo emailu sa môže dostať do local in-memory user cache; v clustri funguje ako invalidation cache, kde mutation evictuje entry a invalidation sa propaguje ostatným nodes. Provider môže cez `OnUserCache` pridať vlastné cached metadata. Ak však external store zmení usera mimo Keycloak-u a nevznikne Keycloak invalidation alebo synchronization event, cache, imported local copy, active session a token môžu reprezentovať štyri odlišné generations.

## 1. Dominantný external-store-to-token lifecycle

```text
external alebo local identity authority
→ exact User Storage Provider component a deployed provider generation
→ provider priority a lookup selection
→ capability-specific user/credential operation
→ imported local copy alebo federated adapter
→ UserModel a provider/storage ID
→ user cache a custom cached metadata
→ authentication/session creation
→ client scopes a token/assertion projection
→ external mutation, synchronization alebo invalidation
→ session/token descendant closure a second-login validation
```

Každý transition musí mať vlastný read-back. Successful `getUserByUsername()` nepreukazuje, že query/count/admin-console capabilities fungujú. Imported user v local DB nepreukazuje, že external credential alebo account stále existuje. Cache eviction neukončí active user session. Full synchronization neprepisuje už vydaný token.

## 2. Exact user-storage subject

```yaml
userStorageSubject:
  keycloak:
    deploymentGeneration: kc-2026-08-02-13
    realm: atlas-prod
    realmId: 7df3...
  provider:
    componentId: 43ad...
    componentName: workforce-jpa
    providerId: atlas-user-storage-jpa
    providerJarDigest: sha256:7b21...
    providerFactoryGeneration: provider-18
    priority: 0
    enabled: true
    importStrategy: true
    cachePolicy: MAX_LIFESPAN
    maxLifespanMs: 300000
    configurationRevision: storage-61
  capabilities:
    lookup: true
    query: true
    count: true
    registration: false
    credentialValidation: true
    credentialUpdate: false
    importSynchronization: true
    importedUserValidation: true
    onUserCache: true
  externalUser:
    stableId: workforce:748c...
    username: dana.settlement
    externalRevision: ext-user-991
  localUser:
    userId: f:43ad...:748c...
    importedLocalId: 4b8e...
    federationLink: 43ad...
    localRevision: local-user-418
  cache:
    node: keycloak-2
    cacheTimestamp: 2026-08-02T06:15:12Z
    customEntitlementRevision: ent-77
  descendants:
    userSessionId: 04d9...
    clientSessionId: 9f31...
    accessTokenJti: 17aa...
```

Provider name a username nestačia. Provider component ID identifikuje realm configuration; provider ID identifikuje factory implementation; JAR digest a server build generation identifikujú loaded code. User storage ID môže obsahovať provider component a external stable ID. Delete/recreate provider alebo zmena factory ID môže odpojiť imported users aj pri rovnakom display name.

## 3. Local storage a provider lookup order

Keycloak najprv rieši local user storage a linked imported users, potom prechádza enabled external providers podľa priority, kým nenájde match. Silent fallback na ďalší provider pri lookup failure sa nevykoná, pretože duplicate username alebo email by mohol načítať inú identitu.

```text
lookup dana.settlement
→ local/imported user resolution
→ linked provider validation/adaptation
OR
→ provider P1 lookup
→ provider P2 iba ak P1 vráti no-match, nie infrastructure failure
```

Provider priority je identity-selection policy. Dva providers s overlapping username/email namespace-om potrebujú explicitnú partition alebo globally unique identifier. Availability sa rieši replikami jedného source/provideru, nie nezávislým providerom s podobnými users.

## 4. User Storage SPI capability model

Custom provider implementuje `UserStorageProvider` a factory, ale reálne operácie prichádzajú cez capability interfaces. Keycloak zisťuje supported behavior podľa implementovaných interfaces a potom volá odlišné methods pri login-e, user searchi, Admin Console inventory, credential update alebo synchronization. Provider preto nemá deklarovať capability iba preto, že dokáže podobnú operáciu emulovať; každá capability musí mať authoritative source, transaction boundary, pagination alebo conflict semantics a explicitné failure správanie.

`UserLookupProvider` poskytuje lookup podľa internal storage ID, username alebo emailu a je základom authentication resolution. `UserQueryMethodsProvider` a `UserCountMethodsProvider` sú samostatná inventory capability: určujú filtering, pagination a count completeness pre Admin Console a Admin REST, preto successful lookup jedného usera nepreukazuje kompletný query surface. `UserRegistrationProvider` vlastní create/remove lifecycle a musí definovať stable external ID, duplicate detection a delete direction. `UserBulkUpdateProvider` pridáva scoped bulk mutation, pri ktorej sa per-item výsledky nesmú schovať za aggregate success.

Credential capabilities majú odlišnú authority než profile lookup. `CredentialInputValidator` rozhoduje, ktoré credential types provider vie authoritative overiť a čo znamená disabled, expired alebo unavailable source. `CredentialInputUpdater` zapisuje alebo odstraňuje credential a musí riešiť policy, partial external/local commit a descendant sessions. Provider môže validovať LDAP password a súčasne odmietať jeho update; implementácia jedného interface preto nesmie implicitne deklarovať druhý.

```java
public final class AtlasUserStorageProvider
        implements UserStorageProvider,
                   UserLookupProvider,
                   UserQueryProvider,
                   CredentialInputValidator,
                   ImportedUserValidation,
                   OnUserCache {
    // Každá capability má samostatný authority a failure contract.
}
```

Login success cez lookup+credential validation nepreukazuje search completeness. Admin Console môže byť prázdna, ak provider neimplementuje query capability, hoci login funguje. Naopak query capability bez credential validatora môže zobrazovať users, ktorí sa týmto providerom nevedia autentizovať.

## 5. Provider instance a transaction boundary

Provider factory vytvára provider instance per Keycloak transaction. Provider class preto nemá držať request-specific mutable state v static fields ani predpokladať long-lived singleton lifecycle. External DB transaction, Keycloak transaction a remote side effect nemusia commitnúť atomicky.

```text
Keycloak request transaction K-17
→ provider instance P-771
→ external read/write transaction E-42
→ Keycloak local mutation L-18
→ commit/rollback boundaries
```

Ak external write uspeje a Keycloak local transaction rollbackne, outcome je partial. Provider potrebuje idempotentný operation ID, authoritative read-back alebo compensating reconciliation. Exception message sama neurčuje, ktorá strana commitla.

## 6. Non-import federated adapter strategy

Pri non-import stratégii provider vracia adapter, ktorý implementuje `UserModel` nad external store alebo federated storage. Keycloak môže uložiť doplnkové attributes/roles/credentials vo federated storage, ak external source ich nepodporuje.

```text
external user stable ID
→ provider adapter
→ direct reads pre authoritative fields
+ federated local storage pre supplemental fields
→ common UserModel
```

Výhoda je menšia duplicated profile state. Nevýhoda je runtime dependency na external store a potreba presne definovať každý method/capability. Mapper alebo protocol code môže volať viac `UserModel` getters, než provider očakáva; N+1 remote reads môžu vytvoriť latency a outage amplification.

## 7. Import strategy

Import strategy vytvorí local Keycloak user a kopíruje vybrané external attributes. Local user má `federationLink` na provider component a môže byť proxied providerom pri ďalšom load-e.

```text
first external lookup
→ local user creation
→ federationLink=provider component ID
→ stable external ID attribute
→ imported profile/metadata
→ future local lookup + provider validation/proxy
```

Import znižuje external read load a umožňuje viac Keycloak features, ale vytvára synchronization problém. External rename, disable alebo deletion nemusí byť okamžite viditeľné. First import navyše zapisuje do Keycloak DB počas loginu, čo môže pri burst trafficu zvýšiť DB load a lock contention.

Stable external-link attribute musí byť read-only pre usera. Ak user môže meniť `LDAP_ID`, legacy ID alebo provider-specific link attribute, môže prepojiť local account na inú external identity.

## 8. `ImportedUserValidation`

Provider s import stratégiou môže implementovať `ImportedUserValidation.validate()`. Callback sa vykoná, keď linked local user načíta local storage. Môže usera proxy-nuť, aktualizovať alebo vrátiť `null`, čím sa local user odstráni.

```java
@Override
public UserModel validate(RealmModel realm, UserModel localUser) {
    ExternalUser external = externalStore.findByStableId(
        localUser.getFirstAttribute("external_id")
    );
    if (external == null || external.isDeleted()) {
        return null;
    }
    return new ImportedUserProxy(localUser, external);
}
```

Dôležitá hranica: ak je user už v user cache, local-storage load a `validate()` sa nemusia vykonať. Cache policy a invalidation preto ovplyvňujú deletion/disable latency. `validate()` návrat `null` odstraňuje local identity state a môže mať side effects na links; musí byť ohraničený exact stable ID a evidence.

## 9. `ImportSynchronization`

Provider factory môže implementovať `ImportSynchronization.sync()` a `syncSince()`. Admin Console potom zobrazí manual a periodic synchronization controls.

```java
public SynchronizationResult sync(
        KeycloakSessionFactory sessionFactory,
        String realmId,
        UserStorageProviderModel model) {
    // full population reconciliation
}

public SynchronizationResult syncSince(
        Date lastSync,
        KeycloakSessionFactory sessionFactory,
        String realmId,
        UserStorageProviderModel model) {
    // changed population reconciliation
}
```

Sync result counts nie sú complete proof. Potrebný je expected population, stable external IDs, failed-record inventory, predecessor/successor `lastSync`, deletion semantics a sampled local/external diff. `syncSince` musí jasne definovať inclusive/exclusive timestamp, clock skew, pagination a replay/idempotency.

## 10. User cache

Pri lookupu podľa ID, username alebo emailu Keycloak načíta `UserModel` a kopíruje jeho fields do local in-memory cache. V clustri je cache local na node, ale mutation eviction event sa distribuuje ostatným nodes. Nejde o shared strongly consistent user object.

```text
provider UserModel generation U-17
→ cache load na node A timestamp C-17
→ cache copy na node A
→ independent cache load na node B C-18
→ mutation/eviction event
→ invalidation propagation
→ next lookup reloads provider
```

Cache hit môže obísť provider read a imported validation. Cache invalidation preukazuje odstránenie snapshotu, nie ukončenie sessions alebo tokenov. Node outage/restart zmaže local cache, ale nemá byť recovery mechanizmom pre provider ownership chybu.

## 11. Cache policies

Provider model môže mať policy ako default cache, no-cache, max lifespan alebo daily eviction podľa podporovaných modelov. Policy definuje, kedy cache entry prestane byť reusable bez explicitnej mutation invalidation.

`MAX_LIFESPAN` ohraničuje staleness časom, ale nevytvára immediate offboarding. `EVICT_DAILY` je batch expiry, nie real-time revocation. `NO_CACHE` zvyšuje external-store load a latency. Default policy sa spolieha na mutation/invalidation behavior.

Policy acceptance potrebuje external change test, cache timestamp, node cohort a next lookup. Admin Console configured value nepreukazuje, ktorý snapshot používa active request.

## 12. `OnUserCache` a custom cached metadata

Provider implementujúci `OnUserCache` dostane callback pri cacheovaní usera a môže pridať provider-specific data do `CachedUserModel.getCachedWith()`.

```java
@Override
public void onCache(
        RealmModel realm,
        CachedUserModel cached,
        UserModel delegate) {
    cached.getCachedWith().put(
        "atlas.entitlementRevision",
        entitlementService.revisionFor(delegate.getId())
    );
}
```

Cached credentials alebo entitlements zvyšujú sensitivity cache a staleness risk. Provider musí invalidovať usera pri authoritative external change. Ak nemá event channel, použije bounded lifespan alebo query-time verification pre high-risk operation. Custom cached map nie je durable audit source.

## 13. Explicit cache eviction

SPI code môže získať `UserCache` a evictnuť usera, realm alebo celý cache cluster:

```java
UserCache cache = session.getProvider(UserCache.class);
cache.evict(realm, user);
```

Realm-wide eviction alebo `clear()` má veľký performance blast radius a môže vyvolať thundering herd proti external store. Preferuj exact user eviction po authoritative mutation. Po eviction-e vykonaj read-back na viacerých nodes alebo request cohortách a over provider generation.

## 14. Provider update, disable a remove

User storage providers sú generic Keycloak components. Update config mení component generation; custom provider JAR update mení loaded code generation a často vyžaduje `kc.sh build` a controlled server rollout.

Provider disable preskočí provider pri nových lookups. Imported local users môžu zostať dostupní v obmedzenom read-only stave, ale linked validation/credential paths sa menia. Provider remove môže odstrániť federation links alebo imported users podľa lifecycle a API behavioru. Destructive operation vyžaduje export/inventory a rollback boundary.

```text
component revision S-61
+ provider JAR digest P-18
→ successor config/code
→ node rollout cohort
→ provider loaded/read-back
→ user lookup/login canary
→ predecessor retirement
```

## 15. Provider failure a emergency administration

Ak high-priority provider hodí infrastructure exception pri lookupu, Keycloak operation zlyhá; nevyberie silent matching usera z ďalšieho provideru. Toto chráni identity integrity, ale môže blokovať login aj Admin Console user queries.

Realm potrebuje local emergency administrator uložený v Keycloak local storage, chránený strong MFA a testovaný bez external provideru. Emergency account slúži na provider disable/config recovery, nie na bežnú administráciu.

## 16. Sessions a tokens sú ďalšie snapshots

User cache reload po external disable ešte nezruší existujúcu user session. Keycloak session obsahuje authenticated identity a client sessions; access token je signed snapshot claims. Resource server môže pokračovať až do expiry alebo current-policy checku.

```text
external entitlement removed E2
→ cache still E1 alebo reload E2
→ user session S1 created under E1
→ access token T1 claims E1
→ application session A1
```

Offboarding alebo privilege incident uzatvára provider/cache, Keycloak sessions, offline tokens, access tokens a application sessions. Fresh login bez role je len jedna časť recovery.

## 17. Connected incident `KC-PAY-68` — cached entitlement a partial provider mutation

Atlas custom provider `workforce-jpa` čítal user profile z HR database a entitlement revision z oddelenej policy service. Provider pri `OnUserCache` uložil `settlement.export=true` do custom cache mapy s `MAX_LIFESPAN=30m`. HR mover odstránil Danine entitlement, ale external change nevyslal Keycloak eviction.

Súčasne automation zmenila provider configuration a client mapper v dvoch samostatných Admin API calls. Provider config commitol, mapper request timeoutol s unknown outcome. Niektoré nodes načítali successor provider code, iné ešte predecessor generation. Existing session a token pokračovali so stale export role.

```text
external entitlement E2 removed
→ user cache E1 bez invalidation
→ mixed provider generations P1/P2
→ unknown mapper mutation
→ session/token claims E1
→ privileged export
```

## 18. Evidence-preserving containment a recovery

Zachovaj provider component export/hash, provider JAR digest a node build generation, external user/revision, local user/federation link, cache timestamp/custom revision per node, sync operation IDs, Admin events, sessions/tokens a downstream requests. Nezapisuj raw credentials alebo sensitive cached values do incident notes.

Containment zablokuje high-risk API action, revoke-ne affected sessions/tokens a evictne exact users. Recovery zavedie authoritative external-change event alebo bounded cache policy, rolloutne jeden provider digest, read-backne component/mappers, reconciliuje unknown Admin API outcome a vykoná fresh login + stale-token negative test.

## 19. Positive, recovery a forbidden acceptance

Acceptance musí odlišovať lookup correctness, synchronization convergence, cache invalidation a descendant revocation. Positive path dokazuje intended source/user/provider generation; recovery path navyše uzatvára mixed code/config a stale sessions; forbidden paths chránia pred duplicate identity, cache bypassom validation a broad eviction side effects.

Positive path:

```text
external user E2
→ intended provider P2
→ local/imported adapter L2
→ cache C2
→ fresh session/token claims E2
→ intended operation succeeds
```

Forbidden paths:

```text
provider P1 infrastructure failure
→ no silent fallback to duplicate user in P2

external user deleted, stale cache hit
→ bounded expiry/event eviction forces authoritative reload

user edits stable external-link attribute
→ reject

provider config updated, old JAR node remains
→ rollout acceptance fails

cache evicted, old session/token still authorizes
→ recovery acceptance fails
```

## 20. Troubleshooting

Pri wrong user alebo stale attribute incidente sleduj local lookup, federation link, provider priority/component ID, provider JAR generation, imported validation, cache timestamp, custom cached values, session creation time a actual token. Pri Admin Console search probléme oddeľ lookup/query/count capability a external pagination.

Pri sync drift-e porovnaj full/since boundary, external revision, failed records, stable IDs a local writes. Pri cluster divergence zober rovnaký user request cez viac nodes a porovnaj cache timestamp/provider build. Restart všetkých nodes môže vyprázdniť cache, ale nepreukazuje opravu invalidation contractu.

## 21. Kontrolné otázky

- Ktorý source a provider component/JAR generation vlastní usera a každý field?
- Ktoré SPI capabilities provider skutočne implementuje?
- Je stratégia import alebo non-import a kde sa drží supplemental state?
- Kedy sa volá imported validation a kedy ho cache obíde?
- Ako full/since sync rieši pagination, timestamp a deletion?
- Ktoré custom metadata sa cacheujú a čo ich invaliduje?
- Ako sa rolloutuje provider code a config naprieč nodes?
- Existuje local emergency admin nezávislý od external provideru?
- Čo sa stane so sessions/tokens po source alebo cache zmene?
- Prešli duplicate-user, provider failure, stale cache, mixed generation a second-login paths?

## Glossary impact

Relevantné pojmy: Keycloak User Storage SPI, provider component generation, capability interface, user-storage adapter, import strategy, non-import strategy, federation link, `ImportedUserValidation`, `ImportSynchronization`, user cache, invalidation cache, cache policy, `OnUserCache`, `CachedUserModel`, custom cached metadata, provider priority, provider JAR generation a session/token snapshot.

## Primárne zdroje

- [Keycloak — Server Developer Guide: User Storage SPI](https://www.keycloak.org/docs/latest/server_development/)
- [Keycloak — Server Administration Guide: User storage federation](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak — Admin REST API: Components](https://www.keycloak.org/docs-api/latest/rest-api/index.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: LDAP a Active Directory federation](ldap-active-directory-federation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Authorization Services, resources, scopes, policies a permissions →](authorization-services-resources-scopes-policies-permissions.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
