# Loki

Grafana Loki je log aggregation systém založený na log streamoch identifikovaných tenant ID a label setom. Na rozdiel od full-text index systems Loki primárne indexuje stream metadata; log content komprimuje do chunks a ukladá do object storage alebo iného configured chunk store-u. Tento model môže znížiť index cost, ale robí z label contractu, timestamps, schema periods, object-store lifecycle a query scope-u zásadné correctness boundaries. citeturn662053search15turn662053search19turn662053search21

Loki nemôže nájsť log, ktorý producer nevytvoril, collector neprečítal, distributor odmietol, ingester neuložil, object-store lifecycle predčasne zmazal alebo query hľadala v nesprávnom tenantovi či streamoch. Process health preto nie je log-delivery verdict.

## End-to-end lifecycle

```text
system alebo business occurrence
→ producer log record a timestamp
→ collector read, parse a metadata
→ tenant a bounded stream labels
→ distributor validation a routing
→ ingester stream/chunk state
→ WAL alebo replication a object-store flush
→ TSDB index publication
→ recent alebo historical query path
→ LogQL parse/filter/aggregation
→ evidence a operational decision
→ retention a cardinality closure
```

Každý stream musí mať aspoň jeden label. Rovnaký complete label set vytvára jeden stream. Zmena jedinej label value vytvorí ďalší stream, preto ephemeral Pod name, request ID alebo payment ID ako indexed labels zvyšujú active cardinality a churn. Loki odporúča low-cardinality labels a high-cardinality metadata ukladať ako structured metadata alebo log fields podľa ingestion modelu. citeturn662053search0turn662053search1

## Exact Loki subject

Atlas používa log subject `LOKI-PAY-43`:

```yaml
tenant: atlas-production
schemaGeneration: LOKI-SCHEMA-13
indexType: tsdb
objectStore: s3://atlas-observability-loki
streamLabels:
  service_name: provider-adapter
  deployment_environment: production
  cloud_region: eu-central-1
  service_namespace: payments
structuredMetadata:
  pod_name: payments-api-7f8d9c6b7b-abcde
  trace_id: 4bf92f3577b34da6a3ce929d0e0e4736
  payment_operation_id: op-884
logSchema: atlas-payments-log-12
retention: 30d
```

`service_name`, environment a Region sú bounded source identity. Pod name a trace ID sú užitočné pri investigation, ale ako indexed labels by vytvárali vysoký počet streams. Structured metadata je v current Loki modeli dostupná pri compatible schema/chunk format; jej použitie a limits treba overiť pre active schema. citeturn662053search0turn662053search13

## Schema a storage

TSDB schema config:

```yaml
schema_config:
  configs:
    - from: 2026-01-01
      store: tsdb
      object_store: s3
      schema: v13
      index:
        prefix: loki_index_
        period: 24h

storage_config:
  aws:
    s3: s3://eu-central-1/atlas-observability-loki
  tsdb_shipper:
    active_index_directory: /var/loki/index
    cache_location: /var/loki/index_cache
```

Configuration preukazuje desired schema period, index type a object-store path. Nepreukazuje, že exact config je loaded, bucket policy/KMS fungujú alebo retention component maže dáta podľa intended window. Schema periods sú časové authority boundaries; nesprávne `from` date môže poslať nové logs do nekompatibilného pathu.

Loki storage obsahuje chunks a index. Index spája label sets s chunks; content samotný nie je plne indexovaný. Query najprv vyberie streams cez selector a potom spracuje log lines v relevantných chunks. citeturn662053search19turn662053search27

## Labels, fields a structured metadata

Collector môže poslať record:

```json
{
  "timestamp": "2026-07-29T09:18:42.114Z",
  "level": "error",
  "service": "provider-adapter",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "payment_operation_id": "op-884",
  "availability_zone": "eu-central-1b",
  "config_generation": "PROVIDER-CFG-34",
  "error_type": "tls.unknown_ca",
  "message": "provider TLS handshake failed"
}
```

Indexed stream labels zostanú bounded. `trace_id`, Pod a operation ID sa uložia ako structured metadata alebo v JSON body. Log level a exception type možno parsovať pri query; nemusia automaticky vytvoriť samostatné streams. Loki labels určujú stream organization, nie každé searchable field. citeturn662053search1turn662053search12

Forbidden label example:

```yaml
labels:
  payment_operation_id: op-884
  trace_id: 4bf92f3577b34da6a3ce929d0e0e4736
```

Každá operation by vytvorila unikátny stream. To zvyšuje index, ingester stream state a query cost. Deployment gate má kontrolovať forbidden label keys ešte pred produkciou.

## LogQL stream selection a parsing

Všetky LogQL log queries začínajú stream selectorom. citeturn662053search12turn662053search29

```logql
{service_name="provider-adapter", deployment_environment="production"}
| json
| error_type="tls.unknown_ca"
| availability_zone="eu-central-1b"
| line_format "{{.trace_id}} {{.config_generation}} {{.payment_operation_id}}"
```

Query preukazuje uložené log entries v selected tenant/time range, ktoré parser úspešne interpretoval a filter matchol. Nepreukazuje completeness producer population. Malformed JSON môže vytvoriť parser error a byť z resultu odfiltrovaný.

Parser errors sa kontrolujú explicitne:

```logql
{service_name="provider-adapter"}
| json
| __error__!=""
```

Prázdny výsledok môže znamenať nulové parser errors alebo chýbajúce streams. Najprv sa overí broad stream selector a volume.

Rate z logs:

```logql
sum by (availability_zone) (
  rate(
    {service_name="provider-adapter", deployment_environment="production"}
    | json
    | error_type="tls.unknown_ca"
    [5m]
  )
)
```

Výsledok preukazuje rate matching stored log lines. Ak producer retryuje a loguje každý attempt, nejde o unikátne business operations.

## `logcli` a HTTP API

```bash
logcli query \
  --addr=http://loki-query-frontend:3100 \
  --org-id=atlas-production \
  --from='2026-07-29T09:10:00Z' \
  --to='2026-07-29T09:35:00Z' \
  --limit=200 \
  '{service_name="provider-adapter",deployment_environment="production"} | json | error_type="tls.unknown_ca"'
```

Príkaz preukazuje query result pre exact tenant, endpoint a absolute range. Nepreukazuje, že Grafana používa rovnaký tenant header, query frontend alebo variables. Incident transcript zachováva command, range, tenant a response statistics.

Raw HTTP query:

```bash
curl -fsS -G 'http://loki-query-frontend:3100/loki/api/v1/query_range' \
  -H 'X-Scope-OrgID: atlas-production' \
  --data-urlencode 'query={service_name="provider-adapter"} | json | error_type="tls.unknown_ca"' \
  --data-urlencode 'start=1753780200000000000' \
  --data-urlencode 'end=1753781700000000000' \
  --data-urlencode 'limit=100' \
  | jq '.data.result'
```

Nanosecond timestamps a tenant identity sú súčasťou request subjectu. Wrong tenant môže vrátiť empty result bez syntax erroru.

## Ingestion limits a timestamps

Distributor môže odmietnuť streams alebo lines pre rate, line size, label count, out-of-order window, old/future timestamp alebo per-tenant limits. HTTP success/failure sa interpretuje podľa push API a collector output contractu.

Loki current upgrade guidance uvádza default max line size a label-count boundaries, ale exact limits sú configurable a version-sensitive; operational chapter sa viaže na live `/config` alebo deployed values, nie na zapamätané defaults. citeturn662053search13

Collector timestamp musí reprezentovať event time podľa schema. Ak parser zlyhá a agent použije ingestion time, incident timeline sa posunie. Future timestamps môžu skryť logs mimo current dashboard range.

## Recent a historical query path

Recent logs môžu byť stále v ingester memory/chunks, zatiaľ čo historical logs sú v object store a index. Query frontend/scheduler rozdeľuje requesty a querier číta relevantné stores podľa topology. Stav `ingester healthy` nepreukazuje object-store historical path; successful historical query nepreukazuje recent ingestion.

Canary test používa unique low-risk token:

```bash
CANARY_ID="loki-canary-$(date -u +%s)"
printf '{"level":"info","event":"telemetry.canary","canary_id":"%s"}\n' "$CANARY_ID" \
  | logger -t atlas-observability-canary

logcli query \
  --addr=http://loki-query-frontend:3100 \
  --org-id=atlas-production \
  --since=10m \
  "{service_name=\"observability-canary\"} |= \"$CANARY_ID\""
```

Prvý command preukazuje local emission do configured system logger path, nie Fluent Bit read. Query success preukazuje end-to-end recent path. Rovnaký canary sa po flush/compaction windowe query-ne ako historical test.

## Retention a deletion

Retention je koordinácia Loki compactor/configuration a object-store lifecycle. Object-store policy kratšia než Loki retention môže zmazať chunks, zatiaľ čo index ešte odkazuje na ne. Dlhšia policy môže držať orphan data a cost.

Retention change sa testuje na canary tenant/stream, kontroluje effective limits, compactor state, marker/deletion delay a object lifecycle. `No data` po očakávanom retention windowe nie je dôkaz správneho governed deletion bez object-store a audit evidence.

## Worked incident: dynamic payment ID vytvorí stream explosion

Po release `OTEL-PAY-12` začne collector mapovať `payment_operation_id` na Loki label. Log volume rastie iba 15 %, ale active streams, ingester memory a index operations prudko stúpnu. Query latency rastie a časť pushes dostáva rate/stream-limit errors. Grafana panel pre enterprise logs zobrazuje intermittent no data.

Competing hypotheses sú object-store outage, distributor rate limit, query frontend overload, malformed records, wrong tenant alebo label cardinality explosion.

Loki metrics a stream analysis ukážu milióny krátko žijúcich streams s labelom `payment_operation_id`. Broad selector bez dynamic labelu potrebuje prehľadať množstvo tiny chunks. Collector config diff potvrdí nový label mapping.

Containment zastaví rollout a odstráni dynamic label z nových records. Existing streams sa nedajú „zlúčiť“ spätnou config zmenou; historical data zostane podľa pôvodnej identity do retention. Query guardrails a tenant limits chránia cluster, ale plošné zvýšenie limitov je zakázané.

Recovery presunie operation ID a trace ID do structured metadata, zachová bounded labels a nasadí canary. Acceptance vyžaduje stabilný active-stream count, successful pushes, recent aj historical query, correct trace lookup a forbidden schema test, ktorý odmietne high-cardinality label. Retention closure sleduje retirement starej stream identity.

## Kontrolné otázky

1. Čo Loki indexuje a čo ukladá v chunks?
2. Prečo complete label set vytvára stream identity?
3. Ktoré fields patria do structured metadata namiesto labels?
4. Čo LogQL query preukazuje a čo nie o producer completeness?
5. Prečo treba kontrolovať `__error__` po parseri?
6. Aký rozdiel je medzi recent a historical query pathom?
7. Čo end-to-end canary preukazuje navyše oproti process healthu?
8. Ako object-store lifecycle môže porušiť retention?
9. Prečo dynamic payment ID vytvoril stream explosion?
10. Čo musí overiť forbidden label schema test?

## Oficiálna dokumentácia

- [Loki overview](https://grafana.com/docs/loki/latest/get-started/overview/)
- [Loki labels](https://grafana.com/docs/loki/latest/get-started/labels/)
- [Structured metadata](https://grafana.com/docs/loki/latest/get-started/labels/structured-metadata/)
- [LogQL](https://grafana.com/docs/loki/latest/query/)
- [Loki storage](https://grafana.com/docs/loki/latest/operations/storage/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Grafana](grafana.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Elasticsearch alebo OpenSearch →](elasticsearch-opensearch.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
