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
