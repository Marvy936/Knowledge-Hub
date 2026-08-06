from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _record(index: int, *, shifted: bool) -> dict[str, object]:
    return {
        "tenure_months": 4 + (index % 72),
        "monthly_spend_eur": (115.0 if shifted else 35.0) + float(index % 80),
        "support_tickets_90d": 8 + (index % 6) if shifted else index % 6,
        "login_days_30d": index % 8 if shifted else 8 + (index % 20),
        "days_since_last_login": 45 + (index % 25) if shifted else index % 25,
        "contract_type": "monthly"
        if shifted
        else ("monthly", "annual", "two_year")[index % 3],
        "region": ("west", "central", "east", "north")[index % 4],
        "auto_pay": "no" if shifted else ("yes" if index % 2 == 0 else "no"),
    }


def _event(index: int, *, shifted: bool) -> dict[str, object]:
    record = _record(index, shifted=shifted)
    score = (
        float(record["monthly_spend_eur"]) / 250.0
        + int(record["support_tickets_90d"]) / 30.0
        + int(record["days_since_last_login"]) / 180.0
        + (0.12 if record["contract_type"] == "monthly" else 0.0)
        + (0.08 if record["auto_pay"] == "no" else 0.0)
    )
    probability = max(0.01, min(0.99, score / 2.0))
    return {
        "record": record,
        "success": True,
        "latency_ms": 9.0 + (index % 5),
        "prediction": int(probability >= 0.40),
        "probability": probability,
    }


def _write_jsonl(path: Path, values: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(value, sort_keys=True) + "\n" for value in values),
        encoding="utf-8",
    )


def test_monitoring_driver_requires_separate_exact_approval(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    monitoring_script = root / "scripts" / "run_monitoring_drift.py"
    approval_script = root / "scripts" / "approve_retraining.py"
    baseline_events = tmp_path / "baseline.jsonl"
    shifted_events = tmp_path / "shifted.jsonl"
    baseline_output = tmp_path / "baseline.json"
    window_output = tmp_path / "window.json"
    drift_output = tmp_path / "drift.json"
    proposal_output = tmp_path / "proposal.json"
    approval_output = tmp_path / "approval.json"
    _write_jsonl(
        baseline_events,
        [_event(index, shifted=False) for index in range(200)],
    )
    _write_jsonl(
        shifted_events,
        [_event(index, shifted=True) for index in range(200)],
    )

    monitoring = subprocess.run(
        [
            sys.executable,
            str(monitoring_script),
            "--baseline-events-jsonl",
            str(baseline_events),
            "--window-events-jsonl",
            str(shifted_events),
            "--profile-name",
            "churn-baseline",
            "--generation",
            "generation-1",
            "--deployment-id",
            "a" * 64,
            "--model-sha256",
            "b" * 64,
            "--policy-generation",
            "retraining-policy-v1",
            "--minimum-successful-events",
            "50",
            "--baseline-output",
            str(baseline_output),
            "--window-output",
            str(window_output),
            "--drift-output",
            str(drift_output),
            "--proposal-output",
            str(proposal_output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert monitoring.returncode == 5, monitoring.stderr
    proposal = json.loads(proposal_output.read_text(encoding="utf-8"))
    assert proposal["action"] == "approval_required"
    assert not approval_output.exists()

    refused = subprocess.run(
        [
            sys.executable,
            str(approval_script),
            "--proposal",
            str(proposal_output),
            "--drift-report",
            str(drift_output),
            "--expected-proposal-id",
            "f" * 64,
            "--approver",
            "ml-platform-owner",
            "--approval-generation",
            "approval-v1",
            "--output",
            str(approval_output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert refused.returncode == 2
    assert not approval_output.exists()

    approved = subprocess.run(
        [
            sys.executable,
            str(approval_script),
            "--proposal",
            str(proposal_output),
            "--drift-report",
            str(drift_output),
            "--expected-proposal-id",
            proposal["retraining_proposal_id"],
            "--approver",
            "ml-platform-owner",
            "--approval-generation",
            "approval-v1",
            "--output",
            str(approval_output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert approved.returncode == 0, approved.stderr
    approval = json.loads(approval_output.read_text(encoding="utf-8"))
    assert approval["retraining_proposal_id"] == proposal["retraining_proposal_id"]
    assert approval["authorized_action"] == "start_controlled_retraining"
