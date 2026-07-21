# Observability

Táto sekcia vysvetľuje, ako navrhovať, zbierať, spracúvať, ukladať a používať telemetry tak, aby bolo možné detegovať problémy, skúmať neznáme failure modes, riadiť SLO a robiť evidence-driven operational decisions.

Cieľom nie je vytvoriť katalóg monitoring produktov. Najprv sa budujú stabilné koncepty: signals, instrumentation, correlation, telemetry pipelines, alerting, cardinality a service-oriented methods. Až potom nasledujú konkrétne platformy ako Prometheus, Grafana, Loki, OpenSearch, Fluent Bit, Jaeger, Tempo a OpenTelemetry.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md),
- [Kubernetes](../09-kubernetes/README.md),
- [Cloud and AWS](../11-cloud-and-aws/README.md).

## Odporúčané poradie

1. [Monitoring vs. observability](monitoring-vs-observability.md)

Nasledujúci blok rozšíri základ o metrics, logs, traces, events, instrumentation, RED, USE a Golden Signals.

## Cieľ zvládnutia

Po dokončení aktuálneho článku má byť možné:

- presne rozlíšiť monitoring, observability, telemetry a instrumentation,
- vysvetliť úlohu metrics, logs, traces, events, audit records a profiles,
- navrhnúť correlation a context-propagation model,
- rozlíšiť white-box a black-box monitoring,
- naviazať telemetry na SLO a user outcomes,
- vyhodnotiť cardinality, sampling, retention, cost a privacy trade-offy,
- diagnostikovať chýbajúce signals cez celý telemetry pipeline,
- rozpoznať anti-patterny ako logovanie všetkého, dashboard inventory a alert fatigue.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Monitoring vs. observability | Learning | L2 |
