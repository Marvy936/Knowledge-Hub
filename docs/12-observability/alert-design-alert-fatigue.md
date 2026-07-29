# Alert design a alert fatigue

Alert nie je threshold, červený panel ani informácia, že sa niečo zmenilo. Je to versionovaný operational action contract: pri konkrétnom user alebo business riziku má správny receiver v správnom čase dostať jednu zrozumiteľnú notification, vykonať bezpečnú prvú akciu a preukázať resolution. Alert fatigue vzniká, keď tento contract produkuje viac prerušení než správnych reakcií.

## 1. Dominantný mentálny model

```text
user/business outcome a urgency
→ exact alert subject a valid signal population
→ action contract
→ condition a evaluation windows
→ pending/firing/resolved state
→ stable alert identity
→ grouping/inhibition/silence/routing
→ notification a external incident identity
→ acknowledgement a safe first action
→ containment/recovery
→ original a forbidden outcome validation
→ alert-quality review a rule retirement/improvement
```

Kritické rozlíšenie:

```text
metric prekročila threshold
≠ existuje incident
≠ treba pageovať človeka
≠ notification dorazila správnemu ownerovi
≠ responder vykonal správnu akciu
```

Alerting sa optimalizuje na čas k správnej reakcii, nie na počet zachytených technických odchýlok.

## 2. Exact alert subject

Pre každú rule generation zaznamenaj:

```text
Alert subject ID:
User/business outcome a affected population:
Signal, numerator/denominator a data authority:
Rule engine a rule generation:
Evaluation interval a windows:
Threshold/burn-rate/no-data policy:
Alert labels a identity:
Severity a required response time:
Owner, runbook a safe first action:
Notification policy/receiver generation:
External incident key:
Validation a retirement criteria:
```

Rovnaký `alertname` v Prometheus, Grafane a cloud monitoringu nie je automaticky jeden alert subject. Môže ísť o tri conditions, tri identities a tri notification lifecycles.

## 3. Page, ticket a informational event

### Page

Page je oprávnený iba keď:

- existuje významný aktuálny alebo bezprostredný user/business impact;
- oneskorenie zvyšuje škodu;
- automatic remediation nestačí;
- on-call má bezpečnú konkrétnu akciu;
- signal má dostatočnú precision.

### Ticket

Ticket je vhodný pre capacity trend, expiráciu, deprecated dependency, stale rule alebo recurring issue, ktoré nevyžadujú okamžité prerušenie.

### Informational event

Deployment, autoscaling, failover alebo config reload môže byť correlation evidence bez notification.

```text
urgent + important + actionable + real
→ page

important, ale nie urgentné
→ ticket

užitočný context bez action
→ event/dashboard
```

## 4. Symptom a cause boundary

Page preferuj na symptóm vysoko v stacku:

- SLO error-budget burn;
- end-to-end latency alebo availability;
- data correctness/integrity failure;
- queue freshness prekračujúca business deadline;
- saturation, ktorá odstránila failover headroom.

Cause signals ako CPU, Pod restart, GC, packet loss alebo dependency errors patria primárne do investigation telemetry.

Cause alert môže pageovať iba ak spoľahlivo predpovedá bezprostredný impact, vyžaduje skorú akciu alebo chráni security/integrity boundary.

## 5. Action contract

Každý page musí odpovedať:

1. čo je poškodené a koho sa to týka;
2. odkedy a v akom scope;
3. prečo je reakcia urgentná;
4. kto je owner;
5. čo má responder urobiť ako prvé;
6. čo nesmie urobiť;
7. kde sú dashboard, traces, logs a runbook;
8. ako sa preukáže resolution.

Alert bez action nemá byť page. Ak runbook prvý krok znie iba „pozri dashboard“, action contract nie je dokončený.

## 6. Condition a population

Condition potrebuje:

- exact numerator a denominator;
- kompatibilný scope a cohort;
- traffic/minimum-population guard;
- evaluation a observation windows;
- transient handling;
- explicitný no-data verdict;
- bounded output labels.

Príklad SLO-oriented signal:

```text
final settlement failures alebo unknown outcomes
/
valid logical settlements
```

nie:

```text
provider failed attempts
/
HTTP acceptance requests
```

Threshold musí byť odvodený od user impactu, SLO, physical limitu alebo recovery horizonu.

## 7. Burn-rate a time semantics

SLO burn-rate alerting porovnáva aktuálnu chybovosť s povoleným error budgetom. Multi-window model vie odlíšiť:

- fast burn — krátky prudký outage;
- slow burn — dlhšiu miernu degradáciu.

`for` filtruje transient condition, ale môže oneskoriť kritický outage alebo skryť periodický failure. `keep_firing_for` môže obmedziť flapping, nie nahradiť recovery validation.

Každý časový control musí byť vysvetlený cez detection a response objective, nie kopírovaný medzi službami.

## 8. No data

No data môže znamenať:

- legitímne nulový demand;
- odstránený target;
- exporter/scrape/ingest failure;
- schema alebo label drift;
- úplný service outage;
- query defect.

Preto:

```text
no series
≠ zero failures
≠ healthy service
```

Rule potrebuje expected-traffic model, telemetry metamonitoring a black-box fallback.

## 9. Identity, grouping a notification policy

Alert identity vzniká z labels. Stabilné labels nesú ownership a incident scope, napríklad `service`, `environment`, `region`, `severity` a bounded operation.

Current value, hostname list, error text a free-form detail patria do annotations.

### Grouping

Groupuj podľa pravdepodobného spoločného incidentu a ownera. Pod/request/trace identity typicky vytvára alert storm.

### Inhibition

Parent alert môže inhibovať child symptoms iba v rovnakej failure domain. `equal` scope musí zahŕňať relevantný environment, cluster, Region alebo tenant.

### Silence

Silence je bounded manuálny mute s ownerom, reasonom, expiry a audit trailom. Permanentná silence je neuzavretý defect.

### External incident identity

HA a receiver retries môžu vytvoriť duplicate notifications. Receiver musí používať stabilný incident key odvodený od intended alert/group identity.

## 10. Alert ownership a control-plane authority

Definuj jediného ownera condition a notification policy.

```text
Prometheus rule + Alertmanager
alebo
Grafana-managed rule + Grafana notification policy
alebo
cloud-native alarm path
```

Viac engines môže koexistovať pre rozdielne signals, ale rovnaký symptom nemá pageovať z troch independent control planes bez explicitného migration alebo fallback contractu.

UI dashboard threshold nie je alert rule. Data-source-managed a Grafana-managed rules môžu používať odlišné windows, transformations a no-data semantics.

## 11. Alert fatigue ako feedback failure

Alert fatigue sa prejavuje:

- vysokým pages-per-incident;
- nízkym actionable rate;
- duplicate notifications;
- častým auto-resolution bez akcie;
- flappingom;
- rastúcim acknowledgement časom;
- broad silences;
- ignorovaním pagera.

Dôsledok nie je iba nepohodlie. Noise zvyšuje pravdepodobnosť, že skutočný incident nebude včas rozpoznaný.

Meraj:

- pages per shift a per incident;
- actionable/false-positive rate;
- duplicate a flap rate;
- time to acknowledge a mitigate;
- rules bez ownera/runbooku;
- notifications bez následnej action;
- vek silences;
- alerting gaps odhalené incidentmi.

## 12. Worked failure: 43 pages pre jeden settlement incident

### Subject

```text
Incident: ALERT-PAY-46
Symptom: enterprise final-settlement failure ratio 6.9 %
Start: 02:10 UTC
Release: 7.23.0
Primary rule authority: nejasná
Prometheus rules: ALERT-GEN-71
Grafana-managed rules: GRAF-ALERT-29
Cloud infrastructure alarms: CLOUD-ALARM-18
Alertmanager policy: AM-POL-52
```

### Notification outcome

Za prvých sedem minút vzniklo:

```text
1 Prometheus SLO page
1 Grafana duplicate SLO page
32 per-task pool-saturation pages
4 Pod restart pages
4 CPU warning pages
1 cloud load-balancer page
= 43 pages
```

On-call mal z predchádzajúcich dvoch týždňov 68 % auto-resolved pages bez zásahu. Prvú settlement page preto považoval za ďalší transient. Acknowledgement prišlo po 14 minútach; správny user-impact scope bol identifikovaný po 27 minútach.

### Competing hypotheses

1. SLO alert bol nesprávny;
2. alert delivery zlyhala;
3. duplicate engines vytvorili viac incidentov;
4. per-task labels vytvorili cardinality storm;
5. inhibition/grouping policy bola chybná;
6. on-call nemal actionable notification;
7. broad silence z predchádzajúcej maintenance potlačila časť symptomov;
8. alert fatigue znížila dôveru a response speed.

### Discriminating evidence

```text
Prometheus SLO condition: valid
Grafana rule: rovnaký symptom, iné 10m window a incident key
per-task alerts: label task_id v identity
Alertmanager group_by: [alertname, task_id]
inhibition: iba cluster, bez service/environment
runbook link: všeobecná observability homepage
pages s action počas 30 dní: 24 %
auto-resolved pages: 68 %
maintenance silence: broad regex, stále aktívna
```

Mechanizmus:

```text
jeden user-impact incident
→ tri rule authorities vyhodnotia podobný symptom
→ cause rules vytvoria instance-level identities
→ grouping zachová task_id
→ notification storm otvorí viac external incidents
→ dlhodobý noise zníži dôveru
→ on-call oneskorí acknowledgement
→ mitigation a user recovery sa spomalia
```

### Containment

- potvrdiť jednu canonical SLO condition a jeden external incident;
- zastaviť duplicate Grafana/cloud paging pre ten istý symptom;
- presne silencing-nuť iba duplicate/cause rules s ownerom a krátkou expiry;
- zachovať fingerprints, route decisions, receiver acknowledgements a on-call timeline;
- neumlčať canonical user-impact page;
- pripojiť respondera na exact settlement dashboard a safe containment.

### Authoritative recovery

1. určiť Prometheus + Alertmanager ako jediný owner settlement page-u;
2. Grafana rule odstrániť alebo zmeniť na non-paging migration comparison;
3. per-task saturation agregovať na service/Region actionable scope a degradovať na ticket/diagnostic signal;
4. odstrániť dynamic task identity z page labels;
5. opraviť grouping, inhibition a external incident key;
6. nahradiť runbook konkrétnym containment/recovery postupom;
7. zaviesť alert fixtures, notification sandbox a synthetic page canary;
8. mesačne retire-nuť rules bez action.

### Acceptance verdict

Recovery je prijatá, keď:

- controlled settlement burn vytvorí jednu canonical external page;
- notification obsahuje user impact, scope, ownera a safe first action;
- cause signals zostanú dostupné bez duplicate paging;
- same incident sa deduplikuje aj pri HA retry;
- forbidden cross-environment inhibition a broad silence nefungujú;
- resolved notification uzavrie ten istý external incident;
- actionable rate a pages-per-incident sa zlepšia;
- druhý canary po rule reload-e zachová celý path.

## 13. Runbook a notification content

Dobrá notification obsahuje symptom, affected population, start/duration, current value, SLO/burn, ownera, runbook a investigation links.

Runbook obsahuje:

1. význam a non-meaning alertu;
2. safety checks;
3. user-impact validation;
4. top hypotheses a discriminating queries;
5. containment options;
6. escalation/rollback;
7. resolution a forbidden-outcome validation;
8. evidence preservation.

## 14. Alert as Code a testovanie

Versionuj:

- rules a recording dependencies;
- routing/grouping/inhibition;
- templates a receiver references;
- ownership a runbook metadata;
- fixtures a expected alert instances.

Pipeline:

```text
lint/schema
→ PromQL/query fixtures
→ pending/firing/resolved tests
→ label/cardinality policy
→ route/inhibition/silence fixtures
→ receiver sandbox
→ staged runtime reload
→ synthetic end-to-end alert
→ resolved closure
```

Source validation nestačí. Treba overiť loaded rule/policy generation a external acknowledgement.

## 15. Metamonitoring

```text
known canary signal
→ rule evaluation
→ firing identity
→ Alertmanager/Grafana policy
→ receiver request
→ external incident
→ test acknowledgement
→ resolved closure
```

Monitoruj rule failures, missed evaluations, notification queue, route outcomes, receiver failures, template errors a canary latency.

## 16. Troubleshooting model

### Condition sa nespustila

```text
source population
→ query result
→ rule loaded generation
→ evaluation interval/errors
→ windows/for/no-data
→ alert identity
```

### Firing bez notification

```text
producer send
→ Alertmanager/policy receive
→ route/group timing
→ silence/mute/inhibition
→ receiver/template
→ external response/incidence key
```

### Duplicate pages

```text
multiple rule engines
→ inconsistent labels/fingerprints
→ HA replica labels
→ route continue/fan-out
→ receiver retry/unknown outcome
→ external dedup key
```

### Flapping

```text
baseline a threshold
→ window/scrape gaps
→ unstable denominator
→ for/keep_firing_for
→ dynamic labels
→ actual periodic failure
```

## 17. Anti-patterny

### Page na každý failure mode

Jeden symptom vytvorí notification storm.

### Auto-resolved ako quality proof

Ak človek nemusel konať, page mohol byť zbytočný.

### Dashboard threshold ako alert policy

Farba nemá ownership, routing ani acknowledgement.

### Duplicate engines bez autority

Rovnaký symptom vytvorí viac incidents a odlišné recovery states.

### Permanentná silence

Vytvorí blind spot bez closure.

### Alert bez forbidden action

Responder môže noise alebo incident zhoršiť nebezpečným broad changeom.

## 18. Kontrolné otázky

1. Čo tvorí exact alert subject?
2. Kedy signal pageuje, vytvorí ticket alebo zostane eventom?
3. Prečo symptom page typicky prevyšuje cause page?
4. Čo musí obsahovať action contract?
5. Ako burn-rate windows a `for` menia detection?
6. Prečo no-data nie je zero?
7. Ako labels vytvárajú alert a external incident identity?
8. Ako grouping, inhibition a silence menia notification outcome?
9. Prečo duplicate alerting engines zvyšujú fatigue?
10. Ktoré metrics dokazujú alert quality?
11. Ako testovať alert od signal-u po resolved acknowledgement?
12. Ako retire-nuť stale alebo neakčný page?

## Glossary impact

Relevantné pojmy: alert-action subject, page eligibility contract, action contract, signal-population contract, alert-rule generation, notification-policy generation, external incident identity, pages-per-incident, actionable-rate verdict, alert-control-plane authority, canonical symptom page, cause-signal demotion, alert-fatigue feedback loop, alert retirement verdict a end-to-end alert acceptance.

## Primárne zdroje

- [Prometheus alerting practices](https://prometheus.io/docs/practices/alerting/)
- [The Zen of Prometheus](https://prometheus.io/docs/practices/the_zen/)
- [Prometheus alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Google SRE — Practical Alerting](https://sre.google/sre-book/practical-alerting/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OpenTelemetry](opentelemetry.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Cardinality →](cardinality.md)
<!-- KNOWLEDGE-NAVIGATION:END -->