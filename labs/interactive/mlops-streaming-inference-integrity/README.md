# MLOps Streaming Inference Integrity

A streaming risk consumer survived a rebalance and its broker offsets look healthy, but one payment event was delivered twice. The starter treats delivery/checkpoint success as end-to-end exactly-once execution and therefore creates the downstream business action twice.

Your task is to repair `stream_gate.py` so a stream replay can be reconciled without losing event identity or duplicating side effects.

## Incident

The exact subject is `MLOPS-PAY-INF-STREAM-2026-08-r42` on topic `payments.risk.v5`, consumer group `risk-inference-prod-r42`, partition `7`, offsets `[918201, 918204)`. There are three unique source events, but the runtime trace contains four deliveries because offset `918202` is replayed after consumer generation changes from `44` to `45`.

The final event is also intentionally late in processing order. Its event time is still inside the contract's allowed-lateness window, so processing time must not silently redefine the subject.

## What must be true

The repaired gate must:

- bind the exact streaming subject, consumer group, topic, partition and offset interval;
- verify the immutable source event bytes plus the exact loaded release, model, runtime image, feature contract, policy and schema;
- preserve event-time semantics, watermark and allowed lateness;
- reject point-in-time feature travel (`feature_available_at > event_time`);
- tolerate a legitimate rebalance replay only at or after the durable checkpoint boundary;
- derive a stable prediction key from release + topic + partition + offset + event ID;
- derive downstream action identity from `operation_id`;
- make replay byte-idempotent and reject conflicting pre-existing ledger state rather than overwrite it;
- advance the end-exclusive checkpoint only after every unique prediction and business action in the subject is durable;
- never infer global broker/end-to-end exactly-once semantics from committed offsets alone;
- preserve `promotion_authorized=false` and `retraining_authorized=false`.

The expected healthy canonical result has 4 deliveries, 3 unique predictions, 3 unique business actions, 1 replay delivery and committed offset `918204`.

## Files

- `stream-contract.json` — exact streaming authority contract.
- `events.json` — immutable source event collection for the bounded offset subject.
- `runtime-trace.json` — actual consumer generations, deliveries and loaded runtime fingerprint.
- `model.json` / `policy.json` — exact scoring and action bytes.
- `stream_gate.py` — intentionally unsafe learner implementation.
- `stream_validator.py` — acceptance suite.

Generated state:

- `prediction-ledger.json`
- `action-ledger.json`
- `stream-checkpoint.json`
- `stream-report.json`

## Commands

```bash
help
status
check
hint
consume
reset
self-test
```

`consume` executes your current gate. `check` runs the full acceptance suite. The lab is shell-only; nested Docker and `--privileged` are not required.

The purpose is not to prove model quality, authorize promotion or authorize retraining. It is to prove that one exact streaming inference subject remains correlatable and side-effect-safe across broker replay and consumer rebalance.
