from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_canary_driver_exposes_help() -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "run_canary_window.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "minimum-canary-requests" in completed.stdout
    assert "maximum-canary-error-rate" in completed.stdout
    assert "rollback-output" in completed.stdout
