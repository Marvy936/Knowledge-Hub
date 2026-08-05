"""Expected MLOps lifecycle failures with stable CLI semantics."""


class MLOpsLabError(RuntimeError):
    """Base error for expected lifecycle refusals."""


class WorkspaceError(MLOpsLabError):
    """Workspace or backend state is unavailable or inconsistent."""


class EvidenceIntegrityError(MLOpsLabError):
    """Digest-bound request, report or release evidence was changed."""


class PromotionRefused(MLOpsLabError):
    """Promotion gates, approval or Registry read-back did not pass."""


class DriftNotActionable(MLOpsLabError):
    """A retraining request lacks a valid actionable drift signal."""


class CanaryRefused(MLOpsLabError):
    """Candidate canary evidence does not satisfy promotion policy."""


class RollbackRefused(MLOpsLabError):
    """Rollback subject or current Registry state is stale or invalid."""
