from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest

from mlops_lab.monitoring import (
    build_baseline_profile,
    build_monitoring_window,
    compare_drift,
    inject_drift,
)


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_live_retraining_runtime.py"
SPEC = importlib.util.spec_from_file_location("run_live_retraining_runtime", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


def test_subject_sha_requires_exact_lowercase_git_sha1() -> None:
    good = "a" * 40
    assert runtime._require_subject_sha(good) == good

    with pytest.raises(runtime.LiveRetrainingError, match="40-character"):
        runtime._require_subject_sha("a" * 39)
    with pytest.raises(runtime.LiveRetrainingError, match="40-character"):
        runtime._require_subject_sha("A" * 40)


def test_tracking_endpoint_is_loopback_only_and_explicit() -> None:
    assert runtime._tracking_endpoint("http://127.0.0.1:5057") == (
        "127.0.0.1",
        5057,
    )
    assert runtime._tracking_endpoint("http://localhost:5057") == (
        "127.0.0.1",
        5057,
    )

    for value in (
        "http://0.0.0.0:5057",
        "https://127.0.0.1:5057",
        "http://127.0.0.1",
        "http://127.0.0.1:5057/path",
    ):
        with pytest.raises(runtime.LiveRetrainingError):
            runtime._tracking_endpoint(value)


def test_deterministic_monitoring_shift_changes_bounded_records() -> None:
    baseline = runtime._records(100)
    shifted = inject_drift(baseline, mode="shift")

    assert len(baseline) == len(shifted) == 100
    assert baseline != shifted
    assert baseline == runtime._records(100)
    assert shifted == inject_drift(runtime._records(100), mode="shift")
    assert all(record["contract_type"] == "monthly" for record in shifted)
    assert all(record["auto_pay"] == "no" for record in shifted)


def test_event_generation_is_deterministic_and_success_only() -> None:
    records = runtime._records(25)
    first = runtime._events(records)
    second = runtime._events(runtime._records(25))

    assert first == second
    assert len(first) == 25
    assert all(event["success"] is True for event in first)
    assert all(event["prediction"] in {0, 1} for event in first)
    assert all(0.0 <= event["probability"] <= 1.0 for event in first)
    assert all(event["latency_ms"] >= 0 for event in first)


def test_driver_monitoring_corpus_crosses_exact_drift_gate() -> None:
    baseline_records = runtime._records()
    baseline = build_baseline_profile(
        events=runtime._events(baseline_records),
        profile_name="live-retraining-baseline",
        generation="live-retraining-v1",
    )
    shifted = inject_drift(baseline_records, mode="shift")
    window = build_monitoring_window(
        events=runtime._events(shifted),
        baseline=baseline,
        deployment_id="a" * 64,
    )
    report = compare_drift(
        baseline=baseline,
        window=window,
        minimum_successful_events=100,
        numeric_psi_threshold=0.20,
        categorical_tvd_threshold=0.15,
        prediction_rate_delta_threshold=0.10,
        maximum_error_rate=0.05,
    )

    assert report["status"] == "drift_detected"
    assert report["observed_successful_events"] == 200
    assert report["observed_failed_events"] == 0
    assert report["observed_no_data"] is False
    assert report["exceeded_numeric_features"] or report["exceeded_categorical_features"]


def test_retraining_snapshot_adds_one_unique_row_without_touching_baseline(
    tmp_path: Path,
) -> None:
    baseline = tmp_path / "baseline.csv"
    baseline.write_text(
        "customer_id,tenure_months,monthly_spend_eur,support_tickets_90d,"
        "login_days_30d,days_since_last_login,contract_type,region,auto_pay,"
        "churned_next_30d\n"
        "1,12,50.0,1,20,2,annual,west,yes,0\n"
        "2,6,75.0,3,10,7,monthly,east,no,1\n",
        encoding="utf-8",
    )
    before = baseline.read_bytes()
    first = tmp_path / "retraining-1.csv"
    second = tmp_path / "retraining-2.csv"

    base_rows, new_rows, first_sha = runtime._build_retraining_snapshot(
        baseline,
        first,
    )
    _, second_rows, second_sha = runtime._build_retraining_snapshot(
        baseline,
        second,
    )

    assert baseline.read_bytes() == before
    assert base_rows == 2
    assert new_rows == second_rows == 3
    assert first_sha == second_sha
    assert first.read_bytes() == second.read_bytes()

    with first.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["customer_id"] for row in rows] == ["1", "2", "3"]
    assert rows[-1]["churned_next_30d"] == rows[0]["churned_next_30d"]
