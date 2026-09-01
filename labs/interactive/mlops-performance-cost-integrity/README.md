# MLOps Performance and Cost Integrity

A payment-risk serving team declares an optimization successful because every request still returns HTTP 200 and the dashboard reports a lower average cost per response. The exact production-style replay says otherwise: scale-to-zero and aggressive batching create cold-start and queue tail latency, 1,200 of 6,000 eligible requests fall back before model success, and the cost report excludes idle GPU cost while dividing by all HTTP responses.

The incident is grounded in `MLOPS-PAY-95` and the authoritative `performance-latency-throughput-cost-monitoring.md` chapter. Repair `performance_gate.py` so raw QPS, average latency, HTTP availability and cost per response cannot substitute for useful model work.

The repaired gate must bind exact release bytes, resolved serving/resource generation, traffic population, warm and cold latency, queue age, result-class denominators, useful throughput and time-compatible cost allocation. Idle cost must be explicit, cost must be recomputed per deadline-successful model prediction, and a second complete window must reproduce the same immutable traffic/runtime/cost subject without a prewarmed cache, manual idle reallocation or changed traffic mix.

A healthy evidence set may verify performance and cost evidence, but it does not authorize an optimization, rollout, promotion or retraining. Accepted evidence must replay byte-identically, authority-contract tampering must be rejected, and conflicting durable state must never be overwritten.

Use `lab-help`, `status`, `hint`, `check`, `assess`, `reset` and `self-test`. This is a shell-only evidence lab; it needs no privileged mode or live serving stack.
