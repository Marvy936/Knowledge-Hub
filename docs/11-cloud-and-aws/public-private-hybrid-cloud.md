# Public, private a hybrid cloud

Deployment model odpovedá na inú otázku než service model. IaaS, PaaS a SaaS určujú, ktoré technologické vrstvy prevádzkuje provider a ktoré zákazník. Public, private a hybrid cloud určujú, v akých administratívnych a fyzických doménach capability beží a ako sa medzi nimi prenášajú identity, DNS, sieťový traffic, dáta a prevádzkový dôkaz.

Public cloud preto neznamená „server dostupný z internetu“. Workload v AWS môže mať iba private addresses, komunikovať cez private endpoints a neprijímať žiadny unsolicited internet traffic. Private cloud zase nie je automaticky bezpečný iba preto, že hardware patrí organizácii. A hybrid cloud nie je jeden VPN tunnel; je to dlhodobý distribuovaný systém spájajúci najmenej dva odlišné operating a failure domains.

## 1. Exact deployment subject

Atlas Payments capability `CAP-PAY-42` používa AWS account `A42` v `eu-central-1`, VPC `V42` a on-premises lokalitu `DC17`. Customer-facing API beží v AWS, ale settlement ledger `L17` zostáva v privátnej lokalite. Medzi prostrediami existuje Direct Connect generation `DX7` a backup VPN `VPN4`. Federácia má generation `IDF8`, hybrid DNS `DNS12` a application release identifikujú image `I42`, configuration `C42` a credential epoch `SE10`.

Tvrdenie „je to hybrid“ nepreukazuje, že tieto generácie tvoria funkčný systém. Reálny request musí prejsť presnou cestou:

```text
cloud workload identity a source IP
→ VPC route-table verdict
→ Direct Connect alebo VPN attachment
→ BGP prefix selection
→ on-premises firewall
→ ledger listener a TLS identity
→ settlement transaction
→ symetrický return path
```

Ak je jedna boundary nejasná, green stav ostatných komponentov môže vytvoriť false confidence.

## 2. Public cloud ako API-riadená izolovaná doména

Public cloud používa provider-owned fyzickú infraštruktúru a zákazníkom poskytuje logicky izolované accounts, identities, virtual networks a managed services. Hlavnou vlastnosťou nie je internet exposure, ale programovateľný control plane a pool zdieľanej provider capacity.

Lifecycle Atlas workloadu v AWS vyzerá približne takto:

```text
Organization/account a Region
→ IAM a guardrails
→ VPC, subnets, routes a endpoints
→ compute/data service provisioning
→ workload identity a configuration
→ application data plane
→ telemetry, scaling a recovery
```

Provider môže mať zdravý Region, zatiaľ čo Atlas používa nesprávny account, vyčerpaný subnet, zablokovaný endpoint policy alebo neplatnú quota. Pri každom príkaze preto explicitne uvádzame account a Region context.

```bash
aws sts get-caller-identity
aws configure get region
aws ec2 describe-vpcs \
  --region eu-central-1 \
  --query 'Vpcs[].{VpcId:VpcId,Cidr:CidrBlock,State:State,Default:IsDefault}'
```

`get-caller-identity` ukáže skutočný AWS principal/account použitý CLI credential chainom. Názov shell profilu nie je dôkaz identity. `configure get region` ukáže lokálny default, ale environment variable alebo command flag ho môže prebiť. `describe-vpcs` potom číta resources v explicitnom Regione. Táto trojica zabraňuje častej chybe, keď operator diagnostikuje správne pomenovaný resource v nesprávnom account-e alebo Regione.

Public cloud umožňuje elastické provisionovanie, no elasticita nie je nekonečná. Subnet IPs, quotas, service capacity, NAT ports alebo database connections sú stále bounded. Public deployment preto potrebuje rovnakú disciplínu capacity a recovery ako private platforma, iba s iným control plane-om.

## 3. Private cloud ako interný cloud operating model

Private cloud je vyhradená platforma pre jednu organizáciu, ktorá poskytuje cloud-like API, self-service, policy enforcement, pooled capacity, metering a štandardizované lifecycle-y. Samotný VMware alebo OpenStack cluster ešte nepreukazuje cloud operating model, ak každý VM provisioning potrebuje manuálny ticket a platforma nemá jednotný image, network, identity a recovery contract.

V zrelom private cloude sa fyzická capacity transformuje na tenant capability:

```text
hardware a facility capacity
→ compute/network/storage platform
→ API a identity
→ images, quotas a policy
→ tenant workload
→ metering a operations
→ platform upgrade a hardware retirement
```

Organizácia tým preberá zodpovednosť, ktorú v public cloude nesie provider: dátové centrum, power, spares, hardware replacement, virtualization security, platform control plane a capacity refresh. Vlastníctvo hardware-u samo osebe negarantuje redundantnú power, moderný patch level, immutable backup alebo 24/7 incident response.

Private deployment je opodstatnený, keď existuje silný locality requirement: veľmi nízka latency k výrobnému zariadeniu, disconnected operation, špecifický hardware alebo regulačná podmienka. Ak jediným dôvodom je všeobecný pocit kontroly, treba porovnať skutočnú platformovú zrelosť a total cost, nie iba cenu serverov.

## 4. Hybrid cloud ako prepojenie dvoch authority domains

Hybrid architecture musí explicitne určiť autoritu nad piatimi oblasťami: identity, DNS, routing, dáta a management. Každá môže mať iného ownera a iný failover model.

Identity flow môže používať workforce federation, workload certificates alebo STS sessions. DNS môže mať public a private hosted zones, on-premises authoritative servers a conditional forwarding. Routing môže kombinovať VPC route tables, Transit Gateway, Direct Connect gateway, BGP a firewall policy. Dáta môžu byť synchrónne, asynchrónne alebo single-writer s replay queue. Management môže zostať centralizovaný, ale workload musí mať definované správanie pri strate central control plane-u.

Hybrid capability preto vznikne až cez celý chain:

```text
authoritative identity a naming
→ redundant network paths
→ deterministic route selection
→ security policy na oboch stranách
→ data consistency a acknowledgement model
→ telemetry correlation
→ disconnected/failover behavior
→ reconciliation a failback
```

## 5. Praktický network inventory

Pri hybride je užitočné vytvoriť machine-readable contract pre každý prefix a flow. Napríklad:

```yaml
flowId: PAY-LEDGER-17
source:
  environment: aws
  account: "100000000042"
  region: eu-central-1
  vpc: vpc-0a42
  subnets:
    - name: payments-a
      cidr: 10.42.16.0/20
      azId: euc1-az1
    - name: payments-b
      cidr: 10.42.32.0/20
      azId: euc1-az2
  securityGroup: sg-payments

destination:
  environment: on-prem
  name: ledger.internal
  address: 10.44.17.20
  port: 5443
  protocol: tcp

paths:
  preferred: direct-connect-dx7
  backup: vpn4

requirements:
  tlsServerName: ledger.internal
  maximumRoundTripMs: 20
  forbiddenSources:
    - 10.42.0.0/24
```

Tento manifest umožní pre-deployment testovať, že nový subnet má forward route, on-premises return route a firewall rule. Bez presného prefix inventory sa „pridali sme subnet do VPC“ môže skončiť one-way connectivity.

## 6. Praktická diagnostika hybrid flowu

Najprv z affected workloadu získaj DNS a connection evidence:

```bash
getent ahostsv4 ledger.internal
nc -vz -w 3 ledger.internal 5443
openssl s_client \
  -connect ledger.internal:5443 \
  -servername ledger.internal \
  -brief </dev/null
```

`getent` ukazuje resolver-visible addresses z rovnakého runtime contextu ako aplikácia. `nc` testuje TCP establishment, nie TLS alebo application authorization. `openssl s_client` pridá TLS handshake a server-name validation evidence. Úspešný TLS ešte nepreukazuje settlement request.

Na AWS strane identifikuj exact ENI, subnet a route table:

```bash
aws ec2 describe-network-interfaces \
  --network-interface-ids eni-0pay42 \
  --region eu-central-1 \
  --query 'NetworkInterfaces[0].{PrivateIp:PrivateIpAddress,Subnet:SubnetId,Vpc:VpcId,Groups:Groups[].GroupId}'

aws ec2 describe-route-tables \
  --region eu-central-1 \
  --filters Name=association.subnet-id,Values=subnet-0payb \
  --query 'RouteTables[0].Routes'
```

Ak subnet nemá explicitnú association, treba skontrolovať main route table. Route do `10.44.0.0/16` musí smerovať na intended Transit/virtual gateway alebo attachment. Samotná route `active` nepreukazuje, že BGP a on-premises return path poznajú source prefix.

Direct Connect evidence:

```bash
aws directconnect describe-virtual-interfaces \
  --region eu-central-1 \
  --query 'virtualInterfaces[].{Id:virtualInterfaceId,State:virtualInterfaceState,Bgp:bgpPeers[].bgpStatus,Vlan:vlan}'
```

Green virtual interface a established BGP dokazujú session state. Nehovoria, že konkrétny prefix je importovaný a preferovaný na oboch stranách. Preto treba porovnať advertised/received routes na routers a firewall connection logs.

VPC Flow Logs môžu pomôcť rozlíšiť SG/NACL reject od trafficu, ktorý VPC opustil. Flow Log `ACCEPT` však nepreukazuje remote firewall ani application response. Každý observation point musí byť spojený s rovnakým source/destination tuple a časom.

## 7. Hybrid identity a credential lifecycle

Dlhodobý access key uložený v on-premises configuration je slabý hybrid identity model. Preferovaný flow používa federáciu alebo workload certificate, z ktorých vznikne krátkodobá cloud session:

```text
on-prem workload identity
→ trusted issuer alebo certificate authority
→ STS alebo service-specific exchange
→ short-lived role session
→ exact API request
→ CloudTrail actor evidence
```

Runtime má logovať bezpečnú session identity a expiry, nie secret value. Pri strate identity linky musí byť definované, ktoré lokálne operácie môžu pokračovať a ktoré musia fail-closed. Ak settlement vyžaduje online autorizáciu, cache starého credentialu nesmie nekonečne predlžovať authority po revocation.

## 8. Hybrid DNS bez implicitnej mágie

DNS flow má vlastný control path:

```text
application resolver
→ local cache a search rules
→ conditional forwarding decision
→ Route 53 Resolver alebo on-prem DNS
→ authoritative zone
→ response a TTL
→ selected connection address
```

AWS private hosted zone môže byť authoritative iba pre associated VPCs. On-premises clients typicky potrebujú Route 53 Resolver inbound endpoint a forwarding rule. AWS clients querying on-prem namespace potrebujú outbound endpoint alebo iný resolver design.

Diagnostika musí bežať z affected networku:

```bash
dig ledger.internal A

dig @10.42.8.10 ledger.internal A +noall +answer +authority
```

Prvý príkaz testuje bežný resolver path. Druhý testuje konkrétny resolver endpoint. Ak druhý funguje a prvý nie, problém môže byť local resolver alebo forwarding policy. Ak lookup funguje, stále treba overiť route, TLS a application.

## 9. Hybrid data a acknowledgement contract

Najťažšia časť hybridu často nie je sieť, ale data authority. Synchronous write cez WAN zjednodušuje niektoré consistency vlastnosti, ale pridáva latency a spraví WAN súčasťou availability pathu. Asynchronous event alebo replication model oddeľuje availability, ale vytvára lag, replay a conflict requirements.

Pre settlement flow musí byť jasné, kedy cloud API môže klientovi potvrdiť úspech. Ak potvrdí payment pred durable zápisom v on-prem ledgeri, výpadok linky vytvorí accepted-but-not-settled cohort. Bez durable outboxu, idempotency key a reconciliation cursoru je recovery nejasná.

Bezpečnejší model môže vyzerať takto:

```text
payment accepted
→ cloud database transaction + outbox commit
→ durable acknowledgement klientovi
→ asynchronous ledger delivery
→ idempotent ledger apply
→ settlement confirmation
→ reconciliation of overdue outbox records
```

Takýto model mení business semantics: „accepted“ a „settled“ sú dva stavy. Je však explicitnejší a odolnejší voči WAN incidentu než skrytý synchronous dependency bez timeout/retry contractu.

## 10. Worked incident: circuits sú green, 35 % platieb timeoutuje

Po network maintenance začalo približne 35 % payment requests timeoutovať. Direct Connect `DX7` aj backup VPN `VPN4` boli podľa dashboardov green. Failures však pochádzali iba z workloadov v AZ ID `euc1-az2`. Ledger VIP bol `10.44.17.20:5443`, cloud route generation `RT42-g19`, on-prem BGP generation `BGP17-g31` a firewall generation `FW17-g22`.

Hypotézy zahŕňali preťažený ledger, stale DNS, chýbajúcu route, asymetrický backup path, firewall rule, MTU a stale connection pool. Rozdelenie podľa source subnetu bolo prvé diskriminačné pozorovanie. DNS vracalo rovnakú VIP a TCP SYN opúšťal AWS. On-prem router však neakceptoval nový source prefix `10.42.32.0/20` cez preferred Direct Connect route. Return traffic vybral backup VPN, kde stateful firewall nemal zodpovedajúci connection state a flow odmietol.

Green circuit dokazoval fyzickú a BGP session availability, nie správny round trip pre každý application prefix.

Containment zastavil rollout do affected subnetu a zachoval capacity v ostatných AZs. Tím neotvoril broad CIDR a nepresmeroval celý hybrid traffic cez jeden link. Recovery doplnila prefix do authoritative inventory, publikovala a prijala ho cez oba paths, zosúladila firewall objects a obnovila iba affected connections.

Closure vyžadovala TCP, TLS a payment settlement z každej production AZ. Následný test odpojil Direct Connect a potvrdil VPN failover so symetrickým return pathom. Zakázané source CIDRs zostali blokované a druhá configuration reconciliation bola no-op.

## 11. Disconnected operation a recovery

Hybrid systém musí mať explicitný behavior pri strate spojenia. Niektoré workloads môžu queue-ovať operations lokálne, iné musia odmietnuť nové writes. Najhorší model je, keď každá aplikácia improvizuje vlastný timeout a retry.

Runbook musí vedieť odpovedať, či je cloud alebo private side authoritative writer, aký je posledný spoločný checkpoint, ako sa zastaví second writer, ako sa replayujú queued operations a čo sa stane s credentials vydanými pred incidentom. Failback je data-authority transfer, nie iba obnovenie BGP preferencie.

## 12. Rozhodovací model

Public cloud je vhodný, keď organizácia chce provider scale, service portfolio a API automation bez vlastníctva dátového centra. Private cloud je vhodný, keď locality alebo hardware requirement prevyšuje platformový a capacity cost. Hybrid je vhodný, keď capability reálne potrebuje obe domény a tím dokáže prevádzkovať identity, DNS, routing, data a recovery contract medzi nimi.

Hybrid nemá byť default kompromis medzi dvoma názormi. Je to najnáročnejší deployment model, pretože kombinuje failure surfaces oboch prostredí a pridáva linku medzi nimi.

## Kontrolné otázky

1. Prečo public cloud neznamená public IP alebo internet exposure?
2. Ktoré vlastnosti odlišujú private cloud od tradičnej virtualizačnej platformy?
3. Akých päť authority domains musí hybrid design explicitne vlastniť?
4. Čo dokazuje green Direct Connect virtual interface a čo nepreukazuje?
5. Ako rozlíšiš DNS, route, firewall, TLS a application failure?
6. Prečo musí route contract obsahovať return path a exact source prefix?
7. Ako sa zmení business semantics pri asynchronous cloud-to-ledger delivery?
8. Čo musí preukázať failover test z Direct Connect na VPN?
9. Ako sa zabráni split-brain writerom pri hybrid failbacku?
10. Ktorý deployment model je najjednoduchší pre CAP-PAY-42 a prečo?

## Oficiálna dokumentácia

- [AWS Regions and Availability Zones](https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions-availability-zones.html)
- [AWS Direct Connect User Guide](https://docs.aws.amazon.com/directconnect/latest/UserGuide/Welcome.html)
- [AWS Site-to-Site VPN User Guide](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html)
- [Route 53 Resolver](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html)
- [Hybrid networking best practices](https://docs.aws.amazon.com/prescriptive-guidance/latest/hybrid-networking/welcome.html)
- [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/reference/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: IaaS, PaaS a SaaS](iaas-paas-saas.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Regions a Availability Zones →](regions-availability-zones.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
