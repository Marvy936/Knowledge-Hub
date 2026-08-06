from __future__ import annotations

from pathlib import Path

import pytest

from mlops_lab.contracts import ContractError
from mlops_lab.controlled_retraining.locking import (
    acquire_operation_lock,
    release_operation_lock,
)


def test_advisory_lock_survives_file_presence_but_refuses_concurrency(
    tmp_path: Path,
) -> None:
    lock_path = tmp_path / "operation.lock"
    first = acquire_operation_lock(lock_path)
    assert lock_path.is_file()

    with pytest.raises(ContractError, match="already locked"):
        acquire_operation_lock(lock_path)

    release_operation_lock(first)

    second = acquire_operation_lock(lock_path)
    assert lock_path.is_file()
    release_operation_lock(second)
