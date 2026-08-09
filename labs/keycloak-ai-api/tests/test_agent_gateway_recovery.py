from __future__ import annotations

import time

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from keycloak_ai_api.agent_bridge import AgentExecutionRefusal
from keycloak_ai_api.app import create_app

ISSUER = "http://127.0.0.1:8080/realms/knowledge-hub"
AUDIENCE = "knowledge-hub-api"


class StaticResolver:
    def __init__(self, key) -> None:
        self.key = key

    def resolve(self, token: str):
        return self.key


class RefusingAgentExecutor:
    policy_id = "a" * 64
    policy_generation = "policy-v1"

    def plan(self, **kwargs):
        raise AssertionError("planning is not part of this recovery test")

    def remediate(self, **kwargs):
        raise AgentExecutionRefusal(
            "bounded remediation did not complete: transport acknowledgement lost",
            operation_id="6" * 64,
            state_id="7" * 64,
            phase="failed",
        )


def _token(private_key) -> str:
    now = int(time.time())
    return jwt.encode(
        {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "sub": "automation-subject",
            "azp": "knowledge-hub-automation",
            "jti": "recovery-test-jti",
            "iat": now,
            "exp": now + 300,
            "token_use": "access",
            "scope": "openid knowledge-hub-api-access",
            "resource_access": {AUDIENCE: {"roles": ["agent.remediate"]}},
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "local-test-key", "typ": "JWT"},
    )


def test_remediation_failure_returns_bounded_checkpoint_for_explicit_recovery() -> None:
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    client = TestClient(
        create_app(
            issuer=ISSUER,
            signing_keys=StaticResolver(private.public_key()),
            agent_executor=RefusingAgentExecutor(),
        )
    )
    response = client.post(
        "/v1/agent/remediate",
        json={"plan_id": "4" * 64, "approval_id": "5" * 64},
        headers={"Authorization": f"Bearer {_token(private)}"},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == {
        "status": "execution_refused",
        "message": "bounded remediation did not complete: transport acknowledgement lost",
        "operation_id": "6" * 64,
        "state_id": "7" * 64,
        "phase": "failed",
    }
