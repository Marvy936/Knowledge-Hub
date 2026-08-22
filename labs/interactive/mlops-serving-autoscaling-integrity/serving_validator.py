#!/usr/bin/env python3
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path.cwd()
PROTECTED = [
    "serving-contract.json",
    "release-manifest.json",
    "capacity-evidence.json",
    "runtime-state.json",
    "traffic-evidence.json",
]
GENERATED = ["capacity-report.json", "capacity-ledger.json"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def clean(root):
    for name in GENERATED:
        (root / name).unlink(missing_ok=True)


def execute(root):
    return subprocess.run(
        ["python3", "serving_gate.py"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=20,
    )


def current_to(dst):
    for name in PROTECTED:
        shutil.copy2(ROOT / name, dst / name)
    shutil.copy2(ROOT / "serving_gate.py", dst / "serving_gate.py")


def refresh_release_digest(root):
    contract = read_json(root / "serving-contract.json")
    contract["release_manifest_digest"] = digest(root / "release-manifest.json")
    write_json(root / "serving-contract.json", contract)


def refresh_capacity_digest(root):
    contract = read_json(root / "serving-contract.json")
    contract["capacity_evidence_digest"] = digest(root / "capacity-evidence.json")
    write_json(root / "serving-contract.json", contract)


def make_healthy(root):
    contract = read_json(root / "serving-contract.json")
    runtime = read_json(root / "runtime-state.json")
    runtime["resolved_scaling"] = {
        "min_replicas": contract["min_replicas"],
        "max_replicas": contract["max_replicas"],
        "container_concurrency": contract["container_concurrency"],
        "target_concurrency": contract["target_concurrency"],
    }
    write_json(root / "runtime-state.json", runtime)
    traffic = read_json(root / "traffic-evidence.json")
    traffic.update({
        "requests": 200,
        "deadline_successes": 199,
        "fallback_requests": 0,
        "p95_end_to_end_ms": 112,
        "p99_queue_ms": 22,
        "replicas_converge_seconds": 49,
    })
    write_json(root / "traffic-evidence.json", traffic)


def assert_no_authority(root):
    assert not (root / "promotion-request.json").exists()
    assert not (root / "retraining-request.json").exists()


def assert_blocked(root, expected):
    report = read_json(root / "capacity-report.json")
    assert report["decision"] == "blocked"
    assert report["capacity_verified"] is False
    assert report["rollout_authorized"] is False
    assert report["promotion_authorized"] is False
    assert report["retraining_authorized"] is False
    assert expected in report["reasons"], (expected, report["reasons"])
    assert not (root / "capacity-ledger.json").exists()
    assert_no_authority(root)


def assert_accepted(root):
    report = read_json(root / "capacity-report.json")
    ledger = read_json(root / "capacity-ledger.json")
    assert report["decision"] == "accepted"
    assert report["capacity_verified"] is True
    assert report["rollout_authorized"] is False
    assert report["promotion_authorized"] is False
    assert report["retraining_authorized"] is False
    assert report["ready_replicas"] == 4
    assert report["deadline_success_rate"] == 0.995
    assert report["fallback_rate"] == 0.0
    assert report["p95_end_to_end_ms"] == 112
    assert report["p99_queue_ms"] == 22
    assert report["replicas_converge_seconds"] == 49
    assert ledger["status"] == "durable"
    assert ledger["capacity_report_digest"] == "sha256:" + hashlib.sha256((root / "capacity-report.json").read_bytes()).hexdigest()
    assert ledger["runtime_state_digest"] == digest(root / "runtime-state.json")
    assert ledger["traffic_evidence_digest"] == digest(root / "traffic-evidence.json")
    assert_no_authority(root)


def mutate_json(path, callback):
    value = read_json(path)
    callback(value)
    write_json(path, value)


def case(name, mutate, expected, refresh=None):
    with tempfile.TemporaryDirectory(prefix="kh-serving-") as tmp:
        root = Path(tmp)
        current_to(root)
        make_healthy(root)
        mutate(root)
        if refresh:
            refresh(root)
        clean(root)
        result = execute(root)
        assert result.returncode == 0, f"{name}: {result.returncode}: {result.stdout}"
        assert_blocked(root, expected)


def main():
    protected_before = {name: sha(ROOT / name) for name in PROTECTED}
    clean(ROOT)

    result = execute(ROOT)
    assert result.returncode == 0, result.stdout
    report = read_json(ROOT / "capacity-report.json")
    expected = {
        "min_replicas_mismatch",
        "container_concurrency_mismatch",
        "target_concurrency_mismatch",
        "deadline_success_below_minimum",
        "fallback_rate_above_maximum",
        "p95_latency_above_maximum",
        "queue_p99_above_maximum",
        "replica_convergence_too_slow",
    }
    assert expected.issubset(set(report["reasons"])), report["reasons"]
    assert_blocked(ROOT, "container_concurrency_mismatch")
    assert {name: sha(ROOT / name) for name in PROTECTED} == protected_before
    print("PASS canonical green-control-plane / unsafe-capacity incident is blocked")

    with tempfile.TemporaryDirectory(prefix="kh-serving-healthy-") as tmp:
        root = Path(tmp)
        current_to(root)
        make_healthy(root)
        result = execute(root)
        assert result.returncode == 0, result.stdout
        assert_accepted(root)
        first = {name: (root / name).read_bytes() for name in ("capacity-report.json", "capacity-ledger.json")}
        result2 = execute(root)
        assert result2.returncode == 0, result2.stdout
        assert_accepted(root)
        assert {name: (root / name).read_bytes() for name in first} == first
        print("PASS exact capacity configuration + exercised SLO evidence is byte-idempotent")

    case("runtime release", lambda r: mutate_json(r / "runtime-state.json", lambda x: x.__setitem__("release_subject", "MLOPS-PAY-RISK-PROD-foreign")), "runtime_release_subject_mismatch")
    case("controller", lambda r: mutate_json(r / "runtime-state.json", lambda x: x.__setitem__("autoscaler_controller", "hpa")), "autoscaler_controller_mismatch")
    case("deployment mode", lambda r: mutate_json(r / "runtime-state.json", lambda x: x.__setitem__("deployment_mode", "Standard")), "runtime_deployment_mode_mismatch")
    case("not ready", lambda r: mutate_json(r / "runtime-state.json", lambda x: x.__setitem__("control_plane_ready", False)), "control_plane_not_ready")
    case("scale zero", lambda r: mutate_json(r / "runtime-state.json", lambda x: x["resolved_scaling"].__setitem__("min_replicas", 0)), "min_replicas_mismatch")
    case("unsafe concurrency", lambda r: mutate_json(r / "runtime-state.json", lambda x: x["resolved_scaling"].__setitem__("container_concurrency", 16)), "container_concurrency_mismatch")
    case("wrong target", lambda r: mutate_json(r / "runtime-state.json", lambda x: x["resolved_scaling"].__setitem__("target_concurrency", 8)), "target_concurrency_mismatch")

    def mixed_model(root):
        runtime = read_json(root / "runtime-state.json")
        runtime["replicas"][2]["loaded_model_digest"] = "sha256:" + "0" * 64
        write_json(root / "runtime-state.json", runtime)
    case("mixed loaded model", mixed_model, "loaded_model_digest_mismatch:fraud-00042-c")

    def unexercised(root):
        runtime = read_json(root / "runtime-state.json")
        runtime["replicas"][1]["exercised"] = False
        write_json(root / "runtime-state.json", runtime)
    case("unexercised replica", unexercised, "replica_not_exercised:fraud-00042-b")

    def replica_not_ready(root):
        runtime = read_json(root / "runtime-state.json")
        runtime["replicas"][3]["ready"] = False
        runtime["observed_ready_replicas"] = 3
        write_json(root / "runtime-state.json", runtime)
    case("replica not ready", replica_not_ready, "replica_not_ready:fraud-00042-d")

    def duplicate_replica(root):
        runtime = read_json(root / "runtime-state.json")
        runtime["replicas"][3]["replica_id"] = runtime["replicas"][2]["replica_id"]
        write_json(root / "runtime-state.json", runtime)
    case("duplicate replica", duplicate_replica, "duplicate_replica_id:fraud-00042-c")

    case("traffic subject", lambda r: mutate_json(r / "traffic-evidence.json", lambda x: x.__setitem__("capacity_subject_id", "foreign")), "traffic_subject_mismatch")
    case("traffic release", lambda r: mutate_json(r / "traffic-evidence.json", lambda x: x.__setitem__("release_subject", "foreign")), "traffic_release_mismatch")
    case("population", lambda r: mutate_json(r / "traffic-evidence.json", lambda x: x.__setitem__("requests", 20)), "insufficient_traffic_population")
    case("deadline", lambda r: mutate_json(r / "traffic-evidence.json", lambda x: x.__setitem__("deadline_successes", 180)), "deadline_success_below_minimum")
    case("fallback", lambda r: mutate_json(r / "traffic-evidence.json", lambda x: x.__setitem__("fallback_requests", 3)), "fallback_rate_above_maximum")
    case("latency", lambda r: mutate_json(r / "traffic-evidence.json", lambda x: x.__setitem__("p95_end_to_end_ms", 121)), "p95_latency_above_maximum")
    case("queue", lambda r: mutate_json(r / "traffic-evidence.json", lambda x: x.__setitem__("p99_queue_ms", 26)), "queue_p99_above_maximum")
    case("convergence", lambda r: mutate_json(r / "traffic-evidence.json", lambda x: x.__setitem__("replicas_converge_seconds", 61)), "replica_convergence_too_slow")

    def tamper_release(root):
        release = read_json(root / "release-manifest.json")
        release["runtime_generation"] = "kserve-sklearn-v0.18"
        write_json(root / "release-manifest.json", release)
    case("release bytes", tamper_release, "release_manifest_digest_mismatch")

    def tamper_benchmark(root):
        evidence = read_json(root / "capacity-evidence.json")
        evidence["tested_container_concurrency"] = 16
        write_json(root / "capacity-evidence.json", evidence)
    case("benchmark bytes", tamper_benchmark, "capacity_evidence_digest_mismatch")

    def weak_benchmark(root):
        evidence = read_json(root / "capacity-evidence.json")
        evidence["steady"]["p95_end_to_end_ms"] = 150
        write_json(root / "capacity-evidence.json", evidence)
    case("weak benchmark", weak_benchmark, "benchmark_warm_p95_above_maximum", refresh=refresh_capacity_digest)

    with tempfile.TemporaryDirectory(prefix="kh-serving-conflict-") as tmp:
        root = Path(tmp)
        current_to(root)
        make_healthy(root)
        (root / "capacity-ledger.json").write_text('{"foreign":"state"}\n')
        before = (root / "capacity-ledger.json").read_bytes()
        result = execute(root)
        assert result.returncode != 0
        assert "conflicting_existing_state:capacity-ledger.json" in result.stdout
        assert (root / "capacity-ledger.json").read_bytes() == before
        print("PASS conflicting durable capacity state is preserved")

    assert {name: sha(ROOT / name) for name in PROTECTED} == protected_before
    clean(ROOT)
    print("VALIDATION PASSED")


if __name__ == "__main__":
    main()
