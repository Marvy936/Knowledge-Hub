# RED method

RED je service-oriented measurement model pre workloady, ktoré prijímajú jednotku práce a produkujú caller-visible alebo business-visible outcome. Sleduje **Rate**, **Errors** a **Duration**, ale tieto tri slová nemajú význam bez presnej operation boundary, denominatora a success contractu.

RED nie je univerzálny dashboard template. Pri zlom scope-e môže vyzerať zdravo a súčasne maskovať retry amplification, fast failures, queue wait alebo nedokončený asynchronous outcome. Správny RED model začína logical operation a až potom vyberá metrics.

## Logical operation pred technical attemptom

Atlas Payments rozlišuje:

```text
logical operation: settle(payment_id)
technical attempts:
  HTTP POST /settle
  queue delivery alebo redelivery
  provider API attempt alebo retry
  ledger transaction attempt
final outcome:
  one settled payment or one explicit terminal failure
```

Ak každý retry zvýši request counter, technical rate môže rásť počas incidentu, hoci business throughput klesá. Error denominator môže tiež klamať, ak retry success prekryje prvý failure a používateľ čaká desiatky sekúnd.

Dominantný RED lifecycle je:

```text
user alebo caller outcome
→ exact logical-operation boundary
→ valid population
→ Rate denominator
→ Error numerator a success semantics
→ Duration start/end a distribution
→ bounded cohort dimensions
→ attempt/retry/fan-out decomposition
→ dashboard alebo alert
→ dependency a resource investigation
→ recovery a business validation
```

## Exact RED subject

Pre `OBS-PAY-43`:

```yaml
operation: payment.settle
population: valid enterprise settlement operations
startBoundary: API accepted stable operation ID
endBoundary: provider confirmed and ledger/outbox committed
success: exactly one terminal completed state
error:
  - terminal provider rejection
  - exhausted retry budget
  - reconciliation timeout
  - duplicate or conflicting completion
latencyObjective: 99.9% complete within 2.5s over 28d
dimensions:
  - provider
  - merchant_class
  - region
  - availability_zone
  - release_channel
```

Dynamic payment ID alebo trace ID nie sú metric dimensions. Tie patria do exemplars, traces alebo protected logs.

## Rate: koľko práce systém skutočne prijíma a dokončuje

Request rate môže merať technical attempts:

```promql
sum by (route) (
  rate(http_server_requests_total{
    service="payments-api",
    environment="production"
  }[5m])
)
```

Query preukazuje per-second increase HTTP countera. Nepreukazuje počet unikátnych business operations, ak client alebo proxy retryuje.

Logical start a completion sa preto merajú samostatne:

```promql
sum(rate(payment_settlement_started_total{
  environment="production"
}[5m]))

sum(rate(payment_settlement_completed_total{
  environment="production",
  result="success"
}[5m]))
```

Rozdiel medzi rates môže znamenať in-flight work, backlog, terminal failures, lost completion telemetry alebo population mismatch. Nie je automaticky „error rate“. Rate dashboard má zobraziť accepted logical operations, technical attempts, completions a retry amplification spolu.

Retry amplification ratio:

```promql
sum(rate(payment_provider_attempts_total[5m]))
/
sum(rate(payment_settlement_started_total[5m]))
```

Hodnota `3.2` znamená priemerne 3.2 provider attempts na jednu started operation v rovnakom okne, ak counters používajú kompatibilnú population. Neurčuje, či retries boli legitímne alebo duplicitné; trace a idempotency evidence musia vysvetliť mechanizmus.

## Errors: zlyhanie podľa caller a business contractu

HTTP `500` je technical error. HTTP `202` môže byť technical success a business failure, ak workflow nikdy nedokončí settlement. Provider `429` môže byť retryable attempt error, ale po vyčerpaní budgetu sa stane terminal logical-operation error.

Business error ratio:

```promql
sum(rate(payment_settlement_completed_total{
  environment="production",
  result=~"terminal_error|duplicate|timeout"
}[5m]))
/
sum(rate(payment_settlement_started_total{
  environment="production"
}[5m]))
```

Táto query preukazuje observed terminal outcomes voči started population. Ak unresolved operations ešte nemajú completion record, krátke okno môže error ratio podhodnotiť. Preto sa dopĺňa age alebo pending-state metric.

Fast failure môže zlepšiť duration a zhoršiť outcome. Dashboard, ktorý zobrazuje iba p95 úspešných requests, môže počas plošných `401` alebo `503` vyzerať rýchlejší. Error a duration sa interpretujú spolu a duration population musí byť explicitná.

Error classification má bounded classes, napríklad `validation`, `dependency_timeout`, `dependency_rejected`, `internal`, `duplicate` a `unknown_outcome`. Raw exception message ako label je nestabilný a high-cardinality.

## Duration: odkiaľ a dokiaľ meriame čas

Duration boundary rozhoduje, čo metric vysvetľuje. HTTP handler môže trvať `84 ms`, kým asynchronous settlement dokončí za 12 sekúnd. Worker processing môže byť rýchle, ale queue wait dlhý.

End-to-end histogram:

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

Query odhaduje p99 successful operation duration podľa buckets. Nepreukazuje error duration ani pending operations, ktoré ešte nevstúpili do completion histogramu. Dopĺňa sa queue age a unresolved operation age.

Queue wait:

```promql
histogram_quantile(
  0.95,
  sum by (le, queue) (
    rate(payment_queue_wait_seconds_bucket[5m])
  )
)
```

Provider latency:

```promql
histogram_quantile(
  0.95,
  sum by (le, provider) (
    rate(payment_provider_request_duration_seconds_bucket[5m])
  )
)
```

Spoločný dashboard umožní rozhodnúť, či end-to-end latency vzniká pred workerom, v providerovi alebo pri ledger locku. Sčítanie p95 jednotlivých komponentov však nedá p95 totalu; percentiles nie sú všeobecne aditívne.

## Histograms, buckets a native histograms

Classic histogram exportuje bucket series s labelom `le`, sum a count. Bucket boundaries musia pokryť SLO a reálnu distribution. Ak najbližší bucket okolo 2.5 s je 2 s a 5 s, quantile a SLI majú hrubú resolution.

SLO compliance z classic histogramu:

```promql
sum(rate(payment_settlement_duration_seconds_bucket{
  environment="production",
  le="2.5"
}[5m]))
/
sum(rate(payment_settlement_duration_seconds_count{
  environment="production"
}[5m]))
```

Výsledok preukazuje podiel observed completed histogram observations do 2.5 s. Ak errors nie sú observed v histograme, SLI potrebuje kombinovať latency a correctness contract.

Prometheus podporuje aj native histograms podľa enabled feature a producer compatibility. Migrácia nie je iba zmena storage typu; queries, recording rules, remote write a dashboards musia akceptovať nový sample model. Current product behavior sa overuje v oficiálnej dokumentácii pre nasadenú version.

## Bounded dimensions a cohort slicing

RED musí umožniť rozlíšiť meaningful cohorts bez cardinality explosion. Pre Atlas sú vhodné provider, merchant class, Region, AZ a release channel. Full semantic version môže byť bounded iba pri kontrolovanom počte active releases; commit SHA na každý build môže výrazne zvýšiť churn.

Cohort query incidentu:

```promql
sum by (availability_zone, provider_config_generation) (
  rate(payment_settlement_completed_total{
    merchant_class="enterprise",
    result="terminal_error"
  }[5m])
)
```

Query preukáže, že errors sú koncentrované na `eu-central-1b/PROVIDER-CFG-34`. Neurčuje TLS root cause. Exemplar alebo trace prejde k failing span-u a logu s `unknown_ca`.

## RED dashboard ako investigation mapa

Silný dashboard začína user outcome a postupne rozkladá mechanismus:

```text
logical operation Rate, Errors, Duration
→ technical attempt rate a retries
→ queue wait a backlog
→ provider request RED
→ ledger transaction RED
→ release/AZ/config cohorts
→ deployment a telemetry health annotations
```

Dashboard nemá ukazovať iba celkový average. Graf musí zachovať denominator, units, time range, data source a query generation. Panel `No data` je odlišný od nuly.

Raw query možno overiť cez Prometheus API:

```bash
curl -fsS -G 'http://prometheus:9090/api/v1/query_range' \
  --data-urlencode 'query=sum by (availability_zone) (rate(payment_settlement_completed_total{result="terminal_error"}[5m]))' \
  --data-urlencode 'start=2026-07-29T09:10:00Z' \
  --data-urlencode 'end=2026-07-29T09:35:00Z' \
  --data-urlencode 'step=30s' \
  | jq '.data.result'
```

Príkaz preukazuje range-query samples z konkrétneho Prometheus backendu. Grafana môže používať recording rule, iný data source alebo transformation, preto sa effective panel request kontroluje samostatne.

## Worked incident: HTTP RED je green, business RED zlyháva

Dňa `2026-07-29` Atlas release `7.19.0` vracia `202` s success rate `99.98 %` a handler p95 `84 ms`. Business completion SLO však horí pre enterprise merchants.

HTTP RED monitoruje entry attempt. Logical settlement RED ukáže:

```text
started rate: stabilný
completed success rate: pokles v 1b
terminal error rate: rast v 1b/CFG-34
end-to-end p99: nad 12 s
provider attempts per operation: 2.8
queue wait p95: 40 ms
```

Nízky queue wait odstraňuje backlog ako vedúcu hypotézu. Provider attempt RED lokalizuje error class `tls`, ale až trace/log evidence ukáže stale trust bundle. Retry ratio `2.8` vysvetľuje rast provider trafficu a zakazuje plošné zvýšenie retries.

Containment odoberie affected cohort z enterprise routingu. Recovery načíta `PROVIDER-CFG-35`, spustí canary a obnoví traffic vo vlnách. Acceptance vyžaduje normalizovaný logical success rate, p99 pod 2.5 s, retry ratio blízky baseline, jeden settlement per operation a forbidden old config cohort bez eligibility.

Skorší control pridá rollout gate, ktorý porovná loaded config generation a vykoná final settlement synthetic. HTTP readiness samotná nestačí.

## RED anti-patterny

Najčastejšie zlyhania vznikajú, keď rate počíta attempts namiesto operations, errors zahŕňajú iba HTTP 5xx, duration končí pred asynchronous completion, percentiles sa priemerujú alebo sčítavajú, a labels obsahujú dynamic IDs. Ďalším anti-patternom je alert z raw request countu bez traffic denominatora alebo seasonality.

RED tiež nie je náhrada USE. RED ukáže service symptom; USE pomôže lokalizovať resource utilization, saturation a errors. Traces a logs vysvetlia causal path a detail.

## Kontrolné otázky

1. Aký rozdiel je medzi logical operation a technical attempt?
2. Prečo request rate môže počas incidentu rásť, hoci business throughput klesá?
3. Prečo `202` nie je final success settlementu?
4. Čo retry amplification ratio preukazuje a čo nie?
5. Prečo p95 úspešných requests môže vyzerať lepšie počas incidentu?
6. Ako sa líšia handler, queue, provider a end-to-end duration?
7. Prečo percentiles nemožno jednoducho sčítať?
8. Čo classic histogram SLO query skutočne meria?
9. Ako RED lokalizoval incident `OBS-PAY-43`?
10. Kedy pokračuješ z RED do USE, traces alebo logs?

## Oficiálna dokumentácia

- [The RED method](https://grafana.com/blog/2018/08/02/the-red-method-how-to-instrument-your-services/)
- [Prometheus metric types](https://prometheus.io/docs/concepts/metric_types/)
- [PromQL rate](https://prometheus.io/docs/prometheus/latest/querying/functions/#rate)
- [Prometheus histograms](https://prometheus.io/docs/practices/histograms/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Instrumentation a telemetry](instrumentation-telemetry.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: USE method →](use-method.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
