from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from mlops_lab.monitoring import inject_drift


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
