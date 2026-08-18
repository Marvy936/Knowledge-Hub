# MLOps Online Inference Integrity

A production endpoint returned HTTP 200 for `payment-op-9001-risk-r42` and declared release `MLOPS-PAY-RISK-PROD-2026-08-r42`. The starter therefore marks the prediction verified and immediately records the returned business action.

That is unsafe. The runtime trace actually shows a stale loaded model digest and a real `online_store_timeout` feature fallback that the response hides. The starter also appends the same business action again when the identical operation is retried.

Your task is to repair `/workspace/inference_gate.py` so an online prediction becomes trustworthy only after the concrete execution is bound end to end.

## Trust boundary

```text
authenticated online request + stable operation_id
→ exact release/model/runtime actually loaded
→ exact point-in-time feature snapshot bytes
→ exact policy/fallback bytes
→ deadline + protocol + request/response schema
→ recomputed non-fallback score/action or explicit fail-closed fallback
→ deterministic prediction evidence
→ idempotent business action ledger
```

The lab proves inference execution integrity. It does **not** prove model quality, mature outcomes, promotion authority or retraining authority.

## Canonical incident

Expected release/model contract:

- release: `MLOPS-PAY-RISK-PROD-2026-08-r42`
- model: `payment-risk-linear-sim-v42`
- model SHA-256: `sha256:7a9990bb20053138e35e9e6f4d574a453b28fde714cbf68654142a538e6e763b`
- feature contract: `payment-risk-features-v6`
- policy: `risk-decision-policy-v12`
- fallback policy: `fail-closed-to-manual-review-v3`

But `runtime-trace.json` contains:

- `http_status=200`,
- stale loaded model digest `sha256:1111...`,
- actual `feature_fallback=true`, reason `online_store_timeout`,
- response falsely reports `feature_fallback=false`,
- response action is `approve` instead of the required fail-closed `manual_review`.

A correct gate rejects this incident before writing prediction or action state. The exact canonical rejection reasons are:

```text
fallback_action_not_allowed
fallback_reason_reporting_mismatch
fallback_reporting_mismatch
loaded_model_digest_mismatch
```

## Healthy non-fallback execution

For the exact pinned model and feature bytes, the simulated linear-logit model produces:

```text
raw logit = 0.69
score = 0.665967
policy action = manual_review
```

A correct gate must recompute this result rather than trust response fields.

## Required behavior

Your repair must reject foreign or mutable execution evidence, including wrong operation/release, caller, model bytes/digest, serving image, feature contract/snapshot bytes, future or stale features, protocol/schema, policy bytes/digest, deadline, reported score/action, fallback reporting and action idempotency key.

For a valid operation it must create deterministic `inference-evidence.json` and `action-ledger.json`. Replaying the identical operation must leave both files byte-for-byte unchanged. Conflicting pre-existing prediction or action state must be rejected without overwrite.

A truthful allowed fallback is valid only when its reason is explicitly reported and its action is the fail-closed `manual_review` action from the pinned policy.

Always preserve:

```text
promotion_authorized=false
retraining_authorized=false
```

Never create `promotion-request.json` or `retraining-request.json`.

## Commands

```text
help       show assignment
status     run the authoritative validator
check      same validator
hint       show a focused repair hint
infer      run the current learner gate against the canonical incident
reset      restore the unsafe starter and canonical evidence
self-test  prove starter → reference repair → reset lifecycle
```

Start with:

```bash
status
```

Then inspect:

```text
/workspace/inference-contract.json
/workspace/request.json
/workspace/feature-snapshot.json
/workspace/model.json
/workspace/policy.json
/workspace/runtime-trace.json
/workspace/inference_gate.py
```

The validator exercises the canonical incident, exact healthy execution, replay idempotency, state conflicts, tampered model/policy bytes, future/stale feature snapshots, loaded runtime mismatches, deadline/protocol failures, score/action mismatches, truthful fallback behavior and generated valid operations.
