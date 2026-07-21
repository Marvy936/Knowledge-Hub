# Internet Gateway a NAT Gateway

Internet Gateway (IGW) a NAT Gateway riešia odlišné network functions. IGW poskytuje VPC route target pre internet-routable traffic. NAT Gateway prekladá source alebo destination addresses podľa connectivity typu a umožňuje typicky private IPv4 resources iniciovať outbound connections bez priamej unsolicited inbound connectivity.

## 1. Internet Gateway

Internet Gateway je horizontally scaled, redundantný a highly available VPC component pripojený k VPC.

Poskytuje:

- route target pre IPv4 a IPv6 internet traffic,
- internet path pre resources s vhodným public addressingom,
- one-to-one public IPv4 translation pre instance public IPv4/EIP model,
- managed availability bez customer-managed appliance lifecycle.

IGW attachment sám internet connectivity nevytvorí.

## 2. Public IPv4 path

EC2 instance potrebuje typicky:

```text
public alebo Elastic IPv4
+ subnet route 0.0.0.0/0 → IGW
+ security group/NACL allow
+ application listener
+ return path
```

Private IPv4 sa na internet neposiela priamo. IGW používa public IPv4/EIP mapovanie resource-u.

## 3. IPv6 internet path

Pri IPv6 resource používa global unicast address.

- IGW môže poskytovať inbound aj outbound internet path podľa routes a security controls.
- Egress-only Internet Gateway umožňuje outbound-initiated IPv6 connections bez unsolicited inbound path.

IPv6 nepoužíva NAT Gateway ako povinný základný egress model.

## 4. Public subnet

Subnet s route `0.0.0.0/0 → IGW` sa bežne nazýva public subnet. Resource v ňom však stále nemusí byť public, ak:

- nemá public IP,
- security group blokuje traffic,
- NACL blokuje traffic,
- application nepočúva,
- OS firewall blokuje traffic.

## 5. NAT Gateway

NAT Gateway je managed Network Address Translation service.

Connectivity types:

- **public NAT Gateway**,
- **private NAT Gateway**.

Najbežnejší model je public NAT Gateway pre outbound IPv4 internet access private subnetov.

## 6. Public NAT Gateway

Public NAT Gateway:

- vytvoríš v public subnet-e,
- priradíš mu Elastic IP,
- jeho subnet route table potrebuje path na IGW,
- private subnet route table smeruje internet traffic na NAT Gateway.

Path:

```text
private instance
→ private subnet route 0.0.0.0/0
→ public NAT Gateway
→ public subnet route 0.0.0.0/0
→ Internet Gateway
→ internet
```

External service vidí NAT Gateway public source IP.

## 7. Inbound behavior

NAT Gateway umožňuje return traffic pre connections iniciované zvnútra. Nie je všeobecný inbound port-forwarding alebo reverse-proxy service.

Pre inbound exposure použi podľa potreby:

- public load balancer,
- API Gateway,
- CloudFront,
- public EC2/EIP,
- firewall/proxy appliance,
- private connectivity.

## 8. Private NAT Gateway

Private NAT Gateway poskytuje NAT pre private connectivity, napríklad medzi networks s overlapping alebo constrained addressing requirements podľa podporovaného routing modelu. Nemá Elastic IP a nie je určený na priamy internet egress cez IGW.

Presný target a connectivity design treba overiť podľa Transit Gateway, virtual private gateway alebo destination network topológie.

## 9. Zonal behavior

NAT Gateway je vytvorený v konkrétnom subnet-e a Availability Zone.

Ak private subnety z viacerých AZ používajú jediný NAT Gateway:

- vzniká cross-AZ dependency,
- zonal failure môže odstrániť egress viacerým AZ,
- cross-AZ data transfer môže zvyšovať cost.

Production baseline často používa jeden NAT Gateway na aktívnu AZ a AZ-local routes.

## 10. Route-table model

Príklad:

```text
public-rt-a:
  0.0.0.0/0 → igw

private-rt-a:
  0.0.0.0/0 → nat-a

private-rt-b:
  0.0.0.0/0 → nat-b
```

NAT Gateway route v jeho vlastnom public subnet-e nemá smerovať späť na ten istý NAT Gateway.

## 11. Security controls

NAT Gateway nemá security group.

Traffic kontrolujú:

- source resource security groups,
- subnet NACLs,
- routes,
- destination controls,
- optional AWS Network Firewall/proxy architecture.

NACL na NAT subnet-e musí umožniť potrebné request aj return ports, pretože je stateless.

## 12. Ephemeral ports a connection capacity

NAT Gateway sleduje connections a používa source-port translation. Pri veľkom počte connections na rovnaký destination tuple môže vzniknúť port exhaustion alebo connection errors.

Sleduj:

- concurrent connections,
- destination concentration,
- connection churn,
- idle timeouts,
- allocated Elastic IP capacity podľa podporovaných features,
- CloudWatch NAT Gateway metrics.

Application connection pooling a destination sharding môžu byť rovnako dôležité ako network scaling.

## 13. NAT Gateway cost

Cost drivers typicky zahŕňajú:

- hourly NAT Gateway charge,
- processed bytes,
- cross-AZ data transfer,
- internet alebo service data transfer,
- duplicated NAT Gateways pre HA.

VPC endpoints môžu pri AWS service trafficu znížiť NAT processing a zlepšiť private connectivity, ale majú vlastný hourly/data cost.

## 14. VPC endpoints ako alternatíva

Pre traffic na podporované AWS services zváž:

- S3/DynamoDB gateway endpoints,
- interface endpoints cez PrivateLink.

Výhody:

- bez general internet path,
- policy boundary,
- private IP/DNS path,
- menšia NAT dependency.

Nevýhody:

- endpoint cost,
- per-AZ placement,
- security group/private DNS complexity,
- service availability podľa Regionu.

## 15. NAT instance

NAT instance je EC2-based NAT appliance.

Oproti NAT Gateway poskytuje väčšiu OS/network kontrolu, ale zákazník vlastní:

- patching,
- scaling,
- HA/failover,
- source/destination check,
- throughput,
- monitoring,
- route replacement.

Použi iba pri konkrétnej capability požiadavke, nie ako default zo zvyku.

## 16. Centralized egress

Veľké multi-account prostredie môže centralizovať egress cez Transit Gateway, inspection VPC, Network Firewall a NAT Gateways.

Musí riešiť:

- symmetric routing,
- attachment/route-table segmentation,
- appliance mode,
- zonal paths,
- DNS/proxy model,
- failure blast radius,
- cost allocation,
- emergency bypass policy.

Centralizácia znižuje duplicitu, ale vytvára shared dependency.

## 17. AWS Network Firewall insertion

Inspection architecture musí zabezpečiť, že forward aj return traffic prejde rovnakým stateful inspection pathom podľa podporovaného designu.

Chyby:

- asymmetric routing,
- NAT pred/po nesprávnej vrstve,
- missing gateway route table,
- AZ mismatch,
- firewall endpoint route omission.

## 18. Observability

Sleduj:

- NAT Gateway state,
- bytes/packets,
- active connections,
- connection attempts/errors,
- port allocation errors,
- VPC Flow Logs source/destination,
- route table changes cez CloudTrail,
- application timeouts a destination telemetry.

NAT metric bez application contextu nemusí odhaliť DNS, TLS alebo remote rate-limit failure.

## 19. Troubleshooting outbound internetu

Postup:

```text
DNS resolve?
→ source private IP a security group?
→ private subnet route na správny NAT?
→ NAT available v očakávanej AZ/subnet?
→ NAT subnet route na IGW?
→ IGW attached?
→ NACL oba smery a ephemeral ports?
→ destination reachable/rate limited?
→ NAT connection/port metrics?
```

Testuj konkrétny protocol a destination. ICMP nemusí byť relevantný pre HTTPS failure.

## 20. Bežné chyby

### NAT Gateway je v private subnet-e

Nemá route cez IGW, takže public NAT internet path nefunguje.

### Private subnet route smeruje na IGW

Instance bez public IP nezíska týmto internet connectivity.

### Jediný NAT Gateway pre tri AZ

Zonal failure alebo maintenance path môže ovplyvniť všetky private subnety.

### NACL povoľuje iba destination port 443

Stateless return traffic potrebuje relevantné ephemeral port rules.

### AWS API calls používajú drahý NAT path

Chýba vhodný VPC endpoint alebo private service architecture.

### Port exhaustion

Veľa short-lived connections smeruje na rovnaký destination IP/port.

## 21. Anti-patterny

### NAT Gateway považovaný za firewall

Primárne prekladá addresses a connection state; security policy potrebuje samostatné controls.

### NAT ako inbound exposure

Nie je load balancer ani destination port mapping service.

### Cross-AZ NAT bez cost/failure analýzy

Vytvára skrytý coupling.

### Všetok service traffic cez internet/NAT

Ignoruje private endpoints a service policies.

### Cleanup NAT bez route dependency analýzy

Odstráni outbound path mnohým workloads.

## 22. Kontrolné otázky

1. Čo IGW poskytuje a čo neposkytuje?
2. Ktoré podmienky potrebuje EC2 pre public IPv4 internet access?
3. Ako funguje public NAT Gateway path?
4. Prečo NAT Gateway neumožňuje unsolicited inbound connections?
5. Prečo je NAT Gateway zonálna dependency?
6. Aké controls filtrujú NAT traffic?
7. Kedy je vhodný VPC endpoint?
8. Čo spôsobuje NAT port exhaustion?
9. Ako sa líši NAT instance od NAT Gateway?
10. Ako diagnostikuješ private-subnet outbound failure?

## Glossary impact

Relevantné pojmy: Internet Gateway, public IPv4 path, egress-only Internet Gateway, public NAT Gateway, private NAT Gateway, NAT subnet, NAT port exhaustion, AZ-local egress, centralized egress, NAT instance a VPC endpoint substitution.

## Oficiálna dokumentácia

- [Internet gateways](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html)
- [NAT gateways](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)
- [NAT gateway basics](https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-basics.html)
- [Compare NAT gateways and NAT instances](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-comparison.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: VPC, subnets a route tables](vpc-subnets-route-tables.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Security Groups a Network ACLs →](security-groups-network-acls.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
