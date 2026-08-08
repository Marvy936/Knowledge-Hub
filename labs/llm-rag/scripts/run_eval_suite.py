from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from knowledge_hub_rag.contracts import ContractError, atomic_write_json, read_json
from knowledge_hub_rag.evaluation import build_prompt_release, run_eval_suite
from knowledge_hub_rag.runtime_config import build_runtime_config


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run deterministic RAG eval slices and promote one exact runtime config only on hard pass."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--generation", required=True)
    parser.add_argument("--implementation-revision", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--min-score", type=float, default=0.01)
    parser.add_argument("--context-max-chars", type=int, default=6000)
    parser.add_argument("--answer-max-chars", type=int, default=700)
    parser.add_argument("--config-output", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    parser.add_argument("--release-output", type=Path, required=True)
    return parser


def _load_cases(path: Path) -> list[dict[str, object]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"eval cases file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid eval cases JSON: {exc}") from exc
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, dict) for item in value)
    ):
        raise ContractError("eval cases root must be a non-empty array of objects")
    return value


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.release_output.exists():
            raise ContractError(
                "release output already exists; use a fresh path so a failed eval cannot leave stale promotion evidence"
            )
        manifest = read_json(args.manifest)
        index = read_json(args.index)
        cases = _load_cases(args.cases)
        config = build_runtime_config(
            generation=args.generation,
            implementation_revision=args.implementation_revision,
            top_k=args.top_k,
            min_score=args.min_score,
            context_max_chars=args.context_max_chars,
            answer_max_chars=args.answer_max_chars,
        )
        report = run_eval_suite(
            cases=cases,
            manifest=manifest,
            index=index,
            runtime_config=config,
        )
        atomic_write_json(args.config_output, config)
        atomic_write_json(args.report_output, report)
        if report["suite_passed"] is not True:
            if args.release_output.exists():
                raise ContractError("failed eval unexpectedly created release output")
            print(
                json.dumps(
                    {
                        "status": "eval_failed",
                        "eval_report_id": report["eval_report_id"],
                        "implementation_revision": config["implementation_revision"],
                        "critical_failures": report["critical_failures"],
                        "high_risk_failures": report["high_risk_failures"],
                        "threshold_failures": report["threshold_failures"],
                    },
                    sort_keys=True,
                )
            )
            return 4
        release = build_prompt_release(
            runtime_config=config,
            eval_report=report,
            cases=cases,
            manifest=manifest,
            index=index,
        )
        atomic_write_json(args.release_output, release)
    except ContractError as exc:
        print(
            json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True),
            file=sys.stderr,
        )
        return 2

    print(
        json.dumps(
            {
                "status": "promoted",
                "runtime_config_id": config["runtime_config_id"],
                "implementation_revision": config["implementation_revision"],
                "eval_report_id": report["eval_report_id"],
                "prompt_release_id": release["prompt_release_id"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
