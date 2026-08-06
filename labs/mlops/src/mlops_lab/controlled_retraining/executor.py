from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Mapping

from ..contracts import (
    ContractError,
    atomic_write_json,
    build_candidate_manifest,
    canonical_json_bytes,
    promote_candidate,
    read_json,
    sha256_bytes,
    sha256_file,
)
from ..lineage import (
    build_evaluation_from_training_manifest,
    validate_training_manifest,
)
from ..registry import validate_registry_evidence
from .operation import validate_operation_inputs
from .state import (
    _acquire_lock,
    _build_state,
    _paths,
    _readback_checkpoint,
    _transition,
    _write_phase,
    reconcile_controlled_retraining,
    validate_controlled_retraining_state,
)

TrainAdapter = Callable[[Path, Path, int, str], Mapping[str, Any]]
RegistryAdapter = Callable[
    [Mapping[str, Any], Path, Path, Mapping[str, str], Path], Mapping[str, Any]
]


def _registry_intent_path(output_dir: Path) -> Path:
    return output_dir / "registry-attempt.json"


def _registry_response_path(output_dir: Path) -> Path:
    return output_dir / "registry-response.json"


def _build_registry_intent(
    operation: Mapping[str, Any], candidate: Mapping[str, Any]
) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
        "operation_id": operation["operation_id"],
        "candidate_id": candidate["candidate_id"],
        "source_revision": candidate["source_revision"],
        "model_sha256": candidate["model"]["sha256"],
        "tracking_uri": operation["registry"]["tracking_uri"],
        "model_name": operation["registry"]["model_name"],
        "alias": operation["registry"]["alias"],
    }
    return {
        **payload,
        "registry_attempt_id": sha256_bytes(canonical_json_bytes(payload)),
    }


def _registry_response_matches_intent(
    response: Mapping[str, Any], intent: Mapping[str, Any]
) -> bool:
    return (
        response["candidate_id"] == intent["candidate_id"]
        and response["source_revision"] == intent["source_revision"]
        and response["artifact_readback"]["downloaded_sha256"]
        == intent["model_sha256"]
    )


def _guard_registry_unknown_outcome(
    *, operation: Mapping[str, Any], output_dir: Path
) -> None:
    intent_path = _registry_intent_path(output_dir)
    if not intent_path.is_file():
        return

    intent = read_json(intent_path)
    attempt_id = intent.get("registry_attempt_id")
    payload = {
        key: value
        for key, value in intent.items()
        if key != "registry_attempt_id"
    }
    if (
        not isinstance(attempt_id, str)
        or sha256_bytes(canonical_json_bytes(payload)) != attempt_id
        or intent.get("operation_id") != operation["operation_id"]
    ):
        raise ContractError(
            "Registry attempt intent is invalid or belongs to another operation"
        )

    evidence_path = output_dir / "registry-evidence.json"
    response_path = _registry_response_path(output_dir)
    if evidence_path.is_file():
        response_path.unlink(missing_ok=True)
        intent_path.unlink()
        return

    if response_path.is_file():
        response = read_json(response_path)
        validate_registry_evidence(response)
        if _registry_response_matches_intent(response, intent):
            atomic_write_json(evidence_path, response)
        response_path.unlink()
        intent_path.unlink()
        return

    raise ContractError(
        "Registry mutation outcome is unknown; external Registry read-back "
        "and explicit reconciliation are required"
    )


def execute_controlled_retraining(
    *,
    operation: Mapping[str, Any],
    approval: Mapping[str, Any],
    proposal: Mapping[str, Any],
    drift_report: Mapping[str, Any],
    current_deployment: Mapping[str, Any],
    dataset_path: Path,
    sample_request_path: Path,
    output_dir: Path,
    alias_state_path: Path,
    state_path: Path,
    train_adapter: TrainAdapter,
    registry_adapter: RegistryAdapter,
    recover_expected_state_id: str | None = None,
) -> dict[str, Any]:
    dataset_manifest = validate_operation_inputs(
        operation=operation,
        approval=approval,
        proposal=proposal,
        drift_report=drift_report,
        current_deployment=current_deployment,
        dataset_path=dataset_path,
        sample_request_path=sample_request_path,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = _paths(output_dir)
    lock_path = state_path.with_suffix(state_path.suffix + ".lock")
    descriptor = _acquire_lock(lock_path)
    current: dict[str, Any] | None = None
    mutated_state = False

    try:
        if not state_path.is_file():
            _guard_registry_unknown_outcome(
                operation=operation, output_dir=output_dir
            )

        if state_path.is_file():
            current = read_json(state_path)
            validate_controlled_retraining_state(current)
            if current["operation_id"] != operation["operation_id"]:
                raise ContractError("retraining state belongs to another operation")
            if current["phase"] == "completed":
                phase, artifacts = _readback_checkpoint(
                    operation=operation,
                    dataset_path=dataset_path,
                    sample_request_path=sample_request_path,
                    output_dir=output_dir,
                    alias_state_path=alias_state_path,
                )
                if phase != "completed" or artifacts != current["artifacts"]:
                    raise ContractError(
                        "completed retraining state failed output read-back"
                    )
                return {"status": "already_completed", "state": current}
            if recover_expected_state_id is None:
                raise ContractError(
                    "incomplete retraining operation requires explicit recovery"
                )
            _guard_registry_unknown_outcome(
                operation=operation, output_dir=output_dir
            )
            current = reconcile_controlled_retraining(
                operation=operation,
                state_path=state_path,
                dataset_path=dataset_path,
                sample_request_path=sample_request_path,
                output_dir=output_dir,
                alias_state_path=alias_state_path,
                expected_state_id=recover_expected_state_id,
            )
            mutated_state = True
            if current["phase"] == "completed":
                return {"status": "already_completed", "state": current}
        else:
            phase, artifacts = _readback_checkpoint(
                operation=operation,
                dataset_path=dataset_path,
                sample_request_path=sample_request_path,
                output_dir=output_dir,
                alias_state_path=alias_state_path,
            )
            if phase != "planned":
                raise ContractError(
                    "orphaned retraining outputs require explicit reconciliation"
                )
            current = _build_state(
                operation_id=operation["operation_id"],
                phase="planned",
                attempt=1,
                previous_state_id=None,
                artifacts=artifacts,
                failure=None,
            )
            atomic_write_json(state_path, current)
            mutated_state = True

        if current["phase"] == "planned":
            current = _write_phase(
                state_path, current, phase="training_started"
            )
            mutated_state = True
            train_adapter(
                dataset_path,
                paths["artifact_dir"],
                operation["seed"],
                operation["source_revision"],
            )
            manifest = read_json(paths["training_manifest"])
            validate_training_manifest(
                manifest,
                dataset_path=dataset_path,
                model_path=paths["model"],
                expected_source_revision=operation["source_revision"],
            )
            current = _write_phase(
                state_path,
                current,
                phase="training_completed",
                artifacts={
                    "training_manifest_sha256": sha256_file(
                        paths["training_manifest"]
                    ),
                    "model_sha256": sha256_file(paths["model"]),
                },
            )
            mutated_state = True

        if current["phase"] == "training_completed":
            evaluation = build_evaluation_from_training_manifest(
                training_manifest_path=paths["training_manifest"],
                dataset_path=dataset_path,
                model_path=paths["model"],
                expected_source_revision=operation["source_revision"],
                policy_generation=operation["evaluation_policy_generation"],
            )
            atomic_write_json(paths["evaluation"], evaluation)
            candidate = build_candidate_manifest(
                dataset_manifest=dataset_manifest,
                model_path=paths["model"],
                evaluation=evaluation,
                source_revision=operation["source_revision"],
            )
            atomic_write_json(paths["candidate"], candidate)
            current = _write_phase(
                state_path,
                current,
                phase="candidate_recorded",
                artifacts={
                    "evaluation_file_sha256": sha256_file(paths["evaluation"]),
                    "candidate_id": candidate["candidate_id"],
                },
            )
            mutated_state = True

        if current["phase"] == "candidate_recorded":
            candidate = read_json(paths["candidate"])
            intent_path = _registry_intent_path(output_dir)
            atomic_write_json(
                intent_path, _build_registry_intent(operation, candidate)
            )
            registry_evidence = registry_adapter(
                candidate,
                paths["model"],
                sample_request_path,
                operation["registry"],
                paths["download_dir"],
            )
            response_path = _registry_response_path(output_dir)
            atomic_write_json(response_path, registry_evidence)
            validate_registry_evidence(registry_evidence)
            if registry_evidence["candidate_id"] != candidate["candidate_id"]:
                response_path.unlink()
                intent_path.unlink()
                raise ContractError(
                    "Registry adapter returned evidence for another candidate"
                )
            if registry_evidence["source_revision"] != operation["source_revision"]:
                response_path.unlink()
                intent_path.unlink()
                raise ContractError(
                    "Registry adapter returned another source revision"
                )
            if (
                registry_evidence["artifact_readback"]["downloaded_sha256"]
                != current["artifacts"]["model_sha256"]
            ):
                response_path.unlink()
                intent_path.unlink()
                raise ContractError(
                    "Registry adapter returned another model digest"
                )
            atomic_write_json(paths["registry_evidence"], registry_evidence)
            response_path.unlink()
            intent_path.unlink()
            current = _write_phase(
                state_path,
                current,
                phase="registry_recorded",
                artifacts={
                    "registry_evidence_id": registry_evidence[
                        "registry_evidence_id"
                    ],
                    "registry_version": registry_evidence["registry"]["version"],
                },
            )
            mutated_state = True

        if current["phase"] == "registry_recorded":
            current = _write_phase(
                state_path, current, phase="promotion_started"
            )
            mutated_state = True
            candidate = read_json(paths["candidate"])
            if not alias_state_path.is_file():
                raise ContractError("promotion alias state does not exist")
            alias_state = read_json(alias_state_path)
            release, next_alias_state = promote_candidate(
                candidate=candidate,
                alias_state=alias_state,
                alias=operation["promotion"]["alias"],
                expected_current=operation["promotion"][
                    "expected_current_candidate_id"
                ],
            )
            atomic_write_json(paths["release"], release)
            atomic_write_json(alias_state_path, next_alias_state)
            current = _write_phase(
                state_path,
                current,
                phase="completed",
                artifacts={
                    "release_id": release["release_id"],
                    "alias_state_file_sha256": sha256_file(alias_state_path),
                },
            )
            mutated_state = True

        return {"status": "completed", "state": current}
    except Exception as exc:
        if (
            mutated_state
            and current is not None
            and current.get("phase") != "completed"
        ):
            try:
                failed = _transition(
                    current,
                    phase="failed",
                    failure=f"{type(exc).__name__}: {str(exc)[:240]}",
                )
                atomic_write_json(state_path, failed)
            except Exception:
                pass
        raise
    finally:
        os.close(descriptor)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
