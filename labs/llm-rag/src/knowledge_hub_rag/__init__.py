"""Deterministic corpus, retrieval and grounded-answer contracts for the Knowledge Hub RAG flagship."""

from .answers import build_answer_envelope, validate_answer_envelope
from .binding import validate_chunk_manifest_against_snapshot
from .contracts import (
    ContractError,
    build_chunk_manifest,
    build_corpus_snapshot,
    validate_chunk_manifest,
    validate_corpus_snapshot,
    verify_snapshot_bytes,
)
from .retrieval import (
    build_grounded_context,
    build_retrieval_index,
    retrieve,
    validate_retrieval_index,
    validate_retrieval_result,
)

__all__ = [
    "ContractError",
    "build_answer_envelope",
    "build_chunk_manifest",
    "build_corpus_snapshot",
    "build_grounded_context",
    "build_retrieval_index",
    "retrieve",
    "validate_answer_envelope",
    "validate_chunk_manifest",
    "validate_chunk_manifest_against_snapshot",
    "validate_corpus_snapshot",
    "validate_retrieval_index",
    "validate_retrieval_result",
    "verify_snapshot_bytes",
]
