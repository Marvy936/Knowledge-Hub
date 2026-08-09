# Keycloak-secured AI API — Practical v1

Tento lab implementuje identity a authorization boundary pre Practical v1 AI API a voliteľné executable adapters pre promoted RAG a bounded operations agent. Používa lokálny Keycloak development realm, public Authorization Code + PKCE klienta, confidential service account a resource server, ktorý validuje JWT cryptografiu, issuer, audience, access-token class, required API scope, caller (`azp`) a exact client roles.

```text
browser user
→ Authorization Code + PKCE S256
→ Keycloak access token
→ issuer/JWKS/signature/time/audience/token_use validation
→ knowledge-hub-api-access scope
→ azp + client-role authorization
→ promoted RAG adapter

service account
→ Client Credentials
→ Keycloak access token
→ rovnaká token authority
→ automation-only bounded agent routes
→ separate human approval pre mutation
```

Default `keycloak_ai_api.app:app` sa spúšťa bez RAG a agent adapterov. V tomto režime resource server stále vykoná authentication/authorization, ale po úspešnej autorizácii vráti `503`, pretože executable backend nie je nakonfigurovaný. Package ako celok však už obsahuje dva explicitné adapters:

- [`PROMOTED-RAG-INTEGRATION.md`](PROMOTED-RAG-INTEGRATION.md) — exact promoted RAG lifecycle za `rag.read`,
- [`BOUNDED-AGENT-INTEGRATION.md`](BOUNDED-AGENT-INTEGRATION.md) — local-only bounded incident agent za `agent.run` a `agent.remediate`.

JWT role sama osebe nie je mutation authority. `agent.remediate` navyše vyžaduje exact external approval artifact, policy/kill-switch read-back a durable operation contract z `labs/agent-ops`.

## Local Keycloak

Compose pinne presný development image:

```text
quay.io/keycloak/keycloak:26.7.0
```

Keycloak je publikovaný iba na `127.0.0.1:8080` a spúšťa sa cez `start-dev --import-realm`. `start-dev` je development-only režim; tento compose nie je production deployment contract.

Pred spustením nastav bootstrap admin credentials iba v shell environment:

```bash
export KEYCLOAK_BOOTSTRAP_ADMIN_USERNAME=admin
export KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD='<local-disposable-password>'

docker compose -f labs/keycloak-ai-api/compose.yaml up
```

Realm import je v:

```text
labs/keycloak-ai-api/realm/knowledge-hub-realm.json
```

Import neobsahuje browser-user heslo ani automation client secret.

## Realm subjects

Realm: `knowledge-hub`

### `knowledge-hub-web`

Public browser client:

- Standard/Authorization Code flow enabled.
- PKCE `S256` required.
- Implicit flow disabled.
- Direct Access Grants/password grant disabled.
- Service account disabled.
- Exact callback `http://127.0.0.1:8765/callback`.
- Exact web origin `http://127.0.0.1:8765`.
- Default client scope `knowledge-hub-api-access` included.

Browser používateľ nedostáva API oprávnenie automaticky. Pre local live test sa vytvorí test user a priradí sa mu iba potrebná client role, typicky `knowledge-hub-api/rag.read`.

### `knowledge-hub-api`

Resource/audience client definuje client roles:

- `rag.read`,
- `agent.run`,
- `agent.remediate`.

API neprijíma realm role ako náhradu za tieto resource roles.

### `knowledge-hub-automation`

Confidential service-account client:

- Standard flow disabled.
- Implicit flow disabled.
- Direct Access Grants disabled.
- Service account enabled.
- Default client scope `knowledge-hub-api-access` included.
- Client secret nie je commitnutý v realm JSON.
- Service-account user má explicitné `knowledge-hub-api` client roles pre local source contract.

Po importe sa generated client secret získa z Keycloak Credentials UI/admin API a vloží sa iba do environmentu:

```bash
export KEYCLOAK_AUTOMATION_CLIENT_SECRET='<generated-local-secret>'
```

## Audience, API scope a access-token marker

Default client scope `knowledge-hub-api-access` má `include.in.token.scope=true` a pridáva dva explicitné protocol mappers.

Audience mapper:

```text
oidc-audience-mapper
included.client.audience = knowledge-hub-api
access.token.claim = true
id.token.claim = false
```

Hardcoded access marker:

```text
claim.name = token_use
claim.value = access
access.token.claim = true
id.token.claim = false
```

Resource server preto nemusí hádať, či mu niekto poslal access token alebo ID token. Token bez `token_use=access` je authentication refusal. Kryptograficky validný access token, ktorému v `scope` claim chýba exact `knowledge-hub-api-access`, je authorization refusal aj vtedy, ak má správnu client role.

Scope a role majú odlišný význam:

```text
knowledge-hub-api-access scope
→ token patrí do API access contractu

resource client role
→ konkrétny caller smie vykonať konkrétnu route
```

Jedno nenahrádza druhé.

## PKCE browser flow

Vytvorenie disposable session:

```bash
python labs/keycloak-ai-api/scripts/begin_pkce.py \
  --session-output .runtime/keycloak/pkce-session.json
```

Script vypíše authorization URL, ale nevypíše code verifier. Session file má byť mode `0600` v Linux/WSL execution profile a obsahuje verifier, state a nonce.

Po prihlásení a redirecte sa code a state vymenia:

```bash
python labs/keycloak-ai-api/scripts/exchange_pkce_code.py \
  --session .runtime/keycloak/pkce-session.json \
  --code '<authorization-code>' \
  --returned-state '<returned-state>' \
  --token-output .runtime/keycloak/browser-access.jwt
```

Exchange:

- porovnáva callback `state`,
- posiela exact `code_verifier`,
- nepoužíva client secret,
- povoľuje HTTPS alebo explicitný loopback HTTP token endpoint,
- zapisuje access token do fresh disposable file,
- token value nevypisuje do stdout,
- po úspechu zmaže PKCE session/verifier,
- ID token nepoužíva ako API bearer token.

Nonce je súčasť authorization requestu/session. Source block ešte nevykonáva plnú browser-side ID-token cryptographic validation; live browser client integration je samostatný runtime gate.

## Client Credentials flow

Automation token:

```bash
python labs/keycloak-ai-api/scripts/request_client_credentials.py \
  --token-output .runtime/keycloak/automation-access.jwt
```

Client secret sa číta iba z `KEYCLOAK_AUTOMATION_CLIENT_SECRET`. Token helper nepíše secret ani access token do logu. Output path musí byť fresh.

## API resource server

Základná inštalácia identity/RAG package:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e 'labs/keycloak-ai-api[dev]'
```

Default auth boundary bez executable backendov:

```bash
export KEYCLOAK_ISSUER='http://127.0.0.1:8080/realms/knowledge-hub'
uvicorn keycloak_ai_api.app:app --host 127.0.0.1 --port 8090
```

Pre bounded agent sa explicitne inštaluje aj sibling package a používa sa dedicated runner; exact lifecycle je v [`BOUNDED-AGENT-INTEGRATION.md`](BOUNDED-AGENT-INTEGRATION.md).

JWKS URL sa odvodí iba z operatorom nakonfigurovaného issueru:

```text
<issuer>/protocol/openid-connect/certs
```

Token si nikdy neurčuje vlastný issuer/JWKS trust anchor.

## Token validation contract

Resource server povoľuje iba `RS256` a vyžaduje header `kid`.

Cryptographically/identity valid token musí prejsť:

- signature cez configured realm JWKS,
- exact issuer,
- expected audience `knowledge-hub-api`,
- `exp`,
- `iat`,
- `nbf` ak je prítomné,
- `sub`,
- `azp`,
- `jti`,
- `token_use=access`.

Po PyJWT audience validation sa audience normalizuje a Practical v1 contract vyžaduje presne jediný accepted audience `knowledge-hub-api`. Token s ďalším audience je odmietnutý; legitímny budúci multi-audience contract musí byť explicitná policy-generation zmena.

Authorization potom vyžaduje:

- allowed route `azp`,
- exact scope `knowledge-hub-api-access`,
- required client role z `resource_access["knowledge-hub-api"]["roles"]`.

## Route policy matrix

| Route | Allowed `azp` | Required scope | Required client role | Execution boundary |
|---|---|---|---|---|
| `POST /v1/rag/query` | `knowledge-hub-web`, `knowledge-hub-automation` | `knowledge-hub-api-access` | `rag.read` | promoted RAG only when exact RAG adapter is configured; otherwise `503` |
| `POST /v1/agent/run` | `knowledge-hub-automation` | `knowledge-hub-api-access` | `agent.run` | bounded inspection/diagnostic/plan only; no mutation |
| `POST /v1/agent/remediate` | `knowledge-hub-automation` | `knowledge-hub-api-access` | `agent.remediate` | mutation only through exact external approval + policy + kill-switch + durable operation contract |

Browser token s `rag.read` preto nemôže spustiť automation route len preto, že je inak platný. Automation token s `agent.remediate` rolou nemôže obísť approval artifact.

## Liveness a readiness

`GET /healthz` rozlišuje nakonfigurovaný RAG a agent backend.

- process môže byť live aj bez executable adaptera,
- `/readyz` je RAG readiness,
- `/readyz/agent` je bounded-agent readiness a pinne exact policy ID/generation,
- missing backend je `503`, nie predstieraná readiness.

## 401 vs 403 vs backend refusal

`401 Unauthorized`:

- bearer token chýba,
- JWT format/header je invalid,
- algorithm nie je RS256,
- `kid` chýba,
- signature/JWKS validation zlyhá,
- issuer/audience/time claims zlyhajú,
- `token_use` nie je `access`.

`403 Forbidden`:

- token je validný, ale `azp` nie je povolený pre route,
- token nemá required `knowledge-hub-api-access` scope,
- token nemá required `knowledge-hub-api` client role.

Po úspešnej autorizácii môže request stále skončiť explicitným backend refusalom:

- `503` — executable backend nie je configured alebo RAG backend nie je ready/valid,
- `409` — bounded agent planning/remediation safety contract odmietol request.

Authentication success teda nie je execution success.

## Source negative matrix

Test source pokrýva identity a route boundary vrátane:

- valid access token,
- wrong issuer,
- wrong audience,
- additional audience,
- wrong signing key,
- expired token,
- future `nbf`,
- ID-token marker namiesto access markeru,
- wrong authorized party,
- missing API scope,
- missing client role,
- 401/403 HTTP semantics,
- missing backend readiness,
- protected promoted-RAG execution a wrong-release refusal,
- oddelené `agent.run` a `agent.remediate` role,
- invalid agent request bez backend callu,
- wrong-policy agent result,
- injected extra tool-output field,
- bounded explicit recovery checkpoint,
- exact runtime filesystem/symlink boundary,
- exact PKCE S256 form bez client secretu,
- realm config assumptions: no committed automation secret, implicit/password grants off, access-only audience/token marker a API client scope.

Existencia test source nie je sama osebe runtime evidence. Kým issue #151 nevytvorí authoritative workflow run alebo nevznikne explicitný equivalent runtime record, `Runtime verified` zostáva `Nie`.

## Runtime evidence boundary

[`RUNTIME-EVIDENCE.md`](RUNTIME-EVIDENCE.md) zostáva `Pending`.

Source vrstva ešte nepreukazuje:

- že Keycloak 26.7.0 container reálne na aktuálnom commite nabootoval,
- že realm JSON sa úspešne importoval,
- discovery/JWKS read-back,
- browser Authorization Code exchange,
- service-account Client Credentials exchange,
- live scope/role mapping v vydanom tokene,
- protected RAG alebo agent HTTP request proti živému Keycloaku,
- token/session cleanup po reálnom flow,
- approval expiry,
- wall-clock/tool resource limit pre agent mutation,
- retrieved-content → agent injection evaluation,
- production TLS, reverse proxy, HA, external DB, rotation alebo backup/restore.

## Cleanup

Keycloak token/session artifacts patria do `.runtime/keycloak` a nesmú sa commitovať. Po live identity teste:

```bash
rm -rf .runtime/keycloak
docker compose -f labs/keycloak-ai-api/compose.yaml down -v
```

Bounded-agent runtime patrí striktne do `.runtime/agent-ops`; jeho cleanup contract je dokumentovaný v [`BOUNDED-AGENT-INTEGRATION.md`](BOUNDED-AGENT-INTEGRATION.md) a `labs/agent-ops/README.md`.

Cleanup je runtime-verified až po read-backu, že deklarované token/session/runtime paths, container a disposable volume už neexistujú.
