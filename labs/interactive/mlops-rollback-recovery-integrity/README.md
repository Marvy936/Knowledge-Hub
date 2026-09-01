# MLOps Rollback Recovery Integrity

A production payment-risk incident appears resolved because the mutable Registry alias `champion` points back to the previous model and every serving Pod is `Ready`. The data plane is still mixed: one replica remains on the incident release, the feature service and review/fallback policies remain on canary generations, only part of traffic reaches the known-good revision, and affected business actions are only partially reconciled.

The incident is grounded in `MLOPS-PAY-95` and the authoritative `model-rollback-recovery.md` chapter. Repair `rollback_gate.py` so Registry/control-plane mutation cannot substitute for recovery of one exact composite release.

The repaired gate must bind immutable rollback-contract and known-good release bytes; prove an approved decision with the exact first divergence; reconcile timeout/unknown rollback outcomes with read-before-retry and compare-and-set semantics; verify every ready replica and global feature/policy/resource generation against the target manifest; prove actual target traffic plus an end-to-end synthetic journey; require a stable recovery window with deadline, fallback, latency and mature business-outcome evidence; reconcile all affected side effects without duplicate compensation; and reproduce a second no-op apply without mutable-alias dependence or manual steps.

Rollback recovery is evidence, not causal proof. A successful recovery must keep `root_cause_model_confirmed=false`, `rollout_authorized=false`, `promotion_authorized=false` and `retraining_authorized=false`. Accepted evidence must replay byte-identically and conflicting durable state must never be overwritten.

Use `lab-help`, `status`, `hint`, `recover`, `check`, `assess`, `reset` and `self-test`. This is a shell-only evidence lab; it needs no privileged runtime or live serving stack.
