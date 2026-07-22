# OpenTelemetry

OpenTelemetry je vendor-neutral framework a specification pre vytváranie, propagovanie, spracovanie a export telemetry. Nejde o observability backend ani o jediný konkrétny agent. OpenTelemetry definuje APIs, SDKs, semantic conventions, OTLP a Collector komponenty, ktoré umožňujú oddeliť application instrumentation od konkrétneho storage, query a visualization produktu.

## 1. Mentálny model

```text
application a libraries
→ OpenTelemetry API
→ OpenTelemetry SDK alebo zero-code agent
→ traces, metrics a logs
→ context propagation a resources
→ OTLP
→ OpenTelemetry Collector
→ receivers
→ processors
→ exporters
→ Prometheus, Loki, Tempo, Jaeger, OpenSearch alebo managed backend
```

OpenTelemetry rieši telemetry generation a transport. Samotné alerting, long-term storage, query, dashboards, SLO a incident workflow zostávajú úlohou backendov a prevádzkového modelu.

## 2. Čo OpenTelemetry je a čo nie je

OpenTelemetry poskytuje:

- vendor-neutral APIs a SDKs,
- automatic a manual instrumentation,
- traces, metrics a logs data model,
- context propagation,
- resource a instrumentation-scope identity,
- semantic conventions,
- OTLP protocol,
- Collector distribution a component ecosystem.

OpenTelemetry neposkytuje automaticky:

- production observability bez správneho signal designu,
- long-term telemetry storage,
- query UI,
- SLO a alert strategy,
- incident ownership,
- data privacy bez explicitnej konfigurácie,
- exactly-once telemetry delivery,
- nulový overhead.

## 3. API a SDK

### API

API je contract, ktorý používa application code a instrumentation libraries.

Príklady:

- vytvorenie span-u,
- získanie meter-a,
- vytvorenie countera alebo histogramu,
- prístup k current contextu,
- propagovanie baggage.

Reusable library má používať API a nemá vynucovať konkrétny SDK alebo exporter.

### SDK

SDK implementuje runtime behavior:

- span processors,
- metric readers a views,
- sampling,
- batching,
- aggregation,
- resource configuration,
- exporters,
- limits a shutdown/flush lifecycle.

Application owner rozhoduje, aký SDK, exporter a processing policy sa použije.

## 4. Traces

Trace reprezentuje jednu distributed operation a skladá sa zo spans.

Span obsahuje typicky:

- trace ID,
- span ID,
- parent alebo links,
- name,
- kind,
- start/end time,
- status,
- attributes,
- events,
- resource,
- instrumentation scope.

### Span names

Span name má byť stabilný a bounded.

Vhodné:

```text
GET /orders/{id}
process payment
SELECT orders
publish order.created
```

Nevhodné:

```text
GET /orders/981723
SELECT * FROM orders WHERE id=981723
payment failed for user martin@example.com
```

Dynamic payload v span name vytvára cardinality a privacy problém.

### Span kind

Bežné kinds:

- `SERVER`,
- `CLIENT`,
- `PRODUCER`,
- `CONSUMER`,
- `INTERNAL`.

Kind pomáha backendu interpretovať service boundaries a zostaviť service graph.

### Status a errors

Error recording má používať semantic conventions a jasný contract.

Nie každý exception musí znamenať failed span, ak bol očakávane spracovaný. Naopak business failure môže vyžadovať error status aj bez runtime exception.

## 5. Metrics

OpenTelemetry metrics model oddeľuje:

- instrument použitý application code,
- measurement,
- aggregation,
- temporality,
- exported metric data.

Bežné instruments:

- Counter,
- UpDownCounter,
- Histogram,
- ObservableCounter,
- ObservableUpDownCounter,
- ObservableGauge.

### Views

Views umožňujú meniť:

- názov exportovanej metric,
- description,
- aggregation,
- histogram buckets,
- povolené attributes.

Views sú dôležitý control point na:

- cardinality reduction,
- compatibility migration,
- aggregation tuning,
- odstránenie citlivých dimensions.

### Temporality

Backend a exporter môžu používať cumulative alebo delta temporality.

Pri migrácii alebo fan-out-e over:

- čo exporter produkuje,
- čo backend očakáva,
- ako sa riešia process restarts,
- či downstream správne interpretuje monotonic counters.

## 6. Logs

OpenTelemetry logs model umožňuje korelovať log records s trace contextom a spoločnými resources.

Log record môže obsahovať:

- timestamp a observed timestamp,
- severity,
- body,
- attributes,
- trace ID a span ID,
- resource,
- instrumentation scope.

OpenTelemetry logging nemusí znamenať nahradenie existujúceho logging API. Bežný model používa logging bridge alebo Collector, ktorý prevádza existujúce records do OpenTelemetry data modelu.

## 7. Events a profiles

OpenTelemetry events smerujú k pomenovanému structured log modelu alebo span events podľa contextu.

Profiles sú rozvíjajúca sa signal vrstva. Pred production implementáciou treba overiť:

- status konkrétnej language implementation,
- Collector component support,
- backend compatibility,
- overhead a sampling,
- semantic-convention stability.

Návrh nemá predpokladať rovnakú stabilitu všetkých signals a language SDKs.

## 8. Resource

Resource opisuje entitu, ktorá telemetry vytvorila.

Kritické attributes:

- `service.name`,
- `service.namespace`,
- `service.version`,
- `service.instance.id`,
- deployment environment,
- cloud provider, account, Region a zone,
- Kubernetes cluster, namespace, Pod a container,
- host a process identity.

### Stabilná service identity

`service.name` má reprezentovať logical service, nie ephemeral instance.

Nevhodné:

```text
orders-api-7b9f8d6d74-kp2rx
```

Vhodné:

```text
orders-api
```

Ephemeral Pod identity patrí do instance/resource attributes.

### Resource detection

Resource detectors môžu získať metadata z:

- environment variables,
- cloud metadata services,
- Kubernetes Downward API,
- host/process runtime,
- explicitnej application konfigurácie.

Pri konflikte musí byť jasná precedence a autoritatívny source.

## 9. Instrumentation scope

Instrumentation scope identifikuje library alebo component, ktorý telemetry vytvoril.

Obsahuje typicky:

- name,
- version,
- schema URL.

Použitie:

- odlíšenie application a framework instrumentation,
- migrácia chybných library versions,
- troubleshooting duplicate spans,
- audit schema changes.

## 10. Semantic conventions

Semantic conventions definujú spoločné názvy a významy operations, metrics, attributes, events a resources.

Výhody:

- cross-language konzistencia,
- reusable dashboards a rules,
- korelácia medzi services,
- menší vendor-specific mapping,
- jednoduchšia platform governance.

### Stability

Semantic conventions nemajú všetky rovnaký stability status.

Pred adoption over:

- stable, experimental alebo development status,
- migration guide,
- schema/version,
- compatibility s používaným SDK a backendom,
- či auto-instrumentation používa starú alebo novú convention.

Upgrade môže premenovať attributes alebo zmeniť units a tým poškodiť dashboards, rules a SLO queries.

## 11. Context propagation

Context propagation prenáša trace context cez service boundaries.

Typický W3C model:

- `traceparent`,
- `tracestate`,
- optional baggage.

Boundaries:

- HTTP,
- gRPC,
- messaging,
- queues,
- scheduled jobs,
- batch processing,
- async callbacks.

### Injection a extraction

Outbound instrumentation injectuje context do carrier-a.

Inbound instrumentation context extrahuje a vytvorí child alebo linked span.

Broken propagation spôsobí:

- nové root traces,
- fragmentované service graphs,
- nemožnosť trace-to-logs correlation,
- nesprávne sampling decisions.

## 12. Baggage

Baggage prenáša contextual key/value metadata.

Možné použitie:

- tenant class,
- experiment cohort,
- workflow ID,
- priority class.

Riziká:

- PII alebo secret leakage,
- propagation do third-party systems,
- rast headers,
- high cardinality po automatickom pridaní do spans/metrics,
- stale values.

Baggage musí mať allowlist, lifecycle a trust-boundary pravidlá.

## 13. OTLP

OTLP je OpenTelemetry protocol pre prenos telemetry.

Bežné transports:

- gRPC,
- HTTP/protobuf.

Pri konfigurácii explicitne definuj:

- endpoint,
- transport,
- TLS a CA,
- authentication headers,
- compression,
- timeout,
- batching,
- retry,
- max message size,
- tenant routing.

Port alebo endpoint dostupný na TCP úrovni ešte nepreukazuje správny OTLP protocol a signal path.

## 14. Collector architecture

Collector pipeline má tvar:

```text
receivers
→ optional processors
→ exporters
```

Collector môže mať viac pipelines pre traces, metrics a logs.

### Receivers

Príklady:

- OTLP,
- Prometheus,
- filelog,
- host metrics,
- syslog,
- cloud-specific receivers.

### Processors

Príklady:

- memory limiter,
- batch,
- attributes,
- resource,
- filter,
- transform,
- tail sampling,
- probabilistic sampling,
- routing podľa distribúcie/component availability.

### Exporters

Príklady:

- OTLP,
- Prometheus-compatible remote write,
- debug,
- vendor backends,
- Kafka alebo ďalšie supported targets podľa distribution.

Component availability sa môže líšiť medzi core, contrib a vendor distributions.

## 15. Collector distributions

Nie každý OpenTelemetry Collector binary obsahuje všetky components.

Rozlišuj:

- core distribution,
- contrib distribution,
- vendor distribution,
- custom Collector build.

Production manifest musí pinovať:

- image/version,
- component inventory,
- configuration schema,
- security patches,
- compatibility tests.

Kopírovanie konfigurácie z internetu môže zlyhať, ak používa component, ktorý v danej distribution nie je.

## 16. Agent a gateway topology

### Agent

Collector pri workload-e alebo Node-e.

Úlohy:

- local OTLP endpoint,
- file/host collection,
- resource enrichment,
- batching,
- krátkodobý buffer,
- forwarding.

### Gateway

Shared central processing tier.

Úlohy:

- tail sampling,
- tenant routing,
- policy a redaction,
- backend fan-out,
- authentication boundary,
- centralized scaling.

### Combined model

```text
applications
→ node/sidecar agents
→ load-balanced gateway tier
→ backends
```

Gateway je shared failure domain a musí mať HA, capacity, queue a self-monitoring model.

## 17. Load balancing a trace affinity

Stateless processors možno škálovať bežným load balancingom.

Stateful trace processing, najmä tail sampling, potrebuje dostať spans rovnakého trace-u na rovnakú processing identity.

Možnosti:

- trace-ID-aware routing,
- load-balancing exporter,
- upstream partitioning,
- durable queue/stream partitioning podľa trace ID.

Náhodný round-robin pred tail samplerom môže vytvoriť neúplné sampling decisions.

## 18. Sampling

### Head sampling

Rozhodnutie vzniká pri začiatku trace-u.

Výhody:

- nízky processing overhead,
- jednoduché propagation,
- predictable volume.

Nevýhody:

- nevie dopredu, či trace skončí errorom alebo vysokou latency,
- rare failures môžu byť zahodené.

### Tail sampling

Rozhodnutie vzniká po získaní väčšej časti trace-u.

Môže zachovať:

- errors,
- high-latency traces,
- selected services/routes,
- rare attributes,
- probabilistic sample ostatných.

Cena:

- state a memory,
- wait latency,
- trace affinity,
- incomplete-trace handling,
- vyššia prevádzková zložitosť.

### Sampling governance

Dokumentuj:

- policy a ownera,
- expected keep rate,
- per-service limits,
- treatment errors,
- max trace duration,
- incomplete traces,
- cost budget,
- impact na trace-derived metrics.

## 19. Filtering, transformation a redaction

Collector môže meniť telemetry pred exportom.

Použitie:

- odstránenie PII a secrets,
- normalized resource identity,
- drop noisy spans,
- route tenants,
- rename legacy attributes,
- enforce bounded attribute set.

Riziká:

- processor order mení výsledok,
- drop rule môže poškodiť SLO alebo audit evidence,
- transformation môže vytvoriť cardinality,
- redaction po fan-out-e môže byť neskoro,
- silent config change poškodí queries.

Transformácie testuj na representative telemetry fixtures.

## 20. Memory limiter, batching a queues

### Memory limiter

Chráni Collector pred uncontrolled memory growth a môže odmietať alebo dropovať telemetry podľa component behavior.

Musí byť nastavený vo vzťahu k:

- container limitu,
- traffic burstu,
- batch size,
- queue size,
- tail-sampling state.

### Batch processor

Znižuje export overhead, ale zvyšuje latency a loss window.

### Sending queue

Exporter queue absorbuje krátke downstream výpadky.

Over:

- queue capacity,
- memory alebo persistent storage,
- retry age,
- dropped records,
- shutdown drain,
- backend recovery rate.

Collector nie je automaticky durable broker.

## 21. Persistent buffering

Pri kritickej telemetry môže byť potrebná persistent queue alebo external durable buffer.

Otázky:

- čo sa stane pri process crashi,
- ako sa obnoví queue,
- čo pri plnom disku,
- aké delivery semantics poskytuje component,
- ako sa riešia duplicates,
- aký je maximum outage window,
- ako sa monitoruje oldest item age.

Audit alebo security telemetry môže vyžadovať odlišný pipeline než best-effort application traces.

## 22. Fan-out

Jeden receiver môže posielať dáta do viacerých pipelines/exporters.

Príklad:

```text
OTLP traces
→ production tracing backend
→ security archive
→ debug sampling backend
```

Fan-out trade-offy:

- backend-specific transformations,
- rozdielne retry a failure behavior,
- duplicate network cost,
- privacy boundaries,
- koordinované sampling semantics.

Pomalý exporter nemá bez kontroly zablokovať všetky ostatné paths.

## 23. Prometheus compatibility

OpenTelemetry metrics možno integrovať s Prometheus modelom cez:

- Prometheus exporter endpoint,
- Prometheus receiver scraping,
- Prometheus remote-write exporter podľa distribution,
- OTLP ingestion v podporovanom backendu.

Pri mapovaní over:

- metric name normalization,
- units,
- cumulative/delta temporality,
- histogram model,
- resource-to-label conversion,
- target metadata,
- staleness semantics,
- cardinality.

OpenTelemetry resource attributes nie sú automaticky vhodné ako všetky Prometheus labels.

## 24. Logs pipeline

OpenTelemetry Collector môže prijímať logs cez:

- OTLP,
- filelog receiver,
- syslog,
- external agent ako Fluent Bit,
- platform-specific receivers.

Dôležité:

- checkpoint/position state,
- multiline parsing,
- timestamp normalization,
- severity mapping,
- trace correlation,
- resource enrichment,
- redaction,
- backend delivery.

Pri filelog collection musí byť position state persistentný, inak po reštarte vzniknú duplicity alebo gaps.

## 25. Kubernetes deployment

Bežný model:

### DaemonSet agents

- file logs,
- host metrics,
- kubelet/node telemetry,
- local OTLP endpoint.

### Gateway Deployment

- tail sampling,
- centralized export,
- tenant routing,
- policy a transformation.

### Cluster receiver singleton

Niektoré cluster-level receivers nemajú bežať na každom Node-e, inak vytvoria duplicate telemetry.

Over:

- RBAC,
- service discovery,
- Pod/Node resource attributes,
- topology spread,
- PDB,
- HPA/custom scaling,
- persistent queue volumes,
- rollout compatibility.

## 26. Security

Chráň:

- OTLP endpoints,
- Collector configuration,
- exporter credentials,
- tenant headers,
- TLS private keys,
- debug endpointy,
- telemetry payloads,
- internal metadata.

Controls:

- mTLS alebo workload identity,
- network policies,
- least privilege,
- secret injection,
- attribute allowlists,
- redaction,
- tenant validation,
- config review,
- audit a rotation.

Collector je privileged observation point a môže vidieť citlivé dáta naprieč službami.

## 27. Telemetry self-observability

Sleduj:

- received records,
- accepted records,
- refused/dropped records,
- queue size a capacity,
- exporter successes/failures,
- retry count,
- batch size a latency,
- memory limiter actions,
- processor drops,
- process CPU/memory,
- config reload/restart,
- backend ingestion lag.

End-to-end canary:

```text
synthetic telemetry producer
→ agent
→ gateway
→ backend
→ query validation
```

Collector `/health` endpoint sám nepreukazuje funkčný telemetry path.

## 28. Configuration management

Collector configuration je production code.

Použi:

- version control,
- pinned image/component versions,
- schema validation,
- test fixtures,
- staging rollout,
- canary Collectors,
- config diff,
- rollback,
- secret references namiesto plaintextu.

Pri zmene processor order alebo sampling policy vykonaj impact review.

## 29. Migration strategy

### Vendor agent na OpenTelemetry

Postup:

1. inventory existujúcich signals,
2. mapovanie naming a resources,
3. dual export alebo shadow pipeline,
4. porovnanie coverage a cost,
5. dashboard/rule migration,
6. sampling parity,
7. cutover,
8. odstránenie duplicate instrumentation.

### Legacy semantic conventions

Použi:

- schema mapping,
- temporary dual attributes,
- backend query compatibility,
- staged SDK upgrade,
- telemetry contract tests.

Nemigruj všetky services a dashboards naraz bez compatibility windowu.

## 30. Troubleshooting: žiadna telemetry

```text
application vytvára signal?
→ SDK/agent inicializovaný?
→ service.name/resource?
→ endpoint a protocol?
→ DNS/TLS/auth?
→ agent receiver?
→ pipeline obsahuje signal type?
→ processor filter/drop?
→ exporter queue/retry?
→ backend tenant a ingestion?
→ query/time range?
```

Zachovaj sample trace ID, Collector logs a internal metrics.

## 31. Troubleshooting: chýbajúce spans

Over:

- sampling decision,
- context propagation,
- async boundaries,
- max span/attribute limits,
- tail-sampling wait a trace affinity,
- exporter timeout,
- backend rejection,
- incomplete trace handling.

## 32. Troubleshooting: duplicate telemetry

Možné príčiny:

- manual aj auto-instrumentation rovnakého frameworku,
- dva agents čítajú rovnaký log file,
- cluster receiver beží na každom Node-e,
- retry po ambiguous backend acknowledgement,
- dual export počas migrácie,
- duplicate service discovery.

Najprv identifikuj duplicate producer alebo pipeline hop.

## 33. Troubleshooting: Collector OOM

Over:

- ingest rate,
- active trace count,
- tail-sampling state,
- batch size,
- exporter queue,
- backend outage,
- memory limiter,
- number of pipelines/fan-out,
- large attributes alebo payloads,
- container limit a Go runtime behavior.

Zníženie queue bez recovery plánu môže iba zmeniť OOM na dropped telemetry.

## 34. Troubleshooting: backend throttling

Over:

- backend response codes,
- retry/backoff,
- queue growth,
- oldest item age,
- batching,
- tenant quotas,
- cardinality alebo payload size,
- exporter concurrency,
- backend recovery throughput.

Pri dlhom throttlingu musí byť explicitne definované, kedy sa telemetry dropne a ako sa alertuje.

## 35. Anti-patterny

### OpenTelemetry ako observability stratégia

Framework nerieši, čo má byť merané, kto reaguje a čo je user impact.

### Auto-instrumentation bez business signals

Vznikne technická call graph telemetry bez business outcome-u.

### Všetky resource attributes exportované ako metric labels

Vytvorí sa vysoká cardinality.

### Tail sampling za náhodným load balancerom

Spans jedného trace-u sa rozdelia medzi samplery.

### Collector bez self-monitoringu

Dropped telemetry sa prejaví iba ako chýbajúce dáta.

### Redaction až v backendu

Sensitive data už prešlo transportom a mohlo byť uložené.

### Jeden shared gateway bez HA a capacity modelu

Vznikne centrálny observability bottleneck.

### Experimental semantic convention ako stabilný enterprise contract

Upgrade môže poškodiť dashboards a queries.

## 36. Kontrolné otázky

1. Aký je rozdiel medzi OpenTelemetry API a SDK?
2. Čo rieši Collector a čo nerieši?
3. Prečo je `service.name` kritický?
4. Ako sa líši resource a instrumentation scope?
5. Na čo slúžia semantic conventions a aké majú stability riziko?
6. Ako funguje context propagation?
7. Kedy použiť agent a kedy gateway Collector?
8. Prečo tail sampling potrebuje trace affinity?
9. Ako memory limiter, batching a queues menia failure behavior?
10. Ako mapovať OpenTelemetry metrics do Prometheus modelu?
11. Ako diagnostikovať duplicate telemetry?
12. Ako bezpečne migrovať vendor instrumentation na OpenTelemetry?

## Glossary impact

Relevantné pojmy: OpenTelemetry, OTel API, OTel SDK, OTLP, Resource, Resource Detector, Instrumentation Scope, Semantic Conventions, schema URL, propagator, W3C Trace Context, baggage, Collector distribution, agent Collector, gateway Collector, receiver, processor, exporter, memory limiter, batch processor, sending queue, persistent queue, tail sampling, trace affinity, telemetry fan-out a telemetry contract test.

## Primárne zdroje

- [OpenTelemetry documentation](https://opentelemetry.io/docs/)
- [OpenTelemetry specification overview](https://opentelemetry.io/docs/specs/otel/overview/)
- [OpenTelemetry Collector architecture](https://opentelemetry.io/docs/collector/architecture/)
- [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
- [OpenTelemetry sampling](https://opentelemetry.io/docs/concepts/sampling/)
- [OpenTelemetry logs specification](https://opentelemetry.io/docs/specs/otel/logs/)
