#!/usr/bin/env python3
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path.cwd()


def run(expect_success):
    proc = subprocess.run(["python3", "gpu_gate.py"], capture_output=True, text=True)
    if (proc.returncode == 0) != expect_success:
        raise AssertionError(f"unexpected gate result rc={proc.returncode}\n{proc.stdout}\n{proc.stderr}")
    return proc


run(False)
report = json.loads(Path("gpu-capacity-report.json").read_text())
assert report["accepted"] is False
assert report["rollout_authorized"] is False
assert not Path("gpu-capacity-ledger.json").exists()
print("PASS canonical time-slicing / interference incident is blocked")

runtime = json.loads(Path("runtime-state.json").read_text())
resource = json.loads(Path("resource-class.json").read_text())
for key in [
    "node_pool_generation",
    "physical_model",
    "driver_generation",
    "container_runtime_generation",
    "device_plugin_generation",
    "mig_strategy",
    "sharing",
    "extended_resource",
    "isolation",
]:
    runtime[key] = resource[key]
for replica in runtime["replicas"]:
    replica["resource_class_id"] = resource["resource_class_id"]
Path("runtime-state.json").write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n")

traffic = json.loads(Path("traffic-evidence.json").read_text())
traffic.update({
    "deadline_successes": 239,
    "useful_rps": 19.4,
    "p95_latency_ms": 112,
    "p99_queue_ms": 22,
    "memory_high_water_gib": 13.5,
    "fallback_rate": 0.001,
})
Path("traffic-evidence.json").write_text(json.dumps(traffic, indent=2, sort_keys=True) + "\n")

second = json.loads(Path("second-operation.json").read_text())
second.update({
    "allocation_reproducible": True,
    "same_profile_observed": True,
    "deadline_success_rate": 0.995,
    "p95_latency_ms": 114,
    "manual_node_cleanup_required": False,
})
Path("second-operation.json").write_text(json.dumps(second, indent=2, sort_keys=True) + "\n")

Path("gpu-capacity-report.json").unlink(missing_ok=True)
Path("gpu-capacity-ledger.json").unlink(missing_ok=True)
run(True)
first = Path("gpu-capacity-report.json").read_bytes() + Path("gpu-capacity-ledger.json").read_bytes()
run(True)
second_bytes = Path("gpu-capacity-report.json").read_bytes() + Path("gpu-capacity-ledger.json").read_bytes()
assert first == second_bytes
print("PASS exact MIG resource class + exercised capacity evidence is byte-idempotent")

Path("gpu-capacity-ledger.json").write_text('{"conflict":true}\n')
proc = subprocess.run(["python3", "gpu_gate.py"], capture_output=True, text=True)
assert proc.returncode != 0
assert Path("gpu-capacity-ledger.json").read_text() == '{"conflict":true}\n'
print("PASS conflicting durable GPU capacity state is preserved")

print("VALIDATION PASSED")
