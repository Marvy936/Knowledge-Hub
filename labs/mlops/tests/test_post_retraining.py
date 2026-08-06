from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from mlops_lab.contracts import (
    ContractError,
    canonical_json_bytes,
    read_json,
    sha256_bytes,
)
from mlops_lab.post_retraining import (
    build_post_retraining_handoff,
    validate_post_retraining_handoff,
)

from test_controlled_retraining import _execute, _inputs, _registry, _train


def _routing(current_deployment):
    payload = {
        "schema_version": 1,
        "service_name": current_deployment["service_name"],
        "stable_deployment_id": current_deployment["deployment_id"],
        "canary_deployment_id": None,
        "canary_basis_points": 0,
        "previous_routing_state_id": None,
    }
    return {
        **payload,
        "routing_state_id": sha256_bytes(canonical_json_bytes(payload)),
    }


def _completed(tmp_path: Path):
    args = _inputs(tmp_path)
    result = _execute(args, _train([]), _registry([]))
    output = tmp_path / "output"
    return (
        args[6],
        result["state"],
        read_json(output / "release.json"),
        read_json(output / "registry-evidence.json"),
        args[0],
        _routing(args[0]),
    )


def _handoff(tmp_path: Path):
    operation, state, release, registry, current, routing = _completed(tmp_path)
    return build_post_retraining_handoff(
        operation=operation,
        completed_state=state,
        release=release,
        registry_evidence=registry,
        current_deployment=current,
        current_routing_state=routing,
        service_name=current["service_name"],
        generation="canary-2",
        image_reference="example/churn:2",
        image_digest="sha256:" + "8" * 64,
        canary_basis_points=1000,
        expected_current_routing_state_id=routing["routing_state_id"],
    )


def test_completed_retraining_builds_exact_canary_handoff(
    tmp_path: Path,
) -> None:
    handoff = _handoff(tmp_path)
    validate_post_retraining_handoff(handoff)
    assert handoff["routing_state"]["canary_basis_points"] == 1000
    assert (
        handoff["routing_state"]["canary_deployment_id"]
        == handoff["deployment"]["deployment_id"]
    )
    assert handoff["deployment"]["model"]["registry_version"] == "2"


def test_incomplete_state_is_refused(tmp_path: Path) -> None:
    operation, state, release, registry, current, routing = _completed(tmp_path)
    state = deepcopy(state)
    state["phase"] = "registry_recorded"
    payload = {key: item for key, item in state.items() if key != "state_id"}
    state["state_id"] = sha256_bytes(canonical_json_bytes(payload))

    with pytest.raises(ContractError, match="completed operation"):
        build_post_retraining_handoff(
            operation=operation,
            completed_state=state,
            release=release,
            registry_evidence=registry,
            current_deployment=current,
            current_routing_state=routing,
            service_name=current["service_name"],
            generation="canary-2",
            image_reference="example/churn:2",
            image_digest="sha256:" + "8" * 64,
            canary_basis_points=1000,
            expected_current_routing_state_id=routing["routing_state_id"],
        )


def test_release_must_advance_current_candidate(tmp_path: Path) -> None:
    operation, state, release, registry, current, routing = _completed(tmp_path)
    release = deepcopy(release)
    release["previous_candidate_id"] = "f" * 64
    payload = {
        key: item for key, item in release.items() if key != "release_id"
    }
    release["release_id"] = sha256_bytes(canonical_json_bytes(payload))
    state = deepcopy(state)
    state["artifacts"]["release_id"] = release["release_id"]
    state_payload = {
        key: item for key, item in state.items() if key != "state_id"
    }
    state["state_id"] = sha256_bytes(canonical_json_bytes(state_payload))

    with pytest.raises(ContractError, match="advance the current"):
        build_post_retraining_handoff(
            operation=operation,
            completed_state=state,
            release=release,
            registry_evidence=registry,
            current_deployment=current,
            current_routing_state=routing,
            service_name=current["service_name"],
            generation="canary-2",
            image_reference="example/churn:2",
            image_digest="sha256:" + "8" * 64,
            canary_basis_points=1000,
            expected_current_routing_state_id=routing["routing_state_id"],
        )


def test_existing_canary_and_stale_routing_are_refused(
    tmp_path: Path,
) -> None:
    operation, state, release, registry, current, routing = _completed(tmp_path)
    existing = deepcopy(routing)
    existing["canary_deployment_id"] = "e" * 64
    existing["canary_basis_points"] = 100
    payload = {
        key: item
        for key, item in existing.items()
        if key != "routing_state_id"
    }
    existing["routing_state_id"] = sha256_bytes(canonical_json_bytes(payload))

    with pytest.raises(ContractError, match="existing canary"):
        build_post_retraining_handoff(
            operation=operation,
            completed_state=state,
            release=release,
            registry_evidence=registry,
            current_deployment=current,
            current_routing_state=existing,
            service_name=current["service_name"],
            generation="canary-2",
            image_reference="example/churn:2",
            image_digest="sha256:" + "8" * 64,
            canary_basis_points=1000,
            expected_current_routing_state_id=existing["routing_state_id"],
        )

    with pytest.raises(ContractError, match="stale"):
        build_post_retraining_handoff(
            operation=operation,
            completed_state=state,
            release=release,
            registry_evidence=registry,
            current_deployment=current,
            current_routing_state=routing,
            service_name=current["service_name"],
            generation="canary-2",
            image_reference="example/churn:2",
            image_digest="sha256:" + "8" * 64,
            canary_basis_points=1000,
            expected_current_routing_state_id="d" * 64,
        )


def test_handoff_tampering_is_detected(tmp_path: Path) -> None:
    handoff = _handoff(tmp_path)
    handoff["routing_state"]["canary_basis_points"] = 2000
    with pytest.raises(ContractError):
        validate_post_retraining_handoff(handoff)
