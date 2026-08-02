# Admin Console, Admin REST API a automation

Keycloak administration nie je súbor formulárov a CRUD endpointov. Je to privilegovaný control-plane lifecycle, v ktorom konkrétny administrator alebo workload autentizovaný v konkrétnom realm-e vykonáva mutation nad presne identifikovaným target realmom a internal resource ID. Admin Console a Admin REST API sú dve používateľské surfaces nad rovnakým authorization modelom; úspešné kliknutie alebo HTTP `204` preukazuje prijatie requestu, nie správny target, complete mutation, loaded runtime generation ani business outcome.

Najčastejší automation incident vznikne spojením troch nepresností. Script sa autentizuje do `master` realm-u broad admin účtom, target realm určuje mutable environment variable a client vyhľadá iba podľa `clientId`, hoci mutation endpoint vyžaduje internal UUID. Pri timeout-e potom request slepo zopakuje alebo spustí partial import. Výsledkom môže byť duplicate, partial state alebo zmena rovnako pomenovaného clienta v inom realm-e. Safe administration preto vždy zachová actor, authentication realm, target realm, exact internal IDs, predecessor configuration, mutation body hash, Admin Event, authoritative read-back a druhú no-op operáciu.

## 1. Dominantný desired-change-to-effective-state lifecycle

```text
administrative alebo platform intent
→ exact actor, authentication realm a credential/session generation
→ exact target deployment, realm a resource internal ID
→ current-state inventory a predecessor configuration hash
→ canonical desired state, diff a preconditions
→ authorized Admin Console alebo Admin REST mutation
→ HTTP/result a Admin Event evidence
→ authoritative target-resource read-back
→ dependent graph, runtime/session alebo business verification
→ second no-op, adjacent-resource negative test a rollback/recovery closure
```

Žiadna jednotlivá fáza nestačí. Admin Event môže potvrdiť request, ale jeho body môže byť redacted alebo event recording disabled. GET read-back môže ukázať uložený client mapper, no už vydané tokens používajú predecessor projection. Realm import môže skončiť s conflictom po časti už vykonaných mutations. Druhý rovnaký `POST` môže vytvoriť duplicate namiesto no-op. Automation musí poznať semantics každého endpointu a nesmie interpretovať status code ako globálnu transakciu.

## 2. Exact administrative operation subject

```yaml
adminOperationSubject:
  keycloak:
    publicBaseUrl: https://sso.atlas.example
    adminBaseUrl: https://sso-admin.atlas.example
    deploymentGeneration: kc-2026-08-02-13
    serverVersion: 26.7.x
  actor:
    type: service-account
    authenticationRealm: platform-admin
    clientId: keycloak-config-controller
    clientUuid: 9e14...
    serviceAccountUserId: f2b8...
    authenticationMethod: private_key_jwt
    keyGeneration: admin-key-31
    tokenJtiHash: sha256:...
    effectiveAdminRoleRevision: admin-scope-19
  targetRealm:
    realmName: atlas-prod
    realmInternalId: 7df3...
    realmRevision: realm-304
  targetResource:
    kind: client
    clientId: settlement-api
    internalId: 31bf...
    predecessorRepresentationHash: sha256:93a2...
    expectedResourceVersion: client-231
  operation:
    operationId: kc-change-2026-08-02-771
    method: PUT
    path: /admin/realms/atlas-prod/clients/31bf...
    desiredBodyHash: sha256:f02e...
    planCommit: 8a7f...
    requestedAt: 2026-08-02T06:40:00Z
  result:
    httpStatus: 204
    adminEventId: 3f8a...
    successorRepresentationHash: sha256:31dd...
    readBackAt: 2026-08-02T06:40:03Z
```

Realm name v Admin REST path a realm internal ID sú odlišné identities. `clientId` je protocol-facing identifier; väčšina client-specific Admin REST endpointov používa internal client UUID. Group path, role name, flow alias alebo IdP alias môžu tiež vyžadovať resolution na internal ID. Exact operation subject zachová oba forms a odmietne zero alebo multiple lookup matches.

## 3. Admin Console a Admin REST API

Admin Console volá administračné APIs a zobrazuje len resources, ktoré actor smie query/view/manage podľa effective permissions. Formulár môže skryť field, aplikovať client-side default alebo vykonať viac requestov. Browser success banner preto nie je canonical audit evidence.

Admin REST API poskytuje explicitnejší automation surface, ale nezaručuje idempotency alebo atomicitu. Caller musí riešiť pagination, internal IDs, status semantics, partial failure, unknown outcome a secret redaction.

```text
Admin Console
→ interactive discovery a bounded manual operation
→ browser/session/CSRF/UI-version dependency

Admin REST API
→ machine-readable inventory a mutation
→ caller-owned diff, retry, completeness a recovery contract
```

Critical production change má reproducible source artifact alebo plan aj vtedy, keď sa vykoná ručne. Break-glass Console operation sa po incidente reconciliuje späť do authoritative source-of-truth.

## 4. Authentication realm a target realm

Administrator sa môže autentizovať v `master` realm-e alebo v dedicated realm-e. Master realm administrators môžu mať cross-realm authority; realm-local administrators typicky používajú `realm-management` client v target realm-e. Authentication realm určuje issuer admin tokenu, nie automaticky target realm requestu.

```text
admin token issuer /realms/master
→ request path /admin/realms/atlas-prod/...
→ actor z master realm-u mení atlas-prod
```

Automation má preferovať dedicated administrative realm/client a scoped service account pred permanentným master adminom. Master/recovery administrator zostáva break-glass identity s oddelenou custody, MFA a usage auditom.

Target realm sa nikdy neodvodzuje len z current shell contextu alebo filename-u. Plan obsahuje expected public issuer, realm name, internal realm ID a environment marker. Pre-mutation gate číta realm representation a odmietne mismatch.

## 5. Built-in realm-management roles

Každý non-master realm obsahuje `realm-management` client s roles pre query, view a manage capabilities, napríklad users, clients, groups, roles, identity providers alebo events. Broad `realm-admin` composition poskytuje takmer úplnú realm administration a môže obísť fine-grained restrictions.

```text
query-users
→ umožní vyhľadávanie/inventory surface

view-users
→ čítanie user detailov podľa effective permission

manage-users
→ create/update/delete/credential/session operations

realm-admin
→ broad composite; nepoužívať ako default automation role
```

Query role neznamená view alebo manage permission. Console section môže byť viditeľná, ale detail access odmietnutý. Automation preto testuje intended list/read/mutate endpoint aj forbidden adjacent operations.

## 6. Fine-Grained Admin Permissions

Fine-Grained Admin Permissions V2 umožňujú delegovať administration nad supported resource types ako users, groups, clients, roles a organizations cez permissions/policies naviazané na `admin-permissions` client. Permission môže obmedziť, kto smie view/manage konkrétny client, group subtree alebo user cohort.

```text
admin actor identity/roles/groups
→ admin-permissions authorization model
→ resource-specific view/manage permission
→ Admin Console/REST operation allowed alebo denied
```

Broad built-in admin roles ako `realm-admin` alebo resource-wide manage roles môžu obísť FGAP. Delegated model preto začína minimal realm-management query capability a explicitnými fine-grained permissions, nie broad role plus očakávanie, že policy ju zúži.

FGAP source, resource IDs, policies a permissions sú samostatná authorization generation. Export/read-back musí zachovať internal references. User/group/client rename nesmie rozbiť stable permission binding.

## 7. Service account pre automation

Admin automation používa confidential client so service accountom alebo workload-bound authentication. Service-account roles sú intersection medzi assigned service-account roles a client role-scope mappings; priradenie role samo nepreukazuje, že sa dostane do admin tokenu.

```text
service-account assigned realm-management roles
∩ client role scope mappings
→ token-eligible admin roles
→ Admin REST authorization
```

Client secret v CI variable je jednoduchý, ale replayable. Preferuj private-key JWT, mTLS alebo federovanú workload identity podľa podporovaného deploymentu. Credential generation má ownera, rotation, expiry a predecessor negative test. Automation client nemá interactive browser flows, Direct Grant ani unrelated service-account roles.

## 8. `kcadm.sh` configuration a credential custody

`kcadm.sh config credentials` môže uložiť server, realm, client a access/refresh tokens do config file-u. Default file musí mať restrictive filesystem permissions a nesmie byť CI artifactom, shared home directory alebo debug attachmentom.

```bash
export KCADM_CONFIG="$(mktemp)"
chmod 600 "$KCADM_CONFIG"

kcadm.sh config credentials \
  --config "$KCADM_CONFIG" \
  --server 'https://sso-admin.atlas.example' \
  --realm platform-admin \
  --client keycloak-config-controller \
  --secret "$KEYCLOAK_ADMIN_CLIENT_SECRET"
```

`--no-config` zabráni uloženiu session state-u, ale caller potom autentizuje každý command alebo explicitne spravuje token. Ani jeden mode neospravedlňuje secret v process list-e alebo shell history. CI runner po jobe zmaže config file a workspace; logs maskujú secret aj token.

## 9. Resource resolution: names versus internal IDs

List/search endpointy často používajú query podľa human identifiera, ale mutation endpoint potrebuje internal UUID. Safe resolver vyžaduje presne jeden match.

```bash
CLIENT_UUID="$({
  kcadm.sh get clients \
    --config "$KCADM_CONFIG" \
    -r atlas-prod \
    -q clientId=settlement-api \
    --fields id,clientId,enabled,protocol
} | jq -er '
  if length == 1 and .[0].clientId == "settlement-api"
  then .[0].id
  else error("expected exactly one settlement-api client")
  end
')"
```

Empty result, duplicate normalized identifiers alebo wrong realm sú hard failure. Resolver read-backne related namespace marker, protocol a expected internal ID when known. Cached UUID sa po delete/recreate nesmie reuse-nuť bez predecessor identity checku.

## 10. Pagination a inventory completeness

Admin REST list endpoints môžu byť paginated a callerove permissions môžu filtrovať výsledky. Prvá page alebo Console count nie sú complete inventory.

```text
endpoint + filters
→ first/max alebo cursor semantics
→ all pages
→ de-duplication podľa internal ID
→ expected count/cohort comparison
→ completeness verdict
```

Automation zachová page count, item count, duplicate IDs a terminal-page condition. Pri users/groups/clients s veľkou population používa bounded filters a nevykonáva unfiltered bulk mutations. Query permission testuje oddelene od view/manage permission, pretože invisible resource môže vyzerať ako absent.

## 11. Desired-state automation

Safe controller neodosiela export ako slepý PUT. Najprv číta current representation, odstráni server-generated/secret fields, canonicalizuje ordered/unordered collections a vypočíta semantic diff.

```text
source desired generation D-18
+ target current generation C-31
→ canonical normalization
→ semantic plan P-771
→ policy/owner approval
→ precondition C-31 stále current
→ bounded mutations
→ read-back R-32
→ D-18 == R-32
→ second run produces no mutation
```

Plan obsahuje exact target IDs a predecessor hashes. Ak target zmenil niekto iný po plan-e, automation odmietne stale plan namiesto prepisu. Endpoint bez ETag/version precondition potrebuje application-level pre-read immediately before mutation a post-read reconciliation.

## 12. HTTP status a mutation semantics

Create endpoint často vracia `201 Created` s `Location`; duplicate môže vrátiť `409 Conflict`. Update alebo delete často vracia `204 No Content`. Semantics sa overujú pre konkrétny endpoint a version.

```text
201
→ resource creation accepted; resolve Location/ID a GET read-back

204
→ request accepted without body; GET read-back required

409
→ conflict/duplicate; determine whether existing object equals desired state

5xx alebo timeout
→ outcome unknown; reconcile before retry
```

Blind retry `POST` po timeout-e môže vytvoriť duplicate. Retry najprv hľadá durable external identifier alebo canonical unique key, porovná desired state a až potom rozhodne create/update/abort.

## 13. Create, update a second no-op

Client creation example:

```bash
cat > /tmp/settlement-api-client.json <<'JSON'
{
  "clientId": "settlement-api",
  "protocol": "openid-connect",
  "enabled": true,
  "publicClient": false,
  "bearerOnly": true,
  "standardFlowEnabled": false,
  "directAccessGrantsEnabled": false,
  "serviceAccountsEnabled": false
}
JSON

kcadm.sh create clients \
  --config "$KCADM_CONFIG" \
  -r atlas-prod \
  -f /tmp/settlement-api-client.json
```

Po create resolver získa internal UUID a GET representation. Desired-state normalizer ignoruje server-generated fields, ale neignoruje security-relevant defaults. Druhý run nesmie vytvoriť ďalší client; musí skončiť no-op alebo explicitným update planom.

Update example číta predecessor a až potom PUT-ne exact client UUID:

```bash
kcadm.sh get "clients/${CLIENT_UUID}" \
  --config "$KCADM_CONFIG" \
  -r atlas-prod \
  | jq -S 'del(.secret, .registrationAccessToken)' \
  > /tmp/client-before.json

kcadm.sh update "clients/${CLIENT_UUID}" \
  --config "$KCADM_CONFIG" \
  -r atlas-prod \
  -f /tmp/client-desired.json

kcadm.sh get "clients/${CLIENT_UUID}" \
  --config "$KCADM_CONFIG" \
  -r atlas-prod \
  | jq -S 'del(.secret, .registrationAccessToken)' \
  > /tmp/client-after.json
```

Diff `desired` versus `after` je persistence evidence. Token/request canary je runtime/business evidence.

## 14. Secrets a write-only fields

Client secrets, private keys, SMTP credentials, LDAP bind passwords a identity-provider credentials sú sensitive. Admin GET môže redigovať, maskovať alebo nevrátiť write-only value. Automation preto nesmie interpretovať absent/redacted secret ako drift a neustále ho rotovať.

```text
secret source generation S-17
→ write-only Admin REST field
→ Keycloak encrypted/persisted credential
→ runtime client authentication test
→ predecessor secret negative test po rotation
```

Desired state uchováva secret reference a generation, nie plaintext v Git alebo plan outpute. Rotation je explicitná operation s consumer rolloutom a descendant-token boundary. Logs a Admin Events majú body redaction policy.

## 15. Partial import

Realm partial import môže vytvárať alebo aktualizovať selected resources podľa conflict strategy. Nie je globálna ACID transakcia. Response môže obsahovať added, overwritten, skipped alebo error results a HTTP status ako `200`, `403` alebo `409` podľa outcome/permissions/conflict.

```text
partial-import artifact I-18
→ parse a validate references
→ per-resource create/skip/overwrite
→ possible partial side effects
→ response summary
→ complete resource read-back a reconciliation
```

Timeout alebo `409` neznamená „nič sa nezmenilo“. Automation inventarizuje every target kind/ID a porovná successor graph. Large realm migration používa staged dependency order a backup, nie blind repeated partial import.

## 16. Bulk operations a partial success

Bulk user/group/role operations môžu obsahovať viac independent mutations. Ak jedna položka zlyhá, ostatné môžu byť committed. Controller zachová per-item operation ID/result a nevydá aggregate success iba podľa process exit code.

```text
bulk request B-771
→ item U1 success
→ item U2 conflict
→ item U3 timeout/unknown
→ per-item reconciliation
→ only failed/unknown item retried safely
```

Bulk delete je forbidden bez expected count, target ID allowlist, approval, backup/restore path a post-delete session/token handling.

## 17. Admin Events

Admin Events môžu zaznamenávať actor, realm, resource type/path, operation type, time, IP a voliteľne representation. Event recording a representation inclusion musia byť enabled a retention/export pipeline definované.

Admin Event je evidence, nie jediný oracle. Event môže potvrdiť request, ale nie downstream session invalidation alebo token claim. Sensitive representations môžu obsahovať PII alebo secrets; logging policy ich obmedzí.

```text
operationId/change ticket
↔ admin event time/actor/resourcePath
↔ target GET representation hash
↔ runtime token/session/business evidence
```

Automation correlation ID môže byť uložený do change metadata, commit/message alebo adjacent audit system, ak Keycloak endpoint body nemá custom operation ID field.

## 18. Fine-grained negative testing

Delegated administrator acceptance zahŕňa intended aj forbidden endpoints. Client automation smie update-nuť `settlement-api`, ale nesmie meniť realm keys, Browser flow, unrelated client, user credentials alebo admin permissions.

```text
positive
→ GET/PUT exact client UUID succeeds

forbidden adjacent client
→ 403 alebo invisible according to query policy

forbidden realm key operation
→ 403

forbidden user impersonation
→ 403

query-only actor attempts mutation
→ 403
```

`404` môže znamenať absent resource alebo authorization-filtered invisibility. Incident diagnosis koreluje actor permissions a admin events, nie iba status text.

## 19. Deletion a recovery boundary

Delete client/user/group/role/provider/flow môže cascade-nuť links, sessions, mappings alebo secrets. Internal ID reuse sa nepredpokladá. Pre-delete inventory obsahuje representation hash, dependent references, sessions/credentials a restore artifact.

```text
exact target ID + expected representation
→ dependency inventory
→ approval a backup
→ delete request
→ target absent read-back
→ dependent graph/session verification
→ recreate/restore creates successor IDs
→ consumers updated to successor identities
```

Recreate s rovnakým name/clientId nie je rollback identity. Clients dostanú nový internal UUID a možno secret; users nový user ID; flows nové execution IDs. Recovery musí aktualizovať references a sessions.

## 20. Bootstrap a recovery administrator

Prvý/bootstrap admin alebo recovery admin je installation/emergency mechanismus. Nemá byť permanentným automation credentialom. Po bootstrap-e sa vytvoria named administrative identities, scoped service accounts a break-glass custody; bootstrap credential sa odstráni alebo deaktivuje podľa deployment lifecycle-u.

Recovery admin procedure sa testuje pri LDAP/IdP outage a FGAP misconfiguration. Každé použitie má incident/change ticket, MFA, time-bounded access, session revocation a post-use credential rotation.

## 21. Connected incident `KC-PAY-68` — wrong realm, broad admin a blind retry

Atlas configuration controller sa autentizoval clientom `realm-config-bot` v `master` realm-e s broad `realm-admin`-equivalent authority. Pipeline parameter `TARGET_REALM` defaultoval na `atlas-stage`, ale artifact bol pre `atlas-prod`. Script vyhľadal `clientId=settlement-api`, nevynútil expected realm ID a získal stage client UUID.

Controller najprv PUT-ol broad token-exchange scopes a Authorization Services permission. Response timeoutol. Bez read-backu spustil partial import do `atlas-prod`, kde rovnaký clientId existoval s iným internal UUID. Import skončil `409` po časti mutations. Admin events boli enabled bez representations a pipeline log redigoval target URL, takže prvý verdict mylne znel „change failed“.

```text
master-realm broad actor
+ ambiguous target realm/clientId
→ wrong stage client mutation
→ timeout s unknown outcome
→ blind partial import do prod
→ partial policy/client changes
→ stale caches/sessions a broad token exchange
→ privileged settlement operation
```

## 22. Evidence-preserving containment a recovery

Zachovaj actor token hash a issuer, service-account user/client IDs, effective admin roles/FGAP policies, target realm IDs, every resolved internal UUID, plan/body hashes, HTTP timings, Admin Events, partial-import response, current target representations, sessions/tokens a downstream operation IDs. Secrets a full tokens sa neredigovane neukladajú.

Containment disable-ne controller credential a high-risk operations, zastaví ďalšie retries a snapshotne stage aj prod. Recovery reconciliuje each target resource, obnoví predecessor/successor policy graph podľa approved source, invaliduje caches/sessions/tokens podľa blast radiusu a zavedie target-realm/internal-ID preconditions a scoped automation service account.

## 23. Positive, recovery a forbidden acceptance

Acceptance musí oddeliť actor authorization, exact target resolution, persistence, dependent/runtime convergence a idempotency. Positive path dokazuje intended mutation; recovery uzatvára unknown/partial outcomes; forbidden paths dokazujú, že wrong realm/resource alebo broad admin capability nevytvoria side effect.

Positive path:

```text
scoped automation actor
→ expected realm name + internal ID
→ unique target clientId + known UUID
→ predecessor hash matches plan
→ bounded PUT
→ Admin Event + GET read-back
→ token/API canary
→ second run no-op
```

Recovery path:

```text
timeout alebo partial import
→ no blind retry
→ inventory affected resource IDs
→ classify applied/not-applied/unknown
→ reconcile to approved generation
→ verify sessions/tokens/business outcome
```

Forbidden paths:

```text
wrong realm ID alebo issuer
→ precondition rejects before mutation

zero/multiple client lookup results
→ resolver rejects

query-only actor attempts PUT
→ 403

controller tries unrelated client/realm keys/impersonation
→ 403

write-only secret absent from GET
→ no automatic rotation

repeated create with same operation intent
→ no duplicate

second run after convergence
→ no mutation/Admin Event
```

## 24. Troubleshooting

Pri `403` oddeľ authentication realm, actor token roles, client scope intersection, realm-management built-ins a FGAP policies/resource IDs. Pri `404` over target realm/path/internal UUID a či resource nie je authorization-filtered. Pri `409` čítaj endpoint-specific conflict a existing representation; nepredpokladaj global rollback.

Pri timeout-e zafixuj request hash/time/target ID a okamžite vykonaj authoritative GET/list/Admin Event reconciliation. Pri Console-versus-API rozdiele porovnaj actor session, hidden defaults, multiple browser requests a payload. Pri partial import-e inventarizuj všetky resource kinds a references.

## 25. Kontrolné otázky

- Ktorý actor, authentication realm, credential/session generation a effective permission vykonáva operation?
- Ktorý exact target realm name/internal ID a resource UUID sa menia?
- Je lookup unique, paginated a permission-complete?
- Má plan predecessor hash a stale-plan refusal?
- Aké endpoint-specific status a retry semantics platia?
- Ako sa riešia write-only secrets a rotation descendants?
- Je partial import alebo bulk operation per-item reconciled?
- Sú Admin Events enabled, correlated a bezpečne redigované?
- Ktoré forbidden adjacent operations delegated actor nevie vykonať?
- Prešli wrong realm, wrong UUID, timeout/unknown, second no-op a recovery paths?

## Glossary impact

Relevantné pojmy: Keycloak administrative operation subject, authentication realm, target realm, realm-management client, fine-grained admin permissions, admin-permissions client, master admin, realm administrator, delegated administrator, Admin Console, Admin REST API, `kcadm.sh`, internal client UUID, canonical desired state, stale plan, unknown mutation outcome, partial import, Admin Event, bootstrap admin, recovery admin a administrative second no-op.

## Primárne zdroje

- [Keycloak — Server Administration Guide: Admin Console, dedicated realm admin and fine-grained admin permissions](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak — Admin REST API](https://www.keycloak.org/docs-api/latest/rest-api/index.html)
- [Keycloak — Configuring `kcadm.sh`](https://www.keycloak.org/docs/latest/server_admin/#admin-cli)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Token exchange, impersonation a delegated access](token-exchange-impersonation-delegated-access.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
