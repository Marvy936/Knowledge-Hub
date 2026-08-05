"""Domain-specific errors with stable CLI semantics."""


class MLLabError(RuntimeError):
    """Base error for expected lab failures."""


class DataValidationError(MLLabError):
    """Dataset violates the declared training contract."""


class TrainingGateError(MLLabError):
    """Candidate model does not satisfy the declared acceptance gate."""


class ArtifactIntegrityError(MLLabError):
    """Persisted artifact or manifest failed integrity validation."""


class InferenceInputError(MLLabError):
    """Inference request does not match the feature contract."""
