from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from mlops_lab.contracts import ContractError, canonical_json_bytes, sha256_bytes
from mlops_lab.post_retraining import build_post_retraining_handoff

from test_post_retraining import _completed


def test_current_deployment_must_match_operation_subject(tmp_path: Path) -> None:
    operation, state, release, registry, current, routing = _completed(tmp_path)
    changed = deepcopy(current)
    changed["generation"] = "unexpected-generation"
    payload = {
        key: item for key, item in changed.items() if key != "deployment_id"
    }
    changed["deployment_id"] = sha256_bytes(canonical_json_bytes(payload))

    with pytest.raises(ContractError, match="current deployment does not match"):
        build_post_retraining_handoff(
            operation=operation,
            completed_state=state,
            release=release,
            registry_evidence=registry,
            current_deployment=changed,
            current_routing_state=routing,
            service_name=changed["service_name"],
            generation="canary-2",
            image_reference="example/churn:2",
            image_digest="sha256:" + "8" * 64,
            canary_basis_points=1000,
            expected_current_routing_state_id=routing["routing_state_id"],
        )
