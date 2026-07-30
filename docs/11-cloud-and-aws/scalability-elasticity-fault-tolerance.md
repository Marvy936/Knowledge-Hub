# Scalability, elasticity a fault tolerance

Scalability, elasticity a fault tolerance opisujú tri rozdielne vlastnosti. Scalability hovorí, či sa bezpečná kapacita systému dokáže zväčšiť. Elasticity je control loop, ktorý kapacitu pridáva alebo odoberá podľa signálu. Fault tolerance určuje, či business outcome pokračuje po strate komponentu alebo celej failure domain.

Tieto vlastnosti sa nesmú merať počtom instances. Business capacity vzniká až vtedy, keď celý critical path prijme request, spracuje ho a durable ukončí bez porušenia invariantu.

```text
arrival rate
→ load balancer
→ ready application workers
→ thread a connection pools
→ database, queue a external provider
→ durable payment result
```

Najužší článok určuje bezpečný throughput. Ak databázový writer zvládne 3 000 commitov za sekundu, ďalších dvadsať application instances môže iba zvýšiť connection pressure a retries.

## 1. Exact capacity subject

Atlas Payments prevádzkuje release `PAY-4.2.0` s image `I57` v `eu-central-1`. Auto Scaling group `ASG-PAY-42` má minimum 6, desired 6 a maximum 30. Target group `TG-PAY-42` prijíma traffic vo viacerých AZs. Warm-up budget je 180 sekúnd, drain 60 sekúnd. Kritickým downstreamom je database writer `DB-P42`.

Scaling policy generation `SP-19` má udržať payment p99 pod 800 ms a presne jeden authorization outcome. Capacity evidence musí viazať metric generation, ASG, launch template, serving target cohort, DB connection envelope a business request. Bez toho môže tím porovnávať desired capacity novej fleet generation s latency starej release cohorty.

## 2. Kapacitný model pred autoscalingom

Najprv zmeraj jednu bezpečnú workload unit. Ak jedna ready instance pri target latency zvládne 120 validných requestov za sekundu a potrebuje maximálne 12 database connections, šesť instances má teoretický application envelope 720 requestov/s a 72 connections.

Tento výpočet ešte nepreukazuje end-to-end capacity. Database môže mať limit 500 commitov/s a external provider 450 requestov/s. Skutočný bezpečný maximum je potom bližšie k 450, nie 720.

Kapacitný manifest môže vyzerať takto:

```yaml
service: payments-api
release: PAY-4.2.0
unit:
  type: ready-target
  safeRequestsPerSecond: 120
  databaseConnections: 12
  warmupSeconds: 180
fleet:
  minimum: 6
  maximum: 30
dependencies:
  database:
    safeCommitsPerSecond: 500
    maximumConnections: 180
  provider:
    safeRequestsPerSecond: 450
business:
  p99Milliseconds: 800
  duplicateAuthorizationRate: 0
```

Pri 12 connections na instance môže maximum 30 instances požadovať 360 connections, teda dvojnásobok database budgetu. Autoscaling maximum musí rešpektovať dependency envelope alebo použiť proxy/pooling model, ktorý tento vzťah kontroluje.

## 3. Scalability: vertical a horizontal

Vertical scaling zväčšuje jeden resource. Môže byť správne pre single-writer databázu alebo workload, kde distributed coordination stojí viac než väčší node. Neprináša však fault tolerance. Väčší jediný writer môže zvýšiť throughput aj blast radius.

Horizontal scaling pridáva workers, replicas alebo partitions. Funguje iba vtedy, keď traffic alebo work možno rozdeliť, state ownership je explicitný, operácie sú idempotentné, downstream má headroom a scale-in dokáže bezpečne odovzdať rozpracovanú prácu.

Praktický test horizontal scalability nesleduje iba throughput. Zobrazuje throughput, p50/p99, error rate, queue age, connection count, retries a cost per successful payment pri 6, 12, 18 a 24 ready targets. Ak throughput po 12 instances prestane rásť a DB wait time rastie, scalability limit leží downstream.

## 4. Elasticity ako merateľná feedback slučka

Autoscaling vzniká cez celý chain:

```text
metric emission
→ CloudWatch time series
→ aggregation a threshold
→ scaling policy
→ desired capacity
→ instance launch
→ bootstrap a health
→ target registration
→ serving capacity
→ nový metric a business result
```

Každý krok má latency. Pri EC2 môže burst skončiť skôr, než nová instance bootne, načíta secret, warmne connection pool a prejde health checkom. Elasticity preto nenahrádza minimum pre okamžitý burst.

Desired capacity nie je serving capacity:

```text
DesiredCapacity=18
≠ 18 launched
≠ 18 healthy
≠ 18 registered
≠ 18 ready
≠ 18 targets prijímajúcich validný traffic
```

## 5. Praktický custom metric contract

Raw ALB `RequestCount` môže obsahovať user requests aj retries. Pre Atlas je vhodnejší signál `ValidOriginRequestsPerReadyTarget` a samostatný alarm na queueing latency.

Aplikácia publikuje bounded custom metric:

```bash
aws cloudwatch put-metric-data \
  --namespace Atlas/Payments \
  --metric-data '[
    {
      "MetricName": "ValidOriginRequests",
      "Dimensions": [
        {"Name":"Service","Value":"payments-api"},
        {"Name":"Release","Value":"PAY-4.2.0"}
      ],
      "Unit": "Count",
      "Value": 118
    }
  ]' \
  --region eu-central-1
```

Production emitter by metric nepoužíval request-by-request CLI. Ukážka iba materializuje identitu time series. `Service` a `Release` sú bounded dimensions. Payment ID by vytvorilo high-cardinality metric a patrí do logs/traces.

Over series:

```bash
aws cloudwatch list-metrics \
  --namespace Atlas/Payments \
  --metric-name ValidOriginRequests \
  --region eu-central-1
```

Existencia metric nepreukazuje freshness ani správnu hodnotu. Alarm potrebuje expected publication cadence a samostatný telemetry-freshness control.

## 6. Target tracking policy s resource-aware guardrailom

Application Load Balancer target tracking môže používať predefined metric `ALBRequestCountPerTarget`. Nasledujúci JSON nastaví cieľ 100 requestov na target:

```json
{
  "AutoScalingGroupName": "ASG-PAY-42",
  "PolicyName": "SP-20-request-per-target",
  "PolicyType": "TargetTrackingScaling",
  "EstimatedInstanceWarmup": 180,
  "TargetTrackingConfiguration": {
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ALBRequestCountPerTarget",
      "ResourceLabel": "app/atlas-payments/1234567890abcdef/targetgroup/TG-PAY-42/abcdef1234567890"
    },
    "TargetValue": 100.0,
    "DisableScaleIn": false
  }
}
```

Apply:

```bash
aws autoscaling put-scaling-policy \
  --cli-input-json file://sp-20.json \
  --region eu-central-1
```

Tento policy signal je bližšie k workload unit než fleet CPU. Stále však nevie o database saturation. Preto sa maximum ASG a deployment concurrency viažu na DB connection budget. CloudWatch alarm na DB connections môže zastaviť rollout alebo aktivovať backpressure, nie automaticky škálovať application ďalej.

Read-back:

```bash
aws autoscaling describe-policies \
  --auto-scaling-group-name ASG-PAY-42 \
  --region eu-central-1 \
  --query 'ScalingPolicies[].{Name:PolicyName,Type:PolicyType,Target:TargetTrackingConfiguration.TargetValue,Warmup:EstimatedInstanceWarmup}'
```

## 7. Fault tolerance potrebuje nezávislé failure domains

Tri instances nie sú fault tolerant, ak všetky bežia v jednej AZ alebo používajú jedinú NAT Gateway, single-writer bez failoveru či jednu chybnú configuration generation. Fault tolerance kombinuje redundantnú capacity, health-based traffic withdrawal, explicitný state model, retry/idempotency a statically stable minimum.

Stavová operácia potrebuje fencing. Ak leader zlyhá a druhý writer sa aktivuje bez preukázaného odobratia starej authority, redundantná capacity vytvorí split brain.

Pre stateless payment API je fault-tolerant path:

```text
healthy targets v troch AZs
→ ALB odstráni failed cohort
→ remaining capacity prevezme traffic
→ database failover alebo surviving writer ostáva authoritative
→ clients používajú bounded retry s idempotency key
→ business canary overí jednu autorizáciu
```

## 8. Scale-out a dependency pressure

Každá nová instance môže vytvoriť connection pool, cache warmup, secret fetch a outbound sockets. Preto scaling relationship nie je lineárny.

Aktuálny fleet a DB pressure:

```bash
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names ASG-PAY-42 \
  --region eu-central-1 \
  --query 'AutoScalingGroups[0].{Min:MinSize,Desired:DesiredCapacity,Max:MaxSize,Instances:Instances[].LifecycleState}'

aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=DB-P42 \
  --statistics Maximum \
  --period 60 \
  --start-time 2026-07-30T18:00:00Z \
  --end-time 2026-07-30T19:00:00Z \
  --region eu-central-1
```

Prvý príkaz ukazuje control-plane capacity. Druhý ukazuje downstream connection pressure. Korelácia musí použiť rovnaké časové okno a release cohort.

## 9. Worked incident: autoscaling zosilní database saturation

Po marketingovej kampani stúpla p99 latency z 450 ms na 2,8 sekundy. ASG sa rozšírila zo 6 na 24 instances, no timeout rate aj database connections ďalej rástli.

Hypotézy zahŕňali pomalý scale-out, nerovnomerný ALB, ne-ready nové instances, retry-amplified metric, database bottleneck, provider throttling, subnet capacity a connection leak.

Evidence ukázalo, že scaling metric `RequestCount` zahŕňala origin requests aj automatické retries. Každá instance otvorila 40 DB connections. Writer dosiahol commit a connection limit. Timeouty vytvorili retries, retries zvýšili metric a policy pridala ďalšie instances.

```text
DB saturation
→ latency
→ client/application retries
→ vyšší RequestCount
→ scale-out
→ viac connection pools
→ ešte väčšia DB saturation
```

Containment nastavil bezpečné ASG maximum, obmedzil retries a chránil DB connection budget. Tím nezvyšoval timeouty ani nevypínal health checks. Zachoval per-instance, ALB a database evidence a operation IDs pre reconciliation.

Recovery zmenila metric generation na valid origin requests per ready target, znížila pool per instance a zaviedla proxy/shared connection envelope. Retry policy dostala exponential backoff, jitter a total budget. `SP-20` sa nasadila po cohorts a load test zahrnul burst, sustained load, scale-in a zonal failure.

Acceptance vyžadovala p99 pod 800 ms, rast successful throughputu s ready capacity, bounded DB connections, bounded retry ratio a nulové duplicate authorization. Scale-out, ktorý iba zvýši počet instances, nie je úspech.

## 10. Scale-in je correctness boundary

Scale-in môže ukončiť instance, ktorá drží keep-alive connection, queue lease alebo rozpracovanú transakciu. Bez drain contractu elasticity pri poklese trafficu vytvorí dropped alebo duplicate work.

Pre HTTP workload lifecycle vyzerá takto:

```text
instance selected for termination
→ lifecycle hook alebo target deregistration
→ stop new traffic
→ wait for in-flight requests
→ close alebo hand off background work
→ emit final telemetry
→ complete lifecycle action
→ terminate
```

Auto Scaling lifecycle hook:

```bash
aws autoscaling put-lifecycle-hook \
  --lifecycle-hook-name payments-terminating-drain \
  --auto-scaling-group-name ASG-PAY-42 \
  --lifecycle-transition autoscaling:EC2_INSTANCE_TERMINATING \
  --heartbeat-timeout 300 \
  --default-result CONTINUE \
  --region eu-central-1
```

Hook iba vytvorí wait state. Drain automation musí byť idempotentná a musí nakoniec zavolať `complete-lifecycle-action`. Ak automation zlyhá, timeout/default result určí ďalšie správanie. Hook success nepreukazuje, že request drain bol korektný.

## 11. Failure-mode capacity

Capacity sa neplánuje iba pre normálny steady state. Pri troch AZs musí remaining capacity po strate jednej AZ obslúžiť aspoň critical traffic. Ak každá AZ drží presne tretinu peak capacity bez headroomu, loss jednej AZ preťaží remaining dve.

Jednoduchý výpočet:

```text
peak demand = 1 200 requests/s
safe target capacity = 100 requests/s
required targets in normal state = 12
required targets after one-AZ loss = 12 in two AZs
minimum per surviving AZ = 6
normal placement with headroom = 6 + 6 + 6 = 18 targets
```

Tento model zvyšuje steady cost, ale umožňuje prežiť loss bez okamžitého control-plane scale-outu. Alternatívou môže byť rýchle scale-out s preukázanou capacity reservation, no musí byť testované.

## 12. Testovanie elasticity a fault tolerance

Test začína normal baselineom a explicitným stop condition. Burst test meria detection, scaling decision, launch latency, readiness a business recovery. Sustained test odhalí leak a downstream saturation. Scale-in test overí drain a idempotency. Zonal test overí traffic withdrawal a failure-mode capacity.

Každý test musí obsahovať forbidden outcome. Pre payments je to duplicate authorization, lost settlement, unrestricted retry storm alebo scale-in termination pred durable completion.

## Kontrolné otázky

1. Aký je rozdiel medzi scalability, elasticity a fault tolerance?
2. Ktorý resource je workload unit a akú má bezpečnú kapacitu?
3. Ktorý downstream určuje end-to-end maximum?
4. Prečo desired capacity nie je serving capacity?
5. Ako retries skreslia scaling metric?
6. Ako maximum ASG súvisí s DB connection budgetom?
7. Čo musí urobiť lifecycle hook automation pred termination?
8. Koľko capacity musí zostať po strate jednej AZ?
9. Ktoré evidence odlíši compute shortage od database saturation?
10. Aký business a forbidden outcome uzatvorí load/failure test?

## Oficiálna dokumentácia

- [AWS Well-Architected Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
- [Amazon EC2 Auto Scaling target tracking policies](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html)
- [Auto Scaling lifecycle hooks](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html)
- [CloudWatch metrics](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/working_with_metrics.html)
- [AWS Fault Isolation Boundaries](https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/welcome.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shared responsibility model](shared-responsibility-model.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: High availability a disaster recovery →](high-availability-disaster-recovery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
