from __future__ import annotations

from typing import Any, Mapping

from .contracts import ContractError, validate_chunk_manifest, validate_corpus_snapshot


def validate_chunk_manifest_against_snapshot(
    *, manifest: Mapping[str, Any], snapshot: Mapping[str, Any]
) -> None:
    """Bind every chunk source identity back to the exact corpus snapshot."""

    validate_chunk_manifest(manifest)
    validate_corpus_snapshot(snapshot)

    if manifest["corpus_snapshot_id"] != snapshot["corpus_snapshot_id"]:
        raise ContractError("chunk manifest belongs to another corpus snapshot")
    if manifest["source_revision"] != snapshot["source_revision"]:
        raise ContractError("chunk manifest source revision differs from corpus snapshot")

    source_files = {item["path"]: item["sha256"] for item in snapshot["files"]}
    observed_paths: set[str] = set()
    for index, chunk in enumerate(manifest["chunks"]):
        path = chunk["source_path"]
        if path not in source_files:
            raise ContractError(f"chunks[{index}] references a path outside the corpus snapshot")
        if chunk["source_sha256"] != source_files[path]:
            raise ContractError(f"chunks[{index}] source digest differs from corpus snapshot")
        observed_paths.add(path)

    missing = sorted(set(source_files) - observed_paths)
    if missing:
        raise ContractError(f"chunk manifest contains no chunks for snapshot files: {missing}")
