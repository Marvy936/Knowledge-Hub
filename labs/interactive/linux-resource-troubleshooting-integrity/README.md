# Linux Resource Troubleshooting Integrity

A slow service is not diagnosed by choosing the largest number in `top`. The starter incident sees high host CPU and very low `MemFree`, then jumps directly to host exhaustion and removes the workload limit. That conclusion ignores the exact affected cohort, cgroup CPU quota, runnable pressure, CPU PSI and the fact that memory remains reclaimable and below its effective cgroup thresholds.

Repair `resource_gate.py` so diagnosis is bound to the exact user-visible symptom and to the host -> cgroup -> process scope that can actually explain it.

The repaired gate must bind the operation, incident window and cohort; distinguish host utilization from workload saturation; prove cgroup CPU quota throttling with matching runnable/PSI evidence; reject low free memory as a root cause when `MemAvailable`, cgroup usage, memory PSI, major faults and OOM evidence are healthy; accept only the bounded quota repair; prove p99/error-rate/throughput recovery; reject adjacent broad mutations such as disabling resource limits; and prove an identical second assessment is mutation-free and byte-reproducible.

Direct practical coverage:

- `cpu-and-memory-fundamentals.md`
- `performance-and-troubleshooting.md`

Commands: `lab-help`, `status`, `hint`, `assess`, `check`, `reset`, `self-test`.
