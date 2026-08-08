from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

from keycloak_ai_api.rag_bridge import (
    OfflinePromotedRagExecutor,
    RagBridgeError,
    RagBundlePaths,
)


def _write(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
    return path


def _paths(tmp_path: Path, *, forged_release: bool = False) -> RagBundlePaths:
    manifest = {
        "chunk_manifest_id": "a" * 64,
        "corpus_snapshot_id": "b" * 64,
        "source_revision": "c" * 40,
    }
    index = {"retrieval_index_id": "d" * 64}
    config = {
        "runtime_config_id": "e" * 64,
        "implementation_revision": "c" * 40,
        "retrieval": {"top_k": 5, "min_score": 0.01},
        "context": {"max_chars": 6000},
    }
    cases = [{"case_id": "safe"}]
    report = {
        "eval_report_id": "f" * 64,
        "runtime_config_id": "e" * 64,
        "suite_passed": True,
    }
    release = {
        "prompt_release_id": ("0" if forged_release else "1") * 64,
        "source_revision": "c" * 40,
        "runtime_config_id": "e" * 64,
    }
    return RagBundlePaths(
        manifest=_write(tmp_path / "manifest.json", manifest),
        index=_write(tmp_path / "index.json", index),
        runtime_config=_write(tmp_path / "config.json", config),
        eval_cases=_write(tmp_path / "cases.json", cases),
        eval_report=_write(tmp_path / "report.json", report),
        prompt_release=_write(tmp_path / "release.json", release),
    )


def _install_fake_rag(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    calls: list[str] = []
    expected_release = {
        "prompt_release_id": "1" * 64,
        "source_revision": "c" * 40,
        "runtime_config_id": "e" * 64,
    }

    evaluation = types.ModuleType("knowledge_hub_rag.evaluation")

    def validate_eval_report(report, *, cases, manifest, index, runtime_config):
        calls.append("validate_eval_report")
        assert report["suite_passed"] is True
        assert cases == [{"case_id": "safe"}]
        assert manifest["source_revision"] == runtime_config["implementation_revision"]
        assert index["retrieval_index_id"] == "d" * 64

    def build_prompt_release(*, runtime_config, eval_report, cases, manifest, index):
        calls.append("build_prompt_release")
        return dict(expected_release)

    evaluation.validate_eval_report = validate_eval_report
    evaluation.build_prompt_release = build_prompt_release

    retrieval_module = types.ModuleType("knowledge_hub_rag.retrieval")

    def validate_retrieval_index(index, manifest):
        calls.append("validate_retrieval_index")
        assert index["retrieval_index_id"] == "d" * 64
        assert manifest["chunk_manifest_id"] == "a" * 64

    def retrieve(*, index, manifest, query, top_k, min_score):
        calls.append("retrieve")
        assert query == "Kubernetes Service"
        return {
            "retrieval_result_id": "2" * 64,
            "query": {"query_id": "3" * 64},
            "hit_count": 1,
        }

    def build_grounded_context(result, *, index, manifest, max_chars):
        calls.append("build_grounded_context")
        return {"context_id": "4" * 64, "context_chars": 120}

    retrieval_module.validate_retrieval_index = validate_retrieval_index
    retrieval_module.retrieve = retrieve
    retrieval_module.build_grounded_context = build_grounded_context

    runtime_config = types.ModuleType("knowledge_hub_rag.runtime_config")

    def validate_runtime_config(config):
        calls.append("validate_runtime_config")
        assert config["implementation_revision"] == "c" * 40

    runtime_config.validate_runtime_config = validate_runtime_config

    offline = types.ModuleType("knowledge_hub_rag.offline_adapter")

    def run_offline_adapter(*, retrieval_result, index, manifest, runtime_config):
        calls.append("run_offline_adapter")
        return {
            "adapter_result_id": "5" * 64,
            "answer": {
                "status": "answered",
                "answer": "A Kubernetes Service provides a stable endpoint.",
                "abstention_reason": None,
                "citations": [{"chunk_id": "6" * 64}],
                "answer_id": "7" * 64,
            },
        }

    offline.run_offline_adapter = run_offline_adapter

    tracing = types.ModuleType("knowledge_hub_rag.tracing")

    def build_trace(**kwargs):
        calls.append("build_trace")
        assert kwargs["context"]["context_id"] == "4" * 64
        return {"trace_id": "8" * 64, "latency_ms": 1.5}

    tracing.build_trace = build_trace

    root = types.ModuleType("knowledge_hub_rag")
    monkeypatch.setitem(sys.modules, "knowledge_hub_rag", root)
    monkeypatch.setitem(sys.modules, "knowledge_hub_rag.evaluation", evaluation)
    monkeypatch.setitem(sys.modules, "knowledge_hub_rag.retrieval", retrieval_module)
    monkeypatch.setitem(sys.modules, "knowledge_hub_rag.runtime_config", runtime_config)
    monkeypatch.setitem(sys.modules, "knowledge_hub_rag.offline_adapter", offline)
    monkeypatch.setitem(sys.modules, "knowledge_hub_rag.tracing", tracing)
    return {"calls": calls, "release": expected_release}


def test_promoted_bundle_is_rebuilt_before_query_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _install_fake_rag(monkeypatch)
    executor = OfflinePromotedRagExecutor(_paths(tmp_path))
    assert executor.prompt_release_id == "1" * 64
    assert executor.source_revision == "c" * 40

    result = executor.query("Kubernetes Service")
    assert result["status"] == "answered"
    assert result["prompt_release_id"] == "1" * 64
    assert result["source_revision"] == "c" * 40
    assert result["retrieval_result_id"] == "2" * 64
    assert result["answer_id"] == "7" * 64
    assert result["trace_id"] == "8" * 64
    assert fake["calls"][:4] == [
        "validate_runtime_config",
        "validate_retrieval_index",
        "validate_eval_report",
        "build_prompt_release",
    ]
    assert "retrieve" in fake["calls"]
    assert "run_offline_adapter" in fake["calls"]
    assert "build_trace" in fake["calls"]


def test_forged_prompt_release_is_refused_before_query(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_fake_rag(monkeypatch)
    with pytest.raises(RagBridgeError, match="prompt release does not match"):
        OfflinePromotedRagExecutor(_paths(tmp_path, forged_release=True))


def test_bridge_refuses_missing_or_oversized_query(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_fake_rag(monkeypatch)
    executor = OfflinePromotedRagExecutor(_paths(tmp_path))
    with pytest.raises(RagBridgeError, match="non-empty"):
        executor.query("   ")
    with pytest.raises(RagBridgeError, match="2000-character"):
        executor.query("x" * 2001)
