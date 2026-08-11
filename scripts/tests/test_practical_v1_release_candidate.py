from __future__ import annotations

from pathlib import Path

import pytest

from scripts import run_practical_v1_release_candidate as rc


def test_release_candidate_subject_requires_exact_git_sha1() -> None:
    assert rc._require_git_sha("a" * 40) == "a" * 40
    with pytest.raises(rc.ReleaseCandidateError, match="40-character"):
        rc._require_git_sha("a" * 39)
    with pytest.raises(rc.ReleaseCandidateError, match="40-character"):
        rc._require_git_sha("A" * 40)


def test_release_candidate_composes_canonical_identity_gate() -> None:
    assert (
        rc.IDENTITY_GATE_SCRIPT
        == "labs/keycloak-ai-api/scripts/run_live_identity_gate_canonical.py"
    )


def test_release_candidate_paths_are_external_disjoint_and_exact(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    work = tmp_path / "work"
    evidence = tmp_path / "evidence"
    output = evidence / "release-candidate.json"

    resolved = rc._validate_paths(repo, work, evidence, output)
    assert resolved == (
        repo.resolve(),
        work.resolve(),
        evidence.resolve(),
        output.resolve(),
    )

    with pytest.raises(rc.ReleaseCandidateError, match="outside the Git checkout"):
        rc._validate_paths(
            repo,
            repo / ".runtime" / "work",
            evidence,
            output,
        )

    with pytest.raises(rc.ReleaseCandidateError, match="must be <evidence-dir>"):
        rc._validate_paths(
            repo,
            work,
            evidence,
            tmp_path / "other.json",
        )


def test_core_summary_requires_cleanup_and_worktree_readback() -> None:
    value = {
        "subject_sha": "a" * 40,
        "all_passed": True,
        "cleanup_verified": True,
        "worktree_verified": True,
        "stage_count": 8,
        "expected_stage_count": 8,
        "evidence_id": "b" * 64,
    }
    summary = rc._verify_core(value, "a" * 40)
    assert summary["evidence_id"] == "b" * 64
    assert summary["stage_count"] == 8

    broken = dict(value)
    broken["worktree_verified"] = False
    with pytest.raises(rc.ReleaseCandidateError, match="worktree"):
        rc._verify_core(broken, "a" * 40)


def test_rag_summary_refuses_missing_hard_security_slice() -> None:
    value = {
        "subject_sha": "a" * 40,
        "all_passed": True,
        "cleanup_verified": True,
        "failure": None,
        "evidence_id": "b" * 64,
        "lifecycle": {
            "snapshot_id": "c" * 64,
            "index_id": "d" * 64,
            "prompt_release_id": "e" * 64,
            "positive": {
                "answer_id": "f" * 64,
                "trace_id": "1" * 64,
                "citation_chunk_ids": ["2" * 64],
            },
            "no_result": {"status": "no_result"},
            "evaluation": {
                "report_id": "3" * 64,
                "all_passed": True,
                "failed_count": 0,
                "required_security_slices": ["direct_prompt_injection"],
            },
        },
        "proof_boundary": {
            "external_api_key_required": False,
            "production_serving_claimed": False,
        },
    }
    with pytest.raises(rc.ReleaseCandidateError, match="security case evidence"):
        rc._verify_rag(value, "a" * 40)


def test_identity_summary_refuses_browser_exchange_overclaim() -> None:
    value = {
        "subject_sha": "a" * 40,
        "cleanup_verified": True,
        "evidence_id": "b" * 64,
        "keycloak": {
            "realm_import_live": True,
            "jwks_key_count": 1,
            "issuer": "http://127.0.0.1:8080/realms/knowledge-hub",
            "local_image_id": "sha256:" + "c" * 64,
        },
        "pkce": {
            "pkce_method": "S256",
            "authorization_code_exchange_executed": False,
        },
        "service_account": {
            "audience": ["knowledge-hub-api"],
            "scope_present": True,
            "roles": ["rag.read", "agent.run", "agent.remediate"],
        },
        "rag": {
            "protected_status": 200,
            "answer_status": "answered",
            "answer_id": "d" * 64,
            "trace_id": "e" * 64,
        },
        "agent": {
            "disposition": "approval_required",
            "remediation_http_status": 200,
            "replay_http_status": 200,
            "service_after_remediation": {"generation": 2, "status": "healthy", "restart_count": 1},
            "service_after_replay": {"generation": 2, "status": "healthy", "restart_count": 1},
            "plan_id": "f" * 64,
            "retrieval_context_id": "1" * 64,
            "action_digest": "2" * 64,
            "approval_id": "3" * 64,
        },
        "negative_authorization": {
            "missing_bearer": {"observed_http_status": 401},
            "tampered_signature": {"observed_http_status": 401},
            "wrong_audience": {"observed_http_status": 401},
            "missing_scope": {"observed_http_status": 403},
            "missing_agent_remediate_role": {"observed_http_status": 403},
            "expired_token": {"observed_http_status": 401},
        },
        "proof_boundary": {
            "browser_authorization_code_exchange": "executed",
            "production_identity_platform_claimed": False,
        },
    }
    with pytest.raises(rc.ReleaseCandidateError, match="browser exchange"):
        rc._verify_identity(value, "a" * 40)
