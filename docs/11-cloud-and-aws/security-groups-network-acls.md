# Security Groups a Network ACLs

Security Groups a Network ACLs nie sú dva varianty toho istého firewallu. Security Group je stateful allow policy viazaná na ENI/resource identity. NACL je stateless ordered allow/deny policy viazaná na subnet boundary. Reálny connection verdict vznikne až po route resolution, vyhodnotení source a destination controls v správnom smere, connection tracking-u, listeneri a return path-e.

## Dominantný lifecycle

```text
communication a isolation intent
→ exact source/destination flow identity
→ route reachability
→ source SG new-flow verdict
→ source-subnet NACL ordered verdict
→ gateway/inspection/NAT path
→ destination-subnet NACL ordered verdict
→ destination SG a connection tracking
→ listener, TLS a application authorization
→ return path a tracked/stateless verdicts
→ business outcome
→ revocation, exception expiry a recovery closure
```

Route hovorí, kam packet smeruje. SG a NACL rozhodujú iba na svojich enforcement boundaries. Application authentication stále zostáva samostatná vrstva.

## Connected Atlas Payments subject

Atlas Payments používa:

```text
source fleet: payments-api-prod
source ENI SG: SG-PAY-APP
source subnet cohorts: SUB-PA, SUB-PB, SUB-PC
source NACLs: NACL-PA, NACL-PB, NACL-PC
NAT path: NAT-A/B/C alebo regional NAT subject
partner destination: 203.0.113.42:443
business request: P-884
```

Exact flow-policy subject musí obsahovať:

```text
account/Region/VPC
source ENI, SG set, private IP, subnet a NACL
original protocol a source/destination ports
selected route a intermediate path
translated tuple, ak používa NAT
source a destination NACL rule generations
source a destination SG rule IDs/generations
new alebo established connection state
listener/TLS/application identity
Flow Log record a request timeline
business/idempotency result
```

Bez direction a tuple identity sa outbound rule ľahko porovná s inbound packetom alebo pre-NAT address s post-NAT observation pointom.

## 1. Security Group je ENI-level stateful allow graph

Security Group:

- je asociovaná s ENI alebo podporovaným resource-om;
- má inbound a outbound allow rules;
- nemá explicitné deny rules;
- vyhodnocuje všetky applicable allows ako spoločný set;
- používa connection tracking pre return traffic;
- môže referencovať CIDR, prefix list alebo inú SG podľa podporovaného connectivity modelu.

SG rule teda reprezentuje:

```text
source alebo destination identity
+ protocol
+ port/range
+ direction
→ allow new flow
```

Ak new connection initiation prejde, tracked response traffic nepotrebuje zrkadlovú SG rule. Nová reverse-direction connection je však nový flow a potrebuje vlastné allow pravidlá.

## 2. SG reference je identity contract, nie transit path

Rule:

```text
SG-ALB → SG-PAY-APP TCP/8080
```

znamená, že target ENI prijíma applicable traffic z ENIs reprezentovaných SG-ALB podľa service semantics. Packet „neprechádza cez“ Security Group.

SG-to-SG model je vhodný pre dynamické fleets, pretože sa neviaže na konkrétne private IPs. Potrebuje však čistý ownership:

- dedicated SG pre workload tier;
- stabilný communication contract;
- descriptions/rule IDs;
- source IaC a owner;
- expiry pri temporary rules;
- kontrolu shared-group blast radiusu.

## 3. Security Group stateful neznamená okamžitú revokáciu každého flowu

Pri incidente rozlišuj:

```text
nový connection attempt
established tracked connection
long-lived TCP/TLS session
application pool connection
```

Rule mutation a successful API response nepreukazujú, že všetky existujúce sessions okamžite prestali prenášať traffic. Revocation closure musí testovať fresh connections aj existing sessions podľa threat modelu.

Pre urgentný coarse deny môže byť vhodná NACL alebo iná stateless enforcement vrstva, ale jej subnet-wide blast radius musí byť explicitný.

## 4. Network ACL je subnet-level ordered stateless verdict

Každý subnet je asociovaný s jednou NACL; jedna NACL môže obsluhovať viac subnetov.

NACL:

- má samostatné inbound a outbound rules;
- podporuje `ALLOW` aj `DENY`;
- vyhodnocuje rules podľa rastúceho rule number;
- prvý matching rule rozhodne;
- unmatched traffic skončí default deny;
- nepozná connection state;
- vyžaduje explicitný forward aj return contract.

NACL rule subject:

```text
subnet boundary
+ direction
+ source/destination CIDR
+ protocol
+ source/destination port semantics
+ rule number
→ allow alebo deny
```

## 5. Stateless return path

Pre outbound HTTPS client flow:

```text
client ephemeral port → destination TCP/443
```

source subnet NACL typicky potrebuje:

```text
outbound: destination TCP/443 allow
inbound: response na client ephemeral destination port allow
```

Destination-side boundaries majú zrkadlovo správne directions.

Presný ephemeral range závisí od client OS/runtime a pathu. Autoritatívny návrh vychádza z actual source-port behavioru a threat modelu, nie zo slepo skopírovaného historického rozsahu.

## 6. Rule ordering je executable policy

Príklad:

```text
100 DENY 203.0.113.0/24 TCP/443
200 ALLOW 0.0.0.0/0 TCP/443
*   DENY all
```

Specific deny funguje iba preto, že sa vyhodnotí pred broad allow. Renumbering alebo insertion môže zmeniť efektívny verdict bez zmeny samotných CIDRs.

NACL review preto musí porovnávať ordered ruleset ako celok, nie iba existenciu jednej allow rule.

## 7. Default a custom NACL

Default NACL býva broad. Nový custom NACL začína restrictive behaviorom, kým nepridáš všetky potrebné directions a ports.

Mechanizmus častého failure:

```text
nový subnet sa asociuje s custom NACL
→ service-port allow existuje
→ return ephemeral rule chýba
→ SYN odíde
→ SYN-ACK je odmietnutý
→ client vidí timeout
```

Association je okamžitá policy zmena pre celý subnet a potrebuje canary a rollback path.

## 8. SG a NACL majú rozdielny purpose

| Boundary | Security Group | Network ACL |
|---|---|---|
| Scope | ENI/resource | subnet |
| State | stateful | stateless |
| Verdicts | allow only | ordered allow/deny |
| Return traffic | tracked response automaticky | explicitná rule |
| Identity | SG/CIDR/prefix list | CIDR/protocol/ports |
| Typický účel | workload least access | subnet guardrail/emergency coarse deny |

NACL nemá nahrádzať precise workload SG. Zrkadlenie každej SG rule do NACL vytvára duplicitu a zvyšuje failure risk bez automatického security benefitu.

## 9. Load balancer vytvára dve connection subjects

Pri ALB/NLB path-e analyzuj oddelene:

```text
client → load balancer listener
load balancer → target port
```

Potrebné observation points:

- LB subnet, NACL a SG;
- listener/protocol/certificate;
- target-group port a health-check path;
- target subnet NACL;
- target ENI SG inbound z LB identity;
- target process listener;
- return paths oboch connections.

Client IP preservation a protocol mode menia visible source fields, ale nemenia potrebu viazať policy na exact observation point.

## 10. Egress dependencies a least privilege

Broad outbound SG je jednoduchý, ale skryje dependency inventory. Restrictive egress musí zahŕňať:

- DNS a time;
- identity/token endpoints;
- image/package repositories;
- telemetry;
- AWS service endpoints;
- Secrets/KMS/configuration paths;
- partner APIs a certificate infrastructure.

Policy closure má overiť povolené dependencies aj forbidden destinations. „Application sa spustila“ nepreukazuje, že všetky runtime alebo recovery paths zostali funkčné.

## 11. Flow Logs a analyzátory

VPC Flow Logs môžu poskytnúť:

- source/destination IP a port;
- protocol;
- interface ID;
- `ACCEPT` alebo `REJECT`;
- AZ/account/traffic-path fields podľa formátu;
- observation window.

Hranice:

- `REJECT` sám nemusí jednoznačne pomenovať SG alebo NACL;
- `ACCEPT` nepreukazuje listener, TLS ani business success;
- aggregation môže skryť packet-level detail;
- pre-NAT/post-NAT observation sa môže líšiť.

Reachability Analyzer modeluje configuration path. Network Access Analyzer hľadá paths podľa access requirements. Ani jeden nenahrádza runtime connection test a application evidence.

## 12. Worked incident — NACL blokuje return ephemeral ports iba v AZ-c

### Symptóm

Po prijatí `SUB-PC` do production fleet:

```text
HTTPS calls na PSP fungujú z AZ-a a AZ-b
rovnaký binary a SG v AZ-c timeoutuje
DNS je rovnaké
NAT-C je available
Flow Logs ukazujú outbound attempts
```

### Exact subject

```text
source ENI: ENI-P42C
source SG: SG-PAY-APP generation 31
source subnet: SUB-PC
source NACL: NACL-PC generation 7
original flow: 10.42.48.27:53144 → 203.0.113.42:443
route/NAT: RT-PC → NAT-C
business request: P-884
```

### Competing hypotheses

1. SG-PAY-APP outbound rule chýba.
2. Partner blokuje NAT-C EIP.
3. NAT-C port allocation alebo AZ path zlyháva.
4. NACL-PC outbound rule blokuje TCP/443.
5. NACL-PC inbound return rule blokuje destination port `53144`.
6. DNS/TLS je odlišné iba v AZ-c.
7. Host firewall alebo application socket pool zlyháva.
8. Route association SUB-PC je nesprávna.

### Discriminating observations

- SG ID a effective outbound allow sú identické s healthy cohortami.
- RT-PC a NAT-C path sú správne; NAT metrics nemajú port-allocation errors.
- Partner log vidí SYN/connection attempt z NAT-C EIP.
- NACL-PC má outbound allow na destination 443.
- NACL-PC inbound umožňuje iba destination 443, nie client ephemeral range.
- Flow evidence koreluje return packet s `REJECT` na affected subnet path.

Causal chain:

```text
client SYN z portu 53144
→ outbound NACL TCP/443 allow
→ NAT a partner
→ SYN-ACK sa vracia na client port 53144
→ inbound NACL-PC nemá matching allow
→ default deny
→ client timeout
```

### Containment

- odober SUB-PC z nového ASG rollout/scale placementu;
- zachovaj NACL generation, Flow Logs, CloudTrail a source-port sample;
- nepovoľuj `ALL 0.0.0.0/0` bez bounded review;
- zachovaj healthy serving capacity v AZ-a/AZ-b.

### Authoritative recovery

1. Urči actual ephemeral port contract pre používaný OS/runtime.
2. Uprav IaC pre inbound return rule s najmenším udržateľným scope-om.
3. Aplikuj zmenu s explicitným rule number a rollback planom.
4. Testuj fresh TCP/TLS connections z SUB-PC.
5. Over allowed partner path aj forbidden inbound/new reverse connection.
6. Vytvor canary instance a payment request pred plným fleet admission.

### Closure verdict

Incident je uzavretý až keď:

- fresh HTTPS flows fungujú z každej AZ;
- NACL ordered ruleset zodpovedá IaC;
- SG least-access contract ostal nezmenený;
- unsolicited inbound a forbidden destinations ostávajú blokované;
- request `P-884` má presne jeden authorization outcome;
- subnet conformance test overuje forward aj return directions.

## 13. Ďalšie failure boundaries

### Broad SG reference vytvorí shared trust domain

Nesúvisiace workloady zdieľajú rovnakú SG a automaticky získajú communication path. Rule review musí zahŕňať membership inventory SG, nie iba samotnú rule.

### Emergency NACL deny zablokuje management alebo recovery traffic

Subnet-wide deny zastaví aj Systems Manager, DNS, identity alebo evidence export. Emergency change potrebuje ownera, expiry a explicitný recovery-access test.

### SG rule bola odstránená, ale existing session pokračuje

Fresh connection je blocked, no long-lived tracked/application pool session môže prežiť podľa connection state-u. Revocation test musí pozorovať oba subjects.

### Load balancer health funguje, user traffic nie

Health-check source/port môže mať samostatnú allow rule, zatiaľ čo listener-to-target alebo client-to-LB flow používa iný protocol/path.

### `Connection refused` nie je typický silent policy drop

Packet pravdepodobne dosiahol endpoint, ale nič nepočúva, binduje iba localhost, target port je chybný alebo host firewall aktívne rejectuje. Timeout a refused sú rozdielne observation outcomes.

### Prefix list update rozšíri access mnohým SGs

Central reusable identity zmení effective allow graph všetkých consumers. Potrebuje dependency inventory, review a regression test.

## 14. Troubleshooting sequence

```text
exact source/destination tuple a direction
→ route reachability
→ source SG new-flow allow
→ source NACL outbound ordered verdict
→ NAT/TGW/firewall observation
→ destination NACL inbound ordered verdict
→ destination SG allow/connection tracking
→ listener/TLS/application authorization
→ reverse path
→ fresh aj established flow verification
→ business a forbidden outcome
```

Preskakovanie priamo na SG console často ignoruje route, NACL, listener alebo translated address identity.

## 15. Earlier controls

- purpose-specific SGs a rule descriptions/IDs;
- no broad management ports from internet;
- NACL ordered-policy tests vrátane return paths;
- canary association pred subnet-wide NACL rolloutom;
- temporary-rule expiry a owner;
- SG membership inventory pri SG references;
- Flow Logs a configuration analyzers;
- allowed aj forbidden synthetic flows;
- load-balancer two-connection test;
- emergency deny runbook s management/recovery exception validation;
- IaC drift detection pre SGs, NACLs a associations.

## Referenčné rozlíšenia

| Symptóm/otázka | Najbližšia boundary |
|---|---|
| Fresh flow timeoutuje | route, SG, NACL, silent firewall, listener path |
| `Connection refused` | listener/bind/target port/active reject |
| Return traffic chýba | NACL, asymmetry, NAT/stateful inspection |
| Rule existuje, flow stále blocked | direction, tuple, ordering, observation point |
| Rule odstránená, session pokračuje | connection tracking/long-lived session |
| Flow Log `ACCEPT`, app zlyhá | TLS/auth/application/downstream |

## Kontrolné otázky

1. Prečo SG nepotrebuje zrkadlovú return rule pre tracked flow?
2. Prečo NACL return rule potrebuje client ephemeral ports?
3. Ako SG reference reprezentuje workload identity?
4. Ako ordered NACL rules menia effective verdict?
5. Prečo custom NACL association môže spôsobiť okamžitý subnet outage?
6. Ako odlíšiš new flow od established connection pri revokácii?
7. Aké dve connections vytvára load balancer?
8. Čo preukazuje a nepreukazuje Flow Log `ACCEPT`/`REJECT`?
9. Kedy je emergency NACL deny vhodný a aké má riziká?
10. Ako overíš original aj forbidden outcome po oprave?

## Glossary impact

Relevantné pojmy: VPC flow-policy subject, SG effective allow graph, SG membership inventory, tracked connection subject, fresh-flow revocation test, NACL ordered-policy generation, stateless return-path contract, policy observation point, load-balancer dual-connection subject, emergency deny lifecycle a network-policy recovery closure.

## Oficiálna dokumentácia

- [Security groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [Security group connection tracking](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-connection-tracking.html)
- [Network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [Reachability Analyzer](https://docs.aws.amazon.com/vpc/latest/reachability/what-is-reachability-analyzer.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Internet Gateway a NAT Gateway](internet-gateway-nat-gateway.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: EC2 a Auto Scaling →](ec2-auto-scaling.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
