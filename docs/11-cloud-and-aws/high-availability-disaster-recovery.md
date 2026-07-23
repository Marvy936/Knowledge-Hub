# High availability a disaster recovery

High availability (HA) a disaster recovery (DR) riešia príbuzné, ale odlišné problémy. HA minimalizuje prerušenie pri očakávateľných lokálnych zlyhaniach v rámci bežného production designu, zatiaľ čo DR obnovuje business capability po udalosti, ktorá poškodila alebo znefunkčnila primárne prostredie, jeho dáta alebo trust model.

```text
HA → služba pokračuje alebo sa automaticky zotaví v primárnom prostredí
DR → služba a dáta sa obnovia v náhradnom stave alebo prostredí podľa RPO/RTO
```

Multi-AZ deployment môže byť vysoko dostupný a pritom nemať použiteľný disaster-recovery plán. Rovnako môže organizácia vlastniť backupy, ale nemať schopnosť obnoviť kompletnú aplikáciu, identity, DNS, certificates, secrets a traffic v požadovanom čase.

## 1. Mentálny model

Availability a recovery treba navrhovať ako jeden end-to-end business capability, nie ako zoznam infraštruktúrnych produktov. Používateľský outcome závisí od application compute-u, state-u, identity, networku, DNS, certificates, artifacts, secrets, observability a ľudí schopných vykonať rozhodnutie.

```text
business service a dependency map
→ failure scope a disaster scenáre
→ RTO/RPO a minimálna funkčná kapacita
→ HA a DR architektúra
→ backup, replication a isolation
→ detection a failover decision
→ recovery a validation
→ traffic cutover
→ failback a post-incident improvement
```

Každý krok má vlastný čas, ownera a failure mode. Ak sa v RTO počíta iba technický restore databázy, ale nie detekcia, schválenie, DNS cutover a business validácia, recovery objective nie je reálne podložený.

## 2. Availability ako user outcome

Availability vyjadruje podiel času alebo operácií, počas ktorých služba spĺňa definovaný úspešný outcome pre oprávneného používateľa. Process, VM alebo health endpoint môže byť dostupný, zatiaľ čo checkout, login alebo data processing zostáva nefunkčný.

Praktická definícia musí uviesť measurement point, scope, success criteria a exclusions. Tiež musí vysvetliť, ako sa klasifikuje partial degradation, planned maintenance, stale response a nedostupnosť iba pre konkrétny Region alebo tenant.

```text
availability = successful valid operations / všetky valid operations
```

## 3. High availability

High availability používa redundantnú kapacitu, health checks, load balancing, automatic replacement a replicated state na obmedzenie výpadku pri zlyhaní komponentu. Cieľom je, aby bežné zlyhanie hosta, instance alebo Availability Zone nevyžadovalo improvizovanú manuálnu obnovu celej služby.

HA má vždy definovaný failure scope. Multi-AZ architektúra môže tolerovať zonal failure, ale nemusí tolerovať regional outage, compromise accountu, logical corruption, zmazanie KMS keyu alebo chybný deployment aplikovaný súčasne do všetkých zón.

## 4. HA nie je DR

HA zvyčajne pracuje s aktuálnym production state-om a automaticky presúva traffic alebo work na redundantný component. DR môže vyžadovať obnovu staršieho dôveryhodného recovery pointu, vytvorenie nového prostredia a explicitné rozhodnutie, ktorý state je autoritatívny.

Rozdiel je kritický pri logical corruption alebo security incidente. Replica môže byť technicky zdravá, ale obsahovať rovnakú poškodenú databázu, malicious configuration alebo kompromitované credentials ako primárne prostredie.

## 5. Disaster a recovery trigger

Disaster je udalosť, ktorá spôsobí neprijateľné prerušenie alebo stratu a vyžaduje aktiváciu recovery plánu. Definícia vychádza z business impactu a tolerancie organizácie, nie iba z názvu technického incidentu.

Regionálny outage môže byť disaster pre jednu službu a iba lokálna degradácia pre inú, ktorá beží active-active vo viacerých lokalitách. Naopak hromadné zmazanie dát alebo kompromitácia deployment pipeline môže byť disaster aj vtedy, keď všetky AWS služby a Availability Zones fungujú normálne.

## 6. Business Impact Analysis

Business Impact Analysis (BIA) určuje, ktoré business capabilities sú kritické, aký dopad má ich výpadok a v akom poradí sa majú obnovovať. Bez BIA môže technický tím investovať do drahého active-active modelu pre nekritický systém a ponechať bez recovery kritickú identity alebo payment dependency.

BIA má zachytiť maximum tolerable downtime, data-loss toleranciu, právne povinnosti, manuálne workaroundy a minimálnu funkčnú kapacitu. Výsledok sa následne premieta do RTO, RPO, recovery stratégie a rozpočtu.

## 7. Recovery Time Objective

Recovery Time Objective (RTO) je cieľový maximálny čas od definovaného začiatku incidentu po obnovenie konkrétnej business capability. RTO nie je iba čas kopírovania dát alebo spustenia infraštruktúry.

End-to-end čas typicky obsahuje detekciu, eskaláciu, rozhodnutie deklarovať disaster, provisioning, restore alebo promotion state-u, application startup, validation a traffic cutover. RTO 30 minút nie je splnené, ak technický restore trvá 20 minút, ale schválenie a DNS zmena ďalšie dve hodiny.

## 8. Recovery Point Objective

Recovery Point Objective (RPO) je maximálna tolerovaná strata dát vyjadrená časovým rozdielom medzi incidentom a posledným použiteľným recovery pointom. RPO určuje, akú frekvenciu, replication lag alebo transaction capture musí data-protection model podporovať.

Denný backup môže teoreticky zodpovedať RPO 24 hodín, iba ak je posledná záloha dokončená, nepoškodená, dostupná a obnoviteľná. Backup frekvencia sama osebe nepreukazuje RPO, pretože posledný súbor môže byť neúplný alebo jeho decryption key nedostupný.

## 9. RTA a RPA

Recovery Time Actual (RTA) je skutočne nameraný čas obnovy počas testu alebo incidentu. Recovery Point Actual (RPA) opisuje reálny vek alebo množstvo stratených dát po obnove.

Tieto hodnoty sú prevádzkovým dôkazom, či RTO a RPO zodpovedajú realite. Ak RTA pravidelne prekračuje cieľ pre manuálne rozhodovanie alebo RPA prekračuje RPO pre replication lag, deklarovaný recovery contract nie je podporovaný architektúrou ani procesom.

## 10. Backup, replication a DR

Backup je versioned alebo point-in-time kópia state-u určená na obnovu. Replication priebežne prenáša zmeny do ďalšej lokality alebo systému, zatiaľ čo DR je celý people-process-technology mechanizmus obnovenia business služby.

Replication poskytuje nízke RPO a rýchlejší failover, ale môže okamžite preniesť deletion, ransomware-encrypted data alebo logical corruption. Backup môže zachovať starší čistý recovery point, ale jeho restore môže trvať podstatne dlhšie; robustný návrh preto často kombinuje oba mechanizmy.

## 11. Backup contract

Backup je dôveryhodný iba vtedy, keď je jasné, čo obsahuje, kto ho môže zmazať, ako sa šifruje a ako sa obnovuje. Zelený status backup jobu znamená, že workflow dokončil zápis, nie že aplikácia bola úspešne obnovená do konzistentného stavu.

Backup contract má definovať:

- authoritative data a scope;
- cadence, retention a recovery points;
- encryption a key recovery;
- off-account alebo off-environment copy;
- immutability a deletion protection;
- integrity checks;
- catalog a ownership;
- restore procedure a pravidelné testovanie.

Backup uložený v rovnakom account-e a spravovaný rovnakou kompromitovanou admin identity môže byť zmazaný spolu s production dátami.

## 12. Application-consistent recovery

Storage snapshot môže byť crash-consistent, ale application môže vyžadovať koordináciu viacerých databáz, queues alebo filesystems. Obnova jednotlivých volumes z rôznych časových bodov môže vytvoriť technicky čitateľné, ale business nekonzistentné dáta.

Application-consistent recovery definuje transaction boundary, quiesce alebo log-replay mechanizmus a poradie obnovy dependencies. Po restore treba validovať referenčnú integritu, message offsets, external side effects a skutočný business outcome, nie iba to, že process štartuje.

## 13. DR stratégie

Recovery stratégia určuje, koľko prostredia a state-u je pripraveného ešte pred incidentom. Nižšie RTO typicky vyžaduje vyšší steady-state cost, viac replication a častejšie testovanie.

### Backup and restore

Primárny workload beží iba v primárnom prostredí a recovery environment sa vytvorí počas incidentu. Tento model má najnižší priebežný compute cost, ale najvyššiu závislosť od IaC, restore throughputu, artifact availability a okamžitej cloud capacity.

Je vhodný pre menej kritické systémy s hodinovým alebo dlhším RTO. Test musí preukázať, že environment možno skutočne vytvoriť z prázdneho accountu alebo Regionu a že všetky zálohy a keys sú dostupné.

### Pilot light

Pilot light udržiava v recovery lokalite kritický data layer alebo minimálne core services, zatiaľ čo application capacity sa pri incidente rozšíri. RTO je kratšie než pri úplnom restore, pretože najpomalší state a základná infraštruktúra už existujú.

Rizikom je drift a neotestovaný scale-up. Minimal environment môže vyzerať zdravo, ale pri aktivácii naraziť na quotas, subnet capacity, chýbajúce images alebo neaktuálne secrets.

### Warm standby

Warm standby je zmenšená, ale funkčná kópia workloadu, ktorá priebežne prijíma replication a môže byť testovaná synthetics alebo obmedzeným trafficom. Pri disaster sa zvýši capacity a traffic sa presmeruje.

Vyšší steady-state cost prináša nižšie RTO a viac priebežných dôkazov o funkčnosti. Stále však treba testovať, či standby zvládne plný production load a či scale-up neprekročí recovery objective.

### Multi-site active-active

Active-active používa viac lokalít, ktoré súčasne obsluhujú production traffic. Môže poskytovať veľmi nízke RTO, pretože surviving site už beží, ale vyžaduje komplexný routing, data consistency a conflict-resolution model.

Spoločné logical failures, credential compromise alebo chybný deployment môžu zasiahnuť všetky sites naraz. Active-active preto nie je náhrada immutable backupov, isolation boundaries ani security recovery plánu.

## 14. Recovery Region

Recovery Region sa vyberá podľa data residency, service availability, latency, connectivity, quotas, costu a požadovanej geografickej izolácie. Najbližší Region nemusí byť vhodný, ak nepodporuje potrebnú službu, instance family alebo compliance scope.

Region nesmie existovať iba v architektonickom diagrame. Musí mať otestované account bootstrap, IAM, network, KMS, artifacts, quotas, backup access a schopnosť spustiť minimálnu aj plnú recovery kapacitu.

## 15. Cross-Region data replication

Cross-Region replication prenáša state medzi lokalitami a môže výrazne znížiť RPO. Návrh musí vysvetliť, či je replication synchronous alebo asynchronous, ako sa meria lag a čo sa stane pri prerušení linky.

Asynchronous model umožňuje geografickú vzdialenosť s nižším write latency, ale pripúšťa stratu posledných nezreplikovaných zmien. Synchronous model znižuje data loss, no môže zvýšiť latency a vytvoriť spoločný availability dependency medzi lokalitami.

## 16. Logical corruption a replication

Replication nerozlišuje legitímnu zmenu od chybného delete-u alebo corrupted recordu. Ak primárny writer poškodí dáta, chyba sa môže preniesť do všetkých read replicas ešte pred detekciou.

Recovery model preto potrebuje versioned alebo point-in-time recovery mimo live replication pathu. Pri incidente sa najprv určuje posledný dôveryhodný recovery point a až potom sa rozhoduje, či je vhodný failover, PITR alebo čiastočná data reconstruction.

## 17. Traffic routing a cutover

Traffic cutover môže používať DNS failover, global load balancing, anycast edge alebo application-level discovery. Každý mechanizmus má inú detekčnú latency, cache behavior a schopnosť vrátiť traffic späť.

DNS zmena nie je okamžitý globálny switch, pretože resolvers a clients môžu držať cached odpoveď dlhšie než očakávaný TTL. Cutover plán musí riešiť health signal kvalitu, stale clients, certificates, session state, hard-coded endpoints a split traffic počas transition.

## 18. Failover decision

Failover je business a data decision, nie iba technický príkaz. Pred aktiváciou treba vedieť, či je primárny writer skutočne nedostupný, aký state je v recovery lokalite a akú data loss failover spôsobí.

Decision model definuje authority, požadované evidence, automatický alebo manuálny trigger, abort conditions a communication. Automatický regional failover môže znížiť RTO, ale pri network partition alebo nejasnom write ownership vytvoriť split brain.

## 19. Authoritative state

Authoritative state je verzia dát, ktorá sa po incidente považuje za zdroj pravdy pre ďalšie writes. Bez tohto rozhodnutia môžu primárna a recovery lokalita prijímať rozdielne zmeny, ktoré neskôr nemožno bezpečne zlúčiť.

Návrh musí definovať fencing alebo lease mechanizmus, ktorý zabráni starému writeru pokračovať po failover-e. Pri databázach to môže znamenať promotion iba jedného leadera; pri business workflowoch môže byť potrebné zastaviť externé integrations a manuálne reconciliovať side effects.

## 20. Failback

Failback je samostatná migration a recovery operácia. Nejde o mechanické prepnutie DNS späť, pretože recovery lokalita môže po incidente obsahovať najnovší authoritative state.

Bezpečný failback stabilizuje pôvodné prostredie, prenesie alebo synchronizuje zmeny správnym smerom, overí compatibility a až potom vykoná traffic cutover. Musí zachovať rollback cestu a presne určiť, kedy sa write ownership vracia.

## 21. Dependency mapping

Recovery application compute-u nestačí, ak chýba identity provider, DNS, certificate authority, registry, KMS key alebo third-party allowlist. DR plán musí pokrývať celý critical path potrebný na uskutočnenie business operácie.

Dependency map má zachytiť technické aj organizačné dependencies. Ak jediný človek pozná break-glass credential alebo provider support contract nie je dostupný mimo pracovných hodín, recovery capability má ľudský single point of failure.

## 22. Identity a account isolation

Recovery v oddelenom account-e môže znížiť blast radius credential compromise, broad deletion alebo chybnej organization policy. Oddelenie však funguje iba vtedy, keď recovery role, backups a KMS policies nie sú závislé od rovnakého kompromitovaného trust rootu.

Cross-account model musí riešiť delegated recovery roles, break-glass authentication, artifact access, network a DNS. Pravidelné testovanie musí preukázať, že recovery team dokáže získať oprávnenia aj pri nedostupnosti primárneho identity plane-u.

## 23. KMS a key recovery

Encrypted backup bez dostupného decryption keyu je nepoužiteľný. Recovery plán musí preto zahŕňať key policies, replicas alebo vhodný cross-Region key model, ochranu proti deletion a nezávislý prístup recovery role.

Key isolation má trade-off: príliš spoločná policy zvyšuje blast radius, príliš oddelená policy môže počas incidentu zablokovať restore. KMS access sa musí testovať priamo v recovery account-e a Regione, nie iba kontrolou konfigurácie.

## 24. Infrastructure as Code pre DR

IaC umožňuje reprodukovať network, compute, policies a managed services bez ručného klikania. Samotná existencia Terraform alebo CloudFormation súborov však nepreukazuje, že ich možno po mesiacoch použiť v novom Regione alebo account-e.

Recovery IaC potrebuje versionované modules, pinned artifacts, dostupný state alebo bootstrap bez state-u, environment values a policy validation. Pravidelný test má odhaliť removed APIs, provider drift, chýbajúce quotas a resources, ktoré boli manuálne vytvorené mimo source of truth.

## 25. Artifacts, configuration a secrets

Recovery environment musí používať dôveryhodné a dostupné application artifacts. Ak container image existuje iba v regionálnom registry v poškodenom account-e, infraštruktúru možno obnoviť, ale aplikáciu nie.

Artifacts, packages, configuration a secrets preto potrebujú replication alebo nezávislý recovery source. Recovery musí zároveň validovať signatures a provenance, aby security incident neobnovil rovnaký kompromitovaný build.

## 26. Runbook a automation

Runbook spája technické kroky s authority, validation a časovým očakávaním. Mal by vysvetliť trigger, prerequisites, jednotlivé rozhodnutia, expected evidence, abort conditions, rollback a failback.

Automatizácia znižuje manuálnu latency a chyby, ale zväčšuje blast radius nesprávneho príkazu. One-click DR bez pravidelných kontrolovaných testov môže hromadne prepísať routing, policies alebo state rýchlejšie, než tím rozpozná chybu.

## 27. Recovery validation

Infrastructure status `CREATE_COMPLETE` alebo running instances nie sú dôkazom obnovenej business služby. Validation musí prejsť od základných dependencies k synthetics a business transaction, ktorá číta aj zapisuje state podľa recovery contractu.

Praktická validácia kontroluje identity, DNS, TLS, network, application health, data freshness, queue processing a external integrations. Tiež musí potvrdiť, že telemetry a audit fungujú, pretože recovery bez observability vytvára ďalší slepý incident.

## 28. DR testy

DR testovanie má postupovať od diskusie po technický failover. Každá úroveň overuje inú časť capability a nemala by sa zamieňať s plným production dôkazom.

- **Tabletop** overuje role, rozhodnutia, communication a medzery v runbooku.
- **Component restore** overuje konkrétny backup, database alebo secret.
- **Isolated recovery** obnoví celý workload bez production trafficu.
- **Partial failover** presunie obmedzený service, tenant alebo read traffic.
- **Full failover exercise** overí reálny production cutover a business outcome.

Každý test musí merať RTA a RPA a zaznamenať manuálne kroky, chyby a dependency gaps. Úspech scriptu bez business validácie nie je úspešný DR test.

## 29. Operational readiness

Recovery capability degraduje, ak sa netestuje. Quotas, certificates, images, runtime versions, KMS policies a third-party allowlists sa menia aj vtedy, keď sa DR environment aktívne nepoužíva.

Readiness review preto kontroluje backup freshness, capacity, credentials, DNS, support contracts, on-call coverage a monitoring. Výsledky majú mať ownera a deadline; zoznam známych problémov bez remediation je iba dokumentácia nefunkčného plánu.

## 30. Security incident recovery

Pri compromise nemožno automaticky dôverovať existujúcim credentials, images, configuration ani live replicas. Recovery musí začať izoláciou, preservation evidence a rozhodnutím, ktoré trust roots a artifacts zostali dôveryhodné.

Čisté prostredie používa rotované identities, overené artifacts, známe recovery points a kontrolovaný návrat external connectivity. Automatická replication alebo GitOps reconciliation sa môže dočasne zastaviť, aby nepreniesla malicious state do recovery lokality.

## 31. Cost a recovery tiering

Nižšie RTO a RPO spravidla zvyšujú steady-state cost. Viac replication, warm capacity, redundant licenses a 24/7 operational coverage poskytujú rýchlejšiu obnovu, ale nemusia byť odôvodnené pre každý workload.

```text
backup/restore < pilot light < warm standby < active-active
```

Porovnanie musí zahŕňať compute, storage, transfer, licenses, engineering, testovanie a complexity risk. BIA umožňuje použiť drahší model iba tam, kde downtime alebo data loss spôsobuje primerane vysoký dopad.

## 32. End-to-end príklad

Objednávková aplikácia beží Multi-AZ v primárnom Regione, používa managed database a ukladá dokumenty do object storage. HA rieši zonal failure cez redundantné application instances, load balancer a database failover.

DR používa asynchronous cross-Region replication, immutable cross-account backupy a warm standby application capacity. Pri regional outage responder overí replication checkpoint, deklaruje recovery Region ako authoritative writer, zvýši capacity, vykoná synthetic objednávku a až potom presmeruje traffic.

Ak incident spôsobila logical corruption, tím nepromuje najnovšiu repliku automaticky. Vyberie čistý point-in-time recovery point, reconciliuje chýbajúce orders a až následne obnoví writes.

## 33. Troubleshooting recovery

Troubleshooting má rozdeliť RTO na jednotlivé fázy a identifikovať, kde čas alebo failure vznikol. Všeobecné tvrdenie „restore je pomalý“ nepomôže, ak väčšinu času zaberá approval, provisioning, image pull alebo DNS propagation.

```text
detection
→ declaration a approval
→ identity a access
→ infrastructure provisioning
→ data recovery
→ application startup
→ validation
→ traffic cutover
```

Typické scenáre:

- **Recovery environment beží, ale application nefunguje** — over secrets, DNS, KMS, certificates, registry, network a external allowlists.
- **Obnovené dáta sú príliš staré** — over posledný úspešný recovery point, replication lag a backup completeness.
- **DNS failover nepokrýva všetkých clients** — over TTL, resolver cache, hard-coded endpoints a client retry behavior.
- **Failback vytvára konflikty** — zastav dual writes, urč authoritative state a synchronizačný smer pred cutover-om.
- **RTO je prekročené** — zmeraj každú fázu a odstráň najdlhší manuálny alebo technický bottleneck.

## 34. Anti-patterny

### Multi-AZ sa považuje za kompletný DR

Multi-AZ chráni najmä pred zonal failure a niektorými host alebo platform incidentmi. Nepokrýva automaticky regional outage, account compromise, logical corruption ani hromadné zmazanie.

### Replication sa považuje za backup

Replication znižuje lag, ale kopíruje aj škodlivé zmeny. Recovery potrebuje oddelené versioned points, ktoré možno vybrať podľa posledného dôveryhodného času.

### Backup bez restore testu

Backup success dokazuje iba vykonanie backup workflowu. Bez obnovy, decryption a application validation nie je známe, či dáta podporujú požadovaný RTO a RPO.

### Automatický failover bez authoritative-state pravidla

Automatizácia môže aktivovať druhého writera počas network partition a vytvoriť split brain. Failover mechanizmus musí obsahovať fencing, lease alebo iný spôsob jednoznačného write ownershipu.

### Runbook bez failbacku

Dočasný recovery Region sa môže stať dlhodobým neplánovaným production prostredím. Bez synchronizácie, ownershipu a spätného cutover plánu rastie drift a ďalší incident risk.

## 35. Kontrolné otázky

1. Aký je rozdiel medzi high availability a disaster recovery?
2. Prečo dostupný process nemusí znamenať dostupnú business službu?
3. Čo všetko sa musí započítať do RTO?
4. Prečo backup cadence sama nepreukazuje RPO?
5. Ako sa líšia RTA/RPA od RTO/RPO?
6. Prečo replication nenahrádza backup?
7. Aké trade-offy majú backup/restore, pilot light, warm standby a active-active?
8. Kedy môže automatický failover vytvoriť split brain?
9. Čo znamená authoritative state a ako sa vynúti?
10. Prečo je failback samostatná operácia?
11. Ako account a KMS isolation ovplyvňujú security recovery?
12. Prečo IaC súbor bez pravidelného deployment testu nie je DR dôkaz?
13. Čo musí overiť end-to-end recovery validation?
14. Ako logical corruption mení voľbu recovery pointu?
15. Ako zmeriaš, ktorá fáza recovery spôsobila prekročenie RTO?

## Glossary impact

Relevantné pojmy: high availability, disaster recovery, disaster, Business Impact Analysis, RTO, RPO, RTA, RPA, backup, replication, application-consistent recovery, backup and restore, pilot light, warm standby, multi-site active-active, recovery Region, failover, authoritative state, fencing, failback, recovery runbook, recovery exercise a break-glass recovery.

## Oficiálna dokumentácia

- [AWS Well-Architected — Plan for Disaster Recovery](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/plan-for-disaster-recovery-dr.html)
- [High availability is not disaster recovery](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/high-availability-is-not-disaster-recovery.html)
- [Disaster Recovery of Workloads on AWS](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/welcome.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Scalability, elasticity a fault tolerance](scalability-elasticity-fault-tolerance.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: AWS Organizations a accounts →](aws-organizations-accounts.md)
<!-- KNOWLEDGE-NAVIGATION:END -->