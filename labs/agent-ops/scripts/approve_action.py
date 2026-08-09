from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from agent_ops.contracts import AgentContractError, atomic_write_json, read_json
from agent_ops.safety import approve_action_plan


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Approve exactly one bounded action plan and action digest for a finite validity window."
    )
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--expected-plan-id", required=True)
    parser.add_argument("--approver", required=True)
    parser.add_argument("--approval-generation", required=True)
    parser.add_argument(
        "--ttl-seconds",
        type=int,
        default=300,
        help="Requested approval lifetime; the policy maximum is authoritative.",
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.output.exists():
        print(
            json.dumps({"status": "refused", "error": "approval output already exists"}),
            file=sys.stderr,
        )
        return 2
    issued_at_unix = int(time.time())
    try:
        approval = approve_action_plan(
            plan=read_json(args.plan),
            policy=read_json(args.policy),
            expected_plan_id=args.expected_plan_id,
            approver=args.approver,
            approval_generation=args.approval_generation,
            issued_at_unix=issued_at_unix,
            ttl_seconds=args.ttl_seconds,
        )
        atomic_write_json(args.output, approval)
    except AgentContractError as exc:
        print(
            json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True),
            file=sys.stderr,
        )
        return 2
    print(
        json.dumps(
            {
                "status": "approved",
                "approval_id": approval["approval_id"],
                "plan_id": approval["plan_id"],
                "action_digest": approval["action_digest"],
                "issued_at_unix": approval["issued_at_unix"],
                "expires_at_unix": approval["expires_at_unix"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
