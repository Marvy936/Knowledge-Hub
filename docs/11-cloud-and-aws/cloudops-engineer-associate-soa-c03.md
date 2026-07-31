# AWS Certified CloudOps Engineer – Associate (SOA-C03)

AWS Certified CloudOps Engineer – Associate neoveruje iba schopnosť zapamätať si názvy služieb. Skúša, či kandidát vie z neúplného prevádzkového symptómu vytvoriť exact subject, lokalizovať prvú divergentnú boundary, vybrať najlepší AWS-native evidence source, navrhnúť bounded remediation a overiť výsledok bez zväčšenia incidentu.

K 31. júlu 2026 má SOA-C03 päť content domains. Monitoring, Logging, Analysis, Remediation and Performance Optimization má 22 %, Reliability and Business Continuity 22 %, Deployment, Provisioning and Automation 22 %, Security and Compliance 16 % a Networking and Content Delivery 18 % scored contentu. Oficiálny exam guide je versionovaný dokument; pred skúškou sa musí overiť jeho aktuálna revision, pretože AWS môže meniť skills aj in-scope služby.

Váha neurčuje poradie učenia ani diagnostiky. Networking, IAM, observability, deployment a recovery sa v reálnom scenári prekrývajú. Kandidát preto potrebuje spoločný reasoning lifecycle:

```text
business alebo technical symptom
→ exact account, Region, resource, principal a generation
→ required outcome a hard constraints
→ managed-service responsibility boundary
→ known healthy a first divergent boundary
→ competing hypotheses
→ najlacnejšia discriminating observation
→ evidence-preserving containment
→ authoritative remediation
→ technical, business a forbidden validation
```

## Exam reasoning lifecycle

Prvá otázka nie je „ktorá AWS služba sa hodí?“, ale „čo presne zlyhalo a čo už vieme, že funguje?“. Ak TLS handshake prejde, DNS, route a TCP path pravdepodobne nie sú primary failure. Ak ECS task zostáva `PENDING`, application process ešte nevznikol a jeho logiku nemá zmysel analyzovať.

Lifecycle zároveň oddeľuje observation od mutation. Read-only API call má zmenšiť hypothesis space. Containment má chrániť business outcome a dôkaz. Remediation má meniť authoritative boundary, nie náhodný symptom. Acceptance musí obsahovať runtime alebo business oracle; control-plane status je iba čiastkový verdict.

## Subject card pre každú otázku

Pri čítaní scenára si vytvor krátku kartu. Jej úlohou je zabrániť odpovedi nad nesprávnym accountom, Regionom, resource-om alebo generation.

```yaml
service: payments-api
account: production-payments
region: eu-central-1
resource: ecs-service/payments-api
change: task-definition 118 -> 119
symptom: new tasks PENDING
knownHealthy:
  - old tasks serve traffic
  - database is reachable from old tasks
unknown:
  - capacity-provider placement
  - subnet IP headroom
  - task execution role
requiredOutcome: restore serving capacity without interrupting old cohort
forbiddenOutcome: terminate healthy old tasks before replacement capacity serves
```

Táto karta odfiltruje riešenia, ktoré menia application health check, hoci scheduler ešte task nespustil. Zároveň fixuje safety boundary: old cohort zostáva healthy capacity a nesmie byť zničený iba preto, aby sa deployment „pohol“.

## Domain 1: Monitoring, Logging, Analysis, Remediation and Performance Optimization

Doména testuje CloudWatch metrics, logs, alarms, EventBridge, CloudTrail, Systems Manager a performance observations. Kandidát musí rozlíšiť reálny service failure od chyby telemetry identity, ingestion, query alebo alarm evaluation.

```bash
aws cloudwatch describe-alarms \
  --alarm-names ALARM-PAY-SUCCESS-18 \
  --region eu-central-1 \
  --query 'MetricAlarms[0].{State:StateValue,Metric:MetricName,Dimensions:Dimensions,Missing:TreatMissingData}'

aws cloudwatch describe-alarm-history \
  --alarm-name ALARM-PAY-SUCCESS-18 \
  --history-item-type StateUpdate \
  --region eu-central-1

aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=PutMetricAlarm \
  --start-time 2026-07-30T10:00:00Z \
  --end-time 2026-07-30T11:00:00Z \
  --region eu-central-1
```

Prvý príkaz číta exact alarm contract. Druhý ukazuje state transitions a dôvod vyhodnotenia. CloudTrail viaže zmenu configuration na caller session a timestamp. Ani jeden výsledok sám nepreukazuje payment failure alebo recovery. Business logs, current metric publication a synthetic transaction musia overiť, či sa opravil iba alarm alebo aj používateľský outcome.

Pri automatizovanej remediation sleduj target scope, idempotency, max concurrency, cooldown, retry contract a postcondition. Odpoveď „restartuj všetky instances“ je nesprávna, ak zničí healthy capacity alebo diagnostický dôkaz. Správna remediation má byť viazaná na exact alarm generation a musí po mutation vykonať read-back aj workload check.

## Domain 2: Reliability and Business Continuity

Táto doména zahŕňa Multi-AZ, scaling, quotas, backup, restore, failover, RTO/RPO a recovery testing. Kandidát musí rozlišovať availability, replication a historical recovery. Každý mechanizmus chráni inú failure class.

```bash
aws ec2 describe-subnets \
  --filters Name=tag:Application,Values=payments \
  --region eu-central-1 \
  --query 'Subnets[].{Subnet:SubnetId,Az:AvailabilityZoneId,Free:AvailableIpAddressCount}'

aws backup list-restore-jobs \
  --by-status COMPLETED \
  --region eu-west-1

aws rds describe-events \
  --source-type db-cluster \
  --source-identifier db-pay-prod-17 \
  --duration 60 \
  --region eu-central-1
```

Subnet output preukazuje address headroom, nie EC2 alebo downstream capacity. Backup restore status preukazuje vytvorenie restore resource-u, nie application recoverability. RDS events vysvetľujú service transitions, ale nepreukazujú reconnect správanie klientov ani výsledok in-flight transactions.

Typický distractor použije Multi-AZ failover na logical deletion. Standby však môže chybnú zmenu korektne replikovať. Správny recovery path používa clean PITR alebo backup generation, isolated validation, reconciliation a controlled cutover. Acceptance meria Recovery Point Actual, Recovery Time Actual a business invariants, nie iba `available`.

## Domain 3: Deployment, Provisioning and Automation

Doména spája CloudFormation a IaC, launch templates, Auto Scaling, ECS, Lambda, Systems Manager a immutable artifacts. Kľúčom je rozlíšiť source intent, API acceptance, controller convergence, runtime generation a business acceptance.

```text
source template alebo release intent
→ rendered/processed input
→ accepted API mutation
→ controller convergence
→ admitted runtime resources
→ serving workload
→ business acceptance
```

CloudFormation `UPDATE_COMPLETE` môže koexistovať s application regression. Lambda alias rollback zmení traffic pointer, ale nevráti external side effects. Instance refresh bez pinned launch-template version môže miešať generations.

```bash
aws autoscaling describe-instance-refreshes \
  --auto-scaling-group-name payments-api-prod \
  --region eu-central-1

aws ecs describe-services \
  --cluster payments-prod \
  --services payments-api \
  --region eu-central-1 \
  --query 'services[0].{Desired:desiredCount,Running:runningCount,Deployments:deployments,Events:events[0:5]}'

aws lambda get-alias \
  --function-name payments-settle \
  --name live \
  --region eu-central-1
```

Každý príkaz číta iný controller subject. Instance refresh ukazuje replacement progress a failure reason. ECS service ukazuje task cohorts a rollout events. Lambda alias ukazuje effective traffic target. Po read-backu musí nasledovať runtime probe cez intended network path a business request s traceable identity.

## Domain 4: Security and Compliance

Security otázky kombinujú actual caller, IAM evaluation, KMS, Secrets Manager, Organizations guardrails, logging a data protection. Authorization verdict nevzniká iba z identity policy. Môže ho ovplyvniť permissions boundary, session policy, resource policy, SCP alebo RCP, KMS key policy, endpoint policy a explicit deny.

```bash
aws sts get-caller-identity

aws kms describe-key \
  --key-id "$KEY_ARN" \
  --region eu-central-1 \
  --query 'KeyMetadata.{Arn:Arn,State:KeyState,Usage:KeyUsage}'

aws organizations list-parents \
  --child-id 100000000042
```

`get-caller-identity` fixuje actual role session a account. KMS read-back overuje exact key a state, ale úspešný `DescribeKey` nepreukazuje `Decrypt`. Organizations parent určuje OU context, z ktorého môžu prichádzať guardrails. Správna odpoveď hľadá prvú authorization boundary, nie broad allow pridávaný naslepo.

Compliance remediation musí zachovať evidence, retention a separation of duties. Vypnutie loggingu kvôli costu alebo otvorenie S3 bucketu kvôli CloudFront 403 odstráni symptom za cenu väčšieho security incidentu. Positive test musí byť doplnený forbidden testom, ktorý preukáže, že nepovolený principal alebo context zostáva odmietnutý.

## Domain 5: Networking and Content Delivery

Doména skúša VPC, subnets, routes, security groups, NACLs, NAT, endpoints, hybrid connectivity, Route 53, load balancers a CloudFront. Diagnostika má rešpektovať packet a request path:

```text
DNS a selected address
→ effective route
→ stateful a stateless policy
→ gateway, endpoint alebo attachment
→ TCP a TLS
→ listener, rule alebo cache behavior
→ application outcome
```

`REJECT` vo VPC Flow Logs lokalizuje určitú network boundary; `ACCEPT` nepreukazuje listener alebo application response. ALB target `healthy` nepreukazuje, že intended listener rule routuje na správny target group. CloudFront `Hit` môže byť performance success alebo security incident, ak cache key ignoruje tenant identity.

```bash
dig pay.example.com A

aws ec2 describe-route-tables \
  --filters Name=association.subnet-id,Values=subnet-0payc \
  --region eu-central-1

aws elbv2 describe-target-health \
  --target-group-arn "$TG_ARN" \
  --region eu-central-1
```

DNS output dokazuje resolver-visible answer. Route-table output dokazuje configured next-hop candidates, nie return path. Target health ukazuje load-balancer health-check verdict a reason code. Správna exam odpoveď vyberá observation point, ktorý najlacnejšie rozlíši vedúce hypotheses pri zachovaní healthy trafficu.

## Eliminačné pravidlá

Eliminačné pravidlá nie sú zoznamom magických slov. Každé odstraňuje answer pattern, ktorý porušuje operational reasoning.

Odpoveď, ktorá mení viac vrstiev naraz bez discriminating evidence, zväčšuje blast radius a skrýva root cause. Odpoveď, ktorá pridáva wildcard privileges alebo public exposure, rieši authorization symptom vytvorením väčšieho security problému. Dashboard alebo control-plane status nemožno použiť ako jediný business oracle, pretože meria iba určitú observation boundary.

Destructive replay bez idempotency a reconciliation je nebezpečný pri unknown transaction outcome. Managed service nepreberá zákaznícku zodpovednosť za application semantics, data classification alebo customer configuration. Answer, ktorý ignoruje exact account, Region, principal, resource generation alebo time window, rieši neurčitý systém a musí byť vyradený.

## Timed question workflow

Na jednu otázku používaj tri prechody. Prvý do približne 20 sekúnd identifikuje subject, required outcome a hard constraint. Druhý lokalizuje first-divergent boundary a porovná answer choices podľa evidence a blast radiusu. Tretí overí, či vybraná odpoveď obsahuje read-back, runtime validation alebo bezpečný ďalší observation point.

```text
SYMPTOM
RECENT CHANGE
KNOWN HEALTHY
HARD CONSTRAINT
FIRST DIVERGENT BOUNDARY
BEST NEXT OBSERVATION OR ACTION
```

Formulácia `MOST operationally efficient` neznamená najkratší príkaz. AWS-native managed mechanismus je efektívny iba vtedy, keď rieši správnu boundary a spĺňa correctness, security a recovery constraints. Automatický restart celej fleet-y môže byť jednoduchý na vykonanie a zároveň operationally najhorší.

## Worked mini-scenario: ECS tasks zostávajú PENDING

Po deployment-e nové ECS tasks zostávajú `PENDING`. Old tasks sú healthy, host CPU je približne 40 % a service event obsahuje `RESOURCE:ENI`. Tento reason lokalizuje failure pred application process startupom. Meniť application health check alebo reštartovať old cohort preto nerieši prvú divergentnú boundary.

```bash
aws ecs describe-services \
  --cluster payments-prod \
  --services payments-api \
  --region eu-central-1 \
  --query 'services[0].events[0:10]'

aws ec2 describe-subnets \
  --subnet-ids subnet-0paya subnet-0payb subnet-0payc \
  --region eu-central-1 \
  --query 'Subnets[].{Subnet:SubnetId,Az:AvailabilityZoneId,Free:AvailableIpAddressCount}'
```

Prvý read-back potvrdí scheduler reason a časový vzťah k deploymentu. Druhý porovná subnet headroom medzi AZs. Ak je first boundary IP exhaustion, recovery pridá approved subnet alebo address generation a spustí controlled canary rollout. Acceptance overí task definition digest, task role, target health, per-AZ serving a payment canary. Forbidden outcome je strata old healthy capacity pred pripravenosťou replacementu.

## Praktická príprava

Každý service topic sa uč v štyroch vrstvách: mechanizmus a scope, konkrétna configuration, observation commands a failure/recovery experiment. Definícia NAT Gateway nestačí, ak nevieš vysvetliť route dependency, source-port pressure, telemetry a recovery. CLI syntax nestačí, ak nevieš povedať, čo output dokazuje a čo stále zostáva neznáme.

Príprava preto spája túto syllabus kapitolu s timed reasoning, hands-on labs a troubleshooting drills. Topic sa považuje za zvládnutý až vtedy, keď kandidát vie správny command nielen rozpoznať, ale interpretovať output, zvoliť bounded mutation a vykonať positive, recovery, forbidden a second-operation validation.

## Kontrolné otázky

1. Ktoré informácie tvoria subject card?
2. Prečo sa pri ECS `PENDING` nezačína application logom?
3. Aký rozdiel je medzi CloudTrail API success a runtime convergence?
4. Prečo Multi-AZ nepreukazuje business continuity?
5. Kedy je rollback iba code pointer a nie business rollback?
6. Prečo actual caller identity predchádza policy analýze?
7. Čo CloudFront cache hit preukazuje a aké riziko môže skrývať?
8. Ako tri timed prechody znižujú náhodné tipovanie?
9. Ktoré answer patterns treba vyradiť a prečo?
10. Ako sa service topic premení z teórie na practical readiness?

## Oficiálna dokumentácia

- [AWS Certified CloudOps Engineer – Associate](https://aws.amazon.com/certification/certified-cloudops-engineer-associate/)
- [SOA-C03 Exam Guide](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03.html)
- [SOA-C03 revisions](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/soa-03-revisions.html)
- [AWS Certification exam preparation](https://aws.amazon.com/certification/certification-prep/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cost management a FinOps](cost-management-finops.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CloudOps domain review a timed reasoning →](cloudops-domain-review-timed-reasoning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
