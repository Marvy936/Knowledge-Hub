# MLOps Retraining Trigger Incident

Payment-risk production monitoring reports a persistent recall drop. A cron schedule and a drift webhook both want to start retraining, and the starter coordinator immediately creates a training request from the latest bad window.

That is not sufficient retraining authority. Your task is to repair `/workspace/retraining_coordinator.py` so Continuous Training starts only from a new, mature and complete information state.

## Incident

The retraining contract pins:

- subject `MLOPS-PAY-CT-2026-08-16-021`;
- model family `payment-risk` and baseline `risk-serving-r39`;
- trigger policy `performance-persistent-v4`;
- three consecutive failed windows with minimum mature-label counts;
- logical event-time interval and source watermark;
- label contract `confirmed_loss_within_30d-v2` and required label cutoff;
- training schema and feature generation;
- semantic deduplication over model family + dataset generation + label contract;
- `promotion_mode=validation-required`.

The canonical signal really is persistently degraded, but the label watermark is still behind the contract cutoff. The correct result is therefore `blocked`, not a training request.

The starter is intentionally unsafe. It looks only at the latest recall drop, ignores readiness and the operation ledger, writes `training-request.json`, and even sets `promotion_authorized=true`.

A valid repair must distinguish:

```text
scheduler / webhook event
!= valid retraining trigger
!= ready supervised dataset
!= novel training subject
!= candidate creation
!= promotion authority
```

## Workspace

```text
/workspace/
  retraining_coordinator.py
  retraining-contract.json
  trigger-evidence.json
  readiness-evidence.json
  operations-ledger.json
```

The contract and both evidence files are protected canonical inputs. `operations-ledger.json` is mutable coordinator state. A valid new training subject may create `/workspace/training-request.json`; blocked, no-op, duplicate, or invalid evidence must not.

## Commands

```bash
help
status
check
hint
coordinate
reset
self-test
```

Run the current coordinator:

```bash
coordinate
```

Inspect any side effect:

```bash
cat /workspace/training-request.json
cat /workspace/operations-ledger.json
```

Edit the learner implementation:

```bash
nano /workspace/retraining_coordinator.py
```

Then validate:

```bash
check
```

## Acceptance contract

The validator proves that your implementation:

1. binds retraining to the exact contract, trigger subject, model family, baseline and policy generation;
2. requires the configured number of consecutive complete failed windows;
3. requires minimum mature-label counts in every persistence window;
4. treats incomplete trigger evidence as blocked rather than as confirmation;
5. validates logical interval, schema, feature generation and label-contract identity;
6. requires the source event-time watermark to close the supervised data interval;
7. requires the label watermark to reach the maturity cutoff before supervised retraining;
8. blocks undersized or duplicate-contaminated training populations;
9. derives a semantic deduplication key from model family, dataset generation and label contract;
10. reuses an existing operation instead of starting duplicate cron/webhook work over the same information state;
11. creates one deterministic training request only for persistent degradation plus ready, novel data;
12. makes an exact replay byte-for-byte idempotent for ledger and request state;
13. rejects malformed or foreign evidence without side effects;
14. always records `promotion_authorized=false` and `promotion_mode=validation-required`;
15. never creates `promotion-request.json` and never changes the production baseline;
16. preserves all protected canonical evidence bytes.

The validator also exercises valid start, exact replay, semantic duplicate reuse, incomplete telemetry, insufficient labels, transient degradation, stale source watermark, too-small training population, duplicate rows, generated ready subjects, and foreign/mismatched evidence.

The objective is the Continuous Training authority boundary: **persistent signal + mature complete data + immutable information state + semantic deduplication; candidate creation remains separate from promotion and delivery**.
