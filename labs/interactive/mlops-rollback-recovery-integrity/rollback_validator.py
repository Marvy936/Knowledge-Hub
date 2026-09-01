#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

FILES = [
    "rollback-contract.json",
    "known-good-release.json",
    "decision-record.json",
    "rollback-operation.json",
    "runtime-state.json",
    "recovery-window.json",
    "side-effects.json",
    "second-operation.json",
]
OUTPUTS = ["rollback-report.json", "rollback-evidence-ledger.json"]
BASELINE = {name: Path(name).read_text() for name in FILES}


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + "\n")


def load(path):
    return json.loads(Path(path).read_text())


def restore():
    for name, text in BASELINE.items():
        Path(name).write_text(text)
    for name in OUTPUTS:
        Path(name).unlink(missing_ok=True)


def run_gate():
    return subprocess.run(
        [sys.executable, "./rollback_gate.py"],
        text=True,
        capture_output=True,
    )


def expect_rejected(label):
    result = run_gate()
    assert result.returncode != 0, f"{label}: gate unexpectedly accepted"
    assert not Path("rollback-evidence-ledger.json").exists(), f"{label}: durable ledger must not be created"
    if Path("rollback-report.json").exists():
        report = load("rollback-report.json")
        assert report.get("recovery_verified") is False, f"{label}: rejection report must not verify recovery"


def make_healthy():
    operation = load("rollback-operation.json")
    operation["read_before_retry_performed"] = True
    operation["compare_and_set_preserved"] = True
    operation["retry_submitted"] = False
    write_json("rollback-operation.json", operation)

    target = load("known-good-release.json")
    runtime = load("runtime-state.json")
    runtime["target_traffic_share"] = 1.0
    runtime["feature_service_generation"] = target["feature_generation"]
    runtime["threshold_policy"] = target["threshold_policy"]
    runtime["fallback_policy"] = target["fallback_policy"]
    runtime["resource_class"] = target["resource_class"]
    for replica in runtime["replicas"]:
        replica["loaded_release_id"] = target["release_id"]
        for field in ("model_digest", "serving_image", "feature_generation", "schema_generation", "threshold_policy", "fallback_policy", "resource_class"):
            replica[field] = target[field]
    journey = runtime["synthetic_journey"]
    journey["target_release_verified"] = True
    journey["feature_generation_verified"] = True
    journey["policy_generation_verified"] = True
    journey["fallback_generation_verified"] = True
    write_json("runtime-state.json", runtime)

    window = load("recovery-window.json")
    window["successful_model_predictions"] = 1994
    window["fallback_responses"] = 6
    window["deadline_successful_predictions"] = 1984
    window["p95_end_to_end_ms"] = 118
    window["mature_outcomes_observed"] = 1960
    window["mature_successful_outcomes"] = 1940
    write_json("recovery-window.json", window)

    sidefx = load("side-effects.json")
    sidefx["resolved_operations"] = sidefx["affected_operations"]
    sidefx["compensated_operations"] = 10
    sidefx["irreversible_followups_completed"] = True
    write_json("side-effects.json", sidefx)

    second = load("second-operation.json")
    second["mutable_alias_dependency"] = False
    second["manual_step_required"] = False
    second["loaded_parity_reproduced"] = True
    write_json("second-operation.json", second)


restore()
expect_rejected("canonical mixed rollback")
print("PASS alias/control-plane rollback without loaded composite parity is blocked")

restore()
contract = load("rollback-contract.json")
contract["authority"]["promotion_authorized"] = True
write_json("rollback-contract.json", contract)
expect_rejected("tampered rollback contract")
print("PASS tampered rollback authority contract is blocked")

restore()
make_healthy()
accepted = run_gate()
assert accepted.returncode == 0, accepted.stdout + accepted.stderr
report = load("rollback-report.json")
assert report["recovery_verified"] is True
assert report["component_recovery_verified"] is True
assert report["journey_recovery_verified"] is True
assert report["business_recovery_verified"] is True
assert report["reconciliation_verified"] is True
assert report["second_operation_verified"] is True
assert report["incident_closed"] is True
assert report["root_cause_model_confirmed"] is False
assert report["rollout_authorized"] is False
assert report["promotion_authorized"] is False
assert report["retraining_authorized"] is False
report_bytes = Path("rollback-report.json").read_bytes()
ledger_bytes = Path("rollback-evidence-ledger.json").read_bytes()

replay = run_gate()
assert replay.returncode == 0, replay.stdout + replay.stderr
assert Path("rollback-report.json").read_bytes() == report_bytes
assert Path("rollback-evidence-ledger.json").read_bytes() == ledger_bytes
print("PASS exact composite rollback + stable recovery evidence is byte-idempotent")

Path("rollback-evidence-ledger.json").write_text('{"conflict":true}\n')
conflict_before = Path("rollback-evidence-ledger.json").read_bytes()
conflict = run_gate()
assert conflict.returncode != 0, "conflicting durable rollback state unexpectedly overwritten"
assert Path("rollback-evidence-ledger.json").read_bytes() == conflict_before
print("PASS conflicting durable rollback evidence is preserved")

restore()
print("VALIDATION PASSED")
