# Public, private a hybrid cloud

Cloud deployment model opisuje, kde capability beží, kto ovláda infraštruktúrny a platformový boundary a ktoré failure, identity, data a connectivity domains musia spolupracovať. Nie je to synonymum service modelu. Public cloud môže poskytovať IaaS, PaaS aj SaaS; private cloud môže poskytovať interné IaaS alebo PaaS capabilities.

Užitočný mentálny model:

```text
business capability a locality constraints
→ placement a control requirements
→ deployment-domain inventory
→ identity/network/DNS/data integration
→ workload a management-plane realization
→ failure isolation a autonomous behavior
→ end-to-end verification
→ failover, reconciliation alebo exit
```

## 1. Deployment-model subject

Deployment model posudzuj cez exact subject:

```text
capability: CAP-PAY-42
public-cloud environment: AWS account A42, eu-central-1
private environment: on-premises site DC17
cloud VPC: V42
on-premises network domain: NET17
hybrid identity generation: IDF8
hybrid DNS generation: DNS12
connectivity generation: DX7 + VPN4 backup
application release: I42/C42/SE10
cloud database: DB42
on-premises ledger: L17
```

Označenie „hybrid“ samo nepreukazuje, že tieto subjects majú kompatibilný routing, identity, data consistency, observability a recovery contract.

## 2. Service model a deployment model sú dve osi

```text
service model
→ ktorú technologickú vrstvu spravuje provider alebo zákazník
→ IaaS / PaaS / SaaS

deployment model
→ kde capability beží, komu je infraštruktúra určená a ako sa prepája
→ public / private / hybrid / multi-cloud / edge
```

Príklady:

- EC2 v AWS je public-cloud IaaS;
- RDS je public-cloud managed data platform;
- interný OpenStack môže byť private-cloud IaaS;
- SaaS môže používať public-cloud infraštruktúru a private connectivity k zákazníkovi;
- AWS Outposts môže rozšíriť AWS operating model do zákazníckej lokality, ale lokálny hardware a service-link failure zostávajú samostatné boundaries.

## 3. Public-cloud lifecycle

```text
account/organization a Region selection
→ identity a guardrails
→ VPC/subnet/endpoint placement
→ service a workload provisioning cez API
→ provider physical/platform realization
→ customer configuration a data
→ operational/business verification
→ scale, recovery a decommission
```

Public cloud používa provider-owned fyzickú infraštruktúru a logicky izolované accounts, identities a virtual networks. „Public“ neznamená, že workload musí byť verejne dostupný. Private subnets, private endpoints, resource policies, encryption a workload identity môžu vytvoriť neverejný data path v public-cloud infraštruktúre.

### Public-cloud failure boundary

Healthy provider Region nepreukazuje:

- správny account a Region;
- správnu VPC route a endpoint policy;
- správne IAM/session context;
- dostupnú customer quota alebo IP capacity;
- správny application release;
- obnoviteľné dáta;
- funkčný hybrid dependency path.

## 4. Private-cloud lifecycle

Private cloud je dedicated cloud operating model pre jednu organizáciu, nie iba skupina hypervisorov.

```text
capacity pool a platform ownership
→ API/self-service catalog
→ identity/policy/quotas
→ standardized image a network/storage contracts
→ tenant provisioning
→ platform a workload lifecycle
→ metering, reliability a recovery
→ hardware refresh a decommission
```

Cloud-like characteristics zahŕňajú:

- API a automation;
- self-service provisioning;
- štandardizované templates;
- policy enforcement;
- metering, showback alebo chargeback;
- pool-based capacity management;
- platform service ownera;
- upgrade a hardware replacement lifecycle.

Bez nich ide skôr o tradičnú virtualizačnú platformu.

### Private-cloud failure boundary

Vlastná fyzická kontrola neposkytuje automaticky:

- aktuálny patch level;
- redundantnú power/network/storage architektúru;
- elastickú spare capacity;
- kvalitnú identity governance;
- immutable backup;
- 24/7 incident response;
- testovaný site recovery.

Private cloud môže byť vhodný pre specialized hardware, disconnected operation, veľmi nízku local latency, regulačné constraints alebo stabilný veľký workload. Výhoda existuje iba pri dostatočnej platformovej a prevádzkovej zrelosti.

## 5. Hybrid-cloud lifecycle

Hybrid cloud spája najmenej dva odlišné operating a failure domains.

```text
cloud a private capability inventory
→ authoritative identity, DNS a data ownership
→ redundant connectivity a routing
→ security/policy translation
→ workload a data placement
→ management/telemetry correlation
→ connected aj disconnected behavior
→ failover/failback/reconciliation
→ business acceptance
```

Hybrid cloud nie je jeden VPN tunnel. Je to dlhodobý contract pre:

- network connectivity a return path;
- identity federation a machine credentials;
- DNS authority a forwarding;
- data replication, consistency a conflict resolution;
- deployment a configuration ownership;
- observability a audit correlation;
- behavior pri strate WAN alebo cloud control plane;
- capacity a recovery v každom prostredí.

AWS Prescriptive Guidance organizuje hybrid best practices okolo networking, security, resiliency, capacity planning a infrastructure management. Tieto oblasti tvoria jeden systém, nie päť nezávislých checklistov.

## 6. Connectivity subject

Pre CAP-PAY-42:

```text
source workload Pod/instance UID
→ source IP/port a security identity
→ VPC route table generation
→ Transit/DX/VPN attachment generation
→ BGP route a tunnel/circuit state
→ on-premises firewall generation
→ destination IP/port
→ return route
```

Dedicated connectivity môže stabilizovať capacity a routing, ale sama nezaručuje encryption ani redundancy. VPN cez internet môže byť rýchlejšia na provisioning, ale má variabilnejší path a throughput. Production hybrid design často potrebuje viac circuits, lokalít, gateways a dynamické routing controls.

### Unknown network outcome

TCP timeout nepreukazuje, že link je down. Hypotézy zahŕňajú:

- DNS vrátil chybnú alebo stale adresu;
- source route chýba;
- BGP propaguje nesprávny prefix;
- firewall/NACL/SG blokuje flow;
- destination process nepočúva;
- return path je asymetrický;
- MTU alebo fragmentation zlyháva;
- identity/TLS zlyhá po vytvorení TCP session.

## 7. Hybrid identity

Preferovaný model používa federáciu a krátkodobé credentials:

```text
workforce/workload identity source
→ federation/trust policy
→ short-lived cloud session alebo certificate
→ service authorization
→ audit request identity
```

Dlhodobé access keys synchronizované do on-premises systémov vytvárajú rotation, revocation a exfiltration risk. Identity availability musí mať jasné disconnected behavior: ktoré lokálne operations pokračujú pri strate cloud IdP a ktoré musia fail-closed.

## 8. Hybrid DNS

Exact DNS path:

```text
application query
→ local resolver a cache
→ authoritative/conditional-forwarding decision
→ inbound/outbound resolver endpoint
→ cloud alebo private authoritative zone
→ TTL/negative cache
→ selected address
→ connection
```

Navrhni:

- authoritative zone ownera;
- split-horizon behavior;
- conditional forwarding;
- overlapping namespace policy;
- resolver endpoint HA;
- TTL a failover timing;
- behavior pri strate linky;
- DNSSEC alebo validation podľa scope-u.

Funkčná route nepreukazuje funkčné DNS. Úspešný lookup nepreukazuje funkčný endpoint.

## 9. Hybrid data

Data contract musí určiť:

```text
authoritative source
→ replication/transfer mechanism
→ ordering a consistency
→ lag a checkpoint
→ conflict resolution
→ consumer compatibility
→ failover/failback
→ reconciliation a recovery
```

Synchronous cross-environment writes znižujú niektoré consistency gaps, ale pridávajú WAN latency a spoločný failure domain. Asynchronous replikácia zlepšuje decoupling, ale vyžaduje explicitný RPO, lag telemetry, idempotenciu a conflict/replay model.

## 10. Management-plane boundary

Jednotný dashboard neznamená jednotný control plane. Urči:

- authoritative inventory;
- source of truth pre configuration;
- ownership každého mutable fieldu;
- policy distribution;
- agent/update behavior;
- log a metric transport pri WAN outage;
- lokálnu autonomy;
- emergency access;
- kto môže vykonať recovery pri nedostupnom central control plane.

Hybrid management musí odlíšiť management-plane outage od pokračujúceho workload data plane-u.

## 11. Worked incident: healthy circuits, payment timeouty

Atlas presunie customer-facing API do AWS, ale settlement ledger L17 zostane on-premises. Po network maintenance približne 35 % payments timeoutuje. DX dashboard aj backup VPN sú green.

### Exact incident subject

```text
capability CAP-PAY-42
release I42/C42/SE10
cloud client cohort: instances v AZ ID euc1-az2
on-premises ledger VIP: 10.44.17.20:5443
DNS name: ledger.internal
DX connection: DX7
backup VPN: VPN4
cloud route generation: RT42-g19
on-premises route generation: BGP17-g31
firewall generation: FW17-g22
```

### Competing hypotheses

1. ledger process je preťažený;
2. DNS vracia starú VIP;
3. DX path nepropaguje cloud subnet prefix pre jednu AZ;
4. backup VPN má preferovanejšiu asymetrickú route;
5. firewall generation nepovoľuje nový source CIDR;
6. MTU zlyháva iba pri väčších TLS records;
7. application connection pool drží stale sessions.

### Discriminating observations

```text
scope podľa source AZ/subnet
→ exact DNS answer
→ source/destination IP a port
→ cloud route a propagated prefixes
→ DX/VPN/BGP path
→ firewall allow/deny log
→ SYN/SYN-ACK a TLS handshake
→ application request/correlation ID
```

Finding: nový subnet v euc1-az2 bol pridaný do AWS route table, ale on-premises route policy neprijala jeho prefix. Return traffic preto išiel cez backup VPN a bol odmietnutý stateful firewallom. Green circuits nepreukazovali správny per-prefix round trip.

### Containment

- zastaviť rollout do affected subnet cohorty;
- ponechať healthy AZ capacity;
- zachovať BGP, firewall a flow-log evidence;
- nesmerovať všetok traffic naslepo cez jeden link;
- nepovoľovať broad CIDR iba kvôli rýchlej oprave.

### Recovery

1. opraviť authoritative prefix inventory;
2. publikovať a akceptovať nový prefix cez redundantné paths;
3. zosúladiť firewall object s exact source CIDR;
4. vyčistiť iba affected stale sessions;
5. overiť TCP, TLS a payment settlement z každej AZ;
6. simulovať loss DX7 a overiť VPN4 failover/return path;
7. pridať pre-deployment route-contract test pre nový subnet.

### Closure verdict

```text
povolený payment flow funguje z každej production AZ
zakázané source CIDRs zostávajú blokované
DX aj VPN path majú symetrický return contract
second reconciliation BGP/firewall configuration je no-op
payment authorization a settlement sú presne raz
```

## 12. Edge a disconnected operation

Edge placement dáva compute alebo storage bližšie k users, devices alebo production processu. Potrebuje:

- secure bootstrap a hardware identity;
- fleet inventory;
- offline queueing a local decisions;
- bounded local data retention;
- update/rollback;
- local telemetry buffer;
- conflict resolution po reconnecte;
- hardware replacement a decommission.

Local Zone, Wavelength alebo Outposts nie sú automaticky samostatný Region alebo DR boundary. Ich parent-Region a service-link dependencies sa musia overiť podľa konkrétnej služby.

## 13. Multi-cloud

Multi-cloud používa viac cloud providers. Môže znížiť concentration risk alebo splniť business/regulatory požiadavku, ale pridáva:

- viac IAM a policy modelov;
- odlišné network/DNS semantics;
- duplicate platform tooling;
- data transfer a consistency complexity;
- skills fragmentation;
- slabšiu observability correlation;
- viac recovery a support boundaries.

Druhý provider nie je DR, kým tam nie je testovaný artifact, data generation, identity, capacity, traffic switch a operating runbook.

## 14. Portability subject

Portability zahŕňa:

```text
source a artifact
infrastructure a platform contract
data format a export
identity a key model
network/DNS assumptions
observability a audit
deployment/recovery runbooks
capacity a commercial constraints
```

Lowest-common-denominator architecture môže odstrániť hodnotu managed služieb bez toho, aby zabezpečila reálnu portable recovery.

## 15. Deployment-model decision

Vyhodnoť:

1. latency a locality;
2. data residency a regulation;
3. connected/disconnected behavior;
4. hardware a licensing constraints;
5. workload variability a capacity;
6. team operations maturity;
7. identity a data integration;
8. failure domains a RPO/RTO;
9. TCO a data transfer;
10. exit, failback a decommission.

Rozhodnutie rob per capability alebo component, nie iba raz pre celú organizáciu.

## 16. Anti-patterny

### Private cloud rovná sa virtualizácia

Bez API, self-service, policy, metering a lifecycle ownershipu chýba cloud operating model.

### Hybrid cloud rovná sa VPN

VPN rieši iba časť packet pathu. Identity, DNS, data, management, observability a recovery zostávajú nevyriešené.

### Public endpoint znamená verejné dáta

Exposure závisí od routing, resource policy, identity, TLS a application authorization.

### Multi-cloud je automatický DR

Bez deployable artifacts, data, identity, capacity a testovaného failoveru je druhý provider iba potenciálna lokalita.

### Central dashboard znamená central control

Dashboard môže byť stale alebo nedostupný; lokálna authority a disconnected behavior musia byť explicitné.

## 17. Kontrolné otázky

1. Aký je rozdiel medzi service a deployment modelom?
2. Čo tvorí exact hybrid-flow subject?
3. Prečo green circuit nepreukazuje funkčný application round trip?
4. Ktoré layers musí hybrid operating model zosúladiť?
5. Ako sa líši synchronous a asynchronous hybrid data contract?
6. Čo musí fungovať pri disconnected operation?
7. Prečo private cloud nie je automaticky bezpečnejší?
8. Kedy je multi-cloud skutočný recovery mechanism?
9. Čo tvorí portability subject?
10. Ako uzavrieš hybrid incident bez broad security bypassu?

## Glossary impact

Relevantné pojmy: cloud deployment subject, public-cloud control boundary, private-cloud operating model, hybrid capability subject, hybrid flow subject, connected/disconnected behavior, authoritative hybrid identity, hybrid DNS authority, hybrid data generation, per-prefix route contract, multi-cloud recovery subject, edge autonomy a deployment-model acceptance verdict.

## Oficiálna dokumentácia

- [Types of cloud computing](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/types-of-cloud-computing.html)
- [Cloud deployment strategies](https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-education-hybrid-multicloud/cloud-deployment-strategies.html)
- [Hybrid cloud best practices](https://docs.aws.amazon.com/prescriptive-guidance/latest/hybrid-cloud-best-practices/overview.html)
- [Hybrid Cloud with AWS](https://docs.aws.amazon.com/whitepapers/latest/hybrid-cloud-with-aws/hybrid-cloud-with-aws.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: IaaS, PaaS a SaaS](iaas-paas-saas.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Regions a Availability Zones →](regions-availability-zones.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
