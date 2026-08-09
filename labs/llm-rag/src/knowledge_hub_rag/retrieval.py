from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from typing import Any, Mapping

from .contracts import ContractError, canonical_json_bytes, sha256_bytes, validate_chunk_manifest

RETRIEVAL_SCHEMA_VERSION = 1
TOKENIZER_GENERATION = "unicode-word-v1"
TOKEN_RE = re.compile(r"[^\W_]+(?:[-'][^\W_]+)*", re.UNICODE)
DEFAULT_K1 = 1.2
DEFAULT_B = 0.75
RETRIEVAL_ALGORITHM = "bm25-source-path-v2"
SOURCE_PATH_BOOST = 1.0


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value.strip()


def _require_sha256(value: Any, field: str) -> str:
    text = _require_nonempty_string(value, field)
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise ContractError(f"{field} must be a lowercase SHA-256 digest")
    return text


def tokenize(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", _require_nonempty_string(text, "text")).casefold()
    return TOKEN_RE.findall(normalized)


def _canonical_index_payload(manifest: Mapping[str, Any]) -> dict[str, Any]:
    validate_chunk_manifest(manifest)
    documents: list[dict[str, Any]] = []
    document_frequencies: Counter[str] = Counter()
    total_length = 0
    for chunk in manifest["chunks"]:
        tokens = tokenize(chunk["content"])
        frequencies = Counter(tokens)
        document_frequencies.update(frequencies.keys())
        total_length += len(tokens)
        documents.append(
            {
                "chunk_id": chunk["chunk_id"],
                "source_path": chunk["source_path"],
                "source_sha256": chunk["source_sha256"],
                "heading_path": list(chunk["heading_path"]),
                "content_sha256": chunk["content_sha256"],
                "token_count": len(tokens),
                "term_frequencies": dict(sorted(frequencies.items())),
            }
        )
    if not documents:
        raise ContractError("retrieval index requires at least one chunk")
    return {
        "schema_version": RETRIEVAL_SCHEMA_VERSION,
        "chunk_manifest_id": manifest["chunk_manifest_id"],
        "corpus_snapshot_id": manifest["corpus_snapshot_id"],
        "source_revision": manifest["source_revision"],
        "tokenizer_generation": TOKENIZER_GENERATION,
        "retrieval_generation": RETRIEVAL_ALGORITHM,
        "document_count": len(documents),
        "average_document_tokens": round(total_length / len(documents), 12),
        "document_frequencies": dict(sorted(document_frequencies.items())),
        "documents": documents,
    }


def build_retrieval_index(manifest: Mapping[str, Any]) -> dict[str, Any]:
    payload = _canonical_index_payload(manifest)
    return {**payload, "retrieval_index_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_retrieval_index(index: Mapping[str, Any], manifest: Mapping[str, Any]) -> None:
    expected = build_retrieval_index(manifest)
    if dict(index) != expected:
        raise ContractError("retrieval index does not match deterministic chunk-manifest rebuild")


def _query_payload(*, query: str, index_id: str, top_k: int, min_score: float) -> dict[str, Any]:
    resolved = _require_nonempty_string(query, "query")
    tokens = tokenize(resolved)
    if not tokens:
        raise ContractError("query produced no lexical tokens")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1 or top_k > 100:
        raise ContractError("top_k must be an integer between 1 and 100")
    if isinstance(min_score, bool) or not isinstance(min_score, (int, float)) or not math.isfinite(float(min_score)) or float(min_score) < 0:
        raise ContractError("min_score must be a finite non-negative number")
    payload = {
        "query": resolved,
        "normalized_query": " ".join(tokens),
        "query_tokens": tokens,
        "retrieval_index_id": _require_sha256(index_id, "retrieval_index_id"),
        "top_k": top_k,
        "min_score": float(min_score),
    }
    return {**payload, "query_id": sha256_bytes(canonical_json_bytes(payload))}


def _score_document(*, query_tokens: list[str], document: Mapping[str, Any], index: Mapping[str, Any], k1: float, b: float) -> float:
    n = int(index["document_count"])
    avgdl = float(index["average_document_tokens"])
    dl = int(document["token_count"])
    frequencies = document["term_frequencies"]
    dfs = index["document_frequencies"]
    score = 0.0
    for term in sorted(set(query_tokens)):
        tf = int(frequencies.get(term, 0))
        if tf == 0:
            continue
        df = int(dfs.get(term, 0))
        if df < 1 or df > n:
            raise ContractError("retrieval index document frequency is invalid")
        idf = math.log(1.0 + (n - df + 0.5) / (df + 0.5))
        norm = tf + k1 * (1.0 - b + b * (dl / avgdl if avgdl else 0.0))
        score += idf * ((tf * (k1 + 1.0)) / norm)
    return round(score, 12)


def _source_path_bonus(*, query_tokens: list[str], document: Mapping[str, Any], index: Mapping[str, Any]) -> float:
    n = int(index["document_count"])
    dfs = index["document_frequencies"]
    source_path = _require_nonempty_string(document.get("source_path"), "document.source_path")
    normalized_path = re.sub(r"[/._-]+", " ", source_path)
    path_tokens = set(tokenize(normalized_path))
    bonus = 0.0
    for term in sorted(set(query_tokens) & path_tokens):
        df = int(dfs.get(term, 0))
        if df < 1:
            idf = math.log(1.0 + (n - 0.5) / 0.5)
        elif df <= n:
            idf = math.log(1.0 + (n - df + 0.5) / (df + 0.5))
        else:
            raise ContractError("retrieval index document frequency is invalid")
        bonus += idf * SOURCE_PATH_BOOST
    return round(bonus, 12)


def retrieve(
    *,
    index: Mapping[str, Any],
    manifest: Mapping[str, Any],
    query: str,
    top_k: int = 5,
    min_score: float = 0.01,
    k1: float = DEFAULT_K1,
    b: float = DEFAULT_B,
) -> dict[str, Any]:
    validate_retrieval_index(index, manifest)
    if not (0.0 < k1 <= 10.0):
        raise ContractError("k1 must be greater than 0 and at most 10")
    if not (0.0 <= b <= 1.0):
        raise ContractError("b must be between 0 and 1")
    q = _query_payload(query=query, index_id=index["retrieval_index_id"], top_k=top_k, min_score=min_score)
    chunks_by_id = {chunk["chunk_id"]: chunk for chunk in manifest["chunks"]}
    scored: list[tuple[float, str, Mapping[str, Any]]] = []
    for document in index["documents"]:
        content_score = _score_document(query_tokens=q["query_tokens"], document=document, index=index, k1=k1, b=b)
        score = round(
            content_score
            + _source_path_bonus(
                query_tokens=q["query_tokens"],
                document=document,
                index=index,
            ),
            12,
        )
        if score >= float(min_score) and score > 0.0:
            scored.append((score, document["chunk_id"], document))
    scored.sort(key=lambda item: (-item[0], item[1]))
    hits: list[dict[str, Any]] = []
    for rank, (score, chunk_id, document) in enumerate(scored[:top_k], start=1):
        chunk = chunks_by_id.get(chunk_id)
        if chunk is None:
            raise ContractError("retrieval index references an unknown chunk")
        citation_payload = {
            "chunk_id": chunk_id,
            "source_path": document["source_path"],
            "source_sha256": document["source_sha256"],
            "heading_path": list(document["heading_path"]),
            "content_sha256": document["content_sha256"],
        }
        hits.append(
            {
                "rank": rank,
                "score": score,
                "citation": {
                    **citation_payload,
                    "citation_id": sha256_bytes(canonical_json_bytes(citation_payload)),
                },
                "content": chunk["content"],
            }
        )
    payload = {
        "schema_version": RETRIEVAL_SCHEMA_VERSION,
        "query": q,
        "chunk_manifest_id": manifest["chunk_manifest_id"],
        "corpus_snapshot_id": manifest["corpus_snapshot_id"],
        "source_revision": manifest["source_revision"],
        "retrieval_config": {"algorithm": RETRIEVAL_ALGORITHM, "k1": k1, "b": b},
        "status": "results" if hits else "no_result",
        "hit_count": len(hits),
        "hits": hits,
    }
    return {**payload, "retrieval_result_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_retrieval_result(result: Mapping[str, Any], *, index: Mapping[str, Any], manifest: Mapping[str, Any]) -> None:
    query = result.get("query") if isinstance(result, Mapping) else None
    config = result.get("retrieval_config") if isinstance(result, Mapping) else None
    if not isinstance(query, dict) or not isinstance(config, dict):
        raise ContractError("retrieval result query/config is invalid")
    if config.get("algorithm") != RETRIEVAL_ALGORITHM:
        raise ContractError("retrieval result algorithm generation mismatch")
    expected = retrieve(
        index=index,
        manifest=manifest,
        query=query.get("query"),
        top_k=query.get("top_k"),
        min_score=query.get("min_score"),
        k1=config.get("k1"),
        b=config.get("b"),
    )
    if dict(result) != expected:
        raise ContractError("retrieval result does not match deterministic query/index rebuild")


def build_grounded_context(
    result: Mapping[str, Any],
    *,
    index: Mapping[str, Any],
    manifest: Mapping[str, Any],
    max_chars: int = 6000,
) -> dict[str, Any]:
    validate_retrieval_result(result, index=index, manifest=manifest)
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or max_chars < 256:
        raise ContractError("context max_chars must be at least 256")
    if result.get("status") == "no_result":
        payload = {
            "schema_version": RETRIEVAL_SCHEMA_VERSION,
            "retrieval_result_id": _require_sha256(result.get("retrieval_result_id"), "retrieval_result_id"),
            "status": "no_result",
            "max_chars": max_chars,
            "context_chars": 0,
            "items": [],
        }
        return {**payload, "context_id": sha256_bytes(canonical_json_bytes(payload))}
    if result.get("status") != "results" or not isinstance(result.get("hits"), list):
        raise ContractError("retrieval result status/hits are invalid")
    items: list[dict[str, Any]] = []
    used = 0
    for hit in result["hits"]:
        content = _require_nonempty_string(hit.get("content"), "hit.content")
        if used + len(content) > max_chars:
            continue
        items.append({"citation": dict(hit["citation"]), "content": content})
        used += len(content)
    status = "context" if items else "insufficient_context"
    payload = {
        "schema_version": RETRIEVAL_SCHEMA_VERSION,
        "retrieval_result_id": _require_sha256(result.get("retrieval_result_id"), "retrieval_result_id"),
        "status": status,
        "max_chars": max_chars,
        "context_chars": used,
        "items": items,
    }
    return {**payload, "context_id": sha256_bytes(canonical_json_bytes(payload))}
