from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_ops.contracts import AgentContractError, atomic_write_json
from agent_ops.planning import (
    build_agent_policy,
    build_diagnostic_snapshot,
    build_incident,
    plan_incident_action,
)
from agent_ops.tools import LocalServiceStateAdapter


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build deterministic incident, inspection, diagnostic, policy and bounded action-plan artifacts."
    )
    parser.add_argument("--target", required=True)
    parser.add_argument("--signal", required=True)
    parser.add_argument("--operator-note", required=True)
    parser.add_argument("--incident-generation", required=True)
    parser.add_argument("--policy-generation", required=True)
    parser.add_argument("--allowed-target", action="append", required=True)
    parser.add_argument("--tool-state", type=Path, required=True)
    parser.add_argument("--inspection-output", type=Path, required=True)
    parser.add_argument("--incident-output", type=Path, required=True)
    parser.add_argument("--diagnostic-output", type=Path, required=True)
    parser.add_argument("--policy-output", type=Path, required=True)
    parser.add_argument("--plan-output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    outputs = [
        args.inspection_output,
        args.incident_output,
        args.diagnostic_output,
        args.policy_output,
        args.plan_output,
    ]
    if any(path.exists() for path in outputs):
        print(
            json.dumps(
                {"status": "refused", "error": "one or more action preparation outputs already exist"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    try:
        policy = build_agent_policy(
            generation=args.policy_generation,
            allowed_targets=args.allowed_target,
        )
        incident = build_incident(
            generation=args.incident_generation,
            target=args.target,
            signal=args.signal,
            operator_note=args.operator_note,
        )
        inspection = dict(LocalServiceStateAdapter(args.tool_state).inspect(args.target))
        diagnostic = build_diagnostic_snapshot(
            incident=incident,
            inspection=inspection,
        )
        plan = plan_incident_action(
            incident=incident,
            diagnostic=diagnostic,
            policy=policy,
        )
        atomic_write_json(args.policy_output, policy)
        atomic_write_json(args.incident_output, incident)
        atomic_write_json(args.inspection_output, inspection)
        atomic_write_json(args.diagnostic_output, diagnostic)
        atomic_write_json(args.plan_output, plan)
    except AgentContractError as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "status": "planned",
                "incident_id": incident["incident_id"],
                "inspection_id": inspection["inspection_id"],
                "diagnostic_id": diagnostic["diagnostic_id"],
                "policy_id": policy["policy_id"],
                "plan_id": plan["plan_id"],
                "disposition": plan["disposition"],
                "action_digest": plan["action_digest"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
