# Keycloak-secured bounded operations agent

Táto vrstva pripája local-only `labs/agent-ops` core za Keycloak automation routes bez toho, aby JWT role nahradila mutation approval.

```text
Client Credentials access token
→ JWT issuer/audience/token-class validation
→ required scope = knowledge-hub-api-access
→ allowed azp = knowledge-hub-automation
→ route-specific client role
→ bounded agent backend
```

Scope a role sú dve nezávislé authorization podmienky. Realm pridáva `knowledge-hub-api-access` ako default client scope s `include.in.token.scope=true`; API preto odmietne aj kryptograficky validný token so správnou rolou, ak exact scope chýba.

Authority sa ďalej delí podľa route:

```text
agent.run
→ typed inspection
→ diagnostic snapshot
→ deterministic plan
→ durable plan artifacts
→ no service mutation

external human approval
→ exact plan_id
→ exact action_digest
→ policy_id/generation
→ approval artifact

agent.remediate
→ JWT authorization
→ exact plan + approval read-back
→ fresh policy-bound kill-switch read-back
→ deterministic operation rebuild
→ durable state + read-before-retry
→ at most one typed restart_service mutation
```

`agent.remediate` role preto sama osebe nie je mutation authority.

## Cross-package installation

Keycloak package zámerne nedeklaruje filesystem-relative dependency na sibling lab. Fresh local environment nainštaluje oba packages explicitne:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e 'labs/agent-ops[dev]'
python -m pip install -e 'labs/keycloak-ai-api[dev]'
```

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
  --output .runtime/agent-ops/policy.json

python labs/agent-ops/scripts/set_kill_switch.py \
  --policy .runtime/agent-ops/policy.json \
  --generation kill-v1 \
  --disengage \
  --output .runtime/agent-ops/kill-switch.json
```

Policy a kill switch sú odlišné subjects. Policy je immutable planning/execution contract; kill switch je dynamic safety state viazaný na exact `policy_id` a `policy_generation`.

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

Tool-state envelope sa číta už pri startup readiness. Konkrétny service record sa napriek tomu validuje nanovo cez typed `inspect_service` pri každom pláne, aby readiness snapshot nenahradil fresh operational evidence.

## API runner

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

Runner odmieta non-loopback host. Pri štarte validuje tool-state envelope, policy, kill switch a exact runtime-root boundary. `GET /readyz/agent` vráti configured `policy_id` a generation; liveness a readiness nie sú zamieňané.

## `POST /v1/agent/run`

Vyžaduje automation access token s exact scope `knowledge-hub-api-access` a client role `agent.run`.

Request:

```json
{
  "target": "payments-api",
  "signal": "service_degraded",
  "operator_note": "Alert reports elevated failures.",
  "incident_generation": "incident-v1"
}
```

`operator_note` a incident signal sú context, nie mutation authority. Backend vždy vykoná typed `inspect_service` nad local sandbox state. Ak alert tvrdí degraded, ale aktuálny inspection je healthy, výsledok je `no_action`.

Plan response pinne:

- incident ID,
- inspection ID,
- diagnostic ID,
- plan ID,
- disposition,
- action digest ak ide o mutation proposal,
- tool a target,
- exact policy ID/generation.

Gateway revaliduje response schema a policy identity pred HTTP 200.

Canonical artifacts sa zapisujú do:

```text
.runtime/agent-ops/plans/<plan_id>/
  incident.json
  inspection.json
  diagnostic.json
  policy.json
  plan.json
```

Rovnaký deterministic plan môže artifact read-back zopakovať iba ak bytesemantický JSON subject sedí. Existujúci path s iným subjectom je refusal.

## Human approval zostáva mimo JWT route

Po `approval_required` pláne sa approval vytvorí separátne:

```bash
python labs/agent-ops/scripts/approve_action.py \
  --plan .runtime/agent-ops/plans/<plan_id>/plan.json \
  --policy .runtime/agent-ops/plans/<plan_id>/policy.json \
  --expected-plan-id '<plan_id>' \
  --approver on-call-owner \
  --approval-generation approval-v1 \
  --output .runtime/agent-ops/plans/<plan_id>/approval.json
```

Approval pinne exact plan, action digest, tool, target a policy subject. API approval nevytvára a `agent.remediate` role ho nedokáže preskočiť.

Practical v1 roadmap ešte vyžaduje approval expiry. Táto integration vrstva ju zámerne netvrdí; expiry bude samostatné rozšírenie approval contractu pred final v1 closeoutom.

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
→ exact approval_id read-back
→ stored policy equality with configured policy
→ fresh kill-switch read-back
→ canonical operation rebuild
→ durable operation write/read-back
→ execute_operation()
```

Missing alebo mismatched approval je `409` safety refusal, nie úspešná authorization response.

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

Gateway tým klientovi sprístupní exact recovery subject, ale sám retry nespustí. `unknown_outcome` zostáva explicitne neretryovateľný bez authoritative lookup evidence.

## Kill-switch semantics

Bridge číta kill switch nanovo pri každom remediation requeste.

- engaged + new operation → refusal,
- engaged + recovery `not_found` → refusal,
- engaged + recovery `completed` → read-only reconciliation je povolená,
- stale switch z inej policy → refusal,
- `unknown` tool outcome → automatic retry forbidden.

Tým emergency stop neblokuje bezpečné uzavretie už preukázaného side effectu, ale blokuje každú novú mutation decision.

## Tool-output trust boundary

Gateway akceptuje generation-1 remediation result iba ak:

```text
tool = restart_service
output keys = previous_generation,current_generation,status
current_generation = previous_generation + 1
status = healthy
```

Extra free-text field typu `instruction`, `command` alebo prompt-like payload je odmietnutý. Tool output sa teda nesmie stať novým neštruktúrovaným authority channelom.

## Čo tento blok ešte nepreukazuje

Toto je source implementation, nie runtime verification. Stále nepreukazuje:

- live Keycloak Client Credentials token + live protected agent request,
- external cryptographic approval identity,
- approval expiry,
- distributed locking,
- remote provider idempotency,
- real Kubernetes/cloud/service restart,
- wall-clock/tool runtime limit,
- production credentials,
- retrieved-content → agent prompt-injection gate,
- final trajectory/tool-selection/policy/business-outcome evaluation,
- clean-checkout combined runtime evidence,
- user acceptance.

Issue #151 preto naďalej blokuje prechod z `Implemented` na `Runtime verified` pre central Actions evidence.
