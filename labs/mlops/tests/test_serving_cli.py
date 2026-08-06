from __future__ import annotations

import json
from pathlib import Path

from mlops_lab.cli import main
from mlops_lab.contracts import canonical_json_bytes, sha256_bytes
from mlops_lab.registry import build_registry_evidence


def _write(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def _release() -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": 1,
        "alias": "champion",
        "previous_candidate_id": None,
        "candidate_id": "a" * 64,
        "dataset_sha256": "c" * 64,
        "model_sha256": "b" * 64,
        "evaluation_sha256": "d" * 64,
        "policy_generation": "ml-training-manifest-v1",
        "source_revision": "exact-revision",
    }
    return {**payload, "release_id": sha256_bytes(canonical_json_bytes(payload))}


def _registry() -> dict[str, object]:
    return build_registry_evidence(
        tracking_uri="http://127.0.0.1:5000",
        experiment_id="1",
        run_id="run-1",
        logged_model_id="m-1",
        candidate_id="a" * 64,
        source_revision="exact-revision",
        model_name="KnowledgeHubChurn",
        version="1",
        alias="champion",
        alias_resolved_version="1",
        source_uri="models:/m-1",
        source_run_id="run-1",
        model_version_status="READY",
        model_version_tags={
            "knowledge_hub.candidate_id": "a" * 64,
            "knowledge_hub.source_revision": "exact-revision",
            "knowledge_hub.model_sha256": "b" * 64,
        },
        artifact_path="source/model.joblib",
        original_model_sha256="b" * 64,
        downloaded_model_sha256="b" * 64,
        model_size_bytes=123,
        request={"feature": 1},
        source_probability=0.75,
        source_prediction=1,
        registry_probability=0.75,
        registry_prediction=1,
        mlflow_version="3.14.0",
    )


def test_serving_cli_lifecycle(tmp_path: Path, capsys) -> None:
    release_path = tmp_path / "release.json"
    registry_path = tmp_path / "registry.json"
    stable_path = tmp_path / "stable.json"
    canary_path = tmp_path / "canary.json"
    initial_path = tmp_path / "initial-routing.json"
    canary_state_path = tmp_path / "canary-routing.json"
    rollback_path = tmp_path / "rollback.json"
    _write(release_path, _release())
    _write(registry_path, _registry())

    assert main(
        [
            "deployment",
            "--release",
            str(release_path),
            "--registry-evidence",
            str(registry_path),
            "--service-name",
            "churn-api",
            "--generation",
            "generation-1",
            "--image-reference",
            "ghcr.io/example/churn-api",
            "--image-digest",
            "sha256:" + "1" * 64,
            "--output",
            str(stable_path),
        ]
    ) == 0
    capsys.readouterr()
    assert main(
        [
            "deployment",
            "--release",
            str(release_path),
            "--registry-evidence",
            str(registry_path),
            "--service-name",
            "churn-api",
            "--generation",
            "generation-2",
            "--image-reference",
            "ghcr.io/example/churn-api",
            "--image-digest",
            "sha256:" + "2" * 64,
            "--output",
            str(canary_path),
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        [
            "routing-state",
            "--stable",
            str(stable_path),
            "--canary-basis-points",
            "0",
            "--expected-current-state-id",
            "none",
            "--output",
            str(initial_path),
        ]
    ) == 0
    capsys.readouterr()
    initial = json.loads(initial_path.read_text(encoding="utf-8"))

    assert main(
        [
            "routing-state",
            "--stable",
            str(stable_path),
            "--canary",
            str(canary_path),
            "--canary-basis-points",
            "1000",
            "--current-state",
            str(initial_path),
            "--expected-current-state-id",
            initial["routing_state_id"],
            "--output",
            str(canary_state_path),
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        [
            "route",
            "--routing-state",
            str(canary_state_path),
            "--stable",
            str(stable_path),
            "--canary",
            str(canary_path),
            "--routing-key",
            "tenant-1/request-99",
        ]
    ) == 0
    routed = json.loads(capsys.readouterr().out)
    assert routed["status"] == "request_routed"
    assert routed["selected_role"] in {"stable", "canary"}
    assert len(routed["routing_key_sha256"]) == 64

    canary_state = json.loads(canary_state_path.read_text(encoding="utf-8"))
    assert main(
        [
            "rollback",
            "--current-state",
            str(canary_state_path),
            "--target-stable",
            str(stable_path),
            "--expected-current-state-id",
            canary_state["routing_state_id"],
            "--output",
            str(rollback_path),
        ]
    ) == 0
    capsys.readouterr()
    rollback = json.loads(rollback_path.read_text(encoding="utf-8"))
    stable = json.loads(stable_path.read_text(encoding="utf-8"))
    assert rollback["stable_deployment_id"] == stable["deployment_id"]
    assert rollback["canary_deployment_id"] is None
    assert rollback["canary_basis_points"] == 0
