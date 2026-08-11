from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from keycloak_ai_api.pkce import build_authorization_request, code_challenge_s256


ROOT = Path(__file__).resolve().parents[1]


def test_realm_pins_pkce_audience_access_marker_and_service_account_roles() -> None:
    realm = json.loads((ROOT / "realm" / "knowledge-hub-realm.json").read_text(encoding="utf-8"))
    assert realm["realm"] == "knowledge-hub"
    assert realm["defaultSignatureAlgorithm"] == "RS256"

    clients = {client["clientId"]: client for client in realm["clients"]}
    web = clients["knowledge-hub-web"]
    assert web["publicClient"] is True
    assert web["standardFlowEnabled"] is True
    assert web["implicitFlowEnabled"] is False
    assert web["directAccessGrantsEnabled"] is False
    assert web["attributes"]["pkce.code.challenge.method"] == "S256"
    assert web["redirectUris"] == ["http://127.0.0.1:8765/callback"]

    automation = clients["knowledge-hub-automation"]
    assert automation["publicClient"] is False
    assert automation["serviceAccountsEnabled"] is True
    assert automation["standardFlowEnabled"] is False
    assert automation["directAccessGrantsEnabled"] is False
    assert automation["fullScopeAllowed"] is False
    assert "secret" not in automation

    role_scope_mappings = realm["clientScopeMappings"]["knowledge-hub-automation"]
    assert role_scope_mappings == [
        {
            "client": "knowledge-hub-api",
            "roles": ["rag.read", "agent.run", "agent.remediate"],
        }
    ]

    scopes = {scope["name"]: scope for scope in realm["clientScopes"]}
    api_scope = scopes["knowledge-hub-api-access"]
    mappers = {mapper["name"]: mapper for mapper in api_scope["protocolMappers"]}
    audience = mappers["knowledge-hub-api-audience"]
    assert audience["protocolMapper"] == "oidc-audience-mapper"
    assert audience["config"]["included.client.audience"] == "knowledge-hub-api"
    assert audience["config"]["access.token.claim"] == "true"
    assert audience["config"]["id.token.claim"] == "false"
    marker = mappers["knowledge-hub-access-token-marker"]
    assert marker["config"]["claim.name"] == "token_use"
    assert marker["config"]["claim.value"] == "access"
    assert marker["config"]["access.token.claim"] == "true"
    assert marker["config"]["id.token.claim"] == "false"
    roles_mapper = mappers["knowledge-hub-api-client-roles"]
    assert roles_mapper["protocolMapper"] == "oidc-usermodel-client-role-mapper"
    assert roles_mapper["config"]["usermodel.clientRoleMapping.clientId"] == "knowledge-hub-api"
    assert roles_mapper["config"]["claim.name"] == "resource_access.knowledge-hub-api.roles"
    assert roles_mapper["config"]["multivalued"] == "true"
    assert roles_mapper["config"]["access.token.claim"] == "true"
    assert roles_mapper["config"]["id.token.claim"] == "false"

    users = {user["username"]: user for user in realm["users"]}
    service = users["service-account-knowledge-hub-automation"]
    assert service["serviceAccountClientId"] == "knowledge-hub-automation"
    assert set(service["clientRoles"]["knowledge-hub-api"]) == {
        "rag.read",
        "agent.run",
        "agent.remediate",
    }


def test_pkce_request_uses_s256_state_nonce_and_exact_callback() -> None:
    request = build_authorization_request(
        issuer="http://127.0.0.1:8080/realms/knowledge-hub",
        client_id="knowledge-hub-web",
        redirect_uri="http://127.0.0.1:8765/callback",
    )
    parsed = urlparse(request.authorization_url)
    query = parse_qs(parsed.query)
    assert parsed.path.endswith("/protocol/openid-connect/auth")
    assert query["response_type"] == ["code"]
    assert query["client_id"] == ["knowledge-hub-web"]
    assert query["redirect_uri"] == ["http://127.0.0.1:8765/callback"]
    assert query["code_challenge_method"] == ["S256"]
    assert query["code_challenge"] == [code_challenge_s256(request.code_verifier)]
    assert query["state"] == [request.state]
    assert query["nonce"] == [request.nonce]
    assert 43 <= len(request.code_verifier) <= 128


def test_pkce_rejects_non_https_non_loopback_issuer() -> None:
    try:
        build_authorization_request(
            issuer="http://identity.example.test/realms/knowledge-hub",
            client_id="knowledge-hub-web",
            redirect_uri="http://127.0.0.1:8765/callback",
        )
    except ValueError as exc:
        assert "HTTPS or an explicit loopback" in str(exc)
    else:
        raise AssertionError("non-loopback HTTP issuer was accepted")
