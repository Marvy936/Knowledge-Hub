# A/B testing

A/B testing porovnáva dve alebo viac variantov správania na súbežných skupinách používateľov s cieľom zmerať rozdiel v definovanom výsledku. Je to experimentačná technika pre produktové alebo behaviorálne rozhodnutia, nie deployment stratégia sama osebe.

## 1. Základný model

```text
eligible population
→ deterministic assignment
→ control A / treatment B
→ exposure logging
→ outcome measurement
→ statistical and practical evaluation
→ product decision
```

Variant B môže byť nasadený pomocou feature flagu, canary infraštruktúry alebo samostatného deployment targetu. Mechanizmus doručenia však nie je experimentálny dizajn.

## 2. A/B test vs. canary deployment

**Canary deployment** primárne odpovedá:

> Je nová verzia dostatočne bezpečná na širší rollout?

**A/B testing** primárne odpovedá:

> Ktorý variant vedie k lepšiemu používateľskému alebo business výsledku?

Canary sa často vyhodnocuje podľa reliability a safety metrík. A/B test potrebuje experimentálnu hypotézu, control group, outcome metrics a analýzu biasu.

## 3. Experiment hypothesis

Dobrá hypotéza je explicitná:

```text
Ak zmeníme onboarding flow z A na B,
noví používatelia dokončia aktiváciu častejšie,
bez zhoršenia support rate a error rate.
```

Musí obsahovať:

- population,
- treatment,
- primary outcome,
- očakávaný smer alebo efekt,
- observation horizon,
- guardrail metrics.

## 4. Experiment unit

Randomizovať možno podľa:

- user ID,
- account alebo tenant ID,
- device ID,
- session,
- requestu,
- geografického clusteru,
- organizácie.

Unit musí zodpovedať tomu, kde môže treatment ovplyvniť výsledok. Pri team collaboration produkte randomizácia jednotlivcov v jednom tíme môže spôsobiť interference medzi variantmi.

## 5. Deterministic assignment

Použi stabilný identifikátor a versioned experiment salt:

```text
bucket = hash(subject_id + experiment_key) mod N
```

Požiadavky:

- rovnaký subjekt zostáva v rovnakom variante,
- assignment je auditovateľný,
- rollout percentage možno meniť bez neúmyselného reshuffle,
- experimenty nemajú kolidovať,
- missing identity má explicitné správanie.

Random assignment pri každom requeste porušuje experimentálnu konzistenciu.

## 6. Eligibility

Pred assignmentom definuj, kto môže vstúpiť do experimentu:

- noví vs. existujúci používatelia,
- krajina alebo právna jurisdikcia,
- plan alebo tenant tier,
- client version,
- device capability,
- používateľské nastavenie,
- predchádzajúca exposure.

Eligibility zmenená počas experimentu môže meniť population mix a skresliť výsledok.

## 7. Exposure event

Assignment nie je to isté ako exposure. Používateľ môže byť zaradený do B, ale variant reálne neuvidí.

Exposure event má obsahovať:

- experiment ID a version,
- variant,
- stable subject ID alebo privacy-safe key,
- timestamp,
- eligibility context,
- application version,
- relevantný request/session ID.

Outcome sa má analyzovať podľa vopred zvoleného modelu, napríklad intention-to-treat alebo exposed population.

## 8. Metrics hierarchy

### Primary metric

Hlavný výsledok, podľa ktorého sa rozhoduje.

### Secondary metrics

Pomáhajú vysvetliť mechanizmus alebo dopad.

### Guardrail metrics

Nesmú sa neprijateľne zhoršiť, napríklad:

- error rate,
- latency,
- cancellation rate,
- support contacts,
- abuse alebo fraud,
- accessibility,
- revenue quality,
- retention.

### Diagnostic metrics

Pomáhajú analyzovať segmenty a technické príčiny, ale nemajú sa post hoc meniť na hlavný cieľ.

## 9. Statistical significance vs. practical significance

Štatisticky detegovateľný rozdiel nemusí byť produktovo významný. Pred experimentom definuj:

- baseline rate,
- minimum detectable effect,
- significance alebo credible interval policy,
- požadovanú power,
- maximálnu duration,
- rozhodovací threshold.

Veľmi veľká vzorka môže označiť zanedbateľný efekt za štatisticky významný.

## 10. Sequential peeking

Opakované sledovanie výsledku a ukončenie pri prvom priaznivom čísle zvyšuje false-positive riziko.

Možnosti:

- pevne definovaná sample size a duration,
- sequential testing s korektnou boundary,
- Bayesian decision policy,
- explicitný early-stop model pre harm.

Safety guardrail môže experiment zastaviť okamžite aj pri inom analytickom modeli.

## 11. Sample ratio mismatch

Ak sa očakáva 50/50, ale reálna exposure je 57/43, môže ísť o:

- assignment bug,
- variant-specific crash,
- logging loss,
- cache alebo routing problém,
- eligibility rozdiel,
- bot traffic,
- client incompatibility.

Sample ratio mismatch treba vyšetriť pred interpretáciou outcome.

## 12. Interference a network effects

Výsledok jedného subjektu môže ovplyvniť iných, napríklad:

- marketplace supply a demand,
- social feed,
- collaboration,
- shared tenant quota,
- pricing,
- recommendation inventory.

Vtedy môže byť potrebná cluster randomization, geo experiment alebo switchback design.

## 13. Novelty a learning effects

Krátkodobý efekt môže vzniknúť iba preto, že zmena je nová. Naopak, používateľ môže potrebovať čas na naučenie nového flow.

Observation horizon musí pokryť:

- celý business cycle,
- weekday/weekend variation,
- retention window,
- delayed outcomes,
- adaptation.

## 14. Multiple experiments

Súbežné experimenty môžu interagovať. Potrebné sú:

- experiment namespaces,
- mutual exclusion groups,
- dependency metadata,
- exposure joinability,
- interaction analysis pri kritických kombináciách.

Globálne vypnutie všetkých kombinácií znižuje experimentačnú kapacitu; úplné ignorovanie interakcií znižuje dôveryhodnosť.

## 15. Experiment lifecycle

```text
draft hypothesis
→ review metrics and ethics
→ validate instrumentation
→ dry run / A-A test
→ limited rollout
→ full planned exposure
→ analysis
→ decision
→ rollout or removal
→ archive experiment record
```

A-A test môže odhaliť assignment, logging a analysis pipeline problémy bez rozdielneho treatmentu.

## 16. Ethics, privacy a compliance

Over:

- či treatment môže poškodiť používateľa,
- či je potrebný consent alebo disclosure,
- či nie je segmentácia diskriminačná,
- minimalizáciu osobných údajov,
- retention experiment dát,
- citlivé segmenty,
- právo používateľa opt-out,
- právne obmedzenia podľa jurisdikcie.

Nie každý produktový nápad je vhodný na tichý experiment.

## 17. Operational safety

Experiment musí mať:

- ownera,
- kill switch,
- guardrail alerts,
- max exposure,
- expiry,
- on-call context,
- rollback alebo disable postup.

Experiment platforma je produkčný control plane a vyžaduje audit, least privilege a vysokú dostupnosť.

## 18. Troubleshooting

### Variant B má menej exposure eventov než assignmentov

Over rendering path, crashes, client compatibility, ad blockers, logging a network failures.

### Výsledok sa líši podľa dashboardu

Skontroluj metric definition, attribution window, timezone, deduplication, late events a inclusion rules.

### Experiment je pozitívny iba v jednom segmente

Rozlišuj vopred plánovanú segmentáciu od post hoc data dredging. Over sample size a interaction effect.

### Po ukončení experimentu sa efekt stratil

Možné novelty effect, seasonality, instrumentation drift alebo zmena population mixu.

## 19. Anti-patterny

### Testujeme bez primárnej metriky

Po výsledku sa vyberie najpriaznivejšie číslo.

### 50/50 routing = A/B test

Bez assignment integrity, exposure a outcome modelu ide iba o traffic split.

### Experiment beží bez expiry

Varianty sa menia na nezdokumentovanú permanentnú konfiguráciu.

### Každý používateľ vidí oba varianty

Carryover a learning effects môžu znemožniť interpretáciu.

### Štatistická významnosť = automatický rollout

Rozhodnutie musí zahŕňať practical effect, guardrails, náklady, ethics a dlhodobý dopad.

## 20. Kontrolné otázky

1. Aký je rozdiel medzi A/B testom a canary deploymentom?
2. Ako zvoliť správnu experiment unit?
3. Prečo assignment nie je exposure?
4. Čo je primary metric a guardrail metric?
5. Čo je minimum detectable effect?
6. Prečo je sequential peeking problém?
7. Čo signalizuje sample ratio mismatch?
8. Kedy treba cluster randomization?
9. Na čo slúži A-A test?
10. Aké etické a privacy kontroly má experiment potrebovať?

## Glossary impact

Relevantné pojmy: A/B testing, control variant, treatment variant, experiment unit, deterministic assignment, eligibility, exposure event, intention-to-treat, primary metric, guardrail metric, minimum detectable effect, statistical power, sample ratio mismatch, A-A test a experiment namespace.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Canary deployment](canary-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Shadow deployment →](shadow-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
