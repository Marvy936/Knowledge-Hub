# MLOps GPU Resource Isolation Integrity

A production payment-risk service moved from its validated MIG resource class to GPU time-slicing to improve reported utilization. Kubernetes still schedules the pods and the dashboard still shows healthy average GPU utilization, but the runtime no longer has the hardware memory/fault isolation that the serving capacity evidence was measured against.

The incident is based on `MLOPS-PAY-94`: a neighboring batch workload introduces memory pressure and tail-latency interference. The learner must repair `gpu_gate.py` so scheduler success and utilization cannot substitute for exact GPU resource-class identity and exercised request outcomes.

The repaired gate must bind the exact release manifest and resource-class bytes; require the expected node-pool, physical GPU, driver/runtime/device-plugin generations, extended resource, MIG strategy/profile and hardware isolation; verify each ready replica completed GPU smoke and loaded the exact release; enforce memory headroom, useful throughput, deadline success, queue age and tail latency from an exercised window; require a second-operation test proving the same profile remains allocatable and performant; reject time-sliced evidence even when utilization is high; make successful evidence replay byte-idempotent; reject conflicting durable state; and preserve `rollout_authorized=false`, `promotion_authorized=false` and `retraining_authorized=false`.

Commands: `help`, `status`, `check`, `hint`, `assess`, `reset`, `self-test`.

This is a shell-only evidence-contract lab. It models GPU scheduling/runtime/telemetry evidence with immutable fixtures; it does not require a physical GPU or privileged Docker.
