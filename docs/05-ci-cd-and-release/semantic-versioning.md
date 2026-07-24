# Semantic Versioning

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Semantic Versioning (SemVer) je verzovací kontrakt, ktorý formátom `MAJOR.MINOR.PATCH` komunikuje zamýšľanú kompatibilitu novej verzie voči explicitne deklarovanému verejnému API.

```text
MAJOR.MINOR.PATCH
```

SemVer nie je algoritmus, ktorý kompatibilitu automaticky dokáže. Producer musí poznať svoj verejný kontrakt, posúdiť zmenu a priradiť správny increment. Consumer musí rozumieť, ktorú časť kontraktu používa, a svoju kompatibilitu overovať testami.

```text
explicitný public contract
+ zmena contractu
+ compatibility policy
→ version increment
```

Bez explicitného public API je SemVer iba trojica čísel bez spoľahlivého významu.

## 2. Základný význam

Pre stabilný public API od verzie `1.0.0` platí:

- **MAJOR —** zvyšuje sa pri backward-incompatible zmene public API.
- **MINOR —** zvyšuje sa pri backward-compatible pridaní capability; zahŕňa aj označenie existujúcej capability za deprecated.
- **PATCH —** zvyšuje sa pri backward-compatible oprave chyby.

Príklady:

```text
2.4.1 → 2.4.2   PATCH
2.4.2 → 2.5.0   MINOR
2.5.0 → 3.0.0   MAJOR
```

Pri zvýšení MINOR sa PATCH resetuje na nulu. Pri zvýšení MAJOR sa MINOR aj PATCH resetujú na nulu.

## 3. Public API je rozhodujúca boundary

Public API nie je iba exportovaná function alebo HTTP endpoint. Je to všetko, na čo sa consumer môže podľa deklarovaného kontraktu spoľahnúť.

Môže zahŕňať:

- function signatures a typy,
- HTTP/GraphQL endpoints, fields a status/error semantics,
- event schemas, ordering a delivery assumptions,
- CLI commands, flags, stdout/stderr format a exit codes,
- configuration schema, defaults a precedence,
- environment variables,
- file alebo serialization formats,
- package/module names,
- Terraform module inputs, outputs a resource behavior,
- Helm values a rendered-resource contract,
- container entrypoint, ports, signals a filesystem paths,
- plugin interfaces,
- documented performance alebo resource guarantees,
- operational behavior relevantný pre integráciu.

Interný detail sa stane de facto public contractom, ak je dokumentovaný alebo široko používaný a producer jeho použitie toleruje. Preto treba public boundary zámerne definovať, nie ju odhadovať až pri breaking change.

## 4. `1.0.0` ako deklarácia stability

Verzia `1.0.0` definuje public API, ktoré má byť od tohto bodu spravované podľa SemVer compatibility pravidiel.

To neznamená, že software je bez chýb alebo dokončený. Znamená to, že producer prijíma zodpovednosť za stabilný contract a breaking zmeny bude komunikovať MAJOR verziou a migration lifecycleom.

Dlhodobé zotrvanie na `0.x`, aby sa producer vyhol tejto zodpovednosti, neprenáša riziko preč. Iba ho presúva na consumerov bez jasného signálu.

## 5. Verzie `0.y.z`

Pri `0.y.z` sa public API považuje za nestabilný. SemVer povoľuje, aby sa čokoľvek zmenilo.

```text
0.8.4
```

To však neznamená náhodné alebo nezdokumentované breaking changes. Organizácia má deklarovať vlastnú policy, napríklad:

```text
0.MINOR.PATCH
MINOR môže obsahovať breaking change
PATCH zachováva compatibility v rámci MINOR série
```

Táto policy je nadstavba, nie univerzálne SemVer pravidlo. Consumer musí vedieť, či `0.8.4 → 0.9.0` vyžaduje migráciu.

## 6. PATCH verzia

PATCH increment označuje backward-compatible bug fix.

Príklady:

- oprava nesprávneho výpočtu podľa existujúcej špecifikácie,
- security fix bez zmeny public contractu,
- performance optimalizácia so zachovanou observable semantics,
- oprava memory/resource leak bez zmeny API,
- interný refactoring,
- oprava package metadata, ak nemení resolution contract.

Úmysel „iba opravujeme bug“ nestačí. Ak consumer legitímne závisel od dokumentovaného pôvodného behavioru, zmena môže byť breaking. Oprava implementácie proti špecifikácii je PATCH iba vtedy, keď špecifikácia bola skutočným contractom.

## 7. MINOR verzia

MINOR increment pridáva backward-compatible functionality alebo označuje existujúce API ako deprecated.

Príklady:

- nový optional parameter s kompatibilným defaultom,
- nový endpoint alebo command,
- nový output, ktorý tolerantný consumer môže ignorovať,
- nový optional configuration field,
- nový interface method iba v modeli, kde existing implementations nie sú rozbité,
- nový event type, ak consumers majú definovanú unknown-event policy.

„Pridávame, neodstraňujeme“ nie je automaticky kompatibilné. Pridanie enum hodnoty, JSON fieldu alebo virtual method môže rozbiť strict consumerov. Compatibility sa posudzuje podľa deklarovaného contractu a reálnych ecosystem assumptions.

## 8. MAJOR verzia

MAJOR increment signalizuje backward-incompatible zmenu public API.

Príklady:

- odstránenie endpointu alebo exportu,
- zmena významu existujúceho fieldu,
- nový povinný parameter,
- zmena default behavioru,
- zmena error alebo retry semantics,
- odstránenie CLI flagu,
- zmena output formátu,
- nekompatibilná event schema,
- zmena Terraform inputu bez migration compatibility,
- zmena authentication alebo authorization contractu,
- odstránenie podporovanej platformy, ak bola súčasťou public contractu.

MAJOR číslo iba oznamuje nekompatibilitu. Samo nevytvorí migration guide, compatibility window ani bezpečný rollout.

## 9. Verzia musí byť nemenná

Po publikovaní sa obsah verzie nesmie meniť. Oprava vydanej `2.4.1` musí dostať novú version, napríklad `2.4.2`; nesmie prepísať bytes pod `2.4.1`.

Immutability je nevyhnutná pre:

- dependency lockfiles,
- reprodukovateľné buildy,
- audit,
- incidentnú diagnostiku,
- rollback,
- signatures a provenance,
- cache correctness.

SemVer version je logical identity. Konkrétne bytes sa majú navyše viazať na artifact digest.

## 10. Lexikálny formát

Core version má tri nezáporné integer časti oddelené bodkou:

```text
MAJOR.MINOR.PATCH
```

Core časti nesmú obsahovať leading zero, okrem samotnej nuly:

```text
1.2.3   valid
0.9.0   valid
01.2.3  invalid
1.02.3  invalid
```

Pre-release metadata sa zapisujú po `-`, build metadata po `+`.

```text
1.4.0-rc.2+build.18422
```

## 11. Pre-release identifiers

Pre-release verzia má formát:

```text
1.4.0-alpha
1.4.0-alpha.1
1.4.0-beta.2
1.4.0-rc.1
```

Identifiers sú oddelené bodkami. Používajú ASCII alphanumeric znaky a hyphen. Numeric identifier nesmie mať leading zero.

Pre-release version má nižšiu precedence než zodpovedajúca final version:

```text
1.4.0-rc.1 < 1.4.0
```

Označenie `rc` komunikuje release phase, nie automatický quality alebo security dôkaz. Každý pre-release artifact musí byť immutable.

## 12. Build metadata

Build metadata sa zapisujú za `+`:

```text
1.4.0+build.18422.sha.8a71c9d
1.4.0-rc.1+linux.amd64
```

Build metadata:

- môžu identifikovať build, source alebo variant,
- nemenia SemVer precedence,
- nemajú sa používať ako jediný spôsob ordering releaseov,
- môžu mať ecosystem-specific obmedzenia.

Z pohľadu SemVer majú `1.4.0+build.1` a `1.4.0+build.2` rovnakú precedence. Konkrétne artifacts musí odlíšiť registry/package identity alebo digest.

## 13. Precedence algoritmus

Version precedence sa určuje nasledovne:

1. porovnaj MAJOR numericky;
2. ak je rovnaký, porovnaj MINOR numericky;
3. ak je rovnaký, porovnaj PATCH numericky;
4. final version má vyššiu precedence než pre-release s rovnakou core version;
5. pre-release identifiers porovnávaj zľava doprava;
6. dva numeric identifiers sa porovnávajú numericky;
7. numeric identifier má nižšiu precedence než non-numeric identifier;
8. dva non-numeric identifiers sa porovnávajú lexikálne podľa ASCII;
9. ak sú všetky spoločné identifiers rovnaké, dlhší zoznam má vyššiu precedence;
10. build metadata ignoruj.

Príklad rastúceho poradia:

```text
1.0.0-alpha
< 1.0.0-alpha.1
< 1.0.0-alpha.beta
< 1.0.0-beta
< 1.0.0-beta.2
< 1.0.0-beta.11
< 1.0.0-rc.1
< 1.0.0
```

## 14. Producer a consumer asymetria

Producer rozhoduje o version bump-e, ale consumer znáša dôsledky nesprávneho rozhodnutia.

Producer potrebuje:

- explicitný public API inventory,
- compatibility tests a diff tooling,
- review behavior changes,
- release notes a migration guidance,
- telemetry deprecated usage,
- immutable publication.

Consumer potrebuje:

- dependency ranges zodpovedajúce reálnej tolerancii,
- lockfile/resolved manifest,
- update automation,
- contract/integration tests,
- rollback alebo pinning možnosť,
- monitoring po update.

SemVer je komunikačný protokol medzi oboma stranami, nie jednostranná marketingová značka.

## 15. Compatibility dimensions

Kompatibilita nie je jedna boolean vlastnosť. Zmena môže byť kompatibilná v jednej dimenzii a breaking v inej.

- **Source compatibility —** existujúci source sa stále skompiluje.
- **Binary/ABI compatibility —** existujúci binary sa načíta a linkuje.
- **Schema compatibility —** serialized dáta alebo messages sa dajú čítať/zapisovať.
- **Behavior compatibility —** výsledok, side effects a error semantics zostávajú v contracte.
- **Operational compatibility —** deployment, signals, ports, health checks a resource assumptions zostávajú podporované.
- **Performance compatibility —** latency, memory alebo capacity ostávajú v deklarovaných hraniciach.
- **Security compatibility —** auth, crypto, trust a permission assumptions sa nemenia nečakane.
- **Data compatibility —** nová a stará verzia rozumejú spoločnému persistentnému stavu.

Version policy má pomenovať, ktoré dimenzie public API zahŕňa.

## 16. Syntaktická verzus behaviorálna kompatibilita

API môže byť syntakticky nezmenené a behaviorálne breaking.

```text
GET /items stále existuje a vracia HTTP 200,
ale default page size sa zmení zo 100 na 10.
```

Ďalšie behaviorálne breaky:

- zmena sort orderu,
- odlišné timeouty alebo retries,
- zmena rounding pravidla,
- nový rate limit,
- zmena consistency modelu,
- odlišná error classification,
- zmena default security posture.

Schema diff tool tieto zmeny nemusí odhaliť. Potrebné sú contract tests, behavior specs a consumer telemetry.

## 17. Rozširovanie enumov a unions

Pridanie enum hodnoty je backward-compatible iba vtedy, ak consumer contract prikazuje tolerovať neznáme hodnoty.

Strict pattern:

```text
switch status:
  ACTIVE
  INACTIVE
  else → crash
```

môže nová hodnota rozbiť. Tolerantný contract môže vyžadovať explicitný `UNKNOWN`, fallback alebo version negotiation.

To isté platí pre nové event types, union variants, object subtypes a protocol capabilities.

## 18. Version ranges

Consumer môže deklarovať rozsah, napríklad:

```text
>=1.4.0 <2.0.0
```

Syntaxy ako `^`, `~`, wildcards alebo intervaly sú package-manager specific. Ich význam sa môže výrazne líšiť, najmä pri `0.x`.

Range vyjadruje, ktoré budúce versions resolver smie vybrať. Neznamená, že ich consumer reálne otestoval.

Široký range:

- znižuje update friction,
- umožňuje automaticky prijímať fixes,
- zvyšuje priestor neotestovaných combinations.

Presný pin:

- zvyšuje reprodukovateľnosť,
- vyžaduje pravidelný update proces,
- môže odkladať security fixes.

## 19. Lockfile a resolved manifest

Version range je policy. Lockfile je konkrétne resolution rozhodnutie.

```text
declaration: ^1.4.0
resolved:    1.7.3
integrity:   sha256:...
```

Lockfile má zachytiť:

- presné direct a transitive versions,
- source/registry,
- integrity hash podľa ecosystemu,
- platform markers podľa potreby.

Reproducible build používa lockfile alebo ekvivalentný resolved manifest. Update automation zámerne mení lock a spúšťa tests.

## 20. Dependency update policy

Bez update procesu sú aj správne ranges alebo pins nebezpečné.

Policy môže definovať:

- automatické PATCH updates,
- grouped MINOR updates,
- manuálne MAJOR migrations,
- security override,
- update cadence,
- compatibility test matrix,
- rollback/pin behavior,
- deprecation alerts.

Automatický merge iba podľa version čísla predpokladá, že producer SemVer dodržiava. Dôveryhodnejší model kombinuje version signal s tests, provenance a security evidence.

## 21. Pre-release dependency ranges

Package managers často nezačlenia pre-release verziu do bežného stable range bez explicitného opt-inu. Presné pravidlá sú ecosystem-specific.

Consumer má explicitne rozhodnúť:

- či pre-release versions povoľuje,
- z ktorého channelu,
- pre ktoré environments,
- ako zabráni náhodnému promotion pre-release artifactu do produkcie,
- ako sa final version resolve-ne po vydaní.

## 22. Deprecation lifecycle

Bezpečný breaking-change proces:

```text
nová alternatíva
→ deprecation notice
→ telemetry consumerov
→ migration tooling a guide
→ compatibility window
→ removal v MAJOR release
→ monitoring po migrácii
```

Deprecation contract má obsahovať:

- čo je deprecated,
- dostupnú náhradu,
- prvú deprecated version,
- plánovanú removal version alebo deadline,
- migration instructions,
- ownera a support channel,
- telemetry alebo consumer inventory.

Deprecation bez termínu vytvára permanentný compatibility dlh. Removal bez telemetry riskuje skrytých consumerov.

## 23. Parallel major versions

Producer môže dočasne podporovať viac major línií:

```text
v1 — security fixes do dátumu X
v2 — aktívny stable release
v3 — pre-release/migration
```

Potrebná je explicitná policy:

- support a end-of-life termíny,
- ktoré fixes sa backportujú,
- security severity threshold,
- compatibility a test matrix,
- documentation channels,
- artifact retention,
- consumer migration ownership.

Viac major línií zvyšuje maintenance cost a patch divergence.

## 24. Backports

Fix môže byť implementovaný na aktuálnej mainline a backportovaný do podporovanej staršej série.

Príklad:

```text
3.4.0 — aktuálna séria
2.9.5 — backport security fixu
```

Každá séria má vlastný PATCH sequence a artifact identity. Rovnaký logical fix nemusí vytvoriť identické bytes ani identické implementation details.

Backport workflow potrebuje:

- supported branch/source of truth,
- cherry-pick alebo samostatnú implementáciu,
- tests pre danú dependency/runtime matrix,
- samostatné release notes,
- provenance a digest,
- forward-propagation kontrolu.

## 25. Monorepo: unified versioning

Pri unified versioning používa celý release set jednu version.

Výhody:

- jednoduchšia kompatibilná kombinácia,
- jeden release manifest a changelog,
- ľahšie koordinované cross-component zmeny.

Nevýhody:

- unchanged komponenty dostávajú novú version,
- breaking zmena jedného contractu môže zvýšiť MAJOR celého setu,
- consumers jednotlivých packageov môžu dostávať zbytočné updates.

Unified version má zmysel, keď komponenty tvoria silne koordinovaný produkt a sú testované ako release set.

## 26. Monorepo: independent versioning

Každý package alebo service má vlastnú version.

Vyžaduje:

- spoľahlivý dependency graph,
- affected-package detection,
- per-component public API inventory,
- version bump calculation,
- internal dependency-range update,
- per-component changelog,
- compatible release manifest pre coordinated deployments.

Independent versions nevylučujú coordinated release. Release manifest môže pinovať konkrétnu kombináciu component versions/digestov.

## 27. Services a contract versioning

Pri deployovanej service si consumer často nevyberá deployment artifact version. SemVer môže opisovať client SDK alebo API contract, ale rollout potrebuje ďalší model.

Rozlišuj:

- application artifact version,
- API/schema contract version,
- deployment revision,
- release/exposure cohort,
- database migration state.

Service môže deployovať `artifact 18422`, pričom stále podporuje API v1 aj v2. Naopak MAJOR artifact version nemusí znamenať verejnú API zmenu, ak ide o interný produktový release model.

## 28. HTTP/API versioning

MAJOR API zmena môže byť doručená cez:

- versioned URL alebo hostname,
- media type/content negotiation,
- header alebo protocol negotiation,
- nový endpoint a parallel support,
- nový SDK major.

Bezpečný migration model zachováva starú aj novú cestu počas compatibility windowu a meria consumer adoption. SemVer číslo samo traffic nepresmeruje a consumerov nezmigruje.

## 29. Event a schema versioning

Event-driven contract musí zohľadniť uložené messages, replay a súbeh producer/consumer versions.

Posudzuj:

- backward compatibility nového consumera so starými events,
- forward compatibility starého consumera s novými events,
- unknown fields/types,
- default values,
- ordering a idempotency,
- schema registry mode,
- retention a replay window.

MAJOR bump packageu nevyrieši event už uložený v queue alebo archive.

## 30. Databázové migrations

Database schema používa vlastnú monotónnu migration history a compatibility lifecycle.

```text
application version 3.0.0
≠ automaticky schema version 3.0.0
```

Deployment musí vedieť:

- ktoré migrations sú applied,
- či stará a nová application version fungujú so spoločným stavom,
- expand/backfill/contract fázu,
- rollback alebo roll-forward možnosti.

SemVer komunikuje application contract, nie bezpečnosť database rollbacku.

## 31. Infrastructure a modules

Terraform module, Helm chart alebo deployment template môže používať SemVer, ale public API zahŕňa aj runtime effects.

Breaking zmeny môžu byť:

- replacement resourceu,
- zmena default security policy,
- zmena naming, labels alebo outputs,
- zmena provider requirements,
- odstránenie supported platform version,
- zmena ownership alebo lifecycle behavioru.

Schema-valid input môže viesť k deštruktívnemu planu. Version bump má sprevádzať plan/migration guidance.

## 32. Automatické určovanie bumpu

Tooling môže navrhnúť version increment z:

- API/ABI diffu,
- schema compatibility kontroly,
- changelog fragments,
- conventional commits,
- pull-request labels,
- explicitného release manifestu.

Automatizácia je decision support, nie úplný oracle. Nevidí vždy behaviorálne, prevádzkové alebo security contract changes. Potrebuje review a explicitný override s dôvodom.

## 33. Changelog a release notes

Version number neobsahuje všetky informácie potrebné pre update.

Release notes majú uviesť:

- nové capabilities,
- bug a security fixes,
- breaking changes,
- deprecated a removed APIs,
- migration steps,
- configuration/default changes,
- compatibility requirements,
- known issues,
- supported platform changes,
- artifact/release-manifest identity.

## 34. Troubleshooting nesprávneho version signálu

Pri PATCH/MINOR release, ktorý rozbil consumera:

1. identifikuj presnú resolved version a digest;
2. porovnaj declared public contract so zmenou;
3. skontroluj behavior/default/error semantics;
4. over strict parsers, enums a unknown-field handling;
5. skontroluj transitive dependency changes;
6. porovnaj supported platform/runtime matrix;
7. over package-manager range a lockfile update;
8. pridaj consumer/contract regression test;
9. rozhodni o yank/revocation alebo novej opravnej version;
10. oprav release process a versioning policy.

## 35. Typické anti-patterny

### Každá interná zmena je PATCH

Observable behavior a consumer contract sa ignorujú.

### MAJOR bump ako náhrada migration plánu

Číslo signalizuje break, ale nerieši súbeh verzií, dáta ani consumer rollout.

### `0.x` ako permanentná výnimka

Producer sa vyhýba deklarácii stability a consumer nesie neobmedzené riziko.

### Rozšírenie enumu automaticky ako MINOR

Strict consumer môže zlyhať na novej hodnote.

### Version range bez lockfile a update evidence

Build sa mení bez source diffu a bez jasného testovaného resolutionu.

### Build metadata používané na ordering

SemVer precedence ich ignoruje.

### SemVer version bez immutable artifactu

Rovnaké číslo môže označovať rozdielne bytes.

### Service artifact version zamieňaná za API version

Deployment a public contract majú odlišné lifecycle.

### Breaking database change iba cez MAJOR číslo

Nevytvorí expand-contract ani bezpečný rollback.

## 36. Praktický rozhodovací rámec

1. Čo je deklarovaný public API?
2. Ktoré compatibility dimensions sú súčasťou contractu?
3. Je zmena observable pre existujúceho consumera?
4. Je nový behavior kompatibilný s dokumentovanými defaults a errors?
5. Sú nové fields, enums alebo event types tolerantne spracované?
6. Je zmena PATCH, MINOR alebo MAJOR podľa contractu, nie podľa veľkosti diffu?
7. Je version immutable a viazaná na digest?
8. Aké pre-release a build metadata sú potrebné?
9. Ako consumer ranges a lockfiles ovplyvnia adoption?
10. Existuje deprecation, telemetry a migration window?
11. Treba podporovať parallel major versions alebo backport?
12. Ako sa versioning rieši v monorepe?
13. Je contract version oddelená od deployment a schema identity?
14. Aké tests dokazujú compatibility?
15. Aký release note a rollback postup consumer dostane?

## 37. Kontrolný checklist

Pred vydaním SemVer release over:

- public API a supported platforms sú explicitné,
- core version a identifiers sú syntakticky validné,
- MAJOR/MINOR/PATCH reset pravidlá sú správne,
- publikovaná version je immutable,
- artifact digest a provenance sú zaznamenané,
- API/schema diff bol posúdený,
- behavior, defaults, errors a performance contract boli reviewované,
- enum/union rozšírenia sú kompatibilné,
- deprecations majú termín a migration guide,
- dependency ranges a lock update boli testované,
- pre-release channel sa nemôže náhodne dostať do stable release,
- monorepo/internal dependencies majú konzistentné versions,
- services/events/databáza majú vlastný compatibility plan,
- changelog uvádza breaking changes a known issues,
- backport alebo parallel-major support policy je jasná.

## 38. Kontrolné otázky

1. Čo SemVer komunikuje a čo nedokazuje?
2. Čo všetko môže tvoriť public API?
3. Aký význam má `1.0.0`?
4. Čo presne SemVer hovorí o `0.y.z`?
5. Kedy je bug fix MAJOR namiesto PATCH?
6. Prečo môže additive zmena rozbiť consumera?
7. Aké reset pravidlá platia pri MAJOR a MINOR incrementoch?
8. Ako funguje pre-release precedence?
9. Prečo build metadata nemenia precedence?
10. Aký je rozdiel medzi version range a lockfileom?
11. Aké compatibility dimensions poznáš?
12. Ako funguje deprecation lifecycle?
13. Prečo SemVer sám nevyrieši major API migráciu?
14. Aký je rozdiel medzi unified a independent versioningom?
15. Ako sa líši artifact, API, deployment a database version?
16. Ako fungujú parallel major lines a backports?
17. Kedy automatický version bump potrebuje ľudský override?

## Summary

Semantic Versioning je compatibility komunikačný kontrakt nad explicitným public API. `MAJOR.MINOR.PATCH`, pre-release identifiers a precedence majú presné pravidlá, ale správny bump závisí od source, binary, schema, behavior, operational, security a data compatibility. Producer musí publikovať immutable versions, deprecation a migration lifecycle; consumer musí používať rozumné ranges, lockfiles, update automation a contract tests. SemVer nenahrádza artifact digest, deployment identity, event/schema migration ani databázovú kompatibilitu.

## Glossary impact

Relevantné pojmy: Semantic Versioning, public API, MAJOR version, MINOR version, PATCH version, version immutability, pre-release identifier, build metadata, version precedence, version range, lockfile, source compatibility, binary compatibility, behavior compatibility, deprecation window, parallel major version, backport, unified versioning a independent versioning.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Artifact versioning](artifact-versioning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Release management →](release-management.md)
<!-- KNOWLEDGE-NAVIGATION:END -->