from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from mlops_lab.contracts import ContractError, atomic_write_json, read_json
from mlops_lab.post_retraining import build_post_retraining_handoff


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build an immutable post-retraining deployment and canary handoff."
    )
    parser.add_argument("--operation", type=Path, required=True)
    parser.add_argument("--completed-state", type=Path, required=True)
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--registry-evidence", type=Path, required=True)
    parser.add_argument("--current-deployment", type=Path, required=True)
    parser.add_argument("--current-routing-state", type=Path, required=True)
    parser.add_argument("--service-name", required=True)
    parser.add_argument("--generation", required=True)
    parser.add_argument("--image-reference", required=True)
    parser.add_argument("--image-digest", required=True)
    parser.add_argument("--canary-basis-points", type=int, required=True)
    parser.add_argument("--expected-current-routing-state-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        handoff = build_post_retraining_handoff(
            operation=read_json(args.operation),
            completed_state=read_json(args.completed_state),
            release=read_json(args.release),
            registry_evidence=read_json(args.registry_evidence),
            current_deployment=read_json(args.current_deployment),
            current_routing_state=read_json(args.current_routing_state),
            service_name=args.service_name,
            generation=args.generation,
            image_reference=args.image_reference,
            image_digest=args.image_digest,
            canary_basis_points=args.canary_basis_points,
            expected_current_routing_state_id=(
                args.expected_current_routing_state_id
            ),
        )
        atomic_write_json(args.output, handoff)
    except ContractError as exc:
        print(
            json.dumps(
                {"status": "refused", "error": str(exc)},
                sort_keys=True,
            )
        )
        return 2

    print(
        json.dumps(
            {
                "status": "post_retraining_handoff_recorded",
                "post_retraining_handoff_id": handoff[
                    "post_retraining_handoff_id"
                ],
                "deployment_id": handoff["deployment"]["deployment_id"],
                "routing_state_id": handoff["routing_state"][
                    "routing_state_id"
                ],
                "canary_basis_points": handoff["routing_state"][
                    "canary_basis_points"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
