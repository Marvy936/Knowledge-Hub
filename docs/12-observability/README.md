# Observability

Táto sekcia vysvetľuje, ako navrhovať, zbierať, spracúvať, ukladať a používať telemetry tak, aby bolo možné detegovať problémy, skúmať neznáme failure modes, riadiť SLO a robiť evidence-driven operational decisions.

Cieľom nie je vytvoriť katalóg monitoring produktov. Najprv sa budujú stabilné koncepty: signals, instrumentation, correlation, telemetry pipelines, service/resource monitoring methods, alerting a cardinality. Až potom nasledujú konkrétne platformy ako Prometheus, Alertmanager, Grafana, Loki, OpenSearch, Fluent Bit, Jaeger, Tempo a OpenTelemetry.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md),
- [Kubernetes](../09-kubernetes/README.md),
- [Cloud and AWS](../11-cloud-and-aws/README.md).

## Odporúčané poradie

1. [Monitoring vs. observability](monitoring-vs-observability.md)
2. [Metrics, logs, traces a events](metrics-logs-traces-events.md)
3. [Instrumentation a telemetry](instrumentation-telemetry.md)
4. [RED method](red-method.md)
5. [USE method](use-method.md)
6. [Golden Signals](golden-signals.md)

Nasledujúci blok prejde od metodík ku konkrétnej metrics platforme: Prometheus, Alertmanager a Grafana. Následne sa doplnia logs, traces, OpenTelemetry, alert design a cardinality.

## Cieľ zvládnutia

Po dokončení aktuálneho bloku má byť možné:

- presne rozlíšiť monitoring, observability, telemetry a instrumentation,
- vysvetliť odlišný data model a operational use metrics, logs, traces, events, audit records a profiles,
- vybrať signal podľa otázky a prejsť od agregovaného symptómu ku konkrétnej operácii,
- navrhnúť structured log, metric, trace a event correlation contract,
- vysvetliť counter, gauge, histogram, distribution, temporality a bounded cardinality,
- odlíšiť parent-child spans, span links, span events a samostatné events,
- navrhnúť code-based a zero-code instrumentation bez zamieňania automatic coverage za business observability,
- vysvetliť OpenTelemetry API, SDK, instrumentation scope, resource identity, semantic conventions a context propagation,
- navrhnúť telemetry pipeline cez receiver, processor, batching, sampling, redaction a exporter,
- vyhodnotiť agent, sidecar a gateway Collector deployment trade-offy,
- monitorovať telemetry pipeline cez accepted, dropped, queued a failed records,
- aplikovať RED na HTTP, gRPC, queues a batch workloads,
- definovať request rate, error numerator/denominator a duration distribution bez retry alebo cardinality skreslenia,
- aplikovať USE cez kompletný resource inventory a rozlíšiť utilization, saturation a errors,
- analyzovať CPU, memory, storage, network, pools, containers a cloud quotas podľa správnej enforcement boundary,
- definovať Golden Signals pre konkrétny user journey alebo workload,
- oddeľovať successful a failed latency, logical demand a retry amplification,
- naviazať Golden Signals a RED na SLIs/SLOs a saturation na capacity risk,
- kombinovať Golden Signals, RED, traces, USE, logs a profiles v jednom investigation workflowe,
- diagnostikovať chýbajúcu alebo skreslenú telemetry cez producer, pipeline a backend vrstvy,
- riadiť telemetry overhead, privacy, schema versioning a cost ako production contract.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Monitoring vs. observability | Learning | L2 |
| Metrics, logs, traces a events | Learning | L2 |
| Instrumentation a telemetry | Learning | L2 |
| RED method | Learning | L2 |
| USE method | Learning | L2 |
| Golden Signals | Learning | L2 |
