# Performance, load a stress tests

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

## 1. Definícia

Performance testing overuje časové a kapacitné vlastnosti systému pod definovaným workloadom. Nejde iba o otázku, koľko requests systém zvládne. Test musí sledovať najmenej:

- latency distribúciu,
- throughput,
- concurrency,
- resource utilization a saturation,
- error rate,
- queueing,
- stabilitu počas času,
- správanie pri degradácii a recovery.

Výsledok bez workload modelu, prostredia a success criteria nie je reprodukovateľný performance dôkaz.

## 2. Základné druhy testov

### Performance test

Širší pojem pre meranie časových a kapacitných vlastností pri definovaných podmienkach.

### Load test

Overuje očakávaný alebo plánovaný workload. Cieľom je zistiť, či systém spĺňa SLO a kapacitné požiadavky pri normálnej prevádzke.

### Stress test

Zvyšuje záťaž nad plánovaný rozsah, kým systém nedegraduje alebo nezlyhá. Sleduje failure mode, ochranné mechanizmy a recovery.

### Spike test

Simuluje prudký nárast alebo pokles trafficu. Overuje autoscaling, queueing, connection pools, caches a cold-start behavior.

### Soak alebo endurance test

Udržiava záťaž dlhý čas. Hľadá memory leaks, resource leaks, rast queues, fragmentation, cache churn a kumulatívne zlyhania.

### Capacity test

Hľadá maximálny udržateľný workload pri definovaných SLO a safety margins.

### Scalability test

Overuje, ako sa výsledky menia po pridaní CPU, memory, replicas alebo partitions. Rozlišuje vertical a horizontal scaling.

## 3. Workload model

Workload musí reprezentovať reálnu prevádzku:

```text
operations mix
+ arrival rate
+ concurrency
+ payload distributions
+ think time
+ session behavior
+ cache state
+ data volume
+ regional/network characteristics
```

Test s jediným malým requestom a rovnomerným trafficom môže zásadne podhodnotiť produkčné riziko.

### Open workload model

Requests prichádzajú podľa arrival rate nezávisle od odozvy systému. Lepšie reprezentuje externý traffic a odhalí queue buildup.

### Closed workload model

Fixný počet virtual users posiela ďalšiu operáciu až po dokončení predchádzajúcej. Pri spomalení systému prirodzene klesne request rate, čo môže skryť overload.

## 4. Latency distribúcia

Priemer nestačí. Sleduj minimálne:

- median alebo p50,
- p90,
- p95,
- p99,
- maximum iba ako doplnkový signál,
- error latency oddelene od successful latency.

Príklad:

```text
p50 = 80 ms
p95 = 240 ms
p99 = 1.8 s
```

Priemer môže vyzerať prijateľne, hoci významná časť používateľov zažíva vysokú tail latency.

## 5. Coordinated omission

Coordinated omission vzniká, keď load generator počas spomalenia neposiela requests, ktoré by v reálnom open modeli prišli. Nameraná latency potom ignoruje čas, počas ktorého klient čakal na možnosť request vôbec odoslať.

Ochrana:

- používať arrival-rate model,
- zaznamenávať intended send time,
- reportovať corrected latency,
- validovať generator capacity.

## 6. Throughput a concurrency

Little's Law poskytuje orientačný vzťah:

```text
concurrency ≈ throughput × response time
```

Ak throughput zostáva rovnaký, ale latency rastie, rastie aj počet rozpracovaných operácií. To zvyšuje tlak na:

- connections,
- threads alebo event-loop tasks,
- memory,
- queue depth,
- downstream dependencies.

## 7. Bottleneck a saturation

Performance test musí korelovať aplikačné výsledky s resource metrics:

- CPU utilization, run queue a throttling,
- memory, GC, page faults a OOM,
- disk latency, IOPS a queue depth,
- network bandwidth, retransmissions a connection states,
- database locks, pool saturation a query latency,
- thread pools, worker queues a event-loop lag,
- cache hit rate a eviction,
- rate limits a downstream quotas.

Vysoká utilization sama osebe nemusí byť problém. Kritická je saturation, queueing a dopad na SLO.

## 8. Load profile

Test má explicitné fázy:

```text
warm-up
→ ramp-up
→ steady state
→ peak/spike
→ ramp-down
→ recovery observation
```

Bez warm-upu výsledok ovplyvnia cold caches, JIT compilation, connection establishment a lazy initialization.

Príliš rýchly ramp-up môže testovať iba startup behavior namiesto udržateľnej kapacity.

## 9. Testovacie prostredie

Výsledok je platný iba pre zdokumentovanú konfiguráciu:

- hardware alebo instance type,
- CPU/memory limits,
- replica count,
- autoscaling policy,
- database size a indexes,
- cache state,
- network path,
- dependency versions,
- logging a tracing overhead,
- production-like data distributions.

Malé shared test environment môže merať jeho obmedzenia, nie kapacitu produkčného návrhu.

## 10. Load generator

Load generator je tiež systém s limitmi. Sleduj:

- CPU a network utilization generatora,
- connection a file descriptor limity,
- timer precision,
- dropped samples,
- clock synchronization,
- client-side errors,
- počet generator nodes.

Ak generator saturuje, môže vytvoriť falošný throughput plateau.

## 11. Success criteria

Príklad merateľného kontraktu:

```text
Pri 1 500 requests/s počas 30 minút:
- p95 < 250 ms,
- p99 < 600 ms,
- error rate < 0.1 %,
- bez OOM alebo restartu,
- database pool utilization < 80 %,
- backlog sa po skončení špičky vyprázdni do 2 minút.
```

Success criteria majú vychádzať zo SLO, capacity planu a failure budgetu, nie z ľubovoľného čísla.

## 12. Baseline a porovnávanie

Baseline musí obsahovať:

- commit alebo artifact version,
- konfiguráciu,
- dataset,
- workload profile,
- environment,
- tool version,
- výsledné distributions a resource metrics.

Regresiu posudzuj kombináciou:

- absolútnych SLO limitov,
- relatívneho rozdielu voči baseline,
- štatistickej variability,
- technického vysvetlenia zmeny.

Jediný run nie je spoľahlivý baseline.

## 13. Testovanie autoscalingu

Overuj celý control loop:

```text
metric vznikne
→ monitoring ju zozbiera
→ autoscaler rozhodne
→ platforma vytvorí capacity
→ workload sa inicializuje
→ load balancer ju zaradí
```

Meraj:

- detection delay,
- provisioning delay,
- readiness delay,
- overshoot a oscillation,
- scale-down safety,
- dopad na existing connections.

Autoscaling nenahrádza baseline capacity a nemôže odstrániť bottleneck v shared database.

## 14. Stress a graceful degradation

Stress test nemá iba nájsť bod kolapsu. Má overiť:

- admission control,
- bounded queues,
- rate limiting,
- timeouts,
- circuit breakers,
- load shedding,
- priority traffic,
- degraded response mode,
- automatické recovery.

Preferovaný failure mode je kontrolované odmietnutie časti práce, nie globálny cascading failure.

## 15. Databázy a stavové systémy

Testuj realisticky:

- read/write ratio,
- hot keys alebo hot partitions,
- index selectivity,
- transaction contention,
- connection pool,
- replication lag,
- compaction/checkpoints,
- storage growth,
- backup alebo maintenance overlap.

Prázdna databáza môže viesť k nereprezentatívnym query plans a cache hit rate.

## 16. Bezpečnosť testu

Load test môže spôsobiť incident. Pred spustením definuj:

- povolené prostredie a čas,
- maximálny arrival rate,
- emergency stop,
- kontakty a ownership,
- ochranu downstream služieb,
- test data a cleanup,
- cost limit,
- observability dashboard,
- zákaz smerovania na produkciu bez explicitného schválenia.

## 17. Výstup testu

Report má obsahovať:

1. cieľ a hypotézu,
2. environment a artifact version,
3. workload model,
4. success criteria,
5. latency/throughput/error výsledky,
6. resource a dependency metrics,
7. bottleneck evidence,
8. failure a recovery behavior,
9. porovnanie s baseline,
10. odporúčania a limity interpretácie.

## 18. Typické omyly

### „Priemer je pod limitom, test prešiel“

Tail latency môže porušovať SLO.

### „Viac virtual users znamená vyšší load“

Závisí od think time, response time a open/closed modelu.

### „Stress test je iba väčší load test“

Stress test skúma failure mode a recovery za hranicou plánovanej kapacity.

### „CPU nie je 100 %, systém má rezervu“

Bottleneck môže byť lock, database, I/O, quota alebo serial section.

### „Test environment je polovičný, výsledok vynásobíme dvoma“

Škálovanie nemusí byť lineárne.

### „Autoscaling vyrieši každý spike“

Control loop má latency a môže naraziť na ďalší bottleneck.

## 19. Kontrolné otázky

1. Aký je rozdiel medzi load, stress, spike a soak testom?
2. Aký je rozdiel medzi open a closed workload modelom?
3. Čo je coordinated omission?
4. Prečo p95 a p99 poskytujú iný signál než priemer?
5. Ako súvisia throughput, latency a concurrency?
6. Ako odlíšiš bottleneck od vysokej, ale zdravej utilization?
7. Čo musí obsahovať reprodukovateľný baseline?
8. Ako otestuješ autoscaling control loop?
9. Aké ochrany má overiť stress test?
10. Ako bezpečne spustíš load test v zdieľanom prostredí?

## Glossary impact

Relevantné pojmy: performance test, load test, stress test, spike test, soak test, open workload model, closed workload model, coordinated omission, tail latency, throughput, concurrency, saturation, load shedding, capacity test a scalability test.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Smoke a regression tests](smoke-and-regression-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Security a infrastructure tests →](security-and-infrastructure-tests.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
