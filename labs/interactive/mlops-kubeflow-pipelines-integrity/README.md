# MLOps Kubeflow Pipelines Integrity

A Kubeflow Pipeline run is green, but that does not prove a reproducible or side-effect-safe training subject. In incident `MLOPS-PAY-97`, preprocessing was reused from cache even though a mutable lookup table had changed, the compiled pipeline graph was not bound to the reviewed source, and a timed-out Registry mutation was retried and created a duplicate model version.

Repair `kfp_gate.py` so a successful KFP run cannot substitute for exact source → compiled IR → parameters → component images → task attempts → artifacts → external mutation evidence.

The repaired gate must pin the exact integrity contract; bind source commit, SDK lock, compiled IR digest, pipeline root, namespace, service account and parameters; prove cache eligibility from complete immutable dependencies; verify one accepted attempt per logical task; read every required artifact by immutable digest; reconcile unknown external mutation outcomes before retry; and prove a second identical operation reuses only pure cache outputs while the mutation step becomes a deterministic no-op.

A healthy run remains evidence only. It must preserve `rollout_authorized=false`, `promotion_authorized=false` and `retraining_authorized=false`.

Use `lab-help`, `status`, `hint`, `reconcile`, `check`, `assess`, `reset` and `self-test`. This lab is shell-only.
