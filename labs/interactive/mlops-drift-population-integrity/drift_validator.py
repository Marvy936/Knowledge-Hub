#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path


def run(expect_ok):
    result = subprocess.run(["python3", "drift_gate.py"], text=True, capture_output=True)
    if (result.returncode == 0) != expect_ok:
        raise SystemExit(
            f"unexpected gate result rc={result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}"
        )
    return result


def read(path):
    return Path(path).read_bytes()


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


# The canonical incident is selection-biased and overclaims concept drift/retraining.
Path("drift-report.json").unlink(missing_ok=True)
Path("drift-evidence-ledger.json").unlink(missing_ok=True)
run(False)
report = json.loads(Path("drift-report.json").read_text())
assert report["drift_evidence_verified"] is False
assert report["concept_drift_confirmed"] is False
assert report["retraining_authorized"] is False
assert not Path("drift-evidence-ledger.json").exists()
print("PASS biased fallback denominator and causal/retraining overclaim are blocked")

# Repair the authority boundary without fabricating predictions for fallback requests.
# The eligible denominator includes fallback, while prediction-distribution rows remain scored-only.
evidence = json.loads(Path("drift-evidence.json").read_text())
evidence["eligible_denominator_includes_fallback"] = True
evidence["fallback_reported_separately"] = True
evidence["policy_change_acknowledged"] = True
evidence["concept_drift_claimed"] = False
evidence["retraining_requested"] = False
write_json("drift-evidence.json", evidence)
run(True)
report = json.loads(Path("drift-report.json").read_text())
assert report["drift_evidence_verified"] is True
assert report["investigation_required"] is True
assert report["concept_drift_confirmed"] is False
assert report["retraining_authorized"] is False
assert evidence["current_distribution_rows"] == evidence["current_scored_requests"]
assert evidence["current_scored_requests"] + evidence["fallback_requests"] == evidence["current_eligible_requests"]

first_report = read("drift-report.json")
first_ledger = read("drift-evidence-ledger.json")
healthy_evidence = read("drift-evidence.json")
healthy_contract = read("drift-contract.json")
run(True)
assert read("drift-report.json") == first_report
assert read("drift-evidence-ledger.json") == first_ledger
print("PASS exact eligible/scored populations remain diagnostic and byte-idempotent")

# High label coverage alone must not manufacture a concept-drift claim.
adversarial = json.loads(healthy_evidence)
adversarial["label_coverage"] = 0.99
adversarial["concept_drift_claimed"] = True
write_json("drift-evidence.json", adversarial)
run(False)
report = json.loads(Path("drift-report.json").read_text())
assert report["concept_drift_confirmed"] is False
assert read("drift-evidence-ledger.json") == first_ledger
Path("drift-evidence.json").write_bytes(healthy_evidence)
print("PASS label coverage without ground-truth conditional-performance proof cannot confirm concept drift")

# The authority contract itself is immutable evidence, not a learner-adjustable threshold file.
tampered_contract = json.loads(healthy_contract)
tampered_contract["thresholds"]["minimum_rows"] = 1
write_json("drift-contract.json", tampered_contract)
run(False)
assert read("drift-evidence-ledger.json") == first_ledger
Path("drift-contract.json").write_bytes(healthy_contract)
print("PASS tampered drift authority contract is rejected")

# Durable evidence must never be silently replaced after acceptance.
Path("drift-evidence-ledger.json").write_text('{"conflict":true}\n')
conflict_before = read("drift-evidence-ledger.json")
run(False)
assert read("drift-evidence-ledger.json") == conflict_before
print("PASS conflicting durable drift evidence is preserved")
print("VALIDATION PASSED")
