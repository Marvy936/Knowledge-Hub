# Cardinality

Cardinality je počet unikátnych hodnôt alebo kombinácií dimensions v telemetry a indexed data modeli. V observability systémoch je cardinality zároveň funkčný, nákladový aj reliability parameter. Nesprávne zvolený label, attribute alebo indexed field môže vytvoriť milióny nových time series, log streams, trace indexes alebo document terms a destabilizovať ingestion, memory, storage aj query vrstvu.

## 1. Mentálny model

```text
počet dimensions
× počet možných hodnôt každej dimension
× kombinácie, ktoré sa reálne objavia
→ cardinality
→ počet series, streams, buckets, terms alebo index entries
→ memory, storage, CPU, network a query cost
```

Cardinality nie je iba počet labels. Aj niekoľko labels s veľkým alebo nekontrolovaným priestorom hodnôt môže byť nebezpečných.

## 2. Cardinality oproti volume

### Volume

Koľko records alebo bytes systém spracuje.

Príklady:

- 100 000 log lines za sekundu,
- 10 000 spans za sekundu,
- 1 milión metric samples za minútu.

### Cardinality

Koľko unikátnych identities alebo indexed combinations vznikne.

Príklady:

- počet Prometheus time series,
- počet Loki log streams,
- počet unikátnych values v indexed OpenSearch field-e,
- počet span attribute values používaných pri search indexe.

Vysoký volume s nízkou cardinality môže byť zvládnuteľný cez throughput scaling. Nízky volume s extrémnou cardinality môže vyčerpať memory a metadata limits.

## 3. Combinatorial growth

Príklad labels:

```text
environment: 3
region: 4
service: 100
operation: 50
status: 5
```

Teoretický priestor:

```text
3 × 4 × 100 × 50 × 5 = 300 000 kombinácií
```

Ak pridáš:

```text
customer_id: 100 000
```

potenciálny priestor exploduje.

Nie všetky kombinácie sa musia reálne objaviť, ale návrh sa nemá spoliehať na náhodne nízku aktivitu.

## 4. Bounded a unbounded dimensions

### Bounded

Majú malý, kontrolovaný a stabilný set hodnôt.

Príklady:

- environment,
- Region,
- HTTP method,
- status class,
- deployment ring,
- service,
- normalized route.

### Unbounded alebo effectively unbounded

Hodnoty rastú s každou operáciou, používateľom alebo resource instance.

Príklady:

- request ID,
- trace ID,
- user ID,
- order ID,
- session ID,
- raw URL,
- exception message,
- timestamp,
- full SQL statement,
- Pod UID,
- random file path.

Takéto hodnoty patria do logs, trace attributes, structured metadata alebo document body podľa use case-u, nie automaticky do indexed labels.

## 5. Cardinality budget

Každý telemetry contract má mať cardinality budget.

Definuj:

- povolené dimensions,
- očakávaný počet hodnôt,
- max series/streams/documents per service alebo tenant,
- growth trend,
- retention,
- cost ownera,
- enforcement a alerting,
- exception process.

Príklad:

```text
Metric: http.server.request.duration
Required dimensions: service, route, method, status_class, region
Forbidden dimensions: user_id, request_id, trace_id, raw_url
Expected active series: < 20 000 per service
Review trigger: +25 % week-over-week
```

## 6. Prometheus cardinality

Prometheus time series identity je:

```text
metric name + celý label set
```

Každá unikátna kombinácia vytvorí samostatnú series.

Dopad:

- head memory,
- WAL a disk,
- compaction,
- remote write,
- query fan-out,
- recording rules,
- startup a recovery.

### Rizikové labels

- `user_id`,
- `request_id`,
- `trace_id`,
- raw `path`,
- error text,
- container ID,
- dynamic target metadata.

### Series churn

Churn je rýchle vytváranie a zánik series.

Príklady:

- ephemeral Pods s instance labels,
- batch jobs s unique run ID,
- autoscaling workload,
- dynamic route labels.

Aj keď počet active series nie je extrémny, vysoký churn zaťažuje WAL, compaction a downstream storage.

## 7. Histograms a cardinality

Classic Prometheus histogram vytvára pre každý label set viac series:

- bucket pre každý boundary,
- `_sum`,
- `_count`.

Ak má histogram 15 buckets a 10 000 label combinations, vznikne približne 170 000 series.

Preto:

- obmedz labels,
- zvoľ potrebné buckets,
- používaj recording rules pre drahé queries,
- vyhodnoť native histogram support a backend compatibility,
- neaplikuj histogram na každú granular operation bez use case-u.

## 8. Recording rules

Recording rules môžu cardinality:

- znížiť agregáciou,
- zachovať pre critical dimensions,
- alebo zvýšiť vytvorením ďalších series.

Dobrý rule:

```promql
sum by (service, route) (
  rate(http_requests_total[5m])
)
```

Rizikový rule zachová všetky ephemeral labels alebo pridáva nové dynamické labels.

Recording-rule output má mať vlastný budget a naming contract.

## 9. Relabeling a metric filtering

Prometheus `metric_relabel_configs` môže:

- dropnúť nepotrebné metrics,
- odstrániť labels,
- normalizovať values,
- obmedziť vysokú cardinality pred storage.

Riziká:

- silent poškodenie dashboardov a SLO,
- odlišná konfigurácia medzi replicas,
- nejasný owner,
- odstránenie diagnosticky dôležitého signalu.

Filter testuj na sample exposition a dependency inventory.

## 10. Loki cardinality

Loki log stream je definovaný label setom.

Vysoká stream cardinality spôsobuje:

- veľa active streams,
- malé a zle využité chunks,
- vyšší index overhead,
- vyššiu memory potrebu ingesterov,
- drahšie query planning,
- rate-limit alebo stream-limit failures.

Loki odporúča používať málo stabilných labels. Unikátne hodnoty ako trace ID, user ID, IP alebo order ID patria do log body alebo structured metadata, nie do indexed stream labels.

### Príklad

Vhodné labels:

```text
cluster, namespace, service, environment, level
```

Nevhodné:

```text
pod_uid, request_id, trace_id, user_id, filename s random suffixom
```

## 11. Loki stream churn

Ephemeral Kubernetes labels môžu vytvárať nové streams pri každom rolloute.

Over:

- Pod name oproti workload identity,
- container restart,
- dynamic annotations,
- filename,
- label drop rules,
- structured metadata.

Nie každá Kubernetes metadata hodnota má byť Loki label.

## 12. Elasticsearch a OpenSearch cardinality

Lucene-based systémy indexujú field values a terms.

High-cardinality `keyword` fields môžu zvyšovať:

- index size,
- global ordinals,
- aggregation memory,
- query latency,
- heap pressure,
- shard overhead.

Príklady:

- user ID,
- session ID,
- IP address,
- URL,
- trace ID,
- UUID.

Na rozdiel od Prometheus nemusí byť high-cardinality field automaticky zakázaný. Môže byť potrebný na exact search. Musí však mať explicitný search, aggregation, mapping a retention use case.

### Indexed oproti stored

Field možno:

- indexovať pre search,
- ukladať v `_source`,
- použiť pre aggregations podľa mappingu,
- vypnúť alebo obmedziť podľa potreby.

Nie každý field v documente musí byť indexed a aggregatable.

## 13. Mapping explosion

Dynamic mapping môže vytvoriť tisíce nových field names.

Príčiny:

- arbitrary JSON keys,
- tenant-defined metadata,
- dynamic labels uložené ako object fields,
- flattened business payload,
- Kubernetes annotations.

Dopad:

- veľký cluster state,
- heap pressure,
- mapping conflicts,
- ingestion rejection,
- pomalé updates.

Controls:

- explicit templates,
- `dynamic: false` alebo strict model podľa use case-u,
- flattened field type,
- allowlist,
- field-count limits,
- schema versioning.

## 14. Trace cardinality

Trace storage zvyčajne ukladá unikátne trace/span IDs, ale hlavný cardinality problém vzniká pri indexed alebo promoted attributes.

Rizikové attributes:

- raw URL,
- SQL statement,
- user ID,
- request ID,
- arbitrary tool arguments,
- prompt text,
- exception message.

Dopad:

- index/storage growth,
- query cost,
- privacy risk,
- service graph fragmentation,
- metrics-generator series explosion.

Span attributes môžu byť užitočné na exact trace lookup bez toho, aby sa všetky používali ako indexed dimensions alebo derived metrics labels.

## 15. Trace-derived metrics

Span metrics generátor môže vytvoriť RED metrics podľa span attributes.

Ak zahrnieš high-cardinality attributes, vznikne Prometheus cardinality incident.

Bezpečné dimensions:

- service,
- span kind,
- status,
- normalized operation,
- bounded peer service.

Rizikové:

- trace ID,
- user ID,
- full endpoint,
- database statement,
- message ID.

## 16. OpenTelemetry attribute limits

SDK alebo Collector môže obmedzovať:

- počet attributes,
- value length,
- počet events,
- počet links,
- cardinality metrics streams podľa implementation.

Limits chránia runtime, ale môžu silent odstrániť diagnostický context.

Monitoruj dropped attributes a dokumentuj priority fields.

## 17. Resource attributes a cardinality

Resource identity je potrebná, ale nie každá resource hodnota patrí do každého backendového indexu.

Príklad:

- `service.name` je stabilná logical identity,
- `service.instance.id` je unikátna instance identity.

`service.instance.id` môže byť užitočné v traces/logs, ale ako dimension na všetkých long-term metrics môže vytvárať churn.

Pri resource-to-label mappingu vytvor allowlist.

## 18. Kubernetes cardinality

Kubernetes je prirodzene dynamické prostredie.

Riziká:

- Pod names,
- Pod UIDs,
- ReplicaSet hashes,
- container IDs,
- arbitrary labels/annotations,
- Job run IDs,
- owner references.

Preferuj stabilné workload identity:

- cluster,
- namespace,
- workload kind,
- workload name,
- service,
- environment.

Ephemeral identity ponechaj iba tam, kde je potrebná na krátkodobý troubleshooting.

## 19. Multi-tenancy

Cardinality musí byť riadená per tenant, nie iba globálne.

Controls:

- series/stream limits,
- ingestion rate limits,
- label count/value limits,
- query concurrency,
- maximum query range,
- shard/field limits,
- retention tiers,
- quotas a cost attribution.

Bez tenant limits môže jeden tím destabilizovať shared observability platformu.

## 20. Cost model

Cardinality ovplyvňuje:

- ingestion pricing,
- active-series pricing,
- index storage,
- memory,
- object-store requests,
- query compute,
- remote-write bandwidth,
- retention,
- backup a replication.

Cost attribution podľa service/team/tenant vytvára spätnú väzbu pre instrumentation decisions.

Bez cost visibility vzniká observability tragedy of the commons.

## 21. Detection

Sleduj:

- active series/streams,
- new series/streams rate,
- series churn,
- top metrics podľa series count,
- top labels podľa distinct values,
- ingestion bytes,
- index size,
- field count,
- rejected samples/streams/documents,
- query scanned data,
- top tenants,
- growth po deploymente.

Deployment annotations pomáhajú korelovať cardinality spike s instrumentation zmenou.

## 22. Prometheus investigation

Otázky:

- Ktoré metric names majú najviac series?
- Ktoré labels majú najviac distinct values?
- Ktorý job/tenant/service rastie?
- Je problém active count alebo churn?
- Vznikla nová metric alebo nový label?
- Zmenil sa histogram bucket count?
- Recording rule duplikuje raw dimensions?

Použi TSDB status a backend-specific cardinality tooling podľa deploymentu.

## 23. Loki investigation

Over:

- top labels a values,
- active streams per tenant,
- streams per service,
- chunk utilization,
- rejected streams,
- label set po collector pipeline,
- deployment alebo Kubernetes metadata change.

`trace_id` alebo `request_id` ako label je častý okamžitý root cause.

## 24. Search-index investigation

Over:

- index mappings,
- field count,
- top high-cardinality keyword fields,
- global ordinals,
- shard size/count,
- aggregation queries,
- dynamic field creation,
- data stream/template change.

Odstránenie field mappingu neopraví automaticky už existujúce indexes; môže byť potrebný rollover/reindex alebo retention-based recovery.

## 25. Prevention v CI/CD

Instrumentation change má prejsť:

- schema diff,
- label/attribute allowlist,
- representative load test,
- estimated series/stream count,
- forbidden-dimension checks,
- dashboard/SLO dependency test,
- privacy scan,
- cost estimate.

Príklad testu:

```text
new dimension: customer_id
expected distinct values: 250 000/day
backend use: exact log search only
allowed as metric label: no
allowed as Loki stream label: no
allowed as structured log field: yes, with retention/privacy policy
```

## 26. Runtime enforcement

Controls:

- SDK views,
- Collector filter/transform processors,
- Prometheus relabeling,
- Loki label allowlists a limits,
- Fluent Bit filters,
- index templates,
- attribute promotion allowlists,
- tenant quotas.

Runtime drop musí byť monitorovaný. Silent data removal môže vytvoriť observability gap.

## 27. Remediation

Pri cardinality incidente:

1. zastav ďalší rast,
2. identifikuj producer a dimension,
3. dropni alebo normalize-nuť problematickú hodnotu,
4. chráň platformu limitmi,
5. zachovaj critical signals,
6. vyhodnoť existing data cleanup/retention,
7. oprav dashboards/rules,
8. pridaj CI guardrail,
9. vykonaj cost a incident review.

Emergency drop rule má byť minimálna a auditovaná.

## 28. Normalization

Príklady:

Raw URL:

```text
/orders/981723/items/55
```

Normalized route:

```text
/orders/{order_id}/items/{item_id}
```

Error message:

```text
connection failed to db-17 at 10.0.4.18
```

Normalized error type:

```text
DB_CONNECTION_FAILED
```

Raw detail môže zostať v log body alebo trace evente.

## 29. Hashing

Hashing unique value neznižuje cardinality. Milión unikátnych user IDs vytvorí milión unikátnych hashov.

Hash môže pomôcť s pseudonymizáciou, nie s cardinality reduction.

## 30. Aggregation

Cardinality možno znížiť agregáciou:

- status code → status class,
- raw endpoint → route template,
- instance → service/workload,
- exact customer → customer tier,
- error message → error type,
- exact latency → histogram buckets.

Aggregation musí zachovať decision use case.

Príliš agresívna agregácia skryje regionálny alebo tenant-specific incident.

## 31. Retention tiers

Nie všetka granular telemetry potrebuje rovnakú retention.

Príklad:

- per-instance metrics: 7 dní,
- service aggregates: 13 mesiacov,
- detailed logs: 14 dní,
- audit logs: podľa compliance,
- sampled traces: 7–30 dní,
- SLO recording rules: dlhodobé.

Retention znižuje storage cost, ale nerieši active memory/index cardinality počas ingestionu.

## 32. Privacy a security

High-cardinality identifiers často obsahujú osobné alebo citlivé údaje.

Controls:

- data classification,
- minimization,
- hashing/tokenization podľa threat modelu,
- access control,
- retention,
- deletion,
- audit,
- tenant isolation.

Technicky queryovateľný field nie je automaticky oprávnený na zber.

## 33. Cardinality a alerting

Alert rule môže vytvoriť jednu alert instance pre každý output label set.

Riziká:

- alert storm,
- Alertmanager memory/routing load,
- stovky notifications,
- silences sa ťažko matchujú.

Agreguj alert condition na actionable scope:

```text
service + cluster + symptom
```

nie automaticky na každý Pod alebo request.

## 34. Cardinality a dashboards

Dashboard variables a repeating panels môžu queryovať každý label value.

Riziká:

- tisíce variable options,
- query storm,
- browser overload,
- backend fan-out.

Použi:

- bounded variables,
- search/filter,
- top-N,
- drilldown,
- query limits,
- default aggregate view.

## 35. Anti-patterny

### Unique ID ako metric label

Time-series systém sa používa ako event database.

### Všetky Kubernetes labels automaticky exportované

Arbitrary metadata vytvára nekontrolované series a streams.

### Hashovanie ako cardinality fix

Počet unikátnych hodnôt zostáva rovnaký.

### High-cardinality field indexovaný „pre istotu“

Platí sa index cost bez reálneho query use case-u.

### Riešenie iba kratšou retention

Active series/streams stále zaťažujú ingestion a memory.

### Drop bez dependency analýzy

SLO, alerts alebo investigation workflow stratia vstup.

### Global limit bez tenant attribution

Nie je možné identifikovať ani motivovať problematického producenta.

## 36. Kontrolné otázky

1. Aký je rozdiel medzi volume a cardinality?
2. Ako vzniká combinatorial growth?
3. Čo je bounded a unbounded dimension?
4. Ako cardinality ovplyvňuje Prometheus TSDB?
5. Čo je series churn?
6. Prečo Loki indexuje iba málo stabilných labels?
7. Kedy môže byť high-cardinality OpenSearch field oprávnený?
8. Čo je mapping explosion?
9. Ako trace-derived metrics vytvoria metrics cardinality?
10. Prečo hashing neznižuje cardinality?
11. Ako nastaviť cardinality budget?
12. Ako postupovať pri cardinality incidente?

## Glossary impact

Relevantné pojmy: cardinality, bounded dimension, unbounded dimension, combinatorial cardinality, active series, active stream, series churn, stream churn, cardinality budget, mapping explosion, global ordinals, promoted trace attribute, attribute allowlist, cardinality incident, normalization, observability cost attribution a telemetry tragedy of the commons.

## Primárne zdroje

- [Prometheus data model](https://prometheus.io/docs/concepts/data_model/)
- [Prometheus instrumentation practices](https://prometheus.io/docs/practices/instrumentation/)
- [Loki cardinality](https://grafana.com/docs/loki/latest/get-started/labels/cardinality/)
- [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
- [Elasticsearch mappings](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html)
- [OpenSearch mappings](https://docs.opensearch.org/latest/field-types/)
