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
DRIFT_STATUSES = {
    "no_data",
    "insufficient_evidence",
    "operational_failure",
    "drift_detected",
    "stable",
}
EPSILON = 1e-6
SUM_TOLERANCE = 1e-6


def _require_exact_keys(value: Mapping[str, Any], expected: set[str], field: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ContractError(
            f"{field} keys mismatch: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )


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


def _nonnegative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ContractError(f"{field} must be a non-negative integer")
    return value


def _rate(value: Any, field: str) -> float:
    resolved = _finite_number(value, field)
    if not 0.0 <= resolved <= 1.0:
        raise ContractError(f"{field} must be between 0 and 1")
    return resolved


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((len(ordered) - 1) * percentile)))
    return round(ordered[index], 6)


def _validate_event(event: Mapping[str, Any], index: int) -> None:
    _require_exact_keys(
        event,
        {"record", "success", "latency_ms", "prediction", "probability"},
        f"monitoring event {index}",
    )
    record = event.get("record")
    if not isinstance(record, dict) or set(record) != set(ALL_FEATURES):
        raise ContractError(f"monitoring event {index} has invalid record fields")
    for feature in NUMERIC_FEATURES:
        _finite_number(record[feature], f"event[{index}].record.{feature}")
    for feature in CATEGORICAL_FEATURES:
        _require_nonempty_string(record[feature], f"event[{index}].record.{feature}")
    if not isinstance(event.get("success"), bool):
        raise ContractError(f"monitoring event {index} success must be boolean")
    if _finite_number(event.get("latency_ms"), f"event[{index}].latency_ms") < 0:
        raise ContractError(f"monitoring event {index} latency must be non-negative")
    if event["success"]:
        if event.get("prediction") not in (0, 1):
            raise ContractError(f"monitoring event {index} prediction must be binary")
        _rate(event.get("probability"), f"event[{index}].probability")
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
    resolved = _quantile_boundaries(values, bin_count) if boundaries is None else boundaries
    return {
        "count": len(values),
        "mean": None if not values else round(sum(values) / len(values), 6),
        "minimum": None if not values else round(min(values), 6),
        "maximum": None if not values else round(max(values), 6),
        "boundaries": [round(value, 6) for value in resolved],
        "bin_proportions": [round(value, 9) for value in _histogram(values, resolved)],
    }


def _categorical_profile(
    values: list[str], *, categories: list[str] | None
) -> dict[str, Any]:
    resolved = sorted(set(values)) if categories is None else categories
    counts = {category: 0 for category in resolved}
    other = 0
    for value in values:
        if value in counts:
            counts[value] += 1
        else:
            other += 1
    total = len(values)
    return {
        "count": total,
        "categories": resolved,
        "proportions": {
            category: 0.0 if total == 0 else round(count / total, 9)
            for category, count in counts.items()
        },
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
        boundaries = None if baseline is None else list(
            baseline["numeric_features"][feature]["boundaries"]
        )
        numeric[feature] = _numeric_profile(
            values, boundaries=boundaries, bin_count=numeric_bin_count
        )
    for feature in CATEGORICAL_FEATURES:
        values = [str(event["record"][feature]) for event in successful]
        categories = None if baseline is None else list(
            baseline["categorical_features"][feature]["categories"]
        )
        categorical[feature] = _categorical_profile(values, categories=categories)
    latencies = [float(event["latency_ms"]) for event in events]
    predictions = [int(event["prediction"]) for event in successful]
    probabilities = [float(event["probability"]) for event in successful]
    return {
        "total_events": len(events),
        "successful_events": len(successful),
        "failed_events": len(events) - len(successful),
        "error_rate": 0.0 if not events else round((len(events) - len(successful)) / len(events), 9),
        "no_data": len(events) == 0,
        "latency_ms": {
            "minimum": None if not latencies else round(min(latencies), 6),
            "average": None if not latencies else round(sum(latencies) / len(latencies), 6),
            "p95": _percentile(latencies, 0.95),
            "maximum": None if not latencies else round(max(latencies), 6),
        },
        "prediction": {
            "positive_rate": None if not predictions else round(sum(predictions) / len(predictions), 9),
            "probability_mean": None if not probabilities else round(sum(probabilities) / len(probabilities), 9),
        },
        "numeric_features": numeric,
        "categorical_features": categorical,
    }


def _validate_numeric_profile(value: Any, *, expected_count: int, field: str) -> None:
    if not isinstance(value, dict):
        raise ContractError(f"{field} must be an object")
    _require_exact_keys(
        value,
        {"count", "mean", "minimum", "maximum", "boundaries", "bin_proportions"},
        field,
    )
    if _nonnegative_int(value["count"], f"{field}.count") != expected_count:
        raise ContractError(f"{field}.count does not match successful_events")
    boundaries = value["boundaries"]
    proportions = value["bin_proportions"]
    if not isinstance(boundaries, list) or not isinstance(proportions, list):
        raise ContractError(f"{field} boundaries and bin_proportions must be lists")
    resolved_boundaries = [_finite_number(item, f"{field}.boundaries") for item in boundaries]
    if any(left >= right for left, right in zip(resolved_boundaries, resolved_boundaries[1:])):
        raise ContractError(f"{field}.boundaries must be strictly increasing")
    if len(proportions) != len(boundaries) + 1:
        raise ContractError(f"{field}.bin_proportions length is inconsistent")
    resolved_proportions = [_rate(item, f"{field}.bin_proportions") for item in proportions]
    expected_sum = 0.0 if expected_count == 0 else 1.0
    if abs(sum(resolved_proportions) - expected_sum) > SUM_TOLERANCE:
        raise ContractError(f"{field}.bin_proportions do not sum to {expected_sum}")
    stats = (value["minimum"], value["mean"], value["maximum"])
    if expected_count == 0:
        if any(item is not None for item in stats):
            raise ContractError(f"{field} statistics must be null without successful events")
    else:
        minimum, mean, maximum = (
            _finite_number(value["minimum"], f"{field}.minimum"),
            _finite_number(value["mean"], f"{field}.mean"),
            _finite_number(value["maximum"], f"{field}.maximum"),
        )
        if not minimum <= mean <= maximum:
            raise ContractError(f"{field} statistics are inconsistent")


def _validate_categorical_profile(value: Any, *, expected_count: int, field: str) -> None:
    if not isinstance(value, dict):
        raise ContractError(f"{field} must be an object")
    _require_exact_keys(
        value,
        {"count", "categories", "proportions", "other_proportion"},
        field,
    )
    if _nonnegative_int(value["count"], f"{field}.count") != expected_count:
        raise ContractError(f"{field}.count does not match successful_events")
    categories = value["categories"]
    proportions = value["proportions"]
    if not isinstance(categories, list) or not all(
        isinstance(item, str) and item.strip() for item in categories
    ):
        raise ContractError(f"{field}.categories must be non-empty strings")
    if len(categories) != len(set(categories)):
        raise ContractError(f"{field}.categories must be unique")
    if not isinstance(proportions, dict) or set(proportions) != set(categories):
        raise ContractError(f"{field}.proportions keys must match categories")
    resolved = [_rate(proportions[item], f"{field}.proportions.{item}") for item in categories]
    other = _rate(value["other_proportion"], f"{field}.other_proportion")
    expected_sum = 0.0 if expected_count == 0 else 1.0
    if abs(sum(resolved) + other - expected_sum) > SUM_TOLERANCE:
        raise ContractError(f"{field} proportions do not sum to {expected_sum}")


def _validate_aggregate(value: Mapping[str, Any], *, field: str) -> None:
    total = _nonnegative_int(value.get("total_events"), f"{field}.total_events")
    success = _nonnegative_int(value.get("successful_events"), f"{field}.successful_events")
    failed = _nonnegative_int(value.get("failed_events"), f"{field}.failed_events")
    if success + failed != total:
        raise ContractError(f"{field} event counts are inconsistent")
    if value.get("no_data") is not (total == 0):
        raise ContractError(f"{field}.no_data is inconsistent")
    expected_error = 0.0 if total == 0 else round(failed / total, 9)
    if abs(_rate(value.get("error_rate"), f"{field}.error_rate") - expected_error) > 1e-9:
        raise ContractError(f"{field}.error_rate is inconsistent")

    latency = value.get("latency_ms")
    prediction = value.get("prediction")
    numeric = value.get("numeric_features")
    categorical = value.get("categorical_features")
    if not all(isinstance(item, dict) for item in (latency, prediction, numeric, categorical)):
        raise ContractError(f"{field} nested profiles must be objects")
    _require_exact_keys(latency, {"minimum", "average", "p95", "maximum"}, f"{field}.latency_ms")
    _require_exact_keys(prediction, {"positive_rate", "probability_mean"}, f"{field}.prediction")
    if total == 0:
        if any(latency[item] is not None for item in latency):
            raise ContractError(f"{field} latency must be null for no-data windows")
    else:
        minimum = _finite_number(latency["minimum"], f"{field}.latency.minimum")
        average = _finite_number(latency["average"], f"{field}.latency.average")
        p95 = _finite_number(latency["p95"], f"{field}.latency.p95")
        maximum = _finite_number(latency["maximum"], f"{field}.latency.maximum")
        if minimum < 0 or not (minimum <= average <= maximum and minimum <= p95 <= maximum):
            raise ContractError(f"{field} latency statistics are inconsistent")
    if success == 0:
        if prediction["positive_rate"] is not None or prediction["probability_mean"] is not None:
            raise ContractError(f"{field} prediction aggregates must be null without successes")
    else:
        _rate(prediction["positive_rate"], f"{field}.prediction.positive_rate")
        _rate(prediction["probability_mean"], f"{field}.prediction.probability_mean")
    if set(numeric) != set(NUMERIC_FEATURES) or set(categorical) != set(CATEGORICAL_FEATURES):
        raise ContractError(f"{field} feature profile keys mismatch")
    for feature in NUMERIC_FEATURES:
        _validate_numeric_profile(
            numeric[feature], expected_count=success, field=f"{field}.numeric_features.{feature}"
        )
    for feature in CATEGORICAL_FEATURES:
        _validate_categorical_profile(
            categorical[feature], expected_count=success, field=f"{field}.categorical_features.{feature}"
        )


def _validate_canonical_id(value: Mapping[str, Any], id_field: str) -> None:
    identifier = _require_sha256(value.get(id_field), id_field)
    payload = {key: item for key, item in value.items() if key != id_field}
    if sha256_bytes(canonical_json_bytes(payload)) != identifier:
        raise ContractError(f"{id_field} does not match canonical payload")


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
        **_profile_events(resolved_events, baseline=None, numeric_bin_count=numeric_bin_count),
    }
    profile = {**payload, "baseline_profile_id": sha256_bytes(canonical_json_bytes(payload))}
    validate_baseline_profile(profile)
    return profile


def validate_baseline_profile(value: Mapping[str, Any]) -> None:
    expected = {
        "schema_version", "profile_name", "generation", "numeric_bin_count",
        "total_events", "successful_events", "failed_events", "error_rate", "no_data",
        "latency_ms", "prediction", "numeric_features", "categorical_features",
        "baseline_profile_id",
    }
    _require_exact_keys(value, expected, "baseline profile")
    if value.get("schema_version") != MONITORING_SCHEMA_VERSION:
        raise ContractError("baseline schema_version must equal 1")
    _require_nonempty_string(value.get("profile_name"), "baseline.profile_name")
    _require_nonempty_string(value.get("generation"), "baseline.generation")
    bins = value.get("numeric_bin_count")
    if isinstance(bins, bool) or not isinstance(bins, int) or bins < 2:
        raise ContractError("baseline numeric_bin_count must be at least 2")
    _validate_aggregate(value, field="baseline")
    if value["total_events"] < 1 or value["failed_events"] != 0:
        raise ContractError("baseline must contain successful events only")
    _validate_canonical_id(value, "baseline_profile_id")


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
            resolved_events, baseline=baseline, numeric_bin_count=baseline["numeric_bin_count"]
        ),
    }
    window = {**payload, "monitoring_window_id": sha256_bytes(canonical_json_bytes(payload))}
    validate_monitoring_window(window)
    return window


def validate_monitoring_window(value: Mapping[str, Any]) -> None:
    expected = {
        "schema_version", "baseline_profile_id", "deployment_id",
        "total_events", "successful_events", "failed_events", "error_rate", "no_data",
        "latency_ms", "prediction", "numeric_features", "categorical_features",
        "monitoring_window_id",
    }
    _require_exact_keys(value, expected, "monitoring window")
    if value.get("schema_version") != MONITORING_SCHEMA_VERSION:
        raise ContractError("monitoring window schema_version must equal 1")
    _require_sha256(value.get("baseline_profile_id"), "window.baseline_profile_id")
    _require_sha256(value.get("deployment_id"), "window.deployment_id")
    _validate_aggregate(value, field="window")
    _validate_canonical_id(value, "monitoring_window_id")


def _psi(expected: list[float], actual: list[float]) -> float:
    if len(expected) != len(actual):
        raise ContractError("numeric profile bin counts do not match")
    return sum(
        (observed - reference) * math.log((observed + EPSILON) / (reference + EPSILON))
        for reference, observed in zip(expected, actual, strict=True)
    )


def _tvd(reference: Mapping[str, float], actual: Mapping[str, float], other: float) -> float:
    return 0.5 * (
        sum(abs(float(reference[key]) - float(actual.get(key, 0.0))) for key in reference)
        + abs(other)
    )


def _expected_drift_status(value: Mapping[str, Any]) -> str:
    if value["observed_no_data"]:
        return "no_data"
    if value["observed_successful_events"] < value["minimum_successful_events"]:
        return "insufficient_evidence"
    if value["observed_error_rate"] > value["thresholds"]["maximum_error_rate"]:
        return "operational_failure"
    if (
        value["exceeded_numeric_features"]
        or value["exceeded_categorical_features"]
        or (
            value["prediction_rate_delta"] is not None
            and value["prediction_rate_delta"] > value["thresholds"]["prediction_rate_delta"]
        )
    ):
        return "drift_detected"
    return "stable"


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
        "categorical_tvd": _rate(categorical_tvd_threshold, "categorical_tvd_threshold"),
        "prediction_rate_delta": _rate(
            prediction_rate_delta_threshold, "prediction_rate_delta_threshold"
        ),
        "maximum_error_rate": _rate(maximum_error_rate, "maximum_error_rate"),
    }
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
    prediction_delta = None if baseline_rate is None or window_rate is None else round(
        abs(float(window_rate) - float(baseline_rate)), 9
    )
    exceeded_numeric = sorted(
        feature for feature, score in numeric_scores.items()
        if score > thresholds["numeric_psi"]
    )
    exceeded_categorical = sorted(
        feature for feature, score in categorical_scores.items()
        if score > thresholds["categorical_tvd"]
    )
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
        "observed_total_events": window["total_events"],
        "observed_successful_events": window["successful_events"],
        "observed_failed_events": window["failed_events"],
        "observed_no_data": window["no_data"],
        "observed_error_rate": window["error_rate"],
    }
    payload["status"] = _expected_drift_status(payload)
    report = {**payload, "drift_report_id": sha256_bytes(canonical_json_bytes(payload))}
    validate_drift_report(report)
    return report


def validate_drift_report(value: Mapping[str, Any]) -> None:
    expected = {
        "schema_version", "baseline_profile_id", "monitoring_window_id", "deployment_id",
        "minimum_successful_events", "thresholds", "numeric_psi", "categorical_tvd",
        "prediction_rate_delta", "exceeded_numeric_features", "exceeded_categorical_features",
        "observed_total_events", "observed_successful_events", "observed_failed_events",
        "observed_no_data", "observed_error_rate", "status", "drift_report_id",
    }
    _require_exact_keys(value, expected, "drift report")
    if value.get("schema_version") != MONITORING_SCHEMA_VERSION:
        raise ContractError("drift report schema_version must equal 1")
    for field in ("baseline_profile_id", "monitoring_window_id", "deployment_id"):
        _require_sha256(value.get(field), f"drift.{field}")
    minimum = value.get("minimum_successful_events")
    if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 1:
        raise ContractError("drift minimum_successful_events must be positive")
    thresholds = value.get("thresholds")
    if not isinstance(thresholds, dict):
        raise ContractError("drift thresholds must be an object")
    _require_exact_keys(
        thresholds,
        {"numeric_psi", "categorical_tvd", "prediction_rate_delta", "maximum_error_rate"},
        "drift thresholds",
    )
    numeric_threshold = _finite_number(thresholds["numeric_psi"], "drift.thresholds.numeric_psi")
    if numeric_threshold < 0:
        raise ContractError("drift numeric PSI threshold must be non-negative")
    for field in ("categorical_tvd", "prediction_rate_delta", "maximum_error_rate"):
        _rate(thresholds[field], f"drift.thresholds.{field}")
    numeric = value.get("numeric_psi")
    categorical = value.get("categorical_tvd")
    if not isinstance(numeric, dict) or set(numeric) != set(NUMERIC_FEATURES):
        raise ContractError("drift numeric_psi feature keys mismatch")
    if not isinstance(categorical, dict) or set(categorical) != set(CATEGORICAL_FEATURES):
        raise ContractError("drift categorical_tvd feature keys mismatch")
    for feature, score in numeric.items():
        if _finite_number(score, f"drift.numeric_psi.{feature}") < 0:
            raise ContractError("drift numeric PSI must be non-negative")
    for feature, score in categorical.items():
        _rate(score, f"drift.categorical_tvd.{feature}")
    expected_numeric = sorted(
        feature for feature, score in numeric.items() if score > numeric_threshold
    )
    expected_categorical = sorted(
        feature for feature, score in categorical.items()
        if score > thresholds["categorical_tvd"]
    )
    if value.get("exceeded_numeric_features") != expected_numeric:
        raise ContractError("drift exceeded_numeric_features are inconsistent")
    if value.get("exceeded_categorical_features") != expected_categorical:
        raise ContractError("drift exceeded_categorical_features are inconsistent")
    delta = value.get("prediction_rate_delta")
    if delta is not None:
        _rate(delta, "drift.prediction_rate_delta")
    total = _nonnegative_int(value.get("observed_total_events"), "drift.observed_total_events")
    success = _nonnegative_int(value.get("observed_successful_events"), "drift.observed_successful_events")
    failed = _nonnegative_int(value.get("observed_failed_events"), "drift.observed_failed_events")
    if success + failed != total:
        raise ContractError("drift observed event counts are inconsistent")
    if value.get("observed_no_data") is not (total == 0):
        raise ContractError("drift observed_no_data is inconsistent")
    expected_error = 0.0 if total == 0 else round(failed / total, 9)
    if abs(_rate(value.get("observed_error_rate"), "drift.observed_error_rate") - expected_error) > 1e-9:
        raise ContractError("drift observed_error_rate is inconsistent")
    status = _require_nonempty_string(value.get("status"), "drift.status")
    if status not in DRIFT_STATUSES:
        raise ContractError("drift status is unsupported")
    if status != _expected_drift_status(value):
        raise ContractError("drift status is inconsistent with observed evidence")
    _validate_canonical_id(value, "drift_report_id")


def inject_drift(records: Iterable[Mapping[str, Any]], *, mode: str) -> list[dict[str, Any]]:
    resolved_mode = _require_nonempty_string(mode, "drift mode")
    if resolved_mode not in {"control", "shift"}:
        raise ContractError("drift mode must be control or shift")
    output = [deepcopy(dict(record)) for record in records]
    if resolved_mode == "control":
        return output
    for record in output:
        record["monthly_spend_eur"] = min(250.0, float(record["monthly_spend_eur"]) + 80.0)
        record["support_tickets_90d"] = min(30, int(record["support_tickets_90d"]) + 6)
        record["login_days_30d"] = max(0, int(record["login_days_30d"]) - 8)
        record["days_since_last_login"] = min(180, int(record["days_since_last_login"]) + 40)
        record["contract_type"] = "monthly"
        record["auto_pay"] = "no"
    return output
