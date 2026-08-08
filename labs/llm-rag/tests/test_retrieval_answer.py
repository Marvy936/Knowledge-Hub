from __future__ import annotations

from copy import deepcopy

import pytest

from knowledge_hub_rag.answers import build_answer_envelope, validate_answer_envelope
from knowledge_hub_rag.contracts import ContractError, canonical_json_bytes, sha256_bytes
from knowledge_hub_rag.retrieval import (
    build_grounded_context,
    build_retrieval_index,
    retrieve,
    validate_retrieval_index,
    validate_retrieval_result,
)


def _chunk(path: str, ordinal: int, heading: str, text: str, source_sha: str) -> dict[str, object]:
    payload = {
        "source_path": path,
        "source_sha256": source_sha,
        "heading_path": [heading],
        "ordinal": ordinal,
        "content_sha256": sha256_bytes(text.encode("utf-8")),
        "char_count": len(text),
    }
    return {
        **payload,
        "chunk_id": sha256_bytes(canonical_json_bytes(payload)),
        "content": text,
    }


def _manifest() -> dict[str, object]:
    chunks = [
        _chunk(
            "docs/kubernetes.md",
            0,
            "Services",
            "A Kubernetes Service exposes a stable virtual IP and DNS name for Pods. ClusterIP is internal.",
            "a" * 64,
        ),
        _chunk(
            "docs/kubernetes.md",
            1,
            "ConfigMap",
            "A ConfigMap stores non-secret configuration data for Kubernetes workloads.",
            "a" * 64,
        ),
        _chunk(
            "docs/tls.md",
            0,
            "TLS certificates",
            "TLS certificates bind public keys to identities. PKI chains certificates to trusted roots.",
            "b" * 64,
        ),
    ]
    payload = {
        "schema_version": 1,
        "corpus_snapshot_id": "c" * 64,
        "source_revision": "d" * 40,
        "chunking": {"max_chars": 1800, "min_chars": 240},
        "chunk_count": len(chunks),
        "chunks": chunks,
    }
    return {
        **payload,
        "chunk_manifest_id": sha256_bytes(canonical_json_bytes(payload)),
    }


def test_index_is_deterministic_and_semantically_rebuilt() -> None:
    manifest = _manifest()
    first = build_retrieval_index(manifest)
    second = build_retrieval_index(manifest)
    assert first == second
    validate_retrieval_index(first, manifest)

    forged = deepcopy(first)
    forged["document_count"] = 2
    with pytest.raises(ContractError, match="deterministic chunk-manifest rebuild"):
        validate_retrieval_index(forged, manifest)


def test_retrieval_ranks_relevant_chunk_and_carries_exact_citation() -> None:
    manifest = _manifest()
    index = build_retrieval_index(manifest)
    result = retrieve(
        index=index,
        manifest=manifest,
        query="How does Kubernetes Service expose pods?",
        top_k=2,
    )
    assert result["status"] == "results"
    assert result["hits"][0]["citation"]["source_path"] == "docs/kubernetes.md"
    assert result["hits"][0]["citation"]["heading_path"] == ["Services"]
    validate_retrieval_result(result, index=index, manifest=manifest)


def test_no_result_is_explicit_and_contains_no_hits() -> None:
    manifest = _manifest()
    index = build_retrieval_index(manifest)
    result = retrieve(index=index, manifest=manifest, query="quantum entanglement photon")
    assert result["status"] == "no_result"
    assert result["hit_count"] == 0
    assert result["hits"] == []


def test_query_and_result_identity_are_deterministic() -> None:
    manifest = _manifest()
    index = build_retrieval_index(manifest)
    first = retrieve(index=index, manifest=manifest, query="TLS certificates PKI", top_k=3)
    second = retrieve(index=index, manifest=manifest, query="TLS certificates PKI", top_k=3)
    assert first == second
    assert first["query"]["query_id"] == second["query"]["query_id"]
    assert first["retrieval_result_id"] == second["retrieval_result_id"]


def test_rehashed_result_with_dropped_top_hit_is_refused() -> None:
    manifest = _manifest()
    index = build_retrieval_index(manifest)
    result = retrieve(index=index, manifest=manifest, query="kubernetes service pods", top_k=3)
    forged = deepcopy(result)
    forged["hits"] = forged["hits"][1:]
    forged["hit_count"] = len(forged["hits"])
    payload = {key: value for key, value in forged.items() if key != "retrieval_result_id"}
    forged["retrieval_result_id"] = sha256_bytes(canonical_json_bytes(payload))
    with pytest.raises(ContractError, match="deterministic query/index rebuild"):
        validate_retrieval_result(forged, index=index, manifest=manifest)


def test_grounded_context_is_bounded_and_keeps_exact_citations() -> None:
    manifest = _manifest()
    index = build_retrieval_index(manifest)
    result = retrieve(
        index=index,
        manifest=manifest,
        query="kubernetes service configmap pods",
        top_k=3,
    )
    context = build_grounded_context(
        result,
        index=index,
        manifest=manifest,
        max_chars=256,
    )
    assert context["status"] in {"context", "insufficient_context"}
    allowed = [hit["citation"] for hit in result["hits"]]
    assert context["context_chars"] <= 256
    for item in context["items"]:
        assert item["citation"] in allowed


def test_answer_requires_an_exact_retrieved_citation() -> None:
    manifest = _manifest()
    index = build_retrieval_index(manifest)
    result = retrieve(index=index, manifest=manifest, query="What is a Kubernetes Service?")
    chunk_id = result["hits"][0]["citation"]["chunk_id"]
    answer = build_answer_envelope(
        retrieval_result=result,
        index=index,
        manifest=manifest,
        answer_text="It provides a stable virtual IP and DNS name.",
        cited_chunk_ids=[chunk_id],
        prompt_generation="grounded-answer-v1",
    )
    validate_answer_envelope(
        answer,
        retrieval_result=result,
        index=index,
        manifest=manifest,
    )

    with pytest.raises(ContractError, match="not present"):
        build_answer_envelope(
            retrieval_result=result,
            index=index,
            manifest=manifest,
            answer_text="Unsupported answer",
            cited_chunk_ids=["f" * 64],
            prompt_generation="grounded-answer-v1",
        )


def test_no_result_must_abstain_without_answer_or_citation() -> None:
    manifest = _manifest()
    index = build_retrieval_index(manifest)
    result = retrieve(index=index, manifest=manifest, query="quantum entanglement photon")
    answer = build_answer_envelope(
        retrieval_result=result,
        index=index,
        manifest=manifest,
        answer_text=None,
        cited_chunk_ids=[],
        prompt_generation="grounded-answer-v1",
    )
    assert answer["status"] == "abstained"
    assert answer["answer"] is None
    validate_answer_envelope(
        answer,
        retrieval_result=result,
        index=index,
        manifest=manifest,
    )

    with pytest.raises(ContractError, match="must abstain"):
        build_answer_envelope(
            retrieval_result=result,
            index=index,
            manifest=manifest,
            answer_text="Invented answer",
            cited_chunk_ids=[],
            prompt_generation="grounded-answer-v1",
        )


def test_rehashed_answer_with_modified_citation_is_refused() -> None:
    manifest = _manifest()
    index = build_retrieval_index(manifest)
    result = retrieve(index=index, manifest=manifest, query="TLS certificates PKI")
    chunk_id = result["hits"][0]["citation"]["chunk_id"]
    answer = build_answer_envelope(
        retrieval_result=result,
        index=index,
        manifest=manifest,
        answer_text="Certificates bind public keys to identities.",
        cited_chunk_ids=[chunk_id],
        prompt_generation="grounded-answer-v1",
    )
    forged = deepcopy(answer)
    forged["citations"][0]["source_path"] = "docs/other.md"
    payload = {key: value for key, value in forged.items() if key != "answer_id"}
    forged["answer_id"] = sha256_bytes(canonical_json_bytes(payload))
    with pytest.raises(ContractError, match="exact retrieved citation"):
        validate_answer_envelope(
            forged,
            retrieval_result=result,
            index=index,
            manifest=manifest,
        )
