"""Approval-bound Registry promotion and alias rollback."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import mlflow.pyfunc

from .constants import (
    CANDIDATE_ALIAS,
    CANARY_SCHEMA_VERSION,
    CHAMPION_ALIAS,
    RELEASE_SCHEMA_VERSION,
    REGISTERED_MODEL_NAME,
    ROLLBACK_SCHEMA_VERSION,
)
from .errors import PromotionRefused, RollbackRefused
from .io_utils import read_json_object, write_json_atomic
from .workspace import configure_workspace


def _alias_version(client: Any, alias: str) -> int | None:
    try:
        return int(
            client.get_model_version_by_alias(REGISTERED_MODEL_NAME, alias).version
        )
    except Exception:
        return None


def promote_candidate(
    workspace_root: Path,
    request_path: Path,
    *,
    approver: str,
    canary_report_path: Path | None = None,
) -> dict[str, Any]:
    workspace, client = configure_workspace(workspace_root)
    request = read_json_object(request_path)
    if request.get("promotion_gate") != "passed":
        raise PromotionRefused("promotion request does not contain a passed gate")
    if request.get("model_name") != REGISTERED_MODEL_NAME:
        raise PromotionRefused("promotion request targets a different registered model")

    candidate_version = int(request["candidate_version"])
    alias_candidate = _alias_version(client, CANDIDATE_ALIAS)
    if alias_candidate != candidate_version:
        raise PromotionRefused(
            f"candidate alias is {alias_candidate}; request expects {candidate_version}"
        )

    version = client.get_model_version(REGISTERED_MODEL_NAME, str(candidate_version))
    if version.tags.get("promotion_gate") != "passed":
        raise PromotionRefused("candidate Registry version lacks a passed gate tag")
    if version.tags.get("dataset_sha256") != request.get("dataset_sha256"):
        raise PromotionRefused("candidate Registry lineage differs from request dataset")

    previous_champion = _alias_version(client, CHAMPION_ALIAS)
    expected_previous = request.get("previous_champion_version")
    if expected_previous is not None and previous_champion != int(expected_previous):
        raise PromotionRefused(
            f"champion changed after request: expected {expected_previous}, got {previous_champion}"
        )

    canary: dict[str, Any] | None = None
    if previous_champion is not None:
        if canary_report_path is None:
            raise PromotionRefused("promotion over an incumbent requires canary evidence")
        canary = read_json_object(canary_report_path)
        if canary.get("schema_version") != CANARY_SCHEMA_VERSION:
            raise PromotionRefused("unsupported canary evidence schema")
        if canary.get("status") != "passed":
            raise PromotionRefused("canary evidence did not pass")
        if int(canary.get("champion_version")) != previous_champion:
            raise PromotionRefused("canary champion version is stale")
        if int(canary.get("candidate_version")) != candidate_version:
            raise PromotionRefused("canary candidate version differs from request")
        if canary.get("dataset_sha256") != request.get("dataset_sha256"):
            raise PromotionRefused("canary and request use different dataset generations")

    client.set_registered_model_alias(
        REGISTERED_MODEL_NAME, CHAMPION_ALIAS, str(candidate_version)
    )
    readback = _alias_version(client, CHAMPION_ALIAS)
    if readback != candidate_version:
        raise PromotionRefused("champion alias read-back does not match promoted version")

    client.set_model_version_tag(
        REGISTERED_MODEL_NAME, str(candidate_version), "promoted_by", approver
    )
    client.set_model_version_tag(
        REGISTERED_MODEL_NAME,
        str(candidate_version),
        "previous_champion_version",
        str(previous_champion) if previous_champion is not None else "none",
    )

    release_path = workspace.releases / f"release-v{candidate_version}.json"
    release = write_json_atomic(
        release_path,
        {
            "schema_version": RELEASE_SCHEMA_VERSION,
            "status": "promoted",
            "model_name": REGISTERED_MODEL_NAME,
            "candidate_version": candidate_version,
            "champion_alias_readback": readback,
            "previous_champion_version": previous_champion,
            "approver": approver,
            "promotion_request_path": str(request_path.resolve()),
            "promotion_request_sha256": request["evidence_sha256"],
            "canary_report_path": (
                str(canary_report_path.resolve()) if canary_report_path else None
            ),
            "canary_report_sha256": canary.get("evidence_sha256") if canary else None,
            "dataset_sha256": request["dataset_sha256"],
            "candidate_run_id": request["candidate_run_id"],
            "candidate_model_id": request.get("candidate_model_id"),
            "decision_threshold": request["decision_threshold"],
            "test_metrics": request["test_metrics"],
        },
    )

    model = mlflow.pyfunc.load_model(
        f"models:/{REGISTERED_MODEL_NAME}@{CHAMPION_ALIAS}"
    )
    input_example = {
        "tenure_months": 8,
        "monthly_spend_eur": 79.5,
        "support_tickets_90d": 4,
        "login_days_30d": 6,
        "days_since_last_login": 19,
        "contract_type": "monthly",
        "region": "east",
        "auto_pay": "no",
    }
    import pandas as pd

    probabilities = model.predict(pd.DataFrame([input_example]))
    positive_probability = float(probabilities[0][1])

    return {
        "status": "promoted",
        "release": str(release_path),
        "release_evidence": release,
        "champion_version": readback,
        "previous_champion_version": previous_champion,
        "inference_readback_probability": round(positive_probability, 6),
    }


def rollback_release(
    workspace_root: Path,
    release_path: Path,
    *,
    approver: str,
) -> dict[str, Any]:
    workspace, client = configure_workspace(workspace_root)
    release = read_json_object(release_path)
    if release.get("schema_version") != RELEASE_SCHEMA_VERSION:
        raise RollbackRefused("unsupported release evidence schema")
    promoted_version = int(release["candidate_version"])
    previous_version = release.get("previous_champion_version")
    if previous_version is None:
        raise RollbackRefused("initial release has no previous champion to restore")
    previous_version = int(previous_version)

    current = _alias_version(client, CHAMPION_ALIAS)
    if current != promoted_version:
        raise RollbackRefused(
            f"stale rollback subject: champion is {current}, release promoted {promoted_version}"
        )

    client.set_registered_model_alias(
        REGISTERED_MODEL_NAME, CHAMPION_ALIAS, str(previous_version)
    )
    readback = _alias_version(client, CHAMPION_ALIAS)
    if readback != previous_version:
        raise RollbackRefused("rollback alias read-back differs from previous champion")

    client.set_model_version_tag(
        REGISTERED_MODEL_NAME, str(promoted_version), "rolled_back_by", approver
    )
    report_path = workspace.rollback / f"rollback-v{promoted_version}-to-v{previous_version}.json"
    report = write_json_atomic(
        report_path,
        {
            "schema_version": ROLLBACK_SCHEMA_VERSION,
            "status": "rolled_back",
            "model_name": REGISTERED_MODEL_NAME,
            "from_version": promoted_version,
            "to_version": previous_version,
            "champion_alias_readback": readback,
            "approver": approver,
            "release_path": str(release_path.resolve()),
            "release_sha256": release["evidence_sha256"],
        },
    )

    return {
        "status": "rolled_back",
        "rollback_report": str(report_path),
        "rollback_evidence": report,
        "champion_version": readback,
    }
