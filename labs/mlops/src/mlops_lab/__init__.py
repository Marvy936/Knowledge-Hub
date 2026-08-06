"""Deterministic MLOps lineage, registry and promotion contracts."""

from .contracts import (
    ContractError,
    build_candidate_manifest,
    build_dataset_manifest,
    promote_candidate,
)
from .lineage import (
    build_evaluation_from_training_manifest,
    validate_training_manifest,
)
from .registry import (
    build_registry_evidence,
    register_candidate,
    validate_registry_evidence,
    verify_registered_model,
    verify_source_model,
)

__all__ = [
    "ContractError",
    "build_candidate_manifest",
    "build_dataset_manifest",
    "build_evaluation_from_training_manifest",
    "build_registry_evidence",
    "promote_candidate",
    "register_candidate",
    "validate_registry_evidence",
    "validate_training_manifest",
    "verify_registered_model",
    "verify_source_model",
]
