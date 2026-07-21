# Flaky tests a test data

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

## 1. Flaky test

Flaky test pri rovnakom kóde a deklarovaných vstupoch niekedy prejde a niekedy zlyhá. Je to porucha testovacieho systému, nie bežná vlastnosť automatizácie.

Flakiness môže vzniknúť v:

- samotnom teste,
- testovanom systéme,
- prostredí,
- dátach,
- externých dependencies,
- CI orchestration.

## 2. Prečo je flakiness kritický problém

Vedie k:

- rerun-until-green,
- ignorovaniu reálnych regresií,
- dlhšiemu feedbacku,
- náhodným blokáciám,
- zníženiu dôvery v CI,
- bypassom quality gates,
- skrytým concurrency a timing chybám.

Test suite bez dôvery prestáva fungovať ako rozhodovací mechanizmus.

## 3. Hlavné príčiny

### Timing a race conditions

- fixed sleeps,
- nedokončená asynchronous operácia,
- polling bez deadline,
- race medzi setupom a consumerom,
- event ordering.

### Shared mutable state

- spoločná databáza,
- rovnaký user alebo resource name,
- global cache,
- shared filesystem path,
- singleton mock.

### Order dependence

Test prejde iba po inom teste alebo zlyhá pri inom poradí.

### Environment dependence

- timezone,
- locale,
- clock,
- CPU speed,
- filesystem order,
- network latency,
- port availability,
- OS differences.

### External dependencies

- rate limits,
- service outages,
- DNS,
- uncontrolled data,
- eventual consistency.

### Randomness

Nezaznamenaný seed alebo náhodný výber, ktorý nie je reprodukovateľný.

## 4. Fixed sleep anti-pattern

```python
time.sleep(5)
assert job.finished
```

Sleep je zároveň:

- príliš dlhý, keď systém reaguje rýchlo,
- príliš krátky, keď je CI pomalšie.

Preferuj condition-based wait s deadline:

```python
wait_until(lambda: job.finished, timeout=10)
```

Pri failure zachovaj posledný pozorovaný stav a timeline.

## 5. Eventual consistency

Test musí rozlišovať:

- operácia bola prijatá,
- stav sa propaguje,
- read model je aktualizovaný,
- side effect bol doručený.

Polling potrebuje:

- maximálny deadline,
- interval alebo backoff,
- jasnú terminal failure condition,
- diagnostický output.

Neobmedzený retry môže maskovať poruchu.

## 6. Deterministický čas

Testy nemajú nekontrolovane závisieť od wall clock. Používaj:

- injected clock,
- fixed instant,
- explicit timezone,
- monotonic clock pre durations,
- fake clock pre expiry a retry.

Testovanie presne o polnoci, DST prechodu alebo na konci mesiaca má byť zámerné, nie náhodné.

## 7. Randomness a seeds

Property-based alebo randomized test musí pri failure zaznamenať:

- seed,
- generated input,
- shrinknutý minimal failing example,
- tool/version.

Regression test má následne používať konkrétny reprodukčný prípad.

## 8. Paralelné testy

Paralelizácia odhalí skryté shared-state assumptions. Izoluj:

- database schema alebo tenant,
- resource names,
- ports,
- temp directories,
- queues/topics,
- environment variables,
- credentials.

Používaj unique names odvodené z run/test ID a garantovaný cleanup.

## 9. Port a network collisions

Nehardcoduj rovnaký port pre všetky tests. Preferuj:

- OS-assigned ephemeral port,
- isolated network namespace/container,
- per-test server lifecycle,
- readiness signal pred client requestom.

„Connection refused“ môže znamenať, že test poslal request skôr, než server začal počúvať.

## 10. Test data kategórie

### Hand-crafted fixtures

Malé explicitné dáta pre konkrétny scenár.

### Factories/builders

Generujú validný default objekt s možnosťou override relevantných polí.

### Golden alebo snapshot data

Versioned expected output pre komplexné reprezentácie.

### Synthetic datasets

Umelo generované dátové distribúcie bez reálnych osobných údajov.

### Production-derived data

Vyžadujú anonymizáciu, právny základ, obmedzenie scope a bezpečný lifecycle.

## 11. Test data factory

Dobrá factory:

- vytvára minimálny validný objekt,
- má stabilné defaults,
- umožňuje explicitné overrides,
- neskrýva kritické business vlastnosti,
- nevytvára náhodnosť bez seedu.

Príklad:

```python
user = user_factory(role="admin", active=False)
```

Test má ukazovať hodnoty relevantné pre scenár.

## 12. Fixtures a coupling

Veľká shared fixture môže spôsobiť:

- nejasný setup,
- závislosť na poradí,
- pomalé tests,
- neúmyselné prepojenie scenárov,
- ťažký cleanup.

Preferuj composable fixtures a lokálny ownership stavu.

## 13. Database isolation

Možnosti:

- transaction rollback,
- schema/database per test worker,
- container per suite alebo test,
- deterministic cleanup,
- immutable seed + unique test data.

Transaction rollback nemusí fungovať pre:

- async worker v inom connection,
- commit hooks,
- external side effects,
- testovanie transaction semantics.

## 14. Cleanup

Cleanup musí prebehnúť aj po failure. Používaj:

- `finally`,
- fixtures teardown,
- context managers,
- TTL/garbage collector pre orphan resources,
- run labels.

Cleanup failure sa nemá potichu ignorovať. Môže ovplyvniť ďalšie tests a náklady.

## 15. Idempotentný setup

Setup má bezpečne zvládnuť:

- resource už existuje,
- predchádzajúci run zlyhal,
- retry rovnakého jobu,
- partial creation.

Preferuj create-or-reconcile alebo unique isolated resource pred fragile shared resetom.

## 16. Quarantine

Quarantine dočasne odstráni flaky test z blocking gate-u, ale musí zachovať:

- pravidelné spúšťanie,
- viditeľný failure report,
- ownera,
- issue,
- expiry,
- prioritu opravy.

Quarantine bez expiry je trvalé vypnutie testu.

## 17. Retry policy

Automatický retry môže pomôcť diagnostike, ale nesmie prepísať prvý failure na success bez záznamu.

Sleduj:

- first-attempt pass rate,
- pass-after-retry rate,
- failure signature,
- test ownera.

Blocking decision môže byť dočasne založený na policy, ale flaky debt musí zostať viditeľný.

## 18. Flaky test detection

Metódy:

- opakované runs rovnakého commitu,
- randomizované test order,
- paralelné a serial porovnanie,
- environment matrix,
- failure clustering,
- historical pass/fail trend,
- first-attempt metriky.

Jednorazový zelený rerun nie je root-cause analýza.

## 19. Failure artifacts

Pri failure zachovaj:

- stdout/stderr,
- structured logs,
- timestamps,
- screenshots/video pri UI,
- network trace podľa potreby,
- test seed,
- environment metadata,
- resource IDs,
- relevantný state dump,
- junit/report file.

Artifact musí byť dostupný bez rerunu, ktorý môže problém odstrániť.

## 20. Flakiness metrics

Sleduj:

- first-run failure rate,
- retry recovery rate,
- flaky tests podľa ownershipu,
- quarantine age,
- mean time to repair,
- suite duration variability,
- failure reason distribution.

Celková pass rate môže zakryť veľa rerunov.

## 21. Test data privacy

Produkčné dáta v testoch predstavujú riziko. Ochrany:

- synthetic data ako default,
- anonymization/pseudonymization,
- data minimization,
- access control,
- retention a deletion,
- zákaz secrets,
- audit prenosu,
- oddelenie environmentov.

Maskovanie niekoľkých stĺpcov nemusí odstrániť re-identification riziko.

## 22. Test data versioning

Fixtures a schemas sa menia spolu so systémom. Versionuj:

- input fixtures,
- expected outputs,
- migrations,
- contract versions,
- generator version a seed.

Staršie fixtures sú užitočné pre backward compatibility a migration tests.

## 23. Typické omyly

### „Stačí test rerunúť“

Rerun môže maskovať reálny intermittent defect.

### „Test je flaky iba v CI“

CI môže odhaliť timing, isolation alebo resource problém skrytý lokálne.

### „Sleep zvýšime z 5 na 30 sekúnd“

Znižuje pravdepodobnosť, nie príčinu.

### „Quarantined test už neblokuje, problém je vyriešený“

Iba sa zmenil gate behavior.

### „Test data môžu byť production dump, repository je private“

Private repository ani test environment nie sú povolenie na kopírovanie citlivých dát.

### „Random test bez reprodukovateľného seedu je dostatočný“

Failure nebude spoľahlivo analyzovateľný.

## 24. Kontrolné otázky

1. Čo presne definuje flaky test?
2. Aké hlavné kategórie flakiness poznáš?
3. Prečo je fixed sleep problematický?
4. Ako testovať eventual consistency?
5. Ako izolovať paralelné tests?
6. Aký je rozdiel medzi fixture, factory a synthetic datasetom?
7. Kedy transaction rollback nestačí na database isolation?
8. Ako má fungovať quarantine lifecycle?
9. Aké metriky odhalia rerun-until-green kultúru?
10. Ako bezpečne používať production-derived test data?

## Glossary impact

Relevantné pojmy: flaky test, first-attempt pass rate, rerun-until-green, quarantine, test fixture, test data factory, synthetic data, production-derived data, deterministic clock, condition-based wait, eventual consistency, test isolation, cleanup a random seed.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Mocks, stubs a fakes](mocks-stubs-fakes.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
