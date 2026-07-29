# Metrics, logs, traces a events

Metrics, logs, traces, events, audit records a profiles nie sú rôzne vizualizácie toho istého faktu. Každý signal vzniká inou transformáciou system occurrence-u: niečo agreguje, niečo zachová detail, niečo modeluje causal path a niečo chráni actor/action evidence. Signal je užitočný iba vtedy, keď poznáme jeho source observation, schema, coverage, sampling a rozhodnutie, ktoré má podporiť.

## 1. Dominantný lifecycle

```text
system alebo business occurrence
→ observation point
→ telemetry record generation
→ signal-specific model a kompresia reality
→ resource, operation, context a schema identity
→ delivery, processing a storage
→ query alebo derived signal
→ evidence quality verdict
→ operational decision
→ outcome validation
```

Tento model oddeľuje:

```text
udalosť v systéme
≠ telemetry record o udalosti
≠ uložený signal
≠ query výsledok
≠ pravdivý operational verdict
```

Request môže zlyhať bez logu. Log môže existovať, ale nebyť doručený. Trace môže byť doručený, ale sampled subset nereprezentuje všetky requests. Dashboard môže správne zobraziť query, ktorá používa nesprávny denominator.

## 2. Exact signal subject

Pri každom signale urč:

```text
signal subject: SIG-PAY-43
observed operation: settle(payment_id)
measurement boundary: client / service / dependency / final business completion
producer: payments-api, provider-adapter, ledger-writer alebo platform
release generation: 7.19.0
instrumentation generation: OTEL-PAY-12
resource identity: service, environment, Region, AZ, version
schema generation: name, unit, attributes, event fields
coverage: all operations alebo sampled/filterovaný subset
pipeline generation: collector a backend route
retention a query cut-off
```

Bez measurement boundary nie je možné bezpečne porovnať dva signals. `provider request errors` a `failed logical settlements` môžu mať odlišný počet aj semantics, pretože jeden settlement vykonáva viac attempts.

## 3. Metrics: agregovaná odpoveď o rozsahu a trende

Metric stream komprimuje veľa observations do time series. Je vhodný na rate, ratio, distribution, utilization, saturation, SLO a capacity. Cena tejto efektívnosti je strata per-operation detailu.

### Counter

Counter reprezentuje kumulatívny počet udalostí alebo množstvo práce. Reštart produceru ho môže resetnúť, preto sa operational význam typicky získava cez rate alebo increase.

```text
settlement_logical_operations_total
settlement_failures_total
provider_attempts_total
provider_attempt_failures_total
```

Tieto štyri counters nesmú byť zlúčené, pretože logical operations a attempts majú rozdielny denominator contract.

### Gauge

Gauge môže rásť aj klesať a reprezentuje current observation, napríklad queue depth, in-flight requests, active connections alebo loaded config generation count. Krátky spike sa môže stratiť medzi observations; gauge tiež nemusí byť autoritatívny pre historický total.

### Histogram alebo distribution

Duration, size a queue wait sú distributions. Average odstráni tvar rozdelenia a môže skryť tail latency alebo dve odlišné populations. Histogram alebo iný distribution model umožní vyhodnotiť threshold compliance a percentiles podľa backend semantics.

### Metric identity

Time series je určená metric name a úplnou množinou dimensions. Labels majú byť bounded a decision-relevant:

```text
service.name
operation
result.class
release.channel
deployment.environment.name
cloud.region
cloud.availability_zone
```

Raw payment ID, request ID, trace ID, unbounded URL alebo exception message vytvárajú prakticky neobmedzenú cardinality. Tento detail patrí skôr do protected logs alebo sampled traces.

### Temporality a aggregation

Cumulative a delta temporality určujú, kto drží aggregation state a čo export predstavuje. Pri konverzii, reštarte, duplicate delivery alebo backend migration musí byť jasné, či sa hodnoty sčítavajú, resetujú alebo deduplikujú. Unit a temporality sú súčasťou schema contractu, nie iba metadata.

## 4. Logs a structured events: detail state transitionu

Log record zachováva detail konkrétneho occurrence-u alebo diagnostického rozhodnutia. Production log má stabilné typed fields, aby query nebola závislá od parsovania meniaceho sa textu.

Príklad:

```json
{
  "timestamp": "2026-07-29T09:20:14.183Z",
  "observed_timestamp": "2026-07-29T09:20:14.201Z",
  "severity": "ERROR",
  "event.name": "payment.provider.tls_failed",
  "service.name": "provider-adapter",
  "service.version": "7.19.0",
  "deployment.environment.name": "production",
  "cloud.availability_zone": "eu-central-1b",
  "trace_id": "opaque-trace-id",
  "span_id": "opaque-span-id",
  "logical_operation_id": "opaque-settlement-id",
  "config.generation": "PROVIDER-CFG-34",
  "error.type": "TlsHandshakeError",
  "error.code": "UNKNOWN_CA",
  "duration_ms": 47
}
```

`Timestamp` opisuje čas occurrence-u podľa source clocku. `ObservedTimestamp` môže zachytiť čas, keď collection system record pozoroval. Rozdiel pomáha pri delayed delivery a clock-quality analýze.

OpenTelemetry log data model je stable a umožňuje trace/span correlation. V current modeli je pomenovaný structured event reprezentovaný log recordom s event name. Platformové „events“ však môžu mať vlastnú delivery a retention semantics, preto pojem event vždy viaž na konkrétny producer a schema.

Severity opisuje operational význam occurrence-u. Každý retry attempt logovaný ako `ERROR` môže vytvoriť noise; naopak final business failure bez structured recordu vytvorí diagnostickú medzeru. Message môže zostať human-readable doplnkom, ale nesmie byť jediným contractom.

## 5. Distributed traces: causal path jednej operácie

Trace modeluje execution path jednej logical operation cez synchronous aj asynchronous boundaries. Span reprezentuje konkrétnu operation a nesie timing, status, attributes, resource a instrumentation scope.

```text
client settlement
→ payments-api acceptance span
→ queue publish span
→ consumer process span linked k producer contextu
→ provider authorization attempts
→ ledger commit
→ completion event
```

Parent-child relation je vhodná pre priame call stack-like väzby. Async fan-out, batching alebo redelivery môže potrebovať span links. Vynútenie falošného jediného parenta skryje causalitu medzi producer message a neskorším consumer processingom.

Span event zachytáva bodový occurrence v rámci span-u, napríklad retry, exception, lock wait alebo acknowledgement. Samostatný structured event je vhodnejší, keď potrebuje vlastný lifecycle, retention, delivery alebo existenciu nezávislú od zachovania trace-u.

### Sampling contract

Head sampling rozhoduje pri začiatku trace-u, keď ešte nepozná final outcome. Tail sampling rozhoduje po zhromaždení väčšej časti trace-u a môže zachovať errors alebo high-latency paths. Tail sampling však potrebuje state, trace affinity, buffer capacity a explicitný failure model.

Sampling mení coverage. Sampled traces preto nemajú automaticky nahradiť unsampled request counters pre SLO denominator. Sampling decision a trace context sa musia propagovať konzistentne, inak vzniknú fragmented traces.

## 6. Events: významná zmena v čase

Operational event opisuje zmenu, ktorá poskytuje context pre behavior:

- deployment alebo rollback;
- configuration generation transition;
- scaling alebo failover;
- feature-flag change;
- certificate rotation;
- queue redrive;
- incident declaration.

Event contract potrebuje producer identity, occurred/observed time, schema version, deduplication key, ordering expectations, delivery semantics, retention a correlation fields. „Deployment marker“ bez release ID alebo affected scope je slabý hint.

Events sú často mostom medzi symptomom a zmenou. Neznamená to, že každá časová korelácia je príčina. Event zúži hypotézu; mechanismus sa musí preukázať ďalším evidence pathom.

## 7. Audit records: actor, request a control-plane action

Audit record odpovedá na otázky kto, cez akú session, odkiaľ, čo zmenil, voči akému resource-u a s akým API výsledkom. Má inú integritu a access boundary než application diagnostics.

Audit success často dokazuje prijatie control-plane requestu, nie úplnú runtime realizáciu. Napríklad úspešná config update action nepreukazuje, že všetky tasks načítali novú generation.

Pre kritické audit evidence používaj centralizáciu, write protection, identity resolution, dlhšiu retention a tamper-evident model mimo workload blast radiusu.

## 8. Profiles: code-level resource attribution

Profile odpovedá na otázku, ktorý code path spotrebúva CPU, alokuje memory alebo čaká na lock/I/O. Metric môže ukázať 95 % CPU a trace pomalý span, ale profile lokalizuje konkrétnu funkciu alebo stack.

OpenTelemetry Profiles specification je aktuálne Alpha. Pri produkčnom návrhu preto over language agent, transport, backend, schema a overhead maturity; nepovažuj všeobecnú existenciu specification za garanciu rovnakých capabilities vo všetkých SDKs.

## 9. Correlation contract

Signals majú zdieľať minimálne sufficient identity bez kopírovania high-cardinality detailu do každej vrstvy.

```text
metric alert podľa service/operation/AZ/version
→ exemplar alebo bounded time/cohort filter
→ trace ID
→ failing span a dependency
→ logs s trace/span/logical-operation ID
→ deployment/config event
→ audit actor
→ profile pri resource mechanism-e
```

Resource identity opisuje observed entity, napríklad logical service, process, Pod alebo cloud resource. Instrumentation scope opisuje library alebo component, ktorý record vytvoril. Operation attributes opisujú konkrétny occurrence. Ich zamenenie vedie k nestabilným service names a neinterpretovateľným queries.

## 10. Derived signals a source-of-truth contract

Z logs alebo spans možno odvodiť metrics, z traces service graph a z audit recordov change events. Derived signal dedí coverage, sampling, delay a chyby source signalu.

Príklad:

```text
error ratio zo sampled traces
≠ automaticky error ratio všetkých valid requests
```

Pred použitím derived signalu pre SLO alebo page urč:

- autoritatívny source occurrence;
- sampling a filtering;
- duplicate a late-data behavior;
- derivation version;
- refresh/ingestion latency;
- comparison proti nezávislému oracle-u.

## 11. Signal quality verdict

Signal hodnoti podľa correctness, completeness, freshness, contextu, correlation, bounded cardinality, schema stability, delivery reliability, retention, security, cost a ownershipu.

Praktický verdict môže byť:

```text
complete and authoritative
partial but useful
stale
sampled and non-authoritative for denominator
missing due to pipeline failure
unknown coverage
```

Takéto pomenovanie je presnejšie než univerzálne „data available“.

## 12. Worked failure: sampled trace metric predstiera recovery

### Exact subject

```text
SIG-PAY-43
operation: settle(payment_id)
release: 7.19.0
window: 09:12–09:22 UTC
logical operations: 20,000
instrumentation generation: OTEL-PAY-12
trace policy: tail sampling
metric source A: unsampled application counters
metric source B: derived metric zo zachovaných traces
```

### Symptom

Authoritative counters ukazujú `4.8 %` failed logical settlements. Dashboard odvodený zo traces ukazuje iba `0.4 %` errors a po niekoľkých minútach zdanlivé zlepšenie.

### Competing hypotheses

1. application counter duplicitne počíta retries;
2. trace-derived query používa nesprávny denominator;
3. tail sampler zahadzuje fast failures;
4. traces strácajú status na provider span-e;
5. metric pipeline má duplicate samples;
6. service sa skutočne zotavila a counter je stale.

### Discriminating evidence

```text
logical-operation counter source
→ trace keep/drop counters podľa policy reason
→ raw provider-adapter logs
→ sampled a non-sampled request cohort test
→ span status a event fields
→ collector tail-sampling config generation
→ backend ingestion timestamps
```

Zistenia:

- application counter má jeden increment pri final logical outcome a retries počíta osobitne;
- TLS handshake failures končia rýchlo;
- auto-instrumentation vytvorí exception event, ale custom wrapper nenastaví final span status na error;
- tail policy zachováva explicit errors a high latency, takže fast spans s unset statusom väčšinou dropne;
- derived trace metric preto reprezentuje selected subset, nie všetky settlements;
- logs a unsampled counters zostávajú konzistentné s reálnym `4.8 %` failure rate.

Root cause nie je uzdravenie služby. Je to kombinácia incomplete span error semantics a nesprávneho source-of-truth rozhodnutia pre SLO dashboard.

### Containment

- odstrániť trace-derived ratio z paging a SLO verdictu;
- označiť panel ako sampled diagnostic signal;
- zachovať collector policy, keep/drop counters a raw example traces;
- nevypnúť sampling plošne počas incidentu bez capacity analýzy;
- používať unsampled logical-operation counters pre aktuálny impact.

### Recovery

1. explicitne nastaviť span status podľa final provider operation contractu;
2. pridať bounded `error.type` a structured event;
3. vytvoriť canary pre fast TLS failure aj slow failure;
4. overiť tail policy keep reason a trace completeness;
5. porovnať trace-derived diagnostic ratio s authoritative counterom;
6. versionovať derivation query a dashboard.

### Acceptance verdict

- logical-operation counter a business reconciliation sú zhodné;
- fast aj slow failures majú správny span status;
- sampled trace coverage je viditeľná a nepoužíva sa ako úplný denominator;
- trace, log, deployment event a audit record sa korelujú;
- forbidden duplicate counting retries ako logical failures nevzniká;
- no-data alebo collector drop stav nevytvára false-green panel.

## 13. Troubleshooting chýbajúceho alebo sporného signalu

```text
occurrence skutočne nastal?
→ správny observation point?
→ producer vytvoril record?
→ schema/resource/operation identity?
→ sampling alebo filtering?
→ queue, exporter, network, auth a TLS?
→ backend ingestion a indexing?
→ tenant/time range/time zone?
→ query a derivation generation?
→ source coverage postačuje pre daný verdict?
```

Zachovaj sample operation ID, occurred a observed timestamps, producer logs, collector self-telemetry, exporter errors, backend ingestion metrics, exact query a source generation.

## 14. Anti-patterny

### Všetko ako log

Agregované SLO a capacity queries sú drahé a závislé od parsing/schema stability.

### Všetko ako metric

Per-operation causal detail a error context sa stratia.

### Trace ID ako metric label

Vytvára unbounded series cardinality.

### Sampled trace metric ako úplný SLO denominator

Coverage závisí od sampling policy a instrumentation semantics.

### Average latency

Maskuje tail a rozdiel medzi successful a failed paths.

### Event bez identity a schema

Nie je spoľahlivo queryable, deduplicable ani korelovateľný.

### Audit a application diagnostics v rovnakom blast radiuse

Workload compromise môže poškodiť incident evidence.

### Resource identity zamenená za process instance

Logical service sa rozpadne na ephemeral Pod alebo host names.

## 15. Kontrolné otázky

1. Aký je rozdiel medzi system occurrence, telemetry record a query verdict?
2. Čo musí obsahovať exact signal subject?
3. Prečo logical-operation a attempt counters potrebujú samostatný contract?
4. Ako sa líši resource identity, instrumentation scope a operation attributes?
5. Kedy použiť span event a kedy samostatný structured event?
6. Prečo sampled traces nemusia byť vhodný SLO denominator?
7. Čo audit API success nepreukazuje o runtime stave?
8. Aký je aktuálny maturity status OpenTelemetry Profiles specification?
9. Ako hodnotíš signal quality?
10. Ako bol false-green trace dashboard v `SIG-PAY-43` opravený?

## Glossary impact

Relevantné pojmy: signal subject, occurrence-to-record boundary, measurement boundary, metric stream identity, logical-operation counter, attempt counter, occurred timestamp, observed timestamp, named telemetry event, sampled coverage, derived-signal authority, signal-quality verdict, resource-versus-scope identity a profile maturity boundary.

## Primárne zdroje

- [OpenTelemetry signals](https://opentelemetry.io/docs/concepts/signals/)
- [OpenTelemetry metrics data model](https://opentelemetry.io/docs/specs/otel/metrics/data-model/)
- [OpenTelemetry logs data model](https://opentelemetry.io/docs/specs/otel/logs/data-model/)
- [OpenTelemetry Profiles specification](https://opentelemetry.io/docs/specs/otel/profiles/)
- [Prometheus instrumentation practices](https://prometheus.io/docs/practices/instrumentation/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Monitoring vs. observability](monitoring-vs-observability.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Instrumentation a telemetry →](instrumentation-telemetry.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
