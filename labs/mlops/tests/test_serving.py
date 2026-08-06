from __future__ import annotations

import copy

import pytest

from mlops_lab.contracts import ContractError, canonical_json_bytes, sha256_bytes
from mlops_lab.registry import build_registry_evidence
from mlops_lab.serving import (
    build_deployment_manifest,
    build_rollback_state,
    build_routing_state,
    route_request,
    validate_deployment_manifest,
    validate_routing_state,
)


def _release(candidate_id: str = "a" * 64, model_sha256: str = "b" * 64) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": 1,
        "alias": "champion",
        "previous_candidate_id": None,
        "candidate_id": candidate_id,
        "dataset_sha256": "c" * 64,
        "model_sha256": model_sha256,
        "evaluation_sha256": "d" * 64,
        "policy_generation": "ml-training-manifest-v1",
        "source_revision": "exact-revision",
    }
    return {**payload, "release_id": sha256_bytes(canonical_json_bytes(payload))}


def _registry(candidate_id: str = "a" * 64, model_sha256: str = "b" * 64) -> dict[str, object]:
    return build_registry_evidence(
        tracking_uri="http://127.0.0.1:5000",
        experiment_id="1",
        run_id="run-1",
        logged_model_id="m-1",
        candidate_id=candidate_id,
        source_revision="exact-revision",
        model_name="KnowledgeHubChurn",
        version="1",
        alias="champion",
        alias_resolved_version="1",
        source_uri="models:/m-1",
        source_run_id="run-1",
        model_version_status="READY",
        model_version_tags={
            "knowledge_hub.candidate_id": candidate_id,
            "knowledge_hub.source_revision": "exact-revision",
            "knowledge_hub.model_sha256": model_sha256,
        },
        artifact_path="source/model.joblib",
        original_model_sha256=model_sha256,
        downloaded_model_sha256=model_sha256,
        model_size_bytes=123,
        request={"feature": 1},
        source_probability=0.75,
        source_prediction=1,
        registry_probability=0.75,
        registry_prediction=1,
        mlflow_version="3.14.0",
    )


def _deployment(generation: str, image_hex: str) -> dict[str, object]:
    return build_deployment_manifest(
        release=_release(),
        registry_evidence=_registry(),
        service_name="churn-api",
        generation=generation,
        image_reference="ghcr.io/example/churn-api",
        image_digest=f"sha256:{image_hex * 64}",
    )


def test_deployment_manifest_is_deterministic_and_pins_exact_subjects() -> None:
    first = _deployment("generation-1", "1")
    second = _deployment("generation-1", "1")
    assert first == second
    validate_deployment_manifest(first)
    assert first["model"]["exact_uri"] == "models:/KnowledgeHubChurn/1"
    assert "@" not in first["model"]["exact_uri"]
    assert first["image"]["digest"].startswith("sha256:")


def test_deployment_refuses_release_registry_candidate_mismatch() -> None:
    with pytest.raises(ContractError, match="release candidate"):
        build_deployment_manifest(
            release=_release(candidate_id="e" * 64),
            registry_evidence=_registry(candidate_id="a" * 64),
            service_name="churn-api",
            generation="generation-1",
            image_reference="ghcr.io/example/churn-api",
            image_digest="sha256:" + "1" * 64,
        )


def test_deployment_refuses_mutated_payload() -> None:
    deployment = _deployment("generation-1", "1")
    deployment["generation"] = "changed"
    with pytest.raises(ContractError, match="deployment_id"):
        validate_deployment_manifest(deployment)


def test_routing_is_deterministic_and_approximately_matches_canary_weight() -> None:
    stable = _deployment("generation-1", "1")
    canary = _deployment("generation-2", "2")
    initial = build_routing_state(
        stable=stable,
        canary=None,
        canary_basis_points=0,
        current_state=None,
        expected_current_state_id=None,
    )
    state = build_routing_state(
        stable=stable,
        canary=canary,
        canary_basis_points=1000,
        current_state=initial,
        expected_current_state_id=initial["routing_state_id"],
    )
    deployments = {
        stable["deployment_id"]: stable,
        canary["deployment_id"]: canary,
    }
    first = route_request(
        routing_state=state,
        deployments=deployments,
        routing_key="tenant-42/request-7",
    )
    second = route_request(
        routing_state=state,
        deployments=deployments,
        routing_key="tenant-42/request-7",
    )
    assert first == second

    selected_canary = sum(
        route_request(
            routing_state=state,
            deployments=deployments,
            routing_key=f"request-{index}",
        )["selected_role"]
        == "canary"
        for index in range(10_000)
    )
    assert 850 <= selected_canary <= 1150


def test_routing_update_refuses_stale_state() -> None:
    stable = _deployment("generation-1", "1")
    canary = _deployment("generation-2", "2")
    current = build_routing_state(
        stable=stable,
        canary=None,
        canary_basis_points=0,
        current_state=None,
        expected_current_state_id=None,
    )
    with pytest.raises(ContractError, match="stale routing update"):
        build_routing_state(
            stable=stable,
            canary=canary,
            canary_basis_points=500,
            current_state=current,
            expected_current_state_id="f" * 64,
        )


def test_rollback_restores_exact_deployment_without_alias_resolution() -> None:
    stable = _deployment("generation-1", "1")
    canary = _deployment("generation-2", "2")
    initial = build_routing_state(
        stable=stable,
        canary=None,
        canary_basis_points=0,
        current_state=None,
        expected_current_state_id=None,
    )
    canary_state = build_routing_state(
        stable=stable,
        canary=canary,
        canary_basis_points=2500,
        current_state=initial,
        expected_current_state_id=initial["routing_state_id"],
    )
    rollback = build_rollback_state(
        current_state=canary_state,
        target_stable=stable,
        expected_current_state_id=canary_state["routing_state_id"],
    )
    validate_routing_state(rollback)
    assert rollback["stable_deployment_id"] == stable["deployment_id"]
    assert rollback["canary_deployment_id"] is None
    assert rollback["canary_basis_points"] == 0
    assert rollback["previous_routing_state_id"] == canary_state["routing_state_id"]


def test_route_refuses_missing_deployment_subject() -> None:
    stable = _deployment("generation-1", "1")
    state = build_routing_state(
        stable=stable,
        canary=None,
        canary_basis_points=0,
        current_state=None,
        expected_current_state_id=None,
    )
    with pytest.raises(ContractError, match="does not contain"):
        route_request(
            routing_state=state,
            deployments={},
            routing_key="request-1",
        )
