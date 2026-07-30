# Security Groups a Network ACLs

Security Group a Network ACL nie sú dva varianty toho istého firewallu. Security Group je stateful allow policy viazaná na ENI alebo podporovaný resource. Network ACL je stateless ordered allow/deny policy viazaná na subnet boundary. Connection prejde až vtedy, keď route dovedie packet na správny enforcement point, new-flow rules ho povolia, return path rešpektuje connection state alebo explicitné stateless rules a destination process prijme request.

```text
communication intent
→ exact source and destination tuple
→ route reachability
→ source Security Group and source-subnet NACL
→ NAT, endpoint or inspection path
→ destination-subnet NACL and destination Security Group
→ listener, TLS and application authorization
→ return packet or tracked response
→ business outcome
```

Security controls sa preto diagnostikujú podľa direction a observation pointu. Outbound rule na source ENI sa nesmie porovnávať s inbound packetom na destination subnet-e a pre-NAT address sa nesmie zamieňať s adresou, ktorú pozoruje partner.

## 1. Exact flow-policy subject

Atlas Payments používa source ENI `ENI-P42C` s private IP `10.42.48.27` v subnet-e `SUB-PC`. ENI je asociovaná so Security Group generation `SG-PAY-APP-31`; subnet používa NACL generation `NACL-PC-7`. Egress route je `RT-PC → NAT-C`. Partner destination je `203.0.113.42:443` a sample request `P-884`.

Konkrétny TCP flow je:

```text
10.42.48.27:53144
→ 203.0.113.42:443
```

Pri incidente sa zachová account, Region, VPC, source ENI a SG set, subnet a NACL, source/destination ports, route/NAT generation, new alebo established connection state, Flow Log observation, TLS peer a business idempotency result.

Bez source portu `53144` nemožno správne vyhodnotiť stateless return rule.

## 2. Security Group ako stateful ENI policy

Security Group obsahuje iba allow rules. Všetky SGs asociované s ENI sa vyhodnocujú ako spoločný allow set; poradie rules nerozhoduje. Ak new connection prejde outbound a inbound policy, return traffic patriaci k tracked connection je povolený bez zrkadlovej SG rule.

```text
new HTTPS connection
→ source SG outbound allow
→ destination SG inbound allow
→ connection tracked
→ response traffic allowed as tracked return
```

Stateful neznamená, že rule mutation okamžite ukončí každú existujúcu long-lived connection. Revocation test musí rozlíšiť fresh connection, established socket a application connection pool.

Security Group reference je identity relationship. Rule `SG-ALB → SG-PAY-APP TCP/8080` znamená, že application target ENI prijíma relevantný traffic z ENIs reprezentovaných load-balancer SG podľa service semantics. Packet neprechádza cez SG ako cez samostatné zariadenie.

## 3. Praktický SG model v Terraform-e

Load balancer môže prijímať HTTPS od clients a application targets iba backend traffic od load balancera:

```hcl
resource "aws_security_group" "alb" {
  name        = "atlas-payments-alb"
  description = "Public HTTPS entry for Atlas Payments"
  vpc_id      = aws_vpc.payments.id

  tags = {
    Generation = "SG-PAY-ALB-18"
  }
}

resource "aws_vpc_security_group_ingress_rule" "alb_https" {
  security_group_id = aws_security_group.alb.id
  description       = "HTTPS from approved client networks"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_security_group" "application" {
  name        = "atlas-payments-app"
  description = "Payments application ENIs"
  vpc_id      = aws_vpc.payments.id

  tags = {
    Generation = "SG-PAY-APP-31"
  }
}

resource "aws_vpc_security_group_ingress_rule" "application_from_alb" {
  security_group_id            = aws_security_group.application.id
  description                  = "Application port only from ALB"
  referenced_security_group_id = aws_security_group.alb.id
  ip_protocol                  = "tcp"
  from_port                    = 8080
  to_port                      = 8080
}

resource "aws_vpc_security_group_egress_rule" "application_https" {
  security_group_id = aws_security_group.application.id
  description       = "HTTPS to governed external dependencies"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}
```

Application SG nemá inbound `0.0.0.0/0:8080`; backend listener je dostupný iba z ALB identity. Egress je v ukážke broad, pretože partner IPs môžu byť dynamické. Production design môže použiť managed prefix lists, proxy, Network Firewall alebo private endpoints podľa dependency contractu. Broad egress sa nesmie prezentovať ako automaticky least privilege.

Moderné standalone SG rule resources dávajú každej rule samostatnú Terraform identity a znižujú nejasnosti pri zmene alebo importe. Plan stále nie je runtime verdict; live ENI môže mať ďalšiu SG alebo manuálnu rule.

## 4. Live SG read-back

Najprv zisti SG set exact ENI:

```bash
aws ec2 describe-network-interfaces \
  --network-interface-ids eni-0pay42c \
  --region eu-central-1 \
  --query 'NetworkInterfaces[0].{Ip:PrivateIpAddress,Subnet:SubnetId,Groups:Groups[].{Id:GroupId,Name:GroupName}}'
```

Potom zobraz rule IDs a descriptions:

```bash
aws ec2 describe-security-group-rules \
  --region eu-central-1 \
  --filters Name=group-id,Values=sg-0payapp31 \
  --query 'SecurityGroupRules[].{RuleId:SecurityGroupRuleId,Egress:IsEgress,Protocol:IpProtocol,From:FromPort,To:ToPort,Cidr4:CidrIpv4,ReferencedGroup:ReferencedGroupInfo.GroupId,Description:Description}' \
  --output table
```

Tento read-back preukazuje configured SG rules a ich stable rule IDs. Nehovorí, ktorú rule použil konkrétny packet ani či route a listener fungujú.

## 5. NACL ako ordered stateless subnet policy

Každý subnet je asociovaný s jednou Network ACL; jedna NACL môže byť shared viacerými subnetmi. NACL má samostatné inbound a outbound rules. Rules sa vyhodnocujú podľa rastúceho rule number a prvý match rozhodne. Unmatched traffic skončí implicitným deny.

NACL nepozná connection state. Outbound HTTPS request a inbound SYN-ACK sú dva samostatné policy verdicts.

```text
outbound packet:
source 10.42.48.27:53144 → destination 203.0.113.42:443

inbound return packet:
source 203.0.113.42:443 → destination 10.42.48.27:53144
```

Inbound return rule preto matchuje destination ephemeral port `53144`, nie destination port `443`.

## 6. Praktický custom NACL v Terraform-e

Nasledujúci NACL povoľuje outbound HTTPS a inbound return traffic pre Linux ephemeral range z governance contractu. Presný range musí zodpovedať používanému OS/runtime-u.

```hcl
resource "aws_network_acl" "application_c" {
  vpc_id     = aws_vpc.payments.id
  subnet_ids = [aws_subnet.application["c"].id]

  tags = {
    Name       = "payments-application-c"
    Generation = "NACL-PC-8"
  }
}

resource "aws_network_acl_rule" "application_c_out_https" {
  network_acl_id = aws_network_acl.application_c.id
  rule_number    = 100
  egress         = true
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 443
  to_port        = 443
}

resource "aws_network_acl_rule" "application_c_in_return" {
  network_acl_id = aws_network_acl.application_c.id
  rule_number    = 100
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 32768
  to_port        = 60999
}
```

Táto ukážka je zámerne minimálna a neobsahuje DNS, internal VPC alebo management flows. Production NACL musí pokryť celý subnet communication contract. Custom NACL sa nemá aplikovať na production subnet, kým preflight nepreukáže všetky forward a return paths.

Rule number je executable priority. Ak rule 90 denyuje partner CIDR a rule 100 povoľuje general HTTPS, deny vyhrá. NACL review preto musí hodnotiť ordered ruleset ako celok.

## 7. Live NACL association a ordered rules

Zisti NACL používanú subnetom:

```bash
aws ec2 describe-network-acls \
  --region eu-central-1 \
  --filters Name=association.subnet-id,Values=subnet-0payc \
  --query 'NetworkAcls[].{Id:NetworkAclId,Associations:Associations,Entries:Entries}'
```

Pre čitateľnejší výstup:

```bash
aws ec2 describe-network-acls \
  --region eu-central-1 \
  --network-acl-ids acl-0payc \
  --query 'NetworkAcls[0].Entries[].{Number:RuleNumber,Egress:Egress,Action:RuleAction,Protocol:Protocol,Cidr:CidrBlock,From:PortRange.From,To:PortRange.To}' \
  --output table
```

Rules s číslom `32767` alebo `*` reprezentujú default deny boundary podľa output formátu. Presence outbound TCP/443 nepreukazuje inbound return allowance.

## 8. Default a custom NACL behavior

Default NACL typicky povoľuje traffic a možno ho sprísniť. Nový custom NACL začína s deny-all behaviorom, kým explicitné rules nepridáš. To je bezpečný default, ale nebezpečný rollout, ak tím zabudne DNS, response ports alebo internal dependencies.

Association custom NACL so subnetom je okamžitá policy zmena pre celú subnet cohortu. Safe rollout používa canary subnet alebo exact preflight, rollback association a business test.

## 9. SG a NACL majú odlišný účel

Security Group je primárny workload-level least-access mechanismus. Sleduje ENI/resource identity a stateful connections. NACL je subnet guardrail, coarse isolation alebo emergency deny boundary. Kopírovanie každej SG rule do NACL vytvára dve policy sources, ktoré sa ľahko rozídu.

NACL je vhodná napríklad na explicitný deny známeho CIDR pre celý subnet alebo na baseline segmentation. SG je vhodnejšia na dynamický application-to-database contract cez SG reference.

## 10. Load balancer vytvára dve connections

Pri Application Load Balanceri existujú dva samostatné network subjects:

```text
client → ALB listener
ALB node → application target
```

Client connection používa ALB subnets, NACL a ALB SG. Backend connection používa target subnet NACL a target SG inbound from ALB SG. Client-side success nepreukazuje backend path; ALB môže vrátiť `502` alebo `503`.

Read-back target health:

```bash
aws elbv2 describe-target-health \
  --target-group-arn "$TARGET_GROUP_ARN" \
  --region eu-central-1 \
  --query 'TargetHealthDescriptions[].{Target:Target.Id,Port:Target.Port,Az:Target.AvailabilityZone,State:TargetHealth.State,Reason:TargetHealth.Reason}'
```

Target `healthy` preukazuje health-check contract, nie customer payment journey.

## 11. Revocation fresh vs established flow

Po odstránení SG rule otestuj nový TCP handshake. Existing keep-alive alebo long-lived TLS session môže určitý čas pokračovať podľa connection tracking a application behavioru. Ak threat model vyžaduje okamžitý cut, treba uzavrieť existing connections, rotate endpoint/credential alebo použiť ďalšiu enforcement vrstvu.

Revocation closure:

```text
rule or identity removed
→ fresh connection denied
→ existing sessions inventoried and terminated when required
→ forbidden destination inaccessible
→ required allowed paths remain healthy
→ audit evidence retained
```

## 12. Flow Logs a Reachability Analyzer

VPC Flow Logs môžu zachytiť ENI, source/destination addresses a ports, protocol, action a observation interval. `REJECT` pomáha lokalizovať network policy boundary, ale sám nemusí jednoznačne označiť SG alebo NACL. `ACCEPT` preukazuje, že capture boundary packet akceptovala; nepreukazuje destination listener alebo response.

Reachability Analyzer modeluje configuration path medzi supported AWS resources. Je užitočný pri SG/NACL/route diagnosis, ale nevykonáva TLS alebo application transaction.

Praktický modeled path:

```bash
PATH_ID=$(aws ec2 create-network-insights-path \
  --source eni-0pay42c \
  --destination eni-0internal-api \
  --protocol tcp \
  --destination-port 443 \
  --region eu-central-1 \
  --query NetworkInsightsPath.NetworkInsightsPathId \
  --output text)

aws ec2 start-network-insights-analysis \
  --network-insights-path-id "$PATH_ID" \
  --region eu-central-1
```

Pre internet destination bez AWS resource identity je runtime a Flow Log evidence dôležitejšia než modeled end-to-end path.

## 13. Runtime flow test

Z affected workloadu:

```bash
getent ahostsv4 auth.psp.example
nc -vz -w 3 auth.psp.example 443
openssl s_client \
  -connect auth.psp.example:443 \
  -servername auth.psp.example \
  -brief </dev/null
```

Ak TCP timeoutuje, packet capture alebo `ss` môže ukázať chosen source port:

```bash
ss -tnp dst 203.0.113.42:443
```

Source port sa následne porovná s NACL return rule. Tento observation je silnejší než všeobecná veta „ephemeral ports sú povolené“.

## 14. Worked incident: NACL blokuje return port iba v AZ-c

Po zaradení `SUB-PC` do production fleet-u fungovali PSP HTTPS calls z AZ-a a AZ-b, no rovnaký binary a SG v AZ-c timeoutoval. DNS odpoveď bola rovnaká, NAT-C bol available a Flow Logs ukazovali outbound attempts.

Exact flow bol `10.42.48.27:53144 → 203.0.113.42:443`. Source ENI bola `ENI-P42C`, SG generation `SG-PAY-APP-31`, NACL generation `NACL-PC-7`, route `RT-PC → NAT-C` a request `P-884`.

Hypotézy zahŕňali SG outbound, partner EIP allowlist, NAT port pressure, outbound NACL, inbound return NACL, TLS, host firewall a route association.

SG a route boli rovnaké ako v healthy cohorts. NAT metrics nemali port-allocation errors a partner videl SYN z NAT-C EIP. NACL-PC mala outbound allow na destination `443`, ale inbound allowovala iba destination `443`. SYN-ACK sa vracal na client destination port `53144` a skončil default deny. Flow evidence korelovala return packet s `REJECT` na affected subnet path.

```text
client SYN from 53144
→ outbound destination 443 allowed
→ NAT-C and partner
→ SYN-ACK returns to destination 53144
→ inbound NACL has no matching ephemeral rule
→ default deny
→ client timeout
```

Containment odobral `SUB-PC` z rollout a scale placementu, zachoval NACL generation, Flow Logs, CloudTrail a source-port sample a ponechal healthy capacity v ostatných AZs. Tím nepridal `ALLOW ALL` ako rýchlu opravu.

Recovery najprv zmerala actual ephemeral range používaného runtime-u, potom upravila IaC o bounded inbound return rule s explicitným numberom. Fresh TCP/TLS connection z canary instance prešla. Nová inbound connection z partner side zostala forbidden, pretože return rule nepovoľuje unsolicited new connection cez NAT/state model.

Closure vyžadovala allowed partner path z každej AZ, correct business response pre `P-884`, žiadne broad inbound exposure a druhý fleet scale-out bez policy driftu.

## 15. Policy-as-code tests

Static policy test má odmietnuť:

```text
application SG inbound 0.0.0.0/0 on backend port
NACL allow-all rule before intended deny
custom NACL without required return-path fixture
shared SG mutated without owner and impact set
rule without description or stable rule identity
```

Integration fixture vytvorí canary ENI/Pod v každej subnet cohort-e a overí DNS, TCP, TLS, allowed business path a forbidden path. Policy JSON/YAML sama nepreukazuje effective enforcement.

## Kontrolné otázky

1. Prečo SG return traffic nepotrebuje zrkadlovú rule?
2. Prečo NACL return traffic explicitnú rule potrebuje?
3. Ktorý port matchuje inbound SYN-ACK pre outbound HTTPS clienta?
4. Ako zistíš SG set exact ENI?
5. Ako zistíš NACL asociovanú so subnetom?
6. Prečo rule number mení NACL verdict?
7. Aký rozdiel je medzi SG reference a CIDR rule?
8. Čo Flow Log `ACCEPT` a `REJECT` preukazujú a čo nie?
9. Ako revocation test rozlišuje fresh a established connection?
10. Aký positive a forbidden test uzavrie AZ-c incident?

## Oficiálna dokumentácia

- [Security groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [How security groups work](https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html)
- [Network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [Control subnet traffic with network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/nacl-rules.html)
- [VPC Flow Logs](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html)
- [Reachability Analyzer](https://docs.aws.amazon.com/vpc/latest/reachability/what-is-reachability-analyzer.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Internet Gateway a NAT Gateway](internet-gateway-nat-gateway.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: EC2 a Auto Scaling →](ec2-auto-scaling.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
