from __future__ import annotations

import math
from typing import Any, Iterable, Mapping

from .contracts import (
    AgentContractError,
    canonical_json_bytes,
    require_exact_keys,
    require_nonempty,
    require_sha256,
    sha256_bytes,
    validate_canonical_id,
)

AGENT_SCHEMA_VERSION = 1
SUPPORTED_SIGNALS = {"service_degraded", "service_healthy", "unknown"}
RETRIEVAL_STATUSES = {"answered", "abstained"}


def _positive_seconds(value: Any, field: str, *, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AgentContractError(f"{field} must be a positive finite number")
    resolved = float(value)
    if not math.isfinite(resolved) or resolved <= 0.0 or resolved > maximum:
        raise AgentContractError(f"{field} must be > 0 and <= {maximum:g} seconds")
    return resolved


def _require_sha1(value: Any, field: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 40
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise AgentContractError(f"{field} must be a lowercase 40-character Git SHA-1")
    return value


def build_agent_policy(
    *,
    generation: str,
    allowed_targets: Iterable[str],
    max_approval_ttl_seconds: int = 900,
    max_tool_wait_seconds: float = 5.0,
) -> dict[str, Any]:
    targets = sorted({require_nonempty(item, "allowed_target") for item in allowed_targets})
    if not targets:
        raise AgentContractError("agent policy requires at least one allowed target")
    if (
        isinstance(max_approval_ttl_seconds, bool)
        or not isinstance(max_approval_ttl_seconds, int)
        or max_approval_ttl_seconds <= 0
        or max_approval_ttl_seconds > 86400
    ):
        raise AgentContractError(
            "policy.max_approval_ttl_seconds must be an integer between 1 and 86400"
        )
    tool_wait = _positive_seconds(
        max_tool_wait_seconds,
        "policy.max_tool_wait_seconds",
        maximum=60.0,
    )
    payload = {
        "schema_version": AGENT_SCHEMA_VERSION,
        "generation": require_nonempty(generation, "policy.generation"),
        "sandbox": "local-state-only",
        "allowed_targets": targets,
        "allowed_tools": ["inspect_service", "restart_service"],
        "approval_required_tools": ["restart_service"],
        "max_mutations_per_operation": 1,
        "max_approval_ttl_seconds": max_approval_ttl_seconds,
        "max_tool_wait_seconds": tool_wait,
    }
    return {**payload, "policy_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_agent_policy(value: Mapping[str, Any]) -> None:
    require_exact_keys(
        value,
        {
            "schema_version",
            "generation",
            "sandbox",
            "allowed_targets",
            "allowed_tools",
            "approval_required_tools",
            "max_mutations_per_operation",
            "max_approval_ttl_seconds",
            "max_tool_wait_seconds",
            "policy_id",
        },
        "agent policy",
    )
    if value.get("schema_version") != AGENT_SCHEMA_VERSION:
        raise AgentContractError("agent policy schema_version must equal 1")
    require_nonempty(value.get("generation"), "policy.generation")
    if value.get("sandbox") != "local-state-only":
        raise AgentContractError("agent policy sandbox must equal local-state-only")
    targets = value.get("allowed_targets")
    if (
        not isinstance(targets, list)
        or not targets
        or targets != sorted(set(targets))
        or any(not isinstance(item, str) or not item for item in targets)
    ):
        raise AgentContractError("agent policy allowed_targets are invalid")
    if value.get("allowed_tools") != ["inspect_service", "restart_service"]:
        raise AgentContractError("agent policy allowed_tools do not match generation 1")
    if value.get("approval_required_tools") != ["restart_service"]:
        raise AgentContractError(
            "agent policy approval-required tools do not match generation 1"
        )
    if value.get("max_mutations_per_operation") != 1:
        raise AgentContractError("agent policy max mutations must equal 1")
    ttl = value.get("max_approval_ttl_seconds")
    if isinstance(ttl, bool) or not isinstance(ttl, int) or ttl <= 0 or ttl > 86400:
        raise AgentContractError(
            "policy.max_approval_ttl_seconds must be an integer between 1 and 86400"
        )
    wait = _positive_seconds(
        value.get("max_tool_wait_seconds"),
        "policy.max_tool_wait_seconds",
        maximum=60.0,
    )
    if value.get("max_tool_wait_seconds") != wait:
        raise AgentContractError("policy.max_tool_wait_seconds must be canonical numeric seconds")
    validate_canonical_id(value, "policy_id")


def build_incident(
    *,
    generation: str,
    target: str,
    signal: str,
    operator_note: str,
) -> dict[str, Any]:
    resolved_signal = require_nonempty(signal, "incident.signal")
    if resolved_signal not in SUPPORTED_SIGNALS:
        raise AgentContractError("incident signal is unsupported")
    payload = {
        "schema_version": AGENT_SCHEMA_VERSION,
        "generation": require_nonempty(generation, "incident.generation"),
        "target": require_nonempty(target, "incident.target"),
        "signal": resolved_signal,
        "operator_note": require_nonempty(operator_note, "incident.operator_note"),
    }
    return {**payload, "incident_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_incident(value: Mapping[str, Any]) -> None:
    require_exact_keys(
        value,
        {
            "schema_version",
            "generation",
            "target",
            "signal",
            "operator_note",
            "incident_id",
        },
        "incident",
    )
    if value.get("schema_version") != AGENT_SCHEMA_VERSION:
        raise AgentContractError("incident schema_version must equal 1")
    require_nonempty(value.get("generation"), "incident.generation")
    require_nonempty(value.get("target"), "incident.target")
    signal = require_nonempty(value.get("signal"), "incident.signal")
    if signal not in SUPPORTED_SIGNALS:
        raise AgentContractError("incident signal is unsupported")
    require_nonempty(value.get("operator_note"), "incident.operator_note")
    validate_canonical_id(value, "incident_id")


def build_service_inspection(
    *, target: str, service_generation: int, service_status: str
) -> dict[str, Any]:
    resolved_target = require_nonempty(target, "inspection.target")
    if (
        isinstance(service_generation, bool)
        or not isinstance(service_generation, int)
        or service_generation < 1
    ):
        raise AgentContractError("inspection service_generation must be a positive integer")
    status = require_nonempty(service_status, "inspection.service_status")
    if status not in {"healthy", "degraded", "unknown"}:
        raise AgentContractError("inspection service_status is unsupported")
    payload = {
        "schema_version": AGENT_SCHEMA_VERSION,
        "tool": "inspect_service",
        "target": resolved_target,
        "service_generation": service_generation,
        "service_status": status,
    }
    return {**payload, "inspection_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_service_inspection(value: Mapping[str, Any]) -> None:
    require_exact_keys(
        value,
        {
            "schema_version",
            "tool",
            "target",
            "service_generation",
            "service_status",
            "inspection_id",
        },
        "service inspection",
    )
    if value.get("schema_version") != AGENT_SCHEMA_VERSION:
        raise AgentContractError("service inspection schema_version must equal 1")
    if value.get("tool") != "inspect_service":
        raise AgentContractError("service inspection tool must equal inspect_service")
    require_nonempty(value.get("target"), "inspection.target")
    generation = value.get("service_generation")
    if isinstance(generation, bool) or not isinstance(generation, int) or generation < 1:
        raise AgentContractError("inspection service_generation is invalid")
    if value.get("service_status") not in {"healthy", "degraded", "unknown"}:
        raise AgentContractError("inspection service_status is unsupported")
    validate_canonical_id(value, "inspection_id")


def build_diagnostic_snapshot(
    *,
    incident: Mapping[str, Any],
    inspection: Mapping[str, Any],
) -> dict[str, Any]:
    validate_incident(incident)
    validate_service_inspection(inspection)
    if inspection["target"] != incident["target"]:
        raise AgentContractError("inspection target does not match incident")
    payload = {
        "schema_version": AGENT_SCHEMA_VERSION,
        "incident_id": incident["incident_id"],
        "inspection_id": inspection["inspection_id"],
        "target": incident["target"],
        "service_generation": inspection["service_generation"],
        "service_status": inspection["service_status"],
    }
    return {
        **payload,
        "diagnostic_id": sha256_bytes(canonical_json_bytes(payload)),
    }


def validate_diagnostic_snapshot(value: Mapping[str, Any]) -> None:
    require_exact_keys(
        value,
        {
            "schema_version",
            "incident_id",
            "inspection_id",
            "target",
            "service_generation",
            "service_status",
            "diagnostic_id",
        },
        "diagnostic snapshot",
    )
    if value.get("schema_version") != AGENT_SCHEMA_VERSION:
        raise AgentContractError("diagnostic schema_version must equal 1")
    require_sha256(value.get("incident_id"), "diagnostic.incident_id")
    require_sha256(value.get("inspection_id"), "diagnostic.inspection_id")
    require_nonempty(value.get("target"), "diagnostic.target")
    generation = value.get("service_generation")
    if isinstance(generation, bool) or not isinstance(generation, int) or generation < 1:
        raise AgentContractError("diagnostic service_generation is invalid")
    if value.get("service_status") not in {"healthy", "degraded", "unknown"}:
        raise AgentContractError("diagnostic service_status is unsupported")
    validate_canonical_id(value, "diagnostic_id")


def build_retrieval_context(
    *,
    status: str,
    prompt_release_id: str,
    source_revision: str,
    answer_id: str,
    trace_id: str,
    chunk_ids: Iterable[str],
    text: str | None,
    abstention_reason: str | None,
) -> dict[str, Any]:
    resolved_status = require_nonempty(status, "retrieval_context.status")
    if resolved_status not in RETRIEVAL_STATUSES:
        raise AgentContractError("retrieval context status is unsupported")
    chunks = [require_sha256(item, "retrieval_context.chunk_id") for item in chunk_ids]
    if len(chunks) != len(set(chunks)):
        raise AgentContractError("retrieval context chunk_ids must be unique")
    payload = {
        "schema_version": AGENT_SCHEMA_VERSION,
        "status": resolved_status,
        "prompt_release_id": require_sha256(
            prompt_release_id, "retrieval_context.prompt_release_id"
        ),
        "source_revision": _require_sha1(
            source_revision, "retrieval_context.source_revision"
        ),
        "answer_id": require_sha256(answer_id, "retrieval_context.answer_id"),
        "trace_id": require_sha256(trace_id, "retrieval_context.trace_id"),
        "chunk_ids": chunks,
        "text": text,
        "abstention_reason": abstention_reason,
    }
    if resolved_status == "answered":
        if not isinstance(text, str) or not text.strip():
            raise AgentContractError("answered retrieval context requires non-empty text")
        if not chunks:
            raise AgentContractError("answered retrieval context requires chunk_ids")
        if abstention_reason is not None:
            raise AgentContractError("answered retrieval context cannot carry abstention_reason")
    else:
        if text is not None:
            raise AgentContractError("abstained retrieval context must not carry text")
        if chunks:
            raise AgentContractError("abstained retrieval context must not carry chunk_ids")
        require_nonempty(abstention_reason, "retrieval_context.abstention_reason")
    return {**payload, "context_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_retrieval_context(value: Mapping[str, Any]) -> None:
    require_exact_keys(
        value,
        {
            "schema_version",
            "status",
            "prompt_release_id",
            "source_revision",
            "answer_id",
            "trace_id",
            "chunk_ids",
            "text",
            "abstention_reason",
            "context_id",
        },
        "retrieval context",
    )
    if value.get("schema_version") != AGENT_SCHEMA_VERSION:
        raise AgentContractError("retrieval context schema_version must equal 1")
    rebuilt = build_retrieval_context(
        status=value.get("status"),
        prompt_release_id=value.get("prompt_release_id"),
        source_revision=value.get("source_revision"),
        answer_id=value.get("answer_id"),
        trace_id=value.get("trace_id"),
        chunk_ids=value.get("chunk_ids") if isinstance(value.get("chunk_ids"), list) else [],
        text=value.get("text"),
        abstention_reason=value.get("abstention_reason"),
    )
    if dict(value) != rebuilt:
        raise AgentContractError("retrieval context is not canonical")


def _action_digest(tool: str, target: str, arguments: Mapping[str, Any]) -> str:
    return sha256_bytes(
        canonical_json_bytes(
            {
                "tool": tool,
                "target": target,
                "arguments": dict(arguments),
            }
        )
    )


def plan_incident_action(
    *,
    incident: Mapping[str, Any],
    diagnostic: Mapping[str, Any],
    policy: Mapping[str, Any],
    retrieval_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    validate_incident(incident)
    validate_diagnostic_snapshot(diagnostic)
    validate_agent_policy(policy)
    if retrieval_context is not None:
        validate_retrieval_context(retrieval_context)
    if diagnostic["incident_id"] != incident["incident_id"]:
        raise AgentContractError("diagnostic belongs to another incident")
    if diagnostic["target"] != incident["target"]:
        raise AgentContractError("diagnostic target does not match incident")
    if incident["target"] not in policy["allowed_targets"]:
        raise AgentContractError("incident target is outside the sandbox allowlist")

    retrieval_abstained = (
        retrieval_context is not None and retrieval_context["status"] == "abstained"
    )
    if retrieval_abstained:
        disposition = "abstained"
        tool = None
        arguments: dict[str, Any] = {}
        rationale = "promoted retrieval abstained; retrieved content cannot authorize mutation"
    elif diagnostic["service_status"] == "degraded":
        disposition = "approval_required"
        tool = "restart_service"
        arguments = {"expected_generation": diagnostic["service_generation"]}
        rationale = "validated degraded service may be restarted once after exact approval"
    elif diagnostic["service_status"] == "healthy":
        disposition = "no_action"
        tool = None
        arguments = {}
        rationale = "validated service is healthy; mutation is forbidden"
    else:
        disposition = "abstained"
        tool = None
        arguments = {}
        rationale = "diagnostic state is unknown; mutation requires more evidence"

    digest = None if tool is None else _action_digest(tool, incident["target"], arguments)
    payload = {
        "schema_version": AGENT_SCHEMA_VERSION,
        "incident_id": incident["incident_id"],
        "diagnostic_id": diagnostic["diagnostic_id"],
        "policy_id": policy["policy_id"],
        "policy_generation": policy["generation"],
        "target": incident["target"],
        "disposition": disposition,
        "tool": tool,
        "arguments": arguments,
        "action_digest": digest,
        "rationale": rationale,
    }
    if retrieval_context is not None:
        payload["retrieval_context_id"] = retrieval_context["context_id"]
    return {**payload, "plan_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_action_plan(value: Mapping[str, Any]) -> None:
    base_keys = {
        "schema_version",
        "incident_id",
        "diagnostic_id",
        "policy_id",
        "policy_generation",
        "target",
        "disposition",
        "tool",
        "arguments",
        "action_digest",
        "rationale",
        "plan_id",
    }
    keys = set(value)
    if keys not in {frozenset(base_keys), frozenset(base_keys | {"retrieval_context_id"})}:
        raise AgentContractError("action plan keys mismatch")
    if value.get("schema_version") != AGENT_SCHEMA_VERSION:
        raise AgentContractError("action plan schema_version must equal 1")
    for field in ("incident_id", "diagnostic_id", "policy_id"):
        require_sha256(value.get(field), f"plan.{field}")
    if "retrieval_context_id" in value:
        require_sha256(value.get("retrieval_context_id"), "plan.retrieval_context_id")
    require_nonempty(value.get("policy_generation"), "plan.policy_generation")
    target = require_nonempty(value.get("target"), "plan.target")
    require_nonempty(value.get("rationale"), "plan.rationale")
    disposition = value.get("disposition")
    if disposition == "approval_required":
        if value.get("tool") != "restart_service":
            raise AgentContractError("approval-required plan must use restart_service")
        arguments = value.get("arguments")
        if not isinstance(arguments, dict) or set(arguments) != {"expected_generation"}:
            raise AgentContractError("restart_service arguments are invalid")
        generation = arguments["expected_generation"]
        if isinstance(generation, bool) or not isinstance(generation, int) or generation < 1:
            raise AgentContractError("restart_service expected_generation is invalid")
        expected_digest = _action_digest("restart_service", target, arguments)
        if value.get("action_digest") != expected_digest:
            raise AgentContractError("plan action_digest does not match typed action")
    elif disposition in {"no_action", "abstained"}:
        if value.get("tool") is not None or value.get("arguments") != {}:
            raise AgentContractError("non-mutating plan must not contain tool arguments")
        if value.get("action_digest") is not None:
            raise AgentContractError("non-mutating plan must not contain action_digest")
    else:
        raise AgentContractError("action plan disposition is unsupported")
    validate_canonical_id(value, "plan_id")
