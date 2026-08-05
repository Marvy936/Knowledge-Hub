# Evaluation-driven automation lifecycle

Evaluation-driven automation premieňa kvalitu inteligentného workflowu z dojmu na versioned engineering contract. Nestačí otestovať, či model vytvorí peknú odpoveď. Produkčný systém musí hodnotiť celý path od vstupu cez retrieval, reasoning, tool selection, approvals a side effects až po authoritative business outcome. Eval je užitočný len vtedy, keď je jeho subject, dataset, grader, threshold a promotion decision reprodukovateľný a auditovateľný.

## 1. Business outcome

Cieľom evaluačného lifecycle je povoliť zmenu iba vtedy, keď preukázateľne zachová alebo zlepší definované user, service, security a business invarianty. Výsledkom nemá byť najvyššie aggregate score, ale dôveryhodné rozhodnutie promote, hold, rollback alebo retire.

Zmena, ktorá zlepší priemernú helpfulness a zároveň zhorší autorizáciu citlivých tool calls, je neprijateľná.

## 2. Exact evaluation subject

Evaluation subject nie je len názov modelu. Zahŕňa workflow commit, prompt digest, model a provider generation, tool schemas, connector versions, policy bundle, retrieval index, memory contract, runtime image, feature flags, dataset version, evaluator versions a execution environment.

Bez composed subject identity nemožno výsledok priradiť ku konkrétnemu kandidátovi ani neskôr reprodukovať.

## 3. Candidate a baseline

Každý experiment porovnáva explicitný candidate s pinned baseline. Baseline môže byť aktuálna produkčná generation, posledná schválená release alebo deterministic reference implementation.

„Novší model“ nie je baseline definícia. Ak sa zmení provider alias alebo index za behu experimentu, porovnanie je kontaminované.

## 4. Evaluation objective

Objective popisuje merateľný outcome a riziko, ktoré rozhodnutie pokrýva. Môže ísť o správnu klasifikáciu, grounded answer, autorizovaný tool call, idempotent side effect, bezpečné odmietnutie alebo úspešnú recovery.

Objective musí uviesť aj forbidden success. Napríklad ticket sa nesmie označiť za vyriešený iba preto, že workflow skončil bez exception.

## 5. System decomposition

Komplexný agent sa hodnotí na component, trajectory a end-to-end úrovni. Component eval izoluje retrieval alebo argument generation, trajectory eval skúma postup tool calls a end-to-end eval overuje skutočný business post-condition.

Jedna vrstva nemôže nahradiť ostatné. Správna finálna veta môže vzniknúť nesprávnym, privilegovaným alebo náhodným pathom.

## 6. Dataset authority

Dataset je governed artifact s ownerom, účelom, provenance, consent a retention pravidlami. Každý príklad má stable ID, source class, created-at, effective period, expected outcome, risk labels a reviewer evidence.

Dataset export bez provenance môže obsahovať stale policies, uniknuté secrets alebo produkčné dáta, ktoré sa nemali použiť na modelové hodnotenie.

## 7. Dataset generations

Zmena examples, labels, slices alebo sampling strategy vytvára novú dataset generation. Experimenty nad rozdielnymi generáciami sa nesmú porovnávať ako keby používali rovnaký benchmark.

Dataset version sa pinne rovnako ako source commit. „Latest eval set“ nie je reprodukovateľný input.

## 8. Representative distribution

Eval corpus obsahuje bežné prípady, hraničné prípady, high-risk prípady, adversarial vstupy, failures dependencies a historical incidents. Produkčný traffic distribution sa sleduje oddelene od kritických slices, ktoré môžu byť zriedkavé.

Priemer nesmie potlačiť scenár s malou frekvenciou a katastrofickým dopadom.

## 9. Slice taxonomy

Slices sa definujú podľa tenantov, jazykov, user rolí, action classes, resource criticality, input length, connectorov, policy paths a failure modes. Každý slice má minimum sample count a samostatný threshold.

Ak candidate dosiahne 98 % celkovo, ale 60 % pri cross-tenant authorization, promotion musí zlyhať.

## 10. Positive, negative a abstention cases

Positive cases overujú správnu akciu. Negative cases overujú, že systém neuskutoční forbidden mutation. Abstention cases skúmajú, či agent pri nedostatočných evidence zastaví, požiada o doplnenie alebo eskaluje.

V intelligent automation je správne „neviem“ často bezpečnejšie než sebavedomá odpoveď.

## 11. Adversarial corpus

Adversarial príklady zahŕňajú prompt injection, poisoned retrieval, tool-description manipulation, stale approval, ambiguous recipient, duplicate event, partial timeout, malicious attachment a cross-tenant identifier collision.

Red-team dataset sa nesmie používať iba na vývoj a následne vynechať z release gate.

## 12. Deterministic tests

Schema validation, exact identifiers, permissions, policy decisions, idempotency keys, state-machine transitions a ledger reconciliation sa hodnotia deterministic kódom. Modelový grader nie je vhodný na tvrdenie, že JSON schema, digest alebo authorization tuple je správny.

Tvrdé invarianty majú hard fail, nie vážený fuzzy score.

## 13. Model-based graders

LLM-as-judge je užitočný pre relevanciu, helpfulness, tone, groundedness alebo trajectory critique, kde neexistuje jeden exact string. Judge má pinned model, prompt, rubric, examples, sampling parameters a calibration dataset.

Judge explanation je evidence pre review, nie automatická pravda.

## 14. Judge independence

Target a judge by nemali zdieľať nekontrolovanú failure mode. Použitie rovnakej modelovej rodiny, rovnakého prompt template alebo rovnakého retrieval contextu môže vytvoriť correlated blind spot.

High-risk rozhodnutie kombinuje deterministic checks, ľudské labels a podľa potreby nezávislý modelový judge.

## 15. Human calibration

Human reviewers definujú rubriku, označia representative a disputed cases a pravidelne merajú agreement s automatickými gradermi. Reviewer identity, expertise, conflict of interest a label version sú súčasťou evidence.

Automated score sa nepoužíva ako release gate, ak sa jeho agreement s ľuďmi rozpadol pod schválený limit.

## 16. Inter-rater agreement

Subjektívne labels potrebujú viac než jedného reviewera alebo adjudication process. Disagreement môže odhaliť nejasnú rubriku, ambiguous example alebo reálny product trade-off.

Nízke agreement nie je „šum, ktorý treba spriemerovať“, ale finding o kvalite evaluácie.

## 17. Grader drift

Judge model, rubric prompt, policy, reference documents alebo parser sa môžu zmeniť. Každá zmena vytvára evaluator generation a vyžaduje revalidation proti frozen calibration setu.

Score trend bez pinnej evaluator generation môže byť zmena meradla, nie zmena produktu.

## 18. Metric portfolio

Kvalita sa meria portfóliom: correctness, safety, authorization, groundedness, tool selection, argument validity, side-effect integrity, latency, cost, abstention a business completion. Každá metrika má ownera a význam.

Composite score nesmie zakryť hard safety failure.

## 19. Threshold semantics

Threshold je decision policy, nie estetické číslo. Definuje minimum, confidence interval, allowed regression voči baseline, slice rules, hard blockers a treatment missing data.

No-data alebo príliš malý sample count je `insufficient_evidence`, nie pass.

## 20. Statistical uncertainty

Nondeterministické systémy potrebujú opakované runs a uncertainty bounds. Jediný run na example môže prehliadnuť variance alebo rare trajectory.

Promotion policy určuje repetitions, seeds, temperature, concurrency a minimálnu detekovateľnú regresiu.

## 21. Cost a latency

Eval meria nielen output quality, ale token use, tool count, wall time, retries, queue delay a external API cost. Candidate, ktorý mierne zvýši helpfulness a desaťnásobne zvýši cost alebo approval burden, môže byť prevádzkovo neprijateľný.

Cost optimization však nesmie odstrániť security checks alebo business verification.

## 22. Tool trajectory evaluation

Agentický path sa hodnotí podľa selected tool, poradia, arguments, authority, retries, stop condition a read-backu. Trajectory sa neakceptuje iba preto, že finálny output vyzerá správne.

Forbidden trajectory zahŕňa generic admin tool, mutation pred approvalom, blind retry a cross-tenant lookup.

## 23. Side-effect evaluation

Sandbox alebo controlled test environment musí zachytiť skutočné semantic side effects. Fake tool returning `success` nepreukazuje idempotency, provider behavior ani unknown-outcome recovery.

Test double musí explicitne modelovať accept-then-timeout, partial apply, stale generation a duplicate delivery.

## 24. Business post-condition

End-to-end eval končí domain read-backom: entitlement existuje, platba je zaúčtovaná raz, ticket má správneho recipienta, deployment obsluhuje traffic alebo credential rotation zachovala dependent services.

Workflow status ani model answer nie sú business oracle.

## 25. Offline evaluation

Offline eval používa curated dataset a pinned candidate pred promotion. Je vhodný pre regression, benchmarking, backtesting a failure injection, pretože môže používať reference outputs a kontrolované dependencies.

Offline pass však nepreukazuje produkčný distribution, permissions ani live connector behavior.

## 26. Shadow evaluation

Shadow režim spracuje kópiu produkčných vstupov bez mutation authority. Porovnáva decisions, tool plans, latency a abstention s active generation.

Shadow output sa nikdy nesmie dostať do downstream systemu iba preto, že candidate získal vysoké score.

## 27. Canary evaluation

Canary dostane malý, explicitne vybraný traffic slice a bounded capabilities. Promotion pokračuje iba po technických, safety a business checks počas stabilizačného okna.

Canary sample musí obsahovať minimálnu reprezentáciu kritických slices; čisto náhodný malý traffic ich môže úplne vynechať.

## 28. Online evaluation

Online eval hodnotí produkčné traces, user feedback, policy denials, tool outcomes a business results. Reference outputs často chýbajú, preto sa používa reference-free monitoring, deterministic invariants a sampled human review.

Online score je monitoring signal, nie automatická authorization na rozšírenie capability.

## 29. Sampling policy

Sampling sa definuje podľa risku, nie iba percenta trafficu. High-risk mutations, denials, unknown outcomes a new generations sa môžu hodnotiť na 100 %, kým low-risk read-only interactions sa vzorkujú.

Sampling po úspešnom completione vytvára survivorship bias a skrýva failed alebo dropped runs.

## 30. Production feedback loop

Negative feedback, incidents, policy escapes, human overrides a unexplained abstentions sa menia na reviewed dataset examples. Nový example má source evidence a neprepíše historical label bez versioningu.

Production log mining je vstup do governance procesu, nie automatické samoučenie.

## 31. Promotion gate

Promotion manifest viaže candidate, baseline, dataset, evaluators, results, waivers, reviewers a decision. Gate vyhodnotí hard invariants, per-slice thresholds, uncertainty, cost a known risks.

Manuálny override má ownera, expiry, scope a follow-up test. „Business needs it today“ nie je trvalý waiver.

## 32. Rollback gate

Rollback target je pinned a kompatibilný s data, policy a connector generations. Evaluačný lifecycle obsahuje rollback alebo compensation drill pred produkčným rolloutom.

Ak candidate vytvoril non-reversible side effect, model rollback nestačí; treba domain reconciliation.

## 33. Continuous evaluation

Každá významná zmena promptu, modelu, tool schema, policy, indexu, runtime alebo connectora spustí relevantný regression suite. Produkčné monitoring signals zároveň kontrolujú drift medzi releases.

Continuous eval neznamená neustále meniť thresholds podľa aktuálneho skóre.

## 34. Evaluation debt

Chýbajúce incident cases, stale labels, unowned metrics, flaky graders a nepinované datasets tvoria evaluation debt. Debt sa eviduje rovnako ako test alebo security debt.

Capability sa nerozširuje, ak debt zasahuje high-risk slice bez alternative controlu.

## 35. Evaluator security

Evaluator je aktívny software a môže byť napadnutý rovnakými vstupmi ako target. Modelový judge môže podľahnúť prompt injection z hodnoteného outputu, code grader môže spracovať nebezpečný payload a human review queue môže odhaliť citlivé dáta.

Evaluation runtime preto používa sandbox, minimálny network access, redaction, resource limits a oddelené credentials. Hodnotený text sa považuje za untrusted data, nie za instruction pre judge.

## 36. Experiment reproducibility

Experiment record obsahuje dataset order, repetitions, concurrency, cache policy, dependency snapshots, timestamps a randomization controls. Re-run sa označí ako nový experiment, aj keď používa rovnaký manifest.

Cache môže zrýchliť eval, ale musí byť keyed composed subjectom. Reuse outputu zo starého promptu alebo tool schema vytvára falošnú reprodukovateľnosť.

## 37. Waiver lifecycle

Known regression možno dočasne prijať iba explicitným waiverom s risk ownerom, affected slices, compensating controls, expiry a remediation issue. Waiver sa viaže na konkrétnu candidate generation.

Nový model, prompt alebo policy nesmie zdediť starý waiver automaticky. Expired waiver mení promotion decision na hold, nie na implicitné predĺženie.

## 38. Incident AGENT-EVAL-16

Candidate mení prompt, model a tool schema pre onboarding automation. Aggregate eval dosiahne 94 %, pretože dataset obsahuje veľa jednoduchých read-only otázok a iba dva service-principal cases.

Modelový judge z rovnakej rodiny označí oba risky outputs za „reasonable“, hoci jeden plánuje disable shared identity a druhý vynechá idempotency key.

## 39. False promotion

Release gate používa iba weighted average a nevyžaduje per-slice minimum. Candidate ide do canary, online evaluator vzorkuje iba completed runs a dropped traces sa neukladajú.

Prvý accept-then-timeout vytvorí onboarding side effect, retry ho zopakuje a monitoring stále ukazuje vysokú helpfulness.

## 40. Containment

Capability sa prepne do proposal-only režimu, mutation credentials sa zneplatnia a release sa označí `evaluation_invalid`. Presný candidate, dataset, grader outputs, traces a provider records sa zachovajú.

Threshold sa spätne neupraví tak, aby incident vyzeral ako očakávaný pass.

## 41. Recovery

Dataset dostane dedicated high-risk slices, timeout a duplicate cases. Deterministic graders overia identity UID, approval, operation ID, idempotency a business ledger. Judge sa rekalibruje proti human labels a canary sampling pokryje všetky mutations.

Duplicate onboarding operations sa zreconciliujú pred znovuotvorením capability.

## 42. Positive acceptance

Candidate prejde hard invariants, všetky critical slices, calibrated human agreement, cost a latency limits, shadow aj canary. Online evidence potvrdí technický a business outcome a incident replay nevytvorí duplicate side effect.

## 43. Forbidden acceptance

Aggregate score, benchmark rank, model confidence, judge agreement sám so sebou alebo absence alertu nesmú byť acceptance. Missing traces, unknown outcomes a insufficient samples nesmú byť premenené na zero failures.

## 44. Recovery acceptance

Po invalid eval sa opraví eval system aj product candidate. Druhý-operation test zopakuje accept-then-timeout, stale approval a cross-tenant case a musí skončiť reconcile alebo deny bez duplicate mutation.

Recovery sa neuzavrie iba novým promptom.

## 45. Practical evaluation manifest

Manifest oddeľuje subject, dataset, evaluators a decision. Hard gates nie sú miešané do jedného priemerného skóre a každá result generation je spätne dohľadateľná.

```yaml
evaluation:
  subject:
    workflow_commit: 8bba6ff080b6
    prompt_digest: sha256:prompt-v22
    model: provider/model@2026-08-01
    tool_catalog: onboarding-tools-v14
    policy_bundle: agent-policy-v31
    retrieval_index: support-index-v18
  baseline:
    release: onboarding-agent-2026.07
  dataset:
    id: onboarding-eval
    generation: 47
    slices:
      critical: [shared-identity, duplicate-event, stale-approval]
      representative: [faq, standard-onboarding, status]
  evaluators:
    deterministic: [schema, authorization, idempotency, ledger]
    judge: groundedness-judge-v8
    human_calibration: security-review-2026-08
  gates:
    hard_fail: [cross_tenant_access, unapproved_mutation, duplicate_side_effect]
    min_slice_pass_rate: 0.95
    max_baseline_regression: 0.01
    min_samples_per_critical_slice: 50
    on_missing_data: hold
  rollout:
    shadow_hours: 24
    canary_percent: 2
    mutation_sampling: 1.0
    stabilization_minutes: 30
```

Failure injection zmení judge model bez zmeny manifestu, odstráni failed traces zo sample a vráti provider timeout po accepted mutation. Správny lifecycle zablokuje comparison, označí evidence ako incomplete a vykoná ledger reconciliation.

## 46. Primary sources

NIST AI RMF a Generative AI Profile organizujú risk management cez Govern, Map, Measure a Manage a požadujú dokumentované test, evaluation, verification a validation procesy. LangSmith dokumentácia oddeľuje offline evaluation nad datasets od online evaluation nad production traces a opisuje human, code, model-based a pairwise evaluators.

OpenAI evaluation guidance odporúča task-specific evals, representative datasets, human calibration, logging a continuous evaluation. Aktuálna dokumentácia zároveň oznamuje, že legacy Evals platform prejde 31. októbra 2026 do read-only a 30. novembra 2026 sa má vypnúť; preto produktový endpoint nie je dlhodobou architecture authority a lifecycle musí mať portable datasets, graders a evidence.

## Zhrnutie

Evaluation-driven automation je release a operations discipline, nie dashboard so skóre. Pinned subject, authoritative datasets, independent graders, per-slice gates, failure injection, shadow, canary, online monitoring, human calibration a business read-back spolu rozhodujú, či sa capability môže rozšíriť.

Nasledujúca kapitola uzavrie sekciu systematickým troubleshootingom inteligentnej automatizácie.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Autonomous remediation boundaries](autonomous-remediation-boundaries.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Intelligent automation troubleshooting →](intelligent-automation-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
