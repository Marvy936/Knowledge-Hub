# Security Groups a Network ACLs

Security Groups (SG) a Network Access Control Lists (NACL) sú dve rozdielne VPC traffic-control vrstvy. Security Group je stateful allow-list priradený k network interface/resource-u. Network ACL je stateless ordered allow/deny list aplikovaný na subnet boundary. Správny návrh používa každú vrstvu na jej účel a pri diagnostike overuje oba smery trafficu.

## 1. Security Group

Security Group je virtual firewall pre resources používajúce ENI-based networking.

Vlastnosti:

- priraďuje sa k network interface-u alebo podporovanému resource-u,
- obsahuje inbound a outbound allow rules,
- nemá explicitné deny rules,
- je stateful,
- všetky rules sa vyhodnocujú ako spoločný allow set,
- zmena rules sa aplikuje na asociované resources podľa service behavioru.

## 2. Stateful behavior

Ak SG povolí connection initiation, return traffic pre túto tracked connection je povolený bez potreby zrkadlovej SG rule.

Príklad:

```text
client → server TCP/443 povolené inbound SG servera
server → client return traffic povolený connection trackingom
```

Stateful neznamená, že nový reverse-direction connection je automaticky povolený.

## 3. Security Group references

Rule môže používať:

- IPv4/IPv6 CIDR,
- prefix list,
- inú Security Group podľa podporovaného same-VPC/cross-connectivity modelu.

SG reference neznamená, že traffic „prechádza cez skupinu“. Identifikuje source alebo destination ENIs asociované s referencovanou SG podľa semantics konkrétnej rule.

## 4. Source a destination identity

Preferuj SG-to-SG rules pre application tiers, keď lifecycle a topology zodpovedajú tomuto modelu.

Príklad:

```text
ALB SG → application SG TCP/8080
application SG → database SG TCP/5432
```

Výhody:

- nezávislosť od dynamických private IPs,
- jasný workload-tier contract,
- menší CIDR blast radius.

## 5. Default Security Group

Default SG typicky umožňuje traffic medzi resources používajúcimi tú istú default SG a má broad outbound rule.

Production resources nemajú používať default SG ako neurčitý shared trust domain. Vytváraj purpose-specific groups.

## 6. Outbound rules

Broad outbound `0.0.0.0/0` je bežný default, ale nie vždy správny production policy.

Egress restriction musí zohľadniť:

- DNS,
- package/image repositories,
- AWS service endpoints,
- telemetry,
- identity/token endpoints,
- third-party APIs,
- certificate revocation alebo time services podľa workloadu.

Príliš úzky egress bez dependency inventory spôsobuje ťažko diagnostikovateľné failures.

## 7. Rule identity a descriptions

Moderné SG rules majú vlastné rule IDs. Používaj descriptions, tags/ownership a IaC source, aby bolo jasné:

- kto rule vlastní,
- prečo existuje,
- source ticket/service,
- expiry pri temporary access,
- expected protocol/path.

## 8. Security Group quotas

Effective scale ovplyvňujú:

- počet SGs na ENI,
- počet rules na SG,
- referenced groups/prefix lists,
- managed service ENIs,
- centralized policy tooling.

Quota increase nie je náhrada za odstránenie duplicitných alebo stale rules.

## 9. Network ACL

Network ACL je subnet-level stateless packet filter.

Vlastnosti:

- každý subnet je asociovaný s jedným NACL,
- jeden NACL môže byť asociovaný s viacerými subnetmi,
- má inbound a outbound rules,
- podporuje allow aj deny,
- rules sa vyhodnocujú podľa rastúceho rule number,
- prvý matching rule rozhodne,
- unmatched traffic skončí default deny.

## 10. Stateless behavior

NACL nepozná connection state. Musí povoliť request aj return path.

Pre TCP service typicky potrebuješ:

- inbound destination service port,
- outbound return ephemeral ports,
- a zrkadlové pravidlá na druhej subnet boundary podľa smeru.

Presný ephemeral port range závisí od client OS/runtime a network path. Nepoužívaj slepo jeden historický rozsah bez overenia.

## 11. Rule ordering

Príklad:

```text
100 DENY 203.0.113.0/24 TCP 443
200 ALLOW 0.0.0.0/0 TCP 443
*   DENY all
```

Specific deny musí mať nižšie rule number než broad allow. Zmena numbering môže neúmyselne zmeniť výsledok.

Nechávaj medzery medzi číslami pre budúce insertion, napríklad 100, 110, 120.

## 12. Default a custom NACL

Default NACL typicky povoľuje broad inbound/outbound traffic. Custom NACL začína restrictive default behaviorom, kým nepridáš rules.

Pri asociácii nového custom NACL môže dôjsť k okamžitému výpadku, ak chýbajú return-path rules.

## 13. Security Group vs NACL

| Vlastnosť | Security Group | Network ACL |
|---|---|---|
| Scope | ENI/resource | Subnet |
| State | Stateful | Stateless |
| Rules | Allow only | Allow a deny |
| Evaluation | Všetky matching allows | Prvý matching rule podľa čísla |
| Return traffic | Connection tracking | Explicitné rules |
| Typický účel | Workload-level least access | Subnet defense-in-depth a coarse deny |

## 14. Defense in depth

Bežný model:

- SG definuje presný workload communication contract,
- NACL poskytuje subnet-level guardrail alebo emergency deny,
- route tables určujú reachability,
- host/application firewall a authentication chránia vyššie vrstvy.

NACL nemá nahrádzať presné SG rules.

## 15. Load balancer path

Pri load balanceri analyzuj dve oddelené connections:

```text
client → load balancer
load balancer → target
```

Over:

- LB SG inbound od clientov,
- LB SG outbound na target port,
- target SG inbound z LB SG,
- NACLs na LB a target subnetoch,
- health-check source/port,
- listener/target-group configuration.

Client IP preservation závisí od load balancer typu/protocolu a nemení základný SG ownership model bez overenia service semantics.

## 16. Referencing SG cez peering alebo Transit Gateway

SG referencing support závisí od connectivity typu, Regionu a konkrétneho ingress/egress modelu. Nezamieňaj route reachability s podporou SG references.

Pri unsupported scenári používaj spravované prefix lists, CIDRs alebo central policy model.

## 17. Prefix lists

Prefix list zoskupuje CIDR prefixes do reusable identity.

Použitie:

- AWS-managed service prefixes,
- customer-managed network groups,
- zníženie duplicity v SG/routes,
- central update contract.

Zmena customer-managed prefix listu môže ovplyvniť veľa resources; potrebuje review a audit.

## 18. Reachability nie je iba firewall

Aj keď SG a NACL povoľujú traffic, connection môže zlyhať pre:

- chýbajúcu route,
- DNS,
- listener/process,
- OS firewall,
- asymmetric return path,
- MTU,
- TLS/application authentication,
- unhealthy load balancer target,
- Network Firewall/proxy policy.

## 19. VPC Flow Logs

Flow Logs pomáhajú identifikovať accepted/rejected traffic podľa ENI/subnet/VPC scope-u.

Použi fields ako:

- source/destination address a port,
- protocol,
- action `ACCEPT`/`REJECT`,
- interface ID,
- traffic path a flow direction podľa zvoleného formátu,
- account/Region/AZ context.

`REJECT` nehovorí automaticky, či blokoval SG alebo NACL. Koreluj s live configuration a pathom.

## 20. Reachability Analyzer a Network Access Analyzer

- Reachability Analyzer modeluje path medzi source a destination a identifikuje blocking component.
- Network Access Analyzer hľadá paths, ktoré spĺňajú alebo porušujú definované access requirements.

Ide o configuration analysis, nie náhradu runtime telemetry alebo application testu.

## 21. Troubleshooting connection timeout

Postup:

```text
DNS a destination IP
→ route path
→ source SG outbound/new connection
→ source subnet NACL outbound
→ intermediate gateway/firewall
→ destination subnet NACL inbound
→ destination SG inbound
→ process listener
→ return path/NACL
```

Pri stateful SG nepotrebuješ zrkadlovú return rule pre tracked connection, ale NACL ju potrebuje.

## 22. Troubleshooting `Connection refused`

`Connection refused` často znamená, že packet dosiahol host/endpoint, ale:

- nič nepočúva na porte,
- service binduje iba na localhost/inú IP,
- host firewall rejectuje,
- load balancer target port je chybný.

Firewall drop typicky vyzerá skôr ako timeout, hoci presný symptom závisí od vrstvy.

## 23. Emergency deny

NACL môže byť užitočný na rýchly subnet-level deny konkrétneho CIDR/protocolu.

Riziká:

- ordered rules,
- stateless return path,
- široký subnet blast radius,
- zablokovanie incident-response alebo management trafficu,
- configuration drift po incidente.

Emergency change musí mať expiry, ownera a rollback validation.

## 24. Multi-account governance

Centralizované controls môžu používať:

- AWS Firewall Manager,
- Organizations policies,
- Config rules,
- Security Hub findings,
- IaC/policy-as-code,
- central prefix lists.

Central policy musí rozlišovať required baseline od application-specific rules a mať exception lifecycle.

## 25. Anti-patterny

### SG `0.0.0.0/0` na management port

Vystavuje SSH/RDP alebo admin API celému internetu.

### NACL ako jediný application firewall

Je subnet-wide, stateless a nepozná workload identity.

### Zrkadlenie každej SG rule do NACL

Zvyšuje duplicitu a failure risk bez jasného benefit modelu.

### Shared SG pre nesúvisiace workloady

Rozširuje implicitný trust a blast radius zmien.

### Dočasná rule bez expiry

Stáva sa trvalým stale accessom.

### Diagnostika iba podľa SG

Ignoruje route, NACL, listener a return path.

## 26. Kontrolné otázky

1. Prečo je Security Group stateful?
2. Prečo SG nepodporuje explicit deny?
3. Ako funguje SG-to-SG reference?
4. Prečo je NACL stateless?
5. Ako sa vyhodnocuje poradie NACL rules?
6. Ktoré return rules potrebuje NACL pre TCP?
7. Ako sa líši timeout od connection refused?
8. Ako analyzuješ load balancer path?
9. Čo dokážu Flow Logs a čo nie?
10. Kedy je vhodný emergency NACL deny?

## Glossary impact

Relevantné pojmy: Security Group, stateful firewall, SG reference, Security Group rule ID, Network ACL, stateless firewall, NACL rule number, ephemeral return ports, VPC Flow Logs, Reachability Analyzer, Network Access Analyzer, prefix list a emergency network deny.

## Oficiálna dokumentácia

- [Security groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [Network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [Infrastructure security in Amazon VPC](https://docs.aws.amazon.com/vpc/latest/userguide/infrastructure-security.html)
- [VPC network inventory and analysis](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-inventory.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Internet Gateway a NAT Gateway](internet-gateway-nat-gateway.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
