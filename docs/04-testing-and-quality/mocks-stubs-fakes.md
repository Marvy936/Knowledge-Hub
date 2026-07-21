# Mocks, stubs a fakes

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

## 1. Test doubles

Test double je náhrada reálnej dependency použitá v teste. Hlavné druhy:

- dummy,
- stub,
- fake,
- spy,
- mock.

Tieto pojmy opisujú rozdielne správanie a účel. Nie každá náhrada dependency je mock.

## 2. Dummy

Dummy je hodnota potrebná iba na vyplnenie parametra. Test ju aktívne nepoužíva.

```python
send_report(report, unused_audit_context)
```

Dummy nemá modelovať správanie systému.

## 3. Stub

Stub vracia vopred pripravené odpovede:

```python
class UserRepositoryStub:
    def find(self, user_id):
        return User(id=user_id, active=True)
```

Používa sa na riadenie vstupov a stavov testu. Typicky neoveruje počet alebo poradie volaní.

## 4. Fake

Fake je zjednodušená, ale funkčná implementácia:

- in-memory repository,
- lokálny object storage emulator,
- jednoduchý message broker,
- deterministic clock,
- test payment gateway.

Fake môže podporovať realistickejší workflow než stub, ale musí zachovať relevantné semantics reálnej dependency.

## 5. Spy

Spy zaznamenáva interakcie, ktoré test neskôr vyhodnotí:

```text
ktoré metódy boli volané
s akými argumentmi
v akom poradí
koľkokrát
```

Môže obaliť reálnu implementáciu alebo test double.

## 6. Mock

Mock je test double s očakávaniami na interakcie. Test overuje behavior interaction:

```text
pri zrušení objednávky
→ payment gateway dostane refund
→ event publisher odošle OrderCancelled
```

Mock je vhodný, keď samotná interakcia tvorí kontrakt. Nadmerné mockovanie však viaže test na internú implementáciu.

## 7. State vs. interaction testing

### State-based test

Overuje výsledný stav alebo output:

```python
assert account.balance == 90
```

### Interaction-based test

Overuje komunikáciu medzi objektmi:

```python
payment_gateway.refund.assert_called_once_with(payment_id, 10)
```

Preferuj observable state/output, pokiaľ interakcia sama nie je dôležitý boundary contract.

## 8. Kedy použiť reálnu dependency

Reálna dependency je vhodná, keď:

- je rýchla a lokálne spustiteľná,
- jej semantics sú hlavným rizikom,
- fake by bol náročnejší než containerized service,
- potrebuješ overiť serialization, SQL, network alebo protocol behavior.

Príklady:

- reálna PostgreSQL v integration teste,
- lokálny HTTP server,
- skutočný parser,
- ephemeral container.

## 9. Kedy použiť stub alebo fake

Vhodné pri:

- drahej alebo nedostupnej externej službe,
- deterministickom simulovaní errors,
- riadení času,
- rate limit alebo timeout scenároch,
- unit teste rozhodovacej logiky,
- izolácii testu od nekontrolovateľného prostredia.

## 10. Contract drift

Fake alebo stub môže prestať zodpovedať reálnej službe.

Ochrany:

- contract tests,
- shared schemas,
- pravidelné conformance tests,
- verziovanie fake-u,
- testovanie rovnakých fixtures proti fake aj real dependency,
- obmedzenie modelovaných semantics.

Fake, ktorý je pohodlnejší než realita, môže vytvárať false confidence.

## 11. Mocking boundaries

Dobré boundaries na nahradenie:

- čas,
- random source,
- filesystem alebo network port,
- external API,
- message publisher,
- secrets provider,
- payment alebo notification service.

Rizikové je mockovať:

- každý interný helper,
- value objects,
- framework internals,
- vlastný business object graph po každom call-e.

Test potom overuje implementačný postup namiesto výsledného správania.

## 12. Time a clock

Nepoužívaj priamo wall clock v každom module. Injektuj clock abstraction:

```python
class Clock:
    def now(self) -> datetime:
        ...
```

Fake clock umožní testovať:

- expiry,
- retry schedule,
- daylight-saving transitions,
- timeout,
- lease renewal,
- backoff.

## 13. Randomness

Použi seedovaný generator alebo injected random source. Test musí vedieť:

- reprodukovať failure,
- zaznamenať seed,
- odlíšiť property-based exploration od deterministic regression testu.

Mockovať každé random call poradie je krehké; lepšie je kontrolovať seed alebo vyšší kontrakt.

## 14. Network failures

Test double má vedieť simulovať:

- timeout,
- connection reset,
- partial response,
- malformed response,
- rate limit,
- retryable a non-retryable status,
- pomalý stream,
- duplicate alebo out-of-order event.

Jednoduchý stub, ktorý vždy vráti 200, nepokrýva resilience logiku.

## 15. Database fakes

In-memory map nie je automaticky náhradou SQL databázy. Môže sa líšiť v:

- transactions,
- constraints,
- isolation,
- collation,
- null semantics,
- query planner,
- locking,
- generated IDs.

Business unit tests môžu použiť fake repository, ale persistence behavior potrebuje test s reálnym engine-om.

## 16. Mock server a service virtualization

HTTP mock server môže simulovať external API cez reálne protocol boundary:

- request matching,
- response fixtures,
- delays,
- connection failure,
- stateful scenarios.

Je realistickejší než mockovanie klientovej internej metódy, pretože overuje serialization a network client behavior.

## 17. Over-specification

Krehký test:

```text
metóda A volaná presne raz
potom B presne dvakrát
potom C s interným DTO
```

Ak poradie nie je contract, taký test blokuje bezpečný refactoring.

Overuj iba interakcie relevantné pre výsledok, side effect alebo boundary protocol.

## 18. Default strictness

Strict mock zlyhá pri neočakávanej interakcii. Loose mock ignoruje nešpecifikované calls.

Strictness zvoľ podľa rizika:

- strict pri security-sensitive alebo finančnom side effecte,
- menej strict pri incidental telemetry,
- explicitne ignorovať iba vedľajšie interakcie.

## 19. Argument matching

Overuj významné vlastnosti, nie celý objekt, ak zvyšok nie je contract:

```text
order_id musí sedieť
amount musí sedieť
trace timestamp nemusí byť exact
```

Príliš široký matcher typu `any()` môže skryť chybu. Príliš presný matcher vytvára krehkosť.

## 20. Cleanup a isolation

Test doubles nesmú zdieľať mutable state medzi testami. Resetuj:

- recorded calls,
- fake database,
- virtual clock,
- queued events,
- configured responses.

Global singleton mock spôsobuje order-dependent failures.

## 21. Typické omyly

### „Každá dependency má byť mock“

Nie. Relevantné integration semantics by sa stratili.

### „In-memory database sa správa ako production database“

Často nie.

### „Mock overí, že systém funguje“

Overí iba naprogramované expectations; môže kopírovať rovnaký chybný predpoklad ako implementácia.

### „Viac interaction assertions znamená presnejší test“

Môže znamenať iba silnejšie coupling na implementation details.

### „Fake netreba testovať“

Fake musí mať conformance voči relevantnému kontraktu.

## 22. Rozhodovací rámec

1. Aké správanie testujem?
2. Je dependency súčasťou rizika?
3. Môžem použiť reálnu dependency lokálne?
4. Potrebujem iba pripravený output alebo funkčný model?
5. Je interakcia observable contract?
6. Ako zabránim driftu fake-u?
7. Aké failures potrebujem simulovať?
8. Bude test odolný voči internému refactoringu?
9. Aké state treba resetovať?
10. Ktorá vyššia testovacia vrstva overí real integration?

## Glossary impact

Relevantné pojmy: test double, dummy, stub, fake, spy, mock, state-based testing, interaction-based testing, fake clock, service virtualization, mock server, strict mock, contract drift a over-specification.
