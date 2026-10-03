# MLOps KServe Serving Integrity

A KServe `InferenceService` can be `Ready=True` while production traffic is still served by the wrong composite release. In incident `MLOPS-PAY-97`, a classifier moved from Knative to Standard mode but retained stale Knative expectations, the selected shared `ServingRuntime` changed generation, one replica reloaded a mutable model URI, autoscaling still followed CPU instead of the approved queue signal, configured canary percentage was treated as actual exposure, and rollback changed the CRD before old candidate endpoints had drained.

Repair `kserve_gate.py` so control-plane readiness and one HTTP 200 cannot substitute for data-plane proof.

The repaired gate must pin exact contract bytes; bind the mode-specific `InferenceService`, `ServingRuntime` generation/image, protocol, transformer, feature generation and resource profile; require immutable model URI plus manifest digest; verify every active replica has the exact release/model/runtime fingerprint and completed warmup; exercise an end-to-end V2 synthetic request; reconcile actual routing/result classes and the approved autoscaling policy; require endpoint convergence and connection drain during rollback; and prove a second identical apply is a no-op with fresh synthetic evidence.

KServe evidence does not itself grant rollout, promotion or retraining authority. Healthy output preserves `rollout_authorized=false`, `promotion_authorized=false` and `retraining_authorized=false`.

Use `lab-help`, `status`, `hint`, `reconcile`, `check`, `assess`, `reset` and `self-test`. This is a shell-only evidence lab and does not require a live KServe cluster.
