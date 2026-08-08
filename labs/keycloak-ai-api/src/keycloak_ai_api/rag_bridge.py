from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol


class RagBridgeError(ValueError):
    pass


class RagExecutor(Protocol):
    def query(self, text: str) -> Mapping[str, Any]: ...


def _load_json(path: Path, *, expected: type = dict) -> Any:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RagBridgeError(f"required RAG artifact does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RagBridgeError(f"invalid RAG artifact JSON: {path}") from exc
    if not isinstance(value, expected):
        raise RagBridgeError(
            f"RAG artifact {path} must contain a {expected.__name__} root"
        )
    return value


@dataclass(frozen=True)
class RagBundlePaths:
    manifest: Path
    index: Path
    runtime_config: Path
    eval_cases: Path
    eval_report: Path
    prompt_release: Path


class OfflinePromotedRagExecutor:
    def __init__(self, paths: RagBundlePaths) -> None:
        try:
            from knowledge_hub_rag.evaluation import (
                build_prompt_release,
                validate_eval_report,
            )
            from knowledge_hub_rag.retrieval import validate_retrieval_index
            from knowledge_hub_rag.runtime_config import validate_runtime_config
        except ImportError as exc:
            raise RagBridgeError(
                "RAG bridge requires the local knowledge-hub-rag package to be installed"
            ) from exc

        manifest = _load_json(paths.manifest)
        index = _load_json(paths.index)
        config = _load_json(paths.runtime_config)
        cases = _load_json(paths.eval_cases, expected=list)
        report = _load_json(paths.eval_report)
        release = _load_json(paths.prompt_release)

        try:
            validate_runtime_config(config)
            validate_retrieval_index(index, manifest)
            validate_eval_report(
                report,
                cases=cases,
                manifest=manifest,
                index=index,
                runtime_config=config,
            )
            expected_release = build_prompt_release(
                runtime_config=config,
                eval_report=report,
                cases=cases,
                manifest=manifest,
                index=index,
            )
        except Exception as exc:
            raise RagBridgeError(
                f"RAG promotion bundle validation failed: {type(exc).__name__}: {exc}"
            ) from exc
        if release != expected_release:
            raise RagBridgeError(
                "prompt release does not match the exact rebuilt eval/config/corpus/index subject"
            )

        self._manifest = manifest
        self._index = index
        self._config = config
        self._release = release

    @property
    def prompt_release_id(self) -> str:
        return str(self._release["prompt_release_id"])

    @property
    def source_revision(self) -> str:
        return str(self._release["source_revision"])

    def query(self, text: str) -> Mapping[str, Any]:
        if not isinstance(text, str) or not text.strip():
            raise RagBridgeError("RAG query must be a non-empty string")
        if len(text) > 2000:
            raise RagBridgeError("RAG query exceeds the 2000-character request bound")
        try:
            from knowledge_hub_rag.offline_adapter import run_offline_adapter
            from knowledge_hub_rag.retrieval import build_grounded_context, retrieve
            from knowledge_hub_rag.tracing import build_trace
        except ImportError as exc:
            raise RagBridgeError("RAG runtime package is unavailable") from exc

        started = time.perf_counter()
        try:
            retrieval = retrieve(
                index=self._index,
                manifest=self._manifest,
                query=text,
                top_k=self._config["retrieval"]["top_k"],
                min_score=self._config["retrieval"]["min_score"],
            )
            context = build_grounded_context(
                retrieval,
                index=self._index,
                manifest=self._manifest,
                max_chars=self._config["context"]["max_chars"],
            )
            adapter = run_offline_adapter(
                retrieval_result=retrieval,
                index=self._index,
                manifest=self._manifest,
                runtime_config=self._config,
            )
            latency_ms = (time.perf_counter() - started) * 1000.0
            trace = build_trace(
                runtime_config=self._config,
                retrieval_result=retrieval,
                adapter_result=adapter,
                context=context,
                index=self._index,
                manifest=self._manifest,
                latency_ms=latency_ms,
            )
        except Exception as exc:
            raise RagBridgeError(
                f"bounded offline RAG execution failed: {type(exc).__name__}: {exc}"
            ) from exc

        answer = adapter["answer"]
        return {
            "status": answer["status"],
            "answer": answer["answer"],
            "abstention_reason": answer["abstention_reason"],
            "citations": answer["citations"],
            "prompt_release_id": self.prompt_release_id,
            "source_revision": self.source_revision,
            "retrieval_result_id": retrieval["retrieval_result_id"],
            "answer_id": answer["answer_id"],
            "trace_id": trace["trace_id"],
            "latency_ms": trace["latency_ms"],
        }
