from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping


class AgentContractError(ValueError):
    """Raised when an agent subject violates an authoritative local contract."""


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


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AgentContractError(f"required JSON file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AgentContractError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AgentContractError(f"expected JSON object in {path}")
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


def require_nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AgentContractError(f"{field} must be a non-empty string")
    return value.strip()


def require_sha256(value: Any, field: str) -> str:
    text = require_nonempty(value, field)
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise AgentContractError(f"{field} must be a lowercase SHA-256 digest")
    return text


def validate_canonical_id(value: Mapping[str, Any], id_field: str) -> None:
    identifier = require_sha256(value.get(id_field), id_field)
    payload = {key: item for key, item in value.items() if key != id_field}
    if sha256_bytes(canonical_json_bytes(payload)) != identifier:
        raise AgentContractError(f"{id_field} does not match canonical payload")


def require_exact_keys(value: Mapping[str, Any], expected: set[str], field: str) -> None:
    actual = set(value)
    if actual != expected:
        raise AgentContractError(
            f"{field} keys mismatch: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )
