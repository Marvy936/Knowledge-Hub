# Chaos testing

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

## 1. Definícia

Chaos testing je riadené experimentovanie so zlyhaniami, ktorého cieľom je získať dôkaz o resilience systému. Experiment zámerne vytvorí konkrétny fault alebo prevádzkové narušenie a overí, či používateľsky významný steady state zostane v prijateľných hraniciach a či sa systém po odstránení faultu úplne zotaví.

Nejde o náhodné vypínanie komponentov ani o demonštráciu chaos nástroja. Každý experiment má hypotézu, presný target, merateľný oracle, safety controls a následné remediation actions.

```text
riziko a hypotéza
→ definovaný steady state
→ kontrolovaný fault
→ pozorovanie dopadu
→ abort alebo dokončenie
→ recovery observation
→ rozhodnutie
→ trvalé zlepšenie
```

Chaos testing je praktická súčasť chaos engineeringu a resilience engineeringu. Testuje nielen technickú redundanciu, ale aj observability, incident response, runbooky, ownership a recovery procesy.

## 2. Čo chaos experiment skutočne overuje

Bežný funkčný test sa často pýta:

```text
Za očakávaných podmienok vytvorí systém správny výsledok?
```

Chaos experiment sa pýta:

```text
Pri konkrétnom narušení zostane používateľský výsledok
v definovaných hraniciach a systém sa následne zotaví?
```

Príklady testovaných mechanizmov:

- **Redundancia —** traffic sa presunie zo zlyhanej instance alebo zóny.
- **Timeouty a circuit breakers —** pomalá dependency nevyčerpá všetky workers alebo connections.
- **Idempotencia —** retry po nejasnom výsledku nevytvorí duplicitný side effect.
- **Backpressure a load shedding —** overload je kontrolovane odmietnutý namiesto globálneho kolapsu.
- **Autoscaling —** control loop včas zistí potrebu, vytvorí kapacitu a zaradí ju do trafficu.
- **Recovery —** backlog, replikácia a cache sa po fault-e vrátia do normálneho stavu.
- **Operability —** alert, dashboard, runbook a on-call postup vedú k správnej akcii.

## 3. Resilience nie je iba availability

Systém môže zostať „up“, ale zároveň produkovať nesprávne alebo nebezpečné výsledky. Preto steady state nesmie byť definovaný iba cez počet bežiacich procesov.

Resilience môže zahŕňať:

- dostupnosť kritického journey,
- správnosť finančných alebo dátových side effects,
- bounded latency a error rate,
- tenant isolation a authorization,
- zachovanie poradia alebo idempotencie eventov,
- bounded backlog a čas jeho vyprázdnenia,
- graceful degradation,
- RPO a RTO,
- schopnosť operátora problém zistiť a zvládnuť.

Príklad: služba môže počas network partition naďalej vracať HTTP 200, ale zapisovať duplicitné transakcie. Technická availability je zelená, no business steady state je porušený.

## 4. Steady state

Steady state je merateľný používateľský alebo prevádzkový výsledok, ktorý má systém zachovať pred faultom, počas neho a po recovery.

Silné steady-state ukazovatele:

- checkout success rate zostáva nad 99,5 %, 
- p95 latency zostáva pod 500 ms,
- nevznikne žiadna duplicitná platba,
- authorization deny rate pre zakázanú cestu zostane 100 %, 
- backlog neprekročí 50 000 správ a po obnove klesne na normál do 15 minút,
- failover sa dokončí do 60 sekúnd,
- error-budget burn rate neprekročí definovanú hranicu,
- používateľ dostane read-only alebo cached režim namiesto úplného výpadku.

Interné metrics sú užitočné ako diagnostika, ale steady state má byť viazaný na outcome. „Leader election prebehla“ nestačí, ak používateľský write path ostal nefunkčný.

## 5. Hypotéza

Dobrá hypotéza prepája fault, očakávaný výsledok, limit a konkrétny resilience mechanizmus:

```text
Ak nastane X,
systém zachová Y
v limite Z,
pretože funguje mechanizmus M.
```

Príklad:

```text
Ak jedna application instance prestane odpovedať,
readiness kontrola ju vyradí z trafficu do 20 sekúnd,
error rate zostane pod 1 %
a chýbajúca kapacita sa doplní do 2 minút.
```

Hypotéza musí byť vyvrátiteľná. Tvrdenie „systém by mal byť odolný“ neposkytuje oracle ani rozhodnutie.

## 6. Experiment contract

Pred spustením experimentu vytvor explicitný kontrakt:

- **Cieľ —** ktorú resilience vlastnosť a risk testujeme.
- **Hypotéza —** očakávaný výsledok a mechanizmus.
- **Steady-state metrics —** primárne a guardrail signály.
- **Fault —** presný typ, intenzita, smer a trvanie narušenia.
- **Target identity —** konkrétny process, pod, node, dependency, route, tenant alebo region.
- **Environment —** artifact, config, topology, data state a traffic model.
- **Preconditions —** zdravý baseline, dostupná observability a recovery kapacita.
- **Blast radius —** maximálny prípustný rozsah dopadu.
- **Abort criteria —** automatické a manuálne podmienky zastavenia.
- **Kill switch —** mechanizmus nezávislý od fault domainu, ak je to možné.
- **Recovery plan —** ako sa fault odstráni a ako sa overí návrat.
- **Owner a observers —** kto spúšťa, sleduje a rozhoduje.
- **Communication —** informovanie on-call, stakeholders a incident kanálu.
- **Evidence —** metrics, logs, traces, timeline, config a experiment metadata.
- **Remediation closure —** ako sa actions evidujú a experiment opakuje.

Experiment bez kontraktu je neauditovateľný zásah. Aj úspešný výsledok má nízku dôkaznú hodnotu, ak nepoznáme presné podmienky.

## 7. Experiment validity

Chaos experiment môže zlyhať technicky aj metodologicky. Preto výsledok nemá byť iba pass/fail.

Možné výsledky:

- **Hypotéza potvrdená —** fault bol aplikovaný podľa kontraktu a steady state ostal v hraniciach.
- **Hypotéza vyvrátená —** platný experiment ukázal porušenie steady state alebo recovery.
- **Inconclusive —** fault prebehol, ale signál alebo vzorka nestačí na rozhodnutie.
- **Invalid experiment —** fault nezasiahol správny target, baseline nebol zdravý, observability chýbala alebo setup porušil kontrakt.
- **Aborted for safety —** experiment bol zastavený podľa guardrailu; tento výsledok stále poskytuje evidence o limite systému.

Invalid experiment sa nesmie interpretovať ako potvrdená resilience.

## 8. Baseline a preconditions

Pred fault injection over normálny stav. Ak systém už degraduje, experiment nebude vedieť oddeliť pôvodný problém od spôsobeného faultu.

Prechecks typicky potvrdia:

- správny artifact a konfiguráciu,
- dostatočnú zdravú kapacitu,
- stabilné SLI v baseline okne,
- funkčné dashboardy a alerty,
- dostupnosť recovery mechanizmu,
- neprebiehajúci incident alebo konfliktujúca zmena,
- správny target a scope allowlist,
- pripravenosť on-call a kill switchu,
- bezpečný stav dát a backup/recovery podľa rizika.

Baseline interval musí byť dostatočný na zachytenie bežnej variability. Jedna okamžitá zdravá hodnota nemusí byť reprezentatívna.

## 9. Fault model

Fault musí reprezentovať realistický failure mode. Náhodné vypnutie ľubovoľného podu nemusí testovať najdôležitejší risk.

Fault model obsahuje:

- **Failure domain —** process, node, zone, network, dependency, storage, identity alebo človek.
- **Failure mode —** úplný výpadok, vysoká latency, partial error, stale response, corruption alebo resource pressure.
- **Direction —** ingress, egress, client-to-server, server-to-dependency alebo iba jeden segment.
- **Intensity —** percento packet loss, latency distribúcia, CPU limit, počet zasiahnutých replík.
- **Duration —** krátky transient fault alebo dlhodobé narušenie.
- **Correlation —** nezávislá chyba jednej instance alebo spoločný failure viacerých components.
- **Recovery behavior —** automatické odstránenie faultu alebo manuálny zásah.

Často je realistickejší „brownout“ než úplný outage. Pomalé alebo intermittent dependency môže byť nebezpečnejšia než okamžité connection refused, pretože drží resources a spúšťa retries.

## 10. Target identity a scope

Experiment musí zasiahnuť presne zamýšľaný target. V cloud-native prostredí môže názov podu, label selector, namespace alebo service route označovať iný rozsah, než experimentátor predpokladá.

Over:

- target UID alebo stabilnú identitu,
- namespace, cluster, account a region,
- labels/selectors a ich aktuálny match,
- počet zasiahnutých instances,
- traffic cohort alebo tenant,
- dependency route a network direction,
- vylúčené kritické targets,
- experiment correlation label.

Pred spustením vytvor dry-run alebo target preview. Scope expansion mimo allowlistu má experiment automaticky zablokovať.

## 11. Blast radius

Blast radius je maximálny rozsah prijateľného dopadu. Má sa zvoliť ako najmenší scope, ktorý ešte overí hypotézu.

Obmedzenia môžu byť:

- jedna instance alebo pod,
- jedna availability zone,
- jeden read-only workflow,
- jeden izolovaný tenant,
- interní používatelia,
- malé percento trafficu,
- krátke trvanie,
- obmedzený request rate,
- fault iba na non-primary replike,
- staging alebo dedicated resilience environment.

Blast radius zahŕňa aj downstream amplification. Vypnutie jednej instance môže cez retry storm zaťažiť všetky ostatné služby. Preto nestačí počítať iba priamo zasiahnutý target.

## 12. Safety state machine

Bezpečný chaos experiment má explicitné stavy:

```text
planned
→ prechecks
→ armed
→ fault active
→ observing
→ fault removed
→ recovery observing
→ completed / aborted / invalid
→ cleanup verified
```

Každý stav má povolené transitions a timeout. Napríklad experiment nesmie prejsť do `fault active`, ak baseline alebo observability precheck zlyhá.

Safety controls:

- scope allowlist a denylist,
- technický approval podľa rizika,
- automatický experiment timeout,
- independent kill switch,
- live guardrail evaluation,
- emergency traffic shift alebo flag-off,
- rate a intensity limits,
- automatické fault removal,
- cleanup verification,
- zákaz súbehu s iným experimentom alebo rizikovou zmenou,
- evidence o každom state transition.

## 13. Kill switch

Kill switch musí odstrániť fault alebo zastaviť experiment aj vtedy, keď zlyhá hlavná orchestration cesta. Ak chaos controller a target zdieľajú rovnaký fault domain, experiment môže stratiť schopnosť sám seba ukončiť.

Dobrý kill switch:

- je dostupný z nezávislého control pathu,
- má minimálne potrebné oprávnenia,
- je otestovaný pred experimentom,
- má audit trail,
- odstráni fault idempotentne,
- nevyžaduje komplexný manuálny postup pod tlakom.

Kill switch nemusí automaticky obnoviť zdravý stav. Po jeho aktivácii stále treba pozorovať recovery a prípadne vykonať ďalší zásah.

## 14. Abort criteria

Abort criteria chránia používateľov, dáta a error budget. Majú byť merateľné a vyhodnocované počas experimentu.

Príklady:

- error rate prekročí 2 % počas 60 sekúnd,
- p99 latency prekročí 2 sekundy v dvoch po sebe idúcich oknách,
- vznikne prvá duplicitná finančná transakcia,
- authorization invariant je porušený,
- backlog prekročí 100 000 správ,
- SLO burn rate prekročí definovanú hranicu,
- observability alebo experiment correlation sa stratí,
- fault zasiahne target mimo allowlistu,
- recovery capacity klesne pod bezpečný limit,
- on-call alebo incident commander vydá manuálny abort.

„Zastavíme, keď to bude vyzerať zle“ nie je operovateľný kontrakt.

## 15. Observation points

Fault aj jeho dopad treba pozorovať z viacerých vrstiev. Interná metrika zasiahnutého komponentu môže zmiznúť práve vtedy, keď ju najviac potrebujeme.

Observation points:

- **User-facing probe —** syntetický journey alebo externý API check.
- **Control plane —** scheduler, load balancer, autoscaler alebo orchestration stav.
- **Application telemetry —** metrics, logs, traces a domain events.
- **Dependency telemetry —** latency, errors, quotas a queue depth downstreamu.
- **Infrastructure telemetry —** CPU, memory, network, disk a kernel signals.
- **Data integrity probe —** duplicates, missing records, reconciliation a constraints.
- **Experiment telemetry —** target, fault intensity, start/stop a correlation ID.

Externý observation point je kritický pri resource exhaustion alebo network faultoch, ktoré môžu poškodiť lokálnu telemetry.

## 16. Experiment ladder

Resilience dôkaz sa buduje postupne:

```text
architecture review a model
→ tabletop
→ unit/component failure injection
→ integration alebo staging
→ internal cohort alebo shadow
→ malý produkčný scope
→ širší pravidelný experiment
```

Každý krok má testovať relevantnejšiu vlastnosť. Nemá zmysel slepo opakovať identický fault v každom prostredí, ak topology a failure semantics sú odlišné.

Nižšie vrstvy majú odstrániť základné chyby. Produkčný experiment má overiť zostávajúce predpoklady, ktoré závisia od reálneho trafficu, topológie, identity alebo prevádzkových procesov.

## 17. Tabletop exercise

Tabletop je simulované cvičenie bez technického fault injection. Testuje ľudský a procesný control plane.

Scenár môže zahŕňať:

- region je nedostupný,
- alert prichádza on-call tímu,
- tím identifikuje blast radius,
- používa runbook a rozhoduje o failoveri,
- komunikuje stakeholderom,
- overuje dátové riziko,
- plánuje návrat do primary režimu.

Tabletop odhaľuje:

- chýbajúce alebo zastarané kontakty,
- nejasné ownership a rozhodovacie práva,
- chýbajúce prístupy alebo break-glass proces,
- nefunkčné runbooky,
- konflikt technickej a business priority,
- nejasné RPO/RTO očakávania,
- nedostatočný communication plan.

Cieľom nie je hodnotiť jednotlivca. Cieľom je zlepšiť systém, v ktorom ľudia reagujú.

## 18. Process a instance failure

Ukončenie procesu alebo instance overuje viac než restart policy.

Pozoruj celý lifecycle:

```text
failure vznikne
→ health detection
→ traffic removal
→ in-flight request behavior
→ restart/reschedule
→ capacity replacement
→ readiness
→ traffic re-entry
→ state a backlog recovery
```

Kontroluj:

- connection draining a client retry,
- idempotency nejasne dokončených writes,
- leader election alebo lease expiration,
- session affinity,
- alert timing a severity,
- retry amplification,
- chýbajúcu kapacitu počas warm-upu,
- orphaned locks alebo resources.

## 19. Network faults

Sieťové zlyhanie nie je iba úplný partition. Realistické faults:

- latency a jitter,
- packet loss,
- bandwidth limit,
- connection reset,
- DNS timeout alebo stale answer,
- asymmetric reachability,
- iba egress alebo ingress failure,
- MTU/fragmentation problém,
- partial regional partition.

Overuj:

- connect, read a total timeouty,
- retry budget a jitter,
- circuit breaker a bulkhead,
- queueing a pool saturation,
- fallback alebo cached response,
- idempotency a duplicate side effects,
- telemetry koreláciu,
- recovery po obnove route.

Fault musí byť vložený na správnej vrstve. Service mesh, proxy, container namespace alebo cloud firewall môže zmeniť, ktorý packet flow je skutočne zasiahnutý.

## 20. Dependency degradation

Externá dependency môže byť dostupná, ale nezdravá. Testuj aj:

- pomalé responses,
- partial alebo segment-specific errors,
- malformed či schema-valid, ale nesprávne dáta,
- rate limiting a quota exhaustion,
- stale response,
- intermittent timeout,
- auth alebo certificate failure,
- connection pool exhaustion,
- nesprávne retry-after semantics.

Systém musí rozlíšiť retryable a non-retryable failure. Neobmedzené retries môžu násobiť load a spôsobiť cascading failure.

## 21. Resource pressure

Resource experiments testujú bounded behavior pri nedostatku kapacity:

- CPU saturation alebo throttling,
- memory pressure a OOM,
- disk alebo inode exhaustion,
- file-descriptor exhaustion,
- thread alebo worker pool saturation,
- database connection pool saturation,
- queue depth a storage pressure,
- API quota exhaustion.

Overuj:

- admission control a backpressure,
- bounded queues,
- priority traffic,
- load shedding,
- graceful degradation,
- autoscaling alebo vertical limits,
- alerting pred úplným kolapsom,
- recovery po odstránení pressure,
- data integrity pri interrupted writes.

## 22. Messaging a data faults

Stateful a event-driven systems potrebujú zvlášť opatrný fault model.

Scenáre:

- duplicitný event,
- out-of-order delivery,
- oneskorenie alebo replay,
- poison message,
- consumer restart po side effecte, ale pred checkpointom,
- partial transaction,
- schema mismatch,
- replication lag,
- stale read,
- split-brain alebo leader ambiguity.

Overuj:

- idempotency a deduplication,
- ordering assumptions,
- transactional outbox/inbox behavior,
- checkpointing a replay,
- dead-letter handling,
- reconciliation,
- uniqueness a integrity constraints,
- bezpečný operator recovery.

Fault injection nesmie nevratne poškodiť produkčné dáta. Pri rizikových data experiments používaj izolovaný tenant, synthetic records, read-only variant alebo overený restore/compensation postup.

## 23. Data-integrity boundary

Pred experimentom explicitne klasifikuj, čo sa môže zmeniť:

- žiadne writes,
- iba syntetické alebo označené records,
- idempotentné a kompenzovateľné writes,
- produkčné writes s overenými constraints a recovery,
- zakázané nevratné operácie.

Definuj data oracle:

- počet vytvorených side effects,
- uniqueness,
- reconciliation totals,
- checksum alebo integrity query,
- audit log completeness,
- RPO hranicu,
- business invariant.

Technický recovery bez dátovej verification nie je úspešný experiment.

## 24. Recovery je samostatná fáza

Dôležitá otázka nie je iba „prežil systém fault?“, ale aj „vrátil sa úplne do zdravého stavu?“

Po odstránení faultu sleduj:

- backlog drain a jeho rýchlosť,
- cache warming,
- replica synchronization a lag,
- leader election stability,
- stuck locks a leases,
- orphaned resources,
- connection-pool normalizáciu,
- autoscaling scale-down,
- data reconciliation,
- error-rate a latency návrat,
- alert closure,
- user-facing journey.

Systém môže počas faultu graceful degradovať, ale po obnove zostať v skrytom degraded mode. Recovery observation musí mať vlastný timeout a success criteria.

## 25. Disaster recovery experiments

DR experimenty overujú, či sa služba a jej dáta dajú obnoviť po veľkom failure domaine.

Kontroluj:

- backup dostupnosť, integrity a encryption keys,
- restore do izolovaného prostredia,
- RPO a skutočne stratené dáta,
- RTO od rozhodnutia po použiteľný business outcome,
- schema a application compatibility,
- DNS/routing cutover,
- secrets, certificates a identity dependencies,
- external integrations,
- data reconciliation,
- failback alebo návrat do primary režimu,
- runbook a rozhodovacie ownership.

Úspešný backup job nie je recovery dôkaz. DR experiment musí overiť, že používateľ alebo business workflow po obnove funguje.

## 26. Game day

Game day je plánované tímové cvičenie spájajúce faults, observability, incident response, communication a recovery.

Dobrý game day:

- má jasný experiment contract,
- používa realistický, ale bezpečný scenár,
- nie je skúškou alebo pascou pre jednotlivca,
- zachytáva presnú timeline,
- testuje technické aj organizačné dependencies,
- má facilitátora a safety ownera,
- končí konkrétnymi actions, ownermi a termínmi,
- opakuje kritický experiment po remediation.

Psychologická bezpečnosť je súčasť resilience. Ak ľudia skrývajú nejasnosť alebo sa boja použiť kill switch, proces nie je odolný.

## 27. Automatizované chaos experimenty

Opakovateľný a nízkorizikový experiment možno automatizovať v CI/CD alebo scheduled production workflow. Automatizácia je vhodná iba vtedy, keď je experiment dostatočne stabilný a jeho safety mechanizmy sú spoľahlivé.

Eligibility criteria:

- hypotéza a target sú stabilné,
- fault injection je deterministicky ohraničený,
- blast radius je malý,
- prechecks a abort rules sú automatizované,
- kill switch je nezávislý a otestovaný,
- cleanup je idempotentný a overiteľný,
- telemetry je úplná a korelovaná,
- experiment má nízky false-abort a invalid rate,
- owner reaguje na failure a remediation debt.

Automatizácia neznižuje zodpovednosť. Zvyšuje frekvenciu zásahov, a teda potrebu guardrails, rate limits a audit trailu.

## 28. Chaos testing v CI/CD

Nie všetky chaos experimenty patria do pull-request pipeline. Umiestnenie závisí od fidelity, ceny a rizika.

Príklad vrstvenia:

```text
unit/component
→ injected timeout, duplicate event, fake clock

integration
→ process kill, dependency degradation, broker restart

pre-release
→ failover, load shedding, recovery v sandboxe

production scheduled/progressive
→ malý fault domain s reálnym trafficom a guardrails
```

Rýchle deterministic failure-injection testy patria čo najskôr. Veľké regionálne alebo DR experimenty potrebujú samostatný riadený workflow.

## 29. SLO a error budget

SLO poskytuje používateľsky orientovanú hranicu steady state. Chaos experiment môže overiť:

- či fault neprekročí SLO,
- ako rýchlo sa spotrebúva error budget,
- či alert reaguje pred neprijateľným dopadom,
- či graceful degradation chráni kritický journey,
- či recovery obnoví SLI v požadovanom čase.

Pred produkčným experimentom zohľadni aktuálny error-budget stav. Pri rýchlom burne alebo existujúcom incidente môže byť správne experiment odložiť alebo zmenšiť scope.

## 30. Evidence a experiment provenance

Výsledok experimentu musí byť reprodukovateľný a auditovateľný. Uchovaj:

- experiment definition a version,
- artifact a configuration identity,
- target preview a skutočne zasiahnuté resources,
- start/stop timestamps,
- fault intensity a state transitions,
- baseline a steady-state metrics,
- logs, traces a dashboards,
- abort/kill-switch udalosti,
- recovery timeline,
- data-integrity results,
- observer notes a incident communication,
- výslednú klasifikáciu,
- remediation actions a repeat result.

Bez provenance nemožno porovnať experiment po zmene systému ani dokázať, čo bolo reálne testované.

## 31. Learning a remediation closure

Výsledkom chaos experimentu nemá byť iba report. Každý finding musí viesť k trvalej zmene alebo explicitnému risk rozhodnutiu.

Možné actions:

- oprava timeout/retry alebo idempotency mechanizmu,
- bounded queue alebo load shedding,
- nový alert alebo SLI,
- zlepšenie telemetry,
- aktualizácia runbooku,
- nový regression alebo component failure test,
- platformový guardrail,
- zmena autoscaling alebo capacity baseline,
- doplnenie backup/restore procesu,
- ownership alebo communication zmena,
- opakovanie experimentu po remediation.

Remediation lifecycle:

```text
finding
→ owner a priority
→ implementácia
→ skorší regression/control
→ repeat chaos experiment
→ potvrdenie zlepšenia
```

Potvrdená hypotéza tiež potrebuje ďalšiu prácu: experiment sa má versionovať a podľa rizika periodicky opakovať, pretože systém a jeho dependencies sa menia.

## 32. Metriky programu

Počet spôsobených failures nie je cieľ. Sleduj kvalitu evidence a uzatváranie rizík:

- coverage kritických failure domains a recovery paths,
- podiel potvrdených, vyvrátených, inconclusive a invalid experimentov,
- experiment abort rate a dôvody,
- neplánované rozšírenie blast radiusu,
- detection time a recovery time,
- SLI a error-budget dopad,
- počet a vek remediation actions,
- repeat-experiment success rate,
- percento findings prevedených na skorší regression test alebo guardrail,
- kill-switch a cleanup reliability,
- data-integrity incidents spôsobené experimentom,
- čas od experimentu po uzavretie learning loopu.

Vysoký počet invalid experimentov signalizuje problém v targetingu, baseline, telemetry alebo orchestration platforme.

## 33. Diagnostický postup pri neočakávanom výsledku

1. **Aktivuj safety policy —** abort, kill switch alebo zníženie expozície podľa guardrailu.
2. **Over fault state —** bol fault reálne aplikovaný, na správny target a s plánovanou intenzitou?
3. **Over baseline —** bol systém pred experimentom zdravý?
4. **Over observation —** sú metrics, logs, traces a user probe úplné?
5. **Urči blast radius —** zasiahol fault iba povolený scope alebo sa amplifikoval?
6. **Rozlíš mechanizmus —** health detection, retry, queueing, data integrity, capacity alebo recovery.
7. **Odstráň fault —** použi idempotentný control path.
8. **Sleduj recovery —** neukonči incident pri prvom zelenom health checku.
9. **Over dáta —** duplicates, missing records, reconciliation a RPO.
10. **Klasifikuj experiment —** vyvrátený, inconclusive, invalid alebo aborted.
11. **Uchovaj evidence —** vrátane orchestration a kill-switch udalostí.
12. **Uzavri remediation —** owner, skorší test a repeat experiment.

## 34. Typické anti-patterny

### Chaos bez hypotézy

Fault vytvorí šum alebo incident, ale neposkytne jasný poznatok ani rozhodnutie.

### Náhodné vypínanie produkcie

Bez target scope, steady state a safety controls nejde o experiment, ale o neplánovaný risk.

### Experiment iba podľa infra metrík

CPU alebo počet podov môže zostať zdravý, hoci používateľský workflow zlyháva alebo vznikajú duplicity.

### Test iba v stagingu ako dôkaz produkcie

Staging je užitočný krok, ale nemusí reprezentovať produkčný traffic, topology, identities a quotas.

### Kill switch v rovnakom fault domaine

Experiment môže stratiť schopnosť sám seba zastaviť.

### Abort bez recovery observation

Fault je odstránený, ale backlog, locks alebo replikácia zostanú degradované.

### Chaos na produkčných dátach bez integrity oracle

Systém môže vyzerať dostupne, no experiment poškodí alebo duplikuje dáta.

### Game day ako skúška ľudí

Vedie k skrývaniu problémov a znižuje psychologickú bezpečnosť.

### Chaos framework ako cieľ

Nainštalovaný tool alebo počet faultov nie je dôkaz resilience.

### Potvrdená hypotéza bez opakovania

Systém sa mení a pôvodný dôkaz starne. Kritické experimenty potrebujú periodický repeat alebo automatizáciu.

### Remediation backlog bez ownera

Experiment generuje reporty, ale riziká zostávajú otvorené a program neprináša zlepšenie.

## 35. Praktický rozhodovací rámec

Pred experimentom odpovedz:

1. Akú konkrétnu resilience vlastnosť a failure mode overujeme?
2. Aký používateľsky významný steady state má zostať zachovaný?
3. Aký mechanizmus má podľa hypotézy fungovať?
4. Je systém v zdravom baseline stave?
5. Aký fault najpresnejšie reprezentuje riziko?
6. Aký je target a ako overíme jeho identitu?
7. Aký je najmenší relevantný blast radius?
8. Ktoré downstream amplifikácie sú možné?
9. Aké sú automatické a manuálne abort criteria?
10. Je kill switch dostupný mimo fault domainu?
11. Aké externé observation points použijeme?
12. Aký je data-integrity risk a oracle?
13. Ako sa fault odstráni a cleanup overí?
14. Ako dlho budeme sledovať recovery?
15. Kto experiment vlastní, pozoruje a má rozhodovaciu právomoc?
16. Aký výsledok bude confirmed, disproved, inconclusive alebo invalid?
17. Ako sa finding premení na skorší test, guardrail a repeat experiment?

## 36. Kontrolný checklist

Pred spustením over:

- hypotéza je konkrétna a vyvrátiteľná,
- steady state je používateľsky relevantný,
- baseline je zdravý,
- artifact, config a topology sú identifikované,
- target preview zodpovedá allowlistu,
- fault intensity a duration sú ohraničené,
- blast radius zahŕňa downstream amplification,
- abort criteria sú automatizovateľné,
- kill switch je otestovaný a nezávislý,
- observability funguje aj mimo targetu,
- experiment má correlation ID,
- data writes a integrity oracle sú explicitné,
- cleanup je idempotentný,
- recovery má vlastné success criteria,
- on-call a stakeholders poznajú experiment,
- evidence retention je definovaná,
- remediation workflow má ownera a repeat podmienku.

## 37. Kontrolné otázky

1. Aký je rozdiel medzi chaos testingom a náhodným rozbíjaním?
2. Prečo steady state nemá byť iba „proces beží“?
3. Ako vyzerá vyvrátiteľná experiment hypothesis?
4. Čo musí obsahovať experiment contract?
5. Aký je rozdiel medzi vyvráteným, inconclusive a invalid experimentom?
6. Prečo treba baseline prechecks?
7. Čo tvorí realistický fault model?
8. Ako sa overuje target identity a scope?
9. Prečo blast radius zahŕňa aj retry alebo downstream amplification?
10. Aké stavy má safety state machine?
11. Prečo má byť kill switch mimo fault domainu?
12. Aké observation points sú potrebné pri resource alebo network faultoch?
13. Čo experiment ladder zvyšuje v každej fáze?
14. Ako sa testuje data integrity pri messaging faults?
15. Prečo recovery potrebuje samostatnú observation fázu?
16. Čo musí dokazovať disaster-recovery experiment?
17. Kedy je experiment vhodný na automatizáciu?
18. Ako SLO a error budget ovplyvňujú chaos experiment?
19. Aké evidence musí zostať po experimente?
20. Ako sa finding uzavrie opakovaným experimentom?

## Summary

Chaos testing je riadený spôsob overovania resilience pomocou konkrétnej hypotézy, merateľného steady state a kontrolovaného faultu. Dôveryhodný experiment potrebuje zdravý baseline, presný target, realistický fault model, obmedzený blast radius, nezávislý kill switch, viac observation points, data-integrity oracle a samostatnú recovery fázu. Výsledok nemusí byť iba pass alebo fail; môže byť vyvrátený, inconclusive, invalid alebo bezpečnostne aborted. Hodnota vzniká až vtedy, keď evidence vedie k remediation, skoršiemu regression testu alebo platformovému guardrailu a experiment sa po zmene zopakuje.

## Glossary impact

Relevantné pojmy: chaos testing, chaos engineering, resilience engineering, steady state, experiment hypothesis, experiment contract, experiment validity, fault model, target identity, blast radius, safety state machine, abort criterion, kill switch, observation point, fault injection, game day, tabletop exercise, graceful degradation, load shedding, recovery observation, RPO a RTO.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shift-right](shift-right.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Continuous Integration →](../05-ci-cd-and-release/continuous-integration.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
