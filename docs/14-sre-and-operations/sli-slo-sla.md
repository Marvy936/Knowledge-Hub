# SLI, SLO a SLA

SLI, SLO a SLA tvoria tri rozdielne contracts. **SLI** je presne definované meranie poskytovanej service level. **SLO** je cieľ alebo povolený rozsah nad týmto meraním počas konkrétneho okna. **SLA** je dohoda s používateľom alebo zákazníkom, ktorá môže obsahovať záväzok, exclusions, reporting a následky pri nesplnení.

```text
user journey a požadovaný outcome
→ exact measurement subject
→ valid event population
→ good/bad classification a observation point
→ SLI calculation
→ target a compliance window
→ SLO verdict
→ operational action a error budget
→ external commitment a remedy, ak existuje
```

Najčastejšia chyba je začať od metric, ktorú už systém ľahko exportuje. Správny návrh začína od toho, čo používateľ potrebuje, a až potom hľadá najbližší dostatočne autoritatívny signal.

## 1. Service-level subject

Pred výpočtom treba pomenovať:

- service alebo business capability;
- user alebo workload cohort;
- operation a request type;
- exact valid-event population;
- expected outcome;
- threshold alebo deadline;
- observation point;
- source a schema generation;
- compliance window;
- exclusions a missing-data semantics;
- ownera a response policy.

Príklad:

```text
capability: settlement completion
population: valid production settlements acknowledged HTTP 202
cohort: all merchants, separately tracked for top-tier merchants
success: provider-confirmed exactly-once completion do 10 minút
observation: reconciled payment + provider ledger
window: rolling 28 days
objective: 99.9 %
```

SLO bez population, success criteria a window-u nie je reprodukovateľný decision contract.

## 2. Service Level Indicator — SLI

SLI je kvantitatívne meranie jedného aspektu poskytovanej služby. Bežný event-based tvar je:

```text
SLI = good eligible events / total eligible events
```

SLI však môže merať aj distribution alebo stav:

- podiel successful requests;
- podiel requests pod latency thresholdom;
- podiel records spracovaných do deadline-u;
- podiel správnych answers;
- podiel acknowledged writes, ktoré zostali reconstructable;
- freshness data projection;
- podiel času, keď bola capability usable.

SLI definition musí určiť nielen numerator, ale aj denominator. Chybný denominator dokáže vytvoriť zelený výsledok bez ohľadu na kvalitu numeratoru.

## 3. Valid events a denominator

Nie každý observed event patrí do SLI population. Treba explicitne rozhodnúť o:

- syntactically invalid client requests;
- unauthorized requests;
- rate-limited traffic;
- client cancellations;
- health checks a synthetic traffic;
- retries a hedged requests;
- duplicate idempotency attempts;
- requests počas planned maintenance;
- requests, ktoré zlyhali pred observation pointom;
- asynchronous operations bez final outcome-u.

Príklad request SLI:

```text
eligible = valid merchant POST /settlements attempts
exclude = malformed request a invalid authentication
bad = 5xx, timeout, connection failure alebo incorrect 2xx
```

Ak sa retries rátajú ako samostatné opportunities, jedna user operation môže spotrebovať budget viackrát. Niekedy je to správne, pretože retry load je reálny service impact. Inokedy treba merať unique business operation podľa idempotency keyu. Obe metriky odpovedajú na inú otázku.

## 4. Good event nie je iba status code

Good event má vyjadrovať user-relevant outcome. Pre synchronous read môže byť:

```text
correct response
+ authorized data scope
+ latency ≤ 300 ms
```

Pre asynchronous settlement:

```text
acknowledged intent
+ final provider confirmation
+ exactly-once business result
+ completion ≤ 10 minút
```

HTTP `202` meria iba acceptance boundary. Ak final outcome zlyhá, acceptance SLI môže byť dobré a completion SLI zlé. Preto jedna journey často potrebuje viac SLIs:

- front-door acceptance;
- end-to-end completion;
- correctness;
- durability alebo reconstructability;
- freshness.

Tieto SLIs sa nemajú neuvážene spriemerovať do jedného score. Critical objective môže zlyhať aj pri dobrom aggregate score.

## 5. Observation point

Signal má byť čo najbližšie k user experience alebo authoritative business outcome-u.

### Server-side observation

Výhody:

- vysoká coverage;
- jednotná schema;
- jednoduchšia korelácia s release a dependency state-om.

Hranice:

- nevidí DNS, client network alebo edge failure pred serverom;
- môže merať response write, nie client receive;
- nemusí poznať downstream business completion.

### Client-side alebo edge observation

Výhody:

- bližšie k reálnemu user journey;
- zahŕňa viac network a rendering boundary.

Hranice:

- sampling a privacy;
- ad blockers alebo telemetry loss;
- heterogénne clients;
- zložitejšia identity a deduplication.

### Business-ledger observation

Výhody:

- autoritatívny final outcome;
- vhodné pre settlement, order, export alebo workflow completion.

Hranice:

- väčšia latency;
- potreba reconciliation;
- missing outcome môže znamenať failure služby alebo failure evidence pipeline-u.

Silný SLI contract dokumentuje, čo observation point vidí aj čo nevidí.

## 6. Measurement pipeline je súčasť SLI

```text
business event
→ instrumentation alebo ledger record
→ collection
→ transport a buffering
→ ingestion
→ deduplication a classification
→ query
→ SLI result
```

Chyba v ktorejkoľvek vrstve môže zmeniť SLO verdict. Preto treba evidovať:

- source generation;
- schema a semantic version;
- collection coverage;
- delay a lateness;
- duplicate handling;
- missing-data semantics;
- correction a backfill behavior;
- query revision;
- retention.

`No bad events` nie je to isté ako `complete evidence shows no bad events`.

## 7. Service Level Objective — SLO

SLO je target value alebo range nad konkrétnym SLI počas definovaného compliance window-u.

Príklady:

```text
99.95 % validných settlement-acceptance attempts bude úspešných
počas rolling 28-day window.

99.9 % acknowledged settlements bude provider-confirmed exactly once
najneskôr do 10 minút počas rolling 28-day window.

99 % status reads sa dokončí do 300 ms
pre top-tier merchant cohort počas rolling 7-day window.
```

SLO musí uviesť:

- SLI definition alebo stabilný odkaz na ňu;
- target;
- window;
- cohort a scope;
- ownera;
- error-budget policy;
- review trigger;
- known limitations.

## 8. Rolling a calendar windows

### Rolling window

Napríklad posledných 28 dní sa prepočítava pri každom evaluation time. Poskytuje priebežný obraz a nemá ostrý reset na začiatku mesiaca.

### Calendar window

Napríklad júl 2026 alebo Q3 2026. Je jednoduchšia pre reporting a contract settlement, ale reset môže vytvoriť neželané incentives. Incident na konci mesiaca môže byť pri novom mesiaci okamžite „odpustený“, hoci risk pretrváva.

Výber okna ovplyvňuje:

- citlivosť na krátke incidenty;
- seasonality;
- traffic volume;
- alerting a burn-rate model;
- release decisions;
- SLA reporting.

## 9. Target nie je aktuálny priemer

SLO sa nemá automaticky nastaviť podľa dnešného výkonu. Target má vychádzať z:

- user potreby a alternatives;
- business impactu;
- dependency contracts;
- achievable architecture;
- costu a staffing;
- change velocity;
- risk tolerance;
- safety marginu medzi interným a externým commitmentom.

Príliš prísny SLO môže vytvárať heroics, zablokovať zmeny a viesť k metric manipulation. Príliš voľný SLO dovolí zlý user experience bez operational consequence.

## 10. Service Level Agreement — SLA

SLA je dohoda medzi providerom a consumerom. Môže byť právna, obchodná alebo interná a typicky obsahuje:

- definovaný service a scope;
- commitment metric a threshold;
- measurement source;
- reporting period;
- exclusions;
- claim process;
- service credits alebo inú remedy;
- liability a support boundaries.

SLA nie je synonymum SLO. Praktický model môže byť:

```text
internal SLO: 99.95 % monthly availability
external SLA commitment: 99.9 % monthly availability
```

Rozdiel vytvára safety margin. Nie je však povinné mať SLA pre každú internú službu. Interný SLO môže riadiť engineering decisions bez finančnej alebo právnej remedy.

SLA success tiež nemusí znamenať spokojného používateľa. Exclusions a credit thresholds môžu byť splnené, hoci kritický cohort utrpel významný impact.

## 11. Exclusions a maintenance

Exclusion má byť explicitná, obmedzená a auditovateľná. Bežné riziká:

- planned maintenance sa odpočíta aj vtedy, keď používateľ nemá alternatívu;
- provider dependency failure sa vylúči, hoci user kupuje end-to-end service;
- invalid requests sa klasifikujú príliš široko;
- rate limiting skryje capacity failure;
- missing telemetry sa považuje za success;
- incidents sa spätne preklasifikujú po spotrebovaní budgetu.

SLO môže mať odlišné exclusions než SLA, ale rozdiel musí byť vedomý. Interný SLO má chrániť user experience, nie iba optimalizovať contractual report.

## 12. Connected failure `SRE-PAY-52`

Pôvodný Atlas dashboard používal jediný indicator:

```text
SLI-HTTP-01 = HTTP 2xx a 3xx / všetky ALB requests
SLO = 99.95 % za rolling 28 dní
```

Počas broker partition API naďalej commitovalo payment a outbox rows a vracalo `202`. Cleanup následne odstránil `4 182` nepublikovaných commands. `SLI-HTTP-01` zostalo zelené, pretože meralo acceptance response, nie settlement completion.

Nový SLO document zaviedol tri samostatné subjects.

### Acceptance SLI

```text
SLI-SET-ACCEPT-02
population: valid unique merchant settlement attempts
success: durable payment + outbox commit a correct acknowledgement
observation: edge request + PostgreSQL commit correlation
objective: 99.95 % / rolling 28 days
```

### Completion SLI

```text
SLI-SET-COMPLETE-03
population: acknowledged unique settlement intents
success: provider-confirmed exactly once do 10 minút
observation: reconciled payment, broker a provider ledger
objective: 99.9 % / rolling 28 days
```

### Durability SLI

```text
SLI-SET-DURABLE-01
population: acknowledged settlement intents retained 90 dní
success: intent je reconstructable z production alebo approved recovery lineage
observation: scheduled restore + reconciliation canary
objective: 99.9999 % / rolling annual window
```

Pri `5 000 000` eligible completion events umožňuje `99.9 %` SLO najviac `5 000` bad outcomes. Incident s `4 182` lost intents spotreboval `83.64 %` completion error budgetu, hoci request availability budget takmer neovplyvnil.

Tento rozdiel nie je metric detail. Mení release, incident a prioritization decision.

## 13. SLI correction a late data

Async business outcome môže doraziť po prvom evaluation-e. SLI pipeline preto potrebuje rules pre:

- provisional outcome;
- finalization delay;
- late provider acknowledgement;
- corrected classification;
- duplicate event;
- replay;
- query backfill;
- audit trail zmeneného verdictu.

Napríklad settlement bez outcome-u po 10 minútach je bad pre latency objective aj vtedy, keď sa dokončí po 30 minútach. Neskoršie dokončenie môže zmeniť completion-state metric, ale nemá spätne vymazať porušenie deadline SLO.

## 14. SLO acceptance verdict

SLO je operationally použiteľné, keď:

- začína od user journey a požadovaného outcome-u;
- exact population, good event a exclusions sú testovateľné;
- observation point je dostatočne blízko user alebo business outcome-u;
- measurement pipeline má coverage a missing-data verdict;
- retries a duplicates majú explicitnú identity semantics;
- target a window majú business aj technical rationale;
- SLA je od interného SLO oddelená;
- error-budget policy určuje consequences;
- critical cohorts sa nestratia v aggregate;
- synthetic incident spotrebuje očakávaný budget;
- silent-success, missing-telemetry a wrong-denominator fixtures zlyhajú;
- druhá measurement generation vytvorí reprodukovateľný verdict.

## 15. Troubleshooting flow

```text
sporný SLO verdict
→ exact SLI ID, revision, window a cohort
→ raw eligible event identity
→ good/bad classification rule
→ observation point
→ source/schema generation
→ collection a ingestion coverage
→ duplicate, retry a late-data handling
→ query revision
→ SLO target a exclusions
→ independent recomputation
→ operational consequence
```

## 16. Earlier controls

- versionovaný SLO document;
- stable SLI IDs a owners;
- client/business-ledger evidence pre critical journeys;
- valid-event fixtures;
- synthetic bad-event canary;
- completeness a lateness metrics;
- semantic query tests;
- separate critical cohorts;
- independent SLO recomputation;
- internal SLO safety margin pred SLA;
- scheduled review po architecture alebo user-behavior change;
- explicit provisional/final outcome semantics.

## 17. Anti-patterny

### Metric first

Tím vyberie ľahko dostupný CPU alebo HTTP signal a až potom mu vymyslí user význam.

### Average latency

Priemer skryje tail latency a kritické cohorts.

### `2xx` equals success

Transport acceptance sa zamieňa za business completion alebo correctness.

### Missing equals good

Výpadok telemetry zlepší SLI.

### SLA equals reliability strategy

Contractual minimum nahrádza interný user-centered objective.

### Jeden composite score

Výborná availability prekryje zlú durability alebo correctness.

### SLO bez consequence

Metric sa reportuje, ale neovplyvní release, staffing ani reliability work.

## 18. Kontrolné otázky

1. Čo je SLI, SLO a SLA?
2. Prečo denominator určuje význam SLI?
3. Kedy rátať request attempts a kedy unique business operations?
4. Prečo server-side SLI nemusí vidieť user failure?
5. Ako sa rolling a calendar window líšia?
6. Prečo target nemá byť iba current performance?
7. Čo tvorí SLA safety margin?
8. Ako planned maintenance mení user a contractual pohľad?
9. Prečo neskoré dokončenie nevymaže latency violation?
10. Ako missing telemetry ovplyvní verdict?
11. Prečo Atlas HTTP SLI nevidelo lost settlements?
12. Čo musí overiť SLO acceptance verdict?

## Glossary impact

Relevantné pojmy: service-level subject, Service Level Indicator, valid-event population, good event, observation point, measurement-generation identity, Service Level Objective, compliance window, rolling window, calendar window, Service Level Agreement, SLO safety margin, exclusion contract, provisional outcome, finalization delay a SLO acceptance verdict.

## Primárne zdroje

- [Google SRE — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/)
- [Google SRE Workbook — Example SLO Document](https://sre.google/workbook/slo-document/)
- [Google SRE — Availability Table](https://sre.google/sre-book/availability-table/)
