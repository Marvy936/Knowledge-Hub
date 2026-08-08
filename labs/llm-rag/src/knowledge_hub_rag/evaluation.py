from __future__ import annotations

from typing import Any, Iterable, Mapping

from .answers import validate_answer_envelope
from .contracts import ContractError, canonical_json_bytes, sha256_bytes
from .offline_adapter import run_offline_adapter, validate_offline_adapter_result
from .retrieval import build_grounded_context, retrieve, validate_retrieval_result
from .runtime_config import validate_runtime_config

EVAL_SCHEMA_VERSION = 1
SLICES = ("retrieval", "citation", "faithfulness", "abstention", "security")
ATTACK_TYPES = {"none", "direct", "indirect"}
EXPECTED_RETRIEVAL = {"results", "no_result", "any"}
EXPECTED_ANSWER = {"answered", "abstained"}


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value.strip()


def validate_eval_case(case: Mapping[str, Any]) -> None:
    expected = {
        "case_id",
        "query",
        "critical",
        "slices",
        "expected_retrieval",
        "expected_answer",
        "expected_abstention_reason",
        "expected_source_paths",
        "attack_type",
    }
    if set(case) != expected:
        raise ContractError("eval case keys mismatch")
    _require_nonempty_string(case.get("case_id"), "case_id")
    _require_nonempty_string(case.get("query"), "query")
    if not isinstance(case.get("critical"), bool):
        raise ContractError("eval case critical must be boolean")
    slices = case.get("slices")
    if not isinstance(slices, list) or not slices or slices != sorted(set(slices)):
        raise ContractError("eval case slices must be a sorted unique non-empty list")
    if any(item not in SLICES for item in slices):
        raise ContractError("eval case contains an unsupported slice")
    if case.get("expected_retrieval") not in EXPECTED_RETRIEVAL:
        raise ContractError("eval case expected_retrieval is unsupported")
    if case.get("expected_answer") not in EXPECTED_ANSWER:
        raise ContractError("eval case expected_answer is unsupported")
    if case["expected_retrieval"] == "any" and "retrieval" in slices:
        raise ContractError("retrieval slice requires an exact expected retrieval state")
    if case["expected_answer"] == "abstained" and any(
        item in slices for item in ("citation", "faithfulness")
    ):
        raise ContractError("abstention case cannot require citation or faithfulness slices")
    if case["expected_answer"] == "answered" and "abstention" in slices:
        raise ContractError("answered case cannot require abstention slice")
    reason = case.get("expected_abstention_reason")
    if case["expected_answer"] == "answered" and reason is not None:
        raise ContractError("answered eval case must not expect abstention reason")
    if reason is not None:
        _require_nonempty_string(reason, "expected_abstention_reason")
    paths = case.get("expected_source_paths")
    if not isinstance(paths, list) or paths != sorted(set(paths)):
        raise ContractError("expected_source_paths must be a sorted unique list")
    if any(not isinstance(item, str) or not item for item in paths):
        raise ContractError("expected_source_paths entries must be non-empty strings")
    if case.get("attack_type") not in ATTACK_TYPES:
        raise ContractError("eval case attack_type is unsupported")


def _slice(value: bool | None, detail: str) -> dict[str, Any]:
    return {"applicable": value is not None, "passed": value, "detail": detail}


def _faithfulness(answer: Mapping[str, Any], retrieval: Mapping[str, Any]) -> bool | None:
    if answer.get("status") != "answered":
        return None
    text = answer.get("answer")
    if not isinstance(text, str) or not text:
        return False
    cited = {item.get("chunk_id") for item in answer.get("citations", [])}
    contents = [
        hit.get("content", "")
        for hit in retrieval.get("hits", [])
        if hit.get("citation", {}).get("chunk_id") in cited
    ]
    return bool(contents) and any(text in content for content in contents)


def run_eval_case(
    *,
    case: Mapping[str, Any],
    manifest: Mapping[str, Any],
    index: Mapping[str, Any],
    runtime_config: Mapping[str, Any],
) -> dict[str, Any]:
    validate_eval_case(case)
    validate_runtime_config(runtime_config)
    retrieval = retrieve(
        index=index,
        manifest=manifest,
        query=case["query"],
        top_k=runtime_config["retrieval"]["top_k"],
        min_score=runtime_config["retrieval"]["min_score"],
    )
    validate_retrieval_result(retrieval, index=index, manifest=manifest)
    context = build_grounded_context(
        retrieval,
        index=index,
        manifest=manifest,
        max_chars=runtime_config["context"]["max_chars"],
    )
    adapter = run_offline_adapter(
        retrieval_result=retrieval,
        index=index,
        manifest=manifest,
        runtime_config=runtime_config,
    )
    validate_offline_adapter_result(
        adapter,
        retrieval_result=retrieval,
        index=index,
        manifest=manifest,
        runtime_config=runtime_config,
    )
    answer = adapter["answer"]
    validate_answer_envelope(
        answer,
        retrieval_result=retrieval,
        index=index,
        manifest=manifest,
    )

    expected_retrieval = case["expected_retrieval"]
    retrieval_pass = None if expected_retrieval == "any" else retrieval["status"] == expected_retrieval
    paths = set(case["expected_source_paths"])
    if paths and retrieval_pass is not False:
        retrieval_pass = any(hit["citation"]["source_path"] in paths for hit in retrieval["hits"])

    if answer["status"] == "answered":
        citation_pass: bool | None = bool(answer["citations"])
        if citation_pass and paths:
            citation_pass = all(item["source_path"] in paths for item in answer["citations"])
    else:
        citation_pass = None

    faithfulness_pass = _faithfulness(answer, retrieval)
    abstention_pass = answer["status"] == case["expected_answer"]
    if (
        abstention_pass
        and case["expected_answer"] == "abstained"
        and case["expected_abstention_reason"] is not None
    ):
        abstention_pass = answer["abstention_reason"] == case["expected_abstention_reason"]

    query_security = adapter["query_security"]
    hit_security = adapter["hit_security"]
    attack_type = case["attack_type"]
    if attack_type == "direct":
        security_pass = (
            query_security["classification"] == "prompt_injection_detected"
            and answer["status"] == "abstained"
            and answer["abstention_reason"] == "direct_prompt_injection"
        )
    elif attack_type == "indirect":
        unsafe_ids = {
            evidence["subject_id"]
            for evidence in hit_security
            if evidence["classification"] == "prompt_injection_detected"
        }
        cited_ids = {item["chunk_id"] for item in answer.get("citations", [])}
        security_pass = bool(unsafe_ids) and not unsafe_ids.intersection(cited_ids)
    else:
        security_pass = query_security["classification"] == "clean"
        if answer["status"] == "answered":
            cited_ids = {item["chunk_id"] for item in answer["citations"]}
            security_by_id = {item["subject_id"]: item for item in hit_security}
            security_pass = security_pass and all(
                security_by_id.get(chunk_id, {}).get("classification") == "clean"
                for chunk_id in cited_ids
            )

    observed = {
        "retrieval": _slice(retrieval_pass, retrieval["status"]),
        "citation": _slice(citation_pass, f"citations={len(answer['citations'])}"),
        "faithfulness": _slice(faithfulness_pass, "extractive substring of cited chunk"),
        "abstention": _slice(abstention_pass, answer["status"]),
        "security": _slice(security_pass, attack_type),
    }
    case_passed = all(
        observed[name]["applicable"] and observed[name]["passed"] is True
        for name in case["slices"]
    )
    payload = {
        "schema_version": EVAL_SCHEMA_VERSION,
        "case_id": case["case_id"],
        "critical": case["critical"],
        "required_slices": list(case["slices"]),
        "runtime_config_id": runtime_config["runtime_config_id"],
        "retrieval_result_id": retrieval["retrieval_result_id"],
        "context_id": context["context_id"],
        "adapter_result_id": adapter["adapter_result_id"],
        "answer_id": answer["answer_id"],
        "slices": observed,
        "case_passed": case_passed,
    }
    return {**payload, "case_result_id": sha256_bytes(canonical_json_bytes(payload))}


def run_eval_suite(
    *,
    cases: Iterable[Mapping[str, Any]],
    manifest: Mapping[str, Any],
    index: Mapping[str, Any],
    runtime_config: Mapping[str, Any],
) -> dict[str, Any]:
    validate_runtime_config(runtime_config)
    resolved = list(cases)
    if not resolved:
        raise ContractError("eval suite requires at least one case")
    ids: set[str] = set()
    results: list[dict[str, Any]] = []
    for case in resolved:
        validate_eval_case(case)
        if case["case_id"] in ids:
            raise ContractError("eval case IDs must be unique")
        ids.add(case["case_id"])
        results.append(
            run_eval_case(
                case=case,
                manifest=manifest,
                index=index,
                runtime_config=runtime_config,
            )
        )

    metrics: dict[str, dict[str, Any]] = {}
    threshold_failures: list[str] = []
    for name in SLICES:
        required = [result for result in results if name in result["required_slices"]]
        applicable = [result["slices"][name] for result in required]
        passed = sum(
            item["applicable"] and item["passed"] is True for item in applicable
        )
        rate = None if not applicable else passed / len(applicable)
        threshold = float(runtime_config["eval_thresholds"][name])
        gate_passed = rate is not None and rate >= threshold
        metrics[name] = {
            "passed": passed,
            "total": len(applicable),
            "rate": None if rate is None else round(rate, 9),
            "threshold": threshold,
            "gate_passed": gate_passed,
        }
        if not gate_passed:
            threshold_failures.append(name)

    critical_failures = sorted(
        result["case_id"]
        for result in results
        if result["critical"] and result["case_passed"] is not True
    )
    high_risk_failures = sorted(
        name
        for name in runtime_config["high_risk_slices"]
        if metrics[name]["gate_passed"] is not True
    )
    passed_cases = sum(result["case_passed"] is True for result in results)
    suite_passed = not threshold_failures and not critical_failures and not high_risk_failures
    payload = {
        "schema_version": EVAL_SCHEMA_VERSION,
        "runtime_config_id": runtime_config["runtime_config_id"],
        "case_count": len(results),
        "passed_cases": passed_cases,
        "aggregate_case_rate": round(passed_cases / len(results), 9),
        "slice_metrics": metrics,
        "critical_failures": critical_failures,
        "high_risk_failures": high_risk_failures,
        "threshold_failures": sorted(threshold_failures),
        "suite_passed": suite_passed,
        "results": results,
    }
    return {**payload, "eval_report_id": sha256_bytes(canonical_json_bytes(payload))}


def validate_eval_report(
    value: Mapping[str, Any],
    *,
    cases: Iterable[Mapping[str, Any]],
    manifest: Mapping[str, Any],
    index: Mapping[str, Any],
    runtime_config: Mapping[str, Any],
) -> None:
    expected = run_eval_suite(
        cases=cases,
        manifest=manifest,
        index=index,
        runtime_config=runtime_config,
    )
    if dict(value) != expected:
        raise ContractError("eval report does not match deterministic suite rebuild")


def build_prompt_release(
    *,
    runtime_config: Mapping[str, Any],
    eval_report: Mapping[str, Any],
    cases: Iterable[Mapping[str, Any]],
    manifest: Mapping[str, Any],
    index: Mapping[str, Any],
) -> dict[str, Any]:
    validate_runtime_config(runtime_config)
    resolved_cases = list(cases)
    validate_eval_report(
        eval_report,
        cases=resolved_cases,
        manifest=manifest,
        index=index,
        runtime_config=runtime_config,
    )
    if eval_report.get("suite_passed") is not True:
        raise ContractError("runtime config cannot be released while eval suite fails")
    payload = {
        "schema_version": EVAL_SCHEMA_VERSION,
        "runtime_config_id": runtime_config["runtime_config_id"],
        "generation": runtime_config["generation"],
        "eval_report_id": eval_report["eval_report_id"],
        "status": "promoted",
    }
    return {**payload, "prompt_release_id": sha256_bytes(canonical_json_bytes(payload))}
