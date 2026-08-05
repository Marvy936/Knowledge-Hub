"""Local SQLite-backed MLflow workspace and Registry authority."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import mlflow
from mlflow import MlflowClient

from .constants import EXPERIMENT_NAME, REGISTERED_MODEL_NAME


@dataclass(frozen=True)
class Workspace:
    root: Path
    database: Path
    artifacts: Path
    data: Path
    requests: Path
    reports: Path
    releases: Path
    rollback: Path
    tracking_uri: str
    experiment_id: str


def _sqlite_uri(database: Path) -> str:
    return f"sqlite:///{database.resolve().as_posix()}"


def configure_workspace(root: Path) -> tuple[Workspace, MlflowClient]:
    root = root.resolve()
    database = root / "mlflow.db"
    artifacts = root / "artifacts"
    data = root / "data"
    requests = root / "requests"
    reports = root / "reports"
    releases = root / "releases"
    rollback = root / "rollback"

    for directory in (root, artifacts, data, requests, reports, releases, rollback):
        directory.mkdir(parents=True, exist_ok=True)

    tracking_uri = _sqlite_uri(database)
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_registry_uri(tracking_uri)
    client = MlflowClient(tracking_uri=tracking_uri, registry_uri=tracking_uri)

    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        experiment_id = client.create_experiment(
            EXPERIMENT_NAME,
            artifact_location=artifacts.as_uri(),
            tags={
                "knowledge_hub.section": "19",
                "knowledge_hub.lifecycle": "local-flagship",
            },
        )
    else:
        experiment_id = experiment.experiment_id

    try:
        client.get_registered_model(REGISTERED_MODEL_NAME)
    except Exception:
        client.create_registered_model(
            REGISTERED_MODEL_NAME,
            tags={
                "task": "binary-classification",
                "owner": "knowledge-hub",
                "serialization": "skops",
            },
            description="Synthetic churn model used by the Section 19 MLOps flagship lab.",
        )

    workspace = Workspace(
        root=root,
        database=database,
        artifacts=artifacts,
        data=data,
        requests=requests,
        reports=reports,
        releases=releases,
        rollback=rollback,
        tracking_uri=tracking_uri,
        experiment_id=str(experiment_id),
    )
    return workspace, client
