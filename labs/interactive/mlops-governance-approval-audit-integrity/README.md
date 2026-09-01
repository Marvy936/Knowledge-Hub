# MLOps Governance Approval Audit Integrity

A high-impact fraud-serving candidate is marked approved because offline metrics and CI are green. The decision is not authoritative: the business owner never approved the new review-capacity policy, privacy review covers the previous telemetry generation, and a deployment operator enabled an emergency override across all governance gates without expiry. The runtime then exceeds the approved canary traffic condition and lacks the required human-review capacity.

The incident is grounded in `MLOPS-PAY-95` and the authoritative `governance-approvals-audit.md` chapter. Repair `governance_gate.py` so a generic approved ticket or emergency bypass cannot substitute for an exact, independently approved, reconstructable governance decision.

The repaired gate must bind immutable governance-contract, release-manifest and evidence-bundle bytes; require the risk-based approval roles for the exact model/policy/telemetry changes; enforce separation of duties for protected approvals; require business approval of the exact capacity policy and privacy approval of the exact telemetry scope; bound any emergency override by actor, reason, narrow scope, expiry and post-review; verify runtime conformity to the approved composite and conditions; validate an append-only SHA-256 audit chain with actor/role/operation/subject/evidence/state transitions; and reproduce the same no-op approval from the same immutable evidence without an expired override or missing approver.

A valid governance decision is evidence about decision rights, not the deployment operation itself. The lab therefore keeps `deployment_authorized=false`, `promotion_authorized=false` and `retraining_authorized=false`. Accepted evidence must replay byte-identically, tampered authority/audit state must be rejected, and conflicting durable evidence must never be overwritten.

Use `lab-help`, `status`, `hint`, `review`, `check`, `assess`, `reset` and `self-test`. This is a shell-only evidence lab; it needs no privileged runtime or live policy engine.
