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

Nasledujúci blok doplní public/private/hybrid cloud, Regions a Availability Zones, shared responsibility, scalability/elasticity/fault tolerance, high availability/disaster recovery a AWS Organizations/accounts.

## Cieľ zvládnutia

Po dokončení aktuálneho bloku má byť možné:

- vysvetliť cloud service model ako responsibility boundary,
- rozlíšiť IaaS, PaaS a SaaS podľa toho, kto vlastní jednotlivé vrstvy,
- identifikovať zákaznícke responsibilities aj pri managed a SaaS službách,
- rozlíšiť replication, durability, availability, backup a business continuity,
- vyhodnotiť service model podľa control, toil, TCO, lock-in, portability, compliance a recovery požiadaviek,
- vytvoriť responsibility matrix pre konkrétnu službu,
- diagnostikovať incident podľa customer, provider a shared integration boundary.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| IaaS, PaaS a SaaS | Learning | L2 |
