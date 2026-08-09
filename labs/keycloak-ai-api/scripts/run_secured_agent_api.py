from __future__ import annotations

import argparse
import sys
from pathlib import Path

import uvicorn

from keycloak_ai_api.agent_bridge import AgentBridgeError, LocalBoundedAgentExecutor
from keycloak_ai_api.app import create_app


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Start the Keycloak-secured API with the local bounded incident agent backend."
    )
    parser.add_argument(
        "--issuer", default="http://127.0.0.1:8080/realms/knowledge-hub"
    )
    parser.add_argument("--tool-state", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--kill-switch", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8091)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.host not in {"127.0.0.1", "localhost"}:
        print(
            "refused: Practical v1 bounded agent API runner is loopback-only",
            file=sys.stderr,
        )
        return 2
    try:
        executor = LocalBoundedAgentExecutor(
            tool_state=args.tool_state,
            policy_path=args.policy,
            kill_switch_path=args.kill_switch,
            runtime_root=args.runtime_root,
        )
        app = create_app(issuer=args.issuer, agent_executor=executor)
    except (AgentBridgeError, ValueError) as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2

    uvicorn.run(app, host=args.host, port=args.port, workers=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
