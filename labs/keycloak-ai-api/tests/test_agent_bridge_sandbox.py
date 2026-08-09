from __future__ import annotations

import json
from pathlib import Path

import pytest

from keycloak_ai_api.agent_bridge import (
    AgentBridgeError,
    _bounded_identity_dir,
    _exact_runtime_file,
    _validate_tool_state_envelope,
)


def _runtime(tmp_path: Path) -> Path:
    root = tmp_path / ".runtime" / "agent-ops"
    root.mkdir(parents=True)
    return root.resolve()


def test_exact_runtime_files_cannot_point_outside_agent_root(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    expected = runtime / "tool-state.json"
    assert (
        _exact_runtime_file(
            expected,
            runtime_root=runtime,
            name="tool-state.json",
        )
        == expected
    )

    outside = tmp_path / "tool-state.json"
    with pytest.raises(AgentBridgeError, match="exact"):
        _exact_runtime_file(
            outside,
            runtime_root=runtime,
            name="tool-state.json",
        )


def test_exact_runtime_file_refuses_symlink_escape(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    link = runtime / "policy.json"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("file symlink is unavailable in this test environment")

    with pytest.raises(AgentBridgeError, match="must not be a symlink"):
        _exact_runtime_file(
            link,
            runtime_root=runtime,
            name="policy.json",
        )


def test_tool_state_readiness_requires_exact_local_envelope(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    state = runtime / "tool-state.json"
    state.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "services": {},
                "operations": {},
            }
        ),
        encoding="utf-8",
    )
    _validate_tool_state_envelope(state)

    state.write_text(json.dumps({"schema_version": 1, "services": {}}), encoding="utf-8")
    with pytest.raises(AgentBridgeError, match="keys mismatch"):
        _validate_tool_state_envelope(state)


def test_identity_collections_cannot_be_symlinked_outside_runtime(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    outside = tmp_path / "outside-plans"
    outside.mkdir()
    plans = runtime / "plans"
    try:
        plans.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("directory symlink is unavailable in this test environment")

    with pytest.raises(AgentBridgeError, match="root must not be a symlink"):
        _bounded_identity_dir(
            runtime_root=runtime,
            collection="plans",
            identity="a" * 64,
        )


def test_identity_directory_is_pinned_below_expected_collection(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    result = _bounded_identity_dir(
        runtime_root=runtime,
        collection="operations",
        identity="b" * 64,
    )
    assert result == runtime / "operations" / ("b" * 64)
    assert result.parent == runtime / "operations"
