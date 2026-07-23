# Scalability, elasticity a fault tolerance

Scalability, elasticity a fault tolerance opisujú tri odlišné vlastnosti systému. Všetky súvisia s kapacitou a odolnosťou, ale každá rieši inú otázku a vyžaduje iné mechanizmy, testy a prevádzkové dôkazy.

```text
Scalability      → dokáže systém obslúžiť väčší workload bez neprimeraného zhoršenia?
Elasticity       → dokáže systém meniť kapacitu podľa aktuálneho alebo očakávaného demandu?
Fault tolerance  → dokáže systém pokračovať pri zlyhaní komponentu alebo failure domainu?
```

Systém môže byť škálovateľný, ale neelastický, ak zvládne vyššiu záťaž iba po manuálnom rozšírení. Rovnako môže byť elastický, ale nie fault-tolerant, ak automaticky pridáva instances v jednej Availability Zone a výpadok tejto zóny vyradí celý workload.

## 1. Mentálny model

Najpresnejší model začína pracovnou jednotkou, obmedzenými resources a failure domains. Workload vytvára demand, jednotlivé vrstvy ho spracúvajú a každá vrstva má kapacitnú hranicu, provisioning latency a vlastný spôsob zlyhania.

```text
workload a arrival rate
→ load balancing alebo partitioning
→ compute workers
→ connection a thread pools
→ cache, queue alebo databáza
→ storage a network
→ výsledok pre používateľa
```

Scalability skúma, ako sa mení maximálny bezpečný throughput tohto toku. Elasticity riadi, kedy a ako sa kapacita pridá alebo odoberie, zatiaľ čo fault tolerance určuje, čo sa stane, keď časť toku prestane fungovať.

## 2. Scalability

Scalability je schopnosť systému zväčšiť alebo zmenšiť spracovateľskú kapacitu bez neprimeraného zhoršenia latency, reliability, operability alebo jednotkových nákladov. Nejde iba o počet serverov; škálovať musí celý kritický path vrátane databázy, storage, network, control plane-u a ľudského operating modelu.

Systém môže zvládnuť desaťnásobný počet webových requestov a stále zlyhať na jednom serializovanom locku alebo malej database connection pool. Pri hodnotení scalability preto hľadaj prvú vrstvu, ktorej kapacita nerastie spolu s demand-om.

## 3. Kapacitný model a bottleneck

Kapacita systému je obmedzená jeho najslabším relevantným článkom. Ak všetky application instances zapisujú do jednej databázy s maximom 5 000 transakcií za sekundu, pridávanie ďalších webových instances po dosiahnutí tohto limitu iba zvýši počet čakajúcich requestov.

Praktický kapacitný model má spájať demand unit s konkrétnymi resources. Pre checkout službu môže jedna objednávka znamenať dva database writes, jedno payment API volanie, niekoľko cache operations a určitý počet prenesených bytes; až z tohto vzťahu možno odhadovať, ktorá vrstva sa stane bottleneckom.

## 4. Vertical scaling

Vertical scaling zväčšuje alebo zmenšuje kapacitu jedného resource-u, napríklad pridaním CPU a memory k virtuálnemu stroju alebo prechodom databázy na väčšiu instance class. Mechanizmus nemení počet aktívnych uzlov, ale poskytne jednému uzlu viac výkonu, cache, I/O alebo concurrency.

Výhodou je jednoduchší application a consistency model, pretože stav nemusí byť rozdelený medzi ďalšie uzly. Limity tvoria maximálna dostupná veľkosť, skokové ceny, možný restart pri zmene a rastúci blast radius jedného veľkého resource-u.

Vertical scaling sa hodí najmä tam, kde by distribúcia stavu alebo práce priniesla väčšiu zložitosť než samotné zväčšenie uzla:

- **Legacy aplikácia** — monolit alebo vendor software nemusí podporovať bezpečné rozdelenie na viac aktívnych instances, preto je väčší host najjednoduchší spôsob získania kapacity.
- **Relačná databáza pred scale-up limitom** — väčšia instance môže zvýšiť buffer cache, CPU a I/O bez zavedenia shardingu, kým workload ešte neprekročil praktickú hranicu jedného writer-a.
- **Dočasné odstránenie bottlenecku počas migrácie** — scale-up môže vytvoriť časový priestor na redesign, ale nesmie sa prezentovať ako trvalé riešenie bez maximálnej veľkosti a rollback plánu.
- **Workload s drahou distributed coordination** — ak consensus, rebalancing alebo cross-node communication stoja viac než väčší uzol, vertical scaling môže mať lepší pomer výkonu, ceny a operability.

Vertical scaling je legitímny návrh, nie zlyhanie cloud-native architektúry. Nesmie sa však zamieňať s neobmedzenou škálovateľnosťou alebo vysokou dostupnosťou.

## 5. Horizontal scaling

Horizontal scaling pridáva alebo odoberá samostatné instances, workers, shards alebo partitions. Traffic alebo pracovné jednotky sa musia medzi tieto jednotky distribuovať pomocou load balancera, queue, partition keyu alebo iného routing mechanizmu.

Aby horizontal scaling priniesol reálnu kapacitu, jednotlivé replicas nesmú byť blokované spoločným serializovaným stavom. Aplikácia preto často externalizuje sessions, používa idempotentné operations a navrhne databázový alebo queue model, ktorý podporuje paralelné spracovanie.

Horizontal scaling potrebuje viac než iba možnosť vytvoriť ďalšiu repliku:

- **Stabilné rozdelenie trafficu alebo práce** — load balancer, queue alebo partition function musí prideľovať nové operations zdravým workers bez hot spots a bez straty ordering contractu.
- **Health checks a odstránenie nezdravých replicas** — routing vrstva musí prestať posielať traffic targetu, ktorý síce beží, ale nedokáže bezpečne obslúžiť požadovaný outcome.
- **Stateless processing alebo explicitný state ownership** — lokálny stav nesmie rozhodovať o výsledku requestu bez mechanizmu, ktorý ho replikuje, presúva alebo smeruje request k správnemu ownerovi.
- **Koordinácia, partitioning a consistency model** — systém musí vysvetliť, kto smie zapisovať, ako sa riešia concurrent updates a čo používateľ uvidí počas rebalancingu alebo výpadku.
- **Graceful scale-in a odovzdanie práce** — odoberaná replika musí dokončiť, checkpointnúť alebo bezpečne vrátiť rozpracovanú operáciu, aby nevznikla strata alebo duplicita.
- **Observability per replica aj za celý service** — lokálne hot spots musia byť viditeľné, ale zároveň treba merať end-to-end throughput, latency a errors za celý logical service.

Viac replicas automaticky neznamená lineárne viac throughputu. Shared lock, jedna queue partition, database write leader alebo externá API quota môžu rast zastaviť dávno pred vyčerpaním compute vrstvy.

## 6. Diagonal scaling

Diagonal scaling kombinuje vertical a horizontal scaling. Systém najprv používa efektívnu veľkosť jedného uzla a po dosiahnutí praktického bodu pridáva ďalšie uzly rovnakej alebo podobnej veľkosti.

Tento model býva ekonomicky vhodný, pretože príliš malé instances vytvárajú vysoký orchestration overhead a príliš veľké instances zvyšujú blast radius a cenu nevyužitej kapacity. Nevýhodou je zložitejší autoscaling, keď sa súčasne mení počet aj veľkosť resources a každý prechod môže mať inú provisioning latency.

## 7. Scalability nie je performance

Performance opisuje, ako rýchlo alebo efektívne systém funguje pri konkrétnom workload-e. Scalability opisuje, ako sa toto správanie mení pri raste workloadu alebo kapacity.

Aplikácia môže mať výbornú latency pri 100 requestoch za sekundu, ale po zdvojnásobení trafficu skolabovať pre lock contention. Naopak škálovateľná aplikácia môže mať vyššiu základnú latency, ale udržať podobné správanie pri desaťnásobnom raste pridaním kapacity.

## 8. Elasticity

Elasticity je schopnosť meniť pridelenú kapacitu podľa demandu a následne ju bezpečne znížiť, keď už nie je potrebná. Oproti scalability pridáva automatizovaný control loop: systém meria signal, porovná ho s policy a vykoná scaling action.

```text
demand signal
→ aggregation a evaluation window
→ scaling policy
→ provisioning alebo termination
→ readiness a traffic shift
→ nový observed state
```

Elasticita nie je okamžitá. Provisioning VM, spustenie Podu, inicializácia runtime-u, warming cache a registrácia do load balancera môžu trvať sekundy až minúty, počas ktorých musí existujúca kapacita absorbovať špičku.

## 9. Scaling signal

Scaling signal musí korelovať s resource-om, ktorý je potrebné rozšíriť. CPU je vhodný pre CPU-bound workload, ale môže byť zavádzajúci pre service čakajúcu na I/O, connection pool alebo externé API.

Jednotlivé workloady preto potrebujú signál viazaný na svoju skutočnú pracovnú jednotku a bottleneck:

- **HTTP service — request concurrency, requests per target alebo queueing latency** ukazujú, či requests čakajú na dostupný worker a či pridaná replika môže reálne zvýšiť serving capacity.
- **Queue consumer — oldest-message age, backlog depth a processing rate** spoločne odlišujú krátky burst od trvalého nedostatku kapacity alebo zaseknutého consumera.
- **Stream consumer — consumer lag a partition ownership** ukazujú, koľko dát zostáva nespracovaných a či je vôbec možné pridať ďalší parallel consumer pri danom počte partitions.
- **Database proxy — active connections, waiters a acquire latency** odhaľujú saturation connection poolu, ktorú samotné CPU databázy nemusí zachytiť.
- **Batch workers — remaining work voči deadline-u** prepája objem zostávajúcej práce s časom, ktorý zostáva do business termínu.
- **Inference service — queued requests, accelerator utilization a batch latency** ukazujú, či je bottleneck v GPU kapacite, batching policy alebo čakaní pred samotnou inferenciou.

Signal musí mať známy measurement point, bounded dimensions a definované no-data správanie. Ak telemetry pipeline zlyhá, autoscaler nesmie nekontrolovane zmenšiť kritickú službu iba preto, že metric zmizla.

## 10. Target tracking, step a scheduled scaling

Target tracking sa snaží udržiavať metric približne okolo cieľovej hodnoty, napríklad priemerne 60 % CPU alebo 100 requestov na target. Control loop priebežne odhaduje potrebnú kapacitu a je vhodný pre plynule sa meniaci demand.

Step scaling používa explicitné pásma, napríklad pridať dve instances pri queue depth nad 1 000 a ďalších päť nad 5 000. Scheduled scaling nastaví kapacitu pred známou udalosťou, napríklad pred pracovným dňom alebo pravidelným mesačným spracovaním.

Tieto modely sa môžu kombinovať. Scheduled baseline pripraví kapacitu pred predvídateľnou špičkou a target tracking následne reaguje na odchýlky, ktoré forecast nezachytil.

## 11. Reactive a predictive scaling

Reactive scaling reaguje na už pozorovaný stav. Je jednoduchšie overiteľný, ale prirodzene zaostáva za náhlym demand-om, pretože signal sa musí nazbierať, vyhodnotiť a nová kapacita musí dosiahnuť readiness.

Predictive scaling používa historické patterns alebo forecast na prípravu kapacity vopred. Znižuje riziko cold startu pri opakovaných špičkách, ale môže sa pomýliť pri promo kampani, incidente alebo zmene používateľského správania.

Kritické služby preto často kombinujú minimálnu rezervu, scheduled alebo predictive prípravu a reactive korekciu. Forecast nie je náhrada hard limits, quota monitoring-u a load testov.

## 12. Scale-out lifecycle

Scale-out nie je dokončený vytvorením novej instance. Nový resource musí prejsť bootstrapom, načítať konfiguráciu a secrets, inicializovať dependencies, prejsť readiness checkom a až potom prijať traffic.

```text
policy trigger
→ resource provisioning
→ bootstrap a configuration
→ application start
→ cache alebo connection warm-up
→ readiness
→ load-balancer registration
→ stabilný traffic share
```

Ak autoscaler počíta novú kapacitu ako dostupnú príliš skoro, môže zastaviť ďalší scale-out, hoci nové instances ešte neobsluhujú requesty. Sleduj preto rozdiel medzi desired, provisioned, ready a serving capacity.

## 13. Scale-in lifecycle

Scale-in je rizikovejší než scale-out, pretože odoberá aktívnu kapacitu a môže prerušiť rozpracovanú prácu. Systém musí prestať prideľovať nové operations, dokončiť alebo bezpečne odovzdať existujúce operations a až potom resource ukončiť.

Bezpečný lifecycle typicky zahŕňa connection draining, shutdown grace period, work handoff, checkpoint alebo idempotent retry. Pre batch a queue workers môže byť potrebná scale-in protection, aby autoscaler neukončil dlhý kritický job tesne pred dokončením.

## 14. Cooldown a stabilization

Cooldown alebo stabilization window bráni tomu, aby control loop reagoval na každý krátky výkyv. Po scaling action potrebuje systém čas, aby sa zmena prejavila v metrics a bolo možné posúdiť nový stav.

Príliš krátke okno vedie k oscilácii: systém pridá kapacitu, metric klesne, kapacitu odoberie a o chvíľu ju opäť pridáva. Príliš dlhé okno zase oneskorí potrebnú reakciu na skutočný rast demandu.

## 15. Stateless a stateful scaling

Stateless replica neuchováva lokálny authoritative state potrebný na ďalší request. Ľubovoľný zdravý worker preto môže spracovať ďalšiu operáciu a horizontal scaling je relatívne priamočiary.

Stateful tier musí rozhodnúť, kde je authoritative state, ako sa replikuje a kto smie zapisovať. Scaling môže vyžadovať rebalancing partitions, presun leaderov, obnovu replicas a riadenie consistency počas prechodu.

Stateful scaling musí explicitne riešiť tieto navzájom prepojené problémy:

- **Partition alebo shard ownership** — určuje, ktorý uzol zodpovedá za konkrétnu časť keyspace-u a kam sa má request smerovať počas normálnej prevádzky aj presunu.
- **Leader/follower alebo multi-writer model** — definuje, kto smie prijímať writes a ako sa zabráni divergentným hodnotám alebo split brainu.
- **Replication lag** — vyjadruje, ako ďaleko môže replica zaostávať a aké stale reads alebo data loss vzniknú pri failover-e.
- **Conflict resolution** — určuje, ako sa zlúčia concurrent updates, ak systém povoľuje viac writerov alebo dočasne oddelené partitions.
- **Storage throughput a locality** — limitujú, ako rýchlo možno state čítať, zapisovať a presúvať bez preťaženia networku alebo diskov.
- **Failover a recovery** — popisujú voľbu nového ownera, obnovu chýbajúcich replicas a validáciu consistency pred návratom plného trafficu.
- **Rebalancing cost** — zachytáva data movement, cache misses a dočasnú duplicitu práce, ktoré môžu počas scale-outu zhoršiť latency skôr, než sa kapacita zvýši.

Práve stateful vrstva býva dominantnou hranicou scalability aj fault tolerance celého systému.

## 16. Queue-based load leveling

Queue oddeľuje okamžitý producer rate od consumer capacity. Producer môže uložiť prácu rýchlejšie, než ju workers spracujú, a workers následne backlog postupne vyrovnávajú.

```text
producer → durable queue → consumers → downstream system
```

Queue absorbuje burst, ale nevytvára novú kapacitu. Ak priemerný arrival rate dlhodobo prevyšuje processing rate, backlog a message age budú rásť až po prekročenie storage alebo business deadline-u.

Použiteľný model potrebuje visibility timeout alebo acknowledgement semantics, retry policy, dead-letter handling, idempotent consumer a SLO pre najstaršiu správu. Queue depth bez age a processing rate môže skryť, že malý backlog obsahuje veľmi starú kritickú prácu.

## 17. Backpressure

Backpressure je mechanizmus, ktorým preťažený downstream signalizuje upstreamu, že nemôže prijímať ďalšiu prácu plnou rýchlosťou. Cieľom je udržať preťaženie v kontrolovanej boundary namiesto nekonečného rastu memory, queues a connection pools.

Systém môže spomaliť producenta, odmietnuť low-priority requesty, použiť bounded buffer alebo degradovať menej dôležitú funkcionalitu. Bez explicitného backpressure modelu sa overload presúva medzi vrstvami a často končí kaskádovým zlyhaním.

## 18. Load balancing

Load balancer distribuuje traffic medzi targets, ktoré považuje za zdravé. Rozhodnutie môže používať round-robin, least-connections, hash, locality alebo ďalší algoritmus podľa typu load balancera a protokolu.

Health check je iba aproximácia schopnosti targetu obslúžiť reálny user journey. Target môže odpovedať na jednoduchý `/health`, ale súčasne zlyhávať na databáze alebo mať vyčerpaný thread pool.

Návrh musí riešiť connection reuse, sticky sessions, cross-zone distribution, draining, TLS termination a fail-open alebo fail-closed správanie. Load balancer neodstráni bottleneck v spoločnej databáze ani neopravenú hot partition.

## 19. Fault tolerance

Fault tolerance je schopnosť systému pokračovať v poskytovaní definovanej funkcie pri zlyhaní komponentu alebo failure domainu. Neznamená, že používateľ nikdy neuvidí žiadnu chybu; znamená, že architektúra zlyhanie očakáva, obmedzí jeho blast radius a obnoví službu v rámci contractu.

Mechanizmy zahŕňajú redundanciu, replication, quorum, automatic failover, retries, isolation a graceful degradation. Každý mechanizmus má vlastné consistency, latency, cost a operational trade-offy a musí sa testovať počas reálneho failure scenára.

## 20. Redundancy a nezávislé failure domains

Redundancy pomáha iba vtedy, keď redundantné kópie nezdieľajú rovnaký kritický failure mode. Dve instances v jednej Availability Zone alebo dve network links cez ten istý router nemusia poskytovať očakávanú odolnosť.

Nezávislosť treba posudzovať cez power, network, software version, configuration, identity, account, Region a administratívny access. Viac kópií s rovnakou chybnou konfiguráciou môže iba rýchlejšie rozšíriť logical corruption.

Nasledujúce návrhy vyzerajú redundantne iba počtom komponentov, ale zdieľajú rozhodujúcu príčinu zlyhania:

- **Primary a replica na rovnakom hoste alebo v jednej zóne** — strata hosta alebo zóny odstráni obe kópie a z redundancy nezostane použiteľná capacity.
- **Backup v rovnakom account-e s rovnakým delete oprávnením** — compromised administrator alebo chybná automation môže zmazať production state aj recovery copy jednou identity cestou.
- **Dve DNS cesty závislé od jednej authoritative zóny** — odlišné resolvery alebo endpoints nepomôžu, ak spoločný authoritative source publikuje chybnú alebo nedostupnú odpoveď.
- **Všetky replicas deployované rovnakou chybnou pipeline naraz** — software alebo configuration failure sa rozšíri do všetkých kópií skôr, než health model dokáže zachovať zdravú verziu.
- **Multi-Region aplikácia s jedným globálnym identity alebo data bottleneckom** — regionálny compute prežije lokálny výpadok, ale spoločná závislosť stále vyradí celý user journey.

## 21. Active-active a active-passive

Active-active model používa viac aktívnych komponentov, ktoré súčasne spracúvajú traffic. Redundantná kapacita je využitá aj počas normálnej prevádzky, ale systém musí riešiť concurrent writes, routing, consistency a prípadný split brain.

Active-passive model drží jeden primárny component a standby, ktorý preberie funkciu po failover-e. Zjednodušuje write ownership, ale vytvára failover latency, riziko driftu standby prostredia a potrebu pravidelne dokazovať, že pasívna kapacita je stále použiteľná.

Výber závisí od recovery objective-u, data modelu a tolerancie ku konfliktom. Active-active nie je automaticky lepšie, ak business proces vyžaduje jeden autoritatívny writer.

## 22. Retry

Retry opakuje operáciu po failure, ktorý môže byť dočasný. Je vhodný napríklad pri krátkom network interruption alebo dočasnom throttlingu, ale nie pri invalid requeste alebo trvalo zamietnutej authorization.

Bez timeoutu, backoffu a jitteru môžu tisíce clients retryovať naraz a zabrániť dependency v zotavení. Idempotency key alebo iný deduplication mechanizmus je potrebný tam, kde opakovaná operácia môže vytvoriť duplicitnú platbu, objednávku alebo message.

Bezpečný retry contract musí presne vysvetliť každú časť rozhodnutia:

- **Retryable error classes** — rozlišujú transient failure, pri ktorom môže ďalší pokus uspieť, od permanentnej chyby, ktorú opakovanie iba zosilní.
- **Maximálny čas alebo počet attempts** — ohraničuje, ako dlho môže pôvodná operácia spotrebúvať threads, connections a downstream capacity.
- **Exponential backoff a jitter** — rozkladajú ďalšie pokusy v čase, aby sa clients nevrátili k dependency v rovnakom okamihu.
- **Timeout hierarchy** — zabezpečuje, že každý downstream pokus skončí skôr než celkový user alebo workflow deadline.
- **Idempotency alebo deduplication** — zabraňuje tomu, aby opakovaný write vytvoril viac platieb, objednávok alebo messages.
- **Retry budget voči pôvodnému trafficu** — limituje amplification factor, aby zotavujúca sa dependency nebola zahltená prevažne opakovanými pokusmi.

## 23. Circuit breaker

Circuit breaker dočasne zastaví calls na dependency, ktorá opakovane zlyháva alebo prekračuje latency boundary. Namiesto čakania na rovnaký timeout pre každý request systém rýchlo vráti kontrolovaný error alebo fallback a chráni svoje threads a connections.

Typický lifecycle má stavy `closed`, `open` a `half-open`. V stave `half-open` prejde obmedzený počet skúšobných requestov; ak uspejú, circuit sa zavrie, inak zostane dependency izolovaná.

Circuit breaker potrebuje správny scope. Jeden globálny circuit pre všetky tenants alebo operations môže odstaviť zdravé paths kvôli lokalizovanému problému.

## 24. Bulkhead isolation

Bulkhead rozdeľuje kapacitu na samostatné pools, aby jedna skupina requestov nemohla vyčerpať všetky spoločné resources. Názov vychádza z priečok na lodi, ktoré obmedzia zaplavenie na jednu časť trupu.

Praktickou implementáciou môžu byť oddelené thread pools, queues, connection pools, tenant quotas, cells, accounts alebo Regions. Isolation znižuje blast radius, ale príliš malé pools môžu vytvoriť nevyužitú kapacitu a lokálnu saturation aj vtedy, keď je inde kapacita voľná.

## 25. Graceful degradation

Graceful degradation zachová kritickú časť služby a dočasne obmedzí menej dôležité capabilities. Systém môže prejsť do read-only režimu, použiť známu cache, odložiť background processing alebo vypnúť recommendations.

Degradácia musí byť vopred navrhnutá, bezpečná a pozorovateľná. Cached response nie je vhodný fallback, ak môže viesť k nesprávnej finančnej alebo bezpečnostnej operácii, a read-only režim musí jasne informovať používateľa o obmedzení.

## 26. Capacity headroom

Fault tolerance potrebuje rezervu, pretože po zlyhaní musí zostávajúca kapacita prevziať prácu z nefunkčného failure domainu. Ak dve AZ bežne obsluhujú po 50 % trafficu, každá musí byť schopná počas výpadku dočasne obslúžiť približne celý workload alebo musí existovať rýchly a overený scale-out.

```text
normálny stav:     AZ-a 50 % + AZ-b 50 %
výpadok AZ-a:      AZ-b musí zvládnuť približne 100 %
```

Ak obe zóny bežia na 85 %, zonal failure vytvorí okamžitú saturation. Autoscaling nemusí stihnúť reagovať a cloud provider nemusí mať požadovanú instance capacity práve počas rozsiahleho incidentu.

## 27. Quotas a reálna capacity

Cloud quotas obmedzujú počet vCPU, IP adries, targets, concurrent executions, API calls alebo ďalších resources. Autoscaling policy môže byť správna, ale provisioning zlyhá, keď narazí na account quota alebo nedostatok subnet IP adries.

Zvýšenie quota znamená povolenie používať viac resources, nie rezerváciu fyzickej kapacity. Kritický recovery model preto potrebuje quota headroom, vhodné instance diversification, capacity reservations podľa potreby a pravidelný canary test v recovery zóne alebo Regione.

## 28. Elasticity a cost

Elasticity môže znížiť idle cost tým, že odstráni nepotrebnú kapacitu. Rovnaký mechanizmus však môže náklady dramaticky zvýšiť pri attack trafficu, retry storme, zlej metric alebo runaway queue.

Cost guardrails majú byť súčasťou scaling policy, nie iba mesačného reportu. Použi maximálnu kapacitu, budgets, anomaly detection, per-tenant limits a unit-cost metrics, ale limit nastav tak, aby počas legitímneho incidentu neblokoval požadovaný failover.

## 29. Testovanie scalability

Scalability sa nedá preukázať statickým diagramom. Potrebný je workload test, ktorý meria throughput, latency distributions, errors a saturation pri postupnom aj náhlom raste demandu.

Testovacie scenáre majú zahŕňať steady state, burst, dlhý peak, downstream slowdown, scale-out latency, scale-in a quota exhaustion. Dôležité je sledovať aj cost per transaction a recovery po skončení testu, pretože systém môže zvládnuť peak iba za neprimeranú cenu alebo zostať po teste v nestabilnom stave.

## 30. Resilience a fault-injection testing

Fault-injection test overuje konkrétnu hypotézu o správaní pri zlyhaní. Pred experimentom sa definuje steady state, očakávaná reakcia, blast radius a abort conditions.

```text
steady-state evidence
→ fault hypothesis
→ obmedzený experiment
→ observability počas failure
→ recovery validation
→ odstránenie zistenej slabiny
```

Náhodné vypínanie komponentov bez hypotézy nie je kvalitný chaos engineering. Experiment je úspešný aj vtedy, keď odhalí chybný predpoklad, pokiaľ bol blast radius kontrolovaný a výsledok sa premietne do návrhu.

## 31. End-to-end príklad

Predstav si queue-based image-processing službu. Producer zapisuje jobs do durable queue, workers sa škálujú podľa oldest-message age a processing rate a výsledky ukladajú do object storage.

Scalability vzniká pridaním workers a prípadným partitioningom queue. Elasticity vzniká control loopom, ktorý pridáva kapacitu pri raste age a odoberá ju až po dokončení rozpracovaných jobs; fault tolerance zabezpečuje redundantná queue, idempotentný consumer, multi-AZ workers a retry s dead-letter pathom.

Ak sa workers škálujú iba podľa CPU, systém môže reagovať nesprávne, pretože časť práce čaká na storage I/O. Ak queue nemá business-age SLO, backlog môže rásť celé hodiny bez zjavného resource alarmu.

## 32. Troubleshooting scalability a elasticity

Diagnostika má začať otázkou, či problém vzniká pre nedostatočnú kapacitu, nesprávny scaling signal alebo bottleneck mimo škálovanej vrstvy. Samotný počet instances nepreukazuje, že nová kapacita prijíma traffic alebo že dependency dokáže spracovať vyšší throughput.

```text
user impact a workload rate
→ scaling signal a evaluation window
→ desired/provisioned/ready/serving capacity
→ load distribution
→ saturation per layer
→ downstream limits a quotas
→ scale-in alebo retry behavior
```

Typické prípady prepájajú symptóm s vrstvou, ktorú treba overiť:

- **Autoscaler nepridáva capacity** — over metric, policy, cooldown, maximum, quota, launch errors a subnet IP space, pretože zlyhať môže decision loop aj samotný provisioning.
- **Capacity rastie, latency zostáva vysoká** — hľadaj shared lock, database, connection pool, hot partition alebo load-balancer imbalance, ktoré nepridávajú kapacitu spolu s compute vrstvou.
- **Scale-in vytvára errors** — over draining, termination grace, in-flight work, leases a session affinity, aby si odlíšil prerušenie práce od nedostatku celkovej kapacity.
- **Zonal failure preťaží zvyšok** — over headroom, failover routing, instance availability a recovery quota, pretože healthy druhá zóna nemusí mať dostatok serving capacity.
- **Retry storm** — over timeout hierarchy, retry count, jitter, error classification a dependency recovery rate, aby opakované pokusy neblokovali samotné zotavenie.

## 33. Anti-patterny

### Auto Scaling sa považuje za fault tolerance

Autoscaling rieši množstvo kapacity, nie nezávislosť failure domains. Ak sú všetky instances v jednej AZ alebo závisia od jednej databázy, automatické pridávanie replicas neodstráni kritický single point of failure.

### Viac replicas sa považuje za lineárny scale

Throughput rastie iba dovtedy, kým ho neobmedzí shared resource alebo coordination overhead. Pri každom scale teste treba identifikovať, ktorá vrstva sa stala novým bottleneckom.

### Retry bez budgetu

Neobmedzený retry mení pôvodný incident na load amplification. Retry traffic má mať explicitný pomer voči originálnemu trafficu a permanentné failures sa musia rýchlo zastaviť.

### Maximálna utilization ako optimalizácia

Systém bez headroomu nemá priestor pre burst, failover ani pomalší recovery. Krátkodobá úspora sa môže zmeniť na rozsiahly outage pri prvom zlyhaní zóny alebo dependency.

### Scale-to-zero bez latency contractu

Scale-to-zero môže byť ekonomický pre sporadický workload, ale prvý request musí čakať na provisioning a warm-up. Pre latency-critical service treba cold-start čas zahrnúť do SLO alebo udržiavať minimálnu pripravenú kapacitu.

## 34. Kontrolné otázky

1. Aký je rozdiel medzi scalability, elasticity a fault tolerance?
2. Prečo viac application replicas nemusí zvýšiť end-to-end throughput?
3. Kedy je vertical scaling primeranejší než horizontal scaling?
4. Ako sa odlišuje desired, provisioned, ready a serving capacity?
5. Prečo CPU nemusí byť správny scaling signal pre queue consumer?
6. Prečo je scale-in rizikovejší než scale-out?
7. Aký je rozdiel medzi queue load leveling a skutočnou processing capacity?
8. Ako backpressure zabraňuje kaskádovému zlyhaniu?
9. Prečo redundancy vyžaduje nezávislé failure domains?
10. Kedy je active-passive vhodnejší než active-active?
11. Prečo retry potrebuje timeout, backoff, jitter a idempotenciu?
12. Ako circuit breaker a bulkhead chránia odlišnými mechanizmami?
13. Prečo Multi-AZ architektúra potrebuje capacity headroom?
14. Aký je rozdiel medzi quota a reálne dostupnou cloud capacity?
15. Ako navrhneš fault-injection test bez neprimeraného blast radiusu?

## Glossary impact

Relevantné pojmy: scalability, capacity model, bottleneck, vertical scaling, horizontal scaling, diagonal scaling, elasticity, target tracking, step scaling, scheduled scaling, reactive scaling, predictive scaling, scale-out, scale-in, stabilization window, backpressure, load leveling, fault tolerance, redundancy, failure domain, active-active, active-passive, retry budget, circuit breaker, bulkhead, graceful degradation a capacity headroom.

## Oficiálna dokumentácia

- [AWS Well-Architected Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
- [AWS fault isolation boundaries](https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/welcome.html)
- [Amazon EC2 Auto Scaling documentation](https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shared responsibility model](shared-responsibility-model.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: High availability a disaster recovery →](high-availability-disaster-recovery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
