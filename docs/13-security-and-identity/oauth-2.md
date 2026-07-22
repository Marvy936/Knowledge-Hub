# OAuth 2.0

OAuth 2.0 je authorization framework, ktorý umožňuje client aplikácii získať obmedzený prístup k protected resource v mene resource ownera alebo vo vlastnom machine identity kontexte. OAuth neurčuje univerzálny login protocol ani formát používateľskej identity. Jeho hlavným výstupom je access token určený pre resource server.

## 1. Mentálny model

```text
resource owner alebo workload
→ client požiada authorization server o oprávnenie
→ authorization server vydá obmedzený token
→ client predloží access token resource serveru
→ resource server overí token, audience, scope a policy
→ vykoná alebo odmietne operáciu
```

OAuth oddeľuje:

- používateľské credentials od client aplikácie,
- authorization decision od API enforcementu,
- krátkodobý access token od dlhodobejšieho credential lifecycle-u,
- client identity od resource-owner identity.

## 2. Role

### Resource owner

Entita, ktorá môže autorizovať prístup k protected resource.

Často ide o používateľa, ale pri machine-to-machine flowe nemusí byť prítomný človek.

### Client

Aplikácia, ktorá požaduje access token a používa ho voči resource serveru.

Client môže byť:

- confidential — vie bezpečne chrániť vlastné credentials,
- public — nedokáže spoľahlivo udržať client secret, napríklad browser alebo native aplikácia.

### Authorization server

Autentizuje relevantného principal-a, získava alebo vyhodnocuje authorization grant a vydáva tokens.

### Resource server

API alebo služba, ktorá prijíma access token, validuje ho a presadzuje resource-level authorization.

Resource server nesmie považovať samotnú existenciu tokenu za dostatočný dôkaz prístupu.

## 3. Authorization endpoint a token endpoint

### Authorization endpoint

Používa user agent redirect flow.

Typicky rieši:

- authentication používateľa,
- consent alebo policy decision,
- redirect späť ku clientovi,
- vydanie authorization code-u.

### Token endpoint

Server-to-server endpoint, ktorý vymieňa grant alebo refresh token za access token.

Token endpoint typicky vyžaduje:

- client authentication, ak je client confidential,
- validáciu grant type-u,
- redirect URI binding,
- PKCE verifier,
- scope a policy evaluation.

## 4. Authorization grant

Authorization grant je credential reprezentujúci authorization udelenú clientovi.

Nie je totožný s access tokenom.

Príklady:

- authorization code,
- refresh token,
- device code,
- client credentials context,
- token-exchange subject token podľa extension protocolu.

Grant musí byť:

- viazaný na správneho clienta,
- krátkodobý alebo revoke-nuteľný,
- chránený pred replay,
- obmedzený scope-om a audience,
- auditovateľný.

## 5. Authorization Code flow

Odporúčaný browser-based model:

```text
client
→ redirect na authorization endpoint
→ používateľ sa autentizuje a autorizuje
→ authorization server vráti authorization code
→ client vymení code na token endpoint-e
→ dostane access token a voliteľne refresh token
```

Authorization code:

- má byť krátkodobý,
- jednorazový,
- viazaný na clienta,
- viazaný na redirect URI,
- chránený PKCE.

Access token sa nemá vracať priamo cez browser URL, ak sa tomu dá vyhnúť.

## 6. PKCE

Proof Key for Code Exchange chráni authorization code pred odcudzením a injection útokmi.

Flow:

```text
client vytvorí náhodný code_verifier
→ odvodí code_challenge
→ pošle challenge v authorization requeste
→ authorization server uloží binding
→ client pri token exchange pošle verifier
→ server overí, že verifier zodpovedá challenge
```

Používaj:

- transaction-specific náhodný verifier,
- `S256` challenge method,
- PKCE pre public clients povinne,
- PKCE aj pre confidential clients ako defense in depth.

PKCE nenahrádza:

- exact redirect URI validation,
- `state`/transaction binding,
- client authentication confidential clienta,
- ID Token `nonce` pri OpenID Connect.

## 7. Redirect URI

Redirect URI je kritická security boundary.

Požiadavky:

- pre-registration,
- exact string matching okrem štandardom definovaných native-loopback výnimiek,
- HTTPS pre web clients,
- žiadny open redirector,
- oddelenie development a production URI,
- žiadne wildcardy bez veľmi presného threat modelu.

Chybná redirect URI validácia umožňuje ukradnúť authorization code alebo token.

## 8. State a transaction binding

`state` pomáha viazať authorization response na pôvodnú client transaction a chrániť pred CSRF a response confusion.

Musí byť:

- náhodný,
- nepredvídateľný,
- session-bound,
- jednorazový,
- validovaný pred použitím response.

Do `state` nevkladaj citlivé údaje v plaintext-e.

Pri OpenID Connect sa navyše používa `nonce` na binding ID Token-u k authentication requestu.

## 9. Access token

Access token reprezentuje oprávnenie volať resource server.

Môže byť:

- opaque reference token,
- structured token, často JWT,
- sender-constrained token.

Resource server musí overiť minimálne:

- issuer alebo dôveryhodný introspection endpoint,
- audience/resource binding,
- expiration a časové claims,
- signature alebo introspection status,
- scope/permissions,
- token type,
- sender binding, ak sa používa,
- application authorization policy.

Access token nie je určený client aplikácii ako používateľský profil.

## 10. Bearer token

Bearer token môže použiť každý, kto ho získa.

Preto vyžaduje:

- TLS end to end,
- krátku lifetime,
- bezpečné storage,
- žiadne logovanie,
- žiadne URL query parameters,
- audience restriction,
- scope restriction,
- incidentný revocation model.

Bearer token leakage je ekvivalent credential compromise počas jeho platnosti.

## 11. Sender-constrained token

Sender-constrained token vyžaduje, aby client preukázal vlastníctvo konkrétneho key materialu.

Príklady:

- mutual TLS-bound access token,
- DPoP.

Výhoda:

- ukradnutý token nestačí bez príslušného private key alebo proofu.

Zostávajúce riziká:

- compromised client runtime,
- stolen private key,
- nesprávna nonce/replay validácia,
- proxy, ktorý odstráni sender-binding context,
- resource server, ktorý binding neoveruje.

## 12. Scope

Scope je client-requested a server-approved obmedzenie oprávnení.

Dobré scopes sú:

- stabilné,
- zrozumiteľné,
- viazané na API capability,
- dostatočne jemné pre least privilege,
- nie extrémne granularizované na každý resource instance.

Príklady:

```text
orders.read
orders.write
payments.refund
```

Scope nie je kompletná authorization policy. Resource server stále môže vyhodnocovať:

- resource ownership,
- tenant,
- account status,
- transaction amount,
- environment,
- ABAC/RBAC pravidlá.

## 13. Audience a resource indicators

Audience určuje, pre ktorý resource server je token určený.

Bez správnej audience restriction môže token vydaný pre jedno API prijať iné API.

Resource server musí odmietnuť token:

- s nesprávnym `aud`,
- bez očakávaného resource bindingu,
- z nedôveryhodného issuera,
- určený pre iné environment alebo tenant boundary.

Scope a audience riešia odlišné otázky:

```text
audience → kde možno token použiť
scope    → čo možno vykonať
```

## 14. Refresh token

Refresh token umožňuje získať nový access token bez opakovanej user interaction.

Je spravidla citlivejší než access token, pretože:

- má dlhšiu lifetime,
- môže vydávať viac access tokens,
- kompromitácia môže prežiť krátku access-token expiráciu.

Controls:

- rotation,
- reuse detection,
- client binding,
- sender constraint, ak je dostupná,
- inactivity a absolute expiration,
- revocation pri logout/credential compromise,
- bezpečné storage,
- minimálny scope.

Public clients musia používať refresh-token rotation alebo sender-constrained refresh tokens podľa security modelu authorization servera.

## 15. Refresh-token rotation

Pri každom použití sa vydá nový refresh token a starý sa stane neplatným.

```text
RT1 → access token + RT2
RT2 → access token + RT3
```

Ak sa po použití RT1 objaví ďalší request s RT1, server môže detegovať reuse a revoke-nuť token family.

Riziká:

- race conditions medzi súbežnými refreshmi,
- client, ktorý neuloží nový token atomicky,
- nejasný recovery model,
- distributed authorization-server consistency.

## 16. Client authentication

Confidential client sa autentizuje voči token endpointu.

Možnosti:

- client secret,
- `private_key_jwt`,
- mutual TLS,
- ďalšie štandardizované metódy.

Preferuj asymmetric authentication, keď je praktická:

- authorization server nemusí držať rovnaký symmetric secret,
- jednoduchšia key rotation boundary,
- menší dopad server-side credential leakage.

Client secret zabudovaný v browseri, mobile aplikácii alebo distribuovanom binary nie je dôveryhodný secret.

## 17. Client Credentials grant

Používa sa pre machine-to-machine access, kde client koná vo vlastnom mene.

```text
workload identity
→ client authentication
→ token endpoint
→ access token pre API
```

Nejde o používateľskú delegation.

Controls:

- workload-specific client identity,
- krátkodobé credentials alebo federation,
- úzky scope/audience,
- environment isolation,
- rotation,
- audit podľa workload instance/session,
- zákaz shared client credentials medzi viacerými tímami.

## 18. Device Authorization flow

Vhodný pre zariadenia bez pohodlného browser inputu.

Model:

```text
device získa device code a user code
→ používateľ otvorí verification URI na inom zariadení
→ autentizuje sa a autorizuje
→ device polluje token endpoint
→ po schválení dostane token
```

Controls:

- dostatočne náhodný user code,
- obmedzená lifetime,
- správny polling interval,
- rate limiting,
- jasné zobrazenie clienta a požadovaného accessu,
- ochrana proti phishingu a code substitution.

## 19. Deprecated alebo neodporúčané patterns

### Implicit grant

Access token sa vracia cez browser redirect. Moderné security odporúčania preferujú Authorization Code flow, aby token nebol vystavený v browser URL a aby bolo možné použiť PKCE a ďalšie controls.

### Resource Owner Password Credentials

Client priamo zbiera user password a vymieňa ho za token.

Tento model:

- ruší separation medzi clientom a credentials,
- komplikuje MFA a federation,
- podporuje password reuse,
- nemá byť používaný v nových systémoch.

### Wildcard redirect URIs

Zväčšujú attack surface a umožňujú code leakage.

### Long-lived broad bearer tokens

Zvyšujú blast radius compromise.

## 20. Token format: opaque oproti JWT

### Opaque token

Resource server používa introspection alebo lokálnu reference cache.

Výhody:

- okamžitejšia central revocation,
- claims nie sú vystavené clientovi,
- authorization server kontroluje aktuálny stav.

Nevýhody:

- runtime dependency na introspection,
- latency a availability,
- cache consistency.

### JWT access token

Resource server validuje token lokálne.

Výhody:

- nižšia runtime dependency na authorization server,
- škálovateľnosť,
- explicitné claims.

Nevýhody:

- revocation je ťažšia,
- stale authorization do expirácie,
- key rotation/JWKS cache failures,
- claim leakage,
- chybná algorithm/issuer/audience validácia.

JWT nie je automaticky bezpečnejší než opaque token.

## 21. Token introspection

Introspection endpoint umožňuje resource serveru zistiť, či je token aktívny a aké metadata sa naň viažu.

Resource server musí:

- autentizovať sa voči introspection endpointu,
- chrániť response,
- validovať `active`, audience a scope,
- definovať cache TTL,
- správať sa bezpečne pri timeout-e,
- monitorovať dependency availability.

Fail-open pri nefunkčnej introspection službe môže porušiť authorization.

## 22. Token revocation

Revocation endpoint umožňuje clientovi alebo operátorovi zneplatniť token alebo grant.

Revocation model musí určiť:

- access token vs refresh token,
- token family,
- propagáciu do distributed resource servers,
- cache invalidation,
- logout semantics,
- incident response,
- audit.

JWT access token môže zostať technicky validný do expirácie, pokiaľ resource server nepoužíva denylist, introspection alebo veľmi krátku lifetime.

## 23. Authorization Server Metadata

Metadata discovery znižuje configuration drift.

Môže publikovať:

- authorization endpoint,
- token endpoint,
- issuer,
- JWKS URI,
- supported grants,
- PKCE methods,
- token endpoint authentication methods,
- revocation/introspection endpoints.

Client musí metadata načítať z dôveryhodného issuer location a validovať issuer identity.

Dynamic discovery bez trust policy môže viesť na attacker-controlled endpoints.

## 24. Key management

Authorization server používa cryptographic keys na signing alebo client authentication.

Potrebné controls:

- oddelenie signing a encryption keys,
- stable key IDs,
- JWKS publication,
- overlap počas rotation,
- cache refresh,
- emergency revocation,
- HSM/KMS podľa risku,
- audit key lifecycle-u,
- zákaz weak alebo unexpected algorithms.

Resource server nesmie automaticky akceptovať algorithm určený neovereným token headerom bez vlastnej allowlist policy.

## 25. Consent

Consent je user-facing authorization interaction, nie náhrada server-side policy.

Dobrý consent:

- identifikuje clienta,
- uvádza požadované capabilities,
- odlišuje povinný a voliteľný access,
- nezahlcuje technickými scope názvami,
- umožňuje revocation,
- rešpektuje organization policy.

Pri first-party enterprise aplikácii môže authorization vychádzať z administratívnej policy bez individuálneho consentu.

## 26. Multi-tenant model

Explicitne definuj:

- issuer per tenant alebo shared issuer,
- tenant claim a validation,
- client registration boundary,
- redirect URI ownership,
- admin consent,
- cross-tenant access,
- token audience,
- audit ownera.

Resource server nesmie veriť tenant claimu bez overenia issuera a authorization contextu.

## 27. Browser applications a BFF

Browser-based applications nevedia spoľahlivo chrániť long-lived secrets.

Patterns:

- Authorization Code + PKCE priamo v browseri,
- Backend for Frontend, ktorý drží tokens server-side a browseru vydáva chránenú session cookie.

BFF môže znížiť token exposure v browser runtime, ale pridáva:

- session a CSRF security,
- backend availability,
- cookie configuration,
- proxy authorization boundary.

## 28. Native applications

Native application je public client.

Požiadavky:

- system browser namiesto embedded webview,
- Authorization Code + PKCE,
- loopback alebo claimed HTTPS/custom URI podľa platform guidance,
- exact redirect validation,
- secure OS storage podľa možností,
- žiadny embedded client secret považovaný za confidential.

## 29. API gateway a token propagation

Gateway môže validovať token, ale downstream service musí poznať trust contract.

Možnosti:

- propagovať originálny access token,
- token exchange na downstream audience,
- signed internal identity context,
- service-to-service workload token.

Riziká:

- confused deputy,
- broad token použiteľný vo všetkých services,
- spoofed identity headers,
- proxy, ktorý neodstráni inbound security headers,
- strata original actor/delegation chain.

## 30. Token exchange a delegation

Token exchange umožňuje vymeniť token za iný token vhodný pre downstream resource alebo delegation context.

Musí byť explicitné:

- subject,
- actor,
- audience,
- scope,
- delegation vs impersonation,
- chain depth,
- audit correlation.

Downstream token nemá automaticky zdediť všetky oprávnenia upstream tokenu.

## 31. Audit

Audit record pre OAuth má obsahovať podľa udalosti:

- issuer,
- client ID,
- resource owner/subject,
- actor/delegated identity,
- grant type,
- requested a granted scopes,
- audience/resource,
- authentication method,
- token family alebo opaque correlation identifier,
- result/error,
- source context,
- timestamp,
- revocation/rotation event.

Neloguj:

- access token,
- refresh token,
- authorization code,
- client secret,
- PKCE verifier.

## 32. Threats a mitigations

### Authorization code interception

Mitigácia: PKCE, short lifetime, one-time code, exact redirect URI.

### Authorization code injection

Mitigácia: PKCE alebo OIDC nonce binding podľa správneho flowu, issuer validation.

### CSRF

Mitigácia: transaction-bound `state`, secure session/cookies, PKCE defense in depth.

### Mix-up attack

Mitigácia: issuer binding, metadata validation, distinct endpoints/redirect bindings.

### Token replay

Mitigácia: sender-constrained tokens, short lifetime, secure storage, audience restriction.

### Token leakage

Mitigácia: TLS, no URL/logs, browser/storage controls, redaction.

### Refresh-token theft

Mitigácia: rotation, reuse detection, sender binding, revocation.

### Confused deputy

Mitigácia: audience/resource binding, explicit actor/subject, downstream token exchange.

## 33. Troubleshooting authorization flow

```text
client registration a redirect URI?
→ issuer/metadata?
→ authorization request parameters?
→ user authentication a consent/policy?
→ state/nonce transaction binding?
→ authorization code lifetime a reuse?
→ PKCE verifier/challenge?
→ client authentication?
→ token endpoint response?
→ access-token issuer/audience/scope?
→ resource-server policy?
```

Zachovaj correlation ID bez zachytenia secret values.

## 34. Typické chyby

### `invalid_redirect_uri`

Over exact registration, scheme, host, port, path, encoding a environment.

### `invalid_grant`

Možné:

- code expired alebo už použitý,
- redirect URI mismatch,
- PKCE mismatch,
- refresh token revoked/rotated,
- wrong client binding,
- clock problem.

### `invalid_client`

Over client ID, authentication method, secret/key rotation, JWT audience a clock.

### `invalid_scope`

Over scope allowlist, grant type, client policy, resource indicator a tenant.

### API vracia `401`

Over token presence, format, signature/introspection, issuer, audience, expiration a sender proof.

### API vracia `403`

Authentication/token validation mohli uspieť, ale chýba scope alebo resource-level oprávnenie.

## 35. Operational monitoring

Sleduj:

- authorization success/error rate,
- token endpoint latency/errors,
- errors podľa grant type-u a clienta v bounded forme,
- PKCE/state/nonce validation failures,
- refresh reuse detection,
- token revocation,
- JWKS/key rotation failures,
- introspection latency a availability,
- client authentication failures,
- suspicious consent alebo scope escalation,
- DPoP/mTLS proof failures.

High-cardinality identifiers drž v logs/audit records, nie metric labels.

## 36. Incident response

Pri token alebo client credential compromise:

1. identifikuj token/grant/client scope,
2. revoke-ni refresh token family a sessions,
3. rotate client secret/private key podľa compromise,
4. skráť alebo denylistni access tokens podľa možností,
5. zachovaj audit evidence,
6. analyzuj použité audiences/scopes,
7. obnov dôveryhodný client deployment,
8. monitoruj replay a ďalšie token issuance,
9. oprav root cause.

## 37. Anti-patterny

### OAuth ako login bez OpenID Connect

Access token nie je štandardný proof používateľskej authentication pre clienta.

### JWT decode bez validácie

Claims z neovereného tokenu sú attacker-controlled input.

### Jeden token pre všetky APIs

Chýba audience isolation a rastie blast radius.

### Scope ako jediná authorization vrstva

Resource ownership, tenant a business policy zostanú neoverené.

### Client secret v SPA/mobile aplikácii

Distribuovaný secret nemožno považovať za confidential.

### Tokens v local storage bez threat analýzy

XSS môže token odcudziť.

### Long-lived refresh token bez rotation

Kompromitácia sa ťažko deteguje a revoke-nuje.

### Wildcard redirect URI

Umožňuje code leakage alebo redirect abuse.

### Access token poslaný inému audience

Vzniká confused-deputy a cross-service abuse.

## 38. Kontrolné otázky

1. Aké sú štyri hlavné OAuth role?
2. Prečo OAuth nie je login protocol?
3. Ako funguje Authorization Code + PKCE?
4. Aký je rozdiel medzi `state`, PKCE a OIDC `nonce`?
5. Ako sa líši scope a audience?
6. Prečo bearer token potrebuje krátku lifetime?
7. Čo rieši sender-constrained token?
8. Ako funguje refresh-token rotation a reuse detection?
9. Kedy použiť Client Credentials grant?
10. Ako sa líši opaque a JWT access token?
11. Prečo úspešná token validation neznamená resource authorization?
12. Ako diagnostikuješ `401` oproti `403`?

## Glossary impact

Relevantné pojmy: OAuth 2.0, resource owner, client, authorization server, resource server, authorization endpoint, token endpoint, authorization grant, authorization code, PKCE, code verifier, code challenge, redirect URI, state, access token, bearer token, sender-constrained token, scope, audience, refresh token, refresh-token rotation, token family, client authentication, client credentials grant, device authorization flow, opaque token, JWT access token, token introspection, token revocation, authorization-server metadata, consent, BFF, token exchange a confused deputy.

## Primárne zdroje

- [OAuth 2.0 Authorization Framework — RFC 6749](https://www.rfc-editor.org/rfc/rfc6749)
- [OAuth 2.0 Security Best Current Practice — RFC 9700](https://www.rfc-editor.org/rfc/rfc9700)
- [Bearer Token Usage — RFC 6750](https://www.rfc-editor.org/rfc/rfc6750)
- [PKCE — RFC 7636](https://www.rfc-editor.org/rfc/rfc7636)
- [OAuth 2.0 Authorization Server Metadata — RFC 8414](https://www.rfc-editor.org/rfc/rfc8414)
- [Token Introspection — RFC 7662](https://www.rfc-editor.org/rfc/rfc7662)
- [Token Revocation — RFC 7009](https://www.rfc-editor.org/rfc/rfc7009)
- [Device Authorization Grant — RFC 8628](https://www.rfc-editor.org/rfc/rfc8628)
- [OAuth 2.0 mTLS — RFC 8705](https://www.rfc-editor.org/rfc/rfc8705)
- [DPoP — RFC 9449](https://www.rfc-editor.org/rfc/rfc9449)
- [OAuth 2.0 Token Exchange — RFC 8693](https://www.rfc-editor.org/rfc/rfc8693)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Kerberos](kerberos.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OpenID Connect →](openid-connect.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
