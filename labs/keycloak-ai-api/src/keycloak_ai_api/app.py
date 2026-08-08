from __future__ import annotations

import os
from dataclasses import asdict
from typing import Callable

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth import (
    AuthorizationError,
    JwksSigningKeyResolver,
    Principal,
    SigningKeyResolver,
    policy,
    validate_access_token,
)

bearer = HTTPBearer(auto_error=False)


def create_app(
    *,
    issuer: str | None = None,
    audience: str = "knowledge-hub-api",
    signing_keys: SigningKeyResolver | None = None,
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
                raise HTTPException(status_code=401, detail="bearer token required")
            try:
                return validate_access_token(
                    credentials.credentials,
                    policy=route_policies[action],
                    signing_keys=resolver,
                )
            except AuthorizationError as exc:
                raise HTTPException(status_code=403, detail=str(exc)) from exc

        return dependency

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/rag/query")
    def rag_query(principal: Principal = Depends(require("rag.read"))) -> dict[str, object]:
        return {
            "status": "authorized",
            "action": "rag.read",
            "principal": asdict(principal),
            "boundary": "authorization-only; RAG execution is not performed by this foundation endpoint",
        }

    @app.post("/v1/agent/run")
    def agent_run(principal: Principal = Depends(require("agent.run"))) -> dict[str, object]:
        return {
            "status": "authorized",
            "action": "agent.run",
            "principal": asdict(principal),
            "boundary": "authorization-only; agent execution is not performed by this foundation endpoint",
        }

    @app.post("/v1/agent/remediate")
    def agent_remediate(
        principal: Principal = Depends(require("agent.remediate")),
    ) -> dict[str, object]:
        return {
            "status": "authorized",
            "action": "agent.remediate",
            "principal": asdict(principal),
            "boundary": "authorization-only; remediation is not performed by this foundation endpoint",
        }

    return app


app = create_app()
