from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from knowledge_hub_rag.contracts import (
    ContractError,
    atomic_write_json,
    build_chunk_manifest,
    build_corpus_snapshot,
)
from knowledge_hub_rag.evaluation import build_prompt_release, run_eval_suite
from knowledge_hub_rag.offline_adapter import run_offline_adapter
from knowledge_hub_rag.retrieval import (
    build_grounded_context,
    build_retrieval_index,
    retrieve,
    validate_retrieval_index,
)
from knowledge_hub_rag.runtime_config import build_runtime_config, validate_runtime_config
from knowledge_hub_rag.tracing import build_trace


class RagRuntimeError(RuntimeError):
    pass


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RUNTIME_RELATIVE = Path(".runtime/llm-rag")
RUNTIME_GENERATION = "practical-v1-rag-runtime-v1"
POSITIVE_SEARCH_LIMIT = 100


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Execute the authoritative Knowledge Hub RAG corpus→chunk→index→retrieval→"
            "adapter→trace→eval→release lifecycle for an exact clean Git subject."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--subject-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def _require_git_sha(value: str) -> str:
    text = value.strip()
    if len(text) != 40 or any(character not in "0123456789abcdef" for character in text):
        raise RagRuntimeError("subject SHA must be a lowercase 40-character Git SHA-1")
    return text


def _require_sha256(value: object, field: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise RagRuntimeError(f"{field} must be a lowercase SHA-256")
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RagRuntimeError(f"cannot read JSON artifact {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RagRuntimeError(f"JSON artifact must be an object: {path}")
    return value


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RagRuntimeError(f"cannot read JSON list {path}: {exc}") from exc
    if not isinstance(value, list) or not value or not all(isinstance(item, dict) for item in value):
        raise RagRuntimeError(f"JSON artifact must be a non-empty object list: {path}")
    return [dict(item) for item in value]


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
    expected_codes: set[int] | None = None,
) -> subprocess.CompletedProcess[str]:
    allowed = {0} if expected_codes is None else expected_codes
    result = subprocess.run(
        list(command),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONHASHSEED": "0"},
    )
    if result.returncode not in allowed:
        raise RagRuntimeError(
            f"command returned {result.returncode}, expected {sorted(allowed)}: {' '.join(command)}\n"
            f"stdout tail:\n{(result.stdout or '')[-5000:]}\n"
            f"stderr tail:\n{(result.stderr or '')[-5000:]}"
        )
    return result


def _walk(value: object) -> Iterable[object]:
    yield value
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _contains_exact(value: object, expected: object) -> bool:
    return any(item == expected for item in _walk(value))


def _chunk_records(value: object) -> list[dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}

    def visit(item: object) -> None:
        if isinstance(item, dict):
            chunk_id = item.get("chunk_id")
            if isinstance(chunk_id, str) and chunk_id:
                records.setdefault(chunk_id, dict(item))
            for nested in item.values():
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)

    visit(value)
    return [records[chunk_id] for chunk_id in sorted(records)]


def _query_from_chunk(chunk: Mapping[str, Any]) -> str:
    for field in ("content", "text", "body", "chunk_text"):
        value = chunk.get(field)
        if isinstance(value, str):
            words = [word for word in re.findall(r"[A-Za-z0-9_./:-]+", value) if len(word) >= 3]
            if words:
                return " ".join(words[: min(8, len(words))])
    for value in chunk.values():
        if isinstance(value, str) and not SHA256_RE.fullmatch(value):
            words = [word for word in re.findall(r"[A-Za-z0-9_./:-]+", value) if len(word) >= 3]
            if words:
                return " ".join(words[: min(8, len(words))])
    raise RagRuntimeError("cannot derive positive query from corpus chunk")


def _query_from_chunks(chunks: Sequence[Mapping[str, Any]]) -> str:
    for chunk in chunks:
        try:
            return _query_from_chunk(chunk)
        except RagRuntimeError:
            continue
    raise RagRuntimeError("cannot derive positive query from any canonical corpus chunk")


def _citation_chunk_ids(answer: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    citations = answer.get("citations")
    if not isinstance(citations, list):
        return result

    def visit(item: object) -> None:
        if isinstance(item, dict):
            chunk_id = item.get("chunk_id")
            if isinstance(chunk_id, str):
                result.add(chunk_id)
            for nested in item.values():
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)

    visit(citations)
    return result


def _write_artifact(
    *,
    name: str,
    path: Path,
    value: Mapping[str, Any],
    artifacts: dict[str, dict[str, Any]],
) -> None:
    atomic_write_json(path, value)
    artifacts[name] = {
        "sha256": _sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def _positive_execution(
    *,
    chunks: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Any],
    index: Mapping[str, Any],
    runtime_config: Mapping[str, Any],
) -> tuple[str, dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    attempted = 0
    for chunk in chunks:
        if attempted >= POSITIVE_SEARCH_LIMIT:
            break
        try:
            query = _query_from_chunk(chunk)
        except RagRuntimeError:
            continue
        attempted += 1
        retrieval = retrieve(
            index=index,
            manifest=manifest,
            query=query,
            top_k=runtime_config["retrieval"]["top_k"],
            min_score=runtime_config["retrieval"]["min_score"],
        )
        if retrieval["status"] != "results":
            continue
        context = build_grounded_context(
            retrieval,
            index=index,
            manifest=manifest,
            max_chars=runtime_config["context"]["max_chars"],
        )
        adapter = run_offline_adapter(
            retrieval_result=retrieval,
            index=index,
            manifest=manifest,
            runtime_config=runtime_config,
        )
        answer = adapter["answer"]
        if answer["status"] != "answered" or not answer["citations"]:
            continue
        trace = build_trace(
            runtime_config=runtime_config,
            retrieval_result=retrieval,
            adapter_result=adapter,
            context=context,
            index=index,
            manifest=manifest,
            latency_ms=0.0,
        )
        return query, retrieval, context, adapter, trace
    raise RagRuntimeError(
        f"no answered positive query found in first {min(len(chunks), POSITIVE_SEARCH_LIMIT)} canonical chunks"
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve(strict=True)
    subject_sha = _require_git_sha(args.subject_sha)
    output_path = args.output.resolve(strict=False)
    runtime_root = repo_root / RUNTIME_RELATIVE

    if not (repo_root / ".git").exists():
        raise RagRuntimeError("repo root is not a Git checkout")
    if output_path.exists() or output_path.is_symlink():
        raise RagRuntimeError("evidence output must be a fresh path")
    if runtime_root.exists() or runtime_root.is_symlink():
        raise RagRuntimeError(".runtime/llm-rag must not exist before clean-checkout runtime")
    head = _run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
    if head != subject_sha:
        raise RagRuntimeError("subject SHA does not match checked-out Git HEAD")
    dirty = _run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=repo_root).stdout
    if dirty.strip():
        raise RagRuntimeError("tracked checkout must be clean before RAG runtime")

    runtime_root.mkdir(parents=True, exist_ok=False)
    paths = {
        "corpus_snapshot": runtime_root / "corpus-snapshot.json",
        "chunk_manifest": runtime_root / "chunk-manifest.json",
        "retrieval_index": runtime_root / "retrieval-index.json",
        "runtime_config": runtime_root / "runtime-config.json",
        "positive_retrieval": runtime_root / "positive-retrieval.json",
        "positive_context": runtime_root / "positive-context.json",
        "positive_adapter": runtime_root / "positive-adapter.json",
        "positive_trace": runtime_root / "positive-trace.json",
        "no_result_retrieval": runtime_root / "no-result-retrieval.json",
        "no_result_context": runtime_root / "no-result-context.json",
        "no_result_adapter": runtime_root / "no-result-adapter.json",
        "no_result_trace": runtime_root / "no-result-trace.json",
        "evaluation": runtime_root / "eval-report.json",
        "prompt_release": runtime_root / "prompt-release.json",
    }
    eval_cases_path = repo_root / "labs" / "llm-rag" / "data" / "eval-cases.json"

    artifacts: dict[str, dict[str, Any]] = {}
    cleanup_verified = False
    lifecycle: dict[str, Any] = {}
    failure: str | None = None

    try:
        snapshot = build_corpus_snapshot(
            repo_root=repo_root,
            source_revision=subject_sha,
        )
        corpus_snapshot_id = _require_sha256(
            snapshot.get("corpus_snapshot_id"), "corpus_snapshot_id"
        )
        _write_artifact(
            name="corpus_snapshot",
            path=paths["corpus_snapshot"],
            value=snapshot,
            artifacts=artifacts,
        )

        manifest = build_chunk_manifest(repo_root=repo_root, snapshot=snapshot)
        chunk_manifest_id = _require_sha256(
            manifest.get("chunk_manifest_id"), "chunk_manifest_id"
        )
        if manifest.get("corpus_snapshot_id") != corpus_snapshot_id:
            raise RagRuntimeError("chunk manifest is detached from corpus snapshot")
        chunks = manifest.get("chunks")
        if not isinstance(chunks, list) or not chunks:
            raise RagRuntimeError("chunk manifest does not contain canonical chunks")
        _write_artifact(
            name="chunk_manifest",
            path=paths["chunk_manifest"],
            value=manifest,
            artifacts=artifacts,
        )

        index = build_retrieval_index(manifest)
        validate_retrieval_index(index, manifest)
        retrieval_index_id = _require_sha256(
            index.get("retrieval_index_id"), "retrieval_index_id"
        )
        if index.get("chunk_manifest_id") != chunk_manifest_id:
            raise RagRuntimeError("retrieval index is detached from chunk manifest")
        _write_artifact(
            name="retrieval_index",
            path=paths["retrieval_index"],
            value=index,
            artifacts=artifacts,
        )

        runtime_config = build_runtime_config(
            generation=RUNTIME_GENERATION,
            implementation_revision=subject_sha,
        )
        validate_runtime_config(runtime_config)
        runtime_config_id = _require_sha256(
            runtime_config.get("runtime_config_id"), "runtime_config_id"
        )
        _write_artifact(
            name="runtime_config",
            path=paths["runtime_config"],
            value=runtime_config,
            artifacts=artifacts,
        )

        positive_query, positive_retrieval, positive_context, positive_adapter, positive_trace = (
            _positive_execution(
                chunks=chunks,
                manifest=manifest,
                index=index,
                runtime_config=runtime_config,
            )
        )
        positive_answer = positive_adapter["answer"]
        citation_ids = _citation_chunk_ids(positive_answer)
        manifest_chunk_ids = {chunk["chunk_id"] for chunk in chunks}
        if not citation_ids or not citation_ids.issubset(manifest_chunk_ids):
            raise RagRuntimeError("positive answer does not contain exact manifest citations")
        for name, value in (
            ("positive_retrieval", positive_retrieval),
            ("positive_context", positive_context),
            ("positive_adapter", positive_adapter),
            ("positive_trace", positive_trace),
        ):
            _write_artifact(name=name, path=paths[name], value=value, artifacts=artifacts)

        no_result_query = "xylophonic-quantum-zebra-7391"
        no_result_retrieval = retrieve(
            index=index,
            manifest=manifest,
            query=no_result_query,
            top_k=runtime_config["retrieval"]["top_k"],
            min_score=runtime_config["retrieval"]["min_score"],
        )
        if no_result_retrieval["status"] != "no_result":
            raise RagRuntimeError("nonsense query did not produce explicit no_result")
        no_result_context = build_grounded_context(
            no_result_retrieval,
            index=index,
            manifest=manifest,
            max_chars=runtime_config["context"]["max_chars"],
        )
        no_result_adapter = run_offline_adapter(
            retrieval_result=no_result_retrieval,
            index=index,
            manifest=manifest,
            runtime_config=runtime_config,
        )
        no_result_answer = no_result_adapter["answer"]
        if (
            no_result_answer["status"] != "abstained"
            or no_result_answer["abstention_reason"] != "retrieval_no_result"
            or no_result_answer["citations"]
        ):
            raise RagRuntimeError("no_result path did not produce exact citation-free abstention")
        no_result_trace = build_trace(
            runtime_config=runtime_config,
            retrieval_result=no_result_retrieval,
            adapter_result=no_result_adapter,
            context=no_result_context,
            index=index,
            manifest=manifest,
            latency_ms=0.0,
        )
        for name, value in (
            ("no_result_retrieval", no_result_retrieval),
            ("no_result_context", no_result_context),
            ("no_result_adapter", no_result_adapter),
            ("no_result_trace", no_result_trace),
        ):
            _write_artifact(name=name, path=paths[name], value=value, artifacts=artifacts)

        cases = _read_json_list(eval_cases_path)
        evaluation = run_eval_suite(
            cases=cases,
            manifest=manifest,
            index=index,
            runtime_config=runtime_config,
        )
        eval_report_id = _require_sha256(
            evaluation.get("eval_report_id"), "eval_report_id"
        )
        failed_case_ids = sorted(
            result["case_id"]
            for result in evaluation["results"]
            if result["case_passed"] is not True
        )
        if evaluation.get("suite_passed") is not True or failed_case_ids:
            raise RagRuntimeError(
                f"RAG hard evaluation failed: cases={failed_case_ids}, "
                f"thresholds={evaluation.get('threshold_failures')}"
            )
        result_by_case = {result["case_id"]: result for result in evaluation["results"]}
        security_cases = []
        for case in cases:
            if "security" not in case.get("slices", []):
                continue
            result = result_by_case[case["case_id"]]
            security_cases.append(
                {
                    "case_id": case["case_id"],
                    "attack_type": case["attack_type"],
                    "case_passed": result["case_passed"],
                }
            )
        direct = [
            item
            for item in security_cases
            if item["case_id"] == "security-direct-injection" and item["attack_type"] == "direct"
        ]
        if len(direct) != 1 or direct[0]["case_passed"] is not True:
            raise RagRuntimeError("required direct prompt-injection runtime case did not pass")
        _write_artifact(
            name="evaluation",
            path=paths["evaluation"],
            value=evaluation,
            artifacts=artifacts,
        )

        prompt_release = build_prompt_release(
            runtime_config=runtime_config,
            eval_report=evaluation,
            cases=cases,
            manifest=manifest,
            index=index,
        )
        prompt_release_id = _require_sha256(
            prompt_release.get("prompt_release_id"), "prompt_release_id"
        )
        for label, expected in (
            ("runtime_config_id", runtime_config_id),
            ("eval_report_id", eval_report_id),
            ("chunk_manifest_id", chunk_manifest_id),
            ("corpus_snapshot_id", corpus_snapshot_id),
            ("retrieval_index_id", retrieval_index_id),
            ("source_revision", subject_sha),
        ):
            if prompt_release.get(label) != expected:
                raise RagRuntimeError(f"prompt release does not bind exact {label}")
        _write_artifact(
            name="prompt_release",
            path=paths["prompt_release"],
            value=prompt_release,
            artifacts=artifacts,
        )

        lifecycle = {
            "snapshot_id": corpus_snapshot_id,
            "corpus_snapshot_id": corpus_snapshot_id,
            "chunk_manifest_id": chunk_manifest_id,
            "chunk_count": manifest["chunk_count"],
            "index_id": retrieval_index_id,
            "retrieval_index_id": retrieval_index_id,
            "runtime_config_id": runtime_config_id,
            "implementation_revision": subject_sha,
            "positive": {
                "query": positive_query,
                "retrieval_result_id": positive_retrieval["retrieval_result_id"],
                "answer_id": positive_answer["answer_id"],
                "trace_id": positive_trace["trace_id"],
                "citation_chunk_ids": sorted(citation_ids),
            },
            "no_result": {
                "query": no_result_query,
                "retrieval_result_id": no_result_retrieval["retrieval_result_id"],
                "status": no_result_retrieval["status"],
                "answer_status": no_result_answer["status"],
                "abstention_reason": no_result_answer["abstention_reason"],
                "trace_id": no_result_trace["trace_id"],
            },
            "evaluation": {
                "report_id": eval_report_id,
                "eval_report_id": eval_report_id,
                "suite_passed": True,
                "all_passed": True,
                "failed_count": 0,
                "security_case_ids": sorted(item["case_id"] for item in security_cases),
                "security_cases": sorted(security_cases, key=lambda item: item["case_id"]),
                "retrieved_context_attack_case_present": any(
                    item["attack_type"] == "indirect" for item in security_cases
                ),
            },
            "prompt_release_id": prompt_release_id,
        }
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        try:
            if runtime_root.exists() or runtime_root.is_symlink():
                cleanup = subprocess.run(
                    [
                        sys.executable,
                        "labs/llm-rag/scripts/cleanup_runtime.py",
                        "--runtime-root",
                        RUNTIME_RELATIVE.as_posix(),
                    ],
                    cwd=repo_root,
                    check=False,
                    capture_output=True,
                    text=True,
                    env={**os.environ, "PYTHONHASHSEED": "0"},
                )
                if cleanup.returncode != 0:
                    cleanup_error = (
                        f"cleanup returned {cleanup.returncode}: "
                        f"{(cleanup.stderr or cleanup.stdout or '')[-3000:]}"
                    )
                    failure = f"{failure}; {cleanup_error}" if failure else cleanup_error
                cleanup_verified = not runtime_root.exists() and not runtime_root.is_symlink()
            else:
                cleanup_verified = True
        finally:
            payload: dict[str, Any] = {
                "schema_version": 1,
                "evidence_generation": "rag-clean-checkout-runtime-v3",
                "subject_sha": subject_sha,
                "runtime_root": RUNTIME_RELATIVE.as_posix(),
                "lifecycle": lifecycle,
                "artifacts": artifacts,
                "cleanup_verified": cleanup_verified,
                "failure": failure,
                "proof_boundary": {
                    "retrieval": "deterministic-offline-bm25",
                    "generation": "bounded-extractive-ci-adapter",
                    "direct_prompt_injection_eval": "executed",
                    "retrieved_context_prompt_injection_eval": "not-present-in-current-runtime-case-set",
                    "external_api_key_required": False,
                    "semantic_vector_provider_claimed": False,
                    "production_serving_claimed": False,
                },
            }
            payload["all_passed"] = (
                failure is None
                and cleanup_verified
                and bool(lifecycle)
                and len(artifacts) == len(paths)
            )
            evidence = {
                **payload,
                "evidence_id": hashlib.sha256(_canonical_bytes(payload)).hexdigest(),
            }
            if not output_path.exists() and not output_path.is_symlink():
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(
                    json.dumps(evidence, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                    encoding="utf-8",
                )

    evidence = _read_json(output_path)
    if evidence.get("all_passed") is not True:
        raise RagRuntimeError("clean-checkout RAG evidence is not all-passed")
    return evidence


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        evidence = run(args)
    except (ContractError, RagRuntimeError, OSError, RuntimeError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "refused", "error": f"{type(exc).__name__}: {exc}"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    lifecycle = evidence["lifecycle"]
    print(
        json.dumps(
            {
                "status": "passed",
                "subject_sha": evidence["subject_sha"],
                "corpus_snapshot_id": lifecycle["corpus_snapshot_id"],
                "chunk_manifest_id": lifecycle["chunk_manifest_id"],
                "retrieval_index_id": lifecycle["retrieval_index_id"],
                "eval_report_id": lifecycle["evaluation"]["eval_report_id"],
                "prompt_release_id": lifecycle["prompt_release_id"],
                "answer_id": lifecycle["positive"]["answer_id"],
                "trace_id": lifecycle["positive"]["trace_id"],
                "cleanup_verified": evidence["cleanup_verified"],
                "evidence_id": evidence["evidence_id"],
                "output": args.output.as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
