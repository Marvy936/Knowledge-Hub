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
from .serving import (
    build_deployment_manifest,
    build_rollback_state,
    build_routing_state,
    route_request,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mlops-lab",
        description="Deterministic lineage, registry, serving and promotion contracts for the MLOps flagship lab.",
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

    deployment = commands.add_parser(
        "deployment",
        help="Bind a release, exact Registry version and image digest into one deployment subject",
    )
    deployment.add_argument("--release", type=Path, required=True)
    deployment.add_argument("--registry-evidence", type=Path, required=True)
    deployment.add_argument("--service-name", required=True)
    deployment.add_argument("--generation", required=True)
    deployment.add_argument("--image-reference", required=True)
    deployment.add_argument("--image-digest", required=True)
    deployment.add_argument("--output", type=Path, required=True)

    routing_state = commands.add_parser(
        "routing-state",
        help="Create a compare-before-change stable/canary routing state",
    )
    routing_state.add_argument("--stable", type=Path, required=True)
    routing_state.add_argument("--canary", type=Path)
    routing_state.add_argument("--canary-basis-points", type=int, required=True)
    routing_state.add_argument("--current-state", type=Path)
    routing_state.add_argument("--expected-current-state-id", required=True)
    routing_state.add_argument("--output", type=Path, required=True)

    route = commands.add_parser(
        "route",
        help="Resolve one deterministic request assignment from an immutable routing state",
    )
    route.add_argument("--routing-state", type=Path, required=True)
    route.add_argument("--stable", type=Path, required=True)
    route.add_argument("--canary", type=Path)
    route.add_argument("--routing-key", required=True)

    rollback = commands.add_parser(
        "rollback",
        help="Restore an exact stable deployment without resolving a mutable Registry alias",
    )
    rollback.add_argument("--current-state", type=Path, required=True)
    rollback.add_argument("--target-stable", type=Path, required=True)
    rollback.add_argument("--expected-current-state-id", required=True)
    rollback.add_argument("--output", type=Path, required=True)

    return parser


def _load_alias_state(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"schema_version": 1, "aliases": {}}
    state = read_json(path)
    if state.get("schema_version") != 1:
        raise ContractError("alias state schema_version must equal 1")
    return state


def _optional_state_id(value: str) -> str | None:
    resolved = value.strip()
    return None if resolved.lower() == "none" else resolved


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
        elif args.command == "registry-verify":
            result = verify_registered_model(
                evidence=read_json(args.evidence),
                sample_request_path=args.sample_request,
                tracking_uri=args.tracking_uri,
            )
        elif args.command == "deployment":
            deployment_manifest = build_deployment_manifest(
                release=read_json(args.release),
                registry_evidence=read_json(args.registry_evidence),
                service_name=args.service_name,
                generation=args.generation,
                image_reference=args.image_reference,
                image_digest=args.image_digest,
            )
            atomic_write_json(args.output, deployment_manifest)
            result = {
                "status": "deployment_subject_recorded",
                "output": args.output.as_posix(),
                "deployment_id": deployment_manifest["deployment_id"],
                "generation": deployment_manifest["generation"],
                "exact_uri": deployment_manifest["model"]["exact_uri"],
                "image_digest": deployment_manifest["image"]["digest"],
            }
        elif args.command == "routing-state":
            stable = read_json(args.stable)
            canary = None if args.canary is None else read_json(args.canary)
            current = (
                None if args.current_state is None else read_json(args.current_state)
            )
            state = build_routing_state(
                stable=stable,
                canary=canary,
                canary_basis_points=args.canary_basis_points,
                current_state=current,
                expected_current_state_id=_optional_state_id(
                    args.expected_current_state_id
                ),
            )
            atomic_write_json(args.output, state)
            result = {
                "status": "routing_state_recorded",
                "output": args.output.as_posix(),
                "routing_state_id": state["routing_state_id"],
                "stable_deployment_id": state["stable_deployment_id"],
                "canary_deployment_id": state["canary_deployment_id"],
                "canary_basis_points": state["canary_basis_points"],
            }
        elif args.command == "route":
            stable = read_json(args.stable)
            deployments = {stable["deployment_id"]: stable}
            if args.canary is not None:
                canary = read_json(args.canary)
                deployments[canary["deployment_id"]] = canary
            result = {
                "status": "request_routed",
                **route_request(
                    routing_state=read_json(args.routing_state),
                    deployments=deployments,
                    routing_key=args.routing_key,
                ),
            }
        else:
            state = build_rollback_state(
                current_state=read_json(args.current_state),
                target_stable=read_json(args.target_stable),
                expected_current_state_id=args.expected_current_state_id,
            )
            atomic_write_json(args.output, state)
            result = {
                "status": "rollback_state_recorded",
                "output": args.output.as_posix(),
                "routing_state_id": state["routing_state_id"],
                "stable_deployment_id": state["stable_deployment_id"],
                "previous_routing_state_id": state["previous_routing_state_id"],
            }
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
