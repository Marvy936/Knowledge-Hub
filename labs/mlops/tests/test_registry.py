from __future__ import annotations

from pathlib import Path

import pytest

from mlops_lab.contracts import (
    ContractError,
    build_candidate_manifest,
    canonical_json_bytes,
    sha256_bytes,
)
from mlops_lab.registry import (
    build_registry_evidence,
    validate_registry_evidence,
    verify_source_model,
)


def _candidate(model_path: Path) -> dict[str, object]:
    return build_candidate_manifest(
        dataset_manifest={
            "schema_version": 1,
            "subject": {
                "dataset_name": "customers",
                "generation": "v1",
                "path": "runtime/customers.csv",
                "size_bytes": 12,
                "sha256": "1" * 64,
            },
        },
        model_path=model_path,
        evaluation={
            "accepted": True,
            "metrics": {"f1": 0.7, "recall": 0.65},
            "policy_generation": "promotion-v1",
        },
        source_revision="abc123",
    )


def _evidence() -> dict[str, object]:
    return build_registry_evidence(
        tracking_uri="http://127.0.0.1:5000",
        experiment_id="1",
        run_id="run-1",
        logged_model_id="m-1",
        candidate_id="a" * 64,
        source_revision="abc123",
        model_name="KnowledgeHubChurn",
        version="1",
        alias="champion",
        alias_resolved_version="1",
        source_uri="models:/m-1",
        source_run_id="run-1",
        model_version_status="READY",
        model_version_tags={
            "knowledge_hub.candidate_id": "a" * 64,
            "knowledge_hub.source_revision": "abc123",
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


def _resign(evidence: dict[str, object]) -> None:
    payload = {
        key: value
        for key, value in evidence.items()
        if key != "registry_evidence_id"
    }
    evidence["registry_evidence_id"] = sha256_bytes(canonical_json_bytes(payload))


def test_source_model_must_match_candidate_before_deserialization(
    tmp_path: Path,
) -> None:
    path = tmp_path / "model.joblib"
    path.write_bytes(b"model")
    candidate = _candidate(path)
    verify_source_model(candidate, path)

    path.write_bytes(b"tampered")
    with pytest.raises(ContractError, match="model size|model SHA-256"):
        verify_source_model(candidate, path)


def test_registry_evidence_is_deterministic() -> None:
    first = _evidence()
    second = _evidence()
    assert first == second
    assert len(first["registry_evidence_id"]) == 64


def test_registry_evidence_rejects_mutable_model_uri() -> None:
    evidence = _evidence()
    evidence["registry"]["exact_uri"] = "models:/KnowledgeHubChurn@champion"
    _resign(evidence)
    with pytest.raises(ContractError, match="exact registered model version"):
        validate_registry_evidence(evidence)


def test_registry_evidence_rejects_artifact_mismatch() -> None:
    evidence = _evidence()
    evidence["artifact_readback"]["downloaded_sha256"] = "c" * 64
    _resign(evidence)
    with pytest.raises(ContractError, match="artifact read-back"):
        validate_registry_evidence(evidence)


def test_registry_evidence_rejects_prediction_mismatch() -> None:
    evidence = _evidence()
    evidence["parity"]["registry_probability"] = 0.5
    evidence["parity"]["absolute_error"] = 0.25
    evidence["parity"]["passed"] = False
    _resign(evidence)
    with pytest.raises(ContractError, match="prediction parity"):
        validate_registry_evidence(evidence)


def test_registry_evidence_rejects_wrong_source_run() -> None:
    evidence = _evidence()
    evidence["registry"]["source_run_id"] = "other-run"
    _resign(evidence)
    with pytest.raises(ContractError, match="source run"):
        validate_registry_evidence(evidence)


def test_registry_evidence_rejects_tag_mismatch() -> None:
    evidence = _evidence()
    evidence["registry"]["tags"]["knowledge_hub.source_revision"] = "wrong"
    _resign(evidence)
    with pytest.raises(ContractError, match="tag read-back mismatch"):
        validate_registry_evidence(evidence)
