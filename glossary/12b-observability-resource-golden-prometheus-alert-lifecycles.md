# Observability resource, Golden Signal, Prometheus and alert lifecycle glossary entries

## Resource-analysis subject — USE

Versionovaný subject spájajúci affected service operation a cohort s exact bounded resource-om, jeho enforcement boundary, configured a loaded capacity generation, observation windowom a ownerom. Pozri [USE method](docs/12-observability/use-method.md).

## Effective resource capacity

Kapacita skutočne dostupná konkrétnemu workloadu po zohľadnení loaded limits, reservations, unhealthy members, topology, quotas, maintenance a failover constraints. Pozri [USE method](docs/12-observability/use-method.md).

## Loaded resource limit

Runtime limit, ktorý component skutočne používa, napríklad per-process connection-pool maximum; môže sa líšiť od desired alebo deklarovanej konfigurácie. Pozri [USE method](docs/12-observability/use-method.md).

## Utilization observation — USE

Meranie podielu effective resource capacity používaného v presnom intervale a scope-e, vrátane explicitného time-, capacity-, throughput- alebo concurrency-based denominatora. Pozri [USE method](docs/12-observability/use-method.md).

## Saturation observation — USE

Dôkaz práce, ktorú resource nevie okamžite obslúžiť, napríklad queue length, wait time, throttling, blocked tasks, drops alebo rejection. Pozri [USE method](docs/12-observability/use-method.md).

## Resource error observation — USE

Časovo a subjectovo viazaný dôkaz explicitného resource failure-u, napríklad OOM, acquire timeout, I/O error, quota rejection alebo allocation failure. Pozri [USE method](docs/12-observability/use-method.md).

## Hidden-queue inventory

Versionovaný zoznam všetkých čakacích vrstiev v operation path-e, napríklad client backoff, worker queue, connection pool, lock wait, device queue alebo provider scheduler. Pozri [USE method](docs/12-observability/use-method.md).

## USE acceptance verdict

Rozhodnutie, že exact resource bottleneck bol odstránený, original user outcome obnovený, saturation a errors sa vrátili do guardrailov a capacity change nevytvorila forbidden downstream amplification. Pozri [USE method](docs/12-observability/use-method.md).

## Golden-Signal subject

Exact capability, workflow, valid demand population, cohort, version, measurement window a caller outcome, pre ktoré Latency, Traffic, Errors a Saturation tvoria spoločný service-health contract. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Latency-boundary contract

Explicitný start a end measurement point pre latency vrátane queue, dependency alebo final workflow completion semantics a oddelenia successful, failed a degraded populations. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Logical demand unit — Golden Signals

Caller alebo business jednotka trafficu, napríklad logical settlement alebo message, oddelená od retries, fan-out calls a technical attempts. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Demand amplification

Pomer interných attempts, fan-out calls alebo redeliveries voči logical demandu, ktorý môže rásť bez rastu user trafficu a vytvárať downstream overload. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Business error population

Množina valid operations klasifikovaných podľa final caller alebo business outcome-u vrátane timeoutov, partial, degraded, silent a unknown výsledkov. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Silent outcome failure

Operation, ktorá neprodukuje bežný explicitný transport error, ale nesplní final business contract, napríklad accepted command bez completion alebo `200` s nesprávnym resultom. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Saturation-resource contract

Výber exact critical resource-u alebo queue, jeho effective capacity denominatora, wait/rejection signalu a leading thresholdu pre konkrétny Golden-Signal subject. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Capacity-risk verdict

Rozhodnutie, či aktuálna saturation, scaling delay a failover headroom predstavujú imminent risk pre caller outcome alebo error budget. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Black-box outcome canary

Kontrolovaná external operácia overujúca skutočný caller alebo business contract nezávisle od internal telemetry a dashboard assumptions. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Golden-Signal acceptance verdict

Dôkaz, že Latency, Traffic, Errors a Saturation používajú kompatibilné populations, original outcome je obnovený a traffic drop, duplicate effect ani telemetry absence nevytvárajú false-green stav. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Prometheus subject

Versionovaný metrics evidence subject zahŕňajúci producer/release, discovery a scrape config, target, post-relabel labels, Prometheus replica, TSDB, rule generation, remote-write generation a query window. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Metric-contract generation — Prometheus

Versionovaná definícia metric name, type, base unit, observation/reset boundary, labels, resource identity, expected freshness a consumers. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Expected target generation — Prometheus

Versionovaný inventory endpoints, ktoré majú po service discovery a target relabelingu zostať eligible na scrape. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Scrape attempt — Prometheus

Jedna HTTP retrieval, exposition parsing a sample-validation operácia pre exact target a evaluation time; úspech vytvára `up=1`, nie business-health verdict. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Post-relabel sample set

Exact množina samples a labels, ktorá zostane po target-label application a metric relabelingu a môže byť ingestovaná do local TSDB. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Local TSDB generation — Prometheus

Queryovateľný local state konkrétnej Prometheus replica vytvorený z WAL, head blocku, immutable blocks, compaction a retention lifecycle-u. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Staleness verdict — Prometheus

Rozhodnutie, či series predstavuje current measurement, zmizla pre target/label/producer zmenu alebo je už stale a nesmie byť interpretovaná ako aktuálna hodnota. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Recording-rule generation

Versionovaný PromQL expression, input-series inventory, evaluation interval a output metric/label contract materializujúci derived time series. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Rule-input closure

Dôkaz, že všetky expected source series a labels pre recording alebo alerting rule existujú, sú fresh a pokrývajú správnu population. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Local-versus-remote metrics state

Explicitné porovnanie local Prometheus samples/rule state-u s remote-write queue a downstream backend read-back stavom. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Native-histogram compatibility generation

Versionovaný adoption contract spájajúci client library, exposition, scrape, local storage/PromQL, rules, remote backend, dashboards a rollback pre Prometheus native histograms. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Prometheus acceptance verdict

Dôkaz, že expected targets a post-relabel series existujú, TSDB/rules používajú správnu population, controlled signal vytvorí alert a local/remote/no-data states sú rozlíšené. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Alert-notification subject

Versionovaný subject spájajúci Prometheus rule generation, complete alert labels, Alertmanager cluster/config, route, group, receiver a external incident key. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert-identity generation

Complete stable label set určujúci Alertmanager fingerprint, deduplication, grouping, routing, silence a inhibition behavior pre konkrétnu alert generation. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Notification-decision path

Alertmanager lifecycle od prijatého alertu cez route, grouping, timing, silence/mute/inhibition verdict, template a receiver attempt po external incident outcome. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Route-policy generation — Alertmanager

Versionovaný route tree, matcher order, inherited grouping/timing, `continue` behavior a receiver mapping načítané konkrétnym Alertmanager runtime-om. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Group-identity contract — Alertmanager

Množina labels reprezentujúca spoločný incident boundary a určujúca, ktoré alerts sa spoja do jednej notification group. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Inhibition-scope contract

Source, target a `equal` label policy určujúca, v ktorých environment, Region, cluster alebo service boundaries môže firing parent alert mutovať child notifications. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Receiver-delivery subject

Exact receiver integration, template generation, authentication, external incident key, attempt a acknowledgement/unknown-outcome state pre jednu notification group. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Unknown notification outcome

Stav, keď Alertmanager nevie, či receiver vytvoril incident, pretože request mohol uspieť, ale acknowledgement sa stratilo; retry potom môže vytvoriť duplicate external outcome. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Notification-path canary

Kontrolovaný alert prechádzajúci rule, všetky Alertmanager replicas, route/group/muting policy, test receiver, external acknowledgement a resolved closure. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alertmanager acceptance verdict

Dôkaz, že expected alert vytvoril správnu receiver notification a resolved outcome, unrelated scope nebol inhibovaný alebo silencovaný a HA/retry nevytvorili neakceptované duplicity. Pozri [Alertmanager](docs/12-observability/alertmanager.md).
