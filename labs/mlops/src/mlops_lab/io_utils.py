"""Canonical JSON digests and atomic evidence writes."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .errors import EvidenceIntegrityError

DIGEST_FIELD = "evidence_sha256"


def canonical_json(payload: dict[str, Any]) -> bytes:
    without_digest = {key: value for key, value in payload.items() if key != DIGEST_FIELD}
    return json.dumps(
        without_digest,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def evidence_digest(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload)).hexdigest()


def bind_digest(payload: dict[str, Any]) -> dict[str, Any]:
    bound = dict(payload)
    bound[DIGEST_FIELD] = evidence_digest(bound)
    return bound


def verify_digest(payload: dict[str, Any]) -> None:
    actual = payload.get(DIGEST_FIELD)
    expected = evidence_digest(payload)
    if actual != expected:
        raise EvidenceIntegrityError(
            f"evidence digest mismatch: expected {expected}, got {actual}"
        )


def write_json_atomic(path: Path, payload: dict[str, Any], *, bind: bool = True) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    final_payload = bind_digest(payload) if bind else dict(payload)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(final_payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)
    return final_payload


def read_json_object(path: Path, *, verify: bool = True) -> dict[str, Any]:
    if not path.is_file():
        raise EvidenceIntegrityError(f"evidence file does not exist: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise EvidenceIntegrityError(f"{path} must contain one JSON object")
    if verify:
        verify_digest(payload)
    return payload
