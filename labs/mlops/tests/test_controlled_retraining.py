from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from mlops_lab.contracts import (
    ContractError,
    atomic_write_json,
    canonical_json_bytes,
    read_json,
    sha256_bytes,
    sha256_file,
)
from mlops_lab.controlled_retraining import (
    build_controlled_retraining_operation,
    execute_controlled_retraining,
    validate_controlled_retraining_operation,
)
from mlops_lab.monitoring import (
    build_baseline_profile,
    build_monitoring_window,
    compare_drift,
    inject_drift,
)
from mlops_lab.registry import build_registry_evidence
from mlops_lab.retraining import approve_retraining, build_retraining_proposal


def _records(count: int = 100) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for index in range(count):
        records.append(
            {
                "tenure_months": 5 + index % 50,
                "monthly_spend_eur": 40.0 + index % 50,
                "support_tickets_90d": index % 5,
                "login_days_30d": 10 + index % 15,
                "days_since_last_login": index % 20,
                "contract_type": ("monthly", "annual", "two_year")[index % 3],
                "region": ("west", "central", "east", "north")[index % 4],
                "auto_pay": "yes" if index % 2 == 0 else "no",
            }
        )
    return records


def _events(records: list[dict[str, object]]) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    for index, record in enumerate(records):
        probability = min(
            0.99,
            (
                float(record["monthly_spend_eur"]) / 250
                + int(record["support_tickets_90d"]) / 30
                + int(record["days_since_last_login"]) / 180
                + (0.2 if record["contract_type"] == "monthly" else 0)
                + (0.1 if record["auto_pay"] == "no" else 0)
            )
            / 2,
        )
        events.append(
            {
                "record": record,
                "success": True,
                "latency_ms": 10.0 + index % 3,
                "prediction": int(probability >= 0.4),
                "probability": probability,
            }
        )
    return events


def _deployment() -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": 1,
        "service_name": "churn",
        "generation": "stable-1",
        "release_id": "1" * 64,
        "candidate_id": "2" * 64,
        "source_revision": "old-revision",
        "dataset_sha256": "3" * 64,
        "evaluation_sha256": "4" * 64,
        "model": {
            "sha256": "5" * 64,
            "registry_name": "Churn",
            "registry_version": "1",
            "exact_uri": "models:/Churn/1",
            "registry_evidence_id": "6" * 64,
        },
        "image": {
            "reference": "example/churn:1",
            "digest": "sha256:" + "7" * 64,
        },
    }
    return {
        **payload,
        "deployment_id": sha256_bytes(canonical_json_bytes(payload)),
    }


def _authorization(current_deployment: dict[str, object]):
    baseline = build_baseline_profile(
        events=_events(_records()),
        profile_name="baseline",
        generation="g1",
    )
    shifted = inject_drift(_records(), mode="shift")
    window = build_monitoring_window(
        events=_events(shifted),
        baseline=baseline,
        deployment_id=current_deployment["deployment_id"],
    )
    report = compare_drift(
        baseline=baseline,
        window=window,
        minimum_successful_events=50,
        numeric_psi_threshold=0.2,
        categorical_tvd_threshold=0.15,
        prediction_rate_delta_threshold=0.1,
        maximum_error_rate=0.05,
    )
    assert report["status"] == "drift_detected"
    proposal = build_retraining_proposal(
        drift_report=report,
        model_sha256=current_deployment["model"]["sha256"],
        policy_generation="retraining-policy-v1",
    )
    approval = approve_retraining(
        proposal=proposal,
        drift_report=report,
        expected_proposal_id=proposal["retraining_proposal_id"],
        approver="owner",
        approval_generation="approval-v1",
    )
    return report, proposal, approval


def _inputs(tmp_path: Path):
    deployment = _deployment()
    report, proposal, approval = _authorization(deployment)
    dataset = tmp_path / "new.csv"
    dataset.write_text("customer_id,value\n1,new\n", encoding="utf-8")
    request = tmp_path / "request.json"
    request.write_text(json.dumps({"x": 1}), encoding="utf-8")
    operation = build_controlled_retraining_operation(
        approval=approval,
        proposal=proposal,
        drift_report=report,
        current_deployment=deployment,
        dataset_path=dataset,
        dataset_name="churn-retraining",
        dataset_generation="2026-08-06",
        sample_request_path=request,
        source_revision="new-revision",
        seed=20260806,
        tracking_uri="http://127.0.0.1:5000",
        experiment_name="retraining",
        model_name="Churn",
        registry_alias="candidate",
        promotion_alias="champion",
    )
    alias_state = tmp_path / "alias.json"
    atomic_write_json(
        alias_state,
        {
            "schema_version": 1,
            "aliases": {"champion": deployment["candidate_id"]},
        },
    )
    return (
        deployment,
        report,
        proposal,
        approval,
        dataset,
        request,
        operation,
        alias_state,
    )


def _valid_manifest(
    dataset: Path, model: Path, source_revision: str
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "artifact_type": "trusted-local-scikit-learn-pipeline",
        "model_file": "model.joblib",
        "dataset_sha256": sha256_file(dataset),
        "model_sha256": sha256_file(model),
        "source_revision": source_revision,
        "threshold_status": "recall_gate_satisfied",
        "selected_model": "logistic_regression",
        "test_metrics": {"f1": 0.8, "recall": 0.75, "precision": 0.81},
        "acceptance_gates": {
            "minimum_test_f1": 0.55,
            "minimum_test_recall": 0.55,
            "selected_f1_must_exceed_dummy": True,
        },
        "library_versions": {
            "python": "3.13",
            "numpy": "2",
            "pandas": "2",
            "scikit_learn": "1.8",
            "joblib": "1.5",
        },
        "decision_threshold": 0.4,
    }


def _train(calls: list[str], *, fail_after_write: bool = False):
    def adapter(
        dataset: Path, artifact_dir: Path, seed: int, source_revision: str
    ):
        del seed
        calls.append("train")
        artifact_dir.mkdir(parents=True, exist_ok=False)
        model = artifact_dir / "model.joblib"
        model.write_bytes(b"new-model-bytes")
        manifest = _valid_manifest(dataset, model, source_revision)
        atomic_write_json(artifact_dir / "manifest.json", manifest)
        if fail_after_write:
            raise RuntimeError("crash after training")
        return manifest

    return adapter


def _registry(calls: list[str], *, wrong_candidate: bool = False):
    def adapter(candidate, model_path, sample_request_path, config, download_dir):
        calls.append("registry")
        download_dir.mkdir(parents=True, exist_ok=True)
        model_sha256 = sha256_file(model_path)
        candidate_id = "f" * 64 if wrong_candidate else candidate["candidate_id"]
        return build_registry_evidence(
            tracking_uri=config["tracking_uri"],
            experiment_id="experiment-1",
            run_id="run-1",
            logged_model_id="logged-1",
            candidate_id=candidate_id,
            source_revision=candidate["source_revision"],
            model_name=config["model_name"],
            version="2",
            alias=config["alias"],
            alias_resolved_version="2",
            source_uri="runs:/run-1/model",
            source_run_id="run-1",
            model_version_status="READY",
            model_version_tags={
                "knowledge_hub.candidate_id": candidate_id,
                "knowledge_hub.source_revision": candidate["source_revision"],
                "knowledge_hub.model_sha256": model_sha256,
            },
            artifact_path="source/model.joblib",
            original_model_sha256=model_sha256,
            downloaded_model_sha256=model_sha256,
            model_size_bytes=model_path.stat().st_size,
            request=json.loads(
                sample_request_path.read_text(encoding="utf-8")
            ),
            source_probability=0.2,
            source_prediction=0,
            registry_probability=0.2,
            registry_prediction=0,
            mlflow_version="3.14.0",
        )

    return adapter


def _execute(args, train_adapter, registry_adapter, recover=None):
    (
        deployment,
        report,
        proposal,
        approval,
        dataset,
        request,
        operation,
        alias_state,
    ) = args
    return execute_controlled_retraining(
        operation=operation,
        approval=approval,
        proposal=proposal,
        drift_report=report,
        current_deployment=deployment,
        dataset_path=dataset,
        sample_request_path=request,
        output_dir=dataset.parent / "output",
        alias_state_path=alias_state,
        state_path=dataset.parent / "state.json",
        train_adapter=train_adapter,
        registry_adapter=registry_adapter,
        recover_expected_state_id=recover,
    )


def test_operation_binds_authorization_deployment_and_fresh_dataset(
    tmp_path: Path,
) -> None:
    args = _inputs(tmp_path)
    operation = args[6]
    validate_controlled_retraining_operation(operation)
    assert operation["current_deployment_id"] == args[0]["deployment_id"]
    tampered = deepcopy(operation)
    tampered["seed"] += 1
    with pytest.raises(ContractError, match="operation_id"):
        validate_controlled_retraining_operation(tampered)


def test_same_dataset_as_current_deployment_is_refused(tmp_path: Path) -> None:
    deployment = _deployment()
    dataset = tmp_path / "same.bin"
    dataset.write_bytes(b"same")
    deployment["dataset_sha256"] = sha256_file(dataset)
    payload = {
        key: value for key, value in deployment.items() if key != "deployment_id"
    }
    deployment["deployment_id"] = sha256_bytes(canonical_json_bytes(payload))
    report, proposal, approval = _authorization(deployment)
    request = tmp_path / "request.json"
    request.write_text("{}", encoding="utf-8")
    with pytest.raises(ContractError, match="new dataset snapshot"):
        build_controlled_retraining_operation(
            approval=approval,
            proposal=proposal,
            drift_report=report,
            current_deployment=deployment,
            dataset_path=dataset,
            dataset_name="d",
            dataset_generation="g2",
            sample_request_path=request,
            source_revision="new",
            seed=1,
            tracking_uri="http://127.0.0.1",
            experiment_name="x",
            model_name="M",
            registry_alias="candidate",
            promotion_alias="champion",
        )


def test_full_execution_and_second_call_are_idempotent(tmp_path: Path) -> None:
    args = _inputs(tmp_path)
    calls: list[str] = []
    result = _execute(args, _train(calls), _registry(calls))
    assert result["status"] == "completed"
    assert calls == ["train", "registry"]
    state = result["state"]
    assert state["phase"] == "completed"
    assert (
        read_json(args[7])["aliases"]["champion"]
        == state["artifacts"]["candidate_id"]
    )
    replay = _execute(
        args,
        lambda *unused: (_ for _ in ()).throw(
            AssertionError("training repeated")
        ),
        lambda *unused: (_ for _ in ()).throw(
            AssertionError("Registry repeated")
        ),
    )
    assert replay["status"] == "already_completed"
    assert replay["state"]["state_id"] == state["state_id"]


def test_incomplete_operation_requires_exact_recovery(tmp_path: Path) -> None:
    args = _inputs(tmp_path)
    calls: list[str] = []

    def crash(*unused):
        calls.append("train")
        raise RuntimeError("before outputs")

    with pytest.raises(RuntimeError):
        _execute(args, crash, _registry(calls))
    failed = read_json(tmp_path / "state.json")
    assert failed["phase"] == "failed"
    with pytest.raises(ContractError, match="explicit recovery"):
        _execute(args, _train(calls), _registry(calls))
    result = _execute(
        args,
        _train(calls),
        _registry(calls),
        recover=failed["state_id"],
    )
    assert result["state"]["phase"] == "completed"
    assert result["state"]["attempt"] == 2


def test_recovery_uses_completed_training_readback_without_retraining(
    tmp_path: Path,
) -> None:
    args = _inputs(tmp_path)
    calls: list[str] = []
    with pytest.raises(RuntimeError):
        _execute(
            args,
            _train(calls, fail_after_write=True),
            _registry(calls),
        )
    failed = read_json(tmp_path / "state.json")
    result = _execute(
        args,
        lambda *unused: (_ for _ in ()).throw(
            AssertionError("training repeated")
        ),
        _registry(calls),
        recover=failed["state_id"],
    )
    assert result["state"]["phase"] == "completed"
    assert calls.count("train") == 1


def test_stale_alias_failure_recovers_from_registry_checkpoint(
    tmp_path: Path,
) -> None:
    args = list(_inputs(tmp_path))
    atomic_write_json(
        args[7],
        {"schema_version": 1, "aliases": {"champion": "9" * 64}},
    )
    calls: list[str] = []
    with pytest.raises(ContractError, match="stale promotion"):
        _execute(tuple(args), _train(calls), _registry(calls))
    failed = read_json(tmp_path / "state.json")
    atomic_write_json(
        args[7],
        {
            "schema_version": 1,
            "aliases": {"champion": args[0]["candidate_id"]},
        },
    )
    result = _execute(
        tuple(args),
        lambda *unused: (_ for _ in ()).throw(
            AssertionError("training repeated")
        ),
        lambda *unused: (_ for _ in ()).throw(
            AssertionError("Registry repeated")
        ),
        recover=failed["state_id"],
    )
    assert result["state"]["phase"] == "completed"


def test_registry_evidence_for_another_candidate_is_refused(
    tmp_path: Path,
) -> None:
    args = _inputs(tmp_path)
    calls: list[str] = []
    with pytest.raises(ContractError, match="another candidate"):
        _execute(args, _train(calls), _registry(calls, wrong_candidate=True))
    assert read_json(tmp_path / "state.json")["phase"] == "failed"


def test_current_deployment_change_after_approval_is_refused(
    tmp_path: Path,
) -> None:
    args = list(_inputs(tmp_path))
    changed = deepcopy(args[0])
    changed["generation"] = "stable-2"
    payload = {
        key: value for key, value in changed.items() if key != "deployment_id"
    }
    changed["deployment_id"] = sha256_bytes(canonical_json_bytes(payload))
    args[0] = changed
    with pytest.raises(ContractError, match="current deployment changed"):
        _execute(tuple(args), _train([]), _registry([]))


def test_completed_state_detects_output_tampering(tmp_path: Path) -> None:
    args = _inputs(tmp_path)
    _execute(args, _train([]), _registry([]))
    (tmp_path / "output" / "release.json").write_text(
        "{}", encoding="utf-8"
    )
    with pytest.raises(ContractError):
        _execute(args, _train([]), _registry([]))


def test_stale_recovery_subject_is_refused_without_state_mutation(
    tmp_path: Path,
) -> None:
    args = _inputs(tmp_path)
    with pytest.raises(RuntimeError):
        _execute(
            args,
            lambda *unused: (_ for _ in ()).throw(RuntimeError("crash")),
            _registry([]),
        )
    before = read_json(tmp_path / "state.json")
    with pytest.raises(ContractError, match="stale retraining recovery subject"):
        _execute(args, _train([]), _registry([]), recover="f" * 64)
    assert read_json(tmp_path / "state.json") == before


def test_registry_failure_recovers_from_candidate_checkpoint(
    tmp_path: Path,
) -> None:
    args = _inputs(tmp_path)
    calls: list[str] = []
    with pytest.raises(ContractError, match="another candidate"):
        _execute(args, _train(calls), _registry(calls, wrong_candidate=True))
    failed = read_json(tmp_path / "state.json")
    result = _execute(
        args,
        lambda *unused: (_ for _ in ()).throw(
            AssertionError("training repeated")
        ),
        _registry(calls),
        recover=failed["state_id"],
    )
    assert result["state"]["phase"] == "completed"
    assert calls.count("train") == 1
    assert calls.count("registry") == 2
