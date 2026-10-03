# Foundations Flow, Feedback and DORA

A faster local build step does not prove a faster or safer software delivery system. The starter incident models a checkout service whose build time falls from roughly fourteen minutes to six minutes while the same two-day approval queue dominates the end-to-end value stream. A dashboard is green and claims excellent DORA numbers, so the starter gate incorrectly declares success.

Repair `flow_gate.py` so the verdict is derived from the exact change lifecycle rather than a local dashboard metric.

The repaired gate must preserve the same service/change population across baseline and improvement windows; validate one traceable SDLC identity chain from request through source, immutable artifact, release/runtime and production verification; recompute process time, waiting time and DORA delivery/reliability metrics from raw events; use systems thinking to identify the dominant approval queue instead of optimizing the already-small build step; require a bounded improvement hypothesis against that bottleneck; close the feedback loop through owner, decision, corrective action and re-observation; record the learning in standard work; and recompute the identical evidence contract on the second operation without manual metric overrides.

This lab provides direct practical coverage for:

- `sdlc.md`
- `devops.md`
- `devops-lifecycle.md`
- `systems-thinking.md`
- `feedback-loops.md`
- `three-ways.md`
- `continuous-improvement.md`
- `value-stream-mapping.md`
- `dora-metrics.md`

Dashboard status remains evidence only and does not grant rollout or promotion authority.

Commands: `lab-help`, `status`, `hint`, `analyze`, `check`, `assess`, `reset`, `self-test`.
