# VPC, subnets a route tables

Amazon VPC nie je iba CIDR blok okolo EC2 instances. Je to regionálna network-identity a routing boundary, v ktorej vznikajú zonálne subnety, ENIs, route-table associations, DNS behavior, gateways a private endpoints. Funkčný connection path vznikne až vtedy, keď presný source ENI dostane adresu, subnet používa očakávanú route table, longest-prefix rozhodnutie vyberie správny target, return path je symetrický podľa stateful dependencies a traffic prejde security aj application vrstvou.

```text
business communication intent
→ account, Region a VPC generation
→ CIDR a zonálny subnet
→ source ENI a private IP
→ effective route-table association
→ longest-prefix route selection
→ gateway, endpoint alebo attachment
→ forward a return path
→ SG, NACL, TLS a listener
→ business request
```

Route table odpovedá iba na otázku, kam má packet smerovať. Nehovorí, či je traffic povolený alebo či destination application počúva.

## 1. Exact network-flow subject

Atlas Payments používa VPC subject `VPC-P42` v account-e `100000000042` a Regione `eu-central-1`. IPv4 CIDR je `10.42.0.0/16`. Application subnets sú `SUB-PA` v `euc1-az1` s `10.42.16.0/20`, `SUB-PB` v `euc1-az2` s `10.42.32.0/20` a `SUB-PC` v `euc1-az3` s `10.42.48.0/20`.

Release `4.2.0` beží v Auto Scaling group `payments-api-prod`. Request `P-884` potrebuje HTTPS egress na artifact endpoint `203.0.113.42:443`. Pre každý incident sa zachová source ENI, private IP, subnet, AZ ID, route-table association, exact destination IP/port, route target, DNS answer, timestamp a business request ID.

Bez source ENI a destination tuple možno správne analyzovať diagram a nesprávne vysvetliť live flow.

## 2. VPC, subnet a ENI majú rozdielny scope

VPC je regionálny resource. Subnet patrí do jednej Availability Zone. ENI je zonálna network identity s private addresses a Security Groups, ktorú používa EC2 alebo managed service.

Multi-AZ application preto potrebuje viac než tri names:

```text
subnet v každej accepted AZ
→ dostatočný IP headroom
→ explicitná route-table association
→ zonálne alebo regionálne gateway dependencies
→ workload ENIs
→ per-AZ connectivity a failure test
```

Jeden healthy subnet nepreukazuje ostatné. Managed service môže používať vlastné ENIs a spotrebovať address space počas failoveru alebo scale-outu.

## 3. Public, private a isolated sú výsledky pathu

Subnet nemá intrinsic field `public`. Public IPv4 path typicky potrebuje public alebo Elastic IP identity, default route na Internet Gateway a security/listener contract. Private subnet nemá priamy inbound internet path; outbound môže používať NAT, endpoint, proxy alebo hybrid route. Isolated subnet nemá general internet egress, ale môže komunikovať cez `local` route alebo explicitné private attachments.

Názov `private-c` ani tag connectivity nevytvára. Rozhodujú live addresses a routes.

## 4. CIDR a IPAM ako dlhodobý compatibility contract

CIDR plán musí zahŕňať budúce accounts, Regions, hybrid prefixes, peering, Transit Gateway, IPv6 a service ENI demand. Overlap môže znemožniť jednoznačný route verdict alebo prinútiť architektúru používať translation a proxy layers.

Machine-readable allocation:

```yaml
allocationId: IPAM-PAY-42
vpc:
  cidr: 10.42.0.0/16
  region: eu-central-1
subnets:
  - name: application-a
    azId: euc1-az1
    cidr: 10.42.16.0/20
    minimumFreeIps: 300
  - name: application-b
    azId: euc1-az2
    cidr: 10.42.32.0/20
    minimumFreeIps: 300
  - name: application-c
    azId: euc1-az3
    cidr: 10.42.48.0/20
    minimumFreeIps: 300
reservedFor:
  - rollout-surge
  - az-failure-replacement
  - load-balancer-enis
  - interface-endpoints
  - eks-pod-addresses
```

`minimumFreeIps` je failure-mode requirement, nie iba monitoring threshold.

## 5. Praktický VPC a subnet základ v Terraform-e

```hcl
resource "aws_vpc" "payments" {
  cidr_block           = "10.42.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name       = "payments-prod"
    Generation = "VPC-P42"
  }
}

locals {
  application_subnets = {
    a = { cidr = "10.42.16.0/20", az = "eu-central-1a" }
    b = { cidr = "10.42.32.0/20", az = "eu-central-1b" }
    c = { cidr = "10.42.48.0/20", az = "eu-central-1c" }
  }
}

resource "aws_subnet" "application" {
  for_each = local.application_subnets

  vpc_id                  = aws_vpc.payments.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.az
  map_public_ip_on_launch = false

  tags = {
    Name       = "payments-app-${each.key}"
    Tier       = "application"
    Generation = "SUB-P42-${each.key}"
  }
}
```

Tento code vytvorí VPC a tri private-address subnety. `map_public_ip_on_launch=false` nepreukazuje, že subnet nemá internet path; route table a instance addressing stále rozhodujú.

Pre cross-account placement je vhodnejšie mapovať stabilné AZ IDs na account-specific names, ako ukazuje predchádzajúca kapitola.

## 6. Route-table association je explicitná production dependency

Každý subnet používa práve jednu subnet route table. Explicitná association vyberie custom table. Bez nej subnet dedí main route table. Jedna route table môže byť shared viacerými subnetmi a zmena má širší blast radius.

Terraform pre samostatnú application route table:

```hcl
resource "aws_route_table" "application" {
  for_each = local.application_subnets
  vpc_id   = aws_vpc.payments.id

  tags = {
    Name       = "payments-app-${each.key}"
    Generation = "RT-P42-${each.key}"
  }
}

resource "aws_route_table_association" "application" {
  for_each = local.application_subnets

  subnet_id      = aws_subnet.application[each.key].id
  route_table_id = aws_route_table.application[each.key].id
}
```

Explicit association zabraňuje tomu, aby nový subnet potichu zdedil main route table. Terraform plan však nepreukazuje, že live association nebola manuálne zmenená; read-back zostáva potrebný.

## 7. Longest-prefix route selection

Route je destination prefix a target. Ak viac routes matchuje destination, VPC používa najšpecifickejší prefix. `10.44.17.0/24` vyhrá nad `10.44.0.0/16`, ktorý vyhrá nad `0.0.0.0/0`.

Príklad:

```text
10.42.0.0/16   → local
10.44.0.0/16   → Transit Gateway
10.44.17.0/24  → inspection ENI
0.0.0.0/0      → NAT Gateway
```

Flow na `10.44.17.20` použije inspection ENI. Flow na `10.44.18.20` použije Transit Gateway. Internet destination použije NAT.

Pri identickom prefixe môžu platiť ďalšie priority medzi static, prefix-list a propagated routes. Návrh nemá závisieť od nejasnej konkurencie rovnakých prefixes.

## 8. Live route a association read-back

Najprv identifikuj source ENI:

```bash
aws ec2 describe-network-interfaces \
  --network-interface-ids eni-0pay42c \
  --region eu-central-1 \
  --query 'NetworkInterfaces[0].{Ip:PrivateIpAddress,Subnet:SubnetId,Vpc:VpcId,Groups:Groups[].GroupId,Status:Status}'
```

Potom zisti explicitnú route-table association:

```bash
aws ec2 describe-route-tables \
  --region eu-central-1 \
  --filters Name=association.subnet-id,Values=subnet-0payc \
  --query 'RouteTables[].{Id:RouteTableId,Associations:Associations,Routes:Routes}'
```

Prázdny result neznamená, že subnet nemá route table. Znamená, že pravdepodobne používa main table. Zisti ju:

```bash
aws ec2 describe-route-tables \
  --region eu-central-1 \
  --filters Name=vpc-id,Values=vpc-0pay42 Name=association.main,Values=true
```

Tieto commands preukazujú control-plane route state. Neoverujú actual packet traversal, SG/NACL ani return path.

## 9. Subnet IP capacity

AWS rezervuje časť addresses a ďalšie spotrebujú primary/secondary ENIs, load balancers, NAT, endpoints, RDS a EKS Pods. Free-IP observation:

```bash
aws ec2 describe-subnets \
  --subnet-ids subnet-0paya subnet-0payb subnet-0payc \
  --region eu-central-1 \
  --query 'Subnets[].{Subnet:SubnetId,Az:AvailabilityZoneId,Cidr:CidrBlock,Free:AvailableIpAddressCount}' \
  --output table
```

Free count sa porovnáva s maximum concurrent replacementom a rollout surge. Desired Auto Scaling capacity môže rásť, kým ENI allocation zlyháva a serving capacity ostáva rovnaká.

## 10. VPC endpoints menia DNS, route a policy path

Gateway endpoints pre podporované services integrujú route tables. Interface endpoints vytvárajú ENIs v subnets, Security Groups a optional private DNS. Endpoint policy je ďalší authorization filter.

Interface endpoint path:

```text
service hostname
→ private DNS answer
→ endpoint ENI in selected AZ
→ route/local VPC path
→ endpoint SG
→ endpoint policy
→ target service authorization
```

DNS môže resolve-nuť na endpoint a request môže stále zlyhať na endpoint SG alebo policy. Endpoint `available` nepreukazuje application operation.

Read-back:

```bash
aws ec2 describe-vpc-endpoints \
  --region eu-central-1 \
  --filters Name=vpc-id,Values=vpc-0pay42 \
  --query 'VpcEndpoints[].{Id:VpcEndpointId,Service:ServiceName,Type:VpcEndpointType,State:State,PrivateDns:PrivateDnsEnabled,Subnets:SubnetIds}'
```

## 11. Peering, Transit Gateway a hybrid routing

VPC peering nie je transitive. A↔B a B↔C nevytvoria A↔C. Obe strany potrebujú non-overlapping CIDRs, forward/return routes a security rules.

Transit Gateway pridáva vlastný attachment a routing graph:

```text
source subnet route table
→ TGW attachment
→ TGW route-table association
→ propagation alebo static route
→ destination attachment
→ destination subnet/on-prem route
```

VPC route table a TGW route table sú odlišné observation points. Inspection architecture navyše potrebuje symmetric flow podľa stateful firewall modelu.

## 12. Reachability Analyzer ako configuration-path experiment

Reachability Analyzer môže modelovať, či configuration umožňuje path medzi supported source a destination resources. Vytvor path:

```bash
PATH_ID=$(aws ec2 create-network-insights-path \
  --source eni-0pay42c \
  --destination eni-0artifact \
  --protocol tcp \
  --destination-port 443 \
  --region eu-central-1 \
  --query NetworkInsightsPath.NetworkInsightsPathId \
  --output text)

ANALYSIS_ID=$(aws ec2 start-network-insights-analysis \
  --network-insights-path-id "$PATH_ID" \
  --region eu-central-1 \
  --query NetworkInsightsAnalysis.NetworkInsightsAnalysisId \
  --output text)

aws ec2 describe-network-insights-analyses \
  --network-insights-analysis-ids "$ANALYSIS_ID" \
  --region eu-central-1
```

Analysis vysvetľuje modeled configuration path a blocking component. Nevykonáva application TLS alebo business request a nemusí reprezentovať external device state mimo modeled AWS graphu.

## 13. Runtime packet a application evidence

Z affected workloadu:

```bash
getent ahostsv4 artifact.example.net
nc -vz -w 3 artifact.example.net 443
openssl s_client \
  -connect artifact.example.net:443 \
  -servername artifact.example.net \
  -brief </dev/null
```

DNS, TCP a TLS sú tri rôzne verdicts. Až application request overí HTTP/auth/business layer.

Flow Logs môžu ukázať source/destination tuple a ACCEPT/REJECT na capture interface. `ACCEPT` nepreukazuje remote response. `REJECT` nemusí bez ďalšej korelácie jednoznačne určiť SG alebo NACL.

## 14. Worked incident: nový subnet zdedí main route table

Po pridaní zone C sa instances v `SUB-PC` spustili a EC2 status checks boli green, no bootstrap a HTTPS calls timeoutovali iba v tejto AZ. Diagram aj tags tvrdili, že subnet používa `RT-PC → NAT-C`.

Exact source bol `ENI-P42C`, IP `10.42.48.27`, subnet `SUB-PC`, destination `203.0.113.42:443` a instance generation `LT57/AMI57`.

Hypotézy zahŕňali DNS, SG, NACL, NAT-C, IP exhaustion, route association, partner allowlist a application proxy. ENI aj IP existovali, DNS a SG boli rovnaké ako v healthy cohorts a NAT-C nemalo capacity error. `describe-route-tables` pre explicit subnet association vrátilo prázdny result. Main route table `RT-MAIN` smerovala default traffic na central transit attachment bez return pathu pre tento flow.

Root cause bol chýbajúci `aws_route_table_association` pre nový subnet.

Containment odobral `SUB-PC` z deployment/scale placementu a zachoval healthy AZ-a/AZ-b capacity. Recovery opravila IaC, explicitne asociovala `RT-PC`, overila route na NAT-C a spustila fresh DNS/TCP/TLS/bootstrap test z canary instance. Až potom sa subnet vrátil do fleet-u.

Closure vyžadovala live association zodpovedajúcu IaC, allowed flow z každej AZ, forbidden inbound path a druhý scale-out bez driftu.

## 15. Decommission a address reuse

VPC alebo subnet sa neodstraňuje iba preto, že v ňom nie sú EC2 instances. Môže obsahovať endpoints, ENIs, load balancer nodes, peering/TGW attachments, route dependencies, DNS associations a retained evidence.

```text
workload drain
→ ENI and managed-resource inventory
→ route and attachment removal
→ DNS and security cleanup
→ Flow Log/evidence retention
→ IPAM release
→ subnet/VPC deletion
```

Address prefix sa nesmie okamžite znovu použiť, ak stale routes, firewalls alebo DNS ešte odkazujú na starý ownership.

## Kontrolné otázky

1. Prečo route table sama nepreukazuje connectivity?
2. Ako sa líši VPC, subnet a ENI scope?
3. Čo robí subnet public alebo private v praxi?
4. Ako zistíš effective route table pri chýbajúcej explicit association?
5. Ako longest-prefix match vyberie route?
6. Prečo free IP count patrí do rollout a failover gate-u?
7. Ktoré vrstvy pridáva interface endpoint?
8. Prečo VPC peering nie je transitive?
9. Čo Reachability Analyzer preukazuje a čo nepreukazuje?
10. Aký dôkaz uzavrie route-association incident?

## Oficiálna dokumentácia

- [What is Amazon VPC?](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
- [Subnet route tables](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-route-tables.html)
- [Route priority](https://docs.aws.amazon.com/vpc/latest/userguide/route-tables-priority.html)
- [VPC IP addressing](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-ip-addressing.html)
- [VPC endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints.html)
- [Reachability Analyzer](https://docs.aws.amazon.com/vpc/latest/reachability/what-is-reachability-analyzer.html)
- [VPC Flow Logs](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: IAM](iam.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Internet Gateway a NAT Gateway →](internet-gateway-nat-gateway.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
