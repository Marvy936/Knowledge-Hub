from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from mlops_lab.contracts import (
    ContractError,
    atomic_write_json,
    canonical_json_bytes,
    read_json,
    sha256_bytes,
)
from mlops_lab.post_retraining import validate_post_retraining_handoff
from mlops_lab.serving import (
    build_rollback_state,
    build_routing_state,
    route_request,
    validate_deployment_manifest,
    validate_routing_state,
)


class PostRetrainingChainError(RuntimeError):
    pass


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compose live controlled retraining, exact post-retraining containerized inference, "
            "immutable deployment handoff, deterministic canary routing and rollback evidence."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--subject-sha", required=True)
    parser.add_argument("--sample-request", type=Path, required=True)
    parser.add_argument("--tracking-uri", default="http://127.0.0.1:5057")
    parser.add_argument("--retraining-seed", type=int, default=20260805)
    parser.add_argument("--service-name", default="knowledge-hub-churn-api")
    parser.add_argument("--generation", default="post-retraining-live-v1")
    parser.add_argument("--canary-basis-points", type=int, default=2500)
    parser.add_argument("--container-host", default="127.0.0.1")
    parser.add_argument("--container-port", type=int, default=18082)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def _require_subject_sha(value: str) -> str:
    text = value.strip()
    if len(text) != 40 or any(character not in "0123456789abcdef" for character in text):
        raise PostRetrainingChainError(
            "subject SHA must be a lowercase 40-character Git SHA-1"
        )
    return text


def _require_sha256(value: object, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise PostRetrainingChainError(f"{field} must be a lowercase SHA-256")
    return value


def _require_nonempty(value: str, field: str) -> str:
    text = value.strip()
    if not text:
        raise PostRetrainingChainError(f"{field} must be a non-empty string")
    return text


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(command),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise PostRetrainingChainError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout tail:\n{(result.stdout or '')[-5000:]}\n"
            f"stderr tail:\n{(result.stderr or '')[-5000:]}"
        )
    return result


def _stdout_json(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    lines = [line for line in (result.stdout or "").splitlines() if line.strip()]
    if not lines:
        raise PostRetrainingChainError("command did not return JSON output")
    try:
        value = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise PostRetrainingChainError("command final stdout line is not JSON") from exc
    if not isinstance(value, dict):
        raise PostRetrainingChainError("command JSON output must be an object")
    return value


def _validate_component_lineage(
    *,
    retraining: Mapping[str, Any],
    container: Mapping[str, Any],
    deployment: Mapping[str, Any],
) -> None:
    validate_deployment_manifest(deployment)
    expected_pairs = {
        "candidate_id": retraining["retraining"]["candidate_id"],
        "release_id": retraining["retraining"]["release_id"],
        "registry_evidence_id": retraining["retraining"]["registry_evidence_id"],
        "registry_version": retraining["retraining"]["registry_version"],
        "model_sha256": retraining["retraining"]["model_sha256"],
    }
    for field, expected in expected_pairs.items():
        if container.get(field) != expected:
            raise PostRetrainingChainError(
                f"container {field} does not match live retraining subject"
            )
    if container.get("input_mode") != "explicit-subjects":
        raise PostRetrainingChainError("post-retraining container did not use explicit subjects")
    if container.get("release_source") != "provided-release":
        raise PostRetrainingChainError("post-retraining container regenerated release lineage")
    if deployment["deployment_id"] != container.get("deployment_id"):
        raise PostRetrainingChainError("container deployment read-back mismatch")
    if deployment["candidate_id"] != expected_pairs["candidate_id"]:
        raise PostRetrainingChainError("deployment candidate does not match retraining subject")
    if deployment["release_id"] != expected_pairs["release_id"]:
        raise PostRetrainingChainError("deployment release does not match retraining subject")
    if deployment["model"]["registry_evidence_id"] != expected_pairs["registry_evidence_id"]:
        raise PostRetrainingChainError("deployment Registry evidence does not match retraining subject")
    if deployment["model"]["registry_version"] != expected_pairs["registry_version"]:
        raise PostRetrainingChainError("deployment Registry version does not match retraining subject")
    if deployment["model"]["sha256"] != expected_pairs["model_sha256"]:
        raise PostRetrainingChainError("deployment model digest does not match retraining subject")
    if deployment["image"]["digest"] != container.get("docker_image_id"):
        raise PostRetrainingChainError("deployment image digest does not match tested container image")
    if deployment["image"]["reference"] != container.get("image_reference"):
        raise PostRetrainingChainError("deployment image reference does not match tested container image")


def _find_route_probe(
    *,
    routing_state: Mapping[str, Any],
    deployments: Mapping[str, Mapping[str, Any]],
    selected_role: str,
) -> dict[str, Any]:
    for index in range(20_000):
        result = route_request(
            routing_state=routing_state,
            deployments=deployments,
            routing_key=f"post-retraining-probe-{index}",
        )
        if result["selected_role"] == selected_role:
            return result
    raise PostRetrainingChainError(
        f"could not find deterministic {selected_role} routing probe"
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve(strict=True)
    runtime_dir = args.runtime_dir.resolve(strict=True)
    sample_request = args.sample_request.resolve(strict=True)
    output_path = args.output.resolve(strict=False)
    subject_sha = _require_subject_sha(args.subject_sha)
    service_name = _require_nonempty(args.service_name, "service_name")
    generation = _require_nonempty(args.generation, "generation")

    if output_path.exists() or output_path.is_symlink():
        raise PostRetrainingChainError("chain evidence output must be a fresh path")
    if sample_request.is_symlink() or not sample_request.is_file():
        raise PostRetrainingChainError("sample request must be a regular non-symlink file")
    if args.retraining_seed < 0:
        raise PostRetrainingChainError("retraining seed must be non-negative")
    if not 1 <= args.canary_basis_points <= 9999:
        raise PostRetrainingChainError(
            "canary basis points must be between 1 and 9999 so stable and canary routes both exist"
        )
    if args.container_host not in {"127.0.0.1", "localhost"}:
        raise PostRetrainingChainError("container host must be loopback")
    if not 1 <= args.container_port <= 65535:
        raise PostRetrainingChainError("container port must be between 1 and 65535")
    if _run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip() != subject_sha:
        raise PostRetrainingChainError("subject SHA does not match checked-out Git HEAD")

    chain_root = runtime_dir / "post-retraining-runtime-chain"
    chain_root.mkdir(parents=True, exist_ok=False)
    retraining_evidence_path = chain_root / "live-retraining-evidence.json"
    container_evidence_path = chain_root / "container-evidence.json"
    handoff_path = chain_root / "handoff.json"
    routing_path = chain_root / "current-routing.json"
    rollback_path = chain_root / "rollback-routing.json"

    retraining_result = _run(
        [
            sys.executable,
            "labs/mlops/scripts/run_live_retraining_runtime.py",
            "--repo-root",
            str(repo_root),
            "--runtime-dir",
            str(runtime_dir),
            "--subject-sha",
            subject_sha,
            "--sample-request",
            str(sample_request),
            "--tracking-uri",
            args.tracking_uri,
            "--retraining-seed",
            str(args.retraining_seed),
            "--output",
            str(retraining_evidence_path),
        ],
        cwd=repo_root,
    )
    retraining_summary = _stdout_json(retraining_result)
    retraining = read_json(retraining_evidence_path)
    _require_sha256(retraining.get("evidence_id"), "live retraining evidence_id")
    if retraining.get("subject_sha") != subject_sha:
        raise PostRetrainingChainError("live retraining evidence belongs to another Git subject")
    if retraining.get("provider_stopped") is not True:
        raise PostRetrainingChainError("live retraining provider was not stopped")
    if retraining_summary.get("operation_id") != retraining["retraining"]["operation_id"]:
        raise PostRetrainingChainError("live retraining CLI summary operation mismatch")

    live_root = runtime_dir / "live-controlled-retraining"
    controlled_output = live_root / "controlled-output"
    candidate_path = controlled_output / "candidate.json"
    registry_path = controlled_output / "registry-evidence.json"
    artifact_dir = controlled_output / "artifact"
    release_path = controlled_output / "release.json"
    operation_path = live_root / "operation.json"
    state_path = live_root / "state.json"
    current_deployment_path = live_root / "current-deployment.json"

    container_result = _run(
        [
            sys.executable,
            "labs/mlops/scripts/run_containerized_inference_runtime.py",
            "--repo-root",
            str(repo_root),
            "--runtime-dir",
            str(runtime_dir),
            "--subject-sha",
            subject_sha,
            "--sample-request",
            str(sample_request),
            "--candidate",
            str(candidate_path),
            "--registry-evidence",
            str(registry_path),
            "--artifact-dir",
            str(artifact_dir),
            "--release",
            str(release_path),
            "--service-name",
            service_name,
            "--generation",
            generation,
            "--host",
            args.container_host,
            "--port",
            str(args.container_port),
            "--output",
            str(container_evidence_path),
        ],
        cwd=repo_root,
    )
    container_summary = _stdout_json(container_result)
    container = read_json(container_evidence_path)
    _require_sha256(container.get("evidence_id"), "container evidence_id")
    if container.get("subject_sha") != subject_sha:
        raise PostRetrainingChainError("container evidence belongs to another Git subject")
    if container.get("cleanup_verified") is not True:
        raise PostRetrainingChainError("container runtime cleanup was not verified")
    if container_summary.get("deployment_id") != container.get("deployment_id"):
        raise PostRetrainingChainError("container CLI summary deployment mismatch")

    new_deployment_path = runtime_dir / "container-runtime-deployment.json"
    current_deployment = read_json(current_deployment_path)
    new_deployment = read_json(new_deployment_path)
    validate_deployment_manifest(current_deployment)
    _validate_component_lineage(
        retraining=retraining,
        container=container,
        deployment=new_deployment,
    )
    if current_deployment["deployment_id"] == new_deployment["deployment_id"]:
        raise PostRetrainingChainError("post-retraining deployment did not change")
    if current_deployment["service_name"] != service_name:
        raise PostRetrainingChainError("current deployment service does not match chain service")

    current_routing = build_routing_state(
        stable=current_deployment,
        canary=None,
        canary_basis_points=0,
        current_state=None,
        expected_current_state_id=None,
    )
    validate_routing_state(current_routing)
    atomic_write_json(routing_path, current_routing)

    handoff_result = _run(
        [
            sys.executable,
            "labs/mlops/scripts/run_post_retraining_handoff.py",
            "--operation",
            str(operation_path),
            "--state",
            str(state_path),
            "--release",
            str(release_path),
            "--registry-evidence",
            str(registry_path),
            "--current-deployment",
            str(current_deployment_path),
            "--current-routing-state",
            str(routing_path),
            "--expected-current-routing-state-id",
            current_routing["routing_state_id"],
            "--service-name",
            service_name,
            "--generation",
            generation,
            "--image-reference",
            new_deployment["image"]["reference"],
            "--image-digest",
            new_deployment["image"]["digest"],
            "--canary-basis-points",
            str(args.canary_basis_points),
            "--output",
            str(handoff_path),
        ],
        cwd=repo_root,
    )
    handoff_summary = _stdout_json(handoff_result)
    handoff = read_json(handoff_path)
    validate_post_retraining_handoff(handoff)
    if handoff["deployment"] != new_deployment:
        raise PostRetrainingChainError(
            "post-retraining handoff did not rebuild the exact live-tested deployment"
        )
    if handoff_summary.get("deployment_id") != new_deployment["deployment_id"]:
        raise PostRetrainingChainError("handoff CLI summary deployment mismatch")
    canary_state = handoff["routing_state"]
    if canary_state["previous_routing_state_id"] != current_routing["routing_state_id"]:
        raise PostRetrainingChainError("canary state is detached from current routing subject")
    if canary_state["stable_deployment_id"] != current_deployment["deployment_id"]:
        raise PostRetrainingChainError("canary state changed the stable deployment subject")
    if canary_state["canary_deployment_id"] != new_deployment["deployment_id"]:
        raise PostRetrainingChainError("canary state does not target live-tested deployment")

    deployments = {
        current_deployment["deployment_id"]: current_deployment,
        new_deployment["deployment_id"]: new_deployment,
    }
    stable_probe = _find_route_probe(
        routing_state=canary_state,
        deployments=deployments,
        selected_role="stable",
    )
    canary_probe = _find_route_probe(
        routing_state=canary_state,
        deployments=deployments,
        selected_role="canary",
    )
    if stable_probe["deployment_id"] != current_deployment["deployment_id"]:
        raise PostRetrainingChainError("stable route probe resolved to wrong deployment")
    if canary_probe["deployment_id"] != new_deployment["deployment_id"]:
        raise PostRetrainingChainError("canary route probe resolved to wrong deployment")

    stale_rollback_refused = False
    try:
        build_rollback_state(
            current_state=canary_state,
            target_stable=current_deployment,
            expected_current_state_id="0" * 64,
        )
    except ContractError:
        stale_rollback_refused = True
    if not stale_rollback_refused:
        raise PostRetrainingChainError("stale rollback subject was not refused")

    rollback = build_rollback_state(
        current_state=canary_state,
        target_stable=current_deployment,
        expected_current_state_id=canary_state["routing_state_id"],
    )
    validate_routing_state(rollback)
    atomic_write_json(rollback_path, rollback)
    rollback_probe = route_request(
        routing_state=rollback,
        deployments=deployments,
        routing_key="post-retraining-rollback-verification",
    )
    if rollback_probe["selected_role"] != "stable":
        raise PostRetrainingChainError("rollback routing did not select stable role")
    if rollback_probe["deployment_id"] != current_deployment["deployment_id"]:
        raise PostRetrainingChainError("rollback did not restore previous deployment")
    if rollback["previous_routing_state_id"] != canary_state["routing_state_id"]:
        raise PostRetrainingChainError("rollback state is detached from canary state")

    payload: dict[str, Any] = {
        "schema_version": 1,
        "evidence_generation": "mlops-post-retraining-runtime-chain-v1",
        "subject_sha": subject_sha,
        "live_retraining": {
            "evidence_id": retraining["evidence_id"],
            "operation_id": retraining["retraining"]["operation_id"],
            "state_id": retraining["retraining"]["state_id"],
            "candidate_id": retraining["retraining"]["candidate_id"],
            "release_id": retraining["retraining"]["release_id"],
            "registry_evidence_id": retraining["retraining"]["registry_evidence_id"],
            "registry_version": retraining["retraining"]["registry_version"],
            "model_sha256": retraining["retraining"]["model_sha256"],
            "provider_stopped": retraining["provider_stopped"],
            "replay_status": retraining["replay"]["status"],
        },
        "container_runtime": {
            "evidence_id": container["evidence_id"],
            "input_mode": container["input_mode"],
            "release_source": container["release_source"],
            "deployment_id": container["deployment_id"],
            "docker_image_id": container["docker_image_id"],
            "image_reference": container["image_reference"],
            "container_uid": container["container_uid"],
            "cleanup_verified": container["cleanup_verified"],
            "invalid_request_status": container["invalid_request_status"],
            "wrong_image_digest_refused": container["wrong_image_digest"]["refused"],
        },
        "handoff": {
            "post_retraining_handoff_id": handoff["post_retraining_handoff_id"],
            "deployment_id": new_deployment["deployment_id"],
            "current_routing_state_id": current_routing["routing_state_id"],
            "canary_routing_state_id": canary_state["routing_state_id"],
            "canary_basis_points": canary_state["canary_basis_points"],
            "exact_live_tested_deployment_rebuilt": True,
        },
        "routing_probes": {
            "stable": stable_probe,
            "canary": canary_probe,
        },
        "rollback": {
            "stale_subject_refused": stale_rollback_refused,
            "routing_state_id": rollback["routing_state_id"],
            "previous_routing_state_id": rollback["previous_routing_state_id"],
            "stable_deployment_id": rollback["stable_deployment_id"],
            "canary_deployment_id": rollback["canary_deployment_id"],
            "canary_basis_points": rollback["canary_basis_points"],
            "probe": rollback_probe,
        },
        "proof_boundary": {
            "new_model_training": "live-local",
            "new_registry_version": "live-local-mlflow",
            "new_container": "live-local-docker-http",
            "previous_stable_deployment_image": "control-plane-subject-not-runtime-verified",
            "canary_traffic": "deterministic-routing-state-not-live-proxy",
            "rollback": "deterministic-routing-state",
            "remote_oci_registry_claimed": False,
            "production_platform_claimed": False,
        },
    }
    evidence = {**payload, "evidence_id": sha256_bytes(canonical_json_bytes(payload))}
    atomic_write_json(output_path, evidence)
    return evidence


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        evidence = run(args)
    except (ContractError, PostRetrainingChainError, OSError, RuntimeError, ValueError) as exc:
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
                "operation_id": evidence["live_retraining"]["operation_id"],
                "registry_version": evidence["live_retraining"]["registry_version"],
                "deployment_id": evidence["container_runtime"]["deployment_id"],
                "docker_image_id": evidence["container_runtime"]["docker_image_id"],
                "canary_routing_state_id": evidence["handoff"]["canary_routing_state_id"],
                "rollback_routing_state_id": evidence["rollback"]["routing_state_id"],
                "evidence_id": evidence["evidence_id"],
                "output": args.output.as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
