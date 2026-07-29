# Prometheus

Prometheus je metrics monitoring a alerting systém založený na multidimenzionálnych time series, pravidelnom scrapingu a PromQL. Jeho operational contract nie je „target je green“. Prometheus vytvára reťaz od expected targetu cez exact post-relabel sample set, local TSDB state a rule evaluation až po alert state. Každá boundary môže zmeniť alebo stratiť evidence.

Prometheus nie je log store, trace backend, durable event bus ani automaticky globálny long-term metrics cluster. Jeho lokálny model je zámerne transparentný: targets sa scrape-ujú, samples sa ukladajú do lokálnej TSDB a rules sa vyhodnocujú nad queryovateľným lokálnym stavom.

## 1. Dominantný lifecycle

```text
business/operational measurement intent
→ versionovaný metric a label contract
→ expected target/discovery generation
→ target relabeling a scrape eligibility
→ HTTP scrape attempt
→ exposition parsing a sample validation
→ metric relabeling
→ exact post-relabel sample set
→ WAL a TSDB head/block state
→ staleness a query-time selection
→ PromQL expression
→ recording-rule generation
→ alerting-rule inactive/pending/firing/resolved state
→ Alertmanager delivery subject
→ local/remote/read-back validation a lifecycle closure
```

Prometheus troubleshooting musí určiť, na ktorej boundary sa očakávaná measurement stratila alebo zmenila.

## 2. Exact Prometheus subject

Pre Atlas Payments používame:

```text
Prometheus subject: PROM-PAY-44
observability subject: OBS-PAY-44
service/release: provider-adapter 7.20.0
cluster/namespace: prod-eu-1 / payments
Prometheus replica: prometheus-prod-eu-1-a
configuration generation: PROM-CFG-118
scrape job: payments-provider-adapter
scrape interval/timeout: 30 s / 10 s
metric contract: provider_pool_connections{state}
critical series:
  state="active"
  state="idle"
  state="waiters"
capacity series: provider_pool_limit
recording-rule generation: PAY-RULES-44
alert rule: SettlementProviderPoolSaturated
remote-write generation: RW-PROD-9
analysis window: 2026-07-29T08:10Z–08:35Z
```

Subject zahŕňa producer, config, target, post-relabel labels, TSDB replica, rule generation a query window. Rovnaký metric name v inom clusteri, po inom relabelingu alebo na inej replica nie je automaticky ten istý evidence subject.

## 3. Measurement contract pred scrape konfiguráciou

Metric contract musí určiť:

- čo je measurement a v akej base unit;
- counter, gauge alebo histogram semantics;
- observation a reset boundary;
- bounded labels a ich meanings;
- producer/resource identity;
- expected scrape interval a freshness;
- dashboards, recording rules, alerts a SLO consumers;
- compatibility a migration policy.

Príklad:

```text
provider_pool_connections{state="waiters"}
```

musí znamenať aktuálny počet settlement workers čakajúcich na connection v konkrétnom process-local provider poole. Ak sa zmení na cumulative počet wait events bez rename-u, queries zostanú syntakticky validné a semanticky nesprávne.

## 4. Expected targets a discovery generation

Service discovery odpovedá:

```text
ktoré potential endpoints existujú a aké metadata o nich platforma pozná?
```

Target relabeling následne rozhoduje:

```text
ktoré endpoints sú eligible na scrape
→ aká address/scheme/path sa použije
→ ktoré stabilné target labels zostanú
```

Target identity preto vzniká až po relabelingu. Discovery object, Kubernetes Pod a final Prometheus target nie sú rovnaký state.

### Target relabeling

`relabel_configs` sa vykonáva pred scrape. Používa sa na:

- keep/drop targetov;
- address, scheme alebo metrics path;
- mapovanie discovery metadata na stabilné labels;
- environment/service/cluster identity;
- sharding.

Broad mapping všetkých Kubernetes labels alebo annotations môže preniesť ephemeral a unbounded values do každej series.

## 5. Scrape attempt a `up`

Prometheus vykoná HTTP request na metrics endpoint, parsuje exposition, validuje samples a labels a až potom ingestuje prijaté dáta.

```promql
up{job="payments-provider-adapter"}
```

- `1` znamená, že konkrétny scrape attempt prebehol úspešne;
- `0` znamená scrape failure.

`up == 1` nepreukazuje:

- business health;
- prítomnosť každej očakávanej metric;
- správne label semantics;
- zachovanie metric po relabelingu;
- úspech recording/alerting rule;
- remote-write ingestion;
- receiver notification.

Scrape môže byť green, hoci kritická series je producerom vynechaná alebo metric relabelingom zahodená.

Relevantné scrape evidence:

```promql
up
scrape_duration_seconds
scrape_samples_scraped
scrape_samples_post_metric_relabeling
scrape_series_added
```

Rozdiel medzi scraped a post-relabel samples je diagnostická boundary, nie iba cost údaj.

## 6. Metric relabeling a post-relabel sample set

`metric_relabel_configs` sa aplikuje po úspešnom scrape a pred ingestion do local TSDB.

Môže:

- dropnúť metrics alebo series;
- odstrániť rizikový label;
- normalizovať values;
- znížiť stored a remote-written cardinality.

Metric relabeling už nezníži network a parse cost endpointu. Mení však authoritative local sample set, z ktorého vychádzajú PromQL, rules a remote write.

Pre kritickú zmenu treba poznať:

```text
raw exposition set
→ post-target-label set
→ post-metric-relabel set
→ ingested TSDB set
```

Cost rule bez dependency auditu môže ticho odstrániť SLI numerator, saturation signal alebo alert input.

## 7. Time-series identity a cardinality

Jedna Prometheus series je identifikovaná:

```text
metric name
+ úplná množina label names a values
```

Každá odlišná kombinácia vytvára samostatnú series. Labels preto reprezentujú bounded aggregation dimensions, nie unikátne events.

Nevhodné labels:

- request, trace alebo user ID;
- raw URL s dynamickým segmentom;
- exception message;
- timestamp;
- Pod UID, ak consumer potrebuje logical service a retention nemá churn model.

Cardinality ovplyvňuje head memory, WAL, blocks, queries, rule evaluation aj remote write. Zmena label contractu je production schema migration.

## 8. Metric types a distributions

### Counter

Monotónny počet, ktorý môže resetnúť s process lifecycle-om. Analyzuje sa cez `rate()` alebo `increase()`.

```promql
rate(settlement_operations_total[5m])
```

### Gauge

Aktuálna hodnota, ktorá môže rásť aj klesať, napríklad pool waiters alebo queue depth.

### Classic histogram

Exportuje cumulative `_bucket{le}`, `_count` a `_sum`. Umožňuje server-side agregáciu a threshold/quantile queries.

### Native histogram

Prometheus podporuje native histograms ako stable feature od verzie `3.8.0`. Sú first-class histogram samples, ale adoption stále potrebuje compatible client library, scrape/storage, PromQL, remote backend, dashboards a migration contract.

### Summary

Client-side quantiles sa vo všeobecnosti nedajú správne agregovať naprieč instances. Pre service-wide latency býva histogram vhodnejší.

Histogram buckets alebo native schema musia zodpovedať SLO thresholdom a reálnej distribution. Samotné p95 bez population a volume contractu nie je kompletný SLI.

## 9. Local TSDB state

Local storage obsahuje:

```text
incoming samples
→ WAL
→ in-memory head
→ immutable blocks
→ compaction
→ retention deletion
```

### WAL

WAL podporuje recovery nedávneho head state-u po reštarte. Nie je business backup ani multi-site DR.

Riziká:

- disk full alebo corruption;
- dlhý WAL replay;
- cardinality/churn explosion;
- compaction failure;
- retention väčšia než capacity.

### Head a blocks

Recent active series žijú v head blocku. Staršie dáta sú v immutable blocks. Query môže prechádzať oboma vrstvami. Disk a memory pressure preto závisia od active series, churn, samples aj query patternu.

### Staleness

Keď target alebo series zmizne, Prometheus musí zabrániť tomu, aby posledná stará hodnota vyzerala ako current.

Missing series môže znamenať:

- producer už metric neemituje;
- target zmizol alebo scrape zlyhal;
- label set sa zmenil;
- metric bola relabelingom dropnutá;
- series je stale;
- selector alebo time range nesedí;
- retention/compaction odstránila data.

`absent()` alebo no-data alert musí mať expected-series contract. Inak nevie odlíšiť zdravú neprítomnosť od evidence failure.

## 10. PromQL a population correctness

PromQL selector vyberá series. Functions a aggregations z nich vytvoria nový query result. Query correctness preto závisí od identity oboch populations.

Error ratio:

```promql
sum by (service) (
  rate(settlement_operations_total{outcome="failed"}[5m])
)
/
sum by (service) (
  rate(settlement_operations_total[5m])
)
```

Numerator a denominator musia používať rovnakú operation, cohort a logical-versus-attempt semantics.

### Vector matching

Binary operations potrebujú jednoznačný label relation. `on`, `ignoring`, `group_left` a `group_right` nemenia nesprávny data model na správny. Many-to-many ambiguity často znamená chýbajúcu agregáciu alebo nejasnú identity.

### Rate window

Range window musí obsahovať dostatok samples a byť dlhší než krátky scrape jitter. Príliš krátke window pri dlhom scrape intervale vytvára unstable alebo absent result.

## 11. Recording-rule generation

Recording rule materializuje PromQL result ako novú series.

Použitie:

- štandardné RED/Golden-Signal rates;
- SLI numerators a denominators;
- drahé stabilné queries;
- hierarchické aggregations.

Recording rule je derived signal. Potrebuje:

- versionovaný expression;
- input series inventory;
- output metric/label contract;
- evaluation interval;
- fixture tests;
- migration/dual-read window;
- ownera.

Ak input label zmizne, rule môže produkovať empty vector bez syntax erroru. `promtool check rules` overí syntax a vybrané tests, nie automaticky production population completeness.

## 12. Alerting-rule state

Alerting rule vytvára monitoring condition state:

```text
inactive
→ pending počas `for`
→ firing
→ resolved po zániku condition
```

Labels tvoria alert identity a routing context. Dynamic values, error text a current metric value patria do annotations.

Rule acceptance vyžaduje:

- expression vracia expected series;
- evaluation je fresh a úspešná;
- `for` zodpovedá failure dynamics;
- no-data policy je explicitná;
- labels sú stable a bounded;
- Alertmanager discovery/delivery funguje;
- resolved path je overený.

## 13. Remote write, local truth a global views

Remote write číta samples z local WAL-derived pipeline a odosiela ich do kompatibilného receivera cez queues, shards, batching a retries.

Môže vzniknúť:

```text
local Prometheus má current samples a firing rule
→ remote write má backlog
→ central dashboard je stale
```

alebo:

```text
local metric relabeling series dropne
→ local TSDB ju nikdy nemá
→ remote write ju tiež nemôže odoslať
```

Sleduj pending samples, failed/retried/dropped samples, oldest unsent timestamp a receiver throttling. Remote-write success nepreukazuje correctness metric contractu. Remote backend nie je automaticky authority pre local rule state.

Federation a global query layers môžu poskytovať cross-cluster views, deduplication a long-term storage. Prometheus replicas však zostávajú nezávislé local TSDB a rule evaluators.

## 14. High availability

Bežný HA model spúšťa viac nezávislých Prometheus replicas s rovnakým scrape a rule intentom.

Každá replika:

- samostatne objavuje a scrape-uje targets;
- má vlastnú local TSDB;
- samostatne vyhodnocuje rules;
- posiela alerts všetkým Alertmanager replicas.

HA replicas môžu mať mierne odlišné scrape timestamps a samples. Downstream global layer potrebuje replica identity a deduplication. Load balancer pred jednou local TSDB nevytvára shared-state Prometheus cluster.

## 15. Worked failure: `up=1`, ale pool saturation signal zmizol

### Symptóm

Enterprise settlement latency a pool wait rastú, ale Prometheus dashboard neukazuje žiadne `provider_pool_*` series. Všetkých 24 targets má `up == 1`. Alert `SettlementProviderPoolSaturated` je inactive a central remote dashboard ukazuje no-data.

### Competing hypotheses

1. application metric nikdy neemituje;
2. iba release `7.20.0` používa iný metric name;
3. target discovery alebo scrape path je nesprávny;
4. exposition parser metric odmieta;
5. metric relabeling ju dropuje;
6. local TSDB alebo query selector používa iné labels;
7. recording rule zlyháva;
8. remote-write backlog skryl current local data.

### Discriminating observations

```text
raw /metrics na affected task:
  provider_pool_connections{state="waiters"} 317
  provider_pool_limit 8

Prometheus target:
  up = 1
  scrape_samples_scraped = 1 842
  scrape_samples_post_metric_relabeling = 1 506

local expression browser:
  provider_pool_connections = empty

recording-rule output:
  payment:provider_pool_wait_ratio = empty

remote backend:
  rovnaká series chýba
```

Config generation `PROM-CFG-118` obsahovala cost rule:

```yaml
metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'provider_.*'
    action: drop
```

Rule mala odstrániť debug metrics starého provider SDK. Broad regex však odstránil aj authoritative pool saturation metrics.

Mechanizmus:

```text
producer emituje správne samples
→ scrape a exposition parsing uspejú
→ `up` zostane 1
→ metric relabeling samples zahodí
→ local TSDB ich nikdy neuloží
→ recording a alerting rules majú empty input
→ remote write ich nemôže odoslať
→ dashboard a alert sú false no-data
```

### Containment

- zastaviť rollout `PROM-CFG-118`;
- zachovať raw exposition, scrape counters, effective config, rule state a remote-write evidence;
- nesprávne neinterpretovať empty series ako zero waiters;
- použiť business SLI a black-box settlement evidence na incident response;
- nezvyšovať scrape interval ani retention, pretože problém je pre-ingestion drop.

### Authoritative recovery

1. nahradiť broad regex explicitným allow/drop contractom;
2. canary-nuť Prometheus config na jednej replica;
3. porovnať raw a post-relabel sample inventory;
4. overiť local query a recording-rule output;
5. vynútiť controlled pool saturation fixture;
6. overiť alert pending/firing a Alertmanager receive path;
7. rozšíriť config na druhú repliku;
8. overiť remote backend read-back a cardinality budget.

### Prometheus acceptance verdict

Recovery je prijatá, keď:

- expected target a exact series existujú na oboch replicas;
- post-relabel sample set obsahuje pool metrics;
- rule output používa správny task/service denominator;
- controlled saturation vytvorí firing alert;
- zero waiters a absent series sú rozlíšiteľné;
- remote dashboard dobehne bez duplicate/label conflictu;
- unbounded debug metrics zostanú zakázané;
- druhý config reload a task replacement zachovajú measurement.

## 16. Native-histogram compatibility gate

Native histograms sú stable v Prometheus od `3.8.0`, ale migration nie je iba zapnutie producer feature.

```text
client-library generation
→ exposition format
→ scrape acceptance
→ local storage/query
→ recording/alerting rules
→ remote write/backend
→ dashboard/SLO comparison
```

Pred cutoverom over:

- classic/native dual exposure alebo migration mode;
- bucket/quantile query equivalence;
- remote receiver support;
- rule a dashboard functions;
- cardinality/storage zmenu;
- rollback po ingestovaní nového sample type-u.

## 17. Self-monitoring a canaries

Prometheus musí monitorovať:

- target discovery a `up`;
- scrape duration/sample counts/failures;
- active head series a churn;
- WAL, compaction a disk;
- query latency/concurrency;
- rule evaluation failures a missed iterations;
- config reload success;
- remote-write queue age a drops;
- replica divergence.

Kritický pipeline potrebuje canary:

```text
known producer metric
→ expected target
→ post-relabel series
→ recording rule
→ controlled alert
→ Alertmanager receive
```

External black-box check má zistiť aj úplný výpadok samotného Prometheus systému.

## 18. Troubleshooting paths

### Target down

```text
discovery object
→ target relabel result
→ /targets error
→ DNS/address/route
→ TLS/auth
→ path/port
→ exposition validity
→ timeout/sample limits
```

Test vykonaj z rovnakej network boundary ako Prometheus.

### Missing series

```text
raw endpoint
→ scrape counters
→ metric relabel result
→ local TSDB selector
→ labels/staleness
→ recording rule
→ remote-write/backend
```

### High memory alebo disk

```text
active series
→ new-series rate a churn
→ high-cardinality labels
→ duplicate targets/histograms
→ WAL/compaction
→ retention
→ remote-write backlog
→ expensive queries/rules
```

### Slow PromQL

Najprv zmenši selector a zmeraj series fan-out. Over regex, range, vector matching, histogram buckets, subqueries a dashboard concurrency. Recording rule má materializovať stabilný správny model, nie maskovať nesprávnu cardinality.

## 19. Anti-patterny

### `up == 1` ako service verdict

Preukazuje scrape attempt, nie business outcome ani completeness metric setu.

### Metric relabeling bez dependency inventory

Cost optimization môže ticho odstrániť SLI a alert inputs.

### Dynamic identifiers v labels

Request/user/trace identity destabilizuje TSDB a queries.

### Summary quantiles agregované naprieč instances

Client-side quantiles nemajú všeobecne správnu service-wide agregáciu.

### Remote dashboard ako jediná truth

Backlog alebo deduplication môže vytvoriť rozdiel oproti local rule state-u.

### Jedna replika s lokálnym diskom ako HA/DR

Nemá independent scrape, rule ani recovery boundary.

### Config syntax check ako runtime acceptance

Nevie preukázať expected targets, post-relabel series, rule population ani notification path.

## 20. Kontrolné otázky

1. Čo tvorí exact Prometheus subject?
2. Aký je rozdiel medzi discovery objectom a final targetom?
3. Čo `up == 1` preukazuje a čo nie?
4. Kde sa líši target a metric relabeling?
5. Čo je post-relabel sample set?
6. Ako metric name a labels definujú series identity?
7. Ako WAL, head, blocks a staleness menia queryovateľný state?
8. Prečo recording rule potrebuje input inventory a fixture tests?
9. Ako local rule truth môže divergrovať od remote dashboardu?
10. Aké compatibility gates potrebuje native-histogram migration?
11. Prečo Prometheus HA nie je shared-state cluster?
12. Ako overíš celý metric-to-alert path po config reload-e?

## Glossary impact

Relevantné pojmy: Prometheus subject, metric-contract generation, expected target generation, target eligibility, scrape attempt, post-relabel sample set, local TSDB generation, staleness verdict, recording-rule generation, rule-input closure, local-versus-remote metrics state, native-histogram compatibility generation, Prometheus canary a Prometheus acceptance verdict.

## Primárne zdroje

- [Prometheus overview](https://prometheus.io/docs/introduction/overview/)
- [Prometheus data model](https://prometheus.io/docs/concepts/data_model/)
- [Prometheus metric types](https://prometheus.io/docs/concepts/metric_types/)
- [Native histograms](https://prometheus.io/docs/specs/native_histograms/)
- [Prometheus configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
- [PromQL basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Prometheus storage](https://prometheus.io/docs/prometheus/latest/storage/)
- [Recording rules](https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/)
- [Alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Remote write tuning](https://prometheus.io/docs/practices/remote_write/)
- [Federation](https://prometheus.io/docs/prometheus/latest/federation/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Golden Signals](golden-signals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Alertmanager →](alertmanager.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
