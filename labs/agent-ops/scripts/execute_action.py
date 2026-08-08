from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_ops.contracts import AgentContractError, atomic_write_json, read_json
from agent_ops.execution import build_operation, execute_operation
from agent_ops.tools import LocalServiceStateAdapter, UnknownToolOutcome


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Execute one approval-bound typed tool operation in the local sandbox."
    )
    parser.add_argument("--incident", type=Path, required=True)
    parser.add_argument("--diagnostic", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--kill-switch", type=Path, required=True)
    parser.add_argument("--tool-state", type=Path, required=True)
    parser.add_argument("--operation-output", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--recover-expected-state-id")
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        incident = read_json(args.incident)
        diagnostic = read_json(args.diagnostic)
        plan = read_json(args.plan)
        approval = read_json(args.approval)
        policy = read_json(args.policy)
        kill_switch = read_json(args.kill_switch)
        operation = build_operation(
            incident=incident,
            diagnostic=diagnostic,
            plan=plan,
            approval=approval,
            policy=policy,
        )
        if args.operation_output.exists():
            if read_json(args.operation_output) != operation:
                raise AgentContractError("operation output already contains another subject")
        else:
            atomic_write_json(args.operation_output, operation)
        outcome = execute_operation(
            operation=operation,
            incident=incident,
            diagnostic=diagnostic,
            plan=plan,
            approval=approval,
            policy=policy,
            kill_switch=kill_switch,
            adapter=LocalServiceStateAdapter(args.tool_state),
            state_path=args.state,
            result_path=args.result,
            recover_expected_state_id=args.recover_expected_state_id,
        )
    except UnknownToolOutcome as exc:
        print(json.dumps({"status": "unknown_outcome", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 4
    except AgentContractError as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "status": outcome["status"],
                "operation_id": operation["operation_id"],
                "state_id": outcome["state"]["state_id"],
                "result_id": outcome["result"]["result_id"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
