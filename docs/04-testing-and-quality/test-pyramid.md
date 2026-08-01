# Test pyramid

Test pyramid je heuristický model portfólia testov. Odporúča mať veľa rýchlych a úzko scoped testov pri základe, menej integračných testov v strede a malý počet drahých end-to-end testov na vrchu. Nie je to fixná percentuálna kvóta ani tvrdenie, že všetky systémy potrebujú rovnaký pomer.

Základná myšlienka vychádza z trade-offu:

```text
nižší scope
→ rýchlejší feedback
→ lepšia lokalizácia chyby
→ nižšia environment fidelity

vyšší scope
→ viac reálnych hraníc
→ vyššia confidence pre celý journey
→ pomalší a menej diagnostický feedback
```

Test trophy alebo iné varianty kladú väčší dôraz na integration tests, najmä pri aplikáciách, kde riziko vzniká hlavne medzi modulmi a frameworkom. Dôležitý nie je tvar diagramu, ale risk-based umiestnenie dôkazu.

Najnižší vhodný scope je taký, ktorý spoľahlivo aktivuje failure mode. Čistú business funkciu je výhodné testovať unit testom. SQL transaction behavior potrebuje reálnu alebo fidelity-valid databázovú hranicu. DNS, TLS alebo browser behavior nemožno presvedčivo nahradiť čistým unit testom.

Neutrálny príklad e-shopu:

```text
unit:
výpočet ceny a dane

integration:
repository voči databáze

component:
celá API služba s controlled dependencies

contract:
kompatibilita client–provider

E2E:
používateľ vytvorí a zaplatí objednávku
```

Portfólio musí zohľadniť execution time, determinism, maintenance cost, diagnostickosť a unikátny risk coverage. Desať E2E testov, ktoré všetky zlyhajú pri rovnakom database outage-i, neposkytuje desať nezávislých dôkazov.

Pyramid tiež nehovorí, že testy vyššieho scope-u sú menej dôležité. Kritický end-to-end journey môže byť release-blocking aj pri jednom teste, pretože overuje unikátnu kombináciu boundaries, ktorú nižšie testy nevidia.

## 1. Definícia

Test pyramid je model rozdelenia automatizovaných kontrol podľa scope, rýchlosti, ceny, fidelity, stability a diagnostickej hodnoty. Jej základná myšlienka je jednoduchá: väčšinu rizík treba zachytiť čo najnižšie a najlacnejšie, zatiaľ čo široké systémové testy sa používajú iba tam, kde nižší scope nevie poskytnúť potrebný dôkaz.

Klasická vizualizácia:

```text
          E2E
       Integration
          Unit
```

Pyramída nie je percentuálna kvóta a neurčuje univerzálny počet testov. Je to ekonomický a architektonický model feedbacku, ktorý má znižovať čas od zavedenia chyby po jej lokalizované odhalenie.

## 2. Mentálny model: riziko, scope a cena dôkazu

Každý test má cenu vytvorenia, vykonania, údržby a diagnostiky. Čím viac reálnych vrstiev test vykonáva, tým viac druhov chýb môže zachytiť, ale zároveň rastie počet príčin, ktoré môžu spôsobiť jeho zlyhanie.

```text
širší scope
  → viac reálnych integrácií
  → vyššia fidelity
  → pomalší a drahší setup
  → viac variability
  → náročnejšia lokalizácia failure
```

Cieľom pyramídy nie je minimalizovať fidelity. Cieľom je kúpiť dostatočný dôkaz za najnižšiu cenu a širší test pridať iba vtedy, keď overuje nový failure mode alebo novú runtime hranicu.

## 3. Prečo jeden typ testu nestačí

Softvérový systém obsahuje viac druhov rizík:

- lokálna logika — výpočty, podmienky, state transitions a invarianty môžu byť chybné aj bez externých dependencies;
- integration semantics — databáza, broker, filesystem alebo serializer sa môžu správať inak než test double;
- distribuovaný contract — producer a consumer môžu mať rozdielne očakávania o fields, erroroch alebo ordering-u;
- deployment wiring — DNS, routing, TLS, secrets, config a process startup môžu byť chybné napriek správnemu kódu;
- používateľská cesta — jednotlivé komponenty môžu fungovať, ale ich kombinácia nemusí priniesť správny výsledok.

Žiadny test scope neoptimalizuje všetky tieto vlastnosti naraz. Robustná suite preto vrství dôkazy namiesto toho, aby jeden drahý typ testu používala ako univerzálnu ochranu.

## 4. Spodná vrstva: unit tests

Unit test overuje malú, zmysluplnú jednotku správania s minimálnym počtom externých hraníc. „Unit“ nemusí byť jedna funkcia; môže to byť class, modul alebo doménová operácia, pokiaľ je jej správanie možné kontrolovať bez reálnej infraštruktúry.

Silné stránky:

- rýchly feedback — testy typicky bežia v milisekundách až sekundách a môžu sa spúšťať pri každej malej zmene;
- presná lokalizácia — failure zvyčajne ukazuje na malý počet pravidiel alebo branches;
- edge cases — lacno sa testujú hraničné hodnoty, neplatné vstupy, kombinácie stavov a properties;
- determinism — clock, random, filesystem alebo network sa môžu nahradiť explicitnými seams;
- paralelizácia — izolované testy sa ľahko delia medzi workers bez shared state.

Limity:

- neoverujú reálny wiring a dependency konfiguráciu;
- neodhaľujú rozdiely SQL dialektu, serializeru alebo sieťového protokolu;
- môžu byť príliš previazané na internú implementáciu;
- mocks môžu potvrdiť vlastné nesprávne predpoklady o externom systéme.

Unit test je správna voľba pre business rules a invarianty, ale slabý dôkaz pre integračné a deployment riziko.

## 5. Stredná vrstva: integration tests

Integration test overuje spoluprácu s reálnou boundary alebo medzi viacerými reálnymi časťami systému. Boundary môže byť databáza, filesystem, queue, HTTP server, serializer, operating-system API alebo externá služba v kontrolovanom prostredí.

Príklady:

- repository vrstva proti skutočnému PostgreSQL serveru;
- producer a consumer proti reálnemu message brokeru;
- HTTP adapter proti lokálnemu test serveru s reálnou serializáciou;
- migrácia databázy na reprezentatívnej predchádzajúcej schéme;
- aplikácia zapisujúca do filesystemu s reálnymi permissions a symlink semantics.

Integration tests zachytávajú chyby, ktoré izolované mocks nevidia: constraints, transactions, encoding, connection pooling, timeouty, isolation levels, protocol defaults a cleanup behavior. Ich cena je vyššia, preto potrebujú deterministický provisioning, namespacing test data a rýchly recovery pri failure.

## 6. Component tests

Component test spúšťa celý deployable alebo logický komponent a nahrádza iba jeho externé hranice. Napríklad celý API proces môže používať reálnu routing, middleware, serialization a databázu, zatiaľ čo vzdialená platobná služba je nahradená kontrolovaným fake serverom.

Component test poskytuje širší behavior dôkaz než úzko zameraný integration test, ale stále umožňuje kontrolovať vstupy, failures a timing externých závislostí. Je vhodný na overenie toho, či vnútorné vrstvy komponentu spolupracujú správne bez nákladov celej produkčnej topológie.

## 7. Vrchná vrstva: end-to-end tests

E2E test sleduje kritickú cestu cez väčšiu časť nasadeného systému. Môže začínať v browseri alebo API klientovi a pokračovať cez proxy, služby, databázu, broker a worker až po viditeľný výsledok.

```text
client
→ edge/proxy
→ application services
→ storage alebo broker
→ asynchronous processing
→ používateľský výsledok
```

Silné stránky:

- overujú reálne wiring, routing a konfiguráciu;
- zachytávajú chyby vznikajúce kombináciou viacerých komponentov;
- poskytujú dôkaz pre kritické používateľské alebo prevádzkové journeys;
- overujú, že testovaný artifact je v cieľovom prostredí skutočne použiteľný.

Limity:

- pomalší setup a vykonanie;
- vysoká citlivosť na timing, shared data a environment drift;
- failure má veľa možných príčin;
- výsledok sa ťažšie reprodukuje lokálne;
- suite sa pri nekontrolovanom raste stáva bottleneckom delivery.

E2E vrstva má byť malá a zameraná na kritické journeys, nie na každú validáciu poľa alebo UI variant.

## 8. Scope nie je počet procesov

Test scope sa definuje podľa toho, ktoré boundaries sú reálne a ktoré sú kontrolované. Dva testy spúšťajúce jeden proces môžu mať rozdielny scope, ak jeden používa in-memory storage a druhý reálnu databázu.

Rovnako E2E nemusí znamenať celý podnikový ekosystém. Má definovaný začiatok a koniec relevantnej cesty, napríklad od public API requestu po vytvorený auditovaný business state.

Dôležité otázky:

```text
Ktoré komponenty sa vykonávajú reálne?
Ktoré boundaries sú nahradené?
Kde vzniká oracle?
Aké failure modes zostávajú mimo scope?
```

Bez tejto definície pomenovania „unit“, „integration“ a „E2E“ poskytujú málo informácií.

## 9. Fidelity, determinism a diagnosability

Fidelity opisuje podobnosť testu s cieľovým runtime. Determinism opisuje, či rovnaký vstup a stav vedú k rovnakému výsledku. Diagnosability opisuje, ako rýchlo sa dá zo zlyhania určiť mechanizmus a owner.

Tieto vlastnosti sú v napätí:

- reálna externá služba zvyšuje fidelity, ale môže priniesť latency, rate limits a nepredvídateľné zmeny;
- fake služba zvyšuje determinism, ale nemusí presne reprezentovať protocol edge cases;
- široký E2E test potvrdí cestu, ale failure môže pochádzať z desiatok komponentov;
- úzky unit test lokalizuje chybu, ale nemá dôkaz o deployment wiring-u.

Dobrá suite kombinuje tieto vlastnosti. Namiesto maximalizácie jednej z nich vytvára viac vrstiev s jasne odlišnou dôkaznou hodnotou.

## 10. Test trophy

Test trophy zdôrazňuje statické kontroly a väčší podiel integration tests:

```text
          E2E
       Integration
          Unit
     Static checks
```

Model reaguje na situáciu, keď množstvo izolovaných unit testov overuje interné calls, ale nie skutočné správanie aplikácie cez verejné rozhranie a reálne moduly. Je často vhodný pre frontend, API a modulárne aplikácie, kde component/integration test poskytuje vysokú behavior hodnotu za rozumnú cenu.

Pyramída a trophy nie sú protiklady. Obe odmietajú dominanciu drahých E2E testov a podporujú presun kontroly do najnižšej vrstvy, ktorá ešte zachytí relevantné riziko.

## 11. Test diamond a honeycomb

Test diamond používa väčšiu strednú vrstvu integration/component tests a menej veľmi izolovaných unit aj širokých E2E testov. Môže byť vhodný tam, kde doménová logika je jednoduchá, ale hlavné riziko leží v protokoloch, storage alebo transformácii dát.

Pri microservices sa používa aj test honeycomb: silný dôraz na component, contract a observability-driven tests okolo každej služby, pričom globálnych E2E testov je málo. Takýto model predpokladá kvalitné service boundaries, contract ownership a schopnosť testovať komponent samostatne.

Tvar modelu sa má odvodiť z architektúry a failure modes. Nemá sa kopírovať podľa trendu alebo typu frameworku.

## 12. Ice cream cone anti-pattern

Ice cream cone znamená, že väčšinu dôkazu poskytujú manuálne alebo široké E2E testy a spodné vrstvy sú slabé.

```text
veľa manuálnych/E2E testov
       integration
          unit
```

Dôsledky:

- chyby sa odhaľujú neskoro po dokončení veľkého batchu;
- test cycle je pomalý a blokuje paralelnú prácu;
- failure localization je náročná;
- test data a prostredie sa stávajú zdieľaným bottleneckom;
- flaky výsledky podporujú rerun-until-green;
- tím sa bojí zmeny suite, pretože každá úprava je drahá.

Náprava nie je iba „napísať viac unit testov“. Treba analyzovať failure modes a presunúť konkrétne assertions do nižšieho scope, pričom E2E ponechá iba unikátnu integračnú hodnotu.

## 13. Test patrí do najnižšieho spoľahlivého scope

Pravidlo:

```text
umiestni kontrolu čo najnižšie,
ale nie nižšie, než kde ešte zachytí reálny failure mode
```

Príklady:

- povolené enum hodnoty — schema alebo unit test, pretože nepotrebujú deployment;
- SQL uniqueness constraint — database integration test, pretože in-memory model nemusí mať rovnaké semantics;
- producer/consumer kompatibilita — contract test, nie globálny E2E test;
- nesprávny reverse-proxy route — deployment smoke alebo component/E2E test s reálnym proxy;
- používateľ nevie dokončiť checkout — acceptance alebo E2E test kritickej journey;
- regionálny failover — resilience alebo game-day validation v kontrolovanom prostredí.

Presun testu nižšie skracuje feedback, znižuje variabilitu a zlepšuje lokalizáciu. Presun príliš nízko môže odstrániť presne tú boundary, v ktorej chyba vzniká.

## 14. Redundancia podľa failure mode

Rovnaký invariant môže byť overený vo viacerých vrstvách, ak každá vrstva chráni pred iným mechanizmom zlyhania.

Príklad tenant isolation:

- unit test — overí policy decision pre rôzne identity;
- DB integration test — overí tenant filter a query behavior;
- API test — overí authorization a response bez leakage;
- E2E test — overí kritickú cestu cez reálne identity a routing;
- production detection — audit a anomaly signal hľadajú nečakaný cross-tenant access.

Toto nie je zbytočná duplicita, pretože každá vrstva pridáva novú boundary. Zbytočná redundancia vzniká vtedy, keď desiatky E2E scenárov opakujú rovnakú field validation bez ďalšej fidelity.

## 15. Test suite ako portfólio rizík

Suite sa navrhuje podľa rizika, nie podľa počtu files alebo coverage targetu. Pre každý významný failure mode sa vyberie kombinácia kontrol s primeranou cenou a silou dôkazu.

Riziko ovplyvňujú:

- impact — finančný, bezpečnostný, právny, používateľský alebo prevádzkový dopad;
- pravdepodobnosť — ako často sa daná vrstva alebo contract mení;
- detectability — či by failure zachytila observability pred používateľským dopadom;
- blast radius — koľko tenantov, služieb alebo dát môže byť ovplyvnených;
- reversibility — či sa zmena dá rýchlo rollbacknúť bez straty dát;
- historical evidence — ktoré chyby sa v tejto oblasti už opakovali.

Payment idempotency alebo authorization potrebuje viac vrstiev dôkazu než statický marketingový text. Test portfolio má túto asymetriu odrážať.

## 16. Ekonomika feedbacku

Cena chyby rastie s časom, počas ktorého zostáva neodhalená. Unit failure pri lokálnom behu typicky opraví autor v kontexte zmeny; E2E failure o hodinu neskôr vyžaduje rekonstrukciu prostredia a širšiu koordináciu.

Praktické feedback lanes:

```text
editor/pre-commit      sekundy
PR fast lane           jednotky minút
full component/integration suite  desiatky minút
nightly alebo periodic broader suite
pre-release E2E/performance/resilience
production synthetics a SLO validation
```

Dlhší test nepatrí automaticky iba do nightly jobu. Ak chráni kritické nereverzibilné rozhodnutie, musí bežať pred týmto rozhodnutím alebo musí existovať iná bezpečná control vrstva.

## 17. Change amplification a maintenance cost

Široký test často závisí od množstva UI selectors, test data, service versions a environment configu. Jedna bezpečná produktová zmena preto môže vyžadovať aktualizáciu mnohých testov, hoci behavior contract zostal rovnaký.

Tento jav je change amplification. Je signálom, že testy môžu byť previazané na implementáciu alebo že priveľa assertions je umiestnených vo vysokom scope.

Sleduj:

- počet testov menených pri jednej produktovej zmene;
- podiel failure spôsobených fixture alebo environmentom;
- čas od failure po root cause;
- priemernú dĺžku a ownership testov;
- koľko E2E scenárov chráni unikátny risk.

## 18. Test environment ako produkt

Stredné a horné vrstvy potrebujú provisioning, data lifecycle, observability a recovery. Zdieľané prostredie bez vlastníctva sa rýchlo stane zdrojom flakiness a fronty.

Dobrý test environment má:

- versioned a reprodukovateľný setup;
- namespacing alebo izoláciu paralelných behov;
- kontrolovaný seed dát a deterministic cleanup;
- dostupné logs, traces, screenshots a network evidence;
- jasnú politiku externých dependencies;
- limitovaný lifetime a automatický garbage collection;
- ownera pre platformové failure, nie iba autorov testov.

Ephemeral environment nie je automaticky hermetický. Ak používa shared database, DNS, rate-limited SaaS alebo globálne identity, shared-state failure zostáva.

## 19. Selection a affected tests

Veľká suite môže používať affected-test selection podľa zmenených files a dependency graphu. Cieľom je zrýchliť fast lane bez straty relevantného pokrytia.

Selection je bezpečná iba vtedy, keď dependency graph obsahuje aj nepriame väzby, ako schema, build tool, base image, shared config a test fixtures. Chybná selekcia vytvára false green pipeline tým, že test vôbec nespustí.

Preto sa často kombinuje:

- presný affected run pri každom PR;
- širší periodic run;
- full suite pred kritickým release;
- telemetry selection misses a post-merge failures.

## 20. Flaky tests a quarantine

Flaky test vracia rozdielne výsledky bez relevantnej zmeny produktu. V blocking suite znižuje dôveru v celý feedback systém a učí tím ignorovať červené výsledky.

Možné príčiny:

- shared test data alebo order dependency;
- fixed sleeps namiesto condition-based wait;
- reálny wall clock, random alebo timezone bez kontroly;
- resource saturation a paralelná contention;
- environment drift alebo nestabilná externá služba;
- cleanup, ktorý po failure nezanechá čistý stav.

Quarantine je dočasný containment, nie vyriešenie. Musí mať issue, ownera, dátum expirácie, first-attempt pass metriku a plán presunu assertionu do stabilnejšieho scope.

## 21. Infrastructure testing pyramid

Pre Infrastructure as Code môže vrstvenie vyzerať takto:

```text
syntax, schema a formatter
→ policy a module unit tests
→ plan assertions a provider integration
→ apply do sandboxu
→ connectivity a deployment smoke
→ failover, restore a game day
```

Každá vrstva odpovedá na inú otázku. `terraform validate` overí syntax a základný model; sandbox apply overí provider a permissions; connectivity probe overí reálnu enforcement cestu; game day overí recovery a operability.

Nahradiť všetky vrstvy jediným produkčným apply je nebezpečné. Rovnako iba statická policy neposkytuje dôkaz, že výsledná sieťová alebo IAM cesta funguje podľa zámeru.

## 22. Príklad: objednávkový systém

Riziká a vhodné scopes:

| Failure mode | Najnižší spoľahlivý scope | Dodatočný dôkaz |
|---|---|---|
| nesprávny výpočet dane | unit/property test | component test reprezentatívnej objednávky |
| duplicate payment pri retry | component/integration test s payment fake | E2E kritickej platobnej journey |
| nekompatibilná event schema | contract test | broker integration test |
| chýbajúci DB index | migration/integration a performance test | produkčná query latency observability |
| chybný proxy route | deployment smoke | synthetic transaction |
| používateľ nevie dokončiť checkout | E2E/acceptance | RUM a conversion guardrail |

Tabuľka ukazuje, že „najnižší scope“ neznamená jediný test. Kritické riziko môže mať ďalší dôkaz vo vyššej vrstve, ale základná logika sa nemá testovať iba cez browser.

## 23. Suite health metrics

Počet testov nie je dostatočná metrika. Sleduj vlastnosti feedback systému:

- first-attempt pass rate — odhaľuje flakiness skrytú rerunmi;
- p50/p95 duration — ukazuje bežný aj tail čas suite;
- queue time — odhaľuje nedostatok runner kapacity;
- failure localization time — meria, ako rýchlo tím nájde mechanizmus;
- quarantine age — ukazuje akumulovaný test debt;
- false-positive rate — meria náklad noisy gates;
- escaped defect mapping — ukazuje, ktoré failure modes suite prehliada;
- maintenance amplification — koľko testov sa mení pri behavior-stabilnej zmene.

Metriky majú viesť k zmene scope, isolation alebo ownershipu, nie k penalizácii tímu za červený test.

## Ako vybrať správny test scope

Test pyramid nie je príkaz, aby každá codebase mala presný počet unit, integration a end-to-end testov. Je to heuristika o cene spätnej väzby. Čím väčší scope test vykonáva, tým viac reálnych hraníc môže pozorovať, ale zároveň rastie čas, množstvo setupu, počet možných príčin zlyhania a náročnosť diagnostiky. Malý test býva rýchly a presný, no neposkytuje dôkaz o konfigurácii, sieti alebo spolupráci procesov.

Správna otázka preto nie je „do ktorej vrstvy patrí tento test podľa názvu frameworku“, ale „aký najmenší scope dokáže zachytiť konkrétny failure mode“. Výpočet ceny alebo authorization decision možno overiť unit testom, pretože riziko leží v lokálnej logike. SQL transakcia, serializácia eventu alebo správanie retry klienta potrebuje reálny adapter a integration scope. Kritická používateľská cesta potrebuje niekoľko end-to-end kontrol, pretože jej riziko vzniká až spojením identity, routingu, aplikácie, databázy a side effectu.

Fidelity označuje, do akej miery testované prostredie a závislosti reprodukujú mechanizmus, o ktorom chceme rozhodovať. Fake databáza môže byť vhodná pre domain workflow, ale nevie potvrdiť isolation level, index behavior alebo engine-specific SQL. Vyššia fidelity však sama osebe nevytvára lepší test. End-to-end test s neurčitým oraclom môže byť menej hodnotný než malý component test, ktorý presne kontroluje invariant a forbidden outcome.

Portfólio preto vzniká od rizík. Veľa lacných testov chráni lokálnu logiku a hraničné prípady, menší počet integračných testov chráni technologické kontrakty a úzky súbor vyšších testov overuje najdôležitejšie cesty. Keď vyšší test odhalí defect, tím sa má pýtať, či možno rovnaký failure mode zachytiť skôr a lacnejšie. To neznamená odstrániť pôvodný end-to-end dôkaz, ale doplniť rýchlejšiu regresnú kontrolu na vhodnej hranici.

Pyramid sa mení podľa architektúry. Služba s bohatou domain logikou bude mať inú skladbu než tenký integračný gateway alebo dátová pipeline. Dôležité je, aby žiadne kritické riziko nezostalo pokryté iba pomalým, flaky alebo slabo diagnostickým testom.

## 24. Anti-patterny

### Pyramída ako percentuálna kvóta

Pravidlo „70 % unit, 20 % integration, 10 % E2E“ ignoruje architektúru a riziká. Správny pomer pre transformačnú knižnicu sa bude líšiť od integračnej platformy alebo IaC repository.

### Všetko cez browser

UI testy overujú aj routing a rendering, ale sú drahým miestom pre business edge cases a field validation. Väčšina takýchto assertions patrí do unit, API alebo component scope.

### Všetko mockované

Suite môže byť rýchla a zelená, hoci reálna databáza, serializer alebo remote API má iné semantics. Aspoň kritické boundaries potrebujú reálny integration alebo contract dôkaz.

### E2E ako náhrada observability

E2E test vie potvrdiť zvolenú cestu v konkrétnom čase. Nevie dlhodobo reprezentovať všetky production traffic patterns, preto nenahrádza SLI, logs, traces a business telemetry.

### Nightly ako skládka pomalých testov

Testy sa presunú do nightly jobu bez jasného rozhodnutia, ktoré chránia. Failure príde neskoro, nemá ownera a zostáva ignorovaný.

## 25. Rozhodovací rámec pre nový test

Pred implementáciou odpovedz:

1. Aký failure mode a dopad test pokrýva?
2. Aký najnižší scope ho spoľahlivo odhalí?
3. Ktoré boundaries musia byť reálne?
4. Aký oracle potvrdí význam výsledku?
5. Aký setup, data lifecycle a cleanup potrebuje?
6. Aký je požadovaný feedback time?
7. Ako sa failure lokalizuje a aké artifacts sa uchovajú?
8. Je test bezpečne paralelizovateľný?
9. Pridáva novú fidelity alebo iba duplikuje assertion?
10. Kto vlastní test a jeho environment?
11. Kedy sa test odstráni alebo zjednoduší?
12. Aký produkčný signál doplní jeho blind spots?

## 26. Kontrolný checklist portfólia

- kritické failure modes majú identifikovateľný dôkaz;
- väčšina lokálnej logiky sa testuje v rýchlom a izolovanom scope;
- reálne boundaries majú integration alebo contract testy;
- E2E suite je malá, kritická a diagnostikovateľná;
- test data sú izolované a cleanup je spoľahlivý;
- blocking suite nemá dlhodobo flaky testy bez ownera;
- pipeline má primerané fast a full lanes;
- affected-test selection je krytá širším periodic runom;
- suite health sa meria nad rámec počtu a coverage;
- produkčná validation dopĺňa predprodukčné blind spots.

## 27. Časté omyly

### „Čím vyšší scope, tým kvalitnejší test“

Nie. Vyšší scope prináša inú fidelity, ale aj väčšiu variabilitu a slabšiu lokalizáciu. Kvalita závisí od zhody testu s rizikom a od sily oraclu.

### „Unit test znamená jedna funkcia“

Nie. Unit je izolovaná jednotka správania; jej veľkosť závisí od architektúry a verejného contractu.

### „Integration test musí používať viac microservices“

Nie. Aplikácia proti reálnej databáze alebo filesystemu je integration test, pretože overuje reálnu boundary.

### „Redundancia medzi vrstvami je vždy waste“

Nie. Je užitočná, keď každá vrstva chráni proti odlišnému mechanizmu zlyhania alebo pridáva novú fidelity.

### „Flaky E2E je nevyhnutná cena fidelity“

Nie. Niektorá variabilita je vyššia, ale chronická flakiness zvyčajne signalizuje shared state, zlé waits, nekontrolované dependencies alebo nevhodný scope.

## 28. Kontrolné otázky

1. Čo test pyramid optimalizuje?
2. Prečo nie je percentuálnou kvótou?
3. Aký je rozdiel medzi fidelity, determinismom a diagnosability?
4. Čo odlišuje unit, integration, component a E2E scope?
5. Kedy je test trophy alebo diamond vhodnejší opis portfólia?
6. Čo je ice cream cone anti-pattern?
7. Čo znamená najnižší spoľahlivý scope?
8. Kedy je redundancia medzi vrstvami užitočná?
9. Ako affected-test selection môže vytvoriť false green?
10. Prečo musí mať test environment vlastníctvo a lifecycle?
11. Ktoré metriky ukazujú zdravie suite?
12. Ako by si navrhol test pyramid pre Infrastructure as Code?

## 29. Zhrnutie

Test pyramid je model alokácie dôkazov podľa rizika, feedback time a nákladov. Väčšinu lokálnej logiky chráni rýchla spodná vrstva, reálne boundaries stredná vrstva a iba kritické používateľské alebo deployment journeys široká horná vrstva.

Správny tvar suite závisí od architektúry. Dôležité je umiestniť každý assertion do najnižšieho scope, ktorý ešte zachytí reálny failure mode, a pravidelne merať stabilitu, diagnostikovateľnosť a reziduálne riziko celého portfólia.

## Glossary impact

Relevantné pojmy: test pyramid, test trophy, test diamond, test honeycomb, ice cream cone, test scope, fidelity, determinism, diagnosability, affected-test selection, first-attempt pass rate, quarantine a test portfolio.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Verification vs. validation](verification-vs-validation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Unit, integration a component tests →](unit-integration-component-tests.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
