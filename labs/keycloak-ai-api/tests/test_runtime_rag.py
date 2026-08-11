from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("knowledge_hub_rag")

from keycloak_ai_api import runtime_rag


def test_runtime_rag_requires_exact_subject_sha() -> None:
    assert runtime_rag._require_subject_sha("a" * 40) == "a" * 40
    with pytest.raises(runtime_rag.RuntimeRagError, match="40-character"):
        runtime_rag._require_subject_sha("A" * 40)
    with pytest.raises(runtime_rag.RuntimeRagError, match="40-character"):
        runtime_rag._require_subject_sha("a" * 39)


def test_runtime_rag_derives_query_only_from_chunk_content() -> None:
    chunk = {
        "chunk_id": "a" * 64,
        "source_path": "docs/example.md",
        "content": "Exact issuer audience scope and client role validation",
    }
    query = runtime_rag._query_from_chunk(chunk)
    assert query.startswith("Exact issuer audience")
    assert "client" in query

    with pytest.raises(runtime_rag.RuntimeRagError, match="queryable text"):
        runtime_rag._query_from_chunk({"chunk_id": "b" * 64})


def test_runtime_rag_requires_fresh_runtime_root(tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime"
    (runtime_root / "rag").mkdir(parents=True)
    with pytest.raises(runtime_rag.RuntimeRagError, match="must be fresh"):
        runtime_rag.build_live_rag_bundle(
            repo_root=tmp_path,
            runtime_root=runtime_root,
            subject_sha="a" * 40,
        )
