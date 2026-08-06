from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_post_retraining_driver_exposes_exact_subjects() -> None:
    script = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "run_post_retraining_handoff.py"
    )
    completed = subprocess.run(
        [sys.executable, str(script), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "--completed-state" in completed.stdout
    assert "--registry-evidence" in completed.stdout
    assert "--current-routing-state" in completed.stdout
    assert "--expected-current-routing-state-id" in completed.stdout
    assert "--image-digest" in completed.stdout
