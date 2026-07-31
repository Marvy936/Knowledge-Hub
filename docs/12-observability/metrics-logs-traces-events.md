# Metrics, logs, traces a events

Metrics, logs, traces, events, audit records a profiles nie sú rôzne vizualizácie toho istého faktu. Každý signal zachováva inú časť reality a inú časť zahadzuje. Metric komprimuje veľa occurrences do time series. Log zachováva vybraný record s detailom. Trace modeluje causal path jednej sampled operation. Event zaznamenáva state transition alebo occurrence. Audit record viaže actor, action a target. Profile agreguje, kde runtime spotreboval CPU, memory alebo inú resource dimension.

Silný observability systém nevyberá „najlepší signal“. Navrhuje, ktorý signal je authority pre ktorú otázku, ako sa signals korelujú a kde sú ich coverage, sampling a retention hranice.

## Od system occurrence k evidence

```text
system alebo business occurrence
→ observation point
→ telemetry record generation
→ signal-specific model a strata detailu
→ resource, operation, context a schema identity
→ collection, processing a storage
→ query alebo derived signal
→ evidence-quality verdict
→ operational decision
```

Udalosť v systéme nie je totožná s telemetry recordom. Record nemusí byť prijatý, durable ani queryovateľný. Query result zase nemusí reprezentovať správnu population. Pri každom signale preto sleduj producer, schema generation, sampling, route, backend a consumer query.

## Connected subject

Atlas settlement subject `OBS-PAY-43` používa stable logical operation `settle(payment_id)` a correlation context:

```yaml
service.name: payments-api
service.version: 7.19.0
deployment.environment.name: production
cloud.region: eu-central-1
cloud.availability_zone: eu-central-1b
operation.name: payment.settle
payment.operation.id: op-884
trace_id: 4bf92f3577b34da6a3ce929d0e0e4736
telemetry.schema: atlas-payments-12
```

Nie všetky fields patria do každého signal typu. `payment.operation.id` je vhodný v protected logu alebo trace, ale ako Prometheus label by vytvoril jednu series na operation. Metrics preto používajú bounded dimensions, napríklad `operation`, `result_class`, `provider`, `region`, `availability_zone` a controlled `release_channel`.

## Metrics: agregovaný state a trend

Metric je time series identifikovaná menom a label setom. Counter rastie pre occurrences, gauge reprezentuje current value, histogram rozdeľuje observations do buckets a summary vykonáva client-side quantile aggregation s vlastnými trade-offmi.

Counter pre final settlement:

```text
payment_settlement_completed_total{
  environment="production",
  result="success",
  provider="provider-a"
} 184233
```

Rate query:

```promql
sum by (provider) (
  rate(payment_settlement_completed_total{
    environment="production",
    result="success"
  }[5m])
)
```

Táto query preukazuje priemerný per-second increase countera v danom okne, agregovaný podľa providera. Nepreukazuje unikátne payment operations, ak producer incrementuje counter pri každom retry attempt-e.

Histogram umožňuje server-side vypočítať quantile nad agregovanými buckets:

```promql
histogram_quantile(
  0.95,
  sum by (le, provider) (
    rate(payment_settlement_duration_seconds_bucket{
      environment="production"
    }[5m])
  )
)
```

Výsledok odhaduje p95 podľa bucket boundaries. Nejde o presnú hodnotu každého requestu a accuracy závisí od vhodných buckets. Ak queue wait nie je zahrnutý do duration boundary, rýchly worker histogram môže maskovať pomalý end-to-end settlement.

Metrics sú vhodné pre SLI, trends, capacity a alerting, pretože sú lacné na agregáciu. Nie sú vhodné na uloženie každého request ID alebo payload detailu.

## Logs: detail vybraného observation pointu

Structured log record má stabilnú schema a explicitný event meaning:

```json
{
  "timestamp": "2026-07-29T09:18:42.114Z",
  "severity": "ERROR",
  "service": "provider-adapter",
  "serviceVersion": "7.19.0",
  "operation": "payment.settle.provider_call",
  "paymentOperationId": "op-884",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
  "availabilityZone": "eu-central-1b",
  "configGeneration": "PROVIDER-CFG-34",
  "errorType": "tls.unknown_ca",
  "outcome": "failure"
}
```

Record preukazuje, že konkrétny producer zaznamenal failure s daným contextom. Nepreukazuje automaticky, že request začal iba raz, že log bol durable v centrálnom backende alebo že rovnaký error ovplyvnil celú population.

Log schema má definovať required fields, types, redaction a version transition. Free-text message je užitočná pre človeka, ale stable investigation queries sa viažu na structured fields. Raw token, card data a celé provider payloads sa nesmú logovať.

Praktická Loki query:

```logql
{service="provider-adapter", environment="production"}
| json
| errorType="tls.unknown_ca"
| availabilityZone="eu-central-1b"
| line_format "{{.traceId}} {{.configGeneration}} {{.paymentOperationId}}"
```

Táto query preukazuje matching uložené log records v selected tenant/time range. Prázdny výsledok nepreukazuje neprítomnosť incidentu, kým nie je overená producer emission, Fluent Bit/Collector route, Loki ingest a retention.

## Traces: causal graph sampled operation

Trace spája spans cez trace a parent context. Span má operation name, start/end, status, attributes, events a links. Expected graph pre settlement môže byť:

```text
HTTP POST /settle
└── payment.settle
    ├── database.idempotency_claim
    ├── queue.publish
    └── provider-a.authorize
        └── TLS handshake
```

TraceQL query v Tempo:

```traceql
{
  resource.service.name = "provider-adapter" &&
  span.payment.provider = "provider-a" &&
  status = error
}
| by(resource.cloud.availability_zone)
```

Query preukazuje stored sampled traces, ktoré spĺňajú conditions. Nepreukazuje population rate, ak sampling nie je známy alebo unbiased. Trace s errorom môže vysvetliť mechanizmus, zatiaľ čo metric určí, koľko operations bolo affected.

Context propagation je correctness boundary. Ak async queue consumer nevytvorí link alebo pokračovanie contextu, trace graph sa rozpadne aj keď business workflow pokračuje. Missing span môže znamenať sampling, propagation, instrumentation alebo export failure.

## Events a audit records

Domain event reprezentuje business state transition, napríklad `PaymentSettlementCompleted`. Operational event môže byť deployment, config reload alebo leader change. Audit record viaže actor a control-plane action.

```json
{
  "eventType": "PaymentSettlementCompleted",
  "eventId": "evt-991",
  "operationId": "op-884",
  "occurredAt": "2026-07-29T09:18:45Z",
  "ledgerVersion": 842991,
  "providerRequestId": "provider-7781",
  "schemaVersion": 4
}
```

Domain event môže byť súčasť business truth alebo integration contractu; observability event je record pre investigation. Tieto role sa nesmú zamieňať. Log deletion nesmie zmeniť payment state a replay observability eventu nesmie znovu vykonať settlement.

CloudTrail alebo Kubernetes audit record dokazuje accepted control-plane request a actor/session context. Nepreukazuje eventual runtime convergence. Deployment event sa preto koreluje s loaded release/config generation a application outcome.

## Profiles: kde runtime spotreboval resource

Continuous profile agreguje stack samples podľa process, service a cohort identity. Pomáha odlíšiť CPU v JSON serialization od TLS, garbage collection alebo application loopu. Profile nepovie automaticky, ktorý user request zlyhal; spája sa s metrics a traces cez time/release/cohort context.

## Korelácia bez high-cardinality metric labels

Praktický investigation postup:

```text
business completion rate klesne
→ metric určí operation, provider, AZ a release cohort
→ exemplar vyberie representative trace
→ trace lokalizuje failing dependency span
→ trace ID otvorí structured logs
→ config/deployment event vysvetlí recent change
→ audit record identifikuje actor alebo controller
```

Exemplar umožňuje metric sample prepojiť s trace ID bez vloženia každého trace ID do label setu. Tak sa zachová bounded metric cardinality a detailná causal investigation.

## Signal quality a coverage

Evidence quality závisí od semantics, coverage, freshness, sampling, schema compatibility a integrity. Silný signal contract odpovedá:

```text
Kto record produkuje?
Pri akej state transition?
Čo je numerator, denominator alebo sampled population?
Aká identity a schema generation je uložená?
Čo môže byť dropped, delayed alebo redacted?
Ktorý operational decision signal podporuje?
```

Viac detailu nemusí znamenať vyššiu kvalitu. Nekontrolovaný user ID v labels zvýši cost a môže znefunkčniť queries. Full payload logs zvýšia privacy risk. Sto percent tracing môže preťažiť producer alebo backend. Signal design vyberá minimum detailu potrebné na rozhodnutie.

## Worked walkthrough: rovnaký incident cez štyri signals

Pri `OBS-PAY-43` HTTP acceptance ostáva green, ale final completion klesá pre enterprise cohort v `eu-central-1b`.

Metric query najprv lokalizuje cohort:

```promql
sum by (availability_zone, config_generation) (
  rate(payment_settlement_completed_total{
    merchant_class="enterprise",
    result="error"
  }[5m])
)
```

Metric preukáže concentration na `1b/CFG-34`, ale nie mechanizmus. Exemplar otvorí trace, ktorý končí na provider TLS span-e. Trace event uvádza `unknown_ca`; log s rovnakým trace ID pridá loaded config generation. Deployment event ukáže, že config `CFG-35` bol published, ale audit a task inventory dokazujú partial rollout.

Containment odoberie stale cohort z enterprise routing-u. Recovery vytvorí canary s `CFG-35` a overí mTLS, one-settlement business outcome a telemetry producer-to-backend path. Forbidden test spustí task s old trust bundle v isolated environment a očakáva controlled TLS failure bez production trafficu.

Žiadny signal sám neuzatvoril incident. Metric určila rozsah, trace path, log detail a event/audit recent change a actor context.

## Kontrolné otázky

1. Aký detail metric zámerne zahadzuje?
2. Čo structured log preukazuje a čo nepreukazuje?
3. Prečo trace nie je spoľahlivý population counter bez sampling contextu?
4. Aký rozdiel je medzi domain eventom a observability eventom?
5. Prečo audit API success neznamená runtime convergence?
6. Ako exemplar prepája metric a trace bez cardinality explosion?
7. Čo môže znamenať missing span?
8. Prečo p95 histogram nezahŕňa automaticky queue wait?
9. Ako sa signals skombinovali pri `OBS-PAY-43`?
10. Ktoré fields patria do bounded metrics a ktoré do logs/traces?

## Oficiálna dokumentácia

- [Prometheus metric types](https://prometheus.io/docs/concepts/metric_types/)
- [PromQL functions](https://prometheus.io/docs/prometheus/latest/querying/functions/)
- [Grafana Loki LogQL](https://grafana.com/docs/loki/latest/query/)
- [Grafana Tempo TraceQL](https://grafana.com/docs/tempo/latest/traceql/)
- [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [OpenTelemetry logs](https://opentelemetry.io/docs/concepts/signals/logs/)
- [OpenTelemetry metrics](https://opentelemetry.io/docs/concepts/signals/metrics/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Monitoring vs. observability](monitoring-vs-observability.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Instrumentation a telemetry →](instrumentation-telemetry.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
