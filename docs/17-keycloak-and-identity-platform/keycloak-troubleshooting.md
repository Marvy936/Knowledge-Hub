# Keycloak troubleshooting

Keycloak troubleshooting nezačína restartom ani screenshotom Admin Console. Začína presným subjectom a symptomom: ktorý deployment, realm, client, user/workload, protocol transaction, node, session/token, external dependency a business operation zlyhali, odkedy a pre ktorú population. Potom sa vytvoria konkurenčné hypotézy naprieč edge routingom, hostname/TLS, server configuration, authentication flowom, identity source-om, database/cache clusterom, token consumerom a downstream authorization. Každá hypotéza dostane evidence, ktorá ju môže potvrdiť aj vyvrátiť.

„Keycloak nefunguje“ môže znamenať DNS failure pred serverom, reverse-proxy `502`, server startup migration, redirect URI mismatch, expired action token, LDAP timeout, stale client cache, wrong token audience, custom provider exception alebo downstream API `403`. Rovnaký browser symptom môže mať desať odlišných authority boundaries. Reštart môže dočasne vyčistiť cache alebo presunúť traffic, ale zároveň zničiť in-progress evidence a zakryť mechanismus. Recovery je uzavretá až po authoritative read-backu a opakovaní intended aj forbidden journey bez workaroundu.

## 1. Dominantný troubleshooting lifecycle

```text
user/business symptom
→ exact subject, population a first/last known-good time
→ timeline a change/failure inventory
→ layer map a competing hypotheses
→ read-only evidence collection
→ authoritative configured/loaded/live/business comparison
→ bounded containment
→ one-axis repair alebo rollback/forward fix
→ positive, recovery a forbidden acceptance
→ second journey/node/client/operation
→ incident record a prevention
```

Každá fáza chráni pred inou chybou. Bez exact subjectu sa skúma nesprávny realm alebo client. Bez timeline sa zamieňa príčina s následkom. Bez competing hypotheses sa prvý nájdený warning vyhlási za root cause. Bez read-backu sa mutation retryne do unknown outcome. Bez forbidden testu sa oprava môže otvoriť privilege path.

## 2. Exact incident subject

```yaml
incidentSubject:
  symptom:
    reported: "Settlement administrators receive login loop"
    firstObservedAt: 2026-08-02T08:14:12Z
    lastKnownGoodAt: 2026-08-02T07:51:03Z
    affectedPopulation:
      realms: [atlas-prod]
      clients: [settlement-admin-web]
      users: 312
      regions: [eu-central]
      browsers: [Chrome-138, Edge-138]
  keycloak:
    version: 26.7.0
    imageDigest: sha256:7c21...
    deploymentGeneration: kc-release-53
    realm: atlas-prod
    issuer: https://sso.atlas.example/realms/atlas-prod
    nodeUids: [a1..., b2..., c3...]
  client:
    clientId: settlement-admin-web
    internalId: 2b2b...
    configurationRevision: client-224
    redirectUri: https://settlement-admin.atlas.example/oauth/callback
  transaction:
    protocol: oidc
    requestId: edge-req-9122
    authenticationSessionId: auth-6e21...
    stateHash: sha256:8fe1...
    codeHash: sha256:30c2...
    userSessionId: null
  edge:
    dnsRevision: dns-211
    loadBalancerRevision: edge-214
    tlsCertificateGeneration: edge-cert-91
  dependencies:
    databaseWriterGeneration: db-writer-94
    cacheTopologyId: 419
    ldapProviderRevision: ldap-71
  business:
    operation: settlement-admin-login
    expectedOutcome: authenticated privileged session after fresh WebAuthn step-up
```

Bez exact internal client ID sa rovnaký `clientId` v inom realm-e môže pomýliť. Bez browser/client population sa globálny outage zamieňa s one-client regression. Bez authentication session/state correlation sa authorization request a callback nespájajú. Bez image/config/edge generations sa incident nedá viazať na change.

## 3. Najprv klasifikuj failure layer

```text
Layer 0 — DNS/network/TCP/TLS
Layer 1 — reverse proxy/load balancer/hostname/path
Layer 2 — Keycloak process/startup/readiness
Layer 3 — database/cache/cluster/dependencies
Layer 4 — realm/client/flow/identity configuration
Layer 5 — protocol request/response/session/token
Layer 6 — resource server/local authorization
Layer 7 — downstream business operation
```

Začni najnižšou vrstvou, kde existuje dôkaz requestu. Ak edge access log request nevidí, neanalyzuj authentication flow. Ak Keycloak User Event ukazuje `LOGIN`, ale client callback zlyhal, nehľadaj password policy. Ak API vráti `403` po validnom token-e, problém je local authorization, nie token endpoint.

## 4. First-response evidence pack

Pred mutation/restartom zachovaj:

```text
current UTC time a incident window
DNS answers a TTL
external TLS chain/fingerprint
HTTP request/response headers bez secrets
edge access/error logs a route config revision
Keycloak Pods, image IDs, restarts, conditions a placement
startup/server/access logs per node
User/Admin Events a event-config generation
metrics dashboards/raw queries a target population
Keycloak CR/config/environment/process args hashes
database pool/DB writer/locks/latency
cache cluster views/topology/rebalance
client/flow/IdP/LDAP object read-backs
redacted token/header/claims + hashes
resource-server logs/policy generation
recent deploy/config/secret/cert/schema changes
```

Raw access/refresh tokens, passwords, OTP, authorization codes, client secrets a action-token URLs sa neukladajú. Použi hash a decoded non-secret claims. Evidence má source timestamp aj ingest timestamp.

## 5. Change timeline

```text
T-30m new image rollout
T-24m first successor Pod Ready
T-20m client mapper Admin REST update
T-18m TLS Secret rotation
T-15m first error spike
T-10m database writer failover
T-5m manual Pod restart
```

Korelácia nie je causality. Každý change sa porovná s affected population a mechanismom. TLS rotation nemôže sama meniť role claims; mapper update môže. Database failover môže spôsobiť timeouts, ale nie wrong redirect URI.

Zachovaj predecessor/successor generations a actual rollout times per Pod, nie iba Git commit timestamp.

## 6. Competing hypotheses table

| Hypotéza | Predikcia | Potvrdzujúci dôkaz | Vyvracajúci dôkaz |
|---|---|---|---|
| Wrong redirect URI | authorization succeeds, callback rejected | event/error `invalid_redirect_uri`, client read-back | exact redirect matches a callback reaches app |
| Proxy scheme/host drift | redirects/action URLs use internal/wrong authority | forwarded headers, discovery mismatch | canonical URLs on every node/path |
| DB pool saturation | latency + awaiting connections | `agroal_awaiting_count`, DB saturation | no waits and low DB latency |
| Split cache cluster | node-specific stale config/session | member/topology mismatch, node-specific result | same cluster view and successor result all nodes |
| LDAP timeout | only federated users fail | provider errors, LDAP latency | local users and federated both fail equally |
| API wrong audience | Keycloak token issue succeeds, API returns 401 | token `aud`, API validator log | intended audience present/accepted |

Tabuľka zabraňuje „log line archaeology“ bez testovateľnej predikcie. Hypotéza sa neuzavrie iba preto, že dôkaz je kompatibilný; musí vysvetliť population, timing a recovery.

## 7. DNS, network a TLS

```bash
getent ahosts sso.atlas.example

dig +trace sso.atlas.example

openssl s_client \
  -connect sso.atlas.example:443 \
  -servername sso.atlas.example \
  -showcerts </dev/null

curl --fail --silent --show-error \
  -D /tmp/headers.txt \
  -o /dev/null \
  https://sso.atlas.example/realms/atlas-prod/.well-known/openid-configuration
```

Over DNS answer, route, SNI, chain, validity, SAN a HTTP status. `curl -k` môže izolovať trust failure od route failure, ale nie je acceptance. Porovnaj external edge a proxy→Keycloak backend TLS pri re-encrypt topology.

Symptom signatures:

```text
connection refused
→ listener/service/route absent

timeout
→ network policy, firewall, LB, saturation alebo packet loss

TLS unknown_ca
→ trust chain/store

hostname mismatch
→ DNS/SNI/certificate target
```

## 8. Reverse proxy, hostname a redirect loops

Read-back discovery:

```bash
curl -fsS \
  https://sso.atlas.example/realms/atlas-prod/.well-known/openid-configuration \
  | jq '{issuer,authorization_endpoint,token_endpoint,end_session_endpoint}'
```

Inspect redirects:

```bash
curl -skI \
  'https://sso.atlas.example/realms/atlas-prod/account'
```

Porovnaj `Host`, `Forwarded`/`X-Forwarded-*`, proxy source a trusted-address configuration. Redirect loop často vzniká pri:

```text
external HTTPS + Keycloak sees HTTP
wrong X-Forwarded-Port
inconsistent relative path/rewrite
frontend/admin hostname mismatch
application callback cookie/session mismatch
```

Testuj každý proxy cohort a direct backend forbidden path. `hostname-admin` sám neblokuje public `/admin/`.

## 9. `502`, `503`, `504`

Tieto statusy generuje edge alebo proxy podľa rozdielnych upstream outcomes a nesmú sa zjednotiť na generic Keycloak outage. `502` typicky znamená connect/TLS/protocol failure, `503` nedostupnú alebo zámerne odmietajúcu capacity a `504` prekročený response timeout. Diagnostika preto koreluje edge error s endpoint population, Pod healthom a Keycloak request logom.

```text
502 Bad Gateway
→ proxy nedostal validnú upstream response; connect/TLS/protocol/reset

503 Service Unavailable
→ no ready endpoints, load shedding, maintenance alebo saturation

504 Gateway Timeout
→ upstream response prekročila proxy timeout
```

Edge status nie je Keycloak status. Skontroluj upstream connect error, Pod readiness, endpoint slices, Keycloak access log a request ID. Zvýšenie proxy timeoutu môže iba zakryť database pool, external IdP alebo thread queue bottleneck.

## 10. Pod a Operator state

```bash
kubectl -n identity-prod get keycloak atlas-keycloak -o yaml
kubectl -n identity-prod get pods -l app.kubernetes.io/component=server -o wide
kubectl -n identity-prod describe pod <pod>
kubectl -n identity-prod logs <pod> --previous
kubectl -n identity-prod get events --sort-by=.lastTimestamp
```

Rozlišuj CR generation, observed generation, managed workload revision, Pod image/config, startup/liveness/readiness a protocol acceptance. `CrashLoopBackOff` potrebuje previous logs a termination reason. `OOMKilled`, CPU throttling, probe failure a application exception majú odlišnú recovery.

Ručný child-resource patch Operator vráti; oprav CR/source of truth.

## 11. Startup failure

Startup sequence zahŕňa configuration resolution, optimized build compatibility, providers, database connection/schema migration, cache initialization, hostname/TLS a management interface.

```text
unknown/removed option
provider class/dependency conflict
database auth/TLS/schema mismatch
migration lock/timeout
cache discovery/network failure
certificate/key read/parse failure
port bind conflict
```

Zachovaj full startup log od process startu. Posledný stack trace môže byť secondary failure po root cause. Nevymaž data/tmp alebo rebuild bez artifact diffu.

## 12. Health endpoint interpretation

```bash
curl -fsS http://127.0.0.1:9000/health/started | jq .
curl -fsS http://127.0.0.1:9000/health/live | jq .
curl -fsS http://127.0.0.1:9000/health/ready | jq .
```

Started/live/ready dokazujú process/component health podľa checks. Nepreukazujú realm/client journey, external IdP, SMTP, resource server alebo business authorization. Public access na management port je forbidden.

Readiness flapping môže byť database, cache, management TLS/probe mismatch alebo overload. Liveness restart loop môže zhoršiť migration/rebalance.

## 13. Logs, events, metrics a traces

```text
logs
→ internal mechanism a exception

User Events
→ identity/protocol operation

Admin Events
→ administration mutation attempt

metrics
→ population/rate/latency/saturation

traces
→ sampled request path
```

Absence eventu môže znamenať request neprišiel, event type disabled, retention expired alebo listener delivery lost. Metrics counters sú per instance a resetujú sa po restart-e. Trace absence pri sampling-u nie je dôkaz absence requestu.

Koreluj request/session/client/user/trace/operation IDs bez raw secrets.

## 14. Login failure taxonomy

```text
invalid_user_credentials
user_not_found
user_disabled
credential_expired
brute_force_lockout
required_action_pending
identity_provider_error
invalid_code
expired_code
invalid_redirect_uri
session_not_found
```

Browser text môže byť zámerne generic. User Event `error`, flow execution logs a user/credential/provider read-back odlíšia path. Neodhaľuj user enumeration v response.

Testuj local known-good user a affected federated user; fresh browser bez SSO a remembered SSO; intended client a adjacent client.

## 15. Redirect URI a OIDC transaction

Authorization request subject:

```text
issuer/realm
client internal ID
authorization endpoint
redirect_uri exact string
state/nonce/code_challenge hashes
response_type/mode
requested scopes/acr/prompt/max_age
```

Keycloak exact-match/allowed redirect policy je authority. URL encoding, trailing slash, scheme, port, path, query a case môžu meniť match. Wildcard expansion nie je recovery.

`state` mismatch alebo missing correlation je client/application issue aj keď Keycloak code bol validný. Code je single-use a short-lived; retry callback s rovnakým code má zlyhať.

## 16. `invalid_client` a token endpoint

`invalid_client` je client-authentication alebo client-resolution verdict, nie dôkaz nesprávneho user passwordu. Token endpoint najprv musí nájsť exact realm/client generation, overiť enabled grant a potom credential method vrátane secretu, private-key JWT alebo mTLS. Troubleshooting preto oddeľuje client capability, credential generation a request endpoint skôr, než mení grant alebo secret.

```text
wrong client ID/realm
client authentication disabled/enabled mismatch
expired/rotated secret or key
wrong token endpoint/issuer
private-key JWT aud/iss/sub/time/jti error
unsupported grant
public client sends secret alebo confidential client secret absent
```

Inspect client internal ID/capabilities a credential generation. Neprintuj secret. Test successor credential, predecessor forbidden path a exact grant. `Direct Access Grant` sa nemá zapínať ako workaround pre browser flow.

## 17. Token validation failure

Decode redacted token locally:

```bash
python - <<'PY'
import base64, json, os
parts = os.environ['ACCESS_TOKEN'].split('.')
for name, part in zip(('header','payload'), parts[:2]):
    part += '=' * (-len(part) % 4)
    print(name, json.dumps(json.loads(base64.urlsafe_b64decode(part)), indent=2))
PY
```

Kontroluj:

```text
access token, nie ID/refresh
iss
aud
azp/caller
kid/alg/signature
exp/nbf/iat a clock skew
scope/roles/claims types
cnf/DPoP/mTLS proof podľa profile
```

`401` s valid signature často znamená wrong audience/issuer/token type alebo stale JWKS cache. `403` znamená local permission/tenant/resource/action. Resource server logs/policy generation sú required evidence.

## 18. JWKS a signing-key rotation

```bash
curl -fsS \
  https://sso.atlas.example/realms/atlas-prod/protocol/openid-connect/certs \
  | jq '.keys[] | {kid,kty,alg,use}'
```

Unknown `kid` môže byť stale consumer cache, wrong realm/issuer alebo incomplete rotation. Porovnaj token `kid`, current JWKS, realm key generation a resource-server cache refresh. Nevymaž všetky keys/caches bez overlap a token-lifetime analysis.

HTTPS certificate je iný key family než realm signing keys.

## 19. Session, refresh a logout

Browser session, Keycloak user/client session, refresh alebo offline credential, access token a local application session sú samostatné descendants. Failure alebo revocation jednej vrstvy nemusí okamžite odstrániť ostatné, preto sa symptom mapuje na exact session/token generation a consumer. Nasledujúce patterns pomáhajú odlíšiť stale bearer acceptance od refresh alebo logout lifecycle problému.

```text
access token valid, refresh fails
→ refresh/session/client state issue

logout UI succeeds, API token still accepted
→ access-token offline validation/stale window

other browser remains logged in
→ descendant/application session not revoked
```

Zachovaj user session ID, client session, `sid`, refresh/offline token hashes, not-before generations a application session. Test refresh before/after rotation, logout, session revoke a second login.

Point-in-time restore môže vrátiť predecessor revocation/session state.

## 20. MFA, WebAuthn a passkeys

Troubleshoot:

```text
flow binding/override generation
Cookie ALTERNATIVE a remembered SSO
ACR/LoA requested a achieved
user credential inventory
RP ID/origin
challenge/session/tab
user verification/discoverable credential policy
browser/authenticator capability
required action enrollment
```

WebAuthn `NotAllowedError` je generic: user cancel, timeout, origin/RP mismatch, credential absence alebo policy. Capture browser console/device data bez credential secrets. Fresh-login and remembered-session paths sa testujú zvlášť.

## 21. Required actions a email links

Required-action journey spája stored pending action, signed action-token generation, hostname/theme render, SMTP delivery, browser transaction a authoritative user mutation. Zelený SMTP response alebo redirect pokrýva iba jednu časť chainu. Troubleshooting musí preto prejsť issue, delivery, validation, mutation a replay denial v rovnakom user/client context-e.

```text
pending requiredActions on user
provider enabled/default state
action-token issue/expiry/user/action/client
canonical hostname a email theme URL
SMTP accept/delivery
mutation read-back
replay denial
```

SMTP `250` nepreukazuje delivery. Redirect po action nepreukazuje mutation. Hardcoded/stale hostname alebo locale placeholder môže rozbiť link. Expired link sa nerepairuje predĺžením všetkých token lifespans naslepo.

## 22. Identity brokering

```text
external IdP alias/config generation
upstream issuer/client/redirect/JWKS/metadata
state/nonce/relay correlation
upstream subject
federated identity link
First/Post Broker Login flow
Trust Email/AutoLink/mappers
local user/session
```

Valid upstream token nepreukazuje correct local account link. Recycled email alebo unsafe AutoLink je privilege incident. Test existing link, first login, wrong subject/email, link/unlink a upstream logout.

## 23. SAML

Kontroluj:

```text
entityID
ACS URL/index/binding
AuthnRequest ID/issuer/destination
RelayState
assertion Response/InResponseTo/audience/recipient/time
signature/encryption certificate generation
NameID/session index/mappers
```

Clock skew, metadata drift, cert rotation a unsolicited IdP-initiated flow majú odlišné symptoms. XML signature validation error sa nerieši vypnutím signature requirement. Zachovaj redacted XML hash a metadata generation.

## 24. LDAP/Active Directory

```text
provider enabled/priority/edit/import/sync mode
connection/bind/TLS/hostname
users DN/filter/UUID attribute
mapper ownership/group role mappings
cache policy/generation
full/changed sync timestamps/results
credential validation latency/error
```

`Test connection` preukazuje connect/bind podľa testu, nie user search, mapper, password, group sync alebo failover. Local imported user môže existovať, ale external credential/attribute state byť stale. Cache eviction/restart môže dočasne zmeniť symptom; oprav invalidation/sync authority.

## 25. User Storage SPI

Custom storage provider failure môže byť timeout, duplicate user ID, unstable external ID, capability mismatch, transaction/external side effect alebo cache issue. Fixuj provider JAR/version/config, external target a imported-user link.

Provider `null`/exception semantics nesmú fallbacknúť na wrong local user. Test node A/B, cache miss/hit, external outage, duplicate username a second update.

## 26. Database pool a DB

Metrics:

```text
agroal_active_count
agroal_available_count
agroal_awaiting_count
```

```text
awaiting > 0 + DB saturated
→ DB/query/cache bottleneck; larger pool may worsen

awaiting > 0 + DB healthy/idle
→ pool/thread sizing or connection creation problem

connection creation errors
→ DNS/TLS/auth/writer failover
```

Over global ceiling across replicas. Inspect DB CPU/IOPS/locks/commit latency/connection count. Unknown outcome po connection reset sa read-backne pred Admin/import retry.

## 27. Schema migration

```text
exact source/target version
schema version
migration strategy/owner
SQL artifact/hash
locks/progress
timeout/probe behavior
mixed writer versions
backup/rollback boundary
```

Restart loop during migration môže opakovane čakať na lock. Never manually edit schema bez supported plan. `Ready` after upgrade nepreukazuje missing indexes/performance or predecessor compatibility.

## 28. Infinispan a cluster

```text
cache mode local/ispn
cluster name
member view per Pod
topology ID/rebalance
JGroups transport/network
site/rack/machine
persistent/volatile session model
work invalidations
external Infinispan site state
```

Node-specific stale client/role/mapper result naznačuje split cluster alebo invalidation failure. Restart stale node je containment/evidence, nie root-cause fix. Test second mutation across every node without restart.

## 29. Operator reconciliation

```text
CR generation vs status observed generation
conditions/messages
Operator logs/events
managed child owner references
image/config/Secret revisions
Pod rollout/probe/routes
```

Ak manual patch mizne, Operator obnovuje CR-derived state. GitOps má vlastniť CR, nie child workload. `spec.env` pre first-class settings môže vytvoriť controller/runtime mismatch.

## 30. CPU, memory, GC a performance

Symptom map:

```text
CPU throttling + high hashing validations
→ password CPU saturation

rising old gen after full GC
→ leak/cache/session/provider retention

low cache hit + high DB reads
→ cache cardinality/size/churn

high P99 + low CPU + awaiting DB
→ DB pool/database latency

503 + queue saturation
→ load shedding/executor capacity
```

Compare affected and healthy Pod cohorts. Heap dump/profiling je sensitive a bounded. Zmeň jednu axis a rerun representative load; pridanie memory/threads/replicas bez mechanismu môže zhoršiť DB/cache.

## 31. Custom provider failure

```text
NoClassDefFoundError/NoSuchMethodError
→ target-version/dependency/shared-classloader conflict

provider not found
→ service descriptor/build/selection

request hangs
→ blocking external call/unbounded queue/deadlock

node-only behavior
→ static/local state or mixed provider image

DB errors after rollback
→ custom schema/data incompatibility
```

Fix entire immutable image, nie live JAR injection. Capture provider/dependency hashes, thread dump, transaction/external event IDs a rollout cohorts.

## 32. Themes a localization

```text
actual selected login/email theme
JAR/theme/parent/template generation
browser/CDN/server cache
form action/hidden fields
CSP/resources
email action URL
locale precedence/message placeholders
```

Password path green nepreukazuje passkey/required-action path. Switch to built-in theme can be bounded containment; preserve rendered samples and artifact hashes. Compare overridden templates with target Keycloak version.

## 33. API a MCP

API failure ladder:

```text
network/TLS
→ token present/type
→ issuer/signature/time
→ audience/caller
→ scope/role/permission
→ tenant/resource/action/tool policy
→ downstream operation
```

MCP additionally checks protected-resource metadata, Keycloak authorization-server metadata, client registration/CIMD/DCR, PKCE, exact MCP server audience and tool/resource/prompt policy. Keycloak 26.7 novšie MCP profiles bez RFC 8707 sú partial workaround, nie full conformance. Wrong-audience token must fail even with correct signature.

## 34. Backup, restore a upgrade incidents

Po restore/upgrade vždy over:

```text
image/schema/provider/theme/config generations
realm keys/discovery/SAML metadata
sessions/offline tokens/revocation
LDAP/broker links
client credentials/redirects/mappers
Admin access/audit
business operations
```

Green login is insufficient. Restore may rewind revocation; image rollback may be incompatible with successor schema/provider data. Decide exact rollback axes or forward fix.

## 35. Safe containment patterns

```text
remove one bad Pod cohort from traffic
freeze admin/import/config mutations
block one client/audience/tool
switch affected realm to built-in theme
fence degraded site
reduce load via load shedding
extend evidence retention
```

Containment must be bounded and reversible. Broad actions like disable realm, clear all caches, rotate all keys, delete sessions or restart every node destroy evidence and increase blast radius unless failure demands them.

## 36. Dangerous troubleshooting anti-patterns

```text
restart until green
clear caches without before/after evidence
disable TLS/hostname/signature/audience checks
add wildcard redirect/origin
turn on Direct Access Grant
increase every timeout/pool/thread limit
run import override with active nodes
manually patch Operator-managed children
edit database schema/data directly
install debug provider in production
log raw tokens/passwords/OTP
```

Každý workaround môže zmeniť security semantics. Emergency change má source, owner, expiry, audit a successor immutable artifact.

## 37. Authoritative read-back examples

Client:

```bash
CLIENT_UUID="$(kcadm.sh get clients -r atlas-prod -q clientId=settlement-admin-web --fields id | jq -er '.[0].id')"
kcadm.sh get "clients/${CLIENT_UUID}" -r atlas-prod | jq '{id,clientId,redirectUris,webOrigins,publicClient,serviceAccountsEnabled,standardFlowEnabled,directAccessGrantsEnabled,fullScopeAllowed,protocolMappers,defaultClientScopes,optionalClientScopes}'
```

User/session:

```bash
USER_ID="$(kcadm.sh get users -r atlas-prod -q username=alice.payments --fields id | jq -er '.[0].id')"
kcadm.sh get "users/${USER_ID}" -r atlas-prod --fields id,username,enabled,emailVerified,requiredActions
kcadm.sh get "users/${USER_ID}/sessions" -r atlas-prod | jq '[.[] | {id,start,lastAccess,clients}]'
```

Realm events:

```bash
kcadm.sh get events/config -r atlas-prod
kcadm.sh get events -r atlas-prod -q client=settlement-admin-web -q dateFrom=2026-08-02 | jq .
```

Read-back preukazuje current admin target state, nie necessarily runtime cache/business effect. Nasleduje node/protocol/application test.

## 38. Bounded experiment design

```yaml
experiment:
  hypothesis: node B has stale client cache after missed invalidation
  subject:
    realm: atlas-prod
    clientInternalId: 2b2b...
    nodes: [A, B, C]
  readOnlyEvidence:
    - cluster views
    - current DB/client hash
    - token claims per node-routed request
  boundedAction: update dedicated harmless mapper generation once
  expected:
    allNodes: successor claim
  forbidden:
    - restart
    - cache clear
    - production privilege expansion
  rollback: remove harmless mapper
```

Experiment musí mať stop conditions, small blast radius a business-safe test identity. Ak nie je možné bezpečne testovať v production, reproduce v restored/canary environment-e s rovnakými generations.

## 39. Recovery acceptance matrix

Positive:

```text
original intended user/workload journey
→ correct Keycloak artifact/session
→ resource-server authorization
→ business operation succeeds once
```

Recovery:

```text
predecessor failure scenario replayed
→ no recurrence
→ evidence sources complete
→ second node/client/session succeeds
```

Forbidden:

```text
wrong realm/client/redirect/token type/audience/tenant/resource/tool
→ rejects

old credential/key/session po retirement
→ rejects podľa contractu

public admin/management/direct backend path
→ network/proxy rejects
```

Acceptance uses fresh and pre-existing sessions/tokens as required. One green browser is not closure.

## 40. Incident `KC-PAY-82`

Po release `kc-release-53` mali settlement admins login loop. Edge log ukázal `302`, Keycloak User Event `LOGIN` a application log `state mismatch`. Tím reštartoval všetky Pods, čím stratil authentication-session a cache evidence. Symptom na päť minút zmizol.

Skutočný incident bol kombinovaný. Jedna proxy cohort posielala wrong `X-Forwarded-Port`, preto callback URI mala interný port. Successor theme zároveň používala predecessor JavaScript pre WebAuthn a application BFF rollout zmenil session-cookie domain. User Events dokazovali identity authentication, nie client callback/session success.

Po reštarte sa traffic náhodne presunul na healthy proxy cohort. Neskôr problém recurred. Paralelne API vracalo `403`, pretože nový token mapper zmenil claim type z listu na string; tím to nesprávne spájal s login loopom.

```text
multiple independent failures
+ one generic browser symptom
+ restart without subject/evidence
→ temporary recovery a false root cause
```

Final recovery oddelila transaction chain: canonical discovery/redirect per proxy cohort, theme artifact/form/WebAuthn path, BFF state/cookie correlation a API claim/policy contract. Každá oprava mala predecessor/successor generation a positive/forbidden test. Second login prešiel cez každý proxy/Pod, remembered SSO aj fresh WebAuthn a downstream settlement operation.

## 41. Post-incident closure

Postmortem obsahuje:

```text
exact impact/population/duration
first/last known-good generations
timeline a detection gaps
competing hypotheses a evidence
root/trigger/contributing conditions
containment a recovery mutations
proof boundaries
forbidden/second-operation results
recurrence controls a owners/dates
runbook/alert/test updates
```

Root cause nie je „Keycloak“ ani „cache“. Musí pomenovať konkrétny mechanismus a authority failure. Blameless neznamená without accountability; systems/permissions/gates sa zmenia tak, aby rovnaká chyba bola harder alebo harmless.

## 42. Kontrolné otázky

- Aký je exact deployment/realm/client/user/session/token/request/business subject?
- Ktorá najnižšia layer request videla a kde chain prestal?
- Aké competing hypotheses vysvetľujú timing aj population?
- Ktorý evidence source môže každú hypotézu vyvrátiť?
- Čo je configured, loaded, live a business-effective state?
- Existuje unknown mutation outcome, ktorý treba read-backnúť pred retry?
- Je containment bounded a zachováva evidence?
- Mení workaround security semantics alebo authority?
- Prešla original positive journey aj wrong-client/token/tenant/resource forbidden path?
- Prešiel second node/proxy/client/session/operation bez restart workaroundu?
- Boli dočasné accounts, debug settings a broadened policies odstránené?

## Primárne zdroje

- [Keycloak — Troubleshooting using metrics](https://www.keycloak.org/observability/metrics-for-troubleshooting)
- [Keycloak — Database metrics](https://www.keycloak.org/observability/metrics-for-troubleshooting-database)
- [Keycloak — Logging](https://www.keycloak.org/server/logging)
- [Keycloak — Health checks](https://www.keycloak.org/observability/health)
- [Keycloak — Metrics](https://www.keycloak.org/observability/configuration-metrics)
- [Keycloak — Configuring the hostname](https://www.keycloak.org/server/hostname)
- [Keycloak — Using a reverse proxy](https://www.keycloak.org/server/reverseproxy)
- [Keycloak — Configuring distributed caches](https://www.keycloak.org/server/caching)
- [Keycloak — Upgrading Guide](https://www.keycloak.org/docs/latest/upgrading/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Keycloak performance, sizing a load testing](keycloak-performance-sizing-load-testing.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
