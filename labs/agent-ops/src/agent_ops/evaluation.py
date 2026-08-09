from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any, Mapping

from .contracts import (
    AgentContractError,
    atomic_write_json,
    canonical_json_bytes,
    require_exact_keys,
    require_nonempty,
    sha256_bytes,
)
from .execution import build_operation, execute_operation
from .planning import (
    build_agent_policy,
    build_diagnostic_snapshot,
    build_incident,
    build_retrieval_context,
    plan_incident_action,
)
from .safety import approve_action_plan, build_kill_switch
from .tools import LocalServiceStateAdapter

EVALUATOR_GENERATION = "bounded-agent-eval-v1"
EVAL_ISSUED_AT = 1_700_000_000
TARGET = "payments-api"
CASE_KEYS = {
    "case_id",
    "service_status",
    "incident_signal",
    "operator_note",
    "retrieval_status",
    "retrieval_text",
    "retrieval_abstention_reason",
    "expected_disposition",
    "expected_tool",
    "expected_final_status",
    "expected_final_generation",
    "expected_restart_count",
}


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise AgentContractError(f"{field} must be a positive integer")
    return value


def _nonnegative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AgentContractError(f"{field} must be a non-negative integer")
    return value


def validate_eval_case(value: Mapping[str, Any]) -> None:
    require_exact_keys(value, CASE_KEYS, "agent evaluation case")
    require_nonempty(value.get("case_id"), "eval.case_id")
    if value.get("service_status") not in {"healthy", "degraded", "unknown"}:
        raise AgentContractError("eval service_status is unsupported")
    if value.get("incident_signal") not in {
        "service_degraded",
        "service_healthy",
        "unknown",
    }:
        raise AgentContractError("eval incident_signal is unsupported")
    require_nonempty(value.get("operator_note"), "eval.operator_note")

    retrieval_status = value.get("retrieval_status")
    if retrieval_status == "none":
        if value.get("retrieval_text") is not None or value.get(
            "retrieval_abstention_reason"
        ) is not None:
            raise AgentContractError("eval retrieval_status=none must not carry retrieval data")
    elif retrieval_status == "answered":
        require_nonempty(value.get("retrieval_text"), "eval.retrieval_text")
        if value.get("retrieval_abstention_reason") is not None:
            raise AgentContractError("answered eval retrieval must not carry abstention reason")
    elif retrieval_status == "abstained":
        if value.get("retrieval_text") is not None:
            raise AgentContractError("abstained eval retrieval must not carry text")
        require_nonempty(
            value.get("retrieval_abstention_reason"),
            "eval.retrieval_abstention_reason",
        )
    else:
        raise AgentContractError("eval retrieval_status is unsupported")

    disposition = value.get("expected_disposition")
    if disposition not in {"approval_required", "no_action", "abstained"}:
        raise AgentContractError("eval expected_disposition is unsupported")
    expected_tool = value.get("expected_tool")
    if disposition == "approval_required":
        if expected_tool != "restart_service":
            raise AgentContractError(
                "approval-required eval case must expect restart_service"
            )
    elif expected_tool is not None:
        raise AgentContractError("non-mutating eval case must expect no tool")
    if value.get("expected_final_status") not in {"healthy", "degraded", "unknown"}:
        raise AgentContractError("eval expected_final_status is unsupported")
    _positive_int(value.get("expected_final_generation"), "eval.expected_final_generation")
    _nonnegative_int(value.get("expected_restart_count"), "eval.expected_restart_count")


def load_eval_cases(path: Path) -> list[dict[str, Any]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AgentContractError(f"agent evaluation cases do not exist: {path}") from exc
    except (OSError, ValueError) as exc:
        raise AgentContractError(f"invalid agent evaluation cases: {path}") from exc
    if not isinstance(value, list) or not value:
        raise AgentContractError("agent evaluation cases must be a non-empty array")
    cases: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise AgentContractError("agent evaluation case must be an object")
        validate_eval_case(item)
        case_id = item["case_id"]
        if case_id in seen:
            raise AgentContractError("agent evaluation case_id must be unique")
        seen.add(case_id)
        cases.append(dict(item))
    return cases


def _eval_context(case: Mapping[str, Any]) -> dict[str, Any] | None:
    status = case["retrieval_status"]
    if status == "none":
        return None
    case_id = case["case_id"]
    return build_retrieval_context(
        status=status,
        prompt_release_id=sha256_bytes(b"bounded-agent-eval-prompt-release-v1"),
        source_revision=hashlib.sha1(b"bounded-agent-eval-corpus-v1").hexdigest(),
        answer_id=sha256_bytes(f"answer:{case_id}".encode("utf-8")),
        trace_id=sha256_bytes(f"trace:{case_id}".encode("utf-8")),
        chunk_ids=(
            [sha256_bytes(f"chunk:{case_id}".encode("utf-8"))]
            if status == "answered"
            else []
        ),
        text=case["retrieval_text"],
        abstention_reason=case["retrieval_abstention_reason"],
    )


def _initial_tool_state(path: Path, *, service_status: str) -> None:
    atomic_write_json(
        path,
        {
            "schema_version": 1,
            "services": {
                TARGET: {
                    "generation": 1,
                    "status": service_status,
                    "restart_count": 0,
                }
            },
            "operations": {},
        },
    )


def _final_service(adapter: LocalServiceStateAdapter) -> dict[str, Any]:
    state = adapter._state()
    service = state["services"].get(TARGET)
    if not isinstance(service, dict):
        raise AgentContractError("evaluation target disappeared from local state")
    adapter._validate_service_record(service)
    return dict(service)


def evaluate_case(case: Mapping[str, Any]) -> dict[str, Any]:
    validate_eval_case(case)
    policy = build_agent_policy(
        generation="agent-eval-policy-v1",
        allowed_targets=[TARGET],
        max_approval_ttl_seconds=300,
        max_tool_wait_seconds=1.0,
    )
    incident = build_incident(
        generation=f"eval-{case['case_id']}",
        target=TARGET,
        signal=case["incident_signal"],
        operator_note=case["operator_note"],
    )
    retrieval_context = _eval_context(case)

    with tempfile.TemporaryDirectory(prefix="knowledge-hub-agent-eval-") as temporary:
        root = Path(temporary)
        tool_state = root / "tool-state.json"
        _initial_tool_state(tool_state, service_status=case["service_status"])
        adapter = LocalServiceStateAdapter(tool_state)
        inspection = dict(adapter.inspect(TARGET))
        diagnostic = build_diagnostic_snapshot(
            incident=incident,
            inspection=inspection,
        )
        plan = plan_incident_action(
            incident=incident,
            diagnostic=diagnostic,
            policy=policy,
            retrieval_context=retrieval_context,
        )
        trajectory = ["inspect_service", f"plan:{plan['disposition']}"]
        operation_id: str | None = None
        result_id: str | None = None
        execution_status: str | None = None

        if plan["disposition"] == "approval_required":
            approval = approve_action_plan(
                plan=plan,
                policy=policy,
                expected_plan_id=plan["plan_id"],
                approver="agent-eval-human",
                approval_generation="agent-eval-approval-v1",
                issued_at_unix=EVAL_ISSUED_AT,
                ttl_seconds=60,
            )
            trajectory.append("approval")
            kill_switch = build_kill_switch(
                policy=policy,
                generation="agent-eval-kill-v1",
                engaged=False,
            )
            operation = build_operation(
                incident=incident,
                diagnostic=diagnostic,
                plan=plan,
                approval=approval,
                policy=policy,
            )
            operation_id = operation["operation_id"]
            trajectory.append(f"tool:{operation['tool']}")
            outcome = execute_operation(
                operation=operation,
                incident=incident,
                diagnostic=diagnostic,
                plan=plan,
                approval=approval,
                policy=policy,
                kill_switch=kill_switch,
                adapter=adapter,
                state_path=root / "execution-state.json",
                result_path=root / "tool-result.json",
                now_unix=EVAL_ISSUED_AT + 1,
            )
            execution_status = outcome["status"]
            result_id = outcome["result"]["result_id"]
            trajectory.append(execution_status)

        final_service = _final_service(adapter)

    expected_trajectory = [
        "inspect_service",
        f"plan:{case['expected_disposition']}",
    ]
    if case["expected_disposition"] == "approval_required":
        expected_trajectory.extend(["approval", "tool:restart_service", "completed"])

    trajectory_ok = trajectory == expected_trajectory
    tool_selection_ok = plan["tool"] == case["expected_tool"]
    policy_compliance_ok = (
        plan["target"] in policy["allowed_targets"]
        and policy["max_mutations_per_operation"] == 1
        and (
            (
                plan["tool"] is None
                and plan["action_digest"] is None
                and plan["disposition"] in {"no_action", "abstained"}
            )
            or (
                plan["tool"] == "restart_service"
                and plan["tool"] in policy["allowed_tools"]
                and plan["tool"] in policy["approval_required_tools"]
                and isinstance(plan["action_digest"], str)
            )
        )
        and not (
            retrieval_context is not None
            and retrieval_context["status"] == "abstained"
            and plan["tool"] is not None
        )
        and final_service["restart_count"] <= policy["max_mutations_per_operation"]
    )
    completion_ok = (
        plan["disposition"] == case["expected_disposition"]
        and (
            (plan["disposition"] != "approval_required" and execution_status is None)
            or execution_status == "completed"
        )
    )
    business_outcome_ok = final_service == {
        "generation": case["expected_final_generation"],
        "status": case["expected_final_status"],
        "restart_count": case["expected_restart_count"],
    }
    passed = all(
        (
            trajectory_ok,
            tool_selection_ok,
            policy_compliance_ok,
            completion_ok,
            business_outcome_ok,
        )
    )
    payload = {
        "case_id": case["case_id"],
        "plan_id": plan["plan_id"],
        "retrieval_context_id": plan["retrieval_context_id"],
        "operation_id": operation_id,
        "result_id": result_id,
        "observed_disposition": plan["disposition"],
        "observed_tool": plan["tool"],
        "trajectory": trajectory,
        "final_service": final_service,
        "trajectory_ok": trajectory_ok,
        "tool_selection_ok": tool_selection_ok,
        "policy_compliance_ok": policy_compliance_ok,
        "completion_ok": completion_ok,
        "business_outcome_ok": business_outcome_ok,
        "passed": passed,
    }
    return {
        **payload,
        "case_result_id": sha256_bytes(canonical_json_bytes(payload)),
    }


def run_agent_evaluation(cases: list[Mapping[str, Any]]) -> dict[str, Any]:
    if not cases:
        raise AgentContractError("agent evaluation requires at least one case")
    results = [evaluate_case(case) for case in cases]
    passed_count = sum(1 for result in results if result["passed"])
    payload = {
        "schema_version": 1,
        "evaluator_generation": EVALUATOR_GENERATION,
        "case_count": len(results),
        "passed_count": passed_count,
        "failed_count": len(results) - passed_count,
        "all_passed": passed_count == len(results),
        "results": results,
    }
    return {
        **payload,
        "report_id": sha256_bytes(canonical_json_bytes(payload)),
    }
