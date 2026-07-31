# Golden Signals

Google SRE používa štyri Golden Signals pre user-facing systémy: **Latency**, **Traffic**, **Errors** a **Saturation**. Ich hodnota nevzniká tým, že dashboard obsahuje štyri panely. Vzniká až vtedy, keď všetky štyri signals opisujú kompatibilný user alebo caller outcome, správnu measurement boundary a relevantnú capacity risk.

Golden Signals spájajú dve otázky: čo práve zažíva caller a ako blízko je systém k mechanizmu, ktorý tento outcome poškodí. Ak latency meria iba úspešné synchronous requests, errors iba HTTP 5xx, traffic všetky retries a saturation CPU hosta, panely opisujú štyri odlišné populations a nevytvárajú jeden operational model.

## Outcome-first lifecycle

```text
user journey a SLO
→ exact operation a valid population
→ Traffic ako demand
→ Errors ako incorrect outcomes
→ Latency ako end-to-end distribution
→ Saturation ako leading capacity risk
→ bounded cohort dimensions
→ SLO/burn a investigation dashboard
→ dependency a resource decomposition
→ containment, recovery a validation
```

Atlas Payments používa operation `payment.settle` pre valid enterprise payments. Operation začína pridelením stable idempotency key a končí provider confirmation plus ledger/outbox commitom. HTTP `202` je iba entry boundary.

## Exact Golden Signals subject

```yaml
subject: GS-PAY-43
service: Atlas Payments
logicalOperation: payment.settle
population: valid enterprise settlement operations
success: one completed settlement with matching ledger state
latencyBoundary: accepted operation ID -> final completion
dimensions:
  - provider
  - merchant_class
  - region
  - availability_zone
  - release_channel
capacityRisks:
  - queue age
  - provider concurrency
  - database pool wait
  - NAT port allocation
```

Dynamic operation IDs zostávajú v traces a logs. Golden Signals metrics používajú bounded cohorts.

## Traffic: demand, nie iba počet requestov

Traffic reprezentuje workload, ktorý systém prijíma. Pri asynchronous journey je potrebné rozlíšiť logical operations od technical attempts:

```promql
sum by (merchant_class) (
  rate(payment_settlement_started_total{
    environment="production"
  }[5m])
)
```

Táto query preukazuje observed started logical operations za sekundu podľa merchant class. Ak producer incrementuje counter pred idempotency claimom, client retries môžu population nafúknuť. Contract preto určuje presný increment point.

Technical traffic sa sleduje samostatne:

```promql
sum(rate(http_server_requests_total{
  service="payments-api",
  route="POST /payments/{id}/settle"
}[5m]))
```

Rozdiel medzi HTTP attempts a logical starts ukazuje edge/client retry amplification alebo rejected duplicates. Provider attempts per operation zase odhaľuje downstream retries.

Traffic panel bez expected seasonality a capacity contextu nevie rozlíšiť úspešný business growth od retry stormu.

## Errors: incorrect caller alebo business outcome

Errors zahŕňajú všetky outcomes, ktoré porušia operation contract, nie iba process exceptions. Pre settlement sú to terminal provider rejection, exhausted retry budget, duplicate settlement, conflicting ledger state alebo operation, ktorá nebola dokončená do reconciliation deadline-u.

```promql
sum by (error_class) (
  rate(payment_settlement_completed_total{
    environment="production",
    result!="success"
  }[5m])
)
/
sum(rate(payment_settlement_started_total{
  environment="production"
}[5m]))
```

Výsledok preukazuje observed non-success completions voči starts v rovnakom okne. Pending operations ešte nemusia byť v numerator-e, preto sa samostatne sleduje oldest unresolved age. `202` responses nie sú final success a provider `429` je attempt error, ktorý môže skončiť úspešným logical outcome-om alebo terminal timeoutom.

Fast errors môžu zlepšiť aggregate latency, preto error a latency panel musia používať explicitné populations.

## Latency: distribution celého outcome-u

Latency začína na caller-relevant boundary a končí výsledkom, ktorý caller potrebuje. Atlas sleduje end-to-end completion, queue wait, provider request a database acquisition oddelene.

```promql
histogram_quantile(
  0.99,
  sum by (le, merchant_class) (
    rate(payment_settlement_duration_seconds_bucket{
      environment="production",
      result="success"
    }[5m])
  )
)
```

Query odhaduje p99 úspešných completions podľa histogram buckets. Nepreukazuje latency terminal errors ani operations, ktoré ešte neskončili. Preto sa dopĺňa successful/error distributions a unresolved age.

SLO compliance pri boundary 2.5 s:

```promql
sum(rate(payment_settlement_duration_seconds_bucket{
  environment="production",
  le="2.5"
}[5m]))
/
sum(rate(payment_settlement_started_total{
  environment="production"
}[5m]))
```

Tento pomer je správny iba ak numerator reprezentuje unikátne completed operations a denominator kompatibilné starts. Ak histogram obsahuje retries alebo iba success population, recording rule musí semantics upraviť.

## Saturation: leading signal kapacitného mechanizmu

Saturation ukazuje queued alebo throttled work. Nie je synonymom CPU utilization. Relevantný signal závisí od bottleneck modelu:

```promql
max(
  db_pool_waiting_requests{
    service="payments-api"
  }
)

max(
  payment_queue_oldest_message_age_seconds{
    queue="settlement"
  }
)

sum(rate(container_cpu_cfs_throttled_periods_total{
  namespace="payments",
  container="payments-api"
}[5m]))
/
sum(rate(container_cpu_cfs_periods_total{
  namespace="payments",
  container="payments-api"
}[5m]))
```

Prvá query preukazuje current pool waiters, druhá oldest queue age a tretia CPU quota throttling ratio. Žiadna sama nepreukazuje user impact. Golden Signals dashboard koreluje saturation s traffic, latency a errors pre rovnaký cohort a time window.

Saturation môže byť zdravý backpressure. Queue rast počas krátkeho burstu je prijateľný, ak age ostáva pod deadline a downstream sa nepreťažuje. Alarm sa viaže na business deadline a trend, nie na nenulovú queue depth.

## Jeden dashboard, kompatibilné populations

Golden Signals dashboard pre `payment.settle` používa:

```text
Traffic: logical starts/s a completions/s
Errors: terminal incorrect outcomes / starts
Latency: end-to-end p50/p95/p99, success aj error
Saturation: queue age, pool wait, provider concurrency, CPU throttling
Context: release, AZ, provider config a deployment annotations
Telemetry health: scrape/export/query canary
```

Raw panel query sa overí cez backend API:

```bash
curl -fsS -G 'http://prometheus:9090/api/v1/query_range' \
  --data-urlencode 'query=max(payment_queue_oldest_message_age_seconds{queue="settlement"})' \
  --data-urlencode 'start=2026-07-29T09:10:00Z' \
  --data-urlencode 'end=2026-07-29T09:35:00Z' \
  --data-urlencode 'step=30s' \
  | jq '.data.result'
```

Príkaz preukazuje backend samples pre exact query a time range. Nepreukazuje, že Grafana panel používa rovnaký data source, variables alebo transformations; panel query inspector sa kontroluje samostatne.

## Golden Signals a SLO

Golden Signals podporujú investigation, ale SLO potrebuje presnú SLI population a objective. Error budget burn alert by mal vychádzať z user outcome. Resource saturation môže byť warning alebo contextual alert, ak ešte nepoškodzuje outcome.

Fast burn signal:

```promql
(
  1 - (
    sum(rate(payment_settlement_completed_total{result="success"}[5m]))
    /
    sum(rate(payment_settlement_started_total[5m]))
  )
)
/
(1 - 0.999)
```

Výsledok vyjadruje observed error ratio ako násobok povoleného 0.1 % budgetu, ak metrics majú kompatibilné semantics. Alerting rule zvyčajne kombinuje short a long windows, aby zachytila rýchly incident bez page-u na krátky noise.

## Worked incident: traffic stabilný, latency a errors rastú iba v jednej cohorte

Pri `OBS-PAY-43` je logical traffic stabilný. HTTP acceptance ostáva `99.98 %`, no enterprise completion errors rastú v `eu-central-1b`. End-to-end p99 prekročí 12 s. Queue age je 40 ms a pool wait nízky, ale provider concurrency je na limite a attempts per operation stúpnu na 2.8.

Golden Signals vedú investigation takto. Traffic vylúči pokles demandu. Errors lokalizujú `1b/CFG-34`. Latency ukáže end-to-end, nie handler problém. Saturation provider concurrency vysvetlí retry amplification, ale nie pôvodný TLS error. Trace a logs následne ukážu `unknown_ca` na stale trust bundle.

Containment odoberie affected cohort z enterprise routing-u a zníži retry concurrency. Recovery nasadí `PROVIDER-CFG-35`, overí mTLS a obnoví traffic po vlnách.

Acceptance vyžaduje business success nad SLO, p99 pod 2.5 s, provider attempts per operation na baseline, nulový stale-config cohort a telemetry canary. Forbidden test spustí old config v isolated cohort-e a musí zlyhať bez vstupu do production routing-u.

## Praktické query validation

PromQL syntax a rule behavior sa testujú pred rolloutom:

```yaml
groups:
  - name: atlas-payments-golden-signals
    interval: 30s
    rules:
      - record: service:payment_settlement_started:rate5m
        expr: sum(rate(payment_settlement_started_total[5m]))
      - record: service:payment_settlement_error_ratio:rate5m
        expr: |
          sum(rate(payment_settlement_completed_total{result!="success"}[5m]))
          /
          sum(rate(payment_settlement_started_total[5m]))
```

```bash
promtool check rules golden-signals.rules.yml

promtool test rules golden-signals.test.yml
```

`check rules` preukazuje parse a rule syntax, nie správnu business semantics. Unit test s input series a expected samples overí vybrané scenarios, ale production population, missing data a scrape lag sa testujú canary a shadow dashboardom.

## Anti-patterny

Golden Signals zlyhajú, keď traffic počíta retries, errors iba HTTP 5xx, latency iba successful handler duration a saturation CPU pri database bottlenecku. Ďalším problémom je panel bez denominatora alebo units, aggregate bez cohort dimensions a no-data zobrazené ako nula.

Dashboard nemá byť wallboard s desiatkami všeobecných resources. Začína user outcome a až potom vedie k dependency a USE detailu.

## Kontrolné otázky

1. Prečo musia Golden Signals používať kompatibilnú population?
2. Aký rozdiel je medzi logical trafficom a HTTP attempts?
3. Prečo `202` nie je final success?
4. Čo end-to-end p99 zahŕňa navyše oproti handler latency?
5. Prečo saturation nie je iba CPU utilization?
6. Kedy queue depth predstavuje zdravý backpressure?
7. Čo raw Prometheus API query preukazuje a čo nie o Grafana paneli?
8. Ako Golden Signals viedli incident `OBS-PAY-43`?
9. Čo `promtool check rules` nepreukazuje?
10. Kedy saturation patrí do page alertu a kedy iba do contextu?

## Oficiálna dokumentácia

- [Google SRE Workbook: Monitoring](https://sre.google/workbook/monitoring/)
- [Prometheus recording rules](https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/)
- [Prometheus rule unit testing](https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: USE method](use-method.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Prometheus →](prometheus.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
