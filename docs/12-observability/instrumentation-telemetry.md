# Instrumentation a telemetry

Instrumentation je production mechanismus, ktorý rozhoduje, ktoré system occurrences sa zmenia na telemetry records, s akou identitou, semantics a failure behavior. Telemetry je výsledok tohto mechanismu a následného delivery, processing a storage lifecycle-u. Collector ani backend nedokážu spätne doplniť business meaning, ktorý producer nikdy nevytvoril.

Instrumentation sa preto navrhuje od business questions a failure boundaries smerom k observation points. Nie od zoznamu dostupných agentov smerom k náhodným dátam.

## End-to-end lifecycle

Instrumentation sa správa ako versionovaný production data path, nie ako jednorazové pridanie SDK. Každá transition mení, čo responder môže z výsledku usúdiť: producer môže record vytvoriť, processor ho transformovať, exporter potvrdiť transport a backend ho až následne sprístupniť query. Preto sa celý mechanizmus číta v nasledujúcom poradí a každá boundary má samostatný read-back.

```text
business outcome a investigation otázky
→ exact operation a failure-boundary inventory
→ telemetry requirements a authority
→ manual, automatic a platform instrumentation
→ resource, scope, operation a context identity
→ local SDK alebo agent processing
→ Collector receiver, processors a routing
→ sampling, filtering, redaction a enrichment
→ export, acknowledgement a retry
→ backend ingest, storage a query
→ coverage, overhead, privacy a loaded-state validation
→ rollout, rollback a retirement
```

Configured instrumentation nie je automaticky loaded. Emitted record nie je automaticky accepted, durable ani queryable. Každá transition potrebuje observation point a accounting.

## Exact instrumentation subject

Atlas používa generation `OTEL-PAY-12` pre settlement workflow:

```yaml
service.name: payments-api
service.version: 7.19.0
deployment.environment.name: production
cloud.region: eu-central-1
telemetry.sdk.name: opentelemetry
telemetry.schema: atlas-payments-12
collector.pipeline: otlp-payments-v9
sampling.policy: tail-payments-v6
redaction.policy: pii-redaction-v8
```

OpenTelemetry resource opisuje entity, ktorá telemetry produkuje. Instrumentation scope identifikuje knižnicu alebo component, ktorý record vytvoril. Span alebo metric operation identity opisuje pozorovaný work. Tieto vrstvy sa nemajú zlievať do jedného voľného `service` labelu.

Aktuálne OpenTelemetry semantic conventions poskytujú spoločné názvy a významy pre resources, spans, metrics, events a attributes. Ich stability sa môže líšiť podľa convention groupu, preto schema generation a migration musia byť explicitné. Producer upgrade nesmie potichu premenovať HTTP attributes a rozbiť dashboards alebo sampling policies.

## Manual, automatic a platform instrumentation

Manual instrumentation pridáva business state transitions, ktoré generic library nepozná. Automatic instrumentation zachytáva podporované frameworky a dependencies bez ručného zásahu do každého call-site. Platform telemetry opisuje runtime, orchestrator, load balancer alebo database behavior.

Pre settlement operation potrebuje application explicitný business span:

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer("atlas.payments.settlement", "12.0.0")


def settle_payment(operation_id: str, provider: str) -> None:
    with tracer.start_as_current_span("payment.settle") as span:
        span.set_attribute("payment.provider", provider)
        span.set_attribute("payment.operation.class", "enterprise")
        span.set_attribute("payment.operation.id", operation_id)
        try:
            claim_idempotency(operation_id)
            call_provider(operation_id, provider)
            commit_ledger(operation_id)
            span.add_event("payment.settlement.completed")
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise
```

Tento kód preukazuje intended span name, attributes a event generation. Neznamená, že SDK provider/exporter je configured, context prejde cez queue, record dorazí do Collectora alebo tail sampler trace zachová. `payment.operation.id` je high-cardinality a citlivý field; patrí do protected trace contextu iba podľa data policy, nie do metric dimensions.

Automatic HTTP alebo database instrumentation môže vytvoriť child spans, ale nedokáže sama určiť final business success. Platform metrics zase môžu ukázať healthy Pod a zároveň chýbajúci provider span. Signals sa dopĺňajú.

## Context propagation

Synchronous HTTP používa trace context headers. Async messaging potrebuje inject/extract alebo span links podľa message a processing semantics.

```python
from opentelemetry.propagate import inject, extract

headers: dict[str, str] = {}
inject(headers)
queue.publish(payload, headers=headers)

# consumer
context = extract(message.headers)
with tracer.start_as_current_span(
    "payment.settle.consume",
    context=context,
):
    process(message)
```

Táto ukážka preukazuje intended propagation code path. Nepreukazuje, že broker zachoval headers alebo že retry a dead-letter replay používajú správny parent/link model. Controlled message test musí porovnať producer a consumer trace IDs a ordering semantics.

Baggage nie je miesto pre secrets ani nekontrolované user identifiers. Baggage sa môže propagovať cez mnoho services a exporterov; jeho privacy a size budget musí byť prísnejší než pri lokálnom log field-e.

## Collector pipeline ako executable policy

OpenTelemetry Collector config explicitne spája receivers, processors, exporters a pipelines:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
    spike_limit_mib: 128
  attributes/redact:
    actions:
      - key: http.request.header.authorization
        action: delete
      - key: payment.card_number
        action: delete
  batch:
    send_batch_size: 2048
    timeout: 5s

exporters:
  otlp/tempo:
    endpoint: tempo-distributor:4317
    tls:
      insecure: true
  prometheus:
    endpoint: 0.0.0.0:9464

service:
  pipelines:
    traces/payments:
      receivers: [otlp]
      processors: [memory_limiter, attributes/redact, batch]
      exporters: [otlp/tempo]
    metrics/payments:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus]
```

Configuration file preukazuje desired processor order a routing. Nepreukazuje, že exact file je loaded, exporter endpoint je reachable alebo data policy pokrýva nested payloads. Collector sa spúšťa s explicitným config pathom a kontroluje sa effective process generation:

```bash
otelcol-contrib --config=/etc/otelcol/config.yaml --dry-run

curl -fsS http://otel-collector:13133/

curl -fsS http://otel-collector:8888/metrics \
  | grep -E 'otelcol_(receiver_accepted|processor_refused|exporter_sent|exporter_send_failed)'
```

Dry-run preukazuje parse a component configuration compatibility, nie runtime connectivity. Health endpoint preukazuje process health podľa extension contractu, nie signal delivery. Internal metrics poskytujú per-hop accounting, ale durable backend ingest stále vyžaduje backend query alebo canary.

Processor order je významný. Redaction po exporterovi je nemožná a sampling pred error classification môže odstrániť traces potrebné pre incident. Memory limiter musí byť navrhnutý spolu s queue/batch behaviorom, inak Collector pri pressure odmietne data alebo ho runtime ukončí.

## Sampling ako population transformácia

Head sampling rozhoduje pri začiatku trace a je lacné, ale ešte nepozná final outcome. Tail sampling čaká na spans a môže zachovať errors alebo high latency, no potrebuje trace affinity, buffer capacity a decision latency.

Tail policy príklad:

```yaml
processors:
  tail_sampling/payments:
    decision_wait: 10s
    num_traces: 50000
    expected_new_traces_per_sec: 3000
    policies:
      - name: keep-errors
        type: status_code
        status_code:
          status_codes: [ERROR]
      - name: keep-slow-settlements
        type: latency
        latency:
          threshold_ms: 2500
      - name: baseline
        type: probabilistic
        probabilistic:
          sampling_percentage: 5
```

Táto policy preukazuje intended selection rules. Nepreukazuje, že všetky spans jednej trace prichádzajú do rovnakého sampler shard-u, že `decision_wait` pokryje async duration alebo že `num_traces` zvládne burst. Sampling evidence musí obsahovať received, sampled, dropped a late-span accounting.

Sampling nie je vhodný pre low-volume security audit alebo billing truth, kde každý event môže byť významný. Metrics môžu poskytovať population count a sampled traces detail.

## Cardinality, privacy a overhead

Instrumentation budget obsahuje CPU, allocations, network, record size, attribute count, active series, log volume a trace storage. Overhead sa meria na representative workload-e, nie iba idle benchmarkom.

Forbidden dimensions pre metrics zahŕňajú payment ID, trace ID, raw URL s dynamic path segmentom a customer email. HTTP route template je bounded; raw path `/payments/884` nie. Collector filter môže zabrániť exportu, ale najbezpečnejšie je citlivý field nevytvoriť.

Redaction test odošle synthetic token a následne vyhľadá jeho fingerprint v Collector debug outpute, backendu a export capture. Dashboard hiding nie je redaction.

## Loaded-state a rollout validation

Instrumentation rollout môže vytvoriť mixed population: staré Pods používajú schema 11, nové schema 12 a časť JVM procesov zero-code agent nenačítala. Deployment success preto nepreukazuje telemetry adoption.

Praktický inventory query môže použiť metric emitovanú každým processom:

```promql
count by (service_version, telemetry_schema, availability_zone) (
  otel_instrumentation_info{
    service_name="payments-api",
    environment="production"
  }
)
```

Query preukazuje active time series v backendu pre observed processes. Neprítomný process môže znamenať missing instrumentation alebo chýbajúci scrape/export. Porovnáva sa s authoritative workload inventory z Kubernetes/ECS.

Rollout gate vykoná multi-signal canary:

```bash
curl -fsS -X POST \
  -H 'X-Test-Operation: telemetry-canary-43' \
  https://pay.example.com/internal/telemetry-canary
```

Po requeste sa overí metric increment, trace graph, structured log, Collector hop accounting a backend query. Príkaz preukazuje iba odoslanie synthetic requestu; acceptance vznikne až koreláciou všetkých očakávaných records a absenciou forbidden sensitive fields.

## Worked failure: Collector je healthy, traces chýbajú

Po rollout-e `OTEL-PAY-12` sú application metrics a logs dostupné, no enterprise settlement traces z `eu-central-1b` chýbajú. Collector health endpoint je green.

Competing hypotheses zahŕňajú absent SDK exporter, context propagation failure, receiver route mismatch, tail-sampling drop, exporter authentication, Tempo ingest failure a query time/tenant error. Responder zachová exact Collector config, process args, internal metrics a synthetic trace ID.

Producer debug endpoint preukáže span creation. Collector metrics ukážu accepted spans, ale `otelcol_processor_tail_sampling_late_span_age` a dropped trace count rastú. Async provider call trvá často 14 sekúnd, zatiaľ čo `decision_wait` je 10 sekúnd; spans prichádzajú po sampling decision. Health endpoint bol správne green, pretože process fungoval. Coverage contract bol nesprávny.

Containment ponechá metrics/logs a dočasne zvýši baseline sampling iba pre bounded enterprise cohort. Recovery nastaví decision window podľa measured async pathu, overí sampler memory capacity a trace affinity a nasadí canary. Acceptance vyžaduje complete trace graph, bounded drop rate, no sensitive attributes, stable Collector memory a successful backend query. Forbidden test odošle token fingerprint a musí potvrdiť redaction.

## Kontrolné otázky

1. Prečo Collector nevie doplniť business semantics, ktoré producer nevytvoril?
2. Aký rozdiel je medzi resource a instrumentation scope identity?
3. Čo manual instrumentation pridáva nad automatic HTTP spans?
4. Čo propagation code preukazuje a čo treba testovať na brokerri?
5. Prečo Collector health endpoint nepreukazuje signal delivery?
6. Ako processor order mení privacy a reliability?
7. Aký rozdiel je medzi head a tail samplingom?
8. Prečo loaded-state query treba porovnať s workload inventory?
9. Čo musí obsahovať multi-signal canary?
10. Prečo `decision_wait=10s` rozbilo async traces?

## Oficiálna dokumentácia

- [OpenTelemetry overview](https://opentelemetry.io/docs/specs/otel/overview/)
- [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
- [OpenTelemetry Collector configuration](https://opentelemetry.io/docs/collector/configuration/)
- [OpenTelemetry sampling](https://opentelemetry.io/docs/concepts/sampling/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Metrics, logs, traces a events](metrics-logs-traces-events.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: RED method →](red-method.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
