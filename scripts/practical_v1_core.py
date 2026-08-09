from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Sequence

STAGES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "compileall",
        (
            "-m",
            "compileall",
            "-q",
            "scripts",
            "labs/machine-learning/src",
            "labs/mlops/src",
            "labs/llm-rag/src",
            "labs/agent-ops/src",
            "labs/keycloak-ai-api/src",
        ),
    ),
    ("repository-integrity", ("scripts/validate_practical_v1_repo.py", "--repo-root", ".")),
    ("machine-learning-contracts", ("-m", "pytest", "labs/machine-learning/tests", "-q")),
    ("mlops-contracts", ("-m", "pytest", "labs/mlops/tests", "-q")),
    ("llm-rag-contracts", ("-m", "pytest", "labs/llm-rag/tests", "-q")),
    ("agent-contracts", ("-m", "pytest", "labs/agent-ops/tests", "-q")),
    ("keycloak-ai-api-contracts", ("-m", "pytest", "labs/keycloak-ai-api/tests", "-q")),
)
EXPECTED_STAGE_COUNT = len(STAGES) + 1
MAX_CAPTURE_CHARS = 12_000


class CoreRunError(RuntimeError):
    pass


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def _canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _atomic_write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_bytes(_canonical_json_bytes(value))
    os.replace(temporary, path)


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise CoreRunError(
            f"git {' '.join(args)} failed: {result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout.strip()


def _validate_paths(
    repo_root: Path, work_root: Path, evidence_path: Path
) -> tuple[Path, Path, Path]:
    root = repo_root.resolve(strict=True)
    if not (root / ".git").exists():
        raise CoreRunError(f"repo root is not a Git checkout: {root}")
    work = work_root.resolve(strict=False)
    evidence = evidence_path.resolve(strict=False)
    if work == root or root in work.parents:
        allowed = root / ".runtime" / "practical-v1"
        try:
            work.relative_to(allowed)
        except ValueError as exc:
            raise CoreRunError(
                "work root inside repository must be below .runtime/practical-v1"
            ) from exc
    if evidence == work or work in evidence.parents:
        raise CoreRunError("evidence path must be outside disposable work root")
    if work.exists() or work.is_symlink():
        raise CoreRunError(f"work root already exists: {work}")
    if evidence.exists() or evidence.is_symlink():
        raise CoreRunError(f"evidence output already exists: {evidence}")
    return root, work, evidence


def _run_stage(
    *, name: str, command: Sequence[str], repo_root: Path
) -> dict[str, object]:
    started = time.monotonic()
    result = subprocess.run(
        list(command),
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONHASHSEED": "0"},
    )
    duration_ms = int((time.monotonic() - started) * 1000)
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    if stdout:
        print(stdout, end="" if stdout.endswith("\n") else "\n")
    if stderr:
        print(stderr, file=sys.stderr, end="" if stderr.endswith("\n") else "\n")
    return {
        "name": name,
        "command": list(command),
        "returncode": result.returncode,
        "passed": result.returncode == 0,
        "duration_ms": duration_ms,
        "stdout_sha256": _sha256_text(stdout),
        "stderr_sha256": _sha256_text(stderr),
        "stdout_tail": stdout[-MAX_CAPTURE_CHARS:],
        "stderr_tail": stderr[-MAX_CAPTURE_CHARS:],
    }


def _agent_eval_stage(repo_root: Path, work_root: Path) -> dict[str, object]:
    report_path = work_root / "agent-hard-eval.json"
    stage = _run_stage(
        name="agent-hard-evaluation",
        command=(
            sys.executable,
            "labs/agent-ops/scripts/run_evaluation.py",
            "--cases",
            "labs/agent-ops/data/eval-cases.json",
            "--output",
            str(report_path),
        ),
        repo_root=repo_root,
    )
    if not stage["passed"]:
        return stage
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        stage["passed"] = False
        stage["returncode"] = 4
        stage["evidence_error"] = f"cannot read agent hard-eval report: {exc}"
        return stage
    if not isinstance(report, dict) or report.get("all_passed") is not True:
        stage["passed"] = False
        stage["returncode"] = 4
        stage["evidence_error"] = "agent hard-eval report is not all_passed"
        return stage
    report_id = report.get("report_id")
    if not isinstance(report_id, str) or len(report_id) != 64:
        stage["passed"] = False
        stage["returncode"] = 4
        stage["evidence_error"] = "agent hard-eval report_id is invalid"
        return stage
    stage["agent_report_id"] = report_id
    stage["agent_case_count"] = report.get("case_count")
    stage["agent_passed_count"] = report.get("passed_count")
    return stage


def _build_report(
    *,
    subject_sha: str,
    python_version: str,
    stages: list[dict[str, object]],
    cleanup_verified: bool,
    preflight_error: str | None,
) -> dict[str, object]:
    expected_names = [name for name, _ in STAGES] + ["agent-hard-evaluation"]
    observed_names = [str(stage.get("name")) for stage in stages]
    all_passed = (
        preflight_error is None
        and len(stages) == EXPECTED_STAGE_COUNT
        and observed_names == expected_names
        and all(stage.get("passed") is True for stage in stages)
        and cleanup_verified
    )
    payload: dict[str, object] = {
        "schema_version": 1,
        "runner_generation": "practical-v1-core-v1",
        "subject_sha": subject_sha,
        "python_version": python_version,
        "expected_stage_count": EXPECTED_STAGE_COUNT,
        "stage_count": len(stages),
        "all_passed": all_passed,
        "cleanup_verified": cleanup_verified,
        "preflight_error": preflight_error,
        "stages": stages,
    }
    return {
        **payload,
        "evidence_id": hashlib.sha256(_canonical_json_bytes(payload)).hexdigest(),
    }


def run(repo_root: Path, work_root: Path, evidence_path: Path) -> dict[str, object]:
    stages: list[dict[str, object]] = []
    cleanup_verified = False
    preflight_error: str | None = None
    subject_sha = "unknown"
    root: Path | None = None
    work: Path | None = None
    evidence: Path | None = None

    try:
        root, work, evidence = _validate_paths(repo_root, work_root, evidence_path)
        subject_sha = _git(root, "rev-parse", "HEAD")
        if len(subject_sha) != 40 or any(ch not in "0123456789abcdef" for ch in subject_sha):
            raise CoreRunError("Git HEAD is not a lowercase 40-character SHA-1")
        tracked_changes = _git(root, "status", "--porcelain", "--untracked-files=no")
        if tracked_changes:
            raise CoreRunError("tracked worktree is not clean; refusing revision-bound evidence")
        work.mkdir(parents=True, exist_ok=False)

        for name, args in STAGES:
            stage = _run_stage(
                name=name,
                command=(sys.executable, *args),
                repo_root=root,
            )
            stages.append(stage)
            if stage["passed"] is not True:
                break
        else:
            stages.append(_agent_eval_stage(root, work))
    except Exception as exc:
        preflight_error = f"{type(exc).__name__}: {exc}"
        print(preflight_error, file=sys.stderr)
    finally:
        if work is not None:
            try:
                if work.exists() or work.is_symlink():
                    if work.is_symlink():
                        work.unlink()
                    else:
                        shutil.rmtree(work)
            except OSError as exc:
                cleanup_error = f"cleanup failed: {type(exc).__name__}: {exc}"
                preflight_error = (
                    cleanup_error
                    if preflight_error is None
                    else f"{preflight_error}; {cleanup_error}"
                )
            cleanup_verified = not work.exists() and not work.is_symlink()
        report = _build_report(
            subject_sha=subject_sha,
            python_version=sys.version.split()[0],
            stages=stages,
            cleanup_verified=cleanup_verified,
            preflight_error=preflight_error,
        )
        if evidence is None:
            evidence = evidence_path.resolve(strict=False)
        _atomic_write_json(evidence, report)

    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the deterministic Knowledge Hub Practical v1 offline/core contract lifecycle "
            "and emit bounded evidence."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        report = run(args.repo_root, args.work_root, args.evidence)
    except Exception as exc:
        print(
            f"orchestrator evidence write failed: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2
    print(
        json.dumps(
            {
                "status": "passed" if report["all_passed"] else "failed",
                "subject_sha": report["subject_sha"],
                "stage_count": report["stage_count"],
                "cleanup_verified": report["cleanup_verified"],
                "evidence_id": report["evidence_id"],
                "evidence": args.evidence.as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0 if report["all_passed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
