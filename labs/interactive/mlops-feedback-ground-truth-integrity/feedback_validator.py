#!/usr/bin/env python3
import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PASS = "PASS: feedback gate binds realized model performance to exact prediction identity, mature versioned ground truth, idempotent corrections and action-conditioned coverage while preserving promotion and retraining authority boundaries"


def dump(obj):
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def sha_bytes(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def run_gate(gate, case_dir):
    report = case_dir / "feedback-report.json"
    cmd = [
        sys.executable,
        "-S",
        str(gate),
        "--contract",
        str(case_dir / "feedback-contract.json"),
        "--predictions",
        str(case_dir / "prediction-snapshot.json"),
        "--label-contract",
        str(case_dir / "label-contract.json"),
        "--labels",
        str(case_dir / "label-events.json"),
        "--report",
        str(report),
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc, report


def parse_stdout(proc):
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        return None


def write_case(case_dir, base, transforms=None):
    objects = {
        name: json.loads(data.decode())
        for name, data in base.items()
    }
    if transforms:
        transforms(objects)
    pred_data = dump(objects["prediction-snapshot.json"]).encode()
    label_contract_data = dump(objects["label-contract.json"]).encode()
    objects["feedback-contract.json"]["prediction_snapshot_sha256"] = sha_bytes(pred_data)
    objects["feedback-contract.json"]["label_contract_sha256"] = sha_bytes(label_contract_data)
    payloads = {
        "feedback-contract.json": dump(objects["feedback-contract.json"]).encode(),
        "prediction-snapshot.json": pred_data,
        "label-contract.json": label_contract_data,
        "label-events.json": dump(objects["label-events.json"]).encode(),
    }
    for name, data in payloads.items():
        (case_dir / name).write_bytes(data)
    return payloads


def complete_labels(objects):
    events = objects["label-events.json"]["events"]
    events.extend(
        [
            {
                "event_id": "label-003",
                "operation_id": "pay-op-003",
                "entity_id": "merchant-300",
                "label": "loss",
                "label_source": "chargeback_confirmed",
                "label_event_time": "2026-08-13T09:00:00Z",
                "maturity": "final",
                "source_sequence": 1,
            },
            {
                "event_id": "label-005f",
                "operation_id": "pay-op-005",
                "entity_id": "merchant-105",
                "label": "no_loss",
                "label_source": "settlement_final",
                "label_event_time": "2026-08-14T09:00:00Z",
                "maturity": "final",
                "source_sequence": 2,
                "supersedes_event_id": "label-005p",
            },
        ]
    )


def expect_blocked(gate, base, mutate, expected_reason=None):
    with tempfile.TemporaryDirectory() as td:
        case_dir = Path(td)
        write_case(case_dir, base, mutate)
        proc, report = run_gate(gate, case_dir)
        result = parse_stdout(proc)
        if proc.returncode == 0 or not isinstance(result, dict) or result.get("decision") != "blocked":
            raise AssertionError("case was not blocked: " + proc.stdout + proc.stderr)
        if expected_reason and expected_reason not in result.get("reasons", []):
            raise AssertionError(f"missing reason {expected_reason}: {result}")
        if report.exists():
            raise AssertionError("blocked case created feedback-report.json")
        if (case_dir / "promotion-request.json").exists() or (case_dir / "retraining-request.json").exists():
            raise AssertionError("blocked case created authority side effect")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", default="/workspace/feedback_gate.py")
    parser.add_argument("--workspace", default="/workspace")
    args = parser.parse_args()

    gate = Path(args.gate)
    workspace = Path(args.workspace)
    names = [
        "feedback-contract.json",
        "prediction-snapshot.json",
        "label-contract.json",
        "label-events.json",
    ]
    base = {name: (workspace / name).read_bytes() for name in names}
    protected = {name: hashlib.sha256(data).hexdigest() for name, data in base.items()}

    with tempfile.TemporaryDirectory() as td:
        case_dir = Path(td)
        for name, data in base.items():
            (case_dir / name).write_bytes(data)
        proc, report = run_gate(gate, case_dir)
        result = parse_stdout(proc)
        expected = {
            "overall_coverage_below_minimum",
            "action_coverage_below_minimum:approve",
        }
        if proc.returncode == 0 or not isinstance(result, dict) or result.get("decision") != "blocked":
            raise AssertionError("canonical feedback incident was not blocked")
        if set(result.get("reasons", [])) != expected:
            raise AssertionError(f"canonical reasons mismatch: {result}")
        if report.exists():
            raise AssertionError("canonical blocked incident created a report")

    with tempfile.TemporaryDirectory() as td:
        case_dir = Path(td)
        write_case(case_dir, base, complete_labels)
        proc, report = run_gate(gate, case_dir)
        result = parse_stdout(proc)
        if proc.returncode != 0 or result.get("decision") != "verified" or not report.exists():
            raise AssertionError("healthy feedback cohort did not verify: " + proc.stdout + proc.stderr)
        first_stdout = proc.stdout
        first_bytes = report.read_bytes()
        doc = json.loads(first_bytes)
        if doc.get("join_key") != "operation_id":
            raise AssertionError("report does not bind operation_id join")
        if doc.get("performance_scope") != "mature-fixed-cohort":
            raise AssertionError("report scope is not mature-fixed-cohort")
        if doc.get("realized_performance_verified") is not True:
            raise AssertionError("realized performance not verified")
        if doc.get("promotion_authorized") is not False or doc.get("retraining_authorized") is not False:
            raise AssertionError("feedback report crossed an authority boundary")
        coverage = doc.get("coverage", {})
        if coverage.get("eligible") != 6 or coverage.get("joined_final") != 6 or coverage.get("overall") != 1.0:
            raise AssertionError("healthy coverage mismatch")
        if coverage.get("provisional_events_ignored") != 1:
            raise AssertionError("provisional event was not explicitly ignored")
        if coverage.get("corrections_applied") != 2:
            raise AssertionError("correction count mismatch")
        if coverage.get("by_action", {}).get("manual_review", {}).get("coverage") != 1.0:
            raise AssertionError("manual_review coverage mismatch")
        if coverage.get("by_action", {}).get("approve", {}).get("coverage") != 1.0:
            raise AssertionError("approve coverage mismatch")
        if doc.get("confusion_matrix") != {"fn": 1, "fp": 1, "tn": 3, "tp": 1}:
            raise AssertionError(f"confusion matrix mismatch: {doc.get('confusion_matrix')}")
        if doc.get("metrics") != {
            "accuracy": 0.666667,
            "false_positive_rate": 0.25,
            "precision": 0.5,
            "recall": 0.5,
        }:
            raise AssertionError(f"metric recomputation mismatch: {doc.get('metrics')}")
        evidence = doc.get("evidence", {})
        for key in [
            "feedback_contract_sha256",
            "prediction_snapshot_sha256",
            "label_contract_sha256",
            "label_events_sha256",
        ]:
            value = evidence.get(key, "")
            if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71:
                raise AssertionError("missing exact evidence digest " + key)
        if (case_dir / "promotion-request.json").exists() or (case_dir / "retraining-request.json").exists():
            raise AssertionError("healthy verification created authority request")

        proc2, report2 = run_gate(gate, case_dir)
        if proc2.returncode != 0 or proc2.stdout != first_stdout or report2.read_bytes() != first_bytes:
            raise AssertionError("exact replay is not byte-idempotent")

        report.write_text('{"conflict":true}\n')
        before = report.read_bytes()
        proc3, _ = run_gate(gate, case_dir)
        result3 = parse_stdout(proc3)
        if proc3.returncode == 0 or "feedback_report_state_conflict" not in result3.get("reasons", []):
            raise AssertionError("conflicting report state was not rejected")
        if report.read_bytes() != before:
            raise AssertionError("conflicting report state was overwritten")

    expect_blocked(
        gate,
        base,
        lambda o: o["feedback-contract.json"].update({"contract_id": "payment-risk-feedback-v2"}),
        "unsupported_feedback_contract",
    )
    expect_blocked(
        gate,
        base,
        lambda o: o["feedback-contract.json"].update({"promotion_authorized": True}),
        "promotion_authority_forbidden",
    )
    expect_blocked(
        gate,
        base,
        lambda o: o["feedback-contract.json"].update({"retraining_authorized": True}),
        "retraining_authority_forbidden",
    )

    def foreign_release(o):
        complete_labels(o)
        o["prediction-snapshot.json"]["release_id"] = "MLOPS-PAY-RISK-PROD-FOREIGN"
    expect_blocked(gate, base, foreign_release, "release_id_mismatch")

    def duplicate_op(o):
        complete_labels(o)
        o["prediction-snapshot.json"]["rows"][5]["operation_id"] = "pay-op-005"
    expect_blocked(gate, base, duplicate_op, "duplicate_operation_id")

    def wrong_policy(o):
        complete_labels(o)
        o["prediction-snapshot.json"]["rows"][4]["action_policy"] = "review-capacity-v3"
    expect_blocked(gate, base, wrong_policy, "action_policy_mismatch")

    def immature(o):
        complete_labels(o)
        o["prediction-snapshot.json"]["rows"][4]["event_time"] = "2026-08-10T14:00:00Z"
    expect_blocked(gate, base, immature, "prediction_not_mature")

    def entity_mismatch(o):
        complete_labels(o)
        o["label-events.json"]["events"][0]["entity_id"] = "merchant-999"
    expect_blocked(gate, base, entity_mismatch, "label_entity_mismatch")

    def unknown_op(o):
        complete_labels(o)
        o["label-events.json"]["events"][0]["operation_id"] = "pay-op-999"
    expect_blocked(gate, base, unknown_op, "unknown_label_operation")

    def invalid_final_source(o):
        complete_labels(o)
        o["label-events.json"]["events"][0]["label_source"] = "review_verdict"
    expect_blocked(gate, base, invalid_final_source, "final_label_source_invalid")

    def duplicate_seq(o):
        complete_labels(o)
        for event in o["label-events.json"]["events"]:
            if event["event_id"] == "label-006b":
                event["source_sequence"] = 1
    expect_blocked(gate, base, duplicate_seq, "duplicate_source_sequence")

    def bad_supersedes(o):
        complete_labels(o)
        for event in o["label-events.json"]["events"]:
            if event["event_id"] == "label-006b":
                event["supersedes_event_id"] = "missing-event"
    expect_blocked(gate, base, bad_supersedes, "supersedes_missing_event")

    def late_label(o):
        complete_labels(o)
        for event in o["label-events.json"]["events"]:
            if event["event_id"] == "label-003":
                event["label_event_time"] = "2026-08-17T09:00:00Z"
    expect_blocked(gate, base, late_label, "label_after_maturity_as_of")

    with tempfile.TemporaryDirectory() as td:
        case_dir = Path(td)
        for name, data in base.items():
            (case_dir / name).write_bytes(data)
        pred = json.loads((case_dir / "prediction-snapshot.json").read_text())
        pred["rows"][0]["score"] = 0.91
        (case_dir / "prediction-snapshot.json").write_text(dump(pred))
        proc, report = run_gate(gate, case_dir)
        result = parse_stdout(proc)
        if "prediction_snapshot_digest_mismatch" not in result.get("reasons", []) or report.exists():
            raise AssertionError("tampered prediction bytes were not rejected")

    with tempfile.TemporaryDirectory() as td:
        case_dir = Path(td)
        for name, data in base.items():
            (case_dir / name).write_bytes(data)
        lc = json.loads((case_dir / "label-contract.json").read_text())
        lc["maturity_days"] = 29
        (case_dir / "label-contract.json").write_text(dump(lc))
        proc, report = run_gate(gate, case_dir)
        result = parse_stdout(proc)
        if "label_contract_digest_mismatch" not in result.get("reasons", []) or report.exists():
            raise AssertionError("tampered label-contract bytes were not rejected")

    for name, digest in protected.items():
        if hashlib.sha256((workspace / name).read_bytes()).hexdigest() != digest:
            raise AssertionError("protected input changed: " + name)

    if (workspace / "promotion-request.json").exists() or (workspace / "retraining-request.json").exists():
        raise AssertionError("validator found forbidden authority side effect in workspace")

    print(PASS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
