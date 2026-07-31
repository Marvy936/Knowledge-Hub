# FinOps

FinOps je operating model, v ktorom engineering, finance a business spoločne riadia cloud value. Nie je to jednorazové „znižovanie AWS účtu“. FinOps prepája allocation, visibility, forecasting, anomaly response, unit economics, optimization a commitment decisions s business outcome a reliability constraints.

```text
financial ownership a allocation
→ normalized cost a usage data
→ forecast a budget
→ anomaly detection a investigation
→ unit economics
→ rightsizing, scheduling a architecture changes
→ pricing commitments
→ realized savings a business validation
→ repeated planning cycle
```

Najlacnejšia infraštruktúra nemusí byť najhodnotnejšia. Odstránenie Multi-AZ, backup retention alebo failure headroomu môže znížiť spend a zároveň zvýšiť expected business loss. FinOps zmena je preto prijatá iba vtedy, keď sa preukáže finančný výsledok aj zachovanie reliability, security a recovery contractov.

## 1. Exact financial subject

Atlas Payments používa FinOps subject `FIN-PAY-42`. Workload owner je Payments Platform Lead, business owner Payments Product Owner a finance partner Cloud Finance. Accounts zahŕňajú production `100000000042` a recovery `200000000042`. Cost allocation generation je `ALLOC-PAY-12`, budget `BUD-PAY-2026`, anomaly monitor `ANOM-PAY-7` a commitment portfolio `SP-COMPUTE-9`.

Primary unit metric je amortized workload cost delený počtom successful settled payments. Secondary metrics sú cost per 1 000 authorization requests, idle non-production cost, restore-test cost a provider/data-transfer cost. Denominator musí reprezentovať správny business outcome; raw request count vrátane retries a failures môže zakryť regresiu.

Forbidden outcomes sú savings vypočítané z list price namiesto realized baseline, commitments kúpené pred stabilizáciou usage, presun costu do iného accountu bez zmeny total economics a cost action, ktorá poruší RTO, RPO alebo security boundary.

## 2. Allocation predchádza optimalizácii

Bez allocation tímy optimalizujú to, čo vidia, nie to, čo vlastnia. Allocation kombinuje account structure, cost categories, cost allocation tags, resource IDs a pravidlá pre shared costs. Každý model musí mať version, ownera a reconciliation voči billing totalu.

```yaml
CostCenter: PAYMENTS
Application: atlas-payments
Environment: production
Owner: payments-platform
DataClass: confidential
Lifecycle: persistent
```

Tag presence na resource-e nestačí. User-defined cost allocation tag musí byť aktivovaný pre billing data a nie každý charge nesie resource tag. Support, data transfer, shared observability, centralized networking a untagged spend preto potrebujú explicitnú allocation policy, napríklad podľa usage, account, request volume alebo dohodnutého shared-services kľúča.

```bash
aws ce list-cost-allocation-tags \
  --status Active \
  --region us-east-1 \
  --output table
```

Tento príkaz preukazuje, ktoré tag keys sú active v Cost Explorer allocation surface. Nepreukazuje coverage jednotlivých resources ani to, že historical data bola spätne prepočítaná. Coverage sa kontroluje cez export alebo Cost Explorer groupovanie s explicitnou `No tag key` cohortou.

## 3. Cost Explorer query a metric semantics

Cost query musí fixovať časové hranice, metric, filters, groupings, currency a zaobchádzanie s credits, refunds a commitments. Rovnaký workload môže mať rozdielny `UnblendedCost`, `NetUnblendedCost`, `AmortizedCost` a `NetAmortizedCost`; nejde o zameniteľné views.

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
  --region us-east-1 \
  > payments-cost.json
```

`AmortizedCost` rozkladá upfront a recurring commitment charges cez obdobie používania a je vhodný pre stabilnejšie unit economics. Výstup preukazuje Cost Explorer view po dostupné billing dáta; nepreukazuje real-time spend, pretože billing ingestion má oneskorenie. Query sa musí reconciliovať s invoice alebo export totalom a musí evidovať, či filters nevylúčili shared či untagged spend.

```bash
jq -r '
  .ResultsByTime[] |
  .TimePeriod.Start as $day |
  .Groups[] |
  [$day, .Keys[0], .Metrics.AmortizedCost.Amount] |
  @tsv
' payments-cost.json
```

Tento transformačný príkaz rozbalí každú service group samostatne. Pôvodný report by bol chybný, keby nezávisle iteroval dve `.Groups[]` expressions a vytvoril cartesian product. Production pipeline preto potrebuje schema tests, expected row counts a sum reconciliation.

## 4. Data Exports a queryable billing model

Pre resource-level analýzu sa používa AWS Data Exports, najmä CUR 2.0, alebo existujúci legacy CUR pipeline. Export vytvára versionovaný dataset v S3 s definovanou schema a delivery contractom. Athena alebo warehouse potom poskytne reprodukovateľné queries nad line items.

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

Column names závisia od export type, schema version a Athena normalization. Query nesmie bez podmienok sčítať mutually exclusive effective-cost fields. Výstup sa najprv porovná s billing totalom za rovnaké obdobie a až potom sa používa ako baseline optimalizácie.

CUR 2.0 prináša stabilnejšiu schema a nested structures, ale migration môže zmeniť názvy alebo spôsob prístupu k tags a cost fields. Export generation sa preto pinne v pipeline contracte a pri schema zmene sa spúšťa compatibility test.

## 5. Budget ako decision threshold

Budget je governance signal nad definovaným cost scope-om. Forecasted threshold môže spustiť diskusiu pred prekročením limitu; actual threshold potvrdzuje, že billing view už hranicu prekročil. Ani jeden sám nepreukazuje waste alebo root cause.

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

Production budget action nemá naslepo vypínať resources. Scope môže obsahovať recovery capacity, seasonal growth alebo planned migration. Alert preto otvorí owned investigation s recent changes, usage quantity a business volume.

```bash
aws budgets describe-budget \
  --account-id 100000000042 \
  --budget-name BUD-PAY-2026 \
  --region us-east-1 \
  --output yaml
```

Výstup preukazuje configured limit, filters a current calculated values. Nepreukazuje, že notification dorazila správnemu ownerovi ani že budget filter pokrýva celý workload; delivery a allocation sa overujú osobitne.

## 6. Cost Anomaly Detection

Cost Anomaly Detection používa cost monitor na definovanie sledovaného segmentu a subscription na routing alerts. Detekcia pracuje nad spracovanými billing dátami, nie ako real-time operational metric. Alert preto môže prísť s oneskorením a nesmie nahradiť CloudWatch telemetry pre retry storm alebo runaway resource creation.

```hcl
resource "aws_ce_anomaly_monitor" "payments" {
  name         = "ANOM-PAY-7"
  monitor_type = "CUSTOM"

  monitor_specification = jsonencode({
    Tags = {
      Key          = "Application"
      Values       = ["atlas-payments"]
      MatchOptions = ["EQUALS"]
    }
  })
}

resource "aws_ce_anomaly_subscription" "payments" {
  name             = "payments-daily-anomalies"
  frequency        = "DAILY"
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

Provider schema a supported monitor types sa majú validovať proti current API. Anomaly signal začína investigation cez service, account, Region, usage type, release a business volume; nepreukazuje root cause.

```bash
aws ce get-anomalies \
  --date-interval StartDate=2026-07-01,EndDate=2026-08-01 \
  --total-impact NumericOperator=GREATER_THAN_OR_EQUAL,StartValue=500 \
  --region us-east-1 \
  --output json \
  > anomalies.json
```

Tento príkaz vráti detected anomaly subjects a impact estimates. Výstup nepreukazuje, že charge je nesprávny; môže ísť o legitímny traffic growth. Každá anomaly sa preto koreluje s usage quantity, operational telemetry a business denominatorom.

## 7. Unit economics

Raw monthly cost môže rásť, zatiaľ čo unit cost klesá vďaka vyššiemu business volume. Stabilný účet môže naopak skrývať declining demand a rastúci waste. FinOps verdict sa preto viaže na successful business units.

```text
unit cost = amortized workload cost / successful business units
```

```sql
select
  usage_day,
  total_amortized_cost / nullif(successful_settlements, 0) as cost_per_settlement
from payments_daily_finops;
```

Denominator musí byť successful a reconciled settlement, nie raw API request vrátane retries. Ak release zvýši retry count, cost per request môže vyzerať lepšie alebo horšie bez vzťahu k business value; cost per successful settlement odhalí skutočný efekt.

## 8. Optimization hierarchy

Optimization začína odstránením abandoned resources a duplicate data, pokračuje schedulingom non-production a opravou retry, logging alebo data-transfer waste-u. Až potom nasleduje rightsizing, architecture change a pricing commitment pre stabilný residual usage.

```text
remove abandoned resources a duplicate data
→ schedule non-production
→ fix retry, logging a data-transfer waste
→ rightsize resource a storage configuration
→ improve architecture a managed-service fit
→ purchase commitments pre stable residual usage
```

Buying Savings Plans pre waste urobí waste lacnejším a menej viditeľným. Rightsizing evidence musí kombinovať utilization distributions, latency a error SLO, failure headroom, deployment surge, queue backlog a recovery capacity. Average CPU bez p95/p99 a failure scenario nestačí.

## 9. Cost Optimization Hub

Cost Optimization Hub agreguje supported rightsizing, idle-resource a commitment recommendations naprieč accounts a Regions. Pri configured preferences môže zohľadňovať commercial terms, takže odhad je užitočnejší než jednoduchý list-price comparison. Stále však ide o modelovanú recommendation, nie automatic approval.

```bash
aws cost-optimization-hub list-recommendations \
  --filter '{"accountIds":["100000000042"]}' \
  --region us-east-1 \
  --output json \
  > coh-recommendations.json
```

Výstup preukazuje aktuálne imported recommendations a estimated savings podľa Hub modelu. Nepreukazuje workload generation, migration cost, reliability headroom ani realized savings. Pred implementáciou sa preto overí resource owner, current configuration, performance constraints, commitment overlap a rollback path.

Po zmene sa recommendation status nepoužíva ako acceptance oracle. Realized spend, unit cost, business SLI a forbidden outcomes sa porovnajú s normalizovaným baseline windowom.

## 10. Commitments

Commitment premieňa časť budúcej flexibility na zľavu, preto sa nakupuje až nad stabilným residual usage po odstránení waste-u. Rozhodnutie musí modelovať coverage, utilization, migration roadmap a downside overcommitmentu; purchase recommendation sama nepozná budúcu architektonickú zmenu ani business neistotu.

Savings Plans a Reserved Instances vymieňajú flexibility za discounted committed usage. Purchase decision potrebuje stabilný baseline po odstránení waste-u, forecast confidence, plánované migrations, service a Region flexibility a downside model pri overcommitment-e.

```bash
aws ce get-savings-plans-purchase-recommendation \
  --savings-plans-type COMPUTE_SP \
  --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT \
  --lookback-period-in-days SIXTY_DAYS \
  --region us-east-1 \
  --output json \
  > savings-plan-recommendation.json
```

Tento príkaz vytvorí recommendation view z historical usage a pricing assumptions. Nepreukazuje budúci workload shape ani to, že pending architecture change zachová coverage. Approval preto porovnáva viac lookback windows, utilization, coverage, forecast a downside pri nižšom demand-e.

Po nákupe sa sleduje commitment utilization aj coverage. Vysoká utilization môže koexistovať s nízkou coverage a vysoká coverage s preplateným commitmentom; obe metrics potrebujú spoločný interpretation model.

## 11. Worked incident: cost spike bol retry storm

Daily Atlas spend stúpol o 42 % po release `7.16.0`. EC2 a Lambda resource count vyzeral podobne, takže prvá hypotéza bola price change. Cost and usage data však ukázali, že NAT processed bytes, Lambda duration a provider API calls rástli v rovnakom intervale.

Operational telemetry odhalila disabled HTTP pooling a tri timeout retries na request. Business volume stúpol iba o 4 %. Cost anomaly teda nebola izolovaná finančná odchýlka, ale reliability regression s network a provider amplification.

Containment zastavil rollout a obmedzil retry amplification. Recovery obnovila connection pooling, bounded retry a idempotency guard. NAT port-allocation errors aj payment latency sa vrátili do baseline.

Savings verification porovnala rovnaký business volume, amortized cost a cost per successful settlement. Tím nekúpil väčší commitment, ktorý by iba maskoval regresiu. Second load test zopakoval peak bez návratu cost alebo retry amplification.

## 12. Change business case a acceptance

FinOps change business case viaže navrhovanú úsporu na exact resource cohort, baseline window, business denominator a reliability constraints. Bez tejto väzby nemožno po zmene rozlíšiť skutočnú úsporu od poklesu trafficu, presunu costu do inej služby alebo degradácie, ktorá iba znížila spotrebu.

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

Positive acceptance preukáže nižší normalized unit cost a zachovaný business SLI. Recovery acceptance overí rollback alebo scale-back pri OOM či latency regression. Forbidden acceptance potvrdí, že nezmizla AZ-loss capacity, backup retention ani security logging. Second operation zopakuje deployment alebo peak demand bez skrytého capacity deficit-u.

## 13. FinOps cadence

Daily cadence rieši anomalies a urgent runaway spend. Weekly review spája material changes, idle resources a owners. Monthly cycle reconciliuje export s invoice, aktualizuje budget a forecast a vyhodnocuje unit economics. Quarterly review posudzuje architecture, commitments, allocation quality a shared-cost policy.

Každá action má ownera, deadline, acceptance evidence a expiry. Temporary exception bez expiry sa mení na permanent waste. Accepted financial risk bez reliability ownera je neúplné rozhodnutie, pretože eventual cost sa môže prejaviť až incidentom alebo neúspešným restore-om.

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
10. Ako sa preukáže realized savings a bezpečný second operation?

## Oficiálna dokumentácia

- [AWS Cloud Financial Management](https://aws.amazon.com/aws-cost-management/)
- [AWS Cost Management User Guide](https://docs.aws.amazon.com/cost-management/latest/userguide/what-is-costmanagement.html)
- [Cost allocation tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html)
- [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
- [AWS Cost Anomaly Detection](https://docs.aws.amazon.com/cost-management/latest/userguide/manage-ad.html)
- [AWS Data Exports](https://docs.aws.amazon.com/cur/latest/userguide/what-is-data-exports.html)
- [Cost Optimization Hub](https://docs.aws.amazon.com/cost-management/latest/userguide/cost-optimization-hub.html)
- [Savings Plans recommendations](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-sp-recommendations.html)
- [Cost Explorer API](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-api.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Well-Architected Framework](well-architected-framework.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: AWS Certified CloudOps Engineer – Associate (SOA-C03) →](cloudops-engineer-associate-soa-c03.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
