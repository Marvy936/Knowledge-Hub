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

Canonical combined baseline na `789b5038b81b9342b1aef57b809bd3b67202ebde`:

- release-candidate run `31542501323` — success,
- release-evidence run `31542501346` — success,
- `release_candidate_id=2e0a0754332864ca5898852b921d76d88e78d0c8209ea3dccfab7a92c6fe0778`,
- `release_evidence_id=1bced14424764a890f8c8fbd346c49992c5ba1d2c7963d9f3b65485547c37b47`,
- `artifact_manifest_id=52f6c2c886c14d746f3fdd7c35fc82a93e24372570acea50f6a90cad08c6eca2`,
- `workflow_cleanup_verified=true`,
- `release_tag_created=false`,
- `user_acceptance_claimed=false`.

RAG security closeout bol následne sprísnený a overený na `8c861edac728e5d19e7dd6035e4b438b8e8f8c2a` runom `31636019897`; retrieved-context/indirect injection je teraz explicitný runtime case.

## Release boundary

Technická baseline je overená. Pred immutable `v1.0.0` zostávajú presne tri release kroky:

1. exact aktuálny `main` po metadata closeoute musí prejsť canonical RC + release-evidence workflowom,
2. používateľ musí výslovne potvrdiť `User accepted`,
3. tag `v1.0.0` sa vytvorí na tom istom už overenom SHA bez ďalšej source mutation.
