from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_ops.contracts import AgentContractError, atomic_write_json
from agent_ops.evaluation import load_eval_cases, run_agent_evaluation


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run deterministic bounded-agent hard evaluation for trajectory, tool selection, "
            "policy compliance, completion and business outcome."
        )
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=Path("labs/agent-ops/data/eval-cases.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.output.exists() or args.output.is_symlink():
        print(
            json.dumps(
                {"status": "refused", "error": "evaluation output already exists"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    try:
        report = run_agent_evaluation(load_eval_cases(args.cases))
        atomic_write_json(args.output, report)
    except AgentContractError as exc:
        print(
            json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True),
            file=sys.stderr,
        )
        return 2
    print(
        json.dumps(
            {
                "status": "passed" if report["all_passed"] else "failed",
                "report_id": report["report_id"],
                "case_count": report["case_count"],
                "passed_count": report["passed_count"],
                "failed_count": report["failed_count"],
                "output": args.output.as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0 if report["all_passed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
