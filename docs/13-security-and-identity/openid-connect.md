# OpenID Connect

OpenID Connect 1.0 je federated identity a authentication vrstva postavená nad OAuth 2.0. Umožňuje clientovi overiť, že End-User bol autentizovaný OpenID Providerom, a získať štandardizované identity claims. Hlavným identity artifactom je ID Token; access token zostáva určený pre resource server.

## 1. Mentálny model

```text
End-User
→ Relying Party spustí OpenID Connect request
→ OpenID Provider autentizuje používateľa
→ authorization code
→ token endpoint
→ ID Token + access token + voliteľne refresh token
→ Relying Party validuje ID Token
→ vytvorí vlastnú application session
```

OpenID Connect rieši otázku:

```text
Ktorý issuer autentizoval ktorého subjecta pre ktorého clienta a v akom kontexte?
```

## 2. Role

### End-User

Používateľ, ktorého identitu a authentication event OpenID Provider potvrdzuje.

### Relying Party

OAuth client používajúci OpenID Connect na authentication používateľa.

Relying Party sa často označuje ako OIDC client.

### OpenID Provider

Authorization server podporujúci OpenID Connect a vydávajúci ID Tokens.

### UserInfo endpoint

Protected resource, z ktorého môže client s access tokenom získať ďalšie user claims.

## 3. OAuth oproti OpenID Connect

### OAuth 2.0

Primárny cieľ:

- delegovaný alebo workload access k API.

Hlavný artifact:

- access token.

### OpenID Connect

Primárny cieľ:

- authentication a interoperabilná identity federation.

Hlavný artifact:

- ID Token.

```text
OAuth access token
→ čo môže client vykonať voči resource serveru

OIDC ID Token
→ koho OpenID Provider autentizoval pre konkrétneho clienta
```

Access token sa nemá používať ako náhrada ID Token-u pre client login.

## 4. Scope `openid`

OIDC request musí obsahovať scope:

```text
openid
```

Bez neho ide o OAuth request, nie OpenID Connect authentication request.

Ďalšie štandardné scopes:

- `profile`,
- `email`,
- `address`,
- `phone`,
- `offline_access`.

Scope vyjadruje requested claim categories alebo refresh semantics; konkrétne claims stále závisia od policy a consentu providera.

## 5. ID Token

ID Token je signed JWT obsahujúci claims o authentication evente a subjecte.

Minimálne relevantné claims:

- `iss` — issuer,
- `sub` — subject identifier,
- `aud` — client audience,
- `exp` — expiration,
- `iat` — issued at.

Ďalšie možné claims:

- `auth_time`,
- `nonce`,
- `acr`,
- `amr`,
- `azp`,
- `at_hash`,
- `c_hash`,
- user profile claims.

ID Token nie je API authorization token.

## 6. Subject identifier

`sub` je lokálne unikátny a stabilný identifier používateľa u konkrétneho issuera.

Správna identity key je typicky:

```text
issuer + subject
```

Nie:

- email,
- display name,
- username bez issuer contextu.

Email môže byť:

- zmenený,
- recyklovaný,
- neoverený,
- zdieľaný,
- odlišný medzi tenants.

## 7. Public a pairwise subject

### Public subject

Rovnaký `sub` pre všetkých clients v danom issuer scope-e.

### Pairwise subject

Odlišný `sub` pre rôzne sectors alebo clients.

Výhoda pairwise identifiers:

- znižujú možnosť korelovať používateľa medzi nesúvisiacimi aplikáciami.

Nevýhoda:

- zložitejšie account linking a migration.

## 8. Authorization Code flow

Odporúčaný OIDC browser flow:

```text
Relying Party
→ authorization request s response_type=code
→ OpenID Provider autentizuje používateľa
→ authorization code
→ token endpoint + PKCE/client authentication
→ ID Token + access token
```

Výhody:

- tokens nejdú priamo cez browser URL,
- code je jednorazový a krátkodobý,
- PKCE chráni code exchange,
- confidential client môže použiť silnú client authentication.

## 9. Authorization request

Dôležité parameters:

- `scope=openid`,
- `response_type=code`,
- `client_id`,
- `redirect_uri`,
- `state`,
- `nonce`,
- PKCE `code_challenge`,
- voliteľne `prompt`, `max_age`, `login_hint`, `acr_values`.

Client musí uchovať transaction state bezpečne a jednorazovo ho validovať pri callbacku.

## 10. Nonce

`nonce` viaže ID Token na konkrétny authentication request a pomáha chrániť pred replay a token injection.

Flow:

```text
client vytvorí náhodný nonce
→ odošle ho v authorization requeste
→ provider ho vloží do ID Token-u
→ client overí exact match
```

Nonce musí byť:

- náhodný,
- transaction-specific,
- session-bound,
- jednorazový,
- validovaný pred vytvorením session.

Nonce nenahrádza `state` ani PKCE; každý rieši inú boundary.

## 11. State, nonce a PKCE

```text
state
→ viaže authorization response na client transaction a pomáha proti CSRF

nonce
→ viaže ID Token na authentication request

PKCE
→ viaže authorization code exchange na client instance
```

Bezpečný flow typicky používa všetky tri podľa client modelu.

## 12. ID Token validation

Relying Party musí validovať minimálne:

1. token je syntakticky validný JWT,
2. signature používa povolený algorithm,
3. signing key pochádza z dôveryhodného issuera,
4. `iss` presne zodpovedá nakonfigurovanému issueru,
5. `aud` obsahuje client ID,
6. `azp` sa validuje, keď je relevantné,
7. `exp` ešte neuplynulo,
8. `iat` a ďalšie časové claims sú rozumné,
9. `nonce` zodpovedá pôvodnej transakcii,
10. `auth_time`, `acr`, `amr` spĺňajú požadovaný assurance context,
11. hash claims sa validujú podľa použitého flowu.

Samotné base64 decode nie je validácia.

## 13. Issuer validation

Issuer je trust anchor OIDC relationshipu.

Client musí:

- poznať očakávaný issuer,
- porovnať exact issuer URL,
- nepoužívať issuer odvodený z neovereného request parametra,
- zabrániť mix-up attacku,
- oddeliť tenants/environments.

Token z development issuera nemá byť prijatý v production iba preto, že signature key vyzerá dôveryhodne.

## 14. Audience a authorized party

`aud` určuje, pre ktorý client je ID Token vydaný.

Ak obsahuje viac audiences, `azp` môže identifikovať authorized party.

Client musí odmietnuť ID Token:

- bez svojho client ID v `aud`,
- s neočakávaným `azp`,
- určený pre inú aplikáciu.

ID Token ukradnutý z iného clienta sa nesmie dať použiť na login.

## 15. Signature, JWKS a key rotation

Provider publikuje public signing keys cez JWKS URI.

Client potrebuje:

- algorithm allowlist,
- `kid` lookup,
- JWKS cache,
- bezpečný refresh pri unknown key,
- overlap počas rotation,
- ochranu proti untrusted JWKS URL,
- emergency key revocation model.

Chyby:

- akceptovanie `none`,
- algorithm confusion,
- použitie token-provided key URL bez trust policy,
- nekonečné JWKS refresh loops,
- stará cache po rotácii.

## 16. Discovery

OpenID Provider Configuration je typicky dostupná cez well-known endpoint.

Metadata môže obsahovať:

- issuer,
- authorization endpoint,
- token endpoint,
- UserInfo endpoint,
- JWKS URI,
- supported scopes,
- response types,
- subject types,
- signing algorithms,
- logout capabilities.

Client musí validovať, že metadata issuer zodpovedá očakávanej hodnote.

Discovery znižuje configuration drift, ale neodstraňuje potrebu trust bootstrap-u.

## 17. UserInfo endpoint

UserInfo je OAuth-protected endpoint, ktorý vracia claims o subjecte.

Client:

- používa access token,
- validuje TLS a issuer relationship,
- overí, že `sub` v UserInfo response zodpovedá `sub` z ID Token-u,
- minimalizuje requested claims,
- chráni response ako osobné údaje.

UserInfo response nemá meniť authenticated subject identity bez validácie.

## 18. Standard claims

Bežné claims:

- `name`,
- `given_name`,
- `family_name`,
- `preferred_username`,
- `email`,
- `email_verified`,
- `locale`,
- `zoneinfo`,
- `phone_number`.

Claims sú assertions od issuera, nie automaticky autoritatívne business údaje.

Príklady:

- `email_verified=true` neznamená, že email patrí zamestnancovi,
- group claim môže byť stale alebo truncated,
- role claim môže mať iný význam medzi aplikáciami.

## 19. Claims mapping

Application musí mať explicitný mapping:

```text
issuer claim
→ normalization
→ internal identity attribute
→ authorization policy
```

Kontroluj:

- source claim,
- type,
- required/optional,
- multi-value semantics,
- case sensitivity,
- missing claim behavior,
- tenant boundary,
- maximum size,
- trust level.

Dynamický claim nemá automaticky vytvárať privileged role.

## 20. Authentication Context Class Reference

`acr` vyjadruje authentication context class podľa dohody ekosystému.

Môže reprezentovať:

- assurance level,
- policy class,
- phishing-resistant authentication,
- step-up requirement.

Client nesmie interpretovať ľubovoľnú `acr` hodnotu bez contractu s providerom.

## 21. Authentication Methods References

`amr` opisuje použité authentication methods.

Príklady môžu reprezentovať:

- password,
- OTP,
- hardware key,
- biometric,
- federated authentication.

`amr` je informatívne podľa provider contractu. Authorization rozhodnutie má vychádzať z definovanej assurance policy, nie z náhodnej string hodnoty.

## 22. Authentication time a max age

`auth_time` uvádza čas aktívnej authentication.

`max_age` umožňuje clientovi požadovať čerstvú authentication.

Použitie:

- citlivá operácia,
- step-up,
- zmena security settings,
- financial action.

Existing SSO session nemusí spĺňať požadovanú freshness alebo assurance.

## 23. Prompt

`prompt` ovplyvňuje interaction behavior.

Príklady:

- `none` — bez user interaction,
- `login` — požadovať reauthentication,
- `consent` — požadovať consent,
- `select_account` — account selection.

`prompt=none` failure je normálny protocol outcome, ak neexistuje vhodná session alebo consent.

## 24. Session model

OIDC authentication vytvorí identity evidence; application si typicky vytvorí vlastnú session.

Application session musí mať:

- secure, HttpOnly a SameSite cookies podľa flowu,
- session fixation protection,
- idle a absolute timeout,
- reauthentication/step-up policy,
- server-side revocation alebo bounded lifetime,
- CSRF protection,
- logout semantics.

ID Token nemá byť automaticky používaný ako browser session cookie.

## 25. Logout

Logout môže znamenať viac vecí:

- ukončenie local application session,
- revocation refresh tokenu,
- ukončenie provider session,
- front-channel/back-channel notification ďalším clients,
- device-wide alebo account-wide logout.

Client musí presne definovať požadovaný scope logoutu.

Local logout bez provider logoutu umožní okamžitý SSO návrat. Provider logout môže ovplyvniť ďalšie aplikácie.

## 26. Front-channel a back-channel logout

### Front-channel

Browser komunikuje s logout endpoints ďalších clients.

Riziká:

- browser restrictions,
- third-party cookie policy,
- unreliable delivery,
- UI dependency.

### Back-channel

Provider posiela signed logout token priamo client backendu.

Výhody:

- nezávislosť od browseru,
- server-to-server delivery.

Client musí validovať logout token, issuer, audience, events claim a session/subject binding.

## 27. Refresh token a offline access

`offline_access` môže signalizovať požiadavku na refresh token pre access bez aktívnej user session.

Provider stále rozhoduje podľa:

- client type,
- consent/policy,
- risk,
- requested scopes,
- session assurance.

Refresh token patrí do OAuth credential lifecycle-u a vyžaduje rotation, revocation a secure storage.

## 28. Pairwise federation a account linking

Pri viacerých issueroch môže rovnaký človek mať viac identities.

Account linking musí byť explicitný a bezpečný.

Nebezpečný pattern:

```text
rovnaký email → automaticky zlúčiť účty
```

Bezpečnejšie možnosti:

- authenticated linking oboch identities,
- administratívne schválenie,
- autoritatívny enterprise identifier,
- audit a unlink recovery.

## 29. Multi-tenant OIDC

Definuj:

- issuer per tenant alebo shared issuer,
- tenant discovery,
- allowed issuer list,
- client registration boundary,
- subject uniqueness,
- claims mapping,
- admin consent,
- logout scope.

Používateľ-controlled tenant parameter nesmie viesť na ľubovoľný issuer bez trust policy.

## 30. Native a browser clients

### Native application

- system browser,
- Authorization Code + PKCE,
- public-client model,
- platform-approved redirect URI,
- secure token storage podľa OS možností.

### Browser SPA

- Authorization Code + PKCE,
- minimálna token lifetime,
- XSS threat model,
- zváženie Backend for Frontend,
- secure transaction state.

OIDC neznižuje browser security requirements.

## 31. Workload a service identity

OIDC sa používa aj pri workload identity federation.

Workload môže získať signed identity token od platform issuera a použiť ho voči trustujúcej službe alebo token exchange endpointu.

Controls:

- issuer/audience restriction,
- krátka lifetime,
- workload-specific subject,
- podmienky na repository, branch, service account alebo environment,
- replay protection,
- no static cloud credentials.

User OIDC login a workload OIDC federation používajú podobný token model, ale odlišný identity lifecycle a threat model.

## 32. ID Token oproti access tokenu

| Vlastnosť | ID Token | Access token |
|---|---|---|
| Audience | OIDC client | resource server |
| Účel | authentication assertion | API authorization |
| Konzument | Relying Party | API |
| Claims | issuer, subject, auth context | scope/permissions/resource context |
| Posielať API | nie | áno |
| Použiť na login | áno po validácii | nie ako štandardný login artifact |

Resource server nemá akceptovať ID Token ako access token.

## 33. ID Token encryption

ID Token môže byť podpísaný a voliteľne šifrovaný.

Signing poskytuje:

- integrity,
- issuer authenticity.

Encryption pridáva:

- confidentiality claims voči intermediaries alebo client front channelu.

Encryption:

- nenahrádza TLS,
- komplikuje key management,
- vyžaduje správny recipient key lifecycle,
- nie je potrebná pri každom use case-e.

## 34. Privacy

OIDC prenáša identity data a vyžaduje privacy design.

Controls:

- minimal scopes/claims,
- pairwise subjects,
- consent/transparency,
- retention,
- data residency,
- purpose limitation,
- no sensitive claims v browser logs/URLs,
- audit accessu k claims,
- account deletion/unlink lifecycle.

ID Token môže byť čitateľný clientom a ďalšími držiteľmi, aj keď je podpísaný.

## 35. Threats a mitigations

### Token replay

- nonce,
- short lifetime,
- secure storage,
- sender constraint pre access tokens.

### Mix-up attack

- exact issuer validation,
- authorization response issuer binding,
- trusted discovery.

### Login CSRF

- `state`,
- transaction-bound session,
- PKCE,
- issuer validation.

### ID Token injection

- signature, audience, issuer, nonce a time validation.

### Key confusion

- algorithm allowlist,
- trusted JWKS URI,
- no token-controlled key fetch.

### Account linking takeover

- neprepájať iba podľa emailu,
- vyžadovať authenticated proof oboch identities.

### Claim escalation

- claim allowlist a normalization,
- privileged role mapping iba z dôveryhodného authoritative source-u.

## 36. Troubleshooting login flow

```text
správny issuer a discovery?
→ client registration a redirect URI?
→ scope obsahuje openid?
→ state/nonce/PKCE uložené?
→ authentication/consent?
→ code exchange?
→ client authentication?
→ ID Token signature a JWKS?
→ iss/aud/azp/exp/nonce?
→ claims mapping?
→ application session creation?
→ authorization po login-e?
```

## 37. Typické chyby

### `invalid_client`

Over client ID, authentication method, secret/key rotation a token endpoint audience.

### `invalid_grant`

Over code expiry/reuse, redirect URI, PKCE, refresh rotation a client binding.

### Signature validation failure

Over issuer, `kid`, JWKS cache, algorithm allowlist a clock.

### Audience mismatch

Token bol vydaný pre iného clienta alebo environment.

### Nonce mismatch

Možný replay, zamenená transaction, session loss alebo parallel-login bug.

### Login funguje, ale role chýba

Authentication uspela; over claims mapping, group/role source, token size, stale directory data a application authorization.

### Redirect loop

Over session cookie, proxy scheme/host headers, redirect URI, SameSite, clock a provider session.

## 38. Observability a audit

Sleduj:

- login success/failure rate,
- errors podľa clienta/issuera v bounded forme,
- nonce/state/PKCE failures,
- signature/JWKS failures,
- unknown issuer/audience,
- reauthentication a step-up outcomes,
- logout delivery failures,
- claim mapping failures,
- session creation/revocation,
- suspicious account linking.

Neloguj authorization codes, tokens, client secrets ani citlivé claims.

## 39. Incident response

Pri signing-key alebo provider compromise:

1. identifikuj affected issuer a key IDs,
2. zastav dôveru alebo quarantine-ni issuer podľa dopadu,
3. rotate/revoke keys,
4. invaliduj application sessions podľa risku,
5. analyzuj vydané tokens a login audit,
6. obnov trusted discovery/JWKS,
7. testuj issuer/audience/nonce validation,
8. komunikuj account recovery.

Pri client compromise rotate client credentials a revokuj refresh-token/session families.

## 40. Anti-patterny

### Access token používaný ako ID Token

Client nevie štandardne overiť authentication event a audience.

### Email ako primary key

Email sa môže zmeniť alebo recyklovať.

### Decode bez signature validation

Claims sú attacker-controlled.

### Issuer vybraný user inputom

Umožňuje dôveru attacker-controlled provideru.

### Group claim priamo na admin role

Bez authoritative contractu vzniká privilege escalation.

### ID Token poslaný API

Token je určený clientovi, nie resource serveru.

### Logout považovaný za automatickú globálnu revocation

Local session, provider session a tokens majú odlišný lifecycle.

## 41. Kontrolné otázky

1. Čo OpenID Connect pridáva nad OAuth 2.0?
2. Aký je rozdiel medzi Relying Party a OpenID Providerom?
3. Prečo je scope `openid` povinný?
4. Ktoré ID Token claims musí client validovať?
5. Prečo je identity key `issuer + subject`?
6. Aký je rozdiel medzi `state`, `nonce` a PKCE?
7. Ako sa líši ID Token a access token?
8. Na čo slúžia discovery a JWKS?
9. Ako sa používajú `acr`, `amr` a `auth_time`?
10. Prečo nie je bezpečné linkovať účty iba podľa emailu?
11. Ako funguje local, front-channel a back-channel logout?
12. Ako diagnostikuješ login, ktorý skončí `403` v aplikácii?

## Glossary impact

Relevantné pojmy: OpenID Connect, Relying Party, OpenID Provider, End-User, ID Token, `openid` scope, subject identifier, public subject, pairwise subject, nonce, issuer validation, audience validation, authorized party, JWKS, OIDC discovery, UserInfo endpoint, standard claims, claims mapping, ACR, AMR, authentication time, max age, prompt, OIDC session, front-channel logout, back-channel logout, offline access, account linking a workload identity federation.

## Primárne zdroje

- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [OpenID Connect Discovery 1.0](https://openid.net/specs/openid-connect-discovery-1_0.html)
- [OpenID Connect Session Management 1.0](https://openid.net/specs/openid-connect-session-1_0.html)
- [OpenID Connect Front-Channel Logout 1.0](https://openid.net/specs/openid-connect-frontchannel-1_0.html)
- [OpenID Connect Back-Channel Logout 1.0](https://openid.net/specs/openid-connect-backchannel-1_0.html)
- [OAuth 2.0 Security Best Current Practice — RFC 9700](https://www.rfc-editor.org/rfc/rfc9700)
- [JSON Web Token — RFC 7519](https://www.rfc-editor.org/rfc/rfc7519)
- [JSON Web Key — RFC 7517](https://www.rfc-editor.org/rfc/rfc7517)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OAuth 2.0](oauth-2.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: SAML →](saml.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
