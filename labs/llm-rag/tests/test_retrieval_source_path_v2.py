from __future__ import annotations

import math

from knowledge_hub_rag import retrieval


def _index() -> dict[str, object]:
    return {
        "document_count": 100,
        "document_frequencies": {
            "configmap": 5,
            "kubernetes": 20,
            "secret": 10,
            "error": 8,
        },
    }


def test_source_path_bonus_splits_repository_path_separators() -> None:
    index = _index()
    expected = {"source_path": "docs/09-kubernetes/configmap-secret.md"}
    unrelated = {"source_path": "docs/07-infrastructure/vault.md"}
    query = ["na", "čo", "slúži", "kubernetes", "configmap", "secret"]

    expected_bonus = retrieval._source_path_bonus(
        query_tokens=query, document=expected, index=index
    )
    unrelated_bonus = retrieval._source_path_bonus(
        query_tokens=query, document=unrelated, index=index
    )

    assert unrelated_bonus == 0.0
    assert expected_bonus == round(
        sum(
            math.log(
                1.0
                + (100 - index["document_frequencies"][term] + 0.5)
                / (index["document_frequencies"][term] + 0.5)
            )
            for term in ("configmap", "kubernetes", "secret")
        ),
        12,
    )


def test_retrieval_algorithm_generation_is_explicit_v2() -> None:
    assert retrieval.RETRIEVAL_ALGORITHM == "bm25-source-path-v2"
    assert retrieval.SOURCE_PATH_BOOST == 1.0
