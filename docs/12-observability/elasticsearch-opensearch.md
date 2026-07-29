# Elasticsearch alebo OpenSearch

Elasticsearch a OpenSearch sú samostatné distribuované search a analytics produkty založené na Apache Lucene. Obe prijímajú JSON documents, mapujú fields, rozdeľujú indexy na shards a poskytujú full-text search, filtering a aggregations. Spoločný pôvod však neznamená identické APIs, lifecycle semantics, security plugins, managed-service obmedzenia ani upgrade path.

Pri log observability nie je rozhodujúce iba to, či cluster svieti green. Potrebujeme vedieť, či exact source event vytvoril validný document, či každý bulk item prešiel mappingom, ktorý data stream/backing index ho prijal, či write acknowledgement bolo durable, kedy sa stal searchable a či lifecycle/snapshot zachováva požadované evidence window.

## 1. Dominantný model

```text
system alebo business event
→ collector alebo ingest client record
→ product/version a data-stream subject
→ template, mapping a ingest-pipeline generation
→ bulk/request routing na primary shard
→ per-document validation a indexing outcome
→ acknowledgement, replica a durability state
→ refresh a search visibility
→ Lucene segment a merge lifecycle
→ rollover, tiering, retention a snapshot
→ query/aggregation result
→ evidence-quality a recovery verdict
```

Request-level úspech nie je document-level úspech a cluster health nie je business evidence completeness.

## 2. Exact document-search subject

Pre Atlas Payments používame `SEARCH-PAY-45`:

```text
product: Elasticsearch alebo OpenSearch — explicitne jeden
runtime/product generation: versioned deployment
cluster/domain identity
environment a region
data stream alebo index alias
template generation a priority
mapping/schema generation
ingest pipeline generation
write backing index a generation
primary/replica topology
collector/client generation
bulk request ID a per-item outcomes
lifecycle policy generation: Elastic ILM/DSL alebo OpenSearch ISM
snapshot repository a recovery generation
query time/index/tenant scope
```

Dokumentácia a runbook musia pomenovať produkt. „Elastic-compatible“ nestačí na rozhodovanie o APIs, lifecycle, security alebo upgrade-e.

## 3. Oddelené stavy

```text
bulk HTTP request dostal 2xx
≠ všetky items boli indexed
≠ documents sú searchable
≠ replicas sú assigned
≠ snapshot je obnoviteľný
```

Rovnako:

```text
template bol aktualizovaný
≠ existujúci backing index dostal nový mapping
≠ producer už emituje novú schema
≠ historical documents sú kompatibilné
```

Tieto rozdiely vysvetľujú veľkú časť „missing logs“ incidentov.

## 4. Document a field contract

Document je JSON record s explicitnou schema intent:

```json
{
  "@timestamp": "2026-07-29T04:55:00Z",
  "service": {"name": "provider-adapter", "version": "7.21.0"},
  "event": {"name": "payment.settlement.completed", "outcome": "failure"},
  "provider": {"code": "TIMEOUT"},
  "trace": {"id": "opaque-id"},
  "duration_ms": 5200,
  "message": "Provider response was not confirmed"
}
```

Field design rozlišuje:

- exact identifiers a bounded categories;
- full-text content;
- numeric/date/boolean values;
- object oproti nested structure;
- sensitive alebo high-cardinality fields;
- raw payload, ktorý nemá byť dynamicky rozbalený do mappings.

`keyword` je vhodný na exact filter, sort a aggregation. `text` používa analyzer a full-text semantics. Rovnaký field path nemôže byť v jednej mapping generation raz scalar a inokedy object.

## 5. Data stream a backing-index lifecycle

Data stream poskytuje stabilný logical write a read subject pre append-oriented telemetry:

```text
logs-payments-production
→ current write backing index
→ rollover
→ nový write backing index
→ read naprieč generations
```

Producer zapisuje do data streamu, nie priamo do backing-index mena. Matching template definuje mappings a settings pre nové backing indexes.

Zmena template neprepisuje automaticky historické backing indexes. Nová schema sa realizuje cez rollover, nový data stream alebo reindex workflow podľa compatibility potreby.

Data stream je vhodný hlavne pre append-oriented logs/events. Ak use case potrebuje časté updates rovnakého `_id` s last-write-wins semantics, treba overiť vhodnejší alias/index model.

## 6. Template a mapping generation

Template resolution môže zahŕňať viac component templates a priorít.

```text
index/data-stream name
→ matching templates
→ priority/merge
→ effective settings a mappings
→ nový backing index
```

Pri incidente uchovaj effective template, nie iba source file, o ktorom tím predpokladá, že sa použil.

Dynamic mapping bez boundary môže vytvoriť:

- field/mapping explosion;
- scalar/object conflicts;
- nesprávny date alebo numeric type;
- cluster-state a heap pressure;
- producer-version drift.

Production logs potrebujú explicitnú schema, dynamic templates alebo field allowlist a quarantine path pre nekompatibilné records.

## 7. Shards, segments a search visibility

Index je rozdelený na primary shards a replicas. Shard je Lucene index z immutable segments.

Zjednodušený lifecycle:

```text
document indexing
→ primary shard validation/write
→ replica coordination podľa contractu
→ acknowledgement a translog/durability state
→ refresh vytvorí searchable segment
→ segment merges
→ deleted/updated documents sa fyzicky odstránia neskôr
```

Write acknowledgement a search visibility sú odlišné. Document môže byť prijatý a durable, ale ešte nie visible pre search pred refreshom.

Replica poskytuje redundancy a read capacity. Nie je backup proti logical delete, corruption alebo zlému lifecycle policy.

## 8. Bulk-ingest contract

Bulk request znižuje per-document overhead, ale odpoveď treba vyhodnotiť per item.

```text
bulk transport outcome
→ top-level response
→ per-item status
→ retryable 429/5xx
→ permanent mapping/auth 4xx
→ unknown timeout outcome
→ checkpoint/offset decision
```

Kritické rozlíšenia:

- request `2xx` môže obsahovať failed items;
- `429` potrebuje bounded backoff a queue control;
- mapping conflict je permanentný pre túto schema generation;
- timeout po write môže mať unknown outcome;
- retry celého batchu môže duplikovať úspešné items.

Použi stable document identity alebo downstream dedup/reconciliation model tam, kde duplicates majú význam.

## 9. Cluster health a allocation

Health farby opisujú shard assignment:

- green — primaries aj replicas assigned;
- yellow — primaries assigned, aspoň jedna replica nie;
- red — aspoň jeden primary unassigned.

Green nepreukazuje správne mappings, kompletný ingest, search semantics ani snapshot recovery.

Pri unassigned shard postupuj:

```text
exact shard a primary/replica role
→ allocation explanation
→ node roles a topology
→ disk watermarks
→ awareness/tier/filter constraints
→ shard limits
→ recovery state
→ authoritative repair
```

Náhodný reroute alebo delete indexu môže zhoršiť data loss.

## 10. Shard a resource economics

Príliš veľa malých shards zvyšuje heap, cluster state, file handles, recovery a query fan-out. Príliš veľký shard predlžuje relocation, restore a single-shard query.

Sizing vychádza z:

- ingest volume a document size;
- retention a rollover;
- mapping/field count;
- query concurrency a aggregations;
- recovery objective;
- node/disk/heap capacity;
- failure-domain placement.

Daily index pre každú malú service je typický oversharding anti-pattern. Data stream s rolloverom podľa age/size/document countu býva stabilnejší.

## 11. Search a aggregation contract

Log investigation má začať bounded scope-om:

```text
time range
→ data stream/index
→ environment/service/tenant
→ exact event/error field
→ trace/request ID
→ full-text message až potom
```

Rizikové queries:

- leading wildcard alebo broad regex;
- long range cez všetky indexes;
- high-cardinality terms aggregation;
- deep pagination;
- scripts/runtime fields nad veľkým datasetom;
- sorting na nevhodnom field type.

Log-derived counts a percentiles nemusia byť SLO autorita, ak ingest loss, delay alebo sampling mení population.

## 12. Lifecycle semantics: Elasticsearch verzus OpenSearch

### Elasticsearch

Môže používať Index Lifecycle Management a Data Stream Lifecycle podľa deploymentu a use case-u. Phases/actions, data tiers a searchable-snapshot semantics treba overiť pre konkrétnu verziu a licenciu.

### OpenSearch

Index State Management používa policy states, transitions a actions ako rollover, replica change, read-only, force merge, snapshot alebo delete podľa platformy a plugin generation.

Názov podobnej funkcie nepreukazuje rovnaký execution, retry, failure alebo migration contract. Policy sa testuje na novom backing indexe aj pri upgrade-e.

## 13. Snapshots a recovery

Snapshot je external backup generation. Replica shard nie je snapshot.

Recovery contract zahŕňa:

- repository identity a isolation;
- encryption a credentials;
- index/system/security scope;
- retention;
- product/version compatibility;
- restore target a rename rules;
- dashboards/clients/integrations mimo samotných indexes;
- test restore a query validation.

Snapshot success nepreukazuje obnoviteľnosť business investigation workflowu.

## 14. Security a tenancy

Chráň REST API, inter-node transport, Dashboards/Kibana, ingest identities, snapshot repository a audit logs.

Tenant models môžu používať samostatné clusters, data streams/indexes alebo shared index s enforced tenant filterom. Shared field je security boundary iba vtedy, keď authorization vrstva filter vynucuje a používateľ nemá obchádzajúci raw API access.

Producer-side minimization zostáva povinná. Field-level permission nezruší fakt, že secret už bol ingestovaný, replikovaný a snapshotovaný.

## 15. Self-observability a canary

Sleduj:

- cluster state publication a node membership;
- primary/replica assignment;
- heap, GC, CPU a disk watermarks;
- indexing rate/latency/rejections;
- bulk item failures podľa reason;
- refresh, segment count a merges;
- search latency/rejections;
- thread-pool queues;
- lifecycle/rollover failures;
- snapshot a restore tests;
- template/mapping growth;
- dead-letter/quarantine backlog.

End-to-end canary:

```text
known document generation
→ bulk item acceptance
→ expected data stream/write index
→ search visibility po refresh boundary
→ rollover do ďalšej generation
→ lifecycle transition
→ snapshot/restore query
```

## 16. Worked failure: bulk request je 200, error logs chýbajú

### Symptóm

Po release `7.22.0` prestanú v OpenSearch data streame pribúdať niektoré provider failure logs. Cluster je green, bulk endpoint vracia HTTP `200` a collector checkpoint napreduje. Grafana preto ukazuje prudký pokles failures, hoci payment reconciliation eviduje rast unknown outcomes.

### Exact subject

```text
subject: SEARCH-PAY-45
product: OpenSearch
cluster generation: OS-PAY-09
data stream: logs-payments-production
write backing index generation: 000184
template generation: TPL-PAY-31
mapping generation: MAP-PAY-31
producer release: 7.22.0
bulk client generation: BULK-RELAY-12
field: provider.response
```

Mapping `MAP-PAY-31` definuje:

```json
"provider.response": {"type": "keyword"}
```

Release `7.22.0` začne pri failure emittovať:

```json
"provider.response": {
  "code": "TLS_HANDSHAKE_FAILED",
  "retryable": true
}
```

### Competing hypotheses

1. application failure log vôbec nevznikol;
2. collector filter ho zahodil;
3. bulk transport alebo auth zlyháva;
4. cluster/backing index je red;
5. refresh delay skrýva recent documents;
6. mapping conflict odmieta iba novú producer schema;
7. query používa nesprávny data stream alebo timestamp;
8. lifecycle predčasne maže documents.

### Discriminating evidence

```text
source sample: failure document existuje
collector/bulk request: obsahuje document
HTTP status: 200
bulk response errors: true
failed item status: 400 mapper_parsing_exception
successful items v tom istom batchi: indexed
cluster health: green
current mapping: provider.response = keyword
producer 7.21.x: string
producer 7.22.0: object
bulk relay: checkpoint podľa HTTP statusu, nie item outcomes
```

Mechanizmus:

```text
batch obsahuje validné aj nekompatibilné documents
→ request transport uspeje
→ OpenSearch vyhodnotí každý item
→ nové object values konfliktujú s keyword mappingom
→ iba affected items dostanú 400
→ top-level HTTP zostane 200
→ bulk relay označí celý batch ako úspešný
→ source checkpoint sa posunie
→ rejected failure logs sa stratia z search evidence
→ dashboard ukáže falošné zlepšenie
```

### Containment

- zastaviť producer rollout alebo problematický field emission;
- zachovať raw redacted item, complete bulk response, mapping, template a checkpoint evidence;
- prestať interpretovať log-derived failure count ako business truth;
- smerovať permanent failed items do bounded quarantine;
- ne-retryovať celý batch naslepo.

### Authoritative recovery

1. zvoliť kompatibilný schema contract — napríklad nový object field alebo novú stream generation;
2. aktualizovať template a vykonať rollover, aby nový backing index dostal nový mapping;
3. testovať starú aj novú producer schema;
4. opraviť bulk relay tak, aby klasifikoval per-item outcomes;
5. reprocessovať quarantine/source archive so stable document IDs alebo dedup modelom;
6. overiť search visibility, counts a sample documents;
7. reconciliovať business unknown outcomes nezávisle od logov;
8. pridať mapping fixture a bulk partial-failure canary.

### Acceptance verdict

Recovery je prijatá, keď:

- každý bulk item má explicitný accepted, retryable alebo quarantined verdict;
- nový write backing index používa očakávanú mapping generation;
- producer `7.21.x` aj `7.22.0` fixtures majú definovaný outcome;
- query vráti recovered failure documents bez uncontrolled duplicates;
- dashboard trend sa zhoduje s authoritative business counterom v rámci delivery lag contractu;
- mapping conflict alert funguje;
- rollover, lifecycle a snapshot test zachovajú nový schema model;
- forbidden arbitrary dynamic fields nevytvárajú mapping explosion.

## 17. Troubleshooting model

### Missing documents

```text
source event
→ collector offset/filter
→ bulk request
→ per-item response
→ ingest pipeline
→ data stream/write index
→ mapping/template
→ acknowledgement
→ refresh
→ query/timezone/lifecycle
```

### Yellow alebo red

```text
exact shard
→ primary/replica
→ allocation explanation
→ nodes/roles/zones
→ disk/tier/filter/shard limits
→ recovery
```

### Indexing 429

```text
write queue a rejections
→ bulk size/concurrency
→ hot shards
→ ingest CPU
→ refresh/merge pressure
→ heap/GC/disk
→ bounded backoff a backlog
```

### High heap alebo slow query

```text
shard/field count
→ cluster state
→ query/index scope
→ aggregations/cardinality
→ segments/cache
→ heap/GC/hot threads
```

## 18. Anti-patterny

### HTTP 200 ako bulk success

Ignoruje per-item failures.

### Dynamic mapping pre arbitrary JSON

Vytvára conflicts a field explosion.

### Replica ako backup

Logical deletion a corruption sa replikujú.

### Refresh po každom documente

Zvyšuje segment a merge overhead.

### Retry celého batchu

Duplikuje successful items a opakuje permanent failures.

### Jeden lifecycle model kopírovaný medzi produktmi

Elasticsearch ILM/DSL a OpenSearch ISM nemajú automaticky rovnaké semantics.

## 19. Kontrolné otázky

1. Čo tvorí exact document-search subject?
2. Aký je rozdiel medzi data streamom, backing indexom, shardom a segmentom?
3. Prečo write acknowledgement nie je search visibility?
4. Ako template generation súvisí s novým backing indexom?
5. Prečo scalar/object mapping conflict nemožno vyriešiť iba refreshom?
6. Ako bulk HTTP 200 môže obsahovať failed documents?
7. Kedy je 429 retryable a mapping 400 permanentný?
8. Prečo green cluster nepreukazuje ingest completeness?
9. Ako rollover rieši schema a shard lifecycle?
10. Prečo replica nie je backup?
11. Ako sa líši Elastic lifecycle a OpenSearch ISM?
12. Ako overíš celý ingest-to-restore path?

## Glossary impact

Relevantné pojmy: document-search subject, product-generation identity, data-stream generation, write backing index, template-resolution generation, mapping generation, per-item bulk verdict, search-visibility boundary, shard-assignment verdict, Lucene segment lifecycle, schema quarantine, lifecycle-policy generation, snapshot-recovery generation a document-search acceptance verdict.

## Primárne zdroje

- [Elasticsearch data streams](https://www.elastic.co/docs/manage-data/data-store/data-streams/)
- [Elasticsearch clusters, nodes and shards](https://www.elastic.co/docs/deploy-manage/distributed-architecture/clusters-nodes-shards)
- [Elasticsearch Index Lifecycle Management](https://www.elastic.co/docs/manage-data/lifecycle/index-lifecycle-management/index-lifecycle)
- [Elasticsearch Data Stream Lifecycle](https://www.elastic.co/docs/manage-data/lifecycle/data-stream)
- [OpenSearch data streams](https://docs.opensearch.org/latest/dashboards/im-dashboards/datastream/)
- [OpenSearch Index State Management](https://docs.opensearch.org/latest/im-plugin/ism/index/)
- [OpenSearch index APIs](https://docs.opensearch.org/latest/api-reference/index-apis/index/)
- [OpenSearch cluster health](https://docs.opensearch.org/latest/api-reference/cluster-api/cluster-health/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Loki](loki.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Fluent Bit →](fluent-bit.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
