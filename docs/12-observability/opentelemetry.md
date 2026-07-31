# OpenTelemetry

OpenTelemetry je vendor-neutral specification, API/SDK ecosystem, protocol a Collector framework pre vytváranie, propagovanie, spracovanie a export telemetry. Nie je to observability backend ani hotová monitoring stratégia. Úspech sa neposudzuje podľa toho, či Collector beží, ale podľa toho, či exact signal contract prejde od application occurrence až po správny backend outcome bez neviditeľnej straty, schema driftu alebo privacy porušenia.

OpenTelemetry oddeľuje instrumentation od backendu, nie zodpovednosť za semantics. Tím stále musí definovať business operation, metric population, span boundaries, log schema, sampling, redaction, resource identity a loaded-state acceptance.

## End-to-end signal lifecycle

OpenTelemetry oddeľuje producer API, runtime SDK policy, transport a Collector processing, preto žiadny z týchto komponentov sám nepreukazuje end-to-end evidence. Signal musí zachovať operation semantics, resource identity a schema cez každú boundary a backend musí výsledok sprístupniť query. Lifecycle sa preto overuje v nasledujúcom poradí a pri každom kroku sa rozlišuje configured, loaded, accepted a queryable state.

```text
business alebo operational otázka
→ exact signal requirement a schema generation
→ manual, library alebo zero-code instrumentation
→ API a SDK runtime policy
→ resource, instrumentation scope a context
→ signal-specific processing
→ OTLP serialization a transport
→ Collector receiver/processors/exporters
→ backend ingest a query
→ dashboard, rule alebo investigation
→ coverage, privacy, overhead a failure validation
```

OpenTelemetry API calls bez configured SDK/provider môžu byť no-op podľa language/runtime. Configured SDK bez exporter endpointu môže records bufferovať alebo zahadzovať. OTLP success preukazuje receiver acknowledgement, nie automaticky durable backend queryability.

## Exact OTel subject

Atlas používa:

```yaml
subject: OTEL-PAY-12
service.name: payments-api
service.namespace: atlas-payments
service.version: 7.19.0
deployment.environment.name: production
cloud.region: eu-central-1
schema.url: atlas-observability/12
instrumentationScopes:
  - atlas.payments.settlement@12.0.0
  - opentelemetry.instrumentation.http@current-approved
collectorConfig: OTELCOL-PAY-19
samplingPolicy: TAIL-PAY-6
redactionPolicy: PII-RED-8
metricsBackend: prometheus-compatible production
logsBackend: loki atlas-production
tracesBackend: tempo atlas-production
```

Resource attributes identifikujú entity, ktorá telemetry produkuje. Instrumentation scope identifikuje library/component, ktorý signal vytvoril. Span/metric/log fields opisujú operation alebo event. `service.name` sa nesmie meniť podľa Pod alebo hostname; ephemeral identity patrí do `service.instance.id` alebo platform attributes podľa semantic conventions.

Current semantic conventions sú versionované a jednotlivé convention groups môžu mať rôzny stability status. Upgrade instrumentation package preto potrebuje schema diff a consumer compatibility test, nie iba dependency update.

## Tracer, Meter a Logger provider

Python trace a metric example:

```python
from opentelemetry import metrics, trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer("atlas.payments.settlement", "12.0.0")
meter = metrics.get_meter("atlas.payments.settlement", "12.0.0")

started = meter.create_counter(
    "payment.settlement.started",
    unit="{operation}",
    description="Logical settlement operations admitted after idempotency claim",
)
completed = meter.create_counter(
    "payment.settlement.completed",
    unit="{operation}",
    description="Terminal logical settlement outcomes",
)
duration = meter.create_histogram(
    "payment.settlement.duration",
    unit="s",
    description="End-to-end logical settlement duration",
)


def settle(operation_id: str, provider: str) -> None:
    attributes = {
        "payment.provider": provider,
        "payment.merchant.class": "enterprise",
    }
    started.add(1, attributes)
    with tracer.start_as_current_span("payment.settle", attributes=attributes) as span:
        start = monotonic_seconds()
        try:
            claim_idempotency(operation_id)
            authorize_provider(operation_id, provider)
            commit_ledger(operation_id)
            completed.add(1, {**attributes, "payment.result": "success"})
            span.add_event("payment.settlement.completed")
        except Exception as exc:
            completed.add(1, {**attributes, "payment.result": "terminal_error"})
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise
        finally:
            duration.record(monotonic_seconds() - start, attributes)
```

Code preukazuje intended instrument definitions a increment boundaries. Nepreukazuje, že `operation_id` je atomically claimed, metric temporality/backend translation je compatible alebo exceptions sú terminal rather than retryable. Metric attribute values musia zostať bounded; operation ID sa nepridáva do metrics.

Log correlation môže pridať trace/span IDs do structured log recordu cez language logging bridge. Log message stále potrebuje schema a redaction; trace context samo nedáva logu business meaning.

## Context propagation

OpenTelemetry propagators prenášajú context cez HTTP headers, message metadata alebo iné carriers. W3C Trace Context je bežný default. Baggage prenáša application context, ale môže sa šíriť cez mnoho trust boundaries a nesmie obsahovať secrets.

```python
from opentelemetry.propagate import inject, extract

headers: dict[str, str] = {}
inject(headers)
queue.publish(body=payload, headers=headers)

consumer_context = extract(message.headers)
with tracer.start_as_current_span(
    "payment.settle.consume",
    context=consumer_context,
):
    process(message)
```

Príklad preukazuje intended inject/extract code. Controlled broker test musí overiť, že headers sa zachovajú pri retry, dead-letter a replayi. Blind trust external `traceparent` môže umožniť collision alebo sampling influence podľa threat modelu; ingress môže vytvoriť nový root a pôvodný context uložiť ako link.

## OTLP transport

OTLP môže používať gRPC alebo HTTP/protobuf podľa SDK/Collector/backend supportu. Endpoint, TLS, compression, headers, timeout a retry sú súčasťou signal pathu.

Environment configuration example:

```bash
export OTEL_SERVICE_NAME=payments-api
export OTEL_RESOURCE_ATTRIBUTES='service.namespace=atlas-payments,deployment.environment.name=production,cloud.region=eu-central-1'
export OTEL_EXPORTER_OTLP_ENDPOINT='https://otel-gateway.observability.svc:4317'
export OTEL_EXPORTER_OTLP_CERTIFICATE='/etc/otel/certs/ca.pem'
export OTEL_TRACES_SAMPLER='parentbased_traceidratio'
export OTEL_TRACES_SAMPLER_ARG='0.10'
```

Environment variables preukazujú intended process inputs. Nepreukazujú, že runtime library ich podporuje alebo načítala; effective loaded state sa publikuje bezpečným generation fieldom a overuje canary.

Network handshake:

```bash
openssl s_client \
  -connect otel-gateway.observability.svc:4317 \
  -servername otel-gateway.observability.svc \
  -CAfile /etc/otel/certs/ca.pem \
  -brief </dev/null
```

TLS success lokalizuje transport/trust boundary. Nepreukazuje OTLP protocol, authorization headers alebo signal acceptance.

## Collector pipelines

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
    limit_mib: 1024
    spike_limit_mib: 256
  resource/normalize:
    attributes:
      - key: deployment.environment.name
        value: production
        action: upsert
  attributes/redact:
    actions:
      - key: http.request.header.authorization
        action: delete
      - key: payment.card_number
        action: delete
  tail_sampling/payments:
    decision_wait: 20s
    policies:
      - name: errors
        type: status_code
        status_code:
          status_codes: [ERROR]
      - name: baseline
        type: probabilistic
        probabilistic:
          sampling_percentage: 5
  batch:
    timeout: 5s
    send_batch_size: 2048

exporters:
  otlp/tempo:
    endpoint: tempo-distributor:4317
    tls:
      insecure: false
  otlphttp/loki:
    endpoint: https://loki-gateway/otlp
  prometheus:
    endpoint: 0.0.0.0:9464

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, resource/normalize, attributes/redact, tail_sampling/payments, batch]
      exporters: [otlp/tempo]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, resource/normalize, attributes/redact, batch]
      exporters: [otlphttp/loki]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, resource/normalize, batch]
      exporters: [prometheus]
```

Processor order je executable policy. Redaction pred exportom chráni all configured backends. Tail sampling patrí iba do traces pipeline. Resource upsert môže maskovať producer environment drift; pre security-relevant identity môže byť safer validate/reject než overwrite.

```bash
otelcol-contrib --config=/etc/otelcol/config.yaml --dry-run

curl -fsS http://otel-collector:8888/metrics \
  | grep -E 'otelcol_(receiver_accepted|processor_refused|processor_dropped|exporter_sent|exporter_send_failed)'
```

Dry run preukazuje config parse/component initialization. Internal metrics poskytujú hop accounting. Backend query a end-to-end canary sú stále required.

## Metric temporality a translation

OTel metrics podporujú instruments a aggregation/temporality model. Exporter/backend môže prekladať names, units, histogram representation a temporality. Counter reset, delta-to-cumulative conversion alebo duplicate collectors môžu skresliť Prometheus rates.

Migration gate porovnáva:

```text
instrument name/type/unit
→ attributes a bounded values
→ aggregation a temporality
→ exporter translation
→ backend series names/labels
→ recording rules a dashboards
```

Producer unit `ms` a dashboard assumption `s` vytvoria 1000× error bez transport failure. Semantic contract test posiela known histogram samples a overuje backend values/units.

## Sampling

Head sampler rozhodne pred final outcome. Parent-based behavior rešpektuje upstream sampling decision podľa configuration. Tail sampling umožní outcome-aware policy, ale pridáva buffering, decision wait a trace-affinity requirements.

Sampling affects traces, not automatically metrics/logs. Span-derived metrics inherit sampled population unless metrics-generator has another source. Audit alebo billing truth nesmie byť probabilistically sampled.

## Zero-code instrumentation

Java agent, Python auto-instrumentation, .NET auto-instrumentation a Kubernetes/operator injection môžu pridať telemetry bez ručného code change-u. Zero-code stále mení process startup, class/module hooks, resource attributes a exporter behavior. Loaded-agent inventory je potrebný.

```bash
ps -ef | grep -E 'opentelemetry|javaagent' | grep -v grep

tr '\0' '\n' < /proc/1/environ | grep '^OTEL_'
```

Commands preukazujú process args/environment v danom containeri, nie úspešné hooks alebo telemetry export. Synthetic request a backend query overia actual instrumentation.

## Schema, attributes a privacy

Semantic conventions znižujú pomenovacie rozdiely, ale custom domain attributes potrebujú namespace, ownera, type a stability. Attribute rename môže rozbiť tail policy, dashboard aj routing naraz.

Cardinality a data classification sa kontrolujú pred emission. Raw HTTP URL s IDs, database statement s secrets alebo user email môžu unikať. Collector redaction je druhá defense; producer minimization je prvá.

Forbidden-field canary odošle synthetic fingerprint a vyhľadá ho vo všetkých backends. Acceptance znamená, že expected safe fields existujú a forbidden value nikde nie je queryable.

## Worked incident: Collector upgrade zmení metric identity

Po upgrade Collector/exporter generation `OTELCOL-PAY-19` zmizne Grafana settlement duration panel, hoci traces a logs sú zdravé. Prometheus targets sú up.

Competing hypotheses sú producer metric absence, Collector metrics pipeline failure, exporter translation rename, unit/temporality change, scrape relabel drop alebo dashboard query drift.

Producer debug output obsahuje `payment.settlement.duration` v sekundách. Collector internal metrics ukazujú accepted/sent metric points. Prometheus exposition však obsahuje premenovanú translated series a histogram representation, zatiaľ čo recording rule stále očakáva staré `_bucket` series. Transport je healthy; consumer compatibility sa rozbila.

Containment ponechá business completion counter alert a zastaví upgrade rollout. Recovery pinne approved exporter behavior alebo migruje recording rules cez dual-publish/shadow period. Schema contract test overí name, type, unit, labels, buckets/native histogram a query result.

Acceptance vyžaduje producer record, Collector accounting, Prometheus series, recording rule, Grafana panel a alert canary. Forbidden test odošle high-cardinality payment ID attribute do metric a deployment gate ho musí odmietnuť alebo odstrániť pred exportom.

## Kontrolné otázky

1. Prečo OpenTelemetry nie je observability backend?
2. Aký rozdiel je medzi resource a instrumentation scope?
3. Čo API instrumentation code preukazuje a čo nie?
4. Ako sa overuje propagation cez queue retry/replay?
5. Čo TLS test nepreukazuje o OTLP?
6. Prečo processor order mení security a reliability?
7. Ako exporter translation môže rozbiť Prometheus rules?
8. Prečo span-derived metrics nemusia byť úplná population?
9. Čo loaded-agent commands nepreukazujú?
10. Aké evidence uzatvára metric-translation incident?

## Oficiálna dokumentácia

- [OpenTelemetry specification](https://opentelemetry.io/docs/specs/otel/)
- [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
- [OTLP specification](https://opentelemetry.io/docs/specs/otlp/)
- [Collector configuration](https://opentelemetry.io/docs/collector/configuration/)
- [OpenTelemetry sampling](https://opentelemetry.io/docs/concepts/sampling/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Jaeger a Tempo](jaeger-tempo.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Alert design a alert fatigue →](alert-design-alert-fatigue.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
