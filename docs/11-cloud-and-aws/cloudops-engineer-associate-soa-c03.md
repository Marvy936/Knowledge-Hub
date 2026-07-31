# AWS Certified CloudOps Engineer – Associate (SOA-C03)

AWS Certified CloudOps Engineer – Associate neoveruje schopnosť zapamätať si názvy služieb. Skúša, či kandidát vie z neúplného prevádzkového symptómu vytvoriť exact subject, lokalizovať prvú divergentnú boundary, vybrať najlepší AWS-native evidence source, navrhnúť bounded remediation a overiť výsledok bez zväčšenia incidentu.

Aktuálny SOA-C03 blueprint rozdeľuje hodnotené úlohy do piatich domén:

| Doména | Váha |
|---|---:|
| Monitoring, Logging, and Remediation | 22 % |
| Reliability and Business Continuity | 22 % |
| Deployment, Provisioning, and Automation | 22 % |
| Security and Compliance | 16 % |
| Networking and Content Delivery | 18 % |

Váha neurčuje poradie učenia. Networking, IAM, observability a recovery sa v scenári často prekrývajú. Kandidát preto potrebuje spoločný reasoning model.

## 1. Exam reasoning lifecycle

```text
business or technical symptom
→ exact account, Region, resource and generation
→ managed-service responsibility boundary
→ competing hypotheses
→ cheapest discriminating observation
→ immediate containment when required
→ authoritative remediation
→ technical and business verification
```

Prvá otázka nie je „ktorá služba sa hodí?“, ale „čo presne zlyhalo a čo už vieme, že funguje?“. Ak TLS handshake prejde, route a TCP path pravdepodobne nie sú primary failure. Ak ECS task zostáva `PENDING`, application logiku ešte nemá zmysel analyzovať.

## 2. Subject card pre každú otázku

Pri čítaní scenára si v hlave vyplň krátku kartu:

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
```

Takáto karta odfiltruje odpovede, ktoré riešia inú generation alebo inú vrstvu.

## 3. Monitoring, Logging, and Remediation

Doména skúša CloudWatch metrics, logs, alarms, EventBridge, CloudTrail, Systems Manager a automatizovanú remediation. Treba odlíšiť symptom od evidence pipeline failure.

Praktický command chain:

```bash
aws cloudwatch describe-alarms \
  --alarm-names ALARM-PAY-SUCCESS-18 \
  --region eu-central-1

aws cloudwatch describe-alarm-history \
  --alarm-name ALARM-PAY-SUCCESS-18 \
  --region eu-central-1

aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=UpdateService \
  --start-time 2026-07-30T10:00:00Z \
  --end-time 2026-07-30T11:00:00Z \
  --region eu-central-1
```

Alarm state preukazuje vyhodnotenie metric/query contractu. CloudTrail preukazuje accepted API operation a caller session. Ani jeden dôkaz sám nepreukazuje runtime convergence alebo business recovery.

Pri automatizovanej remediation hľadaj idempotency, target scope, max concurrency, cooldown a postcondition. Odpoveď „restartuj všetky instances“ je zlá, ak zničí evidence alebo healthy capacity.

## 4. Reliability and Business Continuity

Táto doména zahŕňa Multi-AZ, backups, failover, quotas, scaling, RTO/RPO a recovery testing. Kandidát musí vedieť, že replication, HA a backup riešia odlišné failures.

```bash
aws ec2 describe-subnets \
  --filters Name=tag:Application,Values=payments \
  --region eu-central-1 \
  --query 'Subnets[].{Az:AvailabilityZoneId,Free:AvailableIpAddressCount}'

aws backup list-restore-jobs --region eu-west-1

aws rds describe-events \
  --source-type db-cluster \
  --source-identifier db-pay-prod-17 \
  --duration 60 \
  --region eu-central-1
```

`MultiAZ=true` nepreukazuje application reconnect. Backup `COMPLETED` nepreukazuje restore. Scale-out policy nepreukazuje subnet alebo downstream capacity.

## 5. Deployment, Provisioning, and Automation

Doména spája CloudFormation/IaC, launch templates, Auto Scaling, ECS/Lambda deployments, Systems Manager a immutable artifacts.

Rozlišuj:

```text
source template
→ rendered/processed template
→ API acceptance
→ controller convergence
→ runtime generation
→ business acceptance
```

CloudFormation stack `UPDATE_COMPLETE` môže koexistovať s application regression. Lambda alias rollback nevráti external side effects. Instance refresh bez pinned launch-template version môže miešať generations.

Praktický read-back:

```bash
aws autoscaling describe-instance-refreshes \
  --auto-scaling-group-name payments-api-prod \
  --region eu-central-1

aws ecs describe-services \
  --cluster payments-prod \
  --services payments-api \
  --region eu-central-1

aws lambda get-alias \
  --function-name payments-settle \
  --name live \
  --region eu-central-1
```

## 6. Security and Compliance

Security otázky často kombinujú actual caller, IAM evaluation, KMS, Secrets Manager, logging, encryption a Organizations guardrails.

```bash
aws sts get-caller-identity
aws kms describe-key --key-id "$KEY_ARN" --region eu-central-1
aws organizations list-parents --child-id 100000000042
```

Najprv over actual principal/session. Identity policy allow nemusí prekonať boundary, SCP, key policy alebo explicit deny. Encryption at rest nepreukazuje least-privilege decrypt ani recovery key availability.

Compliance odpoveď musí zachovať evidence, retention a separation of duties. Vypnutie loggingu kvôli costu alebo otvorenie S3 bucketu kvôli CloudFront 403 je typicky nesprávna remediation.

## 7. Networking and Content Delivery

Doména skúša VPC, subnets, routes, SG/NACL, NAT, endpoints, hybrid connectivity, Route 53, ELB a CloudFront.

Reasoning order:

```text
DNS
→ route and address identity
→ stateful/stateless policy
→ gateway or endpoint
→ TCP/TLS
→ listener/rule/cache behavior
→ application
```

`REJECT` vo Flow Logs lokalizuje network policy boundary; `ACCEPT` nepreukazuje listener. ALB target `healthy` nepreukazuje správnu listener rule. CloudFront `Hit` môže byť security incident, ak cache key ignoruje tenant identity.

## 8. Eliminačné pravidlá

Pri odpovediach odmietni riešenie, ktoré:

- mení veľa vrstiev naraz bez diskriminačného dôkazu;
- zvyšuje privileges alebo public exposure, aby zmizol symptom;
- používa dashboard alebo control-plane status ako jediný business oracle;
- navrhuje destructive replay bez idempotency a reconciliation;
- predpokladá, že managed service vlastní customer configuration alebo application semantics;
- ignoruje exact account, Region, resource generation alebo time window.

## 9. Timed question workflow

Na jednu otázku používaj tri prechody. Prvý do 20 sekúnd identifikuje subject a requirement. Druhý do 40 sekúnd porovná odpovede podľa boundary a blast radiusu. Tretí overí, že zvolená odpoveď obsahuje evidence alebo validation a nerieši iba symptom.

Pri dlhom scenári si označ:

```text
SYMPTOM
RECENT CHANGE
KNOWN HEALTHY
HARD CONSTRAINT
BEST NEXT OBSERVATION OR ACTION
```

Ak otázka žiada „MOST operationally efficient“, vyber managed/native mechanismus len vtedy, keď spĺňa correctness a scope. Efficiency nikdy neospravedlňuje nesprávnu boundary.

## 10. Mini-scenario

Po deployment-e nové ECS tasks zostávajú `PENDING`. Old tasks sú healthy, CPU hostov je 40 % a service event obsahuje `RESOURCE:ENI`.

Najlepšia ďalšia observation nie je zvýšiť CPU alebo meniť application health check. `RESOURCE:ENI` lokalizuje placement/network capacity pred process startupom. Over subnet free IPs a ENI density:

```bash
aws ec2 describe-subnets \
  --subnet-ids subnet-0paya subnet-0payb subnet-0payc \
  --query 'Subnets[].{Subnet:SubnetId,Free:AvailableIpAddressCount}'
```

Po nájdení IP exhaustion sa recovery vykoná novou subnet/address generation a controlled rolloutom. Application restart by healthy capacity iba znížil.

## 11. Praktická príprava

Každý service topic sa uč v štyroch vrstvách:

```text
mechanism and scope
→ configuration example
→ observation commands
→ failure and recovery experiment
```

Ak poznáš len definíciu NAT Gateway, nevieš riešiť port exhaustion. Ak poznáš iba CLI command, ale nie business boundary, nevieš určiť, či output incident uzatvára.

## Kontrolné otázky

1. Ktoré informácie tvoria subject card?
2. Prečo sa pri ECS `PENDING` nezačína application logom?
3. Aký rozdiel je medzi CloudTrail API success a runtime convergence?
4. Prečo Multi-AZ nepreukazuje business continuity?
5. Kedy je rollback iba code pointer a nie business rollback?
6. Prečo actual caller identity predchádza policy analýze?
7. Čo CloudFront cache hit preukazuje a aké riziko môže skrývať?
8. Ako časové tri prechody znižujú náhodné tipovanie?
9. Ktoré answer patterns treba okamžite odmietnuť?
10. Ako sa topic premení z teórie na praktickú prípravu?

## Oficiálna dokumentácia

- [AWS Certified CloudOps Engineer – Associate](https://aws.amazon.com/certification/certified-cloudops-engineer-associate/)
- [SOA-C03 Exam Guide](https://docs.aws.amazon.com/aws-certification/latest/examguides/cloudops-associate-03.html)
- [AWS Certification exam preparation](https://aws.amazon.com/certification/certification-prep/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cost management a FinOps](cost-management-finops.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CloudOps domain review a timed reasoning →](cloudops-domain-review-timed-reasoning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
