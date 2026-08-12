# Knowledge Hub Practical v1 Roadmap

> **Stav: technical source closeout complete — final exact-head evidence + user acceptance pending**

Practical v1 je prvý prepojený, reprodukovateľný local profile Knowledge Hubu. Neznamená implementáciu každého budúceho labu ani production platform readiness.

## Podporovaný execution profile

```text
Windows 11 + WSL2 alebo Linux
→ Python 3.12
→ CPU-only deterministic core
→ Docker/Compose tam, kde je súčasťou runtime gate-u
→ bez plateného cloudu
→ bez povinného externého LLM API key
→ disposable runtime state mimo Git history
```

## Required v1 tracks

- [x] Machine Learning deterministic flagship lifecycle.
- [x] MLOps lineage → MLflow Tracking/Registry → immutable deployment → live container inference → canary/rollback → monitoring/drift → approval-gated retraining → post-retraining handoff.
- [x] Knowledge Hub RAG exact corpus → deterministic chunk/index/retrieval → exact citations → structured answer/abstention → hard eval → direct prompt-injection gate → retrieved-context/indirect prompt-injection gate → cleanup.
- [x] Keycloak local realm/JWKS/service-account identity boundary, exact audience/scope/role/azp validation a secured RAG/agent routes.
- [x] Bounded agent durable state, typed tools, separate finite approval, kill switch, idempotency/read-before-retry, unknown-outcome handling, strict result schema a deterministic hard evaluation.
- [x] Unified core orchestrator, repository integrity validator, permanent CI matrix, RC driver a final release-evidence finalizer.
- [x] GitHub Actions dispatch blocker #151 resolved.
- [x] Temporary/one-shot runtime diagnostic workflows removed.
- [x] Historical superseded PR #134 closed without merge.
- [x] Remote branch hygiene: only `main` remains.

## Evidence milestones

Combined technical baseline `789b5038b81b9342b1aef57b809bd3b67202ebde`:

- RC run `31542501323` — success,
- final release-evidence run `31542501346` — success,
- cleanup/worktree and artifact manifest verified,
- no tag and no user-acceptance claim created by workflow.

RAG indirect-injection closeout:

- SHA `8c861edac728e5d19e7dd6035e4b438b8e8f8c2a`,
- run `31636019897` — success,
- artifact `9157100163`,
- `evidence_id=b1db832a962fc2e4886dd59b13607b41a7a4cf276a19867098fd0232699c5116`,
- synthetic untrusted retrieved document classified unsafe and excluded from citations.

Standalone Keycloak hygiene run `31542501300` also succeeds on rerun attempt 2; the original red attempt failed during checkout, before the identity runtime gate executed.

## Hard final release gates

- [ ] Exact current `main` after this metadata closeout passes `Practical v1 release candidate`.
- [ ] The same exact SHA passes `Practical v1 release evidence` and produces readable canonical artifact/provenance/cleanup evidence.
- [ ] No source commit is made after that successful exact-head evidence run.
- [ ] User explicitly accepts the Practical v1 scope (`User accepted`).
- [ ] Immutable `v1.0.0` tag is created on the same validated SHA.

The final run ID is intentionally not committed after execution: committing a record of a future run would create a new Git subject and invalidate exact-SHA release evidence. GitHub Actions artifact provenance is therefore authoritative for the final tag subject.

## Explicit proof boundaries / post-v1

Practical v1 does **not** claim:

- production Kubernetes/cloud deployment, HA, autoscaling or DR,
- remote OCI Registry durability as a production service,
- production MLflow multi-user authorization,
- GPU/distributed training or production datasets/business A/B proof,
- semantic/vector-provider quality or external generative LLM factuality,
- production Keycloak TLS/HA/federation/WebAuthn/Operator lifecycle,
- automated real-browser Authorization Code exchange (PKCE configuration/authority contract exists; browser exchange remains unclaimed),
- production remediation credentials, distributed locks or exactly-once remote side effects,
- production SLO/business outcome readiness.

Those are post-v1 extensions, not hidden blockers of the bounded local Practical v1 profile.
