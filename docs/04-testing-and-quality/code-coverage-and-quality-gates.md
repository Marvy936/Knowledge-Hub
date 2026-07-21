# Code coverage a quality gates

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

## 1. Definícia

Code coverage meria, ktorá časť kódu bola vykonaná počas testov. Quality gate je automatické rozhodovacie pravidlo, ktoré na základe definovaných signálov povoľuje alebo blokuje ďalší krok delivery procesu.

Coverage je meranie exekúcie. Nie je to priama metrika correctness, kvality assertions ani business coverage.

## 2. Základné coverage metriky

### Line coverage

Podiel vykonaných riadkov.

### Statement coverage

Podiel vykonaných príkazov podľa jazyka alebo instrumentácie.

### Function alebo method coverage

Podiel funkcií, ktoré boli aspoň raz zavolané.

### Branch coverage

Podiel vykonaných výsledkov rozhodnutí, napríklad true/false vetiev.

### Condition coverage

Podiel jednotlivých boolean podmienok, ktoré nadobudli true aj false.

### Path coverage

Podiel možných execution paths. Pri reálnom kóde rastie kombinatoricky a úplné pokrytie býva nepraktické.

## 3. Prečo 100 % coverage nestačí

Test môže vykonať kód bez meaningful assertion:

```python
result = calculate_total(items)
assert result is not None
```

Coverage môže byť 100 %, hoci test neoverí správny výpočet.

Coverage neodpovedá priamo:

- či assertions kontrolujú správne správanie,
- či existujú negatívne scenáre,
- či sú testované boundaries,
- či kontrakt zodpovedá používateľskej potrebe,
- či testy odhalia mutation alebo regresiu.

## 4. Branch coverage vs. line coverage

Príklad:

```python
if user.is_admin or user.is_owner:
    allow()
```

Line coverage môže byť 100 % po jedinom admin scenári. Condition alebo branch-oriented testovanie musí overiť kombinácie:

- admin true,
- owner true,
- obe false,
- prípadne obe true.

Vyššia granularita môže odhaliť neotestovanú rozhodovaciu logiku.

## 5. Instrumentation

Coverage tool typicky:

- instrumentuje source alebo bytecode,
- zaznamenáva executed probes,
- mapuje výsledky späť na source lines/branches,
- agreguje report.

Výsledok môže ovplyvniť:

- compiler optimization,
- generated code,
- inline functions,
- subprocessy,
- parallel execution,
- dynamic loading,
- path mapping medzi containerom a hostom.

## 6. Unit vs. aggregate coverage

Aggregate coverage môže kombinovať:

- unit tests,
- integration tests,
- component tests,
- E2E tests.

To poskytuje širší obraz, ale môže skryť, že kritická logika je pokrytá iba pomalým E2E testom. Pri rozhodovaní sleduj aj coverage podľa test layeru a ownership oblasti.

## 7. New-code coverage

Pri legacy codebase je často vhodnejší gate na changed alebo new code než okamžitá požiadavka vysokej globálnej coverage.

Princíp:

```text
existujúci debt sa nezhoršuje
+ nový alebo zmenený kód má primerané testy
+ dlhodobý trend sa zlepšuje
```

Diff coverage musí správne pracovať s rename, generated files a merge base.

## 8. Risk-based coverage

Rovnaký threshold pre každý súbor nie je optimálny. Vyššiu dôkaznú úroveň potrebujú:

- authorization,
- billing,
- migration logic,
- parsers,
- recovery paths,
- concurrency,
- security controls,
- destructive automation.

Jednoduchý generated adapter nemusí mať rovnakú požiadavku.

## 9. Mutation testing

Mutation testing zámerne mení program, napríklad:

```text
> na >=
true na false
+ na -
odstránenie podmienky
```

Test suite má mutanta zabiť zlyhaním. Surviving mutants signalizujú slabú assertion alebo chýbajúci scenár.

Mutation score je užitočný doplnok coverage, ale býva výpočtovo drahý. Môže sa používať na kritické moduly alebo changed code.

## 10. Exclusions

Coverage exclusions majú byť explicitné a reviewované. Typické legitímne prípady:

- generated code,
- platform-specific unreachable branch v danom rune,
- defensive code, ktorý sa testuje iným mechanizmom,
- trivial bootstrap glue.

Exclusion nesmie byť jednoduchý spôsob, ako dosiahnuť threshold.

## 11. Quality gate

Quality gate kombinuje signály, napríklad:

- build success,
- tests,
- coverage,
- static analysis,
- security findings,
- contract compatibility,
- performance regression,
- required reviews,
- policy compliance.

Gate má vyjadrovať rizikový kontrakt, nie zbierku náhodných metrík.

## 12. Blocking vs. advisory gate

### Blocking

Zastaví merge, release alebo deployment.

Vhodný pre:

- presné a kritické kontroly,
- reprodukovateľný failure,
- jasnú remediation,
- nízku flaky rate.

### Advisory

Reportuje problém, ale neblokuje.

Vhodný pri:

- zavádzaní novej kontroly,
- baseline zbere,
- menej presnom signále,
- trendoch a odporúčaniach.

Advisory kontrola má mať plán, či a kedy sa stane blocking.

## 13. Gate placement

Rôzne gates patria do rôznych bodov:

```text
editor/local
→ syntax, format, targeted lint

pull request
→ build, unit, static, diff coverage, contracts

pre-merge/merge queue
→ integration proti aktuálnemu main

pre-release
→ broader regression, security, performance

post-deploy
→ smoke, SLI a policy verification
```

Najrýchlejšie spoľahlivé kontroly patria čo najskôr.

## 14. Threshold dizajn

Threshold má byť:

- vysvetlený rizikom,
- stabilný,
- versioned,
- lokálne reprodukovateľný,
- primeraný scope,
- odolný voči gaming-u.

Príklad:

```text
global line coverage >= 75 %
changed-code branch coverage >= 85 %
žiadny pokles coverage kritického authorization modulu
```

Percento samo osebe nie je univerzálny štandard.

## 15. Ratcheting

Ratcheting povoľuje iba rovnaký alebo lepší stav:

```text
current threshold = max(minimum, previous accepted baseline)
```

Je vhodný na postupné znižovanie legacy debt bez jednorazového blokovania celého vývoja.

## 16. Exceptions a waivers

Exception má obsahovať:

- konkrétny gate a scope,
- dôvod,
- risk ownera,
- compensating control,
- expiry,
- issue na odstránenie,
- audit trail.

Permanentný globálny bypass ničí dôveryhodnosť gate-u.

## 17. Flaky gates

Gate, ktorý zlyháva náhodne, vedie k:

- rerun-until-green,
- ignorovaniu failures,
- dlhšiemu lead time,
- bypassom,
- zníženiu dôvery.

Pred blocking režimom meraj stability a false-positive rate kontroly.

## 18. Trendy a dashboards

Sleduj:

- coverage trend,
- changed-code coverage,
- untested critical paths,
- mutation score,
- gate failure reasons,
- bypass count,
- mean time to resolve gate failure,
- flaky rate.

Dashboard bez ownership a akcie je iba reporting.

## 19. Anti-gaming dizajn

Coverage môže byť umelo zvýšená:

- testami bez assertions,
- trivial tests,
- exclusions,
- volaním kódu bez overenia,
- testami implementation details.

Ochrany:

- review test intentu,
- mutation testing,
- branch coverage,
- risk-based test cases,
- failure injection,
- sledovanie defect escape rate.

## 20. Typické omyly

### „80 % coverage znamená 80 % kvalitu“

Coverage a kvalita nemajú takýto lineárny vzťah.

### „100 % coverage znamená bezchybný systém“

Nie. Chýba dôkaz správnych assertions a požiadaviek.

### „Každý repository potrebuje rovnaký threshold“

Riziko, jazyk a testability sa líšia.

### „Viac blocking gates vždy zvyšuje bezpečnosť“

Pomalé alebo hlučné gates môžu viesť k bypassom a väčšiemu batch size.

### „Exception je iba kliknutie na override“

Musí byť časovo obmedzené a auditovateľné risk rozhodnutie.

## 21. Kontrolné otázky

1. Aký je rozdiel medzi line, branch, condition a path coverage?
2. Prečo vysoká coverage nedokazuje kvalitu assertions?
3. Čo je diff alebo new-code coverage?
4. Ako funguje mutation testing?
5. Kedy je coverage exclusion legitímna?
6. Aký je rozdiel medzi blocking a advisory gate?
7. Ako zvoliť gate placement v pipeline?
8. Čo je ratcheting?
9. Ako má vyzerať exception lifecycle?
10. Ako odhaliť gaming coverage metrík?

## Glossary impact

Relevantné pojmy: code coverage, line coverage, branch coverage, condition coverage, path coverage, diff coverage, mutation testing, mutation score, quality gate, blocking gate, advisory gate, threshold, ratcheting, waiver a compensating control.
