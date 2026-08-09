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
| MLOps Tracking/Registry a artifact read-back | Áno | Áno — MLflow server, SQLite Registry, artifact checksum, exact-version contracts a hosted Registry runtime harness | Nie — Actions dispatch blocker #151; executable workflow ešte nevytvoril authoritative run | Nie | [`labs/mlops/RUNTIME-EVIDENCE.md`](labs/mlops/RUNTIME-EVIDENCE.md) |
| MLOps serving, canary a rollback | Áno | Áno na source/runtime-harness úrovni — immutable deployment, FastAPI source, deterministic routing, loopback canary/rollback contracts, post-retraining handoff a Docker containerized-inference driver/workflow s exact local image-ID, non-root a live-HTTP acceptance contractom | Nie — PR #186 je source-merged, ale jeho exact head aj merge commit nemajú Actions run/status; actual Docker execution, remote OCI manifest/pull a post-retraining platform read-back zostávajú nepreukázané | Nie | [`labs/mlops/CONTAINER-SERVING.md`](labs/mlops/CONTAINER-SERVING.md), [`labs/mlops/RUNTIME-EVIDENCE.md`](labs/mlops/RUNTIME-EVIDENCE.md) |
| MLOps monitoring, drift a retraining | Áno | Áno na source/runtime-harness úrovni — aggregate monitoring, semantic drift report, exact approval, durable controlled executor a live-local-MLflow retraining driver/workflow s forged-approval refusal, new-version/alias read-back a completed replay contractom | Nie — PR #187 je source-merged, ale exact workflow execution neexistuje kvôli #151; live MLflow retraining side effect ani cleanup evidence sa preto neclaimujú | Nie | [`labs/mlops/CONTROLLED-RETRAINING.md`](labs/mlops/CONTROLLED-RETRAINING.md), [`labs/mlops/LIVE-CONTROLLED-RETRAINING.md`](labs/mlops/LIVE-CONTROLLED-RETRAINING.md) |
| Knowledge Hub LLM/RAG corpus a chunking | Áno | Áno — exact Git corpus snapshot, byte read-back, deterministic Markdown chunking a rebuild validation | Nie — `RUNTIME-EVIDENCE.md` je `Pending`; Actions blocker #151 | Nie | [`labs/llm-rag/README.md`](labs/llm-rag/README.md) |
| Knowledge Hub LLM/RAG retrieval a answer lifecycle | Áno | Áno — deterministic BM25-v1 index/retrieval, explicitný `no_result`, exact chunk citations, bounded context a structured answer/abstention envelope | Nie — vykonaný izolovaný reconstruction 8/8 pred posledným dodatočným determinism testom; final source obsahuje 9 test cases a Actions blocker #151 | Nie | [`labs/llm-rag/RETRIEVAL-GROUNDED-ANSWER.md`](labs/llm-rag/RETRIEVAL-GROUNDED-ANSWER.md) |
| Knowledge Hub LLM/RAG eval, security a observability | Áno | Áno — exact implementation/corpus revision, bounded-context extractive adapter, direct/indirect injection gates, slice-based hard evals, prompt/config release, trace counters a bounded cleanup | Nie — PR #171 source/test inventory bez central Actions runu; blocker #151 | Nie | [`labs/llm-rag/EVAL-SECURITY-OBSERVABILITY.md`](labs/llm-rag/EVAL-SECURITY-OBSERVABILITY.md) |
| Keycloak-secured AI API | Áno | Áno na source úrovni — reproducible realm import, PKCE a Client Credentials contracts, exact issuer/audience/access-token/scope/azp/client-role validation, promoted RAG adapter, protected agent routes a optional promoted-RAG `knowledge_query` path do bounded agenta | Nie — bez authoritative live Keycloak end-to-end runu a kvôli Actions blockeru #151 | Nie | [`labs/keycloak-ai-api/README.md`](labs/keycloak-ai-api/README.md), [`labs/keycloak-ai-api/BOUNDED-AGENT-INTEGRATION.md`](labs/keycloak-ai-api/BOUNDED-AGENT-INTEGRATION.md) |
| Bounded incident/operations agent | Áno | Áno na source úrovni — durable workflow state, typed local inspection/restart tool, exact time-bounded action approval, one-mutation budget, bounded control-plane tool wait, idempotency/read-before-retry, hardened unknown-outcome handling, sandbox/allowlist/kill switch, promoted retrieval-context/injection boundary, strict typed tool-result boundary a deterministic hard eval pre trajectory/tool-selection/policy/completion/business outcome | Nie — PR #179 je source-merged ako `eff39d9d10110a5eb7fb30f0ae8c5ee3dddedc63`, ale corrected PR head aj merge commit nemajú Actions run/status; #151 a clean-checkout combined evidence zostávajú otvorené | Nie | [`labs/agent-ops/README.md`](labs/agent-ops/README.md), [`labs/agent-ops/RETRIEVAL-INJECTION-EVALUATION.md`](labs/agent-ops/RETRIEVAL-INJECTION-EVALUATION.md) |
| Unified Practical v1 runner/evidence | Áno | Čiastočne na source úrovni — lab index, status ledger, MLOps runtime harnesses, offline/core orchestrátor, repository-integrity validator, permanentná five-package CI matrix, root quick start a `PRACTICAL-V1-EVIDENCE.md` foundation | Nie — source surface ešte nemá executed central run; #151 | Nie | [`PRACTICAL-V1-EVIDENCE.md`](PRACTICAL-V1-EVIDENCE.md), [`README.md`](README.md), `scripts/practical_v1_core.py`, `.github/workflows/practical-v1-core.yml` |

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
- PR #164 — completed-retraining → immutable deployment → bounded canary routing handoff,
- PR #186 — executable local Docker containerized-inference runtime driver + hosted evidence workflow; source-merged bez executed runtime evidence,
- PR #187 — executable live-local-MLflow controlled-retraining runtime driver + hosted evidence workflow; source-merged bez executed runtime evidence.

Oddelené exact-source rekonštrukcie pred novými runtime harnessmi prešli 16/16 testami po Registry implementácii, 21/21 po training-lineage rozšírení, 29/29 po serving control-plane vrstve, 38/38 po HTTP serving source vrstve, 42/42 po live-canary vrstve, 13/13 pre monitoring/drift/approval, 16/16 pre controlled retraining executor a 7/7 pre post-retraining deployment handoff. Tieto historické počty patria samostatným validačným bodom; nepredstavujú jeden spoločný vykonaný repository run a neclaimujú nové testy z PR #186/#187.

Nové runtime harnesses pre containerized inference a live controlled retraining sú source-level executable. Ich contracty vyžadujú actual Docker alebo live local MLflow provider read-back, exact identity, refusal variants, replay/cleanup a canonical evidence. Kým GitHub nevytvorí workflow run, tieto požiadavky sú pripravený acceptance contract, nie vykonaný dôkaz.

Issue #151 je explicitný Practical v1 blocker pre central runtime closeout. Reproducer už nie je viazaný na starý MLOps workflow: established `practical-v1-core.yml` na `main` opakovane nevytvoril PR/push runy ani na explicitne matching paths. Rovnaký problém pokračoval na PR #186 a #187. Kým GitHub nevytvorí exact workflow run a jeho read-back, príslušné runtime states zostávajú `Nie`.

## LLM/RAG implementačné subjects

- PR #167 — exact Git corpus snapshot, per-file byte identity, workspace-independent snapshot ID, deterministic Markdown heading/code-fence chunking, per-chunk identity a deterministic full-manifest rebuild.
- PR #169 — deterministic offline lexical index, canonical query/result identity, explicitný `no_result`, exact retrieved citations, bounded context a structured answer/abstention envelope s deterministic retrieval read-backom.
- PR #171 — exact implementation-revision binding, code-defined system policy, bounded-context extractive adapter, direct/indirect prompt-injection policy, per-slice retrieval/citation/faithfulness/abstention/security gates, critical/high-risk release refusal, explicit corpus/index provenance, trace/token-equivalent evidence a bounded cleanup.

PR #167 obsahuje 17 test cases v source pre corpus/chunk positive a refusal contracts. Úspešný pytest/CI run sa neclaimuje, pretože Actions dispatch blocker #151 zostáva otvorený.

Pre PR #169 prešiel izolovaný exact-source reconstruction `compileall` + 8/8 tests pred pridaním posledného samostatného query/result determinism testu. Finálny merged source obsahuje 9 retrieval/answer test cases. Tento ledger preto neclaimuje `9/9`; rozlišuje vykonanú evidence od počtu testov prítomných vo final source.

PR #171 obsahuje 10 focused eval/security/observability test functions v source. Central pytest/CI run sa neclaimuje. Self-review pred merge odstránil raw-retrieval context bypass, stale release artifact, runtime-editable untested system policy, nejednoznačné no-result security dôvody, chýbajúcu implementation revision a chýbajúcu top-level corpus/index provenance.

`labs/llm-rag/RUNTIME-EVIDENCE.md` zostáva `Pending`. LLM/RAG source lifecycle je pre Practical v1 funkčne implementovaný na offline deterministic úrovni; otvorený zostáva central runtime closeout a voliteľné post-v1 generative/semantic adapters.

## Keycloak a agent implementačné subjects

- PR #173 — reproducible local realm, PKCE/public-client a service-account contracts, RS256/JWKS resource-server validation, exact audience a client-role boundary, secret hygiene a disposable cleanup contract.
- PR #174 — promoted RAG executor za Keycloak `rag.read` route, strict request/result schema, exact prompt/source identity a backend readiness/refusal boundary.
- PR #175 — bounded local incident-agent foundation: durable state, typed inspection/restart tool, exact policy/action approval binding, local idempotency, read-before-retry, unknown-outcome checkpoint, kill switch a replay without duplicate side effect.
- PR #177 — exact `knowledge-hub-api-access` scope enforcement, Keycloak-protected `agent.run`/`agent.remediate` integration, exact runtime filesystem sandbox, external approval preservation, fresh kill-switch read-back, strict tool-output boundary a explicit recovery checkpoint response.
- PR #178 — finite approval TTL pinning, server-side approval-time enforcement, one-mutation/resource policy bounds, bounded control-plane tool wait a refusal of `unknown_outcome + not_found` automatic retry.
- PR #179 — optional promoted-RAG `knowledge_query` pred `agent.run`, canonical retrieval context viazaný na plan identity, retrieved-injection abstention, core-level exact `restart_service` result schema, combined loopback runner a deterministic hard eval pre trajectory/tool-selection/policy/completion/business outcome.

Approval expiry a bounded tool-wait gate sú v #178 source-level implementované bez nepravdivého hard-cancellation claimu. Timeout znamená `unknown_outcome`; provider/tool môže stále dobehnúť a recovery musí použiť authoritative lookup. `not_found` po unknown outcome už nie je považovaný za dôkaz bezpečný pre retry.

PR #179 uzatvára source-level retrieval/injection a evaluation medzeru. Retrieved text je read-only evidence: `retrieval_context_id` vstupuje do `plan_id`, ale `action_digest` zostáva odvodený iba z typed `tool + target + arguments`. `abstained` promoted retrieval blokuje mutačný plan; malicious answered text nevie rozšíriť generation-1 tool authority. Plan bez retrieval contextu zachováva starú schema a identity. Remediation znovu validuje persisted retrieval context pred side effectom a strict tool-result schema odmieta prompt-like extra fields.

Source-level bounded-agent Practical v1 lifecycle je tým implementovaný. Otvorený zostáva central clean-checkout runtime evidence, live Keycloak + promoted RAG + agent execution path a user acceptance. External cryptographic approver identity, distributed locking, production credentials, hard remote cancellation a remote provider idempotency zostávajú mimo local Practical v1 reference implementation.

PR #177 zároveň doplnil scope gate, ktorý bol v realm confige pripravený cez default client scope `knowledge-hub-api-access`, ale resource server ho predtým iba parsoval. Scope je teraz samostatná authorization podmienka vedľa `azp` a client role. Central pytest/CI alebo live Keycloak run sa neclaimuje, pretože issue #151 zostáva otvorený.

## Practical v1 release-surface subjects

Aktuálny source-level release surface je tvorený:

- `scripts/practical_v1_core.py` — exact-order offline/core orchestrátor s clean tracked-worktree preflightom, fail-fast stage execution a canonical evidence ID,
- `scripts/validate_practical_v1_repo.py` — repository integrity pre tracked Markdown internal links, `labs/**/*.json`, five-package imports a zakázané tracked runtime/model artifacts,
- `scripts/tests/test_practical_v1_tools.py` — meta-contracty release tooling-u vrátane zero-stage refusal, stage order/cleanup a workroot boundary,
- `.github/workflows/practical-v1-core.yml` — SHA-pinned standalone five-package matrix, combined RAG/agent/Keycloak job a all-five-package offline orchestrator job,
- `.github/workflows/mlops-containerized-inference-runtime.yml` — hosted Docker/non-root/live-HTTP MLOps serving runtime harness,
- `.github/workflows/mlops-live-retraining-runtime.yml` — hosted drift/approval/live-MLflow/new-version/replay MLOps retraining runtime harness,
- root `README.md` — podporovaný Python 3.12 clean-checkout quick start a cleanup/read-back semantics,
- `PRACTICAL-V1-EVIDENCE.md` — súhrnný evidence ledger s existujúcim verified ML subjectom a explicitne pending ostatnými flagship/runtime gates.

Tento blok implementuje source contract pre roadmap položky „jeden orchestrátor“, „permanent CI matrix“, repository integrity a súhrnný evidence document. Roadmap hard checkboxes zostávajú otvorené, kým exact source neprejde executed gate-om a evidence sa nezapíše proti skutočnému runu. Issue #151 preto stále oddeľuje `Implemented` od `Runtime verified`.

## Dokumentačné sekcie a praktický stav

| Sekcia | Dokumentačný stav | Praktická interpretácia |
|---|---|---|
| 00–17 | `User reviewed` v aktuálnom dokumentačnom rozsahu | Neznamená automaticky vykonané laby ani runtime acceptance. |
| 18 — Machine Learning Fundamentals | `Ready for user review` | Flagship package je implementovaný a runtime verified; sekcia ako celok ešte nie je `User accepted`. |
| 19 — MLOps and ML Platforms | `Ready for user review` | Promotion, training lineage, Registry, serving/canary/rollback contracts, containerized-inference runtime harness, monitoring/drift/approval, controlled retraining executor, live-local-MLflow retraining harness a post-retraining handoff sú source-level implementované. Otvorené zostávajú executed central runtime evidence pre container/retraining, actual post-retraining container/canary chain, remote OCI/platform boundaries a user acceptance. |
| 20 — LLM and GenAI Engineering | `Ready for user review` | Offline Practical v1 source lifecycle od exact corpusu cez retrieval/citations po eval/security/promotion/trace/cleanup je implementovaný. Central runtime evidence zostáva `Pending` kvôli #151. |
| 21 — AI Agents and Intelligent Automation | `Ready for user review` | Practical v1 bounded-agent source lifecycle je implementovaný vrátane durable authority/state, time-bounded approval, resource/wait bounds, idempotency/recovery, Keycloak-protected routes, promoted retrieval/injection boundary a hard evaluation. Otvorený zostáva recorded clean-checkout runtime evidence, live combined identity path a user acceptance. |

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
