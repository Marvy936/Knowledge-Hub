from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Mapping, Sequence

from mlops_lab.contracts import (
    ContractError,
    atomic_write_json,
    canonical_json_bytes,
    promote_candidate,
    read_json,
    sha256_bytes,
    sha256_file,
)
from mlops_lab.monitoring import inject_drift
from mlops_lab.registry import validate_registry_evidence
from mlops_lab.serving import build_deployment_manifest, validate_deployment_manifest


class LiveRetrainingError(RuntimeError):
    pass


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Execute a real SQLite-backed MLflow controlled retraining lifecycle over the "
            "existing hosted Registry runtime subjects and emit bounded Practical v1 evidence."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--subject-sha", required=True)
    parser.add_argument("--sample-request", type=Path, required=True)
    parser.add_argument("--tracking-uri", default="http://127.0.0.1:5057")
    parser.add_argument("--retraining-seed", type=int, default=20260805)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def _require_subject_sha(value: str) -> str:
    text = value.strip()
    if len(text) != 40 or any(character not in "0123456789abcdef" for character in text):
        raise LiveRetrainingError("subject SHA must be a lowercase 40-character Git SHA-1")
    return text


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
    expected_codes: set[int] | None = None,
) -> subprocess.CompletedProcess[str]:
    allowed = {0} if expected_codes is None else expected_codes
    result = subprocess.run(
        list(command),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONHASHSEED": "0"},
    )
    if result.returncode not in allowed:
        raise LiveRetrainingError(
            f"command returned {result.returncode}, expected {sorted(allowed)}: {' '.join(command)}\n"
            f"stdout tail:\n{(result.stdout or '')[-5000:]}\n"
            f"stderr tail:\n{(result.stderr or '')[-5000:]}"
        )
    return result


def _stdout_json(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    lines = [line for line in (result.stdout or "").splitlines() if line.strip()]
    if not lines:
        raise LiveRetrainingError("command did not return JSON output")
    try:
        value = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise LiveRetrainingError("command final stdout line is not JSON") from exc
    if not isinstance(value, dict):
        raise LiveRetrainingError("command JSON output must be an object")
    return value


def _tracking_endpoint(value: str) -> tuple[str, int]:
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise LiveRetrainingError("tracking URI must use loopback HTTP")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise LiveRetrainingError("tracking URI must not contain path/query/fragment")
    port = parsed.port
    if port is None or not 1 <= port <= 65535:
        raise LiveRetrainingError("tracking URI must contain a valid explicit port")
    return "127.0.0.1", port


def _require_port_unused(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.5)
        if probe.connect_ex((host, port)) == 0:
            raise LiveRetrainingError(
                f"tracking endpoint {host}:{port} is already in use; refusing ambiguous provider ownership"
            )


def _wait_mlflow(tracking_uri: str, process: subprocess.Popen[str], timeout: int = 60) -> None:
    deadline = time.monotonic() + timeout
    last_error = "not attempted"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise LiveRetrainingError(
                f"MLflow server exited before readiness with code {process.returncode}"
            )
        try:
            with urllib.request.urlopen(tracking_uri + "/health", timeout=1) as response:
                if response.status == 200:
                    return
                last_error = f"HTTP {response.status}"
        except (OSError, urllib.error.URLError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        time.sleep(1)
    raise LiveRetrainingError(f"MLflow server did not become ready: {last_error}")


def _start_mlflow(
    *, runtime_dir: Path, tracking_uri: str
) -> tuple[subprocess.Popen[str], Any, Path]:
    host, port = _tracking_endpoint(tracking_uri)
    _require_port_unused(host, port)
    backend = runtime_dir / "mlflow.db"
    artifacts = runtime_dir / "mlartifacts"
    log_path = runtime_dir / "live-retraining-mlflow.log"
    if not backend.is_file() or not artifacts.is_dir():
        raise LiveRetrainingError("baseline Registry database/artifact store is missing")
    handle = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "mlflow",
            "server",
            "--host",
            host,
            "--port",
            str(port),
            "--backend-store-uri",
            f"sqlite:///{backend}",
            "--artifacts-destination",
            f"file://{artifacts}",
            "--allowed-hosts",
            "127.0.0.1:*,localhost:*",
        ],
        cwd=runtime_dir,
        stdout=handle,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        _wait_mlflow(tracking_uri, process)
    except Exception:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        handle.close()
        raise
    return process, handle, log_path


def _stop_mlflow(process: subprocess.Popen[str] | None, handle: Any | None) -> bool:
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=15)
    if handle is not None:
        handle.close()
    return process is None or process.poll() is not None


def _records(count: int = 200) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for index in range(count):
        output.append(
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
    return output


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


def _write_jsonl(path: Path, values: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        for item in values:
            handle.write(json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n")


def _build_retraining_snapshot(baseline: Path, output: Path) -> tuple[int, int, str]:
    if not baseline.is_file() or baseline.is_symlink():
        raise LiveRetrainingError("baseline retraining source must be a regular file")
    if output.exists() or output.is_symlink():
        raise LiveRetrainingError("retraining snapshot output must be fresh")
    with baseline.open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        fieldnames = reader.fieldnames
        if not fieldnames or "customer_id" not in fieldnames:
            raise LiveRetrainingError("baseline dataset does not expose customer_id")
        rows = list(reader)
    if not rows:
        raise LiveRetrainingError("baseline dataset is empty")
    try:
        max_customer_id = max(int(row["customer_id"]) for row in rows)
    except (KeyError, TypeError, ValueError) as exc:
        raise LiveRetrainingError("baseline customer_id values must be integers") from exc
    appended = dict(rows[0])
    appended["customer_id"] = str(max_customer_id + 1)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        writer.writerow(appended)
    return len(rows), len(rows) + 1, sha256_file(output)


def _baseline_subjects(
    *, runtime_dir: Path, subject_sha: str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    candidate = read_json(runtime_dir / "ml" / "candidate.json")
    registry = read_json(runtime_dir / "registry-evidence.json")
    validate_registry_evidence(registry)
    if candidate.get("source_revision") != subject_sha or registry.get("source_revision") != subject_sha:
        raise LiveRetrainingError("baseline candidate/Registry source revision mismatch")
    if candidate.get("candidate_id") != registry.get("candidate_id"):
        raise LiveRetrainingError("baseline candidate and Registry evidence mismatch")

    release, alias_state = promote_candidate(
        candidate=candidate,
        alias_state={"schema_version": 1, "aliases": {}},
        alias="champion",
        expected_current=None,
    )
    control_plane_image_digest = "sha256:" + sha256_bytes(
        canonical_json_bytes(
            {
                "subject": "controlled-retraining-current-deployment-control-plane-image",
                "source_revision": subject_sha,
                "candidate_id": candidate["candidate_id"],
            }
        )
    )
    deployment = build_deployment_manifest(
        release=release,
        registry_evidence=registry,
        service_name="knowledge-hub-churn-api",
        generation="live-retraining-baseline-v1",
        image_reference="knowledge-hub/churn-serving:control-plane-baseline",
        image_digest=control_plane_image_digest,
    )
    validate_deployment_manifest(deployment)
    return candidate, registry, deployment, alias_state


def _version_numbers(client: Any, model_name: str) -> list[str]:
    versions = client.search_model_versions(f"name='{model_name}'")
    resolved = sorted({str(item.version) for item in versions}, key=int)
    if not resolved:
        raise LiveRetrainingError("MLflow model has no registered versions")
    return resolved


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve(strict=True)
    runtime_dir = args.runtime_dir.resolve(strict=True)
    output_path = args.output.resolve(strict=False)
    sample_request = args.sample_request.resolve(strict=True)
    subject_sha = _require_subject_sha(args.subject_sha)
    if output_path.exists() or output_path.is_symlink():
        raise LiveRetrainingError("evidence output must be a fresh path")
    if not sample_request.is_file():
        raise LiveRetrainingError("sample request does not exist")
    if args.retraining_seed < 0:
        raise LiveRetrainingError("retraining seed must be non-negative")
    if _run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip() != subject_sha:
        raise LiveRetrainingError("subject SHA does not match checked-out Git HEAD")

    candidate, registry, deployment, alias_state = _baseline_subjects(
        runtime_dir=runtime_dir,
        subject_sha=subject_sha,
    )
    live_root = runtime_dir / "live-controlled-retraining"
    live_root.mkdir(parents=True, exist_ok=False)
    current_deployment_path = live_root / "current-deployment.json"
    alias_state_path = live_root / "alias-state.json"
    atomic_write_json(current_deployment_path, deployment)
    atomic_write_json(alias_state_path, alias_state)

    baseline_events_path = live_root / "baseline-events.jsonl"
    shifted_events_path = live_root / "shifted-events.jsonl"
    baseline_records = _records()
    shifted_records = inject_drift(baseline_records, mode="shift")
    _write_jsonl(baseline_events_path, _events(baseline_records))
    _write_jsonl(shifted_events_path, _events(shifted_records))

    baseline_path = live_root / "baseline.json"
    window_path = live_root / "window.json"
    drift_path = live_root / "drift.json"
    proposal_path = live_root / "proposal.json"
    monitoring_result = _run(
        [
            sys.executable,
            "labs/mlops/scripts/run_monitoring_drift.py",
            "--baseline-events-jsonl",
            str(baseline_events_path),
            "--window-events-jsonl",
            str(shifted_events_path),
            "--profile-name",
            "live-retraining-baseline",
            "--generation",
            "live-retraining-v1",
            "--deployment-id",
            deployment["deployment_id"],
            "--model-sha256",
            deployment["model"]["sha256"],
            "--policy-generation",
            "retraining-policy-v1",
            "--minimum-successful-events",
            "100",
            "--numeric-psi-threshold",
            "0.20",
            "--categorical-tvd-threshold",
            "0.15",
            "--prediction-rate-delta-threshold",
            "0.10",
            "--maximum-error-rate",
            "0.05",
            "--baseline-output",
            str(baseline_path),
            "--window-output",
            str(window_path),
            "--drift-output",
            str(drift_path),
            "--proposal-output",
            str(proposal_path),
        ],
        cwd=repo_root,
        expected_codes={5},
    )
    monitoring_summary = _stdout_json(monitoring_result)
    drift = read_json(drift_path)
    proposal = read_json(proposal_path)
    if drift.get("status") != "drift_detected" or proposal.get("action") != "approval_required":
        raise LiveRetrainingError("deterministic shift did not create approval-required drift")

    invalid_approval_path = live_root / "invalid-approval.json"
    invalid_result = _run(
        [
            sys.executable,
            "labs/mlops/scripts/approve_retraining.py",
            "--proposal",
            str(proposal_path),
            "--drift-report",
            str(drift_path),
            "--expected-proposal-id",
            "0" * 64,
            "--approver",
            "ml-platform-owner",
            "--approval-generation",
            "live-retraining-approval-v1",
            "--output",
            str(invalid_approval_path),
        ],
        cwd=repo_root,
        expected_codes={2},
    )
    invalid_summary = _stdout_json(invalid_result)
    if invalid_approval_path.exists() or invalid_summary.get("status") != "refused":
        raise LiveRetrainingError("forged proposal approval was not refused cleanly")

    approval_path = live_root / "approval.json"
    approval_result = _run(
        [
            sys.executable,
            "labs/mlops/scripts/approve_retraining.py",
            "--proposal",
            str(proposal_path),
            "--drift-report",
            str(drift_path),
            "--expected-proposal-id",
            proposal["retraining_proposal_id"],
            "--approver",
            "ml-platform-owner",
            "--approval-generation",
            "live-retraining-approval-v1",
            "--output",
            str(approval_path),
        ],
        cwd=repo_root,
    )
    approval_summary = _stdout_json(approval_result)
    approval = read_json(approval_path)
    if approval.get("authorized_action") != "start_controlled_retraining":
        raise LiveRetrainingError("valid approval did not authorize controlled retraining")
    if approval_summary.get("retraining_approval_id") != approval.get("retraining_approval_id"):
        raise LiveRetrainingError("approval CLI summary does not match approval artifact")

    baseline_dataset = runtime_dir / "ml" / "customers.csv"
    if sha256_file(baseline_dataset) != candidate["dataset"]["sha256"]:
        raise LiveRetrainingError("baseline dataset bytes do not match candidate")
    retraining_dataset = live_root / "retraining.csv"
    baseline_rows, retraining_rows, retraining_dataset_sha = _build_retraining_snapshot(
        baseline_dataset,
        retraining_dataset,
    )
    if retraining_dataset_sha == candidate["dataset"]["sha256"]:
        raise LiveRetrainingError("retraining dataset is not a new snapshot")

    server: subprocess.Popen[str] | None = None
    server_handle: Any | None = None
    server_log_path: Path | None = None
    provider_stopped = False
    evidence: dict[str, Any] | None = None
    try:
        server, server_handle, server_log_path = _start_mlflow(
            runtime_dir=runtime_dir,
            tracking_uri=args.tracking_uri,
        )
        import mlflow
        import mlflow.sklearn
        import pandas as pd
        from mlflow.tracking import MlflowClient

        mlflow.set_tracking_uri(args.tracking_uri)
        mlflow.set_registry_uri(args.tracking_uri)
        client = MlflowClient(
            tracking_uri=args.tracking_uri,
            registry_uri=args.tracking_uri,
        )
        model_name = registry["registry"]["name"]
        before_alias = client.get_model_version_by_alias(model_name, "champion")
        before_version = str(before_alias.version)
        if before_version != registry["registry"]["version"]:
            raise LiveRetrainingError("baseline MLflow champion alias does not match Registry evidence")
        before_versions = _version_numbers(client, model_name)

        controlled_output = live_root / "controlled-output"
        operation_path = live_root / "operation.json"
        state_path = live_root / "state.json"
        command = [
            sys.executable,
            "labs/mlops/scripts/run_controlled_retraining.py",
            "--approval",
            str(approval_path),
            "--proposal",
            str(proposal_path),
            "--drift-report",
            str(drift_path),
            "--current-deployment",
            str(current_deployment_path),
            "--dataset",
            str(retraining_dataset),
            "--dataset-name",
            "churn-retraining",
            "--dataset-generation",
            "live-retraining-v1",
            "--sample-request",
            str(sample_request),
            "--source-revision",
            subject_sha,
            "--seed",
            str(args.retraining_seed),
            "--tracking-uri",
            args.tracking_uri,
            "--experiment-name",
            "knowledge-hub-live-controlled-retraining",
            "--model-name",
            model_name,
            "--registry-alias",
            "champion",
            "--promotion-alias",
            "champion",
            "--alias-state",
            str(alias_state_path),
            "--output-dir",
            str(controlled_output),
            "--operation-output",
            str(operation_path),
            "--state",
            str(state_path),
        ]
        first_result = _run(command, cwd=repo_root)
        first_summary = _stdout_json(first_result)
        if first_summary.get("status") != "completed" or first_summary.get("phase") != "completed":
            raise LiveRetrainingError("controlled retraining did not complete")

        state = read_json(state_path)
        new_version = str(state["artifacts"]["registry_version"])
        if new_version == before_version:
            raise LiveRetrainingError("controlled retraining did not create a new Registry version")
        after_alias = client.get_model_version_by_alias(model_name, "champion")
        if str(after_alias.version) != new_version:
            raise LiveRetrainingError("MLflow champion alias did not resolve to the new version")
        after_versions = _version_numbers(client, model_name)
        if len(after_versions) != len(before_versions) + 1 or new_version not in after_versions:
            raise LiveRetrainingError("Registry version inventory did not increase exactly once")
        required_tags = {
            "knowledge_hub.candidate_id": state["artifacts"]["candidate_id"],
            "knowledge_hub.source_revision": subject_sha,
            "knowledge_hub.model_sha256": state["artifacts"]["model_sha256"],
        }
        for key, expected in required_tags.items():
            if (after_alias.tags or {}).get(key) != expected:
                raise LiveRetrainingError(f"new Registry alias tag mismatch for {key}")

        registry_evidence_path = controlled_output / "registry-evidence.json"
        _run(
            [
                sys.executable,
                "-m",
                "mlops_lab",
                "registry-verify",
                "--evidence",
                str(registry_evidence_path),
                "--sample-request",
                str(sample_request),
                "--tracking-uri",
                args.tracking_uri,
            ],
            cwd=repo_root,
        )
        new_registry_evidence = read_json(registry_evidence_path)
        validate_registry_evidence(new_registry_evidence)
        if new_registry_evidence["registry"]["version"] != new_version:
            raise LiveRetrainingError("controlled output Registry evidence version mismatch")

        exact_uri = f"models:/{model_name}/{new_version}"
        loaded = mlflow.sklearn.load_model(exact_uri)
        request = read_json(sample_request)
        frame = pd.DataFrame([request])
        probability = float(loaded.predict_proba(frame)[:, 1][0])
        prediction = int(loaded.predict(frame)[0])
        if not 0.0 <= probability <= 1.0 or prediction not in {0, 1}:
            raise LiveRetrainingError("exact new Registry model returned invalid prediction")

        replay_result = _run(command, cwd=repo_root)
        replay_summary = _stdout_json(replay_result)
        if replay_summary.get("status") != "already_completed":
            raise LiveRetrainingError("second controlled-retraining call was not idempotent replay")
        replay_state = read_json(state_path)
        if replay_state["state_id"] != state["state_id"]:
            raise LiveRetrainingError("completed replay changed durable state identity")
        replay_versions = _version_numbers(client, model_name)
        replay_alias = client.get_model_version_by_alias(model_name, "champion")
        if replay_versions != after_versions or str(replay_alias.version) != new_version:
            raise LiveRetrainingError("completed replay created another Registry side effect")

        payload: dict[str, Any] = {
            "schema_version": 1,
            "evidence_generation": "mlops-live-controlled-retraining-v1",
            "subject_sha": subject_sha,
            "tracking_uri": args.tracking_uri,
            "provider": {
                "type": "mlflow",
                "backend": "sqlite",
                "artifact_store": "local-filesystem",
            },
            "baseline": {
                "candidate_id": candidate["candidate_id"],
                "model_sha256": candidate["model"]["sha256"],
                "dataset_sha256": candidate["dataset"]["sha256"],
                "dataset_rows": baseline_rows,
                "registry_evidence_id": registry["registry_evidence_id"],
                "registry_version": before_version,
                "registry_exact_uri": registry["registry"]["exact_uri"],
                "champion_alias_version": before_version,
                "registered_versions": before_versions,
                "current_deployment_id": deployment["deployment_id"],
                "current_deployment_image_boundary": "control-plane-subject-not-runtime-verified",
            },
            "monitoring": {
                "baseline_profile_id": monitoring_summary["baseline_profile_id"],
                "monitoring_window_id": monitoring_summary["monitoring_window_id"],
                "drift_report_id": drift["drift_report_id"],
                "drift_status": drift["status"],
                "retraining_proposal_id": proposal["retraining_proposal_id"],
                "proposal_action": proposal["action"],
                "event_count": len(baseline_records),
                "injection_mode": "deterministic-shift",
            },
            "approval": {
                "forged_proposal_refused": True,
                "retraining_approval_id": approval["retraining_approval_id"],
                "authorized_action": approval["authorized_action"],
                "approver": approval["approver"],
                "approval_generation": approval["approval_generation"],
                "cli_summary_id": approval_summary["retraining_approval_id"],
            },
            "retraining": {
                "operation_id": first_summary["operation_id"],
                "state_id": state["state_id"],
                "phase": state["phase"],
                "attempt": state["attempt"],
                "dataset_sha256": retraining_dataset_sha,
                "dataset_rows": retraining_rows,
                "snapshot_derivation": "baseline-plus-one-valid-row",
                "training_seed": args.retraining_seed,
                "candidate_id": state["artifacts"]["candidate_id"],
                "model_sha256": state["artifacts"]["model_sha256"],
                "registry_evidence_id": state["artifacts"]["registry_evidence_id"],
                "registry_version": new_version,
                "release_id": state["artifacts"]["release_id"],
            },
            "provider_readback": {
                "registered_versions_after": after_versions,
                "champion_alias_version": new_version,
                "exact_uri": exact_uri,
                "exact_model_probability": round(probability, 15),
                "exact_model_prediction": prediction,
                "registry_verify_passed": True,
            },
            "replay": {
                "status": replay_summary["status"],
                "state_id": replay_state["state_id"],
                "registered_versions_after_replay": replay_versions,
                "champion_alias_version_after_replay": str(replay_alias.version),
                "duplicate_registry_side_effect": False,
            },
            "proof_boundary": {
                "monitoring_events": "deterministic-synthetic",
                "retraining_dataset": "deterministic-synthetic-snapshot",
                "registry_provider": "live-local-mlflow",
                "training": "live-machine-learning-flagship",
                "current_deployment_image_runtime_verified": False,
                "production_traffic_claimed": False,
            },
        }
        evidence = {**payload, "evidence_id": sha256_bytes(canonical_json_bytes(payload))}
    finally:
        provider_stopped = _stop_mlflow(server, server_handle)

    if evidence is None:
        raise LiveRetrainingError("live retraining ended without evidence")
    if not provider_stopped:
        raise LiveRetrainingError("MLflow provider did not stop cleanly")
    if server_log_path is None or not server_log_path.is_file():
        raise LiveRetrainingError("MLflow server log is missing after provider stop")
    database_path = runtime_dir / "mlflow.db"
    if not database_path.is_file():
        raise LiveRetrainingError("MLflow SQLite database is missing after provider stop")
    evidence["provider"]["database_sha256_after_stop"] = sha256_file(database_path)
    evidence["provider"]["server_log_sha256_after_stop"] = hashlib.sha256(
        server_log_path.read_bytes()
    ).hexdigest()
    evidence["provider_stopped"] = True
    payload = {key: value for key, value in evidence.items() if key != "evidence_id"}
    evidence["evidence_id"] = sha256_bytes(canonical_json_bytes(payload))
    atomic_write_json(output_path, evidence)
    return evidence


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        evidence = run(args)
    except (ContractError, LiveRetrainingError, OSError, RuntimeError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "refused", "error": f"{type(exc).__name__}: {exc}"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(
        json.dumps(
            {
                "status": "passed",
                "subject_sha": evidence["subject_sha"],
                "before_version": evidence["baseline"]["registry_version"],
                "after_version": evidence["retraining"]["registry_version"],
                "operation_id": evidence["retraining"]["operation_id"],
                "champion_alias_version": evidence["provider_readback"]["champion_alias_version"],
                "replay_status": evidence["replay"]["status"],
                "provider_stopped": evidence["provider_stopped"],
                "evidence_id": evidence["evidence_id"],
                "output": args.output.as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
