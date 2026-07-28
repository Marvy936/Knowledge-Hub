# IaaS, PaaS a SaaS

IaaS, PaaS a SaaS nie sú iba tri marketingové kategórie. Sú to rôzne **responsibility contracts** pre tú istú business capability. Správna otázka nie je „ktorý názov služby znie modernejšie“, ale:

```text
ktorý outcome potrebujeme
→ ktoré vrstvy musí niekto prevádzkovať
→ ktoré vrstvy preberá provider
→ ktoré zostávajú zákazníkovi
→ ako sa contract prejaví v identity, data, availability, recovery, evidence a coste
```

Vyššia abstrakcia odstraňuje časť infraštruktúrneho toil-u, ale neodstraňuje vlastníctvo business dát, identity, konfigurácie, integrácií ani výsledku obnovy.

## 1. Dominantný lifecycle service modelu

```text
business capability, SLO a constraints
→ workload/data/integration inventory
→ požadovaný control a portability level
→ service-model candidate
→ provider/customer responsibility matrix
→ architecture a configuration
→ deployment a process-loaded state
→ availability/security/cost evidence
→ incident a recovery ownership
→ periodic contract review alebo exit
```

Service model je správne zvolený až vtedy, keď je pre každý kritický krok známe:

- kto môže meniť desired state;
- kto patchuje a upgraduje platformu;
- kto riadi identity a secrets;
- kto navrhuje HA, backup a DR;
- kto produkuje a uchováva evidence;
- kto rozhoduje pri neznámom alebo partial failure;
- ako sa dá workload alebo dáta exportovať.

## 2. Exact capability subject

V tejto kapitole používame Atlas Payments capability:

```text
capability: CAP-PAY-42
business outcome: payment authorization do 700 ms p99
availability target: 99.95 % mesačne
RPO settlement dát: 0 pre potvrdené transakcie
RTO customer-facing API: 30 minút
source generation: Git commit G42
application artifact: image digest I42
configuration generation: C42
credential epoch: SE10
primary Region: eu-central-1
sensitive settlement dependency: on-premises ledger L17
```

Service-model rozhodnutie sa musí viazať na celý tento subject. Samotné „EC2“, „RDS“ alebo „SaaS“ nie je dostatočná identita výsledku.

## 3. Celý responsibility stack

Zjednodušený stack:

```text
business process a legal outcome
business data a retention
application behavior
application configuration a identity
runtime/middleware/data engine
operating system
virtualization/container platform
compute, storage a network primitives
physical facilities a hardware
```

Pri každej vrstve treba rozlíšiť štyri úlohy:

```text
provisionovanie
→ bezpečná prevádzka
→ pozorovanie a incident response
→ recovery a decommission
```

To, že provider vrstvu prevádzkuje, ešte neznamená, že provider vlastní zákaznícky configuration alebo business acceptance.

## 4. IaaS contract

Infrastructure as a Service poskytuje compute, network a storage primitives. Provider spravuje fyzické facilities, hardware a virtualization/control plane. Zákazník typicky spravuje guest OS, image lifecycle, packages, runtime, application, data, network policy, identity usage, monitoring, backup a workload HA.

Mechanizmus:

```text
customer machine/image intent
→ provider vytvorí virtual resource
→ customer bootstrapping a OS/runtime configuration
→ application process
→ customer health, scale, backup a recovery controls
```

IaaS je vhodný, keď workload potrebuje OS/kernel control, špecifické agents alebo drivers, legacy runtime, vlastné network appliance behavior alebo presnú host-level observability.

Cena tejto kontroly je väčší operational surface:

- patching a reboot orchestration;
- AMI/image provenance;
- configuration drift;
- capacity a fleet replacement;
- host telemetry a vulnerability management;
- backup/restore orchestration;
- snowflake-server riziko.

### IaaS failure boundary

EC2 instance `running` a system-status checks `ok` nepreukazujú:

- že guest OS je patchnutý;
- že application načítala C42 a SE10;
- že data sú konzistentné;
- že workload prežije stratu AZ;
- že backup je obnoviteľný;
- že API spĺňa 700 ms p99.

Provider môže mať zdravý virtualization plane a zákaznícky workload môže byť nefunkčný pre chybný OS firewall, expirovaný certificate alebo plný filesystem.

## 5. PaaS contract

Platform as a Service preberá OS a časť runtime alebo data-platform operations. Môže poskytovať managed database, application runtime, serverless compute, managed container control plane, message broker alebo cache.

Mechanizmus:

```text
customer code/schema/config intent
→ provider-managed runtime alebo engine
→ customer identity, network a service configuration
→ application/data execution
→ shared platform a business verification
```

Provider môže spravovať host replacement, platform patching, replication mechanism a control plane. Zákazník stále vlastní:

- application code, schema a dependency compatibility;
- data classification a access;
- service configuration a network exposure;
- IAM roles, resource policies a KMS usage;
- capacity mode, quotas a cost limits;
- backup retention, restore test a business RPO/RTO;
- client retry, timeout a failover behavior;
- application telemetry a user-path validation.

### PaaS failure boundary

Managed database `available` nepreukazuje:

```text
správny endpoint a Region
→ network path
→ database identity a TLS
→ správnu schema generation
→ application-consistent data
→ tested restore
→ payment outcome
```

Managed Kubernetes control plane nepreberá ownership workload images, Kubernetes RBAC, NetworkPolicy, data, add-ons ani application recovery.

## 6. SaaS contract

Software as a Service poskytuje hotovú application capability. Provider spravuje application code, runtime, platform a infraštruktúru. Zákazník spravuje tenant configuration, users, federation, sharing, data governance, integrations, client/device security, retention/export a business proces.

Mechanizmus:

```text
tenant a identity configuration
→ provider application service
→ provider internal runtime/data implementation
→ customer users/integrations
→ customer business process a compliance outcome
```

SaaS minimalizuje infrastructure operations, ale zväčšuje dependence na provider feature, API, tenant, rate-limit, retention a export contracts.

### SaaS failure boundary

Provider status page `operational` nepreukazuje:

- že Atlas tenant federation funguje;
- že admin permissions sú least privilege;
- že webhook credential neexpiroval;
- že retention spĺňa právny contract;
- že dáta možno exportovať v použiteľnom formáte;
- že kritický business proces je obnoviteľný po tenant misconfiguration.

## 7. Shared responsibilities sa neposúvajú lineárne

Vyššia abstrakcia zvyčajne presúva viac host/runtime práce na providera, ale nie každá responsibility sa presúva rovnakým smerom.

```text
IaaS: customer owns guest-to-business stack
PaaS: provider owns viac runtime/platform vrstiev, customer owns code/data/config
SaaS: provider owns application implementation, customer owns tenant/data/process
```

Identity, data governance, business continuity, integration credentials a outcome verification zostávajú shared alebo customer-owned vo všetkých modeloch.

## 8. Responsibility matrix pre CAP-PAY-42

| Capability layer | EC2/IaaS | Managed runtime/database | SaaS replacement |
|---|---|---|---|
| Physical hardware | AWS | AWS | provider |
| Guest OS/runtime patching | Atlas | provider/shared | provider |
| Application code | Atlas | Atlas | provider |
| Tenant/service configuration | Atlas | Atlas | Atlas |
| IAM/federation | Atlas/shared | Atlas/shared | Atlas/shared |
| Business data governance | Atlas | Atlas | Atlas/shared |
| Network exposure | Atlas | Atlas/shared | provider + Atlas tenant controls |
| HA feature mechanism | Atlas architecture | provider mechanism + Atlas configuration | provider service contract |
| Business RPO/RTO | Atlas | Atlas | Atlas |
| Restore test | Atlas | Atlas | Atlas/provider podľa export contractu |
| User-path telemetry | Atlas | Atlas | Atlas synthetic + provider evidence |
| Exit/portability | Atlas | Atlas | Atlas podľa export/API contractu |

Všeobecná tabuľka nenahrádza service-specific dokumentáciu a commercial contract.

## 9. Worked scenario: nesprávne vyhodnotená managed responsibility

Atlas presúva payment API z VM fleet-u na managed application runtime a ledger databázu na managed relational database. Tím predpokladá:

```text
managed runtime + managed database
→ provider vlastní patching, HA a backup
→ customer už nepotrebuje recovery design
```

Tri mesiace po migrácii operator omylom zmaže settlement records cez application credential. Platforma a databáza zostávajú healthy.

### Exact incident subject

```text
capability CAP-PAY-42
managed DB resource DB42, Region eu-central-1
backup policy generation BP7
retention 7 dní
latest automated recovery point RP92
application transaction ledger generation L17
credential epoch SE10
incident window 2026-07-28T08:10Z–08:17Z
```

### Competing hypotheses

1. provider storage corruption;
2. database failover vrátil starú repliku;
3. application migration odstránila records;
4. compromised alebo chybný customer credential vykonal delete;
5. backup policy neobsahuje požadovaný retention alebo point-in-time window;
6. API číta nesprávny Region alebo database endpoint.

### Discriminating observations

```text
audit event a principal
→ SQL/application operation ID
→ DB endpoint/Region a engine event
→ backup/recovery-point inventory
→ transaction ledger a downstream settlement evidence
→ provider health event
```

Audit ukáže delete operáciu cez Atlas application role. Provider platforma fungovala podľa contractu. Root cause je customer-owned authorization a application behavior; slabý recovery contract je contributing control failure.

### Containment

- revoke SE10 a zastaviť delete-capable writer;
- zachovať audit, request IDs a DB logs;
- zastaviť ďalšie settlement processing;
- nevykonať restore cez current production DB naslepo;
- určiť canonical transaction ledger a incident cut-off.

### Recovery

1. vytvoriť isolated point-in-time restore;
2. porovnať restored records s immutable settlement ledgerom;
3. doplniť chýbajúce transakcie idempotentnou reconciliation operáciou;
4. vydať scoped credential SE11;
5. obnoviť payment processing po read/write a business verification;
6. predĺžiť retention a pridať cross-account recovery copy podľa RPO/RTO;
7. testovať restore a reconciliation ako jeden recovery workflow.

### Closure verdict

Incident nie je uzavretý pri stave DB `available`. Musí platiť:

```text
všetky potvrdené payments majú presne jeden settlement record
old credential SE10 je odmietnutý
nový writer používa SE11
backup/recovery policy spĺňa RPO/RTO
druhý reconciliation pass je no-op
```

## 10. Availability a SLA boundary

SLA je service contract a prípadný service credit mechanism. Nie je to hotová workload architecture.

Provider môže ponúknuť Multi-AZ capability, ale zákazník často musí:

- zvoliť správny deployment mode;
- rozložiť application capacity;
- nakonfigurovať health checks;
- navrhnúť clients, retries a timeouts;
- odstrániť single-AZ dependencies;
- overiť quotas a recovery capacity;
- testovať failover a failback.

## 11. Backup, replication a durability

Rozlišuj:

```text
durability
replication
snapshot/recovery point
backup policy
isolated immutable copy
application-consistent restore
business recovery
```

Provider durability chráni proti určitej triede media failure. Replication môže replikovať aj customer delete alebo corruption. Backup existuje až s jasným obsahom, retention, isolation a restore contractom. Recovery je preukázaná až business validáciou.

## 12. Observability contract

Každý service model potrebuje inú evidence surface:

### IaaS

- provider instance/system checks;
- OS/kernel/process telemetry;
- network a storage evidence;
- application a business signals.

### PaaS

- provider service health a engine/platform events;
- customer configuration/audit;
- application telemetry;
- synthetic user path;
- backup/restore evidence.

### SaaS

- tenant audit a identity logs;
- provider status/support evidence;
- API/webhook telemetry;
- client synthetic;
- export a retention validation.

Absencia host metrics pri PaaS alebo SaaS nie je dôkaz absencie problému. Observation contract sa musí prispôsobiť vrstve, ktorú provider sprístupňuje.

## 13. Cost a total ownership

Porovnávaj:

```text
service bill
+ engineering a operations labor
+ security/compliance controls
+ support
+ backup/DR
+ migration a data transfer
+ downtime risk
+ opportunity cost
```

IaaS môže mať nižšiu unit cenu a vyšší toil. PaaS môže mať vyššiu service cenu a nižší platform toil. SaaS môže byť lacný pri malom tenant scope-e a drahý pri per-user, data alebo integration scale.

## 14. Portability a exit subject

Portability nie je binárna. Posudzuj:

- application/source portability;
- runtime a deployment portability;
- data format a volume export;
- identity a policy translation;
- network assumptions;
- observability a audit portability;
- operational runbooks;
- commercial notice, egress a migration time.

Container image sama negarantuje, že managed database semantics, IAM, KMS, queues alebo provider APIs možno preniesť bez redesignu.

## 15. Rozhodovací postup

Pre každú capability prejdite:

```text
1. outcome/SLO/RPO/RTO
2. data a compliance constraints
3. required OS/runtime control
4. workload variability a capacity
5. team operations capability
6. service-specific responsibility matrix
7. failure a recovery model
8. observability a support evidence
9. TCO
10. exit a portability
```

Výber sa môže líšiť po components. Atlas môže používať IaaS pre legacy settlement adapter, PaaS pre API/databázu a SaaS pre customer support bez toho, aby bol celý systém jedným service modelom.

## 16. Troubleshooting podľa responsibility boundary

Pri incidente mapuj exact path:

```text
customer configuration/identity
→ customer application/runtime
→ shared service endpoint/integration
→ provider-managed platform
→ provider infrastructure
→ external dependency
```

Pre každú hypotézu priraď observation point a ownera. Provider escalation musí obsahovať Region, resource ID, UTC window, request IDs, impact, reproduction a už overené customer-controlled vrstvy.

## 17. Anti-patterny

### Managed znamená bez zákazníckej zodpovednosti

Managed service odstraňuje časť platform operations, nie identity, data, configuration a outcome ownership.

### IaaS je automaticky najlacnejší

Ignoruje labor, drift, incidenty, spare capacity a recovery engineering.

### SaaS nepotrebuje architecture alebo security review

Tenant federation, sharing, retention, integrations a export môžu byť kritické failure boundaries.

### Platform HA je to isté ako business continuity

Healthy service nemusí obnoviť správne dáta, dependency alebo user journey.

### Service model sa určí iba podľa produktu

Jedna služba môže mať pre rôzne features rozdielne responsibility boundaries. Contract a konkrétna konfigurácia majú prednosť.

## 18. Kontrolné otázky

1. Čo tvorí exact cloud service subject?
2. Ktoré responsibilities zostávajú zákazníkovi vo všetkých troch modeloch?
3. Čo preukazuje provider service health a čo nepreukazuje?
4. Prečo replication nie je automaticky backup?
5. Ako sa líši IaaS host evidence od PaaS/SaaS evidence?
6. Kedy OS-level control odôvodňuje IaaS?
7. Ako sa hodnotí rollback alebo restore pri managed data service?
8. Prečo SLA nenahrádza Multi-AZ a application design?
9. Čo musí obsahovať exit/portability subject?
10. Ako rozlíšiš provider root cause od customer configuration failure?

## Glossary impact

Relevantné pojmy: cloud service-model subject, responsibility contract, customer-managed layer, provider-managed layer, shared integration boundary, managed-service outcome boundary, capability acceptance verdict, service health verdict, recovery responsibility, service-model exit subject, portability dimension a total-cost-of-ownership subject.

## Oficiálna dokumentácia

- [What is cloud computing?](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/what-is-cloud-computing.html)
- [Types of cloud computing](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/types-of-cloud-computing.html)
- [AWS Shared Responsibility Model](https://docs.aws.amazon.com/whitepapers/latest/aws-risk-and-compliance/shared-responsibility-model.html)
- [Shared responsibility — Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/shared-responsibility.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CKA troubleshooting drills](../10-helm-and-cka/cka-troubleshooting-drills.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Public, private a hybrid cloud →](public-private-hybrid-cloud.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
