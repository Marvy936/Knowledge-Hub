# Code coverage a quality gates

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Testing and Software Quality
- Predpoklady: [Static analysis, linting a type checking](static-analysis-linting-type-checking.md), [Test pyramid](test-pyramid.md)
- Súvisiace témy: instrumentation, line coverage, branch coverage, condition coverage, diff coverage, mutation testing, quality gate, ratcheting, waiver

## 1. Mentálny model

Code coverage meria, ktoré instrumentované časti programu boli vykonané počas konkrétneho súboru test runs. Quality gate je rozhodovací contract, ktorý z viacerých dôkazov určuje, či sa zmena môže posunúť do ďalšej fázy delivery.

```text
source a build configuration
→ instrumentation
→ test execution
→ raw coverage probes
→ merge a source mapping
→ metriky a scope
→ threshold alebo risk policy
→ pass, fail, advisory alebo incomplete
```

Coverage odpovedá na otázku „čo sa počas merania vykonalo?“. Neodpovedá priamo, či test mal správny oracle, či vykonaná vetva bola overená meaningful assertionom ani či test suite pokrýva používateľské a prevádzkové riziká.

## 2. Coverage je negatívny signál

Coverage je najsilnejšia pri odhaľovaní zjavne neotestovaného kódu. Ak kritická branch nikdy nebola vykonaná, test suite ju nemohla dynamicky overiť.

Vysoká coverage je slabší pozitívny dôkaz. Kód môže byť vykonaný bez assertionu, s nesprávnym vstupom alebo iba ako vedľajší efekt širokého E2E testu.

```python
result = calculate_total(items)
assert result is not None
```

Takýto test môže vykonať všetky riadky a stále neoveriť správnu cenu, rounding, tax alebo discount invariant.

Praktická interpretácia:

```text
nízka coverage
→ pravdepodobne chýba testované vykonanie

vysoká coverage
→ iba predpoklad na ďalšie hodnotenie oracle a scenárov
```

## 3. Line a statement coverage

**Line coverage** meria podiel source riadkov mapovaných na aspoň jeden executed probe. **Statement coverage** meria vykonané programové príkazy podľa modelu konkrétneho jazyka a instrumentácie.

Tieto metriky sa môžu líšiť. Jeden riadok môže obsahovať viac statements a compiler môže jeden source statement rozložiť na viac bytecode instructions.

```python
if enabled: start(); log_started()
```

Line coverage môže označiť riadok ako covered, aj keď sa vykonala iba časť jeho logiky. Preto treba rozumieť reportovaciemu modelu použitého nástroja.

## 4. Function alebo method coverage

Function coverage hovorí, či bola function aspoň raz zavolaná. Pomáha nájsť úplne nedotknuté entry points, no nehovorí nič o ich vnútorných branches a input space.

Function s desiatkami state transitions môže mať 100 % function coverage po jednom happy-path calle. Metrika je preto orientačný inventory signal, nie dôkaz behavioru.

## 5. Branch coverage

Branch coverage meria, ktoré výsledky rozhodnutí sa vykonali. Pri `if` to typicky znamená true aj false vetvu; pri `switch`, exception handleri alebo short-circuit expression závisí model od nástroja.

```python
if user.is_admin or user.is_owner:
    allow()
```

Jeden admin scenár môže dosiahnuť line coverage, ale nemusí vykonať owner path ani deny path. Branch coverage odhalí, že niektoré rozhodnutia neboli pozorované.

Branch coverage stále neznamená všetky kombinácie conditions. Výraz s viacerými boolean operands môže mať obe výsledné branches vykonané bez toho, aby sa každá podmienka vyhodnotila ako true aj false.

## 6. Condition a decision coverage

Condition coverage sleduje jednotlivé boolean subexpressions. Pri kritickej decision logic môže byť potrebné overiť:

- každá condition bola true aj false;
- výsledné rozhodnutie bolo allow aj deny;
- short-circuit nezakryl významný operand;
- kombinácie chránia bezpečnostný alebo business invariant.

Pre safety-critical domény existujú prísnejšie modely, napríklad Modified Condition/Decision Coverage. Bežný aplikačný tím ich nemusí používať plošne, ale mal by rozumieť, že „branch covered“ a „decision logic dôkladne otestovaná“ nie sú synonymá.

## 7. Path coverage a kombinatorický rast

Path coverage sa snaží pokryť execution paths cez viac rozhodnutí. Ich počet rastie kombinatoricky a pri loops môže byť teoreticky neobmedzený.

Úplná path coverage preto nie je realistický globálny cieľ. Rizikové paths treba identifikovať cez domain model, threat model, historical failures, property-based testing alebo model-based testing.

Coverage metrika nemá nahradiť analýzu input partitions a state transitions.

## 8. Instrumentation lifecycle

Coverage nástroj vkladá probes do source, bytecode alebo runtime profilu a pri behu zaznamenáva ich execution.

```text
source
→ compile/transpile
→ instrumentation alebo runtime hooks
→ tests a subprocessy
→ raw execution data
→ source-map resolution
→ merged report
```

Výsledok môže ovplyvniť:

- compiler optimization a inlining;
- transpilation a source maps;
- generated code;
- subprocessy a child runtimes;
- parallel workers;
- dynamic imports alebo plugins;
- container/host path rozdiely;
- test process crash pred flushom dát;
- language runtime a coverage-tool verzia.

Coverage report je dôveryhodný iba vtedy, keď poznáme, ktoré processes boli instrumentované a či všetky úspešne zapísali výsledky.

## 9. Source mapping

Instrumentácia môže merať bytecode alebo transpiled output a až následne mapovať probes späť na source. Chybná alebo chýbajúca source map spôsobí nepresné lines, branches alebo úplne neviditeľné files.

Pri containeroch a remote runners treba normalizovať paths:

```text
/workspace/src/app.py
C:\agent\_work\repo\src\app.py
repo/src/app.py
```

Ak report merge považuje tieto paths za rozdielne files, výsledok sa rozdelí alebo duplikuje. Autoritatívna pipeline musí mať stabilný repository-relative mapping.

## 10. Parallel tests a report merge

Každý worker alebo process môže vytvárať vlastný raw report. Merge musí zachovať union probes a zároveň zabrániť strate alebo dvojitému započítaniu dát.

Pred agregáciou over:

- rovnaký source revision a build artifact;
- rovnakú instrumentačnú konfiguráciu;
- unikátne output files pre workers;
- dokončenie všetkých shardov;
- kompatibilné report versions;
- správne path mapping;
- explicitný status chýbajúcich shardov.

Ak jeden test shard zlyhá pred uploadom coverage, aggregate výsledok nie je kompletný. Pipeline ho nesmie interpretovať ako plnohodnotnú nižšiu coverage ani ako clean pass bez označenia incomplete.

## 11. Coverage podľa test layeru

Aggregate coverage môže zlúčiť unit, integration, component a E2E testy. To ukáže celkové vykonanie, ale môže skryť nevhodnú alokáciu dôkazov.

Kritická calculation logic môže byť covered iba cez pomalý UI test. Taká suite má síce vysoké percento, ale pomalý feedback a slabú failure localization.

Užitočné pohľady sú:

- unit-only coverage pre lokálnu logiku;
- integration coverage pre adapters a storage boundaries;
- aggregate coverage pre celkový runtime reach;
- coverage kritických modulov;
- diff coverage zmeneného kódu.

Coverage podľa vrstvy nie je ďalšia kvóta. Pomáha zistiť, kde sa dôkaz reálne nachádza.

## 12. Generated code

Generated code môže výrazne skresliť percento. Rozhodnutie závisí od ownershipu:

- **vendor-generated code bez lokálnej logiky** — často sa vylúči a testuje sa generator/source contract;
- **code generation template vlastnená tímom** — treba testovať generátor, output invariants a aspoň integračný behavior;
- **generated client používaný ako public API** — môže vyžadovať compile a smoke tests aj keď sa riadky nepočítajú do threshold;
- **rendered infrastructure** — coverage metrika nemusí byť vhodná; dôležitejšia je schema, policy a runtime verification.

Exclusion nesmie byť nástroj na estetické zvýšenie percenta. Má mať explicitný dôvod a review.

## 13. Exclusions

Legitímne exclusions môžu zahŕňať compiler-generated glue, platform-specific vetvu testovanú v inom jobe, defensive fatal path overený fault injectionom alebo trivial entrypoint bez vlastnej logiky.

Každá exclusion potrebuje:

- minimálny scope;
- vysvetlenie;
- ownera;
- dôkaz alternatívneho testu, ak behavior ostáva kritický;
- pravidelnú kontrolu;
- zákaz automatického rozširovania wildcardom bez review.

Rozsiahla exclusion konfigurácia je forma test debt a mala by byť trendovaná.

## 14. New-code a diff coverage

Pri legacy codebase je praktické blokovať regresiu na zmenenom kóde bez požiadavky okamžite opraviť celý historický deficit.

```text
starý codebase debt
+ zmena v pull requeste
→ diff coverage nad executable changed lines
→ nový kód debt nezvyšuje
```

Diff coverage závisí od správneho diff base. Pri pull requeste to typicky nie je lokálny `HEAD~1`, ale merge base s cieľovou branchou.

Treba správne riešiť:

- renames a moves;
- generated files;
- deleted lines;
- formatting-only zmeny;
- branch coverage na zmenených decisions;
- stacked branches;
- merge queue synthetic commit;
- zmenu base branch počas behu.

Nesprávny merge base môže označiť príliš veľa alebo príliš málo riadkov a vytvoriť chybný gate.

## 15. Diff coverage limity

Diff coverage chráni nový alebo zmenený code, ale môže prehliadnuť behavior ovplyvnený nepriamo:

- zmena shared configu aktivuje starú vetvu;
- zmena dependency mení behavior nezmeneného adaptera;
- rename alebo refactor zachová riadky, ale zmení call graph;
- nový caller používa starú function s neotestovaným inputom;
- schema migration mení interpretáciu existujúceho kódu.

Preto je diff coverage doplnok k risk-based regression, contract tests a architecture awareness, nie úplná test-selection stratégia.

## 16. Risk-weighted coverage

Rovnaký threshold pre každý file nezohľadňuje impact a complexity. Vyššiu dôkaznú úroveň zvyčajne potrebujú:

- authorization a tenant isolation;
- billing a financial calculations;
- migrations a destructive automation;
- parsers a protocol handling;
- idempotency a concurrency;
- recovery a compensation paths;
- cryptographic alebo policy code;
- data retention a compliance logic.

Risk-weighted model nemusí znamenať desiatky odlišných percent. Môže kombinovať globálne minimum, vyššie diff branch coverage pre kritické paths a povinné named scenarios alebo mutation testing.

## 17. Mutation testing

Mutation testing zámerne vytvorí malé zmeny v programe a overí, či test suite zlyhá.

```text
>  → >=
true → false
+ → -
condition removed
return value changed
```

Mutant je **killed**, ak test zlyhá. **Surviving mutant** môže znamenať chýbajúci scenár, slabý assertion, equivalent mutant alebo neexecuted path.

Mutation score poskytuje silnejší signál o citlivosti testov než samotné execution coverage. Je však drahý a jeho výsledok treba triagovať; nie každý mutant reprezentuje reálnu behavior change.

Praktické použitie:

- kritické domain moduly;
- changed code v pull requeste;
- periodický job;
- investigation po vysokej coverage a defect escape;
- overenie kvality regression testu po incidente.

## 18. Coverage a assertions

Coverage nástroj typicky nevie, či executed code ovplyvnil assertion. Test môže vykonať vetvu počas setupu alebo cleanupu bez kontroly jej výsledku.

Dôkaz assertion quality možno posilniť cez:

- mutation testing;
- property-based assertions;
- negative tests;
- invariant checks;
- failure injection;
- review test intentu;
- defect escape analýzu.

Coverage je mapa vykonania. Oracle quality sa musí hodnotiť samostatne.

## 19. Quality gate ako risk contract

Quality gate má chrániť konkrétne rozhodnutie, napríklad merge do `main`, publikovanie artifactu, promotion do production alebo pokračovanie rollout-u.

```text
inputs a evidence
→ policy evaluation
→ decision
→ audit record
```

Gate môže kombinovať:

- build a package integrity;
- tests podľa vrstvy;
- coverage a mutation score;
- static analysis;
- contract compatibility;
- security findings;
- performance budget;
- required review a ownership;
- policy compliance;
- deployment smoke a SLI.

Zbierka metrík bez väzby na riziko nie je kvalitný gate. Každý signal má mať dôvod, scope a failure semantics.

## 20. Blocking a advisory kontroly

**Blocking gate** zastaví chránený krok. Je vhodný pre presný, reprodukovateľný a akčný signal s jasným ownerom.

**Advisory gate** reportuje riziko bez automatického zastavenia. Je vhodný pri zavádzaní nástroja, baseline zbere, neistej heuristike alebo dlhodobom trende.

Advisory kontrola potrebuje explicitný lifecycle:

```text
observe
→ tune
→ odmerať precision a stability
→ definovať remediation
→ pilot blocking scope
→ rozšíriť alebo ponechať advisory
```

Advisory, ktorý nikto nesleduje, nie je kontrola. Blocking gate s chronickým šumom sa zase zmení na bypass mechanizmus.

## 21. Gate placement

Kontrola má bežať pred rozhodnutím, ktoré chráni, a čo najskôr, ako je dostupná potrebná fidelity.

```text
editor/local
→ format, syntax, targeted lint

pull request
→ build, unit, diff coverage, static, contracts

merge queue
→ integration proti budúcemu main

pre-release
→ širšia regression, security, performance

post-deploy
→ smoke, policy a SLI verification
```

Dlhý performance test nemôže nahradiť rýchly PR gate. Rýchla coverage kontrola zasa nemôže potvrdiť produkčný rollout.

## 22. Threshold design

Threshold musí byť verzovaný, reprodukovateľný a vysvetlený rizikom. Môže obsahovať viac rozmerov:

```text
global line coverage >= 75 %
changed-code branch coverage >= 85 %
authorization module coverage nesmie klesnúť
critical recovery paths musia mať named tests
mutation score critical module >= dohodnuté minimum
```

Percento nemá byť univerzálne kopírované medzi repositories. Jazyk, generated code, testability, risk a legacy stav sa líšia.

Príliš presný threshold, napríklad 82.47 %, často vytvára falošný dojem vedeckej objektivity. Dôležitejšia je stabilná policy a review zmien prahu.

## 23. Ratcheting

Ratcheting zabraňuje zhoršeniu a postupne zvyšuje baseline.

```text
accepted minimum
= max(organizational floor, previous accepted state)
```

Pri každom raste threshold treba overiť, že výsledok nie je spôsobený exclusions, generated files alebo testami bez assertionov. Ratchet má zlepšovať ochranu, nie iba číslo.

Ratcheting možno použiť aj na:

- znižovanie uncovered critical branches;
- znižovanie suppression count;
- rast mutation score;
- znižovanie flaky gate rate;
- skracovanie gate duration.

## 24. Anti-gaming design

Coverage možno zvýšiť bez zlepšenia testov:

- volaním functions bez meaningful assertions;
- trivial tests nad getters;
- broad exclusions;
- generovaním low-value files;
- testovaním implementation details;
- používaním E2E testu na vykonanie veľkého množstva kódu;
- zmenou report scope namiesto pridania dôkazu.

Ochrany zahŕňajú branch coverage, mutation testing, review test intentu, risk-based required scenarios, exclusion audit a defect-escape feedback.

Metrika, ktorá sa stane cieľom bez kontextu, bude optimalizovaná na číslo. Gate preto musí hodnotiť kombináciu dôkazov.

## 25. Tool failure a incomplete evidence

Coverage job môže zlyhať bez toho, aby testy zlyhali:

- instrumentácia sa neaktivovala;
- raw report chýba;
- jeden shard neodoslal dáta;
- source mapping zlyhal;
- report merge crashol;
- uploader alebo dashboard bol nedostupný;
- report patrí inému commitu.

Pipeline musí rozlíšiť:

```text
coverage complete and above policy
coverage complete and below policy
coverage incomplete
coverage infrastructure failed
```

Chýbajúci report nesmie byť interpretovaný ako 0 % ani ako „gate skipped“ bez viditeľného statusu. Fail-open alebo fail-closed policy musí byť explicitná.

## 26. Provenance aggregate reportu

Autoritatívny coverage report má byť viazaný na:

- source commit alebo synthetic merge commit;
- build artifact alebo compilation output;
- test suite a shard list;
- instrumentačný tool a config version;
- report merge version;
- exclusions;
- timestamp a CI run;
- merge base pre diff coverage.

Bez provenance nemožno dokázať, že percento patrí k release kandidátovi, ktorý sa má schváliť.

## 27. Waiver a exception lifecycle

Gate waiver je risk decision, nie technické kliknutie. Má obsahovať:

- presný gate a scope;
- dôvod failure alebo nemožnosti opravy;
- impact a risk ownera;
- compensating control;
- expiry;
- issue a remediation plán;
- approvals;
- audit trail;
- podmienky, za ktorých sa waiver automaticky zruší.

Waiver nesmie prepísať samotný výsledok na zelený. Evidence má zostať červená alebo označená ako waived, aby audit rozlíšil technický stav od manažérskeho rozhodnutia.

## 28. Flaky gate

Gate, ktorý náhodne zlyháva, mení delivery behavior. Vývojári začnú rerunovať, ignorovať alebo obchádzať výsledky a batch size rastie.

Pred blocking režimom meraj:

- first-attempt pass rate;
- false-positive rate;
- tool a infrastructure failure rate;
- duration a queue time;
- local reproducibility;
- time to remediation;
- waiver frequency.

Rerun môže poskytnúť diagnostický dôkaz, ale prvý failure sa nesmie potichu vymazať. Finálny status má rozlišovať pass-on-first-attempt, flaky recovery a reálny fix.

## 29. Trend a ownership

Dashboard má viesť k akcii. Užitočné signály sú:

- global a diff coverage trend;
- uncovered critical branches;
- mutation score;
- exclusions a uncovered generated-owned code;
- incomplete report rate;
- gate failures podľa príčiny;
- waiver count a age;
- test duration a flaky rate;
- defect escape z covered paths;
- time to resolve gate failure.

Každý trend potrebuje ownera a decision rule. Samotný graf bez reakcie nevytvára quality control.

## 30. Diagnostický workflow

Keď coverage alebo gate zlyhá neočakávane:

1. potvrď source commit, target branch a merge base;
2. over, že všetky test shards skončili a odovzdali raw report;
3. skontroluj instrumentation a source-map logy;
4. porovnaj tool, config a exclusion versions;
5. over repository-relative paths po merge;
6. rozlíš reálny uncovered change od reportovacieho problému;
7. skontroluj, či branch alebo condition metrika zodpovedá očakávaniu;
8. prečítaj konkrétne uncovered lines v kontexte rizika;
9. pridaj meaningful test alebo zdôvodnenú exclusion;
10. over kompletný autoritatívny rerun nad rovnakým kandidátom.

Pri quality-gate failure navyše rozlíš, ktorý signal zlyhal, či je blocking, či je evidence kompletná a či existuje platný waiver.

## 31. Časté omyly

### „80 % coverage znamená 80 % kvalitu“

Coverage a kvalita nemajú lineárny vzťah. Percento nevyjadruje oracle, risk ani business correctness.

### „100 % coverage znamená bezchybný systém“

Všetky probes môžu byť vykonané nesprávnymi scenármi alebo slabými assertions.

### „Diff coverage chráni všetky dopady zmeny“

Nepriame behavioral zmeny môžu ležať v nezmenenom kóde, konfigurácii alebo dependency grafe.

### „Chýbajúci coverage report je iba infra problém“

Je to chýbajúci dôkaz. Pipeline ho musí označiť ako incomplete alebo failed podľa policy.

### „Waiver robí gate zeleným“

Waiver povoľuje postup napriek známemu failure. Technický výsledok sa nesmie prepísať.

### „Viac blocking gates vždy zvyšuje kvalitu“

Hlučné a pomalé gates zvyšujú bypassy, lead time a batch size. Gate musí byť presný a prevádzkovo udržateľný.

## 32. Prevádzkový checklist

- Je jasné, ktorú coverage metriku nástroj reportuje?
- Sú instrumentované všetky relevantné processes a shards?
- Je source mapping stabilný medzi hostom, containerom a CI?
- Je report viazaný na presný commit a artifact?
- Používa diff coverage správny merge base?
- Sú generated code a exclusions explicitne reviewované?
- Rozlišuje sa unit-only a aggregate coverage tam, kde to pomáha?
- Má kritická decision logic branch/condition a named scenario evidence?
- Používa sa mutation testing cielene na high-risk code?
- Rozlišuje gate pass, fail, incomplete a infrastructure failure?
- Má threshold risk rationale a version history?
- Sú waivers úzke, expirovateľné a auditovateľné?
- Meria sa flaky rate, waiver age a defect escape?

## 33. Kontrolné otázky

1. Prečo je coverage silnejšia ako negatívny než pozitívny signál?
2. Aký je rozdiel medzi line, statement, branch a condition coverage?
3. Prečo branch coverage neznamená všetky kombinácie boolean podmienok?
4. Ako instrumentation a source mapping ovplyvňujú výsledok?
5. Čo sa môže pokaziť pri merge coverage reportov z paralelných workerov?
6. Ako sa má pracovať s generated code a exclusions?
7. Prečo diff coverage potrebuje správny merge base?
8. Aké riziká diff coverage nevidí?
9. Čo mutation testing meria navyše oproti execution coverage?
10. Aké stavy musí coverage gate rozlišovať okrem pass a fail?
11. Ako funguje ratcheting a ako sa dá gamovať?
12. Prečo waiver nesmie prepísať technický failure na pass?

## Glossary impact

Relevantné pojmy: code coverage, line coverage, statement coverage, function coverage, branch coverage, condition coverage, path coverage, instrumentation, probe, source mapping, aggregate coverage, diff coverage, mutation testing, mutation score, quality gate, blocking gate, advisory gate, threshold, ratcheting, waiver, compensating control a incomplete evidence.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Static analysis, linting a type checking](static-analysis-linting-type-checking.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Mocks, stubs a fakes →](mocks-stubs-fakes.md)
<!-- KNOWLEDGE-NAVIGATION:END -->