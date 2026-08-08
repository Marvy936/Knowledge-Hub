from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_ops.contracts import AgentContractError, atomic_write_json


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a fresh local-only service sandbox with no external credentials."
    )
    parser.add_argument("--target", required=True)
    parser.add_argument("--status", choices=["healthy", "degraded", "unknown"], required=True)
    parser.add_argument("--generation", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.output.exists():
        print(json.dumps({"status": "refused", "error": "sandbox output already exists"}), file=sys.stderr)
        return 2
    if args.generation < 1:
        print(json.dumps({"status": "refused", "error": "generation must be positive"}), file=sys.stderr)
        return 2
    try:
        atomic_write_json(
            args.output,
            {
                "schema_version": 1,
                "services": {
                    args.target: {
                        "generation": args.generation,
                        "status": args.status,
                        "restart_count": 0,
                    }
                },
                "operations": {},
            },
        )
    except AgentContractError as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps({"status": "sandbox_initialized", "target": args.target}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
