from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_clean_checkout_runtime.py"
SPEC = importlib.util.spec_from_file_location("run_clean_checkout_runtime_v2", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(driver)


def test_query_from_chunks_skips_identity_only_chunk() -> None:
    query = driver._query_from_chunks(
        [
            {"chunk_id": "a" * 64},
            {
                "chunk_id": "b" * 64,
                "text": "Exact prompt release binds runtime config and evaluation evidence.",
            },
        ]
    )
    assert query.startswith("Exact prompt release")
    assert "runtime" in query


def test_query_from_chunks_refuses_when_no_chunk_is_queryable() -> None:
    with pytest.raises(driver.RagRuntimeError, match="any canonical corpus chunk"):
        driver._query_from_chunks(
            [
                {"chunk_id": "a" * 64},
                {"chunk_id": "b" * 64},
            ]
        )
