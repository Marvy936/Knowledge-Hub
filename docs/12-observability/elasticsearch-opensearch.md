# Elasticsearch alebo OpenSearch

Elasticsearch a OpenSearch sú samostatné distribuované search a analytics produkty založené na Apache Lucene. Obe prijímajú JSON documents, mapujú fields, rozdeľujú indexy na primary a replica shards a poskytujú full-text search, filtering a aggregations. Spoločný pôvod však neznamená identické APIs, lifecycle semantics, security plugins, managed-service obmedzenia ani upgrade path. Production design musí pomenovať presný produkt, version a service distribution.

Pri log observability nestačí, že cluster health je green. Potrebujeme vedieť, či source event vytvoril validný document, či každý bulk item prešiel mappingom, do ktorého data streamu a backing indexu bol zapísaný, kedy sa stal searchable a či lifecycle/snapshot zachováva požadované evidence window.

## Document-to-query lifecycle

```text
system alebo business event
→ collector JSON document
→ product, cluster a tenant/security subject
→ index template a mapping resolution
→ data stream alebo write alias
→ coordinating node a bulk-item validation
→ primary shard indexing a acknowledgement
→ replica propagation
→ refresh a search visibility
→ query, aggregation a dashboard
→ rollover, lifecycle, snapshot a retention
→ evidence and recovery closure
```

HTTP `200` z `_bulk` neznamená, že všetky items uspeli. Bulk response obsahuje top-level `errors` a per-item status/error. Client musí vyhodnotiť každý item a retryovať iba eligible failures s idempotentnou document identity. citeturn662053search6turn662053search23turn662053search46

## Exact search subject

Atlas používa:

```yaml
product: Elasticsearch
cluster: logs-prod-eu
versionGeneration: ES-PROD-9
namespace: logs-atlas-payments-production
dataStream: logs-atlas-payments-production
indexTemplate: logs-atlas-payments-v12
mappingGeneration: LOG-MAP-12
writeBackingIndex: .ds-logs-atlas-payments-production-2026.07.29-000084
lifecycle: logs-30d-hot-warm
snapshotRepository: observability-snapshots-eu
sourceEvent: provider TLS failure for operation op-884
```

Pri OpenSearch by subject uvádzal OpenSearch distribution/version, Index State Management policy a relevantné security/plugin generation. Dokumentácia a command syntax sa overujú pre zvolený produkt; príklady nižšie používajú common REST surfaces, ale nie sú implicitnou garanciou parity.

## Component a index templates

Elasticsearch data stream potrebuje matching index template s `data_stream` objectom. OpenSearch používa rovnaký základný concept, ale current API a lifecycle features sa viažu na jeho dokumentáciu. citeturn662053search4turn662053search10turn662053search36turn662053search41

Component template pre log mapping:

```bash
curl -fsS -X PUT "$SEARCH_URL/_component_template/atlas-payments-log-fields-v12" \
  -H 'Content-Type: application/json' \
  -H "Authorization: ApiKey $SEARCH_API_KEY" \
  -d '{
    "template": {
      "mappings": {
        "dynamic": "strict",
        "properties": {
          "@timestamp": {"type": "date"},
          "service.name": {"type": "keyword"},
          "service.version": {"type": "keyword"},
          "deployment.environment": {"type": "keyword"},
          "cloud.availability_zone": {"type": "keyword"},
          "trace.id": {"type": "keyword", "doc_values": false},
          "payment.operation.id": {"type": "keyword", "doc_values": false},
          "error.type": {"type": "keyword"},
          "message": {"type": "text"}
        }
      }
    },
    "_meta": {"schema_generation": "LOG-MAP-12"}
  }'
```

Command preukazuje accepted component-template update v target clusteri. Neaplikuje mapping spätne na existujúce backing indexes. Component templates sa použijú pri vytvorení nových indexes/data stream backing indexes. citeturn662053search37

Index template:

```bash
curl -fsS -X PUT "$SEARCH_URL/_index_template/logs-atlas-payments-v12" \
  -H 'Content-Type: application/json' \
  -H "Authorization: ApiKey $SEARCH_API_KEY" \
  -d '{
    "index_patterns": ["logs-atlas-payments-*"],
    "priority": 500,
    "data_stream": {},
    "composed_of": ["atlas-payments-log-fields-v12"],
    "template": {
      "settings": {
        "index.number_of_shards": 3,
        "index.number_of_replicas": 1
      }
    },
    "_meta": {"owner": "observability-platform"}
  }'
```

Template priority a overlapping patterns môžu zmeniť effective result. Pred rolloutom sa používa template simulation podľa produktu. OpenSearch poskytuje simulate index template API; Elasticsearch má equivalent simulation surfaces v current API. citeturn662053search40

```bash
curl -fsS -X POST "$SEARCH_URL/_index_template/_simulate_index/logs-atlas-payments-production" \
  -H 'Content-Type: application/json' \
  -H "Authorization: ApiKey $SEARCH_API_KEY" \
  | jq '{template, overlapping_templates}'
```

Výstup preukazuje template resolution pre synthetic index name. Nepreukazuje mapping current backing indexu ani successful ingest.

## Data stream a backing indexes

Data stream poskytuje stable write/search name nad generation backing indexes. Writes smerujú na current write index, searches na všetky relevantné backing indexes. citeturn662053search8turn662053search41

```bash
curl -fsS -X PUT \
  -H "Authorization: ApiKey $SEARCH_API_KEY" \
  "$SEARCH_URL/_data_stream/logs-atlas-payments-production"

curl -fsS \
  -H "Authorization: ApiKey $SEARCH_API_KEY" \
  "$SEARCH_URL/_data_stream/logs-atlas-payments-production" \
  | jq '.data_streams[] | {name, generation, indices, template, status}'
```

Create command preukazuje data-stream creation podľa matching template. Read-back ukáže backing index generations a current metadata. Nepreukazuje document mapping correctness alebo search freshness.

Rollover vytvorí nový backing index, na ktorý sa aplikujú current templates. Mapping change preto často potrebuje template update plus rollover. In-place mapping update podporuje iba compatible additions; existing field type nemožno bezpečne zmeniť na incompatible type bez nového index/data stream generation a reindex/migration. citeturn662053search14turn662053search17

## Bulk ingest a per-item acknowledgement

Bulk request používa newline-delimited JSON:

```bash
cat > /tmp/payments.ndjson <<'EOF'
{"create":{"_index":"logs-atlas-payments-production","_id":"evt-991"}}
{"@timestamp":"2026-07-29T09:18:42.114Z","service":{"name":"provider-adapter","version":"7.19.0"},"deployment":{"environment":"production"},"cloud":{"availability_zone":"eu-central-1b"},"trace":{"id":"4bf92f3577b34da6a3ce929d0e0e4736"},"payment":{"operation":{"id":"op-884"}},"error":{"type":"tls.unknown_ca"},"message":"provider TLS handshake failed"}
{"create":{"_index":"logs-atlas-payments-production","_id":"evt-992"}}
{"@timestamp":"not-a-date","service":{"name":"provider-adapter"},"message":"invalid timestamp sample"}
EOF

curl -fsS -X POST "$SEARCH_URL/_bulk?refresh=false" \
  -H 'Content-Type: application/x-ndjson' \
  -H "Authorization: ApiKey $SEARCH_API_KEY" \
  --data-binary @/tmp/payments.ndjson \
  | tee /tmp/bulk-response.json \
  | jq '{took, errors, items: [.items[] | to_entries[0].value | {status, result, error}]}'
```

Response môže mať HTTP `200`, `errors=true`, prvý item `201` a druhý `400 mapper_parsing_exception`. Client nesmie potvrdiť celý buffer iba podľa HTTP statusu. `create` s stable `_id` vráti conflict pri duplicate replay, čo možno použiť ako idempotency boundary; random `_id` by duplicate document prijal.

`refresh=false` acknowledgement neznamená okamžitú search visibility. Primary indexing môže uspieť a document sa stane searchable až po refresh. `refresh=wait_for` čaká na refresh, ale zvyšuje latency/pressure a nie je default riešením pre každý log event.

## Mapping a dynamic field risk

Mapping read-back:

```bash
curl -fsS \
  -H "Authorization: ApiKey $SEARCH_API_KEY" \
  "$SEARCH_URL/logs-atlas-payments-production/_mapping" \
  | jq 'to_entries[] | {index: .key, schema: .value.mappings._meta.schema_generation, properties: .value.mappings.properties}'
```

Výstup preukazuje mapping každého matched backing indexu. Data stream môže obsahovať viac mapping generations. Query, ktorá predpokladá field type uniformity, môže zlyhať alebo vrátiť partial výsledok.

Dynamic mapping pri arbitrary JSON môže vytvoriť field explosion: každý customer-defined key sa stane novým mapped fieldom. `dynamic: strict` odmietne unknown fields; `flattened` alebo equivalent product feature môže byť vhodná pre bounded arbitrary map podľa use case-u. Mapping limit zvýšený bez schema opravy iba odloží cluster pressure.

## Search, refresh a evidence

Search exact error cohort:

```bash
curl -fsS -X POST "$SEARCH_URL/logs-atlas-payments-production/_search" \
  -H 'Content-Type: application/json' \
  -H "Authorization: ApiKey $SEARCH_API_KEY" \
  -d '{
    "size": 100,
    "sort": [{"@timestamp": "asc"}],
    "query": {
      "bool": {
        "filter": [
          {"range": {"@timestamp": {"gte": "2026-07-29T09:10:00Z", "lt": "2026-07-29T09:35:00Z"}}},
          {"term": {"service.name": "provider-adapter"}},
          {"term": {"cloud.availability_zone": "eu-central-1b"}},
          {"term": {"error.type": "tls.unknown_ca"}}
        ]
      }
    }
  }' \
  | jq '{took, timed_out, shards: ._shards, hits: [.hits.hits[]._source]}'
```

Search response preukazuje documents visible v selected cluster/data stream/time range. `_shards.failed > 0` alebo timeout znamená partial/failed evidence. Prázdne hits nepreukazujú absent source event, kým bulk item, collector delivery, mapping rejection a retention nie sú overené.

## Shards, replicas a cluster health

```bash
curl -fsS \
  -H "Authorization: ApiKey $SEARCH_API_KEY" \
  "$SEARCH_URL/_cluster/health/logs-atlas-payments-production?level=shards" \
  | jq '{status, number_of_nodes, active_primary_shards, active_shards, unassigned_shards}'

curl -fsS \
  -H "Authorization: ApiKey $SEARCH_API_KEY" \
  "$SEARCH_URL/_cat/shards/logs-atlas-payments-production?v=true"
```

Green health preukazuje assigned primary a replica shards podľa cluster contractu. Nepreukazuje correct mapping, ingest completeness, query semantics alebo snapshot recoverability. Yellow môže byť expected v single-node sandboxe a unacceptable v production; status sa interpretuje podľa topology.

Too many small shards zvyšujú heap/cluster-state overhead. Too few large shards môžu obmedziť parallelism a recovery. Shard plan vychádza z data rate, retention, query pattern, rollover size a node capacity.

## Lifecycle a snapshots

Elasticsearch môže používať data stream lifecycle alebo ILM podľa deployment/product capabilities; OpenSearch používa Index State Management a vlastné snapshot/lifecycle modely. Product-specific syntax sa nemieša.

Lifecycle transition nie je backup. Delete phase odstráni data podľa policy. Snapshot repository a restore test poskytujú recovery evidence. Snapshot success nepreukazuje query/application compatibility po restore.

## Worked incident: HTTP 200, časť logs sa stratila v bulk items

Po schema rollout-e `LOG-MAP-12` dashboard ukazuje pokles provider error logs, hoci Prometheus error metric rastie. Collector output reports HTTP success. Competing hypotheses sú telemetry recovery, wrong dashboard query, delayed refresh, mapping conflict, partial shard failure alebo bulk client bug.

Captured bulk response má HTTP `200`, ale `errors=true`. Documents s `provider.response.code` ako integer uspeli; starší producer posiela rovnaký field ako string a items dostávajú `mapper_parsing_exception`. Collector kontroloval iba HTTP status a odstránil buffer, preto failed items neboli retried ani dead-lettered.

Containment zachová raw failed payload samples a zastaví destructive acknowledgement. Recovery versionuje schema, normalizuje field u producer/collector-a a smeruje incompatible old cohort do quarantine data streamu. Bulk client vyhodnocuje per-item status a retryuje iba transient failures; permanent mapping errors idú do bounded dead-letter pathu.

Acceptance odošle mixed bulk batch a očakáva úspešné valid items, explicitne zachytený invalid item, žiadnu stratu valid records a searchable document po refresh. Mapping read-back musí ukázať intended generation vo všetkých current write paths. Forbidden replay s rovnakým `_id` nesmie vytvoriť duplicate document.

## Kontrolné otázky

1. Prečo Elasticsearch a OpenSearch nemožno považovať za identický produkt?
2. Čo index template simulation preukazuje?
3. Prečo mapping update neprepíše automaticky staré backing indexes?
4. Ako data stream oddeľuje write index a search scope?
5. Prečo HTTP `200` z `_bulk` nie je batch success?
6. Ako stable `_id` pomáha pri replayi?
7. Aký rozdiel je medzi indexing acknowledgement a search visibility?
8. Prečo dynamic mapping môže vytvoriť field explosion?
9. Čo green cluster health nepreukazuje?
10. Aké evidence uzatvára bulk partial-failure incident?

## Oficiálna dokumentácia

- [Elasticsearch data streams](https://www.elastic.co/guide/en/elasticsearch/reference/current/data-streams.html)
- [Elasticsearch index templates](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-put-template.html)
- [Elasticsearch Bulk API](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html)
- [OpenSearch data streams](https://docs.opensearch.org/latest/im-plugin/data-streams/)
- [OpenSearch index templates](https://docs.opensearch.org/latest/api-reference/index-apis/index-templates/)
- [OpenSearch Bulk API](https://docs.opensearch.org/latest/api-reference/document-apis/bulk/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Loki](loki.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Fluent Bit →](fluent-bit.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
