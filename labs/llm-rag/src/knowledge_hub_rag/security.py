from __future__ import annotations

import re
import unicodedata
from typing import Any

from .contracts import ContractError, canonical_json_bytes, sha256_bytes

SECURITY_SCHEMA_VERSION = 1
SECURITY_GENERATION = "prompt-injection-policy-v1"
RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_previous_instructions", re.compile(r"\bignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions?\b", re.I)),
    ("system_prompt_request", re.compile(r"\b(?:reveal|show|print|repeat|expose)\s+(?:the\s+)?system\s+prompt\b", re.I)),
    ("developer_instruction_request", re.compile(r"\b(?:reveal|show|print|repeat|expose)\s+(?:the\s+)?developer\s+(?:message|instructions?)\b", re.I)),
    ("secret_exfiltration", re.compile(r"\b(?:reveal|show|print|exfiltrate|leak)\s+(?:the\s+)?(?:secret|token|credential|password)s?\b", re.I)),
    ("instruction_override", re.compile(r"\byou\s+are\s+now\b|\bnew\s+instructions?\s*:", re.I)),
    ("tool_execution_instruction", re.compile(r"\b(?:execute|run|call)\s+(?:this\s+)?(?:command|tool|function)\b", re.I)),
)


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value.strip()


def scan_prompt_injection(
    *, text: str, subject_type: str, subject_id: str
) -> dict[str, Any]:
    resolved = _require_nonempty_string(text, "security text")
    subject_type = _require_nonempty_string(subject_type, "subject_type")
    subject_id = _require_nonempty_string(subject_id, "subject_id")
    normalized = unicodedata.normalize("NFKC", resolved)
    matched = sorted(name for name, pattern in RULES if pattern.search(normalized))
    payload = {
        "schema_version": SECURITY_SCHEMA_VERSION,
        "security_generation": SECURITY_GENERATION,
        "subject_type": subject_type,
        "subject_id": subject_id,
        "text_sha256": sha256_bytes(resolved.encode("utf-8")),
        "classification": "prompt_injection_detected" if matched else "clean",
        "matched_rules": matched,
    }
    return {**payload, "security_evidence_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_security_evidence(value: dict[str, Any], *, text: str) -> None:
    expected = scan_prompt_injection(
        text=text,
        subject_type=value.get("subject_type"),
        subject_id=value.get("subject_id"),
    )
    if value != expected:
        raise ContractError("security evidence does not match deterministic policy scan")
