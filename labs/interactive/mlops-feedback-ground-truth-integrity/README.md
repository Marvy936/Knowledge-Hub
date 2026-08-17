# MLOps Feedback / Ground-Truth Integrity Incident

A production payment-risk model has accumulated delayed outcome feedback. A naive feedback job reports full coverage and acceptable accuracy, then immediately requests retraining.

The result looks plausible, but the evidence is not authoritative.

Repair `/workspace/feedback_gate.py` so realized model performance is built from the **exact prediction operation**, the versioned label contract, mature outcomes, deterministic corrections and explicit coverage denominators. A verified feedback report must remain evidence only; it must not silently become promotion or retraining authority.

## Incident

The exact feedback subject is:

```text
MLOPS-PAY-FEEDBACK-2026-08-W31
```

The contract pins:

- model family `payment-risk`;
- deployed release `MLOPS-PAY-RISK-PROD-2026-07-r31`;
- feature contract `payment-risk-features-v6`;
- exact prediction snapshot bytes;
- label contract `confirmed_loss_within_30d-v2` and exact contract bytes;
- a 30-day maturity policy;
- authoritative as-of time `2026-08-16T23:59:59Z`;
- action policy `review-capacity-v4`;
- minimum overall final-label coverage of `0.80`;
- minimum `manual_review` coverage of `0.80`;
- minimum `approve` coverage of `0.75`;
- `promotion_authorized=false`;
- `retraining_authorized=false`.

The prediction snapshot contains six mature operations. Two different operations intentionally share `entity_id=merchant-300`.

The label stream contains:

- final outcomes for `pay-op-001`, `pay-op-002` and `pay-op-004`;
- only a **provisional** review verdict for `pay-op-005`;
- two final events for `pay-op-006`, where source sequence 2 corrects sequence 1;
- no final outcome for `pay-op-003`.

The unsafe starter collapses labels by `entity_id`, treats the provisional review verdict as truth, and applies the latest `merchant-300` label to both operations. It therefore manufactures apparent full coverage and creates `retraining-request.json`.

The authoritative operation-level mature coverage is actually:

```text
overall:       4 / 6 = 0.666667
manual_review: 2 / 2 = 1.0
approve:       2 / 4 = 0.5
```

The canonical correct result is:

```text
blocked
- overall_coverage_below_minimum
- action_coverage_below_minimum:approve
```

No feedback report or authority request may be created for that incomplete cohort.

## Why this is different from the other MLOps labs

`mlops-drift-monitoring` asks whether input/prediction distributions changed and deliberately avoids claiming realized model quality when labels are unavailable.

This lab begins when delayed labels start arriving. It asks a different question:

```text
production prediction
→ policy/action
→ delayed outcome
→ exact operation join
→ maturity + correction semantics
→ coverage/censoring proof
→ realized performance evidence
```

`mlops-retraining-trigger` owns a later training-authority decision. A successful feedback report here may become evidence for that decision, but this lab itself must always keep:

```text
promotion_authorized=false
retraining_authorized=false
```

## Workspace

```text
/workspace/
  feedback_gate.py
  feedback-contract.json
  prediction-snapshot.json
  label-contract.json
  label-events.json
```

The four JSON evidence files are protected canonical inputs. The validator creates isolated modified cases to test fail-closed behavior without changing them.

## Commands

```bash
help
status
check
hint
analyze
reset
self-test
```

Inspect the evidence:

```bash
cat /workspace/feedback-contract.json
cat /workspace/prediction-snapshot.json
cat /workspace/label-contract.json
cat /workspace/label-events.json
sha256sum /workspace/prediction-snapshot.json /workspace/label-contract.json
```

Run the current implementation:

```bash
analyze
```

Edit it:

```bash
nano /workspace/feedback_gate.py
```

Then validate:

```bash
check
```

## Acceptance contract

The validator proves that the repaired feedback gate:

1. supports only `payment-risk-feedback-v3`;
2. preserves the evidence-only authority boundary;
3. binds the actual prediction-snapshot bytes to the contract SHA-256;
4. binds the actual label-contract bytes to the contract SHA-256;
5. binds model family, exact deployed release, feature contract and snapshot identity;
6. uses the versioned label definition `confirmed_loss_within_30d-v2`;
7. requires the label maturity policy to match the contract;
8. uses one authoritative `maturity_as_of` boundary;
9. requires every fixed-cohort prediction to have completed its 30-day horizon;
10. permits repeated entity IDs but requires unique `operation_id`;
11. preserves the exact action policy generation;
12. joins labels only by `operation_id`;
13. checks that a label's entity metadata still matches that operation;
14. rejects labels for unknown operations;
15. distinguishes provisional and final label sources;
16. never counts provisional review verdicts as realized ground truth;
17. validates unique label-event IDs;
18. validates positive monotonic `source_sequence`;
19. rejects duplicate source sequence for the same operation;
20. validates correction/supersedes chains;
21. deterministically selects the highest valid final source sequence;
22. rejects labels that arrived after the evidence as-of boundary;
23. computes coverage against the full mature prediction denominator;
24. computes coverage independently for each required action;
25. blocks the canonical selectively observed cohort;
26. verifies a completed cohort after the two missing final outcomes arrive;
27. recomputes the confusion matrix and realized metrics from exact records;
28. records provisional events ignored and corrections applied;
29. writes exact SHA-256 evidence bindings into the report;
30. writes a deterministic content-derived feedback report ID;
31. is byte-idempotent on exact replay;
32. refuses to overwrite conflicting pre-existing report state;
33. rejects tampered prediction or label-contract bytes;
34. rejects foreign release, wrong action policy, immature predictions and malformed label provenance;
35. never creates `promotion-request.json`;
36. never creates `retraining-request.json`;
37. always keeps `promotion_authorized=false`;
38. always keeps `retraining_authorized=false`;
39. preserves all protected canonical input bytes.

The objective is the feedback trust boundary: **`label IS NOT NULL` is not a realized-performance cohort. Production feedback is authoritative only after exact decision identity, maturity, correction semantics and action-conditioned coverage survive the join.**
