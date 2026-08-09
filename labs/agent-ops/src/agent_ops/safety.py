from __future__ import annotations

from typing import Any, Mapping

from .contracts import (
    AgentContractError,
    canonical_json_bytes,
    require_exact_keys,
    require_nonempty,
    require_sha256,
    sha256_bytes,
    validate_canonical_id,
)
from .planning import AGENT_SCHEMA_VERSION, validate_action_plan, validate_agent_policy


def build_kill_switch(
    *,
    policy: Mapping[str, Any],
    generation: str,
    engaged: bool,
) -> dict[str, Any]:
    validate_agent_policy(policy)
    if not isinstance(engaged, bool):
        raise AgentContractError("kill switch engaged must be boolean")
    payload = {
        "schema_version": AGENT_SCHEMA_VERSION,
        "policy_id": policy["policy_id"],
        "policy_generation": policy["generation"],
        "generation": require_nonempty(generation, "kill_switch.generation"),
        "engaged": engaged,
    }
    return {
        **payload,
        "kill_switch_id": sha256_bytes(canonical_json_bytes(payload)),
    }


def validate_kill_switch(value: Mapping[str, Any]) -> None:
    require_exact_keys(
        value,
        {
            "schema_version",
            "policy_id",
            "policy_generation",
            "generation",
            "engaged",
            "kill_switch_id",
        },
        "kill switch",
    )
    if value.get("schema_version") != AGENT_SCHEMA_VERSION:
        raise AgentContractError("kill switch schema_version must equal 1")
    require_sha256(value.get("policy_id"), "kill_switch.policy_id")
    require_nonempty(
        value.get("policy_generation"), "kill_switch.policy_generation"
    )
    require_nonempty(value.get("generation"), "kill_switch.generation")
    if not isinstance(value.get("engaged"), bool):
        raise AgentContractError("kill switch engaged must be boolean")
    validate_canonical_id(value, "kill_switch_id")


def validate_kill_switch_against_policy(
    *, kill_switch: Mapping[str, Any], policy: Mapping[str, Any]
) -> None:
    validate_kill_switch(kill_switch)
    validate_agent_policy(policy)
    if kill_switch["policy_id"] != policy["policy_id"]:
        raise AgentContractError("kill switch belongs to another policy")
    if kill_switch["policy_generation"] != policy["generation"]:
        raise AgentContractError("kill switch policy generation does not match policy")


def approve_action_plan(
    *,
    plan: Mapping[str, Any],
    policy: Mapping[str, Any],
    expected_plan_id: str,
    approver: str,
    approval_generation: str,
) -> dict[str, Any]:
    validate_action_plan(plan)
    validate_agent_policy(policy)
    if plan["plan_id"] != require_sha256(expected_plan_id, "expected_plan_id"):
        raise AgentContractError("stale or mismatched action plan")
    if plan["policy_id"] != policy["policy_id"]:
        raise AgentContractError("action plan belongs to another policy")
    if plan["policy_generation"] != policy["generation"]:
        raise AgentContractError("action plan policy generation does not match policy")
    if plan["disposition"] != "approval_required":
        raise AgentContractError("action plan is not eligible for approval")
    if plan["tool"] not in policy["approval_required_tools"]:
        raise AgentContractError("action plan tool is not approval-gated by policy")
    if plan["target"] not in policy["allowed_targets"]:
        raise AgentContractError("action plan target is outside policy allowlist")

    payload = {
        "schema_version": AGENT_SCHEMA_VERSION,
        "plan_id": plan["plan_id"],
        "policy_id": policy["policy_id"],
        "policy_generation": policy["generation"],
        "action_digest": plan["action_digest"],
        "tool": plan["tool"],
        "target": plan["target"],
        "approver": require_nonempty(approver, "approval.approver"),
        "approval_generation": require_nonempty(
            approval_generation, "approval.generation"
        ),
        "authorized_action": "execute_typed_tool_once",
    }
    return {
        **payload,
        "approval_id": sha256_bytes(canonical_json_bytes(payload)),
    }


def validate_action_approval(value: Mapping[str, Any]) -> None:
    require_exact_keys(
        value,
        {
            "schema_version",
            "plan_id",
            "policy_id",
            "policy_generation",
            "action_digest",
            "tool",
            "target",
            "approver",
            "approval_generation",
            "authorized_action",
            "approval_id",
        },
        "action approval",
    )
    if value.get("schema_version") != AGENT_SCHEMA_VERSION:
        raise AgentContractError("action approval schema_version must equal 1")
    for field in ("plan_id", "policy_id", "action_digest"):
        require_sha256(value.get(field), f"approval.{field}")
    for field in (
        "policy_generation",
        "tool",
        "target",
        "approver",
        "approval_generation",
    ):
        require_nonempty(value.get(field), f"approval.{field}")
    if value.get("authorized_action") != "execute_typed_tool_once":
        raise AgentContractError("action approval authorized_action is invalid")
    validate_canonical_id(value, "approval_id")


def validate_approval_against_plan(
    *, approval: Mapping[str, Any], plan: Mapping[str, Any], policy: Mapping[str, Any]
) -> None:
    validate_action_approval(approval)
    validate_action_plan(plan)
    validate_agent_policy(policy)
    expected = {
        "plan_id": plan["plan_id"],
        "policy_id": policy["policy_id"],
        "policy_generation": policy["generation"],
        "action_digest": plan["action_digest"],
        "tool": plan["tool"],
        "target": plan["target"],
    }
    for field, expected_value in expected.items():
        if approval[field] != expected_value:
            raise AgentContractError(f"approval {field} does not match action plan")
