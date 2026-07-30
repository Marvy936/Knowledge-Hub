# Internet Gateway a NAT Gateway

Internet Gateway a NAT Gateway riešia odlišné časti network pathu. Internet Gateway je VPC attachment a route target pre internet traffic. NAT Gateway prekladá source alebo destination addresses podľa svojho connectivity modelu a drží connection state pre return traffic. Ani jeden resource sám nevytvára application connectivity.

```text
source ENI a IP family
→ subnet route-table verdict
→ Internet Gateway alebo NAT Gateway
→ translation a connection state
→ security a return-path controls
→ destination DNS, TLS a application
→ response and reverse translation
→ business outcome
```

Ak application vidí timeout, problém môže byť pred NAT, v NAT capacity, na destination side alebo v samotnom client retry modeli. Preto egress incident potrebuje original aj translated flow identity.

## 1. Exact egress subject

Atlas Payments release `4.2.0` beží v private subnets `SUB-PA`, `SUB-PB` a `SUB-PC`. Partner FQDN je `auth.psp.example`, observed destination `203.0.113.42:443` a sample business request `P-884`.

Egress subject zahŕňa source instance alebo Pod, ENI, private IP, subnet, AZ ID, route table, selected NAT/IGW ID, NAT availability a connectivity mode, public/private translation address, original a translated 5-tuple, DNS answer, TLS peer, connection attempt, retry generation a idempotency key.

Bez translated source identity nemožno odlíšiť NAT capacity od partner allowlistu alebo rate limitu.

## 2. Internet Gateway boundary

Internet Gateway sa attachne k VPC a môže byť route targetom. Attachment neznamená, že každý resource vo VPC je public.

Public IPv4 inbound/outbound path typicky potrebuje:

```text
instance ENI with public IPv4 or Elastic IP mapping
+ subnet route 0.0.0.0/0 → IGW
+ Security Group and NACL allowance
+ process listener and application authorization
```

Private IPv4 resource nezíska internet connectivity iba default route-om na IGW, pretože nemá internet-routable public mapping. Pre private IPv4 egress sa používa NAT alebo iný proxy/inspection path.

Pri IPv6 môže resource používať global unicast address. Internet Gateway umožní inbound alebo outbound podľa routes a controls. Egress-only Internet Gateway poskytuje outbound-initiated IPv6 path bez general unsolicited inbound initiation.

## 3. Praktický public subnet a IGW v Terraform-e

```hcl
resource "aws_internet_gateway" "payments" {
  vpc_id = aws_vpc.payments.id

  tags = {
    Name       = "payments-prod"
    Generation = "IGW-P42"
  }
}

resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.payments.id
  cidr_block              = "10.42.1.0/24"
  availability_zone       = "eu-central-1a"
  map_public_ip_on_launch = false

  tags = {
    Name = "payments-public-a"
  }
}

resource "aws_route_table" "public_a" {
  vpc_id = aws_vpc.payments.id
}

resource "aws_route" "public_a_internet" {
  route_table_id         = aws_route_table.public_a.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.payments.id
}

resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public_a.id
}
```

`map_public_ip_on_launch=false` je úmyselné. Public subnet route umožňuje public-addressed resources používať IGW, ale neudeľuje automaticky public IP každému workloadu. NAT Gateway môže mať vlastný required address model podľa availability mode.

## 4. Public a private NAT sú connectivity typy

Public NAT Gateway sa používa najmä pre private IPv4 internet egress a používa public source identity. Private NAT Gateway prekladá private addresses pre VPC, Transit Gateway alebo on-premises paths a nepoužíva sa na priamy internet egress cez IGW.

Connectivity type odpovedá, kam môže translated traffic smerovať. Availability mode odpovedá, v koľkých AZs a akým spôsobom NAT funguje. Tieto osi sa nesmú zamieňať.

## 5. Zonal a regional NAT sú availability modely

Zonal NAT Gateway funguje v jednej Availability Zone. Tradičný resilient design vytvára jeden public NAT v každej aktívnej AZ a private subnety smerujú na AZ-local NAT.

```text
SUB-PA → NAT-A
SUB-PB → NAT-B
SUB-PC → NAT-C
```

Regional NAT Gateway je jedna logical NAT identity s multi-AZ coverage. Môže automaticky rozširovať coverage podľa workload footprintu alebo používať explicitne spravovaný model. Regional NAT má vlastnú route table a pri public internet modeli nepotrebuje public subnet ako hosting boundary. Private NAT use cases naďalej používajú zonálny model podľa service supportu.

Regional model zjednodušuje route identity, ale neodstraňuje EIP governance, AZ coverage, partner allowlists, expansion timing ani per-AZ observability.

## 6. Vytvorenie regional NAT cez AWS CLI

```bash
aws ec2 create-nat-gateway \
  --vpc-id vpc-0pay42 \
  --availability-mode regional \
  --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=payments-egress},{Key=Generation,Value=NAT-P42-R1}]' \
  --region eu-central-1
```

Command vytvorí regional NAT request. Result obsahuje NAT Gateway ID a state, ale `pending` alebo `available` nepreukazuje coverage všetkých workload AZs ani partner connectivity.

Read-back:

```bash
aws ec2 describe-nat-gateways \
  --filter Name=tag:Generation,Values=NAT-P42-R1 \
  --region eu-central-1 \
  --query 'NatGateways[].{Id:NatGatewayId,State:State,Mode:AvailabilityMode,AutoZones:AutoProvisionZones,AutoIps:AutoScalingIps,Addresses:NatGatewayAddresses}'
```

Pri automatic mode treba sledovať, či NAT už expandoval do novej AZ. Po prvom workload ENI v novej AZ môže service expansion trvať; počas transition môže traffic dočasne použiť existing AZ path. Capacity a cutover test preto nesmie predpokladať okamžitú local coverage.

## 7. Zonal public NAT v Terraform-e

```hcl
resource "aws_eip" "nat_a" {
  domain = "vpc"

  tags = {
    Name       = "payments-nat-a"
    Generation = "EIP-P42-A"
  }
}

resource "aws_nat_gateway" "a" {
  allocation_id = aws_eip.nat_a.id
  subnet_id     = aws_subnet.public_a.id

  tags = {
    Name       = "payments-nat-a"
    Generation = "NAT-P42-A"
  }

  depends_on = [aws_internet_gateway.payments]
}

resource "aws_route" "application_a_internet" {
  route_table_id         = aws_route_table.application["a"].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.a.id
}
```

Tento code vytvorí zonal public NAT v public subnet-e. Pre tri-AZ resilience sa pattern opakuje s independent EIPs a AZ-local routes. Jediný NAT-A pre všetky private subnets vytvára cross-AZ dependency a transfer path.

## 8. Address a port translation

NAT transformuje connection tuple:

```text
10.42.16.27:53144
→ 198.51.100.10:40217
→ 203.0.113.42:443
```

Return packet musí byť mapovateľný späť na source flow. Capacity preto nie je iba Gbit/s. Dôležitý je počet concurrent connections, destination concentration, translated addresses, source ports a connection churn.

Veľa connections rozdelených medzi veľa destination tuples má iné port pressure než rovnaký počet connections na jeden destination IP/port. Partner API s jednou VIP môže byť bottleneck aj pri nízkom byte throughput-e.

## 9. Pooling, keep-alive a retries menia NAT demand

HTTP connection pooling znižuje počet TCP/TLS handshakes a source-port churn. Vypnutie keep-alive môže zmeniť každý business request na novú connection. Timeout retry násobí pressure a pri unknown outcome-e môže vytvoriť duplicate provider authorization.

Application capacity model musí obsahovať:

```text
business request rate
× connection creation ratio
× retry attempts
× average connection lifetime
→ NAT connection and port demand
```

Scale-out môže incident zhoršiť, ak každá nová instance vytvorí nový veľký pool alebo retry cohort.

## 10. NAT nie je firewall ani inbound load balancer

NAT Gateway nemá Security Group. Nie je reverse proxy a neposkytuje arbitrary inbound port forwarding. Return traffic je povolený iba v kontexte outbound-initiated connection state podľa service modelu.

Policy enforcement vykonávajú source/destination SGs, subnet NACLs, route tables, endpoint policies, Network Firewall, proxy a application authentication. Zmena NAT resource-u neopraví KMS, TLS alebo HTTP authorization failure.

## 11. Private alternatives k general NAT

AWS service calls nemusia prechádzať cez internet NAT. Gateway endpoints pre S3 a DynamoDB integrujú route tables. Interface endpoints používajú ENIs, Security Groups, endpoint policies a private DNS. Central proxy alebo Network Firewall môže poskytnúť explicitnú egress inspection.

Voľba sa robí podľa service supportu, policy, DNS, costu, AZ placementu a failure modelu. Endpoint odstráni NAT dependency pre konkrétnu service, ale pridá vlastnú identity a capacity boundary.

## 12. NACL return path

NAT Gateway nemá SG, no source a NAT subnets používajú NACLs. NACL je stateless. Outbound allow na destination TCP/443 nestačí, ak inbound return packet na client ephemeral destination port nie je povolený.

Source port range sa overuje podľa runtime/OS, nie slepo kopíruje. Broad range môže byť potrebný, ale musí byť odvodený z actual behavioru a threat modelu.

## 13. Centralized egress

Multi-account architecture môže viesť traffic cez Transit Gateway, inspection VPC, Network Firewall alebo proxy a až potom NAT/IGW.

```text
spoke subnet route
→ Transit Gateway attachment
→ TGW route table
→ inspection endpoint
→ firewall state
→ NAT translation
→ Internet Gateway
→ symmetric return path
```

Centralizácia znižuje duplicitu policy, ale vytvára shared throughput, route, inspection a operational failure domain. Stateful firewall potrebuje symetrický forward a return path.

## 14. Runtime diagnostika egressu

Z affected workloadu:

```bash
getent ahostsv4 auth.psp.example
nc -vz -w 3 auth.psp.example 443
openssl s_client \
  -connect auth.psp.example:443 \
  -servername auth.psp.example \
  -brief </dev/null
```

DNS success nepreukazuje TCP. TCP success nepreukazuje TLS. TLS success nepreukazuje application authorization alebo payment correctness.

NAT state a addresses:

```bash
aws ec2 describe-nat-gateways \
  --nat-gateway-ids nat-0pay42 \
  --region eu-central-1
```

Route read-back:

```bash
aws ec2 describe-route-tables \
  --filters Name=association.subnet-id,Values=subnet-0paya \
  --region eu-central-1 \
  --query 'RouteTables[0].Routes'
```

Metrics:

```bash
aws cloudwatch get-metric-data \
  --region eu-central-1 \
  --metric-data-queries file://nat-metric-queries.json \
  --start-time 2026-07-30T18:00:00Z \
  --end-time 2026-07-30T19:00:00Z
```

`nat-metric-queries.json` môže čítať `ActiveConnectionCount`, `ErrorPortAllocation`, `PacketsDropCount` a bytes pre exact NAT Gateway. Nulový `ErrorPortAllocation` oslabuje port-exhaustion hypothesis, no nevylučuje destination alebo application failure.

## 15. Worked incident: retry-amplified NAT port exhaustion

Po release `4.2.0` rástla payment authorization latency a časť HTTPS calls timeoutovala. EC2, ASG a targets zostali green. Všetky private subnets používali jeden zonal `NAT-A` a jednu partner-allowlisted EIP.

Hypotézy zahŕňali partner outage, DNS, NACL, NAT AZ degradation, port allocation, TLS, application socket exhaustion a duplicate retries.

Low-rate canary dokončil DNS a TLS. Flow evidence ukázala concentration na `203.0.113.42:443`. `ActiveConnectionCount` prudko rástol a `ErrorPortAllocation` časovo koreloval s timeoutmi. Release diff ukázal vypnuté HTTP pooling a tri retries pre každý timeout. Partner videl viac connection attempts než business requests.

Causal chain:

```text
pooling disabled
→ more short-lived TCP/TLS connections
→ timeout retries ×3
→ destination-tuple concentration
→ NAT port pressure
→ connection failures
→ more retries
```

Containment zastavil rollout a ďalší scale-out, obnovil pooling, znížil retry concurrency a aktivoval stable provider idempotency key. Tím zachoval NAT metrics, Flow Logs, release diff a provider audit.

Recovery zaviedla bounded retries, tested connection pool a egress architecture s per-AZ zonal NAT alebo approved regional NAT. Nové public source identities sa koordinovali s partner allowlistom. Canary sledoval NAT metrics aj payment ledger.

Closure vyžadovala nulové port-allocation errors pri expected peak-u, bounded connection creation, jeden provider authorization pre `P-884`, fungujúci AZ-loss path a forbidden duplicate test.

## 16. Egress architecture acceptance

Egress je accepted, keď každý source AZ má known path, translated identity je governance-managed, partner allowlists poznajú failure identities, metrics a Flow Logs sú dostupné, connection model spĺňa capacity a failure test a private AWS service calls nepoužívajú zbytočný general NAT.

`curl` z jednej instance je iba sample. Production test potrebuje každú AZ cohortu, expected concurrency a failure transition.

## Kontrolné otázky

1. Čo musí mať public IPv4 resource okrem route na IGW?
2. Aký rozdiel je medzi public a private NAT?
3. Aký rozdiel je medzi zonal a regional NAT?
4. Prečo regional NAT neodstraňuje AZ-coverage test?
5. Ako translation mení flow identity?
6. Prečo pooling a retries ovplyvňujú NAT capacity?
7. Ktorý metric podporuje port-allocation hypothesis?
8. Prečo NAT Gateway nie je firewall?
9. Kedy je VPC endpoint lepší než general NAT path?
10. Aký business test uzavrie egress recovery?

## Oficiálna dokumentácia

- [Internet gateways](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html)
- [NAT gateways](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)
- [Regional NAT gateways](https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateways-regional.html)
- [NAT Gateway metrics](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway-cloudwatch.html)
- [VPC endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: VPC, subnets a route tables](vpc-subnets-route-tables.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Security Groups a Network ACLs →](security-groups-network-acls.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
