# RED method

RED je service-oriented measurement model pre workloady, ktoré prijímajú jednotku práce a produkujú caller-visible alebo business-visible outcome. Sleduje **Rate**, **Errors** a **Duration**, ale tieto tri slová nemajú význam bez presnej operation boundary, denominatora a success contractu.

RED nie je univerzálny dashboard template. Je to spôsob, ako zachovať konzistentný obraz demandu, correctness a latency od logical operation cez technical attempts až po dependency path. Pri zlom scope-e môže RED vyzerať zdravo a súčasne maskovať retry amplification, fast failures alebo dlhý queue wait.

## 1. Dominantný lifecycle

```text
user alebo caller outcome
→ exact logical-operation a measurement boundary
→ valid-operation population
→ Rate denominator contract
→ Error numerator a success semantics
→ Duration boundary a distribution
→ bounded dimensions a cohort identity
→ attempt, retry, fan-out a dependency decomposition
→ SLI/dashboard/alert generation
→ investigation a capacity correlation
→ bounded recovery
→ original a forbidden outcome validation
```

Základné rozlíšenie:

```text
logical operation
≠ technical attempt
≠ dependency call
≠ queue message delivery
≠ batch item
```

Ak sa tieto jednotky zmiešajú, rate, error ratio aj duration prestanú byť interpretovateľné.

## 2. Exact RED subject

Pre Atlas Payments:

```text
RED subject: RED-PAY-43
business capability: CAP-PAY-42
logical operation: settle(payment_id)
entry boundary: accepted valid settlement request
completion boundary: durable ledger + provider outcome reconciled
release generation: 7.19.1
RED schema generation: RED-PAY-8
measurement window: 5 minút a 28-dňové SLO
cohorts: operation, result class, release, Region/AZ, bounded merchant class
```

Subject určuje, či meranie reprezentuje client journey, service handler, queue consumer alebo provider attempt. Rovnaký názov „latency“ na týchto boundaries neznamená rovnaký čas.

## 3. Rate: koľko práce skutočne prichádza a dokončuje sa

Rate je počet definovaných units za čas. Najprv pomenuj unit a observation point.

```text
logical settlement accepted rate
logical settlement completed rate
provider attempt rate
queue delivery rate
ledger commit rate
```

Tieto rates sa môžu legitímne líšiť. Jeden settlement môže vytvoriť viac provider attempts a queue redeliveries. Completed rate môže za accepted rate zaostávať pre queue wait a processing latency.

### Denominator contract

Rate contract obsahuje:

- čo vytvorí jednu unit;
- kde sa počíta;
- či ide o accepted, started alebo completed operations;
- ako sa deduplikuje retry alebo redelivery;
- ako sa spracúva batch;
- ktoré traffic classes sú validné;
- čo znamená absent traffic.

Traffic drop môže znamenať nižší demand, routing failure, neúspešný deployment alebo telemetry loss. Rate sa preto interpretuje spolu s expected traffic, upstream evidence a telemetry freshness.

## 4. Errors: ktoré outcomes porušili contract

Error je operation, ktorá nesplnila definovaný caller alebo business contract. HTTP status class môže byť observation, nie celý verdict.

```text
HTTP 200 s nesprávnym settlement resultom = business failure
HTTP 202 bez následnej completion v deadline = workflow failure
HTTP 404 pre neexistujúci public resource = môže byť expected outcome
provider timeout po úspešnom durable commit-e = unknown outcome, nie automaticky safe retry
fallback response = success alebo degraded failure podľa SLO
```

### Numerator a denominator

```text
logical error rate
= failed valid logical operations
/ all valid logical operations
```

Numerator a denominator musia používať rovnakú unit, scope a time semantics. `failed provider attempts / unique settlements` nie je error ratio; je to zmiešanie dvoch populations.

### Final, partial a unknown outcomes

Distributed operation môže skončiť:

- definitive success;
- definitive failure;
- partial success;
- cancellation;
- deadline exceeded;
- unknown side-effect outcome;
- success after retry;
- unreconciled state.

RED schema má tieto classes explicitne modelovať. Unknown outcome nesmie byť schovaný medzi generic errors, ak potrebuje reconciliation pred ďalším pokusom.

## 5. Duration: ako dlho trvá definovaná práca

Duration potrebuje začiatok, koniec a population. Pre settlement journey:

```text
client end-to-end duration
= edge + acceptance + queue wait + processing + provider attempts
  + retry backoff + ledger commit + completion delivery
```

Service-handler duration môže byť 80 ms, zatiaľ čo async completion trvá 8 sekúnd. Provider-attempt duration môže byť krátka, ale viac retries predĺži logical-operation duration.

### Distribution, nie average

Average latency môže zostať stabilná, aj keď malý kritický cohort zažíva výrazný tail. Používaj histogram/distribution, threshold compliance a vhodné percentiles.

Successful a failed duration sleduj oddelene. Fast rejection alebo circuit-breaker failure môže znížiť aggregate p95 a predstierať performance improvement, hoci user success klesol.

### Measurement point

Client, edge, server, consumer a dependency merajú rozdielne intervals. Dashboard musí measurement point pomenovať. „Request duration“ bez boundary je neúplný contract.

## 6. Bounded operation dimensions

RED musí umožniť zúženie critical cohortu bez unbounded cardinality. Vhodné dimensions:

```text
service.name
operation alebo normalized route
protocol/method
result.class
release channel alebo bounded version cohort
Region/AZ
dependency name
bounded merchant class
```

Raw URL, payment ID, request ID, trace ID alebo error message do metric labels nepatria. Per-operation detail sa získava cez exemplar, trace a structured logs.

Operation names majú byť stabilné. `/payments/{id}/settle` je agregovateľný contract; `/payments/938472/settle` vytvára novú series pre každý business object.

## 7. Retries a attempt amplification

Retry mení všetky tri RED axes:

```text
attempt Rate rastie
attempt Errors rastú
logical Duration rastie
successful final outcome môže zostať dočasne stabilný
```

Preto sleduj samostatne:

- logical operations;
- attempts;
- retry reason;
- attempts per operation distribution;
- success after retry;
- exhausted retries;
- backoff wait;
- dependency attempt RED;
- unknown outcomes a reconciliation.

Final success-only dashboard môže skryť rastúce dependency failures a blížiaci sa capacity cliff. Retry nie je bezplatná reliability vrstva; spotrebúva connections, threads, queue slots a downstream quota.

## 8. Fan-out, batching a caching

Jedna logical operation môže vytvoriť viac parallel dependency calls. Dependency rate preto môže rásť bez rastu user trafficu. Fan-out contract potrebuje expected calls per operation a partial-failure semantics.

Batch môže obsahovať desiatky items. Rozlišuj batch attempt, item outcome a final checkpoint. Jeden failed batch nie je automaticky 100 failed business items.

Cache mení execution path. Celková service duration môže byť zdravá pri vysokom hit ratio, zatiaľ čo origin miss path je nefunkčný. Sleduj hit/miss rate, hit/miss duration, stale serve, fill errors a origin RED oddelene.

## 9. HTTP a gRPC adaptation

### HTTP

HTTP RED sa typicky viaže na normalized route a final application semantics. Status class je užitočný bounded dimension, ale business outcome môže vyžadovať ďalšiu result class.

```text
http.server.request.count
http.server.request.duration
logical settlement completion counters
```

Server request metrics a business completion metrics sa dopĺňajú; jedno nenahrádza druhé.

### gRPC

gRPC error semantics vychádzajú z gRPC statusu a operation contractu, nie iba underlying HTTP transportu. Streaming calls potrebujú message rate, stream age, cancellation, deadline a lag; dlhý duration môže byť normálny healthy channel.

## 10. Queues a asynchronous consumers

Pri queue workload-e je kritické rozlíšiť delivery od logical processingu.

```text
message received rate
→ processing attempts
→ successful logical completions
→ acknowledgement alebo redelivery
```

Doplň queue depth, oldest message age, consumer lag, redelivery count, concurrency a dead-letter rate. Processing duration bez queue wait môže byť green, hoci business freshness objective je porušený.

Span links a logical-operation ID pomáhajú spojiť producer, message a consumer bez falošného synchronous parent-child modelu.

## 11. Batch jobs

Pre batch jobs možno RED prispôsobiť:

- Rate — jobs alebo items completed za obdobie;
- Errors — failed jobs/items pri správnom partial-success modeli;
- Duration — job a item processing distribution.

Batch však potrebuje freshness, last successful completion, expected schedule, checkpoint progress a backlog. Nulový rate mimo schedule nie je incident; nulový rate počas expected window môže byť critical failure.

## 12. RED a SLO

RED signals často tvoria request-based SLIs, ale dashboard nie je automaticky SLO.

Availability SLI:

```text
valid successful logical operations
/ all valid logical operations
```

Latency SLI:

```text
valid successful logical operations dokončené do threshold
/ all valid logical operations
```

SLO contract určuje valid traffic, success semantics, measurement boundary, latency threshold, window, exclusions, retries, partial/unknown outcomes a no-data behavior.

Attempt metrics sú diagnostické a capacity-relevantné. Logical-operation metrics sú typicky bližšie user outcome-u.

## 13. RED, Golden Signals a USE

RED sleduje service work:

```text
Rate, Errors, Duration
```

Golden Signals používajú Traffic, Errors, Latency a Saturation. Saturation dopĺňa otázku, ako blízko je systém k effective capacity boundary.

USE sleduje resources cez Utilization, Saturation a Errors. Investigation chain:

```text
RED ukáže caller-facing symptom
→ trace alebo dependency RED lokalizuje component
→ USE identifikuje resource/enforcement bottleneck
→ logs alebo profile vysvetlia mechanizmus
```

RED môže byť green tesne pred capacity cliffom. Preto neodstraňuj saturation a queue signals iba preto, že nejde o písmeno v RED.

## 14. Dashboard a alert contract

RED dashboard má podporovať investigation flow:

```text
total logical Rate a completion gap
→ logical Error ratio podľa result class
→ successful/failed Duration distributions
→ breakdown operation/release/AZ
→ attempts per operation a dependency RED
→ deployment/config events
→ exemplar/trace/log links
```

Alertuj na user impact alebo SLO risk. Vhodné sú fast/slow burn, sustained zero successful completions, excessive queue age alebo abnormal attempt amplification s downstream riskom.

Rate spike bez error/latency impactu môže byť legitimate growth. Rate drop bez errors môže byť sezónnosť, upstream failure alebo telemetry gap. Alert potrebuje expected traffic alebo multi-signal confirmation.

## 15. Worked failure: retry layer rozbije RED semantics

### Exact subject

```text
RED-PAY-43
release: 7.19.1
operation: settle(payment_id)
window: 10:00–10:05 UTC
logical operations: 10,000
provider retry policy: max 3 attempts
RED schema generation: RED-PAY-8
provider timeout generation: TIMEOUT-12
```

### Change

Release `7.19.1` zníži provider timeout a pridá dve immediate retries bez jitteru. Cieľom bolo znížiť final failure rate pri transient provider latency.

### Observed counts

```text
9,100 logical operations succeed on first attempt
800 logical operations succeed on third attempt
100 logical operations exhaust three attempts

logical operations = 10,000
logical failures = 100
provider attempts = 11,800
failed provider attempts = 1,900
```

Správny logical error rate:

```text
100 / 10,000 = 1 %
```

Attempt failure ratio:

```text
1,900 / 11,800 ≈ 16.1 %
```

Chybný mixed ratio:

```text
1,900 failed attempts / 10,000 logical operations = 19 %
```

Posledný výpočet nie je error rate žiadnej konzistentnej population.

### False-green duration

Immediate retries a otvorený circuit breaker vytvoria veľa fast rejected attempts. Attempt p95 klesne z `350 ms` na `90 ms`. End-to-end logical-operation p95 však rastie na `4.8 s` pre retry/backoff a pool queueing.

Dashboard sledujúci iba attempt duration preto ukazuje „zlepšenie“, zatiaľ čo user journey sa zhoršila.

### Competing hypotheses

1. reálny client traffic vzrástol o 18 %;
2. client posiela duplicate logical requests;
3. metrics pipeline duplikuje samples;
4. internal retry amplification zvyšuje provider attempts;
5. fan-out change pridala viac provider calls;
6. provider latency a connection pool vytvárajú queueing;
7. logical-operation instrumentation vynecháva časť completions.

### Discriminating evidence

```text
ingress logical-operation counter
→ idempotency/logical ID uniqueness
→ attempts-per-operation histogram
→ trace spans a retry events
→ provider connection-pool saturation
→ retry reason a timeout generation
→ release event
→ final business reconciliation
```

Evidence ukáže stabilných `10,000` logical operations, no `11,800` provider attempts. Traces zobrazia immediate retries rovnakého logical operation ID. Connection pool wait a provider throttling rastú. Final settlements sa oneskorujú a 100 operations zlyhá.

Root cause je retry policy bez jitteru a downstream protection. Measurement defect zmiešal attempts s logical operations a fast failures s successful duration, čím zhoršenie nesprávne prezentoval.

### Evidence-preserving containment

- vrátiť retry policy na bounded previous generation;
- obmedziť provider concurrency a chrániť connection pool;
- zachovať attempt/logical counters, traces a pool metrics;
- nepovažovať broad timeout increase za root-cause fix;
- pred ďalším pokusom reconciliovať unknown provider outcomes;
- neodstrániť business-completion monitoring.

### Authoritative recovery

1. oddeliť logical-operation a attempt metrics;
2. pridať attempts-per-operation histogram;
3. merať end-to-end logical duration vrátane queue/backoff;
4. sledovať successful a failed duration oddelene;
5. zaviesť exponential backoff, jitter a retry budget;
6. používať idempotency a reconciliation pred retry po unknown outcome;
7. canary rollout s dependency RED a saturation guardrails;
8. aktualizovať SLO/dashboard queries na schema `RED-PAY-9`.

### Acceptance verdict

- logical error ratio používa konzistentný numerator/denominator;
- attempt amplification zostáva v retry budgete;
- logical p95/p99 a completion SLI sa obnovia;
- provider pool a throttle saturation majú headroom;
- final ledger/provider reconciliation obsahuje exactly one outcome;
- forbidden duplicate authorization nevznikne;
- sampled traces a logs korelujú s authoritative counters;
- second canary load wave nevytvorí rovnakú amplification.

### Earlier controls

- schema test zakazujúci mix logical a attempt units;
- retry-policy load test s dependency throttlingom;
- dashboard panel pre attempts/logical ratio;
- explicit successful/failed logical duration;
- SLO query review pri každej retry alebo async-boundary zmene;
- alert na retry amplification a connection-pool saturation.

## 16. Troubleshooting podľa RED

### Rate klesne bez rastu errors

Over expected demand, upstream routing, deployment registration, queue producer, signal freshness a seasonality. Nulový rate môže byť incident aj telemetry failure.

### Errors rastú a duration klesá

Hľadaj fast rejection, authentication failure, open circuit breaker, validation failure alebo dependency unavailable pred reálnym spracovaním.

### Duration rastie pri nízkom CPU

Hľadaj downstream wait, lock, connection pool, hidden queue, DNS/TLS retry, rate limiting alebo storage/network latency. CPU nie je univerzálny saturation signal.

### Rate rastie, Errors a Duration sú zatiaľ stabilné

Over queue, pool, quota a failover headroom. Healthy current outcome môže byť tesne pred capacity cliffom.

### Final success je stabilný, attempt rate rastie

Hľadaj retries, hedging, fan-out alebo redelivery. Stabilný final success nemusí znamenať stabilný cost a reliability margin.

## 17. Anti-patterny

### RED iba na service total

Malá kritická operation alebo cohort sa stratí v aggregate.

### Status code ako celý error contract

Business, partial a degraded outcomes zostanú skryté.

### Failed attempts nad logical denominatorom

Výsledok nie je konzistentný error ratio.

### Average alebo mixed successful/failed duration

Tail a fast failures skreslia user experience.

### Raw route alebo business ID ako label

Vytvára unbounded cardinality.

### Final success bez attempt a saturation visibility

Retry amplification zostane neviditeľná až do capacity collapse-u.

### Handler duration ako async end-to-end latency

Queue wait a completion path chýbajú.

### RED ako náhrada za traces, USE a business reconciliation

RED deteguje service symptom, ale nemusí vysvetliť interný mechanizmus ani correctness state.

## 18. Kontrolné otázky

1. Čo musí obsahovať exact RED subject?
2. Ako sa líši logical operation, attempt a dependency call?
3. Prečo numerator a denominator musia používať rovnakú population?
4. Kedy `2xx` nie je business success?
5. Prečo failed a successful duration sledovať oddelene?
6. Ako retry mení Rate, Errors a Duration?
7. Ako sa RED prispôsobí async queue a batch workloadu?
8. Ako sa RED viaže na SLO, Golden Signals a USE?
9. Prečo attempt p95 v worked failure predstieral zlepšenie?
10. Aký acceptance verdict uzavrel incident `RED-PAY-43`?

## Glossary impact

Relevantné pojmy: RED subject, logical-operation boundary, measurement population, Rate denominator contract, Error numerator contract, final-outcome class, unknown-outcome class, logical duration, attempt duration, attempt amplification, attempts-per-operation distribution, retry budget, completion gap, dependency RED a RED acceptance verdict.

## Primárne zdroje

- [Prometheus instrumentation practices](https://prometheus.io/docs/practices/instrumentation/)
- [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Grafana dashboard best practices — RED method](https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/best-practices/)
- [OpenTelemetry HTTP semantic conventions](https://opentelemetry.io/docs/specs/semconv/http/)
- [OpenTelemetry messaging semantic conventions](https://opentelemetry.io/docs/specs/semconv/messaging/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Instrumentation a telemetry](instrumentation-telemetry.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: USE method →](use-method.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
