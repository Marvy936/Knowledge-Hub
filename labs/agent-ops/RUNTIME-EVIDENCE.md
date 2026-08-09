# Bounded incident/operations agent runtime evidence

Status: `Pending`

Source implementation exists for typed local inspection, deterministic planning, exact action-digest approval, policy-bound kill switch, single-writer durable execution, idempotent read-before-retry and explicit unknown-outcome handling. No exact clean-checkout runtime run is recorded yet.

## Required Practical v1 closeout evidence

A future exact-revision runtime gate must prove at least:

1. install `labs/agent-ops` in a fresh supported Python environment;
2. initialize one credential-free local sandbox with a degraded allowlisted service;
3. create incident context and obtain the actual service generation/status through the typed `inspect_service` adapter;
4. derive one canonical `restart_service` action plan and action digest;
5. create a separate exact human approval for that plan/action digest;
6. create a policy-bound disengaged kill switch;
7. execute exactly one restart and read back service generation, health and restart count;
8. repeat the same operation and prove no duplicate mutation occurs;
9. change service generation after approval and prove the stale action is refused;
10. engage the kill switch and prove a new mutation or retry-after-`not_found` cannot run;
11. prove read-only reconciliation of an already completed mutation remains possible while the kill switch is engaged;
12. inject an `unknown` lookup outcome and prove automatic retry is forbidden;
13. inject a failure before mutation, obtain `not_found`, provide the exact recovery state ID and prove exactly one later mutation succeeds;
14. corrupt a completed result and prove replay refuses it;
15. remove `.runtime/agent-ops` with the bounded cleanup driver and read back non-existence.

## Integration evidence still required after local core closeout

Practical v1 also needs the Keycloak-secured automation boundary to prove that:

- `agent.run` can produce only a bounded plan/read-only result for an authorized automation identity;
- `agent.remediate` requires a separate exact approval artifact/action digest in addition to the Keycloak role;
- browser/user tokens cannot invoke automation-only agent routes;
- no production credentials or unrestricted shell/network tool is present;
- process restart/replay preserves idempotency and unknown-outcome semantics.

Until these evidence points are recorded for an exact revision, the agent track remains `Implemented`, not `Runtime verified`.
