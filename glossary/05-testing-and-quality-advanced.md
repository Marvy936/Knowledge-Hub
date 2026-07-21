# Advanced Testing and Software Quality glossary entries

## Advisory gate

Quality gate, ktorý reportuje výsledok, ale neblokuje ďalší delivery krok. Používa sa pri zavádzaní alebo kalibrácii kontroly. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Attack surface

Súbor rozhraní, vstupov, identities a trust boundaries, cez ktoré môže aktér ovplyvniť systém. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Blocking gate

Quality gate, ktorého failure zastaví merge, release alebo deployment. Má byť presný, stabilný a reprodukovateľný. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Branch coverage

Podiel výsledkov rozhodovacích vetiev vykonaných test suite. Poskytuje jemnejší signál než samotná line coverage. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Capacity test

Performance test hľadajúci maximálny udržateľný workload pri definovaných SLO a bezpečnostnej rezerve. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Closed workload model

Model, v ktorom fixný počet virtual users generuje ďalšiu operáciu až po dokončení predchádzajúcej. Spomalenie systému preto môže znížiť generovaný arrival rate. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Code coverage

Metrika určujúca, ktorá časť kódu bola vykonaná počas testov. Nedokazuje správnosť assertions ani business behavior. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Condition-based wait

Čakanie na explicitnú podmienku s deadline namiesto pevného sleepu. Znižuje timing flakiness a zrýchľuje test pri rýchlom výsledku. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Condition coverage

Coverage metrika sledujúca, či jednotlivé boolean podmienky nadobudli relevantné true a false výsledky. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Contract drift

Rozdiel medzi správaním test double alebo dokumentovaného kontraktu a skutočnou dependency. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Coordinated omission

Skreslenie performance merania, pri ktorom load generator počas spomalenia neposiela requests, ktoré by v reálnom arrival-rate modeli prišli. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## DAST — Dynamic Application Security Testing

Security testovanie bežiacej aplikácie zvonka cez jej runtime rozhrania. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Diff coverage

Coverage vypočítaná iba pre nový alebo zmenený kód voči zvolenému merge base. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Dummy — test double

Hodnota potrebná iba na vyplnenie parametra bez aktívneho použitia v testovanom scenári. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Fake — test double

Zjednodušená, ale funkčná implementácia dependency používaná v teste, napríklad in-memory repository alebo fake clock. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## First-attempt pass rate

Podiel testov, ktoré prejdú na prvý pokus bez retry. Je citlivejším signálom flakiness než finálna pass rate po opakovaniach. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Flaky test

Test, ktorý pri rovnakom kóde a deklarovaných vstupoch nedeterministicky prechádza alebo zlyháva. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## IAST — Interactive Application Security Testing

Security analýza využívajúca runtime informácie z instrumentovanej aplikácie počas testov. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## IaC scanning

Statická alebo plan-level kontrola Infrastructure as Code proti syntax, schema, security a policy pravidlám. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Interaction-based testing

Testovanie, ktoré overuje komunikáciu a side effects medzi objektmi alebo komponentmi, napríklad volanie gateway s konkrétnymi argumentmi. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Line coverage

Podiel vykonaných source riadkov počas testov. Vysoká hodnota sama osebe nedokazuje správnosť testov. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Load shedding

Kontrolované odmietnutie časti práce pri preťažení s cieľom chrániť jadro služby a zabrániť cascading failure. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Load test

Performance test overujúci očakávaný workload a splnenie latency, throughput, error-rate a resource kritérií. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Mock — test double

Test double s explicitnými očakávaniami na interakcie. Je vhodný, keď komunikácia sama tvorí relevantný kontrakt. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Mutation score

Podiel zámerných code mutations, ktoré test suite odhalí zlyhaním. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Mutation testing

Technika zámerne meniaca produkčný kód a overujúca, či test suite tieto zmeny zachytí. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Open workload model

Model, v ktorom requests prichádzajú podľa arrival rate nezávisle od aktuálnej response time systému. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Over-specification — testing

Test anti-pattern, pri ktorom assertions overujú nepodstatné interné poradie alebo implementačné detaily a blokujú bezpečný refactoring. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Performance test

Test časových a kapacitných vlastností systému pri explicitnom workload modeli, prostredí a success criteria. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Policy as Code

Strojovo vyhodnotiteľná bezpečnostná alebo prevádzková policy spravovaná ako verzovaný kód s testami a exception lifecycle. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Production-derived test data

Testovacie dáta odvodené z produkcie, ktoré vyžadujú data minimization, anonymizáciu, access control a retention policy. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Quality gate

Automatické rozhodovacie pravidlo, ktoré na základe definovaných signálov povoľuje alebo blokuje ďalší delivery krok. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Quarantine — testing

Dočasné vyradenie nestabilného testu z blocking suite pri zachovaní pravidelného spúšťania, ownera, issue a expiry. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Ratcheting — quality

Model, ktorý povoľuje iba zachovanie alebo zlepšenie predchádzajúceho akceptovaného quality baseline. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Rerun-until-green

Anti-pattern opakovania zlyhaného testu dovtedy, kým náhodne neprejde, bez riešenia príčiny alebo zachovania prvého failure signálu. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## SAST — Static Application Security Testing

Statická bezpečnostná analýza source, bytecode alebo intermediate representation bez spustenia celej aplikácie. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## SCA — Software Composition Analysis

Analýza third-party dependencies, transitívneho graphu, licencií a známych vulnerabilities. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Scalability test

Performance test overujúci, ako sa kapacita a SLO menia po pridaní alebo odobratí resources. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Soak test

Dlhodobý performance test hľadajúci memory leaks, resource leaks, queue growth a kumulatívne zlyhania. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Spike test

Performance test prudkej zmeny trafficu, ktorý overuje autoscaling, queues, caches, connection pools a recovery. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Spy — test double

Test double alebo wrapper zaznamenávajúci uskutočnené interakcie na neskoršie assertions. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## State-based testing

Testovanie výsledného outputu alebo stavu namiesto detailného overovania interných interakcií. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Static analysis

Analýza source alebo jeho reprezentácie bez vykonania celej aplikácie, napríklad linting, type checking alebo data-flow analysis. Pozri [Static analysis, linting a type checking](docs/04-testing-and-quality/static-analysis-linting-type-checking.md).

## Stress test

Performance test nad plánovanou kapacitou zameraný na failure mode, ochranné mechanizmy a recovery. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Stub — test double

Kontrolovaná náhrada dependency vracajúca vopred pripravené odpovede pre riadenie testovacieho scenára. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Synthetic test data

Umelo generované testovacie dáta bez priameho kopírovania reálnych osobných alebo citlivých záznamov. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Taint analysis

Statická analýza sledujúca nedôveryhodné dáta od source cez transformácie po citlivý sink. Pozri [Static analysis, linting a type checking](docs/04-testing-and-quality/static-analysis-linting-type-checking.md).

## Test data factory

Programový builder vytvárajúci minimálne validné testovacie objekty so stabilnými defaults a explicitnými overrides. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Test double

Kontrolovaná náhrada dependency používaná v teste; zahŕňa dummy, stub, fake, spy a mock. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Test isolation

Vlastnosť testu, pri ktorej jeho výsledok nezávisí od poradia, paralelných testov ani zdieľaného mutable state. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Threat model

Štruktúrovaný opis assets, trust boundaries, aktérov, attack surfaces, abuse cases a mitigations. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Type checking

Statická kontrola konzistencie typových kontraktov a operácií. Nenahrádza runtime validáciu nedôveryhodných vstupov. Pozri [Static analysis, linting a type checking](docs/04-testing-and-quality/static-analysis-linting-type-checking.md).

## Vulnerability reachability

Posúdenie, či je zraniteľný component a code path skutočne prítomný, dostupný a využiteľný v konkrétnom runtime kontexte. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).
