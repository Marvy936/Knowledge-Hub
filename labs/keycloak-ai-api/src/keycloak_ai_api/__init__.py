"""Keycloak-secured AI API identity and authorization contracts."""

from .app import create_app
from .auth import (
    AuthenticationError,
    ForbiddenError,
    JwksSigningKeyResolver,
    Principal,
    TokenPolicy,
    policy,
    validate_access_token,
)
from .pkce import (
    PkceAuthorizationRequest,
    build_authorization_request,
    code_challenge_s256,
    generate_code_verifier,
)

__all__ = [
    "AuthenticationError",
    "ForbiddenError",
    "JwksSigningKeyResolver",
    "PkceAuthorizationRequest",
    "Principal",
    "TokenPolicy",
    "build_authorization_request",
    "code_challenge_s256",
    "create_app",
    "generate_code_verifier",
    "policy",
    "validate_access_token",
]
