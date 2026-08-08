from __future__ import annotations

from pathlib import Path

import pytest

from keycloak_ai_api.runtime import RuntimeCleanupError, cleanup_runtime


def test_cleanup_removes_only_exact_runtime_keycloak_path(tmp_path: Path) -> None:
    target = tmp_path / ".runtime" / "keycloak"
    target.mkdir(parents=True)
    (target / "token.jwt").write_text("disposable", encoding="utf-8")
    result = cleanup_runtime(target)
    assert result["status"] == "cleanup_verified"
    assert result["existed_before"] is True
    assert result["exists_after"] is False
    assert not target.exists()


def test_cleanup_refuses_broad_or_symlinked_target(tmp_path: Path) -> None:
    with pytest.raises(RuntimeCleanupError, match="must end with .runtime/keycloak"):
        cleanup_runtime(tmp_path / ".runtime")

    real_parent = tmp_path / "real-runtime"
    real_parent.mkdir()
    symlink_parent = tmp_path / ".runtime"
    try:
        symlink_parent.symlink_to(real_parent, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("directory symlink is unavailable in this test environment")
    with pytest.raises(RuntimeCleanupError, match="parent must not be a symlink"):
        cleanup_runtime(symlink_parent / "keycloak")
