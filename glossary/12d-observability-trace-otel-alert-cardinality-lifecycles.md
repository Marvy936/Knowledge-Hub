# Observability tracing, OpenTelemetry, alert and cardinality lifecycle glossary entries

## Action contract — alerting

Versionovaný contract určujúci user impact, urgency, ownera, safe first action, forbidden action, runbook a resolution validation konkrétneho page-u. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Actionable-rate verdict

Pomer pages alebo notifications, ktoré viedli k potrebnej ľudskej či automatickej akcii, vyhodnotený spolu s false positives, duplicates a auto-resolutions. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Active-cardinality verdict

Rozhodnutie, či počet súčasne aktívnych series, streams, terms, alert instances alebo promoted trace dimensions zostáva v budgete pre konkrétny tenant a signal. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Alert-action subject

Exact user outcome, signal population, rule generation, evaluation windows, alert identity, severity, owner, notification policy a external incident identity analyzovaného alertu. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert-control-plane authority

Jediný systém oprávnený vlastniť rule evaluation a paging policy konkrétneho symptom alertu, napríklad Prometheus/Alertmanager alebo Grafana-managed alerting. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert-fatigue feedback loop

Reinforcing loop, v ktorom noisy a neakčné pages znižujú dôveru a response speed, čo zhoršuje incident outcome a vedie k ďalším broad alerts alebo silences. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert retirement verdict

Rozhodnutie odstrániť, demote-nuť, zlúčiť alebo automatizovať alert, ktorý nemá ownera, action, precision alebo jedinečný detection benefit. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert-rule generation

Versionovaná query, population, threshold/burn-rate, windows, `for`, no-data a output-label konfigurácia vytvárajúca alert state. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Block-publication generation — tracing

Exact Kafka offsets, block-builder version, Parquet block objects, object-store paths a commit state, ktoré preukazujú prechod trace records do historical storage. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Canonical symptom page

Jediný authoritative page pre konkrétny user-facing symptom, ku ktorému cause signals slúžia ako investigation evidence namiesto duplicate paging paths. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Cardinality acceptance verdict

Dôkaz, že active identities, churn, backlog, query cost a alerts zostávajú pod budgetom, critical signals sú kompletné a forbidden dimensions sa nevrátili po rollout-e alebo restart-e. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality-budget generation

Versionovaný allowed-dimension, expected-value, active-count, churn, tenant quota, retention, cost a exception contract konkrétneho telemetry signal-u. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality containment

Minimálny auditovaný runtime zásah, ktorý zastaví tvorbu nových problematických identities a chráni platformu bez neanalyzovaného odstránenia critical evidence. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality recovery generation

Authoritative producer, schema, allowlist, aggregation a runtime-limit zmena, ktorá nahradí emergency containment a prejde dependency, cost a restart validation. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality subject

Exact producer, release, tenant, signal/backend, identity model, dimensions, active count, churn, budget, dependencies a observation window analyzovanej cardinality. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Collector distribution generation

Pinned OpenTelemetry Collector artifact a jeho exact receiver, processor, exporter a extension inventory vrátane component stability. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Combination-space estimate

Odhad potenciálnych a expected reálnych combinations dimensions pred zavedením telemetry schema change-u. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Component-stability inventory — OpenTelemetry

Zoznam použitých Collector components a signals s ich signal-specific stability, distribution availability a compatibility statusom. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Cross-signal cardinality amplification

Násobenie jednej dynamic dimension naprieč metrics, log streams, trace-derived metrics, indexed fields, dashboard variables a alert identities. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Dimension inventory — observability

Úplný zoznam labels, attributes, fields a promoted dimensions spolu s ich source, boundedness, purpose, backend use a retention. Pozri [Cardinality](docs/12-observability/cardinality.md).

## End-to-end alert acceptance

Dôkaz, že controlled signal vytvorí intended alert state, jednu správne routovanú external notification, acknowledgement a resolved closure bez forbidden muting alebo duplicate incidentu. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Exact-search exception — cardinality

Schválené použitie high-cardinality field-u pre bounded exact log, trace alebo document search bez jeho promotion do metrics, Loki streams, alerts alebo unrestricted aggregations. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Exact trace lookup

Query konkrétneho trace ID odlíšená od broad attribute searchu a validovaná voči tenant, recent/historical path a storage generation. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Exporter-delivery subject — OpenTelemetry

Exact signal, queue, exporter component/version, endpoint, credential, tenant, acknowledgement, retry a backend read-back identity. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## External incident identity

Stable receiver/on-call key, ktorý viaže duplicate HA notifications a firing/resolved updates k jednému operational incidentu. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Forbidden-dimension contract

Explicitný zákaz unbounded alebo citlivej dimension v konkrétnom backend identity modeli, napríklad `merchant_id` v metric labels alebo Loki stream labels. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Historical-identity retirement

Časovo viazaný lifecycle, počas ktorého staré series, streams, terms alebo blocks po schema fix-e zaniknú cez staleness, retention, rollover alebo reindex. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Historical-trace path

Trace query path cez published blocks alebo external storage, index/block metadata, object permissions, compaction a retention. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Identity-churn rate

Rýchlosť tvorby a zániku telemetry identities, ktorá môže destabilizovať WAL, index, compaction a recovery aj pri miernom active count-e. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Ingest acknowledgement — tracing

Potvrdenie, že tracing backend alebo durable queue prijala trace records; samo nepreukazuje complete trace ani historical block publication. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Instrumentation-scope generation

OpenTelemetry scope name, version a schema URL identifikujúce library alebo component, ktorý telemetry vytvoril. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Kafka trace replay window

Časový interval určený Kafka retention a consumer progressom, počas ktorého Tempo block-builder/live-store alebo Jaeger ingester dokáže znovu spracovať trace records. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Multi-signal canary — OpenTelemetry

Synthetic trace, metric a log overený cez agent, gateway, processing policies, každý intended backend, query correlation a forbidden-field check. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Notification-policy generation

Versionovaný routing, grouping, timing, inhibition, silence, receiver a template contract aplikovaný na alert identity. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## OpenTelemetry acceptance verdict

Dôkaz, že exact signal generations prešli per-hop accountingom, backend read-backom, correlation, cost a privacy checks a zostali správne po topology change alebo restart-e. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## OpenTelemetry subject

Exact application/release, SDK/agent, semantic schema, resource precedence, propagation, sampling, Collector distribution/config/topology, exporter, backend a evidence cut-off. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Page eligibility contract

Kritériá urgentnosti, importance, actionability a reality, ktoré musí signal splniť pred preradením na human page. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Pages-per-incident

Alert-quality metric počítajúca počet human pages vytvorených jedným operational incidentom. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Per-hop telemetry accounting

Porovnanie received, accepted, refused, dropped, queued a acknowledged records na každom SDK, agent, gateway, exporter a backend hop-e. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Processor-order contract — OpenTelemetry

Versionované poradie identity normalization, redaction, cardinality control, sampling/filtering, batching a exportu určujúce final telemetry outcome. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Producer cost attribution — observability

Priradenie ingestion, active-identity, storage, query a retention costu konkrétnemu service, teamu, tenantovi a instrumentation generation. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Propagation generation — tracing

Versionovaný inject/extract a async/message context contract vytvárajúci parent, child a link relationships expected span graphu. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Recent-trace path

Trace query path cez Tempo live-store alebo ekvivalentný current Jaeger/storage visibility model pred alebo nezávisle od historical publication. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Resource-precedence generation — OpenTelemetry

Explicitné poradie environment, cloud/Kubernetes detectorov, processorov a application configu pri určovaní effective resource attributes. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Sampling-policy generation

Versionovaný head/tail/remote policy contract s keep/drop rules, expected rates, trace duration, late-span a incomplete-trace behaviorom. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md) a [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Semantic-schema generation — OpenTelemetry

Exact semantic-convention stability, attribute names/units, schema URL a compatibility mapping používané producers, processors a consumers. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Signal-contract generation — OpenTelemetry

Versionovaný expected signal, population, identity, schema, coverage, overhead, privacy a backend-consumer contract. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Signal-population contract — alerting

Exact valid numerator, denominator, cohort, traffic guard, data authority a no-data semantics alert condition-u. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Telemetry-loss window — OpenTelemetry

Time/signal-specific interval neobnoviteľnej alebo nepreukázateľnej straty pre queue overflow, processor drop, crash, expiry alebo backend failure. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Trace-affinity contract

Pravidlo zabezpečujúce, že všetky spans jedného trace-u dorazia k rovnakej stateful tail-sampling alebo processing identity. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md) a [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Trace-evidence loss window

Časový a tenant/partition-specific interval, pre ktorý historical traces nemožno obnoviť pre sampling, propagation, queue retention, block publication alebo storage loss. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Trace-evidence subject

Exact operation, trace/population, service/release, instrumentation, propagation, sampling, Collector, backend, tenant, recent/historical storage a query generation. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Trace-search generation

Exact backend product/version, tenant, query language/expression, attribute/index contract, time range a scanned storage generation broad trace searchu. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Tracing-backend acceptance verdict

Dôkaz, že synthetic a incident-representative traces prešli samplingom, ingestom, recent/historical publication, lookup/search, retention a tenant-isolation checks. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).