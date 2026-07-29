# OAuth 2.0

OAuth 2.0 je authorization framework pre delegovaný alebo workload access k protected API. Authorization Server vydá token, ale Resource Server stále rozhoduje, či exact principal alebo client smie vykonať exact action nad exact resource-om v current business context-e.

Bezpečný authorization code, platná signature a správny scope nevyriešia stale identity input, broad audience, chýbajúcu object authorization ani neúplnú revocation.

## 1. Dominantný lifecycle

```text
protected-operation intent
→ exact issuer, client a resource registration
→ authorization transaction a authenticated subject/client
→ state, redirect URI a PKCE binding
→ one-time authorization code alebo iný grant
→ token-endpoint validation a client authentication
→ access-token audience, scope, lifetime a sender binding
→ Resource Server token validation
→ local tenant/object/business authorization
→ refresh, exchange, delegation a derived-token graph
→ revocation, audit a forbidden-path validation
```

Oddeľuj:

```text
authorization request uspela
≠ code exchange uspel
≠ token je určený tomuto Resource Serveru
≠ scope povoľuje exact operation
≠ object/tenant/business state povoľuje operation
≠ stale alebo compromised grant bol všade revoke-nutý
```

OAuth nie je samostatný login protocol. User authentication a identity claims štandardizuje OpenID Connect. Access token je credential pre Resource Server, nie univerzálny user-login dôkaz pre clienta.

## 2. Exact OAuth subject

Pri incidente zaznamenaj:

```text
issuer a Authorization Server generation
client ID, type, owner a registration revision
grant/flow a authorization transaction ID
subject, actor a authentication/eligibility generation
redirect URI, state a PKCE generation
requested a granted resource/audience/scope
access-token type, iat/exp a sender binding
refresh family alebo token-exchange lineage
Resource Server a exact action/resource/tenant
policy revision, decision a enforcement point
revocation/cache propagation a audit scope
```

Connected Atlas subject:

```text
security incident: SEC-PAY-48
OAuth subject: OAUTH-PAY-48
issuer: https://identity.corp.atlas.example
client: settlement-console
Resource Server: payments-admin-api
subject: martina.kovacova@corp.atlas.example
upstream authentication: enterprise Kerberos session KRB-PAY-48
scope: payments.approve
JWT issue time: 08:13 UTC
JWT expiry: 09:13 UTC
audience: atlas-internal
privileged group removal: 07:40 UTC
```

## 3. Actors a decision boundaries

OAuth rozlišuje:

- **Resource Owner** alebo administrative policy, ktorá povoľuje access;
- **Client**, ktorý token žiada a používa;
- **Authorization Server — AS**, ktorý vyhodnotí grant policy a vydá token;
- **Resource Server — RS**, ktorý chráni API a pozná actual resource state.

```text
AS:
  môže client dostať token pre payments-admin-api
  s capability payments.approve?

RS:
  môže tento subject/client schváliť práve settlement X
  pre tenant Y, v current workflow state a approval windowe?
```

Scope nie je kompletná business authorization. AS spravidla nepozná všetky object ownership, tenant, transaction-state a separation-of-duties constraints.

## 4. Client registration je trust contract

Registration určuje:

```text
client ID a public/confidential type
redirect URIs
allowed grants/response types
client-auth method a keys
allowed resources/audiences/scopes
owner, environment a tenant
lifecycle, rotation a incident contact
```

Client ID nie je secret. Secret vložený do SPA, mobile alebo desktop binary neposkytuje confidential-client authentication.

Redirect URI, key a allowed-scope changes sú high-impact policy mutations. Potrebujú ownera, approval, audit a deployment verification.

## 5. Authorization Code + PKCE lifecycle

```text
client vytvorí pending transaction
→ random state + high-entropy PKCE verifier
→ authorization request s code_challenge S256
→ AS autentizuje subject a vyhodnotí policy/consent
→ one-time short-lived code cez exact redirect URI
→ client overí state a issuer
→ token request s code, redirect URI, verifier a client auth
→ AS atomicky zneplatní code
→ vydá bounded tokens
```

Code nie je access token. Je viazaný na client, redirect URI, PKCE challenge, issuer a transaction generation.

PKCE chráni code interception/injection. `state` viaže browser callback na client transaction. OIDC `nonce` rieši inú identity-token replay/substitution boundary.

## 6. Redirect URI a issuer binding

Authorization Server má používať exact registered redirect URI matching s úzkymi profile-specific výnimkami, napríklad variable loopback port pre native apps.

Client callback musí overiť:

```text
pending transaction existuje
→ state sedí
→ expected issuer sedí
→ code/error patrí tejto transaction
→ redirect endpoint nie je open redirector
→ transaction sa po použití atomicky odstráni
```

Return destination aplikácie nie je dôvod povoliť wildcard OAuth redirect. Ulož ju server-side alebo ju samostatne allowlistuj.

Mix-up ochrana začína trusted issuer bootstrapom. Discovery URL alebo issuer z user inputu nevytvára trust.

## 7. Public a confidential clients

Public client nedokáže spoľahlivo chrániť distributed credential. Používa Authorization Code + PKCE a platform-appropriate redirect a token storage.

Confidential client môže chrániť private key, certificate alebo secret v controlled backend boundary. Token endpoint authentication môže používať `private_key_jwt`, mTLS alebo iný registered mechanismus.

Client authentication dokazuje client identity pri AS endpoint-e. Nedokazuje resource-owner consent ani permission nad target objectom.

## 8. Access token contract

Access token má byť:

- určený presnému Resource Serveru alebo audience;
- obmedzený scopes/capabilities;
- krátkodobý podľa risku;
- prenášaný iba cez TLS;
- chránený pred log/URL/cache leakage;
- validovaný RS;
- podľa potreby sender-constrained.

Bearer token môže použiť každý holder. mTLS certificate-bound token alebo DPoP viaže použitie na client key/certificate, ale nerieši broad scope alebo wrong audience.

Jeden token s audience `atlas-internal` pre všetky APIs vytvára large replay a confused-deputy boundary. Preferuj resource-specific tokens.

## 9. Scope, audience a local resource policy

```text
issuer
+ expected audience/resource
+ token active/expiry
+ client/subject/actor context
+ granted scope
+ local tenant/object/workflow policy
→ allow alebo deny
```

Scope `payments.approve` nepovoľuje automaticky:

- schváliť payment iného tenant-a;
- obísť JIT approval;
- schváliť vlastný request pri separation of duties;
- meniť provider route;
- vykonať action po eligibility removal-e.

RS musí odmietnuť token pre inú audience, aj keď signature, issuer a scope vyzerajú platne.

## 10. Resource Server token validation

JWT access token typicky vyžaduje:

```text
trusted issuer
→ allowed algorithm a trusted key/kid
→ signature
→ expected audience
→ exp/nbf/iat policy
→ token/client/subject profile claims
→ sender proof, ak required
→ local authorization
```

JWT je signed, nie automaticky encrypted. Claims sú holderovi čitateľné a nemajú obsahovať unnecessary sensitive data.

Opaque token sa overuje introspection alebo authoritative lookupom. Introspection cache vytvára trade-off medzi revocation latency a availability. Endpoint timeout musí byť odlíšený od `active=false`; fail-open/closed behavior patrí do operation-risk contractu.

Base64 decode bez signature a semantic validation nie je token validation.

## 11. `401` a `403`

```text
missing/invalid/expired/wrong-audience token
→ 401

valid token, ale scope/tenant/object/business policy deny
→ 403 alebo policy-specific non-disclosing response
```

Resource existence nemusí byť odhalená unauthorized callerovi. Error response má byť užitočný pre legitimate clienta bez leakage sensitive policy detailu.

## 12. Authorization state nie je len token snapshot

Self-contained token môže zostať cryptographically validný do expiry, aj keď group, role, account alebo JIT grant boli medzitým odstránené.

```text
identity/entitlement generation pri issuance
→ claims/scopes snapshot
→ distributed RS validation
→ residual authorization window
```

High-risk capability potrebuje kombináciu:

- krátkej access-token lifetime;
- revocation/status mechanismu podľa architecture;
- event-driven session/grant revocation;
- current local resource/JIT checku;
- bounded cache;
- negative second-session testu.

Signature validity nepreukazuje current eligibility.

## 13. Refresh-token lifecycle

Refresh token je credential pre AS, často hodnotnejší než access token. Predlžuje grant a môže vydávať nové access tokens.

Rotation:

```text
RT1 → AT2 + RT2
RT1 invalid
RT2 → AT3 + RT3
```

AS uchová family/lineage. Reuse old generation môže signalizovať theft alebo lost-response race. Implementation potrebuje atomicity, bounded retry/idempotency semantics a incident policy.

Pri confirmed reuse sa spravidla revoke-ne active family/grant a vyžaduje reauthorization, pretože server nevie spoľahlivo určiť, ktorý holder je legitímny.

Pre public clients OAuth Security BCP vyžaduje refresh-token rotation alebo sender-constrained refresh tokens.

## 14. Revocation je graph problem

Revocation môže zahŕňať:

```text
local application session
refresh token a family
grant/consent
opaque access-token state
JWT status/denylist alebo expiry window
downstream exchanged tokens
gateway cache
Resource Server introspection/JWKS cache
```

Revocation request success na AS nepreukazuje, že každý RS okamžite odmieta všetky descendants. Incident closure potrebuje end-to-end forbidden-use test.

## 15. Client Credentials

Client Credentials sa používa, keď confidential workload koná vo vlastnom mene.

```text
workload client authentication
→ AS service policy
→ audience/scoped workload token
→ RS workload authorization
```

Nie je to human delegation. Shared client secret medzi veľkým fleetom znižuje attribution. Preferuj workload identity, mTLS alebo private-key authentication s krátkodobým lifecycle-om.

Workload token nesmie predstierať human subjecta bez explicitného impersonation alebo delegation modelu.

## 16. Device Authorization a native/browser clients

Device Authorization oddeľuje constrained device od trusted user browsera. User code nie je dostatočný secret; flow potrebuje short expiry, rate-limited polling, clear client identity a protection pred phishing/code substitution.

Native app používa external system browser a Authorization Code + PKCE. Embedded webview môže pozorovať user credentials a obchádzať browser trust/SSO controls.

SPA je public client a JavaScript-accessible token je vystavený XSS. Backend for Frontend môže držať tokens server-side a browseru dať HttpOnly session cookie, ale pridáva CSRF, session revocation, backend availability a no-generic-proxy requirements.

## 17. Deprecated alebo forbidden patterns

OAuth Security BCP neodporúča nové response types, ktoré vydávajú access token priamo na authorization endpoint-e. Authorization Code + PKCE poskytuje protected code exchange.

Resource Owner Password Credentials — ROPC — sa nesmie používať. Client by priamo zbieral user password a obchádzal MFA, passkeys, federation, consent a origin-bound authentication.

Client secret v SPA/mobile, wildcard redirects a long-lived broad bearer tokens sú architecture defects, nie iba configuration preferences.

## 18. mTLS a DPoP

mTLS môže autentizovať confidential clienta na token endpoint-e a viazať access token na certificate. DPoP používa application-layer signed proof pre HTTP method, URI, issued time a unique `jti`.

```text
token
+ confirmation key thumbprint
+ per-request proof
→ sender-binding verdict
```

Sender constraint znižuje replay po token leakage bez private keyu. Stále potrebuje TLS, exact audience, scope, key rotation a local authorization.

Proxy URI normalization, TLS termination a certificate forwarding musia byť explicitne navrhnuté; inak RS nevie proof spoľahlivo overiť.

## 19. Gateway a downstream propagation

Gateway môže validovať external token, ale downstream identity path musí byť explicitný:

- original token iba pre service, ktorá je intended audience;
- token exchange na narrower audience;
- signed internal subject/actor context;
- oddelený service workload token.

Gateway musí odstrániť client-supplied security headers. Backend smie trustovať internal header iba z authenticated, non-bypassable gateway pathu.

Propagovať jeden broad user token cez všetky services znamená, že každý downstream holder zdedí jeho replay capability.

## 20. Token Exchange, delegation a actor chain

Token Exchange môže vytvoriť nový downstream token z subject a optional actor tokenu.

```text
subject
+ actor/executing service
+ requested resource/audience
+ narrowed scope
+ chain-depth policy
→ downstream token
```

Delegation zachová initiating subject aj actor. Impersonation mení výslednú identity semantics a potrebuje silnejší policy/audit model.

Exchange nesmie automaticky kopírovať všetky upstream scopes. Revocation musí poznať descendants alebo akceptovať explicitný residual window.

## 21. Multi-tenant authorization

Tenant parameter poslaný clientom nie je authority. RS potrebuje server-side mapping:

```text
trusted issuer/subject/client
→ authoritative tenant membership
→ object ownership
→ action/workflow policy
```

Shared issuer môže používať tenant claim, ale claim sa trustuje iba po issuer/audience/profile validation. Identity linking podľa emailu bez issuer+subject boundary môže spojiť cudzie accounts.

Audit má zachovať tenant, subject, client, actor, resource a decision.

## 22. Worked failure: secure code flow vydal stale privilege

### Symptom

Settlement console použije Authorization Code + PKCE, validný `state`, exact redirect URI a trusted signing key. Napriek tomu Martina o `08:17 UTC` schváli provider-route change po odstránení privileged group membershipu.

### Exact subject

```text
OAuth subject: OAUTH-PAY-48
issuer: https://identity.corp.atlas.example
client: settlement-console
flow: Authorization Code + PKCE S256
authenticated subject: martina.kovacova@corp.atlas.example
directory/Kerberos source: DC-FRA-02 / KRB-PAY-48
grant scope: payments.approve
audience: atlas-internal
iat/exp: 08:13–09:13 UTC
Resource Server: payments-admin-api
operation: POST /settlements/PAY-884219/approve
```

### Competing hypotheses

1. authorization code bol intercepted alebo replayed;
2. `state` alebo issuer binding zlyhali;
3. PKCE downgrade umožnil code injection;
4. AS signing key bol compromised;
5. wrong redirect/client registration vydala token attackerovi;
6. stale AD/Kerberos/LDAP eligibility vytvorila wrong scope;
7. broad audience umožnila token použiť na unintended API;
8. RS považoval scope za complete business authorization;
9. stolen refresh token vydal nový access token po revocation.

### Discriminating evidence

```text
state: exact match, single use
PKCE: S256 challenge/verifier match
code: single-use, correct client a redirect
issuer/signature/kid: trusted a valid
client authentication: expected private key
JWT iat: 08:13 UTC, teda po AD removal-e
grant input DC-FRA-02: stale privileged membership
JWT scope: payments.approve
JWT audience: atlas-internal
RS validation: signature/issuer/audience/scope allow
RS local JIT approval check: absent
refresh reuse: none
```

Authorization transaction bola protocol-correct. Root cause inputu je stale directory/Kerberos eligibility. OAuth causal amplifiers sú broad audience, hodinový self-contained privilege snapshot a RS, ktorý nekontroloval current JIT/business authorization.

### Evidence-preserving containment

- zastaviť privileged token issuance pre affected entitlement generation;
- revoke-nuť subject session, refresh family, grant a known exchanged descendants;
- pridať bounded RS deny/status control pre affected token/principal generation;
- preserve-nuť AS transaction, state/PKCE verdict, client auth, token metadata, RS decision a business audit bez raw tokenov/secrets;
- neotáčať signing key, ak key compromise nie je podporené evidence;
- neotvárať broad admin fallback alebo fail-open introspection.

### Authoritative recovery

1. opraviť AD/LDAP/Kerberos freshness path;
2. invalidovať všetky sessions/grants odvodené zo stale group generation;
3. nahradiť broad `atlas-internal` audience resource-specific `payments-admin-api` tokenom;
4. skrátiť high-risk access-token lifetime a zaviesť bounded status/revocation path;
5. grantovať `payments.approve` iba z current JIT approval generation, nie permanentného directory group snapshotu;
6. vyžadovať na RS exact tenant, settlement, workflow state, approver separation a approval ID;
7. zachovať subject+actor pri gateway/token exchange;
8. testovať direct API, alternate audience, stale JWT, old refresh family a second-login paths.

### Acceptance verdict

- correct Authorization Code + PKCE flow vydá token iba oprávnenému current subjectu/clientovi;
- token má exact `payments-admin-api` audience a minimal scope;
- RS povoľuje approved settlement iba s validným JIT approval/resource state-om;
- removed principal zlyhá s fresh loginom, old JWT, refresh, token exchange aj direct API;
- wrong audience, issuer, redirect, PKCE, sender proof a tenant fixtures zlyhajú;
- audit zachová client, subject, actor, grant, resource a decision bez raw credentials;
- druhá controlled eligibility removal prejde revocation-propagation a second-session testom.

## 23. Audit a observability

Podľa stage sleduj:

- authorization request/result, issuer a client;
- state/PKCE/redirect/issuer failures;
- requested a granted resource/scope;
- client-auth method a key generation;
- code reuse a token endpoint errors;
- token family/refresh reuse;
- audience/issuer/signature/introspection failures;
- 401/403 podľa API/action;
- sender-proof failures;
- token-exchange actor/subject chain;
- revocation propagation latency;
- RS local authorization decision.

Neloguj authorization code, PKCE verifier, access/refresh token, client secret ani private-key assertion.

## 24. Incident response

```text
identify issuer/client/subject/actor/resource/scope/family
→ preserve AS, client, gateway a RS evidence
→ revoke session/grant/refresh family/descendants
→ rotate client credential iba ak compromised
→ contain access-token replay window
→ reconcile affected resource actions
→ restore trusted client/identity state
→ validate old paths forbidden
→ add earlier control
```

AS signing-key compromise je odlišný incident. Potrebuje koordinovaný JWKS/trust update a posúdenie všetkých tokens z exposure interval-u.

## 25. Troubleshooting flow

```text
trusted issuer/metadata
→ client registration/type/auth method
→ redirect URI/state/PKCE/resource/scope
→ subject authentication a eligibility
→ code binding/single use
→ token endpoint/client auth
→ granted audience/scope/token type
→ JWT/introspection/sender validation
→ RS tenant/object/business authorization
→ refresh/exchange/revocation lineage
```

`invalid_grant` môže znamenať expired/reused code, redirect alebo PKCE mismatch, wrong client binding, revoked refresh token alebo rotation race.

API `401` smeruje k token trust/validity. API `403` smeruje k scope alebo local resource policy. Admin token, ktorý „funguje“, iba maskuje missing exact permission.

## 26. Earlier controls

- exact redirect a PKCE S256 policy pre code clients;
- resource-specific audience a minimal scope catalog;
- client registration owner, expiry a key rotation;
- entitlement-generation ID v grant audit metadata;
- event-driven revoke pri privileged mover/leaver/removal;
- short-lived high-risk token plus current JIT/resource check;
- refresh-family reuse and lost-response tests;
- negative audience/tenant/object/token-exchange fixtures;
- end-to-end revocation canary;
- actor/subject preservation cez gateway a downstream services.

## 27. Anti-patterny

### OAuth access token ako login identity

Client potrebuje OIDC alebo iný authentication contract.

### Valid signature = allow

Audience, scope, subject/client, local object policy a current state stále chýbajú.

### Jeden token pre všetky APIs

Compromise alebo confused deputy má široký blast radius.

### Scope ako complete authorization

Tenant, object, workflow a separation-of-duties checks sa obídu.

### ROPC alebo implicit flow pre nový client

Primary credential alebo access token sa dostáva do nesprávnej front-channel/client boundary.

### Revocation iba refresh tokenu

Existing access tokens, sessions a exchanged descendants môžu prežiť.

### Gateway header bez non-bypassable trust pathu

Client header spoofne alebo zavolá backend priamo.

## 28. Kontrolné otázky

1. Čo tvorí exact OAuth subject?
2. Kde sa líši AS grant decision od RS business authorization?
3. Ako sa `state`, PKCE, redirect URI a issuer binding dopĺňajú?
4. Prečo client ID nie je secret?
5. Ako sa scope a audience líšia?
6. Čo musí RS overiť nad rámec JWT signature?
7. Ako introspection cache mení revocation a availability?
8. Prečo refresh rotation potrebuje token-family a retry semantics?
9. Ako mTLS/DPoP pomáha a čo nevyrieši?
10. Ako preukážeš end-to-end revocation vrátane exchanged tokens?

## Glossary impact

Relevantné pojmy: OAuth subject, authorization-transaction generation, grant-input generation, resource-specific token, token authorization snapshot, local resource verdict, refresh-family generation, derived-token graph, revocation-propagation verdict, subject-actor chain, JIT-bound scope a OAuth acceptance verdict.

## Primárne zdroje

- [RFC 6749 — OAuth 2.0](https://www.rfc-editor.org/rfc/rfc6749)
- [RFC 9700 — OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700)
- [RFC 7636 — PKCE](https://www.rfc-editor.org/rfc/rfc7636)
- [RFC 8707 — Resource Indicators](https://www.rfc-editor.org/rfc/rfc8707)
- [RFC 9068 — JWT access-token profile](https://www.rfc-editor.org/rfc/rfc9068)
- [RFC 7662 — Token Introspection](https://www.rfc-editor.org/rfc/rfc7662)
- [RFC 7009 — Token Revocation](https://www.rfc-editor.org/rfc/rfc7009)
- [RFC 8705 — OAuth mTLS](https://www.rfc-editor.org/rfc/rfc8705)
- [RFC 9449 — DPoP](https://www.rfc-editor.org/rfc/rfc9449)
- [RFC 8693 — Token Exchange](https://www.rfc-editor.org/rfc/rfc8693)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Kerberos](kerberos.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OpenID Connect →](openid-connect.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
