from __future__ import annotations

from pathlib import Path

import pytest

from mlops_lab.contracts import ContractError, sha256_file
from mlops_lab.lineage import build_evaluation_from_training_manifest


def _manifest(dataset: Path, model: Path) -> dict[str, object]:
    return {
        "schema_version": 1,
        "artifact_type": "trusted-local-scikit-learn-pipeline",
        "model_file": model.name,
        "model_sha256": sha256_file(model),
        "dataset_path_at_training": str(dataset),
        "dataset_sha256": sha256_file(dataset),
        "dataset_rows": 2,
        "dataset_validation": {"status": "valid"},
        "feature_columns": ["feature"],
        "target_column": "target",
        "excluded_identity_column": "id",
        "seed": 20260805,
        "split_rows": {"train": 1, "validation": 1, "test": 1},
        "selected_model": "logistic_regression",
        "decision_threshold": 0.72,
        "threshold_status": "recall_gate_satisfied",
        "validation_metrics": {"f1": 0.66, "recall": 0.62},
        "test_metrics": {
            "accuracy": 0.68,
            "f1": 0.63,
            "precision": 0.70,
            "recall": 0.57,
            "roc_auc": 0.74,
        },
        "experiments": [],
        "acceptance_gates": {
            "minimum_test_f1": 0.55,
            "minimum_test_recall": 0.55,
            "selected_f1_must_exceed_dummy": True,
        },
        "library_versions": {
            "python": "3.12.12",
            "numpy": "2.3.0",
            "pandas": "2.3.0",
            "scikit_learn": "1.8.0",
            "joblib": "1.5.2",
        },
        "source_revision": "exact-revision",
        "security_boundary": {
            "load_only_from_trusted_source": True,
            "checksum_verification_required": True,
            "exact_library_version_match_required": True,
        },
    }


def _write_manifest(path: Path, manifest: dict[str, object]) -> None:
    import json

    path.write_text(json.dumps(manifest), encoding="utf-8")


def test_evaluation_is_derived_from_exact_training_manifest(tmp_path: Path) -> None:
    dataset = tmp_path / "customers.csv"
    model = tmp_path / "model.joblib"
    manifest_path = tmp_path / "manifest.json"
    dataset.write_bytes(b"id,feature,target\n1,1,0\n")
    model.write_bytes(b"trusted-model")
    _write_manifest(manifest_path, _manifest(dataset, model))

    evaluation = build_evaluation_from_training_manifest(
        training_manifest_path=manifest_path,
        dataset_path=dataset,
        model_path=model,
        expected_source_revision="exact-revision",
    )

    assert evaluation["accepted"] is True
    assert evaluation["policy_generation"] == "ml-training-manifest-v1"
    assert evaluation["metrics"]["f1"] == 0.63
    assert evaluation["metrics"]["recall"] == 0.57
    assert evaluation["metrics"]["decision_threshold"] == 0.72


def test_lineage_refuses_changed_dataset_bytes(tmp_path: Path) -> None:
    dataset = tmp_path / "customers.csv"
    model = tmp_path / "model.joblib"
    manifest_path = tmp_path / "manifest.json"
    dataset.write_bytes(b"dataset-v1")
    model.write_bytes(b"trusted-model")
    _write_manifest(manifest_path, _manifest(dataset, model))
    dataset.write_bytes(b"dataset-v2")

    with pytest.raises(ContractError, match="dataset SHA-256"):
        build_evaluation_from_training_manifest(
            training_manifest_path=manifest_path,
            dataset_path=dataset,
            model_path=model,
            expected_source_revision="exact-revision",
        )


def test_lineage_refuses_changed_model_bytes(tmp_path: Path) -> None:
    dataset = tmp_path / "customers.csv"
    model = tmp_path / "model.joblib"
    manifest_path = tmp_path / "manifest.json"
    dataset.write_bytes(b"dataset")
    model.write_bytes(b"model-v1")
    _write_manifest(manifest_path, _manifest(dataset, model))
    model.write_bytes(b"model-v2")

    with pytest.raises(ContractError, match="model SHA-256"):
        build_evaluation_from_training_manifest(
            training_manifest_path=manifest_path,
            dataset_path=dataset,
            model_path=model,
            expected_source_revision="exact-revision",
        )


def test_lineage_refuses_wrong_source_revision(tmp_path: Path) -> None:
    dataset = tmp_path / "customers.csv"
    model = tmp_path / "model.joblib"
    manifest_path = tmp_path / "manifest.json"
    dataset.write_bytes(b"dataset")
    model.write_bytes(b"model")
    _write_manifest(manifest_path, _manifest(dataset, model))

    with pytest.raises(ContractError, match="source revision"):
        build_evaluation_from_training_manifest(
            training_manifest_path=manifest_path,
            dataset_path=dataset,
            model_path=model,
            expected_source_revision="other-revision",
        )


def test_lineage_refuses_failed_acceptance_gate(tmp_path: Path) -> None:
    dataset = tmp_path / "customers.csv"
    model = tmp_path / "model.joblib"
    manifest_path = tmp_path / "manifest.json"
    dataset.write_bytes(b"dataset")
    model.write_bytes(b"model")
    manifest = _manifest(dataset, model)
    manifest["test_metrics"]["recall"] = 0.20
    _write_manifest(manifest_path, manifest)

    with pytest.raises(ContractError, match="recall is below"):
        build_evaluation_from_training_manifest(
            training_manifest_path=manifest_path,
            dataset_path=dataset,
            model_path=model,
            expected_source_revision="exact-revision",
        )
