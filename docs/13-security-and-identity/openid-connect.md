# OpenID Connect

OpenID Connect 1.0 — OIDC — je interoperabilná authentication a identity vrstva nad OAuth 2.0. OAuth definuje, ako client získa obmedzený access k resource serveru. OIDC pridáva štandardizovaný spôsob, ktorým client overí, že OpenID Provider autentizoval konkrétneho End-Usera pre konkrétneho clienta, a získa claims o tejto identity.

Hlavným authentication artifactom je ID Token. Je určený Relying Party, nie API. Application po jeho validácii vytvorí vlastnú local session. Access token má inú audience a lifecycle: používa sa voči UserInfo alebo inému resource serveru.

```text
End-User otvorí Relying Party
→ RP vytvorí OIDC authorization request a transaction state
→ OpenID Provider autentizuje usera
→ browser vráti authorization code
→ RP backend vymení code za tokens
→ RP validuje ID Token a optional UserInfo claims
→ identity key issuer + subject nájde local account
→ RP vytvorí vlastnú application session
→ local authorization rozhoduje o resources a actions
```

## 1. Problém, ktorý OIDC rieši

Samotný OAuth access token nepredstavuje štandardný dôkaz authentication eventu pre client application. Token môže byť opaque, určený inému API, vydaný bez aktívneho user loginu alebo obsahovať claims s resource-server semantics.

OIDC definuje:

- authentication request pomocou scope `openid`;
- ID Token s issuer, subject, audience a time claims;
- exact validation rules;
- standard identity claims;
- UserInfo endpoint;
- discovery a client metadata;
- subject identifier privacy model;
- session a logout specifications.

Client teda nemusí interpretovať vendor-specific access token ako login response.

## 2. Role

**End-User** je human subject, ktorého authentication event Provider potvrdzuje.

**Relying Party — RP** je OAuth client, ktorý používa OIDC na login. Môže byť server-side web application, native app, SPA s Backend for Frontend alebo iný client type.

**OpenID Provider — OP** je OAuth Authorization Server podporujúci OIDC a vydávajúci ID Tokens.

**UserInfo endpoint** je OAuth-protected resource vracajúci claims o subjecte pre access token s vhodným scope-om.

Role sú logical. Jeden product môže byť OP aj API platforma, ale token consumers a audiences zostávajú oddelené.

## 3. OAuth oproti OIDC

OAuth odpovedá:

```text
Aký access môže tento client vykonať voči resource serveru?
```

OIDC odpovedá:

```text
Ktorý issuer autentizoval ktorého subjecta pre ktorého clienta,
kedy a s akým authentication contextom?
```

Access token je credential pre resource server. ID Token je signed authentication assertion pre client. Resource server nemá štandardne akceptovať ID Token a client nemá používať access token ako náhradu ID Token-u.

OIDC používa OAuth authorization endpoint, token endpoint, client registration, redirect URI a code exchange. Preto všetky OAuth transaction protections zostávajú relevantné.

## 4. Scope `openid`

Authorization request sa stáva OIDC requestom iba vtedy, keď scope obsahuje `openid`. Bez neho ide o OAuth request a Provider nie je povinný vydať ID Token.

Ďalšie štandardné scopes žiadajú claim categories:

- `profile` — meno, preferred username, locale a podobné profile claims;
- `email` — email a `email_verified`;
- `address`;
- `phone`;
- `offline_access` — požiadavka na refresh-token/offline semantics podľa Provider policy.

Scope nie je guarantee, že každá claim bude vydaná. OP zohľadňuje consent, privacy, client registration a policy.

## 5. Authorization Code flow

Moderný OIDC web/native design používa Authorization Code flow s PKCE. Browser front channel prenáša iba krátkodobý code; tokens sa získajú na token endpoint-e.

```text
RP → authorization endpoint:
  client_id, redirect_uri, scope=openid,
  state, nonce, code_challenge

OP → RP redirect URI:
  code, state

RP → token endpoint:
  code, redirect_uri, code_verifier,
  client authentication podľa client type-u

OP → RP:
  ID Token, access token, optional refresh token
```

Code je single-use a viazaný na client, redirect URI a PKCE verifier. Confidential RP navyše autentizuje svoju client identity na token endpoint-e.

## 6. Authorization request

OIDC authorization request obsahuje OAuth parameters a OIDC-specific context.

Dôležité fields:

- `client_id` — registered RP identity;
- `redirect_uri` — exact registered callback;
- `response_type=code`;
- `scope` obsahujúci `openid`;
- `state` — client transaction binding a CSRF protection;
- `nonce` — ID Token binding k authentication requestu;
- PKCE `code_challenge` a method;
- optional `prompt`, `max_age`, `login_hint`, `acr_values`, claims request.

RP uloží transaction state server-side alebo v integrity-protected browser state. Parallel login attempts sa musia rozlišovať; jedna global nonce pre celý browser je nesprávna.

## 7. `state`

`state` koreluje authorization response s konkrétnou RP transaction a pomáha brániť login CSRF a response injection.

Flow:

```text
RP vytvorí random state
→ uloží ho s issuerom, nonce, PKCE verifierom, redirect URI a return pathom
→ po callbacku porovná exact value
→ atomicky transaction spotrebuje
```

`state` nemá byť iba pôvodná URL. Return destination sa uloží server-side alebo podpíše a allowlistuje. Sensitive data nepatria do URL-visible state.

## 8. `nonce`

`nonce` viaže ID Token na konkrétny authentication request. RP ho pošle OP a očakáva exact value v ID Token-e.

Ak attacker vloží validný ID Token z inej transaction, signature a audience môžu sedieť, ale nonce mismatch odhalí, že token nepatrí k aktuálnemu loginu.

Nonce má byť random, transaction-specific, jednorazová a uložená oddelene pre parallel attempts. Validuje sa pred vytvorením local session.

## 9. PKCE

Proof Key for Code Exchange via Code Exchange — PKCE — viaže authorization code na RP instance, ktorá vytvorila `code_verifier`.

```text
RP vygeneruje secret code_verifier
→ odošle hash ako code_challenge
→ OP uloží binding k code-u
→ token request musí predložiť original verifier
```

Attacker, ktorý zachytí code, ho bez verifiera nevymení. PKCE nerieši ID Token replay ani login CSRF; preto dopĺňa nonce a state.

## 10. State, nonce a PKCE spolu

Tieto values chránia rozdielne edges:

```text
state
→ callback patrí k RP browser transaction

nonce
→ ID Token patrí k authentication requestu

PKCE
→ code exchange patrí k client instance
```

Jedna value nemá byť mechanicky používaná ako náhrada všetkých troch bez formálneho protocol profile-u. RP library má ich lifecycle spravovať ako jednu transaction, ale validovať ich individuálne.

## 11. Authorization response a issuer binding

Callback obsahuje `code`, `state` alebo protocol error. Pri clients komunikujúcich s viacerými issuers vzniká mix-up risk: response z jedného OP môže byť nesprávne poslaná na token endpoint druhého.

RP preto uchová expected issuer v transaction state a presne validuje issuer ID v následnom ID Token-e. OAuth Authorization Server Issuer Identification podľa RFC 9207 môže pridať `iss` priamo do authorization response, ak Provider podporuje profile.

User-controlled tenant/issuer parameter nesmie automaticky vybrať arbitrary discovery URL.

## 12. Token endpoint exchange

RP posiela code na token endpoint z trusted discovery/configuration. Request obsahuje exact `redirect_uri`, PKCE verifier a client authentication, ak je client confidential.

`invalid_grant` môže znamenať expired alebo reused code, PKCE mismatch, redirect URI mismatch alebo code vydaný inému clientovi. Retry rovnakého code-u nemá pokračovať nekonečne; code je single-use.

Token response je citlivá. Neloguj ID Token, access token, refresh token ani client assertion. RP má overiť TLS a expected endpoint origin.

## 13. ID Token

ID Token je JSON Web Token obsahujúci claims o subjecte a authentication evente. V Authorization Code flowe sa typicky vracia z token endpointu a je podpísaný OP keyom.

Core claims:

- `iss` — exact issuer identifier;
- `sub` — stable subject identifier v issuer scope-e;
- `aud` — intended RP client ID alebo audiences;
- `exp` — expiry;
- `iat` — issuance time.

Context claims môžu zahŕňať `nonce`, `auth_time`, `acr`, `amr`, `azp`, `at_hash`, `c_hash` a profile claims podľa flowu a Provider policy.

ID Token je input do RP authentication. Nie je local session ani API access credential.

## 14. Complete ID Token validation pipeline

RP validuje token v presnom context-e transaction:

1. bounded-size JWT sa syntakticky parsuje;
2. JOSE algorithm je na allowliste pre daného issuera/clienta;
3. key sa vyberie iba z trusted issuer JWKS;
4. signature sa overí;
5. `iss` sa exactne porovná s expected issuerom;
6. `aud` obsahuje RP client ID;
7. `azp` sa validuje pri multiple audiences podľa Core rules;
8. `exp`, `iat` a optional `nbf` sa kontrolujú s bounded skew;
9. nonce sa exactne zhoduje s pending transaction;
10. `auth_time`, `acr`, `amr` spĺňajú requested assurance, ak sú required;
11. `at_hash`/`c_hash` sa validujú, keď ich flow vyžaduje;
12. transaction sa atomicky spotrebuje;
13. až potom sa claims mapujú na local identity/session.

Base64 decode alebo úspešná signature bez issuer/audience/nonce validation nie je authentication.

## 15. Issuer ako trust boundary

Issuer je stable URL identifier OP a primary trust namespace OIDC relationshipu. RP ho konfiguruje alebo získa cez trusted onboarding a následne porovnáva exact string.

Development, production a tenant issuers sa nemajú zamieňať. Token podpísaný známym keyom, ale s neočakávaným `iss`, sa odmietne.

RP nesmie načítať JWKS URI alebo token endpoint z token-provided arbitrary URL. Discovery metadata sú trusted iba po issuer bootstrap a issuer consistency validation.

## 16. Subject identifier

`sub` je locally unique a never-reassigned identifier subjectu u konkrétneho issuer-a podľa Provider contractu. Globálna identity key je kombinácia:

```text
issuer + subject
```

Email, username alebo display name sa môžu zmeniť, recyklovať alebo kolidovať medzi issuers. Použitie emailu ako primary key umožňuje account takeover pri reassignment alebo malicious federation.

Application môže email používať ako contact attribute, nie ako immutable external identity key.

## 17. Public a pairwise subjects

Public subject type používa rovnaký `sub` pre clients v danom issuer scope-e. Uľahčuje account correlation a linking, ale zvyšuje privacy correlation medzi applications.

Pairwise subject generuje odlišný `sub` pre každého sector identifiera alebo client grouping. Dve nesúvisiace RPs nedokážu jednoducho zistiť, že ide o rovnakého usera.

Pairwise model komplikuje linking a migration. Enterprise suite môže používať controlled sector grouping, ale musí rozumieť privacy a lifecycle dôsledkom.

## 18. Audience a authorized party

`aud` identifikuje clients, pre ktoré je ID Token určený. RP odmietne token, ktorý neobsahuje jeho client ID.

Keď `aud` obsahuje viac values, `azp` identifikuje authorized party podľa OIDC rules. RP má odmietnuť unexpected `azp`.

Audience validation zabraňuje tomu, aby attacker použil ID Token získaný pre inú application. Valid issuer a signature bez správnej audience nestačia.

## 19. JWT signature a algorithm policy

RP nemá veriť JOSE `alg` iba preto, že je v token headeri. Pre každého Provider-a/clienta má configured allowlist očakávaných ID Token signing algorithms.

Odmietni `none` a algorithm confusion. Symmetric algorithm vyžaduje shared client secret a má iný trust model než asymmetric issuer signature; library configuration musí zodpovedať registration metadata.

Token header `kid` vyberá candidate key, ale nevytvára trust. Unknown `kid` môže spustiť bounded JWKS refresh, nie arbitrary key fetch.

## 20. JWKS a key rotation

JSON Web Key Set publikuje OP public signing keys. RP ho načíta z trusted `jwks_uri`, cache-uje a používa `kid`/algorithm/key type na selection.

Rotation flow:

```text
OP publikuje nový key popri starom
→ RPs JWKS obnovia
→ OP začne podpisovať novým keyom
→ old tokens zostávajú validovateľné do expiry
→ starý key sa odstráni po overlap intervale
```

RP má bounded cache TTL, refresh-once behavior pri unknown key a protection pred refresh stormom. Emergency key compromise môže vyžadovať okamžité odstránenie trustu a invalidáciu sessions, nie čakanie na normal expiry.

## 21. Discovery

OpenID Provider Configuration je JSON metadata document typicky na well-known endpoint-e. Obsahuje issuer, authorization/token/UserInfo endpoints, JWKS URI, supported response types, subject types, algorithms, scopes a optional logout capabilities.

Trusted flow:

```text
operator alebo tenant onboarding určí expected issuer
→ RP fetchne discovery z issuer-derived well-known URL
→ metadata issuer musí exactne sedieť
→ endpoints/JWKS sa uložia pod týmto trust namespace-om
```

Discovery znižuje configuration drift, ale nevytvára trust z arbitrary URL. Metadata refresh potrebuje TLS, cache, error a last-known-good policy.

## 22. UserInfo endpoint

UserInfo je OAuth-protected resource. RP mu pošle access token a dostane claims o subjecte.

RP musí overiť, že `sub` v UserInfo response exactne zodpovedá validated ID Token `sub`. Inak by response mohla zmeniť authenticated identity.

UserInfo claims sa môžu meniť medzi loginom a callom a majú data-classification/privacy lifecycle. RP žiada iba potrebné scopes a neloguje response.

UserInfo nepridáva nový authentication event. Je to supplemental claims retrieval via access token.

## 23. Standard claims a ich authority

Standard claim name poskytuje interoperabilnú syntax, nie universal business authority.

Examples:

- `name`, `given_name`, `family_name` — display profile;
- `preferred_username` — mutable display/login hint;
- `email` a `email_verified` — provider-specific verification semantics;
- `phone_number` a verification;
- `locale`, `zoneinfo`, `address`.

`email_verified=true` znamená iba to, čo Provider contract definuje o control nad emailom. Neznamená employment, tenant membership ani authorization role.

## 24. Claims mapping

RP prekladá external claims do internal modelu:

```text
issuer + claim name
→ expected type a cardinality
→ normalization
→ internal attribute
→ local policy alebo display use
```

Pre každý mapping definuj required/optional behavior, maximum size/count, Unicode/case rules, trusted source a deprovisioning freshness.

Privileged role nemá vzniknúť z arbitrary group stringu bez allowlistu a federation contractu. Missing optional claim nesmie prepnúť usera do unsafe default tenant-a.

## 25. ACR

Authentication Context Class Reference — `acr` — je identifier authentication assurance alebo policy class. Jeho semantics vznikajú dohodou medzi OP a RP alebo profile specification.

RP môže požadovať `acr_values` a následne overiť returned `acr`. Nemá interpretovať unknown string ako „MFA“ alebo porovnávať values lexicographically.

Example enterprise contract môže definovať:

```text
urn:example:loa:1 → password alebo existing low-assurance session
urn:example:loa:2 → MFA
urn:example:phishing-resistant → WebAuthn hardware-backed authentication
```

Mapping musí byť versionovaný a auditovaný.

## 26. AMR

Authentication Methods References — `amr` — je array identifiers použitých methods, napríklad password, OTP, hardware key alebo federated authentication podľa Provider convention.

`amr` často opisuje components, zatiaľ čo `acr` opisuje resulting class/policy. RP nemá skladať high-impact authorization z náhodných AMR strings bez contractu.

Federated OP môže uviesť method len na základe upstream assertion. RP musí dôverovať celému federation chain-u alebo používať ACR/profile s jasnými semantics.

## 27. `auth_time` a `max_age`

`auth_time` je čas aktívnej End-User authentication. Nie je to ID Token issuance time; OP môže vydať nový token z existujúcej SSO session.

`max_age` žiada, aby authentication nebola staršia než určitý interval. OP potom vracia `auth_time`, ktorý RP validuje.

Sensitive operation môže vyžadovať fresh authentication aj keď application session je validná. Reauthentication freshness a method assurance sú samostatné: fresh password nemusí spĺňať phishing-resistant requirement.

## 28. `prompt`

`prompt` ovplyvňuje interaction policy:

- `none` — žiadna user interaction; ak nie je vhodná OP session/consent, vráti sa protocol error;
- `login` — žiada reauthentication;
- `consent` — žiada consent interaction;
- `select_account` — žiada account selection.

RP nesmie považovať `prompt=login` samo osebe za guarantee konkrétnej authentication method. Výsledné `auth_time` a `acr`/`amr` sa stále validujú.

Silent login failure pri `prompt=none` je normálny branch, nie system outage.

## 29. Local application session

Validated ID Token je evidence pre vytvorenie local session. RP má vlastný session lifecycle:

- regeneruje session ID po login-e;
- používa Secure, HttpOnly a appropriate SameSite cookie;
- chráni state-changing requests pred CSRF;
- má idle a absolute timeout;
- server-side revocation alebo bounded self-contained session;
- step-up/reauthentication pre sensitive actions;
- audit identity a authentication contextu.

ID Token nemá byť automaticky uložený ako long-lived browser session cookie. Jeho expiry a OP claims nemusia zodpovedať application session policy.

## 30. ID Token oproti access tokenu

| Vlastnosť | ID Token | Access token |
|---|---|---|
| Primárny consumer | OIDC Relying Party | Resource server/API |
| Audience | client ID | API/resource audience |
| Účel | authentication assertion | authorization credential |
| Validácia | issuer, client audience, nonce, auth context | API-specific token/introspection policy |
| Posielať API | nie | áno |
| Použiť ako local session | iba ako initial evidence | nie |

Token types môžu byť obe JWT, ale rovnaký serialization neznamená rovnakú semantics.

## 31. Refresh token a `offline_access`

Refresh token je OAuth credential, ktorým client získava nové access tokens bez opätovného user authorization flowu. OIDC `offline_access` signalizuje požiadavku na access mimo aktívnej End-User session podľa Provider policy a consent.

Refresh token nepredstavuje nový user authentication event. Nový ID Token vydaný pri refresh-i môže opisovať pôvodný authentication context.

Refresh token potrebuje secure storage, rotation/reuse detection, revocation, client binding a bounded scope. Browser exposure výrazne zvyšuje risk; BFF môže držať refresh token server-side.

## 32. Account linking

Rovnaký človek môže mať identities od viacerých issuers alebo viac pairwise subjects. Linking je security-sensitive operation, pretože zlúčenie identities prenáša access a account history.

Unsafe pattern:

```text
rovnaký email → automaticky zlúčiť účty
```

Bezpečnejšie patterns:

- user sa autentizuje oboma identities v jednej protected session;
- enterprise authoritative identifier a verified tenant contract;
- administrator approval s auditom;
- notification a recovery/unlink process;
- prevention duplicate privileged account takeover.

Email reassignment alebo malicious issuer nesmie prevziať existing account.

## 33. Multi-tenant OIDC

Multi-tenant RP musí definovať trust onboarding a identity namespace.

Možnosti sú issuer per tenant alebo shared issuer s explicitným tenant claimom. V oboch prípadoch treba určiť:

- allowed issuers a discovery bootstrap;
- client registration ownership;
- `issuer + sub` uniqueness;
- tenant claim authority;
- account-linking isolation;
- admin consent a lifecycle;
- logout/session scope;
- behavior pri tenant removal.

User input ako `?issuer=https://attacker.example` nesmie vytvoriť trust. Email-domain discovery je routing hint a musí mapovať iba na pre-approved issuer.

## 34. Native applications

Native app je public client: binary beží na user device a client secret nemožno považovať za confidential.

Používa system browser, Authorization Code + PKCE a platform-approved redirect pattern, napríklad claimed HTTPS URI alebo loopback URI podľa platform guidance. Embedded webview znižuje phishing a session isolation properties.

Tokens sa ukladajú v OS-provided secure storage podľa threat modelu. Compromised device môže stále získať tokens; short lifetime, refresh rotation a device/application binding znižujú impact.

## 35. Browser SPA a Backend for Frontend

SPA beží v browser origin a je vystavená XSS. Authorization Code + PKCE chráni code interception, ale malicious script v origin-e môže čítať browser-accessible tokens.

Backend for Frontend — BFF — drží tokens server-side a browser dostane application session cookie. Znižuje token exposure v JavaScript, ale pridáva CSRF, session, backend availability a proxy authorization requirements.

Výber závisí od application architecture. OIDC neodstraňuje CSP, dependency security, output encoding ani session-cookie protections.

## 36. Workload identity federation

OIDC-compatible JWT issuers sa používajú aj pre non-human workloads. Kubernetes, CI platforma alebo cloud runtime vydá short-lived identity token; cloud/Vault/resource service ho validuje alebo vymení za scoped credential.

Trust policy kontroluje:

- exact issuer;
- audience určenú target service-u;
- workload-specific subject;
- repository/workflow/branch/environment alebo ServiceAccount/namespace claims;
- short lifetime;
- replay/exchange semantics;
- no broad wildcard mapping.

Workload token nie je human ID Token login. Má odlišný subject lifecycle, authentication mechanism a authorization model, hoci používa JWT/OIDC discovery/JWKS primitives.

## 37. ID Token encryption

ID Token je vždy integrity-protected podľa configured signing/MAC semantics a môže byť voliteľne JWE-encrypted pre RP.

Encryption skryje claims pred browserom/intermediaries, ale RP stále musí validovať inner signed token alebo agreed nested JWT structure. Encryption nenahrádza TLS.

Pridáva client decryption key lifecycle, rotation, algorithm negotiation a outage risk. Sensitive claims je často lepšie nevkladať do ID Token-u a získať ich server-side cez UserInfo alebo domain API.

## 38. Logout meanings

„Logout“ môže znamenať:

- zrušenie local RP session;
- revocation refresh tokenu;
- ukončenie OP browser session;
- notification ďalším RPs;
- account-wide alebo device-wide session termination.

Tieto lifecycles nie sú automaticky synchronizované. Local logout bez OP logoutu môže viesť k okamžitému SSO loginu. OP logout nemusí revoke-nuť API access tokeny alebo application-specific sessions.

RP musí presne definovať desired scope a user expectation.

## 39. RP-Initiated Logout

RP-Initiated Logout umožňuje RP presmerovať usera na OP end-session endpoint. Môže poslať `id_token_hint`, `post_logout_redirect_uri`, `state` a ďalšie parameters podľa specification/Provider supportu.

Post-logout redirect URI musí byť pre-registered. `state` viaže callback k local logout transaction.

RP má local session ukončiť bezpečne aj keď OP logout zlyhá. Nesmie držať local account authenticated iba preto, že browser nedokončil external redirect.

## 40. Front-channel logout

OP komunikuje logout k RPs cez browser a RP front-channel logout URI. Delivery závisí od browser behavior, cookies, iframes/GET requests a network availability.

Third-party cookie restrictions môžu zabrániť RP identifikovať session. Front-channel je preto best-effort distributed notification, nie guaranteed transaction.

Endpoint nesmie vykonávať unsafe state changes bez protocol validation a má byť idempotentný.

## 41. Back-channel logout

OP posiela signed logout token priamo RP backendu. Token obsahuje issuer, audience, issued/expiry time, unique `jti`, events claim a `sid` alebo `sub` binding podľa profile-u.

RP validuje signature, issuer, audience, event, replay a session binding a následne zruší local sessions. Server-to-server delivery je menej závislá od browseru, ale potrebuje reachable endpoint a retry/idempotency model.

Logout token nie je ID Token ani access token a nemá byť použitý na login.

## 42. Privacy

OIDC claims sú personal data. ID Token je podpísaný, nie automaticky encrypted; každý holder ho môže base64 decode-nuť.

Privacy controls:

- minimal scopes a claims;
- pairwise subjects;
- purpose limitation;
- informed consent/transparency podľa contextu;
- retention a access audit;
- no claims v URL/logs;
- tenant/data residency policy;
- unlink/delete lifecycle;
- avoidance sensitive entitlements v browser-visible tokens.

Discovery a federation configuration môžu tiež odhaliť organization relationships a endpoints.

## 43. Threats a controls

**Login CSRF / response injection** — state a browser transaction binding.

**Authorization code interception** — PKCE, exact redirect URI, single-use code.

**ID Token replay/injection** — nonce, issuer/audience/time/signature validation a transaction consumption.

**Mix-up** — expected issuer binding, trusted discovery, optional authorization response `iss`.

**Key confusion** — algorithm allowlist, trusted JWKS URI, bounded key selection.

**Account linking takeover** — never auto-link solely by email; authenticate both identities or use authoritative contract.

**Claim escalation** — explicit mapping, allowlisted values, authoritative source a local authorization.

**Token theft** — secure storage, short lifetimes, sender-constrained access tokens where applicable and XSS/session defenses.

## 44. Observability

Sleduj stage-specific metrics a logs:

- authorization requests/callbacks;
- state, nonce a PKCE failures;
- authorization error codes;
- token endpoint latency a `invalid_client`/`invalid_grant`;
- ID Token signature/JWKS refresh failures;
- issuer/audience/azp/time failures;
- ACR/AMR/max-age mismatch;
- account-link/JIT provisioning failures;
- local session creation/revocation;
- front/back-channel logout delivery;
- discovery/JWKS freshness a key rotation.

Neloguj codes, tokens, client secrets ani full claims. Použi transaction ID, issuer, client ID a redacted subject hash podľa privacy policy.

## 45. Troubleshooting flow

```text
expected issuer a discovery metadata?
→ client registration a exact redirect URI?
→ state, nonce a PKCE transaction uložená?
→ OP authentication/consent/prompt outcome?
→ callback state a optional response issuer?
→ code exchange endpoint, client auth, verifier a redirect URI?
→ ID Token JOSE key/algorithm/signature?
→ iss, aud, azp, exp, iat a nonce?
→ auth_time/acr/amr requirements?
→ UserInfo sub consistency?
→ claims mapping a local account?
→ session cookie a application authorization?
```

Login ending in application `403` usually means authentication succeeded, ale local authorization denied. Redirect loop môže byť SameSite/proxy/session issue, nie OP authentication failure.

Unknown `kid` po rotation má spustiť bounded refresh. Repeated refresh bez keyu môže znamenať wrong issuer, stale metadata alebo malicious token.

## 46. Incident response

Pri OP signing-key compromise:

```text
identifikovať issuer, key IDs a exposure interval
→ odstrániť compromised key z trustu alebo quarantine issuer
→ obnoviť trusted discovery/JWKS
→ invalidovať affected RP sessions podľa risku
→ analyzovať login a account-linking audit
→ rotate/recover OP keys
→ testovať issuer, audience, nonce a algorithm validation
```

Pri RP client credential compromise rotate secret/private key a revoke refresh-token/session families. Public client nemá recoverable confidentiality client secretu.

Pri claim-source compromise analyzuj authorization impact, nie iba login count. Validly signed admin claims môžu byť malicious.

## 47. Časté anti-patterny

**Access token ako login token.** Client nevie štandardne overiť authentication context a intended client audience.

**Email ako primary identity key.** Reassignment alebo cross-issuer collision prevezme account.

**Decode bez validation.** JWT claims sú attacker-controlled.

**Issuer z user inputu.** Arbitrary Provider sa stane trusted.

**JWKS URL z token headera.** Attacker určí verification keys.

**Group claim priamo na admin role.** Chýba authoritative mapping a deprovisioning contract.

**ID Token poslaný API.** Resource server akceptuje token určený clientovi.

**ID Token ako browser session cookie.** Token lifetime/claims sa zamieňajú s application session policy.

**Logout ako global revocation.** Local sessions, OP session, access a refresh tokens majú rozdielne lifecycles.

## 48. Kompletný production príklad

User otvorí workforce expense application.

1. RP vytvorí transaction s expected issuerom, random state/nonce, PKCE verifierom a return pathom.
2. Browser ide na authorization endpoint z trusted discovery.
3. OP autentizuje usera WebAuthn a vráti code, state a podporované issuer binding metadata.
4. RP overí state a vymení code na token endpoint-e s verifierom a private-key client authentication.
5. RP vyberie OP key z cached JWKS a overí ID Token signature, `iss`, `aud`, `azp`, `exp`, `iat`, nonce a required `acr`.
6. `issuer + sub` nájde local account. Email sa aktualizuje ako mutable contact claim; privileged role sa mapuje iba z allowlisted enterprise entitlement.
7. RP optional zavolá UserInfo a overí rovnaké `sub`.
8. Transaction sa spotrebuje a RP vytvorí secure local session cookie s vlastným timeoutom.
9. Application vykonáva resource authorization nezávisle od loginu.
10. Audit zachytí transaction ID, issuer, subject hash, ACR, local account a session ID bez raw tokens.
11. Back-channel logout token môže session zrušiť podľa `sid`; refresh token má samostatnú rotation/revocation policy.

## 49. Kontrolné otázky

1. Čo OIDC pridáva nad OAuth 2.0?
2. Ako sa RP, OP, End-User a UserInfo role líšia?
3. Prečo scope `openid` mení protocol semantics?
4. Ako Authorization Code + PKCE flow prenáša authentication evidence?
5. Aký rozdiel je medzi state, nonce a PKCE?
6. Ktoré claims a context musí RP validovať v ID Token-e?
7. Prečo je issuer primary trust boundary?
8. Prečo identity key tvorí `issuer + sub`?
9. Ako public a pairwise subject ovplyvňujú privacy/linking?
10. Ako `aud` a `azp` bránia token substitution?
11. Ako JWKS rotation funguje bez outage-u?
12. Prečo discovery nevytvára trust z arbitrary URL?
13. Aké pravidlo platí pre UserInfo `sub`?
14. Ako sa ACR, AMR a `auth_time` líšia?
15. Prečo local session nie je ID Token?
16. Aké riziká má automatic account linking podľa emailu?
17. Ako sa native app, SPA a BFF threat modely líšia?
18. Ako OIDC primitives podporujú workload identity federation?
19. Ako sa local, RP-initiated, front-channel a back-channel logout líšia?
20. Navrhni complete OIDC ID Token validation a session creation flow.

## Glossary impact

Relevantné pojmy: OpenID Connect, End-User, Relying Party, OpenID Provider, UserInfo endpoint, scope `openid`, Authorization Code OIDC flow, OIDC transaction, state, nonce, PKCE, ID Token, issuer, subject identifier, public subject, pairwise subject, audience, authorized party, ID Token validation, JWKS, OIDC discovery, standard claims, claims mapping, Authentication Context Class Reference, Authentication Methods References, authentication time, max age, prompt, local application session, offline access, account linking, multi-tenant OIDC, Backend for Frontend, workload identity federation, ID Token encryption, RP-Initiated Logout, front-channel logout, back-channel logout a logout token.

## Primárne zdroje

- [OpenID Connect Core 1.0 incorporating errata set 2](https://openid.net/specs/openid-connect-core-1_0.html)
- [OpenID Connect Discovery 1.0 incorporating errata set 2](https://openid.net/specs/openid-connect-discovery-1_0.html)
- [OpenID Connect Session Management 1.0](https://openid.net/specs/openid-connect-session-1_0.html)
- [OpenID Connect RP-Initiated Logout 1.0](https://openid.net/specs/openid-connect-rpinitiated-1_0.html)
- [OpenID Connect Front-Channel Logout 1.0](https://openid.net/specs/openid-connect-frontchannel-1_0.html)
- [OpenID Connect Back-Channel Logout 1.0](https://openid.net/specs/openid-connect-backchannel-1_0.html)
- [RFC 9207 — OAuth 2.0 Authorization Server Issuer Identification](https://datatracker.ietf.org/doc/html/rfc9207)
- [RFC 7636 — Proof Key for Code Exchange](https://datatracker.ietf.org/doc/html/rfc7636)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OAuth 2.0](oauth-2.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: SAML →](saml.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
