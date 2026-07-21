# Shared responsibility model

AWS Shared Responsibility Model rozdeľuje security, compliance, availability a operations responsibilities medzi AWS a zákazníka. Základná formulácia je:

```text
AWS je zodpovedné za security OF the cloud.
Zákazník je zodpovedný za security IN the cloud.
```

Toto pravidlo je iba východisko. Konkrétna responsibility boundary sa mení podľa použitej služby, konfigurácie, integrácie a regulačných požiadaviek.

## 1. Security of the cloud

AWS typicky zodpovedá za:

- fyzickú bezpečnosť dátových centier,
- physical servers, storage a network hardware,
- host operating system a virtualization layer,
- základnú AWS global infrastructure,
- provider service control plane a managed service runtime podľa service contractu,
- hardware disposal a facility resilience,
- provider-level compliance controls a audity.

Zákazník nemá prístup k hypervisoru alebo fyzickému dátovému centru a nemôže tieto vrstvy sám patchovať.

## 2. Security in the cloud

Zákazník typicky vlastní:

- identity, credentials a authorization,
- account a organization configuration,
- data classification a protection,
- encryption choices a key policy podľa služby,
- network configuration,
- workload OS a patching pri IaaS,
- application code a dependencies,
- security groups, resource policies a service configuration,
- logging, monitoring a incident response,
- backup, recovery a business continuity,
- compliance použitia služby a spracovania dát.

Managed service znižuje rozsah technickej prevádzky, ale neodstraňuje zákaznícku zodpovednosť za data, access a configuration.

## 3. Responsibility sa mení podľa service modelu

### EC2

AWS spravuje:

- physical facility,
- hardware,
- host OS,
- hypervisor.

Zákazník spravuje:

- guest OS,
- patches,
- packages a agents,
- application,
- security groups a IAM,
- EBS/data encryption konfiguráciu,
- backup a recovery.

### Managed database

AWS preberá viac vrstiev:

- host a database platform operations podľa služby,
- patching engine/platformy podľa configured maintenance modelu,
- infrastructure replacement,
- built-in replication alebo backup capabilities podľa configuration.

Zákazník stále vlastní:

- database users a permissions,
- schema a queries,
- data classification,
- network exposure,
- encryption/KMS policy,
- retention a restore testing,
- engine parameters, ktoré služba sprístupňuje,
- application consistency a migration.

### Serverless

AWS spravuje runtime infrastructure a scaling platformu. Zákazník vlastní:

- function code,
- dependencies,
- IAM execution role,
- event sources,
- input validation,
- secrets,
- logging,
- concurrency a cost controls,
- business continuity.

### SaaS

Provider spravuje celý application stack, ale zákazník stále vlastní tenant identities, sharing, configuration, data governance, integrations, endpoint security a export/recovery plán.

## 4. Responsibility matrix

Pre každú službu vytvor tabuľku:

| Vrstva | AWS | Zákazník | Shared/poznámka |
|---|---|---|---|
| Physical facilities | Owns | — | AWS audit evidence |
| Host/hypervisor | Owns | — | service-specific |
| Guest OS | — | Owns pri EC2 | pri PaaS preberá AWS |
| Network policy | platform | configures | SG/NACL/routes |
| Identity | IAM service | policies a principals | federácia je shared integration |
| Data | storage platform | classification a access | durability ≠ backup |
| Encryption | capability | enable/key policy/use | service-specific defaults |
| Logging | emits signals | enable, retain, alert | centralizácia je customer scope |
| Recovery | service features | design, test, execute | business RPO/RTO customer scope |

Bez service-specific matrixu vznikajú slepé miesta.

## 5. Control inheritance

Zákazník môže zdediť provider controls, napríklad:

- physical security,
- facility environmental controls,
- hardware lifecycle,
- hypervisor patching,
- provider certifications.

Inheritance neznamená automatickú compliance workloadu. Zákazník musí:

- vybrať eligible službu a Region,
- nakonfigurovať ju správne,
- chrániť data a identities,
- zachovať evidence,
- vykonať vlastné risk assessment,
- splniť aplikačné a procesné controls.

## 6. Compliance

AWS certification alebo audit report necertifikuje automaticky zákaznícku aplikáciu.

Zákazník vlastní:

- applicability regulácie,
- data mapping,
- retention a deletion,
- access review,
- separation of duties,
- incident notification,
- vendor risk,
- lawful processing,
- audit evidence z vlastnej vrstvy.

Provider dokumentácia a Artifact reports sú vstup do zákazníckeho compliance programu.

## 7. Identity boundary

AWS poskytuje IAM, STS, Organizations a ďalšie identity capabilities. Zákazník rozhoduje:

- kto je principal,
- ako sa autentifikuje,
- aké policies sa aplikujú,
- kde je trust relationship,
- ako sa používajú temporary credentials,
- ako sa ruší access,
- ako sa auditujú requests.

Credential leak alebo broad role je zákaznícky incident aj vtedy, keď IAM service funguje správne.

## 8. Network boundary

AWS spravuje physical network a virtual networking platformu. Zákazník spravuje:

- VPC a subnet topology,
- routes,
- security groups,
- NACLs,
- internet/NAT/transit gateways,
- private endpoints,
- DNS a hybrid connectivity,
- application TLS a authorization.

„AWS network outage“ nesmie byť prvá hypotéza pred overením route, policy, endpoint a customer changes.

## 9. Data protection

AWS môže poskytovať durability, encryption, snapshots a replication features. Zákazník musí určiť:

- authoritative data,
- klasifikáciu,
- kto má access,
- encryption requirements,
- KMS key ownership,
- backup schedule,
- retention a immutability,
- restore test,
- RPO/RTO,
- deletion a legal hold.

Service-side replication nie je automaticky zákaznícky backup ani DR.

## 10. Encryption responsibility

Rozlišuj:

- provider encryption of infrastructure,
- service-side encryption,
- customer-managed keys,
- client-side encryption,
- TLS in transit,
- key access policy,
- key rotation a recovery.

Zapnutá encryption s broad decrypt policy nemusí spĺňať security cieľ. KMS key deletion alebo deny policy môže spôsobiť data unavailability.

## 11. Logging a detection

AWS poskytuje service logs, CloudTrail events, metrics a security findings podľa služby. Zákazník musí:

- logovanie zapnúť, ak nie je default,
- centralizovať ho,
- chrániť pred zmenou,
- nastaviť retention,
- monitorovať coverage,
- vytvoriť detections a alerts,
- reagovať na findings,
- testovať incident workflow.

Log capability bez retention a alerting nie je funkčný detection control.

## 12. Availability

AWS zodpovedá za dostupnosť služby podľa publikovaného service designu a SLA. Zákazník zodpovedá za architektúru workloadu:

- Multi-AZ alebo multi-Region placement,
- health checks a failover,
- application retry/timeouts,
- capacity a quotas,
- data replication,
- backup a restore,
- dependency mapping,
- DR testing.

Použitie single-AZ EC2 instance je zákaznícke architektonické rozhodnutie, nie porušenie providerovej shared responsibility hranice.

## 13. Patching

### Customer-managed OS

Zákazník vlastní inventory, vulnerability assessment, patching, reboot, validation a rollback.

### Managed runtime

AWS patchuje platformu, ale zákazník môže vlastniť:

- maintenance window,
- engine/runtime version,
- upgrade deadline,
- application compatibility,
- deprecation migration,
- post-change validation.

„Managed“ neznamená, že version lifecycle možno ignorovať.

## 14. Infrastructure as Code

AWS poskytuje APIs a service behavior. Zákazník vlastní:

- IaC source,
- review a approval,
- state protection,
- policy-as-code,
- drift detection,
- deployment credentials,
- rollback,
- environment separation.

Misconfiguration nasadená cez Terraform zostáva zákazníckou zodpovednosťou.

## 15. Marketplace a third-party services

Pri third-party produkte vzniká trojstranný model:

```text
AWS infrastructure responsibility
+ vendor product responsibility
+ customer configuration/data responsibility
```

Over:

- support boundary,
- patch owner,
- data processing,
- network path,
- IAM permissions,
- backup/export,
- end-of-life,
- incident escalation.

## 16. Managed service neznamená managed outcome

AWS môže spravovať:

- hardware,
- replication mechanism,
- service patching,
- automatic replacement.

Zákazník stále musí spravovať:

- business availability cieľ,
- správnu konfiguráciu,
- capacity mode,
- data consistency,
- access,
- restore validity,
- cost a quotas.

Feature existence nie je dôkaz správneho použitia.

## 17. Support boundary

Pri support case priprav:

- account ID bez credentials,
- Region,
- service/resource IDs,
- UTC timestamps,
- request IDs,
- error messages,
- scope a impact,
- recent changes,
- reproduction,
- customer-side evidence.

Provider support nemôže efektívne diagnostikovať neurčitý opis „AWS nefunguje“.

## 18. Incident ownership

Použi otázky:

1. Zlyháva provider service pre viac zákazníkov/Region?
2. Zlyháva iba jeden account, VPC alebo resource?
3. Bola recent customer config/IAM/network zmena?
4. Je API request odmietnutý alebo data plane nedostupný?
5. Funguje rovnaká operácia v inom resource/Region/account?
6. Existuje AWS Health event?
7. Aký request ID a error code poskytol service?

Incident môže byť shared: provider degradation odhalí zákaznícky single point of failure.

## 19. Anti-patterny

### AWS spravuje security

AWS spravuje iba svoju časť stacku.

### Service je compliant, teda workload je compliant

Chýba zákaznícka konfigurácia, proces a evidence.

### Encryption je zapnutá, teda dáta sú bezpečné

Kľúčová je policy, identity, context a lifecycle.

### Managed database nepotrebuje backup test

Platform backup feature nepreukazuje application recovery.

### Provider outage je príčina každého incidentu

Najprv over customer-controlled layers.

## 20. Troubleshooting responsibility

Príklad managed database connectivity:

```text
application identity/config
→ DNS
→ route
→ security group/NACL
→ service endpoint
→ database auth/TLS
→ engine availability
→ provider service health
```

Každý krok má iného vlastníka alebo shared boundary. Diagnostika musí postupovať cez evidence, nie cez organizačné predpoklady.

## 21. Kontrolné otázky

1. Čo znamená security of a security in the cloud?
2. Ako sa responsibility boundary mení medzi EC2 a managed database?
3. Prečo provider compliance neznamená customer compliance?
4. Kto vlastní IAM policies a credential lifecycle?
5. Prečo service replication nie je automaticky backup?
6. Kto vlastní Multi-AZ workload design?
7. Ako sa mení patching responsibility pri managed runtime?
8. Aké riziko vzniká pri Marketplace produkte?
9. Aké evidence patrí do AWS support case?
10. Ako rozlíšiš provider a customer incident?

## Glossary impact

Relevantné pojmy: AWS Shared Responsibility Model, security of the cloud, security in the cloud, control inheritance, customer responsibility, provider responsibility, shared control, service responsibility matrix, customer configuration risk, compliance inheritance a support boundary.

## Oficiálna dokumentácia

- [AWS Shared Responsibility Model](https://docs.aws.amazon.com/whitepapers/latest/aws-risk-and-compliance/shared-responsibility-model.html)
- [Shared responsibility — Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/shared-responsibility.html)
