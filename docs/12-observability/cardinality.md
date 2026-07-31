# Cardinality

Cardinality je počet unikátnych identities alebo kombinácií dimensions vytvorených telemetry contractom. Je to súčasne funkčný, cost, capacity a reliability parameter. Jeden dynamický label alebo promoted attribute môže rozmnožiť Prometheus series, Loki streams, trace-derived metrics, alert instances a search-index terms rýchlejšie, než rastie samotný traffic.

Cardinality nie je abstraktné „príliš veľa labels“. Potrebuje presný subject: ktorý signal, ktoré dimensions, koľko values existuje súčasne, ako často churnujú, aké combinations reálne vznikajú a ktorá backend boundary ich drží v memory/index/storage.

## Cardinality lifecycle

```text
operational question a required drilldown
→ dimension inventory
→ bounded/unbounded a sensitive classification
→ value-count a combination model
→ series/stream/document/alert identity
→ ingest, memory, index a query cost
→ budget a forbidden dimensions
→ schema validation a rollout canary
→ runtime growth detection
→ containment a migration
→ retirement starej identity
```

Detail potrebný na investigation nemusí byť indexed dimension. Request ID môže byť trace/log lookup field. Pod name môže byť structured metadata. Payment ID môže zostať v protected document body. Label sa používa iba vtedy, keď pomáha selektovať alebo agregovať stable operational cohort.

## Exact cardinality subject

Atlas používa `CARD-PAY-43`:

```yaml
metric: payment_settlement_completed_total
boundedLabels:
  environment: 3
  provider: 4
  merchant_class: 3
  result: 5
  region: 2
  availability_zone: 6
  release_channel: 3
forbiddenLabels:
  - payment_id
  - payment_operation_id
  - trace_id
  - raw_http_path
  - exception_message
budgets:
  activePrometheusSeries: 2000000
  activeLokiStreamsPerTenant: 250000
  pageAlertInstancesPerRule: 50
  searchMappedFieldsPerDataset: 1000
```

Theoretical maximum pre metric je product label value counts, ale actual active series závisia od combinations a churn. `3×4×3×5×2×6×3 = 6480` potential series je ešte len jedna metric family. Histogram s 15 buckets vytvorí bucket series plus sum/count a násobí footprint.

## Prometheus series identity

Prometheus series identity je metric name plus complete label set. Dynamic `payment_id` vytvorí novú series pre každú operation:

```text
payment_settlement_duration_seconds_count{payment_id="P-884"}
payment_settlement_duration_seconds_count{payment_id="P-885"}
...
```

Tento design nedáva aggregation benefit a drží series state v producer registry, scrape payload, Prometheus head/WAL, remote write a backend indexe.

Current cardinality inspection:

```promql
count({__name__!=""})
```

Táto query môže byť veľmi drahá a v large system-e sa nepoužíva bez scope-u. Lepšie je analyzovať konkrétnu metric:

```promql
count by (__name__) (
  payment_settlement_completed_total
)
```

Výsledok preukazuje active/queryable series v selected Prometheus evaluation time. Nepreukazuje churned historical series ani producer-side registry memory.

TSDB status:

```bash
curl -fsS http://prometheus:9090/api/v1/status/tsdb \
  | jq '.data | {headStats, seriesCountByMetricName, labelValueCountByLabelName, memoryInBytesByLabelName}'
```

Response preukazuje local server head/cardinality summary. Nepreukazuje remote backend, other replicas alebo exact business owner. Output shape je version-sensitive a automation musí tolerovať absent fields.

Top values pre suspect label:

```promql
count by (payment_id) (
  payment_settlement_completed_total
)
```

Ak query vráti tisíce one-series values, je to explicitný evidence dynamic labelu. V production sa taká query najprv scope-ne na metric/job a short range, aby sama nevytvorila query incident.

## Histogram multiplication

Classic histogram s labels `provider`, `region`, `result` a 12 buckets vytvára pre každú combination 14 series: 12 buckets, sum a count. Pridanie `release` s 20 active values násobí count 20×.

Bucket design preto ovplyvňuje accuracy aj cardinality. Každý bucket má podporovať SLO alebo meaningful distribution boundary. Jemné lineárne buckets bez use case-u zvyšujú storage a query cost.

Native histograms môžu zmeniť representation a cardinality/cost model podľa Prometheus/backend supportu. Migrácia potrebuje measurement, nie automatický predpoklad úspory.

## Loki stream cardinality

Loki stream identity je complete indexed label set. Ephemeral Pod, container ID, trace ID alebo payment operation ID ako label vytvára veľa streams. Loki odporúča low-cardinality source labels a high-cardinality metadata držať ako structured metadata alebo log content. citeturn662053search0turn662053search1

Stream query:

```logql
sum by (service_name) (
  count_over_time(
    {deployment_environment="production"}[5m]
  )
)
```

Táto query počíta stored log lines, nie streams. Stream/cardinality investigation používa Loki metrics, label APIs a tooling podľa deployment version. `logcli series` môže vypísať matching series:

```bash
logcli series \
  --addr=http://loki-query-frontend:3100 \
  --org-id=atlas-production \
  --since=1h \
  '{service_name="provider-adapter"}'
```

Výstup preukazuje matching stream label sets v selected tenant/range. Nepreukazuje active ingester memory alebo historical cardinality mimo range. Pri dynamic operation labeloch môže output byť obrovský; používa sa carefully scoped.

Structured metadata umožňuje filter na high-cardinality metadata bez indexed stream explosion, ale metric LogQL query môže stále vytvoriť veľa output series, ak metadata zostanú v result labels. `keep`/`drop` stages a aggregation scope sú dôležité. citeturn662053search0

## Trace attributes a derived metrics

Trace backend môže uložiť high-cardinality span attributes, napríklad trace ID alebo operation ID, pre lookup/search podľa capabilities. Problém vznikne, keď metrics-generator alebo service graph promotion urobí z attribute dimension.

```yaml
metrics_generator:
  processor:
    span_metrics:
      dimensions:
        - payment.provider
        - payment.merchant.class
        - cloud.availability_zone
```

Bounded dimensions sú vhodné. `payment.operation.id` by vytvoril jednu metrics series na operation. Trace storage cardinality, search index cardinality a derived metrics cardinality sú odlišné budgets a musia sa merať samostatne.

## Alert instances

Prometheus alert instance identity obsahuje rule labels plus labels zachované z expression resultu. Query:

```promql
payment_queue_oldest_message_age_seconds > 60
```

môže vytvoriť alert per `queue,pod,instance`, ak metric má tieto labels. Ak intended action je jedna per queue, expression musí agregovať:

```promql
max by (queue, environment) (
  payment_queue_oldest_message_age_seconds
) > 60
```

Aggregation znižuje alert instances a alignuje identity s action scope-om. Príliš široká aggregation však môže skryť jednu Region alebo tenant cohort. Grouping sa navrhuje podľa ownership a independent remediation.

## Search-index field cardinality

Elasticsearch/OpenSearch mapping cardinality má viac osí: počet mapped fields, term cardinality pre keyword field, document count, shard count a aggregation working set. Dynamic object keys môžu vytvoriť mapping explosion:

```json
{
  "customer_attributes": {
    "custom_key_1": "a",
    "custom_key_2": "b"
  }
}
```

Každý nový key sa môže stať fieldom pri dynamic mapping. `dynamic: strict`, explicit mapping alebo flattened-style field podľa product/use case-u obmedzí mapping growth.

Mapping count:

```bash
curl -fsS \
  -H "Authorization: ApiKey $SEARCH_API_KEY" \
  "$SEARCH_URL/logs-atlas-payments-production/_mapping" \
  | jq '[.. | objects | select(has("type"))] | length'
```

JQ output je approximate traversal podľa mapping JSON, nie authoritative field-limit verdict pre all nested/multi-fields. Cluster/index stats a actual limit errors sa kontrolujú tiež.

High-cardinality keyword aggregations môžu spotrebovať memory pre global ordinals a aggregation buckets. Field je searchable bez toho, aby bol vhodný na unbounded terms dashboard.

## Churn

Bounded count v jednom okamihu môže stále vytvárať vysoký churn. Pod names pri rolling deployment-e môžu byť stovky denne, hoci concurrent Pods je 24. Prometheus stale series zostávajú v historical blocks a remote backend indexe podľa retention.

Release label s full commit SHA môže mať 1000 values za rok. Controlled `release_channel` alebo small active version set je vhodnejší pre metrics; full digest zostane v resource inventory, logs alebo traces.

Cardinality review preto sleduje active count, new series/streams per minute, churn, retention a owner.

## Schema-as-code guardrail

Metric schema manifest:

```yaml
metric: payment_settlement_completed_total
type: counter
unit: operations
labels:
  environment:
    bounded: true
    allowed: [production, staging, development]
  provider:
    bounded: true
    maxValues: 10
  result:
    bounded: true
    allowed: [success, terminal_error, timeout, duplicate, conflict]
forbidden:
  - payment_id
  - payment_operation_id
  - trace_id
  - user_id
  - raw_path
estimatedSeriesBudget: 5000
owner: payments-platform
```

CI fixture creates representative label combinations and estimates series. Static estimate nepreukazuje runtime producer behavior, preto canary scrape and backend cardinality delta sú promotion gates.

Exposition validation:

```bash
curl -fsS http://payments-api-canary:9464/metrics > /tmp/canary.metrics

promtool check metrics < /tmp/canary.metrics

grep '^payment_settlement_completed_total' /tmp/canary.metrics \
  | grep -E 'payment_id=|trace_id=|user_id=|path="/payments/[0-9]+' \
  && { echo 'forbidden dynamic label'; exit 1; } || true
```

`promtool check metrics` preukazuje exposition validity. Grep test preukazuje absence matching forbidden forms vo fixture output, nie vo všetkých runtime paths. Load test a schema instrumentation tests dopĺňajú coverage.

## Runtime guardrails

Prometheus monitoruje head series, scrape samples, remote-write queue a query latency. Loki sleduje active streams, stream-rate limits, ingester memory a index/chunk metrics. Trace pipeline sleduje active traces and derived series. Search cluster sleduje field count, shard/segment count, heap a aggregation failures.

Alert na cardinality má ownera a action. Page je opodstatnená, ak growth ohrozuje ingest alebo query availability. Pomalý trend patrí do ticket/capacity planning.

## Worked incident: jeden promoted attribute zasiahne štyri backends

Release `OTEL-PAY-12` pridá `payment.operation.id` ako OpenTelemetry attribute. Collector transform ho omylom:

```text
→ konvertuje na Prometheus metric label
→ mapuje na Loki indexed label
→ ponechá v trace-derived span metrics
→ pridá do alert expression outputu
```

Počas 20 minút Prometheus head series rastú 8×, Loki active streams 20×, span-metrics backend throttluje a Alertmanager prijíma tisíce alert instances. Traffic vzrástol iba 5 %.

Competing hypotheses sú real demand spike, scrape duplication, service discovery loop, collector replay alebo dimension promotion. Config diff a top label-value analysis ukážu operation ID naprieč signals.

Containment zastaví rollout a odstráni promotion v nových Collector records. Existing Prometheus series a Loki streams nezmiznú okamžite; zostanú do staleness/retention. Query/alert limits chránia platformu a business SLO monitor používa independent bounded metrics.

Recovery ponechá operation ID v trace/log structured metadata, odstráni ho z metric labels a alert identity, versionuje schema a nasadí canary. Recording rules agregujú bounded dimensions. Search mapping používa keyword field bez dashboard terms aggregation.

Acceptance vyžaduje stabilný new-series/stream rate, head/ingester memory recovery, successful signal canary, bounded alert instances a preserved trace/log lookup by operation ID. Forbidden schema fixture s dynamic ID musí CI a runtime admission gate odmietnuť.

## Kontrolné otázky

1. Čo presne cardinality počíta v Prometheus a Loki?
2. Prečo theoretical label combination product nie je rovný actual active series?
3. Ako classic histogram násobí series?
4. Prečo Pod name môže byť bounded concurrentne a high-churn historicky?
5. Kedy high-cardinality trace attribute začne škodiť metrics pipeline?
6. Ako alert aggregation súvisí s action scope-om?
7. Prečo mapping field count a keyword term cardinality sú odlišné problémy?
8. Čo schema-as-code static estimate nepreukazuje?
9. Ako operation ID zasiahol štyri telemetry backends?
10. Aké evidence uzatvára cardinality recovery?

## Oficiálna dokumentácia

- [Prometheus metric and label naming](https://prometheus.io/docs/practices/naming/)
- [Prometheus instrumentation practices](https://prometheus.io/docs/practices/instrumentation/)
- [Loki labels](https://grafana.com/docs/loki/latest/get-started/labels/)
- [Loki structured metadata](https://grafana.com/docs/loki/latest/get-started/labels/structured-metadata/)
- [OpenTelemetry attributes](https://opentelemetry.io/docs/specs/otel/common/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Alert design a alert fatigue](alert-design-alert-fatigue.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CI/CD, delivery a governance →](../13-cicd-delivery-governance/README.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
