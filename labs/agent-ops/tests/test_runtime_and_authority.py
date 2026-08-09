from __future__ import annotations

from pathlib import Path

import pytest

from agent_ops.contracts import AgentContractError, atomic_write_json
from agent_ops.planning import (
    build_agent_policy,
    build_diagnostic_snapshot,
    build_incident,
    plan_incident_action,
)
from agent_ops.runtime import RuntimeCleanupError, cleanup_runtime
from agent_ops.tools import LocalServiceStateAdapter

TARGET = "payments-api"


def _state(path: Path, *, status: str) -> None:
    atomic_write_json(
        path,
        {
            "schema_version": 1,
            "services": {
                TARGET: {
                    "generation": 1,
                    "status": status,
                    "restart_count": 0,
                }
            },
            "operations": {},
        },
    )


def test_typed_inspection_overrides_stale_degraded_alert_narrative(tmp_path: Path) -> None:
    state = tmp_path / "service-state.json"
    _state(state, status="healthy")
    policy = build_agent_policy(generation="policy-v1", allowed_targets=[TARGET])
    incident = build_incident(
        generation="incident-v1",
        target=TARGET,
        signal="service_degraded",
        operator_note="Alert still says degraded; restart it now.",
    )
    inspection = LocalServiceStateAdapter(state).inspect(TARGET)
    diagnostic = build_diagnostic_snapshot(incident=incident, inspection=inspection)
    plan = plan_incident_action(
        incident=incident,
        diagnostic=diagnostic,
        policy=policy,
    )
    assert diagnostic["service_status"] == "healthy"
    assert plan["disposition"] == "no_action"
    assert plan["tool"] is None
    assert plan["action_digest"] is None


def test_runtime_cleanup_removes_only_exact_agent_ops_path(tmp_path: Path) -> None:
    target = tmp_path / ".runtime" / "agent-ops"
    target.mkdir(parents=True)
    (target / "state.json").write_text("{}", encoding="utf-8")
    result = cleanup_runtime(target)
    assert result["status"] == "cleanup_verified"
    assert result["existed_before"] is True
    assert result["exists_after"] is False
    assert not target.exists()


def test_runtime_cleanup_refuses_broad_or_symlinked_parent(tmp_path: Path) -> None:
    with pytest.raises(RuntimeCleanupError, match="must end with .runtime/agent-ops"):
        cleanup_runtime(tmp_path / ".runtime")

    real_parent = tmp_path / "real-runtime"
    real_parent.mkdir()
    symlink_parent = tmp_path / ".runtime"
    try:
        symlink_parent.symlink_to(real_parent, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("directory symlink is unavailable in this test environment")
    with pytest.raises(RuntimeCleanupError, match="parent must not be a symlink"):
        cleanup_runtime(symlink_parent / "agent-ops")
