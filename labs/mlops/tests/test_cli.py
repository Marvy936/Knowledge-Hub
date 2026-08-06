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
    assert "Deterministic lineage, registry, serving and promotion contracts" in completed.stdout
    assert "snapshot" in completed.stdout
    assert "evaluation-from-training" in completed.stdout
    assert "candidate" in completed.stdout
    assert "promote" in completed.stdout
    assert "registry-roundtrip" in completed.stdout
    assert "registry-verify" in completed.stdout
    assert "deployment" in completed.stdout
    assert "routing-state" in completed.stdout
    assert "route" in completed.stdout
    assert "rollback" in completed.stdout
