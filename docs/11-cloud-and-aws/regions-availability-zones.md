# Regions a Availability Zones

AWS Region a Availability Zone nie sú iba geografické názvy. Sú to placement, identity a failure-isolation boundaries, ktoré určujú, kde vznikne resource, akú capacity môže použiť, ktoré dependencies môže prežiť a aký recovery path je vôbec možný.

Dominantný model:

```text
business locality, compliance a recovery intent
→ Region a account eligibility
→ zonal/regional/global resource inventory
→ AZ identity a subnet/capacity placement
→ data a traffic topology
→ control-plane a data-plane realization
→ zonal/regional failure observation
→ containment a failover
→ business verification a failback
```

## 1. Exact placement subject

Pre Atlas Payments používame:

```text
capability: CAP-PAY-42
account: A42
primary Region: eu-central-1
recovery Region: eu-west-1
production AZ IDs: euc1-az2, euc1-az3, euc1-az1
subnets: SUB42-a, SUB42-b, SUB42-c
application release: I42/C42/SE10
regional load balancer: ALB42
zonal NAT gateways: NAT42-a/b/c
managed database: DB42, Multi-AZ generation MZ9
object backup copy: BC42 in recovery Region
capacity contract: CAP42
```

Placement verdict sa musí viazať na Region, AZ ID, resource UID/ARN, subnet, release generation a data generation. Samotné `eu-central-1a` nie je spoľahlivá cross-account physical-zone identita.

## 2. Region lifecycle

Region je geografický a administratívny scope pre veľkú časť AWS služieb.

```text
Region selection
→ account enablement a governance
→ service/feature/quota eligibility
→ regional network a service resources
→ zonal placements
→ regional operations a telemetry
→ regional recovery alebo exit
```

Region selection ovplyvňuje:

- data residency a sovereignty;
- latency k users, partners a on-premises systems;
- service a feature availability;
- pricing a data transfer;
- quotas a capacity;
- compliance scope;
- support a operations coverage;
- recovery Region a failback model.

Najbližší Region nemusí byť správny, ak chýba požadovaná služba, capacity, compliance alebo recovery contract.

## 3. Availability Zone lifecycle

Availability Zone je jedna alebo viac oddelených fyzických lokalít v Regione s nezávislejšími power, cooling a networking failure boundaries.

```text
regional workload intent
→ AZ ID a subnet placement
→ zonal compute/storage/network realization
→ cross-AZ service a data dependencies
→ zonal health/capacity observation
→ failover do surviving AZ
→ replacement a rebalancing
```

Multi-AZ znamená viac než „máme viac subnetov“. Každá kritická vrstva musí mať surviving capacity a kompatibilný failover:

- compute;
- load balancing;
- data;
- NAT/egress;
- endpoints;
- cache/queue;
- DNS;
- observability;
- deployment a autoscaling;
- quotas a IP space.

## 4. AZ name a AZ ID

```text
Region code: eu-central-1
AZ name:     eu-central-1a
AZ ID:       euc1-az2
```

AZ ID identifikuje rovnakú fyzickú Availability Zone naprieč AWS accounts. AZ name mapping môže byť account-specific, najmä pre staršie accounts a Regions. Cross-account placement, shared subnets a capacity coordination preto používajú AZ ID.

```bash
aws ec2 describe-availability-zones \
  --region eu-central-1 \
  --query 'AvailabilityZones[].{Name:ZoneName,Id:ZoneId,State:State}'
```

## 5. Resource-scope subject

Resource môže byť global, regional alebo zonal. Scope určuje, aká operácia a failure ho môžu ovplyvniť.

### Zonal

Typicky:

- subnet;
- EC2 instance;
- EBS volume;
- network interface;
- zonal capacity reservation.

Zonal resource nemožno automaticky „presunúť“ do inej AZ bez replacementu, snapshotu, reattachment alebo service-specific migration.

### Regional

Typicky:

- VPC;
- regionálny load balancer contract;
- veľká časť managed services;
- regional API endpoint;
- Region-specific quotas.

Regional resource môže používať zonálne data-plane components. Regionálny názov preto nepreukazuje, že všetky AZ cohorts sú healthy.

### Global alebo multi-Region control

Niektoré services majú global identity, routing alebo control-plane aspects. Presný scope sa overuje podľa konkrétnej služby; „global“ neznamená, že každý data object alebo operation je automaticky multi-Region resilient.

## 6. Subnet a placement

Subnet patrí jednej AZ:

```text
VPC42 (regional)
├─ SUB42-a → euc1-az2
├─ SUB42-b → euc1-az3
└─ SUB42-c → euc1-az1
```

Application tier je Multi-AZ iba vtedy, keď workload môže reálne vytvoriť a obsluhovať capacity vo viacerých AZ. Potrebné sú kompatibilné routes, security controls, endpoints, IP space, load-balancer targets a data dependencies.

## 7. Capacity je súčasť availability

Healthy AZ môže mať nedostatočnú capacity pre konkrétny instance type alebo service configuration. Recovery design preto potrebuje:

- viac kompatibilných instance families/sizes;
- quota headroom;
- IP-address headroom;
- capacity reservations alebo warm capacity podľa criticality;
- diversified Auto Scaling policy;
- testovanú capacity v recovery AZ/Regione;
- explicitný degraded-capacity mode.

Availability architektúra bez capacity contractu môže zlyhať presne v momente, keď sa celý workload snaží presunúť do surviving AZ.

## 8. Cross-AZ traffic a zonal affinity

Cross-AZ traffic môže zvyšovať resilience a zároveň priniesť latency, transfer cost a dependence na inter-AZ networking. Zonal affinity môže znížiť latency/cost, ale nesmie odstrániť failover.

Dobrý contract rozlišuje:

```text
preferred same-AZ path
→ fallback cross-AZ path
→ data consistency a capacity pri failover
→ rebalancing po obnove
```

Optimalizácia costu cez single-AZ database, NAT alebo cache môže zrušiť celý availability cieľ.

## 9. Control plane a data plane

Pri AWS incidente rozlišuj:

```text
control-plane operation
→ create/update/delete/scale/failover request

data-plane operation
→ existujúci request, packet, read/write alebo connection
```

Control-plane degradation môže blokovať nový resource, scale alebo failover, zatiaľ čo existujúce resources naďalej obsluhujú traffic. Data-plane failure môže zasiahnuť jednu AZ cohortu pri funkčnom regional API.

Observation musí zahŕňať oba smery:

- API request IDs, error codes a Region;
- resource health a status transitions;
- per-AZ endpoint a target health;
- packet/data path;
- application a business telemetry.

## 10. Multi-AZ nie je multi-Region

### Multi-AZ

Optimalizuje availability v jednom Regione. Typicky využíva low-latency inter-AZ networking a service-specific synchronous alebo tightly coordinated replication.

### Multi-Region

Používa sa pre regional disaster recovery, global proximity, sovereignty alebo isolation. Potrebuje:

- artifact a configuration replication;
- data replication a lag contract;
- identity, key a secret availability;
- DNS/traffic switch;
- capacity a quotas;
- dependency readiness;
- failover a failback;
- conflict/reconciliation model.

Cross-Region replikácia býva často asynchronous. Green replication status nepreukazuje nulový RPO ani application-consistent recovery.

## 11. Edge placement boundaries

Local Zones, Wavelength Zones a Outposts riešia špecifické latency, locality alebo hybrid use cases. Pri každom over:

- parent Region dependency;
- service catalog a instance availability;
- local capacity;
- network/service-link dependency;
- data transfer a routing;
- disconnected behavior;
- hardware replacement;
- actual failure-isolation contract.

Local Zone alebo jeden Outposts rack nie je automaticky samostatný DR boundary.

## 12. Worked incident: Multi-AZ na papieri, single-AZ outcome

Atlas deklaruje payment API ako Multi-AZ. ALB42 používa targets v troch AZ a DB42 je Multi-AZ. Po strate euc1-az2 však error rate stúpne na 65 % a nové instances v surviving AZ nevzniknú.

### Exact incident subject

```text
incident: INC-AZ-42
failed AZ ID: euc1-az2
healthy AZ IDs: euc1-az3, euc1-az1
ASG launch template: LT42 generation 14
subnet IP inventory: SUB42-b 92 % used, SUB42-c 89 % used
NAT placement: iba NAT42-a v failed AZ
DB42: writer failover complete
application target cohort: T42
quota/capacity contract: CAP42 generation 3
```

### Competing hypotheses

1. ALB nepremenil target selection;
2. application capacity v surviving AZ je nedostatočná;
3. subnet IP space blokuje scale-out;
4. instance family nemá zonálnu capacity;
5. jediný NAT gateway v failed AZ zablokoval dependencies;
6. DB failover endpoint/cache je stale;
7. rollout policy alebo topology rules nedovoľujú rebalancing.

### Discriminating observations

```text
per-AZ ALB target health
→ ASG desired/current/activity failures
→ subnet available IP count
→ EC2 insufficient-capacity/error code
→ route table a NAT target per subnet
→ DB endpoint a connection cohort
→ application dependency requests
```

Finding:

- DB failover bol úspešný;
- ALB odstránil failed targets;
- surviving subnets nemali IP headroom pre požadovaný fleet;
- všetky private subnets zároveň smerovali internet egress na NAT42-a vo failed AZ.

Root cause je zákaznícky single-AZ egress a capacity design, nie regionálny AWS outage.

### Containment

- zastaviť nonessential deployments;
- obmedziť workload na healthy existing capacity;
- znížiť retry amplification;
- zachovať ASG, route, Flow Log a target-health evidence;
- nepresúvať traffic do neovereného recovery Regionu.

### Recovery

1. vytvoriť/aktivovať zonálny NAT v surviving AZ a opraviť routes;
2. uvoľniť alebo rozšíriť subnet IP capacity podľa pre-planned contractu;
3. použiť kompatibilné diversified instance families;
4. obnoviť required replica count;
5. overiť DB connection refresh a dependencies;
6. vykonať payment synthetic a settlement verification;
7. po obnove euc1-az2 rebalansovať bez prekročenia capacity a error budgetu.

### Closure verdict

```text
surviving AZ unesie failure-mode load
každá AZ má independent egress path
ASG môže vytvoriť replacement capacity
payment SLO a settlement outcome sú green
forbidden single-AZ route sa v policy teste neobjaví
zonal-failure drill prejde druhýkrát bez manuálneho zásahu
```

## 13. Regional recovery

Recovery Region musí mať preukázané:

- account/Region enablement;
- service a feature availability;
- quotas;
- deployable artifacts;
- network a identity;
- KMS/secrets;
- data recovery point a restore procedure;
- observability;
- capacity canary;
- traffic switch a failback.

„Terraform je pripravený“ nepreukazuje, že capacity, data a external dependencies sú pripravené.

## 14. Testing failure domains

Bezpečný test postupuje:

```text
expected normal/failure outcome
→ exact resources a AZ IDs
→ bounded fault alebo capacity removal
→ observe control/data plane
→ verify surviving capacity a business outcome
→ restore a rebalancing
→ verify forbidden dependency
```

Testy pokrývajú:

- loss jednej AZ capacity;
- zonal NAT/endpoint dependency;
- database failover;
- load-balancer target removal;
- zonal storage;
- deployment počas failure;
- autoscaling a quotas;
- DNS/cache;
- telemetry coverage.

## 15. Anti-patterny

### Viac subnetov v jednej AZ je Multi-AZ

Stále ide o jeden physical failure domain.

### AZ letter je cross-account identita

Pre cross-account physical-zone coordination používaj AZ ID.

### Recovery Region bez capacity testu

Počas regionálneho incidentu nemusí byť potrebná capacity dostupná.

### Regional service je automaticky odolná voči každej AZ failure

Service môže mať zonálne customer resources alebo dependencies, ktoré sú stále single-AZ.

### Znižovanie cross-AZ costu bez failure analýzy

Cost optimalizácia môže vytvoriť single-AZ data, egress alebo cache bottleneck.

## 16. Troubleshooting chain

```text
account a Region
→ resource scope a ARN/UID
→ AZ ID a subnet
→ control-plane request
→ capacity/quota/IP allocation
→ zonal network/storage/data dependency
→ per-AZ endpoint health
→ application process a data generation
→ user/business outcome
```

Resource „neexistuje“ často znamená wrong account, role alebo Region. Deployment failure iba v jednej AZ vyžaduje porovnať subnet, routes, IP capacity, instance/service capacity a zonal dependencies.

## 17. Kontrolné otázky

1. Čo tvorí exact AWS placement subject?
2. Prečo je AZ ID dôležitý pri cross-account koordinácii?
3. Aký je rozdiel medzi zonal, regional a global scope-om?
4. Čo musí byť Multi-AZ okrem compute vrstvy?
5. Prečo capacity patrí do availability contractu?
6. Ako odlíšiš control-plane a data-plane failure?
7. Aký je rozdiel medzi Multi-AZ a multi-Region recovery?
8. Prečo Local Zone alebo Outposts nie sú automatický DR boundary?
9. Ako overíš single-AZ dependency?
10. Čo musí obsahovať regional recovery acceptance?

## Glossary impact

Relevantné pojmy: AWS placement subject, Region generation, Availability Zone identity, AZ ID, zonal resource subject, regional resource subject, global-control boundary, failure-mode capacity, zonal egress subject, Multi-AZ acceptance verdict, recovery-Region subject, per-AZ endpoint cohort a control-plane/data-plane split.

## Oficiálna dokumentácia

- [AWS Regions and Availability Zones](https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions-availability-zones.html)
- [Availability Zones](https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-availability-zones.html)
- [AZ IDs](https://docs.aws.amazon.com/global-infrastructure/latest/regions/az-ids.html)
- [Regions and Zones — EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Public, private a hybrid cloud](public-private-hybrid-cloud.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Shared responsibility model →](shared-responsibility-model.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
