#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

FIXTURES = [
    "release-manifest.json",
    "performance-contract.json",
    "runtime-state.json",
    "traffic-evidence.json",
    "cost-evidence.json",
    "second-window.json",
]
OUTPUTS = ["performance-report.json", "performance-evidence-ledger.json"]
originals = {p: Path(p).read_bytes() for p in FIXTURES}


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + "\n")


def clear_outputs():
    for path in OUTPUTS:
        Path(path).unlink(missing_ok=True)


def run(expect_success):
    cp = subprocess.run(["python3", "./performance_gate.py"], capture_output=True, text=True)
    if expect_success and cp.returncode != 0:
        raise AssertionError(f"expected gate success, got {cp.returncode}: {cp.stderr.strip()}")
    if not expect_success and cp.returncode == 0:
        raise AssertionError("expected gate rejection, got success")
    return cp


try:
    clear_outputs()

    # Canonical incident must be rejected by a correct gate.
    run(False)
    report = json.loads(Path("performance-report.json").read_text())
    assert report["performance_evidence_verified"] is False
    assert report["cost_evidence_verified"] is False
    assert report["optimization_authorized"] is False
    assert not Path("performance-evidence-ledger.json").exists()
    print("PASS HTTP-200 / average-cost optimization incident is blocked")

    # Repair the runtime and evidence while keeping the exact immutable subject.
    runtime = json.loads(originals["runtime-state.json"])
    runtime["min_replicas"] = 2
    runtime["ready_replicas_observed"] = 2
    runtime["scale_to_zero_enabled"] = False
    write_json("runtime-state.json", runtime)

    traffic = json.loads(originals["traffic-evidence.json"])
    traffic.update({
        "model_invocations": 5990,
        "successful_model_predictions": 5990,
        "deadline_successful_model_predictions": 5960,
        "fallback_responses": 10,
        "average_latency_ms": 72,
        "warm_p95_ms": 102,
        "cold_p95_ms": 510,
        "end_to_end_p99_ms": 144,
        "queue_p99_ms": 24,
        "oldest_queue_age_ms": 37,
        "in_flight_high_water": 12,
        "queue_depth_high_water": 5,
        "gpu_memory_high_water_gib": 13.4,
        "downstream_p95_ms": 34,
        "raw_response_rps": 50.0,
        "reported_useful_rps": 5960 / 120,
        "monitoring_coverage": 0.997,
    })
    write_json("traffic-evidence.json", traffic)

    cost = json.loads(originals["cost-evidence.json"])
    cost.update({
        "allocated_workload_cost_eur": 45.0,
        "idle_cost_eur": 5.0,
        "allocation_policy": "idle_explicit",
        "reported_idle_included": True,
        "reported_total_cost_eur": 50.0,
        "reported_denominator": "deadline_successful_model_predictions",
        "reported_denominator_count": 5960,
        "reported_cost_per_operation_eur": 50.0 / 5960,
        "fallback_cost_eur": 0.08,
    })
    write_json("cost-evidence.json", cost)

    second = json.loads(originals["second-window.json"])
    second.update({
        "input_mix": "merchant-segments-v4",
        "min_replicas": 2,
        "max_replicas": 12,
        "concurrency_target": 1,
        "cost_currency": "EUR",
        "cost_denominator": "deadline_successful_model_predictions",
        "idle_cost_included": True,
        "allocation_policy": "idle_explicit",
        "eligible_requests": 6000,
        "http_200_responses": 6000,
        "model_invocations": 5985,
        "successful_model_predictions": 5985,
        "deadline_successful_model_predictions": 5950,
        "fallback_responses": 15,
        "schema_rejections": 0,
        "duplicate_retries": 0,
        "monitoring_coverage": 0.996,
        "warm_p95_ms": 104,
        "cold_p95_ms": 520,
        "end_to_end_p99_ms": 146,
        "queue_p99_ms": 25,
        "oldest_queue_age_ms": 38,
        "in_flight_high_water": 13,
        "queue_depth_high_water": 5,
        "gpu_memory_high_water_gib": 13.2,
        "downstream_p95_ms": 35,
        "useful_rps": 5950 / 120,
        "allocated_workload_cost_eur": 45.5,
        "idle_cost_eur": 5.075,
        "reported_total_cost_eur": 50.575,
        "cost_denominator_count": 5950,
        "cost_per_deadline_successful_prediction_eur": 0.0085,
        "cost_window_matches_performance": True,
        "warm_cache_preloaded": False,
        "manual_idle_reallocation": False,
        "complete_window": True,
        "reproducible_from_saved_manifest": True,
    })
    write_json("second-window.json", second)

    clear_outputs()
    run(True)
    report_bytes = Path("performance-report.json").read_bytes()
    ledger_bytes = Path("performance-evidence-ledger.json").read_bytes()
    report = json.loads(report_bytes)
    assert report["performance_evidence_verified"] is True
    assert report["cost_evidence_verified"] is True
    assert report["second_window_verified"] is True
    assert report["optimization_authorized"] is False
    assert report["rollout_authorized"] is False
    assert report["promotion_authorized"] is False
    assert report["retraining_authorized"] is False

    run(True)
    assert Path("performance-report.json").read_bytes() == report_bytes
    assert Path("performance-evidence-ledger.json").read_bytes() == ledger_bytes
    print("PASS useful-work latency and idle-inclusive cost evidence is byte-idempotent")

    # Authority contract tampering must fail before durable acceptance.
    contract = json.loads(originals["performance-contract.json"])
    contract["authority"]["optimization_authorized"] = True
    write_json("performance-contract.json", contract)
    clear_outputs()
    run(False)
    assert not Path("performance-evidence-ledger.json").exists()
    print("PASS tampered performance authority contract is rejected")

    # Restore the exact contract, create accepted state, then prove conflicts are preserved.
    Path("performance-contract.json").write_bytes(originals["performance-contract.json"])
    clear_outputs()
    run(True)
    Path("performance-evidence-ledger.json").write_text('{"conflict":true}\n')
    Path("performance-report.json").unlink(missing_ok=True)
    cp = run(False)
    assert "conflicting durable state" in cp.stderr
    assert Path("performance-evidence-ledger.json").read_text() == '{"conflict":true}\n'
    print("PASS conflicting durable performance evidence is preserved")

    print("VALIDATION PASSED")
finally:
    for path, data in originals.items():
        Path(path).write_bytes(data)
    clear_outputs()
