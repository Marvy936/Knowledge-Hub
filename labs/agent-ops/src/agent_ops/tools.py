from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Protocol

from .contracts import (
    AgentContractError,
    atomic_write_json,
    canonical_json_bytes,
    read_json,
    require_exact_keys,
    require_nonempty,
    require_sha256,
    sha256_bytes,
    validate_canonical_id,
)
from .planning import AGENT_SCHEMA_VERSION

LOOKUP_STATUSES = {"completed", "not_found", "unknown"}


class UnknownToolOutcome(RuntimeError):
    """Raised when a remote/local mutation may have happened but cannot be proven."""


class MutationToolAdapter(Protocol):
    def lookup(self, operation_id: str) -> Mapping[str, Any]: ...

    def execute(
        self,
        *,
        operation_id: str,
        action_digest: str,
        tool: str,
        target: str,
        arguments: Mapping[str, Any],
    ) -> Mapping[str, Any]: ...


def build_lookup(*, status: str, result: Mapping[str, Any] | None) -> dict[str, Any]:
    if status not in LOOKUP_STATUSES:
        raise AgentContractError("tool lookup status is unsupported")
    if status == "completed" and not isinstance(result, Mapping):
        raise AgentContractError("completed tool lookup requires result")
    if status != "completed" and result is not None:
        raise AgentContractError("non-completed tool lookup must not contain result")
    payload = {
        "schema_version": AGENT_SCHEMA_VERSION,
        "status": status,
        "result": None if result is None else dict(result),
    }
    return {**payload, "lookup_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_lookup(value: Mapping[str, Any]) -> None:
    require_exact_keys(
        value,
        {"schema_version", "status", "result", "lookup_id"},
        "tool lookup",
    )
    if value.get("schema_version") != AGENT_SCHEMA_VERSION:
        raise AgentContractError("tool lookup schema_version must equal 1")
    if value.get("status") not in LOOKUP_STATUSES:
        raise AgentContractError("tool lookup status is unsupported")
    result = value.get("result")
    if value["status"] == "completed":
        if not isinstance(result, dict):
            raise AgentContractError("completed tool lookup requires result object")
        validate_tool_result(result)
    elif result is not None:
        raise AgentContractError("non-completed lookup must not contain result")
    validate_canonical_id(value, "lookup_id")


def build_tool_result(
    *,
    operation_id: str,
    action_digest: str,
    tool: str,
    target: str,
    output: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": AGENT_SCHEMA_VERSION,
        "operation_id": require_sha256(operation_id, "tool_result.operation_id"),
        "action_digest": require_sha256(action_digest, "tool_result.action_digest"),
        "tool": require_nonempty(tool, "tool_result.tool"),
        "target": require_nonempty(target, "tool_result.target"),
        "status": "completed",
        "output": dict(output),
    }
    return {**payload, "result_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_tool_result(value: Mapping[str, Any]) -> None:
    require_exact_keys(
        value,
        {
            "schema_version",
            "operation_id",
            "action_digest",
            "tool",
            "target",
            "status",
            "output",
            "result_id",
        },
        "tool result",
    )
    if value.get("schema_version") != AGENT_SCHEMA_VERSION:
        raise AgentContractError("tool result schema_version must equal 1")
    require_sha256(value.get("operation_id"), "tool_result.operation_id")
    require_sha256(value.get("action_digest"), "tool_result.action_digest")
    require_nonempty(value.get("tool"), "tool_result.tool")
    require_nonempty(value.get("target"), "tool_result.target")
    if value.get("status") != "completed":
        raise AgentContractError("tool result status must equal completed")
    if not isinstance(value.get("output"), dict):
        raise AgentContractError("tool result output must be an object")
    validate_canonical_id(value, "result_id")


def validate_result_against_action(
    value: Mapping[str, Any],
    *,
    operation_id: str,
    action_digest: str,
    tool: str,
    target: str,
) -> None:
    validate_tool_result(value)
    expected = {
        "operation_id": operation_id,
        "action_digest": action_digest,
        "tool": tool,
        "target": target,
    }
    for field, subject in expected.items():
        if value[field] != subject:
            raise AgentContractError(f"tool result {field} does not match operation")


class LocalServiceStateAdapter:
    """A local-only idempotent mutation adapter for Practical v1 source tests."""

    def __init__(self, state_path: Path) -> None:
        self.state_path = state_path

    def _state(self) -> dict[str, Any]:
        value = read_json(self.state_path)
        if set(value) != {"schema_version", "services", "operations"}:
            raise AgentContractError("local service state keys mismatch")
        if value.get("schema_version") != 1:
            raise AgentContractError("local service state schema_version must equal 1")
        if not isinstance(value.get("services"), dict) or not isinstance(
            value.get("operations"), dict
        ):
            raise AgentContractError("local service state maps are invalid")
        return value

    def lookup(self, operation_id: str) -> Mapping[str, Any]:
        require_sha256(operation_id, "operation_id")
        state = self._state()
        result = state["operations"].get(operation_id)
        if result is None:
            return build_lookup(status="not_found", result=None)
        if not isinstance(result, dict):
            raise AgentContractError("stored operation result must be an object")
        validate_tool_result(result)
        return build_lookup(status="completed", result=result)

    def execute(
        self,
        *,
        operation_id: str,
        action_digest: str,
        tool: str,
        target: str,
        arguments: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        if tool != "restart_service":
            raise AgentContractError("local adapter supports only restart_service mutation")
        state = self._state()
        existing = state["operations"].get(operation_id)
        if existing is not None:
            validate_result_against_action(
                existing,
                operation_id=operation_id,
                action_digest=action_digest,
                tool=tool,
                target=target,
            )
            return existing
        service = state["services"].get(target)
        if not isinstance(service, dict):
            raise AgentContractError("target service does not exist in local sandbox")
        if set(service) != {"generation", "status", "restart_count"}:
            raise AgentContractError("local service record keys mismatch")
        expected_generation = arguments.get("expected_generation")
        if set(arguments) != {"expected_generation"}:
            raise AgentContractError("restart_service arguments are invalid")
        if service.get("generation") != expected_generation:
            raise AgentContractError("service generation changed since action approval")
        if service.get("status") != "degraded":
            raise AgentContractError("restart_service requires degraded service status")
        restart_count = service.get("restart_count")
        if isinstance(restart_count, bool) or not isinstance(restart_count, int):
            raise AgentContractError("service restart_count is invalid")
        next_service = {
            "generation": expected_generation + 1,
            "status": "healthy",
            "restart_count": restart_count + 1,
        }
        result = build_tool_result(
            operation_id=operation_id,
            action_digest=action_digest,
            tool=tool,
            target=target,
            output={
                "previous_generation": expected_generation,
                "current_generation": expected_generation + 1,
                "status": "healthy",
            },
        )
        next_services = dict(state["services"])
        next_services[target] = next_service
        next_operations = dict(state["operations"])
        next_operations[operation_id] = result
        atomic_write_json(
            self.state_path,
            {
                "schema_version": 1,
                "services": next_services,
                "operations": next_operations,
            },
        )
        return result
