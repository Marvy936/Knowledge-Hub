# VPC, subnets a route tables

Amazon Virtual Private Cloud (VPC) je logicky izolovaný network scope v jednom AWS Regione. VPC neurčuje iba IP rozsah. Definuje routing boundary, subnet placement, DNS behavior, connectivity targets, security enforcement points a observability surface pre resources používajúce VPC networking.

## 1. Regionálny a zonálny scope

- VPC je regional resource.
- Subnet je viazaný na jednu Availability Zone.
- Route table je VPC resource asociovaný so subnetmi alebo vybranými gateways.
- Elastic network interface (ENI) je zonálny network object.

Multi-AZ workload preto potrebuje subnet v každej používanej AZ a zodpovedajúce route, capacity a dependency modely.

## 2. CIDR plánovanie

Pri návrhu VPC vyber:

- IPv4 CIDR,
- voliteľný IPv6 CIDR,
- subnet segmentation,
- growth headroom,
- hybrid a peering overlap risk,
- future acquisitions/regions/accounts,
- IPAM ownership.

Prekrývajúce sa CIDR komplikujú alebo blokujú routing cez VPC peering, Transit Gateway, VPN a Direct Connect.

## 3. Subnet

Subnet je contiguous IP rozsah v jednej AZ. Označenie public/private nie je intrinsic field.

Subnet sa prakticky považuje za:

- **public**, ak jeho route table poskytuje internet path a resource má vhodnú public addressing/security konfiguráciu,
- **private**, ak nemá priamu inbound internet path,
- **isolated**, ak nemá ani general outbound internet path.

Názov subnetu sám connectivity nemení.

## 4. Reserved IP addresses

AWS rezervuje časť adries v každom IPv4 subnet CIDR. Capacity planning musí pracovať s reálne použiteľnými adresami a ENI consumption, nie iba s veľkosťou CIDR.

IP pressure môžu vytvoriť:

- EC2 instances,
- load balancer nodes,
- NAT alebo interface endpoints,
- EKS Pods pri VPC CNI modeli,
- RDS/managed service ENIs,
- failover a scaling headroom.

## 5. VPC router

Každý VPC má implicitný router. Route tables určujú destination-to-target rozhodnutia.

Route obsahuje:

```text
destination CIDR/prefix list
→ target
```

Target môže byť napríklad:

- `local`,
- Internet Gateway,
- NAT Gateway,
- Transit Gateway,
- virtual private gateway,
- VPC peering connection,
- network interface,
- Gateway Load Balancer endpoint,
- egress-only Internet Gateway.

## 6. Local route

VPC route table obsahuje local route pre VPC CIDR. Umožňuje routing medzi subnetmi v rámci VPC, pokiaľ traffic neblokuje security alebo resource behavior.

Subnety nie sú automaticky security-isolated iba preto, že používajú rozdielne route tables.

## 7. Longest prefix match

Pri viacerých matching routes sa používa najšpecifickejší destination prefix.

Príklad:

```text
10.0.0.0/8   → transit gateway
10.20.0.0/16 → peering connection
```

Traffic na `10.20.5.10` použije `/16` route.

Pri rovnako špecifických routes rozhodujú service-specific priority pravidlá; návrh nemá závisieť od nejasnej duplicity.

## 8. Main a custom route table

Každý VPC má main route table.

- Subnet bez explicitnej asociácie používa main route table.
- Subnet môže byť asociovaný iba s jednou subnet route table naraz.
- Jedna route table môže obsluhovať viac subnetov.

Production návrh typicky používa explicitné custom route tables podľa tieru/AZ, aby zmena main table nespôsobila nečakaný blast radius.

## 9. Public subnet path

Pre IPv4 internet connectivity EC2 instance typicky potrebuje:

```text
subnet route 0.0.0.0/0 → Internet Gateway
+ public IPv4 alebo Elastic IP
+ security group/NACL allow
+ application listener
```

Chýbajúci ktorýkoľvek prvok spôsobí failure.

## 10. Private subnet egress

Private subnet môže používať:

- NAT Gateway pre IPv4 outbound,
- egress-only Internet Gateway pre IPv6 outbound-only model,
- VPC endpoints pre private service access,
- proxy/firewall appliance,
- Transit Gateway/VPN/Direct Connect do central egressu.

NAT nie je potrebný pre každý AWS service call, ak existuje vhodný VPC endpoint.

## 11. IPv6

IPv6 adresy sú global unicast a nepoužívajú IPv4-style public NAT ako základný model.

Možnosti:

- Internet Gateway pre inbound/outbound internet path podľa security controls,
- egress-only Internet Gateway pre outbound-initiated connectivity,
- route a NACL rules s IPv6 CIDRs,
- dual-stack DNS a application support.

IPv4 a IPv6 route/security paths treba testovať oddelene.

## 12. Route propagation

Vybrané gateways môžu propagovať routes do route table, napríklad virtual private gateway pri VPN/Direct Connect modeloch.

Over:

- ktoré routes sú static a propagated,
- BGP preference a prefixes,
- overlap,
- failover behavior,
- route limits.

Propagation nezaručuje return-path symmetry.

## 13. VPC peering

VPC peering poskytuje private routing medzi dvoma VPCs.

Hranice:

- nie je transitive,
- CIDRs sa nesmú prekrývať,
- route tables musia obsahovať paths na oboch stranách,
- security groups/NACLs a DNS behavior treba nakonfigurovať,
- scale pri full-mesh topológii je slabý.

## 14. Transit Gateway

Transit Gateway centralizuje connectivity pre viac VPCs a hybrid networks.

Obsahuje vlastné attachment a route-table concepts. Potrebuje:

- segmentation,
- propagation/association design,
- asymmetric-routing kontrolu,
- appliance mode podľa topológie,
- cross-account governance,
- flow evidence.

VPC route table a Transit Gateway route table sú odlišné vrstvy.

## 15. VPC endpoints

### Gateway endpoints

Používajú route-table integration pre podporované služby, typicky S3 a DynamoDB.

### Interface endpoints

Vytvárajú ENIs s private IPs v zvolených subnetoch a používajú PrivateLink.

Pri interface endpoint-e over:

- endpoint security group,
- subnet/AZ placement,
- private DNS,
- endpoint policy,
- service/client Region,
- cost za hodinu a traffic.

## 16. DNS attributes

VPC DNS model ovplyvňujú najmä:

- DNS resolution support,
- DNS hostnames,
- DHCP options,
- Route 53 Resolver,
- private hosted zones,
- interface-endpoint private DNS.

Routing connectivity a DNS resolution sú samostatné failure domains.

## 17. Network interfaces

ENI nesie napríklad:

- private IP addresses,
- security groups,
- MAC address,
- attachment,
- source/destination check setting,
- flow-log identity.

Pri failover alebo appliance modeli treba rozlišovať instance lifecycle od ENI/IP identity.

## 18. Source/destination check

EC2 instance má štandardne source/destination check. Network appliance, NAT instance alebo router môže vyžadovať jeho vypnutie.

Vypnutie bez routing a hardening modelu môže vytvoriť neplánovaný transit path.

## 19. Route-table design podľa AZ

Pre resilient egress sa často používa:

```text
private subnet AZ-a → NAT Gateway AZ-a
private subnet AZ-b → NAT Gateway AZ-b
private subnet AZ-c → NAT Gateway AZ-c
```

Znižuje cross-AZ dependency a data-transfer cost. Centralizovaný egress môže byť správny, ale musí explicitne riešiť HA, inspection a return path.

## 20. Network observability

Použi:

- VPC Flow Logs,
- Reachability Analyzer,
- Network Access Analyzer,
- CloudTrail pre control-plane zmeny,
- route table/subnet/ENI inventory,
- service logs a packet capture na customer-controlled hosts.

Flow Logs neobsahujú application payload a nemusia zachytiť každý packet-level detail.

## 21. Troubleshooting path

```text
source IP/ENI
→ source security group
→ source subnet NACL
→ source route table
→ transit target/gateway
→ intermediate route/policy
→ destination route table
→ destination NACL
→ destination security group
→ listener/application
→ return path
```

Over oba smery. Stateless controls a asymmetric routing často spôsobia one-way failure.

## 22. Bežné chyby

### Resource je v „public subnet“, ale nemá internet

Chýba public IP/EIP, IGW route, security rule alebo listener.

### Private instance nevie na internet

Over NAT placement, private route, NAT public-subnet route na IGW a NAT state/port capacity.

### VPC peering funguje iba jedným smerom

Chýba return route alebo security rule na druhej strane.

### DNS resolve funguje, TCP nie

DNS a data path sú odlišné; pokračuj route/security/listener kontrolou.

### Nový subnet používa nesprávne routes

Bol implicitne asociovaný s main route table.

### EKS/RDS nevie vytvoriť ENI

Subnet nemá dostatok voľných IPs alebo chýba service permission/configuration.

## 23. Anti-patterny

### Jeden obrovský VPC bez segmentation

Rozširuje route/security a blast-radius complexity.

### Public/private určené iba názvom

Connectivity určuje route a addressing model.

### Default VPC ako production baseline

Obsahuje convenience defaults, ktoré nemusia zodpovedať governance a isolation požiadavkám.

### Všetok egress cez jednu AZ bez vedomého trade-offu

Vytvára zonal dependency.

### Ručná analýza iba podľa diagramu

Diagram môže byť stale; over live associations a routes.

## 24. Kontrolné otázky

1. Aký je rozdiel medzi VPC a subnet scope-om?
2. Čo robí subnet public?
3. Ako funguje longest prefix match?
4. Čo sa stane subnetu bez explicitnej route-table asociácie?
5. Prečo sa CIDR overlap rieši pred deploymentom?
6. Ako sa líši gateway a interface VPC endpoint?
7. Prečo VPC peering nie je transitive?
8. Kedy použiť Transit Gateway?
9. Ako navrhneš zonally independent NAT egress?
10. Aký je systematický network troubleshooting path?

## Glossary impact

Relevantné pojmy: Amazon VPC, subnet, public subnet, private subnet, isolated subnet, VPC router, route table, main route table, local route, longest prefix match, route propagation, VPC peering, Transit Gateway, gateway endpoint, interface endpoint, PrivateLink, ENI, source/destination check a VPC Flow Logs.

## Oficiálna dokumentácia

- [How Amazon VPC works](https://docs.aws.amazon.com/vpc/latest/userguide/how-it-works.html)
- [Subnets](https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html)
- [Route tables](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html)
- [VPC endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: IAM](iam.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Internet Gateway a NAT Gateway →](internet-gateway-nat-gateway.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
