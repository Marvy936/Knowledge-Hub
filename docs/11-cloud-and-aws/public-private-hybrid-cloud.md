# Public, private a hybrid cloud

Cloud deployment model opisuje, **kde a pod čou kontrolou** bežia compute, storage, networking a platform services a ako sa prepájajú s ostatnými prostrediami. Nie je to to isté ako service model IaaS, PaaS alebo SaaS. Public cloud môže poskytovať všetky tri service modely; private cloud môže rovnako poskytovať vlastné IaaS alebo PaaS capabilities.

## 1. Deployment model a service model

Rozlišuj dve osi:

```text
service model   → ktorú technologickú vrstvu spravuje provider a ktorú zákazník
                  IaaS / PaaS / SaaS

deployment model → kde infraštruktúra beží, komu je určená a ako je riadená
                   public / private / hybrid / multi-cloud
```

Príklady:

- EC2 v AWS public cloude je IaaS,
- RDS v AWS public cloude je managed database/PaaS-like service,
- interný OpenStack môže byť private-cloud IaaS,
- SaaS aplikácia môže používať public cloud a súčasne private connectivity k zákazníkom.

## 2. Public cloud

Public cloud poskytuje zdielané provider-managed infrastructure a services viacerým zákazníkom cez logicky izolované účty, tenants, identities a virtual networks.

Typické vlastnosti:

- on-demand provisioning cez API,
- pay-as-you-go alebo commitment pricing,
- provider-owned physical facilities a hardware,
- veľký katalóg managed services,
- globálna infraštruktúra,
- elasticita a automatizácia,
- zákaznícka zodpovednosť za konfiguráciu, identity, data a workload security.

„Public“ neznamená, že workload alebo dáta musia byť verejne dostupné na internete. VPC, private subnets, private endpoints, encryption a identity policies môžu vytvoriť neverejný workload v public-cloud infraštruktúre.

## 3. Multi-tenancy

Provider typicky zdieľa fyzickú infraštruktúru medzi zákazníkmi a používa isolation controls:

- hypervisor alebo hardware isolation,
- tenant/account identity,
- virtual networking,
- encryption,
- service-level authorization,
- resource quotas a control-plane boundaries.

Zákazník musí stále overiť:

- service isolation contract,
- compliance eligibility,
- data residency,
- encryption a key ownership,
- noisy-neighbor a capacity behavior,
- dedicated-host alebo single-tenant možnosti, ak sú potrebné.

## 4. Private cloud

Private cloud je cloud-like platforma určená jednej organizácii. Môže bežať:

- vo vlastnom dátovom centre,
- v colocation,
- na dedicated provider infraštruktúre,
- ako appliance alebo cloud extension na zákazníckej lokalite.

Private cloud nie je iba virtualizované dátové centrum. Cloud operating model potrebuje:

- self-service provisioning,
- API a automation,
- štandardizované resource templates,
- metering/showback alebo chargeback,
- policy enforcement,
- elastic alebo pool-based capacity management,
- platform lifecycle a service ownership.

Bez týchto vlastností ide skôr o tradičnú virtualizačnú platformu než plnohodnotný cloud model.

## 5. Výhody private cloudu

Môže byť vhodný pri:

- prísnej physical/data-location kontrole,
- legacy hardware alebo specialized devices,
- nízkej a predvídateľnej latency k lokálnym systémom,
- disconnected alebo air-gapped prostredí,
- regulatorných požiadavkách,
- stabilnom veľkom workload-e s efektívne využitou vlastnou kapacitou,
- potrebe vlastného hypervisor/kernel/network stacku.

Výhoda existuje iba vtedy, keď organizácia dokáže infraštruktúru bezpečne financovať, kapacitne plánovať, patchovať a prevádzkovať.

## 6. Náklady private cloudu

Zahrň:

- hardware a refresh cyklus,
- dátové centrum, napájanie a chladenie,
- network connectivity,
- software licencie a support,
- spare capacity pre failure a growth,
- platform engineering,
- security a compliance operations,
- backup a DR,
- 24/7 incident response,
- decommissioning.

Nízky účet za prenájom hardware neznamená nízke TCO.

## 7. Hybrid cloud

Hybrid cloud integruje public-cloud resources so systémami mimo public cloudu, typicky on-premises alebo edge infraštruktúrou.

Integrácia môže zahŕňať:

- networking,
- identity federation,
- DNS,
- data replication alebo transfer,
- management a observability,
- security policy,
- deployment pipeline,
- backup a disaster recovery.

Hybrid cloud nie je iba VPN tunel. Je to dlhodobý operating model dvoch alebo viacerých rozdielnych failure, identity a lifecycle domains.

## 8. Hybrid connectivity

Bežné možnosti:

### Site-to-site VPN

Encrypted tunnel cez verejný internet.

Trade-offy:

- rýchle nasadenie,
- závislosť od internet paths,
- variabilná latency,
- throughput a tunnel limits,
- potreba redundantných tunnels a gateways.

### Dedicated connectivity

Napríklad AWS Direct Connect cez partnera alebo colocation.

Trade-offy:

- stabilnejšia kapacita a routing,
- dlhší provisioning,
- physical a provider dependencies,
- dedicated link sám nezaručuje encryption,
- potreba redundantných lokalít, zariadení a circuits.

### Public service endpoints

On-premises workload komunikuje s public API endpointom cez internet alebo provider edge.

### Private service endpoints

Private connectivity k provider službe bez bežného public-internet routing modelu podľa konkrétnej služby.

## 9. Hybrid identity

Model môže používať:

- federáciu workforce identities,
- workload identity federation,
- directory integration,
- certificate-based machine identity,
- krátkodobé cloud credentials,
- centralized alebo delegated authorization.

Anti-pattern je synchronizovať dlhodobé access keys do on-premises systémov bez rotation a scope-u.

## 10. Hybrid DNS

Treba navrhnúť:

- authoritative zones,
- conditional forwarding,
- split-horizon records,
- inbound a outbound resolver endpoints,
- failure behavior pri strate linky,
- TTL a caching,
- overlapping namespaces.

DNS dependency môže znefunkčniť hybrid workload aj vtedy, keď network route a firewall fungujú.

## 11. Hybrid data

Rozlišuj:

- synchronous a asynchronous replication,
- bulk transfer,
- event streaming,
- cache,
- authoritative data source,
- conflict resolution,
- data residency,
- RPO/RTO,
- egress cost.

Synchronous cross-environment write môže zvýšiť latency a vytvoriť spoločný failure domain. Asynchronous model potrebuje pracovať so stale data a recovery lagom.

## 12. Hybrid management

Jednotný dashboard neznamená jednotnú control plane.

Potrebné je vedieť:

- kto vlastní source of truth,
- ktoré policies sú centrálne a ktoré lokálne,
- ako sa distribuujú updates,
- ako funguje inventory,
- ako sa korelujú logs a identities,
- čo sa stane pri strate cloud alebo WAN connectivity,
- či lokálne workloady pokračujú autonómne.

## 13. Edge cloud

Edge umiestňuje compute alebo storage bližšie k zariadeniam, používateľom alebo výrobnému procesu.

Dôvody:

- nízka latency,
- obmedzená alebo prerušovaná WAN konektivita,
- lokálne spracovanie dát,
- data sovereignty,
- vysoký objem raw telemetry.

Edge potrebuje:

- fleet management,
- offline behavior,
- secure bootstrap,
- remote update a rollback,
- hardware replacement,
- local observability buffer,
- conflict a synchronization model.

## 14. Multi-cloud

Multi-cloud používa služby od viacerých cloud providers. Nie je automaticky hybrid cloud, hoci modely sa môžu prekrývať.

Dôvody:

- regulačné alebo zákaznícke požiadavky,
- best-of-breed service,
- merger/acquisition,
- geographic availability,
- komerčná vyjednávacia pozícia,
- provider concentration risk.

Náklady:

- viac IAM a network modelov,
- duplikované platform tooling,
- skills fragmentation,
- observability a incident complexity,
- data egress,
- slabší leverage managed services pri lowest-common-denominator dizajne.

Multi-cloud nie je automatický DR. Workload musí byť reálne deployovateľný, data musia byť obnoviteľné a failover musí byť testovaný.

## 15. Cloud bursting

Cloud bursting presúva alebo rozširuje workload z private prostredia do public cloudu pri špičke.

Praktické prekážky:

- image/runtime parity,
- data locality,
- identity a secrets,
- network capacity,
- licensing,
- autoscaling latency,
- observability,
- stateful workloady.

Je vhodnejší pre stateless alebo batch workloady s prenositeľnými vstupmi než pre latency-sensitive stateful systémy.

## 16. Portability

Portability vrstvy:

- source code,
- container image,
- infrastructure manifest,
- data format,
- identity model,
- network assumptions,
- observability,
- operational runbooks.

Container image sám negarantuje portability. Workload môže závisieť od provider database, IAM, object storage semantics, queue, KMS alebo load-balancer capabilities.

## 17. Deployment model nie je security level

Public cloud nie je automaticky menej bezpečný a private cloud nie je automaticky bezpečnejší.

Security závisí od:

- identity a authorization,
- network segmentation,
- patching,
- encryption,
- logging a detection,
- supply chain,
- backup/recovery,
- physical controls,
- operational maturity.

Private platform bez patchingu a monitoringu môže mať vyššie riziko než správne nakonfigurovaná managed služba.

## 18. Výber deployment modelu

Vyhodnoť:

1. latency a locality,
2. data residency a regulation,
3. connectivity a offline requirements,
4. hardware alebo license dependencies,
5. workload variability,
6. platform skills a operations capacity,
7. TCO a opportunity cost,
8. RPO/RTO a failure domains,
9. portability a exit plan,
10. modernization roadmap.

Rozhodnutie môže byť per workload alebo per component, nie iba jedno pre celú organizáciu.

## 19. Troubleshooting hybridného prostredia

Postup:

```text
source workload
→ local DNS/identity
→ local routing/firewall
→ WAN/VPN/dedicated link
→ cloud edge/gateway
→ VPC route/security
→ service endpoint
→ destination workload
→ return path
```

Zachovaj:

- timestamps v UTC,
- source/destination IP a port,
- route tables,
- tunnel/BGP state,
- DNS odpovede,
- authentication request ID,
- packet/flow logs,
- configuration changes,
- provider status.

## 20. Anti-patterny

### Private cloud = virtualizácia

Bez API, self-service, policy a lifecycle automation nevzniká cloud operating model.

### Hybrid = jedna VPN

Chýba identity, DNS, data, observability a recovery model.

### Multi-cloud = automatická odolnosť

Bez deploy, data a failover capability je druhý provider iba nevyužitá možnosť.

### Public endpoint = verejné dáta

Exposure závisí od routing, authorization a service policy, nie iba od deployment modelu.

### Lowest-common-denominator architecture

Môže odstrániť hodnotu managed služieb a zároveň nezabezpečiť skutočnú portability.

## 21. Kontrolné otázky

1. Aký je rozdiel medzi service a deployment modelom?
2. Prečo public cloud neznamená verejne dostupný workload?
3. Kedy je virtualizačná platforma private cloudom?
4. Ktoré vrstvy musí riešiť hybridný operating model?
5. Aký je rozdiel medzi VPN a dedicated connectivity?
6. Prečo synchronous hybrid data model zväčšuje failure domain?
7. Prečo container image negarantuje cloud portability?
8. Je private cloud automaticky bezpečnejší?
9. Prečo multi-cloud nie je automatický DR?
10. Aký troubleshooting chain použiješ pri hybridnom výpadku?

## Glossary impact

Relevantné pojmy: cloud deployment model, public cloud, private cloud, hybrid cloud, multi-cloud, edge cloud, cloud bursting, hybrid connectivity, dedicated connectivity, cloud portability, data locality a disconnected operation.

## Oficiálna dokumentácia

- [Types of cloud computing](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/types-of-cloud-computing.html)
- [Hybrid Cloud with AWS](https://docs.aws.amazon.com/whitepapers/latest/hybrid-cloud-with-aws/hybrid-cloud-with-aws.html)
- [Hybrid cloud best practices](https://docs.aws.amazon.com/prescriptive-guidance/latest/hybrid-cloud-best-practices/overview.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: IaaS, PaaS a SaaS](iaas-paas-saas.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Regions a Availability Zones →](regions-availability-zones.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
