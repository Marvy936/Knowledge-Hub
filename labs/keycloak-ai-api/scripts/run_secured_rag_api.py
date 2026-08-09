from __future__ import annotations

import argparse
import sys
from pathlib import Path

import uvicorn

from keycloak_ai_api.app import create_app
from keycloak_ai_api.rag_bridge import OfflinePromotedRagExecutor, RagBridgeError, RagBundlePaths


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Start the Keycloak-secured API with one exact promoted offline RAG bundle."
    )
    parser.add_argument(
        "--issuer", default="http://127.0.0.1:8080/realms/knowledge-hub"
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--runtime-config", type=Path, required=True)
    parser.add_argument("--eval-cases", type=Path, required=True)
    parser.add_argument("--eval-report", type=Path, required=True)
    parser.add_argument("--prompt-release", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8090)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.host not in {"127.0.0.1", "localhost"}:
        print(
            "refused: Practical v1 secured API source runner is loopback-only",
            file=sys.stderr,
        )
        return 2
    try:
        executor = OfflinePromotedRagExecutor(
            RagBundlePaths(
                manifest=args.manifest,
                index=args.index,
                runtime_config=args.runtime_config,
                eval_cases=args.eval_cases,
                eval_report=args.eval_report,
                prompt_release=args.prompt_release,
            )
        )
        app = create_app(issuer=args.issuer, rag_executor=executor)
    except (RagBridgeError, ValueError) as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2

    uvicorn.run(app, host=args.host, port=args.port, workers=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
