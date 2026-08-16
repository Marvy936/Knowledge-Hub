# MLOps A/B Experiment Integrity Incident

Payment-risk candidate `risk-serving-r42` appears to outperform known-good `risk-serving-r39` in an A/B experiment. The starter analyzer sees a large conversion lift and immediately declares the candidate a winner.

That conclusion is not causally trustworthy. Your task is to repair `/workspace/experiment_analyzer.py` so a winner claim is allowed only when the exact experiment subject has valid randomization, no sample-ratio mismatch, no assignment contamination, no outcome-affecting shared-capacity interference, and a mature fixed-horizon analysis window.

## Incident

The canonical experiment contract pins:

- experiment subject `MLOPS-PAY-EXP-2026-08-r42-vs-r39`;
- control `risk-serving-r39` and candidate `risk-serving-r42`;
- stable randomization unit `merchant_id`;
- assignment policy `merchant-hash-50-v3`;
- eligibility policy `eligible-card-not-present-v5`;
- expected 50/50 allocation with an explicit SRM threshold;
- shared manual-review pool `manual-review-pool-v4` and its independence bound;
- fixed-horizon winner authority;
- required outcome maturity watermark;
- minimum mature outcomes, alpha and minimum absolute lift.

The starter is intentionally unsafe. It filters to currently mature request rows, compares request-weighted candidate/control conversion rates, ignores randomization integrity and shared-resource interference, peeks during an interim window, and treats an observed winner as promotion authority.

A valid repair must distinguish:

```text
observed lift
!= valid randomization
!= mature fixed-horizon evidence
!= causal winner claim
!= promotion authority
```

## Canonical failure

The incident contains multiple independent reasons why the apparent winner must not be trusted:

- the assignment split is materially inconsistent with the expected 50/50 allocation;
- one `merchant_id` crosses candidate/control variants;
- the shared manual-review pool is above the independence utilization bound;
- the analysis is still marked `interim`;
- the required outcome maturity watermark has not been reached and some outcomes remain pending.

The correct canonical decision is therefore `invalidate`, not `winner_candidate`.

## Workspace

```text
/workspace/
  experiment_analyzer.py
  experiment-contract.json
  experiment-evidence.json
  experiment-state.json
```

`experiment-contract.json` and `experiment-evidence.json` are canonical protected evidence. Do not repair the lab by editing them.

`experiment-state.json` is mutable analysis state. Repeating the same exact evidence must be byte-for-byte idempotent.

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

Run the current implementation directly:

```bash
analyze
```

Inspect the analysis state:

```bash
cat /workspace/experiment-state.json
```

Edit the learner implementation:

```bash
nano /workspace/experiment_analyzer.py
```

Then validate:

```bash
check
```

## Acceptance contract

The validator proves that your implementation:

1. binds analysis to the exact experiment contract and evidence subject;
2. validates control/candidate, assignment policy, eligibility policy, shared-resource identity and event-time completeness;
3. treats `merchant_id` as the stable randomization unit and detects cross-variant contamination;
4. detects delivered-release mismatches separately from intended assignment;
5. performs an SRM check against the expected 50/50 unit allocation;
6. blocks causal interpretation when the outcome-affecting shared review pool exceeds its independence bound;
7. uses unit-level mature outcomes rather than request-weighted partial observations;
8. refuses a winner claim during an interim analysis or before the required outcome watermark/maturity is complete;
9. requires the configured minimum mature outcomes per variant;
10. applies the configured lift direction, minimum effect and two-sided significance threshold only after integrity/readiness gates pass;
11. distinguishes `invalidate`, `continue`, `winner_candidate` and `no_winner`;
12. never converts an A/B result into promotion authority and never creates `promotion-request.json`;
13. rejects malformed or foreign evidence without mutating experiment state;
14. makes repeated analysis of the same exact subject deterministic and byte-for-byte idempotent;
15. preserves the canonical contract and experiment evidence bytes.

The validator also exercises a valid final candidate winner, valid no-winner result, interim hold, immature outcomes, underpowered evidence, isolated SRM, assignment contamination, delivered-release mismatch, shared-capacity interference, ignored out-of-window/ineligible noise, generated reorder/outcome cases, and malformed-evidence rejection.

The objective is not to memorize a p-value formula. The objective is to understand the authority boundary of online experiments: **stable assignment + allocation integrity + no material interference + mature predeclared analysis + explicit separation from release authority**.
