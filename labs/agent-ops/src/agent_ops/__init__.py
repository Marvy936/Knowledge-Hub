"""Bounded incident and operations agent contracts for Knowledge Hub Practical v1."""

from .contracts import AgentContractError
from .execution import (
    build_operation,
    execute_operation,
    validate_execution_state,
    validate_operation,
)
from .planning import (
    build_agent_policy,
    build_diagnostic_snapshot,
    build_incident,
    build_service_inspection,
    plan_incident_action,
    validate_action_plan,
    validate_agent_policy,
    validate_diagnostic_snapshot,
    validate_incident,
    validate_service_inspection,
)
from .safety import (
    approve_action_plan,
    build_kill_switch,
    validate_action_approval,
    validate_approval_against_plan,
    validate_kill_switch,
    validate_kill_switch_against_policy,
)
from .tools import LocalServiceStateAdapter, UnknownToolOutcome

__all__ = [
    "AgentContractError",
    "LocalServiceStateAdapter",
    "UnknownToolOutcome",
    "approve_action_plan",
    "build_agent_policy",
    "build_diagnostic_snapshot",
    "build_incident",
    "build_kill_switch",
    "build_operation",
    "build_service_inspection",
    "execute_operation",
    "plan_incident_action",
    "validate_action_approval",
    "validate_action_plan",
    "validate_agent_policy",
    "validate_approval_against_plan",
    "validate_diagnostic_snapshot",
    "validate_execution_state",
    "validate_incident",
    "validate_kill_switch",
    "validate_kill_switch_against_policy",
    "validate_operation",
    "validate_service_inspection",
]
