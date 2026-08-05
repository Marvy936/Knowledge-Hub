from __future__ import annotations

from pathlib import Path

import pytest

from ml_lab.data import write_dataset
from ml_lab.errors import ArtifactIntegrityError, DataValidationError
from ml_lab.inference import predict_record
from ml_lab.io_utils import sha256_file
from ml_lab.training import train_and_package
from ml_lab.validation import load_dataset, validate_dataframe


SAMPLE_RECORD = {
    "tenure_months": 8,
    "monthly_spend_eur": 79.5,
    "support_tickets_90d": 4,
    "login_days_30d": 6,
    "days_since_last_login": 19,
    "contract_type": "monthly",
    "region": "east",
    "auto_pay": "no",
}


def test_dataset_generation_is_byte_reproducible(tmp_path: Path) -> None:
    first = write_dataset(tmp_path / "first.csv", rows=500, seed=42)
    second = write_dataset(tmp_path / "second.csv", rows=500, seed=42)
    assert first.read_bytes() == second.read_bytes()
    assert sha256_file(first) == sha256_file(second)


def test_validation_rejects_post_outcome_leakage(tmp_path: Path) -> None:
    dataset = write_dataset(tmp_path / "customers.csv", rows=500, seed=42)
    frame = load_dataset(dataset)
    frame["future_refund_30d"] = frame["churned_next_30d"]
    with pytest.raises(DataValidationError, match="leakage"):
        validate_dataframe(frame)


def test_validation_rejects_non_numeric_feature(tmp_path: Path) -> None:
    dataset = write_dataset(tmp_path / "customers.csv", rows=500, seed=42)
    frame = load_dataset(dataset)
    frame["monthly_spend_eur"] = frame["monthly_spend_eur"].astype(object)
    frame.loc[0, "monthly_spend_eur"] = "not-a-number"
    with pytest.raises(DataValidationError, match="non-numeric"):
        validate_dataframe(frame)


def test_training_packaging_and_inference_end_to_end(tmp_path: Path) -> None:
    dataset = write_dataset(tmp_path / "customers.csv", rows=900, seed=20260805)
    artifact_dir = tmp_path / "artifact"
    manifest = train_and_package(dataset, artifact_dir, seed=20260805)

    assert manifest["selected_model"] in {"logistic_regression", "random_forest"}
    assert manifest["test_metrics"]["f1"] >= manifest["acceptance_gates"]["minimum_test_f1"]
    assert manifest["test_metrics"]["recall"] >= manifest["acceptance_gates"]["minimum_test_recall"]
    assert (artifact_dir / "manifest.json").is_file()
    assert (artifact_dir / "evaluation.json").is_file()
    assert (artifact_dir / "model.joblib").is_file()

    prediction = predict_record(artifact_dir, SAMPLE_RECORD)
    assert prediction["prediction"] in {0, 1}
    assert 0.0 <= prediction["probability"] <= 1.0
    assert prediction["model_sha256"] == manifest["model_sha256"]


def test_tampered_model_is_rejected_before_deserialization(tmp_path: Path) -> None:
    dataset = write_dataset(tmp_path / "customers.csv", rows=700, seed=7)
    artifact_dir = tmp_path / "artifact"
    train_and_package(dataset, artifact_dir, seed=7)

    model_path = artifact_dir / "model.joblib"
    model_path.write_bytes(model_path.read_bytes() + b"tamper")

    with pytest.raises(ArtifactIntegrityError, match="checksum mismatch"):
        predict_record(artifact_dir, SAMPLE_RECORD)
