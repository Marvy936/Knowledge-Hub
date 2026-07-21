# Alertmanager

Alertmanager prijíma alerts z Prometheus serverov alebo kompatibilných clients, deduplikuje ich, zoskupuje, aplikuje routing, inhibition a silences a následne odosiela notifications do definovaných receivers. Nevyhodnocuje PromQL conditions a nerozhoduje, či monitoring condition vznikla; to je úloha Prometheus alerting rules alebo iného alert producer-a.

## 1. Mentálny model

```text
Prometheus alerting rule
→ pending/firing alert
→ alert labels a annotations
→ odoslanie všetkým Alertmanager replicas
→ fingerprint a deduplication
→ routing tree
→ grouping a timing
→ silence/inhibition
→ receiver integration
→ notification template
→ external on-call/chat/email systém
```

Alert a notification nie sú to isté:

- alert je stav monitoring condition,
- notification je správa odoslaná konkrétnemu receiveru podľa policy.

Jeden alert môže vytvoriť viac notifications v čase alebo nemusí vytvoriť žiadnu, ak je muted.

## 2. Rozdelenie zodpovedností

### Prometheus

- vyhodnocuje PromQL,
- spravuje `for` a `keep_firing_for` semantics podľa rule konfigurácie,
- vytvára alert labels a annotations,
- posiela firing a resolved alerts Alertmanageru.

### Alertmanager

- deduplikuje alerts,
- zoskupuje súvisiace alerts,
- routuje podľa labels,
- aplikuje silences a inhibition,
- riadi notification timing,
- renderuje templates,
- odosiela receiverom.

### Receiver

- doručuje page, ticket, email alebo chat message,
- môže mať vlastný deduplication, retry a escalation model,
- musí byť monitorovaný samostatne.

## 3. Alert data model

Alert typicky obsahuje:

- labels,
- annotations,
- `startsAt`,
- `endsAt`,
- generator URL,
- fingerprint odvodený z label setu.

### Labels

Labels určujú alert identity, grouping, routing, silences a inhibition.

Príklady:

- `alertname`,
- `service`,
- `cluster`,
- `namespace`,
- `severity`,
- `team`,
- `environment`,
- `region`.

Labels musia byť:

- stabilné,
- bounded,
- konzistentné medzi rules,
- vhodné pre ownership a routing.

### Annotations

Annotations poskytujú ľudský context:

- summary,
- description,
- runbook URL,
- dashboard URL,
- current value,
- troubleshooting hints.

Dynamický text patrí primárne do annotations, nie do labels. Ak sa aktuálna hodnota alebo error message vloží do labelu, alert identity sa môže meniť pri každom evaluation cykle.

## 4. Alert fingerprint a deduplication

Alertmanager identifikuje alert podľa label setu.

Dve alerts s rovnakými labels sa považujú za rovnakú alert identity aj keď:

- prišli z dvoch Prometheus HA replicas,
- annotations majú odlišné hodnoty,
- prišli opakovane počas firing stavu.

Pre HA Prometheus model je kritické, aby replica-specific label nebol súčasťou alert identity, ktorú má Alertmanager deduplikovať. To možno riešiť cez Prometheus alert relabeling alebo konzistentný external-label model.

Deduplication neznamená, že Alertmanager vyberie „správny“ source sample. Znamená iba, že neposiela duplicity tej istej alert identity receiveru.

## 5. Routing tree

Alertmanager používa hierarchický route tree.

Root route:

- musí existovať,
- definuje default receiver,
- nesmie mať matchers,
- poskytuje zdedené grouping a timing defaults.

Child routes môžu matchovať labels a prepisovať:

- receiver,
- `group_by`,
- `group_wait`,
- `group_interval`,
- `repeat_interval`,
- active alebo mute time intervals,
- ďalšie child routes.

Príklad:

```yaml
route:
  receiver: default-email
  group_by: [cluster, alertname]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

  routes:
    - receiver: platform-pager
      matchers:
        - team="platform"
        - severity="page"
      group_by: [cluster, service, alertname]

    - receiver: security-pager
      matchers:
        - team="security"
      continue: true
```

## 6. Route matching

Route matching používa label matchers:

- equality,
- inequality,
- regular expression,
- negative regular expression.

Route sa vyhodnocuje zhora nadol.

Pri zhode s child route sa spracovanie sibling routes štandardne zastaví, pokiaľ nie je nastavené `continue: true`.

Riziká:

- broad route zachytí alerts pred špecifickou route,
- chýbajúci ownership label pošle alert default receiveru,
- regex matchuje viac hodnôt než sa očakávalo,
- `continue: true` vytvorí duplicitné notifications,
- child route nezdedí očakávané timing po explicitnom prepísaní.

Routing tree testuj s konkrétnymi label sets, nie iba vizuálnou kontrolou YAML.

## 7. Grouping

Grouping spája alerts podobnej povahy do jednej notification.

Príklad incidentu:

```text
200 Pod alerts
→ group_by: [cluster, alertname]
→ jedna notification s 200 alerts
```

Grouping znižuje notification storm, ale príliš broad group môže zmiešať odlišné incidents.

### `group_by`

Labels určujúce group identity.

Príklady:

- `[cluster, alertname]`,
- `[service, alertname]`,
- `[team, environment, alertname]`.

`group_by: ['...']` znamená agregovanie bez klasického obmedzeného group label setu a treba ho používať opatrne, pretože prakticky vypína zoskupovanie do väčších skupín.

### Grouping trade-off

Príliš jemné grouping:

- mnoho pages,
- alert storm,
- opakovaný rovnaký context.

Príliš hrubé grouping:

- unrelated services v jednej notification,
- nejasný owner,
- veľká správa,
- pomalé pochopenie scope-u.

Group podľa incident ownership a spoločnej root-cause pravdepodobnosti.

## 8. Notification timing

### `group_wait`

Čas čakania pred prvou notification novej group.

Umožní:

- prísť ďalším súvisiacim alerts,
- doraziť inhibiting parent alertu,
- vytvoriť kompaktnejšiu notification.

Príliš dlhý `group_wait` odkladá page. Príliš krátky zvyšuje množstvo partial notifications.

### `group_interval`

Minimálny interval pred odoslaním aktualizácie existujúcej group po pridaní alebo resolved stave alerts.

### `repeat_interval`

Interval opakovania notification, ak alert group zostáva firing a od poslednej úspešnej notification neprišla relevantná zmena.

Repeat interval zosúlaď s:

- on-call escalation,
- expected incident duration,
- receiver deduplication,
- shift handover,
- maintenance modelom.

## 9. Notification log

Alertmanager udržiava notification state potrebný na deduplication a timing.

Tento stav pomáha rozhodnúť:

- či už bola group odoslaná,
- ktorému receiveru,
- s akým alert setom,
- či treba poslať update alebo repeat.

Pri HA clustri sa notification log replikuje medzi peers pomocou cluster communication. Je eventually consistent, preto môžu pri partition alebo cold start-e vzniknúť obmedzené duplicate notifications. HA cieľom je dostupnosť notification pipeline, nie exactly-once delivery.

## 10. Receivers

Receiver je pomenovaná kolekcia jednej alebo viacerých notification integrations.

Typy môžu zahŕňať:

- email,
- generic webhook,
- PagerDuty,
- Opsgenie,
- Slack,
- Microsoft Teams cez podporovaný integration model,
- ďalšie on-call alebo chat služby podľa aktuálnej verzie.

Receiver konfigurácia obsahuje citlivé údaje:

- API tokens,
- webhook URLs,
- SMTP credentials,
- TLS konfiguráciu.

Secrets nesmú byť commitnuté priamo v otvorenom configuration repository. Použi secret injection, permissions a rotation model vhodný pre runtime.

## 11. Notification retries

Alertmanager retryuje notification delivery podľa receiver a error semantics.

Rozlišuj:

- dočasný network failure,
- receiver throttling,
- permanent invalid request,
- authentication failure,
- template rendering failure,
- DNS/TLS problém,
- proxy failure.

Alertmanager nie je ticketing system ani nekonečný durable queue. Dlhodobý receiver outage môže viesť k oneskoreniu alebo strate očakávanej operational reakcie podľa konkrétneho failure a retry lifecycle-u.

Monitoruj úspešnosť notification attempts a receiver-side ingestion.

## 12. Silences

Silence dočasne mutuje notifications pre alerts, ktoré matchujú všetky silence matchers.

Silence typicky obsahuje:

- matchers,
- start a end time,
- creator,
- comment alebo ticket/change reference.

Použitie:

- plánovaná údržba,
- známy incident so samostatnou koordináciou,
- dočasná mitigation počas opravy alertu.

Silence neodstraňuje alert a nemení Prometheus rule state. Alert zostáva firing a viditeľný ako silenced.

### Silence governance

Vyžaduj:

- bounded duration,
- ownera,
- dôvod,
- change/incident ID,
- čo najpresnejšie matchers,
- review dlhých silences.

Broad silence ako `severity=page` môže skryť nesúvisiace incidents.

## 13. Mute time intervals

Mute timing môže pravidelne mutovať notifications podľa kalendára alebo time intervals.

Príklady:

- non-production warnings mimo pracovných hodín,
- známe pravidelné maintenance windows,
- business-hours routing.

Root route nemá byť mutovaná spôsobom, ktorý odstráni default safety path. Time zone a daylight-saving behavior explicitne over.

Kalendárové muting pravidlo nesmie maskovať kritický 24/7 production alert bez business rozhodnutia.

## 14. Inhibition

Inhibition mutuje target alerts, keď je firing source alert s matching scope labels.

Príklad:

```text
source: ClusterDown
→ inhibit: InstanceDown, PodUnavailable, ScrapeFailed
→ iba parent incident page
```

Inhibition rule obsahuje:

- source matchers,
- target matchers,
- `equal` labels, ktoré musia byť zhodné medzi source a target alertom.

Príklad:

```yaml
inhibit_rules:
  - source_matchers:
      - alertname="ClusterDown"
    target_matchers:
      - severity=~"warning|page"
    equal:
      - cluster
```

### Inhibition riziká

- chýbajúci `equal` scope mutuje alerts z iného clusteru,
- parent alert nie je spoľahlivý,
- source a target labels nie sú konzistentné,
- broad source matcher vytvára príliš veľké muting pole.

Inhibition nesmie nahradiť root-cause-quality alert design.

## 15. Silence oproti inhibition

| Silence | Inhibition |
|---|---|
| manuálna alebo API-created mute policy | automatická závislosť medzi firing alerts |
| bounded časom | aktívna, kým source alert firing |
| používa matchers | používa source, target a equal matchers |
| maintenance alebo incident coordination | parent-child failure suppression |

Obe mutujú notifications, nie alert state.

## 16. Resolved notifications

Receiver môže byť nakonfigurovaný na odosielanie resolved notifications.

Výhody:

- incident closure signal,
- ticket/on-call state update,
- meranie duration,
- automatizovaný recovery workflow.

Riziká:

- flapping vytvára firing/resolved spam,
- niektoré receivers majú vlastný incident lifecycle,
- zlá alert identity môže otvoriť a zatvoriť nesprávne incident records.

Resolved notification má obsahovať rovnakú stabilnú identity a relevantný recovery context.

## 17. Templates

Notification templates používajú Go templating na vytvorenie title, body, links a receiver-specific payloadu.

Template má poskytovať:

- stručný user impact,
- service/environment/region,
- firing count a group context,
- začiatok a duration,
- dashboard a runbook link,
- generator/query link,
- incident alebo ownership metadata.

### Template safety

- nepredpokladaj, že label vždy existuje,
- správne escape-ni receiver syntax,
- nedávaj secrets do outputu,
- obmedz payload size,
- testuj empty, one-alert a many-alert group,
- testuj firing aj resolved path.

Template failure môže zablokovať notification, aj keď routing bol správny.

## 18. Configuration validation

Alertmanager configuration validuj pred reloadom.

Príklad:

```bash
amtool check-config alertmanager.yml
```

Validácia má byť súčasťou CI spolu s:

- YAML syntax,
- matcher syntax,
- receiver references,
- template files,
- secret placeholders,
- policy tests pre sample alerts.

Alertmanager podporuje runtime reload cez `SIGHUP` alebo `POST /-/reload`. Neplatná nová konfigurácia sa nemá aplikovať; reload failure musí byť monitorovaný.

## 19. Routing testovanie

Vytvor fixture alerts:

```json
{
  "labels": {
    "alertname": "ServiceHighErrorRate",
    "service": "orders",
    "team": "payments",
    "severity": "page",
    "environment": "production",
    "cluster": "prod-eu-1"
  },
  "annotations": {
    "summary": "Orders error rate is high"
  }
}
```

Pre každý fixture over:

- matched route,
- inherited group/timing,
- receiver,
- `continue` behavior,
- inhibition,
- silence matching,
- rendered template.

Configuration review bez test fixtures je náchylný na neviditeľné route-order chyby.

## 20. High availability

Alertmanager podporuje HA cluster cez peer-to-peer mesh.

HA model:

- každá instance prijíma a spracúva alerts,
- silences a notification state sa replikuje medzi peers,
- receiver notifications sa koordinujú na zníženie duplicít,
- peers majú nezávislé process a storage lifecycle.

Prometheus má byť nakonfigurovaný tak, aby posielal alerts všetkým Alertmanager instances priamo. Medzi Prometheus a Alertmanager replicas sa nemá použiť load balancer ako jediný endpoint, pretože jedna replika by mohla alerts neprijať a cluster coordination nie je náhrada client fan-outu.

### HA nie je exactly once

Pri:

- network partition,
- peer restart-e,
- state convergence,
- receiver timeout-e,
- split-brain situácii

môžu vzniknúť duplicate notifications.

Receiver integration a on-call workflow majú zvládnuť idempotent alebo deduplicovateľný incident key.

## 21. Cluster networking

Over:

- advertise address,
- peer list/discovery,
- TCP/UDP cluster ports podľa verzie a konfigurácie,
- NetworkPolicy/firewall,
- DNS stability,
- cross-zone latency,
- instance identity,
- persistent storage pre silences podľa deployment modelu.

Load balancer health nepreukazuje funkčný peer mesh.

## 22. Persistent state

Alertmanager local storage obsahuje silence a notification-log state.

Pri ephemeral disk alebo úplnom cluster restart-e môže dôjsť k:

- strate silences,
- opakovaným notifications,
- strate deduplication history.

Rozhodni:

- či je silence persistence kritická,
- ako sa backupuje alebo rekonštruuje configuration,
- ako sa obnovuje cluster po strate state-u,
- či external automation vytvára silences znovu.

Configuration v Git/IaC nenahrádza runtime silences.

## 23. Multi-tenant a ownership model

Alertmanager routing často zdieľa viac tímov.

Potrebné contracts:

- povinný `team` alebo `owner` label,
- severity taxonomy,
- environment taxonomy,
- receiver ownership,
- default fallback receiver,
- route review proces,
- silence permissions,
- template standards,
- rate/alert count limits podľa platformy.

Missing ownership label nemá ticho zahodiť alert. Default route má smerovať na platform triage alebo jasne monitorovanú fallback queue.

## 24. Severity model

Príklad:

- `page` — okamžitá ľudská reakcia je potrebná,
- `ticket` — musí byť spracované v pracovnom workflowe,
- `warning` — diagnostický alebo pre-incident signal bez okamžitého page,
- `info` — zmena alebo kontext, typicky nie pager.

Severity sa nemá odvíjať iba od technického threshold-u. Má vyjadrovať urgency a požadovanú reakciu.

Alert bez action nemá byť page.

## 25. Notification content

Dobrá page odpovedá:

- čo je poškodené,
- koho sa to týka,
- aký je scope,
- odkedy,
- aký je user impact,
- kto je owner,
- čo má responder urobiť ako prvé,
- kde sú dashboard, logs, traces a runbook.

Zlá notification:

```text
CPU > 80 %
```

Lepšia:

```text
Orders API prekračuje latency SLO v prod-eu-1;
error-budget burn 14x počas 10 minút;
12/18 instances má connection-pool saturation.
```

## 26. Self-monitoring

Sleduj:

- počet prijatých alerts,
- active alerts,
- notification attempts a failures,
- notification latency,
- receiver errors,
- silences count,
- inhibition/mute behavior,
- config reload success,
- cluster peers a health,
- state persistence,
- process CPU/memory,
- alert limits alebo dropped alerts, ak sú nakonfigurované.

Critical notification path potrebuje synthetic test:

```text
known test alert
→ Alertmanager route
→ test receiver
→ potvrdené doručenie
```

Samotný `/ready` endpoint nepreukazuje funkčný PagerDuty alebo webhook path.

## 27. Troubleshooting alert sa nezobrazil v Alertmanageri

```text
Prometheus rule existuje?
→ expression vracia series?
→ alert pending alebo firing?
→ `for` ešte neuplynulo?
→ rule evaluation error?
→ Prometheus Alertmanager discovery/config?
→ network/TLS/auth?
→ Alertmanager API prijalo alert?
```

Over:

- Prometheus Rules UI,
- Prometheus Alerts UI,
- rule evaluation metrics/logs,
- Alertmanager target status v Prometheus,
- Alertmanager active alerts.

## 28. Troubleshooting alert je firing, ale notification neprišla

```text
alert labels a fingerprint
→ matched route
→ group_wait/group_interval
→ active silence?
→ inhibition source?
→ mute time interval?
→ receiver configuration
→ template render
→ network/DNS/TLS/auth
→ receiver API response
→ receiver-side dedup/escalation
```

Zachovaj exact label set. Routing sa nedá spoľahlivo diagnostikovať iba podľa alertname.

## 29. Troubleshooting duplicate notifications

Možnosti:

- replica label je súčasťou alert identity,
- Prometheus neposiela konzistentné labels,
- viac nezávislých Alertmanager clusters,
- HA mesh partition,
- receiver incident key nezodpovedá group identity,
- `continue: true` routuje do viacerých integrations,
- notification retry po nejasnom receiver timeout-e,
- group labels sa menia.

Najprv porovnaj fingerprints a complete labels medzi duplikátmi.

## 30. Troubleshooting alert storm

Postup:

1. identifikuj dominantný `alertname` a label dimension,
2. odlíš reálny široký incident od cardinality chyby,
3. over parent alert a inhibition,
4. over grouping,
5. dočasne použi presný bounded silence iba pri koordinovanom incidente,
6. oprav rule, labels alebo dependency alert model,
7. over receiver rate limits a Alertmanager health.

Nerob broad silence bez incident ownera a expiry.

## 31. Troubleshooting silence nefunguje

Over:

- active time range a time zone,
- equality/regex matcher,
- všetky required matchers,
- skutočné alert labels,
- Unicode/UTF-8 matcher parsing podľa verzie,
- replika/cluster state convergence,
- či notification už nebola odoslaná pred silence creation.

Silence sa aplikuje na budúce notification decisions; nevráti už odoslanú page.

## 32. Troubleshooting inhibition nefunguje

Over:

- source alert je firing,
- source a target matchers,
- `equal` labels existujú a majú rovnaké hodnoty,
- labels nie sú prázdne alebo chýbajúce nečakaným spôsobom,
- source a target nie sú ten istý alert podľa pravidiel,
- route alebo receiver očakávanie.

Testuj s konkrétnou dvojicou source/target alerts.

## 33. Anti-patterny

### Alertmanager vyhodnocuje alerts

Alertmanager notification pipeline nezačne existenciu PromQL condition; tú vytvára rule evaluator.

### Dynamický error text v labeli

Mení alert identity a rozbíja deduplication.

### Route bez default owner pathu

Alerts s chýbajúcimi labels sa stratia v nesprávnom receiveri.

### Silence bez expiry alebo commentu

Vzniká trvalý blind spot bez accountability.

### Inhibition bez scope labels

Parent incident môže mutovať nesúvisiace services alebo clusters.

### Jeden Alertmanager za load balancerom ako HA

Prometheus neposiela všetkým replicas a cluster failure môže stratiť alert delivery.

### Page pre každý instance threshold

Vytvára alert storm namiesto service-level incident signal-u.

### Notification bez runbooku a user impactu

Responder musí znovu objavovať základný context.

## 34. Kontrolné otázky

1. Aký je rozdiel medzi alertom a notification?
2. Ktoré dáta patria do labels a ktoré do annotations?
3. Ako Alertmanager deduplikuje HA Prometheus alerts?
4. Ako funguje route tree a `continue`?
5. Čo robia `group_wait`, `group_interval` a `repeat_interval`?
6. Aký je rozdiel medzi silence a inhibition?
7. Prečo `equal` labels rozhodujú o bezpečnosti inhibition?
8. Prečo Prometheus posiela alerts všetkým Alertmanager replicas?
9. Prečo HA negarantuje exactly-once notification?
10. Ako diagnostikuješ firing alert bez notification?
11. Ako navrhneš severity a ownership labels?
12. Ako overíš end-to-end notification path?

## Glossary impact

Relevantné pojmy: Alertmanager, alert fingerprint, alert identity, notification, receiver, route tree, matcher, grouping, group_wait, group_interval, repeat_interval, silence, mute time interval, inhibition, source alert, target alert, equal labels, notification log, resolved notification, notification template, Alertmanager HA, peer mesh, fallback receiver a alert storm.

## Primárne zdroje

- [Alertmanager concepts](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Alertmanager configuration](https://prometheus.io/docs/alerting/latest/configuration/)
- [Alertmanager high availability](https://prometheus.io/docs/alerting/latest/high_availability/)
- [Prometheus alerting overview](https://prometheus.io/docs/alerting/latest/overview/)
- [Prometheus alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Alertmanager notification templates](https://prometheus.io/docs/alerting/latest/notifications/)
