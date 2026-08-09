from __future__ import annotations

import base64
import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_live_identity_gate.py"
SPEC = importlib.util.spec_from_file_location("run_live_identity_gate", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _token(signature: bytes = b"stable-signature-bytes") -> str:
    header = _b64url(json.dumps({"alg": "RS256", "kid": "kid-1"}).encode())
    payload = _b64url(json.dumps({"sub": "service-account"}).encode())
    return f"{header}.{payload}.{_b64url(signature)}"


def test_subject_sha_requires_exact_lowercase_git_sha1() -> None:
    assert gate._require_git_sha("a" * 40) == "a" * 40
    with pytest.raises(gate.IdentityRuntimeError, match="40-character"):
        gate._require_git_sha("a" * 39)
    with pytest.raises(gate.IdentityRuntimeError, match="40-character"):
        gate._require_git_sha("A" * 40)


def test_signature_tamper_changes_decoded_signature_bytes() -> None:
    original = _token()
    tampered = gate._tamper_jwt_signature(original)

    assert tampered != original
    original_signature = gate._b64url_decode(original.split(".")[2])
    tampered_signature = gate._b64url_decode(tampered.split(".")[2])
    assert tampered_signature != original_signature
    assert tampered.split(".")[:2] == original.split(".")[:2]


def test_signature_tamper_refuses_malformed_token() -> None:
    with pytest.raises(gate.IdentityRuntimeError, match="malformed"):
        gate._tamper_jwt_signature("not-a-jwt")


def test_claim_normalizers_keep_authorization_dimensions_separate() -> None:
    claims = {
        "aud": ["knowledge-hub-api"],
        "scope": "openid profile knowledge-hub-api-access",
        "resource_access": {
            "knowledge-hub-api": {
                "roles": ["rag.read", "agent.run", "agent.remediate"]
            }
        },
    }
    assert gate._audiences(claims) == {"knowledge-hub-api"}
    assert gate._scopes(claims) == {
        "openid",
        "profile",
        "knowledge-hub-api-access",
    }
    assert gate._client_roles(claims, "knowledge-hub-api") == {
        "rag.read",
        "agent.run",
        "agent.remediate",
    }
    assert gate._client_roles(claims, "other-client") == set()


def test_service_state_reads_canonical_service_envelope() -> None:
    state = {
        "services": {
            "payments-api": {
                "generation": 2,
                "status": "healthy",
                "restart_count": 1,
            }
        }
    }
    assert gate._service_state(state, "payments-api") == {
        "generation": 2,
        "status": "healthy",
        "restart_count": 1,
    }
    with pytest.raises(gate.IdentityRuntimeError, match="does not expose target"):
        gate._service_state(state, "missing")


def test_query_is_derived_from_actual_chunk_text() -> None:
    chunks = [
        {"chunk_id": "a" * 64},
        {
            "chunk_id": "b" * 64,
            "text": "Exact issuer audience scope and client role validation",
        },
    ]
    query = gate._query_from_chunks(chunks)
    assert query.startswith("Exact issuer audience")
    assert "client" in query


def test_chunk_discovery_deduplicates_canonical_chunk_ids() -> None:
    first = {"chunk_id": "a" * 64, "text": "first"}
    second = {"chunk_id": "b" * 64, "text": "second"}
    manifest = {"files": [{"chunks": [second, first]}, {"copy": first}]}
    chunks = gate._chunk_records(manifest)
    assert [item["chunk_id"] for item in chunks] == ["a" * 64, "b" * 64]
