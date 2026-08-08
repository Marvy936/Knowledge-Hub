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


def test_gateway_route_matrix_uses_401_for_bad_token_and_403_for_permissions(keys) -> None:
    private, public, wrong_public = keys
    client = TestClient(create_app(issuer=ISSUER, signing_keys=StaticResolver(public)))

    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.post("/v1/rag/query").status_code == 401

    browser_rag = _token(
        private,
        azp="knowledge-hub-web",
        roles=("rag.read",),
    )
    response = client.post(
        "/v1/rag/query", headers={"Authorization": f"Bearer {browser_rag}"}
    )
    assert response.status_code == 200
    assert response.json()["action"] == "rag.read"
    assert response.json()["principal"]["authorized_party"] == "knowledge-hub-web"

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
        "/v1/rag/query", headers={"Authorization": f"Bearer {browser_rag}"}
    )
    assert invalid.status_code == 401
    assert invalid.headers["www-authenticate"] == "Bearer"
