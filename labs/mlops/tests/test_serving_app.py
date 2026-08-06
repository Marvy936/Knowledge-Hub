from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from mlops_lab.contracts import ContractError, canonical_json_bytes, sha256_bytes
from mlops_lab.registry import build_registry_evidence
from mlops_lab.serving import build_deployment_manifest
from mlops_lab.serving_app import ServingRuntime, create_app, validate_runtime_binding


FEATURE_COLUMNS = [
    "tenure_months",
    "monthly_spend_eur",
    "support_tickets_90d",
    "login_days_30d",
    "days_since_last_login",
    "contract_type",
    "region",
    "auto_pay",
]


class FakeModel:
    def predict_proba(self, frame):
        assert list(frame.columns) == FEATURE_COLUMNS
        return [[0.18, 0.82]]


def _release() -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": 1,
        "alias": "champion",
        "previous_candidate_id": None,
        "candidate_id": "a" * 64,
        "dataset_sha256": "c" * 64,
        "model_sha256": "b" * 64,
        "evaluation_sha256": "d" * 64,
        "policy_generation": "ml-training-manifest-v1",
        "source_revision": "exact-revision",
    }
    return {**payload, "release_id": sha256_bytes(canonical_json_bytes(payload))}


def _registry() -> dict[str, object]:
    return build_registry_evidence(
        tracking_uri="http://127.0.0.1:5000",
        experiment_id="1",
        run_id="run-1",
        logged_model_id="m-1",
        candidate_id="a" * 64,
        source_revision="exact-revision",
        model_name="KnowledgeHubChurn",
        version="1",
        alias="champion",
        alias_resolved_version="1",
        source_uri="models:/m-1",
        source_run_id="run-1",
        model_version_status="READY",
        model_version_tags={
            "knowledge_hub.candidate_id": "a" * 64,
            "knowledge_hub.source_revision": "exact-revision",
            "knowledge_hub.model_sha256": "b" * 64,
        },
        artifact_path="source/model.joblib",
        original_model_sha256="b" * 64,
        downloaded_model_sha256="b" * 64,
        model_size_bytes=123,
        request={"feature": 1},
        source_probability=0.75,
        source_prediction=1,
        registry_probability=0.75,
        registry_prediction=1,
        mlflow_version="3.14.0",
    )


def _deployment() -> dict[str, object]:
    return build_deployment_manifest(
        release=_release(),
        registry_evidence=_registry(),
        service_name="churn-api",
        generation="generation-1",
        image_reference="ghcr.io/example/churn-api",
        image_digest="sha256:" + "1" * 64,
    )


def _artifact_manifest() -> dict[str, object]:
    return {
        "schema_version": 1,
        "artifact_type": "trusted-local-scikit-learn-pipeline",
        "model_sha256": "b" * 64,
        "dataset_sha256": "c" * 64,
        "source_revision": "exact-revision",
        "feature_columns": FEATURE_COLUMNS,
        "decision_threshold": 0.72,
    }


def _record() -> dict[str, object]:
    return {
        "tenure_months": 18,
        "monthly_spend_eur": 84.5,
        "support_tickets_90d": 2,
        "login_days_30d": 12,
        "days_since_last_login": 5,
        "contract_type": "monthly",
        "region": "east",
        "auto_pay": "no",
    }


def _runtime() -> ServingRuntime:
    return ServingRuntime(
        deployment=_deployment(),
        artifact_manifest=_artifact_manifest(),
        model=FakeModel(),
        validate_record=lambda record: None,
    )


def test_runtime_binding_accepts_exact_subjects() -> None:
    deployment = _deployment()
    validate_runtime_binding(
        deployment=deployment,
        artifact_manifest=_artifact_manifest(),
        expected_image_digest=deployment["image"]["digest"],
    )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("model_sha256", "e" * 64, "model digest"),
        ("dataset_sha256", "e" * 64, "dataset digest"),
        ("source_revision", "other", "source revision"),
    ],
)
def test_runtime_binding_refuses_artifact_mismatch(
    field: str, value: str, message: str
) -> None:
    manifest = _artifact_manifest()
    manifest[field] = value
    deployment = _deployment()
    with pytest.raises(ContractError, match=message):
        validate_runtime_binding(
            deployment=deployment,
            artifact_manifest=manifest,
            expected_image_digest=deployment["image"]["digest"],
        )


def test_runtime_binding_requires_exact_image_digest() -> None:
    with pytest.raises(ContractError, match="image digest"):
        validate_runtime_binding(
            deployment=_deployment(),
            artifact_manifest=_artifact_manifest(),
            expected_image_digest="sha256:" + "2" * 64,
        )


def test_http_health_readiness_and_prediction_include_subject_identity() -> None:
    runtime = _runtime()
    with TestClient(create_app(runtime)) as client:
        assert client.get("/healthz").json() == {"status": "live"}
        ready = client.get("/readyz")
        assert ready.status_code == 200
        assert ready.json()["deployment_id"] == runtime.deployment["deployment_id"]

        response = client.post("/v1/predict", json=_record())
        assert response.status_code == 200
        body = response.json()
        assert body["prediction"] == 1
        assert body["probability"] == 0.82
        assert body["deployment_id"] == runtime.deployment["deployment_id"]
        assert body["generation"] == "generation-1"
        assert body["release_id"] == runtime.deployment["release_id"]
        assert body["model_sha256"] == "b" * 64
        assert body["registry_exact_uri"] == "models:/KnowledgeHubChurn/1"
        assert body["image_digest"] == "sha256:" + "1" * 64


def test_http_request_schema_refuses_extra_and_invalid_values() -> None:
    with TestClient(create_app(_runtime())) as client:
        extra = {**_record(), "unknown": "value"}
        assert client.post("/v1/predict", json=extra).status_code == 422

        invalid = deepcopy(_record())
        invalid["monthly_spend_eur"] = 999
        assert client.post("/v1/predict", json=invalid).status_code == 422


def test_prediction_validator_failure_is_a_bounded_client_error() -> None:
    def refuse(record: dict[str, object]) -> None:
        raise RuntimeError("feature contract refused")

    runtime = ServingRuntime(
        deployment=_deployment(),
        artifact_manifest=_artifact_manifest(),
        model=FakeModel(),
        validate_record=refuse,
    )
    with TestClient(create_app(runtime)) as client:
        response = client.post("/v1/predict", json=_record())
        assert response.status_code == 422
        assert response.json()["detail"] == "feature contract refused"
