# Observability

Táto sekcia vysvetľuje, ako navrhovať, zbierať, spracúvať, ukladať a používať telemetry tak, aby bolo možné detegovať problémy, skúmať neznáme failure modes, riadiť SLO a robiť evidence-driven operational decisions.

Cieľom nie je vytvoriť katalóg monitoring produktov. Sekcia najprv buduje stabilné koncepty: signals, instrumentation, correlation, service/resource monitoring methods, alerting a cardinality. Následne ich aplikuje na Prometheus, Alertmanager, Grafana, Loki, Elasticsearch/OpenSearch, Fluent Bit, Jaeger, Tempo a OpenTelemetry.

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
14. [OpenTelemetry](opentelemetry.md)
15. [Alert design a alert fatigue](alert-design-alert-fatigue.md)
16. [Cardinality](cardinality.md)

Sekcia je dokončená. Lineárna dokumentácia pokračuje sekciou [Security and Identity](../13-security-and-identity/README.md).

## Cieľ zvládnutia

### Signals a instrumentation

- presne rozlíšiť monitoring, observability, telemetry a instrumentation,
- vysvetliť odlišný data model a operational use metrics, logs, traces, events, audit records a profiles,
- vybrať signal podľa otázky a prejsť od agregovaného symptómu ku konkrétnej operácii,
- navrhnúť structured log, metric, trace a event correlation contract,
- vysvetliť counter, gauge, histogram, distribution, temporality a bounded cardinality,
- odlíšiť parent-child spans, span links, span events a samostatné events,
- kombinovať manual, automatic a platform instrumentation,
- riadiť telemetry overhead, privacy, versioning a cost ako production contract.

### Monitoring methodologies

- aplikovať RED na HTTP, gRPC, queues a batch workloads,
- definovať request rate, error numerator/denominator a duration distribution bez retry skreslenia,
- aplikovať USE cez kompletný resource inventory,
- analyzovať CPU, memory, storage, network, pools, containers a cloud quotas podľa enforcement boundary,
- definovať Golden Signals pre konkrétny user journey,
- naviazať Golden Signals a RED na SLIs/SLOs a saturation na capacity risk,
- kombinovať Golden Signals, RED, traces, USE, logs a profiles v jednom investigation workflowe.

### Prometheus a Alertmanager

- vysvetliť scrape, service discovery, relabeling, multidimenzionálne series a staleness,
- vysvetliť TSDB, WAL, head block, compaction a retention,
- používať PromQL selectors, rates, aggregations, vector matching a histogram queries,
- navrhovať recording a alerting rules a validovať ich cez `promtool`,
- vysvetliť remote write, federation, HA a hranice lokálneho Prometheus modelu,
- rozlíšiť alert condition, identity, group a notification,
- navrhnúť routing tree, grouping, timing, silences, inhibition a templates,
- diagnostikovať target, rule, notification, deduplication a HA failures.

### Grafana

- vysvetliť rozdiel medzi Grafanou a telemetry backendom,
- navrhovať panels a dashboards podľa operational questions,
- používať variables, annotations, links, correlations a Explore,
- rozlíšiť query, expression, transformation, field config a visualization,
- spravovať dashboards, data sources a alerting cez provisioning/IaC,
- rozlíšiť Grafana-managed a data-source-managed alerting,
- diagnostikovať `No data`, nesprávne hodnoty, pomalé dashboardy a provisioning drift.

### Logs

- vysvetliť Loki log stream, labels, structured metadata, chunks a TSDB index,
- rozlíšiť Loki write/read path, deployment modes, multi-tenancy, retention a LogQL,
- vysvetliť documents, shards, Lucene segments, data streams, mappings a rollover,
- porovnať Elasticsearch lifecycle modely a OpenSearch ISM bez predpokladu identických semantics,
- navrhnúť Fluent Bit input, parser, tag, filter, buffering, retry a output pipeline,
- diagnostikovať missing logs, duplicates, rejected entries, mapping failures, backlog a slow queries,
- rozpoznať, kedy použiť label-based store, document-search store alebo kombináciu.

### Distributed tracing

- vysvetliť trace/span identity, context propagation a OTLP ingestion,
- vysvetliť Jaeger v2 roles, storage a sampling modely,
- vysvetliť Tempo monolithic a microservices architecture, object storage a TraceQL,
- rozlíšiť recent a historical trace query paths,
- navrhnúť head, tail, remote alebo adaptive sampling,
- prepojiť traces s logs, metrics, exemplars a service graphom,
- diagnostikovať missing, incomplete a dropped traces, queue lag a storage failures.

### OpenTelemetry

- vysvetliť rozdiel medzi OpenTelemetry API, SDK, semantic conventions, OTLP a Collectorom,
- navrhnúť stabilnú resource a instrumentation-scope identity,
- overovať stability status semantic conventions a riadiť schema migrations,
- navrhnúť agent a gateway Collector topology,
- používať receivers, processors, exporters, memory limiter, batching a queues,
- zabezpečiť trace affinity pre tail sampling,
- navrhnúť filtering, transformation, redaction a fan-out bez straty kritických signals,
- prevádzkovať Collector s version pinningom, self-observability, canary testom a rollbackom,
- diagnostikovať missing, duplicate, throttled a dropped telemetry.

### Alert design

- rozlíšiť page, ticket a informational event,
- navrhovať actionable symptom alerts s ownerom, impactom, runbookom a validation krokom,
- používať SLO burn-rate alerting, vhodné thresholds, `for`, `keep_firing_for` a no-data policy,
- riadiť alert identity, severity, grouping, inhibition, silences a maintenance,
- merať alert quality cez actionable rate, duplicates, flapping, pages per incident a time to acknowledgement,
- testovať alerts ako code od rule expression po receiver a acknowledgement,
- rozpoznať a systematicky znižovať alert fatigue.

### Cardinality

- rozlíšiť telemetry volume a cardinality,
- vypočítať combinatorial growth dimensions,
- rozlíšiť bounded a unbounded dimensions,
- navrhovať cardinality budgets per service a tenant,
- vysvetliť series a stream churn,
- riadiť Prometheus series, histogram, Loki stream, indexed-field a trace-attribute cardinality,
- chrániť platformu cez views, relabeling, allowlists, mappings, quotas a runtime limits,
- diagnostikovať cardinality spikes a vykonať bezpečnú remediation,
- naviazať observability cost na producenta, use case a retention model.

### Prevádzkový contract

- monitorovať každý observability component ako kritickú platformu,
- používať end-to-end metric, alert, log a trace canaries,
- navrhnúť koreláciu `SLO alert → exemplar/trace → logs → resource metrics/profile`,
- chrániť security a audit telemetry oddelenou access a failure boundary,
- riadiť upgrades, backups, lifecycle, retention, tenancy a cost.

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
| OpenTelemetry | Learning | L2 |
| Alert design a alert fatigue | Learning | L2 |
| Cardinality | Learning | L2 |
