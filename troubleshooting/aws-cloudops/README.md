# AWS CloudOps troubleshooting drills

Praktický fault-injection index pre AWS Certified CloudOps Engineer – Associate (SOA-C03). Každý drill má jednu známu primárnu chybu, presný expected state, bezpečný reset a merateľnú hard validation.

Autoritatívny kontext:

- [SOA-C03 guide](../../docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md)
- [CloudOps troubleshooting drills](../../docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md)
- [CloudOps hands-on labs](../../docs/11-cloud-and-aws/cloudops-hands-on-labs.md)

## Execution protocol

```text
1. Over caller identity, account a Region.
2. Spusti timer.
3. Zapíš symptóm, scope a poslednú zmenu.
4. Zachovaj API, CloudTrail, metric, log a configuration evidence.
5. Identifikuj control-plane alebo data-plane path.
6. Pomenuj root cause pred opravou.
7. Urob minimálnu zmenu.
8. Over pozitívny aj negatívny path.
9. Resetni fault a odstráň resources.
10. Zapíš diagnosis/repair/verify čas a cost residue.
```

## Scenario index

| ID | Scenár | Primárna vrstva | Limit |
|---|---|---|---:|
| AWS-CO-001 | Cross-account AssumeRole AccessDenied | IAM/STS | 10 min |
| AWS-CO-002 | KMS key policy blokuje povolenú application action | IAM/KMS | 12 min |
| AWS-CO-003 | SCP deny blokuje member account | Organizations/IAM | 12 min |
| AWS-CO-004 | Public EC2 bez internet connectivity | VPC/IGW | 10 min |
| AWS-CO-005 | Private subnet bez NAT egressu | VPC/NAT | 12 min |
| AWS-CO-006 | NACL blokuje ephemeral return traffic | NACL | 12 min |
| AWS-CO-007 | ALB zero healthy targets | ELB/application | 12 min |
| AWS-CO-008 | Auto Scaling launch failure | EC2/ASG | 15 min |
| AWS-CO-009 | CloudWatch alarm `INSUFFICIENT_DATA` | Monitoring | 10 min |
| AWS-CO-010 | EventBridge remediation target sa nespustí | Automation/IAM | 12 min |
| AWS-CO-011 | CloudTrail central delivery failure | Audit/S3/KMS | 15 min |
| AWS-CO-012 | SSM managed node offline | Systems Manager | 12 min |
| AWS-CO-013 | EBS volume attach/performance failure | Storage | 15 min |
| AWS-CO-014 | RDS connection timeout | Database/network | 15 min |
| AWS-CO-015 | Backup copy alebo restore failure | Backup/KMS/IAM | 18 min |
| AWS-CO-016 | Route 53 failover neprepne traffic | DNS/HA | 15 min |
| AWS-CO-017 | CloudFront 403 alebo stale content | CDN/origin | 15 min |
| AWS-CO-018 | Lambda timeout vo VPC | Serverless/network | 12 min |
| AWS-CO-019 | ECS task `PENDING` alebo `STOPPED` | Containers | 15 min |
| AWS-CO-020 | EKS Pod nemá AWS API permissions | EKS/IAM | 15 min |
| AWS-CO-021 | CloudFormation stack rollback failure | IaC | 15 min |
| AWS-CO-022 | NAT cost/port exhaustion spike | Network/performance | 15 min |
| AWS-CO-023 | Region mismatch | Scope/config | 6 min |
| AWS-CO-024 | Service quota alebo zonal capacity failure | Capacity | 12 min |

## AWS-CO-001 — Cross-account AssumeRole

Fault injection:

- odstráň source permission `sts:AssumeRole`, alebo
- zmeň target trust principal.

Evidence:

```bash
aws sts get-caller-identity
aws sts assume-role --role-arn <arn> --role-session-name drill
```

Validation:

- target session vznikne,
- allowed action uspeje,
- unrelated privileged action zostane denied.

## AWS-CO-002 — KMS policy mismatch

Fault injection:

- workload IAM role má service action, ale key policy/grant neumožňuje cryptographic use.

Expected diagnosis:

- primary service permission je allow,
- dependent KMS action alebo key policy blokuje request.

Neopravuj broad `kms:*` na `*`.

## AWS-CO-003 — SCP deny

Fault injection:

- pripoj scoped explicit deny na test OU/account.

Evidence:

- CloudTrail event,
- effective OU hierarchy,
- IAM policy simulator podľa podporovaného scope-u,
- Organizations policy attachment.

Validation:

- požadovaná action funguje po úzkej oprave,
- guardrail pre zakázaný scope zostáva.

## AWS-CO-004 — Public EC2 bez internetu

Varianty:

- bez public IPv4,
- missing `0.0.0.0/0 → IGW`,
- IGW detached,
- SG/NACL,
- OS listener/firewall.

Validation musí oddeliť outbound HTTPS od inbound application pathu.

## AWS-CO-005 — Private subnet bez NAT egressu

Fault injection:

- private route na nesprávny NAT,
- NAT public subnet bez IGW route,
- NAT Gateway v nevyhovujúcom subnet-e.

Validation:

- instance zostáva bez public IP,
- outbound HTTPS funguje,
- source address zodpovedá očakávanému NAT EIP.

## AWS-CO-006 — NACL return path

Fault injection:

- povoľ inbound service port, ale zablokuj relevantný outbound ephemeral range.

Expected diagnosis:

- SG je správny,
- Flow Logs/NACL ordering ukazuje stateless return failure.

## AWS-CO-007 — ALB targets unhealthy

Fault variants:

- wrong target port,
- health path,
- target SG,
- application bind,
- NACL.

Evidence:

```bash
aws elbv2 describe-target-health --target-group-arn <arn>
```

Validation:

- targets healthy,
- request cez ALB funguje,
- direct unauthorized path je blokovaný.

## AWS-CO-008 — Auto Scaling launch failure

Fault variants:

- invalid AMI/instance type,
- subnet IP exhaustion,
- PassRole/service-linked role,
- quota/capacity,
- user data failure.

Rozlišuj launch failure od health-check replacement loopu.

## AWS-CO-009 — Alarm without data

Fault variants:

- wrong Region,
- namespace/dimensions,
- statistic/period,
- agent permission,
- metric frequency.

Validation:

- kontrolovaný datapoint spôsobí očakávaný state transition.

## AWS-CO-010 — Automated remediation chain

Path:

```text
event/metric
→ EventBridge/alarm
→ target permission
→ execution role
→ automation/function
→ target resource
→ result
```

Validation zahŕňa audit event a idempotentný repeat.

## AWS-CO-011 — CloudTrail delivery

Fault variants:

- bucket policy,
- KMS key policy,
- wrong prefix/account condition,
- trail stopped,
- organization scope.

Validation:

- nový test event je doručený,
- log-file validation/encryption zostáva aktívna.

## AWS-CO-012 — Systems Manager offline

Fault variants:

- agent stopped,
- instance profile,
- endpoint/NAT/DNS,
- proxy/time sync.

Validation:

- managed-node status online,
- Session Manager a Run Command bez inbound SSH.

## AWS-CO-013 — EBS

Fault variants:

- AZ mismatch,
- stale attachment,
- KMS permission,
- filesystem not mounted/full,
- throughput/IOPS or instance bandwidth.

Validation musí overiť block device aj filesystem/application layer.

## AWS-CO-014 — RDS timeout

Path:

```text
endpoint DNS
→ route
→ client SG
→ DB SG
→ NACL
→ RDS state/listener
→ auth/TLS/connections
```

Nemeň `PubliclyAccessible=true` ako univerzálnu opravu.

## AWS-CO-015 — Backup/restore

Fault variants:

- selection tags,
- vault policy,
- IAM/KMS,
- cross-account copy,
- restore subnet/parameter/security config.

Validation:

- restore do izolovaného targetu,
- data integrity,
- actual RTA/RPA.

## AWS-CO-016 — Route 53 failover

Fault variants:

- health-check target,
- record identifiers,
- secondary unhealthy,
- TTL/cache,
- hosted-zone scope.

Over authoritative DNS aj end-to-end request.

## AWS-CO-017 — CloudFront

Fault variants:

- OAC/bucket policy,
- certificate/domain,
- cache behavior/path,
- WAF,
- cached error.

Validation:

- origin access je private podľa designu,
- správny object/status cez distribution.

## AWS-CO-018 — Lambda VPC timeout

Fault variants:

- no NAT/endpoint,
- SG/DNS,
- dependency latency,
- memory/CPU,
- concurrency throttling.

Rozlišuj timeout, throttle a initialization failure.

## AWS-CO-019 — ECS task

Evidence:

- service events,
- task stopped reason,
- execution-role vs task-role permissions,
- image pull/log configuration,
- placement resources.

## AWS-CO-020 — EKS workload identity

Fault variants:

- OIDC trust condition,
- ServiceAccount mapping,
- Pod identity/IRSA mismatch,
- STS network path,
- SDK credential chain.

Node role broadening je zakázaná shortcut oprava.

## AWS-CO-021 — CloudFormation

Evidence:

```bash
aws cloudformation describe-stack-events --stack-name <name>
```

Fault variants:

- immutable property,
- custom resource timeout,
- IAM/PassRole,
- quota,
- retained dependency.

## AWS-CO-022 — NAT spike

Evidence:

- NAT metrics,
- Flow Logs,
- destination concentration,
- cross-AZ routes,
- AWS service traffic,
- application connection churn.

Remediation vyber podľa root cause, nie iba zväčšením infra.

## AWS-CO-023 — Region mismatch

Baseline:

```bash
aws configure get region
aws sts get-caller-identity
```

Fault môže vyzerať ako missing AMI, metric, KMS key, secret alebo certificate.

## AWS-CO-024 — Quota vs capacity

Rozlišuj:

- Service Quotas limit,
- API throttling,
- AZ capacity shortage,
- subnet IP exhaustion,
- unsupported instance/service,
- SCP/Region disablement.

Quota increase nevyrieši všetky capacity failures.

## Review template

```text
Drill ID:
Dátum:
Account/Region:
Symptóm:
Scope:
Control/data plane:
Evidence:
Root cause:
Oprava:
Pozitívna validation:
Negatívna validation:
Diagnosis/repair/verify čas:
Cost/cleanup:
SOA-C03 domain:
Čo zopakovať:
```

## Reset requirements

Každý scenár musí mať:

- IaC destroy alebo explicitný cleanup,
- obnovenie pôvodnej policy/route/rule,
- odstránenie NAT/EIP/LB/RDS a iných hourly resources,
- kontrolu orphan ENIs/snapshots/log groups,
- billing review nasledujúci deň pri cost-sensitive laboch.
