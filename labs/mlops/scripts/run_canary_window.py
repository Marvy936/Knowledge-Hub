from __future__ import annotations

import argparse
import json
from pathlib import Path

from mlops_lab.canary import (
    build_canary_decision,
    execute_canary_window,
    rollback_from_canary_decision,
)
from mlops_lab.contracts import ContractError, atomic_write_json, read_json


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Execute a loopback live-canary window and write bounded evidence."
    )
    parser.add_argument("--routing-state", type=Path, required=True)
    parser.add_argument("--stable", type=Path, required=True)
    parser.add_argument("--stable-endpoint", required=True)
    parser.add_argument("--canary", type=Path, required=True)
    parser.add_argument("--canary-endpoint", required=True)
    parser.add_argument("--requests-jsonl", type=Path, required=True)
    parser.add_argument("--minimum-canary-requests", type=int, required=True)
    parser.add_argument("--maximum-canary-error-rate", type=float, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=3.0)
    parser.add_argument("--evidence-output", type=Path, required=True)
    parser.add_argument("--decision-output", type=Path, required=True)
    parser.add_argument("--rollback-output", type=Path)
    return parser


def _load_requests(path: Path) -> list[tuple[str, dict[str, object]]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise ContractError(f"request corpus does not exist: {path}") from exc
    requests: list[tuple[str, dict[str, object]]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError(
                f"invalid JSONL request at line {line_number}: {exc}"
            ) from exc
        if not isinstance(item, dict) or set(item) != {"routing_key", "record"}:
            raise ContractError(
                f"request line {line_number} must contain routing_key and record"
            )
        if not isinstance(item["routing_key"], str) or not item["routing_key"].strip():
            raise ContractError(f"request line {line_number} has invalid routing_key")
        if not isinstance(item["record"], dict):
            raise ContractError(f"request line {line_number} record must be an object")
        requests.append((item["routing_key"], item["record"]))
    return requests


def main() -> int:
    args = _parser().parse_args()
    try:
        routing_state = read_json(args.routing_state)
        stable = read_json(args.stable)
        canary = read_json(args.canary)
        deployments = {
            stable["deployment_id"]: stable,
            canary["deployment_id"]: canary,
        }
        evidence = execute_canary_window(
            routing_state=routing_state,
            deployments=deployments,
            endpoints={
                stable["deployment_id"]: args.stable_endpoint,
                canary["deployment_id"]: args.canary_endpoint,
            },
            requests=_load_requests(args.requests_jsonl),
            timeout_seconds=args.timeout_seconds,
        )
        decision = build_canary_decision(
            evidence=evidence,
            expected_routing_state_id=routing_state["routing_state_id"],
            minimum_canary_requests=args.minimum_canary_requests,
            maximum_canary_error_rate=args.maximum_canary_error_rate,
        )
        atomic_write_json(args.evidence_output, evidence)
        atomic_write_json(args.decision_output, decision)
        if decision["action"] == "rollback":
            if args.rollback_output is None:
                raise ContractError(
                    "rollback-output is required when the canary decision is rollback"
                )
            rollback = rollback_from_canary_decision(
                decision=decision,
                current_routing_state=routing_state,
                target_stable=stable,
            )
            atomic_write_json(args.rollback_output, rollback)
            return 4
        if decision["action"] in {"no_data", "insufficient_evidence"}:
            return 3
        return 0
    except ContractError as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
