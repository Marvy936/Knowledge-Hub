# Bounded incident/operations agent — Practical v1

Tento lab implementuje deterministický reference agent pre incident/operations automation. Nie je to autonomous production SRE agent a nepoužíva LLM ani retrieved text na autorizáciu mutácie. Cieľom je preukázať authority, durable state, approval, idempotency, bounded execution, recovery a retrieval-safety hranice, na ktoré sa môže bezpečne pripojiť reasoning alebo RAG vrstva.

```text
incident context
→ typed read-only inspection
→ canonical diagnostic snapshot
→ optional promoted retrieval context
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

Agent oddeľuje päť rozdielnych subjects:

1. incident narrative,
2. typed diagnostic evidence,
3. optional promoted retrieval evidence,
4. deterministic action proposal,
5. mutation authorization.

Free-text `operator_note` ani retrieved answer text nie sú command parser ani mutation authority. Planner rozhoduje o tool authority iba z canonical typed inspection evidence a explicitnej policy generation.

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

State obsahuje iba service records a operation-result records. Service record pinne `generation`, `status` a `restart_count`; operation record pinne canonical completed typed tool result.

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

Generation 1 pozná iba `inspect_service` ako read-only evidence a `restart_service` ako approval-gated mutation. Planner odmietne incident target mimo `allowed_targets`.

`max_tool_wait_seconds` je control-plane wait bound, nie hard cancellation mechanizmus. Ak provider/tool nevydá authoritative response v limite, executor prejde do `unknown_outcome`; operácia môže stále dobehnúť a ďalší krok musí použiť authoritative lookup.

## Typed inspection a diagnostic snapshot

`prepare_action.py` neberie service status ani generation z CLI ako authoritative input. Číta ich cez `LocalServiceStateAdapter.inspect()`.

Inspection pinne target, current service generation a `healthy|degraded|unknown` status do `inspection_id`. Diagnostic snapshot pinne tento exact inspection subject spolu s incidentom.

## Optional promoted retrieval context

PR #179 pridáva canonical retrieval subject pre Knowledge Hub RAG evidence. Context obsahuje iba:

```text
status = answered | abstained
prompt_release_id
source_revision
answer_id
trace_id
chunk_ids
text | abstention_reason
→ context_id
```

Answered context vyžaduje non-empty text a exact chunk IDs. Abstained context nesmie obsahovať answer text ani chunks a musí niesť explicitný dôvod.

`validate_retrieval_context()` celý subject canonical rebuildne. Dodatočná zmena textu, provenance alebo citations bez zmeny `context_id` je refusal.

Retrieval context je read-only evidence:

```text
retrieval_context_id
→ vstupuje do plan_id

retrieved text
↛ nevstupuje do action_digest
↛ nevytvára tool
↛ nemení target
↛ nemení typed arguments
```

Ak promoted retrieval vráti `abstained`, planner tiež abstainuje a mutačný plan nevytvorí. Ak RAG vráti answered text obsahujúci prompt-like príkazy, tool selection stále vyplýva iba z typed diagnostic a policy.

Plan bez retrieval contextu zachováva pôvodnú schema a identity; optional RAG integrácia preto nemení existujúci direct incident flow.

## Planning semantics

Bez retrieval abstention používa planner diagnostic status:

| Status | Plan |
|---|---|
| `degraded` | `approval_required` pre `restart_service` |
| `healthy` | `no_action` |
| `unknown` | `abstained` |

Pri `retrieval_context.status = abstained` je výsledok vždy non-mutating `abstained` bez ohľadu na degraded service status.

Pre restart vzniknú typed arguments:

```json
{"expected_generation": 1}
```

Canonical `action_digest` je SHA-256 nad:

```text
tool + target + typed arguments
```

Zmena targetu alebo `expected_generation` mení digest a invaliduje starý approval. Zmena read-only retrieval textu môže zmeniť `plan_id`, ale sama osebe nesmie zmeniť action digest.

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

Approval pinne exact plan ID, policy ID/generation, action digest, tool, target, approver, approval generation a interval `issued_at_unix <= now_unix < expires_at_unix`.

Requested TTL musí byť kladná a nesmie prekročiť `policy.max_approval_ttl_seconds`. `now == expires_at_unix` je už expired.

Expiry sa kontroluje pred prvou mutation a pred retry po authoritative `not_found` po bežnom failure. Nezablokuje read-only reconciliation už preukázaného completed side effectu.

Keycloak role, incident severity, planner confidence ani retrieved text nikdy nenahrádzajú approval artifact.

## Kill switch

Kill switch je dynamic safety subject viazaný na exact policy.

```bash
python labs/agent-ops/scripts/set_kill_switch.py \
  --policy .runtime/agent-ops/policy.json \
  --generation kill-v1 \
  --disengage \
  --output .runtime/agent-ops/kill-switch.json
```

Engaged switch blokuje novú mutáciu a retry po authoritative `not_found`. Neblokuje read-only reconciliation už preukázaného completed side effectu. Kill switch z inej policy generation je refusal.

## Durable operation a execution

`build_operation()` pinne incident ID, diagnostic ID, plan ID, approval ID, policy ID/generation, action digest a typed tool/target/arguments. Keď plan obsahuje retrieval context, operation ho neprenáša ako nový command channel; operation pinne celý plan cez `plan_id`.

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

Local `restart_service` prejde iba ak tool a target sú allowlisted, approval sedí s action digestom a je časovo validný pre novú mutáciu, kill switch mutation povoľuje, current service generation sa rovná approved `expected_generation` a current status je `degraded`.

Úspech zmení iba sandbox service:

```text
generation N → N+1
status degraded → healthy
restart_count +1
```

V rovnakom atomic local state write sa uloží canonical result pod operation ID.

## Strict typed tool-result boundary

PR #179 sprísňuje generation-1 tool result aj v samotnom core. `restart_service` result smie obsahovať iba:

```text
previous_generation
current_generation = previous_generation + 1
status = healthy
```

Extra field ako `instruction`, `command` alebo iný prompt-like payload je refusal pri `build_tool_result()` aj `validate_tool_result()`. Tool output sa teda nemôže stať novým free-text authority channelom ani vtedy, ak by HTTP gateway nebola prítomná.

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

Daemon thread nie je cancellation primitive. Wait breach nikdy neznamená „mutation sa nestala“.

## Idempotency a read-before-retry

Ak rovnaký operation ID príde znova po completed state, executor prečíta state a result, revaliduje operation/action subject a vráti `already_completed`. `restart_count` sa nezvýši druhýkrát.

Incomplete operation sa bez exact `recover_expected_state_id` nespustí. Pri recovery executor najprv volá `adapter.lookup(operation_id)`.

- `completed` → validate exact result a read-only reconcile bez druhej mutácie,
- `unknown` → `unknown_outcome`, automatic retry zakázaný,
- `not_found` po bežnom failure → retry je možný iba s exact recovery state, disengaged kill switchom a stále validným approvalom,
- `not_found` po `unknown_outcome` → stále `unknown_outcome`; absencia provider recordu nepreukazuje, že side effect nenastal.

```text
transport timeout
≠ operácia neprebehla

lookup not_found po unknown outcome
≠ bezpečný dôkaz na retry
```

## Retrieval persistence boundary

Keycloak bridge pri combined flow canonical retrieval context uloží pod exact plan directory. Pred remediation platí:

- plan bez `retrieval_context_id` nesmie mať orphan context artifact,
- plan s `retrieval_context_id` musí mať context file,
- context file musí byť canonical,
- `context_id` musí presne sedieť s planom.

Tampered retrieval evidence je refusal ešte pred operation buildom a side effectom.

Podrobný cross-package flow je v [`../keycloak-ai-api/BOUNDED-AGENT-INTEGRATION.md`](../keycloak-ai-api/BOUNDED-AGENT-INTEGRATION.md).

## Deterministický hard eval

PR #179 pridáva `data/eval-cases.json`, `evaluation.py` a executable `scripts/run_evaluation.py`.

Každý case vykoná:

```text
incident
→ typed inspection
→ optional retrieval context
→ plan
→ optional time-bounded approval
→ optional execute_operation
→ final service read-back
```

Evaluator hodnotí samostatne:

- trajectory,
- tool selection,
- policy compliance,
- completion criteria,
- business/operational outcome.

Reference slices pokrývajú stale-alert direct injection, safe degraded remediation, retrieved-injection abstention, unknown diagnostic abstention a malicious answered-context defense in depth. Negatívny evaluator test zámerne zadá nesprávny expected business outcome a musí vytvoriť failed report.

Source test inventory zároveň pokrýva forged retrieval context, extra prompt-like tool output a tampered completed result.

## Concurrency boundary

Executor používa local exclusive lock vedľa state file. Je to single-host/single-filesystem coordination, nie distributed lock. Practical v1 agent core preto nesmie byť spustený viacerými nezávislými workers bez nadradeného authoritative orchestrátora alebo distribuovanej coordination vrstvy.

## Cleanup

```bash
python labs/agent-ops/scripts/cleanup_runtime.py \
  --runtime-root .runtime/agent-ops
```

Cleanup povoľuje iba exact non-symlink `.runtime/agent-ops` target, odmieta symlinked `.runtime` parent a po zmazaní číta späť non-existence.

## Source closeout a runtime evidence boundary

PR #179 uzatvára source-level Practical v1 medzery pre promoted retrieval/injection a agent hard evaluation. Source lifecycle teraz obsahuje:

```text
durable authority/state
→ time-bounded approval
→ mutation/resource bounds
→ idempotency/read-before-retry
→ hardened unknown outcome
→ kill switch + allowlist
→ promoted retrieval-context boundary
→ strict typed tool result
→ deterministic hard eval
```

[`RUNTIME-EVIDENCE.md`](RUNTIME-EVIDENCE.md) však zostáva `Pending`.

Source implementation stále nepreukazuje:

- central clean-checkout Actions run exact merged subjectu,
- live Keycloak automation token,
- live promoted RAG + agent request v jednom procese,
- external cryptographic approval identity/system,
- hard cancellation remote mutácie,
- OS/container CPU-memory isolation,
- real Kubernetes/cloud/service restart,
- distributed locking,
- provider-specific remote idempotency API,
- production telemetry alebo business recovery,
- user acceptance.

Corrected PR #179 head aj merge commit nemajú connector-readable Actions run/status; issue #151 preto naďalej blokuje prechod z `Implemented` na `Runtime verified`.
