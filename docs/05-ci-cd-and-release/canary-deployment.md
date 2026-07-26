# Canary deployment

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Canary deployment postupne vystavuje nový release obmedzenej a identifikovateľnej časti produkčného workloadu. Jeho cieľom nie je iba znižovať traffic percentage, ale testovať konkrétnu release-risk hypotézu pri bounded blast radiuse a rozhodovať podľa porovnateľnej evidence.

```text
stable baseline
→ immutable canary subject
→ stabilná a reprezentatívna cohorta
→ bounded exposure
→ technical + functional + business evidence
→ promote / pause / abort / inconclusive
→ ďalší krok alebo recovery
→ delayed validation a learning
```

Canary bez cohort identity, control group, sample sufficiency a recovery contractu je iba nejasná mixed fleet.

## 1. Nosný model: riadený experiment pre release safety

Každý Atlas canary krok testuje vetu:

```text
Pri expozícii cohorty C release subjectu M2
zostanú technické, funkčné a business outcomes
v definovaných hraniciach voči porovnateľnému stable controlu S.
```

Z toho vyplýva päť povinných častí:

```text
subject identity
+ cohort assignment
+ porovnateľný control
+ rozhodovací oracle
+ recovery action
```

Percento trafficu samo osebe neodpovedá, kto bol vystavený, aký workload vytvoril, koľko relevantných outcomes vzniklo ani či možno rozdiel pripísať release-u.

## 2. Nosný scenár: Atlas Orders 3.11.0 `riskDecision`

Atlas chce exponovať optional `riskDecision` capability z release manifestu `M2`.

```text
stable manifest M_prev
canary manifest M2
rendered config C17
feature flag revision F22
cohort policy H7
analysis policy P9
```

Release risk nie je iba „server nespadne“. Nový path volá risk dependency, zapisuje enrichment event a mení order response. Atlas preto definuje:

```text
technical hypothesis
→ latency, errors, DB wait, dependency retries ostanú v hraniciach

functional hypothesis
→ jeden logical order na idempotency key a správny riskDecision

business hypothesis
→ order completion a rejection distribution sa nezhoršia
```

Rollout:

```text
internal ring
→ 1 % alebo aspoň 2 000 relevantných orders
→ 5 % vrátane large-tenant segmentu
→ 25 % vo všetkých regiónoch
→ 50 %
→ 100 %
→ delayed async a reconciliation watch
```

Každý krok má minimum sample, minimum a maximum duration, promotion/abort criteria a konkrétnu recovery akciu.

## 3. Experiment identity musí byť reprodukovateľná

Canary verdict patrí presnému subjectu:

```text
M2
+ C17
+ F22
+ cohort policy H7 a salt
+ rollout step 25 %
+ region/route scope
+ analysis query revision Q14
+ policy P9
+ observation window
```

Ak sa zmení config, flag default, cohort salt alebo metrics query, predchádzajúci verdict nemusí zostať platný. Tieto zmeny môžu zmeniť behavior, exposure aj interpretáciu evidence bez zmeny application digestu.

Atlas preto zaznamenáva experiment identity pri každom promotion decisione.

## 4. Cohort musí reprezentovať riziko, nie iba byť malá

Cohort môže byť vytvorená podľa:

- stabilného hashovania user alebo tenant identity;
- interného ring-u;
- regionu alebo availability zone;
- route či operation;
- client version;
- tenant size alebo risk class;
- explicitnej allowlist policy.

Atlas používa stabilné assignment:

```text
bucket = hash(subject_id + rollout_salt) mod N
```

Stabilita chráni stateful journey. Random routing per request by mohol začať order na stable a dokončiť ho na canary, čím by sa znejasnila príčina aj user experience.

Malá cohorta však môže byť nereprezentatívna. Interní používatelia nemajú rovnaký data skew, veľké tenants ani client versions ako produkcia. Preto Atlas stratifikovane zahrnie segmenty spojené s konkrétnym rizikom.

## 5. Traffic percentage a sample sufficiency sú odlišné veličiny

`1 %` môže znamenať:

- nula relevantných udalostí pri nízkom trafficu;
- desaťtisíce používateľov pri vysokom trafficu;
- veľa jednoduchých reads, ale žiadne long-running orders;
- prevažne jeden region alebo tenant class.

Canary gate preto čaká na:

```text
minimum requests alebo sessions
+ minimum business completions
+ minimum occurrences risk pathu
+ potrebné region/tenant zastúpenie
+ observation čas pokrývajúci failure latency
```

Ak minimum nevznikne do maximum duration, verdict je `inconclusive`, nie pass.

## 6. Control group musí byť porovnateľná v rovnakom čase

Atlas porovná canary so stable controlom podľa:

- regionu a zóny;
- operation a request complexity;
- tenant-size tier;
- client version;
- resource pressure;
- časového okna;
- feature eligibility.

Historický baseline je doplnok. Súčasný control lepšie oddeľuje release effect od regionálneho incidentu, sezónnosti alebo traffic spike-u.

Ak canary obsahuje veľkých tenants a control iba malých, rozdiel nemožno pripísať artifactu. Cohort composition je súčasť evidence provenance.

## 7. Oracle má tri vrstvy

### Technical oracle

```text
5xx a timeout rate
p95/p99 latency
DB connection wait
risk dependency retry rate
worker backlog a saturation
```

### Functional oracle

```text
CreateOrder completion
jeden order na idempotency key
správny riskDecision contract
authorization a tenant isolation
event processing completion
```

### Business oracle

```text
order completion rate
rejection distribution
manual-review volume
support contact a abandonment
```

Server health nemôže nahradiť functional ani business outcome. HTTP 200 môže obsahovať nesprávne rozhodnutie; normálna CPU môže sprevádzať duplicate side effects.

## 8. Promotion policy je explicitný viacstavový decision contract

Atlas policy vyžaduje:

```text
required evidence complete
AND sample sufficient
AND control porovnateľný
AND technical deltas v hraniciach
AND functional invariants healthy
AND business guardrails healthy
AND žiadna critical security/data violation
```

Verdicty:

- `PROMOTE` — podmienky sú splnené;
- `PAUSE` — scope zostáva malý a treba ďalšiu triage alebo čas;
- `ABORT` — exposure sa nesmie rozšíriť;
- `INCONCLUSIVE` — evidence nestačí alebo nie je porovnateľná;
- `ROLLBACK` — previous subject je state-compatible;
- `ROLL_FORWARD` — oprava je bezpečnejšia než návrat.

Query error, missing report alebo prázdna time series nie sú nulový počet failures. Sú chýbajúca evidence.

## 9. Observation window vychádza z mechanizmu failure

Rôzne riziká sa prejavia v inom čase:

```text
routing/startup failure → sekundy
retry amplification a queue growth → minúty
large-tenant completion → desiatky minút
batch, settlement alebo reconciliation → hodiny
memory leak alebo retention → dlhšie obdobie
```

Atlas nepromotuje po piatich zelených requestoch, ak risk path obsahuje tridsaťminútový async retry cyklus. Po 100 % exposure pokračuje delayed validation pre failures, ktoré nemohli vzniknúť v menšom alebo kratšom kroku.

## 10. Canary capacity musí byť posúdená per instance

Malá canary fleet môže dostať malý podiel celkového trafficu, ale veľa trafficu na jednu instance.

```text
stable = 20 instances, 95 % traffic
canary = 1 instance, 5 % traffic
```

Pri rovnomernom workloade môže canary dostať približne rovnaký requests-per-instance ako stable. Pri sticky sessions, zone skew alebo nerovnakej instance class môže dostať podstatne viac.

Atlas sleduje:

- requests a sessions per instance;
- CPU/memory/pool pressure per instance;
- zone distribution;
- autoscaler response;
- cache warm-up;
- load-balancer effective weights.

Inak môže capacity artifact vyzerať ako code regression.

## 11. Shared state rozširuje blast radius za hranice cohorty

Canary používateľ môže zapisovať do spoločnej databázy alebo emitovať event, ktorý spracuje stable worker. Preto obmedzený traffic neznamená automaticky obmedzený state impact.

Compatibility zahŕňa:

```text
old/new database reads a writes
events a queue messages
cache a session schemas
background workers
long-lived workflows
external side effects
```

Traffic removal zastaví nové requests, no neodstráni rows, messages, payments alebo notifications, ktoré už canary vytvorila. Recovery package preto obsahuje feature disable, producer stop, reconciliation a compensating actions.

## 12. Worked failure: nereprezentatívna cohorta skryla capacity problém

Prvých 5 % Atlas canary tvorili prevažne malí tenants. `riskDecision` path bol zelený.

```text
small-tenant canary
→ nízky počet paralelných items per order
→ DB wait a worker backlog normálne
→ promotion na 100 %
→ large tenants aktivujú stovky items
→ risk calls a enrichment writes rastú
→ DB pool a worker partitions sa saturujú
→ order completion prudko klesne
```

### Príčina

Assignment bolo stabilné, ale nereprezentovalo workload dimension spojenú s rizikom. Tím považoval percento trafficu za reprezentatívnu vzorku.

### Dôsledok

Release effect sa prejavil až po plnej promotion, keď už blast radius nebol bounded.

### Trvalá náprava

```text
tenant-size stratification
→ samostatný large-tenant step
→ minimum risk-path volume
→ DB wait a queue age per segment
→ capacity fixture s produkčnou distribúciou
→ post-promotion watch
```

## 13. Worked failure: missing telemetry sa vyhodnotila ako pass

Pri 25 % kroku zlyhala business-events pipeline. Query pre `order_completion_rate` vrátila prázdny dataset.

```text
technical metrics healthy
→ business query empty
→ aggregator použije default delta = 0
→ verdict PROMOTE
→ 100 % exposure
→ nový timeout path znižuje completion
→ chýbajúci business signal incident skryje
```

### Príčina

Decision contract nerozlišoval healthy metric, no-data stav a query/tool failure. Expected evidence manifest nevyžadoval explicitný execution status business query.

### Náprava

- každá required metric má expected identity a execution status;
- no-data, delayed a query-error stavy vedú k `INCONCLUSIVE` alebo `PAUSE`;
- telemetry pipeline má vlastný SLO a synthetic heartbeat;
- manual override potrebuje scoped risk acceptance a expiry;
- promotion record uchová query revision aj raw evidence digest.

## 14. Kauzálny diagnostický walkthrough

Symptom: pri 25 % kroku má canary vyššiu p99 latency a nižšiu order completion než stable.

### Krok 1 — stabilizuj experiment subject

```text
stable = M_prev
canary = M2 + C17 + F22
cohort policy H7
step = 25 %
query revision Q14
window = 14:00–14:30
```

Bez toho by sa mohli miešať iné configy, cohorty alebo metrics queries.

### Krok 2 — formuluj konkurenčné hypotézy

```text
H1: M2 má code regression
H2: canary fleet je kapacitne preťažená
H3: canary cohort obsahuje ťažší workload než control
H4: regionálna risk dependency degraduje obe verzie
H5: telemetry query alebo latency vytvára falošný rozdiel
```

### Krok 3 — vyber observation points, ktoré hypotézy rozlíšia

- requests a resource pressure per instance testujú H2;
- tenant/region/operation distribution testuje H3;
- stable a canary dependency latency v rovnakom regióne testuje H4;
- raw event count, query status a ingestion lag testujú H5;
- rovnaký bounded synthetic na stable a canary testuje H1 pri kontrolovanom inpute.

Atlas zistí:

```text
canary requests per instance = 2.4× stable
cohort composition je porovnateľná
risk dependency latency je rovnaká
business telemetry je complete
bounded synthetic sa po scale-up vráti k stable latency
```

Evidence podporuje H2, nie H1, H3, H4 ani H5.

### Krok 4 — zastav promotion, ale nepredstieraj code failure

Atlas dá `PAUSE`, zvýši canary minimum replicas a upraví weight tak, aby requests per instance boli porovnateľné. Automatický binary rollback by odstránil predmet experimentu bez potvrdenia code regresie.

### Krok 5 — zopakuj rovnaký decision contract

Po scale-up-e sa znova zbiera minimálna vzorka. Promotion je povolená iba keď technical, functional aj business deltas zostanú zdravé pri porovnateľnom load-e.

### Krok 6 — zachovaj learning

Failure sa mení na precheck `effective requests per canary instance`, minimum replica policy a test sticky-routing/capacity interaction. Diagnostický výsledok sa nestane iba poznámkou v incidente.

## 15. Recovery sa vyberá podľa failure boundary

- routing/cohort failure: odobrať traffic;
- feature behavior failure: flag na off;
- application binary failure: rollback alebo roll-forward;
- producer/event failure: zastaviť producers a consumers;
- data integrity failure: write freeze, reconciliation alebo restore;
- external side effect: compensating action;
- telemetry failure: pause/inconclusive, nie automatická promotion.

Traffic rollback je najrýchlejší containment, ale nemusí byť úplnou recovery.

## 16. Diagnostický runbook

1. Potvrď stable/canary manifest, config, flag, cohort a rollout step.
2. Over skutočný assignment, traffic a requests per instance.
3. Porovnaj cohort composition a control comparability.
4. Rozdeľ technical, functional a business signals.
5. Validuj sample sufficiency, query status a telemetry latency.
6. Formuluj code, capacity, cohort, dependency a telemetry hypotézy.
7. Nájdite observation point, ktorý ich rozlíši.
8. Zastav promotion alebo zníž exposure podľa abort contractu.
9. Vyber recovery podľa application, data a side-effect compatibility.
10. Po recovery zopakuj pôvodný outcome a pridaj skorší control.

## 17. Referenčné pravidlá

- Canary je experiment nad explicitným release-riskom.
- Artifact, config, flag, cohort a query identity patria do subjectu.
- Percento trafficu nie je sample size ani reprezentatívnosť.
- Assignment má byť stabilný pre stateful journey.
- Control group musí byť porovnateľná v rovnakom čase.
- Oracle kombinuje technical, functional aj business outcomes.
- Missing, delayed alebo neporovnateľná evidence vedie k `inconclusive`.
- Observation window sa odvodzuje z failure latency.
- Capacity sa hodnotí per instance a per segment.
- Traffic removal nevracia shared state ani external side effects.
- Produkčný finding sa vracia do prechecku, testu alebo trvalého guardrailu.

## 18. Časté omyly

### „Jeden nový pod je canary“

Bez cohort policy, controlu a evidence je to iba mixed fleet.

### „5 % je bezpečná a reprezentatívna vzorka“

Záleží od absolútneho počtu outcomes a workload composition.

### „Zelené server metrics stačia“

Functional alebo business journey môže byť chybný.

### „No data znamená no failures“

Chýbajúca evidence je `inconclusive`, nie pass.

### „Rollback trafficu opraví incident“

Canary mohla zmeniť databázu, eventy alebo external systems.

## 19. Zhrnutie

Atlas canary lifecycle je:

```text
explicitný release-risk contract
→ immutable stable/canary subject
→ stabilná a reprezentatívna cohorta
→ porovnateľný concurrent control
→ sample-aware bounded exposure
→ technical + functional + business oracle
→ promote/pause/abort/inconclusive
→ state-compatible recovery
→ delayed watch a skorší regression control
```

Canary znižuje exposure pred detekciou iba vtedy, keď rozumie tomu, koho exponuje, čo meria a aký mechanizmus môže výsledok skresliť. Riadené percentá bez kauzálnej evidence sú iba pomalší rollout.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Blue-green deployment](blue-green-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: A/B testing →](a-b-testing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
