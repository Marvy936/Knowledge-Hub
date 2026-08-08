from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol

import jwt
from jwt import PyJWKClient


class AuthorizationError(ValueError):
    """Base class for bounded bearer-token failures."""


class AuthenticationError(AuthorizationError):
    """Token cryptography, identity or required access-token claims are invalid."""


class ForbiddenError(AuthorizationError):
    """Token is valid but the caller or role is not authorized for the route."""


class SigningKeyResolver(Protocol):
    def resolve(self, token: str) -> Any: ...


class JwksSigningKeyResolver:
    def __init__(self, jwks_url: str) -> None:
        self._client = PyJWKClient(jwks_url, cache_keys=True)

    def resolve(self, token: str) -> Any:
        return self._client.get_signing_key_from_jwt(token).key


@dataclass(frozen=True)
class TokenPolicy:
    issuer: str
    audience: str
    allowed_azp: frozenset[str]
    required_roles: frozenset[str]
    leeway_seconds: int = 30


@dataclass(frozen=True)
class Principal:
    subject: str
    authorized_party: str
    audience: tuple[str, ...]
    roles: frozenset[str]
    scopes: frozenset[str]
    jti: str


def _auth_nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AuthenticationError(f"{field} must be a non-empty string")
    return value.strip()


def _config_nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _audiences(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        resolved = (_auth_nonempty(value, "aud"),)
    elif (
        isinstance(value, list)
        and value
        and all(isinstance(item, str) and item for item in value)
    ):
        resolved = tuple(value)
    else:
        raise AuthenticationError("aud must be a string or a non-empty string array")
    if len(set(resolved)) != len(resolved):
        raise AuthenticationError("aud contains duplicate audiences")
    return resolved


def _roles(claims: Mapping[str, Any], audience: str) -> frozenset[str]:
    resource_access = claims.get("resource_access")
    if not isinstance(resource_access, dict):
        return frozenset()
    resource = resource_access.get(audience)
    if not isinstance(resource, dict):
        return frozenset()
    roles = resource.get("roles")
    if not isinstance(roles, list) or not all(
        isinstance(role, str) and role for role in roles
    ):
        return frozenset()
    return frozenset(roles)


def _scopes(claims: Mapping[str, Any]) -> frozenset[str]:
    value = claims.get("scope")
    if value is None:
        return frozenset()
    if not isinstance(value, str):
        raise AuthenticationError("scope claim must be a space-delimited string")
    return frozenset(item for item in value.split() if item)


def validate_access_token(
    token: str,
    *,
    policy: TokenPolicy,
    signing_keys: SigningKeyResolver,
) -> Principal:
    if not isinstance(token, str) or token.count(".") != 2:
        raise AuthenticationError("bearer token must be a compact JWT")
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise AuthenticationError("bearer token header is invalid") from exc
    if header.get("alg") != "RS256":
        raise AuthenticationError("bearer token algorithm must be RS256")
    _auth_nonempty(header.get("kid"), "kid")

    try:
        key = signing_keys.resolve(token)
        claims = jwt.decode(
            token,
            key=key,
            algorithms=["RS256"],
            issuer=policy.issuer,
            audience=policy.audience,
            leeway=policy.leeway_seconds,
            options={
                "require": [
                    "exp",
                    "iat",
                    "iss",
                    "aud",
                    "sub",
                    "azp",
                    "jti",
                    "token_use",
                ],
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True,
                "verify_iss": True,
                "verify_aud": True,
            },
        )
    except (jwt.PyJWTError, ValueError) as exc:
        raise AuthenticationError(
            f"bearer token cryptographic/claim validation failed: {type(exc).__name__}"
        ) from exc

    if claims.get("token_use") != "access":
        raise AuthenticationError("token_use must equal access")
    audiences = _audiences(claims.get("aud"))
    if set(audiences) != {policy.audience}:
        raise AuthenticationError(
            "access token audience must contain only the configured API audience"
        )
    azp = _auth_nonempty(claims.get("azp"), "azp")
    if azp not in policy.allowed_azp:
        raise ForbiddenError("authorized party is not allowed for this route")
    roles = _roles(claims, policy.audience)
    missing = sorted(policy.required_roles - roles)
    if missing:
        raise ForbiddenError(f"required API roles are missing: {missing}")
    return Principal(
        subject=_auth_nonempty(claims.get("sub"), "sub"),
        authorized_party=azp,
        audience=audiences,
        roles=roles,
        scopes=_scopes(claims),
        jti=_auth_nonempty(claims.get("jti"), "jti"),
    )


def policy(
    *,
    issuer: str,
    audience: str,
    allowed_azp: Iterable[str],
    required_roles: Iterable[str],
) -> TokenPolicy:
    callers = frozenset(_config_nonempty(item, "allowed_azp") for item in allowed_azp)
    roles = frozenset(_config_nonempty(item, "required_role") for item in required_roles)
    if not callers:
        raise ValueError("route policy requires at least one allowed caller")
    return TokenPolicy(
        issuer=_config_nonempty(issuer, "issuer"),
        audience=_config_nonempty(audience, "audience"),
        allowed_azp=callers,
        required_roles=roles,
    )
