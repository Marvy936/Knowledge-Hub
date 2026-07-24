# Flaky tests a test data

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Testing and Software Quality
- Predpoklady: [Mocks, stubs a fakes](mocks-stubs-fakes.md), [End-to-end a acceptance tests](end-to-end-and-acceptance-tests.md)
- Súvisiace témy: nondeterminism, first-attempt pass rate, quarantine, retries, test isolation, fixtures, synthetic data, cleanup, environment saturation

## 1. Mentálny model

Flaky test pri rovnakom source revision, deklarovaných vstupoch a očakávanom environment contracte niekedy prejde a niekedy zlyhá. Flakiness znamená, že testovací systém nevie spoľahlivo rozlíšiť správnu zmenu od regresie.

```text
rovnaký kandidát
+ deklarovane rovnaké vstupy
+ rovnaký test contract
→ rozdielny výsledok
→ existuje skrytý alebo nekontrolovaný vstup
```

Skrytý vstup môže byť v samotnom teste, testovanom systéme, prostredí, dátach, externých dependencies alebo CI orchestration. Cieľom nie je iba „stabilizovať test“, ale identifikovať, ktorá nondeterministická boundary ovplyvnila verdict.

## 2. Flaky test verzus intermittent product defect

Nie každý premenlivý failure je chyba testu. Test môže korektne odhaľovať race condition, lost update, startup race, resource leak alebo timeout v produkčnom kóde.

Rozlišuj:

- **test flakiness** — test používa nesprávny wait, shared state, nestabilný selector alebo neizolované dáta;
- **system intermittency** — aplikácia sa pri rovnakom scenári reálne správa rozdielne kvôli concurrency, consistency alebo resource limitu;
- **environment instability** — runner, network, storage alebo external service porušuje deklarovaný test contract;
- **orchestration failure** — test nebežal, artifact chýbal alebo CI zle agregoval výsledok.

Rerun môže ukázať, že failure nie je deterministický. Neurčuje však automaticky, do ktorej kategórie patrí.

## 3. Prečo flakiness poškodzuje delivery

Flaky suite mení správanie tímu. Keď červený výsledok často neznamená regresiu, vývojári začnú rerunovať namiesto diagnostiky.

Dôsledky sú:

- reálne regresie sa zamieňajú za „známy flaky test“;
- blocking gates strácajú autoritu;
- lead time rastie o queue a rerun čas;
- vznikajú manual bypassy;
- batch size sa zväčšuje, pretože feedback je drahý;
- ownership sa presúva z opravy príčiny na správu rerunov;
- intermittent product chyby unikajú do produkcie.

Testovací systém je rozhodovací mechanizmus. Jeho prvou požiadavkou je dôveryhodný verdict.

## 4. Deklarované a skryté vstupy

Reprodukovateľný test musí poznať všetky vstupy, ktoré môžu meniť výsledok.

```text
source revision
artifact version
test code a config
fixture a schema version
clock a timezone
random seed
process order a concurrency
OS/runtime/tool versions
resource limits
external dependency state
```

Ak test tvrdí, že beží s rovnakými vstupmi, ale neuchováva seed, environment metadata alebo dependency version, flakiness sa ťažko dokazuje aj diagnostikuje.

## 5. Taxonómia príčin

### Timing a race conditions

Operácia ešte neskončila, test pozoruje prechodný stav alebo dve paralelné operácie súťažia bez explicitnej synchronizácie.

### Shared mutable state

Testy používajú rovnakú databázu, účet, cache, queue, filesystem path, singleton alebo environment variable.

### Order dependence

Jeden test mení stav, ktorý iný test implicitne očakáva. Výsledok závisí od poradia alebo od toho, či sa test spustí samostatne.

### Environment dependence

Výsledok mení timezone, locale, filesystem ordering, CPU scheduling, OS, runtime version, port availability alebo sieťová latencia.

### External dependency

Shared test service má outage, rate limit, nekontrolované dáta, eventual consistency alebo iné tenants.

### Randomness

Seed alebo generovaný input nie je uložený, prípadne test nesprávne očakáva konkrétne poradie random calls.

### Resource saturation

Runner, database, broker alebo test environment je preťažený. Timeout je symptóm kapacitného problému, nie nutne chyba timeout hodnoty.

### Test orchestration

Shard sa nespustí, artifact sa stratí, cleanup job koliduje s ďalším runom alebo CI nesprávne priradí výsledok k commitu.

## 6. Fixed sleep anti-pattern

Pevný sleep nečaká na podmienku. Iba odkladá assertion o zvolený čas.

```python
time.sleep(5)
assert job.finished
```

Na rýchlom stroji zbytočne spomaľuje test. Na pomalom alebo preťaženom runneri môže byť príliš krátky. Zvýšenie na 30 sekúnd znižuje frekvenciu failure, ale neodstraňuje race.

Použi condition-based wait:

```python
wait_until(
    lambda: job.finished,
    timeout=10,
    description="job reaches terminal state",
)
```

Wait má pri failure uchovať posledný observed state, elapsed time a relevantnú timeline.

## 7. Condition-based waiting

Kvalitný wait contract obsahuje:

- konkrétnu success condition;
- deadline, nie neobmedzený retry;
- interval alebo bounded backoff;
- terminal failure states;
- cancellation;
- diagnostiku poslednej hodnoty;
- korelačné ID alebo event timeline.

Polling príliš často môže preťažiť testovaný systém. Polling príliš zriedka zbytočne predlžuje suite. Interval má zodpovedať očakávanej latency a nákladom observationu.

## 8. Eventual consistency

Asynchrónny workflow má viac odlišných míľnikov:

```text
request prijatý
→ command commitnutý
→ event publikovaný
→ consumer spracoval event
→ read model aktualizovaný
→ používateľský výsledok viditeľný
```

Test musí pomenovať, ktorý míľnik je oracle. HTTP 202 neznamená, že downstream side effect už existuje.

Consistency contract má definovať maximálnu očakávanú dobu, terminal failure a observable state. Neobmedzené čakanie môže zmeniť poruchu na pomalý „pass“.

## 9. Deterministický čas

Wall clock je skrytý globálny vstup. Testy majú používať explicitný clock, timezone a pri durations monotonic time.

Kontrolovať treba:

- pevný instant;
- timezone;
- DST transition;
- koniec mesiaca a leap day;
- expiry boundary;
- retry schedule;
- lease renewal;
- clock skew medzi komponentmi.

Fake clock musí byť prepojený so schedulerom vedome. Posunutie `now` nemusí automaticky vykonať pending task, ak produkčný scheduler reaguje na timer queue.

## 10. Randomness a property-based tests

Randomizovaný test má pri failure uložiť:

- seed;
- pôvodný generated input;
- minimalizovaný counterexample;
- generator a framework version;
- relevantnú configuration;
- execution order, ak sa randomizoval aj test order.

Property-based framework môže failure „shrinknúť“ na malý príklad. Tento counterexample je vhodný pre trvalý regression test.

Samotný seed nemusí stačiť, ak sa medzi verziami zmení generator algorithm alebo počet random calls. Preto uchovaj aj konkrétny failing input.

## 11. Order dependence

Order-dependent test prejde iba po inom teste alebo zlyhá po konkrétnom predecessorovi. Odhaľovanie:

- spúšťať test samostatne;
- randomizovať order a ukladať seed;
- spustiť suite v opačnom poradí;
- rozdeliť tests do rôznych shardov;
- opakovať suspect pair;
- porovnať clean environment s reused environmentom.

Root cause býva shared state, neobnovená konfigurácia, global singleton, nevyčistená databáza alebo test, ktorý očakáva cudziu fixture.

## 12. Paralelná izolácia

Paralelné testy musia vlastniť svoje zdroje. Izolácia môže používať:

- database/schema/tenant per worker;
- unikátny resource prefix z run ID a test ID;
- OS-assigned ephemeral port;
- temp directory per test;
- queue/topic namespace;
- dedikované credentials;
- feature-flag namespace;
- idempotentný cleanup.

Unikátny názov musí byť dostatočne dlhý, no rešpektovať platform limits. Collision pri truncation alebo case folding je častý skrytý problém.

## 13. Port a startup race

Hardcoded port vedie ku kolíziám medzi workers alebo so systémovým procesom. Preferuj bind na port `0`, z ktorého OS vyberie voľný port, a odovzdaj reálnu hodnotu klientovi.

```text
server process started
≠ server ready
```

Readiness má overiť, že socket počúva a služba je schopná spracovať relevantný request. Process existence alebo log line nemusia znamenať pripravenosť.

## 14. Environment saturation

Test môže zlyhávať iba pri vysokom paralelizme, pretože runner alebo dependency dosiahne limit:

- CPU throttling;
- memory pressure alebo OOM;
- file-descriptor exhaustion;
- connection-pool saturation;
- database lock contention;
- rate limit;
- disk I/O queue;
- ephemeral port exhaustion;
- test artifact upload bottleneck.

Pri timeoutoch koreluj test timeline s resource metrics. Zvýšenie timeoutu môže iba skryť neudržateľnú test-environment kapacitu.

## 15. External dependencies

Test závislý od verejného internetu alebo shared sandboxu nie je plne hermetický. Ak je external dependency súčasťou testovaného rizika, musí mať explicitný contract:

- dostupnosť a maintenance window;
- rate limit;
- test tenant a credentials;
- data ownership;
- cleanup;
- version alebo contract;
- failure classification;
- fallback alebo quarantine policy.

Pre rýchle suites preferuj local fake, mock server alebo emulator a doplň periodický sandbox/contract test.

## 16. Test data lifecycle

Test data nie sú iba input fixture. Majú lifecycle:

```text
navrhnúť scenár
→ vytvoriť alebo vygenerovať dáta
→ versionovať schema a generator
→ izolovať run
→ použiť v teste
→ zachovať diagnostické identifiers
→ vyčistiť alebo expirovať
→ auditovať privacy a retention
```

Dáta musia reprezentovať relevantné boundaries bez zbytočného objemu a citlivosti.

## 17. Hand-crafted fixtures

Ručná fixture je malý explicitný dataset pre konkrétny scenár. Je vhodná, keď každý field nesie význam a reviewer má vedieť presne, prečo je hodnota prítomná.

Nevýhodou je maintenance pri schema evolution. Obrovská JSON fixture môže obsahovať veľa nepodstatných defaults a skryť relevantný rozdiel.

Preferuj minimálnu fixture alebo builder, ktorý explicitne ukáže scenario-specific fields.

## 18. Factories a builders

Factory vytvára validný default object a umožňuje override relevantných vlastností.

```python
user = user_factory(
    role="admin",
    active=False,
)
```

Dobrá factory:

- má stabilné, validné defaults;
- nepoužíva náhodnosť bez reprodukovateľného seedu;
- umožňuje explicitné overrides;
- neskrýva security alebo business-critical fields;
- generuje unikátne identifiers iba tam, kde je to potrebné;
- má versionovaný contract so schema evolution.

Príliš „magická“ factory vytvorí veľké graphy a test prestane ukazovať vlastné preconditions.

## 19. Golden a snapshot data

Golden file alebo snapshot uchováva očakávaný komplexný output. Je vhodný, keď diff zostáva čitateľný a reviewer vie posúdiť význam zmeny.

Stabilizuj:

- ordering;
- timestamps;
- random IDs;
- newline a encoding;
- serializer version;
- platform-specific paths;
- floating-point formatting.

Automatické prepísanie snapshotu pri failure ruší oracle. Baseline update musí byť explicitný a reviewovaný.

## 20. Synthetic datasets

Synthetic data sú navrhnuté bez kopírovania reálnych osobných údajov. Majú modelovať relevantné distribúcie, correlations a edge cases.

Náhodný generátor s uniform distributions nemusí reprezentovať produkciu. Performance alebo migration test môže potrebovať:

- hot keys;
- skewed tenant sizes;
- Unicode a locale variants;
- sparse aj dense records;
- long-tail payloads;
- historical schema versions.

Generator version, seed a parameters patria do provenance výsledku.

## 21. Production-derived data

Production-derived data sú vysokorizikové. Private repository ani non-production environment neodstraňuje privacy, licensing a security povinnosti.

Pred použitím treba riešiť:

- právny základ a schválenie;
- data minimization;
- anonymizáciu alebo pseudonymizáciu;
- re-identification risk;
- secrets a tokens;
- access control;
- encryption;
- retention a deletion;
- audit prenosu;
- oddelenie environmentov.

Maskovanie niekoľkých stĺpcov nemusí byť dostatočné. Kombinácia quasi-identifiers môže osobu znovu identifikovať.

## 22. Fixture provenance

Pri failure musí byť jasné, s akými dátami test bežal. Uchovaj:

- fixture alebo dataset version;
- schema/migration version;
- factory/generator version;
- seed a parameters;
- anonymization version;
- test-created resource IDs;
- environment a tenant;
- creation timestamp.

Bez provenance môže rovnaký názov fixture po zmene reprezentovať iný input a znemožniť reprodukciu historického failure.

## 23. Database isolation

Bežné stratégie:

- transaction rollback;
- schema alebo database per worker;
- disposable container;
- snapshot restore;
- immutable seed plus unique rows;
- deterministic cleanup podľa run labelu.

Transaction rollback neizoluje async worker na inom connection, committed side effect, database trigger s externým efektom ani samotné transaction semantics. Scope testu určuje vhodný model.

## 24. Setup lifecycle

Setup má vytvoriť minimálny požadovaný stav a potvrdiť preconditions pred spustením action.

```text
allocate namespace
→ create dependencies
→ wait for readiness
→ create fixture state
→ verify precondition
→ run action
```

Ak setup zlyhá, test verdict nemá tvrdiť, že product behavior je chybný. Report má rozlišovať setup/infrastructure failure od assertion failure.

## 25. Idempotentný setup

CI môže job retry-nuť po partial failure. Setup musí vedieť spracovať:

- resource už existuje;
- predchádzajúci run skončil pred registráciou ownershipu;
- create request bol commitnutý, ale response sa stratila;
- rovnaký job ID sa spustil znova;
- časť dependencies existuje a časť nie.

Preferuj unique resources alebo reconcile semantics. Fragile „delete everything and recreate“ môže zasiahnuť paralelný run.

## 26. Cleanup ownership

Každý vytvorený resource potrebuje owner label, run ID a cleanup policy. Cleanup má prebehnúť po success aj failure, no diagnostické artifacts treba zachovať pred odstránením relevantného stavu.

Viac vrstiev ochrany:

- `finally` alebo fixture teardown;
- explicitný cleanup job;
- TTL na dočasných resources;
- periodický garbage collector;
- cost a orphan dashboard;
- bezpečnostný limit, ktorý bráni mazaniu cudzieho namespace-u.

Cleanup failure je samostatný failure. Ak sa ignoruje, ďalšie testy môžu zlyhávať a cloud náklady rásť.

## 27. Resource leaks

Flaky suite môže postupne degradovať v rámci dlhého runu kvôli leakom:

- neuzavreté sockets;
- processes a containers;
- database connections;
- temp files;
- threads alebo event loops;
- subscriptions;
- credentials alebo leases.

Diagnostika porovnáva clean-run behavior s behaviorom po stovkách testov, sleduje resource counters a spúšťa suspect test opakovane v jednom procese.

## 28. Retry ako diagnostický nástroj

Retry môže poskytnúť informáciu o reprodukovateľnosti, ale prvý failure musí zostať súčasťou výsledku.

Uchovaj:

- attempt number;
- first failure signature;
- artifacts každého pokusu;
- rovnaký commit a vstupy;
- environment zmeny medzi pokusmi;
- pass-after-retry status.

```text
pass on first attempt
≠ fail then pass
```

Pipeline a dashboard musia tieto výsledky rozlišovať. Inak celková pass rate maskuje flaky debt.

## 29. First-attempt pass rate

First-attempt pass rate meria podiel test executions, ktoré prešli bez retry. Je citlivejší na flakiness než finálny pipeline pass rate.

Sleduj aj:

- first-attempt failure rate per test;
- recovery-on-retry rate;
- repeated-failure rate;
- unique failure signatures;
- suite duration variability;
- environment a shard correlation;
- owner a age.

Test, ktorý vždy prejde na tretí pokus, nie je zelený test. Je to chronicky flaky kontrola.

## 30. Quarantine lifecycle

Quarantine dočasne odstráni test z blocking decisionu, aby jeden nestabilný signal nezastavil celý tím. Nesmie ho vypnúť ani skryť.

Povinné vlastnosti:

- test sa naďalej pravidelne spúšťa;
- failure zostáva viditeľný;
- existuje owner a issue;
- je uvedený dôvod a failure signature;
- quarantine má expiry a SLA;
- je definované náhradné krytie rizika;
- návrat do blocking suite vyžaduje stabilizačný dôkaz.

Quarantine bez expiry je trvalé odstránenie kontroly. Počet a vek quarantined tests musí byť quality metric.

## 31. Kedy quarantine nie je vhodná

Nequarantinuj test, ak pravdepodobne odhaľuje kritický production race alebo security failure a neexistuje náhradná kontrola. V takom prípade môže byť správne zastaviť release, znížiť concurrency alebo izolovať problematický component.

Quarantine je gate-management mechanizmus, nie root-cause fix.

## 32. Detekčné stratégie

Flakiness možno hľadať cielene:

- opakované runs rovnakého commitu;
- randomizované order;
- serial verzus parallel comparison;
- test samostatne verzus full suite;
- clean environment verzus reused environment;
- environment matrix;
- zvýšený alebo znížený CPU limit;
- network latency/failure injection;
- historical failure clustering;
- bisect suspect predecessorov;
- resource-leak loop.

Opakovanie má byť ohraničené a evidované. Tisíc zelených behov nezaručuje nulovú flakiness, ale pomáha odhadnúť pravdepodobnosť.

## 33. Failure artifacts

Artifact musí existovať z prvého failure, pretože rerun môže stav zmeniť alebo cleanup odstrániť.

Zachovaj podľa vrstvy:

- stdout a stderr;
- structured logs;
- timestamps a timeline;
- test seed a order seed;
- screenshot, video alebo browser trace;
- network trace;
- process a container logs;
- resource metrics;
- environment/tool versions;
- fixture provenance;
- resource IDs;
- JUnit alebo structured report;
- pending tasks a last observed state.

Artifacts musia byť redacted a dostupné ownerovi bez prístupu k secrets.

## 34. Root-cause workflow

Pri podozrení na flaky test:

1. zachovaj prvý failure a candidate revision;
2. klasifikuj assertion, setup, cleanup, environment alebo orchestration failure;
3. reprodukuj s rovnakým fixture, seed a order;
4. spusti test samostatne a vo full suite;
5. porovnaj serial a parallel run;
6. skontroluj shared state a resource ownership;
7. nahraď fixed sleeps condition-based waits;
8. koreluj timeout s environment saturation;
9. over, či failure nie je reálny product race;
10. oprav príčinu a vykonaj stabilizačný repeated run;
11. pridaj trvalý regression dôkaz;
12. odstráň quarantine až po splnení exit criteria.

## 35. Exit criteria po oprave

„Jeden zelený rerun“ nie je dôkaz opravy. Exit criteria môžu zahŕňať:

- reprodukčný test pred fixom konzistentne zlyhal;
- root cause je zdokumentovaný;
- fix odstraňuje nekontrolovaný vstup alebo product race;
- test prejde opakovane v serial aj parallel režime;
- prejde random-order suite;
- nevznikne nový cleanup alebo duration problém;
- first-attempt pass rate sa počas observation window obnoví;
- quarantine a temporary retry policy sa odstránia.

## 36. Flakiness metrics

Sleduj:

- first-attempt pass rate;
- pass-after-retry rate;
- flaky tests podľa ownera a vrstvy;
- failure signature distribution;
- quarantine count a age;
- mean time to repair;
- suite duration variance;
- cleanup failure rate;
- orphan resources;
- environment saturation incidents;
- percento failures bez diagnostických artifacts.

Metrika má viesť k oprave. Rebríček tímov podľa flaky count môže podporiť skrývanie alebo vypínanie testov namiesto zlepšenia systému.

## 37. Časté omyly

### „Stačí rerun“

Rerun mení evidence. Môže maskovať reálny intermittent defect aj chybný test.

### „Test je flaky iba v CI“

CI môže odhaľovať skutočný race, resource pressure alebo isolation problém, ktorý lokálny serial run nevytvorí.

### „Zvýšime sleep alebo timeout“

Tým sa zmení pravdepodobnosť failure, nie jeho mechanizmus.

### „Quarantine problém vyriešila“

Zmenila blocking policy. Riziko a flaky debt ostali.

### „Production dump je najrealistickejšia fixture“

Môže porušiť privacy a stále nereprezentovať potrebné edge cases alebo distributions.

### „Cleanup failure nevadí, test už skončil“

Orphan state ovplyvní ďalšie runy, bezpečnosť a náklady.

### „Final pipeline pass rate je dostatočná metrika“

Maskuje first-attempt failures a rerun-until-green kultúru.

## 38. Prevádzkový checklist

- Je verdict viazaný na presný commit, artifact a fixture version?
- Ukladá sa first failure pred rerunom?
- Rozlišuje pipeline assertion, setup, cleanup a infrastructure failure?
- Používajú async tests condition-based waits s deadline?
- Je clock, timezone a random seed kontrolovaný?
- Spúšťa sa suite aj v random order a paralelne?
- Vlastní každý test unikátne resources?
- Korelujú sa timeouty s CPU, memory, I/O a dependency saturation?
- Majú fixtures a generators provenance?
- Sú production-derived data výnimočné, schválené a minimalizované?
- Je cleanup idempotentný a chránený TTL/garbage collectorom?
- Má quarantine ownera, expiry, náhradnú kontrolu a exit criteria?
- Meria sa first-attempt pass rate a quarantine age?

## 39. Kontrolné otázky

1. Čo presne znamená flaky test a aké vstupy musia byť „rovnaké“?
2. Ako rozlíšiš chybný test od intermittent product defectu?
3. Prečo fixed sleep nevytvára správny wait contract?
4. Ako sa testuje eventual consistency bez neobmedzeného retry?
5. Ako odhalíš order dependency?
6. Ktoré resources treba izolovať pri paralelnom behu?
7. Ako environment saturation vytvára zdanlivú flakiness?
8. Aký je rozdiel medzi fixture, factory, golden file a synthetic datasetom?
9. Prečo fixture potrebuje provenance?
10. Kedy transaction rollback nestačí?
11. Ako má retry ovplyvniť finálny test status a metriky?
12. Aké povinné prvky má quarantine lifecycle?
13. Aký dôkaz je potrebný pred odstránením quarantine?
14. Prečo private test environment neospravedlňuje production data dump?

## Glossary impact

Relevantné pojmy: flaky test, nondeterminism, intermittent defect, hidden input, first-attempt pass rate, pass-after-retry, rerun-until-green, quarantine, condition-based wait, eventual consistency, order dependence, environment saturation, test fixture, test data factory, golden file, synthetic data, production-derived data, fixture provenance, test isolation, idempotent setup, cleanup a random seed.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Mocks, stubs a fakes](mocks-stubs-fakes.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Shift-left →](shift-left.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
