# AWS CloudOps hands-on labs

Praktická oblasť pre AWS Certified CloudOps Engineer – Associate (SOA-C03). Laby sú originálne operations scenáre; nereprodukujú exam questions. Každý set sa vykonáva v samostatnom sandbox account-e alebo explicitne izolovanom training prostredí.

Autoritatívny kontext:

- [SOA-C03 guide](../../docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md)
- [CloudOps hands-on labs](../../docs/11-cloud-and-aws/cloudops-hands-on-labs.md)
- [CloudOps troubleshooting drills](../../docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md)

## Safety baseline

Pred každým labom:

```text
[ ] správny sandbox account a Region
[ ] aws sts get-caller-identity overený
[ ] budget/alarm aktívny
[ ] žiadne production data alebo credentials
[ ] tags Owner/Purpose/ExpiresAt
[ ] cleanup command alebo IaC destroy pripravený
[ ] service quotas a očakávaný cost skontrolované
```

NAT Gateways, load balancers, RDS, EKS, public IPv4, data transfer a dlhodobé logs môžu vytvárať cost aj bez aktívneho trafficu.

## Spoločný execution protocol

```text
1. Spusti timer.
2. Zapíš account, Region a expected outcome.
3. Nasadzuj cez CLI alebo IaC, nie iba klikmi bez záznamu.
4. Zachovaj baseline output a telemetry.
5. Aplikuj presne definovaný fault.
6. Diagnostikuj a oprav bez resetu.
7. Over pozitívny aj negatívny path.
8. Vykonaj cleanup.
9. Skontroluj orphan resources a billing dashboard.
10. Zapíš výsledok do review logu.
```

## Scoring

| Oblasť | Body |
|---|---:|
| Funkčný expected outcome | 35 |
| Security/least privilege | 15 |
| Monitoring a audit evidence | 15 |
| Root-cause diagnosis/remediation | 20 |
| Cost a cleanup | 10 |
| Reprodukovateľnosť a dokumentácia | 5 |

## Lab A — Identity and networking foundation — 75 minút

### A1 — Cross-account operations role — 20 bodov

- source principal assume-ne target role,
- target role povoľuje iba read operations nad vybraným S3 prefixom,
- CloudTrail zachytí role session,
- delete action zostane denied.

Fault variant: trust policy principal alebo external condition je chybná.

### A2 — Two-AZ VPC — 25 bodov

- VPC s public/private subnetom v dvoch AZ,
- explicitné route tables,
- AZ-local NAT Gateways,
- Flow Logs,
- private instances bez public IP.

Fault variant: private subnet AZ-b smeruje na NAT AZ-a alebo chýba return NACL rule.

### A3 — Session Manager — 15 bodov

- access bez inbound SSH,
- správna instance profile role,
- agent a HTTPS/VPC endpoint path.

Fault variant: chýba endpoint alebo IAM permission.

### A4 — Cleanup — 15 bodov

- odstránené NAT Gateways, EIPs, endpoints, ENIs a logs podľa retention contractu,
- nulové orphan hourly resources.

## Lab B — Monitoring and remediation — 90 minút

### B1 — Custom metric and alarm — 15 bodov

- publikuj metric,
- vytvor alarm so správnymi dimensions/statistic/period,
- over `OK → ALARM → OK`.

### B2 — Event-driven remediation — 25 bodov

- alarm alebo EventBridge rule,
- Systems Manager Automation alebo Lambda,
- least-privilege execution role,
- idempotentná remediation,
- notification.

Fault variant: target role alebo event pattern nesedí.

### B3 — Central log query — 20 bodov

- CloudWatch Logs group s explicitnou retention,
- Logs Insights query pre failure pattern,
- metric filter alebo alarm.

### B4 — Performance diagnosis — 20 bodov

- identifikuj CPU, memory, EBS, network alebo dependency bottleneck,
- zvoľ remediation podľa evidence,
- neaplikuj blind vertical scaling.

### B5 — Cleanup/review — 10 bodov

## Lab C — Availability and recovery — 120 minút

### C1 — ALB and Auto Scaling — 25 bodov

- launch template,
- ASG cez dve AZ,
- ALB/target group,
- health checks,
- scaling policy.

Fault variant: wrong target port alebo bootstrap failure.

### C2 — Backup and restore — 25 bodov

- snapshot/backup plan,
- encryption,
- restore do izolovaného targetu,
- integrity test,
- actual RTA/RPA.

### C3 — Route 53 failover — 20 bodov

- primary/secondary records,
- health model,
- TTL/cache observation,
- controlled failover a failback.

### C4 — Failure review — 15 bodov

- rozlíš Multi-AZ HA od DR,
- zdokumentuj authoritative state a recovery dependencies.

### C5 — Cleanup/cost — 15 bodov

## Lab D — Deployment and automation — 120 minút

### D1 — CloudFormation stack lifecycle — 25 bodov

- create,
- change set,
- update,
- intentional failure,
- rollback,
- drift detection.

### D2 — Image or container pipeline — 20 bodov

- versionovaný AMI alebo container image,
- vulnerability/test gate,
- immutable deployment.

### D3 — Systems Manager fleet operations — 20 bodov

- Inventory,
- Run Command,
- Patch Manager/State Manager,
- maintenance window alebo Automation.

### D4 — Multi-account deployment — 20 bodov

- StackSets alebo iný controlled organization deployment,
- delegated/least-privilege execution,
- failure/rollback evidence.

### D5 — Cleanup/review — 15 bodov

## Lab E — Security and compliance — 90 minút

### E1 — IAM policy evaluation — 20 bodov

- identity allow,
- permissions boundary,
- explicit SCP deny,
- resource/KMS policy,
- vysvetli effective result.

### E2 — Central audit — 20 bodov

- CloudTrail a Config evidence,
- encrypted log archive,
- alert na root alebo IAM policy change.

### E3 — Secret and encryption workflow — 20 bodov

- KMS key policy,
- Secrets Manager secret,
- workload role,
- rotation alebo controlled update,
- CloudTrail audit.

### E4 — Ransomware recovery control — 20 bodov

- isolated backup copy,
- protected deletion/access,
- restore test,
- incident role.

### E5 — Cleanup/review — 10 bodov

## Lab F — Networking and content delivery — 105 minút

### F1 — SG/NACL path — 20 bodov

- povolený app path,
- blokovaný neautorizovaný path,
- Flow Logs evidence,
- stateless return rule.

### F2 — Private AWS API access — 20 bodov

- gateway/interface endpoint,
- private DNS,
- endpoint policy/SG,
- bez NAT dependency podľa scenára.

### F3 — Route 53/Resolver — 20 bodov

- private hosted zone alebo hybrid Resolver path,
- query logging,
- fault v rule/association.

### F4 — CloudFront or load-balancer path — 25 bodov

- origin security,
- certificate/domain,
- caching behavior,
- access/error logs.

### F5 — Cleanup/review — 20 bodov

## Full simulation — 180 minút

Použi približne doménové váhy SOA-C03:

- Monitoring/analysis/remediation/performance — 22 bodov,
- Reliability/business continuity — 22 bodov,
- Deployment/provisioning/automation — 22 bodov,
- Security/compliance — 16 bodov,
- Networking/content delivery — 18 bodov.

Zostav 8–12 úloh z Lab A–F a minimálne tri fault-injection scenáre z troubleshooting indexu.

## Hard validation checklist

```text
[ ] caller/account/Region správny
[ ] expected API/resource state
[ ] end-to-end data path
[ ] least-privilege positive aj negative test
[ ] metrics/logs/audit evidence
[ ] failover alebo restore výsledok podľa scenára
[ ] no broad public exposure
[ ] resources tagged
[ ] cleanup dokončený
[ ] orphan ENI/EIP/NAT/LB/RDS/snapshot/log group skontrolovaný
[ ] cost po lab-e skontrolovaný
```

## Review log

```text
Dátum:
Lab/set:
Account/Region:
Čas:
Skóre:
SOA-C03 domains:
Knowledge gaps:
Operational mistakes:
Security mistakes:
Cost/cleanup residue:
Najpomalšia vrstva:
Nasledujúce 3 drilly:
```
