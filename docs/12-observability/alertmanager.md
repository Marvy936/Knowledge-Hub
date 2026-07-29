# Alertmanager

Alertmanager prijíma firing a resolved alerts od Prometheus serverov alebo kompatibilných producers a rozhoduje, **či, kedy, kam a v akej forme** vznikne notification. Nevyhodnocuje PromQL a nevytvára pôvodnú monitoring condition. Jeho contract začína existujúcim alert state-om a pokračuje cez alert identity, routing, grouping, timing, muting, receiver delivery a external incident outcome.

```text
alert firing
≠ notification bola rozhodnutá
≠ receiver ju prijal
≠ človek alebo automation ju spracovali
```

## 1. Dominantný lifecycle

```text
Prometheus alert-rule generation
→ inactive/pending/firing/resolved alert state
→ exact alert label identity a annotations
→ fan-out všetkým Alertmanager replicas
→ receive a HA peer-state convergence
→ route-tree traversal
→ group identity a timing
→ silence/mute-interval/inhibition verdict
→ receiver a template generation
→ notification attempt/retry
→ receiver acknowledgement alebo unknown outcome
→ external incident/escalation state
→ repeat/update/resolved lifecycle
→ end-to-end delivery, forbidden-route a recovery validation
```

Alertmanager success sa nemeria iba process readiness. Kritická otázka je, či exact alert subject vytvoril správny operational outcome bez nebezpečného muting scope-u alebo duplicate stormu.

## 2. Exact alert-notification subject

Pre Atlas Payments používame:

```text
notification subject: AM-PAY-44
observability subject: OBS-PAY-44
Prometheus alert: SettlementProviderPoolSaturated
rule generation: PAY-RULES-44
alert identity labels:
  alertname="SettlementProviderPoolSaturated"
  service="payments"
  operation="final-settlement"
  environment="production"
  region="eu-central-1"
  severity="page"
  team="payments"
Alertmanager cluster: am-prod-global-3
configuration generation: AM-CFG-77
expected route: payments-production-pager
expected group: service + operation + environment + region + alertname
expected receiver: pager-primary
external incident key: payments/final-settlement/eu-central-1
window: 2026-07-29T08:18Z–08:40Z
```

Notification subject zahŕňa rule generation, complete labels, Alertmanager config, group, receiver a external incident key. Rovnaký `alertname` s odlišným environmentom alebo regionom nie je ten istý incident subject.

## 3. Rozdelenie zodpovedností

### Prometheus

- vyhodnocuje PromQL;
- drží `for` a `keep_firing_for` state;
- vytvára alert labels a annotations;
- posiela firing a resolved updates Alertmanagerom.

### Alertmanager

- identifikuje a deduplikuje alerts;
- aplikuje route tree;
- zoskupuje alerts;
- riadi notification timing;
- aplikuje silences, mute intervals a inhibition;
- renderuje templates;
- volá receiver integrations.

### Receiver a external workflow

- prijíma page, webhook, chat, email alebo ticket event;
- môže mať vlastný incident key, deduplication, retry a escalation;
- musí potvrdiť delivery a byť monitorovaný samostatne.

Alertmanager notification success nepreukazuje acknowledgement človekom. Receiver HTTP `2xx` nemusí preukazovať správne incident routing alebo escalation.

## 4. Alert identity

Alertmanager identity je odvodená z complete label setu. Labels preto musia byť stabilné, bounded a semanticky konzistentné.

Vhodné identity/routing labels:

- `alertname`;
- service a operation;
- environment;
- region/cluster podľa incident boundary;
- severity;
- team/owner;
- bounded tenant alebo priority class, iba ak mení routing.

Annotations nesú dynamický ľudský context:

- summary a user impact;
- current value a threshold;
- dashboard/query/runbook URL;
- troubleshooting hint;
- deployment alebo incident link.

Aktuálna hodnota, exception text alebo timestamp v labeli mení fingerprint pri každom evaluation cykle. Dôsledkom je strata deduplication, nové groups, notification storm a nefunkčný resolved lifecycle.

## 5. HA producer fan-out a deduplication

Viac Prometheus replicas môže vytvoriť rovnaký logical alert. Alertmanager ich deduplikuje iba vtedy, keď majú kompatibilnú alert identity.

Prometheus má posielať alerts **všetkým Alertmanager replicas priamo**, nie cez load balancer, ktorý vyberie iba jednu. Každá Alertmanager instance alert prijme a spracuje; peer mesh koordinuje notification state a silences.

Deduplication znamená:

```text
rovnaká alert identity
→ receiver nedostane jednu notification za každú Prometheus repliku
```

Neznamená:

- exactly-once delivery;
- výber „správnej“ source sample;
- globálny consensus o business incidente;
- ochranu pred odlišnými labels medzi replicas.

Replica-specific label, ktorý zostane v alert identity, vytvorí dva logical alerts a dve notifications.

## 6. Route-tree generation

Route tree rozhoduje receiver, grouping a timing. Root route poskytuje default safety path. Child routes sa vyhodnocujú v poradí a môžu dediť alebo prepísať policy.

```yaml
route:
  receiver: platform-fallback
  group_by: [service, environment, region, alertname]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - receiver: payments-production-pager
      matchers:
        - team="payments"
        - environment="production"
        - severity="page"
      group_by: [service, operation, region, alertname]
```

Policy risks:

- broad route zachytí alert pred špecifickou route;
- missing owner label skončí v nesprávnom default receiveri;
- regex matchuje širšiu population;
- `continue: true` pošle neplánované duplicity;
- child route prepíše timing alebo grouping bez zámeru;
- route existuje v source YAML, ale runtime používa starú config generation.

Routing sa testuje complete fixture label setom, nie iba alertname alebo vizuálnym čítaním YAML.

## 7. Grouping a incident identity

Grouping spája alerts, ktoré pravdepodobne patria k jednej operational reakcii.

```text
24 task-level symptoms
→ group podľa service + operation + region + alertname
→ jedna incident notification s bounded scope-om
```

Príliš jemná group identity vytvorí page storm. Príliš broad grouping spojí odlišné incidents, owners alebo Regions.

Group labels majú reprezentovať spoločný incident boundary. Instance/Pod labels patria do alert detailu, ak každá instance nepotrebuje samostatnú reakciu.

## 8. Notification timing

### `group_wait`

Odklad pred prvou notification novej group. Umožní prísť súvisiacim alerts alebo inhibiting parentu. Príliš dlhá hodnota odloží kritickú page.

### `group_interval`

Minimálny interval pred ďalšou notification po relevantnej zmene existujúcej group.

### `repeat_interval`

Opakovanie pri stále firing group. Musí korešpondovať s on-call escalation, handover a expected incident duration.

Timing nie je iba noise tuning. Je súčasťou detection-to-human latency. Fast-burn outage nesmie čakať na grouping interval navrhnutý pre pomalé warning alerts.

## 9. Silence, mute interval a inhibition

Všetky tri mechanizmy mutujú notification decision, nie pôvodný Prometheus alert state.

### Silence

Manuálna alebo API-created bounded matcher policy. Potrebuje ownera, dôvod, expiry a change/incident reference.

### Mute time interval

Kalendárová policy, napríklad non-production warnings mimo pracovných hodín. Time zone a daylight-saving behavior sa musia explicitne testovať.

### Inhibition

Automatická dependency policy:

```text
source alert firing
+ target alert firing
+ source/target/equal match
→ target notification muted
```

Príklad:

```yaml
inhibit_rules:
  - source_matchers:
      - alertname="RegionUnavailable"
    target_matchers:
      - severity="page"
    equal:
      - environment
      - region
```

`equal` labels definujú muting scope. Ak chýbajú, source alert môže inhibovať unrelated target v inom Regione, environment-e alebo tenant-e.

## 10. Receiver a template generation

Receiver je pomenovaná notification integration alebo ich kolekcia. Obsahuje secrets, TLS/auth a receiver-specific delivery contract.

Template má renderovať:

- user/business impact;
- service, operation, environment a region;
- group scope a firing count;
- start a duration;
- dashboard, trace/log a runbook links;
- ownera a prvý safe action;
- stable external incident key.

Template sa testuje pre:

- empty/one/many alert group;
- firing a resolved path;
- missing optional label;
- payload limits a escaping;
- secret leakage.

Správny route verdict s template errorom nevytvorí usable notification.

## 11. Delivery, retries a unknown outcome

Notification attempt môže skončiť:

- acknowledged receiver success;
- permanent validation/auth failure;
- transient network/throttling failure;
- timeout s neznámym receiver outcome-om;
- template/render failure;
- external receiver success bez správnej escalation.

Alertmanager koordinuje delivery a retry podľa integration semantics, ale nie je nekonečný durable ticketing queue. Receiver outage a timeout potrebujú monitoring.

Unknown outcome je dôležitý:

```text
Alertmanager odošle request
→ receiver incident možno vytvorí
→ response sa stratí
→ retry môže vytvoriť duplicate incident
```

External incident key a receiver idempotency majú zodpovedať stable Alertmanager group identity.

## 12. Resolved lifecycle

Resolved notification môže zatvoriť alebo aktualizovať external incident. Potrebuje rovnakú stable identity ako firing notification.

False resolve môže vzniknúť pri:

- flapping rule;
- label-set change;
- no-data interpretovanom ako recovery;
- producer replica divergence;
- incorrect group identity;
- rule generation migration bez overlapu.

Incident closure má overiť business recovery, nie iba prijatie resolved payloadu.

## 13. High availability a state

Alertmanager HA používa peer-to-peer mesh. Replikuje silences a notification state, aby znížil duplicate notifications a zachoval availability.

HA nie je exactly-once. Pri partition, restart-e, cold state, receiver timeout-e alebo convergence môžu vzniknúť duplicity.

Persistent/runtime state zahŕňa:

- silences;
- notification log a dedup history;
- loaded config a templates;
- peer membership.

Git/IaC configuration nenahrádza runtime silences. Load-balancer health nepreukazuje funkčný peer mesh ani receiver path.

## 14. Worked failure: staging maintenance inhibuje production page

### Symptóm

Prometheus alert `SettlementProviderPoolSaturated` je `firing` počas 14 minút. Alert je viditeľný aj v Alertmanager UI, ale payments on-call nedostal page. Alertmanager process, peer mesh a pager receiver synthetics sú green.

### Target alert

```text
alertname="SettlementProviderPoolSaturated"
service="payments"
operation="final-settlement"
environment="production"
region="eu-central-1"
severity="page"
team="payments"
```

### Súbežný source alert

```text
alertname="ProviderMaintenance"
service="payments"
environment="staging"
region="eu-west-1"
severity="info"
```

### Effective inhibition generation `AM-CFG-77`

```yaml
inhibit_rules:
  - source_matchers:
      - alertname="ProviderMaintenance"
    target_matchers:
      - severity="page"
    equal:
      - service
```

### Competing hypotheses

1. Prometheus alert neposlal Alertmanageru;
2. alert ešte čaká v `group_wait`;
3. route skončila vo fallback receiveri;
4. active silence target matchuje;
5. mute time interval je aktívny;
6. inhibition source target mutuje;
7. template alebo pager API zlyhali;
8. receiver vytvoril incident, ale escalation zlyhala.

### Discriminating evidence

```text
Prometheus:
  alert firing, AM targets healthy
Alertmanager:
  target alert received
  matched payments-production-pager route
  no matching silence
  no active mute interval
  inhibition verdict = true
Receiver:
  žiadny notification attempt pre target group
```

Alertmanager fungoval podľa effective policy. Policy však definovala unsafe scope. Rovnaké `service="payments"` stačilo na to, aby staging maintenance v inom Regione inhibovala production page.

Mechanizmus:

```text
staging source alert firing
→ target production alert má rovnaký service label
→ inhibition equal kontroluje iba service
→ environment a region nie sú scope gates
→ target notification je muted
→ pager receiver nikdy nie je volaný
→ production incident zostane bez page
```

### Containment

- odstrániť alebo dočasne zúžiť chybnú inhibition generation;
- zachovať source/target labels, inhibition status, loaded config a timestamps;
- manuálne deklarovať production incident a kontaktovať on-call;
- nevypnúť všetku inhibition globálne bez kontroly alert stormu;
- overiť ďalšie target alerts ovplyvnené rovnakou source alert identity.

### Authoritative recovery

1. pridať `environment` a `region` do `equal` scope-u;
2. oddeliť maintenance source taxonomy od production dependency parent alerts;
3. vytvoriť fixture pairs pre same/different environment a region;
4. validovať config a runtime reload;
5. poslať controlled production canary alert;
6. overiť notification attempt, receiver acknowledgement a external incident key;
7. poslať matching staging target a potvrdiť, že intended inhibition stále funguje;
8. overiť resolved notification a druhý reload.

### Alertmanager acceptance verdict

Recovery je prijatá, keď:

- production target nie je inhibovaný staging source alertom;
- same-region production parent správne inhibuje iba intended child symptoms;
- exact page smeruje na payments receiver;
- fallback route zachytí missing-owner fixture;
- canary vytvorí jedno external incident bez duplicate stormu;
- resolved path aktualizuje ten istý incident;
- peer restart a producer fan-out zachovajú delivery;
- forbidden receiver a broad silence paths zostanú neaktívne.

## 15. End-to-end notification canary

Kritická notification platforma potrebuje viac než `/ready`:

```text
known Prometheus test series
→ alert pending/firing
→ send všetkým Alertmanager replicas
→ expected route/group/timing
→ no unintended silence/inhibition
→ test receiver
→ receiver acknowledgement
→ external incident/escalation confirmation
→ resolved closure
```

Canary má používať separátny bezpečný receiver alebo controlled incident key, ale rovnakú policy class ako production page.

## 16. Self-monitoring

Sleduj:

- received a active alerts;
- notification attempts, failures a latency;
- receiver response codes a throttling;
- group count a notification volume;
- silences a inhibition decisions;
- config reload status;
- peer membership/convergence;
- state persistence;
- template errors;
- end-to-end canary success.

Alertmanager môže byť healthy a zároveň nepoužiteľný pre jeden route alebo inhibition subject. Self-monitoring potrebuje policy-level fixtures a canaries.

## 17. Troubleshooting paths

### Alert nie je v Alertmanageri

```text
rule existuje a expression vracia series?
→ pending/firing a `for` state
→ rule evaluation error
→ Alertmanager target discovery
→ network/TLS/auth
→ Alertmanager receive/API evidence
```

### Alert je firing, notification neprišla

```text
complete labels a fingerprint
→ route traversal
→ group timing
→ silence
→ mute interval
→ inhibition source/equal scope
→ receiver/template
→ delivery attempt
→ receiver-side incident/escalation
```

### Duplicate notifications

Over:

- replica label v alert identity;
- inconsistent producer labels;
- viac nezávislých Alertmanager clusters;
- peer partition alebo cold state;
- `continue: true`;
- meniace sa group labels;
- receiver timeout/unknown outcome;
- external incident key.

### Alert storm

Najprv odlíš reálny široký incident od identity/cardinality chyby. Potom over grouping, parent alert, inhibition a receiver rate limits. Broad silence bez ownera a expiry iba vytvorí nový blind spot.

## 18. Configuration a policy tests

```bash
amtool check-config alertmanager.yml
```

Syntax validation doplň o fixture tests pre:

- exact route a inherited timing;
- missing owner/default fallback;
- `continue` behavior;
- same/different inhibition scope;
- silence matcher;
- firing/resolved template;
- receiver incident key;
- HA producer fan-out.

Source YAML acceptance nestačí. Po reload-e treba overiť loaded generation a runtime decision.

## 19. Anti-patterny

### Alertmanager ako rule evaluator

Zakrýva boundary medzi monitoring condition a notification policy.

### Dynamický text v labels

Mení identity, groups a deduplication pri každom evaluation cykle.

### Inhibition bez environment/region scope-u

Parent z jednej failure domain môže mutovať unrelated production incident.

### Silence bez ownera a expiry

Vytvorí dlhodobý blind spot bez accountability.

### Jeden Alertmanager za load balancerom ako HA

Prometheus neposiela všetkým replicas a jedna instance nemusí alert prijať.

### Receiver `2xx` ako incident acceptance

Nepreukazuje správne deduplication, escalation ani human acknowledgement.

### Page bez user impactu a safe first action

Responder musí znovu rekonštruovať základný incident context.

## 20. Kontrolné otázky

1. Aký je rozdiel medzi alert state-om a notification outcome-om?
2. Čo tvorí exact alert-notification subject?
3. Prečo labels a annotations majú rozdielne úlohy?
4. Prečo Prometheus posiela alerts všetkým Alertmanager replicas?
5. Ako route order a `continue` menia receiver verdict?
6. Ako group identity súvisí s incident boundary?
7. Aký je rozdiel medzi silence, mute intervalom a inhibition?
8. Prečo `equal` labels definujú bezpečnosť inhibition?
9. Prečo HA negarantuje exactly-once notification?
10. Ako unknown receiver outcome vytvorí duplicate incident?
11. Ako overíš firing aj resolved notification path?
12. Čo musí testovať policy fixture okrem syntaxe YAML?

## Glossary impact

Relevantné pojmy: alert-notification subject, alert-identity generation, notification-decision path, route-policy generation, group-identity contract, notification timing contract, inhibition-scope contract, receiver-delivery subject, unknown notification outcome, external incident key, notification-path canary a Alertmanager acceptance verdict.

## Primárne zdroje

- [Alertmanager concepts](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Alertmanager configuration](https://prometheus.io/docs/alerting/latest/configuration/)
- [Alertmanager high availability](https://prometheus.io/docs/alerting/latest/high_availability/)
- [Prometheus alerting overview](https://prometheus.io/docs/alerting/latest/overview/)
- [Prometheus alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Alertmanager notification templates](https://prometheus.io/docs/alerting/latest/notifications/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Prometheus](prometheus.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Grafana →](grafana.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
