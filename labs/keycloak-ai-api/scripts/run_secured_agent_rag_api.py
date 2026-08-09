from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn

from keycloak_ai_api.agent_bridge import LocalBoundedAgentExecutor
from keycloak_ai_api.app import create_app
from keycloak_ai_api.rag_bridge import (
    OfflinePromotedRagExecutor,
    RagBundlePaths,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the loopback-only Keycloak-secured API with both the exact promoted RAG "
            "bundle and the bounded local operations agent configured."
        )
    )
    parser.add_argument(
        "--issuer",
        default="http://127.0.0.1:8080/realms/knowledge-hub",
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--runtime-config", type=Path, required=True)
    parser.add_argument("--eval-cases", type=Path, required=True)
    parser.add_argument("--eval-report", type=Path, required=True)
    parser.add_argument("--prompt-release", type=Path, required=True)
    parser.add_argument("--tool-state", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--kill-switch", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8091)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("combined secured AI API runner is loopback-only")

    rag_executor = OfflinePromotedRagExecutor(
        RagBundlePaths(
            manifest=args.manifest,
            index=args.index,
            runtime_config=args.runtime_config,
            eval_cases=args.eval_cases,
            eval_report=args.eval_report,
            prompt_release=args.prompt_release,
        )
    )
    agent_executor = LocalBoundedAgentExecutor(
        tool_state=args.tool_state,
        policy_path=args.policy,
        kill_switch_path=args.kill_switch,
        runtime_root=args.runtime_root,
    )
    uvicorn.run(
        create_app(
            issuer=args.issuer,
            rag_executor=rag_executor,
            agent_executor=agent_executor,
        ),
        host=args.host,
        port=args.port,
        workers=1,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
