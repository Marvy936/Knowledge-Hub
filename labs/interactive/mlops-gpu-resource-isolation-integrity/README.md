# MLOps GPU Resource Isolation Integrity

An online payment-risk service is `Running`, the scheduler successfully allocated GPU capacity and the dashboard reports 94% average GPU utilization. The platform therefore looks busy and healthy. It is not authoritative capacity evidence.

The workload was moved from the supported isolated `a100-online-v3` MIG class to a time-sliced A100 profile. Time-slicing keeps the scheduler green but does not provide the memory or fault isolation of the required `2g.20gb` MIG instance. A neighboring batch workload now drives memory pressure, queue age and tail latency while aggregate utilization remains high.

Your task is to repair `gpu_gate.py` so scheduler allocation and utilization remain diagnostic signals rather than capacity authority.

## Incident

The exact GPU capacity subject is `MLOPS-PAY-GPU-CAP-2026-08-r42` for release `MLOPS-PAY-RISK-PROD-2026-08-r42`.

The approved resource class is:

```text
resource class:      a100-online-v3
physical GPU:        A100-80GB
node pool:           gpu-online-a100-gen17
sharing mode:        MIG
MIG profile:         2g.20gb
extended resource:   nvidia.com/mig-2g.20gb
memory isolation:    hardware
fault isolation:     hardware-instance
workload class:      online-inference
profile memory:      20 GiB
max model memory:    14 GiB
latency SLO:         120 ms
```

Production instead reports `a100-shared-v5`, `time-slicing`, `shared-8x`, `nvidia.com/gpu` and no memory/fault isolation. Both replicas are `Ready`, initialize the accelerator, allocate the expected model and even pass a GPU smoke test. That still does not make the substituted sharing generation equivalent to the approved resource class.

In the exercised primary window:

```text
requests:                500
deadline successes:      456
p95 latency:             228 ms
p99 queue age:            97 ms
useful throughput:      62.4 rps
GPU memory high-water:  18.7 GiB
average GPU utilization: 94%
```

The required second operation also schedules successfully, but reproduces the wrong shared class and degrades to 241 ms p95 with 221/250 requests inside deadline.

## What must be true

The repaired gate must:

- bind the exact immutable release-manifest bytes and exact resource-class bytes;
- bind the GPU capacity subject and release subject across runtime and capacity evidence;
- verify node-pool generation, physical GPU model, driver/runtime generation, device-plugin generation and MIG strategy;
- require the exact sharing mode/profile, extended resource, workload class and memory/fault isolation policy;
- treat scheduler allocation and `Pod Running` only as lifecycle evidence;
- verify every ready replica has a unique identity, initializes the accelerator, allocates the model, passes the GPU smoke test and loads the exact release/model/image/features/policy/runtime generation;
- require complete ready-replica evidence rather than cluster-wide allocatable counts;
- recompute deadline-success rates from raw counts;
- enforce request-level p95 latency, queue age, useful throughput and GPU memory headroom;
- treat average GPU utilization as informational rather than an acceptance threshold;
- require a second-operation test that reproduces the same resource class and acceptable performance without manual node cleanup;
- write durable GPU-capacity evidence only after all layers agree;
- make exact replay byte-idempotent and reject conflicting durable state rather than overwrite it;
- preserve `rollout_authorized=false`, `promotion_authorized=false` and `retraining_authorized=false` even when GPU capacity is verified.

A healthy repair can prove `capacity_verified=true`. It does not by itself authorize rollout, model promotion or retraining.

## Files

- `gpu-contract.json` — exact GPU capacity subject and acceptance thresholds.
- `release-manifest.json` — immutable serving release identity.
- `resource-class.json` — exact supported accelerator/resource/isolation generation.
- `runtime-state.json` — scheduler/runtime/replica evidence from production.
- `capacity-evidence.json` — request outcomes, memory evidence, utilization and second-operation evidence.
- `gpu_gate.py` — intentionally unsafe learner implementation.
- `gpu_validator.py` — acceptance and mutation suite.

Generated state:

- `gpu-capacity-report.json`
- `gpu-capacity-ledger.json`

## Commands

```bash
help
status
check
hint
assess
reset
self-test
```

`assess` runs your current gate. `check` runs the full acceptance suite.

The lab is shell-only. It models the GPU scheduling/capacity evidence boundary from immutable fixtures; it does not require a physical GPU, Kubernetes cluster or `--privileged`.
