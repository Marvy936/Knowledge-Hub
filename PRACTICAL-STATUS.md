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
| MLOps serving, canary a rollback | Áno v sekcii 19 | Nie | Nie | Nie | Nasledujúci Practical v1 blok |
| MLOps monitoring, drift a retraining | Áno v sekcii 19 | Nie | Nie | Nie | Neskorší Practical v1 blok |
| Knowledge Hub LLM/RAG flagship | Áno v sekcii 20 | Nie | Nie | Nie | Required for Practical v1 |
| Keycloak-secured AI API | Áno v sekciách 17, 20 a 21 | Nie | Nie | Nie | Required for Practical v1 |
| Bounded incident/operations agent | Áno v sekcii 21 | Nie | Nie | Nie | Required for Practical v1 |
| Unified Practical v1 runner/evidence | Áno v roadmap-e | Čiastočne — lab index, status ledger a MLOps unified runner | Nie | Nie | Required for Practical v1 closeout |

## MLOps implementačné subjects

Aktuálny implementovaný MLOps rozsah je viazaný najmä na:

- PR #140 — deterministic promotion foundation,
- PR #145 — MLflow Registry a artifact read-back lifecycle,
- PR #150 — evaluation odvodená z exact training manifestu,
- PR #152 — hosted unified Registry runner,
- PR #153 — self-hosted unified Registry runner.

Exact-source reconstruction prešla 16/16 testami po Registry implementácii a 21/21 testami po training-lineage rozšírení. Tieto výsledky dokazujú Python a contract správanie v rekonštruovanom prostredí. Nenahrádzajú chýbajúci GitHub Actions run, live package installation, MLflow server execution, restart verification alebo cleanup evidence.

Issue #151 je explicitný Practical v1 blocker pre runtime closeout. Kým GitHub nevytvorí exact workflow run a jeho read-back, MLOps riadky zostávajú `Runtime verified = Nie`.

## Dokumentačné sekcie a praktický stav

| Sekcia | Dokumentačný stav | Praktická interpretácia |
|---|---|---|
| 00–17 | `User reviewed` v aktuálnom dokumentačnom rozsahu | Neznamená automaticky vykonané laby ani runtime acceptance. |
| 18 — Machine Learning Fundamentals | `Ready for user review` | Flagship package je implementovaný a runtime verified; sekcia ako celok ešte nie je `User accepted`. |
| 19 — MLOps and ML Platforms | `Ready for user review` | Promotion, training-lineage a Registry contracts sú implementované; runtime closeout, serving, canary, rollback, drift a retraining zostávajú otvorené. |
| 20 — LLM and GenAI Engineering | `Ready for user review` | Practical v1 flagship ešte nie je implementovaný. |
| 21 — AI Agents and Intelligent Automation | `Ready for user review` | Practical v1 bounded agent ešte nie je implementovaný. |

## Stavový postup

```text
Documented
→ Implemented
→ Runtime verified pre exact subject a environment
→ User accepted pre explicitne vymedzený rozsah
```

Prechod môže byť čiastočný. Napríklad MLOps promotion foundation môže byť `Runtime verified`, zatiaľ čo celá MLOps flagship zostáva `In progress`.

## Pravidlá konzistencie

- zelený unit test nemení automaticky celý flagship na runtime verified,
- úspešné vytvorenie resource alebo manifestu nie je samo osebe business outcome,
- manuálne vykonaný lab bez exact evidence nie je central CI verification,
- documentation review nie je practical user acceptance,
- chýbajúci workflow status alebo chýbajúca telemetry nie je úspech,
- `Pending`, `Queued`, `Unknown outcome` a `No data` zostávajú otvorené stavy bez read-back dôkazu.

## Aktualizácia ledgeru

Ledger sa aktualizuje v rovnakom closeout PR ako runtime evidence alebo explicitné používateľské prijatie. Každá zmena na `Runtime verified` uvádza exact subject, workflow/run alebo ekvivalentný evidence record a proof boundary. Každá zmena na `User accepted` je založená na explicitnom rozhodnutí používateľa, nie na inferencii z merge alebo CI.
