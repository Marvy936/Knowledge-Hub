from __future__ import annotations

from pathlib import Path


def test_serving_dockerfile_excludes_runtime_state_and_runs_non_root() -> None:
    dockerfile = (
        Path(__file__).resolve().parents[1] / "Dockerfile.serving"
    ).read_text(encoding="utf-8")

    assert "FROM python:3.12-slim" in dockerfile
    assert "COPY labs/machine-learning /" not in dockerfile
    assert "COPY labs/mlops /" not in dockerfile
    assert "COPY labs/machine-learning/src " in dockerfile
    assert "COPY labs/mlops/src " in dockerfile
    assert ".runtime" not in dockerfile
    assert "model.joblib" not in dockerfile
    assert "deployment.json" not in "\n".join(
        line for line in dockerfile.splitlines() if line.startswith("COPY ")
    )
    assert "USER 10001:10001" in dockerfile
    assert '"--workers", "1"' in dockerfile
    assert "MLOPS_DEPLOYMENT_MANIFEST=/runtime/deployment.json" in dockerfile
    assert "MLOPS_ARTIFACT_DIR=/runtime/artifact" in dockerfile
    assert "HEALTHCHECK" in dockerfile
