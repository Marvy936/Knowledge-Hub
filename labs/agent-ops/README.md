# Bounded incident/operations agent — Practical v1

Tento lab implementuje deterministický reference agent pre incident/operations automation. Nie je to autonomous production SRE agent a nepoužíva LLM na autorizáciu mutácie. Cieľom je preukázať authority, state, approval, idempotency a recovery hranice, na ktoré sa neskôr môže bezpečne pripojiť agentický reasoning layer.

```text
incident context
→ typed read-only inspection
→ canonical diagnostic snapshot
→ deterministic bounded plan
→ exact action digest
→ separate human approval
→ policy-bound kill switch
→ durable operation state
→ authoritative lookup before retry
→ one typed mutation or explicit refusal/unknown outcome
→ result read-back
→ second-operation replay
```

## Core authority model

Agent oddeľuje štyri rozdielne subjects:

1. incident narrative,
2. typed diagnostic evidence,
3. deterministic action proposal,
4. mutation authorization.

Free-text `operator_note` je kontext. Nie je command parser ani mutation authority. Planner rozhoduje iba z canonical typed inspection evidence a explicitnej policy generation.

Príklad:

```text
incident signal = service_degraded
operator note = "restart it now"
typed inspect_service = healthy
→ plan = no_action
```

Stale alert alebo prompt-like text teda nevynúti side effect proti novšiemu authoritative read-backu.

## Local-only sandbox

Practical v1 source adapter nepoužíva production credentials, shell, SSH, Kubernetes API ani cloud account. Mutuje iba explicitný local JSON state.

Inicializácia:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e 'labs/agent-ops[dev]'

python labs/agent-ops/scripts/init_sandbox.py \
  --target payments-api \
  --status degraded \
  --generation 1 \
  --output .runtime/agent-ops/tool-state.json
```

State obsahuje iba:

```text
services
→ target
  → generation
  → status
  → restart_count

operations
→ operation_id
  → canonical completed tool result
```

## Policy

`build_agent_policy()` pinne:

- exact policy generation,
- sandbox `local-state-only`,
- allowlisted targets,
- allowed typed tools,
- tools vyžadujúce approval,
- maximum jednej mutácie na operation.

Generation 1 pozná iba:

- `inspect_service` — read-only evidence,
- `restart_service` — approval-gated mutation.

Planner odmietne incident target mimo `allowed_targets`.

## Typed inspection

`prepare_action.py` neberie service status ani generation z CLI ako authoritative input. Číta ich cez `LocalServiceStateAdapter.inspect()`.

```bash
python labs/agent-ops/scripts/prepare_action.py \
  --target payments-api \
  --signal service_degraded \
  --operator-note 'Alert reports elevated failures.' \
  --incident-generation incident-v1 \
  --policy-generation policy-v1 \
  --allowed-target payments-api \
  --tool-state .runtime/agent-ops/tool-state.json \
  --inspection-output .runtime/agent-ops/inspection.json \
  --incident-output .runtime/agent-ops/incident.json \
  --diagnostic-output .runtime/agent-ops/diagnostic.json \
  --policy-output .runtime/agent-ops/policy.json \
  --plan-output .runtime/agent-ops/plan.json
```

Inspection pinne target, current service generation a `healthy|degraded|unknown` status do `inspection_id`. Diagnostic snapshot pinne tento exact inspection subject.

## Planning semantics

Deterministický planner používa diagnostic status:

| Status | Plan |
|---|---|
| `degraded` | `approval_required` pre `restart_service` |
| `healthy` | `no_action` |
| `unknown` | `abstained` |

Pre restart vytvorí typed arguments:

```json
{"expected_generation": 1}
```

A canonical `action_digest` nad:

```text
tool + target + typed arguments
```

Zmena targetu alebo `expected_generation` mení digest a invaliduje starý approval.

## Separate approval

Approval nie je súčasť planning commandu.

```bash
python labs/agent-ops/scripts/approve_action.py \
  --plan .runtime/agent-ops/plan.json \
  --policy .runtime/agent-ops/policy.json \
  --expected-plan-id '<exact-plan-id>' \
  --approver on-call-owner \
  --approval-generation approval-v1 \
  --output .runtime/agent-ops/approval.json
```

Approval pinne:

- exact plan ID,
- policy ID a generation,
- action digest,
- tool,
- target,
- approver,
- approval generation,
- `authorized_action=execute_typed_tool_once`.

Keycloak role, incident severity ani planner confidence nikdy nenahrádzajú tento approval artifact.

## Kill switch

Kill switch je samostatný dynamic safety subject, ale je viazaný na exact policy.

```bash
python labs/agent-ops/scripts/set_kill_switch.py \
  --policy .runtime/agent-ops/policy.json \
  --generation kill-v1 \
  --disengage \
  --output .runtime/agent-ops/kill-switch.json
```

Engaged switch blokuje:

- novú mutáciu,
- retry po authoritative `not_found` lookup-u.

Neblokuje read-only reconciliation. Ak provider/tool side effect už preukázateľne existuje, executor ho môže pri engaged switchi prečítať a uzavrieť local state bez druhej mutácie.

Kill switch z inej policy generation je refusal.

## Durable operation

`build_operation()` pinne:

- incident ID,
- diagnostic ID,
- plan ID,
- approval ID,
- policy ID/generation,
- action digest,
- typed tool/target/arguments.

Operation ID je deterministic SHA-256. Workspace path ani wall-clock timestamp nie sú súčasťou identity.

Executor state používa fázy:

```text
planned
→ tool_started
→ completed

failure branches:
→ failed
→ unknown_outcome
```

Každý state má:

- operation ID,
- attempt,
- previous state ID,
- lookup ID,
- result ID,
- bounded failure summary,
- canonical state ID.

## Execution

```bash
python labs/agent-ops/scripts/execute_action.py \
  --incident .runtime/agent-ops/incident.json \
  --diagnostic .runtime/agent-ops/diagnostic.json \
  --plan .runtime/agent-ops/plan.json \
  --approval .runtime/agent-ops/approval.json \
  --policy .runtime/agent-ops/policy.json \
  --kill-switch .runtime/agent-ops/kill-switch.json \
  --tool-state .runtime/agent-ops/tool-state.json \
  --operation-output .runtime/agent-ops/operation.json \
  --state .runtime/agent-ops/execution-state.json \
  --result .runtime/agent-ops/tool-result.json
```

Local `restart_service` prejde iba ak:

- tool a target sú allowlisted,
- approval sedí s action digestom,
- kill switch povoľuje mutation,
- current service generation sa rovná approved `expected_generation`,
- current status je `degraded`.

Úspech zmení iba sandbox service:

```text
generation N → N+1
status degraded → healthy
restart_count +1
```

A v rovnakom atomic local state write uloží canonical result pod operation ID.

## Idempotency a second operation

Ak rovnaký operation ID príde znova po completed state, executor:

1. prečíta state,
2. prečíta result,
3. revaliduje operation/action subject,
4. vráti `already_completed`.

`restart_count` sa nezvýši druhýkrát.

Local adapter navyše ukladá result pod operation ID, takže aj recovery po strate response vie authoritative lookupom zistiť, či side effect už nastal.

## Read-before-retry

Incomplete operation sa bez exact `recover_expected_state_id` nespustí.

Pri recovery executor najprv volá:

```text
adapter.lookup(operation_id)
```

Možné výsledky:

### `completed`

Side effect je preukázaný. Executor validuje exact result a uzavrie state bez opakovania mutácie.

### `not_found`

Side effect nebol nájdený. Retry je možný iba:

- s exact recovery state ID,
- s disengaged kill switchom,
- po opätovnej validácii všetkých operation subjects.

### `unknown`

Výsledok nie je možné spoľahlivo určiť. State sa stane `unknown_outcome` a automatic retry je zakázaný.

To je zásadná hranica:

```text
transport timeout
≠ operácia neprebehla
```

## Failure variants

Source test inventory zahŕňa:

- free-text mutation attempt pri healthy typed inspection → `no_action`,
- stale degraded incident proti healthy inspection → `no_action`,
- unknown diagnostic → `abstained`,
- target mimo allowlistu → refusal,
- stale/modified action plan → approval refusal,
- generation zmenená po approval → mutation refusal,
- engaged kill switch → nová mutation refusal,
- kill switch z inej policy → refusal,
- side effect zapísaný, ale response stratená → recovery lookup closes operation bez duplicate mutation,
- unknown provider outcome → no automatic retry,
- failure pred mutation + `not_found` → exact recovery môže vykonať jednu mutation,
- stale recovery state ID → refusal,
- concurrent lock → refusal,
- tampered completed result → replay refusal.

## Concurrency boundary

Executor používa local exclusive lock vedľa state file. Je to single-host/single-filesystem coordination, nie distributed lock.

Practical v1 agent core preto nesmie byť spustený viacerými nezávislými workers bez nadradeného authoritative orchestrátora alebo distribuovanej coordination vrstvy.

## Cleanup

```bash
python labs/agent-ops/scripts/cleanup_runtime.py \
  --runtime-root .runtime/agent-ops
```

Cleanup povoľuje iba exact non-symlink `.runtime/agent-ops` target, odmieta symlinked `.runtime` parent a po zmazaní číta späť non-existence.

## Runtime evidence boundary

[`RUNTIME-EVIDENCE.md`](RUNTIME-EVIDENCE.md) zostáva `Pending`.

Source implementation nepreukazuje:

- central clean-checkout Actions run,
- live Keycloak automation token,
- `/v1/agent/run` planning integration,
- `/v1/agent/remediate` execution integration,
- external approval identity/system,
- real Kubernetes/cloud/service restart,
- distributed locking,
- provider-specific remote idempotency API,
- production telemetry alebo business recovery,
- user acceptance.

Tento blok je reference authority/execution core. Ďalší blok ho pripojí za Keycloak agent routes bez toho, aby Keycloak role sama nahradila exact approval.
