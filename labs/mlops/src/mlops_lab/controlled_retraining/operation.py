from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from ..contracts import (
    ContractError,
    build_dataset_manifest,
    canonical_json_bytes,
    sha256_bytes,
    sha256_file,
)
from ..monitoring import validate_drift_report
from ..retraining import validate_retraining_approval, validate_retraining_proposal
from ..serving import validate_deployment_manifest
from .common import (
    EXECUTOR_SCHEMA_VERSION,
    require_exact_keys,
    require_nonempty_string,
    require_sha256,
    validate_canonical_id,
)


def _validate_authorization_chain(
    *,
    approval: Mapping[str, Any],
    proposal: Mapping[str, Any],
    drift_report: Mapping[str, Any],
    current_deployment: Mapping[str, Any],
) -> None:
    validate_retraining_approval(approval)
    validate_retraining_proposal(proposal)
    validate_drift_report(drift_report)
    validate_deployment_manifest(current_deployment)

    if approval["retraining_proposal_id"] != proposal["retraining_proposal_id"]:
        raise ContractError("retraining approval belongs to another proposal")
    if approval["drift_report_id"] != drift_report["drift_report_id"]:
        raise ContractError("retraining approval belongs to another drift report")
    if proposal["drift_report_id"] != drift_report["drift_report_id"]:
        raise ContractError("retraining proposal belongs to another drift report")
    if (
        approval["drift_status"] != "drift_detected"
        or proposal["drift_status"] != drift_report["status"]
    ):
        raise ContractError(
            "retraining authorization does not pin drift_detected evidence"
        )
    if approval["deployment_id"] != current_deployment["deployment_id"]:
        raise ContractError("current deployment changed after retraining approval")
    if proposal["deployment_id"] != current_deployment["deployment_id"]:
        raise ContractError("retraining proposal belongs to another deployment")
    if approval["model_sha256"] != current_deployment["model"]["sha256"]:
        raise ContractError("current model changed after retraining approval")
    if proposal["model_sha256"] != current_deployment["model"]["sha256"]:
        raise ContractError("retraining proposal belongs to another model")
    if approval["policy_generation"] != proposal["policy_generation"]:
        raise ContractError("approval policy generation does not match proposal")


def build_controlled_retraining_operation(
    *,
    approval: Mapping[str, Any],
    proposal: Mapping[str, Any],
    drift_report: Mapping[str, Any],
    current_deployment: Mapping[str, Any],
    dataset_path: Path,
    dataset_name: str,
    dataset_generation: str,
    sample_request_path: Path,
    source_revision: str,
    seed: int,
    tracking_uri: str,
    experiment_name: str,
    model_name: str,
    registry_alias: str,
    promotion_alias: str,
) -> dict[str, Any]:
    _validate_authorization_chain(
        approval=approval,
        proposal=proposal,
        drift_report=drift_report,
        current_deployment=current_deployment,
    )
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ContractError("retraining seed must be a non-negative integer")
    if not sample_request_path.is_file():
        raise ContractError(f"sample request does not exist: {sample_request_path}")

    dataset_manifest = build_dataset_manifest(
        dataset_path,
        dataset_name=dataset_name,
        generation=dataset_generation,
    )
    subject = dataset_manifest["subject"]
    if subject["sha256"] == current_deployment["dataset_sha256"]:
        raise ContractError("controlled retraining requires a new dataset snapshot")

    registry = {
        "tracking_uri": require_nonempty_string(tracking_uri, "tracking_uri"),
        "experiment_name": require_nonempty_string(
            experiment_name, "experiment_name"
        ),
        "model_name": require_nonempty_string(model_name, "model_name"),
        "alias": require_nonempty_string(registry_alias, "registry_alias"),
        "sample_request_sha256": sha256_file(sample_request_path),
    }
    promotion = {
        "alias": require_nonempty_string(promotion_alias, "promotion_alias"),
        "expected_current_candidate_id": current_deployment["candidate_id"],
    }
    payload = {
        "schema_version": EXECUTOR_SCHEMA_VERSION,
        "operation_type": "controlled_retraining",
        "retraining_approval_id": approval["retraining_approval_id"],
        "retraining_proposal_id": proposal["retraining_proposal_id"],
        "drift_report_id": drift_report["drift_report_id"],
        "current_deployment_id": current_deployment["deployment_id"],
        "current_candidate_id": current_deployment["candidate_id"],
        "current_model_sha256": current_deployment["model"]["sha256"],
        "dataset": {
            "name": subject["dataset_name"],
            "generation": subject["generation"],
            "size_bytes": subject["size_bytes"],
            "sha256": subject["sha256"],
        },
        "source_revision": require_nonempty_string(
            source_revision, "source_revision"
        ),
        "seed": seed,
        "evaluation_policy_generation": proposal["policy_generation"],
        "registry": registry,
        "promotion": promotion,
    }
    operation = {
        **payload,
        "operation_id": sha256_bytes(canonical_json_bytes(payload)),
    }
    validate_controlled_retraining_operation(operation)
    return operation


def validate_controlled_retraining_operation(value: Mapping[str, Any]) -> None:
    require_exact_keys(
        value,
        {
            "schema_version",
            "operation_type",
            "retraining_approval_id",
            "retraining_proposal_id",
            "drift_report_id",
            "current_deployment_id",
            "current_candidate_id",
            "current_model_sha256",
            "dataset",
            "source_revision",
            "seed",
            "evaluation_policy_generation",
            "registry",
            "promotion",
            "operation_id",
        },
        "controlled retraining operation",
    )
    if value.get("schema_version") != EXECUTOR_SCHEMA_VERSION:
        raise ContractError("controlled retraining schema_version must equal 1")
    if value.get("operation_type") != "controlled_retraining":
        raise ContractError("operation_type must be controlled_retraining")

    for field in (
        "retraining_approval_id",
        "retraining_proposal_id",
        "drift_report_id",
        "current_deployment_id",
        "current_candidate_id",
        "current_model_sha256",
    ):
        require_sha256(value.get(field), f"operation.{field}")

    dataset = value.get("dataset")
    registry = value.get("registry")
    promotion = value.get("promotion")
    if not all(isinstance(item, dict) for item in (dataset, registry, promotion)):
        raise ContractError(
            "operation dataset, registry and promotion must be objects"
        )

    require_exact_keys(
        dataset,
        {"name", "generation", "size_bytes", "sha256"},
        "operation dataset",
    )
    require_nonempty_string(dataset.get("name"), "operation.dataset.name")
    require_nonempty_string(
        dataset.get("generation"), "operation.dataset.generation"
    )
    size = dataset.get("size_bytes")
    if isinstance(size, bool) or not isinstance(size, int) or size < 1:
        raise ContractError("operation.dataset.size_bytes must be positive")
    require_sha256(dataset.get("sha256"), "operation.dataset.sha256")

    require_nonempty_string(
        value.get("source_revision"), "operation.source_revision"
    )
    seed = value.get("seed")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ContractError("operation.seed must be a non-negative integer")
    require_nonempty_string(
        value.get("evaluation_policy_generation"),
        "operation.evaluation_policy_generation",
    )

    require_exact_keys(
        registry,
        {
            "tracking_uri",
            "experiment_name",
            "model_name",
            "alias",
            "sample_request_sha256",
        },
        "operation registry",
    )
    for field in ("tracking_uri", "experiment_name", "model_name", "alias"):
        require_nonempty_string(
            registry.get(field), f"operation.registry.{field}"
        )
    require_sha256(
        registry.get("sample_request_sha256"),
        "operation.registry.sample_request_sha256",
    )

    require_exact_keys(
        promotion,
        {"alias", "expected_current_candidate_id"},
        "operation promotion",
    )
    require_nonempty_string(promotion.get("alias"), "operation.promotion.alias")
    expected_candidate = require_sha256(
        promotion.get("expected_current_candidate_id"),
        "operation.promotion.expected_current_candidate_id",
    )
    if expected_candidate != value["current_candidate_id"]:
        raise ContractError(
            "promotion expected candidate does not match current candidate"
        )
    validate_canonical_id(value, "operation_id")


def validate_operation_inputs(
    *,
    operation: Mapping[str, Any],
    approval: Mapping[str, Any],
    proposal: Mapping[str, Any],
    drift_report: Mapping[str, Any],
    current_deployment: Mapping[str, Any],
    dataset_path: Path,
    sample_request_path: Path,
) -> dict[str, Any]:
    validate_controlled_retraining_operation(operation)
    _validate_authorization_chain(
        approval=approval,
        proposal=proposal,
        drift_report=drift_report,
        current_deployment=current_deployment,
    )
    bindings = {
        "retraining_approval_id": approval["retraining_approval_id"],
        "retraining_proposal_id": proposal["retraining_proposal_id"],
        "drift_report_id": drift_report["drift_report_id"],
        "current_deployment_id": current_deployment["deployment_id"],
        "current_candidate_id": current_deployment["candidate_id"],
        "current_model_sha256": current_deployment["model"]["sha256"],
    }
    for field, expected in bindings.items():
        if operation[field] != expected:
            raise ContractError(
                f"operation {field} does not match execution input"
            )

    if not dataset_path.is_file():
        raise ContractError(f"retraining dataset does not exist: {dataset_path}")
    if dataset_path.stat().st_size != operation["dataset"]["size_bytes"]:
        raise ContractError("retraining dataset size does not match operation")
    if sha256_file(dataset_path) != operation["dataset"]["sha256"]:
        raise ContractError("retraining dataset digest does not match operation")
    if (
        not sample_request_path.is_file()
        or sha256_file(sample_request_path)
        != operation["registry"]["sample_request_sha256"]
    ):
        raise ContractError("sample request digest does not match operation")

    return build_dataset_manifest(
        dataset_path,
        dataset_name=operation["dataset"]["name"],
        generation=operation["dataset"]["generation"],
    )
