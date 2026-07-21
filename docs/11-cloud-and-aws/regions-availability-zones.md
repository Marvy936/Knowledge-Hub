# Regions a Availability Zones

AWS global infrastructure je navrhnutá ako hierarchia geografických a fault-isolation boundaries. Základnými jednotkami sú **Region** a **Availability Zone (AZ)**. Správny návrh musí rozlišovať, ktoré resources sú regionálne, zonálne alebo globálne, aký failure domain každá vrstva predstavuje a ako sa medzi nimi prenášajú dáta, traffic a control-plane operácie.

## 1. Region

AWS Region je geografická oblasť, v ktorej AWS prevádzkuje viac Availability Zones.

Region je dôležitý pre:

- data residency,
- latency k používateľom a externým systémom,
- service availability,
- compliance,
- pricing,
- account/Region enablement,
- DR a business continuity,
- quota a capacity plánovanie.

Regiony sú navrhnuté ako oddelené failure a administrative domains. Nie všetky služby, features, instance types ani quotas sú dostupné vo všetkých Regionoch.

## 2. Availability Zone

Availability Zone je jedna alebo viac oddelených fyzických lokalít v rámci Regionu s nezávislejším power, cooling a networking failure domainom.

AZs v jednom Regione sú prepojené low-latency, high-throughput a redundant networkingom, ale stále sú navrhnuté tak, aby zlyhanie jednej AZ nemuselo vyradiť ostatné.

Multi-AZ architektúra používa aspoň dve AZ na odstránenie single-AZ failure domainu.

## 3. Region code, AZ name a AZ ID

Príklad:

```text
Region code: eu-central-1
AZ name:     eu-central-1a
AZ ID:       euc1-az2
```

AZ name ako `eu-central-1a` nemusí historicky označovať rovnakú fyzickú AZ vo všetkých AWS účtoch. Pri cross-account koordinácii používaj **AZ ID**, ktoré poskytuje konzistentnú identitu fyzickej zóny.

Použitie:

```bash
aws ec2 describe-availability-zones \
  --region eu-central-1 \
  --query 'AvailabilityZones[].{Name:ZoneName,Id:ZoneId,State:State}'
```

## 4. Region selection

Vyhodnoť:

1. proximity a latency,
2. data residency a sovereignty,
3. service/feature availability,
4. capacity a instance-family availability,
5. pricing a data transfer,
6. compliance programs,
7. connectivity k on-premises a partners,
8. recovery Region,
9. customer requirements,
10. support a operational coverage.

Najbližší Region nie je vždy jediný správny. Môže chýbať potrebná služba, capacity alebo compliance scope.

## 5. Resource scope

### Global resources

Niektoré AWS services alebo ich control planes majú globálny scope. Príklady sa líšia podľa služby a nesmú sa generalizovať bez dokumentácie.

### Regional resources

Existujú v konkrétnom Regione:

- VPC,
- väčšina managed service deployments,
- mnohé load balancers,
- regionálne API endpoints,
- väčšina quotas.

### Zonal resources

Sú viazané na konkrétnu AZ:

- subnet,
- EC2 instance,
- EBS volume,
- niektoré network interfaces,
- zonal capacity reservations.

Architektúra musí vedieť, ktoré závislosti nemožno transparentne presunúť medzi AZ.

## 6. Subnets a AZ

Subnet je viazaný na jednu Availability Zone.

```text
VPC (regional)
├─ subnet-a (AZ-a)
├─ subnet-b (AZ-b)
└─ subnet-c (AZ-c)
```

Multi-AZ application tier potrebuje samostatné subnets v každej použitej AZ. Jeden subnet sa nerozprestiera cez viac AZ.

## 7. Multi-AZ návrh

Minimálny model:

```text
regional load balancer
├─ application capacity v AZ-a
└─ application capacity v AZ-b

regional database service
├─ primary/active component
└─ standby alebo replicas v inej AZ podľa service semantics
```

Potrebné je overiť:

- že každá AZ má dostatočnú capacity,
- že health checks reálne odstránia nefunkčný endpoint,
- že state layer podporuje failover,
- že routing/DNS neblokuje presun,
- že deployment nevyradí všetky AZ naraz,
- že quotas a IP space umožnia recovery.

## 8. Cell a failure isolation

Niektoré veľké služby používajú cell-based alebo partitioned architectures nad rámec Region/AZ modelu. Zákazník však nesmie predpokladať internú service topology, ak nie je súčasťou verejného service contractu.

Vlastný workload môže používať cells:

- každá cell má samostatný compute, data a control scope,
- zákazníci alebo tenants sa priraďujú do cells,
- failure jednej cell neovplyvní celý Region,
- blast radius sa zmenší za cenu vyššej complexity.

## 9. Local Zones

Local Zone približuje vybrané AWS services k veľkým populačným alebo priemyselným centrám.

Použitie:

- latency-sensitive media,
- gaming,
- virtual desktop,
- edge application processing.

Treba overiť:

- dostupné services a instance types,
- parent Region dependency,
- routing a data transfer,
- quota/capacity,
- resilience model.

Local Zone nie je automaticky samostatný Region ani DR boundary.

## 10. Wavelength Zones

Wavelength integruje vybrané AWS capabilities do telekomunikačnej 5G infraštruktúry pre ultra-low-latency use cases. Je to špecializovaná edge placement možnosť s obmedzeným service katalógom a dependency na carrier ecosystem.

## 11. AWS Outposts

Outposts prináša AWS infrastructure a operating model do zákazníckej lokality.

Dôležité hranice:

- local hardware capacity,
- service link k parent Regionu,
- local power/network failure,
- hardware support a replacement,
- disconnected behavior podľa služby,
- data residency a operational responsibility.

Outposts rack v jednom dátovom centre nie je automaticky vysoko dostupný bez redundancie lokality, power, network a capacity.

## 12. Cross-AZ traffic

Cross-AZ communication môže prinášať:

- latency,
- data transfer cost podľa služby a direction,
- dependency na inter-AZ networking,
- väčšiu odolnosť proti zonal failure.

Optimalizácia costu nesmie vytvoriť single-AZ state alebo traffic bottleneck. Posudzuj cost spolu s reliability requirementom.

## 13. Zonal affinity

Niektoré workloady preferujú komunikáciu v rovnakej AZ:

- application a cache,
- compute a zonal storage,
- service endpoints,
- Kubernetes topology-aware routing.

Cieľom je znížiť latency a cross-AZ transfer, ale zachovať failover. Zonal affinity bez cross-zone recovery môže premeniť optimalizáciu na availability riziko.

## 14. AZ capacity

Aj healthy AZ môže mať dočasne obmedzenú kapacitu pre konkrétny instance type alebo service configuration.

Ochrana:

- viac instance families/sizes,
- capacity reservations pre kritické workloady,
- diversified Auto Scaling groups,
- warm capacity,
- multi-AZ placement,
- včasný quota request,
- canary capacity test v recovery Region/AZ.

DR plán, ktorý predpokladá okamžitú neobmedzenú on-demand capacity počas regionálneho incidentu, je slabý.

## 15. Regional service endpoints

SDK/CLI request musí smerovať do správneho Regionu.

Symptómy nesprávneho Regionu:

- resource „neexistuje“,
- prázdny list,
- iná quota,
- iný KMS key alebo Secret,
- deployment do nesprávnej lokality,
- vyššia latency.

Over:

```bash
aws configure get region
aws sts get-caller-identity
aws ec2 describe-regions
```

Identity a Region sú dve odlišné dimenzie requestu.

## 16. Region enablement

Niektoré Regions môžu vyžadovať explicitné enablement na úrovni accountu. Organizational governance musí definovať:

- ktoré Regions sú povolené,
- ako sa blokujú nepovolené deployments,
- kde sú security logging a detection služby,
- ako sa rieši opt-in Region identity/STS behavior,
- či control-plane/global services potrebujú výnimky.

Region deny policy bez dôkladného testovania môže zablokovať global alebo support operácie.

## 17. Data replication medzi AZ a Regionmi

### Multi-AZ

Typicky optimalizuje availability v jednom Regione a používa low-latency inter-AZ connectivity.

### Cross-Region

Používa sa pre:

- disaster recovery,
- geographic proximity,
- sovereignty,
- global read scale,
- isolation od regional failure.

Cross-Region replikácia býva častejšie asynchronous a potrebuje explicitný conflict, lag, failover a failback model.

## 18. Control plane a data plane

Regional service môže mať:

- regionálny control plane,
- zonálne data-plane resources,
- globálny identity alebo DNS component.

Pri incidente rozlišuj:

```text
nedá sa vytvoriť nový resource?
existujúce resource-y stále obsluhujú traffic?
zlyhala jedna AZ alebo celý Region?
ide o service API, dataplane alebo customer configuration?
```

Control-plane degradation nemusí okamžite zastaviť existujúci data plane, ale môže blokovať scale, failover alebo recovery.

## 19. Testing zonal failure

Testuj:

- odstránenie capacity jednej AZ,
- dependency na zonal NAT gateway alebo endpoint,
- databázový failover,
- load-balancer health routing,
- zonal storage attachment,
- DNS/cache behavior,
- deployment a autoscaling počas failure,
- observability a alerting.

Nevypínaj náhodne produkčnú AZ bez runbooku a blast-radius kontroly.

## 20. Anti-patterny

### Viac subnetov v jednej AZ považovaných za Multi-AZ

Stále ide o jeden physical failure domain.

### AZ letter ako cross-account identita

`1a` nemusí historicky označovať rovnakú fyzickú zónu; používaj AZ ID.

### DR Region bez capacity testu

Pri incidente nemusí byť možné vytvoriť požadovaný fleet.

### Cross-AZ cost optimalizácia cez single-AZ databázu

Úspora môže zrušiť availability cieľ.

### Region selection iba podľa latency

Ignoruje compliance, services, price a recovery.

## 21. Troubleshooting

### Resource nie je viditeľný

Over account, role a Region.

### Podarí sa deploy v AZ-a, nie v AZ-b

Over subnet, route, security, IP capacity, instance type a zonal service availability.

### Multi-AZ aplikácia zlyhá pri výpadku jednej AZ

Hľadaj single-AZ dependencies: NAT, database writer, cache, queue consumer, storage, static IP alebo insufficient capacity.

### Cross-account AZ mapping nesedí

Porovnávaj ZoneId, nie iba ZoneName.

### Recovery Region je pripravený, ale data sú staré

Over replication lag, last successful checkpoint, encryption keys a promotion procedure.

## 22. Kontrolné otázky

1. Aký failure domain predstavuje Region a AZ?
2. Prečo subnet patrí iba jednej AZ?
3. Aký je rozdiel medzi AZ name a AZ ID?
4. Čo znamená Multi-AZ pre application, data a capacity vrstvu?
5. Prečo Local Zone nie je automaticky DR Region?
6. Aké trade-offy má cross-AZ traffic?
7. Ako sa líši Multi-AZ a cross-Region replication?
8. Prečo treba testovať capacity v recovery lokalite?
9. Ako rozlíšiš control-plane a data-plane incident?
10. Ktoré single-AZ dependencies často porušia Multi-AZ návrh?

## Glossary impact

Relevantné pojmy: AWS Region, Availability Zone, AZ name, AZ ID, zonal resource, regional resource, global resource, Local Zone, Wavelength Zone, AWS Outposts, Multi-AZ architecture, cross-AZ traffic, zonal affinity, regional endpoint a recovery Region.

## Oficiálna dokumentácia

- [AWS Regions and Availability Zones](https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions-availability-zones.html)
- [Availability Zones](https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-availability-zones.html)
- [AZ IDs](https://docs.aws.amazon.com/global-infrastructure/latest/regions/az-ids.html)
- [AWS fault isolation boundaries](https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/regions.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Public, private a hybrid cloud](public-private-hybrid-cloud.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Shared responsibility model →](shared-responsibility-model.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
