# MLOps Drift Population Integrity

A payment-risk drift alert reports a large prediction shift and immediately requests retraining. The comparison is not authoritative: the prediction distribution is correctly computed only from successfully scored requests, but the dashboard silently treats those 4,800 rows as the full current population and hides 1,200 eligible requests that fell back before scoring. The review threshold generation also changed between reference and current populations, and the same evidence claims concept drift with only 42% mature-label coverage and no recomputed conditional-performance proof.

The incident is grounded in `MLOPS-PAY-94` and the authoritative `data-drift-concept-drift-prediction-drift.md` chapter. Repair `drift_gate.py` so a drift statistic cannot substitute for exact population, exposure, completeness, method and causal evidence.

The repaired gate must bind immutable drift-contract and release-manifest bytes; preserve exact reference/current identity and event-time completeness; reconcile the full eligible denominator including fallback while keeping the prediction distribution scoped to successfully scored requests; report fallback separately; bind feature generation, threshold generation and statistical/multiplicity methods; distinguish prediction drift from concept drift; require mature ground-truth and recomputed conditional-performance evidence for any concept claim; account for threshold/policy changes; and keep drift diagnostic rather than granting retraining, promotion or rollback authority.

A successful result must also prove a second exact complete window with the same reference/population/method contract, scored-versus-fallback reconciliation, no manual filtering/backfill, deterministic report bytes and conflict-preserving durable evidence. Tampering with the authority contract must be rejected.

Use `lab-help`, `status`, `hint`, `check`, `assess`, `reset` and `self-test`. This is a shell-only evidence lab; it needs no privileged mode or live ML service.
