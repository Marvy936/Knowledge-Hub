from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Request a Keycloak client-credentials access token without logging the token value."
    )
    parser.add_argument(
        "--token-endpoint",
        default="http://127.0.0.1:8080/realms/knowledge-hub/protocol/openid-connect/token",
    )
    parser.add_argument("--client-id", default="knowledge-hub-automation")
    parser.add_argument("--client-secret-env", default="KEYCLOAK_AUTOMATION_CLIENT_SECRET")
    parser.add_argument("--token-output", type=Path, required=True)
    return parser


def _allowed_endpoint(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme == "https":
        return bool(parsed.hostname)
    return parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost"}


def main() -> int:
    args = _parser().parse_args()
    if not _allowed_endpoint(args.token_endpoint):
        print(json.dumps({"status": "refused", "error": "token endpoint must use HTTPS or loopback HTTP"}), file=sys.stderr)
        return 2
    secret = os.environ.get(args.client_secret_env)
    if not secret:
        print(json.dumps({"status": "refused", "error": f"missing environment secret {args.client_secret_env}"}), file=sys.stderr)
        return 2
    if args.token_output.exists():
        print(json.dumps({"status": "refused", "error": "token output already exists; use a fresh disposable path"}), file=sys.stderr)
        return 2

    body = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": args.client_id,
            "client_secret": secret,
        }
    ).encode("ascii")
    request = urllib.request.Request(
        args.token_endpoint,
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "request_failed", "error": type(exc).__name__}), file=sys.stderr)
        return 3

    token = payload.get("access_token")
    if not isinstance(token, str) or token.count(".") != 2:
        print(json.dumps({"status": "request_failed", "error": "response did not contain a compact access token"}), file=sys.stderr)
        return 3
    args.token_output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(args.token_output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(token)
            stream.write("\n")
    except Exception:
        args.token_output.unlink(missing_ok=True)
        raise
    if stat.S_IMODE(args.token_output.stat().st_mode) & 0o077:
        args.token_output.unlink(missing_ok=True)
        print(json.dumps({"status": "refused", "error": "token output permissions are too broad"}), file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "status": "token_recorded",
                "token_type": payload.get("token_type"),
                "expires_in": payload.get("expires_in"),
                "scope": payload.get("scope"),
                "token_output": args.token_output.as_posix(),
                "access_token_logged": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
