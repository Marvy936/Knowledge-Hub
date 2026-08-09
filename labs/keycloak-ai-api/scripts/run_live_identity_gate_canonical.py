from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Sequence


LEGACY_DRIVER = Path(__file__).with_name("run_live_identity_gate.py")
SPEC = importlib.util.spec_from_file_location("keycloak_live_identity_gate_core", LEGACY_DRIVER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load identity gate lifecycle: {LEGACY_DRIVER}")
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)

IdentityRuntimeError = core.IdentityRuntimeError


def _build_rag(repo_root: Path, runtime_root: Path, subject_sha: str) -> dict[str, Any]:
    try:
        from keycloak_ai_api.runtime_rag import RuntimeRagError, build_live_rag_bundle

        return build_live_rag_bundle(
            repo_root=repo_root,
            runtime_root=runtime_root,
            subject_sha=subject_sha,
        )
    except (ImportError, RuntimeRagError, OSError, RuntimeError, ValueError) as exc:
        raise IdentityRuntimeError(
            f"cannot build canonical promoted RAG bundle: {type(exc).__name__}: {exc}"
        ) from exc


core._build_rag = _build_rag


def main(argv: Sequence[str] | None = None) -> int:
    return int(core.main(argv))


if __name__ == "__main__":
    raise SystemExit(main())
