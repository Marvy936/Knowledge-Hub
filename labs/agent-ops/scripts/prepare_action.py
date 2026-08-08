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


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build deterministic incident, diagnostic, policy and bounded action-plan artifacts."
    )
    parser.add_argument("--target", required=True)
    parser.add_argument("--signal", required=True)
    parser.add_argument("--operator-note", required=True)
    parser.add_argument("--service-generation", type=int, required=True)
    parser.add_argument("--service-status", required=True)
    parser.add_argument("--incident-generation", required=True)
    parser.add_argument("--policy-generation", required=True)
    parser.add_argument("--allowed-target", action="append", required=True)
    parser.add_argument("--incident-output", type=Path, required=True)
    parser.add_argument("--diagnostic-output", type=Path, required=True)
    parser.add_argument("--policy-output", type=Path, required=True)
    parser.add_argument("--plan-output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    outputs = [
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
        diagnostic = build_diagnostic_snapshot(
            incident=incident,
            service_generation=args.service_generation,
            service_status=args.service_status,
        )
        plan = plan_incident_action(
            incident=incident,
            diagnostic=diagnostic,
            policy=policy,
        )
        atomic_write_json(args.policy_output, policy)
        atomic_write_json(args.incident_output, incident)
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
