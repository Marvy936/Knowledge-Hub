from __future__ import annotations

import math
from typing import Any, Mapping

from .contracts import ContractError, canonical_json_bytes, sha256_bytes
from .offline_adapter import validate_offline_adapter_result
from .retrieval import (
    build_grounded_context,
    tokenize,
    validate_retrieval_result,
)
from .runtime_config import validate_runtime_config

TRACE_SCHEMA_VERSION = 1


def build_trace(
    *,
    runtime_config: Mapping[str, Any],
    retrieval_result: Mapping[str, Any],
    adapter_result: Mapping[str, Any],
    context: Mapping[str, Any],
    index: Mapping[str, Any],
    manifest: Mapping[str, Any],
    latency_ms: float,
) -> dict[str, Any]:
    validate_runtime_config(runtime_config)
    validate_retrieval_result(retrieval_result, index=index, manifest=manifest)
    validate_offline_adapter_result(
        adapter_result,
        retrieval_result=retrieval_result,
        index=index,
        manifest=manifest,
        runtime_config=runtime_config,
    )
    if not isinstance(context, dict):
        raise ContractError("context must be an object")
    expected_context = build_grounded_context(
        retrieval_result,
        index=index,
        manifest=manifest,
        max_chars=context.get("max_chars"),
    )
    if context != expected_context:
        raise ContractError("context does not match deterministic bounded-context rebuild")

    if isinstance(latency_ms, bool) or not isinstance(latency_ms, (int, float)):
        raise ContractError("latency_ms must be numeric")
    latency = float(latency_ms)
    if not math.isfinite(latency) or latency < 0:
        raise ContractError("latency_ms must be finite and non-negative")
    answer = adapter_result.get("answer")
    if not isinstance(answer, dict):
        raise ContractError("adapter result answer is invalid")
    query = retrieval_result["query"]["query"]
    answer_text = answer.get("answer") or ""
    retrieved_chars = sum(
        len(hit.get("content", "")) for hit in retrieval_result.get("hits", [])
    )
    retrieved_token_units = sum(
        len(tokenize(hit.get("content", "")))
        for hit in retrieval_result.get("hits", [])
    )
    query_token_units = len(tokenize(query))
    output_token_units = 0 if not answer_text else len(tokenize(answer_text))
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "runtime_config_id": runtime_config["runtime_config_id"],
        "query_id": retrieval_result["query"]["query_id"],
        "retrieval_result_id": retrieval_result["retrieval_result_id"],
        "context_id": context["context_id"],
        "adapter_result_id": adapter_result["adapter_result_id"],
        "answer_id": answer["answer_id"],
        "status": answer["status"],
        "latency_ms": round(latency, 6),
        "counters": {
            "query_token_equivalents": query_token_units,
            "retrieved_chunk_count": retrieval_result["hit_count"],
            "retrieved_chars": retrieved_chars,
            "context_chars": context["context_chars"],
            "answer_token_equivalents": output_token_units,
            "citation_count": len(answer.get("citations", [])),
        },
        "cost_equivalent": {
            "unit": "lexical_token_equivalent",
            "input_units": query_token_units + retrieved_token_units,
            "output_units": output_token_units,
            "monetary_cost": None,
        },
    }
    return {**payload, "trace_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_trace(value: Mapping[str, Any], **kwargs: Any) -> None:
    expected = build_trace(**kwargs)
    if dict(value) != expected:
        raise ContractError("trace does not match deterministic evidence reconstruction")
