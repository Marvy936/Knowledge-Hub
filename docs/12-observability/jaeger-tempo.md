# Jaeger a Tempo

Jaeger a Grafana Tempo sú distributed tracing backends. Prijímajú spans, ukladajú trace data a poskytujú query a visualization vrstvu na rekonštrukciu request paths naprieč services. Oba systémy podporujú OpenTelemetry-based ingestion, ale používajú odlišný storage, deployment a query model.

Tracing backend nevytvára kvalitné traces automaticky. Potrebuje správnu application instrumentation, context propagation, sampling, stable resource identity, bounded attributes a koreláciu s metrics a logs.

## 1. Mentálny model

```text
application instrumentation
→ trace context propagation
→ spans
→ OpenTelemetry Collector alebo agent
→ sampling, enrichment a redaction
→ Jaeger alebo Tempo ingest path
→ trace storage
→ query service
→ Jaeger UI alebo Grafana
→ trace-to-logs, trace-to-metrics a service graph investigation
```

Backend vidí iba spans, ktoré boli vytvorené, sampled, exportované a úspešne uložené.

## 2. Trace a span identity

Trace identifikuje end-to-end operation pomocou trace ID.

Span reprezentuje jednu operation a typicky obsahuje:

- trace ID,
- span ID,
- parent span ID alebo links,
- operation name,
- start/end time,
- status,
- resource attributes,
- span attributes,
- span events,
- links,
- instrumentation scope.

Backend skladá graph podľa IDs a relationships. Nevie spoľahlivo opraviť chýbajúci alebo nesprávny parent context.

## 3. Context propagation

Trace continuity závisí od propagation cez:

- HTTP headers,
- gRPC metadata,
- message headers,
- queue attributes,
- async callbacks,
- batch boundaries,
- scheduled jobs.

Chyby:

- client nevloží context,
- proxy odstráni headers,
- consumer nevytiahne context,
- thread/coroutine context sa stratí,
- nový trace sa vytvorí namiesto child span-u,
- propaguje sa sampled flag nekonzistentne.

Broken trace je často instrumentation problém, nie storage problém.

## 4. OTLP

OpenTelemetry Protocol je preferovaný vendor-neutral transport pre traces medzi SDKs, Collectors a backends.

Varianty:

- OTLP/gRPC,
- OTLP/HTTP.

Over:

- endpoint a port,
- TLS/mTLS,
- authentication,
- compression,
- max message size,
- retries,
- queue,
- tenant headers,
- protocol compatibility.

Jaeger aj Tempo môžu prijímať OTLP podľa použitej konfigurácie a verzie.

## 5. OpenTelemetry Collector pred tracing backendom

Collector môže vykonávať:

- receiver termination,
- batching,
- memory limiting,
- resource detection,
- attribute normalization,
- redaction,
- filtering,
- tail sampling,
- multi-tenant routing,
- fan-out,
- retries a queues.

Častý production model:

```text
SDK alebo auto-instrumentation
→ local/agent Collector
→ gateway Collector
→ tracing backend
```

Každá ďalšia vrstva pridáva buffering, latency, configuration a failure boundaries. Potrebuje vlastnú self-observability.

## 6. Jaeger v2 architektúra

Aktuálna Jaeger v2 architektúra je postavená ako distribúcia nad OpenTelemetry Collector frameworkom a jeden binary môže vykonávať rôzne roles.

Hlavné roles:

- `collector` — prijíma traces a zapisuje ich do storage,
- `query` — poskytuje query APIs a UI,
- `ingester` — číta spans z Kafka a zapisuje do storage,
- `all-in-one` — collector a query v jednom procese,
- agent role je možná, ale dokumentácia odporúča štandardný OpenTelemetry Collector pre bežný multi-signal edge model.

Jaeger collector a query sú pri external storage stateless a možno ich škálovať horizontálne.

## 7. Jaeger all-in-one

All-in-one spája ingestion, query a UI.

Vhodné pre:

- development,
- lokálne testy,
- demo,
- malé laby.

In-memory storage stráca data pri reštarte a nie je production retention model.

Single-node persistent backend môže byť vhodný iba pre bounded volume a bez očakávania horizontal scalingu.

## 8. Jaeger direct-to-storage

Model:

```text
applications/collectors
→ Jaeger collector
→ external storage
→ Jaeger query
```

Výhody:

- jednoduchšia architektúra,
- nižšia latency a menej komponentov,
- collector/query možno škálovať samostatne.

Riziká:

- storage musí absorbovať peak writes,
- krátka in-memory queue nepokryje dlhý storage outage,
- backpressure môže viesť k dropped spans,
- storage write latency ovplyvňuje ingestion.

## 9. Jaeger cez Kafka

Model:

```text
collector
→ Kafka
→ Jaeger ingester
→ storage
```

Výhody:

- durable buffer,
- oddelenie ingestion burstu od storage throughputu,
- replay,
- nezávislé scaling consumers.

Riziká:

- Kafka operations,
- partitioning a ordering,
- consumer lag,
- retention window,
- duplicate processing,
- ďalší security a cost boundary.

Kafka nie je automaticky potrebná pri každom deployment-e. Použi ju, keď durability a burst decoupling ospravedlňujú complexity.

## 10. Jaeger storage

Jaeger podporuje viacero storage backends podľa verzie a deploymentu, napríklad distributed document stores alebo databases.

Pri výbere over:

- supported version,
- index/schema lifecycle,
- write throughput,
- search latency,
- retention,
- backup/restore,
- multi-tenancy,
- encryption,
- storage cost,
- migration path.

Collector a query musia používať konzistentný storage configuration a schema contract.

## 11. Jaeger Query a UI

Query role poskytuje:

- trace lookup,
- service/operation search,
- UI,
- dependency/service performance views podľa konfigurácie,
- query APIs.

Search completeness závisí od storage indexing, sampling a time range.

Trace lookup podľa exact trace ID je iný workload než broad search podľa service, operation a attributes.

## 12. Jaeger Service Performance Monitoring

Jaeger môže odvodiť service metrics zo spans pomocou span metrics pipeline a Prometheus-compatible metrics storage.

Typické derived metrics:

- request rate,
- error rate,
- duration distributions,
- service dependencies.

Trace-derived metrics sú ovplyvnené samplingom. Ak sampled traces nereprezentujú všetok traffic, nemusia byť vhodné ako autoritatívne SLI denominator data.

## 13. Jaeger remote sampling

Jaeger podporuje centralizované remote sampling strategies pre SDKs podľa service a operation.

Modely môžu zahŕňať:

- probabilistic sampling,
- rate-limiting sampling,
- service/operation-specific policies,
- adaptive sampling podľa podporovaného storage a verzie.

Remote sampling je head-based: rozhodnutie sa robí pred poznaním finálneho outcome-u trace-u.

## 14. Tempo architektúra

Grafana Tempo je tracing backend orientovaný na object storage a integráciu s Grafanou.

Aktuálna Tempo 3.0 architektúra rozlišuje:

- monolithic mode,
- microservices mode.

V microservices mode používa Kafka-compatible queue ako durable intermediary medzi distributorom a downstream consumers. V monolithic mode Kafka nie je potrebná a komponenty komunikujú in-process.

Version-specific architektúru treba pri implementácii vždy overiť podľa používanej Tempo verzie; staršie Tempo návrhy používali odlišný ingestion lifecycle.

## 15. Tempo microservices write path

Aktuálny model:

```text
OTLP traces
→ distributor
→ validation a sharding podľa trace ID
→ Kafka-compatible queue
→ block builders
→ Parquet blocks
→ object storage
```

Write je acknowledged po durable Kafka acknowledgement podľa aktuálnej microservices architektúry.

Block builders:

- konzumujú partitions,
- skladajú spans do blocks,
- zapisujú Parquet/object-store formát,
- commitujú consumer progress.

Kafka retention musí preklenúť čas potrebný na bezpečné spracovanie a flush do object storage.

## 16. Tempo monolithic write path

Monolithic mode:

```text
distributor
→ live store in-process
→ local WAL/temporary blocks
→ object storage
```

Vhodné pre:

- development,
- menší deployment,
- jednoduchšiu prevádzku.

Nemá rovnaké independent scaling a durable queue boundaries ako microservices model.

## 17. Tempo recent a historical data

Tempo read path kombinuje:

- live stores pre recent traces,
- object storage pre historical blocks.

Query frontend:

- prijme trace ID alebo TraceQL query,
- rozdelí search na jobs,
- použije per-tenant queue,
- distribuuje prácu queriers,
- merge-ne a deduplikuje results.

Querier číta:

- recent traces z live stores,
- historical blocks z object storage.

Preto môže existovať failure mode, keď historical traces fungujú, ale recent nie, alebo naopak.

## 18. Tempo object storage

Object storage je long-term storage pre trace blocks.

Podporované hlavné APIs zahŕňajú:

- S3/S3-compatible,
- GCS,
- Azure Blob Storage,
- local filesystem pre development/test.

Trace data je organizované podľa tenantov a blocks.

Object-store cost zahŕňa:

- retained bytes,
- PUT/GET/LIST operations,
- query scans,
- compaction,
- cache,
- cross-zone/Region transfer.

Object-store lifecycle nesmie mazať blocks skôr než Tempo retention/maintenance model.

## 19. Parquet blocks

Tempo používa columnar Parquet block format pre trace data.

Výhody:

- column pruning,
- efektívnejší attribute search,
- compression,
- query parallelism.

Query performance stále závisí od:

- time range,
- attributes,
- dedicated columns,
- block count/size,
- bloom/index structures,
- object-store latency,
- cache,
- query sharding.

## 20. Backend scheduler a workers

Aktuálna Tempo maintenance architektúra používa backend scheduler a workers pre jobs ako:

- compaction,
- retention,
- redaction podľa podpory.

Workers možno horizontálne škálovať, zatiaľ čo scheduler koordinuje job assignment.

Pri migration zo staršieho Compactor modelu treba zabrániť súbežnému conflict processingu a riadiť sa version-specific upgrade dokumentáciou.

## 21. Tempo metrics-generator

Metrics-generator odvodzuje metrics zo spans.

Use cases:

- span metrics,
- service graphs,
- exemplars,
- RED metrics.

Output typicky smeruje do Prometheus-compatible metrics storage.

Riziká:

- sampled traces menia counts,
- high-cardinality span attributes vytvoria metric series explosion,
- generated metrics potrebujú retention a alert ownership,
- extra compute a queue load.

## 22. TraceQL

TraceQL je query language pre Tempo trace search.

Môže filtrovať podľa:

- resource attributes,
- span attributes,
- span duration,
- status,
- structural relationships podľa capability,
- trace-level properties.

Príklad konceptuálne:

```text
nájdi traces služby orders-api
kde downstream payment span skončil errorom
a trace trvala viac než 2 sekundy
```

Broad TraceQL search cez dlhý time range môže skenovať veľký počet blocks. Začni service, environment a časovým rozsahom.

## 23. Jaeger search oproti Tempo TraceQL

Jaeger typicky poskytuje trace lookup a search podľa service, operation, tags/attributes a time/duration filters podľa storage modelu.

Tempo poskytuje exact trace lookup a TraceQL-oriented search nad object-storage blocks.

Voľba závisí od:

- query patterns,
- storage preference,
- Grafana integration,
- existing Elasticsearch/OpenSearch/Cassandra footprint,
- multi-tenancy,
- operational skillset,
- cost,
- migration a support model.

## 24. Sampling

Sampling kontroluje volume, overhead a cost.

### Head sampling

Rozhodnutie na začiatku trace-u.

Výhody:

- nízky backend a network cost,
- jednoduché,
- SDK-level.

Limity:

- nepozná outcome,
- rare errors môžu byť zahodené,
- high-latency trace sa nedá identifikovať vopred.

### Tail sampling

Rozhodnutie po zhromaždení spans.

Môže zachovať:

- errors,
- high latency,
- specific tenants/routes,
- rare attribute combinations.

Náklady:

- všetky spans musia prísť do sampling vrstvy,
- memory/state,
- trace completeness wait,
- routing všetkých spans trace-u na konzistentný sampler,
- late spans.

### Remote/adaptive sampling

Centralizuje head-based strategies a môže meniť probabilities podľa service trafficu.

Sampling policy musí byť versionovaná, monitorovaná a testovaná.

## 25. Sampling a completeness

Sampling affects:

- trace search coverage,
- incident forensics,
- service graph,
- span metrics,
- apparent error rate,
- tenant fairness.

Sleduj:

- received spans,
- accepted spans,
- sampled/dropped traces,
- reason/policy,
- effective sampling rate per service,
- late spans,
- incomplete traces.

Nikdy nevydávaj sampled trace count za exact request count bez korekcie a reprezentatívneho sampling modelu.

## 26. Tail sampling architecture

Tail sampler potrebuje všetky spans konkrétneho trace-u smerovať na rovnakú stateful processing jednotku.

Riziká:

- load balancer bez trace-ID affinity,
- trace dlhší než decision wait,
- late spans po rozhodnutí,
- memory pressure,
- collector restart,
- policy overlap,
- dropped spans pred samplerom.

Pri horizontal scale over consistent hashing alebo gateway architecture odporúčanú Collectorom.

## 27. Trace retention

Retention musí vychádzať z:

- incident investigation window,
- sampling rate,
- compliance/privacy,
- object/index storage cost,
- search latency,
- deletion requirements,
- audit/forensic value.

Trace môže obsahovať citlivejšie údaje než metrics, pretože spans nesú detailed attributes a events.

## 28. Multi-tenancy

Tenant boundary môže ovplyvniť:

- ingest authentication,
- storage prefix/index,
- query,
- limits,
- retention,
- cache,
- sampling,
- cost allocation.

Tenant header musí vzniknúť z dôveryhodnej identity boundary. Nesmie ho voľne určovať application client bez gateway authorization.

Jaeger multi-tenancy capability závisí od deploymentu, query/storage a surrounding access layer. Tempo má explicitný tenant-oriented storage a query model podľa konfigurácie.

## 29. Security a privacy

Span attributes môžu obsahovať:

- HTTP headers,
- URLs a query parameters,
- database statements,
- RPC payload metadata,
- customer IDs,
- file paths,
- prompt/model content,
- exception stack traces,
- internal topology.

Controls:

- semantic attribute allowlist,
- redaction v SDK/Collector,
- TLS/mTLS,
- authenticated OTLP,
- tenant isolation,
- encryption at rest,
- query RBAC,
- retention/deletion,
- audit,
- data residency.

`db.statement`, HTTP bodies alebo messaging payloady sa nemajú automaticky zachytávať bez privacy a volume analýzy.

## 30. Trace-to-logs

Trace UI môže odkazovať na logs podľa:

- trace ID,
- span ID,
- service,
- timestamp window,
- resource metadata.

Potrebné je:

- vložiť trace/span ID do structured logs,
- zachovať rovnaký service/environment naming,
- query template v Grafane alebo UI,
- tenant mapping,
- timezone a clock sync.

Trace ID nemusí byť Loki label; môže byť structured metadata alebo parsed log field.

## 31. Trace-to-metrics a exemplars

Metric exemplar spája histogram sample/bucket s konkrétnym trace ID.

Workflow:

```text
latency p99 alebo SLO burn
→ exemplar
→ konkrétny trace
→ slow span/dependency
→ logs/profile
```

Exemplars potrebujú:

- compatible instrumentation,
- metrics backend support,
- trace retention,
- sampling coverage,
- UI correlation.

## 32. Service graph

Service graph možno odvodiť zo spans.

Zobrazuje napríklad:

- caller/callee edges,
- request rate,
- error rate,
- latency.

Limity:

- sampling bias,
- broken propagation,
- missing client/server spans,
- async semantics,
- duplicate spans,
- uninstrumented dependencies.

Service graph je derived view, nie autoritatívny architecture inventory.

## 33. Span naming

Operation names musia byť stabilné a bounded.

Vhodné:

- `GET /orders/{id}`,
- `payments.authorize`,
- `orders.consume`.

Nevhodné:

- raw URL s ID,
- SQL statement ako span name,
- user-controlled text,
- exception message.

Unbounded span names zvyšujú search index/cardinality, UI noise a metrics-generator series.

## 34. Attribute governance

Attributes klasifikuj:

- required semantic conventions,
- bounded operational dimensions,
- high-cardinality correlation fields,
- sensitive fields,
- debug-only fields.

Urči:

- kde sa field vytvára,
- či je indexed/searchable,
- retention,
- redaction,
- sampling use,
- metric promotion zákaz/povolenie.

## 35. Self-monitoring

Monitoruj tracing pipeline:

- SDK export errors,
- Collector accepted/refused/dropped spans,
- queue size/capacity,
- tail-sampling state/drops,
- backend ingestion rate/errors,
- Kafka lag/retention pri použití,
- storage writes/errors,
- live-store/recent-data health,
- block builder throughput,
- query rate/latency/errors,
- object-store requests,
- compaction/retention backlog,
- trace search scanned bytes,
- process CPU/memory/GC,
- tenant limits.

Doplň synthetic trace cez viac services a over exact trace ID lookup.

## 36. Troubleshooting: trace sa nenájde

```text
trace bol sampled?
→ SDK vytvoril spans?
→ export error?
→ context/trace ID?
→ Collector receiver?
→ filter/tail sampler drop?
→ exporter queue/retry?
→ backend tenant?
→ ingestion acknowledgement?
→ recent alebo historical path?
→ správny time range?
→ exact trace ID format?
```

Zachovaj trace ID, service/version, timestamp, SDK/Collector metrics a backend ingest evidence.

## 37. Troubleshooting: broken trace

Symptómy:

- viac roots,
- missing child spans,
- orphan spans,
- nesprávne duration overlap,
- oddelené traces pre jednu operation.

Over:

- propagation inject/extract,
- async context,
- message headers,
- parent span lifecycle,
- client/server instrumentation duplication,
- sampling consistency,
- clock skew,
- late spans.

Backend visualization nie je primárna príčina chýbajúceho parent ID.

## 38. Troubleshooting: recent traces nefungujú, historical áno

Tempo:

- live stores,
- Kafka consumer offsets,
- partition ring,
- recent-data query path,
- distributor ingestion.

Jaeger:

- collector/storage visibility,
- refresh/indexing latency,
- query time range,
- direct vs buffered ingestion.

## 39. Troubleshooting: historical traces nefungujú, recent áno

Over:

- block flush/build,
- object storage alebo external storage,
- index/schema,
- compaction/blocklist,
- lifecycle/retention,
- KMS/permissions,
- query tier/cache.

## 40. Troubleshooting: slow trace search

Over:

- exact trace lookup alebo attribute search,
- time range,
- tenant,
- service/operation filters,
- indexed/promoted attributes,
- block/shard count,
- object-store latency,
- search parallelism,
- query queue,
- storage heap/CPU,
- result limit,
- UI timeout.

Exact trace ID lookup by mal byť diagnostikovaný oddelene od broad search.

## 41. Troubleshooting: dropped spans

Možné vrstvy:

- SDK queue full,
- exporter timeout,
- Collector memory limiter,
- batch queue,
- tail-sampling capacity,
- rate limit,
- Kafka/backlog,
- storage rejection,
- invalid span,
- max message size.

Sleduj counters na každom hop-e. Bez per-hop accepted/dropped metrics sa strata nedá lokalizovať.

## 42. Troubleshooting: Kafka lag v trace pipeline

Over:

- producer rate,
- partitions,
- consumer group,
- block builder/ingester throughput,
- storage latency,
- rebalance,
- retention headroom,
- disk/network,
- poison/oversized messages.

Lag väčší než retention window môže viesť k strate nespracovaných trace records.

## 43. Troubleshooting: object-store cost rastie

Over:

- ingestion bytes,
- sampling rate,
- retention,
- block size/compaction,
- query scans,
- cache hit ratio,
- promoted attributes,
- tenant abuse,
- cross-zone/Region transfer,
- LIST/GET request rate.

Zníženie sampling rate bez investigation requirements analýzy môže odstrániť rare failures.

## 44. Jaeger oproti Tempo

### Jaeger

Vhodný, keď:

- chceš Jaeger UI a ecosystem,
- používaš supported external storage,
- potrebuješ direct-to-storage alebo Kafka-ingester model,
- máš existujúci Elasticsearch/OpenSearch/Cassandra skillset,
- potrebuješ Jaeger remote sampling.

### Tempo

Vhodný, keď:

- preferuješ object-storage-first tracing,
- používaš Grafana stack,
- chceš TraceQL,
- potrebuješ nezávislé read/write scaling,
- chceš span metrics/service graph integráciu s Prometheus-compatible backendom.

Výber testuj na reálnom:

- ingest volume,
- attribute search,
- retention,
- tail sampling,
- query latency,
- failure recovery,
- operational cost.

## 45. Anti-patterny

### Trace všetkého bez sampling a attribute governance

Backend, network a storage cost rastie nekontrolovane.

### Head sampling 1 % a očakávanie všetkých errors

Rare failures môžu byť zahodené.

### Tail sampling bez trace-ID-aware routing

Spans jedného trace-u sa rozdelia a rozhodnutia budú neúplné.

### Raw URL alebo SQL ako span name

Vytvára high cardinality a sensitive data exposure.

### Trace-derived metrics ako exact SLI bez sampling analýzy

Counts a ratios môžu byť biased.

### All-in-one in-memory deployment označený ako production HA

Data sa stratia pri reštarte a nie je independent failure domain.

### Object-store lifecycle mimo Tempo retention

Môže zmazať blocks nekonzistentne.

### Collector bez self-monitoringu

Dropped spans sa prejavia iba ako chýbajúce traces.

## 46. Kontrolné otázky

1. Čo musí obsahovať span a ako sa skladá trace?
2. Prečo context propagation určuje trace continuity?
3. Aké roles používa Jaeger v2?
4. Kedy použiť direct-to-storage a kedy Kafka?
5. Ako sa líši Tempo monolithic a microservices write path?
6. Na čo slúžia live stores a object storage?
7. Ako sa líši head a tail sampling?
8. Prečo tail sampling potrebuje trace-ID-aware routing?
9. Ako sampling ovplyvňuje span metrics a service graph?
10. Ako funguje trace-to-logs a exemplar workflow?
11. Ako diagnostikuješ missing trace?
12. Kedy zvoliť Jaeger a kedy Tempo?

## Glossary impact

Relevantné pojmy: Jaeger, Jaeger collector, Jaeger query, Jaeger ingester, Jaeger all-in-one, Jaeger remote sampling, direct-to-storage tracing, Kafka-buffered tracing, Tempo, Tempo distributor, Kafka-compatible trace WAL, block builder, live store, Parquet trace block, query frontend, TraceQL, backend scheduler, backend worker, metrics-generator, span metrics, service graph, head sampling, tail sampling, adaptive sampling, trace completeness, trace-to-logs, exemplar a trace attribute governance.

## Primárne zdroje

- [Jaeger v2 architecture](https://www.jaegertracing.io/docs/2.20/architecture/)
- [Jaeger deployment](https://www.jaegertracing.io/docs/2.20/deployment/)
- [Jaeger sampling](https://www.jaegertracing.io/docs/2.20/architecture/sampling/)
- [Jaeger storage](https://www.jaegertracing.io/docs/2.20/storage/)
- [Jaeger Service Performance Monitoring](https://www.jaegertracing.io/docs/2.20/architecture/spm/)
- [Tempo architecture](https://grafana.com/docs/tempo/latest/reference-tempo-architecture/about-tempo-architecture/)
- [Tempo object storage](https://grafana.com/docs/tempo/latest/reference-tempo-architecture/object-storage/)
- [Tempo query frontend](https://grafana.com/docs/tempo/latest/reference-tempo-architecture/components/query-frontend/)
- [Tempo TraceQL](https://grafana.com/docs/tempo/latest/traceql/)
- [OpenTelemetry sampling](https://opentelemetry.io/docs/concepts/sampling/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Fluent Bit](fluent-bit.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CIA triáda →](../13-security-and-identity/cia-triad.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
