# High availability a disaster recovery

High availability (HA) a disaster recovery (DR) riešia príbuzné, ale odlišné problémy. HA minimalizuje prerušenie pri očakávateľných lokálnych zlyhaniach. DR obnovuje business capability po udalosti, ktorá presiahla bežný availability design alebo poškodila primárny environment a jeho state.

```text
HA → služba pokračuje alebo sa rýchlo automaticky zotaví v primárnom prostredí
DR → služba a dáta sa obnovia v náhradnom stave alebo prostredí podľa RPO/RTO
```

## 1. Availability

Availability vyjadruje podiel času, počas ktorého služba spĺňa definovaný úspešný user outcome.

Príklad:

```text
availability = successful service time / total measured time
```

Potrebné je definovať:

- čo znamená úspech,
- merané obdobie,
- scope používateľov/Regions,
- planned maintenance,
- partial degradation,
- dependency behavior.

„Process beží“ nie je availability definícia.

## 2. High availability

HA používa:

- redundantnú kapacitu,
- Multi-AZ placement,
- health checks,
- load balancing,
- automatic replacement,
- failover,
- replicated state,
- retry a graceful degradation,
- capacity headroom.

HA návrh má odstrániť single points of failure v rámci definovaného failure scope-u.

## 3. HA nie je DR

Multi-AZ architektúra môže tolerovať:

- instance failure,
- host failure,
- časť network failure,
- jednu Availability Zone,
- planned maintenance.

Nemusí tolerovať:

- regional outage,
- credential compromise,
- logical data corruption,
- ransomware alebo malicious deletion,
- chybný deployment do všetkých AZ,
- account suspension,
- KMS key deletion,
- organizovaný supply-chain incident.

Preto AWS dokumentácia výslovne oddeľuje high availability od disaster recovery.

## 4. Disaster

Disaster je udalosť, ktorá spôsobí neprijateľné prerušenie alebo stratu a vyžaduje aktiváciu recovery planu.

Príklady:

- regional service disruption,
- strata primárneho accountu alebo identity controlu,
- data corruption,
- hromadné zmazanie,
- compromised deployment pipeline,
- dlhodobá strata on-premises lokality,
- regulatorné odpojenie Regionu,
- kritický vendor/service failure.

Disaster sa definuje business dopadom, nie iba technickou kategóriou.

## 5. Business Impact Analysis

Pred technickým návrhom urči:

- kritické business services,
- maximum tolerable downtime,
- data-loss toleranciu,
- závislosti,
- právne a regulačné povinnosti,
- manuálne workaroundy,
- priority obnovy,
- minimálnu funkčnú kapacitu.

BIA určuje, ktoré systémy potrebujú drahší recovery model.

## 6. RTO

**Recovery Time Objective** je cieľový maximálny čas na obnovenie definovanej capability po incidente.

RTO zahŕňa:

- detekciu,
- rozhodnutie aktivovať DR,
- infrastructure provisioning,
- data restore/promotion,
- application startup,
- validation,
- traffic cutover.

RTO 30 minút nie je splnené, ak restore trvá 20 minút, ale rozhodnutie a DNS cutover ďalšie dve hodiny.

## 7. RPO

**Recovery Point Objective** je maximálna tolerovaná strata dát vyjadrená časom.

Príklady:

- RPO 24 hodín → denný backup môže byť dostatočný,
- RPO 15 minút → častejší backup alebo replication,
- near-zero RPO → synchronous alebo veľmi nízkolagová replication s vyššou complexity.

RPO nie je backup frekvencia sama o sebe. Dôležitý je posledný **použiteľný a obnoviteľný** recovery point.

## 8. Recovery Time Actual a Recovery Point Actual

Po teste alebo incidente meraj:

- RTA — skutočný recovery čas,
- RPA — skutočnú stratu/vek obnovenej dátovej verzie.

Ak RTA/RPA pravidelne prekračuje RTO/RPO, cieľ nie je reálne podporovaný.

## 9. Backup, replication a DR

### Backup

Point-in-time alebo versioned copy určená na obnovu.

### Replication

Priebežné kopírovanie state-u do ďalšej lokality alebo systému.

### DR

Celý people/process/technology mechanizmus obnovenia služby.

Replication môže okamžite preniesť logical corruption alebo deletion. Backup môže byť bezpečný, ale pomalý. Robustný návrh často používa oboje.

## 10. Backup requirements

Backup potrebuje:

- scope a authoritative data map,
- encryption,
- access separation,
- off-account alebo off-environment copy,
- immutability alebo deletion protection,
- retention,
- catalog/inventory,
- integrity validation,
- restore testing,
- key a credential recovery.

Backup v rovnakom account-e s rovnakými admin credentials môže zlyhať pri compromise.

## 11. DR stratégie

AWS Well-Architected typicky rozlišuje štyri všeobecné stratégie.

### Backup and restore

Primary workload beží iba v primárnom prostredí. Recovery environment sa vytvorí a data sa obnovia zo záloh.

- najnižší steady-state cost,
- najvyššie RTO,
- RPO podľa backup cadence,
- vysoká závislosť od automatizácie a capacity pri incidente.

### Pilot light

Kritická data a minimálne core components sú pripravené v recovery lokalite; application capacity sa pri incidente rozšíri.

- nižšie RTO než backup/restore,
- stredné náklady,
- potreba testovať scale-up a dependency activation.

### Warm standby

Zmenšená, ale funkčná kópia workloadu beží v recovery lokalite.

- rýchlejší cutover,
- priebežná validácia,
- vyšší cost,
- potreba vedieť zvýšiť capacity.

### Multi-site active-active

Viac lokalít aktívne obsluhuje traffic.

- potenciálne veľmi nízke RTO,
- zložitý data consistency a routing model,
- najvyšší cost a operational complexity,
- spoločné logical failures môžu zasiahnuť obe lokality.

## 12. Recovery Region

Vyber Region podľa:

- geographic a fault isolation,
- data residency,
- latency,
- service/feature availability,
- quotas a capacity,
- connectivity,
- cost,
- organizational policy,
- KMS/key availability,
- operational coverage.

Recovery Region nesmie existovať iba v diagrame. Musí mať overenú deploy a restore capability.

## 13. Cross-Region data replication

Treba definovať:

- synchronous/asynchronous behavior,
- replication lag,
- encryption keys,
- conflict resolution,
- promotion,
- failback,
- deletion/corruption propagation,
- network a transfer cost,
- consistency po cutover-e.

Asynchronous replication môže splniť availability, ale nie near-zero RPO.

## 14. Routing a failover

Traffic cutover môže používať:

- DNS failover,
- global load balancing,
- anycast alebo edge routing,
- application-level discovery,
- client configuration.

Posudzuj:

- health signal kvalitu,
- TTL a caching,
- false failover,
- split traffic,
- stale clients,
- TLS certificates,
- rollback/failback.

DNS change nie je okamžitý globálny switch.

## 15. Failover decision

Definuj:

- kto deklaruje disaster,
- aké evidence sú potrebné,
- automatický alebo manuálny model,
- abort conditions,
- data-loss consequence,
- communication a approval,
- legal/compliance krok,
- failback owner.

Automatic regional failover môže znížiť RTO, ale pri nejasnom state-e vytvoriť split brain alebo data loss.

## 16. Failback

Failback je samostatná recovery operácia, nie „prepnutie späť“.

Potrebuje:

1. stabilizovať pôvodnú lokalitu,
2. rozhodnúť authoritative state,
3. replikovať zmeny späť,
4. overiť compatibility,
5. naplánovať traffic cutover,
6. zachovať rollback možnosť,
7. vykonať post-failback validation.

## 17. Dependency mapping

DR workloadu zlyhá, ak chýba:

- identity provider,
- DNS,
- certificate authority,
- KMS key,
- container/image registry,
- artifact repository,
- secrets,
- CI/CD alebo IaC state,
- third-party API,
- email/SMS provider,
- observability.

Recovery plan musí obsahovať celý critical path.

## 18. Account-level isolation

Recovery v inom AWS account-e môže znížiť riziko:

- credential compromise,
- broad deletion,
- policy chyby,
- quota/cost coupling,
- blast radius management accountu.

Potrebné je vyriešiť:

- cross-account backup access,
- KMS policies,
- delegated recovery roles,
- network a DNS,
- artifact replication,
- break-glass access.

## 19. Infrastructure as Code pre DR

DR environment musí byť reprodukovateľný:

- versionované IaC,
- pinned modules/artifacts,
- remote state recovery,
- configuration a secrets workflow,
- environment-specific values,
- policy validation,
- capacity prerequisites.

IaC, ktoré nebolo dlho spustené, môže zlyhať na removed API, quota alebo module drift.

## 20. Runbook a automation

Runbook má obsahovať:

- trigger a authority,
- prerequisites,
- exact steps,
- validation po každom kroku,
- expected duration,
- rollback/abort,
- contacts a communication,
- evidence collection,
- failback.

Automatizácia musí byť testovaná. Neoverený one-click DR zvyšuje riziko hromadnej zmeny.

## 21. DR testy

Typy:

### Tabletop

Tím prejde scenár, rozhodnutia a runbook bez technického failoveru.

### Component restore

Obnova konkrétnej database, object store alebo secret.

### Isolated recovery test

Celý workload sa obnoví v izolovanom account-e/Region-e bez produkčného trafficu.

### Partial failover

Vybraný service alebo tenant sa presunie do recovery prostredia.

### Full failover exercise

Kontrolovaný presun production trafficu s business validáciou.

Test musí merať RTA/RPA, nie iba „script skončil úspešne“.

## 22. Operational readiness

Pred DR testom over:

- quotas a capacity,
- backup freshness,
- KMS keys,
- credentials,
- DNS a certificates,
- images a packages,
- third-party allowlists,
- monitoring,
- support contracts,
- on-call availability.

## 23. Data corruption

Pri logical corruption:

- replication môže poškodenie šíriť,
- active-active môže konflikt rozšíriť,
- failover na repliku nemusí pomôcť,
- potrebný je point-in-time restore alebo clean recovery point.

DR stratégia musí pokrývať infra failure aj data integrity failure.

## 24. Security incident recovery

Pri compromise:

- nepoužívaj nedôveryhodné credentials,
- izoluj affected accounts/resources,
- zachovaj forensic evidence,
- rotuj trust roots a secrets,
- obnov z dôveryhodných artifacts a backupov,
- validuj supply chain,
- nepovoľ automatickú replikáciu malware/config corruption.

Recovery environment musí mať oddelený trust model.

## 25. Cost model

Vyššia pripravenosť znižuje RTO, ale zvyšuje cost:

```text
backup/restore < pilot light < warm standby < active-active
```

Skutočný cost zahŕňa:

- compute/storage/network,
- replication,
- licenses,
- engineering,
- testing,
- operational coverage,
- complexity a incident risk.

## 26. Anti-patterny

### Multi-AZ = DR

Chráni najmä pred zonal failure, nie pred všetkými regional/logical/account incidentmi.

### Replication = backup

Corruption a deletion sa môžu replikovať.

### Backup bez restore testu

Nie je dôveryhodný recovery mechanism.

### DR environment bez capacity/quota testu

Pri incidente sa nemusí spustiť.

### Automatic failover bez authoritative-state pravidla

Môže vytvoriť split brain.

### Runbook bez failbacku

Recovery sa skončí v dočasnom nestabilnom režime.

## 27. Troubleshooting DR

### Restore je pomalší než RTO

Rozdeľ čas na detection, approval, provisioning, data, startup, validation a routing.

### Recovery environment beží, ale aplikácia nefunguje

Over dependencies, secrets, DNS, KMS, network, certificates a external allowlists.

### Data po failover-e chýbajú

Over replication checkpoint, lag, consistency a write routing pred cutover-om.

### DNS failover nepokrýva všetkých klientov

Over TTL, resolver/client caching, health check a hard-coded endpoints.

### Failback vytvorí konflikty

Urči authoritative writer a synchronizačný smer pred cutover-om.

## 28. Kontrolné otázky

1. Aký je rozdiel medzi HA a DR?
2. Čo vyjadruje RTO a RPO?
3. Prečo je RPA/RTA dôležitý po teste?
4. Ako sa líši backup, replication a DR?
5. Aké sú štyri základné recovery stratégie?
6. Prečo active-active nie je automaticky najlepšie riešenie?
7. Čo musí obsahovať failover decision model?
8. Prečo je failback samostatná operácia?
9. Ako logical corruption mení recovery postup?
10. Prečo musí DR testovať celý dependency chain?

## Glossary impact

Relevantné pojmy: high availability, disaster recovery, disaster, Business Impact Analysis, RTO, RPO, RTA, RPA, backup and restore, pilot light, warm standby, multi-site active-active, recovery Region, failover, failback, recovery runbook, recovery exercise, authoritative state a break-glass recovery.

## Oficiálna dokumentácia

- [Plan for Disaster Recovery](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/plan-for-disaster-recovery-dr.html)
- [High availability is not disaster recovery](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/high-availability-is-not-disaster-recovery.html)
- [Disaster Recovery of Workloads on AWS](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/welcome.html)
