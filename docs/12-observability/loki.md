# Loki

Grafana Loki je log aggregation systém navrhnutý okolo streamov identifikovaných bounded label setom. Na rozdiel od plnotextových search engine-ov typicky neindexuje celý obsah každej log line. Indexuje najmä metadata streamu a samotné log lines ukladá komprimované do chunks. Tento model môže výrazne znížiť index cost, ale vyžaduje disciplinovaný label contract a query workflow.

Loki nie je univerzálna databáza dokumentov, SIEM, message broker ani náhrada structured loggingu. Je to backend na ingest, retention a query log telemetry, ktorý dobre zapadá do Grafana, Prometheus a OpenTelemetry ekosystému.

## 1. Mentálny model

```text
application/container/system logs
→ collector alebo agent
→ parsing, enrichment a redaction
→ tenant + bounded labels + timestamp + log line
→ distributor
→ ingestion path
→ compressed chunks + TSDB index v object storage
→ LogQL query
→ query frontend/scheduler/querier
→ Grafana Explore, dashboard alebo alert rule
```

Loki query model najprv zúži streamy podľa labels a až potom filtruje alebo parsuje obsah log lines.

## 2. Log stream

Log stream je množina log entries s rovnakým tenant ID a rovnakým úplným label setom.

Príklad:

```text
{service="orders-api", environment="production", cluster="eu1"}
```

Každá zmena label value vytvára iný stream.

Log entry typicky obsahuje:

- nanosecond timestamp,
- textovú alebo structured log line,
- voliteľné structured metadata,
- stream labels,
- tenant context.

## 3. Labels

Labels sú indexované metadata používané na výber streamov.

Vhodné labels:

- `service`,
- `environment`,
- `cluster`,
- `namespace`,
- bounded `level`,
- `region`,
- stabilný workload alebo component name.

Rizikové labels:

- request ID,
- trace ID,
- user ID,
- order ID,
- full URL,
- exception message,
- container ID pri nekontrolovanom churn-e,
- filename s neobmedzeným počtom hodnôt.

Label cardinality ovplyvňuje:

- počet streamov,
- index size,
- ingester memory,
- chunk utilization,
- query fan-out,
- compaction,
- object-store operations.

V Loki je zvyčajne lepšie ponechať high-cardinality field v structured log body alebo structured metadata a queryovať ho až po výbere bounded streamov.

## 4. Structured metadata

Structured metadata umožňuje pripojiť ku log entry key/value fields bez toho, aby sa stali stream labels.

Vhodné použitie:

- trace ID,
- span ID,
- request ID,
- user alebo business identifier v súlade s privacy policy,
- Kubernetes Pod identity,
- dynamically changing attributes.

Structured metadata nie je zadarmo. Stále zvyšuje payload, storage a query cost, ale nevytvára nový stream pri každej hodnote.

## 5. Log body

Log body má byť ideálne structured, napríklad JSON:

```json
{
  "timestamp": "2026-07-21T20:00:00Z",
  "level": "error",
  "event": "payment.authorization.failed",
  "message": "Payment provider timed out",
  "trace_id": "...",
  "provider": "payments-a",
  "duration_ms": 2500,
  "error_code": "UPSTREAM_TIMEOUT"
}
```

Collector môže body parsovať a vybrané stabilné fields povýšiť na labels. Neindexuj automaticky každý JSON field.

## 6. Loki storage model

Loki ukladá dva hlavné typy dát:

- **index** — mapuje label sets a časové rozsahy na chunks,
- **chunks** — komprimované log entries konkrétneho streamu za časový interval.

Moderný production model používa object storage pre index aj chunks.

Aktuálna dokumentácia odporúča TSDB index store. Staršie BoltDB-based index paths sú legacy alebo deprecated a nové storage features sa sústreďujú na TSDB model.

Object storage môže byť napríklad:

- Amazon S3,
- Google Cloud Storage,
- Azure Blob Storage,
- kompatibilný object store podľa podporovaného modelu.

Filesystem backend je vhodný najmä pre lokálny development alebo jednoduché single-instance prostredie; sám neposkytuje production durability a independent recovery boundary.

## 7. Schema configuration

Loki schema určuje:

- od ktorého dátumu platí storage schema,
- index store,
- object store,
- schema version,
- index prefix a period.

Schema migration musí byť dopredne kompatibilná s existujúcimi dátami.

Typický model:

```text
staršie obdobie → stará schema zostáva čitateľná
novší dátum     → nová schema sa používa pre nové writes
```

Nemeň historický `from` dátum bez migration plánu. Chybná schema configuration môže spôsobiť, že nové alebo staré logy sa javia ako chýbajúce.

## 8. Deployment modes

Loki je zostavený z komponentov, ktoré možno spustiť v jednom procese alebo oddelene.

### Single binary

Všetky hlavné roles bežia v jednom procese.

Vhodné pre:

- development,
- laby,
- malé prostredia,
- jednoduchý operational model.

Limity:

- spoločný failure domain,
- obmedzené nezávislé scaling,
- menšia isolation read/write paths.

### Distributed alebo microservices deployment

Komponenty bežia oddelene a škálujú sa podľa write, read a backend potreby.

Aktuálne Loki dokumenty treba pri návrhu kontrolovať, pretože deployment modes sa vyvíjajú. Simple Scalable Deployment je v aktuálnej dokumentácii označený ako deprecated a plánovaný na odstránenie v Loki 4.0. Nový production návrh preto nemá slepo kopírovať starší `read/write/backend` chart bez overenia aktuálne odporúčaného modelu.

## 9. Write path

Typický write path zahŕňa:

1. client alebo collector odošle batch log entries,
2. gateway overí access a smeruje request,
3. distributor validuje tenant, limits, labels a timestamps,
4. hash/ring určí ingestion ownership,
5. ingesters prijmú entries,
6. entries sa agregujú do chunks,
7. chunks a index blocks sa flushnú do object storage.

Podľa deploymentu a verzie môžu byť medzi komponentmi ďalšie durable alebo coordination vrstvy. Pri prevádzke sa riaď aktuálnou architektúrou použitej Loki verzie.

## 10. Ingester

Ingester drží recent log data a vytvára chunks.

Prevádzkové riziká:

- memory pressure,
- príliš veľa active streams,
- small underutilized chunks,
- out-of-order entries,
- WAL alebo local-disk pressure podľa konfigurácie,
- object-store flush failures,
- ring membership problémy.

Sleduj:

- active streams,
- ingested bytes/lines,
- rejected entries,
- chunk utilization,
- flush duration/failures,
- WAL recovery,
- ring health.

## 11. Distributor a limits

Distributor môže aplikovať:

- authentication/tenant resolution,
- rate limits,
- line-size limits,
- label validation,
- stream count limits,
- timestamp age/future checks,
- per-tenant overrides.

HTTP success collectora nepreukazuje, že všetky log entries boli prijaté. Agent musí monitorovať response codes a retry/drop counters.

## 12. Read path

Typický read path:

```text
LogQL query
→ query frontend
→ query splitting a caching
→ query scheduler
→ queriers
→ recent data z ingesters/live path
→ historical chunks/index z object storage
→ merge a deduplication
→ client/Grafana
```

Query frontend môže:

- splitovať dlhý time range,
- paralelizovať prácu,
- cachovať výsledky,
- enforce-nuť limits,
- retryovať subqueries,
- zlučovať výsledky.

Pomalý query nemusí byť problém Grafany. Môže ísť o broad stream selector, príliš dlhý časový rozsah, parser nad veľkým objemom lines, object-store latency alebo nedostatočný query parallelism.

## 13. LogQL

LogQL kombinuje stream selection, line filtering, parsing a metric queries nad logs.

### Stream selector

```logql
{service="orders-api", environment="production"}
```

Selector má čo najskôr zúžiť tenant, service a environment.

### Line filter

```logql
{service="orders-api"} |= "timeout"
```

Negatívny filter:

```logql
{service="orders-api"} != "healthcheck"
```

Regex používaj opatrne; broad regex nad veľkým časovým rozsahom môže byť drahý.

### JSON parser

```logql
{service="orders-api"} | json
```

Následný field filter:

```logql
{service="orders-api"}
| json
| level="error"
| duration_ms > 1000
```

### Pattern alebo logfmt parser

Použiteľný pre stabilné textové/logfmt schemas. Parser failure musí byť viditeľný; inak sa query môže ticho opierať o neexistujúce fields.

### Metric query z logs

```logql
sum by (service) (
  rate({environment="production"} |= "ERROR" [5m])
)
```

Log-derived metric má odlišné completeness a cost properties než native application metric.

## 14. `unwrap`

`unwrap` umožňuje extrahovať numerickú hodnotu z parsed log field a vytvoriť range aggregation.

Príklad:

```logql
quantile_over_time(
  0.95,
  {service="orders-api"}
  | json
  | unwrap duration_ms [5m]
)
```

Over:

- parse errors,
- units,
- missing fields,
- outliers,
- whether log sampling mení distribution.

Pre SLO latency je často vhodnejší native histogram než výpočet z sampled logs.

## 15. Recording a alerting rules

Loki ruler môže vyhodnocovať LogQL rules.

Použitie:

- error pattern alert,
- audit event detection,
- log-derived metric recording,
- absence/freshness signal podľa modelu.

Rules majú mať:

- bounded query,
- stabilné labels,
- ownership,
- explicitný time window,
- no-data semantics,
- links na log query a runbook.

Nevytváraj page alert na každú jednotlivú error log line. Alertuj na user impact, security event alebo sustained failure pattern.

## 16. Multi-tenancy

Loki môže oddeliť dáta podľa tenant ID.

Tenant boundary ovplyvňuje:

- ingestion,
- query,
- limits,
- retention,
- cache keys,
- storage prefix,
- authorization.

Samotný `X-Scope-OrgID` header nie je security boundary, ak ho môže nedôveryhodný client voľne nastavovať. Gateway musí tenant identity odvodiť z autentizovanej identity alebo dôveryhodnej routing vrstvy.

## 17. Retention a deletion

Retention pri object-storage modeli typicky vykonáva Compactor alebo aktuálna maintenance vrstva.

Potrebné je nakonfigurovať:

- retention enablement,
- global alebo per-tenant/per-stream periods,
- delete delay,
- object-store lifecycle compatibility,
- compactor working state,
- delete request storage podľa modelu.

Object-store lifecycle policy nesmie mazať chunks alebo index skôr, než Loki retention model očakáva. Inak vzniknú index references na neexistujúce objekty alebo nečitateľné historické obdobia.

Log deletion môže byť nákladná a version-specific. Pri compliance use case-e over aktuálnu podporu, scaling status a audit evidence.

## 18. Compaction

Compaction zlučuje index blocks a podporuje retention/deletion lifecycle.

Sleduj:

- compaction backlog,
- failed operations,
- object-store API errors,
- working disk,
- tenant distribution,
- delete processing,
- singleton alebo horizontal-scaling status podľa používanej verzie.

Experimentálne horizontálne škálovanie Compactoru nepovažuj automaticky za stabilný production default bez overenia verzie.

## 19. Caching

Loki môže používať caches pre:

- query results,
- index/chunk metadata,
- frontend results,
- object-store reads podľa deploymentu.

Cache ovplyvňuje latency a object-store cost, ale môže skryť backend degradation.

Sleduj:

- hit ratio,
- evictions,
- memory,
- request latency,
- cache consistency boundaries,
- tenant isolation,
- stampede behavior.

## 20. Log collectors

Loki môže prijímať logs z rôznych collectors, napríklad:

- Fluent Bit,
- Grafana Alloy,
- OpenTelemetry Collector,
- cloud/service integrations,
- custom clients.

Collector zodpovedá za:

- source read position,
- multiline reconstruction,
- parsing,
- Kubernetes metadata,
- redaction,
- buffering,
- retries,
- tenant a label mapping.

Loki backend nevie obnoviť log lines, ktoré collector nikdy neprečítal alebo dropol.

## 21. Kubernetes deployment

Typický model:

```text
container stdout/stderr
→ CRI log files na Node
→ DaemonSet collector
→ Loki gateway/distributor
→ object storage
→ Grafana
```

Dôležité boundaries:

- hostPath access ku container log files,
- position database,
- log rotation,
- multiline,
- Kubernetes metadata API/RBAC,
- namespace/tenant mapping,
- collector resource limits,
- network policy,
- object-store identity.

Pod logs v `kubectl logs` môžu existovať, zatiaľ čo Loki ich nemá, ak collector tail path, permissions alebo position state zlyhali.

## 22. Security a privacy

Logs môžu obsahovať:

- credentials,
- tokens,
- personal data,
- request/response bodies,
- SQL queries,
- internal topology,
- source code paths,
- prompt/model inputs.

Controls:

- producer-side minimization,
- collector redaction,
- TLS,
- authenticated tenant gateway,
- object-store encryption,
- least privilege,
- query audit,
- retention a deletion,
- data residency,
- separate audit-log boundary.

Redaction iba v Grafana UI je neskoro.

## 23. Self-monitoring

Monitoruj Loki ako kritickú platformu:

- ingestion request rate/errors,
- accepted/rejected bytes a lines,
- active streams,
- chunk flush latency/errors,
- object-store requests/errors,
- query rate/latency/errors,
- scheduler queues,
- cache hit ratio,
- compaction/retention backlog,
- ruler evaluation,
- ring health,
- process CPU/memory/GC,
- tenant limit violations.

Doplň synthetic log:

```text
periodicky emitni unikátny bounded canary event
→ over collector ingest
→ over Loki query availability
→ over end-to-end latency
```

Canary ID nesmie byť label s neobmedzenou cardinality.

## 24. Troubleshooting: chýbajúce logy

```text
source log reálne vznikol?
→ správny Node/container/file?
→ collector tail path a permissions?
→ position database?
→ rotation/inode behavior?
→ multiline/parser/filter drop?
→ tag/route/output match?
→ Loki response code a retry?
→ tenant ID?
→ labels a timestamp validity?
→ schema/object store?
→ správny LogQL selector/timezone?
```

Zachovaj sample line, timestamp, source file inode, collector metrics/logs, batch response a exact query.

## 25. Troubleshooting: query je pomalý

Over:

- tenant a time range,
- stream selector selectivity,
- regex/line filters,
- parser a `unwrap`,
- bytes scanned,
- query splitting,
- querier concurrency,
- scheduler queue,
- cache,
- object-store latency,
- active streams/cardinality,
- Grafana query interval.

Najprv zúž selector a time range. Nepridávaj queriers bez pochopenia, či bottleneckom nie je object store alebo extrémny stream fan-out.

## 26. Troubleshooting: rejected entries

Bežné príčiny:

- ingestion rate limit,
- stream limit,
- príliš dlhá line,
- príliš veľa labels,
- invalid label name/value,
- timestamp príliš starý alebo v budúcnosti,
- out-of-order policy,
- tenant authentication,
- request size.

Collector musí rozlišovať retryable a permanent errors. Nekonečný retry permanentne invalidného batchu blokuje queue.

## 27. Troubleshooting: vysoká cardinality

Symptómy:

- rast active streams,
- ingester memory,
- malé chunks,
- pomalé queries,
- index/object-store cost,
- stream-limit rejections.

Postup:

1. identifikuj label names s najväčším počtom values,
2. nájdi producer alebo collector mapping,
3. presuň dynamic field do structured metadata/body,
4. rollout-ni zmenu,
5. počkaj na lifecycle starých streamov,
6. over chunk utilization a query latency.

Odstránenie labelu z nových logs okamžite neodstráni historické streamy.

## 28. Troubleshooting: recent logs existujú, historical nie

Over:

- chunk flush,
- object-store writes,
- schema period,
- index gateway/cache,
- compactor,
- object-store lifecycle,
- retention,
- permissions/KMS,
- query time range.

## 29. Troubleshooting: historical logs existujú, recent nie

Over:

- distributor/ingester health,
- ring ownership,
- recent-data query path,
- collector ingest,
- current tenant limits,
- clock skew.

## 30. Loki oproti Elasticsearch/OpenSearch

### Loki

Silné stránky:

- label-based index,
- object-storage-first model,
- integrácia s Grafana/Prometheus,
- efektívny cost pri disciplinovaných labels,
- LogQL a log-derived metrics.

### Elasticsearch/OpenSearch

Silné stránky:

- indexovanie document fields,
- full-text search,
- komplexné aggregations,
- širší search/analytics use case,
- mature document mapping a search semantics.

Voľba závisí od:

- query patterns,
- field search požiadaviek,
- ingestion volume,
- retention,
- operational skillset,
- compliance,
- cost,
- ecosystem integrations.

Nesnaž sa emulovať Elasticsearch tým, že každý field spravíš Loki labelom.

## 31. Anti-patterny

### High-cardinality labels

Request alebo user identity vytvára stream explosion.

### Broad selector `{environment="production"}` na 30 dní

Query skenuje veľký počet streams a chunks.

### Parser v každom dashboard paneli nad raw JSON

Opakované drahé parsing; zváž stabilnejšiu schema, derived metric alebo recording rule.

### Object-store lifecycle nezávislý od Loki retention

Môže mazať dáta pred indexom alebo opačne.

### Collector bez filesystem bufferu pri kritických logs

Backend outage môže viesť k strate podľa input semantics.

### Audit logs v rovnakom tenante a access modeli ako application logs

Compromise workloadu alebo broad user access poškodí evidence boundary.

### Single binary s local filesystemom označený ako HA

Nemá independent replicas ani durable object-store recovery.

## 32. Kontrolné otázky

1. Čo Loki indexuje a čo ukladá do chunks?
2. Ako label set vytvára log stream?
3. Prečo trace ID nepatrí medzi bežné Loki labels?
4. Na čo slúži structured metadata?
5. Ako funguje write a read path?
6. Prečo je TSDB index store aktuálne preferovaný?
7. Ako schema periods ovplyvňujú upgrade?
8. Ako sa líši LogQL stream selector, line filter a parser?
9. Čo rieši Compactor?
10. Ako multi-tenancy súvisí s autentizáciou?
11. Ako diagnostikuješ chýbajúce logs?
12. Kedy je vhodnejší Elasticsearch alebo OpenSearch?

## Glossary impact

Relevantné pojmy: Loki, log stream, stream selector, Loki labels, structured metadata, chunk, TSDB index store, schema period, distributor, ingester, query frontend, query scheduler, querier, LogQL, line filter, parser, `unwrap`, Loki ruler, tenant ID, Compactor, Loki retention, active stream, chunk utilization a log canary.

## Primárne zdroje

- [Loki architecture](https://grafana.com/docs/loki/latest/get-started/architecture/)
- [Loki storage](https://grafana.com/docs/loki/latest/operations/storage/)
- [Configure Loki storage](https://grafana.com/docs/loki/latest/configure/storage/)
- [LogQL](https://grafana.com/docs/loki/latest/query/)
- [Loki components](https://grafana.com/docs/loki/latest/get-started/components/)
- [Loki deployment modes](https://grafana.com/docs/loki/latest/get-started/deployment-modes/)
- [Loki retention](https://grafana.com/docs/loki/latest/operations/storage/retention/)
- [Loki limits](https://grafana.com/docs/loki/latest/operations/request-validation-rate-limits/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Grafana](grafana.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Elasticsearch alebo OpenSearch →](elasticsearch-opensearch.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
