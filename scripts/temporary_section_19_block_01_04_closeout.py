#!/usr/bin/env python3
"""Temporary closeout helper for Section 19 chapters 01-04."""

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
    "- [ ] ML lifecycle a rozdiel medzi DevOps a MLOps":
        "- [x] [ML lifecycle a rozdiel medzi DevOps a MLOps](docs/19-mlops-and-ml-platforms/ml-lifecycle-devops-vs-mlops.md)",
    "- [ ] Data, code, environment a model lineage":
        "- [x] [Data, code, environment a model lineage](docs/19-mlops-and-ml-platforms/data-code-environment-model-lineage.md)",
    "- [ ] Dataset versioning":
        "- [x] [Dataset versioning](docs/19-mlops-and-ml-platforms/dataset-versioning.md)",
    "- [ ] Experiment tracking":
        "- [x] [Experiment tracking](docs/19-mlops-and-ml-platforms/experiment-tracking.md)",
}
for old, new in replacements.items():
    replace_once_or_present(roadmap, old, new)

review = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = review.read_text(encoding="utf-8").splitlines()
prefix = "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms |"
new_line = (
    "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms | "
    "4/34 authoritative drafting | In progress | 2026-08-03 | "
    "Prvý authoritative blok aktivuje kapitoly 1–4 a vytvára spoločný incident `MLOPS-PAY-90`. "
    "Kapitoly oddeľujú DevOps software release od MLOps data/model/feedback variability; definujú composite release subject, CI/CD/CT, configured/resolved/loaded/exercised/outcome evidence a component/journey/business recovery; "
    "budujú traversable data-code-environment-model lineage s immutable dataset, run, artifact a deployment identities; vysvetľujú physical/logical/evaluation dataset versions, DVC a Git LFS pointer boundaries, schema/semantic contracts, label maturity, split membership a garbage-collection reachability; "
    "a používajú MLflow experiment/run/logged-model model, backend/artifact store separation, explicitný tracking contract, autologging boundary, unknown outcomes a read-before-retry recovery. "
    "Prvé štyri kapitoly prešli substantial prose, executable/model surface a subject/evidence/failure/recovery/acceptance gate-om. "
    "Reálne datasety, tracking server, object storage, training, model promotion, serving a business outcome neboli vykonané; sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
matching = [index for index, line in enumerate(lines) if line.startswith(prefix)]
if len(matching) != 1:
    raise SystemExit(f"DOCUMENTATION-REVIEW-STATUS.md: expected one Section 19 row, found {len(matching)}")
lines[matching[0]] = new_line
review.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

print("Section 19 block 01-04 status files updated.")
