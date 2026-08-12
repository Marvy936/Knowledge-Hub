# Bounded incident/operations agent runtime evidence

> **Evidence status: Runtime verified for the bounded combined Practical v1 local profile**

Tento dokument je authoritative runtime-evidence contract pre Practical v1 bounded incident/operations agent. Combined canonical release baseline na `789b5038b81b9342b1aef57b809bd3b67202ebde` vykonal deterministic agent contracts/hard evaluation aj protected Keycloak/RAG-agent composition. Runtime claim je bounded na local single-host profile; production credentials, distributed locking a remote exactly-once semantics sa neclaimujú.

## Required execution subject

Každý successful record musí pinovať:

- exact Git SHA,
- Python/package resolution,
- agent policy ID + generation,
- allowed target set,
- kill-switch subject,
- local sandbox/tool-state subject,
- workflow/run alebo equivalent execution ID,
- disposable runtime paths,
- cleanup/read-back result,
- explicit proof boundary.

Generation 1 nesmie počas runtime gate-u získať production credentials, unrestricted shell, SSH, Kubernetes/cloud mutation authority alebo nebounded network tool.

## 1. Typed inspection and diagnostic evidence

Fresh sandbox musí obsahovať minimálne jeden allowlisted service subject s generation, status a restart count.

Required chain:

```text
incident context
→ LocalServiceStateAdapter.inspect(target)
→ canonical service inspection
→ diagnostic snapshot
→ deterministic plan
```

Gate musí preukázať:

- authoritative status/generation čítané zo sandbox adaptera, nie z caller free-textu,
- inspection ID,
- diagnostic ID,
- incident/inspection target equality,
- stale alebo prompt-like operator note nevie prepísať fresh typed status,
- target mimo policy allowlistu je refusal.

## 2. Planning and action-digest evidence

Pre `degraded` service bez retrieval abstention musí vzniknúť jediný generation-1 mutation proposal:

```text
tool = restart_service
target = exact allowlisted service
arguments = {expected_generation: N}
action_digest = SHA-256(tool + target + typed arguments)
```

`healthy` musí viesť na `no_action`; `unknown` na `abstained`.

Mutation authority sa nesmie odvodiť z incident note, retrieved text, JWT role alebo model confidence.

## 3. Promoted retrieval-context evidence

Combined RAG→agent runtime musí preukázať optional canonical read-only context:

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

Required evidence:

- answered context s exact release/source/answer/trace/chunk provenance,
- `retrieval_context_id` zahrnutý do `plan_id`,
- `action_digest` nezávislý od free-text retrieval answeru,
- malicious answered text nevie zmeniť tool/target/typed args,
- promoted RAG `abstained` context vynúti non-mutating agent `abstained`,
- persisted `retrieval-context.json` je pred remediation znovu canonical validovaný,
- missing/orphaned/tampered context je refusal pred side effectom.

Direct incident injection a retrieved-context injection musia byť oddelené test slices.

## 4. Separate finite approval evidence

Approval musí byť vytvorený mimo planning route a pinovať:

- exact plan ID,
- exact action digest,
- tool a target,
- policy ID + generation,
- approver/generation,
- `issued_at_unix`,
- `expires_at_unix`.

Runtime musí preukázať interval:

```text
issued_at_unix <= now_unix < expires_at_unix
```

Required variants:

- valid approval povoľuje presne schválenú mutation,
- wrong plan/action/policy approval je refusal,
- TTL nad `policy.max_approval_ttl_seconds` je refusal,
- `now == expires_at_unix` je expired,
- expired approval nevytvorí novú mutation/retry authority,
- expired approval stále môže dovoliť read-only reconciliation už preukázaného completed side effectu.

## 5. Kill-switch evidence

Kill switch musí byť viazaný na exact policy subject a čítaný fresh pred remediation.

Required variants:

- disengaged switch + valid approval umožní bounded mutation,
- engaged switch blokuje novú operation,
- engaged switch blokuje retry po ordinary failure + authoritative `not_found`,
- engaged switch neblokuje read-only reconciliation `completed` resultu,
- stale switch z inej policy generation je refusal.

Kill switch nie je substitute za approval a approval nie je substitute za kill switch.

## 6. Durable operation and one-mutation evidence

Required successful chain:

```text
plan + approval + policy
→ canonical operation
→ durable planned/tool_started states
→ one typed restart_service mutation
→ completed tool result
→ completed execution state
→ service read-back
```

Evidence musí obsahovať:

- operation ID,
- state IDs/phase transition,
- attempt count,
- action digest,
- exact tool/target/arguments,
- tool result ID,
- service generation `N → N+1`,
- status `degraded → healthy`,
- restart count `+1`,
- `max_mutations_per_operation = 1` policy read-back.

Second execution rovnakého operation ID musí vrátiť already/recovered completed semantics bez druhého restartu.

## 7. Bounded tool-wait and unknown-outcome evidence

`policy.max_tool_wait_seconds` je control-plane wait bound, nie hard cancellation.

Required timeout branch:

```text
tool_started
→ wait bound exceeded
→ unknown_outcome
→ no automatic retry
```

Provider/tool môže fyzicky dobehnúť po timeout-e. Evidence preto musí preukázať, že timeout nikdy nie je reinterpretovaný ako „mutation sa nestala“.

## 8. Read-before-retry and recovery evidence

Incomplete recovery vyžaduje exact `recover_expected_state_id` a authoritative `lookup(operation_id)` pred retry.

Required variants:

### Completed lookup

```text
lookup = completed
→ exact result validation
→ read-only reconcile
→ no duplicate mutation
```

### Unknown lookup

```text
lookup = unknown
→ unknown_outcome
→ automatic retry forbidden
```

### Ordinary failure + not_found

Ak failure vznikol pred mutáciou a lookup authoritative preukáže `not_found`, retry je možné iba s exact recovery state, disengaged kill switchom a stále validným approvalom. Musí vzniknúť presne jedna neskoršia mutation.

### Unknown outcome + not_found

```text
previous state = unknown_outcome
lookup = not_found
→ stále unknown_outcome
→ retry forbidden
```

`not_found` po unknown outcome nepreukazuje, že pôvodný side effect nenastal.

## 9. Stale-state and tamper refusals

Runtime musí odmietnuť minimálne:

- service generation zmenenú po approvale,
- healthy service pri `restart_service`,
- wrong target/tool/arguments,
- forged/tampered plan/action digest,
- approval z iného plan/policy subjectu,
- stale/foreign kill switch,
- tampered retrieval context,
- tampered durable execution state/result,
- completed result s iným operation/action/tool/target subjectom.

## 10. Strict typed tool-result evidence

Generation-1 `restart_service` output smie obsahovať iba:

```text
previous_generation
current_generation = previous_generation + 1
status = healthy
```

Gate musí explicitne odmietnuť prompt-like extra field typu `instruction`, `command` alebo iný free-text authority payload. Refusal musí existovať v core tool-result validation, nie iba na HTTP gateway boundary.

## 11. Deterministic hard evaluation evidence

Executable hard eval musí pre každý case vykonať:

```text
incident
→ typed inspection
→ optional retrieval context
→ plan
→ optional approval
→ optional execute_operation
→ final service read-back
```

Evaluator musí samostatne hodnotiť:

- trajectory,
- tool selection,
- policy compliance,
- completion criteria,
- business/operational outcome.

Required reference slices:

- stale direct injection proti healthy read-backu,
- safe degraded remediation s final healthy generation `N+1`,
- retrieved-injection abstention bez mutation,
- unknown diagnostic abstention,
- malicious answered retrieval context, ktorý nemení bounded tool authority.

Negatívny evaluator test musí zámerne zmeniť expected final business outcome a vytvoriť failed report. Green report teda nesmie vzniknúť iba preto, že evaluator sám generuje expected result.

Evidence musí obsahovať hard-eval report ID, case count, passed/failed count a per-case business-outcome status.

## 12. Keycloak-secured integration evidence

Local core closeout nestačí na celý Practical v1 agent track. Exact identity integration musí preukázať:

- live automation token s required scope + `agent.run`,
- `agent.run` vytvorí iba bounded plan/read-only result,
- optional `knowledge_query` používa promoted RAG backend,
- live automation token s `agent.remediate` stále vyžaduje separate exact approval artifact,
- browser/public-client token nemôže volať automation-only route,
- missing scope/wrong role/wrong `azp` je refusal pred backend callom,
- JWT role sama osebe nikdy nie je mutation authority.

Dedicated identity evidence contract je v [`../keycloak-ai-api/RUNTIME-EVIDENCE.md`](../keycloak-ai-api/RUNTIME-EVIDENCE.md).

## Concurrency proof boundary

Source executor používa local single-host/single-filesystem coordination. Practical v1 runtime evidence preto môže preukázať iba tento bounded coordination profile.

Nepreukazuje distributed lock, multi-worker global serialization ani remote provider exactly-once guarantee.

## Cleanup evidence

Cleanup musí prebehnúť aj po failure/recovery branchi.

Required cleanup/read-back:

- `.runtime/agent-ops` removed,
- plan/retrieval-context/approval artifacts removed,
- operation/execution-state/tool-result artifacts removed,
- local sandbox state removed,
- no new runtime artifact in tracked/untracked repository checkout after declared cleanup,
- combined Keycloak/RAG runtime removed podľa ich dedicated cleanup contracts, ak boli súčasťou runu.

Cleanup driver musí odmietnuť unsafe/symlinked target path podľa source contractu.

## Evidence record

Finálny successful agent record musí uviesť minimálne:

- exact Git SHA,
- workflow/run/job ID,
- Python/package resolution,
- policy/kill-switch IDs,
- incident/inspection/diagnostic IDs,
- optional retrieval-context ID + RAG provenance,
- plan/action-digest ID,
- approval ID + validity interval,
- operation/state/result IDs,
- before/after service generation/status/restart count,
- idempotent replay result,
- unknown-outcome/recovery results,
- hard-eval report ID + business outcomes,
- Keycloak identity subject, ak bol combined run použitý,
- cleanup/worktree read-back,
- explicit proof boundary.

## Proof boundary

Úspešný Practical v1 agent evidence set preukáže bounded local incident remediation authority model s exact typed state, separate finite approval, kill switch, one-mutation semantics, read-before-retry, hardened unknown outcome, promoted retrieval safety, strict tool-result schema a deterministic business-outcome evaluation; combined gate navyše prepojí live Keycloak identity boundary.

Nepreukáže automaticky:

- production credentials alebo production remediation authority,
- distributed locking,
- hard remote cancellation,
- remote provider exactly-once semantics,
- unrestricted shell/network operation,
- real Kubernetes/cloud/service restart,
- production telemetry/SLO recovery,
- production readiness.

Required bounded local/combined records existujú; production/distributed proof boundaries uvedené vyššie zostávajú mimo Practical v1 claimu.
