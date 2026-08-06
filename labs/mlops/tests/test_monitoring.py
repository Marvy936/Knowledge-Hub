from __future__ import annotations

from copy import deepcopy

import pytest

from mlops_lab.contracts import ContractError
from mlops_lab.monitoring import (
    build_baseline_profile,
    build_monitoring_window,
    compare_drift,
    inject_drift,
    validate_baseline_profile,
    validate_monitoring_window,
)
from mlops_lab.retraining import approve_retraining, build_retraining_proposal

DEPLOYMENT_ID = "a" * 64
MODEL_SHA256 = "b" * 64


def _records(count: int = 200) -> list[dict[str, object]]:
    contract_types = ("monthly", "annual", "two_year")
    regions = ("west", "central", "east", "north")
    records: list[dict[str, object]] = []
    for index in range(count):
        records.append(
            {
                "tenure_months": 4 + (index % 72),
                "monthly_spend_eur": 35.0 + float(index % 80),
                "support_tickets_90d": index % 6,
                "login_days_30d": 8 + (index % 20),
                "days_since_last_login": index % 25,
                "contract_type": contract_types[index % len(contract_types)],
                "region": regions[index % len(regions)],
                "auto_pay": "yes" if index % 2 == 0 else "no",
            }
        )
    return records


def _events(
    records: list[dict[str, object]], *, failed_indexes: set[int] | None = None
) -> list[dict[str, object]]:
    failed = failed_indexes or set()
    events: list[dict[str, object]] = []
    for index, record in enumerate(records):
        if index in failed:
            events.append(
                {
                    "record": record,
                    "success": False,
                    "latency_ms": 15.0 + (index % 7),
                    "prediction": None,
                    "probability": None,
                }
            )
            continue
        score = (
            float(record["monthly_spend_eur"]) / 250.0
            + int(record["support_tickets_90d"]) / 30.0
            + int(record["days_since_last_login"]) / 180.0
            + (0.12 if record["contract_type"] == "monthly" else 0.0)
            + (0.08 if record["auto_pay"] == "no" else 0.0)
        )
        probability = max(0.01, min(0.99, score / 2.0))
        events.append(
            {
                "record": record,
                "success": True,
                "latency_ms": 8.0 + (index % 9),
                "prediction": int(probability >= 0.40),
                "probability": probability,
            }
        )
    return events


def _baseline():
    return build_baseline_profile(
        events=_events(_records()),
        profile_name="churn-baseline",
        generation="generation-1",
        numeric_bin_count=10,
    )


def _report(events, *, minimum=50, maximum_error_rate=0.05):
    baseline = _baseline()
    window = build_monitoring_window(
        events=events,
        baseline=baseline,
        deployment_id=DEPLOYMENT_ID,
    )
    report = compare_drift(
        baseline=baseline,
        window=window,
        minimum_successful_events=minimum,
        numeric_psi_threshold=0.20,
        categorical_tvd_threshold=0.15,
        prediction_rate_delta_threshold=0.10,
        maximum_error_rate=maximum_error_rate,
    )
    return baseline, window, report


def test_control_window_is_stable_and_does_not_store_raw_records() -> None:
    baseline, window, report = _report(_events(inject_drift(_records(), mode="control")))
    assert report["status"] == "stable"
    assert report["exceeded_numeric_features"] == []
    assert report["exceeded_categorical_features"] == []
    assert baseline["total_events"] == 200
    assert window["total_events"] == 200
    assert "observations" not in baseline
    assert "records" not in window
    validate_baseline_profile(baseline)
    validate_monitoring_window(window)


def test_reproducible_shift_is_detected() -> None:
    shifted = inject_drift(_records(), mode="shift")
    _, _, report = _report(_events(shifted))
    assert report["status"] == "drift_detected"
    assert report["exceeded_numeric_features"]
    assert report["exceeded_categorical_features"] or (
        report["prediction_rate_delta"] > report["thresholds"]["prediction_rate_delta"]
    )


def test_no_data_and_insufficient_evidence_are_explicit() -> None:
    _, empty_window, empty_report = _report([], minimum=20)
    assert empty_window["no_data"] is True
    assert empty_report["status"] == "no_data"

    _, sparse_window, sparse_report = _report(_events(_records(5)), minimum=20)
    assert sparse_window["successful_events"] == 5
    assert sparse_report["status"] == "insufficient_evidence"


def test_high_error_rate_is_operational_failure_not_drift() -> None:
    events = _events(_records(100), failed_indexes=set(range(30)))
    _, window, report = _report(events, minimum=50, maximum_error_rate=0.05)
    assert window["error_rate"] == 0.3
    assert report["status"] == "operational_failure"
    proposal = build_retraining_proposal(
        drift_report=report,
        model_sha256=MODEL_SHA256,
        policy_generation="retraining-policy-v1",
    )
    assert proposal["action"] == "blocked"


def test_drift_requires_exact_human_approval() -> None:
    _, _, report = _report(_events(inject_drift(_records(), mode="shift")))
    proposal = build_retraining_proposal(
        drift_report=report,
        model_sha256=MODEL_SHA256,
        policy_generation="retraining-policy-v1",
    )
    assert proposal["action"] == "approval_required"
    approval = approve_retraining(
        proposal=proposal,
        expected_proposal_id=proposal["retraining_proposal_id"],
        approver="ml-platform-owner",
        approval_generation="approval-2026-08-06",
    )
    assert approval["authorized_action"] == "start_controlled_retraining"
    assert approval["retraining_proposal_id"] == proposal["retraining_proposal_id"]
    assert len(approval["retraining_approval_id"]) == 64


def test_stale_or_ineligible_proposal_cannot_be_approved() -> None:
    _, _, drift_report = _report(_events(inject_drift(_records(), mode="shift")))
    proposal = build_retraining_proposal(
        drift_report=drift_report,
        model_sha256=MODEL_SHA256,
        policy_generation="retraining-policy-v1",
    )
    with pytest.raises(ContractError, match="stale or mismatched"):
        approve_retraining(
            proposal=proposal,
            expected_proposal_id="f" * 64,
            approver="ml-platform-owner",
            approval_generation="approval-v1",
        )

    _, _, stable_report = _report(_events(_records()))
    blocked = build_retraining_proposal(
        drift_report=stable_report,
        model_sha256=MODEL_SHA256,
        policy_generation="retraining-policy-v1",
    )
    with pytest.raises(ContractError, match="not eligible"):
        approve_retraining(
            proposal=blocked,
            expected_proposal_id=blocked["retraining_proposal_id"],
            approver="ml-platform-owner",
            approval_generation="approval-v1",
        )


def test_modified_drift_report_cannot_create_retraining_proposal() -> None:
    _, _, stable_report = _report(_events(_records()))
    tampered = deepcopy(stable_report)
    tampered["status"] = "drift_detected"
    with pytest.raises(ContractError, match="drift_report_id"):
        build_retraining_proposal(
            drift_report=tampered,
            model_sha256=MODEL_SHA256,
            policy_generation="retraining-policy-v1",
        )


def test_modified_proposal_cannot_be_approved() -> None:
    _, _, report = _report(_events(inject_drift(_records(), mode="shift")))
    proposal = build_retraining_proposal(
        drift_report=report,
        model_sha256=MODEL_SHA256,
        policy_generation="retraining-policy-v1",
    )
    tampered = deepcopy(proposal)
    tampered["model_sha256"] = "e" * 64
    with pytest.raises(ContractError, match="retraining_proposal_id"):
        approve_retraining(
            proposal=tampered,
            expected_proposal_id=proposal["retraining_proposal_id"],
            approver="ml-platform-owner",
            approval_generation="approval-v1",
        )


def test_profile_and_window_tampering_is_detected() -> None:
    baseline = _baseline()
    baseline["prediction"]["positive_rate"] = 0.99
    with pytest.raises(ContractError, match="baseline_profile_id"):
        validate_baseline_profile(baseline)

    clean_baseline = _baseline()
    window = build_monitoring_window(
        events=_events(_records()),
        baseline=clean_baseline,
        deployment_id=DEPLOYMENT_ID,
    )
    window["error_rate"] = 0.9
    with pytest.raises(ContractError, match="error_rate|monitoring_window_id"):
        validate_monitoring_window(window)
