from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .binding import validate_chunk_manifest_against_snapshot
from .contracts import (
    ContractError,
    atomic_write_json,
    build_chunk_manifest,
    build_corpus_snapshot,
    read_json,
    verify_snapshot_bytes,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="knowledge-hub-rag",
        description="Deterministic corpus and chunking contracts for the Knowledge Hub RAG flagship.",
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

    validate = commands.add_parser("validate-chunks", help="Validate chunks against an exact corpus snapshot")
    validate.add_argument("--manifest", type=Path, required=True)
    validate.add_argument("--snapshot", type=Path, required=True)

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
        else:
            manifest = read_json(args.manifest)
            snapshot = read_json(args.snapshot)
            validate_chunk_manifest_against_snapshot(manifest=manifest, snapshot=snapshot)
            result = {
                "status": "chunk_manifest_valid",
                "chunk_manifest_id": manifest["chunk_manifest_id"],
                "corpus_snapshot_id": snapshot["corpus_snapshot_id"],
                "chunk_count": manifest["chunk_count"],
            }
    except ContractError as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
