"""Training lifecycle, acceptance gates and artifact packaging."""

from __future__ import annotations

import os
import platform
import shutil
import uuid
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split

from .constants import (
    ARTIFACT_SCHEMA_VERSION,
    DEFAULT_SEED,
    FEATURE_COLUMNS,
    ID_COLUMN,
    MIN_TEST_F1,
    MIN_TEST_RECALL,
    TARGET_COLUMN,
)
from .errors import TrainingGateError
from .io_utils import sha256_file, write_json_atomic
from .modeling import evaluate_at_threshold, fit_and_evaluate_candidates, select_candidate
from .validation import load_dataset, validate_dataframe


def _split_dataset(frame: pd.DataFrame, seed: int) -> tuple[pd.DataFrame, ...]:
    features = frame[FEATURE_COLUMNS].copy()
    target = frame[TARGET_COLUMN].astype(int).copy()

    x_train, x_remaining, y_train, y_remaining = train_test_split(
        features,
        target,
        test_size=0.40,
        random_state=seed,
        stratify=target,
    )
    x_validation, x_test, y_validation, y_test = train_test_split(
        x_remaining,
        y_remaining,
        test_size=0.50,
        random_state=seed + 1,
        stratify=y_remaining,
    )
    return x_train, x_validation, x_test, y_train, y_validation, y_test


def _library_versions() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scikit_learn": sklearn.__version__,
        "joblib": joblib.__version__,
    }


def train_and_package(
    dataset_path: Path,
    output_dir: Path,
    seed: int = DEFAULT_SEED,
    overwrite: bool = False,
) -> dict[str, Any]:
    frame = load_dataset(dataset_path)
    validation_report = validate_dataframe(frame)
    dataset_sha256 = sha256_file(dataset_path)

    if output_dir.exists() and not overwrite:
        raise TrainingGateError(
            f"artifact directory already exists: {output_dir}; use --overwrite for an intentional replacement"
        )

    x_train, x_validation, x_test, y_train, y_validation, y_test = _split_dataset(
        frame, seed
    )
    evaluations = fit_and_evaluate_candidates(
        x_train, y_train, x_validation, y_validation, seed
    )
    selected = select_candidate(evaluations)
    baseline = next(item for item in evaluations if item.name == "dummy_most_frequent")
    test_metrics = evaluate_at_threshold(
        selected.pipeline, x_test, y_test, selected.threshold
    )

    gate_failures: list[str] = []
    if test_metrics["f1"] < MIN_TEST_F1:
        gate_failures.append(
            f"test f1 {test_metrics['f1']:.3f} is below {MIN_TEST_F1:.3f}"
        )
    if test_metrics["recall"] < MIN_TEST_RECALL:
        gate_failures.append(
            f"test recall {test_metrics['recall']:.3f} is below {MIN_TEST_RECALL:.3f}"
        )
    if selected.metrics["f1"] <= baseline.metrics["f1"]:
        gate_failures.append("selected validation f1 does not exceed the dummy baseline")
    if selected.threshold_status != "recall_gate_satisfied":
        gate_failures.append("selected model could not satisfy the validation recall gate")
    if gate_failures:
        raise TrainingGateError("; ".join(gate_failures))

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary_dir = output_dir.parent / f".{output_dir.name}.tmp-{uuid.uuid4().hex}"
    temporary_dir.mkdir(parents=False, exist_ok=False)

    try:
        model_path = temporary_dir / "model.joblib"
        joblib.dump(selected.pipeline, model_path, compress=3)
        model_sha256 = sha256_file(model_path)

        experiment_table = [
            {
                "name": item.name,
                "threshold": round(item.threshold, 6),
                "threshold_status": item.threshold_status,
                "validation_metrics": item.metrics,
            }
            for item in evaluations
        ]

        manifest: dict[str, Any] = {
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "artifact_type": "trusted-local-scikit-learn-pipeline",
            "model_file": model_path.name,
            "model_sha256": model_sha256,
            "dataset_path_at_training": str(dataset_path),
            "dataset_sha256": dataset_sha256,
            "dataset_rows": int(len(frame)),
            "dataset_validation": validation_report,
            "feature_columns": FEATURE_COLUMNS,
            "target_column": TARGET_COLUMN,
            "excluded_identity_column": ID_COLUMN,
            "seed": seed,
            "split_rows": {
                "train": int(len(x_train)),
                "validation": int(len(x_validation)),
                "test": int(len(x_test)),
            },
            "selected_model": selected.name,
            "decision_threshold": round(selected.threshold, 6),
            "threshold_status": selected.threshold_status,
            "validation_metrics": selected.metrics,
            "test_metrics": test_metrics,
            "experiments": experiment_table,
            "acceptance_gates": {
                "minimum_test_f1": MIN_TEST_F1,
                "minimum_test_recall": MIN_TEST_RECALL,
                "selected_f1_must_exceed_dummy": True,
            },
            "library_versions": _library_versions(),
            "source_revision": os.environ.get("GITHUB_SHA", "unavailable"),
            "security_boundary": {
                "load_only_from_trusted_source": True,
                "checksum_verification_required": True,
                "exact_library_version_match_required": True,
            },
        }
        write_json_atomic(temporary_dir / "manifest.json", manifest)
        write_json_atomic(
            temporary_dir / "evaluation.json",
            {
                "selected_model": selected.name,
                "validation_metrics": selected.metrics,
                "test_metrics": test_metrics,
                "experiments": experiment_table,
            },
        )

        if output_dir.exists():
            shutil.rmtree(output_dir)
        temporary_dir.replace(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(temporary_dir, ignore_errors=True)
        raise
