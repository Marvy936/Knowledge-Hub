"""Dataset contract validation and leakage refusal."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .constants import (
    ALLOWED_CATEGORIES,
    EXPECTED_COLUMNS,
    FEATURE_COLUMNS,
    ID_COLUMN,
    KNOWN_LEAKAGE_COLUMNS,
    MAX_FEATURE_MISSING_FRACTION,
    MIN_CLASS_COUNT,
    MIN_DATASET_ROWS,
    NUMERIC_RANGES,
    TARGET_COLUMN,
)
from .errors import DataValidationError
from .io_utils import sha256_file


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise DataValidationError(f"dataset does not exist: {path}")
    try:
        return pd.read_csv(path)
    except Exception as exc:  # pandas parser failures need stable CLI semantics
        raise DataValidationError(f"cannot parse dataset {path}: {exc}") from exc


def validate_dataframe(frame: pd.DataFrame) -> dict[str, Any]:
    failures: list[str] = []

    actual_columns = list(frame.columns)
    leakage = sorted(KNOWN_LEAKAGE_COLUMNS.intersection(actual_columns))
    if leakage:
        failures.append(f"known post-outcome leakage columns are forbidden: {leakage}")

    missing_columns = sorted(set(EXPECTED_COLUMNS) - set(actual_columns))
    unexpected_columns = sorted(set(actual_columns) - set(EXPECTED_COLUMNS))
    if missing_columns:
        failures.append(f"required columns are missing: {missing_columns}")
    if unexpected_columns:
        failures.append(f"unexpected columns require an explicit contract change: {unexpected_columns}")

    if failures:
        raise DataValidationError("; ".join(failures))

    if len(frame) < MIN_DATASET_ROWS:
        failures.append(f"dataset has {len(frame)} rows; minimum is {MIN_DATASET_ROWS}")

    if frame[ID_COLUMN].isna().any():
        failures.append(f"{ID_COLUMN} contains null values")
    duplicate_ids = int(frame[ID_COLUMN].duplicated().sum())
    if duplicate_ids:
        failures.append(f"{ID_COLUMN} contains {duplicate_ids} duplicate values")

    if frame[TARGET_COLUMN].isna().any():
        failures.append(f"{TARGET_COLUMN} contains null values")
    numeric_target = pd.to_numeric(frame[TARGET_COLUMN], errors="coerce")
    invalid_target_types = int((frame[TARGET_COLUMN].notna() & numeric_target.isna()).sum())
    if invalid_target_types:
        failures.append(f"{TARGET_COLUMN} contains {invalid_target_types} non-numeric values")
    target_values = set(numeric_target.dropna().unique().tolist())
    if target_values != {0, 1}:
        failures.append(f"{TARGET_COLUMN} must contain both binary classes 0 and 1")

    class_counts = {
        str(int(label)): int(count)
        for label, count in numeric_target.value_counts(dropna=False).sort_index().items()
        if pd.notna(label)
    }
    for label in ("0", "1"):
        if class_counts.get(label, 0) < MIN_CLASS_COUNT:
            failures.append(
                f"class {label} has {class_counts.get(label, 0)} rows; minimum is {MIN_CLASS_COUNT}"
            )

    missing_fractions: dict[str, float] = {}
    for column in FEATURE_COLUMNS:
        fraction = float(frame[column].isna().mean())
        missing_fractions[column] = round(fraction, 6)
        if fraction > MAX_FEATURE_MISSING_FRACTION:
            failures.append(
                f"{column} missing fraction {fraction:.3f} exceeds {MAX_FEATURE_MISSING_FRACTION:.3f}"
            )

    for column, (minimum, maximum) in NUMERIC_RANGES.items():
        coerced = pd.to_numeric(frame[column], errors="coerce")
        invalid_types = int((frame[column].notna() & coerced.isna()).sum())
        if invalid_types:
            failures.append(f"{column} contains {invalid_types} non-numeric values")
        series = coerced.dropna()
        invalid = int(((series < minimum) | (series > maximum)).sum())
        if invalid:
            failures.append(
                f"{column} contains {invalid} values outside [{minimum}, {maximum}]"
            )

    for column, allowed in ALLOWED_CATEGORIES.items():
        observed = set(frame[column].dropna().astype(str).unique().tolist())
        invalid_values = sorted(observed - allowed)
        if invalid_values:
            failures.append(f"{column} contains unsupported categories: {invalid_values}")

    if failures:
        raise DataValidationError("; ".join(failures))

    return {
        "status": "valid",
        "rows": int(len(frame)),
        "columns": actual_columns,
        "class_counts": class_counts,
        "positive_fraction": round(float(numeric_target.mean()), 6),
        "feature_missing_fraction": missing_fractions,
    }


def validate_dataset(path: Path) -> dict[str, Any]:
    frame = load_dataset(path)
    report = validate_dataframe(frame)
    report["dataset_path"] = str(path)
    report["dataset_sha256"] = sha256_file(path)
    return report
