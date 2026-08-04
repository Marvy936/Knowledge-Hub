# LLMOps a production readiness

LLMOps je operational discipline pre zostavenie, promotion, deployment, monitoring, recovery a continuous improvement LLM application. Neoperuje iba modelom. Produkčný behavior vzniká z model snapshotu, promptu, retrieval corpus/indexu, tools, schemas, gateway route, guardrails, privacy controls, media preprocessing, cache generations, eval datasets, infrastructure a application code. Production readiness preto patrí composed release-u, nie jednému model endpointu.

V incidente `GENAI-SUPPORT-09` release zmenil multimodálny model, image detail policy, audio downmix, moderation thresholds a provider background mode. Pipeline evidovala iba application image tag a model alias, takže canary porovnával neúplné generations. Overall success rate sa zlepšil, ale regulated identity segment začal vytvárať nesprávne refund decisions a raw media zostávali dlhšie než privacy contract. Rollback vrátil model alias, no nie preprocessing, guardrail, cache ani retention features, preto incident pokračoval.

## 1. Exact production release

Každá runtime operation sa viaže na immutable composed release manifest. Manifest rozlišuje intended release, resolved dependencies a loaded state.

```yaml
llm_release:
  release_id: support-release-2026-08-04.10
  application_image: sha256:app91...
  model_snapshot: model-2026-07-15
  adapter: none
  prompt_release: support-prompt-v22
  gateway_policy: support-route-v14
  retrieval_corpus: support-corpus-g184
  index_generation: hybrid-index-g91
  tool_catalog: support-tools-v17
  tool_schemas: tools-schema-v17
  guardrail_release: support-safety-v15
  privacy_profile: eu-zdr-v4
  media_preprocessing: media-pipeline-v18
  cache_generation: support-cache-g77
  eval_suite: support-prod-gate-v31
  infrastructure: prod-eu-stack-204
```

Mutable aliases môžu slúžiť ako promotion pointers, ale runtime trace zapisuje resolved immutable IDs a digests. Inak sa incident nedá reprodukovať a rollback nevie, čo presne má obnoviť.

## 2. Business outcome pred technológiou

Production readiness začína explicitným business outcome-om a harm boundary. „Nasadiť chatbot“ alebo „použiť nový model“ nie je acceptance criterion.

```yaml
business_contract:
  outcome: resolve-supported-refund-cases
  success_metric: accepted_resolution_rate
  forbidden_outcomes:
    - refund_wrong_customer
    - disclose_cross-tenant-data
    - execute_without-required-approval
  max_case_cost_eur: 0.12
  p95_latency_ms: 6000
  escalation_target: human-support
```

Technical metrics sa mapujú na tento contract. Nízka latency nie je úspech, ak systém rýchlejšie vykonáva nesprávne business action.

## 3. Ownership model

Každý release má business ownera, application ownera, model/prompt ownera, data ownera, security/privacy ownera a on-call. Shared responsibility bez explicitného decision ownera vedie k incidentom, ktoré každý považuje za problém iného tímu.

RACI alebo obdobný model určuje, kto môže promotion schváliť, kto môže aktivovať kill switch a kto uzatvára business recovery. Vendor support môže pomôcť s provider incidentom, ale nemá authority nad zákazníckym tool side effectom.

## 4. Lifecycle

LLMOps lifecycle spája scoping, design, build, evaluation, approval, deployment, operation a retirement. Každá fáza vytvára artifacts a evidence pre nasledujúci gate.

```text
business scope
→ threat/privacy/data design
→ versioned implementation
→ offline eval a integration tests
→ release review
→ shadow/canary deployment
→ business verification
→ continuous monitoring
→ incident learning
→ controlled retirement
```

Lifecycle nie je lineárny waterfall. Produkčný feedback a incidents vytvárajú nové eval cases, policy rules a architecture decisions, ale zmeny sa vracajú cez rovnaké promotion gates.

## 5. Environment boundaries

Development, test, staging a production majú oddelené credentials, data, registries a tool endpoints. Production prompt alebo provider project sa netestuje manuálne z developer notebooku s broad tokenom.

Staging musí byť behaviorally representative, no nesmie kopírovať production PII bez purpose a minimization. Environment parity sa definuje explicitne; differences ako fake tools alebo menší model sa zaznamenajú ako validation limits.

## 6. Artifact registries

Model registry sám nestačí. LLM application potrebuje prompt registry, corpus/index registry, tool/schema catalog, guardrail policy registry, eval dataset/grader registry a release manifest registry.

Artifact má immutable version, digest, owner, provenance, compatibility metadata a lifecycle state. Promotion pointer sa mení compare-and-swap operáciou, aby concurrent releases neprepísali jeden druhého.

## 7. Source of truth

Declarative repository alebo authoritative registry drží desired state. Console edits a ad hoc provider configuration vytvárajú drift, pokiaľ sa neimportujú späť alebo explicitne zakážu.

```text
reviewed desired state
→ rendered provider/application config
→ deployment
→ loaded-state read-back
→ drift comparison
```

Source of truth neznamená, že Git commit je produkčný dôkaz. Runtime musí preukázať, že exact commit a dependencies boli skutočne načítané.

## 8. Dependency resolution

Model alias, latest prompt, current corpus alebo default guardrail sú mutable dependencies. Release builder ich resolve-ne na immutable subjects pred approval.

Dependency lockfile obsahuje provider model snapshot, tokenizer/template, tool versions, region, endpoint capabilities a pricing generation. Ak dependency nemožno pin-nuť, release uvádza uncertainty, monitoring a emergency response pre provider-side change.

## 9. CI pre deterministic surfaces

CI najprv overuje surfaces, ktoré môžu byť deterministic: schemas, prompt variables, config syntax, links, policy rules, IaC, migrations, tool contracts a data manifests. Tieto chyby netreba odkladať na expensive LLM eval.

Static checks nepreukazujú behavior quality. Sú prvým gate-om, ktorý odstraňuje známe configuration a contract failures pred model invocation.

## 10. Behavioral test pyramid

LLM test pyramid kombinuje deterministic tests a statistical evals. Nižšie vrstvy sú rýchle a presné; vyššie vrstvy sú drahšie a bližšie business outcome-u.

```text
static/config/schema tests
→ unit tests s mocked model/tool
→ component evals pre prompt/retrieval/model
→ integration tests s real providers
→ adversarial/security/privacy tests
→ load/cost/recovery tests
→ shadow/canary business verification
```

Jeden offline average score nemôže nahradiť integration, operational a recovery evidence. Každý gate odpovedá na inú failure hypothesis.

## 11. Eval suite ako release dependency

Eval dataset, grader, rubric, repetition policy a aggregation sú versioned dependencies. Release verdict bez ich generations nie je reprodukovateľný.

Eval suite obsahuje baseline, target thresholds, hard forbidden gates, segment requirements a uncertainty method. High-risk failure sa nesmie spriemerovať s veľkým počtom easy cases.

## 12. Change-impact analysis

Každá zmena určí affected surfaces. Prompt edit môže zmeniť tool selection, token cost a safety; corpus update môže zmeniť factuality a privacy; provider route môže zmeniť retention a regional processing.

```yaml
change_impact:
  changed: [media_preprocessing]
  required_tests:
    - multimodal-identity-eval
    - prompt-injection-media-eval
    - privacy-retention-check
    - latency-load-test
    - rollback-replay
```

Pipeline nevyberá tests iba podľa file path. Dependency graph mapuje artifact na behavioral risks a required evidence.

## 13. Release gates

Gate má machine-checkable inputs, threshold a authority. „QA sa na to pozrela“ nie je auditovateľný verdict.

```yaml
promotion_gate:
  required:
    schema_tests: pass
    critical_eval_failures: 0
    high_risk_segment_lower_bound: ">= 0.97"
    p95_latency_ms: "<= 6000"
    cost_per_accepted_case_eur: "<= 0.12"
    privacy_policy: pass
    rollback_drill: pass
  approvers:
    - product-owner
    - security-owner
```

Exception má expiry, compensating controls a rollback trigger. Permanent waiver bez ownera sa stáva neviditeľným policy downgrade-om.

## 14. Security a privacy gates

Security gate testuje prompt injection, tool abuse, cross-tenant access, secret exposure, schema smuggling, egress a excessive agency. Privacy gate overuje provider product, endpoint, region, retention-compatible features, telemetry capture a deletion semantics.

Tieto gates používajú exact composed release. Testovať prompt injection bez reálnych tools alebo privacy bez zapnutého background mode nevytvára validnú production evidence.

## 15. Load a capacity testing

Load test používa open-loop arrival pattern, realistic input lengths, media sizes, tool latency a retry behavior. Closed-loop test s malým concurrency môže zakryť queue growth a overload collapse.

Metrics zahŕňajú TTFT, inter-token latency, end-to-end latency, queue time, tokens/s, tool latency, timeout rate, cache hit, cost a accepted outcome. Capacity verdict uvádza sustainable load a overload behavior, nie iba peak throughput.

## 16. Cost gate

Cost sa meria per attempt, operation a accepted business outcome. Retry, fallback, retrieval, moderation, tools, media preprocessing a human review patria do complete cost.

Lacnejší model môže zvýšiť escalation a rework. Cost optimization preto používa paired quality/cost eval a segment constraints, nie najnižšiu cenu za input token.

## 17. Shadow deployment

Shadow traffic kopíruje production input do candidate release bez ovplyvnenia user outcome alebo side effects. Sensitive content sa nesmie kopírovať do iného provider/regionu bez privacy authority.

Shadow output sa porovná s production behaviorom a neskorším outcome-om. Tool calls sú simulované alebo policy-blocked; inak shadow nie je read-only experiment.

## 18. Canary deployment

Canary pošle obmedzený traffic na candidate release a má explicitný exposure budget. Selection pokrýva risk segments, nie iba náhodný percentuálny sample.

```yaml
canary:
  traffic: 5%
  segments:
    - language: sk
    - modality: image+audio
    - risk: regulated-identity
  abort_on:
    forbidden_outcome: "> 0"
    p95_latency_regression: "> 20%"
    cost_regression: "> 15%"
```

Canary sa nepromuje automaticky len preto, že error rate je nízky. Potrebuje delayed business outcome a segment completeness.

## 19. A/B test boundary

A/B test optimalizuje preference alebo business metric medzi releases, ktoré už prešli safety a correctness gates. Nie je vhodný na zisťovanie, či variant porušuje privacy alebo vykonáva unauthorized actions.

Experiment assignment, exposure, metric a stop rules sú versioned. User harm alebo forbidden outcome okamžite ukončí variant bez čakania na statistical significance.

## 20. Runtime configuration read-back

Po deployment-e system prečíta loaded model, prompt digest, route, corpus/index generation, tool catalog, guardrails, privacy profile a media preprocessing. Read-back sa porovná s manifestom.

Health endpoint, trace alebo synthetic request musí identifikovať loaded release. Pod readiness gate-om sa nesmie skrývať stav „process beží, ale používa starý prompt cache“.

## 21. Configuration drift

Drift vzniká console editom, provider default change, stale cache, partial deployment alebo manually rotated secretom. Drift detector porovná desired a effective state a klasifikuje impact.

High-risk drift vyvolá fail-safe, rollback alebo traffic isolation. Automatická remediation sa používa iba tam, kde je recovery bezpečná; neznámy provider change môže vyžadovať human decision.

## 22. Feature flags

Feature flag je behavior dependency. Flag pre web search, background mode, new tool, high image detail alebo relaxed moderation mení security, privacy, cost a quality.

Flags sú tenant- a environment-scoped, versioned a zahrnuté v trace. Emergency kill switch je oddelený od experiment flagu a má tested propagation time.

## 23. Observability

Production trace spája operation, attempts, retrieval, caches, model calls, tools, guardrails, user delivery a business outcome. Každý span nesie release ID a resolved component generations.

Telemetry je privacy-minimized a sampling-aware. Alerty zahŕňajú technical health, behavior quality, safety, privacy, cost a business KPIs; samotný HTTP 200 rate nie je production health.

## 24. SLI, SLO a error budget

SLI sa viaže na user alebo business outcome: accepted resolution rate, grounded answer rate, correct abstention, unauthorized-action rate, p95 latency a cost. SLO definuje target a evaluation window.

Error budget spája reliability a change velocity. Forbidden security alebo privacy outcome môže mať nulový budget a okamžitý stop, zatiaľ čo mierny latency regression môže spotrebúvať klasický budget.

## 25. Delayed outcomes

Mnohé failures sa objavia až po hodinách alebo dňoch: refund chargeback, user correction, human escalation alebo deletion failure. Operation record preto zostáva joinable s delayed business events bez uchovávania unnecessary raw contentu.

Promotion window musí byť dostatočne dlhý pre relevantný outcome. Early canary success nie je acceptance, ak rozhodujúci signal ešte nemohol prísť.

## 26. On-call a runbooks

On-call potrebuje runbook podľa symptomov a first-divergence hypotheses. Runbook obsahuje dashboards, queries, kill switches, fallback modes, rollback manifests, business containment a escalation contacts.

Runbook sa testuje v game day alebo incident drill-e. Dokument, ktorý nikto nevie vykonať s aktuálnymi permissions, nie je operational evidence.

## 27. Incident classification

Incident sa klasifikuje podľa confidentiality, integrity, availability, safety, privacy, cost a business impact. Model hallucination môže byť nízky content-quality issue alebo critical financial incident podľa downstream authority.

Severity sa neurčuje podľa počtu 500 errors. Jediný cross-tenant disclosure alebo unauthorized payment môže mať vyššiu závažnosť než rozsiahly read-only outage.

## 28. Containment modes

Prepared containment zahŕňa stop traffic, disable tool, read-only mode, remove retrieval source, force abstention, route to human, pin alternate model alebo queue requests. Každý mode má privacy, capacity a user-experience boundary.

Kill switch musí fungovať bez závislosti od failing model alebo orchestration layer. Propagation sa meria a testuje; dashboard toggle bez loaded-state verification nestačí.

## 29. Rollback

Rollback obnoví celý composed release alebo explicitne compatible subset. Vrátiť iba model alias je nebezpečné, ak prompt, schema, tools, corpus alebo guardrails zostali na novej generation.

```text
select known-good manifest
→ apply immutable dependencies
→ invalidate caches
→ verify loaded state
→ replay incident + controls
→ gradually restore traffic
```

Rollback evidence zahŕňa business read-back. Ak release už vykonal side effects, samostatná compensating recovery opraví data alebo transakcie.

## 30. Forward fix versus rollback

Rollback je preferovaný, keď known-good release existuje a compatibility je zachovaná. Forward fix sa používa, keď rollback by obnovil kritickú zraniteľnosť, provider už starý model neponúka alebo data migration nie je reversible.

Decision record uvádza riziká, authority a time budget. Incident pressure nesmie viesť k neoverenému prompt patchu priamo v production console.

## 31. Provider outage a fallback

Fallback candidate musí spĺňať schema, tool, safety, privacy, region, latency a quality compatibility. Availability-only routing na „akýkoľvek model“ môže zmeniť behavior a compliance.

Fallback matrix je versioned a pravidelne testovaný. Ak compatible model nie je dostupný, application použije degraded mode alebo queue namiesto unsafe substitution.

## 32. Vendor portability

Portability sa navrhuje na úrovni application contractu, nie najmenšieho spoločného API denominatora. Provider adapters mapujú message roles, tools, schemas, usage, errors a safety signals do canonical modelu.

Nie všetky capabilities sú portable. Release evidence explicitne uvádza provider-specific features a exit plan; fake portability bez parity evalov iba presúva incident na deň migrácie.

## 33. Data a index operations

Corpus update, re-embedding a index rebuild sú production releases. Blue/green index alebo immutable generation umožní canary a rollback bez partial mixture.

Data quality gates overujú ACL, tenant, freshness, duplicates, parsing a chunking. Index ready status sa overí query-based acceptance, nie iba completed build jobom.

## 34. Cache operations

Prompt, semantic a response caches majú generation viazanú na model, prompt, corpus, schema, tenant a security context. Release invaliduje alebo oddelí incompatible entries.

Cache warm-up nesmie použiť production sensitive data bez authority. Rollback musí obnoviť compatible cache generation alebo bezpečne začať cold, nie zdieľať výsledky medzi releases.

## 35. Secrets a credentials

Secrets sa referencujú cez secret manager a short-lived workload identity, nie v prompt registry alebo release manifest value. Manifest obsahuje secret reference generation a required scopes.

Rotation sa testuje bez downtime a stale workerov. Tool executor musí používať task-scoped permissions; model nikdy nedostane raw credential.

## 36. Human operations

Human review queue, escalation a override sú production components s capacity, SLA a quality metrics. Náhly model regression môže zaplaviť queue a vytvoriť secondary outage.

Override má reason, authority, expiry a audit. Operator nesmie obísť tenant alebo privacy boundary iba preto, že AI označila case ako urgentný.

## 37. Continuous improvement

User feedback, corrections, escalations a incidents sa triage-nu na prompt, retrieval, model, tool, policy alebo UX causes. Nie každý negatívny feedback sa má automaticky pridať ako training example.

Approved learning artifacts prechádzajú privacy a leakage review a vstupujú do versioned eval alebo training datasetu. Improvement loop zostáva kontrolovaný release process, nie online self-modification bez gate-u.

## 38. Decommissioning

Retirement odstráni traffic, aliases, credentials, provider projects, files, caches, vector stores, dashboards a on-call obligations. Data retention a deletion pokračujú aj po vypnutí endpointu.

Decommission record uvádza replacement, residual risks a evidence o odstránení resources. Zombie prompt, tool alebo provider key je security a cost risk, aj keď application už nemá používateľov.

## 39. Production readiness review

Readiness review je evidence-based decision nad exact release. Zahŕňa business, architecture, data, model, security, privacy, reliability, performance, cost, operations a recovery.

```yaml
readiness_verdict:
  release_id: support-release-2026-08-04.10
  functional_eval: pass
  forbidden_outcomes: 0
  security_review: pass
  privacy_review: pass
  capacity_test: pass
  cost_gate: pass
  rollback_drill: pass
  runbook_drill: pass
  loaded_state_verified: true
  decision: canary-approved
```

`canary-approved` nie je `production-stable`. Stav sa mení až po controlled exposure a outcome evidence.

## 40. Failure hypotheses

Pri produkčnom regresse sa drží viacero hypotheses, pretože LLM behavior vzniká z composed systemu.

- **Wrong release resolution** — alias alebo dependency sa resolve-li na neočakávaný model, prompt, corpus alebo policy.
- **Partial deployment** — niektoré instances používajú starú generation alebo stale cache, čo vytvára bimodal behavior.
- **Provider-side change** — model, safety filter, quota alebo endpoint semantics sa zmenili bez customer deploymentu.
- **Data/index drift** — corpus, ACL alebo parser zmenili evidence dostupné modelu.
- **Tool/business failure** — model output bol správny, ale tool retry, authorization alebo downstream state zlyhali.
- **Segment regression** — overall metrics sú stabilné, no konkrétny jazyk, modality, tenant alebo risk tier sa zhoršil.
- **Privacy/config drift** — feature flag alebo provider mode zmenili retention, region alebo telemetry behavior.
- **Capacity collapse** — queue, rate limit alebo retry storm zmenili fallback a timeout behavior.

Incident commander nevyberá root cause podľa najhlasnejšieho dashboardu. Trace, loaded state, replay a business read-back určia first divergence.

## 41. Containment a recovery

Containment zastaví ďalší harm pomocou pripraveného mode-u a zachová evidence. Traffic sa môže izolovať podľa tenant, route, modality alebo tool, aby sa neodstavila bezpečná časť systému.

Recovery použije known-good manifest alebo reviewed forward fix, overí loaded state, replay-ne incident a controls a obnovuje traffic postupne. Po technickom recovery sa dokončia business, privacy a security remediation tasks.

## 42. Acceptance

Pozitívna acceptance preukazuje požadovaný business outcome, quality, latency, cost a operational health pre reprezentatívne segments. Forbidden acceptance preukazuje nulový unauthorized side effect, cross-tenant disclosure a policy-incompatible provider behavior.

Recovery acceptance dokazuje rollback alebo degraded mode pod reálnou dependency failure. Second-change test nasadí malú ďalšiu zmenu a overí, že pipeline, registries, loaded-state read-back a monitoring stále fungujú po prvom release-i.

## 43. Čo dokumentačná validácia nepreukazuje

Repository checks môžu overiť manifests, links, prose model a static contracts. Nepreukazujú provider behavior, offline eval results, load capacity, canary outcome, on-call readiness ani rollback execution.

Runtime `Verified` vyžaduje vykonané gates a read-back pre exact release. Produkčný `Stable` stav vyžaduje časové evidence z prevádzky, business outcomes, incidents a úspešné recovery drills; user `Accepted` vyžaduje explicitný owner alebo stakeholder verdict.

## Primárne zdroje

- [AWS Well-Architected Generative AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html)
- [AWS Generative AI Lens — operational excellence](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/operational-excellence.html)
- [AWS Generative AI lifecycle](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lifecycle.html)
- [AWS Agentic AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html)
- [NIST AI RMF Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)

## Kontrolné otázky

1. Ktorý immutable composed release manifest vytvoril konkrétny production behavior?
2. Ako sa resolved dependencies a loaded runtime state porovnávajú s desired state?
3. Ktoré deterministic, behavioral, security, privacy, load, cost a recovery gates blokujú promotion?
4. Pokrýva canary high-risk segments a delayed business outcomes, alebo iba náhodný traffic a HTTP errors?
5. Vracia rollback model, prompt, corpus, tools, guardrails, privacy, preprocessing a cache ako compatible celok?
6. Aký degraded mode sa použije, keď neexistuje behaviorally a privacy-compatible fallback?
7. Ktoré artifacts, credentials a data stores sa odstránia pri decommissioningu?

## Navigácia

- Predchádzajúca kapitola: [Multimodal models](multimodal-models.md)
- Späť na sekciu: [LLM and GenAI Engineering](README.md)
- Nasledujúca kapitola: [LLM application troubleshooting](llm-application-troubleshooting.md)
