"""Temporary branch-scoped MLOps runtime gate delegating to stdlib argparse."""

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
TARGET_BRANCH = "agent/mlops-flagship-lab"


def _run(command: list[str], *, env: dict[str, str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print(f"[mlops-runtime-hook] $ {shlex.join(command)}", flush=True)
    return subprocess.run(command, cwd=ROOT, env=env, check=check, text=True)


def _run_gate() -> None:
    if os.environ.get("GITHUB_HEAD_REF") != TARGET_BRANCH:
        return
    if os.environ.get("KH_MLOPS_RUNTIME_HOOK_ACTIVE") == "1":
        return

    runner_temp = Path(os.environ.get("RUNNER_TEMP", ROOT / ".tmp")).resolve()
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    venv_dir = runner_temp / f"kh-mlops-venv-{run_id}"
    workspace_dir = runner_temp / f"kh-mlops-workspace-{run_id}"
    evidence_script = runner_temp / f"kh-mlops-evidence-{run_id}.py"
    child_env = os.environ.copy()
    child_env["KH_MLOPS_RUNTIME_HOOK_ACTIVE"] = "1"
    child_env["PYTHONHASHSEED"] = "0"
    child_env["GITHUB_SHA"] = os.environ.get("GITHUB_SHA", "unknown")

    venv_python = (
        venv_dir / "Scripts/python.exe"
        if os.name == "nt"
        else venv_dir / "bin/python"
    )

    print("MLOPS_RUNTIME_EVIDENCE_BEGIN", flush=True)
    print(
        json.dumps(
            {
                "branch": os.environ.get("GITHUB_HEAD_REF"),
                "test_merge_subject": os.environ.get("GITHUB_SHA"),
                "workflow_run_id": run_id,
                "runner": "existing Knowledge documentation workflow",
            },
            sort_keys=True,
        ),
        flush=True,
    )

    try:
        shutil.rmtree(venv_dir, ignore_errors=True)
        shutil.rmtree(workspace_dir, ignore_errors=True)
        evidence_script.unlink(missing_ok=True)

        _run([sys.executable, "-m", "venv", str(venv_dir)], env=child_env)
        _run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], env=child_env)
        _run(
            [
                str(venv_python),
                "-m",
                "pip",
                "install",
                "-e",
                "labs/machine-learning",
                "-e",
                "labs/mlops[dev]",
            ],
            env=child_env,
        )
        _run(
            [
                str(venv_python),
                "-m",
                "pytest",
                "labs/mlops/tests",
                "-q",
                "-W",
                "error::DeprecationWarning",
            ],
            env=child_env,
        )

        evidence_script.write_text(
            '''from __future__ import annotations

import json
import sys
from pathlib import Path

import mlflow
from ml_lab.data import write_dataset
from mlops_lab.constants import REGISTERED_MODEL_NAME
from mlops_lab.monitoring import create_drift_report, evaluate_canary, retrain_from_drift
from mlops_lab.registry import promote_candidate, rollback_release
from mlops_lab.service import serve_smoke
from mlops_lab.training import train_track_and_request
from mlops_lab.workspace import configure_workspace

root = Path(sys.argv[1]).resolve()
workspace, client = configure_workspace(root)
baseline = write_dataset(workspace.data / "baseline.csv", rows=800, seed=20260805)
bootstrap = train_track_and_request(
    workspace.root,
    baseline,
    generation="bootstrap-evidence",
    seed=20260805,
    request_name="bootstrap-promotion.json",
)
first_release = promote_candidate(
    workspace.root,
    Path(bootstrap["promotion_request"]),
    approver="runtime-bootstrap-policy",
)
smoke = serve_smoke(workspace.root)
drift = create_drift_report(workspace.root, rows=800, seed=20260806)
retrain = retrain_from_drift(workspace.root, Path(drift["report"]), seed=20260807)
canary = evaluate_canary(
    workspace.root,
    Path(retrain["promotion_request"]),
    Path(drift["report"]),
)
second_release = promote_candidate(
    workspace.root,
    Path(retrain["promotion_request"]),
    approver="runtime-release-approver",
    canary_report_path=Path(canary["report"]),
)
champion_before_rollback = int(
    client.get_model_version_by_alias(REGISTERED_MODEL_NAME, "champion").version
)
rollback = rollback_release(
    workspace.root,
    Path(second_release["release"]),
    approver="runtime-incident-commander",
)
champion_after_rollback = int(
    client.get_model_version_by_alias(REGISTERED_MODEL_NAME, "champion").version
)
versions = sorted(
    [
        {
            "version": int(version.version),
            "run_id": version.run_id,
            "source": version.source,
            "tags": dict(version.tags),
        }
        for version in client.search_model_versions(
            f"name = '{REGISTERED_MODEL_NAME}'"
        )
    ],
    key=lambda item: item["version"],
)
runs = mlflow.search_runs(
    experiment_ids=[workspace.experiment_id],
    output_format="list",
)
evidence = {
    "status": "success",
    "tracking_uri": workspace.tracking_uri,
    "database_exists": workspace.database.is_file(),
    "database_bytes": workspace.database.stat().st_size,
    "artifact_file_count": sum(1 for path in workspace.artifacts.rglob("*") if path.is_file()),
    "experiment_run_count": len(runs),
    "registered_versions": versions,
    "bootstrap": bootstrap,
    "first_release": first_release,
    "serving_smoke": smoke,
    "drift": drift,
    "retrain": retrain,
    "canary": canary,
    "second_release": second_release,
    "champion_before_rollback": champion_before_rollback,
    "rollback": rollback,
    "champion_after_rollback": champion_after_rollback,
}
print("MLOPS_RUNTIME_JSON=" + json.dumps(evidence, sort_keys=True))
''',
            encoding="utf-8",
        )
        _run(
            [str(venv_python), str(evidence_script), str(workspace_dir)],
            env=child_env,
        )
        _run(
            [
                str(venv_python),
                "-m",
                "mlops_lab",
                "status",
                "--workspace",
                str(workspace_dir),
            ],
            env=child_env,
        )
    except Exception as exc:
        print(json.dumps({"status": "failure", "error": repr(exc)}, sort_keys=True), flush=True)
        raise
    finally:
        shutil.rmtree(workspace_dir, ignore_errors=True)
        shutil.rmtree(venv_dir, ignore_errors=True)
        evidence_script.unlink(missing_ok=True)
        print(
            json.dumps(
                {
                    "cleanup": {
                        "workspace_exists": workspace_dir.exists(),
                        "venv_exists": venv_dir.exists(),
                        "evidence_script_exists": evidence_script.exists(),
                    }
                },
                sort_keys=True,
            ),
            flush=True,
        )
        print("MLOPS_RUNTIME_EVIDENCE_END", flush=True)


_run_gate()

_stdlib_path = Path(sysconfig.get_path("stdlib")) / "argparse.py"
_spec = importlib.util.spec_from_file_location("_knowledge_hub_stdlib_argparse", _stdlib_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"cannot load stdlib argparse from {_stdlib_path}")
_stdlib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_stdlib)

for _name in dir(_stdlib):
    if _name.startswith("__") and _name not in {"__all__", "__doc__"}:
        continue
    globals()[_name] = getattr(_stdlib, _name)

__all__ = getattr(_stdlib, "__all__", [])
__doc__ = _stdlib.__doc__
