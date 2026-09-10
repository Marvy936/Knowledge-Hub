# MLOps MLflow Registry Integrity

A fraud model run is green in MLflow and the `champion` alias points to the new Registry version, but that does not prove a coherent production release. The run logged a mutable `latest` dataset URI without the immutable manifest digest, the alias mutation timed out and was blindly retried, and serving replicas independently resolved the mutable alias so the fleet is split across Registry versions 184 and 185.

The incident is grounded in `MLOPS-PAY-96` and the authoritative `mlflow-experiment-tracking-model-registry.md` chapter. Repair `mlflow_gate.py` so Tracking metadata, a Registry version or alias and HTTP 200 cannot substitute for an exact dataset → run → logged model → evaluation → Registry read-back → immutable deployment chain.

The repaired gate must pin exact contract, dataset and evaluation bytes; bind exact Tracking/Registry generations, run/source/pipeline identity and immutable dataset manifest; verify the logged model package, signature/environment lock and fresh load; validate exact Registry version source/run/evaluation linkage and alias read-back; reconcile unknown alias mutation outcomes with read-before-retry semantics; resolve the Registry version once into an immutable deployment identity; verify every loaded replica and a synthetic inference against that exact version/model digest; and prove a second register/load operation reuses the existing exact version rather than silently creating a duplicate after an uncertain result.

MLflow metadata remains evidence rather than rollout or promotion authority. Accepted state keeps `rollout_authorized=false`, `promotion_authorized=false` and `retraining_authorized=false`, replays byte-identically and rejects conflicting durable evidence.

Use `lab-help`, `status`, `hint`, `reconcile`, `check`, `assess`, `reset` and `self-test`. This is a shell-only evidence lab; it requires no live MLflow server or privileged Docker.
