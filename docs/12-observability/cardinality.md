# Cardinality

Cardinality je počet unikátnych identities alebo kombinácií dimensions vytvorených telemetry contractom. Je to súčasne funkčný, cost, capacity a reliability parameter. Jeden dynamický label alebo promoted attribute môže rozmnožiť Prometheus series, Loki streams, trace-derived metrics, alert instances a document-index terms rýchlejšie, než rastie samotný traffic.

## 1. Dominantný mentálny model

```text
operational question a required drilldown
→ exact telemetry subject a dimension inventory
→ bounded/unbounded classification
→ expected values a combination model
→ cardinality budget a forbidden dimensions
→ producer/schema generation
→ backend identity multiplication
→ ingestion, memory, storage, query a alert cost
→ runtime limits a observed growth
→ capacity/cost/evidence verdict
→ containment
→ authoritative schema migration a historical retirement
→ user, telemetry a forbidden-outcome validation
```

Kritické rozlíšenie:

```text
viac detailu
≠ viac užitočnej observability

nižší retention
≠ nižšia active cardinality

hash unikátnej hodnoty
≠ zníženie počtu unikátnych hodnôt
```

## 2. Exact cardinality subject

Pri návrhu alebo incidente zaznamenaj:

```text
Cardinality subject ID:
Business/operational question:
Producer/service/release/tenant:
Signal a backend:
Metric/log/trace/document identity:
Dimension/field inventory:
Expected distinct values a combinations:
Current active count a churn:
Budget/limit generation:
Retention a cost owner:
Dependent dashboards/rules/SLOs:
Forbidden dimensions:
Observation window a evidence cut-off:
```

„Máme veľa series“ nestačí. Treba poznať producer generation, exact metric/stream/index/derived signal, dimension a tenant, ktorý rast vytvoril.

## 3. Volume, cardinality a churn

### Volume

Počet records, samples, spans alebo bytes za čas.

### Cardinality

Počet unikátnych identities alebo indexed combinations.

### Churn

Rýchlosť vzniku a zániku identities.

```text
nízky volume + milión unikátnych IDs
→ metadata/memory problém

vysoký volume + malý stabilný label set
→ throughput problém

mierny active count + rýchly ephemeral churn
→ WAL/index/compaction/recovery problém
```

Tieto tri osy sa merajú samostatne.

## 4. Combinatorial growth

Ak dimensions majú teoretické počty hodnôt:

```text
environment: 3
region: 4
service: 40
operation: 25
status_class: 5
```

potenciálny priestor je:

```text
3 × 4 × 40 × 25 × 5 = 60 000 combinations
```

Pridanie `merchant_id` s 80 000 hodnotami nevytvorí „iba jeden label navyše“. Potenciálny priestor narastie o faktor 80 000.

Nie všetky kombinácie sa objavia, ale budget sa nesmie spoliehať na dočasne nízky traffic.

## 5. Bounded a unbounded dimensions

### Bounded

Kontrolovaný a stabilný set:

- environment;
- Region;
- service;
- normalized route/operation;
- HTTP method;
- status class;
- deployment ring;
- bounded customer tier.

### Unbounded alebo effectively unbounded

Rastú s každou operáciou, používateľom alebo instance:

- request, trace, session, order alebo merchant ID;
- raw URL;
- timestamp;
- full SQL statement;
- exception message;
- Pod UID alebo Job run ID;
- arbitrary Kubernetes label/annotation;
- user-defined JSON key.

Unbounded field môže byť oprávnený v log/trace body alebo exact-search indexe. To však neznamená, že patrí do metric labels, Loki stream labels, alert identity alebo trace-derived metric dimensions.

## 6. Cardinality budget

Budget definuje:

- allowed dimensions;
- expected distinct values a growth;
- active identities a churn limit;
- per-service/per-tenant quota;
- retention a storage tier;
- query a alert dependencies;
- cost ownera;
- runtime enforcement;
- exception a expiry process.

Príklad:

```text
Signal: settlement.duration
Backend: Prometheus
Required dimensions: service, normalized_operation, status_class, region, merchant_tier
Forbidden: merchant_id, trace_id, settlement_id, raw_url
Expected active series: < 30 000/service
Churn guardrail: < 5 % active count/hour
Review trigger: +20 % after release
```

Budget je acceptance contract instrumentation change-u, nie iba platform capacity spreadsheet.

## 7. Prometheus identity multiplication

Prometheus series identity:

```text
metric name + celý label set
```

Classic histogram vytvára pre každý label set:

```text
N bucket series + _sum + _count
```

Histogram s 15 buckets a 100 000 label combinations vytvorí približne 1.7 milióna series.

Dopady:

- head memory;
- WAL a replay;
- disk/compaction;
- remote-write bandwidth a backlog;
- rule/query fan-out;
- startup a recovery time.

Recording rule môže cardinality znížiť agregáciou alebo zvýšiť zachovaním ephemeral labels. Output rule má vlastný budget.

Metric relabeling je silný emergency control, ale broad drop bez dependency inventory môže odstrániť SLO numerator alebo saturation evidence.

## 8. Loki streams

Loki stream identity:

```text
tenant + úplný label set
```

High-cardinality labels vytvárajú:

- veľa active streams;
- malé neefektívne chunks;
- ingester memory a stream-limit pressure;
- index/object-store operations;
- broad query fan-out.

Trace/request/customer identity patrí typicky do structured metadata alebo body. Kubernetes workload name môže byť label; Pod UID typicky nie.

Odstránenie labelu z nových entries nezmaže historical streams okamžite. Recovery zahŕňa ich prirodzený retention lifecycle.

## 9. Elasticsearch/OpenSearch fields a mappings

High-cardinality `keyword` field môže byť oprávnený pre exact search, ale zvyšuje:

- index size;
- term dictionaries/global ordinals;
- aggregation memory;
- heap a query latency;
- snapshot/restore volume.

Samostatný problém je mapping explosion: veľké množstvo field names, často z arbitrary JSON keys alebo Kubernetes annotations. To zväčšuje cluster state a môže blokovať ingestion.

Controls:

- explicit template/mapping generation;
- `dynamic: false` alebo strict podľa use case-u;
- field allowlist;
- flattened/raw object pre bounded search potrebu;
- field-count limits;
- rollover a schema quarantine.

Nie každý field v `_source` musí byť indexed alebo aggregatable.

## 10. Traces a derived metrics

Trace/span IDs sú prirodzene unikátne, ale hlavný platform risk vzniká pri:

- indexed/promoted attributes;
- raw span names;
- attribute search cez dlhú retention;
- metrics-generator dimensions;
- service-graph fragmentation.

Span metrics nad dimensions ako `service`, `span.kind`, `status` a normalized operation môžu byť bounded. `trace_id`, user ID, full URL alebo SQL statement v derived metric vytvára Prometheus incident.

Sampling znižuje volume, nie automaticky cardinality každého indexed attribute. Rare unikátne values môžu zostať vysoko variabilné aj v sampled population.

## 11. Alerts a dashboards ako multiplikátory

Alert rule môže vytvoriť jednu alert instance na každý output label set. Per-Pod alebo per-customer output môže zmeniť telemetry cardinality na pager storm.

Dashboard variables a repeating panels môžu expandovať každý label value:

```text
values × panels × queries × viewers × refresh cadence
```

Default overview má byť agregovaný. Exact instance/tenant detail patrí do bounded drilldownu alebo searchu.

## 12. Multi-tenancy a cost attribution

Shared platform potrebuje per-tenant limits:

- series/stream/field count;
- ingestion rate;
- new-identity rate;
- label count/value limits;
- query range a concurrency;
- retention tiers;
- cost attribution.

Globálny limit bez producer attribution iba presunie incident na platform team. Cost visibility vytvára feedback medzi instrumentation detailom a jeho skutočnou hodnotou.

## 13. Detection a evidence

Sleduj:

- active series/streams;
- new identities rate a churn;
- top metrics/labels/fields podľa distinct count;
- histogram bucket multiplication;
- field count a cluster-state growth;
- rejected samples/streams/documents;
- remote-write alebo backend backlog;
- query scanned bytes/series/shards;
- alert instances;
- top tenants a release correlation;
- cost per service/signal.

Deployment annotation bez producer/schema generation nestačí. Exact dimension diff je diskriminačný dôkaz.

## 14. Worked failure: jeden `merchant_id`, štyri platformové incidenty

### Subject

```text
Incident: CARD-PAY-46
Release: provider-adapter 7.23.0
Change: merchant_id promoted for per-merchant debugging
Metric generation: METRIC-124
Loki label generation: LOKI-LABEL-37
Tempo metrics-generator generation: TEMPO-MG-22
Alert rule generation: ALERT-72
Tenants: payments-prod
Window: 02:00–02:22 UTC
```

### Change

Rovnaký dynamic field bol pridaný do:

```text
Prometheus histogram label: merchant_id
Loki stream label: merchant_id
Tempo span-metrics dimension: merchant_id
Alert output labels: merchant_id
```

Počet active merchantov v okne bol 46 000.

### Symptómy

```text
Prometheus active series: 210 000 → 5.4 million
new series rate: 38 000/s peak
remote-write oldest sample: 19 min
Prometheus replica 2: OOM restart

Loki active streams: 82 000 → 2.1 million
ingester stream-limit rejections: rising
chunk utilization: sharply down

Tempo metrics-generator series: 160 000 → 3.8 million
metrics-generator queue: saturated

Alert instances: 18 → 12 400
Alertmanager notification groups: 9 700+
```

Business settlement traffic vzrástol iba o 6 %.

### Competing hypotheses

1. legitímny traffic spike;
2. duplicate scrape targets;
3. retry amplification;
4. histogram bucket expansion;
5. new merchant dimension;
6. Kubernetes Pod churn;
7. remote backend outage;
8. alert rule zachovala unbounded output label.

### Discriminating evidence

```text
request/log/span volume: +6 až +9 %
distinct merchant_id: 46 000
series/streams grouped without merchant_id: near baseline
release/schema diff: merchant_id added in all four pipelines
Prometheus top label distinct count: merchant_id
Loki top stream label: merchant_id
Tempo generated metric dimensions: merchant_id present
alert fingerprints differ only by merchant_id
```

Mechanizmus:

```text
one per-operation identifier
→ promoted do multiple indexed identities
→ combinations sa rozmnožia per operation/status/region/bucket
→ active metadata a churn rastú
→ Prometheus/Loki/Tempo queues a memory sa saturujú
→ queries/rules zaostávajú
→ alert output vytvorí tisíce identities
→ observability platforma degraduje počas business incidentu
```

### Containment

- zastaviť rollout instrumentation generation;
- zachovať schema/config diff a top-dimension evidence;
- odstrániť `merchant_id` z new Prometheus/Loki/metrics-generator/alert identities cez presný emergency control;
- ponechať business SLI a service/Region/merchant-tier dimensions;
- chrániť backends tenant limitmi a query concurrency;
- nehashovať merchant ID ako údajný cardinality fix;
- ponechať exact identifier v redacted structured log/trace field-e s bounded retention a accessom.

### Authoritative recovery

1. zaviesť `merchant_tier` ako bounded operational dimension;
2. ponechať `merchant_id` iba v approved exact-search fields;
3. opraviť SDK views, Collector/Fluent Bit transforms, Loki labels, Tempo dimensions a alert aggregation;
4. vytvoriť CI cardinality fixture s 50 000 merchant IDs;
5. canary-nuť jednu service/tenant cohortu;
6. overiť active count, churn, backlog a query latency;
7. počkať na retirement historical streams/series/index terms podľa backend lifecycle-u;
8. prepočítať cost a capacity budget.

### Acceptance verdict

Recovery je prijatá, keď:

- active series/streams a generated metrics sú pod budgetom;
- churn a backlog sa vrátia k baseline;
- SLO, saturation a alert inputs zostanú kompletné;
- exact merchant lookup funguje iba v schválenom log/trace search path-e;
- alert vytvorí service/Region incident, nie per-merchant storm;
- forbidden ID nie je metric/Loki/alert dimension;
- neighboring tenant neregresuje;
- druhý rollout/restart nevytvorí nový identity spike.

## 15. Containment a remediation lifecycle

```text
protect platform
→ stop new identity creation
→ locate producer/dimension
→ preserve critical signals
→ apply minimal bounded drop/normalization
→ validate dependencies
→ migrate authoritative schema
→ retire historical identities
→ update budget, cost a CI guardrail
```

Emergency drop je containment. Authoritative recovery opravuje producer a všetky downstream promotions.

## 16. Normalization a aggregation

Bezpečné príklady:

```text
/orders/981723/items/55
→ /orders/{order_id}/items/{item_id}
```

```text
merchant_id
→ merchant_tier
```

```text
HTTP 503
→ status_class=5xx
```

```text
connection failed to db-17 at 10.0.4.18
→ error_type=DB_CONNECTION_FAILED
```

Raw detail môže zostať v bounded-retention log alebo trace evidence. Aggregation nesmie odstrániť Region, tenant tier alebo failure-domain dimension potrebnú na rozhodnutie.

Hashing nemení počet distinct values. Je privacy transformácia, nie cardinality transformácia.

## 17. Prevention v delivery pipeline

Instrumentation change musí prejsť:

```text
schema/dimension diff
→ bounded/unbounded classification
→ representative distinct-value fixture
→ series/stream/index estimate
→ forbidden-dimension policy
→ privacy a cost review
→ dashboard/rule dependency test
→ canary runtime count/churn
→ promotion alebo rollback
```

Runtime enforcement:

- SDK metric views;
- Collector processors;
- Prometheus relabeling a limits;
- Loki label allowlists/tenant limits;
- Fluent Bit filters;
- Tempo metrics-generator dimension allowlist;
- explicit search mappings;
- alert aggregation policy.

Každý runtime drop musí mať counter a ownera.

## 18. Troubleshooting model

### Prometheus

```text
metric name
→ top label combinations
→ active count vs churn
→ histogram buckets
→ scrape/recording duplication
→ producer/config generation
→ remote-write/backlog impact
```

### Loki

```text
tenant active streams
→ top label/value counts
→ stream churn/chunk utilization
→ collector label mapping
→ release generation
→ limits/rejections
```

### Search backend

```text
data stream/index
→ field/mapping count
→ high-cardinality keyword terms
→ dynamic field creation
→ shard/heap/query impact
→ template generation
```

### Tracing/derived metrics

```text
span attribute/name inventory
→ indexed/promoted dimensions
→ service graph/metrics-generator output
→ sampling population
→ downstream Prometheus cardinality
```

## 19. Anti-patterny

### Unique ID ako metric alebo stream label

Time-series/log-stream store sa používa ako event database.

### Hashovanie ako fix

Milión IDs zostáva miliónom hashov.

### Kratšia retention ako jediná remediation

Active memory/index identities zostanú počas ingestu.

### Broad drop bez dependency inventory

Môže odstrániť SLO alebo incident evidence.

### Všetky Kubernetes labels automaticky

Producer nemá bounded schema ani privacy control.

### High-cardinality field „pre istotu“

Platí sa permanentný index cost bez query use case-u.

## 20. Kontrolné otázky

1. Čo tvorí exact cardinality subject?
2. Aký je rozdiel medzi volume, active cardinality a churn?
3. Ako vzniká combinatorial growth?
4. Kedy je dimension bounded alebo effectively unbounded?
5. Prečo histogram násobí series?
6. Ako sa líši Prometheus series, Loki stream a indexed document field?
7. Prečo sampling alebo hashing automaticky nerieši cardinality?
8. Ako trace attributes vytvoria downstream metric cardinality?
9. Čo musí obsahovať per-tenant budget?
10. Ako alert labels a dashboard variables násobia incident impact?
11. Aký je rozdiel medzi containment dropom a authoritative schema recovery?
12. Ako overíš, že remediation zachovala critical evidence?

## Glossary impact

Relevantné pojmy: cardinality subject, dimension inventory, active-cardinality verdict, identity-churn rate, combination-space estimate, cardinality-budget generation, forbidden-dimension contract, cross-signal cardinality amplification, historical-identity retirement, exact-search exception, cardinality containment, cardinality recovery generation, producer cost attribution a cardinality acceptance verdict.

## Primárne zdroje

- [Prometheus data model](https://prometheus.io/docs/concepts/data_model/)
- [Prometheus instrumentation practices](https://prometheus.io/docs/practices/instrumentation/)
- [Loki cardinality](https://grafana.com/docs/loki/latest/get-started/labels/cardinality/)
- [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
- [OpenTelemetry metrics data model](https://opentelemetry.io/docs/specs/otel/metrics/data-model/)
- [Elasticsearch mappings](https://www.elastic.co/docs/manage-data/data-store/mapping)
- [OpenSearch field types](https://docs.opensearch.org/latest/field-types/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Alert design a alert fatigue](alert-design-alert-fatigue.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CIA triáda →](../13-security-and-identity/cia-triad.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
