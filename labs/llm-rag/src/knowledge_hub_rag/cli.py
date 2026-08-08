from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .answers import build_answer_envelope, validate_answer_envelope
from .binding import verify_chunk_manifest_rebuild
from .contracts import (
    ContractError,
    atomic_write_json,
    build_chunk_manifest,
    build_corpus_snapshot,
    read_json,
    verify_snapshot_bytes,
)
from .retrieval import (
    build_grounded_context,
    build_retrieval_index,
    retrieve,
    validate_retrieval_index,
    validate_retrieval_result,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="knowledge-hub-rag",
        description="Deterministic corpus, retrieval and grounded-answer contracts for the Knowledge Hub RAG flagship.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    snapshot = commands.add_parser("snapshot", help="Create an immutable Markdown corpus snapshot")
    snapshot.add_argument("--repo-root", type=Path, required=True)
    snapshot.add_argument("--source-revision", required=True)
    snapshot.add_argument("--include-root", action="append", dest="include_roots")
    snapshot.add_argument("--output", type=Path, required=True)

    verify = commands.add_parser("verify-snapshot", help="Read back exact corpus bytes")
    verify.add_argument("--repo-root", type=Path, required=True)
    verify.add_argument("--snapshot", type=Path, required=True)

    chunks = commands.add_parser("chunk", help="Build deterministic Markdown chunks")
    chunks.add_argument("--repo-root", type=Path, required=True)
    chunks.add_argument("--snapshot", type=Path, required=True)
    chunks.add_argument("--max-chars", type=int, default=1800)
    chunks.add_argument("--min-chars", type=int, default=240)
    chunks.add_argument("--output", type=Path, required=True)

    validate = commands.add_parser("validate-chunks", help="Rebuild and validate chunks against exact corpus bytes")
    validate.add_argument("--repo-root", type=Path, required=True)
    validate.add_argument("--manifest", type=Path, required=True)
    validate.add_argument("--snapshot", type=Path, required=True)

    index = commands.add_parser("index", help="Build a deterministic offline lexical retrieval index")
    index.add_argument("--manifest", type=Path, required=True)
    index.add_argument("--output", type=Path, required=True)

    search = commands.add_parser("retrieve", help="Run deterministic retrieval with explicit no-result state")
    search.add_argument("--manifest", type=Path, required=True)
    search.add_argument("--index", type=Path, required=True)
    search.add_argument("--query", required=True)
    search.add_argument("--top-k", type=int, default=5)
    search.add_argument("--min-score", type=float, default=0.01)
    search.add_argument("--context-max-chars", type=int, default=6000)
    search.add_argument("--output", type=Path, required=True)
    search.add_argument("--context-output", type=Path)

    answer = commands.add_parser("answer", help="Validate and record a structured answer or exact abstention")
    answer.add_argument("--manifest", type=Path, required=True)
    answer.add_argument("--index", type=Path, required=True)
    answer.add_argument("--retrieval", type=Path, required=True)
    answer.add_argument("--answer-text-file", type=Path)
    answer.add_argument("--cite-chunk-id", action="append", default=[])
    answer.add_argument("--prompt-generation", required=True)
    answer.add_argument("--output", type=Path, required=True)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "snapshot":
            snapshot = build_corpus_snapshot(
                repo_root=args.repo_root,
                source_revision=args.source_revision,
                include_roots=args.include_roots or ("docs",),
            )
            atomic_write_json(args.output, snapshot)
            result = {
                "status": "corpus_snapshot_recorded",
                "corpus_snapshot_id": snapshot["corpus_snapshot_id"],
                "file_count": snapshot["file_count"],
                "output": args.output.as_posix(),
            }
        elif args.command == "verify-snapshot":
            snapshot = read_json(args.snapshot)
            verify_snapshot_bytes(repo_root=args.repo_root, snapshot=snapshot)
            result = {
                "status": "corpus_snapshot_verified",
                "corpus_snapshot_id": snapshot["corpus_snapshot_id"],
                "file_count": snapshot["file_count"],
            }
        elif args.command == "chunk":
            manifest = build_chunk_manifest(
                repo_root=args.repo_root,
                snapshot=read_json(args.snapshot),
                max_chars=args.max_chars,
                min_chars=args.min_chars,
            )
            atomic_write_json(args.output, manifest)
            result = {
                "status": "chunk_manifest_recorded",
                "chunk_manifest_id": manifest["chunk_manifest_id"],
                "corpus_snapshot_id": manifest["corpus_snapshot_id"],
                "chunk_count": manifest["chunk_count"],
                "output": args.output.as_posix(),
            }
        elif args.command == "validate-chunks":
            manifest = read_json(args.manifest)
            snapshot = read_json(args.snapshot)
            verify_chunk_manifest_rebuild(
                repo_root=args.repo_root,
                manifest=manifest,
                snapshot=snapshot,
            )
            result = {
                "status": "chunk_manifest_valid",
                "chunk_manifest_id": manifest["chunk_manifest_id"],
                "corpus_snapshot_id": snapshot["corpus_snapshot_id"],
                "chunk_count": manifest["chunk_count"],
            }
        elif args.command == "index":
            manifest = read_json(args.manifest)
            index = build_retrieval_index(manifest)
            validate_retrieval_index(index, manifest)
            atomic_write_json(args.output, index)
            result = {
                "status": "retrieval_index_recorded",
                "retrieval_index_id": index["retrieval_index_id"],
                "chunk_manifest_id": index["chunk_manifest_id"],
                "document_count": index["document_count"],
                "output": args.output.as_posix(),
            }
        elif args.command == "retrieve":
            manifest = read_json(args.manifest)
            index = read_json(args.index)
            retrieval = retrieve(
                index=index,
                manifest=manifest,
                query=args.query,
                top_k=args.top_k,
                min_score=args.min_score,
            )
            validate_retrieval_result(retrieval, index=index, manifest=manifest)
            atomic_write_json(args.output, retrieval)
            context = build_grounded_context(
                retrieval,
                index=index,
                manifest=manifest,
                max_chars=args.context_max_chars,
            )
            if args.context_output is not None:
                atomic_write_json(args.context_output, context)
            result = {
                "status": retrieval["status"],
                "retrieval_result_id": retrieval["retrieval_result_id"],
                "query_id": retrieval["query"]["query_id"],
                "hit_count": retrieval["hit_count"],
                "context_status": context["status"],
                "output": args.output.as_posix(),
            }
        else:
            manifest = read_json(args.manifest)
            index = read_json(args.index)
            retrieval = read_json(args.retrieval)
            validate_retrieval_result(retrieval, index=index, manifest=manifest)
            if args.answer_text_file is None:
                answer_text = None
            else:
                try:
                    answer_text = args.answer_text_file.read_text(encoding="utf-8").strip()
                except FileNotFoundError as exc:
                    raise ContractError(f"answer text file does not exist: {args.answer_text_file}") from exc
            envelope = build_answer_envelope(
                retrieval_result=retrieval,
                index=index,
                manifest=manifest,
                answer_text=answer_text,
                cited_chunk_ids=args.cite_chunk_id,
                prompt_generation=args.prompt_generation,
            )
            validate_answer_envelope(
                envelope,
                retrieval_result=retrieval,
                index=index,
                manifest=manifest,
            )
            atomic_write_json(args.output, envelope)
            result = {
                "status": envelope["status"],
                "answer_id": envelope["answer_id"],
                "retrieval_result_id": envelope["retrieval_result_id"],
                "citation_count": len(envelope["citations"]),
                "output": args.output.as_posix(),
            }
    except ContractError as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
