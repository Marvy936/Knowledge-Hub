# Error budgets

Error budget prevádza SLO na explicitnú toleranciu failure-u a následne na riadené engineering rozhodnutie. Nie je to povolenie ignorovať chyby, bankový účet downtime-u ani automatický trest za incident. Je to shared control loop medzi product velocity a reliability: keď služba poskytuje dohodnutú user experience, tím môže prijímať bounded change risk; keď failure spotrebúva budget príliš rýchlo, prioritu dostane containment a odstránenie recurrence mechanizmu.

Pre event-based SLO je základná aritmetika jednoduchá:

```text
budget fraction = 1 - SLO target
allowed bad events = eligible events × budget fraction
remaining budget = allowed bad events - observed bad events
```

Pri `99.9 %` objective a `5 000 000` eligible operations je povolených približne `5 000` bad operations. Výpočet sám však nič neriadi. Potrebuje exact SLO generation, trustworthy evidence, policy thresholds, decision authority a closure criteria.

## 1. Dominantný SLO-to-governance model

Budget vzniká z versionovaného SLO a konkrétneho compliance window-u. Bad events ho spotrebúvajú, burn-rate signal ukazuje tempo a policy prekladá stav na bounded action. Návrat do normal mode-u vyžaduje nielen lepšie percento, ale aj dôkaz, že root cause alebo exposure je pod kontrolou.

```text
versionovaný SLO a eligible population
→ budget generation pre exact window
→ bad-event consumption
→ remaining budget, burn rate a forecast
→ policy threshold
→ release/incident/reliability decision
→ containment alebo risk-reduction action
→ SLI recovery + recurrence evidence
→ controlled return to normal mode
```

Budget bez policy je iba report. Policy bez trustworthy SLI je automatizované rozhodovanie nad chybným inputom.

## 2. Exact error-budget subject

Tvrdenie „zostáva nám 40 %“ je neúplné. Exact subject obsahuje SLI a SLO revision, service journey, cohort, environment, eligible population, good/bad/missing semantics, compliance window, source/query generation, policy revision a ownera.

```text
budget: EB-SET-COMPLETE-03-2026-07
SLI: SLI-SET-COMPLETE-03 / q-set-complete-17
SLO: 99.9 %
window: rolling 28 dní
cohort: all production merchants
eligible events: 5 000 000
allowed bad: 5 000
policy: EBP-PAY-08
decision authority: Payments Product + SRE
```

Dve budgets s rovnakým remaining percentage môžu mať iný počet operations, business impact a čas do konca window-u. Zmena SLI query alebo exclusions vytvára novú generation a musí zachovať comparison s pôvodnou.

## 3. Consumption a burn rate

Remaining budget opisuje kumulovaný stav. Burn rate opisuje rýchlosť spotreby voči tempu, ktoré by budget minulo presne na konci okna.

```text
burn rate = observed bad-event rate / allowed bad-event rate
```

`1×` znamená spotrebu presne plánovaným tempom. Vysoký short-window burn signalizuje akútny incident; mierne zvýšený long-window burn odhaľuje chronic degradation. Remaining percentage samotné môže reagovať neskoro, pretože na začiatku okna vyzerá veľké aj počas rýchleho failure-u.

Multiwindow, multi-burn-rate model kombinuje citlivé krátke okno so stabilnejším potvrdením:

```text
fast burn:
vysoký burn v short window
+ zvýšený burn v confirmation window
→ page

slow burn:
mierne zvýšený burn vo viacerých dlhších windows
→ ticket a reliability action
```

Thresholds sa odvodzujú od SLO window-u, trafficu a požadovaného response time-u. CPU alebo queue depth nie sú budget consumption; môžu byť causes, kým burn rate musí vychádzať z user-impact SLI.

## 4. Error-budget policy

Policy určuje actions, nie iba farbu dashboardu. Spoločne ju vlastnia stakeholders, ktorí rozhodujú o product velocity, operational risk a customer impact.

Praktický state model:

```text
Healthy
→ Watch
→ AtRisk
→ Exhausted
→ RecoveryOnly
→ RecurrenceValidated
→ Normal
```

`Healthy` povoľuje bežné bounded releases. `Watch` vyžaduje analýzu top consumers a risk pri najbližších changes. `AtRisk` obmedzuje discretionary high-risk rollouty. `Exhausted` zastaví risk-increasing changes, ale musí povoliť security fixes, containment a reliability remediation. `RecoveryOnly` trvá, kým sa SLI stabilizuje. `RecurrenceValidated` vyžaduje regression alebo second-failure evidence pred návratom do normal mode-u.

Freeze všetkých zmien je zlý univerzálny mechanizmus. Niektoré zmeny budget zachránia. Policy preto klasifikuje change intent a vyžaduje risk-reduction path, nie úplnú nečinnosť.

## 5. Multiple objectives a hard invariants

Service môže mať oddelené budgets pre availability, latency, correctness, completion, durability a critical cohorts. Tieto budgets sa nesmú spriemerovať. Zelená latency nekompenzuje duplicate payment a zdravý aggregate cohort nekompenzuje data loss top-tier merchant-a.

Error budget tiež nie je jediný risk control. Jeden corrupt high-value settlement, security breach, compliance incident alebo systemic near miss môže vyžadovať incident a release block aj pri zdravom aggregate budgete. Hard invariants existujú mimo percentuálnej tolerancie.

```text
critical correctness/durability invariant violated
→ incident a containment
bez ohľadu na remaining aggregate budget
```

Budget reguluje prijateľnú frekvenciu bežných failures, nie povolenie porušovať nekompenzovateľný business alebo safety contract.

## 6. Shared dependencies a attribution

Dependency failure môže spotrebovať budgets viacerých consumer services. User-impact attribution a remediation ownership sú dve samostatné otázky. Consumer SLO má zachytiť end-to-end failure, pretože user používa capability, nie organizačný diagram. Technical action item však môže patriť broker alebo provider tímu.

Retries môžu vytvoriť correlated budget consumption na viacerých vrstvách. Pri portfolio rozhodnutí treba zachovať causal graph, aby jedna dependency udalosť nebola nesprávne interpretovaná ako desať nezávislých incidentov. Zároveň sa failure nesmie odstrániť z consumer SLO len preto, že root cause leží inde.

## 7. Launch eligibility a forecast

Pred rolloutom sa kombinuje remaining budget, fast/slow burn, recent incident concentration, evidence confidence, change risk, cohort blast radius, dependency health a rollback capability.

```text
remaining completion budget ≥ 50 %
+ 6h a 24h burn < 1×
+ žiadny unresolved P0 recurrence risk
+ canary rollback overený
→ change je budget-eligible
```

Eligibility nie je automatický deploy approval; je to jeden input do širšieho release decisionu. Forecast má zohľadniť traffic seasonality, planned launch, backlog, provider slowdown a measurement delay. Jedno presné projected date bez assumptions a uncertainty vytvára falošnú autoritu.

## 8. Connected failure `SRE-PAY-52`

Completion objective bolo:

```text
SLI: provider-confirmed exactly-once settlement do 10 minút
SLO: 99.9 %
window: rolling 28 dní
eligible operations: 5 000 000
allowed bad: 5 000
```

Broker partition a unsafe cleanup spôsobili `4 182` lost intents. Incident teda spotreboval `83.64 %` completion budgetu a zostalo iba `818` bad-event opportunities.

Pôvodný release dashboard sledoval front-door HTTP budget, ktorý zostal zdravý. Nový completion budget zmenil policy outcome:

```text
stop unsafe cleanup
→ zastaviť discretionary risky releases
→ povoliť recovery/security/risk-reduction changes
→ povinný postmortem
→ P0 safe-retention a reconciliation remediation
→ multiwindow completion burn alerts
→ normal mode až po recurrence testoch
```

Calendar reset by 1. augusta numericky obnovil budget, ale unsafe query by zostala schopná incident zopakovať. Policy preto vyžaduje dve oddelené podmienky:

```text
budget state je prijateľný
+ root-cause exposure a recurrence gates sú uzavreté
```

## 9. Competing interpretations a evidence integrity

Rýchly burn môže znamenať reálny service failure, chybnú denominator query, delayed provider events, duplicate retry classification, cohort mix change alebo monitoring outage. Decision preto potrebuje raw operation samples, expected population, query/schema generation, source lag a nezávislý business ledger.

Historical budget sa nesmie potichu prepočítať po query fix-e. Zachovaj decision-time generation, corrected generation a delta explanation. Ak chýba evidence coverage, policy môže prejsť do `UnknownEvidence` a obmedziť risk, namiesto predstierania zdravého budgetu.

## 10. Budget acceptance contract

Positive acceptance vytvorí known population s kontrolovaným počtom good a bad operations a overí presný allowed, consumed a remaining budget. Synthetic fast burn musí vyvolať intended page a slow burn intended ticket. Policy transition musí povoliť remediation a zablokovať iba risk-increasing change class.

Forbidden paths musia zlyhať. Query change nesmie spätne vymazať incident, missing telemetry nesmie obnoviť budget, calendar reset nesmie automaticky uzavrieť recurrence risk, healthy availability budget nesmie prekryť exhausted durability budget a broad „emergency“ label nesmie obísť decision authority.

```text
positive:
known bad events → exact consumption → intended policy action

recovery:
SLI stabilizácia + remediation + second-failure test → Normal

forbidden:
missing data as healthy
automatic reset closes root cause
aggregate budget hides critical cohort
all changes blocked including remediation
unapproved query revision
```

Verdict patrí exact SLO, query, window a policy generation.

## 11. Troubleshooting flow

Pri nečakanom budget stave najprv over exact subject a aritmetiku. Potom population, event classification, source lag a query revision. Až následne vyhodnoť service causes a policy action.

```text
budget alert alebo release block
→ SLO/query/window identity
→ expected vs observed population
→ good/bad/missing event samples
→ burn calculation
→ service vs evidence hypothesis
→ discriminating source
→ corrected budget verdict
→ policy action
→ recurrence closure
```

Ručný override bez preserved reason, expiry a approvera vytvára druhú neauditovateľnú policy.

## 12. Anti-patterny

Error-budget anti-patterny oddeľujú aritmetiku od user risku alebo policy consequence. Taký budget môže vyzerať presne, ale nevedie k bezpečnému change rozhodnutiu ani k uzavretiu recurrence mechanizmu.

- **Budget ako povolenie míňať chyby —** Budget umožňuje bounded risk, nie vedomé poškodzovanie users alebo ignorovanie known defectu. Known high-impact mechanismus potrebuje remediation aj pri formálne zdravom budgete.
- **Percento bez operation countu a času —** `40 % zostáva` nehovorí, či ide o štyri alebo štyri milióny events ani ako rýchlo sa budget míňa. Decision potrebuje remaining count, burn rate a zostávajúci window.
- **Automatický freeze všetkého —** Globálny freeze blokuje aj changes, ktoré risk znižujú. Policy musí rozlišovať discretionary, emergency, security a remediation work.
- **Calendar reset ako recovery —** Window reset mení číslo, nie production mechanismus. Normal mode sa obnoví až po SLI recovery a recurrence evidence.
- **Priemer budgets —** Availability, correctness, durability a critical cohorts majú nekompenzovateľné verdicts. Composite average nesmie zelenou osou prekryť exhausted critical objective.

## 13. Kontrolné otázky

1. Čo tvorí exact error-budget subject?
2. Ako sa vypočíta allowed a remaining budget?
3. Čo burn rate vyjadruje navyše oproti remaining percentage?
4. Prečo kombinovať short a long windows?
5. Čo musí obsahovať error-budget policy?
6. Prečo exhausted budget nemá blokovať remediation?
7. Kedy hard invariant prevažuje nad budgetom?
8. Ako shared dependency ovplyvní user attribution a owner action?
9. Prečo forecast potrebuje assumptions a confidence?
10. Prečo calendar reset neuzavrie `SRE-PAY-52`?
11. Ktoré evidence odlíši real burn od query defectu?
12. Čo musí forbidden acceptance test odmietnuť?

## Glossary impact

Relevantné pojmy: error-budget subject, budget generation, bad-event consumption, remaining budget, burn rate, multiwindow burn signal, error-budget policy, budget state machine, budget-eligible change, hard reliability invariant, `UnknownEvidence` a recurrence gate.

## Primárne zdroje

- [Google SRE — Embracing Risk](https://sre.google/sre-book/embracing-risk/)
- [Google SRE — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google SRE Workbook — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- [Google SRE Workbook — Example Error Budget Policy](https://sre.google/workbook/error-budget-policy/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SLI, SLO a SLA](sli-slo-sla.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Toil →](toil.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
