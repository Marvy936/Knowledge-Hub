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
from .lineage import build_evaluation_from_training_manifest
from .registry import register_candidate, verify_registered_model


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mlops-lab",
        description="Deterministic lineage, registry and promotion contracts for the MLOps flagship lab.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    snapshot = commands.add_parser("snapshot", help="Create an immutable dataset manifest")
    snapshot.add_argument("--dataset", type=Path, required=True)
    snapshot.add_argument("--output", type=Path, required=True)
    snapshot.add_argument("--dataset-name", required=True)
    snapshot.add_argument("--generation", required=True)

    evaluation = commands.add_parser(
        "evaluation-from-training",
        help="Derive an accepted evaluation bundle from an exact ML training manifest",
    )
    evaluation.add_argument("--training-manifest", type=Path, required=True)
    evaluation.add_argument("--dataset", type=Path, required=True)
    evaluation.add_argument("--model", type=Path, required=True)
    evaluation.add_argument("--source-revision", required=True)
    evaluation.add_argument(
        "--policy-generation", default="ml-training-manifest-v1"
    )
    evaluation.add_argument("--output", type=Path, required=True)

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

    registry_roundtrip = commands.add_parser(
        "registry-roundtrip",
        help="Register a candidate in MLflow and prove metadata, artifact and model read-back",
    )
    registry_roundtrip.add_argument("--candidate", type=Path, required=True)
    registry_roundtrip.add_argument("--model", type=Path, required=True)
    registry_roundtrip.add_argument("--sample-request", type=Path, required=True)
    registry_roundtrip.add_argument("--tracking-uri", required=True)
    registry_roundtrip.add_argument("--experiment-name", required=True)
    registry_roundtrip.add_argument("--model-name", required=True)
    registry_roundtrip.add_argument("--alias", required=True)
    registry_roundtrip.add_argument("--download-dir", type=Path, required=True)
    registry_roundtrip.add_argument("--output", type=Path, required=True)

    registry_verify = commands.add_parser(
        "registry-verify",
        help="Load the exact registered model version and verify recorded prediction parity",
    )
    registry_verify.add_argument("--evidence", type=Path, required=True)
    registry_verify.add_argument("--sample-request", type=Path, required=True)
    registry_verify.add_argument("--tracking-uri")

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
        elif args.command == "evaluation-from-training":
            evaluation = build_evaluation_from_training_manifest(
                training_manifest_path=args.training_manifest,
                dataset_path=args.dataset,
                model_path=args.model,
                expected_source_revision=args.source_revision,
                policy_generation=args.policy_generation,
            )
            atomic_write_json(args.output, evaluation)
            result = {
                "status": "training_evaluation_recorded",
                "output": args.output.as_posix(),
                "accepted": evaluation["accepted"],
                "policy_generation": evaluation["policy_generation"],
                "metrics": evaluation["metrics"],
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
        elif args.command == "promote":
            expected_current = (
                None
                if args.expected_current.strip().lower() == "none"
                else args.expected_current.strip()
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
        elif args.command == "registry-roundtrip":
            evidence = register_candidate(
                candidate=read_json(args.candidate),
                model_path=args.model,
                sample_request_path=args.sample_request,
                tracking_uri=args.tracking_uri,
                experiment_name=args.experiment_name,
                model_name=args.model_name,
                alias=args.alias,
                download_dir=args.download_dir,
            )
            atomic_write_json(args.output, evidence)
            result = {
                "status": "registry_roundtrip_verified",
                "output": args.output.as_posix(),
                "registry_evidence_id": evidence["registry_evidence_id"],
                "run_id": evidence["run_id"],
                "model_name": evidence["registry"]["name"],
                "version": evidence["registry"]["version"],
                "exact_uri": evidence["registry"]["exact_uri"],
            }
        else:
            result = verify_registered_model(
                evidence=read_json(args.evidence),
                sample_request_path=args.sample_request,
                tracking_uri=args.tracking_uri,
            )
    except ContractError as exc:
        print(
            json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True),
            file=sys.stderr,
        )
        return 2

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
