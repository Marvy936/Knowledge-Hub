# Identity brokering

Keycloak identity broker oddeľuje dve rôzne trust relationships. Voči externému OpenID Connect, SAML alebo social providerovi vystupuje ako client alebo service provider a validuje jeho authentication response. Voči lokálnej aplikácii vystupuje ako vlastný authorization server alebo IdP a vydáva nový Keycloak token alebo assertion. Aplikácia preto nedostáva upstream token ako automatickú autoritu. Dostáva Keycloak artifact odvodený z external identity, first-login alebo account-linking flowu, lokálneho user recordu, mapperov, session policy a client authorization contractu.

Najnebezpečnejší broker incident nemusí obsahovať neplatný podpis. External IdP môže korektne potvrdiť email, ktorý bol recyklovaný inému človeku; Keycloak môže `Trust Email` a unsafe AutoLink použiť na spojenie s existujúcim privilegovaným accountom; mapper môže pri `FORCE` prepísať lokálny tenant alebo group attribute; post-login flow nemusí vykonať intended step-up. Výsledkom je kryptograficky platná, ale nesprávne prepojená lokálna identita.

## 1. Dominantný upstream-response-to-local-session lifecycle

```text
local client a protected journey
→ Keycloak broker selection alebo redirector
→ exact external IdP configuration generation
→ upstream OIDC/SAML authorization request
→ external authentication a upstream session
→ signed response/token/assertion validation
→ brokered identity context a mapper preprocessing
→ federated-identity lookup
→ first-login create/link/verify flow alebo existing-link path
→ local Keycloak user a user session
→ post-login flow, required actions a step-up
→ local client session
→ Keycloak token alebo SAML assertion
→ downstream application session a resource authorization
→ unlink, upstream/local logout a descendant-revocation closure
```

Každá vrstva má vlastný subject. Upstream `sub` alebo SAML NameID identifikuje external account v namespace konkrétneho IdP. Lokálny Keycloak `userId` identifikuje realm account. Federated-identity link spája tieto dva subjects. Email alebo username môže pomôcť pri discovery, ale nesmie nahradiť verifikované account linking.

## 2. Exact broker subject

```yaml
brokerSubject:
  keycloak:
    publicBaseUrl: https://sso.atlas.example
    deploymentGeneration: kc-2026-08-02-09
    realm: atlas-prod
    realmIssuer: https://sso.atlas.example/realms/atlas-prod
  localClient:
    clientId: settlement-admin-web
    internalId: 2b2b...
    redirectUri: https://settlement-admin.atlas.example/oauth/callback
  identityProvider:
    alias: workforce-oidc
    internalId: 88af...
    configurationRevision: idp-42
    providerType: oidc
    upstreamIssuer: https://login.corp.example
    upstreamClientId: keycloak-atlas-prod
    signingKeyGeneration: upstream-jwks-19
    enabled: true
    hideOnLoginPage: false
    accountLinkingOnly: false
    trustEmail: false
    storeTokens: false
    syncMode: import
    firstLoginFlow: atlas-first-broker-login-v4
    postLoginFlow: atlas-broker-stepup-v2
  upstreamIdentity:
    subject: 00u82...
    username: dana@corp.example
    email: dana@corp.example
    emailVerified: true
    authenticationContext: phishing-resistant
  localIdentity:
    userId: 4b8e...
    federatedIdentityProvider: workforce-oidc
    federatedUserId: 00u82...
    linkRevision: broker-link-77
  sessions:
    authenticationSessionId: 64c1...
    keycloakUserSessionId: 04d9...
    localClientSessionId: 9f31...
```

Rovnaký alias po delete/recreate nemusí znamenať rovnakú configuration generation. Rovnaký upstream email pri inom `issuer` alebo SAML entity ID je odlišná identity. Rovnaký external subject po migration providerov môže mať inú authority. Incident evidence preto uchováva alias aj internal ID, upstream issuer/entity ID, exact external subject, local user ID a link revision.

## 3. Broker selection, `kc_idp_hint` a default provider

Keycloak môže zobraziť provider buttons, použiť Identity Provider Redirector v Browser flowe, nastaviť default provider alebo prijať client parameter `kc_idp_hint`. Provider s `Hide on Login Page` sa nezobrazuje, ale client ho stále môže explicitne requestnuť. `Account Linking Only` provider neslúži na login; je dostupný iba na pridanie linku k už autentizovanému accountu.

```text
no provider hint
→ Browser flow a login page/redirector policy

kc_idp_hint=workforce-oidc
→ exact provider alias resolution
→ direct broker redirect, ak provider a policy dovolia

provider Account Linking Only
→ unauthenticated login path rejected
→ existing authenticated user môže linknúť provider
```

Client nesmie voľne používať ľubovoľný provider pre privileged journey, ak provider cohorts majú rozdielnu assurance. Platform môže obmedziť provider podľa clienta, organization domainu alebo flow condition. `Hide on Login Page` nie je access control.

## 4. Upstream OIDC a SAML validation

Pri OIDC brokerovi Keycloak validuje issuer, authorization response, state, code exchange, ID token signature, key, audience/client, nonce, time a configured essential claims. Pri SAML brokerovi validuje issuer/entity ID, destination/ACS, signatures, audience, time conditions, InResponseTo a binding podľa configuration.

```text
external protocol response
→ transaction state/RelayState correlation
→ issuer/entity authority
→ signature a key generation
→ audience/client/destination
→ time a replay boundaries
→ upstream subject/profile extraction
→ BrokeredIdentityContext
```

Valid upstream artifact nepreukazuje, že lokálny account link je správny. Naopak správny existing link neospravedlňuje vypnutú signature validation. Protocol validation a identity correlation sú dve samostatné gates.

## 5. Brokered identity context a mappers

Identity provider mappers transformujú upstream claims alebo SAML attributes na brokered username, email, user attributes, roles alebo groups. Mappers môžu bežať pred First Broker Login flowom a ovplyvniť hodnoty zobrazené v Review Profile aj uniqueness/account-linking rozhodnutie.

Mapper contract obsahuje upstream claim path, JSON/SAML type, normalization, target Keycloak field alebo role/group, sync mode, source authority, absence semantics a conflict behavior. Dot notation a array indexes pri JSON claims musia byť testované na actual profile shape.

```text
upstream claim department=settlements
→ IdP mapper generation M-31
→ local attribute department=settlements
→ optional group/role mapper
→ downstream client-scope mapper
→ local token claim
```

Broker mapper nemá priamo vytvárať broad realm admin role z mutable upstream attribute bez exact allowlistu a ownera. Organization membership, tenant a authorization roles potrebujú stable upstream authority a deprovisioning behavior.

## 6. Sync modes: IMPORT, FORCE, LEGACY a INHERIT

IdP-level `Sync Mode` a per-mapper `Sync Mode Override` určujú, kedy sa upstream data premietnu do local user state.

**IMPORT** aplikuje mapper pri prvom vytvorení/linknutí usera a neskoršie upstream zmeny automaticky neprepisuje.

**FORCE** sa pokúša aktualizovať user data pri každom broker login-e. To môže opraviť stale attributes, ale upstream change má okamžitý blast radius na local profile, email verification, groups alebo roles.

**INHERIT** použije provider-level mode. **LEGACY** zachováva historické mapper behavior a nemá byť používaný bez presnej compatibility potreby.

```text
first login s IMPORT
→ local snapshot L1
→ upstream attribute sa neskôr zmení
→ local value zostáva L1

repeated login s FORCE
→ upstream value U2
→ mapper prepisuje local value na U2
```

Sync mode nie je directory synchronization. Aktualizácia nastane pri broker login-e. User, ktorý sa dlho neprihlásil, môže mať stale local data; deprovisioning sa nesmie spoliehať iba na ďalší login.

## 7. First Broker Login flow

Prvý login z konkrétneho provider+external-subject linku spúšťa `First Login Flow`. Default flow môže obsahovať Review Profile, Create User If Unique, Confirm Link Existing Account a overenie existujúceho accountu emailom alebo re-authentication.

```text
valid external identity bez existing federated linku
→ Review Profile podľa policy/missing fields
→ uniqueness lookup podľa username/email
→ create new local user
OR
→ candidate existing local account
→ explicit link confirmation
→ existing-account verification
→ federated link write
```

First-login flow je security-critical authentication graph. Copy, versionuj a priraď providerovi successor flow; neupravuj implicitne všetkých providerov bez cohort testu.

## 8. `Create User If Unique` a automatic user creation

`Create User If Unique` vytvorí local account, ak username/email nekolidujú. User creation cez broker je nezávislá od realm self-registration switchu. Realm môže mať self-registration vypnutú a broker stále vytvárať users.

Pri read-only LDAP-backed population môže byť automatic local creation nežiaduca. Vtedy sa Create User If Unique a Confirm Link Existing Account vypnú a flow vyžaduje explicitné rozpoznanie existujúceho federated usera. `Detect Existing Broker User` možno použiť, keď majú login povolený iba preprovisioned users.

Creation acceptance musí overiť exact local user/storage-provider subject, mandatory profile, group/role mapping a first-login required actions. „Login prešiel“ nepreukazuje, že user vznikol v intended storage alebo tenantovi.

## 9. Account linking a existing-account verification

Federated link je durable relation:

```text
realm local user ID
+ IdP alias/internal ID
+ external subject/user ID
→ federated identity link
```

Email alebo username match môže identifikovať candidate account, ale link sa má potvrdiť proofom, že current actor ovláda existing account. Default flow môže poslať verification email alebo vyžadovať re-authentication heslom, OTP alebo už linked IdP.

Pri passwordless alebo LDAP userovi musí flow ponúknuť supported existing-account proof. Verification email je silná iba ako mailbox authority. Re-authentication cez ďalší linked IdP musí validovať, že ide o už linked identity toho istého local usera.

## 10. AutoLink a recycled identifier risk

`Automatically Set Existing User`/AutoLink nastaví matching existing local user bez nezávislého verification proofu. Keycloak dokumentácia ho označuje ako nebezpečný v prostredí, kde users môžu ovládať usernames alebo emails. Je prijateľný iba pri kurátorovanej identity population a authoritative, globally unique, non-recycled mappingu.

```text
external email dana@atlas.example
→ local account lookup podľa emailu
→ AutoLink bez existing-account proofu
→ external identity linked k local userovi
```

Ak email po odchode zamestnanca dostane nový človek alebo external IdP dovolí self-asserted email, link prevezme starý local account. Bezpečný design používa stable workforce identifier alebo preprovisioned mapping a overuje issuer+subject, nie iba email.

## 11. `Trust Email` a `email_verified`

`Trust Email` môže označiť brokered email ako verified bez Keycloak verification emailu. Pri OIDC providerovi môže Keycloak zohľadniť upstream `email_verified`; pri `FORCE` sync môže verification state aktualizovať pri ďalších loginoch.

Tento switch je delegácia email-ownership authority externému IdP. Pred zapnutím over:

```text
upstream email source
+ email_verified semantics
+ domain ownership a reassignment policy
+ issuer/client validation
+ sync mode
+ local duplicate-email policy
+ recovery a account-linking usage emailu
```

Verified email nie je stable person ID. Nemá automaticky oprávniť account linking, tenant membership ani privileged recovery.

## 12. Stored upstream tokens

`Store Tokens` uloží access/refresh token alebo response z external IdP po broker login-e. Aplikácia môže upstream token získať cez broker endpoint, ak user/client má príslušnú permission; `Stored Tokens Readable` pridáva/read-token capability podľa configuration.

Stored token mení Keycloak z autentizačného brokeru aj na custody system pre upstream credentials. Risk zahŕňa database compromise, overly broad client role, token replay voči upstream API, refresh descendants a logout mismatch.

```text
external IdP token U-17
→ encrypted/DB stored broker token record
→ local user a provider link
→ authorized client retrieves token
→ upstream API call
```

Zapni ho iba pri konkrétnom upstream API use case. Samotné login brokering ho nepotrebuje. Recovery musí revoke-nuť stored token aj upstream authorization, nie iba local Keycloak session.

## 13. Post Login Flow a brokered step-up

`Post Login Flow` sa vykoná po successful external authentication a existing/created link resolution. Môže vynútiť lokálne OTP, WebAuthn, terms alebo ďalšie checks. Je vhodný na zvýšenie assurance, keď upstream IdP neposkytuje dostatočný alebo dôveryhodne mapovaný authentication context.

```text
upstream authentication context silver
→ external response valid
→ post-login flow pre privileged provider/client cohort
→ Keycloak WebAuthn step-up
→ achieved local LoA gold
→ local token acr=gold
```

Post-login flow musí byť explicitne naviazaný na provider. Client/resource server validuje resulting local `acr/auth_time`, nie iba fakt, že `identity_provider=workforce-oidc`.

## 14. Session notes a downstream evidence

Po broker login-e Keycloak uchováva user-session notes:

- `identity_provider` — alias použitý pri login-e;
- `identity_provider_identity` — upstream username/identity display value.

Client protocol mapper môže tieto notes publikovať do tokenu. Sú užitočné pre audit a policy, ale nemajú nahradiť stable upstream subject. Display username alebo email sa môže meniť.

Downstream evidence spája Keycloak user/session ID, provider alias/internal ID, upstream issuer+subject, achieved authentication context, local client session, local token `sid/jti` a business request ID.

## 15. Logout, unlink a revocation

Lokálny Keycloak logout nemusí zrušiť upstream IdP session. Ďalší broker login môže byť silent, ak upstream cookie zostáva. Upstream logout nemusí zrušiť local application session alebo už vydané Keycloak access tokens.

Unlink federated identity odstráni budúci link, ale nezaručí okamžité ukončenie existing user/client/application sessions. Delete/recreate link môže zmeniť external subject relation.

```text
unlink provider
→ federated link removed
→ existing Keycloak user zostáva
→ active sessions/token descendants inventory
→ explicit revocation podľa incident contractu
→ second broker login must not auto-relink unsafely
```

## 16. Connected incident `KC-PAY-67` — recycled email a unsafe AutoLink

Atlas pripojil partner OIDC provider `vega-oidc`. `Trust Email` bolo zapnuté, First Broker Login flow používal Create User If Unique a Automatically Set Existing User bez re-authentication. Mapper pri `FORCE` synchronizoval `email`, `partner_tenant` a hardcoded group `/settlement-partners`.

Po odchode partnera bola external mailbox adresa `ops@vega.example` recyklovaná. Nový pracovník dostal nový upstream `sub`, ale rovnaký verified email. Pri prvom login-e Keycloak našiel existujúci local account podľa emailu a AutoLink ho pripojil bez independent proofu. Post Login Flow neobsahoval MFA. Local account mal historickú client role `settlement-api.export`.

```text
new external subject
+ recycled verified email
→ Trust Email
→ existing local account match
→ AutoLink bez proofu
→ FORCE mapper a partner group
→ local privileged session
→ valid Keycloak token
→ export operation
```

## 17. Evidence-preserving containment a recovery

Zachovaj external response/token hash, issuer/entity ID, external subject, provider alias/internal ID/config export hash, mapper IDs/sync modes, first/post-login flow IDs a executions, local user ID, federated-link record, user/session notes, local session/token IDs a downstream requests. Full upstream tokens a action links sa nemajú zapisovať do incident notes.

Containment disable-ne provider alebo affected client path, blokne high-risk operations, revoke-ne local sessions a podľa potreby upstream grants. Recovery odstráni unsafe link, obnoví local account ownera, nahradí AutoLink verified first-login flowom, vypne `Trust Email` alebo presne zdokumentuje authority, nahradí email stable identifierom a pridá post-login step-up.

## 18. Positive, recovery a forbidden acceptance

Broker acceptance musí preukázať správny external issuer+subject, bezpečný local link a intended downstream session ako jeden chain. Recovery navyše uzatvára wrong link, stored upstream token a local descendants, zatiaľ čo forbidden paths dokazujú, že email collision, wrong issuer, low assurance alebo explicitný provider hint nevytvoria privilegovanú local identity.

Positive path:

```text
known external issuer+subject
→ valid response
→ verified existing link alebo secure first-login proof
→ intended local user
→ required post-login assurance
→ local token s correct tenant/roles
→ intended operation succeeds
```

Recovery path:

```text
wrong link detected
→ provider/link/session evidence preserved
→ sessions a stored upstream tokens contained
→ wrong link removed
→ owner identity re-verified
→ successor link created
→ old external subject fails
→ owner second login succeeds
```

Forbidden paths:

```text
same email, different external subject
→ no automatic privileged link

unverified alebo self-asserted email s Trust Email disabled
→ email remains unverified a cannot satisfy recovery/link proof

provider hidden on login page + explicit unauthorized kc_idp_hint
→ policy rejects or flow prevents privileged use

stored-token retrieval bez read-token permission
→ reject

low-assurance broker login pre gold client
→ post-login step-up required

unlinked external identity reappears
→ no silent AutoLink
```

## 19. Troubleshooting

Pri broker login failure oddeľ provider selection, outbound request/state, callback URL, external issuer/key/audience/time, proxy/hostname, BrokeredIdentityContext, mapper errors, first-login flow, uniqueness/account-linking, required actions, post-login flow a local client callback.

Pri wrong-user alebo wrong-claims incidente začni external issuer+subject a federated linkom, nie local emailom. Porovnaj IdP sync mode, mapper overrides, local predecessor values, external profile a actual local token. Pri repeated redirect loop-e skontroluj provider default/redirector, external session, prompt/max-age a required interactive screens.

## 20. Kontrolné otázky

- Ktorý external issuer/entity ID, provider alias a configuration generation spracovali login?
- Ktorý stable external subject je linknutý na ktorý local user ID?
- Kto je authority pre email, username, tenant, groups a roles?
- Je First Broker Login flow bezpečný pri duplicate alebo recycled emailoch?
- Je AutoLink naozaj podopretý curated non-recycled identifierom?
- Kedy mappers používajú IMPORT alebo FORCE a čo sa stane pri absent claim-e?
- Ukladá Keycloak upstream tokens a kto ich môže čítať?
- Vynucuje Post Login Flow intended MFA/LoA?
- Čo sa revoke-ne pri unlinku alebo provider compromise?
- Prešli different-subject-same-email, wrong issuer, stale link, low-assurance, stored-token a second-login paths?

## Glossary impact

Relevantné pojmy: Keycloak identity broker, external IdP alias, BrokeredIdentityContext, First Broker Login, Post Login Flow, federated identity link, Create User If Unique, Confirm Link Existing Account, AutoLink, Detect Existing Broker User, Trust Email, broker sync mode, identity-provider mapper, stored upstream token, `kc_idp_hint`, Account Linking Only, `identity_provider` session note a broker descendant revocation.

## Primárne zdroje

- [Keycloak — Server Administration Guide: Identity brokering](https://www.keycloak.org/docs/latest/server_admin/)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [SAML V2.0 Technical Overview](https://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Password policies, brute-force protection a account recovery](password-policies-brute-force-protection-account-recovery.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: LDAP a Active Directory federation →](ldap-active-directory-federation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
