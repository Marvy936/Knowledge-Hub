# OAuth 2.0

OAuth 2.0 je authorization framework, ktorým client získa obmedzený access k protected resource-u bez toho, aby resource owner odovzdal clientovi svoj primary credential. Authorization Server sprostredkuje grant, vydá access token s obmedzeným scope-om a audience a Resource Server token validuje pri každej API operation.

OAuth nie je samostatný login protocol. Access token je credential pre API, nie štandardný dôkaz, že client autentizoval konkrétneho usera. Ak application potrebuje login a identity claims, používa OpenID Connect.

```text
resource owner alebo workload
→ client požiada Authorization Server o delegovaný access
→ Authorization Server autentizuje relevantných actors a vyhodnotí policy
→ vydá authorization code alebo iný grant artifact
→ client získa access token
→ Resource Server overí token, audience, scope a local resource policy
→ token expiry, refresh, revocation a audit uzatvárajú lifecycle
```

## 1. Problém delegovaného accessu

Bez OAuth by third-party application často potrebovala user password k cieľovej službe. Tým by získala všetky privileges usera, mohla by credential ukladať a používateľ by nevedel odobrať iba jednej application access bez zmeny hesla všade.

OAuth oddeľuje actors a capabilities:

- client dostane token namiesto primary credentialu;
- token môže mať obmedzený scope, resource a lifetime;
- authorization možno revoke-nuť per client/grant;
- Resource Server môže auditovať clienta aj subject;
- Authorization Server centralizuje consent, policy a credential lifecycle.

Delegation však stále vytvára trust. Malicious client môže zneužiť legitimate token v rámci granted scope-u. OAuth preto potrebuje least privilege, client governance a resource-level authorization.

## 2. Štyri základné role

**Resource Owner** je actor oprávnený rozhodnúť o access-e k resource-u. Pri user-facing flowe je to často End-User; pri machine flowe môže authorization vyplývať z administrative policy.

**Client** je application žiadajúca access. Client nevlastní protected resource a používa access token voči Resource Serveru.

**Authorization Server — AS** autentizuje clienta a podľa grant type-u aj resource ownera, vyhodnotí authorization policy a vydáva tokens.

**Resource Server — RS** hostuje protected API. Overuje token a rozhoduje, či request smie vykonať konkrétnu action na konkrétnom resource-e.

Roly môžu byť implementované rovnakým produktom, ale security responsibilities ostávajú oddelené.

## 3. Authorization Server nie je Resource Server

Authorization Server rozhoduje o vydaní tokenu a jeho broad capabilities. Resource Server pozná actual business objects, tenant ownership, transaction state a operation impact.

```text
AS:
  client X môže dostať scope orders.read pre Orders API

RS:
  subject môže čítať iba orders svojho tenant-a
  a iba records, na ktoré má local permission
```

Scope preto nie je kompletná business authorization. Resource Server musí vykonať object/tenant/action checks aj pri validnom token-e.

## 4. Authorization grant

Authorization grant je credential alebo protocol result reprezentujúci authorization udelenú resource ownerom alebo policy. Client ho vymení za access token.

Najčastejšie grant types:

- Authorization Code — user-interactive browser flow;
- Client Credentials — client/workload koná vo vlastnom mene;
- Device Authorization — zariadenie bez vhodného browser/inputu;
- Refresh Token — pokračovanie už udeleného grant lifecycle-u;
- Token Exchange — výmena identity/delegation contextu pre downstream resource.

Grant type určuje actors, authentication a threat model. Nie je to iba parameter, ktorý možno ľubovoľne zameniť.

## 5. Authorization Code flow

Authorization Code flow oddeľuje browser authorization interaction od token issuance.

```text
1. client vytvorí authorization transaction
2. browser ide na authorization endpoint
3. AS autentizuje usera a vyhodnotí consent/policy
4. AS vráti short-lived one-time code cez redirect
5. client backend/token component vymení code na token endpoint-e
6. AS overí code binding, PKCE a client authentication
7. vydá access token a optional refresh token
```

Browser nevidí access token v authorization response. Code sám nie je API credential a má byť krátkodobý, single-use a viazaný na client, redirect URI a PKCE transaction.

## 6. Authorization request

Client posiela na authorization endpoint typicky:

- `response_type=code`;
- `client_id`;
- exact `redirect_uri`;
- requested `scope`;
- `state`;
- PKCE `code_challenge` a `code_challenge_method=S256`;
- optional `resource` indicators;
- OIDC parameters ako `nonce`, ak ide o OpenID Connect.

Client uloží transaction context: expected issuer, state, PKCE verifier, redirect URI, requested resources/scopes a return destination. Authorization response sa nesmie spracovať bez nájdenia tejto pending transaction.

## 7. Redirect URI ako security boundary

Redirect URI je endpoint, kam AS pošle authorization response. Ak attacker presmeruje code na svoj endpoint, môže sa pokúsiť grant ukradnúť alebo injectnúť.

RFC 9700 vyžaduje exact string matching registered redirect URI, s úzkou výnimkou variable localhost portu pre native loopback redirects. Wildcards, prefix matching a arbitrary subdomains zväčšujú attack surface.

Client redirect endpoint nesmie byť open redirector. Return URL aplikácie sa uloží server-side alebo allowlistuje; nesmie ovplyvniť OAuth redirect URI validation.

## 8. `state`

`state` viaže callback na client browser transaction a chráni pred CSRF/response injection.

```text
client vygeneruje random state
→ uloží ho spolu s transaction contextom
→ callback musí obsahovať exact value
→ state sa po použití atomicky zneplatní
```

State nemá byť predictable ani iba plaintext destination URL. Pri parallel authorization flows potrebuje každá transaction vlastnú value.

OIDC nonce a PKCE chránia iné edges; state zostáva dôležitý pre client transaction integrity.

## 9. PKCE

Proof Key for Code Exchange — PKCE — chráni authorization code pred interception a injection.

Client vytvorí high-entropy `code_verifier` a pošle jeho SHA-256 transformáciu ako `code_challenge`. Token endpoint vydá token iba ak predložený verifier zodpovedá challenge uloženému pri code-e.

```text
code_challenge = BASE64URL(SHA256(code_verifier))
```

RFC 9700 vyžaduje PKCE pre public clients a Authorization Server ho musí podporovať. Odporúča sa aj confidential clients ako defense in depth a protection proti code injection. Používaj `S256`, nie `plain`, ak nejde o legacy interoperability.

## 10. PKCE downgrade protection

Ak authorization request obsahoval challenge, token request musí obsahovať matching verifier. AS nesmie akceptovať token exchange bez verifiera.

Ak token request pošle verifier, ale original transaction challenge nemala, AS ho nesmie považovať za PKCE-protected. Inak attacker odstráni challenge z front-channel requestu a neskôr obíde kontrolu.

Client má publikované AS metadata použiť na overenie supportu `S256`, ale trustuje iba metadata z expected issuer bootstrapu.

## 11. Authorization code properties

Code má byť:

- random a neuhádnuteľný;
- krátkodobý;
- single-use;
- viazaný na client ID;
- viazaný na exact redirect URI, keď je súčasť requestu;
- viazaný na PKCE challenge;
- viazaný na issuer/authorization transaction;
- nepoužiteľný priamo na Resource Serveri.

Opakovaný token exchange musí zlyhať a môže signalizovať interception alebo retry race. Client nemá pri `invalid_grant` slepo opakovať rovnaký code.

## 12. Token endpoint

Token endpoint je direct client-to-AS channel chránený TLS. Browser ho bežne nevolá za confidential web clienta.

Pri code exchange AS overí:

- grant type a code state;
- client binding;
- redirect URI binding;
- PKCE verifier;
- client authentication, ak je required;
- issuer/tenant context;
- replay a expiry.

Token response obsahuje access token, token type, expiry, granted scope a optional refresh token. Neloguj response body ani request secrets.

## 13. Public a confidential clients

**Confidential client** dokáže chrániť client credentials, napríklad backend service s private keyom alebo secretom v controlled server environment-e.

**Public client** nedokáže spoľahlivo chrániť distributed credential. SPA, mobile app a desktop binary možno inspectovať alebo modifikovať.

Client ID nie je secret. Embedded mobile/SPA client secret nemá authentication value, pretože každý inštalovaný client ho môže extrahovať.

Client type ovplyvňuje token endpoint authentication, PKCE a token storage, nie automaticky trustworthiness business code-u.

## 14. Client authentication

Confidential client sa autentizuje na token/introspection/revocation endpoints podľa registered method.

Metódy môžu zahŕňať:

- HTTP Basic s client secretom;
- POST client secret, ak interoperabilita vyžaduje;
- signed JWT assertion s shared secretom;
- `private_key_jwt`;
- mutual TLS;
- workload identity/federated assertion podľa platform profile-u.

`private_key_jwt` assertion potrebuje issuer/subject client ID, token-endpoint audience, short expiry, unique `jti` a signature trusted registered keyom. Client authentication neznamená resource-owner authorization; iba preukazuje client identity.

## 15. Access token

Access token je credential pre Resource Server. Reprezentuje authorization grant a môže niesť subject, client, audience, scopes a ďalší context.

Token má byť:

- určený presnému resource-u alebo audience;
- obmedzený scopes/actions;
- krátkodobý podľa risku;
- prenášaný iba cez TLS;
- chránený pred URL/log/cache leakage;
- validovaný Resource Serverom;
- podľa potreby sender-constrained.

Client nemá token parsovať ako stabilný business API, ak formát nie je súčasť explicitného contractu. Opaque token je pre clienta iba string.

## 16. Bearer token

Bearer token môže použiť každý, kto ho drží. Resource Server nevie z tokenu samotného odlíšiť legitímneho clienta od thief-a.

Preto bearer model vyžaduje secure storage, TLS, no-logging, short lifetime, audience restriction a minimal scope. Token v URL môže uniknúť cez browser history, referrer, proxy logs a analytics.

Bearer token je jednoduchý a interoperabilný, ale high-value use case môže potrebovať proof-of-possession mechanizmus.

## 17. Scope

Scope je client-visible authorization dimension, často reprezentovaná space-delimited strings ako `orders.read` alebo `payments.create`.

Scope semantics definuje Authorization Server a Resource Server contract. `read` bez resource namespace-u môže byť ambiguous. Scope má predstavovať capabilities, nie internú implementation role bez stability.

Granted scope môže byť užší než requested. Client používa token response, nie original request, ako source granted scope-u.

Scope neoveruje object ownership, transaction limits, tenant ani current business state. Tie zostávajú Resource Server policy.

## 18. Audience a resource indicators

Audience určuje Resource Server, pre ktorý je token určený. Resource indicator parameter podľa RFC 8707 umožňuje clientovi explicitne požiadať token pre konkrétny protected resource.

```text
client potrebuje Orders API a Payments API
→ žiada oddelené audience-restricted tokens
→ compromise Orders tokenu neotvorí Payments API
```

Jeden broad token pre všetky internal APIs vytvára confused-deputy risk a veľký blast radius. Resource Server musí odmietnuť token, ktorý nebol vydaný preň, aj keď issuer a signature sú validné.

## 19. Resource Server validation

Resource Server vykoná dve vrstvy:

1. **Token validation** — token je active, trusted issuer, expected audience, non-expired a správne sender-bound.
2. **Authorization** — scope/claims a local state povoľujú requested action na exact resource-e.

Pre JWT access token typicky overuje signature, `iss`, `aud`, `exp`, `iat`, client/subject claims a profile-specific fields. Pre opaque token používa introspection alebo AS-supported validation.

RS nesmie trustovať identity header od gateway, kým nevie, že direct access je blokovaný a header inbound od clienta odstránený.

## 20. `401` oproti `403`

`401 Unauthorized` v HTTP semantics typicky znamená chýbajúci, invalidný, expired alebo neakceptovateľný authentication credential pre Resource Server. Response môže obsahovať `WWW-Authenticate` s bounded error information.

`403 Forbidden` znamená, že credential môže byť validný, ale current principal/client nemá permission na operation/resource.

```text
invalid audience alebo expired token → 401
valid token, chýba payments.approve → 403
valid scope, ale order patrí inému tenantovi → 403
```

Neodhaľuj sensitive resource existence viac, než application policy dovoľuje.

## 21. Opaque access token

Opaque token nemá clientom interpretovateľný self-contained format. Resource Server ho overí introspection endpointom alebo local authoritative lookupom/cache.

Výhody:

- AS môže centralizovať current active state;
- token claims nie sú viditeľné clientovi;
- revocation môže byť rýchlejšia;
- format sa môže meniť bez client coupling-u.

Nevýhody:

- runtime dependency a latency;
- introspection capacity a outage risk;
- cache staleness;
- shared token lookup infrastructure.

Opaque neznamená „encrypted JWT“ automaticky. Je to contract, že consumer ho neinterpretuje lokálne.

## 22. JWT access token

JWT access token profile podľa RFC 9068 definuje interoperabilnejší signed token pre Resource Servers. Môže obsahovať issuer, subject, audience, expiry, client ID a scopes.

Výhody sú local validation a nižšia per-request dependency na AS. Nevýhody sú revocation latency, JWKS cache, claim exposure a risk nesprávnej validation.

JWT je signed, nie automaticky encrypted. Client alebo holder môže claims čítať. Do tokenu nevkladaj unnecessary sensitive data.

Resource Server má explicitný algorithm/key/issuer/audience allowlist. Base64 decode bez signature a semantic validation je security vulnerability.

## 23. Token introspection

RFC 7662 introspection umožňuje authorized Resource Serveru zistiť, či token je active a získať metadata.

RS musí:

- autentizovať sa voči endpointu;
- chrániť token aj response cez TLS;
- vyhodnotiť `active` a required audience/scope/subject metadata;
- definovať bounded cache TTL;
- rozlíšiť inactive token od endpoint outage-u;
- fail behavior prispôsobiť operation risku;
- monitorovať latency a availability.

Fail-open pri introspection timeout-e môže povoliť revoked alebo attacker token. Fail-closed môže spôsobiť API outage. Local cache a short degraded window musia byť explicitné.

## 24. Access-token lifetime

Krátka lifetime obmedzuje replay window a stale authorization. Príliš krátka lifetime zvyšuje token issuance load a failure coupling.

Lifetime závisí od:

- bearer vs sender-constrained modelu;
- audience a privileges;
- client storage risku;
- Resource Server revocation capability;
- transaction duration;
- offline/background use;
- incident response requirements.

Long-running operation môže autorizovať start tokenom a následne spracovanie dokončiť pod durable job identity, nie držať broad bearer token hodiny.

## 25. Refresh token

Refresh token je credential pre Authorization Server, nie Resource Server. Client ho použije na získanie nového access tokenu bez opakovania full authorization interaction.

Je často hodnotnejší než access token, pretože predlžuje grant a môže vydávať nové tokens. Potrebuje secure storage, client binding, scope/audience controls, expiry, revocation a compromise detection.

Refresh token issuance má zodpovedať client type-u a use case-u. Public/browser clients potrebujú obzvlášť silný model; RFC 9700 vyžaduje pre public clients refresh-token rotation alebo sender-constrained refresh tokens.

## 26. Refresh-token rotation

Pri rotation každý úspešný refresh vráti nový refresh token a starý zneplatní.

```text
RT1 → refresh → AT2 + RT2
RT1 je invalid
RT2 → refresh → AT3 + RT3
```

Server uchová token family a lineage. Ak sa starý token neskôr objaví, legitímny client a attacker pravdepodobne držia kópiu tej istej family.

Rotation znižuje reusable lifetime, ale potrebuje atomicity a retry handling. Client, ktorý stratí response s RT2 a retry-ne RT1, môže spustiť reuse detection; implementation musí mať jasné idempotency/family semantics.

## 27. Refresh-token reuse detection

Pri použití už rotated tokenu AS identifikuje compromise alebo race. Bez spoľahlivého rozlíšenia, kto je attacker, bezpečný response typicky revoke-ne active family/grant a vyžaduje reauthorization.

Audit zachytí client, subject, family identifier, token generation, source/device context a timestamp bez raw tokenu.

Reuse detection nie je useful, ak server udržiava staré refresh tokens validné počas neobmedzeného overlapu.

## 28. Token revocation

RFC 7009 definuje revocation endpoint, kde client požiada o invalidation tokenu. Server môže revoke-nuť token aj related grant podľa policy.

Revocation semantics musia určiť:

- refresh token a family;
- access token behavior;
- distributed JWT propagation;
- introspection/cache invalidation;
- local application sessions;
- downstream exchanged tokens;
- audit a incident workflow.

Self-contained JWT môže zostať cryptographically validný do expiry. Resource Server potrebuje short lifetime, denylist/status/introspection mechanismus alebo acceptable residual window.

## 29. Consent a administrative authorization

Consent je user-facing authorization decision. Má používateľovi zrozumiteľne ukázať clienta, requested capabilities, data a duration.

Scope string `contacts.read` môže byť pre engineer-a jasný, ale UI má vysvetliť praktický access. Consent fatigue a bundled broad scope znižujú meaningful choice.

Enterprise first-party application môže používať administrative authorization bez individual consentu. To nemení potrebu least privilege, audit a revocation.

Consent nie je Resource Server policy. User nemôže consentom obísť organization restriction alebo získať access k cudziemu tenantovi.

## 30. Client registration

Client registration vytvára trust contract:

- client ID a type;
- redirect URIs;
- allowed grant/response types;
- token endpoint authentication method;
- public keys/JWKS;
- allowed scopes/resources;
- tenant/environment owner;
- logout/revocation metadata podľa profile-u;
- lifecycle a secret/key rotation.

Redirect URI ownership a client metadata changes sú high-impact. Dynamic client registration potrebuje initial access policy, software statements alebo approval; arbitrary self-registration nemá automaticky dostať privileged scopes.

## 31. Authorization Server metadata

RFC 8414 metadata publikujú issuer, authorization/token endpoints, JWKS URI, supported grants, PKCE methods, client auth methods a optional introspection/revocation endpoints.

Client začne trusted issuerom a načíta metadata z issuer-derived location. Metadata `issuer` musí exactne sedieť. Arbitrary discovery URL z user inputu nevytvára trust.

Metadata cache potrebuje expiry, last-known-good behavior a monitoring endpoint/key changes.

## 32. Authorization Server key lifecycle

AS používa signing keys pre JWT tokens/metadata assertions a môže používať encryption alebo client-auth verification keys.

Controls:

- oddelený purpose a environment;
- stable `kid` a algorithm allowlist;
- JWKS publication;
- overlap pri rotation;
- bounded Resource Server cache;
- emergency compromise removal;
- HSM/KMS podľa risku;
- audit generation/use/deletion;
- historical verification podľa token lifetime.

Token header nesmie prinútiť RS stiahnuť attacker key alebo akceptovať unexpected algorithm.

## 33. Client Credentials grant

Client Credentials sa používa, keď confidential client/workload koná vo vlastnom mene. Nie je to user delegation.

```text
workload autentizuje client identity na token endpoint-e
→ AS vyhodnotí client/service policy
→ vydá audience/scoped access token
→ RS audit identifikuje client/workload actor-a
```

Shared client secret medzi množstvom instances znižuje attribution. Preferuj workload identity, mTLS alebo private-key client authentication s short-lived credentials.

Grant sa nesmie používať na predstieranie human subjecta bez explicitného impersonation/delegation modelu.

## 34. Device Authorization Grant

RFC 8628 je určený pre devices bez vhodného browsera alebo text inputu, napríklad TV alebo CLI.

```text
device požiada AS o device_code a user_code
→ zobrazí verification URI a user code
→ user otvorí trusted browser na inom zariadení
→ autentizuje sa a schváli client/device
→ device polluje token endpoint s device_code
→ po approval dostane tokens
```

User code je human-friendly a nie dostatočne secret sám osebe. Flow potrebuje short expiry, rate-limited polling, `slow_down` handling, jasné zobrazenie clienta a protection pred phishing/code substitution.

Device nesmie usera presmerovať na attacker verification site. User má vidieť domain/brand dôveryhodného AS.

## 35. Implicit flow

Implicit flow vracia access token priamo v authorization response cez browser. Token môže skončiť vo fragment handlingu, browser history, scripts alebo redirect chain-e a chýba protected code exchange.

RFC 9700 odporúča nepoužívať response types, ktoré vydávajú access token na authorization endpoint-e, pre nové návrhy. Authorization Code + PKCE poskytuje lepšiu ochranu proti leakage, injection a sender-constraining integration.

Existing legacy deployments potrebujú migration plan a strict redirect/fragment handling; nový client nemá implicit zvoliť iba preto, že je „jednoduchší“.

## 36. Resource Owner Password Credentials

ROPC grant necháva client priamo zbierať user password a vymeniť ho za token. Ruší separation medzi clientom a Authorization Serverom.

Dôsledky:

- password sa dostane do ďalšej application boundary;
- client môže credential ukladať alebo phishovať;
- MFA, WebAuthn, federation a adaptive authentication sa nedajú správne vložiť;
- users sa učia zadávať credentials mimo originu AS;
- recovery/consent/session semantics sú nejasné.

RFC 9700 stanovuje, že tento grant sa nesmie používať. Legacy migration má presunúť user authentication na browser/AS flow.

## 37. Browser clients a BFF

SPA je public client a browser origin je vystavený XSS. Authorization Code + PKCE chráni authorization transaction, ale JavaScript-accessible access token môže malicious script ukradnúť.

Backend for Frontend drží OAuth tokens server-side a browseru vydáva application session cookie. BFF proxy volá APIs v mene session.

BFF znižuje token exposure, ale pridáva:

- CSRF protection;
- Secure/HttpOnly/SameSite cookie lifecycle;
- session fixation/revocation;
- backend availability;
- correct API audience/token selection;
- no open generic proxy;
- propagation original actor a audit.

## 38. Native applications

Native app je public client. Používa external system browser a Authorization Code + PKCE podľa RFC 8252.

Redirect options zahŕňajú claimed HTTPS URI, private-use custom scheme alebo loopback URI podľa platformy. Exact registration a OS app-link binding znižujú code interception.

Embedded webview umožňuje clientovi pozorovať credentials a znižuje SSO/browser security. Client secret zabudovaný do binary nie je confidential.

Tokens ukladaj v OS secure storage podľa možností a používaj rotation/revocation pre compromised device.

## 39. mTLS client authentication

RFC 8705 umožňuje client authentication mutual TLS certificate-om. AS overí client certificate pri token endpoint connection a mapuje ho na registered client.

Toto autentizuje client transport identity. Certificate lifecycle, trusted CAs, subject/SAN mapping a rotation musia byť presné.

mTLS client authentication sa môže používať nezávisle od certificate-bound access tokens. Jedno rieši, kto žiada token; druhé viaže issued token na certificate holdera pri Resource Serveri.

## 40. Certificate-bound access tokens

AS vloží do token metadata/thumbprint client certificate-u. Resource Server pri requeste vyžaduje mTLS a overí, že presented certificate zodpovedá token bindingu.

Ukradnutý token bez private keyu/certificate proofu je nepoužiteľný. Token theft risk sa znižuje, ale certificate/private key compromise zostáva.

Load balancer alebo mesh termination musí bezpečne preniesť verified certificate identity. Spoofable header medzi proxy a RS by binding obchádzal.

## 41. DPoP

Demonstrating Proof of Possession — DPoP — viaže token na asymmetric key clienta na application layer-i.

Client pri token requeste a API call-e posiela signed DPoP proof JWT obsahujúci HTTP method, URI, issued time, unique `jti` a public key identity. AS vydá token s confirmation thumbprintom; RS overí proof signature a binding.

DPoP znižuje použiteľnosť stolen tokenu bez private keyu. Nie je transport encryption a stále vyžaduje TLS.

Replay protection potrebuje `jti`, time window, exact method/URI a podľa profile-u nonce. Proxy normalization URI musí byť konzistentná.

## 42. Bearer oproti sender-constrained tokenu

| Vlastnosť | Bearer | Sender-constrained |
|---|---|---|
| Kto môže token použiť | každý holder | holder + private-key/certificate proof |
| Deployment complexity | nižšia | vyššia |
| Replay po leakage | vysoké riziko | obmedzené bez keyu |
| Proxy/load balancer requirements | bežné TLS | proof/cert binding musí prežiť topology |
| Key lifecycle | iba token storage | token + client key/certificate |

Sender constraint neznižuje broad scope alebo nesprávnu audience. Je ďalšia vrstva, nie náhrada least privilege.

## 43. API gateway

Gateway môže validovať external access token a fungovať ako policy enforcement point. Downstream architecture musí explicitne rozhodnúť, čo ďalej propaguje.

Možnosti:

- original token pre service, ktorá je jeho intended audience;
- token exchange na narrower downstream audience;
- internal signed identity/delegation context;
- service workload token oddelený od user delegation.

Gateway musí odstrániť client-supplied security headers a backend musí akceptovať internal identity header iba z authenticated gateway pathu. Direct backend access je bypass.

## 44. Token propagation a confused deputy

Propagovanie jedného broad tokenu cez všetky services umožní každému downstream holderovi volať všetky audiences/scopes, ktoré token povoľuje.

Confused deputy vznikne, keď privileged service vykoná operation pre attacker-controlled request bez zachovania correct subject, actor, audience alebo target bindingu.

Narrow token per service/resource a explicitný delegation context znižujú blast radius. Downstream authorization má overiť initiating subject aj executing service podľa use case-u.

## 45. Token Exchange

RFC 8693 definuje Security Token Service-like exchange. Client predloží subject token a optional actor token a žiada nový token s konkrétnym resource/audience/scope.

Dôležité semantics:

- **subject** — identity, za ktorú sa nový token vydáva;
- **actor** — service alebo principal konajúci v mene subjectu;
- **delegation** — subject zostáva v chain-e;
- **impersonation** — resulting token reprezentuje identity bez rovnakého actor contextu podľa policy;
- **audience/resource** — intended downstream consumer;
- **scope** — narrowed capabilities.

Exchange nesmie automaticky kopírovať všetky upstream privileges. Chain depth, trust, revocation a audit musia byť bounded.

## 46. Multi-tenant authorization

Multi-tenant model potrebuje explicitný issuer, client-registration a resource boundary.

Shared issuer môže vydávať tenant claim, ale RS ho trustuje iba po issuer/audience validation a authoritative mapping. Client-supplied tenant parameter nie je authority.

Cross-tenant controls:

- token audience per API;
- tenant claim type a source;
- server-side object ownership;
- admin consent scope;
- client registration owner;
- redirect URI isolation;
- no automatic identity linking podľa emailu;
- audit tenant + subject + client + actor.

Scope `orders.read` bez tenant enforcementu môže stále povoliť cross-tenant leak.

## 47. Audit

Audit events podľa stage zachytávajú:

- issuer a AS instance;
- client ID a authentication method;
- subject/resource owner a optional actor;
- grant type;
- requested a granted scopes/resources;
- redirect URI/result bez sensitive query;
- token family/generation alebo opaque correlation ID;
- audience;
- consent/admin policy;
- refresh rotation/reuse;
- revocation/exchange;
- RS authorization decision;
- timestamp, source context a correlation ID.

Neloguj authorization code, PKCE verifier, access/refresh token, client secret ani private-key assertion.

## 48. Threats a controls

**Authorization code interception** — PKCE, short one-time code, exact redirect URI.

**Code injection** — PKCE, transaction state a issuer binding.

**CSRF** — random state viazaný na browser transaction; secure cookies/session.

**Mix-up** — expected issuer binding, RFC 9207 `iss` response parameter alebo equivalent protected issuer signal.

**Redirect leakage** — exact registration, no open redirectors, no token in authorization response.

**Token replay** — short lifetime, audience restriction, secure storage, DPoP/mTLS sender constraint.

**Refresh theft** — rotation/reuse detection alebo sender-bound token; family revocation.

**Confused deputy** — explicit audience/resource, narrowed token exchange, actor/subject tracking.

**Client compromise** — scoped credentials, key rotation, deployment integrity a incident revocation.

## 49. Operational monitoring

Sleduj:

- authorization success/error rate;
- callback state/issuer/PKCE failures;
- token endpoint latency a errors podľa grant/client v bounded form;
- authorization-code reuse;
- client authentication failures;
- refresh rotation/reuse detection;
- introspection latency/cache/outage;
- JWKS/key rotation;
- invalid issuer/audience/scope;
- 401/403 rates per API/action;
- revocation propagation latency;
- DPoP/mTLS proof failures;
- suspicious scope/consent escalation;
- token-exchange chain depth a denied delegations.

Client IDs môžu byť bounded labels; subject/token IDs patria do logs, nie high-cardinality metrics.

## 50. Troubleshooting flow

```text
expected issuer a metadata?
→ client registration/type/auth method?
→ exact redirect URI?
→ authorization request, state, PKCE a resource/scope?
→ user authentication/consent/policy?
→ response issuer/state a code lifetime?
→ token endpoint client auth, redirect URI a verifier?
→ granted audience/scope/token type?
→ JWT validation alebo introspection?
→ sender proof?
→ RS resource-level authorization?
→ refresh/revocation/exchange lifecycle?
```

`invalid_redirect_uri` — compare exact scheme, host, port, path a encoding s registration.

`invalid_grant` — expired/reused code, redirect mismatch, PKCE mismatch, revoked refresh token, wrong client binding alebo race.

`invalid_client` — client ID, auth method, secret/key/certificate rotation, JWT assertion audience/time.

API `401` — token presence, issuer, audience, expiry, signature/introspection a sender proof.

API `403` — token valid, ale scope, tenant, object alebo business policy deny.

## 51. Incident response

Pri access/refresh token alebo client credential compromise:

1. identifikuj issuer, client, subject, audience, scope a token family;
2. revoke-ni refresh family/grant a relevantné local sessions;
3. rotate client secret/private key/certificate podľa compromise;
4. zablokuj alebo skráť access tokens cez available RS mechanisms;
5. zachovaj AS, RS, gateway a client audit evidence;
6. analyzuj token use naprieč audiences a exchanged descendants;
7. obnov dôveryhodný client deployment;
8. monitoruj replay a nové issuance;
9. oprav leakage/root cause;
10. over staré credentials a paths ako neplatné.

Pri AS signing-key compromise posúď všetky tokens z exposure interval-u a koordinuj JWKS/trust change so Resource Servers.

## 52. Časté anti-patterny

**OAuth ako login bez OIDC.** Access token sa nesprávne používa ako user authentication proof.

**Client secret v SPA/mobile.** Distributed credential nie je confidential.

**Wildcard redirect URI.** Code/token môže uniknúť attacker-controlled endpointu.

**Implicit flow v novom clientovi.** Token je vydaný cez browser bez protected code exchange.

**ROPC.** Client zbiera user password a obchádza modern authentication.

**Jeden token pre všetky APIs.** Chýba audience isolation.

**Scope ako jediná authorization.** Object ownership, tenant a business rules sa neoveria.

**JWT decode bez validation.** Claims sú attacker-controlled.

**Long-lived bearer refresh token bez rotation.** Theft sa ťažko deteguje a revoke-nuje.

**Gateway identity header bez backend trust boundary.** Client ho spoofne alebo obíde gateway.

**Token exchange bez actor/subject modelu.** Delegation sa mení na broad impersonation.

## 53. Kompletný production príklad

Third-party reporting application potrebuje read-only access k user orders.

1. Client registration povoľuje exact HTTPS redirect URI, Authorization Code grant, PKCE S256 a scopes `orders.read` pre Orders API resource.
2. Client vytvorí state, PKCE verifier/challenge a resource indicator pre Orders API.
3. AS autentizuje usera a zobrazí meaningful consent pre read-only orders.
4. Browser vráti short-lived code; client overí state.
5. Backend vymení code s verifierom a private-key client authentication.
6. AS vydá audience-restricted JWT access token s `orders.read` a rotated refresh token.
7. Orders API overí issuer, signature, audience, expiry, client/subject a scope.
8. API server-side filtruje orders podľa authenticated subject/tenant; scope sám nestačí.
9. Refresh každým use vydá nový token; reuse old generation revoke-ne family.
10. Audit prepája client, subject, consent, token family a API decision bez raw tokens.
11. Pri client compromise sa rotate-ne client key, revoke-nú grants/families a RS monitoruje access-token replay do expiry.

## 54. Kontrolné otázky

1. Aké sú štyri OAuth role a kde sa vykonáva business authorization?
2. Prečo OAuth nie je login protocol?
3. Čo je authorization grant?
4. Ako Authorization Code flow oddeľuje browser od token issuance?
5. Prečo redirect URI potrebuje exact matching?
6. Ako sa `state` a PKCE líšia?
7. Ako PKCE downgrade attack funguje?
8. Ako sa public a confidential client líšia?
9. Čo access token reprezentuje a kto ho validuje?
10. Ako sa scope, audience/resource a local authorization dopĺňajú?
11. Kedy API vráti 401 a kedy 403?
12. Aké trade-offs majú opaque a JWT access tokens?
13. Ako introspection cache ovplyvňuje revocation a availability?
14. Prečo refresh token býva hodnotnejší než access token?
15. Ako rotation a reuse detection fungujú?
16. Prečo implicit a ROPC nie sú vhodné pre nové návrhy?
17. Ako Device Authorization flow oddelí constrained device od user browsera?
18. Ako mTLS a DPoP viažu token na sendera?
19. Ako API gateway bezpečne propaguje identity downstream?
20. Ako token exchange rozlišuje subject, actor, delegation a impersonation?
21. Ako navrhnúť multi-tenant audience a tenant authorization?
22. Navrhni complete OAuth incident response pre stolen refresh-token family.

## Glossary impact

Relevantné pojmy: OAuth 2.0, Resource Owner, Client, Authorization Server, Resource Server, authorization grant, Authorization Code flow, authorization endpoint, token endpoint, redirect URI, state, PKCE, code verifier, code challenge, public client, confidential client, client authentication, access token, bearer token, scope, audience, resource indicator, opaque token, JWT access token, token introspection, refresh token, refresh-token rotation, token family, reuse detection, token revocation, consent, client registration, Authorization Server Metadata, Client Credentials grant, Device Authorization Grant, implicit flow, Resource Owner Password Credentials, Backend for Frontend, mutual-TLS client authentication, certificate-bound access token, DPoP, sender-constrained token, API gateway token propagation, confused deputy, OAuth Token Exchange, subject token, actor token, delegation a impersonation.

## Primárne zdroje

- [RFC 6749 — OAuth 2.0 Authorization Framework](https://datatracker.ietf.org/doc/html/rfc6749)
- [RFC 6750 — Bearer Token Usage](https://datatracker.ietf.org/doc/html/rfc6750)
- [RFC 9700 — Best Current Practice for OAuth 2.0 Security](https://datatracker.ietf.org/doc/html/rfc9700)
- [RFC 7636 — Proof Key for Code Exchange](https://datatracker.ietf.org/doc/html/rfc7636)
- [RFC 8414 — OAuth 2.0 Authorization Server Metadata](https://datatracker.ietf.org/doc/html/rfc8414)
- [RFC 9207 — Authorization Server Issuer Identification](https://datatracker.ietf.org/doc/html/rfc9207)
- [RFC 8707 — Resource Indicators for OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707)
- [RFC 9068 — JWT Profile for OAuth 2.0 Access Tokens](https://datatracker.ietf.org/doc/html/rfc9068)
- [RFC 7662 — OAuth 2.0 Token Introspection](https://datatracker.ietf.org/doc/html/rfc7662)
- [RFC 7009 — OAuth 2.0 Token Revocation](https://datatracker.ietf.org/doc/html/rfc7009)
- [RFC 8628 — OAuth 2.0 Device Authorization Grant](https://datatracker.ietf.org/doc/html/rfc8628)
- [RFC 8252 — OAuth 2.0 for Native Apps](https://datatracker.ietf.org/doc/html/rfc8252)
- [RFC 8705 — OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens](https://datatracker.ietf.org/doc/html/rfc8705)
- [RFC 9449 — OAuth 2.0 Demonstrating Proof of Possession](https://datatracker.ietf.org/doc/html/rfc9449)
- [RFC 8693 — OAuth 2.0 Token Exchange](https://datatracker.ietf.org/doc/html/rfc8693)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Kerberos](kerberos.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OpenID Connect →](openid-connect.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
