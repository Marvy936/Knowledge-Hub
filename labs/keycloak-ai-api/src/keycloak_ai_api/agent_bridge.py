from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Protocol


class AgentBridgeError(ValueError):
    """Raised when a bounded agent request cannot satisfy the local authority contract."""


class AgentExecutionRefusal(AgentBridgeError):
    """Execution refusal carrying only the durable checkpoint needed for explicit recovery."""

    def __init__(
        self,
        message: str,
        *,
        operation_id: str,
        state_id: str,
        phase: str,
    ) -> None:
        super().__init__(message)
        self.operation_id = operation_id
        self.state_id = state_id
        self.phase = phase

    def evidence(self) -> dict[str, str]:
        return {
            "operation_id": self.operation_id,
            "state_id": self.state_id,
            "phase": self.phase,
        }


class AgentExecutor(Protocol):
    @property
    def policy_id(self) -> str: ...

    @property
    def policy_generation(self) -> str: ...

    def plan(
        self,
        *,
        target: str,
        signal: str,
        operator_note: str,
        incident_generation: str,
    ) -> Mapping[str, Any]: ...

    def remediate(
        self,
        *,
        plan_id: str,
        approval_id: str,
        recover_expected_state_id: str | None,
    ) -> Mapping[str, Any]: ...


def _require_sha256(value: str, field: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(ch not in "0123456789abcdef" for ch in value)
    ):
        raise AgentBridgeError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _read_json(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise AgentBridgeError(f"agent artifact must not be a symlink: {path}")
    try:
        import json

        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AgentBridgeError(f"required agent artifact does not exist: {path}") from exc
    except (OSError, ValueError) as exc:
        raise AgentBridgeError(f"invalid agent artifact: {path}") from exc
    if not isinstance(value, dict):
        raise AgentBridgeError(f"agent artifact must contain an object: {path}")
    return value


def _exact_runtime_file(path: Path, *, runtime_root: Path, name: str) -> Path:
    if path.is_symlink():
        raise AgentBridgeError(f"{name} must not be a symlink")
    resolved = path.resolve(strict=False)
    expected = runtime_root / name
    if resolved != expected:
        raise AgentBridgeError(f"{name} must be the exact {expected.as_posix()} runtime artifact")
    return resolved


def _bounded_identity_dir(
    *, runtime_root: Path, collection: str, identity: str
) -> Path:
    resolved_identity = _require_sha256(identity, f"{collection} identity")
    collection_root = runtime_root / collection
    if collection_root.is_symlink():
        raise AgentBridgeError(f"agent runtime {collection} root must not be a symlink")
    collection_root.mkdir(parents=True, exist_ok=True)
    resolved_collection = collection_root.resolve(strict=False)
    if resolved_collection.parent != runtime_root or resolved_collection.name != collection:
        raise AgentBridgeError(f"agent runtime {collection} root escaped the bounded runtime")
    identity_dir = resolved_collection / resolved_identity
    if identity_dir.is_symlink():
        raise AgentBridgeError(f"agent runtime {collection} identity directory must not be a symlink")
    resolved_dir = identity_dir.resolve(strict=False)
    if resolved_dir.parent != resolved_collection or resolved_dir.name != resolved_identity:
        raise AgentBridgeError(f"agent runtime {collection} identity escaped the bounded runtime")
    return resolved_dir


class LocalBoundedAgentExecutor:
    """Bridge the Keycloak API to the local-only agent_ops authority/execution core.

    The bridge intentionally does not create approvals. Planning writes canonical read-only
    evidence and a plan. Remediation resolves an approval artifact from the exact plan
    directory and then delegates mutation authority to agent_ops.execute_operation().
    """

    def __init__(
        self,
        *,
        tool_state: Path,
        policy_path: Path,
        kill_switch_path: Path,
        runtime_root: Path,
    ) -> None:
        try:
            from agent_ops.planning import validate_agent_policy
            from agent_ops.runtime import validate_runtime_root
            from agent_ops.safety import validate_kill_switch_against_policy
        except ImportError as exc:
            raise AgentBridgeError(
                "bounded agent bridge requires the local agent-ops package to be installed"
            ) from exc

        try:
            resolved_runtime = validate_runtime_root(runtime_root)
            resolved_tool_state = _exact_runtime_file(
                tool_state, runtime_root=resolved_runtime, name="tool-state.json"
            )
            resolved_policy = _exact_runtime_file(
                policy_path, runtime_root=resolved_runtime, name="policy.json"
            )
            resolved_kill_switch = _exact_runtime_file(
                kill_switch_path, runtime_root=resolved_runtime, name="kill-switch.json"
            )
            policy = _read_json(resolved_policy)
            validate_agent_policy(policy)
            kill_switch = _read_json(resolved_kill_switch)
            validate_kill_switch_against_policy(kill_switch=kill_switch, policy=policy)
        except Exception as exc:
            if isinstance(exc, AgentBridgeError):
                raise
            raise AgentBridgeError(
                f"agent bridge startup validation failed: {type(exc).__name__}: {exc}"
            ) from exc

        self._tool_state = resolved_tool_state
        self._policy_path = resolved_policy
        self._kill_switch_path = resolved_kill_switch
        self._runtime_root = resolved_runtime
        self._policy = policy

    @property
    def policy_id(self) -> str:
        return str(self._policy["policy_id"])

    @property
    def policy_generation(self) -> str:
        return str(self._policy["generation"])

    def _plan_dir(self, plan_id: str) -> Path:
        return _bounded_identity_dir(
            runtime_root=self._runtime_root,
            collection="plans",
            identity=plan_id,
        )

    def _operation_dir(self, operation_id: str) -> Path:
        return _bounded_identity_dir(
            runtime_root=self._runtime_root,
            collection="operations",
            identity=operation_id,
        )

    @staticmethod
    def _write_exact(path: Path, value: Mapping[str, Any]) -> None:
        try:
            from agent_ops.contracts import atomic_write_json, read_json
        except ImportError as exc:
            raise AgentBridgeError("agent runtime package is unavailable") from exc
        if path.is_symlink():
            raise AgentBridgeError(f"agent artifact must not be a symlink: {path}")
        if path.exists():
            existing = read_json(path)
            if existing != dict(value):
                raise AgentBridgeError(f"agent artifact already contains another subject: {path}")
            return
        atomic_write_json(path, value)

    def plan(
        self,
        *,
        target: str,
        signal: str,
        operator_note: str,
        incident_generation: str,
    ) -> Mapping[str, Any]:
        try:
            from agent_ops.planning import (
                build_diagnostic_snapshot,
                build_incident,
                plan_incident_action,
                validate_agent_policy,
            )
            from agent_ops.tools import LocalServiceStateAdapter

            policy = _read_json(self._policy_path)
            validate_agent_policy(policy)
            if policy != self._policy:
                raise AgentBridgeError(
                    "configured policy changed after agent bridge startup; restart is required"
                )
            incident = build_incident(
                generation=incident_generation,
                target=target,
                signal=signal,
                operator_note=operator_note,
            )
            inspection = dict(LocalServiceStateAdapter(self._tool_state).inspect(target))
            diagnostic = build_diagnostic_snapshot(incident=incident, inspection=inspection)
            plan = plan_incident_action(
                incident=incident,
                diagnostic=diagnostic,
                policy=policy,
            )
            plan_dir = self._plan_dir(plan["plan_id"])
            self._write_exact(plan_dir / "incident.json", incident)
            self._write_exact(plan_dir / "inspection.json", inspection)
            self._write_exact(plan_dir / "diagnostic.json", diagnostic)
            self._write_exact(plan_dir / "policy.json", policy)
            self._write_exact(plan_dir / "plan.json", plan)
        except Exception as exc:
            if isinstance(exc, AgentBridgeError):
                raise
            raise AgentBridgeError(
                f"bounded agent planning refused: {type(exc).__name__}: {exc}"
            ) from exc

        return {
            "status": "planned",
            "incident_id": incident["incident_id"],
            "inspection_id": inspection["inspection_id"],
            "diagnostic_id": diagnostic["diagnostic_id"],
            "plan_id": plan["plan_id"],
            "disposition": plan["disposition"],
            "action_digest": plan["action_digest"],
            "tool": plan["tool"],
            "target": plan["target"],
            "policy_id": policy["policy_id"],
            "policy_generation": policy["generation"],
        }

    def remediate(
        self,
        *,
        plan_id: str,
        approval_id: str,
        recover_expected_state_id: str | None,
    ) -> Mapping[str, Any]:
        resolved_plan_id = _require_sha256(plan_id, "plan_id")
        resolved_approval_id = _require_sha256(approval_id, "approval_id")
        if recover_expected_state_id is not None:
            _require_sha256(recover_expected_state_id, "recover_expected_state_id")
        plan_dir = self._plan_dir(resolved_plan_id)

        try:
            from agent_ops.contracts import atomic_write_json, read_json
            from agent_ops.execution import build_operation, execute_operation
            from agent_ops.planning import validate_agent_policy
            from agent_ops.safety import validate_kill_switch_against_policy
            from agent_ops.tools import LocalServiceStateAdapter

            incident = _read_json(plan_dir / "incident.json")
            diagnostic = _read_json(plan_dir / "diagnostic.json")
            plan = _read_json(plan_dir / "plan.json")
            policy = _read_json(plan_dir / "policy.json")
            approval = _read_json(plan_dir / "approval.json")
            if plan.get("plan_id") != resolved_plan_id:
                raise AgentBridgeError("stored plan does not match requested plan_id")
            if approval.get("approval_id") != resolved_approval_id:
                raise AgentBridgeError("stored approval does not match requested approval_id")
            validate_agent_policy(policy)
            if policy != self._policy:
                raise AgentBridgeError("stored plan policy differs from configured agent policy")

            kill_switch = _read_json(self._kill_switch_path)
            validate_kill_switch_against_policy(kill_switch=kill_switch, policy=policy)
            operation = build_operation(
                incident=incident,
                diagnostic=diagnostic,
                plan=plan,
                approval=approval,
                policy=policy,
            )
            operation_dir = self._operation_dir(operation["operation_id"])
            operation_path = operation_dir / "operation.json"
            state_path = operation_dir / "execution-state.json"
            result_path = operation_dir / "tool-result.json"
            if operation_path.is_symlink():
                raise AgentBridgeError("stored operation artifact must not be a symlink")
            if operation_path.exists():
                if read_json(operation_path) != operation:
                    raise AgentBridgeError("stored operation differs from exact authoritative rebuild")
            else:
                atomic_write_json(operation_path, operation)
            try:
                outcome = execute_operation(
                    operation=operation,
                    incident=incident,
                    diagnostic=diagnostic,
                    plan=plan,
                    approval=approval,
                    policy=policy,
                    kill_switch=kill_switch,
                    adapter=LocalServiceStateAdapter(self._tool_state),
                    state_path=state_path,
                    result_path=result_path,
                    recover_expected_state_id=recover_expected_state_id,
                )
            except Exception as exc:
                if state_path.is_file() and not state_path.is_symlink():
                    state = read_json(state_path)
                    state_id = state.get("state_id")
                    phase = state.get("phase")
                    if isinstance(state_id, str) and isinstance(phase, str):
                        raise AgentExecutionRefusal(
                            f"bounded remediation did not complete: {type(exc).__name__}: {str(exc)[:160]}",
                            operation_id=operation["operation_id"],
                            state_id=state_id,
                            phase=phase,
                        ) from exc
                raise
        except AgentExecutionRefusal:
            raise
        except Exception as exc:
            if isinstance(exc, AgentBridgeError):
                raise
            raise AgentBridgeError(
                f"bounded remediation refused: {type(exc).__name__}: {exc}"
            ) from exc

        return {
            "status": outcome["status"],
            "plan_id": resolved_plan_id,
            "approval_id": resolved_approval_id,
            "operation_id": operation["operation_id"],
            "state_id": outcome["state"]["state_id"],
            "result_id": outcome["result"]["result_id"],
            "tool": operation["tool"],
            "target": operation["target"],
            "output": outcome["result"]["output"],
            "policy_id": policy["policy_id"],
            "policy_generation": policy["generation"],
        }
