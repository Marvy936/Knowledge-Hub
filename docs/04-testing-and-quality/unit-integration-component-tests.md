# Unit, integration a component tests

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Testing and Software Quality
- Predpoklady: [Test pyramid](test-pyramid.md), [Python for automation](../03-git-and-automation/python-for-automation.md)
- Súvisiace témy: test seams, fixtures, hermetic tests, test doubles, ephemeral dependencies, mutation testing

## 1. Definícia podľa reálnych hraníc

Unit, integration a component tests sa nelíšia frameworkom ani názvom adresára. Líšia sa tým, aký behavior je predmetom testu, ktoré boundaries sú vykonané reálne a ktoré vstupy alebo dependencies sú pod priamou kontrolou testu.

```text
unit test        → izolovaná jednotka správania
integration test → reálna technická alebo procesná boundary
component test   → celý komponent cez jeho verejné rozhranie
```

Názov testu má opisovať skutočný execution model. Test označený ako „unit“, ktorý komunikuje cez sieť so shared databázou, má integračný failure model bez ohľadu na jeho package alebo annotation.

## 2. Mentálny model: subject, boundary, dependency a oracle

Pred návrhom testu pomenuj štyri prvky:

```text
subject under test
  ↓ používa
dependencies a boundaries
  ↓ vytvárajú
pozorovateľné výsledky a side effects
  ↓ hodnotí
oracle
```

Scope sa určuje podľa toho, čo je vo vnútri testovaného systému a čo už test považuje za externú boundary. Rovnaká application service môže byť predmetom unit testu s fake repository, integration testu s PostgreSQL a component testu cez spustený HTTP endpoint.

## 3. Unit test

Unit test overuje malú, zmysluplnú jednotku správania bez nekontrolovaných externých dependencies. Jednotkou môže byť funkcia, class, modul, domain aggregate, parser, policy engine alebo koordinovaná skupina objektov v pamäti.

Dobrý unit test:

- má malý failure scope — pri zlyhaní je možné rýchlo určiť porušené pravidlo;
- používa deterministické vstupy — clock, random, identity a externé odpovede sú kontrolované;
- overuje behavior alebo invariant — nie náhodné interné kroky implementácie;
- beží rýchlo — podporuje lokálny feedback a široké edge-case pokrytie;
- nepotrebuje sieť, shared filesystem ani persistentnú externú službu.

Unit test nie je definovaný jedným method callom. Doménová operácia môže spolupracovať s viacerými reálnymi in-memory objektmi a stále zostať jednotkou správania.

## 4. Príklad unit testu

Predstavme si výpočet finálnej ceny:

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Line:
    price: Decimal
    quantity: int


def calculate_total(lines: list[Line], discount: Decimal) -> Decimal:
    subtotal = sum((line.price * line.quantity for line in lines), Decimal("0"))
    return max(Decimal("0"), subtotal - discount)
```

Relevantné unit scenáre zahŕňajú nulový košík, záporný alebo príliš vysoký discount podľa contractu, rounding policy, viac quantities a invariant, že výsledok nikdy neklesne pod nulu. Test nepotrebuje databázu ani HTTP server, pretože riziko leží v lokálnej doménovej logike.

## 5. Solitary a sociable unit tests

Solitary unit test izoluje subject od väčšiny spolupracovníkov pomocou doubles. Je užitočný, keď treba presne simulovať chybu, timeout alebo zriedkavú odpoveď a keď interakcia sama tvorí významný contract.

Rizikom solitary prístupu je over-specification. Ak test očakáva presné poradie interných method calls bez behavior významu, bezpečný refaktoring ho rozbije a mock môže reprezentovať rozhranie inak než reálna implementácia.

Sociable unit test používa reálne objekty v rámci jednej doménovej boundary a izoluje iba externé systémy. Často lepšie overuje behavior, znižuje počet interaction assertions a podporuje refaktoring, ale pri zlyhaní má mierne širší scope.

Ani jeden prístup nie je univerzálne správny. Výber závisí od architektúry, stability contractu a typu failure, ktorý má test zachytiť.

## 6. Test seam

Test seam je miesto, kde možno správanie alebo dependency nahradiť bez zmeny production intentu. Môže to byť interface, function parameter, factory, dependency-injection registration, clock abstraction, transport adapter alebo filesystem wrapper.

Dobrá seam:

- zodpovedá skutočnej architektonickej boundary;
- umožňuje kontrolovať nedeterministický alebo drahý vstup;
- neslúži iba na sprístupnenie private implementation detailu;
- má contract, ktorý možno overiť aj proti reálnej implementácii;
- neumožňuje testu obísť dôležitú production logiku.

Príliš veľa umelých interfaces vytvorených iba kvôli mockovaniu zvyšuje komplexitu. Seam má vzniknúť tam, kde systém už prirodzene komunikuje s vonkajším svetom alebo s nestabilnou dependency.

## 7. Integration test

Integration test vykonáva reálnu spoluprácu cez aspoň jednu technickú alebo procesnú boundary. Môže ísť o aplikáciu a databázu, client a HTTP server, producer a message broker, controller a API server alebo kód a filesystem s reálnymi permissions.

Jeho účelom je overiť semantics, ktoré test double nemusí reprezentovať:

- serializáciu, framing a protocol errors;
- SQL dialect, constraints, transactions a isolation;
- authentication, TLS a connection configuration;
- queue ordering, acknowledgements a redelivery;
- filesystem permissions, symlinks a atomic rename;
- provider API defaults, quotas a eventual consistency.

Integration test má reálnu boundary, ale nemusí spúšťať celý produkt. Má zostať čo najmenší, aby failure lokalizoval konkrétnu integráciu.

## 8. Component test

Component test spúšťa celý deployable alebo logický komponent cez jeho verejné rozhranie. Vnútorné vrstvy, middleware, routing, serialization, persistence a observability môžu byť reálne, zatiaľ čo externé podnikové služby sú nahradené kontrolovanými doubles.

```text
HTTP request
→ reálny application process
→ routing a middleware
→ domain logic
→ test database
→ fake externý provider
```

Component test overuje behavior komponentu ako čiernej alebo sivej skrinky. Poskytuje vyššiu fidelity než izolovaný unit test a lepšiu diagnostiku než multi-service E2E test, pretože externý svet zostáva kontrolovaný.

## 9. Component test verzus E2E

Component test má jasnú ownership boundary: zodpovednosť jedného komponentu a jeho public contract. E2E test prechádza cez viac autonómnych komponentov a overuje širšiu používateľskú alebo deployment cestu.

Ak component test potrebuje celý podnikový stack, produkčné identity a shared prostredie, prakticky sa zmenil na E2E test. To prináša vyššiu cenu, širší failure scope a závislosť od tímov, ktoré komponent nevlastnia.

## 10. In-process a out-of-process execution

In-process test načíta framework a application code do test runner procesu. Je rýchlejší, umožňuje priame assertions a často jednoduchšie dependency overrides.

Jeho blind spots môžu zahŕňať:

- packaging a missing runtime dependencies;
- process startup a environment parsing;
- socket, TLS a real HTTP framing;
- signal handling a graceful shutdown;
- rozdiely thread alebo event-loop lifecycle.

Out-of-process test spustí reálny executable alebo kontajner a komunikuje cez verejný protokol. Overuje packaging, startup, network boundary a process lifecycle, ale potrebuje readiness detection, log collection a spoľahlivý cleanup.

Obe formy sú užitočné. In-process test je vhodný pre rýchlu behavior kontrolu; out-of-process test pridáva dôkaz o runtime artifacte a deployment-like správaní.

## 11. Reálna dependency alebo test double

Dependency má byť reálna, keď jej semantics tvoria predmet rizika. Má byť nahradená, keď je mimo scope, drahá, nebezpečná alebo nedeterministická a test potrebuje kontrolovať konkrétne odpovede.

Použi reálnu dependency, keď testuješ:

- SQL query a transaction behavior;
- message acknowledgement alebo ordering;
- serializer kompatibilitu;
- TLS, authentication alebo protocol negotiation;
- filesystem permission a atomicity;
- runtime framework wiring.

Použi double, keď testuješ:

- lokálnu reakciu na timeout alebo malformed response;
- zriedkavé externé failure, ktoré nemožno bezpečne vyvolať;
- business logiku nezávislú od konkrétnej implementácie;
- rate-limited alebo platenú externú službu;
- destructive provider operation.

Kritické doubles potrebujú contract tests alebo porovnanie s reálnou službou, aby sa znižoval contract drift.

## 12. Typy test doubles

- dummy — vyplní povinný parameter, ale test jeho správanie nepoužíva;
- stub — vracia vopred definované odpovede pre konkrétne vstupy;
- fake — poskytuje funkčnú, zjednodušenú implementáciu, napríklad in-memory repository;
- spy — zaznamenáva uskutočnené interakcie na neskoršie assertions;
- mock — má vopred definované očakávania interakcií a failure pri ich porušení;
- simulator alebo emulator — napodobňuje širší protokol alebo platformu.

Názvy sa medzi frameworkmi líšia, ale rozhodujúce je správanie double. In-memory fake databáza neoverí PostgreSQL constraints iba preto, že implementuje rovnaké repository interface.

## 13. Database integration tests

Databáza nie je iba key-value úložisko. Reálne semantics zahŕňajú schema, constraints, indexes, transactions, isolation levels, locking, collation, timezone, query planner a connection pool.

Testuj najmä:

- migrácie z podporovaných predchádzajúcich verzií schémy;
- uniqueness, foreign keys, check constraints a null semantics;
- transaction commit, rollback a concurrent update;
- správne query results pri reprezentatívnych edge cases;
- encoding, collation a case sensitivity;
- connection pool exhaustion a timeout;
- behavior pri deadlocku alebo serialization failure;
- idempotenciu migration a seed mechanizmov.

Preferuj rovnaký engine a kompatibilnú major verziu ako produkcia. SQLite alebo in-memory fake môže byť vhodný pre lokálnu logiku, ale nie ako dôkaz PostgreSQL, MySQL alebo SQL Server semantics.

## 14. Izolácia databázových dát

Možnosti izolácie:

- transaction rollback — rýchly, ale nemusí pokryť code, ktorý používa viac connections alebo commits;
- schema per test alebo worker — poskytuje namespace isolation, ale potrebuje spoľahlivý cleanup;
- unique tenant alebo identifier — vhodný pri shared schéme, ak všetky queries rešpektujú namespace;
- disposable database/container — poskytuje silnú izoláciu za cenu startupu;
- snapshot/template restore — zrýchľuje veľké reprezentatívne datasety.

Isolation strategy musí zodpovedať testovanému behavioru. Ak testuješ transaction commit alebo asynchronous consumer, rollback obal v test runneri môže vytvoriť nereálny execution model.

## 15. Message broker integration tests

Broker tests majú overovať viac než publish bez exception. Relevantné semantics zahŕňajú:

- topic alebo queue provisioning;
- serialization a schema compatibility;
- partitioning a ordering;
- acknowledgement a redelivery;
- duplicate delivery a consumer idempotency;
- visibility timeout alebo lease;
- dead-letter routing;
- retention a offset behavior;
- consumer restart a rebalance.

Test musí čakať na podmienku s deadline, nie pevný `sleep`. Asynchronous systém potrebuje correlation ID a diagnostické artifacts, aby sa dalo zistiť, či message nebola publikovaná, spracovaná alebo iba ešte nepozorovaná.

## 16. HTTP a API integration tests

HTTP client alebo server integration test má používať reálne request parsing, headers, serialization a status semantics. Nemusí komunikovať cez internet; lokálny test server môže poskytnúť deterministickú protocol boundary.

Overuj:

- request target, method, headers a body encoding;
- status, response schema a content type;
- timeout, cancellation a connection reuse;
- authentication a authorization failures;
- malformed alebo partial response;
- retry iba pre bezpečné operations;
- idempotency key a duplicate request behavior;
- propagation correlation a trace metadata.

Pri component teste cez reálny socket sa navyše overí process startup, port binding a middleware order.

## 17. Filesystem integration tests

Filesystem behavior závisí od platformy, permissions a mount semantics. Test s temporary directory overuje skutočné path, file creation a atomic replace behavior bez používania shared produkčného adresára.

Relevantné scenáre:

- path s whitespace, Unicode alebo dlhým názvom;
- permission denied a read-only filesystem;
- symlink a path traversal;
- partial write a cleanup temp file;
- rename v rámci jedného verzus medzi filesystems;
- concurrent writer a lock behavior;
- file mode a line-ending policy.

Test má používať explicitný encoding a nesmie predpokladať, že Linux, Windows a network filesystem majú identické semantics.

## 18. Cloud a provider integration tests

Cloud API alebo Infrastructure as Code integration test môže používať sandbox account, local emulator alebo provider test harness. Každá možnosť má iný fidelity a bezpečnostný profil.

Sandbox test potrebuje:

- izolovaný account, project alebo subscription;
- least-privilege test identity;
- namespacing resources a tags pre garbage collection;
- cost a quota limits;
- cleanup odolný voči partial failure;
- audit logs a explicitný region;
- zákaz prístupu k produkčným dátam.

Emulator je rýchlejší, ale nemusí reprezentovať IAM, quotas, eventual consistency alebo managed-service defaults. Kritické assumptions preto potrebujú aspoň periodický test proti reálnemu provider API.

## 19. Containerized dependencies

Ephemeral containers umožňujú spustiť reálnu dependency v známej verzii lokálne aj v CI. Zlepšujú reprodukovateľnosť, ale samy osebe nezaručujú hermeticity.

Riziká:

- image tag drift alebo neoverený digest;
- image pull latency a registry outage;
- port collision pri paralelnom behu;
- proces beží, ale služba ešte nie je ready;
- uniknuté containers, volumes alebo networks;
- odlišnosť od managed cloud variantu;
- nedostatok runner CPU alebo memory.

Readiness musí používať funkčný probe s deadline. Otvorený TCP port nemusí znamenať, že migrácie alebo leader election sú dokončené.

## 20. Hermetic test

Hermetic test kontroluje všetky významné vstupy a nespolieha sa na nepredvídateľný externý stav. Hermetic neznamená bez reálnych dependencies; disposable PostgreSQL s pinned image a vlastnými dátami môže byť súčasťou hermetického environmentu.

Kontrolované vstupy zahŕňajú:

- dependency versions a artifact digest;
- clock, timezone a locale;
- random seed a ID generator;
- environment variables a config;
- network access a DNS;
- filesystem a permissions;
- test data a starting schema;
- CPU/memory limity, ak ovplyvňujú behavior.

Test, ktorý nevedome používa developerovu lokálnu databázu alebo internetový endpoint, nie je hermetický a jeho výsledok má slabú reprodukovateľnosť.

## 21. Clock, random a identity

Priamy prístup na wall clock vytvára hranice okolo polnoci, DST, expiry a timezone. Global random source alebo UUID generátor komplikuje reprodukciu failure a assertions.

Používaj explicitné seams:

```text
Clock
RandomSource
IdGenerator
Scheduler alebo Sleeper
```

Test môže dodať fixed clock, seeded random a deterministické identifiers. Production implementácia stále používa reálne systémové zdroje, ale doménová logika ich nečíta skryto.

## 22. Fixtures a test builders

Fixture je počiatočný stav potrebný pre test. Má byť minimálna, čitateľná a vlastnená konkrétnym testom alebo jasne definovanou skupinou testov.

Dobré patterns:

- object builder s rozumnými defaults a explicitnými relevantnými overrides;
- factory, ktorá vytvorí unikátne namespaced dáta;
- migration a seed z rovnakého artifactu ako produkcia;
- fixture version viazaná na schema alebo API contract;
- helper, ktorý vracia vytvorené IDs pre cleanup a assertions.

Gigantická shared fixture skrýva, ktoré dáta test reálne potrebuje. Zmena jedného defaultu môže rozbiť desiatky nesúvisiacich testov a vytvoriť order dependency.

## 23. Setup, readiness a teardown lifecycle

Test lifecycle:

```text
allocate namespace/resources
→ provision dependency
→ wait for readiness with deadline
→ seed minimal data
→ execute behavior
→ collect assertions a artifacts
→ cleanup aj pri failure
→ verify cleanup alebo schedule garbage collection
```

Setup má zlyhať s jasným dôvodom, ak dependency nie je ready. Teardown musí byť idempotentný a odolný voči stavu, keď setup skončil iba čiastočne.

Cleanup error nesmie potichu prepísať pôvodný test failure. Obe chyby treba zaznamenať, pričom primárny behavior failure zostáva zachovaný.

## 24. Condition-based waiting

Fixed `sleep` predpokladá, že systém bude hotový v arbitrárnom čase. Na rýchlom runneri zbytočne spomaľuje suite a na pomalom runneri stále zlyhá.

Lepší model:

```text
opakuj diskriminačný probe
s krátkym intervalom a jitterom
kým podmienka neplatí
alebo nevyprší celkový deadline
```

Failure má uviesť posledný pozorovaný stav, elapsed time a relevantné logs. Polling bez deadline môže zablokovať celý pipeline worker.

## 25. Paralelizácia a isolation

Paralelný beh zrýchľuje suite iba vtedy, keď testy nezdieľajú mutable state. Konflikty vznikajú cez fixed ports, filenames, global config, shared users, queues, tenants a rate limits.

Bezpečné patterns:

- OS-assigned alebo dynamicky alokované ports;
- unique namespace per test alebo worker;
- database/schema per worker;
- correlation IDs a unique resource names;
- immutable fixtures;
- bounded concurrency podľa kapacity dependency;
- cleanup scoped na vlastný namespace, nie globálny delete.

Paralelný test, ktorý potrebuje global lock, môže byť legitímny, ale jeho bottleneck má byť explicitný a meraný.

## 26. Negative a failure paths

Failure handling je produkčné správanie. Testuj nielen úspech, ale aj:

- timeout a cancellation;
- dependency unavailable alebo slow;
- malformed, partial alebo semanticky chybnú odpoveď;
- duplicate message alebo request;
- permission denied a expired credential;
- rate limit a retry exhaustion;
- stale version a optimistic-concurrency conflict;
- partial write a compensation;
- process termination počas operation;
- pool, queue alebo disk saturation.

Double je často vhodný na presné vyvolanie failure. Aspoň kritické failure assumptions však majú byť overené aj na reálnej boundary, napríklad skutočný SQL deadlock alebo connection timeout.

## 27. Assertions podľa scope

Unit test typicky overuje hodnoty, domain errors, state transition a invariant. Nemá kontrolovať databázové details, ktoré nie sú v jeho scope.

Integration test overuje persisted state, constraints, protocol response, transaction effects, retry behavior a cleanup reálnej boundary. Má zachytiť differences, ktoré fake nevidí.

Component test overuje public API behavior, middleware, authorization, emitted events, side effects a observability metadata. Interné method call counts nie sú contract, pokiaľ nepredstavujú významný external effect.

## 28. Failure artifacts a observability

Test má pri failure uchovať dôkaz potrebný na lokalizáciu:

- seed a correlation ID;
- request/response metadata s redaction;
- logs relevantných procesov;
- container alebo service status;
- DB query/error a schema version;
- broker offsets alebo message IDs;
- screenshots, DOM alebo trace pre UI/component tests;
- časový priebeh setup, execute a teardown;
- artifact a dependency versions.

Artifact musí byť naviazaný na konkrétny test attempt. Zdieľaný log bez timestampu a correlation ID má nízku diagnostickú hodnotu.

## 29. Mutation testing

Mutation testing zámerne vytvorí malé chyby v produkčnom kóde, napríklad obráti comparison, odstráni condition alebo zmení návratovú hodnotu. Ak test suite zostane zelená, mutácia prežila a odhaľuje slabý oracle alebo chýbajúci scenár.

Mutation score nie je cieľ sám osebe. Používa sa cielene pre kritickú doménovú logiku, authorization, financial calculations alebo parsers, kde line coverage môže byť vysoké bez citlivosti na chybu.

## 30. Výber správneho scope

Rozhodovací postup:

1. pomenuj behavior a failure mode;
2. urč boundary, v ktorej failure vzniká;
3. zvoľ najnižší scope, ktorý boundary vykoná reálne;
4. rozhodni, ktoré ostatné dependencies môžu byť doubles;
5. definuj oracle a side effects;
6. navrhni data isolation a parallelism;
7. urč readiness, deadline a cancellation;
8. definuj cleanup pri partial failure;
9. urč failure artifacts a ownera;
10. doplň vyšší scope iba ak pridáva novú fidelity.

## 31. Diagnostika zlyhania

Najprv rozlíš:

```text
behavior failure
boundary/dependency failure
fixture alebo setup failure
environment capacity failure
test implementation failure
cleanup failure
```

Postup:

1. over, či subject dostal očakávané vstupy;
2. skontroluj dependency version, readiness a config;
3. nájdi correlation ID v logs a traces;
4. over reálny persisted alebo emitted state;
5. porovnaj first attempt s rerunom bez zmeny;
6. reprodukuj najmenší scope s rovnakou boundary;
7. zachovaj artifacts pred cleanupom, ak to bezpečnostná policy povoľuje;
8. oprav produkt, test seam, fixture alebo environment podľa dôkazu.

## 32. Anti-patterny

### Unit test cez reálnu sieť

Test lokálnej logiky získava latency a externú variabilitu bez pridanej hodnoty. Sieťová boundary patrí do integration testu.

### Integration test s úplne mockovanou boundary

Test používa názov integration, ale reálny serializer, DB alebo protocol nikdy nevykoná. Poskytuje iba ďalší unit-level dôkaz.

### In-memory databáza ako univerzálna náhrada

Fake môže urýchliť doménové testy, ale nepreukazuje constraints, transactions, collation ani query planner produkčného engine.

### Component test závislý od celého stacku

Scope sa rozšíril na E2E, failure má veľa ownerov a lokálna reprodukcia je náročná. Externé systémy majú byť kontrolované cez stabilné fakes alebo simulators.

### Cleanup iba po úspechu

Failure zanechá dáta a resources, ktoré ovplyvnia ďalšie testy. Teardown musí bežať v `finally`-like lifecycle a byť idempotentný.

### Fixed sleep

Test predpokladá timing namiesto pozorovania readiness alebo výslednej podmienky. To vytvára pomalé aj flaky správanie.

## 33. Kontrolný checklist

- scope je definovaný reálnymi a nahradenými boundaries;
- test overuje behavior a relevantný oracle;
- reálne dependencies sú pinned a pripravené funkčným probe-om;
- test data sú minimálne, namespaced a reprodukovateľné;
- clock, random a identity sú kontrolované tam, kde ovplyvňujú výsledok;
- parallel runs nemajú shared mutable state;
- waits používajú deadline a condition-based polling;
- cleanup funguje aj po partial setup alebo interrupted behu;
- failure artifacts majú correlation a verzie;
- doubles majú contract ochranu proti driftu;
- vyšší scope pridáva novú fidelity, nie iba duplicitný assertion.

## 34. Časté omyly

### „Unit test musí testovať jednu metódu“

Nie. Testuje izolovanú jednotku správania, ktorá môže obsahovať viac spolupracujúcich objektov.

### „Integration test znamená dve microservices“

Nie. Jedna aplikácia proti reálnej databáze, brokeru alebo filesystemu je integration test.

### „Hermetic test nepoužíva reálne dependencies“

Nie. Reálna dependency môže byť hermetická, ak je jej verzia, stav, config a lifecycle plne kontrolovaný testom.

### „Component test je menší E2E test“

Je definovaný ownership boundary jedného komponentu a kontrolovanými externými systémami. E2E prechádza cez viac autonómnych komponentov.

### „Mock zaručuje správnosť integrácie“

Mock overuje očakávania testu. Bez contract alebo real-boundary testu môže iba potvrdiť nesprávny model externého systému.

## 35. Kontrolné otázky

1. Čo určuje scope unit, integration a component testu?
2. Aký je rozdiel medzi solitary a sociable unit testom?
3. Čo je test seam a kedy je vhodná?
4. Kedy má byť dependency reálna a kedy nahradená double?
5. Ako sa component test líši od E2E testu?
6. Aký je rozdiel medzi in-process a out-of-process testom?
7. Prečo in-memory DB nie je dôkazom production SQL semantics?
8. Ako izoluješ databázové a broker test data?
9. Čo znamená hermetic test?
10. Prečo fixed `sleep` vytvára flaky test?
11. Aké artifacts potrebuje integration failure?
12. Načo slúži mutation testing?

## 36. Zhrnutie

Unit test poskytuje rýchly a lokalizovaný dôkaz izolovaného správania. Integration test vykonáva reálnu technickú boundary a component test overuje celý komponent cez jeho verejný contract pri kontrolovanom externom svete.

Dôveryhodnosť nevzniká z názvu testu. Vzniká z presnej definície scope, správneho výberu reálnych dependencies, deterministického lifecycle, silného oraclu, izolovaných dát a diagnostických artifacts.

## Glossary impact

Relevantné pojmy: unit test, integration test, component test, test seam, solitary test, sociable test, test double, dummy, stub, fake, spy, mock, simulator, hermetic test, fixture, readiness, condition-based waiting a mutation testing.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Test pyramid](test-pyramid.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Contract a API tests →](contract-and-api-tests.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
