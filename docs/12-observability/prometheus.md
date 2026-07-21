# Prometheus

Prometheus je metrics monitoring a alerting systém založený na multidimenzionálnych time series, pull-based scrapingu a jazyku PromQL. Jeho hlavnou silou je lokálne a transparentné vyhodnocovanie numerickej telemetry podľa labels. Nie je to univerzálny log store, distributed trace backend, durable event bus ani automaticky neobmedzený long-term metrics warehouse.

## 1. Mentálny model

```text
instrumented application alebo exporter
→ service discovery
→ target relabeling
→ HTTP scrape
→ sample validation a metric relabeling
→ local TSDB/WAL
→ PromQL
→ recording a alerting rules
→ Alertmanager alebo query consumers
→ voliteľný remote write / federation
```

Prometheus pravidelne zisťuje targets, scrape-ne ich metrics endpointy a ukladá prijaté samples ako time series. Alerting rules vznikajú nad uloženými alebo aktuálne queryovateľnými series; notification routing patrí Alertmanageru.

## 2. Architektúra

Typický deployment obsahuje:

- Prometheus server,
- instrumented applications,
- exporters pre systémy bez native metrics endpointu,
- service-discovery integrácie,
- Pushgateway iba pre špecifické short-lived batch use cases,
- Alertmanager,
- Grafana alebo iný query client,
- voliteľný remote-storage alebo global-query layer.

Prometheus server zahŕňa:

- retrieval engine,
- service discovery,
- relabeling pipeline,
- local TSDB,
- PromQL query engine,
- rule evaluator,
- HTTP API a UI,
- remote-write queue pri konfigurácii.

## 3. Pull model

Prometheus štandardne sťahuje metrics z targets cez HTTP.

Výhody:

- centrálne riadený scrape interval a timeout,
- jednoznačný zoznam expected targets,
- jednoduchá detekcia nedostupného endpointu cez `up`,
- service discovery a target metadata,
- target nemusí poznať monitoring backend,
- lokálna diagnostika cez `/targets`.

Pull neznamená, že každá telemetry musí byť pull-based. Logs, traces a udalosti prirodzene často používajú push/export model.

### Čo signal `up` znamená

Prometheus generuje pre scrape target time series:

```promql
up{job="api"}
```

- `1` znamená, že scrape prebehol úspešne,
- `0` znamená, že scrape zlyhal.

`up == 1` nepreukazuje správnosť business služby. Preukazuje iba úspešný metrics scrape podľa konfigurácie.

## 4. Exporters

Exporter prekladá stav externého systému do Prometheus exposition formátu.

Príklady:

- Node Exporter,
- database exporter,
- blackbox exporter,
- SNMP exporter,
- cloud-service exporter.

Exporter vytvára ďalšiu prevádzkovú vrstvu. Treba monitorovať:

- jeho vlastnú dostupnosť,
- scrape duration,
- počet a veľkosť series,
- timeouty voči zdroju,
- credential a permission failures,
- stale alebo partial data,
- kompatibilitu so zdrojovým systémom.

Exporter success nemusí znamenať, že úspešne získal všetky source metrics.

## 5. Pushgateway

Pushgateway je určený najmä pre service-level metrics short-lived batch jobov, ktoré zaniknú skôr, než ich Prometheus stihne scrape-nuť.

Nie je všeobecná náhrada pull modelu.

Riziká:

- series zostávajú uložené aj po skončení jobu, kým sa explicitne neodstránia,
- target health semantics sa presúvajú na Pushgateway,
- machine alebo instance metrics strácajú prirodzený lifecycle,
- grouping key môže vytvoriť cardinality alebo stale data.

Pre batch job monitoruj aj:

- timestamp posledného úspechu,
- duration,
- business output,
- schedule freshness,
- explicitný cleanup series.

## 6. Time-series data model

Prometheus ukladá všetky dáta ako time series.

Jedna series je určená:

```text
metric name
+ úplná množina label names a values
```

Príklad:

```text
http_requests_total{
  service="orders",
  method="GET",
  route="/orders/{id}",
  status_code="200"
}
```

Každá odlišná kombinácia labels vytvára samostatnú series.

### Cardinality

Ak pridáš label `user_id` s miliónom hodnôt, môže vzniknúť milión alebo viac series.

Cardinality cost ovplyvňuje:

- ingestion,
- active head memory,
- WAL,
- disk blocks,
- query fan-out,
- remote-write traffic,
- rule evaluation,
- dashboard latency.

Labels majú reprezentovať bounded dimensions vhodné na agregáciu, nie unikátnu identitu udalosti.

## 7. Metric naming

Dobrý metric contract obsahuje:

- stabilný názov,
- jednu presnú vec,
- správnu base unit,
- suffix podľa semantics,
- bounded labels,
- jasnú help text definíciu,
- konzistentnosť medzi services.

Bežné suffixy:

- `_total` pre counters,
- `_seconds` pre duration,
- `_bytes` pre veľkosť,
- `_info` pre statické informačné labels,
- `_created` podľa client-library správania.

Nepoužívaj label na odlíšenie konceptov, ktoré majú odlišné units alebo meanings.

## 8. Metric types

### Counter

Monotónne rastie a resetne sa pri reštarte.

Query:

```promql
rate(http_requests_total[5m])
```

Nepočítaj counter ako gauge a nealertuj na jeho absolútnu hodnotu bez lifecycle kontextu.

### Gauge

Môže rásť aj klesať.

Príklady:

- queue depth,
- active connections,
- temperature,
- current replicas.

### Histogram

Klasický histogram exportuje:

- cumulative bucket counters `_bucket{le="..."}`,
- `_count`,
- `_sum`.

Umožňuje server-side agregáciu a výpočet quantiles cez `histogram_quantile()` pri správnej query.

### Native histogram

Native histograms používajú kompaktnejšiu histogram sample reprezentáciu s dynamickejším rozlíšením a lepšou atomicitou pri prenose než skupina samostatných classic-histogram series.

Pred použitím over:

- verziu Prometheus a client library,
- feature a storage compatibility,
- remote-write/backend podporu,
- query a dashboard kompatibilitu,
- migration contract.

### Summary

Summary môže počítať client-side quantiles a exportuje count/sum.

Client-side quantiles typicky nemožno bezpečne agregovať naprieč instances. Pre service-wide latency býva histogram vhodnejší.

## 9. Exposition a scrape lifecycle

Scrape obsahuje:

1. target selection,
2. HTTP request,
3. exposition parsing,
4. sample a label validation,
5. target labels,
6. metric relabeling,
7. ingestion do TSDB.

Scrape môže zlyhať pre:

- DNS alebo route,
- TLS/authentication,
- timeout,
- neplatný exposition formát,
- duplicate labels alebo samples,
- label/sample limits,
- response príliš veľkú,
- target process failure.

Sleduj:

```promql
up
scrape_duration_seconds
scrape_samples_scraped
scrape_samples_post_metric_relabeling
scrape_series_added
```

## 10. Scrape configuration

Prometheus configuration používa `scrape_configs`.

Príklad:

```yaml
global:
  scrape_interval: 30s
  scrape_timeout: 10s
  evaluation_interval: 30s

scrape_configs:
  - job_name: orders-api
    metrics_path: /metrics
    scheme: https
    static_configs:
      - targets:
          - orders-1.example.internal:9443
          - orders-2.example.internal:9443
```

Scrape timeout nemôže byť väčší než scrape interval.

Kratší interval:

- zachytí kratšie udalosti,
- znižuje detection latency,
- zvyšuje requests, samples, storage a query cost.

Interval vyber podľa signal dynamics a operational potreby, nie univerzálne pre všetky jobs.

## 11. Service discovery

Service discovery vytvára dynamický zoznam target groups a dočasné metadata labels.

Prometheus podporuje viacero discovery mechanizmov vrátane cloudových platforiem, Kubernetes, Consul, DNS a file-based discovery.

Discovery odpovedá na otázku:

```text
ktoré endpoints potenciálne existujú?
```

Relabeling následne rozhoduje:

```text
ktoré z nich scrape-nuť a aké target labels priradiť?
```

## 12. Target relabeling

`relabel_configs` sa vykonáva pred scrape-nutím.

Použitie:

- keep/drop targetov,
- výber address, scheme alebo metrics path,
- mapovanie discovery metadata na stabilné labels,
- normalizácia environment/service/namespace,
- hash-based sharding,
- odstránenie dočasných labels.

Interné labels začínajú `__`, napríklad:

- `__address__`,
- `__scheme__`,
- `__metrics_path__`,
- service-discovery `__meta_*` labels.

Po target relabelingu sa väčšina interných labels odstráni.

### Anti-pattern

Bezhlavé `labelmap` všetkých Kubernetes annotations alebo labels môže preniesť nestabilné a vysokokardinalitné metadata do každej series.

## 13. Metric relabeling

`metric_relabel_configs` sa aplikuje po scrape-nutí a pred ingestion.

Použitie:

- drop nepotrebných metrics,
- odstránenie rizikových labels,
- normalizácia label values,
- obmedzenie ingestion costu.

Metric relabeling už nezníži network a parse cost scrape response. Zníži však stored/remote-written series.

Nedropuj kritické series bez evidencie o dashboardoch, rules a SLO dependencies.

## 14. External labels

External labels identifikujú Prometheus repliku alebo environment v externých systémoch.

Príklady:

- cluster,
- region,
- prometheus replica,
- tenant.

Sú relevantné pre:

- remote storage,
- federation,
- HA deduplication v global-query vrstve.

External labels nevyriešia automaticky conflicts medzi application labels a monitoring topology.

## 15. Local TSDB

Prometheus local storage používa:

- in-memory head block,
- Write-Ahead Log — WAL,
- pravidelne vytvárané immutable blocks,
- index a chunk files,
- compaction,
- retention podľa time alebo size konfigurácie.

### WAL

WAL chráni nedávne samples pred stratou pri reštarte a podporuje recovery head state-u.

Riziká:

- pomalý alebo poškodený disk,
- príliš veľký replay čas,
- nedostatok disk space,
- filesystem corruption,
- vysoká churn/cardinality.

### Retention

Local retention nie je backup ani DR plán.

Prometheus local TSDB je navrhnutá primárne ako lokálny operational store. Pri požiadavkách na dlhú retention, global query alebo multi-cluster durability sa zvažuje remote storage alebo kompatibilná metrics platforma.

## 16. Staleness

Keď target prestane exportovať series alebo zmizne, Prometheus musí zabrániť tomu, aby stará hodnota vyzerala ako aktuálna.

Staleness semantics ovplyvňujú:

- instant-vector queries,
- target disappearance,
- scrape failures,
- label-set changes,
- recording a alerting rules.

Pri „missing metric“ incidente rozlišuj:

- target down,
- series už nie je exportovaná,
- label set sa zmenil,
- query selector už nesedí,
- series je stale,
- rule alebo dashboard filtruje výsledok.

## 17. PromQL data types

PromQL pracuje najmä s:

- instant vectors,
- range vectors,
- scalars,
- strings v obmedzenom kontexte.

### Instant vector

Series s jednou sample hodnotou v evaluation čase.

```promql
up{job="orders-api"}
```

### Range vector

Series s množinou samples za časové okno.

```promql
http_requests_total[5m]
```

Range vector sa typicky používa ako vstup funkcie ako `rate()`.

## 18. Selectors a matchers

```promql
http_requests_total{
  service="orders",
  status_code=~"5.."
}
```

Matcher types:

- `=` equality,
- `!=` inequality,
- `=~` regex,
- `!~` negative regex.

Broad selector môže načítať veľké množstvo series. Query najprv over v tabular pohľade a sleduj výslednú cardinality.

## 19. Rate a increase

Pre counter používaj:

```promql
rate(metric_total[5m])
increase(metric_total[1h])
```

`rate()` zohľadňuje counter resets.

Window musí obsahovať dostatok samples. Pri scrape intervale 60 sekúnd je príliš krátke range window nestabilné alebo prázdne.

Pravidlo:

```text
rate window > niekoľkonásobok scrape intervalu
```

## 20. Aggregation

Príklad service error ratio:

```promql
sum by (service) (
  rate(http_requests_total{status_code=~"5.."}[5m])
)
/
sum by (service) (
  rate(http_requests_total[5m])
)
```

Pri aggregation explicitne určuj labels, ktoré majú zostať.

Chyby:

- numerator a denominator majú odlišný scope,
- zabudnutý `by` alebo `without`,
- mix rôznych units,
- duplicate series z HA replicas,
- division by zero alebo missing denominator.

## 21. Vector matching

Binary operations medzi vectors potrebujú zhodu label sets.

Mechanizmy:

- default one-to-one matching,
- `on(...)`,
- `ignoring(...)`,
- `group_left`,
- `group_right`.

Many-to-many ambiguity je často signál nesprávneho data modelu alebo nedostatočnej agregácie.

Pred joinom si zobraz obe strany a over uniqueness matching labels.

## 22. Histograms a latency

Classic histogram quantile:

```promql
histogram_quantile(
  0.95,
  sum by (le, service) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)
```

Pre threshold-based SLI je často presnejšie použiť priamo cumulative bucket:

```promql
sum(rate(http_request_duration_seconds_bucket{le="0.5"}[5m]))
/
sum(rate(http_request_duration_seconds_count[5m]))
```

Bucket boundaries musia zodpovedať SLO thresholds a reálnej distribution.

## 23. Recording rules

Recording rule predpočíta PromQL expression a uloží výsledok ako novú series.

Použitie:

- drahé alebo opakované dashboards,
- štandardné service-level rates,
- SLI numerators a denominators,
- hierarchické agregácie,
- zjednotenie query contractu.

Príklad:

```yaml
groups:
  - name: service-red
    rules:
      - record: service:http_requests:rate5m
        expr: |
          sum by (service) (
            rate(http_requests_total[5m])
          )
```

Naming má vyjadriť level, metric semantics a operation.

Recording rule môže maskovať source-label zmenu. Testuj rules proti fixture alebo representative data.

## 24. Alerting rules

Alerting rule vyhodnocuje PromQL condition.

```yaml
groups:
  - name: service-alerts
    rules:
      - alert: ServiceHighErrorRate
        expr: |
          (
            sum by (service) (
              rate(http_requests_total{status_code=~"5.."}[5m])
            )
            /
            sum by (service) (
              rate(http_requests_total[5m])
            )
          ) > 0.05
        for: 10m
        labels:
          severity: page
        annotations:
          summary: "High error rate for {{ $labels.service }}"
```

Prometheus alert lifecycle:

```text
inactive
→ pending počas `for`
→ firing
→ resolved po zániku condition
```

`for` filtruje krátke transient conditions. Nesmie však odkladať detekciu kritického rýchleho outage bez analýzy.

Labels určujú identity a routing alertu. Annotations nesú dynamický ľudský context a links.

## 25. Rule evaluation

Sleduj:

- evaluation duration,
- missed iterations,
- rule failures,
- query sample limits,
- number of active series,
- evaluation interval,
- dependency na recording rules.

Drahá rule môže spomaliť celý group evaluation.

Rozdeľ rule groups podľa:

- požadovaného evaluation intervalu,
- dependency poradia,
- ownershipu,
- failure blast radiusu.

## 26. Configuration validation a reload

Konfiguráciu a rules validuj cez `promtool`.

Príklady:

```bash
promtool check config prometheus.yml
promtool check rules rules/*.yml
```

Prometheus môže reload-nuť validnú konfiguráciu cez `SIGHUP` alebo `POST /-/reload`, ak je lifecycle endpoint povolený.

Pri neplatnej konfigurácii sa nová konfigurácia neaplikuje. Monitoruj reload success a logs.

## 27. Remote write

Remote write streamuje samples do kompatibilného receivera.

Použitie:

- long-term storage,
- centralizovaná metrics platforma,
- multi-cluster aggregation,
- managed monitoring backend.

Pipeline obsahuje lokálne queues, batching, sharding a retries.

Sleduj:

- pending samples,
- queue capacity,
- failed/retried samples,
- oldest unsent timestamp,
- dropped samples,
- WAL retention voči outage duration,
- network a receiver throttling.

Remote-write outage nesmie nekontrolovane vyčerpať disk alebo memory Prometheus servera.

## 28. Remote read a global query

Remote read umožňuje query engine-u načítať dáta z externého systému, ale presný contract a performance závisia od backendu.

Global query vrstvy alebo compatible ecosystems môžu poskytovať:

- query naprieč viacerými Prometheus servers,
- HA replica deduplication,
- long-term object storage,
- tenant isolation,
- global recording/alerting.

Prometheus samotný nevytvára automaticky jeden globally consistent metrics cluster.

## 29. Federation

Federation scrape-ne vybrané aggregated alebo raw series z iného Prometheus servera cez federation endpoint.

Použitie:

- hierarchické aggregation,
- global overview metrics,
- vybrané cross-cluster signals.

Riziká:

- duplicate series,
- nejasné external labels,
- prenesenie vysokej cardinality,
- failure dependency medzi tiers,
- oneskorenie a staleness.

Federation nie je univerzálna náhrada scalable long-term storage.

## 30. High availability

Bežný HA model spúšťa dve alebo viac nezávislých Prometheus replicas s rovnakou konfiguráciou.

Každá replika:

- scrape-ne targets samostatne,
- má vlastný local TSDB,
- vyhodnocuje rules,
- posiela alerts Alertmanagerom.

Dôsledky:

- local queries môžu mať mierne odlišné samples,
- obe repliky vytvárajú duplicate metrics v centrálnej vrstve bez deduplication,
- alert labels musia umožniť Alertmanager deduplication,
- external replica label sa typicky odstráni pri alert identity alebo deduplikuje downstream.

Nedávaj iba jednu repliku za load balancer a nepovažuj to za shared-state cluster.

## 31. Kubernetes deployment

Prometheus v Kubernetes typicky používa:

- StatefulSet,
- persistent volume,
- ServiceAccounts a RBAC pre discovery,
- ServiceMonitor/PodMonitor pri Prometheus Operator modeli,
- ConfigMap/Secret alebo generated configuration,
- resource requests/limits,
- anti-affinity/topology spread,
- PodDisruptionBudget podľa dostupnosti,
- local alebo remote storage strategy.

Riziká:

- TSDB disk saturation,
- memory rast pre cardinality,
- duplicate discovery,
- scrape cez nesprávny Service port,
- RBAC discovery failure,
- Operator reconciliation override,
- retention väčšia než volume capacity.

## 32. Security

Chráň:

- Prometheus UI a HTTP API,
- scrape credentials,
- remote-write credentials,
- service-discovery permissions,
- rule/configuration repository,
- admin/lifecycle endpoints,
- network access k metrics endpointom.

Metrics môžu odhaliť:

- interné hostname,
- topology,
- customer identifiers,
- software versions,
- business volume,
- security state.

Do labels alebo metric values nepatria secrets ani unbounded personal identifiers.

## 33. Self-monitoring

Prometheus musí monitorovať sám seba.

Sleduj:

- process CPU/memory,
- TSDB head series,
- samples ingested,
- series churn,
- WAL a compaction failures,
- disk space,
- scrape failures a duration,
- query duration a concurrency,
- rule evaluation failures,
- remote-write backlog,
- config reload success,
- target count a discovery errors.

Samostatný Prometheus alebo external check môže monitorovať kritickú monitoring platformu, aby úplný výpadok nebol neviditeľný.

## 34. Troubleshooting target down

Postup:

```text
je target objavený?
→ `/service-discovery` metadata
→ target relabeling result
→ `/targets` error
→ DNS a address
→ route/firewall/NetworkPolicy
→ TLS/auth
→ metrics path a port
→ response time a size
→ valid exposition
→ scrape timeout/limits
```

Príkazy:

```bash
curl -vk https://target.example.internal:9443/metrics
promtool check config prometheus.yml
```

Test vykonaj z rovnakej network boundary ako Prometheus.

## 35. Troubleshooting missing series

```text
target `up`?
→ metric je v raw `/metrics`?
→ target relabeling zachovalo target?
→ metric relabeling nedropuje series?
→ labels sa nezmenili?
→ query time range a selector?
→ staleness?
→ recording rule failure?
→ remote-write/backend ingestion?
```

Porovnaj:

- raw endpoint,
- Prometheus expression browser,
- rule output,
- remote backend.

## 36. Troubleshooting high memory alebo disk

Over:

- active head series,
- new series rate,
- label-value explosion,
- scrape sample counts,
- target churn,
- histogram bucket count,
- duplicate targets,
- retention,
- compaction/WAL stav,
- remote-write backlog,
- dashboard/rule query pressure.

Cardinality incident workflow:

1. identifikuj metric a label s rastom,
2. zastav alebo metric-relabel-ni unbounded source,
3. zachovaj evidence a ownera,
4. oprav instrumentation contract,
5. over pokles active series,
6. zhodnoť disk/memory recovery lifecycle.

## 37. Troubleshooting slow PromQL

Over:

- broad selectors,
- príliš dlhý range,
- vysokú cardinality,
- regex matchers,
- many-to-many joins,
- subqueries,
- histogram buckets,
- chýbajúce recording rules,
- dashboard refresh a variable fan-out,
- concurrent users/rules.

Najprv zmenši scope a zobraz počet výsledných series. Recording rule používaj na stabilný opakovaný výpočet, nie ako maskovanie nesprávneho data modelu.

## 38. Anti-patterny

### Prometheus ako event alebo log store

Time-series model nie je vhodný na unikátne payloady a per-event vysokú cardinality.

### User ID, request ID alebo trace ID v labels

Vytvára neobmedzený počet series.

### `up == 1` ako jediný service health signal

Metrics endpoint môže fungovať, zatiaľ čo business path zlyháva.

### Summary quantiles agregované naprieč instances

Client-side quantiles nie sú všeobecne agregovateľné.

### Scrape interval 5 sekúnd pre všetko

Zvyšuje load a storage bez jasnej detection potreby.

### Metric relabeling bez dependency auditu

Dashboardy, rules a SLO môžu ticho stratiť vstupy.

### Jedna Prometheus replika s lokálnym diskom ako enterprise DR

Nemá nezávislú availability ani long-term recovery model.

### Alert labels s dynamickým textom

Každá hodnota vytvorí novú alert identity a poškodí deduplication/routing.

## 39. Kontrolné otázky

1. Ako funguje pull-based scrape model?
2. Čo presne znamená `up`?
3. Ako metric name a labels vytvárajú time series?
4. Aký je rozdiel medzi target a metric relabelingom?
5. Prečo je cardinality hlavný operational risk?
6. Kedy použiť histogram a prečo summary quantiles nemožno bežne agregovať?
7. Ako fungujú WAL, head block, compaction a retention?
8. Čo je staleness a ako ovplyvňuje missing metrics?
9. Ako sa líši recording a alerting rule?
10. Aké sú hranice Prometheus HA modelu?
11. Ako diagnostikuješ remote-write backlog?
12. Kedy federation nestačí?

## Glossary impact

Relevantné pojmy: Prometheus, scrape, target, exporter, Pushgateway, time series, sample, label set, service discovery, target relabeling, metric relabeling, external labels, local TSDB, WAL, head block, compaction, staleness, PromQL, instant vector, range vector, vector matching, recording rule, alerting rule, remote write, remote read, federation, Prometheus HA, native histogram a series churn.

## Primárne zdroje

- [Prometheus overview](https://prometheus.io/docs/introduction/overview/)
- [Prometheus data model](https://prometheus.io/docs/concepts/data_model/)
- [Prometheus metric types](https://prometheus.io/docs/concepts/metric_types/)
- [Prometheus configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
- [PromQL basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Prometheus storage](https://prometheus.io/docs/prometheus/latest/storage/)
- [Recording rules](https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/)
- [Alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Remote write tuning](https://prometheus.io/docs/practices/remote_write/)
- [Federation](https://prometheus.io/docs/prometheus/latest/federation/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Golden Signals](golden-signals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Alertmanager →](alertmanager.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
