# Cloud foundations, resilience and AWS governance glossary entries

## Account vending — AWS

Automatizovaný proces vytvorenia a baseline konfigurácie nového AWS accountu vrátane OU placementu, identity, loggingu, networku, budgets, guardrails a ownership metadata. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Active-active architecture

Architektúra, v ktorej viac lokalít alebo replicas súčasne spracúva production traffic; poskytuje vysokú využiteľnosť redundantnej kapacity, ale vyžaduje consistency, conflict-resolution a split-brain model. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Active-passive architecture

Architektúra, v ktorej primárny component spracúva workload a standby component prevezme úlohu po failover-e; zjednodušuje write ownership za cenu standby driftu a failover latency. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Availability Zone — AWS

Oddelený infraštruktúrny failure domain v rámci AWS Regionu, pozostávajúci z jednej alebo viacerých fyzických lokalít s nezávislejším power, cooling a networking modelom. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## AWS account

Základná AWS resource ownership, IAM, billing, quota, telemetry a blast-radius boundary s vlastným dvanásťmiestnym account ID. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## AWS Organizations

AWS služba na centrálne riadenie kolekcie účtov cez management account, root, OUs, organization policies, consolidated billing a delegated administration. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## AWS Outposts

AWS-managed infrastructure umiestnená v zákazníckej alebo colocation lokalite a prepojená s parent AWS Regionom, určená pre hybridné workloady s locality alebo latency požiadavkami. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## AWS Region

Geografická AWS infraštruktúrna oblasť obsahujúca viac Availability Zones a predstavujúca regionálnu service, data-residency a fault-isolation boundary. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## AWS Shared Responsibility Model

Model rozdeľujúci bezpečnostné a prevádzkové responsibilities medzi AWS ako prevádzkovateľa infraštruktúry a zákazníka ako vlastníka identities, configuration, data a workloadu podľa konkrétnej služby. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## AZ ID — AWS

Stabilný identifikátor fyzickej Availability Zone, napríklad `euc1-az2`, konzistentný naprieč AWS accounts a vhodný na cross-account topology koordináciu. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## AZ name — AWS

Account-visible názov Availability Zone, napríklad `eu-central-1a`, ktorého historické písmeno nemusí mapovať na rovnakú fyzickú zónu v rôznych účtoch. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Backup and restore — DR

Recovery stratégia, pri ktorej sa náhradné prostredie a state obnovujú zo záloh po incidente; má nízky steady-state cost a typicky vyššie RTO. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Break-glass access — AWS

Núdzový, oddelene chránený a auditovaný prístup do kritického AWS accountu používaný pri výpadku bežnej identity cesty alebo incidente. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Bulkhead isolation

Rozdelenie resources, queues, threads, tenants, cells alebo accounts do samostatných poolov, aby failure alebo overload jednej skupiny nevyčerpal celý systém. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Business Impact Analysis — BIA

Proces určujúci kritické business capabilities, dopad výpadku, maximálne tolerované prerušenie, data-loss toleranciu, dependencies a priority obnovy. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Capacity headroom

Rezervovaná nevyužitá kapacita potrebná na absorpciu burstu alebo presun trafficu pri zlyhaní časti systému, napríklad jednej Availability Zone. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Circuit breaker

Resilience pattern, ktorý po prekročení failure prahu dočasne zastaví calls na zlyhávajúcu dependency a neskôr vykoná kontrolované test requests. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Cloud bursting

Hybridný scaling model, pri ktorom workload dočasne rozšíri capacity z private prostredia do public cloudu; vyžaduje runtime, data, identity, networking a licensing kompatibilitu. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Cloud deployment model

Klasifikácia určujúca, kde cloud infraštruktúra beží, komu je určená a ako sa prepája a riadi, napríklad public, private alebo hybrid cloud. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Cloud portability

Schopnosť presunúť workload medzi prostrediami vrátane source, runtime, data, identity, network, observability a operational contracts, nie iba container image-u. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Consolidated billing — AWS

AWS Organizations capability združujúca billing member accounts do centrálneho payer/management scope-u pri zachovaní resource ownershipu v jednotlivých účtoch. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Control inheritance — cloud compliance

Použitie provider-managed controls, napríklad physical security alebo hypervisor patchingu, ako zdedenej časti zákazníckeho compliance programu; nezbavuje zákazníka vlastných configuration a process responsibilities. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Customer responsibility — cloud

Časť service security a operations contractu, ktorú vlastní zákazník, typicky identity, data, application, network configuration, logging, backup a business recovery. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Delegated administrator — AWS Organizations

Member account zaregistrovaný na centralizovanú správu podporovanej AWS služby naprieč organization, aby sa znížil počet operácií vykonávaných v management account-e. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Diagonal scaling

Kombinácia vertical a horizontal scalingu, pri ktorej sa najprv mení veľkosť resource-u a následne počet replicas alebo nodes. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Disaster recovery — DR

People, process a technology capability obnoviť business službu a jej dáta po udalosti presahujúcej bežný high-availability design podľa definovaných RPO a RTO. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Disconnected operation

Schopnosť hybridného alebo edge workloadu pokračovať v definovanom režime pri strate spojenia s central cloud control plane alebo WAN dependency. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Edge cloud

Compute a storage platforma umiestnená bližšie k používateľom, zariadeniam alebo výrobnému procesu pre nízku latency, lokálne spracovanie alebo prerušovanú konektivitu. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Elasticity

Schopnosť systému dynamicky pridávať alebo odoberať kapacitu podľa demandu, provisioning latency, policy, quotas a cost guardrails. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Failback

Riadený návrat workloadu a authoritative state-u z recovery lokality späť do stabilizovaného primárneho prostredia po failover-e. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Failover

Presun trafficu, processingu alebo write ownershipu z nefunkčného primárneho componentu alebo lokality na pripravený náhradný target. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Fault tolerance

Schopnosť systému pokračovať vo funkcii pri zlyhaní componentu prostredníctvom redundancy, replication, automatic failover, isolation a controlled retry. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Global resource — AWS

AWS resource alebo service control scope, ktorý nie je viazaný iba na jeden Region; konkrétne data-plane, endpoint a consistency semantics treba overiť v service dokumentácii. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Graceful degradation

Zámerné zachovanie kritickej funkcie pri výpadku dependency alebo capacity za cenu vypnutia menej dôležitých features alebo zníženia kvality. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## High availability — HA

Architektonická schopnosť minimalizovať prerušenie služby pri očakávateľných component, host alebo zonal failures pomocou redundancy, health checks a failoveru. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Hybrid cloud

Deployment model integrujúci public-cloud services s on-premises, colocation alebo edge resources cez networking, identity, DNS, data a management contracts. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Hybrid connectivity

Network boundary prepájajúca cloud a externé prostredie cez VPN, dedicated link, public endpoint alebo private service endpoint s explicitným routing, encryption a redundancy modelom. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Local Zone — AWS

AWS infrastructure extension približujúca vybrané služby k určitej metropolitnej oblasti pre latency-sensitive workloady a závislá od parent Regionu podľa service modelu. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Log archive account — AWS

Oddelený AWS member account určený na centrálne, dlhodobo chránené uloženie organization-wide audit a security logs. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Management account — AWS Organizations

Najvyšší organization account s billing a Organizations administrative capabilities; SCPs neobmedzujú jeho principals a preto má byť bez bežných workloadov a s minimálnym accessom. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Member account — AWS Organizations

AWS account patriaci do organization a umiestnený pod root alebo OU, s vlastnými resources a IAM, ale podliehajúci relevantným organization policies. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Multi-AZ architecture — AWS

Workload design rozkladajúci compute, networking a stateful capabilities cez viac Availability Zones tak, aby zlyhanie jednej zóny neodstavilo definovanú službu. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Multi-cloud

Používanie services od viacerých cloud providers z obchodných, geografických, regulačných alebo technických dôvodov; samo osebe negarantuje portability ani disaster recovery. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Multi-site active-active — DR

Disaster-recovery stratégia, v ktorej viac geografických lokalít aktívne obsluhuje production traffic a potrebuje cross-site routing, capacity a data consistency model. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Network account — AWS

Centralizovaný AWS account vlastniaci organization network capabilities ako Transit Gateway, hybrid connectivity, DNS resolvers, inspection alebo IPAM. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Organization root — AWS

Najvyšší kontajner AWS Organizations hierarchy, pod ktorým sa nachádzajú OUs a member accounts a z ktorého sa dedia podporované organization policies. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Organizational unit — OU

Logická skupina AWS accounts v Organizations hierarchy určená na spoločné policy a lifecycle riadenie; nie je network ani Region boundary. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Pilot light — DR

Recovery stratégia udržiavajúca v náhradnej lokalite kritický data/core základ, ktorý sa pri incidente rozšíri na plnú application capacity. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Predictive scaling

Elasticity model pripravujúci capacity pred očakávaným demand-om na základe historických vzorov alebo forecastu. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Private cloud

Cloud-like platforma vyhradená jednej organizácii s API, self-service, automation, policy, metering a pooled-capacity operating modelom. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Provider responsibility — cloud

Časť service contractu vlastnená cloud providerom, typicky physical facilities, hardware, host platform, virtualization a managed-service runtime podľa služby. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Public cloud

Provider-operated multi-tenant cloud platforma poskytujúca on-demand services cez logicky izolované accounts a networks; neznamená automaticky public-internet exposure workloadu. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Quarantine OU — AWS

Organizational unit s prísnymi incident alebo decommission guardrails určená na izoláciu member accountu pri zachovaní potrebného response a evidence accessu. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Reactive scaling

Elasticity model, ktorý mení capacity po zistení aktuálneho metric alebo demand signalu, napríklad CPU, request rate alebo queue depth. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Recovery Point Actual — RPA

Skutočný vek alebo bod obnovených dát dosiahnutý pri recovery teste alebo incidente, porovnávaný s cieľovým RPO. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery Point Objective — RPO

Maximálna tolerovaná strata dát vyjadrená časom medzi incidentom a posledným použiteľným recovery pointom. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery Region — AWS

AWS Region pripravený ako cieľ cross-Region disaster recovery vrátane data, capacity, quotas, identity, KMS, networking, artifacts a runbookov. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery Time Actual — RTA

Skutočný čas od začiatku recovery procesu po obnovenie validovanej business capability, porovnávaný s cieľovým RTO. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery Time Objective — RTO

Cieľový maximálny čas na obnovenie definovanej business capability po incidente vrátane detekcie, rozhodnutia, data recovery, startupu, validácie a traffic cutoveru. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Regional endpoint — AWS

Service API alebo data endpoint smerujúci request do konkrétneho AWS Regionu; nesprávny Region môže viesť k prázdnemu inventory, iným quotas alebo deploymentu do nesprávnej lokality. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Regional resource — AWS

Resource s identity a lifecycle scope-om v konkrétnom AWS Regione, napríklad VPC alebo väčšina managed service deployments. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Retry budget

Explicitný limit množstva alebo času retry pokusov, ktorý zabraňuje nekonečným retries a zosilneniu downstream incidentu. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Scalability

Schopnosť systému zvýšiť alebo znížiť spracovateľskú kapacitu bez neprimeraného zhoršenia výkonu, spoľahlivosti alebo nákladov. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Security in the cloud — AWS

Zákaznícka responsibility vrstva zahŕňajúca identity, configuration, data, workload OS/application, logging, backup a recovery podľa použitej AWS služby. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Security of the cloud — AWS

AWS responsibility vrstva zahŕňajúca physical facilities, hardware, host platform, virtualization a provider-managed service infrastructure. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Security tooling account — AWS

Oddelený member account používaný ako delegated administrator a operational scope pre organization-wide security findings, detection a response tooling. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Service control policy — SCP

AWS Organizations guardrail definujúci maximálny permissions envelope pre principals v member accounts; sám access neudeľuje a neobmedzuje management account. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Service responsibility matrix

Tabuľka mapujúca pre konkrétnu cloud službu provider, customer a shared responsibilities v oblastiach compute, identity, network, data, encryption, logging, patching a recovery. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Shared control — cloud

Security alebo operations control, pri ktorom provider poskytuje platform capability a zákazník ju musí správne nakonfigurovať, používať, monitorovať alebo integrovať. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Shared services account — AWS

AWS member account prevádzkujúci organization-wide platform services ako artifacts, directory integrations, CI, observability alebo package mirrors. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Support boundary — cloud

Hranica určujúca, ktorú časť incidentu môže meniť alebo diagnostikovať provider, zákazník alebo third party a aké evidence sú potrebné na efektívnu eskaláciu. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Vertical scaling

Zmena kapacity jedného resource-u, napríklad väčšia VM alebo database instance, bez pridania ďalších replicas. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Horizontal scaling

Pridanie alebo odobratie instances, workers, replicas alebo partitions s potrebným traffic distribution a state coordination modelom. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Warm standby — DR

Recovery stratégia s priebežne bežiacou zmenšenou, ale funkčnou kópiou workloadu v náhradnej lokalite, ktorá sa pri incidente rozšíri a prevezme traffic. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Wavelength Zone — AWS

Špecializovaná AWS edge zóna integrovaná do telekomunikačnej 5G siete pre veľmi nízkolatenčné workloady a obmedzený service katalóg. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Zonal affinity

Preferencia komunikácie a placementu resources v rovnakej Availability Zone pre nižšiu latency alebo transfer cost pri zachovaní cross-zone recovery modelu. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Zonal resource — AWS

Resource viazaný na jednu Availability Zone, napríklad subnet, EC2 instance alebo EBS volume, ktorého lifecycle a attachment constraints sú súčasťou zonal failure modelu. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).
