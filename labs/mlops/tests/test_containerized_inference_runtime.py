from __future__ import annotations

import importlib.util
import json
import stat
from pathlib import Path

import pytest

from mlops_lab.contracts import canonical_json_bytes, promote_candidate, sha256_bytes


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_containerized_inference_runtime.py"
SPEC = importlib.util.spec_from_file_location("run_containerized_inference_runtime", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


def _deployment() -> dict[str, object]:
    return {
        "service_name": "knowledge-hub-churn-api",
        "deployment_id": "a" * 64,
        "generation": "container-runtime-v1",
        "release_id": "b" * 64,
        "candidate_id": "c" * 64,
        "model": {
            "sha256": "d" * 64,
            "exact_uri": "models:/KnowledgeHubChurn/2",
        },
        "image": {"digest": "sha256:" + "e" * 64},
    }


def _candidate(seed: str) -> dict[str, object]:
    evaluation_payload = {
        "accepted": True,
        "metrics": {"f1": 0.8, "recall": 0.75},
        "policy_generation": "policy-v1",
    }
    payload = {
        "schema_version": 1,
        "dataset": {
            "name": "customers",
            "generation": "dataset-v1",
            "sha256": seed * 64,
        },
        "model": {
            "size_bytes": 10,
            "sha256": ("a" if seed != "a" else "b") * 64,
        },
        "evaluation": {
            **evaluation_payload,
            "sha256": sha256_bytes(canonical_json_bytes(evaluation_payload)),
        },
        "source_revision": "c" * 40,
    }
    return {**payload, "candidate_id": sha256_bytes(canonical_json_bytes(payload))}


def test_image_id_requires_content_addressed_sha256() -> None:
    good = "sha256:" + "1" * 64
    assert runtime._validate_image_id(good) == good

    with pytest.raises(runtime.RuntimeGateError, match="sha256"):
        runtime._validate_image_id("knowledge-hub-mlops-runtime:latest")

    with pytest.raises(runtime.RuntimeGateError, match="64-hex"):
        runtime._validate_image_id("sha256:abcd")


def test_subject_sha_requires_exact_lowercase_git_sha1() -> None:
    good = "a" * 40
    assert runtime._require_subject_sha(good) == good

    with pytest.raises(runtime.RuntimeGateError, match="40-character"):
        runtime._require_subject_sha("a" * 39)

    with pytest.raises(runtime.RuntimeGateError, match="40-character"):
        runtime._require_subject_sha("A" * 40)


def test_explicit_subject_mode_requires_complete_inputs_and_release(tmp_path: Path) -> None:
    runtime_dir = tmp_path / "runtime"
    runtime_dir.mkdir()
    candidate = tmp_path / "candidate.json"
    registry = tmp_path / "registry.json"
    artifact = tmp_path / "artifact"
    release = tmp_path / "release.json"
    candidate.write_text("{}\n", encoding="utf-8")
    registry.write_text("{}\n", encoding="utf-8")
    artifact.mkdir()
    release.write_text("{}\n", encoding="utf-8")

    with pytest.raises(runtime.RuntimeGateError, match="requires --candidate"):
        runtime._resolve_subject_paths(
            runtime_dir=runtime_dir,
            candidate_path=candidate,
            registry_path=None,
            artifact_dir=artifact,
            release_path=release,
        )

    with pytest.raises(runtime.RuntimeGateError, match="requires --release"):
        runtime._resolve_subject_paths(
            runtime_dir=runtime_dir,
            candidate_path=candidate,
            registry_path=registry,
            artifact_dir=artifact,
            release_path=None,
        )

    resolved = runtime._resolve_subject_paths(
        runtime_dir=runtime_dir,
        candidate_path=candidate,
        registry_path=registry,
        artifact_dir=artifact,
        release_path=release,
    )
    assert resolved["input_mode"] == "explicit-subjects"
    assert resolved["candidate_path"] == candidate.resolve()
    assert resolved["registry_path"] == registry.resolve()
    assert resolved["artifact_dir"] == artifact.resolve()
    assert resolved["release_path"] == release.resolve()


def test_provided_release_must_match_exact_candidate_lineage(tmp_path: Path) -> None:
    first = _candidate("d")
    second = _candidate("e")
    second_release, _ = promote_candidate(
        candidate=second,
        alias_state={"schema_version": 1, "aliases": {}},
        alias="champion",
        expected_current=None,
    )
    release_path = tmp_path / "release.json"
    release_path.write_text(json.dumps(second_release), encoding="utf-8")

    with pytest.raises(runtime.RuntimeGateError, match="does not match candidate subject"):
        runtime._resolve_release(
            candidate=first,
            provided_release_path=release_path,
        )


def test_readonly_mount_preparation_preserves_model_bytes(tmp_path: Path) -> None:
    deployment = tmp_path / "deployment.json"
    manifest = tmp_path / "manifest.json"
    model = tmp_path / "model.joblib"
    deployment.write_text("{}\n", encoding="utf-8")
    manifest.write_text("{}\n", encoding="utf-8")
    model.write_bytes(b"stable-model-bytes")
    expected = runtime._sha256_file(model)

    modes = runtime._prepare_readonly_mounts(
        deployment_path=deployment,
        artifact_manifest_path=manifest,
        model_path=model,
        expected_model_sha256=expected,
    )

    assert modes == {
        "deployment": "0o444",
        "manifest": "0o444",
        "model": "0o444",
    }
    for path in (deployment, manifest, model):
        assert stat.S_IMODE(path.stat().st_mode) == 0o444
    assert runtime._sha256_file(model) == expected


def test_readonly_mount_preparation_refuses_model_tampering(tmp_path: Path) -> None:
    deployment = tmp_path / "deployment.json"
    manifest = tmp_path / "manifest.json"
    model = tmp_path / "model.joblib"
    deployment.write_text("{}\n", encoding="utf-8")
    manifest.write_text("{}\n", encoding="utf-8")
    model.write_bytes(b"tampered")

    with pytest.raises(runtime.RuntimeGateError, match="model digest changed"):
        runtime._prepare_readonly_mounts(
            deployment_path=deployment,
            artifact_manifest_path=manifest,
            model_path=model,
            expected_model_sha256="0" * 64,
        )


def test_ready_response_must_equal_exact_deployment_identity() -> None:
    deployment = _deployment()
    ready = {
        "status": "ready",
        "service_name": deployment["service_name"],
        "deployment_id": deployment["deployment_id"],
        "generation": deployment["generation"],
        "release_id": deployment["release_id"],
        "model_sha256": deployment["model"]["sha256"],
        "registry_exact_uri": deployment["model"]["exact_uri"],
        "image_digest": deployment["image"]["digest"],
    }
    runtime._validate_ready(ready, deployment=deployment)

    tampered = dict(ready)
    tampered["image_digest"] = "sha256:" + "f" * 64
    with pytest.raises(runtime.RuntimeGateError, match="exact deployment"):
        runtime._validate_ready(tampered, deployment=deployment)


def test_prediction_response_cannot_hide_wrong_runtime_subject() -> None:
    deployment = _deployment()
    prediction = {
        "prediction": 1,
        "probability": 0.81,
        "decision_threshold": 0.72,
        "service_name": deployment["service_name"],
        "deployment_id": deployment["deployment_id"],
        "generation": deployment["generation"],
        "release_id": deployment["release_id"],
        "candidate_id": deployment["candidate_id"],
        "model_sha256": deployment["model"]["sha256"],
        "registry_exact_uri": deployment["model"]["exact_uri"],
        "image_digest": deployment["image"]["digest"],
    }
    runtime._validate_prediction(prediction, deployment=deployment)

    wrong = dict(prediction)
    wrong["deployment_id"] = "f" * 64
    with pytest.raises(runtime.RuntimeGateError, match="deployment_id"):
        runtime._validate_prediction(wrong, deployment=deployment)

    invalid_probability = dict(prediction)
    invalid_probability["probability"] = "0.81"
    with pytest.raises(runtime.RuntimeGateError, match="probability"):
        runtime._validate_prediction(invalid_probability, deployment=deployment)
