# Keycloak architecture a responsibility boundary

Keycloak je identity and access management server, ktorý môže vystupovať ako OAuth 2.0 authorization server, OpenID Connect Provider, SAML Identity Provider, identity broker a administračná platforma pre users, credentials, sessions, clients, roles a federation. Táto veta však neznamená, že Keycloak vlastní každé identity alebo authorization rozhodnutie. Human resource system môže zostať autoritou pre employment, LDAP alebo Active Directory pre directory attributes, aplikácia pre business permissions a reverse proxy pre publikovaný network endpoint. Keycloak tieto authorities skladá do authentication a token-issuance lifecycle-u.

Najčastejší architektonický omyl je považovať Keycloak za izolovaný „login service“. Login page je iba jedna viditeľná časť. Reálny výsledok závisí od hostname a proxy trustu, realm configuration, client registration, authentication flowu, user-storage providerov, keys, databázy, session/cache vrstvy, protocol response-u, application validation a local session. Zelený Keycloak health endpoint preto nepreukazuje, že konkrétny user získal správnu identity, správny client, správne claims ani správne business oprávnenie.

## 1. Dominantný request-to-outcome model

Architecture sa má čítať ako reťaz autorít a stavov. Browser request najprv prichádza cez DNS, TLS a reverse proxy. Keycloak z neho a zo svojej explicitnej hostname konfigurácie odvodí public endpoints a issuer. Realm následne vyberie client, authentication flow, identity source, keys a token/session policy. Aplikácia po návrate ešte musí overiť protocol response, vytvoriť vlastnú session a vykonať resource authorization.

```text
business login alebo machine-access intent
→ public hostname, TLS a reverse-proxy boundary
→ Keycloak deployment a loaded server configuration
→ exact realm issuer a realm generation
→ exact client registration a protocol
→ authentication transaction a identity source
→ credential, flow, required-action a policy evaluation
→ Keycloak authentication session
→ user session a client session
→ signed token alebo SAML Response/Assertion
→ client-side cryptographic a semantic validation
→ local application session
→ action/resource/tenant authorization
→ events, revocation a lifecycle closure
```

Každý krok má inú failure semantics. Proxy môže poslať požiadavku na zdravý node, ale nesprávne forwarded headers vytvoria zlý issuer alebo redirect. Keycloak môže správne autentizovať usera, ale client scope môže publikovať priveľa roles. Aplikácia môže validovať signature, ale prijať token pre nesprávne audience. Incident analysis preto nesmie skončiť pri „Keycloak login succeeded“.

## 2. Keycloak responsibility a non-responsibility

Keycloak typicky vlastní protocol endpoints, authentication transaction orchestration, credential verification pre lokálnych users, session bookkeeping, token alebo assertion generation a realm/client administration. Môže tiež synchronizovať alebo cache-ovať external users, no external directory môže zostať authoritative source. Keycloak vie vložiť role alebo claim do tokenu, ale resource server musí rozhodnúť, či je táto informácia dostatočná pre konkrétnu operation.

Responsibility boundary možno zhrnúť takto:

- **Keycloak server** — vykonáva configured identity a protocol mechanizmy, chráni signing keys, udržiava realm a session state a publikuje endpoints;
- **identity authority** — určuje, kto user alebo workload je, či je aktívny a ktoré attributes sú authoritative;
- **client application** — registruje svoj redirect, trust a logout contract, validuje protocol response a vytvára local session;
- **resource server** — validuje access token a vykonáva resource-level authorization;
- **platform/runtime** — poskytuje DNS, TLS, proxy, database, cache, compute, secrets, observability a recovery;
- **business owner** — určuje, ktoré roles alebo claims majú oprávnenie vykonať konkrétnu business operáciu.

Keycloak nesmie byť nútený suplovať chýbajúci business authorization model. Realm role `settlement-admin` môže byť bezpečne vydaná iba vtedy, keď existuje authority, ktorá určuje jej členstvo, a resource server stále overí tenant, object state, workflow a prípadnú JIT podmienku.

## 3. Deployment subject a configuration generations

Názov „production Keycloak“ nie je exact subject. Jeden cluster môže prevádzkovať viac realms a viac protocol clients. Rovnaký realm môže byť obsluhovaný viacerými nodes. Počas rolling upgrade môžu nodes krátko používať odlišnú binary alebo provider generation. Configuration môže pochádzať z build-time options, startup environmentu, database state-u, realm importu, Admin API zmien a custom providers.

Pri troubleshooting-u zachovaj:

```text
Keycloak deployment identity
+ server version a feature profile
+ image digest a provider extensions
+ node/pod identity
+ build-time configuration generation
+ runtime configuration generation
+ public frontend/admin/backchannel URLs
+ proxy-header trust mode
+ realm internal ID, name a issuer
+ client internal UUID, clientId a protocol
+ realm/client key generation
+ authentication-flow revision
+ user-storage/provider revision
+ session IDs a protocol transaction IDs
+ downstream application release a validation policy
```

Bez tohto subjectu sa ľahko porovnajú logy z iného node-u, realm-u alebo clienta. Pri rolling change môže jedna node generation emitovať staré metadata a druhá už nové. Aplikácia potom vidí intermittent issuer, key alebo endpoint failure, hoci „cluster je dostupný“.

## 4. Endpoint groups a exposure boundary

Keycloak má viac endpoint groups s odlišným účelom. Frontend endpoints obsluhujú browser redirects, login pages, account actions a discovery URLs. Backchannel endpoints používajú clients a resource servers pre token, introspection, UserInfo, JWKS, logout alebo direct server-to-server komunikáciu. Administration endpoints menia realm configuration. Management interface nesie health a metrics a nemá byť automaticky publikovaný rovnakým internetovým ingressom.

```text
frontend
→ browser-visible issuer, login, action a redirect endpoints

backchannel
→ token, introspection, UserInfo, JWKS a server-to-server operations

administration
→ Admin Console a Admin REST API mutation boundary

management
→ health, readiness a metrics pre platform operations
```

Oddelenie nie je iba network hardening. Frontend hostname sa objavuje v issuer-i, discovery metadata, email action links a redirectoch. Administration hostname môže byť interný alebo prísnejšie chránený. Management port obsahuje operational signals, ktoré nemajú byť verejným API. Reverse proxy musí publikovať iba zamýšľané paths a prepisovať forwarded headers namiesto ich slepého preposlania od klienta.

## 5. Hostname, issuer a reverse-proxy trust

Keycloak odporúča explicitný hostname preto, že server sám publikuje URLs. Ak by prijal arbitrary Host alebo forwarded header ako autoritu, útočník môže ovplyvniť discovery document, reset link, action token URL alebo redirect. Hostname teda nie je kozmetická base URL; je súčasťou identity-provider trust contractu.

Pri proxy termination treba rozlišovať public connection a backend connection. Browser môže používať HTTPS, zatiaľ čo proxy komunikuje s Keycloakom cez re-encrypted TLS alebo interné HTTP. Keycloak musí vedieť public scheme, host, port a path, ale forwarded údaje smie prijímať iba od trusted proxy, ktorá pôvodné client headers odstráni alebo prepíše.

Failure chain vyzerá napríklad takto:

```text
untrusted X-Forwarded-Host prejde cez edge
→ Keycloak dynamicky odvodí public URL
→ discovery alebo action link obsahuje attacker host
→ client alebo user nasleduje nesprávny endpoint
→ credential alebo authorization response unikne
```

Fix nie je vypnúť issuer alebo redirect validation v clientovi. Správne riešenie je obnoviť jednu authoritative public URL, správny proxy-header trust a exact client contract.

## 6. Realm runtime a administration plane

Realm je logical identity a protocol namespace. Má vlastných users, credentials, roles, groups, clients, keys, sessions a policy configuration. Realms sú od seba logicky izolované v Keycloak modeli, ale zdieľajú server process, database engine, cache infrastructure, nodes a často administračný trust. Realm preto nie je automaticky fyzický ani regulatory isolation boundary.

Administration mutation má väčší dosah než bežný login request. Zmena client redirectu, mappera, keyu alebo authentication flowu ovplyvní budúce sessions a tokens. Admin Console je iba UI nad administračnými APIs a server-side permission modelom. „User nevidí tlačidlo“ nie je authorization proof; rozhoduje effective admin permission na API boundary.

Operational design má oddeliť:

- **server administration** — build, startup, database, cache, hostname, TLS, providers a upgrades;
- **realm administration** — users, clients, roles, flows, keys, identity providers a policies;
- **delegated administration** — obmedzené operations nad vybranými realm resources;
- **application administration** — business accounts, permissions a workflow mimo Keycloaku.

Broad `realm-admin` alebo `manage-realm` pridelený kvôli jednej úlohe vytvára privilege escalation path cez client, mapper alebo flow mutation.

## 7. Database, cache a session state

Keycloak používa relational database pre persistent realm a identity configuration. Infinispan poskytuje cache a clustered state mechanizmy. Presné uloženie online sessions sa menilo medzi verziami a feature profilmi, preto architekt nesmie predpokladať session survival iba podľa starej skúsenosti. Musí overiť konkrétnu verziu, enabled features, cache topology, database migration a upgrade path.

Cache nie je nezávislá druhá autorita. Slúži na výkon, distribúciu a dočasný state. Stale cache, partition alebo failed invalidation však môže dočasne ovplyvniť effective behavior. Pri session incidente treba rozlišovať:

```text
authentication session
→ rozpracovaný login transaction

user session
→ realm-level authenticated user state

client session
→ väzba user session na konkrétny client

offline session
→ dlhodobejší refresh/offline access state

token
→ podpísaný credential so snapshotom claims a expiry

application session
→ state vlastnený downstream aplikáciou
```

Vymazanie jedného state-u automaticky neodstráni všetky descendants. Napríklad ukončenie Keycloak browser session nemusí okamžite zneplatniť self-contained access token ani local application cookie.

## 8. Keys a cryptographic boundary

Realm keys podpisujú OIDC tokens alebo SAML messages a môžu sa používať na encryption. Key identity zahŕňa purpose, algorithm, priority, active/passive state, `kid` alebo certificate, storage a rollover generation. Private key je high-impact secret: jeho kompromitácia môže umožniť vytvárať protocol-valid artifacts.

Keycloak podpisom dokazuje, že artifact vydala príslušná key authority. Neoveruje tým automaticky business správnosť claims. Client musí vybrať trusted realm/issuer alebo SAML entity a až potom key patriaci danej generation. Shared key naprieč staging a production alebo naprieč nesúvisiacimi trust domains zväčšuje blast radius.

Rollover je distribuovaná zmena:

```text
nový signing key publikovaný
→ verifiers načítajú nový public key
→ Keycloak začne podpisovať novým active keyom
→ staré tokeny/assertions zostanú overiteľné počas overlapu
→ starý key sa odstráni až po expiry a verifier convergence
```

Príliš skoré odstránenie rozbije validné sessions; príliš dlhé ponechanie kompromitovaného keyu predlžuje attack window.

## 9. Authentication execution a provider boundary

Authentication flow skladá executions, authenticators, conditional logic a required actions. Local password, WebAuthn, OTP, identity brokering a custom authenticator majú rozdielne trust a recovery properties. User-storage provider môže overovať credentials proti external directory alebo importovať attributes. Protocol flow preto závisí od provider availability, attribute freshness a transaction state.

Custom SPI alebo provider beží v Keycloak process-e a môže získať prístup k realm, user a credential internals. Extension nie je bezpečná iba preto, že je zabalená ako JAR. Potrebuje source, build, compatibility, permission, secret a upgrade lifecycle. Chybný provider môže spomaliť všetky login requests, meniť claims alebo spôsobiť partial failure počas rolling upgrade-u.

## 10. High availability nie je iba viac replík

Dve Keycloak repliky chránia iba proti strate jedného processu, ak fungujú ich spoločné dependencies a routing. Production availability závisí od database, cache/discovery, DNS, TLS, proxy, keys, external LDAP/IdP, email provider a downstream clients. Sticky sessions môžu znížiť remote cache lookups, ale nie sú náhradou za správnu clustered session consistency.

Readiness má odpovedať, či node dokončil bootstrap a môže bezpečne obsluhovať requests. Neoveruje, že konkrétny realm client funguje end-to-end. Potrebné sú capability canaries:

```text
discovery a JWKS
→ test authentication flow
→ code alebo SAML response
→ client validation
→ local session
→ protected resource
→ logout/revocation
```

Canary musí používať bezpečný test subject a nesmie vytvárať broad production privilege.

## 11. Connected incident `KC-PAY-65`

Atlas prevádzkoval Keycloak `26.7.0` za shared reverse proxy. Realm `atlas-payments-prod` obsahoval OIDC client `payments-admin-web` a SAML client `settlement-partner-sp`. Platform dashboard sledoval iba node readiness, database connectivity a počet login errors. Neoveroval exact realm/client role projection ani downstream revocation.

Configuration chain bol:

```text
group /payments
→ realm role settlement-admin
→ subgroup /payments/partners/vega
→ inherited realm role
→ Full Scope Allowed na oboch clients
→ OIDC realm_access alebo SAML role mapper
→ downstream admin session
```

OIDC client povoľoval `https://*.atlas.example/*` a nevyžadoval PKCE. Kompromitovaný `preview.atlas.example` prijal authorization code a vymenil ho za tokens. SAML client podporoval IdP-initiated login na shared ACS a publikoval rovnakú inherited realm role. Keycloak správne overil credentials a podpísal artifacts. Chyba bola v identity/role/client responsibility boundary.

Po zistení incidentu administrátor použil realm-wide sign-out. Browser SSO sessions zmizli, ale päťminútové access tokens a local application sessions prežili. Settlement API dostalo ďalších 186 privileged requests; 28 z nich zmenilo approval state pre 4 912 settlement položiek.

Root cause nebol „Keycloak nevie logout“. Root cause bol chýbajúci end-to-end contract:

```text
organizational membership
≠ application permission

Keycloak sign-out
≠ okamžitá revokácia self-contained tokenu
≠ local application session invalidation
```

## 12. Architecture redesign

Recovery najprv oddelí authority:

```text
HR/partner registry
→ active identity a organization membership

Keycloak group
→ organizačné zoskupenie bez broad app privilege

client role
→ payments-admin specific entitlement

client scope a role scope mapping
→ minimálny token/assertion projection

resource server
→ tenant, action, object a workflow authorization
```

Server-side redesign používa explicitný public hostname, trusted proxy headers, oddelený admin exposure, inventory realms/clients/providers/keys, scoped admin permissions, versioned realm configuration, key rollover procedure a canaries pre OIDC aj SAML. Session response playbook ruší Keycloak sessions, refresh/offline descendants, nastavuje relevantnú revocation/not-before policy, zruší downstream application sessions a overí, že starý token aj cookie sú odmietnuté.

## 13. Architecture acceptance verdict

Architecture je prijatá iba vtedy, keď evidence spája exact deployment a realm configuration s protocol a business outcome-om. Kontrola musí preukázať správny aj zakázaný path.

```text
server generation je reprodukovateľná
+ public/admin/management exposure je explicitné
+ realm/client/flow/key generations sú inventarizované
+ database/cache/session failure semantics sú známe
+ delegated admin má bounded effective permission
+ OIDC a SAML canary prejde
+ wrong realm/client/redirect/issuer path zlyhá
+ logout/revocation odstráni všetky intended descendants
+ second node a second change zachovajú outcome
```

Node readiness bez týchto dôkazov je iba platform signal, nie identity-platform acceptance.

## 14. Troubleshooting flow

Pri symptóme „login nefunguje“ alebo „user má nesprávnu role“ nezačni náhodnou zmenou mappera. Najprv identifikuj observation boundary.

```text
user/business symptom
→ exact public URL, realm, client a transaction
→ node/version/configuration generation
→ proxy a hostname decision
→ realm/client/flow selection
→ identity source a credential result
→ Keycloak auth/user/client session
→ token/assertion fields a signature key
→ client validation a local session
→ resource authorization
→ revocation descendants
```

Competing hypotheses môžu byť wrong public URL, wrong realm, disabled client, stale user provider, failed authenticator, missing role, over-broad inherited role, stale key cache, invalid audience, local session bug alebo resource-policy failure. Každá hypotéza potrebuje diskriminačný observation point, nie iba ďalší restart.

Containment musí zachovať realm/client export, event IDs, session IDs, token/assertion hashes a proxy logs bez ukladania raw credentials. Recovery sa overí pôvodným business journey aj forbidden journey, napríklad partner login musí fungovať, ale nesmie vytvoriť `settlement-admin` session.

## 15. Anti-patterny

### Keycloak ako jediná authorization autorita

Keycloak role môže byť input, nie úplný business decision. Ak API povolí settlement podľa jedného claimu bez tenant a object state-u, token snapshot sa stane priveľkou autoritou.

### Realm ako hard tenant boundary

Realms izolujú identity configuration, ale zdieľajú server, database engine, nodes, administrators a extensions. Regulatory alebo adversarial isolation môže vyžadovať samostatný deployment, account alebo ďalšie boundaries.

### Health endpoint ako login acceptance

Readiness dokazuje schopnosť node-u prijímať requests. Neoveruje redirect, flow, external identity source, token validation ani protected business operation.

### UI-only administration

Skryté tlačidlo alebo oddelená Admin Console URL nenahrádza server-side Admin API authorization. Effective delegated permission treba testovať positive aj negative requestmi.

### Restart ako session recovery

Restart môže vyčistiť časť cache state-u, ale nemusí zrušiť database sessions, offline sessions, access tokens ani downstream cookies. Revocation musí sledovať descendant graph.

## 16. Kontrolné otázky

1. Ktoré identity a authorization decisions vlastní Keycloak a ktoré zostávajú mimo neho?
2. Prečo hostname ovplyvňuje issuer, discovery a action links?
3. Aký je rozdiel medzi frontend, backchannel, administration a management endpointmi?
4. Čo tvorí exact Keycloak deployment a request subject?
5. Prečo realm nie je automaticky fyzický tenant boundary?
6. Akú úlohu majú database a Infinispan?
7. Prečo user session, client session, token a application session nemajú rovnaký lifecycle?
8. Ako custom provider mení trust a upgrade boundary?
9. Prečo dve repliky nepreukazujú end-to-end identity availability?
10. Čo bolo root cause incidentu `KC-PAY-65`?
11. Aké descendants treba zrušiť pri credential alebo entitlement compromise?
12. Čo musí obsahovať architecture acceptance verdict?

## Glossary impact

Relevantné pojmy: Keycloak deployment subject, realm issuer, frontend endpoint, backchannel endpoint, administration endpoint, management interface, hostname authority, proxy-header trust, authentication session, user session, client session, offline session, session descendant graph, realm key generation, provider extension boundary, identity-platform acceptance verdict.

## Primárne zdroje

- [Keycloak Documentation 26.7.0](https://www.keycloak.org/documentation)
- [Keycloak — Configuring for production](https://www.keycloak.org/server/configuration-production)
- [Keycloak — Configuring the hostname](https://www.keycloak.org/server/hostname)
- [Keycloak — Configuring a reverse proxy](https://www.keycloak.org/server/reverseproxy)
- [Keycloak — Configuring distributed caches](https://www.keycloak.org/server/caching)
- [Keycloak — Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak — Upgrading Guide](https://www.keycloak.org/docs/latest/upgrading/)
