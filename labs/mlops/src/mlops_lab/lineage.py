from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .contracts import ContractError, read_json, sha256_file

LINEAGE_POLICY_VERSION = "ml-training-manifest-v1"


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{field} must be an object")
    return value


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value.strip()


def _require_metric(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{field} must be numeric")
    resolved = float(value)
    if resolved != resolved or resolved in (float("inf"), float("-inf")):
        raise ContractError(f"{field} must be finite")
    return resolved


def validate_training_manifest(
    manifest: Mapping[str, Any],
    *,
    dataset_path: Path,
    model_path: Path,
    expected_source_revision: str,
) -> dict[str, Any]:
    """Validate the ML flagship manifest against the exact dataset and model bytes."""

    if not dataset_path.is_file():
        raise ContractError(f"Training dataset does not exist: {dataset_path}")
    if not model_path.is_file():
        raise ContractError(f"Training model does not exist: {model_path}")

    if manifest.get("schema_version") != 1:
        raise ContractError("training manifest schema_version must equal 1")
    if manifest.get("artifact_type") != "trusted-local-scikit-learn-pipeline":
        raise ContractError("training manifest artifact_type is not trusted")
    if manifest.get("model_file") != model_path.name:
        raise ContractError("training manifest model_file does not match model path")

    dataset_sha256 = sha256_file(dataset_path)
    model_sha256 = sha256_file(model_path)
    if manifest.get("dataset_sha256") != dataset_sha256:
        raise ContractError("training manifest dataset SHA-256 does not match dataset bytes")
    if manifest.get("model_sha256") != model_sha256:
        raise ContractError("training manifest model SHA-256 does not match model bytes")

    source_revision = _require_nonempty_string(
        manifest.get("source_revision"), "training manifest source_revision"
    )
    expected_revision = _require_nonempty_string(
        expected_source_revision, "expected_source_revision"
    )
    if source_revision != expected_revision:
        raise ContractError(
            "training manifest source revision does not match execution subject"
        )

    threshold_status = _require_nonempty_string(
        manifest.get("threshold_status"), "training manifest threshold_status"
    )
    if threshold_status != "recall_gate_satisfied":
        raise ContractError("training manifest threshold acceptance gate did not pass")

    selected_model = _require_nonempty_string(
        manifest.get("selected_model"), "training manifest selected_model"
    )
    if selected_model == "dummy_most_frequent":
        raise ContractError("training manifest selected the dummy baseline")

    metrics = _require_mapping(manifest.get("test_metrics"), "training manifest test_metrics")
    required_metric_names = ("f1", "recall")
    resolved_metrics = {
        name: _require_metric(metrics.get(name), f"training manifest test_metrics.{name}")
        for name in required_metric_names
    }
    for optional_name in ("precision", "roc_auc", "accuracy"):
        if optional_name in metrics:
            resolved_metrics[optional_name] = _require_metric(
                metrics[optional_name],
                f"training manifest test_metrics.{optional_name}",
            )

    gates = _require_mapping(
        manifest.get("acceptance_gates"), "training manifest acceptance_gates"
    )
    minimum_f1 = _require_metric(
        gates.get("minimum_test_f1"), "acceptance_gates.minimum_test_f1"
    )
    minimum_recall = _require_metric(
        gates.get("minimum_test_recall"), "acceptance_gates.minimum_test_recall"
    )
    if resolved_metrics["f1"] < minimum_f1:
        raise ContractError("training manifest test f1 is below its acceptance gate")
    if resolved_metrics["recall"] < minimum_recall:
        raise ContractError("training manifest test recall is below its acceptance gate")
    if gates.get("selected_f1_must_exceed_dummy") is not True:
        raise ContractError("training manifest does not require selected f1 to beat baseline")

    library_versions = _require_mapping(
        manifest.get("library_versions"), "training manifest library_versions"
    )
    for package_name in ("python", "numpy", "pandas", "scikit_learn", "joblib"):
        _require_nonempty_string(
            library_versions.get(package_name),
            f"training manifest library_versions.{package_name}",
        )

    decision_threshold = _require_metric(
        manifest.get("decision_threshold"), "training manifest decision_threshold"
    )
    if not 0.0 <= decision_threshold <= 1.0:
        raise ContractError("training manifest decision_threshold must be between 0 and 1")

    return {
        "dataset_sha256": dataset_sha256,
        "model_sha256": model_sha256,
        "source_revision": source_revision,
        "selected_model": selected_model,
        "decision_threshold": decision_threshold,
        "test_metrics": dict(sorted(resolved_metrics.items())),
        "minimum_test_f1": minimum_f1,
        "minimum_test_recall": minimum_recall,
        "library_versions": dict(sorted(library_versions.items())),
    }


def build_evaluation_from_training_manifest(
    *,
    training_manifest_path: Path,
    dataset_path: Path,
    model_path: Path,
    expected_source_revision: str,
    policy_generation: str = LINEAGE_POLICY_VERSION,
) -> dict[str, Any]:
    manifest = read_json(training_manifest_path)
    lineage = validate_training_manifest(
        manifest,
        dataset_path=dataset_path,
        model_path=model_path,
        expected_source_revision=expected_source_revision,
    )
    policy = _require_nonempty_string(policy_generation, "policy_generation")
    metrics = dict(lineage["test_metrics"])
    metrics["decision_threshold"] = lineage["decision_threshold"]
    return {
        "accepted": True,
        "metrics": dict(sorted(metrics.items())),
        "policy_generation": policy,
    }
