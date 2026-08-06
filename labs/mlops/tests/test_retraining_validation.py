from __future__ import annotations

import pytest

from mlops_lab.contracts import ContractError, canonical_json_bytes, sha256_bytes
from mlops_lab.retraining import validate_retraining_proposal


def test_rehashed_proposal_with_unsupported_drift_status_is_rejected() -> None:
    payload = {
        "schema_version": 1,
        "drift_report_id": "a" * 64,
        "drift_status": "invented_status",
        "deployment_id": "b" * 64,
        "model_sha256": "c" * 64,
        "policy_generation": "retraining-policy-v1",
        "action": "blocked",
        "reason": "retraining is blocked while drift status is invented_status",
    }
    proposal = {
        **payload,
        "retraining_proposal_id": sha256_bytes(canonical_json_bytes(payload)),
    }

    with pytest.raises(ContractError, match="drift status is unsupported"):
        validate_retraining_proposal(proposal)
