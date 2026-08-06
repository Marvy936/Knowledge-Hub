from __future__ import annotations

import socket
import threading
import time
from contextlib import contextmanager

import uvicorn

from mlops_lab.canary import (
    build_canary_decision,
    execute_canary_window,
    rollback_from_canary_decision,
)
from mlops_lab.contracts import canonical_json_bytes, sha256_bytes
from mlops_lab.registry import build_registry_evidence
from mlops_lab.serving import build_deployment_manifest, build_routing_state
from mlops_lab.serving_app import ServingRuntime, create_app


FEATURE_COLUMNS = [
    "tenure_months",
    "monthly_spend_eur",
    "support_tickets_90d",
    "login_days_30d",
    "days_since_last_login",
    "contract_type",
    "region",
    "auto_pay",
]


class FakeModel:
    def __init__(self, probability: float) -> None:
        self.probability = probability

    def predict_proba(self, frame):
        assert list(frame.columns) == FEATURE_COLUMNS
        return [[1.0 - self.probability, self.probability]]


def _release() -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": 1,
        "alias": "champion",
        "previous_candidate_id": None,
        "candidate_id": "a" * 64,
        "dataset_sha256": "c" * 64,
        "model_sha256": "b" * 64,
        "evaluation_sha256": "d" * 64,
        "policy_generation": "ml-training-manifest-v1",
        "source_revision": "exact-revision",
    }
    return {**payload, "release_id": sha256_bytes(canonical_json_bytes(payload))}


def _registry() -> dict[str, object]:
    return build_registry_evidence(
        tracking_uri="http://127.0.0.1:5000",
        experiment_id="1",
        run_id="run-1",
        logged_model_id="m-1",
        candidate_id="a" * 64,
        source_revision="exact-revision",
        model_name="KnowledgeHubChurn",
        version="1",
        alias="champion",
        alias_resolved_version="1",
        source_uri="models:/m-1",
        source_run_id="run-1",
        model_version_status="READY",
        model_version_tags={
            "knowledge_hub.candidate_id": "a" * 64,
            "knowledge_hub.source_revision": "exact-revision",
            "knowledge_hub.model_sha256": "b" * 64,
        },
        artifact_path="source/model.joblib",
        original_model_sha256="b" * 64,
        downloaded_model_sha256="b" * 64,
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
        image_digest="sha256:" + image_hex * 64,
    )


def _runtime(deployment: dict[str, object], probability: float) -> ServingRuntime:
    return ServingRuntime(
        deployment=deployment,
        artifact_manifest={
            "feature_columns": FEATURE_COLUMNS,
            "decision_threshold": 0.72,
        },
        model=FakeModel(probability),
        validate_record=lambda record: None,
    )


def _record() -> dict[str, object]:
    return {
        "tenure_months": 18,
        "monthly_spend_eur": 84.5,
        "support_tickets_90d": 2,
        "login_days_30d": 12,
        "days_since_last_login": 5,
        "contract_type": "monthly",
        "region": "east",
        "auto_pay": "no",
    }


@contextmanager
def _live_server(runtime: ServingRuntime):
    socket_probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_probe.bind(("127.0.0.1", 0))
    port = socket_probe.getsockname()[1]
    socket_probe.close()

    server = uvicorn.Server(
        uvicorn.Config(
            create_app(runtime),
            host="127.0.0.1",
            port=port,
            log_level="critical",
            access_log=False,
        )
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 5.0
    while not server.started and thread.is_alive() and time.monotonic() < deadline:
        time.sleep(0.01)
    if not server.started:
        server.should_exit = True
        thread.join(timeout=2)
        raise RuntimeError("Uvicorn test server did not start")
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        assert not thread.is_alive()


def _subjects():
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
    deployments = {
        stable["deployment_id"]: stable,
        canary["deployment_id"]: canary,
    }
    return stable, canary, canary_state, deployments


def test_two_live_generations_produce_identity_bound_canary_evidence() -> None:
    stable, canary, routing_state, deployments = _subjects()
    requests = [(f"request-{index}", _record()) for index in range(100)]

    with _live_server(_runtime(stable, 0.40)) as stable_endpoint, _live_server(
        _runtime(canary, 0.82)
    ) as canary_endpoint:
        evidence = execute_canary_window(
            routing_state=routing_state,
            deployments=deployments,
            endpoints={
                stable["deployment_id"]: stable_endpoint,
                canary["deployment_id"]: canary_endpoint,
            },
            requests=requests,
        )

    assert evidence["total_requests"] == 100
    assert evidence["successful_requests"] == 100
    assert evidence["failed_requests"] == 0
    assert evidence["identity_mismatches"] == 0
    assert evidence["stable_requests"] + evidence["canary_requests"] == 100
    assert evidence["canary_requests"] >= 10
    assert evidence["latency_ms"]["p95"] is not None

    decision = build_canary_decision(
        evidence=evidence,
        expected_routing_state_id=routing_state["routing_state_id"],
        minimum_canary_requests=10,
        maximum_canary_error_rate=0.05,
    )
    assert decision["action"] == "continue"
    assert decision["observed_canary_error_rate"] == 0.0


def test_wrong_canary_endpoint_identity_authorizes_exact_rollback() -> None:
    stable, canary, routing_state, deployments = _subjects()
    requests = [(f"request-{index}", _record()) for index in range(100)]

    with _live_server(_runtime(stable, 0.40)) as stable_endpoint:
        evidence = execute_canary_window(
            routing_state=routing_state,
            deployments=deployments,
            endpoints={
                stable["deployment_id"]: stable_endpoint,
                canary["deployment_id"]: stable_endpoint,
            },
            requests=requests,
        )

    assert evidence["identity_mismatches"] > 0
    assert evidence["canary_failed_requests"] > 0
    decision = build_canary_decision(
        evidence=evidence,
        expected_routing_state_id=routing_state["routing_state_id"],
        minimum_canary_requests=10,
        maximum_canary_error_rate=0.05,
    )
    assert decision["action"] == "rollback"

    rollback = rollback_from_canary_decision(
        decision=decision,
        current_routing_state=routing_state,
        target_stable=stable,
    )
    assert rollback["stable_deployment_id"] == stable["deployment_id"]
    assert rollback["canary_deployment_id"] is None
    assert rollback["canary_basis_points"] == 0
    assert rollback["previous_routing_state_id"] == routing_state["routing_state_id"]


def test_no_data_and_insufficient_canary_are_not_success() -> None:
    stable, canary, routing_state, deployments = _subjects()
    endpoints = {
        stable["deployment_id"]: "http://127.0.0.1:1",
        canary["deployment_id"]: "http://127.0.0.1:2",
    }
    no_data = execute_canary_window(
        routing_state=routing_state,
        deployments=deployments,
        endpoints=endpoints,
        requests=[],
    )
    no_data_decision = build_canary_decision(
        evidence=no_data,
        expected_routing_state_id=routing_state["routing_state_id"],
        minimum_canary_requests=10,
        maximum_canary_error_rate=0.05,
    )
    assert no_data_decision["action"] == "no_data"

    with _live_server(_runtime(stable, 0.40)) as stable_endpoint, _live_server(
        _runtime(canary, 0.82)
    ) as canary_endpoint:
        sparse = execute_canary_window(
            routing_state=routing_state,
            deployments=deployments,
            endpoints={
                stable["deployment_id"]: stable_endpoint,
                canary["deployment_id"]: canary_endpoint,
            },
            requests=[("single-request", _record())],
        )
    sparse_decision = build_canary_decision(
        evidence=sparse,
        expected_routing_state_id=routing_state["routing_state_id"],
        minimum_canary_requests=10,
        maximum_canary_error_rate=0.05,
    )
    assert sparse_decision["action"] == "insufficient_evidence"
