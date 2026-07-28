# AWS networking and fleet lifecycle glossary entries

## AWS network-generation subject

Versionovaný AWS network subject obsahujúci account, Region, VPC CIDRs, subnet/AZ inventory, ENIs, route-table associations, gateway/endpoint attachments, policy generations a DNS/observation contract. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## VPC address-to-route lifecycle

Chain `network outcome → VPC/CIDR generation → zonálny subnet a ENI → effective route-table association → selected route → gateway/endpoint target → forward/return path → security a application verification`. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Subnet placement subject — AWS

Exact subnet identity vrátane VPC, AZ, IPv4/IPv6 prefixes, available IP headroom, route-table association, NACL, endpoint/gateway dependencies a workload cohorts, ktoré do subnetu môžu byť umiestnené. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## ENI identity subject

Elastic network interface identity zahŕňajúca ENI ID, private/public addresses, subnet/AZ, Security Groups, attachment, MAC a flow-log observation fields. Instance alebo managed-service lifecycle nemusí byť totožný s ENI lifecycle-om. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Effective route-table association

Route table, ktorú subnet skutočne používa po explicitnej asociácii alebo inheritance z main route table; subnet tag alebo diagram ju nenahrádza. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Selected route subject — AWS

Pre konkrétnu destination IP úplný súbor matching routes, longest-prefix/priority verdict, route origin a výsledný target ID/stav. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Route origin — AWS VPC

Pôvod route, napríklad local, static alebo propagated, ktorý ovplyvňuje ownership, priority, change path a recovery evidence. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Forward/return path contract — AWS

Požiadavka, aby presný flow mal kompatibilnú route, policy a stateful-inspection cestu v oboch smeroch; forward reachability sama connection nepreukazuje. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Subnet IP headroom

Voľná použiteľná IP/ENI capacity po zohľadnení reserved addresses, steady state-u, load balancerov, endpoints, Pods, managed services a rollout/failover replacementu. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## VPC flow acceptance verdict

Closure, pri ktorom selected route, forward/return path, SG/NACL/firewall rules, DNS, listener/TLS a application/business request preukazujú očakávaný allowed flow aj forbidden paths. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Internet-egress subject — AWS

Exact outbound flow identity obsahujúca source ENI/subnet/AZ, selected route, IGW/NAT identity, original a translated tuple, destination/DNS/TLS identity, connection generation a business operation. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## NAT connectivity type

Vlastnosť rozlišujúca public NAT Gateway pre internet-routable translation a private NAT Gateway pre private/transit communication use cases. Nie je totožná s availability mode-om. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## NAT availability mode

Vlastnosť rozlišujúca zonal single-AZ a regional multi-AZ NAT Gateway model. Availability mode nehovorí, či connectivity type je public alebo private. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Zonal NAT Gateway subject

NAT Gateway generation s konkrétnou AZ, subnetom, private/public addresses, route dependencies, connection capacity a source-subnet cohorts. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Regional NAT Gateway subject

Logical multi-AZ NAT Gateway generation s AZ coverage, per-AZ addresses/EIPs, auto-provision alebo explicit coverage policy, routes a operational evidence. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Translated flow subject — AWS NAT

Original source/destination tuple spolu s NAT public/private addressom, translated source portom, destination tuple, connection state a reverse mappingom. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## NAT address generation

Aktuálny súbor private/public NAT addresses a AZ coverage, ktorý určuje source identity pozorovanú destination service-om a musí byť zosúladený s allowlists. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Destination-tuple concentration

Sústredenie veľkého počtu concurrent alebo short-lived connections na rovnaký destination IP, port a protocol, ktoré môže vytvoriť NAT source-port pressure aj pri nízkom bandwidth-e. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## NAT port-allocation verdict

Evidence založená na `ErrorPortAllocation`, connection counts, destination concentration, application retries/pooling a request timeline, že NAT nedokázal alokovať ďalší translated source port. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Egress AZ coverage

Zoznam source AZ cohorts, ktoré majú accepted NAT/IGW/endpoint path, address identity a failure behavior; logical regional resource alebo healthy jedna AZ nepokrýva automaticky všetky cohorts. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Partner allowlist boundary

External authorization boundary, pri ktorej partner rozhoduje podľa translated public source IP alebo inej egress identity; zmena NAT/EIP generation môže znefunkčniť technicky zdravý path. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## VPC flow-policy subject

Exact communication subject obsahujúci source/destination ENI a subnet identities, original/translated tuple, route, SG sets, NACL generations, connection state, listener/TLS identity a business request. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## SG effective allow graph

Aditívny súbor applicable inbound/outbound Security Group rules, referenced SG membership, prefix lists a ENI associations, ktorý povoľuje nový flow na konkrétnej direction a porte. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## SG membership inventory

Aktuálny zoznam ENIs/resources reprezentovaných referencovanou Security Groupou; broad alebo zmenené membership môže rozšíriť access bez zmeny rule textu. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Tracked connection subject — Security Group

Established flow rozpoznaný SG connection trackingom podľa relevantného tuple/state-u, odlišný od fresh connection attemptu po policy zmene. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Fresh-flow revocation test

Negatívne overenie, že po odstránení allow pathu nový connection attempt zlyhá, oddelene od testu existujúcich long-lived alebo pooled sessions. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## NACL ordered-policy generation

Kompletný inbound/outbound NACL ruleset vrátane rule numbers, CIDRs, protocols, ports, verdictov a subnet associations; first-match semantics znamená, že poradie je súčasťou policy. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Stateless return-path contract — NACL

Explicitné rules potrebné pre response direction vrátane client ephemeral destination ports, pretože NACL nepozná stav pôvodnej connection. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Policy observation point — AWS network

Presná enforcement/telemetry boundary, na ktorej sú viditeľné konkrétne addresses, ports, direction a pre/post-NAT identity; verdict z iného bodu nemusí patriť rovnakému flow subjectu. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Load-balancer dual-connection subject

Oddelené identity pre `client → load balancer` a `load balancer → target`, z ktorých každá má vlastné route, SG, NACL, port, health a return-path evidence. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Emergency deny lifecycle — AWS network

Coarse subnet alebo central-policy deny s ownerom, scope-om, expiry, management/recovery-access validation, rollbackom a post-incident drift cleanupom. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## EC2 fleet-realization subject

Exact ASG/fleet identity vrátane desired boundaries, launch template version, AMI, instance types, subnets, SG, role, EBS/KMS, bootstrap, health, target and business generations. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Immutable launch subject — EC2

Pinned launch template version, AMI/provenance, user-data digest, network/storage/IAM configuration a purchase/placement constraints, ktoré reprodukovateľne vytvárajú jednu instance generation. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Launch-template version closure

Dôkaz, že ASG, refresh a každá target instance používajú explicitne schválenú launch template version; `$Latest` alebo uncontrolled `$Default` closure nespĺňajú. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Effective machine generation — EC2

Výsledná machine/application generation vytvorená z AMI, launch template-u, user data, reachable artifacts, retrieved configuration/secrets a runtime service startupu. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Serving-capacity realization — ASG

Prechod `desired → launched → running → bootstrapped → healthy/registered → traffic-accepting → business-capable`, ktorý odlišuje fleet count od reálnej kapacity. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## ASG reconciliation subject

Auto Scaling Group desired state, current instance/lifecycle inventory, health sources, scaling activities, suspended processes a launch/termination decisions pre jednu fleet generation. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Health-source chain — EC2 Auto Scaling

Poradie EC2 system/instance statusu, ASG health, optional ELB/EBS/VPC Lattice/custom checks, target readiness, application health a business request evidence. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Replacement-loop subject — ASG

Opakovaný chain `launch → bootstrap/health failure → terminate → replacement`, identifikovaný exact launch generation, target-health reason, grace/warmup a scaling activity evidence. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Instance-refresh transition subject

Source a target fleet cohorts, exact launch generations, healthy-capacity preferences, warmup, checkpoints, skip-matching, rollback eligibility a business acceptance jedného refreshu. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Lifecycle-hook operation subject — ASG

Logical launch alebo termination side effect viazaný na instance ID, transition, hook name, operation/idempotency key, heartbeat, timeout, durable result a retry attempts. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Scale-out downstream envelope

Maximum fleet concurrency, connections, requests alebo work claims, ktoré downstream database, queue, partner alebo network path bezpečne absorbuje počas scale-out-u. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Fleet recovery closure — EC2

Verdict, že ASG používa approved launch generation, desired/InService/serving capacity je kompatibilná, všetky AZ cohorts prešli health/business tests, bad generation je retired a druhý scale/refresh cyklus nereprodukuje failure. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).
