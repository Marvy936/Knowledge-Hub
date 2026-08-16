# MLOps Offline Evaluation Integrity Incident

A lineage-verified payment-risk candidate has already been produced by the training pipeline. The offline evaluator run finishes `succeeded`, reports a large F1 improvement over the production baseline, and the starter immediately declares the candidate safe for promotion.

That is not sufficient evaluation authority. Repair `/workspace/evaluate.py` so an evaluation report is created only when the **actual candidate bytes, baseline bytes, independent holdout snapshot, split exclusion set, label maturity, feature availability and evaluator execution** all belong to the exact evaluation subject.

## Incident

The upstream candidate is already in state `evaluation-required` and explicitly carries:

- candidate `candidate-9c3e2c97ef2a7d31`;
- training subject `MLOPS-PAY-CT-2026-08-16-028`;
- model family `payment-risk`;
- baseline `risk-serving-r39`;
- exact model artifact SHA-256;
- `lineage_verified=true`;
- `evaluation_required=true`;
- `promotion_mode=validation-required`;
- `promotion_authorized=false`.

The evaluation contract pins:

- evaluation subject `MLOPS-PAY-EVAL-2026-08-16-029`;
- exact upstream candidate-manifest bytes;
- exact incumbent baseline model bytes;
- independent holdout manifest `risk-holdout-manifest-v3`;
- split generation `merchant-group-time-v4` with an `unseen-merchant` exclusion policy;
- exact training-membership exclusion set;
- label contract `confirmed_loss_within_30d-v2` and cutoff `2026-07-01T00:00:00Z`;
- evaluator generation/image, metric contract and decision threshold;
- quality policy for overall F1 improvement and per-segment recall regression.

The canonical evaluator run reports `status=succeeded`, `quality_passed=true`, candidate F1 `1.0` and baseline F1 `0.4`. But the actual evaluation rows are contaminated in two ways:

1. one holdout merchant is present in the training membership; and
2. one feature value was only available after the prediction timestamp.

The correct canonical result is therefore **rejection with no `evaluation-report.json` and no `promotion-request.json`**.

The starter is intentionally unsafe. It trusts the run's `quality_passed` flag and reported metrics, claims the holdout is independent without inspecting its rows, writes an evaluation report, and even grants promotion authority.

A valid repair must distinguish:

```text
lineage-verified candidate
!= successful evaluator process
!= immutable independent holdout
!= leakage-free point-in-time evidence
!= recomputed model-quality evidence
!= evaluation pass
!= promotion authority
```

## Workspace

```text
/workspace/
  evaluate.py
  evaluation-contract.json
  candidate-manifest.json
  candidate-model.bin
  baseline-model.bin
  evaluation-dataset-manifest.json
  evaluation-dataset.json
  training-membership.json
  evaluation-run.json
```

All evidence/model inputs are protected canonical files. The canonical contaminated case must not create an evaluation report. The validator creates isolated valid variants and expects a deterministic report only when the entire evidence chain is sound. The lab must never create `promotion-request.json` after the repair.

## Commands

```bash
help
status
check
hint
evaluate
reset
self-test
```

Run the current evaluator gate:

```bash
evaluate
```

Inspect the evidence:

```bash
cat /workspace/candidate-manifest.json
cat /workspace/evaluation-contract.json
cat /workspace/evaluation-dataset-manifest.json
cat /workspace/training-membership.json
cat /workspace/evaluation-run.json
sha256sum /workspace/candidate-model.bin /workspace/baseline-model.bin /workspace/evaluation-dataset.json
```

Edit the learner implementation:

```bash
nano /workspace/evaluate.py
```

Then validate:

```bash
check
```

## Acceptance contract

The validator proves that your implementation:

1. supports only the expected offline-evaluation contract generation;
2. binds the exact upstream candidate-manifest bytes and candidate ID;
3. requires `lineage_verified=true`, `candidate_state=evaluation-required`, `evaluation_required=true`, `promotion_authorized=false` and `promotion_mode=validation-required`;
4. hashes the actual candidate model bytes and binds them to the candidate manifest;
5. hashes the actual baseline model bytes and binds them to the exact incumbent release;
6. binds the exact evaluation dataset manifest and dataset bytes;
7. binds the exact training-membership exclusion set used by the split policy;
8. requires the manifest purpose to be an independent holdout and the exact split generation/group key/observation unit/label contract;
9. rejects train/evaluation group overlap for the configured unseen-merchant scenario;
10. rejects duplicate evaluation operations beyond the configured allowance;
11. requires every evaluated feature to have been available no later than prediction time;
12. requires labels and the label watermark to be mature by the declared cutoff;
13. requires every configured segment to have the minimum evaluation population;
14. binds the evaluator run to the exact contract, candidate, baseline, dataset, exclusion set, evaluator generation/image, metric contract and threshold;
15. treats evaluator `status=succeeded` as necessary but not sufficient;
16. recomputes candidate and baseline metrics from the actual model/data bytes instead of trusting `quality_passed` or dashboard metrics;
17. rejects reported metrics that disagree with recomputation;
18. separates evidence validity from model quality: a valid evaluation may deterministically produce `failed_quality`;
19. records exact evidence digests and quality deltas in the evaluation report;
20. makes exact replay byte-for-byte idempotent;
21. refuses to overwrite conflicting pre-existing evaluation state;
22. rejects foreign/malformed/mismatched evidence without side effects;
23. records `promotion_authorized=false` and preserves `promotion_mode=validation-required` even when evaluation passes;
24. never creates `promotion-request.json` or changes production state;
25. preserves every protected canonical input byte-for-byte.

The validator also exercises the canonical dual-leakage incident, a valid independent holdout, exact replay, report-state conflict, valid-but-failed quality, candidate authority violations, candidate/baseline byte tampering, failed evaluator execution, evaluator-generation mismatch, forged metrics, group leakage, future-feature leakage, duplicates, immature labels, stale label watermark, wrong holdout purpose/split, missing segment population and generated valid holdouts.

The objective is the evaluation authority boundary: **good offline numbers are meaningful only when they are computed for the exact lineage-verified candidate and incumbent over a genuinely independent, mature, point-in-time-correct evaluation population. Even a valid evaluation pass is evidence for a later promotion gate, not promotion authority itself.**
