# Live Keycloak identity runtime gate

Tento gate preukazuje jeden bounded Practical v1 identity path cez reálny disposable Keycloak, live OIDC/JWKS a live protected RAG/agent HTTP API. Nepredstiera production identity platformu a neautomatizuje interaktívny browser login.

Canonical executable driver:

```text
labs/keycloak-ai-api/scripts/run_live_identity_gate.py
```

Dedicated hosted workflow:

```text
.github/workflows/keycloak-live-identity-runtime.yml
```

Pôvodný rozpracovaný `run_live_identity_runtime.py` nie je authoritative workflow entrypoint. Runtime evidence sa smie viazať iba na canonical gate vyššie.

## Runtime composition

Gate skladá existujúce authoritative komponenty:

```text
realm/knowledge-hub-realm.json
→ compose.yaml
→ begin_pkce.py
→ request_client_credentials.py
→ existing RAG corpus/index/eval/release CLIs
→ existing bounded-agent bootstrap/approval tools
→ run_secured_agent_rag_api.py
```

Nevytvára druhý resource server, druhý RAG engine ani druhý agent executor.

## 1. Exact disposable Keycloak

Driver vyžaduje exact loopback issuer:

```text
http://127.0.0.1:8080/realms/knowledge-hub
```

Pred štartom odmietne obsadený Keycloak alebo API port. Compose dostane unique exact project name viazaný na Git subject, runtime-generated bootstrap admin username a runtime-generated password. Credentials zostávajú iba v process environment/memory.

Po importe gate číta:

- OIDC discovery,
- exact discovery issuer,
- realm JWKS URI,
- minimálne jeden JWKS key,
- configured container image tag,
- local content-addressed Docker image ID.

Pinned development image contract je:

```text
quay.io/keycloak/keycloak:26.7.0
```

Local Docker image ID sa zaznamená do evidence. Gate netvrdí remote OCI Registry manifest digest.

## 2. Live realm/client contract read-back

Gate používa runtime bootstrap admin iba na read-back a bounded negative-test mutations.

Importovaný `knowledge-hub-web` musí byť:

```text
publicClient=true
standardFlowEnabled=true
PKCE=S256
implicitFlowEnabled=false
directAccessGrantsEnabled=false
serviceAccountsEnabled=false
```

Importovaný `knowledge-hub-automation` musí byť:

```text
publicClient=false
serviceAccountsEnabled=true
standardFlowEnabled=false
directAccessGrantsEnabled=false
```

Client scope `knowledge-hub-api-access` musí byť zahrnutý do access-token scope claimu a jeho audience mapper musí smerovať na:

```text
knowledge-hub-api
```

## 3. PKCE boundary

Driver spustí existujúci:

```text
begin_pkce.py
```

A overí disposable session artifact:

- code verifier,
- state,
- nonce,
- mode `0600` na Linux execution profile.

Live Keycloak admin read-back zároveň overí S256 policy public clienta.

Gate však nevykonáva interaktívny browser login ani Authorization Code callback/exchange. Evidence to explicitne zaznamená:

```text
authorization_code_exchange_executed=false
```

Practical v1 live identity claim je preto:

```text
live imported public-client PKCE contract + real PKCE session helper
```

nie:

```text
fully automated browser login
```

## 4. Live service-account Client Credentials

Automation client secret sa po realm importe získa z live Keycloak Admin API. Secret:

- nie je commitnutý,
- nezapisuje sa do canonical evidence,
- neposiela sa do CLI argumentov,
- existujúci token helper ho číta iba z environmentu.

Token sa vydá cez existing:

```text
request_client_credentials.py
```

Positive token musí mať exact:

- issuer,
- single accepted audience `knowledge-hub-api`,
- `azp=knowledge-hub-automation`,
- `token_use=access`,
- scope `knowledge-hub-api-access`,
- client roles `rag.read`, `agent.run`, `agent.remediate`.

Raw secret ani bearer token value sa nezapisujú do evidence.

## 5. Negative tokens vydáva live Keycloak

Gate nepoužíva lokálne podpísaný fake JWT na authorization matrix. Negative access tokeny vydáva ten istý disposable Keycloak po jednej bounded temporary policy mutation a následnom restore.

### Wrong audience

Audience mapper sa dočasne zmení na:

```text
knowledge-hub-wrong-audience
```

Token musí obsahovať intended wrong audience a nesmie obsahovať accepted `knowledge-hub-api`. Mapper sa potom obnoví.

### Missing API scope

`include.in.token.scope` sa dočasne vypne pre API client scope. Vydaný token musí zachovať správne audience, ale nesmie obsahovať `knowledge-hub-api-access`. Scope representation sa potom obnoví.

### Missing `agent.remediate` role

Service-account userovi sa dočasne odoberie iba exact `knowledge-hub-api/agent.remediate` role. Vydaný token musí:

- zachovať `rag.read`,
- zachovať `agent.run`,
- nemať `agent.remediate`.

Role mapping sa potom obnoví.

### Expired access token

Realm access-token lifespan sa dočasne zníži na jednu sekundu, vydá sa token, pôvodná hodnota sa obnoví a gate čaká až za token `exp` boundary.

Tieto mutations slúžia iba disposable test realm-u a sú odstránené spolu s compose volume.

## 6. Signature-tamper negative variant

Tampered-signature token nemení posledný Base64URL znak, kde by sa pri niektorých signature lengths mohli meniť iba padding bits. Canonical helper zmení prvý znak signature segmentu a potom explicitne overí:

```text
decoded tampered signature bytes != decoded original signature bytes
```

Header a payload segment zostanú nezmenené. Resource server preto dostane token s rovnakými claims, ale kryptograficky iným podpisom.

## 7. Live protected promoted RAG

Pred API štartom driver z existujúcich RAG CLIs vytvorí exact:

```text
Git corpus
→ index
→ runtime config
→ hard eval
→ prompt release
```

Derived query musí byť `answered` už pri preflight query.

Combined secured runner potom dostane exact promoted bundle. Positive automation token musí prejsť:

```text
POST /v1/rag/query
→ HTTP 200
→ status=answered
→ canonical answer_id
→ canonical trace_id
```

## 8. Live protected bounded agent

Local agent sandbox sa inicializuje ako:

```text
payments-api
generation=1
status=degraded
restart_count=0
```

Policy pinne finite approval TTL, bounded tool wait a target allowlist. Kill switch je disengaged.

Authorized `agent.run` používa aj promoted Knowledge Hub query. Response musí mať:

- `approval_required`,
- exact `plan_id`,
- exact `retrieval_context_id`,
- exact `action_digest`.

Mutation approval nevytvára Keycloak route. Gate použije existujúci `approve_action.py` nad exact persisted plan/policy a až potom zavolá:

```text
POST /v1/agent/remediate
```

Positive outcome musí byť:

```text
generation 1 → 2
status degraded → healthy
restart_count 0 → 1
```

Rovnaký remediation request sa zopakuje. Replay musí skončiť HTTP success bez ďalšej mutácie a service state musí zostať byte-equivalent v relevantnom state read-backu.

## 9. Live 401/403 matrix

Po štarte resource servera sa očakáva:

| Variant | Expected |
|---|---:|
| missing bearer | 401 |
| byte-level tampered signature | 401 |
| live Keycloak wrong audience | 401 |
| live Keycloak missing API scope | 403 |
| live Keycloak missing `agent.remediate` role | 403 |
| live Keycloak expired token | 401 |

Tým sa rozlišuje authentication failure od authorization failure.

## 10. Secret/log boundary

Po stopnutí secured API gate číta jeho log a odmietne evidence, ak obsahuje:

- generated automation client secret,
- ktorýkoľvek raw bearer token vydaný počas testu.

Evidence ukladá iba SHA-256 API logu a boolean redaction results.

Tento check neclaimuje kompletný secret scan Keycloak interných development logov.

## Cleanup

Driver vždy:

1. stopne secured API process,
2. vykoná `docker compose down -v --remove-orphans` pre exact project,
3. odstráni `.runtime/keycloak`,
4. odstráni `.runtime/agent-ops`,
5. prečíta späť compose `ps -q`,
6. vyžaduje žiadny remaining runtime path ani compose container.

Až potom môže evidence dostať:

```text
cleanup_verified=true
```

Hosted workflow má navyše vlastný `always()` emergency cleanup.

## Canonical evidence

Evidence pinne minimálne:

- exact Git SHA,
- Keycloak image tag + local image ID,
- issuer/discovery/JWKS read-back,
- live realm-import marker,
- PKCE config/session boundary,
- positive service-account claim summary bez tokenu,
- RAG snapshot/index/eval/release IDs,
- protected RAG answer/trace IDs,
- agent plan/retrieval-context/action-digest/approval IDs,
- service state po remediation a replay,
- exact negative 401/403 outcomes,
- wrong-audience/missing-scope/missing-role confirmation,
- API-log redaction evidence,
- cleanup read-back,
- canonical evidence ID.

## Proof boundary

Successful exact-revision workflow preukáže:

```text
live local Keycloak import
→ live OIDC discovery + JWKS
→ live service-account Client Credentials token
→ live resource-server signature/issuer/audience/scope/role validation
→ live protected promoted RAG HTTP
→ live protected agent plan
→ separate approval
→ live local sandbox remediation + replay
→ live negative 401/403 token variants
→ cleanup
```

Nepreukáže:

- interactive browser login/Authorization Code exchange,
- production TLS/reverse proxy,
- LDAP/AD federation,
- WebAuthn,
- identity brokering,
- external production approval authority,
- multi-node Keycloak/HA,
- external database,
- rotation/backup/restore,
- production credentials or production remediation.

Kým `.github/workflows/keycloak-live-identity-runtime.yml` nevytvorí successful authoritative run, tento gate je `Implemented`, nie `Runtime verified`.
