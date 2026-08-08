from __future__ import annotations

import shutil
from pathlib import Path


class RuntimeCleanupError(ValueError):
    pass


def validate_runtime_root(path: Path) -> Path:
    if path.name != "keycloak" or path.parent.name != ".runtime":
        raise RuntimeCleanupError("runtime root must end with .runtime/keycloak")
    if path.is_symlink():
        raise RuntimeCleanupError("runtime root must not be a symlink")
    if path.parent.is_symlink():
        raise RuntimeCleanupError(".runtime parent must not be a symlink")
    resolved = path.resolve(strict=False)
    if resolved.name != "keycloak" or resolved.parent.name != ".runtime":
        raise RuntimeCleanupError("resolved runtime root must end with .runtime/keycloak")
    return resolved


def cleanup_runtime(path: Path) -> dict[str, object]:
    target = validate_runtime_root(path)
    existed = target.exists()
    if existed:
        if not target.is_dir():
            raise RuntimeCleanupError("runtime root must be a directory")
        shutil.rmtree(target)
    if target.exists():
        raise RuntimeCleanupError("runtime cleanup read-back failed")
    return {
        "status": "cleanup_verified",
        "target": target.as_posix(),
        "existed_before": existed,
        "exists_after": False,
    }
