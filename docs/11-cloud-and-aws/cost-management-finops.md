# FinOps

FinOps je operating model, v ktorom engineering, finance a business spoločne riadia cloud value. Nie je to jednorazové „znižovanie AWS účtu“. FinOps prepája allocation, visibility, forecasting, anomaly response, unit economics, optimization a commitment decisions s business outcome a reliability constraints.

```text
financial ownership and allocation
→ normalized cost and usage data
→ forecast and budget
→ anomaly detection and investigation
→ unit economics
→ rightsizing, scheduling and architecture changes
→ pricing commitments
→ verified savings and business impact
→ repeated planning cycle
```

Najlacnejšia infraštruktúra nemusí byť najhodnotnejšia. Odstránenie Multi-AZ, backup retention alebo failure headroom môže znížiť spend a zvýšiť expected business loss.

## 1. Exact financial subject

Atlas Payments používa FinOps subject `FIN-PAY-42`. Workload owner je Payments Platform Lead, business owner Payments Product Owner a finance partner Cloud Finance. Accounts zahŕňajú production `100000000042` a recovery `200000000042`. Cost allocation generation je `ALLOC-PAY-12`, budget `BUD-PAY-2026`, anomaly monitor `ANOM-PAY-7` a commitment portfolio `SP-COMPUTE-9`.

Primary unit metric je:

```text
total amortized workload cost / successful settled payments
```

Secondary metrics sú cost per 1 000 authorization requests, idle non-production cost, restore-test cost and provider/data-transfer cost. Forbidden outcomes sú savings calculated from list price rather than realized baseline, commitments purchased before usage stability and cost action that violates RTO/RPO or security.

## 2. Allocation before optimization

Without allocation, teams optimize what is visible, not what they own. Allocation combines account structure, cost categories, tags, resource IDs and shared-cost rules.

Required tags:

```yaml
CostCenter: PAYMENTS
Application: atlas-payments
Environment: production
Owner: payments-platform
DataClass: confidential
Lifecycle: persistent
```

Tag presence is not enough. Cost allocation tags must be activated and resource types may not support tags for every charge. Untagged spend, support, data transfer and shared services need explicit allocation policy.

List cost allocation tags:

```bash
aws ce list-cost-allocation-tags \
  --status Active \
  --region us-east-1
```

Cost Explorer APIs are global endpoints commonly called in `us-east-1`; billing account permissions and Organizations context matter.

## 3. Cost and usage query

Monthly workload cost by service:

```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-07-01,End=2026-08-01 \
  --granularity DAILY \
  --metrics AmortizedCost UsageQuantity \
  --group-by Type=DIMENSION,Key=SERVICE \
  --filter '{
    "And": [
      {"Tags": {"Key": "Application", "Values": ["atlas-payments"], "MatchOptions": ["EQUALS"]}},
      {"Tags": {"Key": "Environment", "Values": ["production"], "MatchOptions": ["EQUALS"]}}
    ]
  }' \
  --region us-east-1 > payments-cost.json
```

`AmortizedCost` distributes upfront/recurring commitment cost across usage period. `UnblendedCost` answers a different question. Query must record metric, time boundary, currency, credits/refunds and shared-cost treatment.

## 4. Data Exports and Athena model

For detailed analysis use AWS Data Exports or Cost and Usage Report delivery to S3, then query with Athena/warehouse.

Illustrative SQL:

```sql
select
  date_trunc('day', line_item_usage_start_date) as usage_day,
  product_servicecode,
  resource_tags_user_application as application,
  sum(line_item_unblended_cost) as unblended_cost,
  sum(reservation_effective_cost) as reservation_effective_cost,
  sum(savings_plan_savings_plan_effective_cost) as savings_plan_effective_cost
from cur_database.cur_table
where line_item_usage_start_date >= date '2026-07-01'
  and resource_tags_user_application = 'atlas-payments'
group by 1, 2, 3
order by 1, 2;
```

Column names depend on export schema and Athena table normalization. Query must avoid double-counting mutually exclusive effective-cost fields. Version schema and reconciliation to invoice totals.

## 5. Budget as decision threshold

Terraform budget:

```hcl
resource "aws_budgets_budget" "payments_monthly" {
  name         = "BUD-PAY-2026"
  budget_type  = "COST"
  limit_amount = "25000"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filter {
    name   = "TagKeyValue"
    values = ["user:Application$atlas-payments"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = ["payments-finops@example.com"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = ["payments-finops@example.com"]
  }
}
```

Budget notification is governance signal, not automatic proof of waste. Production budget action should rarely shut down resources blindly; use approval and workload context.

Read-back:

```bash
aws budgets describe-budget \
  --account-id 100000000042 \
  --budget-name BUD-PAY-2026 \
  --region us-east-1
```

## 6. Cost anomaly detection

Anomaly monitor observes cost segments and anomaly subscription routes alerts.

```hcl
resource "aws_ce_anomaly_monitor" "payments" {
  name              = "ANOM-PAY-7"
  monitor_type      = "CUSTOM"
  monitor_dimension = "SERVICE"
  monitor_specification = jsonencode({
    Tags = {
      Key         = "Application"
      Values      = ["atlas-payments"]
      MatchOptions = ["EQUALS"]
    }
  })
}

resource "aws_ce_anomaly_subscription" "payments" {
  name      = "payments-daily-anomalies"
  frequency = "DAILY"
  monitor_arn_list = [aws_ce_anomaly_monitor.payments.arn]

  threshold_expression {
    dimension {
      key           = "ANOMALY_TOTAL_IMPACT_ABSOLUTE"
      values        = ["500"]
      match_options = ["GREATER_THAN_OR_EQUAL"]
    }
  }

  subscriber {
    type    = "EMAIL"
    address = "payments-finops@example.com"
  }
}
```

Exact provider schema changes should be validated with current Terraform/AWS API. Anomaly alert starts investigation: release, usage quantity, price, data transfer, retries or new resource. It does not prove root cause.

List anomalies:

```bash
aws ce get-anomalies \
  --date-interval StartDate=2026-07-01,EndDate=2026-08-01 \
  --total-impact NumericOperator=GREATER_THAN_OR_EQUAL,StartValue=500 \
  --region us-east-1
```

## 7. Unit economics

Raw monthly cost can grow while unit cost improves because business volume grows. Conversely stable bill can hide declining demand and waste.

```text
unit cost = amortized workload cost / successful business units
```

For Atlas:

```sql
select
  usage_day,
  total_amortized_cost / nullif(successful_settlements, 0) as cost_per_settlement
from payments_daily_finops;
```

Denominator must be successful, correct business outcome, not raw requests including retries and failures.

## 8. Optimization hierarchy

Optimize in order:

```text
remove abandoned resources and duplicate data
→ schedule non-production
→ fix retry/log/data-transfer waste
→ rightsize resource and storage configuration
→ improve architecture and managed-service fit
→ purchase commitments for stable residual usage
```

Buying Savings Plans for waste makes waste cheaper and harder to remove.

Rightsizing evidence combines utilization distributions, performance SLO, failure headroom and deployment surge. Average CPU alone is insufficient.

## 9. Cost Optimization Hub and recommendations

Cost Optimization Hub aggregates supported rightsizing, idle-resource and commitment recommendations across accounts/Regions.

```bash
aws cost-optimization-hub list-recommendations \
  --filter '{"accountIds":["100000000042"]}' \
  --region us-east-1
```

Recommendation savings is modeled estimate. Before implementation verify resource generation, workload owner, performance and reliability constraints, migration cost and commitment coverage. After change measure realized spend and unit cost.

## 10. Commitments

Savings Plans and Reserved Instances exchange flexibility for discounted committed usage. Decision requires stable baseline after removing waste, forecast confidence, service/Region/instance flexibility needs and risk appetite.

```bash
aws ce get-savings-plans-purchase-recommendation \
  --savings-plans-type COMPUTE_SP \
  --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT \
  --lookback-period-in-days SIXTY_DAYS \
  --region us-east-1
```

Recommendation is input, not purchase approval. Compare coverage/utilization, expected migrations and downside of overcommitment.

## 11. Worked incident: cost spike is retry storm

Daily Atlas spend increased 42 % after release 7.16.0. EC2 and Lambda count looked similar, so first assumption was price change.

Cost and usage data showed NAT processed bytes, Lambda duration and provider API calls rising together. Operational telemetry showed disabled HTTP pooling and three timeout retries per request. Business volume grew only 4 %.

The anomaly was not isolated FinOps waste; it was reliability regression. Containment stopped rollout and retry amplification. Recovery restored pooling and bounded retries. NAT port errors and payment latency also recovered.

Savings verification compared same-volume baseline, amortized cost and cost per successful settlement. The team did not purchase a larger commitment to mask the spike.

## 12. Change business case

FinOps change business case viaže navrhovanú úsporu na presný resource cohort, baseline window a business denominator. Bez tejto väzby nemožno po zmene rozlíšiť skutočnú úsporu od poklesu trafficu, presunu costu do inej služby alebo degradácie reliability, ktorá iba znížila spotrebu.

Optimization record:

```yaml
changeId: FIN-PAY-OPT-31
resource: payments-api fleet
baselineWindow: 2026-06-01/2026-06-30
proposal: reduce task memory from 4 GiB to 2 GiB after p99 profiling
expectedMonthlySavingsUsd: 3200
constraints:
  p99LatencyMs: 800
  azLossCapacity: 40-percent-peak
  deploymentSurge: 25-percent
validation:
  canaryDurationHours: 24
  metrics:
    - memory-p99
    - oom-kills
    - payment-p99
    - error-rate
rollback: restore task definition 118
owner: payments-platform
```

Realized savings are measured after promotion and normalized for volume.

## 13. FinOps cadence

Daily: anomaly triage. Weekly: owner review of material changes and idle resources. Monthly: invoice/export reconciliation, budget/forecast and unit economics. Quarterly: architecture, commitments, allocation quality and shared-cost policy.

Every action has owner and expiry. Temporary resource exception without expiry becomes permanent waste.

## Kontrolné otázky

1. Prečo FinOps nie je iba cost cutting?
2. Aký rozdiel je medzi unblended a amortized cost?
3. Prečo allocation predchádza optimization?
4. Čo budget alert preukazuje a čo nepreukazuje?
5. Ako anomaly alert prejde do operational investigation?
6. Prečo denominator unit costu musí byť successful business outcome?
7. Prečo commitments nasledujú až po removal waste-u?
8. Čo treba overiť pred Cost Optimization Hub recommendation?
9. Ako reliability constraint vstupuje do rightsizingu?
10. Ako sa preukáže realized savings?

## Oficiálna dokumentácia

- [AWS Cloud Financial Management](https://aws.amazon.com/aws-cost-management/)
- [AWS Cost Management User Guide](https://docs.aws.amazon.com/cost-management/latest/userguide/what-is-costmanagement.html)
- [Cost allocation tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html)
- [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
- [AWS Cost Anomaly Detection](https://docs.aws.amazon.com/cost-management/latest/userguide/manage-ad.html)
- [AWS Data Exports](https://docs.aws.amazon.com/cur/latest/userguide/what-is-data-exports.html)
- [Cost Optimization Hub](https://docs.aws.amazon.com/cost-management/latest/userguide/cost-optimization-hub.html)
- [Savings Plans recommendations](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-sp-recommendations.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Well-Architected Framework](well-architected-framework.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: AWS Certified CloudOps Engineer – Associate (SOA-C03) →](cloudops-engineer-associate-soa-c03.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
