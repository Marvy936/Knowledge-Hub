# Foundations Reconciliation and Idempotency

A green script exit code does not prove that an automation produced one correct effective state. The starter incident models an environment provisioning workflow whose first create call returned an unknown outcome. The workflow blindly retries the imperative create, leaves two resources with the same environment identity, one resource uses a mutable artifact reference, and the final smoke check happens to be green.

Repair `automation_gate.py` so automation success is bound to an exact request subject and authoritative state rather than the last command result.

The repaired gate must validate the typed request; use one stable operation/resource identity; switch from blind imperative create semantics to desired-state reconciliation; read the authoritative inventory before retrying an unknown mutation outcome; preserve and reconcile partial state instead of creating a duplicate; require a digest-pinned immutable artifact; read back the effective runtime and smoke outcome; reject conflicting manual state instead of silently overwriting it; and prove an identical second operation is a no-op while repeating effective verification.

This lab provides direct practical coverage for:

- `automation-mindset.md`
- `declarative-vs-imperative.md`
- `idempotency.md`
- `desired-state-and-reconciliation.md`

It provides partial coverage for `immutable-vs-mutable-infrastructure.md`; a later replacement-lifecycle lab will cover the full immutable rollout boundary.

Commands: `lab-help`, `status`, `hint`, `reconcile`, `check`, `assess`, `reset`, `self-test`.
