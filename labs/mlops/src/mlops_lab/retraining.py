from __future__ import annotations

from typing import Any, Mapping

from .contracts import ContractError, canonical_json_bytes, sha256_bytes
from .monitoring import CATEGORICAL_FEATURES, MONITORING_SCHEMA_VERSION, NUMERIC_FEATURES

DRIFT_STATUSES = {
    "no_data",
    "insufficient_evidence",
    "operational_failure",
    "drift_detected",
    "stable",
}


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
    if resolved != resolved or resolved in (float("inf"), float("-inf")):
        raise ContractError(f"{field} must be finite")
    return resolved


def _validate_canonical_id(value: Mapping[str, Any], id_field: str) -> None:
    identifier = _require_sha256(value.get(id_field), id_field)
    payload = {key: item for key, item in value.items() if key != id_field}
    if sha256_bytes(canonical_json_bytes(payload)) != identifier:
        raise ContractError(f"{id_field} does not match canonical payload")


def validate_drift_report(value: Mapping[str, Any]) -> None:
    _require_exact_keys(
        value,
        {
            "schema_version",
            "baseline_profile_id",
            "monitoring_window_id",
            "deployment_id",
            "minimum_successful_events",
            "thresholds",
            "numeric_psi",
            "categorical_tvd",
            "prediction_rate_delta",
            "exceeded_numeric_features",
            "exceeded_categorical_features",
            "observed_error_rate",
            "status",
            "drift_report_id",
        },
        "drift report",
    )
    if value.get("schema_version") != MONITORING_SCHEMA_VERSION:
        raise ContractError("drift report schema_version must equal 1")
    for field in ("baseline_profile_id", "monitoring_window_id", "deployment_id"):
        _require_sha256(value.get(field), f"drift.{field}")
    minimum = value.get("minimum_successful_events")
    if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 1:
        raise ContractError("drift minimum_successful_events must be positive")
    status = _require_nonempty_string(value.get("status"), "drift.status")
    if status not in DRIFT_STATUSES:
        raise ContractError("drift status is unsupported")
    thresholds = value.get("thresholds")
    if not isinstance(thresholds, dict) or set(thresholds) != {
        "numeric_psi",
        "categorical_tvd",
        "prediction_rate_delta",
        "maximum_error_rate",
    }:
        raise ContractError("drift thresholds keys mismatch")
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
        resolved = _finite_number(score, f"drift.categorical_tvd.{feature}")
        if not 0.0 <= resolved <= 1.0:
            raise ContractError("drift categorical TVD must be between 0 and 1")
    exceeded_numeric = value.get("exceeded_numeric_features")
    exceeded_categorical = value.get("exceeded_categorical_features")
    if not isinstance(exceeded_numeric, list) or not set(exceeded_numeric).issubset(
        NUMERIC_FEATURES
    ):
        raise ContractError("drift exceeded_numeric_features are invalid")
    if not isinstance(exceeded_categorical, list) or not set(
        exceeded_categorical
    ).issubset(CATEGORICAL_FEATURES):
        raise ContractError("drift exceeded_categorical_features are invalid")
    error_rate = _finite_number(
        value.get("observed_error_rate"), "drift.observed_error_rate"
    )
    if not 0.0 <= error_rate <= 1.0:
        raise ContractError("drift observed_error_rate must be between 0 and 1")
    delta = value.get("prediction_rate_delta")
    if delta is not None:
        resolved_delta = _finite_number(delta, "drift.prediction_rate_delta")
        if not 0.0 <= resolved_delta <= 1.0:
            raise ContractError("drift prediction_rate_delta must be between 0 and 1")
    _validate_canonical_id(value, "drift_report_id")


def build_retraining_proposal(
    *,
    drift_report: Mapping[str, Any],
    model_sha256: str,
    policy_generation: str,
) -> dict[str, Any]:
    validate_drift_report(drift_report)
    action = (
        "approval_required"
        if drift_report["status"] == "drift_detected"
        else "blocked"
    )
    reason = (
        "validated drift evidence requires explicit retraining approval"
        if action == "approval_required"
        else f"retraining is blocked while drift status is {drift_report['status']}"
    )
    payload = {
        "schema_version": MONITORING_SCHEMA_VERSION,
        "drift_report_id": drift_report["drift_report_id"],
        "deployment_id": drift_report["deployment_id"],
        "model_sha256": _require_sha256(model_sha256, "model_sha256"),
        "policy_generation": _require_nonempty_string(
            policy_generation, "policy_generation"
        ),
        "action": action,
        "reason": reason,
    }
    proposal = {
        **payload,
        "retraining_proposal_id": sha256_bytes(canonical_json_bytes(payload)),
    }
    validate_retraining_proposal(proposal)
    return proposal


def validate_retraining_proposal(value: Mapping[str, Any]) -> None:
    _require_exact_keys(
        value,
        {
            "schema_version",
            "drift_report_id",
            "deployment_id",
            "model_sha256",
            "policy_generation",
            "action",
            "reason",
            "retraining_proposal_id",
        },
        "retraining proposal",
    )
    if value.get("schema_version") != MONITORING_SCHEMA_VERSION:
        raise ContractError("retraining proposal schema_version must equal 1")
    for field in ("drift_report_id", "deployment_id", "model_sha256"):
        _require_sha256(value.get(field), f"proposal.{field}")
    _require_nonempty_string(value.get("policy_generation"), "proposal.policy_generation")
    action = _require_nonempty_string(value.get("action"), "proposal.action")
    if action not in {"approval_required", "blocked"}:
        raise ContractError("retraining proposal action is unsupported")
    _require_nonempty_string(value.get("reason"), "proposal.reason")
    _validate_canonical_id(value, "retraining_proposal_id")


def approve_retraining(
    *,
    proposal: Mapping[str, Any],
    expected_proposal_id: str,
    approver: str,
    approval_generation: str,
) -> dict[str, Any]:
    validate_retraining_proposal(proposal)
    proposal_id = proposal["retraining_proposal_id"]
    if proposal_id != _require_sha256(expected_proposal_id, "expected_proposal_id"):
        raise ContractError("stale or mismatched retraining proposal")
    if proposal["action"] != "approval_required":
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
    approval = {
        **payload,
        "retraining_approval_id": sha256_bytes(canonical_json_bytes(payload)),
    }
    validate_retraining_approval(approval)
    return approval


def validate_retraining_approval(value: Mapping[str, Any]) -> None:
    _require_exact_keys(
        value,
        {
            "schema_version",
            "retraining_proposal_id",
            "drift_report_id",
            "deployment_id",
            "model_sha256",
            "policy_generation",
            "approver",
            "approval_generation",
            "authorized_action",
            "retraining_approval_id",
        },
        "retraining approval",
    )
    if value.get("schema_version") != MONITORING_SCHEMA_VERSION:
        raise ContractError("retraining approval schema_version must equal 1")
    for field in (
        "retraining_proposal_id",
        "drift_report_id",
        "deployment_id",
        "model_sha256",
    ):
        _require_sha256(value.get(field), f"approval.{field}")
    for field in ("policy_generation", "approver", "approval_generation"):
        _require_nonempty_string(value.get(field), f"approval.{field}")
    if value.get("authorized_action") != "start_controlled_retraining":
        raise ContractError("retraining approval action is unsupported")
    _validate_canonical_id(value, "retraining_approval_id")
