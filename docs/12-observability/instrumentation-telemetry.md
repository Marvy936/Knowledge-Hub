# Instrumentation a telemetry

Instrumentation je mechanizmus, ktorým application, runtime, operating system alebo infrastructure vytvára telemetry. Telemetry je výsledný tok dát opisujúci správanie systému. Observability nevznikne samotným nasadením collectora alebo backendu; vzniká až vtedy, keď správne zvolená instrumentation vytvára korelovateľné a prevádzkovo užitočné signals.

## 1. Mentálny model

```text
business a operational otázky
→ telemetry requirements
→ instrumentation points
→ API/SDK alebo zero-code agent
→ resource a context metadata
→ local buffering/batching
→ collector alebo priamy export
→ processing, sampling a redaction
→ backend ingestion
→ query, alert, dashboard, SLO a investigation
```

Najčastejšia chyba je začať backendom a až potom hľadať, aké dáta doň posielať.

## 2. Instrumentation oproti telemetry

### Instrumentation

Kód alebo mechanizmus, ktorý pozoruje operáciu a vytvára signal.

Príklady:

- application counter pre dokončené objednávky,
- HTTP middleware vytvárajúci spans,
- log appender dopĺňajúci trace ID,
- runtime agent zbierajúci JVM metrics,
- eBPF program sledujúci system calls,
- cloud service exportujúca service metrics,
- Kubernetes collector čítajúci object state.

### Telemetry

Dáta, ktoré instrumentation vytvorí:

- metric measurements,
- log records,
- spans a traces,
- events,
- profiles,
- resource metadata,
- context a baggage.

Instrumentation je producer contract. Telemetry pipeline je delivery a processing contract.

## 3. Business-first instrumentation

Infrastructure metrics nestačia na posúdenie business služby.

Príklady business signals:

- úspešné checkouty,
- payment authorization outcomes,
- queue processing age,
- document indexing success,
- backup restore validation,
- model inference success a confidence boundary,
- account provisioning duration.

Pre každý critical user journey definuj:

- začiatok a koniec operácie,
- success a failure semantics,
- latency boundary,
- business volume,
- dependency calls,
- retry a idempotency behavior,
- ownera,
- SLI alebo operational decision.

## 4. Code-based instrumentation

Code-based instrumentation používa explicitné APIs a SDKs.

Výhody:

- business semantics,
- vlastné operation names,
- presné error a status pravidlá,
- custom metrics,
- domain attributes,
- kontrola spans a events,
- explicitné propagation boundaries.

Nevýhody:

- potrebuje zmenu kódu,
- vyžaduje review a testing,
- môže sa líšiť medzi tímami,
- nekvalitná implementácia pridáva overhead alebo cardinality.

Code instrumentation je potrebná tam, kde framework alebo agent nepozná business význam operácie.

## 5. Zero-code a automatic instrumentation

Zero-code instrumentation používa agent, runtime hooks, bytecode injection, environment variables alebo platform integráciu bez úpravy application source.

Typicky pokrýva:

- inbound a outbound HTTP,
- database clients,
- messaging libraries,
- runtime metrics,
- common frameworks,
- standard context propagation.

Výhody:

- rýchle adoption,
- konzistentné baseline signals,
- vhodné pre legacy alebo third-party software,
- menší zásah do application code.

Limity:

- nepozná business outcome,
- môže vytvoriť príliš generické operation names,
- nemusí pokryť custom protocols,
- môže pridať overhead,
- môže omylom zachytiť citlivé attributes,
- version compatibility treba testovať.

Najlepší model často kombinuje automatic baseline s explicitnou business instrumentation.

## 6. Manual, generated a platform telemetry

### Manual instrumentation

Developer explicitne vytvára metrics, spans, logs alebo events.

### Generated instrumentation

Framework, library alebo code generation vytvára telemetry podľa štandardného contractu.

### Platform telemetry

Cloud, Kubernetes, service mesh, proxy, database alebo runtime poskytuje signals bez application zmeny.

Platform signal nie je automaticky user-outcome signal. Napríklad healthy load balancer target nepreukazuje správnosť checkout workflowu.

## 7. OpenTelemetry architecture

OpenTelemetry je vendor-neutral framework pre instrumentation, generation, collection a export traces, metrics a logs.

Hlavné prvky:

- API — contract používaný application a libraries,
- SDK — sampling, processing, aggregation a export implementation,
- instrumentation libraries,
- auto-instrumentation agents,
- context propagation,
- semantic conventions,
- Collector,
- exporters.

Application code má byť čo najmenej viazaný na konkrétny observability backend.

## 8. API oproti SDK

Library má typicky používať API, nie vynucovať konkrétny SDK/backend.

Application alebo runtime configuration rozhoduje:

- ktorý SDK sa použije,
- sampling,
- exporters,
- processors,
- resource attributes,
- endpointy,
- authentication,
- batching.

Tým sa znižuje vendor coupling a konflikt viacerých telemetry implementácií.

## 9. Instrumentation scope

Instrumentation scope identifikuje logical library alebo component, ktorý telemetry vytvoril.

Zahŕňa typicky:

- name,
- version,
- schema URL alebo ďalšie metadata.

Pomáha rozlíšiť:

- application-owned instrumentation,
- framework instrumentation,
- database client instrumentation,
- auto-instrumentation package,
- rozdielne versions toho istého instrumentora.

Pri incidente možno identifikovať, či chybný attribute alebo span vytvorila application alebo konkrétna instrumentation library.

## 10. Resource identity

Resource opisuje entitu produkujúcu telemetry.

Príklady attributes:

- `service.name`,
- `service.version`,
- `deployment.environment.name`,
- host alebo cloud resource identity,
- Kubernetes cluster, namespace, Pod a container,
- cloud account, Region a zone.

`service.name` musí byť stabilný a konzistentný. Dynamic Pod name nemá nahrádzať logical service identity.

## 11. Semantic conventions

Semantic conventions štandardizujú names a meanings pre operations a attributes.

Výhody:

- interoperabilita,
- reusable dashboards,
- konzistentné queries,
- cross-language correlation,
- menší počet custom schemas.

Riziko:

- conventions sa môžu vyvíjať,
- migration môže meniť names alebo stability,
- custom business attributes stále potrebujú governance.

Version instrumentation a schema changes explicitne sleduj.

## 12. Context propagation

Context propagation prenáša trace a correlation informácie cez service boundaries.

Môže obsahovať:

- trace ID,
- parent span ID,
- sampling decision,
- tracestate,
- baggage.

Boundaries:

- HTTP headers,
- gRPC metadata,
- message headers,
- queue attributes,
- scheduled jobs,
- batch records,
- async callbacks.

Prerušená propagation vytvára samostatné fragmenty trace-u a znemožňuje causal investigation.

## 13. Baggage

Baggage je contextual key/value informácia prenášaná spolu s requestom.

Použitie:

- tenant class,
- experiment cohort,
- region routing context,
- business workflow ID.

Riziká:

- propagation do nedôveryhodných systems,
- sensitive data leakage,
- rast header size,
- high-cardinality attributes,
- nejasný lifecycle.

Baggage nie je secret store ani univerzálny business payload.

## 14. Telemetry pipeline

Typický pipeline:

```text
application SDK alebo agent
→ OTLP/export protocol
→ node/sidecar/gateway Collector
→ receivers
→ processors
→ exporters
→ one alebo viac backends
```

### Receivers

Prijímajú telemetry cez OTLP, Prometheus scrape, logs, cloud protocols alebo ďalšie integrations.

### Processors

Môžu vykonávať:

- batching,
- memory limiting,
- filtering,
- attribute transformation,
- redaction,
- tail sampling,
- resource enrichment,
- routing.

### Exporters

Odosielajú telemetry do backendu alebo ďalšieho collectora.

Collector nie je durable message broker, pokiaľ konkrétna konfigurácia a komponenty neposkytujú taký contract.

## 15. Agent, sidecar a gateway deployment

### Agent alebo DaemonSet

Blízko workloadu alebo Node-u.

Výhody:

- local collection,
- host/container metadata,
- kratšia network path,
- rozdelenie loadu.

### Sidecar

Per-Pod alebo per-application collector.

Výhody:

- silná isolation,
- application-specific config.

Nevýhody:

- resource overhead,
- vysoký počet instances,
- configuration drift.

### Gateway

Centralizovaná alebo tiered processing vrstva.

Výhody:

- tail sampling,
- centralized policy,
- backend fan-out,
- tenant routing.

Nevýhody:

- shared bottleneck,
- potreba HA a scalingu,
- väčší blast radius.

Bežný production model kombinuje node agents a gateway collectors.

## 16. Push a pull

### Pull

Monitoring system periodicky scrape-ne target.

Výhody:

- target discovery,
- explicitná scrape health,
- central control intervalu,
- jednoduché detection chýbajúceho targetu.

### Push

Producer alebo agent posiela telemetry do receivera.

Výhody:

- prirodzené pre traces/logs/events,
- funguje pre ephemeral alebo outbound-only sources,
- async batching.

Push success nepreukazuje backend ingestion. Pull failure nemusí znamenať application failure. Monitoruj celý pipeline.

## 17. Batching, queue a backpressure

Batching znižuje network a backend overhead, ale zvyšuje latency a potential loss window.

Konfiguračné trade-offy:

- batch size,
- flush interval,
- memory queue,
- persistent queue,
- retry policy,
- max age,
- exporter concurrency.

Pri backend outage môže telemetry pipeline:

- bufferovať,
- dropovať,
- retryovať,
- blokovať application thread,
- spotrebovať disk/memory.

Production design musí explicitne určiť, čo sa stane pri dlhom výpadku backendu.

## 18. Sampling a filtering

Sampling znižuje volume, ale mení analytical coverage.

Filtering môže odstraňovať:

- health-check traffic,
- low-value debug logs,
- noisy framework spans,
- sensitive fields,
- redundant attributes.

Nesmie bez analýzy odstrániť:

- rare errors,
- high-latency traces,
- security events,
- SLO denominator/numerator data,
- audit evidence.

Sampling policy musí byť meraná: koľko records prišlo, koľko sa zachovalo a prečo.

## 19. Telemetry self-observability

Telemetry pipeline potrebuje vlastné signals:

- accepted records,
- refused records,
- dropped records,
- queue size a capacity,
- exporter failures,
- retry count,
- batch latency,
- memory a CPU,
- backend ingestion lag,
- scrape health,
- config reload status.

Bez self-observability vyzerá strata telemetry ako zdravý systém.

## 20. Overhead

Instrumentation môže zvýšiť:

- CPU,
- allocations a memory,
- request latency,
- network bandwidth,
- storage,
- backend cardinality,
- application startup time.

Testuj:

- baseline bez instrumentation,
- representative load,
- error a high-cardinality path,
- collector/backend outage,
- max queue,
- dynamic config change.

Overhead budget má byť explicitný a sledovaný.

## 21. Security a privacy

Instrumentation môže zachytiť:

- authorization headers,
- cookies,
- database statements,
- request bodies,
- file paths,
- user IDs,
- tokens a secrets,
- prompt alebo model inputs.

Controls:

- attribute allowlist,
- redaction pri producerovi aj collectore,
- TLS,
- exporter authentication,
- tenant isolation,
- least privilege,
- retention a deletion,
- audit,
- data residency,
- secure defaults.

Redaction až v backend UI je neskoro, ak sensitive data už prešlo pipeline-om.

## 22. Versioning a change management

Telemetry je production contract.

Zmeny, ktoré môžu poškodiť consumers:

- metric rename,
- label rename,
- unit change,
- histogram bucket change,
- span operation rename,
- semantic-convention migration,
- log schema change,
- sampling zmena,
- service identity zmena.

Použi:

- schema/version field,
- compatibility window,
- dual-write pri kritickom migration,
- dashboard/alert tests,
- rollout a rollback,
- cardinality review.

## 23. Instrumentation review checklist

Pre každú service over:

1. Ktoré user journeys sú kritické?
2. Aké SLIs a operational decisions potrebujeme?
3. Máme rate, errors a latency distribution?
4. Sú dependency calls traced?
5. Sú errors korelované v logs a spans?
6. Je context propagovaný cez async boundaries?
7. Sú labels bounded?
8. Sú citlivé fields odstránené?
9. Je signal schema stabilná?
10. Je telemetry pipeline monitorovaná?
11. Poznáme overhead a cost?
12. Má každý signal ownera?

## 24. Troubleshooting instrumentation gapu

```text
chýba telemetry pre všetky alebo len niektoré requests?
→ správna application/version/environment?
→ SDK/agent načítaný?
→ instrumentation library kompatibilná?
→ resource/service identity?
→ context propagator?
→ sampling/filtering?
→ exporter endpoint/auth/TLS?
→ collector receiver a pipeline routing?
→ backend tenant/schema/time range?
```

Príklady:

### Traces končia na service boundary

Over outbound injection, inbound extraction, proxy/header forwarding a message metadata.

### Metrics existujú, ale labels chýbajú

Over resource detection, views/processors, attribute limits a backend transformation.

### Logs nemajú trace ID

Over active span context, logging bridge/appender a async execution context.

### Collector dropuje records

Over memory limiter, queue, backend throttling, retry age a exporter failures.

## 25. Anti-patterny

### Auto-instrumentation považovaná za hotovú observability

Chýbajú business outcomes a custom failure semantics.

### Custom instrumentation bez conventions

Každý tím používa iné names a attributes.

### Collector ako neobmedzený buffer

Backend outage vyčerpá memory alebo disk.

### Telemetry zlyhanie blokuje business request

Observability dependency môže vytvoriť outage, ak nie je navrhnutá s bounded failure behavior.

### Secret redaction iba v dashboarde

Sensitive data už bolo exportované a uložené.

### Zmena metric unit bez migration

Alerts a dashboards produkujú nesprávne výsledky.

## 26. Kontrolné otázky

1. Aký je rozdiel medzi instrumentation a telemetry?
2. Kedy potrebuješ code-based instrumentation?
3. Čo zero-code instrumentation typicky nevie?
4. Aký je rozdiel medzi OpenTelemetry API a SDK?
5. Na čo slúži instrumentation scope?
6. Prečo je resource identity kritická?
7. Kedy použiť agent, sidecar alebo gateway collector?
8. Ako batching a retry menia loss a latency?
9. Ako monitoruješ samotný telemetry pipeline?
10. Ktoré instrumentation zmeny sú breaking changes?

## Glossary impact

Relevantné pojmy: code-based instrumentation, zero-code instrumentation, automatic instrumentation, OpenTelemetry API, OpenTelemetry SDK, instrumentation library, instrumentation scope, resource attributes, semantic conventions, context propagation, baggage, OTLP, receiver, processor, exporter, Collector agent, Collector gateway, telemetry batching, telemetry backpressure a telemetry self-observability.

## Primárne zdroje

- [OpenTelemetry instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/)
- [OpenTelemetry concepts](https://opentelemetry.io/docs/concepts/)
- [OpenTelemetry instrumentation scope](https://opentelemetry.io/docs/concepts/instrumentation-scope/)
- [OpenTelemetry documentation](https://opentelemetry.io/docs/)
- [Prometheus instrumentation practices](https://prometheus.io/docs/practices/instrumentation/)
- [Prometheus client libraries](https://prometheus.io/docs/instrumenting/clientlibs/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Metrics, logs, traces a events](metrics-logs-traces-events.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: RED method →](red-method.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
