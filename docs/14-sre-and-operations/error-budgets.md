# Error budgets

Error budget prevádza SLO na explicitnú toleranciu failure-u. Nie je to povolenie ignorovať incidenty ani účtovná tabuľka downtime-u. Je to riadiaci mechanizmus, ktorý spája user impact, release risk, reliability investment a business priority.

Pre event-based SLO platí základný model:

```text
error budget fraction = 1 - SLO target
allowed bad events = eligible events × error budget fraction
remaining budget = allowed bad events - observed bad events
```

Pre `99.9 %` SLO je budget `0.1 %`. Ak je v okne `5 000 000` eligible events, budget povoľuje `5 000` bad events.

Samotný výpočet nestačí. Error budget funguje až vtedy, keď je naviazaný na ownera, policy, burn-rate signals, release decisions, incident response a overenie, že prijaté opatrenia skutočne znižujú user risk.

```text
versionovaný SLO a valid population
→ budget generation pre konkrétne okno
→ bad-event consumption
→ burn rate a forecast
→ policy threshold
→ release, incident alebo reliability decision
→ bounded action
→ SLI recovery a recurrence evidence
→ next-window governance
```

## 1. Exact error-budget subject

Budget musí patriť konkrétnemu:

- SLI ID a revision;
- SLO targetu;
- service a user journey;
- cohort a environmentu;
- compliance window-u;
- eligible-event population;
- good/bad classification;
- exclusions;
- measurement generation;
- policy revision;
- ownerovi.

`Máme 40 % budgetu` bez týchto údajov je neauditovateľné tvrdenie. Dve služby s rovnakým percentom môžu mať odlišný počet events, business impact a zostávajúci čas v okne.

## 2. Budget nie je iba downtime

Error budget môže byť vyjadrený cez:

- bad requests;
- slow requests nad thresholdom;
- nedokončené workflows;
- incorrect results;
- stale data;
- lost alebo unreconstructable acknowledged state;
- unavailable minutes.

Time-based downtime je vhodný iba vtedy, keď service opportunity približne korešponduje s časom. Pri premenlivom trafficu môže päť minút počas peak-u poškodiť viac používateľov než hodina počas nulového trafficu. Event-based budget preto často lepšie reprezentuje user impact.

## 3. Budget generation

Budget nie je nekonečný counter. Vzniká pre konkrétne okno a population:

```text
SLO target: 99.9 %
window: rolling 28 days
eligible events: 5 000 000
allowed bad: 5 000
observed bad: 4 182
remaining: 818
consumed: 83.64 %
```

Pri rolling window-e sa staré events postupne vyraďujú a nové vstupujú. Budget sa teda môže obnovovať aj bez calendar resetu. Pri calendar window-e sa resetne na hranici mesiaca alebo kvartálu, ale root cause a residual risk sa tým automaticky nestratia.

Budget generation musí byť reprodukovateľná z raw alebo retained aggregate evidence. Ak sa po incident-e zmení SLI query, treba zachovať pôvodný verdict aj corrected generation.

## 4. Burn rate

**Burn rate** vyjadruje, ako rýchlo sa budget spotrebúva vzhľadom na tempo, ktoré by ho rovnomerne minulo presne na konci okna.

```text
burn rate = observed bad-event rate / allowed bad-event rate
```

Interpretácia:

- `1×` — budget sa míňa presne plánovaným tempom;
- `<1×` — spotreba je pomalšia;
- `>1×` — pri pokračovaní sa budget minie pred koncom okna;
- veľmi vysoký burn rate — krátky, závažný incident;
- mierne zvýšený burn rate — chronic degradation alebo slow burn.

Samotný remaining percentage môže reagovať neskoro. Burn rate dokáže upozorniť na rýchle vyčerpanie ešte vtedy, keď veľká časť budgetu formálne zostáva.

## 5. Multi-window burn-rate signals

Jedno krátke okno je citlivé, ale hlučné. Jedno dlhé okno je stabilné, ale pomalé. Praktický model kombinuje viac okien:

```text
fast burn:
short window vysoký burn rate
+ longer confirmation window zvýšený burn rate
→ urgent page

slow burn:
longer windows mierne zvýšený burn rate
→ ticket alebo planned reliability action
```

Presné thresholds závisia od SLO window-u, trafficu a incident modelu. Dôležité je, aby alert odpovedal na otázku: **hrozí významné minutie budgetu v čase, keď ešte možno konať?**

Burn-rate alert nemá byť odvodený od CPU alebo queue depth bez preukázanej väzby na SLI. Resource signal môže byť diagnostická príčina, nie user-impact budget consumption.

## 6. Error-budget policy

Policy určuje, čo sa stane pri určitom stave budgetu. Musí byť schválená stakeholders, ktorí rozhodujú o product velocity aj reliability.

Obsahuje napríklad:

- ownerov SLO a budgetu;
- evaluation cadence;
- thresholds a actions;
- pravidlá pre releases a experiments;
- security a emergency exceptions;
- incident/postmortem triggers;
- prioritization reliability worku;
- escalation pri spore;
- návrat do normal mode-u;
- review a retirement policy.

Príklad:

| Stav | Decision |
|---|---|
| Budget healthy a burn rate pod limitom | bežné releases a experiments |
| Predikcia vyčerpania pred koncom okna | obmedziť high-risk changes, analyzovať top consumers |
| Viac než 50 % budgetu spotreboval jeden incident | povinný postmortem a P0/P1 recurrence item podľa impactu |
| Budget exhausted | zastaviť discretionary risky changes, prioritizovať reliability |
| Security fix alebo oprava príčiny incidentu | povolená cez explicitný emergency path |
| SLI recovery bez odstránenia root cause | normal mode sa automaticky neobnoví |

`Freeze all changes` nie je univerzálny cieľ. Niektoré zmeny znižujú risk. Policy má blokovať najmä discretionary risk a zároveň umožniť bezpečné remediation.

## 7. Error budget ako spoločný incentive

Bez error budgetu vzniká štrukturálny konflikt:

```text
product: rýchlejšie releases
operations: menej zmien a incidentov
```

SLO a budget vytvoria spoločný cieľ:

```text
maximalizovať hodnotné zmeny
pri zachovaní dohodnutej user reliability
```

Ak je budget zdravý, tím môže vedome prijímať bounded release risk. Ak sa míňa príliš rýchlo, reliability work dostane objektívnu prioritu. Rozhodnutie už nestojí iba na hlasnejšom stakeholderovi.

## 8. Čo budget nemá riadiť automaticky

Budget je silný input, nie jediný decision factor. Samostatne nevyrieši:

- bezpečnostný incident bez okamžitého SLI impactu;
- data corruption s malým počtom, ale vysokým impactom;
- compliance breach;
- safety-critical failure;
- systemic near miss;
- dependency risk, ktorý zatiaľ nevyprodukoval bad events;
- extrémne nerovnomerný impact medzi cohorts.

Jeden lost high-value settlement môže vyžadovať incident aj vtedy, keď aggregate budget je zdravý. Policy preto môže mať hard guardrails mimo budget arithmetic.

## 9. Multiple SLOs a budgets

Service môže mať osobitné budgets pre:

- availability;
- latency;
- correctness;
- completion deadline;
- durability;
- critical cohorts.

Tieto budgets sa nemajú spriemerovať. Ak correctness budget zlyhá, dobrá latency ho nekompenzuje. Policy môže používať:

```text
all critical objectives must remain within policy
```

alebo explicitnú risk matrix. Composite score bez semantics umožňuje jednu silnú vlastnosť použiť na zakrytie inej zlyhanej vlastnosti.

## 10. Shared dependencies a attribution

Jeden dependency incident môže spotrebovať budgets viacerých services. Attribution má odpovedať na dve odlišné otázky:

1. Ktorí users a services utrpeli impact?
2. Ktorý technical owner má odstrániť príčinu?

Consumer SLO nemá ignorovať failure iba preto, že ho spôsobil provider. User používa end-to-end capability. Interné chargeback alebo ownership modely môžu následne rozlíšiť provider a consumer action items.

Pri retries môže rovnaký dependency failure spotrebovať budget vo viacerých vrstvách. To nie je automaticky double counting chyba; každá vrstva môže merať vlastnú user alebo service opportunity. Pri portfolio rozhodnutí však treba rozumieť causal overlapu.

## 11. Budget a launch decisions

Pred launchom alebo rolloutom sa hodnotí:

- remaining budget;
- current fast a slow burn;
- recent incident concentration;
- confidence v SLI evidence;
- expected change risk;
- rollback a containment;
- cohort blast radius;
- dependency health;
- active reliability work.

Príklad decision contractu:

```text
remaining completion budget ≥ 50 %
+ 6h a 24h burn rate < 1×
+ žiadny unresolved P0 recurrence risk
+ canary rollback tested
→ release eligible
```

Eligibility neznamená automatický launch. Je to jeden gate v širšom release decisione.

## 12. Budget forecast

Forecast odhaduje, či sa budget minie do konca okna. Nemá používať iba jednoduchú lineárnu extrapoláciu bez kontextu. Zohľadniť možno:

- traffic forecast;
- seasonality;
- planned launches;
- known dependency maintenance;
- current backlog;
- recovery trend;
- cohort expansion;
- measurement delay.

Forecast má uvádzať confidence a assumptions. Presné číslo bez uncertainty môže vytvoriť falošnú autoritu.

## 13. Connected failure `SRE-PAY-52`

Completion objective:

```text
SLI: provider-confirmed exactly-once settlement do 10 minút
SLO: 99.9 %
window: rolling 28 days
eligible events: 5 000 000
budget: 5 000 bad settlements
```

Broker partition a unsafe cleanup spôsobili `4 182` lost intents:

```text
consumed = 4 182 / 5 000 = 83.64 %
remaining = 818 events
```

Pred incidentom tím sledoval iba `SLI-HTTP-01`, takže release dashboard ukazoval healthy budget. Nový completion budget odhalil, že jedna udalosť spotrebovala väčšinu tolerovaného failure-u.

### Policy outcome

1. okamžite zastaviť cleanup a discretionary production releases;
2. povoliť iba recovery, security a risk-reduction changes;
3. vykonať postmortem, pretože incident spotreboval viac než polovicu budgetu;
4. vytvoriť P0 item pre safe outbox retention a reconciliation;
5. zaviesť multi-window completion burn-rate alerting;
6. obnoviť normálny release mode až po recovery a regression evidence.

### Prečo calendar reset nestačí

Ak by sa budget resetol 1. augusta, unsafe cleanup by zostal schopný incident zopakovať. Policy preto vyžaduje dve podmienky:

```text
budget state je znovu prijateľný
+ root-cause a recurrence gates sú uzavreté
```

## 14. Competing interpretations

Pri rýchlej spotrebe budgetu treba odlíšiť:

- reálny user incident;
- zmenu denominatoru;
- duplicate events;
- telemetry backfill;
- nesprávnu good/bad klasifikáciu;
- cohort migration;
- query revision drift;
- legitimate traffic shift;
- missing data spätne klasifikované ako bad.

Discriminating evidence:

```text
SLI/policy revision
→ raw event IDs a population
→ incident timeline
→ source a ingestion completeness
→ independent recomputation
→ cohort a release breakdown
→ business ledger reconciliation
```

Containment nemá spočívať v rýchlej zmene query tak, aby budget vyzeral lepšie. Pôvodná generation musí zostať auditovateľná.

## 15. Error-budget acceptance verdict

Budget control je prijatý, keď:

- patrí versionovanému SLI, SLO a window-u;
- allowed a observed bad events možno reprodukovať;
- rolling/calendar semantics sú explicitné;
- burn rate rozlišuje fast a slow failure;
- missing a late data majú definovaný verdict;
- policy má schválených owners a consequences;
- release gate rozlišuje discretionary risk a remediation;
- critical correctness/security guardrails nemožno prehlasovať aggregate budgetom;
- reset neobchádza unresolved recurrence risk;
- synthetic incident aktivuje očakávaný alert a policy action;
- changed query, stale data a duplicate-event fixtures zlyhajú;
- second-window decision je reprodukovateľný.

## 16. Troubleshooting flow

```text
unexpected budget state
→ exact SLI/SLO/policy revision
→ window boundaries a current time
→ eligible-event denominator
→ bad-event classification
→ raw incident/cohort contribution
→ ingestion, lateness a correction
→ burn-rate calculation
→ forecast assumptions
→ triggered policy action
→ independent decision replay
```

## 17. Earlier controls

- versionovaný error-budget policy document;
- budget owner a escalation path;
- multi-window burn-rate alerts;
- top-consumer attribution;
- SLI completeness guard;
- immutable query/revision record;
- critical-cohort budgets;
- release eligibility API alebo dashboard;
- expiring policy exceptions;
- postmortem trigger podľa budget impactu;
- reset + recurrence dual gate;
- quarterly policy game day.

## 18. Anti-patterny

### Budget ako outage allowance

Tím úmyselne spotrebúva budget bez bounded hypothesis alebo user value.

### Freeze všetkého

Risk-reducing a security changes sú blokované spolu s discretionary launches.

### Calendar amnesty

Nové okno vymaže governance consequence bez odstránenia príčiny.

### Aggregate budget kompenzuje correctness

Rýchla služba môže vracať nesprávne alebo stratené výsledky.

### Budget bez policy

Percento sa zobrazuje, ale nič nemení.

### Query tuning po incidente

Measurement sa spätne upraví s cieľom znížiť consumption namiesto opravy klasifikácie transparentnou new generation.

### Remaining budget bez burn rate

Tím reaguje až vtedy, keď už je neskoro.

## 19. Kontrolné otázky

1. Ako sa error budget odvodí zo SLO?
2. Prečo event-based budget môže byť lepší než downtime?
3. Čo je budget generation?
4. Ako sa interpretuje burn rate `1×`?
5. Prečo kombinovať krátke a dlhé windows?
6. Čo má obsahovať error-budget policy?
7. Prečo budget nie je jediný security alebo safety gate?
8. Ako riešiť viac critical SLOs?
9. Prečo consumer budget zahŕňa provider failure?
10. Ako budget vstupuje do launch decisionu?
11. Prečo calendar reset neuzatvára `SRE-PAY-52`?
12. Čo musí overiť error-budget acceptance verdict?

## Glossary impact

Relevantné pojmy: error-budget subject, error-budget generation, allowed bad events, remaining budget, consumed budget, burn rate, fast burn, slow burn, multi-window burn-rate alert, error-budget policy, reliability mode, discretionary change, recurrence gate, budget forecast a error-budget acceptance verdict.

## Primárne zdroje

- [Google SRE — Embracing Risk](https://sre.google/sre-book/embracing-risk/)
- [Google SRE — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google SRE Workbook — Example Error Budget Policy](https://sre.google/workbook/error-budget-policy/)
- [Google SRE — Production Services Best Practices](https://sre.google/sre-book/service-best-practices/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SLI, SLO a SLA](sli-slo-sla.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Toil →](toil.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
