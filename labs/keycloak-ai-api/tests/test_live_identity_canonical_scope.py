from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_live_identity_gate_canonical.py"
SPEC = importlib.util.spec_from_file_location("live_identity_canonical_scope_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def _client(client_id: str, internal_id: str) -> dict[str, Any]:
    return {
        "clientId": client_id,
        "id": internal_id,
        "fullScopeAllowed": False,
    }


def test_scope_bootstrap_adds_only_missing_bounded_roles(monkeypatch: pytest.MonkeyPatch) -> None:
    clients = {
        "knowledge-hub-automation": _client("knowledge-hub-automation", "automation-id"),
        "knowledge-hub-api": _client("knowledge-hub-api", "api-id"),
    }
    monkeypatch.setattr(
        module,
        "_ORIGINAL_ADMIN_GET_CLIENT",
        lambda _base, _token, client_id: clients[client_id],
    )

    assigned = {"rag.read"}
    scoped = {"rag.read", "agent.run"}
    posts: list[tuple[str, list[str]]] = []

    def fake_json_request(
        url: str,
        *,
        method: str = "GET",
        bearer: str | None = None,
        payload: object | None = None,
        timeout: float = 10.0,
        expected: set[int] | None = None,
    ) -> tuple[int, Any]:
        del bearer, timeout, expected
        if url.endswith("/clients/automation-id/service-account-user"):
            return 200, {"id": "service-user-id"}
        if "/clients/api-id/roles/" in url:
            name = url.rsplit("/", 1)[-1]
            return 200, {"id": f"role-{name}", "name": name}
        if url.endswith("/users/service-user-id/role-mappings/clients/api-id"):
            if method == "POST":
                assert isinstance(payload, list)
                names = [item["name"] for item in payload if isinstance(item, dict)]
                posts.append(("assigned", names))
                assigned.update(names)
                return 204, None
            return 200, [{"name": name} for name in sorted(assigned)]
        if url.endswith("/clients/automation-id/scope-mappings/clients/api-id"):
            if method == "POST":
                assert isinstance(payload, list)
                names = [item["name"] for item in payload if isinstance(item, dict)]
                posts.append(("scoped", names))
                scoped.update(names)
                return 204, None
            return 200, [{"name": name} for name in sorted(scoped)]
        raise AssertionError(f"unexpected request: {method} {url}")

    monkeypatch.setattr(module.core, "_json_request", fake_json_request)
    module._ensure_automation_role_scope("http://keycloak/admin", "admin-token")

    assert posts == [
        ("assigned", ["agent.remediate", "agent.run"]),
        ("scoped", ["agent.remediate"]),
    ]
    assert assigned == module._REQUIRED_API_ROLES
    assert scoped == module._REQUIRED_API_ROLES


def test_scope_bootstrap_refuses_roles_outside_allowlist(monkeypatch: pytest.MonkeyPatch) -> None:
    clients = {
        "knowledge-hub-automation": _client("knowledge-hub-automation", "automation-id"),
        "knowledge-hub-api": _client("knowledge-hub-api", "api-id"),
    }
    monkeypatch.setattr(
        module,
        "_ORIGINAL_ADMIN_GET_CLIENT",
        lambda _base, _token, client_id: clients[client_id],
    )

    def fake_json_request(
        url: str,
        *,
        method: str = "GET",
        bearer: str | None = None,
        payload: object | None = None,
        timeout: float = 10.0,
        expected: set[int] | None = None,
    ) -> tuple[int, Any]:
        del method, bearer, payload, timeout, expected
        if url.endswith("/clients/automation-id/service-account-user"):
            return 200, {"id": "service-user-id"}
        if url.endswith("/users/service-user-id/role-mappings/clients/api-id"):
            return 200, [{"name": "rag.read"}, {"name": "unexpected.admin"}]
        raise AssertionError(f"unexpected request: {url}")

    monkeypatch.setattr(module.core, "_json_request", fake_json_request)
    with pytest.raises(
        module.IdentityRuntimeError,
        match="outside the bounded allowlist",
    ):
        module._ensure_automation_role_scope("http://keycloak/admin", "admin-token")


def test_protected_api_uses_execution_timeout_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: dict[str, Any] = {}

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return b'{"status":"completed"}'

    def fake_urlopen(request, *, timeout: float):
        observed["url"] = request.full_url
        observed["authorization"] = request.get_header("Authorization")
        observed["timeout"] = timeout
        return Response()

    monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)
    status, value = module._api_json(
        "http://127.0.0.1:18091",
        "/v1/rag/query",
        token="signed-token",
        payload={"query": "Kubernetes Service"},
    )

    assert status == 200
    assert value == {"status": "completed"}
    assert observed == {
        "url": "http://127.0.0.1:18091/v1/rag/query",
        "authorization": "Bearer signed-token",
        "timeout": module._PROTECTED_API_TIMEOUT_SECONDS,
    }
    assert module._PROTECTED_API_TIMEOUT_SECONDS == 120.0


def test_protected_api_timeout_reports_exact_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    def timeout_urlopen(_request, *, timeout: float):
        assert timeout == module._PROTECTED_API_TIMEOUT_SECONDS
        raise TimeoutError("timed out")

    monkeypatch.setattr(module.urllib.request, "urlopen", timeout_urlopen)
    with pytest.raises(
        module.IdentityRuntimeError,
        match=r"protected API /v1/agent/run timed out after 120s",
    ):
        module._api_json(
            "http://127.0.0.1:18091",
            "/v1/agent/run",
            token="signed-token",
            payload={"target": "payments-api"},
        )


def test_control_plane_timeout_keeps_short_budget_and_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def timeout_request(
        url: str,
        *,
        method: str = "GET",
        bearer: str | None = None,
        payload: object | None = None,
        timeout: float = 10.0,
        expected: set[int] | None = None,
    ) -> tuple[int, Any]:
        del url, method, bearer, payload, timeout, expected
        raise TimeoutError("timed out")

    monkeypatch.setattr(module, "_ORIGINAL_JSON_REQUEST", timeout_request)
    with pytest.raises(
        module.IdentityRuntimeError,
        match=r"HTTP GET http://keycloak/admin timed out after 10s",
    ):
        module._json_request("http://keycloak/admin")
