# MLOps SageMaker Cloud Mapping Integrity

A cloud migration can look green while violating the same MLOps subject and evidence boundaries that were enforced on Kubernetes. In incident `MLOPS-PAY-97`, the SageMaker Pipeline execution succeeded, the Model Package was `Approved`, and the Endpoint was `InService`, yet processing read a mutable S3 prefix, training and inference used mutable ECR tags, the production variant still loaded an older Model Package, and Model Monitor used a baseline from a different feature generation.

Repair `sagemaker_gate.py` so SageMaker resource status cannot substitute for exact cloud release identity.

The repaired gate must pin exact contract bytes; bind AWS account and Region; bind Pipeline definition/execution, source commit and SDK lock; require versioned S3 data plus digest and digest-pinned processing/training/inference images; verify the exact approved Model Package and model artifact; verify the Endpoint, EndpointConfig, SageMaker Model and loaded production variant by exact identity; exercise a synthetic request carrying the expected release/model identity; bind Model Monitor to the correct endpoint, feature generation, baseline and mature coverage; preserve Kubernetes-to-AWS model/image and acceptance parity; and use read-before-retry for unknown Model Package or Endpoint mutations.

`Succeeded`, `Approved` and `InService` remain evidence only. Healthy output preserves `rollout_authorized=false`, `promotion_authorized=false` and `retraining_authorized=false`, supports byte-identical replay and preserves conflicting durable state.

Use `lab-help`, `status`, `hint`, `reconcile`, `check`, `assess`, `reset` and `self-test`. This lab is shell-only and does not require live AWS credentials.
