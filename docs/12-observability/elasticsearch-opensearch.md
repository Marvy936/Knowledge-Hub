# Elasticsearch alebo OpenSearch

Elasticsearch a OpenSearch sú distribuované search a analytics platformy založené na Apache Lucene. Obe ukladajú JSON documents do indexes, rozdeľujú indexes na shards a poskytujú full-text search, structured filtering, aggregations a time-series log analytics. Napriek spoločnému pôvodu ide o samostatné produkty s odlišným release, licensing, plugin, API a managed-service ekosystémom.

Nie sú automaticky drop-in zameniteľné vo všetkých verziách a use cases. Produkčný výber musí overiť konkrétne APIs, clients, mappings, security, lifecycle, dashboards, plugins, upgrade path a support model.

## 1. Mentálny model

```text
structured log alebo event
→ collector / ingest pipeline
→ JSON document
→ data stream alebo index
→ primary shard
→ Lucene segments
→ replica shards
→ distributed query a aggregation
→ Kibana alebo OpenSearch Dashboards / API / Grafana
→ lifecycle, snapshot a retention
```

Na rozdiel od Loki sa typicky indexujú vybrané document fields, čo umožňuje bohaté field a full-text queries, ale zvyšuje mapping, shard, storage, heap a merge complexity.

## 2. Document

Document je JSON objekt uložený v indexe.

Príklad:

```json
{
  "@timestamp": "2026-07-21T20:00:00Z",
  "service": {
    "name": "orders-api",
    "version": "4.2.1"
  },
  "log": {
    "level": "ERROR"
  },
  "event": {
    "action": "payment.authorization",
    "outcome": "failure"
  },
  "trace": {
    "id": "..."
  },
  "message": "Payment provider timed out",
  "duration_ms": 2500
}
```

Document model musí rozlišovať:

- machine-queryable fields,
- full-text content,
- exact identifiers,
- numeric/date fields,
- nested/object structures,
- sensitive data,
- high-cardinality fields.

## 3. Index

Index je logical collection documents s vlastnými mappings, settings a shard topology.

Index nie je jeden fyzický súbor. Je rozdelený na primary shards a ich replicas.

Dôležité settings:

- počet primary shards,
- počet replicas,
- refresh interval,
- analyzers,
- mappings,
- routing,
- lifecycle policy,
- allocation a tier preferences.

Počet primary shards sa pri vytvorení indexu nastavuje ako základná topology decision. Neskôr sa mení cez rollover, reindex, split alebo shrink workflows, nie jednoduchým prepísaním existujúceho indexu.

## 4. Primary a replica shard

Primary shard vlastní primárnu kópiu subsetu documents.

Replica shard je kópia primary shardu.

Replicas poskytujú:

- redundancy,
- failover,
- vyššiu read capacity.

Neposkytujú:

- ochranu pred logical deletion alebo corruption,
- nezávislý backup,
- automatický cross-cluster DR,
- úplnú ochranu pri zlom allocation modeli.

Primary a jeho replica by nemali byť umiestnené na rovnakom failure domain-e.

## 5. Lucene segment

Shard je samostatný Lucene index zložený z immutable segments.

Indexing lifecycle zjednodušene:

```text
document write
→ in-memory buffer + transaction durability mechanism
→ refresh vytvorí searchable segment
→ segment merges
→ deleted/updated documents sa časom fyzicky odstránia merge-om
```

Dôsledky:

- document nemusí byť searchable okamžite po acknowledgement-e podľa refresh modelu,
- časté updates/deletes vytvárajú deleted documents a merge pressure,
- príliš častý refresh zvyšuje segment count a overhead,
- force merge na aktívnom write indexe môže spôsobiť veľký I/O load.

## 6. Refresh

Refresh sprístupní nové documents pre search vytvorením nového segmentu.

Refresh nie je:

- backup,
- durable flush,
- cluster replication,
- index rollover.

Príliš krátky refresh interval:

- znižuje search visibility latency,
- zvyšuje počet malých segments,
- zvyšuje merge a CPU/I/O overhead.

Pri bulk ingestion možno refresh model dočasne upraviť, ale zmena musí mať explicitný restore krok.

## 7. Transaction log a durability

Write acknowledgement, replica coordination, translog a filesystem flush semantics sa líšia podľa konkrétneho produktu a konfigurácie.

Pri návrhu over:

- acknowledgement level,
- in-sync replica model,
- translog durability,
- flush a recovery,
- behavior pri network partition,
- client retries a duplicate writes.

Search visibility a durable acknowledgement sú odlišné concepts.

## 8. Data streams

Data stream je logical abstraction nad rolling backing indexes pre append-oriented time-series data ako logs, events a metrics.

Data stream:

- má stabilný logical name,
- posiela writes do aktuálneho write indexu,
- searchuje naprieč backing indexes,
- používa index template,
- vyžaduje timestamp field,
- integruje sa s rollover a retention lifecycle.

Pre log telemetry je data stream typicky vhodnejší než ručné daily index names.

Použitie:

```text
logs-orders-production
→ .ds-logs-orders-production-000001
→ rollover
→ .ds-logs-orders-production-000002
```

Backing-index names nie sú application API. Application má zapisovať do data streamu.

## 9. Index templates

Index template definuje settings, mappings a aliases/data-stream configuration pre nové indexes.

Template governance musí riešiť:

- index patterns,
- priority,
- component templates,
- mappings,
- analyzers,
- shard/replica defaults,
- lifecycle policy,
- versioning,
- compatibility.

Zmena template typicky neprepíše automaticky mappings všetkých historických backing indexes. Často je potrebný rollover alebo reindex.

## 10. Mappings

Mapping definuje field names a types.

Príklady types:

- `keyword`,
- `text`,
- `date`,
- integer/long/double,
- boolean,
- object,
- nested,
- IP,
- geo,
- vector types podľa produktu/use case-u.

### `keyword` oproti `text`

`keyword`:

- exact match,
- sorting,
- aggregation,
- identifiers a bounded categories.

`text`:

- analyzovaný full-text search,
- tokenization,
- relevance scoring.

Log level alebo service name má byť typicky `keyword`, nie full-text field.

### Multi-fields

Jeden logical field môže mať analyzovanú aj exact variantu:

```json
"message": {
  "type": "text",
  "fields": {
    "keyword": {
      "type": "keyword",
      "ignore_above": 256
    }
  }
}
```

Neaplikuj automaticky multi-field na každý field bez query a storage potreby.

## 11. Dynamic mapping

Dynamic mapping môže automaticky vytvárať fields z prichádzajúcich documents.

Riziká:

- mapping explosion,
- rovnaký field príde raz ako string a inokedy ako object,
- nekontrolované user keys vytvoria tisíce fields,
- schema drift,
- vyšší cluster-state a heap overhead.

Pre production logs preferuj:

- explicitnú schema,
- dynamic templates,
- field allowlist,
- unknown fields v controlled objecte alebo raw payload,
- quarantine/dead-letter path pri mapping conflict.

## 12. Mapping conflict

Príklad:

```text
request.body = "text"
```

v inom documente:

```text
request.body = {"field": "value"}
```

Rovnaký field path nemôže byť súčasne scalar a object v tom istom mapping contracte.

Oprava často vyžaduje:

- nový field name alebo schema,
- nový index/data stream generation,
- reindex historických dát,
- producer/collector fix.

Mapping existujúceho field type-u sa nedá vždy bezpečne zmeniť in-place.

## 13. Elasticsearch a OpenSearch rozdiel

### Elasticsearch

Ekosystém zahŕňa Elasticsearch, Kibana, Elastic Agent, Fleet, ingest pipelines, ILM/Data Stream Lifecycle a ďalšie Elastic features podľa edície a deployment modelu.

### OpenSearch

Ekosystém zahŕňa OpenSearch, OpenSearch Dashboards, Security plugin, Index State Management a ďalšie OpenSearch plugins a managed-service integrations.

Pri porovnaní over:

- konkrétnu verziu,
- REST API compatibility,
- query DSL,
- client libraries,
- security model,
- lifecycle features,
- data-stream behavior,
- alerting/observability plugins,
- vector/search capabilities,
- snapshots,
- managed-service limitations,
- licensing a commercial support.

Názov podobnej funkcie nepreukazuje identické semantics.

## 14. Lifecycle management

### Elasticsearch

Môže používať napríklad:

- Index Lifecycle Management,
- Data Stream Lifecycle,
- data tiers,
- rollover,
- searchable snapshots podľa deploymentu/licencie.

ILM phases typicky zahŕňajú:

- hot,
- warm,
- cold,
- frozen,
- delete.

### OpenSearch

Index State Management používa policy states, transitions a actions, napríklad:

- rollover,
- replica change,
- read-only,
- force merge,
- snapshot,
- cold transition podľa platformy,
- delete.

Lifecycle policy musí byť testovaná na novom backing indexe aj pri upgrade/migration.

## 15. Rollover

Rollover vytvorí nový write backing index podľa conditions, napríklad:

- age,
- size,
- document count,
- shard size.

Rollover je lepší než pevný daily index, ak volume výrazne kolíše.

Cieľom je udržať rozumnú shard size a zabrániť:

- extrémne veľkým shards,
- tisícom malých shards,
- nepredvídateľnej recovery,
- príliš širokým queries.

## 16. Shard sizing

Shards majú fixed overhead aj data-dependent cost.

Príliš veľa malých shards spôsobuje:

- heap a cluster-state overhead,
- pomalé recovery,
- veľa file handles,
- query fan-out,
- dlhé lifecycle operations.

Príliš veľké shards spôsobujú:

- pomalý relocation/recovery,
- dlhé snapshot/restore,
- veľký impact pri failure,
- pomalšie single-shard queries.

Sizing vychádza z:

- ingest rate,
- retention,
- query concurrency,
- document size,
- mapping,
- aggregations,
- recovery objective,
- node capacity.

Univerzálna shard size neexistuje; testuj reálny workload.

## 17. Cluster a node roles

Self-managed cluster potrebuje stabilný control-plane a data-plane model.

Role môžu zahŕňať:

- cluster-manager/master-eligible,
- data roles alebo tiers,
- ingest,
- coordinating,
- machine-learning/search-specific roles podľa produktu.

Dedicated control-plane nodes chránia cluster state pred data/search pressure, ale stále potrebujú správny quorum a failure-domain model.

Nie každý endpoint má byť vystavený priamo každému clientovi. Použi load balancing, authentication a bounded coordinating path.

## 18. Cluster state

Cluster state obsahuje metadata ako:

- indexes,
- mappings,
- shard allocation,
- node membership,
- templates,
- policies a ďalšie metadata.

Príliš veľký cluster state môže vzniknúť pre:

- veľa indexes/shards,
- mapping explosion,
- veľa aliases/templates,
- nekontrolovaný tenant model.

Control-plane health je samostatná od data-node CPU alebo disk health.

## 19. Cluster health

Typický health model:

- **green** — všetky primary aj replica shards sú assigned,
- **yellow** — všetky primaries sú assigned, ale aspoň jedna replica nie,
- **red** — aspoň jeden primary shard nie je assigned.

Yellow na single-node lab clusteri môže byť očakávaný, ak replica nemá druhý node. V production môže signalizovať stratu redundancy.

Red znamená, že časť dát nemusí byť dostupná.

## 20. Shard allocation

Allocation ovplyvňuje:

- available nodes a roles,
- disk watermarks,
- awareness attributes/zones,
- include/exclude filters,
- tier preference,
- shard limits,
- recovery throttling,
- cluster state.

Pri unassigned shard nepoužívaj náhodné reroute commands. Najprv použi allocation explanation a oprav root constraint.

## 21. Ingest pipeline

Ingest pipeline môže pred indexingom vykonávať:

- parsing,
- field rename,
- date normalization,
- enrichment,
- geo/IP processing,
- redaction,
- drop/routing,
- failure handling.

Pipeline môže byť v:

- collectorovi,
- Fluent Bit,
- Logstash/Data Prepper/Elastic Agent,
- ingest node,
- application.

Definuj, ktorá vrstva je autoritou. Duplicitné parsing a rename rules vytvárajú drift.

## 22. Bulk ingestion

Bulk API znižuje per-document request overhead.

Trade-offy:

- väčší batch zvyšuje throughput,
- príliš veľký batch zvyšuje memory, retry cost a timeout risk,
- partial failures treba spracovať per item,
- retry celého batchu môže vytvárať duplicity.

Collector musí rozlišovať:

- `2xx` request s partial item failures,
- `429` backpressure,
- mapping `4xx` permanent failure,
- network timeout s nejasným outcome-om,
- authentication/authorization failure.

## 23. Search

Search query môže obsahovať:

- full-text query,
- exact term filter,
- range,
- boolean logic,
- existence,
- wildcard/regex,
- aggregations,
- sorting,
- pagination.

Filter context je vhodný pre exact constraints bez relevance scoringu.

Full-text query používa analyzers a scoring.

Log investigation typicky začína:

```text
time range
→ environment/service filter
→ event/error code
→ trace/request ID
→ message search
→ aggregation alebo sample documents
```

## 24. Expensive queries

Rizikové patterns:

- leading wildcard,
- regex nad high-cardinality fieldom,
- broad query cez dlhú retention,
- large aggregation cardinality,
- deep pagination,
- sorting nad nevhodným fieldom,
- scripts,
- runtime fields nad veľkým datasetom,
- query všetkých indexes cez wildcard.

Použi:

- presný time filter,
- data-stream/index scope,
- keyword fields,
- pre-aggregated/derived data podľa use case-u,
- query limits a cancellation,
- slow logs/profiling.

## 25. Aggregations

Aggregations poskytujú:

- counts,
- terms/top-N,
- histograms,
- percentiles,
- date histograms,
- cardinality estimates,
- nested buckets.

Terms aggregation nad user ID alebo trace ID môže spotrebovať veľa heap/network resources.

Pre stable SLO metrics nepoužívaj automaticky log aggregation namiesto native metric, ak log pipeline sampling, delay alebo loss mení denominator.

## 26. Near-real-time semantics

Search engine je near-real-time, nie strictly immediate.

Pri chýbajúcom čerstvom logu rozlišuj:

- collector neodoslal,
- indexing zlyhal,
- document je durable, ale ešte nie refreshed,
- query time range/timezone je chybný,
- data stream alias smeruje inam,
- ingest pipeline zmenila timestamp.

Manual refresh ako bežný fix zvyšuje overhead a maskuje nesprávne expectation.

## 27. Storage tiers

Time-series logs možno presúvať medzi výkonnostnými/storage tiers podľa veku a query potreby.

Trade-offy:

- hot tier — write a frequent queries,
- warm — menej writes, stále searchable,
- cold/frozen — lacnejšie, pomalšie alebo snapshot-backed podľa produktu,
- delete — retention koniec.

Tiering musí rešpektovať:

- incident investigation window,
- compliance,
- query SLO,
- restore time,
- snapshot availability,
- node/disk capacity.

## 28. Snapshots

Snapshot je backup indexes a cluster metadata podľa konfigurácie do external repository.

Replica shard nie je backup.

Snapshot plán musí riešiť:

- repository isolation,
- encryption,
- credentials,
- retention,
- cross-account/Region model,
- restore compatibility,
- lifecycle policies,
- test restore,
- system/security indexes.

Snapshot success nepreukazuje, že application dashboards, users a integrations možno obnoviť.

## 29. Security

Chráň:

- REST API,
- inter-node transport,
- Dashboards/Kibana,
- snapshot repository,
- ingest credentials,
- index/data-stream permissions,
- tenant boundaries,
- audit logs,
- encryption keys.

Použi:

- TLS,
- federated authentication,
- least-privilege roles,
- document/field-level controls podľa edície a use case-u,
- network segmentation,
- secret rotation,
- audit,
- dedicated service identities.

Log index môže obsahovať credentials alebo personal data. Field permissions nie sú náhradou producer-side minimization.

## 30. Multi-tenancy

Možnosti:

- samostatný cluster,
- index/data-stream per tenant,
- shared index s tenant fieldom,
- namespace/account segmentation,
- managed-service domain/project boundaries.

Trade-offy:

- isolation,
- shard count,
- mapping flexibility,
- noisy neighbor,
- lifecycle,
- query authorization,
- cost allocation.

Shared index s tenant filterom je bezpečný iba vtedy, ak authorization vrstva vynucuje filter a users nemajú obchádzajúci raw access.

## 31. Monitoring clusteru

Sleduj:

- cluster health,
- unassigned shards,
- node membership,
- cluster-state publication,
- JVM heap a GC,
- CPU/load,
- disk usage a watermarks,
- indexing rate/latency/failures,
- refresh/merge/flush,
- search rate/latency/rejections,
- thread-pool queues/rejections,
- segment count,
- shard count/size,
- cache hit/eviction,
- snapshot success,
- lifecycle errors,
- ingest pipeline failures.

Doplň synthetic document ingest a query, nie iba process health.

## 32. Troubleshooting: yellow alebo red cluster

```text
ktoré indexes/shards?
→ primary alebo replica?
→ allocation explanation
→ available nodes/roles?
→ disk watermarks?
→ awareness/tier/filter constraints?
→ shard limit?
→ recovery state?
→ node loss alebo repository restore?
```

Pri red stave prioritizuj primaries a ochranu existujúcich dát. Nevymaž index iba preto, aby cluster health zozelenel, bez potvrdenia data criticality.

## 33. Troubleshooting: disk watermark

Symptómy:

- shard relocation,
- allocation blocked,
- index read-only block,
- red/yellow health,
- indexing failures.

Postup:

1. identifikuj growth driver,
2. over lifecycle/rollover,
3. odstráň bezpečne expired data podľa policy,
4. rozšír capacity alebo presuň shards,
5. až potom odstráň read-only block,
6. over, že growth sa nevráti.

Ručné zvýšenie watermarku bez kapacity iba odloží failure.

## 34. Troubleshooting: mapping conflict

Over:

- failed document response,
- exact field path,
- current mapping,
- template priority,
- producer versions,
- ingest pipeline transformations,
- historical schema.

Poškodený document presuň do dead-letter/quarantine path. Nekonečne ho nere-tryuj.

## 35. Troubleshooting: indexing `429`

`429` typicky signalizuje backpressure alebo rejection.

Over:

- write thread pool/queue,
- ingest pipeline CPU,
- shard count a hot shards,
- bulk size/concurrency,
- refresh/merge pressure,
- disk/heap/GC,
- replicas,
- downstream lifecycle.

Client má použiť bounded exponential backoff s jitterom a preserved ordering/idempotency modelom.

## 36. Troubleshooting: vysoký heap a GC

Možné príčiny:

- príliš veľa shards,
- mapping/field explosion,
- high-cardinality aggregations,
- fielddata,
- broad queries,
- cache pressure,
- bulk concurrency,
- cluster-state size.

Nezvyšuj iba heap bez overenia compressed-oops/JVM a workload boundary. Najprv nájdi allocation driver.

## 37. Troubleshooting: pomalé queries

Over:

- time/index scope,
- query DSL a filters,
- shard fan-out,
- slow logs/profile,
- segment count,
- filesystem cache,
- heap/GC,
- hot threads,
- data tier,
- concurrent searches,
- aggregations a cardinality.

Query môže byť pomalý pre oversharding aj pre jeden extrémne veľký shard.

## 38. Troubleshooting: documents chýbajú

```text
source event
→ collector offset/buffer
→ bulk item response
→ ingest pipeline
→ target data stream/index
→ mapping failure
→ timestamp
→ refresh
→ query scope/timezone
→ lifecycle/delete
```

Zachovaj failed item payload v bezpečnej redacted forme a exact response.

## 39. Elasticsearch/OpenSearch oproti Loki

Použi Elasticsearch/OpenSearch, keď potrebuješ:

- rich field indexing,
- full-text search,
- complex document queries,
- broad analytics,
- document updates,
- ecosystem-specific security/search features.

Použi Loki, keď:

- query začína stabilnými labels,
- log body možno filtrovať po stream selection,
- object-storage-first cost model je prioritou,
- Grafana/Prometheus integration je dominantná,
- nepotrebuješ indexovať každý field.

Možný je aj hybridný model, ale duplicita logs zvyšuje cost, governance a consistency complexity.

## 40. Anti-patterny

### Daily index pre každú malú service

Vytvára veľa malých shards a cluster-state overhead.

### Dynamic mapping pre arbitrary JSON

Vedie k field explosion a conflicts.

### Jedna replica označená ako backup

Logical deletion sa replikuje.

### `refresh` po každom documente

Výrazne zvyšuje segment a merge overhead.

### Retry celého bulk requestu bez item analysis

Vytvára duplicity a permanent failure loop.

### Wildcard query cez všetky indexes

Zvyšuje shard fan-out a latency.

### Shared admin credentials v collectoroch

Compromise jedného agenta dáva cluster-wide access.

### Dashboard permissions ako jediná tenant isolation

Raw API alebo iný query path môže obísť UI.

## 41. Kontrolné otázky

1. Ako sa líši document, index a shard?
2. Čo je primary a replica shard?
3. Ako Lucene segments súvisia s refresh a merges?
4. Prečo je data stream vhodný pre logs?
5. Ako templates a mappings riadia schema?
6. Čo spôsobuje mapping explosion?
7. Aký je rozdiel medzi `keyword` a `text`?
8. Ako sa líši ILM a OpenSearch ISM na konceptuálnej úrovni?
9. Prečo je oversharding problém?
10. Čo znamená green, yellow a red health?
11. Ako diagnostikuješ unassigned shard?
12. Kedy zvoliť Loki a kedy Elasticsearch/OpenSearch?

## Glossary impact

Relevantné pojmy: Elasticsearch, OpenSearch, Lucene, document, index, primary shard, replica shard, segment, refresh, translog, data stream, backing index, write index, index template, component template, mapping, dynamic mapping, mapping explosion, `keyword`, `text`, analyzer, rollover, ILM, Data Stream Lifecycle, ISM, data tier, shard allocation, cluster state, disk watermark, bulk API, ingest pipeline a near-real-time search.

## Primárne zdroje

- [Elasticsearch data store](https://www.elastic.co/docs/manage-data/data-store)
- [Elasticsearch data streams](https://www.elastic.co/docs/manage-data/data-store/data-streams)
- [Elasticsearch clusters, nodes and shards](https://www.elastic.co/docs/deploy-manage/distributed-architecture/clusters-nodes-shards)
- [Elasticsearch ILM phases](https://www.elastic.co/docs/manage-data/lifecycle/index-lifecycle-management/index-lifecycle)
- [OpenSearch data streams](https://docs.opensearch.org/latest/im-plugin/data-streams/)
- [OpenSearch Index State Management](https://docs.opensearch.org/latest/im-plugin/ism/index/)
- [OpenSearch indexes and shards](https://docs.opensearch.org/latest/api-reference/index-apis/index/)
- [OpenSearch cluster health](https://docs.opensearch.org/latest/api-reference/cluster-api/cluster-health/)
