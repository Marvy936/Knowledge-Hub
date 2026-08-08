from __future__ import annotations

import base64
import hashlib
import secrets
from dataclasses import dataclass
from urllib.parse import urlencode, urlparse


@dataclass(frozen=True)
class PkceAuthorizationRequest:
    authorization_url: str
    code_verifier: str
    state: str
    nonce: str


def _b64url_no_padding(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def endpoint_is_allowed(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme == "https":
        return bool(parsed.hostname)
    return parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost"}


def generate_code_verifier() -> str:
    verifier = _b64url_no_padding(secrets.token_bytes(48))
    if not 43 <= len(verifier) <= 128:
        raise RuntimeError("generated PKCE verifier is outside RFC 7636 length bounds")
    return verifier


def code_challenge_s256(verifier: str) -> str:
    if not isinstance(verifier, str) or not 43 <= len(verifier) <= 128:
        raise ValueError("PKCE verifier must be a 43-128 character string")
    return _b64url_no_padding(hashlib.sha256(verifier.encode("ascii")).digest())


def build_authorization_request(
    *,
    issuer: str,
    client_id: str,
    redirect_uri: str,
    scope: str = "openid profile",
) -> PkceAuthorizationRequest:
    if not endpoint_is_allowed(issuer):
        raise ValueError("issuer must use HTTPS or an explicit loopback HTTP endpoint")
    verifier = generate_code_verifier()
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    query = urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge_s256(verifier),
            "code_challenge_method": "S256",
        }
    )
    return PkceAuthorizationRequest(
        authorization_url=f"{issuer.rstrip('/')}/protocol/openid-connect/auth?{query}",
        code_verifier=verifier,
        state=state,
        nonce=nonce,
    )


def build_token_exchange_form(
    *,
    code: str,
    code_verifier: str,
    client_id: str,
    redirect_uri: str,
) -> dict[str, str]:
    if not isinstance(code, str) or not code.strip():
        raise ValueError("authorization code must be non-empty")
    code_challenge_s256(code_verifier)
    if not isinstance(client_id, str) or not client_id.strip():
        raise ValueError("client_id must be non-empty")
    if not isinstance(redirect_uri, str) or not redirect_uri.strip():
        raise ValueError("redirect_uri must be non-empty")
    return {
        "grant_type": "authorization_code",
        "code": code.strip(),
        "client_id": client_id.strip(),
        "redirect_uri": redirect_uri.strip(),
        "code_verifier": code_verifier,
    }
