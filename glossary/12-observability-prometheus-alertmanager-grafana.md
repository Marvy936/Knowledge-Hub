# Prometheus, Alertmanager and Grafana glossary entries

## Alert fingerprint

Stabilný identifikátor Alertmanager alertu odvodený z jeho úplného label setu; používa sa na deduplication a alert identity. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert group — Alertmanager

Množina firing alebo resolved alerts zoskupená podľa `group_by` labels a odosielaná ako jedna notification. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert identity

Identita alertu určená stabilným label setom; zmena dynamického labelu vytvorí novú alert identity. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert storm

Veľké množstvo súvisiacich alebo duplicitných alerts a notifications, ktoré zahlcuje Alertmanager, receivers alebo on-call tím. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alertmanager

Komponent Prometheus ekosystému, ktorý prijíma alerts, deduplikuje ich, zoskupuje, routuje, mutuje a posiela notifications do receivers. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alertmanager HA

Viac Alertmanager replicas koordinovaných peer meshom a replikáciou silence/notification state-u; zvyšuje dostupnosť, ale negarantuje exactly-once notifications. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Annotation — Grafana

Časovo označený deployment, incident, configuration alebo iný event zobrazený v dashboardoch na koreláciu telemetry so zmenami. Pozri [Grafana](docs/12-observability/grafana.md).

## Alert annotation — Prometheus

Dynamický ľudský context alerting rule, napríklad summary, description, current value alebo runbook URL, ktorý nie je súčasťou alert identity. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert label — Prometheus

Stabilný key/value atribút alertu používaný na identity, grouping, routing, silences a inhibition. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alerting rule — Prometheus

PromQL expression vyhodnocovaná Prometheus rule engine-om, ktorá po splnení condition a voliteľného `for` vytvára firing alert. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Alertmanager notification log

Runtime state používaný Alertmanagerom na deduplication, group timing a rozhodovanie o update/repeat notifications. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alertmanager peer mesh

Peer-to-peer cluster communication medzi Alertmanager replicas na replikáciu silences a notification state-u. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Dashboard — Grafana

Usporiadaná množina panels, variables, annotations, links a time settings navrhnutá na konkrétny operational alebo business účel. Pozri [Grafana](docs/12-observability/grafana.md).

## Dashboard as code

Správa dashboard definitions cez version-controlled JSON, provisioning files, API, Terraform, Operator alebo generátor namiesto neauditovaných UI-only zmien. Pozri [Grafana](docs/12-observability/grafana.md).

## Dashboard link

Odkaz z dashboardu na ďalší dashboard alebo external systém s voliteľným prenosom time range-u a variables. Pozri [Grafana](docs/12-observability/grafana.md).

## Dashboard provisioning

Automatické vytváranie a synchronizácia Grafana dashboards z deklaratívneho source-u, typicky files alebo IaC. Pozri [Grafana](docs/12-observability/grafana.md).

## Data frame — Grafana

Normalizovaná štruktúra query výsledku zložená z fields, ktorú Grafana transformuje a vizualizuje. Pozri [Grafana](docs/12-observability/grafana.md).

## Data link — Grafana

Odkaz naviazaný na konkrétnu field hodnotu, napríklad trace ID, Pod, error code alebo deployment revision. Pozri [Grafana](docs/12-observability/grafana.md).

## Data source — Grafana

Plugin a configuration umožňujúca Grafane queryovať externý metrics, logs, traces, SQL, cloud alebo iný backend. Pozri [Grafana](docs/12-observability/grafana.md).

## Data-source-managed alert

Alert rule uložená a vyhodnocovaná v Prometheus, Mimir, Loki alebo inom podporovanom ruler systéme, pričom Grafana poskytuje management UI. Pozri [Grafana](docs/12-observability/grafana.md).

## Data-source plugin

Grafana plugin implementujúci query, authentication, health-check a data-frame integration pre konkrétny backend. Pozri [Grafana](docs/12-observability/grafana.md).

## Equal labels — Alertmanager

Labels, ktorých hodnoty musia byť zhodné medzi source a target alertom, aby sa aplikovala inhibition. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Exporter — Prometheus

Komponent, ktorý číta stav systému bez native Prometheus instrumentation a vystavuje ho v Prometheus metrics formáte. Pozri [Prometheus](docs/12-observability/prometheus.md).

## External labels — Prometheus

Labels pridávané Prometheus serverom pri komunikácii s externými systémami na identifikáciu clusteru, Regionu, tenant-u alebo replica topology. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Federation — Prometheus

Hierarchický model, v ktorom jeden Prometheus scrape-ne vybrané series z federation endpointu iného Prometheus servera. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Field — Grafana

Jedna typed column alebo series v Grafana data frame s values, labels a display konfiguráciou. Pozri [Grafana](docs/12-observability/grafana.md).

## Firing alert

Alert, ktorého rule condition je splnená a prešiel voliteľnou pending dobou; Prometheus ho odosiela Alertmanageru. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Folder permission — Grafana

Prístupové pravidlo pre dashboardy a folders; samo osebe nemusí obmedziť možnosť queryovať underlying data source. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana

Platforma na queryovanie, vizualizáciu, alerting a interaktívne skúmanie telemetry z externých data sources. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana correlation

Konfigurácia prepájajúca fields a query context medzi metrics, logs, traces alebo ďalšími data sources počas investigation. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana Explore

Ad hoc query a investigation workspace na interaktívne skúmanie metrics, logs a traces bez vytvorenia dashboardu. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana expression

Server-side alebo alerting calculation nad výsledkami jednej či viacerých data-source queries, napríklad math, reduce, resample alebo threshold. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana HA

Multi-instance Grafana deployment so spoločnou podporovanou SQL database, konzistentnou configuration, plugins a load-balancing modelom. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana-managed alert

Alert rule uložená a vyhodnocovaná Grafana alerting engine-om nad podporovanými data sources a expressions. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana notification policy

Routing a grouping policy Grafana Alerting, ktorá mapuje alert instances na contact points podľa labels a inheritance. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana panel

Základný dashboard component kombinujúci query, transformations, field configuration a visualization. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana variable

Dashboard placeholder získaný z query, custom listu alebo iného source-u a interpolovaný do queries, titles alebo links. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana variable interpolation

Nahradenie variable jej aktuálnou hodnotou pred odoslaním query data source-u, vrátane data-source-specific escaping a formatting. Pozri [Grafana](docs/12-observability/grafana.md).

## Group interval

Minimálny interval pred ďalšou notification aktualizáciou existujúcej Alertmanager group po zmene jej alert setu. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Group wait

Čas, ktorý Alertmanager čaká pred prvou notification novej alert group, aby mohol zhromaždiť súvisiace alerts alebo inhibiting parent alert. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Head block — Prometheus

Aktívna in-memory a WAL-backed časť Prometheus TSDB obsahujúca najnovšie samples pred vytvorením immutable blockov. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Inhibition — Alertmanager

Automatické muting pravidlo, ktoré potlačí target alert notifications, keď firing source alert matchuje definovaný scope. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Instant vector — PromQL

Množina time series s jednou sample hodnotou pre každý label set v konkrétnom evaluation čase. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Local TSDB — Prometheus

Lokálny time-series storage Prometheus servera založený na head blocku, WAL, immutable blocks, compaction a retention. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Matcher — Alertmanager

Podmienka nad alert labels používaná v route, silence alebo inhibition pravidle. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Metric relabeling

Prometheus relabeling fáza po scrape-nutí a pred ingestion, používaná na drop alebo transformáciu metric samples a labels. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Mute time interval — Alertmanager

Opakujúce sa časové pravidlo, ktoré mutuje notifications na matched route počas definovaných intervalov. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Native histogram — Prometheus

Histogram sample reprezentácia s dynamickejším rozlíšením a kompaktnejším prenosom než samostatné classic histogram bucket series, pri kompatibilnej pipeline. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Notification — Alertmanager

Receiver-specific správa vytvorená z jednej alert group podľa routing, timing, muting a template pravidiel. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Notification template — Alertmanager

Go template používaný na renderovanie notification title, body, links a receiver-specific payloadu. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Panel inspector

Grafana nástroj na zobrazenie raw data, query requests, statistics, transformations a panel JSON pri diagnostike. Pozri [Grafana](docs/12-observability/grafana.md).

## Pending alert

Alert, ktorého condition je splnená, ale ešte neuplynula nakonfigurovaná `for` doba potrebná na firing state. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Prometheus

Metrics monitoring a alerting systém založený na multidimenzionálnych time series, pull-based scrapingu, local TSDB a PromQL. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Prometheus HA

Model viacerých nezávislých Prometheus replicas, ktoré samostatne scrape-ujú, ukladajú a vyhodnocujú rules; downstream vrstva musí riešiť deduplication. Pozri [Prometheus](docs/12-observability/prometheus.md).

## PromQL

Prometheus Query Language na selection, aggregation a výpočty nad time series. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Pushgateway

Prometheus ecosystem component na dočasné vystavenie service-level metrics short-lived batch jobov, ktoré nemôžu byť prirodzene scrape-nuté počas behu. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Query storm — Grafana

Nadmerný počet alebo objem backend queries spôsobený kombináciou panels, variables, repeats, users a krátkeho refresh intervalu. Pozri [Grafana](docs/12-observability/grafana.md).

## Range vector — PromQL

Množina time series so samples za definované časové okno, používaná napríklad ako vstup `rate()` alebo `increase()`. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Receiver — Alertmanager

Pomenovaná kolekcia notification integrations, napríklad webhook, email, chat alebo on-call služba. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Recording rule — Prometheus

Pravidelne vyhodnocovaná PromQL expression, ktorej výsledok sa uloží ako nová time series pre opakované alebo drahé výpočty. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Remote read — Prometheus

Mechanizmus, ktorým Prometheus query engine načíta series z kompatibilného externého storage receivera. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Remote write — Prometheus

Asynchrónny pipeline odosielajúci ingested samples cez queues, batching a retries do kompatibilného remote-storage receivera. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Repeat interval

Interval opakovania Alertmanager notification pre nezmenenú group, ktorá zostáva firing. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Repeating panel — Grafana

Panel alebo row dynamicky duplikovaný pre každú vybranú variable value; pri veľkom scope-e môže vytvoriť query storm. Pozri [Grafana](docs/12-observability/grafana.md).

## Resolved notification

Notification informujúca receiver, že predtým firing alert group alebo alert identity už nie je aktívna. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Route tree — Alertmanager

Hierarchická konfigurácia matchers, receivers, grouping a timing, podľa ktorej Alertmanager spracuje každý alert. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Sample — Prometheus

Timestampovaná hodnota patriaca ku konkrétnej Prometheus time series. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Scrape — Prometheus

Periodické HTTP načítanie metrics endpointu targetu, validácia samples a ich ingestion do Prometheus TSDB. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Series churn

Rýchle vytváranie a zanikanie time series, typicky pre nestabilné alebo vysokokardinalitné labels, ktoré zvyšuje TSDB a query overhead. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Service discovery — Prometheus

Mechanizmus dynamicky vytvárajúci potenciálne scrape targets a dočasné metadata labels z Kubernetes, cloud, Consul, DNS alebo iného source-u. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Silence — Alertmanager

Časovo ohraničené muting pravidlo nad alert label matchers vytvorené používateľom alebo API. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Staleness — Prometheus

Semantics, ktorou Prometheus prestane považovať starú sample za aktuálnu po zmiznutí targetu alebo series. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Target — Prometheus

Network endpoint a associated labels, ktorý Prometheus plánuje pravidelne scrape-ovať. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Target relabeling

Prometheus relabeling fáza pred scrape-nutím, ktorá filtruje targets a mapuje discovery metadata na address, path, scheme a stabilné target labels. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Time series — Prometheus

Prúd timestampovaných samples identifikovaný metric name a úplným label setom. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Transformation — Grafana

Operácia aplikovaná na query results po ich získaní z data source-u na úpravu data frame-u pred vizualizáciou. Pozri [Grafana](docs/12-observability/grafana.md).

## Vector matching — PromQL

Pravidlá spájania series pri binary operation podľa labels vrátane `on`, `ignoring`, `group_left` a `group_right`. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Visualization — Grafana

Prezentačný model panelu, napríklad time series, stat, table, heatmap alebo state timeline, zvolený podľa data shape-u a operational otázky. Pozri [Grafana](docs/12-observability/grafana.md).

## WAL — Prometheus

Write-Ahead Log uchovávajúci nedávne ingested samples a metadata pre recovery aktívneho TSDB head state-u po reštarte. Pozri [Prometheus](docs/12-observability/prometheus.md).
