#!/usr/bin/env python3
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROTECTED = {
    "release-manifest.json": "d58e118edd096feb557dd03b3741ff8cacf278a882406d8ca35770b65a10c6db",
    "resource-class.json": "fcd707a984c6faeeb03af07500a952cb2fa50ae682283a19c7f9ca54acc532e9",
    "gpu-contract.json": "693edf5c6639d9b2b5c08baecb800bd2953296ef92eaa0087e798b5988e0d72e",
    "runtime-state.json": "02d5dc9580b5ddf786ca9dd68b26ad84007508b0144c859601517a005da0cf81",
    "capacity-evidence.json": "ff08238702233fcc3af6a48480377d3392dced4c66093a2cd3947df799a7c60e",
}
EVIDENCE = list(PROTECTED)

def die(message):
    print(f"VALIDATION FAILED: {message}", file=sys.stderr)
    sys.exit(1)

def load(path):
    return json.loads(path.read_text())

def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

for name, expected in PROTECTED.items():
    path = ROOT / name
    if not path.exists():
        die(f"protected evidence missing: {name}")
    if sha256(path) != expected:
        die(f"protected evidence changed: {name}")

gate = ROOT / "gpu_gate.py"
if not gate.exists():
    die("gpu_gate.py is missing")

base = {name: load(ROOT / name) for name in EVIDENCE}

def healthy_evidence():
    data = copy.deepcopy(base)
    release = data["release-manifest.json"]
    resource = data["resource-class.json"]
    runtime = data["runtime-state.json"]
    capacity = data["capacity-evidence.json"]

    runtime["observed_resource_class_id"] = resource["resource_class_id"]
    runtime["node_pool_generation"] = resource["node_pool_generation"]
    runtime["physical_model"] = resource["physical_model"]
    runtime["driver_generation"] = resource["driver_generation"]
    runtime["container_runtime_generation"] = resource["container_runtime_generation"]
    runtime["device_plugin_generation"] = resource["device_plugin_generation"]
    runtime["mig_strategy"] = resource["mig_strategy"]
    runtime["sharing"] = copy.deepcopy(resource["sharing"])
    runtime["extended_resource"] = resource["extended_resource"]
    runtime["isolation"] = copy.deepcopy(resource["isolation"])
    runtime["workload_class"] = resource["workload_class"]

    capacity["resource_class_id_observed"] = resource["resource_class_id"]
    capacity["neighbor_batch_active"] = True
    capacity["dashboard"]["average_gpu_utilization"] = 0.43
    capacity["primary_window"] = {
        "requests": 500,
        "deadline_successes": 498,
        "p95_latency_ms": 108,
        "p99_queue_age_ms": 22,
        "useful_throughput_rps": 92.5,
        "memory_high_water_gib": 13.4,
    }
    capacity["second_operation"] = {
        "attempt_id": "gpu-second-op-2026-08-22T08:03Z",
        "scheduled": True,
        "accelerator_initialized": True,
        "model_allocated": True,
        "resource_class_id_observed": resource["resource_class_id"],
        "requests": 250,
        "deadline_successes": 249,
        "p95_latency_ms": 111,
        "useful_throughput_rps": 90.8,
        "memory_high_water_gib": 13.7,
    }
    return data

def make_case(data):
    td = tempfile.TemporaryDirectory(prefix="kh-gpu-validator-")
    d = Path(td.name)
    shutil.copy2(gate, d / "gpu_gate.py")
    os.chmod(d / "gpu_gate.py", 0o755)
    for name, obj in data.items():
        write_json(d / name, obj)
    return td, d

def execute(d):
    return subprocess.run(
        [sys.executable, str(d / "gpu_gate.py")],
        cwd=d,
        text=True,
        capture_output=True,
        timeout=15,
    )

def report(d):
    p = d / "gpu-capacity-report.json"
    return load(p) if p.exists() else None

def expect_block(data, label, reason_fragment=None):
    td, d = make_case(data)
    try:
        proc = execute(d)
        if proc.returncode == 0:
            die(f"{label}: invalid evidence was accepted")
        rep = report(d)
        if rep is None:
            die(f"{label}: blocked case did not create a deterministic report")
        if rep.get("result") != "blocked" or rep.get("capacity_verified") is not False:
            die(f"{label}: blocked report has unsafe verdict")
        if (d / "gpu-capacity-ledger.json").exists():
            die(f"{label}: blocked case created durable capacity ledger")
        if rep.get("rollout_authorized") is not False:
            die(f"{label}: blocked report granted rollout authority")
        if rep.get("promotion_authorized") is not False:
            die(f"{label}: blocked report granted promotion authority")
        if rep.get("retraining_authorized") is not False:
            die(f"{label}: blocked report granted retraining authority")
        if reason_fragment:
            reasons = " | ".join(rep.get("reasons") or [])
            if reason_fragment not in reasons:
                die(f"{label}: expected reason fragment not found: {reason_fragment}")
    finally:
        td.cleanup()

# Canonical incident must be blocked despite scheduler success, Running Pods and 94% utilization.
expect_block(base, "canonical time-slicing incident", "sharing mode/profile")
print("PASS canonical scheduler-green / time-slicing interference incident is blocked")

healthy = healthy_evidence()
td, d = make_case(healthy)
try:
    first = execute(d)
    if first.returncode != 0:
        die(f"healthy exact MIG evidence was rejected: {first.stderr or first.stdout}")
    rep = report(d)
    led = d / "gpu-capacity-ledger.json"
    if rep is None or not led.exists():
        die("healthy case did not create report + durable ledger")
    if rep.get("result") != "accepted" or rep.get("capacity_verified") is not True:
        die("healthy report did not verify capacity")
    if rep.get("exact_resource_class_verified") is not True:
        die("healthy report did not verify exact resource class")
    if rep.get("request_outcomes_verified") is not True:
        die("healthy report did not verify request outcomes")
    if rep.get("second_operation_verified") is not True:
        die("healthy report did not verify second operation")
    if rep.get("rollout_authorized") is not False or rep.get("promotion_authorized") is not False or rep.get("retraining_authorized") is not False:
        die("healthy capacity verification crossed an authority boundary")
    # Low aggregate utilization is intentionally healthy: utilization is diagnostic, not authority.
    if rep.get("observed_metrics", {}).get("dashboard_average_gpu_utilization") != 0.43:
        die("healthy report lost informational utilization evidence")
    before_report = (d / "gpu-capacity-report.json").read_bytes()
    before_ledger = led.read_bytes()
    second = execute(d)
    if second.returncode != 0:
        die("exact healthy replay failed")
    if (d / "gpu-capacity-report.json").read_bytes() != before_report or led.read_bytes() != before_ledger:
        die("exact healthy replay changed durable bytes")
finally:
    td.cleanup()
print("PASS exact MIG resource class + request outcomes + second operation are byte-idempotent")

def mutation(label, fn, reason=None):
    data = healthy_evidence()
    fn(data)
    expect_block(data, label, reason)

mutation("runtime subject mismatch",
         lambda d: d["runtime-state.json"].__setitem__("gpu_capacity_subject", "OTHER-SUBJECT"),
         "runtime evidence belongs to another GPU capacity subject")
mutation("capacity subject mismatch",
         lambda d: d["capacity-evidence.json"].__setitem__("gpu_capacity_subject", "OTHER-SUBJECT"),
         "capacity evidence belongs to another GPU capacity subject")
mutation("runtime release mismatch",
         lambda d: d["runtime-state.json"].__setitem__("release_subject", "OTHER-RELEASE"),
         "runtime evidence belongs to another release")
mutation("capacity release mismatch",
         lambda d: d["capacity-evidence.json"].__setitem__("release_subject", "OTHER-RELEASE"),
         "capacity evidence belongs to another release")
mutation("scheduler allocation missing",
         lambda d: d["runtime-state.json"].__setitem__("scheduler_allocated", False),
         "scheduler did not allocate")
mutation("Pod not Running",
         lambda d: d["runtime-state.json"].__setitem__("pod_running", False),
         "serving Pod is not Running")
mutation("runtime resource class mismatch",
         lambda d: d["runtime-state.json"].__setitem__("observed_resource_class_id", "a100-shared-v5"),
         "runtime resource class")
mutation("node-pool generation mismatch",
         lambda d: d["runtime-state.json"].__setitem__("node_pool_generation", "gpu-online-a100-old"),
         "node-pool generation")
mutation("GPU model mismatch",
         lambda d: d["runtime-state.json"].__setitem__("physical_model", "A10G-24GB"),
         "physical GPU model")
mutation("driver generation mismatch",
         lambda d: d["runtime-state.json"].__setitem__("driver_generation", "nvidia-driver-old"),
         "driver generation")
mutation("container runtime mismatch",
         lambda d: d["runtime-state.json"].__setitem__("container_runtime_generation", "runtime-old"),
         "container runtime generation")
mutation("device-plugin generation mismatch",
         lambda d: d["runtime-state.json"].__setitem__("device_plugin_generation", "plugin-timeslice"),
         "device-plugin generation")
mutation("MIG strategy mismatch",
         lambda d: d["runtime-state.json"].__setitem__("mig_strategy", "none"),
         "MIG strategy")
mutation("time-slicing substitution",
         lambda d: d["runtime-state.json"].__setitem__("sharing", {"mode":"time-slicing","profile":"shared-8x"}),
         "sharing mode/profile")
mutation("extended resource mismatch",
         lambda d: d["runtime-state.json"].__setitem__("extended_resource", "nvidia.com/gpu"),
         "extended resource name")
mutation("isolation mismatch",
         lambda d: d["runtime-state.json"].__setitem__("isolation", {"memory":"none","fault":"none"}),
         "memory/fault isolation")
mutation("workload class mismatch",
         lambda d: d["runtime-state.json"].__setitem__("workload_class", "batch-inference"),
         "workload class")
mutation("capacity evidence resource mismatch",
         lambda d: d["capacity-evidence.json"].__setitem__("resource_class_id_observed", "a100-shared-v5"),
         "capacity evidence was measured on another resource class")

def one_replica(d):
    d["runtime-state.json"]["replicas"] = d["runtime-state.json"]["replicas"][:1]
    d["runtime-state.json"]["ready_replicas"] = 1
mutation("insufficient ready replicas", one_replica, "not enough ready GPU replicas")

mutation("ready count reconciliation",
         lambda d: d["runtime-state.json"].__setitem__("ready_replicas", 3),
         "ready replica count does not reconcile")
mutation("duplicate replica identities",
         lambda d: d["runtime-state.json"]["replicas"][1].__setitem__("replica_id", d["runtime-state.json"]["replicas"][0]["replica_id"]),
         "replica identities are not unique")
mutation("replica not ready",
         lambda d: d["runtime-state.json"]["replicas"][0].__setitem__("ready", False),
         "is not ready")
mutation("replica smoke missing",
         lambda d: d["runtime-state.json"]["replicas"][0].__setitem__("gpu_smoke_passed", False),
         "did not pass the GPU smoke test")
mutation("accelerator init missing",
         lambda d: d["runtime-state.json"]["replicas"][0].__setitem__("accelerator_initialized", False),
         "did not initialize the accelerator")
mutation("model allocation missing",
         lambda d: d["runtime-state.json"]["replicas"][0].__setitem__("model_allocated", False),
         "did not allocate the model")
mutation("mixed loaded model",
         lambda d: d["runtime-state.json"]["replicas"][1].__setitem__("loaded_model_sha256", "sha256:" + "0"*64),
         "loaded another model")
mutation("mixed loaded image",
         lambda d: d["runtime-state.json"]["replicas"][1].__setitem__("loaded_image_sha256", "sha256:" + "1"*64),
         "loaded another serving image")
mutation("mixed feature contract",
         lambda d: d["runtime-state.json"]["replicas"][1].__setitem__("loaded_feature_contract", "other-features"),
         "loaded another feature contract")
mutation("mixed policy",
         lambda d: d["runtime-state.json"]["replicas"][1].__setitem__("loaded_policy_sha256", "sha256:" + "2"*64),
         "loaded another policy")
mutation("mixed runtime generation",
         lambda d: d["runtime-state.json"]["replicas"][1].__setitem__("loaded_runtime_generation", "other-runtime"),
         "loaded another runtime generation")

mutation("primary zero population",
         lambda d: d["capacity-evidence.json"]["primary_window"].update({"requests":0,"deadline_successes":0}),
         "primary request/deadline counts are invalid")
mutation("primary deadline regression",
         lambda d: d["capacity-evidence.json"]["primary_window"].__setitem__("deadline_successes", 480),
         "primary deadline-success rate is below threshold")
mutation("primary latency regression",
         lambda d: d["capacity-evidence.json"]["primary_window"].__setitem__("p95_latency_ms", 121),
         "primary p95 latency exceeds threshold")
mutation("primary queue regression",
         lambda d: d["capacity-evidence.json"]["primary_window"].__setitem__("p99_queue_age_ms", 31),
         "primary p99 queue age exceeds threshold")
mutation("primary throughput regression",
         lambda d: d["capacity-evidence.json"]["primary_window"].__setitem__("useful_throughput_rps", 79.9),
         "primary useful throughput is below threshold")
mutation("primary memory headroom regression",
         lambda d: d["capacity-evidence.json"]["primary_window"].__setitem__("memory_high_water_gib", 16.1),
         "primary GPU memory headroom is below threshold")

mutation("second operation unscheduled",
         lambda d: d["capacity-evidence.json"]["second_operation"].__setitem__("scheduled", False),
         "second operation was not scheduled")
mutation("second accelerator init missing",
         lambda d: d["capacity-evidence.json"]["second_operation"].__setitem__("accelerator_initialized", False),
         "second operation did not initialize")
mutation("second model allocation missing",
         lambda d: d["capacity-evidence.json"]["second_operation"].__setitem__("model_allocated", False),
         "second operation did not allocate")
mutation("second resource class mismatch",
         lambda d: d["capacity-evidence.json"]["second_operation"].__setitem__("resource_class_id_observed", "a100-shared-v5"),
         "second operation did not reproduce")
mutation("second zero population",
         lambda d: d["capacity-evidence.json"]["second_operation"].update({"requests":0,"deadline_successes":0}),
         "second-operation request/deadline counts are invalid")
mutation("second deadline regression",
         lambda d: d["capacity-evidence.json"]["second_operation"].__setitem__("deadline_successes", 240),
         "second-operation deadline-success rate is below threshold")
mutation("second latency regression",
         lambda d: d["capacity-evidence.json"]["second_operation"].__setitem__("p95_latency_ms", 121),
         "second-operation p95 latency exceeds threshold")
mutation("second throughput regression",
         lambda d: d["capacity-evidence.json"]["second_operation"].__setitem__("useful_throughput_rps", 79.9),
         "second-operation useful throughput is below threshold")
mutation("second memory headroom regression",
         lambda d: d["capacity-evidence.json"]["second_operation"].__setitem__("memory_high_water_gib", 16.1),
         "second-operation GPU memory headroom is below threshold")

# Tampering immutable pinned bytes without updating the protected contract must fail.
mutation("release manifest tamper",
         lambda d: d["release-manifest.json"]["model"].__setitem__("id", "tampered-model"),
         "release manifest digest does not match contract")
mutation("resource class tamper",
         lambda d: d["resource-class.json"].__setitem__("node_pool_generation", "tampered-pool"),
         "resource class digest does not match contract")

# Existing conflicting report must be preserved.
td, d = make_case(healthy_evidence())
try:
    conflict = b'{"conflict":"report"}\n'
    (d / "gpu-capacity-report.json").write_bytes(conflict)
    proc = execute(d)
    if proc.returncode == 0:
        die("conflicting report was overwritten")
    if (d / "gpu-capacity-report.json").read_bytes() != conflict:
        die("conflicting report bytes changed")
    if (d / "gpu-capacity-ledger.json").exists():
        die("conflicting report case created a ledger")
finally:
    td.cleanup()

# Existing conflicting ledger must be preserved.
td, d = make_case(healthy_evidence())
try:
    proc = execute(d)
    if proc.returncode != 0:
        die("could not establish healthy durable state for conflict test")
    conflict = b'{"conflict":"ledger"}\n'
    (d / "gpu-capacity-ledger.json").write_bytes(conflict)
    report_before = (d / "gpu-capacity-report.json").read_bytes()
    proc = execute(d)
    if proc.returncode == 0:
        die("conflicting durable ledger was overwritten")
    if (d / "gpu-capacity-ledger.json").read_bytes() != conflict:
        die("conflicting durable ledger bytes changed")
    if (d / "gpu-capacity-report.json").read_bytes() != report_before:
        die("conflicting ledger replay changed the report")
finally:
    td.cleanup()
print("PASS conflicting durable GPU capacity state is preserved")

for name, expected in PROTECTED.items():
    if sha256(ROOT / name) != expected:
        die(f"validator mutated protected evidence: {name}")

print("VALIDATION PASSED")
