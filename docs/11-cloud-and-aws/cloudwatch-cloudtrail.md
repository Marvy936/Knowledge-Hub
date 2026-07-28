# Amazon CloudWatch a AWS CloudTrail

Amazon CloudWatch a AWS CloudTrail produkujú odlišné dôkazové vrstvy. CloudWatch opisuje stav a správanie systému cez metrics, logs, alarms, dashboards a queries. CloudTrail zaznamenáva AWS API a account activity: kto, kedy, z akej session, nad akým resource a s akým výsledkom vykonal podporovanú operáciu. Ani jedna služba sama nevysvetlí celý incident.

Dominantný evidence lifecycle:

```text
operational, security alebo audit otázka
→ exact resource/release/request/time subject
→ signal alebo API event generation
→ collection a delivery
→ identity/dimensions/schema
→ retention, protection a queryability
→ evaluation alebo investigation
→ correlation naprieč vrstvami
→ rozhodnutie a action
→ outcome validation
→ evidence closure a recurrence control
```

Telemetry nie je pravda iba preto, že existuje dashboard. Audit event nie je business dôkaz iba preto, že API call skončil `Success`.

## 1. Exact observability a audit subject

Atlas Payments používa subject `OBS-PAY-42`:

```text
account = 100000000042
Region = eu-central-1
business service = payments-api
release = 7.18.0
deployment generation = ECS-DEP-75
load balancer/target group generation = ALB-PAY-19 / TG-PAY-31
Lambda consumer generation = ALIAS-PAY-32
database generation = DB-PAY-42
business request = payment P-944
correlation ID = corr-944
incident window = 2026-07-28T10:15:00Z..10:42:00Z

CloudWatch metric contract =
  namespace = Atlas/Payments
  metric = SuccessfulAuthorizations
  dimensions = Environment=prod, Service=payments-api, Release=7.18.0
  period = 60 s
  statistic = Sum
  expected cadence = every 60 s

alarm generation = ALARM-PAY-SUCCESS-18
missing data = breaching
evaluation = 3 of 5 periods
action = SNS → Systems Manager Automation ARM-PAY-7

log contract =
  log group = /atlas/prod/payments-api
  schema generation = LOG-PAY-24
  retention = 90 days
  indexed fields = correlationId, paymentId, release
  data-protection policy generation = DPP-PAY-6

CloudTrail contract =
  organization multi-Region trail = org-audit-v9
  S3 archive generation = AUDIT-BKT-11
  management events = enabled
  selected data events = governed selectors
  log-file integrity validation = enabled
  retention/lifecycle generation = RET-AUDIT-14

required outcome =
  operational symptom is detected with correct cohort and time identity
  API change is attributable to actual principal/session
  automation is bounded and validates business recovery
  evidence remains queryable and protected

forbidden outcomes =
  missing telemetry is silently interpreted as healthy
  wrong dimension alarms on an obsolete time series
  alarm action loops without checking application outcome
  Event history is treated as long-term complete audit archive
  CloudTrail success is treated as proof that desired state was realized
  sensitive payment payloads are retained unredacted
```

Evidence musí uvádzať account, Region, resource/release generation, exact metric identity, alarm configuration/history, log schema and ingestion timeline, CloudTrail event ID/request ID, assumed-role session chain, automation execution ID a business result.

## 2. CloudWatch odpovedá na otázku „ako sa systém správa“

CloudWatch zahŕňa viac dátových modelov:

- metrics pre bounded time-series;
- Logs pre event records;
- alarms ako evaluation state machines;
- dashboards a investigations;
- query mechanisms ako Metrics Insights a Logs Insights;
- integrácie pre notification a remediation.

CloudWatch neobjaví automaticky všetky potrebné signály. AWS service metrics môžu pokrývať infrastructure behavior, ale application memory, queue business age, payment success alebo release identity treba emitovať explicitne.

## 3. Metric identity je contract, nie label na grafe

CloudWatch metric time series identifikuje kombinácia:

```text
namespace
+ metric name
+ complete dimension set
+ Region/account context
```

`Service=payments-api` a `Service=payments` sú dve odlišné series. Pridanie `Release=7.18.0` nevylepší existujúcu metric; vytvorí ďalšiu identitu.

Dimensions majú byť bounded a operationally meaningful. Request ID, payment ID alebo user ID ako dimension vytvára high-cardinality explosion. Takéto identity patria do logs alebo traces; metric má agregovať rozhodnuteľný cohort.

Unit, timestamp, resolution a publication cadence sú súčasťou contractu. Hodnota `0` a missing datapoint nie sú to isté.

## 4. Statistic a period menia význam signálu

Alarm alebo graph vyhodnocuje datapoints podľa periodu a statistic:

```text
raw samples
→ period aggregation
→ Sum/Average/Min/Max/percentile alebo query
→ threshold evaluation
```

`Average latency` môže skryť poškodený tail alebo jednu AZ. `Sum` error count bez traffic denominatora môže vyzerať horšie počas špičky. Percentile pri malom počte samples má iný význam než pri stabilnom veľkom cohort-e.

Signal contract má vysvetliť:

- čo sample znamená;
- aký cohort pokrýva;
- aká agregácia je správna;
- aký delay a cadence sa očakáva;
- ktorý business decision z neho vzniká.

## 5. Missing data je explicitný stav

Missing datapoint môže znamenať:

- workload je idle a nič nepublikuje;
- agent/exporter zlyhal;
- resource prestal existovať;
- dimension/schema sa zmenila;
- network alebo ingestion path zlyhal;
- query už nevracia series;
- telemetry pipeline mešká.

Alarm môže podľa konfigurácie missing data považovať za `breaching`, `notBreaching`, `ignore` alebo `missing`. Správna voľba závisí od semantics.

Heartbeat alebo expected periodic success metric má missing často považovať za incident telemetry alebo služby. Sporadický error counter bez eventov nemusí publikovať nulu; missing preto nesmie automaticky znamenať error-free.

Najbezpečnejší model často oddeľuje:

```text
business outcome alarm
+ telemetry freshness alarm
+ dependency/resource alarms
```

## 6. Alarm je state machine

Metric alarm kombinuje:

- metric/query identity;
- period a statistic;
- threshold/comparison;
- evaluation periods;
- datapoints to alarm;
- missing-data behavior;
- actions;
- current/history state.

Stavy `OK`, `ALARM` a `INSUFFICIENT_DATA` opisujú evaluation, nie business reality. Alarm môže byť `OK`, lebo sleduje wrong dimension. Môže byť `ALARM`, hoci application je zdravá a publisher zmenil schema.

Composite alarm kombinuje stavy underlying alarms. Pomáha pri suppression a korelácii, ale komplexná boolean logika môže skryť root signal. Underlying alarm identity a runbook musia zostať viditeľné.

Alarm action je ďalší distributed workflow:

```text
alarm transition
→ action delivery
→ target authorization
→ automation admission
→ mutation
→ reconciliation
→ application validation
```

Každý krok môže zlyhať alebo sa opakovať.

## 7. Dashboards majú podporovať rozhodnutie

Operational dashboard má vrstvy:

```text
business outcome
→ client/service SLI
→ dependency behavior
→ resource saturation
→ release/configuration/audit changes
```

Dashboard plný CPU, memory a request countov môže byť technicky bohatý a prevádzkovo slabý. Pri payment incidente musí byť viditeľné: authorization success, latency, duplicate rate, queue age, release cohort, dependency errors a recent changes.

Dashboard nie je alerting contract. Screenshot nie je durable incident evidence, pokiaľ neobsahuje query/time/cohort identity.

## 8. CloudWatch Logs sú schema a lifecycle boundary

Log event prechádza:

```text
application/agent emission
→ local buffering/stdout
→ transport
→ log group a stream
→ ingestion timestamp
→ retention/protection
→ index/query/subscription
→ incident decision
```

Log group definuje policy boundary pre retention, KMS, access, data protection, class a subscriptions. Infinite retention zvyšuje cost aj data exposure.

Structured log má niesť stabilné fields, napríklad:

```json
{
  "timestamp": "2026-07-28T10:21:14Z",
  "service": "payments-api",
  "release": "7.18.0",
  "correlationId": "corr-944",
  "paymentId": "P-944",
  "operation": "authorize",
  "outcome": "success",
  "durationMs": 183
}
```

Secret, token, authorization header, card data alebo celý incoming payload sa nesmie logovať bez classification a masking contractu.

## 9. Logs Insights a field indexes

Logs Insights umožňuje parse, filter, aggregate a correlate logs v časovom okne. Query cost a latency závisia od scanned volume a log class/capabilities.

Field indexes môžu pri podporovaných queries znížiť scan volume tým, že preskočia events, ktoré indexované field/value neobsahujú. Index nie je úplnosť ani correctness garancia. Query musí stále definovať exact time range, log groups, field schema a expected source coverage.

Praktický investigation chain:

```text
paymentId/correlationId
→ application request log
→ downstream/provider log
→ task/Lambda release
→ target/AZ
→ database transaction
→ audit change
```

## 10. Metric filters a Embedded Metric Format

Metric filter vytvára metric z matching log events. Embedded Metric Format umožňuje extrahovať metrics zo structured logs.

Výhoda je jednoduchšie spojenie contextu a metric emission. Riziká:

- parser/schema change zastaví alebo zmení series;
- duplicate log delivery môže skresliť count;
- high-cardinality dimensions zvýšia cost;
- delayed ingestion oneskorí alarm;
- filter môže potichu prestať matchovať.

Metric extraction pipeline potrebuje test s positive aj forbidden samples a alarm na telemetry freshness.

## 11. Agent a collection path

CloudWatch agent môže zbierať guest OS metrics, logs a ďalšie podporované telemetry. EC2 infrastructure metrics automaticky neobsahujú všetky guest údaje, napríklad filesystem alebo memory usage.

Agent potrebuje:

```text
valid configuration
→ running process
→ readable source
→ local disk/buffer headroom
→ IAM
→ DNS/network/TLS endpoint path
→ log/metric destination
→ ingestion evidence
```

Missing logs sa nemajú riešiť iba v CloudWatch console. Node-side agent logs a buffer state môžu odlíšiť emission failure od delivery failure.

## 12. Centralizácia a cross-account observability

Monitoring account môže získať visibility do source accounts podľa CloudWatch cross-account modelu. Centralizácia znižuje context switching a umožňuje cross-account views.

Stále treba definovať:

- account/Region coverage;
- source enrollment;
- least-privilege access;
- naming a tags;
- retention a data residency;
- incident break-glass;
- cost allocation;
- fallback pri výpadku central plane-u.

Central dashboard nesmie byť jediný spôsob, ako overiť local production state.

## 13. CloudTrail odpovedá na otázku „kto vykonal akú AWS operáciu“

CloudTrail event typicky nesie:

- `eventTime`;
- `eventSource` a `eventName`;
- Region;
- `userIdentity`;
- assumed-role/session issuer context;
- source IP a user agent;
- request parameters a response elements podľa eventu;
- resources;
- request ID a event ID;
- error code/message;
- event category.

Nie každé pole je vždy prítomné a citlivé hodnoty môžu byť redacted. `userIdentity` treba rozbaliť až na session issuer, source identity a automation chain; display name roly sám nemusí identifikovať človeka alebo pipeline.

## 14. Management, data a network activity events

### Management events

Control-plane operations, napríklad `UpdateService`, `PutMetricAlarm`, zmena Security Group alebo role.

### Data events

High-volume data-plane operations nad vybranými resources, napríklad S3 object access alebo Lambda invoke podľa selectorov a podporovaných typov.

### Network activity events

Podľa podporovaných services zaznamenávajú vybrané network activity cez VPC endpoints a výsledok authorization/connectivity vrstvy.

Coverage nie je automatická. Data a network activity events sa vyberajú cez selectors a môžu mať významný volume/cost. Incident runbook musí vedieť, či exact resource/action bola vôbec configured na logging.

## 15. Event history nie je dlhodobý audit archive

CloudTrail Event history poskytuje posledných 90 dní management events pre account v aktuálnom Region context-e. Je vhodný na rýchle lookup.

Nie je náhradou za:

- ongoing trail;
- organization-wide coverage;
- data/network activity events;
- dlhodobú retention;
- protected central archive;
- custom cross-account query model.

Ak incident vyžaduje event spred 120 dní, Event history ho neposkytne.

## 16. Trail je delivery contract

Trail vyberá events a priebežne ich doručuje do S3; môže mať ďalšie integrations podľa configuration.

Production baseline typicky obsahuje:

```text
multi-Region alebo organization scope
→ management-event coverage
→ governed data/network selectors
→ central S3 destination
→ bucket a KMS policy
→ log-file integrity validation
→ retention/lifecycle
→ monitoring zmeny a delivery failure
```

Organization trail potrebuje trusted access/delegated administration a log archive account. Member workload admin nemá mať jednoduchú možnosť odstrániť central audit evidence.

## 17. Log-file integrity validation má presný význam

CloudTrail môže doručovať digest files pre integrity validation. Zapnutie feature iba produkuje potrebné digest records; validáciu treba reálne vykonať.

Integrity validation môže preukázať, že delivered log file nebol po delivery zmenený alebo vymazaný v rámci validovaného chainu. Nezaručuje:

- že selector zachytával required event;
- že trail bol vždy enabled;
- že event service field obsahuje všetok business context;
- že S3 retention/access model je správny;
- že application outcome zodpovedal API callu.

## 18. CloudTrail Lake availability je časovo citlivý design constraint

AWS dokumentácia uvádza, že CloudTrail Lake od 31. mája 2026 nie je otvorený novým zákazníkom; existujúci zákazníci ho môžu ďalej používať podľa service availability contractu. Nová architektúra preto nesmie predpokladať, že event data store možno pre nový customer/account model vždy založiť.

Alternatívny query/archive model môže používať protected S3 trail delivery a služby ako Athena, Glue, OpenSearch alebo SIEM podľa requirements. Presná voľba musí zachovať schema, retention, tamper protection, query performance a cost.

## 19. CloudWatch a CloudTrail sa korelujú cez time a identity

Príklad deployment incidentu:

```text
CloudWatch
→ business failures začali 10:21
→ iba release 7.18.0 a AZ-b cohort
→ target errors a dependency latency

CloudTrail
→ UpdateService o 10:18
→ assumed role pipeline-prod
→ task definition 119
→ request ID a source session

ECS/application/database evidence
→ ktorý task prijal corr-944
→ aký secret/config/image mal
→ kde transaction zlyhala
```

CloudTrail ukáže zmenu desired state. Neoverí, že všetky tasks skutočne spustili novú revision. CloudWatch ukáže symptom. Neidentifikuje automaticky človeka alebo pipeline, ktorá zmenu vykonala.

## 20. Automated remediation je kontrolovaný change workflow

Bezpečný chain:

```text
validated symptom
→ bounded alarm condition
→ notification/approval podľa risku
→ scoped automation role
→ idempotent mutation
→ controller convergence
→ technical a business validation
→ rollback/escalation
→ audit closure
```

Automation musí mať:

- exact target generation;
- max concurrency/error budget;
- deduplication;
- cooldown;
- stop condition;
- precondition a postcondition;
- evidence preservation;
- rollback alebo escalation path.

Restart môže odstrániť volatile evidence a dočasne maskovať root cause. Alarm action bez business validation nie je remediation.

## 21. Worked failure: wrong metric identity spustí remediation loop

Release 7.18.0 zmení structured telemetry field z `Service=payments-api` na `Service=payments`. Application naďalej úspešne autorizuje platby, ale alarm sleduje starú series.

### Competing hypotheses

1. payment authorizations skutočne klesli na nulu;
2. metric publisher alebo log filter zlyhal;
3. dimension/schema sa zmenila;
4. ingestion mešká;
5. alarm query sleduje wrong Region/account;
6. automation action zlyhala a opakuje sa.

### Discriminating evidence

Business ledger a provider success count sú stabilné. Logs pre release 7.18.0 prichádzajú, ale EMF events používajú dimension `Service=payments`. `ListMetrics`/query ukáže novú time series; stará `Service=payments-api` po rollout-e prestala publikovať.

Alarm generation `ALARM-PAY-SUCCESS-18` má missing data `breaching`. Po troch missing periods prejde do `ALARM` a spustí `ARM-PAY-7`, ktorá force-ne ECS deployment. Nové tasks znova emitujú iba novú dimension, takže alarm ostáva v slučke.

CloudTrail korelácia ukáže:

```text
10:18 UpdateService → release 7.18.0
10:21 old metric series missing
10:24 alarm ALARM
10:24 StartAutomationExecution ARM-PAY-7
10:25 UpdateService forceNewDeployment
10:30 repeated automation execution
```

Až opakované deploymenty znížia healthy capacity a vytvoria reálne payment errors. Root cause nie je prvotný business outage, ale telemetry contract drift + missing-data semantics + remediation bez postcondition.

### Evidence-preserving containment

- alarm action sa disable-ne alebo automation target sa pozastaví;
- alarm a execution history sa zachová;
- healthy task cohort sa prestane zbytočne recyklovať;
- business success sa overí nezávislým ledger/provider query;
- telemetry gaps sa označia ako observability incident, nie automaticky service failure.

### Authoritative recovery

1. schválená metric identity sa obnoví alebo versionuje ako nový contract;
2. publisher aj alarm sa deploynú kompatibilne;
3. samostatný telemetry-freshness alarm sleduje expected emission;
4. business success alarm používa numerator/denominator a správny cohort;
5. remediation vyžaduje symptom + telemetry-validity precondition;
6. automation používa cooldown, execution deduplication a post-action business validation;
7. alarm sa testuje syntetickým breach, missing a recovery scenárom.

### Acceptance verdict

Incident je uzavretý, keď:

- approved metric series publikuje v každom period-e;
- alarm prechádza správne cez `OK`, `ALARM`, `INSUFFICIENT_DATA`;
- missing publisher vyvolá telemetry incident, nie nekonečný service restart;
- exact business failure vyvolá jeden bounded remediation execution;
- CloudTrail vie priradiť zmenu alarmu aj automation k session;
- dashboard rozlišuje release/AZ a neagreguje poškodený cohort;
- payment authorization SLO je obnovené;
- forbidden test so zmenenou dimension neaktivuje destructive loop.

Skorší control: observability contract test porovná expected namespace, metric, dimensions, cadence, log schema, alarm query, missing-data semantics a automation postcondition ešte pred promotion release-u.

## 22. Troubleshooting CloudWatch

### Alarm zostáva `INSUFFICIENT_DATA`

Over exact metric identity, Region/account, query result, publication cadence, period, missing-data behavior a resource existence. Nezačínaj zmenou threshold-u.

### Metric existuje, alarm nereaguje

Porovnaj dimension set, statistic, unit, period, datapoints-to-alarm, time alignment a alarm history. Graph môže zobrazovať inú aggregation než alarm.

### Logs chýbajú

Rozlíš application emission, stdout/file path, agent/runtime, local buffer, IAM, network endpoint, log-group identity, retention/deletion a subscription transformation.

### Query nič nenájde

Over time zone/window, source log groups, ingestion time, field/schema generation, parsing a index applicability. Absencia query resultu nie je automaticky absencia udalosti.

## 23. Troubleshooting CloudTrail

### Event nenájdeš

Over account, Region, event time, event category, trail/selectors, global-service semantics, exact API event name a caller. Event history obsahuje iba recent management events.

### Trail nedoručuje do S3

Over trail status, bucket prefix/policy, KMS key policy, service principal, Region, destination ownership a CloudTrail delivery errors.

### Actor nie je jasný

Analyzuj `userIdentity`, assumed-role ARN, principal ID, session issuer, source identity, user agent, source IP, request ID a upstream automation/audit record.

### API success, ale resource je wrong

CloudTrail dokazuje accepted API operation, nie eventual reconciliation. Pokračuj service events, resource state, controller, runtime a business acceptance.

## 24. Security, retention a cost

Chráň:

- log group a archive policies;
- KMS keys;
- CloudTrail configuration;
- delete/lifecycle permissions;
- root a break-glass events;
- data-protection/masking policies;
- query/export roles;
- subscription destinations;
- alarm a automation mutation permissions.

Cost drivers:

```text
custom metric series a resolution
+ alarms/queries
+ log ingestion a retention
+ Logs Insights scan
+ subscription/export
+ CloudTrail paid copies/data/network events
+ archive/query platform
```

Cardinality a debug payload môžu zvýšiť cost rádovo viac než samotný počet services. Cost control nesmie odstrániť required audit coverage alebo skrátiť retention pod incident/compliance window.

## 25. Kontrolné otázky

1. Aký je rozdiel medzi operational telemetry a audit evidence?
2. Čo tvorí exact CloudWatch metric identity?
3. Prečo missing datapoint nie je nula?
4. Ako alarm action vzniká ako samostatný distributed workflow?
5. Čo má obsahovať rozhodovací dashboard?
6. Aký je rozdiel medzi CloudTrail management, data a network activity eventom?
7. Čo Event history poskytuje a čo neposkytuje?
8. Čo log-file integrity validation dokazuje a čo nie?
9. Ako koreluješ CloudWatch symptom s CloudTrail change eventom?
10. Aké gates potrebuje bezpečná automated remediation?

## Glossary impact

Relevantné pojmy: observability evidence subject, metric identity contract, telemetry freshness, alarm evaluation generation, missing-data verdict, evidence coverage, audit-delivery contract, actor-session chain, realization gap, remediation execution subject a observability acceptance verdict.

## Oficiálna dokumentácia

- [Amazon CloudWatch](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html)
- [CloudWatch metrics concepts](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_concepts.html)
- [CloudWatch alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Alarms.html)
- [Missing data in alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/alarms-and-missing-data.html)
- [Amazon CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html)
- [CloudWatch Logs field indexes](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CloudWatchLogs-Field-Indexing.html)
- [AWS CloudTrail](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html)
- [CloudTrail events](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-events.html)
- [CloudTrail Event history](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html)
- [CloudTrail trails](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-trails.html)
- [CloudTrail log-file integrity validation](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html)
- [CloudTrail Lake availability change](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake-service-availability-change.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: ECS a EKS](ecs-eks.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Systems Manager →](systems-manager.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
