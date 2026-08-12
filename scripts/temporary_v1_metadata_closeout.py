from __future__ import annotations

from pathlib import Path

BASELINE_SHA = "789b5038b81b9342b1aef57b809bd3b67202ebde"
BASELINE_RC_RUN = "31542501323"
BASELINE_RELEASE_RUN = "31542501346"
BASELINE_RC_ID = "2e0a0754332864ca5898852b921d76d88e78d0c8209ea3dccfab7a92c6fe0778"
BASELINE_RELEASE_EVIDENCE_ID = "1bced14424764a890f8c8fbd346c49992c5ba1d2c7963d9f3b65485547c37b47"
BASELINE_MANIFEST_ID = "52f6c2c886c14d746f3fdd7c35fc82a93e24372570acea50f6a90cad08c6eca2"
BASELINE_DEPENDENCY_ID = "e37285a9af7f2d53742fa8b29db91de07a6980ba1fad0c785dd60ed1c66a03dc"
BASELINE_PROVENANCE_ID = "80221bfce87ce37820738fe41d9392bc639f8fce216a9b7df1f7d812396471aa"
RAG_CLOSEOUT_SHA = "8c861edac728e5d19e7dd6035e4b438b8e8f8c2a"
RAG_CLOSEOUT_RUN = "31636019897"
RAG_CLOSEOUT_ARTIFACT = "9157100163"
RAG_CLOSEOUT_EVIDENCE = "b1db832a962fc2e4886dd59b13607b41a7a4cf276a19867098fd0232699c5116"
RAG_INDIRECT_CASE = "5ab930d70a11b9aec819860dc26bbd9048bb0310c4871eb57404bca43aed510d"
KEYCLOAK_RUN = "31542501300"


def write(path: str, content: str) -> None:
    Path(path).write_text(content.strip() + "\n", encoding="utf-8", newline="\n")


def replace_if_present(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    if old in text:
        file.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


write(
    "PRACTICAL-STATUS.md",
    f"""
# Practical implementation status

Tento ledger oddeľuje štyri nezávislé stavy praktického obsahu.

| Stav | Presný význam |
|---|---|
| `Documented` | Existuje authoritative vysvetlenie alebo praktický contract. |
| `Implemented` | Existuje vykonateľný package, manifest, script alebo úplný manual lab set. |
| `Runtime verified` | Exact revision prešla zaznamenaným runtime gate-om v deklarovanom prostredí. |
| `User accepted` | Používateľ výslovne prijal praktický rozsah alebo výsledok. |

`Runtime verified` nie je production readiness a automaticky neznamená `User accepted`.

## Practical v1 current state

| Oblasť | Documented | Implemented | Runtime verified | User accepted | Authoritative boundary |
|---|---|---|---|---|---|
| Machine Learning flagship | Áno | Áno | Áno — deterministic Python 3.12 synthetic lifecycle | Nie | [`labs/machine-learning/RUNTIME-EVIDENCE.md`](labs/machine-learning/RUNTIME-EVIDENCE.md) |
| MLOps Practical v1 lifecycle | Áno | Áno | Áno — bounded local MLflow/Registry, containerized inference, canary/rollback, drift/retraining a post-retraining handoff | Nie | [`labs/mlops/RUNTIME-EVIDENCE.md`](labs/mlops/RUNTIME-EVIDENCE.md) |
| Knowledge Hub RAG | Áno | Áno | Áno — clean-checkout deterministic corpus→retrieval→eval/security→cleanup; direct aj retrieved-context injection gate | Nie | [`labs/llm-rag/RUNTIME-EVIDENCE.md`](labs/llm-rag/RUNTIME-EVIDENCE.md) |
| Keycloak-secured AI API | Áno | Áno | Áno pre automated local service-account/JWKS/protected-API profile; browser Authorization Code exchange sa neclaimuje | Nie | [`labs/keycloak-ai-api/RUNTIME-EVIDENCE.md`](labs/keycloak-ai-api/RUNTIME-EVIDENCE.md) |
| Bounded operations agent | Áno | Áno | Áno — deterministic combined local retrieval/plan/approval/execution/recovery hard-eval profile | Nie | [`labs/agent-ops/RUNTIME-EVIDENCE.md`](labs/agent-ops/RUNTIME-EVIDENCE.md) |
| Unified Practical v1 release lifecycle | Áno | Áno | Baseline verified; finálny tag subject musí ešte prejsť exact-head RC + release-evidence runom po tomto source closeoute | Nie | [`PRACTICAL-V1-EVIDENCE.md`](PRACTICAL-V1-EVIDENCE.md) |
| CKA timed labs | Áno | Áno — manual lab set | Nie centrálne; externý/disposable cluster | Nie | [`labs/cka/README.md`](labs/cka/README.md) |
| AWS CloudOps labs | Áno | Áno — manual lab set | Nie centrálne; sandbox account a cost controls | Nie | [`labs/aws-cloudops/README.md`](labs/aws-cloudops/README.md) |

## Verified technical baseline

Canonical combined baseline na `{BASELINE_SHA}`:

- release-candidate run `{BASELINE_RC_RUN}` — success,
- release-evidence run `{BASELINE_RELEASE_RUN}` — success,
- `release_candidate_id={BASELINE_RC_ID}`,
- `release_evidence_id={BASELINE_RELEASE_EVIDENCE_ID}`,
- `artifact_manifest_id={BASELINE_MANIFEST_ID}`,
- `workflow_cleanup_verified=true`,
- `release_tag_created=false`,
- `user_acceptance_claimed=false`.

RAG security closeout bol následne sprísnený a overený na `{RAG_CLOSEOUT_SHA}` runom `{RAG_CLOSEOUT_RUN}`; retrieved-context/indirect injection je teraz explicitný runtime case.

## Release boundary

Technická baseline je overená. Pred immutable `v1.0.0` zostávajú presne tri release kroky:

1. exact aktuálny `main` po metadata closeoute musí prejsť canonical RC + release-evidence workflowom,
2. používateľ musí výslovne potvrdiť `User accepted`,
3. tag `v1.0.0` sa vytvorí na tom istom už overenom SHA bez ďalšej source mutation.
""",
)

write(
    "PRACTICAL-V1-ROADMAP.md",
    f"""
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

Combined technical baseline `{BASELINE_SHA}`:

- RC run `{BASELINE_RC_RUN}` — success,
- final release-evidence run `{BASELINE_RELEASE_RUN}` — success,
- cleanup/worktree and artifact manifest verified,
- no tag and no user-acceptance claim created by workflow.

RAG indirect-injection closeout:

- SHA `{RAG_CLOSEOUT_SHA}`,
- run `{RAG_CLOSEOUT_RUN}` — success,
- artifact `{RAG_CLOSEOUT_ARTIFACT}`,
- `evidence_id={RAG_CLOSEOUT_EVIDENCE}`,
- synthetic untrusted retrieved document classified unsafe and excluded from citations.

Standalone Keycloak hygiene run `{KEYCLOAK_RUN}` also succeeds on rerun attempt 2; the original red attempt failed during checkout, before the identity runtime gate executed.

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
""",
)

write(
    "PRACTICAL-V1-EVIDENCE.md",
    f"""
# Practical v1 evidence ledger

This ledger records executed evidence without turning source text into a substitute for runtime artifacts.

## 1. Combined release baseline

Subject: `{BASELINE_SHA}`

| Evidence | Value |
|---|---|
| Release-candidate run | `{BASELINE_RC_RUN}` — success |
| Release-evidence run | `{BASELINE_RELEASE_RUN}` — success |
| `release_candidate_id` | `{BASELINE_RC_ID}` |
| `dependency_resolution_id` | `{BASELINE_DEPENDENCY_ID}` |
| `workflow_provenance_id` | `{BASELINE_PROVENANCE_ID}` |
| `release_evidence_id` | `{BASELINE_RELEASE_EVIDENCE_ID}` |
| `artifact_manifest_id` | `{BASELINE_MANIFEST_ID}` |
| Cleanup | `workflow_cleanup_verified=true`, core cleanup/worktree verified |
| Tag boundary | `release_tag_created=false` |
| Acceptance boundary | `user_acceptance_claimed=false` |

The baseline proves the bounded combined lifecycle across core contracts, MLOps post-retraining runtime, clean-checkout RAG and live Keycloak/protected RAG-agent identity composition.

## 2. RAG retrieved-context injection closeout

Subject: `{RAG_CLOSEOUT_SHA}`

- workflow run `{RAG_CLOSEOUT_RUN}` — success,
- artifact `{RAG_CLOSEOUT_ARTIFACT}`,
- `evidence_id={RAG_CLOSEOUT_EVIDENCE}`,
- indirect runtime case ID `{RAG_INDIRECT_CASE}`,
- `attack_type=indirect`,
- malicious retrieved chunk classified `prompt_injection_detected`,
- safe chunk remained usable/cited,
- unsafe and cited chunk sets are disjoint,
- `retrieved_context_prompt_injection_eval=executed-synthetic-untrusted-document`,
- cleanup verified.

This closes the previous proof-boundary gap where indirect injection existed in unit/hard-eval coverage but was not represented in the canonical RAG runtime record.

## 3. Keycloak standalone hygiene

Run `{KEYCLOAK_RUN}` now concludes success on `run_attempt=2`. Attempt 1 failed during exact-subject checkout, so it did not execute the Keycloak runtime gate. The successful rerun removes that standalone CI ambiguity.

The automated identity proof still does not claim an actual interactive browser Authorization Code exchange; that remains an explicit proof boundary rather than a hidden success claim.

## 4. Final `v1.0.0` subject policy

The final release subject is **not** one of the historical subjects above. After repository metadata/workflow cleanup, the exact current `main` must run the canonical RC and release-evidence workflows again.

The final authoritative record is the GitHub Actions artifact bound to that exact SHA. No source commit may be made merely to copy the future run ID into this file, because doing so would create a different subject.

Required final artifact properties:

```text
subject_sha == tag target SHA
release candidate all_passed == true
core cleanup/worktree verified == true
workflow_cleanup_verified == true
canonical dependency/workflow provenance IDs valid
release_tag_created == false
user_acceptance_claimed == false
```

After read-back, explicit user acceptance may authorize creation of `v1.0.0` on that same SHA.
""",
)

write(
    "PRACTICAL-V1-RELEASE-EVIDENCE.md",
    f"""
# Practical v1 release evidence

> **Status: release-evidence pipeline runtime verified; final tag subject exact-head run pending.**

The permanent hosted workflow is `.github/workflows/practical-v1-release-evidence.yml`. It composes the canonical release-candidate lifecycle with exact dependency resolution, GitHub workflow/run provenance and post-cleanup artifact manifest verification.

## Verified baseline

On `{BASELINE_SHA}`:

- RC run `{BASELINE_RC_RUN}` succeeded,
- release-evidence run `{BASELINE_RELEASE_RUN}` succeeded,
- `release_candidate_id={BASELINE_RC_ID}`,
- `dependency_resolution_id={BASELINE_DEPENDENCY_ID}`,
- `workflow_provenance_id={BASELINE_PROVENANCE_ID}`,
- `release_evidence_id={BASELINE_RELEASE_EVIDENCE_ID}`,
- `artifact_manifest_id={BASELINE_MANIFEST_ID}`,
- `workflow_cleanup_verified=true`,
- `release_tag_created=false`,
- `user_acceptance_claimed=false`.

The workflow permission remains `contents: read`; it is evidence generation, not release/tag mutation authority.

## Canonical artifact contents

A successful final bundle contains at least:

- `core.json`,
- `mlops.json`,
- `rag.json`,
- `identity.json`,
- `release-candidate.json`,
- `dependency-resolution.json`,
- `workflow-provenance.json`,
- `release-evidence.json`,
- `artifact-manifest.json`.

The finalizer recalculates the canonical candidate/dependency/provenance identities before producing release evidence and the artifact manifest binds SHA-256/size of the complete JSON bundle after cleanup.

## Final tag-subject acceptance

Before `v1.0.0`, the current final `main` SHA must independently satisfy:

1. successful RC lifecycle,
2. successful release-evidence workflow,
3. exact subject SHA equality,
4. canonical IDs verified,
5. cleanup/worktree read-back verified,
6. `release_tag_created=false`,
7. `user_acceptance_claimed=false`.

The final run IDs live in GitHub Actions provenance. They are not committed after execution, because such a commit would create a new unverified Git subject.

## Proof boundary

Successful Practical v1 release evidence proves the bounded local/hosted profile defined by the repository. It does not automatically prove production Kubernetes/cloud readiness, production identity HA/federation, remote production Registry durability, real-browser PKCE exchange, GPU/distributed ML, external LLM quality or production remediation authority.
""",
)

write(
    "PRACTICAL-V1-RELEASE-NOTES.md",
    f"""
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

Combined baseline `{BASELINE_SHA}` passed RC run `{BASELINE_RC_RUN}` and release-evidence run `{BASELINE_RELEASE_RUN}`. RAG indirect-injection runtime closeout passed run `{RAG_CLOSEOUT_RUN}` on `{RAG_CLOSEOUT_SHA}`. Standalone Keycloak run `{KEYCLOAK_RUN}` is successful after rerun.

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
""",
)

write(
    "labs/README.md",
    f"""
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

Combined baseline `{BASELINE_SHA}` passed canonical RC and release-evidence workflows. RAG indirect retrieved-context injection is additionally runtime-verified on `{RAG_CLOSEOUT_SHA}` / run `{RAG_CLOSEOUT_RUN}`.

The current final `main` must still pass one last exact-head release lifecycle after repository metadata closeout. `User accepted` remains false until explicit user confirmation.

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
""",
)

# Root README: remove the obsolete dispatch-blocker claim without rewriting the rest.
replace_if_present(
    "README.md",
    "Permanentný CI contract je v `.github/workflows/practical-v1-core.yml`. Kým issue #151 blokuje vytváranie repository Actions runov, existencia workflowu a runnera znamená iba source-level `Implemented`, nie `Runtime verified`.",
    "Permanentný CI contract je v `.github/workflows/practical-v1-core.yml`. GitHub Actions dispatch blocker #151 je uzavretý; runtime stav sa neurčuje existenciou workflowu, ale exact-SHA evidence. Aktuálny authoritative stav je v [PRACTICAL-STATUS.md](PRACTICAL-STATUS.md) a [PRACTICAL-V1-EVIDENCE.md](PRACTICAL-V1-EVIDENCE.md).",
)

# Preserve detailed runtime contracts; only synchronize their current evidence framing.
replace_if_present(
    "labs/mlops/RUNTIME-EVIDENCE.md",
    "> **Evidence status: Pending**",
    "> **Evidence status: Runtime verified for the bounded Practical v1 local profile**",
)
replace_if_present(
    "labs/mlops/RUNTIME-EVIDENCE.md",
    "Tento dokument je authoritative runtime-evidence contract pre celý Practical v1 MLOps lifecycle. Source implementácia už pokrýva promotion foundation, training lineage, MLflow Tracking/Registry a artifact read-back, immutable serving/canary/rollback, monitoring/drift, approval-gated controlled retraining a post-retraining deployment handoff. `Pending` znamená, že tieto vrstvy ešte nemajú jeden alebo viac exact authoritative runtime records potrebných na ich acceptance; source completeness sa nesmie interpretovať ako `Runtime verified`.",
    f"Tento dokument je authoritative runtime-evidence contract pre celý Practical v1 MLOps lifecycle. Required vrstvy boli vykonané v canonical combined release baseline na `{BASELINE_SHA}` (release-evidence run `{BASELINE_RELEASE_RUN}`) vrátane local MLflow/Registry provider read-backu, containerized inference, canary/rollback, drift/retraining, post-retraining handoff a cleanupu. Stav je bounded na deklarovaný local/hosted v1 profile a neznamená production platform readiness.",
)
replace_if_present(
    "labs/mlops/RUNTIME-EVIDENCE.md",
    "Repository obsahuje MLOps-specific workflows aj spoločný `.github/workflows/practical-v1-core.yml`. Kým issue #151 nevytvára observable Actions runs, ich prítomnosť zostáva source contractom, nie runtime evidence.",
    f"Repository obsahuje MLOps-specific workflows aj spoločný release lifecycle. GitHub Actions blocker #151 je uzavretý; canonical runtime evidence je viazaná na executed baseline `{BASELINE_SHA}` a ďalší final tag subject musí znovu prejsť exact-head release gate-om.",
)
replace_if_present(
    "labs/mlops/RUNTIME-EVIDENCE.md",
    "Kým required evidence records neexistujú, stav zostáva `Pending`.",
    "Required bounded-local evidence records existujú; production/cloud proof boundaries uvedené vyššie zostávajú mimo Practical v1 claimu.",
)

replace_if_present(
    "labs/llm-rag/RUNTIME-EVIDENCE.md",
    "> **Evidence status: Pending**",
    "> **Evidence status: Runtime verified for the deterministic Practical v1 profile**",
)
replace_if_present(
    "labs/llm-rag/RUNTIME-EVIDENCE.md",
    "Tento dokument je authoritative runtime-evidence contract pre celý offline/deterministic Practical v1 RAG flagship. Source implementácia už pokrýva exact Git corpus, deterministic Markdown chunking, lexical index/retrieval, explicitný `no_result`, exact citations, bounded grounded answer/abstention, eval/security release gates, tracing a cleanup. `Pending` znamená, že repository ešte nemá successful authoritative clean-checkout run pre exact merged implementation subject.\n\nGitHub Actions dispatch je momentálne otvorený repository-level blocker v issue #151. Source/test completeness preto nie je `Runtime verified`.",
    f"Tento dokument je authoritative runtime-evidence contract pre celý offline/deterministic Practical v1 RAG flagship. Canonical clean-checkout runtime je verified; po combined baseline bol retrieved-context injection proof explicitne sprísnený a úspešne vykonaný na `{RAG_CLOSEOUT_SHA}` v rune `{RAG_CLOSEOUT_RUN}` (`evidence_id={RAG_CLOSEOUT_EVIDENCE}`). GitHub Actions blocker #151 je uzavretý.",
)
replace_if_present(
    "labs/llm-rag/RUNTIME-EVIDENCE.md",
    "Kým exact clean-checkout record neexistuje, stav zostáva `Pending`.",
    "Exact clean-checkout record existuje; semantic/vector/external-LLM a production proof boundaries uvedené vyššie zostávajú mimo Practical v1 claimu.",
)

replace_if_present(
    "labs/agent-ops/RUNTIME-EVIDENCE.md",
    "> **Evidence status: Pending**",
    "> **Evidence status: Runtime verified for the bounded combined Practical v1 local profile**",
)
replace_if_present(
    "labs/agent-ops/RUNTIME-EVIDENCE.md",
    "Tento dokument je authoritative runtime-evidence contract pre Practical v1 bounded incident/operations agent. Source implementation po PR #179 pokrýva typed inspection, deterministic planning, durable state, exact time-bounded approval, policy-bound kill switch, one-mutation/tool-wait bounds, idempotent read-before-retry, hardened unknown-outcome handling, promoted retrieval-context authority boundary, strict typed tool-result schema a deterministic hard evaluation. Bez exact clean-checkout runtime recordu však track zostáva `Implemented`, nie `Runtime verified`.",
    f"Tento dokument je authoritative runtime-evidence contract pre Practical v1 bounded incident/operations agent. Combined canonical release baseline na `{BASELINE_SHA}` vykonal deterministic agent contracts/hard evaluation aj protected Keycloak/RAG-agent composition. Runtime claim je bounded na local single-host profile; production credentials, distributed locking a remote exactly-once semantics sa neclaimujú.",
)
replace_if_present(
    "labs/agent-ops/RUNTIME-EVIDENCE.md",
    "Kým exact clean-checkout records neexistujú, stav zostáva `Pending`.",
    "Required bounded local/combined records existujú; production/distributed proof boundaries uvedené vyššie zostávajú mimo Practical v1 claimu.",
)

replace_if_present(
    "labs/keycloak-ai-api/RUNTIME-EVIDENCE.md",
    "> **Evidence status: Pending**",
    "> **Evidence status: Runtime verified for automated local service-account/JWKS/protected-API Practical v1 profile**",
)
replace_if_present(
    "labs/keycloak-ai-api/RUNTIME-EVIDENCE.md",
    "Tento dokument je authoritative runtime evidence contract pre Practical v1 identity path. Source implementácia realm configu, token helpers, JWT/resource-server policy, promoted RAG adapter a bounded-agent routes existuje, ale bez exact live runu sa nesmie interpretovať ako `Runtime verified`.",
    f"Tento dokument je authoritative runtime evidence contract pre Practical v1 identity path. Canonical combined release baseline na `{BASELINE_SHA}` a standalone Keycloak run `{KEYCLOAK_RUN}` (successful rerun attempt 2) verify disposable local Keycloak, live JWKS/service-account token validation and protected RAG/agent API paths. Actual interactive browser Authorization Code exchange remains explicitly not executed and is not claimed by this automated profile.",
)
replace_if_present(
    "labs/keycloak-ai-api/RUNTIME-EVIDENCE.md",
    "Kým exact live record neexistuje, stav zostáva `Pending`.",
    "Exact automated local identity record existuje; real-browser Authorization Code exchange a production identity-platform boundaries uvedené vyššie zostávajú mimo automated Practical v1 claimu.",
)

# Remove a few obsolete current-blocker sentences from authoritative entry READMEs while retaining history.
for path in (
    "labs/mlops/README.md",
    "labs/llm-rag/README.md",
    "labs/keycloak-ai-api/README.md",
    "labs/agent-ops/README.md",
):
    replace_if_present(
        path,
        "Issue #151 je repository-level GitHub Actions dispatch blocker; kým nevznikne authoritative run, runtime evidence sa neclaimuje.",
        "GitHub Actions dispatch blocker #151 je uzavretý; authoritative current runtime stav je v príslušnom `RUNTIME-EVIDENCE.md` a root Practical v1 evidence ledgeri.",
    )

# This staging script must not survive the closeout commit.
Path(__file__).unlink()
