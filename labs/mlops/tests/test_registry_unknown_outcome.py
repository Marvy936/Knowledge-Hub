from __future__ import annotations

from pathlib import Path

import pytest

from mlops_lab.contracts import ContractError, read_json

from test_controlled_retraining import _execute, _inputs, _registry, _train


def test_registry_unknown_outcome_requires_external_reconciliation(
    tmp_path: Path,
) -> None:
    args = _inputs(tmp_path)
    calls: list[str] = []

    def remote_then_crash(
        candidate, model_path, sample_request_path, config, download_dir
    ):
        _registry(calls)(
            candidate,
            model_path,
            sample_request_path,
            config,
            download_dir,
        )
        raise RuntimeError("connection lost after remote Registry mutation")

    with pytest.raises(RuntimeError, match="connection lost"):
        _execute(args, _train(calls), remote_then_crash)

    failed = read_json(tmp_path / "state.json")
    assert failed["phase"] == "failed"
    assert (tmp_path / "output" / "registry-attempt.json").is_file()

    with pytest.raises(ContractError, match="outcome is unknown"):
        _execute(
            args,
            lambda *unused: (_ for _ in ()).throw(
                AssertionError("training repeated")
            ),
            lambda *unused: (_ for _ in ()).throw(
                AssertionError("Registry repeated")
            ),
            recover=failed["state_id"],
        )

    assert calls.count("train") == 1
    assert calls.count("registry") == 1
