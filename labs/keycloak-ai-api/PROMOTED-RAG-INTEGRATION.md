# Keycloak-secured promoted RAG integration

Táto vrstva pripája už implementovaný offline deterministic Knowledge Hub RAG flagship za Keycloak `rag.read` authorization gate. Resource server neakceptuje ľubovoľný `runtime-config.json`. Pred prvou query musí načítať a znovu overiť celý promoted RAG subject.

```text
valid Keycloak access token
+ rag.read client role
+ allowed azp
→ promoted RAG bundle read-back
→ runtime config validation
→ index ↔ chunk manifest rebuild validation
→ full eval-report deterministic rerun
→ prompt-release deterministic rebuild
→ exact release equality
→ bounded offline RAG query
→ answer/abstention + citations + trace
```

## Promoted bundle

`OfflinePromotedRagExecutor` vyžaduje explicitné paths pre:

- chunk manifest,
- retrieval index,
- runtime config,
- eval cases,
- eval report,
- prompt release.

Bundle sa nevaliduje iba podľa hashov. Bridge používa priamo authoritative LLM/RAG contracty:

1. `validate_runtime_config`,
2. `validate_retrieval_index(index, manifest)`,
3. `validate_eval_report(...)`, ktorý znovu vykoná full deterministic eval suite,
4. `build_prompt_release(...)`, ktorý znovu odvodí release,
5. byte-semantickú JSON equality medzi uloženým a novo odvodeným release artifactom.

Ak ktorýkoľvek krok zlyhá, secured API sa s týmto bundle-om nemá spustiť.

## Cross-package installation

Keycloak package zámerne nedeklaruje relatívnu filesystem dependency na sibling `labs/llm-rag`. Clean local environment nainštaluje oba workspace packages explicitne:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e 'labs/llm-rag[dev]'
python -m pip install -e 'labs/keycloak-ai-api[dev]'
```

Tým zostáva package metadata prenositeľná a cross-package dependency je viditeľná v execution contracte.

## Spustenie secured API

Najprv musí existovať promoted RAG bundle vytvorený exact LLM/RAG flowom pre rovnaký Git revision.

```bash
python labs/keycloak-ai-api/scripts/run_secured_rag_api.py \
  --issuer 'http://127.0.0.1:8080/realms/knowledge-hub' \
  --manifest .runtime/rag/chunk-manifest.json \
  --index .runtime/rag/retrieval-index.json \
  --runtime-config .runtime/rag/runtime-config.json \
  --eval-cases labs/llm-rag/data/eval-cases.json \
  --eval-report .runtime/rag/eval-report.json \
  --prompt-release .runtime/rag/prompt-release.json \
  --host 127.0.0.1 \
  --port 8090
```

Runner je source-contractom loopback-only. Non-loopback `--host` je refusal.

## `POST /v1/rag/query`

Request:

```json
{
  "query": "Ako funguje Kubernetes ConfigMap?"
}
```

Query je bounded na 1–2000 znakov.

Execution order je:

```text
Bearer authentication
→ issuer/audience/token-class validation
→ azp + rag.read authorization
→ promoted RAG executor availability
→ exact promoted bundle execution
```

Neautorizovaný request nesmie zavolať RAG executor.

Ak token prejde, ale promoted backend nie je nakonfigurovaný, endpoint vracia `503`. `200 authorized` bez backendu sa nepovažuje za hotový RAG outcome.

## Response provenance

Úspešný secured RAG response obsahuje principal boundary aj RAG evidence. RAG časť pinne najmä:

- `prompt_release_id`,
- Git `source_revision`,
- `retrieval_result_id`,
- `answer_id`,
- `trace_id`,
- observed latency,
- exact citations alebo explicitný abstention reason.

HTTP 200 teda neznamená iba „JWT bol platný“. Znamená, že request prešiel authorization a promoted offline RAG execution vrátil bounded contract result.

## Agent routes zostávajú oddelené

`POST /v1/agent/run` a `POST /v1/agent/remediate` v tomto bloku stále vykonávajú iba authorization read-back.

To je zámerné. Keycloak role `agent.run` alebo `agent.remediate` ešte nie sú dôkazom, že bounded agent executor, approval digest, idempotency, checkpoint/replay alebo remediation recovery sú implementované. Tie patria do nasledujúceho Practical v1 agent tracku.

## Refusal variants

Source tests pokrývajú alebo explicitne definujú refusal pre:

- missing/invalid bearer token pred RAG execution,
- browser token na automation-only agent route,
- valid `rag.read` token bez promoted RAG backendu,
- query nad request bound,
- missing RAG artifact,
- invalid runtime config/index/eval report,
- forged alebo stale prompt release,
- non-loopback secured API host.

## Runtime boundary

Táto vrstva je source implementation. Stále nepreukazuje:

- live Keycloak container + realm import,
- real browser/service-account token issuance,
- live JWKS fetch,
- protected request s reálnym Keycloak tokenom,
- fresh clean-checkout build oboch packages,
- promoted RAG bundle vytvorený a použitý v jednom recorded runtime gate,
- cleanup po kombinovanom identity + RAG rune,
- user acceptance alebo business outcome.

`RUNTIME-EVIDENCE.md` preto zostáva `Pending`.
