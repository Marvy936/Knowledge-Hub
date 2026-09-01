# MLOps Drift Population Integrity

A payment-risk drift alert reports a large prediction shift and immediately requests retraining. The comparison is not authoritative: the current distribution contains only successfully scored requests, while 1,200 eligible requests fell back before scoring, and the review threshold generation changed between reference and current populations. The same evidence also claims concept drift with only 42% mature-label coverage.

The incident is grounded in `MLOPS-PAY-94` and the authoritative `data-drift-concept-drift-prediction-drift.md` chapter. Repair `drift_gate.py` so a drift statistic cannot substitute for exact population, exposure, completeness, method and causal evidence.

The repaired gate must bind the exact release-manifest bytes and drift subject; preserve reference/current identity and event-time completeness; require the eligible current denominator including fallback; bind feature generation and statistical/multiplicity methods; distinguish prediction drift from concept drift; account for threshold/policy changes; and keep drift diagnostic rather than granting retraining, promotion or rollback authority.

A successful result must also prove a second complete window with the same population and method contract, no manual filtering/backfill, deterministic report bytes and conflict-preserving durable evidence.

Use `lab-help`, `status`, `hint`, `check`, `assess`, `reset` and `self-test`. This is a shell-only evidence lab; it needs no privileged mode or live ML service.
