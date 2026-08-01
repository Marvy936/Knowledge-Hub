# Unit, integration a component tests

Rozdiel medzi unit, integration a component testom neurčuje názov frameworku ani to, či test beží „lokálne“. Určuje ho subject, boundary a ktoré dependencies sú reálne alebo nahradené.

**Unit test** overuje malú jednotku správania v izolovanom a kontrolovanom prostredí. Unit môže byť funkcia, class alebo coherent modul. Dôležité je, že test rýchlo a deterministicky lokalizuje logic failure a nepoužíva drahé externé boundaries.

**Integration test** overuje spoluprácu medzi dvoma alebo viacerými reálnymi komponentmi alebo technológiami. Môže testovať SQL mapping voči databáze, serialization library, filesystem semantics alebo message broker clienta. Jeho hodnota je práve v reálnom contracte medzi boundaries.

**Component test** spúšťa celý deployable component cez jeho verejné rozhranie, ale kontroluje alebo nahrádza okolité externé systémy. Overuje routing, dependency injection, serialization, business flow a error mapping v rámci jedného componentu.

Neutrálny príklad:

```text
unit:
CalculateDiscount(order)

integration:
OrderRepository ↔ PostgreSQL

component:
HTTP POST /orders cez celú službu,
platobná brána nahradená fake serverom
```

Test double nie je automaticky známkou unit testu. Component test môže používať fake payment provider, zatiaľ čo unit test môže omylom spúšťať reálny filesystem. Scope treba popísať mechanicky.

Hermetic test má explicitné inputs, izolovaný state a kontrolované dependencies. Parallelizability vyžaduje unikátne test data, ports, files alebo database schemas. Cleanup musí fungovať aj pri failure; ešte lepšie je vytvárať disposable environment.

Nižší scope zvyšuje diagnostickosť, ale môže skryť boundary bugs. Vyšší scope zvyšuje fidelity, ale failure má viac možných príčin. Dobré portfolio používa oba a nevytvára component test pre logic, ktorú možno presnejšie overiť unit testom.

## 1. Cieľ kapitoly

Unit, integration a component tests sa nelíšia frameworkom ani názvom adresára. Líšia sa tým, **ktoré hranice systému test vykonáva reálne** a aký failure mode tým dokáže zachytiť.

Nosný model kapitoly je:

```text
behavior alebo riziko
→ subject under test
→ reálne a nahradené boundaries
→ setup a kontrolované vstupy
→ pozorovaný výsledok a side effects
→ oracle
→ dôkaz s explicitnými blind spots
```

Pravidlo výberu scope-u:

```text
Použi najnižší test scope,
ktorý ešte vykoná hranicu,
v ktorej môže relevantná chyba vzniknúť.
```

Unit test nemá simulovať celý svet. Integration test nemá spúšťať celý podnikový stack. Component test nemá byť iba drahší unit test cez HTTP.

## 2. Nosný scenár: Atlas Orders

Atlas prevádzkuje službu `orders-api`. Verejná operácia vytvorenia objednávky má tok:

```text
POST /orders
→ authentication a tenant authorization
→ validácia commandu
→ výpočet ceny a order state transition
→ transakčný zápis do PostgreSQL
→ outbox záznam OrderCreated
→ asynchronous publish do brokeru
→ HTTP 201 s order ID
```

Externá platobná služba sa pri vytvorení objednávky ešte nevolá. Neskorší worker spracuje `OrderCreated`, zavolá Payments API a vytvorí ďalší state transition.

Tím potrebuje dôkaz pre tri odlišné riziká:

1. Doménová logika môže vypočítať nesprávnu cenu alebo povoliť neplatný stav.
2. Repository a outbox môžu používať PostgreSQL inak, než predpokladá in-memory fake.
3. Reálny `orders-api` artifact môže mať chybný routing, middleware, config, serialization alebo idempotency wiring.

Tieto riziká patria do troch rôznych scopes.

## 3. Jedna operácia, tri scopes

### Unit scope

```text
CreateOrder use case
+ reálne doménové objekty
+ fake repository/outbox port
+ fixed clock a ID generator
```

Overuje doménové rozhodnutie bez siete, procesu a databázy.

### Integration scope

```text
PostgreSQL repository a outbox adapter
+ skutočný PostgreSQL engine
+ reálna schema a transaction semantics
```

Overuje technickú boundary, ktorú fake nevie vierohodne reprezentovať.

### Component scope

```text
HTTP request
→ reálny orders-api proces
→ routing, middleware, serialization a domain logic
→ reálny PostgreSQL
→ kontrolovaný fake broker alebo Payments API
```

Overuje komponent cez jeho verejné rozhranie a reálny runtime artifact, ale externý podnikový svet zostáva pod kontrolou testu.

Scope teda neurčuje počet metód ani procesov. Určuje ho mapa reálnych boundaries.

## 4. Subject, boundary, dependency a oracle

Pred napísaním testu pomenuj štyri veci:

```text
subject
→ ktoré dependencies používa
→ ktoré výsledky a side effects vytvára
→ čo oracle považuje za úspech
```

Pre Atlas:

- subject unit testu: `CreateOrder` use case;
- subject integration testu: PostgreSQL repository a outbox transaction;
- subject component testu: nasadený `orders-api` komponent;
- oracle unit testu: doménový result a invarianty;
- oracle integration testu: persisted rows, constraints a transaction outcome;
- oracle component testu: HTTP contract, persisted state, outbox side effect a audit/correlation metadata.

HTTP `201`, nulový exception alebo úspešný SQL command sú iba čiastkové pozorovania. Oracle musí overiť význam výsledku.

## 5. Unit test: izolované správanie

Unit test je vhodný, keď failure vzniká v lokálnej logike a reálna infraštruktúra nepridáva nový dôkaz.

Príklad doménových typov:

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Line:
    sku: str
    unit_price: Decimal
    quantity: int

@dataclass(frozen=True)
class CreateOrder:
    tenant_id: str
    customer_id: str
    lines: tuple[Line, ...]
    idempotency_key: str
```

Doménový use case má overovať napríklad:

- objednávka musí obsahovať aspoň jednu položku;
- quantity musí byť kladné číslo;
- price sa počíta cez `Decimal`, nie binary float;
- total nesmie byť záporný;
- tenant identity sa prenesie do order state-u;
- rovnaký command identity nevytvorí druhú doménovú operáciu podľa zvoleného contractu;
- zakázaný state transition vráti doménovú chybu bez side effectu.

Unit test môže použiť:

- fixed clock;
- deterministický ID generator;
- fake repository;
- spy nad outbox portom;
- stub policy alebo pricing dependency, ak je mimo testovaného scope-u.

Dôležité je, aby test overoval behavior:

```text
vstup a počiatočný stav
→ doménové rozhodnutie
→ nový stav alebo doménová chyba
→ presne definované side effects
```

Nie je potrebné kontrolovať každé interné volanie. Presné method-call poradie je contract iba vtedy, keď jeho zmena mení observable behavior alebo correctness.

## 6. Solitary a sociable unit test

Solitary test nahradí väčšinu collaborators doubles. Umožní presne vyvolať timeout, konflikt alebo zriedkavú odpoveď, ale môže zmraziť internú implementáciu.

Sociable test používa reálne doménové objekty v jednej boundary a nahradí iba externé I/O. Pre Atlas môže `CreateOrder` používať reálne pricing rules, order aggregate a policy objects, pričom repository a clock zostanú doubles.

Výber:

```text
Ak interakcia sama tvorí contract,
kontroluj ju cielene.

Ak je contractom výsledné správanie,
preferuj behavior assertions nad internými calls.
```

Fake alebo mock nie je dôkazom správnosti reálnej dependency. Je dôkazom, že subject reaguje správne na model dependency, ktorý vytvoril test.

## 7. Test seam ako architektonická hranica

Test seam je miesto, kde možno dependency kontrolovane nahradiť:

```text
Clock
IdGenerator
OrderRepository
Outbox
PaymentGateway
MessagePublisher
```

Dobrá seam:

- zodpovedá reálnej boundary systému;
- ukrýva I/O alebo nedeterministický zdroj;
- má malý, pomenovaný contract;
- umožňuje reálnu implementáciu aj test double;
- neobchádza production logiku.

Interface vytvorený iba preto, aby sa dala mockovať private metóda, je slabá seam. Zvyšuje počet abstractions bez zlepšenia architektúry alebo dôkaznej hodnoty.

## 8. Integration test: reálna boundary

Integration test má vykonať presne tú dependency semantics, ktorá predstavuje riziko.

Pre Atlas je prvá kritická boundary PostgreSQL:

```text
application adapter
→ driver a connection pool
→ PostgreSQL parser/planner
→ constraints a transaction manager
→ persisted state
```

Relevantné chyby:

- nesprávny SQL dialect alebo mapping;
- `NULL`, collation alebo timezone semantics;
- chýbajúci unique constraint;
- transaction commit a rollback;
- optimistic concurrency conflict;
- deadlock alebo serialization failure;
- migrácia nekompatibilná so staršou schémou;
- order row sa commitne, ale outbox row nie;
- pool exhaustion alebo timeout.

In-memory repository tieto mechanizmy nevykoná. Preto nemôže byť jediným dôkazom pre persistence correctness.

## 9. Worked integration failure: objednávka bez outbox eventu

Tím pôvodne testoval `CreateOrder` iba s fake repository. Test prešiel:

```text
save(order)
append_event(OrderCreated)
→ obidve fake operácie úspešné
```

Produkčný adapter však vykonal dve samostatné transakcie:

```text
T1: INSERT orders → COMMIT
T2: INSERT outbox → connection timeout → ROLLBACK
```

Dôsledok:

```text
objednávka existuje
ale event neexistuje
→ worker ju nikdy nespracuje
→ používateľ vidí pending objednávku bez platby
```

Správny integration test používa reálny PostgreSQL a vynúti failure medzi zápismi. Oracle overí:

1. order a outbox sa commitnú spolu;
2. alebo sa pri failure necommitne ani jeden;
3. retry nevytvorí duplicitnú objednávku;
4. constraint chráni identitu operácie aj pri concurrency.

Mechanizmus nápravy je jedna transakcia alebo iný explicitný atomicity/compensation model. Viac unit mock expectations by tento failure mode neodhalilo.

## 10. Databázový test lifecycle

Dôveryhodný integration test potrebuje kontrolovaný lifecycle:

```text
allocate schema alebo database namespace
→ aplikovať production migrations
→ čakať na funkčnú readiness
→ seed minimálnych dát
→ vykonať behavior
→ overiť persisted state a constraints
→ uchovať failure artifacts
→ idempotentný cleanup
```

Izolácia môže byť:

- database alebo schema per worker;
- unikátny tenant/operation ID;
- disposable container;
- snapshot/template restore;
- transaction rollback iba vtedy, keď nezmení testovaný execution model.

Ak production code používa viac connections, explicitné commity alebo asynchronous worker, test-runner transaction rollback môže vytvoriť nereálny svet.

## 11. Broker a asynchronous boundary

Pre outbox publisher alebo consumer je predmetom integration testu:

- serialization a schema;
- partition key a ordering;
- acknowledgement;
- redelivery;
- duplicate delivery a idempotency;
- visibility timeout alebo lease;
- dead-letter behavior;
- restart a recovery.

Asynchronous test nesmie používať pevný `sleep` ako oracle.

Správny model:

```text
publish alebo trigger
→ opakovať diskriminačný probe
→ sledovať correlation ID
→ skončiť pri očakávanej podmienke
alebo pri celkovom deadline
```

Failure output má ukázať posledný pozorovaný stav, elapsed time, message identity, offsets alebo queue metadata a relevantné logs.

## 12. Component test: celý komponent cez public boundary

Component test Atlasu spustí reálny `orders-api` artifact:

```text
container/image alebo executable
→ production startup path
→ environment/config parsing
→ HTTP socket
→ routing a middleware
→ authorization
→ serialization
→ domain logic
→ PostgreSQL
```

Externý broker alebo Payments API môže byť nahradený kontrolovaným fake serverom, pretože predmetom testu je vlastníctvo `orders-api`, nie dostupnosť celej organizácie.

Component test pridáva dôkaz, ktorý in-process unit a adapter testy nevidia:

- artifact obsahuje všetky runtime dependencies;
- proces sa spustí s reálnou konfiguráciou;
- route je správne registrovaná;
- middleware order je správny;
- request/response serialization zodpovedá public contractu;
- identity context sa prenesie do domény;
- graceful shutdown a readiness fungujú;
- observability metadata vzniknú na skutočnej request ceste.

## 13. In-process verzus out-of-process

In-process component test je rýchlejší a umožňuje jednoduché dependency overrides. Môže však obísť:

- packaging;
- process startup;
- reálny socket a HTTP framing;
- environment parsing;
- signal handling;
- chýbajúci runtime file alebo module.

Out-of-process test spustí skutočný artifact a komunikuje cez protokol. Je drahší, ale pre release evidence poskytuje silnejší dôkaz.

Rozumné portfólio môže mať:

```text
veľa rýchlych in-process component testov
+
malý počet out-of-process artifact smoke/component testov
```

## 14. Worked component failure: falošne bezpečný idempotency flow

Unit test potvrdil, že `CreateOrder` pri rovnakom idempotency key vráti existujúci order. PostgreSQL integration test potvrdil unique constraint.

Component test však odhalil chybu v middleware:

```text
request A bez tenant prefixu v cache key
request B z iného tenantu s rovnakým key
→ middleware vráti response objednávky tenantu A
```

Doména aj databáza boli lokálne správne. Failure vznikol na component boundary, kde sa skladali:

```text
identity middleware
+ idempotency cache
+ routing
+ response serialization
```

Správny component oracle overí:

- tenant A a tenant B môžu použiť rovnaký klientsky key bez cross-tenant collision;
- unauthorized response neprezradí order identity;
- vznikne presne jeden side effect v správnom tenante;
- audit event obsahuje tenant, operation ID a výsledok.

Tento príklad ukazuje, prečo vyšší scope má zmysel iba vtedy, keď pridáva reálnu boundary.

## 15. Reálna dependency alebo double

Dependency používaj reálne, keď jej semantics tvorí testované riziko:

- PostgreSQL constraints a transactions;
- broker acknowledgement a redelivery;
- filesystem permissions a atomic rename;
- TLS/authentication/protocol negotiation;
- production framework wiring.

Dependency nahraď, keď je mimo scope a test potrebuje kontrolu:

- platená alebo rate-limited externá služba;
- nebezpečná destructive operation;
- zriedkavý timeout alebo malformed response;
- third-party systém bez deterministic test tenant-a.

Kritický fake má mať ochranu proti driftu:

```text
fake behavior
↔ zdieľaný contract test
↔ periodický test proti reálnej dependency
```

## 16. Hermeticita nie je absencia reálnych služieb

Hermetic test kontroluje všetky významné vstupy. Disposable PostgreSQL môže byť súčasťou hermetického testu, ak sú kontrolované:

- image digest a version;
- schema a seed;
- config;
- clock, timezone a locale;
- network access;
- identity a permissions;
- resource limity;
- lifecycle a cleanup.

Ephemeral container nie je automaticky hermetický. Ak používa mutable image tag, shared DNS, internetový dependency endpoint alebo globálny cloud účet, nekontrolovaná boundary zostáva.

## 17. Setup, readiness, execute, evidence, cleanup

Každý integration alebo component test má byť čitateľný ako transakcia dôkazu:

```text
allocate izolovaný namespace
→ provision pinned dependencies
→ funkčná readiness s deadline
→ seed minimálnych dát
→ execute behavior
→ assertions a postcondition
→ capture artifacts
→ cleanup aj po partial failure
```

Readiness nie je iba otvorený port. PostgreSQL musí prijímať query; API musí vedieť obslúžiť relevantný readiness contract; broker musí mať pripravený topic/queue.

Cleanup musí byť:

- idempotentný;
- scoped iba na resources testu;
- bezpečný po partial setup;
- vykonaný v `finally`-like lifecycle;
- nesmie zakryť primárny failure.

Ak cleanup zlyhá, zaznamenaj obe chyby a ponechaj pôvodný behavior failure ako primárny.

## 18. Test data a paralelizácia

Paralelizácia je bezpečná iba bez shared mutable state.

Pre Atlas používaj:

- unikátny tenant ID;
- unikátny idempotency key;
- schema/database per worker;
- dynamický port;
- correlation ID per attempt;
- resource names s run ID;
- cleanup obmedzený na vlastný namespace.

Fixed ports, globálny user `test@example.com`, spoločná queue a `DELETE FROM orders` bez namespace-u vytvárajú order dependency a flakiness.

Concurrency limit je súčasť correctness. Neobmedzený parallel run môže testovať saturáciu test environmentu namiesto product behavioru.

## 19. Failure paths sú produkčné správanie

Testuj aj:

- timeout a cancellation;
- dependency unavailable alebo slow;
- malformed a semanticky chybnú odpoveď;
- duplicate request/message;
- expired credential;
- permission denied;
- stale resource version;
- deadlock alebo optimistic conflict;
- partial write;
- process termination počas operácie;
- retry exhaustion;
- pool, queue alebo disk saturation.

Double môže presne vyvolať failure. Kritické assumptions však over aj na reálnej boundary, napríklad skutočný DB conflict alebo socket timeout.

## 20. Assertions podľa scope

### Unit

Overuj:

- returned value alebo domain error;
- state transition;
- invariant;
- významný emitted command/event;
- absenciu side effectu pri odmietnutí.

### Integration

Overuj:

- persisted state;
- constraint a transaction outcome;
- serialization/protocol result;
- retry a timeout behavior;
- cleanup a recovery reálnej boundary.

### Component

Overuj:

- public API behavior;
- middleware a authorization;
- state a external side effects;
- error model;
- audit, correlation a observability metadata;
- artifact/runtime identity.

Interný method-call count nie je public contract bez konkrétneho correctness dôvodu.

## 21. Failure artifacts

Pri failure uchovaj minimálne:

- commit a artifact digest;
- test attempt/run ID;
- seed, tenant a correlation ID;
- dependency versions;
- request/response metadata s redaction;
- service/container status;
- relevantné logs a traces;
- DB schema version a persisted rows;
- broker message IDs/offsets;
- setup, execute a teardown timeline.

Artifact bez identity test attemptu alebo bez časovej väzby má malú diagnostickú hodnotu.

## 22. Diagnostický postup

Najprv klasifikuj failure:

```text
behavior failure
boundary/dependency failure
fixture/setup failure
environment capacity failure
test implementation alebo oracle failure
cleanup failure
```

Postup:

1. over subject input a initial state;
2. over artifact a dependency versions;
3. over readiness a config;
4. nájdi correlation ID v logs/traces;
5. pozri autoritatívny persisted alebo emitted state;
6. porovnaj first attempt s rerunom bez zmeny;
7. reprodukuj najmenší scope, ktorý ponechá podozrivú boundary reálnu;
8. oprav produkt, seam, fixture alebo environment podľa dôkazu.

Rerun bez zachovania prvého attemptu môže odstrániť dôkaz race-u, timeoutu alebo cleanup chyby.

## 23. Mutation testing

Mutation testing zámerne zmení produkčnú logiku, napríklad obráti comparison alebo odstráni authorization condition. Ak suite zostane zelená, oracle alebo scenár nie je citlivý na chybu.

Používaj ho cielene pre:

- financial calculations;
- authorization;
- state machines;
- parsers;
- idempotency a deduplication rules.

Mutation score nie je samostatný cieľ. Má ukázať, či testy skutočne rozlišujú správne a chybné správanie.

## 24. Rozhodovací rámec

Pre nový test:

1. pomenuj behavior a failure mode;
2. urč boundary, kde failure vzniká;
3. zvoľ najnižší scope, ktorý ju vykoná reálne;
4. definuj subject a ostatné dependencies;
5. vyber doubles iba pre boundaries mimo scope;
6. definuj oracle, side effects a blind spots;
7. navrhni data isolation a parallelism;
8. definuj readiness a deadline;
9. definuj cleanup po partial failure;
10. urč failure artifacts a ownera;
11. vyšší scope pridaj iba pri novej fidelity.

## 25. Referenčné pravidlá

- Unit test je definovaný izolovanou behavior boundary, nie jednou metódou.
- Integration test vykonáva reálnu technickú alebo procesnú boundary.
- Component test spúšťa jeden celý komponent cez jeho public contract.
- Fake databáza nie je dôkaz produkčných SQL semantics.
- Reálna dependency môže byť súčasťou hermetického testu.
- Fixed `sleep` nahraď condition-based waitingom s deadline.
- Test data namespacuj a cleanup obmedz na vlastnené resources.
- Artifact a dependency versions pinuj a zaznamenávaj.
- Doubles chráň contract testom proti driftu.
- Oracle musí overiť význam a side effects, nie iba úspešný command.
- Vyšší scope musí pridať boundary alebo fidelity.

## 26. Časté omyly

### „Unit test musí testovať jednu metódu“

Nie. Testuje jednu izolovanú jednotku správania.

### „Integration test znamená dve microservices“

Nie. Jedna aplikácia proti reálnemu PostgreSQL, brokeru alebo filesystemu je integration test.

### „Hermetic test nepoužíva reálne dependencies“

Nie. Reálna dependency môže byť plne kontrolovanou súčasťou test environmentu.

### „Component test je menší E2E test“

Component test zostáva v ownership boundary jedného komponentu a kontroluje externý svet. E2E prechádza cez viac autonómnych komponentov.

### „Mock zaručuje správnosť integrácie“

Nie. Potvrdzuje iba model dependency vytvorený testom.

### „Otvorený port znamená readiness“

Nie. Proces môže počúvať, ale ešte nemať migrácie, leadera alebo použiteľnú business boundary.

### „Rerun vyriešil flaky failure“

Nie. Rerun iba vytvoril nový attempt a môže odstrániť pôvodný dôkaz.

## Ako určiť hranicu unit, integration a component testu

Rozdiel medzi unit, integration a component testom sa nedá spoľahlivo určiť podľa názvu frameworku. Rozhoduje **system under test**, teda presný subject, ktorý test vykonáva, a hranice, ktoré sú reálne alebo nahradené.

**Unit test** drží subject úzky a kontroluje jeho dependencies. Unit nemusí znamenať jednu metódu; môže to byť malá coherent business jednotka. Dôležité je, že failure sa dá lokalizovať bez štartu databázy, siete alebo ďalšieho procesu.

```python
def test_discount_is_not_applied_below_threshold():
    policy = DiscountPolicy(threshold=1000, percent=10)
    assert policy.apply(900) == 900
```

Test vytvorí objekt s explicitnými vstupmi a overí jedno business pravidlo. Neoveruje serializáciu, databázu ani konfiguráciu aplikácie. Jeho hodnota je rýchla a presná diagnóza logiky.

**Integration test** ponechá aspoň jednu významnú reálnu hranicu. Pri databáze nejde iba o to, že query „nejako prejde“. Test overuje driver, schema, constraints, transaction isolation, encoding a mapping medzi aplikačným a databázovým modelom.

```text
application repository code
→ database driver
→ reálna database engine
→ migration generation
→ read-back a invariant
```

Ak test používa SQLite namiesto produkčnej PostgreSQL, ide stále o dynamický test, ale fidelity voči SQL dialektu, locking-u a typom je obmedzená. Toto obmedzenie musí byť viditeľné vo verdicte.

**Component test** spustí väčší komponent cez jeho verejnú hranicu, často ako samostatný process alebo container, no externé dependencies nahradí kontrolovanými implementáciami. Napríklad Orders API môže bežať s reálnym HTTP serverom a databázou, ale provider platieb je fake server.

Rozlišuj tiež **in-process** a **out-of-process** boundary. Priame volanie controller function neoveruje HTTP routing, middleware a serialization. Request cez socket na reálny server ich už zahŕňa, aj keď oba testy používajú rovnaký jazyk.

Setup a cleanup sú súčasťou dôkazu. Transaction rollback po každom teste znižuje kontamináciu, ale môže skryť behavior, ktorý nastáva až pri commit-e. Container vytvorený pre suite môže zrýchliť testy, no shared state môže spôsobiť order dependency. Preto má test explicitne uviesť:

```text
čo sa vytvára pre každý test
čo sa zdieľa v suite
ako sa generuje jedinečná identita dát
ako sa overí cleanup
```

Ak test prejde s fake dependency, preukazuje správanie voči contractu fake-u. Nepreukazuje, že fake presne reprezentuje reálnu dependency. Túto medzeru uzatvára contract test alebo samostatný integration test s reálnym systémom.

## 27. Zhrnutie

Atlas `CreateOrder` potrebuje tri odlišné vrstvy dôkazu:

```text
unit
→ správna doménová state transition

integration
→ správna reálna PostgreSQL/broker boundary

component
→ správny orders-api artifact cez public HTTP contract
```

Dôveryhodnosť nevzniká z názvu testu. Vzniká z presnej mapy boundaries, vhodného scope-u, silného oraclu, kontrolovaného lifecycle-u, izolovaných dát a diagnostických artifacts.

## 28. Kontrolné otázky

1. Čo určuje scope unit, integration a component testu?
2. Aký je rozdiel medzi subject, dependency, boundary a oracle?
3. Prečo Atlas pricing rule patrí do unit testu?
4. Prečo transakčný outbox potrebuje reálny PostgreSQL integration test?
5. Aký nový dôkaz pridáva out-of-process component test?
6. Kedy má byť dependency reálna a kedy nahradená double?
7. Prečo fake repository nepreukazuje SQL constraints a transactions?
8. Čo znamená hermetic test s reálnou databázou?
9. Prečo fixed `sleep` vytvára flaky test?
10. Ako izoluješ test data pri paralelnom behu?
11. Aké artifacts potrebuješ pri timeout-e alebo race failure?
12. Kedy vyšší scope nepridáva hodnotu?
13. Ako mutation testing odhalí slabý oracle?
14. Ako rozlíšiš product failure od setup alebo test failure?

## Glossary impact

Relevantné pojmy: unit test, integration test, component test, subject under test, boundary, dependency, oracle, test seam, solitary test, sociable test, dummy, stub, fake, spy, mock, simulator, hermetic test, fixture, readiness, condition-based waiting, correlation ID, namespace isolation, mutation testing a failure artifact.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Test pyramid](test-pyramid.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Contract a API tests →](contract-and-api-tests.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
