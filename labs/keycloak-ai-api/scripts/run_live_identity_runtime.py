from __future__ import annotations

import argparse
import base64
import json
import os
import re
import secrets
import shutil
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Mapping, Sequence


class IdentityRuntimeError(RuntimeError):
    pass


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Execute the Practical v1 live Keycloak realm/JWKS/service-account/protected "
            "RAG+agent identity path and bounded negative authorization matrix."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--subject-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--issuer",
        default="http://127.0.0.1:8080/realms/knowledge-hub",
    )
    parser.add_argument("--api-host", default="127.0.0.1")
    parser.add_argument("--api-port", type=int, default=18091)
    parser.add_argument("--startup-timeout-seconds", type=int, default=90)
    return parser


def _require_git_sha(value: str) -> str:
    text = value.strip()
    if len(text) != 40 or any(character not in "0123456789abcdef" for character in text):
        raise IdentityRuntimeError("subject SHA must be a lowercase 40-character Git SHA-1")
    return text


def _require_sha256(value: object, field: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise IdentityRuntimeError(f"{field} must be a lowercase SHA-256")
    return value


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    import hashlib

    return hashlib.sha256(value).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IdentityRuntimeError(f"cannot read JSON artifact {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise IdentityRuntimeError(f"JSON artifact must be an object: {path}")
    return value


def _atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
    env_extra: Mapping[str, str] | None = None,
    expected_codes: set[int] | None = None,
) -> subprocess.CompletedProcess[str]:
    allowed = {0} if expected_codes is None else expected_codes
    env = {
        **os.environ,
        "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if env_extra:
        env.update(env_extra)
    result = subprocess.run(
        list(command),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode not in allowed:
        raise IdentityRuntimeError(
            f"command returned {result.returncode}, expected {sorted(allowed)}: {' '.join(command)}\n"
            f"stdout tail:\n{(result.stdout or '')[-3000:]}\n"
            f"stderr tail:\n{(result.stderr or '')[-3000:]}"
        )
    return result


def _json_request(
    url: str,
    *,
    method: str = "GET",
    bearer: str | None = None,
    payload: object | None = None,
    timeout: float = 10.0,
    expected: set[int] | None = None,
) -> tuple[int, Any]:
    headers = {"Accept": "application/json"}
    body = None
    if bearer is not None:
        headers["Authorization"] = "Bearer " + bearer
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
            raw = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read()
    allowed = expected if expected is not None else {200}
    if status not in allowed:
        raise IdentityRuntimeError(f"HTTP {method} {url} returned unexpected status {status}")
    if not raw:
        return status, None
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IdentityRuntimeError(f"HTTP {method} {url} did not return JSON") from exc
    return status, value


def _form_request(
    url: str,
    *,
    values: Mapping[str, str],
    timeout: float = 10.0,
) -> dict[str, Any]:
    body = urllib.parse.urlencode(values).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            status = response.status
    except urllib.error.HTTPError as exc:
        raise IdentityRuntimeError(
            f"form POST to {url} returned HTTP {exc.code}"
        ) from exc
    if status != 200:
        raise IdentityRuntimeError(f"form POST to {url} returned HTTP {status}")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IdentityRuntimeError("form response is not JSON") from exc
    if not isinstance(value, dict):
        raise IdentityRuntimeError("form response must be a JSON object")
    return value


def _wait_json(url: str, timeout_seconds: int) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last = "not attempted"
    while time.monotonic() < deadline:
        try:
            status, value = _json_request(url, timeout=2.0, expected={200})
            if status == 200 and isinstance(value, dict):
                return value
            last = f"HTTP {status}"
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
        time.sleep(1)
    raise IdentityRuntimeError(f"endpoint did not become ready: {url}: {last}")


def _decode_jwt_payload(token: str) -> dict[str, Any]:
    parts = token.strip().split(".")
    if len(parts) != 3:
        raise IdentityRuntimeError("access token is not a compact JWT")
    segment = parts[1]
    segment += "=" * (-len(segment) % 4)
    try:
        value = json.loads(base64.urlsafe_b64decode(segment.encode("ascii")).decode("utf-8"))
    except Exception as exc:
        raise IdentityRuntimeError("cannot decode JWT payload") from exc
    if not isinstance(value, dict):
        raise IdentityRuntimeError("JWT payload must be an object")
    return value


def _audiences(payload: Mapping[str, Any]) -> set[str]:
    audience = payload.get("aud")
    if isinstance(audience, str):
        return {audience}
    if isinstance(audience, list) and all(isinstance(item, str) for item in audience):
        return set(audience)
    return set()


def _scopes(payload: Mapping[str, Any]) -> set[str]:
    scope = payload.get("scope")
    if not isinstance(scope, str):
        return set()
    return {item for item in scope.split() if item}


def _client_roles(payload: Mapping[str, Any], client_id: str) -> set[str]:
    resource_access = payload.get("resource_access")
    if not isinstance(resource_access, dict):
        return set()
    client = resource_access.get(client_id)
    if not isinstance(client, dict):
        return set()
    roles = client.get("roles")
    if not isinstance(roles, list):
        return set()
    return {role for role in roles if isinstance(role, str)}


def _walk(value: object):
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _chunk_records(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for item in _walk(manifest):
        if not isinstance(item, dict):
            continue
        chunk_id = item.get("chunk_id")
        if isinstance(chunk_id, str) and SHA256_RE.fullmatch(chunk_id):
            found[chunk_id] = item
    if not found:
        raise IdentityRuntimeError("RAG manifest contains no canonical chunks")
    return [found[key] for key in sorted(found)]


def _query_from_chunks(chunks: Sequence[Mapping[str, Any]]) -> str:
    for chunk in chunks:
        for field in ("text", "content", "body", "chunk_text"):
            value = chunk.get(field)
            if not isinstance(value, str):
                continue
            words = [word for word in re.findall(r"[A-Za-z0-9_./:-]+", value) if len(word) >= 3]
            if words:
                return " ".join(words[: min(8, len(words))])
    raise IdentityRuntimeError("cannot derive a positive query from the exact RAG corpus")


def _find_key(value: object, key: str) -> Any:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for item in value.values():
            found = _find_key(item, key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = _find_key(item, key)
            if found is not None:
                return found
    return None


def _service_state(tool_state: Mapping[str, Any], target: str) -> dict[str, Any]:
    services = tool_state.get("services")
    if isinstance(services, dict):
        value = services.get(target)
        if isinstance(value, dict):
            return value
    for item in _walk(tool_state):
        if isinstance(item, dict) and item.get("target") == target:
            if all(field in item for field in ("generation", "status", "restart_count")):
                return item
    raise IdentityRuntimeError(f"tool state does not expose target {target}")


def _api_json(
    base_url: str,
    path: str,
    *,
    token: str | None,
    payload: Mapping[str, Any],
) -> tuple[int, dict[str, Any]]:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token is not None:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(
        base_url + path,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        method="POST",
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            status = response.status
            raw = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read()
    try:
        value = json.loads(raw.decode("utf-8")) if raw else {}
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IdentityRuntimeError(f"protected API {path} returned non-JSON body") from exc
    if not isinstance(value, dict):
        raise IdentityRuntimeError(f"protected API {path} response must be an object")
    return status, value


def _admin_get_client(admin_base: str, token: str, client_id: str) -> dict[str, Any]:
    query = urllib.parse.urlencode({"clientId": client_id})
    _, value = _json_request(
        admin_base + "/clients?" + query,
        bearer=token,
        expected={200},
    )
    if not isinstance(value, list) or len(value) != 1 or not isinstance(value[0], dict):
        raise IdentityRuntimeError(f"Keycloak client lookup for {client_id} was not unique")
    return value[0]


def _admin_get_scope(admin_base: str, token: str, name: str) -> dict[str, Any]:
    _, value = _json_request(admin_base + "/client-scopes", bearer=token, expected={200})
    matches = [
        item
        for item in value
        if isinstance(item, dict) and item.get("name") == name
    ] if isinstance(value, list) else []
    if len(matches) != 1:
        raise IdentityRuntimeError(f"Keycloak client scope lookup for {name} was not unique")
    return matches[0]


def _issue_service_token(
    *,
    repo_root: Path,
    runtime_root: Path,
    secret: str,
    label: str,
    issuer: str,
) -> tuple[str, dict[str, Any]]:
    token_path = runtime_root / "tokens" / f"{label}.jwt"
    token_path.parent.mkdir(parents=True, exist_ok=True)
    if token_path.exists() or token_path.is_symlink():
        raise IdentityRuntimeError(f"token output already exists for {label}")
    _run(
        [
            sys.executable,
            "labs/keycloak-ai-api/scripts/request_client_credentials.py",
            "--token-output",
            str(token_path),
        ],
        cwd=repo_root,
        env_extra={
            "KEYCLOAK_AUTOMATION_CLIENT_SECRET": secret,
            "KEYCLOAK_ISSUER": issuer,
        },
    )
    token = token_path.read_text(encoding="utf-8").strip()
    if not token:
        raise IdentityRuntimeError(f"token helper wrote an empty token for {label}")
    return token, _decode_jwt_payload(token)


def _build_rag(repo_root: Path, runtime_root: Path, subject_sha: str) -> dict[str, Any]:
    rag = runtime_root / "rag"
    rag.mkdir(parents=True, exist_ok=False)
    manifest = rag / "manifest.json"
    index = rag / "index.json"
    config = rag / "runtime-config.json"
    evaluation = rag / "eval-report.json"
    release = rag / "prompt-release.json"
    preflight = rag / "preflight-query.json"
    cases = repo_root / "labs" / "llm-rag" / "data" / "eval-cases.json"

    _run(
        [sys.executable, "labs/llm-rag/scripts/build_corpus.py", "--repo", str(repo_root), "--revision", subject_sha, "--output", str(manifest)],
        cwd=repo_root,
    )
    manifest_value = _read_json(manifest)
    if manifest_value.get("source_revision") != subject_sha:
        raise IdentityRuntimeError("RAG corpus source revision mismatch")
    query = _query_from_chunks(_chunk_records(manifest_value))
    _run([sys.executable, "labs/llm-rag/scripts/build_index.py", "--manifest", str(manifest), "--output", str(index)], cwd=repo_root)
    _run([sys.executable, "labs/llm-rag/scripts/build_runtime_config.py", "--implementation-revision", subject_sha, "--output", str(config)], cwd=repo_root)
    _run(
        [sys.executable, "labs/llm-rag/scripts/run_evaluation.py", "--manifest", str(manifest), "--index", str(index), "--runtime-config", str(config), "--cases", str(cases), "--output", str(evaluation)],
        cwd=repo_root,
    )
    eval_value = _read_json(evaluation)
    if eval_value.get("all_passed") is not True or eval_value.get("failed_count") != 0:
        raise IdentityRuntimeError("promoted RAG evaluation is not all-passed")
    _run(
        [sys.executable, "labs/llm-rag/scripts/build_prompt_release.py", "--manifest", str(manifest), "--index", str(index), "--runtime-config", str(config), "--eval-report", str(evaluation), "--output", str(release)],
        cwd=repo_root,
    )
    _run(
        [sys.executable, "labs/llm-rag/scripts/query.py", "--manifest", str(manifest), "--index", str(index), "--query", query, "--output", str(preflight)],
        cwd=repo_root,
    )
    preflight_value = _read_json(preflight)
    if preflight_value.get("status") != "answered":
        raise IdentityRuntimeError("derived RAG query is not answered by promoted bundle")
    return {
        "manifest": manifest,
        "index": index,
        "runtime_config": config,
        "eval_cases": cases,
        "eval_report": evaluation,
        "prompt_release": release,
        "query": query,
        "snapshot_id": _require_sha256(manifest_value.get("snapshot_id"), "RAG snapshot_id"),
        "index_id": _require_sha256(_read_json(index).get("index_id"), "RAG index_id"),
        "report_id": _require_sha256(eval_value.get("report_id"), "RAG report_id"),
        "prompt_release_id": _require_sha256(_read_json(release).get("prompt_release_id"), "RAG prompt_release_id"),
    }


def _build_agent(repo_root: Path, runtime_root: Path) -> dict[str, Path]:
    tool_state = runtime_root / "tool-state.json"
    policy = runtime_root / "policy.json"
    kill_switch = runtime_root / "kill-switch.json"
    _run(
        [sys.executable, "labs/agent-ops/scripts/init_sandbox.py", "--target", "payments-api", "--status", "degraded", "--generation", "1", "--output", str(tool_state)],
        cwd=repo_root,
    )
    _run(
        [sys.executable, "labs/agent-ops/scripts/init_policy.py", "--generation", "policy-v1", "--allowed-target", "payments-api", "--max-approval-ttl-seconds", "900", "--max-tool-wait-seconds", "5", "--output", str(policy)],
        cwd=repo_root,
    )
    _run(
        [sys.executable, "labs/agent-ops/scripts/set_kill_switch.py", "--policy", str(policy), "--generation", "kill-v1", "--disengage", "--output", str(kill_switch)],
        cwd=repo_root,
    )
    state = _service_state(_read_json(tool_state), "payments-api")
    if state.get("status") != "degraded" or state.get("generation") != 1 or state.get("restart_count") != 0:
        raise IdentityRuntimeError("agent sandbox did not initialize exact degraded state")
    return {"tool_state": tool_state, "policy": policy, "kill_switch": kill_switch}


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
        env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
    )
    try:
        _wait_json(f"http://{host}:{port}/healthz", timeout_seconds)
    except Exception:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        handle.close()
        raise
    return process, handle


def _stop_process(process: subprocess.Popen[str] | None, handle: Any | None) -> bool:
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=15)
    if handle is not None:
        handle.close()
    return process is None or process.poll() is not None


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve(strict=True)
    subject_sha = _require_git_sha(args.subject_sha)
    output_path = args.output.resolve(strict=False)
    issuer = args.issuer.rstrip("/")
    if args.api_host not in {"127.0.0.1", "localhost"}:
        raise IdentityRuntimeError("secured API runtime is loopback-only")
    if not 1 <= args.api_port <= 65535:
        raise IdentityRuntimeError("API port must be between 1 and 65535")
    if not 10 <= args.startup_timeout_seconds <= 300:
        raise IdentityRuntimeError("startup timeout must be between 10 and 300 seconds")
    if output_path.exists() or output_path.is_symlink():
        raise IdentityRuntimeError("identity evidence output must be a fresh path")
    if _run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip() != subject_sha:
        raise IdentityRuntimeError("subject SHA does not match checked-out Git HEAD")
    if _run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=repo_root).stdout.strip():
        raise IdentityRuntimeError("tracked checkout must be clean before live identity runtime")

    compose_file = repo_root / "labs" / "keycloak-ai-api" / "compose.yaml"
    keycloak_root = repo_root / ".runtime" / "keycloak"
    agent_root = repo_root / ".runtime" / "agent-ops"
    for path in (keycloak_root, agent_root):
        if path.exists() or path.is_symlink():
            raise IdentityRuntimeError(f"runtime path must be absent before start: {path}")
    keycloak_root.mkdir(parents=True, exist_ok=False)
    agent_root.mkdir(parents=True, exist_ok=False)

    rag = _build_rag(repo_root, keycloak_root, subject_sha)
    agent = _build_agent(repo_root, agent_root)
    pkce_session = keycloak_root / "pkce-session.json"
    _run(
        [sys.executable, "labs/keycloak-ai-api/scripts/begin_pkce.py", "--session-output", str(pkce_session)],
        cwd=repo_root,
    )
    pkce_value = _read_json(pkce_session)
    for field in ("code_verifier", "state", "nonce"):
        if not isinstance(pkce_value.get(field), str) or not pkce_value[field]:
            raise IdentityRuntimeError(f"PKCE session is missing {field}")
    pkce_mode = stat.S_IMODE(pkce_session.stat().st_mode)
    if os.name != "nt" and pkce_mode != 0o600:
        raise IdentityRuntimeError(f"PKCE session mode must be 0600, got {oct(pkce_mode)}")

    admin_user = "kh-runtime-admin"
    admin_password = secrets.token_urlsafe(24)
    compose_env = {
        "KEYCLOAK_BOOTSTRAP_ADMIN_USERNAME": admin_user,
        "KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD": admin_password,
    }
    api_process: subprocess.Popen[str] | None = None
    api_handle: Any | None = None
    compose_started = False
    cleanup_verified = False
    evidence: dict[str, Any] | None = None
    secret: str | None = None
    issued_tokens: list[str] = []
    try:
        _run(
            ["docker", "compose", "-f", str(compose_file), "up", "-d"],
            cwd=repo_root,
            env_extra=compose_env,
        )
        compose_started = True
        discovery = _wait_json(issuer + "/.well-known/openid-configuration", args.startup_timeout_seconds)
        if discovery.get("issuer") != issuer:
            raise IdentityRuntimeError("OIDC discovery issuer mismatch")
        jwks_uri = discovery.get("jwks_uri")
        if not isinstance(jwks_uri, str) or not jwks_uri.startswith(issuer + "/"):
            raise IdentityRuntimeError("OIDC discovery JWKS URI is not bound to configured issuer")
        _, jwks = _json_request(jwks_uri, expected={200})
        keys = jwks.get("keys") if isinstance(jwks, dict) else None
        if not isinstance(keys, list) or not keys:
            raise IdentityRuntimeError("live realm JWKS contains no keys")

        container_id = _run(
            ["docker", "compose", "-f", str(compose_file), "ps", "-q"],
            cwd=repo_root,
            env_extra=compose_env,
        ).stdout.strip().splitlines()
        if len(container_id) != 1:
            raise IdentityRuntimeError("Keycloak compose did not expose exactly one container")
        keycloak_container_id = container_id[0]
        configured_image = _run(
            ["docker", "inspect", "--format", "{{.Config.Image}}", keycloak_container_id],
            cwd=repo_root,
        ).stdout.strip()
        local_image_id = _run(
            ["docker", "inspect", "--format", "{{.Image}}", keycloak_container_id],
            cwd=repo_root,
        ).stdout.strip()
        if configured_image != "quay.io/keycloak/keycloak:26.7.0":
            raise IdentityRuntimeError("running Keycloak container image tag does not match pinned compose contract")
        if not local_image_id.startswith("sha256:"):
            raise IdentityRuntimeError("running Keycloak container does not expose content-addressed local image ID")

        admin_token = _form_request(
            "http://127.0.0.1:8080/realms/master/protocol/openid-connect/token",
            values={
                "grant_type": "password",
                "client_id": "admin-cli",
                "username": admin_user,
                "password": admin_password,
            },
        ).get("access_token")
        if not isinstance(admin_token, str) or not admin_token:
            raise IdentityRuntimeError("bootstrap admin token response is missing access_token")
        admin_base = "http://127.0.0.1:8080/admin/realms/knowledge-hub"

        web_client = _admin_get_client(admin_base, admin_token, "knowledge-hub-web")
        automation_client = _admin_get_client(admin_base, admin_token, "knowledge-hub-automation")
        api_client = _admin_get_client(admin_base, admin_token, "knowledge-hub-api")
        if web_client.get("publicClient") is not True:
            raise IdentityRuntimeError("web client is not public in imported realm")
        if web_client.get("standardFlowEnabled") is not True:
            raise IdentityRuntimeError("web client standard flow is not enabled")
        if web_client.get("implicitFlowEnabled") is not False or web_client.get("directAccessGrantsEnabled") is not False:
            raise IdentityRuntimeError("web client exposes forbidden implicit/password flow")
        if web_client.get("serviceAccountsEnabled") is not False:
            raise IdentityRuntimeError("web client unexpectedly enables service account")
        web_attributes = web_client.get("attributes") or {}
        if web_attributes.get("pkce.code.challenge.method") != "S256":
            raise IdentityRuntimeError("imported web client does not require PKCE S256")
        if automation_client.get("serviceAccountsEnabled") is not True:
            raise IdentityRuntimeError("automation client service account is not enabled")
        if automation_client.get("publicClient") is not False:
            raise IdentityRuntimeError("automation client must be confidential")
        if automation_client.get("standardFlowEnabled") is not False or automation_client.get("directAccessGrantsEnabled") is not False:
            raise IdentityRuntimeError("automation client exposes forbidden browser/password flow")

        scope = _admin_get_scope(admin_base, admin_token, "knowledge-hub-api-access")
        if (scope.get("attributes") or {}).get("include.in.token.scope") != "true":
            raise IdentityRuntimeError("API client scope is not included in token scope")
        scope_id = scope.get("id")
        if not isinstance(scope_id, str) or not scope_id:
            raise IdentityRuntimeError("API client scope has no ID")
        _, mappers = _json_request(
            f"{admin_base}/client-scopes/{scope_id}/protocol-mappers/models",
            bearer=admin_token,
            expected={200},
        )
        if not isinstance(mappers, list):
            raise IdentityRuntimeError("client scope protocol mapper read-back is invalid")
        audience_mappers = [
            item for item in mappers
            if isinstance(item, dict) and item.get("protocolMapper") == "oidc-audience-mapper"
        ]
        if len(audience_mappers) != 1:
            raise IdentityRuntimeError("API client scope must expose exactly one audience mapper")
        audience_mapper = audience_mappers[0]
        if (audience_mapper.get("config") or {}).get("included.client.audience") != "knowledge-hub-api":
            raise IdentityRuntimeError("live audience mapper does not target knowledge-hub-api")

        automation_id = automation_client.get("id")
        api_id = api_client.get("id")
        if not isinstance(automation_id, str) or not isinstance(api_id, str):
            raise IdentityRuntimeError("Keycloak clients are missing internal IDs")
        _, secret_rep = _json_request(
            f"{admin_base}/clients/{automation_id}/client-secret",
            bearer=admin_token,
            expected={200},
        )
        secret = secret_rep.get("value") if isinstance(secret_rep, dict) else None
        if not isinstance(secret, str) or not secret:
            raise IdentityRuntimeError("automation client secret was not generated by imported realm")

        positive_token, positive_claims = _issue_service_token(
            repo_root=repo_root,
            runtime_root=keycloak_root,
            secret=secret,
            label="positive",
            issuer=issuer,
        )
        issued_tokens.append(positive_token)
        if positive_claims.get("iss") != issuer:
            raise IdentityRuntimeError("positive token issuer mismatch")
        if _audiences(positive_claims) != {"knowledge-hub-api"}:
            raise IdentityRuntimeError("positive token audience is not exact knowledge-hub-api")
        if positive_claims.get("azp") != "knowledge-hub-automation":
            raise IdentityRuntimeError("positive token azp mismatch")
        if positive_claims.get("token_use") != "access":
            raise IdentityRuntimeError("positive token is not marked as access token")
        if "knowledge-hub-api-access" not in _scopes(positive_claims):
            raise IdentityRuntimeError("positive token is missing API scope")
        required_roles = {"rag.read", "agent.run", "agent.remediate"}
        if not required_roles.issubset(_client_roles(positive_claims, "knowledge-hub-api")):
            raise IdentityRuntimeError("positive token is missing required API roles")

        audience_mapper_id = audience_mapper.get("id")
        if not isinstance(audience_mapper_id, str):
            raise IdentityRuntimeError("audience mapper is missing ID")
        wrong_audience_mapper = json.loads(json.dumps(audience_mapper))
        wrong_audience_mapper.setdefault("config", {})["included.client.audience"] = "knowledge-hub-wrong-audience"
        _json_request(
            f"{admin_base}/client-scopes/{scope_id}/protocol-mappers/models/{audience_mapper_id}",
            method="PUT",
            bearer=admin_token,
            payload=wrong_audience_mapper,
            expected={204},
        )
        try:
            wrong_audience_token, wrong_audience_claims = _issue_service_token(
                repo_root=repo_root,
                runtime_root=keycloak_root,
                secret=secret,
                label="wrong-audience",
                issuer=issuer,
            )
            issued_tokens.append(wrong_audience_token)
        finally:
            _json_request(
                f"{admin_base}/client-scopes/{scope_id}/protocol-mappers/models/{audience_mapper_id}",
                method="PUT",
                bearer=admin_token,
                payload=audience_mapper,
                expected={204},
            )
        if "knowledge-hub-api" in _audiences(wrong_audience_claims):
            raise IdentityRuntimeError("wrong-audience token still contains accepted audience")

        scope_without_name = json.loads(json.dumps(scope))
        scope_without_name.setdefault("attributes", {})["include.in.token.scope"] = "false"
        _json_request(
            f"{admin_base}/client-scopes/{scope_id}",
            method="PUT",
            bearer=admin_token,
            payload=scope_without_name,
            expected={204},
        )
        try:
            missing_scope_token, missing_scope_claims = _issue_service_token(
                repo_root=repo_root,
                runtime_root=keycloak_root,
                secret=secret,
                label="missing-scope",
                issuer=issuer,
            )
            issued_tokens.append(missing_scope_token)
        finally:
            _json_request(
                f"{admin_base}/client-scopes/{scope_id}",
                method="PUT",
                bearer=admin_token,
                payload=scope,
                expected={204},
            )
        if "knowledge-hub-api-access" in _scopes(missing_scope_claims):
            raise IdentityRuntimeError("missing-scope token still contains API scope")
        if _audiences(missing_scope_claims) != {"knowledge-hub-api"}:
            raise IdentityRuntimeError("missing-scope token unexpectedly lost exact audience")

        _, service_user = _json_request(
            f"{admin_base}/clients/{automation_id}/service-account-user",
            bearer=admin_token,
            expected={200},
        )
        service_user_id = service_user.get("id") if isinstance(service_user, dict) else None
        if not isinstance(service_user_id, str):
            raise IdentityRuntimeError("automation service-account user is missing ID")
        _, remediate_role = _json_request(
            f"{admin_base}/clients/{api_id}/roles/agent.remediate",
            bearer=admin_token,
            expected={200},
        )
        if not isinstance(remediate_role, dict):
            raise IdentityRuntimeError("agent.remediate role read-back is invalid")
        role_mapping_url = f"{admin_base}/users/{service_user_id}/role-mappings/clients/{api_id}"
        _json_request(
            role_mapping_url,
            method="DELETE",
            bearer=admin_token,
            payload=[remediate_role],
            expected={204},
        )
        try:
            missing_role_token, missing_role_claims = _issue_service_token(
                repo_root=repo_root,
                runtime_root=keycloak_root,
                secret=secret,
                label="missing-remediate-role",
                issuer=issuer,
            )
            issued_tokens.append(missing_role_token)
        finally:
            _json_request(
                role_mapping_url,
                method="POST",
                bearer=admin_token,
                payload=[remediate_role],
                expected={204},
            )
        if "agent.remediate" in _client_roles(missing_role_claims, "knowledge-hub-api"):
            raise IdentityRuntimeError("missing-role token still contains agent.remediate")
        if not {"rag.read", "agent.run"}.issubset(_client_roles(missing_role_claims, "knowledge-hub-api")):
            raise IdentityRuntimeError("missing-role token unexpectedly lost unrelated roles")

        _, realm_rep = _json_request(admin_base, bearer=admin_token, expected={200})
        if not isinstance(realm_rep, dict):
            raise IdentityRuntimeError("realm read-back is invalid")
        original_lifespan = realm_rep.get("accessTokenLifespan")
        if isinstance(original_lifespan, bool) or not isinstance(original_lifespan, int) or original_lifespan < 1:
            raise IdentityRuntimeError("realm accessTokenLifespan is invalid")
        _json_request(
            admin_base,
            method="PUT",
            bearer=admin_token,
            payload={"accessTokenLifespan": 1},
            expected={204},
        )
        try:
            expired_token, expired_claims = _issue_service_token(
                repo_root=repo_root,
                runtime_root=keycloak_root,
                secret=secret,
                label="expired",
                issuer=issuer,
            )
            issued_tokens.append(expired_token)
        finally:
            _json_request(
                admin_base,
                method="PUT",
                bearer=admin_token,
                payload={"accessTokenLifespan": original_lifespan},
                expected={204},
            )
        exp = expired_claims.get("exp")
        if isinstance(exp, bool) or not isinstance(exp, int):
            raise IdentityRuntimeError("short-lived token is missing numeric exp")
        while time.time() <= exp + 1:
            time.sleep(0.25)

        api_log = keycloak_root / "secured-api.log"
        api_process, api_handle = _start_api(
            repo_root=repo_root,
            issuer=issuer,
            rag=rag,
            agent=agent,
            agent_root=agent_root,
            host=args.api_host,
            port=args.api_port,
            log_path=api_log,
            timeout_seconds=args.startup_timeout_seconds,
        )
        api_base = f"http://{args.api_host}:{args.api_port}"
        _wait_json(api_base + "/readyz", args.startup_timeout_seconds)
        _wait_json(api_base + "/readyz/agent", args.startup_timeout_seconds)

        rag_status, rag_response = _api_json(
            api_base,
            "/v1/rag/query",
            token=positive_token,
            payload={"query": rag["query"]},
        )
        if rag_status != 200 or rag_response.get("status") != "answered":
            raise IdentityRuntimeError("authorized promoted RAG request did not return answered 200")

        run_status, run_response = _api_json(
            api_base,
            "/v1/agent/run",
            token=positive_token,
            payload={
                "target": "payments-api",
                "signal": "service_degraded",
                "operator_note": "Use typed evidence and promoted Knowledge Hub context.",
                "incident_generation": "live-keycloak-incident-v1",
                "knowledge_query": rag["query"],
            },
        )
        if run_status != 200:
            raise IdentityRuntimeError(f"authorized agent.run returned HTTP {run_status}")
        plan_id = _find_key(run_response, "plan_id")
        action_digest = _find_key(run_response, "action_digest")
        disposition = _find_key(run_response, "disposition")
        _require_sha256(plan_id, "agent plan_id")
        _require_sha256(action_digest, "agent action_digest")
        if disposition != "approval_required":
            raise IdentityRuntimeError("authorized degraded agent plan is not approval_required")

        plan_dir = agent_root / "plans" / plan_id
        approval_path = plan_dir / "approval.json"
        _run(
            [
                sys.executable,
                "labs/agent-ops/scripts/approve_action.py",
                "--plan",
                str(plan_dir / "plan.json"),
                "--policy",
                str(plan_dir / "policy.json"),
                "--expected-plan-id",
                plan_id,
                "--approver",
                "live-keycloak-operator",
                "--approval-generation",
                "live-keycloak-approval-v1",
                "--ttl-seconds",
                "300",
                "--output",
                str(approval_path),
            ],
            cwd=repo_root,
        )
        approval = _read_json(approval_path)
        approval_id = _require_sha256(approval.get("approval_id"), "agent approval_id")

        remediate_payload = {
            "plan_id": plan_id,
            "approval_id": approval_id,
            "recover_expected_state_id": None,
        }
        remediate_status, remediate_response = _api_json(
            api_base,
            "/v1/agent/remediate",
            token=positive_token,
            payload=remediate_payload,
        )
        if remediate_status != 200:
            raise IdentityRuntimeError(f"authorized agent.remediate returned HTTP {remediate_status}")
        after_first = _service_state(_read_json(agent["tool_state"]), "payments-api")
        if after_first.get("status") != "healthy" or after_first.get("generation") != 2 or after_first.get("restart_count") != 1:
            raise IdentityRuntimeError("authorized remediation did not produce exact healthy generation-2 state")

        replay_status, replay_response = _api_json(
            api_base,
            "/v1/agent/remediate",
            token=positive_token,
            payload=remediate_payload,
        )
        if replay_status != 200:
            raise IdentityRuntimeError(f"completed remediation replay returned HTTP {replay_status}")
        after_replay = _service_state(_read_json(agent["tool_state"]), "payments-api")
        if dict(after_replay) != dict(after_first):
            raise IdentityRuntimeError("completed remediation replay changed service state")

        no_token_status, _ = _api_json(api_base, "/v1/rag/query", token=None, payload={"query": rag["query"]})
        tampered_token = positive_token[:-1] + ("A" if positive_token[-1] != "A" else "B")
        tampered_status, _ = _api_json(api_base, "/v1/rag/query", token=tampered_token, payload={"query": rag["query"]})
        wrong_audience_status, _ = _api_json(api_base, "/v1/rag/query", token=wrong_audience_token, payload={"query": rag["query"]})
        missing_scope_status, _ = _api_json(api_base, "/v1/rag/query", token=missing_scope_token, payload={"query": rag["query"]})
        missing_role_status, _ = _api_json(api_base, "/v1/agent/remediate", token=missing_role_token, payload=remediate_payload)
        expired_status, _ = _api_json(api_base, "/v1/rag/query", token=expired_token, payload={"query": rag["query"]})
        expected_statuses = {
            "missing_bearer": (no_token_status, 401),
            "tampered_signature": (tampered_status, 401),
            "wrong_audience": (wrong_audience_status, 401),
            "missing_scope": (missing_scope_status, 403),
            "missing_agent_remediate_role": (missing_role_status, 403),
            "expired_token": (expired_status, 401),
        }
        for label, (observed, expected) in expected_statuses.items():
            if observed != expected:
                raise IdentityRuntimeError(
                    f"negative authorization variant {label} returned HTTP {observed}, expected {expected}"
                )

        api_stopped = _stop_process(api_process, api_handle)
        api_process = None
        api_handle = None
        if not api_stopped:
            raise IdentityRuntimeError("secured API did not stop cleanly")
        log_text = api_log.read_text(encoding="utf-8", errors="replace")
        if secret in log_text:
            raise IdentityRuntimeError("automation client secret appeared in secured API log")
        if any(token in log_text for token in issued_tokens):
            raise IdentityRuntimeError("bearer token appeared in secured API log")

        payload: dict[str, Any] = {
            "schema_version": 1,
            "evidence_generation": "keycloak-live-identity-runtime-v1",
            "subject_sha": subject_sha,
            "keycloak": {
                "configured_image": configured_image,
                "local_image_id": local_image_id,
                "issuer": issuer,
                "discovery_issuer": discovery["issuer"],
                "jwks_uri": jwks_uri,
                "jwks_key_count": len(keys),
                "realm_import_live": True,
            },
            "pkce": {
                "public_client": "knowledge-hub-web",
                "standard_flow_enabled": True,
                "pkce_method": "S256",
                "implicit_flow_enabled": False,
                "direct_access_grants_enabled": False,
                "service_account_enabled": False,
                "session_created": True,
                "session_mode": oct(pkce_mode),
                "authorization_code_exchange_executed": False,
            },
            "service_account": {
                "client_id": "knowledge-hub-automation",
                "secret_obtained_from_live_realm": True,
                "secret_persisted_in_evidence": False,
                "token_value_persisted_in_evidence": False,
                "issuer": positive_claims["iss"],
                "audience": sorted(_audiences(positive_claims)),
                "azp": positive_claims["azp"],
                "token_use": positive_claims["token_use"],
                "scope_present": "knowledge-hub-api-access" in _scopes(positive_claims),
                "roles": sorted(_client_roles(positive_claims, "knowledge-hub-api")),
            },
            "rag": {
                "snapshot_id": rag["snapshot_id"],
                "index_id": rag["index_id"],
                "report_id": rag["report_id"],
                "prompt_release_id": rag["prompt_release_id"],
                "protected_status": rag_status,
                "answer_status": rag_response["status"],
                "answer_id": _find_key(rag_response, "answer_id"),
                "trace_id": _find_key(rag_response, "trace_id"),
            },
            "agent": {
                "plan_id": plan_id,
                "action_digest": action_digest,
                "disposition": disposition,
                "approval_id": approval_id,
                "remediation_http_status": remediate_status,
                "replay_http_status": replay_status,
                "service_after_remediation": after_first,
                "service_after_replay": after_replay,
                "remediation_status": _find_key(remediate_response, "status"),
                "replay_status": _find_key(replay_response, "status"),
            },
            "negative_authorization": {
                label: {"observed_http_status": observed, "expected_http_status": expected}
                for label, (observed, expected) in expected_statuses.items()
            },
            "negative_token_claims": {
                "wrong_audience": sorted(_audiences(wrong_audience_claims)),
                "missing_scope_confirmed": "knowledge-hub-api-access" not in _scopes(missing_scope_claims),
                "missing_remediate_role_confirmed": "agent.remediate" not in _client_roles(missing_role_claims, "knowledge-hub-api"),
                "expired_token_exp": exp,
            },
            "redaction": {
                "api_log_sha256": _sha256_bytes(log_text.encode("utf-8", errors="replace")),
                "client_secret_found_in_api_log": False,
                "bearer_token_found_in_api_log": False,
            },
            "proof_boundary": {
                "realm_import": "live-local-keycloak",
                "jwks_signature_path": "live-resource-server",
                "service_account_client_credentials": "live",
                "protected_rag": "live-loopback-http",
                "protected_agent_plan_and_remediation": "live-loopback-http-local-sandbox",
                "browser_pkce_config": "live-import-readback-plus-session-helper",
                "browser_authorization_code_exchange": "not-executed",
                "production_tls_claimed": False,
                "production_identity_platform_claimed": False,
            },
        }
        evidence = {**payload, "evidence_id": _sha256_bytes(_canonical_bytes(payload))}
    finally:
        _stop_process(api_process, api_handle)
        if compose_started:
            _run(
                ["docker", "compose", "-f", str(compose_file), "down", "-v", "--remove-orphans"],
                cwd=repo_root,
                env_extra=compose_env,
                expected_codes={0},
            )
        shutil.rmtree(keycloak_root, ignore_errors=True)
        shutil.rmtree(agent_root, ignore_errors=True)
        try:
            (repo_root / ".runtime").rmdir()
        except OSError:
            pass
        compose_ps = _run(
            ["docker", "compose", "-f", str(compose_file), "ps", "-q"],
            cwd=repo_root,
            env_extra=compose_env,
            expected_codes={0},
        ).stdout.strip()
        cleanup_verified = (
            not keycloak_root.exists()
            and not keycloak_root.is_symlink()
            and not agent_root.exists()
            and not agent_root.is_symlink()
            and not compose_ps
        )

    if evidence is None:
        raise IdentityRuntimeError("live identity runtime ended without evidence")
    if not cleanup_verified:
        raise IdentityRuntimeError("live identity cleanup read-back failed")
    evidence["cleanup_verified"] = True
    final_payload = {key: value for key, value in evidence.items() if key != "evidence_id"}
    evidence["evidence_id"] = _sha256_bytes(_canonical_bytes(final_payload))
    _atomic_write_json(output_path, evidence)
    return evidence


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        evidence = run(args)
    except (IdentityRuntimeError, OSError, RuntimeError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "refused", "error": f"{type(exc).__name__}: {exc}"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(
        json.dumps(
            {
                "status": "passed",
                "subject_sha": evidence["subject_sha"],
                "issuer": evidence["keycloak"]["issuer"],
                "jwks_key_count": evidence["keycloak"]["jwks_key_count"],
                "rag_status": evidence["rag"]["protected_status"],
                "plan_id": evidence["agent"]["plan_id"],
                "approval_id": evidence["agent"]["approval_id"],
                "cleanup_verified": evidence["cleanup_verified"],
                "evidence_id": evidence["evidence_id"],
                "output": args.output.as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
