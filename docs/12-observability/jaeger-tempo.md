# Jaeger a Tempo

Jaeger a Grafana Tempo sú distributed tracing backends. Prijímajú spans, ukladajú trace data a poskytujú lookup, search a visualization nad distributed operations. Backend však vidí iba telemetry, ktorá bola vytvorená, správne propagovaná, zachovaná sampling policy, prijatá ingest pathom a ešte existuje v queryovateľnej storage generation.

## 1. Dominantný mentálny model

```text
business alebo operational operation
→ exact trace subject a expected span graph
→ context propagation
→ span generation a resource identity
→ sampling decision
→ Collector processing a export
→ backend ingest acknowledgement
→ recent-data state
→ durable historical storage generation
→ exact trace lookup alebo attribute search
→ evidence-completeness verdict
→ operational decision a recovery validation
```

Kritické rozlíšenie:

```text
operation prebehla
≠ spans vznikli
≠ trace je kompletný
≠ backend ingest prijal data
≠ trace je durable v historical storage
≠ search ho dokáže nájsť
```

Tracing je detailný diagnostický evidence systém, nie autoritatívny request counter. Sampling, broken propagation a storage loss menia jeho coverage.

## 2. Exact tracing subject

Pre incident alebo migration zaznamenaj:

```text
Trace subject ID:
Business operation a caller:
Trace ID alebo expected trace population:
Service/release/cohort:
Instrumentation a semantic-convention generation:
Propagation format:
Sampling policy generation:
Collector topology/config generation:
Backend product/version/deployment mode:
Tenant:
Recent-data generation:
Historical storage/index/block generation:
Retention generation:
Query type, time range a cut-off:
```

Trace ID bez service, tenant, sampling, Collector a storage generation nestačí. Rovnaký business operation môže byť v rôznych generations reprezentovaný odlišným alebo neúplným span graphom.

## 3. Trace continuity a span graph

Span typicky obsahuje:

- trace ID a span ID;
- parent span ID alebo links;
- stable operation name a kind;
- start/end time a status;
- resource a instrumentation-scope identity;
- bounded attributes a events.

Context sa musí preniesť cez HTTP, gRPC, message headers, queues, async callbacks, batches a scheduled jobs. Backend nevie spätne opraviť parent ID, ktorý producer nevytvoril.

Broken graph môže vzniknúť takto:

```text
caller injectne trace context
→ proxy header zachová alebo odstráni
→ consumer context extrahuje alebo vytvorí nový root
→ async worker current context zachová alebo stratí
→ child spans sa pripoja, linknú alebo osirejú
```

Viac roots alebo missing child span je najprv propagation/instrumentation hypotéza, nie automaticky storage defect.

## 4. Jaeger v2

Jaeger v2 je postavený nad OpenTelemetry Collector frameworkom a jeden binary môže vykonávať rôzne roles:

- `collector` prijíma traces a zapisuje ich do storage;
- `query` poskytuje query APIs a UI;
- `ingester` číta spans z Kafka a zapisuje ich do storage;
- `all-in-one` kombinuje collector a query;
- pre bežný multi-signal edge model je preferovaný štandardný OpenTelemetry Collector namiesto samostatnej Jaeger agent role.

Dve hlavné production topológie:

```text
Direct-to-storage
applications/OTel Collectors
→ Jaeger collector
→ external storage
→ Jaeger query
```

```text
Kafka-buffered
Jaeger collector
→ Kafka
→ Jaeger ingester
→ external storage
→ Jaeger query
```

Direct model má menej components, ale storage musí absorbovať peak writes. Kafka model pridáva durable buffer a replay, ale aj partitioning, lag, retention a duplicate-processing boundaries.

Jaeger `all-in-one` s in-memory storage je development/test model. Process health alebo funkčný UI nepreukazuje production retention ani independent failure domain.

## 5. Tempo 3.0

Tempo 3.0 rozlišuje monolithic a microservices deployment.

### Microservices write path

```text
OTLP spans
→ distributor validation
→ trace-ID partitioning
→ Kafka-compatible durable queue
→ acknowledgement producerovi
→ live-store pre recent queries
→ block-builder
→ Parquet blocks
→ object storage
```

Distributor potvrdí write po Kafka acknowledgement-e. To preukazuje durable prijatie do queue generation, nie vytvorenie historical blocku.

Block-builder:

1. číta pridelené Kafka partitions;
2. skladá spans do blocks;
3. zapisuje Parquet blocks do object storage;
4. až po úspešnom flushi commitne consumer progress.

Live-store má samostatný consumer progress a obsluhuje recent data. Preto môže recent lookup fungovať, zatiaľ čo historical publication zaostáva.

### Monolithic write path

```text
distributor
→ in-process live-store
→ local WAL/temporary blocks
→ object storage
```

Monolithic mode nepotrebuje Kafka, ale nemá rovnaké independent scaling a durable-queue boundaries ako microservices model.

### Read a maintenance path

```text
query frontend
→ recent jobs do live-stores
→ historical jobs do object storage
→ queriers
→ merge results
```

Backend scheduler a workers vykonávajú compaction, retention a blocklist maintenance. Scheduler je coordination identity; workers sú škálovateľní executors. Pri migration nesmú starý compactor a nový scheduler/worker súčasne meniť tie isté blocks.

## 6. Sampling a trace completeness

### Head sampling

Rozhodnutie vzniká na začiatku trace-u. Je lacné a predvídateľné, ale nepozná budúci error ani tail latency.

### Tail sampling

Rozhodnutie vzniká po zhromaždení spans a môže zachovať errors, high-latency traces alebo vybrané cohorts. Vyžaduje:

- trace-ID-aware routing;
- state a memory;
- decision wait;
- late-span policy;
- incomplete-trace classification;
- per-policy keep/drop evidence.

Random round-robin pred stateful samplerom môže rozdeliť spans jedného trace-u medzi replicas. Každý sampler potom urobí rozhodnutie nad neúplným subjectom.

Sampling policy musí byť versionovaná. `1 % sampled` nie je iba cost knob; mení incident coverage, service graph, span metrics a apparent error rate.

## 7. Lookup, search a derived views

Exact trace-ID lookup a broad attribute search sú rozdielne workloads.

```text
exact trace ID
→ bounded object/index lookup
```

```text
service + operation + attributes + time range
→ index/Parquet scan
→ query sharding a merge
```

Tempo používa TraceQL pre attribute a structural search. Jaeger search semantics závisia od použitej storage generation.

Derived views:

- span metrics;
- service graph;
- trace-to-logs links;
- exemplars z metrics na trace;
- dependency performance views.

Sú ovplyvnené samplingom, propagation a missing spans. Service graph nie je autoritatívny architecture inventory a sampled span count nie je exact request count.

## 8. Worked failure: acknowledged traces bez historical evidence

### Subject

```text
Incident: TRACE-PAY-46
Operation: enterprise final settlement
Release: 7.23.0
Region: eu-central-1
Tempo: 3.0 microservices
Tenant: payments-prod
Kafka topic generation: TEMPO-KAFKA-31
Partitions: 12
Block-builder generation: BB-GEN-18
Kafka retention: 2 h
Tempo trace retention: 14 d
Affected window: 01:10–04:05 UTC
```

### Symptóm

On-call otvorí trace počas incidentu a exact lookup funguje. O štyri hodiny neskôr už trace ani susedné traces z affected window nie sú v historical search. Distributor, OTLP clients aj Tempo API hlásili úspešné requests.

### Competing hypotheses

1. application trace nebola sampled;
2. propagation vytvorila nový trace ID;
3. Collector filter trace dropol;
4. tenant header pri query je nesprávny;
5. live-store mal trace, ale block-builder ju nepublikoval;
6. object-store lifecycle ju predčasne zmazal;
7. TraceQL selector alebo time range je chybný;
8. block-builder lag prekročil Kafka replay window.

### Discriminating evidence

```text
SDK sampled flag: true
Collector accepted/exported spans: present
Tempo distributor acknowledgement: present
live-store lookup počas incidentu: present
block-builder consumer lag: 3 h 11 min
Kafka retention: 2 h
block-builder replica 7 unavailable: 2 h 46 min
historical Parquet blocks pre partition 7/window: absent
object-store delete events: none
other partitions v rovnakom čase: historical traces present
```

Pri rollout-e sa Kafka rozšírila na 12 partitions, ale block-builder StatefulSet zostal na 11 replicas. Partition 7 po reschedule nemala dostatočnú processing capacity, lag prekročil retention a Kafka odstránila ešte nespracované records.

Mechanizmus:

```text
distributor zapíše spans do Kafka
→ Kafka potvrdí durable queue write
→ live-store ich spotrebuje a recent lookup funguje
→ block-builder zaostáva
→ lag prekročí Kafka retention
→ records zmiznú pred block publication
→ historical object storage nemá trace
→ neskorší lookup je permanentne neúplný
```

### Containment

- zastaviť ďalšie partition/topology changes;
- zachovať Kafka offsets, lag metrics, partition ownership, Tempo config a object inventory;
- zvýšiť Kafka retention skôr než sa stratí ďalší backlog, ak disk/capacity dovolí;
- obnoviť block-builder consumer capacity pre všetky partitions;
- neoznačiť missing historical query za „trace sa nestala“;
- použiť logs, metrics a surviving traces na incident reconstruction.

### Authoritative recovery

1. zosúladiť Kafka partitions, block-builder a live-store ownership;
2. nastaviť retention headroom nad maximum recovery/replay window;
3. alertovať na lag age, nie iba record count;
4. canary-nuť jednu partition a preukázať recent aj historical transition;
5. overiť object-store block publication a offset commit;
6. vykonať controlled consumer restart a replay;
7. označiť neobnoviteľné obdobie ako explicitný trace-evidence loss window.

### Acceptance verdict

Recovery je prijatá, keď:

- synthetic multi-service trace je dostupná recent aj po historical cutover-e;
- všetky partitions majú consumer ownera a bounded lag;
- Kafka retention pokrýva failure a restart objective;
- block, object a committed offset patria k rovnakej generation;
- neighboring tenant a partition neregresujú;
- forbidden cross-tenant lookup zlyhá;
- sampled trace count sa nepoužíva ako exact settlement denominator;
- druhý controlled restart zachová trace availability.

## 9. Jaeger alebo Tempo

Jaeger je vhodný, keď je dôležitý Jaeger UI/ecosystem, remote sampling alebo existujúca supported external-storage expertíza. Tempo je vhodný pri object-storage-first modeli, Grafana integrácii, TraceQL a oddelenom recent/historical query path-e.

Výber musí porovnať:

- exact lookup a search patterns;
- ingest durability a outage window;
- sampling control;
- storage/index cost;
- tenant a authorization model;
- retention/deletion;
- upgrade a migration path;
- backup/recovery evidence.

Názov backendu nenahrádza end-to-end trace contract.

## 10. Troubleshooting model

### Trace sa nenájde

```text
operation a expected trace ID
→ sampled flag a span generation
→ propagation a resource identity
→ SDK/Collector accepted/dropped counters
→ sampling/filter policy
→ exporter acknowledgement
→ backend tenant
→ recent path
→ historical storage/index/block
→ query time range a selector
```

### Broken trace

```text
expected span graph
→ inject/extract boundaries
→ async/message propagation
→ parent/link semantics
→ duplicate instrumentation
→ sampling consistency
→ late spans a clock skew
```

### Recent áno, historical nie

```text
live-store visibility
→ Kafka/block-builder alebo Jaeger storage ingest
→ consumer lag a replay window
→ block/index publication
→ object/external storage
→ compaction/retention
```

### Historical áno, recent nie

```text
current distributor/collector
→ live-store alebo storage refresh path
→ partition/ring ownership
→ current tenant/limits
→ recent-query routing
```

## 11. Anti-patterny

### Backend acknowledgement ako retention proof

Queue alebo collector acknowledgement nemusí znamenať historical publication.

### Tail sampling bez trace affinity

Rozdelí trace subject medzi stateful samplery.

### Trace-derived metrics ako exact SLI

Sampling a missing spans menia numerator aj denominator.

### Raw URL, SQL alebo customer ID ako span name

Vytvára cardinality a privacy risk.

### In-memory all-in-one ako production HA

Nemá independent data ani recovery boundary.

### Recent lookup ako historical canary

Neoverí block/index publication, object storage ani retention.

## 12. Kontrolné otázky

1. Čo tvorí exact trace subject?
2. Prečo operation, spans, complete trace a searchable trace nie sú totožné stavy?
3. Ako context propagation vytvára span graph?
4. Ako sa líši Jaeger direct-to-storage a Kafka-buffered model?
5. Kedy Tempo 3.0 potvrdzuje ingest write?
6. Ako sa líši recent a historical Tempo path?
7. Prečo block-builder lag musí byť porovnaný s Kafka retention?
8. Prečo tail sampling potrebuje trace-ID-aware routing?
9. Ako sampling mení service graph a span metrics?
10. Prečo exact lookup a broad search potrebujú rozdielne dôkazy?
11. Ako overíš trace retention end-to-end?
12. Kedy zvoliť Jaeger a kedy Tempo?

## Glossary impact

Relevantné pojmy: trace-evidence subject, expected span graph, propagation generation, sampling-policy generation, trace-affinity contract, ingest acknowledgement, recent-trace path, historical-trace path, Kafka trace replay window, block-publication generation, trace-evidence loss window, exact trace lookup, trace-search generation a tracing-backend acceptance verdict.

## Primárne zdroje

- [Jaeger v2 architecture](https://www.jaegertracing.io/docs/2.20/architecture/)
- [Jaeger deployment](https://www.jaegertracing.io/docs/2.20/deployment/)
- [Jaeger sampling](https://www.jaegertracing.io/docs/2.20/architecture/sampling/)
- [Tempo architecture](https://grafana.com/docs/tempo/latest/introduction/architecture/)
- [Tempo 3.0 migration](https://grafana.com/docs/tempo/latest/set-up-for-tracing/setup-tempo/migrate-to-3/)
- [Tempo Kafka component](https://grafana.com/docs/tempo/latest/reference-tempo-architecture/components/kafka/)
- [Tempo compaction](https://grafana.com/docs/tempo/latest/reference-tempo-architecture/components/compaction/)
- [TraceQL](https://grafana.com/docs/tempo/latest/traceql/)
- [OpenTelemetry sampling](https://opentelemetry.io/docs/concepts/sampling/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Fluent Bit](fluent-bit.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OpenTelemetry →](opentelemetry.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
