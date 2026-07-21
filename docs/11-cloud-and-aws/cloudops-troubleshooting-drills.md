# CloudOps troubleshooting drills

CloudOps troubleshooting drills trénujú failure-domain narrowing pre AWS workloads. Každý scenár má jednu známu primárnu chybu, merateľný expected state, bezpečný reset a explicitnú evidence path. Cieľom nie je uhádnuť službu podľa symptómu, ale preukázať systematickú diagnostiku naprieč identity, network, compute, storage, observability a recovery vrstvami.

## 1. Drill protocol

```text
1. Potvrď account, Region a caller identity.
2. Definuj symptóm, čas a scope.
3. Zachovaj CloudTrail/log/metric/config evidence.
4. Nakresli control-plane alebo data-plane path.
5. Pomenuj root cause pred opravou.
6. Urob najmenšiu bezpečnú zmenu.
7. Vykonaj pozitívnu aj negatívnu validation.
8. Resetni fault a odstráň lab resources.
9. Zapíš diagnosis/repair/verify čas.
```

## 2. Evidence baseline

Začni podľa scenára:

```bash
aws sts get-caller-identity
aws configure list
aws ec2 describe-regions
```

Ďalej zachovaj:

- UTC timestamp,
- API request/error ID,
- CloudTrail event,
- CloudWatch alarm/log/metric,
- resource configuration JSON,
- route/SG/NACL/policy state,
- recent deployment/change,
- provider service health podľa scope-u.

## 3. Drill 1 — AccessDenied pri cross-account role

### Varianty

- source nemá `sts:AssumeRole`,
- target trust policy používa chybný principal,
- SCP explicitne denyuje action,
- permissions boundary zúžila role,
- KMS key policy nepovoľuje target action,
- session tag condition chýba.

### Validation

- `aws sts get-caller-identity` ukazuje target session,
- povolená action uspeje,
- zakázaná action zostáva denied.

## 4. Drill 2 — EC2 v public subnet-e nemá internet

### Varianty

- chýba public IPv4/EIP,
- default route nesmeruje na IGW,
- IGW nie je attached,
- SG/NACL blokuje,
- instance/listener problém.

### Path

```text
addressing → route → IGW → SG/NACL → OS/application
```

## 5. Drill 3 — Private subnet nemá outbound internet

### Varianty

- private route na nesprávny NAT,
- NAT v private subnet-e,
- NAT public subnet nemá IGW route,
- NACL blokuje ephemeral return ports,
- NAT unavailable alebo port allocation errors.

Nepridávaj public IP private instance ako rýchlu opravu.

## 6. Drill 4 — ALB má zero healthy targets

### Varianty

- wrong target port,
- target SG nepovoľuje ALB SG,
- health path vracia non-success,
- application binduje na localhost,
- target subnet/NACL,
- target type/registration mismatch.

### Validation

- target health reason je healthy,
- request cez ALB uspeje,
- direct unauthorized path zostáva blokovaný.

## 7. Drill 5 — Auto Scaling nevytvára instances

### Varianty

- launch template AMI neexistuje v Regione,
- subnet nemá IP capacity,
- instance type unavailable,
- service-linked role/PassRole problem,
- quota,
- user-data/bootstrap failure,
- health check replacement loop.

Rozlišuj launch failure od launch success + unhealthy termination.

## 8. Drill 6 — CloudWatch alarm zostáva `INSUFFICIENT_DATA`

### Varianty

- nesprávny namespace/dimensions,
- metric sa publikuje v inom Regione,
- period/statistic mismatch,
- chýbajúce datapoints,
- agent/permissions failure,
- low-frequency metric.

### Validation

Vynúť kontrolovaný datapoint a sleduj prechod alarm state-u.

## 9. Drill 7 — Automated remediation sa nespustí

### Path

```text
signal/event
→ EventBridge rule/alarm action
→ target invocation
→ execution role
→ runbook/function
→ target permissions
→ result/notification
```

Varianty:

- event pattern nesedí,
- target role trust,
- Lambda resource policy,
- SSM Automation assume role,
- throttling/dead-letter failure.

## 10. Drill 8 — CloudTrail neprijíma events do central bucketu

### Varianty

- bucket policy,
- KMS key policy,
- organization trail scope,
- Region/global-service settings,
- trail stopped,
- log-file validation alebo prefix mismatch.

Nemeň bucket na public alebo broad write access.

## 11. Drill 9 — Systems Manager managed node offline

### Varianty

- SSM Agent stopped,
- instance profile missing permissions,
- DNS/HTTPS egress,
- chýbajúce interface endpoints v isolated subnet-e,
- time drift,
- unsupported OS/agent,
- proxy config.

### Validation

Node je managed, Run Command a Session Manager fungujú bez inbound SSH.

## 12. Drill 10 — EBS volume performance alebo attach failure

### Varianty

- volume a instance v odlišných AZ,
- device/filesystem nie je mounted,
- IOPS/throughput limit,
- instance EBS bandwidth,
- filesystem full/inodes,
- stale attachment,
- encryption/KMS permissions.

Rozlišuj AWS volume metrics od guest filesystem state-u.

## 13. Drill 11 — RDS connection timeout

### Path

```text
DNS endpoint
→ route/subnet
→ client SG outbound
→ DB SG inbound
→ NACL
→ RDS state
→ listener/auth/TLS
```

Varianty:

- wrong endpoint/port,
- SG reference,
- public accessibility confusion,
- route/VPN,
- max connections,
- failover DNS cache,
- credential rotation.

## 14. Drill 12 — Backup job failed alebo restore unusable

### Varianty

- IAM role,
- KMS permissions,
- backup vault policy,
- resource not selected/tagged,
- lifecycle/retention,
- cross-account copy trust,
- restore networking/parameter groups,
- application-consistency gap.

Backup status `COMPLETED` nepreukazuje usable restore.

## 15. Drill 13 — Route 53 failover neprepne traffic

### Varianty

- health check sleduje nesprávny endpoint,
- record routing policy/identifier,
- TTL/cache,
- alias evaluation,
- secondary unhealthy,
- private/public hosted zone confusion.

Validuj authoritative DNS response aj end-to-end service.

## 16. Drill 14 — CloudFront vracia 403 alebo stale content

### Varianty

- origin access policy/OAC,
- S3 bucket policy,
- alternate domain/certificate,
- cache behavior/path,
- signed URL/cookie,
- WAF,
- cached error response.

Invalidation nie je prvý krok pri origin authorization failure.

## 17. Drill 15 — Lambda timeout vo VPC

### Varianty

- private subnet bez NAT/VPC endpointu,
- SG outbound,
- DNS,
- cold-start/ENI behavior,
- dependency latency,
- memory/CPU allocation,
- reserved concurrency/throttling.

Rozlišuj function duration timeout od invocation throttlingu.

## 18. Drill 16 — ECS task `PENDING` alebo `STOPPED`

### Varianty

- image pull/network,
- task execution role,
- task role,
- CPU/memory placement,
- log driver,
- secret/KMS permission,
- health check,
- target registration.

Použi stopped reason, service events a task logs.

## 19. Drill 17 — EKS workload nevie AWS API

### Varianty

- node role vs Pod identity/IRSA confusion,
- OIDC trust condition,
- ServiceAccount annotation/association,
- SDK credential chain,
- STS endpoint/network,
- IAM/SCP/KMS policy.

Nepoužívaj node role broadening ako fix pre Pod identity.

## 20. Drill 18 — CloudFormation stack v rollback/pending state

### Varianty

- immutable property,
- custom resource timeout,
- IAM/PassRole,
- missing dependency,
- resource quota,
- deletion policy/retained resource,
- nested stack failure.

Zachovaj stack events v chronologickom poradí.

## 21. Drill 19 — NAT cost alebo port exhaustion spike

### Evidence

- NAT CloudWatch metrics,
- Flow Logs,
- destination concentration,
- cross-AZ routing,
- AWS service traffic,
- application connection churn.

### Remediation možnosti

- connection pooling,
- VPC endpoint,
- AZ-local NAT,
- destination distribution,
- additional supported NAT capacity,
- proxy architecture.

## 22. Drill 20 — Organization-wide deny po SCP zmene

### Bezpečnostný postup

- identifikuj attachment point a inheritance,
- over management-account behavior,
- použi break-glass/incident role,
- zachovaj policy version/change event,
- zúž deny alebo presuň account do quarantine/recovery OU podľa runbooku,
- over, že požadované guardrails zostávajú.

Nikdy nerob ďalšie broad policy zmeny bez simulácie scope-u.

## 23. Drill 21 — Region mismatch

Symptómy:

- resource „neexistuje“,
- alarm bez dát,
- AMI ID invalid,
- certificate unavailable pre service scope,
- KMS key alebo secret nenájdený.

Prvý test:

```bash
aws configure get region
aws sts get-caller-identity
```

Potom explicitne používaj `--region` v laboch.

## 24. Drill 22 — Service quota alebo capacity failure

Rozlišuj:

- account quota,
- regional service quota,
- zonal capacity shortage,
- API throttling,
- subnet IP exhaustion,
- organization policy,
- unsupported instance/service in AZ.

Quota increase nevyrieši zonal capacity shortage.

## 25. Fault injection design

Použi jednu známu zmenu:

- odstráň route,
- zmeň SG source,
- pridaj explicit deny condition,
- zastav SSM Agent,
- zmeň alarm dimension,
- poškodi health-check path,
- zmeň KMS key policy principal,
- odstráň VPC endpoint,
- zmeň backup selection tag.

Neskôr kombinuj dve súvisiace chyby, nie náhodný chaos.

## 26. Time limits

- jednoduchý resource/config drill: 8 minút,
- multi-layer data path: 12–15 minút,
- multi-account/backup/control-plane: 15–20 minút,
- composite incident: 30 minút.

Meraj osobitne diagnosis, repair a validation.

## 27. Review template

```text
Drill ID:
Account/Region:
Symptóm:
Scope:
Control alebo data plane:
Prvá hypotéza:
Evidence:
Root cause:
Remediation:
Pozitívna validation:
Negatívna validation:
Diagnosis/repair/verify čas:
Cost/cleanup:
SOA-C03 domain:
```

## 28. Praktická oblasť

Scenárový index je v [troubleshooting/aws-cloudops](../../troubleshooting/aws-cloudops/README.md).

## 29. Anti-patterny

### Okamžité pridanie AdministratorAccess

Zničí IAM evidence a rozšíri blast radius.

### Otvorenie `0.0.0.0/0` pri network failure

Maskuje route/listener root cause a vytvára exposure.

### Restart/replace bez evidence

Odstráni logs, state a failure reason.

### Restore do production ako prvý test

Obchádza isolated validation a môže prepísať state.

### Troubleshooting iba cez console

Skrýva reproducible CLI/API evidence a presné JSON fields.

## 30. Glossary impact

Relevantné pojmy: AWS CloudOps troubleshooting drill, account/Region baseline, control-plane path, data-plane path, CloudTrail evidence, hard validation, organization-wide deny, zonal capacity failure, operational fault injection a CloudOps incident review.

## Oficiálne zdroje

- [SOA-C03 exam guide](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03.html)
- [AWS troubleshooting resources](https://repost.aws/knowledge-center/)
- [AWS Systems Manager troubleshooting](https://docs.aws.amazon.com/systems-manager/latest/userguide/troubleshooting.html)
- [Amazon VPC troubleshooting](https://docs.aws.amazon.com/vpc/latest/userguide/troubleshooting.html)
