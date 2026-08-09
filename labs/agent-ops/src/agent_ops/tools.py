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
from .planning import AGENT_SCHEMA_VERSION, build_service_inspection

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


def _validate_restart_output(output: Mapping[str, Any]) -> None:
    if not isinstance(output, Mapping):
        raise AgentContractError("restart_service output must be an object")
    require_exact_keys(
        output,
        {"previous_generation", "current_generation", "status"},
        "restart_service output",
    )
    previous = output.get("previous_generation")
    current = output.get("current_generation")
    if isinstance(previous, bool) or not isinstance(previous, int) or previous < 1:
        raise AgentContractError("restart_service previous_generation is invalid")
    if isinstance(current, bool) or not isinstance(current, int):
        raise AgentContractError("restart_service current_generation is invalid")
    if current != previous + 1:
        raise AgentContractError(
            "restart_service current_generation must equal previous_generation + 1"
        )
    if output.get("status") != "healthy":
        raise AgentContractError("restart_service output status must equal healthy")


def build_tool_result(
    *,
    operation_id: str,
    action_digest: str,
    tool: str,
    target: str,
    output: Mapping[str, Any],
) -> dict[str, Any]:
    resolved_tool = require_nonempty(tool, "tool_result.tool")
    if resolved_tool != "restart_service":
        raise AgentContractError("generation-1 tool result supports only restart_service")
    _validate_restart_output(output)
    payload = {
        "schema_version": AGENT_SCHEMA_VERSION,
        "operation_id": require_sha256(operation_id, "tool_result.operation_id"),
        "action_digest": require_sha256(action_digest, "tool_result.action_digest"),
        "tool": resolved_tool,
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
    if value.get("tool") != "restart_service":
        raise AgentContractError("generation-1 tool result supports only restart_service")
    require_nonempty(value.get("target"), "tool_result.target")
    if value.get("status") != "completed":
        raise AgentContractError("tool result status must equal completed")
    output = value.get("output")
    if not isinstance(output, dict):
        raise AgentContractError("tool result output must be an object")
    _validate_restart_output(output)
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
    """A local-only typed inspection and idempotent mutation adapter for Practical v1."""

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

    @staticmethod
    def _validate_service_record(service: Mapping[str, Any]) -> None:
        if set(service) != {"generation", "status", "restart_count"}:
            raise AgentContractError("local service record keys mismatch")
        generation = service.get("generation")
        if isinstance(generation, bool) or not isinstance(generation, int) or generation < 1:
            raise AgentContractError("local service generation is invalid")
        if service.get("status") not in {"healthy", "degraded", "unknown"}:
            raise AgentContractError("local service status is unsupported")
        restart_count = service.get("restart_count")
        if (
            isinstance(restart_count, bool)
            or not isinstance(restart_count, int)
            or restart_count < 0
        ):
            raise AgentContractError("service restart_count is invalid")

    def inspect(self, target: str) -> Mapping[str, Any]:
        resolved_target = require_nonempty(target, "inspection.target")
        state = self._state()
        service = state["services"].get(resolved_target)
        if not isinstance(service, dict):
            raise AgentContractError("target service does not exist in local sandbox")
        self._validate_service_record(service)
        return build_service_inspection(
            target=resolved_target,
            service_generation=service["generation"],
            service_status=service["status"],
        )

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
        self._validate_service_record(service)
        expected_generation = arguments.get("expected_generation")
        if set(arguments) != {"expected_generation"}:
            raise AgentContractError("restart_service arguments are invalid")
        if service.get("generation") != expected_generation:
            raise AgentContractError("service generation changed since action approval")
        if service.get("status") != "degraded":
            raise AgentContractError("restart_service requires degraded service status")
        restart_count = service["restart_count"]
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
