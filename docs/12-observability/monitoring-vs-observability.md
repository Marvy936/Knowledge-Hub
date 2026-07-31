# Monitoring vs. observability

Monitoring a observability nie sú dve konkurenčné platformové funkcie. Monitoring priebežne vyhodnocuje vopred definované otázky nad známym subjectom: prekračuje SLO burn rate hranicu, starne queue, chýba očakávaný backup alebo sa vyčerpáva capacity headroom? Observability je širšia vlastnosť systému a jeho telemetry. Určuje, či responder dokáže po detekcii položiť novú otázku, oddeliť poškodenú cohortu od zdravej, lokalizovať mechanizmus a overiť nápravu bez nasadenia diagnostickej verzie počas incidentu.

Počet dashboardov, terabajty logov ani kúpa konkrétneho produktu observability nevytvoria. Vzniká až vtedy, keď business outcome, instrumentation, telemetry pipeline, query model, ownership a incident workflow tvoria jeden testovaný evidence contract.

## Od business otázky k rozhodnutiu

Celý systém možno čítať ako jeden lifecycle:

```text
business alebo operational otázka
→ exact observed subject a expected outcome
→ signal a coverage contract
→ instrumentation a context propagation
→ collection, processing, transport a storage
→ query alebo monitorovací verdict
→ competing hypotheses a diskriminačné evidence
→ bounded operational decision
→ recovery
→ original, forbidden a telemetry validation
```

Tento tok oddeľuje tri stavy, ktoré sa často nesprávne považujú za ekvivalentné. Green monitor znamená iba to, že jeho konkrétna expression a population neprekročili nakonfigurovanú podmienku. Neznamená automaticky správny používateľský outcome a už vôbec nie schopnosť vysvetliť neznámy failure. Rovnako neprítomnosť errorov v backende môže znamenať zdravú službu, ale aj zlyhanú emission, collection alebo query boundary.

## Exact observed subject

Názov služby je príliš široký observation subject. Atlas Payments používa subject `OBS-PAY-43`:

```yaml
businessCapability: CAP-PAY-42
journey: enterprise payment settlement
logicalOperation: settle(payment_id)
entryOperation: POST /payments/{id}/settle
release: 7.19.0
providerConfigGeneration: PROVIDER-CFG-34
telemetryGeneration: OTEL-PAY-12
environment: production
region: eu-central-1
azCohorts: [eu-central-1a, eu-central-1b]
slo: 99.9% valid settlements completed within 2.5s over 28d
```

Tento subject umožňuje rozlíšiť HTTP acceptance, provider authorization, durable ledger commit a final settlement completion. Ak dashboard agreguje iba handler `202` responses, môže byť úplne správny a zároveň nereprezentovať business outcome, ktorý používateľ očakáva o niekoľko sekúnd neskôr.

## Monitoring ako vopred definovaný action contract

Monitor má zmysel iba vtedy, keď jeho podmienka vedie k rozhodnutiu. Complete contract obsahuje measurement boundary, validnú population, numerator a denominator, no-data semantics, threshold, duration, ownera, route, runbook a recovery condition.

Pre HTTP acceptance môže byť PromQL expression:

```promql
sum(rate(http_server_requests_total{
  service="payments-api",
  route="POST /payments/{id}/settle",
  status_code=~"2.."
}[5m]))
/
sum(rate(http_server_requests_total{
  service="payments-api",
  route="POST /payments/{id}/settle"
}[5m]))
```

Táto query preukazuje podiel úspešných HTTP attempts v zvolenom päťminútovom okne. Nepreukazuje final settlement, pretože `202` znamená prijatie asynchronous workflowu, nie provider a ledger completion.

Business completion potrebuje samostatnú population:

```promql
sum(rate(payment_settlement_completed_total{
  environment="production",
  result="success"
}[5m]))
/
sum(rate(payment_settlement_started_total{
  environment="production"
}[5m]))
```

Výsledok query je použiteľný iba vtedy, keď oba counters reprezentujú rovnakú logical-operation population a retry nevytvára druhý `started` event pre tú istú business operation. Pri rozdielnom semantics by ratio meralo telemetry implementáciu, nie business correctness.

Query možno overiť priamo cez Prometheus HTTP API:

```bash
curl -fsS -G 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=sum(rate(payment_settlement_completed_total{environment="production",result="success"}[5m])) / sum(rate(payment_settlement_started_total{environment="production"}[5m]))' \
  | jq '.data.result'
```

Tento príkaz preukazuje raw instant-query result v konkrétnom Prometheus serveri. Dashboard môže používať inú data source, tenant, time range, step alebo transformation, preto rovnaký vizuálny panel stále treba porovnať s jeho effective query requestom.

## Observability ako schopnosť odpovedať na nové otázky

Po detekcii často nevieme, či failure súvisí s release, AZ, provider route, tenant class, configuration generation alebo queue pathom. Observable systém umožní prejsť od symptom-u k mechanizmu pomocou už existujúceho kontextu:

```text
business SLO burn
→ affected operation a cohort
→ exemplar alebo trace ID
→ dependency spans
→ structured logs s rovnakým trace a logical-operation contextom
→ release/configuration event
→ loaded-state inventory
→ bezpečná remediation
```

Observability neznamená ukladať každý payload navždy. Metrics používajú bounded dimensions, napríklad operation, result class, release channel, Region alebo AZ. Request, trace a payment identifiers patria do traces alebo chránených logs, nie automaticky do metric labels. Tak sa zachová detail pre investigation bez nekontrolovanej cardinality.

## Coverage kopíruje business transaction

Telemetry coverage sa navrhuje podľa failure boundaries journey, nie podľa organizačného zoznamu microservices. Settlement workflow potrebuje dôkaz na každej významnej state transition:

```text
client alebo black-box outcome
→ edge a service acceptance
→ stable logical-operation identity
→ provider attempt a response
→ ledger commit alebo rollback
→ queue acknowledgement alebo redelivery
→ final business completion
```

Ak telemetry končí pri HTTP acceptance, nevysvetlí zlyhanie po `202`. Ak začína až na workerovi, nepreukáže, čo dostal client. Coverage má aj negatívny contract: raw token, card data a nekontrolovaný customer identifier nesmú prejsť do logs, baggage ani indexed attributes.

White-box telemetry opisuje interný state, napríklad pool wait, queue age alebo exporter drops. Black-box synthetics overujú DNS, TLS, HTTP a user-like flow zvonka. Business-outcome signal overuje správne dokončenie. Kritická journey potrebuje všetky tri perspektívy, pretože healthy target a rýchly `202` môžu koexistovať s nedokončenou platbou.

## Telemetry pipeline je samostatný production systém

Application a observability platforma majú vlastné failure domains:

```text
operation
→ instrumentation
→ SDK alebo agent buffer
→ collector receiver
→ processors, sampling a redaction
→ exporter, network a authentication
→ backend ingest a storage
→ query, tenant a time range
→ dashboard alebo rule
```

Absent signal preto vytvára dve competing hypotheses: udalosť nenastala alebo zlyhala emission/delivery/query boundary. Pipeline sa monitoruje vlastnými accepted, refused, queued, retried a dropped records, ingestion lagom, scrape healthom, loaded configuration generation a end-to-end canary.

Praktický health check môže porovnať producer counter s collector exportom:

```bash
curl -fsS http://payments-api:9464/metrics \
  | grep '^payment_settlement_completed_total'

curl -fsS http://otel-collector:8888/metrics \
  | grep -E 'otelcol_(receiver_accepted|exporter_sent|exporter_send_failed)_metric_points'
```

Prvý výstup preukazuje, že producer endpoint publikuje metric sample. Druhý preukazuje receiver/exporter accounting Collectora. Ani jeden nepreukazuje durable backend ingest alebo queryability; posledný hop sa overuje backend query a telemetry canary.

## Worked incident: monitoring je green na nesprávnej boundary

Dňa `2026-07-29` o `09:18 UTC` spustí settlement-completion SLO fast-burn page. HTTP dashboard ostáva green: `202` success je `99.98 %`, handler p95 `84 ms`, CPU `46 %` a healthy targets `24/24`. Enterprise merchants však dostávajú settlement confirmation neskoro alebo vôbec.

Incident subject je release `7.19.0`, operation `settle(payment_id)`, `merchant.class=enterprise`, provider route `provider-a/high-value`, AZ `eu-central-1b`, config `PROVIDER-CFG-34` a window `09:12–09:31 UTC`.

HTTP monitor a business SLI si neprotirečia. Prvý meria acceptance, druhý final completion. Responder zachová oba signály a vytvorí competing hypotheses: telemetry pipeline failure, provider outage, release-wide bug, AZ/config cohort failure, queue lag, mTLS trust failure alebo stratený completion event.

Cohort query odhalí rozdiel:

```promql
sum by (availability_zone, release, provider_config_generation) (
  rate(payment_settlement_completed_total{
    merchant_class="enterprise",
    result="error"
  }[5m])
)
```

Táto query preukazuje error attempts rozdelené podľa bounded cohort dimensions. Neurčuje root cause. Trace exemplar následne končí na provider-adapter mTLS handshake a correlated log nesie `tls.alert=unknown_ca`. Loaded-state inventory ukáže, že tasks v `eu-central-1a` používajú `PROVIDER-CFG-35`, zatiaľ čo affected `1b` cohort zostal na `PROVIDER-CFG-34`.

Containment odoberie iba `1b/7.19.0/CFG-34` cohort z enterprise routingu, zastaví ďalšiu replacement slučku a zachová trace IDs, task definition, config inventory a provider logs. Plošné zvýšenie timeoutov alebo retries je zakázané, pretože by zosilnilo provider load.

Authoritative recovery publikuje immutable `PROVIDER-CFG-35`, vytvorí canary task v affected AZ, overí loaded trust generation, mTLS handshake a controlled enterprise settlement. Traffic sa vracia po bounded cohorts. Incident je uzavretý až keď final completion SLI aj original enterprise journey prejdú, stale config cohort neexistuje, forbidden old trust generation zlyhá a telemetry pipeline preukáže producer-to-backend canary.

Skorší control porovnáva intended a loaded configuration generation pred target eligibility a deployment gate vykonáva synthetic final settlement, nie iba HTTP acceptance.

## Operating zásady

Monitoring deteguje a prioritizuje. Observability lokalizuje a vysvetľuje. Recovery obnoví outcome a oba systémy overia closure. Investigation finding sa môže zmeniť na nový monitor, ale iba ak jeho dimensions zostanú bounded a condition je actionable. Detail vhodný pre traces nemusí patriť do permanentnej metric alebo page rule.

Telemetry cost sa riadi už pri signal design-e: emission overhead, network, ingest, index, query a retention. Retention vychádza z detection latency, SLO windows, recurrence a compliance. Redaction sa vykonáva čo najbližšie k producerovi; odstránenie citlivého field-u až v dashboarde nezabráni jeho exportu a uloženiu.

## Kontrolné otázky

1. Aký rozdiel je medzi monitorovacou podmienkou a observability otázkou?
2. Prečo green HTTP acceptance nepreukazuje final settlement?
3. Čo musí obsahovať exact observed subject?
4. Ako odlíšiš absent business event od telemetry pipeline failure?
5. Čo producer a Collector health commands preukazujú a čo ešte nie?
6. Prečo request ID nepatrí automaticky do metric labels?
7. Ako coverage contract kopíruje business journey?
8. Prečo sa affected cohort odoberá z routingu pred broad restartom?
9. Aké evidence uzatvára recovery incidentu `OBS-PAY-43`?
10. Kedy sa investigation finding má zmeniť na permanentný monitor?

## Oficiálna dokumentácia

- [Prometheus overview](https://prometheus.io/docs/introduction/overview/)
- [Prometheus querying basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [OpenTelemetry concepts](https://opentelemetry.io/docs/concepts/)
- [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CloudOps troubleshooting drills](../11-cloud-and-aws/cloudops-troubleshooting-drills.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Metrics, logs, traces a events →](metrics-logs-traces-events.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
