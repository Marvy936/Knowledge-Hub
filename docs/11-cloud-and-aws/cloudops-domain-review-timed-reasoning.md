# CloudOps domain review a timed reasoning

Táto kapitola trénuje spôsob uvažovania pre AWS Certified CloudOps Engineer – Associate (SOA-C03). Skúška je scenario-based multiple-choice/multiple-response test, preto nestačí poznať definície služieb. Potrebné je rýchlo identifikovať operational goal, constraints, failure boundary a najvhodnejšiu managed capability.

## 1. Vstupný protokol otázky

Pri každej otázke si v prvých sekundách urč:

```text
1. Čo je požadovaný outcome?
2. Je problém monitoring, reliability, deployment, security alebo networking?
3. Aký je scope: resource, AZ, Region, account alebo organization?
4. Ktorá vrstva je customer-managed a ktorá AWS-managed?
5. Aké constraints sú explicitné: least effort, lowest cost, no downtime, RPO/RTO, automatic remediation?
6. Je otázka create/configure, troubleshoot, optimize alebo recover?
```

## 2. Constraint words

Slová, ktoré zásadne menia správnu odpoveď:

- **MOST operationally efficient**,
- **LEAST administrative overhead**,
- **MOST cost-effective**,
- **without downtime**,
- **automatically**,
- **near real time**,
- **cross-account**,
- **multi-Region**,
- **private connectivity**,
- **least privilege**,
- **meet RPO/RTO**,
- **retain evidence**.

Odpoveď môže byť technicky funkčná, ale nesprávna podľa constraintu.

## 3. Scope matrix

Pred výberom služby urč scope:

| Scope | Typické otázky |
|---|---|
| Resource | alarm, SG, volume, instance profile |
| Availability Zone | subnet, NAT Gateway, zonal failure |
| Region | VPC, regional service, cross-AZ HA |
| Account | IAM, quota, billing, CloudTrail trail |
| Organization | SCP, delegated admin, central logging |
| Global/multi-Region | Route 53, replication, DR, global identity |

Nesprávny scope je častý distractor.

## 4. Control plane vs data plane

- **Control plane failure**: API call, configuration update, policy, provisioning alebo service management nefunguje.
- **Data plane failure**: workload traffic, request processing, storage I/O alebo DNS path nefunguje.

Príklad:

```text
EC2 instance beží, ale ModifyInstanceAttribute API zlyhá
→ control plane/IAM/API issue

API calls fungujú, ale HTTPS na instance timeoutuje
→ data plane/routing/security/listener issue
```

## 5. Domain 1 reasoning

### Monitoring source selection

- CloudWatch metrics: numeric operational signals.
- CloudWatch Logs: log ingestion, query, subscription a retention.
- CloudTrail: AWS API activity/audit.
- AWS Config: resource configuration history a compliance.
- VPC Flow Logs: network flow metadata.
- service-specific logs: ALB, Route 53 Resolver, RDS, CloudFront a ďalšie.

Otázka „kto zmenil Security Group?“ smeruje na CloudTrail, nie na Flow Logs.

### Alarm vs event

- Alarm vyhodnocuje metric/alarm state.
- EventBridge reaguje na events/patterns a môže spustiť automation.
- Logs metric filter vytvorí metric z log patternu.

### Automated remediation

Typický chain:

```text
signal/event
→ EventBridge alebo CloudWatch alarm
→ Systems Manager Automation / Lambda / Step Functions
→ remediation
→ validation a notification
```

Vyber najmenší vhodný managed mechanismus.

### Performance optimization

Najprv identifikuj bottleneck:

- CPU,
- memory,
- storage throughput/IOPS,
- network,
- database connections,
- queue depth,
- latency dependency,
- throttling/quota.

Zväčšenie EC2 instance nevyrieši NAT port exhaustion alebo RDS connection limit.

## 6. Domain 2 reasoning

### Availability vs durability

- Availability: služba je teraz použiteľná.
- Durability: dáta prežijú definovaný failure model.

Multi-AZ môže zlepšiť availability, ale neochráni pred logical deletion bez backupu.

### Backup vs replication

Replication môže okamžite preniesť corruption alebo deletion. Backup poskytuje time-separated recovery point podľa retention a restore contractu.

### RPO/RTO selection

- Nízkemu RPO vyhovuje častejšia alebo continuous replication/log shipping.
- Nízkemu RTO vyhovuje pripravená capacity a automation.
- Backup-and-restore je lacnejší, ale pomalší.
- Active-active je rýchly, ale komplexný a drahý.

### Scaling

- Scheduled: známy časový pattern.
- Target tracking: udržiavanie metric targetu.
- Step scaling: rozdielne kroky podľa severity.
- Queue depth/backlog: asynchronous workers.

CPU nie je správny signal pre každý workload.

## 7. Domain 3 reasoning

### IaC lifecycle

Pri CloudFormation scenario rozlišuj:

- template validation,
- change set,
- stack update,
- rollback,
- drift detection,
- nested stacks,
- StackSets pre multi-account/Region.

### Systems Manager selection

- Run Command: spustenie commands bez inbound SSH.
- Automation: multi-step operational workflow.
- Patch Manager: patch baselines a patch operations.
- State Manager: desired instance configuration.
- Inventory: software/config metadata.
- Session Manager: audited shell/tunnel access bez inbound management portu.

### AMI a image pipeline

Pre repeatable fleet preferuj versioned image pipeline, test a replacement pred in-place snowflake patchingom.

### Failed deployment

Over:

```text
artifact/image
→ permissions
→ bootstrap/user data
→ network/endpoints
→ health checks
→ capacity/quota
→ rollback state
```

## 8. Domain 4 reasoning

### IAM evaluation

Pri `AccessDenied` hľadaj:

- caller identity,
- action/resource,
- explicit deny,
- identity/resource allow,
- boundary/session/SCP/RCP,
- trust/PassRole,
- KMS key policy,
- conditions/tags.

### Encryption service selection

- KMS: key management a cryptographic authorization.
- Secrets Manager: secret storage, retrieval a rotation workflow.
- Systems Manager Parameter Store: configuration/secrets podľa tier a feature requirements.
- ACM: managed certificates pre podporované integrations.

### Compliance evidence

- CloudTrail: API activity.
- Config: configuration state/history/rules.
- Security Hub: aggregated security findings/posture.
- GuardDuty: threat detection.
- Inspector: vulnerability/exposure findings podľa podporovaných workloads.

### Ransomware defense

Hľadaj kombináciu:

- least privilege,
- immutable/isolated backups,
- MFA a protected deletion,
- cross-account backup/log archive,
- detection,
- restore testing,
- incident roles.

## 9. Domain 5 reasoning

### Public internet path

```text
public IP/EIP
+ subnet route to IGW
+ SG/NACL
+ listener
```

### Private outbound path

```text
private subnet route
→ NAT Gateway alebo egress proxy/firewall
→ public subnet/IGW
```

Pre AWS service traffic môže byť správnejší VPC endpoint.

### Security Group vs NACL

- SG: stateful, ENI/resource, allow only.
- NACL: stateless, subnet, ordered allow/deny.

### DNS

Rozlišuj:

- public hosted zone,
- private hosted zone,
- Route 53 Resolver inbound/outbound endpoints,
- health checks a routing policies,
- TTL a cache,
- alias record.

### Load balancing

- ALB: HTTP/HTTPS L7 routing.
- NLB: TCP/UDP/TLS L4, high performance/static IP requirements podľa designu.
- GWLB: transparent network appliance insertion.

## 10. Eliminácia distractorov

Odstráň odpoveď, keď:

- používa nesprávny scope,
- zvyšuje manual operations bez dôvodu,
- porušuje explicitný security constraint,
- nepokrýva return path alebo druhú policy boundary,
- ponúka HA, keď otázka vyžaduje backup/DR,
- používa monitoring service na audit alebo opačne,
- vyžaduje custom fleet, keď existuje presná managed capability,
- rieši len polovicu multiple-response chainu.

## 11. Dvojice, ktoré sa často zamieňajú

| Pojem A | Pojem B | Rozdiel |
|---|---|---|
| CloudTrail | CloudWatch | API audit vs operational telemetry |
| Config | CloudTrail | resource state/compliance vs API events |
| SG | NACL | stateful ENI allow-list vs stateless subnet ACL |
| IAM policy | SCP | grant vs maximum permissions guardrail |
| NAT Gateway | IGW | private outbound translation vs internet route target |
| Multi-AZ | Multi-Region | zonal HA vs region-level recovery/distribution |
| Backup | Replication | historical recovery vs current-state copy |
| Run Command | Session Manager | remote command execution vs interactive access |
| Target tracking | Step scaling | target metric vs threshold-based increments |
| ALB | NLB | L7 HTTP routing vs L4 transport load balancing |

## 12. Timed sets

### Set A — 20 otázok / 35 minút

Domain-balanced fundamentals.

### Set B — 35 otázok / 65 minút

Scenario questions s minimálne 25 % multiple-response.

### Set C — 65 otázok / 130 minút

Plná simulácia podľa váh 22/22/22/16/18.

### Review phase

Po sete kategorizuj každú chybu:

- knowledge gap,
- missed constraint,
- wrong scope,
- wrong policy evaluation,
- wrong network path,
- availability/DR confusion,
- cost/operations trade-off,
- changed answer without evidence.

## 13. Confidence marking

Pri tréningu označ:

- `H` — high confidence,
- `M` — medium,
- `L` — low/guess.

Analýza:

- wrong + H = chybný mentálny model,
- correct + L = slabé alebo náhodné porozumenie,
- wrong + L = očakávaný knowledge gap,
- correct + H = stabilná schopnosť.

## 14. Question review template

```text
Question ID:
Domain:
Outcome:
Constraints:
Correct answer:
Prečo je správna:
Prečo sú ostatné nesprávne:
Moja chyba:
Autoritatívna kapitola:
Lab/drill:
```

## 15. Anti-patterny

### Hľadanie service keywordu bez čítania outcome-u

Jedna služba môže byť v otázke distractor aj správna vrstva.

### Vyberanie najkomplexnejšej architektúry

Skúška často preferuje najjednoduchšiu managed možnosť spĺňajúcu všetky requirements.

### Menenie odpovede bez nového dôvodu

Review má byť založený na constraint alebo technical correction, nie na neistote.

### Ignorovanie negatívnych požiadaviek

„Without public internet“, „without downtime“ alebo „least operational effort“ mení celé riešenie.

## 16. Glossary impact

Relevantné pojmy: CloudOps timed reasoning, question constraint, scope matrix, control-plane failure, data-plane failure, distractor elimination, confidence marking, knowledge gap, wrong-scope error, multiple-response chain a domain-weighted simulation.

## Oficiálne zdroje

- [SOA-C03 content outline](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03.html)
- [Domain 1](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain1.html)
- [Domain 2](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain2.html)
- [Domain 3](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain3.html)
- [Domain 4](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain4.html)
- [Domain 5](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain5.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: AWS Certified CloudOps Engineer – Associate (SOA-C03)](cloudops-engineer-associate-soa-c03.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CloudOps hands-on labs →](cloudops-hands-on-labs.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
