# Practical implementation status

Tento ledger oddeľuje štyri nezávislé stavy praktického obsahu.

| Stav | Presný význam |
|---|---|
| `Documented` | Existuje authoritative vysvetlenie alebo praktický contract. |
| `Implemented` | Existuje vykonateľný package, manifest, script alebo úplný manual lab set. |
| `Runtime verified` | Exact revision prešla zaznamenaným runtime gate-om v deklarovanom prostredí. |
| `User accepted` | Používateľ výslovne prijal praktický rozsah alebo výsledok. |

Stavy sa nededia automaticky. `Runtime verified` nie je production readiness a `Implemented` nie je dôkaz úspešného vykonania.

## Praktické oblasti

| Oblasť | Documented | Implemented | Runtime verified | User accepted | Autoritatívny dôkaz alebo ďalší gate |
|---|---|---|---|---|---|
| CKA timed labs | Áno | Áno — manual lab set | Nie centrálne; vykonáva sa na externom alebo disposable clustri | Nie | [`labs/cka/README.md`](labs/cka/README.md) |
| AWS CloudOps labs | Áno | Áno — manual lab set | Nie centrálne; vyžaduje sandbox account a cost controls | Nie | [`labs/aws-cloudops/README.md`](labs/aws-cloudops/README.md) |
| Networking practical walkthrough | Áno | Áno — guided walkthrough | Nie ako samostatný package | Nie | [`docs/02-networking-and-web/networking-practical-walkthrough.md`](docs/02-networking-and-web/networking-practical-walkthrough.md) |
| Machine Learning flagship | Áno | Áno | Áno — syntetický Python 3.12 lifecycle | Nie | [`labs/machine-learning/RUNTIME-EVIDENCE.md`](labs/machine-learning/RUNTIME-EVIDENCE.md) |
| MLOps promotion foundation | Áno | Áno — candidate, release a compare-before-promote contracts | Nie — Actions dispatch blocker #151 | Nie | [`labs/mlops/RUNTIME-EVIDENCE.md`](labs/mlops/RUNTIME-EVIDENCE.md) |
| MLOps training lineage | Áno | Áno — evaluation odvodená z exact ML training manifestu | Nie — 21/21 exact-source tests nie sú live workflow evidence | Nie | [`labs/mlops/TRAINING-LINEAGE.md`](labs/mlops/TRAINING-LINEAGE.md) |
| MLOps Tracking/Registry a artifact read-back | Áno | Áno — MLflow server, SQLite Registry, artifact checksum a exact-version contracts | Nie — Actions dispatch blocker #151 | Nie | [`labs/mlops/RUNTIME-EVIDENCE.md`](labs/mlops/RUNTIME-EVIDENCE.md) |
| MLOps serving, canary a rollback | Áno | Áno na source/control-plane úrovni — immutable deployment, FastAPI source, deterministic routing, live loopback canary, rollback a post-retraining handoff | Nie — bez actual OCI build/digest, container artifact mount, platform traffic read-back a kvôli blockeru #151 | Nie | [`labs/mlops/POST-RETRAINING-HANDOFF.md`](labs/mlops/POST-RETRAINING-HANDOFF.md) |
| MLOps monitoring, drift a retraining | Áno | Áno — aggregate monitoring, semantic drift report, exact human approval a approval-bound controlled executor s durable checkpoint/recovery contractom | Nie — 16/16 izolovaných executor testov nie je live MLflow retraining ani workflow evidence | Nie | [`labs/mlops/CONTROLLED-RETRAINING.md`](labs/mlops/CONTROLLED-RETRAINING.md) |
| Knowledge Hub LLM/RAG corpus a chunking | Áno | Áno — exact Git corpus snapshot, byte read-back, deterministic Markdown chunking a rebuild validation | Nie — `RUNTIME-EVIDENCE.md` je `Pending`; Actions blocker #151 | Nie | [`labs/llm-rag/README.md`](labs/llm-rag/README.md) |
| Knowledge Hub LLM/RAG retrieval a answer lifecycle | Áno v sekcii 20 | Nie | Nie | Nie | Nasledujúce Practical v1 bloky |
| Keycloak-secured AI API | Áno v sekciách 17, 20 a 21 | Nie | Nie | Nie | Required for Practical v1 |
| Bounded incident/operations agent | Áno v sekcii 21 | Nie | Nie | Nie | Required for Practical v1 |
| Unified Practical v1 runner/evidence | Áno v roadmap-e | Čiastočne — lab index, status ledger a MLOps unified runner | Nie | Nie | Required for Practical v1 closeout |

## MLOps implementačné subjects

Aktuálny implementovaný MLOps rozsah je viazaný najmä na:

- PR #140 — deterministic promotion foundation,
- PR #145 — MLflow Registry a artifact read-back lifecycle,
- PR #150 — evaluation odvodená z exact training manifestu,
- PR #152 — hosted unified Registry runner,
- PR #153 — self-hosted unified Registry runner,
- PR #155 — immutable deployment, canary routing a rollback control-plane contracts,
- PR #157 — identity-bound FastAPI serving source a Dockerfile contract,
- PR #158 — live two-generation loopback canary evidence a rollback decision,
- PR #160 — aggregate monitoring, semantically validated drift a exact retraining approval,
- PR #162 — approval-bound controlled retraining executor, durable state, Registry unknown-outcome checkpoint a compare-before-promote recovery,
- PR #164 — completed-retraining → immutable deployment → bounded canary routing handoff.

Oddelené exact-source rekonštrukcie prešli 16/16 testami po Registry implementácii, 21/21 po training-lineage rozšírení, 29/29 po serving control-plane vrstve, 38/38 po HTTP serving source vrstve, 42/42 po live-canary vrstve, 13/13 pre monitoring/drift/approval, 16/16 pre controlled retraining executor a 7/7 pre post-retraining deployment handoff. Tieto počty patria samostatným validačným bodom; nepredstavujú jeden spoločný vykonaný repository run.

Dôkazy preukazujú Python, CLI, HTTP loopback, durable local state, failure recovery, Registry intent/response checkpoint, completed-retraining handoff a contract správanie vo vymedzených rekonštruovaných prostrediach. Nenahrádzajú chýbajúci GitHub Actions run, live end-to-end MLflow retraining, actual OCI build a digest read-back, container artifact mount, skutočnú platform traffic zmenu, post-retraining container/canary read-back, production telemetry ani business outcome.

Issue #151 je explicitný Practical v1 blocker pre central runtime closeout. Diagnostické PR #166 aj jednorazový `main` diagnostic nevytvorili Actions run; aktuálna klasifikácia je repository-level Actions dispatch/settings/workflow-enable problém. Kým GitHub nevytvorí exact workflow run a jeho read-back, príslušné runtime states zostávajú `Nie`.

## LLM/RAG implementačné subjects

- PR #167 — exact Git corpus snapshot, per-file byte identity, workspace-independent snapshot ID, deterministic Markdown heading/code-fence chunking, per-chunk identity a deterministic full-manifest rebuild.

PR #167 obsahuje 17 test cases v source pre positive a refusal contracts. Úspešný pytest/CI run sa neclaimuje, pretože Actions dispatch blocker #151 zostáva otvorený. `labs/llm-rag/RUNTIME-EVIDENCE.md` preto zostáva `Pending`.

## Dokumentačné sekcie a praktický stav

| Sekcia | Dokumentačný stav | Praktická interpretácia |
|---|---|---|
| 00–17 | `User reviewed` v aktuálnom dokumentačnom rozsahu | Neznamená automaticky vykonané laby ani runtime acceptance. |
| 18 — Machine Learning Fundamentals | `Ready for user review` | Flagship package je implementovaný a runtime verified; sekcia ako celok ešte nie je `User accepted`. |
| 19 — MLOps and ML Platforms | `Ready for user review` | Promotion, training lineage, Registry, serving source, loopback canary, monitoring, drift, approval, controlled retraining executor a post-retraining deployment handoff sú implementované. Otvorené zostávajú central runtime closeout, actual OCI/container execution, živý retraining s novou Registry version a platform post-retraining canary read-back. |
| 20 — LLM and GenAI Engineering | `Ready for user review` | Corpus snapshot a deterministic chunking sú implementované; retrieval, grounded answer, eval/security a observability vrstvy zostávajú otvorené. |
| 21 — AI Agents and Intelligent Automation | `Ready for user review` | Practical v1 bounded agent ešte nie je implementovaný. |

## Stavový postup

```text
Documented
→ Implemented
→ Runtime verified pre exact subject a environment
→ User accepted pre explicitne vymedzený rozsah
```

Prechod môže byť čiastočný. Jednotlivá flagship vrstva môže byť `Implemented`, zatiaľ čo celý flagship zostáva otvorený.

## Pravidlá konzistencie

- zelený unit test nemení automaticky celý flagship na runtime verified,
- úspešné vytvorenie resource alebo manifestu nie je samo osebe business outcome,
- manuálne vykonaný lab bez exact evidence nie je central CI verification,
- documentation review nie je practical user acceptance,
- chýbajúci workflow status alebo chýbajúca telemetry nie je úspech,
- `Pending`, `Queued`, `Unknown outcome` a `No data` zostávajú otvorené stavy bez read-back dôkazu.

## Aktualizácia ledgeru

Ledger sa aktualizuje v rovnakom closeout PR ako runtime evidence alebo explicitné používateľské prijatie. Každá zmena na `Runtime verified` uvádza exact subject, workflow/run alebo ekvivalentný evidence record a proof boundary. Každá zmena na `User accepted` je založená na explicitnom rozhodnutí používateľa, nie na inferencii z merge alebo CI.
