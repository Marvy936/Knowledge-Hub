"""FastAPI serving contract resolved through the MLflow champion alias."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import mlflow.pyfunc
import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict

from .constants import CHAMPION_ALIAS, REGISTERED_MODEL_NAME
from .workspace import configure_workspace


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenure_months: int
    monthly_spend_eur: float
    support_tickets_90d: int
    login_days_30d: int
    days_since_last_login: int
    contract_type: str
    region: str
    auto_pay: str


def create_app(workspace_path: Path | None = None) -> FastAPI:
    resolved = workspace_path or Path(
        os.environ.get("MLOPS_WORKSPACE", "labs/mlops/.runtime")
    )
    _, client = configure_workspace(resolved)
    version = client.get_model_version_by_alias(
        REGISTERED_MODEL_NAME, CHAMPION_ALIAS
    )
    threshold = float(version.tags["decision_threshold"])
    model = mlflow.pyfunc.load_model(
        f"models:/{REGISTERED_MODEL_NAME}@{CHAMPION_ALIAS}"
    )

    application = FastAPI(title="Knowledge Hub MLOps flagship serving")

    @application.get("/health")
    def health() -> dict[str, Any]:
        readback = client.get_model_version_by_alias(
            REGISTERED_MODEL_NAME, CHAMPION_ALIAS
        )
        return {
            "status": "ok",
            "model_name": REGISTERED_MODEL_NAME,
            "alias": CHAMPION_ALIAS,
            "version": int(readback.version),
            "run_id": readback.run_id,
            "dataset_sha256": readback.tags.get("dataset_sha256"),
            "decision_threshold": threshold,
        }

    @application.post("/predict")
    def predict(request: PredictionRequest) -> dict[str, Any]:
        frame = pd.DataFrame([request.model_dump()])
        values = np.asarray(model.predict(frame), dtype=float)
        if values.ndim != 2 or values.shape != (1, 2):
            raise RuntimeError(f"unexpected model output shape: {values.shape}")
        probability = float(values[0, 1])
        return {
            "prediction": int(probability >= threshold),
            "probability": round(probability, 6),
            "decision_threshold": threshold,
            "model_name": REGISTERED_MODEL_NAME,
            "alias": CHAMPION_ALIAS,
            "version": int(version.version),
            "run_id": version.run_id,
            "dataset_sha256": version.tags.get("dataset_sha256"),
        }

    return application


def app() -> FastAPI:
    """Uvicorn factory entrypoint."""

    return create_app()


def serve_smoke(workspace_path: Path) -> dict[str, Any]:
    client = TestClient(create_app(workspace_path))
    health = client.get("/health")
    health.raise_for_status()
    request = {
        "tenure_months": 8,
        "monthly_spend_eur": 79.5,
        "support_tickets_90d": 4,
        "login_days_30d": 6,
        "days_since_last_login": 19,
        "contract_type": "monthly",
        "region": "east",
        "auto_pay": "no",
    }
    prediction = client.post("/predict", json=request)
    prediction.raise_for_status()
    return {
        "status": "serving_smoke_passed",
        "health": health.json(),
        "prediction": prediction.json(),
    }
