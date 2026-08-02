# Token exchange, impersonation a delegated access

Token exchange v Keycloak-e nie je univerzálny endpoint, ktorý ľubovoľný token premení na ľubovoľnú identitu. Aktuálny podporovaný Standard Token Exchange V2 implementuje interný-to-interný exchange v rovnakom realm-e: client s povolenou capability predloží existujúci Keycloak access token a requestne nový token pre inú audience alebo užší client context. Legacy Token Exchange V1 je preview a deprecated; pokrýva historické external-token a impersonation use cases, ale nemá rovnaký support a future-compatibility contract.

External-to-internal trust sa má riešiť podporovaným JWT Authorization Grantom a identity-provider trust configuration, prípadne v identity-chaining flowe kombináciou JWT grantu a Standard Token Exchange. Internal-to-external access používa identity-brokering token APIs. Admin impersonation je samostatná administratívna session mutation. Ak tieto mechanizmy spojíme do jedného „delegated access“ pojmu, stratíme actor, subject, target audience, grant authority a revocation chain.

## 1. Dominantný subject-token-to-target-token lifecycle

Token exchange vytvára nový credential subject, nie iba nový encoding predecessor tokenu. Requester client musí byť autorizovaný spracovať subject token, target client musí vytvoriť vlastný scope/mapper projection a successor token má samostatný audience, lifetime, session a revocation contract. Lifecycle sa preto číta ako transition medzi dvoma token generations a jednou business operation, nie ako jednoduché „forwardovanie usera“.

Najdôležitejšie je zachovať tri identities: user alebo workload subject, requester/acting client a target resource server. Ak successor token ponechá iba `sub` a API ignoruje acting client, confused-deputy alebo overbroad service môže vykonať operáciu, ktorú user context sám nevysvetľuje. Ak retry vytvorí dva successor tokens, credential duplication nesmie vytvoriť dva business side effects; operation idempotency patrí do downstream API.

```text
originating user alebo workload a business intent
→ exact subject token issuer/session/client/audience/scope generation
→ requester client authentication a token-exchange capability
→ exchange request type, audience, scopes a requested token type
→ Keycloak subject-token validation a requester authorization
→ target client scope/mapper/session evaluation
→ successor access alebo refresh token
→ target resource-server validation
→ actor/subject/resource/action authorization
→ revocation, expiry, retry a second-exchange validation
```

Exchange success dokazuje iba issuance successor tokenu. Nedokazuje, že target API akceptuje správnu audience, že scopes sú downscoped, že actor chain je zachovaný ani že predecessor token revocation automaticky zruší všetky access-token descendants.

## 2. Exact exchange subject

```yaml
tokenExchangeSubject:
  keycloak:
    deploymentGeneration: kc-2026-08-02-13
    realm: atlas-prod
    issuer: https://sso.atlas.example/realms/atlas-prod
    tokenExchangeImplementation: standard-v2
  requesterClient:
    clientId: settlement-orchestrator
    internalId: 13c4...
    configurationRevision: client-231
    standardTokenExchangeEnabled: true
    authenticationMethod: private_key_jwt
    keyGeneration: key-29
  subjectToken:
    tokenHash: sha256:...
    jti: 17aa...
    sub: 4b8e...
    azp: settlement-admin-web
    audiences: [settlement-orchestrator]
    scopes: [openid, profile, settlement.read]
    sessionId: 04d9...
    issuedAt: 2026-08-02T06:11:00Z
    expiresAt: 2026-08-02T06:16:00Z
  request:
    grantType: urn:ietf:params:oauth:grant-type:token-exchange
    subjectTokenType: urn:ietf:params:oauth:token-type:access_token
    requestedTokenType: urn:ietf:params:oauth:token-type:access_token
    audience: settlement-api
    requestedScopes: [settlement.reconcile]
    operationId: exchange-771
  successorToken:
    jti: 81bf...
    audience: settlement-api
    authorizedParty: settlement-orchestrator
    subject: 4b8e...
    scopes: [settlement.reconcile]
    exchangeGeneration: exchange-882
```

`sub` identifikuje subject identity, `azp` alebo client claim identifikuje authorized party podľa token profile, audience identifikuje intended resource server. Requester client, originating client a target audience môžu byť tri odlišné entities. Incident evidence musí zachovať všetky tri.

## 3. Standard Token Exchange V2

Standard V2 je podporovaná a default-enabled server feature, ale konkrétny requester client musí mať zapnutú `Standard Token Exchange` capability. Podporovaný core use case je Keycloak internal access token → nový internal token v rovnakom realm-e.

```text
Keycloak subject token pre service1/requester
→ authenticated requester service1
→ audience=service2
→ target client scopes a mappers
→ service2 access token
```

Typický design drží initial frontend token bez audience `service2`. Frontend ho pošle service1; service1 je audience subject tokenu a môže ho exchange-nuť na service2-specific token. Frontend tak nevie priamo volať service2 iba preto, že user má relevantnú role.

## 4. Requester authorization

Standard V2 overuje, že requester client je oprávnený exchange vykonať. Základná boundary je, že requester musí byť audience subject tokenu; inak by ľubovoľný client, ktorý token získa, mohol mintovať descendants.

Client Policies môžu ďalej obmedziť requester, target, scopes alebo ďalšie request vlastnosti. Capability switch nie je globálna permission na všetky target clients. Negative matrix zahŕňa requester absent z `aud`, disabled exchange capability, wrong realm, public/unauthenticated requester a unauthorized target/scope.

## 5. Exchange request

```bash
curl --fail --silent --show-error \
  --request POST \
  --user "settlement-orchestrator:${CLIENT_SECRET}" \
  --data-urlencode 'grant_type=urn:ietf:params:oauth:grant-type:token-exchange' \
  --data-urlencode "subject_token=${SUBJECT_TOKEN}" \
  --data-urlencode 'subject_token_type=urn:ietf:params:oauth:token-type:access_token' \
  --data-urlencode 'requested_token_type=urn:ietf:params:oauth:token-type:access_token' \
  --data-urlencode 'audience=settlement-api' \
  --data-urlencode 'scope=settlement.reconcile' \
  'https://sso.atlas.example/realms/atlas-prod/protocol/openid-connect/token' \
  | jq '{issued_token_type,token_type,expires_in,scope,refresh_expires_in}'
```

Secret v príklade reprezentuje chránený runtime secret source, nie literal command-line history. Produkčný requester preferuje asymmetric alebo workload-bound client authentication. HTTP 200 je len issuance evidence; successor JWT sa decode-ne/validuje a použije proti intended aj adjacent API.

## 6. Subject token

Subject token musí byť validný Keycloak token expected type-u, issueru, času a session/policy contextu. Lightweight access token môže byť exchange-nutý na full token iba ak required audience information zostáva v lightweight token-e; audience mapper musí byť configured aj pre lightweight surface.

Sender-constrained tokens majú extra proof boundary. mTLS certificate-bound token sa podľa current Standard Exchange limitations nepoužíva ako subject token. DPoP-bound token môže byť podporovaný iba pri splnení DPoP proof a `cnf.jkt` contractu. Bearer-token príklad sa nemá mechanicky aplikovať na holder-of-key token.

## 7. Audience a target client

`audience` request parameter vyberá target client/resource server. Target token claims vznikajú z target client scopes, role scope mappings, protocol mappers a requested scopes; nejde o jednoduché prepísanie `aud` v predecessor token-e.

```text
subject identity a effective roles
∩ requester/exchange policy
∩ target client scope mappings
∩ requested scope
→ successor token claims
```

Target client má byť resource-server registration alebo client s jasným consumer contractom. Exchange na browser clienta s redirects a broad scopes je design smell. API validuje target audience a podľa potreby requester/actor claim, nie iba user subject.

## 8. Downscoping a privilege amplification

Exchange je bezpečný iba ak successor permissions zodpovedajú target operation. Requester nesmie získať role/scope, ktoré subject ani exchange policy neoprávňujú. Broad target default scopes alebo `Full Scope Allowed` môžu successor token rozšíriť.

Downscope acceptance porovná predecessor a successor fixtures:

```text
predecessor: aud orchestrator, scopes settlement.read
requested: aud settlement-api, scope settlement.reconcile
expected successor: only reconcile subset approved by policy
forbidden: export/admin/unrelated tenant claims
```

Exchange nemusí byť monotonic subset vo všetkých claim dimensions, pretože target token má iný consumer schema. Každý novo pridaný claim má authority a consumer justification.

## 9. Access a refresh token descendants

`requested_token_type` môže podľa supported flowu requestnúť access alebo refresh semantics. Refresh token vytvára dlhšie žijúci descendant a session lifecycle. Standard V2 dokumentuje revocation chain pre refresh-token descendants, ale nie všeobecnú immediate access-token chain revocation.

```text
subject access token T1
→ exchanged access token T2
→ T1 revoked/expired
→ T2 behavior podľa vlastného expiry/revocation contractu
```

Incident response nesmie predpokladať, že predecessor access token revocation okamžite odstráni T2. Používa short lifetimes, session/not-before/revocation policy a target API enforcement. Refresh descendants sa inventarizujú samostatne.

## 10. Standard versus Legacy Token Exchange

Legacy V1 je preview, deprecated a disabled unless explicitly enabled. Pokrýva internal-to-external, external-to-internal a subject impersonation use cases, ale používa odlišné permission modely a vyžaduje legacy Fine-Grained Admin Permissions V1 pre niektoré exchange permissions.

```text
Standard V2
→ supported
→ internal Keycloak token to internal Keycloak token
→ RFC 8693-oriented parameters
→ Client Policies a requester audience checks

Legacy V1
→ preview/deprecated
→ historical external/internal/impersonation cases
→ non-standard parameters ako requested_issuer/requested_subject
→ migration required
```

Ak sú oba features enabled, request parameters môžu určiť, ktorý implementation path request spracuje. Monitoring a acceptance preto zachovajú exact request parameter set a server feature generation.

## 11. External-to-internal: JWT Authorization Grant

Moderný external-to-internal flow používa JWT Authorization Grant podľa RFC 7523. Confidential client predloží external signed JWT assertion token endpointu s `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer`. Keycloak trustuje configured IdP/JWT grant authority, validuje issuer, signature, audience, time a mapping a vydá internal token.

```text
external issuer JWT assertion
→ configured external trust/IdP generation
→ requester client authentication a allowed provider
→ JWT Authorization Grant validation
→ local identity/link/mapping
→ Keycloak internal access token
```

V cross-domain chain-e môže Domain A najprv použiť Standard Token Exchange na audience-specific assertion/token, ktorý Domain B prijme cez JWT Authorization Grant. Každý realm má vlastný issuer, client a mapping authority. Preview/support status konkrétnej JWT grant generation sa musí overiť pri použitom Keycloak release.

## 12. Internal-to-external access

Ak aplikácia potrebuje upstream provider token pre linked identity, používa identity-brokering token retrieval API a `Store Tokens`/read-token permission contract. Nie je to Standard V2 target audience exchange.

Stored upstream token má vlastný issuer, scopes, refresh a revocation lifecycle. Local Keycloak logout ani exchange token expiry nemusia revoke-nuť upstream grant.

## 13. Impersonation

Impersonation mení subject identity. Standard Token Exchange V2 subject impersonation aktuálne nepodporuje. Legacy V1 historicky používa `requested_subject`, ale je preview/deprecated a nemá byť default production delegation model.

Admin Console/Admin REST impersonation je samostatná administratívna capability. Oprávnený administrator vytvorí session ako target user; audit musí zachovať admin actor, target user, initiating realm/client, session ID, time, reason a business operations. Impersonated session nesmie skryť actor identity iba preto, že access token `sub` je target user.

```text
admin actor A
→ explicit impersonation permission
→ target user U
→ impersonated Keycloak session S
→ downstream request
→ audit A acted as U
```

High-risk APIs môžu impersonated sessions odmietnuť alebo vyžadovať additional approval. Helpdesk troubleshooting nemá automaticky znamenať settlement authorization.

## 14. Delegated access a actor chain

Delegation znamená, že service actor koná v kontexte user subjectu bez zmeny na inú osobu. Secure token potrebuje odlíšiť:

```text
subject
→ človek alebo workload, ktorého authority sa používa

actor
→ client/service vykonávajúci aktuálny hop

audience/resource
→ intended recipient

scope/authorization details
→ čo je delegované
```

Aktuálne Keycloak verzie môžu mať experimentálnu Token Exchange Delegation podporu. Experimental feature sa nepovažuje za stabilný production contract bez pinned release, explicitného feature flagu, interoperability testu a migration planu. Bez actor semantics API aspoň validuje `azp`/requester client a operation-specific delegation policy.

## 15. Cross-domain identity chaining

Distributed chain môže kombinovať external JWT Authorization Grant a internal Standard Token Exchange. Každý hop minimalizuje audience/scopes a zachová original subject + current actor podľa supported token profile.

```text
user in Domain A
→ Domain A access token for service A
→ Standard exchange to cross-domain audience
→ signed assertion presented to Domain B JWT grant
→ Domain B token for service B
→ optional internal exchange for downstream service C
```

Chain length zvyšuje revocation, observability a confused-deputy risk. Každý service overuje issuer, audience, actor, subject, tenant, action a chain depth/context. Generic service account replacing user subject destroys traceability.

## 16. Retry a idempotency

Token exchange je credential issuance; business operation je samostatná mutation. Retry exchange po timeout-e môže vytvoriť viac valid successor tokens. To nemusí byť problém, ale downstream operation musí používať durable operation ID.

```text
exchange request E-771 timeout
→ outcome unknown
→ retry môže vydať T2b
→ both T2a/T2b potentially valid
→ business operation deduped by operationId O-991
```

Do not use token `jti` as business idempotency key. Každý retry token má iné `jti`, hoci vykonáva rovnakú operation.

## 17. Connected incident `KC-PAY-68` — broad exchange a lost actor context

`settlement-orchestrator` dostal frontend token s audience orchestrator. Client mal Standard Token Exchange enabled a target `settlement-api` broad default scopes. Exchange requestoval iba audience, bez explicitného scope; successor token získal `settlement.export` aj `settlement.reconcile`.

API validovalo `sub` usera a target audience, ale ignorovalo requester/actor client. Orchestrator retryol exchange po timeout-e a vytvoril dva valid tokens; oba použil s odlišným business operation ID. Custom authorization cache ešte obsahoval stale tenant entitlement.

```text
valid frontend subject token
→ requester orchestrator authorized exchange
→ broad target scopes
→ successor token bez enforced actor/action boundary
→ duplicate tokens a duplicate business IDs
→ two exports
```

## 18. Evidence-preserving containment a recovery

Zachovaj server feature set, requester/target client IDs a revisions, client policies, subject/successor token hashes a sanitized claims, exchange request parameters, token endpoint events, session IDs, actor/subject/audience, downstream requests a operation IDs. Raw refresh tokens a client credentials sa neukladajú do incident reportu.

Containment vypne exchange capability alebo target action, revoke-ne relevant sessions/refresh descendants a blokne duplicate operations. Recovery explicitne nastaví target scopes, audience/requester checks, actor-aware API policy a durable operation ID; legacy V1 paths sa odstránia alebo izolujú s migration deadline-om.

## 19. Positive, recovery a forbidden acceptance

Acceptance musí odlíšiť requester authorization, successor token shape, actor/subject traceability a business idempotency. Positive path dokazuje intended target operation; recovery uzatvára stale/duplicate descendants; forbidden paths testujú wrong requester, target, scope, realm a impersonation.

Positive path:

```text
subject token aud includes orchestrator
→ authenticated orchestrator exchange
→ target settlement-api
→ minimal reconcile scope
→ API validates subject+actor+tenant+action
→ one operation succeeds
```

Forbidden paths:

```text
requester absent zo subject-token audience
→ exchange rejected

public/unautentizovaný requester
→ rejected

requested export scope mimo policy
→ denied alebo absent

wrong realm/external token cez Standard V2
→ rejected

requested_subject impersonation parameter
→ not processed by Standard V2

predecessor revoked, stale successor access token still accepted beyond policy
→ recovery acceptance fails

duplicate exchange tokens + same operationId
→ one business effect
```

## 20. Troubleshooting

Pri exchange failure oddeľ server feature/version, client capability, requester authentication, subject-token issuer/type/audience/time, request parameters, target client, Client Policies a target scope mappings. `invalid_target`, `invalid_client`, `invalid_grant` a `not_allowed` potrebujú exact request correlation.

Pri overprivileged successor token-e porovnaj target default/optional/dedicated scopes, role-scope mappings, requested `scope`, audience mappers a actual API policy. Pri legacy behavior over request parameters a enabled features; non-standard `requested_issuer/requested_subject` indikujú legacy path.

## 21. Kontrolné otázky

- Používa request podporovaný Standard V2 alebo deprecated Legacy V1?
- Ktorý requester client je audience subject tokenu a ako sa autentizuje?
- Ktorý target audience a scope sú requestnuté a prečo?
- Aké target mappers/role scopes vytvoria successor claims?
- Zachová API subject aj actor/requester identity?
- Aký je access/refresh descendant a revocation contract?
- Je external-to-internal riešený JWT Authorization Grantom namiesto legacy exchange?
- Je impersonation explicitná admin capability s actor auditom?
- Ako sa deduplikuje business operation pri exchange retry?
- Prešli wrong requester, wrong target, excess scope, stale descendant a second-exchange paths?

## Glossary impact

Relevantné pojmy: OAuth Token Exchange, Standard Token Exchange V2, Legacy Token Exchange V1, subject token, requested token type, requester client, target audience, successor token, exchange descendant, JWT Authorization Grant, identity chaining, actor, subject impersonation, admin impersonation, delegated access, downscoping a exchange operation idempotency.

## Primárne zdroje

- [Keycloak — Configuring and using token exchange](https://www.keycloak.org/securing-apps/token-exchange)
- [Keycloak — JWT Authorization Grant](https://www.keycloak.org/securing-apps/jwt-authorization-grant)
- [RFC 8693 — OAuth 2.0 Token Exchange](https://www.rfc-editor.org/rfc/rfc8693.html)
- [RFC 7523 — JWT Profile for OAuth 2.0 Authorization Grants](https://www.rfc-editor.org/rfc/rfc7523.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Authorization Services, resources, scopes, policies a permissions](authorization-services-resources-scopes-policies-permissions.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Admin Console, Admin REST API a automation →](admin-console-admin-rest-api-automation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
