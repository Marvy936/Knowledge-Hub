# Continuous Deployment

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Continuous Deployment je delivery model, v ktorom každý artifact spĺňajúci automatizovanú promotion policy pokračuje bez rutinného manuálneho release approvalu do produkčného deploymentu a následnej produkčnej validácie.

```text
integrovaná zmena
→ dôveryhodný immutable artifact
→ automatizované evidence a policy rozhodnutie
→ kontrolovaný produkčný rollout
→ produkčná verification a validation
→ promote / pause / rollback / roll-forward
```

Continuous Deployment nie je „deploy po každom zelenom teste“. Je to automatizovaný rozhodovací a recovery systém, ktorý musí rozlišovať kvalitu evidence, riziko zmeny, stav cieľového prostredia, shared-state kompatibilitu a produkčné guardrails.

## 2. Vzťah k CI a Continuous Delivery

Continuous Deployment stojí na dvoch predchádzajúcich schopnostiach:

```text
Continuous Integration
→ presný merge candidate sa často a dôveryhodne integruje

Continuous Delivery
→ artifact je trvalo deployable a promotion cesta je bezpečná

Continuous Deployment
→ production promotion sa vykoná automaticky podľa policy
```

Ak mainline nie je stabilná, build nie je reprodukovateľný alebo deployment vyžaduje ručné improvizácie, automatizácia iba skracuje čas od zmeny k incidentu.

## 3. Mental model: policy-driven rollout state machine

Automatický deployment je stavový stroj, nie jedno tlačidlo:

```text
candidate
→ evidence complete
→ policy eligible
→ deployed with no/limited exposure
→ canary observing
→ wider rollout
→ fully promoted
```

Alternatívne vetvy:

```text
insufficient evidence → wait/revalidate
policy denied         → stop
signal inconclusive   → pause
critical guardrail    → abort/recover
state incompatible    → roll-forward alebo feature disable
```

Každý state transition musí byť auditovateľný a viazaný na artifact digest, policy version, target environment a pozorované metrics.

## 4. Automatické promotion rozhodnutie

Manuálny approval je nahradený explicitnou policy, nie absenciou rozhodnutia.

Policy môže vyhodnocovať:

- required test a security results,
- completeness a freshness evidence,
- artifact provenance, podpis a SBOM,
- source branch a protected-ref status,
- change risk classification,
- database, IAM alebo network impact,
- target environment health,
- current incident a maintenance stav,
- SLO a error-budget burn,
- rollout window a capacity,
- canary alebo previous-ring výsledok.

Policy musí byť:

- versionovaná,
- reviewovaná,
- deterministická tam, kde je to možné,
- vysvetliteľná,
- testovaná cez allow aj deny fixtures,
- auditovateľná,
- vybavená expirovateľnou exception cestou.

## 5. Evidence completeness a freshness

Automatické rozhodnutie je dôveryhodné iba vtedy, keď evidence patrí presnému artifactu a je stále platné.

Kontroluj:

- candidate a artifact digest,
- úspech všetkých required shardov,
- tool a scanner execution status,
- test environment a config identity,
- policy version,
- target branch freshness,
- dependency a base-image zmeny,
- expiráciu výsledkov pri dlhom čakaní,
- či artifact nebol po validácii mutovaný.

Chýbajúci report, timeout analyzátora alebo nedostupný scanner nie sú zelený výsledok. Správny outcome môže byť `incomplete` alebo `wait`, nie automatická promotion.

## 6. Predpoklady Continuous Deployment

Praktické predpoklady:

- často integrovaná a zdravá mainline,
- malé a spätne kompatibilné zmeny,
- immutable artifacty s provenance,
- nízko-noise blocking gates,
- reprodukovateľné environmenty,
- versionovaná a testovaná deployment automation,
- kvalitná version-level observability,
- bezpečný progressive rollout,
- rýchla recovery cesta,
- on-call a ownership pripravenosť,
- shared-state compatibility,
- incident a error-budget policy.

Continuous Deployment je organizačná a architektonická capability. Nedá sa zaviesť iba odstránením approval tlačidla.

## 7. Deployment verzus release

Automatický deployment nemusí okamžite sprístupniť novú funkcionalitu všetkým používateľom.

Deployment a release možno oddeliť cez:

- feature flags,
- dark launch,
- ring alebo tenant targeting,
- canary traffic,
- region allowlist,
- configuration activation,
- API routing.

Kód môže byť nasadený v produkcii s nulovou alebo obmedzenou expozíciou. To umožňuje overiť startup, wiring a telemetry skôr než sa zmena stane business releaseom.

Oddelenie však vytvára ďalší state space. Flags, routing a cohort configuration musia mať provenance, testy, ownera a cleanup lifecycle.

## 8. Risk classification

Nie každá zmena má rovnaké riziko a nemá používať rovnaký rollout.

Risk model môže zohľadniť:

- business criticality komponentu,
- veľkosť a typ diffu,
- database alebo event schema zmenu,
- IAM, network alebo secret policy zmenu,
- data-mutation a external side effects,
- rollback complexity,
- test a contract coverage,
- novelty a change history,
- incident history,
- blast radius a počet tenantov,
- časový kontext a error-budget stav.

Príklad policy:

```text
nízke riziko
→ automatický krátky canary a rýchle promotion kroky

stredné riziko
→ menší cohort, dlhšia observation a širšie guardrails

vysoké riziko
→ protected environment, explicitný approval alebo plánované okno
```

Organizácia môže používať Continuous Deployment iba pre subset zmien. To je legitímny risk-based model, nie zlyhanie automatizácie.

## 9. Progressive exposure

Bezpečnejší rollout zvyšuje expozíciu postupne:

```text
deployed, 0 % user traffic
→ internal ring
→ 1 %
→ 5 %
→ 25 %
→ 50 %
→ 100 %
```

Každý krok definuje:

- target cohort a routing rule,
- minimálny počet requests alebo sessions,
- observation duration,
- promotion metrics,
- guardrail a abort metrics,
- baseline alebo control group,
- signal latency,
- rollback/roll-forward action,
- maximálny blast radius.

Percentá nie sú cieľ. Cieľom je získať dostatočný dôkaz pred zväčšením dopadu.

## 10. Canary analysis

Canary analysis porovnáva novú verziu s control group alebo relevantným baseline.

Signály môžu zahŕňať:

- error-rate delta,
- p95/p99 latency delta,
- restart a saturation rate,
- dependency errors,
- queue growth,
- business completion alebo conversion,
- authorization a data-integrity invariants,
- log/trace anomalies,
- synthetic journeys.

Výsledok nemá byť iba pass/fail:

- **promote —** evidence spĺňa kritériá;
- **abort/rollback —** kritický guardrail je porušený;
- **pause —** je potrebná manuálna alebo dlhšia analýza;
- **inconclusive —** vzorka alebo telemetry nestačí;
- **invalid —** cohorty nie sú porovnateľné alebo rollout setup bol chybný.

Inconclusive nie je pass. Automatický systém musí vedieť bezpečne čakať alebo eskalovať.

## 11. Control group a attribution

Absolútna metrika bez súbežného kontextu môže viesť k false rollbacku alebo false promotion.

Control group má byť porovnateľná podľa:

- času,
- regiónu,
- tenant alebo customer typu,
- device/client verzie,
- request mixu,
- data size a cache state,
- dependency topology.

Telemetry musí obsahovať artifact, deployment a cohort labels. Bez nich nemožno spoľahlivo určiť, či failure patrí novej verzii, globálnemu incidentu alebo konkrétnemu segmentu.

## 12. Automatický rollback

Automatický rollback je vhodný, keď:

- failure je rýchlo a presne detegovateľný,
- predchádzajúca verzia je kompatibilná s aktuálnym stavom,
- rollback proces je overený,
- návrat znižuje používateľský dopad,
- signal má nízky false-positive rate.

Rollback je nebezpečný pri:

- nevratnej database migrácii,
- novom event alebo serialization formáte,
- external side effects,
- data corruption,
- nekompatibilnom backfille,
- oneskorenom business settlement signále.

V týchto prípadoch môže byť bezpečnejšie:

- vypnúť feature flag,
- zastaviť writes,
- roll-forward hotfix,
- izolovať tenant alebo region,
- vykonať reconciliation alebo restore.

## 13. Deployment oscillation

Hlučný signal môže spôsobiť cyklus:

```text
deploy
→ alert
→ rollback
→ metrics sa stabilizujú
→ znovu deploy
→ alert
```

Ochrany:

- hysteresis a minimálna observation window,
- oddelené promotion a abort thresholds,
- cooldown po rollbacku,
- korelácia viacerých signálov,
- limit automatických recovery pokusov,
- human escalation pri opakovaní,
- audit false rollbackov.

Automatický rollback nie je náhradou root-cause analýzy.

## 14. Feature flags

Feature flags podporujú oddelenie deploymentu od releaseu a rýchle obmedzenie blast radiusu.

Každý flag potrebuje:

- ownera,
- typ a účel,
- default behavior,
- fail-open/fail-closed semantics,
- target a hashing pravidlo,
- audit zmien,
- test relevantných kombinácií,
- removal criteria a deadline.

Feature flag nesmie byť jediná authorization kontrola. Flag service outage, stale cache alebo nekonzistentné vyhodnotenie medzi clients musí mať definované správanie.

## 15. Databázová kompatibilita

Continuous Deployment predpokladá súbeh starých a nových aplikačných verzií nad spoločným stavom.

Používaj:

- expand-contract,
- additive schema changes,
- online migrations,
- postupný backfill,
- dual-read alebo dual-write iba s jasným reconciliation modelom,
- tolerant readers,
- explicitnú deprecation policy,
- oddelenie destructive cleanupu do neskoršieho releaseu.

Automatický rollback starej aplikácie je bezpečný iba vtedy, keď stará verzia rozumie aktuálnemu schema a dátam.

## 16. Event-driven systémy

Pri automatickom deploymente producers a consumers overuj:

- payload a semantic compatibility,
- staré messages v retention,
- duplicate a out-of-order delivery,
- consumer restart a checkpointing,
- poison-message behavior,
- replay a dead-letter queue,
- partition key a ordering assumptions,
- backlog počas canary a rollbacku,
- idempotency side effects.

Nový consumer môže fungovať na čerstvých eventoch, ale zlyhať pri replayi historických messages. Compatibility evidence musí pokrývať reálny retention horizon.

## 17. Delayed failures

Niektoré failures sa prejavia po minútach, hodinách alebo dňoch:

- memory alebo resource leak,
- queue backlog,
- cache churn,
- batch alebo settlement job,
- certificate refresh,
- replication lag,
- data corruption,
- cost explosion,
- business KPI zmena.

Krátky canary gate ich nemusí zachytiť. Potrebná je kombinácia:

- immediate rollout guardrails,
- dlhšie observation windows pre relevantné zmeny,
- kontinuálne production monitoring,
- periodic reconciliation,
- automated rollback iba pre reverzibilné rýchle failures,
- incident a roll-forward proces pre oneskorené failures.

## 18. Error budgets a incident state

Promotion policy môže zohľadniť reliability stav služby.

```text
budget healthy
→ štandardný rollout

budget pod warning hranicou
→ menší canary a dlhšia observation

budget rýchlo horí alebo prebieha incident
→ pause/freeze okrem urgentných reliability zmien
```

Error budget musí byť založený na používateľskom SLI. Nemá slúžiť ako všeobecný zákaz zmien bez kontextu.

## 19. Observability požiadavky

Automatický rollout potrebuje okamžité aj oneskorené signály:

- artifact a deployment labels,
- cohort a feature-variant dimensions,
- request/trace IDs,
- user-facing SLIs,
- technical saturation metrics,
- business outcomes,
- synthetic checks,
- migration a backlog metrics,
- rollout event markers.

Telemetry failure musí mať vlastnú policy. Ak systém nevie pozorovať rollout, nemá ho automaticky promovať.

## 20. Human-in-the-loop

Continuous Deployment odstraňuje rutinný mechanický approval, nie ľudskú zodpovednosť.

Ľudia stále:

- navrhujú a reviewujú policy,
- kalibrujú thresholds,
- rozhodujú pri `pause`, `inconclusive` alebo high-risk zmene,
- reagujú na incident,
- schvaľujú expirovateľné exceptions,
- analyzujú false rollback a false promotion,
- zlepšujú testy, telemetry a recovery.

Human override musí byť auditovaný, časovo obmedzený a spojený s risk ownerom.

## 21. Audit trail

Pre každý deployment uchovaj:

- artifact digest a source commit,
- pipeline run a evidence bundle,
- policy version a risk classification,
- actor/deployment identity,
- target environment,
- config a feature-flag version,
- rollout steps a cohorty,
- metrics a rozhodnutia,
- pause/abort/override udalosti,
- rollback alebo roll-forward výsledok,
- post-deploy validation.

Audit trail má vysvetliť nielen čo sa stalo, ale prečo systém promotion povolil alebo zastavil.

## 22. Failure taxonomy

Rozlišuj:

- pre-deploy policy denial,
- incomplete evidence,
- artifact verification failure,
- deployment execution failure,
- rollout timeout,
- canary guardrail failure,
- inconclusive alebo invalid analysis,
- observability/tool failure,
- rollback failure,
- delayed production regression.

Každá trieda má inú recovery cestu. Slepo retryovať policy denial alebo data-integrity failure je nebezpečné.

## 23. Metriky Continuous Deployment

Sleduj:

- deployment frequency a batch size,
- commit-to-production lead time,
- change fail rate,
- mean exposure before detection,
- canary abort a pause rate,
- inconclusive/invalid analysis rate,
- automatic rollback a false rollback rate,
- roll-forward time,
- rollout duration a queue time,
- delayed regression rate,
- stale feature flags,
- percent deploymentov s úplnou version-level telemetry,
- manual override count a age exceptions.

Veľa deploymentov bez nízkeho dopadu a rýchlej recovery nie je úspešný model.

## 24. Diagnostický postup

Pri zastavenom alebo chybném rolloute:

1. identifikuj artifact, policy, config a cohort;
2. over úplnosť a čerstvosť pre-deploy evidence;
3. skontroluj environment health a súbežné incidenty;
4. rozlíš deployment failure od canary signal failure;
5. over porovnateľnosť control group a telemetry completeness;
6. posúď shared-state a rollback kompatibilitu;
7. vyber pause, rollback, roll-forward, flag-off alebo traffic shift;
8. over recovery cez technický, funkčný a data-integrity oracle;
9. uchovaj rollout timeline a rozhodnutia;
10. oprav policy, test, telemetry alebo architektúru a revaliduj.

## 25. Typické anti-patterny

### Zelené CI automaticky znamená 100 % production traffic

Chýba risk classification, progressive exposure a production validation.

### Rovnaká policy pre všetky zmeny

Ignoruje database, IAM, business a rollback rozdiely.

### Automatický rollback na každý alert

Noise vytvára oscillation a môže zhoršiť state compatibility.

### Canary bez version-level telemetry

Nie je možné pripísať failure konkrétnej verzii.

### Promotion pri neúplnom signále

Nedostupný monitoring alebo malá vzorka sa nesprávne interpretujú ako pass.

### Feature flags bez cleanupu

State space a incident complexity trvalo rastú.

### Krátke observation window pre delayed failure

Rollout prejde a problém sa prejaví až po plnej expozícii.

### Automatizácia bez on-call pripravenosti

Failure sa šíri bez schopnosti rýchlej a kompetentnej reakcie.

## 26. Praktický rozhodovací rámec

1. Je artifact immutable, overený a evidence kompletné?
2. Aká policy version rozhoduje o promotion?
3. Aký je risk classification zmeny?
4. Aká rollout strategy a cohort zodpovedajú riziku?
5. Aká control group alebo baseline je porovnateľná?
6. Aké sú promote, pause, abort a inconclusive criteria?
7. Aká je signal latency a minimálna vzorka?
8. Je rollback kompatibilný so stavom?
9. Aká je roll-forward alebo feature-disable cesta?
10. Ktoré delayed failures treba monitorovať po promotion?
11. Ako incident a error budget menia policy?
12. Kto rozhoduje pri nejednoznačnom výsledku?
13. Aký audit trail a evidence sa uchová?

## 27. Kontrolný checklist

- artifact digest a provenance sú jednoznačné;
- required evidence je úplné a čerstvé;
- policy má testované allow/deny scenáre;
- risk classification ovplyvňuje rollout;
- deployment a release sú oddelené podľa potreby;
- canary má porovnateľnú control group;
- telemetry obsahuje version a cohort labels;
- neúplná telemetry blokuje alebo pause-ne promotion;
- existuje inconclusive stav;
- rollback/roll-forward/flag-off sú otestované;
- database a event schemas sú kompatibilné;
- delayed failures majú kontinuálne guardrails;
- automatic recovery má hysteresis a retry limit;
- human override má audit, ownera a expiry;
- post-deploy learning sa vracia do policy a tests.

## 28. Kontrolné otázky

1. Čo presne automatizuje Continuous Deployment?
2. Prečo nie je synonymom „deploy po zelenom CI“?
3. Aké stavy má policy-driven rollout?
4. Prečo evidence potrebuje freshness a completeness?
5. Ako risk classification mení rollout strategy?
6. Prečo deployment nemusí znamenať okamžitý release?
7. Aké výsledky má vracať canary analysis?
8. Prečo control group musí byť porovnateľná?
9. Kedy je automatický rollback nebezpečný?
10. Čo spôsobuje deployment oscillation?
11. Ako feature flags ovplyvňujú state space?
12. Prečo event retention komplikuje compatibility?
13. Ktoré failures sa prejavia až po krátkom canary okne?
14. Ako error budget ovplyvňuje promotion policy?
15. Akú úlohu má človek v automatickom deployment systéme?

## Summary

Continuous Deployment automatizuje promotion dôveryhodného artifactu do produkcie podľa explicitnej policy a produkčných guardrails. Bezpečný model používa risk classification, progressive exposure, porovnateľnú control group, úplnú version-level telemetry a viacstavové rozhodnutia vrátane `pause` a `inconclusive`. Automatický rollback je vhodný iba pri reverzibilnom stave; database, events a external side effects často vyžadujú roll-forward alebo feature disable. Ľudia zostávajú vlastníkmi policy, nejednoznačných rozhodnutí a učenia z incidentov.

## Glossary impact

Relevantné pojmy: Continuous Deployment, automated promotion, promotion policy, evidence freshness, risk classification, progressive exposure, canary analysis, control group, inconclusive result, automatic rollback, deployment oscillation, human override, rollout window a delayed failure.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Continuous Delivery](continuous-delivery.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Pipeline, stage, job a runner →](pipeline-stage-job-runner.md)
<!-- KNOWLEDGE-NAVIGATION:END -->