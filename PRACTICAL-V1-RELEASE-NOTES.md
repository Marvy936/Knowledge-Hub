# Knowledge Hub Practical v1 — release candidate notes

> **Status: `v1.0.0` release candidate — not tagged; explicit user acceptance pending.**

Practical v1 is the first integrated, evidence-driven local execution profile of Knowledge Hub.

## Included in v1

### Machine Learning Fundamentals

Deterministic Python 3.12 flagship with dataset/schema/leakage validation, candidate comparison, validation-only selection, test gate, integrity-bound packaging, strict inference and cleanup.

### MLOps and ML Platforms

Bounded local lifecycle:

```text
training lineage
→ MLflow Tracking + database-backed Registry
→ artifact/checksum read-back
→ immutable release/deployment subject
→ containerized live HTTP inference
→ deterministic canary + rollback
→ monitoring/no-data/drift states
→ exact approval-gated controlled retraining
→ new Registry version
→ post-retraining deployment/canary handoff
```

### Knowledge Hub RAG

Exact Git-bound deterministic documentation RAG with corpus/chunk/index identities, explicit `no_result`, bounded context, exact chunk citations, structured answered/abstained envelopes, hard evaluation, direct injection gate, retrieved-context/indirect injection gate, prompt/config provenance, trace counters and cleanup.

### Keycloak-secured AI API

Disposable local realm/JWKS trust, service-account Client Credentials, strict issuer/audience/token-use/scope/azp/client-role validation and protected promoted-RAG/bounded-agent routes with positive and negative authorization paths. Actual interactive browser Authorization Code exchange is explicitly not claimed by the automated v1 evidence.

### Bounded operations agent

Typed inspection, deterministic plan/action digest, separate finite approval, kill switch, durable operation state, one-mutation budget, bounded wait/unknown outcome, read-before-retry, idempotent recovery, strict typed result validation, retrieved-content authority boundary and deterministic hard evaluation.

### Unified release surface

Clean-checkout core orchestrator, repository integrity validator, permanent runtime workflows, canonical RC lifecycle and final dependency/provenance/artifact evidence manifest.

## Verified pre-release evidence

Combined baseline `789b5038b81b9342b1aef57b809bd3b67202ebde` passed RC run `31542501323` and release-evidence run `31542501346`. RAG indirect-injection runtime closeout passed run `31636019897` on `8c861edac728e5d19e7dd6035e4b438b8e8f8c2a`. Standalone Keycloak run `31542501300` is successful after rerun.

The **final** release SHA will be the current `main` after this source closeout, but only after that exact SHA passes the canonical RC + release-evidence lifecycle. The resulting run IDs are retained in GitHub Actions artifact provenance rather than committed afterward.

## Supported v1 profile

```text
Windows 11 + WSL2 or Linux
Python 3.12
CPU-only deterministic core
Docker/Compose for required local runtime gates
no paid cloud requirement
no mandatory external model API key
```

## Not claimed by v1

- production cloud/Kubernetes/HA/DR,
- production remote OCI/MLflow durability,
- production datasets or business A/B outcome,
- GPU/distributed training,
- semantic/vector or external generative-provider quality,
- production Keycloak TLS/HA/federation/WebAuthn/Operator lifecycle,
- actual automated browser Authorization Code exchange,
- production credentials/autonomous remediation/distributed exactly-once side effects,
- production SLO or business readiness.

## Release gate

`v1.0.0` may be created only when:

1. exact final `main` passes RC and release-evidence workflows,
2. final evidence artifact is read back and matches the same SHA,
3. repository branch state remains only `main`,
4. no temporary closeout mechanisms remain,
5. user explicitly accepts the Practical v1 scope,
6. tag is created on the already validated SHA without another source commit.
