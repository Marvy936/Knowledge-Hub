# Knowledge Hub Practical v1 evidence

> **Release evidence status: In progress**

Tento dokument je súhrnný evidence ledger pre Practical v1. Nezamieňa `Implemented` s `Runtime verified`: každá oblasť môže prejsť na verified iba vtedy, keď existuje exact execution subject, zaznamenaný run alebo ekvivalentný immutable evidence record, resolved dependencies, positive/forbidden/recovery proof a cleanup boundary zodpovedajúca danému gate-u.

## Evidence model

```text
source revision
→ resolved runtime/dependencies
→ exact executable subject
→ positive + forbidden + recovery checks
→ output/read-back identities
→ cleanup read-back
→ proof boundary
```

Chýbajúci run, status, telemetry alebo artifact sa neinterpretuje ako success.

## Current flagship evidence state

| Oblasť | Runtime state | Authoritative evidence | Otvorená hranica |
|---|---|---|---|
| Machine Learning Fundamentals | Verified v deklarovanom syntetickom profile | [`labs/machine-learning/RUNTIME-EVIDENCE.md`](labs/machine-learning/RUNTIME-EVIDENCE.md) | Nie production dataset/business A/B outcome |
| MLOps | Pending | [`labs/mlops/RUNTIME-EVIDENCE.md`](labs/mlops/RUNTIME-EVIDENCE.md) | Central workflow run, live provider/container lifecycle a cleanup evidence |
| Knowledge Hub LLM/RAG | Pending | [`labs/llm-rag/RUNTIME-EVIDENCE.md`](labs/llm-rag/RUNTIME-EVIDENCE.md) | Clean-checkout corpus→retrieval→eval/security→cleanup run |
| Keycloak-secured AI API | Pending | [`labs/keycloak-ai-api/README.md`](labs/keycloak-ai-api/README.md) | Live realm/token/JWKS/protected-route positive a negative run |
| Bounded incident/operations agent | Pending | [`labs/agent-ops/RUNTIME-EVIDENCE.md`](labs/agent-ops/RUNTIME-EVIDENCE.md) | Clean-checkout combined RAG→plan→approval→execution/recovery hard-eval run |
| Practical v1 offline/core orchestrator | Pending | `scripts/practical_v1_core.py` | Exact CI/local run a recorded evidence ID |
| Permanent Practical v1 core CI matrix | Pending | `.github/workflows/practical-v1-core.yml` | GitHub Actions dispatch/run; issue #151 |

## Existing verified Machine Learning subject

Authoritative ML runtime evidence už existuje a nie je odvodené iba zo source test inventory.

Recorded subject podľa ML evidence dokumentu:

```text
workflow:        Knowledge documentation
workflow run:    1998
GitHub run ID:   31037119011
job ID:          92411983199
runner:          self-hosted MARVY
Python:          3.12.13
feature revision: 6b325080307c594ff74c1ca97273e6bb15431967
PR merge subject: 0e434e9cfa68173f3e3b76a61b93d08201474c81
inventory closeout: 07cfe2a883b901b40e7e0d266a00ff9a3fd12d4f
```

Dataset a packaged-model identities:

```text
dataset SHA-256: 08e795494731fa4c22f566769549240bf05413a918e34f9b0323091aa79cc3d6
model SHA-256:   34de60e4a5254a98b262abead6ccbca9b09a0c5c549328f37e88c6f21b7b19e9
```

Plný dependency resolution, metrics, leakage refusal, strict inference a cleanup proof zostáva v dedicated ML evidence dokumente; tento súhrn ho nekopíruje ako nový dôkaz.

## Practical v1 core runner evidence contract

`script/practical_v1_core.py` nevytvára nový ML/RAG/agent algoritmus. Orchestruje existujúce authoritative contracts v exact poradí:

```text
compileall
→ repository-integrity validator
→ Machine Learning tests
→ MLOps tests
→ LLM/RAG tests
→ bounded-agent tests
→ Keycloak AI API tests
→ deterministic agent hard evaluation
→ disposable workroot cleanup
```

Poznámka: authoritative path je `scripts/practical_v1_core.py`; názov `script/` vyššie je iba opis komponentu, nie filesystem path.

Successful core evidence musí obsahovať:

- lowercase 40-character Git `subject_sha`,
- clean tracked worktree preflight,
- Python version,
- presne 8 stages v exact poradí,
- per-stage command, return code a duration,
- SHA-256 stdout/stderr a bounded log tails,
- hard-eval `report_id`, case count a passed count,
- `cleanup_verified=true`,
- canonical `evidence_id`.

`all_passed=true` je dovolené iba ak sa vykoná celý expected stage set. Partial alebo zero-stage run nemôže byť success.

Evidence file musí byť mimo disposable workrootu. Workroot sa po rune odstráni; evidence sa ponechá iba na read-back a následne sa tiež odstráni alebo uloží do explicitného CI evidence surface-u.

## Permanent CI source contract

`.github/workflows/practical-v1-core.yml` definuje tri nezávislé vrstvy:

1. standalone matrix pre `machine-learning`, `mlops`, `llm-rag`, `agent-ops`, `keycloak-ai-api`,
2. combined RAG/agent/Keycloak integration + agent hard eval,
3. all-five-package offline/core orchestrator + release-tooling self-tests.

Workflow používa SHA-pinned `actions/checkout` a `actions/setup-python`, exact PR-head/push SHA, `persist-credentials:false` a repository-level `contents: read` permission. Source existence workflowu nie je runtime evidence.

## Central Actions blocker

Issue #151 zostáva otvorený. Corrected PR #179 head aj jeho merge commit nevytvorili connector-readable workflow run alebo commit status. Preto:

```text
workflow YAML exists
≠ workflow was dispatched

source tests exist
≠ central runtime verified
```

Kým repository Actions control plane nezačne vytvárať runs, MLOps, RAG, Keycloak, agent a nový core runner zostávajú `Runtime verified = Pending` bez ohľadu na completeness source implementácie.

## Required future closeout records

### MLOps

Evidence musí viazať training lineage, Tracking/Registry metadata, artifact bytes, exact registered version, immutable deployment subject, serving/container identity, canary/rollback, monitoring/drift, approval-gated retraining, recovery a cleanup. Zelený unit-test job bez provider/runtime read-backu nestačí.

### LLM/RAG

Evidence musí preukázať exact Git corpus snapshot, deterministic chunks/index, answered aj no-result retrieval, exact citations, structured output, hard eval slices, direct/indirect injection refusal, trace identity a cleanup.

### Keycloak-secured API

Evidence musí preukázať live imported realm, Authorization Code + PKCE contract alebo browser-flow proof boundary, service-account Client Credentials token, JWKS signature validation, issuer/audience/scope/azp/client-role claims, protected RAG/agent positive requesty a negative token/authorization variants.

### Bounded agent

Evidence musí preukázať durable plan/operation state, typed inspection/result, retrieval-context binding, exact approval expiry/action digest, kill switch, idempotent read-before-retry, unknown-outcome refusal, replay bez duplicate mutation a hard-eval business outcome.

## User acceptance boundary

Dokumentačný stav sekcií 18–21 je `Ready for user review`. Practical v1 runtime merge, zelený CI alebo tento evidence ledger automaticky nemenia sekciu na `User accepted`.

Finálny `v1.0.0` tag je dovolený až po repository-wide release-candidate rune, kontrole výsledného diffu, explicitnom proof-boundary review a splnení pravidla pre sekcie 18–21 z `PRACTICAL-V1-ROADMAP.md`.
