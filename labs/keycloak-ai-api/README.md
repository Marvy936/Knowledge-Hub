# Keycloak-secured AI API — Practical v1

Tento lab implementuje identity a authorization foundation pre Practical v1 AI API. Používa lokálny Keycloak development realm, public Authorization Code + PKCE klienta, confidential service account a resource server, ktorý validuje JWT cryptografiu, issuer, audience, access-token class, caller (`azp`) a exact client roles.

```text
browser user
→ Authorization Code + PKCE S256
→ Keycloak access token
→ issuer/JWKS/signature/time/audience validation
→ azp + client-role authorization
→ bounded RAG route

service account
→ Client Credentials
→ Keycloak access token
→ rovnaká token authority
→ automation-only agent routes
```

Source blok zámerne nevykonáva RAG, agent ani remediation side effects. Chránené endpoints vracajú iba authorization evidence a explicitne označujú execution boundary.

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
- Client secret nie je commitnutý v realm JSON.
- Service-account user má explicitné `knowledge-hub-api` client roles pre local source contract.

Po importe sa generated client secret získa z Keycloak Credentials UI/admin API a vloží sa iba do environmentu:

```bash
export KEYCLOAK_AUTOMATION_CLIENT_SECRET='<generated-local-secret>'
```

## Audience a access-token marker

Default client scope `knowledge-hub-api-access` pridáva dva explicitné protocol mappers.

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

Resource server preto nemusí hádať, či mu niekto poslal access token alebo ID token. Token bez `token_use=access` je refusal.

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

Nonce je súčasť authorization requestu/session. Tento source block však ešte nevykonáva plnú browser-side ID-token cryptographic validation; live browser client integration je samostatný runtime gate.

## Client Credentials flow

Automation token:

```bash
python labs/keycloak-ai-api/scripts/request_client_credentials.py \
  --token-output .runtime/keycloak/automation-access.jwt
```

Client secret sa číta iba z `KEYCLOAK_AUTOMATION_CLIENT_SECRET`. Token helper nepíše secret ani access token do logu. Output path musí byť fresh.

## API resource server

Inštalácia:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e 'labs/keycloak-ai-api[dev]'
```

Spustenie:

```bash
export KEYCLOAK_ISSUER='http://127.0.0.1:8080/realms/knowledge-hub'
uvicorn keycloak_ai_api.app:app --host 127.0.0.1 --port 8090
```

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

Po PyJWT audience validation sa audience normalizuje a tento Practical v1 contract vyžaduje presne jediný accepted audience `knowledge-hub-api`. Token s ďalším audience je odmietnutý; ak sa neskôr zavedie legitímny multi-audience contract, musí to byť explicitná policy-generation zmena.

API roles sa čítajú iba z:

```text
resource_access["knowledge-hub-api"]["roles"]
```

## Route policy matrix

| Route | Allowed `azp` | Required client role | Execution boundary |
|---|---|---|---|
| `POST /v1/rag/query` | `knowledge-hub-web`, `knowledge-hub-automation` | `rag.read` | authorization-only |
| `POST /v1/agent/run` | `knowledge-hub-automation` | `agent.run` | authorization-only |
| `POST /v1/agent/remediate` | `knowledge-hub-automation` | `agent.remediate` | authorization-only |

Browser token s `rag.read` preto nemôže spustiť automation route len preto, že je inak platný.

## 401 vs 403

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
- token nemá required `knowledge-hub-api` client role.

## Source negative matrix

Test source pokrýva:

- valid access token,
- wrong issuer,
- wrong audience,
- additional audience,
- wrong signing key,
- expired token,
- future `nbf`,
- ID-token marker namiesto access markeru,
- wrong authorized party,
- missing client role,
- 401/403 HTTP route semantics,
- exact PKCE S256 form bez client secretu,
- realm config refusal assumptions: no committed automation secret, implicit/password grants off, access-only audience/token marker.

## Runtime evidence boundary

[`RUNTIME-EVIDENCE.md`](RUNTIME-EVIDENCE.md) zostáva `Pending`.

Tento source block ešte nepreukazuje:

- že Keycloak 26.7.0 container reálne na tomto commite nabootoval,
- že realm JSON sa úspešne importoval,
- discovery/JWKS read-back,
- browser Authorization Code exchange,
- service-account Client Credentials exchange,
- live role mapping v vydanom tokene,
- protected HTTP request proti živému Keycloaku,
- token/session cleanup po reálnom flow,
- production TLS, reverse proxy, HA, external DB, rotation alebo backup/restore.

## Cleanup

Runtime artifacts patria do `.runtime/keycloak` a nesmú sa commitovať. Po live teste:

```bash
rm -rf .runtime/keycloak
docker compose -f labs/keycloak-ai-api/compose.yaml down -v
```

Cleanup je runtime-verified až po read-backu, že token/session paths, container a disposable volume už neexistujú.
