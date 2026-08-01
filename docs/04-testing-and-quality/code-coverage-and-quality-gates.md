# Code coverage a quality gates

Code coverage meria, ktoré časti instrumentovaného programu vykonal konkrétny test run. Nehodnotí správnosť assertions ani business význam. Vysoká coverage môže vzniknúť testom bez oracle a nízka coverage môže byť prijateľná pri generated alebo defensive code.

Bežné metriky:

```text
line coverage
ktoré riadky sa vykonali

branch coverage
ktoré vetvy rozhodnutia sa vykonali

condition coverage
ktoré boolean podmienky nadobudli hodnoty

function coverage
ktoré funkcie sa zavolali
```

Coverage denominator závisí od toolu, compileru, generated code a exclusions. Čísla z dvoch toolchains preto nemusia byť priamo porovnateľné.

Neutrálny príklad:

```python
if user.is_admin or user.is_owner:
    allow()
```

Test s admin userom môže vykonať riadok a dosiahnuť line coverage, ale neoverí owner branch ani unauthorized case. Branch/condition coverage odhalí chýbajúce paths, no stále nezaručí správny authorization oracle.

Diff coverage meria nový alebo zmenený code a je vhodná na ratcheting. Globálny threshold môže motivovať k bezvýznamným testom alebo penalizovať legacy code, ktorý aktuálny change nezhoršil.

Quality gate kombinuje evidence a rozhoduje, či subject smie pokračovať. Môže byť blocking alebo advisory. Dobrý gate viaže findings na presný commit/artifact, má stabilné pravidlá, jasné owners a auditovateľnú exception.

Gate nemá zamieňať signál za výsledok. `coverage >= 80 %` nepreukazuje correctness. Lepší model kombinuje required tests, diff coverage, critical risk checks, security findings a explicitné policy.

Flaky alebo environment-sensitive checks nesmú byť maskované rerun-until-green. Gate musí zachovať first-attempt evidence a failure artifacts. Exception má mať dôvod, scope, expiry a compensating control.

## 1. Cieľ kapitoly

Nosný model je:

```text
failure mode a chránené rozhodnutie
→ zvoliť potrebný test scope a coverage pohľad
→ preukázať úplnosť instrumentation a reportu
→ interpretovať uncovered kód podľa rizika
→ doplniť oracle-quality a compatibility evidence
→ vyhodnotiť verzovanú gate policy
→ opraviť, zastaviť alebo použiť expirovateľnú waiver
→ sledovať defect escapes a upraviť kontrolu
```

Coverage je najsilnejšia ako negatívny signál. Nevykonaná kritická vetva určite nebola týmto test runom dynamicky overená. Vykonaná vetva však môže byť bez meaningful assertionu alebo iba náhodne prejdená širokým E2E testom.

## 2. Nosný scenár: Atlas Orders 3.9.1

Atlas mení export objednávok a retry handling workeru. Pull request zasahuje:

```text
ExportCommand tenant context
Retry-After parser
object-storage path builder
export worker state machine
```

Riziká sú:

- cross-tenant export;
- chýbajúci header spôsobí crash namiesto bounded retry;
- path builder umožní object key mimo tenant prefixu;
- failure state nevytvorí audit event;
- nový worker branch je vykonaný iba v pomalom E2E teste.

Atlas quality gate nemá otázku „je coverage nad 80 %?“. Má otázku:

> Poskytuje tento release kandidát dostatočný, kompletný a diagnostikovateľný dôkaz pre zmenené authorization, retry a storage boundaries?

Evidence portfolio:

```text
unit branch coverage
→ parser a state transitions

component/API negative tests
→ tenant context a zakázané side effects

integration tests
→ persistence a object-storage adapter

mutation testing
→ citlivosť authorization/retry assertions

diff coverage
→ nový a zmenený executable code

regression/smoke
→ artifact wiring a kritická journey
```

## 3. Coverage je execution evidence, nie kvalita

Coverage tool typicky zaznamená, že probe bol vykonaný. Nevie automaticky určiť, či vykonanie ovplyvnilo assertion.

```python
result = export_orders(request)
assert result is not None
```

Tento test môže vykonať authorization, query aj storage branches a stále neoveriť správny tenant, počet rows alebo object key.

Interpretácia:

```text
uncovered critical path
→ chýba execution evidence

covered critical path
→ execution existuje; oracle, input a scope treba hodnotiť samostatne
```

## 4. Coverage experiment contract

Autoritatívny report definuje:

- source commit alebo synthetic merge commit;
- instrumentovaný artifact a build configuration;
- test suites, shards a processes;
- coverage tool a configuration version;
- included a excluded files;
- source-map a path-normalization pravidlá;
- merge algorithm;
- diff base;
- completion status;
- threshold/gate policy version;
- retained raw reports.

Bez tohto contractu je percento nereprodukovateľné a nemožno ho spojiť s release kandidátom.

## 5. Instrumentation lifecycle

Coverage vzniká transformačným tokom:

```text
source
→ compile/transpile
→ probes alebo runtime hooks
→ test processes a subprocesses
→ raw execution files
→ source-map resolution
→ shard/process merge
→ repository-relative report
```

Výsledok môže skresliť compiler optimization, inlining, generated code, subprocess bez instrumentation, crash pred flushom, paralelné output collisions alebo rozdielne tool versions.

Report je platný iba vtedy, keď sú všetky očakávané producers známe a dokončené.

## 6. Line a statement coverage

Line coverage označuje source riadok, na ktorý sa mapoval vykonaný probe. Statement coverage pracuje s príkazmi podľa modelu jazyka a toolu.

```python
if enabled: start(); audit()
```

Jeden source riadok môže obsahovať viac statements. Line môže byť označená covered, aj keď sa nevykonala celá významná logika. Preto sa metrika interpretuje spolu s instrumentačným modelom.

## 7. Function coverage

Function coverage hovorí, či bola function aspoň raz zavolaná. Je užitočná ako inventory signal pre úplne nedotknuté entry points.

Atlas `handle_export()` môže mať 100 % function coverage po jednom happy-path calle, hoci neboli vykonané deny, retry, timeout ani cleanup states. Function coverage preto neposkytuje dostatočný dôkaz pre state machine.

## 8. Branch coverage

Branch coverage sleduje výsledky rozhodnutí:

```python
if authenticated_tenant == resource_tenant:
    allow_export()
else:
    deny_export()
```

Line coverage môže byť vysoká po allow scenári, ale deny branch zostane uncovered. Branch coverage odhaľuje, že verdict nebol pozorovaný v oboch smeroch.

Význam branchu závisí od oraclu. Test musí overiť aj absenciu query, eventu a objectu pri deny rozhodnutí.

## 9. Condition a decision coverage

Pri zloženom výraze:

```python
allow = is_owner or (is_admin and tenant_matches)
```

Branch coverage môže vykonať výsledné `True` aj `False`, ale nie všetky významné conditions. Condition coverage sleduje jednotlivé operands. Kritická policy môže vyžadovať explicitné kombinácie, nie globálnu percentuálnu kvótu.

Atlas authorization tests pomenúvajú matrix cases:

```text
owner + same tenant → allow
admin + same tenant → allow
admin + other tenant → deny
regular user + same tenant → deny podľa contractu
```

## 10. Path coverage a kombinatorický rast

Počet paths rastie s decisions a loops kombinatoricky. Úplná path coverage nie je realistický všeobecný cieľ.

Rizikové paths sa vyberajú cez:

- domain state model;
- threat a authorization matrix;
- historical incidents;
- property-based tests;
- failure injection;
- mutation testing;
- concurrency model.

Coverage report nemá nahradiť návrh input partitions a state transitions.

## 11. Coverage podľa testovacej vrstvy

Aggregate coverage ukazuje union vykonaných probes, ale môže skryť, kde dôkaz vznikol.

```text
unit-only
→ lokálne decisions a edge cases

integration
→ adapters, transactions a protocols

component
→ artifact wiring cez public interface

aggregate
→ celkový runtime reach
```

Ak je retry parser covered iba cez 12-minútový E2E test, percento môže byť vysoké, ale feedback a failure localization sú slabé. Layered pohľad pomáha presunúť lokálne risks do nižšieho scope-u.

## 12. Parallel processes a complete merge

Každý worker, shard alebo subprocess môže vytvárať vlastný raw report. Pred merge over:

- rovnaký source a artifact;
- rovnakú instrumentačnú config;
- unikátny output per producer;
- očakávaný shard manifest;
- úspešný flush/upload;
- kompatibilnú report verziu;
- stabilný path mapping.

Ak chýba jeden shard, aggregate report je `INCOMPLETE`. Nie je to legitímne nižšie percento ani green report.

## 13. Source mapping a path identity

Transpiled alebo bytecode probes sa mapujú späť na source. V distributed CI sa jeden file môže objaviť ako:

```text
/workspace/src/export.py
C:\agent\repo\src\export.py
src/export.py
```

Merge musí normalizovať na repository-relative identity. Inak môže rovnaký file rozdeliť, duplikovať alebo priradiť k nesprávnej revision.

## 14. Generated code a exclusions

Rozhodnutie závisí od ownershipu:

```text
vendor-generated glue
→ často vylúčiť z percenta; overiť spec/generator a compile

tímom vlastnená template
→ testovať generator a output invariants

generated public client
→ compile, contract a smoke dôkaz
```

Exclusion nesmie byť nástroj na zvýšenie percenta. Má minimálny scope, dôvod, ownera a alternatívny dôkaz pre kritický behavior.

## 15. Diff coverage

Diff coverage sa sústreďuje na executable lines a branches zmenené v pull requeste:

```text
legacy baseline
+ nový diff
→ nový kód nezvyšuje test debt
```

Autoritatívny base je merge base s cieľovou branchou alebo synthetic merge commit používaný merge queue. `HEAD~1` môže pri viacerých commitoch, stacked branchi alebo aktualizovanom targete merať nesprávny rozsah.

Diff coverage rieši nový kód, ale nevidí všetky nepriame dopady. Zmena schema, configu, dependency alebo call graphu môže aktivovať nezmenenú vetvu.

## 16. Risk-weighted interpretation

Rovnaké percento nemá rovnaký význam pre každý modul. Vyššiu dôkaznú úroveň potrebujú:

- authorization a tenant isolation;
- billing a financial calculations;
- destructive automation a migrations;
- idempotency a concurrency;
- protocol parsers;
- recovery a compensation;
- security policy a cryptographic code.

Risk-weighted model môže kombinovať:

```text
globálne minimum
+ diff branch coverage
+ named critical scenarios
+ mutation testing kritických modulov
+ zákaz uncovered security decisions
```

Nemusí vytvárať desiatky arbitrárnych percent.

## 17. Mutation testing

Mutation testing mení program malou semantic zmenou a sleduje, či test suite zlyhá:

```text
== → !=
> → >=
allow → deny
retry count 3 → 4
condition removed
```

Mutant je killed, ak test odhalí zmenu. Surviving mutant môže znamenať slabý oracle, chýbajúci scenár, neexecuted path alebo equivalent mutant.

Pre Atlas je mutation testing vhodné na authorization a retry state machine. Nie je potrebné plošne pre celý repository pri každom PR; môže bežať nad changed critical code alebo periodicky.

## 18. Worked failure: 96 % coverage, ale tenant mutant prežil

Atlas export module mal 96 % line a 91 % branch coverage. Mutation tool zmenil:

```text
authenticated_tenant == requested_tenant
→ authenticated_tenant != requested_tenant
```

Suite zostala zelená.

### Root cause

E2E test vykonal authorization branch, ale assertion kontroloval iba vznik exportu. Fixture používala rovnaký tenant na oboch stranách a žiadny negatívny test neoveril cross-tenant deny ani zakázané side effects.

### Náprava

- pridala sa explicitná authorization matrix;
- deny test overuje response, nulovú DB query, nulový queue event a DENY audit;
- critical mutation scope blokuje surviving semantic mutants;
- coverage zostáva execution mapou, mutation signal kontroluje citlivosť oraclu.

## 19. Quality gate ako decision contract

Gate chráni konkrétny krok:

```text
merge
artifact publication
pre-release promotion
production rollout
```

Gate contract obsahuje:

- rozhodnutie a ownera;
- vstupný candidate identity;
- required evidence;
- completeness podmienky;
- blocking/advisory semantics;
- thresholds alebo explicitné invariants;
- tool-failure policy;
- waiver lifecycle;
- audit record.

Zbierka metrík bez rozhodovacieho významu nie je quality gate.

## 20. Atlas pull-request gate

Atlas PR gate pre export change používa:

```text
build a static analysis complete
→ unit/component tests first-attempt green
→ changed-code branch coverage >= policy
→ authorization named scenarios present
→ no surviving critical mutants
→ contract compatibility green
→ no new blocking security findings
→ decision
```

Global line coverage je trend a floor. Nie je jediným release verdictom.

## 21. Blocking a advisory controls

Blocking signal má byť presný, reprodukovateľný, včasný a akčný. Advisory signal je vhodný počas rollout-u nového toolu, pri heuristickej metrike alebo trendovaní.

Advisory lifecycle:

```text
observe
→ tune precision a stability
→ priradiť ownera a remediation
→ pilot blocking scope
→ rozšíriť, ponechať advisory alebo odstrániť
```

Advisory bez reakcie je dekorácia. Hlučný blocking gate vytvára rerun a bypass kultúru.

## 22. Threshold design

Threshold je policy, nie prírodná konštanta. Musí byť:

- viazaný na metriku a scope;
- versioned;
- reprodukovateľný;
- vysvetlený rizikom;
- stabilný voči tool/config zmenám;
- reviewovaný pri zmene exclusions.

Príklad Atlas policy:

```text
global line floor nesmie klesnúť
changed-code branch coverage >= 85 %
authorization decisions: 100 % named allow/deny scenarios
critical mutation score >= dohodnutý floor
coverage report: complete pre všetky shards
```

Číslo sa nekopíruje medzi repositories bez analýzy jazyka, generated code, legacy stavu a risk profilu.

## 23. Ratcheting

Ratcheting zabraňuje zhoršeniu a postupne zvyšuje accepted baseline:

```text
nové minimum
= max(organizational floor, predchádzajúci accepted state)
```

Ratchet možno použiť aj na uncovered critical branches, surviving mutants, exclusions, suppressions, flaky gate rate a duration.

Rast percenta musí vzniknúť lepším dôkazom, nie rozšírením exclusions alebo trivial tests.

## 24. Anti-gaming design

Coverage možno zvýšiť bez zvýšenia dôvery:

- calls bez meaningful assertions;
- testovanie trivial getters;
- široké exclusions;
- generated low-value code;
- broad E2E execution namiesto lokálnych tests;
- zmena denominatora alebo report scope-u;
- snapshot update bez review.

Ochrany sú branch/condition pohľady, mutation testing, named scenarios, review test intentu, exclusion audit a defect-escape feedback.

## 25. Worked failure: chýbajúci shard vytvoril false green

Atlas test suite mala štyri shards. Shard 4 obsahoval export component tests a zlyhal pred uploadom raw coverage.

```text
shard 1–3 uploadli reporty
→ merge job nenačítal očakávaný shard manifest
→ aggregate coverage 88 %
→ threshold 85 % prešiel
→ PR gate green
```

Po merge sa ukázalo, že nové export branches neboli v aggregate reporte vôbec prítomné.

### Root cause

Pipeline hodnotila percento bez completeness contractu. Chýbajúci producer zmenšil denominator aj evidence scope.

### Náprava

- build vytvára manifest očakávaných shards/processes;
- merge vyžaduje raw report a status každého producer-a;
- report obsahuje instrumented file inventory;
- chýbajúci shard je `COVERAGE_INCOMPLETE` a blocking;
- raw artifacts sa viažu na source a artifact digest;
- dashboard oddelí test failure od coverage infrastructure failure.

## 26. Tool failure a incomplete evidence

Rozlišuj:

```text
COMPLETE_PASS
COMPLETE_BELOW_POLICY
INCOMPLETE
TOOL_INFRA_FAILURE
WAIVED_FAILURE
```

Chýbajúci report sa nesmie interpretovať ako 0 % ani ako skipped-green. Fail-open alebo fail-closed semantics závisia od chráneného rozhodnutia, no unknown stav zostáva viditeľný.

## 27. Gate placement

Kontrola má bežať pred rozhodnutím, ktoré chráni, a čo najskôr pri dostatočnej fidelity:

```text
editor/local
→ formatter, targeted tests

pull request
→ build, unit, static, diff coverage, contracts

merge queue
→ synthetic-main integration a správny diff base

pre-release
→ širšia regression, security, performance

post-deploy
→ smoke, runtime policy a SLI
```

Coverage nemôže potvrdiť produkčný rollout. Post-deploy smoke nemôže nahradiť rýchly PR feedback.

## 28. Waiver lifecycle

Waiver povoľuje pokračovanie napriek známemu gate failure. Technický výsledok zostáva červený alebo označený `WAIVED`.

Waiver obsahuje:

- presný gate, candidate a scope;
- dôvod;
- impact a risk ownera;
- compensating control;
- expiry;
- remediation issue;
- approvals;
- audit trail;
- podmienku automatického zrušenia.

Permanentná waiver alebo prepis failure na green ničí auditovateľnosť gate-u.

## 29. Flaky gate a first-attempt evidence

Gate, ktorý náhodne zlyháva, stráca autoritu. Sleduj:

- first-attempt pass rate;
- recovery-on-retry rate;
- false-positive a infrastructure-failure rate;
- duration a queue time;
- local reproducibility;
- waiver frequency;
- ownera a time-to-remediation.

Rerun môže pomôcť diagnostike, ale nesmie odstrániť prvý failure z výsledku.

## 30. Provenance reportu a rozhodnutia

Autoritatívny report viaž na:

- source/synthetic merge commit;
- build artifact;
- shard a process manifest;
- tool/config version;
- exclusions;
- raw report digests;
- merge base;
- gate policy version;
- CI run a timestamp;
- final decision a waiver.

Bez provenance nemožno dokázať, že gate vyhodnotil správneho kandidáta.

## 31. Defect-escape feedback

Gate policy sa učí z incidentov:

```text
defect escape
→ identifikovať failure boundary
→ zistiť, ktorý dôkaz chýbal alebo bol slabý
→ pridať najnižší spoľahlivý regression control
→ upraviť coverage/gate model
→ sledovať recurrence
```

Ak defect vznikol v covered path-e, riešením nemusí byť vyšší threshold. Môže chýbať negative scenario, assertion, contract test alebo mutation sensitivity.

## 32. Diagnostický workflow

Keď coverage alebo gate neočakávane zlyhá:

1. potvrď candidate commit, artifact a target branch;
2. over diff base alebo synthetic merge identity;
3. načítaj expected shard/process manifest;
4. skontroluj raw reporty, flush a upload status;
5. over instrumentation inventory a source maps;
6. porovnaj tool, config a exclusion versions;
7. rozlíš uncovered behavior od neúplného reportu;
8. prečítaj uncovered branch v kontexte rizika;
9. over oracle cez mutation alebo named scenario;
10. pridaj meaningful test alebo úzku zdôvodnenú exclusion;
11. rerun autoritatívny complete gate nad rovnakým kandidátom;
12. waiver použi iba ako explicitné risk rozhodnutie.

## 33. Referenčné pravidlá

- Coverage je execution mapa, nie percento kvality.
- Kritický uncovered path je silný negatívny signal.
- Covered path potrebuje samostatné hodnotenie oraclu.
- Report je platný iba pri kompletnej instrumentation a merge.
- Diff coverage používa správny merge base.
- Branch/condition coverage sú významnejšie pri decision logic.
- Mutation testing meria citlivosť testov na semantic zmenu.
- Generated-code exclusions sa riadia ownershipom.
- Threshold je verzovaná risk policy, nie univerzálna konštanta.
- Gate kombinuje viac druhov dôkazu.
- Incomplete evidence nie je green.
- Waiver nemení technický výsledok.
- First-attempt evidence sa zachováva.
- Defect escapes spätne upravujú evidence portfolio.

## 34. Časté omyly

### „80 % coverage znamená 80 % kvality“

Coverage a kvalita nemajú lineárny vzťah. Metrika nevyjadruje business correctness, oracle ani impact.

### „100 % coverage znamená bezchybný systém“

Všetky probes môžu byť vykonané slabými alebo nesprávnymi scenármi.

### „Diff coverage chráni celý dopad zmeny“

Nepriame dependencies, konfigurácia a nezmenené paths môžu meniť behavior.

### „Chýbajúci shard iba znižuje coverage“

Mení scope dôkazu. Report je incomplete.

### „Mutation score musí byť 100 %“

Equivalent alebo low-value mutants existujú. Dôležitý je triage a critical scope.

### „Waiver robí pipeline zelenou“

Waiver povoľuje risk decision napriek známemu failure; evidence ostáva failure/waived.

### „Viac blocking gates vždy zvyšuje kvalitu“

Hlučné a pomalé gates zvyšujú bypassy, batch size a lead time.

## Doplnenie výkladu: denominator coverage a význam gate-u

Coverage je pomer pozorovaných programových prvkov k zvolenému denominatoru. **Line coverage** sleduje vykonané riadky, **branch coverage** výsledky podmienok, **function coverage** volané funkcie a **condition coverage** jednotlivé boolean časti. Hodnota 80 % bez uvedenia typu, scope a exclusions je neúplná.

Príklad:

```python
def classify(amount: int) -> str:
    if amount <= 0:
        return "invalid"
    if amount > 1000:
        return "review"
    return "accepted"
```

Jeden test s `amount=100` vykoná väčšinu riadkov, ale neoverí `invalid` ani `review` branch. Vysoká line coverage preto nemusí znamenať silný oracle. Test môže riadok vykonať bez assertion na jeho výsledok.

Coverage report odpovedá „čo testy vykonali“, nie „čo správne overili“. Chýbajúca coverage je užitočná mapa nepozorovaného kódu; prítomná coverage nie je dôkaz correctness.

**Mutation testing** skúša silu testov tak, že nástroj úmyselne zmení program, napríklad `>` na `>=` alebo odstráni volanie, a sleduje, či testy zlyhajú. Preživší mutant naznačuje slabý alebo chýbajúci oracle, ale nie každý mutant je významný alebo neekvivalentný.

Quality gate je policy decision nad evidence:

```text
coverage delta
+ blocking findings
+ test results
+ risk/ownership pravidlá
→ allow alebo block transition
```

Gate `coverage >= 80 %` môže motivovať bezcenné testy alebo trestať generated code. Lepší gate môže sledovať coverage zmeneného rizikového kódu, branch coverage a zakázaný pokles, pričom kritické paths majú explicitné tests nezávisle od percenta.

Pri pull requeste rozlišuj absolute a differential gate. Absolute gate hodnotí celý repository. Differential gate hodnotí novú zmenu. Oba potrebujú stabilný baseline; ak sa base branch medzitým zmenila, porovnanie sa môže stať stale.

Gate failure neznamená automaticky product defect. Môže ísť o missing report, parser error alebo policy service outage. Fail-open prekladá chýbajúce evidence na PASS a je nebezpečný pri required controls. Pipeline má odlíšiť `FAIL`, `ERROR` a `MISSING`, aby owner vedel, či opraviť kód, test alebo evidence path.

## 35. Zhrnutie

Atlas coverage a gate chain je:

```text
release candidate
→ complete instrumentation a test execution
→ line/branch/condition/diff pohľady
→ mutation a named critical scenarios
→ risk-weighted policy
→ complete pass, fail, unknown alebo waived
→ auditované merge/release rozhodnutie
→ defect-escape learning
```

Hlavný princíp je oddeliť execution evidence od decision evidence. Coverage ukazuje, čo sa vykonalo. Gate musí navyše posúdiť úplnosť reportu, kvalitu oraclu, kritické failure modes a význam výsledku pre konkrétny delivery krok.

## 36. Kontrolné otázky

1. Čo code coverage meria a čo nemeria?
2. Prečo je coverage silnejšia ako negatívny než pozitívny signal?
3. Aký instrumentation lifecycle vytvára report?
4. Ako sa líši line, branch a condition coverage?
5. Prečo aggregate coverage môže skryť zlú test-layer alokáciu?
6. Čo musí obsahovať complete shard/process merge?
7. Prečo diff coverage potrebuje merge base?
8. Aké limity má diff coverage pri nepriamych zmenách?
9. Čo mutation testing meria navyše oproti coverage?
10. Prečo tenant mutant prežil pri vysokej coverage?
11. Čo musí obsahovať quality-gate contract?
12. Ako sa líši blocking a advisory control?
13. Ako funguje ratcheting bez metric gaming-u?
14. Prečo chýbajúci shard vytvoril false green?
15. Aký je rozdiel medzi failure, incomplete a waived statusom?
16. Ako defect escape mení gate policy?

## Glossary impact

Relevantné pojmy: code coverage, instrumentation, line coverage, statement coverage, function coverage, branch coverage, condition coverage, path coverage, diff coverage, merge base, mutation testing, killed mutant, surviving mutant, quality gate, blocking control, advisory control, ratcheting, waiver, report provenance a incomplete evidence.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Static analysis, linting a type checking](static-analysis-linting-type-checking.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Mocks, stubs a fakes →](mocks-stubs-fakes.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
