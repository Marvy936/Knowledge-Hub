# Keycloak-secured AI API runtime evidence

> **Evidence status: Runtime verified for automated local service-account/JWKS/protected-API Practical v1 profile**

Tento dokument je authoritative runtime evidence contract pre Practical v1 identity path. Canonical combined release baseline na `789b5038b81b9342b1aef57b809bd3b67202ebde` a standalone Keycloak run `31542501300` (successful rerun attempt 2) verify disposable local Keycloak, live JWKS/service-account token validation and protected RAG/agent API paths. Actual interactive browser Authorization Code exchange remains explicitly not executed and is not claimed by this automated profile.

## Required execution subject

Budúci runtime record musí pinovať minimálne:

```text
Git subject SHA
Python version
Keycloak image = quay.io/keycloak/keycloak:26.7.0
realm = knowledge-hub
issuer = http://127.0.0.1:8080/realms/knowledge-hub
resource audience = knowledge-hub-api
required scope = knowledge-hub-api-access
public client = knowledge-hub-web
service client = knowledge-hub-automation
```

Dependency resolution pre Python package a container image identity musia byť zaznamenané pred testom. Mutable image tag bez read-backu resolved container/image identity nie je dostatočný release proof.

## Required live bootstrap evidence

Gate musí preukázať celý bootstrap, nie iba validitu JSON súboru:

```text
fresh disposable runtime
→ Keycloak container start
→ realm import
→ health/readiness
→ OIDC discovery read-back
→ JWKS read-back
→ exact issuer confirmation
```

Required evidence:

- container/revision identity,
- successful realm import bez ručnej editácie,
- discovery document získaný z configured issueru,
- JWKS s použiteľným RS256 signing key `kid`,
- žiadny automation secret v Git history alebo stdout/stderr evidence,
- cleanup target identita pred ďalším flowom.

## Browser/public-client PKCE evidence

Practical v1 nepotrebuje browser UI automation ako production end-to-end test, ale musí preukázať live Authorization Code + PKCE authority boundary.

Minimum:

1. `knowledge-hub-web` je public client bez client secretu,
2. authorization request používa `code_challenge_method=S256`, state a nonce,
3. Direct Access Grants/password grant a implicit flow zostávajú disabled,
4. authorization code exchange používa exact code verifier a neposiela client secret,
5. returned state musí sedieť s disposable session subjectom,
6. session/verifier artifact sa po úspešnom exchange odstráni,
7. výsledný access token je možné validovať proti live realm JWKS a exact issueru.

Ak browser login zostane manuálny interaction step, evidence musí explicitne odlíšiť manual user-authentication step od automatizovaného token/API validation pathu. Manuálny klik nesmie skryť ďalší nezdokumentovaný setup krok.

## Service-account Client Credentials evidence

Automation path musí byť reprodukovateľný bez committed secretu:

```text
generated local client secret in environment only
→ Client Credentials token request
→ access token
→ live JWT/JWKS validation
→ exact audience + token_use + scope + azp + client roles
```

Token read-back musí potvrdiť:

- `iss` = exact local issuer,
- jediný accepted API audience = `knowledge-hub-api`,
- `token_use=access`,
- `scope` obsahuje `knowledge-hub-api-access`,
- `azp=knowledge-hub-automation`,
- `resource_access["knowledge-hub-api"]["roles"]` obsahuje role očakávané pre daný positive scenár,
- `exp`, `iat`, voliteľné `nbf`, `sub` a `jti` spĺňajú resource-server contract.

Raw client secret ani raw bearer token nesmú byť uložené do committed evidence alebo log outputu. Evidence môže obsahovať iba redacted metadata/digests, ktoré nepotrebujú opätovné použitie credentialu.

## Protected API positive evidence

Live API musí bežať na loopbacke a používať configured live Keycloak issuer/JWKS.

### RAG

```text
valid browser alebo automation token
+ scope knowledge-hub-api-access
+ client role rag.read
→ POST /v1/rag/query
→ authentication/authorization success
→ exact promoted-RAG backend identity alebo explicitne scoped auth-only proof
```

Pre celý Practical v1 flagship musí byť nakonfigurovaný promoted RAG adapter; `503 backend not configured` nie je positive business path.

### Agent planning

```text
valid automation token
+ agent.run
→ POST /v1/agent/run
→ bounded inspection/diagnostic/plan
→ no mutation
```

Optional `knowledge_query` scenár musí používať promoted RAG backend a result zredukovať na canonical read-only retrieval context. `retrieval_context_id` musí byť viazaný na plan identity, nie na mutation action digest.

### Agent remediation

```text
valid automation token
+ agent.remediate
+ separately created exact approval artifact
→ POST /v1/agent/remediate
→ one bounded mutation alebo safe read-only reconciliation
```

JWT role nesmie nahradiť approval artifact, policy/kill-switch read-back ani durable operation state.

## Required negative authorization matrix

Gate musí proti live Keycloaku/resource serveru odlíšiť authentication failure od authorization failure.

### `401` refusal

Minimálne:

- missing bearer token,
- expired token,
- wrong issuer,
- wrong audience,
- invalid signature/wrong signing key alebo nepoužiteľný `kid`,
- ID-token marker alebo missing/wrong `token_use=access`.

### `403` refusal

Minimálne:

- valid token s wrong `azp`,
- missing `knowledge-hub-api-access` scope,
- insufficient client role,
- browser/public-client token na automation-only agent route.

Negative request nesmie zavolať RAG alebo agent side-effect backend pred úspešnou authorization boundary.

## Safety and mutation authority evidence

Identity success nie je remediation success. Live combined gate musí preukázať, že:

- `agent.run` nevykoná side effect,
- `agent.remediate` bez exact approval artifactu skončí refusalom,
- expired approval nevytvorí novú mutation authority,
- engaged kill switch blokuje novú mutation/retry authority,
- completed operation sa dá read-only reconciliovať bez duplicate side effectu,
- retrieved prompt-injection abstention nevytvorí tool/action digest,
- prompt-like extra field v tool result je odmietnutý strict typed schema boundary.

Tieto body môžu odkazovať na exact bounded-agent evidence record, ak je spustený v tom istom immutable release subjecte a identity chain je explicitne prepojený.

## Cleanup evidence

Cleanup musí byť vykonaný aj po failure scenári.

Required cleanup:

```text
.runtime/keycloak token/session artifacts removed
.runtime/agent-ops removed when combined agent path was used
Keycloak compose stack stopped
container removed
anonymous/disposable volumes removed
temporary client/user/secret state removed with disposable realm/container
```

Po cleanup-e musí read-back potvrdiť non-existence deklarovaných runtime paths a neprítomnosť live disposable container/volume subjectov.

Secret/token cleanup sa nesmie dokazovať vypísaním secretu alebo bearer tokenu do logu.

## Evidence record fields

Finálny successful record musí obsahovať aspoň:

- exact Git SHA,
- workflow/run alebo equivalent execution ID,
- resolved Python dependencies,
- resolved Keycloak image/container identity,
- issuer/discovery/JWKS metadata bez private key materialu,
- PKCE flow result boundary,
- service-account token claim summary bez raw tokenu,
- positive route matrix resulty,
- negative 401/403 matrix resulty,
- optional promoted-RAG release/source IDs,
- optional bounded-agent policy/plan/operation/result IDs,
- cleanup read-back,
- canonical evidence ID alebo immutable evidence artifact identity,
- explicit proof boundary.

## Proof boundary

Úspešný Practical v1 Keycloak runtime gate preukáže lokálny disposable identity provider, live OIDC/JWKS trust chain, public PKCE a confidential service-account contracts, exact API scope/role boundary a secured local RAG/agent path v deklarovanom loopback profile.

Nepreukáže:

- production TLS/reverse proxy,
- external production database,
- HA/multi-AZ,
- LDAP/AD federation,
- WebAuthn alebo identity brokering,
- secret rotation platform,
- Operator lifecycle,
- backup/restore alebo disaster recovery,
- production readiness.

Exact automated local identity record existuje; real-browser Authorization Code exchange a production identity-platform boundaries uvedené vyššie zostávajú mimo automated Practical v1 claimu.
