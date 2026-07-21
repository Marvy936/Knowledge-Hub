# Continuous Integration

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Continuous Integration (CI) je pracovný a technický model, v ktorom vývojári často integrujú malé zmeny do spoločnej hlavnej línie a automatizovaný systém nad každou významnou zmenou vytvára reprodukovateľný build, spúšťa kontroly a poskytuje rýchly feedback.

CI nie je iba „server, ktorý spúšťa testy“. Je to kombinácia:

- krátkodobých branches alebo práce priamo na trunku,
- častej integrácie,
- automatizovaného buildu,
- dôveryhodných testov a statických kontrol,
- rýchleho odstránenia broken main,
- viditeľného výsledku pre celý tím.

## 2. Problém, ktorý CI rieši

Bez častej integrácie vznikajú:

- dlhodobé divergentné branches,
- veľké merge konflikty,
- skryté nekompatibility,
- pomalý feedback,
- nejasný vlastník integration failure,
- „integration phase“ tesne pred release.

CI skracuje vzdialenosť medzi:

```text
zmena
→ integrácia
→ dôkaz kvality
→ oprava
```

## 3. Hlavná línia

Main branch má reprezentovať najaktuálnejší integrovaný stav systému.

Praktické očakávania:

- build je reprodukovateľný,
- blocking checks prechádzajú,
- artifact možno jednoznačne identifikovať,
- failure je viditeľný,
- tím broken main prioritne opraví alebo revertne.

Main nemusí byť vždy automaticky nasadený do produkcie, ale má byť v stave vhodnom na ďalšiu delivery validáciu.

## 4. Frekvencia integrácie

CI preferuje malé a časté zmeny.

Výhody:

- menší diff,
- jednoduchší review,
- menší blast radius,
- rýchlejšia diagnostika,
- lacnejší rollback alebo revert,
- menej konfliktov.

Veľká zmena môže byť rozdelená pomocou:

- feature flags,
- branch by abstraction,
- backward-compatible schema zmien,
- dark code paths,
- postupného refactoringu.

## 5. Build pipeline

Základný CI flow:

```text
checkout
→ restore dependencies
→ compile/build
→ static checks
→ unit tests
→ integration/contract tests
→ package artifact
→ publish evidence
```

Poradie má maximalizovať rýchly useful failure. Lacné deterministické kontroly patria pred drahé testy.

## 6. Reprodukovateľný build

Rovnaké vstupy majú vytvoriť ekvivalentný výstup.

Kontroluj:

- pinned toolchain,
- dependency lock,
- explicitné environment variables,
- timezone a locale,
- deterministic timestamps podľa potreby,
- izolované build prostredie,
- identifikáciu source commit-u.

Build, ktorý funguje iba na konkrétnom notebooku, nie je dôveryhodný CI build.

## 7. Build once

Odporúčaný princíp:

```text
commit
→ jeden build
→ immutable artifact
→ ďalšie testovanie a promotion toho istého artifactu
```

Opakované rebuildovanie pre každý environment vytvára riziko, že staging a produkcia dostanú rozdielne bytes.

Konfigurácia prostredia má byť pokiaľ možno oddelená od artifactu.

## 8. Quality gates

Blocking gate má zastaviť integráciu pri vysoko dôveryhodnom a relevantnom failure.

Príklady:

- compile error,
- unit failure,
- contract incompatibility,
- high-confidence secret finding,
- policy violation,
- neplatný artifact signature.

Advisory kontroly môžu reportovať trend alebo findings bez okamžitého blokovania.

Gate potrebuje:

- ownera,
- dokumentované pravidlo,
- nízky noise,
- exception lifecycle,
- primeraný runtime.

## 9. Pull request CI

PR pipeline overuje candidate change pred merge.

Môže používať:

- merge commit simuláciu,
- merge queue,
- affected test selection,
- ephemeral environment,
- required reviews,
- policy checks.

Dôležité je testovať stav, ktorý sa reálne integruje. Samotný feature branch tip môže prejsť, ale po merge s aktuálnym main zlyhať.

## 10. Merge queue

Merge queue zoradí schválené zmeny a testuje ich proti predpokladanému aktuálnemu main.

Rieši race:

```text
PR A green
PR B green
A merge
B už nie je overený proti novému main
```

Merge queue znižuje broken main pri vysokej paralelizácii zmien.

## 11. Caching

Cache zrýchľuje pipeline, ale nie je source of truth.

Cache môže obsahovať:

- downloaded dependencies,
- compiler cache,
- intermediate build outputs,
- package-manager metadata.

Riziká:

- stale cache,
- cache poisoning,
- nesprávny cache key,
- zdieľanie medzi nedôveryhodnými branches,
- nereprodukovateľný build.

Pipeline musí vedieť prejsť aj s prázdnou cache.

## 12. Artifacts a test evidence

CI má zachovať:

- build artifact,
- test reports,
- logs,
- coverage report,
- SBOM alebo scan report podľa potreby,
- source commit metadata,
- tool versions,
- provenance.

Evidence umožňuje diagnostiku bez rerunu a vytvára audit trail.

## 13. Secrets v CI

CI runner spracúva dôveryhodný kód aj credentials, preto je citlivou boundary.

Ochrany:

- least privilege,
- short-lived identity,
- environment-scoped secrets,
- zákaz secrets pre nedôveryhodné fork pipelines,
- masked logs,
- izolované runners,
- pravidelná rotácia,
- audit použitia.

Secret dostupný každému jobu je zbytočne široký blast radius.

## 14. Runner isolation

Runners môžu byť:

- shared,
- dedicated,
- ephemeral,
- self-hosted,
- containerized alebo VM-based.

Riziká persistent runnera:

- zvyškový workspace,
- credentials v procese alebo súbore,
- poisoned cache,
- cross-project contamination,
- drift toolchainu.

Ephemeral runner znižuje persistence riziko, ale potrebuje rýchle provisioning a observability.

## 15. Broken main

Keď main zlyhá:

1. zastaviť ďalšiu integráciu podľa policy,
2. identifikovať first bad change,
3. revertovať alebo opraviť,
4. obnoviť green stav,
5. analyzovať, prečo gate chybu nezachytil skôr.

Dlhodobo červený main normalizuje failure a ničí dôveru v CI.

## 16. Flaky tests

Flaky blocking tests spôsobujú:

- rerun-until-green,
- obchádzanie gates,
- dlhé queue times,
- nejasnú diagnostiku.

CI má sledovať first-attempt result, quarantine lifecycle a ownership. Retry nesmie vymazať pôvodný failure.

## 17. Pipeline performance

Sleduj:

- queue time,
- time to first failure,
- total duration,
- cache hit rate,
- flaky rate,
- infrastructure failure rate,
- tests per stage,
- critical-path duration.

Optimalizuj kritickú cestu, nie iba počet paralelných jobov.

## 18. CI anti-patterny

### CI iba raz denne

Zmeny sa integrujú vo veľkom batchi a feedback prichádza neskoro.

### Build iba na developer notebooku

Nie je reprodukovateľný ani auditovateľný.

### Každá kontrola blokuje

Noise vytvorí výnimky a obchádzanie pipeline.

### Main je často červený

Tím prestane považovať failure za urgentný.

### Rebuild pre každý environment

Nie je garantované, že sa promuje rovnaký artifact.

### Tajomstvá v repository alebo logu

CI sa stáva zdrojom credential compromise.

## 19. Metriky CI

Užitočné metriky:

- integration frequency,
- PR lead time,
- time to first useful feedback,
- main branch health,
- mean time to repair broken main,
- pipeline success rate podľa failure class,
- flaky test rate,
- queue time,
- artifact reproducibility,
- defect escape rate.

Samotný počet pipeline runs nehovorí o kvalite CI.

## 20. Kontrolné otázky

1. Čo odlišuje CI od obyčajného build servera?
2. Prečo sú malé a časté zmeny dôležité?
3. Čo znamená build once?
4. Prečo treba testovať merge result?
5. Ako funguje merge queue?
6. Prečo cache nesmie byť source of truth?
7. Aké dôkazy má CI zachovať?
8. Aké riziká majú persistent runners?
9. Ako reagovať na broken main?
10. Ktoré metriky ukazujú kvalitu feedback loopu?

## Glossary impact

Relevantné pojmy: Continuous Integration, mainline, build once, reproducible build, merge queue, pipeline cache, build artifact, runner isolation, broken main a time to first feedback.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Chaos testing](../04-testing-and-quality/chaos-testing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Continuous Delivery →](continuous-delivery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
