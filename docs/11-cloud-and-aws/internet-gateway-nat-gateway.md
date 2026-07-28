# Internet Gateway a NAT Gateway

Internet Gateway a NAT Gateway riešia odlišné časti network pathu. IGW je internet route target pre VPC resources s vhodnou public alebo IPv6 identity. NAT Gateway prekladá addresses a udržiava connection state pre flows iniciované zo source networku. Ani jeden resource sám nevytvára application connectivity: výsledok závisí od addressing identity, subnet routes, NAT availability/connectivity mode, Security Groups, NACLs, destination behavior a return pathu.

## Dominantný lifecycle

```text
internet alebo private-egress outcome
→ source IP family, ENI a subnet identity
→ effective default/service route
→ IGW alebo NAT Gateway target
→ NAT availability a connectivity mode
→ address/port translation a connection tracking
→ security a stateless return-path controls
→ destination DNS/TLS/application behavior
→ reverse translation a response
→ metric, request a business verification
→ scale, failover alebo recovery
```

## Connected Atlas Payments subject

Atlas Payments release `4.2.0` beží v private subnets subjectu `CAP-PAY-42` a autorizuje platby cez partnera:

```text
source fleet: ASG payments-api-prod
source subnets: SUB-PA, SUB-PB, SUB-PC
expected egress: AZ-local alebo regional managed NAT path
partner FQDN: auth.psp.example
observed destination: 203.0.113.42:443
business request: P-884
required property: one authorization, bounded latency
```

Exact egress-flow subject musí obsahovať:

```text
source instance/ENI/private IP/subnet/AZ
selected route table a route target
IGW/NAT Gateway ID
NAT availability mode: zonal alebo regional
NAT connectivity type: public alebo private
EIP/private address generation a AZ coverage
original a translated 5-tuple
connection/retry generation
DNS answer, TLS peer a destination identity
CloudWatch/Flow Log observation window
transaction a idempotency key
```

Bez original a translated tuple sa NAT failure ľahko zamieňa za remote rate limit, DNS, TLS alebo firewall problém.

## 1. Internet Gateway boundary

IGW je managed VPC attachment a route target. Attachment sám connectivity nevytvorí.

Public IPv4 path typicky potrebuje:

```text
resource public IPv4 alebo Elastic IP mapping
+ subnet route 0.0.0.0/0 → IGW
+ SG/NACL/host policy
+ listener a return path
```

Private IPv4 resource nezíska internet connectivity iba tým, že jeho subnet smeruje na IGW. Chýba mu internet-routable public IPv4 mapping.

Pri IPv6 resource používa global unicast address. IGW môže poskytovať inbound/outbound path podľa routes a security controls. Egress-only IGW poskytuje outbound-initiated IPv6 model bez general unsolicited inbound pathu.

## 2. NAT Gateway má dve nezávislé klasifikácie

### Connectivity type

- **public NAT Gateway** — typický private-IPv4 internet egress; používa public EIP identity;
- **private NAT Gateway** — private address translation pre VPC/on-premises/transit use cases, nie priamy internet egress cez IGW.

### Availability mode

Aktuálne AWS API rozlišuje:

- **zonal NAT Gateway** — managed redundancy a scale v jednej Availability Zone;
- **regional NAT Gateway** — jedna logical NAT Gateway identity s multi-AZ coverage a per-AZ address handling podľa konfigurácie/auto-provision modelu.

Availability mode a connectivity type sú rozdielne axes. `public` neznamená `regional`; `regional` neznamená private connectivity.

Pri návrhu over aj podporu konkrétneho Regionu, IaC providera a operations tooling-u.

## 3. Public NAT internet path

Pri zonálnom modeli:

```text
private ENI v AZ-a
→ private route table 0.0.0.0/0 → NAT-A
→ NAT-A private/EIP translation
→ NAT subnet route 0.0.0.0/0 → IGW
→ internet destination
→ IGW
→ NAT-A reverse translation
→ source ENI
```

Pri regional modeli musí route a AZ-coverage contract smerovať traffic na regional NAT subject a musí byť jasné, ktoré EIPs/addresses reprezentujú jednotlivé AZ paths.

External allowlist sa viaže na observed public source IP. Zmena EIP coverage, NAT mode alebo failover preto môže byť application compatibility zmena, nie iba infra detail.

## 4. NAT nie je inbound load balancer ani firewall

NAT Gateway povoľuje return traffic pre connections iniciované zo source side. Nie je general inbound destination-port mapping, reverse proxy ani application load balancer.

NAT Gateway tiež nie je policy firewall. Nemá Security Group. Traffic control vykonávajú source/destination SGs, NACLs, routes, endpoint policies, Network Firewall/proxy layers a application authentication.

## 5. Address a port translation

NAT path transformuje original connection subject:

```text
source-private-IP:source-port
→ NAT public/private IP:translated-port
→ destination-IP:destination-port
```

NAT musí vedieť reverse-mapovať response na pôvodný source flow. Capacity preto nie je iba bytes/second; zahŕňa concurrent connections, source-port availability, destination concentration a connection churn.

Dôležitý distinction:

```text
veľa total connections rozložených medzi destinations
≠
veľa concurrent connections na rovnaký destination IP/port
```

Port-allocation pressure môže vzniknúť aj pri nízkom average bandwidth.

## 6. Connection pooling, retries a idle timeouts

Application behavior priamo mení NAT capacity:

- pooling a keep-alive znižujú nové connection attempts;
- short-lived connections zvyšujú source-port churn;
- agresívne retries násobia rovnaký destination pressure;
- DNS odpoveď sústreďujúca traffic na jeden IP zvyšuje tuple concentration;
- NAT idle timeout môže ukončiť dlho neaktívne connections;
- client musí správne rozlíšiť timeout, retry eligibility a idempotency.

Scale-out workloadu môže NAT pressure zhoršiť, ak každá nová instance vytvorí vlastný connection pool alebo retry storm.

## 7. Zonal a regional resilience

### Zonal NAT design

Tradičný resilient model používa NAT Gateway v každej aktívnej AZ a AZ-local private routes:

```text
SUB-PA → NAT-A
SUB-PB → NAT-B
SUB-PC → NAT-C
```

Znižuje cross-AZ dependency a transfer cost, ale zvyšuje počet resources a EIP identities.

### Regional NAT design

Regional NAT Gateway zjednodušuje logical management a poskytuje multi-AZ coverage. Stále potrebuje:

- overenú AZ auto-provision alebo explicit coverage policy;
- EIP governance a allowlist awareness;
- per-AZ observation a capacity evidence;
- route-table conformance;
- failure a decommission runbook.

Regional resource neodstraňuje potrebu testovať každú source AZ cohortu.

## 8. VPC endpoints a private alternatives

General NAT path nie je potrebný pre každý AWS service call.

- S3 a DynamoDB gateway endpoints integrujú route tables;
- interface endpoints používajú ENIs, SGs, endpoint policy a private DNS;
- proxy alebo central egress môže poskytovať explicitnú inspection a identity policy.

Výber závisí od service coverage, hourly/data costu, AZ placementu, DNS, policy a operational ownershipu.

Endpoint môže odstrániť NAT dependency, ale pridá vlastnú endpoint policy, SG a DNS failure boundary.

## 9. Stateless NACL a return ports

NAT Gateway nemá SG, ale NAT subnet a source subnet používajú NACLs. NACL je stateless, preto musí explicitne povoliť forward aj return directions vrátane relevantných ephemeral destination ports.

Rule `outbound TCP/443 allow` sama nestačí pre response packet smerujúci na client ephemeral port.

Presný ephemeral range závisí od client OS/runtime a pathu; netreba kopírovať historický rozsah bez overenia actual source-port behavioru.

## 10. Centralized egress a inspection

Multi-account environment môže smerovať traffic cez Transit Gateway, inspection VPC, Network Firewall/proxy a NAT.

Taký path pridáva:

```text
source VPC route
→ TGW attachment/route table
→ inspection endpoint/appliance
→ NAT translation
→ IGW
→ symmetric reverse path
```

Stateful inspection vyžaduje compatible forward a return path. Centralizácia znižuje duplicitu, ale vytvára shared capacity, failure a change domain.

## 11. Observability contract

NAT evidence zahŕňa:

- NAT Gateway state a availability mode;
- AZ/address coverage;
- `ActiveConnectionCount`;
- `ErrorPortAllocation`;
- `PacketsDropCount` a ďalšie relevantné metrics;
- bytes/packets a connection attempts;
- source/destination tuples vo Flow Logs;
- route a EIP changes v CloudTrail;
- DNS answers, TLS errors, partner rate-limit evidence;
- application retry a connection-pool metrics;
- transaction/idempotency outcomes.

`ErrorPortAllocation > 0` je silný discriminating signal pre NAT source-port capacity. Samotný application timeout ho nepreukazuje.

## 12. Worked incident — retry-amplified NAT port exhaustion

### Symptóm

Po release `4.2.0`:

```text
payment authorization latency rastie
časť HTTPS calls timeoutuje
EC2/ASG/target health ostáva green
všetky source AZs sú affected
remote PSP hlási iba mierne zvýšený load
```

Legacy topology smeruje všetky private subnety cez jeden zonal `NAT-A` a jednu allowlisted EIP.

### Exact subject

```text
release: 4.2.0
source fleet: payments-api-prod
source subnets: SUB-PA/SUB-PB/SUB-PC
route target: NAT-A
NAT mode: public + zonal
public source identity: EIP-A
flow: many private source ports → 203.0.113.42:443
transaction sample: P-884
client behavior: pooling disabled, 3 retries per timeout
```

### Competing hypotheses

1. Partner PSP rate-limit alebo outage.
2. DNS vracia chybný alebo jediný unhealthy IP.
3. SG/NACL blokuje časť return trafficu.
4. Cross-AZ path alebo NAT-A AZ degradation.
5. NAT port allocation exhaustion.
6. TLS trust/certificate failure.
7. Application thread/socket/file-descriptor exhaustion.
8. Retry amplification vytvára duplicate authorizations.

### Discriminating observations

- DNS a TLS handshake z low-rate canary requestu fungujú.
- Flow Logs ukazujú vysokú concentration na jeden destination tuple.
- `ActiveConnectionCount` prudko rastie.
- `ErrorPortAllocation` je nenulové a časovo koreluje s timeoutmi.
- Release diff ukazuje vypnutý HTTP connection pooling a agresívnejší retry policy.
- Partner audit neukazuje úplný outage, ale vidí viac connection attempts než business requests.

Causal chain:

```text
pooling disabled
→ viac short-lived TCP/TLS connections
→ timeout retries ×3
→ destination-tuple concentration
→ NAT source-port allocation pressure
→ connection failures
→ ďalšie retries
→ latency a duplicate-risk amplification
```

### Containment

- zastav ďalší rollout alebo scale-out release-u 4.2.0;
- obnov pooling a zníž retry concurrency/rate;
- aktivuj idempotency gate na partner authorization operation;
- zachovaj NAT metrics, Flow Logs, release diff a partner transaction audit;
- neotváraj broad inbound ani nevymieňaj SG/NACL bez evidence.

### Authoritative recovery

1. Oprav client connection pool a bounded retry policy.
2. Over one-business-operation-to-one-idempotency-key contract.
3. Vyhodnoť egress architecture:
   - zonal NAT per AZ;
   - regional NAT s overenou AZ/EIP coverage;
   - ďalšie EIPs/capacity podľa service supportu;
   - partner/DNS destination distribution;
   - private endpoint/proxy, ak applicable.
4. Koordinuj nové public source identities s partner allowlistom.
5. Nasadi canary cohortu a sleduj connection metrics aj payment SLI.

### Closure verdict

Recovery je prijatá až keď:

- `ErrorPortAllocation` ostáva nulové pri peak test-e;
- connection churn a retries sú v budgete;
- request `P-884` a opakované samples majú bounded latency;
- partner audit potvrdí presne jednu authorization per idempotency key;
- každá AZ má funkčný expected egress path;
- zakázaný unsolicited inbound path ostáva nedostupný;
- regression test reprodukuje destination-concentration load.

## 13. Ďalšie failure boundaries

### Public NAT je umiestnený bez IGW pathu

NAT resource môže existovať, ale jeho egress subnet nemá správnu default route na IGW alebo EIP/network-border-group contract. Private routes na taký NAT internet nevytvoria.

### Private subnet smeruje priamo na IGW

Resource bez public IPv4 mappingu nebude internet-routable. Route target a address identity musia byť kompatibilné.

### Cross-AZ zonal NAT dependency

NAT-A failure alebo route maintenance ovplyvní aj source AZ-b/AZ-c a môže vytvárať cross-AZ transfer cost.

### Regional NAT nemá expected AZ coverage

Auto-provision je disabled alebo explicit coverage neobsahuje novú AZ. Logical NAT resource existuje, ale affected subnet cohort nemá accepted path.

### NACL povoľuje iba destination port 443

Return packets smerujú na client ephemeral ports a sú stateless rule-setom odmietnuté.

### AWS service calls používajú general NAT

Chýba vhodný endpoint alebo private DNS/policy design. Cost a shared dependency rastú bez business potreby.

### Remote allowlist nepozná novú EIP

Network path a NAT metrics sú zdravé, ale partner odmietne translated source identity. Ide o external authorization boundary.

## 14. Recovery hierarchy

```text
presná flow identita a observation
→ application retry/pooling containment
→ route/NAT/address correction
→ bounded capacity alebo AZ-coverage expansion
→ architecture change: regional/zonal/endpoints/proxy
→ partner allowlist reconciliation
→ business a forbidden-outcome verification
```

NAT delete/recreate alebo default-route zmena je vysoký-blast-radius zásah a nemá byť prvý troubleshooting krok.

## 15. Earlier controls

- versionovaný egress architecture a EIP inventory;
- explicitný NAT availability/connectivity mode;
- AZ route conformance tests;
- connection pooling a retry budgets;
- NAT metrics alarms vrátane `ErrorPortAllocation`;
- destination concentration/load test;
- partner allowlist change workflow;
- endpoint substitution review pre AWS services;
- synthetic outbound test z každej source AZ;
- business idempotency nezávislá od network retry behavioru.

## Referenčné rozlíšenia

| Otázka | Observation |
|---|---|
| Má resource internet-routable identity? | public/EIP/IPv6 ENI attributes |
| Ktorý gateway sa vybral? | effective route table a selected route |
| Aký NAT model platí? | connectivity type + availability mode |
| Ktorá source IP vidí partner? | NAT address/EIP a partner logs |
| Je problém capacity? | connection a port-allocation metrics |
| Je return path blokovaný? | NACL/Flow Logs/route observations |
| Je request business-safe? | transaction a idempotency audit |

## Kontrolné otázky

1. Prečo IGW attachment sám nevytvorí internet connectivity?
2. Aký je rozdiel medzi public a private NAT connectivity type?
3. Aký je rozdiel medzi zonal a regional NAT availability mode?
4. Prečo NAT nie je inbound load balancer ani firewall?
5. Ako connection pooling ovplyvňuje NAT port capacity?
6. Čo presne znamená `ErrorPortAllocation`?
7. Prečo môže scale-out NAT exhaustion zhoršiť?
8. Ako NACL return rules ovplyvňujú outbound HTTPS flow?
9. Kedy môže VPC endpoint nahradiť NAT path?
10. Ako overíš recovery bez duplicate payment authorization?

## Glossary impact

Relevantné pojmy: internet-egress subject, IGW path subject, NAT connectivity type, NAT availability mode, zonal NAT Gateway, regional NAT Gateway, translated flow subject, NAT address generation, destination-tuple concentration, NAT port-allocation verdict, egress AZ coverage, partner allowlist boundary a egress recovery closure.

## Oficiálna dokumentácia

- [Internet gateways](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html)
- [NAT gateways](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)
- [CreateNatGateway API](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_CreateNatGateway.html)
- [NAT gateway metrics](https://docs.aws.amazon.com/vpc/latest/userguide/metrics-dimensions-nat-gateway.html)
- [Troubleshoot NAT gateways](https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-troubleshooting.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: VPC, subnets a route tables](vpc-subnets-route-tables.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Security Groups a Network ACLs →](security-groups-network-acls.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
