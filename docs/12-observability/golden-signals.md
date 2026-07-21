# Golden Signals

Google SRE definuje štyri Golden Signals pre user-facing systémy: **Latency**, **Traffic**, **Errors** a **Saturation**. Metodika spája caller experience s capacity riskom a poskytuje minimálny konzistentný monitoring model pre služby, ktoré musia spoľahlivo obsluhovať demand.

Golden Signals nie sú univerzálny zoznam štyroch konkrétnych metrics. Každý workload musí presne definovať measurement boundary, success semantics, demand unit a saturation resource.

## 1. Mentálny model

```text
ako dlho operácia trvá?          → Latency
koľko demandu systém dostáva?    → Traffic
koľko operácií zlyháva?          → Errors
ako blízko je systém k limitu?   → Saturation
```

Ak sa tieto štyri signály merajú na správnej vrstve, poskytujú základný obraz user impactu aj capacity pressure.

## 2. Latency

Latency je čas potrebný na obslúženie requestu alebo jednotky práce.

Measurement points:

- client-observed latency,
- edge/load-balancer latency,
- server-handler latency,
- dependency latency,
- queue wait,
- end-to-end workflow latency.

Musí byť jasné, ktorú boundary metric reprezentuje.

### Successful a failed latency

Google SRE upozorňuje, že latency úspešných a neúspešných requestov treba oddeľovať.

Príklad:

- healthy request trvá 300 ms,
- database failure vráti HTTP 500 za 10 ms.

Ak sa obe skupiny zmiešajú, rast errors môže zdanlivo zlepšiť average latency.

Sleduj preto:

- successful latency distribution,
- failed latency distribution,
- timeout/cancellation latency,
- degraded/fallback latency.

### Tail latency

User experience často určuje tail, nie average.

Relevantné pohľady:

- histogram,
- p50 pre typický request,
- p95/p99 pre tail,
- podiel requestov pod SLO thresholdom,
- max iba ako diagnostický signal.

Percentile bez traffic volume môže byť nestabilný pri malom počte samples.

### Coordinated omission

Load test alebo client metric môže prehliadnuť obdobia, keď systém nevie prijímať novú prácu. Measurement model musí zahrnúť queueing, rejected requests a plánovaný arrival rate, nie iba dokončené requesty.

## 3. Traffic

Traffic vyjadruje demand kladený na systém v high-level workload-specific jednotke.

Príklady:

- HTTP requests za sekundu,
- concurrent sessions,
- messages za sekundu,
- bytes za sekundu,
- queries za sekundu,
- transactions za minútu,
- jobs alebo items za hodinu,
- model inferences za sekundu.

Traffic má odrážať business load, nie iba interný implementation detail.

### Traffic dimensions

Vhodné breakdowns:

- operation/route,
- client class,
- Region alebo zone,
- read/write,
- payload class,
- version,
- priority.

Labels musia zostať bounded.

### Traffic drop

Pokles trafficu môže znamenať:

- upstream outage,
- DNS/routing failure,
- load balancer deregistration,
- broken client release,
- business sezónnosť,
- instrumentation failure.

Preto traffic interpretuj s expected demand, black-box probes a upstream telemetry.

### Retry amplification

Internal traffic môže rásť rýchlejšie než user demand kvôli retries alebo fan-out.

Sleduj:

- external logical requests,
- internal attempts,
- retry rate,
- downstream amplification factor.

Inak môže byť príčina overloadu nesprávne pripísaná používateľom.

## 4. Errors

Errors sú operácie, ktoré nesplnili contract.

Typy:

- explicit failure response,
- timeout,
- cancellation,
- invalid alebo incomplete result,
- stale/degraded response,
- dropped message,
- retry exhaustion,
- policy alebo quota rejection,
- partial workflow failure.

Error semantics musia byť definované z pohľadu caller-a alebo business outcome-u.

### Error ratio

```text
failed valid operations / all valid operations
```

Urči:

- ktoré requesty sú valid,
- či client errors patria do SLI,
- ako sa počítajú retries,
- ako sa klasifikuje partial success,
- či fallback je success alebo degraded failure,
- ktorý measurement point je autoritatívny.

### Silent errors

Niektoré failures neprodukujú `5xx`:

- `200` s chybným obsahom,
- async message prijatá, ale nikdy spracovaná,
- stale cache response,
- data loss,
- background job sa nespustil,
- backup vznikol, ale nie je obnoviteľný.

Potrebné sú semantic checks a end-to-end validation.

## 5. Saturation

Saturation vyjadruje, ako blízko je systém alebo kritický resource k svojej kapacitnej hranici a koľko práce už čaká.

Príklady:

- CPU run queue alebo throttling,
- memory pressure a reclaim,
- thread-pool queue,
- connection-pool waiters,
- disk queue/latency,
- queue oldest message age,
- in-flight requests voči limitu,
- Lambda concurrency voči quota,
- subnet IP exhaustion,
- database connections,
- worker backlog.

Saturation je forward-looking signal. Latency a errors môžu byť ešte zdravé, ale systém môže byť tesne pred capacity cliffom.

### Priama a odvodená saturation

Priama:

- queue length,
- wait time,
- throttled requests,
- resource pressure.

Odvodená:

```text
current usage / effective capacity
```

Odvodené percento musí používať reálnu effective capacity po failover, reservations, limits a unavailable instances.

### Saturation nie je iba utilization

CPU utilization 90 % nemusí byť incident, ak nie je queueing ani SLO impact.

CPU utilization 40 % môže byť problém, ak:

- jeden core je saturovaný,
- container je throttled,
- critical thread je blocked,
- traffic je nerovnomerne rozdelený.

Saturation potrebuje wait/queue/error context.

## 6. Golden Signals podľa workloadu

### HTTP API

- Latency — request duration distribution,
- Traffic — requests/s,
- Errors — failed request ratio,
- Saturation — in-flight requests, worker/connection queues, CPU throttling.

### Queue consumer

- Latency — end-to-end message age a processing duration,
- Traffic — messages produced/consumed za sekundu,
- Errors — failed/dead-letter ratio,
- Saturation — backlog, oldest message age, busy workers.

### Batch pipeline

- Latency — job duration a data freshness,
- Traffic — items/jobs za obdobie,
- Errors — failed/partial jobs,
- Saturation — backlog, parallel slots, missed schedule window.

### Database

- Latency — query/transaction latency,
- Traffic — queries/transactions/s,
- Errors — failed/aborted transactions,
- Saturation — connections, locks, CPU, I/O queues, replica lag.

### Storage

- Latency — read/write operation latency,
- Traffic — IOPS alebo throughput,
- Errors — failed operations,
- Saturation — queue depth, provisioned limit, capacity.

### LLM inference service

- Latency — time to first token a total generation duration,
- Traffic — requests, input/output tokens za sekundu,
- Errors — provider/model/tool/validation failures,
- Saturation — GPU memory, batch queue, concurrency, rate limits.

## 7. Measurement layers

Jedna služba môže mať Golden Signals na viacerých vrstvách:

```text
client
→ edge/CDN
→ load balancer
→ application
→ dependency
→ resource
```

Rozdiel medzi vrstvami je diagnosticky cenný.

Príklad:

- client latency vysoká,
- edge latency vysoká,
- application latency nízka.

Možný problém je network, TLS, queue alebo edge processing mimo handler measurementu.

## 8. Golden Signals a SLI/SLO

Golden Signals poskytujú candidates pre SLIs.

### Availability

Errors a valid traffic definujú success ratio.

### Latency

Podiel validných requestov pod thresholdom.

### Throughput alebo freshness

Pre batch/queue systémy môže byť critical traffic completion alebo data freshness.

### Saturation

Saturation často nie je priamo user-facing SLI, ale je leading indicator a capacity alert signal.

SLO má zostať založené na user outcome. Saturation alert chráni error budget pred vyčerpaním.

## 9. Multi-window alerting

Golden Signals sú vhodné pre:

- fast burn alert pri prudkom outage,
- slow burn alert pri dlhšej miernej degradácii,
- saturation warning pred user impactom,
- traffic absence alert pri očakávanom demand-e.

Alert potrebuje:

- service a ownera,
- user impact,
- threshold/window,
- current SLO/budget context,
- links na dashboard, traces a runbook,
- suppression alebo maintenance model.

## 10. Dashboard hierarchy

### Service overview

- traffic,
- error ratio,
- latency distribution,
- saturation,
- SLO/burn,
- active deployments/incidents.

### Operation breakdown

- endpoint/method,
- dependency,
- Region/AZ,
- version,
- client class.

### Resource drilldown

- USE metrics,
- queues/pools,
- infrastructure failures,
- profiles.

Dashboard má viesť od user symptomu k root-cause evidence.

## 11. Golden Signals a RED

Mapovanie:

| Golden Signal | RED |
|---|---|
| Traffic | Rate |
| Errors | Errors |
| Latency | Duration |
| Saturation | samostatný doplnok |

RED je praktický service instrumentation pattern. Golden Signals explicitne zahŕňajú capacity risk.

## 12. Golden Signals a USE

Golden Signals začínajú user-facing systémom.

USE začína resources.

```text
Golden Signals lokalizujú user impact a capacity risk
→ RED rozdelí service operations
→ traces lokalizujú dependency path
→ USE analyzuje resource bottleneck
```

Metodiky sa dopĺňajú.

## 13. Golden Signals a black-box monitoring

White-box Golden Signals môžu byť nesprávne alebo nedostupné.

Doplň black-box measurements:

- DNS success/latency,
- TCP/TLS connection,
- HTTP status/content,
- end-to-end transaction,
- regional probes,
- synthetic queue/job.

Black-box signal overuje skutočný external contract, ale nemusí vysvetliť root cause.

## 14. Capacity a failure scenarios

Golden Signals testuj pri:

- traffic burst,
- loss jednej AZ,
- dependency slowdown,
- retry storm,
- cache miss burst,
- connection pool exhaustion,
- deployment surge,
- rate limit,
- partial network failure,
- telemetry backend failure.

Cieľom je overiť, že saturation rastie pred alebo spolu s user impactom a alerty majú správne poradie.

## 15. Troubleshooting patterns

### Latency a saturation rastú, traffic stabilný

Pravdepodobný capacity/resource bottleneck alebo dependency slowdown.

### Errors rastú, latency klesá

Fast rejection, auth/policy failure alebo circuit breaker.

### Traffic rastie, saturation rastie, latency zatiaľ stabilná

Systém sa blíži k hranici; over autoscaling delay a failover headroom.

### Traffic klesne na nulu, ostatné metrics zmiznú

Over upstream, DNS/routing, target registration a telemetry pipeline. Nulový error rate nie je zdravie bez trafficu.

### Saturation nízka, latency vysoká

Over downstream dependency, lock, network, queue mimo sledovaného scope-u alebo nesprávny capacity denominator.

## 16. Anti-patterny

### Štyri panely bez definovaného contractu

Názvy existujú, ale nie je jasné, čo sa počíta.

### Infrastructure traffic namiesto business demandu

Network bytes nemusia reprezentovať počet user operations.

### Error metric iba z exceptions

Timeouty, invalid results a rejected operations sa stratia.

### Saturation ako CPU percento

Ignoruje queueing, throttling, pools a service quotas.

### Latency iba na serveri

Client, edge alebo queue wait zostane neviditeľný.

### Traffic drop považovaný za zlepšenie

Errors aj saturation môžu klesnúť preto, že requesty sa k službe nedostanú.

## 17. Implementačný template

```text
Service/workflow:
User/caller:
Critical operations:

Latency:
- measurement point:
- successful/failed separation:
- distribution/threshold:

Traffic:
- demand unit:
- attempts vs logical operations:
- expected pattern:

Errors:
- success contract:
- numerator/denominator:
- degraded/partial outcomes:

Saturation:
- critical resources/queues:
- effective capacity:
- leading threshold:

SLO:
Alerts:
Dashboards:
Trace/log links:
Owner a runbook:
```

## 18. Kontrolné otázky

1. Ktoré sú štyri Golden Signals?
2. Prečo oddeľovať successful a failed latency?
3. Ako vyberieš traffic unit pre queue alebo batch workload?
4. Čo je silent error?
5. Prečo saturation nie je to isté ako utilization?
6. Ako retries menia traffic?
7. Ako Golden Signals súvisia so SLO?
8. Aký je rozdiel medzi Golden Signals, RED a USE?
9. Prečo dopĺňať black-box monitoring?
10. Ako by si definoval Golden Signals pre konkrétnu službu?

## Glossary impact

Relevantné pojmy: Golden Signals, latency, traffic, errors, saturation, successful latency, failed latency, tail latency, coordinated omission, demand unit, silent error, effective capacity, capacity cliff, leading indicator a black-box Golden Signals.

## Primárne zdroje

- [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Google SRE — Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/)
- [Google SRE — Practical Alerting from Time-Series Data](https://sre.google/sre-book/practical-alerting/)
- [Grafana dashboard best practices — Golden Signals](https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/best-practices/)
