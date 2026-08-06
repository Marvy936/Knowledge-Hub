from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from mlops_lab.contracts import ContractError, atomic_write_json, read_json
from mlops_lab.controlled_retraining import (
    build_controlled_retraining_operation,
    execute_controlled_retraining,
    validate_controlled_retraining_operation,
)
from mlops_lab.registry import register_candidate


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Execute one approval-bound controlled retraining operation."
    )
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--proposal", type=Path, required=True)
    parser.add_argument("--drift-report", type=Path, required=True)
    parser.add_argument("--current-deployment", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--dataset-generation", required=True)
    parser.add_argument("--sample-request", type=Path, required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--tracking-uri", required=True)
    parser.add_argument("--experiment-name", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--registry-alias", required=True)
    parser.add_argument("--promotion-alias", required=True)
    parser.add_argument("--alias-state", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--operation-output", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--recover-expected-state-id")
    return parser


def _train_adapter(
    dataset_path: Path,
    artifact_dir: Path,
    seed: int,
    source_revision: str,
):
    try:
        from ml_lab.training import train_and_package
    except ImportError as exc:
        raise ContractError(
            "controlled retraining requires the Machine Learning flagship package"
        ) from exc

    previous = os.environ.get("GITHUB_SHA")
    os.environ["GITHUB_SHA"] = source_revision
    try:
        return train_and_package(
            dataset_path,
            artifact_dir,
            seed=seed,
            overwrite=False,
        )
    finally:
        if previous is None:
            os.environ.pop("GITHUB_SHA", None)
        else:
            os.environ["GITHUB_SHA"] = previous


def _registry_adapter(
    candidate,
    model_path: Path,
    sample_request_path: Path,
    config,
    download_dir: Path,
):
    return register_candidate(
        candidate=candidate,
        model_path=model_path,
        sample_request_path=sample_request_path,
        tracking_uri=config["tracking_uri"],
        experiment_name=config["experiment_name"],
        model_name=config["model_name"],
        alias=config["alias"],
        download_dir=download_dir,
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        approval = read_json(args.approval)
        proposal = read_json(args.proposal)
        drift_report = read_json(args.drift_report)
        current_deployment = read_json(args.current_deployment)
        operation = build_controlled_retraining_operation(
            approval=approval,
            proposal=proposal,
            drift_report=drift_report,
            current_deployment=current_deployment,
            dataset_path=args.dataset,
            dataset_name=args.dataset_name,
            dataset_generation=args.dataset_generation,
            sample_request_path=args.sample_request,
            source_revision=args.source_revision,
            seed=args.seed,
            tracking_uri=args.tracking_uri,
            experiment_name=args.experiment_name,
            model_name=args.model_name,
            registry_alias=args.registry_alias,
            promotion_alias=args.promotion_alias,
        )
        if args.operation_output.is_file():
            existing = read_json(args.operation_output)
            validate_controlled_retraining_operation(existing)
            if existing != operation:
                raise ContractError(
                    "operation output already contains another controlled retraining subject"
                )
        else:
            atomic_write_json(args.operation_output, operation)

        result = execute_controlled_retraining(
            operation=operation,
            approval=approval,
            proposal=proposal,
            drift_report=drift_report,
            current_deployment=current_deployment,
            dataset_path=args.dataset,
            sample_request_path=args.sample_request,
            output_dir=args.output_dir,
            alias_state_path=args.alias_state,
            state_path=args.state,
            train_adapter=_train_adapter,
            registry_adapter=_registry_adapter,
            recover_expected_state_id=args.recover_expected_state_id,
        )
    except (ContractError, RuntimeError) as exc:
        print(
            json.dumps(
                {"status": "refused", "error": str(exc)},
                sort_keys=True,
            )
        )
        return 2

    state = result["state"]
    print(
        json.dumps(
            {
                "status": result["status"],
                "operation_id": state["operation_id"],
                "state_id": state["state_id"],
                "phase": state["phase"],
                "attempt": state["attempt"],
                "candidate_id": state["artifacts"]["candidate_id"],
                "registry_evidence_id": state["artifacts"][
                    "registry_evidence_id"
                ],
                "registry_version": state["artifacts"]["registry_version"],
                "release_id": state["artifacts"]["release_id"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
