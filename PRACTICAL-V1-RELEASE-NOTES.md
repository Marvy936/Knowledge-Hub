# Knowledge Hub Practical v1 — release candidate notes

> **Status: Release candidate draft — not released**
>
> Tento dokument pripravuje release notes pre budúci tag `v1.0.0`. Neoznačuje Practical v1 za hotovú, nevytvára release subject a nemení žiadny `Runtime verified` alebo `User accepted` stav. Finálny exact release commit, workflow runs a tag sa doplnia až po splnení acceptance gates v [`PRACTICAL-V1-ROADMAP.md`](PRACTICAL-V1-ROADMAP.md).

## Čo Practical v1 predstavuje

Practical v1 je prvý prepojený praktický profil Knowledge Hubu, v ktorom má používateľ vedieť z čistého checkoutu prejsť bounded lifecycle od dát a modelu cez MLOps, Knowledge Hub RAG, identitu a agentickú automatizáciu až po failure, recovery a cleanup.

Podporovaný core profil je:

```text
Windows 11 + WSL2 alebo Linux
→ Python 3.12
→ CPU-only deterministic core path
→ Docker/Compose iba tam, kde je súčasťou konkrétneho runtime gate-u
→ bez plateného cloudu
→ bez povinného externého model API key
→ disposable runtime state mimo Git history
```

Dependency bootstrap môže potrebovať package index alebo lokálny cache. Samotný deterministic core lifecycle po inštalácii dependencies nepotrebuje komerčný LLM provider ani cloud account.

## Source surface pripravený pre v1

### Machine Learning Fundamentals

Executable flagship pokrýva deterministic dataset, schema a leakage validation, train/validation/test lifecycle, model comparison, validation-only threshold selection, test gate, artifact packaging, strict inference a cleanup.

Machine Learning má už samostatný historický runtime-verified subject. Exact run, dependency resolution, dataset/model SHA-256, negative leakage path a cleanup sú zaznamenané v [`labs/machine-learning/RUNTIME-EVIDENCE.md`](labs/machine-learning/RUNTIME-EVIDENCE.md).

Tento dôkaz je bounded na deklarovaný syntetický Python 3.12 profil. Nie je to production dataset alebo business A/B evidence.

### MLOps and ML Platforms

Source lifecycle zahŕňa:

```text
ML training lineage
→ candidate + immutable release identity
→ compare-before-promote
→ MLflow Tracking Server
→ database-backed Registry
→ artifact checksum/read-back
→ exact numeric model version
→ immutable deployment subject
→ identity-bound FastAPI serving
→ deterministic two-generation canary
→ rollback
→ monitoring/no-data/drift states
→ exact human retraining approval
→ durable controlled retraining
→ post-retraining deployment/canary handoff
```

Authority boundaries oddeľujú mutable alias od immutable deployment identity, no-data od healthy state, retraining proposal od approval authority a Registry unknown outcome od bezpečného retry.

Runtime status MLOps zostáva `Pending`. Authoritative future acceptance boundary je v [`labs/mlops/RUNTIME-EVIDENCE.md`](labs/mlops/RUNTIME-EVIDENCE.md).

### LLM and GenAI Engineering — Knowledge Hub RAG

Offline deterministic source lifecycle zahŕňa:

```text
exact Git documentation corpus
→ byte-bound snapshot
→ deterministic Markdown chunking
→ deterministic lexical index
→ retrieval / explicit no_result
→ bounded context
→ exact chunk citations
→ structured answered/abstained output
→ hard-slice evaluation
→ direct + retrieved-context injection gates
→ prompt/config release provenance
→ trace + token-equivalent counters
→ cleanup
```

Core path zámerne nevyžaduje externý LLM API key. Deterministic extractive adapter je reference CI adapter; generative/semantic provider je samostatná post-v1 alebo optional vrstva.

Runtime status RAG zostáva `Pending`. Exact acceptance boundary je v [`labs/llm-rag/RUNTIME-EVIDENCE.md`](labs/llm-rag/RUNTIME-EVIDENCE.md).

### Keycloak-secured AI API

Source identity path obsahuje:

```text
local Keycloak realm contract
→ public Authorization Code + PKCE S256 client
→ confidential service account / Client Credentials
→ RS256 + configured issuer/JWKS trust
→ exact audience + token_use + scope + azp + client-role validation
→ protected promoted-RAG route
→ protected bounded-agent routes
```

JWT role nie je mutation authority. `agent.remediate` navyše vyžaduje exact external approval artifact, policy generation, kill-switch read-back a durable bounded-agent operation contract.

Secrets a bearer tokens nesmú byť committed ani logované. Runtime status zostáva `Pending`; live realm import, token issuance, JWKS signature validation, protected requests, negative authorization matrix a cleanup musia byť ešte zaznamenané podľa [`labs/keycloak-ai-api/RUNTIME-EVIDENCE.md`](labs/keycloak-ai-api/RUNTIME-EVIDENCE.md).

### AI Agents and Intelligent Automation

Bounded incident/operations agent source lifecycle obsahuje:

```text
incident context
→ typed read-only inspection
→ optional promoted retrieval context
→ canonical diagnostic
→ deterministic bounded plan
→ exact action digest
→ separate finite human approval
→ policy-bound kill switch
→ durable operation state
→ bounded tool wait
→ one typed mutation or refusal/unknown_outcome
→ authoritative read-before-retry
→ result read-back
→ replay / hard evaluation
```

Retrieved text je read-only evidence. `retrieval_context_id` môže meniť plan identity, ale nevstupuje do mutation `action_digest`; retrieved text preto nevie rozšíriť tool/target/argument authority. `unknown_outcome + not_found` nie je licencia na automatic retry.

Hard evaluation pokrýva trajectory, tool selection, policy compliance, completion a business/operational outcome. Runtime status zostáva `Pending`; exact combined evidence boundary je v [`labs/agent-ops/RUNTIME-EVIDENCE.md`](labs/agent-ops/RUNTIME-EVIDENCE.md).

## Unified Practical v1 product surface

Repository obsahuje source-level unified release surface:

- [`labs/README.md`](labs/README.md) — authoritative practical index,
- [`PRACTICAL-STATUS.md`](PRACTICAL-STATUS.md) — oddelené `Documented`, `Implemented`, `Runtime verified`, `User accepted`,
- [`PRACTICAL-V1-ROADMAP.md`](PRACTICAL-V1-ROADMAP.md) — 49 hard Practical v1 gates,
- [`PRACTICAL-V1-EVIDENCE.md`](PRACTICAL-V1-EVIDENCE.md) — cross-flagship evidence ledger,
- `scripts/validate_practical_v1_repo.py` — repository integrity gate,
- `scripts/practical_v1_core.py` — exact eight-stage offline/core orchestrator,
- `.github/workflows/practical-v1-core.yml` — permanent standalone/combined/orchestrator CI matrix,
- root [`README.md`](README.md) — clean-checkout Practical v1 quick start.

Offline/core orchestrator je fail-closed. Successful report vyžaduje presne všetkých osem stages, exact Git subject, clean tracked preflight, successful contract suites, deterministic agent hard eval, `cleanup_verified=true` a `worktree_verified=true`. Partial alebo zero-stage execution nemôže vytvoriť `all_passed=true`.

## Release evidence stav

Aktuálna release hranica je zámerne asymetrická:

| Oblasť | Source state | Runtime state |
|---|---|---|
| Machine Learning | Implemented | Verified v deklarovanom syntetickom profile |
| MLOps | Implemented pre aktuálny Practical v1 source lifecycle | Pending |
| Knowledge Hub RAG | Implemented pre deterministic offline Practical v1 lifecycle | Pending |
| Keycloak-secured AI API | Implemented na source úrovni | Pending |
| Bounded operations agent | Implemented na source úrovni | Pending |
| Unified offline/core orchestrator | Implemented na source úrovni | Pending |
| Permanent Practical v1 core CI | Implemented na source úrovni | Pending |

`Implemented` sa nesmie prezentovať ako executed evidence. Presný authoritative stav určuje [`PRACTICAL-STATUS.md`](PRACTICAL-STATUS.md).

## Aktuálny release blocker

Issue #151 je stále release blocker pre central runtime closeout.

Po tom, čo `.github/workflows/practical-v1-core.yml` už existoval na `main`, ďalšie PR aj push eventy na explicitne matchujúcich paths stále nevytvorili connector-readable workflow run ani commit status. Tým sa blocker oddelil od MLOps-specific path filtrov aj od vysvetlenia „workflow ešte nie je na default branch“.

Core workflow už podporuje aj `workflow_dispatch`, aby po oprave Actions control plane bolo možné spustiť exact default-branch gate bez ďalšieho diagnostického source commitu.

Kým existuje chýbajúci run:

```text
workflow source exists
≠ workflow dispatched

source tests exist
≠ central runtime verified

merge succeeded
≠ Practical v1 accepted
```

## Čo ešte musí prejsť pred `v1.0.0`

Tag sa nesmie vytvoriť, kým nie sú súčasne splnené aspoň tieto release gates:

1. GitHub Actions control plane je obnovený a issue #151 má executable resolution evidence.
2. Permanent Practical v1 core CI prejde na exact release-candidate SHA.
3. Offline/core orchestrator vytvorí successful exact-SHA evidence s `cleanup_verified=true` a `worktree_verified=true`.
4. MLOps dostane authoritative runtime closeout podľa svojho `RUNTIME-EVIDENCE.md`.
5. RAG dostane clean-checkout corpus→retrieval→eval/security→cleanup runtime evidence.
6. Keycloak dostane live realm/token/JWKS/protected-route positive aj negative authorization evidence.
7. Agent dostane combined retrieval→plan→approval→execution/recovery hard-eval evidence bez duplicate mutation.
8. Repository-wide links, JSON schemas/data, flagship imports a prohibited runtime-artifact gate prejdú na exact RC.
9. Výsledný release diff neobsahuje secrets, databases, model bytes ani disposable runtime state.
10. Sekcie 18–21 zostanú pravdivo označené `Ready for user review`, pokiaľ používateľ explicitne nepotvrdí `User accepted`.
11. [`PRACTICAL-V1-EVIDENCE.md`](PRACTICAL-V1-EVIDENCE.md) sa doplní o exact RC SHA, run/job IDs, dependency resolutions a proof boundaries.
12. Až potom sa vytvorí immutable Git tag `v1.0.0`.

## Dôležité source milestones

Practical v1 source vznikala po bounded vrstvách. Medzi hlavné authoritative PR subjects patria:

- #140 — deterministic MLOps promotion foundation,
- #145 / #150 — MLflow Registry a training-lineage integration,
- #155 / #157 / #158 — immutable serving, FastAPI source a live loopback canary/rollback contracts,
- #160 / #162 / #164 — monitoring/drift approval, controlled retraining a post-retraining handoff,
- #167 / #169 / #171 — RAG corpus/chunking, retrieval/citations a eval/security/observability,
- #173 / #174 — Keycloak identity foundation a promoted-RAG route,
- #175 / #177 / #178 / #179 — bounded agent foundation, Keycloak route integration, approval/resource bounds a retrieval-injection/hard-eval closeout,
- #181 — unified Practical v1 release surface,
- #182 — Keycloak runtime-evidence contract,
- #183 — manual core workflow dispatch source,
- #184 — MLOps/RAG/agent evidence-contract alignment.

Tieto PR subjects dokazujú source history. Nie sú náhradou za chýbajúce runtime evidence.

## Mimo Practical v1 release boundary

Prvý release zámerne nevyžaduje:

- production Kubernetes/cloud deployment,
- Kubeflow/KServe/SageMaker,
- GPU/distributed training,
- commercial LLM provider,
- LDAP/AD federation, WebAuthn, Keycloak HA alebo Operator,
- production TLS/reverse-proxy/HA/DR pre local Keycloak profile,
- multi-agent autonomous loops,
- broad cloud credentials alebo production remediation authority,
- production SLO/business A/B outcome.

Tieto oblasti zostávajú post-v1 rozšírenia a nesmú blokovať bounded local Practical v1, pokiaľ sa nezmení authoritative roadmap.

## Final release record — zatiaľ nevyplnené

Nasledujúce polia sa vyplnia iba pri skutočnom release closeoute:

```text
release candidate SHA:  PENDING
core workflow run ID:   PENDING
core evidence ID:       PENDING
MLOps evidence:         PENDING
RAG evidence:           PENDING
Keycloak evidence:      PENDING
Agent evidence:         PENDING
final acceptance:       PENDING
tag:                    PENDING
```

Kým je čo i len jeden z týchto povinných subjects `PENDING`, tento dokument zostáva release-candidate draft a tag `v1.0.0` sa nevytvára.
