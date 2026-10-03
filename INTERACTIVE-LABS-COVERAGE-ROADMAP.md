# Interactive Labs Coverage Roadmap

## Goal

Every authoritative documentation topic must have explicit practical coverage. Coverage is complete only when a topic maps to at least one `labs/interactive` lab whose published runtime self-test passes.

Manual CKA/AWS exercises and Practical v1 tracks are supplemental evidence; they do not replace missing interactive coverage.

## Coverage states

- `covered` — one or more published interactive labs exercise the topic materially.
- `partial` — a lab touches the topic but does not exercise its main operational boundary.
- `planned` — no adequate interactive lab yet.
- `not-applicable` — reserved for a topic that cannot meaningfully be exercised; requires explicit rationale.

Section completion requires every topic in the section to be `covered`.

## Backfill order

1. Wave A — Foundations, Linux, Networking, Git/Automation (`00–03`)
2. Wave B — Testing, CI/CD, GitLab, IaC/Configuration Management, Docker (`04–08`)
3. Wave C — Kubernetes, Helm/CKA, AWS (`09–11`)
4. Wave D — Observability, Security/Identity, SRE, Databases/Distributed Systems (`12–15`)
5. Wave E — GitOps/Platform Engineering, Keycloak, ML Fundamentals (`16–18`)
6. Phase 8 — LLM/GenAI and Agents only after the `00–18` backfill gate is complete.

## Section inventory

| Section | Topics | Backfill direction |
|---|---:|---|
| 00 Foundations | 20 | delivery-flow/DORA, feedback/systems thinking, automation/idempotency/reconciliation, ownership/toil |
| 01 Linux and Systems | 19 | filesystem/storage, services/logging/timers, isolation, networking/SSH/security, resource troubleshooting |
| 02 Networking and Web | 17 | L2/L3 addressing/routing, transport/sockets, DNS/DHCP, NAT/firewall, HTTP/TLS/proxy/load-balancing, API/WebSocket troubleshooting |
| 03 Git and Automation | 15 | object/history model, remotes/branching, history surgery, conflict/rebase, Bash/Python/PowerShell/YAML automation |
| 04 Testing and Quality | 15 | pyramid/mocks, contract/E2E, static/coverage gates, performance/security/chaos, flaky/shift-left/right |
| 05 CI/CD and Release | 24 | pipeline primitives, cache/artifacts, promotion/approvals, reusable pipelines, versioning, deployment strategies, DB-safe rollback |
| 06 GitLab | 12 | permissions/MR/protection, CI syntax/runners, vars/secrets/cache/artifacts, registry/releases/scanning/troubleshooting |
| 07 IaC and Config Management | 23 | Terraform graph/state/backend/modules/lifecycle/testing; Ansible inventory/playbooks/templates/handlers/roles/vault/troubleshooting |
| 08 Docker | 19 | image/layer/build, registries, networking/storage, Compose/health, BuildKit, security, troubleshooting |
| 09 Kubernetes | 32 | core workload/service/config, storage/stateful, jobs/daemonsets, networking/DNS/ingress, scheduling/resources/HPA, RBAC/security, lifecycle/etcd/upgrades/troubleshooting |
| 10 Helm and CKA | 10 | templating/named templates, dependencies/hooks, upgrade/rollback, testing/troubleshooting, timed repair drills |
| 11 AWS | 30 | identity/networking, compute/LB, storage/DB, DNS/CDN, serverless/containers, observability/audit, secrets/backup/DR/FinOps |
| 12 Observability | 16 | telemetry model, Prometheus/Grafana/Alertmanager, logs, tracing/OTel, cardinality, RED/USE/golden signals |
| 13 Security and Identity | 19 | authn/authz/audit, federation protocols, least privilege/zero trust, secrets/encryption, SBOM/signing/supply chain, vulnerability/policy/threat model |
| 14 SRE and Operations | 15 | SLI/SLO/error budgets, incident/on-call/RCA/postmortem, capacity/readiness, backup/DR, chaos/runbooks/toil |
| 15 Databases and Distributed Systems | 18 | transactions/indexes/migrations/pools, backup/replication, cache, CAP/consistency/consensus, messaging/retries/backpressure, gateway/discovery/rate-limit |
| 16 GitOps and Platform Engineering | 17 | Git source/reconciliation, Argo/Flux, promotion/secrets, paved roads/self-service/catalog, tenancy/guardrails/troubleshooting |
| 17 Keycloak | 30 | realm/client/token fundamentals, OIDC/PKCE/M2M, flows/MFA, federation/brokering, authz, admin automation, proxy/TLS/observability, backup/upgrade/clustering/operator |
| 18 ML Fundamentals | 26 | data/splits/preprocessing/leakage, core algorithms, optimization, overfit/CV/HPO, metrics/imbalance/calibration, explainability/bias, reproducibility/outcome troubleshooting |

The exact per-document mapping lives in [INTERACTIVE-LABS-COVERAGE.md](INTERACTIVE-LABS-COVERAGE.md) and is updated atomically with each lab.
