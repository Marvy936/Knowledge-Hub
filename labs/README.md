# Knowledge Hub practical labs

This is the authoritative index of the practical layer. `Implemented`, `Runtime verified` and `User accepted` remain separate states; see [`../PRACTICAL-STATUS.md`](../PRACTICAL-STATUS.md).

## Practical v1 executable flagships

| Track | Runtime state | Boundary |
|---|---|---|
| [Machine Learning](machine-learning/README.md) | Runtime verified | Deterministic synthetic Python 3.12 lifecycle; not production data/business proof. |
| [MLOps](mlops/README.md) | Runtime verified for bounded local v1 profile | Local MLflow/Registry, container inference, canary/rollback, monitoring/drift, controlled retraining and post-retraining handoff; not production platform durability. |
| [Knowledge Hub RAG](llm-rag/README.md) | Runtime verified | Exact Git corpus, deterministic retrieval/citations, eval/security, direct + retrieved-context injection runtime gates and cleanup; no semantic/external LLM quality claim. |
| [Keycloak-secured AI API](keycloak-ai-api/README.md) | Runtime verified for automated local service-account/JWKS/protected-API profile | Actual interactive browser Authorization Code exchange remains explicitly unclaimed. |
| [Bounded operations agent](agent-ops/README.md) | Runtime verified for combined local profile | Approval/idempotency/recovery/hard-eval semantics; no production credentials or distributed exactly-once claim. |

## Unified Practical v1 surface

- core orchestrator: `../scripts/practical_v1_core.py`,
- repository integrity validator: `../scripts/validate_practical_v1_repo.py`,
- permanent core CI: `../.github/workflows/practical-v1-core.yml`,
- release candidate: `../.github/workflows/practical-v1-release-candidate.yml`,
- final release evidence: `../.github/workflows/practical-v1-release-evidence.yml`,
- roadmap: [`../PRACTICAL-V1-ROADMAP.md`](../PRACTICAL-V1-ROADMAP.md),
- evidence ledger: [`../PRACTICAL-V1-EVIDENCE.md`](../PRACTICAL-V1-EVIDENCE.md).

Practical v1.0.0 is released at tag `v1.0.0`. Post-v1.0 development continues on `main`.

## Interactive Labs

- Index: [`interactive/README.md`](interactive/README.md)
- Host contract: Docker only; no clone, Git, Compose, Python or lab-specific CLI is required on the learner host.
- Public one-command runtime: `ghcr.io/marvy936/knowledge-hub-lab-docker-network-debug:latest`.
- The authoritative current lab set is the registry in `interactive/runtime/labs.tsv`; coverage spans Docker, Git, IaC/configuration management, Kubernetes, identity, databases, messaging, observability, reverse proxy/TLS and S3-compatible object storage.
- Interactive Labs are post-v1.0 development and do not alter the immutable `v1.0.0` release subject.

## Manual environment labs

### CKA timed labs

- Index: [`cka/README.md`](cka/README.md)
- Requires an external/disposable Kubernetes cluster.
- Central execution is not a hard blocker for the bounded local Practical v1 release.

### AWS CloudOps labs

- Index: [`aws-cloudops/README.md`](aws-cloudops/README.md)
- Requires an explicit sandbox account/Region, cost controls and cleanup/read-back.
- Cloud execution is not a hard blocker for the bounded local Practical v1 release.

## Common execution contract

Every executable flagship must preserve exact subject identity, reproducible setup, positive + refusal paths, recovery/rollback where applicable, explicit no-data/unknown-outcome semantics, cleanup/read-back and a proof boundary that does not exceed the executed run.
