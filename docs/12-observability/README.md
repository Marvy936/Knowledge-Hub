# Observability

Táto sekcia vysvetľuje, ako navrhovať, zbierať, spracúvať, ukladať a používať telemetry tak, aby bolo možné detegovať problémy, skúmať neznáme failure modes, riadiť SLO a robiť evidence-driven operational decisions.

Cieľom nie je vytvoriť katalóg monitoring produktov. Najprv sa budujú stabilné koncepty: signals, instrumentation, correlation, telemetry pipelines, service/resource monitoring methods, alerting a cardinality. Až potom nasledujú konkrétne platformy ako Prometheus, Alertmanager, Grafana, Loki, Elasticsearch/OpenSearch, Fluent Bit, Jaeger, Tempo a OpenTelemetry.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md),
- [Kubernetes](../09-kubernetes/README.md),
- [Cloud and AWS](../11-cloud-and-aws/README.md).

## Odporúčané poradie

1. [Monitoring vs. observability](monitoring-vs-observability.md)
2. [Metrics, logs, traces a events](metrics-logs-traces-events.md)
3. [Instrumentation a telemetry](instrumentation-telemetry.md)
4. [RED method](red-method.md)
5. [USE method](use-method.md)
6. [Golden Signals](golden-signals.md)
7. [Prometheus](prometheus.md)
8. [Alertmanager](alertmanager.md)
9. [Grafana](grafana.md)
10. [Loki](loki.md)
11. [Elasticsearch alebo OpenSearch](elasticsearch-opensearch.md)
12. [Fluent Bit](fluent-bit.md)
13. [Jaeger a Tempo](jaeger-tempo.md)

Nasledujúci blok uzavrie sekciu cez OpenTelemetry, alert design a cardinality. Potom lineárna dokumentácia prejde do Security and Identity.

## Cieľ zvládnutia

Po dokončení aktuálneho bloku má byť možné:

### Signals a instrumentation

- presne rozlíšiť monitoring, observability, telemetry a instrumentation,
- vysvetliť odlišný data model a operational use metrics, logs, traces, events, audit records a profiles,
- vybrať signal podľa otázky a prejsť od agregovaného symptómu ku konkrétnej operácii,
- navrhnúť structured log, metric, trace a event correlation contract,
- vysvetliť counter, gauge, histogram, distribution, temporality a bounded cardinality,
- odlíšiť parent-child spans, span links, span events a samostatné events,
- navrhnúť code-based a zero-code instrumentation bez zamieňania automatic coverage za business observability,
- vysvetliť OpenTelemetry API, SDK, instrumentation scope, resource identity, semantic conventions a context propagation,
- navrhnúť telemetry pipeline cez receiver, processor, batching, sampling, redaction a exporter,
- vyhodnotiť agent, sidecar a gateway Collector deployment trade-offy,
- monitorovať telemetry pipeline cez accepted, dropped, queued a failed records.

### Monitoring methodologies

- aplikovať RED na HTTP, gRPC, queues a batch workloads,
- definovať request rate, error numerator/denominator a duration distribution bez retry alebo cardinality skreslenia,
- aplikovať USE cez kompletný resource inventory a rozlíšiť utilization, saturation a errors,
- analyzovať CPU, memory, storage, network, pools, containers a cloud quotas podľa správnej enforcement boundary,
- definovať Golden Signals pre konkrétny user journey alebo workload,
- oddeľovať successful a failed latency, logical demand a retry amplification,
- naviazať Golden Signals a RED na SLIs/SLOs a saturation na capacity risk,
- kombinovať Golden Signals, RED, traces, USE, logs a profiles v jednom investigation workflowe.

### Prometheus

- vysvetliť pull-based scrape model, exporters, service discovery a target lifecycle,
- modelovať multidimenzionálne time series pomocou stabilných metric names a bounded labels,
- rozlíšiť target relabeling, metric relabeling a external labels,
- vysvetliť local TSDB, WAL, head block, compaction, retention a staleness,
- používať PromQL selectors, rates, aggregations, vector matching a histogram queries,
- navrhovať recording a alerting rules a validovať ich cez `promtool`,
- vysvetliť remote write, federation, HA replicas a hranice lokálneho Prometheus modelu,
- diagnostikovať target failures, missing series, cardinality incidents, slow queries a remote-write backlog.

### Alertmanager

- rozlíšiť alert condition, alert identity, alert group a notification,
- navrhnúť stabilné labels, annotations, ownership a severity contract,
- vytvoriť route tree s bezpečným inheritance a matcher modelom,
- vysvetliť grouping, `group_wait`, `group_interval` a `repeat_interval`,
- odlíšiť silences, mute time intervals a inhibition,
- navrhovať notification templates a receiver integrations,
- vysvetliť Alertmanager peer mesh, replicated notification state a duplicate-delivery hranice,
- diagnostikovať firing alert bez notification, duplicity, alert storm, silence a inhibition failures.

### Grafana

- vysvetliť rozdiel medzi Grafanou a telemetry backendom,
- navrhovať panels, dashboards a visualization hierarchy podľa operational questions,
- používať variables, annotations, data links, correlations a Explore bez vytvárania query stormu,
- rozlíšiť backend query, expression, transformation, field config a visualization,
- spravovať dashboards, data sources a alerting resources cez provisioning/IaC,
- rozlíšiť Grafana-managed a data-source-managed alert rules,
- vysvetliť authentication, folder permissions, data-source access a edition-specific RBAC hranice,
- navrhnúť Grafana HA, database backup, plugin a upgrade lifecycle,
- diagnostikovať `No data`, nesprávne hodnoty, pomalé dashboardy, data-source failures a provisioning drift.

### Loki

- vysvetliť log stream ako tenant a label-set boundary,
- odlíšiť bounded labels, structured metadata a log body,
- vysvetliť index/chunk model, object storage, TSDB index store a schema periods,
- rozlíšiť single-binary a distributed deployment a overovať version-specific deployment modes,
- vysvetliť distributor, ingester, query frontend, scheduler, querier, ruler a compaction lifecycle,
- používať LogQL stream selectors, line filters, parsers, range aggregations a `unwrap`,
- navrhnúť multi-tenant authentication, retention a deletion model,
- diagnostikovať missing logs, rejected entries, slow queries, stream explosion a recent/historical path failures.

### Elasticsearch alebo OpenSearch

- vysvetliť documents, indexes, primary/replica shards a Lucene segments,
- rozlíšiť write acknowledgement, refresh/search visibility a lifecycle operations,
- navrhovať data streams, backing indexes, templates, mappings a rollover,
- odlíšiť `keyword`, `text`, analyzers, dynamic mapping a mapping explosion,
- porovnať Elasticsearch ILM/Data Stream Lifecycle s OpenSearch ISM bez predpokladu identických semantics,
- navrhnúť shard sizing, allocation, failure-domain, tiering a snapshot model,
- spracovať bulk partial failures, `429` backpressure a mapping quarantine,
- diagnostikovať yellow/red health, disk watermarks, unassigned shards, heap/GC, slow queries a missing documents.

### Fluent Bit

- vysvetliť pipeline input → parser → tag → filters → chunks → output,
- prevádzkovať Tail input s persistentnou position database a rotation/multiline modelom,
- navrhnúť Kubernetes metadata allowlist, parsing, redaction a routing,
- rozlíšiť memory a filesystem buffering a ich loss/replay boundaries,
- vysvetliť backpressure, pause, retry, per-output queue limits a duplicate semantics,
- konfigurovať Loki, Elasticsearch/OpenSearch a OTLP output contracts,
- nasadiť Fluent Bit ako Kubernetes DaemonSet s persistentným state-om a graceful shutdownom,
- diagnostikovať missing logs, duplicates, multiline failures, memory/disk backlog, `429` a metadata failures.

### Jaeger a Tempo

- vysvetliť trace/span identity, context propagation a OTLP ingestion,
- navrhnúť OpenTelemetry Collector pred tracing backendom,
- vysvetliť Jaeger v2 roles, all-in-one, direct-to-storage a Kafka-ingester model,
- vysvetliť Tempo monolithic a aktuálnu microservices architektúru s durable queue a object storage,
- rozlíšiť recent-data a historical-data query paths,
- vysvetliť Parquet blocks, query frontend, TraceQL, backend maintenance a metrics-generator,
- navrhnúť head, tail, remote alebo adaptive sampling s explicitným completeness modelom,
- prepojiť traces s logs, metrics, exemplars a service graphom,
- diagnostikovať missing/broken traces, dropped spans, Kafka lag, recent/historical failures a slow search.

### Prevádzkový contract

- diagnostikovať chýbajúcu alebo skreslenú telemetry cez producer, agent, collector, backend a query vrstvy,
- riadiť telemetry overhead, privacy, schema versioning, retention a cost ako production contract,
- monitorovať Prometheus, Alertmanager, Grafana, Loki, search cluster, Fluent Bit a tracing backend ako kritickú platformu,
- testovať end-to-end metric, alert, log a trace canaries,
- navrhnúť koreláciu `SLO alert → exemplar/trace → logs → resource metrics/profile`,
- rozpoznať, kedy je vhodný label-based log store, document-search store alebo kombinovaný model.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Monitoring vs. observability | Learning | L2 |
| Metrics, logs, traces a events | Learning | L2 |
| Instrumentation a telemetry | Learning | L2 |
| RED method | Learning | L2 |
| USE method | Learning | L2 |
| Golden Signals | Learning | L2 |
| Prometheus | Learning | L2 |
| Alertmanager | Learning | L2 |
| Grafana | Learning | L2 |
| Loki | Learning | L2 |
| Elasticsearch alebo OpenSearch | Learning | L2 |
| Fluent Bit | Learning | L2 |
| Jaeger a Tempo | Learning | L2 |
