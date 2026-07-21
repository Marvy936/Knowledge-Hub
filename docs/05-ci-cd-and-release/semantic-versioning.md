# Semantic Versioning

Semantic Versioning, skrátene SemVer, je verzovací kontrakt, ktorý pomocou formátu `MAJOR.MINOR.PATCH` komunikuje význam zmien voči deklarovanému verejnému API alebo compatibility boundary.

SemVer nie je automatický dôkaz kompatibility. Je to dohoda medzi producerom a consumermi, ktorá funguje iba vtedy, keď je verejný kontrakt explicitný, testovaný a disciplinovane spravovaný.

## 1. Základný formát

```text
MAJOR.MINOR.PATCH
```

Príklad:

```text
3.7.2
```

Interpretácia:

- `MAJOR` — nekompatibilná zmena verejného kontraktu,
- `MINOR` — backward-compatible nová funkcionalita,
- `PATCH` — backward-compatible oprava.

## 2. Čo je public API

Public API nemusí byť iba HTTP endpoint alebo library function.

Môže zahŕňať:

- programové interfaces,
- CLI flags a exit codes,
- configuration schema,
- environment variables,
- file formats,
- event schemas,
- database views,
- Terraform module inputs/outputs,
- Helm values,
- container entrypoint a filesystem contract,
- operational behavior,
- documented error semantics.

Pred použitím SemVer musí byť jasné, čo sa považuje za compatibility boundary.

## 3. PATCH verzia

PATCH increment je určený pre backward-compatible opravy:

```text
2.4.1 → 2.4.2
```

Príklady:

- oprava nesprávneho výpočtu,
- security fix bez zmeny verejného contractu,
- performance zlepšenie so zachovanou semantics,
- oprava dokumentácie package-u,
- interný refactoring bez observable zmeny.

Aj oprava môže byť breaking, ak consumer závisel od pôvodného správania. Rozhoduje deklarovaný kontrakt, nie úmysel autora.

## 4. MINOR verzia

MINOR increment pridáva backward-compatible capability:

```text
2.4.2 → 2.5.0
```

Príklady:

- nový optional API field,
- nový endpoint,
- nový backward-compatible CLI command,
- nový optional configuration parameter,
- rozšírenie enumu iba vtedy, ak consumer contract povoľuje neznáme hodnoty.

Pridanie poľa môže byť breaking pre strict consumerov. Compatibility musí byť overená reálnymi contract tests, nie iba teoretickým pravidlom.

## 5. MAJOR verzia

MAJOR increment signalizuje vedomú nekompatibilnú zmenu:

```text
2.5.0 → 3.0.0
```

Príklady:

- odstránenie endpointu,
- zmena významu existujúceho poľa,
- povinný nový parameter,
- zmena default behavior,
- odstránenie CLI flagu,
- nekompatibilná event schema,
- premenovanie Terraform inputu bez migration mechanizmu.

MAJOR version nerieši migráciu automaticky. Potrebné sú deprecation, dokumentácia, tooling a transition window.

## 6. Verzia `0.y.z`

Verzie pred `1.0.0` sa často používajú pre nestabilné API:

```text
0.8.4
```

To neznamená, že breaking changes môžu byť náhodné. Consumeri stále potrebujú explicitnú policy.

Praktický model:

```text
0.MINOR.PATCH
```

kde MINOR môže obsahovať breaking change, ale release notes ho musia jasne označiť.

Pre interné platformové komponenty môže dlhodobé `0.x` maskovať chýbajúci ownership compatibility kontraktu.

## 7. Pre-release identifiers

Formát:

```text
1.4.0-alpha.1
1.4.0-beta.2
1.4.0-rc.1
```

Pre-release verzia má nižšiu precedence než final release:

```text
1.4.0-rc.1 < 1.4.0
```

Identifiers sa porovnávajú po častiach. Numeric identifiers majú špecifické ordering pravidlá.

Pre-release označenie komunikuje readiness, nie security alebo kvalitu bez ďalšej evidence.

## 8. Build metadata

Build metadata sa zapisujú za `+`:

```text
1.4.0+build.18422.sha.8a71c9d
```

Build metadata nemenia version precedence.

To znamená, že:

```text
1.4.0+build.1
1.4.0+build.2
```

majú z pohľadu SemVer rovnakú precedence. Package repository môže mať vlastné dodatočné pravidlá.

## 9. Version precedence

SemVer definuje ordering pre:

- major,
- minor,
- patch,
- pre-release identifiers.

Build metadata sa pri precedence ignorujú.

Príklad rastúceho poradia:

```text
1.0.0-alpha
1.0.0-alpha.1
1.0.0-beta
1.0.0-rc.1
1.0.0
1.0.1
1.1.0
2.0.0
```

## 10. Version ranges

Consumer môže deklarovať rozsah:

```text
>=1.4.0 <2.0.0
```

Package manager syntaxy sa líšia:

```text
^1.4.0
~1.4.0
1.x
```

Význam `^` pri `0.x` môže byť odlišný od očakávania. Range syntax musí byť interpretovaná podľa konkrétneho ecosystemu.

Široký range zvyšuje flexibilitu, ale aj riziko neotestovanej kombinácie. Presný pin zvyšuje reprodukovateľnosť, ale potrebuje dependency-update proces.

## 11. Dependency resolution

SemVer pomáha resolveru vybrať kompatibilnú verziu, ale nevie overiť:

- skutočnú backward compatibility,
- runtime environment,
- transitive dependency konflikty,
- security stav,
- behavior pri konkrétnej konfigurácii.

Pre reprodukovateľnosť používaj lockfile alebo presný resolved manifest.

## 12. API compatibility a behavior compatibility

Binary alebo schema compatibility nestačí.

Breaking zmena môže byť:

- syntaktická,
- typová,
- behaviorálna,
- výkonnostná,
- prevádzková,
- bezpečnostná.

Príklad behaviorálneho breaku:

```text
API stále vracia HTTP 200,
ale default pagination limit sa zmenil z 100 na 10.
```

## 13. Deprecation lifecycle

Bezpečný breaking-change proces:

```text
nová alternatíva
→ deprecation warning
→ telemetry používania
→ migration guide
→ compatibility window
→ removal v MAJOR release
```

Deprecation bez termínu a ownera vytvára trvalý compatibility dlh.

## 14. SemVer v monorepe

Možnosti:

### Unified version

Celý repository používa jednu verziu.

Výhody:

- jednoduchý release manifest,
- koordinované cross-component changes.

Nevýhody:

- verzia sa mení aj komponentom bez zmeny,
- major bump jedného contractu ovplyvní celý produkt.

### Independent versions

Každý package alebo service má vlastnú verziu.

Vyžaduje:

- dependency graph,
- affected-project detection,
- per-component changelog,
- koordináciu compatibility.

## 15. Services a SemVer

Pri deployovaných services consumer často nevyberá package version. SemVer môže stále opisovať API alebo event contract, ale nestačí ako rollout mechanizmus.

Potrebné sú:

- endpoint alebo schema versioning,
- backward-compatible rollout,
- consumer inventory,
- contract tests,
- deprecation telemetry,
- migration policy.

Service deployment version a API contract version môžu byť odlišné.

## 16. Databázové schema versions

Databázová migrácia nemusí nasledovať SemVer release aplikácie.

Bezpečnejší model zachováva:

- monotónne migration IDs,
- applied migration history,
- compatibility s old/new application versions,
- expand-contract lifecycle.

`3.0.0` samo nehovorí, či je rollback databázy bezpečný.

## 17. Automatické určovanie verzie

Version bump môže byť odvodený z:

- explicitného release manifestu,
- conventional commits,
- labels,
- changelog fragments,
- API diff tooling.

Automatizácia musí mať override a review mechanizmus. Commit message nevie spoľahlivo identifikovať všetky behaviorálne breaking changes.

## 18. Changelog a release notes

Version number nie je náhrada za release notes.

Dobrý changelog uvádza:

- nové capabilities,
- opravy,
- breaking changes,
- deprecations,
- security implications,
- migration kroky,
- known issues,
- compatibility requirements.

## 19. Typické anti-patterny

### Každá interná zmena je PATCH

Ignoruje observable behavior a consumer contract.

### MAJOR bump bez migration plánu

Číslo iba pomenovalo problém.

### Verzia sa vypočíta z branch názvu

Nevytvára stabilný release contract.

### `latest compatible` bez lockfile

Build sa mení bez source zmeny.

### Dlhodobé `0.x`, aby nič nebolo breaking

Consumer riziko nezmizlo.

### SemVer pre mutable artifact

Rovnaká verzia nesmie meniť obsah.

## 20. Troubleshooting

### PATCH release rozbil consumerov

Over:

- nedokumentované behavior dependencies,
- strict schema parsing,
- enum expansion,
- default zmeny,
- transitive dependencies,
- rozdiel medzi testovaným a reálnym contractom.

### Resolver vybral neočakávanú verziu

Skontroluj range syntax, pre-release pravidlá, lockfile a registry metadata.

### Dve build metadata verzie sa nedajú zoradiť

SemVer build metadata nemenia precedence. Potrebuješ repository-specific identity alebo artifact digest.

### Major release sa nedá bezpečne rolloutnúť

Chýba compatibility window. Použi dual-read/write, versioned endpoint, adapter alebo staged consumer migration.

## 21. Kontrolné otázky

1. Čo presne komunikuje `MAJOR.MINOR.PATCH`?
2. Čo všetko môže tvoriť public API?
3. Prečo môže byť pridanie optional fieldu breaking?
4. Aký význam majú pre-release identifiers?
5. Ovplyvňuje build metadata version precedence?
6. Aký je rozdiel medzi version range a lockfile?
7. Prečo SemVer negarantuje behavior compatibility?
8. Ako má fungovať deprecation lifecycle?
9. Ako sa líši unified a independent versioning v monorepe?
10. Prečo service deployment version nemusí byť API version?

## Glossary impact

Relevantné pojmy: Semantic Versioning, MAJOR version, MINOR version, PATCH version, pre-release identifier, build metadata, version precedence, version range, public API, deprecation window, compatibility contract a changelog.
