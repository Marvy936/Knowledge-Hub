# Observability signals and methods glossary entries

## Attempt rate

Počet technických pokusov o vykonanie operácie za čas vrátane retries; môže byť vyšší než počet logical operations. Pozri [RED method](docs/12-observability/red-method.md).

## Automatic instrumentation

Instrumentation poskytovaná agentom, runtime hookom, frameworkom alebo knižnicou bez explicitného vytvárania každého signalu v application code. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Baggage — OpenTelemetry

Contextual key/value informácie propagované cez service boundaries spolu s trace contextom; vyžadujú prísny privacy, size a cardinality model. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Capacity cliff

Bod, pri ktorom malé ďalšie zvýšenie demandu spôsobí prudký rast queueing, latency alebo errors, pretože systém vyčerpal effective capacity. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Capacity headroom — observability

Rozdiel medzi aktuálnym demandom alebo využitím a effective capacity po zohľadnení failoveru, limits a unavailable resources. Pozri [USE method](docs/12-observability/use-method.md).

## Code-based instrumentation

Explicitné použitie telemetry API alebo SDK v application code na zachytenie business semantics, custom metrics, spans, logs alebo events. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Collector agent

Telemetry Collector nasadený blízko workloadu alebo Node-u na lokálny príjem, enrichment, batching a export signals. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Collector gateway

Centralizovaná alebo tiered Collector vrstva používaná na routing, policy, tail sampling, tenant isolation a fan-out do backendov. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Coordinated omission

Measurement chyba, pri ktorej test alebo client nepočíta obdobia, keď systém nevedel prijímať novú prácu, a preto podhodnotí skutočnú latency alebo failure impact. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Counter — metric

Monotónne rastúca metric hodnota používaná pre počty udalostí alebo práce; pri analýze sa typicky prevádza na rate alebo increase za časové okno. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Demand unit

Workload-specific jednotka trafficu, napríklad request, message, transaction, byte, query alebo inference, ktorá reprezentuje reálny demand na systém. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Dependency RED

Rate, Errors a Duration merané pre outbound dependency calls, používané na oddelenie vlastného service behavior od downstream degradácie. Pozri [RED method](docs/12-observability/red-method.md).

## Derived signal

Telemetry signal vypočítaný z iného signalu, napríklad metrics zo spans alebo logs; musí mať explicitný source-of-truth a sampling contract. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Distribution — metric

Reprezentácia rozdelenia nameraných hodnôt, napríklad latency alebo response size, ktorá zachováva viac informácií než average. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Duration distribution

Rozdelenie trvania operácií používané v RED na sledovanie typical aj tail latency bez redukcie na jediný priemer. Pozri [RED method](docs/12-observability/red-method.md).

## Effective capacity

Kapacita skutočne dostupná workloadu po zohľadnení quotas, reservations, failures, topology, limits a maintenance, nie iba nominálny súčet resources. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Enforcement boundary — resource

Vrstva, na ktorej sa reálne presadzuje resource limit alebo quota, napríklad cgroup, Node, connection pool, Availability Zone alebo cloud account. Pozri [USE method](docs/12-observability/use-method.md).

## Error rate — RED

Podiel failed operations voči relevantnému počtu valid operations pri rovnakom scope-e a success contracte. Pozri [RED method](docs/12-observability/red-method.md).

## Exporter — telemetry

Komponent telemetry pipeline, ktorý odosiela spracované signals do backendu alebo ďalšieho collectora. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Failed latency

Latency requestov alebo operácií, ktoré skončili failure; sleduje sa oddelene, aby rýchle errors neskresľovali successful latency. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Gauge — metric

Metric hodnota, ktorá môže rásť aj klesať a reprezentuje napríklad aktuálnu queue depth, memory usage alebo počet connections. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Golden Signals

Google SRE monitoring model pozostávajúci zo Latency, Traffic, Errors a Saturation pre user-facing workload. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Head sampling

Trace sampling decision vykonané na začiatku trace-u pred poznaním finálneho outcome-u a celkovej latency. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Hidden queue

Čakacia vrstva, ktorá nie je viditeľná v hlavnom service dashboarde, napríklad connection pool, thread pool, kernel queue alebo downstream scheduler. Pozri [USE method](docs/12-observability/use-method.md).

## Histogram — metric

Metric aggregation zaznamenávajúca počet observations v definovaných buckets spolu s count a typicky sum, vhodná na latency distributions a threshold SLIs. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Instrumentation library

Knižnica, ktorá vytvára telemetry pre application, framework alebo dependency a nesie vlastný instrumentation scope. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Instrumentation scope

Logical software unit a jej version, s ktorou OpenTelemetry spája vytvorené spans, metrics a log records. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Leading indicator — capacity

Signal, ktorý upozorňuje na blížiaci sa failure pred viditeľným user impactom, napríklad queue growth, throttling alebo saturation. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Logical operation

Jedna business alebo caller-visible operácia bez ohľadu na počet interných retry attempts a fan-out calls. Pozri [RED method](docs/12-observability/red-method.md).

## Normalized route

Stabilný route pattern, napríklad `/orders/{id}`, používaný namiesto raw URL na zachovanie bounded metric a trace cardinality. Pozri [RED method](docs/12-observability/red-method.md).

## OpenTelemetry API

Vendor-neutral programming contract používaný application a libraries na vytváranie telemetry bez vynútenia konkrétneho backendu alebo SDK konfigurácie. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## OpenTelemetry SDK

Runtime implementácia OpenTelemetry API, ktorá zabezpečuje sampling, processing, aggregation, resource configuration a export telemetry. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## OTLP

OpenTelemetry Protocol používaný na prenos telemetry medzi SDKs, Collectors a podporovanými backends. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Pipeline processor — telemetry

Komponent medzi receiverom a exporterom, ktorý môže vykonávať batching, filtering, redaction, enrichment, sampling alebo routing. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## RED method

Service-oriented monitoring metodika sledujúca Rate, Errors a Duration pre každú relevantnú operation. Pozri [RED method](docs/12-observability/red-method.md).

## Receiver — telemetry

Komponent telemetry pipeline, ktorý prijíma signals cez OTLP, scrape, logs alebo iný podporovaný protocol. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Request rate

Počet requestov alebo jednotiek práce za čas na presne definovanej measurement boundary. Pozri [RED method](docs/12-observability/red-method.md).

## Resource inventory — USE

Systematický zoznam bounded hardware, software a cloud resources, pre ktoré sa hľadajú utilization, saturation a error signals. Pozri [USE method](docs/12-observability/use-method.md).

## Semantic conventions — telemetry

Štandardizované názvy a významy operations, resources a attributes umožňujúce interoperabilitu instrumentation a backendov. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Severity — log

Klasifikácia operational závažnosti log recordu, napríklad DEBUG, INFO, WARN, ERROR alebo FATAL, ktorá musí odrážať význam pre konkrétnu operáciu. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Signal quality

Hodnotenie telemetry podľa correctness, completeness, freshness, contextu, correlation, schema stability, security, cost a ownershipu. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Silent error

Failure, ktorý neprodukuje bežný explicitný error status, napríklad `200` s chybným obsahom, nespracovaná async message alebo neobnoviteľný backup. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Span event

Časovo označená bodová udalosť priradená ku konkrétnemu span-u, napríklad exception, retry alebo cache miss. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Span link

Vzťah medzi spanmi používaný pri async, batch alebo fan-out causalite, ktorá nevytvára jednoduchý parent-child strom. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Structured log

Log record so stabilnými typed fields a schema namiesto závislosti na parsovaní voľného textu. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Successful latency

Latency operácií, ktoré splnili success contract, sledovaná oddelene od rýchlych alebo pomalých failures. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Tail latency

Latency najpomalšej časti request distribution, typicky sledovaná cez vyššie percentiles alebo threshold compliance. Pozri [RED method](docs/12-observability/red-method.md).

## Tail sampling

Trace sampling decision vykonané po zhromaždení väčšej časti trace-u, aby bolo možné zachovať errors, high-latency alebo inak zaujímavé traces. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Telemetry backpressure

Stav, keď downstream receiver alebo backend nestíha prijímať telemetry a producers alebo collectors musia bufferovať, retryovať, dropovať alebo obmedziť tok. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Telemetry batching

Zoskupovanie viacerých telemetry records pred exportom na zníženie overheadu za cenu vyššej latency a väčšieho loss windowu. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Telemetry self-observability

Monitoring samotného telemetry pipeline cez accepted, queued, dropped, retried a failed records spolu s resource usage a ingestion lagom. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Temporality — metric

Semantics určujúca, či metric export reprezentuje cumulative hodnotu od začiatku alebo delta zmenu za konkrétny interval. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## USE method

Resource-oriented performance metodika, ktorá pre každý resource preveruje Utilization, Saturation a Errors. Pozri [USE method](docs/12-observability/use-method.md).

## Utilization — USE

Miera používania resource-u vyjadrená ako busy time, obsadená kapacita, throughput voči limitu alebo concurrency voči maximu. Pozri [USE method](docs/12-observability/use-method.md).

## Saturation — USE

Množstvo práce, ktoré resource nedokáže okamžite obslúžiť a prejavuje sa queueingom, wait time, throttlingom alebo rejection. Pozri [USE method](docs/12-observability/use-method.md).

## Zero-code instrumentation

Automatic telemetry generation bez zmeny application source, typicky cez agent, runtime hooks alebo platform integration. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).
