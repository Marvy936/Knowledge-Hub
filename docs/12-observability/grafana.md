# Grafana

Grafana je platforma na queryovanie, vizualizáciu, alerting a interaktívne skúmanie telemetry z externých data sources. Grafana typicky nie je primárnym source-of-truth metrics, logs alebo traces; pristupuje k systémom ako Prometheus, Loki, Elasticsearch/OpenSearch, Tempo, Jaeger, CloudWatch, SQL databázy a ďalšie plugins.

Dobrý Grafana deployment nie je zbierka farebných dashboardov. Je to riadená investigation vrstva, ktorá prepája user impact, SLO, deployment events, metrics, logs, traces, ownership a runbooks.

## 1. Mentálny model

```text
telemetry backends
→ Grafana data-source plugins
→ queries a expressions
→ transformations
→ fields a data frames
→ panels a visualizations
→ dashboards, Explore a correlations
→ Grafana-managed alerting alebo externý alerting path
→ users, teams a permissions
```

Grafana zobrazuje a spracúva výsledky queries. Ak source data, query alebo time range nie sú správne, vizualizácia nemôže vytvoriť správny záver.

## 2. Základné komponenty

Grafana deployment typicky obsahuje:

- Grafana server,
- configuration,
- internal database,
- data-source plugins,
- visualization a application plugins,
- dashboards a folders,
- users, teams a authentication,
- alerting resources,
- provisioning alebo API/IaC workflow,
- optional image renderer a reporting components podľa edície/use case-u.

Grafana server:

- autentizuje používateľov,
- autorizuje prístup ku Grafana resources,
- proxyuje alebo vykonáva data-source queries podľa plugin modelu,
- ukladá dashboards a metadata,
- renderuje UI,
- vyhodnocuje Grafana-managed alert rules,
- odosiela notifications podľa Grafana Alerting konfigurácie.

## 3. Data sources

Data source je plugin a configuration, ktorá Grafane umožňuje komunikovať s externým systémom.

Príklady:

- Prometheus pre metrics,
- Loki pre logs,
- Tempo alebo Jaeger pre traces,
- Elasticsearch/OpenSearch,
- CloudWatch,
- PostgreSQL/MySQL,
- TestData pre simulované dáta.

Data source configuration môže obsahovať:

- endpoint,
- access/proxy model,
- authentication,
- TLS,
- organization/tenant headers,
- default query settings,
- timeout,
- custom HTTP headers,
- derived fields alebo correlations,
- caching podľa edície a plugin capability.

### Data source nie je dashboard permission

Dashboard access a data-source access sú odlišné boundaries.

V Grafana OSS je potrebné dôkladne overiť organization a data-source security model; niektoré jemnejšie data-source permissions a RBAC capabilities sú dostupné iba v Enterprise alebo Cloud edíciách. Skrytie dashboardu samo osebe nemusí zabrániť používateľovi queryovať dostupný data source cez Explore.

## 4. Proxy a credentials

Grafana často vykonáva backend query server-side a používa data-source credentials uložené v konfigurácii.

Dôsledky:

- user nemusí mať priamy network access k backendu,
- Grafana service identity môže mať širší access než user,
- permissions musia byť presadzované v Grafane aj v backend/tenant modeli,
- query audit potrebuje rozlíšiť Grafana server od koncového používateľa,
- credentials musia byť šifrované, rotované a oddelené od dashboard JSON.

Nepoužívaj jeden broad admin token pre všetky data sources bez tenant a least-privilege modelu.

## 5. Dashboard

Dashboard je organizovaná množina panels, variables, annotations, links a time settings.

Mal by odpovedať na konkrétny operational účel:

- Je služba zdravá?
- Ktorý user journey degraduje?
- Ktorá dependency je problematická?
- Ako sa správa capacity?
- Čo sa zmenilo?
- Kam pokračovať pri vyšetrovaní?

Dashboard nemá byť inventory všetkých dostupných metrics.

## 6. Panel

Panel kombinuje:

- jednu alebo viac queries,
- data-source selection,
- optional expressions,
- transformations,
- field configuration,
- visualization,
- thresholds, links a descriptions.

Panel je prezentačná vrstva nad query výsledkom. Pri nesprávnom grafe najprv over raw query result.

### Panel inspector

Panel inspector pomáha zobraziť:

- raw data,
- query request a response,
- query statistics,
- transformed data,
- panel JSON.

Je základným nástrojom pri diagnostike „Grafana ukazuje inú hodnotu než backend“.

## 7. Data frames a fields

Grafana normalizuje query výsledky do data frames a fields.

Field môže obsahovať:

- values,
- type,
- name,
- labels,
- unit a display configuration,
- thresholds,
- mappings,
- links.

Rovnaká query môže byť vizualizovaná rôzne podľa field configu. Zmena unit alebo reduceru môže zmeniť interpretáciu bez zmeny source dát.

## 8. Vizualizácie

Výber vizualizácie musí zodpovedať otázke a data shape-u.

### Time series

Pre trends, rates, latency percentiles, utilization a SLO burn.

### Stat

Pre jednu aktuálnu alebo redukovanú hodnotu, napríklad current availability alebo queue depth.

### Gauge a bar gauge

Pre hodnotu voči explicitnému range-u. Nevhodné, ak maximum nie je zmysluplné alebo stabilné.

### Table

Pre multi-dimensional data, inventory, top-N, states a drilldown links.

### Heatmap

Pre distributions, histogram buckets a latency shape v čase.

### State timeline/status history

Pre categorical states, rollout alebo availability transitions.

### Logs a traces panels

Pre contextual drilldown, nie ako náhrada plného Explore workflowu.

## 9. Query options

Panel query options ovplyvňujú:

- time range,
- max data points,
- interval,
- relative time,
- time shift,
- query timeout podľa data source,
- instant oproti range query.

Grafana automaticky vypočítava intervaly podľa time range a panel resolution.

Pri Prometheus query sa často používa:

- `$__interval`,
- `$__rate_interval`,
- `$__range`,
- `$__range_s`.

Hard-coded príliš krátke `rate()` window môže zlyhať pri inom scrape intervale alebo dashboard time range-u.

## 10. Transformations

Transformations upravujú query výsledok po jeho získaní z data source.

Príklady:

- rename/organize fields,
- join alebo merge frames,
- filter fields,
- calculate field,
- reduce,
- group,
- labels-to-fields,
- rows-to-fields.

Transformations sú vhodné na presentation shaping, ale nie vždy na heavy data processing.

Riziká:

- veľký dataset sa najprv prenesie do Grafany,
- browser/server memory a latency,
- výsledok sa líši od source query semantics,
- alert rule nemusí používať totožnú frontend transformation,
- zložitý chain je ťažko testovateľný.

Preferuj agregáciu v data source alebo recording rules, ak ide o stabilný opakovaný výpočet.

## 11. Expressions

Grafana expressions môžu kombinovať query results a vykonávať math, reduce, resample alebo threshold operácie podľa podporovaného alerting/query modelu.

Použitie:

- normalizácia rôznych source queries,
- alert condition,
- jednoduchý derived signal,
- resampling časových radov.

Expression nenahrádza konzistentný data model. Pri kombinácii series over label matching, timestamps a missing-data behavior.

## 12. Variables

Variables parametrizujú dashboards.

Typy zahŕňajú:

- query variable,
- custom variable,
- text box,
- constant,
- data source,
- interval,
- ad hoc filters podľa data source.

Príklad hierarchy:

```text
environment
→ cluster
→ namespace
→ service
→ instance
```

### Výhody

- jeden dashboard pre viac environments/services,
- menej duplicitných dashboardov,
- reusable links,
- interactive drilldown.

### Riziká

- variable query vytvára veľkú cardinality,
- „All“ expanduje na tisíce values,
- regex alebo interpolation mení query semantics,
- text-box variable umožní broad alebo drahú query,
- chained variables spúšťajú mnoho queries,
- URL variable môže preniesť nečakanú hodnotu.

Variables nie sú authorization mechanism.

## 13. Variable interpolation

Grafana interpoluje variable pred odoslaním query data source-u.

Syntax môže zahŕňať:

```text
$service
${service}
${service:regex}
${service:raw}
```

Formatting závisí od data source-u.

`raw` alebo nesprávne escaping môže vytvoriť chybnú query alebo injection risk pri SQL a iných languages. Používaj data-source-aware formatting a bounded values.

## 14. Repeating panels a rows

Panel alebo row možno opakovať podľa variable values.

Použitie:

- rovnaký panel per Region,
- per service,
- per cluster.

Riziká:

- N variables × M panels × refresh rate vytvorí query storm,
- dashboard sa stane nečitateľný,
- panel count rastie podľa dynamického prostredia.

Pre veľké fleet použite aggregate overview a drilldown namiesto panelu pre každú instance.

## 15. Annotations

Annotations zobrazujú významné events v časových grafoch.

Príklady:

- deployment,
- configuration change,
- incident start/end,
- failover,
- feature-flag change,
- scaling event,
- maintenance.

Annotations môžu byť:

- uložené v Grafane,
- načítané query z externého data source-u.

Kvalitná annotation obsahuje:

- timestamp alebo interval,
- event type,
- service/environment,
- revision/change ID,
- owner,
- link na deployment alebo incident.

Annotations znižujú potrebu manuálne korelovať telemetry a change timeline.

## 16. Dashboard a panel links

Links vytvárajú investigation path:

```text
service overview
→ operation dashboard
→ Explore query
→ logs podľa service/trace ID
→ trace
→ infrastructure dashboard
→ runbook alebo incident
```

Prenášaj:

- time range,
- environment,
- service,
- region/cluster,
- trace alebo correlation ID podľa use case-u.

Link musí byť testovaný s URL encodingom a permissions.

## 17. Data links a correlations

Data link viaže konkrétnu field hodnotu na ďalší dashboard alebo external URL.

Príklady:

- trace ID → Tempo/Jaeger trace,
- Pod → Kubernetes dashboard,
- error code → runbook,
- deployment revision → Git commit,
- instance → host dashboard.

Correlations umožňujú prechádzať medzi data sources a signals podľa fields alebo query contextu.

Cieľ:

```text
metric exemplar alebo label
→ trace
→ logs
→ profile alebo deployment event
```

Correlation musí používať stabilné identifiers a bezpečné field handling.

## 18. Explore

Explore je ad hoc query a investigation workspace bez potreby najprv uložiť dashboard.

Použitie:

- iteratívne PromQL/LogQL/query building,
- split view a porovnanie,
- logs context,
- trace analysis,
- query inspector,
- prechod medzi metrics, logs a traces,
- incident investigation.

Dashboard odpovedá na preddefinované otázky. Explore je vhodnejší na nové alebo detailné otázky.

## 19. Dashboard hierarchy

Odporúčaná štruktúra:

### Executive alebo service health

- SLO a user outcomes,
- Golden Signals,
- active incidents,
- critical business volume.

### Service overview

- RED,
- dependencies,
- deployment markers,
- saturation.

### Component/resource dashboard

- USE,
- queues/pools,
- runtime,
- database/network/storage.

### Troubleshooting dashboard

- high-resolution details,
- per-instance/shard breakdown,
- links na logs/traces/profiles.

Jeden dashboard nemá obsahovať všetky vrstvy naraz.

## 20. Dashboard design principles

Každý dashboard má mať:

- jasný title a purpose,
- ownera,
- audience,
- default time range,
- template variables s bounded scope-om,
- units a legends,
- SLO alebo operational thresholds,
- annotations,
- drilldown links,
- version a lifecycle.

Panel description má vysvetliť:

- čo metric znamená,
- query scope,
- threshold semantics,
- čo urobiť pri abnormalite.

## 21. Units a value mappings

Grafana unit formatting nemení source hodnotu.

Chyby:

- bytes zobrazené ako bits,
- seconds zobrazené ako milliseconds bez konverzie,
- ratio `0–1` zobrazené ako percento `0–100` nesprávnym unitom,
- counter value zobrazený ako rate,
- timezone mismatch.

Value mappings sú vhodné pre categorical states, ale nemajú maskovať raw hodnotu pri diagnostike.

## 22. Thresholds

Thresholdy menia vizuálny stav panelu.

Nie sú automaticky alert rules ani SLO.

Threshold musí mať:

- business/operational dôvod,
- správnu unit,
- time-window semantics,
- ownera,
- action.

Červená farba bez alert alebo runbook contractu je iba vizuálna dekorácia.

## 23. Dashboard provisioning

Grafana môže provisionovať data sources a dashboards z files.

Výhody:

- version control,
- review,
- repeatable environments,
- disaster recovery,
- menší UI drift.

Pri provisionovaných dashboardoch je source file autorita. Ak sa dashboard upraví v UI a neskôr sa provisioning source aktualizuje, source môže databázovú verziu prepísať.

Preto definuj:

- či je UI editing povolený,
- export/import workflow,
- Git ownership,
- folder/provider mapping,
- deletion behavior,
- reconciliation interval.

## 24. Dashboards as code

Možnosti:

- raw dashboard JSON,
- provisioning files,
- HTTP APIs,
- Terraform provider,
- Kubernetes/Grafana Operator,
- Jsonnet/grafonnet alebo iné generation tools.

Trade-off:

- raw JSON je presný, ale hlučný,
- higher-level abstraction znižuje duplication, ale pridáva generator dependency,
- UI-first workflow je rýchly, ale potrebuje export a review discipline.

Generated dashboard artifact musí byť reprodukovateľný a testovateľný.

## 25. Provisioning data sources

Data-source provisioning môže definovať:

- name a UID,
- plugin type,
- URL,
- default status,
- JSON settings,
- secure JSON data,
- deletion/pruning behavior.

Používaj stabilné UIDs, aby dashboardy neboli viazané na environment-specific numeric IDs.

Secure credentials nevkladaj do dashboard JSON ani plain Git files.

## 26. Folders a permissions

Folders organizujú dashboards a môžu byť authorization boundary podľa Grafana modelu.

Použitie:

- team ownership,
- environment alebo domain separation,
- admin/editor/viewer access,
- provisioning scope.

Over inheritance a edition-specific RBAC capabilities.

Folder permission nechráni automaticky source data pred query cez iný dashboard alebo Explore.

## 27. Authentication

Grafana môže používať:

- local users,
- OAuth/OIDC,
- SAML alebo LDAP podľa edície/integrácie,
- auth proxy,
- service accounts a API tokens.

Production požiadavky:

- federovaná identity,
- MFA v identity providerovi,
- group/team mapping,
- least privilege,
- service-account rotation,
- audit,
- break-glass model,
- anonymous access explicitne vypnutý alebo striktne obmedzený.

## 28. Sharing a snapshots

Grafana podporuje viacero sharing modelov podľa edície a konfigurácie.

Riziká:

- snapshot môže obsahovať citlivé query výsledky,
- externally shared dashboard môže sprístupniť širší scope,
- embedded dashboard môže obísť očakávaný UI context,
- panel link môže obsahovať tenant alebo identifier,
- exportovaný JSON môže obsahovať data-source metadata.

Sharing musí prejsť data-classification a access review.

## 29. Plugins

Grafana používa plugins pre data sources, panels a applications.

Plugin lifecycle:

- source a trust,
- signature,
- version compatibility,
- permissions a network access,
- upgrade testing,
- deprecation,
- vulnerability management.

Neoverený plugin beží v citlivej observability/control vrstve a môže mať access k query data alebo credentials podľa architektúry.

## 30. Grafana Alerting

Grafana Alerting môže vytvárať alert rules nad jedným alebo viacerými data sources a používať expressions.

Hlavné concepts:

- Grafana-managed alert rules,
- data-source-managed rules,
- rule groups a evaluation interval,
- alert instances podľa labels,
- contact points,
- notification policies,
- mute timings a silences,
- templates.

Grafana-managed alerting a Prometheus + Alertmanager sú dva možné alerting control planes. Môžu koexistovať, ale ownership musí byť jasný.

## 31. Grafana-managed oproti data-source-managed alerts

### Grafana-managed

- evaluation vykonáva Grafana alerting engine,
- môže kombinovať podporované data sources a expressions,
- routing/contact points sú spravované Grafanou.

### Data-source-managed

- rules žijú v Prometheus/Mimir/Loki alebo inom podporovanom ruler systéme,
- evaluation a storage semantics vlastní data source,
- Grafana poskytuje UI a management integráciu podľa capability.

Rozhodnutie ovplyvňuje:

- availability,
- GitOps/provisioning,
- tenant model,
- query compatibility,
- rule location,
- notification ownership,
- migration.

## 32. Grafana Alerting provisioning

Alerting resources možno podľa deploymentu spravovať cez:

- files,
- Terraform,
- provisioning APIs,
- supported app-platform APIs.

Provisioned resources môžu byť v UI read-only alebo musia byť upravené v pôvodnom source podľa spôsobu provisioningu.

Aktuálna dokumentácia označuje niektoré staršie provisioning HTTP API endpoints pre contact points, notification policies, templates a mute timings ako deprecated v prospech novších Grafana App Platform alerting APIs. Pri automatizácii preto over aktuálny API contract a verziu Grafany.

## 33. Grafana HA

Grafana HA typicky vyžaduje:

- viac stateless Grafana instances,
- spoločnú podporovanú SQL database,
- load balancer,
- konzistentnú configuration a plugins,
- shared secret/encryption settings,
- session a auth consistency,
- alerting HA configuration podľa použitého modelu,
- externalized dashboards/provisioning.

SQLite nie je vhodný shared database model pre multi-instance HA.

Grafana HA nezabezpečuje HA data sources. Prometheus, Loki, Tempo a ďalšie backends potrebujú vlastnú availability.

## 34. Internal database

Grafana internal database uchováva napríklad:

- dashboards a folders,
- users/teams/organizations,
- data-source metadata a encrypted secure fields,
- alerting resources,
- annotations,
- preferences a permissions.

Potrebný je:

- backup a restore,
- schema migration plán,
- upgrade testing,
- connection pool monitoring,
- database HA podľa požadovanej dostupnosti.

Provisioning z Git pomáha rekonštruovať časť state-u, ale nenahrádza všetky database data.

## 35. Upgrade model

Pred upgrade-om:

- prečítaj release notes a breaking changes,
- over plugin compatibility,
- zálohuj database a configuration,
- exportuj critical dashboards/alerting resources,
- testuj v staging,
- over auth, data sources, dashboards, alerting a provisioning,
- priprav rollback boundary.

Database migration môže obmedziť jednoduchý binary rollback. Rollback plán musí zohľadniť schema compatibility.

## 36. Performance a query cost

Grafana môže vytvoriť vysoký load na backends cez:

- krátky auto-refresh,
- veľa panels,
- repeated panels,
- broad variables,
- long time ranges,
- high-resolution queries,
- many users,
- alert evaluations,
- transformations veľkých datasets.

Query budget dashboardu:

```text
panels
× queries per panel
× repeated variable values
× viewers
× refresh frequency
```

Optimalizácia:

- recording rules,
- bounded variables,
- rozumný refresh,
- aggregate overview,
- query caching podľa capability,
- max data points a intervals,
- drilldown namiesto všetkého naraz.

## 37. Self-monitoring

Sleduj:

- HTTP request rate/errors/latency,
- active users a sessions,
- database connections a latency,
- data-source query duration/errors,
- alert evaluation a notification failures,
- provisioning errors,
- plugin failures,
- authentication failures,
- cache behavior,
- process CPU/memory,
- frontend/backend logs,
- dashboard load time.

Critical synthetic path:

```text
login
→ open service dashboard
→ execute known query
→ render panel
→ open Explore/drilldown
```

## 38. Troubleshooting „No data“

```text
správny dashboard time range?
→ variable values?
→ data source selected a healthy?
→ raw query v Explore?
→ query inspector request/response?
→ labels/tenant/environment?
→ instant vs range query?
→ interval/rate window?
→ transformations/filtering?
→ field mapping/visualization?
→ source backend ingestion?
```

„No data“ sa líši od nuly. Nula je sample hodnota; no data znamená, že query nevrátila očakávanú series/frame.

## 39. Troubleshooting panel ukazuje zlú hodnotu

Over v poradí:

1. raw data-source query,
2. query time range a step,
3. aggregation a label scope,
4. transformations,
5. reducer/calculation,
6. field unit,
7. value mapping,
8. panel overrides,
9. timezone,
10. cache.

Porovnaj Grafana query s query vykonanou priamo v data source expression browseri/API.

## 40. Troubleshooting pomalý dashboard

Over:

- panel query durations,
- počet queries,
- variable queries,
- repeated panels,
- time range,
- data-source latency,
- browser rendering,
- transformations,
- backend cardinality,
- concurrent refresh,
- network proxy.

Použi panel inspector a server/data-source metrics. Neoptimalizuj iba browser, ak backend spracúva milióny series.

## 41. Troubleshooting data source

```text
Grafana server network path
→ DNS
→ TLS/CA/SNI
→ authentication/token
→ tenant/header
→ data-source URL
→ health check
→ plugin logs
→ backend API permissions
→ proxy/firewall
```

Test z browsera môže byť irelevantný, ak query vykonáva Grafana server zo server-side boundary.

## 42. Troubleshooting variables

Problémy:

- variable vracia príliš veľa values,
- dependent variable sa neobnoví,
- „All“ regex je nesprávny,
- value obsahuje special characters,
- data source interpolation format nesedí,
- URL parameter prepisuje očakávanú hodnotu,
- hidden variable drží stale default.

Zobraz final interpolated query v inspector/Explore.

## 43. Troubleshooting provisioning drift

```text
ktorý source je autorita?
→ file/Terraform/API/Operator/UI?
→ stabilný UID a folder?
→ provider scan/reload?
→ file permissions/path?
→ provisioning logs?
→ UI edit prepísaný source-om?
→ duplicate dashboard UID?
→ prune/delete semantics?
```

Nemiešaj viac writers pre ten istý dashboard bez ownership pravidla.

## 44. Troubleshooting Grafana alert

Over:

- rule type a owner,
- data-source query,
- evaluation interval,
- pending/for semantics,
- no-data/error handling,
- labels a alert instances,
- notification policy,
- silence/mute timing,
- contact point,
- template,
- receiver response.

Dashboard panel a alert rule môžu používať odlišný query time range, transformations alebo evaluation engine. Vizuálne podobný panel nie je dôkaz totožnej alert condition.

## 45. Anti-patterny

### Dashboard ako source of truth

Source telemetry a query contract musia existovať nezávisle od konkrétnej vizualizácie.

### Panel pre každú metric

Vzniká inventory bez investigation hierarchy.

### Variables ako authorization

Používateľ môže query zmeniť alebo použiť Explore podľa permissions.

### Transformations namiesto správnej backend query

Prenáša veľké datasety a komplikuje alerting/testovanie.

### Červený threshold ako alerting stratégia

Panel color nemá notification ani ownership lifecycle.

### UI edit provisionovaného dashboardu bez exportu

Nasledujúci reconciliation ho prepíše.

### Jedna broad data-source identity pre všetkých tenantov

Dashboard permissions nemusia zabrániť cross-tenant query.

### Auto-refresh 5 sekúnd na dlhom time range

Vytvára zbytočný backend a browser load.

### Alerting v Prometheus aj Grafane bez ownershipu

Vznikajú duplicity, odlišné conditions a nejasný routing.

## 46. Kontrolné otázky

1. Aký je rozdiel medzi Grafanou a telemetry backendom?
2. Čo tvorí panel a kde sa aplikujú transformations?
3. Prečo treba najprv overiť raw query result?
4. Ako variables menia query cost a security?
5. Na čo slúžia annotations, links a correlations?
6. Ako sa líši dashboard od Explore?
7. Aké sú výhody a riziká dashboard provisioningu?
8. Čo je rozdiel medzi Grafana-managed a data-source-managed alerts?
9. Čo Grafana HA vyžaduje a čo nerieši?
10. Ako diagnostikuješ „No data“?
11. Ako vzniká dashboard query storm?
12. Prečo folder permission nemusí chrániť data source?

## Glossary impact

Relevantné pojmy: Grafana, data source, data-source plugin, dashboard, panel, data frame, field, visualization, transformation, expression, variable, variable interpolation, repeating panel, annotation, dashboard link, data link, correlation, Explore, panel inspector, dashboard provisioning, dashboard as code, folder permission, Grafana-managed alert, data-source-managed alert, contact point, notification policy, Grafana HA a query storm.

## Primárne zdroje

- [Grafana introduction](https://grafana.com/docs/grafana/latest/introduction/)
- [Grafana data sources](https://grafana.com/docs/grafana/latest/datasources/concepts/)
- [Grafana dashboards](https://grafana.com/docs/grafana/latest/visualizations/dashboards/)
- [Panels and visualizations](https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/)
- [Query and transform data](https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/query-transform-data/)
- [Dashboard variables](https://grafana.com/docs/grafana/latest/visualizations/dashboards/variables/)
- [Annotations](https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/annotate-visualizations/)
- [Explore](https://grafana.com/docs/grafana/latest/visualizations/explore/)
- [Provision Grafana](https://grafana.com/docs/grafana/latest/administration/provisioning/)
- [Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/)
- [Provision alerting resources](https://grafana.com/docs/grafana/latest/alerting/set-up/provision-alerting-resources/)
- [Roles and permissions](https://grafana.com/docs/grafana/latest/administration/roles-and-permissions/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Alertmanager](alertmanager.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Loki →](loki.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
