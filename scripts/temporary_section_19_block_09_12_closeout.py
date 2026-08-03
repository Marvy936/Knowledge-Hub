#!/usr/bin/env python3
"""Temporary closeout helper for Section 19 chapters 09-12."""

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


roadmap = ROOT / "ROADMAP.md"
replacements = {
    "- [ ] ML pipeline orchestration":
        "- [x] [ML pipeline orchestration](docs/19-mlops-and-ml-platforms/ml-pipeline-orchestration.md)",
    "- [ ] Training pipelines a distributed training":
        "- [x] [Training pipelines a distributed training](docs/19-mlops-and-ml-platforms/training-pipelines-distributed-training.md)",
    "- [ ] CI pre ML code, data a pipelines":
        "- [x] [CI pre ML code, data a pipelines](docs/19-mlops-and-ml-platforms/ci-for-ml-code-data-pipelines.md)",
    "- [ ] Continuous Delivery pre modely":
        "- [x] [Continuous Delivery pre modely](docs/19-mlops-and-ml-platforms/continuous-delivery-for-models.md)",
}
for old, new in replacements.items():
    replace_once_or_present(roadmap, old, new)

review = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = review.read_text(encoding="utf-8").splitlines()
prefix = "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms |"
new_line = (
    "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms | "
    "12/34 authoritative drafting | In progress | 2026-08-03 | "
    "Tretí authoritative blok aktivuje kapitoly 9–12 a incident `MLOPS-PAY-92`. "
    "Pipeline orchestration oddeľuje source definition, compiled IR, run, task, attempt, cache hit, artifact a external side effect; zavádza complete cache keys, read-before-retry, logical intervals a component/journey/business recovery. "
    "Distributed-training kapitola používa aktuálny PyTorch `torchrun`/DDP a Kubeflow Trainer V2 `TrainJob` model, pričom rozlišuje ranks, worker-group generations, data partitioning, global batch, collectives, complete checkpoints a elastic resume. "
    "ML CI vytvára immutable evidence bundle cez code, data/feature contracts, compiled graph, component images, tiny training, package-load a permission/supply-chain gates bez predstierania produkčnej quality. "
    "Model CD oddeľuje promotion, immutable composite release, configured/resolved/loaded/serving state, bounded traffic exposure, multidimensional rollback a business acceptance. "
    "Kapitoly 9–12 prešli substantial prose, executable/model surface a subject/evidence/failure/recovery/acceptance gate-om. Reálne pipeline runs, distributed jobs, CI runners, deployments, traffic routing a business outcomes neboli vykonané; sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
matching = [index for index, line in enumerate(lines) if line.startswith(prefix)]
if len(matching) != 1:
    raise SystemExit(f"DOCUMENTATION-REVIEW-STATUS.md: expected one Section 19 row, found {len(matching)}")
lines[matching[0]] = new_line
review.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

print("Section 19 block 09-12 status files updated.")
