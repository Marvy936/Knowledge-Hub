# Service accounts a machine-to-machine authentication

Keycloak service account nie je technický user, ktorému stačí prideliť rovnaké realm roles ako človeku. Je to workload identity naviazaná na confidential clienta a client-credentials grant. Token, ktorý Keycloak vydá, vzniká z client authentication, service-account usera, jeho effective roles, role scope mappings clienta a linked client scopes, protocol mappers, audience policy a token lifetime. Bez presného rozlíšenia týchto vrstiev môže machine client úspešne autentizovať a súčasne dostať priveľa oprávnení alebo token určený nesprávnemu API.

Najčastejší prevádzkový omyl je považovať client secret za samotnú workload identity. Secret je iba jedna client-authentication credential generation. Nehovorí, ktorý Pod, VM, pipeline alebo externý partner ho práve používa, neobmedzuje resource ani action a po úniku môže byť replaynutý z iného prostredia. Machine-to-machine acceptance preto musí spojiť client registration, credential generation, service-account role graph, token projection, calling workload a downstream business operation.

## 1. Dominantný client-credentials lifecycle

Client-credentials flow nemá human browser transaction, user password, MFA prompt ani user consent. Keycloak autentizuje clienta na token endpoint-e a vytvorí access token reprezentujúci jeho service-account identity.

```text
machine workload a operation intent
→ exact realm a confidential client generation
→ client-authentication credential alebo workload proof
→ token endpoint client_credentials request
→ service-account user resolution
→ service-account effective roles
→ client a client-scope role-scope intersection
→ protocol mappers, audience a token generation
→ resource-server issuer/signature/time/audience/caller validation
→ local tenant/resource/action authorization
→ credential rotation, token expiry/revocation a second-operation test
```

Každý transition má vlastnú failure boundary. Client authentication môže byť správna, ale service-account user je disable-nutý. Service account môže mať intended role, ale client role scope ju neprepustí do tokenu. Token môže obsahovať správnu role, ale broad audience umožní replay voči ďalšej službe. API môže správne validovať token a napriek tomu povoliť operation nad nesprávnym tenantom, pretože lokálna authorization viaže iba role, nie resource ownership.

## 2. Exact service-account subject

Incident veta „unikol secret settlement-batch“ nestačí. Zachovaj:

```yaml
serviceAccountSubject:
  keycloak:
    publicBaseUrl: https://sso.atlas.example
    deploymentGeneration: kc-2026-08-01-17
    realm: atlas-prod
    issuer: https://sso.atlas.example/realms/atlas-prod
  client:
    clientId: settlement-batch
    internalId: 36f3dbf1-86ac-48c7-b274-c3c398d94150
    configurationRevision: client-221
    clientAuthentication: true
    serviceAccountsEnabled: true
    standardFlowEnabled: false
    directAccessGrantsEnabled: false
    fullScopeAllowed: false
  serviceAccount:
    userId: f1901380-1da8-4350-a866-b294f65cd226
    username: service-account-settlement-batch
    enabled: true
    roleGraphRevision: service-role-58
  credential:
    method: private_key_jwt
    keyId: settlement-batch-2026-07
    publicKeyGeneration: key-17
  scopes:
    default: [roles, settlement-batch-base]
    optional: [settlement-export]
    roleScopeRevision: scope-31
  token:
    audience: settlement-api
    lifespanSeconds: 300
  workload:
    clusterUid: 27c7...
    namespace: payments-prod
    serviceAccount: settlement-batch
    deploymentUid: c5e8...
    podUid: 11a4...
```

Rovnaký `clientId` po delete/recreate môže mať nový internal ID, nový service-account user a inú credential alebo role generation. Rovnaký Kubernetes ServiceAccount môže spúšťať viac Pods; ak všetky používajú statický secret, Keycloak token neidentifikuje konkrétny Pod. Exact workload identity preto musí pochádzať z credential methodu alebo z externého deployment evidence, nie z názvu clienta.

## 3. Client registration a service-account user

Service Accounts capability je dostupná confidential clientovi, ktorý sa vie autentizovať na token endpoint-e. Keycloak vytvorí alebo používa internal service-account user naviazaný na clienta. Tento user má stable internal ID, enabled state, attributes a role mappings, ale nemá human login lifecycle.

```text
client settlement-batch
→ linked service-account user service-account-settlement-batch
→ direct/group/composite effective roles
→ role-scope filtering
→ access token subject a claims
```

Service-account user sa nemá pridávať do organizačných groups iba preto, aby zdedil role. Group hierarchy je spravidla model ľudskej organization alebo tenant membership a môže sa meniť nezávisle od workload contractu. Machine identity potrebuje explicitný owner, environment, consumer, operation set, expiry/rotation policy a decommission lifecycle.

## 4. Role intersection: service-account roles a client scope

Keycloak nevydá automaticky všetky role service-account usera. Effective role projection pre client-credentials token je intersection medzi service-account effective roles a role scope mappings clienta vrátane linked client scopes.

```text
service-account direct a composite roles
∩ client role scope mappings
∩ linked client-scope role mappings
→ token-eligible role set
→ role protocol mappers
→ realm_access alebo resource_access claims
```

Tento model vysvetľuje dva opačné symptoms. Ak service account má role, ale token ju neobsahuje, problém môže byť v `Full Scope Allowed`, role scope mappings, client-scope linku alebo mapper placement. Ak token obsahuje priveľa roles, broad `Full Scope Allowed`, composite realm role alebo shared default scope môže rozšíriť projection bez editovania samotného service-account usera.

Least-privilege M2M model preferuje client roles resource servera, napríklad `settlement-api.reconcile`, pred broad realm role `platform-admin`. Realm-management roles pre Admin REST API sú vysoko privilegované a musia byť oddelené od business API identity.

## 5. Inventory cez Admin API a `kcadm.sh`

Najprv sa zafixuje client a linked service-account user:

```bash
CLIENT_UUID="$({
  kcadm.sh get clients \
    -r atlas-prod \
    -q clientId=settlement-batch \
    --fields id,clientId,enabled,serviceAccountsEnabled,standardFlowEnabled,directAccessGrantsEnabled,fullScopeAllowed
} | jq -er '.[0].id')"

kcadm.sh get "clients/${CLIENT_UUID}/service-account-user" \
  -r atlas-prod \
  --fields id,username,enabled,attributes
```

Lookup preukazuje client record v admin targete a service-account link v danom realm-e. Nepreukazuje current token, credential validity ani downstream acceptance. Pri viacerých deployments musí evidence obsahovať base URL, realm issuer a deployment generation.

Role mappings sa čítajú oddelene:

```bash
SERVICE_USER_ID="$({
  kcadm.sh get "clients/${CLIENT_UUID}/service-account-user" \
    -r atlas-prod \
    --fields id
} | jq -er '.id')"

kcadm.sh get "users/${SERVICE_USER_ID}/role-mappings/realm/composite" \
  -r atlas-prod \
  --fields id,name,containerId

kcadm.sh get "clients/${CLIENT_UUID}/scope-mappings" \
  -r atlas-prod
```

Prvý output ukazuje effective composite realm-role expansion service-account usera. Druhý ukazuje client role-scope configuration. Ani jeden sám nepreukazuje final JWT; token fixture je potrebný na overenie mapperov, audience a claim shape-u.

## 6. Token request so secretom

Client secret je jednoduchý bootstrap, ale má vysoký replay blast radius. Secret sa nemá zapisovať do command line, repository, image layer ani shared shell history. Príklad používa environment variable a HTTP Basic client authentication:

```bash
export KEYCLOAK_CLIENT_SECRET="$(secret-tool-read settlement-batch)"

curl --fail --silent --show-error \
  --user "settlement-batch:${KEYCLOAK_CLIENT_SECRET}" \
  --data-urlencode 'grant_type=client_credentials' \
  --data-urlencode 'scope=settlement-reconcile' \
  'https://sso.atlas.example/realms/atlas-prod/protocol/openid-connect/token' \
  | tee token-response.json \
  | jq '{token_type,expires_in,scope,not_before_policy,session_state}'
```

HTTP success preukazuje, že token endpoint prijal client authentication a grant v danom čase. Nepreukazuje least privilege, správnu audience, konkrétny workload caller ani business operation. Access token sa musí validovať a použiť proti intended API aj forbidden adjacent API.

Client-credentials design má typicky získavať fresh short-lived access token. Consumer nemá predpokladať refresh token. Ak konkrétna Keycloak/client-policy generation explicitne umožňuje refresh token pre client credentials, ide o samostatný descendant credential contract, ktorý potrebuje rotation, theft a revocation testy.

## 7. Private-key JWT, mTLS a workload-bound authentication

Static shared secret neumožňuje serveru rozlíšiť dve kópie workloadu. Private-key JWT používa asymmetric client credential: workload podpisuje client assertion private keyom a Keycloak validuje registered public key/certificate. Rotation môže prebiehať s overlapom predecessor a successor key generation.

```text
workload private key generation W-17
→ signed client assertion s iss=sub=client_id, aud=token endpoint, exp a jti
→ Keycloak client-authenticator validation
→ replay cache/jti policy
→ client_credentials token
```

Private-key JWT znižuje potrebu distribuovať shared secret, ale private key môže byť stále exportovateľný a replaynutý z compromised hosta. mTLS môže viazať client authentication alebo token na certificate/key possession podľa deployment contractu. Federovaná workload identity môže odstrániť long-lived Keycloak credential, ale pridáva trust chain medzi Kubernetes/cloud identity providerom, token exchange alebo client-authentication SPI a Keycloakom.

Acceptance musí overiť exact key/certificate generation, issuer/audience assertion, clock skew, replayed `jti`, expired assertion, wrong client a predecessor-key retirement. „Používame JWT“ bez key custody a replay modelu nie je bezpečnostný verdict.

## 8. Client secret a key rotation

Credential rotation má tri odlišné outcomes:

```text
nové client authentication requests
→ používajú successor credential

staré credential
→ odmietnuté po overlap/retirement boundary

už vydané access tokens
→ zostávajú podľa vlastného lifespan/revocation contractu
```

Secret alebo key rotation nezmení už vydaný access token. Incident response musí preto sledovať credential descendants. Bez krátkeho access-token TTL, session/token revocation alebo resource-server current-policy checku môže attacker pokračovať aj po úspešnej credential rotation.

Safe rotation pre machine fleet potrebuje consumer inventory a staged rollout. Pri private-key JWT sa najprv publikuje successor public key, potom sa workload cohort prepne na successor signing key, následne sa overí druhý token a až potom sa predecessor odstráni. Pri statickom secre­te treba explicitne vedieť, ktoré Pods, jobs a externé systems ešte používajú predecessor hodnotu.

## 9. Audience, caller identity a local authorization

Resource server nesmie akceptovať machine token iba podľa role. Minimálny contract je:

```text
iss == atlas-prod issuer
AND signature/key generation je trusted
AND token je neexpirovaný a správneho type-u
AND aud contains settlement-api
AND azp/client identity == settlement-batch
AND sub == expected service-account user alebo workload subject class
AND role contains settlement.reconcile.batch
AND tenant == operation tenant
AND requested resource/action je v local allowlist-e
AND operation ID je idempotentný
```

`azp` alebo client ID je dôležitý, pretože dve machine identities môžu mať rovnakú client role. Service-account `sub` odlišuje delete/recreate alebo odlišný linked user. Tenant claim nesmie pochádzať z mutable user-editable attribute. Business operation musí byť viazaná na operation ID a resource ownera.

Broad multi-audience token umožní compromised service replaynúť credential voči ďalšiemu API. Service-specific audience alebo token exchange znižujú blast radius, ale nenahrádzajú local action/resource authorization.

## 10. Retry, idempotency a token theft

Machine workloads retryujú pri timeoutoch. Token issuance success a business mutation success sú odlišné outcomes. Pri strate API response nemá client automaticky vytvoriť nový operation ID a zopakovať side effect.

```text
operationId reconcile-2026-08-01-991
+ machine client settlement-batch
+ tenant orion
+ desired reconciliation generation 184
→ API deduplication ledger
→ one authoritative business result
```

Token `jti` nie je automaticky business idempotency key. Nový token vytvorí nový `jti`, ale môže retryovať tú istú operation. Resource server potrebuje durable operation ledger a caller/resource binding.

Pri token theft sa attack path často začína mimo Keycloak: CI log, Pod environment, mounted secret, crash dump, proxy trace alebo debug endpoint. Keycloak event ukazuje token request podľa clienta, nie nutne compromised workload host. Correlation preto spája token endpoint event, source network, credential/key generation, workload Pod/VM identity, API request ID a business operation ID.

## 11. Admin REST API service accounts

Automation pre Keycloak Admin REST API často dostane roles z `realm-management` clienta. Role ako `manage-users`, `manage-clients`, `manage-realm` alebo `realm-admin` majú veľmi odlišný blast radius. Broad `realm-admin` pre CI job znamená schopnosť meniť clients, redirects, mappers, keys, flows a sessions v realm-e.

Preferovaný model oddeľuje read-only inventory, scoped user lifecycle, client deployment a emergency administration do samostatných clients alebo workload identities. Admin API caller musí používať intended realm a explicitné target IDs. Query `clientId=foo` bez kontroly internal ID a realm base URL môže mutovať nesprávny object.

Forbidden test pre user-provisioning automation overí, že nevie meniť realm keys, authentication flows ani unrelated clients. Positive test overí presný create/update/read-back lifecycle a second-run idempotency.

## 12. Connected incident `KC-PAY-66` — machine path

Client `settlement-ops` reprezentoval desktop CLI aj batch workload. Mal client secret distribuovaný v CLI balíku, Service Accounts capability, Standard Flow, Direct Access Grants a `Full Scope Allowed`. Service-account user zdedil composite realm role `settlement-operator`, ktorá zahŕňala reconcile aj export permissions.

Po extrakcii secretu útočník získal client-credentials token. Browser MFA, password policy ani remembered SSO nemali na grant žiadny vplyv. Token mal broad `aud=settlement-api`, `tenant_id=orion` a export role. API kontrolovalo signature, expiry, audience a role, ale nie expected client pre konkrétnu operation ani tenant/resource binding.

```text
shared secret v public CLI
→ confidential machine capability na rovnakom clientovi
→ client_credentials bez human authentication
→ broad role-scope projection
→ valid machine token
→ API role-only authorization
→ export a reconciliation operations
```

Rotácia secretu zastavila nové token requests, ale už vydaný päťminútový token zostal prijateľný. Incident closure preto vyžadoval credential retirement, token/session descendant handling a API policy update.

## 13. Evidence-preserving containment a recovery

Zachovaj:

```text
client internal ID a configuration export hash
+ service-account user ID a effective role graph
+ role scope mappings a mapper IDs
+ credential method a key/secret generation
+ token request event, source IP a timestamp
+ raw token hash, jti, iat, exp, aud, azp, sub
+ workload deployment/Pod/VM identity
+ API request a business operation IDs
+ affected tenant/resource inventory
```

Containment môže disable-nuť clienta, zastaviť workload cohort, zablokovať high-risk API operations a odobrať affected credential. Recovery rozdelí mixed-purpose clienta, vypne unused grants, zavedie workload-bound authentication, explicitné role scope mappings, service-specific audience a local caller/resource authorization. Stale token path sa rieši podľa TTL, not-before/revocation a API enforcement contractu.

## 14. Positive, recovery a forbidden acceptance

Positive path:

```text
settlement-batch successor workload identity
→ client_credentials s successor keyom
→ aud settlement-api
→ azp settlement-batch
→ jediná reconcile role
→ intended tenant/resource operation succeeds once
```

Forbidden paths:

```text
old secret alebo predecessor key po retirement
→ token endpoint rejects

settlement-batch token voči export endpointu
→ local action policy rejects

správna role, wrong tenant/resource
→ ownership policy rejects

browser/native client sa pokúsi client_credentials
→ capability alebo client authentication rejects

stale access token po incident cutoff
→ rejects podľa descendant-revocation contractu
```

Second-token test získa nový token po nezmenenej konfigurácii a porovná audience, caller, role a claim shape. Second-operation test retryne rovnaký operation ID a musí vrátiť rovnaký business result bez duplicate side effectu.

## 15. Kontrolné otázky

- Ktorý exact client, service-account user, credential a workload generation token reprezentuje?
- Je client confidential iba preto, že má secret, alebo credential skutočne chráni trusted runtime?
- Ktoré role má service-account user a ktoré prejdú role-scope intersectionom?
- Sú Standard Flow, Direct Access Grants alebo iné nepotrebné capabilities vypnuté?
- Overuje API audience, caller client, service-account subject, tenant, resource a action?
- Je credential rotation oddelená od already-issued-token revocation?
- Má automation durable operation ID a second-run idempotency?
- Prešli positive, old-credential, wrong-client, wrong-audience, wrong-tenant, stale-token a second-operation paths?

## Glossary impact

Relevantné pojmy: Keycloak service account, service-account user, client-credentials grant, machine identity subject, role-scope intersection, client authentication, private-key JWT, mTLS client authentication, credential generation, workload-bound identity, machine audience, descendant token a M2M acceptance matrix.

## Primárne zdroje

- [Keycloak — Server Administration Guide: Using a service account](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak — Securing applications and services: Service accounts](https://www.keycloak.org/securing-apps/oidc-layers)
- [RFC 6749 — OAuth 2.0 Client Credentials Grant](https://www.rfc-editor.org/rfc/rfc6749.html)
- [RFC 7523 — JWT Profile for OAuth 2.0 Client Authentication](https://www.rfc-editor.org/rfc/rfc7523.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Public, confidential a bearer-only client model](public-confidential-and-bearer-only-clients.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Authentication flows, executions a required actions →](authentication-flows-executions-and-required-actions.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
