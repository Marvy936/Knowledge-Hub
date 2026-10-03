# MLOps Kubeflow Trainer Distributed Integrity

A Kubeflow Trainer `TrainJob` can finish as `Succeeded` while the resulting candidate is not reproducible. In incident `MLOPS-PAY-97`, the shared Runtime changed after submission, four GPU workers consumed overlapping dataset shards, and the published checkpoint contained only model weights. A later resume changed world size and silently lost optimizer, scheduler, sampler and RNG state.

Repair `trainer_gate.py` so Kubernetes terminal status cannot substitute for an exact TrainJob → resolved Runtime → worker topology → dataset partition → complete checkpoint → resume chain.

The repaired gate must pin exact contract bytes; bind source, training image, dataset/feature generation and the controller-resolved Runtime generation/manifest; prove rank/world-size/device topology and global-batch semantics; recompute complete non-overlapping sample coverage; require an atomically committed checkpoint with model, optimizer, scheduler, sampler and RNG state; verify a clean restore can execute the next step; reject undeclared topology changes or incomplete resume state; and prove a second operation does not duplicate samples or artifacts.

Trainer success remains evidence rather than rollout, promotion or retraining authority. A healthy result preserves `rollout_authorized=false`, `promotion_authorized=false` and `retraining_authorized=false`.

Use `lab-help`, `status`, `hint`, `reconcile`, `check`, `assess`, `reset` and `self-test`. This is a shell-only evidence lab and does not require a live Kubeflow cluster.
