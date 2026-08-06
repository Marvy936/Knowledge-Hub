from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from mlops_lab.contracts import ContractError, atomic_write_json
from mlops_lab.monitoring import (
    build_baseline_profile,
    build_monitoring_window,
    compare_drift,
)
from mlops_lab.retraining import build_retraining_proposal


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build aggregate monitoring, drift and retraining-proposal evidence."
    )
    parser.add_argument("--baseline-events-jsonl", type=Path, required=True)
    parser.add_argument("--window-events-jsonl", type=Path, required=True)
    parser.add_argument("--profile-name", required=True)
    parser.add_argument("--generation", required=True)
    parser.add_argument("--deployment-id", required=True)
    parser.add_argument("--model-sha256", required=True)
    parser.add_argument("--policy-generation", required=True)
    parser.add_argument("--minimum-successful-events", type=int, required=True)
    parser.add_argument("--numeric-psi-threshold", type=float, default=0.20)
    parser.add_argument("--categorical-tvd-threshold", type=float, default=0.15)
    parser.add_argument("--prediction-rate-delta-threshold", type=float, default=0.10)
    parser.add_argument("--maximum-error-rate", type=float, default=0.05)
    parser.add_argument("--baseline-output", type=Path, required=True)
    parser.add_argument("--window-output", type=Path, required=True)
    parser.add_argument("--drift-output", type=Path, required=True)
    parser.add_argument("--proposal-output", type=Path, required=True)
    return parser


def _load_events(path: Path) -> list[dict[str, object]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise ContractError(f"event corpus does not exist: {path}") from exc
    events: list[dict[str, object]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError(
                f"invalid JSONL event at line {line_number}: {exc}"
            ) from exc
        if not isinstance(item, dict):
            raise ContractError(f"event line {line_number} must be an object")
        events.append(item)
    return events


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        baseline = build_baseline_profile(
            events=_load_events(args.baseline_events_jsonl),
            profile_name=args.profile_name,
            generation=args.generation,
        )
        window = build_monitoring_window(
            events=_load_events(args.window_events_jsonl),
            baseline=baseline,
            deployment_id=args.deployment_id,
        )
        drift = compare_drift(
            baseline=baseline,
            window=window,
            minimum_successful_events=args.minimum_successful_events,
            numeric_psi_threshold=args.numeric_psi_threshold,
            categorical_tvd_threshold=args.categorical_tvd_threshold,
            prediction_rate_delta_threshold=args.prediction_rate_delta_threshold,
            maximum_error_rate=args.maximum_error_rate,
        )
        proposal = build_retraining_proposal(
            drift_report=drift,
            model_sha256=args.model_sha256,
            policy_generation=args.policy_generation,
        )
        atomic_write_json(args.baseline_output, baseline)
        atomic_write_json(args.window_output, window)
        atomic_write_json(args.drift_output, drift)
        atomic_write_json(args.proposal_output, proposal)
    except ContractError as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True))
        return 2

    print(
        json.dumps(
            {
                "status": drift["status"],
                "baseline_profile_id": baseline["baseline_profile_id"],
                "monitoring_window_id": window["monitoring_window_id"],
                "drift_report_id": drift["drift_report_id"],
                "retraining_proposal_id": proposal["retraining_proposal_id"],
                "proposal_action": proposal["action"],
            },
            sort_keys=True,
        )
    )
    return {
        "stable": 0,
        "no_data": 3,
        "insufficient_evidence": 3,
        "operational_failure": 4,
        "drift_detected": 5,
    }[drift["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
