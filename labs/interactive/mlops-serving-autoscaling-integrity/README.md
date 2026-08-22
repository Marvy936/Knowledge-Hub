# MLOps Serving Autoscaling Integrity

A payment-risk `InferenceService` is green and the autoscaler has already grown the serving fleet to four ready replicas. The dashboard therefore looks healthy. During the real morning burst, however, most of the business deadline is spent in the runtime queue and 35% of requests fall back.

The starter treats `Ready` plus a nonzero replica count as capacity proof and even grants rollout authority. Repair `serving_gate.py` so control-plane health, loaded release identity, pretested runtime capacity and exercised request outcomes remain separate evidence layers.

## Incident

The exact capacity subject is `MLOPS-PAY-SERVE-CAP-2026-08-r42` for production release `MLOPS-PAY-RISK-PROD-2026-08-r42`.

The release was load-tested on `nvidia-mig-2g20gb` with safe `containerConcurrency=2`. The production runtime instead resolves:

```text
minReplicas=0
maxReplicas=12
containerConcurrency=16
targetConcurrency=8
```

Four replicas are currently ready, exercised and loaded with the expected release. That does not repair the capacity contract. In the exact exercised burst window, only 130/200 requests meet deadline, 70/200 use fallback, p95 end-to-end latency is 780 ms, p99 queue time is 540 ms and replica convergence takes 78 seconds.

## What must be true

The repaired gate must:

- bind the exact immutable release-manifest bytes and load-test capacity-evidence bytes;
- prove that the benchmark belongs to the exact serving image, runtime generation and accelerator/resource profile;
- require the resolved deployment mode, autoscaler controller, min/max replicas, hard container concurrency and autoscaler target from the capacity contract;
- distinguish the hard per-replica admission limit from the autoscaler operating target;
- verify every observed replica is uniquely identified, ready, exercised and loaded with the exact release/model/image/feature/policy/runtime generation;
- bind the exact exercised traffic window and minimum population;
- recompute deadline-success and fallback rates from counts rather than trust dashboard health;
- enforce latency, queue and scale-convergence thresholds against the real exercised window;
- create durable capacity evidence only after all authority layers agree;
- make exact replay byte-idempotent and reject conflicting durable state instead of overwriting it;
- preserve `rollout_authorized=false`, `promotion_authorized=false` and `retraining_authorized=false` even when capacity is verified.

A healthy evidence set may prove `capacity_verified=true`. That is capacity evidence, not permission to increase traffic, promote a model or start retraining.

## Files

- `serving-contract.json` — exact serving/capacity authority contract.
- `release-manifest.json` — immutable production release identity.
- `capacity-evidence.json` — pre-production load-test evidence for the exact runtime/resource profile.
- `runtime-state.json` — resolved autoscaler configuration and loaded replica fingerprints.
- `traffic-evidence.json` — exercised production-window outcomes.
- `serving_gate.py` — intentionally unsafe learner implementation.
- `serving_validator.py` — acceptance suite.

Generated state:

- `capacity-report.json`
- `capacity-ledger.json`

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

`assess` runs your current gate. `check` runs the full acceptance suite. The lab is shell-only and models the serving evidence contract from immutable fixtures; it does not start a real KServe cluster and does not require `--privileged`.
