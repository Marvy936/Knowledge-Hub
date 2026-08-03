#!/usr/bin/env python3
"""Temporary closeout helper for Section 19 chapters 29-32."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once_or_present(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{path.relative_to(ROOT)}: expected one replacement target, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


section_readme = ROOT / "docs/19-mlops-and-ml-platforms/README.md"
replace_once_or_present(
    section_readme,
    "28. [MLflow evaluation, tracing a deployment](mlflow-evaluation-tracing-deployment.md)\n\n## Plánované authoritative poradie",
    "28. [MLflow evaluation, tracing a deployment](mlflow-evaluation-tracing-deployment.md)\n29. [Kubeflow Pipelines](kubeflow-pipelines.md)\n30. [Kubeflow Trainer a distributed training](kubeflow-trainer-distributed-training.md)\n31. [KServe alebo ekvivalentný Kubernetes model serving](kserve-kubernetes-model-serving.md)\n32. [Amazon SageMaker a cloud MLOps mapping](amazon-sagemaker-cloud-mlops-mapping.md)\n\n## Plánované authoritative poradie",
)
for planned in (
    "29. Kubeflow Pipelines\n",
    "30. Kubeflow Trainer a distributed training\n",
    "31. KServe alebo ekvivalentný Kubernetes model serving\n",
    "32. Amazon SageMaker a cloud MLOps mapping\n",
):
    replace_once_or_present(section_readme, planned, "")

readme_lines = section_readme.read_text(encoding="utf-8").splitlines()
status_prefix = "Aktuálny authoritative stav sekcie je **"
status_line = (
    "Aktuálny authoritative stav sekcie je **32/34 · In progress**. Ôsmy blok uzatvára platform-implementation mapping cez incident `MLOPS-PAY-97`. "
    "Kubeflow Pipelines kapitola viaže Python DSL, compiled IR alebo Kubernetes Native manifest, run/task/attempt, cache provenance, pipeline root, artifacts, ML Metadata a external mutation read-back do jedného reproducible orchestration subjectu. "
    "Kubeflow Trainer kapitola používa aktuálny V2 model `TrainJob` + Runtime, rozlišuje requested a resolved workload, rank/world-size a data partitioning, scheduler admission, complete checkpoints, elastic restart generations a downstream model acceptance. "
    "KServe kapitola oddeľuje `InferenceService` desired state, `ServingRuntime`, Standard a Knative deployment modes, resolved Kubernetes resources, loaded model fingerprint, protocol/schema, warmup, useful capacity, actual exposure a composite rollback. "
    "SageMaker kapitola mapuje platform-neutral experiments, pipelines, training, Registry, deployment, monitoring a CI/CD subjects na SageMaker AI resources, S3/ECR digests, ARNs, account/Region a AWS control/data-plane evidence bez zamieňania `Succeeded`, `Approved` alebo `InService` za business outcome. "
    "Kapitoly 29–32 prešli substantial prose, executable/model surface a subject/evidence/failure/recovery/acceptance gate-om. Reálne KFP runs, TrainJobs, KServe serving, SageMaker jobs/endpoints, recovery a business outcomes neboli vykonané; sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší a posledný authoritative blok sekcie sú kapitoly 33–34: MLOps platform architecture a MLOps troubleshooting."
)
matching = [index for index, line in enumerate(readme_lines) if line.startswith(status_prefix)]
if len(matching) != 1:
    raise SystemExit(
        f"Section README: expected one status paragraph, found {len(matching)}"
    )
readme_lines[matching[0]] = status_line
section_readme.write_text("\n".join(readme_lines) + "\n", encoding="utf-8", newline="\n")

roadmap = ROOT / "ROADMAP.md"
replacements = {
    "- [ ] Kubeflow Pipelines":
        "- [x] [Kubeflow Pipelines](docs/19-mlops-and-ml-platforms/kubeflow-pipelines.md)",
    "- [ ] Kubeflow Trainer a distributed training":
        "- [x] [Kubeflow Trainer a distributed training](docs/19-mlops-and-ml-platforms/kubeflow-trainer-distributed-training.md)",
    "- [ ] KServe alebo ekvivalentný Kubernetes model serving":
        "- [x] [KServe alebo ekvivalentný Kubernetes model serving](docs/19-mlops-and-ml-platforms/kserve-kubernetes-model-serving.md)",
    "- [ ] Amazon SageMaker a cloud MLOps mapping":
        "- [x] [Amazon SageMaker a cloud MLOps mapping](docs/19-mlops-and-ml-platforms/amazon-sagemaker-cloud-mlops-mapping.md)",
}
for old, new in replacements.items():
    replace_once_or_present(roadmap, old, new)

review = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = review.read_text(encoding="utf-8").splitlines()
prefix = "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms |"
new_line = (
    "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms | "
    "32/34 authoritative drafting | In progress | 2026-08-03 | "
    "Ôsmy authoritative blok aktivuje kapitoly 29–32 a incident `MLOPS-PAY-97`. "
    "KFP kapitola viaže source/SDK, compiled IR alebo native manifests, run/task/attempt, cache dependencies, pipeline root, artifacts, ML Metadata, multi-user identity a read-before-retry external mutations. "
    "Trainer kapitola používa Kubeflow Trainer V2 `TrainJob` a Runtime authority, DDP ranks/world size, non-overlapping shards, global batch, collectives, queue/topology scheduling, complete checkpoints, elasticity a model-quality evidence. "
    "KServe kapitola oddeľuje control/data plane, Standard a Knative modes, Runtime/model/transformer release identity, readiness/warmup, protocol, useful capacity, actual exposure, rollout a loaded-runtime rollback. "
    "SageMaker mapping kapitola zachováva rovnaké subjects cez Pipelines, Training Jobs, Experiments/Lineage, Model Registry, Endpoint Configurations, Endpoints, Model Monitor, Projects, IAM/KMS/S3/ECR a hybrid KFP integrations. "
    "Kapitoly 29–32 prešli substantial prose, executable/model surface a subject/evidence/failure/recovery/acceptance gate-om. Reálne platform runs, deployments, restores a business outcomes neboli vykonané; sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
matching = [index for index, line in enumerate(lines) if line.startswith(prefix)]
if len(matching) != 1:
    raise SystemExit(
        f"DOCUMENTATION-REVIEW-STATUS.md: expected one Section 19 row, found {len(matching)}"
    )
lines[matching[0]] = new_line
review.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

print("Section 19 block 29-32 status files updated.")
