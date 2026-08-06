from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from ..contracts import (
    ContractError,
    atomic_write_json,
    read_json,
    sha256_bytes,
    canonical_json_bytes,
    sha256_file,
    validate_candidate_manifest,
)
from ..lineage import validate_training_manifest
from ..registry import validate_registry_evidence
from ..serving import validate_release_manifest
from .common import (
    ARTIFACT_FIELDS,
    EXECUTOR_SCHEMA_VERSION,
    PHASES,
    require_exact_keys,
    require_nonempty_string,
    require_sha256,
    validate_canonical_id,
)


def _empty_artifacts() -> dict[str, Any]:
    return {field: None for field in ARTIFACT_FIELDS}


def _build_state(
    *,
    operation_id: str,
    phase: str,
    attempt: int,
    previous_state_id: str | None,
    artifacts: Mapping[str, Any],
    failure: str | None,
) -> dict[str, Any]:
    payload = {
        "schema_version": EXECUTOR_SCHEMA_VERSION,
        "operation_id": require_sha256(operation_id, "state.operation_id"),
        "phase": phase,
        "attempt": attempt,
        "previous_state_id": previous_state_id,
        "artifacts": dict(artifacts),
        "failure": failure,
    }
    state = {**payload, "state_id": sha256_bytes(canonical_json_bytes(payload))}
    validate_controlled_retraining_state(state)
    return state


def validate_controlled_retraining_state(value: Mapping[str, Any]) -> None:
    require_exact_keys(
        value,
        {
            "schema_version",
            "operation_id",
            "phase",
            "attempt",
            "previous_state_id",
            "artifacts",
            "failure",
            "state_id",
        },
        "controlled retraining state",
    )
    if value.get("schema_version") != EXECUTOR_SCHEMA_VERSION:
        raise ContractError("controlled retraining state schema_version must equal 1")
    require_sha256(value.get("operation_id"), "state.operation_id")
    phase = require_nonempty_string(value.get("phase"), "state.phase")
    if phase not in PHASES:
        raise ContractError("controlled retraining state phase is unsupported")

    attempt = value.get("attempt")
    if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 1:
        raise ContractError("state.attempt must be a positive integer")
    previous = value.get("previous_state_id")
    if previous is not None:
        require_sha256(previous, "state.previous_state_id")

    artifacts = value.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != set(ARTIFACT_FIELDS):
        raise ContractError("state.artifacts keys mismatch")
    for field, item in artifacts.items():
        if item is None:
            continue
        if field == "registry_version":
            if not isinstance(item, str) or not item.isdigit() or int(item) < 1:
                raise ContractError(
                    "state.artifacts.registry_version must be numeric"
                )
        else:
            require_sha256(item, f"state.artifacts.{field}")

    failure = value.get("failure")
    if phase == "failed":
        require_nonempty_string(failure, "state.failure")
    elif failure is not None:
        raise ContractError("state.failure must be null outside failed phase")

    required_by_phase = {
        "training_completed": (
            "training_manifest_sha256",
            "model_sha256",
        ),
        "candidate_recorded": (
            "training_manifest_sha256",
            "model_sha256",
            "evaluation_file_sha256",
            "candidate_id",
        ),
        "registry_recorded": (
            "training_manifest_sha256",
            "model_sha256",
            "evaluation_file_sha256",
            "candidate_id",
            "registry_evidence_id",
            "registry_version",
        ),
        "promotion_started": (
            "training_manifest_sha256",
            "model_sha256",
            "evaluation_file_sha256",
            "candidate_id",
            "registry_evidence_id",
            "registry_version",
        ),
        "completed": ARTIFACT_FIELDS,
    }
    for field in required_by_phase.get(phase, ()):
        if artifacts[field] is None:
            raise ContractError(f"state phase {phase} requires artifact {field}")
    validate_canonical_id(value, "state_id")


def _transition(
    current: Mapping[str, Any],
    *,
    phase: str,
    artifacts: Mapping[str, Any] | None = None,
    failure: str | None = None,
    increment_attempt: bool = False,
) -> dict[str, Any]:
    validate_controlled_retraining_state(current)
    next_artifacts = dict(current["artifacts"])
    if artifacts:
        next_artifacts.update(artifacts)
    return _build_state(
        operation_id=current["operation_id"],
        phase=phase,
        attempt=current["attempt"] + (1 if increment_attempt else 0),
        previous_state_id=current["state_id"],
        artifacts=next_artifacts,
        failure=failure,
    )


def _paths(output_dir: Path) -> dict[str, Path]:
    return {
        "artifact_dir": output_dir / "artifact",
        "training_manifest": output_dir / "artifact" / "manifest.json",
        "model": output_dir / "artifact" / "model.joblib",
        "evaluation": output_dir / "evaluation.json",
        "candidate": output_dir / "candidate.json",
        "registry_evidence": output_dir / "registry-evidence.json",
        "release": output_dir / "release.json",
        "download_dir": output_dir / "registry-download",
    }


def _readback_checkpoint(
    *,
    operation: Mapping[str, Any],
    dataset_path: Path,
    sample_request_path: Path,
    output_dir: Path,
    alias_state_path: Path,
) -> tuple[str, dict[str, Any]]:
    del sample_request_path
    paths = _paths(output_dir)
    artifacts = _empty_artifacts()
    manifest_exists = paths["training_manifest"].is_file()
    model_exists = paths["model"].is_file()
    if manifest_exists != model_exists:
        raise ContractError("partial training output requires manual reconciliation")
    if not manifest_exists:
        managed = (
            paths["evaluation"],
            paths["candidate"],
            paths["registry_evidence"],
            paths["release"],
        )
        if any(path.exists() for path in managed):
            raise ContractError(
                "orphaned retraining outputs require manual reconciliation"
            )
        return "planned", artifacts

    manifest = read_json(paths["training_manifest"])
    validate_training_manifest(
        manifest,
        dataset_path=dataset_path,
        model_path=paths["model"],
        expected_source_revision=operation["source_revision"],
    )
    artifacts["training_manifest_sha256"] = sha256_file(
        paths["training_manifest"]
    )
    artifacts["model_sha256"] = sha256_file(paths["model"])

    if not paths["evaluation"].is_file() and not paths["candidate"].is_file():
        if paths["registry_evidence"].exists() or paths["release"].exists():
            raise ContractError(
                "orphaned Registry or release output requires reconciliation"
            )
        return "training_completed", artifacts
    if not paths["evaluation"].is_file() or not paths["candidate"].is_file():
        raise ContractError("partial candidate output requires manual reconciliation")

    evaluation = read_json(paths["evaluation"])
    candidate = read_json(paths["candidate"])
    validate_candidate_manifest(candidate)
    candidate_evaluation = {
        "accepted": candidate["evaluation"]["accepted"],
        "metrics": candidate["evaluation"]["metrics"],
        "policy_generation": candidate["evaluation"]["policy_generation"],
    }
    if evaluation != candidate_evaluation:
        raise ContractError("evaluation file does not match candidate evidence")
    if candidate["source_revision"] != operation["source_revision"]:
        raise ContractError("candidate source revision does not match operation")
    if candidate["model"]["sha256"] != artifacts["model_sha256"]:
        raise ContractError("candidate model digest does not match training output")
    if candidate["dataset"]["sha256"] != operation["dataset"]["sha256"]:
        raise ContractError("candidate dataset digest does not match operation")

    artifacts["evaluation_file_sha256"] = sha256_file(paths["evaluation"])
    artifacts["candidate_id"] = candidate["candidate_id"]
    if not paths["registry_evidence"].is_file():
        if paths["release"].exists():
            raise ContractError("release exists without Registry evidence")
        return "candidate_recorded", artifacts

    registry_evidence = read_json(paths["registry_evidence"])
    validate_registry_evidence(registry_evidence)
    if registry_evidence["candidate_id"] != candidate["candidate_id"]:
        raise ContractError("Registry evidence belongs to another candidate")
    if registry_evidence["source_revision"] != operation["source_revision"]:
        raise ContractError(
            "Registry evidence source revision does not match operation"
        )
    if (
        registry_evidence["artifact_readback"]["downloaded_sha256"]
        != artifacts["model_sha256"]
    ):
        raise ContractError("Registry artifact digest does not match training output")
    artifacts["registry_evidence_id"] = registry_evidence[
        "registry_evidence_id"
    ]
    artifacts["registry_version"] = registry_evidence["registry"]["version"]
    if not paths["release"].is_file():
        return "registry_recorded", artifacts

    release = read_json(paths["release"])
    validate_release_manifest(release)
    if release["candidate_id"] != candidate["candidate_id"]:
        raise ContractError("release belongs to another candidate")
    if not alias_state_path.is_file():
        raise ContractError("release exists without alias-state read-back")
    alias_state = read_json(alias_state_path)
    if (
        alias_state.get("schema_version") != 1
        or alias_state.get("aliases", {}).get(operation["promotion"]["alias"])
        != candidate["candidate_id"]
    ):
        raise ContractError("alias state does not point to completed candidate")
    artifacts["release_id"] = release["release_id"]
    artifacts["alias_state_file_sha256"] = sha256_file(alias_state_path)
    return "completed", artifacts


def reconcile_controlled_retraining(
    *,
    operation: Mapping[str, Any],
    state_path: Path,
    dataset_path: Path,
    sample_request_path: Path,
    output_dir: Path,
    alias_state_path: Path,
    expected_state_id: str,
) -> dict[str, Any]:
    if not state_path.is_file():
        raise ContractError("no retraining state exists to recover")
    current = read_json(state_path)
    validate_controlled_retraining_state(current)
    if current["operation_id"] != operation["operation_id"]:
        raise ContractError("retraining state belongs to another operation")
    if current["state_id"] != require_sha256(
        expected_state_id, "expected_state_id"
    ):
        raise ContractError("stale retraining recovery subject")
    if current["phase"] == "completed":
        return current

    phase, artifacts = _readback_checkpoint(
        operation=operation,
        dataset_path=dataset_path,
        sample_request_path=sample_request_path,
        output_dir=output_dir,
        alias_state_path=alias_state_path,
    )
    recovered = _build_state(
        operation_id=operation["operation_id"],
        phase=phase,
        attempt=current["attempt"] + 1,
        previous_state_id=current["state_id"],
        artifacts=artifacts,
        failure=None,
    )
    atomic_write_json(state_path, recovered)
    return recovered


def _acquire_lock(lock_path: Path) -> int:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        return os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ContractError(
            "controlled retraining operation is already locked"
        ) from exc


def _write_phase(
    state_path: Path, current: Mapping[str, Any], **kwargs: Any
) -> dict[str, Any]:
    state = _transition(current, **kwargs)
    atomic_write_json(state_path, state)
    return state
