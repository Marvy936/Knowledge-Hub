# Grafana

Grafana je query, visualization, investigation a alerting vrstva nad externými telemetry backends. Typicky nevlastní autoritatívne metrics, logs ani traces. Vlastní však dôležitú časť operational contractu: ktorý backend a tenant sa queryujú, aký exact query result vznikol, ako sa výsledok transformoval a zobrazil, kto ho smie vidieť a či z neho vznikol správny operational decision.

Preto zelený panel nie je dôkazom zdravého systému. Je to výsledok konkrétnej data-source identity, query, time range-u, transformation chainu, field configuration, dashboard revision a viewer contextu.

## 1. Dominantný model

```text
business alebo operational otázka
→ exact Grafana subject
→ data-source, tenant a authorization boundary
→ raw backend query
→ query response a data frame
→ expressions a transformations
→ reducer, field unit, mappings a overrides
→ panel/dashboard/Explore representation
→ viewer alebo alerting consumer
→ operational decision
→ backend, user-outcome a forbidden-path validation
```

Grafana je užitočná iba vtedy, keď sa dá spätne prejsť od rozhodnutia až k autoritatívnemu backend recordu a exact loaded dashboard generation.

## 2. Exact Grafana subject

Pre Atlas Payments používame subject `GRAF-PAY-45`:

```text
business capability: final payment settlement
service: provider-adapter
environment: production
region: eu-central-1
cohort: enterprise merchants
Grafana organization: atlas-prod
folder UID: payments-prod
dashboard UID: settlement-overview
panel UID: final-error-ratio
data-source UID: prometheus-prod-eu1
dashboard source generation: Git commit / generated artifact
loaded dashboard version: Grafana database revision
query generation: PromQL + variables + time range + step
transformation generation: expressions/transformations/reducer
field generation: unit, thresholds, mappings, overrides
alert ownership: Prometheus/Alertmanager alebo Grafana-managed
viewer identity a permission scope
```

Názov dashboardu nestačí. Rovnaký title môže existovať v inom folderi, organization alebo environment-e. Pri incidente treba poznať UID, source generation aj runtime-loaded revision.

## 3. Štyri oddelené stavy

```text
backend obsahuje správne dáta
≠ Grafana poslala správny query
≠ panel interpretuje výsledok správne
≠ používateľ urobil správny decision
```

Podobne:

```text
query v paneli vyzerá správne
≠ variables boli interpolované správne
≠ transformation zachovala population
≠ field unit zodpovedá value semantics
≠ provisioned source a loaded dashboard sú rovnaké
```

Táto separácia je základ troubleshootingu.

## 4. Data-source boundary

Data source pozostáva z pluginu a runtime konfigurácie:

- stable UID a plugin type;
- backend endpoint;
- tenant, organization alebo project header;
- authentication a TLS;
- timeout, query limits a default settings;
- server-side proxy alebo browser access model;
- service identity a audit model.

Dashboard permission nechráni automaticky backend data. Používateľ s accessom k data source-u môže podľa permissions použiť Explore alebo iný dashboard a vytvoriť vlastný query. Tenant isolation preto musí byť presadená aj v backend-e alebo v dôveryhodnej Grafana authorization vrstve, nie iba skrytím panelu.

Test z používateľského browsera môže byť irelevantný, keď Grafana vykonáva query server-side. Diagnostický test sa musí vykonať z rovnakej network, identity a tenant boundary ako Grafana server.

## 5. Query-to-frame lifecycle

Panel môže obsahovať jednu alebo viac backend queries. Výsledky Grafana normalizuje do data frames a fields.

```text
query text + variables + time range + step
→ request cez data-source plugin
→ backend response
→ Grafana data frame
→ expression alebo transformation
→ field configuration
→ visualization
```

Panel Inspector je kľúčový observation point. Umožňuje porovnať request, raw response, transformed frame, statistics a panel JSON. Pri rozdiele medzi backendom a panelom sa nezačína farbou, ale raw query resultom.

## 6. Variables a population identity

Variables umožňujú reusable dashboards, ale menia exact query population.

```text
environment
→ region
→ service
→ operation
→ cohort
```

Riziká:

- stale hidden default;
- URL parameter prepíše očakávanú hodnotu;
- `All` expanduje broad regex;
- chained variables spustia query storm;
- nesprávne escaping zmení PromQL, LogQL alebo SQL semantics;
- variable vyberie inú release, AZ alebo tenant population.

Variables nie sú authorization mechanism. Každý critical dashboard potrebuje fixtures pre intended aj forbidden values.

## 7. Expressions, transformations a field semantics

Transformations sa aplikujú po získaní dát. Môžu joinovať, filtrovať, redukovať, premenovávať alebo vypočítať fields. Sú vhodné na presentation shaping, ale môžu vytvoriť nový derived signal, ktorý už nemá rovnakú autoritu ako backend query.

Pre každý critical panel eviduj:

- source queries;
- expression order;
- transformation order;
- join keys a missing-data behavior;
- reducer, napríklad `last`, `lastNotNull`, `mean` alebo `max`;
- unit semantics;
- threshold a value mappings;
- panel overrides.

Príklad ratio:

```text
backend value = 0.074
```

Ak ide o fraction `0–1`, unit musí interpretovať `0.074` ako `7.4 %`. Unit určená pre už škálovaný rozsah `0–100` zobrazí `0.074 %`. Source data sa nezmenili, ale operational meaning áno.

Červený alebo zelený threshold nie je alert rule ani SLO. Je to presentation state, kým nemá ownera, time-window semantics, action a samostatne testovaný notification path.

## 8. Dashboard a investigation hierarchy

Dashboard má odpovedať na preddefinovanú otázku. Explore slúži na ad hoc investigation.

Odporúčaná hierarchy:

```text
service health a SLO
→ Golden Signals a business outcomes
→ operation/cohort/version breakdown
→ dependency RED
→ USE resource evidence
→ logs, traces, profiles a change events
```

Links a correlations majú preniesť exact time range, environment, region, service a podľa potreby trace alebo correlation ID. Link bez zachovania scope-u môže respondera poslať do iného incident population.

## 9. Provisioning a ownership

Dashboard môže byť spravovaný cez:

- file provisioning;
- Terraform;
- Grafana Operator alebo iný controller;
- HTTP/API workflow;
- generated JSON/Jsonnet;
- UI.

Pre jeden dashboard musí existovať jeden authoritative writer.

```text
source artifact
→ validation a rendering
→ provisioning provider/controller
→ Grafana database revision
→ loaded dashboard read-back
→ known-query render test
```

UI edit provisionovaného dashboardu nie je durable oprava, ak reconciliation neskôr znovu načíta chybný source artifact. Acceptance vyžaduje opravu autority a runtime read-back.

Pri alerting automatizácii treba používať API contract podporovaný konkrétnou Grafana verziou. Legacy Alerting Provisioning HTTP API je v aktuálnej dokumentácii deprecated; nové implementácie majú overiť Grafana App Platform alerting APIs, ich version a provenance semantics.

## 10. Grafana Alerting boundary

Grafana-managed alerts a data-source-managed alerts sú samostatné control planes.

### Grafana-managed

Grafana vykonáva query, expressions, evaluation, alert-instance generation a notification policy.

### Data-source-managed

Rule žije a vyhodnocuje sa v Prometheus, Loki alebo inom ruler systéme; Grafana poskytuje management a visualization integration.

Pre každý alert definuj jediného ownera:

```text
rule source
→ evaluation engine
→ alert identity
→ notification policy
→ receiver
→ incident closure
```

Panel a alert nemusia používať rovnaký time range, transformation ani execution engine. Vizuálne podobný panel preto nie je dôkazom totožnej alert condition.

## 11. Security, HA a recovery

Grafana HA typicky potrebuje viac stateless instances, podporovanú shared SQL database, rovnaké encryption secrets, plugins, configuration, auth a alerting HA model. SQLite nie je shared multi-instance database.

Grafana HA nerieši HA data sources. Prometheus, Loki, Tempo, Elasticsearch/OpenSearch a ďalšie backends majú vlastné failure a recovery boundaries.

Chráň:

- data-source credentials;
- internal database;
- service accounts a API tokens;
- dashboards, alerting resources a provisioning sources;
- plugins;
- externally shared dashboards a snapshots;
- query audit a tenant context.

Provisioning z Git pomáha rekonštruovať dashboards a časť configu, ale nenahrádza backup internal database, users, teams, permissions, annotations, silences a ďalší runtime state.

## 12. Query budget a self-observability

Dashboard load približne rastie ako:

```text
panels
× queries per panel
× repeated variable values
× viewers
× refresh frequency
× backend series/document fan-out
```

Sleduj:

- Grafana HTTP rate/errors/latency;
- data-source query duration a failures;
- internal DB pool a latency;
- dashboard load time;
- alert evaluation a notification failures;
- provisioning a plugin errors;
- authentication failures;
- backend query concurrency.

Critical canary:

```text
login
→ open exact dashboard UID
→ load known variables a time range
→ execute known backend query
→ verify expected raw value
→ verify rendered value/unit
→ open drilldown/Explore
```

## 13. Worked failure: backend ukazuje 7.4 %, dashboard 0.074 %

### Symptóm

Po release `7.21.0` rastú enterprise final-settlement failures. Prometheus a incident query ukazujú error ratio `0.074`, teda `7.4 %`. Grafana service overview však zobrazuje `0.074 %`, panel zostáva zelený a page nevznikne, pretože alert je stále vlastnený Prometheusom, ale on-call používa panel ako manuálny severity gate.

### Exact subject

```text
subject: GRAF-PAY-45
dashboard UID: settlement-overview
panel UID: final-error-ratio
data source UID: prometheus-prod-eu1
source revision: DASH-GEN-212
loaded Grafana revision: 481
variable cohort: enterprise
raw PromQL result: 0.074
configured unit: percent 0–100
required unit: percent fraction 0–1
```

### Competing hypotheses

1. Prometheus query používa nesprávny numerator alebo denominator;
2. Grafana variable vybrala standard cohort;
3. panel time range alebo step vynechal incident;
4. transformation zmenila hodnotu;
5. field unit nesprávne interpretuje ratio;
6. cache alebo stale dashboard revision zobrazuje starý stav;
7. UI a provisioned source sa rozchádzajú.

### Discriminating evidence

```text
Prometheus expression browser: 0.074
Grafana Query Inspector request: rovnaký PromQL a cohort
Grafana raw data frame: 0.074
transformations: bez numerickej zmeny
field unit: percent 0–100
panel display: 0.074 %
Git source DASH-GEN-212: chybná unit
UI hotfix: správna unit, ale provisioning ju o 60 s prepíše
```

Mechanizmus:

```text
autoritatívny ratio 0.074
→ query a frame zostanú správne
→ field unit očakáva už škálovanú hodnotu 0–100
→ Grafana neprenásobí fraction stokrát
→ panel zobrazí 0.074 %
→ threshold zostane green
→ responder podhodnotí incident
→ UI oprava sa stratí pri reconciliation
```

### Containment

- prestať používať panel ako severity autoritu;
- pripojiť on-call priamo na Prometheus SLO/error-budget query;
- zastaviť ďalší dashboard provisioning rollout;
- zachovať panel JSON, Query Inspector output, source artifact a provisioning logs;
- neprepínať data source ani nevytvárať nový duplicate dashboard.

### Authoritative recovery

1. opraviť unit a threshold v source generatori;
2. pridať fixture `0.074 → 7.4 %`;
3. vygenerovať immutable dashboard artifact `DASH-GEN-213`;
4. validovať UID, data-source UID, variables a panel JSON;
5. provisionovať canary organization/folder;
6. read-backnúť loaded dashboard revision;
7. vykonať known-query render canary;
8. rozšíriť rollout a odstrániť dočasný manual gate.

### Acceptance verdict

Recovery je prijatá, keď:

- backend, raw frame a rendered value sú semanticky zhodné;
- `0.074` sa zobrazuje ako `7.4 %`;
- threshold a legend používajú správnu unit;
- enterprise aj standard cohort fixtures fungujú;
- UI edit už nie je potrebný a druhý reconciliation zachová opravu;
- dashboard link prenesie správny time range a cohort;
- forbidden cross-tenant query zlyhá;
- Prometheus alerting path zostane jediným ownerom page condition.

## 14. Troubleshooting model

### No data

```text
backend occurrence existuje?
→ data source/tenant/auth?
→ variables a time range?
→ exact query request?
→ raw backend response?
→ frame/expression/transformation?
→ field filtering?
→ source ingestion/staleness/retention?
```

No data nie je nula.

### Zlá hodnota

```text
backend direct query
→ Grafana request
→ raw frame
→ transformation chain
→ reducer
→ unit a mapping
→ overrides
→ timezone/cache
```

### Provisioning drift

```text
authoritative writer
→ source generation
→ stable UID/folder
→ provider/controller logs
→ loaded revision
→ UI mutation
→ prune/delete semantics
```

### Pomalý dashboard

```text
panel a variable query count
→ query fan-out a time range
→ backend latency/cardinality
→ transformations/browser render
→ concurrent refresh
→ recording/caching/drilldown opportunity
```

## 15. Anti-patterny

### Dashboard ako source of truth

Autoritatívny je telemetry a query contract, nie pixel alebo farba.

### Variables ako authorization

Query možno zmeniť cez Explore alebo iný client.

### UI hotfix provisionovaného dashboardu

Reconciliation ho prepíše a incident sa vráti.

### Transformations ako skrytý business model

Complex client-side calculation sa ťažko testuje a nemusí byť dostupný alert engine-u.

### Alerting v dvoch control planes bez ownershipu

Vzniknú odlišné conditions, duplicates a nejasný receiver.

### Broad data-source credential

Grafana service identity môže prekročiť user alebo tenant boundary.

## 16. Kontrolné otázky

1. Čo tvorí exact Grafana subject?
2. Prečo dashboard nie je source of truth?
3. Aký je rozdiel medzi raw query resultom, data frame-om a rendered value?
4. Ako variables menia population a query cost?
5. Prečo unit configuration môže zmeniť operational meaning bez zmeny dát?
6. Kedy patrí calculation do backendu alebo recording rule namiesto transformation?
7. Ako sa líši dashboard a Explore?
8. Čo znamená authoritative writer pri provisioningu?
9. Ako sa líši Grafana-managed a data-source-managed alerting?
10. Čo Grafana HA rieši a čo nerieši?
11. Ako diagnostikuješ no-data oproti zero?
12. Ako overíš dashboard end-to-end po reconciliation?

## Glossary impact

Relevantné pojmy: Grafana subject, data-source identity, query generation, data frame, transformation generation, field-semantics contract, rendered-value verdict, dashboard source generation, loaded dashboard revision, authoritative dashboard writer, Grafana investigation path, alerting control-plane ownership, dashboard query budget, dashboard render canary a Grafana acceptance verdict.

## Primárne zdroje

- [Grafana introduction](https://grafana.com/docs/grafana/latest/introduction/)
- [Grafana data sources](https://grafana.com/docs/grafana/latest/datasources/concepts/)
- [Panels and visualizations](https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/)
- [Panel Inspector](https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/panel-inspector/)
- [Explore](https://grafana.com/docs/grafana/latest/visualizations/explore/)
- [Provision Grafana](https://grafana.com/docs/grafana/latest/administration/provisioning/)
- [Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/)
- [Alerting Provisioning HTTP API](https://grafana.com/docs/grafana/latest/developer-resources/api-reference/http-api/api-legacy/alerting_provisioning/)
- [Grafana API structure](https://grafana.com/docs/grafana/latest/developer-resources/api-reference/http-api/apis/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Alertmanager](alertmanager.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Loki →](loki.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
