"""Deterministic corpus and chunking contracts for the Knowledge Hub RAG flagship."""

from .binding import validate_chunk_manifest_against_snapshot
from .contracts import (
    ContractError,
    build_chunk_manifest,
    build_corpus_snapshot,
    validate_chunk_manifest,
    validate_corpus_snapshot,
    verify_snapshot_bytes,
)

__all__ = [
    "ContractError",
    "build_chunk_manifest",
    "build_corpus_snapshot",
    "validate_chunk_manifest",
    "validate_chunk_manifest_against_snapshot",
    "validate_corpus_snapshot",
    "verify_snapshot_bytes",
]
