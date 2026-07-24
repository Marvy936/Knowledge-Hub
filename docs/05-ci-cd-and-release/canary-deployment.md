# Canary deployment

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Canary deployment postupne vystavuje novú verziu obmedzenému a identifikovateľnému segmentu produkčného trafficu. Cieľom je získať produkčný dôkaz pri malom blast radiuse a rozhodovať o ďalšej promotion na základe explicitnej policy.

```text
stable + canary deployed
→ limited exposure
→ observe and compare
→ promote / pause / abort / inconclusive
→ next exposure step
→ full release alebo recovery
```

Canary nie je iba „jeden nový pod“ ani pomalší rolling update. Potrebuje cohort assignment, control group, version-level telemetry, observation contract a bezpečný recovery mechanizmus.

## 2. Deployment, release a exposure

Rozlišuj:

- **Deployment —** artifact existuje v produkčnom runtime.
- **Release —** capability je používateľsky dostupná.
- **Exposure —** konkrétny podiel alebo segment skutočne používa novú verziu.

Canary môže riadiť exposure pomocou routingu, feature flagu, tenant allowlistu, regionálneho ring-u alebo ich kombinácie.

## 3. Mental model: riadený experiment pre release risk

Canary testuje hypotézu:

```text
Pri expozícii segmentu C artifactu A
zostanú technické, funkčné a business guardrails
v definovaných hraniciach voči control skupine S.
```

Je to release-safety experiment, nie automaticky produktový A/B test. Primárnou otázkou je, či možno bezpečne rozšíriť novú verziu.

## 4. Canary subject a experiment identity

Každý rollout krok musí byť viazaný na:

- canary artifact digest,
- stable artifact digest,
- config a feature-flag revision,
- deployment a rollout ID,
- cohort definition a salt/version,
- region/zone/route scope,
- policy version,
- observation window,
- metrics query/version.

Bez tejto identity nemožno výsledok reprodukovať ani pripísať konkrétnej zmene.

## 5. Canary state machine

```text
planned
→ prechecks
→ canary deployed, no exposure
→ warm-up
→ exposure step active
→ collecting evidence
→ evaluating
→ promote / pause / abort / inconclusive
→ next step alebo full release
→ delayed validation
→ completed
```

Recovery vetvy:

- traffic removed,
- feature disabled,
- rollback,
- roll-forward,
- compensating action,
- data repair.

## 6. Preconditions

Pred prvým requestom over:

- immutable artifact a config identity,
- stable baseline health,
- canary capacity a warm-up,
- database/event/cache/session compatibility,
- telemetry dimensions,
- cohort routing correctness,
- promotion/abort/inconclusive rules,
- rollback eligibility,
- privacy a targeting policy,
- on-call a automated controller readiness.

## 7. Výber canary segmentu

Segment môže byť:

- náhodné percento stabilne hashovaných používateľov,
- interný cohort,
- nízkorizikoví tenants,
- konkrétny región alebo zóna,
- API route alebo operation,
- client/device verzia,
- ring podľa support modelu.

Segment musí reprezentovať riziko, ktoré testuješ. Interní používatelia neodhalia veľký data skew; jeden región nemusí reprezentovať ostatné dependencies.

## 8. Stabilné cohort assignment

Pri stateful workflow musí subjekt zostať v rovnakej skupine:

```text
bucket = hash(subject_id + rollout_salt) mod N
```

Vlastnosti:

- deterministic assignment,
- versionovaný salt/policy,
- auditovateľné eligibility rules,
- ochrana osobných identifikátorov,
- explicitné fallback správanie.

Random routing per request môže miešať verzie v jednom journey a vytvoriť neplatné porovnanie.

## 9. Traffic percentage verzus sample size

`1 %` nie je dôkazná veličina. Potrebný je minimálny počet relevantných udalostí.

Sleduj:

- request a session count,
- počet business completions,
- error event count,
- variability metric,
- minimálny zmysluplný efekt,
- dĺžku async workflowu,
- region/tenant distribution.

Pri nízkom trafficu môže byť 1 % nulová vzorka; pri extrémnom trafficu môže byť 1 % príliš veľký blast radius.

## 10. Rollout steps

Príklad:

```text
internal
→ 1 % alebo minimum N events
→ 5 %
→ 20 %
→ 50 %
→ 100 %
```

Každý krok definuje:

- target cohort/weight,
- minimálnu vzorku,
- minimálnu a maximálnu observation duration,
- promotion criteria,
- abort criteria,
- missing-data behavior,
- recovery action.

Timer bez dôkaznej podmienky nie je kvalitný rollout gate.

## 11. Control group a comparability

Canary porovnávaj so stable verziou v rovnakom čase. Control musí byť porovnateľný podľa:

- regionu a zóny,
- route/operation,
- tenant alebo user class,
- request complexity,
- client version,
- capacity a resource pressure.

Historický baseline môže byť doplnok, ale je citlivý na sezónnosť, incidents a workload drift.

## 12. Version-level telemetry

Každý signál musí niesť relevantné dimensions:

- artifact/release version,
- stable/canary cohort,
- rollout step,
- deployment ID,
- region/zone,
- route/operation,
- feature variant,
- tenant segment v súlade s privacy.

Ak telemetry nevie odlíšiť stable a canary, analýza nemá platný subject.

## 13. Technické guardrails

- request error rate,
- p95/p99 latency,
- restart/crash rate,
- CPU, memory, pools a queues,
- dependency failure a retry rate,
- saturation a load shedding,
- queue lag,
- cache hit rate,
- connection errors.

Porovnávaj normalizované metriky na request alebo instance. Malá canary fleet môže byť preťažená aj pri nízkom celkovom podiele trafficu.

## 14. Funkčné a business guardrails

- journey completion,
- payment/order correctness,
- authorization a tenant isolation,
- duplicate alebo missing side effects,
- event processing completion,
- conversion alebo task success,
- support/user signal.

HTTP 200 a nízky CPU nedokazujú správny používateľský výsledok.

## 15. Promotion policy

Promotion môže vyžadovať:

```text
required evidence complete
AND sample size >= minimum
AND technical deltas within limits
AND business guardrails healthy
AND no critical data/security invariant violation
```

Niektoré metrics používajú absolútny threshold, iné delta voči control. Policy musí byť versionovaná a auditovateľná.

## 16. Abort policy

Abort criteria majú byť vopred konkrétne:

- prvá data-integrity alebo authorization violation,
- error-budget burn nad limit,
- p99 latency delta počas definovaného okna,
- business success pokles nad hranicu,
- neočakávaný dopad mimo cohort,
- strata telemetry,
- canary capacity saturation.

Abort neznamená automaticky binary rollback. Môže odstrániť traffic, vypnúť feature alebo zastaviť producers.

## 17. Pause a inconclusive

Výsledok `inconclusive` je správny, keď:

- vzorka je malá,
- metrics meškajú,
- control nie je porovnateľný,
- prebieha globálny incident,
- telemetry je neúplná,
- experiment bol zasiahnutý inou zmenou.

Pause zachová malý scope, ale potrebuje timeout a ownera. Nekonečný pause vytvára stale mixed-version state.

## 18. Automated canary analysis

Controller vykonáva:

1. nastav exposure,
2. over routing state,
3. čaká na minimum evidence,
4. načíta a validuje telemetry,
5. porovná canary/control,
6. aplikuje policy,
7. zaznamená verdict,
8. vykoná promotion alebo recovery.

Musí rozlišovať metric failure od application failure. Query error alebo prázdny report nesmie byť pass.

## 19. Štatistická opatrnosť

Canary analýza je citlivá na:

- malú vzorku,
- rare failures,
- repeated peeking,
- mnoho súčasne sledovaných metrics,
- cohort imbalance,
- delayed outcomes,
- novelty a seasonality.

Nie každý rollout potrebuje formálny hypothesis test, ale musí poznať neistotu a nepoužívať falošnú presnosť.

## 20. Capacity a autoscaling

Canary fleet musí byť dimenzovaná podľa requests per instance, nie iba percenta fleet.

Kontroluj:

- minimum replicas,
- zone distribution,
- autoscaler response,
- warm-up,
- connection pools,
- load-balancer weighting,
- cache state,
- pod disruptions.

Autoscaling môže meniť počet instances a skresliť porovnanie, ak metrics nie sú normalizované.

## 21. Stateful compatibility

Overlap vyžaduje kompatibilitu:

- databázových reads/writes,
- events a queue messages,
- cache/session schemas,
- background jobs,
- long-lived workflows,
- feature-flag state.

Routing rollback nevráti data state. Canary write môže poškodiť aj control používateľov, ak zdieľajú databázu.

## 22. Long-lived connections

WebSockets, streams a keep-alive môžu zostať na starej verzii po zmene weightu. Rieš:

- max connection age,
- controlled reconnect,
- drain,
- session affinity,
- telemetry pre nové verzus existujúce connections,
- separate rollout criteria.

## 23. Background workers a batch jobs

Request canary neotestuje automaticky workers. Možnosti:

- samostatný worker cohort,
- shadow consumer bez side effects,
- isolated queue/partition,
- idempotent production canary,
- schedule experiment v definovanom okne.

Delayed batch alebo settlement failure potrebuje dlhšiu validation fázu než HTTP rollout.

## 24. Security, privacy a fairness

Cohort targeting je produkčná policy. Kontroluj:

- oprávnenosť segmentácie,
- zákaz diskriminačných pravidiel,
- minimalizáciu user identifiers,
- audit assignmentu,
- interné privileged cohorts,
- retention experiment metadata,
- authorization invariant nezávislý od feature flagu.

## 25. Interference a concurrent changes

Súbežný deployment, config zmena alebo incident znižujú atribúciu. Použi:

- environment rollout lock,
- deployment markers,
- change freeze iba počas krátkeho decision window,
- explicitný zoznam concurrent changes,
- invalidation verdictu pri zmene subjectu.

## 26. Recovery options

- odobrať canary traffic,
- vypnúť feature flag,
- scale canary na nulu,
- rollback artifact,
- roll-forward fix,
- zastaviť writes/consumers,
- kompenzovať side effects,
- obnoviť dáta.

Vyber podľa failure domainu. Traffic removal je rýchle, ale nemusí riešiť poškodený state.

## 27. Delayed validation

Po 100 % promotion pokračuj v monitorovaní failure modes, ktoré sa prejavia neskôr:

- memory leak,
- queue accumulation,
- cron/batch job,
- certificate refresh,
- cache churn,
- settlement a reconciliation,
- dlhé user journeys.

Full exposure nie je automaticky final acceptance.

## 28. Failure taxonomy

- deployment/readiness failure,
- cohort-routing failure,
- capacity-induced false regression,
- real technical regression,
- functional/business regression,
- telemetry failure,
- inconclusive sample,
- state corruption,
- recovery failure,
- delayed post-promotion failure.

## 29. Audit trail a evidence

Zachovaj:

- stable/canary identities,
- cohort a routing policy,
- exposure timeline,
- metrics queries a policy version,
- sample size,
- verdict per step,
- manual overrides,
- abort/recovery actions,
- delayed-validation result.

## 30. Metriky stratégie

- mean exposure before detection,
- canary abort rate,
- false abort/rollback rate,
- escaped regression po full promotion,
- inconclusive rate,
- sample sufficiency time,
- rollout duration,
- telemetry completeness,
- rollback eligibility failures,
- user count zasiahnutý pred abortom.

## 31. Typické anti-patterny

### Jeden nový pod bez cohort policy

To nie je canary, iba mixed fleet.

### Promotion iba podľa CPU

Technická stabilita neoveruje funkčný ani business výsledok.

### Percento bez minimálnej vzorky

Observation window môže byť dôkazne prázdna.

### Random routing per request

Stateful journey sa mieša medzi verziami.

### Missing telemetry = pass

Absencia evidence vedie k false promotion.

### Automatický rollback na noisy metric

Vzniká oscillation alebo false rollback.

### Canary config sa líši od final config

Dôkaz nie je prenosný na full rollout.

## 32. Diagnostický postup

1. Over stable/canary digest a config.
2. Over skutočný cohort assignment a traffic weight.
3. Zmeraj requests/sessions per instance a sample size.
4. Skontroluj comparability control group.
5. Validuj telemetry queries a data latency.
6. Rozlíš capacity artifact od code regression.
7. Over stateful side effects a data invariants.
8. Pri abort-e zastav expozíciu a zvoľ správnu recovery vrstvu.
9. Po recovery over control aj affected cohort.
10. Aktualizuj rollout policy alebo skorší test podľa poznatku.

## 33. Rozhodovací rámec

1. Aký release risk má canary odhaliť?
2. Ktorý segment ho reprezentuje?
3. Ako je assignment stabilný a auditovateľný?
4. Aká minimálna vzorka je potrebná?
5. Ktoré technické, funkčné a business guardrails rozhodujú?
6. Aká control group je porovnateľná?
7. Ako sa rieši missing alebo delayed telemetry?
8. Kedy je verdict inconclusive?
9. Sú old/new state-compatible?
10. Aká recovery akcia zodpovedá každému failure typu?
11. Ktoré delayed failures sa sledujú po 100 %?
12. Ako sa výsledok vracia do testov a policy?

## 34. Kontrolný checklist

- immutable stable/canary identities,
- cohort policy a salt sú versionované,
- segment je reprezentatívny,
- sample minimum a duration sú definované,
- control group je porovnateľná,
- telemetry obsahuje version/cohort dimensions,
- metrics queries sú validované,
- promotion/abort/pause/inconclusive policy existuje,
- canary capacity nie je umelo preťažená,
- shared state je compatible,
- recovery rieši aj side effects a dáta,
- privacy a targeting sú auditované,
- delayed validation pokračuje po promotion.

## 35. Kontrolné otázky

1. Čo odlišuje canary od obyčajného mixed rollout-u?
2. Prečo percento trafficu nie je sample size?
3. Ako stabilné cohort assignment chráni stateful journey?
4. Prečo súbežná control group zlepšuje atribúciu?
5. Aký je rozdiel medzi abort, pause a inconclusive?
6. Ako môže malá canary fleet vytvoriť falošnú performance regresiu?
7. Prečo traffic rollback nie je data rollback?
8. Ako testovať worker alebo batch canary?
9. Prečo full promotion neukončuje delayed validation?
10. Aké evidence musí mať automatická canary analysis?

## Summary

Canary deployment je policy-driven progressive exposure novej verzie voči identifikovateľnej control skupine. Jeho kvalita nezávisí od samotného percenta trafficu, ale od stabilného cohort assignmentu, reprezentatívnosti, minimálnej vzorky, version-level telemetry, porovnateľnej baseline a jasných verdictov `promote`, `pause`, `abort` a `inconclusive`. Stateful compatibility a recovery zostávajú kritické, pretože odobratie trafficu nevracia databázové ani externé side effects. Po plnej promotion musí pokračovať validácia oneskorených failure modes.

## Glossary impact

Relevantné pojmy: canary deployment, progressive exposure, canary cohort, stable control, cohort assignment, rollout salt, sample sufficiency, promotion criterion, abort criterion, inconclusive verdict, automated canary analysis, mean exposure before detection a delayed validation.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Blue-green deployment](blue-green-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: A/B testing →](a-b-testing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->