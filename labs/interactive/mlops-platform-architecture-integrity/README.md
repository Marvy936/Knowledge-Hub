# MLOps Platform Architecture Integrity

A platform can have green KFP, Kubeflow Trainer, MLflow Registry, Feast, KServe and SageMaker status while lacking a single authoritative release subject. In incident `MLOPS-PAY-98`, a candidate was created successfully, a Registry pointer moved, KServe loaded a stale feature generation, the SageMaker fallback loaded another runtime image, and monitoring correlated requests only by model name.

Repair `architecture_gate.py` so a central dashboard or individual subsystem status cannot substitute for cross-system architectural authority.

The repaired gate must pin exact architecture-contract and release-manifest bytes; enforce the bounded authority map across Git, object storage, Registry, feature store, deployment, observability and audit; bind KFP, Trainer, Registry, feature materialization, KServe and SageMaker to one immutable release identity; require observability correlation by exact release and actual exposure; deduplicate at-least-once events and reconcile unknown mutations with read-before-retry; verify recovery restores the complete known-good composite release across both serving planes and actual traffic; and prove a second identical journey is reproducible/no-op without manual pointer edits.

Architecture evidence does not itself grant rollout, promotion or retraining authority. Healthy output preserves all three authority flags as false, is byte-idempotent and preserves conflicting durable state.

Use `lab-help`, `status`, `hint`, `reconcile`, `check`, `assess`, `reset` and `self-test`. This is a shell-only evidence lab.
