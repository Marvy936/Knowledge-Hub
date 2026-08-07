from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .contracts import (
    ContractError,
    build_chunk_manifest,
    validate_chunk_manifest,
    validate_corpus_snapshot,
)


def validate_chunk_manifest_against_snapshot(
    *, manifest: Mapping[str, Any], snapshot: Mapping[str, Any]
) -> None:
    """Bind every present chunk source identity back to the exact corpus snapshot."""

    validate_chunk_manifest(manifest)
    validate_corpus_snapshot(snapshot)

    if manifest["corpus_snapshot_id"] != snapshot["corpus_snapshot_id"]:
        raise ContractError("chunk manifest belongs to another corpus snapshot")
    if manifest["source_revision"] != snapshot["source_revision"]:
        raise ContractError("chunk manifest source revision differs from corpus snapshot")

    source_files = {item["path"]: item["sha256"] for item in snapshot["files"]}
    for index, chunk in enumerate(manifest["chunks"]):
        path = chunk["source_path"]
        if path not in source_files:
            raise ContractError(f"chunks[{index}] references a path outside the corpus snapshot")
        if chunk["source_sha256"] != source_files[path]:
            raise ContractError(f"chunks[{index}] source digest differs from corpus snapshot")


def verify_chunk_manifest_rebuild(
    *, repo_root: Path, manifest: Mapping[str, Any], snapshot: Mapping[str, Any]
) -> None:
    """Rebuild chunks from exact source bytes so omissions and reordered content are refused."""

    validate_chunk_manifest_against_snapshot(manifest=manifest, snapshot=snapshot)
    chunking = manifest["chunking"]
    rebuilt = build_chunk_manifest(
        repo_root=repo_root,
        snapshot=snapshot,
        max_chars=chunking["max_chars"],
        min_chars=chunking["min_chars"],
    )
    if rebuilt["chunk_manifest_id"] != manifest["chunk_manifest_id"]:
        raise ContractError("chunk manifest does not match deterministic rebuild from corpus bytes")
