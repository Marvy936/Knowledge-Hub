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


class RagRuntimeError(RuntimeError):
    pass


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Execute the deterministic Knowledge Hub RAG corpus→index→query→eval→release "
            "lifecycle for the exact clean-checkout Git subject and emit bounded evidence."
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


def _atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


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


def _require_sha256(value: object, field: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise RagRuntimeError(f"{field} must be a lowercase SHA-256")
    return value


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


def _chunk_records(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for item in _walk(manifest):
        if not isinstance(item, dict):
            continue
        chunk_id = item.get("chunk_id")
        if isinstance(chunk_id, str) and SHA256_RE.fullmatch(chunk_id):
            candidates.append(item)
    unique: dict[str, dict[str, Any]] = {}
    for item in candidates:
        unique[item["chunk_id"]] = item
    if not unique:
        raise RagRuntimeError("corpus manifest does not expose any canonical chunk records")
    return [unique[key] for key in sorted(unique)]


def _query_from_chunk(chunk: Mapping[str, Any]) -> str:
    for field in ("text", "content", "body", "chunk_text"):
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


def _citation_chunk_ids(result: Mapping[str, Any]) -> set[str]:
    ids: set[str] = set()
    for item in _walk(result.get("citations", [])):
        if isinstance(item, dict):
            chunk_id = item.get("chunk_id")
            if isinstance(chunk_id, str):
                ids.add(chunk_id)
    return ids


def _artifact_identity(value: Mapping[str, Any], key: str, label: str) -> str:
    return _require_sha256(value.get(key), f"{label}.{key}")


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve(strict=True)
    subject_sha = _require_git_sha(args.subject_sha)
    output_path = args.output.resolve(strict=False)
    runtime_root = repo_root / ".runtime" / "llm-rag"

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
    manifest_path = runtime_root / "corpus-manifest.json"
    index_path = runtime_root / "index.json"
    config_path = runtime_root / "runtime-config.json"
    eval_path = runtime_root / "eval-report.json"
    release_path = runtime_root / "prompt-release.json"
    positive_path = runtime_root / "positive-query.json"
    no_result_path = runtime_root / "no-result-query.json"
    eval_cases = repo_root / "labs" / "llm-rag" / "data" / "eval-cases.json"

    artifacts: dict[str, dict[str, Any]] = {}
    cleanup_verified = False
    lifecycle: dict[str, Any] = {}
    failure: str | None = None
    try:
        _run(
            [
                sys.executable,
                "labs/llm-rag/scripts/build_corpus.py",
                "--repo",
                str(repo_root),
                "--revision",
                subject_sha,
                "--output",
                str(manifest_path),
            ],
            cwd=repo_root,
        )
        manifest = _read_json(manifest_path)
        if manifest.get("source_revision") != subject_sha:
            raise RagRuntimeError("corpus manifest source revision mismatch")
        snapshot_id = _artifact_identity(manifest, "snapshot_id", "manifest")
        chunks = _chunk_records(manifest)
        manifest_chunk_ids = {chunk["chunk_id"] for chunk in chunks}

        _run(
            [
                sys.executable,
                "labs/llm-rag/scripts/build_index.py",
                "--manifest",
                str(manifest_path),
                "--output",
                str(index_path),
            ],
            cwd=repo_root,
        )
        index = _read_json(index_path)
        index_id = _artifact_identity(index, "index_id", "index")
        if not _contains_exact(index, snapshot_id):
            raise RagRuntimeError("index does not bind exact corpus snapshot ID")

        _run(
            [
                sys.executable,
                "labs/llm-rag/scripts/build_runtime_config.py",
                "--implementation-revision",
                subject_sha,
                "--output",
                str(config_path),
            ],
            cwd=repo_root,
        )
        config = _read_json(config_path)
        runtime_config_id = _artifact_identity(config, "runtime_config_id", "runtime config")
        if not _contains_exact(config, subject_sha):
            raise RagRuntimeError("runtime config does not bind exact implementation revision")

        positive_query = _query_from_chunks(chunks)
        _run(
            [
                sys.executable,
                "labs/llm-rag/scripts/query.py",
                "--manifest",
                str(manifest_path),
                "--index",
                str(index_path),
                "--query",
                positive_query,
                "--output",
                str(positive_path),
            ],
            cwd=repo_root,
        )
        positive = _read_json(positive_path)
        if positive.get("status") != "answered":
            raise RagRuntimeError("derived positive query did not produce answered status")
        answer_id = _artifact_identity(positive, "answer_id", "positive answer")
        trace_id = _artifact_identity(positive, "trace_id", "positive answer")
        answer = positive.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            raise RagRuntimeError("answered result does not contain a non-empty answer")
        citation_ids = _citation_chunk_ids(positive)
        if not citation_ids:
            raise RagRuntimeError("answered result contains no canonical chunk citations")
        if not citation_ids.issubset(manifest_chunk_ids):
            raise RagRuntimeError("answered result cites chunk outside exact corpus manifest")

        no_result_query = "kh_no_result_9f3a0a6e_zzzz_nonexistent_subject"
        _run(
            [
                sys.executable,
                "labs/llm-rag/scripts/query.py",
                "--manifest",
                str(manifest_path),
                "--index",
                str(index_path),
                "--query",
                no_result_query,
                "--output",
                str(no_result_path),
            ],
            cwd=repo_root,
        )
        no_result = _read_json(no_result_path)
        if no_result.get("status") not in {"no_result", "abstained"}:
            raise RagRuntimeError("nonsense query did not produce explicit no-result/abstention")
        no_result_trace_id = _artifact_identity(no_result, "trace_id", "no-result answer")

        _run(
            [
                sys.executable,
                "labs/llm-rag/scripts/run_evaluation.py",
                "--manifest",
                str(manifest_path),
                "--index",
                str(index_path),
                "--runtime-config",
                str(config_path),
                "--cases",
                str(eval_cases),
                "--output",
                str(eval_path),
            ],
            cwd=repo_root,
        )
        evaluation = _read_json(eval_path)
        report_id = _artifact_identity(evaluation, "report_id", "evaluation")
        if evaluation.get("all_passed") is not True or evaluation.get("failed_count") != 0:
            raise RagRuntimeError("RAG hard evaluation is not all-passed")
        for slice_name in ("direct_prompt_injection", "retrieved_context_prompt_injection"):
            if not _contains_exact(evaluation, slice_name):
                raise RagRuntimeError(f"evaluation does not contain required slice {slice_name}")

        _run(
            [
                sys.executable,
                "labs/llm-rag/scripts/build_prompt_release.py",
                "--manifest",
                str(manifest_path),
                "--index",
                str(index_path),
                "--runtime-config",
                str(config_path),
                "--eval-report",
                str(eval_path),
                "--output",
                str(release_path),
            ],
            cwd=repo_root,
        )
        release = _read_json(release_path)
        prompt_release_id = _artifact_identity(release, "prompt_release_id", "prompt release")
        for label, value in (
            ("snapshot_id", snapshot_id),
            ("index_id", index_id),
            ("runtime_config_id", runtime_config_id),
            ("report_id", report_id),
        ):
            if not _contains_exact(release, value):
                raise RagRuntimeError(f"prompt release does not bind exact {label}")

        for name, path in (
            ("manifest", manifest_path),
            ("index", index_path),
            ("runtime_config", config_path),
            ("positive_query", positive_path),
            ("no_result_query", no_result_path),
            ("evaluation", eval_path),
            ("prompt_release", release_path),
        ):
            artifacts[name] = {
                "sha256": _sha256_file(path),
                "size_bytes": path.stat().st_size,
            }

        lifecycle = {
            "snapshot_id": snapshot_id,
            "chunk_count": len(manifest_chunk_ids),
            "index_id": index_id,
            "runtime_config_id": runtime_config_id,
            "implementation_revision": subject_sha,
            "positive": {
                "query": positive_query,
                "answer_id": answer_id,
                "trace_id": trace_id,
                "citation_chunk_ids": sorted(citation_ids),
            },
            "no_result": {
                "query": no_result_query,
                "status": no_result["status"],
                "trace_id": no_result_trace_id,
            },
            "evaluation": {
                "report_id": report_id,
                "all_passed": True,
                "failed_count": 0,
                "required_security_slices": [
                    "direct_prompt_injection",
                    "retrieved_context_prompt_injection",
                ],
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
                        ".runtime/llm-rag",
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
                "evidence_generation": "rag-clean-checkout-runtime-v2",
                "subject_sha": subject_sha,
                "runtime_root": ".runtime/llm-rag",
                "lifecycle": lifecycle,
                "artifacts": artifacts,
                "cleanup_verified": cleanup_verified,
                "failure": failure,
                "proof_boundary": {
                    "retrieval": "deterministic-offline",
                    "generation": "bounded-extractive-ci-adapter",
                    "external_api_key_required": False,
                    "semantic_vector_provider_claimed": False,
                    "production_serving_claimed": False,
                },
            }
            payload["all_passed"] = (
                failure is None
                and cleanup_verified
                and bool(lifecycle)
                and len(artifacts) == 7
            )
            evidence = {
                **payload,
                "evidence_id": hashlib.sha256(_canonical_bytes(payload)).hexdigest(),
            }
            if not output_path.exists() and not output_path.is_symlink():
                _atomic_write_json(output_path, evidence)

    evidence = _read_json(output_path)
    if evidence.get("all_passed") is not True:
        raise RagRuntimeError("clean-checkout RAG evidence is not all-passed")
    return evidence


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        evidence = run(args)
    except (RagRuntimeError, OSError, RuntimeError, ValueError) as exc:
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
                "snapshot_id": lifecycle["snapshot_id"],
                "index_id": lifecycle["index_id"],
                "report_id": lifecycle["evaluation"]["report_id"],
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
