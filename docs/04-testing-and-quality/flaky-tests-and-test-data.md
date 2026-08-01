# Flaky tests a test data

Flaky test má pri rovnakom zamýšľanom subjecte a inputs premenlivý výsledok. Môže striedavo prejsť a zlyhať bez relevantnej zmeny product code-u. Flakiness ničí dôveru v gate a často vedie k nebezpečnému rerun-until-green behavioru.

Typické zdroje:

```text
čas a race conditions
shared mutable state
poradie testov
neizolované ports/files/databáza
externá dependency
náhodnosť bez uloženého seedu
timezone alebo locale
nedostatočné čakanie na eventual consistency
```

`Sleep(5)` nie je synchronization contract. Test má čakať na pozorovateľnú podmienku s deadline-om a pri failure zachovať timeline. Polling bez limitu zase vytvára hanging suite.

Test data musí byť unikátne, izolované a vlastnené testom. Shared account alebo pevný order ID vytvára konflikty pri paralelnom behu. Disposable database schema, tenant alebo namespaced identifier znižuje coupling.

Neutrálny príklad: dva testy používajú rovnaký email. Jeden usera vytvorí, druhý očakáva, že neexistuje. Samostatne prejdú, paralelne sú nondeterministické. Oprava nie je retry, ale unikátny test subject a cleanup.

Quarantine dočasne odstráni flaky test z blocking gate-u, ale musí mať ownera, incident, expiry a viditeľnú metriku. Inak sa stane trvalým cintorínom failures.

Retry môže byť diagnostický signál, nie pass override. First-attempt pass rate a počet retry treba zachovať. Test, ktorý prejde na tretí pokus, je stále flaky evidence.

Failure artifacts zahŕňajú seed, timestamps, thread dumps, logs, screenshots, network trace a environment identity. Bez nich sa intermittent failure ťažko lokalizuje.

Test data management musí rešpektovať privacy a retention. Production data sa nemá nekontrolovane kopírovať do test environmentu; používa sa syntetická alebo anonymizovaná reprezentatívna data sada.

## 1. Cieľ kapitoly

Nosný model kapitoly je:

```text
rovnaký kandidát, rozdielny verdict
→ zachovať prvý failure a provenance
→ klasifikovať test/product/environment/orchestration
→ inventarizovať deklarované a skryté vstupy
→ nájsť prvý odlišný observation point
→ reprodukovať riadeným experimentom
→ odstrániť nondeterministic boundary alebo product race
→ overiť serial/parallel/random-order stabilitu
→ obnoviť blocking dôveru a odstrániť quarantine/retry
```

Test data sú súčasťou toho istého modelu. Fixture bez identity, ownershipu, schema version a cleanup contractu je skrytý vstup, ktorý môže meniť verdict iného testu.

## 2. Nosný scenár: Atlas export journey

Atlas E2E test vykonáva:

```text
vytvoriť tenant a zákazníka
→ seednúť objednávky
→ POST /exports
→ worker načíta tenant-scoped rows
→ vytvorí CSV object
→ API vráti signed download URL
→ test overí rows, tenant a audit
→ cleanup resources
```

Suite beží v ôsmich paralelných shards. Každý test má deklarovane používať vlastný tenant, queue namespace, object prefix a fixture dataset.

Po niekoľkých týždňoch sa objavia tri signatures:

1. timeout pri čakaní na `EXPORT_READY`;
2. CSV niekedy obsahuje jednu cudziu objednávku;
3. cleanup občas zmaže object, ktorý ešte používa iný test.

Tieto failures nemajú automaticky rovnaký root cause. Potrebujú spoločný evidence lifecycle.

## 3. Determinism contract

Reprodukovateľný test explicitne identifikuje vstupy:

- source a immutable artifact;
- test code, config a framework;
- fixture, schema a migration version;
- tenant/resource IDs;
- clock, timezone a locale;
- random a order seed;
- concurrency a shard;
- OS/runtime/tool versions;
- CPU, memory a quota limits;
- external dependency version a state;
- feature flags;
- orchestration attempt.

„Rovnaký test“ bez týchto údajov môže v skutočnosti znamenať iný dataset, environment, order alebo dependency contract.

## 4. Štyri kategórie premenlivého failure

### Test flakiness

Test používa fixed sleep, shared mutable state, unstable selector, globálny mock alebo neizolované dáta. Product behavior môže byť správny, ale oracle alebo setup je nekontrolovaný.

### Intermittent product defect

Test korektne odhaľuje race, lost update, duplicate side effect, startup race alebo resource leak v aplikácii. Označiť ho za flaky test by skrylo reálnu regresiu.

### Environment instability

Runner, network, storage, broker alebo shared sandbox poruší deklarovaný environment contract. Výsledok nie je validný product verdict, ale nie je ani green.

### Orchestration failure

Test sa nespustil, použil nesprávny artifact, stratil fixture alebo CI zle agregoval výsledok. Ide o incomplete execution evidence.

Rerun môže zmeniť symptóm, ale neklasifikuje príčinu.

## 5. First-attempt evidence

Prvý failure je najcennejší, pretože obsahuje pôvodný timing a state. Uchovaj:

- candidate a attempt identity;
- exact test a shard;
- fixture/dataset provenance;
- seed a execution order;
- structured logs a timeline;
- request, correlation a trace ID;
- last observed state;
- resource metrics;
- pending tasks/queues;
- screenshot, browser alebo network trace podľa scope-u;
- setup a cleanup status.

Rerun nesmie prepísať prvé artifacts ani zmeniť výsledok na obyčajný green.

## 6. Fixed sleep nevytvára synchronizáciu

```python
time.sleep(5)
assert export.status == "READY"
```

Sleep čaká na čas, nie na stav. Na rýchlom runneri plytvá časom; na preťaženom je príliš krátky. Zvýšenie na 30 sekúnd iba zníži frekvenciu failure.

Condition-based wait:

```text
poll diskriminačný observation point
→ skonči pri success condition
→ skonči pri terminal failure
→ skonči pri deadline
→ pri failure ulož posledný state a timeline
```

Polling interval musí rešpektovať latency a náklad observationu. Busy polling môže sám vytvoriť load.

## 7. Eventual consistency a míľniky

Atlas export má viac stavov:

```text
request accepted
→ DB job committed
→ event published
→ worker claimed event
→ query completed
→ object written
→ state READY
→ download visible
```

HTTP `202` nie je dôkaz finálneho exportu. Oracle musí pomenovať konkrétny terminal state a deadline.

Ak timeout nastane, artifacts majú ukázať posledný dosiahnutý míľnik. To odlíši chýbajúci event, worker backlog, storage failure a pomalý read model.

## Ako rozlíšiť flaky test od skutočného defectu

Flaky test vracia odlišný verdikt nad rovnakým deklarovaným subjectom bez relevantnej zmeny vstupov. Príčina však nemusí byť iba v teste. Nedeterministické môže byť aj produkčné správanie, race condition, eventual consistency alebo resource pressure. Automatický retry, ktorý druhý pokus označí za success, zničí first-attempt evidence a môže skryť skutočný defect.

Vyšetrovanie začína exact identitou runu: source revision, artifact, environment, seed, time, test data, dependency versions a worker. Prvý neúspešný pokus sa zachová spolu s logs, trace, screenshotom a state read-backom. Až potom možno porovnávať opakované behy a hľadať meniacu sa premennú.

Častým zdrojom flakiness je čas. Test, ktorý čaká pevné dve sekundy, predpokladá scheduler a dependency latency. Lepší test čaká na explicitnú podmienku s deadline a pri timeout-e vypíše posledný observed state. Hodiny sa pri domain logike injektujú; integračný test zaznamená timezone a clock source.

Test data potrebuje unikátnu identity a lifecycle. Zdieľaný tenant, globálny feature flag alebo opakovane používaný order ID vytvára interference medzi paralelnými runmi. Setup má byť idempotentný alebo vytvoriť nový izolovaný subject; cleanup nesmie zmazať evidence skôr, než sa failure klasifikuje. Pri produkčných synthetics sa používajú jasne označené účty a bezpečné business operácie.

Quarantine môže dočasne zabrániť blokovaniu delivery, ale nie je opravou. Musí mať ownera, deadline a viditeľný stav. Required security alebo data-integrity control sa nemá jednoducho vypnúť; pipeline môže oddeliť `TEST_DEFECT`, `PRODUCT_DEFECT` a `ENVIRONMENT_ERROR`, no každý stav potrebuje reakciu a návrat do dôveryhodného gate-u.

## 8. Worked failure: rerun skryl product race

Atlas test niekedy timeoutol pri `EXPORT_READY`. Automatický retry testu prešiel, preto bol označený ako flaky.

Timeline prvého attemptu:

```text
export job committed
→ event published
→ worker spracoval event
→ object upload dokončený
→ worker zapísal READY
→ cleanup scheduler označil starý job ako expired
→ status sa zmenil na EXPIRED pred polling probe
```

Druhý attempt použil nový job a prešiel.

### Root cause

Išlo o product race medzi completion a expiry schedulerom. Test nebol chybný; fixed polling interval iba menil pravdepodobnosť pozorovania krátkeho `READY` state-u.

### Náprava

- expiry sa počíta od completion timestampu, nie creation timestampu;
- state transition používa optimistic concurrency;
- test má controllable clock a scheduler;
- regression test reprodukuje interleaving;
- E2E wait prijíma stabilný terminal contract;
- auto-rerun už neklasifikuje failure ako test flake.

## 9. Time ako viacero vstupov

Test rozlišuje:

```text
wall clock
→ timestamp, expiry, kalendár

monotonic time
→ elapsed duration a deadline

scheduler
→ execution due work

timezone/locale
→ reprezentácia a business calendar
```

Fake clock bez controllable scheduleru nemusí reprodukovať production timer semantics. Test explicitne advances time a spúšťa due tasks.

Relevantné boundaries sú DST, koniec mesiaca, leap day, token expiry a clock skew medzi komponentmi.

## 10. Randomness a property-based failure

Randomizovaný test pri failure uloží:

- seed;
- konkrétny generated input;
- minimalizovaný counterexample;
- generator/framework version;
- parameters;
- test-order seed.

Seed sám nemusí stačiť po zmene generator algorithmu. Konkrétny input sa stáva trvalou regression fixture.

## 11. Order dependence

Order-dependent test používa state z predecessor testu alebo po sebe neobnoví global state. Odhaľovanie:

```text
run alone
vs full suite
vs reversed order
vs randomized order
vs different shard
vs clean/reused process
```

Root cause býva database row, cache, environment variable, singleton, monkey patch, fake clock alebo feature flag, ktoré test nevlastní alebo neobnoví.

## 12. Parallel ownership

Každý test/run vlastní resources:

- tenant alebo database/schema;
- object prefix;
- queue/topic namespace;
- temp directory;
- OS-assigned port;
- test identity;
- feature-flag namespace;
- cleanup label a TTL.

Unique name sa nesmie spoliehať iba na krátky timestamp. Platform truncation, case folding a normalizácia môžu vytvoriť collision.

## 13. Worked failure: truncation spojila dva tenanty

Atlas generoval tenant ID:

```text
test-{branch}-{shard}-{random}
```

Platforma povolila iba 24 characters a helper string ticho skrátil. Dve dlhé branch names mali rovnaký prvý prefix.

```text
run A tenant → test-feature-export-retr
run B tenant → test-feature-export-retr
→ shared rows a object prefix
→ cross-run CSV contamination
→ cleanup A odstránil objects runu B
```

### Root cause

Resource identity nebola collision-resistant po platform normalization a cleanup neoveroval ownership token.

### Náprava

- ID používa krátky stable hash celého run/test identity;
- helper po normalization kontroluje uniqueness budget;
- každý resource obsahuje immutable owner label a random nonce;
- cleanup vyžaduje zhodu run ID aj namespace allowlistu;
- collision test pokrýva truncation a case folding;
- failure artifacts ukladajú resolved platform IDs.

## 14. Port a readiness race

Hardcoded port koliduje medzi workers. Preferuj bind na port `0` a odovzdanie skutočnej hodnoty klientovi.

```text
process started
≠ socket listening
≠ dependency initialized
≠ relevant request spracovateľný
```

Readiness probe má overiť najnižšiu podmienku potrebnú pre testovaný request. Log line alebo process existence môže prísť pred skutočnou pripravenosťou.

## 15. Environment saturation

Timeout koreluj s metrics:

- CPU throttling;
- memory pressure/OOM;
- file-descriptor usage;
- connection-pool wait;
- DB lock contention;
- disk I/O queue;
- broker lag;
- ephemeral ports;
- rate limit;
- artifact upload queue.

Ak failures rastú s paralelizmom, zvýšenie timeoutu môže skryť nedostatočnú environment capacity. Test environment má vlastný capacity contract.

## 16. External dependencies

Shared sandbox alebo verejný internet prináša nekontrolované inputs. Ak je dependency súčasťou rizika, contract obsahuje:

- version a endpoint;
- test tenant/credentials;
- availability a rate limits;
- data ownership;
- cleanup;
- allowed parallelism;
- failure classification;
- fallback/quarantine policy.

Rýchle suites používajú local simulator alebo emulator; periodický sandbox test kontroluje drift. Shared dependency failure zostáva viditeľný ako environment/dependency failure.

## 17. Test data lifecycle

Test data prechádzajú:

```text
scenario contract
→ fixture/factory/generator design
→ schema a version
→ isolated allocation
→ precondition verification
→ test execution
→ diagnostic provenance
→ cleanup alebo TTL
→ privacy a retention audit
```

Dáta majú byť minimálne, reprezentatívne a vlastnené konkrétnym runom.

## 18. Hand-crafted fixtures

Ručná fixture je vhodná, keď každý field nesie význam. Atlas authorization fixture explicitne ukáže:

```text
requester tenant A
resource tenant B
role export_reader
expected DENY
```

Veľký JSON s desiatkami defaults skrýva preconditions a je krehký pri schema evolution. Preferuj malú fixture alebo builder s explicitnými overrides.

## 19. Factory a builder contract

Dobrá factory:

- vytvára validný minimálny default;
- zobrazuje critical fields;
- podporuje explicitné overrides;
- používa reprodukovateľnú identity;
- nevytvára veľký graph bez potreby;
- má versionovaný schema contract.

„Magická“ factory, ktorá automaticky vytvorí tenant, permissions, inventory a flags, môže obísť boundary, ktorú test mal vykonať.

## 20. Golden files a snapshots

Snapshot je oracle iba vtedy, keď diff zostáva reviewovateľný. Stabilizuj ordering, timestamps, IDs, encoding, paths a serializer version.

`Update all snapshots` pri failure ruší oracle. Baseline sa mení po pochopení behavior change a explicitnom reviewe.

## 21. Synthetic datasets

Synthetic data modelujú distributions a edge cases bez kopírovania reálnych osôb. Performance alebo migration test môže potrebovať:

- hot keys;
- skewed tenant sizes;
- Unicode/locale variants;
- sparse a dense records;
- long-tail payloads;
- historical schema versions.

Uniform random data často nereprezentujú production risk. Generator version, seed a parameters patria do provenance.

## 22. Production-derived data

Production-derived data sú vysokorizikové. Non-production environment ani private repository neodstraňujú privacy a security povinnosti.

Potrebné sú data minimization, schválenie, anonymization/pseudonymization, re-identification assessment, secret removal, access control, encryption, retention, deletion a audit prenosu.

Maskovanie niekoľkých columns nemusí zabrániť re-identification cez kombináciu quasi-identifiers.

## 23. Fixture provenance

Failure evidence obsahuje:

- fixture/dataset version;
- schema a migration version;
- factory/generator version;
- seed a parameters;
- anonymization version;
- test-created IDs;
- environment, tenant a shard;
- creation timestamp;
- owner/cleanup labels.

Bez provenance môže rovnaký fixture name po zmene znamenať iný input.

## 24. Database isolation

Voľba závisí od test scope-u:

```text
transaction rollback
schema/database per worker
disposable container
snapshot restore
immutable seed + unique rows
owned cleanup podľa run labelu
```

Rollback neizoluje async worker na inom connection ani committed outbox event. Testujúci transaction semantics nemôže obísť commit iba kvôli cleanup convenience.

## 25. Setup lifecycle

Setup má vlastný verdict:

```text
allocate namespace
→ start dependencies
→ wait for readiness
→ create fixture
→ verify preconditions
→ execute action
```

Ak fixture creation zlyhá, test nemá reportovať product assertion failure. `SETUP_FAILED` alebo `ENVIRONMENT_FAILED` je odlišný evidence state.

## 26. Idempotentný setup

Job môže byť retried po unknown outcome. Setup zvládne:

- resource už existuje;
- create commitol, response sa stratila;
- partial dependency set;
- rovnaký run ID sa spustil znova;
- predchádzajúci cleanup neprebehol.

Použi unique identity alebo reconcile semantics. „Delete everything“ môže zasiahnuť paralelný run.

## 27. Cleanup ownership

Cleanup používa:

- immutable run/test owner label;
- environment allowlist;
- namespace prefix/hash;
- compare-before-delete;
- teardown v `finally`;
- fallback cleanup job;
- TTL;
- orphan dashboard.

Artifacts sa zachovajú pred odstránením stavu. Cleanup failure je samostatný failure a môže kontaminovať ďalšie runs.

## 28. Resource leaks

Dlhá suite môže degradovať kvôli neuzavretým sockets, processes, containers, DB connections, files, threads alebo subscriptions.

Diagnostika porovná:

```text
clean process
vs test po stovkách predecessors
vs repeated suspect test v jednom procese
```

Sleduje resource counters a owner IDs. Leak môže byť v teste aj produkte.

## 29. Retry ako diagnostika, nie greenwashing

Retry uchová:

- attempt number;
- first failure signature;
- artifacts každého attemptu;
- candidate a inputs;
- environment changes;
- pass-after-retry status.

```text
PASS_FIRST
FAIL_THEN_PASS
FAIL_REPEATED
INFRA_INCOMPLETE
```

Finálny pipeline pass rate nesmie zlučovať `PASS_FIRST` a `FAIL_THEN_PASS`.

## 30. First-attempt pass rate

First-attempt pass rate je podiel executions bez retry. Sleduj aj:

- recovery-on-retry rate;
- repeated failure rate;
- failure signatures;
- duration variability;
- shard/environment correlation;
- ownera a age;
- quarantine count.

Test, ktorý pravidelne prejde až na tretí pokus, nie je zdravý green test.

## 31. Quarantine lifecycle

Quarantine dočasne odstráni nedôveryhodný signal z blocking decisionu. Test zostáva spustený a viditeľný.

Potrebuje:

- issue a ownera;
- failure signature a klasifikáciu;
- expiry/SLA;
- náhradné krytie rizika;
- retained artifacts;
- exit criteria;
- pravidelný report.

Nequarantinuj pravdepodobný kritický product race bez compensating controlu. Quarantine je containment gate-u, nie root-cause fix.

## 32. Stabilizačný experiment

Po oprave nestačí jeden rerun. Experiment môže kombinovať:

```text
reproducer pred fixom
→ serial repeated runs
→ parallel repeated runs
→ randomized order
→ clean/reused process
→ resource-pressure variant
→ observation window first-attempt rate
```

Počet runs závisí od pôvodnej failure probability a impactu. Výsledok musí podporiť explicitné exit criteria.

## 33. Exit criteria

Quarantine/retry sa odstráni, keď:

- root cause je preukázaný;
- reproducer pred fixom zlyhá správnym mechanizmom;
- fix odstráni skrytý input alebo product race;
- serial a parallel runs sú stabilné;
- random order neodhalí dependency;
- cleanup a duration sú zdravé;
- first-attempt pass rate sa obnoví;
- regression control ostáva v najnižšom spoľahlivom scope-e.

## 34. Failure artifacts

Podľa vrstvy uchovaj:

- stdout/stderr a structured logs;
- timestamps a event timeline;
- seed a order seed;
- screenshot/video/browser trace;
- network trace;
- process/container logs;
- resource metrics;
- environment/tool versions;
- fixture provenance;
- resolved resource IDs;
- pending tasks a last observed state;
- setup/cleanup verdict.

Artifacts sú redigované a dostupné ownerovi bez secrets.

## 35. Root-cause workflow

1. Zachovaj first-attempt evidence a candidate identity.
2. Rozlíš assertion, setup, cleanup, environment a orchestration failure.
3. Over, či test neodhaľuje product intermittency.
4. Reprodukuj rovnakú fixture, seed, order a environment.
5. Porovnaj test alone/full-suite a serial/parallel.
6. Nájdite shared state a resource ownership.
7. Nahraď fixed sleep condition waitom, nie vyšším sleepom.
8. Koreluj timeout s queue/resource metrics.
9. Over clock, scheduler a eventual-consistency milestone.
10. Skontroluj ID normalization a cleanup scope.
11. Oprav root cause a pridaj regression test.
12. Vykonaj stabilizačný experiment a odstráň temporary retry/quarantine.

## 36. Referenčné pravidlá

- Premenlivý verdict znamená skrytý input alebo intermittent product behavior.
- Rerun neklasifikuje root cause.
- First-attempt evidence sa nikdy neprepisuje.
- Fixed sleep nie je synchronizácia.
- Async oracle má condition, terminal failures a deadline.
- Test resources majú collision-resistant identity a ownership.
- Setup, product assertion a cleanup majú odlišné verdicts.
- Fixture a generator majú versionovanú provenance.
- Production-derived data sú vysokorizikové.
- Cleanup používa allowlist a compare-before-delete.
- Environment saturation sa rieši capacity evidence, nie iba timeoutom.
- Pass-after-retry zostáva flaky signal.
- Quarantine má ownera, expiry a náhradný control.
- Jeden zelený rerun nie je stabilizačný dôkaz.

## 37. Časté omyly

### „Rerun prešiel, bola to chyba testu“

Intermittent product race môže prejsť na druhý pokus.

### „Predĺžme sleep“

Mení pravdepodobnosť failure, nie synchronization contract.

### „Unikátny prefix z branch name stačí“

Truncation, normalization a paralelné attempts môžu vytvoriť collision.

### „Transaction rollback vyrieši všetky test data“

Async workers a committed side effects môžu používať iné connections a boundaries.

### „Quarantine vyriešila pipeline“

Iba odstránila signal z blocking decisionu. Risk potrebuje náhradné krytie a root-cause fix.

### „Production data sú realistickejšie“

Môžu vytvoriť privacy incident a stále nereprezentovať potrebné edge cases.

### „Cleanup failure môžeme ignorovať“

Kontaminuje ďalšie tests, resources a náklady.

## 38. Zhrnutie

Atlas flakiness a data chain je:

```text
candidate + declared inputs
→ isolated fixture a owned resources
→ controlled time/order/concurrency
→ condition-based observation
→ first-attempt verdict a artifacts
→ classify hidden boundary
→ root-cause experiment
→ fix + regression
→ stability evidence
→ remove retry/quarantine
```

Hlavný princíp je, že testovací verdict je produktom celého test systemu. Kód testu, orchestration, data lifecycle, environment capacity a cleanup sú rovnako súčasťou dôkazu ako samotný assertion.

## 39. Kontrolné otázky

1. Čo presne znamená flaky test?
2. Ako sa líši test flakiness, product intermittency, environment a orchestration failure?
3. Aké vstupy musí obsahovať determinism contract?
4. Prečo first-attempt evidence nemožno prepísať rerunom?
5. Prečo fixed sleep nevytvára synchronization?
6. Ako eventual-consistency milestones zlepšujú diagnostiku?
7. Prečo Atlas timeout v skutočnosti odhalil product race?
8. Ako sa odhaľuje order dependence?
9. Ako truncation vytvorila shared tenant a cleanup collision?
10. Čo musí vlastniť paralelný test?
11. Ako environment saturation mení timeout interpretation?
12. Aký lifecycle majú test data?
13. Kedy použiť fixture, factory, snapshot alebo synthetic dataset?
14. Prečo production-derived data zostávajú rizikové?
15. Ako sa líši setup failure od product failure?
16. Aké vlastnosti má bezpečný cleanup?
17. Čo meria first-attempt pass rate?
18. Aký contract musí mať quarantine?
19. Aké exit criteria dokazujú stabilizáciu?

## Glossary impact

Relevantné pojmy: flaky test, intermittent product defect, hidden input, determinism contract, condition-based waiting, eventual consistency, test isolation, resource ownership, fixture provenance, synthetic data, production-derived data, first-attempt pass rate, pass-after-retry, quarantine, cleanup ownership, stabilization experiment a failure signature.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Mocks, stubs a fakes](mocks-stubs-fakes.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Shift-left →](shift-left.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
