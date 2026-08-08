from __future__ import annotations

import re
from typing import Any, Mapping

from .answers import build_answer_envelope, validate_answer_envelope
from .contracts import ContractError, canonical_json_bytes, sha256_bytes
from .retrieval import (
    build_grounded_context,
    tokenize,
    validate_retrieval_result,
)
from .runtime_config import validate_runtime_config
from .security import scan_prompt_injection

ADAPTER_SCHEMA_VERSION = 1
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def _extract_sentence(content: str, query_tokens: list[str], max_chars: int) -> str:
    candidates = [item.strip() for item in SENTENCE_RE.split(content) if item.strip()]
    if not candidates:
        raise ContractError("safe retrieved chunk produced no extractive sentence")
    query = set(query_tokens)
    ranked: list[tuple[int, int, str]] = []
    for ordinal, sentence in enumerate(candidates):
        overlap = len(query.intersection(tokenize(sentence)))
        ranked.append((-overlap, ordinal, sentence))
    ranked.sort()
    sentence = ranked[0][2]
    answer = sentence[:max_chars].strip()
    if not answer:
        raise ContractError("extractive answer is empty")
    if answer not in content:
        raise ContractError("extractive answer must remain an exact source substring")
    return answer


def run_offline_adapter(
    *,
    retrieval_result: Mapping[str, Any],
    index: Mapping[str, Any],
    manifest: Mapping[str, Any],
    runtime_config: Mapping[str, Any],
) -> dict[str, Any]:
    validate_runtime_config(runtime_config)
    validate_retrieval_result(retrieval_result, index=index, manifest=manifest)
    context = build_grounded_context(
        retrieval_result,
        index=index,
        manifest=manifest,
        max_chars=runtime_config["context"]["max_chars"],
    )

    query = retrieval_result["query"]["query"]
    query_security = scan_prompt_injection(
        text=query,
        subject_type="query",
        subject_id=retrieval_result["query"]["query_id"],
    )
    hit_security: list[dict[str, Any]] = []

    if query_security["classification"] == "prompt_injection_detected":
        answer = build_answer_envelope(
            retrieval_result=retrieval_result,
            index=index,
            manifest=manifest,
            answer_text=None,
            cited_chunk_ids=[],
            prompt_generation=runtime_config["generation"],
            abstention_reason="direct_prompt_injection",
        )
    elif retrieval_result["status"] == "no_result":
        answer = build_answer_envelope(
            retrieval_result=retrieval_result,
            index=index,
            manifest=manifest,
            answer_text=None,
            cited_chunk_ids=[],
            prompt_generation=runtime_config["generation"],
        )
    elif context["status"] != "context":
        answer = build_answer_envelope(
            retrieval_result=retrieval_result,
            index=index,
            manifest=manifest,
            answer_text=None,
            cited_chunk_ids=[],
            prompt_generation=runtime_config["generation"],
            abstention_reason="no_safe_context",
        )
    else:
        safe_item: Mapping[str, Any] | None = None
        for item in context["items"]:
            evidence = scan_prompt_injection(
                text=item["content"],
                subject_type="retrieved_chunk",
                subject_id=item["citation"]["chunk_id"],
            )
            hit_security.append(evidence)
            if evidence["classification"] == "clean" and safe_item is None:
                safe_item = item
        if safe_item is None:
            answer = build_answer_envelope(
                retrieval_result=retrieval_result,
                index=index,
                manifest=manifest,
                answer_text=None,
                cited_chunk_ids=[],
                prompt_generation=runtime_config["generation"],
                abstention_reason="indirect_prompt_injection",
            )
        else:
            text = _extract_sentence(
                safe_item["content"],
                retrieval_result["query"]["query_tokens"],
                int(runtime_config["answer"]["max_chars"]),
            )
            answer = build_answer_envelope(
                retrieval_result=retrieval_result,
                index=index,
                manifest=manifest,
                answer_text=text,
                cited_chunk_ids=[safe_item["citation"]["chunk_id"]],
                prompt_generation=runtime_config["generation"],
            )

    validate_answer_envelope(
        answer,
        retrieval_result=retrieval_result,
        index=index,
        manifest=manifest,
    )
    payload = {
        "schema_version": ADAPTER_SCHEMA_VERSION,
        "runtime_config_id": runtime_config["runtime_config_id"],
        "retrieval_result_id": retrieval_result["retrieval_result_id"],
        "context_id": context["context_id"],
        "adapter_generation": runtime_config["adapter_generation"],
        "query_security": query_security,
        "hit_security": hit_security,
        "answer": answer,
    }
    return {**payload, "adapter_result_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_offline_adapter_result(
    value: Mapping[str, Any],
    *,
    retrieval_result: Mapping[str, Any],
    index: Mapping[str, Any],
    manifest: Mapping[str, Any],
    runtime_config: Mapping[str, Any],
) -> None:
    expected = run_offline_adapter(
        retrieval_result=retrieval_result,
        index=index,
        manifest=manifest,
        runtime_config=runtime_config,
    )
    if dict(value) != expected:
        raise ContractError("offline adapter result does not match deterministic rebuild")
