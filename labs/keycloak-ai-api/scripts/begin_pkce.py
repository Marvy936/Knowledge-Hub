from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from keycloak_ai_api.pkce import build_authorization_request


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create one disposable Authorization Code + PKCE S256 browser session."
    )
    parser.add_argument(
        "--issuer", default="http://127.0.0.1:8080/realms/knowledge-hub"
    )
    parser.add_argument("--client-id", default="knowledge-hub-web")
    parser.add_argument("--redirect-uri", default="http://127.0.0.1:8765/callback")
    parser.add_argument("--session-output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.session_output.exists():
        print(
            json.dumps(
                {"status": "refused", "error": "PKCE session output already exists"}
            ),
            file=sys.stderr,
        )
        return 2
    try:
        request = build_authorization_request(
            issuer=args.issuer,
            client_id=args.client_id,
            redirect_uri=args.redirect_uri,
        )
    except ValueError as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}), file=sys.stderr)
        return 2

    session = {
        "issuer": args.issuer.rstrip("/"),
        "client_id": args.client_id,
        "redirect_uri": args.redirect_uri,
        "code_verifier": request.code_verifier,
        "state": request.state,
        "nonce": request.nonce,
    }
    args.session_output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(args.session_output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(session, stream, sort_keys=True, indent=2)
        stream.write("\n")

    print(
        json.dumps(
            {
                "status": "pkce_session_recorded",
                "authorization_url": request.authorization_url,
                "session_output": args.session_output.as_posix(),
                "verifier_logged": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
