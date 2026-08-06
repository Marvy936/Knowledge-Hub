from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .contracts import (
    ContractError,
    atomic_write_json,
    build_candidate_manifest,
    build_dataset_manifest,
    promote_candidate,
    read_json,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mlops-lab",
        description="Deterministic lineage and promotion foundation for the MLOps flagship lab.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    snapshot = commands.add_parser("snapshot", help="Create an immutable dataset manifest")
    snapshot.add_argument("--dataset", type=Path, required=True)
    snapshot.add_argument("--output", type=Path, required=True)
    snapshot.add_argument("--dataset-name", required=True)
    snapshot.add_argument("--generation", required=True)

    candidate = commands.add_parser("candidate", help="Create an accepted candidate manifest")
    candidate.add_argument("--dataset-manifest", type=Path, required=True)
    candidate.add_argument("--model", type=Path, required=True)
    candidate.add_argument("--evaluation", type=Path, required=True)
    candidate.add_argument("--source-revision", required=True)
    candidate.add_argument("--output", type=Path, required=True)

    promote = commands.add_parser("promote", help="Create a release manifest and move an alias")
    promote.add_argument("--candidate", type=Path, required=True)
    promote.add_argument("--alias-state", type=Path, required=True)
    promote.add_argument("--alias", required=True)
    promote.add_argument("--expected-current", required=True)
    promote.add_argument("--release-output", type=Path, required=True)

    return parser


def _load_alias_state(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"schema_version": 1, "aliases": {}}
    state = read_json(path)
    if state.get("schema_version") != 1:
        raise ContractError("alias state schema_version must equal 1")
    return state


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "snapshot":
            manifest = build_dataset_manifest(
                args.dataset,
                dataset_name=args.dataset_name,
                generation=args.generation,
            )
            atomic_write_json(args.output, manifest)
            result = {
                "status": "dataset_snapshot_recorded",
                "output": args.output.as_posix(),
                "dataset_sha256": manifest["subject"]["sha256"],
            }
        elif args.command == "candidate":
            manifest = build_candidate_manifest(
                dataset_manifest=read_json(args.dataset_manifest),
                model_path=args.model,
                evaluation=read_json(args.evaluation),
                source_revision=args.source_revision,
            )
            atomic_write_json(args.output, manifest)
            result = {
                "status": "candidate_recorded",
                "output": args.output.as_posix(),
                "candidate_id": manifest["candidate_id"],
                "accepted": manifest["evaluation"]["accepted"],
            }
        else:
            expected_current = (
                None if args.expected_current.strip().lower() == "none" else args.expected_current.strip()
            )
            alias_state = _load_alias_state(args.alias_state)
            release, next_state = promote_candidate(
                candidate=read_json(args.candidate),
                alias_state=alias_state,
                alias=args.alias,
                expected_current=expected_current,
            )
            atomic_write_json(args.release_output, release)
            atomic_write_json(args.alias_state, next_state)
            result = {
                "status": "promoted",
                "alias": args.alias,
                "candidate_id": release["candidate_id"],
                "release_id": release["release_id"],
            }
    except ContractError as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
