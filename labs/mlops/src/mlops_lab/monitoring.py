"""Deterministic drift monitoring, retraining authority and canary evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import mlflow.pyfunc
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, recall_score

from ml_lab.constants import FEATURE_COLUMNS, TARGET_COLUMN
from ml_lab.data import generate_dataset
from ml_lab.io_utils import sha256_file
from ml_lab.validation import load_dataset, validate_dataframe

from .constants import (
    CANARY_PERCENT,
    CANARY_SCHEMA_VERSION,
    CANDIDATE_ALIAS,
    CHAMPION_ALIAS,
    DRIFT_PSI_THRESHOLD,
    DRIFT_SCHEMA_VERSION,
    MAX_CANARY_DISAGREEMENT,
    MAX_CANARY_F1_REGRESSION,
    MIN_TEST_RECALL,
    REGISTERED_MODEL_NAME,
)
from .errors import CanaryRefused, DriftNotActionable
from .io_utils import read_json_object, write_json_atomic
from .training import train_track_and_request
from .workspace import configure_workspace


def population_stability_index(
    baseline: pd.Series,
    current: pd.Series,
    *,
    bins: int = 10,
) -> float:
    baseline_numeric = pd.to_numeric(baseline, errors="coerce")
    current_numeric = pd.to_numeric(current, errors="coerce")
    fill = float(baseline_numeric.median())
    baseline_values = baseline_numeric.fillna(fill).to_numpy(dtype=float)
    current_values = current_numeric.fillna(fill).to_numpy(dtype=float)

    quantiles = np.linspace(0.0, 1.0, bins + 1)
    edges = np.unique(np.quantile(baseline_values, quantiles))
    if len(edges) < 3:
        return 0.0
    edges[0] = -np.inf
    edges[-1] = np.inf

    baseline_counts, _ = np.histogram(baseline_values, bins=edges)
    current_counts, _ = np.histogram(current_values, bins=edges)
    epsilon = 1e-6
    baseline_fraction = np.maximum(baseline_counts / baseline_counts.sum(), epsilon)
    current_fraction = np.maximum(current_counts / current_counts.sum(), epsilon)
    return float(
        np.sum(
            (current_fraction - baseline_fraction)
            * np.log(current_fraction / baseline_fraction)
        )
    )


def _probabilities(model: Any, features: pd.DataFrame) -> np.ndarray:
    values = np.asarray(model.predict(features), dtype=float)
    if values.ndim != 2 or values.shape[1] != 2:
        raise DriftNotActionable(
            f"expected binary predict_proba output with shape (n, 2), got {values.shape}"
        )
    return values[:, 1]


def _alias_version(client: Any, alias: str) -> int:
    try:
        return int(
            client.get_model_version_by_alias(REGISTERED_MODEL_NAME, alias).version
        )
    except Exception as exc:
        raise DriftNotActionable(f"required Registry alias does not exist: {alias}") from exc


def create_drift_report(
    workspace_root: Path,
    *,
    rows: int,
    seed: int,
) -> dict[str, Any]:
    workspace, client = configure_workspace(workspace_root)
    baseline_path = workspace.data / "baseline.csv"
    if not baseline_path.is_file():
        raise DriftNotActionable("baseline dataset does not exist; run bootstrap first")
    baseline = load_dataset(baseline_path)
    validate_dataframe(baseline)

    current = generate_dataset(rows=rows, seed=seed)
    current["days_since_last_login"] = (
        pd.to_numeric(current["days_since_last_login"], errors="coerce") + 14
    ).clip(0, 180)
    current["login_days_30d"] = (
        pd.to_numeric(current["login_days_30d"], errors="coerce") - 6
    ).clip(0, 30)
    current.loc[current.index % 4 == 0, "contract_type"] = "monthly"
    current_path = workspace.data / "current.csv"
    current.to_csv(current_path, index=False, lineterminator="\n", float_format="%.6f")
    current = load_dataset(current_path)
    validation = validate_dataframe(current)

    psi = {
        column: round(
            population_stability_index(baseline[column], current[column]), 6
        )
        for column in (
            "tenure_months",
            "monthly_spend_eur",
            "support_tickets_90d",
            "login_days_30d",
            "days_since_last_login",
        )
    }
    max_psi = max(psi.values())
    triggered = max_psi >= DRIFT_PSI_THRESHOLD

    champion_version = _alias_version(client, CHAMPION_ALIAS)
    champion_info = client.get_model_version(
        REGISTERED_MODEL_NAME, str(champion_version)
    )
    threshold = float(champion_info.tags["decision_threshold"])
    model = mlflow.pyfunc.load_model(
        f"models:/{REGISTERED_MODEL_NAME}@{CHAMPION_ALIAS}"
    )
    probabilities = _probabilities(model, current[FEATURE_COLUMNS])
    predictions = (probabilities >= threshold).astype(int)

    report_path = workspace.reports / "drift.json"
    report = write_json_atomic(
        report_path,
        {
            "schema_version": DRIFT_SCHEMA_VERSION,
            "status": "actionable" if triggered else "observed",
            "triggered": triggered,
            "threshold": DRIFT_PSI_THRESHOLD,
            "psi": psi,
            "max_psi": round(max_psi, 6),
            "baseline_dataset_path": str(baseline_path.resolve()),
            "baseline_dataset_sha256": sha256_file(baseline_path),
            "current_dataset_path": str(current_path.resolve()),
            "current_dataset_sha256": sha256_file(current_path),
            "current_validation": validation,
            "champion_version": champion_version,
            "champion_threshold": threshold,
            "current_prediction_positive_fraction": round(float(predictions.mean()), 6),
            "current_probability_mean": round(float(probabilities.mean()), 6),
        },
    )
    return {"status": "drift_reported", "report": str(report_path), "evidence": report}


def retrain_from_drift(
    workspace_root: Path,
    drift_report_path: Path,
    *,
    seed: int,
) -> dict[str, Any]:
    report = read_json_object(drift_report_path)
    if report.get("schema_version") != DRIFT_SCHEMA_VERSION:
        raise DriftNotActionable("unsupported drift report schema")
    if report.get("triggered") is not True:
        raise DriftNotActionable("drift report does not authorize retraining")
    dataset_path = Path(report["current_dataset_path"])
    if sha256_file(dataset_path) != report.get("current_dataset_sha256"):
        raise DriftNotActionable("current dataset changed after drift evidence")

    result = train_track_and_request(
        workspace_root,
        dataset_path,
        generation=f"retrain-{report['current_dataset_sha256'][:12]}",
        seed=seed,
        request_name="retrain-promotion.json",
    )
    result["drift_report_sha256"] = report["evidence_sha256"]
    return result


def evaluate_canary(
    workspace_root: Path,
    request_path: Path,
    drift_report_path: Path,
) -> dict[str, Any]:
    workspace, client = configure_workspace(workspace_root)
    request = read_json_object(request_path)
    drift = read_json_object(drift_report_path)
    if drift.get("triggered") is not True:
        raise CanaryRefused("canary requires an actionable drift report")
    if request.get("dataset_sha256") != drift.get("current_dataset_sha256"):
        raise CanaryRefused("candidate and canary traffic use different dataset generations")

    champion_version = _alias_version(client, CHAMPION_ALIAS)
    candidate_version = _alias_version(client, CANDIDATE_ALIAS)
    if candidate_version != int(request["candidate_version"]):
        raise CanaryRefused("candidate alias differs from promotion request")
    if request.get("previous_champion_version") != champion_version:
        raise CanaryRefused("promotion request was created for a different champion")

    dataset_path = Path(drift["current_dataset_path"])
    frame = load_dataset(dataset_path)
    validate_dataframe(frame)
    features = frame[FEATURE_COLUMNS]
    target = frame[TARGET_COLUMN].astype(int).to_numpy()

    champion_info = client.get_model_version(
        REGISTERED_MODEL_NAME, str(champion_version)
    )
    candidate_info = client.get_model_version(
        REGISTERED_MODEL_NAME, str(candidate_version)
    )
    champion_threshold = float(champion_info.tags["decision_threshold"])
    candidate_threshold = float(request["decision_threshold"])

    champion_model = mlflow.pyfunc.load_model(
        f"models:/{REGISTERED_MODEL_NAME}/{champion_version}"
    )
    candidate_model = mlflow.pyfunc.load_model(
        f"models:/{REGISTERED_MODEL_NAME}/{candidate_version}"
    )
    champion_probabilities = _probabilities(champion_model, features)
    candidate_probabilities = _probabilities(candidate_model, features)
    champion_predictions = (champion_probabilities >= champion_threshold).astype(int)
    candidate_predictions = (candidate_probabilities >= candidate_threshold).astype(int)

    canary_mask = np.arange(len(frame)) % (100 // CANARY_PERCENT) == 0
    route_counts = {
        "champion": int((~canary_mask).sum()),
        "candidate": int(canary_mask.sum()),
    }
    disagreement = float(np.mean(champion_predictions != candidate_predictions))
    champion_current_f1 = float(f1_score(target, champion_predictions, zero_division=0))
    candidate_current_f1 = float(f1_score(target, candidate_predictions, zero_division=0))
    candidate_current_recall = float(
        recall_score(target, candidate_predictions, zero_division=0)
    )

    champion_registered_f1 = float(champion_info.tags["test_f1"])
    candidate_heldout_f1 = float(request["test_metrics"]["f1"])
    candidate_heldout_recall = float(request["test_metrics"]["recall"])
    failures: list[str] = []
    if candidate_heldout_f1 < champion_registered_f1 - MAX_CANARY_F1_REGRESSION:
        failures.append("candidate held-out F1 regresses beyond policy")
    if candidate_heldout_recall < MIN_TEST_RECALL:
        failures.append("candidate held-out recall is below policy")
    if disagreement > MAX_CANARY_DISAGREEMENT:
        failures.append("candidate/champion disagreement exceeds policy")

    status = "passed" if not failures else "failed"
    report_path = workspace.reports / "canary.json"
    report = write_json_atomic(
        report_path,
        {
            "schema_version": CANARY_SCHEMA_VERSION,
            "status": status,
            "failures": failures,
            "model_name": REGISTERED_MODEL_NAME,
            "champion_version": champion_version,
            "candidate_version": candidate_version,
            "dataset_path": str(dataset_path.resolve()),
            "dataset_sha256": sha256_file(dataset_path),
            "route_percent": CANARY_PERCENT,
            "route_counts": route_counts,
            "disagreement_fraction": round(disagreement, 6),
            "champion_registered_test_f1": champion_registered_f1,
            "candidate_heldout_test_f1": candidate_heldout_f1,
            "candidate_heldout_test_recall": candidate_heldout_recall,
            "champion_current_f1_observation": round(champion_current_f1, 6),
            "candidate_current_f1_observation": round(candidate_current_f1, 6),
            "candidate_current_recall_observation": round(candidate_current_recall, 6),
            "promotion_request_sha256": request["evidence_sha256"],
            "drift_report_sha256": drift["evidence_sha256"],
            "policy": {
                "maximum_f1_regression": MAX_CANARY_F1_REGRESSION,
                "minimum_candidate_recall": MIN_TEST_RECALL,
                "maximum_disagreement": MAX_CANARY_DISAGREEMENT,
            },
        },
    )
    if failures:
        raise CanaryRefused("; ".join(failures))
    return {"status": "canary_passed", "report": str(report_path), "evidence": report}
