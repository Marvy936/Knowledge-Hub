# MLOps Canary Rollback Incident

Production payment-risk candidate `risk-serving-r42` is already in a bounded canary beside known-good `risk-serving-r39`.

The rollout controller says the endpoint is healthy and the starter decider wants to ramp the candidate. That conclusion is unsafe: configured traffic percentage and aggregate endpoint metrics are not the rollout authority.

Your task is to repair `/workspace/canary_decider.py` so the decision is bound to the exact rollout subject and actual exposure evidence.

## Incident

The canary contract pins:

- rollout subject `MLOPS-PAY-ROLLOUT-2026-08-r42-step20`;
- candidate `risk-serving-r42`;
- known-good control and rollback target `risk-serving-r39`;
- stable assignment unit `merchant_id`;
- eligibility policy `eligible-card-not-present-v5`;
- routing generation `risk-rollout-router-v8`;
- the current 20% step, its evidence minimums and maximum actual unit exposure;
- candidate-only technical/model leading guardrails;
- the exact known-good release bytes.

The starter is intentionally wrong. It trusts configured exposure, aggregates candidate and control requests, ignores fallback/review guardrails, and lets an aggregate-green endpoint authorize a ramp.

A valid repair must distinguish:

```text
configured traffic
!= actual unique assignment-unit exposure
!= candidate-only behavior
!= aggregate endpoint health
```

It must also treat incomplete or mixed-generation telemetry as **unknown evidence**, not green evidence.

## Workspace

```text
/workspace/
  canary_decider.py
  rollout-contract.json
  known-good-release.json
  exposure-window.json
  routing-state.json
```

`rollout-contract.json`, `known-good-release.json`, and `exposure-window.json` are canonical evidence. Do not repair the lab by editing them.

`routing-state.json` is mutable control-plane state. A correct rollback must reconcile it to the exact known-good release. Repeating the same exact decision must not keep changing the state.

## Commands

```bash
help
status
check
hint
decide
reset
self-test
```

Run the current implementation directly with:

```bash
decide
```

Inspect the resulting state:

```bash
cat /workspace/routing-state.json
```

Edit the learner implementation with the bundled editor:

```bash
nano /workspace/canary_decider.py
```

Then run:

```bash
check
```

## Acceptance contract

The validator proves that your implementation:

1. binds the decision to the exact rollout contract and pinned known-good release bytes;
2. validates release, eligibility, assignment-unit, routing-generation and event-time window identity;
3. refuses incomplete, mixed-assignment, mixed-revision or malformed exposure telemetry without mutating routing state;
4. computes actual canary exposure from unique eligible `merchant_id` values rather than trusting configured request traffic;
5. evaluates candidate error, feature fallback and p95 latency on candidate requests only;
6. compares the candidate action/review rate with the control population;
7. rolls back when actual exposure exceeds its bound or any required candidate guardrail fails;
8. holds when the evidence minimum is not met;
9. ramps only when exact evidence is complete, sufficiently powered and all guardrails pass;
10. reconciles rollback to the exact known-good composite release;
11. makes repeated evaluation of the same exact rollout subject deterministic and byte-for-byte idempotent;
12. preserves the canonical contract, known-good release and exposure evidence.

The lab also exercises healthy ramp, underpowered hold, overexposure rollback, out-of-window noise, generated guardrail failures, and invalid-evidence cases.

The objective is not to memorize one threshold. The objective is to identify the authority boundary of a live canary: **stable assignment + actual exposure + complete per-release evidence + explicit rollback policy**.
