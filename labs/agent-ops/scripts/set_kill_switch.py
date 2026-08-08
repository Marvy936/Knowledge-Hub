from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_ops.contracts import AgentContractError, atomic_write_json
from agent_ops.safety import build_kill_switch


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write one explicit bounded-agent kill-switch generation."
    )
    parser.add_argument("--generation", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--engage", action="store_true")
    group.add_argument("--disengage", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.output.exists():
        print(json.dumps({"status": "refused", "error": "kill-switch output already exists"}), file=sys.stderr)
        return 2
    try:
        value = build_kill_switch(
            generation=args.generation,
            engaged=args.engage,
        )
        atomic_write_json(args.output, value)
    except AgentContractError as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": "kill_switch_recorded",
                "engaged": value["engaged"],
                "kill_switch_id": value["kill_switch_id"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
