#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
from pathlib import Path

FILES = [
    "governance-contract.json",
    "release-manifest.json",
    "evidence-bundle.json",
    "approval-records.json",
    "emergency-override.json",
    "runtime-state.json",
    "audit-events.json",
    "second-operation.json",
]
OUTPUTS = ["governance-report.json", "governance-evidence-ledger.json"]
BASELINE = {name: Path(name).read_text() for name in FILES}

def load(path):
    return json.loads(Path(path).read_text())

def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + "\n")

def event_hash(event):
    body = {k: v for k, v in event.items() if k != "event_hash"}
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()

def chain(raw):
    out = []
    prev = "GENESIS"
    for item in raw:
        event = dict(item)
        event["operation_id"] = "MLOPS-PAY-GOV-OP-2026-09-r44"
        event["prev_event_hash"] = prev
        event["event_hash"] = event_hash(event)
        out.append(event)
        prev = event["event_hash"]
    return out

def restore():
    for name, text in BASELINE.items():
        Path(name).write_text(text)
    for name in OUTPUTS:
        Path(name).unlink(missing_ok=True)

def run_gate():
    return subprocess.run([sys.executable, "./governance_gate.py"], text=True, capture_output=True)

def expect_rejected(label):
    result = run_gate()
    assert result.returncode != 0, f"{label}: gate unexpectedly accepted"
    assert not Path("governance-evidence-ledger.json").exists(), f"{label}: durable ledger must not be created"
    if Path("governance-report.json").exists():
        assert load("governance-report.json").get("governance_verified") is False, f"{label}: rejection report verified governance"

def make_healthy():
    approvals = load("approval-records.json")
    records = [r for r in approvals["records"] if r["role"] != "privacy_reviewer"]
    records.append({
        "role": "business_owner",
        "actor": "business-owner-8",
        "approved": True,
        "approved_policy_generation": "review-capacity-v9",
        "approved_review_capacity_per_hour": 500,
    })
    records.append({
        "role": "privacy_reviewer",
        "actor": "privacy-reviewer-4",
        "approved": True,
        "approved_telemetry_generation": "fraud-monitor-v10",
    })
    order = {"model_owner":0, "business_owner":1, "risk_approver":2, "privacy_reviewer":3}
    approvals["records"] = sorted(records, key=lambda r: order[r["role"]])
    write_json("approval-records.json", approvals)

    override = load("emergency-override.json")
    override["scope"] = "deployment_gate"
    override["expires_at"] = "2026-09-01T20:00:00Z"
    override["post_review_complete"] = True
    write_json("emergency-override.json", override)

    runtime = load("runtime-state.json")
    runtime["canary_traffic_share"] = 0.10
    runtime["human_review_capacity_per_hour"] = 500
    write_json("runtime-state.json", runtime)

    release = load("release-manifest.json")
    contract = load("governance-contract.json")
    bundle_digest = contract["evidence_bundle_digest"]
    subject_digest = contract["release_manifest_digest"]
    decision_id = contract["decision_id"]
    raw = [
        {
          "event_id":"gov-evt-101", "event":"approval_recorded",
          "actor":"model-owner-17", "role":"model_owner", "decision_id":decision_id,
          "subject_digest":subject_digest, "evidence_digest":bundle_digest,
          "approved_component":release["model_digest"], "outcome":"approved",
          "previous_state":"pending_model_review", "new_state":"model_reviewed",
          "timestamp":"2026-09-01T18:10:00Z"
        },
        {
          "event_id":"gov-evt-102", "event":"approval_recorded",
          "actor":"business-owner-8", "role":"business_owner", "decision_id":decision_id,
          "subject_digest":subject_digest, "evidence_digest":bundle_digest,
          "approved_component":release["policy_generation"], "outcome":"approved",
          "previous_state":"model_reviewed", "new_state":"business_reviewed",
          "timestamp":"2026-09-01T18:12:00Z"
        },
        {
          "event_id":"gov-evt-103", "event":"approval_recorded",
          "actor":"risk-approver-12", "role":"risk_approver", "decision_id":decision_id,
          "subject_digest":subject_digest, "evidence_digest":bundle_digest,
          "approved_component":release["release_id"], "outcome":"approved",
          "previous_state":"business_reviewed", "new_state":"risk_reviewed",
          "timestamp":"2026-09-01T18:15:00Z"
        },
        {
          "event_id":"gov-evt-104", "event":"approval_recorded",
          "actor":"privacy-reviewer-4", "role":"privacy_reviewer", "decision_id":decision_id,
          "subject_digest":subject_digest, "evidence_digest":bundle_digest,
          "approved_component":release["telemetry_generation"], "outcome":"approved",
          "previous_state":"risk_reviewed", "new_state":"privacy_reviewed",
          "timestamp":"2026-09-01T18:20:00Z"
        },
        {
          "event_id":"gov-evt-105", "event":"emergency_override_used",
          "actor":"deploy-operator-3", "role":"deployment_operator", "decision_id":decision_id,
          "subject_digest":subject_digest, "evidence_digest":bundle_digest,
          "approved_component":"deployment_gate", "outcome":"override_enabled",
          "previous_state":"privacy_reviewed", "new_state":"override_active",
          "timestamp":"2026-09-01T18:30:00Z"
        },
        {
          "event_id":"gov-evt-106", "event":"decision_recorded",
          "actor":"risk-approver-12", "role":"risk_approver", "decision_id":decision_id,
          "subject_digest":subject_digest, "evidence_digest":bundle_digest,
          "approved_component":"approved_with_conditions", "outcome":"approved_with_conditions",
          "previous_state":"override_active", "new_state":"approved_with_conditions",
          "timestamp":"2026-09-01T18:31:00Z"
        },
    ]
    write_json("audit-events.json", {"decision_id": decision_id, "events": chain(raw)})

    second = load("second-operation.json")
    second["same_evidence_bundle_observed"] = True
    second["required_roles_available"] = True
    second["override_unexpired"] = True
    second["deterministic_decision_reproduced"] = True
    second["audit_chain_reconstructable"] = True
    write_json("second-operation.json", second)

restore()
expect_rejected("canonical incomplete governance")
print("PASS missing business/privacy scope and unbounded override are blocked")

restore()
contract = load("governance-contract.json")
contract["authority"]["deployment_authorized"] = True
write_json("governance-contract.json", contract)
expect_rejected("tampered governance contract")
print("PASS tampered governance authority contract is blocked")

restore()
audit = load("audit-events.json")
audit["events"][0]["actor"] = "tampered-actor"
write_json("audit-events.json", audit)
expect_rejected("tampered audit chain")
print("PASS tampered append-only audit event is blocked")

restore()
make_healthy()
result = run_gate()
assert result.returncode == 0, result.stdout + result.stderr
report = load("governance-report.json")
for field in ("governance_verified", "approval_valid", "separation_of_duties_verified", "override_valid", "runtime_conformity_verified", "audit_chain_verified", "second_operation_verified"):
    assert report[field] is True, field
assert report["deployment_authorized"] is False
assert report["promotion_authorized"] is False
assert report["retraining_authorized"] is False
report_bytes = Path("governance-report.json").read_bytes()
ledger_bytes = Path("governance-evidence-ledger.json").read_bytes()

replay = run_gate()
assert replay.returncode == 0, replay.stdout + replay.stderr
assert Path("governance-report.json").read_bytes() == report_bytes
assert Path("governance-evidence-ledger.json").read_bytes() == ledger_bytes
print("PASS exact independent approvals + scoped override + audit chain are byte-idempotent")

Path("governance-evidence-ledger.json").write_text('{"conflict":true}\n')
before = Path("governance-evidence-ledger.json").read_bytes()
conflict = run_gate()
assert conflict.returncode != 0, "conflicting durable governance state unexpectedly overwritten"
assert Path("governance-evidence-ledger.json").read_bytes() == before
print("PASS conflicting durable governance evidence is preserved")

restore()
print("VALIDATION PASSED")
