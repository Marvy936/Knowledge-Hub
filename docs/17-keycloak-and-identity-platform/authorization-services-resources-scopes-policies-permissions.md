# Authorization Services, resources, scopes, policies a permissions

Keycloak Authorization Services nie sú rozšírený zoznam roles v access tokene. Ide o samostatný fine-grained authorization model naviazaný na konkrétny OIDC client, ktorý vystupuje ako resource server. Resource server registruje chránené resources a scopes, platforma vytvára reusable policies, permissions viažu resources/scopes na policy set a Policy Decision Point vyhodnotí request v identity a runtime context-e. Výsledok musí nakoniec vynútiť Policy Enforcement Point v aplikácii alebo API.

Najčastejší omyl je považovať successful Policy Evaluation v Admin Console za dôkaz, že produkčný request je chránený. Evaluation môže používať iného usera, clienta, claims alebo context. Resource server môže mať enforcement vypnutý, cacheovať staré rozhodnutie, mapovať URI na nesprávny resource alebo po deny pokračovať v business mutation. Authorization acceptance preto musí spájať exact resource-server generation, requested resource/scope, policy inputs, PDP decision, PEP behavior a business side effect.

## 1. Dominantný protected-request lifecycle

```text
business operation a protected object
→ exact Keycloak resource-server client generation
→ resource identity/type/owner/URI a requested scope
→ permission lookup
→ associated policy graph a decision strategies
→ identity, claims, roles, groups, time a runtime context
→ PDP evaluation a grant/deny verdict
→ permission response, RPT alebo entitlement data
→ application-side PEP enforcement
→ authoritative business mutation/read-back
→ policy change, cache invalidation a second-request validation
```

Authorization server rozhoduje podľa modelu, ktorý pozná. Resource server stále vlastní real object identity, tenant, current state, operation idempotency a enforcement. Keycloak resource `invoice:771` nemôže samo preukázať, že HTTP path alebo database row naozaj reprezentuje invoice 771.

## 2. Exact authorization subject

```yaml
authorizationSubject:
  keycloak:
    deploymentGeneration: kc-2026-08-02-13
    realm: atlas-prod
  resourceServer:
    clientId: settlement-api
    clientUuid: 31bf...
    resourceServerId: 31bf...
    authorizationRevision: authz-88
    decisionStrategy: UNANIMOUS
    policyEnforcementMode: ENFORCING
    allowRemoteResourceManagement: false
  resource:
    id: 2e97...
    name: settlement-record-771
    type: urn:atlas:settlement-record
    owner: service-account-settlement-api
    uris: [/tenants/orion/settlements/771]
    scopes: [view, export, reconcile]
    attributes:
      tenant: [orion]
      classification: [restricted]
  permission:
    id: 36cc...
    name: export-settlement-record
    type: scope
    scopes: [export]
    policies: [orion-export-role, fresh-gold-auth, business-hours]
    decisionStrategy: UNANIMOUS
  requester:
    userId: 4b8e...
    clientId: settlement-admin-web
    tokenJti: 17aa...
    tenant: orion
    acr: gold
  request:
    method: POST
    path: /tenants/orion/settlements/771/export
    operationId: export-771-991
    runtimeContextRevision: ctx-58
```

Human-readable resource alebo policy name nie je stable subject. Export/import môže recreate interné IDs. Client `clientId` a internal client UUID sú odlišné. Resource owner môže byť user alebo resource-server client. Incident evidence zachová IDs, names, policy/permission export hash a exact request context.

## 3. PAP, PDP, PEP a PIP

Authorization Services rozdeľujú administration, rozhodovanie, dodanie contextu a enforcement medzi štyri odlišné responsibility boundaries. Toto rozdelenie je dôležité pri dokazovaní incidentu: správna policy uložená cez PAP ešte nepreukazuje, že PDP načítal intended generation; správny PDP deny nepreukazuje, že PEP zastavil handler; complete identity token nepreukazuje, že PIP dodal current object ownership alebo transaction amount.

**Policy Administration Point (PAP)** spravuje resources, scopes, policies a permissions cez Admin Console, Admin REST alebo Protection API. Jeho výstupom je desired authorization graph s konkrétnymi internal IDs a references. **Policy Decision Point (PDP)** tento graph vyhodnotí pre exact subject, client, resource, scopes a context a vytvorí grant, deny alebo error verdict. PDP nevykonáva business mutation a nepozná automaticky current database object, pokiaľ ho request/PIP neposkytne.

**Policy Information Point (PIP)** dodáva policy inputs ako token claims, user/group/role state, pushed claims, time alebo application context. Každý input potrebuje authority a freshness; client-supplied tenant claim nie je automaticky trusted. **Policy Enforcement Point (PEP)** mapuje reálny HTTP alebo business request na resource/scopes, získa alebo validuje decision a musí zastaviť handler pred side effectom pri deny alebo neprijateľnom error-e. PEP je preto posledný security writer boundary, nie iba logging middleware.

```text
PAP desired policy generation
→ PDP loaded evaluation model
+ PIP identity/context
→ decision
→ PEP enforcement
→ business outcome
```

Centralizovaný PDP nezbavuje aplikáciu PEP zodpovednosti. Ak API iba loguje deny alebo interpretuje timeout ako allow, model je fail-open bez ohľadu na správnosť Keycloak policy.

## 4. Resource server

Authorization Services sa enable-nú na confidential OIDC clientovi reprezentujúcom protected API/service. Tým vznikne resource-server configuration s policies, permissions, resources, scopes a Protection API credentials/capabilities.

Client používaný browser UI nemá automaticky byť resource server. Oddelenie `settlement-admin-web` a `settlement-api` drží redirect/session capabilities mimo resource registration a PAT credentialu. Resource-server client má minimal grants; service account/PAT sa používa iba pre Protection API, ak remote management potrebujeme.

Resource-server settings zahŕňajú policy enforcement mode, decision strategy, remote resource management a token/permission behavior. Export configuration je source artifact, no loaded IDs a runtime behavior sa read-backnú po importe.

## 5. Resources

Resource je objekt alebo class objektov, ktorý API chráni. Môže reprezentovať jeden settlement record, celý resource type, endpoint collection alebo user-owned asset.

```text
resource type urn:atlas:settlement-record
→ common policy pre všetky records

resource settlement-record-771
→ instance owner, tenant a attributes
→ instance-specific permission alebo user-managed sharing
```

URI je routing hint, nie stable business identity. Dynamic `/settlements/{id}` mapping musí canonicalizovať path, method a tenant; prefix alebo wildcard overlap môže priradiť wrong resource. Resource attributes sú policy inputs a potrebujú authority, type a update lifecycle.

Resource owner môže byť user alebo resource-server client. Owner-based policy musí overiť, že application registration a actual database ownership zostávajú synchronizované. Delete business objectu má odstrániť alebo tombstone-nuť Authorization Services resource, aby stale permission ticket neodkazoval na reused ID.

## 6. Scopes

Authorization scope opisuje action alebo bounded aspect chráneného resource-u: `view`, `export`, `reconcile`, `approve`. Nie je totožný s OAuth requested scope stringom ani Keycloak client scope objectom.

```text
OAuth scope
→ delegated token request vocabulary

Keycloak client scope
→ reusable protocol mappers a role-scope configuration

Authorization Services scope
→ action alebo data facet nad protected resource
```

Resource môže podporovať iba subset scopes. API route `POST /export` sa musí mapovať na `export`, nie všeobecné `write`. Scope names majú stable business semantics a versioning; zmena `approve` na `approve-high-value` je policy migration, nie iba rename.

## 7. Policies

Policy definuje conditions nezávisle od konkrétneho resource bindingu. Built-in providers podporujú role, user, group, client, time, aggregate a ďalšie conditions; custom policy provider SPI môže pridať domain logic.

```text
policy fresh-gold-auth
→ acr == gold
AND auth_time <= 300 seconds

policy orion-export-role
→ requester tenant == orion
AND client role settlement-api.export
```

Policy source fields musia byť authoritative. Token claim `tenant=orion` pochádzajúci z user-editable attribute nie je bezpečný PIP. Time policy potrebuje timezone a boundary semantics. JavaScript/custom policy môže zvýšiť latency a code-execution blast radius; provider JAR a policy config sú dve generations.

## 8. Aggregated policies a logic

Aggregated policy skladá ďalšie policies. Positive alebo negative logic a decision strategy menia výsledok. Negated policy nie je jednoduchý textový `NOT`; treba presne testovať absent input, error a abstain behavior.

```text
aggregate privileged-export
UNANIMOUS:
  - role policy export-role
  - group policy settlement-team
  - time policy business-hours
  - context policy fresh-gold-auth
```

Cyclic policy references musia byť odmietnuté alebo auditované. Deep graph komplikuje troubleshooting a môže vytvoriť unexpected affirmative path. Policy inventory má resolved dependency graph a ownera každého node-u.

## 9. Permissions

Permission spája protected object s policies. Resource-based permission chráni resources alebo resource type. Scope-based permission chráni scopes, voliteľne v rámci konkrétneho resource-u.

```text
resource permission
resources/type Z
+ policies P1,P2
→ access k resource ako celku

scope permission
resource Z + scopes export
+ policies P1,P3
→ export action nad Z
```

Policy bez permission sa nevyhodnotí pre resource. Permission bez intended resource/scope môže byť broad. Typed resource permission aplikuje policy na všetky resources určitého type-u, vrátane budúcich; creation lifecycle preto musí garantovať correct type a attributes.

## 10. Decision strategies

Decision strategy určuje, ako sa jednotlivé policy outcomes skombinujú do permission verdictu. Nie je to kozmetické nastavenie: rovnaké tri policies nad rovnakým userom môžu pri odlišnej strategy vydať opačný výsledok. Test fixture preto musí zachovať outcomes každého policy node-u aj final strategy na permission a resource-server úrovni.

**UNANIMOUS** vyžaduje positive result všetkých relevantných policies. Je vhodná tam, kde role, tenant ownership, authentication freshness a time window tvoria súčasne povinné preconditions; jeden deny alebo nesplnená podmienka zastaví grant. **AFFIRMATIVE** povolí, ak aspoň jedna policy grantne. Je bezpečná iba vtedy, keď policies reprezentujú skutočne alternatívne rovnocenné authority paths; broad role policy by inak prebila tenant alebo freshness deny. **CONSENSUS** vyžaduje viac positive než negative decisions a pri zhode výsledok deny-ne. Počet policies a ich abstain/error semantics preto priamo menia outcome.

Strategy je súčasť permission aj resource-server graphu a treba ju testovať na complete truth table, nie iba intended positive userovi. Pridanie novej policy môže pri CONSENSUS zmeniť majority a pri AFFIRMATIVE vytvoriť nový bypass, aj keď existujúce policies zostali bez zmeny.

## 11. Evaluation context

PDP môže dostať identity information z subject tokenu a contextual claims cez authorization request. Context zahŕňa client, roles/groups, token claims, requested resource/scope a pushed claims.

Pushed claim nie je automaticky trusted. Resource server alebo client môže poslať `tenant=orion`, ale policy musí vedieť, kto claim vytvoril a či ho Keycloak overil. High-risk data ako object owner alebo transaction amount má často zostať v resource serveri a Keycloak decision byť iba jednou authorization vrstvou.

Admin Console Policy Evaluation je design tool. Musí zachovať simulated user/client/roles/claims/resources/scopes a porovnať ho s actual token a production request. Simulation success nie je runtime PEP evidence.

## 12. Protection API a PAT

Protection API umožňuje resource serveru spravovať resources a permission tickets. Resource server získava Protection API Token (PAT), typicky service-account access token so scope `uma_protection`.

```text
resource-server client authentication
→ PAT s uma_protection
→ Protection API create/update/delete resource
→ resource ID read-back
```

PAT je high-privilege machine credential. Nemá byť v browseri ani zdieľaný s unrelated automation. `Allow Remote Resource Management=false` obmedzí resource changes na Admin Console/API authority. Pri dynamic user-owned resources môže remote management byť potrebný, no operation IDs a database/resource consistency sú povinné.

Create timeout má unknown outcome. Retry najprv queryne resource podľa durable external ID attribute; nevytvorí duplicate iba s novým random name.

## 13. Permission tickets a UMA

UMA flow môže začať requestom bez dostatočného RPT. Resource server vytvorí permission ticket reprezentujúci resource/scopes a vráti `401` s UMA challenge. Client ticket pošle token endpointu s UMA grantom; Keycloak vyhodnotí policies a vydá RPT alebo deny.

```text
client → resource server bez permission
→ resource server Protection API permission ticket
→ 401 WWW-Authenticate UMA + ticket
→ client token endpoint uma-ticket grant
→ PDP evaluates requested resource/scopes
→ RPT s granted permissions alebo 403
→ retry resource request
→ PEP validates/enforces RPT
```

Permission ticket je short-lived authorization request artifact, nie permission samo. RPT je access token s permission data. Resource server stále validuje issuer, signature, lifetime, audience a exact granted resource/scope.

## 14. Requesting Party Token

RPT môže obsahovať `authorization.permissions` s resource IDs/names a scopes. Token je snapshot policy decision. Policy alebo resource change nemusí okamžite zmeniť už vydaný RPT.

```json
{
  "aud": "settlement-api",
  "authorization": {
    "permissions": [
      {
        "rsid": "2e97...",
        "rsname": "settlement-record-771",
        "scopes": ["view", "export"]
      }
    ]
  }
}
```

API nesmie authorizovať podľa `rsname` bez stable ID/object bindingu. Resource ID reuse alebo stale registration môže povoliť wrong object. Token revocation/short lifetime/current decision strategy musí zodpovedať policy-change latency.

## 15. Entitlement a direct permission request

Client môže requestovať permissions priamo na token endpoint-e pomocou UMA grant parameters a existing access tokenu. Depending on request môže dostať RPT s subsetom permissions alebo denial.

```bash
curl --fail --silent --show-error \
  --request POST \
  --header "Authorization: Bearer ${SUBJECT_TOKEN}" \
  --data-urlencode 'grant_type=urn:ietf:params:oauth:grant-type:uma-ticket' \
  --data-urlencode 'audience=settlement-api' \
  --data-urlencode 'permission=2e97...#export' \
  'https://sso.atlas.example/realms/atlas-prod/protocol/openid-connect/token' \
  | jq '{token_type,expires_in,access_token}'
```

HTTP 200 preukazuje token issuance. Nepreukazuje, že API enforce-ne permission, že resource ID zodpovedá URL/database row ani že business export bol idempotentný.

## 16. Policy Enforcement Point

PEP môže byť Keycloak policy enforcer library, API gateway filter alebo application code. Musí mapovať request na resource/scopes, získať/validovať decision alebo RPT, fail-closed pri erroroch a zastaviť business handler pred mutation.

```text
HTTP request
→ authentication/token validation
→ canonical resource ID a scope mapping
→ authorization decision/cache
→ deny: handler not called
→ allow: business preconditions a idempotent mutation
→ audit result
```

Route matcher default resource môže nechtiac pokryť unknown endpoints. Enforcement mode `PERMISSIVE` alebo disabled sa používa iba pri staged observation s explicitným deadline-om; nie ako trvalý production state.

## 17. Decision a entitlement caching

PEP môže cacheovať resource metadata, policy decisions alebo RPT. Cache key musí zahŕňať user/subject, client, tenant, resource ID, scopes, policy generation a relevant context. Key iba podľa route alebo role spôsobí privilege bleed.

TTL určuje revocation latency. Policy publish potrebuje cache invalidation alebo versioned key. Failover/Keycloak outage contract rozhoduje fail-closed versus bounded stale allow pre konkrétne low-risk operations; broad fail-open je forbidden.

## 18. Export, import a versioning

Authorization configuration sa dá exportovať/importovať cez resource-server Admin API. Artifact obsahuje resources, scopes, policies a permissions, ale internal IDs a references sa môžu pri importe zmeniť.

```bash
CLIENT_UUID='31bf...'

curl --fail --silent --show-error \
  --header "Authorization: Bearer ${ADMIN_TOKEN}" \
  "https://sso-admin.atlas.example/admin/realms/atlas-prod/clients/${CLIENT_UUID}/authz/resource-server" \
  | jq -S . > settlement-api-authz.json

sha256sum settlement-api-authz.json
```

Promotion používa reviewed artifact, semantic validation a post-import read-back. Import `204 No Content` nepreukazuje final resolved graph ani runtime PEP. Drift report porovná source generation, loaded resource-server export a policy evaluation fixtures.

## 19. Admin REST inventory a evaluation

Resource server, resources, scopes, policies a permissions majú Admin REST endpoints pod client UUID. Automation musí resolve-nuť `clientId` na unique internal UUID a zachovať realm/base URL.

```bash
CLIENT_UUID="$({
  kcadm.sh get clients \
    -r atlas-prod \
    -q clientId=settlement-api \
    --fields id,clientId
} | jq -er 'if length == 1 then .[0].id else error("ambiguous client") end')"

kcadm.sh get "clients/${CLIENT_UUID}/authz/resource-server/resource" \
  -r atlas-prod \
  | jq '[.[] | {_id,name,type,ownerManagedAccess,uris,scopes}]'
```

List output môže byť paginated alebo permission-filtered podľa endpoint. Completeness evidence zahŕňa expected counts, pagination a references. Policy evaluation API testuje exact request fixture, ale stále nie PEP/business outcome.

## 20. Connected incident `KC-PAY-68` — stale PIP a broad affirmative policy

Atlas `settlement-api` registroval resource type `urn:atlas:settlement-record`. Permission `export-settlement` používala AFFIRMATIVE strategy nad policies `export-role`, `same-tenant` a `fresh-gold-auth`. Broad client role teda stačila aj keď tenant alebo authentication freshness zlyhali.

Custom user-storage provider navyše cacheoval stale `tenant=orion`. PEP cache key používal iba route `/settlements/*/export` a user ID, nie resource ID, scope, policy generation ani tenant. Po prvom allow pre record 771 reuse-ol decision pre record 992 iného tenant-a. Admin Console evaluation nad fresh attributes ukazovala deny, ale runtime PEP používal stale cache.

```text
stale PIP tenant
+ AFFIRMATIVE permission
+ broad export role
→ PDP grant
→ PEP cache bez resource/tenant generation
→ decision reused pre adjacent record
→ cross-tenant export
```

## 21. Evidence-preserving containment a recovery

Zachovaj resource-server export/hash, client UUID, resource/scope/permission/policy IDs, decision strategies, policy inputs, actual token/RPT hash a permissions, PEP route mapping/cache key/value, Keycloak event/log correlation a business operation IDs. Sensitive token body sa uchováva obmedzene alebo ako sanitized claims/hash.

Containment vypne export action alebo invalidate-ne exact PEP decision cohort, revoke-ne affected tokens/RPT a blokne cross-tenant requests. Recovery zmení strategy na UNANIMOUS, opraví PIP authority a cache key, importuje successor policy graph, read-backne IDs/references a vykoná positive, adjacent-tenant, stale-token a second-resource tests.

## 22. Positive, recovery a forbidden acceptance

Acceptance musí odlíšiť policy design, PDP decision, token/permission artifact a resource-server enforcement. Positive verdict dokazuje intended resource/scope a business operation; recovery navyše uzatvára stale decisions/RPT; forbidden paths dokazujú, že missing context, adjacent tenant a PEP outage nevytvoria allow.

Positive path:

```text
user/client/tenant/resource context correct
→ UNANIMOUS policies grant export scope
→ RPT/decision contains exact resource ID
→ PEP maps same business object
→ export succeeds once
```

Forbidden paths:

```text
same role, wrong tenant
→ same-tenant policy denies

acr stale alebo absent
→ freshness policy denies

right user, adjacent resource without permission
→ deny

Keycloak/PDP timeout bez approved stale-low-risk rule
→ fail closed

policy updated, old cached allow/RPT reused
→ recovery acceptance fails

Admin evaluation grant, PEP disabled
→ production acceptance fails
```

## 23. Troubleshooting

Pri unexpected allow/deny začni exact resource ID, scope a permission graph. Read-backni policy references a decision strategies, potom actual identity/context claims a evaluation result. Následne over PEP URI/resource mapping, cache key/generation a handler behavior.

Pri UMA flowe oddeľ PAT/Protection API, permission ticket creation, token endpoint evaluation, RPT contents a retry enforcement. `403 request_denied` môže znamenať policy deny, missing resource/scope, wrong audience alebo invalid ticket; potrebuje correlation s exact request.

## 24. Kontrolné otázky

- Ktorý client UUID/resource-server generation vlastní authorization model?
- Ktorý stable business object reprezentuje resource ID a URI?
- Rozlišujeme OAuth scope, client scope a Authorization Services scope?
- Ktoré policies sú reusable a ktoré permission ich viaže na resource/scope?
- Aká decision strategy platí na každej úrovni?
- Kto je authority pre PIP claims a runtime context?
- Ako PEP mapuje request, failuje a cacheuje decision?
- Ako sa revoke-nú stale RPT/decisions po policy alebo ownership zmene?
- Prešli wrong tenant, adjacent resource, missing context, PDP outage a second-request paths?

## Glossary impact

Relevantné pojmy: Keycloak Authorization Services, resource server, resource, authorization scope, policy, permission, PAP, PDP, PEP, PIP, decision strategy, Protection API, PAT, permission ticket, UMA, RPT, policy evaluation context, owner-managed access, entitlement, decision cache a authorization-generation acceptance.

## Primárne zdroje

- [Keycloak — Authorization Services Guide](https://www.keycloak.org/docs/latest/authorization_services/)
- [Keycloak — Admin REST API: Authorization resources](https://www.keycloak.org/docs-api/latest/rest-api/index.html)
- [RFC 9396 — OAuth 2.0 Rich Authorization Requests](https://www.rfc-editor.org/rfc/rfc9396.html)
- [UMA 2.0 Grant for OAuth 2.0 Authorization](https://docs.kantarainitiative.org/uma/rec-oauth-uma-grant-2.0.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: User storage, synchronization a cache semantics](user-storage-synchronization-cache-semantics.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Token exchange, impersonation a delegated access →](token-exchange-impersonation-delegated-access.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
