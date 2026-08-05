"""Command-line state machine for the MLOps flagship lifecycle."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from ml_lab.data import write_dataset

from .constants import (
    DEFAULT_BASELINE_SEED,
    DEFAULT_CURRENT_SEED,
    DEFAULT_RETRAIN_SEED,
    DEFAULT_ROWS,
    REGISTERED_MODEL_NAME,
)
from .errors import MLOpsLabError
from .monitoring import create_drift_report, evaluate_canary, retrain_from_drift
from .registry import promote_candidate, rollback_release
from .service import serve_smoke
from .training import train_track_and_request
from .workspace import configure_workspace


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mlops-lab",
        description="Knowledge Hub MLOps and ML Platforms flagship lab",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    bootstrap = commands.add_parser("bootstrap", help="create baseline runs and candidate")
    bootstrap.add_argument("--workspace", type=Path, required=True)
    bootstrap.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    bootstrap.add_argument("--seed", type=int, default=DEFAULT_BASELINE_SEED)

    promote = commands.add_parser("promote", help="approve and assign the champion alias")
    promote.add_argument("--workspace", type=Path, required=True)
    promote.add_argument("--request", type=Path, required=True)
    promote.add_argument("--approver", required=True)
    promote.add_argument("--canary-report", type=Path)

    smoke = commands.add_parser("serve-smoke", help="exercise health and prediction HTTP paths")
    smoke.add_argument("--workspace", type=Path, required=True)

    monitor = commands.add_parser("monitor", help="create current data and drift evidence")
    monitor.add_argument("--workspace", type=Path, required=True)
    monitor.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    monitor.add_argument("--seed", type=int, default=DEFAULT_CURRENT_SEED)

    retrain = commands.add_parser("retrain", help="train only from actionable drift evidence")
    retrain.add_argument("--workspace", type=Path, required=True)
    retrain.add_argument("--drift-report", type=Path, required=True)
    retrain.add_argument("--seed", type=int, default=DEFAULT_RETRAIN_SEED)

    canary = commands.add_parser("canary", help="compare champion and exact candidate")
    canary.add_argument("--workspace", type=Path, required=True)
    canary.add_argument("--request", type=Path, required=True)
    canary.add_argument("--drift-report", type=Path, required=True)

    rollback = commands.add_parser("rollback", help="restore the previous champion alias")
    rollback.add_argument("--workspace", type=Path, required=True)
    rollback.add_argument("--release", type=Path, required=True)
    rollback.add_argument("--approver", required=True)

    status = commands.add_parser("status", help="read Registry aliases and model versions")
    status.add_argument("--workspace", type=Path, required=True)

    cleanup = commands.add_parser("cleanup", help="remove the complete local workspace")
    cleanup.add_argument("--workspace", type=Path, required=True)

    return parser


def _registry_status(workspace_path: Path) -> dict[str, Any]:
    workspace, client = configure_workspace(workspace_path)
    aliases: dict[str, int | None] = {}
    for alias in ("candidate", "champion"):
        try:
            aliases[alias] = int(
                client.get_model_version_by_alias(
                    REGISTERED_MODEL_NAME, alias
                ).version
            )
        except Exception:
            aliases[alias] = None
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
    return {
        "status": "registry_readback",
        "workspace": str(workspace.root),
        "tracking_uri": workspace.tracking_uri,
        "aliases": aliases,
        "versions": versions,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "bootstrap":
            workspace, _ = configure_workspace(args.workspace)
            dataset = write_dataset(
                workspace.data / "baseline.csv",
                rows=args.rows,
                seed=args.seed,
            )
            _emit(
                train_track_and_request(
                    workspace.root,
                    dataset,
                    generation="bootstrap",
                    seed=args.seed,
                    request_name="bootstrap-promotion.json",
                )
            )
            return 0

        if args.command == "promote":
            _emit(
                promote_candidate(
                    args.workspace,
                    args.request,
                    approver=args.approver,
                    canary_report_path=args.canary_report,
                )
            )
            return 0

        if args.command == "serve-smoke":
            _emit(serve_smoke(args.workspace))
            return 0

        if args.command == "monitor":
            _emit(
                create_drift_report(
                    args.workspace,
                    rows=args.rows,
                    seed=args.seed,
                )
            )
            return 0

        if args.command == "retrain":
            _emit(
                retrain_from_drift(
                    args.workspace,
                    args.drift_report,
                    seed=args.seed,
                )
            )
            return 0

        if args.command == "canary":
            _emit(
                evaluate_canary(
                    args.workspace,
                    args.request,
                    args.drift_report,
                )
            )
            return 0

        if args.command == "rollback":
            _emit(
                rollback_release(
                    args.workspace,
                    args.release,
                    approver=args.approver,
                )
            )
            return 0

        if args.command == "status":
            _emit(_registry_status(args.workspace))
            return 0

        if args.command == "cleanup":
            resolved = args.workspace.resolve()
            shutil.rmtree(resolved, ignore_errors=True)
            _emit({"status": "cleaned", "workspace": str(resolved), "exists": resolved.exists()})
            return 0

        parser.error(f"unsupported command: {args.command}")
        return 2
    except (MLOpsLabError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
