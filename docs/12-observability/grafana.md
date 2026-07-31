# Grafana

Grafana je query, visualization, investigation a alerting vrstva nad externými telemetry backends. Typicky nevlastní autoritatívne metrics, logs ani traces. Vlastní však dôležitú časť operational contractu: ktorý backend a tenant sa queryujú, aký request Grafana odošle, aké data frames sa vrátia, ktoré transformations a field overrides sa aplikujú a čo nakoniec používateľ vidí.

Zelený panel preto nie je priamy dôkaz zdravého systému. Je to renderovaný výsledok konkrétnej data-source identity, query, time range-u, variable values, transformation chainu, dashboard revision a viewer permissions. Backend môže obsahovať správne dáta a panel ich môže zobraziť nesprávne. Opačne môže panel pôsobiť zdravo, pretože queryuje starý cluster, inú Region alebo cached result.

## Od operational otázky k panelu

```text
business alebo operational otázka
→ exact dashboard a panel subject
→ data-source UID, tenant a authorization
→ variables, time range, step a query
→ backend response
→ Grafana data frames
→ transformations, reduce a field overrides
→ visualization a thresholds
→ operational decision
→ query-inspector a backend validation
→ dashboard source a loaded revision closure
```

Panel má byť poslednou vrstvou rozhodovacieho modelu, nie jeho zdrojom. Query inspector umožňuje pozrieť raw request a response, panel inspector raw data, transformations menia data frames a visualization options menia iba presentation. Tieto boundaries sa pri incidente analyzujú oddelene. citeturn662053search11turn662053search16turn662053search24

## Exact Grafana subject

Atlas Payments používa dashboard subject `GRAF-PAY-43`:

```yaml
organization: production-observability
dashboardUid: atlas-payments-overview
dashboardRevision: 84
folder: Payments
panelId: 17
panelTitle: Final settlement success ratio
dataSourceUid: prometheus-prod-eu
backend: prometheus-platform-0
queryRefId: A
timeRange: now-30m to now
minInterval: 30s
variables:
  environment: production
  merchant_class: enterprise
transformations:
  - reduce:lastNotNull
  - organizeFields
thresholds:
  green: 0.999
```

Incident evidence musí obsahovať dashboard UID/revision, panel ID, data-source UID, variables, absolute time range, query request, response frames a transformation configuration. Screenshot bez týchto údajov nie je reprodukovateľný.

## Data source provisioning

Data source sa spravuje ako versionovaný config:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus Production EU
    uid: prometheus-prod-eu
    type: prometheus
    access: proxy
    url: http://prometheus-platform:9090
    isDefault: false
    editable: false
    jsonData:
      timeInterval: 30s
      httpMethod: POST
```

Provisioning file preukazuje desired data-source identity a endpoint. Nepreukazuje, že Grafana exact file načítala, že DNS/TLS/auth fungujú alebo že endpoint reprezentuje intended tenant. Grafana podporuje provisioning data sources a dashboards as code; UI edit provisioned dashboardu môže byť neskôr prepísaný provisioning source-om. citeturn662053search2turn662053search32

Loaded data source možno overiť cez Grafana API s approved service-account tokenom:

```bash
curl -fsS \
  -H "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/datasources/uid/prometheus-prod-eu" \
  | jq '{uid, name, type, url, isDefault, jsonData}'
```

Výstup preukazuje data-source record v konkrétnej Grafana organization. Nepreukazuje successful query ani backend identity za URL; health/query test zostáva samostatný.

## Dashboard as code

Dashboard provisioning provider:

```yaml
apiVersion: 1

providers:
  - name: payments-dashboards
    orgId: 1
    folder: Payments
    type: file
    disableDeletion: false
    allowUiUpdates: false
    updateIntervalSeconds: 30
    options:
      path: /var/lib/grafana/dashboards/payments
      foldersFromFilesStructure: true
```

Dashboard JSON obsahuje stable UID a panel queries. Source control vlastní intended revision; Grafana database obsahuje loaded representation. Deployment gate porovnáva source hash, loaded dashboard version a expected panels. Provisioned dashboard edited v UI bez spätného source update-u nie je authoritative change.

Dashboard read-back:

```bash
curl -fsS \
  -H "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/dashboards/uid/atlas-payments-overview" \
  > /tmp/dashboard.json

jq '{uid: .dashboard.uid, version: .dashboard.version, title: .dashboard.title, panels: [.dashboard.panels[] | {id, title, datasource, targets, transformations}]}' \
  /tmp/dashboard.json
```

Prvý príkaz preukazuje loaded dashboard record. Druhý z neho extrahuje effective panel configuration. Neznamená, že všetky viewers majú rovnaké permissions alebo že query výsledky sú správne.

## Query, time range a variables

Panel query pre settlement success:

```promql
sum(rate(payment_settlement_completed_total{
  environment="$environment",
  merchant_class="$merchant_class",
  result="success"
}[$__rate_interval]))
/
sum(rate(payment_settlement_started_total{
  environment="$environment",
  merchant_class="$merchant_class"
}[$__rate_interval]))
```

Grafana variables a macros sa expandujú pred backend requestom. Query inspector ukáže expanded expression, start/end, step a response timing. `$__rate_interval` sa odvodzuje od panel resolution a scrape interval; rovnaký dashboard pri inom time range môže použiť iné range window.

Backend query sa reprodukuje mimo Grafany:

```bash
curl -fsS -G 'http://prometheus-platform:9090/api/v1/query_range' \
  --data-urlencode 'query=sum(rate(payment_settlement_completed_total{environment="production",merchant_class="enterprise",result="success"}[2m])) / sum(rate(payment_settlement_started_total{environment="production",merchant_class="enterprise"}[2m]))' \
  --data-urlencode 'start=2026-07-29T09:10:00Z' \
  --data-urlencode 'end=2026-07-29T09:35:00Z' \
  --data-urlencode 'step=30s' \
  | jq '.data.result'
```

Tento output preukazuje Prometheus result pre exact expression a absolute range. Nepreukazuje, že Grafana použila rovnaký backend, query, headers alebo transformation. Porovnanie musí používať údaje z query inspectoru, nie ručne odhadnutú query.

## Transformations a reduce semantics

Grafana transformations menia data frames po backend response. Môžu joinovať series, filtrovať fields, vypočítať hodnotu alebo reduce-nuť time series na jeden number. citeturn662053search9turn662053search24

Panel môže napríklad použiť:

```json
{
  "transformations": [
    {
      "id": "reduce",
      "options": {
        "reducers": ["lastNotNull"]
      }
    }
  ]
}
```

`lastNotNull` môže zobraziť starú hodnotu po tom, čo current series prestala prichádzať. Panel ostane zelený, hoci backend má no data. Ak monitorovací contract vyžaduje fresh value, dashboard musí zobrazovať sample age alebo používať explicitnú freshness query.

```promql
time() - timestamp(
  payment_settlement_completed_total{
    environment="production",
    merchant_class="enterprise"
  }
)
```

Query preukazuje age posledného sample-u pre selected series. Pri viacerých series treba agregáciu navrhnúť podľa expected population; minimum age môže skryť stale cohort.

## Field overrides a thresholds

Unit, decimal formatting, value mappings a thresholds nemenia raw data. Nesprávna unit môže zobraziť ratio `0.999` ako `0.999 %` namiesto `99.9 %`. Threshold môže byť nastavený pre percent value 99.9, zatiaľ čo query vracia ratio 0.999.

Panel inspector raw data a dashboard JSON odlíšia backend value od display override. Threshold color nie je business verdict; SLO formula a units musia byť explicitné v title alebo description.

## Variables a hidden scope

Dashboard variable môže byť `All`, multi-value alebo regex-expanded. Query `environment=~"$environment"` s `All=.*` môže zmiešať production a staging, ak variable query alebo custom all value nie sú správne. Viewer URL môže niesť `var-environment=staging`, zatiaľ čo screenshot title zostane rovnaký.

Dashboard links a incident evidence preto zahŕňajú variable values a absolute time range. Hidden variables sa auditujú rovnako ako visible controls.

## Grafana alerting boundary

Grafana-managed alerting môže queryovať data sources a vyhodnocovať expressions nezávisle od dashboard panelu. Alert rule môže používať podobnú query, ale dashboard edit automaticky nemusí zmeniť alert rule. Naopak transformation v paneli nemusí existovať v alert evaluation pipeline.

Rule a panel sa preto nesmú považovať za rovnaký contract iba podľa názvu. Evaluation query, no-data/error handling, labels, contact point a notification policy sa testujú samostatne.

## Worked incident: backend je správny, panel ostáva green

Po rollout-e `OTEL-PAY-12` prestane enterprise completion metric prichádzať z `eu-central-1b`. Prometheus query pre `1b` vracia empty vector a freshness alert fire-ne. Grafana stat panel `Final settlement success ratio` však stále ukazuje `99.95 %` zelenou farbou.

Competing hypotheses sú wrong data source, cached query, variable scope, panel transformation, stale browser, recording-rule mismatch alebo backend replication lag.

Query inspector ukáže správny data-source UID a Prometheus response: `1a` má current values, `1b` series chýba. Panel query agreguje bez AZ a transformation `lastNotNull` ponecháva posledný predchádzajúci combined value. Threshold navyše neobsahuje freshness condition. Grafana funguje podľa configuration; dashboard contract je zavádzajúci.

Containment pridá panel annotation `telemetry incomplete` a incident response používa raw cohort query. Recovery rozdelí success ratio podľa AZ, pridá expected-target coverage a sample-age panel a nahradí stale reduce explicitným no-data behaviorom. Dashboard source sa aktualizuje v Git a loaded revision sa overí API read-backom.

Acceptance vyžaduje, aby missing `1b` cohort zobrazil no-data/coverage failure, healthy `1a` zostal viditeľný, raw Prometheus a panel inspector values sa zhodovali a forbidden stale series nebola zobrazená ako current green outcome. Druhý test zmení variable na staging a musí byť jasne viditeľný v panel title a URL evidence.

## Kontrolné otázky

1. Prečo zelený panel nie je priamy business dôkaz?
2. Aký rozdiel je medzi backend response, data frame, transformation a visualization?
3. Čo data-source API read-back preukazuje a čo nie?
4. Prečo provisioned dashboard edit v UI nemusí byť authoritative?
5. Čo query inspector poskytuje navyše oproti screenshotu?
6. Ako `lastNotNull` môže maskovať no-data incident?
7. Prečo unit a threshold môžu zmeniť interpretation bez zmeny raw value?
8. Ako variables menia query population?
9. Prečo dashboard panel a Grafana alert rule nie sú automaticky rovnaký contract?
10. Aké evidence uzatvára Grafana stale-panel incident?

## Oficiálna dokumentácia

- [Grafana dashboards](https://grafana.com/docs/grafana/latest/visualizations/dashboards/)
- [Grafana provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)
- [Panel inspector](https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/panel-inspector/)
- [Query and transform data](https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/query-transform-data/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Alertmanager](alertmanager.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Loki →](loki.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
