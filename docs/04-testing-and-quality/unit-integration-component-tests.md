# Unit, integration a component tests

Unit, integration a component tests sa líšia najmä scope-om, hranicami a typom používaných dependencies. Názov testu má opisovať, čo je reálne zahrnuté, nie iba framework alebo adresár, v ktorom sa nachádza.

## 1. Unit test

Unit test overuje malú jednotku správania izolovane od pomalých alebo nedeterministických externých dependencies.

Jednotkou môže byť:

- function,
- class,
- module,
- domain aggregate,
- policy engine,
- parser,
- transformer.

Dôležité je, že failure má úzky diagnostický scope.

Príklad:

```python
def calculate_total(items, discount):
    subtotal = sum(item.price * item.quantity for item in items)
    return max(0, subtotal - discount)
```

Unit tests majú pokryť:

- nulové a hraničné hodnoty,
- rounding,
- invalid input,
- invariants,
- deterministické business rules.

## 2. Sociable vs. solitary unit tests

### Solitary unit test

Izoluje testovaný objekt od spolupracovníkov pomocou test doubles.

Výhody:

- veľmi presný failure,
- jednoduchá simulácia edge cases,
- vysoká rýchlosť.

Nevýhody:

- väzba na interné interakcie,
- riziko, že mockovaný kontrakt nezodpovedá realite.

### Sociable unit test

Používa reálne spolupracujúce objekty v pamäti a izoluje iba externé boundaries.

Výhody:

- testuje behavior viacerých doménových objektov,
- menej brittle interaction assertions.

Nevýhody:

- širší failure scope,
- zložitejší setup.

Oba prístupy sú legitímne. Rozhoduje architektúra a riziko.

## 3. Integration test

Integration test overuje reálnu spoluprácu aspoň dvoch komponentov alebo systému s externou technickou dependency.

Príklady:

- repository a PostgreSQL,
- service a Kafka,
- aplikácia a object storage,
- HTTP client a test server,
- Terraform provider a sandbox account,
- Kubernetes controller a API server.

Integration test má overovať behavior, ktorý unit test nedokáže spoľahlivo simulovať:

- SQL semantics,
- transaction isolation,
- serialization,
- network protocol,
- authentication,
- retry a timeout behavior,
- filesystem permissions,
- cloud API constraints.

## 4. Component test

Component test spúšťa celý deployovateľný komponent ako čiernu alebo sivú skrinku, ale externé systémy môže nahradiť kontrolovanými doubles.

Príklad:

```text
HTTP request
→ reálna application process
→ reálny routing, middleware a domain logic
→ test database
→ fake payment provider
```

Component test poskytuje vyššiu fidelity než unit test a nižšiu komplexitu než multi-service E2E test.

## 5. In-process vs. out-of-process integration

### In-process

Test načíta framework a aplikačné komponenty v test process-e.

Výhody:

- rýchlejší startup,
- jednoduchšie assertions,
- prístup k interným hooks.

Riziká:

- odlišný lifecycle než produkcia,
- môže obísť packaging, network a process boundaries.

### Out-of-process

Test komunikuje s reálne spusteným procesom alebo kontajnerom.

Výhody:

- overuje packaging a startup,
- reálne sockety a protokoly,
- bližšie deploymentu.

Riziká:

- pomalší setup,
- náročnejšia diagnostika.

## 6. Test doubles

### Stub

Vracia pripravené odpovede.

### Fake

Funkčná, ale zjednodušená implementácia, napríklad in-memory repository.

### Mock

Overuje očakávané interakcie.

### Spy

Zaznamenáva uskutočnené volania.

### Simulator alebo emulator

Napodobňuje rozsiahlejší protokol alebo platformu.

Test double musí byť zvolený podľa rizika. In-memory databáza nie je plnohodnotná náhrada PostgreSQL, ak testujeme SQL dialect, constraints alebo isolation.

## 7. Database integration tests

Dôležité oblasti:

- migrations,
- constraints,
- indexes,
- transactions,
- isolation levels,
- query behavior,
- encoding a collation,
- connection pool,
- cleanup.

Preferuj reálny engine rovnakej major verzie ako produkcia.

Test data isolation možnosti:

- transaction rollback,
- samostatná schema,
- unikátny tenant alebo namespace,
- disposable database/container,
- database snapshot restore.

## 8. Containerized dependencies

Ephemeral containers zjednodušujú spustenie reálnych dependencies v CI.

Výhody:

- version pinning,
- izolácia,
- reprodukovateľný startup,
- lokálna a CI podobnosť.

Riziká:

- image pull latency,
- port collisions,
- startup race,
- cleanup leaks,
- rozdiel od managed cloud service.

Readiness musí byť overená funkčným probe-om, nie iba existenciou procesu.

## 9. Hermetic tests

Hermetic test kontroluje všetky vstupy a nespolieha sa na nepredvídateľný externý stav.

Mal by mať pod kontrolou:

- čas,
- random seed,
- locale,
- timezone,
- filesystem,
- network,
- environment variables,
- test data,
- dependency versions.

Hermetic neznamená bez reálnych dependencies. Disposable PostgreSQL môže byť súčasťou hermetického test environmentu.

## 10. Clock a randomness

Priamy prístup na system clock alebo global randomness vytvára flaky tests.

Lepší model:

```text
Clock interface
Random source interface
ID generator interface
```

Test dodá deterministickú implementáciu.

Nejde o mockovanie všetkého, ale o kontrolu nedeterministických vstupov.

## 11. Parallelization

Testy musia byť navrhnuté tak, aby sa neovplyvňovali cez:

- spoločnú databázu,
- rovnaké ports,
- fixed filenames,
- global environment,
- shared queues,
- external rate limits.

Používaj unique identifiers, namespace-per-test a idempotent cleanup.

## 12. Setup a teardown

Setup má vytvoriť minimálny potrebný stav. Teardown má byť bezpečný aj pri partial failure.

Anti-patterny:

- gigantické shared fixtures,
- závislosť poradia testov,
- cleanup iba na success path,
- ručné čakanie cez pevné `sleep`,
- test data vytvorené mimo testu bez ownershipu.

## 13. Assertions podľa vrstvy

Unit test:

- hodnoty,
- invariants,
- domain errors.

Integration test:

- persisted state,
- constraints,
- protocol response,
- transaction effects.

Component test:

- public API behavior,
- middleware,
- authorization,
- emitted events,
- observability metadata.

Test nemá overovať interné detaily, ktoré nie sú súčasťou kontraktu vrstvy.

## 14. Negative paths

Testuj aj:

- dependency timeout,
- malformed response,
- unavailable database,
- duplicate message,
- partial write,
- cancellation,
- permission denied,
- rate limit,
- stale version,
- concurrent update.

Failure handling je produkčné správanie, nie okrajová výnimka.

## 15. Mutation testing

Mutation testing zámerne mení kód, napríklad otočí comparison alebo odstráni condition, a overí, či testy mutáciu zachytia.

Pomáha odhaliť:

- assertions bez hodnoty,
- neotestované branches,
- vysoké coverage bez citlivosti na chyby.

Je drahšie, preto sa používa cielene na kritickú logiku.

## 16. Anti-patterny

### Unit test cez reálnu sieť

Test je pomalý a nondeterministický, hoci cieľom bola lokálna logika.

### Integration test s úplne mockovaným kontraktom

Neoverí skutočnú integráciu.

### Component test, ktorý potrebuje celý podnikový stack

Scope sa zmenil na E2E a diagnostika sa rozšírila.

### Assertion počtu interných method calls

Bez behavior dôvodu vytvára brittle test.

### Shared mutable fixture

Testy závisia od poradia a paralelného timing-u.

## 17. Rozhodovací rámec

1. Akú hranicu alebo správanie testujem?
2. Ktoré dependencies musia byť reálne?
3. Ktoré môžu byť controllable doubles?
4. Aký failure by mock skryl?
5. Potrebujem process alebo network boundary?
6. Ako izolujem test data?
7. Ako test čaká na readiness bez pevného sleepu?
8. Je test bezpečne paralelizovateľný?
9. Aký je cleanup pri zlyhaní?
10. Aký výstup pomôže diagnostike?

## 18. Kontrolné otázky

1. Čo definuje unit test?
2. Aký je rozdiel medzi solitary a sociable unit testom?
3. Čo má overovať integration test?
4. Ako sa component test líši od E2E testu?
5. Aký je rozdiel medzi stub, fake, mock a spy?
6. Prečo in-memory database nemusí byť vhodná náhrada produkčnej DB?
7. Čo znamená hermetic test?
8. Ako izolovať databázové test data?
9. Prečo pevný `sleep` vytvára flaky tests?
10. Načo slúži mutation testing?

## Glossary impact

Relevantné pojmy: unit test, integration test, component test, sociable unit test, solitary unit test, test double, stub, fake, mock, spy, hermetic test, fixture a mutation testing.