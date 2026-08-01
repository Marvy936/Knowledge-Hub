# Mocks, stubs a fakes

Test double je kontrolovaná náhrada dependency použitá na izoláciu subjectu alebo vytvorenie ťažko reprodukovateľného stavu. Jednotlivé typy doubles majú odlišný účel.

**Dummy** iba vyplní parameter a test ho nepoužíva. **Stub** vracia vopred pripravené odpovede. **Fake** má zjednodušenú, ale funkčnú implementáciu, napríklad in-memory repository. **Spy** zaznamenáva calls pre neskoršie assertions. **Mock** overuje očakávané interactions a často je naprogramovaný na presný call sequence.

Neutrálny príklad payment service:

```text
stub:
Authorize() vždy vráti approved

fake:
in-memory ledger udržiava balances

spy:
zaznamená, či bol odoslaný receipt

mock:
očakáva presne jeden call Authorize(amount=10)
```

Double znižuje fidelity. In-memory fake databázy nemusí reprodukovať constraints, transactions, isolation alebo SQL dialect reálneho systému. Stub HTTP response môže ignorovať headers, latency, streaming a retry behavior.

Mock, ktorý overuje každý interný method call, viaže test na implementáciu a zhoršuje refactoring. Interaction assertion je vhodná, keď interaction samotná predstavuje contract alebo side effect, napríklad presne jeden payment authorization.

Contract drift vzniká, keď double naďalej vracia tvar, ktorý reálny provider už nepodporuje. Prevenciou je generovanie z contractu, shared compatibility tests alebo pravidelná verification proti reálnej dependency.

Výber double-u vychádza z failure mode. Čistá domain logika môže používať stub. SQL mapping potrebuje reálnu databázu. Network retry môže potrebovať controllable fake server, ktorý vie simulovať timeout po prijatí requestu.

Doubles nesmú byť ľahšou náhradou všetkých boundaries. Portfólio musí obsahovať aj testy, ktoré overia assumptions voči reálnym dependencies.

## 1. Cieľ kapitoly

Nosný rozhodovací model je:

```text
riziko
→ najnižší spoľahlivý scope
→ test seam
→ real/double boundary map
→ double role a behavior contract
→ state alebo interaction oracle
→ drift protection
→ vyšší integration/contract/runtime evidence
```

Nadmerné mockovanie vytvára rýchlu suite, ktorá testuje vlastné assumptions. Použitie každej reálnej dependency zase môže zmeniť lokálne tests na pomalý, flaky a ťažko diagnostikovateľný systém. Správny výber závisí od failure boundary, nie od preferovaného frameworku.

## 2. Nosný scenár: Atlas CreateOrder a platba

Atlas vytvára objednávku v dvoch fázach:

```text
POST /orders
→ domain validation
→ PostgreSQL order + outbox transaction
→ OrderCreated event
→ payment worker
→ Payments API authorize
→ order state transition
→ audit a confirmation
```

Relevantné risks:

- domain calculation alebo transition je chybná;
- order a outbox nie sú atomické;
- rovnaký idempotency key vytvorí viac payment attempts;
- payment timeout má unknown outcome;
- provider contract alebo serialization driftuje;
- async retry sa vykoná v nesprávnom čase;
- tenant alebo correlation identity sa stratí.

Jeden double nepokryje všetky risks. Atlas používa evidence ladder:

```text
unit
→ fake repository/outbox port, fake clock, payment stub

integration
→ reálny PostgreSQL a broker

component
→ reálny orders-api/worker artifact + controlled payment simulator

contract
→ consumer/provider expectations

sandbox
→ periodický test proti reálnemu providerovi
```

## 3. Test seam

Seam je miesto, kde možno dependency nahradiť alebo riadiť bez zmeny production intentu. Pri Atlas sú seams:

- repository a unit-of-work port;
- outbox publisher boundary;
- Payments API client;
- clock a scheduler;
- ID/idempotency generator;
- object storage adapter;
- audit/event sink.

Dobrá seam zodpovedá reálnej architektúre. Interface vytvorený iba na mockovanie každej private helper function zvyšuje coupling a nevytvára zmysluplnú boundary.

## 4. Real/double boundary map

Pred testom explicitne zapíš:

```text
subject under test
→ reálne collaborators
→ doubles
→ ktoré semantics double sľubuje
→ ktoré semantics zostávajú blind spotom
```

Príklad unit scope-u:

```text
CreateOrder use case
+ reálne domain objects
+ fake repository port
+ spy outbox port
+ fixed clock a ID provider
- bez PostgreSQL constraints/transactions
- bez broker delivery semantics
```

Príklad component scope-u:

```text
reálny worker process
+ reálny serializer/config/retry middleware
+ reálny PostgreSQL
+ controlled HTTP payment simulator
- bez reálnych provider quotas a network edge
```

## 5. Taxonómia podľa účelu

Pojmy označujú rolu v konkrétnom teste:

```text
dummy
→ vyplní nepoužitý parameter

stub
→ vráti pripravený input alebo failure

fake
→ poskytne zjednodušenú funkčnú implementáciu

spy
→ zaznamená uskutočnené interactions

mock
→ nesie vopred definované interaction expectations
```

Jeden object môže byť v jednom teste stub a v inom spy. Dôležité je pomenovať, čo test z jeho správania vyvodzuje.

## 6. Dummy

Dummy je hodnota potrebná na zostavenie callu, ale testovaný path ju nepoužije. Ak test začne čítať alebo overovať jej behavior, už nejde o dummy.

Veľké množstvo dummy dependencies často signalizuje príliš široký constructor alebo komponent s viacerými responsibilities. Testability tu odhaľuje design problém, nie potrebu ďalšieho mocking frameworku.

## 7. Stub

Stub pripraví odpoveď alebo failure:

```text
Payments API
→ 200 Authorized
→ 409 IdempotencyConflict
→ 429 + Retry-After
→ connect timeout
→ read timeout po možnom prijatí requestu
```

Stub riadi vstup do decision logic. Test spravidla neoveruje interný call count, pokiaľ počet pokusov sám nemení finančný alebo prevádzkový výsledok.

Dobrý stub podporuje iba variants potrebné pre scenár. Desiatky stateful odpovedí a transitions znamenajú, že vzniká fake alebo simulator a potrebuje vlastný contract.

## 8. Fake

Fake je zjednodušená funkčná implementácia. Môže udržiavať state a podporovať celý workflow, napríklad in-memory repository alebo virtual clock.

Fake musí deklarovať fidelity:

```text
modeluje
→ save/read, duplicate ID, optimistic version

nemodeluje
→ SQL isolation, collation, locks, connection failure
```

In-memory map nie je „rýchla PostgreSQL“. Je iný systém s inými semantics.

## 9. Spy

Spy zaznamená interactions po vykonaní behavioru. Atlas môže overiť, že vznikol `OrderCreated` event s order ID, tenant ID a correlation ID.

Spy je vhodný, keď side effect nemožno v danom scope-e pohodlne pozorovať cez return value. Zaznamenáva iba fields potrebné pre oracle. Celý request dump môže vytvoriť krehký test a uniknúť secrets do failure logu.

## 10. Mock

Mock nesie očakávania na interaction. Je vhodný, keď komunikácia tvorí contract:

```text
unauthorized request
→ payment gateway sa nesmie volať

confirmed cancellation
→ refund attempt používa správnu payment identity a sumu

security decision
→ audit sink musí dostať DENY event
```

Mock nie je vhodný na overenie každého interného helper callu. Taký test opisuje implementáciu, nie behavior.

## 11. State-based verification ako default

State-based test overuje výsledný state alebo output:

```text
CreateOrder command
→ Order state ACCEPTED
→ total a tenant sú správne
```

Je odolnejší voči refaktoringu, ktorý zachová contract. Preferuj ho, keď je behavior spoľahlivo pozorovateľný.

Pri distribuovanom side effecte nemusí finálny state patriť do scope-u. Vtedy je legitímna interaction verification na boundary port-e, ale má overovať iba významné fields a semantics.

## 12. Interaction verification

Interaction assertion má zmysel, keď:

- nesmie vzniknúť žiadne volanie;
- počet attempts mení finančný alebo bezpečnostný dopad;
- poradie je protokolová požiadavka;
- call obsahuje principal, tenant alebo idempotency identity;
- finálny external state nie je v test scope-e pozorovateľný.

„Logger bol volaný pred repository“ nie je business contract. „Payment authorize nebolo volané po deny authorization“ contract je.

## 13. State a interaction sa dopĺňajú

Atlas payment unit test môže overiť:

```text
state
→ order zostáva PAYMENT_PENDING po retryable failure

interaction
→ vznikol presne jeden scheduled retry s rovnakým idempotency key
```

Tieto assertions dokazujú dve odlišné skutočnosti. Duplicitné overovanie rovnakého výsledku cez fake state aj call count nepridáva hodnotu.

## 14. Matchers a významné fields

Matcher kontroluje contract, nie celý náhodný object graph:

```text
order_id
→ exact

tenant_id
→ exact

amount a currency
→ exact business values

idempotency_key
→ zachovaná identity

trace_id
→ musí existovať a byť korelovateľný

timestamp
→ fixed clock alebo povolený interval
```

`any()` nad celým requestom môže skryť chybný tenant alebo sumu. Exact equality celého DTO môže byť krehká pri backward-compatible metadata field-e.

## 15. Call count a retry semantics

Call count je contract iba vtedy, keď mení outcome:

- `never` — zakázaný side effect;
- `exactly once` — jeden payment attempt pre daný idempotency state;
- `at most N` — bounded retry;
- poradie — iba pri protokole alebo compensation flowe.

Samotné „called three times“ nepreukazuje správny retry policy. Test má overiť retryable classification, backoff, deadline, idempotency key a zastavenie pri terminal outcome.

## 16. Strict a loose expectations

Strict expectation zlyhá pri neočakávanej interaction. Je vhodná pre payment, privilege grant, delete alebo external publication.

Targeted strictness overí kritické calls a ignoruje incidental telemetry. Loose mock je vhodný iba tam, kde neočakávaný call nemení testované riziko.

Príliš loose matcher skryje side effect. Príliš strict mock blokuje bezpečný refactoring. Strictness sa odvodzuje od impactu.

## 17. Async execution bez sleepu

Async double musí mať explicitný completion mechanism:

- awaitable future;
- controllable executor;
- in-memory queue s `drain()`;
- virtual scheduler;
- condition wait s deadline;
- fake clock pre čas plus explicitné spustenie due tasks.

Pevný sleep iba odkladá assertion. Nevysvetľuje, či task skončil, čaká alebo zlyhal.

Failure artifact má ukázať pending tasks, virtual time, queue state a recorded interactions.

## 18. Clock, monotonic time a scheduler

Wall clock, durations a scheduler nie sú tá istá dependency. Atlas rozlišuje:

```text
wall clock
→ business timestamp a expiry instant

monotonic clock
→ elapsed duration a deadline

scheduler
→ kedy sa due work skutočne vykoná
```

Posun fake clocku automaticky nespustí task, ak test explicitne nemodeluje timer queue. Tým sa zabráni testu, ktorý prejde v inej execution semantics než production.

## 19. Randomness a identity

Pri business teste preferuj semantic provider:

```text
generate_order_id()
choose_retry_jitter()
```

Mockovať presné poradie `random()` calls je krehké. Property-based failure uchová seed, framework version a minimalizovaný counterexample. Regression test môže použiť konkrétny failing input.

## 20. HTTP double fidelity ladder

Rôzne náhrady poskytujú rozdielny dôkaz:

```text
stub client method
→ decision logic bez serialization/networku

local mock server
→ reálny HTTP serializer, headers, timeout config a parser

provider simulator
→ stateful protocol a failure sequences

provider sandbox
→ reálne credentials, network, quotas a provider behavior
```

Atlas component test používa local simulator pre timeout-before-send, timeout-after-send, 429, malformed payload a duplicate response. Periodický sandbox test kontroluje drift a platform-specific behavior.

## 21. Unknown outcome ako významný failure model

Network timeout nemusí znamenať „provider request neprijal“:

```text
client odoslal request
→ provider autorizoval payment
→ response sa stratila
→ client vidí timeout
```

Double, ktorý každý timeout modeluje ako nulový side effect, učí aplikáciu nebezpečnú semantics. Správny simulator potrebuje query-by-idempotency-key alebo následnú reconciliation path.

## Doplnenie výkladu: rozdiel medzi stubom, fake-om, mockom a spy

Test double je náhradná implementácia dependency používaná v teste. Jednotlivé názvy opisujú odlišný účel:

- **stub** vracia pripravené odpovede; test sa pýta na výsledok subjectu;
- **fake** má zjednodušenú, ale funkčnú implementáciu, napríklad in-memory repository;
- **mock** obsahuje očakávania na interakcie a test verifikuje, že boli splnené;
- **spy** zaznamenáva volania reálnej alebo náhradnej implementácie na neskoršie assertions;
- **dummy** iba vypĺňa parameter a test ho nepoužíva.

Stub príklad:

```python
class ExchangeRateStub:
    def get_rate(self, currency: str) -> float:
        return 1.10
```

Test s ním overí pricing behavior pre fixnú sadzbu. Neoverí HTTP client, timeout ani parser skutočného provider response.

Mock príklad:

```python
mailer.send.assert_called_once_with(
    recipient="user@example.com",
    template="order-confirmed",
)
```

Assertion kontroluje interaction contract. Je vhodný, ak samotné volanie je dôležitý side effect. Ak test mockuje každý interný call, začne kopírovať implementáciu a zlyhá pri refactore bez zmeny behavioru.

Fake repository môže zrýchliť component tests, ale musí priznať rozdiel oproti reálnej databáze. Python dictionary nemá SQL constraints, isolation ani collation. Ak fake dovolí stav, ktorý produkčná databáza odmietne, zelený test je false confidence. Contract suite môže byť spustená proti fake-u aj reálnej implementácii a overiť spoločné behavior pravidlá.

Dôležité je, kto double vlastní. Consumer-defined stub môže postupne driftovať od providera. Generated client alebo provider contract verification znižuje túto medzeru. Pri externom API sa fake server má viazať na versionovaný contract a podporovať aj chybové odpovede, latency a retry-relevant behavior.

Test double nesmie z testu odstrániť presne tú hranicu, ktorej riziko chceme overiť. Ak rizikom je transaction isolation, in-memory fake nie je vhodný. Ak rizikom je čisto rozhodovacia logika po prijatí provider statusu, stub môže byť najnižší a najlepší scope.

## 22. Worked failure: payment fake zaručoval nemožný timeout

Atlas unit a component tests používali payment fake:

```text
timeout response
→ fake nevytvoril authorization
```

Production provider však mohol request commitnúť pred stratou response.

```text
payment authorized
→ response timeout
→ worker retryoval s novým key
→ druhá authorization
```

### Root cause

Fake modeloval timeout ako jednoznačný failure, hoci reálny protocol mal unknown outcome. Testy boli deterministické, ale semantic fidelity bola chybná.

### Náprava

- simulator podporuje timeout-before-commit aj timeout-after-commit;
- payment request používa stabilný idempotency key;
- worker po unknown outcome vykoná reconciliation;
- interaction test overí, že retry nemení identity;
- sandbox test potvrdí provider semantics;
- fake contract explicitne dokumentuje podporované outcomes.

## 23. Database fake a real engine

In-memory repository je vhodný pre domain decisions. Neoverí:

- transaction atomicity;
- unique a foreign-key constraints;
- isolation a locks;
- null/collation semantics;
- numeric precision a timezone;
- connection failure;
- query planner a index behavior.

Persistence risk preto používa ephemeral PostgreSQL kompatibilnej major verzie.

## 24. Worked failure: fake nepoznal unique constraint

Atlas idempotency unit tests používali dictionary fake keyovaný iba `idempotency_key`. Production unique constraint bol `(tenant_id, idempotency_key)`.

Neskorší refactor zmenil fake aj application lookup na global key, ale unit suite zostala zelená. V produkcii tenant B dostal collision s tenantom A.

### Root cause

Fake contract nebol spoločný s reálnou repository semantics a chýbala conformance fixture pre tenant-scoped uniqueness.

### Náprava

- repository port definuje compound identity;
- rovnaká conformance suite beží proti fake aj PostgreSQL adapteru;
- component test overí dva tenanty s rovnakým key;
- fake zlyhá explicitne pri nepodporovanej semantics;
- critical constraints sú dokumentované mimo fake implementation detailu.

## 25. Broker fake a delivery model

Fake broker musí deklarovať, či modeluje:

- at-least-once delivery;
- acknowledgement a redelivery;
- partition ordering;
- consumer groups;
- dead-letter behavior;
- retention a replay;
- visibility timeout.

In-memory list modeluje iba enqueue/dequeue. Nie je dôkazom broker durability ani retry behavioru. Reálny engine alebo faithful emulator patrí do integration scope-u, keď sú tieto semantics rizikom.

## 26. Simulator, emulator a sandbox

Názov nie je taký dôležitý ako explicitná fidelity. Pri cloud alebo provider náhrade dokumentuj:

- API a version support;
- consistency model;
- IAM/policy behavior;
- quotas a throttling;
- error model;
- unsupported operations;
- rozdiely oproti managed service.

Lokálna náhrada skracuje feedback. Nemôže byť jediným dôkazom pre platform-specific behavior.

## 27. Contract drift

Double driftuje, keď sa reálna dependency zmení a test double zostane rovnaký:

```text
shared contract/spec
→ conformance suite
→ run proti double
→ run proti real/sandbox implementation
→ versionovať double
→ evidovať unsupported semantics
```

Provider-driven schema kontroluje syntax a types. Consumer-driven contract kontroluje používané expectations. Runtime quotas, latency a undocumented behavior stále potrebujú sandbox alebo production evidence.

## 28. Conformance suite

Fake má testovať iba semantics, ktoré sľubuje:

```text
repository conformance
├─ save/read
├─ tenant-scoped duplicate key
├─ missing entity
├─ optimistic version conflict
└─ delete visibility
```

Rovnaké fixtures sa spustia proti fake a reálnemu adapteru. Ak fake contract nepodporuje, musí zlyhať explicitne, nie ticho vrátiť zjednodušený výsledok.

## 29. Kedy je reálna dependency lacnejšia

Reálna ephemeral dependency je vhodnejšia, keď:

- je rýchlo a hermeticky spustiteľná;
- jej semantics sú predmetom testu;
- container/embedded server je jednoduchší než údržba fake-u;
- protocol, transaction alebo filesystem behavior je kritický;
- drift fake-u má vysokú cenu;
- failure sa dá dobre lokalizovať.

Shared staging service nie je automaticky realistickejšia. Môže mať nekontrolované dáta, verziu a availability. Ephemeral instance poskytuje real semantics aj isolation.

## 30. Reset, ownership a paralelnosť

Mutable double má novú instance per test alebo per explicitný scope. Reset zahŕňa:

- prepared responses;
- recorded calls;
- fake state;
- queues a callbacks;
- virtual time;
- random generator;
- global config;
- captured credentials.

Singleton mock vytvára order dependence a race conditions. Failure snapshot sa zachová pred teardownom.

## 31. Secrets a failure messages

Mock framework môže pri mismatchi vypísať celý request. Payment, identity alebo export request môže obsahovať token, osobné údaje alebo signed URL.

Používaj synthetic credentials, redacted representations a domain matchers. Recorded HTTP cassettes sa sanitizujú a reviewujú ako repository content.

## 32. Diagnostický workflow

Keď test s double zlyhá alebo podozrivo prejde:

1. pomenuj behavior a failure boundary;
2. zobraz real/double mapu;
3. urči rolu double-u v tomto teste;
4. skontroluj, ktoré semantics sľubuje;
5. over state versus interaction oracle;
6. skontroluj matchers, count a strictness;
7. pri async teste pozri scheduler, clock a pending work;
8. porovnaj configured response s provider contractom;
9. spusti conformance alebo real integration test;
10. uprav fidelity alebo scope podľa root cause;
11. zachovaj redigované first-failure artifacts;
12. pridaj vyšší dôkaz pre blind spot.

## 33. Referenčné pravidlá

- Double sa vyberá podľa failure boundary, nie framework convenience.
- Pred testom je explicitná real/double mapa.
- Použi najjednoduchší double s dostatočnou fidelity.
- State-based verification je default, keď je výsledok pozorovateľný.
- Interaction assertions chránia iba významný boundary contract.
- Matchers kontrolujú business fields, nie celý náhodný object graph.
- Call count má behavior dôvod.
- Async test používa completion condition, nie fixed sleep.
- Clock a scheduler sú odlišné mechanisms.
- In-memory repository nenahrádza database integration test.
- Fake deklaruje podporované a nepodporované semantics.
- Conformance chráni proti driftu.
- Reálna ephemeral dependency môže byť najjednoduchšia voľba.
- Failure logs nesmú odhaliť secrets.

## 34. Časté omyly

### „Každá dependency má byť mock“

Relevantné transaction, protocol a network semantics by sa stratili.

### „Mock dokazuje integráciu“

Dokazuje iba behavior subjectu voči naprogramovaným expectations.

### „In-memory database sa správa ako PostgreSQL“

Constraints, isolation, locking, collation a precision môžu byť zásadne odlišné.

### „Viac call assertions znamená presnejší test“

Často znamená väčší coupling na interný execution order.

### „Timeout znamená, že side effect nenastal“

Pri network boundary môže mať timeout unknown outcome.

### „Fake netreba testovať“

Fake potrebuje conformance pre všetky semantics, ktoré sľubuje.

### „Pevný sleep stabilizuje async mock“

Sleep nevytvára completion contract a mení sa s loadom runnera.

### „Sandbox stačí pre všetky testy“

Je pomalší, menej deterministický a nemusí umožniť všetky failure paths. Patrí do vrstveného portfólia.

## 35. Zhrnutie

Atlas double evidence chain je:

```text
behavior/risk
→ subject a boundary
→ real/double map
→ stub/fake/spy/mock role
→ controlled input/time/failure
→ state + významná interaction
→ conformance a drift protection
→ real integration/contract/sandbox evidence
```

Hlavný princíp je fidelity s priznanými blind spots. Double je správny vtedy, keď zrýchli a spresní dôkaz bez odstránenia semantics, v ktorých môže relevantná chyba vzniknúť.

## 36. Kontrolné otázky

1. Aký decision lifecycle riadi výber test double-u?
2. Čo je seam a prečo má zodpovedať architektúre?
3. Ako sa líši dummy, stub, fake, spy a mock?
4. Prečo je state verification preferovaný default?
5. Kedy je interaction assertion súčasťou contractu?
6. Ako sa navrhuje matcher pre payment request?
7. Kedy má význam call count alebo strict mock?
8. Ako sa testuje async behavior bez sleepu?
9. Prečo treba oddeliť wall clock, monotonic time a scheduler?
10. Aký unknown outcome môže vytvoriť network timeout?
11. Prečo payment fake vytvoril duplicate authorization failure?
12. Prečo in-memory repository neodhalil tenant collision?
13. Čo musí deklarovať broker alebo cloud fake?
14. Ako conformance suite obmedzuje contract drift?
15. Kedy je reálna ephemeral dependency lepšia než fake?
16. Ako sa izoluje mutable double pri paralelných testoch?

## Glossary impact

Relevantné pojmy: test double, seam, real/double boundary map, dummy, stub, fake, spy, mock, state-based verification, interaction-based verification, strict mock, matcher, fake clock, virtual scheduler, unknown outcome, service virtualization, simulator, emulator, sandbox, conformance test, contract drift a over-specification.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Code coverage a quality gates](code-coverage-and-quality-gates.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Flaky tests a test data →](flaky-tests-and-test-data.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
