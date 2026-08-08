from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from knowledge_hub_rag.contracts import ContractError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Remove only an explicit Knowledge Hub RAG .runtime/rag directory and verify cleanup."
    )
    parser.add_argument("--runtime-root", type=Path, required=True)
    return parser


def _validate_target(path: Path) -> Path:
    if path.name != "rag" or path.parent.name != ".runtime":
        raise ContractError("runtime cleanup target must end with .runtime/rag")
    if path.is_symlink():
        raise ContractError("runtime cleanup target must not be a symlink")
    if path.parent.is_symlink():
        raise ContractError("runtime cleanup .runtime parent must not be a symlink")
    resolved = path.resolve(strict=False)
    if resolved.name != "rag" or resolved.parent.name != ".runtime":
        raise ContractError("resolved runtime cleanup target must end with .runtime/rag")
    return resolved


def main() -> int:
    args = _parser().parse_args()
    try:
        target = _validate_target(args.runtime_root)
        existed = target.exists()
        if existed:
            if not target.is_dir():
                raise ContractError("runtime cleanup target must be a directory")
            shutil.rmtree(target)
        if target.exists():
            raise ContractError("runtime cleanup read-back failed")
    except ContractError as exc:
        print(
            json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True),
            file=sys.stderr,
        )
        return 2

    print(
        json.dumps(
            {
                "status": "cleanup_verified",
                "target": target.as_posix(),
                "existed_before": existed,
                "exists_after": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
