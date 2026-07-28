# VPC, subnets a route tables

Amazon Virtual Private Cloud nie je iba CIDR blok. Je to regionálny routing a network-identity boundary, v ktorom AWS vytvára zonálne subnety, ENI identity, route-table associations, DNS behavior, gateway a endpoint paths. Prevádzkový výsledok vznikne až vtedy, keď presný source ENI a destination flow dostanú správnu adresu, route target, forward aj return path a následne prejdú security a application vrstvami.

## Dominantný lifecycle

```text
network a business outcome contract
→ account, Region a VPC generation
→ CIDR/IPAM allocation
→ zonálny subnet a ENI identity
→ effective route-table association
→ longest-prefix route resolution
→ gateway, endpoint alebo attachment target
→ forward a return path
→ security, DNS a application boundaries
→ flow a business verification
→ change, recovery alebo decommission
```

VPC route table určuje **kam** má packet smerovať. Sama nehovorí, či je traffic povolený Security Groupou, NACL, firewallom alebo application listenerom.

## Connected Atlas Payments subject

Atlas Payments presúva payment API do AWS subjectu `CAP-PAY-42`:

```text
AWS account: production-payments
Region: eu-central-1
VPC subject: VPC-P42
IPv4 CIDR: 10.42.0.0/16

private application subnets:
  SUB-PA / AZ-a / 10.42.16.0/20
  SUB-PB / AZ-b / 10.42.32.0/20
  SUB-PC / AZ-c / 10.42.48.0/20

expected route tables:
  RT-PA → NAT-A
  RT-PB → NAT-B
  RT-PC → NAT-C

workload:
  ASG payments-api-prod
  release 4.2.0
  payment request P-884
```

Exact network-flow subject musí obsahovať minimálne:

```text
account a Region
VPC ID a CIDR generation
source ENI, private IP, subnet a AZ
subnet route-table association
route-table generation a selected route
protocol, source/destination IP a port
DNS answer generation, ak sa používa meno
gateway/endpoint/attachment identity
forward a return path
request alebo transaction ID a timeline
```

Bez tejto identity sa ľahko analyzuje správny diagram, ale nesprávny live subnet alebo route table.

## 1. VPC, subnet a ENI majú rozdielny scope

VPC je regionálny resource. Subnet patrí presne do jednej Availability Zone. ENI je zonálna network identity priradená resource-u alebo managed service-u.

Dôsledok:

```text
Multi-AZ application intent
→ subnet v každej používanej AZ
→ IP headroom v každom subnet-e
→ správna route-table association v každej AZ
→ lokálne gateway/endpoint/capacity dependencies
→ samostatné failure a recovery správanie každej cohorty
```

Jeden zdravý subnet nepreukazuje funkčnosť ostatných subnetov. Regionálny VPC tiež automaticky neposkytuje zonálnu redundanciu všetkým závislostiam.

## 2. Public, private a isolated sú výsledky pathu

Subnet nemá intrinsic field `public` alebo `private`.

IPv4 public instance path typicky potrebuje:

```text
public alebo Elastic IPv4 identity
+ subnet route 0.0.0.0/0 → Internet Gateway
+ Security Group a NACL contract
+ listener a return path
```

Private subnet typicky nemá priamy inbound internet path. Outbound môže používať NAT Gateway, VPC endpoint, proxy/firewall alebo hybrid/transit path.

Isolated subnet nemá general internet egress. Stále môže komunikovať cez local route, endpoints alebo explicitnú private connectivity.

Názov `private-c` connectivity nevytvorí. Rozhodujú live addresses, route associations a targets.

## 3. CIDR a IPAM sú dlhodobý compatibility contract

CIDR plánovanie musí zahrnúť:

- existujúce a budúce accounts, Regions a VPCs;
- on-premises a partner prefixes;
- VPC peering, Transit Gateway, VPN a Direct Connect;
- IPv4 aj IPv6;
- subnet growth a failover headroom;
- EKS, load balancer, RDS, endpoint a managed-service ENI consumption;
- ownership a allocation evidence v IPAM alebo ekvivalentnom source-of-truth.

Prekrývajúci sa CIDR nie je iba estetický problém. Môže znemožniť jednoznačný route verdict alebo prinútiť architektúru používať NAT/proxy translation a zložitejšie recovery paths.

## 4. Subnet capacity je ENI capacity

Použiteľná IP capacity nie je rovná celej veľkosti CIDR. AWS časť adries rezervuje a ďalšie spotrebujú:

- EC2 primary a secondary ENIs;
- load balancer nodes;
- NAT a interface endpoints;
- EKS Pods pri VPC CNI modeli;
- RDS a iné managed service ENIs;
- blue/green, instance refresh a failover headroom.

Mechanizmus failure:

```text
subnet free-IP headroom klesne
→ controller alebo ASG požiada o nový ENI
→ ENI/IP allocation zlyhá
→ Pod, instance, endpoint alebo failover resource nevznikne
→ desired capacity existuje iba na control plane
→ serving capacity a recovery objective sa nesplní
```

Pre každý aktívny subnet preto sleduj usable/free IPs aj maximum concurrent replacementu.

## 5. Effective route-table association

Každý subnet používa jednu subnet route table.

- explicitne asociovaný subnet používa zvolenú custom route table;
- subnet bez explicitnej asociácie používa main route table;
- jedna route table môže byť asociovaná s viacerými subnetmi;
- zmena shared table môže mať multi-subnet blast radius.

Production invariant:

```text
subnet identity
→ explicitná expected route-table identity
→ live association
→ versionovaný route set
→ tested forward a return paths
```

Main route table inheritance je častý zdroj driftu pri nových subnetoch.

## 6. Route resolution

Route je dvojica:

```text
destination prefix alebo prefix list
→ target
```

Target môže byť napríklad `local`, IGW, NAT Gateway, Transit Gateway, peering connection, virtual private gateway, ENI, Gateway Load Balancer endpoint alebo egress-only IGW.

AWS najprv používa longest-prefix match. Route pre `10.42.0.0/16` je špecifickejšia než `0.0.0.0/0`. Pri ďalších konfliktoch platia service-specific priority pravidlá, preto návrh nemá závisieť od nejasnej duplicity rovnakých prefixes.

Route-table observation musí uviesť:

```text
exact destination IP
all matching prefixes
selected longest prefix
target ID a stav
route origin: local/static/propagated
associated subnet
```

## 7. Local route nie je security boundary

VPC obsahuje local route pre vlastné CIDRs. Umožňuje routing medzi subnetmi, ale traffic môže byť stále blokovaný SG, NACL, host firewallom, inspection pathom alebo application policy.

Rozdelenie subnetov samo osebe nevytvára least-privilege segmentation. Potrebuje workload a subnet policy model.

## 8. Internet, NAT a endpoint paths

General IPv4 internet path môže smerovať na IGW alebo NAT Gateway podľa addressing a initiation modelu.

AWS service traffic nemusí používať internet/NAT:

- gateway endpoints integrujú route tables pre podporované services;
- interface endpoints vytvárajú private ENIs a DNS path cez PrivateLink;
- endpoint policy, endpoint SG, subnet placement a private DNS tvoria samostatné controls.

Routing a DNS sú rozdielne failure domains. DNS môže resolve-nuť na private endpoint, zatiaľ čo SG alebo endpoint policy request odmietne. Naopak route môže byť správna, ale stale DNS odpoveď pošle clienta na inú generation.

## 9. Peering, Transit Gateway a hybrid routes

VPC peering je non-transitive. Obe strany potrebujú kompatibilné CIDRs, forward a return routes a security contract.

Transit Gateway pridáva vlastné attachment a route-table vrstvy:

```text
VPC subnet route table
→ TGW attachment
→ TGW route-table association/propagation
→ target attachment
→ destination VPC/on-prem route table
```

VPC a TGW route tables nie sú jedna tabuľka. Pri inspection VPC alebo firewall appliance treba navyše zachovať symmetric path podľa service designu.

## 10. Network identity a source/destination check

ENI nesie private IPs, SG associations, MAC, attachment, flow-log identity a ďalšie attributes. Instance lifecycle a ENI/IP lifecycle sa nemusia zhodovať.

Network appliance môže vyžadovať vypnutý EC2 source/destination check. Bez explicitného routing a hardening modelu však taká instance môže vytvoriť neplánovaný transit path.

## 11. Worked incident — nový subnet používa main route table

### Symptóm

Po pridaní zone C:

```text
instances v SUB-PA a SUB-PB sú healthy
instances v SUB-PC sa spustia
EC2 status checks sú green
bootstrap a HTTPS calls timeoutujú iba v AZ-c
ASG replacementuje zone-C instances
```

Diagram aj tagy hovoria, že `SUB-PC` je private application subnet s NAT-C.

### Exact subject

```text
source ENI: ENI-P42C
source subnet: SUB-PC
source IP: 10.42.48.27
expected route table: RT-PC
actual effective route table: RT-MAIN
flow: 10.42.48.27:any → artifact.example.net:443
resolved destination IP: 203.0.113.42
release: 4.2.0
instance generation: LT57/AMI57
```

### Competing hypotheses

1. DNS odpoveď v AZ-c je chybná.
2. Application SG nemá outbound rule.
3. Custom NACL blokuje return ephemeral ports.
4. NAT-C alebo jeho IGW path je chybný.
5. SUB-PC nemá voľné IPs a ENI je partial.
6. SUB-PC používa nesprávnu route table.
7. Third-party endpoint blokuje NAT-C EIP.
8. Bootstrap process používa iný proxy alebo destination než očakávaný.

### Discriminating observations

- ENI a source IP existujú, takže nejde o IP-allocation failure.
- DNS z affected instance vracia rovnakú destination IP ako v healthy AZs.
- SG identity a rules sú rovnaké pre healthy aj affected cohortu.
- Flow Logs ukazujú outbound attempts z `ENI-P42C`, ale žiadny expected NAT-C path.
- Live subnet association ukazuje `SUB-PC → RT-MAIN`, nie `RT-PC`.
- `RT-MAIN` má default route na central transit attachment, ktorý nemá return path pre tento egress flow.

Toto pozorovanie odlišuje route-association failure od NAT, SG, NACL a application hypotheses.

### Containment

- zastav ďalší scale-out/refresh do SUB-PC alebo dočasne odober subnet z ASG placementu;
- zachovaj affected instance, route-table association, Flow Logs, scaling activities a CloudTrail zmenu;
- nesmeruj celý VPC naslepo cez inú default route;
- zachovaj healthy capacity v AZ-a a AZ-b.

### Authoritative recovery

1. Oprav IaC/source-of-truth asociáciu `SUB-PC → RT-PC`.
2. Aplikuj bounded route-association change.
3. Over selected default route na NAT-C a NAT-C path na IGW.
4. Spusť fresh HTTPS connection z affected subnetu.
5. Vytvor jednu canary instance v AZ-c.
6. Over bootstrap, target health a payment request `P-884`.
7. Vráť SUB-PC do plnej fleet placement policy.

### Closure verdict

Incident je uzavretý až keď:

- live association zodpovedá IaC;
- allowed outbound flow funguje z každej AZ;
- forbidden inbound flow ostáva blokovaný;
- ASG zone-C cohorta je stabilná bez replacement loopu;
- payment request prejde a nevznikne duplicate authorization;
- nový subnet conformance test zachytí nesprávnu main-table inheritance.

## 12. Ďalšie failure boundaries

### CIDR overlap po pripojení acquired VPC

Route target nevie jednoznačne reprezentovať oba rovnaké prefixes. Recovery môže vyžadovať readdressing, proxy alebo translation; samotné pridanie ďalšej route problém nevyrieši.

### Peering funguje iba jedným smerom

Forward route existuje, return route alebo security rule na druhej strane chýba. Stav peering connection `active` nepreukazuje bidirectional application flow.

### Interface endpoint je healthy, ale client používa public service path

Private DNS je disabled, client resolver používa stale/public answer alebo endpoint nie je dostupný v jeho AZ/subnet modeli. Over exact DNS answer a destination ENI.

### Central inspection vytvorí asymmetric return path

Forward packet ide cez firewall endpoint, return packet cez inú AZ alebo priame TGW route. Stateful appliance nevie flow spojiť a traffic dropne.

### Subnet free-IP exhaustion blokuje failover

Steady state funguje, ale blue/green, ASG refresh alebo RDS failover potrebuje nové ENIs. Capacity model musí zahŕňať failure a rollout headroom.

## 13. Observation a control points

Používaj kombináciu:

- live subnet a route-table associations;
- route inventory a route origin;
- VPC Flow Logs s ENI/subnet/VPC identity;
- Reachability Analyzer pre configuration path;
- Network Access Analyzer pre policy paths;
- CloudTrail pre control-plane zmeny;
- DNS queries a exact answers;
- application connect/TLS/request evidence;
- source a return-path telemetry v hybrid alebo appliance layers.

Flow Logs neobsahujú payload a `ACCEPT` nepreukazuje úspešný TLS alebo business request.

## 14. Change a recovery controls

- CIDR a subnet allocation riadi jeden authoritative IPAM/source-of-truth.
- Každý production subnet má explicitnú route-table association.
- Route-table changes majú blast-radius inventory a reverse-path validation.
- Nová AZ/subnet generation prejde canary flow tests pred prijatím workloadov.
- IaC policy kontroluje default routes, cross-AZ dependencies a zakázané broad transit paths.
- Free-IP SLO zahŕňa rollout a failover headroom.
- Central inspection má testovaný symmetric-path invariant.
- Diagramy sa generujú alebo pravidelne porovnávajú s live inventory; nie sú autoritatívnym dôkazom samy osebe.

## Referenčné rozlíšenia

| Otázka | Autoritatívna vrstva |
|---|---|
| Akú IP identitu resource používa? | ENI/IP/subnet inventory |
| Ktorá route table platí? | live subnet association |
| Ktorá route sa vybrala? | destination + longest-prefix/priority rules |
| Je path povolený? | SG, NACL, firewall a endpoint policies |
| Resolve-nul sa správny endpoint? | resolver/DNS answer generation |
| Prešiel reálny request? | connection, TLS, application a business evidence |
| Je zmena trvalá? | IaC/source-of-truth a drift verification |

## Kontrolné otázky

1. Prečo názov subnetu neurčuje, či je public alebo private?
2. Aký je rozdiel medzi regionálnym VPC a zonálnym subnetom/ENI?
3. Ako zistíš effective route table subnetu?
4. Ako longest-prefix match ovplyvní konkrétnu destination IP?
5. Prečo route reachability nie je security allow verdict?
6. Ako IP exhaustion ovplyvní rollout alebo failover aj pri zdravom steady state-e?
7. Ktoré vrstvy pridáva Transit Gateway alebo inspection VPC?
8. Ako odlíšiš DNS failure od route alebo policy failure?
9. Prečo treba vždy overiť return path?
10. Aký conformance test by zabránil incidentu so SUB-PC?

## Glossary impact

Relevantné pojmy: VPC network-generation subject, subnet placement subject, ENI identity, effective route-table association, selected route subject, longest-prefix verdict, route origin, forward/return path, VPC endpoint path, subnet IP headroom, transit attachment subject a VPC flow acceptance verdict.

## Oficiálna dokumentácia

- [How Amazon VPC works](https://docs.aws.amazon.com/vpc/latest/userguide/how-it-works.html)
- [Subnet route tables](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-route-tables.html)
- [Route priority](https://docs.aws.amazon.com/vpc/latest/userguide/route-tables-priority.html)
- [VPC endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: IAM](iam.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Internet Gateway a NAT Gateway →](internet-gateway-nat-gateway.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
