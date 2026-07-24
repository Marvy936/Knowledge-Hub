# Static analysis, linting a type checking

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Testing and Software Quality
- Predpoklady: [Security a infrastructure tests](security-and-infrastructure-tests.md), [YAML, JSON a regular expressions](../03-git-and-automation/yaml-json-regular-expressions.md)
- Súvisiace témy: compiler diagnostics, AST, control-flow graph, data-flow analysis, taint analysis, soundness, baseline, suppression, incremental analysis

## 1. Mentálny model

Statická analýza odvodzuje vlastnosti programu alebo konfigurácie bez vykonania celého produkčného workflowu. Nástroj číta source, bytecode, intermediate representation alebo deklaratívny input, vytvorí interný model a porovná ho s jazykovými, typovými, bezpečnostnými alebo architektonickými pravidlami.

```text
source a configuration
→ parse a symbol resolution
→ AST/CFG/call graph/data-flow model
→ pravidlá a typové constraints
→ findings s location a evidence
→ triage, remediation alebo suppression
→ autoritatívny CI výsledok
```

Výsledok je kontrolný signál o analyzovanom modeli. Nie je to dôkaz, že celý systém funguje v runtime, že business pravidlo je správne alebo že externá dependency sa bude správať podľa očakávania.

## 2. Čo patrí do statickej kontrolnej vrstvy

Statická vrstva zahŕňa viac odlišných mechanizmov. Ich výsledky sa nemajú interpretovať ako jedna homogénna kategória.

- **Parser a compiler diagnostics** — odmietajú syntakticky neplatný program, neznáme symboly, neplatné typové operácie alebo platformovo nepodporovaný kód.
- **Formatter** — deterministicky normalizuje reprezentáciu kódu; rieši diffs a konzistentnosť, nie správnosť business behavioru.
- **Linter** — kontroluje suspicious patterns, conventions, portability, chybnú prácu s API a ďalšie pravidlá, ktoré compiler nemusí vynucovať.
- **Type checker** — overuje konzistenciu deklarovaných alebo odvodených typov, nullability a generických kontraktov.
- **Data-flow a control-flow analýza** — sleduje možné cesty vykonania, hodnoty a propagáciu stavu medzi blokmi alebo funkciami.
- **Security static analysis** — hľadá paths od nedôveryhodného source k nebezpečnému sinku, unsafe API alebo chýbajúcu validáciu.
- **Architecture checks** — vynucujú dependency direction, public API surface, ownership alebo zákaz importov medzi vrstvami.
- **Configuration a schema checks** — parsujú YAML, JSON, Terraform, Kubernetes alebo pipeline definície a overujú ich voči schéme alebo policy.

Kvalitný pipeline rozlišuje, ktorý nástroj vytvoril finding, aké má pokrytie a aké rozhodnutie má výsledok podporiť.

## 3. Prečo je statická analýza hodnotná

Statická kontrola môže bežať ešte pred zostavením deployovateľného systému a často dáva feedback v sekundách až minútach. Tým skracuje vzdialenosť medzi vznikom chyby a jej diagnostikou.

Jej silné vlastnosti sú:

- **široký codebase reach** — analyzátor môže prejsť aj paths, ktoré runtime test v konkrétnom behu nevykoná;
- **deterministickejší vstup** — rovnaký source, konfigurácia a toolchain majú typicky vytvoriť rovnaký výsledok;
- **presná lokalizácia** — finding môže ukázať file, line, symbol, path propagácie a rule ID;
- **nízka environment fidelity requirement** — veľa kontrol nepotrebuje databázu, sieť ani produkčné credentials;
- **automatizovateľnosť** — výsledok možno publikovať ako editor diagnostic, pull-request annotation, SARIF alebo machine-readable report.

Statická kontrola však nevie sama overiť skutočnú latency, behavior databázovej transakcie, platnosť credentials, runtime policy enforcement ani používateľský výsledok. Preto dopĺňa dynamické testy a observability, nie ich nahrádza.

## 4. Parsing, AST a symbol resolution

Analyzátor najprv potrebuje porozumieť syntaxe a symbolom. Abstract Syntax Tree reprezentuje štruktúru programu nezávisle od väčšiny formatting detailov.

```text
source text
→ tokens
→ syntax tree / AST
→ scopes a symbol table
→ type a semantic information
```

Na AST možno spoľahlivejšie rozlíšiť napríklad function call od textu v komentári. Symbol resolution určí, na ktorú function, class, variable alebo import sa referencia skutočne viaže.

Ak analyzátor nemá správny compiler mode, generated source, build flags, module path alebo dependency metadata, môže vytvoriť falošné findingy alebo časť kódu úplne vynechať. Tool invocation preto musí reprodukovať reálny build context.

## 5. Control-flow graph

Control-Flow Graph reprezentuje možné prechody medzi basic blocks programu.

```text
entry
→ condition
  ├─ true path
  └─ false path
→ merge
→ return
```

CFG umožňuje odhaliť napríklad:

- **unreachable branch** — cesta sa podľa analyzovaných podmienok nedá vykonať;
- **missing return** — niektorá cesta nekončí požadovanou hodnotou;
- **use before initialization** — premenná nemusí byť definovaná na každej ceste;
- **resource leak** — file alebo lock sa na niektorej failure path neuvoľní;
- **null dereference** — po konkrétnom branchi môže hodnota zostať null.

Presnosť CFG závisí od jazyka. Reflection, dynamic dispatch, runtime code generation a native extensions môžu obmedziť, čo vie nástroj spoľahlivo odvodiť.

## 6. Call graph a interprocedurálna analýza

Call graph modeluje možné volania medzi functions a methods. Interprocedurálna analýza prenáša informáciu cez tieto hranice.

```text
HTTP handler
→ parser
→ domain service
→ repository
→ SQL builder
```

Bez interprocedurálnej analýzy môže nástroj vidieť iba lokálnu function a prehliadnuť, že nedôveryhodný input sa po viacerých volaniach dostane k shell commandu. Na druhej strane celý call graph veľkého programu je drahý a pri dynamic dispatch môže obsahovať veľa hypotetických hrán.

Analyzátory preto používajú aproximácie. Tie zlepšujú škálovateľnosť, ale menia pomer false positives a false negatives.

## 7. Data-flow facts

Data-flow analýza sleduje vlastnosti hodnôt cez assignments, branches a calls. Typické facts sú:

- **nullability** — hodnota môže alebo nemôže byť null;
- **constant propagation** — analyzátor pozná konkrétnu konštantu;
- **range information** — integer je napríklad vždy medzi 1 a 65535;
- **ownership alebo lifetime** — resource bol otvorený, prenesený alebo uvoľnený;
- **taint state** — hodnota pochádza z nedôveryhodného source;
- **initialization state** — object alebo field už bol pripravený.

Facts sa pri spojení control-flow vetiev musia zlúčiť. Ak je value validná iba v jednej vetve, po merge pointe ju analyzátor nemôže automaticky považovať za validnú všade.

## 8. Taint analysis

Taint analysis sleduje cestu nedôveryhodných dát od source cez propagáciu až k sinku.

```text
request parameter
→ string concatenation
→ helper function
→ shell command sink
```

### Sources

Source je miesto, kde do systému vstupuje nedôveryhodná alebo citlivá hodnota. Môže to byť HTTP request, message, environment variable, uploaded file, database record, external API alebo command-line argument.

### Sinks

Sink je operácia, kde nesprávne spracovanie vytvára riziko. Príkladom je SQL execution, shell command, HTML rendering, filesystem path, deserialization, template engine, redirect URL alebo logging citlivých dát.

### Sanitizers a validators

Sanitizer musí byť správny pre konkrétny sink. HTML escaping nechráni SQL query a URL encoding nechráni shell command. Analyzer potrebuje poznať, ktoré functions reálne validujú, escapujú alebo parametrizujú hodnotu.

Custom wrappery bez modelu môžu spôsobiť false positive alebo false negative. Preto je dôležité udržiavať analyzátorové models spolu s aplikačnými abstractions.

## 9. Compiler diagnostics

Compiler diagnostics majú najbližšie k jazykovým invariantom. Zahŕňajú syntax errors, neznáme symbols, type mismatch, invalid generics, unsafe conversions, unsupported platform API alebo unreachable code.

Warning nie je automaticky menej dôležitý než error. Niektoré jazyky používajú warning pre behavior, ktoré je legálne, ale veľmi pravdepodobne chybné. Tím potrebuje severity policy:

```text
compiler error
→ build sa nedá vytvoriť

high-confidence warning
→ blocking gate

migration alebo style warning
→ advisory alebo ratcheted baseline
```

Policy „všetky warnings ako errors“ funguje iba vtedy, keď je warning set stabilný, presný a codebase nemá tisíce historických findings. Inak vedie k masovým suppression alebo k vypnutiu užitočnej kontroly.

## 10. Formatter a linter

Formatter a linter riešia rozdielne problémy.

```text
formatter
→ vytvorí jednu kanonickú reprezentáciu

linter
→ vyhodnotí pravidlo nad syntaxou alebo semantics
```

Automaticky opraviteľný style detail má spravidla patriť formatteru. Review a CI nemajú míňať pozornosť na medzery, ak ich vie nástroj deterministicky upraviť.

Lint rule má byť zdokumentovaná ako kontrola s dôvodom, nie ako anonymná preferencia. Pri každom pravidle treba vedieť:

- aké riziko alebo maintenance problém rieši;
- akú má presnosť;
- či je auto-fix bezpečný;
- či sa má spúšťať na changed files alebo na celý codebase;
- ako vyzerá oprávnený suppression;
- či finding blokuje merge alebo iba upozorňuje.

## 11. Type checking

Type checker overuje, či použitie hodnôt zodpovedá typovým kontraktom. V staticky typovanom jazyku je táto vrstva zvyčajne súčasťou compilera. Pri gradual typing-u funguje samostatný analyzátor nad annotations a inferred types.

Type systém pomáha odhaliť:

- nesprávny argument alebo návratový typ;
- neobslúžený null alebo optional stav;
- nekompatibilnú generic instantiation;
- neúplný union alebo variant handling;
- nesprávne implementované interface;
- breaking API zmenu pri refaktoringu.

Type checker nevaliduje nedôveryhodný runtime input. JSON payload môže byť typovo nesprávny ešte pred vytvorením typed objectu. Potrebná je parsing a runtime validation boundary.

```text
untrusted bytes
→ parser
→ runtime schema validation
→ typed internal model
→ type-checked business logic
```

## 12. Nullability a stavové typy

Nejasné optional hodnoty sú častým zdrojom chýb. Jeden `null` môže v neformálnom modeli znamenať viac stavov:

```text
hodnota neexistuje
hodnota ešte nebola načítaná
hodnota bola explicitne vymazaná
lookup zlyhal
používateľ nemá prístup
```

Silnejší typový model tieto stavy oddeľuje cez union, result type, option type alebo explicitný state object. Analyzer potom vie vynútiť spracovanie každej vetvy.

Suppression nullability warningu bez vysvetlenia iba prenesie neistotu do runtime. Bezpečnejšie je pridať guard, zmeniť contract alebo modelovať stav presnejšie.

## 13. Soundness, completeness a undecidability

Pre všeobecný program nemožno staticky a zároveň dokonale rozhodnúť všetky runtime vlastnosti. Praktický analyzátor preto volí kompromis medzi:

- **soundness** — snahou neprehliadnuť relevantný problém;
- **completeness** — snahou nehlásiť problém, ktorý sa nemôže stať;
- **execution cost** — časom a memory potrebnou na analýzu;
- **language dynamikou** — reflection, pluginy, generated code a runtime dispatch;
- **developer usability** — množstvom a akčnosťou findings.

Sound analyzer môže byť konzervatívny a hlásiť mnoho teoretických paths. Presnejší praktický nástroj môže vedome ignorovať niektoré dynamické prípady. Preto sa finding interpretuje spolu s confidence a coverage, nie ako absolútna pravda.

## 14. Security finding nie je exploit dôkaz

Static security finding typicky hovorí, že existuje možná cesta alebo risky pattern. Na triage treba doplniť:

- je source reálne attacker-controlled;
- je path reachable v nasadzovanom artifacte;
- má sink nebezpečné semantics;
- existuje vhodná validácia mimo modelu analyzátora;
- je vulnerable feature zapnutá;
- aký je exposure a business impact;
- či finding vznikol nad aktuálnym build contextom.

Vysoká presnosť je dôležitá pre blocking gate. Finding s neistým pathom môže byť stále hodnotný ako review signal, ale nemá automaticky blokovať všetky zmeny bez triage modelu.

## 15. Complexity a maintainability metrics

Statické nástroje môžu merať cyclomatic complexity, cognitive complexity, nesting, duplication, dependency cycles alebo size. Tieto metriky upozorňujú na oblasti so zvýšeným change riskom, nie na automaticky chybný kód.

Napríklad vysoká cyclomatic complexity znamená viac nezávislých control-flow ciest. To zvyšuje počet stavov, ktoré treba pochopiť a testovať. Nevysvetľuje však business kritickosť ani to, či je function správne abstrahovaná.

Metriky používaj na hotspot analysis a trend, nie ako gamifikovaný cieľ. Tvrdý limit bez kontextu môže viesť k mechanickému rozdeleniu function bez zlepšenia modelu.

## 16. Dead code a reachability

Dead-code analysis môže nájsť nepoužité symbols, zastarané feature paths, nevyužité dependencies alebo unreachable branches. Odstránenie dead code znižuje attack surface aj maintenance cost.

False positives vznikajú pri reflection, dependency injection, plugin discovery, serialization frameworks, template references alebo external invocation. Oprávnený suppression má vysvetliť runtime entry point a ideálne obsahovať test, ktorý väzbu overuje.

Generated code a source maps treba správne označiť. Finding v generovanom artifacte sa zvyčajne opravuje v generátore alebo source template, nie ručnou editáciou výstupu.

## 17. Architecture a dependency rules

Statická analýza môže vynucovať architektonický contract nad import graphom.

```text
presentation → application → domain
infrastructure → application/domain

domain ↛ infrastructure
```

Pravidlo má vyjadrovať dôvod hranice. Zákaz importu môže chrániť domain model pred vendor SDK, zabrániť cycle alebo udržať deployability. Bez vysvetlenia sa z architecture checku stane náhodná prekážka.

Path-based ownership a dependency rules sa dopĺňajú. CODEOWNERS určuje review zodpovednosť, ale nevynucuje runtime alebo compile-time dependency smer.

## 18. Configuration, policy a Infrastructure as Code

Rovnaký lifecycle platí pre konfiguráciu a deklaratívnu infraštruktúru:

```text
parse
→ schema
→ static policy
→ rendered/plan analysis
→ runtime verification
```

Syntax-valid YAML nemusí byť validný Kubernetes object. Schema-valid Terraform configuration nemusí mať bezpečný plan. Static IaC scanner nemusí poznať provider defaults ani efektívny runtime state.

Statická vrstva preto musí pomenovať, ktorú reprezentáciu analyzuje:

- authoring source;
- rendered template;
- dependency lock alebo module graph;
- Terraform plan;
- Kubernetes manifest po mutating admission;
- container image metadata.

## 19. Toolchain a configuration provenance

Výsledok závisí od verzie nástroja, rulesetu, compiler flags, dependency graphu a generated inputs. Autoritatívny run musí uchovať minimálne:

- commit alebo source revision;
- analyzer a plugin versions;
- config a ruleset version;
- target platform a language version;
- build flags alebo compilation database;
- excluded a generated paths;
- cache key a scope;
- machine-readable report.

Lokálny editor a CI majú používať kompatibilnú konfiguráciu. Rozdiel „lokálne zelené, CI červené“ často vzniká z odlišnej verzie, working directory, generated source alebo rulesetu.

## 20. Baseline pri existujúcom codebase

Zavedenie analyzátora do legacy codebase môže vytvoriť tisíce findings. Globálne ignorovanie ruší hodnotu nástroja, no okamžité blokovanie všetkého môže zastaviť delivery.

Praktický ratcheting model:

```text
1. odmerať existujúci stav
2. okamžite opraviť kritické high-confidence findings
3. uložiť explicitný baseline historického dlhu
4. blokovať nové alebo zhoršené findings
5. priradiť ownerov a redukčný cieľ
6. pravidelne baseline zmenšovať
7. po odstránení dlhu baseline zrušiť
```

Baseline musí byť verzovaný a auditovateľný. Nesmie sa automaticky regenerovať pri každom failure, pretože by legitimizoval novú regresiu.

## 21. Suppression governance

Suppression mení kontrolný contract. Má byť čo najužší a vysvetľovať, prečo je finding v danom kontexte false positive alebo akceptované riziko.

Kvalitný suppression obsahuje:

- presné rule ID a minimálny scope;
- technické zdôvodnenie;
- ownera;
- issue alebo risk-acceptance referenciu;
- expiry, ak je výnimka dočasná;
- kompenzačnú kontrolu, ak riziko ostáva;
- test alebo dôkaz, ktorý podopiera predpoklad.

Globálne vypnutie pravidla má byť výnimočné. Pred ním treba overiť tuning, framework model, custom sanitizer alebo oddelenie generated code.

## 22. Incremental a affected analysis

Veľký codebase potrebuje cache a incremental execution. Rýchlosť však nesmie zmeniť význam kontroly.

Changed-file linting je vhodný pre lokálne syntax a style pravidlá. Whole-program type analysis, architecture graph alebo interprocedurálny taint path môže závisieť od nezmenených súborov.

Bezpečný model kombinuje:

- editor alebo pre-commit analýzu changed files;
- PR affected analysis s dependency graphom;
- autoritatívny širší CI run;
- periodický clean run bez cache;
- invalidáciu cache pri zmene toolchainu, configu, dependencies alebo build flags.

Chybná cache môže vytvoriť false green. Cache key preto musí reprezentovať všetky vstupy, ktoré menia výsledok.

## 23. Feedback chain

Kontrola má byť dostupná čo najbližšie k autorovi zmeny, ale autoritatívne rozhodnutie patrí do kontrolovaného CI prostredia.

```text
editor diagnostic
→ local command
→ optional pre-commit hook
→ pull-request annotations
→ autoritatívny CI gate
→ trend a debt reporting
```

Pre-commit hook možno obísť a developer machine nie je bezpečnostná boundary. CI musí kontrolu zopakovať nad presným source revision a deklarovaným toolchainom.

## 24. Gate policy

Finding má blokovať merge iba vtedy, keď kontrola spĺňa prevádzkový contract:

- **relevance** — pravidlo chráni pomenované riziko alebo invariant;
- **precision** — false-positive rate je prijateľný;
- **reproducibility** — developer vie failure lokálne zopakovať;
- **actionability** — finding vysvetľuje opravu alebo ďalší diagnostický krok;
- **ownership** — je jasné, kto rieši tool aj code finding;
- **availability** — tool failure sa nerozlišuje od clean resultu;
- **latency** — kontrola dá feedback pred chráneným rozhodnutím;
- **exception path** — obídenie je explicitné, expirovateľné a auditovateľné.

Security taint path a formatting preference nemajú rovnakú severity. Ruleset potrebuje kategórie a odlišné gate semantics.

## 25. Tool failure verzus clean result

Ak analyzátor crashne, nenájde dependencies, prekročí timeout alebo preskočí polovicu projektu, výsledok nie je „0 findings“. Pipeline musí rozlišovať:

```text
analysis completed, no findings
analysis completed, findings exist
analysis incomplete
analysis infrastructure failed
```

Fail-open alebo fail-closed rozhodnutie závisí od rizika. Kritický security gate má spravidla zablokovať neúplnú analýzu; advisory style job môže výpadok reportovať bez blokovania. V oboch prípadoch musí byť stav viditeľný.

## 26. Reportovanie a developer experience

Akčný finding má obsahovať file, line, symbol, rule ID, severity, vysvetlenie rizika a remediation. Pri data-flow probléme má ukázať relevantný source-to-sink path.

Machine-readable report umožňuje deduplikáciu, trendovanie a integráciu s pull requestom. Fingerprint findings musí zostať dostatočne stabilný, aby rovnaký problém nevznikal ako nový ticket pri každom posune riadku.

Tisíce duplicitných alebo neakčných findings vytvárajú noise floor. Tuning, framework models a kvalitné defaults sú súčasťou security aj quality engineeringu.

## 27. Meranie účinnosti

Počet zapnutých pravidiel nie je dobrá metrika kvality. Sleduj skôr:

- findings podľa severity a rule;
- first-seen a age;
- time to remediation;
- suppression a baseline trend;
- false-positive rate;
- analyzer failure rate a duration;
- percento codebase reálne analyzované;
- defecty alebo incidenty, ktoré kontrola zachytila či prepustila;
- developer rerun a local reproducibility rate.

Kontrola, ktorú všetci obchádzajú alebo ktorá často zlyháva bez diagnostiky, neplní svoj účel ani pri vysokej teoretickej kvalite pravidiel.

## 28. Diagnostický workflow

Pri nečakanom findingu alebo rozdiele medzi lokálnym a CI výsledkom:

1. potvrď presný commit a analyzovanú path;
2. over verziu analyzátora, pluginov a konfigurácie;
3. skontroluj language target, build flags a generated sources;
4. reprodukuj command bez cache;
5. prečítaj rule documentation a celý data-flow path;
6. rozlíš skutočný problém, model gap a false positive;
7. over, či framework wrapper alebo sanitizer potrebuje model;
8. oprav source, contract alebo analyzer model;
9. suppression použi iba s explicitným dôkazom;
10. over, že CI znova analyzovalo relevantný scope.

## 29. Časté omyly

### „Linter prešiel, program funguje“

Linter pokrýva iba svoje rules a statický model. Runtime dependency, business invariant alebo latency môže stále zlyhať.

### „Type hints validujú API payload“

Annotations chránia typed code po parsing boundary. Nedôveryhodný input potrebuje runtime validáciu.

### „Všetky warnings treba okamžite blokovať“

Bez severity modelu a baseline môže politika vytvoriť suppression debt a zničiť dôveru v gate.

### „Suppression opravil finding“

Suppression odstránil signal. Riziko ostáva, pokiaľ neexistuje dôkaz, že finding je neplatný alebo kontrolovaný inak.

### „Changed-file scan stačí“

Cross-file typový, architecture alebo data-flow problém môže vzniknúť mimo priamo zmeneného súboru.

### „Analyzer timeout znamená, že nič nenašiel“

Neúplný run nie je clean evidence. Musí mať samostatný failure stav.

## 30. Prevádzkový checklist

- Je toolchain a ruleset pinovaný a reprodukovateľný?
- Analyzuje sa rovnaký build context ako pri skutočnom zostavení?
- Sú generated a excluded paths explicitné?
- Je rozdiel medzi formatterom, linterom, compilerom a security analyzerom jasný?
- Má každý blocking rule pomenované riziko a remediation?
- Rozlišuje pipeline findings, incomplete run a infrastructure failure?
- Je baseline verzovaný a zmenšuje sa?
- Sú suppression úzke, zdôvodnené a reviewované?
- Invaliduje sa incremental cache pri všetkých relevantných zmenách?
- Existuje periodický clean whole-program run?
- Dostane developer finding pri file a line spolu s rule ID?
- Meria sa precision, duration, coverage a remediation trend?

## 31. Kontrolné otázky

1. Aký je rozdiel medzi parserom, formatterom, linterom a type checkerom?
2. Čo reprezentujú AST, control-flow graph a call graph?
3. Ako data-flow analýza spája facts z rôznych branches?
4. Ako funguje source, propagation, sanitizer a sink v taint analýze?
5. Prečo static analyzer nemôže byť zároveň dokonale sound aj complete pre všetky programy?
6. Prečo type checking nenahrádza runtime input validation?
7. Ako zaviesť blocking analyzer do legacy codebase bez permanentného baseline dlhu?
8. Aké podmienky má spĺňať oprávnený suppression?
9. Prečo changed-file analysis nestačí pre všetky pravidlá?
10. Ako musí pipeline rozlíšiť clean result od neúplnej analýzy?
11. Kedy má finding blokovať merge a kedy má byť advisory?
12. Ako overíš, že analyzer skutočne spracoval celý zamýšľaný scope?

## Glossary impact

Relevantné pojmy: static analysis, compiler diagnostic, formatter, linter, type checker, gradual typing, AST, control-flow graph, call graph, symbol table, data-flow analysis, taint analysis, source, sink, sanitizer, soundness, completeness, baseline, suppression, incremental analysis, architecture rule a SARIF.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Security a infrastructure tests](security-and-infrastructure-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Code coverage a quality gates →](code-coverage-and-quality-gates.md)
<!-- KNOWLEDGE-NAVIGATION:END -->