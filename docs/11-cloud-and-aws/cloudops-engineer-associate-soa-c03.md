# AWS Certified CloudOps Engineer – Associate (SOA-C03)

AWS Certified CloudOps Engineer – Associate je associate-level certifikácia pre deployment, management a operations workloads na AWS. Od 30. septembra 2025 nahradila názov AWS Certified SysOps Administrator – Associate pre novú exam verziu SOA-C03. Certifikačný track v tomto repozitári nenahrádza hlavné AWS kapitoly; mapuje ich na aktuálne exam domains a dopĺňa timed reasoning, hands-on operations a troubleshooting drilly.

## 1. Aktuálny exam contract

Podľa oficiálnych AWS zdrojov:

- exam code: `SOA-C03`,
- level: Associate,
- duration: 130 minút,
- format: 65 multiple-choice alebo multiple-response questions,
- intended experience: približne jeden rok deploymentu, managementu a operations AWS workloads,
- aktuálny exam-guide revision: 1.1, publikovaný 1. júna 2026.

Skúška nie je performance-based hands-on exam ako CKA. Praktické laby v tomto repozitári slúžia na vytvorenie reálneho operations porozumenia, ktoré je potrebné na správne vyhodnotenie scenario questions.

## 2. Exam domains a váhy

| Doména | Váha |
|---|---:|
| Monitoring, Logging, Analysis, Remediation, and Performance Optimization | 22 % |
| Reliability and Business Continuity | 22 % |
| Deployment, Provisioning, and Automation | 22 % |
| Security and Compliance | 16 % |
| Networking and Content Delivery | 18 % |

Tri najväčšie domény majú rovnakú váhu. Príprava nesmie byť redukovaná iba na CloudWatch alebo networking.

## 3. Čo SOA-C03 overuje

Kandidát má vedieť:

- podporovať a udržiavať AWS workloads podľa Well-Architected princípov,
- používať AWS Management Console a AWS CLI,
- implementovať security a compliance controls,
- monitorovať, logovať a troubleshootovať systémy,
- aplikovať DNS, TCP/IP, routing a firewall concepts,
- implementovať availability, performance a capacity requirements,
- vykonávať business continuity a DR procedures,
- automatizovať provisioning a remediation,
- analyzovať cost a total cost of ownership,
- pracovať s multi-account, multi-Region a containerized workloads.

## 4. Rozdiel oproti starému SOA-C02

SOA-C03 rozširuje dôraz najmä na:

- containers,
- multi-account architectures,
- multi-Region operations,
- automation a Infrastructure as Code,
- moderné monitoring a governance services,
- ransomware defense a broader security operations,
- cost, capacity a performance optimization.

Staré SysOps materials sú použiteľné iba po kontrole proti aktuálnemu SOA-C03 guide-u.

## 5. Domain 1 — Monitoring, Logging, Analysis, Remediation and Performance Optimization

### Potrebné schopnosti

- konfigurácia monitoring/logging pre compute, serverless, containers a managed services,
- CloudWatch metrics, logs, alarms, dashboards a anomaly detection,
- CloudTrail, AWS Config a service logs,
- centralizácia telemetry medzi accounts/Regions,
- performance analysis,
- automated remediation cez EventBridge, Lambda a Systems Manager,
- cost/capacity/performance optimization,
- incident evidence a root-cause narrowing.

### Hlavné kapitoly repozitára

- CloudWatch a CloudTrail,
- Systems Manager,
- EC2 a Auto Scaling,
- ECS a EKS,
- Lambda,
- Cost management a FinOps,
- Observability sekcia,
- SRE and Operations sekcia.

## 6. Domain 2 — Reliability and Business Continuity

### Potrebné schopnosti

- scalability a elasticity,
- Multi-AZ a multi-Region resilience,
- health checks, load balancing a failover,
- backup policies a restore,
- RPO/RTO,
- AWS Backup,
- storage/database recovery,
- DR strategy selection a testing.

### Hlavné kapitoly repozitára

- Regions a Availability Zones,
- Scalability, elasticity a fault tolerance,
- High availability a disaster recovery,
- EC2 a Auto Scaling,
- Elastic Load Balancing,
- S3, EBS a EFS,
- RDS,
- Route 53 a CloudFront,
- AWS Backup.

## 7. Domain 3 — Deployment, Provisioning and Automation

### Potrebné schopnosti

- provisioning a maintenance cloud resources,
- AMIs a container images,
- CloudFormation a Infrastructure as Code concepts,
- Systems Manager automation,
- patching a configuration management,
- deployment failure remediation,
- scheduled/event-driven operations,
- repeatable multi-account operations,
- CLI/API automation.

### Hlavné kapitoly repozitára

- Infrastructure as Code section,
- EC2 a Auto Scaling,
- ECS a EKS,
- Lambda,
- Systems Manager,
- IAM,
- AWS Organizations a accounts.

SOA-C03 môže používať CloudFormation-specific scenarios aj keď hlavný IaC track používa Terraform. Treba rozumieť CloudFormation stack lifecycle, change sets, drift, rollback a StackSets.

## 8. Domain 4 — Security and Compliance

### Potrebné schopnosti

- IAM policy evaluation,
- federation, roles a temporary credentials,
- SCPs a multi-account guardrails,
- KMS, Secrets Manager a encryption,
- CloudTrail/Config/Security Hub/GuardDuty concepts podľa scope-u,
- patching a vulnerability response,
- data protection a ransomware defense,
- compliance evidence,
- least privilege a incident containment.

### Hlavné kapitoly repozitára

- Shared responsibility model,
- AWS Organizations a accounts,
- IAM,
- Security Groups a Network ACLs,
- KMS a Secrets Manager,
- CloudWatch a CloudTrail,
- Systems Manager,
- Security and Identity section.

## 9. Domain 5 — Networking and Content Delivery

### Potrebné schopnosti

- VPC, subnet a route-table design,
- internet/NAT/private endpoint connectivity,
- Security Groups a NACLs,
- DNS a Route 53,
- load balancers a content delivery,
- hybrid connectivity,
- VPC Flow Logs a network troubleshooting,
- multi-account/multi-Region connectivity.

### Hlavné kapitoly repozitára

- VPC, subnets a route tables,
- Internet Gateway a NAT Gateway,
- Security Groups a Network ACLs,
- Elastic Load Balancing,
- Route 53 a CloudFront,
- Public, private a hybrid cloud.

## 10. In-scope service model

Oficiálny guide obsahuje široký zoznam in-scope services. Cieľom nie je memorovať každý názov rovnako hlboko.

Rozdeľ services na:

1. **Core operations** — musíš vedieť configure, monitor, troubleshoot a recover.
2. **Supporting integration** — musíš vedieť, prečo a kde sa používa.
3. **Recognition level** — musíš vedieť odlíšiť vhodnú službu od distractorov.

Core set typicky zahŕňa IAM, Organizations, EC2, Auto Scaling, ELB, VPC, Route 53, S3/EBS/EFS, RDS, CloudWatch, CloudTrail, Config, Systems Manager, CloudFormation, Backup, KMS a Secrets Manager. Containers a serverless sú v SOA-C03 relevantné tiež.

## 11. Scenario-question model

Pri každej otázke identifikuj:

```text
požadovaný outcome
+ explicitné constraints
+ failure/operations boundary
+ managed capability
+ security/cost/availability trade-off
```

Potom eliminuj odpovede, ktoré:

- neriešia všetky constraints,
- vyžadujú neprimeraný manual toil,
- porušujú least privilege,
- nemajú HA alebo restore model,
- používajú nesprávny scope služby,
- riešia symptom, nie root cause,
- pridávajú zbytočnú custom infra oproti managed capability.

## 12. Multiple-response otázky

Pri multiple-response:

- vyhodnoť každú možnosť samostatne,
- nehľadaj iba jednu „najlepšiu“ odpoveď,
- over, či kombinácia tvorí kompletný path,
- dávaj pozor na dependency pairs, napríklad route + gateway alebo alarm + remediation target,
- nevyberaj redundantnú možnosť, ktorá nepridáva požadovanú capability.

## 13. Časový model

130 minút / 65 otázok je priemer 2 minúty na otázku.

Odporúčaný tréning:

```text
pass 1: jasné otázky, približne 60–75 sekúnd
pass 2: stredne ťažké scenarios
pass 3: označené otázky a consistency review
```

Neinvestuj 5 minút do jednej otázky na začiatku.

## 14. Praktický track v repozitári

- [CloudOps domain review a timed reasoning](cloudops-domain-review-timed-reasoning.md)
- [CloudOps hands-on labs](cloudops-hands-on-labs.md)
- [CloudOps troubleshooting drills](cloudops-troubleshooting-drills.md)
- [Praktické AWS CloudOps laby](../../labs/aws-cloudops/README.md)
- [AWS CloudOps troubleshooting scenáre](../../troubleshooting/aws-cloudops/README.md)

## 15. Študijné fázy

### Fáza A — Foundation

Dokonči cloud fundamentals, Organizations, IAM a VPC.

### Fáza B — Core services

Dokonči compute, load balancing, storage, database, DNS/CDN, serverless, containers, observability, Systems Manager, KMS/secrets a Backup.

### Fáza C — Domain review

Mapuj každú task statement na:

- service,
- control plane,
- data plane,
- failure evidence,
- remediation,
- security/cost trade-off.

### Fáza D — Labs a troubleshooting

Vykonávaj scenáre bez krokového návodu a meraj diagnosis/repair/validation čas.

### Fáza E — Exam simulations

Použi 65-question/130-minute timed sets a analyzuj chyby podľa domain a reasoning failure typu.

## 16. Readiness criteria

Pred skúškou má byť možné:

- konzistentne dosahovať cieľové skóre na kvalitných practice sets,
- dokončiť 130-minútovú simuláciu bez time collapse,
- vysvetliť, prečo sú distractors nesprávne,
- prakticky nakonfigurovať core operations paths,
- diagnostikovať AccessDenied, no-route, alarm, unhealthy target, failed backup a deployment rollback scenarios,
- rozlíšiť customer a AWS responsibility,
- pracovať s CLI bez závislosti na console-only pamäti.

## 17. Review log

```text
Dátum:
Zdroj/set:
Skóre:
Čas:
Domain 1:
Domain 2:
Domain 3:
Domain 4:
Domain 5:
Chyby znalosti:
Chyby čítania constraints:
Chyby service selection:
Chyby policy/network reasoning:
Nasledujúce laby/drilly:
```

## 18. Anti-patterny

### Memorovanie service descriptions

Skúška používa operational scenarios a trade-offs.

### Iba video kurz bez labov

Vytvára recognition bez schopnosti diagnostiky.

### Starý SOA-C02 blueprint ako autorita

SOA-C03 má rozšírený scope.

### Ignorovanie cost a automation

Sú súčasťou role aj exam guide-u.

### Učenie odpovedí z dumps

Neoveruje schopnosť a porušuje exam integrity.

## 19. Glossary impact

Relevantné pojmy: AWS Certified CloudOps Engineer – Associate, SOA-C03, exam domain, scored content weighting, timed reasoning, scenario-question model, distractor elimination, domain gap map, exam readiness a CloudOps lab.

## Oficiálne zdroje

- [AWS Certified CloudOps Engineer – Associate](https://aws.amazon.com/certification/certified-cloudops-engineer-associate/)
- [SOA-C03 exam guide](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03.html)
- [SOA-C03 revisions](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/soa-03-revisions.html)
- [In-scope AWS services](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/soa-03-in-scope-services.html)
