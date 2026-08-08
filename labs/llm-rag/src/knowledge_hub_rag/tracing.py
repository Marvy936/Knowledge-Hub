from __future__ import annotations

import math
from typing import Any, Mapping

from .contracts import ContractError, canonical_json_bytes, sha256_bytes
from .retrieval import tokenize

TRACE_SCHEMA_VERSION = 1


def build_trace(
    *,
    runtime_config: Mapping[str, Any],
    retrieval_result: Mapping[str, Any],
    adapter_result: Mapping[str, Any],
    context: Mapping[str, Any],
    latency_ms: float,
) -> dict[str, Any]:
    if isinstance(latency_ms, bool) or not isinstance(latency_ms, (int, float)):
        raise ContractError("latency_ms must be numeric")
    latency = float(latency_ms)
    if not math.isfinite(latency) or latency < 0:
        raise ContractError("latency_ms must be finite and non-negative")
    if adapter_result.get("retrieval_result_id") != retrieval_result.get("retrieval_result_id"):
        raise ContractError("adapter result belongs to another retrieval result")
    answer = adapter_result.get("answer")
    if not isinstance(answer, dict):
        raise ContractError("adapter result answer is invalid")
    query = retrieval_result.get("query", {}).get("query", "")
    answer_text = answer.get("answer") or ""
    retrieved_chars = sum(len(hit.get("content", "")) for hit in retrieval_result.get("hits", []))
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "runtime_config_id": runtime_config.get("runtime_config_id"),
        "query_id": retrieval_result.get("query", {}).get("query_id"),
        "retrieval_result_id": retrieval_result.get("retrieval_result_id"),
        "context_id": context.get("context_id"),
        "adapter_result_id": adapter_result.get("adapter_result_id"),
        "answer_id": answer.get("answer_id"),
        "status": answer.get("status"),
        "latency_ms": round(latency, 6),
        "counters": {
            "query_token_equivalents": len(tokenize(query)),
            "retrieved_chunk_count": retrieval_result.get("hit_count"),
            "retrieved_chars": retrieved_chars,
            "context_chars": context.get("context_chars"),
            "answer_token_equivalents": 0 if not answer_text else len(tokenize(answer_text)),
            "citation_count": len(answer.get("citations", [])),
        },
        "cost_equivalent": {
            "unit": "lexical_token_equivalent",
            "input_units": len(tokenize(query)) + sum(len(tokenize(hit.get("content", ""))) for hit in retrieval_result.get("hits", [])),
            "output_units": 0 if not answer_text else len(tokenize(answer_text)),
            "monetary_cost": None,
        },
    }
    return {**payload, "trace_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_trace(value: Mapping[str, Any], **kwargs: Any) -> None:
    expected = build_trace(**kwargs)
    if dict(value) != expected:
        raise ContractError("trace does not match deterministic evidence reconstruction")
