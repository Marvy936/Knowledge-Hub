#!/usr/bin/env python3
"""Temporary closeout helper for Section 19 chapters 21-24."""

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
    "- [ ] Performance, latency, throughput a cost monitoring":
        "- [x] [Performance, latency, throughput a cost monitoring](docs/19-mlops-and-ml-platforms/performance-latency-throughput-cost-monitoring.md)",
    "- [ ] Feedback loops a ground-truth delay":
        "- [x] [Feedback loops a ground-truth delay](docs/19-mlops-and-ml-platforms/feedback-loops-ground-truth-delay.md)",
    "- [ ] Model rollback a recovery":
        "- [x] [Model rollback a recovery](docs/19-mlops-and-ml-platforms/model-rollback-recovery.md)",
    "- [ ] Governance, approvals a audit":
        "- [x] [Governance, approvals a audit](docs/19-mlops-and-ml-platforms/governance-approvals-audit.md)",
}
for old, new in replacements.items():
    replace_once_or_present(roadmap, old, new)

review = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = review.read_text(encoding="utf-8").splitlines()
prefix = "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms |"
new_line = (
    "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms | "
    "24/34 authoritative drafting | In progress | 2026-08-03 | "
    "Šiesty authoritative blok aktivuje kapitoly 21–24 a incident `MLOPS-PAY-95`. "
    "Performance kapitola viaže composite release, traffic a resource profile na latency decomposition, useful throughput, saturation, OpenCost asset/allocation/usage vrstvy, idle policy a cost per deadline-successful action alebo mature outcome namiesto raw HTTP response. "
    "Feedback kapitola zachytáva prediction-action-environment-label lifecycle, versioned label definitions, maturity horizons, coverage, right censoring, selective labels, human-review bias, counterfactual blind spots a reprodukovateľné event-time snapshoty. "
    "Rollback kapitola používa immutable known-good composite target, first-divergence decision, traffic/deployment/model/feature/policy strategy, compatibility, read-before-retry, loaded parity, side-effect reconciliation, game days a component/journey/business recovery. "
    "Governance kapitola viaže inventory, intended use, risk-based controls, separation of duties, content-addressed evidence, policy-as-code, human judgment, append-only audit, NIST AI RMF mapping, EU AI Act context, expirovateľné waivery a retirement. "
    "Kapitoly 21–24 prešli substantial prose, executable/model surface a subject/evidence/failure/recovery/acceptance gate-om. Reálne cost allocation, feedback joins, rollback, approvals, regulatory classification, runtime recovery a business outcomes neboli vykonané; sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
matching = [index for index, line in enumerate(lines) if line.startswith(prefix)]
if len(matching) != 1:
    raise SystemExit(
        f"DOCUMENTATION-REVIEW-STATUS.md: expected one Section 19 row, found {len(matching)}"
    )
lines[matching[0]] = new_line
review.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

print("Section 19 block 21-24 status files updated.")
