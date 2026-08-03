#!/usr/bin/env python3
"""Temporary closeout helper for Section 19 chapters 05-08."""

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
    "- [ ] Artifact stores":
        "- [x] [Artifact stores](docs/19-mlops-and-ml-platforms/artifact-stores.md)",
    "- [ ] Model packaging a reproducible environments":
        "- [x] [Model packaging a reproducible environments](docs/19-mlops-and-ml-platforms/model-packaging-reproducible-environments.md)",
    "- [ ] Model Registry, versions, stages a aliases":
        "- [x] [Model Registry, versions, stages a aliases](docs/19-mlops-and-ml-platforms/model-registry-versions-stages-aliases.md)",
    "- [ ] Feature stores a online/offline consistency":
        "- [x] [Feature stores a online/offline consistency](docs/19-mlops-and-ml-platforms/feature-stores-online-offline-consistency.md)",
}
for old, new in replacements.items():
    replace_once_or_present(roadmap, old, new)

review = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = review.read_text(encoding="utf-8").splitlines()
prefix = "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms |"
new_line = (
    "| `19-mlops-and-ml-platforms` — MLOps and ML Platforms | "
    "8/34 authoritative drafting | In progress | 2026-08-03 | "
    "Druhý authoritative blok aktivuje kapitoly 5–8 a incident `MLOPS-PAY-91`. "
    "Kapitoly oddeľujú MLflow backend metadata od artifact-store bytes a zavádzajú committed multi-file manifest, checksum/signature, cache-independent read-back, retention reachability a DR; "
    "vysvetľujú MLflow Model flavors, PyFunc, serialization/code boundary, dependency inference oproti locking-u, signatures, OCI packaging, remote-loaded modely, conversion parity a supply-chain controls; "
    "nahrádzajú deprecated fixed Model Stages aliases/tags a environment-specific registered modelmi, pričom rozlišujú Registry version/alias/promotion od immutable package a loaded runtime; "
    "a modelujú Feast feature views/services, point-in-time historical retrieval, online latest-value store, materialization, push/stream paths, freshness, fallback a viacrozmernú offline-online consistency. "
    "Kapitoly 5–8 prešli substantial prose, executable/model surface a subject/evidence/failure/recovery/acceptance gate-om. "
    "Reálne object stores, package builds, Registry mutations, Feast deployment, materialization, online serving a business outcomes neboli vykonané; sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
matching = [index for index, line in enumerate(lines) if line.startswith(prefix)]
if len(matching) != 1:
    raise SystemExit(f"DOCUMENTATION-REVIEW-STATUS.md: expected one Section 19 row, found {len(matching)}")
lines[matching[0]] = new_line
review.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

print("Section 19 block 05-08 status files updated.")
