# Cloud and AWS

Táto sekcia vysvetľuje cloud computing od service a deployment modelov cez global infrastructure, shared responsibility a high availability až po AWS accounts, identity, networking, compute, storage, databases, observability, security, cost a disaster recovery.

Cieľom nie je memorovať názvy AWS služieb. Každá téma má vysvetliť ownership boundary, control plane, data plane, failure domains, security model, cost drivers a troubleshooting evidence.

## Predpoklady

Odporúča sa najprv dokončiť:

- [DevOps Foundations](../00-foundations/README.md),
- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md),
- [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md),
- [Kubernetes](../09-kubernetes/README.md).

## Odporúčané poradie

1. [IaaS, PaaS a SaaS](iaas-paas-saas.md)
2. [Public, private a hybrid cloud](public-private-hybrid-cloud.md)
3. [Regions a Availability Zones](regions-availability-zones.md)
4. [Shared responsibility model](shared-responsibility-model.md)
5. [Scalability, elasticity a fault tolerance](scalability-elasticity-fault-tolerance.md)
6. [High availability a disaster recovery](high-availability-disaster-recovery.md)
7. [AWS Organizations a accounts](aws-organizations-accounts.md)

Nasledujúci blok prejde na AWS identity a network foundation: IAM principals, policies a roles, STS a federation, VPC, subnets, routing, security groups, NACLs a hybrid connectivity.

## Cieľ zvládnutia

Po dokončení aktuálneho bloku má byť možné:

- vysvetliť cloud service model ako responsibility boundary,
- rozlíšiť IaaS, PaaS a SaaS podľa toho, kto vlastní jednotlivé vrstvy,
- identifikovať zákaznícke responsibilities aj pri managed a SaaS službách,
- rozlíšiť replication, durability, availability, backup a business continuity,
- vyhodnotiť service model podľa control, toil, TCO, lock-in, portability, compliance a recovery požiadaviek,
- vytvoriť responsibility matrix pre konkrétnu službu,
- diagnostikovať incident podľa customer, provider a shared integration boundary,
- rozlíšiť service model od deployment modelu,
- vysvetliť public, private, hybrid, edge a multi-cloud model bez zamieňania network exposure a ownershipu,
- navrhnúť hybrid connectivity, identity, DNS, data a management boundary,
- vyhodnotiť cloud portability podľa source, runtime, data, identity, networking a operations vrstvy,
- rozpoznať, kedy virtualizované dátové centrum nespĺňa cloud operating model,
- vysvetliť AWS Region a Availability Zone ako odlišné fault-isolation boundaries,
- rozlíšiť regional, zonal a global resource scope,
- používať AZ ID namiesto AZ letter pri cross-account koordinácii,
- navrhnúť Multi-AZ architektúru s capacity headroom, health routing a state failoverom,
- rozlíšiť Multi-AZ od cross-Region recovery a zohľadniť replication lag, capacity a data-transfer trade-offy,
- diagnostikovať nesprávny Region, zonal capacity, subnet/IP a single-AZ dependency problémy,
- vysvetliť security of the cloud a security in the cloud,
- vytvoriť service-specific shared-responsibility matrix pre compute, networking, identity, data, encryption, logging, patching a recovery,
- rozlíšiť provider compliance controls od zákazníckeho workload compliance,
- určiť zákaznícke responsibilities pri EC2, managed database, serverless a SaaS modeloch,
- pripraviť evidence-rich provider support case a oddeliť customer, provider a shared failure boundary,
- rozlíšiť scalability, elasticity a fault tolerance,
- navrhnúť vertical, horizontal alebo diagonal scaling podľa bottlenecku,
- používať správny scaling signal, scale-in protection, backpressure a queue-based load leveling,
- vysvetliť active-active, active-passive, retry budget, circuit breaker, bulkhead a graceful degradation,
- testovať capacity, quotas, zonal failure a autoscaling pod burstom alebo dependency slowdownom,
- rozlíšiť high availability od disaster recovery,
- definovať BIA, RTO, RPO, RTA a RPA,
- navrhnúť backup and restore, pilot light, warm standby alebo active-active recovery stratégiu,
- oddeliť backup, replication a kompletný DR operating model,
- navrhnúť failover, authoritative-state, DNS/routing a failback proces,
- testovať recovery cez tabletop, component restore, isolated restore a kontrolovaný failover,
- vysvetliť AWS account ako resource, IAM, quota, billing a blast-radius boundary,
- navrhnúť AWS Organizations hierarchy cez management account, root, OUs a member accounts,
- používať SCP ako permissions guardrail, nie ako grant,
- vysvetliť SCP inheritance, deny-list a allow-list trade-offy a management-account výnimku,
- navrhnúť account vending, federovaný workforce access, delegated administration a cross-account role model,
- oddeliť log archive, security tooling, network, shared services, production, sandbox a quarantine accounts,
- vykonať bezpečný account decommissioning a break-glass access test.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| IaaS, PaaS a SaaS | Learning | L2 |
| Public, private a hybrid cloud | Learning | L2 |
| Regions a Availability Zones | Learning | L2 |
| Shared responsibility model | Learning | L2 |
| Scalability, elasticity a fault tolerance | Learning | L2 |
| High availability a disaster recovery | Learning | L2 |
| AWS Organizations a accounts | Learning | L2 |