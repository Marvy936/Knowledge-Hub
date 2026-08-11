from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any, Mapping, Sequence


LEGACY_DRIVER = Path(__file__).with_name("run_live_identity_gate.py")
SPEC = importlib.util.spec_from_file_location("keycloak_live_identity_gate_core", LEGACY_DRIVER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load identity gate lifecycle: {LEGACY_DRIVER}")
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)

IdentityRuntimeError = core.IdentityRuntimeError
_REQUIRED_API_ROLES = frozenset({"rag.read", "agent.run", "agent.remediate"})
_ORIGINAL_ADMIN_GET_CLIENT = core._admin_get_client


def _role_names(value: object, *, label: str) -> set[str]:
    if not isinstance(value, list):
        raise IdentityRuntimeError(f"{label} read-back must be a list")
    names: set[str] = set()
    for item in value:
        if not isinstance(item, Mapping):
            raise IdentityRuntimeError(f"{label} read-back contains a non-object role")
        name = item.get("name")
        if not isinstance(name, str) or not name:
            raise IdentityRuntimeError(f"{label} read-back contains a role without a name")
        names.add(name)
    return names


def _api_role_representations(
    admin_base: str,
    admin_token: str,
    api_client_id: str,
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for role_name in sorted(_REQUIRED_API_ROLES):
        _, value = core._json_request(
            f"{admin_base}/clients/{api_client_id}/roles/{urllib.parse.quote(role_name, safe='')}",
            bearer=admin_token,
            expected={200},
        )
        if not isinstance(value, dict) or value.get("name") != role_name:
            raise IdentityRuntimeError(
                f"Keycloak API role representation is invalid for {role_name}"
            )
        result[role_name] = value
    return result


def _ensure_automation_role_scope(admin_base: str, admin_token: str) -> None:
    automation = _ORIGINAL_ADMIN_GET_CLIENT(
        admin_base,
        admin_token,
        "knowledge-hub-automation",
    )
    api_client = _ORIGINAL_ADMIN_GET_CLIENT(
        admin_base,
        admin_token,
        "knowledge-hub-api",
    )
    automation_id = automation.get("id")
    api_id = api_client.get("id")
    if not isinstance(automation_id, str) or not automation_id:
        raise IdentityRuntimeError("automation client is missing internal ID")
    if not isinstance(api_id, str) or not api_id:
        raise IdentityRuntimeError("API client is missing internal ID")
    if automation.get("fullScopeAllowed") is not False:
        raise IdentityRuntimeError("automation client must keep fullScopeAllowed disabled")

    _, service_account = core._json_request(
        f"{admin_base}/clients/{automation_id}/service-account-user",
        bearer=admin_token,
        expected={200},
    )
    service_account_id = service_account.get("id") if isinstance(service_account, dict) else None
    if not isinstance(service_account_id, str) or not service_account_id:
        raise IdentityRuntimeError("automation service-account user is missing internal ID")

    _, assigned_value = core._json_request(
        f"{admin_base}/users/{service_account_id}/role-mappings/clients/{api_id}",
        bearer=admin_token,
        expected={200},
    )
    assigned = _role_names(assigned_value, label="service-account API role mapping")
    if not assigned.issubset(_REQUIRED_API_ROLES):
        raise IdentityRuntimeError(
            "service-account API role mapping contains roles outside the bounded allowlist"
        )

    _, scope_value = core._json_request(
        f"{admin_base}/clients/{automation_id}/scope-mappings/clients/{api_id}",
        bearer=admin_token,
        expected={200},
    )
    scoped = _role_names(scope_value, label="automation API role scope mapping")
    if not scoped.issubset(_REQUIRED_API_ROLES):
        raise IdentityRuntimeError(
            "automation API role scope mapping contains roles outside the bounded allowlist"
        )

    role_representations = _api_role_representations(admin_base, admin_token, api_id)
    missing_assigned = _REQUIRED_API_ROLES - assigned
    if missing_assigned:
        core._json_request(
            f"{admin_base}/users/{service_account_id}/role-mappings/clients/{api_id}",
            method="POST",
            bearer=admin_token,
            payload=[role_representations[name] for name in sorted(missing_assigned)],
            expected={204},
        )
    missing_scoped = _REQUIRED_API_ROLES - scoped
    if missing_scoped:
        core._json_request(
            f"{admin_base}/clients/{automation_id}/scope-mappings/clients/{api_id}",
            method="POST",
            bearer=admin_token,
            payload=[role_representations[name] for name in sorted(missing_scoped)],
            expected={204},
        )

    _, assigned_after_value = core._json_request(
        f"{admin_base}/users/{service_account_id}/role-mappings/clients/{api_id}",
        bearer=admin_token,
        expected={200},
    )
    _, scoped_after_value = core._json_request(
        f"{admin_base}/clients/{automation_id}/scope-mappings/clients/{api_id}",
        bearer=admin_token,
        expected={200},
    )
    assigned_after = _role_names(
        assigned_after_value,
        label="service-account API role mapping after bootstrap",
    )
    scoped_after = _role_names(
        scoped_after_value,
        label="automation API role scope mapping after bootstrap",
    )
    if assigned_after != _REQUIRED_API_ROLES:
        raise IdentityRuntimeError(
            "service-account API role mapping does not equal the bounded allowlist after bootstrap"
        )
    if scoped_after != _REQUIRED_API_ROLES:
        raise IdentityRuntimeError(
            "automation API role scope mapping does not equal the bounded allowlist after bootstrap"
        )


def _admin_get_client(admin_base: str, token: str, client_id: str) -> dict[str, Any]:
    value = _ORIGINAL_ADMIN_GET_CLIENT(admin_base, token, client_id)
    if client_id == "knowledge-hub-automation":
        _ensure_automation_role_scope(admin_base, token)
    return value


def _build_rag(repo_root: Path, runtime_root: Path, subject_sha: str) -> dict[str, Any]:
    try:
        from keycloak_ai_api.runtime_rag import RuntimeRagError, build_live_rag_bundle

        return build_live_rag_bundle(
            repo_root=repo_root,
            runtime_root=runtime_root,
            subject_sha=subject_sha,
        )
    except (ImportError, RuntimeRagError, OSError, RuntimeError, ValueError) as exc:
        raise IdentityRuntimeError(
            f"cannot build canonical promoted RAG bundle: {type(exc).__name__}: {exc}"
        ) from exc


def _log_tail(log_path: Path, limit: int = 6000) -> str:
    try:
        return log_path.read_text(encoding="utf-8", errors="replace")[-limit:]
    except OSError as exc:
        return f"<cannot read secured API log: {type(exc).__name__}: {exc}>"


def _start_api(
    *,
    repo_root: Path,
    issuer: str,
    rag: Mapping[str, Any],
    agent: Mapping[str, Path],
    agent_root: Path,
    host: str,
    port: int,
    log_path: Path,
    timeout_seconds: int,
) -> tuple[subprocess.Popen[str], Any]:
    handle = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            sys.executable,
            "labs/keycloak-ai-api/scripts/run_secured_agent_rag_api.py",
            "--issuer",
            issuer,
            "--manifest",
            str(rag["manifest"]),
            "--index",
            str(rag["index"]),
            "--runtime-config",
            str(rag["runtime_config"]),
            "--eval-cases",
            str(rag["eval_cases"]),
            "--eval-report",
            str(rag["eval_report"]),
            "--prompt-release",
            str(rag["prompt_release"]),
            "--tool-state",
            str(agent["tool_state"]),
            "--policy",
            str(agent["policy"]),
            "--kill-switch",
            str(agent["kill_switch"]),
            "--runtime-root",
            str(agent_root),
            "--host",
            host,
            "--port",
            str(port),
        ],
        cwd=repo_root,
        stdout=handle,
        stderr=subprocess.STDOUT,
        text=True,
        env={
            **os.environ,
            "PYTHONHASHSEED": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
        },
    )
    deadline = time.monotonic() + timeout_seconds
    last = "not attempted"
    while time.monotonic() < deadline:
        returncode = process.poll()
        if returncode is not None:
            handle.flush()
            handle.close()
            raise IdentityRuntimeError(
                f"secured API exited before readiness with code {returncode}\n"
                f"secured-api.log tail:\n{_log_tail(log_path)}"
            )
        try:
            status, value = core._json_request(
                f"http://{host}:{port}/healthz",
                timeout=2.0,
                expected={200},
            )
            if status == 200 and isinstance(value, dict):
                return process, handle
            last = f"HTTP {status}"
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
        time.sleep(1)

    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)
    handle.flush()
    handle.close()
    raise IdentityRuntimeError(
        f"secured API did not become ready: http://{host}:{port}/healthz: {last}\n"
        f"secured-api.log tail:\n{_log_tail(log_path)}"
    )


core._admin_get_client = _admin_get_client
core._build_rag = _build_rag
core._start_api = _start_api


def main(argv: Sequence[str] | None = None) -> int:
    return int(core.main(argv))


if __name__ == "__main__":
    raise SystemExit(main())
