# Observability logs and tracing glossary entries

## Active stream — Loki

Log stream, pre ktorý Loki ingester aktuálne drží alebo spracúva recent entries; veľký počet active streams zvyšuje memory a chunk overhead. Pozri [Loki](docs/12-observability/loki.md).

## Adaptive sampling — tracing

Sampling model, ktorý priebežne upravuje head-sampling probabilities podľa pozorovaného trafficu a target volume-u. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Analyzer — search

Komponent Lucene-based search engine-u, ktorý tokenizuje a normalizuje text pri indexing alebo query time. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Backing index

Skrytý fyzický index patriaci data streamu; writes smerujú do aktuálneho write backing indexu a searches prechádzajú všetky relevantné generations. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Backend scheduler — Tempo

Tempo component, ktorý plánuje maintenance jobs ako compaction, retention alebo redaction a prideľuje ich backend workers. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Backend worker — Tempo

Tempo component vykonávajúci maintenance jobs pridelené backend schedulerom nad object-storage blocks. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Block builder — Tempo

Component, ktorý konzumuje trace records z durable queue, skladá ich do Parquet blocks a zapisuje do object storage. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Bulk API

Search-engine API na odoslanie viacerých indexing/update/delete operations v jednom requeste; response môže obsahovať partial item failures aj pri úspešnom HTTP statuse. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Chunk — Fluent Bit

Interná jednotka zoskupujúca telemetry records na buffering, routing a output flush. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Chunk — Loki

Komprimovaný container log entries jedného streamu za určitý časový interval uložený typicky v object storage. Pozri [Loki](docs/12-observability/loki.md).

## Chunk utilization — Loki

Miera naplnenia Loki chunks; príliš veľa malých streamov vytvára underutilized chunks a zvyšuje storage/index overhead. Pozri [Loki](docs/12-observability/loki.md).

## Component template — search

Reusable časť index template-u obsahujúca mappings, settings alebo aliases pre Elasticsearch/OpenSearch index model podľa produktu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Data Stream Lifecycle — Elasticsearch

Elasticsearch lifecycle mechanizmus na retention a správu backing indexes data streamu podľa podporovaného deployment modelu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Data stream — search

Logical abstraction nad rolling backing indexes optimalizovaná pre timestamped a prevažne append-only data ako logs, events a metrics. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Direct-to-storage tracing

Jaeger deployment model, v ktorom collectors zapisujú traces priamo do external storage bez durable Kafka bufferu. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Disk watermark — search cluster

Threshold disk usage ovplyvňujúci shard allocation, relocation alebo write blocks v Elasticsearch/OpenSearch clusteri. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Document — search

JSON objekt uložený v Elasticsearch/OpenSearch indexe a spracovaný podľa mappingu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Dynamic mapping

Automatické vytváranie field mappings podľa prichádzajúcich documents; bez governance môže spôsobiť schema conflicts a mapping explosion. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Elasticsearch

Distribuovaný search, analytics a document-store systém založený na Apache Lucene. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Exemplar

Reference z metric sample alebo histogram observation na konkrétny trace ID, ktorá umožňuje prechod z agregovanej metriky na trace. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Filesystem buffering — Fluent Bit

Buffering telemetry chunks na local filesystem na zvýšenie backlog capacity a restart recovery oproti memory-only modelu. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Fluent Bit

Ľahký telemetry agent na inputs, parsing, filtering, buffering, routing a export logs, metrics a traces. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Graceful shutdown — telemetry agent

Riadené ukončenie inputov, flush queued chunks a uloženie offset state-u pred zastavením agenta. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Index — search

Logical collection documents s vlastným mappingom, settings a shard topology. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Index State Management — ISM

OpenSearch policy framework na riadenie index lifecycle-u cez states, transitions a actions. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Index template

Policy aplikovaná na nové indexes alebo backing indexes podľa patternu, ktorá definuje mappings, settings a lifecycle integration. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Ingest pipeline — search

Server-side pipeline, ktorá pred indexingom parsuje, normalizuje, enrichuje, rediguje alebo routuje documents. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Ingester — Loki

Loki write-path component, ktorý prijíma recent log entries, drží active streams a vytvára chunks pred flushom do storage. Pozri [Loki](docs/12-observability/loki.md).

## Jaeger

Distributed tracing backend s collector, query, ingester a all-in-one roles, aktuálne postavený na OpenTelemetry Collector frameworku. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Jaeger all-in-one

Jaeger deployment role spájajúca collector a query/UI v jednom procese, vhodná najmä pre development a bounded use cases. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Jaeger collector

Jaeger role prijímajúca trace data a zapisujúca ich do storage alebo durable queue podľa deploymentu. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Jaeger ingester

Jaeger role, ktorá konzumuje spans z Kafka a zapisuje ich do trace storage. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Jaeger query

Jaeger role poskytujúca query APIs a user interface nad trace storage. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Jaeger remote sampling

Centralizovaný head-sampling model, v ktorom SDKs získavajú sampling strategies z Jaeger backendu. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Kafka-buffered tracing

Tracing architecture, v ktorej durable Kafka-compatible queue oddeľuje trace ingestion od storage consumers. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## `keyword` field

Search field type určený na exact matching, sorting a aggregations bez full-text analysis. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Log canary

Periodicky generovaný synthetic log event používaný na overenie end-to-end collection, ingestion, storage a query latency. Pozri [Loki](docs/12-observability/loki.md).

## Log loss boundary

Konkrétny stav, pri ktorom telemetry pipeline môže zahodiť logs, napríklad full buffer, volatile crash, permanent output error alebo odstránený file pred dočítaním. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Log replay

Opätovné načítanie a odoslanie log records po reštarte, offset strate alebo backlog recovery, ktoré môže vytvoriť duplicates. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Log stream — Loki

Množina log entries s rovnakým tenant ID a úplným label setom. Pozri [Loki](docs/12-observability/loki.md).

## LogQL

Loki query language kombinujúci stream selectors, line filters, parsing a metric aggregations nad logs. Pozri [Loki](docs/12-observability/loki.md).

## Loki

Label-indexed log aggregation systém ukladajúci log body komprimovane v chunks a používajúci object-storage-oriented storage model. Pozri [Loki](docs/12-observability/loki.md).

## Loki Compactor

Maintenance component, ktorý compactuje index blocks a podľa konfigurácie vykonáva retention a log deletion lifecycle. Pozri [Loki](docs/12-observability/loki.md).

## Loki labels

Bounded metadata tvoriace identity log streamov a indexovaný výberový priestor pre LogQL. Pozri [Loki](docs/12-observability/loki.md).

## Loki retention

Policy a maintenance proces určujúci, ako dlho sa log chunks a index data uchovávajú a kedy sa bezpečne odstránia. Pozri [Loki](docs/12-observability/loki.md).

## Loki ruler

Component vyhodnocujúci LogQL recording alebo alerting rules. Pozri [Loki](docs/12-observability/loki.md).

## Lucene

Search library tvoriaca základ Elasticsearch a OpenSearch shards a segment-based indexing/search modelu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Mapping — search

Schema určujúca field names, types, analyzers a object structure dokumentov v indexe. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Mapping explosion

Nekontrolovaný rast počtu mapped fields, často spôsobený dynamic keys alebo nekonzistentnými documents, ktorý zvyšuje cluster-state a heap overhead. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Memory buffering — Fluent Bit

Dočasné držanie telemetry chunks v RAM; poskytuje nízku latency, ale obmedzenú capacity a slabšiu crash durability. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Metrics-generator — Tempo

Tempo component, ktorý odvodzuje span metrics, service graphs a ďalšie metrics z ingestovaných traces. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Multiline parser

Parser rekonštruujúci viac fyzických log lines do jedného logical recordu, napríklad stack trace-u. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Near-real-time search

Search model, v ktorom acknowledged document nemusí byť okamžite viditeľný, kým neprebehne refresh. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## OpenSearch

Distribuovaný search a analytics systém založený na Apache Lucene s vlastným plugin, security a lifecycle ekosystémom. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Output plugin — Fluent Bit

Plugin odosielajúci routed telemetry records do konkrétneho backendu alebo destination. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Parquet trace block

Columnar Tempo storage block obsahujúci traces a attributes v Apache Parquet formáte pre efektívnejšie selective querying. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Position database — Fluent Bit

Persistentný state Tail inputu uchovávajúci file identity a read offset na restart a rotation recovery. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Primary shard

Autoritatívna shard kópia subsetu documents, z ktorej sa koordinuje replication. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Query frontend — Loki

Read-path component, ktorý prijíma LogQL queries, splituje ich, aplikuje caching/limits a zlučuje výsledky. Pozri [Loki](docs/12-observability/loki.md).

## Query frontend — Tempo

Read-path component, ktorý sharduje trace lookup alebo TraceQL search na jobs, distribuuje ich queriers a zlučuje výsledky. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Query scheduler — Loki

Component koordinujúci a frontujúci query work medzi query frontendmi a queriers. Pozri [Loki](docs/12-observability/loki.md).

## Querier — Loki

Component vykonávajúci LogQL subqueries nad recent ingestion state-om a historical object-storage dátami. Pozri [Loki](docs/12-observability/loki.md).

## Refresh — search

Operácia sprístupňujúca nové Lucene segments pre search; nie je totožná s durable flushom alebo backupom. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Replica shard

Kópia primary shardu poskytujúca redundancy a read capacity, ale nie ochranu pred logical corruption alebo deletion. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Retry queue — Fluent Bit

Queue chunks čakajúcich na opakovaný output flush po retryable failure. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Rollover — search

Lifecycle operácia vytvárajúca nový write index po splnení age, size, document-count alebo shard-size conditions. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Schema period — Loki

Časovo ohraničená Loki storage schema configuration používaná na forward-compatible zmenu index/storage formátu pre nové dáta. Pozri [Loki](docs/12-observability/loki.md).

## Segment — Lucene

Immutable index fragment v rámci shardu; nové documents sa sprístupňujú refreshom a segments sa neskôr zlučujú merge procesom. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Service graph

Derived graph caller/callee relationships a performance characteristics vytvorený zo spans; jeho úplnosť závisí od instrumentation a sampling coverage. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Shard allocation

Rozhodovanie search clusteru, na ktorom node a failure domain-e budú umiestnené primary a replica shard copies. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Stream selector — LogQL

Label matcher expression, ktorá vyberie Loki log streamy pred line filteringom a parsingom. Pozri [Loki](docs/12-observability/loki.md).

## Structured metadata — Loki

Per-entry key/value metadata uložené bez vytvorenia novej stream identity, vhodné pre high-cardinality correlation fields. Pozri [Loki](docs/12-observability/loki.md).

## Tail input — Fluent Bit

Input plugin sledujúci log files, ich offsets a rotation lifecycle. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Tempo

Object-storage-oriented distributed tracing backend s TraceQL, Grafana integráciou a oddeleným write/read lifecycle-om. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Tempo distributor

Write-path component prijímajúci trace data, validujúci limits a sharding records podľa trace ID. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Tempo live store

Read-path component poskytujúci recent trace data pred alebo nezávisle od ich historical object-storage availability. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Tenant ID — Loki

Identifier oddeľujúci ingestion, storage, query a limits jednotlivých Loki tenantov. Pozri [Loki](docs/12-observability/loki.md).

## `text` field

Search field type analyzovaný pre full-text search a relevance, nie primárne pre exact aggregations. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Trace attribute governance

Policy určujúca povolené, bounded, sensitive a searchable span attributes spolu s retention a sampling použitím. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Trace completeness

Miera, do akej backend obsahuje všetky relevantné spans a relationships konkrétneho trace-u; ovplyvňuje ju propagation, sampling, export a storage loss. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Trace-to-logs

Correlation workflow, ktorý z trace ID, span ID, service a času vytvorí query do log backendu. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## TraceQL

Tempo query language na trace a span search podľa attributes, duration, status a structural conditions. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Translog

Elasticsearch/OpenSearch transaction-log mechanism používaný pri write durability a shard recovery podľa konkrétnej konfigurácie a produktu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## TSDB index store — Loki

Odporúčaný Loki index format ukladajúci TSDB index blocks v object storage popri chunks. Pozri [Loki](docs/12-observability/loki.md).

## `unwrap` — LogQL

LogQL operation premieňajúca parsed numerický field log entry na sample hodnotu pre range aggregation. Pozri [Loki](docs/12-observability/loki.md).

## Write index

Aktuálny backing index data streamu, do ktorého smerujú nové documents. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).
