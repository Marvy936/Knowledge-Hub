"""Deterministic corpus, retrieval, evaluation, security and answer contracts for Knowledge Hub RAG."""

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
from .evaluation import (
    build_prompt_release,
    run_eval_case,
    run_eval_suite,
    validate_eval_case,
    validate_eval_report,
)
from .offline_adapter import run_offline_adapter, validate_offline_adapter_result
from .retrieval import (
    build_grounded_context,
    build_retrieval_index,
    retrieve,
    validate_retrieval_index,
    validate_retrieval_result,
)
from .runtime_config import build_runtime_config, validate_runtime_config
from .security import scan_prompt_injection, validate_security_evidence
from .tracing import build_trace, validate_trace

__all__ = [
    "ContractError",
    "build_answer_envelope",
    "build_chunk_manifest",
    "build_corpus_snapshot",
    "build_grounded_context",
    "build_prompt_release",
    "build_retrieval_index",
    "build_runtime_config",
    "build_trace",
    "retrieve",
    "run_eval_case",
    "run_eval_suite",
    "run_offline_adapter",
    "scan_prompt_injection",
    "validate_answer_envelope",
    "validate_chunk_manifest",
    "validate_chunk_manifest_against_snapshot",
    "validate_corpus_snapshot",
    "validate_eval_case",
    "validate_eval_report",
    "validate_offline_adapter_result",
    "validate_retrieval_index",
    "validate_retrieval_result",
    "validate_runtime_config",
    "validate_security_evidence",
    "validate_trace",
    "verify_snapshot_bytes",
]
