from __future__ import annotations

import bisect
import math
from copy import deepcopy
from typing import Any, Iterable, Mapping

from .contracts import ContractError, canonical_json_bytes, sha256_bytes

MONITORING_SCHEMA_VERSION = 1
NUMERIC_FEATURES = (
    "tenure_months",
    "monthly_spend_eur",
    "support_tickets_90d",
    "login_days_30d",
    "days_since_last_login",
)
CATEGORICAL_FEATURES = ("contract_type", "region", "auto_pay")
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
EPSILON = 1e-6


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value.strip()


def _require_sha256(value: Any, field: str) -> str:
    text = _require_nonempty_string(value, field)
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise ContractError(f"{field} must be a lowercase SHA-256 digest")
    return text


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{field} must be numeric")
    resolved = float(value)
    if not math.isfinite(resolved):
        raise ContractError(f"{field} must be finite")
    return resolved


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((len(ordered) - 1) * percentile)))
    return round(ordered[index], 6)


def _validate_event(event: Mapping[str, Any], index: int) -> None:
    expected = {"record", "success", "latency_ms", "prediction", "probability"}
    if set(event) != expected:
        raise ContractError(f"monitoring event {index} keys mismatch")
    record = event.get("record")
    if not isinstance(record, dict) or set(record) != set(ALL_FEATURES):
        raise ContractError(f"monitoring event {index} has invalid record fields")
    for feature in NUMERIC_FEATURES:
        _finite_number(record[feature], f"event[{index}].record.{feature}")
    for feature in CATEGORICAL_FEATURES:
        _require_nonempty_string(record[feature], f"event[{index}].record.{feature}")
    if not isinstance(event.get("success"), bool):
        raise ContractError(f"monitoring event {index} success must be boolean")
    latency = _finite_number(event.get("latency_ms"), f"event[{index}].latency_ms")
    if latency < 0:
        raise ContractError(f"monitoring event {index} latency must be non-negative")
    if event["success"]:
        if event.get("prediction") not in (0, 1):
            raise ContractError(f"monitoring event {index} prediction must be binary")
        probability = _finite_number(
            event.get("probability"), f"event[{index}].probability"
        )
        if not 0.0 <= probability <= 1.0:
            raise ContractError(f"monitoring event {index} probability is out of range")
    elif event.get("prediction") is not None or event.get("probability") is not None:
        raise ContractError(
            f"monitoring event {index} failed outcome must not contain prediction"
        )


def _quantile_boundaries(values: list[float], bin_count: int) -> list[float]:
    if bin_count < 2:
        raise ContractError("numeric bin_count must be at least 2")
    ordered = sorted(values)
    boundaries: list[float] = []
    for index in range(1, bin_count):
        position = min(len(ordered) - 1, int(index * len(ordered) / bin_count))
        boundary = ordered[position]
        if not boundaries or boundary > boundaries[-1]:
            boundaries.append(boundary)
    return boundaries


def _histogram(values: list[float], boundaries: list[float]) -> list[float]:
    counts = [0] * (len(boundaries) + 1)
    for value in values:
        counts[bisect.bisect_right(boundaries, value)] += 1
    total = len(values)
    return [0.0] * len(counts) if total == 0 else [count / total for count in counts]


def _numeric_profile(
    values: list[float], *, boundaries: list[float] | None, bin_count: int
) -> dict[str, Any]:
    resolved_boundaries = (
        _quantile_boundaries(values, bin_count) if boundaries is None else boundaries
    )
    return {
        "count": len(values),
        "mean": None if not values else round(sum(values) / len(values), 6),
        "minimum": None if not values else round(min(values), 6),
        "maximum": None if not values else round(max(values), 6),
        "boundaries": [round(value, 6) for value in resolved_boundaries],
        "bin_proportions": [
            round(value, 9) for value in _histogram(values, resolved_boundaries)
        ],
    }


def _categorical_profile(
    values: list[str], *, categories: list[str] | None
) -> dict[str, Any]:
    resolved_categories = sorted(set(values)) if categories is None else categories
    counts = {category: 0 for category in resolved_categories}
    other = 0
    for value in values:
        if value in counts:
            counts[value] += 1
        else:
            other += 1
    total = len(values)
    proportions = {
        category: 0.0 if total == 0 else round(count / total, 9)
        for category, count in counts.items()
    }
    return {
        "count": total,
        "categories": resolved_categories,
        "proportions": proportions,
        "other_proportion": 0.0 if total == 0 else round(other / total, 9),
    }


def _profile_events(
    events: list[Mapping[str, Any]],
    *,
    baseline: Mapping[str, Any] | None,
    numeric_bin_count: int,
) -> dict[str, Any]:
    successful = [event for event in events if event["success"]]
    numeric: dict[str, Any] = {}
    categorical: dict[str, Any] = {}
    for feature in NUMERIC_FEATURES:
        values = [float(event["record"][feature]) for event in successful]
        boundaries = (
            None
            if baseline is None
            else list(baseline["numeric_features"][feature]["boundaries"])
        )
        numeric[feature] = _numeric_profile(
            values, boundaries=boundaries, bin_count=numeric_bin_count
        )
    for feature in CATEGORICAL_FEATURES:
        values = [str(event["record"][feature]) for event in successful]
        categories = (
            None
            if baseline is None
            else list(baseline["categorical_features"][feature]["categories"])
        )
        categorical[feature] = _categorical_profile(values, categories=categories)
    latencies = [float(event["latency_ms"]) for event in events]
    predictions = [int(event["prediction"]) for event in successful]
    probabilities = [float(event["probability"]) for event in successful]
    return {
        "total_events": len(events),
        "successful_events": len(successful),
        "failed_events": len(events) - len(successful),
        "error_rate": 0.0
        if not events
        else round((len(events) - len(successful)) / len(events), 9),
        "no_data": len(events) == 0,
        "latency_ms": {
            "minimum": None if not latencies else round(min(latencies), 6),
            "average": None
            if not latencies
            else round(sum(latencies) / len(latencies), 6),
            "p95": _percentile(latencies, 0.95),
            "maximum": None if not latencies else round(max(latencies), 6),
        },
        "prediction": {
            "positive_rate": None
            if not predictions
            else round(sum(predictions) / len(predictions), 9),
            "probability_mean": None
            if not probabilities
            else round(sum(probabilities) / len(probabilities), 9),
        },
        "numeric_features": numeric,
        "categorical_features": categorical,
    }


def build_baseline_profile(
    *,
    events: Iterable[Mapping[str, Any]],
    profile_name: str,
    generation: str,
    numeric_bin_count: int = 10,
) -> dict[str, Any]:
    resolved_events = list(events)
    for index, event in enumerate(resolved_events):
        _validate_event(event, index)
    if not resolved_events:
        raise ContractError("baseline profile requires at least one event")
    if any(not event["success"] for event in resolved_events):
        raise ContractError("baseline profile requires successful events only")
    payload = {
        "schema_version": MONITORING_SCHEMA_VERSION,
        "profile_name": _require_nonempty_string(profile_name, "profile_name"),
        "generation": _require_nonempty_string(generation, "generation"),
        "numeric_bin_count": numeric_bin_count,
        **_profile_events(
            resolved_events, baseline=None, numeric_bin_count=numeric_bin_count
        ),
    }
    return {**payload, "baseline_profile_id": sha256_bytes(canonical_json_bytes(payload))}


def build_monitoring_window(
    *,
    events: Iterable[Mapping[str, Any]],
    baseline: Mapping[str, Any],
    deployment_id: str,
) -> dict[str, Any]:
    validate_baseline_profile(baseline)
    resolved_events = list(events)
    for index, event in enumerate(resolved_events):
        _validate_event(event, index)
    payload = {
        "schema_version": MONITORING_SCHEMA_VERSION,
        "baseline_profile_id": baseline["baseline_profile_id"],
        "deployment_id": _require_sha256(deployment_id, "deployment_id"),
        **_profile_events(
            resolved_events,
            baseline=baseline,
            numeric_bin_count=baseline["numeric_bin_count"],
        ),
    }
    return {**payload, "monitoring_window_id": sha256_bytes(canonical_json_bytes(payload))}


def _validate_profile_identity(value: Mapping[str, Any], id_field: str) -> None:
    identifier = _require_sha256(value.get(id_field), id_field)
    payload = {key: item for key, item in value.items() if key != id_field}
    if sha256_bytes(canonical_json_bytes(payload)) != identifier:
        raise ContractError(f"{id_field} does not match canonical payload")


def validate_baseline_profile(value: Mapping[str, Any]) -> None:
    if value.get("schema_version") != MONITORING_SCHEMA_VERSION:
        raise ContractError("baseline schema_version must equal 1")
    _require_nonempty_string(value.get("profile_name"), "baseline.profile_name")
    _require_nonempty_string(value.get("generation"), "baseline.generation")
    if not isinstance(value.get("numeric_bin_count"), int):
        raise ContractError("baseline numeric_bin_count must be an integer")
    if value.get("total_events", 0) < 1 or value.get("failed_events") != 0:
        raise ContractError("baseline must contain successful events only")
    if not isinstance(value.get("numeric_features"), dict) or not isinstance(
        value.get("categorical_features"), dict
    ):
        raise ContractError("baseline feature profiles must be objects")
    _validate_profile_identity(value, "baseline_profile_id")


def validate_monitoring_window(value: Mapping[str, Any]) -> None:
    if value.get("schema_version") != MONITORING_SCHEMA_VERSION:
        raise ContractError("monitoring window schema_version must equal 1")
    _require_sha256(value.get("baseline_profile_id"), "window.baseline_profile_id")
    _require_sha256(value.get("deployment_id"), "window.deployment_id")
    total = value.get("total_events")
    success = value.get("successful_events")
    failed = value.get("failed_events")
    if not all(isinstance(item, int) and not isinstance(item, bool) for item in (total, success, failed)):
        raise ContractError("monitoring window event counts must be integers")
    if success + failed != total:
        raise ContractError("monitoring window event counts are inconsistent")
    if value.get("no_data") is not (total == 0):
        raise ContractError("monitoring window no_data state is inconsistent")
    _validate_profile_identity(value, "monitoring_window_id")


def _psi(expected: list[float], actual: list[float]) -> float:
    if len(expected) != len(actual):
        raise ContractError("numeric profile bin counts do not match")
    return sum(
        (observed + EPSILON - reference - EPSILON)
        * math.log((observed + EPSILON) / (reference + EPSILON))
        for reference, observed in zip(expected, actual, strict=True)
    )


def _tvd(reference: Mapping[str, float], actual: Mapping[str, float], other: float) -> float:
    return 0.5 * (
        sum(abs(float(reference[key]) - float(actual.get(key, 0.0))) for key in reference)
        + abs(other)
    )


def compare_drift(
    *,
    baseline: Mapping[str, Any],
    window: Mapping[str, Any],
    minimum_successful_events: int,
    numeric_psi_threshold: float,
    categorical_tvd_threshold: float,
    prediction_rate_delta_threshold: float,
    maximum_error_rate: float,
) -> dict[str, Any]:
    validate_baseline_profile(baseline)
    validate_monitoring_window(window)
    if window["baseline_profile_id"] != baseline["baseline_profile_id"]:
        raise ContractError("monitoring window belongs to another baseline")
    if minimum_successful_events < 1:
        raise ContractError("minimum_successful_events must be positive")
    thresholds = {
        "numeric_psi": _finite_number(numeric_psi_threshold, "numeric_psi_threshold"),
        "categorical_tvd": _finite_number(
            categorical_tvd_threshold, "categorical_tvd_threshold"
        ),
        "prediction_rate_delta": _finite_number(
            prediction_rate_delta_threshold, "prediction_rate_delta_threshold"
        ),
        "maximum_error_rate": _finite_number(maximum_error_rate, "maximum_error_rate"),
    }
    if any(not 0.0 <= value <= 1.0 for key, value in thresholds.items() if key != "numeric_psi"):
        raise ContractError("drift rate thresholds must be between 0 and 1")
    if thresholds["numeric_psi"] < 0:
        raise ContractError("numeric PSI threshold must be non-negative")

    numeric_scores = {
        feature: round(
            _psi(
                baseline["numeric_features"][feature]["bin_proportions"],
                window["numeric_features"][feature]["bin_proportions"],
            ),
            9,
        )
        for feature in NUMERIC_FEATURES
    }
    categorical_scores = {
        feature: round(
            _tvd(
                baseline["categorical_features"][feature]["proportions"],
                window["categorical_features"][feature]["proportions"],
                float(window["categorical_features"][feature]["other_proportion"]),
            ),
            9,
        )
        for feature in CATEGORICAL_FEATURES
    }
    baseline_rate = baseline["prediction"]["positive_rate"]
    window_rate = window["prediction"]["positive_rate"]
    prediction_delta = (
        None
        if baseline_rate is None or window_rate is None
        else round(abs(float(window_rate) - float(baseline_rate)), 9)
    )

    exceeded_numeric = sorted(
        feature
        for feature, score in numeric_scores.items()
        if score > thresholds["numeric_psi"]
    )
    exceeded_categorical = sorted(
        feature
        for feature, score in categorical_scores.items()
        if score > thresholds["categorical_tvd"]
    )
    if window["no_data"]:
        status = "no_data"
    elif window["successful_events"] < minimum_successful_events:
        status = "insufficient_evidence"
    elif window["error_rate"] > thresholds["maximum_error_rate"]:
        status = "operational_failure"
    elif (
        exceeded_numeric
        or exceeded_categorical
        or (
            prediction_delta is not None
            and prediction_delta > thresholds["prediction_rate_delta"]
        )
    ):
        status = "drift_detected"
    else:
        status = "stable"

    payload = {
        "schema_version": MONITORING_SCHEMA_VERSION,
        "baseline_profile_id": baseline["baseline_profile_id"],
        "monitoring_window_id": window["monitoring_window_id"],
        "deployment_id": window["deployment_id"],
        "minimum_successful_events": minimum_successful_events,
        "thresholds": thresholds,
        "numeric_psi": numeric_scores,
        "categorical_tvd": categorical_scores,
        "prediction_rate_delta": prediction_delta,
        "exceeded_numeric_features": exceeded_numeric,
        "exceeded_categorical_features": exceeded_categorical,
        "observed_error_rate": window["error_rate"],
        "status": status,
    }
    return {**payload, "drift_report_id": sha256_bytes(canonical_json_bytes(payload))}


def inject_drift(
    records: Iterable[Mapping[str, Any]], *, mode: str
) -> list[dict[str, Any]]:
    resolved_mode = _require_nonempty_string(mode, "drift mode")
    if resolved_mode not in {"control", "shift"}:
        raise ContractError("drift mode must be control or shift")
    output = [deepcopy(dict(record)) for record in records]
    if resolved_mode == "control":
        return output
    for record in output:
        record["monthly_spend_eur"] = min(
            250.0, float(record["monthly_spend_eur"]) + 80.0
        )
        record["support_tickets_90d"] = min(
            30, int(record["support_tickets_90d"]) + 6
        )
        record["login_days_30d"] = max(0, int(record["login_days_30d"]) - 8)
        record["days_since_last_login"] = min(
            180, int(record["days_since_last_login"]) + 40
        )
        record["contract_type"] = "monthly"
        record["auto_pay"] = "no"
    return output


def build_retraining_proposal(
    *,
    drift_report: Mapping[str, Any],
    model_sha256: str,
    policy_generation: str,
) -> dict[str, Any]:
    report_id = _require_sha256(drift_report.get("drift_report_id"), "drift_report_id")
    _require_sha256(drift_report.get("deployment_id"), "drift.deployment_id")
    status = _require_nonempty_string(drift_report.get("status"), "drift.status")
    action = "approval_required" if status == "drift_detected" else "blocked"
    reason = (
        "validated drift evidence requires explicit retraining approval"
        if action == "approval_required"
        else f"retraining is blocked while drift status is {status}"
    )
    payload = {
        "schema_version": MONITORING_SCHEMA_VERSION,
        "drift_report_id": report_id,
        "deployment_id": drift_report["deployment_id"],
        "model_sha256": _require_sha256(model_sha256, "model_sha256"),
        "policy_generation": _require_nonempty_string(
            policy_generation, "policy_generation"
        ),
        "action": action,
        "reason": reason,
    }
    return {**payload, "retraining_proposal_id": sha256_bytes(canonical_json_bytes(payload))}


def approve_retraining(
    *,
    proposal: Mapping[str, Any],
    expected_proposal_id: str,
    approver: str,
    approval_generation: str,
) -> dict[str, Any]:
    proposal_id = _require_sha256(
        proposal.get("retraining_proposal_id"), "retraining_proposal_id"
    )
    if proposal_id != _require_sha256(expected_proposal_id, "expected_proposal_id"):
        raise ContractError("stale or mismatched retraining proposal")
    if proposal.get("action") != "approval_required":
        raise ContractError("retraining proposal is not eligible for approval")
    payload = {
        "schema_version": MONITORING_SCHEMA_VERSION,
        "retraining_proposal_id": proposal_id,
        "drift_report_id": proposal["drift_report_id"],
        "deployment_id": proposal["deployment_id"],
        "model_sha256": proposal["model_sha256"],
        "policy_generation": proposal["policy_generation"],
        "approver": _require_nonempty_string(approver, "approver"),
        "approval_generation": _require_nonempty_string(
            approval_generation, "approval_generation"
        ),
        "authorized_action": "start_controlled_retraining",
    }
    return {**payload, "retraining_approval_id": sha256_bytes(canonical_json_bytes(payload))}
