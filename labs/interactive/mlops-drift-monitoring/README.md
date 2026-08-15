# MLOps Drift Monitoring and Population Correctness

This challenge models a production drift alert that looks actionable but is built from the wrong population and the wrong time boundary.

The current release has an elevated serving fallback rate. The starter monitor filters the current window to successful model invocations, uses processing/ingest time as if it were event time, calls the resulting score shift `concept drift`, and writes an automatic retraining request. That turns a serving incident into a model-change decision without the evidence needed to justify it.

Work on `/workspace/drift_monitor.py`. The reference window, current incident evidence, and drift contract are authoritative inputs for this exercise.

Your repaired monitor must:

- bind its result to the exact `payment-risk-drift-v3` contract bytes and exact stable-production reference digest;
- validate the reference release, current release, feature generation, and threshold-policy generation before computing a verdict;
- select the input-data population from all eligible requests by **event time**, not only successful model invocations and not processing/ingest time;
- require the current event-time window to be complete before issuing a drift verdict;
- report fallback separately from prediction drift instead of silently removing fallback requests from the incident population;
- compute data drift from the eligible population and prediction drift from successfully scored requests;
- treat prediction/data drift as hypothesis evidence, not proof of concept drift;
- report concept drift as not evaluable while mature labels are unavailable;
- never create a retraining side effect from this drift signal alone;
- recommend investigation of the earliest actionable divergence. In the supplied incident that is serving fallback, not model retraining.

Useful commands:

```bash
cat drift_contract.json
cat reference-window.json
cat current-window.json
analyze
check
hint
```

The intentionally broken starter may create `/workspace/retrain-request.json`; that file is evidence of the bug, not a desired output.

Key boundary:

```text
eligible requests + event-time completeness
              |
              v
      authoritative population
        |                 |
        v                 v
   input/data drift   scored prediction drift
        |                 |
        +------ evidence -+
                 |
        fallback / service health
                 |
                 v
          investigation first

mature labels absent  =>  concept drift is not evaluable
one drift signal      !=  automatic retraining authority
```

Lab commands: `analyze`, `status`, `check`, `hint`, `reset`.
