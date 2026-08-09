from __future__ import annotations

import math
import os
from typing import Any, Callable, Mapping

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, field_validator

from .agent_bridge import AgentBridgeError, AgentExecutionRefusal, AgentExecutor
from .auth import (
    AuthenticationError,
    ForbiddenError,
    JwksSigningKeyResolver,
    Principal,
    SigningKeyResolver,
    policy,
    validate_access_token,
)
from .rag_bridge import RagBridgeError, RagExecutor

bearer = HTTPBearer(auto_error=False)
REQUIRED_API_SCOPE = "knowledge-hub-api-access"

RAG_RESULT_KEYS = {
    "status",
    "answer",
    "abstention_reason",
    "citations",
    "prompt_release_id",
    "source_revision",
    "retrieval_result_id",
    "answer_id",
    "trace_id",
    "latency_ms",
}
AGENT_PLAN_BASE_KEYS = {
    "status",
    "incident_id",
    "inspection_id",
    "diagnostic_id",
    "plan_id",
    "disposition",
    "action_digest",
    "tool",
    "target",
    "policy_id",
    "policy_generation",
}
AGENT_REMEDIATION_RESULT_KEYS = {
    "status",
    "plan_id",
    "approval_id",
    "operation_id",
    "state_id",
    "result_id",
    "tool",
    "target",
    "output",
    "policy_id",
    "policy_generation",
}


class RagQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        resolved = value.strip()
        if not resolved:
            raise ValueError("query must be non-empty")
        if len(resolved) > 2000:
            raise ValueError("query exceeds the 2000-character request bound")
        return resolved


class AgentPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: str
    signal: str
    operator_note: str
    incident_generation: str
    knowledge_query: str | None = None

    @field_validator("target", "incident_generation")
    @classmethod
    def validate_short_nonempty(cls, value: str) -> str:
        resolved = value.strip()
        if not resolved:
            raise ValueError("value must be non-empty")
        if len(resolved) > 128:
            raise ValueError("value exceeds the 128-character request bound")
        return resolved

    @field_validator("signal")
    @classmethod
    def validate_signal(cls, value: str) -> str:
        if value not in {"service_degraded", "service_healthy", "unknown"}:
            raise ValueError("signal is unsupported")
        return value

    @field_validator("operator_note")
    @classmethod
    def validate_operator_note(cls, value: str) -> str:
        resolved = value.strip()
        if not resolved:
            raise ValueError("operator_note must be non-empty")
        if len(resolved) > 2000:
            raise ValueError("operator_note exceeds the 2000-character request bound")
        return resolved

    @field_validator("knowledge_query")
    @classmethod
    def validate_knowledge_query(cls, value: str | None) -> str | None:
        if value is None:
            return None
        resolved = value.strip()
        if not resolved:
            raise ValueError("knowledge_query must be non-empty when provided")
        if len(resolved) > 2000:
            raise ValueError("knowledge_query exceeds the 2000-character request bound")
        return resolved


class AgentRemediateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str
    approval_id: str
    recover_expected_state_id: str | None = None

    @field_validator("plan_id", "approval_id")
    @classmethod
    def validate_required_digest(cls, value: str) -> str:
        return _require_hex(value, length=64, field="agent request digest")

    @field_validator("recover_expected_state_id")
    @classmethod
    def validate_optional_digest(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _require_hex(value, length=64, field="recover_expected_state_id")


def _principal_json(principal: Principal) -> dict[str, object]:
    return {
        "subject": principal.subject,
        "authorized_party": principal.authorized_party,
        "audience": list(principal.audience),
        "roles": sorted(principal.roles),
        "scopes": sorted(principal.scopes),
        "jti": principal.jti,
    }


def _require_hex(value: Any, *, length: int, field: str) -> str:
    if not isinstance(value, str) or len(value) != length:
        raise ValueError(f"{field} must be a {length}-character lowercase hex value")
    if any(character not in "0123456789abcdef" for character in value):
        raise ValueError(f"{field} must be lowercase hexadecimal")
    return value


def _validate_rag_result(
    result: Mapping[str, Any], *, executor: RagExecutor
) -> dict[str, Any]:
    if not isinstance(result, Mapping) or set(result) != RAG_RESULT_KEYS:
        raise ValueError("RAG backend result keys mismatch")
    status = result.get("status")
    if status not in {"answered", "abstained"}:
        raise ValueError("RAG backend result status is unsupported")
    prompt_release_id = _require_hex(
        result.get("prompt_release_id"), length=64, field="prompt_release_id"
    )
    source_revision = _require_hex(
        result.get("source_revision"), length=40, field="source_revision"
    )
    if prompt_release_id != executor.prompt_release_id:
        raise ValueError("RAG backend returned another prompt release")
    if source_revision != executor.source_revision:
        raise ValueError("RAG backend returned another source revision")
    for field in ("retrieval_result_id", "answer_id", "trace_id"):
        _require_hex(result.get(field), length=64, field=field)
    latency = result.get("latency_ms")
    if (
        isinstance(latency, bool)
        or not isinstance(latency, (int, float))
        or not math.isfinite(float(latency))
        or float(latency) < 0.0
    ):
        raise ValueError("RAG backend latency_ms must be finite and non-negative")
    citations = result.get("citations")
    if not isinstance(citations, list):
        raise ValueError("RAG backend citations must be a list")
    for citation in citations:
        if not isinstance(citation, dict):
            raise ValueError("RAG backend citation must be an object")
        if "chunk_id" in citation:
            _require_hex(citation["chunk_id"], length=64, field="citation.chunk_id")
    if status == "answered":
        answer = result.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("answered RAG result requires non-empty answer")
        if result.get("abstention_reason") is not None:
            raise ValueError("answered RAG result cannot carry abstention_reason")
        if not citations:
            raise ValueError("answered RAG result requires citations")
    else:
        reason = result.get("abstention_reason")
        if result.get("answer") is not None:
            raise ValueError("abstained RAG result must not contain answer")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("abstained RAG result requires abstention_reason")
        if citations:
            raise ValueError("abstained RAG result must not contain citations")
    return dict(result)


def _rag_result_to_agent_context(result: Mapping[str, Any]) -> dict[str, Any]:
    chunk_ids: list[str] = []
    for citation in result["citations"]:
        if "chunk_id" not in citation:
            raise ValueError("agent knowledge context requires chunk_id on every citation")
        chunk_ids.append(
            _require_hex(citation["chunk_id"], length=64, field="citation.chunk_id")
        )
    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("agent knowledge context contains duplicate chunk citations")
    return {
        "status": result["status"],
        "prompt_release_id": result["prompt_release_id"],
        "source_revision": result["source_revision"],
        "answer_id": result["answer_id"],
        "trace_id": result["trace_id"],
        "chunk_ids": chunk_ids,
        "text": result["answer"],
        "abstention_reason": result["abstention_reason"],
    }


def _validate_agent_plan_result(
    result: Mapping[str, Any], *, executor: AgentExecutor
) -> dict[str, Any]:
    if not isinstance(result, Mapping):
        raise ValueError("agent planning result must be an object")
    keys = set(result)
    if keys not in {
        frozenset(AGENT_PLAN_BASE_KEYS),
        frozenset(AGENT_PLAN_BASE_KEYS | {"retrieval_context_id"}),
    }:
        raise ValueError("agent planning result keys mismatch")
    if result.get("status") != "planned":
        raise ValueError("agent planning result status must equal planned")
    for field in ("incident_id", "inspection_id", "diagnostic_id", "plan_id", "policy_id"):
        _require_hex(result.get(field), length=64, field=f"agent.{field}")
    if "retrieval_context_id" in result and result.get("retrieval_context_id") is not None:
        _require_hex(
            result.get("retrieval_context_id"),
            length=64,
            field="agent.retrieval_context_id",
        )
    if result["policy_id"] != executor.policy_id:
        raise ValueError("agent planning result belongs to another policy")
    if result.get("policy_generation") != executor.policy_generation:
        raise ValueError("agent planning result belongs to another policy generation")
    target = result.get("target")
    if not isinstance(target, str) or not target:
        raise ValueError("agent planning result target is invalid")
    disposition = result.get("disposition")
    if disposition == "approval_required":
        if result.get("tool") != "restart_service":
            raise ValueError("approval-required agent plan must use restart_service")
        _require_hex(result.get("action_digest"), length=64, field="agent.action_digest")
    elif disposition in {"no_action", "abstained"}:
        if result.get("tool") is not None or result.get("action_digest") is not None:
            raise ValueError("non-mutating agent plan must not expose a mutation action")
    else:
        raise ValueError("agent planning disposition is unsupported")
    return dict(result)


def _validate_agent_remediation_result(
    result: Mapping[str, Any], *, executor: AgentExecutor
) -> dict[str, Any]:
    if not isinstance(result, Mapping) or set(result) != AGENT_REMEDIATION_RESULT_KEYS:
        raise ValueError("agent remediation result keys mismatch")
    if result.get("status") not in {"completed", "already_completed", "recovered_completed"}:
        raise ValueError("agent remediation result status is unsupported")
    for field in (
        "plan_id",
        "approval_id",
        "operation_id",
        "state_id",
        "result_id",
        "policy_id",
    ):
        _require_hex(result.get(field), length=64, field=f"agent.{field}")
    if result["policy_id"] != executor.policy_id:
        raise ValueError("agent remediation result belongs to another policy")
    if result.get("policy_generation") != executor.policy_generation:
        raise ValueError("agent remediation result belongs to another policy generation")
    if result.get("tool") != "restart_service":
        raise ValueError("agent remediation result tool is unsupported")
    if not isinstance(result.get("target"), str) or not result["target"]:
        raise ValueError("agent remediation result target is invalid")
    output = result.get("output")
    if not isinstance(output, dict) or set(output) != {
        "previous_generation",
        "current_generation",
        "status",
    }:
        raise ValueError("agent remediation output schema mismatch")
    previous = output.get("previous_generation")
    current = output.get("current_generation")
    if (
        isinstance(previous, bool)
        or not isinstance(previous, int)
        or previous < 1
        or isinstance(current, bool)
        or not isinstance(current, int)
        or current != previous + 1
        or output.get("status") != "healthy"
    ):
        raise ValueError("agent remediation output values are invalid")
    return dict(result)


def create_app(
    *,
    issuer: str | None = None,
    audience: str = "knowledge-hub-api",
    signing_keys: SigningKeyResolver | None = None,
    rag_executor: RagExecutor | None = None,
    agent_executor: AgentExecutor | None = None,
) -> FastAPI:
    resolved_issuer = issuer or os.environ.get(
        "KEYCLOAK_ISSUER", "http://127.0.0.1:8080/realms/knowledge-hub"
    )
    resolver = signing_keys or JwksSigningKeyResolver(
        f"{resolved_issuer.rstrip('/')}/protocol/openid-connect/certs"
    )
    app = FastAPI(title="Knowledge Hub Keycloak AI API authorization gateway")
    route_policies = {
        "rag.read": policy(
            issuer=resolved_issuer,
            audience=audience,
            allowed_azp={"knowledge-hub-web", "knowledge-hub-automation"},
            required_roles={"rag.read"},
            required_scopes={REQUIRED_API_SCOPE},
        ),
        "agent.run": policy(
            issuer=resolved_issuer,
            audience=audience,
            allowed_azp={"knowledge-hub-automation"},
            required_roles={"agent.run"},
            required_scopes={REQUIRED_API_SCOPE},
        ),
        "agent.remediate": policy(
            issuer=resolved_issuer,
            audience=audience,
            allowed_azp={"knowledge-hub-automation"},
            required_roles={"agent.remediate"},
            required_scopes={REQUIRED_API_SCOPE},
        ),
    }

    def require(action: str) -> Callable[..., Principal]:
        def dependency(
            credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
        ) -> Principal:
            if credentials is None or credentials.scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=401,
                    detail="bearer token required",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            try:
                return validate_access_token(
                    credentials.credentials,
                    policy=route_policies[action],
                    signing_keys=resolver,
                )
            except AuthenticationError as exc:
                raise HTTPException(
                    status_code=401,
                    detail=str(exc),
                    headers={"WWW-Authenticate": "Bearer"},
                ) from exc
            except ForbiddenError as exc:
                raise HTTPException(status_code=403, detail=str(exc)) from exc

        return dependency

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {
            "status": "ok",
            "rag_backend": "configured" if rag_executor is not None else "not_configured",
            "agent_backend": "configured" if agent_executor is not None else "not_configured",
        }

    @app.get("/readyz")
    def readyz() -> dict[str, str]:
        if rag_executor is None:
            raise HTTPException(status_code=503, detail="promoted RAG backend is not configured")
        return {
            "status": "ready",
            "prompt_release_id": rag_executor.prompt_release_id,
            "source_revision": rag_executor.source_revision,
        }

    @app.get("/readyz/agent")
    def agent_readyz() -> dict[str, str]:
        if agent_executor is None:
            raise HTTPException(status_code=503, detail="bounded agent backend is not configured")
        policy_id = _require_hex(agent_executor.policy_id, length=64, field="agent policy_id")
        generation = agent_executor.policy_generation
        if not isinstance(generation, str) or not generation.strip():
            raise HTTPException(status_code=503, detail="bounded agent policy generation is invalid")
        return {
            "status": "ready",
            "policy_id": policy_id,
            "policy_generation": generation,
        }

    @app.post("/v1/rag/query")
    def rag_query(
        request: RagQueryRequest,
        principal: Principal = Depends(require("rag.read")),
    ) -> dict[str, object]:
        if rag_executor is None:
            raise HTTPException(status_code=503, detail="promoted RAG backend is not configured")
        try:
            result = rag_executor.query(request.query)
            validated = _validate_rag_result(result, executor=rag_executor)
        except (RagBridgeError, ValueError) as exc:
            raise HTTPException(status_code=503, detail=f"RAG backend refused execution: {exc}") from exc
        except Exception as exc:
            raise HTTPException(status_code=503, detail="RAG backend execution failed") from exc
        return {
            "status": "completed",
            "action": "rag.read",
            "principal": _principal_json(principal),
            "rag": validated,
        }

    @app.post("/v1/agent/run")
    def agent_run(
        request: AgentPlanRequest,
        principal: Principal = Depends(require("agent.run")),
    ) -> dict[str, object]:
        if agent_executor is None:
            raise HTTPException(status_code=503, detail="bounded agent backend is not configured")

        retrieval_context: dict[str, Any] | None = None
        if request.knowledge_query is not None:
            if rag_executor is None:
                raise HTTPException(
                    status_code=503,
                    detail="promoted RAG backend is required for knowledge_query",
                )
            try:
                rag_result = rag_executor.query(request.knowledge_query)
                validated_rag = _validate_rag_result(rag_result, executor=rag_executor)
                retrieval_context = _rag_result_to_agent_context(validated_rag)
            except (RagBridgeError, ValueError) as exc:
                raise HTTPException(
                    status_code=503,
                    detail=f"agent knowledge retrieval refused: {exc}",
                ) from exc
            except Exception as exc:
                raise HTTPException(
                    status_code=503,
                    detail="agent knowledge retrieval failed",
                ) from exc

        try:
            if retrieval_context is None:
                result = agent_executor.plan(
                    target=request.target,
                    signal=request.signal,
                    operator_note=request.operator_note,
                    incident_generation=request.incident_generation,
                )
            else:
                result = agent_executor.plan(
                    target=request.target,
                    signal=request.signal,
                    operator_note=request.operator_note,
                    incident_generation=request.incident_generation,
                    retrieval_context=retrieval_context,
                )
            validated = _validate_agent_plan_result(result, executor=agent_executor)
        except (AgentBridgeError, ValueError) as exc:
            raise HTTPException(status_code=409, detail=f"agent planning refused: {exc}") from exc
        except Exception as exc:
            raise HTTPException(status_code=503, detail="agent planning backend failed") from exc
        return {
            "status": "completed",
            "action": "agent.run",
            "principal": _principal_json(principal),
            "agent": validated,
        }

    @app.post("/v1/agent/remediate")
    def agent_remediate(
        request: AgentRemediateRequest,
        principal: Principal = Depends(require("agent.remediate")),
    ) -> dict[str, object]:
        if agent_executor is None:
            raise HTTPException(status_code=503, detail="bounded agent backend is not configured")
        try:
            result = agent_executor.remediate(
                plan_id=request.plan_id,
                approval_id=request.approval_id,
                recover_expected_state_id=request.recover_expected_state_id,
            )
            validated = _validate_agent_remediation_result(result, executor=agent_executor)
        except AgentExecutionRefusal as exc:
            raise HTTPException(
                status_code=409,
                detail={
                    "status": "execution_refused",
                    "message": str(exc),
                    **exc.evidence(),
                },
            ) from exc
        except (AgentBridgeError, ValueError) as exc:
            raise HTTPException(status_code=409, detail=f"agent remediation refused: {exc}") from exc
        except Exception as exc:
            raise HTTPException(status_code=503, detail="agent remediation backend failed") from exc
        return {
            "status": "completed",
            "action": "agent.remediate",
            "principal": _principal_json(principal),
            "agent": validated,
        }

    return app


app = create_app()
