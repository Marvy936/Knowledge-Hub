from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any, Iterable, Mapping

from .contracts import ContractError, canonical_json_bytes, sha256_bytes
from .serving import (
    build_rollback_state,
    route_request,
    validate_deployment_manifest,
    validate_routing_state,
)

CANARY_SCHEMA_VERSION = 1


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


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((len(ordered) - 1) * percentile)))
    return round(ordered[index], 3)


def _post_prediction(
    *,
    endpoint: str,
    record: Mapping[str, Any],
    timeout_seconds: float,
) -> tuple[int, Mapping[str, Any], float]:
    payload = canonical_json_bytes(record)
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/v1/predict",
        data=payload,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "knowledge-hub-mlops-canary",
        },
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read()
            status = response.status
    except urllib.error.HTTPError as exc:
        body = exc.read()
        status = exc.code
    latency_ms = round((time.perf_counter() - started) * 1000.0, 3)
    try:
        decoded = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError("serving endpoint returned invalid JSON") from exc
    if not isinstance(decoded, dict):
        raise ContractError("serving endpoint response must be a JSON object")
    return status, decoded, latency_ms


def execute_canary_window(
    *,
    routing_state: Mapping[str, Any],
    deployments: Mapping[str, Mapping[str, Any]],
    endpoints: Mapping[str, str],
    requests: Iterable[tuple[str, Mapping[str, Any]]],
    timeout_seconds: float = 3.0,
) -> dict[str, Any]:
    validate_routing_state(routing_state)
    if timeout_seconds <= 0:
        raise ContractError("timeout_seconds must be positive")

    referenced_ids = {routing_state["stable_deployment_id"]}
    if routing_state["canary_deployment_id"] is not None:
        referenced_ids.add(routing_state["canary_deployment_id"])
    if set(deployments) != referenced_ids:
        raise ContractError("deployment map must contain exactly the routing subjects")
    if set(endpoints) != referenced_ids:
        raise ContractError("endpoint map must contain exactly the routing subjects")
    for deployment_id in sorted(referenced_ids):
        deployment = deployments[deployment_id]
        validate_deployment_manifest(deployment)
        if deployment["deployment_id"] != deployment_id:
            raise ContractError("deployment map key does not match deployment_id")
        endpoint = _require_nonempty_string(
            endpoints[deployment_id], f"endpoint[{deployment_id}]"
        )
        if not endpoint.startswith(("http://127.0.0.1:", "http://localhost:")):
            raise ContractError("canary harness only permits loopback HTTP endpoints")

    observations: list[dict[str, Any]] = []
    latencies: list[float] = []
    for routing_key, record in requests:
        if not isinstance(record, Mapping):
            raise ContractError("canary request record must be an object")
        decision = route_request(
            routing_state=routing_state,
            deployments=deployments,
            routing_key=routing_key,
        )
        deployment = deployments[decision["deployment_id"]]
        observation: dict[str, Any] = {
            "routing_key_sha256": decision["routing_key_sha256"],
            "request_sha256": sha256_bytes(canonical_json_bytes(record)),
            "selected_role": decision["selected_role"],
            "expected_deployment_id": decision["deployment_id"],
            "http_status": None,
            "success": False,
            "identity_match": False,
            "latency_ms": None,
            "error": None,
        }
        try:
            status, response, latency_ms = _post_prediction(
                endpoint=endpoints[decision["deployment_id"]],
                record=record,
                timeout_seconds=timeout_seconds,
            )
            latencies.append(latency_ms)
            observation["http_status"] = status
            observation["latency_ms"] = latency_ms
            identity_match = all(
                response.get(field) == expected
                for field, expected in {
                    "deployment_id": deployment["deployment_id"],
                    "generation": deployment["generation"],
                    "release_id": deployment["release_id"],
                    "model_sha256": deployment["model"]["sha256"],
                    "image_digest": deployment["image"]["digest"],
                }.items()
            )
            observation["identity_match"] = identity_match
            observation["success"] = status == 200 and identity_match
            if status != 200:
                observation["error"] = "http_error"
            elif not identity_match:
                observation["error"] = "identity_mismatch"
        except (ContractError, urllib.error.URLError, TimeoutError) as exc:
            observation["error"] = type(exc).__name__
        observations.append(observation)

    total = len(observations)
    stable_observations = [item for item in observations if item["selected_role"] == "stable"]
    canary_observations = [item for item in observations if item["selected_role"] == "canary"]
    successful = sum(item["success"] is True for item in observations)
    identity_mismatches = sum(
        item["http_status"] == 200 and item["identity_match"] is False
        for item in observations
    )
    payload = {
        "schema_version": CANARY_SCHEMA_VERSION,
        "routing_state_id": routing_state["routing_state_id"],
        "service_name": routing_state["service_name"],
        "total_requests": total,
        "stable_requests": len(stable_observations),
        "canary_requests": len(canary_observations),
        "successful_requests": successful,
        "failed_requests": total - successful,
        "stable_failed_requests": sum(
            item["success"] is False for item in stable_observations
        ),
        "canary_failed_requests": sum(
            item["success"] is False for item in canary_observations
        ),
        "identity_mismatches": identity_mismatches,
        "no_data": total == 0,
        "latency_ms": {
            "minimum": None if not latencies else round(min(latencies), 3),
            "average": None
            if not latencies
            else round(sum(latencies) / len(latencies), 3),
            "p95": _percentile(latencies, 0.95),
            "maximum": None if not latencies else round(max(latencies), 3),
        },
        "observations": observations,
    }
    evidence = {
        **payload,
        "canary_window_id": sha256_bytes(canonical_json_bytes(payload)),
    }
    validate_canary_evidence(evidence)
    return evidence


def validate_canary_evidence(value: Mapping[str, Any]) -> None:
    _require_exact_keys(
        value,
        {
            "schema_version",
            "routing_state_id",
            "service_name",
            "total_requests",
            "stable_requests",
            "canary_requests",
            "successful_requests",
            "failed_requests",
            "stable_failed_requests",
            "canary_failed_requests",
            "identity_mismatches",
            "no_data",
            "latency_ms",
            "observations",
            "canary_window_id",
        },
        "canary evidence",
    )
    if value.get("schema_version") != CANARY_SCHEMA_VERSION:
        raise ContractError("canary evidence schema_version must equal 1")
    _require_sha256(value.get("routing_state_id"), "canary.routing_state_id")
    _require_nonempty_string(value.get("service_name"), "canary.service_name")
    count_fields = (
        "total_requests",
        "stable_requests",
        "canary_requests",
        "successful_requests",
        "failed_requests",
        "stable_failed_requests",
        "canary_failed_requests",
        "identity_mismatches",
    )
    for field in count_fields:
        if not isinstance(value.get(field), int) or isinstance(value.get(field), bool):
            raise ContractError(f"canary.{field} must be an integer")
        if value[field] < 0:
            raise ContractError(f"canary.{field} must be non-negative")
    if value["stable_requests"] + value["canary_requests"] != value["total_requests"]:
        raise ContractError("canary role counts do not equal total_requests")
    if value["successful_requests"] + value["failed_requests"] != value["total_requests"]:
        raise ContractError("canary outcome counts do not equal total_requests")
    if value["stable_failed_requests"] + value["canary_failed_requests"] != value["failed_requests"]:
        raise ContractError("canary failure counts do not equal failed_requests")
    if value.get("no_data") is not (value["total_requests"] == 0):
        raise ContractError("canary no_data state does not match request count")
    if not isinstance(value.get("latency_ms"), dict):
        raise ContractError("canary latency_ms must be an object")
    if not isinstance(value.get("observations"), list):
        raise ContractError("canary observations must be a list")
    if len(value["observations"]) != value["total_requests"]:
        raise ContractError("canary observation count does not match total_requests")
    window_id = _require_sha256(value.get("canary_window_id"), "canary_window_id")
    payload = {key: item for key, item in value.items() if key != "canary_window_id"}
    if sha256_bytes(canonical_json_bytes(payload)) != window_id:
        raise ContractError("canary_window_id does not match canonical evidence")


def build_canary_decision(
    *,
    evidence: Mapping[str, Any],
    expected_routing_state_id: str,
    minimum_canary_requests: int,
    maximum_canary_error_rate: float,
) -> dict[str, Any]:
    validate_canary_evidence(evidence)
    _require_sha256(expected_routing_state_id, "expected_routing_state_id")
    if evidence["routing_state_id"] != expected_routing_state_id:
        raise ContractError("canary evidence belongs to another routing state")
    if not isinstance(minimum_canary_requests, int) or minimum_canary_requests < 1:
        raise ContractError("minimum_canary_requests must be a positive integer")
    if not isinstance(maximum_canary_error_rate, (int, float)) or isinstance(
        maximum_canary_error_rate, bool
    ):
        raise ContractError("maximum_canary_error_rate must be numeric")
    threshold = float(maximum_canary_error_rate)
    if not 0.0 <= threshold <= 1.0:
        raise ContractError("maximum_canary_error_rate must be between 0 and 1")

    if evidence["no_data"]:
        action = "no_data"
        reason = "no requests were observed"
        canary_error_rate = None
    elif evidence["canary_requests"] < minimum_canary_requests:
        action = "insufficient_evidence"
        reason = "minimum canary request count was not reached"
        canary_error_rate = (
            None
            if evidence["canary_requests"] == 0
            else evidence["canary_failed_requests"] / evidence["canary_requests"]
        )
    else:
        canary_error_rate = (
            evidence["canary_failed_requests"] / evidence["canary_requests"]
        )
        if evidence["identity_mismatches"] > 0:
            action = "rollback"
            reason = "serving response identity did not match the routed deployment"
        elif canary_error_rate > threshold:
            action = "rollback"
            reason = "canary error rate exceeded the configured threshold"
        else:
            action = "continue"
            reason = "canary evidence satisfied the configured gates"

    payload = {
        "schema_version": CANARY_SCHEMA_VERSION,
        "canary_window_id": evidence["canary_window_id"],
        "routing_state_id": evidence["routing_state_id"],
        "minimum_canary_requests": minimum_canary_requests,
        "maximum_canary_error_rate": threshold,
        "observed_canary_requests": evidence["canary_requests"],
        "observed_canary_error_rate": None
        if canary_error_rate is None
        else round(canary_error_rate, 6),
        "identity_mismatches": evidence["identity_mismatches"],
        "action": action,
        "reason": reason,
    }
    return {
        **payload,
        "canary_decision_id": sha256_bytes(canonical_json_bytes(payload)),
    }


def rollback_from_canary_decision(
    *,
    decision: Mapping[str, Any],
    current_routing_state: Mapping[str, Any],
    target_stable: Mapping[str, Any],
) -> dict[str, Any]:
    if decision.get("action") != "rollback":
        raise ContractError("canary decision does not authorize rollback")
    if decision.get("routing_state_id") != current_routing_state.get(
        "routing_state_id"
    ):
        raise ContractError("canary decision does not match current routing state")
    return build_rollback_state(
        current_state=current_routing_state,
        target_stable=target_stable,
        expected_current_state_id=current_routing_state["routing_state_id"],
    )
