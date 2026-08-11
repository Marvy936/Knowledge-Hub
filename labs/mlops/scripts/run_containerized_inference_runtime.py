from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
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
    validate_candidate_manifest,
)
from mlops_lab.registry import validate_registry_evidence
from mlops_lab.serving import (
    build_deployment_manifest,
    validate_deployment_manifest,
    validate_release_manifest,
)

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
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--registry-evidence", type=Path)
    parser.add_argument("--artifact-dir", type=Path)
    parser.add_argument("--release", type=Path)
    parser.add_argument("--service-name", default="knowledge-hub-churn-api")
    parser.add_argument("--generation", default="container-runtime-v1")
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


def _require_nonempty(value: str, field: str) -> str:
    text = value.strip()
    if not text:
        raise RuntimeGateError(f"{field} must be a non-empty string")
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
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        time.sleep(1)
    raise RuntimeGateError(f"serving container did not become ready: {last_error}")


def _resolve_subject_paths(
    *,
    runtime_dir: Path,
    candidate_path: Path | None,
    registry_path: Path | None,
    artifact_dir: Path | None,
    release_path: Path | None,
) -> dict[str, Any]:
    explicit_values = (candidate_path, registry_path, artifact_dir)
    if any(value is not None for value in explicit_values):
        if not all(value is not None for value in explicit_values):
            raise RuntimeGateError(
                "explicit serving subject mode requires --candidate, --registry-evidence and --artifact-dir together"
            )
        if release_path is None:
            raise RuntimeGateError(
                "explicit serving subject mode requires --release so release lineage cannot be regenerated"
            )
        return {
            "input_mode": "explicit-subjects",
            "candidate_path": candidate_path.resolve(strict=True),
            "registry_path": registry_path.resolve(strict=True),
            "artifact_dir": artifact_dir.resolve(strict=True),
            "release_path": release_path.resolve(strict=True),
        }
    if release_path is not None:
        raise RuntimeGateError("--release is valid only with explicit serving subjects")
    return {
        "input_mode": "runtime-baseline",
        "candidate_path": (runtime_dir / "ml" / "candidate.json").resolve(strict=True),
        "registry_path": (runtime_dir / "registry-evidence.json").resolve(strict=True),
        "artifact_dir": (runtime_dir / "ml" / "artifact").resolve(strict=True),
        "release_path": None,
    }


def _require_runtime_inputs(
    *,
    candidate_path: Path,
    registry_path: Path,
    artifact_dir: Path,
    subject_sha: str,
) -> dict[str, Any]:
    if candidate_path.is_symlink() or not candidate_path.is_file():
        raise RuntimeGateError("candidate input must be a regular non-symlink file")
    if registry_path.is_symlink() or not registry_path.is_file():
        raise RuntimeGateError("Registry evidence input must be a regular non-symlink file")
    if artifact_dir.is_symlink() or not artifact_dir.is_dir():
        raise RuntimeGateError("artifact input must be a regular non-symlink directory")

    artifact_manifest_path = artifact_dir / "manifest.json"
    model_path = artifact_dir / "model.joblib"
    if artifact_manifest_path.is_symlink() or not artifact_manifest_path.is_file():
        raise RuntimeGateError("artifact manifest must be a regular non-symlink file")
    if model_path.is_symlink() or not model_path.is_file():
        raise RuntimeGateError("trained model artifact must be a regular non-symlink file")

    candidate = read_json(candidate_path)
    registry = read_json(registry_path)
    artifact_manifest = read_json(artifact_manifest_path)
    validate_candidate_manifest(candidate)
    validate_registry_evidence(registry)

    if candidate.get("source_revision") != subject_sha:
        raise RuntimeGateError("candidate source revision does not match runtime subject")
    if registry.get("source_revision") != subject_sha:
        raise RuntimeGateError("Registry source revision does not match runtime subject")
    if artifact_manifest.get("source_revision") != subject_sha:
        raise RuntimeGateError("artifact source revision does not match runtime subject")
    if candidate.get("candidate_id") != registry.get("candidate_id"):
        raise RuntimeGateError("candidate and Registry evidence refer to different candidates")
    model_sha256 = candidate["model"]["sha256"]
    if model_sha256 != registry.get("artifact_readback", {}).get("downloaded_sha256"):
        raise RuntimeGateError("candidate model digest does not match Registry artifact read-back")
    if artifact_manifest.get("model_sha256") != model_sha256:
        raise RuntimeGateError("artifact manifest model digest does not match candidate")
    if artifact_manifest.get("dataset_sha256") != candidate["dataset"]["sha256"]:
        raise RuntimeGateError("artifact manifest dataset digest does not match candidate")
    if model_path.stat().st_size != candidate["model"]["size_bytes"]:
        raise RuntimeGateError("trained model size does not match candidate")
    if _sha256_file(model_path) != model_sha256:
        raise RuntimeGateError("trained model bytes do not match candidate digest")

    return {
        "candidate": candidate,
        "registry": registry,
        "artifact_manifest": artifact_manifest,
        "artifact_manifest_path": artifact_manifest_path,
        "model_path": model_path,
        "artifact_dir": artifact_dir,
    }


def _resolve_release(
    *,
    candidate: Mapping[str, Any],
    provided_release_path: Path | None,
) -> tuple[dict[str, Any], str]:
    if provided_release_path is None:
        release, _ = promote_candidate(
            candidate=candidate,
            alias_state={"schema_version": 1, "aliases": {}},
            alias="champion",
            expected_current=None,
        )
        return release, "generated-baseline-release"

    if provided_release_path.is_symlink() or not provided_release_path.is_file():
        raise RuntimeGateError("provided release must be a regular non-symlink file")
    release = read_json(provided_release_path)
    validate_release_manifest(release)
    expected = {
        "candidate_id": candidate["candidate_id"],
        "dataset_sha256": candidate["dataset"]["sha256"],
        "model_sha256": candidate["model"]["sha256"],
        "evaluation_sha256": candidate["evaluation"]["sha256"],
        "policy_generation": candidate["evaluation"]["policy_generation"],
        "source_revision": candidate["source_revision"],
    }
    for key, value in expected.items():
        if release.get(key) != value:
            raise RuntimeGateError(f"provided release {key} does not match candidate subject")
    return release, "provided-release"


def _prepare_readonly_mounts(
    *,
    staging_root: Path,
    deployment_path: Path,
    artifact_manifest_path: Path,
    model_path: Path,
    expected_model_sha256: str,
) -> tuple[dict[str, str], Path, Path]:
    if staging_root.exists() or staging_root.is_symlink():
        raise RuntimeGateError("serving mount staging root must be fresh")
    for path in (deployment_path, artifact_manifest_path, model_path):
        if not path.is_file() or path.is_symlink():
            raise RuntimeGateError(f"serving mount source must be a regular non-symlink file: {path}")
    if _sha256_file(model_path) != expected_model_sha256:
        raise RuntimeGateError("model digest changed before preparing read-only serving mount")

    artifact_staging = staging_root / "artifact"
    artifact_staging.mkdir(parents=True, exist_ok=False)
    staged_deployment = staging_root / "deployment.json"
    staged_manifest = artifact_staging / "manifest.json"
    staged_model = artifact_staging / "model.joblib"
    for source, target in (
        (deployment_path, staged_deployment),
        (artifact_manifest_path, staged_manifest),
        (model_path, staged_model),
    ):
        shutil.copyfile(source, target)
        target.chmod(0o444)

    if _sha256_file(staged_model) != expected_model_sha256:
        raise RuntimeGateError("model digest changed while preparing read-only serving mount")
    return (
        {
            "deployment": oct(stat.S_IMODE(staged_deployment.stat().st_mode)),
            "manifest": oct(stat.S_IMODE(staged_manifest.stat().st_mode)),
            "model": oct(stat.S_IMODE(staged_model.stat().st_mode)),
        },
        staged_deployment,
        artifact_staging,
    )


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
    service_name = _require_nonempty(args.service_name, "service_name")
    generation = _require_nonempty(args.generation, "generation")

    if args.host not in {"127.0.0.1", "localhost"}:
        raise RuntimeGateError("container runtime gate is loopback-only")
    if not 1 <= args.port <= 65535:
        raise RuntimeGateError("port must be between 1 and 65535")
    if args.startup_timeout_seconds < 1 or args.startup_timeout_seconds > 300:
        raise RuntimeGateError("startup timeout must be between 1 and 300 seconds")
    if output_path.exists() or output_path.is_symlink():
        raise RuntimeGateError("evidence output must be a fresh path")
    if not sample_request_path.is_file() or sample_request_path.is_symlink():
        raise RuntimeGateError("sample request must be a regular non-symlink file")

    git_head = _run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
    if git_head != subject_sha:
        raise RuntimeGateError("subject SHA does not match checked-out Git HEAD")

    paths = _resolve_subject_paths(
        runtime_dir=runtime_dir,
        candidate_path=args.candidate,
        registry_path=args.registry_evidence,
        artifact_dir=args.artifact_dir,
        release_path=args.release,
    )
    inputs = _require_runtime_inputs(
        candidate_path=paths["candidate_path"],
        registry_path=paths["registry_path"],
        artifact_dir=paths["artifact_dir"],
        subject_sha=subject_sha,
    )
    candidate = inputs["candidate"]
    registry = inputs["registry"]
    artifact_manifest_path = Path(inputs["artifact_manifest_path"]).resolve(strict=True)
    model_path = Path(inputs["model_path"]).resolve(strict=True)
    release, release_source = _resolve_release(
        candidate=candidate,
        provided_release_path=paths["release_path"],
    )

    if paths["input_mode"] == "runtime-baseline":
        generated_release_path = runtime_dir / "container-runtime-release.json"
        if generated_release_path.exists() or generated_release_path.is_symlink():
            raise RuntimeGateError("generated container runtime release path must be fresh")
        atomic_write_json(generated_release_path, release)

    image_tag = (
        f"knowledge-hub-mlops-runtime:{subject_sha[:10]}-{candidate['candidate_id'][:10]}-{os.getpid()}"
    )
    container_name = f"kh-mlops-runtime-{candidate['candidate_id'][:10]}-{os.getpid()}"
    negative_name = f"{container_name}-wrong-digest"
    image_id: str | None = None
    deployment_path = runtime_dir / "container-runtime-deployment.json"
    if deployment_path.exists() or deployment_path.is_symlink():
        raise RuntimeGateError("container runtime deployment output must be fresh")
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
            service_name=service_name,
            generation=generation,
            image_reference=image_tag,
            image_digest=image_id,
        )
        validate_deployment_manifest(deployment)
        atomic_write_json(deployment_path, deployment)
        mount_modes, serving_deployment_path, serving_artifact_dir = _prepare_readonly_mounts(
            staging_root=runtime_dir / "container-runtime-serving-mounts",
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
                f"type=bind,src={serving_deployment_path.resolve()},dst=/runtime/deployment.json,readonly",
                "--mount",
                f"type=bind,src={serving_artifact_dir.resolve()},dst=/runtime/artifact,readonly",
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
        try:
            ready = _wait_ready(base_url, args.startup_timeout_seconds)
        except Exception as exc:
            inspect_result = _run(
                [
                    "docker",
                    "inspect",
                    "--format",
                    "{{json .State}}",
                    positive_container_id,
                ],
                cwd=repo_root,
                check=False,
            )
            logs_result = _run(
                ["docker", "logs", positive_container_id],
                cwd=repo_root,
                check=False,
            )
            state_text = (inspect_result.stdout or inspect_result.stderr or "").strip()
            combined_logs = (logs_result.stdout or "") + (logs_result.stderr or "")
            log_tail = combined_logs[-4000:]
            log_sha256 = _sha256_bytes(combined_logs.encode("utf-8", errors="replace"))
            raise RuntimeGateError(
                "serving container readiness failed; "
                f"state={state_text}; log_sha256={log_sha256}; log_tail={log_tail}"
            ) from exc
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
            deployment_path=serving_deployment_path.resolve(),
            artifact_dir=serving_artifact_dir.resolve(),
            container_name=negative_name,
            timeout_seconds=min(args.startup_timeout_seconds, 60),
        )
        _run(["docker", "rm", "--force", negative_name], cwd=repo_root, check=False)

        payload: dict[str, Any] = {
            "schema_version": 1,
            "evidence_generation": "mlops-containerized-inference-v2",
            "subject_sha": subject_sha,
            "input_mode": paths["input_mode"],
            "release_source": release_source,
            "candidate_id": candidate["candidate_id"],
            "release_id": release["release_id"],
            "previous_candidate_id": release["previous_candidate_id"],
            "registry_evidence_id": registry["registry_evidence_id"],
            "registry_model_name": registry["registry"]["name"],
            "registry_version": registry["registry"]["version"],
            "registry_exact_uri": registry["registry"]["exact_uri"],
            "model_sha256": deployment["model"]["sha256"],
            "docker_image_id": image_id,
            "image_reference": image_tag,
            "deployment_id": deployment["deployment_id"],
            "deployment_generation": deployment["generation"],
            "service_name": deployment["service_name"],
            "container_uid": uid,
            "mount_file_modes": mount_modes,
            "mount_staging": "disposable-runtime-copy",
            "authoritative_artifacts_mutated": False,
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
                "input_mode": evidence["input_mode"],
                "release_id": evidence["release_id"],
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
