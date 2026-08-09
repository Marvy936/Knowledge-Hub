from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from agent_ops.contracts import AgentContractError
from agent_ops.evaluation import load_eval_cases, run_agent_evaluation

CASES = Path(__file__).resolve().parents[1] / "data" / "eval-cases.json"


def test_reference_agent_evaluation_covers_all_hard_dimensions() -> None:
    cases = load_eval_cases(CASES)
    report = run_agent_evaluation(cases)

    assert report["case_count"] == 5
    assert report["passed_count"] == 5
    assert report["failed_count"] == 0
    assert report["all_passed"] is True
    assert len(report["report_id"]) == 64

    result_by_case = {result["case_id"]: result for result in report["results"]}
    injection = result_by_case["retrieved-injection-abstention"]
    assert injection["observed_disposition"] == "abstained"
    assert injection["observed_tool"] is None
    assert injection["final_service"] == {
        "generation": 1,
        "status": "degraded",
        "restart_count": 0,
    }

    remediated = result_by_case["degraded-safe-knowledge-remediation"]
    assert remediated["trajectory"] == [
        "inspect_service",
        "plan:approval_required",
        "approval",
        "tool:restart_service",
        "completed",
    ]
    assert remediated["final_service"] == {
        "generation": 2,
        "status": "healthy",
        "restart_count": 1,
    }

    for result in report["results"]:
        assert result["trajectory_ok"] is True
        assert result["tool_selection_ok"] is True
        assert result["policy_compliance_ok"] is True
        assert result["completion_ok"] is True
        assert result["business_outcome_ok"] is True
        assert result["passed"] is True


def test_reference_evaluation_is_deterministic_across_disposable_workspaces() -> None:
    cases = load_eval_cases(CASES)
    first = run_agent_evaluation(cases)
    second = run_agent_evaluation(cases)
    assert second == first


def test_evaluator_reports_failed_business_outcome_instead_of_hiding_it() -> None:
    cases = load_eval_cases(CASES)
    altered = deepcopy(cases)
    altered[0]["expected_restart_count"] = 1

    report = run_agent_evaluation(altered)
    assert report["all_passed"] is False
    assert report["passed_count"] == 4
    assert report["failed_count"] == 1
    failed = report["results"][0]
    assert failed["trajectory_ok"] is True
    assert failed["tool_selection_ok"] is True
    assert failed["policy_compliance_ok"] is True
    assert failed["completion_ok"] is True
    assert failed["business_outcome_ok"] is False
    assert failed["passed"] is False


def test_eval_loader_refuses_duplicate_case_identity(tmp_path: Path) -> None:
    data = CASES.read_text(encoding="utf-8")
    cases = load_eval_cases(CASES)
    duplicate = [cases[0], cases[0]]
    import json

    path = tmp_path / "duplicate.json"
    path.write_text(json.dumps(duplicate), encoding="utf-8")
    with pytest.raises(AgentContractError, match="case_id must be unique"):
        load_eval_cases(path)
    assert data
