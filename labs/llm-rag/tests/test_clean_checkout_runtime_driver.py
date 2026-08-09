from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_clean_checkout_runtime.py"
SPEC = importlib.util.spec_from_file_location("run_clean_checkout_runtime", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(driver)


def test_subject_sha_requires_exact_lowercase_git_sha1() -> None:
    assert driver._require_git_sha("a" * 40) == "a" * 40
    with pytest.raises(driver.RagRuntimeError, match="40-character"):
        driver._require_git_sha("a" * 39)
    with pytest.raises(driver.RagRuntimeError, match="40-character"):
        driver._require_git_sha("A" * 40)


def test_chunk_discovery_is_canonical_and_deduplicated() -> None:
    first = {"chunk_id": "a" * 64, "text": "Kubernetes readiness probe behavior"}
    second = {"chunk_id": "b" * 64, "text": "MLflow exact Registry version"}
    manifest = {
        "files": [
            {"chunks": [second, first]},
            {"nested_copy": first},
        ]
    }

    chunks = driver._chunk_records(manifest)
    assert [item["chunk_id"] for item in chunks] == ["a" * 64, "b" * 64]


def test_positive_query_is_derived_from_real_chunk_text() -> None:
    query = driver._query_from_chunk(
        {
            "chunk_id": "a" * 64,
            "text": "Exact Registry version and immutable deployment identity are required.",
        }
    )
    assert query.startswith("Exact Registry version")
    assert "immutable" in query


def test_query_derivation_refuses_identity_only_chunk() -> None:
    with pytest.raises(driver.RagRuntimeError, match="cannot derive"):
        driver._query_from_chunk({"chunk_id": "a" * 64})


def test_citation_chunk_ids_read_only_canonical_chunk_ids() -> None:
    result = {
        "citations": [
            {"chunk_id": "a" * 64, "source": "docs/a.md"},
            {"nested": {"chunk_id": "b" * 64}},
            {"chunk_id": "not-a-sha"},
        ]
    }
    assert driver._citation_chunk_ids(result) == {
        "a" * 64,
        "b" * 64,
        "not-a-sha",
    }


def test_recursive_exact_containment_does_not_use_substring_matching() -> None:
    value = {"outer": [{"id": "a" * 64}, "prefix-" + "b" * 64]}
    assert driver._contains_exact(value, "a" * 64) is True
    assert driver._contains_exact(value, "b" * 64) is False
