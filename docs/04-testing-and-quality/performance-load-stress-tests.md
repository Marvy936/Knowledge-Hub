# Performance, load a stress tests

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

Performance testing overuje časové, kapacitné a degradačné vlastnosti systému pod presne definovaným workloadom. Výsledok nie je iba jedno číslo requests za sekundu. Dôveryhodný test musí vysvetliť, aký traffic bol generovaný, na akom artefakte a prostredí, aké limity platili, čo sa saturovalo, ako systém zlyhal a či sa po záťaži obnovil.

```text
workload model
→ system response
→ resource a dependency evidence
→ SLO a capacity decision
```

Bez workload modelu, environment provenance a success criteria je výsledok nereprodukovateľný a často zavádzajúci.

## 1. Mentálny model výkonu

Výkon systému vzniká interakciou piatich oblastí:

- **demand —** arrival rate, concurrency, operation mix, payloady a session behavior,
- **service time —** čas potrebný na vykonanie práce bez čakania v queues,
- **capacity —** CPU, memory, connections, workers, partitions a dependency quotas,
- **queueing —** čakajúca práca pri nedostatku okamžitej kapacity,
- **control mechanisms —** autoscaling, rate limiting, load shedding, retries a circuit breakers.

Performance test má rozlíšiť, či latency rastie pre drahšiu prácu, queueing, resource saturation, lock contention, downstream dependency alebo nevhodný control loop.

## 2. Experiment contract

Každý performance test potrebuje explicitný experiment contract:

```text
hypotéza
→ testovaný artifact a konfigurácia
→ workload model
→ environment
→ merané signály
→ success a abort criteria
→ trvanie a fázy
→ očakávané recovery
→ limity interpretácie
```

Príklad hypotézy:

```text
Pri 1 500 completed requests/s počas 30 minút
služba udrží p95 pod 250 ms,
p99 pod 600 ms,
error rate pod 0,1 %,
bez restartu,
a backlog sa po skončení špičky vyprázdni do 2 minút.
```

## 3. Druhy performance testov

### Performance test

Širší pojem pre meranie latency, throughputu, resource usage a stability pri definovaných podmienkach.

### Load test

Overuje očakávaný alebo plánovaný workload. Cieľom je potvrdiť SLO a kapacitnú rezervu pri normálnej prevádzke.

### Stress test

Zvyšuje demand za plánovanú hranicu, aby odhalil saturation point, failure mode, ochranné mechanizmy a recovery.

### Spike test

Vytvára prudký nárast alebo pokles trafficu. Overuje cold starts, connection establishment, queueing, autoscaling latency a schopnosť absorbovať krátku špičku.

### Soak alebo endurance test

Udržiava workload dlhší čas. Hľadá memory a resource leaks, cache churn, fragmentation, rast queues, rotáciu credentials, log growth, compaction a kumulatívne failures.

### Capacity test

Hľadá maximálny udržateľný workload pri definovanom SLO, safety margin a stabilnom stave.

### Scalability test

Porovnáva, ako sa výkon mení pri pridávaní alebo odoberaní CPU, memory, replicas, shards alebo partitions. Overuje, či scaling prináša očakávanú hodnotu a kde vzniká shared bottleneck.

## 4. Workload model

Workload model musí reprezentovať produkčné charakteristiky relevantné pre testované riziko:

- operation mix,
- arrival rate a burstiness,
- concurrency,
- payload-size distribution,
- read/write ratio,
- think time a session length,
- authentication a authorization cost,
- cache hit/miss ratio,
- data volume a cardinality,
- hot keys alebo hot partitions,
- regionálna a network latency,
- retry a timeout správanie klientov.

Jeden malý cached request pri rovnomernom trafficu nedokazuje kapacitu systému s veľkými payloadmi, writes, cold cache a nerovnomernou popularitou dát.

## 5. Operation mix

Produkčný systém zvyčajne nevykonáva iba jednu operáciu. Workload môže napríklad obsahovať:

```text
60 % read product
20 % search
10 % create order
7 % update cart
3 % payment authorization
```

Každá operácia má iný service time, dependency path a resource profile. Test musí reportovať globálne aj per-operation percentily a error rate, pretože lacné reads môžu skryť pomalý kritický write path.

## 6. Arrival rate, concurrency a completed throughput

Tieto metriky nie sú zameniteľné:

- **arrival rate —** koľko novej práce prichádza za jednotku času,
- **concurrency —** koľko operácií je práve rozpracovaných,
- **completed throughput —** koľko operácií sa úspešne alebo neúspešne dokončí za jednotku času.

Pri overload-e môže arrival rate ďalej rásť, completed throughput stagnovať a concurrency alebo queue depth prudko narastať.

## 7. Open workload model

Open model plánuje príchody nezávisle od response time systému. Lepšie reprezentuje externý traffic, ktorý neprestane prichádzať iba preto, že služba je pomalá.

```text
čas 0 ms   request A
čas 10 ms  request B
čas 20 ms  request C
```

Ak systém nestíha, requests sa hromadia, odmietajú alebo timeoutujú. Open model preto odhaľuje queue buildup a overload realistickejšie.

## 8. Closed workload model

Closed model používa fixný počet virtual users. Každý user pošle ďalší request až po dokončení predchádzajúceho a prípadnom think time.

Pri spomalení systému automaticky klesá generovaný request rate. To môže byť správny model pre uzavretý počet workers alebo sessions, ale môže skryť overload pri verejnom API.

## 9. Výber workload modelu

Model vyber podľa reálnej demand source:

- verejný web alebo API traffic je často bližší open modelu,
- fixný worker pool alebo batch môže byť closed model,
- používateľská session môže kombinovať arrival process nových sessions a closed správanie krokov v session,
- message queue workload potrebuje modelovať producer arrival rate a consumer backlog.

Nástrojový default nesmie rozhodnúť za architektonickú realitu systému.

## 10. Littleho zákon

V stabilnom systéme platí orientačný vzťah:

```text
priemerná concurrency ≈ throughput × priemerný čas v systéme
```

Ak systém dokončuje 1 000 operácií za sekundu a priemerný čas je 0,2 sekundy, priemerná rozpracovanosť je približne 200 operácií.

Vzťah pomáha odhaliť nepravdepodobné reporty a odhadnúť tlak na connections, memory a worker capacity. Neplatí ako jednoduchá interpretácia počas prudko nestabilného rastu backlogu.

## 11. Latency decomposition

End-to-end latency môže obsahovať:

```text
client scheduling
+ DNS a connection setup
+ TLS
+ proxy queue
+ application queue
+ service time
+ database alebo dependency wait
+ response transfer
```

Celkový percentil bez rozkladu povie, že používateľ čaká, ale nie prečo. Preto koreluj client-side latency s tracingom a server-side timers.

## 12. Percentily a tail latency

Priemer môže vyzerať zdravo, aj keď kritická časť používateľov zažíva vysokú latency. Sleduj minimálne p50, p90, p95 a p99 per operation a per result class.

```text
p50 = 80 ms
p95 = 240 ms
p99 = 1,8 s
```

Oddelene reportuj successful, rejected, timeout a failed requests. Rýchle error responses môžu umelo zlepšiť globálny priemer.

## 13. Percentilová presnosť

Na odhad vysokých percentilov potrebuješ dostatok samples. P99 z malej vzorky je nestabilné číslo. Report má uviesť sample count, histogram resolution a agregáciu medzi generátormi.

Pri distribuovaných histogramoch sa percentily nemajú priemerovať. Potrebné je zlúčiť kompatibilné histograms alebo vyhodnotiť raw samples vhodným spôsobom.

## 14. Coordinated omission

Coordinated omission vzniká, keď generator počas spomalenia nevytvára prácu, ktorá by podľa reálneho arrival schedule mala prísť. Meranie potom ignoruje čas, počas ktorého klient čakal na možnosť request odoslať.

Ochrany:

- arrival-rate generator,
- intended start timestamps,
- corrected latency histogram,
- generator s dostatočnou rezervou,
- porovnanie scheduled a actual send rate.

Closed model nie je automaticky chybný; chybná je jeho interpretácia ako open trafficu.

## 15. Queueing a saturation

Utilization hovorí, ako veľmi sa resource používa. Saturation znamená, že práca čaká na resource alebo limit.

Sleduj napríklad:

- CPU run queue a throttling,
- worker alebo thread queue,
- event-loop lag,
- connection-pool wait time,
- database lock waits,
- disk queue depth,
- broker lag,
- pending load-balancer requests,
- downstream quota rejection.

Latency často rastie prudko ešte pred 100 % utilization, pretože queueing je nelineárne.

## 16. Universal Scalability Law a serial bottleneck

Horizontal scaling nemusí byť lineárne. Shared state, coordination a serial sections môžu spôsobiť klesajúci prínos ďalších replicas.

Scalability test má merať:

```text
capacity pri N replicas
→ capacity pri 2N replicas
→ zmena latency a efficiency
→ nový bottleneck
```

Ak dvojnásobok aplikačných replicas zvýši throughput iba o 10 %, shared database, lock, partition alebo quota pravdepodobne limituje systém.

## 17. Load profile

Performance run má explicitné fázy:

```text
precondition a data preparation
→ warm-up
→ ramp-up
→ steady state
→ peak alebo stress phase
→ ramp-down
→ recovery observation
```

Každá fáza má iný účel a jej samples sa nemajú bezhlavo miešať do jedného výsledku.

## 18. Warm-up

Warm-up stabilizuje JIT, caches, connection pools, DNS, lazy initialization a autoscaling. Je ukončený podmienkou, nie iba náhodným časom.

Príklady stabilizačných podmienok:

- throughput a latency sa ustálili v tolerancii,
- cache hit rate dosiahla reprezentatívnu hodnotu,
- požadovaný počet connections je otvorený,
- replicas sú ready,
- background migrations alebo compaction skončili.

Cold-start performance test môže byť samostatný experiment; nemá sa nevedomky miešať so steady-state kapacitou.

## 19. Ramp-up

Ramp-up má byť dostatočne pomalý na pozorovanie control loops, ale dostatočne reprezentatívny pre produkčné nárasty. Príliš rýchly ramp testuje iba spike a provisioning, príliš pomalý môže skryť reakciu na reálny náhly traffic.

Reportuj demand a system response v čase, nie iba finálny priemer.

## 20. Steady state

Steady state je interval, v ktorom demand, capacity a hlavné queues zostávajú dostatočne stabilné na vyhodnotenie SLO.

Stabilný completed throughput pri rastúcom backlogu nie je steady state. Systém iba odkladá nedokončenú prácu do budúcnosti.

## 21. Recovery observation

Po ramp-down sleduj:

- vyprázdnenie backlogu,
- návrat latency a error rate,
- scale-down,
- uvoľnenie connections a memory,
- ukončenie retries,
- obnovenie circuit breakerov,
- konzistenciu dát,
- neprítomnosť delayed duplicate side effects.

Systém, ktorý zvládne peak, ale po ňom zostane degradovaný, testom neprešiel.

## 22. Test environment provenance

Výsledok platí iba pre zdokumentovaný environment:

- artifact digest a configuration,
- instance alebo hardware type,
- CPU/memory requests a limits,
- replica count,
- autoscaling policy,
- database engine, size, indexes a statistics,
- cache a dataset state,
- network path a region,
- dependency versions a quotas,
- observability sampling a overhead,
- kernel, runtime a container settings.

Shared environment musí evidovať konkurujúci workload. Inak môže test merať cudziu záťaž alebo naopak neprodukčne prázdnu infraštruktúru.

## 23. Dataset representatívnosť

Výkon databázy a cache závisí od objemu a distribúcie dát. Testuj s realistickou:

- tabuľkovou veľkosťou,
- index selectivity,
- cardinality,
- hot/cold distribúciou,
- object size,
- retention history,
- partition count,
- skew a tenant mixom.

Prázdna databáza môže používať iný query plan a držať celý dataset v cache.

## 24. Load generator calibration

Load generator je tiež systém s limitmi. Pred testom over:

- CPU a network headroom,
- file descriptor a ephemeral-port limits,
- timer resolution,
- max connections,
- clock synchronization,
- dropped iterations alebo samples,
- client-side queueing,
- DNS a TLS overhead,
- distribuovanú koordináciu generator nodes.

Ak generator saturuje, môže vytvoriť falošný throughput plateau alebo nízku arrival rate.

## 25. Client-side a server-side errors

Rozlišuj:

- generator nestihol iteration naplánovať,
- connection nebola vytvorená,
- request timeoutol na klientovi,
- proxy request odmietla,
- aplikácia vrátila business error,
- dependency zlyhala,
- server odpoveď prišla po client deadline.

Jedna globálna `error rate` metrika bez kategórií sťažuje root-cause analýzu.

## 26. Success criteria

Success criteria majú kombinovať používateľský výsledok, systémové limity a recovery:

```text
Pri 1 500 arrivals/s počas 30 minút:
- completed throughput neklesne pod 1 480/s,
- p95 successful latency < 250 ms,
- p99 successful latency < 600 ms,
- failed + rejected rate < 0,1 %,
- žiadny OOM ani neplánovaný restart,
- DB connection-pool wait p95 < 20 ms,
- queue backlog je bounded,
- po ramp-down sa backlog vyprázdni do 2 minút.
```

Limity majú vychádzať zo SLO, capacity planu a downstream contracts.

## 27. Abort criteria

Test musí mať emergency stop pri:

- neočakávanom smerovaní na produkciu,
- error rate alebo latency nad bezpečnú hranicu,
- ohrození shared dependency,
- nekontrolovanom cost raste,
- data corruption signále,
- generator runaway,
- výpadku observability.

Abort nie je neúspešná disciplína; je to bezpečnostná hranica experimentu.

## 28. Baseline

Reprodukovateľný baseline obsahuje:

- artifact a source revision,
- environment a configuration,
- dataset fingerprint,
- workload definition,
- tool a script version,
- warm-up a measurement interval,
- latency histograms,
- throughput, error a saturation metrics,
- raw alebo dostatočne detailné artifacts.

Jeden run je slabý baseline. Potrebné sú opakovania alebo známa prirodzená variabilita.

## 29. Porovnávanie výsledkov

Regresiu posudzuj kombináciou:

- absolútneho SLO,
- relatívnej zmeny voči baseline,
- confidence intervalov alebo variability opakovaní,
- zmeny workloadu a environmentu,
- resource a trace evidence,
- praktickej prevádzkovej významnosti.

Štatisticky merateľný rozdiel nemusí byť prevádzkovo významný. Naopak malá zmena p99 pri kritickej službe môže prekročiť SLO.

## 30. Performance noise

Variabilitu vytvárajú shared hosts, CPU frequency scaling, background jobs, network jitter, GC, storage maintenance, autoscaling a cloud placement.

Kontroluj noise cez:

- izolované alebo zaznamenané prostredie,
- viac opakovaní,
- randomizované alebo striedané poradie A/B behov,
- stabilný dataset,
- dostatočne dlhý steady state,
- koreláciu s infra metrics.

## 31. Testovanie autoscalingu

Autoscaling je control loop:

```text
workload vytvorí signal
→ monitoring ho zozbiera a agreguje
→ autoscaler rozhodne
→ platforma provisionuje capacity
→ process sa inicializuje
→ readiness prejde
→ load balancer zaradí endpoint
→ traffic sa redistribuuje
```

Meraj detection, aggregation, decision, provisioning, startup a routing delay. Sleduj overshoot, oscillation, cooldown, scale-down safety a dopad na existujúce connections.

Autoscaling nenahrádza baseline capacity a nevyrieši bottleneck v shared database alebo quota.

## 32. Spike test

Spike test definuje:

- počiatočný steady workload,
- amplitúdu a rýchlosť nárastu,
- dĺžku spike-u,
- opakovanie spike-ov,
- návrat na baseline,
- success a recovery criteria.

Overuje queue absorption, rate limiting, cold starts, scale-up a správanie caches. Po spike-u musí systém odstrániť backlog bez dlhej tail latency alebo duplicate side effects.

## 33. Soak test

Soak test potrebuje dĺžku zodpovedajúcu podozrivým lifecycle-om, napríklad niekoľkým GC cycles, token rotations, log rotations, compactions alebo cache eviction obdobiam.

Sleduj trend, nie iba konečný stav:

- memory po GC,
- open files a sockets,
- goroutines, threads alebo tasks,
- queue depth,
- database bloat,
- disk growth,
- error rate v čase,
- throughput drift,
- credential alebo session expiry.

## 34. Stress test a bod degradácie

Stress test zvyšuje demand, kým systém prekročí plánovaný rozsah. Cieľom nie je iba číslo maximálneho throughputu, ale popis transition:

```text
healthy
→ rising queue
→ SLO violation
→ controlled rejection
→ degraded mode
→ recovery alebo collapse
```

Urči prvý saturation signal, prvý SLO breach, prvé rejection a bod nevratnej degradácie.

## 35. Graceful degradation

Preferovaný overload behavior je bounded a predvídateľný:

- admission control,
- bounded queues,
- rate limiting,
- prioritization,
- load shedding,
- deadlines a timeouts,
- circuit breakers,
- degraded read-only alebo cached response,
- ochrana kritických dependencies.

Globálne vyčerpanie threads, memory alebo database connections vytvára cascading failure a je slabým failure mode-om.

## 36. Retry amplification

Pri stress teste sleduj, či klienti, proxy a služby retryujú rovnaký failure. Viac vrstiev retries môže znásobiť demand presne v čase nedostatku capacity.

Testuj:

- max attempts,
- retryable errors,
- backoff a jitter,
- retry budget,
- idempotency,
- deadline propagation,
- circuit-breaker interaction.

## 37. Databázové performance testy

Modeluj:

- read/write mix,
- transaction length,
- isolation level,
- lock contention,
- connection pool,
- query plans,
- hot rows a indexes,
- replication lag,
- checkpoints a compaction,
- backup alebo maintenance overlap,
- failover a reconnect behavior.

Query benchmark bez aplikačnej concurrency nemusí odhaliť pool alebo transaction bottleneck.

## 38. Queue a broker systémy

Pri asynchronous systéme throughput producenta nie je dostatočný výsledok. Sleduj:

- arrival a consume rate,
- backlog a oldest-message age,
- consumer concurrency,
- redelivery a duplicate rate,
- partition skew,
- processing latency,
- dead-letter growth,
- recovery po consumer outage.

Backlog musí byť bounded a po peak-u sa má vyprázdniť v definovanom čase.

## 39. Cache performance

Cache test potrebuje explicitný stav:

- cold cache,
- warm steady cache,
- partial invalidation,
- eviction pressure,
- hot-key burst,
- cache dependency outage.

Vysoký hit rate môže skrývať neprijateľný origin load pri invalidácii alebo reštarte.

## 40. Network a protocol limity

Sleduj connection setup, TLS handshakes, keepalive reuse, HTTP/2 alebo HTTP/3 streams, retransmissions, bandwidth, packet loss, NAT a ephemeral-port pressure.

Generator blízko servera nemusí reprezentovať regionálnu latency ani mobile network. Network emulation musí mať zdokumentované delay, jitter, loss a bandwidth parametre.

## 41. Cost a efficiency

Performance výsledok možno normalizovať na cost:

```text
completed business operations
÷ infrastructure cost
```

Vyšší throughput za cenu neúmerne väčšieho clusteru nemusí byť efektívnejšie riešenie. Sleduj performance per replica, per CPU alebo per monetary unit podľa rozhodnutia.

## 42. Bezpečnosť experimentu

Pred spustením definuj:

- povolený environment a čas,
- allowlist targetov,
- maximálny arrival rate a concurrency,
- downstream limits,
- test identities a data cleanup,
- cost cap,
- observability dashboard,
- emergency stop,
- ownera a komunikačný kanál,
- zákaz produkčného testu bez explicitného schválenia.

Load script má zlyhať zatvorene, ak target identity nie je očakávaná.

## 43. Failure artifacts

Uchovaj:

- load script a jeho revision,
- resolved workload parameters,
- artifact a environment provenance,
- raw histograms a time series,
- generator metrics,
- server, dependency a infrastructure metrics,
- traces alebo profiles pre reprezentatívne samples,
- logs s correlation IDs,
- autoscaling a deployment events,
- abort alebo operator actions.

Screenshot dashboardu sám osebe nie je dostatočne analyzovateľný dôkaz.

## 44. Performance report

Report má obsahovať:

1. cieľ a hypotézu,
2. testovaný artifact a environment,
3. workload a dataset model,
4. open/closed semantics,
5. fázy a trvanie,
6. success a abort criteria,
7. latency histograms, throughput a error classes,
8. resource, queue a dependency evidence,
9. bottleneck a failure transition,
10. recovery behavior,
11. porovnanie s baseline,
12. limity interpretácie,
13. odporúčanie pre capacity alebo release.

## 45. Diagnostický workflow

1. Over, že generator dosiahol plánovaný arrival rate.
2. Potvrď artifact, environment a dataset identity.
3. Oddeľ client-side scheduling, transport a server latency.
4. Nájdite prvý rastúci queue alebo wait metric.
5. Koreluj SLO breach s CPU, memory, I/O, DB, broker a dependency metrics.
6. Skontroluj retries, timeouts a rejection classes.
7. Over, či throughput plateau nie je limit generatora.
8. Sleduj transition počas ramp-up, nie iba finálny interval.
9. Over recovery po ramp-down.
10. Reprodukuj bottleneck cieleným experimentom s jednou zmenou.

## 46. Časté anti-patterny

### Priemer je pod limitom

Tail latency alebo error class môže porušovať SLO.

### Viac virtual users znamená presne viac loadu

V closed modeli request rate závisí od response time a think time.

### Stress test je iba väčší load test

Stress test musí skúmať failure transition, ochrany a recovery.

### CPU nie je 100 %, systém má rezervu

Bottleneck môže byť lock, connection pool, disk, quota, partition alebo serial section.

### Polovičný environment vynásobíme dvoma

Scaling nie je automaticky lineárny.

### Jeden run je baseline

Cloud noise alebo warm-up stav môže vytvoriť náhodný výsledok.

### Generator report je jediný dôkaz

Bez server-side a dependency telemetry nemožno vysvetliť bottleneck.

### Autoscaling vyrieši každý spike

Control loop má latency a môže naraziť na shared bottleneck.

## 47. Prevádzkový checklist

Pred performance testom over:

- hypotéza a rozhodnutie sú explicitné,
- workload model reprezentuje produkčný demand,
- open/closed semantics sú správne,
- artifact, environment a dataset sú identifikované,
- generator má dostatočnú rezervu,
- warm-up a steady-state podmienky sú definované,
- percentily majú dostatočný sample count,
- coordinated omission je riešené,
- success, abort a recovery criteria sú merateľné,
- server a dependency telemetry sú dostupné,
- test je bezpečný pre downstream a cost,
- raw artifacts sa uchovajú,
- baseline a variabilita sú známe.

## 48. Zhrnutie

Dôveryhodný performance test je kontrolovaný experiment. Spája reprezentatívny demand model, immutable artifact, zdokumentované prostredie, validovaný generator, latency distributions, completed throughput, saturation a dependency evidence. Load test potvrdzuje plánovanú prevádzku, stress test skúma failure transition, spike test control-loop reakciu, soak test kumulatívnu stabilitu a capacity test udržateľný limit. Výsledok musí vždy obsahovať aj recovery a limity interpretácie.

## 49. Kontrolné otázky

1. Aký je rozdiel medzi arrival rate, concurrency a completed throughput?
2. Kedy použiť open a kedy closed workload model?
3. Čo je coordinated omission?
4. Prečo sa percentily medzi generátormi nemajú priemerovať?
5. Ako rozlíšiš utilization od saturation?
6. Čo dokazuje Littleho zákon a aké má limity?
7. Kedy je warm-up ukončený?
8. Prečo steady throughput s rastúcim backlogom nie je steady state?
9. Ako sa testuje celý autoscaling control loop?
10. Aké failure transition má skúmať stress test?
11. Čo musí obsahovať reprodukovateľný baseline?
12. Ako overíš, že load generator nie je bottleneck?
13. Prečo je recovery povinnou časťou testu?
14. Ako retry amplification mení overload?

## Glossary impact

Relevantné pojmy: performance test, load test, stress test, spike test, soak test, capacity test, scalability test, open workload model, closed workload model, arrival rate, concurrency, completed throughput, tail latency, coordinated omission, saturation, queueing, steady state, load shedding, retry amplification a performance baseline.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Smoke a regression tests](smoke-and-regression-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Security a infrastructure tests →](security-and-infrastructure-tests.md)
<!-- KNOWLEDGE-NAVIGATION:END -->