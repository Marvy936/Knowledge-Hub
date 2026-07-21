# CloudOps hands-on labs

SOA-C03 nie je hands-on performance exam, ale reálne operations porozumenie výrazne zlepšuje scenario reasoning. Tieto laby preto netrénujú iba vytvorenie resource-u. Každý scenár musí obsahovať deployment, observability, failure injection, remediation, cost/security kontrolu a cleanup.

## 1. Bezpečnostný model labov

Použi samostatný sandbox AWS account alebo izolovaný training account.

Povinné guardrails:

- budget a billing alarm,
- explicitný Region,
- MFA/federated access,
- žiadne production dáta,
- žiadne permanentné broad access keys,
- tags `Owner`, `Purpose`, `ExpiresAt`,
- cleanup checklist,
- cost review po každom lab-e.

## 2. Vykonávací protokol

```text
1. Prečítaj expected outcome a constraints.
2. Nakresli control/data path.
3. Vytvor resources cez CLI alebo IaC.
4. Over baseline.
5. Zapni monitoring a audit evidence.
6. Aplikuj jednu fault injection.
7. Diagnostikuj bez okamžitého resetu.
8. Urob minimálnu remediation.
9. Vykonaj hard validation.
10. Odstráň resources a over cost residue.
```

## 3. Lab domains

Praktická sada kopíruje váhy SOA-C03:

- monitoring/remediation/performance — 22 %, 
- reliability/business continuity — 22 %, 
- deployment/provisioning/automation — 22 %, 
- security/compliance — 16 %, 
- networking/content delivery — 18 %.

## 4. Lab 1 — IAM a cross-account operations

### Outcome

Workforce principal zo sandbox accountu prevezme operations role v target account-e.

### Požiadavky

- federated alebo temporary source identity,
- target trust policy,
- least-privilege permissions,
- session duration,
- CloudTrail evidence,
- negatívny test zakázanej action.

### Fault injection

- chybný trust principal,
- missing source `sts:AssumeRole`,
- explicit deny v SCP/boundary,
- KMS key policy mismatch.

### Validácia

```bash
aws sts get-caller-identity
aws s3api list-objects-v2 --bucket <allowed-bucket>
# zakázaná action musí zlyhať
```

## 5. Lab 2 — Multi-AZ VPC egress

### Outcome

Private workloads v dvoch AZ majú resilient outbound IPv4 path.

### Požiadavky

- VPC a dva public/private subnet pairs,
- AZ-local NAT Gateways,
- explicitné route tables,
- Flow Logs,
- bez inbound SSH/RDP,
- Session Manager pre access.

### Fault injection

- private route na NAT v nesprávnej AZ,
- chýbajúca IGW route,
- custom NACL bez return ports,
- DNS disabled.

### Validácia

- outbound HTTPS z oboch private subnetov,
- Flow Logs a NAT metrics,
- source public IP podľa AZ-local NAT,
- cleanup EIPs/NAT Gateways.

## 6. Lab 3 — Load balancer a Auto Scaling

### Outcome

Stateless service beží cez viac AZ, automaticky nahrádza unhealthy instances a scale-uje podľa loadu.

### Požiadavky

- launch template,
- Auto Scaling group,
- ALB a target group,
- health checks,
- CloudWatch alarms,
- scaling policy,
- immutable bootstrap.

### Fault injection

- chybný target port,
- health endpoint failure,
- user-data failure,
- subnet capacity issue,
- instance role missing permission.

### Hard validation

- healthy targets v dvoch AZ,
- replacement nefunkčnej instance,
- scale-out a scale-in,
- request success počas replacementu.

## 7. Lab 4 — CloudWatch, EventBridge a automated remediation

### Outcome

Operational signal automaticky spustí bezpečnú remediation a notification.

### Príklad

```text
EC2 status check alebo custom metric
→ CloudWatch alarm/EventBridge
→ Systems Manager Automation
→ remediation
→ SNS/User Notification
→ validation
```

### Požiadavky

- least-privilege execution role,
- idempotentný runbook,
- failure/timeout path,
- audit cez CloudTrail,
- metric/alarm state validation.

## 8. Lab 5 — Central logging a audit

### Outcome

API activity a selected logs sú centralizované do oddeleného log archive accountu.

### Požiadavky

- organization alebo multi-account trail podľa dostupného sandboxu,
- encrypted storage,
- restrictive bucket/KMS policies,
- retention a lifecycle,
- log-file validation,
- alert na root alebo sensitive IAM events.

### Fault injection

- bucket policy deny,
- KMS key policy mismatch,
- trail disabled,
- wrong Region scope.

## 9. Lab 6 — Backup a restore

### Outcome

Workload data má definovaný RPO/RTO a overený restore.

### Varianty

- EBS snapshot a instance recovery,
- RDS snapshot/PITR,
- S3 versioning a restore,
- AWS Backup plan a cross-account copy.

### Povinné

- backup policy,
- retention,
- encryption,
- deletion protection podľa scenára,
- isolated restore,
- data integrity validation,
- evidence actual RTA/RPA.

## 10. Lab 7 — Systems Manager operations

### Outcome

Fleet je spravovaný bez inbound management portov.

Použi:

- Session Manager,
- Run Command,
- Inventory,
- Patch Manager,
- State Manager alebo Automation.

### Fault injection

- chýbajúca instance profile permission,
- unavailable SSM endpoint/internet path,
- stopped agent,
- wrong patch baseline/tag target.

## 11. Lab 8 — CloudFormation lifecycle

### Outcome

Infrastructure stack prejde create, change set, update, drift a rollback scenárom.

### Požiadavky

- parameterized template,
- change set review,
- outputs,
- stack policy alebo termination protection podľa scenára,
- drift detection,
- intentional failed update,
- rollback evidence.

### Rozšírenie

StackSets do viacerých accounts/Regions v sandbox organization.

## 12. Lab 9 — Storage performance a cost

### Outcome

Porovnaj S3, EBS a EFS podľa access, consistency, durability, performance a cost modelu.

Prakticky over:

- EBS volume type/IOPS/throughput,
- filesystem growth,
- EFS mount targets v AZs,
- S3 lifecycle/versioning,
- CloudWatch metrics,
- orphan resources a cost.

## 13. Lab 10 — RDS operations

### Outcome

Managed database má monitoring, backup, HA a controlled failover/restore model.

Požiadavky:

- subnet group,
- Security Groups,
- automated backups/PITR,
- Enhanced Monitoring alebo Performance Insights podľa dostupnosti,
- Multi-AZ podľa scenára,
- parameter change a maintenance semantics,
- restore do nového instance/clusteru.

## 14. Lab 11 — Route 53 a content delivery

### Outcome

DNS a content path používa správny routing, health a caching model.

Varianty:

- alias na ALB,
- weighted alebo failover routing,
- private hosted zone,
- Resolver endpoints,
- CloudFront origin a cache behavior.

Faults:

- wrong record scope,
- TTL/cache confusion,
- unhealthy failover target,
- certificate/alternate-domain mismatch,
- origin SG/policy failure.

## 15. Lab 12 — Containers a serverless operations

### Variant A — ECS/EKS

- deployment,
- IAM role separation,
- logs/metrics,
- image pull,
- health failure,
- scaling a rollback.

### Variant B — Lambda

- execution role,
- environment/secrets,
- timeout/memory,
- concurrency/throttling,
- DLQ/destination,
- VPC networking,
- log-based troubleshooting.

## 16. Timed lab sets

### Set A — 60 minút

- IAM access,
- VPC route failure,
- CloudWatch alarm/remediation,
- cleanup.

### Set B — 90 minút

- ALB/Auto Scaling,
- Systems Manager,
- backup restore,
- security validation.

### Set C — 150 minút

Domain-balanced operations scenario s minimálne jedným multi-account alebo multi-Region prvkom.

## 17. Scoring

| Oblasť | Body |
|---|---:|
| Outcome funguje | 35 |
| Security a least privilege | 15 |
| Observability/evidence | 15 |
| Failure diagnosis/remediation | 20 |
| Cost a cleanup | 10 |
| Dokumentácia validation | 5 |

Funkčný resource bez cleanupu a security contractu nie je plný úspech.

## 18. Review template

```text
Lab:
Dátum/Region/account:
Čas:
Expected outcome:
Architecture:
Fault:
Evidence:
Root cause:
Remediation:
Hard validation:
Cost before/after:
Cleanup residue:
SOA-C03 domain:
Čo zopakovať:
```

## 19. Praktická oblasť

Konkrétne vykonávacie sety a checklisty sú v [labs/aws-cloudops](../../labs/aws-cloudops/README.md).

## 20. Glossary impact

Relevantné pojmy: CloudOps hands-on lab, AWS sandbox account, cost-safe lab, hard validation, operational lab score, fault injection, automated remediation lab, isolated restore lab a cleanup residue.

## Oficiálne zdroje

- [SOA-C03 exam guide](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03.html)
- [AWS Builder Labs](https://skillbuilder.aws/)
- [AWS Well-Architected Labs](https://www.wellarchitectedlabs.com/)
