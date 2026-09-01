#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

FILES = [
    "release-manifest.json",
    "security-contract.json",
    "access-evidence.json",
    "telemetry-evidence.json",
    "feedback-evidence.json",
    "security-test-evidence.json",
    "second-operation.json",
]
OUTPUTS = ["security-report.json", "security-evidence-ledger.json"]
BASELINE = {name: Path(name).read_text() for name in FILES}

def load(path):
    return json.loads(Path(path).read_text())

def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + "\n")

def restore():
    for name, text in BASELINE.items():
        Path(name).write_text(text)
    for name in OUTPUTS:
        Path(name).unlink(missing_ok=True)

def run_gate():
    return subprocess.run([sys.executable, "./security_gate.py"], text=True, capture_output=True)

def expect_rejected(label):
    result = run_gate()
    assert result.returncode != 0, f"{label}: gate unexpectedly accepted"
    assert not Path("security-evidence-ledger.json").exists(), f"{label}: durable ledger must not be created"
    if Path("security-report.json").exists():
        assert load("security-report.json").get("security_verified") is False, f"{label}: rejection report verified security"

def make_healthy():
    access = load("access-evidence.json")
    access["token_scoped"] = True
    access["allowed_operations"] = ["predict"]
    access["queries_last_hour"] = 420
    access["adaptive_boundary_probes_last_hour"] = 18
    access["rate_limit_key"] = "actor_and_operation"
    access["abuse_detection_enabled"] = True
    access["output"] = {
        "score_precision_decimals": 3,
        "explanations_returned": False,
        "confidence_returned": False,
        "model_version_metadata_returned": False,
        "error_detail": "generic",
    }
    write_json("access-evidence.json", access)

    telemetry = load("telemetry-evidence.json")
    telemetry["fields"] = [
        "release_id",
        "result_class",
        "coarse_segment",
        "schema_verdict",
        "protected_trace_pointer",
    ]
    telemetry["retention_days"] = 14
    telemetry["redaction_applied"] = True
    telemetry["protected_trace_pointer_used"] = True
    telemetry["access_class"] = "security-observability"
    write_json("telemetry-evidence.json", telemetry)

    feedback = load("feedback-evidence.json")
    feedback["accepted_records"] = 9300
    feedback["quarantined_records"] = 700
    feedback["authenticated_producer_records"] = 9300
    feedback["signed_records"] = 9300
    feedback["provenance_complete_records"] = 9300
    feedback["unknown_producer_accepted_records"] = 0
    feedback["semantic_validation_complete"] = True
    feedback["deduplication_complete"] = True
    feedback["accepted_producers"] = ["fraud-case-management-v7", "chargeback-settlement-v4"]
    write_json("feedback-evidence.json", feedback)

    second = load("second-operation.json")
    second["prior_token_revoked"] = True
    second["compromised_generation_inaccessible"] = True
    second["minimized_telemetry_observed"] = True
    second["clean_feedback_snapshot_observed"] = True
    second["stale_cache_access_possible"] = False
    second["mutable_alias_dependency"] = False
    second["manual_step_required"] = False
    second["clean_snapshot_build_completed"] = True
    write_json("second-operation.json", second)

restore()
expect_rejected("canonical excessive-capability/privacy incident")
print("PASS excess inference capability + privacy-unsafe telemetry + unprovenanced feedback are blocked")

restore()
contract = load("security-contract.json")
contract["authority"]["retraining_authorized"] = True
write_json("security-contract.json", contract)
expect_rejected("tampered security contract")
print("PASS tampered lifecycle authority contract is blocked")

restore()
make_healthy()
test = load("security-test-evidence.json")
test["query_budget"] = 50
write_json("security-test-evidence.json", test)
expect_rejected("weakened attacker assumptions")
print("PASS security test with weaker attacker capability is blocked")

restore()
make_healthy()
result = run_gate()
assert result.returncode == 0, result.stdout + result.stderr
report = load("security-report.json")
for field in (
    "security_verified",
    "access_control_verified",
    "output_privacy_verified",
    "telemetry_privacy_verified",
    "feedback_integrity_verified",
    "adversarial_test_verified",
    "second_operation_verified",
):
    assert report[field] is True, field
assert report["rollout_authorized"] is False
assert report["promotion_authorized"] is False
assert report["retraining_authorized"] is False
report_bytes = Path("security-report.json").read_bytes()
ledger_bytes = Path("security-evidence-ledger.json").read_bytes()

replay = run_gate()
assert replay.returncode == 0, replay.stdout + replay.stderr
assert Path("security-report.json").read_bytes() == report_bytes
assert Path("security-evidence-ledger.json").read_bytes() == ledger_bytes
print("PASS least-privilege inference + privacy-safe telemetry + authenticated feedback are byte-idempotent")

Path("security-evidence-ledger.json").write_text('{"conflict":true}\n')
before = Path("security-evidence-ledger.json").read_bytes()
conflict = run_gate()
assert conflict.returncode != 0, "conflicting durable security state unexpectedly overwritten"
assert Path("security-evidence-ledger.json").read_bytes() == before
print("PASS conflicting durable security/privacy evidence is preserved")

restore()
print("VALIDATION PASSED")
