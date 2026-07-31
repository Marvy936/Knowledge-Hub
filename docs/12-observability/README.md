# Observability

Táto sekcia vysvetľuje, ako navrhovať, vytvárať, prenášať, ukladať a používať telemetry tak, aby operational decision vychádzal z presného evidence subjectu, nie iba z existencie dashboardu alebo green component healthu.

Cieľom nie je katalóg produktov. Sekcia buduje jeden súvislý systém od user/business otázky cez signal contract, instrumentation, backend state a query až po actionable alert, recovery a cardinality/cost closure.

## Section-wide learning chain

```text
user/business outcome alebo operational otázka
→ exact observed subject a expected population
→ signal a instrumentation contract
→ resource, operation, cohort a schema identity
→ emission a context propagation
→ collector/agent processing
→ sampling, redaction, cardinality a routing policy
→ transport a acknowledgement
→ backend-specific ingest/storage generation
→ query, derived signal a visualization
→ evidence-quality a coverage verdict
→ SLI/SLO, Golden Signals, RED alebo USE interpretation
→ alert/action contract alebo novel investigation
→ competing hypotheses a discriminating observations
→ containment a authoritative recovery
→ original, forbidden, adjacent-cohort a telemetry validation
→ retention, cost, cardinality a recurrence closure
```

Recurring state distinctions:

```text
configured
≠ loaded/effective

record emitted
≠ collected
≠ accepted
≠ durable
≠ queryovateľný

query result
≠ správna visualization
≠ správny operational decision

alert firing
≠ notification delivered
≠ incident acknowledged
≠ user outcome recovered

viac telemetry detailu
≠ vyššia evidence quality
```

Connected worked subjects `OBS-PAY-43` až `OBS-PAY-46` používajú Atlas Payments final-settlement workflow. Sekcia preto opakovane odlišuje HTTP acceptance, technical attempts, final business completion, resource saturation, telemetry coverage a notification outcome.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md),
- [Kubernetes](../09-kubernetes/README.md),
- [Cloud and AWS](../11-cloud-and-aws/README.md).

## Authoritative poradie

1. [Monitoring vs. observability](monitoring-vs-observability.md)
2. [Metrics, logs, traces a events](metrics-logs-traces-events.md)
3. [Instrumentation a telemetry](instrumentation-telemetry.md)
4. [RED method](red-method.md)
5. [USE method](use-method.md)
6. [Golden Signals](golden-signals.md)
7. [Prometheus](prometheus.md)
8. [Alertmanager](alertmanager.md)
9. [Grafana](grafana.md)
10. [Loki](loki.md)
11. [Elasticsearch alebo OpenSearch](elasticsearch-opensearch.md)
12. [Fluent Bit](fluent-bit.md)
13. [Jaeger a Tempo](jaeger-tempo.md)
14. [OpenTelemetry](opentelemetry.md)
15. [Alert design a alert fatigue](alert-design-alert-fatigue.md)
16. [Cardinality](cardinality.md)

Lineárna dokumentácia pokračuje sekciou [Security and Identity](../13-security-and-identity/README.md).

## Cieľ zvládnutia

### Questions, signals a instrumentation

Po dokončení má čitateľ vedieť:

- rozlíšiť monitoring condition, observability question, telemetry a instrumentation;
- definovať exact observed subject, expected outcome a signal coverage;
- rozlíšiť system occurrence, telemetry record, stored signal, query result a verdict;
- navrhnúť stable resource, operation, cohort, context a schema identity;
- kombinovať manual, automatic a platform instrumentation;
- riadiť sampling, processor order, redaction, privacy, overhead a loaded state;
- diagnostikovať absent evidence od produceru po consumer query.

### Service a resource health

- používať RED nad logical operations, nie iba technical attempts;
- aplikovať USE na complete resource inventory a effective capacity;
- definovať Golden Signals nad kompatibilnou user-outcome population;
- odlíšiť utilization, saturation, queues, errors a failover headroom;
- prejsť od SLO/user symptomu cez trace/dependency k resource bottlenecku;
- overiť recovery cez original aj forbidden business outcome.

### Metrics a alert delivery

- vysvetliť Prometheus discovery, relabeling, scrape, post-relabel sample set, TSDB, staleness, PromQL a rule state;
- odlíšiť `up=1`, expected metric completeness, local rule truth a remote read-back;
- navrhnúť Alertmanager identity, route, grouping, timing, inhibition, silence a receiver contract;
- diagnostikovať condition, firing, routing, delivery, duplicate a resolved paths;
- prevádzkovať metric-to-alert canary cez celý pipeline.

### Visualization a logs

- odlíšiť backend truth, query request, data frame, transformation a rendered Grafana value;
- spravovať dashboard source a loaded revision bez multi-writer driftu;
- vysvetliť Loki stream, chunk, TSDB schema, recent/historical path a retention;
- navrhnúť explicitný Elasticsearch/OpenSearch product, data-stream, mapping, bulk-item a lifecycle contract;
- prevádzkovať Fluent Bit od source inode/offsetu cez parser, route, chunk a buffer po backend acknowledgement;
- diagnostikovať no-data, mapping conflicts, replay duplicates, loss windows a retention mismatch.

### Tracing a OpenTelemetry

- vysvetliť expected span graph, propagation, head/tail sampling a trace affinity;
- odlíšiť tracing ingest acknowledgement, recent availability a historical publication;
- vysvetliť Jaeger v2 a Tempo 3.0 deployment/write/read boundaries;
- navrhnúť OpenTelemetry API/SDK, resource/scope/schema, OTLP a Collector topology;
- overovať signal a Collector component stability samostatne;
- používať per-hop accounting a multi-signal canary;
- diagnostikovať incomplete traces, sampling bias, queue loss, duplicate telemetry a semantic drift.

### Alert action a cardinality governance

- rozlíšiť page, ticket a informational event;
- navrhnúť canonical symptom page s action contractom, ownerom a safe first action;
- merať pages-per-incident, actionable rate, duplicates, flapping a response delay;
- testovať rule-to-receiver-to-resolved path ako code;
- rozlíšiť volume, active cardinality a churn;
- navrhnúť per-signal/per-tenant dimension budget a forbidden-dimension contract;
- riadiť series, streams, indexed fields, trace attributes, dashboard variables a alert identities;
- vykonať cardinality containment, authoritative schema recovery a historical-identity retirement.

## Ako sekciu používať

Odporúčaný investigation postup:

```text
1. potvrď user/business symptom a population
2. over signal authority a evidence completeness
3. lokalizuj operation/dependency cez RED, Golden Signals a traces
4. lokalizuj resource cez USE
5. porovnaj metrics, logs, traces, events, release/config a loaded state
6. zachovaj volatile evidence pred broad mutation
7. vykonaj bounded containment
8. oprav authoritative producer/policy/storage generation
9. over original aj forbidden outcome
10. over telemetry canaries, cost, retention a cardinality closure
```

Produktové kapitoly čítaj ako realizáciu tohto modelu, nie ako samostatné tool tutorials.

## Section-level completion gate

Sekcia je pripravená na používateľskú kontrolu, keď:

1. všetkých 16 authoritative kapitol má dominantný lifecycle a exact subject;
2. každý komplexný failure používa competing hypotheses a discriminating evidence;
3. configured/loaded, emitted/accepted/durable/queryable a technical/business boundaries sú konzistentné;
4. recovery obsahuje original, forbidden a relevantnú adjacent-cohort alebo second-operation validation;
5. každá technická kapitola obsahuje executable query, príkaz alebo konfiguráciu naviazanú na konkrétny operational outcome;
6. každý executable artifact vysvetľuje vstup, interný mechanizmus, read-back, proof boundary a failure alebo recovery path;
7. navigation chain funguje od CloudOps troubleshooting po CIA triádu;
8. section glossary je synchronizovaný do `GLOSSARY.md`;
9. learning-depth audit artifacts sú prázdne;
10. current product facts sú overené proti official primary documentation.

Finálny prose/practical gate overil všetkých 16 kapitol samostatne. Každá dosiahla `critical/high/medium = 0/0/0`, obsahuje najmenej dva executable PromQL, LogQL, TraceQL, CLI alebo configuration príklady a vysvetľuje, čo ich output preukazuje aj čo ešte nepreukazuje. Súvislý prose rozsah je 918–1 199 slov na kapitolu a bullet-word share zostáva medzi 9.1 % a 14.9 %, takže zoznamy nenesú hlavnú učebnú záťaž.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Monitoring vs. observability | Prose/practical revalidation complete | L2 |
| Metrics, logs, traces a events | Prose/practical revalidation complete | L2 |
| Instrumentation a telemetry | Prose/practical revalidation complete | L2 |
| RED method | Prose/practical revalidation complete | L2 |
| USE method | Prose/practical revalidation complete | L2 |
| Golden Signals | Prose/practical revalidation complete | L2 |
| Prometheus | Prose/practical revalidation complete | L2 |
| Alertmanager | Prose/practical revalidation complete | L2 |
| Grafana | Prose/practical revalidation complete | L2 |
| Loki | Prose/practical revalidation complete | L2 |
| Elasticsearch alebo OpenSearch | Prose/practical revalidation complete | L2 |
| Fluent Bit | Prose/practical revalidation complete | L2 |
| Jaeger a Tempo | Prose/practical revalidation complete | L2 |
| OpenTelemetry | Prose/practical revalidation complete | L2 |
| Alert design a alert fatigue | Prose/practical revalidation complete | L2 |
| Cardinality | Prose/practical revalidation complete | L2 |
