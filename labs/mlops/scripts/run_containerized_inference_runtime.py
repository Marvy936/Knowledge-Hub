from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Mapping, Sequence

from mlops_lab.contracts import (
    ContractError,
    atomic_write_json,
    canonical_json_bytes,
    promote_candidate,
    read_json,
)
from mlops_lab.registry import validate_registry_evidence
from mlops_lab.serving import build_deployment_manifest, validate_deployment_manifest

IMAGE_ID_PREFIX = "sha256:"
IMAGE_ID_HEX_LENGTH = 64


class RuntimeGateError(RuntimeError):
    pass


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the Practical v1 MLOps serving image, run it by content-addressed "
            "Docker image ID, verify non-root live HTTP inference and record bounded evidence."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--subject-sha", required=True)
    parser.add_argument("--sample-request", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18080)
    parser.add_argument("--startup-timeout-seconds", type=int, default=90)
    return parser


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_subject_sha(value: str) -> str:
    text = value.strip()
    if len(text) != 40 or any(character not in "0123456789abcdef" for character in text):
        raise RuntimeGateError("subject SHA must be a lowercase 40-character Git SHA-1")
    return text


def _validate_image_id(value: str) -> str:
    text = value.strip()
    if not text.startswith(IMAGE_ID_PREFIX):
        raise RuntimeGateError("Docker image ID must use sha256")
    digest = text.removeprefix(IMAGE_ID_PREFIX)
    if len(digest) != IMAGE_ID_HEX_LENGTH or any(
        character not in "0123456789abcdef" for character in digest
    ):
        raise RuntimeGateError("Docker image ID must contain a lowercase 64-hex SHA-256 digest")
    return text


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(command),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        stdout = (result.stdout or "")[-4000:]
        stderr = (result.stderr or "")[-4000:]
        raise RuntimeGateError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout tail:\n{stdout}\nstderr tail:\n{stderr}"
        )
    return result


def _docker_exists(repo_root: Path, kind: str, subject: str) -> bool:
    return (
        _run(
            ["docker", kind, "inspect", subject],
            cwd=repo_root,
            check=False,
        ).returncode
        == 0
    )


def _http_json(
    url: str,
    *,
    method: str = "GET",
    payload: Mapping[str, Any] | None = None,
    timeout: float = 5.0,
) -> tuple[int, dict[str, Any]]:
    data = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
            body = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        body = exc.read()
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeGateError(f"HTTP {url} did not return valid JSON") from exc
    if not isinstance(value, dict):
        raise RuntimeGateError(f"HTTP {url} JSON body must be an object")
    return status, value


def _wait_ready(base_url: str, timeout_seconds: int) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_error = "not attempted"
    while time.monotonic() < deadline:
        try:
            status, value = _http_json(base_url + "/readyz", timeout=2.0)
            if status == 200:
                return value
            last_error = f"HTTP {status}: {value}"
        except Exception as exc:  # bounded polling; final failure is explicit
            last_error = f"{type(exc).__name__}: {exc}"
        time.sleep(1)
    raise RuntimeGateError(f"serving container did not become ready: {last_error}")


def _require_runtime_inputs(runtime_dir: Path, subject_sha: str) -> dict[str, Any]:
    candidate_path = runtime_dir / "ml" / "candidate.json"
    registry_path = runtime_dir / "registry-evidence.json"
    artifact_manifest_path = runtime_dir / "ml" / "artifact" / "manifest.json"
    model_path = runtime_dir / "ml" / "artifact" / "model.joblib"

    candidate = read_json(candidate_path)
    registry = read_json(registry_path)
    artifact_manifest = read_json(artifact_manifest_path)
    validate_registry_evidence(registry)

    if candidate.get("source_revision") != subject_sha:
        raise RuntimeGateError("candidate source revision does not match runtime subject")
    if registry.get("source_revision") != subject_sha:
        raise RuntimeGateError("Registry source revision does not match runtime subject")
    if artifact_manifest.get("source_revision") != subject_sha:
        raise RuntimeGateError("artifact source revision does not match runtime subject")
    if candidate.get("candidate_id") != registry.get("candidate_id"):
        raise RuntimeGateError("candidate and Registry evidence refer to different candidates")
    model_sha256 = candidate.get("model", {}).get("sha256")
    if model_sha256 != registry.get("artifact_readback", {}).get("downloaded_sha256"):
        raise RuntimeGateError("candidate model digest does not match Registry artifact read-back")
    if artifact_manifest.get("model_sha256") != model_sha256:
        raise RuntimeGateError("artifact manifest model digest does not match candidate")
    if not model_path.is_file():
        raise RuntimeGateError("trained model artifact is missing")
    if _sha256_file(model_path) != model_sha256:
        raise RuntimeGateError("trained model bytes do not match candidate digest")

    return {
        "candidate": candidate,
        "registry": registry,
        "artifact_manifest": artifact_manifest,
        "artifact_manifest_path": artifact_manifest_path,
        "model_path": model_path,
        "artifact_dir": artifact_manifest_path.parent,
    }


def _prepare_readonly_mounts(
    *,
    deployment_path: Path,
    artifact_manifest_path: Path,
    model_path: Path,
    expected_model_sha256: str,
) -> dict[str, str]:
    for path in (deployment_path, artifact_manifest_path, model_path):
        if not path.is_file() or path.is_symlink():
            raise RuntimeGateError(f"serving mount must be a regular non-symlink file: {path}")
        path.chmod(0o444)
    if _sha256_file(model_path) != expected_model_sha256:
        raise RuntimeGateError("model digest changed while preparing read-only serving mount")
    return {
        "deployment": oct(stat.S_IMODE(deployment_path.stat().st_mode)),
        "manifest": oct(stat.S_IMODE(artifact_manifest_path.stat().st_mode)),
        "model": oct(stat.S_IMODE(model_path.stat().st_mode)),
    }


def _validate_ready(value: Mapping[str, Any], *, deployment: Mapping[str, Any]) -> None:
    expected = {
        "status": "ready",
        "service_name": deployment["service_name"],
        "deployment_id": deployment["deployment_id"],
        "generation": deployment["generation"],
        "release_id": deployment["release_id"],
        "model_sha256": deployment["model"]["sha256"],
        "registry_exact_uri": deployment["model"]["exact_uri"],
        "image_digest": deployment["image"]["digest"],
    }
    if dict(value) != expected:
        raise RuntimeGateError("readiness response does not match exact deployment subject")


def _validate_prediction(value: Mapping[str, Any], *, deployment: Mapping[str, Any]) -> None:
    expected_identity = {
        "service_name": deployment["service_name"],
        "deployment_id": deployment["deployment_id"],
        "generation": deployment["generation"],
        "release_id": deployment["release_id"],
        "candidate_id": deployment["candidate_id"],
        "model_sha256": deployment["model"]["sha256"],
        "registry_exact_uri": deployment["model"]["exact_uri"],
        "image_digest": deployment["image"]["digest"],
    }
    for key, expected in expected_identity.items():
        if value.get(key) != expected:
            raise RuntimeGateError(f"prediction response {key} does not match deployment subject")
    prediction = value.get("prediction")
    probability = value.get("probability")
    threshold = value.get("decision_threshold")
    if prediction not in {0, 1}:
        raise RuntimeGateError("prediction response contains invalid prediction")
    if isinstance(probability, bool) or not isinstance(probability, (int, float)):
        raise RuntimeGateError("prediction response probability is invalid")
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise RuntimeGateError("prediction response threshold is invalid")


def _negative_wrong_digest_refusal(
    *,
    repo_root: Path,
    image_id: str,
    deployment_path: Path,
    artifact_dir: Path,
    container_name: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    wrong_digest = IMAGE_ID_PREFIX + ("0" * IMAGE_ID_HEX_LENGTH)
    if wrong_digest == image_id:
        wrong_digest = IMAGE_ID_PREFIX + ("f" * IMAGE_ID_HEX_LENGTH)
    result = _run(
        [
            "docker",
            "run",
            "--name",
            container_name,
            "--detach",
            "--mount",
            f"type=bind,src={deployment_path},dst=/runtime/deployment.json,readonly",
            "--mount",
            f"type=bind,src={artifact_dir},dst=/runtime/artifact,readonly",
            "--env",
            f"MLOPS_IMAGE_DIGEST={wrong_digest}",
            image_id,
        ],
        cwd=repo_root,
    )
    container_id = result.stdout.strip()
    if not container_id:
        raise RuntimeGateError("wrong-digest docker run did not return a container ID")

    deadline = time.monotonic() + timeout_seconds
    exit_code: int | None = None
    while time.monotonic() < deadline:
        inspect = _run(
            ["docker", "inspect", "--format", "{{.State.Running}} {{.State.ExitCode}}", container_id],
            cwd=repo_root,
        ).stdout.strip().split()
        if len(inspect) == 2 and inspect[0] == "false":
            exit_code = int(inspect[1])
            break
        time.sleep(1)

    log_result = _run(["docker", "logs", container_id], cwd=repo_root, check=False)
    combined_logs = (log_result.stdout or "") + (log_result.stderr or "")
    if exit_code is None or exit_code == 0:
        raise RuntimeGateError("wrong-image-digest container did not fail startup")
    if "runtime image digest does not match deployment subject" not in combined_logs:
        raise RuntimeGateError("wrong-image-digest refusal was not observable in container logs")
    return {
        "refused": True,
        "exit_code": exit_code,
        "wrong_digest": wrong_digest,
        "log_sha256": _sha256_bytes(combined_logs.encode("utf-8", errors="replace")),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve(strict=True)
    runtime_dir = args.runtime_dir.resolve(strict=True)
    sample_request_path = args.sample_request.resolve(strict=True)
    output_path = args.output.resolve(strict=False)
    subject_sha = _require_subject_sha(args.subject_sha)

    if args.host not in {"127.0.0.1", "localhost"}:
        raise RuntimeGateError("container runtime gate is loopback-only")
    if not 1 <= args.port <= 65535:
        raise RuntimeGateError("port must be between 1 and 65535")
    if args.startup_timeout_seconds < 1 or args.startup_timeout_seconds > 300:
        raise RuntimeGateError("startup timeout must be between 1 and 300 seconds")
    if output_path.exists() or output_path.is_symlink():
        raise RuntimeGateError("evidence output must be a fresh path")
    if not sample_request_path.is_file():
        raise RuntimeGateError("sample request does not exist")

    git_head = _run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
    if git_head != subject_sha:
        raise RuntimeGateError("subject SHA does not match checked-out Git HEAD")

    inputs = _require_runtime_inputs(runtime_dir, subject_sha)
    candidate = inputs["candidate"]
    registry = inputs["registry"]
    artifact_manifest_path = Path(inputs["artifact_manifest_path"]).resolve(strict=True)
    model_path = Path(inputs["model_path"]).resolve(strict=True)
    artifact_dir = Path(inputs["artifact_dir"]).resolve(strict=True)

    release, _ = promote_candidate(
        candidate=candidate,
        alias_state={"schema_version": 1, "aliases": {}},
        alias="champion",
        expected_current=None,
    )
    release_path = runtime_dir / "container-runtime-release.json"
    atomic_write_json(release_path, release)

    image_tag = f"knowledge-hub-mlops-runtime:{subject_sha[:12]}-{os.getpid()}"
    container_name = f"kh-mlops-runtime-{subject_sha[:10]}-{os.getpid()}"
    negative_name = f"{container_name}-wrong-digest"
    image_id: str | None = None
    deployment_path = runtime_dir / "container-runtime-deployment.json"
    positive_container_id: str | None = None
    cleanup_errors: list[str] = []
    evidence: dict[str, Any] | None = None

    try:
        _run(
            [
                "docker",
                "build",
                "--file",
                "labs/mlops/Dockerfile.serving",
                "--tag",
                image_tag,
                ".",
            ],
            cwd=repo_root,
        )
        image_id = _validate_image_id(
            _run(
                ["docker", "image", "inspect", "--format", "{{.Id}}", image_tag],
                cwd=repo_root,
            ).stdout.strip()
        )

        deployment = build_deployment_manifest(
            release=release,
            registry_evidence=registry,
            service_name="knowledge-hub-churn-api",
            generation="container-runtime-v1",
            image_reference=image_tag,
            image_digest=image_id,
        )
        validate_deployment_manifest(deployment)
        atomic_write_json(deployment_path, deployment)
        mount_modes = _prepare_readonly_mounts(
            deployment_path=deployment_path,
            artifact_manifest_path=artifact_manifest_path,
            model_path=model_path,
            expected_model_sha256=deployment["model"]["sha256"],
        )

        run_result = _run(
            [
                "docker",
                "run",
                "--name",
                container_name,
                "--detach",
                "--publish",
                f"{args.host}:{args.port}:8080",
                "--mount",
                f"type=bind,src={deployment_path.resolve()},dst=/runtime/deployment.json,readonly",
                "--mount",
                f"type=bind,src={artifact_dir},dst=/runtime/artifact,readonly",
                "--env",
                f"MLOPS_IMAGE_DIGEST={image_id}",
                image_id,
            ],
            cwd=repo_root,
        )
        positive_container_id = run_result.stdout.strip()
        if not positive_container_id:
            raise RuntimeGateError("docker run did not return a container ID")

        base_url = f"http://{args.host}:{args.port}"
        ready = _wait_ready(base_url, args.startup_timeout_seconds)
        _validate_ready(ready, deployment=deployment)

        uid = _run(
            ["docker", "exec", positive_container_id, "id", "-u"],
            cwd=repo_root,
        ).stdout.strip()
        if uid != "10001":
            raise RuntimeGateError(f"serving container UID must equal 10001, got {uid!r}")

        health_status, health = _http_json(base_url + "/healthz")
        if health_status != 200 or health != {"status": "live"}:
            raise RuntimeGateError("health endpoint did not return the exact liveness contract")

        sample_request = read_json(sample_request_path)
        predict_status, prediction = _http_json(
            base_url + "/v1/predict",
            method="POST",
            payload=sample_request,
        )
        if predict_status != 200:
            raise RuntimeGateError(f"positive prediction returned HTTP {predict_status}")
        _validate_prediction(prediction, deployment=deployment)

        invalid_request = dict(sample_request)
        invalid_request["unexpected_field"] = "must-be-refused"
        invalid_status, invalid_body = _http_json(
            base_url + "/v1/predict",
            method="POST",
            payload=invalid_request,
        )
        if invalid_status != 422:
            raise RuntimeGateError(
                f"extra-field request must return 422, got HTTP {invalid_status}: {invalid_body}"
            )

        _run(["docker", "rm", "--force", positive_container_id], cwd=repo_root)
        positive_container_id = None

        wrong_digest = _negative_wrong_digest_refusal(
            repo_root=repo_root,
            image_id=image_id,
            deployment_path=deployment_path.resolve(),
            artifact_dir=artifact_dir,
            container_name=negative_name,
            timeout_seconds=min(args.startup_timeout_seconds, 60),
        )
        _run(["docker", "rm", "--force", negative_name], cwd=repo_root, check=False)

        payload: dict[str, Any] = {
            "schema_version": 1,
            "evidence_generation": "mlops-containerized-inference-v1",
            "subject_sha": subject_sha,
            "candidate_id": candidate["candidate_id"],
            "release_id": release["release_id"],
            "registry_evidence_id": registry["registry_evidence_id"],
            "registry_model_name": registry["registry"]["name"],
            "registry_version": registry["registry"]["version"],
            "registry_exact_uri": registry["registry"]["exact_uri"],
            "model_sha256": deployment["model"]["sha256"],
            "docker_image_id": image_id,
            "deployment_id": deployment["deployment_id"],
            "container_uid": uid,
            "mount_file_modes": mount_modes,
            "health_status": health["status"],
            "ready_deployment_id": ready["deployment_id"],
            "prediction": {
                "prediction": prediction["prediction"],
                "probability": prediction["probability"],
                "decision_threshold": prediction["decision_threshold"],
                "deployment_id": prediction["deployment_id"],
                "image_digest": prediction["image_digest"],
            },
            "invalid_request_status": invalid_status,
            "wrong_image_digest": wrong_digest,
            "runtime_boundary": {
                "network": "loopback-host-port-to-local-docker",
                "image_subject": "docker-content-addressed-image-id",
                "container_runtime": "docker",
                "production_platform_claimed": False,
            },
        }
        evidence = {
            **payload,
            "evidence_id": _sha256_bytes(canonical_json_bytes(payload)),
        }
    finally:
        for container in (positive_container_id, negative_name):
            if container and _docker_exists(repo_root, "container", container):
                result = _run(
                    ["docker", "rm", "--force", container],
                    cwd=repo_root,
                    check=False,
                )
                if result.returncode != 0:
                    cleanup_errors.append(f"failed to remove container {container}")
        if image_id is not None:
            _run(["docker", "image", "rm", "--force", image_tag], cwd=repo_root, check=False)
            _run(["docker", "image", "rm", "--force", image_id], cwd=repo_root, check=False)
            if _docker_exists(repo_root, "image", image_tag):
                cleanup_errors.append("image tag still exists after cleanup")
            if _docker_exists(repo_root, "image", image_id):
                cleanup_errors.append("content-addressed image still exists after cleanup")

    if evidence is None:
        raise RuntimeGateError("container runtime ended without evidence")
    if cleanup_errors:
        raise RuntimeGateError("; ".join(cleanup_errors))

    evidence["cleanup_verified"] = True
    final_payload = {key: value for key, value in evidence.items() if key != "evidence_id"}
    evidence["evidence_id"] = _sha256_bytes(canonical_json_bytes(final_payload))
    atomic_write_json(output_path, evidence)
    return evidence


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        evidence = run(args)
    except (ContractError, RuntimeGateError, OSError, ValueError) as exc:
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
                "deployment_id": evidence["deployment_id"],
                "docker_image_id": evidence["docker_image_id"],
                "container_uid": evidence["container_uid"],
                "cleanup_verified": evidence["cleanup_verified"],
                "evidence_id": evidence["evidence_id"],
                "output": args.output.as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
