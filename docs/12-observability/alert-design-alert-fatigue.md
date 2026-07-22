# Alert design a alert fatigue

Alert nie je graf, threshold ani informácia, že sa niečo zmenilo. Alert je prevádzkový contract, ktorý má správneho človeka alebo automatizáciu priviesť k včasnej a zmysluplnej akcii. Zlý alerting vytvára hluk, prerušuje sústredenie, znižuje dôveru v monitoring a môže spôsobiť, že kritický incident zostane nepovšimnutý.

## 1. Mentálny model

```text
user alebo business symptom
→ merateľný signal
→ stabilná alert condition
→ pending/firing lifecycle
→ grouping, inhibition a routing
→ správny receiver
→ actionable notification
→ runbook a investigation context
→ potvrdenie alebo automatická remediation
→ resolution a review
```

Alerting má optimalizovať čas k správnej reakcii, nie počet detegovaných anomálií.

## 2. Page, ticket a informational signal

### Page

Vyžaduje rýchlu ľudskú reakciu, pretože:

- existuje významný aktuálny alebo bezprostredný user impact,
- automatická remediation nestačí,
- oneskorenie zvyšuje škodu,
- responder má konkrétnu akciu.

### Ticket

Vyžaduje prácu, ale nie okamžité prerušenie:

- capacity sa blíži k limitu v horizonte dní,
- certificate expiruje o niekoľko týždňov,
- backup coverage chýba pre nový resource,
- deprecated API bude odstránené,
- recurring non-urgent error potrebuje engineering fix.

### Informational event

Je užitočný pre correlation alebo review, ale nemá vytvárať alert notification:

- deployment marker,
- autoscaling event,
- config reload,
- instance replacement,
- transient failover, ktorý prebehol podľa designu.

Dashboard, event stream alebo report je často vhodnejší než page.

## 3. Actionability

Každý alert musí odpovedať:

- Kto je owner?
- Aký je user alebo business impact?
- Čo má responder urobiť teraz?
- Ako dlho možno čakať?
- Kde je runbook a relevantný dashboard?
- Ako sa overí resolution?

Alert bez možnej akcie nemá byť page.

Príklady neakčných pages:

- CPU prekročilo 80 % bez saturation alebo impactu,
- jeden Pod sa reštartoval a Deployment zostal healthy,
- jedna batch execution zlyhala, ale ďalší run má dostatok času a retry funguje,
- disk usage je 70 % bez growth forecastu,
- certifikát expiruje o 90 dní.

## 4. Symptom oproti príčine

Preferuj alerts na symptómy vysoko v stacku:

- error-rate SLO burn,
- latency SLO burn,
- unavailable user journey,
- queue freshness prekračujúca business limit,
- data correctness failure,
- kritická capacity saturation.

Príčiny patria do investigation telemetry:

- CPU,
- GC,
- disk queue,
- konkrétna dependency,
- Pod restarts,
- packet loss.

Cause alert je vhodný, keď:

- spoľahlivo predpovedá bezprostredný impact,
- responder musí zasiahnuť skôr než vznikne symptom,
- failure by inak nebol merateľný na user boundary,
- ide o bezpečnostný alebo integrity incident.

## 5. Alert condition

Dobrá condition má:

- jasný signal contract,
- správny scope,
- stabilný denominator,
- vhodné time window,
- explicitné no-data správanie,
- ochranu proti krátkym blipom,
- validovaný threshold,
- bounded labels.

Príklad request error ratio:

```promql
sum(rate(http_requests_total{service="orders",status_class="5xx"}[5m]))
/
sum(rate(http_requests_total{service="orders"}[5m]))
> 0.05
```

Táto condition stále potrebuje:

- minimálny traffic guard,
- definíciu valid requestov,
- SLO alebo business threshold,
- `for` alebo burn-rate model,
- ownership labels.

## 6. Threshold alerting

Static threshold je vhodný, keď:

- limit je fyzický alebo explicitný,
- signal má stabilnú interpretáciu,
- threshold súvisí s impactom,
- seasonality nie je dominantná.

Príklady:

- filesystem zostáva menej než 5 % free a rast pokračuje,
- certificate expiruje pod definovaný horizon,
- queue oldest message age prekročil business SLA,
- quota headroom je pod failover requirementom.

Nevhodné:

- CPU > 80 % pre každý workload,
- memory > 90 % bez pressure,
- latency > fixná hodnota bez operation scope-u,
- request count pod arbitrary threshold bez expected traffic modelu.

## 7. SLO a burn-rate alerting

SLO-based alerting sleduje, ako rýchlo sa spotrebúva error budget.

Výhody:

- page je naviazaný na user outcome,
- threshold sa prispôsobí reliability targetu,
- rozlišuje krátky prudký outage a dlhú miernu degradáciu,
- redukuje noise z malých neškodných odchýlok.

Multi-window model typicky kombinuje:

- krátke okno pre rýchly detection,
- dlhšie okno na potvrdenie sustained impactu,
- fast-burn a slow-burn policies.

SLO alert musí mať presný numerator, denominator, measurement point a exclusion contract.

## 8. Anomaly detection

Anomaly detection je vhodná ako:

- exploratory signal,
- ticket,
- doplnok k known thresholds,
- detection nezvyčajného costu alebo trafficu.

Riziká:

- seasonality,
- model drift,
- maintenance a deployments,
- nejasná actionability,
- vysoký false-positive rate,
- alert na neobvyklé, ale zdravé správanie.

Anomália nie je automaticky incident.

## 9. `for` a pending state

Prometheus `for` vyžaduje, aby condition zostala aktívna určitý čas pred prechodom do firing stavu.

Použitie:

- odstránenie krátkych transientov,
- čakanie na autoscaling alebo self-healing,
- stabilizácia noisy metrics.

Riziká:

- príliš dlhé `for` oneskorí kritický detection,
- condition môže resetovať pri missing sample,
- pravidelný krátky failure nikdy neprejde do firing,
- pre SLO burn môže byť lepší multi-window model než arbitrary `for`.

`keep_firing_for` môže obmedziť flapovanie po krátkom zmiznutí condition, ale nesmie maskovať skutočný recovery contract.

## 10. No data

No data nie je automaticky healthy ani unhealthy.

Možné významy:

- traffic je legitímne nulový,
- target neexistuje,
- scrape/export zlyhal,
- query labels sa zmenili,
- deployment odstránil metric,
- telemetry pipeline je pokazená,
- service je úplne nedostupná.

Pre každý alert definuj:

- no-data behavior,
- expected traffic model,
- metamonitoring,
- black-box fallback,
- schema-change detection.

Nulový error rate bez trafficu nie je dôkaz zdravia.

## 11. Alert identity

Alert identity vzniká z labels.

Stabilné labels:

- `alertname`,
- `service`,
- `team`,
- `severity`,
- `environment`,
- `cluster`,
- bounded operation alebo region.

Dynamické hodnoty patria do annotations:

- current value,
- hostname list,
- error message,
- free-form description,
- query result.

Dynamic label vytvára nové fingerprints, poškodzuje deduplication, silences a routing.

## 12. Severity

Severity nemá znamenať iba technickú veľkosť čísla.

Príklad modelu:

- `page` — okamžitá ľudská reakcia,
- `ticket` — plánovaná engineering práca,
- `info` — correlation alebo reporting.

Alternatívne organization-specific P1/P2/P3 musí mať explicitné response expectations.

Severity nemá byť odvodená len z environmentu. Production warning bez akcie nemá byť page; security incident v non-production môže byť kritický.

## 13. Ownership

Každý alert musí mať ownera.

Ownership metadata:

- team,
- service,
- escalation policy,
- runbook,
- repository alebo service catalog entry.

Default receiver nemá byť odpadkový kôš pre alerts bez ownershipu. Chýbajúci owner má byť validation failure.

## 14. Notification content

Dobrá notification obsahuje:

- stručný symptom,
- affected service a environment,
- user/business impact,
- začiatok a duration,
- current value a threshold,
- relevantné labels,
- runbook,
- dashboard/Explore link,
- trace/log link,
- recent deployment alebo change,
- silence/acknowledgement link.

Notification nemá obsahovať:

- obrovský dump všetkých labels,
- secrets alebo PII,
- neformátovaný stack trace,
- neurčitú správu typu „Something is wrong“.

## 15. Runbook

Runbook má obsahovať:

1. čo alert znamená,
2. čo neznamená,
3. immediate safety checks,
4. user impact validation,
5. top pravdepodobné príčiny,
6. relevantné queries,
7. remediation options,
8. rollback alebo escalation,
9. hard validation resolution,
10. evidence, ktoré sa má zachovať.

Runbook musí byť testovaný a udržiavaný. Neexistujúci alebo neaktuálny link znižuje actionability.

## 16. Grouping

Grouping znižuje počet notifications počas spoločného incidentu.

Dobré grouping dimensions:

- alertname,
- cluster,
- service,
- environment.

Príliš detailné grouping:

- instance,
- Pod,
- request ID.

Výsledok: stovky notifications.

Príliš broad grouping môže spojiť nesúvisiace incidenty a skryť ownership.

Grouping má zachovať správny routing a investigation scope.

## 17. Inhibition

Inhibition potlačí downstream alerts, keď je známy nadradený incident.

Príklad:

```text
ClusterUnavailable firing
→ inhibit PodDown, NodeExporterDown a ServiceScrapeFailed v rovnakom clustri
```

Inhibition musí používať shared scope labels.

Riziká:

- broad matcher potlačí nezávislý incident,
- root-cause alert sa sám nevytvorí,
- scope labels nesedia,
- security alert je potlačený infra alertom.

Potlačené alerts majú zostať viditeľné v UI a post-incident analýze.

## 18. Silences a maintenance

Silence je dočasné potlačenie podľa matchers.

Použitie:

- plánovaná maintenance,
- známy incident počas remediation,
- krátkodobý test.

Silence musí mať:

- ownera,
- dôvod,
- bounded matchers,
- expiration,
- audit trail.

Nevhodné:

- permanentná silence namiesto opravy alertu,
- regex `.*` cez celý production,
- silence bez expiration,
- použitie silence ako deployment strategy.

Pre pravidelnú maintenance môže byť vhodný mute time interval alebo deployment-aware alert behavior.

## 19. Alert fatigue

Alert fatigue vzniká, keď responder dostáva príliš veľa neakčných, duplicitných alebo nepresných notifications.

Dôsledky:

- alerts sa ignorujú,
- pomalšie acknowledgement,
- vypínanie notifications,
- horší on-call well-being,
- kritický signal sa stratí,
- rast operational toil.

### Typické príčiny

- alert na každú metric,
- cause alerts namiesto symptoms,
- chýbajúce grouping/inhibition,
- flapping,
- nízka precision,
- stale rules,
- duplicitný alerting v rôznych platformách,
- nesprávna severity,
- chýbajúci owner,
- permanentné known issues,
- nevhodné thresholds.

## 20. Alert quality metrics

Sleduj:

- počet pages za on-call shift,
- pages per incident,
- actionable rate,
- false-positive rate,
- duplicate notification rate,
- acknowledged time,
- time to mitigation,
- percent alerts s validným ownerom/runbookom,
- percent auto-resolved bez akcie,
- flapping rate,
- silences a ich vek,
- alerts nikdy nevedúce k action.

„Veľa alerts“ nie je samo osebe kvalita. Dôležitý je pomer signal/action.

## 21. Alert review

Pravidelne kontroluj:

- ktoré alerts pageovali,
- aká akcia nasledovala,
- či alert prišiel včas,
- či bol symptom správny,
- či existovali duplicity,
- či runbook fungoval,
- či notification obsahovala dostatok contextu,
- či sa alert má zrušiť, zmeniť na ticket alebo automatizovať.

Každý incident by mal vyhodnotiť aj alerting gap:

- alert chýbal,
- alert bol neskoro,
- alert bol noisy,
- alert bol správny, ale routing zlyhal.

## 22. Automation

Automatická remediation je vhodná, keď:

- trigger je spoľahlivý,
- action je bounded a idempotentná,
- má safety checks,
- je auditovaná,
- existuje rollback alebo stop condition,
- neeskaluje failure.

Príklady:

- restart jedného stateless workeru,
- scale-out v bezpečnom limite,
- rotate unhealthy instance,
- clear bounded cache,
- open ticket.

Alert po úspešnej automatickej remediation nemusí pageovať človeka, ale event a audit zostávajú dôležité.

## 23. Metamonitoring

Monitoruj celý alert path:

```text
metric/source
→ scrape alebo ingest
→ rule evaluation
→ Prometheus notification queue
→ Alertmanager
→ routing/grouping
→ receiver
→ on-call platform
→ test acknowledgement
```

Použi synthetic canary alert s kontrolovaným lifecycle-om.

Samostatné component health alerts nemusia odhaliť nesprávny routing alebo broken receiver credentials.

## 24. Security alerts

Security alerting má odlišný contract:

- rarity nemusí znamenať nízku dôležitosť,
- evidence retention je kritická,
- attacker môže ovplyvniť telemetry,
- confidentiality a need-to-know routing,
- automation môže byť riskantná,
- false negatives majú vysokú cenu.

Bezpečnostné alerts nemajú byť automaticky inhibited bežným infrastructure incidentom.

## 25. Capacity alerts

Capacity alert má vychádzať z času do vyčerpania a failover requirementu, nie iba percenta.

Príklad:

```text
predicted disk exhaustion < 24h
AND current growth sustained
AND cleanup/autoscaling nereaguje
```

Zohľadni:

- growth rate,
- seasonality,
- recovery time,
- failover capacity,
- deployment surge,
- quotas,
- maintenance window.

Capacity page je oprávnený, ak bez okamžitej akcie hrozí outage skôr, než je možné reagovať bežným ticket workflowom.

## 26. Batch alerts

Pri batch joboch nealertuj automaticky na jeden failed run, ak:

- retry funguje,
- freshness deadline nie je ohrozený,
- ďalší run má dostatočný čas.

Lepšie signals:

- time since last successful completion,
- data freshness,
- repeated failures,
- backlog,
- projected miss business deadline.

## 27. Kubernetes alerts

Noise patterns:

- každý Pod restart,
- jeden Pending Pod počas rolloutu,
- každá Eviction,
- Node NotReady počas kontrolovaného drainu.

Preferuj:

- workload unavailable,
- rollout stuck,
- desired vs available replicas sustained gap,
- Node capacity/failure ohrozujúci redundancy,
- cluster control-plane alebo networking symptom,
- SLO burn.

Topology a owner labels musia byť bounded.

## 28. Testing alerts

Testuj:

- rule syntax,
- query fixtures,
- pending/firing/resolved lifecycle,
- no-data behavior,
- labels a annotations,
- routing,
- grouping,
- inhibition,
- silence matchers,
- templates,
- receiver sandbox,
- end-to-end synthetic alert.

Pri change review zobraz očakávané alert instances pre representative inputs.

## 29. Alert as Code

Ukladaj v Git-e:

- rules,
- route tree,
- inhibition policies,
- notification templates,
- tests,
- ownership metadata,
- runbook references.

Pipeline:

```text
lint a schema
→ unit tests
→ policy checks
→ render/diff
→ staging evaluation
→ controlled rollout
→ metamonitoring
```

UI edits bez exportu vytvárajú drift a slabý audit trail.

## 30. Troubleshooting: alert condition sa nespustila

```text
source metric existuje?
→ správny time range a labels?
→ PromQL result?
→ rule loaded?
→ evaluation errors?
→ evaluation interval?
→ pending `for` state?
→ no-data/staleness?
→ rule group lag?
```

## 31. Troubleshooting: firing, ale bez notification

```text
Prometheus poslal alert?
→ Alertmanager prijal fingerprint?
→ route match?
→ silence?
→ inhibition?
→ group_wait/group_interval?
→ receiver config?
→ template error?
→ external receiver response?
```

## 32. Troubleshooting: duplicate pages

Možné príčiny:

- replica label v alert identity,
- viac Alertmanager clusters bez koordinácie,
- `continue: true`,
- duplicitné rules v Prometheus a Grafane,
- odlišné labels pre rovnaký symptom,
- receiver retry bez deduplication,
- flapping.

## 33. Troubleshooting: flapping

Over:

- threshold pri baseline,
- scrape gaps,
- short window,
- `for`,
- `keep_firing_for`,
- autoscaling oscillation,
- unstable denominator,
- dynamic labels,
- intermittent dependency.

Nezakrývaj reálny periodic failure príliš dlhým `for` bez root-cause analýzy.

## 34. Anti-patterny

### Page na každý failure mode

Jedna user degradácia vytvorí stovky príčinných pages.

### Alert bez ownera

Nikto nevie, kto má reagovať.

### Runbook link iba na homepage dokumentácie

Responder nedostane konkrétny postup.

### Threshold kopírovaný medzi službami

Ignoruje odlišný workload a capacity model.

### Permanentné silences

Maskujú stale alert namiesto jeho opravy.

### „Auto-resolved, teda dobrý alert“

Ak väčšina pages nepotrebovala akciu, alert pravdepodobne vytvára toil.

### Dashboard threshold považovaný za page policy

Vizuálna farba nemá routing, ownership ani notification lifecycle.

### Duplicitné alerting engines bez autority

Prometheus, Grafana a cloud alerts pageujú ten istý symptom.

## 35. Kontrolné otázky

1. Kedy má signal pageovať a kedy vytvoriť ticket?
2. Prečo preferovať symptom alerts?
3. Ako SLO burn-rate alerting redukuje noise?
4. Čo znamená actionability?
5. Ako `for` a `keep_firing_for` menia lifecycle?
6. Ako sa má riešiť no data?
7. Prečo dynamické hodnoty nepatria do labels?
8. Ako grouping, inhibition a silences znižujú hluk?
9. Aké metrics merajú kvalitu alertingu?
10. Ako testovať alert end-to-end?
11. Kedy je vhodná automatic remediation?
12. Ako diagnostikovať duplicate pages?

## Glossary impact

Relevantné pojmy: actionable alert, page, ticket alert, symptom alert, cause alert, alert condition, pending alert, firing alert, resolved alert, burn-rate alert, fast burn, slow burn, no-data policy, alert identity, alert severity, grouping, inhibition, silence, mute interval, alert fatigue, alert precision, alert flapping, metamonitoring, synthetic alert a alert as code.

## Primárne zdroje

- [Prometheus alerting practices](https://prometheus.io/docs/practices/alerting/)
- [Prometheus alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Prometheus Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Google SRE — Practical Alerting from Time-Series Data](https://sre.google/sre-book/practical-alerting/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OpenTelemetry](opentelemetry.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Cardinality →](cardinality.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
