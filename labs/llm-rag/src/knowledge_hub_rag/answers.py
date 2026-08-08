from __future__ import annotations

from typing import Any, Iterable, Mapping

from .contracts import ContractError, canonical_json_bytes, sha256_bytes
from .retrieval import RETRIEVAL_SCHEMA_VERSION, validate_retrieval_result

POLICY_ABSTENTION_REASONS = {
    "direct_prompt_injection",
    "indirect_prompt_injection",
    "no_safe_context",
}
ALL_ABSTENTION_REASONS = {"retrieval_no_result", *POLICY_ABSTENTION_REASONS}


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value.strip()


def _require_sha256(value: Any, field: str) -> str:
    text = _require_nonempty_string(value, field)
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise ContractError(f"{field} must be a lowercase SHA-256 digest")
    return text


def build_answer_envelope(
    *,
    retrieval_result: Mapping[str, Any],
    index: Mapping[str, Any],
    manifest: Mapping[str, Any],
    answer_text: str | None,
    cited_chunk_ids: Iterable[str],
    prompt_generation: str,
    abstention_reason: str | None = None,
) -> dict[str, Any]:
    validate_retrieval_result(retrieval_result, index=index, manifest=manifest)
    retrieval_id = _require_sha256(
        retrieval_result.get("retrieval_result_id"), "retrieval_result_id"
    )
    prompt = _require_nonempty_string(prompt_generation, "prompt_generation")
    status = retrieval_result.get("status")
    cited = list(cited_chunk_ids)
    if len(cited) != len(set(cited)):
        raise ContractError("cited_chunk_ids must be unique")

    hits = retrieval_result.get("hits")
    if not isinstance(hits, list):
        raise ContractError("retrieval result hits must be a list")
    hits_by_id = {
        hit["citation"]["chunk_id"]: hit
        for hit in hits
        if isinstance(hit, dict)
        and isinstance(hit.get("citation"), dict)
        and isinstance(hit["citation"].get("chunk_id"), str)
    }

    if status == "no_result":
        reason = abstention_reason or "retrieval_no_result"
        if reason not in ALL_ABSTENTION_REASONS or answer_text is not None or cited:
            raise ContractError("no_result retrieval must abstain without answer or citations")
        envelope_status = "abstained"
        answer = None
        citations: list[dict[str, Any]] = []
    elif status == "results" and abstention_reason is not None:
        if abstention_reason not in POLICY_ABSTENTION_REASONS:
            raise ContractError("unsupported policy abstention reason")
        if answer_text is not None or cited:
            raise ContractError("policy abstention must not contain answer text or citations")
        envelope_status = "abstained"
        answer = None
        citations = []
        reason = abstention_reason
    elif status == "results":
        answer = _require_nonempty_string(answer_text, "answer_text")
        if not cited:
            raise ContractError("grounded answer requires at least one retrieved citation")
        citations = []
        for chunk_id in cited:
            if chunk_id not in hits_by_id:
                raise ContractError("answer citation was not present in retrieval results")
            citations.append(dict(hits_by_id[chunk_id]["citation"]))
        envelope_status = "answered"
        reason = None
    else:
        raise ContractError("unsupported retrieval status for answer envelope")

    payload = {
        "schema_version": RETRIEVAL_SCHEMA_VERSION,
        "retrieval_result_id": retrieval_id,
        "query_id": _require_sha256(
            retrieval_result.get("query", {}).get("query_id"), "query_id"
        ),
        "prompt_generation": prompt,
        "status": envelope_status,
        "answer": answer,
        "abstention_reason": reason,
        "citations": citations,
    }
    return {**payload, "answer_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_answer_envelope(
    value: Mapping[str, Any],
    *,
    retrieval_result: Mapping[str, Any],
    index: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> None:
    validate_retrieval_result(retrieval_result, index=index, manifest=manifest)
    expected_keys = {
        "schema_version",
        "retrieval_result_id",
        "query_id",
        "prompt_generation",
        "status",
        "answer",
        "abstention_reason",
        "citations",
        "answer_id",
    }
    if set(value) != expected_keys:
        raise ContractError("answer envelope keys mismatch")
    if value.get("schema_version") != RETRIEVAL_SCHEMA_VERSION:
        raise ContractError("answer envelope schema_version must equal 1")
    if value.get("retrieval_result_id") != retrieval_result.get("retrieval_result_id"):
        raise ContractError("answer belongs to another retrieval result")
    if value.get("query_id") != retrieval_result.get("query", {}).get("query_id"):
        raise ContractError("answer belongs to another query")
    _require_nonempty_string(value.get("prompt_generation"), "prompt_generation")
    citations = value.get("citations")
    if not isinstance(citations, list):
        raise ContractError("answer citations must be a list")

    if value.get("status") == "abstained":
        reason = value.get("abstention_reason")
        allowed = (
            ALL_ABSTENTION_REASONS
            if retrieval_result.get("status") == "no_result"
            else POLICY_ABSTENTION_REASONS
        )
        if value.get("answer") is not None or reason not in allowed or citations:
            raise ContractError("abstention envelope is invalid")
    elif retrieval_result.get("status") == "results":
        if value.get("status") != "answered":
            raise ContractError("retrieval results require answered or policy-abstained status")
        _require_nonempty_string(value.get("answer"), "answer")
        if value.get("abstention_reason") is not None:
            raise ContractError("answered envelope must not carry abstention reason")
        if not citations:
            raise ContractError("answered envelope requires citations")
        allowed = {
            hit["citation"]["chunk_id"]: hit["citation"]
            for hit in retrieval_result["hits"]
        }
        seen: set[str] = set()
        for citation in citations:
            if not isinstance(citation, dict):
                raise ContractError("citation must be an object")
            chunk_id = citation.get("chunk_id")
            if chunk_id in seen:
                raise ContractError("answer citations must be unique")
            seen.add(chunk_id)
            if chunk_id not in allowed or citation != allowed[chunk_id]:
                raise ContractError("answer citation is not an exact retrieved citation")
    else:
        raise ContractError("unsupported retrieval/answer status combination")

    answer_id = _require_sha256(value.get("answer_id"), "answer_id")
    payload = {key: item for key, item in value.items() if key != "answer_id"}
    if sha256_bytes(canonical_json_bytes(payload)) != answer_id:
        raise ContractError("answer_id does not match canonical answer payload")
