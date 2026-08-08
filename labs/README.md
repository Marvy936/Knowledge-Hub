# Knowledge Hub practical labs

Tento index je authoritative vstup do praktickej vrstvy repozitára. Nezamieňa učebný text, manuálny exercise set, executable package a runtime-verified flagship. Presný stav každej oblasti je v [`PRACTICAL-STATUS.md`](../PRACTICAL-STATUS.md) a release hranica v [`PRACTICAL-V1-ROADMAP.md`](../PRACTICAL-V1-ROADMAP.md).

## Typy praktického obsahu

| Typ | Význam |
|---|---|
| Executable package | Zdrojový kód a automatizované testy spustiteľné z clean checkoutu. |
| Manual lab set | Presne definované úlohy, failure variants, validation a cleanup, ktoré vyžadujú externé prostredie. |
| Practical walkthrough | Riadený experiment vložený do authoritative kapitoly; nie je samostatným runtime package-om. |
| Troubleshooting drill | Zámerne chybný scenár s diagnostikou, recovery a acceptance hranicou. |
| Runtime verified | Exact revision prešla zaznamenaným workflowom alebo ekvivalentným evidence gate-om. |

`Implemented` neznamená automaticky `Runtime verified`. Manuálny lab môže byť plne zdokumentovaný a použiteľný, ale bez centrálne vykonaného cloudového alebo clusterového runu.

## Executable flagship packages

### Machine Learning Fundamentals

- Index: [`machine-learning/README.md`](machine-learning/README.md)
- Runtime evidence: [`machine-learning/RUNTIME-EVIDENCE.md`](machine-learning/RUNTIME-EVIDENCE.md)
- Stav: implementovaný a runtime verified pre deklarovaný syntetický Python 3.12 lifecycle.
- Preukazuje: deterministic dataset, schema/leakage refusal, model comparison, validation-only threshold selection, test gate, integrity-bound packaging, strict inference a cleanup.
- Nepreukazuje: production dataset, train-serving consistency, reálny drift, business impact alebo production readiness.

### MLOps flagship

- Index: [`mlops/README.md`](mlops/README.md)
- Runtime evidence: [`mlops/RUNTIME-EVIDENCE.md`](mlops/RUNTIME-EVIDENCE.md)
- Stav: source/control-plane lifecycle je implementovaný cez promotion, Registry, serving, canary, monitoring, controlled retraining a post-retraining handoff; central runtime closeout je blokovaný issue #151.
- Preukázané source vrstvy sú viazané na exact subjects, immutable IDs, explicitné no-data/unknown-outcome states, recovery a compare-before-change semantics.
- Otvorené zostávajú actual OCI/container runtime evidence, live end-to-end MLflow retraining closeout a GitHub Actions runtime verification.

### Knowledge Hub LLM/RAG flagship

- Index: [`llm-rag/README.md`](llm-rag/README.md)
- Retrieval/answer contract: [`llm-rag/RETRIEVAL-GROUNDED-ANSWER.md`](llm-rag/RETRIEVAL-GROUNDED-ANSWER.md)
- Eval/security/observability contract: [`llm-rag/EVAL-SECURITY-OBSERVABILITY.md`](llm-rag/EVAL-SECURITY-OBSERVABILITY.md)
- Runtime evidence: [`llm-rag/RUNTIME-EVIDENCE.md`](llm-rag/RUNTIME-EVIDENCE.md)
- Stav: offline deterministic Practical v1 source lifecycle je implementovaný; runtime evidence je `Pending` kvôli Actions blockeru #151.
- Aktuálny rozsah: exact Git corpus snapshot, per-file byte identity, deterministic Markdown chunking, immutable chunk/index/query/result identities, BM25-v1 retrieval, explicitný `no_result`, exact chunk citations, bounded context, exact implementation-revision binding, code-defined system policy, direct/indirect prompt-injection gates, deterministic extractive faithfulness, critical/high-risk eval gates, prompt/config release provenance, trace/token-equivalent evidence a bounded cleanup.
- Otvorené zostávajú central runtime closeout a voliteľné post-v1 generative/semantic adapters; generatívny model nie je hard requirement offline Practical v1 core pathu.

## Manual environment labs

### CKA timed labs

- Index: [`cka/README.md`](cka/README.md)
- Teoretický kontext: [`../docs/10-helm-and-cka/cka-timed-labs.md`](../docs/10-helm-and-cka/cka-timed-labs.md)
- Troubleshooting: [`../troubleshooting/cka/README.md`](../troubleshooting/cka/README.md)
- Execution boundary: disposable alebo obnoviteľný Kubernetes cluster, explicitný context/namespace, timer, hard validation a cleanup.
- Centrálny runtime status: manual/external; konkrétne vykonanie sa eviduje v review zázname používateľa.

### AWS CloudOps hands-on labs

- Index: [`aws-cloudops/README.md`](aws-cloudops/README.md)
- Teoretický kontext: [`../docs/11-cloud-and-aws/cloudops-hands-on-labs.md`](../docs/11-cloud-and-aws/cloudops-hands-on-labs.md)
- Troubleshooting: [`../troubleshooting/aws-cloudops/README.md`](../troubleshooting/aws-cloudops/README.md)
- Execution boundary: explicitný sandbox account/Region, budget controls, least privilege, telemetry, fault injection, cleanup a billing read-back.
- Centrálny runtime status: manual/external; cloud execution nie je hard blocker lokálneho Practical v1 core pathu.

## Practical walkthroughs v authoritative dokumentácii

Niektoré experimenty zostávajú zámerne pri súvisiacej kapitole, pretože nevytvárajú samostatný package alebo persistent environment. Patrí sem napríklad:

- [`Networking practical walkthrough`](../docs/02-networking-and-web/networking-practical-walkthrough.md),
- praktické walkthroughs pre Git, testing, CI/CD, Docker, Kubernetes, Helm, AWS, observability, security, SRE, databázy, GitOps a Keycloak v príslušných section README.

Walkthrough sa do tohto indexu nepovažuje za samostatný flagship, kým nemá vlastný execution contract, tests alebo manual lab index a explicitný status v `PRACTICAL-STATUS.md`.

## Practical v1 required tracky

```text
Machine Learning flagship — runtime verified
→ MLOps end-to-end lifecycle — source lifecycle implemented, runtime closeout blocked
→ Knowledge Hub LLM/RAG flagship — offline source lifecycle implemented, runtime closeout blocked
→ Keycloak-secured AI API — next required v1 track
→ bounded incident/operations agent — planned for v1
→ unified runner, evidence closeout a v1.0.0 tag
```

Úplný checklist a post-v1 backlog sú v [`PRACTICAL-V1-ROADMAP.md`](../PRACTICAL-V1-ROADMAP.md).

## Spoločný execution contract

Každý nový flagship alebo automatizovaný lab musí mať:

1. exact subject a generation identity,
2. clean-checkout setup bez skrytých manuálnych krokov,
3. positive path,
4. forbidden alebo refusal path,
5. recovery alebo rollback path podľa typu scenára,
6. explicitný no-data/unknown-outcome stav,
7. cleanup a read-back,
8. runtime evidence viazané na exact revision,
9. proof boundary, ktorý neprekračuje vykonaný run.

## Čo tento index neznamená

Prítomnosť odkazu neznamená, že bol lab vykonaný používateľom, že prešiel na každom podporovanom prostredí alebo že je produkčne pripravený. Autoritatívny stav určuje kombinácia source, status ledgeru, runtime evidence a používateľského review.
