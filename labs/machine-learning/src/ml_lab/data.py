"""Deterministic synthetic dataset generation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .constants import DEFAULT_ROWS, DEFAULT_SEED


def generate_dataset(rows: int = DEFAULT_ROWS, seed: int = DEFAULT_SEED) -> pd.DataFrame:
    if rows < 200:
        raise ValueError("rows must be at least 200 so every split has useful class support")

    rng = np.random.default_rng(seed)

    tenure = rng.integers(0, 121, size=rows)
    monthly_spend = np.clip(rng.normal(68.0, 26.0, size=rows), 8.0, 220.0)
    support_tickets = np.clip(rng.poisson(1.7, size=rows), 0, 20)
    login_days = np.clip(rng.normal(16.0, 8.0, size=rows).round(), 0, 30).astype(int)
    days_since_login = np.clip(rng.gamma(shape=1.7, scale=8.0, size=rows).round(), 0, 180).astype(int)
    contract_type = rng.choice(
        ["monthly", "annual", "two_year"], size=rows, p=[0.54, 0.31, 0.15]
    )
    region = rng.choice(["west", "central", "east", "north"], size=rows)
    auto_pay = rng.choice(["yes", "no"], size=rows, p=[0.63, 0.37])

    logit = (
        -1.10
        + 0.32 * support_tickets
        + 0.075 * days_since_login
        - 0.070 * login_days
        - 0.025 * tenure
        + 0.008 * (monthly_spend - 68.0)
        + 1.00 * (contract_type == "monthly")
        - 0.55 * (contract_type == "two_year")
        + 0.60 * (auto_pay == "no")
        + 0.25 * (region == "east")
        + rng.normal(0.0, 0.20, size=rows)
    )
    probability = 1.0 / (1.0 + np.exp(-logit))
    target = rng.binomial(1, probability, size=rows)

    frame = pd.DataFrame(
        {
            "customer_id": [f"cust-{index:06d}" for index in range(1, rows + 1)],
            "tenure_months": tenure,
            "monthly_spend_eur": monthly_spend.round(2),
            "support_tickets_90d": support_tickets,
            "login_days_30d": login_days,
            "days_since_last_login": days_since_login,
            "contract_type": contract_type,
            "region": region,
            "auto_pay": auto_pay,
            "churned_next_30d": target,
        }
    )

    # Missingness is injected only into features. The target and identity remain authoritative.
    missing_count = max(1, rows // 50)
    for column in ("monthly_spend_eur", "days_since_last_login", "region"):
        positions = rng.choice(rows, size=missing_count, replace=False)
        frame.loc[positions, column] = np.nan

    return frame


def write_dataset(path: Path, rows: int = DEFAULT_ROWS, seed: int = DEFAULT_SEED) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = generate_dataset(rows=rows, seed=seed)
    temporary = path.with_name(f".{path.name}.tmp")
    frame.to_csv(temporary, index=False, lineterminator="\n", float_format="%.6f")
    temporary.replace(path)
    return path
