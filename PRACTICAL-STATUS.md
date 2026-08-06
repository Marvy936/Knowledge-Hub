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
| MLOps promotion foundation | Áno | Áno | Pending post-merge closeout | Nie | [`labs/mlops/RUNTIME-EVIDENCE.md`](labs/mlops/RUNTIME-EVIDENCE.md) |
| MLOps Tracking/Registry a artifact read-back | Áno v sekcii 19 | Nie | Nie | Nie | Ďalší Practical v1 blok |
| MLOps serving, canary a rollback | Áno v sekcii 19 | Nie | Nie | Nie | Ďalší Practical v1 blok |
| MLOps monitoring, drift a retraining | Áno v sekcii 19 | Nie | Nie | Nie | Ďalší Practical v1 blok |
| Knowledge Hub LLM/RAG flagship | Áno v sekcii 20 | Nie | Nie | Nie | Required for Practical v1 |
| Keycloak-secured AI API | Áno v sekciách 17, 20 a 21 | Nie | Nie | Nie | Required for Practical v1 |
| Bounded incident/operations agent | Áno v sekcii 21 | Nie | Nie | Nie | Required for Practical v1 |
| Unified Practical v1 runner/evidence | Áno v roadmap-e | Nie | Nie | Nie | Required for Practical v1 closeout |

## Dokumentačné sekcie a praktický stav

| Sekcia | Dokumentačný stav | Praktická interpretácia |
|---|---|---|
| 00–17 | `User reviewed` v aktuálnom dokumentačnom rozsahu | Neznamená automaticky vykonané laby ani runtime acceptance. |
| 18 — Machine Learning Fundamentals | `Ready for user review` | Flagship package je implementovaný a runtime verified; sekcia ako celok ešte nie je `User accepted`. |
| 19 — MLOps and ML Platforms | `Ready for user review` | Prvý promotion foundation blok je implementovaný; end-to-end lifecycle a runtime closeout nie sú hotové. |
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
