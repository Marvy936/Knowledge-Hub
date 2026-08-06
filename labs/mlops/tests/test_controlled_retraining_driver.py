from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_controlled_retraining_driver_exposes_recovery_contract() -> None:
    script = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "run_controlled_retraining.py"
    )
    completed = subprocess.run(
        [sys.executable, str(script), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "--approval" in completed.stdout
    assert "--drift-report" in completed.stdout
    assert "--current-deployment" in completed.stdout
    assert "--operation-output" in completed.stdout
    assert "--recover-expected-state-id" in completed.stdout
