# MLOps Model Monitoring Integrity

A fraud-serving release looks healthy on the infrastructure dashboard: every eligible request returns HTTP 200 and average latency is 80 ms. The user journey is not healthy. Fourteen percent of requests miss the business deadline and return a successful HTTP fallback, while the model drift dashboard compares candidate predictions with a monthly training dataset without an actual exposure denominator or segment breakdown and then requests retraining.

The incident is grounded in `MLOPS-PAY-94` and the authoritative model-monitoring chapter. The learner must repair `monitoring_gate.py` so HTTP success, average latency, a drift statistic or one healthy synthetic request cannot substitute for request-correlated production evidence.

The repaired gate must bind exact release-manifest and monitoring-contract bytes; preserve the exact release/revision and monitoring windows; reconcile mutually exclusive ML result classes to the eligible denominator; enforce telemetry coverage, duplicate rate, ingestion freshness, deadline success, fallback rate and p95 latency; require actual exposure and segment evidence for drift interpretation; require an end-to-end synthetic journey; require a second monitoring window that reproduces healthy evidence without manual backfill; reject monitoring-driven retraining authority; make successful evidence byte-idempotent; reject conflicting durable state; and preserve `rollout_authorized=false`, `promotion_authorized=false` and `retraining_authorized=false`.

Commands: `help`, `status`, `check`, `hint`, `assess`, `reset`, `self-test`.

This is a shell-only evidence-contract lab. It models monitoring telemetry and outcome linkage with immutable fixtures; it does not require Prometheus, a live model server or privileged Docker.
