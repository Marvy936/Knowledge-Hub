from __future__ import annotations

from typing import Any, Mapping

from .contracts import ContractError, canonical_json_bytes, sha256_bytes
from .monitoring import DRIFT_STATUSES, MONITORING_SCHEMA_VERSION, validate_drift_report


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


def _validate_canonical_id(value: Mapping[str, Any], id_field: str) -> None:
    identifier = _require_sha256(value.get(id_field), id_field)
    payload = {key: item for key, item in value.items() if key != id_field}
    if sha256_bytes(canonical_json_bytes(payload)) != identifier:
        raise ContractError(f"{id_field} does not match canonical payload")


def _proposal_action(status: str) -> tuple[str, str]:
    if status == "drift_detected":
        return (
            "approval_required",
            "validated drift evidence requires explicit retraining approval",
        )
    return "blocked", f"retraining is blocked while drift status is {status}"


def build_retraining_proposal(
    *,
    drift_report: Mapping[str, Any],
    model_sha256: str,
    policy_generation: str,
) -> dict[str, Any]:
    validate_drift_report(drift_report)
    action, reason = _proposal_action(drift_report["status"])
    payload = {
        "schema_version": MONITORING_SCHEMA_VERSION,
        "drift_report_id": drift_report["drift_report_id"],
        "drift_status": drift_report["status"],
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
            "drift_status",
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
    status = _require_nonempty_string(value.get("drift_status"), "proposal.drift_status")
    if status not in DRIFT_STATUSES:
        raise ContractError("retraining proposal drift status is unsupported")
    expected_action, expected_reason = _proposal_action(status)
    _require_nonempty_string(value.get("policy_generation"), "proposal.policy_generation")
    if value.get("action") != expected_action or value.get("reason") != expected_reason:
        raise ContractError("retraining proposal action is inconsistent with drift status")
    _validate_canonical_id(value, "retraining_proposal_id")


def _validate_proposal_against_report(
    proposal: Mapping[str, Any], drift_report: Mapping[str, Any]
) -> None:
    if proposal["drift_report_id"] != drift_report["drift_report_id"]:
        raise ContractError("retraining proposal belongs to another drift report")
    if proposal["drift_status"] != drift_report["status"]:
        raise ContractError("retraining proposal drift status does not match report")
    if proposal["deployment_id"] != drift_report["deployment_id"]:
        raise ContractError("retraining proposal deployment does not match drift report")
    action, reason = _proposal_action(drift_report["status"])
    if proposal["action"] != action or proposal["reason"] != reason:
        raise ContractError("retraining proposal was not derived from the drift report")


def approve_retraining(
    *,
    proposal: Mapping[str, Any],
    drift_report: Mapping[str, Any],
    expected_proposal_id: str,
    approver: str,
    approval_generation: str,
) -> dict[str, Any]:
    validate_drift_report(drift_report)
    validate_retraining_proposal(proposal)
    _validate_proposal_against_report(proposal, drift_report)
    proposal_id = proposal["retraining_proposal_id"]
    if proposal_id != _require_sha256(expected_proposal_id, "expected_proposal_id"):
        raise ContractError("stale or mismatched retraining proposal")
    if proposal["action"] != "approval_required":
        raise ContractError("retraining proposal is not eligible for approval")
    payload = {
        "schema_version": MONITORING_SCHEMA_VERSION,
        "retraining_proposal_id": proposal_id,
        "drift_report_id": proposal["drift_report_id"],
        "drift_status": proposal["drift_status"],
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
            "drift_status",
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
    if value.get("drift_status") != "drift_detected":
        raise ContractError("retraining approval requires drift_detected status")
    for field in ("policy_generation", "approver", "approval_generation"):
        _require_nonempty_string(value.get(field), f"approval.{field}")
    if value.get("authorized_action") != "start_controlled_retraining":
        raise ContractError("retraining approval action is unsupported")
    _validate_canonical_id(value, "retraining_approval_id")
