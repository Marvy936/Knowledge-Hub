# SLI, SLO a SLA

SLI, SLO a SLA nie sú tri názvy pre rovnaké percento. **Service Level Indicator** je versionovaný measurement contract nad presnou population. **Service Level Objective** je interný alebo shared target nad týmto indicatorom počas definovaného okna a s explicitnou response policy. **Service Level Agreement** je dohoda s consumerom, ktorá môže pridať reporting, exclusions, support záväzky a remedy. Platný SLA report preto nemusí dokazovať dobrú user experience a zelený component metric nemusí byť platný SLI.

Návrh sa má začať user journey, nie metricou, ktorú už exportuje load balancer. Atlas Payments potrebuje vedieť, či potvrdený settlement skončil u providera exactly once do desiatich minút. HTTP status na acceptance boundary je užitočný, ale nedokáže tento outcome reprezentovať sám.

## 1. Dominantný journey-to-decision model

Service-level control loop prekladá používateľskú potrebu na meranie a následné rozhodnutie. Measurement pipeline je súčasťou contractu; ak stráca udalosti alebo oneskoruje final outcomes, neistota sa musí objaviť vo verdicte.

```text
user journey a required outcome
→ exact SLI subject a eligible population
→ authoritative observation point
→ good/bad/missing classification
→ versioned measurement pipeline
→ SLI result a confidence
→ SLO target a compliance window
→ error-budget a operational action
→ optional SLA commitment/report/remedy
→ original a forbidden outcome validation
```

SLI odpovedá „čo sa stalo“. SLO odpovedá „koľko failure-u je ešte prijateľné a čo urobíme“. SLA odpovedá „čo sme s consumerom dohodli a aké sú následky“. Zámena týchto vrstiev vytvára falošné green statusy a zlé incentives.

## 2. Exact service-level subject

SLO statement bez population, success criteria a window-u nie je reprodukovateľný. Exact subject zachováva capability, cohort, operation identity, event eligibility, required outcome, observation point, source/schema/query generation, time window, exclusions, missing-data semantics, ownera a response policy.

```text
SLI ID: SLI-SET-COMPLETE-03
capability: settlement completion
population: acknowledged unique production settlement intents
cohorts: all merchants + separate top-tier merchant view
good: provider-confirmed exactly once do 10 minút
bad: late, duplicate, terminally failed alebo lost intent
missing: unresolved po evidence-lateness budgete
observation: reconciled payment/broker/provider ledger
query generation: q-set-complete-17
window: rolling 28 days
SLO: 99.9 %
owner: Payments Product + SRE
```

Zmena query, source schema, idempotency semantics alebo provider ledgeru vytvára novú measurement generation. Historical verdict sa nemá spätne prepísať bez preserved old resultu a vysvetlenej correction lineage.

## 3. Population, denominator a operation identity

Event-based SLI má typicky tvar:

```text
SLI = good eligible events / total eligible events
```

Najťažšia časť nie je delenie, ale denominator. Tím musí rozhodnúť, či population obsahuje invalid authentication, malformed payloads, rate-limited valid traffic, client cancellations, synthetic checks, retries, duplicate idempotency attempts a operations bez final outcome-u.

Transport-attempt SLI a business-operation SLI odpovedajú na inú otázku. Prvý ukazuje load a request experience; druhý ukazuje, či jeden merchant intent skončil správne. Ak sa tri retries započítajú ako tri samostatné failures, budget meria transport attempts. Ak sa zoskupia podľa idempotency keyu, meria unique business operations. Obe môžu byť potrebné, ale nesmú používať rovnaké meno a target bez vysvetlenia.

Exclusions musia byť bounded a auditable. Validný request odmietnutý pre interný capacity limit nie je automaticky „client error“. Planned maintenance nezmizne z user experience iba tým, že bola naplánovaná. Dependency outage nie je automaticky mimo end-to-end service contractu.

## 4. Good, bad a missing outcome

Good event musí reprezentovať user-relevant výsledok. Pre synchronous read môže znamenať correct authorized response pod latency thresholdom. Pre asynchronous settlement potrebuje celý chain:

```text
durably acknowledged intent
+ provider-confirmed final operation
+ exactly-once business effect
+ completion do 10 minút
```

HTTP `202` je iba acceptance evidence. Môže byť good pre acceptance SLI a súčasne insuficientný pre completion SLI. Jedna journey preto často potrebuje oddelené objectives pre acceptance, completion, correctness a durability. Tieto objectives sa nekompenzujú priemerom.

Missing evidence nie je success. Ak provider ledger mešká alebo telemetry pipeline stratí events, SLI potrebuje explicitný evidence-lateness budget. Po jeho prekročení môže outcome prejsť do `unknown`, ktoré policy považuje za bad alebo za samostatný blocking evidence state. „Nula bad events“ bez coverage proofu nie je pozitívny verdict.

## 5. Observation point a measurement pipeline

Observation point má byť čo najbližšie k authoritative user outcome-u. Server-side request logs poskytujú vysokú coverage, ale nevidia failure pred serverom a často nepoznajú downstream completion. Client alebo edge telemetry je bližšie user experience, ale trpí samplingom a privacy constraints. Business ledger poskytuje authoritative completion, no prichádza neskôr a potrebuje reconciliation.

Kompletný measurement subject obsahuje aj pipeline:

```text
business event
→ instrumentation alebo ledger record
→ collection a transport
→ ingestion
→ deduplication a correlation
→ good/bad/missing classification
→ query generation
→ SLI result
```

Každá vrstva potrebuje coverage, lateness, duplicate, schema a retention semantics. Monitoring outage počas service outage-u nesmie automaticky vytvoriť 100 % success. Backfill môže opraviť report, ale incident response musí zachovať aj verdict dostupný v čase rozhodnutia.

## 6. SLO ako target a action contract

SLO určuje cieľ alebo range nad konkrétnym SLI počas compliance window-u. Dobrý statement je napríklad:

```text
99.9 % acknowledged unique settlement intents
bude provider-confirmed exactly once do 10 minút
počas rolling 28-day window-u.
```

SLO obsahuje target, window, cohort, ownera, error-budget policy, review triggers a known limitations. Target sa nemá mechanicky odvodiť z aktuálneho priemeru. Vychádza z user potreby, business impactu, dependency capabilities, architecture costu a risk tolerance. Príliš voľný target legalizuje zlú službu; nereálne prísny target vytvára heroics alebo metric gaming.

Rolling window priebežne pridáva nové a odstraňuje staré events. Calendar window sa resetuje na pevnej hranici a je praktická pre reporting alebo contracts, ale reset neodstraňuje root cause. Výber ovplyvňuje burn-rate alerting, seasonality, low-volume cohorts a release decisions.

## 7. SLA ako externý commitment

SLA môže používať podobný indicator, ale pridáva consumer-facing scope, measurement source, reporting period, exclusions, claim process a remedy. Interný SLO býva prísnejší než external commitment, aby vytvoril engineering margin.

```text
internal completion SLO: 99.9 % / rolling 28 dní
external SLA commitment: 99.5 % / calendar month
```

Rozdiel nie je povinný a nesmie byť zámienkou na ignorovanie users pod contractual thresholdom. SLA success môže stále zakryť critical cohort failure, príliš široké exclusions alebo user journey, ktorú agreement vôbec nemeria.

## 8. Connected failure `SRE-PAY-52`

Pôvodný dashboard používal:

```text
SLI-HTTP-01 = HTTP 2xx a 3xx / všetky ALB requests
SLO = 99.95 % / rolling 28 dní
```

Počas broker partition API stále commitovalo payment/outbox transaction a vracalo `202`. Cleanup následne zmazal `4 182` unpublished commands. `SLI-HTTP-01` ostalo zelené, pretože meralo front-door response, nie final settlement completion.

Redesign vytvoril tri samostatné subjects:

```text
SLI-SET-ACCEPT-02
population: valid unique settlement attempts
good: durable payment + outbox commit a truthful ack
objective: 99.95 % / rolling 28 dní

SLI-SET-COMPLETE-03
population: acknowledged unique settlement intents
good: provider-confirmed exactly once do 10 minút
objective: 99.9 % / rolling 28 dní

SLI-SET-DURABLE-01
population: acknowledged intents retained 90 dní
good: reconstructable z production alebo approved recovery lineage
objective: 99.9999 % / rolling annual window
```

Acceptance objective ukazuje, či front door správne prijíma intent. Completion objective odhalí async failure. Durability objective sa neopiera iba o production rows, ale o pravidelný restore a reconciliation canary.

## 9. Confidence, cohorts a competing interpretations

Pri zhoršení SLI treba odlíšiť reálny user impact od measurement defectu. Možné hypotézy sú: service failure, jeden affected tenant, stale provider ledger, duplicate classification po retry, schema rollout, query regression alebo telemetry loss.

Discriminating evidence zahŕňa raw event counts, expected inventory, source lag, schema generation, query diff, cohort decomposition a nezávislý business ledger. Ak server-side success zostáva zelený a provider-confirmed completion klesne iba pre jednu Region, problém nie je možné uzavrieť ako „monitoring noise“ bez operation-level correlation.

SLO report má uvádzať confidence a limitations. Low-volume cohort potrebuje dlhšie okno, synthetic probe alebo binomial uncertainty interpretation; nemá sa skrývať v high-volume aggregate.

## 10. Service-level acceptance contract

Positive acceptance musí preukázať, že validná operation vstúpi do správnej population, good outcome sa zachytí na authoritative observation point-e a SLO query vráti očakávaný verdict. Jeden intentional bad event musí spotrebovať správny denominator a error budget.

Forbidden paths musia byť viditeľné. Late completion, duplicate provider effect, missing telemetry, stale query generation, invalid exclusion a úplný failure jedného tenant cohortu nesmú zostať zelené. SLA report nesmie spätne preklasifikovať incident iba preto, aby sa zmestil do commitmentu.

```text
positive:
known good operation → good event → SLI/SLO success

controlled bad:
known bad operation → bad event → budget consumption

forbidden:
missing evidence as success
retry amplification hidden
critical cohort averaged away
old query used after schema change
SLA exclusion without approved contract
```

Acceptance verdict patrí exact source, schema, query a window generation. Druhá Region alebo nový provider potrebuje vlastný correlation test.

## 11. Troubleshooting flow

Pri spore o SLO najprv zachovaj exact subject a query generation. Potom porovnaj expected population s observed denominatorom, good/bad/missing classification a raw source lag. Až následne analyzuj technical cause user failure-u.

```text
user symptom
→ SLI subject a cohort
→ expected vs observed population
→ source/schema/query generation
→ observation lateness a coverage
→ good/bad/missing classification
→ service alebo evidence hypothesis
→ discriminating operation samples
→ corrected verdict
→ operational action
```

Dashboard screenshot bez query, window a source generation nie je dostatočné incident evidence.

## 12. Anti-patterny

### Začať metricou, ktorú už máme

Easy-to-export CPU alebo HTTP status môže byť diagnostický signal, ale nie user-relevant SLI.

### `2xx` equals success

Status code môže potvrdiť iba jednu protocol boundary. Async a business completion potrebuje samostatný oracle.

### Missing telemetry equals zero errors

Evidence outage znižuje confidence a môže vytvoriť blocking unknown state; nesmie zlepšiť SLI.

### Jeden global objective

Aggregate SLO skryje tenant, Region, operation alebo release cohort failure.

### SLA diktuje interné meranie

External agreement je minimum commitmentu, nie horná hranica interného user-centric observability.

## 13. Kontrolné otázky

1. Čo tvorí exact SLI subject?
2. Prečo denominator patrí do contractu?
3. Ako sa líši transport attempt od unique business operation?
4. Prečo `202` môže byť good pre acceptance a bad pre completion?
5. Čo znamená missing evidence?
6. Ako sa líši SLI, SLO a SLA?
7. Prečo target nevychádza automaticky z aktuálneho priemeru?
8. Kedy použiť rolling a kedy calendar window?
9. Ako partial cohort failure zostane skrytý?
10. Ktoré evidence odlíši service failure od query regression?
11. Čo musí positive a forbidden acceptance test overiť?
12. Prečo SLA success nemusí znamenať dobrú user experience?

## Glossary impact

Relevantné pojmy: service-level subject, eligible population, operation-level SLI, good event, bad event, missing outcome, observation point, measurement generation, SLO action contract, compliance window, cohort SLO, SLA commitment a service-level acceptance contract.

## Primárne zdroje

- [Google SRE — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/)
- [Google SRE Workbook — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- [Google SRE — Availability Table](https://sre.google/sre-book/availability-table/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Reliability, availability a durability](reliability-availability-durability.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Error budgets →](error-budgets.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
