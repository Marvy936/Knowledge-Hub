# Performance, load a stress tests

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

Performance test je kontrolovaný experiment nad konkrétnym workloadom, artifactom a prostredím. Jeho výsledkom nie je iba číslo requests za sekundu, ale dôkaz o tom:

```text
aký demand prišiel
→ kde vzniklo čakanie alebo saturation
→ aký používateľský výsledok systém poskytol
→ ako sa správal pri prekročení limitu
→ či sa po záťaži obnovil
→ aké capacity alebo release rozhodnutie z toho vyplýva
```

## 1. Cieľ kapitoly

Nosný model kapitoly je:

```text
business demand a SLO
→ experiment hypothesis
→ immutable artifact a známe prostredie
→ reprezentatívny workload
→ warm-up a steady state
→ latency, throughput, queue a resource evidence
→ saturation/failure transition
→ ramp-down a recovery
→ capacity alebo release decision
```

Load, stress, spike, soak, capacity a scalability test sú varianty toho istého experimentálneho lifecycle-u. Nesmú sa zmeniť na samostatný katalóg bez konkrétnej hypotézy.

## 2. Nosný scenár: Atlas Orders 3.9.0

Atlas očakáva promo špičku. Release `orders-api` 3.9.0 má zvládnuť:

```text
1 500 arrivals/s počas 30 minút
operation mix:
- 60 % read order
- 20 % search/order list
- 12 % create order
- 5 % update order
- 3 % cancel order
```

Hypotéza:

```text
Pri 1 500 arrivals/s počas 30 minút:
- completed throughput ≥ 1 480/s,
- p95 successful latency < 250 ms,
- p99 successful latency < 600 ms,
- failed + rejected rate < 0,1 %,
- backlog zostane bounded,
- nevznikne OOM ani neplánovaný restart,
- po ramp-down sa backlog vyprázdni do 2 minút.
```

Test má rozhodnúť, či je release bezpečný pre plánovaný rollout a akú kapacitnú rezervu má tím deklarovať.

## 3. Performance experiment contract

Každý run definuje:

- **hypotézu a rozhodnutie**;
- **artifact digest a source revision**;
- **environment a konfiguráciu**;
- **dataset fingerprint**;
- **workload model a operation mix**;
- **open alebo closed semantics**;
- **load phases a trvanie**;
- **client, server a dependency signály**;
- **success a abort criteria**;
- **recovery expectation**;
- **limity interpretácie**;
- **ownera a bezpečnostné guardrails**.

Bez tohto kontraktu nie je možné run reprodukovať ani porovnať.

## 4. Demand, service time, capacity a queueing

Výkon vzniká interakciou:

```text
demand
→ arrival rate, concurrency, operation mix, payloady

service time
→ čas reálnej práce bez čakania

capacity
→ CPU, memory, workers, connections, partitions, quotas

queueing
→ práca čakajúca na dostupnú kapacitu

control loops
→ autoscaling, admission, rate limit, retries, circuit breakers
```

Latency môže rásť pre drahšiu prácu, queueing, lock contention, connection-pool wait, downstream quota alebo nevhodný control loop. Jedna CPU metrika preto nestačí.

## 5. Arrival rate, concurrency a completed throughput

Tieto hodnoty nie sú zameniteľné:

- **arrival rate** — koľko novej práce prichádza;
- **concurrency** — koľko operácií je rozpracovaných;
- **completed throughput** — koľko operácií sa skutočne dokončí;
- **backlog** — koľko práce zostáva čakať;
- **rejection/error rate** — koľko práce systém odmietne alebo nezvládne.

Pri overload-e môže arrival rate rásť, completed throughput stagnovať a backlog prudko narastať. Stabilný throughput pri rastúcom backlogu nie je stabilný systém.

## 6. Open a closed workload

Open model plánuje arrivals nezávisle od response time:

```text
scheduled arrival
→ request príde aj keď je systém pomalý
→ queue, rejection alebo timeout sú viditeľné
```

Je vhodný pre verejné API alebo externý traffic, ktorý neprestane prichádzať iba preto, že služba spomalila.

Closed model používa fixný počet users/workers:

```text
user odošle request
→ čaká na response
→ think time
→ odošle ďalší request
```

Je vhodný pre uzavretý worker pool alebo session model. Pri spomalení však automaticky zníži request rate a môže skryť overload verejného API.

Atlas public API preto používa open arrival model. Samostatný batch-worker experiment môže používať closed model.

## 7. Coordinated omission

Coordinated omission vzniká, keď generator počas spomalenia nevytvára prácu, ktorá mala podľa reálneho schedule prísť.

```text
systém spomalí
→ generator čaká
→ neodoslané arrivals sa nemerajú
→ report podhodnotí používateľskú latency
```

Ochrany:

- arrival-rate generator;
- intended-start timestamps;
- meranie scheduled verzus actual send rate;
- corrected histogram podľa tool semantics;
- dostatočná generator capacity.

Closed model nie je automaticky chybný. Chybná je jeho interpretácia ako open trafficu.

## 8. Operation mix a dáta

Globálny p95 môže skryť kritický write path. Atlas reportuje per-operation:

- arrivals a completions;
- success, reject, timeout a business-error classes;
- latency histograms;
- DB/broker/dependency path;
- payload-size a tenant distribution.

Dataset musí reprezentovať:

- tabuľkovú veľkosť a index selectivity;
- hot/cold order distribúciu;
- tenant skew;
- retention históriu;
- cache state;
- partition a broker backlog behavior.

Prázdna databáza a warm cache neposkytujú dôkaz pre produkčný dataset.

## 9. Load phases

Atlas experiment používa:

```text
precondition a data preparation
→ warm-up
→ ramp-up
→ steady state
→ peak/stress phase
→ ramp-down
→ recovery observation
```

### Warm-up

Stabilizuje JIT, caches, pools, DNS, lazy initialization a autoscaling. Končí podmienkou, nie náhodným časom.

### Ramp-up

Ukazuje, ako rast demandu aktivuje queues, limits a control loops. Reportuje sa ako časový priebeh.

### Steady state

Demand, throughput a queues sú dostatočne stabilné na vyhodnotenie SLO. Rastúci backlog diskvalifikuje steady state.

### Recovery

Po ramp-down sa overí vyprázdnenie backlogu, návrat latency, uvoľnenie resources, skončenie retries a absencia delayed duplicate side effects.

## 10. Latency a percentily

End-to-end latency môže obsahovať:

```text
client scheduling
+ DNS/TCP/TLS
+ proxy queue
+ application queue
+ service time
+ DB/broker/dependency wait
+ response transfer
```

Sleduj p50, p90, p95 a p99 per operation a result class. Rýchle errors sa nesmú miešať so successful latency tak, aby umelo zlepšili priemer.

Report obsahuje sample count, histogram resolution a spôsob agregácie. Percentily z viacerých generátorov sa neprieme­rujú; kombinujú sa kompatibilné histograms alebo raw samples.

## 11. Littleho zákon ako sanity check

V stabilnom systéme približne platí:

```text
priemerná concurrency ≈ completed throughput × priemerný čas v systéme
```

Ak Atlas dokončuje 1 000 operations/s s priemerným časom 0,2 s, očakávaná rozpracovanosť je približne 200 operations.

Vzťah pomáha odhaliť nepravdepodobný report alebo tlak na connections a memory. Počas nestabilného rastu backlogu sa nesmie interpretovať ako steady-state dôkaz.

## 12. Saturation a observation points

Utilization ukazuje používanie resource. Saturation ukazuje čakanie na resource alebo limit.

Atlas koreluje client latency s:

- CPU run queue a throttlingom;
- worker/event-loop queue;
- DB connection-pool waitom;
- lock waits a query latency;
- disk I/O queue;
- broker lag a oldest-message age;
- proxy pending requests;
- downstream quota/rejection;
- memory, GC a restartmi;
- autoscaling events.

Prvý rastúci wait/queue signal je často dôležitejší než prvý resource na 100 %.

## 13. Workload generator ako testovaný systém

Generator musí mať rezervu v:

- CPU a network bandwidth;
- file descriptors a ephemeral ports;
- timer resolution;
- connection capacity;
- clock synchronization;
- memory a sample buffering;
- distributed coordination.

Validuj:

```text
planned arrivals
→ scheduled arrivals
→ actual sends
→ completed samples
→ dropped alebo delayed iterations
```

Ak generator saturuje, throughput plateau nemusí patriť serveru.

## 14. Success, abort a safety

Success criteria kombinujú:

- user-facing latency a error limits;
- completed throughput;
- bounded queues;
- resource a dependency limits;
- absence data corruption a duplicate side effects;
- recovery deadline.

Abort criteria zahŕňajú:

- neočakávaný production target;
- error/latency nad bezpečnú hranicu;
- ohrozenie shared dependency;
- data-integrity signal;
- nekontrolovaný cost alebo generator runaway;
- výpadok observability;
- nemožnosť emergency stopu.

Load script zlyhá zatvorene, ak target identity nie je allowlisted.

## 15. Load, stress, spike, soak a capacity

Tieto varianty menia hypotézu a fázu experimentu:

- **load test** — overí plánovaný workload a SLO;
- **stress test** — sleduje transition za plánovanou hranicou;
- **spike test** — skúma prudký nárast a control-loop latency;
- **soak test** — skúma kumulatívny drift a lifecycle leaks;
- **capacity test** — hľadá maximálny udržateľný workload so safety margin;
- **scalability test** — porovná capacity a efficiency pri zmene resources.

Všetky potrebujú artifact, workload, evidence a recovery contract.

## 16. Stress transition a graceful degradation

Stress test nemá skončiť číslom „maximum RPS“. Sleduje:

```text
healthy
→ rising queue
→ SLO breach
→ controlled rejection
→ degraded mode
→ recovery alebo collapse
```

Preferovaný overload behavior:

- admission control;
- bounded queues;
- rate limiting;
- prioritization;
- load shedding;
- deadlines;
- circuit breakers;
- ochrana DB a brokerov;
- read-only alebo cached fallback podľa business contractu.

Globálne vyčerpanie threads, memory alebo DB connections je nekontrolované zlyhanie.

## 17. Autoscaling ako control loop

Atlas meria:

```text
workload signal
→ metrics collection/aggregation
→ autoscaler decision
→ capacity provisioning
→ process startup
→ readiness
→ endpoint registration
→ traffic redistribution
```

Každá fáza má latency. Sleduj overshoot, oscillation, cooldown, scale-down safety a existujúce connections. Autoscaling nevyrieši shared DB bottleneck ani quota.

## 18. Retry amplification

Pri overload-e môžu klient, proxy a služby retryovať rovnaký failure:

```text
pôvodný demand
× client retries
× proxy retries
× service retries
→ incidentný demand násobok
```

Testuj max attempts, retryable errors, backoff/jitter, retry budget, idempotency a deadline propagation. Recovery nesmie vytvoriť oneskorené duplicity.

## 19. Worked failure: closed model skryl overload

Pôvodný Atlas test používal 300 virtual users. Pri spomalení každý user čakal na response, takže generovaný request rate klesol:

```text
latency vzrástla
→ users čakali dlhšie
→ arrival rate klesla z 1 500 na 700/s
→ backlog nevznikol
→ report ukázal nízku error rate
```

Produkčný promo traffic však pokračoval na 1 500 arrivals/s. Queue narástla, requests timeoutovali a retries zvýšili demand.

### Root cause

Closed workload bol interpretovaný ako dôkaz pre open public traffic. Coordinated omission skrylo čakajúcich používateľov.

### Náprava

- public API test používa scheduled open arrivals;
- reportuje planned/actual send rate;
- latency sa viaže na intended start;
- generator capacity sa validuje;
- backlog a oldest-request age sú blocking metrics;
- closed test zostáva iba pre session-specific otázku.

## 20. Worked failure: viac replicas znížilo stabilitu

Atlas zdvojnásobil `orders-api` replicas z 20 na 40. Aplikačná CPU klesla, ale DB pool mal 20 connections na každú repliku:

```text
40 replicas × 20 connections
→ 800 možných DB connections
→ DB limit 500
→ pool/connect waits a rejections
→ retries
→ vyššia latency a nižší completed throughput
```

### Root cause

Scalability experiment meral iba aplikačnú CPU a počet replicas. Shared DB capacity a retry amplification neboli súčasťou modelu.

### Náprava

- connection budget sa počíta na celý deployment;
- autoscaling max replicas zohľadňuje DB limit;
- pool wait a active connections sú success criteria;
- retries sa obmedzia deadline a budgetom;
- ďalší experiment mení jednu kapacitnú premennú a sleduje nový bottleneck.

## 21. Baseline a porovnávanie

Reprodukovateľný baseline obsahuje:

- artifact a environment identity;
- workload a dataset fingerprint;
- generator/tool revision;
- warm-up a measurement windows;
- raw histograms a time series;
- resource, queue a dependency metrics;
- prirodzenú variabilitu z opakovaní.

Regresiu posudzuj kombináciou:

```text
absolútny SLO
+ relatívna zmena
+ známa variabilita
+ praktická prevádzková významnosť
+ bottleneck evidence
```

Jeden run nie je spoľahlivý baseline.

## 22. Failure artifacts a report

Uchovaj:

- load script a resolved parameters;
- artifact, environment a dataset provenance;
- scheduled/actual arrival data;
- raw latency histograms;
- throughput a error classes;
- generator metrics;
- server, DB, broker a infra time series;
- representative traces/profiles;
- autoscaling a deployment events;
- abort/operator actions;
- recovery timeline.

Report odpovie:

1. Aká bola hypotéza?
2. Čo sa testovalo?
3. Aký workload prišiel?
4. Kde vznikol prvý wait alebo saturation?
5. Kedy bol porušený SLO?
6. Ako systém degradoval?
7. Ako sa obnovil?
8. Aké capacity/release rozhodnutie je podporené?
9. Aké blind spots zostávajú?

## 23. Diagnostický postup

1. Over plánovaný verzus skutočný arrival rate.
2. Potvrď artifact, environment a dataset identity.
3. Oddeľ client scheduling, transport a server latency.
4. Nájdite prvý rastúci queue alebo wait metric.
5. Koreluj SLO breach s CPU, memory, I/O, DB, broker a dependencies.
6. Roztrieď timeout, rejection, business a generator errors.
7. Over, či plateau nepatrí generatoru.
8. Sleduj transition počas ramp-up, nie iba priemer.
9. Over recovery po ramp-down.
10. Reprodukuj hypotézu experimentom s jednou zmenou.

## 24. Referenčné pravidlá

- Performance test začína hypotézou a rozhodnutím.
- Arrival rate, concurrency a throughput nezamieňaj.
- Workload model odvoď z demand source.
- Open traffic netestuj náhodne closed modelom.
- Operation mix a dataset musia byť reprezentatívne.
- Percentily reportuj per operation a result class.
- Sleduj queues a waits, nie iba utilization.
- Generator má vlastnú capacity validation.
- Steady throughput s rastúcim backlogom nie je steady state.
- Stress test obsahuje failure transition a recovery.
- Autoscaling testuje celý control loop.
- Retry budget patrí do overload modelu.
- Baseline potrebuje viac než jeden run.
- Raw artifacts a environment provenance sa uchovávajú.

## 25. Časté omyly

### „Viac virtual users znamená viac loadu“

V closed modeli request rate závisí od response time.

### „Priemer je pod limitom“

Tail latency, rejections alebo kritická operation môžu porušovať SLO.

### „CPU nie je 100 %, máme rezervu“

Bottleneck môže byť pool, lock, disk, quota alebo partition.

### „Stress test je iba väčší load test“

Musí ukázať transition, ochrany a recovery.

### „Dvojnásobný cluster dá dvojnásobný throughput“

Shared bottleneck a coordination môžu scaling limitovať.

### „Generator report je celý dôkaz“

Bez server a dependency telemetry nevieš vysvetliť výsledok.

## 26. Zhrnutie

Dôveryhodný Atlas performance experiment je:

```text
SLO a demand
→ experiment contract
→ open workload + reprezentatívne dáta
→ immutable artifact
→ warm-up/ramp/steady/peak
→ latency + throughput + queues + resources
→ controlled failure transition
→ recovery
→ capacity/release decision
```

Názvy load, stress, spike alebo soak sú užitočné iba vtedy, keď menia explicitnú hypotézu a evidence plán.

## 27. Kontrolné otázky

1. Aký decision lifecycle má performance test?
2. Aký je rozdiel medzi arrival rate, concurrency a completed throughput?
3. Kedy použiť open a kedy closed workload?
4. Ako vzniká coordinated omission?
5. Prečo operation mix potrebuje per-operation percentily?
6. Ako rozlíšiš utilization od saturation?
7. Prečo rastúci backlog diskvalifikuje steady state?
8. Ako validuješ load generator?
9. Čo musí obsahovať success a abort contract?
10. Aký transition skúma stress test?
11. Ako sa meria celý autoscaling control loop?
12. Ako retry amplification mení overload?
13. Prečo viac Atlas replicas zhoršilo DB stabilitu?
14. Prečo je recovery povinnou časťou experimentu?

## Glossary impact

Relevantné pojmy: performance test, load test, stress test, spike test, soak test, capacity test, scalability test, experiment contract, open workload, closed workload, arrival rate, concurrency, completed throughput, coordinated omission, tail latency, queueing, saturation, steady state, load shedding, retry amplification, autoscaling control loop, recovery a performance baseline.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Smoke a regression tests](smoke-and-regression-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Security a infrastructure tests →](security-and-infrastructure-tests.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
