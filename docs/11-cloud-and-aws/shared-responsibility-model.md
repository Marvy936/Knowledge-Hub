# Shared responsibility model

AWS Shared Responsibility Model nie je statický obrázok s dvoma stĺpcami. Je to service-specific control-ownership protocol, ktorý musí určiť:

```text
required business/security/recovery outcome
→ konkrétny service a configuration subject
→ provider, customer a shared control inventory
→ evidence a observation owner
→ incident, recovery a support boundary
→ closure verdict
```

Základná formulácia zostáva:

```text
AWS zodpovedá za security OF the cloud.
Zákazník zodpovedá za security IN the cloud.
```

Je to východisko, nie kompletný runbook. Responsibility sa mení podľa služby, feature-u, configuration, integration, Regionu, identity a regulačného contractu.

## 1. Exact responsibility subject

Pre Atlas Payments:

```text
capability: CAP-PAY-42
AWS account: A42
Region: eu-central-1
application release: I42/C42/SE10
compute: managed runtime MR42
managed database: DB42
KMS key: K42
network: VPC42, SG42, endpoints EP42
backup policy: BP7
identity: workload role WR42
business outcome: payment authorization a settlement presne raz
```

Responsibility verdict bez service/resource/configuration identity je príliš všeobecný. „AWS spravuje databázu“ nehovorí, kto spravuje DB users, schema, KMS policy, network exposure, backup retention, restore test alebo application consistency.

## 2. Dominantný lifecycle kontroly

```text
control objective
→ applicability a owner assignment
→ provider capability a customer configuration
→ deployment a effective state
→ evidence emission a retention
→ control operation a alerting
→ incident ownership a escalation
→ remediation/recovery
→ original aj forbidden outcome verification
→ periodic revalidation
```

Každý kritický control potrebuje:

- ownera;
- authoritative configuration source;
- effective-state observation;
- evidence location a retention;
- failure mode;
- escalation boundary;
- recovery procedure;
- test frequency.

## 3. Security of the cloud

AWS typicky vlastní:

- physical facilities a physical security;
- hardware, storage devices a physical network;
- host operating systems a virtualization layer;
- foundational global infrastructure;
- provider service control planes a managed runtime podľa service contractu;
- facility resilience a hardware lifecycle;
- provider-level audits a certifications.

Zákazník nemôže patchovať AWS hypervisor ani vstupovať do dátového centra. Preto tieto controls overuje cez AWS service commitments, compliance evidence, service health, support a publikovanú dokumentáciu.

### Provider boundary neznamená provider business ownership

AWS môže vymeniť failed host alebo replikovať managed database storage. Nevie však rozhodnúť:

- ktoré transakcie sú business-valid;
- či zákaznícky IAM role smie mazať dáta;
- či retention spĺňa Atlas RPO;
- či rollback binary rozumie novej schema;
- či payment bol zúčtovaný presne raz.

## 4. Security in the cloud

Zákazník typicky vlastní:

- accounts, Organizations a Region governance;
- identities, credentials, federation a authorization;
- data classification, retention a legal obligations;
- resource configuration;
- VPC, routes, SG, NACL, endpoints a application TLS;
- workload OS pri IaaS;
- code, dependencies a supply chain;
- KMS key policies a encryption choices;
- logging enablement, centralization, detection a incident response;
- backup, restore, DR a business continuity;
- application a business acceptance.

Ak zákazník môže resource alebo policy konfigurovať, typicky vlastní bezpečnosť tejto konfigurácie.

## 5. Shared control nie je nejasné vlastníctvo

„Shared“ znamená, že provider dodáva capability a zákazník ju musí správne aktivovať, nakonfigurovať a používať.

Príklady:

```text
AWS poskytne IAM/STS
→ zákazník definuje principals, trust a permissions

AWS poskytne encryption capability
→ zákazník zvolí key, policy, context a rotation

AWS poskytne Multi-AZ feature
→ zákazník ju zvolí, navrhne clients a overí failover

AWS emituje CloudTrail/service logs
→ zákazník zapne coverage, retention, detection a response
```

Shared control musí mať explicitné rozhranie. Inak každý tím predpokladá, že druhá strana vykonáva chýbajúcu časť.

## 6. Service-specific responsibility matrix

### EC2

AWS:

- facilities, hardware, host OS, hypervisor;
- EC2 control plane;
- physical network a základnú instance isolation.

Atlas:

- AMI/image provenance;
- guest OS, patches a reboot;
- packages, agents a runtime;
- application a data;
- IAM instance role;
- SG a routes;
- EBS encryption choice a backup;
- fleet HA, scale a recovery.

### Managed relational database

AWS:

- host a engine-platform operation podľa služby;
- infrastructure replacement;
- service patch mechanism;
- replication/backup capability podľa configured mode.

Atlas:

- engine version a maintenance choice podľa exposed controls;
- users, roles a authentication;
- schema, queries a migrations;
- network exposure;
- KMS/key policy;
- parameter configuration;
- retention, point-in-time recovery a restore test;
- application consistency a failover compatibility.

### Serverless/managed runtime

AWS:

- runtime infrastructure a platform scaling mechanism;
- host patching a replacement;
- service control plane.

Atlas:

- code a dependencies;
- execution role a event-source policy;
- input validation;
- concurrency, retries a idempotency;
- secrets a outbound access;
- logging, cost a business continuity.

### SaaS

Provider spravuje application implementation. Atlas stále vlastní:

- tenant identities a admins;
- federation a MFA policy;
- sharing a data classification;
- integrations a API credentials;
- endpoint security;
- retention/export/deletion;
- business process a fallback.

## 7. Control inheritance

Atlas môže zdediť provider controls:

- physical security;
- environmental controls;
- hardware disposal;
- hypervisor patching;
- provider certifications.

Inheritance lifecycle:

```text
control requirement
→ provider control mapping
→ service/Region eligibility
→ provider evidence
→ Atlas configuration a complementary controls
→ workload evidence
→ audit verdict
```

Provider certification necertifikuje automaticky Atlas workload. Zákazník musí overiť applicability, service scope, Region, configuration, data handling, identities, processes a vlastnú evidence.

## 8. Identity responsibility

AWS poskytuje IAM, STS, Organizations a federation capabilities. Atlas určuje:

- principal identity;
- authentication source;
- trust relationship;
- policy layers;
- session duration a conditions;
- credential distribution;
- revocation;
- audit a investigation.

Exact authorization subject:

```text
principal/session
→ account/organization boundary
→ identity policy
→ resource policy
→ permission boundary
→ SCP
→ session policy
→ service-specific condition
→ API action/resource
```

`AccessDenied` nie je provider outage. Diagnostika musí vyhodnotiť celý effective policy graph a request context.

## 9. Network responsibility

AWS spravuje physical a virtual-network platformu. Atlas spravuje:

- VPC/subnet topology;
- route tables;
- SG/NACL;
- IGW/NAT/transit/private endpoints;
- hybrid routing;
- DNS;
- TLS a application authorization.

Network incident subject:

```text
source ENI/IP/identity
→ route
→ gateway/endpoint
→ SG/NACL/service policy
→ destination
→ return path
→ TLS/application auth
```

Provider service health môže byť green a Atlas route alebo SG generation môže blokovať flow.

## 10. Data a encryption responsibility

AWS môže poskytovať durable storage, snapshots, replication a encryption mechanisms. Atlas určuje:

- authoritative data;
- classification;
- access;
- encryption requirement;
- key owner a policy;
- backup a retention;
- immutability/isolation;
- restore a reconciliation;
- RPO/RTO;
- deletion a legal hold.

Rozlišuj:

```text
provider infrastructure encryption
service-side encryption
customer-managed key
client-side encryption
TLS
key policy a grant
rotation
revocation/deletion recovery
```

`Encrypted=true` nepreukazuje least-privilege decrypt access. KMS deny alebo scheduled key deletion môže vytvoriť data unavailability pri zdravej storage službe.

## 11. Logging a detection responsibility

AWS môže emitovať CloudTrail events, service logs, metrics, health events a findings. Atlas musí:

```text
enable coverage
→ route/collect
→ protect integrity
→ retain
→ query a correlate
→ detect a alert
→ investigate
→ respond
→ test coverage
```

Log capability bez enablement, retention alebo alertingu nie je funkčný control. Absencia eventu môže znamenať, že source log nebol zapnutý alebo bol smerovaný do iného accountu/Regionu.

## 12. Availability a recovery responsibility

AWS zodpovedá za service implementation a publikovaný service contract. Atlas zodpovedá za workload architecture a business continuity:

- Multi-AZ/multi-Region placement;
- health checks a traffic removal;
- retry/timeout/idempotency;
- quotas a failure-mode capacity;
- data replication;
- backup/restore;
- dependency mapping;
- failover/failback;
- DR test.

Single-AZ EC2 alebo single-NAT architecture je customer decision. Provider AZ failure môže byť trigger, ale customer architecture určuje business blast radius.

## 13. Patching a version lifecycle

### IaaS

Atlas vlastní inventory, vulnerability assessment, patching, reboot, validation a rollback.

### Managed service

AWS môže patchovať platformu, ale Atlas často vlastní:

- maintenance window;
- engine/runtime version;
- deprecation deadline;
- application compatibility;
- client/driver support;
- post-change verification;
- rollback alebo migration plan.

Managed runtime neodstraňuje version lifecycle.

## 14. Infrastructure as Code a writer ownership

AWS poskytuje API. Atlas vlastní:

- IaC source;
- review/approval;
- state a credentials;
- policy-as-code;
- drift detection;
- field ownership;
- environment boundaries;
- rollback/recovery.

Misconfiguration nasadená cez Terraform alebo CloudFormation zostáva customer-owned. Automatizácia zväčšuje rýchlosť a konzistenciu správnych aj chybných zmien.

## 15. Third-party responsibility

Marketplace alebo partner service vytvára tri boundaries:

```text
AWS infrastructure
+ vendor product
+ Atlas configuration/data/integration
```

Over:

- patch a support ownera;
- IAM permissions;
- network path;
- data processing a residency;
- backup/export;
- vulnerability a EOL;
- billing;
- incident escalation.

## 16. Worked incident: „AWS KMS outage“ bez provider root cause

Payment Pods po release I42 nedokážu dešifrovať settlement credential. Application hlási `AccessDeniedException`; KMS service health je green.

### Exact incident subject

```text
capability CAP-PAY-42
workload role WR42 session S-884
KMS key ARN K42
key policy generation KP19
IAM policy generation IP31
ciphertext encryption context: app=payments, env=prod
request IDs: RQ1001–RQ1188
Region: eu-central-1
```

### Competing hypotheses

1. KMS regional service degradation;
2. workload používa key v inom Regione;
3. IAM policy stratila `kms:Decrypt`;
4. key policy deny alebo chýbajúci principal;
5. encryption context mismatch;
6. session/SCP/permission boundary deny;
7. ciphertext bol vytvorený iným keyom;
8. workload používa stale credential alebo role session.

### Discriminating observations

```text
request ID/error code/Region
→ caller identity a session
→ exact key ARN a state
→ key policy + IAM + SCP + boundary
→ encryption context
→ CloudTrail KMS event
→ porovnanie healthy/stale Pod cohort
```

Finding: security hardening change KP19 vyžaduje encryption context `env=production`, ale application stále posiela `env=prod`. KMS správne odmieta decrypt. Root cause je customer-owned policy/application contract mismatch.

### Containment

- zastaviť rollout ďalšej Pod cohorty;
- zachovať functioning old cohort;
- zachovať request IDs, CloudTrail a policy diff;
- nevytvárať broad `kms:*` grant;
- neotáčať key ani nereencryptovať všetky dáta naslepo.

### Recovery

1. zvoliť canonical encryption-context contract;
2. opraviť application/config alebo policy kompatibilným spôsobom;
3. nasadiť bounded cohort;
4. overiť decrypt s WR42;
5. overiť, že unrelated principal je odmietnutý;
6. dokončiť rollout a payment synthetic;
7. pridať contract test do policy/application pipeline.

### Closure verdict

```text
current payment cohort dešifruje správny ciphertext
old/stale context je riadene podporovaný alebo odmietnutý podľa migration planu
neautorizovaný principal zostáva denied
CloudTrail coverage a alerts fungujú
payment authorization a settlement sú green
```

## 17. Provider incident a customer weakness môžu koexistovať

Provider degradation môže odhaliť customer-owned single point:

```text
provider AZ/service incident
→ customer nemá failure-mode capacity alebo failover
→ business outage je väčší než service blast radius
```

Root cause a contributing controls musia byť oddelené. Support case môže potvrdiť provider event, ale Atlas post-incident review stále hodnotí vlastnú architecture, detection a recovery.

## 18. Support boundary

Kvalitný AWS support case obsahuje:

- account ID bez credentials;
- Region;
- service/resource ARN alebo ID;
- UTC window;
- request IDs a error codes;
- scope a business impact;
- recent customer changes;
- reprodukciu;
- customer-side evidence;
- porovnanie healthy/affected cohort.

„AWS nefunguje“ nie je diagnostický subject.

## 19. Responsibility RACI a escalation

Pre kritický control eviduj:

| Control | AWS capability | Atlas owner | Evidence | Recovery owner |
|---|---|---|---|---|
| KMS platform | KMS service | Cloud security | AWS Health + CloudTrail | shared escalation |
| Key policy | policy API | Cloud security | versioned policy + test | Atlas |
| Workload role | IAM/STS | Platform team | policy/session audit | Atlas |
| DB backup feature | RDS backup | Data platform | recovery points/events | shared |
| Restore validity | restore workflow | Data/application owners | reconciliation report | Atlas |
| Physical facility | AWS | vendor-risk owner | AWS compliance evidence | AWS |

Shared responsibility sa operacionalizuje cez konkrétny owner/evidence/recovery mapping.

## 20. Anti-patterny

### AWS spravuje všetku security

AWS spravuje svoju infraštruktúru; customer configuration, identity, data a workload zostávajú zákaznícke.

### AWS certification znamená compliant workload

Provider control inheritance je iba časť zákazníckeho compliance programu.

### Encryption enabled znamená secure data

Policy, principal, context, key lifecycle a recovery rozhodujú o effective ochrane.

### Managed database nepotrebuje restore test

Backup feature nepreukazuje application-consistent recovery.

### Každý incident je provider outage

Najprv treba overiť customer-controlled layers a exact request subject.

### Shared znamená, že owner nie je jasný

Práve shared controls potrebujú najpresnejší interface, evidence a escalation contract.

## 21. Troubleshooting responsibility chain

```text
business symptom
→ exact account/Region/resource/request
→ customer identity/configuration
→ network a service integration
→ provider service data/control plane
→ external dependency
→ customer business/data outcome
```

Pre každú hypotézu definuj observation point. Zmena ownership predpokladu nie je technická diagnóza.

## 22. Kontrolné otázky

1. Čo tvorí exact responsibility subject?
2. Ako sa security of/in the cloud mení podľa služby?
3. Čo znamená shared control v praxi?
4. Prečo provider certification necertifikuje workload?
5. Ktoré časti IAM/KMS contractu vlastní zákazník?
6. Prečo AWS service health nepreukazuje application outcome?
7. Ako sa rozdeľuje backup capability a restore validity?
8. Čo musí obsahovať support case?
9. Ako oddelíš provider root cause od customer contributing failure?
10. Ako preukážeš, že remediation nezaviedla broad permission?

## Glossary impact

Relevantné pojmy: AWS responsibility subject, provider control, customer control, shared-control interface, control inheritance subject, effective security configuration, responsibility evidence, responsibility RACI, support escalation subject, provider-trigger/customer-amplifier incident, service-specific responsibility matrix a shared-control closure verdict.

## Oficiálna dokumentácia

- [AWS Shared Responsibility Model](https://docs.aws.amazon.com/whitepapers/latest/aws-risk-and-compliance/shared-responsibility-model.html)
- [Shared responsibility — Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/shared-responsibility.html)
- [AWS Security and Compliance](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/security-and-compliance.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Regions a Availability Zones](regions-availability-zones.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Scalability, elasticity a fault tolerance →](scalability-elasticity-fault-tolerance.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
