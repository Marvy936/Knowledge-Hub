# Foundations Feedback and System Dynamics

A green component is not proof of a healthy system. The starter incident scales the checkout API because its local dashboard is visible and the API becomes green, while the downstream payment worker remains the actual constraint. Retries amplify load, the queue stock grows and the end-to-end checkout outcome gets worse.

Repair `system_gate.py` so acceptance uses an explicit end-to-end boundary and a closed feedback loop rather than local component status.

The repaired gate must pin the exact system contract; include client, API, worker, database and business outcome in the same flow; identify the payment worker as the constrained capacity boundary; preserve the queue-stock increase created by the local optimization; recognize timeout → retry → downstream-load → timeout as a reinforcing loop; use complete production trace/queue observation; compare against explicit global targets; route the decision to an owner with end-to-end authority; apply bounded retries, exponential backoff and load shedding instead of more API scale; account for propagation delay; verify recovery on the same global boundary; keep optimization authority false; and prove an identical second analysis is no-op and byte-reproducible.

Direct practical coverage:

- `systems-thinking.md`
- `feedback-loops.md`

Together with `foundations-delivery-flow-dora`, this also strengthens the existing partial coverage of `three-ways.md`: First-Way flow and Second-Way feedback are exercised, while Third-Way institutional learning remains planned.

Commands: `lab-help`, `status`, `hint`, `analyze`, `check`, `assess`, `reset`, `self-test`.
