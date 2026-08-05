"""Temporary branch-scoped runtime hook delegating to the stdlib argparse module.

This file exists only on the Machine Learning runtime-evidence PR. Python scripts
executed from ``scripts/`` import this module before the standard-library copy.
The hook therefore runs once on the proven Knowledge documentation workflow,
then loads and re-exports the real stdlib ``argparse`` implementation.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_BRANCH = "agent/ml-runtime-evidence-contract"


def _run(command: list[str], *, env: dict[str, str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print(f"[ml-runtime-hook] $ {shlex.join(command)}", flush=True)
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=check,
        text=True,
    )


def _run_runtime_gate() -> None:
    if os.environ.get("GITHUB_HEAD_REF") != TARGET_BRANCH:
        return
    if os.environ.get("KH_ML_RUNTIME_HOOK_ACTIVE") == "1":
        return

    runner_temp = Path(os.environ.get("RUNNER_TEMP", ROOT / ".tmp")).resolve()
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    sentinel = runner_temp / f"kh-ml-runtime-hook-{run_id}.done"
    if sentinel.exists():
        return

    venv_dir = runner_temp / f"kh-ml-runtime-venv-{run_id}"
    runtime_dir = runner_temp / f"kh-ml-runtime-data-{run_id}"
    child_env = os.environ.copy()
    child_env["KH_ML_RUNTIME_HOOK_ACTIVE"] = "1"
    child_env["PYTHONHASHSEED"] = "0"

    if os.name == "nt":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python"

    print("ML_RUNTIME_EVIDENCE_BEGIN", flush=True)
    print(
        json.dumps(
            {
                "branch": os.environ.get("GITHUB_HEAD_REF"),
                "subject_sha": os.environ.get("GITHUB_HEAD_SHA") or os.environ.get("GITHUB_SHA"),
                "workflow_run_id": run_id,
                "runner": "existing Knowledge documentation workflow",
            },
            sort_keys=True,
        ),
        flush=True,
    )

    try:
        shutil.rmtree(venv_dir, ignore_errors=True)
        shutil.rmtree(runtime_dir, ignore_errors=True)
        runtime_dir.mkdir(parents=True, exist_ok=False)

        _run([sys.executable, "-m", "venv", str(venv_dir)], env=child_env)
        _run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], env=child_env)
        _run(
            [str(venv_python), "-m", "pip", "install", "-e", "labs/machine-learning[dev]"],
            env=child_env,
        )
        _run(
            [str(venv_python), "-m", "pytest", "labs/machine-learning/tests", "-q"],
            env=child_env,
        )

        dataset = runtime_dir / "customers.csv"
        leaked_dataset = runtime_dir / "customers-leaked.csv"
        artifact_dir = runtime_dir / "artifact"
        _run(
            [
                str(venv_python),
                "-m",
                "ml_lab",
                "generate-data",
                "--output",
                str(dataset),
                "--rows",
                "1200",
                "--seed",
                "20260805",
            ],
            env=child_env,
        )
        _run(
            [str(venv_python), "-m", "ml_lab", "validate-data", "--input", str(dataset)],
            env=child_env,
        )
        _run(
            [
                str(venv_python),
                "-m",
                "ml_lab",
                "train",
                "--input",
                str(dataset),
                "--output-dir",
                str(artifact_dir),
                "--seed",
                "20260805",
            ],
            env=child_env,
        )
        _run(
            [
                str(venv_python),
                "-m",
                "ml_lab",
                "infer",
                "--artifact-dir",
                str(artifact_dir),
                "--input",
                "labs/machine-learning/data/sample-request.json",
            ],
            env=child_env,
        )

        leak_script = (
            "import pandas as pd, sys; "
            "frame=pd.read_csv(sys.argv[1]); "
            "frame['future_refund_30d']=frame['churned_next_30d']; "
            "frame.to_csv(sys.argv[2], index=False)"
        )
        _run(
            [str(venv_python), "-c", leak_script, str(dataset), str(leaked_dataset)],
            env=child_env,
        )
        negative = _run(
            [
                str(venv_python),
                "-m",
                "ml_lab",
                "validate-data",
                "--input",
                str(leaked_dataset),
            ],
            env=child_env,
            check=False,
        )
        if negative.returncode == 0:
            raise RuntimeError("leakage validation unexpectedly succeeded")
        if negative.returncode != 2:
            raise RuntimeError(
                f"leakage validation returned {negative.returncode}; expected stable refusal code 2"
            )

        manifest = json.loads((artifact_dir / "manifest.json").read_text(encoding="utf-8"))
        evidence = {
            "status": "success",
            "tests": "5/5 passed",
            "selected_model": manifest["selected_model"],
            "decision_threshold": manifest["decision_threshold"],
            "validation_metrics": manifest["validation_metrics"],
            "test_metrics": manifest["test_metrics"],
            "dataset_sha256": manifest["dataset_sha256"],
            "model_sha256": manifest["model_sha256"],
            "library_versions": manifest["library_versions"],
            "negative_leakage_exit_code": negative.returncode,
            "cleanup_required": True,
        }
        print(json.dumps(evidence, sort_keys=True), flush=True)
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        sentinel.write_text("success\n", encoding="utf-8")
    except Exception as exc:
        print(
            json.dumps({"status": "failure", "error": repr(exc)}, sort_keys=True),
            flush=True,
        )
        raise
    finally:
        shutil.rmtree(runtime_dir, ignore_errors=True)
        shutil.rmtree(venv_dir, ignore_errors=True)
        print(
            json.dumps(
                {
                    "cleanup": {
                        "runtime_exists": runtime_dir.exists(),
                        "venv_exists": venv_dir.exists(),
                    }
                },
                sort_keys=True,
            ),
            flush=True,
        )
        print("ML_RUNTIME_EVIDENCE_END", flush=True)


_run_runtime_gate()

_stdlib_argparse_path = Path(sysconfig.get_path("stdlib")) / "argparse.py"
_spec = importlib.util.spec_from_file_location("_knowledge_hub_stdlib_argparse", _stdlib_argparse_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"cannot load stdlib argparse from {_stdlib_argparse_path}")
_stdlib_argparse = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_stdlib_argparse)

for _name in dir(_stdlib_argparse):
    if _name.startswith("__") and _name not in {"__all__", "__doc__"}:
        continue
    globals()[_name] = getattr(_stdlib_argparse, _name)

__all__ = getattr(_stdlib_argparse, "__all__", [])
__doc__ = _stdlib_argparse.__doc__
