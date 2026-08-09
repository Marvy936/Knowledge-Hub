from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


class ReleaseEvidenceError(RuntimeError):
    pass


REQUIRED_LOCAL_DISTRIBUTIONS = {
    "knowledge-hub-ml-flagship-lab",
    "knowledge-hub-mlops-flagship-lab",
    "knowledge-hub-rag-flagship-lab",
    "knowledge-hub-bounded-ops-agent",
    "knowledge-hub-keycloak-ai-api",
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Bind an all-passed Practical v1 release candidate to exact dependency "
            "resolution and GitHub workflow-run provenance."
        )
    )
    parser.add_argument("--release-candidate", type=Path, required=True)
    parser.add_argument("--dependency-resolution", type=Path, required=True)
    parser.add_argument("--workflow-provenance", type=Path, required=True)
    parser.add_argument("--subject-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ReleaseEvidenceError(f"{label} must be a regular non-symlink JSON file")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseEvidenceError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReleaseEvidenceError(f"{label} must be a JSON object")
    return value


def _require_git_sha(value: str) -> str:
    text = value.strip()
    if len(text) != 40 or any(character not in "0123456789abcdef" for character in text):
        raise ReleaseEvidenceError("subject SHA must be a lowercase 40-character Git SHA-1")
    return text


def _require_sha256(value: object, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise ReleaseEvidenceError(f"{field} must be a lowercase SHA-256")
    return value


def _require_nonempty(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReleaseEvidenceError(f"{field} must be a non-empty string")
    return value.strip()


def _require_positive_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ReleaseEvidenceError(f"{field} must be a positive integer")
    return value


def _atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise ReleaseEvidenceError("release evidence output must be a fresh path")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _validate_release_candidate(value: Mapping[str, Any], subject_sha: str) -> str:
    if value.get("subject_sha") != subject_sha:
        raise ReleaseEvidenceError("release candidate belongs to another Git subject")
    if value.get("all_passed") is not True:
        raise ReleaseEvidenceError("release candidate is not all-passed")
    if value.get("cleanup_verified") is not True:
        raise ReleaseEvidenceError("release candidate cleanup is not verified")
    if value.get("repository_clean_after") is not True:
        raise ReleaseEvidenceError("release candidate worktree read-back is not clean")
    boundary = value.get("proof_boundary")
    if not isinstance(boundary, dict):
        raise ReleaseEvidenceError("release candidate proof boundary is missing")
    if boundary.get("release_tag_created") is not False:
        raise ReleaseEvidenceError("release candidate already claims a release tag")
    if boundary.get("user_acceptance_claimed") is not False:
        raise ReleaseEvidenceError("release candidate already claims user acceptance")
    components = value.get("components")
    if not isinstance(components, dict) or set(components) != {"core", "mlops", "rag", "identity"}:
        raise ReleaseEvidenceError("release candidate component inventory mismatch")
    return _require_sha256(value.get("release_candidate_id"), "release_candidate_id")


def _validate_dependency_resolution(value: Mapping[str, Any], subject_sha: str) -> str:
    if value.get("subject_sha") != subject_sha:
        raise ReleaseEvidenceError("dependency resolution belongs to another Git subject")
    if value.get("schema_version") != 1:
        raise ReleaseEvidenceError("dependency resolution schema version mismatch")
    _require_nonempty(value.get("python_version"), "dependency python_version")
    _require_nonempty(value.get("python_executable"), "dependency python_executable")
    _require_nonempty(value.get("pip_version"), "dependency pip_version")
    packages = value.get("packages")
    if not isinstance(packages, list) or not packages:
        raise ReleaseEvidenceError("dependency package resolution is empty")
    normalized: list[tuple[str, str]] = []
    for index, item in enumerate(packages):
        if not isinstance(item, dict):
            raise ReleaseEvidenceError(f"dependency package {index} is not an object")
        normalized.append(
            (
                _require_nonempty(item.get("name"), f"dependency package {index} name").lower(),
                _require_nonempty(item.get("version"), f"dependency package {index} version"),
            )
        )
    if normalized != sorted(normalized):
        raise ReleaseEvidenceError("dependency package resolution must be canonically sorted")
    resolved_names = {name for name, _ in normalized}
    if not REQUIRED_LOCAL_DISTRIBUTIONS.issubset(resolved_names):
        missing = sorted(REQUIRED_LOCAL_DISTRIBUTIONS - resolved_names)
        raise ReleaseEvidenceError(f"dependency resolution is missing local packages: {missing}")
    declared_id = _require_sha256(value.get("dependency_resolution_id"), "dependency_resolution_id")
    payload = {key: item for key, item in value.items() if key != "dependency_resolution_id"}
    expected = _sha256_bytes(_canonical_bytes(payload))
    if declared_id != expected:
        raise ReleaseEvidenceError("dependency_resolution_id does not match canonical payload")
    return declared_id


def _validate_workflow_provenance(value: Mapping[str, Any], subject_sha: str) -> str:
    if value.get("subject_sha") != subject_sha:
        raise ReleaseEvidenceError("workflow provenance belongs to another Git subject")
    if value.get("schema_version") != 1:
        raise ReleaseEvidenceError("workflow provenance schema version mismatch")
    if _require_nonempty(value.get("workflow_name"), "workflow_name") != "Practical v1 release evidence":
        raise ReleaseEvidenceError("unexpected workflow name")
    _require_positive_int(value.get("run_id"), "run_id")
    _require_positive_int(value.get("run_attempt"), "run_attempt")
    event_name = _require_nonempty(value.get("event_name"), "event_name")
    if event_name not in {"workflow_dispatch", "push", "pull_request"}:
        raise ReleaseEvidenceError("unsupported workflow event")
    _require_nonempty(value.get("repository"), "repository")
    _require_nonempty(value.get("run_url"), "run_url")
    github_sha = _require_nonempty(value.get("github_sha"), "github_sha")
    _require_git_sha(github_sha)
    declared_id = _require_sha256(value.get("workflow_provenance_id"), "workflow_provenance_id")
    payload = {key: item for key, item in value.items() if key != "workflow_provenance_id"}
    expected = _sha256_bytes(_canonical_bytes(payload))
    if declared_id != expected:
        raise ReleaseEvidenceError("workflow_provenance_id does not match canonical payload")
    return declared_id


def run(args: argparse.Namespace) -> dict[str, Any]:
    subject_sha = _require_git_sha(args.subject_sha)
    release_candidate_path = args.release_candidate.resolve(strict=True)
    dependency_path = args.dependency_resolution.resolve(strict=True)
    workflow_path = args.workflow_provenance.resolve(strict=True)
    output_path = args.output.resolve(strict=False)

    release_candidate = _read_json(release_candidate_path, "release candidate")
    dependencies = _read_json(dependency_path, "dependency resolution")
    workflow = _read_json(workflow_path, "workflow provenance")

    release_candidate_id = _validate_release_candidate(release_candidate, subject_sha)
    dependency_resolution_id = _validate_dependency_resolution(dependencies, subject_sha)
    workflow_provenance_id = _validate_workflow_provenance(workflow, subject_sha)

    payload: dict[str, Any] = {
        "schema_version": 1,
        "evidence_generation": "practical-v1-release-evidence-v1",
        "subject_sha": subject_sha,
        "release_candidate": {
            "release_candidate_id": release_candidate_id,
            "sha256": _sha256_file(release_candidate_path),
            "size_bytes": release_candidate_path.stat().st_size,
        },
        "dependency_resolution": {
            "dependency_resolution_id": dependency_resolution_id,
            "sha256": _sha256_file(dependency_path),
            "size_bytes": dependency_path.stat().st_size,
        },
        "workflow_provenance": {
            "workflow_provenance_id": workflow_provenance_id,
            "run_id": workflow["run_id"],
            "run_attempt": workflow["run_attempt"],
            "event_name": workflow["event_name"],
            "run_url": workflow["run_url"],
            "sha256": _sha256_file(workflow_path),
            "size_bytes": workflow_path.stat().st_size,
        },
        "proof_boundary": {
            "release_tag_created": False,
            "user_acceptance_claimed": False,
            "workflow_run_bound": True,
            "dependency_resolution_bound": True,
        },
    }
    evidence = {
        **payload,
        "release_evidence_id": _sha256_bytes(_canonical_bytes(payload)),
    }
    _atomic_write_json(output_path, evidence)
    return evidence


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        evidence = run(args)
    except (ReleaseEvidenceError, OSError, RuntimeError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "refused", "error": f"{type(exc).__name__}: {exc}"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(
        json.dumps(
            {
                "status": "passed",
                "subject_sha": evidence["subject_sha"],
                "release_evidence_id": evidence["release_evidence_id"],
                "release_candidate_id": evidence["release_candidate"]["release_candidate_id"],
                "dependency_resolution_id": evidence["dependency_resolution"]["dependency_resolution_id"],
                "workflow_provenance_id": evidence["workflow_provenance"]["workflow_provenance_id"],
                "run_id": evidence["workflow_provenance"]["run_id"],
                "output": args.output.as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
