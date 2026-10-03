# Foundations Delivery Flow and DORA

A fast CI dashboard does not prove fast or reliable software delivery. The starter incident counts CI jobs as deployments, ends lead time at pipeline completion, hides rollback/incident deployments from change-failure rate, measures restoration only until a service turns green, and optimizes the longest active-work stage even though most elapsed time is waiting in another queue.

Repair `flow_gate.py` so flow evidence is bound to the exact measurement window and authoritative production change events.

The repaired gate must recompute deployment frequency from actual production exposure; compute median lead time from source commit to production exposure; keep rollback and incident outcomes inside the production-deployment denominator for change failure rate; compute median time to restore from incident detection to business recovery; reconstruct active and waiting time across the value stream; identify the largest wait-time queue as the bottleneck; keep metrics as evidence rather than automatic optimization authority; and prove an identical second measurement is reproducible without mutating evidence.

Direct practical coverage:

- `dora-metrics.md`
- `value-stream-mapping.md`

Partial practical coverage:

- `sdlc.md`
- `devops-lifecycle.md`
- `three-ways.md`

Commands: `lab-help`, `status`, `hint`, `measure`, `check`, `assess`, `reset`, `self-test`.
