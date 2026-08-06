from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping


class ContractError(ValueError):
    """Raised when an input violates the MLOps evidence contract."""


def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"Required JSON file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"Expected a JSON object in {path}")
    return value


def atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    finally:
        temporary = Path(temporary_name)
        if temporary.exists():
            temporary.unlink()


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value.strip()


def _require_sha256(value: Any, field: str) -> str:
    text = _require_nonempty_string(value, field)
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise ContractError(f"{field} must be a lowercase SHA-256 hex digest")
    return text


def build_dataset_manifest(
    dataset_path: Path, *, dataset_name: str, generation: str
) -> dict[str, Any]:
    if not dataset_path.is_file():
        raise ContractError(f"Dataset does not exist or is not a file: {dataset_path}")
    name = _require_nonempty_string(dataset_name, "dataset_name")
    resolved_generation = _require_nonempty_string(generation, "generation")
    return {
        "schema_version": 1,
        "subject": {
            "dataset_name": name,
            "generation": resolved_generation,
            "path": dataset_path.as_posix(),
            "size_bytes": dataset_path.stat().st_size,
            "sha256": sha256_file(dataset_path),
        },
    }


def validate_dataset_manifest(value: Mapping[str, Any]) -> None:
    if value.get("schema_version") != 1:
        raise ContractError("dataset manifest schema_version must equal 1")
    subject = value.get("subject")
    if not isinstance(subject, dict):
        raise ContractError("dataset manifest subject must be an object")
    _require_nonempty_string(subject.get("dataset_name"), "subject.dataset_name")
    _require_nonempty_string(subject.get("generation"), "subject.generation")
    _require_nonempty_string(subject.get("path"), "subject.path")
    if not isinstance(subject.get("size_bytes"), int) or subject["size_bytes"] < 0:
        raise ContractError("subject.size_bytes must be a non-negative integer")
    _require_sha256(subject.get("sha256"), "subject.sha256")


def validate_evaluation_bundle(value: Mapping[str, Any]) -> None:
    if set(value) != {"accepted", "metrics", "policy_generation"}:
        raise ContractError(
            "evaluation bundle must contain exactly accepted, metrics and policy_generation"
        )
    if not isinstance(value["accepted"], bool):
        raise ContractError("evaluation.accepted must be boolean")
    _require_nonempty_string(value["policy_generation"], "evaluation.policy_generation")
    metrics = value["metrics"]
    if not isinstance(metrics, dict) or not metrics:
        raise ContractError("evaluation.metrics must be a non-empty object")
    for name, metric in metrics.items():
        _require_nonempty_string(name, "evaluation metric name")
        if isinstance(metric, bool) or not isinstance(metric, (int, float)):
            raise ContractError(f"evaluation metric {name} must be numeric")
        if metric != metric or metric in (float("inf"), float("-inf")):
            raise ContractError(f"evaluation metric {name} must be finite")


def build_candidate_manifest(
    *,
    dataset_manifest: Mapping[str, Any],
    model_path: Path,
    evaluation: Mapping[str, Any],
    source_revision: str,
) -> dict[str, Any]:
    validate_dataset_manifest(dataset_manifest)
    validate_evaluation_bundle(evaluation)
    if not model_path.is_file():
        raise ContractError(f"Model artifact does not exist or is not a file: {model_path}")

    payload = {
        "schema_version": 1,
        "dataset": {
            "name": dataset_manifest["subject"]["dataset_name"],
            "generation": dataset_manifest["subject"]["generation"],
            "sha256": dataset_manifest["subject"]["sha256"],
        },
        "model": {
            "path": model_path.as_posix(),
            "size_bytes": model_path.stat().st_size,
            "sha256": sha256_file(model_path),
        },
        "evaluation": {
            "accepted": evaluation["accepted"],
            "metrics": dict(sorted(evaluation["metrics"].items())),
            "policy_generation": evaluation["policy_generation"],
            "sha256": sha256_bytes(canonical_json_bytes(evaluation)),
        },
        "source_revision": _require_nonempty_string(source_revision, "source_revision"),
    }
    return {**payload, "candidate_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_candidate_manifest(value: Mapping[str, Any]) -> None:
    candidate_id = _require_sha256(value.get("candidate_id"), "candidate_id")
    payload = {key: item for key, item in value.items() if key != "candidate_id"}
    if sha256_bytes(canonical_json_bytes(payload)) != candidate_id:
        raise ContractError("candidate_id does not match canonical candidate payload")
    if value.get("schema_version") != 1:
        raise ContractError("candidate schema_version must equal 1")
    dataset = value.get("dataset")
    model = value.get("model")
    evaluation = value.get("evaluation")
    if not isinstance(dataset, dict) or not isinstance(model, dict) or not isinstance(evaluation, dict):
        raise ContractError("candidate dataset, model and evaluation must be objects")
    _require_sha256(dataset.get("sha256"), "dataset.sha256")
    _require_sha256(model.get("sha256"), "model.sha256")
    _require_sha256(evaluation.get("sha256"), "evaluation.sha256")
    if evaluation.get("accepted") is not True:
        raise ContractError("candidate evaluation is not accepted")
    _require_nonempty_string(evaluation.get("policy_generation"), "evaluation.policy_generation")
    _require_nonempty_string(value.get("source_revision"), "source_revision")


def promote_candidate(
    *,
    candidate: Mapping[str, Any],
    alias_state: Mapping[str, Any],
    alias: str,
    expected_current: str | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    validate_candidate_manifest(candidate)
    resolved_alias = _require_nonempty_string(alias, "alias")
    aliases = alias_state.get("aliases", {})
    if not isinstance(aliases, dict):
        raise ContractError("alias state aliases must be an object")

    actual_current = aliases.get(resolved_alias)
    if actual_current is not None:
        _require_sha256(actual_current, f"aliases.{resolved_alias}")
    if actual_current != expected_current:
        raise ContractError(
            f"stale promotion for alias {resolved_alias}: expected {expected_current!r}, "
            f"found {actual_current!r}"
        )

    candidate_id = candidate["candidate_id"]
    release_payload = {
        "schema_version": 1,
        "alias": resolved_alias,
        "previous_candidate_id": actual_current,
        "candidate_id": candidate_id,
        "dataset_sha256": candidate["dataset"]["sha256"],
        "model_sha256": candidate["model"]["sha256"],
        "evaluation_sha256": candidate["evaluation"]["sha256"],
        "policy_generation": candidate["evaluation"]["policy_generation"],
        "source_revision": candidate["source_revision"],
    }
    release = {
        **release_payload,
        "release_id": sha256_bytes(canonical_json_bytes(release_payload)),
    }
    next_aliases = dict(aliases)
    next_aliases[resolved_alias] = candidate_id
    next_state = {"schema_version": 1, "aliases": dict(sorted(next_aliases.items()))}
    return release, next_state
