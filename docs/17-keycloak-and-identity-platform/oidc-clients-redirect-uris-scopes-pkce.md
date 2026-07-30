# OIDC clients, redirect URIs, scopes a PKCE

Keycloak OIDC client je server-side registration contract medzi realm-om a konkrétnou aplikáciou alebo službou. Registration určuje, ktorý `client_id` môže začať flow, kam sa môže browser vrátiť, ako sa client autentizuje na token endpoint-e, ktoré grants a logout paths sú povolené, aké role a claims môže dostať a aké session policies sa použijú. OIDC protokol vysvetľuje všeobecné message semantics; Keycloak client určuje ich konkrétnu prevádzkovú a bezpečnostnú konfiguráciu.

Najčastejší omyl je hodnotiť clienta podľa toho, či login funguje. Broad wildcard redirect, nepovinné PKCE, `Full Scope Allowed`, priveľa default client scopes alebo nesprávny audience mapper môžu vytvoriť protokolovo úspešný login a súčasne umožniť code theft, token substitution alebo privilege projection. Client acceptance preto musí testovať intended redirect aj forbidden redirect, intended role aj unrelated role a prvý login aj revocation.

## 1. Dominantný registration-to-session model

```text
application ownership a protected journey
→ exact realm issuer a OIDC client generation
→ client type, authentication method a enabled grants
→ exact redirect URI a web-origin contract
→ authorization transaction: state, nonce a PKCE
→ Keycloak authentication a consent/policy
→ authorization code via browser redirect
→ token endpoint client/PKCE validation
→ ID/access/refresh token generation
→ client-side issuer/audience/nonce validation
→ local application session
→ resource-server authorization
→ refresh, logout, revocation a second-login validation
```

Registration generation musí byť viazaná na application release. Ak frontend release používa callback `/oauth/callback`, ale Keycloak client stále povoľuje starý broad wildcard, bezpečnostný výsledok je daný širším server-side allowlistom, nie intended route-om v kóde.

## 2. Exact OIDC client subject

Pri incidente veta „client payments-admin“ nestačí. Zachovaj:

```text
Keycloak deployment a realm issuer
+ client internal UUID a clientId
+ client enabled state a protocol
+ client authentication on/off a method
+ enabled grants/flows
+ valid redirect URI set
+ web origin set
+ root/home/admin URL
+ PKCE policy a code-challenge method
+ Full Scope Allowed state
+ default/optional/dedicated client scopes
+ protocol mappers a role scope mappings
+ client secret/key generation
+ session/logout configuration
+ Admin event revision a effective loaded state
```

Dva clients s rovnakým `clientId` v rôznych realms sú odlišné subjects. Delete a recreate v rovnakom realm-e môže zachovať `clientId`, ale zmeniť internal UUID, secret, scope links a sessions.

## 3. Public a confidential execution boundary

Public client nedokáže bezpečne držať long-term client secret v browseri, mobile alebo desktop distribution-e. Confidential client má trusted backend capable of protecting client credentials alebo private keys. Keycloak Admin Console dnes tento rozdiel vyjadruje najmä cez client authentication a capability settings, ale underlying trust model zostáva rovnaký.

```text
public browser/native client
→ žiadny deploy-time secret ako authentication proof
→ Authorization Code + PKCE
→ exact redirect a browser transaction controls

confidential web/backend client
→ server-side code exchange
→ client secret, private-key JWT alebo iný approved client authentication
→ secret/key rotation a least privilege
```

Client secret vložený do JavaScript bundle-u nemení public client na confidential. Je to iba zverejnený string. Naopak confidential client bez PKCE nie je automaticky bezpečný proti authorization-code injection alebo mix-up; PKCE a transaction binding môžu byť užitočné aj tam.

Bearer-only a service-account/M2M modely majú odlišné chapters. Tento blok sa sústreďuje na redirect-based login clienta.

## 4. Redirect URI ako authorization-code destination

Authorization endpoint posiela code na `redirect_uri`, ktorú client uviedol a Keycloak porovnal s registration allowlistom. Redirect URI preto nie je convenience navigation. Je to destination credential-delivery boundary.

Secure registration používa čo najpresnejšie hodnoty:

```text
https://payments-admin.atlas.example/oauth/callback
```

Broad pattern:

```text
https://*.atlas.example/*
```

dovoľuje každý matching host a path. Ak organizácia umožní teams vytvárať preview subdomains, compromise alebo takeover jedného hosta môže vytvoriť legitímny callback pre production clienta.

Wildcard nie je vždy technicky zakázaný, ale jeho risk sa odvíja od toho, kto môže ovládať matching origins, DNS, hosting a routes. Production privileged client má typicky exact redirect inventory per environment. Development localhost alebo native loopback exceptions sa oddeľujú od production client registration.

## 5. Root URL, Home URL, Admin URL a Valid Redirect URIs

Tieto polia majú odlišnú semantics. Root URL môže slúžiť ako base pre relative URLs. Home URL je default application landing page. Admin URL sa môže používať pre server-to-client callbacks alebo logout/admin operations podľa adaptera a configuration. Valid Redirect URIs sú security allowlist pre authorization response destinations.

Nastavenie peknej Home URL neopraví broad redirect allowlist. Root URL placeholder môže zjednodušiť environment configuration, ale ak je base mutable alebo nesprávne odvodená, môže rozšíriť effective redirect set. Review má rozbaliť relative values na final absolute URIs.

## 6. Web Origins a CORS nie sú redirect allowlist

Web Origins určujú, z ktorých browser origins môžu JavaScript clients volať Keycloak endpoints cez CORS. Redirect URI určuje, kam sa browser vráti s authorization response. Rovnaký host môže byť v oboch zoznamoch, ale controls chránia odlišné paths.

```text
Valid Redirect URI
→ destination authorization response-u

Web Origin
→ browser origin povolený CORS response headerom
```

`Web Origins = +` alebo broad wildcard môže odvodzovať origins z redirectov alebo povoliť priveľa browser contexts podľa Keycloak semantics. CORS permission nevytvára OAuth authorization, ale môže uľahčiť čítanie responses z neautorizovaného originu. Obe inventories musia byť explicitné a testované.

## 7. Authorization Code + PKCE v Keycloak clientovi

PKCE viaže authorization code na client instance, ktorá vytvorila random `code_verifier`. Client pošle hash verifiera ako `code_challenge` v authorization requeste. Token endpoint pri code exchange overí, že predložený verifier zodpovedá challenge.

```text
client vytvorí random verifier
→ challenge = BASE64URL(SHA256(verifier))
→ authorization request nesie challenge + method S256
→ Keycloak uloží challenge k code transaction
→ browser dostane code
→ token request nesie verifier
→ Keycloak prepočíta challenge
→ iba matching client instance získa tokens
```

`plain` challenge method neposkytuje rovnakú ochranu pri observation authorization requestu. Production policy má vyžadovať `S256`. Ak PKCE nie je server-side required, attacker môže začať transaction bez challenge a využiť najslabší povolený path.

PKCE nenahrádza `state`, `nonce` ani redirect validation:

- **state** — viaže callback na client/browser transaction a chráni proti login CSRF;
- **nonce** — viaže ID Token na OIDC authentication request;
- **PKCE** — viaže code exchange na verifier-owning client instance;
- **redirect validation** — obmedzuje destination code-u.

Všetky štyri controls riešia inú substitúciu.

## 8. Client policies a enforced security profile

Keycloak Client Policies umožňujú uplatniť security profiles a validation na client configuration a protocol requests. Platform môže napríklad vyžadovať PKCE, obmedziť algorithms, client authentication alebo redirect patterns pre určitú client cohortu.

Policy musí mať exact scope. „Máme PKCE policy“ nepreukazuje, že matchuje production client. Potrebný je inventory:

```text
expected clients
→ policy selector/profile
→ actual matched client generations
→ successful compliant flow
→ rejected no-PKCE alebo weak-method flow
```

No-match je rovnaký failure mode ako pri platform guardrails. Manual client vytvorený mimo intended policy cohortu môže zostať slabší.

## 9. Client scopes: default, optional a dedicated

Client scope je reusable Keycloak object s protocol mappers a role scope mappings. Client môže mať default scopes aplikované automaticky a optional scopes aktivované requestom. Každý client má aj dedicated scope pre client-specific mappers a scope configuration.

```text
realm-level client scope
→ reusable claims/mappers/role-scope policy

default link
→ scope sa aplikuje bez explicitného requestu

optional link
→ scope sa môže aktivovať requested scope hodnotou

dedicated scope
→ configuration špecifická pre jedného clienta
```

Default scope má broad blast radius. Zmena mappera môže ovplyvniť mnoho clients a budúce tokens. Optional scope nie je automaticky „user consent“. Server stále rozhoduje, či client scope smie requestnuť, či je consent required a ktoré mappers sa vykonajú.

## 10. Protocol mappers a claim authority

Protocol mapper prekladá user, group, role, session alebo custom data do token claims. Mapper nie je iba formatting. Rozhoduje, ktorá source attribute sa stane externally consumed assertion, pod akým claim name, type a token placement.

Mapper contract obsahuje:

```text
source authority
+ source attribute/role semantics
+ mapper generation
+ claim name a type
+ token types: ID/access/UserInfo
+ cardinality a size
+ client eligibility
+ downstream consumer contract
```

Group path vložená do access tokenu môže prezradiť organization structure. Realm role mapper môže publikovať unrelated admin role. Hardcoded claim môže zastarať. Script/custom mapper môže zvýšiť latency alebo vytvoriť nondeterministic output. Claims sa majú minimalizovať podľa actual consumer need.

## 11. Full Scope Allowed a role scope mappings

User effective roles môžu byť širšie než role set potrebný konkrétnym clientom. Role scope mappings určujú, ktoré roles smie client dostať. Pri `Full Scope Allowed` je effective scope broad a client typicky dostáva všetky user role mappings podľa mapper behavioru.

Least-privilege token model je:

```text
user effective role set
∩ client role scope
∩ linked client-scope role scope
→ token-eligible roles
→ mapper projection
```

Pre `payments-admin-web` má token obsahovať iba payments-admin client roles a nevyhnutné realm roles. Partner, HR alebo unrelated platform roles nemajú byť publikované iba preto, že user ich má.

Vypnutie `Full Scope Allowed` bez explicitných mappings môže odstrániť potrebné audience alebo roles a rozbiť login/API calls. Zmena sa preto testuje token diffom a business journey, nie iba Admin Console save-om.

## 12. OAuth scope parameter a Keycloak client scope

Authorization request môže niesť `scope=openid profile payments.approve`. `openid` aktivuje OIDC semantics. Ostatné names môžu odkazovať na Keycloak client scopes alebo application authorization vocabulary podľa designu. Requested scope neznamená, že client automaticky dostane všetko; Keycloak vyhodnotí linked scopes, consent a policy.

Scope claim v access tokene opisuje granted scope strings. Roles môžu byť v `realm_access` alebo `resource_access`. Audience je samostatný claim. Resource server nemá zamieňať existence role, scope a audience.

```text
audience
→ pre ktorý resource/token consumer je token určený

scope
→ aký delegated access bol granted

role
→ identity/application permission mapping

local policy
→ či principal môže vykonať action nad konkrétnym resource
```

## 13. Audience a token consumer

Token pre client login nemusí byť automaticky vhodný pre každé API. Resource server validuje expected issuer, signature, expiry a audience. Audience mapper alebo client-role relation môže pridať API audience. Broad audience ako `atlas-internal` vytvára token použiteľný naprieč viacerými services a zvyšuje confused-deputy risk.

Client scope review má preto ukázať final access token pre každý protected API, nie iba ID Token pre UI.

## 14. Session a logout configuration

OIDC client môže používať front-channel alebo back-channel logout mechanizmy a post-logout redirect allowlist. Keycloak user/client session, refresh token, access token a application session majú samostatné lifecycles.

Backchannel logout doručuje clientovi server-to-server logout token alebo notification podľa supported contractu. Frontchannel závisí od browsera a iframe/navigation behavioru. Ani jeden automaticky nezruší access token na resource serveri, ak ten používa offline signature validation bez current revocation signal-u.

Post-logout redirect URI je ďalší redirect allowlist. Broad value môže po logout-e presmerovať usera na attacker-controlled page. Logout acceptance musí testovať local cookie aj protected API, nie iba návrat na login page.

## 15. Connected incident `KC-PAY-65` — OIDC path

Client `payments-admin-web` mal:

```text
client authentication: off
standard flow: on
Valid Redirect URIs: https://*.atlas.example/*
Web Origins: +
PKCE enforcement: none
Full Scope Allowed: on
```

Contractor mal inherited realm role `settlement-admin`. Útočník ovládol preview host `preview.atlas.example`. Vytvoril authorization request s production `client_id` a redirectom na svoj callback. Victim browser už mal Keycloak SSO session, takže login prebehol bez nového credential promptu. Keycloak poslal code na povolený wildcard redirect.

Keďže request nemal PKCE challenge a server ju nevyžadoval, attacker vymenil code na token endpoint-e. Access token obsahoval inherited realm role. API validovalo issuer, signature a expiry, ale nevyžadovalo resource-specific audience ani current JIT approval.

Incident response použil sign-out, no už vydaný access token zostal použiteľný do expiry. Root cause chain:

```text
broad redirect
+ missing required PKCE
+ inherited broad realm role
+ Full Scope Allowed
+ weak API authorization
+ incomplete token revocation
```

## 16. OIDC redesign

Redesign vytvorí exact client contract:

```text
clientId: payments-admin-web
realm issuer: https://id.atlas.example/realms/atlas-payments-prod
type: public browser client
redirects:
  - https://payments-admin.atlas.example/oauth/callback
web origins:
  - https://payments-admin.atlas.example
PKCE: required S256
Full Scope Allowed: off
role scope:
  - payments-admin:settlement-read
  - payments-admin:settlement-approve
default scopes:
  - openid/profile baseline podľa need
optional scopes:
  - explicit business capabilities
```

Client policy odmietne no-PKCE request a broad production redirect. API vyžaduje own audience, action scope alebo client role, tenant a object/workflow check. Incident playbook revokuje Keycloak sessions, refresh descendants, relevant token issuance interval a local application sessions.

## 17. Acceptance matrix

Pozitívne tests:

- exact production redirect dostane code;
- PKCE `S256` exchange prejde raz;
- intended user dostane iba expected roles/scopes/audience;
- local session a protected API fungujú;
- refresh a logout behavior zodpovedajú contractu.

Negatívne tests:

- sibling preview subdomain je odmietnutá;
- missing PKCE a `plain` method sú odmietnuté;
- code s wrong verifierom alebo second exchange zlyhá;
- wrong client, wrong realm a wrong audience sú odmietnuté;
- unrelated realm role sa v tokene nenachádza;
- old token alebo cookie po incident revocation nedokáže privileged operation.

## 18. Troubleshooting flow

Pri `invalid_redirect_uri` porovnaj actual authorization request s final resolved allowlistom. Skontroluj scheme, host, port, path, trailing slash, encoding a environment. Nepridávaj `*` iba na odstránenie chyby.

Pri `invalid_grant` na token endpoint-e zachovaj code transaction ID, client, redirect URI, PKCE method, verifier hash, code use/expiry a node logs. Hypotézy sú expired code, reused code, wrong verifier, wrong redirect, wrong client alebo lost transaction/session state.

Pri missing role/claim sleduj:

```text
user effective roles
→ Full Scope Allowed
→ client/linked-scope role mappings
→ mapper execution
→ requested/default/optional scopes
→ actual token claims
→ API mapping
```

Pri logout probléme oddeľ Keycloak session, refresh token, access token a local cookie. Login page po logout-e nie je dôkaz, že API odmietne old bearer token.

## 19. Anti-patterny

### Wildcard pre rýchle preview environments

Preview fleet zväčšuje redirect trust domain na každý matching host. Production client má mať oddelenú exact registration alebo brokered onboarding.

### Secret v SPA

Client secret publikovaný v browser bundle-i nie je authentication secret. Public client potrebuje PKCE a exact redirects.

### Full Scope Allowed ako default

Convenience publikuje role graph, ktorý client nepotrebuje. Token size, privacy a privilege blast radius rastú.

### Mapper ako business policy

Mapper vloží claim; nerozhoduje, či konkrétna settlement operation je povolená. Resource server musí vykonať local authorization.

### Logout page ako revocation test

Browser redirect neoveruje access token ani application session invalidation.

## 20. Kontrolné otázky

1. Čo tvorí exact OIDC client generation?
2. Prečo redirect URI je credential-delivery boundary?
3. Aký je rozdiel medzi Valid Redirect URIs a Web Origins?
4. Prečo secret v SPA nevytvára confidential clienta?
5. Čo viaže `state`, `nonce` a PKCE?
6. Prečo má byť PKCE server-side required?
7. Ako sa líši default, optional a dedicated client scope?
8. Čo robí protocol mapper a prečo je authority-sensitive?
9. Ako `Full Scope Allowed` ovplyvňuje role projection?
10. Aký je rozdiel medzi audience, scope a role?
11. Prečo access token môže prežiť Keycloak logout?
12. Ktoré negative tests by odhalili `KC-PAY-65`?

## Glossary impact

Relevantné pojmy: OIDC client generation, public client, confidential client, valid redirect URI, web origin, PKCE enforcement, `S256`, client policy, default client scope, optional client scope, dedicated client scope, protocol mapper, role scope mapping, Full Scope Allowed, token audience, post-logout redirect, OIDC client acceptance matrix.

## Primárne zdroje

- [Keycloak — Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak — Securing applications and services with OpenID Connect](https://www.keycloak.org/securing-apps/oidc-layers)
- [OpenID Connect Core 1.0 incorporating errata set 2](https://openid.net/specs/openid-connect-core-1_0.html)
- [OAuth 2.0 Security Best Current Practice — RFC 9700](https://www.rfc-editor.org/rfc/rfc9700)
- [OAuth 2.0 for Native Apps — RFC 8252](https://www.rfc-editor.org/rfc/rfc8252)
- [PKCE — RFC 7636](https://www.rfc-editor.org/rfc/rfc7636)
