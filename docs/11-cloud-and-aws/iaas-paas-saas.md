# IaaS, PaaS a SaaS

IaaS, PaaS a SaaS opisujú, ktorú časť technologického stacku prevádzkuje provider a ktorú zákazník. Nejde o tri presne oddelené produktové kategórie; moderné cloud služby často kombinujú viac vrstiev. Užitočný mentálny model je **ownership a responsibility boundary**, nie marketingový názov služby.

## 1. Celý service stack

Zjednodušený stack:

```text
business data a business process
application
runtime a middleware
data platform
operating system
virtualization/container platform
compute, storage a network
physical datacenter
```

Pri každej službe sa pýtaj:

- kto provisionuje,
- kto patchuje,
- kto škáluje,
- kto zálohuje,
- kto monitoruje,
- kto rieši incident,
- kto riadi identity a data access,
- aký je exit/portability model.

## 2. On-premises baseline

Pri vlastnej infraštruktúre organizácia typicky vlastní:

- budovu alebo colocation contract,
- power/cooling,
- physical network a servers,
- storage,
- hypervisor,
- OS,
- runtime,
- application,
- data,
- monitoring, backup a disaster recovery.

Outsourcing datacentra alebo hardware supportu môže responsibility rozdeliť, ale organizácia stále koordinuje väčšinu lifecycle-u.

## 3. IaaS

**Infrastructure as a Service** poskytuje virtualizované compute, network a storage primitives.

Provider typicky vlastní:

- physical datacenter,
- physical servers a network,
- virtualization/control plane,
- základnú availability služby podľa contractu.

Zákazník typicky vlastní:

- guest OS alebo machine image,
- patching OS a packages,
- firewall/security groups a routing configuration,
- runtime a application,
- IAM usage,
- data, encryption choices a backup,
- autoscaling a high-availability architecture.

Príklady typu služby:

- virtual machines,
- block/object storage primitives,
- virtual networks,
- load-balancer infrastructure podľa konkrétneho management modelu.

## 4. IaaS výhody

- vysoká kontrola nad OS a runtime,
- podpora legacy applications,
- flexibilné network a storage topológie,
- jednoduchšie mapovanie tradičných serverových architektúr,
- možnosť vlastných agents, drivers a kernel settings podľa platformy.

## 5. IaaS trade-offy

- OS patching a image lifecycle,
- capacity a autoscaling,
- configuration drift,
- backup a restore,
- agent/runtime maintenance,
- väčší operational surface,
- riziko snowflake servers.

Lift-and-shift na VM nemení automaticky application na cloud-native systém.

## 6. PaaS

**Platform as a Service** poskytuje managed application alebo data runtime. Provider preberá viac vrstiev, napríklad:

- OS a platform patching,
- runtime control plane,
- základné deployment a scaling primitives,
- platform health,
- časť backup/replication podľa služby.

Zákazník stále vlastní:

- application code alebo schema/configuration,
- business data,
- identity a access design,
- dependency compatibility,
- workload sizing a cost controls,
- application observability,
- backup/restore požiadavky nad rámec platform defaultov,
- business continuity.

Príklady typu služby:

- managed relational database,
- managed Kubernetes control plane,
- application runtime,
- serverless functions,
- managed message broker alebo cache.

Managed Kubernetes je PaaS-like platforma, ale zákazník stále vlastní workloads, images, Kubernetes RBAC, network/security policy, data a mnoho add-ons.

## 7. PaaS výhody

- menší undifferentiated operational workload,
- rýchlejší provisioning,
- built-in patching a HA capabilities podľa služby,
- štandardizované deployment paths,
- menší host-level management surface,
- jednoduchšie využitie cloud integrations.

## 8. PaaS trade-offy

- platform constraints,
- provider-specific APIs a configuration,
- version/support window,
- maintenance windows,
- obmedzený host access,
- migration a data-egress náklady,
- nejasný backup alebo failover contract,
- vyššia jednotková cena za časť managed práce.

Managed neznamená, že provider vlastní application correctness alebo data recovery outcome.

## 9. SaaS

**Software as a Service** poskytuje hotovú application službu používateľovi alebo organizácii.

Provider typicky vlastní:

- application code a runtime,
- platform a infraštruktúru,
- deployment a patching,
- service availability podľa contractu,
- väčšinu interného monitoring-u a operations.

Zákazník typicky vlastní:

- tenant configuration,
- users, groups a permissions,
- identity federation,
- data classification a usage,
- retention/export policy,
- client/device security,
- integration credentials,
- business process a compliance konfiguráciu.

Príklady typu služby:

- email/collaboration platforma,
- CRM,
- issue tracker,
- source-code hosting,
- HR alebo finance application.

## 10. SaaS výhody

- najmenší infrastructure/runtime operations scope,
- rýchle nasadenie,
- centralizované updates,
- predvídateľný subscription model podľa contractu,
- jednoduchý prístup pre používateľov.

## 11. SaaS trade-offy

- minimálna kontrola nad internou implementáciou,
- tenant a feature limits,
- provider outage dependency,
- export/portability a deletion guarantees,
- data residency,
- integration a API rate limits,
- identity alebo configuration mistakes stále zostávajú zákazníckym rizikom.

## 12. Shared responsibility

Každá služba má shared responsibility model. Čím vyššia služba:

```text
IaaS → viac kontroly a viac operations ownershipu
PaaS → viac managed platformy a viac platform constraints
SaaS → hotová application, ale tenant/data/identity ownership zostáva
```

Provider security **of** cloud platformy neznamená zákaznícku security **in** používanej konfigurácii a dátach.

## 13. Responsibility matrix

| Vrstva | On-prem | IaaS | PaaS | SaaS |
|---|---|---|---|---|
| Physical datacenter | zákazník | provider | provider | provider |
| Physical compute/network/storage | zákazník | provider | provider | provider |
| Virtualization/platform control plane | zákazník | provider | provider | provider |
| Guest OS | zákazník | zákazník | provider | provider |
| Runtime/middleware | zákazník | zákazník | provider/shared | provider |
| Application | zákazník | zákazník | zákazník/shared | provider |
| Configuration | zákazník | zákazník | zákazník | zákazník/shared |
| Identity a access | zákazník | shared | shared | shared |
| Business data | zákazník | zákazník | zákazník | zákazník/shared |
| Business continuity outcome | zákazník | shared | shared | shared |

Tabuľka je všeobecný model. Konkrétny contract služby má prednosť.

## 14. Backup responsibility

Najčastejší omyl: „Managed služba je automaticky zálohovaná presne podľa našich potrieb.“

Over:

- či backup existuje,
- čo obsahuje,
- retention,
- RPO/RTO,
- encryption a account boundary,
- region/account isolation,
- point-in-time restore,
- export/off-provider copy,
- restore testing,
- deletion a ransomware scenár.

Provider durability alebo replication nie je automaticky zákaznícky backup.

## 15. High availability responsibility

Managed service môže poskytovať multi-zone capability, ale zákazník musí často:

- zapnúť správny deployment mode,
- zvoliť regions/zones,
- nakonfigurovať clients/retries/timeouts,
- odstrániť single points v application vrstve,
- testovať failover,
- navrhnúť data consistency a DR.

SLA je finančný/service contract, nie automatický architecture design.

## 16. Security responsibility

### IaaS

Veľký zákaznícky scope:

- OS hardening,
- patches,
- network rules,
- identities,
- agents,
- malware/vulnerability management,
- application a data.

### PaaS

Provider preberá host/runtime vrstvu, zákazník rieši:

- service configuration,
- IAM,
- network exposure,
- encryption keys/options,
- application dependencies,
- data a secrets.

### SaaS

Hlavné zákaznícke riziká:

- broad sharing,
- weak federation/MFA,
- overprivileged admins,
- unmanaged integrations,
- retention/data export,
- compromised endpoints.

## 17. Observability responsibility

Provider metrics nepostačujú automaticky na business SLO.

Potrebuješ:

- provider service health,
- platform/resource metrics,
- application telemetry,
- synthetic user-path checks,
- audit logs,
- cost a quota signals,
- external dependency monitoring.

Pri SaaS môže byť observability obmedzená na audit, API, status page a synthetic monitoring.

## 18. Cost model

### IaaS

Platíš za primitives a vlastnú operations kapacitu.

### PaaS

Vyššia service unit cena môže byť vyvážená menším platform toilom a rýchlejšou delivery.

### SaaS

Subscription/per-user/per-feature model presúva väčšinu engineering costu na providera, ale môže rásť s počtom používateľov, dátami a integráciami.

Porovnávaj total cost of ownership:

```text
service bill
+ engineering/operations čas
+ support
+ compliance
+ migration/egress
+ downtime risk
+ opportunity cost
```

## 19. Lock-in a portability

Lock-in nie je binárny.

Typy:

- API lock-in,
- data format a volume lock-in,
- identity/integration lock-in,
- operational skill lock-in,
- commercial/contract lock-in,
- egress a migration-time lock-in.

Vyššia abstrakcia často zvyšuje provider-specific value aj migration cost.

## 20. Výber service modelu

Pýtaj sa:

1. Potrebujeme OS/kernel kontrolu?
2. Je workload legacy alebo cloud-native?
3. Aké sú compliance a data residency požiadavky?
4. Aký je support/upgrade lifecycle?
5. Aké sú RPO/RTO a portability požiadavky?
6. Máme tím na prevádzku nižších vrstiev?
7. Aký je cost pri steady state aj peak-u?
8. Čo sa stane pri provider outage alebo ukončení služby?
9. Ako exportujeme dáta a konfiguráciu?
10. Ktorá vrstva je náš diferenciátor?

## 21. Príklad rozhodnutia

### Interná web aplikácia

Možnosti:

- IaaS VM: maximálna kontrola, viac patching/toil,
- managed Kubernetes/PaaS: platform flexibility, stále vysoký workload/platform scope,
- application PaaS: rýchly deployment, menšia infra kontrola,
- SaaS replacement: žiadny vlastný application runtime, ale proces a integration constraints.

Správna voľba závisí od requirements, nie od toho, ktorý model je „modernejší“.

## 22. Anti-patterny

### Managed znamená bez zodpovednosti

Zákazník stále vlastní configuration, identity, data a business continuity.

### IaaS je vždy lacnejší

Ignoruje operations labor a incident cost.

### SaaS nepotrebuje security review

Tenant permissions, federation a integrations môžu spôsobiť data breach.

### PaaS automaticky poskytuje DR

Replication alebo HA nemusia spĺňať cross-region recovery požiadavky.

### Výber podľa marketingovej kategórie

Konkrétny service contract môže mať inú responsibility boundary.

## 23. Troubleshooting ownership

Pri incidente najprv urč:

```text
customer-controlled layer?
provider-managed service layer?
shared integration boundary?
external dependency?
```

Zachovaj:

- request/correlation IDs,
- timestamps v UTC,
- provider status a support case,
- customer config diff,
- application telemetry,
- network/identity evidence.

Escalácia providerovi bez konkrétneho scope-u a evidence predlžuje recovery.

## 24. Kontrolné otázky

1. Čo IaaS, PaaS a SaaS primárne opisujú?
2. Ktoré vrstvy typicky vlastní zákazník pri IaaS?
3. Prečo managed database stále potrebuje zákaznícky backup model?
4. Ktoré responsibilities zostávajú pri SaaS?
5. Ako sa líši provider availability od business continuity?
6. Prečo treba porovnávať TCO a nie iba service bill?
7. Aké typy lock-inu existujú?
8. Kedy je OS-level kontrola rozhodujúca?
9. Ako sa mení observability pri vyššej service abstrakcii?
10. Ako určíš vlastníka incidentu na shared boundary?

## Glossary impact

Relevantné pojmy: cloud service model, IaaS, PaaS, SaaS, shared responsibility, responsibility boundary, managed service, total cost of ownership, provider lock-in, data portability, customer-managed layer, provider-managed layer a service contract.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Hooks](../10-helm-and-cka/hooks.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
