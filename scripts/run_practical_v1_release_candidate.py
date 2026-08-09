from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


class ReleaseCandidateError(RuntimeError):
    pass


EXPECTED_COMPONENTS = ("core", "mlops", "rag", "identity")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Execute the exact-revision Practical v1 release-candidate gates by composing the "
            "existing core, MLOps, RAG and live Keycloak/agent runtime drivers."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--subject-sha", required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def _require_git_sha(value: str) -> str:
    text = value.strip()
    if len(text) != 40 or any(character not in "0123456789abcdef" for character in text):
        raise ReleaseCandidateError(
            "subject SHA must be a lowercase 40-character Git SHA-1"
        )
    return text


def _require_sha256(value: object, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise ReleaseCandidateError(f"{field} must be a lowercase SHA-256")
    return value


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseCandidateError(f"cannot read JSON artifact {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReleaseCandidateError(f"JSON artifact must be an object: {path}")
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
    env_extra: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if env_extra:
        env.update(env_extra)
    result = subprocess.run(
        list(command),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        raise ReleaseCandidateError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout tail:\n{(result.stdout or '')[-6000:]}\n"
            f"stderr tail:\n{(result.stderr or '')[-6000:]}"
        )
    return result


def _git(repo_root: Path, *args: str) -> str:
    return _run(["git", *args], cwd=repo_root).stdout.strip()


def _git_untracked(repo_root: Path) -> list[str]:
    text = _git(
        repo_root,
        "status",
        "--porcelain",
        "--untracked-files=all",
    )
    return sorted(line for line in text.splitlines() if line.strip())


def _validate_paths(
    repo_root: Path,
    work_root: Path,
    evidence_dir: Path,
    output: Path,
) -> tuple[Path, Path, Path, Path]:
    root = repo_root.resolve(strict=True)
    work = work_root.resolve(strict=False)
    evidence = evidence_dir.resolve(strict=False)
    final = output.resolve(strict=False)
    if not (root / ".git").exists():
        raise ReleaseCandidateError("repo root is not a Git checkout")
    for label, path in (("work root", work), ("evidence dir", evidence)):
        if path == root or root in path.parents:
            raise ReleaseCandidateError(f"{label} must be outside the Git checkout")
        if path.exists() or path.is_symlink():
            raise ReleaseCandidateError(f"{label} must be a fresh path: {path}")
    if final == work or work in final.parents:
        raise ReleaseCandidateError("final evidence output must be outside disposable work root")
    if final.exists() or final.is_symlink():
        raise ReleaseCandidateError("final evidence output must be a fresh path")
    if evidence == work or work in evidence.parents or evidence in work.parents:
        raise ReleaseCandidateError("evidence and disposable work roots must be disjoint")
    if final != evidence / "release-candidate.json":
        raise ReleaseCandidateError(
            "final evidence output must be <evidence-dir>/release-candidate.json"
        )
    return root, work, evidence, final


def _component_file(path: Path, name: str) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ReleaseCandidateError(f"component evidence is missing or unsafe: {path}")
    value = _read_json(path)
    return {
        "name": name,
        "path": path.name,
        "sha256": _sha256_file(path),
        "size_bytes": path.stat().st_size,
        "value": value,
    }


def _require_exact_subject(component: Mapping[str, Any], subject_sha: str, label: str) -> None:
    if component.get("subject_sha") != subject_sha:
        raise ReleaseCandidateError(f"{label} evidence belongs to another Git subject")


def _verify_core(value: Mapping[str, Any], subject_sha: str) -> dict[str, Any]:
    _require_exact_subject(value, subject_sha, "core")
    if value.get("all_passed") is not True:
        raise ReleaseCandidateError("core orchestrator evidence is not all-passed")
    if value.get("cleanup_verified") is not True:
        raise ReleaseCandidateError("core orchestrator cleanup is not verified")
    if value.get("worktree_verified") is not True:
        raise ReleaseCandidateError("core orchestrator worktree read-back is not verified")
    if value.get("stage_count") != value.get("expected_stage_count"):
        raise ReleaseCandidateError("core orchestrator did not execute the exact stage count")
    return {
        "evidence_id": _require_sha256(value.get("evidence_id"), "core evidence_id"),
        "stage_count": value["stage_count"],
        "cleanup_verified": True,
        "worktree_verified": True,
    }


def _verify_mlops(value: Mapping[str, Any], subject_sha: str) -> dict[str, Any]:
    _require_exact_subject(value, subject_sha, "MLOps")
    live = value.get("live_retraining")
    container = value.get("container_runtime")
    handoff = value.get("handoff")
    rollback = value.get("rollback")
    boundary = value.get("proof_boundary")
    if not all(isinstance(item, dict) for item in (live, container, handoff, rollback, boundary)):
        raise ReleaseCandidateError("MLOps chain evidence is structurally incomplete")
    if live.get("provider_stopped") is not True or live.get("replay_status") != "already_completed":
        raise ReleaseCandidateError("MLOps live retraining provider/replay evidence is incomplete")
    if container.get("input_mode") != "explicit-subjects":
        raise ReleaseCandidateError("MLOps post-retraining container did not use explicit subjects")
    if container.get("release_source") != "provided-release":
        raise ReleaseCandidateError("MLOps post-retraining container regenerated release lineage")
    if container.get("container_uid") != "10001" or container.get("cleanup_verified") is not True:
        raise ReleaseCandidateError("MLOps container runtime evidence is incomplete")
    if handoff.get("exact_live_tested_deployment_rebuilt") is not True:
        raise ReleaseCandidateError("MLOps handoff did not rebuild exact live-tested deployment")
    if rollback.get("stale_subject_refused") is not True:
        raise ReleaseCandidateError("MLOps rollback stale-subject refusal is missing")
    if rollback.get("canary_deployment_id") is not None or rollback.get("canary_basis_points") != 0:
        raise ReleaseCandidateError("MLOps rollback did not restore stable-only routing")
    if boundary.get("remote_oci_registry_claimed") is not False:
        raise ReleaseCandidateError("MLOps evidence overclaims remote OCI Registry")
    if boundary.get("production_platform_claimed") is not False:
        raise ReleaseCandidateError("MLOps evidence overclaims production platform")
    return {
        "evidence_id": _require_sha256(value.get("evidence_id"), "MLOps evidence_id"),
        "operation_id": _require_sha256(live.get("operation_id"), "MLOps operation_id"),
        "registry_version": str(live.get("registry_version")),
        "deployment_id": _require_sha256(
            container.get("deployment_id"),
            "MLOps deployment_id",
        ),
        "docker_image_id": container.get("docker_image_id"),
        "canary_routing_state_id": _require_sha256(
            handoff.get("canary_routing_state_id"),
            "MLOps canary routing state",
        ),
        "rollback_routing_state_id": _require_sha256(
            rollback.get("routing_state_id"),
            "MLOps rollback routing state",
        ),
    }


def _verify_rag(value: Mapping[str, Any], subject_sha: str) -> dict[str, Any]:
    _require_exact_subject(value, subject_sha, "RAG")
    if value.get("all_passed") is not True or value.get("cleanup_verified") is not True:
        raise ReleaseCandidateError("RAG runtime evidence is not all-passed/cleaned")
    if value.get("failure") is not None:
        raise ReleaseCandidateError("RAG runtime evidence records a failure")
    lifecycle = value.get("lifecycle")
    boundary = value.get("proof_boundary")
    if not isinstance(lifecycle, dict) or not isinstance(boundary, dict):
        raise ReleaseCandidateError("RAG runtime evidence is structurally incomplete")
    positive = lifecycle.get("positive")
    no_result = lifecycle.get("no_result")
    evaluation = lifecycle.get("evaluation")
    if not all(isinstance(item, dict) for item in (positive, no_result, evaluation)):
        raise ReleaseCandidateError("RAG lifecycle evidence is incomplete")
    if not positive.get("citation_chunk_ids"):
        raise ReleaseCandidateError("RAG answered evidence has no exact citations")
    if no_result.get("status") not in {"no_result", "abstained"}:
        raise ReleaseCandidateError("RAG no-result evidence is missing")
    if evaluation.get("all_passed") is not True or evaluation.get("failed_count") != 0:
        raise ReleaseCandidateError("RAG hard evaluation is not all-passed")
    security_cases = evaluation.get("security_cases")
    if not isinstance(security_cases, list):
        raise ReleaseCandidateError("RAG security case evidence is missing")
    direct_cases = [
        item
        for item in security_cases
        if isinstance(item, dict)
        and item.get("case_id") == "security-direct-injection"
        and item.get("attack_type") == "direct"
    ]
    if len(direct_cases) != 1 or direct_cases[0].get("case_passed") is not True:
        raise ReleaseCandidateError("RAG direct prompt-injection runtime case did not pass")
    if boundary.get("direct_prompt_injection_eval") != "executed":
        raise ReleaseCandidateError("RAG direct prompt-injection proof boundary mismatch")
    if (
        boundary.get("retrieved_context_prompt_injection_eval")
        != "not-present-in-current-runtime-case-set"
    ):
        raise ReleaseCandidateError("RAG retrieved-context injection proof boundary is ambiguous")
    if boundary.get("external_api_key_required") is not False:
        raise ReleaseCandidateError("RAG evidence unexpectedly requires external API key")
    if boundary.get("production_serving_claimed") is not False:
        raise ReleaseCandidateError("RAG evidence overclaims production serving")
    return {
        "evidence_id": _require_sha256(value.get("evidence_id"), "RAG evidence_id"),
        "snapshot_id": _require_sha256(lifecycle.get("snapshot_id"), "RAG snapshot_id"),
        "index_id": _require_sha256(lifecycle.get("index_id"), "RAG index_id"),
        "report_id": _require_sha256(evaluation.get("report_id"), "RAG report_id"),
        "prompt_release_id": _require_sha256(
            lifecycle.get("prompt_release_id"),
            "RAG prompt_release_id",
        ),
        "answer_id": _require_sha256(positive.get("answer_id"), "RAG answer_id"),
        "trace_id": _require_sha256(positive.get("trace_id"), "RAG trace_id"),
    }


def _verify_identity(value: Mapping[str, Any], subject_sha: str) -> dict[str, Any]:
    _require_exact_subject(value, subject_sha, "identity")
    if value.get("cleanup_verified") is not True:
        raise ReleaseCandidateError("live identity cleanup is not verified")
    keycloak = value.get("keycloak")
    pkce = value.get("pkce")
    service = value.get("service_account")
    rag = value.get("rag")
    agent = value.get("agent")
    negative = value.get("negative_authorization")
    boundary = value.get("proof_boundary")
    if not all(
        isinstance(item, dict)
        for item in (keycloak, pkce, service, rag, agent, negative, boundary)
    ):
        raise ReleaseCandidateError("live identity evidence is structurally incomplete")
    if keycloak.get("realm_import_live") is not True or keycloak.get("jwks_key_count", 0) < 1:
        raise ReleaseCandidateError("live Keycloak realm/JWKS evidence is incomplete")
    if pkce.get("pkce_method") != "S256":
        raise ReleaseCandidateError("live imported public-client PKCE policy is not S256")
    if pkce.get("authorization_code_exchange_executed") is not False:
        raise ReleaseCandidateError("identity evidence changed the bounded browser-flow claim")
    if service.get("audience") != ["knowledge-hub-api"]:
        raise ReleaseCandidateError("service-account token audience is not exact")
    if service.get("scope_present") is not True:
        raise ReleaseCandidateError("service-account token API scope is missing")
    if not {"rag.read", "agent.run", "agent.remediate"}.issubset(
        set(service.get("roles") or [])
    ):
        raise ReleaseCandidateError("service-account token API roles are incomplete")
    if rag.get("protected_status") != 200 or rag.get("answer_status") != "answered":
        raise ReleaseCandidateError("protected RAG live evidence is incomplete")
    if agent.get("disposition") != "approval_required":
        raise ReleaseCandidateError("protected agent plan is not approval_required")
    if agent.get("remediation_http_status") != 200 or agent.get("replay_http_status") != 200:
        raise ReleaseCandidateError("protected agent remediation/replay HTTP evidence is incomplete")
    if agent.get("service_after_remediation") != agent.get("service_after_replay"):
        raise ReleaseCandidateError("agent completed replay changed service state")
    expected_negative = {
        "missing_bearer": 401,
        "tampered_signature": 401,
        "wrong_audience": 401,
        "missing_scope": 403,
        "missing_agent_remediate_role": 403,
        "expired_token": 401,
    }
    for label, status in expected_negative.items():
        item = negative.get(label)
        if not isinstance(item, dict) or item.get("observed_http_status") != status:
            raise ReleaseCandidateError(f"identity negative variant {label} mismatch")
    if boundary.get("browser_authorization_code_exchange") != "not-executed":
        raise ReleaseCandidateError("identity proof boundary overclaims browser exchange")
    if boundary.get("production_identity_platform_claimed") is not False:
        raise ReleaseCandidateError("identity evidence overclaims production identity platform")
    return {
        "evidence_id": _require_sha256(
            value.get("evidence_id"),
            "identity evidence_id",
        ),
        "issuer": keycloak.get("issuer"),
        "local_keycloak_image_id": keycloak.get("local_image_id"),
        "rag_answer_id": _require_sha256(rag.get("answer_id"), "identity RAG answer_id"),
        "rag_trace_id": _require_sha256(rag.get("trace_id"), "identity RAG trace_id"),
        "plan_id": _require_sha256(agent.get("plan_id"), "identity agent plan_id"),
        "retrieval_context_id": _require_sha256(
            agent.get("retrieval_context_id"),
            "identity retrieval_context_id",
        ),
        "action_digest": _require_sha256(
            agent.get("action_digest"),
            "identity action_digest",
        ),
        "approval_id": _require_sha256(
            agent.get("approval_id"),
            "identity approval_id",
        ),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root, work_root, evidence_dir, output_path = _validate_paths(
        args.repo_root,
        args.work_root,
        args.evidence_dir,
        args.output,
    )
    subject_sha = _require_git_sha(args.subject_sha)
    if _git(repo_root, "rev-parse", "HEAD") != subject_sha:
        raise ReleaseCandidateError("subject SHA does not match checked-out Git HEAD")
    before_status = _git_untracked(repo_root)
    if before_status:
        raise ReleaseCandidateError(
            "release-candidate checkout must be completely clean before execution"
        )

    work_root.mkdir(parents=True, exist_ok=False)
    evidence_dir.mkdir(parents=True, exist_ok=False)
    core_work = work_root / "core"
    mlops_runtime = work_root / "mlops"
    core_evidence = evidence_dir / "core.json"
    mlops_evidence = evidence_dir / "mlops.json"
    rag_evidence = evidence_dir / "rag.json"
    identity_evidence = evidence_dir / "identity.json"
    registry_tracking_uri = "http://127.0.0.1:5057"

    components: dict[str, dict[str, Any]] = {}
    cleanup_verified = False
    repository_clean_after = False
    failure: str | None = None
    try:
        _run(
            [
                sys.executable,
                "scripts/practical_v1_core.py",
                "--repo-root",
                str(repo_root),
                "--work-root",
                str(core_work),
                "--evidence",
                str(core_evidence),
            ],
            cwd=repo_root,
        )
        components["core"] = _component_file(core_evidence, "core")
        core_summary = _verify_core(components["core"]["value"], subject_sha)

        mlops_runtime.mkdir(parents=True, exist_ok=False)
        _run(
            ["bash", "labs/mlops/scripts/run_registry_gate.sh"],
            cwd=repo_root,
            env_extra={
                "RUNTIME_DIR": str(mlops_runtime),
                "VENV_DIR": sys.prefix,
                "SUBJECT_SHA": subject_sha,
                "TRACKING_URI": registry_tracking_uri,
            },
        )
        _run(
            [
                sys.executable,
                "labs/mlops/scripts/run_post_retraining_runtime_chain.py",
                "--repo-root",
                str(repo_root),
                "--runtime-dir",
                str(mlops_runtime),
                "--subject-sha",
                subject_sha,
                "--sample-request",
                "labs/machine-learning/data/sample-request.json",
                "--tracking-uri",
                registry_tracking_uri,
                "--retraining-seed",
                "20260805",
                "--service-name",
                "knowledge-hub-churn-api",
                "--generation",
                "practical-v1-release-candidate-v1",
                "--canary-basis-points",
                "2500",
                "--container-host",
                "127.0.0.1",
                "--container-port",
                "18082",
                "--output",
                str(mlops_evidence),
            ],
            cwd=repo_root,
        )
        components["mlops"] = _component_file(mlops_evidence, "mlops")
        mlops_summary = _verify_mlops(components["mlops"]["value"], subject_sha)

        _run(
            [
                sys.executable,
                "labs/llm-rag/scripts/run_clean_checkout_runtime.py",
                "--repo-root",
                str(repo_root),
                "--subject-sha",
                subject_sha,
                "--output",
                str(rag_evidence),
            ],
            cwd=repo_root,
        )
        components["rag"] = _component_file(rag_evidence, "rag")
        rag_summary = _verify_rag(components["rag"]["value"], subject_sha)

        _run(
            [
                sys.executable,
                "labs/keycloak-ai-api/scripts/run_live_identity_gate.py",
                "--repo-root",
                str(repo_root),
                "--subject-sha",
                subject_sha,
                "--issuer",
                "http://127.0.0.1:8080/realms/knowledge-hub",
                "--api-host",
                "127.0.0.1",
                "--api-port",
                "18091",
                "--startup-timeout-seconds",
                "120",
                "--output",
                str(identity_evidence),
            ],
            cwd=repo_root,
        )
        components["identity"] = _component_file(identity_evidence, "identity")
        identity_summary = _verify_identity(
            components["identity"]["value"],
            subject_sha,
        )

        component_names = tuple(components)
        if component_names != EXPECTED_COMPONENTS:
            raise ReleaseCandidateError(
                f"release-candidate component order mismatch: {component_names}"
            )

        payload: dict[str, Any] = {
            "schema_version": 1,
            "release_candidate_generation": "practical-v1-release-candidate-v1",
            "subject_sha": subject_sha,
            "components": {
                name: {
                    "evidence_id": components[name]["value"]["evidence_id"],
                    "file_sha256": components[name]["sha256"],
                    "size_bytes": components[name]["size_bytes"],
                }
                for name in EXPECTED_COMPONENTS
            },
            "core": core_summary,
            "mlops": mlops_summary,
            "rag": rag_summary,
            "identity": identity_summary,
            "proof_boundary": {
                "machine_learning": "historical-runtime-plus-current-core-contracts",
                "mlops_new_model_container": "live-local-docker-http",
                "mlops_canary": "deterministic-routing-state-not-live-proxy",
                "rag": "deterministic-offline-extractive",
                "identity": "live-local-keycloak-service-account-path",
                "browser_authorization_code_exchange": "not-executed",
                "remote_oci_registry_claimed": False,
                "production_platform_claimed": False,
                "production_identity_claimed": False,
                "user_acceptance_claimed": False,
                "release_tag_created": False,
            },
        }
        release_candidate = {
            **payload,
            "release_candidate_id": hashlib.sha256(
                _canonical_bytes(payload)
            ).hexdigest(),
        }
        _atomic_write_json(output_path, release_candidate)
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        shutil.rmtree(mlops_runtime, ignore_errors=True)
        shutil.rmtree(core_work, ignore_errors=True)
        for runtime_path in (
            repo_root / ".runtime" / "llm-rag",
            repo_root / ".runtime" / "keycloak",
            repo_root / ".runtime" / "agent-ops",
        ):
            shutil.rmtree(runtime_path, ignore_errors=True)
        try:
            (repo_root / ".runtime").rmdir()
        except OSError:
            pass
        cleanup_verified = (
            not mlops_runtime.exists()
            and not core_work.exists()
            and not (repo_root / ".runtime" / "llm-rag").exists()
            and not (repo_root / ".runtime" / "keycloak").exists()
            and not (repo_root / ".runtime" / "agent-ops").exists()
        )
        try:
            after_status = _git_untracked(repo_root)
            repository_clean_after = after_status == before_status
        except Exception:
            repository_clean_after = False

        if output_path.exists() and output_path.is_file():
            final = _read_json(output_path)
            final["cleanup_verified"] = cleanup_verified
            final["repository_clean_after"] = repository_clean_after
            final["failure"] = failure
            final["all_passed"] = (
                failure is None
                and cleanup_verified
                and repository_clean_after
                and set(components) == set(EXPECTED_COMPONENTS)
            )
            final_payload = {
                key: value
                for key, value in final.items()
                if key not in {"release_candidate_id"}
            }
            final["release_candidate_id"] = hashlib.sha256(
                _canonical_bytes(final_payload)
            ).hexdigest()
            _atomic_write_json(output_path, final)

    final = _read_json(output_path)
    if final.get("all_passed") is not True:
        raise ReleaseCandidateError(
            "release-candidate evidence is not all-passed after cleanup/read-back"
        )
    return final


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        evidence = run(args)
    except (ReleaseCandidateError, OSError, RuntimeError, ValueError) as exc:
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
                "release_candidate_id": evidence["release_candidate_id"],
                "component_count": len(evidence["components"]),
                "cleanup_verified": evidence["cleanup_verified"],
                "repository_clean_after": evidence["repository_clean_after"],
                "release_tag_created": evidence["proof_boundary"]["release_tag_created"],
                "output": args.output.as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
