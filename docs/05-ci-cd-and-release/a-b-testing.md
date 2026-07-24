# A/B testing

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

A/B testing porovnáva dve alebo viac súbežných variantov správania na kontrolovane priradených skupinách subjektov. Cieľom je odhadnúť kauzálny dopad treatmentu na vopred definovaný používateľský alebo business výsledok.

```text
eligible population
→ assignment
→ exposure
→ outcomes
→ validity checks
→ effect estimation
→ product decision
→ rollout, iteration alebo removal
```

A/B test nie je deployment stratégia. Variant môže byť doručený feature flagom, samostatným backendom alebo client buildom, ale experimentálnu dôveryhodnosť vytvára dizajn priradenia, merania a rozhodovania.

## 2. A/B verzus canary

Canary odpovedá najmä:

> Je nová verzia prevádzkovo dostatočne bezpečná na širšiu expozíciu?

A/B experiment odpovedá:

> Aký je kauzálny rozdiel medzi variantmi pre definovanú populáciu a outcome?

Canary používa reliability guardrails a môže byť krátky. A/B test potrebuje randomizáciu alebo iný identifikačný dizajn, exposure logging, sample plán a ochranu pred biasom. Obe vrstvy možno kombinovať: najprv safety canary, potom produktový experiment.

## 3. Experiment contract

Pred spustením definuj:

- hypothesis,
- eligible population,
- unit of randomization,
- control a treatment,
- assignment ratio,
- primary metric,
- guardrail metrics,
- attribution a observation window,
- minimum detectable effect,
- sample/duration plán,
- stopping rules,
- planned segments,
- privacy a ethics review,
- ownera a decision policy.

Experiment bez vopred definovaného kontraktu umožňuje po výsledku vybrať najvýhodnejšie vysvetlenie.

## 4. Hypotéza

Silná hypotéza:

```text
Pre nových oprávnených používateľov
variant B zvýši 7-dňovú activation completion
aspoň o prakticky významnú hranicu
bez zhoršenia error, support a retention guardrails.
```

Obsahuje populáciu, treatment, outcome, horizon, očakávaný smer a safety constraints.

## 5. Experiment identity a versioning

Experiment musí mať immutable alebo versionovanú identitu:

- experiment key,
- experiment version,
- variants a payload revisions,
- assignment salt,
- eligibility revision,
- metric definitions,
- application/artifact versions,
- start/stop timestamps.

Ak sa treatment alebo eligibility významne zmení, ide o novú experiment version. Miešanie odlišných variantov do jedného výsledku znehodnocuje interpretáciu.

## 6. Unit of randomization

Unit musí zodpovedať tomu, kde treatment pôsobí:

- user,
- account alebo tenant,
- device,
- session,
- request,
- organization,
- geografický cluster,
- časový interval pri switchback dizajne.

Pri collaboration produkte môžu členovia jedného tímu ovplyvňovať výsledok navzájom; randomizácia userov potom porušuje independence a cluster randomization môže byť vhodnejšia.

## 7. Deterministic assignment

```text
bucket = hash(experiment_key + version + subject_id + salt) mod N
```

Požiadavky:

- rovnaký subjekt má stabilný variant,
- assignment je konzistentný naprieč services,
- zmena percenta má predvídateľný reshuffle model,
- anonymous identity má lifecycle,
- missing identity má explicitný fallback,
- experiment namespaces zabraňujú kolíziám.

## 8. Eligibility

Eligibility sa aplikuje pred assignmentom a môže zahŕňať:

- nový/existujúci používateľ,
- jurisdikciu,
- plan alebo tenant tier,
- client capability,
- locale,
- predchádzajúci experiment exposure,
- consent alebo opt-out,
- bezpečnostné obmedzenia.

Zmenu eligibility počas experimentu versionuj alebo analyzuj ako samostatnú fázu. Inak sa mení population mix.

## 9. Assignment verzus exposure

Assignment znamená, že subjekt patrí do variantu. Exposure znamená, že treatment skutočne ovplyvnil jeho skúsenosť.

Exposure event potrebuje:

- experiment ID/version,
- variant,
- privacy-safe subject key,
- timestamp,
- assignment reason,
- application/artifact version,
- session/request correlation,
- treatment payload revision.

Chýbajúci exposure logging môže zameniť „priradený“ a „reálne zasiahnutý“ population set.

## 10. Intention-to-treat a exposed analysis

- **Intention-to-treat —** analyzuje všetkých pridelených subjektov; zachováva randomizáciu a je robustnejší proti behaviorálnemu selection biasu.
- **Exposed-only —** analyzuje iba potvrdené exposures; môže zlepšiť citlivosť, ale exposure samotná môže závisieť od treatmentu.

Primárny analytický model definuj vopred. Exposed-only výsledok používaj opatrne a spolu s assignment diagnostics.

## 11. Metric contract

Každá metric má definovať:

- event source a schema,
- numerator a denominator,
- deduplication,
- attribution rule,
- time window,
- timezone,
- late-event handling,
- bot/internal traffic,
- missing values,
- unit of analysis.

Rozdielne dashboardy často ukazujú iný výsledok pre odlišné inclusion alebo attribution pravidlá.

## 12. Primary, secondary a guardrail metrics

- **Primary —** hlavný outcome pre decision.
- **Secondary —** vysvetľuje mechanizmus alebo širší dopad.
- **Guardrail —** chráni reliability, bezpečnosť, support, retention, accessibility alebo kvalitu revenue.
- **Diagnostic —** slúži na troubleshooting, nie na post hoc vyhlásenie víťaza.

Viac primárnych metrík zvyšuje decision ambiguity a multiple-testing riziko.

## 13. Sample size a praktický efekt

Pred experimentom odhadni:

- baseline rate/variance,
- minimum detectable effect,
- desired power,
- false-positive policy,
- expected eligibility a exposure rate,
- cluster effect, ak sa randomizuje skupina,
- maximum duration.

Štatisticky detegovateľný efekt môže byť ekonomicky alebo používateľsky zanedbateľný. Rozhodnutie potrebuje practical significance.

## 14. Precedence experimentálnych validity checks

Pred interpretáciou outcome over:

1. assignment integrity,
2. sample ratio,
3. exposure completeness,
4. metric pipeline health,
5. population comparability,
6. concurrent experiment interference,
7. novelty/seasonality,
8. guardrail safety.

Pozitívny primary result pri neplatnom assignment systéme nie je dôveryhodný.

## 15. Sample Ratio Mismatch

Ak očakávaš 50/50, ale pozoruješ významne odlišný pomer, hľadaj:

- assignment bug,
- variant-specific crash,
- logging loss,
- cache/routing rozdiel,
- eligibility aplikovanú po assignment-e,
- bot traffic,
- client incompatibility.

SRM je experiment integrity incident, nie iba kozmetická odchýlka.

## 16. A/A test a instrumentation validation

A/A test posiela ekvivalentné správanie do dvoch skupín a overuje:

- assignment ratio,
- exposure logging,
- metric parity,
- variance assumptions,
- analysis pipeline,
- false-positive calibration.

A/A test nenahrádza produktový experiment, ale môže odhaliť platformové chyby pred treatmentom.

## 17. Sequential monitoring a stopping

Priebežné pozeranie a zastavenie pri prvom priaznivom výsledku zvyšuje false-positive riziko.

Použi:

- fixed horizon,
- validný sequential design,
- Bayesian decision rule,
- oddelené immediate harm guardrails.

Safety abort môže byť okamžitý; product-win decision musí rešpektovať analytický plán.

## 18. Delayed outcomes a attribution

Outcome môže vzniknúť po hodinách alebo týždňoch. Definuj:

- exposure-to-outcome attribution,
- conversion window,
- censoring pri konci testu,
- late events,
- repeat exposure,
- cross-device identity.

Experiment neukončuj skôr, než relevantný outcome horizon dozreje.

## 19. Interference a network effects

Treatment jedného subjektu môže ovplyvniť control:

- marketplace supply/demand,
- social graph,
- collaboration,
- shared tenant quota,
- pricing alebo recommendations.

Možnosti:

- cluster randomization,
- geo experiment,
- switchback design,
- holdout na spoločnom markete,
- modelovanie spillover efektu.

## 20. Novelty, learning a carryover

Krátkodobý efekt môže pochádzať z novosti; používateľ sa tiež môže nový workflow postupne naučiť. Pri crossover alebo switchback dizajne môže treatment ovplyvniť následné obdobie.

Observation horizon má pokrývať celý relevantný business cycle a adaptation.

## 21. Multiple experiments

Experiment platforma potrebuje:

- namespaces,
- mutual-exclusion groups,
- dependencies,
- interaction metadata,
- exposure join keys,
- global holdout podľa potreby.

Úplné zakázanie overlapu znižuje kapacitu; ignorovanie interakcií znižuje validitu.

## 22. Operational safety

Aj produktový experiment je produkčný rollout. Potrebuje:

- kill switch,
- max exposure,
- guardrail alerts,
- ownera a on-call context,
- feature/config fallback,
- expiry,
- rollback alebo disable postup,
- audit zmien.

Experiment platforma je privilegovaný control plane.

## 23. Privacy, ethics a fairness

Over:

- oprávnenie experimentovať,
- consent alebo disclosure,
- citlivé segmenty,
- diskriminačný targeting,
- data minimization,
- retention exposure/outcome dát,
- opt-out,
- jurisdiction constraints,
- možnosť reálnej škody.

Nie každý behaviorálny zásah je vhodný na tichý randomizovaný experiment.

## 24. Experiment decision taxonomy

Výsledok nemusí byť iba „B vyhralo“:

- ship treatment,
- keep control,
- iterate and rerun,
- inconclusive,
- invalid experiment,
- stop for harm,
- segment-specific follow-up,
- no practical benefit.

Decision record má oddeliť evidence od business rozhodnutia.

## 25. Rollout po experimente

Víťazný variant nepromotionuj automaticky bez:

- guardrail review,
- capacity a reliability overenia,
- support/operability readiness,
- cleanup plánu,
- compatibility kontroly,
- monitoring-u po 100 %.

Experiment často bežal na čiastočnom scope a nemusí dokazovať behavior pri plnom load-e.

## 26. Cleanup a archive

Po rozhodnutí:

- nastav finálny behavior,
- odstráň obsolete variant,
- odstráň flag a assignment logiku,
- ukonči exposure events,
- archivuj hypothesis, queries a result,
- zachovaj privacy retention policy,
- vytvor následné actions.

Experiment bez cleanupu sa mení na permanentný nezdokumentovaný branch.

## 27. Failure modes

- assignment bug,
- missing exposure,
- SRM,
- metric drift,
- concurrent treatment interference,
- insufficient sample,
- peeking bias,
- delayed-outcome truncation,
- privacy breach,
- stale variant po expiry.

## 28. Diagnostický postup

1. Over experiment/version a treatment payload.
2. Skontroluj eligibility a assignment counts.
3. Testuj SRM.
4. Porovnaj assignment a exposure funnel.
5. Validuj metric query, dedup a attribution.
6. Skontroluj concurrent experiments a population mix.
7. Over sample maturity a delayed outcomes.
8. Rozlíš planned segment analysis od post hoc data mining.
9. Skontroluj guardrails a operational incidents.
10. Klasifikuj result ako valid, inconclusive alebo invalid.

## 29. Metriky experimentačnej platformy

- SRM incident rate,
- exposure logging completeness,
- invalid/inconclusive experiment rate,
- time to sufficient sample,
- stale experiment count,
- guardrail aborts,
- decision-to-cleanup time,
- metric-definition drift,
- podiel shipped treatments s post-rollout regression,
- privacy alebo targeting incidents.

## 30. Typické anti-patterny

### Traffic split bez assignment integrity

Nie je to dôveryhodný A/B experiment.

### Bez primary metric

Po výsledku sa vyberie najpriaznivejšie číslo.

### Assignment sa zamieňa s exposure

Nezobrazený treatment riedi alebo skresľuje odhad.

### Peeking bez validného dizajnu

False-positive riziko rastie.

### Pozitívny segment nájdený post hoc

Môže ísť o náhodu bez dostatočnej vzorky.

### Statistical significance = automatický ship

Ignoruje practical effect, costs, guardrails a ethics.

### Experiment bez expiry a cleanupu

Varianty zostanú trvalou komplexitou.

## 31. Rozhodovací rámec

1. Aká je kauzálna hypotéza?
2. Aká je správna randomization unit?
3. Kto je eligible a prečo?
4. Ako sa assignment odlišuje od exposure?
5. Aká metric a attribution definícia rozhoduje?
6. Aký minimum detectable effect je prakticky relevantný?
7. Aký sample/duration a stopping design použijeme?
8. Ktoré interference a concurrent experiments hrozia?
9. Aké guardrails chránia používateľov?
10. Aké privacy/ethics constraints platia?
11. Aké výsledné verdicts sú možné?
12. Ako sa variant rolloutne a následne odstráni experiment debt?

## 32. Kontrolný checklist

- hypothesis a primary metric sú vopred zapísané,
- experiment version identifikuje treatment,
- unit a eligibility sú správne,
- assignment je deterministický,
- exposure event je spoľahlivý,
- sample a stopping rules sú definované,
- SRM a instrumentation checks existujú,
- attribution pokrýva delayed outcomes,
- guardrails a kill switch sú aktívne,
- privacy a ethics boli posúdené,
- decision taxonomy zahŕňa invalid/inconclusive,
- rollout a cleanup plan existujú.

## 33. Kontrolné otázky

1. Aký je rozdiel medzi canary a A/B testom?
2. Prečo randomization unit musí zodpovedať mechanismu účinku?
3. Aký je rozdiel medzi assignment a exposure?
4. Kedy je intention-to-treat vhodnejší než exposed-only?
5. Čo je Sample Ratio Mismatch?
6. Načo slúži A/A test?
7. Prečo sequential peeking zvyšuje false positives?
8. Ako interference porušuje jednoduchý user-level experiment?
9. Prečo štatistický efekt nemusí byť prakticky významný?
10. Čo musí nasledovať po experimentálnom rozhodnutí?

## Summary

A/B testing je kauzálny experiment, nie obyčajný traffic split. Dôveryhodnosť vzniká explicitnou hypotézou, správnou randomization unit, stabilným assignmentom, exposure loggingom, versionovanými metric definitions, sample a stopping plánom a validity checks ako SRM. Rozhodnutie musí zohľadniť praktický efekt, guardrails, privacy a operational readiness. Po experimente treba variant bezpečne rolloutovať alebo odstrániť a uzavrieť flag aj analytický debt.

## Glossary impact

Relevantné pojmy: A/B testing, causal effect, experiment contract, randomization unit, eligibility, deterministic assignment, exposure event, intention-to-treat, primary metric, guardrail metric, minimum detectable effect, Sample Ratio Mismatch, A/A test, interference, sequential design a experiment cleanup.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Canary deployment](canary-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Shadow deployment →](shadow-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->