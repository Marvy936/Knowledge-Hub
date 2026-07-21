# Observability foundations glossary entries

## Audit record

Časovo označený záznam o tom, kto vykonal akú operáciu, voči ktorému resource-u, odkiaľ a s akým výsledkom. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Black-box monitoring

Pozorovanie systému zvonka z perspektívy používateľa alebo clienta, napríklad cez HTTP, DNS, TLS alebo end-to-end synthetic test. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Cardinality — telemetry

Počet unikátnych kombinácií labels alebo attributes; vysoká alebo neobmedzená cardinality môže výrazne zvýšiť memory, storage, query cost a destabilizovať telemetry pipeline. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Context propagation

Prenos tracing a correlation contextu cez procesy, služby, queues a async boundaries tak, aby bolo možné rekonštruovať end-to-end operáciu. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Correlation ID

Identifikátor používaný na spojenie logs, requests, events alebo ďalších telemetry records patriacich k rovnakej operácii. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Distributed trace

Model celej cesty requestu alebo operácie cez viac services a dependencies, zložený z navzájom prepojených spans. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Event — observability

Časovo označený záznam významnej zmeny alebo udalosti, napríklad deploymentu, failoveru, scalingu alebo configuration change-u. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Instrumentation

Kód, agent, library alebo platform capability, ktorá generuje telemetry signals o správaní systému. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Log

Časovo označený record udalosti, state-u alebo message, ideálne so stabilnou structured schema a correlation fields. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Metric

Agregovateľný číselný signal v čase používaný napríklad na rate, latency distribution, utilization, saturation alebo SLO measurement. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Monitoring

Systematické sledovanie vopred definovaných signals, states a thresholds s cieľom detegovať známe failure alebo degradation conditions. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Observability

Schopnosť porozumieť internému stavu systému z jeho externých outputs a skúmať aj neočakávané otázky pomocou kvalitnej, korelovateľnej telemetry. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Observability gap

Chýbajúci alebo nekvalitný signal, context, correlation, retention alebo query capability, ktorý bráni spoľahlivej diagnostike systému. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Observability maturity

Úroveň schopnosti organizácie štandardizovať instrumentation, correlation, alerting, SLO, telemetry governance a incident investigation. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Profile — observability

Telemetry signal zobrazujúci, kde application trávi CPU time, alokuje memory alebo čaká, používaný na performance diagnostiku. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Sampling — telemetry

Výber podmnožiny traces, logs alebo profiles na kontrolu volume a cost pri zachovaní relevantných failures a business operations. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Signal — observability

Typ telemetry reprezentujúci určitý pohľad na systém, napríklad metric, log, trace, event alebo profile. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Span

Jednotka distributed trace-u reprezentujúca jednu časovo ohraničenú operation s parent relation, attributes, events a statusom. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Telemetry

Dáta generované systémom o jeho stave a správaní, napríklad metrics, logs, traces, events, profiles a audit records. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Telemetry pipeline

Reťazec instrumentation sources, agents alebo collectors, processingu, exportu, storage a query vrstiev, ktorými telemetry prechádza. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## White-box monitoring

Pozorovanie interných signals systému, napríklad queue depth, connection pool, error counters, garbage collection alebo saturation. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).
