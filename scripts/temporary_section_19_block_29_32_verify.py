#!/usr/bin/env python3
"""Verify that Section 19 chapters 29-32 have no critical/high audit entries."""

from pathlib import Path

AUDIT = Path("DOCUMENTATION-AUDIT.md")
FILES = [
    "kubeflow-pipelines.md",
    "kubeflow-trainer-distributed-training.md",
    "kserve-kubernetes-model-serving.md",
    "amazon-sagemaker-cloud-mlops-mapping.md",
]

audit = AUDIT.read_text(encoding="utf-8")
critical_high = audit.split("## Critical and high findings", 1)[1].split(
    "## All findings by rule", 1
)[0]
remaining = []
for name in FILES:
    marker = f"### `docs/19-mlops-and-ml-platforms/{name}`"
    if marker not in critical_high:
        continue
    remaining.append(name)
    details = critical_high.split(marker, 1)[1].split("\n### `", 1)[0]
    print(f"\n{marker}{details}\n")

if remaining:
    raise SystemExit(
        f"Section 19 block 29-32 critical/high findings remain: {remaining}"
    )

print("Section 19 block 29-32 has no critical/high audit entries.")
