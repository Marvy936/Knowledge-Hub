from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

SCHEMA_VERSION = 1
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
DEFAULT_INCLUDE_ROOTS = ("docs",)
DEFAULT_MAX_CHARS = 1800
DEFAULT_MIN_CHARS = 240


class ContractError(RuntimeError):
    """Expected refusal at a corpus or chunking trust boundary."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"JSON file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON root must be an object: {path}")
    return value


def _require_revision(value: Any) -> str:
    if not isinstance(value, str) or not REVISION_RE.fullmatch(value):
        raise ContractError("source_revision must be an exact lowercase 40-hex Git commit")
    return value


def _require_sha256(value: Any, field: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ContractError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value.strip()


def _relative_posix(path: Path, repo_root: Path) -> str:
    try:
        relative = path.resolve(strict=True).relative_to(repo_root.resolve(strict=True))
    except ValueError as exc:
        raise ContractError(f"path escapes repository root: {path}") from exc
    return relative.as_posix()


def _validate_source_file(path: Path, repo_root: Path) -> str:
    if path.is_symlink():
        raise ContractError(f"symlinked corpus file is forbidden: {path}")
    if not path.is_file():
        raise ContractError(f"corpus subject is not a regular file: {path}")
    if path.suffix.lower() != ".md":
        raise ContractError(f"non-Markdown corpus file is forbidden: {path}")
    return _relative_posix(path, repo_root)


def discover_markdown_files(
    *, repo_root: Path, include_roots: Iterable[str] = DEFAULT_INCLUDE_ROOTS
) -> list[Path]:
    root = repo_root.resolve(strict=True)
    discovered: dict[str, Path] = {}
    resolved_roots = list(include_roots)
    if not resolved_roots:
        raise ContractError("at least one include root is required")

    for include_root in resolved_roots:
        if not isinstance(include_root, str) or not include_root.strip():
            raise ContractError("include roots must be non-empty relative paths")
        candidate = (root / include_root).resolve(strict=True)
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ContractError(f"include root escapes repository: {include_root}") from exc
        if not candidate.is_dir():
            raise ContractError(f"include root is not a directory: {include_root}")
        for path in candidate.rglob("*.md"):
            relative = _validate_source_file(path, root)
            if relative.startswith("labs/") or "/.runtime/" in f"/{relative}/":
                raise ContractError(f"runtime or lab output is forbidden in corpus: {relative}")
            discovered[relative] = path

    if not discovered:
        raise ContractError("corpus discovery produced no Markdown files")
    return [discovered[key] for key in sorted(discovered)]


def build_corpus_snapshot(
    *,
    repo_root: Path,
    source_revision: str,
    include_roots: Iterable[str] = DEFAULT_INCLUDE_ROOTS,
) -> dict[str, Any]:
    revision = _require_revision(source_revision)
    root = repo_root.resolve(strict=True)
    files = []
    for path in discover_markdown_files(repo_root=root, include_roots=include_roots):
        relative = _relative_posix(path, root)
        data = path.read_bytes()
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ContractError(f"corpus Markdown is not UTF-8: {relative}") from exc
        files.append(
            {
                "path": relative,
                "sha256": sha256_bytes(data),
                "size_bytes": len(data),
            }
        )

    payload = {
        "schema_version": SCHEMA_VERSION,
        "source_revision": revision,
        "include_roots": sorted(set(include_roots)),
        "file_count": len(files),
        "files": files,
    }
    return {
        **payload,
        "corpus_snapshot_id": sha256_bytes(canonical_json_bytes(payload)),
    }


def validate_corpus_snapshot(value: Mapping[str, Any]) -> None:
    expected = {
        "schema_version",
        "source_revision",
        "include_roots",
        "file_count",
        "files",
        "corpus_snapshot_id",
    }
    if set(value) != expected:
        raise ContractError("corpus snapshot keys mismatch")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("corpus snapshot schema_version must equal 1")
    _require_revision(value.get("source_revision"))
    identifier = _require_sha256(value.get("corpus_snapshot_id"), "corpus_snapshot_id")
    roots = value.get("include_roots")
    files = value.get("files")
    if not isinstance(roots, list) or not roots or not all(
        isinstance(item, str) and item for item in roots
    ):
        raise ContractError("include_roots must be a non-empty string list")
    if roots != sorted(set(roots)):
        raise ContractError("include_roots must be sorted and unique")
    if not isinstance(files, list) or not files:
        raise ContractError("files must be a non-empty list")
    if value.get("file_count") != len(files):
        raise ContractError("file_count does not match files")

    previous_path = None
    for index, item in enumerate(files):
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "size_bytes"}:
            raise ContractError(f"files[{index}] has invalid structure")
        path = _require_nonempty_string(item.get("path"), f"files[{index}].path")
        if path.startswith("/") or ".." in Path(path).parts or not path.endswith(".md"):
            raise ContractError(f"files[{index}].path is not a safe Markdown path")
        if previous_path is not None and path <= previous_path:
            raise ContractError("files must be strictly path-sorted")
        previous_path = path
        _require_sha256(item.get("sha256"), f"files[{index}].sha256")
        if not isinstance(item.get("size_bytes"), int) or item["size_bytes"] < 0:
            raise ContractError(f"files[{index}].size_bytes must be non-negative")

    payload = {key: item for key, item in value.items() if key != "corpus_snapshot_id"}
    if sha256_bytes(canonical_json_bytes(payload)) != identifier:
        raise ContractError("corpus_snapshot_id does not match canonical payload")


def verify_snapshot_bytes(*, repo_root: Path, snapshot: Mapping[str, Any]) -> None:
    validate_corpus_snapshot(snapshot)
    root = repo_root.resolve(strict=True)
    for item in snapshot["files"]:
        path = root / item["path"]
        relative = _validate_source_file(path, root)
        if relative != item["path"]:
            raise ContractError(f"snapshot path resolution changed: {item['path']}")
        if path.stat().st_size != item["size_bytes"]:
            raise ContractError(f"snapshot size mismatch: {item['path']}")
        if sha256_file(path) != item["sha256"]:
            raise ContractError(f"snapshot digest mismatch: {item['path']}")


def _normalize_heading(text: str) -> str:
    return " ".join(text.strip().split())


def _split_markdown_sections(text: str) -> list[tuple[list[str], str]]:
    heading_stack: list[str] = []
    sections: list[tuple[list[str], list[str]]] = []
    current_lines: list[str] = []
    current_heading = list(heading_stack)
    in_fence = False
    fence_marker = ""

    def flush() -> None:
        nonlocal current_lines
        content = "\n".join(current_lines).strip()
        if content:
            sections.append((list(current_heading), current_lines.copy()))
        current_lines = []

    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            current_lines.append(line.rstrip())
            continue

        match = None if in_fence else HEADING_RE.match(line)
        if match:
            flush()
            level = len(match.group(1))
            heading = _normalize_heading(match.group(2))
            heading_stack = heading_stack[: level - 1]
            while len(heading_stack) < level - 1:
                heading_stack.append("")
            if len(heading_stack) == level - 1:
                heading_stack.append(heading)
            else:
                heading_stack[level - 1] = heading
            current_heading = [item for item in heading_stack if item]
            continue
        current_lines.append(line.rstrip())

    flush()
    return [
        (heading, "\n".join(lines).strip())
        for heading, lines in sections
        if "\n".join(lines).strip()
    ]


def _split_blocks(text: str) -> list[str]:
    lines = text.split("\n")
    blocks: list[str] = []
    current: list[str] = []
    in_fence = False
    fence_marker = ""

    def flush() -> None:
        nonlocal current
        block = "\n".join(current).strip()
        if block:
            blocks.append(block)
        current = []

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            current.append(line)
            continue
        if not in_fence and not line.strip():
            flush()
        else:
            current.append(line)
    flush()
    return blocks


def _hard_split(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    parts: list[str] = []
    remaining = text
    while len(remaining) > max_chars:
        split_at = remaining.rfind("\n", 0, max_chars + 1)
        if split_at < max_chars // 2:
            split_at = remaining.rfind(" ", 0, max_chars + 1)
        if split_at < max_chars // 2:
            split_at = max_chars
        part = remaining[:split_at].strip()
        if not part:
            split_at = max_chars
            part = remaining[:split_at]
        parts.append(part)
        remaining = remaining[split_at:].strip()
    if remaining:
        parts.append(remaining)
    return parts


def _pack_blocks(blocks: list[str], *, max_chars: int, min_chars: int) -> list[str]:
    expanded: list[str] = []
    for block in blocks:
        expanded.extend(_hard_split(block, max_chars))

    chunks: list[str] = []
    current = ""
    for block in expanded:
        candidate = block if not current else current + "\n\n" + block
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        current = block
    if current:
        chunks.append(current)

    if len(chunks) > 1 and len(chunks[-1]) < min_chars:
        merged = chunks[-2] + "\n\n" + chunks[-1]
        if len(merged) <= max_chars:
            chunks[-2:] = [merged]
    return chunks


def build_chunk_manifest(
    *,
    repo_root: Path,
    snapshot: Mapping[str, Any],
    max_chars: int = DEFAULT_MAX_CHARS,
    min_chars: int = DEFAULT_MIN_CHARS,
) -> dict[str, Any]:
    validate_corpus_snapshot(snapshot)
    verify_snapshot_bytes(repo_root=repo_root, snapshot=snapshot)
    if max_chars < 256:
        raise ContractError("max_chars must be at least 256")
    if min_chars < 0 or min_chars >= max_chars:
        raise ContractError("min_chars must be non-negative and smaller than max_chars")

    root = repo_root.resolve(strict=True)
    chunks: list[dict[str, Any]] = []
    for file_item in snapshot["files"]:
        path = root / file_item["path"]
        text = path.read_text(encoding="utf-8")
        file_ordinal = 0
        for heading_path, section_text in _split_markdown_sections(text):
            blocks = _split_blocks(section_text)
            for content in _pack_blocks(blocks, max_chars=max_chars, min_chars=min_chars):
                normalized_content = content.strip()
                if not normalized_content:
                    continue
                payload = {
                    "source_path": file_item["path"],
                    "source_sha256": file_item["sha256"],
                    "heading_path": heading_path,
                    "ordinal": file_ordinal,
                    "content_sha256": sha256_bytes(normalized_content.encode("utf-8")),
                    "char_count": len(normalized_content),
                }
                chunks.append(
                    {
                        **payload,
                        "chunk_id": sha256_bytes(canonical_json_bytes(payload)),
                        "content": normalized_content,
                    }
                )
                file_ordinal += 1

    if not chunks:
        raise ContractError("chunking produced no chunks")

    manifest_payload = {
        "schema_version": SCHEMA_VERSION,
        "corpus_snapshot_id": snapshot["corpus_snapshot_id"],
        "source_revision": snapshot["source_revision"],
        "chunking": {"max_chars": max_chars, "min_chars": min_chars},
        "chunk_count": len(chunks),
        "chunks": chunks,
    }
    return {
        **manifest_payload,
        "chunk_manifest_id": sha256_bytes(canonical_json_bytes(manifest_payload)),
    }


def validate_chunk_manifest(value: Mapping[str, Any]) -> None:
    expected = {
        "schema_version",
        "corpus_snapshot_id",
        "source_revision",
        "chunking",
        "chunk_count",
        "chunks",
        "chunk_manifest_id",
    }
    if set(value) != expected:
        raise ContractError("chunk manifest keys mismatch")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("chunk manifest schema_version must equal 1")
    _require_sha256(value.get("corpus_snapshot_id"), "corpus_snapshot_id")
    _require_revision(value.get("source_revision"))
    chunking = value.get("chunking")
    if not isinstance(chunking, dict) or set(chunking) != {"max_chars", "min_chars"}:
        raise ContractError("chunking config is invalid")
    max_chars = chunking.get("max_chars")
    min_chars = chunking.get("min_chars")
    if not isinstance(max_chars, int) or max_chars < 256:
        raise ContractError("chunking.max_chars is invalid")
    if not isinstance(min_chars, int) or min_chars < 0 or min_chars >= max_chars:
        raise ContractError("chunking.min_chars is invalid")

    chunks = value.get("chunks")
    if not isinstance(chunks, list) or not chunks:
        raise ContractError("chunks must be a non-empty list")
    if value.get("chunk_count") != len(chunks):
        raise ContractError("chunk_count does not match chunks")

    seen_ids: set[str] = set()
    previous_key: tuple[str, int] | None = None
    for index, chunk in enumerate(chunks):
        expected_chunk_keys = {
            "source_path",
            "source_sha256",
            "heading_path",
            "ordinal",
            "content_sha256",
            "char_count",
            "chunk_id",
            "content",
        }
        if not isinstance(chunk, dict) or set(chunk) != expected_chunk_keys:
            raise ContractError(f"chunks[{index}] has invalid structure")
        source_path = _require_nonempty_string(chunk.get("source_path"), "source_path")
        source_sha = _require_sha256(chunk.get("source_sha256"), "source_sha256")
        heading_path = chunk.get("heading_path")
        if not isinstance(heading_path, list) or not all(
            isinstance(item, str) and item for item in heading_path
        ):
            raise ContractError("heading_path must be a string list")
        ordinal = chunk.get("ordinal")
        if not isinstance(ordinal, int) or ordinal < 0:
            raise ContractError("ordinal must be a non-negative integer")
        key = (source_path, ordinal)
        if previous_key is not None and key <= previous_key:
            raise ContractError("chunks must be strictly source/ordinal sorted")
        previous_key = key
        content = _require_nonempty_string(chunk.get("content"), "content")
        if len(content) != chunk.get("char_count"):
            raise ContractError("char_count does not match content")
        if len(content) > max_chars:
            raise ContractError("chunk exceeds max_chars")
        content_sha = _require_sha256(chunk.get("content_sha256"), "content_sha256")
        if sha256_bytes(content.encode("utf-8")) != content_sha:
            raise ContractError("content_sha256 does not match content")
        payload = {
            "source_path": source_path,
            "source_sha256": source_sha,
            "heading_path": heading_path,
            "ordinal": ordinal,
            "content_sha256": content_sha,
            "char_count": chunk["char_count"],
        }
        chunk_id = _require_sha256(chunk.get("chunk_id"), "chunk_id")
        if sha256_bytes(canonical_json_bytes(payload)) != chunk_id:
            raise ContractError("chunk_id does not match canonical chunk metadata")
        if chunk_id in seen_ids:
            raise ContractError("chunk IDs must be unique")
        seen_ids.add(chunk_id)

    manifest_id = _require_sha256(value.get("chunk_manifest_id"), "chunk_manifest_id")
    payload = {key: item for key, item in value.items() if key != "chunk_manifest_id"}
    if sha256_bytes(canonical_json_bytes(payload)) != manifest_id:
        raise ContractError("chunk_manifest_id does not match canonical payload")
