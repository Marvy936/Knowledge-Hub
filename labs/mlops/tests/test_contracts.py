from __future__ import annotations

import json
from pathlib import Path

import pytest

from mlops_lab.contracts import (
    ContractError,
    build_candidate_manifest,
    build_dataset_manifest,
    promote_candidate,
    validate_candidate_manifest,
)


def _evaluation(*, accepted: bool = True) -> dict[str, object]:
    return {
        "accepted": accepted,
        "metrics": {"f1": 0.63, "recall": 0.57},
        "policy_generation": "churn-promotion-v1",
    }


def _candidate(tmp_path: Path, *, accepted: bool = True) -> dict[str, object]:
    dataset = tmp_path / "dataset.csv"
    dataset.write_text("id,label\n1,0\n2,1\n", encoding="utf-8", newline="\n")
    model = tmp_path / "model.bin"
    model.write_bytes(b"deterministic-model-bytes")
    dataset_manifest = build_dataset_manifest(
        dataset, dataset_name="churn-training", generation="data-v1"
    )
    return build_candidate_manifest(
        dataset_manifest=dataset_manifest,
        model_path=model,
        evaluation=_evaluation(accepted=accepted),
        source_revision="abc123",
    )


def test_dataset_and_candidate_identity_are_deterministic(tmp_path: Path) -> None:
    first = _candidate(tmp_path)
    second = _candidate(tmp_path)
    assert first == second
    validate_candidate_manifest(first)


def test_candidate_identity_is_workspace_independent(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.csv"
    dataset.write_text("id,label\n1,0\n2,1\n", encoding="utf-8", newline="\n")
    dataset_manifest = build_dataset_manifest(
        dataset, dataset_name="churn-training", generation="data-v1"
    )

    first_model = tmp_path / "runner-a" / "model.bin"
    second_model = tmp_path / "runner-b" / "renamed-model.bin"
    first_model.parent.mkdir()
    second_model.parent.mkdir()
    first_model.write_bytes(b"deterministic-model-bytes")
    second_model.write_bytes(b"deterministic-model-bytes")

    first = build_candidate_manifest(
        dataset_manifest=dataset_manifest,
        model_path=first_model,
        evaluation=_evaluation(),
        source_revision="abc123",
    )
    second = build_candidate_manifest(
        dataset_manifest=dataset_manifest,
        model_path=second_model,
        evaluation=_evaluation(),
        source_revision="abc123",
    )

    assert first == second


def test_candidate_tampering_is_refused(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path)
    candidate["model"]["sha256"] = "0" * 64
    with pytest.raises(ContractError, match="candidate_id does not match"):
        validate_candidate_manifest(candidate)


def test_unaccepted_candidate_cannot_be_promoted(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path, accepted=False)
    with pytest.raises(ContractError, match="not accepted"):
        promote_candidate(
            candidate=candidate,
            alias_state={"schema_version": 1, "aliases": {}},
            alias="champion",
            expected_current=None,
        )


def test_first_promotion_creates_release_and_alias_state(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path)
    release, state = promote_candidate(
        candidate=candidate,
        alias_state={"schema_version": 1, "aliases": {}},
        alias="champion",
        expected_current=None,
    )
    assert release["candidate_id"] == candidate["candidate_id"]
    assert release["previous_candidate_id"] is None
    assert state["aliases"]["champion"] == candidate["candidate_id"]
    assert len(release["release_id"]) == 64


def test_stale_promotion_is_refused_without_new_state(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path)
    current = "1" * 64
    state = {"schema_version": 1, "aliases": {"champion": current}}
    original = json.loads(json.dumps(state))
    with pytest.raises(ContractError, match="stale promotion"):
        promote_candidate(
            candidate=candidate,
            alias_state=state,
            alias="champion",
            expected_current="2" * 64,
        )
    assert state == original


def test_alias_state_schema_is_validated(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path)
    with pytest.raises(ContractError, match="schema_version must equal 1"):
        promote_candidate(
            candidate=candidate,
            alias_state={"schema_version": 2, "aliases": {}},
            alias="champion",
            expected_current=None,
        )


def test_expected_current_allows_controlled_replacement(tmp_path: Path) -> None:
    candidate = _candidate(tmp_path)
    current = "1" * 64
    release, state = promote_candidate(
        candidate=candidate,
        alias_state={"schema_version": 1, "aliases": {"champion": current}},
        alias="champion",
        expected_current=current,
    )
    assert release["previous_candidate_id"] == current
    assert state["aliases"]["champion"] == candidate["candidate_id"]
