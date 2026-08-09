from __future__ import annotations

from pathlib import Path

from scripts import practical_v1_core
from scripts import validate_practical_v1_repo


def _passing_stages() -> list[dict[str, object]]:
    names = [name for name, _ in practical_v1_core.STAGES] + ["agent-hard-evaluation"]
    return [{"name": name, "passed": True} for name in names]


def test_core_report_refuses_zero_stage_success() -> None:
    report = practical_v1_core._build_report(
        subject_sha="a" * 40,
        python_version="3.12.0",
        stages=[],
        cleanup_verified=True,
        preflight_error=None,
    )
    assert report["all_passed"] is False
    assert report["stage_count"] == 0


def test_core_report_requires_exact_stage_order_and_cleanup() -> None:
    stages = _passing_stages()
    report = practical_v1_core._build_report(
        subject_sha="a" * 40,
        python_version="3.12.0",
        stages=stages,
        cleanup_verified=True,
        preflight_error=None,
    )
    assert report["all_passed"] is True

    reordered = list(reversed(stages))
    report = practical_v1_core._build_report(
        subject_sha="a" * 40,
        python_version="3.12.0",
        stages=reordered,
        cleanup_verified=True,
        preflight_error=None,
    )
    assert report["all_passed"] is False

    report = practical_v1_core._build_report(
        subject_sha="a" * 40,
        python_version="3.12.0",
        stages=stages,
        cleanup_verified=False,
        preflight_error=None,
    )
    assert report["all_passed"] is False


def test_markdown_target_parser_ignores_fenced_examples(tmp_path: Path) -> None:
    document = tmp_path / "README.md"
    document.write_text(
        "[real](docs/real.md)\n"
        "```markdown\n"
        "[example](docs/not-real.md)\n"
        "```\n"
        "[anchor](#section)\n",
        encoding="utf-8",
    )
    assert validate_practical_v1_repo._markdown_targets(document) == [
        "docs/real.md",
        "#section",
    ]


def test_path_policy_allows_only_runtime_subtree_inside_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    evidence = tmp_path / "evidence.json"

    _, allowed, _ = practical_v1_core._validate_paths(
        repo,
        repo / ".runtime" / "practical-v1" / "run-1",
        evidence,
    )
    assert allowed == (repo / ".runtime" / "practical-v1" / "run-1").resolve()

    try:
        practical_v1_core._validate_paths(repo, repo / "other-work", evidence)
    except practical_v1_core.CoreRunError:
        pass
    else:
        raise AssertionError("work root outside .runtime/practical-v1 must be refused")
