"""Checksum-verified local inference with a strict feature contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn

from .constants import ARTIFACT_SCHEMA_VERSION, FEATURE_COLUMNS
from .errors import ArtifactIntegrityError, InferenceInputError
from .io_utils import read_json_object, sha256_file


def _runtime_versions() -> dict[str, str]:
    return {
        "python": __import__("platform").python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scikit_learn": sklearn.__version__,
        "joblib": joblib.__version__,
    }


def load_artifact(artifact_dir: Path) -> tuple[Any, dict[str, Any]]:
    manifest_path = artifact_dir / "manifest.json"
    if not manifest_path.is_file():
        raise ArtifactIntegrityError(f"manifest does not exist: {manifest_path}")
    manifest = read_json_object(manifest_path)

    if manifest.get("schema_version") != ARTIFACT_SCHEMA_VERSION:
        raise ArtifactIntegrityError(
            f"unsupported manifest schema: {manifest.get('schema_version')}"
        )
    if manifest.get("artifact_type") != "trusted-local-scikit-learn-pipeline":
        raise ArtifactIntegrityError(f"unsupported artifact type: {manifest.get('artifact_type')}")
    if manifest.get("feature_columns") != FEATURE_COLUMNS:
        raise ArtifactIntegrityError("manifest feature contract does not match this runtime")

    model_path = artifact_dir / str(manifest.get("model_file", ""))
    if not model_path.is_file():
        raise ArtifactIntegrityError(f"model file does not exist: {model_path}")

    actual_sha = sha256_file(model_path)
    expected_sha = manifest.get("model_sha256")
    if actual_sha != expected_sha:
        raise ArtifactIntegrityError(
            f"model checksum mismatch: expected {expected_sha}, got {actual_sha}"
        )

    expected_versions = manifest.get("library_versions")
    runtime_versions = _runtime_versions()
    if not isinstance(expected_versions, dict):
        raise ArtifactIntegrityError("manifest library_versions must be an object")
    mismatches = {
        name: {"artifact": expected_versions.get(name), "runtime": runtime_versions.get(name)}
        for name in runtime_versions
        if expected_versions.get(name) != runtime_versions.get(name)
    }
    if mismatches:
        raise ArtifactIntegrityError(
            f"runtime library versions differ from the training environment: {mismatches}"
        )

    # joblib uses pickle semantics. Checksum and provenance checks happen before loading,
    # but the artifact must still originate from a trusted source.
    model = joblib.load(model_path)
    return model, manifest


def validate_inference_record(record: dict[str, Any]) -> None:
    missing = sorted(set(FEATURE_COLUMNS) - set(record))
    extra = sorted(set(record) - set(FEATURE_COLUMNS))
    if missing or extra:
        raise InferenceInputError(
            f"inference feature contract mismatch; missing={missing}, extra={extra}"
        )


def predict_record(artifact_dir: Path, record: dict[str, Any]) -> dict[str, Any]:
    validate_inference_record(record)
    model, manifest = load_artifact(artifact_dir)
    frame = pd.DataFrame([record], columns=FEATURE_COLUMNS)
    probability = float(model.predict_proba(frame)[:, 1][0])
    threshold = float(manifest["decision_threshold"])
    prediction = int(probability >= threshold)
    return {
        "prediction": prediction,
        "probability": round(probability, 6),
        "decision_threshold": round(threshold, 6),
        "selected_model": manifest["selected_model"],
        "model_sha256": manifest["model_sha256"],
        "dataset_sha256": manifest["dataset_sha256"],
    }
