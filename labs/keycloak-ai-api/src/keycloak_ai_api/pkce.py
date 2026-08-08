from __future__ import annotations

import base64
import hashlib
import secrets
from dataclasses import dataclass
from urllib.parse import urlencode


@dataclass(frozen=True)
class PkceAuthorizationRequest:
    authorization_url: str
    code_verifier: str
    state: str
    nonce: str


def _b64url_no_padding(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


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
    if not issuer.startswith(("https://", "http://127.0.0.1:", "http://localhost:")):
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
