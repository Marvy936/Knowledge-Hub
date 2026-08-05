"""Leakage-safe preprocessing, model comparison and threshold selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .constants import CATEGORICAL_FEATURES, MIN_REQUIRED_RECALL, NUMERIC_FEATURES


@dataclass(frozen=True)
class ModelEvaluation:
    name: str
    pipeline: Pipeline
    threshold: float
    metrics: dict[str, Any]
    threshold_status: str


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric, NUMERIC_FEATURES),
            ("categorical", categorical, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def build_model_candidates(seed: int) -> dict[str, Pipeline]:
    return {
        "dummy_most_frequent": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                ("model", DummyClassifier(strategy="most_frequent")),
            ]
        ),
        "logistic_regression": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                (
                    "model",
                    LogisticRegression(
                        C=1.0,
                        class_weight="balanced",
                        max_iter=1200,
                        random_state=seed,
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=220,
                        max_depth=8,
                        min_samples_leaf=4,
                        class_weight="balanced_subsample",
                        n_jobs=1,
                        random_state=seed,
                    ),
                ),
            ]
        ),
    }


def _metrics(
    y_true: pd.Series | np.ndarray,
    probabilities: np.ndarray,
    threshold: float,
) -> dict[str, Any]:
    predictions = (probabilities >= threshold).astype(int)
    matrix = confusion_matrix(y_true, predictions, labels=[0, 1])
    try:
        roc_auc = float(roc_auc_score(y_true, probabilities))
    except ValueError:
        roc_auc = 0.0
    return {
        "threshold": round(float(threshold), 6),
        "accuracy": round(float(accuracy_score(y_true, predictions)), 6),
        "precision": round(float(precision_score(y_true, predictions, zero_division=0)), 6),
        "recall": round(float(recall_score(y_true, predictions, zero_division=0)), 6),
        "f1": round(float(f1_score(y_true, predictions, zero_division=0)), 6),
        "roc_auc": round(roc_auc, 6),
        "confusion_matrix": matrix.astype(int).tolist(),
        "predicted_positive_fraction": round(float(predictions.mean()), 6),
    }


def choose_threshold(
    y_true: pd.Series | np.ndarray,
    probabilities: np.ndarray,
    minimum_recall: float = MIN_REQUIRED_RECALL,
) -> tuple[float, dict[str, Any], str]:
    candidates: list[tuple[float, dict[str, Any]]] = []
    for threshold in np.linspace(0.05, 0.95, 91):
        candidates.append((float(threshold), _metrics(y_true, probabilities, float(threshold))))

    eligible = [item for item in candidates if item[1]["recall"] >= minimum_recall]
    pool = eligible if eligible else candidates
    status = "recall_gate_satisfied" if eligible else "recall_gate_fallback"
    threshold, metrics = max(
        pool,
        key=lambda item: (
            item[1]["f1"],
            item[1]["precision"],
            item[1]["recall"],
            -abs(item[0] - 0.5),
        ),
    )
    return threshold, metrics, status


def fit_and_evaluate_candidates(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_validation: pd.DataFrame,
    y_validation: pd.Series,
    seed: int,
) -> list[ModelEvaluation]:
    evaluations: list[ModelEvaluation] = []
    for name, pipeline in build_model_candidates(seed).items():
        pipeline.fit(x_train, y_train)
        probabilities = pipeline.predict_proba(x_validation)[:, 1]
        threshold, metrics, threshold_status = choose_threshold(y_validation, probabilities)
        evaluations.append(
            ModelEvaluation(
                name=name,
                pipeline=pipeline,
                threshold=threshold,
                metrics=metrics,
                threshold_status=threshold_status,
            )
        )
    return evaluations


def select_candidate(evaluations: list[ModelEvaluation]) -> ModelEvaluation:
    non_dummy = [item for item in evaluations if item.name != "dummy_most_frequent"]
    if not non_dummy:
        raise ValueError("at least one non-dummy model candidate is required")
    return max(
        non_dummy,
        key=lambda item: (
            item.metrics["f1"],
            item.metrics["roc_auc"],
            item.metrics["precision"],
            item.metrics["recall"],
        ),
    )


def evaluate_at_threshold(
    pipeline: Pipeline,
    x: pd.DataFrame,
    y: pd.Series,
    threshold: float,
) -> dict[str, Any]:
    probabilities = pipeline.predict_proba(x)[:, 1]
    return _metrics(y, probabilities, threshold)
