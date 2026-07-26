# Static analysis, linting a type checking

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Testing and Software Quality
- Predpoklady: [Security a infrastructure tests](security-and-infrastructure-tests.md), [YAML, JSON a regular expressions](../03-git-and-automation/yaml-json-regular-expressions.md)
- Súvisiace témy: compiler diagnostics, AST, control-flow graph, call graph, data-flow analysis, taint analysis, soundness, baseline, suppression, incremental analysis

Statická kontrolná vrstva odvodzuje vlastnosti source kódu alebo konfigurácie bez vykonania celého produkčného workflowu. Jej sila spočíva v skorom a presne lokalizovanom feedbacku; jej hranicou je, že pracuje s modelom programu, nie so skutočným runtime výsledkom.

```text
source a build context
→ parse a symbol resolution
→ AST, CFG, call graph a data-flow model
→ pravidlá a typové constraints
→ finding s location a evidence pathom
→ triage, fix alebo expirovateľná suppression
→ autoritatívny CI verdict
→ runtime dôkaz v príslušnej vyššej vrstve
```

Formatter, linter, type checker a security analyzer preto nie sú štyri názvy pre tú istú kontrolu. Každý z nich vytvára iný interný model, hľadá inú triedu failure a poskytuje inak silný dôkaz.

## 1. Cieľ kapitoly

Nosný rozhodovací model kapitoly je:

```text
riziko alebo jazykový invariant
→ zvoliť statický model, ktorý ho vie reprezentovať
→ spustiť nástroj v reálnom build contexte
→ vyhodnotiť finding, confidence a blind spots
→ priradiť blocking alebo advisory význam
→ opraviť source alebo riadene potlačiť konkrétny nález
→ potvrdiť výsledok compilerom, testom alebo runtime kontrolou
```

Statická analýza nie je náhrada testov. Je najnižšia spoľahlivá vrstva pre failures, ktoré možno odvodiť zo source alebo deklaratívneho modelu bez potreby reálneho execution environmentu.

## 2. Nosný scenár: Atlas Orders 3.9.1

Atlas pripravuje zmenu exportu objednávok. HTTP handler prijme filter, vytvorí `ExportCommand`, uloží job a worker neskôr vytvorí CSV v object storage.

```text
POST /exports
→ parse request
→ authenticated tenant context
→ ExportCommand
→ repository
→ queue event
→ export worker
→ CSV serializer
→ object storage
```

Zmena prináša štyri staticky detegovateľné riziká:

1. request field `tenantId` sa môže dostať do commandu namiesto server-owned tenant identity;
2. optional `Retry-After` header sa môže použiť bez kontroly `None`;
3. export filename sa môže skladať z nedôveryhodného vstupu a dostať do filesystem pathu;
4. nový worker package môže importovať internú persistence vrstvu, čím obíde povolenú architektonickú boundary.

Atlas potrebuje viac než jeden tool:

```text
formatter
→ kanonická reprezentácia diffu

compiler/type checker
→ nullability, typy a neúplný state handling

linter
→ suspicious API usage a lokálne pravidlá

data-flow/SAST
→ source-to-sink cesta tenantId alebo filename

architecture check
→ zakázaná dependency direction
```

## 3. Čo statický výsledok skutočne dokazuje

Finding dokazuje, že analyzátor vo svojom modeli našiel porušenie pravidla alebo možnú failure path. Sila dôkazu závisí od troch vecí:

```text
model completeness
× presnosť pravidla
× správny build context
```

Ak chýbajú generated sources, production flags alebo dependency metadata, model nemusí obsahovať reálnu cestu. Ak je pravidlo heuristické, finding môže byť false positive. Ak analyzátor používa nepresnú aproximáciu dynamic dispatchu, môže naopak vytvoriť false negative.

Zelený statický job teda znamená:

> V analyzovanom scope-e a konfigurácii nebolo nájdené porušenie aktívnych pravidiel.

Neznamená:

> Program je funkčne správny a bezpečný v produkcii.

## 4. Source a build context ako vstup dôkazu

Autoritatívny run musí poznať rovnaký kontext, ktorý používa reálny build:

- source revision a submodules;
- language a compiler version;
- target platform a feature flags;
- dependency lock a module path;
- generated code a annotation processors;
- preprocessor symbols alebo build profiles;
- analyzer ruleset, plugins a configuration;
- exclusions a suppressions;
- incremental cache identity.

Atlas worker sa zostavuje s feature flagom `OBJECT_STORAGE_EXPORTS`. Ak analyzer beží bez tohto symbolu, export path môže byť zo symbol resolution a call graphu úplne odstránený. Zelený výsledok potom patrí inému programu než release artifact.

## 5. Parsing, AST a symbol resolution

Prvá fáza premieňa text na štruktúru:

```text
source bytes
→ tokenization
→ syntax tree / AST
→ scopes a symbol table
→ resolved imports a calls
→ typové a semantic facts
```

AST umožní rozlíšiť function call od rovnakého textu v komentári alebo stringu. Symbol resolution určí, či `save()` znamená repository method, lokálnu helper function alebo import z iného package-u.

Parser error je silný dôkaz, že daný input nemožno spracovať očakávaným toolchainom. Zelený parser však nehovorí, že program má správne typy, behavior alebo policy.

## 6. Control-flow graph

Control-Flow Graph modeluje možné prechody medzi basic blocks:

```text
entry
→ parse Retry-After
→ value exists?
   ├─ áno → convert a schedule
   └─ nie → default alebo error
→ return
```

CFG podporuje findings ako unreachable branch, missing return, use-before-initialization, resource leak alebo možný null dereference. Pri Atlas workerovi môže type checker zistiť, že `retry_after` zostane `None` na vetve, ktorá následne volá numeric conversion.

Model má limity. Reflection, runtime code generation, native extensions a highly dynamic dispatch môžu vytvárať hrany, ktoré analyzátor nevie presne odvodiť.

## 7. Call graph a interprocedurálna analýza

Call graph prepája functions a methods:

```text
HTTP handler
→ create_export_command
→ enqueue_export
→ worker.handle
→ build_filename
→ filesystem/object-store adapter
```

Lokálna analýza handlera nemusí vidieť, že request filename po štyroch calls skončí vo filesystem sinku. Interprocedurálna analýza prenáša facts cez function boundaries, ale je drahšia a často používa aproximácie.

Príliš široký call graph zvyšuje false positives. Príliš úzky graph vytvára false negatives. Výsledok preto potrebuje evidence path, aby reviewer vedel posúdiť, ktoré hrany analyzátor predpokladal.

## 8. Data-flow a taint model

Data-flow analysis sleduje vlastnosti values cez assignments, branches a calls. Taint analysis je špeciálny prípad:

```text
source
→ propagácia
→ validator alebo sanitizer
→ sink
```

Pre Atlas cross-tenant riziko:

```text
request.body.tenantId        # nedôveryhodný source
→ ExportRequest.tenant_id
→ ExportCommand.tenant_id
→ worker query filter         # authorization-sensitive sink
```

Správny design má inú cestu:

```text
authenticated_context.tenant_id
→ server-owned command field
→ immutable event context
→ tenant-scoped query
```

Analyzer potrebuje modelovať, že authenticated context je trusted source a request field nie. Generic rule „string sa dostal do query“ nestačí na business authorization rozhodnutie.

## 9. Sources, sinks, validators a sanitizers

Source je miesto vstupu nedôveryhodnej alebo citlivej hodnoty: HTTP request, message, environment variable, uploaded file, database record, external API alebo CLI argument.

Sink je operácia, kde nesprávna value vytvára riziko: SQL execution, shell command, HTML rendering, filesystem path, deserialization, redirect URL, logging alebo authorization decision.

Validator a sanitizer musia byť vhodné pre konkrétny sink. HTML escaping nechráni SQL query a path normalization nemusí chrániť object-storage authorization. Custom wrapper bez analyzer modelu môže spôsobiť false positive aj false negative.

## 10. Compiler diagnostics

Compiler kontroluje jazykové invariants potrebné na vytvorenie programu. Môže odmietnuť syntax error, neznámy symbol, invalid generic, type mismatch alebo nepodporovaný platform call.

Warning môže byť rovnako významný ako error, ale potrebuje policy:

```text
compiler error
→ artifact nemožno vytvoriť

high-confidence correctness warning
→ blocking

migration alebo compatibility warning
→ advisory alebo ratcheted baseline

style concern
→ formatter/linter podľa ownershipu
```

„Warnings as errors“ je udržateľné iba pri stabilnom a vlastnenom warning sete. Zapnutie na legacy codebase bez baseline často vedie k masovým suppression, nie k pochopeniu rizika.

## 11. Type checking ako contract medzi stavmi

Type checker overuje, či values a operations zodpovedajú deklarovaným alebo odvodeným typom. Najväčšiu hodnotu má, keď typy reprezentujú doménové stavy namiesto generic stringov a nullable flags.

Slabý model:

```text
status: str
error: str | None
result: Export | None
```

Silnejší model:

```text
ExportPending
ExportRunning
ExportSucceeded(result)
ExportFailed(reason)
```

Discriminated union alebo sealed hierarchy umožní checkeru odhaliť neúplný state handling. Typový systém tým presunie časť runtime failure do build-time decisionu.

## 12. Runtime input zostáva nedôveryhodný

Type checking interného programu nevaliduje bytes z networku:

```text
untrusted JSON bytes
→ parser
→ runtime schema validation
→ authenticated/authorized transformation
→ typed domain model
→ type-checked business logic
```

Type assertion, cast alebo deserialization annotation nemusí runtime value skontrolovať. Atlas testuje schema boundary dynamicky a typy používa až po úspešnej validácii.

## 13. Formatter

Formatter deterministicky vytvára jednu kanonickú reprezentáciu source. Jeho hlavný prínos je:

- menší diff noise;
- menej konfliktov o whitespace;
- jednoduchší review behavior zmien;
- reprodukovateľný generated output;
- lacný editor a pre-commit feedback.

Formatter nevie, či tenant identity pochádza zo správneho source-u. Je to representation control, nie behavior oracle.

Check mode musí analyzovať rovnaký file set ako write mode. Inak môže lokálny formatter meniť files, ktoré CI nekontroluje, alebo naopak.

## 14. Linter

Linter aplikuje syntaktické alebo semantic rules, ktoré compiler nemusí vynucovať. Dobré pravidlo má:

```text
risk alebo maintenance invariant
→ pattern/model
→ finding s rule ID a vysvetlením
→ bezpečný autofix alebo manuálna remediation
→ suppression contract
```

Atlas môže mať custom rule, ktorá zakáže čítať `tenantId` z API DTO pri tvorbe server-owned commandu. Také pravidlo chráni architektonický invariant, nie iba coding style.

Autofix je bezpečný iba vtedy, keď zachová semantics. Import sorting alebo whitespace sú vhodné. Automatická zmena authorization expression potrebuje ľudský review a testy.

## 15. Architecture checks

Architecture rule vynucuje dependency direction alebo ownership boundary. Atlas používa model:

```text
domain
← application
← adapters
← entrypoints
```

Export worker môže používať application port, ale nesmie importovať internú SQL implementation z `orders-api`. Taký import vytvára coupling na schema a obchádza testované repository contracty.

Architecture check môže analyzovať imports, packages, public API surface alebo dependency graph. Runtime plugin loading a generated dependencies však môžu vyžadovať doplnkový integration test.

## 16. Configuration a declarative static checks

Rovnaký model platí pre YAML, Terraform, Kubernetes a pipeline definitions:

```text
source
→ parse
→ schema
→ cross-field invariants
→ policy
→ rendered/plan/runtime dôkaz
```

Schema validation odhalí neplatný field alebo typ. Neodhalí automaticky public exposure, nebezpečný rollout alebo effective IAM. Tieto risks patria do policy, plan a runtime vrstvy vysvetlenej v predchádzajúcej kapitole.

## 17. Soundness a completeness

V praxi sa analyzátory pohybujú medzi dvoma cieľmi:

- **soundness** — ak tool tvrdí, že určitá chyba nemôže nastať, model sa snaží nepovoliť false negative pre danú triedu;
- **completeness** — tool sa snaží nehlásiť paths, ktoré v realite nemôžu nastať.

Úplná soundness aj completeness sú pri všeobecnom programe nedosiahnuteľné. Tool používa konzervatívne aproximácie, heuristiky alebo obmedzený scope.

Pre blocking gate je preto dôležitá nie marketingová kategória nástroja, ale empirická precision, coverage modelu a význam konkrétneho rulesetu.

## 18. Finding triage

Finding má obsahovať:

- rule ID a severity;
- file, symbol a source revision;
- evidence alebo data-flow path;
- analyzer a ruleset version;
- confidence;
- affected artifact alebo component;
- remediation guidance;
- suppression stav;
- ownera.

Reviewer najprv overí, či model obsahuje reálny execution path. Potom posúdi, či path porušuje contract. Finding bez build contextu a evidence pathu je slabý vstup do blocking rozhodnutia.

## 19. Worked failure: analyzer nevidel produkčný export path

Atlas CI spúšťala SAST nad default build profilom. Export worker sa však kompiloval iba s flagom `OBJECT_STORAGE_EXPORTS`.

```text
CI analyzer bez feature flagu
→ export module nebol v call graphe
→ filename source-to-filesystem sink neexistoval
→ SAST green
→ release artifact obsahoval export path
→ crafted filename vytvoril object key mimo tenant prefixu
```

### Root cause

Analyzer a release build nepoužívali rovnaký compilation context. Zelený report patril zjednodušenému programu, nie publikovanému artifactu.

### Náprava

- analyzer používa authoritative build command a production feature set;
- CI zaznamená resolved flags, generated files a dependency graph;
- export module dostane targeted taint rule a unit regression;
- component test overí object key a tenant prefix cez reálny serializer/adapter;
- coverage report kontroluje, či export package bolo analyzované;
- chýbajúci analyzer scope je `INCOMPLETE`, nie green.

## 20. Worked failure: suppression skryla zmenu contractu

Type checker pôvodne hlásil, že `Retry-After` môže byť `None`. Tím pridal file-level suppression, pretože starý client header vždy vracal string.

```text
provider client upgrade
→ missing header sa začal mapovať na None
→ file-level suppression ostala aktívna
→ numeric conversion dostala None
→ worker spadol pred naplánovaním retry
```

### Root cause

Suppression bola príliš široká, nemala ownera ani expiry a chránila predchádzajúci assumption namiesto explicitného invariant testu.

### Náprava

- optional state sa modeluje typom a explicitným branchom;
- suppression sa odstráni;
- narrow suppression je povolená iba s rule ID, dôvodom a issue;
- regression test pokrýva missing, invalid a valid header;
- suppression count a age sa ratchetujú.

## 21. Baseline a zavedenie do legacy codebase

Existujúci codebase môže mať tisíce findings. Okamžité globálne blocking pravidlo vedie k vypnutiu toolu alebo nečitateľným suppression.

Riadený lifecycle:

```text
inventory run
→ klasifikovať rules a false positives
→ uložiť versioned baseline
→ blocking pre nové findings
→ opravovať prioritné historické findings
→ znižovať baseline
→ odstrániť baseline po dosiahnutí cieľa
```

Baseline nie je zoznam „akceptovaných chýb“. Je dočasný migration mechanism s ownerom, trendom a reviewom.

## 22. Suppression lifecycle

Oprávnená suppression má:

- presný rule ID;
- najmenší scope;
- technický dôvod;
- ownera;
- issue alebo risk decision;
- expiry alebo review date;
- alternatívny dôkaz, ak riziko zostáva;
- zákaz maskovania nových findings širokým wildcardom.

Inline suppression je často auditovateľnejšia než globálny ignore, pretože reviewer vidí context. Generated code alebo vendor source môže používať central exclusion, ale ownership a dôvod musia zostať explicitné.

## 23. Blocking a advisory rules

Blocking je vhodný pre presný, reprodukovateľný a akčný signal:

- compiler/type error;
- high-confidence null dereference;
- zakázanú architecture dependency;
- new secret finding;
- known source-to-dangerous-sink path s reálnou reachability;
- schema alebo policy violation s jasným contractom.

Advisory je vhodný pri novom rulesete, heuristickom complexity signále alebo nízkej precision. Advisory finding však potrebuje dashboard, ownera a rozhodnutie, kedy sa stane blocking alebo sa odstráni.

## 24. Tool failure a incomplete evidence

Pipeline musí rozlišovať:

```text
analysis completed bez findings
analysis completed s findings
analysis incomplete
model/build context invalid
ruleset alebo cache stale
tool unavailable
```

Parser crash, chýbajúci generated source alebo analyzer timeout nie sú „no findings“. Pre kritický gate môže unknown dôkaz viesť k fail-closed. Pri advisory tool-e môže pokračovanie zostať povolené, ale stav musí byť viditeľný a auditovaný.

## 25. Incremental analysis a cache

Incremental analyzer zrýchľuje feedback použitím predchádzajúcich výsledkov. Cache key musí zahŕňať:

- source a dependency revision;
- compiler flags;
- tool a plugin versions;
- ruleset a suppression config;
- generated source identity;
- target platform;
- relevantný environment model.

Zmena shared interface alebo analyzer modelu musí invalidovať dependents. Stale cache môže vytvoriť false green, aj keď samotný tool je presný.

## 26. Generated code

Generated output sa hodnotí podľa ownershipu:

```text
vendor-generated glue
→ overiť generator/spec a compile compatibility

tímom vlastnená template
→ testovať generator, output invariants a representative output

generated client ako public contract
→ compile, contract a smoke dôkaz
```

Exclusion generated files nesmie skryť vlastnú business logiku vloženú do templates. Analyzer report má uviesť, čo bolo vylúčené a prečo.

## 27. Local feedback a authoritative CI

Editor poskytuje najrýchlejší signal, ale developer settings môžu byť odlišné. Autoritatívny CI run preto používa pinovaný toolchain a repository config.

```text
editor
→ okamžitá diagnostika

pre-commit
→ formatter a targeted fast rules

pull request CI
→ full authoritative model a gate

scheduled analysis
→ drahé interprocedurálne rules, whole-repo a trend
```

Lokálna a CI konfigurácia majú zdieľať rovnaký source of truth, aby developer nedostával konfliktujúce verdicts.

## 28. Failure artifacts a provenance

Uchovaj:

- source/synthetic merge commit;
- build command a resolved flags;
- analyzer, compiler, plugin a ruleset versions;
- included/excluded file inventory;
- cache hit/miss a key;
- generated-source manifest;
- machine-readable findings;
- evidence paths;
- suppression/baseline version;
- completion status a duration.

Bez provenance nie je možné potvrdiť, že report patrí k reviewovanému release kandidátovi.

## 29. Diagnostický workflow

Keď statický job zlyhá alebo podozrivo prejde:

1. potvrď source commit, target a authoritative build command;
2. over compiler flags, platform a generated sources;
3. skontroluj, či analyzovaný file/symbol patrí do inventory;
4. reprodukuj finding rovnakou tool a ruleset verziou;
5. prečítaj evidence path a resolved symbols;
6. rozlíš reálny contract failure od nepresnej modelovej hrany;
7. over cache invalidation a baseline/suppression;
8. pri false negative pridaj alebo oprav analyzer model;
9. pridaj najnižší runtime alebo behavior regression test;
10. over autoritatívny first-attempt rerun bez novej broad suppression.

## 30. Referenčné pravidlá

- Statický výsledok patrí konkrétnemu source a build contextu.
- Parser, formatter, linter, type checker a SAST poskytujú odlišný dôkaz.
- Type safety nezačína pred runtime parsing a validation boundary.
- Data-flow rule potrebuje explicitné sources, sinks a validators.
- Zelený analyzer nepreukazuje runtime behavior.
- Build flags a generated code musia zodpovedať release artifactu.
- Blocking rules majú byť presné, reprodukovateľné a vlastnené.
- Baseline je dočasný ratchet, nie permanentný ignore list.
- Suppression má minimálny scope, ownera a expiry.
- Incomplete analysis je unknown evidence, nie green.
- Incremental cache key zahŕňa celý semantic context.
- Finding potrebuje runtime alebo behavior potvrdenie podľa rizika.

## 31. Časté omyly

### „Compiler prešiel, program funguje“

Compiler overuje jazykové invariants, nie business výsledok, databázovú transaction semantics ani externý contract.

### „Formatter zvyšuje correctness“

Formatter znižuje representation noise. Behavior nemení, pokiaľ nemá chybný alebo semantic autofix.

### „Type checker validuje JSON“

Typed interný model vzniká až po runtime parsing a validation.

### „SAST green znamená žiadnu injection alebo authorization chybu“

Analyzer vidí iba modelované sources, sinks, calls a build variants.

### „Finding potlačíme, pretože je false positive“

Suppression potrebuje dokumentovaný modelový dôvod a minimálny scope. Inak môže maskovať budúcu reálnu chybu.

### „Analyzer timeout je infra problém, merge môže byť green“

Je to chýbajúci dôkaz. Gate potrebuje explicitnú unknown policy.

### „Incremental run vždy stačí pre pull request“

Stale dependency graph alebo config change môže vyžadovať whole-repo reanalysis.

## 32. Zhrnutie

Atlas statická evidence chain je:

```text
release source a build context
→ parse/symbol model
→ AST + CFG + call/data flow
→ compiler/type/lint/security/architecture rules
→ findings a blind spots
→ fix alebo riadená suppression
→ authoritative CI verdict
→ dynamický regression dôkaz
```

Hlavný princíp je model fidelity. Statický tool môže byť technicky správny a napriek tomu vytvoriť false green, ak analyzuje iný build variant, nevidí generated source alebo používa stale cache. Výsledok sa preto interpretuje iba spolu so scope-om, configuration provenance a failure semantics.

## 33. Kontrolné otázky

1. Aký evidence lifecycle používa statická analýza?
2. Prečo zelený analyzer nie je runtime dôkaz?
3. Aký význam majú AST, CFG a call graph?
4. Ako taint analysis prepája source, propagáciu, validator a sink?
5. Prečo musí analyzer používať reálny build context?
6. Čo navyše poskytuje type checker oproti parseru?
7. Prečo typed model nevaliduje nedôveryhodný JSON?
8. Aký je rozdiel medzi formatterom a linterom?
9. Ako architecture check chráni Atlas worker boundary?
10. Ako chýbajúci feature flag vytvoril false-green SAST report?
11. Prečo file-level suppression skryla `Retry-After` failure?
12. Ako funguje baseline a ratcheting v legacy codebase?
13. Aké vlastnosti má oprávnená suppression?
14. Kedy má statická kontrola blokovať merge?
15. Čo znamená incomplete analysis pre gate?
16. Čo musí obsahovať cache key incremental analyzéra?

## Glossary impact

Relevantné pojmy: static analysis, compiler diagnostic, formatter, linter, type checker, AST, Control-Flow Graph, call graph, interprocedural analysis, data-flow analysis, taint analysis, source, sink, sanitizer, validator, soundness, completeness, architecture test, baseline, suppression, incremental analysis, analyzer provenance a incomplete evidence.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Security a infrastructure tests](security-and-infrastructure-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Code coverage a quality gates →](code-coverage-and-quality-gates.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
