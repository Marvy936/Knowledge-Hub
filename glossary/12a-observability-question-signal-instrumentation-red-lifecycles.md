# Observability question, signal, instrumentation and RED lifecycle glossary entries

## Absent-evidence verdict — observability

Explicitné rozhodnutie, či chýbajúci signal znamená neprítomnosť system occurrence-u alebo failure emission, delivery, processing, ingestion, retention či query boundary. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Attempt amplification — RED

Rast počtu technical attempts voči počtu logical operations spôsobený retries, hedgingom, fan-outom alebo redelivery, ktorý môže zvýšiť downstream load aj pri stabilnom business trafficu. Pozri [RED method](docs/12-observability/red-method.md).

## Attempt counter — observability

Metric counter počítajúci technical executions alebo dependency calls oddelene od caller-visible logical operations. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Attempt duration — RED

Trvanie jedného technical attemptu, ktoré nesmie byť zamieňané s end-to-end duration celej logical operation vrátane retries, queue waitu a backoffu. Pozri [RED method](docs/12-observability/red-method.md).

## Attempts-per-operation distribution

Rozdelenie počtu technical attempts pripadajúcich na jednu logical operation, používané na detekciu retry amplification a degraded dependencies. Pozri [RED method](docs/12-observability/red-method.md).

## Bounded telemetry failure

Failure contract, pri ktorom telemetry export, buffering alebo backend outage nespôsobí nekontrolované blokovanie business threadu ani vyčerpanie application resources. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Business-outcome observation

Telemetry alebo validation merajúca final caller-visible či business-visible correctness a completion, nie iba interný process, target alebo HTTP acceptance stav. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Collector topology generation

Versionovaná agent, sidecar, gateway alebo tiered Collector architektúra vrátane routing, capacity, affinity, failure a tenant boundaries. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Completion gap — RED

Rozdiel medzi accepted alebo started operation rate a final successful completion rate, ktorý môže signalizovať queueing, stuck workflow, dropped state alebo telemetry mismatch. Pozri [RED method](docs/12-observability/red-method.md).

## Correlation chain — observability

Prechod od SLO alebo metric symptómu cez bounded cohort, exemplar/trace, spans, structured logs, deployment/config event a audit actor až po causal explanation a recovery validation. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Derived-signal authority

Verdict určujúci, či signal vypočítaný z logs, spans alebo iného source-u má dostatočnú coverage, sampling a correctness na konkrétne SLO, alert alebo investigation použitie. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Error numerator contract — RED

Explicitná definícia failed outcomes, result classes, partial/unknown states a scope-u používaného v čitateli error ratio. Pozri [RED method](docs/12-observability/red-method.md).

## Final-outcome class — RED

Klasifikácia logical operation ako definitive success, definitive failure, partial success, cancellation, timeout, success after retry alebo iný finálny contract verdict. Pozri [RED method](docs/12-observability/red-method.md).

## Instrumentation acceptance verdict

Dôkaz, že target instrumentation generation je skutočne načítaná, vytvára správnu identity/schema, prejde backend read-backom, neporušuje overhead/privacy budget a jej consumers fungujú. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Instrumentation generation

Versionovaný súbor code-based, zero-code a platform observation mechanisms spolu s resource, scope, propagation, sampling a export semantics. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Instrumentation subject

Exact combination application release-u, instrumentation generation, semantic-convention selection, Collector configu, backend route a observed business journey. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Loaded instrumentation state

Instrumentation, agent, SDK alebo Collector configuration skutočne používaná bežiacim processom, ktorá sa môže líšiť od deklarovaného environmentu alebo desired configu. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Loaded-state telemetry

Telemetry field alebo inventory preukazujúce effective configuration, secret, feature alebo release generation načítanú runtime cohortou namiesto iba desired-state deklarácie. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Logical duration — RED

End-to-end trvanie caller-visible logical operation vrátane queue waitu, processingu, dependency attempts, retry backoffu a final completion pathu. Pozri [RED method](docs/12-observability/red-method.md).

## Logical-operation counter

Metric counter inkrementovaný raz podľa accepted alebo final outcome jednej business/caller-visible operation bez ohľadu na interný retry alebo fan-out počet. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Measurement boundary — telemetry

Presný observation point, napríklad client, edge, handler, consumer, dependency alebo final business completion, na ktorom signal meria occurrence. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Measurement population — RED

Množina valid operations definovaná rovnakou unit, scope, traffic eligibility a time semantics pre RED numerator, denominator a duration. Pozri [RED method](docs/12-observability/red-method.md).

## Monitoring condition contract

Versionovaná známa otázka, measurement query, threshold/no-data semantics, duration, owner, route, action a recovery condition používaná na monitoring verdict. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Named telemetry event

Structured OpenTelemetry log record s neprázdnym event name, ktoré identifikuje event type a jeho schema. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Observability acceptance verdict

Dôkaz, že original business outcome je obnovený, forbidden outcome nevzniká, expected cross-signal correlation funguje a telemetry pipeline nevytvára false-green stav. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Observability question contract

Exact investigation otázka viazaná na subject, time window, possible cohorts, competing hypotheses, required evidence a operational decision. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Observation-point authority

Rozhodnutie, ktorá client, edge, service, queue, dependency alebo business boundary je autoritatívna pre konkrétny metric, SLI alebo outcome. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Observed subject — observability

Versionovaná kombinácia business capability, logical operation, release, configuration, telemetry generation, environment, Region/cohort a expected outcome, ku ktorej sa evidence viaže. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Occurrence-to-record boundary

Prechod medzi skutočnou system udalosťou a instrumentation rozhodnutím vytvoriť alebo nevytvoriť telemetry record. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Processor-order contract

Semantics určujúca poradie Collector processors, pretože enrichment, overwrite, filtering, redaction, sampling a routing môžu pri inom poradí vytvoriť odlišný effective signal. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Profile maturity boundary

Explicitný status OpenTelemetry Profiles specification, SDK/agent a backend supportu, ktorý musí byť overený pred production závislosťou na profile signale. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Rate denominator contract — RED

Definícia unit, accepted/started/completed boundary, deduplication, retries, batches, valid traffic a absent-traffic semantics používaná pre Rate a error-ratio denominator. Pozri [RED method](docs/12-observability/red-method.md).

## RED acceptance verdict

Dôkaz, že Rate, Errors a Duration používajú konzistentné logical-operation semantics, retry amplification je bounded, SLO sa obnovilo a forbidden duplicate alebo hidden-failure outcome nevzniká. Pozri [RED method](docs/12-observability/red-method.md).

## RED subject

Exact logical operation, measurement/completion boundaries, release, RED schema, time window a bounded cohort, pre ktorý sa Rate, Errors a Duration vyhodnocujú. Pozri [RED method](docs/12-observability/red-method.md).

## Resource merge precedence — telemetry

Pravidlá určujúce, ktorý SDK, detector alebo processor attribute zvíťazí pri spájaní resource identity, najmä pri stable service a ephemeral instance fields. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Resource-versus-scope identity

Rozlíšenie observed entity, napríklad service alebo Pod, od instrumentation library/componentu a jeho version, ktorý telemetry record vytvoril. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Sampled coverage

Množina operations alebo records zachovaných sampling policy spolu s keep/drop dôvodmi; nemusí reprezentovať úplný traffic denominator. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Semantic-convention generation

Version a stability selection OpenTelemetry semantic conventions spolu s emitted old/new/dual schema a consumer migration contractom. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Signal-quality verdict

Klasifikácia telemetry ako complete/authoritative, partial, stale, sampled, missing pre pipeline failure alebo unknown coverage podľa konkrétneho use case-u. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Signal subject

Exact producer, operation, measurement boundary, release, instrumentation/schema generation, resource identity, coverage, pipeline a retention/query cut-off konkrétneho signalu. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Stable service identity

Logical `service.name` alebo ekvivalentná identity zachovaná cez scaling, restart a Pod/host replacement, oddelená od ephemeral process a instance attributes. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Telemetry canary

Kontrolovaný end-to-end metric, log, trace alebo event occurrence používaný na overenie emission, delivery, processing, backend read-back, query a alert pathu. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Telemetry coverage contract

Expected evidence inventory pre critical journey a jeho success, failure, no-data, privacy a correlation boundaries. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Telemetry read-back test

Validácia, ktorá po emission a exporte query-ne backend a overí effective identity, schema, value, correlation a freshness namiesto spoliehania sa iba na exporter success. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Telemetry requirement inventory

Zoznam metrics, traces, logs, events, identities, propagation a pipeline evidence odvodený z business journeys, SLIs, failure modes a operational decisions. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Unknown-outcome class — RED

Operation outcome, pri ktorom side effect mohol nastať, ale acknowledgement alebo authoritative evidence chýba; pred retry potrebuje reconciliation. Pozri [RED method](docs/12-observability/red-method.md).
