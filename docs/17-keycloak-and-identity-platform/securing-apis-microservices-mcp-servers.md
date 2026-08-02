# Securing APIs, microservices a MCP servers cez Keycloak

Keycloak vydáva identity a authorization artifacts; samotnú API ochranu dokončuje resource server. Každá služba musí validovať exact issuer, signing key, token type, time, audience, authorized party/caller a následne urobiť local tenant, resource a action decision. API gateway môže centralizovať edge controls, ale nesmie byť jediným enforcement pointom, ak sa služby dajú volať interne alebo ak business permission závisí od konkrétneho resource state-u. Platný access token nie je automaticky povolenie na ľubovoľný endpoint.

MCP server je resource server s ďalšími discovery a client-registration requirements. Keycloak 26.7 podporuje MCP authorization profile 2025-03-26. Profily 2025-06-18 a 2025-11-25 sú iba čiastočne podporované, pretože Keycloak zatiaľ nespracúva OAuth Resource Indicators `resource` parameter podľa RFC 8707. Scope plus Audience mapper môže vytvoriť intended `aud`, ale nie je to plná RFC 8707 conformance. Dokumentácia a acceptance musia tento rozdiel zachovať.

## 1. Dominantný token-to-business-operation lifecycle

```text
client alebo workload intent
→ exact Keycloak realm/client/grant generation
→ access-token request a audience/scope projection
→ signed access token
→ transport k API/MCP serveru
→ issuer/signature/kid/time/token-type validation
→ audience a caller/authorized-party validation
→ local tenant/resource/action/context authorization
→ idempotent business operation
→ audit/evidence
→ revocation/key/policy change a second-operation test
```

Každá fáza má samostatný failure outcome. Token endpoint success nepreukazuje API audience. JWT signature success nepreukazuje access-token type ani intended caller. Role claim nepreukazuje ownership konkrétneho invoice alebo tenant membership v čase requestu. HTTP `200` nepreukazuje single business effect pri retry. Gateway acceptance nepreukazuje, že direct service path je chránený.

## 2. Exact API security subject

```yaml
apiSecuritySubject:
  authorizationServer:
    deploymentGeneration: kc-2026-08-02-31
    realm: atlas-prod
    issuer: https://sso.atlas.example/realms/atlas-prod
    signingKeyGeneration: sig-2026-08-01
    jwksRevision: jwks-84
  client:
    clientId: settlement-web
    internalId: 2b2b...
    grant: authorization_code
    pkce: S256
    clientConfigurationRevision: client-219
  token:
    tokenType: access_token
    jti: 91ae...
    kid: sig-2026-08-01
    sub: 78f4...
    azp: settlement-web
    aud: [settlement-api]
    scope: openid settlement:read
    issuedAt: 2026-08-02T08:01:00Z
    expiresAt: 2026-08-02T08:06:00Z
  resourceServer:
    service: settlement-api
    deploymentUid: 1f8a...
    imageDigest: sha256:91aa...
    policyRevision: api-authz-73
    jwksCacheGeneration: jwks-cache-42
  request:
    method: GET
    route: /tenants/orion/settlements/991
    tenant: orion
    resourceId: 991
    action: settlement.read
    requestId: req-1511
    traceId: 44d2...
    operationId: settlement-read-20260802-991
```

Bez token type-u môže API prijať ID token určený clientovi. Bez audience a `azp` nevie odlíšiť intended resource server a calling client. Bez tenant/resource/action identity sa role-only authorization nedá auditovať. Bez policy revision sa decision po policy rollout-e nedá reprodukovať.

## 3. Access, ID a refresh token boundaries

```text
access token
→ bearer alebo sender-constrained credential pre resource server

ID token
→ authentication statement pre OIDC client
→ nie API credential

refresh token
→ credential pre token endpoint
→ nikdy business API bearer
```

API musí explicitne odmietnuť ID a refresh token. Claim overlap nie je dôkaz správneho token type-u. Token profiles a lightweight access tokens môžu meniť claim surface; consumer contract má sledovať stable required claims a introspection/JWT strategy.

## 4. Local JWT validation

Keycloak access tokens sú typicky signed JWT a resource server ich môže validovať lokálne:

```text
parse compact JWS
→ reject unsupported alg/critical headers
→ resolve kid z trusted realm JWKS
→ verify signature
→ verify iss
→ verify exp/nbf/iat s bounded clock skew
→ verify aud
→ verify token type a caller
→ authorize operation
```

Nikdy nevyberaj issuer alebo JWKS URL z untrusted token claimu bez allowlist-u. Realm issuer je configured trust anchor. Algorithms sú allowlisted; `none` alebo unexpected symmetric algorithm sa odmieta.

Príklad v Java/Spring Security:

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://sso.atlas.example/realms/atlas-prod
          audiences: settlement-api
```

Framework configuration je intended validation. Integration test musí poslať wrong issuer, wrong audience, expired, future `nbf`, unknown `kid`, ID token a malformed token.

## 5. JWKS cache a key rotation

Resource server cacheuje public keys podľa `kid`. Rotation lifecycle:

```text
successor realm key published v JWKS
→ new tokens signed successor kid
→ APIs refresh/cache successor key
→ predecessor tokens remain valid do expiry podľa policy
→ predecessor key retired až po overlap
```

Unknown `kid` môže triggernúť bounded JWKS refresh. Nevykonávaj unbounded network call pre každý invalid token. JWKS outage nesmie okamžite vyradiť valid cached keys; stale-cache policy má limit a alerting.

Key compromise vyžaduje odlišný emergency model: retire key, not-before/session handling, API cache invalidation a token descendants. HTTPS certificate rotation nie je realm signing-key rotation.

## 6. Introspection

Confidential resource server môže volať introspection endpoint:

```bash
curl --fail --silent --show-error \
  --user "settlement-api:${SETTLEMENT_API_SECRET}" \
  --data-urlencode "token=${ACCESS_TOKEN}" \
  https://sso.atlas.example/realms/atlas-prod/protocol/openid-connect/token/introspect \
  | jq '{active,iss,sub,aud,azp,scope,exp,iat}'
```

Introspection umožní current active state a podporuje lightweight/opaque-like patterns, ale pridáva network latency, Keycloak capacity coupling a confidential credential. Cache active response iba do bounded token expiry/policy window. Introspection `active=true` stále nepreukazuje tenant/resource/action permission.

`Accept: application/jwt` môže v configured scenario vrátiť signed introspection response a optional full JWT claim pre lightweight access token. Consumer musí validate-nuť aj túto response.

## 7. Audience a caller validation

Minimálny API contract:

```text
iss == atlas-prod issuer
AND aud contains settlement-api
AND azp/client identity je allowed caller class
AND token type == access token
```

Audience hovorí, pre ktorý resource server je token intended. `azp` identifikuje authorized party/calling client v relevantných flows. Dve clients môžu dostať rovnakú role, ale iba jedna smie volať high-risk endpoint.

Broad multi-audience token zvyšuje replay blast radius. Preferuj service-specific audience cez client scopes/Audience mapper alebo token exchange. Nepridávaj všetky internal APIs do default audience každého tokenu.

## 8. Claims nie sú complete business authorization

Keycloak môže publikovať roles, groups, tenant ID alebo permissions, ale API musí rozhodnúť podľa authoritative resource state-u.

```text
role settlement-reader
+ tenant claim orion
+ resource 991 belongs to tenant orion
+ user/service account is active for operation
→ allow settlement.read
```

Mutable profile attribute nesmie byť security authority bez controlled writer. Group hierarchy alebo composite role môže rozšíriť claims. Claim size a staleness rastie s access-token TTL. High-risk action môže vyžadovať current policy lookup alebo short-lived exchanged token.

## 9. Role, scope a permission semantics

Tieto štyri pojmy môžu používať rovnaký textový názov, ale vznikajú v odlišnej authority a dokazujú odlišnú vec. OAuth scope opisuje granted client capability, role je Keycloak entitlement, Authorization Services permission je PDP decision a local permission je finálny business-resource verdict. API musí preto fixovať namespace, issuer a writer každého claimu skôr, než ho porovná s endpoint policy.

```text
OAuth scope
→ requested/granted client capability string

realm/client role
→ Keycloak entitlement projected do claims

Authorization Services permission
→ resource/scope decision, často v RPT

local API permission
→ final tenant/resource/action decision
```

Názov `settlement:read` môže byť scope, client role alebo local permission; contract musí uviesť namespace a authority. API nesmie porovnávať voľný string bez provenance.

## 10. Gateway versus service enforcement

Gateway môže validovať TLS, token signature, issuer, coarse audience, rate limit a route. Služba musí znovu validate-nuť alebo dôverovať cryptographically/network-bound identity assertion z gateway podľa explicitného modelu.

```text
external client
→ API gateway coarse PEP
→ service local PEP
→ database/resource authorization
```

Header `X-User` od gateway je bezpečný iba ak direct service access je blokovaný, gateway odstraňuje inbound spoofed headers a service autentizuje gateway cez mTLS/workload identity. Pri zero-trust model-e service validuje original access token.

Gateway-only role mapping nevie bezpečne rozhodnúť resource ownership. Service-only validation bez edge rate limiting môže vystaviť Keycloak/JWKS/introspection alebo API DoS.

## 11. Service-to-service client credentials

Machine caller používa confidential client/service account:

```bash
curl --fail --silent --show-error \
  --user "settlement-batch:${SETTLEMENT_BATCH_SECRET}" \
  --data-urlencode 'grant_type=client_credentials' \
  --data-urlencode 'scope=settlement:reconcile' \
  https://sso.atlas.example/realms/atlas-prod/protocol/openid-connect/token
```

API validuje `azp`, service-account `sub`, audience, role/scope a resource/action. Static secret replay risk sa znižuje private-key JWT, mTLS alebo workload federation podľa architecture. Human user a machine client nemajú zdieľať mixed-purpose client.

## 12. Delegation a token exchange

Service chain nemá forwardovať broad user token do všetkých downstreams. Token exchange môže vytvoriť narrower audience/scope a zachovať subject/actor context.

```text
user token pre API A
→ API A authorized exchange
→ token pre API B
→ aud API-B, narrowed scope
→ API B validates actor/subject a local resource
```

API A nesmie token exchange používať ako arbitrary impersonation. Exchange permissions, requested subject, audience, actor context a descendants patria do evidence. Chapter 15 obsahuje detailný exchange lifecycle.

## 13. BFF, browser a CORS

Browser SPA/public client používa Authorization Code + PKCE. Token storage v browseri zvyšuje XSS exposure. Backend-for-frontend môže držať tokens server-side a browseru dať hardened application session cookie.

```text
browser
→ BFF session cookie
→ BFF access token k API
```

BFF musí riešiť CSRF, session fixation, cookie attributes, logout a token refresh. CORS určuje, ktorý browser origin smie čítať response; nie je authentication ani authorization. Allowed origin `*` s credentials je unsafe/nevalidný model.

## 14. Error semantics

HTTP status je súčasť security contractu, nie iba UX detail. `401` signalizuje, že request nemá prijateľnú credential identity; `403` znamená validnú identity bez požadovanej local permission a `404` môže zámerne skryť foreign-resource existence. Konzistentná voľba riadi client retry, reauthentication, audit aj ochranu pred enumeration.

```text
401 Unauthorized
→ credential missing/invalid/expired/wrong issuer/audience/token type

403 Forbidden
→ credential valid, ale local permission absent

404 podľa resource-enumeration policy
→ optional concealment, stále auditovaný deny
```

Neodhaľuj, či foreign-tenant resource existuje. `WWW-Authenticate` header môže uviesť Bearer error podľa standardu bez secrets/internal policy detailov.

## 15. Revocation a token freshness

JWT local validation je offline a nevidí okamžite všetky server-side revocations. Controls:

```text
short access-token TTL
refresh-token/session revocation
realm/client/user not-before
introspection/current-policy check pre high-risk operation
sender-constrained tokens
```

API musí poznať maximum stale authorization window. Role removal nevymaže už vydaný token. Incident response môže vyžadovať denylist `jti` alebo policy cutoff, ale unbounded denylist je operational cost.

## 16. DPoP a mTLS sender constraints

Bearer token môže použiť ktokoľvek, kto ho ukradne. DPoP alebo mTLS môže token viazať na client key/certificate podľa supported feature/profile.

```text
access token cnf claim
+ request proof/certificate
→ resource server verifies possession
```

Sender constraint nenahrádza audience, issuer ani local authorization. Preview feature status a library support musia byť explicitné. Clock/replay cache a key rotation sú nové state boundaries.

## 17. Authorization Services a PEP

Keycloak Authorization Services rozlišuje PAP, PDP, PIP a PEP. Resource server definuje resources/scopes/policies/permissions a PEP v službe presadzuje decision.

```text
request resource/scope
→ PDP policy evaluation
→ RPT/decision
→ PEP local enforcement
→ business operation
```

Central PDP umožní runtime policy updates, ale pridáva availability/cache/staleness coupling. PEP cache key musí obsahovať subject/caller/tenant/resource/scope/policy generation. Authorization Services nie sú povinné pre každé API; jednoduchá local RBAC/ABAC môže byť bezpečnejšia a ľahšie auditovateľná.

## 18. API inventory a client separation

Každý resource server má samostatný client/audience a owner:

```yaml
resourceServer:
  service: settlement-api
  keycloakClientId: settlement-api
  audiences: [settlement-api]
  acceptedCallers: [settlement-web, settlement-batch, reporting-api]
  permissions:
    - settlement.read
    - settlement.reconcile
  tokenTypes: [access_token]
  validationMode: local-jwt
```

Nezdieľaj jeden `platform-api` audience pre unrelated services. Client secret resource servera je potrebný iba pre introspection/Protection API/token exchange podľa use case; local JWT validation môže byť public-key only.

## 19. Microservice east-west network

Token validation predpokladá trustworthy transport. Service mesh mTLS chráni channel/workload identity, ale user access token chráni end-user/delegated authorization.

```text
mTLS workload identity
AND JWT user/client identity
AND local resource permission
→ allow
```

Network identity a token caller sa musia zhodovať podľa policy. Compromised workload s ukradnutým tokenom nesmie volať endpoint určený inej service class.

## 20. MCP authorization architecture

MCP server je OAuth protected resource. Musí publikovať Protected Resource Metadata podľa RFC 9728 a odkázať klienta na authorization server metadata. Keycloak poskytuje Authorization Server Metadata/OIDC discovery a OAuth/OIDC endpoints.

```text
MCP client discovers MCP server
→ MCP protected-resource metadata
→ Keycloak authorization-server metadata
→ client registration/pre-registration/CIMD
→ Authorization Code + PKCE
→ access token bound na MCP server audience
→ MCP server validates token a scopes
→ tool/prompt/resource authorization
```

MCP tool call je business operation. Scope `mcp:tools` nepreukazuje oprávnenie volať každý tool; server musí mapovať tool/resource/prompt name, tenant a arguments na local policy.

## 21. MCP version conformance

Keycloak 26.7 official status:

```text
MCP 2025-03-26
→ supported

MCP 2025-06-18
→ partially supported without RFC 8707 Resource Indicators

MCP 2025-11-25
→ partially supported without RFC 8707 Resource Indicators
```

Neoznačuj novšie versions za plne compliant. MCP 2024-11-05 nemá authorization model a nepatrí do protected production use bez external design.

## 22. MCP audience workaround bez RFC 8707

Novšie MCP versions vyžadujú `resource` parameter a audience binding. Keycloak 26.7 parameter nerozpozná. Official workaround používa requested optional scopes a Audience mapper s Included Custom Audience zhodným s MCP server URL.

```text
optional client scope mcp:tools
→ Audience mapper
→ Included Custom Audience = https://mcp.atlas.example/mcp
```

Token fixture:

```json
{
  "aud": "https://mcp.atlas.example/mcp",
  "scope": "openid mcp:tools mcp:resources"
}
```

MCP server musí exact audience URL validate-nuť. Workaround nevytvára plnú RFC 8707 semantics: Keycloak nespracúva `resource` parameter ako authorization-server input. Dokumentácia a client interoperability test to uvádzajú.

## 23. MCP scopes a local tool policy

MCP scopes definujú hrubú capability surface, nie automatické povolenie každého toolu, resource alebo promptu. Server musí po scope gate-e vykonať local decision nad callerom, tenantom, exact operation name-om, arguments/resource ownershipom a risk contextom. Tým sa z MCP servera nestane confused deputy, ktorý broad capability premení na neobmedzený downstream access.

```text
mcp:tools
→ capability používať tool surface

mcp:resources
→ capability čítať resource surface

mcp:prompts
→ capability používať prompt surface
```

Každá capability sa ďalej zužuje:

```text
caller client + user/workload
+ tenant
+ exact tool/resource/prompt
+ argument/resource ownership
+ risk/step-up context
→ allow
```

Tool `delete_invoice` nesmie byť povolený iba scope-om `mcp:tools`. High-risk tool môže vyžadovať role, fresh LoA/ACR, approval a operation idempotency.

## 24. MCP client registration

MCP 2025-11-25 umožňuje Client ID Metadata Documents, pre-registration alebo dynamic client registration. Keycloak CIMD je experimental feature:

```bash
bin/kc.sh start --features=cimd
```

Client policy musí allowlist-nuť HTTPS scheme a trusted domains, kontrolovať metadata URL properties a size/cache limits. Remote metadata fetch je SSRF/supply-chain boundary.

```text
client_id URL
→ HTTPS/path/query/userinfo validation
→ trusted-domain policy
→ bounded metadata fetch/cache/size
→ redirect/JWKS/token-auth validation
```

Development-only `Allow http` nesmie byť production. Localhost callback pre desktop public client je samostatne allowlisted s PKCE a exact loopback semantics.

Dynamic Client Registration anonymous policies musia limitovať allowed scopes, origins, trusted hosts, redirect patterns a registration lifetime. MCP Inspector convenience nemá otvoriť broad production registration.

## 25. MCP Protected Resource Metadata

MCP server, nie Keycloak, publikuje RFC 9728 metadata. Metadata musí identifikovať resource a trusted authorization server.

```json
{
  "resource": "https://mcp.atlas.example/mcp",
  "authorization_servers": [
    "https://sso.atlas.example/realms/atlas-prod"
  ],
  "scopes_supported": [
    "mcp:tools",
    "mcp:resources",
    "mcp:prompts"
  ]
}
```

Metadata discovery success nepreukazuje token audience ani tool authorization. Cache, TLS, redirect a issuer exactness sa testujú.

## 26. MCP public clients a PKCE

Desktop MCP clients sú public clients a nesmú mať embedded secret. Používajú Authorization Code + PKCE `S256` a loopback redirect podľa client contractu. CIMD/DCR policy nesmie automaticky dôverovať arbitrary localhost port + arbitrary client metadata domain.

```text
random verifier
→ S256 challenge
→ authorization code bound na client/redirect/challenge
→ loopback callback
→ code exchange s verifierom
```

Malicious local process interception, browser session mix-up a open redirect sú negative tests.

## 27. MCP tokens a confused deputy

MCP server môže volať downstream APIs/tools. Nesmie forwardovať broad MCP user token automaticky.

```text
MCP access token
→ authorize MCP operation
→ exchange alebo service credential pre downstream API
→ narrowed audience/scope
→ preserve actor/subject audit
```

Otherwise downstream API môže prijať token, ktorý nebol intended preň, alebo MCP server sa stane confused deputy. Tool execution má durable operation ID, argument validation a output redaction.

## 28. Audit a privacy

API/MCP audit spája:

```text
issuer/sub/azp/jti hash
resource server/image/policy generation
route/tool/resource/prompt identity
requested tenant/resource/action
allow/deny reason class
operation ID/result
```

Neloggovať raw tokens, prompts obsahujúce secrets, tool credentials alebo sensitive outputs. MCP môže pracovať s high-volume model contextom; audit capture musí byť bounded a classified.

## 29. Incident `KC-PAY-80`

Atlas gateway validoval iba signature a expiry. Neoveroval `aud`; access token pre reporting API bol replaynutý voči settlement API. Gateway pridal `X-User`, ale internal service bolo dostupné priamo a dôverovalo headeru bez mTLS. Role `settlement-operator` povoľovala všetky tenants bez resource ownership checku.

MCP server akceptoval token s `scope=mcp:tools`, ale nevalidoval exact audience ani tool-level policy. Tool `export_settlements` použil broad service credential a forwardoval data iného tenant-u. Dokumentácia tvrdila MCP 2025-11-25 compliance, hoci Keycloak nespracúval RFC 8707 `resource` parameter.

```text
signature-only validation
+ gateway-header trust bez network binding
+ role-only resource authorization
+ broad MCP scope bez audience/tool policy
→ confused deputy a cross-tenant data exposure
```

Recovery pridala issuer/audience/azp/token-type validation v každej service, mTLS/direct-path isolation, tenant/resource/action policy a service-specific exchanged tokens. MCP server publikuje protected-resource metadata, validuje exact URL audience a označuje novšie MCP versions ako partial workaround do native RFC 8707 supportu.

## 30. Evidence-preserving containment a recovery

Zachovaj raw token hash/decoded non-secret claims, issuer/JWKS/key generation, client scope/mapper config, gateway/service policy revisions, route/network identities, introspection/JWKS logs, tenant/resource records, MCP metadata/version, client-registration policy, tool calls/operation IDs a downstream token/exchange evidence.

Containment môže block-nuť audience/caller, revoke-nuť sessions/clients, zablokovať direct service path a disable-nuť risky MCP tools/registration. Recovery nasadí successor policy/config, shortens/invalidates descendants podľa scope-u a vykoná cross-service/cross-tenant negative tests.

## 31. Acceptance matrix

Positive:

```text
intended client/token/audience
→ API/MCP validation
→ local tenant/resource/tool permission
→ one business effect
```

Recovery:

```text
key/policy/client rotation alebo stolen token
→ bounded stale window/revocation
→ JWKS/introspection/cache convergence
→ second operation succeeds only s successor credential
```

Forbidden:

```text
ID/refresh/wrong-issuer/wrong-audience/wrong-azp token
→ 401

valid token, wrong tenant/resource/action/tool
→ 403/404 podľa policy

direct service request so spoofed gateway header
→ mTLS/network/token gate rejects

MCP newer profile declared fully compliant bez RFC 8707
→ architecture/release review rejects
```

Second-service test replayne token voči adjacent API. Second-tenant test používa rovnakú role nad foreign resource. Second-MCP test skúsi wrong audience, unregistered tool, malicious CIMD URL a duplicate high-risk operation.

## Kontrolné otázky

- Validuje každá služba issuer, signature, time, token type, audience a caller?
- Je ID/refresh token explicitne odmietnutý na API?
- Kde je final tenant/resource/action authorization?
- Je gateway assertion cryptographically/network-bound a direct path blokovaný?
- Aká je maximum stale authorization window pri local JWT?
- Sú JWKS refresh a introspection cache bounded a failure-safe?
- Používa M2M exact service account a service-specific audience?
- Zužuje token exchange audience/scope a zachováva actor context?
- Ktorú MCP version implementujeme a aký je presný Keycloak conformance status?
- Validuje MCP server exact audience, scopes a tool/resource/prompt policy?
- Je CIMD/DCR metadata fetch chránený pred SSRF a broad registration?
- Prešli wrong-token-type, cross-service, cross-tenant, direct-path, key-rotation, MCP audience a duplicate-tool tests?

## Primárne zdroje

- [Keycloak — Securing applications and services with OpenID Connect](https://www.keycloak.org/securing-apps/oidc-layers)
- [Keycloak — Authorization Services Guide](https://www.keycloak.org/docs/latest/authorization_services/)
- [Keycloak — Integrating with Model Context Protocol](https://www.keycloak.org/securing-apps/mcp-authz-server)
- [RFC 7519 — JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519.html)
- [RFC 8414 — OAuth 2.0 Authorization Server Metadata](https://www.rfc-editor.org/rfc/rfc8414.html)
- [RFC 8707 — Resource Indicators for OAuth 2.0](https://www.rfc-editor.org/rfc/rfc8707.html)
- [RFC 9728 — OAuth 2.0 Protected Resource Metadata](https://www.rfc-editor.org/rfc/rfc9728.html)
- [RFC 9700 — Best Current Practice for OAuth 2.0 Security](https://www.rfc-editor.org/rfc/rfc9700.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Custom providers, SPI a extension lifecycle](custom-providers-spi-extension-lifecycle.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Keycloak performance, sizing a load testing →](keycloak-performance-sizing-load-testing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
