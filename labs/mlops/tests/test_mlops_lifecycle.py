from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from ml_lab.data import write_dataset
from mlops_lab.constants import REGISTERED_MODEL_NAME
from mlops_lab.errors import EvidenceIntegrityError
from mlops_lab.io_utils import bind_digest, read_json_object, verify_digest
from mlops_lab.monitoring import (
    create_drift_report,
    evaluate_canary,
    population_stability_index,
    retrain_from_drift,
)
from mlops_lab.registry import promote_candidate, rollback_release
from mlops_lab.service import serve_smoke
from mlops_lab.training import train_track_and_request
from mlops_lab.workspace import configure_workspace


def test_evidence_digest_rejects_mutation() -> None:
    payload = bind_digest({"subject": "candidate-v1", "gate": "passed"})
    verify_digest(payload)
    payload["gate"] = "failed"
    with pytest.raises(EvidenceIntegrityError, match="digest mismatch"):
        verify_digest(payload)


def test_population_stability_index_distinguishes_shift() -> None:
    baseline = pd.Series(range(1, 101), dtype=float)
    same = pd.Series(range(1, 101), dtype=float)
    shifted = pd.Series(range(81, 181), dtype=float)
    assert population_stability_index(baseline, same) < 0.01
    assert population_stability_index(baseline, shifted) > 0.20


def test_full_mlops_lifecycle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_SHA", "test-source-revision")
    workspace, client = configure_workspace(tmp_path / "workspace")
    baseline = write_dataset(workspace.data / "baseline.csv", rows=700, seed=20260805)

    bootstrap = train_track_and_request(
        workspace.root,
        baseline,
        generation="bootstrap",
        seed=20260805,
        request_name="bootstrap-promotion.json",
    )
    bootstrap_request = Path(bootstrap["promotion_request"])
    assert bootstrap["candidate_version"] == bootstrap["candidate_alias_readback"]

    tampered = read_json_object(bootstrap_request)
    tampered["candidate_version"] = 999
    tampered_path = workspace.requests / "tampered.json"
    tampered_path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(EvidenceIntegrityError, match="digest mismatch"):
        promote_candidate(
            workspace.root,
            tampered_path,
            approver="test-operator",
        )

    first_release = promote_candidate(
        workspace.root,
        bootstrap_request,
        approver="test-operator",
    )
    first_champion = int(first_release["champion_version"])
    champion_readback = client.get_model_version_by_alias(
        REGISTERED_MODEL_NAME, "champion"
    )
    assert int(champion_readback.version) == first_champion

    smoke = serve_smoke(workspace.root)
    assert smoke["status"] == "serving_smoke_passed"
    assert smoke["health"]["version"] == first_champion
    assert 0.0 <= smoke["prediction"]["probability"] <= 1.0

    drift = create_drift_report(workspace.root, rows=700, seed=20260806)
    drift_report = Path(drift["report"])
    assert drift["evidence"]["triggered"] is True
    assert drift["evidence"]["max_psi"] >= drift["evidence"]["threshold"]

    retrain = retrain_from_drift(
        workspace.root,
        drift_report,
        seed=20260807,
    )
    retrain_request = Path(retrain["promotion_request"])
    assert retrain["candidate_version"] != first_champion

    canary = evaluate_canary(
        workspace.root,
        retrain_request,
        drift_report,
    )
    canary_report = Path(canary["report"])
    assert canary["evidence"]["status"] == "passed"
    assert canary["evidence"]["route_counts"]["candidate"] == 70
    assert canary["evidence"]["route_counts"]["champion"] == 630

    second_release = promote_candidate(
        workspace.root,
        retrain_request,
        approver="release-approver",
        canary_report_path=canary_report,
    )
    second_champion = int(second_release["champion_version"])
    assert second_champion != first_champion
    assert second_release["previous_champion_version"] == first_champion

    rollback = rollback_release(
        workspace.root,
        Path(second_release["release"]),
        approver="incident-commander",
    )
    assert rollback["champion_version"] == first_champion
    final_readback = client.get_model_version_by_alias(
        REGISTERED_MODEL_NAME, "champion"
    )
    assert int(final_readback.version) == first_champion
