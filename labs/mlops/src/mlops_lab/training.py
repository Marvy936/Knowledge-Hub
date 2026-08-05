"""MLflow experiment tracking, model registration and candidate requests."""

from __future__ import annotations

import importlib.metadata
import os
from pathlib import Path
from typing import Any

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.models import infer_signature
from sklearn.model_selection import train_test_split

from ml_lab.constants import FEATURE_COLUMNS, TARGET_COLUMN
from ml_lab.io_utils import sha256_file
from ml_lab.modeling import (
    evaluate_at_threshold,
    fit_and_evaluate_candidates,
    select_candidate,
)
from ml_lab.validation import load_dataset, validate_dataframe

from .constants import (
    CANDIDATE_ALIAS,
    MIN_TEST_F1,
    MIN_TEST_RECALL,
    PROMOTION_SCHEMA_VERSION,
    REGISTERED_MODEL_NAME,
)
from .errors import PromotionRefused
from .io_utils import write_json_atomic
from .workspace import Workspace, configure_workspace


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


def _package_versions() -> dict[str, str]:
    names = ["mlflow", "numpy", "pandas", "scikit-learn", "joblib", "skops"]
    return {name: importlib.metadata.version(name) for name in names}


def _champion_version(client: Any) -> int | None:
    try:
        return int(
            client.get_model_version_by_alias(
                REGISTERED_MODEL_NAME, "champion"
            ).version
        )
    except Exception:
        return None


def _registered_version(info: Any, client: Any, run_id: str) -> int:
    direct = getattr(info, "registered_model_version", None)
    if direct is not None:
        return int(direct)
    matches = [
        version
        for version in client.search_model_versions(
            f"name = '{REGISTERED_MODEL_NAME}'"
        )
        if getattr(version, "run_id", None) == run_id
    ]
    if len(matches) != 1:
        raise PromotionRefused(
            f"cannot resolve one registered version for run {run_id}: {len(matches)} matches"
        )
    return int(matches[0].version)


def train_track_and_request(
    workspace_root: Path,
    dataset_path: Path,
    *,
    generation: str,
    seed: int,
    request_name: str,
) -> dict[str, Any]:
    workspace, client = configure_workspace(workspace_root)
    frame = load_dataset(dataset_path)
    dataset_validation = validate_dataframe(frame)
    dataset_sha256 = sha256_file(dataset_path)
    x_train, x_validation, x_test, y_train, y_validation, y_test = _split_dataset(
        frame, seed
    )

    evaluations = fit_and_evaluate_candidates(
        x_train,
        y_train,
        x_validation,
        y_validation,
        seed,
    )
    selected = select_candidate(evaluations)
    versions: dict[str, int] = {}
    tracked_runs: list[dict[str, Any]] = []
    package_versions = _package_versions()

    for evaluation in evaluations:
        test_metrics = evaluate_at_threshold(
            evaluation.pipeline,
            x_test,
            y_test,
            evaluation.threshold,
        )
        with mlflow.start_run(
            experiment_id=workspace.experiment_id,
            run_name=f"{generation}-{evaluation.name}",
            tags={
                "knowledge_hub.generation": generation,
                "knowledge_hub.candidate": evaluation.name,
                "knowledge_hub.dataset_sha256": dataset_sha256,
                "knowledge_hub.source_revision": os.environ.get(
                    "GITHUB_SHA", "unavailable"
                ),
            },
        ) as run:
            mlflow.log_params(
                {
                    "seed": seed,
                    "candidate": evaluation.name,
                    "decision_threshold": evaluation.threshold,
                    "dataset_rows": len(frame),
                    "train_rows": len(x_train),
                    "validation_rows": len(x_validation),
                    "test_rows": len(x_test),
                }
            )
            mlflow.log_metrics(
                {
                    "validation_f1": evaluation.metrics["f1"],
                    "validation_recall": evaluation.metrics["recall"],
                    "validation_precision": evaluation.metrics["precision"],
                    "validation_roc_auc": evaluation.metrics["roc_auc"],
                    "test_f1": test_metrics["f1"],
                    "test_recall": test_metrics["recall"],
                    "test_precision": test_metrics["precision"],
                    "test_roc_auc": test_metrics["roc_auc"],
                }
            )
            mlflow.log_dict(
                {
                    "dataset_path": str(dataset_path),
                    "dataset_sha256": dataset_sha256,
                    "validation": dataset_validation,
                    "split_rows": {
                        "train": len(x_train),
                        "validation": len(x_validation),
                        "test": len(x_test),
                    },
                },
                "lineage/dataset.json",
            )
            mlflow.log_dict(
                {
                    "candidate": evaluation.name,
                    "threshold_status": evaluation.threshold_status,
                    "validation_metrics": evaluation.metrics,
                    "test_metrics": test_metrics,
                },
                "evaluation/metrics.json",
            )

            registered_version: int | None = None
            model_id: str | None = None
            if evaluation.name != "dummy_most_frequent":
                input_example = x_train.head(3).copy()
                probability_example = evaluation.pipeline.predict_proba(input_example)
                signature = infer_signature(input_example, probability_example)
                info = mlflow.sklearn.log_model(
                    sk_model=evaluation.pipeline,
                    name="model",
                    input_example=input_example,
                    signature=signature,
                    serialization_format="skops",
                    pyfunc_predict_fn="predict_proba",
                    registered_model_name=REGISTERED_MODEL_NAME,
                    await_registration_for=60,
                    pip_requirements=[
                        f"mlflow=={package_versions['mlflow']}",
                        f"numpy=={package_versions['numpy']}",
                        f"pandas=={package_versions['pandas']}",
                        f"scikit-learn=={package_versions['scikit-learn']}",
                        f"joblib=={package_versions['joblib']}",
                        f"skops=={package_versions['skops']}",
                    ],
                    metadata={
                        "dataset_sha256": dataset_sha256,
                        "generation": generation,
                        "candidate": evaluation.name,
                    },
                )
                registered_version = _registered_version(info, client, run.info.run_id)
                model_id = getattr(info, "model_id", None)
                versions[evaluation.name] = registered_version
                for key, value in {
                    "candidate": evaluation.name,
                    "generation": generation,
                    "dataset_sha256": dataset_sha256,
                    "decision_threshold": evaluation.threshold,
                    "validation_f1": evaluation.metrics["f1"],
                    "validation_recall": evaluation.metrics["recall"],
                    "test_f1": test_metrics["f1"],
                    "test_recall": test_metrics["recall"],
                    "source_revision": os.environ.get("GITHUB_SHA", "unavailable"),
                    "serialization": "skops",
                }.items():
                    client.set_model_version_tag(
                        REGISTERED_MODEL_NAME,
                        str(registered_version),
                        key,
                        str(value),
                    )

            tracked_runs.append(
                {
                    "candidate": evaluation.name,
                    "run_id": run.info.run_id,
                    "model_id": model_id,
                    "registered_version": registered_version,
                    "threshold": evaluation.threshold,
                    "threshold_status": evaluation.threshold_status,
                    "validation_metrics": evaluation.metrics,
                    "test_metrics": test_metrics,
                }
            )

    selected_run = next(
        item for item in tracked_runs if item["candidate"] == selected.name
    )
    gate_failures: list[str] = []
    if selected_run["test_metrics"]["f1"] < MIN_TEST_F1:
        gate_failures.append("selected test F1 is below the promotion gate")
    if selected_run["test_metrics"]["recall"] < MIN_TEST_RECALL:
        gate_failures.append("selected test recall is below the promotion gate")
    if selected.threshold_status != "recall_gate_satisfied":
        gate_failures.append("validation recall gate was not satisfied")
    if gate_failures:
        raise PromotionRefused("; ".join(gate_failures))

    candidate_version = versions[selected.name]
    client.set_model_version_tag(
        REGISTERED_MODEL_NAME, str(candidate_version), "promotion_gate", "passed"
    )
    client.set_registered_model_alias(
        REGISTERED_MODEL_NAME, CANDIDATE_ALIAS, str(candidate_version)
    )
    candidate_readback = client.get_model_version_by_alias(
        REGISTERED_MODEL_NAME, CANDIDATE_ALIAS
    )
    if int(candidate_readback.version) != candidate_version:
        raise PromotionRefused("candidate alias read-back does not match selected version")

    request = write_json_atomic(
        workspace.requests / request_name,
        {
            "schema_version": PROMOTION_SCHEMA_VERSION,
            "model_name": REGISTERED_MODEL_NAME,
            "generation": generation,
            "candidate_alias": CANDIDATE_ALIAS,
            "candidate_version": candidate_version,
            "candidate_run_id": selected_run["run_id"],
            "candidate_model_id": selected_run["model_id"],
            "candidate_name": selected.name,
            "previous_champion_version": _champion_version(client),
            "dataset_path": str(dataset_path.resolve()),
            "dataset_sha256": dataset_sha256,
            "source_revision": os.environ.get("GITHUB_SHA", "unavailable"),
            "decision_threshold": selected.threshold,
            "validation_metrics": selected.metrics,
            "test_metrics": selected_run["test_metrics"],
            "registered_versions": versions,
            "tracked_runs": tracked_runs,
            "resolved_packages": package_versions,
            "promotion_gate": "passed",
        },
    )
    return {
        "status": "candidate_ready",
        "workspace": str(workspace.root),
        "tracking_uri": workspace.tracking_uri,
        "candidate_version": candidate_version,
        "candidate_alias_readback": int(candidate_readback.version),
        "promotion_request": str(workspace.requests / request_name),
        "request": request,
    }
