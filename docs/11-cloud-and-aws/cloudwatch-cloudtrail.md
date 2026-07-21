# CloudWatch a CloudTrail

Amazon CloudWatch a AWS CloudTrail riešia odlišné prevádzkové otázky. CloudWatch odpovedá najmä na „ako sa systém správa“, zatiaľ čo CloudTrail odpovedá na „kto, kedy a akou API operáciou zmenil alebo použil AWS resources“. Incident response potrebuje obe vrstvy a často aj application logs, configuration history a network evidence.

## 1. Mentálny model

```text
CloudWatch
metrics + logs + alarms + dashboards + traces/insights
→ operational state a behavior

CloudTrail
API a account activity events
→ actor, action, resource, time, request context a result
```

CloudWatch nie je automaticky audit log všetkých zmien. CloudTrail nie je performance monitoring systém.

## 2. CloudWatch metrics

Metric je time-series identifikovaná:

- namespace,
- metric name,
- dimensions,
- timestamp,
- value,
- unit,
- resolution.

Dimensions tvoria identitu time series. Chybná alebo chýbajúca dimension môže vytvoriť inú metric, než alarm očakáva.

Rozlišuj:

- AWS service metrics,
- custom metrics,
- high-resolution metrics,
- metric math,
- percentile statistics,
- anomaly detection,
- Metrics Insights queries.

Average môže skryť tail latency, krátky saturation alebo imbalance medzi instances.

## 3. Period, statistic a evaluation

Alarm výsledok závisí od:

- period,
- statistic,
- evaluation periods,
- datapoints to alarm,
- threshold/comparison,
- missing-data behavior,
- dimensions/query scope.

Príklad:

```text
3 evaluation periods
2 datapoints to alarm
period 60 s
```

Alarm sa prepne, keď aspoň dva z troch hodnotených datapoints porušia podmienku.

## 4. Missing data

Missing data môže znamenať:

- resource neposlal metric,
- resource neexistuje,
- agent zlyhal,
- dimension sa zmenila,
- pipeline má oneskorenie,
- workload je idle a metric sa nepublikuje.

Možnosti ako `breaching`, `notBreaching`, `ignore` alebo `missing` treba voliť podľa významu signálu. Pre heartbeat je missing typicky problém. Pre sporadický error counter nemusí byť.

## 5. CloudWatch alarms

CloudWatch podporuje:

- metric alarms,
- composite alarms,
- log-derived alarms podľa aktuálnych capabilities,
- actions cez SNS, Auto Scaling alebo ďalšie integrácie.

Alarm má stavy:

- `OK`,
- `ALARM`,
- `INSUFFICIENT_DATA`.

Alarm action nie je remediation guarantee. SNS delivery, target IAM, downstream automation a idempotencia sú samostatné contracts.

## 6. Composite alarms

Composite alarm kombinuje stavy iných alarmov.

Použitie:

- zníženie alert fatigue,
- maintenance suppression,
- korelácia symptom + dependency,
- multi-signal incident condition.

Nevýhoda: príliš zložitá boolean logika môže skryť root signal a sťažiť troubleshooting.

## 7. Dashboards

Dashboard má podporovať rozhodnutie, nie iba zobrazovať všetky metrics.

Vrstvy:

1. business outcome,
2. service SLI,
3. dependency health,
4. resource saturation,
5. deployment/config changes.

Dashboard bez alarm ownershipu a runbooku nie je operational control.

## 8. CloudWatch Logs

CloudWatch Logs používa:

- log group,
- log stream,
- log event,
- retention,
- subscription filter,
- metric filter,
- Logs Insights query.

Log group je policy a lifecycle boundary pre retention, KMS encryption, access a subscriptions.

Nastav explicitne:

- retention,
- data classification,
- masking/redaction,
- cross-account destination,
- ingestion rate a cost guardrails,
- archive/export potrebu.

## 9. CloudWatch Logs Insights

Logs Insights umožňuje interaktívne query nad log groups.

Použitie:

- filter status codes,
- parse structured fields,
- group by service/version,
- analyze latency percentiles,
- correlate request IDs,
- compare before/after deployment.

Query cost a latency závisia od scanned data. Narrow time window, selected fields a structured logs znižujú scan surface.

## 10. Metric filters a Embedded Metric Format

Metric filter vytvára metric z matching log events. Embedded Metric Format umožňuje aplikácii zapisovať structured logs, z ktorých CloudWatch extrahuje metrics.

Riziká:

- high-cardinality dimensions,
- unbounded tenant/request IDs,
- duplicate metrics,
- delayed logs,
- parser changes,
- cost explosion.

Metric dimensions musia byť bounded a operationally meaningful.

## 11. CloudWatch agent

CloudWatch agent môže zbierať:

- OS metrics,
- application/system logs,
- traces podľa konfigurácie,
- StatsD alebo collectd inputs podľa supportu.

Agent potrebuje:

- IAM permissions,
- network path k endpoints,
- configuration,
- service health,
- disk buffer/headroom,
- time synchronization.

EC2 basic metrics neobsahujú automaticky všetky guest OS údaje, napríklad memory utilization alebo filesystem usage.

## 12. Cross-account observability

Central observability model môže agregovať metrics, logs a traces z viacerých accounts/Regions.

Navrhni:

- monitoring account,
- source-account enrollment,
- least-privilege read/share,
- naming a tagging,
- Region coverage,
- data retention a residency,
- incident access,
- cost allocation.

Centralizácia nesmie odstrániť local break-glass visibility pri výpadku shared observability vrstvy.

## 13. CloudTrail events

CloudTrail event typicky obsahuje:

- event time,
- event source a name,
- AWS Region,
- source IP/user agent,
- user identity,
- request parameters,
- response elements,
- resources,
- request ID,
- error code/message.

Nie každé pole je vždy dostupné a citlivé hodnoty môžu byť redacted.

## 14. Management, data a network activity events

### Management events

Control-plane operácie, napríklad vytvorenie role, zmena Security Group alebo stop instance.

### Data events

High-volume operations nad konkrétnymi data-plane resources, napríklad S3 object alebo Lambda invoke podľa selectoru.

### Network activity events

Podľa podporovaných služieb zaznamenávajú network activity cez VPC endpoints a súvisiace výsledky.

Data events nie sú automaticky zahrnuté v každom trail-e a môžu mať významný cost/volume.

## 15. Event history

CloudTrail Event history poskytuje recent management events per Region pre account, aktuálne typicky za posledných 90 dní.

Nie je náhradou za:

- organization-wide trail,
- dlhodobú retention,
- immutable central log archive,
- data events,
- custom query/analytics model.

## 16. Trails

Trail zabezpečuje ongoing delivery events do S3 a voliteľne CloudWatch Logs/EventBridge integrations.

Production baseline:

- multi-Region trail,
- organization trail podľa modelu,
- management events,
- selektívne data events,
- log-file validation,
- KMS encryption podľa requirementu,
- protected central S3 bucket,
- lifecycle/retention,
- alerts na zmenu alebo zastavenie loggingu.

## 17. Organization trail

Organization trail centralizuje coverage member accounts. Potrebuje:

- trusted access/delegated admin podľa modelu,
- log archive account,
- bucket/key policies,
- Region strategy,
- protection pred deletion/tampering,
- onboarding/offboarding validation.

Member account admin nesmie byť schopný jednoducho vymazať central evidence.

## 18. CloudTrail Lake a event data stores

CloudTrail Lake poskytuje event data stores a SQL query model pre audit a investigation. Aktuálna AWS dokumentácia uvádza zmenu dostupnosti: od 31. mája 2026 už služba nie je otvorená novým zákazníkom; existujúci zákazníci ju môžu ďalej používať. Architektúra pre nového zákazníka preto nesmie automaticky predpokladať CloudTrail Lake ako dostupnú voľbu.

Alternatívny analytics model môže používať central S3, Glue/Athena, OpenSearch alebo SIEM podľa requirements.

## 19. CloudTrail Insights

Insights deteguje nezvyčajnú API call alebo error-rate aktivitu pre podporovaný event model.

Nie je to všeobecný threat-detection systém. Findings potrebujú kontext, baseline a koreláciu s identity, resource a security telemetry.

## 20. Integrita a ochrana audit logov

Chráň:

- S3 bucket policy,
- Object Lock/versioning podľa requirementu,
- KMS key policy,
- log-file validation,
- delete/lifecycle permissions,
- cross-account delivery role,
- CloudTrail configuration,
- root a break-glass events.

Audit admin a workload admin nemajú byť rovnaká neobmedzená rola.

## 21. CloudWatch oproti CloudTrail pri incidente

Príklad: RDS CPU náhle stúplo po zmene Security Group.

```text
CloudWatch
→ CPU, connections, latency, errors, alarms

CloudTrail
→ kto zmenil SG, kedy, z akej session, request parameters

VPC Flow Logs / DB logs
→ reálny traffic a query behavior
```

Žiadna jedna vrstva nevysvetlí celý incident.

## 22. EventBridge integrácia

CloudTrail-compatible service events a direct service events možno routovať cez EventBridge na:

- alert,
- automation,
- ticket,
- security response,
- enrichment pipeline.

Event pattern musí byť presný. Broad pattern môže spustiť remediation loop alebo vysoký cost.

## 23. Alarm design

Dobrý alarm má:

- jasný symptom alebo risk,
- ownera,
- severity,
- actionable threshold,
- runbook,
- deduplication/suppression,
- escalation,
- recovery condition,
- test.

Preferuj outcome/signals pred internými low-level metrics, ak low-level signal nie je priamo actionable.

## 24. Automated remediation

Chain:

```text
metric/event
→ alarm/EventBridge rule
→ SNS/Lambda/Systems Manager Automation
→ scoped IAM role
→ idempotent action
→ validation
→ audit a rollback
```

Automated restart bez root-cause guardrails môže vytvoriť loop a odstrániť evidence.

## 25. Troubleshooting CloudWatch

### Alarm ostáva `INSUFFICIENT_DATA`

Over metric namespace/name/dimensions, period, publication frequency, missing-data behavior a Region.

### Metric exists, alarm nereaguje

Over statistic, unit, threshold, evaluation periods, query return a alarm history.

### Logs chýbajú

Over agent/runtime logs, IAM, log group/stream, endpoint/network, retention/deletion a application stdout configuration.

### Logs cost prudko rastie

Over ingestion source, debug level, duplicate subscriptions, retention, high-volume payloads a unbounded structured fields.

## 26. Troubleshooting CloudTrail

### Event nenájdeš

Over account, Region, event type, time window, management/data selector, global service handling a caller event source.

### Trail nedoručuje do S3

Over trail status, bucket policy, KMS key policy, prefix, Region, CloudTrail service principal a error notifications.

### Organization account chýba

Over organization trail status, account membership, delegated admin/trusted access a delivery permissions.

### Kto vykonal zmenu nie je jasný

Analyzuj `userIdentity`, assumed-role ARN, session issuer, source identity, user agent, source IP a request ID.

## 27. SOA-C03 mapovanie

- **Domain 1** — hlavná kapitola pre metrics, logs, alarms, dashboards, analysis, remediation a performance.
- **Domain 2** — monitoring backup/failover health, recovery validation a continuity alarms.
- **Domain 3** — telemetry provisioning, agent deployment, organization trails a automation.
- **Domain 4** — audit evidence, tamper protection, encryption, log access a compliance.
- **Domain 5** — network metrics/logs, DNS/load-balancer telemetry a flow correlation.

Praktické drilly:

- alarm používa chybnú dimension,
- missing data je nesprávne považované za OK,
- CloudWatch agent nemá IAM alebo endpoint path,
- organization trail bucket policy blokuje delivery,
- data events nie sú zapnuté pre incident resource,
- log metric filter vytvára high-cardinality cost spike,
- remediation Lambda vytvorí retry loop.

## 28. Anti-patterny

### Všetky metrics na jednom dashboarde

Znižuje signal-to-noise a nevedie k rozhodnutiu.

### Infinite log retention bez klasifikácie

Zvyšuje cost a data exposure.

### CloudTrail Event history ako jediný audit archive

Je recent, regionálny a management-event orientovaný.

### Alarm na priemernú latency

Môže skryť poškodený tail alebo jednu AZ.

### Automatická remediation bez validation

Zmena môže zlyhať alebo spôsobiť ďalší incident.

### CloudTrail vypnutý počas troubleshooting testu

Odstráni najdôležitejšiu evidence vrstvu.

## 29. Kontrolné otázky

1. Aký je rozdiel medzi CloudWatch a CloudTrail?
2. Čo tvorí identitu CloudWatch metric?
3. Ako funguje missing-data behavior alarmu?
4. Kedy použiť composite alarm?
5. Prečo sú high-cardinality dimensions rizikové?
6. Aký je rozdiel medzi management a data eventom?
7. Čo Event history poskytuje a čo nie?
8. Ako chrániš organization trail?
9. Ako koreluješ performance incident s configuration change?
10. Čo potrebuje bezpečná automated remediation?

## Glossary impact

Relevantné pojmy: Amazon CloudWatch, CloudWatch metric, namespace, dimension, period, statistic, CloudWatch alarm, composite alarm, missing data, CloudWatch Logs, log group, log stream, Logs Insights, metric filter, Embedded Metric Format, CloudWatch agent, AWS CloudTrail, management event, data event, network activity event, Event history, trail, organization trail, log-file validation, CloudTrail Insights a event data store.

## Oficiálna dokumentácia

- [What is Amazon CloudWatch?](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html)
- [CloudWatch metrics concepts](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_concepts.html)
- [CloudWatch alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Alarms.html)
- [What is CloudWatch Logs?](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html)
- [What is AWS CloudTrail?](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html)
- [CloudTrail concepts](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html)
- [CloudTrail trails](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-trails.html)
- [CloudTrail Event history](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: ECS a EKS](ecs-eks.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Systems Manager →](systems-manager.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
