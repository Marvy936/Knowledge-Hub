from __future__ import annotations

from typing import Any, Mapping

from .contracts import ContractError, canonical_json_bytes, sha256_bytes
from .registry import validate_registry_evidence

SERVING_SCHEMA_VERSION = 1
ROUTING_BUCKETS = 10_000


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


def _require_image_digest(value: Any) -> str:
    text = _require_nonempty_string(value, "image.digest")
    if not text.startswith("sha256:"):
        raise ContractError("image.digest must use the sha256 algorithm")
    _require_sha256(text.removeprefix("sha256:"), "image.digest")
    return text


def validate_release_manifest(value: Mapping[str, Any]) -> None:
    _require_exact_keys(
        value,
        {
            "schema_version",
            "alias",
            "previous_candidate_id",
            "candidate_id",
            "dataset_sha256",
            "model_sha256",
            "evaluation_sha256",
            "policy_generation",
            "source_revision",
            "release_id",
        },
        "release manifest",
    )
    if value.get("schema_version") != 1:
        raise ContractError("release manifest schema_version must equal 1")
    _require_nonempty_string(value.get("alias"), "release.alias")
    previous = value.get("previous_candidate_id")
    if previous is not None:
        _require_sha256(previous, "release.previous_candidate_id")
    for field in (
        "candidate_id",
        "dataset_sha256",
        "model_sha256",
        "evaluation_sha256",
    ):
        _require_sha256(value.get(field), f"release.{field}")
    _require_nonempty_string(value.get("policy_generation"), "release.policy_generation")
    _require_nonempty_string(value.get("source_revision"), "release.source_revision")
    release_id = _require_sha256(value.get("release_id"), "release.release_id")
    payload = {key: item for key, item in value.items() if key != "release_id"}
    if sha256_bytes(canonical_json_bytes(payload)) != release_id:
        raise ContractError("release.release_id does not match canonical release payload")


def build_deployment_manifest(
    *,
    release: Mapping[str, Any],
    registry_evidence: Mapping[str, Any],
    service_name: str,
    generation: str,
    image_reference: str,
    image_digest: str,
) -> dict[str, Any]:
    validate_release_manifest(release)
    validate_registry_evidence(registry_evidence)
    resolved_service = _require_nonempty_string(service_name, "service_name")
    resolved_generation = _require_nonempty_string(generation, "generation")
    resolved_image_reference = _require_nonempty_string(
        image_reference, "image.reference"
    )
    resolved_image_digest = _require_image_digest(image_digest)

    if release["candidate_id"] != registry_evidence["candidate_id"]:
        raise ContractError("release candidate does not match Registry evidence")
    if release["model_sha256"] != registry_evidence["artifact_readback"]["downloaded_sha256"]:
        raise ContractError("release model digest does not match Registry artifact read-back")
    if release["source_revision"] != registry_evidence["source_revision"]:
        raise ContractError("release source revision does not match Registry evidence")

    exact_uri = registry_evidence["registry"]["exact_uri"]
    if "@" in exact_uri:
        raise ContractError("deployment subject must not contain a mutable Registry alias")
    version = registry_evidence["registry"]["version"]
    if exact_uri != f"models:/{registry_evidence['registry']['name']}/{version}":
        raise ContractError("Registry exact URI does not match its numeric version")

    payload = {
        "schema_version": SERVING_SCHEMA_VERSION,
        "service_name": resolved_service,
        "generation": resolved_generation,
        "release_id": release["release_id"],
        "candidate_id": release["candidate_id"],
        "source_revision": release["source_revision"],
        "dataset_sha256": release["dataset_sha256"],
        "evaluation_sha256": release["evaluation_sha256"],
        "model": {
            "sha256": release["model_sha256"],
            "registry_name": registry_evidence["registry"]["name"],
            "registry_version": version,
            "exact_uri": exact_uri,
            "registry_evidence_id": registry_evidence["registry_evidence_id"],
        },
        "image": {
            "reference": resolved_image_reference,
            "digest": resolved_image_digest,
        },
    }
    return {
        **payload,
        "deployment_id": sha256_bytes(canonical_json_bytes(payload)),
    }


def validate_deployment_manifest(value: Mapping[str, Any]) -> None:
    _require_exact_keys(
        value,
        {
            "schema_version",
            "service_name",
            "generation",
            "release_id",
            "candidate_id",
            "source_revision",
            "dataset_sha256",
            "evaluation_sha256",
            "model",
            "image",
            "deployment_id",
        },
        "deployment manifest",
    )
    if value.get("schema_version") != SERVING_SCHEMA_VERSION:
        raise ContractError("deployment manifest schema_version must equal 1")
    for field in ("service_name", "generation", "source_revision"):
        _require_nonempty_string(value.get(field), f"deployment.{field}")
    for field in (
        "release_id",
        "candidate_id",
        "dataset_sha256",
        "evaluation_sha256",
        "deployment_id",
    ):
        _require_sha256(value.get(field), f"deployment.{field}")

    model = value.get("model")
    image = value.get("image")
    if not isinstance(model, dict) or not isinstance(image, dict):
        raise ContractError("deployment model and image must be objects")
    _require_exact_keys(
        model,
        {
            "sha256",
            "registry_name",
            "registry_version",
            "exact_uri",
            "registry_evidence_id",
        },
        "deployment model",
    )
    _require_sha256(model.get("sha256"), "deployment.model.sha256")
    _require_sha256(
        model.get("registry_evidence_id"), "deployment.model.registry_evidence_id"
    )
    name = _require_nonempty_string(
        model.get("registry_name"), "deployment.model.registry_name"
    )
    version = _require_nonempty_string(
        model.get("registry_version"), "deployment.model.registry_version"
    )
    if not version.isdigit() or int(version) < 1:
        raise ContractError("deployment.model.registry_version must be numeric")
    exact_uri = _require_nonempty_string(
        model.get("exact_uri"), "deployment.model.exact_uri"
    )
    if exact_uri != f"models:/{name}/{version}" or "@" in exact_uri:
        raise ContractError("deployment.model.exact_uri must pin a numeric Registry version")

    _require_exact_keys(image, {"reference", "digest"}, "deployment image")
    _require_nonempty_string(image.get("reference"), "deployment.image.reference")
    _require_image_digest(image.get("digest"))

    deployment_id = value["deployment_id"]
    payload = {key: item for key, item in value.items() if key != "deployment_id"}
    if sha256_bytes(canonical_json_bytes(payload)) != deployment_id:
        raise ContractError("deployment_id does not match canonical deployment payload")


def build_routing_state(
    *,
    stable: Mapping[str, Any],
    canary: Mapping[str, Any] | None,
    canary_basis_points: int,
    current_state: Mapping[str, Any] | None,
    expected_current_state_id: str | None,
) -> dict[str, Any]:
    validate_deployment_manifest(stable)
    if canary is not None:
        validate_deployment_manifest(canary)
        if canary["service_name"] != stable["service_name"]:
            raise ContractError("stable and canary deployments target different services")
        if canary["deployment_id"] == stable["deployment_id"]:
            raise ContractError("stable and canary deployments must be different")
    if not isinstance(canary_basis_points, int) or isinstance(canary_basis_points, bool):
        raise ContractError("canary_basis_points must be an integer")
    if not 0 <= canary_basis_points <= ROUTING_BUCKETS:
        raise ContractError("canary_basis_points must be between 0 and 10000")
    if canary is None and canary_basis_points != 0:
        raise ContractError("canary traffic requires a canary deployment")
    if canary is not None and canary_basis_points == 0:
        raise ContractError("a canary deployment requires non-zero canary traffic")

    actual_current_state_id = None
    if current_state is not None:
        validate_routing_state(current_state)
        actual_current_state_id = current_state["routing_state_id"]
        if current_state["service_name"] != stable["service_name"]:
            raise ContractError("current routing state belongs to another service")
    if expected_current_state_id is not None:
        _require_sha256(expected_current_state_id, "expected_current_state_id")
    if actual_current_state_id != expected_current_state_id:
        raise ContractError(
            "stale routing update: "
            f"expected {expected_current_state_id!r}, found {actual_current_state_id!r}"
        )

    payload = {
        "schema_version": SERVING_SCHEMA_VERSION,
        "service_name": stable["service_name"],
        "stable_deployment_id": stable["deployment_id"],
        "canary_deployment_id": None if canary is None else canary["deployment_id"],
        "canary_basis_points": canary_basis_points,
        "previous_routing_state_id": actual_current_state_id,
    }
    return {
        **payload,
        "routing_state_id": sha256_bytes(canonical_json_bytes(payload)),
    }


def validate_routing_state(value: Mapping[str, Any]) -> None:
    _require_exact_keys(
        value,
        {
            "schema_version",
            "service_name",
            "stable_deployment_id",
            "canary_deployment_id",
            "canary_basis_points",
            "previous_routing_state_id",
            "routing_state_id",
        },
        "routing state",
    )
    if value.get("schema_version") != SERVING_SCHEMA_VERSION:
        raise ContractError("routing state schema_version must equal 1")
    _require_nonempty_string(value.get("service_name"), "routing.service_name")
    _require_sha256(value.get("stable_deployment_id"), "routing.stable_deployment_id")
    canary = value.get("canary_deployment_id")
    if canary is not None:
        _require_sha256(canary, "routing.canary_deployment_id")
    previous = value.get("previous_routing_state_id")
    if previous is not None:
        _require_sha256(previous, "routing.previous_routing_state_id")
    basis_points = value.get("canary_basis_points")
    if not isinstance(basis_points, int) or isinstance(basis_points, bool):
        raise ContractError("routing.canary_basis_points must be an integer")
    if not 0 <= basis_points <= ROUTING_BUCKETS:
        raise ContractError("routing.canary_basis_points must be between 0 and 10000")
    if canary is None and basis_points != 0:
        raise ContractError("routing state has canary traffic without a canary deployment")
    if canary is not None and basis_points == 0:
        raise ContractError("routing state has a canary deployment without traffic")
    routing_state_id = _require_sha256(value.get("routing_state_id"), "routing.routing_state_id")
    payload = {key: item for key, item in value.items() if key != "routing_state_id"}
    if sha256_bytes(canonical_json_bytes(payload)) != routing_state_id:
        raise ContractError("routing_state_id does not match canonical routing payload")


def route_request(
    *,
    routing_state: Mapping[str, Any],
    deployments: Mapping[str, Mapping[str, Any]],
    routing_key: str,
) -> dict[str, Any]:
    validate_routing_state(routing_state)
    resolved_key = _require_nonempty_string(routing_key, "routing_key")
    stable_id = routing_state["stable_deployment_id"]
    canary_id = routing_state["canary_deployment_id"]
    required_ids = {stable_id} if canary_id is None else {stable_id, canary_id}
    if not required_ids.issubset(deployments):
        raise ContractError("routing deployment map does not contain all referenced subjects")
    for deployment_id in required_ids:
        deployment = deployments[deployment_id]
        validate_deployment_manifest(deployment)
        if deployment["deployment_id"] != deployment_id:
            raise ContractError("deployment map key does not match deployment_id")
        if deployment["service_name"] != routing_state["service_name"]:
            raise ContractError("routing deployment belongs to another service")

    bucket = int(sha256_bytes(resolved_key.encode("utf-8"))[:8], 16) % ROUTING_BUCKETS
    selected_id = (
        canary_id
        if canary_id is not None and bucket < routing_state["canary_basis_points"]
        else stable_id
    )
    selected = deployments[selected_id]
    return {
        "routing_state_id": routing_state["routing_state_id"],
        "routing_key_sha256": sha256_bytes(resolved_key.encode("utf-8")),
        "bucket": bucket,
        "selected_role": "canary" if selected_id == canary_id else "stable",
        "deployment_id": selected_id,
        "generation": selected["generation"],
        "release_id": selected["release_id"],
        "model_sha256": selected["model"]["sha256"],
        "image_digest": selected["image"]["digest"],
    }


def build_rollback_state(
    *,
    current_state: Mapping[str, Any],
    target_stable: Mapping[str, Any],
    expected_current_state_id: str,
) -> dict[str, Any]:
    validate_routing_state(current_state)
    validate_deployment_manifest(target_stable)
    if current_state["routing_state_id"] != expected_current_state_id:
        raise ContractError("stale rollback subject")
    return build_routing_state(
        stable=target_stable,
        canary=None,
        canary_basis_points=0,
        current_state=current_state,
        expected_current_state_id=expected_current_state_id,
    )
