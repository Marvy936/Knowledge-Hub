# Alert design a alert fatigue

Alert nie je threshold, červený panel ani informácia, že sa niečo zmenilo. Je to versionovaný operational action contract: pri konkrétnom user alebo business riziku má správny receiver v správnom čase dostať jednu zrozumiteľnú notification, vykonať bezpečnú prvú akciu a preukázať resolution. Alert fatigue vzniká, keď tento contract produkuje viac prerušení než správnych reakcií.

Noisy alert nie je iba nepríjemnosť. Znižuje dôveru, predlžuje acknowledgement, podporuje broad silences a učí on-call ignorovať rovnaký channel. Oprava alert fatigue preto nezačína zvýšením threshold-u naslepo. Začína auditom signal population, actionability, routing, grouping, ownership a closure evidence.

## Alert lifecycle

```text
user alebo business risk
→ exact alert subject a valid population
→ action contract a urgency
→ query, threshold a evaluation windows
→ pending/firing/resolved state
→ identity, labels a routing
→ grouping/inhibition/silence
→ receiver delivery a acknowledgement
→ bounded response
→ technical a business recovery
→ alert resolution a post-incident review
```

Alert môže byť technicky firing a operationally neúspešný, ak page nedorazí alebo responder nevie, čo urobiť. Môže byť resolved, hoci user impact pokračuje, pretože query stratila data. Closure preto obsahuje signal freshness a business validation.

## Exact alert subject

Atlas používa:

```yaml
alertName: PaymentSettlementFastBurn
alertGeneration: ALERT-PAY-31
service: atlas-payments
environment: production
slo: settlement-completion
population: valid logical settlement operations
condition: multi-window error-budget burn
severity: page
owner: payments-oncall
receiver: pagerduty-payments
runbook: payments/settlement-fast-burn
requiredFirstAction: isolate affected cohort after evidence capture
forbiddenActions:
  - restart all payment workloads
  - increase retries globally
  - silence all production alerts
```

Názov alertu, labels a annotations musia poskytovať enough context bez high-cardinality identity. Pod, payment ID a raw exception nepatria do page labels. Alert instance identity má byť stabilná cez replicas a retries.

## Actionability pred thresholdom

Pred vytvorením page alertu odpovedz:

```text
Ktorý user outcome je ohrozený?
Prečo musí človek reagovať teraz?
Akú prvú bezpečnú action môže vykonať?
Ktoré evidence potrebuje?
Aký blast radius má nesprávna action?
Čo znamená resolved?
```

Ak odpoveď znie „pozrieť sa na dashboard“, alert pravdepodobne nemá complete runbook. Low-urgency capacity trend patrí do ticket/weekly planning, nie do nočnej page. Security alebo data-integrity incident môže page-nuť aj pri malom trafficu, preto severity nie je iba percent affected requests.

## SLO burn-rate alert

Pre 99.9 % SLO je allowed error ratio `0.001`. Burn rate je observed error ratio / allowed ratio.

Recording rule:

```yaml
groups:
  - name: atlas-payments-slo
    interval: 30s
    rules:
      - record: service:payment_settlement_error_ratio:rate5m
        expr: |
          sum(rate(payment_settlement_completed_total{result!="success"}[5m]))
          /
          sum(rate(payment_settlement_started_total[5m]))

      - record: service:payment_settlement_error_ratio:rate1h
        expr: |
          sum(rate(payment_settlement_completed_total{result!="success"}[1h]))
          /
          sum(rate(payment_settlement_started_total[1h]))
```

Fast-burn alert:

```yaml
      - alert: PaymentSettlementFastBurn
        expr: |
          (service:payment_settlement_error_ratio:rate5m / 0.001 > 14.4)
          and
          (service:payment_settlement_error_ratio:rate1h / 0.001 > 14.4)
        for: 2m
        labels:
          severity: page
          service: atlas-payments
          environment: production
          slo: settlement-completion
        annotations:
          summary: Payment settlement error budget is burning rapidly
          runbook_url: https://runbooks.example/payments/settlement-fast-burn
```

Short a long window znižujú page na krátky spike a zároveň reagujú na sustained high burn. Values a windows sa odvodzujú od SLO/error-budget strategy, nie kopírujú bez modelu.

`for: 2m` vyžaduje continuous active condition pred firing. Môže oddialiť detection a nie je náhrada multi-window designu. Missing series môže resetnúť pending state alebo vytvoriť absent alert podľa expression; telemetry freshness sa sleduje samostatne.

## Minimum traffic a denominator

Ratio pri jednom requeste môže byť 100 %, ale page nemusí byť správna, ak service nemá urgentný low-volume contract. Naopak jediná failed payment s data-integrity riskom môže byť kritická.

Traffic guard:

```promql
sum(rate(payment_settlement_started_total[5m])) > 1
```

Guard preukazuje observed traffic rate nad threshold. Nepreukazuje, že telemetry je complete. Pri no traffic sa môže použiť synthetic journey alebo heartbeat alert. Alert condition musí rozlíšiť quiet service, missing producer a actual success.

## Query unit tests

Rule fixture overuje deterministic state transition nad známymi input series: či condition zostane pending dostatočne dlho, ktoré labels vytvoria alert identity a či expected alert vznikne v presnom evaluation time. Úspešný unit test nepreukazuje producer completeness, rule deployment ani notification delivery; tie zostávajú samostatnými runtime gates. Nasledujúca fixture preto testuje iba expression a alert-state contract.

```yaml
rule_files:
  - payments.rules.yml

evaluation_interval: 30s

tests:
  - interval: 30s
    input_series:
      - series: 'payment_settlement_started_total{result="all"}'
        values: '0+100x240'
      - series: 'payment_settlement_completed_total{result="terminal_error"}'
        values: '0+2x240'
    alert_rule_test:
      - eval_time: 10m
        alertname: PaymentSettlementFastBurn
        exp_alerts:
          - exp_labels:
              severity: page
              service: atlas-payments
              environment: production
              slo: settlement-completion
```

```bash
promtool check rules payments.rules.yml
promtool test rules payments.test.yml
```

Syntax check nepreukazuje signal semantics. Unit test preukazuje selected synthetic series behavior. Production replay/shadow evaluation musí overiť missing data, counter resets, labels a traffic distributions.

## Severity a routing

Severity vychádza z urgency a impactu:

```text
page   = človek musí konať teraz, aby obmedzil user/data/security impact
ticket = action je potrebná, ale môže počkať na working hours
info   = context alebo audit, nie interruption
```

Route matchers musia byť testované s representative label fixtures. Alert s `severity=page` a chýbajúcim `service` môže skončiť v default ticket receiveri. Routing test a end-to-end canary sú súčasť deployment gate-u.

## Grouping, inhibition a silences

Grouping spája related alert instances do notification. Pri group-by `alertname,service,environment` sa AZ cohorts zobrazia v jednej page; to je vhodné, ak on-call vykonáva jednu action. Ak každá Region vyžaduje nezávislého ownera, Region patrí do group identity.

Inhibition potlačí symptom alerts pri active root-cause alert-e. Musí zachovať rovnaký scope, inak broad Region alert skryje unrelated service failure. Silences sú time-bounded exceptions s ownerom, reasonom a expiry. Silence nie je oprava noisy rule.

## Runbook ako executable decision support

Runbook alertu obsahuje:

```text
meaning a user impact
exact query a data source
subject fields a expected cohort
known false-positive boundaries
first three read-only observations
safe containment options
forbidden actions
recovery and rollback
positive, forbidden and telemetry validation
owner and escalation
```

Runbook command musí vysvetliť output. Napríklad:

```bash
curl -fsS -G 'http://prometheus:9090/api/v1/query_range' \
  --data-urlencode 'query=sum by (availability_zone,provider_config_generation) (rate(payment_settlement_completed_total{result!="success"}[5m]))' \
  --data-urlencode 'start=2026-07-29T09:10:00Z' \
  --data-urlencode 'end=2026-07-29T09:35:00Z' \
  --data-urlencode 'step=30s' \
  | jq '.data.result'
```

Výstup preukazuje observed error rate cohorts v exact backend/range. Nepreukazuje TLS root cause ani metric completeness. Ďalší krok používa exemplar/trace a loaded config inventory.

## Alert delivery SLO

Monitoring condition a notification pipeline majú samostatné SLI:

```text
valid page alerts acknowledged within 5 minutes
/
all valid page alerts
```

Meria sa rule condition-to-firing, firing-to-Alertmanager, route/group delay, receiver API delivery a human acknowledgement. Alertmanager notification success nepreukazuje on-call acknowledgement. Synthetic canary testuje firing aj resolved path bez real incidentu.

## Alert fatigue metrics

Alert quality sa hodnotí cez:

```text
pages per on-call shift
percentage actionable pages
duplicate notifications per incident
alerts without owner/runbook
time to acknowledge
time to correct first action
silence count and broadness
flapping frequency
alerts closed without user impact
```

Nízky page count s missing critical coverage nie je úspech. Cieľom je vysoký signal-to-action ratio pri complete business risks.

Každý alert má review date. Alerts, ktoré tri mesiace nikdy nefiring-li, sa neodstraňujú automaticky; testuje sa, či condition je stále relevantná a canary vie path aktivovať. Alert, ktorý firing-li stokrát bez action, sa prerobí alebo zníži na ticket.

## Flapping a hysteresis

Threshold `queue_age > 60` môže opakovane prechádzať okolo hranice. `for`, multi-window query, recovery threshold alebo smoothing môžu znížiť flap, ale nesmú maskovať sustained impact.

Hysteresis možno implementovať cez odlišný firing/resolution mechanismus v supported alerting system-e alebo cez stateful recording strategy. Každá komplikácia musí mať unit tests. Artificially dlhý `for` môže zmeniť 2-minútový RTO incident na late page.

## Worked incident: noisy Pod alert skryje business outage

Atlas má alert `PodRestarted` s labels `pod`, `container`, `reason`, `namespace` a `severity=page`. Pri node upgrade-e vytvorí 86 pages. On-call použije broad silence `service=atlas-payments` na dve hodiny. O 40 minút neskôr začne final settlement fast-burn incident, ale Alertmanager ho silence-ne.

Root cause nie je iba broad silence. `PodRestarted` je symptom bez immediate action, high-cardinality identity a expected maintenance behavior. Page channel bol zneužitý na inventory event.

Containment zruší broad silence, manuálne eskaluje business alert a zachová notification/audit history. Recovery zmení Pod restart signal na dashboard/ticket podľa restart rate a user impactu. Business SLO page ostane independent. Maintenance suppression používa exact non-production alebo maintenance alert matchers, nie celý service.

Acceptance test vytvorí controlled Pod restart a očakáva žiadnu page pri healthy business outcome. Následne synthetic settlement failure musí vytvoriť jednu grouped page, správny receiver, acknowledgement a resolved notification. Forbidden broad silence policy je odmietnutá admission/review gate-om.

## Kontrolné otázky

1. Prečo alert nie je iba threshold?
2. Kedy signal patrí do page a kedy do ticketu?
3. Čo multi-window burn-rate design rieši?
4. Prečo `for` nie je náhrada správnej query?
5. Ako traffic guard môže stále zlyhať pri telemetry outage?
6. Čo `promtool test rules` preukazuje a čo nie?
7. Ako grouping identity súvisí s action scope-om?
8. Prečo silence nie je oprava noisy alertu?
9. Ktoré metrics ukazujú alert fatigue?
10. Ako Pod restart alert skryl business outage?

## Oficiálna dokumentácia

- [Google SRE Workbook: Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- [Prometheus alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Prometheus rule unit testing](https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/)
- [Alertmanager configuration](https://prometheus.io/docs/alerting/latest/configuration/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OpenTelemetry](opentelemetry.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Cardinality →](cardinality.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
