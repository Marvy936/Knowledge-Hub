#!/usr/bin/env python3
"""Temporary closeout helper for Section 19 chapters 17-20."""

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
    "- [ ] Model serving a autoscaling":
        "- [x] [Model serving a autoscaling](docs/19-mlops-and-ml-platforms/model-serving-autoscaling.md)",
    "- [ ] GPU scheduling, utilization a capacity":
        "- [x] [GPU scheduling, utilization a capacity](docs/19-mlops-and-ml-platforms/gpu-scheduling-utilization-capacity.md)",
    "- [ ] Model monitoring":
        "- [x] [Model monitoring](docs/19-mlops-and-ml-platforms/model-monitoring.md)",
    "- [ ] Data drift, concept drift a prediction drift":
        "- [x] [Data drift, concept drift a prediction drift](docs/19-mlops-and-ml-platforms/data-drift-concept-drift-prediction-drift.md)",
}
for old, new in replacements.items():
    replace_once_or_present(roadmap, old, new)

review = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = review.read_text(encoding="utf-8").splitlines()
prefix = "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms |"
new_line = (
    "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms | "
    "20/34 authoritative drafting | In progress | 2026-08-03 | "
    "Piaty authoritative blok aktivuje kapitoly 17–20 a incident `MLOPS-PAY-94`. "
    "Model serving oddeľuje immutable release, KServe desired/resolved state, loaded runtime, request exposure, useful capacity a business deadline; modeluje deployment-mode-specific autoscaling, concurrency, scale-to-zero cold budget, batching, load shedding a composite recovery. "
    "GPU kapitola viaže physical device, driver/runtime, device plugin, extended resource, scheduler binding a exercised workload; oddeľuje exclusive GPU, MIG a time-slicing, fragmentation, memory high-water mark, DCGM telemetry, pod/node autoscaling a isolation acceptance. "
    "Monitoring kapitola spája platform, service, ML a business vrstvy cez request-correlated release identity, mutually exclusive result classes, correct denominators, Prometheus histogram semantics, traces/logs, label coverage a monitoring-pipeline health. "
    "Drift kapitola oddeľuje `P(X)`, `P(Y)`, `P(Ŷ)` a `P(Y|X)`, versionuje reference/current populations, event-time completeness, statistical method a multiplicity policy a zakazuje automatický retrain z jedného drift signal-u. "
    "Kapitoly 17–20 prešli substantial prose, executable/model surface a subject/evidence/failure/recovery/acceptance gate-om. Reálne KServe serving, GPU scheduling, autoscaling, telemetry, drift jobs, recovery a business outcomes neboli vykonané; sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
matching = [index for index, line in enumerate(lines) if line.startswith(prefix)]
if len(matching) != 1:
    raise SystemExit(
        f"DOCUMENTATION-REVIEW-STATUS.md: expected one Section 19 row, found {len(matching)}"
    )
lines[matching[0]] = new_line
review.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

print("Section 19 block 17-20 status files updated.")
