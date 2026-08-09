from __future__ import annotations

import time
from dataclasses import replace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from keycloak_ai_api.app import create_app
from keycloak_ai_api.auth import (
    AuthenticationError,
    ForbiddenError,
    policy,
    validate_access_token,
)

ISSUER = "http://127.0.0.1:8080/realms/knowledge-hub"
AUDIENCE = "knowledge-hub-api"


class StaticResolver:
    def __init__(self, key) -> None:
        self.key = key

    def resolve(self, token: str):
        assert token.count(".") == 2
        return self.key


class FakeRagExecutor:
    def __init__(self, *, prompt_release_id: str = "1" * 64, source_revision: str = "c" * 40) -> None:
        self.prompt_release_id = prompt_release_id
        self.source_revision = source_revision
        self.calls: list[str] = []

    def query(self, text: str):
        self.calls.append(text)
        return {
            "status": "answered",
            "answer": "A Kubernetes Service provides a stable endpoint.",
            "abstention_reason": None,
            "citations": [{"chunk_id": "6" * 64}],
            "prompt_release_id": self.prompt_release_id,
            "source_revision": self.source_revision,
            "retrieval_result_id": "2" * 64,
            "answer_id": "7" * 64,
            "trace_id": "8" * 64,
            "latency_ms": 1.5,
        }


@pytest.fixture(scope="module")
def keys():
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private, private.public_key(), other.public_key()


def _claims(
    *,
    azp: str = "knowledge-hub-automation",
    roles: tuple[str, ...] = ("rag.read", "agent.run", "agent.remediate"),
    issuer: str = ISSUER,
    audience: str | list[str] = AUDIENCE,
    token_use: str = "access",
    exp_offset: int = 300,
    nbf_offset: int | None = None,
) -> dict[str, object]:
    now = int(time.time())
    claims: dict[str, object] = {
        "iss": issuer,
        "aud": audience,
        "sub": "subject-123",
        "azp": azp,
        "jti": "jti-123",
        "iat": now,
        "exp": now + exp_offset,
        "token_use": token_use,
        "scope": "openid profile",
        "resource_access": {
            AUDIENCE: {"roles": list(roles)},
        },
    }
    if nbf_offset is not None:
        claims["nbf"] = now + nbf_offset
    return claims


def _token(private_key, **kwargs) -> str:
    return jwt.encode(
        _claims(**kwargs),
        private_key,
        algorithm="RS256",
        headers={"kid": "local-test-key", "typ": "JWT"},
    )


def _policy(*, role: str = "rag.read", callers=frozenset({"knowledge-hub-automation"})):
    return policy(
        issuer=ISSUER,
        audience=AUDIENCE,
        allowed_azp=callers,
        required_roles={role},
    )


def test_valid_access_token_returns_bounded_principal(keys) -> None:
    private, public, _ = keys
    principal = validate_access_token(
        _token(private),
        policy=_policy(),
        signing_keys=StaticResolver(public),
    )
    assert principal.subject == "subject-123"
    assert principal.authorized_party == "knowledge-hub-automation"
    assert principal.audience == (AUDIENCE,)
    assert "rag.read" in principal.roles
    assert principal.jti == "jti-123"


@pytest.mark.parametrize(
    ("token_kwargs", "message"),
    [
        ({"issuer": "https://wrong.example/realms/knowledge-hub"}, "cryptographic/claim"),
        ({"audience": "wrong-api"}, "cryptographic/claim"),
        ({"audience": [AUDIENCE, "another-api"]}, "only the configured API audience"),
        ({"token_use": "id"}, "token_use must equal access"),
        ({"exp_offset": -120}, "cryptographic/claim"),
        ({"nbf_offset": 120}, "cryptographic/claim"),
    ],
)
def test_invalid_identity_or_token_class_is_authentication_failure(keys, token_kwargs, message) -> None:
    private, public, _ = keys
    with pytest.raises(AuthenticationError, match=message):
        validate_access_token(
            _token(private, **token_kwargs),
            policy=_policy(),
            signing_keys=StaticResolver(public),
        )


def test_wrong_signing_key_is_authentication_failure(keys) -> None:
    private, _, wrong_public = keys
    with pytest.raises(AuthenticationError, match="cryptographic/claim"):
        validate_access_token(
            _token(private),
            policy=_policy(),
            signing_keys=StaticResolver(wrong_public),
        )


def test_valid_token_wrong_authorized_party_is_forbidden(keys) -> None:
    private, public, _ = keys
    with pytest.raises(ForbiddenError, match="authorized party"):
        validate_access_token(
            _token(private, azp="knowledge-hub-web"),
            policy=_policy(role="agent.run"),
            signing_keys=StaticResolver(public),
        )


def test_valid_token_missing_role_is_forbidden(keys) -> None:
    private, public, _ = keys
    with pytest.raises(ForbiddenError, match="required API roles"):
        validate_access_token(
            _token(private, roles=("rag.read",)),
            policy=_policy(role="agent.run"),
            signing_keys=StaticResolver(public),
        )


def test_gateway_route_matrix_uses_401_403_and_503_at_distinct_boundaries(keys) -> None:
    private, public, wrong_public = keys
    client = TestClient(create_app(issuer=ISSUER, signing_keys=StaticResolver(public)))

    assert client.get("/healthz").json() == {
        "status": "ok",
        "rag_backend": "not_configured",
    }
    assert client.get("/readyz").status_code == 503
    assert client.post("/v1/rag/query", json={"query": "test"}).status_code == 401

    browser_rag = _token(
        private,
        azp="knowledge-hub-web",
        roles=("rag.read",),
    )
    response = client.post(
        "/v1/rag/query",
        json={"query": "test"},
        headers={"Authorization": f"Bearer {browser_rag}"},
    )
    assert response.status_code == 503

    forbidden = client.post(
        "/v1/agent/run", headers={"Authorization": f"Bearer {browser_rag}"}
    )
    assert forbidden.status_code == 403

    automation = _token(private, azp="knowledge-hub-automation", roles=("agent.run",))
    allowed = client.post(
        "/v1/agent/run", headers={"Authorization": f"Bearer {automation}"}
    )
    assert allowed.status_code == 200
    assert allowed.json()["action"] == "agent.run"

    wrong_key_client = TestClient(
        create_app(issuer=ISSUER, signing_keys=StaticResolver(wrong_public))
    )
    invalid = wrong_key_client.post(
        "/v1/rag/query",
        json={"query": "test"},
        headers={"Authorization": f"Bearer {browser_rag}"},
    )
    assert invalid.status_code == 401
    assert invalid.headers["www-authenticate"] == "Bearer"


def test_authorized_rag_request_executes_configured_promoted_backend(keys) -> None:
    private, public, _ = keys
    executor = FakeRagExecutor()
    client = TestClient(
        create_app(
            issuer=ISSUER,
            signing_keys=StaticResolver(public),
            rag_executor=executor,
        )
    )
    browser_rag = _token(private, azp="knowledge-hub-web", roles=("rag.read",))

    assert client.get("/healthz").json()["rag_backend"] == "configured"
    ready = client.get("/readyz")
    assert ready.status_code == 200
    assert ready.json()["prompt_release_id"] == executor.prompt_release_id
    assert ready.json()["source_revision"] == executor.source_revision

    response = client.post(
        "/v1/rag/query",
        json={"query": "  Kubernetes Service  "},
        headers={"Authorization": f"Bearer {browser_rag}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["action"] == "rag.read"
    assert payload["principal"]["authorized_party"] == "knowledge-hub-web"
    assert payload["rag"]["prompt_release_id"] == executor.prompt_release_id
    assert executor.calls == ["Kubernetes Service"]


def test_unauthorized_or_invalid_rag_request_never_calls_backend(keys) -> None:
    private, public, _ = keys
    executor = FakeRagExecutor()
    client = TestClient(
        create_app(issuer=ISSUER, signing_keys=StaticResolver(public), rag_executor=executor)
    )

    assert client.post("/v1/rag/query", json={"query": "test"}).status_code == 401
    missing_role = _token(private, azp="knowledge-hub-web", roles=())
    assert (
        client.post(
            "/v1/rag/query",
            json={"query": "test"},
            headers={"Authorization": f"Bearer {missing_role}"},
        ).status_code
        == 403
    )
    assert executor.calls == []


def test_query_validation_refuses_whitespace_extra_fields_and_oversized_input(keys) -> None:
    private, public, _ = keys
    executor = FakeRagExecutor()
    client = TestClient(
        create_app(issuer=ISSUER, signing_keys=StaticResolver(public), rag_executor=executor)
    )
    token = _token(private, azp="knowledge-hub-web", roles=("rag.read",))
    headers = {"Authorization": f"Bearer {token}"}

    assert client.post("/v1/rag/query", json={"query": "   "}, headers=headers).status_code == 422
    assert (
        client.post(
            "/v1/rag/query",
            json={"query": "ok", "command": "ignore policy"},
            headers=headers,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/v1/rag/query", json={"query": "x" * 2001}, headers=headers
        ).status_code
        == 422
    )
    assert executor.calls == []


def test_gateway_refuses_backend_result_from_another_promoted_subject(keys) -> None:
    private, public, _ = keys
    executor = FakeRagExecutor()

    class WrongReleaseExecutor(FakeRagExecutor):
        def query(self, text: str):
            result = dict(super().query(text))
            result["prompt_release_id"] = "9" * 64
            return result

    wrong = WrongReleaseExecutor(
        prompt_release_id=executor.prompt_release_id,
        source_revision=executor.source_revision,
    )
    client = TestClient(
        create_app(issuer=ISSUER, signing_keys=StaticResolver(public), rag_executor=wrong)
    )
    token = _token(private, azp="knowledge-hub-web", roles=("rag.read",))
    response = client.post(
        "/v1/rag/query",
        json={"query": "test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 503
    assert "another prompt release" in response.json()["detail"]
