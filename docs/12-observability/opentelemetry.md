# OpenTelemetry

OpenTelemetry je vendor-neutral specification, API/SDK ecosystem, protocol a Collector framework pre vytváranie, propagovanie, spracovanie a export telemetry. Nie je to observability backend ani hotová monitoring stratégia. Jeho úspech sa neposudzuje podľa toho, či Collector beží, ale podľa toho, či exact signal contract prejde od application occurrence až po správny backend outcome bez neviditeľnej straty, schema driftu alebo privacy porušenia.

## 1. Dominantný mentálny model

```text
business/operational otázka a signal requirement
→ exact telemetry subject a schema generation
→ API alebo zero-code instrumentation
→ SDK runtime policy
→ resource, scope a context identity
→ signal record
→ OTLP transport
→ Collector receiver
→ ordered processors
→ sampling, filtering, redaction a enrichment
→ exporter queue/retry
→ backend acknowledgement
→ backend query/read-back
→ coverage, correctness, cost a privacy verdict
→ rollout, rollback a contract retirement
```

Kritické rozlíšenie:

```text
OpenTelemetry je nakonfigurované
≠ SDK alebo agent je načítaný
≠ record vznikol
≠ Collector ho prijal
≠ processor ho zachoval správne
≠ exporter ho doručil
≠ backend ho interpretuje podľa rovnakého contractu
```

## 2. Exact OpenTelemetry subject

Pri change alebo incidente zaznamenaj:

```text
OTel subject ID:
Business capability a expected signals:
Application/release/cohort:
Language SDK alebo auto-instrumentation version:
API/SDK/config generation:
Semantic-convention/schema generation:
Resource-detector a precedence generation:
Propagation format:
Sampling generation:
Agent/gateway topology:
Collector distribution/image/component inventory:
Collector config generation a processor order:
Exporter/backend/tenant:
Observation window a evidence cut-off:
```

„Používame OTel“ nie je sufficient identity. Core, contrib, Kubernetes, vendor alebo custom Collector distributions nemusia obsahovať rovnaké components ani rovnakú stability úroveň.

## 3. API, SDK a zero-code instrumentation

### API

Application a libraries používajú API na vytváranie spans, metric measurements, log records a context operations. Reusable library nemá vnucovať konkrétny exporter alebo backend.

### SDK

SDK realizuje runtime policy:

- sampling;
- span/log processors;
- metric readers, views, aggregation a temporality;
- batching a queues;
- resource configuration;
- exporters, limits a shutdown/flush.

### Zero-code alebo automatic instrumentation

Agent alebo operator môže instrumentovať framework bez ručných code changes. To zrýchľuje coverage, ale nevytvára automaticky business outcomes, správne span status semantics ani stabilnú cardinality.

Manual a automatic instrumentation môžu koexistovať, ale ownership musí zabrániť duplicate spans a metrics.

## 4. Signal maturity nie je jednotná

OpenTelemetry podporuje traces, metrics a logs; events sú pomenovaný log model a profiles sa ďalej rozvíjajú.

Aktuálne dôležité stability rozlíšenia:

- metrics data model je Stable;
- logs data model, Logs API a Logs SDK sú Stable okrem explicitných výnimiek;
- Profiles specification je Alpha;
- Collector ako celok má mixed status, pretože jednotlivé receivers, processors, exporters a extensions majú vlastnú stability;
- semantic conventions a telemetry-producing instrumentations môžu mať odlišný stability status.

Production contract musí pinovať konkrétny component a jeho signal-specific stability, nie iba verziu Collector binary.

## 5. Resource, instrumentation scope a schema identity

### Resource

Resource opisuje entitu, ktorá telemetry vytvorila. Stabilná logical identity:

```text
service.name = provider-adapter
```

Ephemeral identity:

```text
service.instance.id = pod/provider-adapter-7d9...
```

Pod name nesmie nahradiť logical service name. Resource detectors z environmentu, cloudu, Kubernetes a explicitnej konfigurácie potrebujú definovanú precedence.

### Instrumentation scope

Scope identifikuje library/component a version, ktorá record vytvorila. Pomáha odlíšiť application instrumentation, framework instrumentation a problematickú library generation.

### Semantic conventions

Semantic conventions zjednocujú names, units a meanings. Upgrade môže premenovať attribute, zmeniť unit alebo status a tým poškodiť dashboards, rules, sampling a backend mappings.

Schema migration potrebuje compatibility window, fixture tests a consumer inventory.

## 6. Context propagation a baggage

W3C Trace Context typicky používa `traceparent` a `tracestate`. Injection a extraction musia fungovať cez HTTP, gRPC, queues, messaging a async boundaries.

Baggage prenáša contextual fields, ale nie je bezplatný ani dôveryhodný automaticky. Potrebuje:

- allowlist;
- size limit;
- trust-boundary policy;
- zákaz secrets a PII;
- zákaz automatickej promotion do metric labels;
- lifecycle pre stale values.

Broken propagation vytvára nové roots, neúplné traces a nekonzistentné sampling decisions.

## 7. OTLP contract

OTLP/gRPC a OTLP/HTTP sú odlišné transports. Explicitne definuj:

- endpoint a signal path;
- protocol;
- TLS/mTLS a CA/SNI;
- authentication/tenant headers;
- compression a message-size limit;
- timeout, batching a retry;
- acknowledgement semantics.

TCP connect alebo Collector `/health` nepreukazuje správny OTLP signal path.

## 8. Collector pipeline a processor order

Collector pipeline:

```text
receiver
→ ordered processors
→ exporter
```

Relevantné processors:

- memory limiter;
- batch;
- resource/attributes;
- filter/transform;
- redaction;
- probabilistic alebo tail sampling;
- routing podľa dostupnej distribution.

Order je behavior:

```text
normalize identity
→ redact sensitive fields
→ enforce bounded dimensions
→ sample/filter
→ batch/export
```

Ak redaction nastane po fan-out-e, data už odišli. Ak filter pred normalization očakáva nový attribute name, môže ticho zachovať alebo zahodiť nesprávnu population.

## 9. Agent a gateway topology

```text
applications
→ agent/DaemonSet/sidecar Collectors
→ gateway Collectors
→ backends
```

Agent rieši local endpoint, file/host collection, krátky buffer a resource enrichment. Gateway rieši shared policy, tenant routing, tail sampling, centralized credentials a backend fan-out.

Gateway je shared failure domain. Potrebuje:

- HA a topology spread;
- capacity a autoscaling model;
- bounded queues;
- independent exporter failure handling;
- config-generation rollout;
- end-to-end canary.

Cluster-level receiver, ktorý má bežať raz, nesmie byť omylom nasadený na každom Node-e.

## 10. Sampling a trace affinity

Head sampling je lacné, ale nepozná final outcome. Tail sampling môže zachovať errors a high-latency traces, ale potrebuje všetky spans trace-u na jednej stateful sampling identity.

```text
trace ID
→ deterministic routing/partition
→ jeden active tail-sampling subject
→ wait a completeness decision
→ keep/drop reason
```

Random load balancing pred tail samplers vytvára partial trace populations. Healthy replicas potom robia správne rozhodnutia nad nesprávnymi subjectmi.

Sampling policy musí publikovať effective keep rate, drops podľa reason, late spans, incomplete traces a impact na trace-derived metrics.

## 11. Metrics, logs a backend mapping

### Metrics

Views riadia aggregation, buckets, names a povolené attributes. Pri Prometheus integrácii over:

- cumulative/delta temporality;
- counter reset semantics;
- histogram type a bucket compatibility;
- units a naming;
- resource-to-label allowlist;
- staleness a target identity.

Všetky resource attributes nesmú byť automaticky metric labels.

### Logs

OTel logs môžu prísť cez application bridge, OTLP, filelog, syslog alebo Fluent Bit. File collection potrebuje persistent checkpoint state, multiline, timestamp, severity mapping a redaction.

### Fan-out

Jeden input môže smerovať do viacerých backends. Každý output potrebuje vlastnú queue, acknowledgement, privacy a termination criteria. Pomalý alebo permanentne chybný exporter nemá blokovať všetky paths.

## 12. Delivery, queues a failure semantics

Memory limiter chráni process, ale jeho aktivácia môže odmietať telemetry. Batch znižuje overhead, ale pridáva loss/latency window. Sending queue absorbuje iba bounded outage.

Collector nie je automaticky durable broker.

Pre kritický pipeline definuj:

```text
queue type a capacity
oldest-item age
retry/backoff limit
persistent storage generation
full-disk behavior
shutdown drain
unknown acknowledgement policy
duplicate tolerance
maximum accepted loss window
```

Audit/security telemetry môže potrebovať oddelený durable pipeline od best-effort traces.

## 13. Worked failure: healthy gateways, neúplné tail-sampling decisions

### Subject

```text
Incident: OTEL-PAY-46
Operation: enterprise final settlement
Release: 7.23.0
Collector distribution: otelcol-contrib 0.135.x
Gateway config: OTEL-GW-88
Gateway replicas: 4
Tail-sampling policy: keep errors, keep p99 > 2 s, sample 2 % ostatných
Routing generation: OTEL-ROUTE-19
Backend: Tempo 3.0 / tenant payments-prod
```

### Symptóm

Authoritative settlement SLI ukazuje `6.9 %` final failures. Tempo search však nájde iba `0.7 %` error traces a väčšina slow traces má missing provider child span. Collector gateways sú Ready, CPU pod 55 % a exporters hlásia úspešné requests.

### Competing hypotheses

1. application nenastavuje span status;
2. provider child spans nevznikajú;
3. Tempo historical path stráca spans;
4. semantic-convention migration zmenila operation names;
5. tail sampler dostáva neúplné traces;
6. memory limiter dropuje batches;
7. query používa nesprávny tenant alebo release;
8. late spans prichádzajú po sampling decision-e.

### Discriminating evidence

```text
SDK sampled flag: true
agent Collector accepted/exported spans: complete per trace fixture
agent → gateway load balancer: round-robin per OTLP request
spans jedného trace-u na gateway replicas: 2–4
per-gateway tail-sampler incomplete traces: high
keep-error decisions: below expected
memory-limiter refusals: 0
Tempo accepted spans: zodpovedajú kept partial populations
controlled trace-ID-aware route: complete trace a error keep
```

Pri scale-out-e sa odstránil load-balancing exporter s trace-ID routingom a agenti začali posielať batches cez bežný round-robin Service. Spans jedného trace-u skončili na rôznych stateful tail sampleroch.

Mechanizmus:

```text
complete trace vznikne v aplikáciách
→ agents exportujú spans v samostatných batches
→ round-robin ich rozdelí medzi gateways
→ každý tail sampler vidí partial trace
→ error/provider span nemusí byť na rovnakej replica
→ policy neidentifikuje error alebo latency
→ partial trace sa dropne alebo zachová neúplne
→ backend je healthy, evidence coverage je chybná
```

### Containment

- zastaviť ďalší gateway topology rollout;
- zachovať per-hop accepted/dropped, sampling reason a trace-ID distribution evidence;
- dočasne zvýšiť bounded head keep rate pre affected cohort, ak cost budget dovolí;
- nepovažovať trace-derived error rate za SLI;
- chrániť metrics/logs pipeline pred spoločným emergency changeom.

### Authoritative recovery

1. obnoviť trace-ID-aware routing pred tail samplingom;
2. pinovať topology a component inventory v manifeste;
3. vytvoriť multi-service complete-trace fixture;
4. testovať errors, slow traces, late spans a ordinary traces;
5. publikovať keep/drop reason metrics per policy;
6. canary-nuť jednu gateway cohortu;
7. overiť backend trace completeness a sampling distribution;
8. vykonať druhý scale/restart test.

### Acceptance verdict

Recovery je prijatá, keď:

- všetky spans synthetic trace-u dorazia k jednej active sampling identity;
- error a high-latency fixtures sú zachované;
- ordinary keep rate zodpovedá policy;
- incomplete/late trace counters sú bounded;
- backend trace graph je kompletný;
- metrics a logs signals neregresujú;
- forbidden sensitive baggage/attributes nie sú exportované;
- druhý gateway scale-out zachová affinity a coverage.

## 14. Self-observability a canary

Sleduj per hop:

- received, accepted, refused a dropped records;
- processor/filter/sampling reasons;
- queue size, capacity a oldest age;
- exporter attempts, failures a acknowledgement;
- memory limiter actions;
- resource/schema distribution;
- backend ingest lag;
- process CPU/memory/restarts.

End-to-end canary:

```text
known trace + metric + log
→ agent
→ gateway
→ policy processors
→ each intended backend
→ query/read-back
→ correlation a forbidden-field check
```

## 15. Troubleshooting model

### Žiadna telemetry

```text
producer signal
→ SDK/agent loaded state
→ resource a schema
→ endpoint/protocol/TLS/auth
→ receiver pipeline
→ processors/drop reasons
→ exporter queue/ack
→ backend tenant/query
```

### Duplicate telemetry

```text
manual + auto instrumentation
→ duplicate discovery/cluster receiver
→ two agents/file readers
→ fan-out/migration
→ ambiguous acknowledgement retry
→ backend dedup identity
```

### Collector OOM alebo backlog

```text
ingest/burst
→ active trace state
→ batch/queue sizes
→ tail-sampling wait
→ exporter/backend throughput
→ memory limiter
→ container/disk limit
→ loss boundary
```

### Schema drift

```text
producer/instrumentation version
→ semantic-convention status
→ resource/scope/schema URL
→ processor transformations
→ backend field/label mapping
→ dashboards/rules/SLO consumers
```

## 16. Anti-patterny

### OpenTelemetry ako observability stratégia

Framework neurčuje user outcome, SLO, alert owner ani incident action.

### Collector health ako delivery proof

Process môže byť healthy pri dropped, misrouted alebo semantically corrupted telemetry.

### Tail sampling za random load balancerom

Rozdelí stateful trace subject.

### Experimental component ako stabilný contract

Collector binary version nezaručuje component maturity.

### Všetky resource attributes ako labels

Vytvorí cardinality a churn.

### Redaction po fan-out-e

Sensitive data už opustili trusted processing boundary.

## 17. Kontrolné otázky

1. Čo tvorí exact OpenTelemetry subject?
2. Aký je rozdiel medzi API, SDK a zero-code instrumentation?
3. Prečo signal a Collector component maturity treba posudzovať samostatne?
4. Ako resource, scope a schema generation vytvárajú telemetry identity?
5. Prečo `service.name` nesmie byť Pod name?
6. Ako processor order mení correctness a privacy?
7. Kedy agent a gateway topology pridáva shared failure domain?
8. Prečo tail sampling potrebuje trace affinity?
9. Ako queues a memory limiter menia loss semantics?
10. Ako OTel metrics mapovať do Prometheus modelu?
11. Ako diagnostikovať duplicate alebo missing telemetry per hop?
12. Čo musí overiť end-to-end telemetry canary?

## Glossary impact

Relevantné pojmy: OpenTelemetry subject, signal-contract generation, Collector distribution generation, component-stability inventory, resource-precedence generation, instrumentation-scope generation, semantic-schema generation, processor-order contract, trace-affinity generation, per-hop telemetry accounting, exporter-delivery subject, telemetry-loss window, multi-signal canary a OpenTelemetry acceptance verdict.

## Primárne zdroje

- [OpenTelemetry specification overview](https://opentelemetry.io/docs/specs/otel/overview/)
- [OpenTelemetry signals](https://opentelemetry.io/docs/concepts/signals/)
- [Collector architecture](https://opentelemetry.io/docs/collector/architecture/)
- [Collector components](https://opentelemetry.io/docs/collector/components/)
- [Semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
- [Telemetry stability](https://opentelemetry.io/docs/specs/otel/telemetry-stability/)
- [Logs data model](https://opentelemetry.io/docs/specs/otel/logs/data-model/)
- [Profiles specification](https://opentelemetry.io/docs/specs/otel/profiles/)
- [OpenTelemetry sampling](https://opentelemetry.io/docs/concepts/sampling/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Jaeger a Tempo](jaeger-tempo.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Alert design a alert fatigue →](alert-design-alert-fatigue.md)
<!-- KNOWLEDGE-NAVIGATION:END -->