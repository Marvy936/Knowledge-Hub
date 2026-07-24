# Progressive delivery

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Progressive delivery je riadený release systém, ktorý oddeľuje deployment od expozície a rozširuje zmenu po krokoch na základe produkčnej evidence. Spája immutable artifacts, canary alebo ring cohorts, feature flags, observability, policy-driven analysis a recovery do jednej state machine.

```text
artifact prepared
→ deployed with bounded exposure
→ evidence collected
→ promote / pause / abort / inconclusive
→ next step
→ intended release state
→ delayed validation
→ cleanup and closure
```

Nie je to jediná deployment technika. Je to orchestration a decision model nad viacerými technikami.

## 2. Nezávislé osi promotion

Progressive delivery môže riadiť oddelene:

- **Artifact promotion —** ktorý digest je nasadený.
- **Environment promotion —** kde artifact beží.
- **Traffic promotion —** aký podiel requests smeruje na novú generation.
- **Audience promotion —** ktoré rings, tenants alebo clients sú eligible.
- **Feature promotion —** ktorý runtime behavior je aktívny.
- **Data migration promotion —** ktorá read/write cesta je autoritatívna.
- **Release acceptance —** či sa zmena považuje za prijatú a podporovanú.

Ak tieto osi nie sú korelované, napríklad traffic je 100 %, ale feature iba 10 %, telemetry a recovery sa ľahko interpretujú nesprávne.

## 3. Mental model: rollout controller nad desired a observed state

Controller porovnáva:

```text
desired rollout state
vs.
observed deployment, exposure, evidence and recovery state
```

A vykonáva ďalší bezpečný transition. Controller nie je iba timer; je to privilegovaný production control plane s právom meniť traffic, flags, deployments a niekedy data migration fázu.

## 4. Progressive delivery contract

Každý rollout potrebuje:

- release/artifact digest,
- config a infrastructure revision,
- target environment,
- rollout strategy a steps,
- cohort/membership definition,
- feature a data-migration state,
- promotion, abort a inconclusive rules,
- evidence sources a queries,
- minimum sample a observation durations,
- maximum blast radius,
- recovery hierarchy,
- ownera, approvals a expiry,
- cleanup a final-state definition.

Contract musí byť versionovaný a viazaný na immutable subject.

## 5. Rollout state machine

```text
planned
→ prechecks
→ deployed, no exposure
→ step active
→ evidence collecting
→ evaluating
→ progressing / paused / aborted / inconclusive
→ next step alebo recovery
→ full exposure
→ delayed validation
→ accepted
→ cleanup
→ closed
```

Stavy `paused`, `inconclusive` a `cleanup pending` sú prvotriedne, nie iba textové poznámky.

## 6. Preconditions

Pred prvým krokom over:

- artifact/provenance a required gates,
- environment baseline health,
- config/flag/data compatibility,
- version-level telemetry,
- cohort routing correctness,
- recovery eligibility,
- controller permissions a health,
- rollout lock,
- error-budget a incident stav,
- on-call a support readiness.

## 7. Strategy composition

Príklady skladania:

```text
shadow
→ canary within ring 0
→ ring 1
→ ring 2 with feature flag at 10 %
→ full artifact exposure
→ feature full exposure
```

Kompozícia zvyšuje kontrolu, ale aj stavový priestor. Každý control plane musí mať spoločný rollout ID a konzistentný desired state.

## 8. Risk classification

Risk môže zohľadniť:

- business criticality,
- IAM/security zmenu,
- databázové a event mutations,
- reversibility,
- blast radius,
- novelty,
- dependency scope,
- test evidence,
- observability quality,
- incident history,
- client/server skew.

Risk class určuje veľkosť krokov, automation level, observation duration a approval.

## 9. Evidence model

Evidence zahŕňa:

- pre-release test a security results,
- artifact signature/provenance,
- deployment verification,
- technical SLIs,
- functional synthetics,
- business outcomes,
- security/data invariants,
- sample completeness,
- support/user signals,
- compatibility a migration state.

Každá evidence položka potrebuje subject identity, timestamp, source a freshness pravidlo.

## 10. Technical, functional a business validation

Technický pass nestačí. Príklad:

```text
error rate stable
latency stable
checkout completion -8 %
```

Rollout môže byť technicky zdravý a produktovo neúspešný. Naopak, business metric môže krátkodobo rásť pri neprijateľnej fraud alebo reliability regresii.

## 11. Sample a observation contract

Každý krok definuje:

- minimálny count relevantných events,
- minimálnu duration,
- maximálnu duration,
- delayed outcome horizon,
- cohort comparability,
- metrics completeness,
- stable baseline interval.

Percento trafficu ani fixných desať minút nie sú univerzálnym dôkazom.

## 12. Promotion verdicts

- **Promote —** required evidence je úplná a policy splnená.
- **Pause —** treba zachovať scope a manuálne alebo automaticky vyšetrovať.
- **Abort —** guardrail je porušený alebo risk je neprijateľný.
- **Inconclusive —** dôkaz nestačí alebo nie je porovnateľný.
- **Invalid —** subject, cohort, config alebo experiment setup nezodpovedal contractu.

## 13. Missing a delayed telemetry

Policy určuje:

- ktoré signály fail closed,
- maximum data lag,
- minimum completeness,
- správanie pri query error,
- rozdiel medzi nulou a missing data,
- fallback analysis,
- ownera analytics dependency.

Controller nesmie promotionovať preto, že monitoring prestal fungovať.

## 14. Automated analysis

Môže používať:

- absolútne thresholds,
- delta voči control,
- SLO burn,
- trends,
- anomaly detection,
- confidence alebo Bayesian rule,
- hard business/security invariants.

Model musí byť vysvetliteľný, versionovaný a testovaný na historických rolloutoch. Composite score nesmie skryť kritický invariant.

## 15. Control group a attribution

Canary alebo ring evidence potrebuje porovnateľnú baseline. Koreluj:

- artifact/version,
- cohort,
- region/zone,
- config/flags,
- route/workload,
- rollout step,
- concurrent changes.

Súbežná environment alebo dependency zmena môže verdict invalidovať.

## 16. Manual checkpoints

Ľudské rozhodnutie je vhodné pri:

- neautomatizovateľnej business/ethical evidence,
- vysokom nevratnom dopade,
- regulácii,
- inconclusive signále,
- emergency risk acceptance.

Approval musí byť naviazaný na aktuálny subject a evidence; nový digest, config alebo stale window ho invaliduje.

## 17. Error budgets a incident state

Policy môže meniť rollout:

```text
healthy budget
→ normal progression

high burn / active incident
→ smaller steps, pause alebo freeze
```

Freeze sa má viazať na user-facing reliability a recovery capacity, nie na všeobecnú averziu k zmene.

## 18. Recovery hierarchy

Od najmenej invazívnej akcie:

1. zastaviť promotion,
2. znížiť exposure,
3. vypnúť feature/migration path,
4. route na stable target,
5. rollback config/artifact,
6. roll-forward fix,
7. compensating action,
8. data repair alebo restore.

Správna vrstva závisí od toho, čo sa už zmenilo v mutable state.

## 19. Shared-state compatibility

Progressive rollout predlžuje overlap. Potrebuje:

- expand-contract DB schema,
- tolerant events,
- cache/session versioning,
- backward-compatible clients,
- idempotent writes,
- feature cleanup až po rollback window,
- explicitnú compatibility matrix.

Traffic a flags neopravia nekompatibilný shared state.

## 20. Multi-service release

Preferuj independently deployable components. Release manifest má obsahovať digests a compatibility ranges.

Pri coordinated change:

- deploy tolerant consumers/readers first,
- potom producers/writers,
- používaj flags/adapters,
- sleduj per-service rollout,
- definuj partial recovery.

Big-bang promotion znižuje blast-radius kontrolu.

## 21. Controller security

Controller môže meniť production routing a flags. Potrebuje:

- least privilege,
- protected workflow/config,
- short-lived identity,
- approval pre high-risk overrides,
- immutable audit,
- separation od untrusted PR code,
- lock a concurrency protection,
- tested kill switch.

## 22. Controller availability a failure semantics

Rieš:

- controller outage počas step-u,
- duplicate reconciliation,
- stale desired state,
- partial traffic update,
- metric-service outage,
- lost lock/lease,
- restart a idempotent resume.

Data plane má zostať v poslednom známom bezpečnom stave, nie náhodne pokračovať.

## 23. Pause lifecycle

Pause record obsahuje:

- dôvod,
- current exposure a artifacts,
- evidence gaps,
- ownera,
- max pause duration,
- allowed actions,
- resume prechecks,
- expiry/recovery fallback.

Nekonečný pause vytvára permanentný skew a flag debt.

## 24. Delayed validation

Po full exposure pokračuj v monitorovaní:

- memory leak,
- queue/backlog,
- scheduled jobs,
- billing/settlement,
- retention/churn,
- certificate/credential cycles,
- data reconciliation.

Release acceptance môže nastať až po tejto fáze.

## 25. Cleanup a closure

Progressive delivery končí až keď:

- final artifact/config/exposure sú zaznamenané,
- old generation je retired,
- flags a temp routing sú odstránené,
- migration je v intended phase,
- rollback window je uzavreté alebo explicitné,
- evidence a decision record sú archivované,
- follow-up findings majú ownerov.

## 26. Audit trail

Zachovaj:

- rollout contract revision,
- subject identities,
- každú exposure/config zmenu,
- metrics queries a snapshots/references,
- policy verdicts,
- approvals/overrides,
- recovery transitions,
- final release a cleanup state.

## 27. Metriky procesu

- mean exposure before detection,
- time to full release,
- pause/inconclusive/abort rate,
- false abort a false promotion,
- stale rollout count,
- controller/analytics failure rate,
- manual override rate,
- cleanup lead time,
- rollback/roll-forward success,
- escaped defects podľa strategy/risk class.

## 28. Typické anti-patterny

### Progressive delivery = pomalý rollout

Bez evidence a decision policy ide iba o pomalšie šírenie.

### Každá zmena rovnaký workflow

Ignoruje risk a reversibility.

### Viac control planes bez spoločnej identity

Traffic, flags a data state sa rozídu.

### Missing metrics = success

Nefunkčný oracle spôsobí false promotion.

### Automatika bez explainability

Operátor nevie auditovať verdict.

### Nekonečný canary/pause

Temporary skew sa stane permanentným.

### 100 % exposure = finished

Old code paths, flags a migration debt zostávajú.

## 29. Diagnostický postup

1. Urči rollout ID, subject a desired state.
2. Zisti actual artifact, traffic, audience, flags a data phase.
3. Over controller lock a last transition.
4. Validuj telemetry completeness a query freshness.
5. Porovnaj cohort/control a concurrent changes.
6. Skontroluj shared-state compatibility.
7. Pri pause urč ownera, expiry a resume preconditions.
8. Pri abort-e vyber recovery podľa state mutation.
9. Po recovery over user/business/data invariants.
10. Uzavri cleanup a learning actions.

## 30. Rozhodovací rámec

1. Ktoré osi promotion potrebujeme oddeliť?
2. Aký immutable subject a rollout contract používame?
3. Aký risk class a blast radius je prijateľný?
4. Aká vzorka a observation horizon dokazujú každý krok?
5. Ktoré metrics sú technical, functional a business guardrails?
6. Ako sa rieši missing/inconclusive evidence?
7. Aké concurrent changes invalidujú verdict?
8. Aká recovery hierarchy platí?
9. Ako sa controller zotaví z partial failure?
10. Kedy je release prijatý a cleanup dokončený?

## 31. Kontrolný checklist

- subject a rollout contract sú immutable/versionované,
- všetky promotion osi majú actual state,
- risk class určuje steps a approvals,
- version-level telemetry je úplná,
- sample/duration a delayed horizon sú definované,
- verdict taxonomy obsahuje inconclusive/invalid,
- controller a analytics failures majú policy,
- shared state je compatible,
- recovery hierarchy a eligibility sú overené,
- rollout lock chráni concurrency,
- pause má expiry,
- full exposure pokračuje delayed validation,
- cleanup a closure sú vynútené.

## 32. Kontrolné otázky

1. Aké osi promotion progressive delivery oddeľuje?
2. Čo musí obsahovať rollout contract?
3. Prečo controller potrebuje desired aj observed state?
4. Aký je rozdiel medzi pause, abort, inconclusive a invalid?
5. Ako missing telemetry ovplyvňuje verdict?
6. Prečo technical pass nemusí znamenať release success?
7. Ako error budget mení rollout policy?
8. Prečo traffic control nevyrieši shared-state nekompatibilitu?
9. Ako sa controller zotaví po partial update?
10. Kedy je progressive delivery lifecycle skutočne uzavretý?

## Summary

Progressive delivery je policy-driven state machine nad artifactom, environmentom, trafficom, audience, feature flags a data migration stavom. Dôveryhodnosť vzniká immutable rollout contractom, version-level evidence, risk-based steps, explicitnými verdictmi a bezpečnou recovery hierarchiou. Controller musí byť chránený ako produkčný control plane a zvládať partial failures aj missing telemetry. Full exposure nie je koniec: release potrebuje delayed validation, odstránenie dočasných paths a formálne uzavretie evidence a rollout state.

## Glossary impact

Relevantné pojmy: progressive delivery, rollout controller, rollout contract, promotion axis, observed state, evidence-driven promotion, inconclusive rollout, rollout pause, exposure control, recovery hierarchy, delayed validation, cleanup phase a rollout closure.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Feature flags](feature-flags.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Rollback a roll-forward →](rollback-and-roll-forward.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
