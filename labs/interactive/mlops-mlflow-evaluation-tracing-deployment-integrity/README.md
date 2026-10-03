# MLOps MLflow Evaluation, Tracing & Deployment Integrity

`MLOPS-PAY-96` has a green-looking MLflow quality story: aggregate classic classifier metrics pass, production traces have strong average scorer results, and `mlflow models serve` returns HTTP 200. That still does not prove a production-safe release.

The canonical incident is grounded in the authoritative `mlflow-evaluation-tracing-deployment.md` chapter. The aggregate classic evaluation hides a failing required `channel=mobile` segment, the trace dataset selects only successful requests and drops 32% of the eligible population, and the local serving smoke uses a different execution profile while the production target is still mixed across old and new runtime/image generations.

Repair `mlflow_eval_gate.py` so classic evaluation, tracing and deployment remain separate evidence surfaces. The repaired gate must pin the exact evaluation contract, immutable release manifest and trace-query manifest; enforce aggregate and required-segment thresholds; bind the classic dataset/evaluator/policy generation; prove trace query identity, unbiased result-class population, delivery accounting, coverage and privacy redaction; treat judge/scorer output as evidence rather than ground truth; and verify the external production target by exact loaded release/model/image/runtime identity plus a synthetic request that checks that identity.

A local MLflow server, trace scorer or validation result must never gain rollout, promotion or retraining authority by itself. Healthy evidence keeps `rollout_authorized=false`, `promotion_authorized=false` and `retraining_authorized=false`, supports byte-identical replay, preserves conflicting durable state, and proves a second evaluation/deployment operation against the same immutable inputs without manual cache warming or target edits.

Use `lab-help`, `status`, `hint`, `verify`, `check`, `assess`, `reset` and `self-test`. This is a shell-only evidence lab; it requires no live MLflow server and no privileged Docker.
