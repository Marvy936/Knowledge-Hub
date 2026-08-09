# Keycloak-secured bounded operations agent

Táto vrstva pripája local-only `labs/agent-ops` core za Keycloak automation routes bez toho, aby JWT role alebo retrieved text nahradili mutation approval.

```text
Client Credentials access token
→ JWT issuer/audience/token-class validation
→ required scope = knowledge-hub-api-access
→ allowed azp = knowledge-hub-automation
→ route-specific client role
→ optional promoted RAG read-only context
→ bounded agent backend
```

Scope a role sú dve nezávislé authorization podmienky. Realm pridáva `knowledge-hub-api-access` ako default client scope s `include.in.token.scope=true`; API preto odmietne aj kryptograficky validný token so správnou rolou, ak exact scope chýba.

Authority sa ďalej delí podľa route:

```text
agent.run
→ optional promoted RAG query
→ canonical retrieval context alebo retrieval abstention
→ typed inspection
→ diagnostic snapshot
→ deterministic plan
→ durable plan artifacts
→ no service mutation

external human approval
→ exact plan_id
→ exact action_digest
→ policy_id/generation
→ issued_at/expires_at
→ approval artifact

agent.remediate
→ JWT authorization
→ exact plan + optional retrieval-context + approval read-back
→ fresh policy-bound kill-switch read-back
→ approval validity check pred novou mutation authority
→ deterministic operation rebuild
→ durable state + read-before-retry
→ bounded tool wait
→ at most one typed restart_service mutation
```

`agent.remediate` role preto sama osebe nie je mutation authority. Rovnako ani text z RAG odpovede nie je mutation authority.

## Cross-package installation

Keycloak package zámerne nedeklaruje filesystem-relative dependency na sibling lab. Fresh local environment nainštaluje packages explicitne:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e 'labs/agent-ops[dev]'
python -m pip install -e 'labs/keycloak-ai-api[dev]'
```

Pre combined RAG→agent path musí byť navyše nainštalovaný `labs/llm-rag` package.

## Bootstrap sandboxu a policy

Runtime root je exact local path `.runtime/agent-ops`.

```bash
python labs/agent-ops/scripts/init_sandbox.py \
  --target payments-api \
  --status degraded \
  --generation 1 \
  --output .runtime/agent-ops/tool-state.json

python labs/agent-ops/scripts/init_policy.py \
  --generation policy-v1 \
  --allowed-target payments-api \
  --max-approval-ttl-seconds 900 \
  --max-tool-wait-seconds 5 \
  --output .runtime/agent-ops/policy.json

python labs/agent-ops/scripts/set_kill_switch.py \
  --policy .runtime/agent-ops/policy.json \
  --generation kill-v1 \
  --disengage \
  --output .runtime/agent-ops/kill-switch.json
```

Policy a kill switch sú odlišné subjects. Policy je immutable planning/execution contract; kill switch je dynamic safety state viazaný na exact `policy_id` a `policy_generation`.

Policy ID pinne aj:

- `max_mutations_per_operation = 1`,
- maximum approval TTL,
- maximum control-plane wait na authoritative tool outcome.

Bridge nevníma `.runtime/agent-ops` iba ako odporúčaný adresár. Startup vyžaduje presne tieto bootstrap subjects:

```text
.runtime/agent-ops/tool-state.json
.runtime/agent-ops/policy.json
.runtime/agent-ops/kill-switch.json
```

Alternatívny path, file symlink alebo `plans/`/`operations/` directory symlink mimo runtime rootu je refusal. Canonical identity directories sú iba:

```text
.runtime/agent-ops/plans/<64-hex-plan-id>
.runtime/agent-ops/operations/<64-hex-operation-id>
```

Tool-state envelope sa číta už pri startup readiness. Konkrétny service record sa validuje nanovo cez typed `inspect_service` pri každom pláne, aby readiness snapshot nenahradil fresh operational evidence.

## API runners

Agent-only runner:

```bash
python labs/keycloak-ai-api/scripts/run_secured_agent_api.py \
  --issuer 'http://127.0.0.1:8080/realms/knowledge-hub' \
  --tool-state .runtime/agent-ops/tool-state.json \
  --policy .runtime/agent-ops/policy.json \
  --kill-switch .runtime/agent-ops/kill-switch.json \
  --runtime-root .runtime/agent-ops \
  --host 127.0.0.1 \
  --port 8091
```

PR #179 pridáva combined loopback runner `run_secured_agent_rag_api.py`. Ten vytvorí `OfflinePromotedRagExecutor` z exact `RagBundlePaths` a rovnaký bounded agent executor v jednom FastAPI procese. Combined runner je source path pre optional `knowledge_query`; nejde o dôkaz live Keycloak runtime execution.

Runnery odmietajú non-loopback host. Agent backend pri štarte validuje tool-state envelope, policy, kill switch a exact runtime-root boundary. `GET /readyz/agent` vráti configured `policy_id` a generation; liveness a readiness nie sú zamieňané.

## `POST /v1/agent/run`

Vyžaduje automation access token s exact scope `knowledge-hub-api-access` a client role `agent.run`.

Request bez retrieval:

```json
{
  "target": "payments-api",
  "signal": "service_degraded",
  "operator_note": "Alert reports elevated failures.",
  "incident_generation": "incident-v1"
}
```

Optional promoted knowledge path pridá:

```json
{
  "knowledge_query": "What does the approved runbook say about this service?"
}
```

Ak `knowledge_query` nie je prítomný, endpoint zachováva pôvodný agent planning contract. Ak je prítomný, promoted RAG backend musí byť nakonfigurovaný; request sa nesmie potichu degradovať na raw text alebo ignorovať retrieval.

RAG result je najprv revalidovaný proti exact `prompt_release_id`, `source_revision`, answer/trace identity a citations. Pre agent context musí mať každá answered citation exact `chunk_id`. Context sa redukuje na canonical read-only subject:

```text
status
prompt_release_id
source_revision
answer_id
trace_id
chunk_ids
text | abstention_reason
→ context_id
```

`operator_note`, incident signal aj retrieved answer text sú context, nie mutation authority. Backend vždy vykoná typed `inspect_service` nad local sandbox state.

Planner pinne `retrieval_context_id` do `plan_id`, ale canonical `action_digest` zostáva odvodený výlučne z:

```text
tool + target + typed arguments
```

To je zásadná authority hranica. Dve rozdielne answered retrieval odpovede môžu vytvoriť rozdielny `plan_id`, ale ak current typed diagnostic a policy povoľujú rovnakú akciu, nemôžu svojím textom prepísať tool, target alebo arguments.

Ak promoted RAG vráti `abstained` — vrátane retrieved-context prompt-injection refusal — agent plán je tiež `abstained` a neobsahuje tool ani action digest. Malicious answered text zase nevie vynútiť iný tool než generation-1 policy a typed diagnostic povoľujú.

Plan response pinne incident, inspection, diagnostic, optional retrieval context, plan, action digest, tool/target a exact policy subject. Gateway revaliduje response schema a policy identity pred HTTP 200.

Canonical artifacts sa zapisujú do:

```text
.runtime/agent-ops/plans/<plan_id>/
  incident.json
  inspection.json
  diagnostic.json
  retrieval-context.json   # iba ak sa retrieval použil
  policy.json
  plan.json
```

Rovnaký deterministic plan môže artifact read-back zopakovať iba ak JSON subject sedí. Existujúci path s iným subjectom je refusal.

## Human approval zostáva mimo JWT route

Po `approval_required` pláne sa approval vytvorí separátne:

```bash
python labs/agent-ops/scripts/approve_action.py \
  --plan .runtime/agent-ops/plans/<plan_id>/plan.json \
  --policy .runtime/agent-ops/plans/<plan_id>/policy.json \
  --expected-plan-id '<plan_id>' \
  --approver on-call-owner \
  --approval-generation approval-v1 \
  --ttl-seconds 300 \
  --output .runtime/agent-ops/plans/<plan_id>/approval.json
```

Approval pinne exact plan, action digest, tool, target, policy subject a finite validity interval. CLI zoberie issue time zo svojho wall clocku; caller neposiela ľubovoľné `now`.

Validity je:

```text
issued_at_unix <= now_unix < expires_at_unix
```

Requested TTL nesmie prekročiť `policy.max_approval_ttl_seconds`.

API approval nevytvára a `agent.remediate` role ho nedokáže preskočiť. Pri remediation bridge používa server-side `time.time()`; HTTP request nemá parameter na posun času.

Expiry blokuje novú mutáciu alebo retry po `not_found`. Nezablokuje read-only reconciliation už preukázaného completed side effectu, pretože tá nevytvára novú mutation authority.

## `POST /v1/agent/remediate`

Vyžaduje automation access token s exact scope `knowledge-hub-api-access` a client role `agent.remediate`.

Request:

```json
{
  "plan_id": "<64-hex-plan-id>",
  "approval_id": "<64-hex-approval-id>",
  "recover_expected_state_id": null
}
```

Execution order:

```text
JWT authentication + scope + route-role authorization
→ exact plan directory
→ optional retrieval-context canonical read-back
→ exact approval_id read-back
→ stored policy equality with configured policy
→ fresh kill-switch read-back
→ canonical operation rebuild
→ durable operation write/read-back
→ read-before-retry ak ide o recovery
→ approval-time check iba pred novou mutation authority
→ bounded tool execution wait
```

Ak plan pinne `retrieval_context_id`, `retrieval-context.json` musí existovať, byť canonical a sedieť s exact ID. Ak plan context nemá, orphan context artifact je refusal. Tampered retrieval evidence sa teda odmietne ešte pred side effectom.

Missing, mismatched, not-yet-valid alebo expired approval je safety refusal tam, kde by request vytváral nový side effect.

Operation state patrí do:

```text
.runtime/agent-ops/operations/<operation_id>/
  operation.json
  execution-state.json
  tool-result.json
```

Incomplete recovery vyžaduje exact `recover_expected_state_id`. Core potom urobí authoritative `lookup(operation_id)` pred akýmkoľvek retry.

Ak request skončí po zapísaní durable checkpointu, HTTP 409 môže vrátiť iba bounded recovery evidence:

```text
operation_id
state_id
phase
```

Gateway tým klientovi sprístupní exact recovery subject, ale sám retry nespustí.

## Unknown outcome a bounded tool wait

`policy.max_tool_wait_seconds` obmedzuje čas, počas ktorého control plane čaká na authoritative tool response. Nie je to hard cancellation remote operácie.

Ak tool v limite nevráti výsledok:

```text
tool_started
→ wait bound exceeded
→ unknown_outcome
→ automatic retry forbidden
```

Provider/tool môže stále dobehnúť. Následná recovery vždy začína lookupom.

- `completed` → read-only reconciliation,
- `unknown` → zostáva `unknown_outcome`,
- `not_found` po `unknown_outcome` → stále zostáva `unknown_outcome`; `not_found` nepreukazuje, že pôvodná mutácia určite nenastala.

Tým timeout nikdy nie je reinterpretovaný ako bezpečná licencia na druhý side effect.

## Kill-switch semantics

Bridge číta kill switch nanovo pri každom remediation requeste.

- engaged + new operation → refusal,
- engaged + recovery `not_found` po bežnom failure → refusal,
- engaged + recovery `completed` → read-only reconciliation je povolená,
- stale switch z inej policy → refusal,
- `unknown_outcome` → automatic retry forbidden bez ohľadu na switch.

Emergency stop teda neblokuje bezpečné uzavretie už preukázaného side effectu, ale blokuje každú novú mutation decision.

## Tool-output trust boundary

Agent core aj gateway akceptujú generation-1 remediation result iba ak:

```text
tool = restart_service
output keys = previous_generation,current_generation,status
current_generation = previous_generation + 1
status = healthy
```

Extra free-text field typu `instruction`, `command` alebo prompt-like payload je odmietnutý ešte v core `build_tool_result`/`validate_tool_result` a znovu na HTTP boundary. Tool output sa nesmie stať novým neštruktúrovaným authority channelom.

## Deterministický hard eval

PR #179 pridáva offline eval cases a executable `run_evaluation.py`. Každý case ide cez:

```text
incident
→ typed inspection
→ optional canonical retrieval context
→ plan
→ optional human-approval artifact
→ optional execute_operation
→ final service read-back
```

Evaluator hodnotí samostatne:

- trajectory,
- tool selection,
- policy compliance,
- completion criteria,
- business/operational outcome.

Reference cases zahŕňajú stale direct injection, safe degraded remediation, retrieved-injection abstention, unknown diagnostic abstention a malicious answered-context defense in depth. Negatívny test zámerne zmení expected final business outcome a musí vytvoriť failed report; evaluator teda nie je iba generátor zeleného výsledku.

Toto je source-level evaluation implementation. Bez central executed runu nejde o runtime evidence.

## Čo tento blok ešte nepreukazuje

Source-level Practical v1 agent/identity integration po PR #179 obsahuje retrieval/injection path aj hard evaluation, ale stále nepreukazuje:

- central clean-checkout Actions run exact merged subjectu,
- live Keycloak Client Credentials token + live protected agent request,
- live promoted RAG + agent request v jednom procese,
- external cryptographic approval identity,
- distributed locking,
- remote provider idempotency,
- hard remote cancellation,
- OS/container CPU-memory isolation,
- real Kubernetes/cloud/service restart,
- production credentials,
- production telemetry alebo business recovery,
- user acceptance.

Approval expiry, one-mutation budget, bounded control-plane tool wait, promoted retrieval-context authority boundary a hard eval sú source-level implementované; nepredstavujú production resource isolation ani runtime verification.

Issue #151 naďalej blokuje prechod z `Implemented` na `Runtime verified` pre central Actions evidence. Corrected PR #179 head aj merge commit nemajú connector-readable workflow run/status.
