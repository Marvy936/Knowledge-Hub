#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path


def run(expect_ok):
    result = subprocess.run(["python3", "drift_gate.py"], text=True, capture_output=True)
    if (result.returncode == 0) != expect_ok:
        raise SystemExit(f"unexpected gate result rc={result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}")
    return result


def read(path):
    return Path(path).read_bytes()


# The canonical incident is selection-biased and overclaims concept drift/retraining.
Path("drift-report.json").unlink(missing_ok=True)
Path("drift-evidence-ledger.json").unlink(missing_ok=True)
run(False)
report = json.loads(Path("drift-report.json").read_text())
assert report["drift_evidence_verified"] is False
assert report["retraining_authorized"] is False
assert not Path("drift-evidence-ledger.json").exists()
print("PASS biased fallback-excluding population and causal overclaim are blocked")

# Repair evidence without hiding the prediction-drift signal: restore the eligible denominator,
# acknowledge the policy generation change, and keep drift diagnostic rather than authoritative.
evidence = json.loads(Path("drift-evidence.json").read_text())
evidence["current_distribution_rows"] = evidence["current_eligible_requests"]
evidence["include_fallback"] = True
evidence["policy_change_acknowledged"] = True
evidence["concept_drift_claimed"] = False
evidence["retraining_requested"] = False
Path("drift-evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
run(True)
report = json.loads(Path("drift-report.json").read_text())
assert report["drift_evidence_verified"] is True
assert report["investigation_required"] is True
assert report["concept_drift_confirmed"] is False
assert report["retraining_authorized"] is False
first_report = read("drift-report.json")
first_ledger = read("drift-evidence-ledger.json")
run(True)
assert read("drift-report.json") == first_report
assert read("drift-evidence-ledger.json") == first_ledger
print("PASS exact population evidence remains diagnostic and is byte-idempotent")

# Durable evidence must never be silently replaced after acceptance.
Path("drift-evidence-ledger.json").write_text('{"conflict":true}\n')
conflict_before = read("drift-evidence-ledger.json")
run(False)
assert read("drift-evidence-ledger.json") == conflict_before
print("PASS conflicting durable drift evidence is preserved")
print("VALIDATION PASSED")
