# AWS service, deployment, placement and responsibility lifecycle glossary entries

## AWS capability subject

Versionovaná identita cloudovej business capability zahŕňajúca account, Region, resources, application artifact, configuration, credential a data generations spolu s požadovaným business outcome-om. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Cloud service-model subject

Konkrétny service contract viazaný na business capability, provider/customer responsibility boundary, effective configuration, evidence, recovery a exit model; nie iba označenie IaaS, PaaS alebo SaaS. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Responsibility contract — cloud service

Explicitné rozdelenie provisioning, patching, identity, data, observability, availability, recovery a decommission responsibilities medzi providera, zákazníka a shared integration boundary. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Managed-service outcome boundary

Hranica medzi provider-managed platform health a zákazníckym application, data a business outcome-om; healthy managed service nepreukazuje správnu schema, access, restore ani user journey. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Service health verdict

Provider alebo platformový verdict o stave služby, ktorý musí byť korelovaný s customer configuration, runtime, data a business evidence a sám neuzatvára workload incident. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Service-model acceptance verdict

Closure podmienka dokazujúca, že zvolený service model spĺňa required availability, security, recovery, observability, cost a portability outcomes pri správnom rozdelení responsibilities. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Service-model exit subject

Inventár artifacts, data formats, identities, keys, network assumptions, telemetry, runbookov, commercial constraints a času potrebný na migráciu alebo ukončenie cloudovej služby. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Cloud deployment subject

Versionovaná identita umiestnenia capability zahŕňajúca public/private/hybrid domains, accounts, sites, networks, identity, DNS, connectivity, data a management generations. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Hybrid capability subject

Business capability rozdelená medzi cloud a private/edge prostredie s explicitným ownershipom identity, DNS, data, connectivity, telemetry a connected/disconnected behavioru. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Hybrid flow subject

Exact network a identity path zahŕňajúci source workload, IP/port, routes, gateway/tunnel/circuit, firewall, destination, return path, TLS a application authorization. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Per-prefix route contract

Hybridný routing invariant určujúci, ktoré source a destination prefixes musia byť propagované, akceptované a symetricky routované cez primary a recovery paths. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Hybrid DNS authority

Versionovaný contract určujúci authoritative zones, conditional forwarding, resolver endpoints, split-horizon behavior, TTL, overlapping namespaces a disconnected failure behavior. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Hybrid data generation

Identita authoritative data state-u a jeho replication checkpointu, lag-u, ordering-u, conflict modelu, failover a reconciliation stavu naprieč cloud a private domains. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Connected/disconnected behavior

Explicitný contract určujúci, ktoré workload, identity, data a management operations pokračujú, fail-closed alebo sa bufferujú pri strate WAN alebo central cloud control plane-u. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Deployment-model acceptance verdict

Closure dôkaz, že public/private/hybrid placement spĺňa povolené flows, zakázané flows, data consistency, autonomous behavior, failover/failback a business outcome. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## AWS placement subject

Exact account, Region, AZ ID, subnet, resource, release, data a capacity identity použitá na rozhodovanie o umiestnení a failure-domain recovery. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Failure-mode capacity

Kapacita, quota, IP space a compatible resource inventory dostupný po strate definovaného failure domainu, nie iba počas healthy steady state-u. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Zonal egress subject

Per-AZ NAT, endpoint, route a source-subnet contract, ktorého zlyhanie môže odstaviť dependency access aj pri healthy compute a regional service control plane. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Per-AZ endpoint cohort

Skupina application, load-balancer alebo service endpoints klasifikovaná podľa AZ ID a generation na rozlíšenie regionálneho od zonálneho failure-u. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Multi-AZ acceptance verdict

Dôkaz, že surviving Availability Zones majú compute, IP, egress, data, endpoint, quota a deployment capacity a udržia business outcome po strate jednej AZ. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Recovery-Region subject

Versionovaný inventár account/Region enablementu, services, quotas, capacity, artifacts, identity, KMS, networking, data recovery pointu, telemetry a traffic/failback runbooku. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## AWS responsibility subject

Konkrétny account, Region, service/resource, feature, configuration, principal, data a requested outcome, ku ktorému sa viaže provider/customer/shared responsibility verdict. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Shared-control interface

Presné rozhranie, kde provider dodáva capability a zákazník vlastní activation, configuration, identity, monitoring, evidence alebo recovery use; shared neznamená nejasného ownera. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Responsibility evidence

Provider a customer dôkazy potrebné na preukázanie effective controlu, napríklad AWS compliance evidence, CloudTrail request, versionovaná policy, configuration test, restore report a business synthetic. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Responsibility RACI — cloud

Service-specific mapping controlu na provider capability, customer ownera, evidence ownera, recovery ownera a escalation boundary. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Provider-trigger/customer-amplifier incident

Incident, pri ktorom provider failure alebo degradation spustí udalosť, ale customer architecture, capacity, configuration alebo recovery weakness zväčší business blast radius. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Shared-control closure verdict

Dôkaz, že provider capability, customer configuration, monitoring, recovery a forbidden-outcome controls spolu dosiahli požadovaný security alebo business outcome. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).
