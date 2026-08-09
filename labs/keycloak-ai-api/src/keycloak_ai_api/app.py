from __future__ import annotations

import math
import os
from typing import Any, Callable, Mapping

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, field_validator

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


def create_app(
    *,
    issuer: str | None = None,
    audience: str = "knowledge-hub-api",
    signing_keys: SigningKeyResolver | None = None,
    rag_executor: RagExecutor | None = None,
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
        ),
        "agent.run": policy(
            issuer=resolved_issuer,
            audience=audience,
            allowed_azp={"knowledge-hub-automation"},
            required_roles={"agent.run"},
        ),
        "agent.remediate": policy(
            issuer=resolved_issuer,
            audience=audience,
            allowed_azp={"knowledge-hub-automation"},
            required_roles={"agent.remediate"},
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
    def agent_run(principal: Principal = Depends(require("agent.run"))) -> dict[str, object]:
        return {
            "status": "authorized",
            "action": "agent.run",
            "principal": _principal_json(principal),
            "boundary": "authorization-only; agent execution is not performed by this endpoint",
        }

    @app.post("/v1/agent/remediate")
    def agent_remediate(
        principal: Principal = Depends(require("agent.remediate")),
    ) -> dict[str, object]:
        return {
            "status": "authorized",
            "action": "agent.remediate",
            "principal": _principal_json(principal),
            "boundary": "authorization-only; remediation is not performed by this endpoint",
        }

    return app


app = create_app()
