# Prometheus

Prometheus je metrics monitoring a alerting systém založený na multidimenzionálnych time series, pravidelnom scrapingu a PromQL. Jeho operational contract nie je „target je green“. Prometheus vytvára reťaz od expected targetu cez service discovery, relabeling, HTTP scrape, exposition parsing, sample limits, local TSDB, query a rule evaluation až po alert delivery. Každá boundary môže zmeniť alebo stratiť evidence.

Prometheus nie je log store, trace backend ani automaticky globálny long-term metrics cluster. Lokálny model je zámerne transparentný: server pulluje targets, ukladá samples do lokálnej TSDB a vyhodnocuje rules nad svojím queryable state-om.

## End-to-end lifecycle

Prometheus verdict vzniká až po sérii odlišných control a data-path rozhodnutí. Discovery určí kandidáta, relabeling z neho vytvorí effective target, scrape prečíta exposition a TSDB až následne sprístupní samples query a rules. Úspech jednej boundary preto nesmie byť použitý ako dôkaz úplnosti nasledujúcej; lifecycle sa číta v tomto poradí.

```text
measurement intent
→ versionovaný metric a label contract
→ expected target inventory
→ discovery a target relabeling
→ HTTP scrape
→ exposition parsing a sample validation
→ metric relabeling a limits
→ WAL, head block a TSDB persistence
→ staleness a query semantics
→ recording alebo alerting rule
→ external notification alebo remote write
→ business a telemetry validation
```

`up=1` znamená, že konkrétny scrape target odpovedal a response sa dala spracovať. Neznamená, že target exportuje všetky očakávané metrics, že labels majú správnu schema alebo že remote backend dáta prijal.

## Exact Prometheus subject

Atlas používa:

```yaml
prometheus: prometheus-platform-0
configurationGeneration: PROM-CFG-41
ruleGeneration: PROM-RULES-33
serviceMonitorGeneration: SM-PAY-19
job: kubernetes-pods/payments-api
expectedTargets: 24
metricSchema: atlas-payments-12
remoteWrite: mimir-prod-eu-v7
businessOperation: payment.settle
```

Incident evidence musí viazať target labels, discovered labels, post-relabel labels, scrape timestamp, sample set, server identity, TSDB/query state a rule generation. Screenshot target page-u bez config a query identity nie je reprodukovateľný dôkaz.

## Scrape configuration

Minimálny static example:

```yaml
global:
  scrape_interval: 30s
  evaluation_interval: 30s

rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  - job_name: payments-api
    metrics_path: /metrics
    scheme: http
    static_configs:
      - targets:
          - payments-api-a:9464
          - payments-api-b:9464
        labels:
          environment: production
          service: payments-api
```

Configuration preukazuje desired scrape interval, targets a labels. Nepreukazuje, že exact file je loaded alebo DNS/network path funguje. Syntax a loaded state sa overujú samostatne:

```bash
promtool check config /etc/prometheus/prometheus.yml

curl -fsS http://prometheus:9090/-/ready

curl -fsS http://prometheus:9090/api/v1/status/config \
  | jq -r '.data.yaml'
```

`promtool check config` preukazuje parse a static validation. Readiness endpoint preukazuje server readiness podľa Prometheus contractu, nie target completeness. Status API ukáže loaded configuration, ale runtime targets sa čítajú cez targets API.

## Discovery a relabeling

V Kubernetes discovery vzniká veľa candidate targets. Target relabeling rozhoduje, čo sa skutočne scrape-uje a aké target labels vzniknú pred scrape-om.

```yaml
scrape_configs:
  - job_name: kubernetes-pods/payments-api
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names: [payments]
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: payments-api
        action: keep
      - source_labels: [__meta_kubernetes_pod_container_port_name]
        regex: metrics
        action: keep
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
      - source_labels: [__meta_kubernetes_pod_node_name]
        target_label: node
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        regex: (.+)
        target_label: __metrics_path__
```

Relabeling je executable selection program. Wrong `keep` regex môže odstrániť všetky targets bez zlyhania Prometheus procesu. Broad rule môže scrape-ovať sidecars alebo admin endpoints a vytvoriť cardinality/cost incident.

Targets API:

```bash
curl -fsS 'http://prometheus:9090/api/v1/targets?state=active' \
  | jq '.data.activeTargets[] | {scrapeUrl, health, labels, discoveredLabels, lastError}'
```

Výstup preukazuje active targets viditeľné danému serveru, post-relabel labels a last scrape state. Nepreukazuje expected inventory; ten sa porovnáva s Kubernetes/ECS authoritative countom.

## Exposition a sample contract

Producer endpoint možno čítať priamo:

```bash
curl -fsS http://payments-api:9464/metrics \
  | grep -E '^(payment_settlement_started_total|payment_settlement_completed_total|payment_settlement_duration_seconds_bucket)'
```

Príkaz preukazuje, že konkrétny endpoint v danom okamihu vystavil matching text. Nepreukazuje, že Prometheus endpoint scrape-ol, že metric relabeling samples zachovalo alebo že labels sú bounded.

Metric name, type, unit a label semantics sú API contract. Counter sa nesmie resetovať logicky pri každom requeste, histogram buckets musia podporovať SLO a label values nesmú niesť dynamic payment IDs.

Metric relabeling sa vykonáva po scrape a môže zahodiť samples:

```yaml
metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'go_.+|process_.+'
    action: drop
  - source_labels: [payment_id]
    action: labeldrop
```

Drop môže znížiť cost, ale odstrániť metric potrebnú pre runtime diagnosis. `labeldrop` pri high-cardinality field-e zlučuje samples, ktoré sa líšili iba týmto labelom; ak vzniknú duplicate label sets v jednom scrape, sample conflict môže viesť k failure. Najbezpečnejšie je forbidden label nevytvoriť u producer-a.

## TSDB, WAL a staleness

Prometheus najprv zapisuje samples do WAL a in-memory head, neskôr ich compactuje do blocks. Local retention sa riadi time/size flags. Storage full, corrupt WAL alebo dlhý compaction pressure môžu ovplyvniť ingest a query.

Query result absent po target disappearance používa staleness semantics. Prometheus pridá stale marker, aby instant queries prestali považovať poslednú hodnotu za current. Range functions majú vlastné semantics a dashboard transformation môže last value držať dlhšie.

Server status:

```bash
curl -fsS http://prometheus:9090/api/v1/status/tsdb \
  | jq '.data | {headStats, seriesCountByMetricName, labelValueCountByLabelName}'

curl -fsS http://prometheus:9090/api/v1/status/runtimeinfo \
  | jq '.data'
```

TSDB status preukazuje local head/cardinality summary daného servera. Nepreukazuje remote-write state ani query load z iných replicas. Runtime info poskytuje storage path a retention/config context, nie filesystem health samotný.

## PromQL a evidence boundaries

Instant query:

```bash
curl -fsS -G 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=sum by (availability_zone) (rate(payment_settlement_completed_total{result="terminal_error"}[5m]))' \
  | jq '.data.result'
```

Range query pridáva start/end/step. Query output platí pre konkrétny server, evaluation timestamp a label population. Empty vector nie je nula. Môže znamenať absent series, label mismatch, staleness alebo wrong tenant/server.

Pri counters používaj `rate()` pred aggregation, aby resets boli identifikované per-series. Pri histograms agreguj buckets podľa `le`. Average of averages bez counts je neplatný. PromQL query musí mať documented units a population.

## Recording a alerting rules

Recording rule pre často používaný logical rate:

```yaml
groups:
  - name: atlas-payments-red
    interval: 30s
    limit: 5000
    rules:
      - record: service:payment_settlement_started:rate5m
        expr: sum(rate(payment_settlement_started_total[5m]))
      - record: service:payment_settlement_error_ratio:rate5m
        expr: |
          sum(rate(payment_settlement_completed_total{result!="success"}[5m]))
          /
          sum(rate(payment_settlement_started_total[5m]))
```

Rule group sa vyhodnocuje sekvenčne v intervale. Ak evaluation trvá dlhšie než interval, ďalšie iterations môžu byť skipped a vznikne gap. Per-group `limit` môže chrániť pred explosion, ale prekročenie spôsobí evaluation error a výsledky sa discard-nú.

Alerting rule:

```yaml
      - alert: PaymentSettlementFastBurn
        expr: service:payment_settlement_error_ratio:rate5m > 0.0144
        for: 2m
        keep_firing_for: 5m
        labels:
          severity: page
          service: atlas-payments
        annotations:
          summary: Settlement error budget burns rapidly
          runbook_url: https://runbooks.example/payments/settlement-fast-burn
```

`for` vyžaduje, aby condition ostala active pred firing. `keep_firing_for` môže zachovať firing určitý čas po clear podľa current Prometheus behavior. Rule syntax sa overuje:

```bash
promtool check rules /etc/prometheus/rules/payments.yml

promtool test rules /etc/prometheus/tests/payments.test.yml
```

Syntax check nepreukazuje business semantics. Unit test overí expression nad synthetic series, no production scrape lag, missing data a labels sa testujú shadow rule a canary.

Loaded rules a evaluation health:

```bash
curl -fsS http://prometheus:9090/api/v1/rules \
  | jq '.data.groups[] | {name, evaluationTime, lastEvaluation, rules}'
```

Výstup preukazuje rules loaded v danom serveri a current state. Nepreukazuje, že Alertmanager notification dorazila.

## Remote write a federation

Remote write odosiela samples asynchrónne z WAL queue do external backendu. Local query môže byť healthy a remote backend zaostávať alebo odmietať samples. Monitoruj queue length, shards, retries, failed/dropped samples a highest sent timestamp.

```promql
max(
  prometheus_remote_storage_highest_timestamp_in_seconds
)
-
time()
```

Expression treba orientovať správne; prakticky sa často používa `time() - highest_timestamp` na lag v sekundách:

```promql
time() - max(prometheus_remote_storage_highest_timestamp_in_seconds)
```

Výsledok preukazuje timestamp lag posledného successful remote sample podľa local exporter metric. Nepreukazuje queryability v remote backendu; end-to-end canary sa musí query-nuť na remote strane.

Federation a HA replicas pridávajú deduplication a external labels. Rovnaká series identity z dvoch replicas bez správnych external labels môže kolidovať. Recording rule authority musí byť jasná, aby lokálny a global rule nevytvárali duplicate alerts.

## Worked incident: `up=1`, business metric chýba

Po release `OTEL-PAY-12` má všetkých 24 targets `up=1`, no enterprise completion dashboard ukazuje no data iba v `eu-central-1b`. Competing hypotheses sú producer schema change, target relabel mismatch, metric relabel drop, scrape sample limit, remote-write lag alebo Grafana variable mismatch.

Direct producer curl ukáže `payment_settlement_completed_total` s novým labelom `provider_config_generation`. Targets API potvrdí successful scrape. Local Prometheus query však vráti series iba z `1a`. Scrape target detail ukáže last error `sample limit exceeded` pre `1b`: release pridala dynamic `payment_id` label na ďalšie metrics a prekročila sample limit. `up` ostal 0 alebo scrape failed podľa exact scrape outcome; ak dashboard agregoval iba healthy targets, absence bola skrytá.

Containment odstráni affected targets z business alert authority a použije independent business ledger monitor. Recovery odstráni forbidden label u producer-a, nasadí canary, overí sample count/cardinality, successful scrape, local query, remote query a rules. Plošné zvýšenie sample limitu je zakázané, kým schema root cause nie je odstránená.

Acceptance vyžaduje 24/24 expected targets, metric completeness, bounded active series, local a remote canary, rule evaluation bez gaps a forbidden test s dynamic labelom, ktorý deployment gate odmietne.

## Kontrolné otázky

1. Prečo `up=1` nepreukazuje metric completeness?
2. Čo target relabeling mení pred scrape-om?
3. Čo producer curl preukazuje a čo nie o Prometheus ingest-e?
4. Aký rozdiel je medzi metric relabeling a target relabeling?
5. Prečo empty PromQL vector nie je nula?
6. Ako staleness ovplyvňuje instant query?
7. Čo `promtool check rules` nepreukazuje?
8. Prečo rule group môže vynechať evaluation?
9. Ako sa local query líši od remote-write queryability?
10. Ktoré evidence uzatvára sample-limit incident?

## Oficiálna dokumentácia

- [Prometheus configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
- [Prometheus querying](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Recording and alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/)
- [Rule unit testing](https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/)
- [Remote write tuning](https://prometheus.io/docs/practices/remote_write/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Golden Signals](golden-signals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Alertmanager →](alertmanager.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
