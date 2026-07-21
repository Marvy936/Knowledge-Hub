# Metrics, logs, traces a events

Observability signals nie sú navzájom zameniteľné formáty rovnakých dát. Každý signal komprimuje alebo zachováva inú časť reality systému a odpovedá na iný typ otázky. Efektívna observability platforma preto nestojí na „čo najväčšom množstve dát“, ale na správnom výbere signals, spoločnom context-e a schopnosti prejsť od agregovaného symptómu ku konkrétnej operácii.

## 1. Mentálny model

```text
systém vykonáva operácie
→ instrumentation vytvára telemetry records
→ records sú spracované a uložené ako signals
→ metrics ukážu rozsah a trend
→ traces ukážu request path a causal context
→ logs vysvetlia detail udalosti alebo state-u
→ events ukážu významnú zmenu
→ audit records ukážu actor a control-plane action
→ profiles ukážu spotrebu resources na úrovni kódu
```

Žiadny signal sám osebe nepokrýva celý incident.

## 2. Signal a telemetry record

Signal je kategória telemetry s vlastným data modelom, semantics a query patternom.

Telemetry record typicky obsahuje:

- timestamp alebo časový interval,
- resource identity,
- service a environment,
- operation alebo event name,
- attributes alebo labels,
- value, body alebo status,
- correlation context,
- instrumentation scope,
- schema/version metadata.

Kvalita signalu závisí od správnej identity a contextu rovnako ako od samotnej hodnoty.

## 3. Metrics

Metric je číselné meranie zachytené v čase a agregované podľa definovaných dimensions.

Typické otázky:

- Koľko requestov prichádza?
- Aký je error rate?
- Aká je latency distribution?
- Koľko CPU alebo memory sa používa?
- Rastie queue depth?
- Plní služba SLO?

### Vlastnosti metrics

- efektívne agregovanie veľkého množstva operácií,
- time-series query a trend analysis,
- vhodné na alerting a capacity planning,
- bounded label set je kritický,
- detail jednotlivého requestu sa typicky stráca.

### Bežné metric semantics

#### Counter

Monotónne rastúca hodnota, ktorá sa resetne pri reštarte processu.

Príklady:

- počet requestov,
- počet errors,
- spracované bytes,
- počet retries.

Operational query typicky používa rate alebo increase za časové okno, nie surovú absolútnu hodnotu.

#### Gauge

Hodnota, ktorá môže rásť aj klesať.

Príklady:

- queue depth,
- aktuálny počet connections,
- memory usage,
- desired replicas.

Gauge môže reprezentovať okamžitý stav, ale bez správneho scrape intervalu nemusí zachytiť krátke spikes.

#### Histogram alebo distribution

Rozdelenie nameraných hodnôt.

Príklady:

- request duration,
- response size,
- queue wait time,
- batch size.

Latency sa nemá redukovať iba na average. Percentiles alebo bucket distributions odhaľujú tail latency a rozdiel medzi bežným a najhorším user experience.

### Metric identity a cardinality

Time series je definovaná kombináciou metric name a labels/attributes.

Rizikové dimensions:

- user ID,
- request ID,
- trace ID,
- full URL s náhodným path segmentom,
- exception message,
- container alebo Pod identity bez retention stratégie.

Neobmedzená cardinality môže zvýšiť ingestion, memory, storage a query cost alebo destabilizovať metrics backend.

### Temporality a aggregation

Metrics môžu používať cumulative alebo delta temporality podľa pipeline a backend contractu.

Pri návrhu over:

- kto drží aggregation state,
- čo sa stane pri reštarte,
- ako sa riešia duplicate alebo out-of-order samples,
- či backend očakáva cumulative alebo delta data,
- ako sa mení semantic pri downsamplingu.

## 4. Logs

Log je časovo označený record udalosti, state-u alebo diagnostickej správy.

Typické otázky:

- Prečo konkrétna operácia zlyhala?
- Aký exception alebo error code vznikol?
- Aké rozhodnutie application vykonala?
- Ktorá configuration alebo dependency bola použitá?
- Čo sa dialo tesne pred failure?

### Structured logs

Preferovaný production model používa stabilnú štruktúru:

```json
{
  "timestamp": "2026-07-21T18:00:00Z",
  "severity": "ERROR",
  "service.name": "orders-api",
  "deployment.environment": "production",
  "event.name": "payment.authorization.failed",
  "trace_id": "...",
  "span_id": "...",
  "order_id": "opaque-business-id",
  "provider": "payment-a",
  "error.type": "TimeoutError",
  "error.code": "UPSTREAM_TIMEOUT",
  "duration_ms": 2500
}
```

Výhody:

- query podľa fields bez parsovania voľného textu,
- stabilnejší alerting a dashboards,
- jednoduchšia correlation,
- kontrolovanejšia redaction,
- schema validation.

Human-readable message môže zostať doplnkom, nie jediným contractom.

### Severity

Severity musí vyjadrovať operational význam:

- `DEBUG` — detail pre vývoj a dočasnú diagnostiku,
- `INFO` — bežný významný lifecycle alebo business event,
- `WARN` — degradácia alebo neočakávaný stav bez okamžitého failure,
- `ERROR` — operácia zlyhala alebo vznikol významný incident signal,
- `FATAL` — process alebo kritický subsystem nemôže pokračovať.

Logovanie retryable transient erroru pri každom pokuse ako `ERROR` môže vytvoriť alert noise. Naopak zlyhanie requestu bez logu alebo metric counteru vytvára observability gap.

### Log volume a sampling

Kontroluj:

- log level per environment,
- duplicate stack traces,
- request/response body logging,
- retry loops,
- high-frequency successful events,
- retention podľa value,
- sensitive fields,
- dynamic sampling.

Sampling úspešných low-value logs môže byť prijateľný. Security, audit a critical failure evidence nemusí byť vhodné zahadzovať rovnakým pravidlom.

## 5. Distributed traces

Trace reprezentuje cestu jednej operácie cez services, processes a async boundaries.

Trace sa skladá zo spans.

Span typicky obsahuje:

- trace ID,
- span ID,
- parent span ID alebo links,
- operation name,
- start a end time,
- status,
- attributes,
- span events,
- resource a instrumentation scope.

### Typické otázky

- Ktorá dependency vytvorila latency?
- Kde request zlyhal?
- Aký fan-out alebo retry pattern vznikol?
- Ktorá service volala ktorú?
- Kde sa prerušila context propagation?
- Ako sa líši úspešná a chybná request path?

### Parent-child a links

Synchronous call často používa parent-child relation.

Async, queue alebo batch systém môže potrebovať span links, pretože:

- jeden producer event spustí viac consumers,
- jeden batch obsahuje viac pôvodných messages,
- operation nemá jednoduchého jediného parenta,
- processing nastane výrazne neskôr.

Vynútenie nepravdivého stromu môže skryť skutočnú causalitu.

### Sampling

Trace sampling kontroluje volume a cost.

Modely:

- head sampling — rozhodnutie pri začiatku trace-u,
- tail sampling — rozhodnutie po zhromaždení väčšej časti trace-u,
- probabilistic sampling,
- rule-based sampling,
- always keep errors alebo high-latency traces.

Tail sampling môže zachovať zaujímavé failures, ale vyžaduje stateful processing, buffer capacity a failure model collectora.

Sampling decision musí byť propagované konzistentne. Inak vzniknú fragmentované traces.

## 6. Events

Event je časovo označený record významnej zmeny alebo occurrence.

Príklady:

- deployment začal alebo skončil,
- autoscaling zmenil desired capacity,
- leader election prebehla,
- certificate sa obnovil,
- feature flag sa zmenil,
- backup alebo restore job zlyhal,
- Kubernetes Pod bol evicted,
- incident bol deklarovaný.

V OpenTelemetry data modeli sa event smeruje k pomenovanému a štruktúrovanému typu log recordu. Praktické platformy však môžu označovať ako event aj cloud control-plane records, Kubernetes Events alebo deployment markers.

Preto vždy definuj:

- producer,
- event schema,
- delivery semantics,
- ordering,
- deduplication identity,
- retention,
- correlation fields,
- či je event audit evidence alebo iba operational hint.

## 7. Span events oproti samostatným events

Span event je bodová udalosť v kontexte konkrétneho span-u.

Príklady:

- exception,
- cache miss,
- retry attempt,
- lock acquisition,
- message acknowledgement.

Samostatný event je vhodnejší, keď:

- nemá jeden prirodzený request context,
- musí existovať aj bez trace backendu,
- má business alebo audit lifecycle,
- potrebuje vlastnú retention a delivery semantics.

## 8. Audit records

Audit record sa zameriava na actor a control-plane operáciu.

Mal by odpovedať:

- kto,
- kedy,
- odkiaľ,
- voči čomu,
- akú action,
- s akým request contextom,
- s akým výsledkom,
- cez akú delegated identity alebo session.

Audit trail má odlišné požiadavky než application log:

- vyššia integrita,
- dlhšia alebo regulovaná retention,
- obmedzený write access,
- centralizácia mimo workload blast radiusu,
- identity resolution,
- tamper evidence.

## 9. Profiles

Profile zachytáva spotrebu resources na úrovni code paths.

Príklady:

- CPU samples,
- memory allocations,
- lock contention,
- goroutine/thread state,
- off-CPU wait,
- garbage collection.

Profiles odpovedajú na otázku „ktorý kód spotreboval resource“, ktorú metric CPU utilization ani trace duration nemusia samy vysvetliť.

Profiles sú vznikajúca observability vrstva a ich presná OpenTelemetry podpora sa má pri implementácii overiť podľa aktuálnej specification a language SDK statusu.

## 10. Porovnanie signals

| Signal | Silná stránka | Slabá stránka | Typický operational use |
|---|---|---|---|
| Metrics | agregácia, trends, alerting | málo per-request detailu | SLO, saturation, capacity |
| Logs | detail eventu a state-u | volume, parsing, noise | exception a decision diagnostics |
| Traces | causal request path | sampling a storage cost | distributed latency a dependency failures |
| Events | významná zmena v čase | nejednotné schemas | deployment, lifecycle a change correlation |
| Audit records | actor a control-plane action | nie sú performance signal | security a change investigation |
| Profiles | code-level resource usage | overhead a interpretácia | CPU, memory a contention diagnosis |

## 11. Correlation

Signals musia zdieľať stabilný context.

Odporúčané fields:

- `service.name`,
- environment,
- service version alebo deployment revision,
- Region, zone, cluster, namespace,
- trace ID a span ID,
- request alebo correlation ID,
- tenant alebo business key iba v bezpečnej bounded forme,
- workload/resource identity,
- change/deployment ID.

Incident workflow:

```text
SLO alebo metric alert
→ relevantný time window a deployment marker
→ exemplár alebo trace ID
→ trace path
→ konkrétny span a dependency
→ korelované structured logs
→ audit/change event
→ profile pri resource bottlenecku
```

Bez correlation sa responder spolieha na časové odhady a manuálne matching patterns.

## 12. Derived signals

Z jedného signalu možno odvodiť iný:

- metrics z logs,
- metrics z spans,
- service graph z traces,
- events z audit records,
- alerts z metric alebo log query,
- profiles korelované s spans.

Derived signal musí mať jasný source-of-truth contract.

Príklad: error rate odvodený iba zo sampled traces nemusí reprezentovať všetky requesty. Na SLO môže byť vhodnejší request counter z application alebo edge vrstvy.

## 13. Signal selection podľa otázky

### „Je služba dostupná?“

- black-box success/latency metric,
- request rate/error rate,
- SLO burn,
- dependency health.

### „Prečo je request pomalý?“

- latency histogram,
- distributed trace,
- downstream spans,
- correlated logs,
- profile pri CPU alebo lock probléme.

### „Kto zmenil konfiguráciu?“

- audit record,
- deployment event,
- Git/IaC revision,
- controller reconciliation log.

### „Prečo rastie memory?“

- memory metrics,
- allocation/heap profile,
- GC metrics,
- deployment correlation,
- workload-specific logs.

## 14. Signal quality

Každý signal hodnoti podľa:

- correctness,
- completeness,
- freshness,
- context,
- correlation,
- bounded cardinality,
- schema stability,
- delivery reliability,
- retention,
- security,
- cost,
- ownera.

Signal bez ownera a decision use case-u sa často stane drahým neudržiavaným dátovým tokom.

## 15. Troubleshooting chýbajúceho signalu

```text
producer skutočne vykonal operáciu?
→ instrumentation vytvorila record?
→ sampling/filtering ho zachovali?
→ agent/collector ho prijal?
→ processor ho nezahodil alebo nezmenil?
→ exporter ho odoslal?
→ network/auth/TLS fungujú?
→ backend ho ingestoval a indexoval?
→ správny tenant/time range/query?
→ retention alebo compaction?
```

Zachovaj:

- sample timestamp,
- trace/request ID,
- producer logs,
- collector self-telemetry,
- exporter errors,
- backend ingestion metrics,
- exact query a time zone.

## 16. Anti-patterny

### Všetko ako log

SLO a trends sa počítajú draho a neefektívne z textových records.

### Všetko ako metric

Per-request causal detail a error context sa stráca.

### Trace ID ako metric label

Vytvára prakticky neobmedzenú cardinality.

### Average latency bez distribution

Maskuje tail latency.

### Events bez stabilnej schema

Nie je možné spoľahlivo filtrovať, deduplikovať ani automatizovať reakciu.

### Audit a application logs v rovnakom blast radiuse

Compromise workloadu môže poškodiť aj evidence.

### Correlation iba podľa timestampu

Clock skew, queues a retry patterns vedú k nesprávnym záverom.

## 17. Kontrolné otázky

1. Ktoré otázky najlepšie riešia metrics, logs a traces?
2. Prečo average latency nestačí?
3. Aký je rozdiel medzi eventom a audit recordom?
4. Kedy použiť span event a kedy samostatný event?
5. Ako head a tail sampling menia trace coverage?
6. Prečo trace ID nepatrí do metric labels?
7. Čo musí obsahovať structured log schema?
8. Ako koreluješ metric alert s konkrétnym requestom?
9. Kedy potrebuješ profile?
10. Ako diagnostikuješ chýbajúci telemetry record?

## Glossary impact

Relevantné pojmy: metric, counter, gauge, histogram, distribution, temporality, structured log, severity, distributed trace, span, span link, span event, head sampling, tail sampling, event, audit record, profile, correlation, derived signal a signal quality.

## Primárne zdroje

- [OpenTelemetry signals](https://opentelemetry.io/docs/concepts/signals/)
- [OpenTelemetry metrics](https://opentelemetry.io/docs/concepts/signals/metrics/)
- [OpenTelemetry observability primer](https://opentelemetry.io/docs/concepts/observability-primer/)
- [OpenTelemetry logging specification](https://opentelemetry.io/docs/specs/otel/logs/)
- [OpenTelemetry profiles](https://opentelemetry.io/docs/concepts/signals/profiles/)
- [Prometheus instrumentation practices](https://prometheus.io/docs/practices/instrumentation/)
