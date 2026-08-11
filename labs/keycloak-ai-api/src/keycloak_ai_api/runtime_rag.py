from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from knowledge_hub_rag.contracts import (
    atomic_write_json,
    build_chunk_manifest,
    build_corpus_snapshot,
)
from knowledge_hub_rag.evaluation import build_prompt_release, run_eval_suite
from knowledge_hub_rag.retrieval import build_retrieval_index, validate_retrieval_index
from knowledge_hub_rag.runtime_config import build_runtime_config, validate_runtime_config

from .rag_bridge import OfflinePromotedRagExecutor, RagBundlePaths


class RuntimeRagError(ValueError):
    pass


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
RUNTIME_GENERATION = "practical-v1-keycloak-live-rag-v1"
POSITIVE_SEARCH_LIMIT = 100


def _require_sha256(value: object, field: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise RuntimeRagError(f"{field} must be a lowercase SHA-256")
    return value


def _require_subject_sha(value: str) -> str:
    text = value.strip()
    if GIT_SHA1_RE.fullmatch(text) is None:
        raise RuntimeRagError("subject SHA must be a lowercase 40-character Git SHA-1")
    return text


def _read_eval_cases(path: Path) -> list[dict[str, Any]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeRagError(f"cannot read RAG eval cases {path}: {exc}") from exc
    if not isinstance(value, list) or not value or not all(isinstance(item, dict) for item in value):
        raise RuntimeRagError("RAG eval cases must be a non-empty object list")
    return [dict(item) for item in value]


def _query_from_chunk(chunk: Mapping[str, Any]) -> str:
    for field in ("content", "text", "body", "chunk_text"):
        value = chunk.get(field)
        if not isinstance(value, str):
            continue
        words = [
            word
            for word in re.findall(r"[A-Za-z0-9_./:-]+", value)
            if len(word) >= 3
        ]
        if words:
            return " ".join(words[: min(8, len(words))])
    raise RuntimeRagError("canonical RAG chunk contains no queryable text")


def build_live_rag_bundle(
    *,
    repo_root: Path,
    runtime_root: Path,
    subject_sha: str,
) -> dict[str, Any]:
    root = repo_root.resolve(strict=True)
    subject = _require_subject_sha(subject_sha)
    rag = runtime_root / "rag"
    if rag.exists() or rag.is_symlink():
        raise RuntimeRagError("Keycloak RAG runtime root must be fresh")
    rag.mkdir(parents=True, exist_ok=False)

    corpus_snapshot_path = rag / "corpus-snapshot.json"
    manifest_path = rag / "chunk-manifest.json"
    index_path = rag / "retrieval-index.json"
    config_path = rag / "runtime-config.json"
    evaluation_path = rag / "eval-report.json"
    release_path = rag / "prompt-release.json"
    preflight_path = rag / "preflight-query.json"
    cases_path = root / "labs" / "llm-rag" / "data" / "eval-cases.json"

    snapshot = build_corpus_snapshot(repo_root=root, source_revision=subject)
    corpus_snapshot_id = _require_sha256(
        snapshot.get("corpus_snapshot_id"),
        "RAG corpus_snapshot_id",
    )
    if snapshot.get("source_revision") != subject:
        raise RuntimeRagError("RAG corpus source revision mismatch")
    atomic_write_json(corpus_snapshot_path, snapshot)

    manifest = build_chunk_manifest(repo_root=root, snapshot=snapshot)
    chunk_manifest_id = _require_sha256(
        manifest.get("chunk_manifest_id"),
        "RAG chunk_manifest_id",
    )
    if manifest.get("corpus_snapshot_id") != corpus_snapshot_id:
        raise RuntimeRagError("RAG chunk manifest is detached from corpus snapshot")
    chunks = manifest.get("chunks")
    if not isinstance(chunks, list) or not chunks or not all(isinstance(item, dict) for item in chunks):
        raise RuntimeRagError("RAG chunk manifest contains no canonical chunks")
    atomic_write_json(manifest_path, manifest)

    index = build_retrieval_index(manifest)
    validate_retrieval_index(index, manifest)
    retrieval_index_id = _require_sha256(
        index.get("retrieval_index_id"),
        "RAG retrieval_index_id",
    )
    if index.get("chunk_manifest_id") != chunk_manifest_id:
        raise RuntimeRagError("RAG retrieval index is detached from chunk manifest")
    atomic_write_json(index_path, index)

    config = build_runtime_config(
        generation=RUNTIME_GENERATION,
        implementation_revision=subject,
    )
    validate_runtime_config(config)
    atomic_write_json(config_path, config)

    cases = _read_eval_cases(cases_path)
    evaluation = run_eval_suite(
        cases=cases,
        manifest=manifest,
        index=index,
        runtime_config=config,
    )
    eval_report_id = _require_sha256(
        evaluation.get("eval_report_id"),
        "RAG eval_report_id",
    )
    failed_case_ids = sorted(
        result.get("case_id", "<missing>")
        for result in evaluation.get("results", [])
        if result.get("case_passed") is not True
    )
    if evaluation.get("suite_passed") is not True or failed_case_ids:
        raise RuntimeRagError(
            f"promoted RAG evaluation is not all-passed: {failed_case_ids}"
        )
    atomic_write_json(evaluation_path, evaluation)

    release = build_prompt_release(
        runtime_config=config,
        eval_report=evaluation,
        cases=cases,
        manifest=manifest,
        index=index,
    )
    prompt_release_id = _require_sha256(
        release.get("prompt_release_id"),
        "RAG prompt_release_id",
    )
    expected_bindings = {
        "source_revision": subject,
        "corpus_snapshot_id": corpus_snapshot_id,
        "chunk_manifest_id": chunk_manifest_id,
        "retrieval_index_id": retrieval_index_id,
        "eval_report_id": eval_report_id,
    }
    for field, expected in expected_bindings.items():
        if release.get(field) != expected:
            raise RuntimeRagError(f"RAG prompt release does not bind exact {field}")
    atomic_write_json(release_path, release)

    executor = OfflinePromotedRagExecutor(
        RagBundlePaths(
            manifest=manifest_path,
            index=index_path,
            runtime_config=config_path,
            eval_cases=cases_path,
            eval_report=evaluation_path,
            prompt_release=release_path,
        )
    )
    if executor.prompt_release_id != prompt_release_id or executor.source_revision != subject:
        raise RuntimeRagError("promoted RAG executor resolved a different release subject")

    query: str | None = None
    preflight: dict[str, Any] | None = None
    attempted = 0
    for chunk in chunks:
        if attempted >= POSITIVE_SEARCH_LIMIT:
            break
        try:
            candidate_query = _query_from_chunk(chunk)
        except RuntimeRagError:
            continue
        attempted += 1
        result = dict(executor.query(candidate_query))
        if result.get("status") == "answered" and result.get("citations"):
            query = candidate_query
            preflight = result
            break
    if query is None or preflight is None:
        raise RuntimeRagError(
            f"no answered promoted RAG query found in first {min(len(chunks), POSITIVE_SEARCH_LIMIT)} chunks"
        )
    if preflight.get("prompt_release_id") != prompt_release_id:
        raise RuntimeRagError("RAG preflight answer is detached from promoted release")
    atomic_write_json(preflight_path, preflight)

    return {
        "corpus_snapshot": corpus_snapshot_path,
        "manifest": manifest_path,
        "index": index_path,
        "runtime_config": config_path,
        "eval_cases": cases_path,
        "eval_report": evaluation_path,
        "prompt_release": release_path,
        "preflight": preflight_path,
        "query": query,
        "snapshot_id": corpus_snapshot_id,
        "corpus_snapshot_id": corpus_snapshot_id,
        "chunk_manifest_id": chunk_manifest_id,
        "index_id": retrieval_index_id,
        "retrieval_index_id": retrieval_index_id,
        "report_id": eval_report_id,
        "eval_report_id": eval_report_id,
        "prompt_release_id": prompt_release_id,
    }
