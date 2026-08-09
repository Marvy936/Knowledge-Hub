from __future__ import annotations

import argparse
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE = re.compile(r"^\s*(```|~~~)")
EXTERNAL_PREFIXES = (
    "http://",
    "https://",
    "mailto:",
    "tel:",
    "data:",
)
EXPECTED_IMPORTS = (
    "ml_lab",
    "mlops_lab",
    "knowledge_hub_rag",
    "agent_ops",
    "keycloak_ai_api",
)
FORBIDDEN_SUFFIXES = {
    ".db",
    ".sqlite",
    ".sqlite3",
    ".joblib",
    ".pkl",
    ".pickle",
    ".onnx",
    ".pt",
    ".pth",
}


class ValidationError(RuntimeError):
    pass


def _git_lines(repo_root: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValidationError(
            f"git {' '.join(args)} failed: {result.stderr.strip() or result.stdout.strip()}"
        )
    return [line for line in result.stdout.splitlines() if line]


def _tracked_files(repo_root: Path) -> list[Path]:
    return [repo_root / item for item in _git_lines(repo_root, "ls-files")]


def _markdown_targets(path: Path) -> list[str]:
    targets: list[str] = []
    in_fence = False
    fence_marker: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        match = FENCE.match(raw_line)
        if match:
            marker = match.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = None
            continue
        if in_fence:
            continue
        for match in MARKDOWN_LINK.finditer(raw_line):
            target = match.group(1).strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1].strip()
            if " \"" in target:
                target = target.split(" \"", 1)[0].strip()
            if " '" in target:
                target = target.split(" '", 1)[0].strip()
            targets.append(target)
    return targets


def _validate_markdown_links(repo_root: Path, tracked: list[Path]) -> list[str]:
    errors: list[str] = []
    markdown_files = [path for path in tracked if path.suffix.lower() == ".md"]
    for path in markdown_files:
        for raw_target in _markdown_targets(path):
            if not raw_target or raw_target.startswith("#"):
                continue
            lowered = raw_target.lower()
            if lowered.startswith(EXTERNAL_PREFIXES):
                continue
            target = unquote(raw_target.split("#", 1)[0].split("?", 1)[0]).strip()
            if not target:
                continue
            candidate = (
                repo_root / target.lstrip("/")
                if target.startswith("/")
                else path.parent / target
            )
            try:
                resolved = candidate.resolve(strict=False)
                resolved.relative_to(repo_root)
            except ValueError:
                errors.append(f"{path.relative_to(repo_root)} -> path escapes repo: {raw_target}")
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(repo_root)} -> missing target: {raw_target}")
    return errors


def _validate_json(repo_root: Path, tracked: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in tracked:
        relative = path.relative_to(repo_root)
        if path.suffix.lower() != ".json" or not relative.parts or relative.parts[0] != "labs":
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{relative}: invalid JSON: {exc}")
    return errors


def _validate_no_tracked_runtime_artifacts(repo_root: Path, tracked: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in tracked:
        relative = path.relative_to(repo_root)
        lowered_parts = {part.lower() for part in relative.parts}
        if ".runtime" in lowered_parts:
            errors.append(f"tracked runtime path is forbidden: {relative}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"tracked runtime/model artifact is forbidden: {relative}")
    return errors


def _validate_imports() -> list[str]:
    errors: list[str] = []
    for module in EXPECTED_IMPORTS:
        try:
            importlib.import_module(module)
        except Exception as exc:  # validation must report the exact package boundary
            errors.append(f"cannot import {module}: {type(exc).__name__}: {exc}")
    return errors


def validate(repo_root: Path) -> dict[str, object]:
    resolved_root = repo_root.resolve(strict=True)
    if not (resolved_root / ".git").exists():
        raise ValidationError(f"repo root is not a Git checkout: {resolved_root}")
    tracked = _tracked_files(resolved_root)
    errors = [
        *_validate_markdown_links(resolved_root, tracked),
        *_validate_json(resolved_root, tracked),
        *_validate_no_tracked_runtime_artifacts(resolved_root, tracked),
        *_validate_imports(),
    ]
    report = {
        "status": "passed" if not errors else "failed",
        "tracked_file_count": len(tracked),
        "markdown_file_count": sum(1 for path in tracked if path.suffix.lower() == ".md"),
        "json_file_count": sum(
            1
            for path in tracked
            if path.suffix.lower() == ".json"
            and path.relative_to(resolved_root).parts
            and path.relative_to(resolved_root).parts[0] == "labs"
        ),
        "validated_imports": list(EXPECTED_IMPORTS),
        "errors": errors,
    }
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate Practical v1 repository links, JSON, imports and artifact hygiene."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        report = validate(args.repo_root)
    except (OSError, ValidationError) as exc:
        report = {"status": "failed", "errors": [str(exc)]}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
