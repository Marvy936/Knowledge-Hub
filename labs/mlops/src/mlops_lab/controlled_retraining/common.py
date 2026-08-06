from __future__ import annotations

from typing import Any, Mapping

from ..contracts import ContractError, canonical_json_bytes, sha256_bytes

EXECUTOR_SCHEMA_VERSION = 1
PHASES = {
    "planned",
    "training_started",
    "training_completed",
    "candidate_recorded",
    "registry_recorded",
    "promotion_started",
    "completed",
    "failed",
}
ARTIFACT_FIELDS = (
    "training_manifest_sha256",
    "model_sha256",
    "evaluation_file_sha256",
    "candidate_id",
    "registry_evidence_id",
    "registry_version",
    "release_id",
    "alias_state_file_sha256",
)


def require_exact_keys(
    value: Mapping[str, Any], expected: set[str], field: str
) -> None:
    actual = set(value)
    if actual != expected:
        raise ContractError(
            f"{field} keys mismatch: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )


def require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value.strip()


def require_sha256(value: Any, field: str) -> str:
    text = require_nonempty_string(value, field)
    if len(text) != 64 or any(
        character not in "0123456789abcdef" for character in text
    ):
        raise ContractError(f"{field} must be a lowercase SHA-256 digest")
    return text


def validate_canonical_id(value: Mapping[str, Any], id_field: str) -> None:
    identifier = require_sha256(value.get(id_field), id_field)
    payload = {key: item for key, item in value.items() if key != id_field}
    if sha256_bytes(canonical_json_bytes(payload)) != identifier:
        raise ContractError(f"{id_field} does not match canonical payload")
