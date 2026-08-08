from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from keycloak_ai_api.runtime import RuntimeCleanupError, cleanup_runtime


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Remove only the explicit Keycloak .runtime/keycloak directory and verify cleanup."
    )
    parser.add_argument("--runtime-root", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        result = cleanup_runtime(args.runtime_root)
    except RuntimeCleanupError as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
