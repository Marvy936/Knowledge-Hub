# MLOps Batch Inference Integrity

A nightly payment-risk batch job finished successfully and published an output prefix. The starter therefore marks the run complete and creates downstream actions for every selected row. One selected payment, however, occurred after the business cutoff because the source snapshot was filtered by processing time rather than event time.

Your task is to repair `batch_gate.py` so job completion becomes only execution evidence, not batch-output authority.

## Incident

The exact operation is `risk-score-2026-08-21-v4` for logical interval `[2026-08-21T00:00:00Z, 2026-08-22T00:00:00Z)`. The immutable input manifest contains four rows, although the contract authorizes three observations in that interval. `payment-8204` has event time `2026-08-22T00:02:00Z`; it entered because the unsafe path used a `00:05` processing-time cutoff.

Both shard attempts report `succeeded`. That proves execution only. It does not prove that the bounded input subject, output rows, publication boundary or downstream actions are correct.

## What must be true

The repaired gate must:

- bind the exact batch operation, immutable input-manifest bytes and logical event-time interval;
- verify exact loaded release, model, runtime image, feature contract, policy and input schema;
- reject processing-time selection when the contract requires event time;
- require unique observation and business-operation identities plus point-in-time features (`feature_available_at <= event_time`);
- reconcile the successful shard attempts to complete, duplicate-free coverage of the exact bounded input subject;
- recompute each prediction and action from the pinned model and policy rather than trust job metadata;
- build deterministic per-shard output bytes before exposing a canonical output manifest;
- publish the canonical manifest only after every expected shard, prediction and business action is durable;
- make a whole-job retry byte-idempotent and reject conflicting existing state rather than overwrite it;
- preserve `promotion_authorized=false` and `retraining_authorized=false` even for a healthy batch.

A healthy canonical repair has 3 predictions, 3 business actions, 2 output parts and one complete canonical output manifest. Re-running the same operation must change no durable bytes.

## Files

- `batch-contract.json` — exact batch authority contract.
- `input-manifest.json` — immutable bounded input snapshot and rows.
- `runtime-trace.json` — actual job/shard execution and loaded runtime fingerprint.
- `model.json` / `policy.json` — exact scoring and action bytes.
- `batch_gate.py` — intentionally unsafe learner implementation.
- `batch_validator.py` — acceptance suite.

Generated state after a valid repair:

- `output/part-*.jsonl`
- `output-manifest.json`
- `action-ledger.json`
- `batch-ledger.json`
- `batch-report.json`

## Commands

```bash
help
status
check
hint
run
reset
self-test
```

`run` executes your current gate. `check` runs the full acceptance suite. The lab is shell-only; nested Docker and `--privileged` are not required.

This lab proves one exact batch inference operation and its side effects. It does not prove model quality, authorize model promotion or authorize retraining.
