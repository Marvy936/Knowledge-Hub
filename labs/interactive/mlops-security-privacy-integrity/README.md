# MLOps Security and Privacy Integrity

An internal fraud analyst can reach the production prediction endpoint and detailed explanation/debug output. The account cannot read the training table directly, but it can issue thousands of adaptive queries, receive high-precision scores and explanations, while monitoring stores raw feature detail and the retraining feedback snapshot accepts records without complete producer provenance.

The incident is grounded in `MLOPS-PAY-96` and the authoritative `privacy-security-adversarial-ml.md` chapter. Repair `security_gate.py` so “internal endpoint” and encrypted storage cannot substitute for bounded attacker capability, privacy-safe outputs/telemetry and authenticated feedback integrity.

The repaired gate must bind exact security-subject and release bytes; enforce least-privilege actor/operation access, actor+operation query budgets and abuse detection; limit externally visible score precision, explanations, confidence, model metadata and error detail; require minimized/redacted bounded-retention telemetry with protected trace pointers; admit feedback only from authenticated signed provenance-complete producers while quarantining unknown/duplicate/conflicting records; validate adversarial/privacy tests against production-realistic attacker assumptions; and reproduce containment with revoked prior credentials, inaccessible compromised generations, minimized telemetry and a clean feedback snapshot.

Security verification is evidence only. It cannot itself authorize rollout, promotion or retraining. Accepted evidence must replay byte-identically, tampered authority/test assumptions must be rejected, and conflicting durable state must never be overwritten.

Use `lab-help`, `status`, `hint`, `secure`, `check`, `assess`, `reset` and `self-test`. This is a shell-only evidence lab; it needs no privileged runtime or live endpoint.
