from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from mlops_lab.contracts import ContractError, atomic_write_json, read_json
from mlops_lab.retraining import approve_retraining


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Authorize one exact retraining proposal without executing training."
    )
    parser.add_argument("--proposal", type=Path, required=True)
    parser.add_argument("--drift-report", type=Path, required=True)
    parser.add_argument("--expected-proposal-id", required=True)
    parser.add_argument("--approver", required=True)
    parser.add_argument("--approval-generation", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        approval = approve_retraining(
            proposal=read_json(args.proposal),
            drift_report=read_json(args.drift_report),
            expected_proposal_id=args.expected_proposal_id,
            approver=args.approver,
            approval_generation=args.approval_generation,
        )
        atomic_write_json(args.output, approval)
    except ContractError as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True))
        return 2

    print(
        json.dumps(
            {
                "status": "retraining_authorized",
                "retraining_proposal_id": approval["retraining_proposal_id"],
                "retraining_approval_id": approval["retraining_approval_id"],
                "authorized_action": approval["authorized_action"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
