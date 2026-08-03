#!/usr/bin/env python3
"""Temporary closeout helper for Section 19 chapters 25-28."""

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
    "- [ ] Privacy, security a adversarial ML":
        "- [x] [Privacy, security a adversarial ML](docs/19-mlops-and-ml-platforms/privacy-security-adversarial-ml.md)",
    "- [ ] ML supply-chain security":
        "- [x] [ML supply-chain security](docs/19-mlops-and-ml-platforms/ml-supply-chain-security.md)",
    "- [ ] MLflow experiment tracking a Model Registry":
        "- [x] [MLflow experiment tracking a Model Registry](docs/19-mlops-and-ml-platforms/mlflow-experiment-tracking-model-registry.md)",
    "- [ ] MLflow evaluation, tracing a deployment":
        "- [x] [MLflow evaluation, tracing a deployment](docs/19-mlops-and-ml-platforms/mlflow-evaluation-tracing-deployment.md)",
}
for old, new in replacements.items():
    replace_once_or_present(roadmap, old, new)

review = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = review.read_text(encoding="utf-8").splitlines()
prefix = "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms |"
new_line = (
    "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms | "
    "28/34 authoritative drafting | In progress | 2026-08-03 | "
    "Siedmy authoritative blok aktivuje kapitoly 25–28 a incident `MLOPS-PAY-96`. "
    "Privacy/security kapitola viaže explicitný threat model, lifecycle attacker capability, data minimization a retention, membership/inversion/extraction leakage, evasion, poisoning/backdoors, serialization, endpoint abuse, workload isolation, privacy-safe telemetry a red-team/recovery acceptance. "
    "Supply-chain kapitola vytvára trust graph od source, data a dependency locku cez trusted builder, SLSA 1.2 provenance, SBOM/model/data manifests, Sigstore signatures/attestations, immutable artifact retention a least-privilege CI identities až po admission a loaded runtime fingerprint. "
    "MLflow Tracking/Registry kapitola implementuje database/artifact store separation, secure installs, dataset inputs, experiment/run/Logged Model lineage, exact registration read-back, mutable aliases ako control pointer, environment separation, smoke serving a dual-store restore. "
    "MLflow evaluation/tracing/deployment kapitola striktne oddeľuje classic `mlflow.models.evaluate()`/`MetricThreshold`, GenAI `mlflow.genai.evaluate()`/`Scorer`, production tracing a external deployment target, pričom všetky evidence viaže na immutable release a data-plane proof. "
    "Kapitoly 25–28 prešli substantial prose, executable/model surface a subject/evidence/failure/recovery/acceptance gate-om. Reálne privacy/adversarial tests, supply-chain signing, MLflow server, Registry mutations, trace export, deployment, recovery a business outcomes neboli vykonané; sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
matching = [index for index, line in enumerate(lines) if line.startswith(prefix)]
if len(matching) != 1:
    raise SystemExit(
        f"DOCUMENTATION-REVIEW-STATUS.md: expected one Section 19 row, found {len(matching)}"
    )
lines[matching[0]] = new_line
review.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

print("Section 19 block 25-28 status files updated.")
