from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from scripts import finalize_practical_v1_release_evidence as finalizer


def _with_id(payload: dict[str, object], field: str) -> dict[str, object]:
    return {
        **payload,
        field: finalizer._sha256_bytes(finalizer._canonical_bytes(payload)),
    }


def _release_candidate(subject: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "subject_sha": subject,
        "all_passed": True,
        "cleanup_verified": True,
        "repository_clean_after": True,
        "components": {
            "core": {"evidence_id": "1" * 64},
            "mlops": {"evidence_id": "2" * 64},
            "rag": {"evidence_id": "3" * 64},
            "identity": {"evidence_id": "4" * 64},
        },
        "proof_boundary": {
            "release_tag_created": False,
            "user_acceptance_claimed": False,
        },
        "release_candidate_id": "a" * 64,
    }


def _dependencies(subject: str) -> dict[str, object]:
    packages = [
        {"name": "knowledge-hub-bounded-ops-agent", "version": "0.1.0"},
        {"name": "knowledge-hub-keycloak-ai-api", "version": "0.1.0"},
        {"name": "knowledge-hub-ml-flagship-lab", "version": "0.1.0"},
        {"name": "knowledge-hub-mlops-flagship-lab", "version": "0.8.0"},
        {"name": "knowledge-hub-rag-flagship-lab", "version": "0.3.0"},
        {"name": "pip", "version": "26.0.1"},
    ]
    payload: dict[str, object] = {
        "schema_version": 1,
        "subject_sha": subject,
        "python_version": "3.12.12",
        "python_executable": "/tmp/venv/bin/python",
        "pip_version": "26.0.1",
        "packages": packages,
    }
    return _with_id(payload, "dependency_resolution_id")


def _workflow(subject: str) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": 1,
        "subject_sha": subject,
        "workflow_name": "Practical v1 release evidence",
        "run_id": 123456789,
        "run_attempt": 1,
        "event_name": "workflow_dispatch",
        "repository": "Marvy936/Knowledge-Hub",
        "github_sha": subject,
        "ref": "refs/heads/main",
        "run_url": "https://github.com/Marvy936/Knowledge-Hub/actions/runs/123456789",
    }
    return _with_id(payload, "workflow_provenance_id")


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def test_final_release_evidence_binds_candidate_dependencies_and_run(tmp_path: Path) -> None:
    subject = "b" * 40
    rc_path = tmp_path / "release-candidate.json"
    dependency_path = tmp_path / "dependency-resolution.json"
    workflow_path = tmp_path / "workflow-provenance.json"
    output = tmp_path / "release-evidence.json"
    _write(rc_path, _release_candidate(subject))
    _write(dependency_path, _dependencies(subject))
    _write(workflow_path, _workflow(subject))

    evidence = finalizer.run(
        argparse.Namespace(
            release_candidate=rc_path,
            dependency_resolution=dependency_path,
            workflow_provenance=workflow_path,
            subject_sha=subject,
            output=output,
        )
    )

    assert evidence["subject_sha"] == subject
    assert evidence["release_candidate"]["release_candidate_id"] == "a" * 64
    assert evidence["workflow_provenance"]["run_id"] == 123456789
    assert evidence["proof_boundary"]["release_tag_created"] is False
    assert evidence["proof_boundary"]["user_acceptance_claimed"] is False
    assert len(evidence["release_evidence_id"]) == 64
    assert output.is_file()


def test_dependency_resolution_refuses_missing_local_distribution() -> None:
    subject = "c" * 40
    value = _dependencies(subject)
    payload = {key: item for key, item in value.items() if key != "dependency_resolution_id"}
    payload["packages"] = [
        item
        for item in payload["packages"]
        if item["name"] != "knowledge-hub-keycloak-ai-api"
    ]
    broken = _with_id(payload, "dependency_resolution_id")
    with pytest.raises(finalizer.ReleaseEvidenceError, match="missing local packages"):
        finalizer._validate_dependency_resolution(broken, subject)


def test_workflow_provenance_refuses_nonpositive_run_id() -> None:
    subject = "d" * 40
    value = _workflow(subject)
    payload = {key: item for key, item in value.items() if key != "workflow_provenance_id"}
    payload["run_id"] = 0
    broken = _with_id(payload, "workflow_provenance_id")
    with pytest.raises(finalizer.ReleaseEvidenceError, match="run_id"):
        finalizer._validate_workflow_provenance(broken, subject)


def test_release_candidate_refuses_tag_or_user_acceptance_overclaim() -> None:
    subject = "e" * 40
    tagged = _release_candidate(subject)
    tagged["proof_boundary"] = {
        "release_tag_created": True,
        "user_acceptance_claimed": False,
    }
    with pytest.raises(finalizer.ReleaseEvidenceError, match="release tag"):
        finalizer._validate_release_candidate(tagged, subject)

    accepted = _release_candidate(subject)
    accepted["proof_boundary"] = {
        "release_tag_created": False,
        "user_acceptance_claimed": True,
    }
    with pytest.raises(finalizer.ReleaseEvidenceError, match="user acceptance"):
        finalizer._validate_release_candidate(accepted, subject)
