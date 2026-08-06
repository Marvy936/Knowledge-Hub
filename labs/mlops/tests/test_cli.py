from __future__ import annotations

import subprocess
import sys


def test_module_entrypoint_exposes_help() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "mlops_lab", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Deterministic lineage, registry and promotion contracts" in completed.stdout
    assert "snapshot" in completed.stdout
    assert "candidate" in completed.stdout
    assert "promote" in completed.stdout
    assert "registry-roundtrip" in completed.stdout
    assert "registry-verify" in completed.stdout
