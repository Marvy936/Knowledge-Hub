# Jaeger a Tempo

Jaeger a Grafana Tempo sú distributed tracing backends. Prijímajú spans, ukladajú trace data a poskytujú lookup, search a visualization nad distributed operations. Backend však vidí iba telemetry, ktorá bola vytvorená, správne propagovaná, zachovaná sampling policy, prijatá ingest pathom a ešte existuje v queryovateľnej storage generation.

Jaeger a Tempo nie sú identické produkty. Jaeger poskytuje vlastný collector/query/storage model a deployment možnosti. Tempo je Grafana Labs tracing backend orientovaný na object storage a TraceQL. Current Tempo deployment modes a dependencies, vrátane Kafka požiadaviek v určitých microservices-mode versions, sa overujú v dokumentácii pre nasadenú release. Architektúra sa nesmie navrhovať podľa staršieho diagramu bez version identity.

## End-to-end trace lifecycle

Trace backend môže vysvetliť distributed operation iba vtedy, keď sa zachová identita a completeness cez celý write a read path. Propagation určí vzťahy medzi spans, sampling rozhodne, ktoré records pokračujú, ingest ich prijme a storage ich až následne sprístupní recent alebo historical query. Úspech jednej boundary preto nie je dôkazom nasledujúcej a lifecycle sa overuje v tomto poradí.

```text
business operation
→ W3C alebo iný propagation context
→ root a child span generation
→ resource a instrumentation-scope identity
→ head alebo tail sampling
→ OTLP/export queue
→ collector alebo backend ingest
→ trace assembly a storage
→ index/search metadata
→ trace lookup alebo TraceQL query
→ causal explanation
→ metric/log correlation a business validation
```

Missing trace nie je automaticky dôkaz, že operation nenastala. Môže byť nesampled, context sa mohol rozpadnúť, spans prišli neskoro, exporter ich zahodil, backend ich odmietol alebo query použila nesprávny tenant/time range.

## Exact trace subject

Atlas používa `TRACE-PAY-43`:

```yaml
logicalOperation: payment.settle
operationId: op-884
traceId: 4bf92f3577b34da6a3ce929d0e0e4736
expectedRoot: payment.settle
expectedPath:
  - http POST /payments/{id}/settle
  - idempotency.claim
  - queue.publish
  - payment.settle.consume
  - provider.authorize
  - ledger.commit
resource:
  service.name: payments-api
  service.version: 7.19.0
  deployment.environment.name: production
  cloud.region: eu-central-1
telemetryGeneration: OTEL-PAY-12
samplingGeneration: TAIL-PAY-6
backendTenant: atlas-production
retention: 14d
```

Trace ID je lookup identity, nie business idempotency key. Retry môže vytvoriť nový trace pre rovnakú operation. Investigation preto viaže trace na stable operation ID a provider/ledger evidence.

## Span model a propagation

Span obsahuje name, start/end, status, attributes, events, links a parent context. Operation graph má reprezentovať causal alebo explicitne linked workflow.

Synchronous HTTP propagation používa trace headers. Async messaging často potrebuje producer span, message context a consumer span alebo link podľa semantics. Ak queue retry vytvorí nový processing attempt, parent-child graph nemusí byť vhodný na vyjadrenie všetkých attempts; links zachovajú vzťah bez falošnej single-chain causality.

Trace context možno overiť synthetic requestom:

```bash
TRACEPARENT='00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01'

curl -fsS -X POST \
  -H "traceparent: $TRACEPARENT" \
  -H 'X-Test-Operation: trace-canary-op-43' \
  https://pay.example.com/internal/trace-canary
```

Príkaz preukazuje odoslanie requestu s validným caller-provided trace contextom. Nepreukazuje, že gateway context zachovala, service ho akceptovala alebo backend trace uložil. Query musí nájsť expected graph a application má podľa trust modelu rozhodnúť, či external trace IDs prijíma alebo vytvára nový root.

## Ingest cez OTLP

Collector exporter:

```yaml
exporters:
  otlp/tempo:
    endpoint: tempo-distributor.observability.svc:4317
    tls:
      insecure: false
      ca_file: /etc/otel/certs/ca.pem
    sending_queue:
      enabled: true
      num_consumers: 8
      queue_size: 20000
    retry_on_failure:
      enabled: true
      initial_interval: 1s
      max_interval: 30s
      max_elapsed_time: 5m

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, tail_sampling/payments, batch]
      exporters: [otlp/tempo]
```

Configuration preukazuje desired endpoint, TLS, queue a retry policy. Nepreukazuje loaded state, certificate trust, tenant header injection ani backend acknowledgement. Collector internal metrics a backend query uzatvárajú ďalšie boundaries.

```bash
curl -fsS http://otel-collector:8888/metrics \
  | grep -E 'otelcol_(receiver_accepted|processor_dropped|exporter_sent|exporter_send_failed)_spans'
```

Counters preukazujú per-hop accounting daného Collector instance. Rozdiel accepted vs sent môže byť queued, sampled, dropped alebo failed podľa processors. Durable trace storage sa overuje backend query.

## Jaeger lookup a API boundary

Jaeger UI/query service umožňuje lookup trace ID a search podľa service/operation/tags podľa storage capabilities. API shape sa viaže na deployed Jaeger version.

```bash
curl -fsS \
  "http://jaeger-query:16686/api/traces/4bf92f3577b34da6a3ce929d0e0e4736" \
  | jq '.data[0] | {traceID, spanCount: (.spans | length), services: [.processes[].serviceName]}'
```

Výstup preukazuje stored trace representation v konkrétnom Jaeger query service. Nepreukazuje completeness, pokiaľ expected graph, late spans a sampling generation nie sú porovnané. Empty data môže znamenať wrong tenant/storage, retention alebo absent sampling.

## Tempo a TraceQL

Tempo lookup:

```bash
curl -fsS \
  -H 'X-Scope-OrgID: atlas-production' \
  "http://tempo-query-frontend:3200/api/traces/4bf92f3577b34da6a3ce929d0e0e4736" \
  | jq '.batches | length'
```

Príkaz preukazuje trace lookup pre exact tenant a query endpoint. Nepreukazuje, že Grafana používa rovnaký tenant alebo že all spans sú present.

TraceQL query:

```traceql
{
  resource.service.name = "provider-adapter" &&
  resource.deployment.environment.name = "production" &&
  span.payment.provider = "provider-a" &&
  status = error
}
| by(resource.cloud.availability_zone)
```

TraceQL preukazuje stored traces/spans matching attributes v selected range. Searchability attributes a query behavior závisia od backend schema/version. Query result nie je population rate bez známého sampling modelu.

Tempo metrics-generator môže odvodiť service graphs alebo span metrics z traces. Derived metric coverage závisí od sampled traces a generator configuration; nesmie byť považovaná za úplný request counter, ak sampling zahadzuje traffic.

## Sampling a trace completeness

Head sampling rozhoduje pred final outcome. Tail sampling umožní zachovať error/slow traces, ale musí dostať všetky relevantné spans v decision window a správnej affinity.

```yaml
processors:
  tail_sampling/payments:
    decision_wait: 20s
    num_traces: 50000
    policies:
      - name: errors
        type: status_code
        status_code:
          status_codes: [ERROR]
      - name: slow-settlements
        type: latency
        latency:
          threshold_ms: 2500
      - name: baseline
        type: probabilistic
        probabilistic:
          sampling_percentage: 5
```

Policy preukazuje intended selection, nie effective completeness. Async operation dlhšia než `decision_wait` môže dostať sampling decision pred neskorými spans. Distributed tail samplers potrebujú trace affinity; inak rôzne spans jednej trace skončia na rôznych samplers.

Sampling metrics musia zahŕňať received traces, decisions, sampled/dropped, policy match, late spans a memory/queue pressure. Security/audit events s requirementom úplnosti sa nesmú spoliehať na probabilistic trace sampling.

## Storage, retention a search

Tempo object-storage model oddeľuje ingest/write path, blocks a query components. Jaeger storage závisí od zvoleného backendu. Trace retention musí pokryť detection a investigation window; object lifecycle kratší než backend retention môže odstrániť blocks predčasne.

Lookup by trace ID a attribute search majú odlišné index/query costs. High-cardinality attributes môžu byť vhodné pre direct trace lookup alebo search scope podľa backend capabilities, ale metrics-generator dimensions musia zostať bounded.

## Correlation s metrics a logs

Exemplar spája Prometheus sample s trace ID. Structured log nesie trace ID a stable operation ID. Investigation tok:

```text
settlement SLO burn
→ metric cohort a exemplar
→ trace graph
→ failing provider span
→ correlated log detail
→ config/deployment event
→ loaded-state inventory
```

Trace nevlastní business truth. Provider a ledger state rozhodujú, či settlement nastal. Trace vysvetľuje execution path a unknown outcome, ale missing span nie je automatický rollback.

## Worked incident: tail sampler zahodí práve problematické traces

Po rollout-e enterprise settlement p99 rastie nad 12 sekúnd, ale Tempo search ukazuje iba healthy short traces. Metrics a logs potvrdzujú `unknown_ca` errors v `eu-central-1b`.

Competing hypotheses sú broken propagation, exporter failure, wrong tenant, TraceQL filter, tail sampler decision, storage/query issue alebo instrumentation gap.

Collector metrics ukážu accepted spans a no exporter failures. Tail-sampling late-span counter rastie. `decision_wait=10s`, zatiaľ čo affected async workflow vytvára provider span po 11–14 sekundách. Sampler rozhodne podľa incomplete healthy-looking prefixu a baseline policy väčšinu traces zahodí; neskorý error span už trace nezachráni.

Containment pridá bounded sampling policy pre enterprise error logs/existing attributes a zachová collector metrics/config. Plošné 100 % tracing je zakázané bez capacity budgetu.

Recovery zvýši decision window na measured workflow duration, overí sampler memory/queue a trace affinity a vytvorí canary. Acceptance vyžaduje complete expected span graph, query by trace ID, TraceQL search, metric exemplar correlation, no forbidden sensitive attributes a bounded sampler drops. Forbidden test odošle 30-sekundový trace nad supported decision budget a musí vytvoriť explicitný incomplete/late-span signal, nie silent absence.

## Kontrolné otázky

1. Prečo missing trace nepreukazuje, že operation nenastala?
2. Aký rozdiel je medzi trace ID a business operation ID?
3. Kedy používaš span link namiesto parent-child vzťahu?
4. Čo OTLP exporter metrics preukazujú a čo nie?
5. Ako sa líši Jaeger trace lookup a Tempo TraceQL search?
6. Prečo derived span metrics nemusia reprezentovať plnú population?
7. Aké dependencies má tail sampling?
8. Ako object-store lifecycle môže porušiť trace retention?
9. Prečo sampler zahodil problematické traces?
10. Aké evidence uzatvára trace-pipeline recovery?

## Oficiálna dokumentácia

- [Jaeger documentation](https://www.jaegertracing.io/docs/)
- [Grafana Tempo documentation](https://grafana.com/docs/tempo/latest/)
- [TraceQL](https://grafana.com/docs/tempo/latest/traceql/)
- [Tempo architecture](https://grafana.com/docs/tempo/latest/introduction/architecture/)
- [OpenTelemetry sampling](https://opentelemetry.io/docs/concepts/sampling/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Fluent Bit](fluent-bit.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OpenTelemetry →](opentelemetry.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
