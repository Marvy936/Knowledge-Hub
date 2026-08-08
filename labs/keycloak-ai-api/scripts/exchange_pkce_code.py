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

from keycloak_ai_api.pkce import build_token_exchange_form, endpoint_is_allowed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Exchange one Authorization Code with the exact disposable PKCE verifier."
    )
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--code", required=True)
    parser.add_argument("--returned-state", required=True)
    parser.add_argument("--token-output", type=Path, required=True)
    return parser


def _read_session(path: Path) -> dict[str, str]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise ValueError("PKCE session is missing or invalid") from exc
    required = {"issuer", "client_id", "redirect_uri", "code_verifier", "state", "nonce"}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("PKCE session fields are invalid")
    if any(not isinstance(value[key], str) or not value[key] for key in required):
        raise ValueError("PKCE session fields must be non-empty strings")
    return value


def main() -> int:
    args = _parser().parse_args()
    try:
        session = _read_session(args.session)
        if args.returned_state != session["state"]:
            raise ValueError("OAuth callback state does not match the PKCE session")
        token_endpoint = session["issuer"].rstrip("/") + "/protocol/openid-connect/token"
        if not endpoint_is_allowed(token_endpoint):
            raise ValueError("token endpoint must use HTTPS or loopback HTTP")
        if args.token_output.exists():
            raise ValueError("token output already exists; use a fresh disposable path")
        form = build_token_exchange_form(
            code=args.code,
            code_verifier=session["code_verifier"],
            client_id=session["client_id"],
            redirect_uri=session["redirect_uri"],
        )
        request = urllib.request.Request(
            token_endpoint,
            data=urllib.parse.urlencode(form).encode("ascii"),
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
        token = payload.get("access_token")
        if not isinstance(token, str) or token.count(".") != 2:
            raise ValueError("token response did not contain a compact access token")
        args.token_output.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(
            args.token_output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
        )
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(token)
            stream.write("\n")
        if stat.S_IMODE(args.token_output.stat().st_mode) & 0o077:
            args.token_output.unlink(missing_ok=True)
            raise ValueError("token output permissions are too broad")
        args.session.unlink()
        if args.session.exists():
            args.token_output.unlink(missing_ok=True)
            raise ValueError("single-use PKCE session cleanup failed")
    except (ValueError, urllib.error.URLError, json.JSONDecodeError) as exc:
        print(
            json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True),
            file=sys.stderr,
        )
        return 2

    print(
        json.dumps(
            {
                "status": "access_token_recorded",
                "token_type": payload.get("token_type"),
                "expires_in": payload.get("expires_in"),
                "scope": payload.get("scope"),
                "token_output": args.token_output.as_posix(),
                "pkce_session_deleted": True,
                "access_token_logged": False,
                "id_token_used_as_api_bearer": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
