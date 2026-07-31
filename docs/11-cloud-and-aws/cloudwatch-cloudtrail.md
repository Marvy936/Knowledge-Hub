# Amazon CloudWatch a AWS CloudTrail

Amazon CloudWatch a AWS CloudTrail produkujú odlišné dôkazové vrstvy. CloudWatch opisuje, ako sa systém správa cez metrics, logs, alarms a queries. CloudTrail zaznamenáva AWS API a account activity: kto, kedy, z akej session, nad akým resource-om a s akým výsledkom vykonal podporovanú operation.

```text
operational or audit question
→ exact resource, release and time subject
→ metric, log or API event generation
→ collection and delivery
→ identity, dimensions and schema
→ retention and protection
→ evaluation or investigation
→ cross-layer correlation
→ bounded action
→ business validation
```

Dashboard nie je pravda iba preto, že má zelenú farbu. CloudTrail API success nie je dôkaz, že controller vytvoril correct runtime state.

## 1. Exact evidence subject

Atlas Payments používa observability subject `OBS-PAY-42`. Release `7.18.0`, deployment `ECS-DEP-75`, database `DB-PAY-42` a request `P-944` sú viazané correlation ID `corr-944` v intervale 10:15–10:42 UTC.

Custom metric `Atlas/Payments:SuccessfulAuthorizations` používa dimensions `Environment=prod`, `Service=payments-api`, `Release=7.18.0`, period 60 sekúnd a statistic `Sum`. Alarm `ALARM-PAY-SUCCESS-18` používa 3 z 5 periods a missing data hodnotí ako breaching. Action spúšťa notification a Systems Manager Automation `ARM-PAY-7`.

CloudTrail organization trail `org-audit-v9` zapisuje do protected S3 archive-u, zahŕňa management events a governed data-event selectors a používa log-file integrity validation.

Forbidden outcomes sú missing telemetry interpretovaná ako healthy, alarm sledujúci old dimension, remediation loop a Event history považovaná za dlhodobý complete audit archive.

## 2. Metric identity

CloudWatch time series identifikuje kombinácia namespace, metric name, complete dimension set, account a Region. Zmena `Service=payments-api` na `Service=payments` nevylepší existujúcu metric; vytvorí inú series.

Dimensions majú byť bounded. Request ID alebo payment ID patria do logs/traces, nie do custom metric dimensions.

Publikovanie sample metric:

```bash
aws cloudwatch put-metric-data \
  --namespace Atlas/Payments \
  --region eu-central-1 \
  --metric-data '[
    {
      "MetricName": "SuccessfulAuthorizations",
      "Dimensions": [
        {"Name":"Environment","Value":"prod"},
        {"Name":"Service","Value":"payments-api"},
        {"Name":"Release","Value":"7.18.0"}
      ],
      "Timestamp": "2026-07-30T19:00:00Z",
      "Unit": "Count",
      "Value": 118
    }
  ]'
```

CLI ukážka materializuje metric identity. Production application používa SDK/EMF/OpenTelemetry podľa architecture. API success nepreukazuje, že alarm query používa rovnakú dimension generation.

Read-back:

```bash
aws cloudwatch get-metric-statistics \
  --namespace Atlas/Payments \
  --metric-name SuccessfulAuthorizations \
  --dimensions \
    Name=Environment,Value=prod \
    Name=Service,Value=payments-api \
    Name=Release,Value=7.18.0 \
  --statistics Sum \
  --period 60 \
  --start-time 2026-07-30T18:55:00Z \
  --end-time 2026-07-30T19:05:00Z \
  --region eu-central-1
```

## 3. Period, statistic and missing data

Raw samples sa agregujú do periodu. `Average` môže skryť damaged tail alebo one-AZ cohort. Error count bez denominatora môže rásť iba preto, že traffic rástol.

Missing datapoint môže znamenať idle workload, failed publisher, new dimension, removed resource alebo delayed ingestion. Nula a missing nie sú rovnaké.

Dobrý design oddeľuje business outcome alarm a telemetry-freshness alarm. Business success metric môže mať missing=breaching, ak musí prichádzať každý period; sporadic error counter potrebuje iný contract.

## 4. Alarm ako state machine

Terraform alarm:

```hcl
resource "aws_cloudwatch_metric_alarm" "payment_success_missing" {
  alarm_name          = "ALARM-PAY-SUCCESS-18"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 5
  datapoints_to_alarm = 3
  threshold           = 1
  treat_missing_data  = "breaching"

  namespace   = "Atlas/Payments"
  metric_name = "SuccessfulAuthorizations"
  period      = 60
  statistic   = "Sum"

  dimensions = {
    Environment = "prod"
    Service     = "payments-api"
    Release     = "7.18.0"
  }

  alarm_actions = [aws_sns_topic.payments_ops.arn]
}
```

Alarm state `OK`, `ALARM` alebo `INSUFFICIENT_DATA` opisuje query evaluation, nie complete business reality. Alarm môže byť OK, lebo sleduje obsolete series.

Read-back:

```bash
aws cloudwatch describe-alarms \
  --alarm-names ALARM-PAY-SUCCESS-18 \
  --region eu-central-1

aws cloudwatch describe-alarm-history \
  --alarm-name ALARM-PAY-SUCCESS-18 \
  --history-item-type StateUpdate \
  --region eu-central-1
```

## 5. Structured logs

Log event musí niesť stable release a business correlation fields bez secrets:

```json
{
  "timestamp": "2026-07-30T10:21:14Z",
  "service": "payments-api",
  "release": "7.18.0",
  "correlationId": "corr-944",
  "paymentId": "P-944",
  "operation": "authorize",
  "outcome": "success",
  "durationMs": 183
}
```

Application stdout alebo agent prechádza bufferingom, transportom, log groupom, retention a query. Missing event môže byť emission alebo delivery failure.

Terraform log group:

```hcl
resource "aws_cloudwatch_log_group" "payments" {
  name              = "/atlas/prod/payments-api"
  retention_in_days = 90
  kms_key_id        = aws_kms_key.logs.arn

  tags = {
    SchemaGeneration = "LOG-PAY-24"
  }
}
```

Infinite retention zvyšuje cost a data exposure. Card data, bearer tokens a secrets sa musia redigovať pred emission.

## 6. Logs Insights investigation

```bash
QUERY_ID=$(aws logs start-query \
  --log-group-name /atlas/prod/payments-api \
  --start-time 1785227300 \
  --end-time 1785229200 \
  --query-string 'fields @timestamp, release, correlationId, paymentId, operation, outcome, durationMs
    | filter correlationId = "corr-944"
    | sort @timestamp asc' \
  --region eu-central-1 \
  --query queryId --output text)

aws logs get-query-results \
  --query-id "$QUERY_ID" \
  --region eu-central-1
```

Unix timestamps musia zodpovedať incident window. Empty result nepreukazuje absence eventu, kým nie je overený log group, ingestion time, schema and source coverage.

Field indexes môžu znížiť scan pre supported queries, no nepreukazujú completeness.

## 7. Embedded Metric Format

Application môže emitovať metric spolu so structured logom:

```json
{
  "_aws": {
    "Timestamp": 1785228074000,
    "CloudWatchMetrics": [
      {
        "Namespace": "Atlas/Payments",
        "Dimensions": [["Environment", "Service", "Release"]],
        "Metrics": [{"Name":"SuccessfulAuthorizations","Unit":"Count"}]
      }
    ]
  },
  "Environment": "prod",
  "Service": "payments-api",
  "Release": "7.18.0",
  "SuccessfulAuthorizations": 1,
  "correlationId": "corr-944"
}
```

Schema change can silently create new metric identity or stop extraction. CI fixture must parse positive and malformed samples and alarm on freshness.

## 8. CloudTrail event meaning

CloudTrail event can contain eventTime, eventSource, eventName, Region, userIdentity, session issuer, source IP, user agent, request parameters, resources, request ID, event ID and error fields.

Management events cover control-plane operations. Data events cover selected high-volume data-plane operations such as S3 object access or Lambda invocation according to selectors. Coverage is not automatic.

Quick lookup of recent management events:

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=payments-api \
  --start-time 2026-07-30T10:00:00Z \
  --end-time 2026-07-30T11:00:00Z \
  --region eu-central-1
```

Event history provides recent management events, not long-term complete organization archive or all data events.

## 9. Organization trail in Terraform

```hcl
resource "aws_cloudtrail" "organization" {
  name                          = "org-audit-v9"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_archive.id
  s3_key_prefix                 = "organization"
  include_global_service_events = true
  is_multi_region_trail         = true
  is_organization_trail         = true
  enable_log_file_validation    = true
  kms_key_id                    = aws_kms_key.cloudtrail.arn

  event_selector {
    read_write_type           = "All"
    include_management_events = true
  }
}
```

S3 bucket policy, KMS policy and organization trusted access are separate dependencies. `enable_log_file_validation` produces digest chain; organization must actually validate it and protect archive retention.

Trail status:

```bash
aws cloudtrail get-trail-status \
  --name org-audit-v9 \
  --region eu-central-1
```

`IsLogging=true` nepreukazuje required selector coverage or successful query in archive.

## 10. CloudWatch and CloudTrail correlation

CloudWatch can show that business failures started at 10:21 only for release 7.18.0 in AZ-b. CloudTrail can show `UpdateService` at 10:18 by assumed role `pipeline-prod`. ECS and application evidence then identify exact task and configuration.

```text
CloudWatch symptom and cohort
→ CloudTrail change and actor session
→ controller/runtime realization
→ application transaction
→ business result
```

CloudTrail proves accepted API change, not that all tasks converged. CloudWatch proves behavior, not who changed configuration.

## 11. Automated remediation as bounded workflow

Alarm action delivery, automation authorization, mutation, controller convergence and validation are independent steps.

```text
validated symptom
→ alarm and action delivery
→ scoped automation role
→ idempotent mutation
→ convergence wait
→ technical and business postcondition
→ rollback or escalation
```

Remediation needs target generation, max concurrency, deduplication, cooldown, stop condition and evidence preservation. Restart can destroy volatile evidence and mask root cause.

## 12. Worked incident: wrong metric identity creates remediation loop

Release 7.18.0 changed EMF dimension from `Service=payments-api` to `Service=payments`. Application continued authorizing payments, but alarm watched old series with missing=breaching.

Logs arrived and business ledger was healthy. `list-metrics` showed new series while old series stopped at deployment. Alarm entered ALARM and started `ARM-PAY-7`, which forced new ECS deployment. New tasks emitted only new dimension, so alarm remained ALARM and automation repeated. Repeated deployments finally reduced healthy capacity and created real errors.

Root cause was telemetry contract drift plus remediation without telemetry-validity precondition.

Containment disabled alarm action, preserved alarm/execution history and stopped task recycling. Recovery restored/versioned metric contract, added freshness alarm and required business symptom plus valid telemetry before automation. Cooldown and execution dedup prevented loop.

Acceptance required correct metric each period, expected alarm transitions, one bounded remediation for real failure, CloudTrail attribution and forbidden dimension-drift test.

## 13. Practical evidence checklist

For a CloudWatch alarm incident capture namespace, metric, complete dimensions, period, statistic, unit, missing policy, query result, alarm history and action execution. For CloudTrail capture account, Region, event category, event ID, request ID, principal/session issuer, API parameters and trail selector coverage.

A screenshot without query, time and cohort identity is weak evidence.

## Kontrolné otázky

1. What creates exact CloudWatch metric identity?
2. Why is missing not zero?
3. What does alarm state prove?
4. How can EMF schema drift create a new series?
5. What does CloudTrail Event history omit?
6. Why is trail logging not selector coverage proof?
7. How do CloudWatch and CloudTrail complement each other?
8. Which postcondition must automated remediation verify?
9. Why can restart worsen investigation?
10. Which forbidden test closes the remediation-loop incident?

## Oficiálna dokumentácia

- [Amazon CloudWatch](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html)
- [CloudWatch metrics](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/working_with_metrics.html)
- [CloudWatch alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html)
- [CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html)
- [Embedded Metric Format](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Embedded_Metric_Format.html)
- [AWS CloudTrail](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html)
- [CloudTrail events](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-events.html)
- [Log file integrity validation](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: ECS a EKS](ecs-eks.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Systems Manager →](systems-manager.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
