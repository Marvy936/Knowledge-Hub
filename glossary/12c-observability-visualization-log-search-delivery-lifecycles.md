# Observability visualization, log, search and delivery lifecycle glossary entries

## Aged-log canary

Synthetic log event, ktorého recent, historical a retention-expiry query behavior sa periodicky overuje cez celý collector, Loki storage a query lifecycle. Pozri [Loki](docs/12-observability/loki.md).

## Alerting control-plane ownership — Grafana

Explicitné určenie, či rule evaluation, alert identity a notification policy vlastní Grafana-managed alerting alebo data-source-managed systém ako Prometheus/Loki. Pozri [Grafana](docs/12-observability/grafana.md).

## Authoritative dashboard writer

Jediný source alebo controller oprávnený meniť konkrétny dashboard UID, napríklad Git provisioning, Terraform alebo Operator; UI edit bez zmeny autority je iba dočasný drift. Pozri [Grafana](docs/12-observability/grafana.md).

## Backend acknowledgement — log delivery

Výsledok output requestu potvrdený cieľovým backendom vrátane per-item semantics, nie iba transportného HTTP statusu. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Chunk-delivery state — Fluent Bit

Runtime stav buffered chunku voči jednému alebo viacerým outputs, napríklad queued, flushing, retrying, acknowledged alebo dropped. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Chunk generation — Loki

Versionovaný compressed object obsahujúci log entries jedného streamu za časový interval a publikovaný spolu s index reference. Pozri [Loki](docs/12-observability/loki.md).

## Dashboard query budget

Odhad a guardrail query loadu odvodený z počtu panels, queries, variable expansions, viewers, refresh cadence a backend fan-outu. Pozri [Grafana](docs/12-observability/grafana.md).

## Dashboard render canary

End-to-end test, ktorý otvorí exact dashboard UID, vykoná known query a overí raw value, transformation, unit, rendered value a drilldown. Pozri [Grafana](docs/12-observability/grafana.md).

## Dashboard source generation

Immutable alebo versionovaný dashboard artifact vytvorený v authoritative source workflowe pred provisioningom do Grafany. Pozri [Grafana](docs/12-observability/grafana.md).

## Data-frame generation — Grafana

Typed query result normalizovaný Grafanou do fields a frames pred expressions, transformations a visualization. Pozri [Grafana](docs/12-observability/grafana.md).

## Data-source identity — Grafana

Stable UID, plugin type, endpoint, tenant, credentials, TLS a query settings konkrétneho Grafana data source-u. Pozri [Grafana](docs/12-observability/grafana.md).

## Data-stream generation — document search

Logical append-oriented telemetry subject a jeho current backing-index generation vytvorená cez template, rollover a product-specific lifecycle. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Document-search acceptance verdict

Dôkaz, že documents prešli per-item ingestom, správnou mapping generation, search visibility, lifecycle a recovery testom bez forbidden schema alebo tenant outcome-u. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Document-search subject

Exact Elasticsearch alebo OpenSearch product/version, cluster, data stream/index, template, mapping, pipeline, backing index, lifecycle, snapshot a query scope analyzovanej telemetry. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Field-semantics contract — Grafana

Explicitný vzťah medzi raw value, reducerom, unitom, mappings, thresholds a rendered operational meaningom. Pozri [Grafana](docs/12-observability/grafana.md).

## Filesystem-backlog generation — Fluent Bit

Množina persistentných local chunks, ich age, size, output references a storage limits počas backend backpressure alebo outage. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Filter-order contract — Fluent Bit

Versionované poradie parse, enrichment, normalization, redaction, cardinality control a routing filters, ktoré určuje final record a security outcome. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Fluent Bit acceptance verdict

Dôkaz, že exact sources, offsets, routes, buffers a outputs prežijú fault/restart scenáre a vytvoria queryovateľné telemetry s definovaným loss/duplicate contractom. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Fluent Bit subject

Exact Node/source, DaemonSet/config, input, inode, Tail DB, parser, tag, filter order, buffer, output, credential a acknowledgement identity analyzovanej pipeline. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Grafana acceptance verdict

Dôkaz, že backend query, raw frame, transformation, unit, loaded dashboard revision, permissions a alert ownership vytvárajú správny allowed aj forbidden operational outcome. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana investigation path

Versionovaný drilldown chain od SLO/Golden Signals panelu cez cohort, dependency, trace/log/resource evidence až po runbook alebo incident. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana subject

Exact organization, folder UID, dashboard/panel UID, data-source UID, source/loaded revision, query, transformation, field config, alert owner a viewer scope. Pozri [Grafana](docs/12-observability/grafana.md).

## Historical-log path — Loki

Query path závislý od TSDB index blocks, flushed chunks, schema periods, object-store access, compaction a retention. Pozri [Loki](docs/12-observability/loki.md).

## Label-contract generation — Loki

Versionovaná množina bounded stream labels, structured metadata rules a forbidden dynamic dimensions používaná pri ingestovaní logs. Pozri [Loki](docs/12-observability/loki.md).

## Loaded dashboard revision

Dashboard representation skutočne uložená a používaná Grafanou po provisioningu alebo UI mutation, odlíšená od source artifactu. Pozri [Grafana](docs/12-observability/grafana.md).

## Log-delivery canary

Bounded synthetic event sledovaný od source inputu cez Fluent Bit acknowledgement až po backend query, duplicate count a delivery latency. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Log-loss window

Časový a source-specific interval, pre ktorý telemetry records nemožno preukázateľne obnoviť pre offset, buffer, rotation, drop alebo backend failure. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Log-stream identity

Tenant ID a úplný bounded Loki label set, ktoré spoločne definujú jeden log stream. Pozri [Loki](docs/12-observability/loki.md).

## Loki acceptance verdict

Dôkaz, že exact tenant/stream/schema logy sú ingestované, queryovateľné cez recent aj historical path a expirované iba podľa authoritative retention policy. Pozri [Loki](docs/12-observability/loki.md).

## Loki entry acceptance

Distributor/ingester verdict, že log entry spĺňa tenant, label, timestamp, line-size, ordering a rate-limit contract a bola prijatá do write pathu. Pozri [Loki](docs/12-observability/loki.md).

## Loki evidence-completeness verdict

Rozhodnutie, či LogQL result reprezentuje očakávanú occurrence population alebo je neúplný pre collector, rejection, chunk, schema, retention či query failure. Pozri [Loki](docs/12-observability/loki.md).

## Loki retention generation

Versionovaný per-tenant/per-stream retention, Compactor/delete-delay a object-store lifecycle contract. Pozri [Loki](docs/12-observability/loki.md).

## Loki subject

Exact tenant, stream-label generation, collector, schema period, deployment, object store, encryption, retention a LogQL scope analyzovaných logs. Pozri [Loki](docs/12-observability/loki.md).

## Lucene segment lifecycle

Prechod indexed documents cez refresh-created immutable segments, merges a neskoršie fyzické odstránenie deleted/updated records. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Mapping generation

Versionovaný field-type a structure contract aplikovaný na konkrétny index alebo backing-index generation. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Object-store lifecycle mismatch — Loki

Stav, keď bucket expiration alebo transition odstráni či zneprístupní index/chunks skôr alebo inak než authoritative Loki retention model. Pozri [Loki](docs/12-observability/loki.md).

## Output-independent liveness — Fluent Bit

Liveness contract, ktorý overuje schopnosť agent processu pokračovať bez reštartu iba preto, že vzdialený telemetry backend je dočasne nedostupný. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Per-item bulk verdict

Accepted, retryable, permanent-failure, quarantined alebo unknown outcome každého documentu v Elasticsearch/OpenSearch bulk response. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Position-state durability — Fluent Bit

Schopnosť Tail DB a source offset/inode state-u prežiť definovaný container, Pod alebo Node restart boundary. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Product-generation identity — document search

Explicitná Elasticsearch alebo OpenSearch product/version a deployment generation, ktorá určuje podporované API, mapping, lifecycle, security a recovery semantics. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Query generation — Grafana

Exact data source, text, variables, time range, step/interval a execution options použité na vytvorenie jedného query resultu. Pozri [Grafana](docs/12-observability/grafana.md).

## Recent-log path — Loki

Query path k neflushnutým alebo recentným entries cez live ingesters a current ring ownership. Pozri [Loki](docs/12-observability/loki.md).

## Rendered-value verdict — Grafana

Rozhodnutie, či panel display zachováva numeric a categorical semantics raw backend value-u po transformations, units, mappings a overrides. Pozri [Grafana](docs/12-observability/grafana.md).

## Replay duplicate — Fluent Bit

Druhá alebo ďalšia backend kópia toho istého source eventu vytvorená rereadom, timeout retry, position-state stratou alebo multi-reader fan-outom. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Schema quarantine — document search

Bounded storage a workflow pre documents odmietnuté pre mapping alebo validation conflict, ktoré sa nesmú nekonečne retryovať ani ticho zahodiť. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Search-visibility boundary

Prechod medzi acknowledged/durable document write-om a okamihom, keď refresh sprístupní document query engine-u. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Shard-assignment verdict

Explicitný green/yellow/red a allocation-explanation stav konkrétneho primary alebo replica shardu, nie všeobecný business-health verdict. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Snapshot-recovery generation — document search

Exact repository, snapshot, product/version compatibility, selected indexes/system state, restore target a validation contract. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Source-file generation — Fluent Bit

Exact path, inode, rotation state, producer/container identity a time window source log file-u čítaného Tail inputom. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Structured-metadata boundary — Loki

Pravidlo určujúce, ktoré dynamic per-entry fields zostanú structured metadata namiesto stream labels, aby nevytvárali stream explosion. Pozri [Loki](docs/12-observability/loki.md).

## Tag-route generation — Fluent Bit

Versionovaný mapping input tags cez filter/output `Match` pravidlá na intended a forbidden destinations. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Tail offset generation

Exact file identity a byte/record position uchovaná Tail DB pre pokračovanie čítania po flushi, rotate alebo restart-e. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Template-resolution generation — document search

Effective merge matching index/component templates, priorít, settings a mappings použitý pri vytvorení nového backing indexu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Transformation generation — Grafana

Versionovaný ordered chain expressions a transformations aplikovaný na query frames pred visualization. Pozri [Grafana](docs/12-observability/grafana.md).

## TSDB schema period — Loki

Dátumom ohraničená Loki storage/index generation určujúca store, object store, schema version a index prefix pre writes a historical reads. Pozri [Loki](docs/12-observability/loki.md).

## Unknown log-delivery outcome

Stav, keď agent nedostal acknowledgement po requeste, hoci backend mohol record prijať, takže retry nesie duplicate risk a checkpoint loss risk. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Write backing index

Najnovší backing index data streamu, do ktorého sa routujú nové documents do ďalšieho rolloveru. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).
