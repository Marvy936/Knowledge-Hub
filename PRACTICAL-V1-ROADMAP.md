# Knowledge Hub Practical v1 Roadmap

Tento dokument definuje minimálnu hranicu prvej použiteľnej praktickej verzie repozitára. V1 neznamená, že je implementovaný každý navrhovaný lab alebo každý produkt zo sekcií 00–21. Znamená, že používateľ vie z čistého checkoutu prejsť jeden prepojený, reprodukovateľný a evidence-driven lifecycle od dát a modelu cez MLOps, LLM/RAG, identitu a agentickú automatizáciu až po failure, recovery a cleanup.

## Stav

> **Practical v1: In progress**

Authoritative dokumentačný základ sekcií 00–21 je dokončený. Sekcie 00–17 sú `User reviewed`; sekcie 18–21 sú `Ready for user review`. Praktická v1 je samostatný runtime a release milestone. Release-candidate draft je v [`PRACTICAL-V1-RELEASE-NOTES.md`](PRACTICAL-V1-RELEASE-NOTES.md); nie je to vydaný release ani náhrada runtime evidence.

## Podporovaný v1 execution profile

Povinný core musí byť spustiteľný bez plateného cloudu a bez externého API key:

```text
Windows 11 + WSL2 alebo Linux
→ Docker/Compose pre lokálne služby
→ Python 3.12 pre deterministic lab tooling
→ CPU-only core path
→ disposable runtime state mimo Git history
```

Voliteľný cloud, GPU alebo komerčný model provider môže rozšíriť scenár, ale nesmie byť podmienkou základného CI ani reprodukovania v1 evidence.

## Dokončený základ

- [x] Authoritative dokumentácia sekcií 00–21.
- [x] Globálny ROADMAP bez nezaškrtnutých chapter topics.
- [x] Documentation learning-depth, glossary a navigation gates.
- [x] CKA timed lab sets a troubleshooting practice.
- [x] AWS CloudOps manual lab inventory.
- [x] Networking a ďalšie existujúce failure-oriented experimenty.
- [x] Machine Learning Fundamentals flagship lab.
- [x] ML runtime evidence: deterministic dataset, validation/leakage refusal, model comparison, threshold selection, package integrity, strict inference a cleanup.

Existujúce manuálne CKA a cloud laby sú súčasťou Knowledge Hubu, ale ich vykonanie na externom clustri alebo cloud účte nie je hard blockerom lokálneho Practical v1 release-u.

## Required for v1

### 1. MLOps flagship lifecycle

Cieľový lifecycle:

```text
ML artifact + dataset snapshot
→ immutable lineage a evaluation bundle
→ MLflow tracking a database-backed local Registry
→ exact registered model version a artifact read-back
→ immutable release manifest
→ containerized serving
→ controlled canary a rollback
→ monitoring a drift evidence
→ approval-gated retraining
```

Povinné bloky:

- [ ] Deterministic promotion foundation: workspace-independent candidate identity, strict contracts, compare-before-promote, stale refusal a immutable release manifest. Implementácia je zlúčená v PR #140; runtime evidence closeout zostáva otvorený.
- [ ] Lokálny MLflow Tracking Server s database-backed backendom a oddeleným artifact store pathom.
- [ ] Run, dataset, model a evaluation lineage zapísaná a prečítaná späť cez API.
- [ ] Registered model version, tags a mutable alias oddelené od immutable deployment identity.
- [ ] Fresh-environment model load a parity smoke test.
- [ ] Containerized inference service pinujúca exact release manifest/model digest.
- [ ] Dve serving generations a deterministic canary traffic test.
- [ ] Rollback na predchádzajúci release bez opätovného resolvovania mutable aliasu.
- [ ] Monitoring window s latency/error/prediction evidence a explicitným no-data stavom.
- [ ] Reproducible drift injection, true/false drift distinction a approval-gated retraining decision.
- [ ] Positive, forbidden, unknown-outcome, recovery a cleanup evidence.

### 2. LLM/RAG flagship nad Knowledge Hub dokumentáciou

Cieľový lifecycle:

```text
versioned documentation corpus
→ deterministic parsing a chunking
→ index generation
→ retrieval a reranking
→ grounded context assembly
→ structured answer s citations
→ eval-driven promotion
→ injection a data-boundary tests
```

Povinné bloky:

- [ ] Corpus snapshot viazaný na exact Git revision a file digests.
- [ ] Deterministic parser, chunk identity, metadata a index manifest.
- [ ] Retrieval s explicitným no-result stavom a bez predstierania odpovede.
- [ ] Citations viazané na exact source/chunk identity.
- [ ] Structured output schema a refusal nevalidného outputu.
- [ ] Versioned prompt/config generation.
- [ ] Eval dataset s retrieval, faithfulness, citation a abstention slices.
- [ ] Hard gate pre high-risk slices; aggregate score nesmie prekryť kritické zlyhanie.
- [ ] Direct a indirect prompt-injection testy nad nedôveryhodným dokumentom.
- [ ] Deterministic CI adapter bez externého API key; voliteľný reálny/local-model adapter je samostatná vrstva.
- [ ] Trace, latency, token/cost-equivalent counters a cleanup evidence.

### 3. Keycloak identity integration pre AI API

V1 nevyžaduje všetkých deväť navrhovaných Keycloak labov. Vyžaduje jeden integračný identity path, ktorý zabezpečí praktický LLM/agent API boundary:

```text
local Keycloak realm
→ public client s Authorization Code + PKCE
→ confidential service account
→ audience/scope/role claims
→ secured RAG/agent API
→ positive a negative authorization tests
```

Povinné bloky:

- [ ] Reproducible local Keycloak configuration a import generation.
- [ ] Browser/public-client PKCE flow contract.
- [ ] Service-to-service client credentials contract.
- [ ] Exact issuer, audience, scope a role validation v API.
- [ ] Refusal expired tokenu, wrong audience, missing scope a insufficient role.
- [ ] Secrets mimo Git history a redacted logs.
- [ ] Realm/config cleanup alebo disposable environment reset.

LDAP/AD federation, WebAuthn, identity brokering, HA, Operator a upgrade/DR rehearsal sú post-v1 rozšírenia.

### 4. Agentický flagship workflow

Cieľový scenár je lokálny incident/operations assistant, ktorý používa Knowledge Hub retrieval a sandboxed tools, ale nevlastní neobmedzenú remediation authority.

```text
incident evidence
→ retrieval a classification
→ bounded plan
→ typed tool proposal
→ human approval pri side effecte
→ idempotent sandbox execution
→ read-back verification
→ outcome alebo escalation
→ replay a audit
```

Povinné bloky:

- [ ] Durable workflow state oddelený od model conversation state.
- [ ] Typed tool contracts a explicitné identity/authorization boundaries.
- [ ] Idempotency key a read-before-retry pre side effects.
- [ ] Human approval viazaný na exact action digest a expiry.
- [ ] Sandbox, allowlist, time/resource limit a kill switch.
- [ ] Prompt-injection test cez retrieved content aj tool output.
- [ ] Unknown-outcome handling bez slepého retry.
- [ ] Trajectory, tool-selection, policy a business-outcome evaluation.
- [ ] Replay z checkpointu bez duplikácie side effectu.
- [ ] Positive, forbidden, recovery, escalation a cleanup evidence.

Live production remediation, široké cloud credentials, email/chat send authority a neobmedzené autonomous loops nie sú súčasťou v1.

### 5. Unified practical product surface

- [x] `labs/README.md` ako authoritative index existujúcich a v1 flagship labov.
- [x] Jednotný status ledger s rozlíšením `Documented`, `Implemented`, `Runtime verified`, `User accepted`.
- [ ] Jeden orchestrátor pre offline/core checks z čistého checkoutu.
- [ ] Permanent CI matrix pre ML, MLOps, LLM/RAG a agentické contracts.
- [ ] Interné linky, package imports, schemas a generated manifests validované v CI.
- [ ] Žiadne runtime artifacts, secrets, local databases alebo model bytes po cleanup-e v Git worktree.
- [ ] Runtime evidence dokument pre každý povinný flagship.
- [ ] Súhrnný `PRACTICAL-V1-EVIDENCE.md` viazaný na exact commit, workflow runs, dependency resolutions a proof boundaries.
- [ ] Root README quick start pre podporovaný v1 execution profile.
- [ ] Changelog/release notes a immutable Git tag `v1.0.0` až po finálnom acceptance gate. Release-candidate notes sú source-level pripravené v `PRACTICAL-V1-RELEASE-NOTES.md`; immutable tag zostáva zakázaný do finálneho acceptance gate-u.

## Hard v1 acceptance gates

Practical v1 možno označiť ako hotovú iba vtedy, keď súčasne platí:

1. Clean checkout vie spustiť core path podľa README bez ručných skrytých krokov.
2. Povinné CI gates prejdú na exact release candidate commite.
3. Každý flagship má positive, forbidden a recovery path; zelený happy path sám nestačí.
4. Každý externý alebo mutable pointer sa pred vykonaním side effectu resolvuje na immutable subject.
5. Retry, alias change, approval a rollback majú explicitnú generation/operation identity.
6. Missing telemetry sa nikdy neinterpretuje ako healthy alebo recovered stav.
7. Cleanup read-back potvrdí odstránenie disposable runtime state-u.
8. Evidence dokumenty neprekračujú to, čo run skutočne vykonal.
9. Sekcie 18–21 prejdú finálnym používateľským review alebo zostanú v release notes explicitne označené ako `Ready for user review`, nie `User accepted`.
10. V1 tag sa vytvorí až po finálnom repository-wide validation rune a kontrole výsledného diffu.

## Post-v1 backlog

Nasledujúce oblasti sú hodnotné, ale neblokujú prvý release:

- kompletný Keycloak lab/drill inventory,
- LDAP/AD, WebAuthn, brokering, multi-AZ a Operator,
- Kubeflow, KServe, SageMaker a distribuovaný/GPU training,
- reálny production dataset a business A/B experiment,
- viac model providerov, lokálny quantized serving a GPU performance matrix,
- n8n, Harness a ďalšie vendor-specific runtime laby,
- live cloud deployment a billing-dependent experiments,
- multi-agent scale, long-running production queues a autonomous remediation,
- production SLO, HA, DR a security certification.

## Odporúčané implementačné poradie

```text
MLOps foundation
→ MLflow Registry + artifact read-back
→ serving + canary + rollback
→ monitoring + drift + retraining
→ LLM/RAG corpus + retrieval
→ LLM eval + security + observability
→ Keycloak-secured AI API
→ agent workflow + approval + replay
→ unified runner + evidence closeout
→ user review + v1.0.0 release
```
