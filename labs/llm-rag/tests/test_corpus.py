from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from knowledge_hub_rag.contracts import (
    ContractError,
    build_chunk_manifest,
    build_corpus_snapshot,
    validate_chunk_manifest,
    validate_corpus_snapshot,
    verify_snapshot_bytes,
)

REVISION = "a" * 40


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    docs = root / "docs"
    docs.mkdir(parents=True)
    (docs / "intro.md").write_text(
        "# Knowledge Hub\n\nIntro paragraph.\n\n## Commands\n\nUse this command:\n\n```bash\necho hello\n```\n\nFinal paragraph.\n",
        encoding="utf-8",
    )
    nested = docs / "platform"
    nested.mkdir()
    (nested / "runtime.md").write_text(
        "# Runtime\n\nRuntime identity matters.\n\n## Failure\n\nMissing evidence is not success.\n",
        encoding="utf-8",
    )
    return root


def test_snapshot_is_deterministic_and_path_sorted(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    first = build_corpus_snapshot(repo_root=root, source_revision=REVISION)
    second = build_corpus_snapshot(repo_root=root, source_revision=REVISION)
    assert first == second
    assert first["file_count"] == 2
    assert [item["path"] for item in first["files"]] == [
        "docs/intro.md",
        "docs/platform/runtime.md",
    ]
    validate_corpus_snapshot(first)


def test_snapshot_identity_is_workspace_independent(tmp_path: Path) -> None:
    first_root = _repo(tmp_path / "one")
    second_root = _repo(tmp_path / "two")
    first = build_corpus_snapshot(repo_root=first_root, source_revision=REVISION)
    second = build_corpus_snapshot(repo_root=second_root, source_revision=REVISION)
    assert first["corpus_snapshot_id"] == second["corpus_snapshot_id"]


def test_snapshot_refuses_non_exact_revision(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    with pytest.raises(ContractError, match="exact lowercase 40-hex"):
        build_corpus_snapshot(repo_root=root, source_revision="main")


def test_snapshot_readback_detects_changed_source_bytes(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    snapshot = build_corpus_snapshot(repo_root=root, source_revision=REVISION)
    verify_snapshot_bytes(repo_root=root, snapshot=snapshot)
    (root / "docs" / "intro.md").write_text("changed\n", encoding="utf-8")
    with pytest.raises(ContractError, match="snapshot size mismatch|snapshot digest mismatch"):
        verify_snapshot_bytes(repo_root=root, snapshot=snapshot)


def test_snapshot_tampering_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    snapshot = build_corpus_snapshot(repo_root=root, source_revision=REVISION)
    tampered = deepcopy(snapshot)
    tampered["files"][0]["size_bytes"] += 1
    with pytest.raises(ContractError, match="corpus_snapshot_id"):
        validate_corpus_snapshot(tampered)


def test_symlinked_corpus_file_is_forbidden(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    link = root / "docs" / "linked.md"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are unavailable in this environment")
    with pytest.raises(ContractError, match="symlinked corpus file"):
        build_corpus_snapshot(repo_root=root, source_revision=REVISION)


def test_chunk_manifest_preserves_heading_path_and_code_fence(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    snapshot = build_corpus_snapshot(repo_root=root, source_revision=REVISION)
    manifest = build_chunk_manifest(
        repo_root=root,
        snapshot=snapshot,
        max_chars=400,
        min_chars=40,
    )
    validate_chunk_manifest(manifest)
    intro_chunks = [item for item in manifest["chunks"] if item["source_path"] == "docs/intro.md"]
    assert any(item["heading_path"] == ["Knowledge Hub", "Commands"] for item in intro_chunks)
    assert any("```bash\necho hello\n```" in item["content"] for item in intro_chunks)


def test_chunk_manifest_is_deterministic(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    snapshot = build_corpus_snapshot(repo_root=root, source_revision=REVISION)
    first = build_chunk_manifest(repo_root=root, snapshot=snapshot, max_chars=320, min_chars=40)
    second = build_chunk_manifest(repo_root=root, snapshot=snapshot, max_chars=320, min_chars=40)
    assert first == second
    assert first["chunk_manifest_id"] == second["chunk_manifest_id"]
    assert len({item["chunk_id"] for item in first["chunks"]}) == first["chunk_count"]


def test_chunk_identity_changes_when_source_bytes_change(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    first_snapshot = build_corpus_snapshot(repo_root=root, source_revision=REVISION)
    first_manifest = build_chunk_manifest(repo_root=root, snapshot=first_snapshot, max_chars=400, min_chars=40)
    (root / "docs" / "intro.md").write_text(
        (root / "docs" / "intro.md").read_text(encoding="utf-8") + "\nAdded evidence.\n",
        encoding="utf-8",
    )
    second_snapshot = build_corpus_snapshot(repo_root=root, source_revision=REVISION)
    second_manifest = build_chunk_manifest(repo_root=root, snapshot=second_snapshot, max_chars=400, min_chars=40)
    assert first_snapshot["corpus_snapshot_id"] != second_snapshot["corpus_snapshot_id"]
    assert first_manifest["chunk_manifest_id"] != second_manifest["chunk_manifest_id"]


def test_chunk_manifest_tampering_is_rejected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    snapshot = build_corpus_snapshot(repo_root=root, source_revision=REVISION)
    manifest = build_chunk_manifest(repo_root=root, snapshot=snapshot, max_chars=400, min_chars=40)
    tampered = deepcopy(manifest)
    tampered["chunks"][0]["content"] += " forged"
    with pytest.raises(ContractError, match="char_count|content_sha256|chunk_manifest_id"):
        validate_chunk_manifest(tampered)
