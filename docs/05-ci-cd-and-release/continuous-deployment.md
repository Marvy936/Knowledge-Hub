# Continuous Deployment

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Continuous Deployment je delivery model, v ktorom každý artifact spĺňajúci automatizovanú promotion policy pokračuje bez rutinného manuálneho release approvalu do produkčného rollout-u a následnej produkčnej validácie.

```text
promotable immutable artifact
→ complete a fresh evidence
→ risk a environment policy
→ bounded production exposure
→ technical + functional + business oracle
→ promote / pause / abort / recover
→ post-promotion observation
→ policy a test learning
```

Continuous Deployment nie je „po zelenom CI pošli 100 % trafficu“. Automatizuje rozhodnutie aj bezpečné state transitions. Ak mainline, deployability, observability alebo recovery nie sú dôveryhodné, odstránenie approval tlačidla iba zrýchli incident.

## 1. Cieľ kapitoly

Nosný model kapitoly je policy-driven rollout lifecycle:

```text
promotable candidate
→ evidence completeness a freshness
→ change-risk classification
→ target-health a incident policy
→ deployment bez alebo s obmedzenou exposure
→ matched canary/control evidence
→ viacstavové rollout rozhodnutie
→ rollback, roll-forward, flag-off alebo containment
→ delayed-failure watch
→ audit a zlepšenie policy
```

Manuálny approval je nahradený explicitnou, verzovanou a vysvetliteľnou policy. Rozhodnutie nezmizne; stáva sa automatizovaným a auditovateľným.

## 2. Nosný scenár: Atlas Orders 3.10.0

Continuous Delivery označilo tieto artifacts ako promotable:

```text
orders-api digest A
payment-worker digest B
migration bundle M
config revision K
feature-flag revision F
promotion evidence E
```

Atlas chce automaticky nasadiť release, ktorý mení event `priority`, retry behavior a PostgreSQL index. Automatický systém musí rozhodnúť:

- či E patrí A/B/M/K/F a je stále fresh;
- aké riziko má database/event/retry zmena;
- či production nie je v incidente alebo bez error budgetu;
- akú cohortu a observation window použiť;
- či technical, functional a business signals umožňujú promotion;
- či je rollback kompatibilný s current schema a messages;
- čo robiť pri incomplete alebo delayed signále.

## 3. Vzťah CI, Delivery a Deployment

```text
Continuous Integration
→ dôveryhodný candidate sa bezpečne integruje

Continuous Delivery
→ artifact zostáva trvalo deployable a promotable

Continuous Deployment
→ production promotion a rollout sa vykonajú automaticky podľa policy
```

Continuous Deployment nemôže kompenzovať broken main, rebuildy medzi environments ani ručný deployment state.

## 4. Rollout state machine

Atlas používa explicitné stavy:

```text
candidate
→ evidence-complete
→ policy-eligible
→ deployed, 0 % exposure
→ synthetic/internal validation
→ canary cohort
→ wider cohorts
→ fully promoted
→ post-promotion watch
```

Alternatívne transitions:

```text
incomplete evidence → wait/revalidate
policy denied       → stop
invalid cohort      → rebuild rollout setup
inconclusive signal → pause/escalate
critical guardrail  → abort/contain
incompatible state  → roll-forward alebo feature disable
```

Každý transition je previazaný na artifact/config/flag identity, policy version, rollout stage, metrics a actor alebo automation identity.

## 5. Promotion policy

Atlas policy vyhodnocuje:

- artifact signature, provenance a SBOM;
- complete required test/security evidence;
- source a protected-ref status;
- change risk classification;
- database, event, IAM a network impact;
- target environment health;
- incident a maintenance stav;
- SLO/error-budget burn;
- rollout capacity a window;
- previous cohort výsledok;
- rollback/roll-forward readiness.

Policy je versionovaná, reviewovaná, testovaná cez allow aj deny fixtures a má expirovateľnú exception cestu.

## 6. Evidence completeness a freshness

Automatický verdict musí potvrdiť:

```text
candidate identity
+ artifact/config/flag revisions
+ expected required controls
+ actual reports a shards
+ tool execution status
+ evidence timestamp a expiry
+ target/policy freshness
→ eligible / incomplete / stale / denied
```

Scanner timeout, missing shard alebo unavailable telemetry nie sú úspech. Správny výsledok je `incomplete`, `wait` alebo `pause` podľa fázy.

Ak artifact dlho čakal, base-image advisory, production config alebo policy sa mohli zmeniť. Freshness je risk contract, nie dekoratívny timestamp.

## 7. Change-risk classification

Atlas risk model zahŕňa:

- business criticality;
- database a event schema zmenu;
- external financial side effects;
- IAM/network/secrets impact;
- rollback complexity;
- test a contract evidence;
- novelty a incident history;
- tenant a region blast radius;
- current SLO/error-budget stav.

Výsledok ovplyvňuje rollout:

```text
low risk
→ krátky internal + small canary

medium risk
→ stratifikovaná cohorta a dlhšie guardrails

high risk
→ protected window alebo explicitný human decision
```

Continuous Deployment môže byť povolený iba pre subset zmien. Risk-based boundary je legitímna súčasť modelu.

## 8. Deployment verzus release

Automatický deployment môže nasadiť kód s nulovou expozíciou:

```text
A/B/M deployed
→ F off alebo 0 % traffic
→ startup, migration a synthetics
→ internal tenant
→ production cohort
```

Feature flag alebo routing oddelí technical deployment od business releaseu. Tento state však potrebuje provenance, fail-open/fail-closed semantics, audit, ownera a cleanup deadline.

Flag nie je authorization boundary a nevypína automaticky všetky shared-resource alebo migration effects.

## 9. Cohort design a progressive exposure

Atlas nepoužíva percento ako jedinú definíciu cohorty. Segmentuje podľa:

- tenant size;
- region a latency profile;
- client version;
- operation mix;
- data volume;
- payment provider route.

Rollout:

```text
0 % user traffic
→ internal tenant
→ small-tenant canary
→ large-tenant canary
→ 25 % matched production
→ 50 % capacity stage
→ 100 %
```

Každá fáza má sample, duration, promote threshold, abort threshold, signal latency a recovery action.

## 10. Canary analysis

Kompozitný oracle zahŕňa:

### Technical

- error a retry-rate delta;
- p95/p99 latency;
- DB pool waits a locks;
- queue depth a oldest-message age;
- restart, CPU a memory saturation;
- dependency errors.

### Functional

- tenant isolation;
- event deserialization;
- idempotent payment outcome;
- migration/backfill integrity;
- audit a correlation completeness.

### Business

- order completion;
- payment confirmation;
- abandonment a repeat attempts;
- segment-specific degradation.

Verdict môže byť `promote`, `pause`, `abort`, `inconclusive` alebo `invalid`. Inconclusive nie je pass.

## 11. Control group a attribution

Canary sa porovnáva so starou verziou v podobných podmienkach. Telemetry obsahuje:

```text
artifact digest
+ deployment/config/flag revision
+ cohort a assignment rule
+ region/tenant segment
+ rollout stage
+ timestamp
```

Ak canary obsahuje prevažne malých tenantov a control veľkých, rozdiel nemožno pripísať verzii. Invalid cohort setup musí zastaviť automatický analysis.

## 12. Signal latency a delayed failures

Rôzne failure mechanizmy majú iné okná:

- routing/startup: sekundy;
- retry amplification a queue growth: minúty;
- backfill alebo large-tenant completion: desiatky minút;
- memory leak, settlement, retention alebo cost: hodiny až dni.

Krátky canary nemôže preukázať delayed behavior. Atlas kombinuje immediate rollout guardrails, post-promotion watch, reconciliation a incident/roll-forward proces.

Automatický rollback je vhodný najmä pre rýchly, presný a reverzibilný failure.

## 13. Recovery policy

Atlas rozhoduje:

```text
reverzibilný artifact/config failure
→ rollback

feature behavior bez shared-state mutation
→ flag off alebo traffic shift

schema/event/external side effect nekompatibilný
→ roll-forward, containment alebo reconciliation
```

Rollback preconditions:

- stará verzia rozumie aktuálnej schema a messages;
- rollout rollbacku je overený;
- signal má nízky false-positive rate;
- návrat znižuje user impact.

Database, event retention a financial side effects môžu urobiť automatický rollback nebezpečným.

## 14. Deployment oscillation

Príliš citlivý alebo hlučný signal môže vytvoriť:

```text
deploy
→ krátky alert spike
→ rollback
→ metrics sa stabilizujú
→ systém znovu deployne candidate
→ opakovaný alert
```

Ochrany:

- hysteresis;
- oddelené promote a abort thresholds;
- minimálna observation window;
- cooldown po recovery;
- limit automatic attempts;
- korelácia viacerých signálov;
- human escalation pri opakovaní.

Automation nesmie sama oscilovať medzi stavmi bez limitu.

## 15. Human-in-the-loop

Continuous Deployment odstraňuje rutinný mechanický approval, nie ľudské vlastníctvo. Ľudia:

- navrhujú a reviewujú policy;
- kalibrujú thresholds;
- riešia `pause`, `inconclusive` a high-risk zmenu;
- rozhodujú pri incompatible state;
- reagujú na incident;
- schvaľujú expirovateľné exceptions;
- analyzujú false promotion a false rollback.

Override je auditovaný, scoped a časovo obmedzený.

## 16. Worked failure: incomplete security evidence bolo fail-open

Dependency scanner timeoutoval. Pipeline wrapper vrátil exit code 0, pretože scan bol označený ako „best effort“:

```text
scanner nevytvoril report
→ aggregator videl nulový počet findings
→ policy vyhodnotila candidate ako eligible
→ automatic rollout pokračoval
→ produkcia dostala reachable vulnerable package
```

### Root cause

Systém zamieňal „žiadny report“ za „žiadne findings“. Evidence manifest nevyžadoval scanner execution status a policy nemala `incomplete` state.

### Náprava

- expected-control manifest a report completeness check;
- samostatné states `pass`, `finding`, `incomplete`, `tool_failure`;
- high-risk dependency control je fail-closed alebo pause;
- scanner outage má ownera a exception workflow;
- eligibility record viaže policy na konkrétny complete evidence bundle.

## 17. Worked failure: automatický rollback zhoršil incident

Atlas rollout pridal additive event field, nový consumer začal zapisovať nový `payment_state` a backfill už časť dát konvertoval. Canary guardrail detegoval latency spike a systém automaticky obnovil starý worker:

```text
new worker zapísal nový state
→ automatic rollback na old worker
→ old worker nový state nepoznal
→ messages išli do poison queue
→ retries zvýšili backlog
→ rollout controller opakovane deployoval a rollbackoval
```

### Root cause

Rollback eligibility kontrolovala iba dostupnosť starého image. Nekontrolovala data/event compatibility ani hysteresis. Latency spike navyše pochádzal z globálneho provider incidentu, nie z canary verzie.

### Náprava

- rollback compatibility matrix pre schema, events a data state;
- matched control group a attribution;
- `pause` namiesto rollbacku pri nejednoznačnom signále;
- cooldown a limit recovery attempts;
- feature disable a roll-forward path;
- poison-queue/replay guardrails a reconciliation.

## 18. Audit trail

Pre každý rollout Atlas uchová:

- artifact/source/config/flag identity;
- evidence bundle a policy version;
- risk classification;
- target environment a deployment identity;
- cohort assignments;
- metrics, decisions a state transitions;
- pause, abort a override events;
- recovery outcome;
- post-promotion validation.

Audit má vysvetliť nielen čo sa stalo, ale prečo policy promotion povolila alebo zastavila.

## 19. Metriky

Atlas sleduje:

- commit-to-production lead time;
- deployment frequency a batch size;
- change fail rate;
- canary pause/abort/invalid rate;
- mean exposure before detection;
- false promotion a false rollback rate;
- rollback/roll-forward time;
- delayed regression rate;
- rollout duration a queue time;
- stale flags a exceptions;
- percent rolloutov s complete version-level telemetry.

Viac deploymentov bez nízkeho dopadu a rýchlej recovery nie je úspech.

## 20. Diagnostický postup

Pri zastavenom alebo chybnom rolloute:

1. Potvrď artifact, config, flag, policy a cohort identity.
2. Over complete a fresh pre-deploy evidence.
3. Skontroluj target health, incident a error-budget stav.
4. Rozlíš deployment execution od canary oracle failure.
5. Over cohort comparability, sample a telemetry completeness.
6. Nájdite prvý observation point, kde sa candidate od controlu odlíšil.
7. Posúď shared-state a rollback compatibility.
8. Vyber pause, rollback, roll-forward, flag-off alebo containment.
9. Over recovery cez technical, functional aj data/business oracle.
10. Zachovaj rollout timeline a policy explanation.
11. Oprav policy, telemetry, tests alebo architecture a revaliduj.

## 21. Referenčné pravidlá

- Continuous Deployment automatizuje policy decision a rollout, nie iba deploy command.
- Evidence musí byť complete, fresh a viazané na presný candidate.
- Risk classification mení rollout a môže vyžadovať human boundary.
- Deployment a business release možno oddeliť.
- Cohorty musia reprezentovať relevantné workload segmenty.
- Canary verdict zahŕňa technical, functional aj business oracle.
- `Inconclusive` a `invalid` nie sú pass.
- Observation window vychádza zo signal latency.
- Automatic rollback potrebuje state compatibility a hysteresis.
- Telemetry failure blokuje alebo pause-ne promotion.
- Human override má ownera, scope, audit a expiry.
- Findings sa vracajú do policy, tests a recovery modelu.

## 22. Časté omyly

### „Green CI znamená automaticky 100 % production“

Chýba production risk, cohort a runtime validation.

### „Žiadne findings znamenajú security pass“

Iba ak sa všetky required controls skutočne vykonali a reporty sú complete.

### „5 % trafficu je bezpečný canary“

Percento bez reprezentatívnej cohorty a guardrails môže byť slepé.

### „Každý alert má spustiť rollback“

Noise, globálny incident alebo incompatible state môžu rollbackom zhoršiť dopad.

### „Feature flag odstráni deployment risk“

Shared resources, migrations a startup paths môžu pôsobiť aj pri flag off.

### „Automatizácia odstraňuje ľudskú zodpovednosť“

Ľudia vlastnia policy, exceptions, incidenty a learning loop.

## 23. Zhrnutie

Bezpečné Continuous Deployment pre Atlas je:

```text
promotable artifact
→ complete/fresh evidence
→ risk-aware policy
→ controlled deployment a exposure
→ matched production oracle
→ promote/pause/abort/inconclusive
→ compatible recovery
→ delayed watch
→ audit a policy learning
```

Automatizácia je bezpečná iba vtedy, keď systém pozná aj stavy, v ktorých nevie rozhodnúť alebo sa nemôže bezpečne vrátiť.

## 24. Kontrolné otázky

1. Čo presne automatizuje Continuous Deployment?
2. Prečo nestačí zelené CI?
3. Aké states má rollout state machine?
4. Ako evidence completeness a freshness ovplyvňujú eligibility?
5. Ako risk classification mení rollout?
6. Prečo deployment nemusí znamenať okamžitý release?
7. Ako sa navrhuje reprezentatívna cohorta?
8. Aké vrstvy má canary oracle?
9. Prečo `inconclusive` nie je pass?
10. Ako signal latency určuje observation window?
11. Prečo fail-open scanner vytvoril false promotion?
12. Prečo automatický rollback zhoršil mixed-state incident?
13. Čo bráni deployment oscillation?
14. Akú úlohu má človek v automatickom systéme?

## Glossary impact

Relevantné pojmy: Continuous Deployment, automated promotion, promotion policy, rollout state machine, evidence completeness, evidence freshness, change-risk classification, progressive exposure, matched cohort, canary analysis, inconclusive result, automatic rollback, rollback compatibility, deployment oscillation, human override a delayed failure.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Continuous Delivery](continuous-delivery.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Pipeline, stage, job a runner →](pipeline-stage-job-runner.md)
<!-- KNOWLEDGE-NAVIGATION:END -->