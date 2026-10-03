# MLOps Troubleshooting Integrity

A green status after a restart is not root-cause proof. In incident `MLOPS-PAY-98`, operators moved a Registry alias, restarted KServe Pods and reran a pipeline after p99 latency and false positives increased. Latency improved, but false positives remained, multiple serving generations were still present, the feature materialization generation was stale, one serving Runtime diverged, delayed-label feedback joins lost evidence, duplicate Model Packages appeared and part of the original evidence was lost.

Repair `troubleshooting_gate.py` so troubleshooting acceptance follows the exact incident subject rather than the latest green dashboard.

The repaired gate must pin exact contract bytes; freeze uncorrelated mutations; preserve source/control-plane/data-plane/feature/log/monitor/side-effect evidence before changes; record exact IDs and clock context; walk the intended → configured → resolved → loaded → exercised → outcome state ladder and identify the first divergence; test explicit competing hypotheses; require bounded containment; restore the complete known-good release including feature generation, runtime fingerprint, actual traffic and business quality; reconcile duplicate/unknown side effects; verify the corrective control; and prove a second identical operation with read-before-retry and no duplicate side effects.

Troubleshooting evidence never grants rollout, promotion or retraining authority. Healthy evidence is byte-idempotent and conflicting durable evidence is preserved.

Use `lab-help`, `status`, `hint`, `diagnose`, `check`, `assess`, `reset` and `self-test`. This lab is shell-only.
