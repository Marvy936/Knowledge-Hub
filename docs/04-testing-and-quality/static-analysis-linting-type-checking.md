# Static analysis, linting a type checking

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

## 1. Definícia

Static analysis skúma source code alebo jeho reprezentáciu bez vykonania celej aplikácie. Cieľom je zachytiť chyby, porušenia pravidiel a rizikové patterns skôr než sa prejavia v runtime.

Do tejto vrstvy patria najmä:

- parser a compiler diagnostics,
- linting,
- type checking,
- data-flow a control-flow analysis,
- security analysis,
- dead-code a complexity analysis,
- configuration a schema validation.

## 2. Prečo je statická kontrola dôležitá

Je:

- rýchla,
- deterministickejšia než runtime testy,
- vhodná pre editor a pre-commit feedback,
- ľahko paralelizovateľná,
- schopná pokryť veľký codebase bez prípravy prostredia.

Nemôže však dokázať všetky runtime vlastnosti, napríklad reálnu latency, správne credentials alebo správanie externého systému.

## 3. Compiler diagnostics

Compiler môže odhaliť:

- syntax errors,
- neplatné symboly,
- type mismatches,
- unreachable code,
- neinitializované hodnoty,
- unsafe conversions,
- platform alebo API incompatibility.

Warnings majú byť spravované ako verzovaný quality signal. Ignorované warnings vytvárajú noise floor, v ktorom sa nové problémy stratia.

## 4. Linting

Linter kontroluje pravidlá, ktoré compiler nemusí vynucovať:

- conventions,
- suspicious constructs,
- portability,
- maintainability,
- error-prone API usage,
- security patterns,
- formatting podľa konfigurácie.

Lint rule má mať:

- jasný dôvod,
- primeranú presnosť,
- konzistentnú konfiguráciu,
- možnosť lokálnej reprodukcie,
- dokumentovaný suppression mechanizmus.

## 5. Formatter vs. linter

Formatter automaticky normalizuje reprezentáciu kódu. Linter analyzuje semantics alebo conventions.

```text
formatter → ako kód vyzerá
linter    → ktoré patterns sú povolené alebo rizikové
```

Automaticky opraviteľné style pravidlá je lepšie riešiť formatterom než blokujúcimi diskusiami v review.

## 6. Type checking

Type checker overuje konzistenciu typových kontraktov.

### Static typing

Typy sú súčasťou jazyka a compiler ich typicky vynucuje.

### Gradual typing

Dynamický jazyk umožňuje pridávať type annotations a analyzovať ich samostatným nástrojom.

Type hints môžu zlepšiť:

- API contracts,
- refactoring safety,
- IDE navigation,
- nullable-state reasoning,
- data model clarity.

Type checker však neoveruje automaticky business invariants ani nedôveryhodný runtime input.

## 7. Soundness a completeness

Statický analyzátor robí trade-off medzi:

- false positives,
- false negatives,
- runtime cost analýzy,
- jazykovou dynamikou,
- škálovateľnosťou na veľký codebase.

Praktické nástroje často nie sú úplne sound ani complete. Výsledok treba interpretovať ako kontrolný signál, nie matematický dôkaz celej aplikácie.

## 8. AST, CFG a data-flow

Pokročilejšia analýza používa:

- AST — Abstract Syntax Tree,
- CFG — Control-Flow Graph,
- call graph,
- symbol table,
- data-flow facts,
- interprocedural analysis.

Príklad taint analýzy:

```text
untrusted request input
→ propagácia cez premenné
→ nebezpečný SQL/command sink
```

## 9. Taint analysis

Taint analysis sleduje dáta od source po sink.

Sources:

- HTTP input,
- environment,
- file upload,
- message queue,
- external API.

Sinks:

- SQL query,
- shell command,
- HTML output,
- filesystem path,
- deserialization,
- log alebo telemetry field.

Sanitizer musí byť správny pre konkrétny sink. HTML escaping nechráni SQL query.

## 10. Nullability a optional values

Mnoho runtime chýb vzniká pri nejasnom modeli absent/null/optional hodnoty. Type system alebo analyzer môže vynútiť explicitné spracovanie:

```text
value exists
value absent
value invalid
value not loaded
```

Suppression bez pochopenia iba presúva riziko do runtime.

## 11. Complexity metrics

Static tools môžu merať:

- cyclomatic complexity,
- cognitive complexity,
- nesting depth,
- function/file size,
- duplication,
- dependency cycles.

Metrika nie je automatický dôkaz nekvality. Používaj ju na identifikáciu review hotspotov a trendov, nie ako izolovaný cieľ.

## 12. Dead a unreachable code

Dead-code analysis môže odhaliť:

- nepoužívané symbols,
- unreachable branches,
- zastarané feature paths,
- nevyužité dependencies,
- konfiguráciu bez consumerov.

Dynamické loading, reflection a pluginy môžu vytvárať false positives. Suppression musí vysvetliť runtime väzbu.

## 13. Dependency a architecture rules

Static analysis môže vynucovať:

- zakázané dependency directions,
- layer boundaries,
- public API surface,
- package ownership,
- import cycles,
- deprecated modules,
- platform-specific restrictions.

Príklad:

```text
presentation → application → domain
infrastructure → application/domain

domain nesmie importovať infrastructure
```

## 14. Configuration analysis

Rovnaké princípy platia pre:

- YAML/JSON schemas,
- Terraform validation,
- Kubernetes manifests,
- Dockerfiles,
- shell scripts,
- CI pipeline definitions,
- policy code.

Syntax validity neznamená semantic alebo runtime correctness.

## 15. Baseline a legacy code

Pri zavedení nástroja do existujúceho codebase môže byť nálezov veľa. Možnosti:

- opraviť kritické problémy,
- vytvoriť dočasný baseline,
- blokovať iba nové violations,
- postupne znižovať debt,
- rozdeliť pravidlá podľa severity.

Baseline nesmie znamenať permanentné ignorovanie. Potrebuje ownera, metriku a plán redukcie.

## 16. Suppression

Suppression má byť:

- čo najužšia,
- lokálna,
- vysvetlená,
- reviewovaná,
- prípadne časovo obmedzená,
- prepojená na issue alebo risk acceptance.

Globálne vypnutie pravidla môže odstrániť hodnotný signal pre celý repository.

## 17. Editor, pre-commit a CI

Dobrý feedback chain:

```text
editor diagnostics
→ local formatter/linter/type checker
→ pre-commit voliteľne
→ CI autoritatívna kontrola
```

CI musí používať rovnaké versions a konfiguráciu ako lokálny workflow.

Pre-commit hook nie je bezpečnostná boundary, pretože ho používateľ môže obísť.

## 18. Incremental a affected analysis

Na veľkom codebase používaj:

- cache,
- incremental analysis,
- changed-file linting,
- dependency graph,
- affected-project selection,
- remote execution.

Rýchlosť nesmie viesť k tomu, že sa cross-file alebo whole-program analýza nikdy nespustí. Môže bežať v samostatnej pipeline.

## 19. Quality gate dizajn

Pravidlo môže blokovať merge, keď:

- je presné,
- reprodukovateľné,
- relevantné pre riziko,
- má jasnú remediation,
- tool je stabilný,
- výsledok nekolíše podľa environmentu.

Style preferencie bez automatického fixu nemajú mať rovnakú severity ako injection alebo type-safety chyba.

## 20. Reportovanie

Výstup má byť:

- priamo pri súbore a riadku,
- deduplikovaný,
- s rule ID,
- vysvetlením rizika,
- remediation príkladom,
- machine-readable formátom pre CI,
- trendovateľný.

Tisíce neakčných findings znižujú dôveru v kontrolu.

## 21. Typické omyly

### „Linter nenašiel chybu, kód funguje“

Static analysis nepokrýva všetky runtime a business vlastnosti.

### „Type checker nahrádza input validation“

Runtime dáta môžu byť neplatné bez ohľadu na annotations.

### „Všetky warnings ako errors“

Bez baseline a severity modelu môže táto politika zablokovať adopciu a vytvoriť masové suppression.

### „Viac pravidiel znamená vyššiu kvalitu“

Dôležitá je presnosť, actionability a pokrytie reálnych rizík.

### „Formatter a linter sú to isté“

Riešia rozdielne vrstvy.

### „Suppression vyriešil problém“

Odstránil signal, nie nutne príčinu.

## 22. Kontrolné otázky

1. Aký je rozdiel medzi compiler diagnostic, formatterom a linterom?
2. Čo type checker dokáže a čo nedokáže?
3. Aký je rozdiel medzi AST, CFG a call graphom?
4. Ako funguje taint analysis?
5. Prečo môže static analyzer produkovať false positives?
6. Ako bezpečne zaviesť nový analyzer do legacy codebase?
7. Aké vlastnosti má dobrý suppression?
8. Kedy má static finding blokovať merge?
9. Ako škálovať analýzu v monorepe?
10. Prečo editor alebo pre-commit kontrola nenahrádza CI gate?

## Glossary impact

Relevantné pojmy: static analysis, linting, formatter, type checking, gradual typing, AST, control-flow graph, call graph, taint analysis, source, sink, sanitizer, cyclomatic complexity, baseline, suppression a incremental analysis.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Security a infrastructure tests](security-and-infrastructure-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Code coverage a quality gates →](code-coverage-and-quality-gates.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
