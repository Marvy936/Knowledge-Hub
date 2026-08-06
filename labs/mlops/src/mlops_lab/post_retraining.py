from __future__ import annotations

from typing import Any, Mapping

from .contracts import ContractError, canonical_json_bytes, sha256_bytes
from .controlled_retraining import (
    validate_controlled_retraining_operation,
    validate_controlled_retraining_state,
)
from .registry import validate_registry_evidence
from .serving import (
    build_deployment_manifest,
    build_routing_state,
    validate_deployment_manifest,
    validate_release_manifest,
    validate_routing_state,
)


def _require_sha256(value: Any, field: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ContractError(f"{field} must be a lowercase SHA-256 digest")
    return value


def build_post_retraining_handoff(
    *,
    operation: Mapping[str, Any],
    completed_state: Mapping[str, Any],
    release: Mapping[str, Any],
    registry_evidence: Mapping[str, Any],
    current_deployment: Mapping[str, Any],
    current_routing_state: Mapping[str, Any],
    service_name: str,
    generation: str,
    image_reference: str,
    image_digest: str,
    canary_basis_points: int,
    expected_current_routing_state_id: str,
) -> dict[str, Any]:
    validate_controlled_retraining_operation(operation)
    validate_controlled_retraining_state(completed_state)
    validate_release_manifest(release)
    validate_registry_evidence(registry_evidence)
    validate_deployment_manifest(current_deployment)
    validate_routing_state(current_routing_state)

    if completed_state["phase"] != "completed":
        raise ContractError("post-retraining handoff requires a completed operation")
    if completed_state["operation_id"] != operation["operation_id"]:
        raise ContractError("completed state belongs to another operation")
    if current_deployment["deployment_id"] != operation["current_deployment_id"]:
        raise ContractError("current deployment does not match retraining operation")
    if current_deployment["candidate_id"] != operation["current_candidate_id"]:
        raise ContractError("current candidate does not match retraining operation")
    if (
        current_deployment["model"]["sha256"]
        != operation["current_model_sha256"]
    ):
        raise ContractError("current model does not match retraining operation")

    artifacts = completed_state["artifacts"]
    if artifacts["release_id"] != release["release_id"]:
        raise ContractError("completed state release does not match handoff release")
    if artifacts["candidate_id"] != release["candidate_id"]:
        raise ContractError("completed state candidate does not match release")
    if artifacts["model_sha256"] != release["model_sha256"]:
        raise ContractError("completed state model does not match release")
    if (
        artifacts["registry_evidence_id"]
        != registry_evidence["registry_evidence_id"]
    ):
        raise ContractError("completed state Registry evidence does not match")
    if artifacts["registry_version"] != registry_evidence["registry"]["version"]:
        raise ContractError("completed state Registry version does not match")
    if release["candidate_id"] != registry_evidence["candidate_id"]:
        raise ContractError("release and Registry evidence candidate mismatch")
    if release["source_revision"] != operation["source_revision"]:
        raise ContractError("release source revision does not match operation")
    if release["dataset_sha256"] != operation["dataset"]["sha256"]:
        raise ContractError("release dataset does not match retraining operation")
    if (
        release["policy_generation"]
        != operation["evaluation_policy_generation"]
    ):
        raise ContractError("release policy generation does not match operation")
    if release["previous_candidate_id"] != current_deployment["candidate_id"]:
        raise ContractError(
            "release does not advance the current deployment candidate"
        )
    if release["candidate_id"] == current_deployment["candidate_id"]:
        raise ContractError("post-retraining deployment must use a new candidate")
    if service_name != current_deployment["service_name"]:
        raise ContractError("handoff service does not match current deployment")
    if generation == current_deployment["generation"]:
        raise ContractError("post-retraining generation must be new")
    if current_routing_state["service_name"] != service_name:
        raise ContractError("current routing state belongs to another service")
    if (
        current_routing_state["stable_deployment_id"]
        != current_deployment["deployment_id"]
    ):
        raise ContractError(
            "current routing stable subject is not the current deployment"
        )
    if current_routing_state["canary_deployment_id"] is not None:
        raise ContractError("existing canary must be closed before retraining handoff")
    if not 1 <= canary_basis_points < 10_000:
        raise ContractError(
            "post-retraining canary traffic must be between 1 and 9999 basis points"
        )
    if current_routing_state["routing_state_id"] != _require_sha256(
        expected_current_routing_state_id,
        "expected_current_routing_state_id",
    ):
        raise ContractError("stale post-retraining routing subject")

    deployment = build_deployment_manifest(
        release=release,
        registry_evidence=registry_evidence,
        service_name=service_name,
        generation=generation,
        image_reference=image_reference,
        image_digest=image_digest,
    )
    routing = build_routing_state(
        stable=current_deployment,
        canary=deployment,
        canary_basis_points=canary_basis_points,
        current_state=current_routing_state,
        expected_current_state_id=expected_current_routing_state_id,
    )
    payload = {
        "schema_version": 1,
        "operation_id": operation["operation_id"],
        "completed_state_id": completed_state["state_id"],
        "previous_deployment_id": current_deployment["deployment_id"],
        "previous_routing_state_id": current_routing_state["routing_state_id"],
        "deployment": deployment,
        "routing_state": routing,
    }
    handoff = {
        **payload,
        "post_retraining_handoff_id": sha256_bytes(
            canonical_json_bytes(payload)
        ),
    }
    validate_post_retraining_handoff(handoff)
    return handoff


def validate_post_retraining_handoff(value: Mapping[str, Any]) -> None:
    expected = {
        "schema_version",
        "operation_id",
        "completed_state_id",
        "previous_deployment_id",
        "previous_routing_state_id",
        "deployment",
        "routing_state",
        "post_retraining_handoff_id",
    }
    if set(value) != expected or value.get("schema_version") != 1:
        raise ContractError("post-retraining handoff keys or schema are invalid")

    for field in (
        "operation_id",
        "completed_state_id",
        "previous_deployment_id",
        "previous_routing_state_id",
    ):
        _require_sha256(value.get(field), field)

    deployment = value.get("deployment")
    routing = value.get("routing_state")
    if not isinstance(deployment, dict) or not isinstance(routing, dict):
        raise ContractError("handoff deployment and routing_state must be objects")
    validate_deployment_manifest(deployment)
    validate_routing_state(routing)

    if routing["previous_routing_state_id"] != value["previous_routing_state_id"]:
        raise ContractError("handoff routing predecessor mismatch")
    if routing["stable_deployment_id"] != value["previous_deployment_id"]:
        raise ContractError("handoff stable deployment mismatch")
    if routing["canary_deployment_id"] != deployment["deployment_id"]:
        raise ContractError("handoff canary deployment mismatch")
    if not 1 <= routing["canary_basis_points"] < 10_000:
        raise ContractError("handoff routing is not a bounded canary")

    identifier = _require_sha256(
        value.get("post_retraining_handoff_id"),
        "post_retraining_handoff_id",
    )
    payload = {
        key: item
        for key, item in value.items()
        if key != "post_retraining_handoff_id"
    }
    if sha256_bytes(canonical_json_bytes(payload)) != identifier:
        raise ContractError(
            "post_retraining_handoff_id does not match canonical payload"
        )
