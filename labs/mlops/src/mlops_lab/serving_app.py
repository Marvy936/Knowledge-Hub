from __future__ import annotations

import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal, Mapping

from .contracts import ContractError, read_json
from .serving import validate_deployment_manifest


@dataclass(frozen=True)
class ServingRuntime:
    deployment: Mapping[str, Any]
    artifact_manifest: Mapping[str, Any]
    model: Any
    validate_record: Callable[[dict[str, Any]], None]

    def ready_payload(self) -> dict[str, Any]:
        return {
            "status": "ready",
            "service_name": self.deployment["service_name"],
            "deployment_id": self.deployment["deployment_id"],
            "generation": self.deployment["generation"],
            "release_id": self.deployment["release_id"],
            "model_sha256": self.deployment["model"]["sha256"],
            "registry_exact_uri": self.deployment["model"]["exact_uri"],
            "image_digest": self.deployment["image"]["digest"],
        }

    def predict(self, record: dict[str, Any]) -> dict[str, Any]:
        self.validate_record(record)
        try:
            import pandas as pd
        except ImportError as exc:
            raise ContractError("serving support requires pandas") from exc

        feature_columns = self.artifact_manifest.get("feature_columns")
        if not isinstance(feature_columns, list) or not all(
            isinstance(value, str) and value for value in feature_columns
        ):
            raise ContractError("artifact manifest feature_columns are invalid")
        frame = pd.DataFrame([record], columns=feature_columns)
        probabilities = self.model.predict_proba(frame)
        probability = float(probabilities[0][1])
        threshold = float(self.artifact_manifest["decision_threshold"])
        prediction = int(probability >= threshold)
        return {
            "prediction": prediction,
            "probability": round(probability, 6),
            "decision_threshold": round(threshold, 6),
            "service_name": self.deployment["service_name"],
            "deployment_id": self.deployment["deployment_id"],
            "generation": self.deployment["generation"],
            "release_id": self.deployment["release_id"],
            "candidate_id": self.deployment["candidate_id"],
            "model_sha256": self.deployment["model"]["sha256"],
            "registry_exact_uri": self.deployment["model"]["exact_uri"],
            "image_digest": self.deployment["image"]["digest"],
        }


def validate_runtime_binding(
    *,
    deployment: Mapping[str, Any],
    artifact_manifest: Mapping[str, Any],
    expected_image_digest: str | None,
) -> None:
    validate_deployment_manifest(deployment)
    if artifact_manifest.get("schema_version") != 1:
        raise ContractError("artifact manifest schema_version must equal 1")
    if artifact_manifest.get("artifact_type") != "trusted-local-scikit-learn-pipeline":
        raise ContractError("artifact manifest type is not trusted")
    if artifact_manifest.get("model_sha256") != deployment["model"]["sha256"]:
        raise ContractError("artifact model digest does not match deployment subject")
    if artifact_manifest.get("dataset_sha256") != deployment["dataset_sha256"]:
        raise ContractError("artifact dataset digest does not match deployment subject")
    if artifact_manifest.get("source_revision") != deployment["source_revision"]:
        raise ContractError("artifact source revision does not match deployment subject")
    if expected_image_digest is None or not expected_image_digest.strip():
        raise ContractError("MLOPS_IMAGE_DIGEST is required")
    if expected_image_digest.strip() != deployment["image"]["digest"]:
        raise ContractError("runtime image digest does not match deployment subject")


def load_serving_runtime(
    *,
    deployment_manifest_path: Path,
    artifact_dir: Path,
    expected_image_digest: str,
) -> ServingRuntime:
    deployment = read_json(deployment_manifest_path)
    try:
        from ml_lab.inference import load_artifact, validate_inference_record
    except ImportError as exc:
        raise ContractError(
            "serving support requires the Machine Learning flagship package"
        ) from exc

    model, artifact_manifest = load_artifact(artifact_dir)
    validate_runtime_binding(
        deployment=deployment,
        artifact_manifest=artifact_manifest,
        expected_image_digest=expected_image_digest,
    )
    return ServingRuntime(
        deployment=deployment,
        artifact_manifest=artifact_manifest,
        model=model,
        validate_record=validate_inference_record,
    )


def load_runtime_from_environment() -> ServingRuntime:
    deployment_path = os.environ.get(
        "MLOPS_DEPLOYMENT_MANIFEST", "/runtime/deployment.json"
    )
    artifact_dir = os.environ.get("MLOPS_ARTIFACT_DIR", "/runtime/artifact")
    image_digest = os.environ.get("MLOPS_IMAGE_DIGEST", "")
    return load_serving_runtime(
        deployment_manifest_path=Path(deployment_path),
        artifact_dir=Path(artifact_dir),
        expected_image_digest=image_digest,
    )


def create_app(runtime: ServingRuntime | None = None):
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel, ConfigDict, Field
    except ImportError as exc:
        raise ContractError("serving support requires FastAPI and Pydantic") from exc

    class PredictionRequest(BaseModel):
        model_config = ConfigDict(extra="forbid")

        tenure_months: int = Field(ge=0, le=120)
        monthly_spend_eur: float = Field(ge=5.0, le=250.0)
        support_tickets_90d: int = Field(ge=0, le=30)
        login_days_30d: int = Field(ge=0, le=30)
        days_since_last_login: int = Field(ge=0, le=180)
        contract_type: Literal["monthly", "annual", "two_year"]
        region: Literal["west", "central", "east", "north"]
        auto_pay: Literal["yes", "no"]

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.runtime = runtime or load_runtime_from_environment()
        yield

    app = FastAPI(
        title="Knowledge Hub MLOps Serving",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )

    @app.get("/healthz")
    def health() -> dict[str, str]:
        return {"status": "live"}

    @app.get("/readyz")
    def ready() -> dict[str, Any]:
        return app.state.runtime.ready_payload()

    @app.post("/v1/predict")
    def predict(request: PredictionRequest) -> dict[str, Any]:
        try:
            return app.state.runtime.predict(request.model_dump())
        except RuntimeError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return app


app = create_app()
