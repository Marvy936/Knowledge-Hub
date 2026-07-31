# Alertmanager

Alertmanager prijíma firing a resolved alerts od Prometheus serverov alebo kompatibilných producers a rozhoduje, **či, kedy, kam a v akej forme** vznikne notification. Nevyhodnocuje PromQL a nevytvára pôvodnú monitoring condition. Jeho contract začína existujúcim alert state-om a pokračuje cez alert identity, routing, grouping, timing, inhibition, silence, receiver delivery a external incident outcome.

```text
alert firing
≠ route vybrala receiver
≠ notification bola odoslaná
≠ receiver ju prijal
≠ incident bol acknowledged
≠ user outcome sa obnovil
```

Alerting je distributed delivery workflow. Každý krok potrebuje identity, retry, evidence a acceptance.

## End-to-end lifecycle

Alertmanager nie je jednorazový forwarder, ale stateful notification workflow. Alert instance sa najprv deduplikuje a routuje, potom vstupuje do grouping a timing state-u a až receiver attempt môže vytvoriť external notification. Každý krok má inú proof boundary, preto sa celý delivery mechanizmus overuje v nasledujúcom poradí.

```text
Prometheus rule evaluation
→ pending alebo firing alert instance
→ send to Alertmanager cluster
→ deduplication a alert fingerprint
→ routing tree
→ grouping a timing state
→ inhibition alebo silence verdict
→ receiver payload a retry
→ external service delivery
→ human alebo automation acknowledgement
→ resolved notification
→ incident a business closure
```

Alertmanager configuration file definuje routing, receivers, inhibition a time intervals. Command-line flags definujú process-level parameters. Configuration možno reload-nuť, ale malformed file sa neaplikuje. Loaded state sa preto overuje, nie predpokladá.

## Exact alert-delivery subject

Atlas používa:

```yaml
alertName: PaymentSettlementFastBurn
alertIdentity:
  service: atlas-payments
  environment: production
  severity: page
  slo: settlement-completion
prometheusRuleGeneration: PROM-RULES-33
alertmanagerConfigGeneration: AM-CFG-28
cluster: alertmanager-platform
route: payments-primary
receiver: pagerduty-payments
notificationPolicy: NOTIFY-PAY-17
runbook: payments/settlement-fast-burn
```

Dynamic labels ako payment ID, Pod name alebo full error message nesmú tvoriť page identity. Každá unikátna label combination je samostatná alert instance a môže vytvoriť notification storm.

## Routing tree

Alertmanager route je strom. Root route musí existovať; child routes sa vyhodnocujú podľa matchers a `continue` semantics.

```yaml
route:
  receiver: default-ticket
  group_by: [alertname, service, environment]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - receiver: pagerduty-payments
      matchers:
        - service="atlas-payments"
        - severity="page"
      group_by: [alertname, environment, slo]
      group_wait: 15s
      group_interval: 2m
      repeat_interval: 30m

    - receiver: payments-ticket
      matchers:
        - service="atlas-payments"
        - severity="ticket"
      group_wait: 5m
      repeat_interval: 24h
```

Configuration preukazuje desired route logic. Nepreukazuje, že exact file je loaded, secrets sú dostupné alebo receiver funguje. `continue: true` by umožnilo pokračovať v matching sibling routes a môže zámerne alebo nechcene poslať duplicate notifications.

Routing sa testuje:

```bash
amtool check-config /etc/alertmanager/alertmanager.yml

amtool config routes test \
  --config.file=/etc/alertmanager/alertmanager.yml \
  service=atlas-payments \
  environment=production \
  severity=page \
  slo=settlement-completion
```

`check-config` preukazuje parse a static config validation. Route test preukazuje receiver selection pre synthetic label set v zadanom file. Nepreukazuje loaded config ani external delivery.

Loaded status:

```bash
curl -fsS http://alertmanager:9093/-/ready

curl -fsS http://alertmanager:9093/api/v2/status \
  | jq '{cluster: .cluster, config: .config.original}'
```

Readiness endpoint preukazuje process readiness, nie notification path. Status API poskytuje loaded config a cluster state daného instance; secrets môžu byť redacted a receiver stále nedostupný.

## Alert identity a deduplication

Alert fingerprint vychádza z labels. Annotations nemenia identity a sú vhodné pre summary, description, runbook URL a dashboard links. Ak `pod` zostane v labels, 24 failing Pods vytvorí 24 alert instances. Ak routing groupuje iba podľa `alertname`, viac environments môže skončiť v jednej notification a maskovať scope.

Silný identity contract používa labels potrebné pre ownership a routing:

```yaml
labels:
  alertname: PaymentSettlementFastBurn
  service: atlas-payments
  environment: production
  severity: page
  slo: settlement-completion
```

Release, AZ alebo provider môžu byť investigation dimensions. Do page identity sa pridávajú iba ak vyžadujú nezávislú action a notification. Inak patria do annotations/dashboardu alebo grouped payloadu.

## Group timing

`group_wait` odkladá prvú notification, aby sa súvisiace alerts stihli zoskupiť. Príliš vysoká hodnota zvyšuje detection-to-notification latency. Príliš nízka vytvára burst jednotlivých pages.

`group_interval` určuje minimálny odstup pred notification o zmenách v existujúcej group. `repeat_interval` riadi opakovanie, ak group ostáva firing. Effective behavior závisí aj od data retention a timing implementation; testuje sa na nasadenej version.

Pri fast-burn page s `group_wait=15s` a external receiver latency 20s je minimálna alert-to-receiver cesta už približne 35s plus Prometheus evaluation/send. SLO alert response budget musí zahŕňať celý chain.

## Inhibition

Inhibition potlačí target alert, keď existuje matching source alert a equal labels určujú spoločný scope.

```yaml
inhibit_rules:
  - source_matchers:
      - alertname="RegionUnavailable"
      - severity="page"
    target_matchers:
      - service="atlas-payments"
      - severity=~"page|ticket"
    equal: [environment, region]
```

Táto rule môže potlačiť symptom alerts počas region incidentu. Je bezpečná iba ak source alert spoľahlivo reprezentuje root incident a on-call z neho vie nájsť affected services. Príliš broad `equal` scope môže potlačiť unrelated environment alebo Region.

Inhibition nie je deduplication a nevyrieši duplicate Prometheus rules. Potlačený alert ostáva active v Alertmanageri a musí byť viditeľný pre investigation.

## Silences a time intervals

Silence je time-bounded matcher-based suppression. Má ownera, dôvod, start/end a ticket/change reference. Broad matcher `severity=page` počas maintenance môže skryť unrelated incident.

```bash
amtool silence add \
  service=atlas-payments \
  environment=staging \
  --duration=2h \
  --author='change-automation' \
  --comment='CHG-2026-991 staging load test'

amtool silence query service=atlas-payments
```

Prvý command vytvorí silence v target Alertmanageri. Nepreukazuje, že matchers zodpovedajú intended alerts; pred vytvorením sa testujú na exact label sets. Query ukáže silence records, nie external change approval.

Time intervals sú vhodné pre pravidelné business schedules, nie na umlčanie permanentne noisy rule. Page alert pre production user impact sa typicky nemute-uje len preto, že je noc.

## Receivers a secret handling

Receiver configuration používa secret file alebo environment integration podľa deployment modelu:

```yaml
receivers:
  - name: pagerduty-payments
    pagerduty_configs:
      - routing_key_file: /etc/alertmanager/secrets/pagerduty-routing-key
        send_resolved: true
        severity: '{{ .CommonLabels.severity }}'
        description: >-
          {{ .CommonAnnotations.summary }}
          env={{ .CommonLabels.environment }}
          slo={{ .CommonLabels.slo }}
```

Secret sa nesmie uložiť do Git ani template outputu. File presence, permissions a loaded secret generation sú runtime dependencies. Receiver API môže prijať HTTP request a neskôr zlyhať pri incident creation; Alertmanager metrics a external receiver audit sa korelujú.

Relevantné metrics zahŕňajú notification attempts, failures, latency, alerts received, invalid alerts a cluster health. Metric names sa overujú pre nasadenú version.

## Cluster a HA

Alertmanager cluster replikuje silence a notification state medzi peers, ale Producers majú posielať alerts na všetky Alertmanager instances podľa supported HA modelu. Load balancer pred clusterom môže vytvoriť single delivery path, ktorý obíde intended producer fan-out.

Cluster status:

```bash
curl -fsS http://alertmanager-0:9093/api/v2/status | jq '.cluster'

curl -fsS http://alertmanager-1:9093/api/v2/status | jq '.cluster'
```

Výstup preukazuje peer view jednotlivých instances. Nepreukazuje, že Prometheus posiela alerts na všetky peers alebo receiver delivery funguje. Network partition môže vytvoriť duplicate notifications; external receiver deduplication a stable group identity znižujú impact, ale presné semantics sa testujú.

## End-to-end canary

Synthetic canary alert testuje rule-to-receiver path bez simulovania real user outage-u:

```yaml
groups:
  - name: alert-delivery-canary
    rules:
      - alert: AlertDeliveryCanary
        expr: vector(1)
        for: 1m
        labels:
          service: observability-platform
          environment: production
          severity: ticket
          canary: "true"
        annotations:
          summary: End-to-end alert delivery canary
```

Rule syntax:

```bash
promtool check rules alert-delivery-canary.yml
```

Canary receiver automaticky potvrdí notification ID a resolved message. `vector(1)` preukazuje rule path, nie application monitoring correctness. Separate SLO canary musí overiť business signal generation.

Alert canary acceptance zahŕňa Prometheus pending/firing timestamps, Alertmanager received state, selected route/group, receiver delivery, acknowledgement a resolved delivery. Missing resolved notification je samostatný failure.

## Worked incident: alert firing, page nedorazila

`PaymentSettlementFastBurn` začne firing o `09:18 UTC`. Prometheus rule API ho zobrazuje firing a posiela alerts bez errors. On-call však page nedostane; incident nájde až business owner o deväť minút neskôr.

Competing hypotheses sú Prometheus send failure, Alertmanager route mismatch, inhibition, active silence, receiver secret failure, PagerDuty API error, grouping delay alebo wrong alert labels.

Prometheus alert API potvrdí firing labels. Alertmanager API ukáže active alert. Route test s rovnakými labels vyberie `default-ticket`, nie `pagerduty-payments`, pretože release zmenil label `service="atlas-payments"` na `service_name="atlas-payments"`. Rule condition bola správna, alert delivery contract driftol.

Containment pridá dočasnú exact child route pre oba schema variants a manuálne eskaluje active incident. Broad default receiver sa nemení, aby nevytvoril page storm.

Recovery obnoví canonical `service` label v recording/alert rule, pridá schema contract test a route unit test. Canary firing a resolved notification prejdú cez production route. Acceptance vyžaduje page receiver audit, on-call acknowledgement, resolved message a forbidden alert s `severity=ticket`, ktorý nesmie page-nuť.

Skorší control testuje reprezentatívne alert label fixtures proti routing tree pri každej rule alebo Alertmanager config zmene.

## Alert delivery metrics a SLO

Alerting pipeline má vlastné SLI:

```text
valid page alerts delivered and acknowledged within objective
/
all valid page alerts
```

Meria sa condition-to-firing, firing-to-Alertmanager, Alertmanager-to-receiver, receiver-to-ack a resolved path. Notification failure metric bez valid-alert denominatora nevysvetlí silent route mismatch.

Page volume, grouped alerts, inhibited alerts, silences a receiver failures sa sledujú podľa ownera a environmentu. High cardinality alert identity môže preťažiť Alertmanager aj receiver a predĺžiť delivery.

## Kontrolné otázky

1. Kde končí Prometheus rule contract a začína Alertmanager contract?
2. Čo route test preukazuje a čo nie o loaded config?
3. Prečo annotations nemenia alert identity?
4. Ako dynamic Pod label vytvorí page storm?
5. Aký rozdiel je medzi grouping, inhibition a silence?
6. Prečo broad silence počas maintenance predstavuje riziko?
7. Čo Alertmanager cluster status nepreukazuje?
8. Ako end-to-end canary overí resolved path?
9. Prečo alert firing pri incidente nedorazil na page receiver?
10. Aký forbidden route test uzatvára recovery?

## Oficiálna dokumentácia

- [Alertmanager configuration](https://prometheus.io/docs/alerting/latest/configuration/)
- [Alertmanager high availability](https://github.com/prometheus/alertmanager#high-availability)
- [amtool](https://github.com/prometheus/alertmanager#amtool)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Prometheus](prometheus.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Grafana →](grafana.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
