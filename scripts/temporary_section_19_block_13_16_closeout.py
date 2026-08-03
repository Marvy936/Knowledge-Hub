#!/usr/bin/env python3
"""Temporary closeout helper for Section 19 chapters 13-16."""

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
    "- [ ] Continuous Training a retraining triggers":
        "- [x] [Continuous Training a retraining triggers](docs/19-mlops-and-ml-platforms/continuous-training-retraining-triggers.md)",
    "- [ ] Model validation a promotion gates":
        "- [x] [Model validation a promotion gates](docs/19-mlops-and-ml-platforms/model-validation-promotion-gates.md)",
    "- [ ] Batch, online a streaming inference":
        "- [x] [Batch, online a streaming inference](docs/19-mlops-and-ml-platforms/batch-online-streaming-inference.md)",
    "- [ ] Shadow, canary a A/B model deployment":
        "- [x] [Shadow, canary a A/B model deployment](docs/19-mlops-and-ml-platforms/shadow-canary-ab-model-deployment.md)",
}
for old, new in replacements.items():
    replace_once_or_present(roadmap, old, new)

review = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = review.read_text(encoding="utf-8").splitlines()
prefix = "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms |"
new_line = (
    "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms | "
    "16/34 authoritative drafting | In progress | 2026-08-03 | "
    "Štvrtý authoritative blok aktivuje kapitoly 13–16 a incident `MLOPS-PAY-93`. "
    "Continuous Training oddeľuje periodic/event trigger od validated retraining need, data/label readiness, watermark, deduplication, concurrency a candidate-only outcome. "
    "Validation a promotion gates viažu exact candidate/baseline/dataset/evaluator/policy, aggregate aj decision metrics, segment/calibration/robustness/package/runtime evidence, waivers a conditional Registry mutation. "
    "Inference kapitola rozlišuje batch manifests a intervals, online request/deadline/fallback a streaming partition/offset/watermark/idempotency semantics s cross-mode parity. "
    "Shadow/canary/A-B kapitola oddeľuje zero-side-effect live comparison, bounded rollout a causal experiment cez stable assignment, actual exposure, interference, mature outcomes a composite rollback. "
    "Kapitoly 13–16 prešli substantial prose, executable/model surface a subject/evidence/failure/recovery/acceptance gate-om. Reálne triggers, evaluations, inference paths, experiments a business outcomes neboli vykonané; sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
matching = [index for index, line in enumerate(lines) if line.startswith(prefix)]
if len(matching) != 1:
    raise SystemExit(f"DOCUMENTATION-REVIEW-STATUS.md: expected one Section 19 row, found {len(matching)}")
lines[matching[0]] = new_line
review.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

print("Section 19 block 13-16 status files updated.")
