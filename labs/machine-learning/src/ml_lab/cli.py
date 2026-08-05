"""Command-line interface for deterministic generation, training and inference."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .constants import DEFAULT_ROWS, DEFAULT_SEED
from .data import write_dataset
from .errors import MLLabError
from .inference import predict_record
from .io_utils import read_json_object, sha256_file
from .training import train_and_package
from .validation import validate_dataset


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ml-lab",
        description="Knowledge Hub Machine Learning Fundamentals flagship lab",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate-data", help="generate a deterministic raw dataset")
    generate.add_argument("--output", type=Path, required=True)
    generate.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    generate.add_argument("--seed", type=int, default=DEFAULT_SEED)

    validate = subparsers.add_parser("validate-data", help="validate schema, ranges and leakage guards")
    validate.add_argument("--input", type=Path, required=True)

    train = subparsers.add_parser("train", help="compare experiments and package the accepted model")
    train.add_argument("--input", type=Path, required=True)
    train.add_argument("--output-dir", type=Path, required=True)
    train.add_argument("--seed", type=int, default=DEFAULT_SEED)
    train.add_argument("--overwrite", action="store_true")

    infer = subparsers.add_parser("infer", help="verify and run one local inference request")
    infer.add_argument("--artifact-dir", type=Path, required=True)
    infer.add_argument("--input", type=Path, required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "generate-data":
            output = write_dataset(args.output, rows=args.rows, seed=args.seed)
            _emit(
                {
                    "status": "generated",
                    "path": str(output),
                    "rows": args.rows,
                    "seed": args.seed,
                    "sha256": sha256_file(output),
                }
            )
            return 0

        if args.command == "validate-data":
            _emit(validate_dataset(args.input))
            return 0

        if args.command == "train":
            manifest = train_and_package(
                args.input,
                args.output_dir,
                seed=args.seed,
                overwrite=args.overwrite,
            )
            _emit(
                {
                    "status": "accepted_and_packaged",
                    "artifact_dir": str(args.output_dir),
                    "selected_model": manifest["selected_model"],
                    "decision_threshold": manifest["decision_threshold"],
                    "validation_metrics": manifest["validation_metrics"],
                    "test_metrics": manifest["test_metrics"],
                    "model_sha256": manifest["model_sha256"],
                }
            )
            return 0

        if args.command == "infer":
            record = read_json_object(args.input)
            _emit(predict_record(args.artifact_dir, record))
            return 0

        parser.error(f"unsupported command: {args.command}")
        return 2
    except (MLLabError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
