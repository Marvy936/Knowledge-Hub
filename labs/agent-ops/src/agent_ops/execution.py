from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

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
from .planning import (
    AGENT_SCHEMA_VERSION,
    validate_action_plan,
    validate_agent_policy,
    validate_diagnostic_snapshot,
    validate_incident,
)
from .safety import (
    validate_approval_against_plan,
    validate_kill_switch,
)
from .tools import (
    MutationToolAdapter,
    UnknownToolOutcome,
    validate_lookup,
    validate_result_against_action,
    validate_tool_result,
)

PHASES = {"planned", "tool_started", "completed", "failed", "unknown_outcome"}


def build_operation(
    *,
    incident: Mapping[str, Any],
    diagnostic: Mapping[str, Any],
    plan: Mapping[str, Any],
    approval: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    validate_incident(incident)
    validate_diagnostic_snapshot(diagnostic)
    validate_action_plan(plan)
    validate_agent_policy(policy)
    validate_approval_against_plan(approval=approval, plan=plan, policy=policy)
    if diagnostic["incident_id"] != incident["incident_id"]:
        raise AgentContractError("diagnostic belongs to another incident")
    if plan["incident_id"] != incident["incident_id"]:
        raise AgentContractError("action plan belongs to another incident")
    if plan["diagnostic_id"] != diagnostic["diagnostic_id"]:
        raise AgentContractError("action plan belongs to another diagnostic snapshot")
    if plan["disposition"] != "approval_required":
        raise AgentContractError("only approval-required mutation plans create operations")
    payload = {
        "schema_version": AGENT_SCHEMA_VERSION,
        "incident_id": incident["incident_id"],
        "diagnostic_id": diagnostic["diagnostic_id"],
        "plan_id": plan["plan_id"],
        "approval_id": approval["approval_id"],
        "policy_id": policy["policy_id"],
        "policy_generation": policy["generation"],
        "action_digest": plan["action_digest"],
        "tool": plan["tool"],
        "target": plan["target"],
        "arguments": dict(plan["arguments"]),
    }
    return {**payload, "operation_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_operation(value: Mapping[str, Any]) -> None:
    require_exact_keys(
        value,
        {
            "schema_version",
            "incident_id",
            "diagnostic_id",
            "plan_id",
            "approval_id",
            "policy_id",
            "policy_generation",
            "action_digest",
            "tool",
            "target",
            "arguments",
            "operation_id",
        },
        "agent operation",
    )
    if value.get("schema_version") != AGENT_SCHEMA_VERSION:
        raise AgentContractError("agent operation schema_version must equal 1")
    for field in (
        "incident_id",
        "diagnostic_id",
        "plan_id",
        "approval_id",
        "policy_id",
        "action_digest",
    ):
        require_sha256(value.get(field), f"operation.{field}")
    require_nonempty(value.get("policy_generation"), "operation.policy_generation")
    if value.get("tool") != "restart_service":
        raise AgentContractError("agent operation tool must equal restart_service")
    require_nonempty(value.get("target"), "operation.target")
    arguments = value.get("arguments")
    if not isinstance(arguments, dict) or set(arguments) != {"expected_generation"}:
        raise AgentContractError("agent operation arguments are invalid")
    generation = arguments["expected_generation"]
    if isinstance(generation, bool) or not isinstance(generation, int) or generation < 1:
        raise AgentContractError("operation expected_generation is invalid")
    validate_canonical_id(value, "operation_id")


def _empty_state(
    *, operation_id: str, phase: str, attempt: int, previous_state_id: str | None
) -> dict[str, Any]:
    payload = {
        "schema_version": AGENT_SCHEMA_VERSION,
        "operation_id": operation_id,
        "phase": phase,
        "attempt": attempt,
        "previous_state_id": previous_state_id,
        "lookup_id": None,
        "result_id": None,
        "failure": None,
    }
    return {**payload, "state_id": sha256_bytes(canonical_json_bytes(payload))}


def _transition(
    current: Mapping[str, Any],
    *,
    phase: str,
    lookup_id: str | None = None,
    result_id: str | None = None,
    failure: str | None = None,
    increment_attempt: bool = False,
) -> dict[str, Any]:
    validate_execution_state(current)
    payload = {
        "schema_version": AGENT_SCHEMA_VERSION,
        "operation_id": current["operation_id"],
        "phase": phase,
        "attempt": current["attempt"] + (1 if increment_attempt else 0),
        "previous_state_id": current["state_id"],
        "lookup_id": lookup_id,
        "result_id": result_id,
        "failure": failure,
    }
    state = {**payload, "state_id": sha256_bytes(canonical_json_bytes(payload))}
    validate_execution_state(state)
    return state


def validate_execution_state(value: Mapping[str, Any]) -> None:
    require_exact_keys(
        value,
        {
            "schema_version",
            "operation_id",
            "phase",
            "attempt",
            "previous_state_id",
            "lookup_id",
            "result_id",
            "failure",
            "state_id",
        },
        "execution state",
    )
    if value.get("schema_version") != AGENT_SCHEMA_VERSION:
        raise AgentContractError("execution state schema_version must equal 1")
    require_sha256(value.get("operation_id"), "state.operation_id")
    phase = require_nonempty(value.get("phase"), "state.phase")
    if phase not in PHASES:
        raise AgentContractError("execution state phase is unsupported")
    attempt = value.get("attempt")
    if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 1:
        raise AgentContractError("execution state attempt must be positive")
    for field in ("previous_state_id", "lookup_id", "result_id"):
        item = value.get(field)
        if item is not None:
            require_sha256(item, f"state.{field}")
    failure = value.get("failure")
    if phase in {"failed", "unknown_outcome"}:
        require_nonempty(failure, "state.failure")
    elif failure is not None:
        raise AgentContractError("state failure must be null outside failed/unknown phase")
    if phase == "completed" and value.get("result_id") is None:
        raise AgentContractError("completed state requires result_id")
    validate_canonical_id(value, "state_id")


def _acquire_lock(path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        return os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise AgentContractError("agent operation is already locked") from exc


def _write_state(path: Path, state: Mapping[str, Any]) -> dict[str, Any]:
    validate_execution_state(state)
    atomic_write_json(path, state)
    return dict(state)


def _validate_operation_inputs(
    *,
    operation: Mapping[str, Any],
    incident: Mapping[str, Any],
    diagnostic: Mapping[str, Any],
    plan: Mapping[str, Any],
    approval: Mapping[str, Any],
    policy: Mapping[str, Any],
    kill_switch: Mapping[str, Any],
) -> None:
    expected = build_operation(
        incident=incident,
        diagnostic=diagnostic,
        plan=plan,
        approval=approval,
        policy=policy,
    )
    if dict(operation) != expected:
        raise AgentContractError("operation does not match authoritative input rebuild")
    validate_kill_switch(kill_switch)
    if kill_switch["engaged"] is True:
        raise AgentContractError("agent mutation kill switch is engaged")
    if operation["tool"] not in policy["allowed_tools"]:
        raise AgentContractError("operation tool is outside policy allowlist")
    if operation["target"] not in policy["allowed_targets"]:
        raise AgentContractError("operation target is outside policy allowlist")


def execute_operation(
    *,
    operation: Mapping[str, Any],
    incident: Mapping[str, Any],
    diagnostic: Mapping[str, Any],
    plan: Mapping[str, Any],
    approval: Mapping[str, Any],
    policy: Mapping[str, Any],
    kill_switch: Mapping[str, Any],
    adapter: MutationToolAdapter,
    state_path: Path,
    result_path: Path,
    recover_expected_state_id: str | None = None,
) -> dict[str, Any]:
    _validate_operation_inputs(
        operation=operation,
        incident=incident,
        diagnostic=diagnostic,
        plan=plan,
        approval=approval,
        policy=policy,
        kill_switch=kill_switch,
    )
    lock_path = state_path.with_suffix(state_path.suffix + ".lock")
    descriptor = _acquire_lock(lock_path)
    current: dict[str, Any] | None = None
    try:
        if state_path.is_file():
            current = read_json(state_path)
            validate_execution_state(current)
            if current["operation_id"] != operation["operation_id"]:
                raise AgentContractError("execution state belongs to another operation")
            if current["phase"] == "completed":
                result = read_json(result_path)
                validate_result_against_action(
                    result,
                    operation_id=operation["operation_id"],
                    action_digest=operation["action_digest"],
                    tool=operation["tool"],
                    target=operation["target"],
                )
                if result["result_id"] != current["result_id"]:
                    raise AgentContractError("completed state result read-back mismatch")
                return {"status": "already_completed", "state": current, "result": result}
            if recover_expected_state_id is None:
                raise AgentContractError(
                    "incomplete agent operation requires exact recovery state ID"
                )
            if current["state_id"] != require_sha256(
                recover_expected_state_id, "recover_expected_state_id"
            ):
                raise AgentContractError("stale agent recovery subject")
            lookup = dict(adapter.lookup(operation["operation_id"]))
            validate_lookup(lookup)
            if lookup["status"] == "completed":
                result = dict(lookup["result"])
                validate_result_against_action(
                    result,
                    operation_id=operation["operation_id"],
                    action_digest=operation["action_digest"],
                    tool=operation["tool"],
                    target=operation["target"],
                )
                if result_path.exists():
                    if read_json(result_path) != result:
                        raise AgentContractError("stored result differs from adapter read-back")
                else:
                    atomic_write_json(result_path, result)
                completed = _transition(
                    current,
                    phase="completed",
                    lookup_id=lookup["lookup_id"],
                    result_id=result["result_id"],
                    increment_attempt=True,
                )
                _write_state(state_path, completed)
                return {"status": "recovered_completed", "state": completed, "result": result}
            if lookup["status"] == "unknown":
                unknown = _transition(
                    current,
                    phase="unknown_outcome",
                    lookup_id=lookup["lookup_id"],
                    failure="tool outcome remains unknown after authoritative lookup",
                    increment_attempt=True,
                )
                _write_state(state_path, unknown)
                raise UnknownToolOutcome(
                    "tool outcome is unknown; automatic retry is forbidden"
                )
            current = _transition(
                current,
                phase="planned",
                lookup_id=lookup["lookup_id"],
                increment_attempt=True,
            )
            _write_state(state_path, current)
        else:
            if result_path.exists():
                raise AgentContractError("orphaned result requires manual reconciliation")
            current = _empty_state(
                operation_id=operation["operation_id"],
                phase="planned",
                attempt=1,
                previous_state_id=None,
            )
            _write_state(state_path, current)

        current = _transition(current, phase="tool_started")
        _write_state(state_path, current)
        try:
            result = dict(
                adapter.execute(
                    operation_id=operation["operation_id"],
                    action_digest=operation["action_digest"],
                    tool=operation["tool"],
                    target=operation["target"],
                    arguments=operation["arguments"],
                )
            )
        except UnknownToolOutcome as exc:
            unknown = _transition(
                current,
                phase="unknown_outcome",
                failure=f"UnknownToolOutcome: {str(exc)[:200]}",
            )
            _write_state(state_path, unknown)
            raise
        except Exception as exc:
            failed = _transition(
                current,
                phase="failed",
                failure=f"{type(exc).__name__}: {str(exc)[:200]}",
            )
            _write_state(state_path, failed)
            raise

        validate_result_against_action(
            result,
            operation_id=operation["operation_id"],
            action_digest=operation["action_digest"],
            tool=operation["tool"],
            target=operation["target"],
        )
        if result_path.exists():
            existing = read_json(result_path)
            if existing != result:
                raise AgentContractError("result output already contains another subject")
        else:
            atomic_write_json(result_path, result)
        completed = _transition(
            current, phase="completed", result_id=result["result_id"]
        )
        _write_state(state_path, completed)
        return {"status": "completed", "state": completed, "result": result}
    finally:
        os.close(descriptor)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
