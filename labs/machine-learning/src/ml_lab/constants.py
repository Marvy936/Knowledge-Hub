"""Stable schema and acceptance constants for the flagship lab."""

from __future__ import annotations

ID_COLUMN = "customer_id"
TARGET_COLUMN = "churned_next_30d"

NUMERIC_FEATURES = [
    "tenure_months",
    "monthly_spend_eur",
    "support_tickets_90d",
    "login_days_30d",
    "days_since_last_login",
]

CATEGORICAL_FEATURES = [
    "contract_type",
    "region",
    "auto_pay",
]

FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES
EXPECTED_COLUMNS = [ID_COLUMN] + FEATURE_COLUMNS + [TARGET_COLUMN]

ALLOWED_CATEGORIES = {
    "contract_type": {"monthly", "annual", "two_year"},
    "region": {"west", "central", "east", "north"},
    "auto_pay": {"yes", "no"},
}

NUMERIC_RANGES = {
    "tenure_months": (0, 120),
    "monthly_spend_eur": (5.0, 250.0),
    "support_tickets_90d": (0, 30),
    "login_days_30d": (0, 30),
    "days_since_last_login": (0, 180),
}

KNOWN_LEAKAGE_COLUMNS = {
    "cancelled_at",
    "future_refund_30d",
    "post_churn_survey_score",
    "termination_reason",
}

DEFAULT_SEED = 20260805
DEFAULT_ROWS = 1200
MIN_DATASET_ROWS = 200
MAX_FEATURE_MISSING_FRACTION = 0.20
MIN_CLASS_COUNT = 20
MIN_REQUIRED_RECALL = 0.60
MIN_TEST_F1 = 0.55
MIN_TEST_RECALL = 0.55
ARTIFACT_SCHEMA_VERSION = 1
