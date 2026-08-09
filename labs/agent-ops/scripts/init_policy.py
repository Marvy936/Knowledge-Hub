from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_ops.contracts import AgentContractError, atomic_write_json
from agent_ops.planning import build_agent_policy


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create one fresh immutable bounded-agent policy artifact."
    )
    parser.add_argument("--generation", required=True)
    parser.add_argument("--allowed-target", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.output.exists():
        print(
            json.dumps({"status": "refused", "error": "policy output already exists"}),
            file=sys.stderr,
        )
        return 2
    try:
        value = build_agent_policy(
            generation=args.generation,
            allowed_targets=args.allowed_target,
        )
        atomic_write_json(args.output, value)
    except AgentContractError as exc:
        print(
            json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True),
            file=sys.stderr,
        )
        return 2
    print(
        json.dumps(
            {
                "status": "policy_initialized",
                "policy_id": value["policy_id"],
                "policy_generation": value["generation"],
                "allowed_targets": value["allowed_targets"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
