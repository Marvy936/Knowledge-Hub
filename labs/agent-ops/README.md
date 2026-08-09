# Bounded incident/operations agent — Practical v1

Tento lab implementuje deterministický reference agent pre incident/operations automation. Nie je to autonomous production SRE agent a nepoužíva LLM na autorizáciu mutácie. Cieľom je preukázať authority, state, approval, idempotency, bounded execution a recovery hranice, na ktoré sa neskôr môže bezpečne pripojiť agentický reasoning layer.

```text
incident context
→ typed read-only inspection
→ canonical diagnostic snapshot
→ deterministic bounded plan
→ exact action digest
→ separate time-bounded human approval
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

## Policy a resource bounds

Policy sa vytvorí ako samostatný immutable subject:

```bash
python labs/agent-ops/scripts/init_policy.py \
  --generation policy-v1 \
  --allowed-target payments-api \
  --max-approval-ttl-seconds 900 \
  --max-tool-wait-seconds 5 \
  --output .runtime/agent-ops/policy.json
```

`build_agent_policy()` pinne do `policy_id`:

- exact policy generation,
- sandbox `local-state-only`,
- allowlisted targets,
- allowed typed tools,
- tools vyžadujúce approval,
- `max_mutations_per_operation = 1`,
- `max_approval_ttl_seconds`,
- `max_tool_wait_seconds`.

Generation 1 pozná iba:

- `inspect_service` — read-only evidence,
- `restart_service` — approval-gated mutation.

Planner odmietne incident target mimo `allowed_targets`.

`max_tool_wait_seconds` je control-plane wait bound, nie hard cancellation mechanizmus. Ak provider/tool nevydá authoritative response v limite, caller nemôže bezpečne tvrdiť, že side effect neprebehol. Executor preto prejde do `unknown_outcome`; background alebo remote operácia môže stále dobehnúť a ďalší krok musí použiť authoritative lookup.

## Typed inspection

`prepare_action.py` neberie service status ani generation z CLI ako authoritative input. Číta ich cez `LocalServiceStateAdapter.inspect()`.

Pre direct lab flow môže `prepare_action.py` vytvoriť policy s default bounds. Pre secured API lifecycle je authoritative bootstrap samostatný `init_policy.py`, aby policy existovala ešte pred prvým plan requestom.

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

## Separate time-bounded approval

Approval nie je súčasť planning commandu a API ho nevytvára.

```bash
python labs/agent-ops/scripts/approve_action.py \
  --plan .runtime/agent-ops/plan.json \
  --policy .runtime/agent-ops/policy.json \
  --expected-plan-id '<exact-plan-id>' \
  --approver on-call-owner \
  --approval-generation approval-v1 \
  --ttl-seconds 300 \
  --output .runtime/agent-ops/approval.json
```

CLI použije vlastný wall clock ako `issued_at_unix`; caller nedodáva ľubovoľné `now`. Approval pinne:

- exact plan ID,
- policy ID a generation,
- action digest,
- tool,
- target,
- approver,
- approval generation,
- `issued_at_unix`,
- `expires_at_unix`,
- `authorized_action=execute_typed_tool_once`.

Requested TTL musí byť kladná a nesmie prekročiť `policy.max_approval_ttl_seconds`.

Validity interval je presne:

```text
issued_at_unix <= now_unix < expires_at_unix
```

Teda `now == expires_at_unix` je už expired.

Expiry sa kontroluje iba pri udelení novej mutation authority:

- pred prvým `restart_service`,
- pred retry po authoritative `not_found` po bežnom failure.

Expiry neblokuje read-only reconciliation už preukázaného completed side effectu. To je zámerné: expirovaný approval už nesmie autorizovať novú mutáciu, ale nemá zabrániť uzavretiu durable state podľa existujúceho authoritative resultu.

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

Pretože approval ID pinne aj issue/expiry window a policy ID pinne runtime bounds, operation lineage nepriamo obsahuje exact authority window aj resource policy.

Operation ID je deterministic SHA-256. Workspace path ani execution-time `now_unix` nie sú súčasťou identity.

Executor state používa fázy:

```text
planned
→ tool_started
→ completed

failure branches:
→ failed
→ unknown_outcome
```

Každý state má operation ID, attempt, previous state ID, lookup ID, result ID, bounded failure summary a canonical state ID.

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

CLI aj Keycloak bridge získavajú `now_unix` zo svojho vlastného server-side wall clocku. HTTP ani execution CLI neposkytujú parameter, ktorým by caller mohol posunúť čas a oživiť expirovaný approval.

Local `restart_service` prejde iba ak:

- tool a target sú allowlisted,
- approval sedí s action digestom a je časovo validný pre novú mutáciu,
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

## Bounded tool wait

Mutation adapter sa spustí v daemon worker thread a control plane čaká najviac `policy.max_tool_wait_seconds` na authoritative return/exception.

```text
tool returns in bound
→ validate result
→ completed

tool does not return in bound
→ unknown_outcome
→ no automatic retry
```

Daemon thread nie je bezpečný cancellation primitive. Po timeout-e môže lokálna alebo remote operácia ešte skončiť. Preto wait breach nikdy neznamená `failed before mutation`; znamená neznámy outcome.

Tento contract limituje čas, počas ktorého request/control plane čaká na tool response, a počet mutácií na operation. Nepredstiera OS/container CPU-memory isolation ani remote provider cancellation. Tie sú mimo Practical v1 local adaptera.

## Idempotency a second operation

Ak rovnaký operation ID príde znova po completed state, executor:

1. prečíta state,
2. prečíta result,
3. revaliduje operation/action subject,
4. vráti `already_completed`.

`restart_count` sa nezvýši druhýkrát. Completed replay je read-only aj keď approval medzičasom expiroval alebo bol kill switch zapnutý.

Local adapter navyše ukladá result pod operation ID, takže aj recovery po strate response vie authoritative lookupom zistiť, či side effect už nastal.

## Read-before-retry

Incomplete operation sa bez exact `recover_expected_state_id` nespustí.

Pri recovery executor najprv volá:

```text
adapter.lookup(operation_id)
```

### `completed`

Side effect je preukázaný. Executor validuje exact result a uzavrie state bez opakovania mutácie. Nepotrebuje fresh approval, pretože nevytvára nový side effect.

### `not_found` po bežnom `failed`/`tool_started`

Retry je možný iba:

- s exact recovery state ID,
- s disengaged kill switchom,
- s approvalom, ktorý je stále v `[issued_at, expires_at)` intervale,
- po opätovnej validácii všetkých operation subjects.

### `unknown`

Výsledok nie je možné spoľahlivo určiť. State sa stane `unknown_outcome` a automatic retry je zakázaný.

### `not_found` po `unknown_outcome`

Automatic retry zostáva zakázaný. Absencia provider recordu nepreukazuje, že side effect nenastal — provider mohol stratiť idempotency/read-back záznam alebo operácia môže byť stále in-flight.

Executor uloží ďalší `unknown_outcome` checkpoint s `lookup_id` a vyžaduje manuálne/authoritative rozuzlenie alebo budúci lookup, ktorý vráti `completed`.

To je zásadná hranica:

```text
transport timeout
≠ operácia neprebehla

lookup not_found po unknown outcome
≠ bezpečný dôkaz na retry
```

## Failure variants

Source test inventory zahŕňa:

- free-text mutation attempt pri healthy typed inspection → `no_action`,
- stale degraded incident proti healthy inspection → `no_action`,
- unknown diagnostic → `abstained`,
- target mimo allowlistu → refusal,
- unbounded policy TTL/tool wait → refusal,
- stale/modified action plan → approval refusal,
- approval TTL nad policy maximum → refusal,
- exact expiry boundary → nová mutation refusal bez execution state,
- completed replay po expiry → read-only success,
- generation zmenená po approval → mutation refusal,
- engaged kill switch → nová mutation refusal,
- side effect zapísaný, response stratená, approval už expired a kill switch engaged → completed lookup sa stále read-only reconciliuje,
- unknown provider outcome + `unknown` lookup → no automatic retry,
- unknown provider outcome + `not_found` lookup → stále no automatic retry,
- failure pred mutation + fresh approval + `not_found` → exact recovery môže vykonať jednu mutation,
- failure pred mutation + expired approval + `not_found` → retry refusal,
- tool wait bound prekročený → `unknown_outcome`,
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
- external cryptographic approval identity/system,
- hard cancellation remote mutácie,
- OS/container CPU-memory isolation,
- real Kubernetes/cloud/service restart,
- distributed locking,
- provider-specific remote idempotency API,
- retrieved-content → agent prompt-injection gate,
- trajectory/tool-selection/policy/business-outcome evaluation,
- production telemetry alebo business recovery,
- user acceptance.

Keycloak-protected route integration je dokumentovaná v `labs/keycloak-ai-api/BOUNDED-AGENT-INTEGRATION.md`. Táto core vrstva zostáva local-only authority reference; production remediation authority nie je cieľom Practical v1.
