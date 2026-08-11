from __future__ import annotations

import json
import platform
from pathlib import Path
from typing import Any, Mapping

from .contracts import (
    ContractError,
    canonical_json_bytes,
    sha256_bytes,
    sha256_file,
    validate_candidate_manifest,
)

REGISTRY_SCHEMA_VERSION = 1
PREDICTION_TOLERANCE = 1e-12


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value.strip()


def _require_sha256(value: Any, field: str) -> str:
    text = _require_nonempty_string(value, field)
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise ContractError(f"{field} must be a lowercase SHA-256 hex digest")
    return text


def _require_exact_keys(value: Mapping[str, Any], expected: set[str], field: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ContractError(
            f"{field} keys mismatch: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )


def verify_source_model(candidate: Mapping[str, Any], model_path: Path) -> None:
    """Refuse deserialization unless the candidate pins the exact source bytes."""

    validate_candidate_manifest(candidate)
    if not model_path.is_file():
        raise ContractError(f"Model artifact does not exist or is not a file: {model_path}")
    actual_size = model_path.stat().st_size
    actual_sha256 = sha256_file(model_path)
    if actual_size != candidate["model"]["size_bytes"]:
        raise ContractError(
            "model size does not match candidate: "
            f"expected {candidate['model']['size_bytes']}, found {actual_size}"
        )
    if actual_sha256 != candidate["model"]["sha256"]:
        raise ContractError(
            "model SHA-256 does not match candidate: "
            f"expected {candidate['model']['sha256']}, found {actual_sha256}"
        )


def _load_request(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"Sample request does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"Invalid sample request JSON in {path}: {exc}") from exc
    if not isinstance(value, dict) or not value:
        raise ContractError("sample request must be a non-empty JSON object")
    if any(not isinstance(key, str) or not key for key in value):
        raise ContractError("sample request keys must be non-empty strings")
    return value


def _prediction(model: Any, frame: Any) -> tuple[float, int]:
    if not hasattr(model, "predict_proba") or not hasattr(model, "predict"):
        raise ContractError("model must expose predict_proba() and predict()")
    probabilities = model.predict_proba(frame)
    predictions = model.predict(frame)
    try:
        probability = float(probabilities[0][1])
        prediction = int(predictions[0])
    except (IndexError, TypeError, ValueError) as exc:
        raise ContractError("model returned an unsupported prediction shape") from exc
    if not 0.0 <= probability <= 1.0:
        raise ContractError("model positive-class probability must be between 0 and 1")
    if prediction not in (0, 1):
        raise ContractError("model prediction must be binary")
    return probability, prediction


def build_registry_evidence(
    *,
    tracking_uri: str,
    experiment_id: str,
    run_id: str,
    logged_model_id: str,
    candidate_id: str,
    source_revision: str,
    model_name: str,
    version: str,
    alias: str,
    alias_resolved_version: str,
    source_uri: str,
    source_run_id: str,
    model_version_status: str,
    model_version_tags: Mapping[str, str],
    artifact_path: str,
    original_model_sha256: str,
    downloaded_model_sha256: str,
    model_size_bytes: int,
    request: Mapping[str, Any],
    source_probability: float,
    source_prediction: int,
    registry_probability: float,
    registry_prediction: int,
    mlflow_version: str,
) -> dict[str, Any]:
    exact_uri = f"models:/{model_name}/{version}"
    error = abs(source_probability - registry_probability)
    payload: dict[str, Any] = {
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "tracking_uri": tracking_uri,
        "experiment_id": experiment_id,
        "run_id": run_id,
        "logged_model_id": logged_model_id,
        "candidate_id": candidate_id,
        "source_revision": source_revision,
        "registry": {
            "name": model_name,
            "version": version,
            "exact_uri": exact_uri,
            "alias": alias,
            "alias_resolved_version": alias_resolved_version,
            "source_uri": source_uri,
            "source_run_id": source_run_id,
            "status": model_version_status,
            "tags": dict(sorted(model_version_tags.items())),
        },
        "artifact_readback": {
            "artifact_path": artifact_path,
            "original_sha256": original_model_sha256,
            "downloaded_sha256": downloaded_model_sha256,
            "size_bytes": model_size_bytes,
            "passed": original_model_sha256 == downloaded_model_sha256,
        },
        "parity": {
            "request_sha256": sha256_bytes(canonical_json_bytes(request)),
            "source_probability": round(source_probability, 15),
            "source_prediction": source_prediction,
            "registry_probability": round(registry_probability, 15),
            "registry_prediction": registry_prediction,
            "absolute_error": round(error, 15),
            "tolerance": PREDICTION_TOLERANCE,
            "passed": error <= PREDICTION_TOLERANCE
            and source_prediction == registry_prediction,
        },
        "runtime": {
            "mlflow_version": mlflow_version,
            "python_version": platform.python_version(),
        },
    }
    evidence = {
        **payload,
        "registry_evidence_id": sha256_bytes(canonical_json_bytes(payload)),
    }
    validate_registry_evidence(evidence)
    return evidence


def validate_registry_evidence(value: Mapping[str, Any]) -> None:
    _require_exact_keys(
        value,
        {
            "schema_version",
            "tracking_uri",
            "experiment_id",
            "run_id",
            "logged_model_id",
            "candidate_id",
            "source_revision",
            "registry",
            "artifact_readback",
            "parity",
            "runtime",
            "registry_evidence_id",
        },
        "registry evidence",
    )
    if value.get("schema_version") != REGISTRY_SCHEMA_VERSION:
        raise ContractError("registry evidence schema_version must equal 1")
    evidence_id = _require_sha256(
        value.get("registry_evidence_id"), "registry_evidence_id"
    )
    payload = {key: item for key, item in value.items() if key != "registry_evidence_id"}
    if sha256_bytes(canonical_json_bytes(payload)) != evidence_id:
        raise ContractError("registry_evidence_id does not match canonical payload")
    for field in (
        "tracking_uri",
        "experiment_id",
        "run_id",
        "logged_model_id",
        "source_revision",
    ):
        _require_nonempty_string(value.get(field), field)
    candidate_id = _require_sha256(value.get("candidate_id"), "candidate_id")

    registry = value.get("registry")
    artifact = value.get("artifact_readback")
    parity = value.get("parity")
    runtime = value.get("runtime")
    if not all(isinstance(item, dict) for item in (registry, artifact, parity, runtime)):
        raise ContractError(
            "registry, artifact_readback, parity and runtime must be objects"
        )

    _require_exact_keys(
        registry,
        {
            "name",
            "version",
            "exact_uri",
            "alias",
            "alias_resolved_version",
            "source_uri",
            "source_run_id",
            "status",
            "tags",
        },
        "registry evidence registry",
    )
    name = _require_nonempty_string(registry.get("name"), "registry.name")
    version = _require_nonempty_string(registry.get("version"), "registry.version")
    if not version.isdigit() or int(version) < 1:
        raise ContractError("registry.version must be a positive integer string")
    exact_uri = _require_nonempty_string(registry.get("exact_uri"), "registry.exact_uri")
    if exact_uri != f"models:/{name}/{version}":
        raise ContractError(
            "registry.exact_uri must pin the exact registered model version"
        )
    if "@" in exact_uri:
        raise ContractError("registry.exact_uri must not contain a mutable alias")
    _require_nonempty_string(registry.get("alias"), "registry.alias")
    if registry.get("alias_resolved_version") != version:
        raise ContractError(
            "registry alias does not resolve to the recorded exact version"
        )
    _require_nonempty_string(registry.get("source_uri"), "registry.source_uri")
    if registry.get("source_run_id") != value.get("run_id"):
        raise ContractError("registry source run does not match the recorded run")
    status = _require_nonempty_string(registry.get("status"), "registry.status")
    if status.upper().split(".")[-1] != "READY":
        raise ContractError("registered model version is not READY")
    tags = registry.get("tags")
    if not isinstance(tags, dict):
        raise ContractError("registry.tags must be an object")
    required_tags = {
        "knowledge_hub.candidate_id": candidate_id,
        "knowledge_hub.source_revision": value["source_revision"],
    }
    for key, expected in required_tags.items():
        if tags.get(key) != expected:
            raise ContractError(f"registry tag read-back mismatch for {key}")

    _require_exact_keys(
        artifact,
        {
            "artifact_path",
            "original_sha256",
            "downloaded_sha256",
            "size_bytes",
            "passed",
        },
        "artifact readback",
    )
    _require_nonempty_string(
        artifact.get("artifact_path"), "artifact_readback.artifact_path"
    )
    original = _require_sha256(
        artifact.get("original_sha256"), "artifact_readback.original_sha256"
    )
    downloaded = _require_sha256(
        artifact.get("downloaded_sha256"), "artifact_readback.downloaded_sha256"
    )
    if original != downloaded or artifact.get("passed") is not True:
        raise ContractError(
            "artifact read-back checksum did not match the source model"
        )
    if tags.get("knowledge_hub.model_sha256") != original:
        raise ContractError("registry model digest tag does not match artifact read-back")
    if not isinstance(artifact.get("size_bytes"), int) or artifact["size_bytes"] < 1:
        raise ContractError("artifact_readback.size_bytes must be a positive integer")

    _require_exact_keys(
        parity,
        {
            "request_sha256",
            "source_probability",
            "source_prediction",
            "registry_probability",
            "registry_prediction",
            "absolute_error",
            "tolerance",
            "passed",
        },
        "registry parity",
    )
    _require_sha256(parity.get("request_sha256"), "parity.request_sha256")
    for field in (
        "source_probability",
        "registry_probability",
        "absolute_error",
        "tolerance",
    ):
        if isinstance(parity.get(field), bool) or not isinstance(
            parity.get(field), (int, float)
        ):
            raise ContractError(f"parity.{field} must be numeric")
    if parity.get("source_prediction") not in (0, 1) or parity.get(
        "registry_prediction"
    ) not in (0, 1):
        raise ContractError("parity predictions must be binary")
    if (
        parity.get("absolute_error") > parity.get("tolerance")
        or parity.get("passed") is not True
    ):
        raise ContractError("registry model prediction parity failed")

    _require_exact_keys(runtime, {"mlflow_version", "python_version"}, "registry runtime")
    _require_nonempty_string(runtime.get("mlflow_version"), "runtime.mlflow_version")
    _require_nonempty_string(runtime.get("python_version"), "runtime.python_version")


def register_candidate(
    *,
    candidate: Mapping[str, Any],
    model_path: Path,
    sample_request_path: Path,
    tracking_uri: str,
    experiment_name: str,
    model_name: str,
    alias: str,
    download_dir: Path,
) -> dict[str, Any]:
    verify_source_model(candidate, model_path)
    request = _load_request(sample_request_path)
    tracking_uri = _require_nonempty_string(tracking_uri, "tracking_uri")
    experiment_name = _require_nonempty_string(experiment_name, "experiment_name")
    model_name = _require_nonempty_string(model_name, "model_name")
    alias = _require_nonempty_string(alias, "alias")

    try:
        import joblib
        import mlflow
        import mlflow.artifacts
        import mlflow.sklearn
        import pandas as pd
        from mlflow import MlflowClient
        from mlflow.models import infer_signature
    except ImportError as exc:
        raise ContractError(
            "registry support requires the 'registry' optional dependencies"
        ) from exc

    model = joblib.load(model_path)
    frame = pd.DataFrame([request])
    source_probability, source_prediction = _prediction(model, frame)

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_registry_uri(tracking_uri)
    experiment = mlflow.set_experiment(experiment_name)
    run_tags = {
        "knowledge_hub.candidate_id": candidate["candidate_id"],
        "knowledge_hub.source_revision": candidate["source_revision"],
        "knowledge_hub.dataset_sha256": candidate["dataset"]["sha256"],
        "knowledge_hub.model_sha256": candidate["model"]["sha256"],
        "knowledge_hub.evaluation_sha256": candidate["evaluation"]["sha256"],
    }
    with mlflow.start_run(
        experiment_id=experiment.experiment_id, tags=run_tags
    ) as active_run:
        run_id = active_run.info.run_id
        mlflow.log_params(
            {
                "candidate_id": candidate["candidate_id"],
                "dataset_name": candidate["dataset"]["name"],
                "dataset_generation": candidate["dataset"]["generation"],
                "policy_generation": candidate["evaluation"]["policy_generation"],
                "source_revision": candidate["source_revision"],
            }
        )
        for metric_name, metric_value in candidate["evaluation"]["metrics"].items():
            mlflow.log_metric(f"evaluation.{metric_name}", float(metric_value))
        mlflow.log_dict(dict(candidate), "evidence/candidate.json")
        mlflow.log_dict(request, "evidence/sample-request.json")
        mlflow.log_artifact(str(model_path), artifact_path="source")
        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            name="model",
            registered_model_name=model_name,
            signature=infer_signature(frame, model.predict(frame)),
            input_example=frame,
            await_registration_for=120,
            metadata={
                "candidate_id": candidate["candidate_id"],
                "source_revision": candidate["source_revision"],
            },
            tags=run_tags,
            skops_trusted_types=["numpy.dtype"],
        )

    if model_info.registered_model_version is None:
        raise ContractError("MLflow did not return a registered model version")
    if not model_info.model_id:
        raise ContractError("MLflow did not return a logged model ID")
    version = str(model_info.registered_model_version)
    client = MlflowClient(tracking_uri=tracking_uri, registry_uri=tracking_uri)
    for key, value in run_tags.items():
        client.set_model_version_tag(model_name, version, key, value)
    client.set_registered_model_alias(model_name, alias, version)

    run_readback = client.get_run(run_id)
    version_readback = client.get_model_version(model_name, version)
    alias_readback = client.get_model_version_by_alias(model_name, alias)
    for key, value in run_tags.items():
        if run_readback.data.tags.get(key) != value:
            raise ContractError(f"run tag read-back mismatch for {key}")
        if version_readback.tags.get(key) != value:
            raise ContractError(f"model version tag read-back mismatch for {key}")
    if str(alias_readback.version) != version:
        raise ContractError(
            "registered model alias read-back points to a different version"
        )
    if version_readback.run_id != run_id:
        raise ContractError(
            "registered model version run lineage does not match the source run"
        )

    artifact_path = f"source/{model_path.name}"
    download_dir.mkdir(parents=True, exist_ok=True)
    downloaded_path = Path(
        mlflow.artifacts.download_artifacts(
            run_id=run_id,
            artifact_path=artifact_path,
            dst_path=str(download_dir),
            tracking_uri=tracking_uri,
        )
    )
    if not downloaded_path.is_file():
        raise ContractError("MLflow artifact download did not return a file")
    downloaded_sha256 = sha256_file(downloaded_path)
    if downloaded_sha256 != candidate["model"]["sha256"]:
        raise ContractError(
            "downloaded source model digest does not match the candidate"
        )

    exact_uri = f"models:/{model_name}/{version}"
    registered_model = mlflow.sklearn.load_model(exact_uri)
    registry_probability, registry_prediction = _prediction(registered_model, frame)

    return build_registry_evidence(
        tracking_uri=tracking_uri,
        experiment_id=str(experiment.experiment_id),
        run_id=run_id,
        logged_model_id=str(model_info.model_id),
        candidate_id=candidate["candidate_id"],
        source_revision=candidate["source_revision"],
        model_name=model_name,
        version=version,
        alias=alias,
        alias_resolved_version=str(alias_readback.version),
        source_uri=str(version_readback.source),
        source_run_id=str(version_readback.run_id),
        model_version_status=str(version_readback.status),
        model_version_tags=version_readback.tags,
        artifact_path=artifact_path,
        original_model_sha256=candidate["model"]["sha256"],
        downloaded_model_sha256=downloaded_sha256,
        model_size_bytes=candidate["model"]["size_bytes"],
        request=request,
        source_probability=source_probability,
        source_prediction=source_prediction,
        registry_probability=registry_probability,
        registry_prediction=registry_prediction,
        mlflow_version=mlflow.__version__,
    )


def verify_registered_model(
    *,
    evidence: Mapping[str, Any],
    sample_request_path: Path,
    tracking_uri: str | None = None,
) -> dict[str, Any]:
    validate_registry_evidence(evidence)
    request = _load_request(sample_request_path)
    request_sha256 = sha256_bytes(canonical_json_bytes(request))
    if request_sha256 != evidence["parity"]["request_sha256"]:
        raise ContractError("sample request does not match registry evidence")
    resolved_tracking_uri = tracking_uri or evidence["tracking_uri"]
    try:
        import mlflow
        import mlflow.sklearn
        import pandas as pd
    except ImportError as exc:
        raise ContractError(
            "registry support requires the 'registry' optional dependencies"
        ) from exc
    mlflow.set_tracking_uri(resolved_tracking_uri)
    mlflow.set_registry_uri(resolved_tracking_uri)
    model = mlflow.sklearn.load_model(evidence["registry"]["exact_uri"])
    probability, prediction = _prediction(model, pd.DataFrame([request]))
    error = abs(probability - evidence["parity"]["registry_probability"])
    if (
        error > evidence["parity"]["tolerance"]
        or prediction != evidence["parity"]["registry_prediction"]
    ):
        raise ContractError(
            "fresh-process exact-version prediction does not match registry evidence"
        )
    return {
        "status": "exact_registry_version_verified",
        "registry_evidence_id": evidence["registry_evidence_id"],
        "exact_uri": evidence["registry"]["exact_uri"],
        "probability": round(probability, 15),
        "prediction": prediction,
    }
