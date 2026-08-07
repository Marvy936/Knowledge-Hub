from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from knowledge_hub_rag.binding import (
    validate_chunk_manifest_against_snapshot,
    verify_chunk_manifest_rebuild,
)
from knowledge_hub_rag.contracts import (
    ContractError,
    build_chunk_manifest,
    build_corpus_snapshot,
    canonical_json_bytes,
    sha256_bytes,
)

REVISION = "d" * 40


def _subjects(tmp_path: Path):
    root = tmp_path / "repo"
    docs = root / "docs"
    docs.mkdir(parents=True)
    (docs / "one.md").write_text("# One\n\nFirst corpus subject.\n", encoding="utf-8")
    (docs / "two.md").write_text("# Two\n\nSecond corpus subject.\n", encoding="utf-8")
    snapshot = build_corpus_snapshot(repo_root=root, source_revision=REVISION)
    manifest = build_chunk_manifest(repo_root=root, snapshot=snapshot, max_chars=400, min_chars=40)
    return root, snapshot, manifest


def test_chunk_manifest_is_bound_to_exact_snapshot(tmp_path: Path) -> None:
    root, snapshot, manifest = _subjects(tmp_path)
    validate_chunk_manifest_against_snapshot(manifest=manifest, snapshot=snapshot)
    verify_chunk_manifest_rebuild(repo_root=root, manifest=manifest, snapshot=snapshot)


def test_rehashed_forged_source_digest_is_rejected(tmp_path: Path) -> None:
    _, snapshot, manifest = _subjects(tmp_path)
    forged = deepcopy(manifest)
    forged_chunk = forged["chunks"][0]
    forged_chunk["source_sha256"] = "e" * 64
    chunk_payload = {
        key: forged_chunk[key]
        for key in (
            "source_path",
            "source_sha256",
            "heading_path",
            "ordinal",
            "content_sha256",
            "char_count",
        )
    }
    forged_chunk["chunk_id"] = sha256_bytes(canonical_json_bytes(chunk_payload))
    manifest_payload = {key: value for key, value in forged.items() if key != "chunk_manifest_id"}
    forged["chunk_manifest_id"] = sha256_bytes(canonical_json_bytes(manifest_payload))

    with pytest.raises(ContractError, match="source digest differs"):
        validate_chunk_manifest_against_snapshot(manifest=forged, snapshot=snapshot)


def test_manifest_from_another_snapshot_is_rejected(tmp_path: Path) -> None:
    root, snapshot, manifest = _subjects(tmp_path)
    (root / "docs" / "one.md").write_text("# One\n\nChanged subject.\n", encoding="utf-8")
    other_snapshot = build_corpus_snapshot(repo_root=root, source_revision=REVISION)
    assert other_snapshot["corpus_snapshot_id"] != snapshot["corpus_snapshot_id"]
    with pytest.raises(ContractError, match="another corpus snapshot"):
        validate_chunk_manifest_against_snapshot(manifest=manifest, snapshot=other_snapshot)


def test_rehashed_omitted_chunk_is_rejected_by_rebuild(tmp_path: Path) -> None:
    root, snapshot, manifest = _subjects(tmp_path)
    forged = deepcopy(manifest)
    forged["chunks"] = forged["chunks"][:-1]
    forged["chunk_count"] = len(forged["chunks"])
    payload = {key: value for key, value in forged.items() if key != "chunk_manifest_id"}
    forged["chunk_manifest_id"] = sha256_bytes(canonical_json_bytes(payload))

    validate_chunk_manifest_against_snapshot(manifest=forged, snapshot=snapshot)
    with pytest.raises(ContractError, match="deterministic rebuild"):
        verify_chunk_manifest_rebuild(repo_root=root, manifest=forged, snapshot=snapshot)
