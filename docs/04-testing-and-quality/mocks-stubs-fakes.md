# Mocks, stubs a fakes

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Testing and Software Quality
- Predpoklady: [Unit, integration a component tests](unit-integration-component-tests.md), [Contract a API tests](contract-and-api-tests.md)
- Súvisiace témy: test double, seam, state verification, interaction verification, conformance, service virtualization, deterministic time, contract drift

## 1. Mentálny model

Test double je kontrolovaná náhrada dependency použitá preto, aby test vedel riadiť vstupy, simulovať konkrétny failure alebo pozorovať boundary interaction. Double nie je cieľom testu; je nástrojom na vytvorenie správneho scope-u a deterministického dôkazu.

```text
správanie, ktoré chceme overiť
→ určiť relevantnú boundary
→ rozhodnúť, čo musí byť reálne
→ zvoliť najjednoduchší vhodný double
→ riadiť vstupy alebo zaznamenať interakcie
→ overiť observable result
→ potvrdiť realitu vo vyššej vrstve
```

Nadmerné používanie doubles môže vytvoriť rýchlu a zelenú suite, ktorá testuje iba vlastné predpoklady. Nedostatočná izolácia môže naopak zmeniť každý unit test na pomalý a flaky integračný test.

## 2. Test seam

Seam je miesto, kde možno produkčné správanie nahradiť alebo riadiť bez zmeny testovaného business contractu. Môže to byť interface, function parameter, dependency injection binding, process boundary, HTTP endpoint, clock provider alebo filesystem adapter.

Dobré seams sa typicky nachádzajú na hraniciach medzi čistou rozhodovacou logikou a nondeterministickým alebo drahým svetom:

- čas a timezone;
- randomness a ID generation;
- sieť a externé API;
- databáza alebo message broker;
- filesystem;
- credentials a secret provider;
- email, payment alebo notification gateway;
- operating-system process.

Seam nemá existovať iba kvôli testom, ak zhoršuje produkčný model. Kvalitná architektúra však už prirodzene oddeľuje domain decisions od I/O a vendor-specific adapters.

## 3. Taxonómia doubles

Pojmy dummy, stub, fake, spy a mock opisujú účel, nie konkrétny framework object. Jeden object môže v rôznych testoch plniť inú rolu.

```text
dummy → iba vyplní parameter
stub  → riadi prepared input alebo response
fake  → poskytuje zjednodušenú funkčnú implementáciu
spy   → zaznamenáva uskutočnené interactions
mock  → nesie očakávania na interactions
```

Presné pomenovanie pomáha review procesu. „Mock database“ môže v skutočnosti znamenať stub repository, in-memory fake alebo reálny ephemeral engine, pričom každá možnosť poskytuje iný dôkaz.

## 4. Dummy

Dummy je hodnota potrebná na zostavenie objectu alebo callu, ale testovaný path ju nepoužíva.

```python
service = ReportService(
    repository=repository,
    audit_context=unused_context,
)
```

Ak test začne závisieť od správania dummy objektu, prestáva byť dummy. Veľké množstvo dummy parametrov často signalizuje príliš široký constructor alebo nejasnú responsibility boundary.

## 5. Stub

Stub vracia vopred pripravené odpovede, aby test dostal konkrétny stav alebo failure.

```python
class UserRepositoryStub:
    def find(self, user_id: str) -> User | None:
        return User(id=user_id, active=True)
```

Stub sa používa na riadenie inputu testovaného behavioru. Typicky sa neoveruje počet interných volaní, pokiaľ interaction nie je súčasťou contractu.

Dobrý stub modeluje iba potrebné variants:

- resource existuje alebo neexistuje;
- dependency vráti timeout;
- token je expirovaný;
- API odpovie rate limitom;
- storage vráti conflict.

Stub, ktorý implementuje desiatky nezávislých behaviors, sa mení na fake alebo komplikovaný simulator.

## 6. Fake

Fake je funkčná, ale zjednodušená implementácia reálnej dependency. Môže udržiavať state a podporovať celý workflow.

Príklady:

- in-memory repository;
- fake clock s manuálnym posunom času;
- local object-store emulator;
- fake message bus;
- payment sandbox;
- deterministic ID generator.

Fake je užitočný, keď test potrebuje behavior bohatší než pripravený stub, ale reálna dependency je pomalá, drahá alebo nedostupná.

Najväčšie riziko je semantic drift. In-memory map môže umožniť behavior, ktorý PostgreSQL odmietne kvôli constraintu, isolation alebo collation. Fake preto musí explicitne deklarovať, ktoré vlastnosti modeluje a ktoré nie.

## 7. Spy

Spy zaznamenáva uskutočnené interactions a test ich vyhodnotí po vykonaní behavioru.

```python
publisher.publish(event)

assert publisher.events == [expected_event]
```

Spy môže obaliť fake aj reálnu implementáciu. Je vhodný, keď side effect nie je jednoducho pozorovateľný cez návratovú hodnotu, napríklad emitted event, audit record alebo notification request.

Interaction log má uchovávať iba údaje potrebné pre assertion. Zaznamenávanie celého interného object graphu zvyšuje coupling a môže neúmyselne ukladať secrets.

## 8. Mock

Mock nesie vopred definované očakávania na interakcie a test zlyhá, keď sa nenaplnia.

```text
pri úspešnom storne
→ refund gateway dostane presnú business sumu
→ event publisher odošle OrderCancelled
```

Mock je vhodný, keď samotná komunikácia tvorí observable contract. Príkladom je exactly-once side-effect attempt, zákaz odoslania emailu pri neautorizovanej operácii alebo povinné auditovanie security decisionu.

Mock nie je vhodný iba preto, že framework ho vie jednoducho vytvoriť. Ak test overuje každé interné volanie medzi vlastnými objects, refactoring implementácie rozbije test bez zmeny behavioru.

## 9. State-based verification

State-based test overuje výsledný output alebo stav po operácii.

```python
account.withdraw(10)
assert account.balance == 90
```

Výhodou je väzba na behavior, nie na interný postup. Test zvyčajne prežije refactoring, ktorý zachová výsledok.

State verification je preferovaný default, ak požadovaný výsledok možno spoľahlivo pozorovať. Pri distribuovaných side effects však nemusí byť výsledný stav dostupný v rovnakom scope-e alebo čase.

## 10. Interaction-based verification

Interaction-based test overuje komunikáciu cez boundary.

```python
payment_gateway.refund.assert_called_once_with(payment_id, amount)
```

Je vhodný, keď:

- side effect je samotným contractom;
- nesmie vzniknúť žiadne volanie;
- počet pokusov ovplyvňuje finančný alebo bezpečnostný dopad;
- poradie je protokolová požiadavka;
- output nie je v scope-e testu pozorovateľný.

Interaction assertions musia rozlišovať nevyhnutný contract od incidental implementation detailu. To, že helper volá logger pred repository, spravidla nie je business požiadavka.

## 11. State a interaction sa dopĺňajú

Niektoré testy potrebujú oba druhy dôkazu. Pri vytvorení objednávky možno overiť výsledný domain state aj emitted event.

```text
state assertion
→ objednávka je v stave accepted

interaction assertion
→ publikoval sa OrderAccepted s rovnakým ID
```

Neoveruj tú istú skutočnosť dvakrát bez novej hodnoty. Ak fake event store poskytuje observable state, explicitné mock call count môže byť zbytočné.

## 12. Over-specification

Test je over-specified, keď vyžaduje viac detailov, než tvorí verejný alebo boundary contract.

Krehký príklad:

```text
A volaná presne raz
potom B presne dvakrát
potom C s konkrétnym interným DTO
```

Ak možno bezpečne batchovať calls, zmeniť poradie alebo nahradiť interné DTO bez zmeny výsledku, test blokuje refactoring.

Lepší assertion kontroluje:

- relevantný side effect nastal alebo nenastal;
- business fields majú správne hodnoty;
- idempotency identity je zachovaná;
- security-sensitive call používa správny principal;
- protocol-required order je dodržaný.

## 13. Strict a loose mocks

Strict mock zlyhá pri neočakávanej interaction. Loose mock nešpecifikované calls ignoruje alebo vracia defaults.

Strictness má zodpovedať riziku:

- **strict** — payment charge, privilege grant, destructive delete, external message publication;
- **targeted strictness** — overujú sa kritické calls, telemetry a incidental calls sa ignorujú;
- **loose** — experimentálny observer alebo nepodstatná dekoratívna dependency.

Príliš loose matcher môže skryť neočakávaný side effect. Príliš strict mock môže viazať test na nepodstatný execution order.

## 14. Argument matching

Matcher má kontrolovať properties, ktoré tvoria contract.

```text
order_id → musí presne sedieť
amount → musí presne sedieť
currency → musí sedieť
timestamp → musí byť v kontrolovanom intervale
trace_id → musí existovať, nie mať konkrétnu náhodnú hodnotu
```

`any()` pre celý request môže skryť chybný tenant alebo sumu. Exact equality celého objectu môže byť krehká kvôli timestampu, optional metadata alebo novému backward-compatible fieldu.

Používaj domain-oriented matchers a jasné failure messages.

## 15. Call count semantics

Call count má zmysel iba vtedy, keď počet mení behavior alebo riziko.

- **presne raz** — financial charge alebo idempotentný event publication contract;
- **nikdy** — notification po zamietnutej authorization;
- **aspoň raz** — zriedkavo vhodné; môže skryť retry storm;
- **najviac N-krát** — bounded retry contract;
- **poradie** — iba ak je protokolovo významné.

Pri retries treba overiť aj časovanie, klasifikáciu retryable errors a zastavenie po deadline. Samotné `called_three_times` nepreukazuje správny retry policy.

## 16. Asynchrónne interactions

Async callbacks, event publication a background tasks vyžadujú deterministické čakanie. Test nemá používať pevný sleep a následne čítať spy log.

Lepšie možnosti:

- await completion future;
- controllable executor;
- in-memory queue s explicitným drain;
- condition polling s timeoutom;
- test scheduler;
- fake clock a manuálne spustenie scheduled tasks.

Failure artifact má ukázať posledný observed state, pending tasks a recorded interactions.

## 17. Time a clock

Priamy wall clock robí test závislý od reálneho času, timezone a boundary transitions. Clock seam umožní explicitne modelovať `now`.

```python
class Clock:
    def now(self) -> datetime:
        ...
```

Fake clock má podporovať:

- pevný čas;
- kontrolovaný advance;
- monotonic a wall-clock rozlíšenie podľa potreby;
- expiry a lease scenarios;
- daylight-saving a timezone cases;
- scheduled retry alebo backoff.

Posun fake clocku sám osebe nemusí spustiť background scheduler. Test musí explicitne modelovať aj execution mechanism.

## 18. Randomness a IDs

Seedovaný random generator zlepšuje reprodukovateľnosť, ale seed nie je vždy vhodný contract pre business test. Pri ID generation je často lepší explicitný deterministic provider.

Property-based test má pri failure uložiť seed alebo minimalizovaný counterexample. Regression test následne môže použiť konkrétny reprodukčný vstup bez závislosti od sequence interných random calls.

Mockovanie každého `random()` callu podľa poradia je krehké. Preferuj vyšší abstraction contract, napríklad `generate_order_id()` alebo `choose_backoff_jitter()`.

## 19. Network a HTTP doubles

Mockovanie metódy HTTP clienta testuje decision logic, ale neoverí serialization, headers, timeout configuration ani response parsing. Local mock server alebo service virtualization prechádza reálnou protocol boundary a poskytuje vyššiu fidelity.

Kontrolovaný server má vedieť simulovať:

- connect timeout alebo refusal;
- read timeout;
- partial a pomalý stream;
- malformed payload;
- connection reset;
- redirects;
- 429 a `Retry-After`;
- retryable a non-retryable 5xx;
- duplicate alebo out-of-order events;
- stateful sequence odpovedí.

Mock server stále nie je skutočný provider. Contract tests a periodické sandbox tests musia kontrolovať drift.

## 20. Database fakes

In-memory repository je vhodný na domain unit tests, ak persistence semantics nie sú testovaným rizikom. Nesmie sa však vydávať za dôkaz PostgreSQL behavioru.

Rozdiely môžu zahŕňať:

- transactions a isolation;
- unique a foreign-key constraints;
- null semantics;
- collation a case sensitivity;
- locking a concurrency;
- generated IDs;
- query planner a index behavior;
- timezone a numeric precision.

Persistence contract potrebuje integration test s reálnym engine-om a kompatibilnou major verziou.

## 21. Message-broker fakes

Fake broker môže pomôcť unit alebo component testu, ale musí deklarovať, či modeluje:

- at-least-once delivery;
- redelivery;
- partition ordering;
- consumer groups;
- acknowledgement;
- visibility timeout;
- dead-letter behavior;
- retention a replay.

Jednoduchý in-memory list zvyčajne nemodeluje reálne failure modes. Broker integration test musí použiť skutočný engine alebo kvalitný emulator, keď je ordering, durability alebo redelivery súčasťou rizika.

## 22. Simulátor a emulator

Simulator napodobňuje behavior na úrovni zvoleného modelu. Emulator sa snaží byť protokolovo alebo platformovo vernejší. Rozdiel nie je vždy striktne definovaný, preto treba opisovať konkrétnu fidelity.

Pri cloud emulátore over:

- podporované API a versions;
- consistency model;
- IAM a policy behavior;
- quotas a throttling;
- error model;
- rozdiely oproti managed service.

Lokálny emulator znižuje cenu feedbacku, ale nemôže byť jediným dôkazom pre platform-specific behavior.

## 23. Contract drift

Double driftuje, keď jeho behavior už nezodpovedá reálnej dependency. Drift môže byť neviditeľný, pretože consumer testy zostanú zelené.

Ochrany:

```text
shared schema alebo contract
→ conformance suite
→ spustiť proti fake aj real dependency
→ versionovať fake
→ dokumentovať nepodporované semantics
→ periodicky overovať sandbox
```

Provider-driven spec pomáha so syntaxou a typmi. Consumer-driven contracts pomáhajú s reálne používanými interactions. Ani jedno samo neoverí performance, quota alebo všetky runtime semantics.

## 24. Conformance testing fake-u

Fake má mať vlastnú test suite iba pre behavior, ktorý sľubuje modelovať. Rovnaké test fixtures možno spustiť proti fake a reálnej implementation.

```text
repository conformance suite
├─ save a read
├─ duplicate key
├─ missing entity
└─ optimistic concurrency
```

Ak fake nevie podporiť konkrétny contract, má zlyhať explicitne alebo byť v danom teste nepoužitý. Tiché zjednodušenie je horšie než priznaný limit.

## 25. Kedy použiť reálnu dependency

Reálna dependency je vhodnejšia, keď:

- je rýchlo a hermeticky spustiteľná;
- jej semantics sú hlavným rizikom;
- container alebo embedded server je jednoduchší než udržiavanie fake-u;
- potrebujeme reálny protocol, serializer, transaction alebo filesystem behavior;
- drift fake-u by bol drahý;
- failure sa dá stále dobre diagnostikovať.

Príklady sú PostgreSQL container, local HTTP server, skutočný parser, filesystem temp directory alebo ephemeral broker.

„Reálna“ dependency neznamená shared staging service bez kontroly. Hermetic ephemeral instance môže byť realistická aj deterministická.

## 26. Kedy použiť double

Double je vhodný, keď:

- testujeme lokálnu rozhodovaciu logiku;
- dependency je externá, drahá alebo nedostupná;
- potrebujeme reprodukovať zriedkavý failure;
- musíme riadiť čas, random alebo ID;
- reálny systém by vytvoril neželaný side effect;
- test potrebuje vysokú rýchlosť a presnú failure localization.

Voľba nie je binárna pre celý projekt. Jedna behavior class môže mať unit tests so stubom, component tests s mock serverom, contract tests a periodický sandbox test.

## 27. Reset a izolácia

Mutable double nesmie zdieľať state medzi testmi bez explicitného scope-u. Resetovať treba:

- prepared responses;
- recorded calls;
- fake database;
- queues a pending callbacks;
- virtual clock;
- random seed alebo generator;
- global configuration;
- captured credentials.

Preferuj novú instance per test. Globálny singleton mock vytvára order dependency a paralelné race conditions.

Cleanup má prebehnúť aj po assertion failure. Pri failure je však vhodné najprv zachovať diagnostický snapshot recorded state.

## 28. Secrets a sensitive data

Spy a mock framework môže logovať celé argumenty pri failure. Requesty môžu obsahovať tokens, personal data alebo payment details.

Používaj redacted representations, domain matchers a synthetic credentials. Failure artifact nemá vypísať celý secret iba preto, že argument equality zlyhala.

Test fixtures a recorded HTTP cassettes sa musia sanitizovať a reviewovať rovnako ako iný repository obsah.

## 29. Diagnostický workflow

Keď test s double zlyhá alebo podozrivo prechádza:

1. pomenuj behavior a boundary, ktoré test chráni;
2. over, či double plní rolu stubu, fake-u, spy alebo mocku;
3. skontroluj, či assertion overuje observable contract alebo implementation detail;
4. porovnaj configured response s reálnym contractom;
5. over reset state a paralelnú izoláciu;
6. skontroluj call order, count a matcher strictness;
7. pri async teste pozri pending work a scheduler state;
8. pri network fake-u over serialization a timeout boundary;
9. pri drift podozrení spusti conformance alebo real integration test;
10. zníž alebo zvýš fidelity podľa konkrétneho rizika.

## 30. Časté omyly

### „Každá dependency má byť mock“

Relevantné database, network alebo protocol semantics by sa stratili a suite by testovala vlastné assumptions.

### „In-memory database sa správa ako produkčná databáza“

Môže mať zásadne odlišné constraints, transactions, collation a concurrency.

### „Mock dokazuje, že integrácia funguje“

Mock dokazuje iba naprogramované expectations. Reálnu integráciu overí integration alebo contract test.

### „Viac interaction assertions znamená vyššiu presnosť“

Často to znamená väčší coupling na interný execution order.

### „Fake netreba testovať“

Fake potrebuje conformance pre semantics, ktoré sľubuje.

### „Pevný sleep stačí pre async mock“

Sleep nevytvára deterministický completion contract a vedie k flaky testom.

## 31. Prevádzkový checklist

- Je jasné, aké správanie a boundary test overuje?
- Používa test najjednoduchší double, ktorý poskytuje potrebný dôkaz?
- Sú relevantné semantics testované aj s reálnou dependency?
- Preferuje test state/output pred incidental interactions?
- Sú call count a order assertions business alebo protocol contract?
- Kontrolujú matchers významné fields bez `any()` nad kritickými dátami?
- Má fake explicitný conformance scope?
- Existuje ochrana proti contract driftu?
- Je time, random a async execution deterministicky riadený?
- Sú doubles izolované per test a bezpečné pre paralelný beh?
- Sú failure logs redacted?
- Je jasné, ktorá vyššia test layer potvrdzuje real integration?

## 32. Kontrolné otázky

1. Čo je test seam a prečo je dôležitejší než konkrétny mocking framework?
2. Aký je rozdiel medzi dummy, stub, fake, spy a mock?
3. Kedy preferovať state-based a kedy interaction-based verification?
4. Čo je over-specification a ako poškodzuje refactoring safety?
5. Kedy má význam strict mock?
6. Ako navrhnúť argument matcher pre business-critical request?
7. Prečo call count assertion potrebuje behavior dôvod?
8. Ako deterministicky testovať čas, random a async callbacks?
9. Prečo in-memory repository nenahrádza database integration test?
10. Ako sa zisťuje a obmedzuje contract drift fake-u?
11. Kedy je reálna ephemeral dependency lacnejšia než fake?
12. Ako zabrániť order-dependent failures zo shared mock state?

## Glossary impact

Relevantné pojmy: test double, seam, dummy, stub, fake, spy, mock, state-based testing, interaction-based testing, strict mock, matcher, fake clock, deterministic random, service virtualization, simulator, emulator, conformance test, contract drift a over-specification.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Code coverage a quality gates](code-coverage-and-quality-gates.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Flaky tests a test data →](flaky-tests-and-test-data.md)
<!-- KNOWLEDGE-NAVIGATION:END -->