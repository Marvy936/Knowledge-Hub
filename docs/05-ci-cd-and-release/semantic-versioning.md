# Semantic Versioning

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Semantic Versioning je compatibility komunikačný contract. Číslo `MAJOR.MINOR.PATCH` nevzniká z veľkosti diffu ani z úmyslu autora. Vzniká porovnaním observable zmeny s explicitne deklarovaným public API a s tým, čo existujúci consumer smie očakávať.

```text
public contract
→ candidate change
→ observable delta
→ compatibility dimensions
→ consumer evidence
→ PATCH, MINOR alebo MAJOR decision
→ immutable publication
→ adoption a deprecation lifecycle
```

## 1. Cieľ kapitoly

Nosný model kapitoly je semantic-version decision lifecycle:

```text
inventarizuj public API
→ identifikuj zmenený behavior
→ urč affected consumerov
→ otestuj backward compatibility
→ klasifikuj bump
→ zostav migration alebo deprecation plan
→ publikuj immutable version a digest
→ sleduj consumer adoption a regressions
```

SemVer je signál. Nedokazuje, že producer správne pochopil contract, že consumer je tolerantný ani že release je prevádzkovo bezpečný.

## 2. Nosný scenár: čo patrí do Orders 3.10.1, 3.11.0 a 4.0.0

Atlas Orders 3.10.0 publikuje HTTP contract:

```yaml
POST /orders
request:
  customerId: string
  items: array
  idempotencyKey: string
response:
  orderId: string
  state: ACCEPTED | REJECTED
behavior:
  rovnaký idempotencyKey a rovnaký request vracia rovnaký order
  neznáme response fields musí consumer ignorovať
  neznáma state hodnota nie je povolená
```

Tím pripraví tri zmeny:

### Zmena A — oprava duplicate race

Implementácia občas vytvorila dve objednávky pri súbežnom retry, hoci contract garantoval jednu. Fix obnovuje už deklarované správanie bez zmeny requestu, response alebo error semantics.

```text
3.10.0 → 3.10.1
PATCH
```

### Zmena B — nový optional `riskDecision` objekt

Response dostane nové optional pole:

```yaml
riskDecision:
  score: integer
  modelVersion: string
```

Contract už vyžaduje ignorovať neznáme fields. Existujúci consumer preto naďalej spracuje `orderId` a `state`; nový consumer môže použiť novú capability.

```text
3.10.1 → 3.11.0
MINOR
```

### Zmena C — nová hodnota `PENDING_REVIEW` v existujúcom `state`

Starý contract označuje enum ako closed. Existujúci mobilný client má exhaustívny switch bez fallbacku. Nová hodnota by ho mohla ukončiť alebo zahodiť order state.

```text
3.11.0 → 4.0.0
MAJOR
```

Alternatívou je najprv v 3.x pridať nový optional field alebo versioned endpoint, migrovať consumerov, zmerať adopciu a až potom zmeniť closed `state` contract v 4.0.0.

Tento scenár ukazuje jadro SemVer: additive syntax nie je automaticky MINOR a bug fix nie je automaticky PATCH. Rozhoduje public contract a observable kompatibilita.

## 3. Public API je boundary, nie iba function signature

Public API Orders zahŕňa viac než OpenAPI schema:

- endpointy, methods a fields;
- required, optional a default hodnoty;
- enum a union openness;
- status, error a retry semantics;
- idempotency a side effects;
- authentication a authorization behavior;
- rate limits a timeout contract;
- event schemas a ordering;
- configuration, environment variables a precedence;
- CLI flags, stdout/stderr a exit codes;
- container ports, signals a filesystem paths;
- supported client, platform a protocol versions;
- deklarované latency alebo capacity boundaries, ak sú integračným záväzkom.

Interný detail sa môže stať de facto public contractom, ak ho producer dokumentuje, dlhodobo podporuje alebo vie, že na ňom závisia consumery. Preto sa contract inventarizuje pred release decisionom, nie až po incidente.

## 4. Zmena sa klasifikuje podľa consumer observation

Version bump workflow pre každú zmenu používa rovnaké otázky:

```text
čo consumer dnes smie poslať alebo očakávať?
→ čo sa po zmene zmení v syntaxi, behavior-e alebo prevádzke?
→ môže existujúci consumer pokračovať bez zmeny?
→ aký dôkaz to podporuje?
```

Veľký interný refactoring môže byť PATCH, ak zachová public contract. Jednoriadková zmena default timeoutu môže byť MAJOR, ak mení observable retry alebo failure behavior, na ktorom consumer oprávnene závisí.

## 5. Compatibility má viac dimenzií

Atlas review rozlišuje:

- **Source compatibility —** existujúci source sa stále skompiluje.
- **Binary/ABI compatibility —** existujúci binary sa načíta a linkuje.
- **Schema compatibility —** existujúce správy alebo dáta sa dajú čítať a zapisovať.
- **Behavior compatibility —** výsledky, defaults, errors a side effects zostávajú v contracte.
- **Operational compatibility —** ports, signals, probes, config a resource assumptions zostávajú podporované.
- **Security compatibility —** auth, permissions, crypto a trust assumptions sa nemenia nečakane.
- **Data compatibility —** stará a nová verzia rozumejú spoločnému persistentnému stavu.
- **Performance compatibility —** deklarované latency alebo throughput hranice zostávajú splnené.

Zmena B je schema-additive a behaviorálne kompatibilná, pretože contract prikazuje unknown-field tolerance. Zmena C je schema-additive, ale behaviorálne breaking pre closed enum consumerov.

## 6. PATCH znamená opravu v rámci existujúceho contractu

Pre stabilnú verziu od `1.0.0` PATCH increment komunikuje backward-compatible bug fix.

Atlas duplicate race je PATCH, pretože:

```text
contract pred zmenou: jeden logical order na idempotency key
chybná implementácia: občas dva orders
nová implementácia: znovu spĺňa pôvodný contract
```

PATCH môže zahŕňať:

- opravu výpočtu podľa existujúcej špecifikácie;
- interný refactoring;
- memory leak fix;
- security fix bez zmeny public contractu;
- performance optimalizáciu v deklarovaných hraniciach.

Ak bola chybná hodnota alebo behavior dlhodobo dokumentovaná ako contract, „oprava“ môže byť breaking. Producer nemôže spätne vyhlásiť consumer dependency za nelegitímnu iba preto, že implementácia bola pôvodne neúmyselná.

## 7. MINOR pridáva capability bez poškodenia existujúcich consumerov

MINOR increment pridáva backward-compatible functionality alebo označuje existujúce API za deprecated.

Orders `riskDecision` je MINOR iba preto, že:

- pole je optional;
- starí consumery ho podľa contractu ignorujú;
- existujúce fields nemenia význam;
- auth, errors a side effects zostávajú rovnaké;
- nový field nepridáva povinný call sequence.

Additive change môže byť breaking, ak pridá:

- enum hodnotu do closed enumu;
- required interface method;
- nový JSON field consumerovi, ktorý odmieta unknown fields a producer to toleroval;
- event type bez unknown-event policy;
- nový default-enabled behavior;
- nový blocking authorization requirement;
- field, ktorý mení signature alebo canonicalization.

„Nič sme neodstránili“ nie je compatibility dôkaz.

## 8. MAJOR signalizuje backward-incompatible contract

MAJOR increment je potrebný, keď existujúci podporovaný consumer musí zmeniť implementáciu alebo assumptions, aby pokračoval.

Pre Atlas by to zahŕňalo:

- odstránenie endpointu alebo fieldu;
- nový povinný request parameter;
- zmenu významu `state`;
- novú closed enum hodnotu;
- zmenu idempotency semantics;
- zmenu default auth alebo permission modelu;
- nekompatibilný event/schema format;
- odstránenie podporovaného client alebo platform version;
- zmenu error classification, na ktorej závisí retry policy.

MAJOR číslo iba oznamuje break. Nevytvára parallel support, migration guide, telemetry ani bezpečný cutover.

## 9. `1.0.0` je prijatie zodpovednosti za stabilitu

Version `1.0.0` definuje stabilný public API podľa SemVer policy. Neznamená bezchybný alebo feature-complete software. Znamená, že producer:

- public contract pozná a dokumentuje;
- breaking zmenu komunikuje MAJOR bumpom;
- published versions nemení;
- poskytuje migration a deprecation lifecycle primeraný produktu.

Dlhodobé zotrvanie na `0.x` neodstraňuje consumer risk. Iba ho môže robiť menej čitateľným.

## 10. `0.y.z` potrebuje lokálnu policy

SemVer považuje `0.y.z` public API za nestabilný. Organizácia môže pridať vlastný contract:

```text
0.MINOR.PATCH
MINOR môže byť breaking
PATCH zachováva compatibility v rámci jednej MINOR série
```

Consumer musí túto policy poznať. Nemá automaticky predpokladať, že všetky `0.x` updates sú bezpečné alebo že `0.8.4 → 0.8.5` je breaking.

## 11. Syntaktický formát a precedence sú referenčná vrstva

Core version má tri nezáporné integer časti bez leading zero:

```text
3.11.0
4.0.0
```

Pre-release identifiers nasledujú za `-`:

```text
3.11.0-alpha.1
3.11.0-beta.2
3.11.0-rc.1
```

Build metadata nasledujú za `+`:

```text
3.11.0-rc.1+build.18422.sha.8a71c9d
```

Pre-release má nižšiu precedence než final release s rovnakou core version:

```text
3.11.0-rc.2 < 3.11.0
```

Build metadata precedence nemenia:

```text
3.11.0+build.1
3.11.0+build.2
```

majú z pohľadu SemVer rovnakú precedence. Konkrétne bytes musí rozlíšiť artifact namespace a digest.

Po MINOR bump-e sa PATCH resetuje na nulu. Po MAJOR bump-e sa resetujú MINOR aj PATCH.

## 12. Pre-release označuje candidate phase, nie kvalitu

Atlas môže publikovať:

```text
3.11.0-rc.1 → manifest M1
3.11.0-rc.2 → manifest M2
3.11.0      → alias na schválený M2
```

Každý candidate je immutable. `rc.2` sa nesmie prepísať novými bytes.

Označenie `rc` nepreukazuje test coverage, bezpečnosť ani readiness. Tie dokazujú evidence viazané na manifest M2.

## 13. Producer decision potrebuje compatibility evidence

Atlas release review pre zmeny A, B a C zbiera:

- API/schema diff;
- behavior contract tests;
- old-client proti new-server test;
- new-client proti old-server test podľa rollout modelu;
- event replay a unknown-field tests;
- configuration/default diff;
- auth a permission diff;
- supported platform matrix;
- consumer inventory a telemetry;
- database shared-state compatibility;
- release notes a migration impact.

Tool môže navrhnúť bump zo schema diffu alebo changelog fragmentu. Nevidí však vždy zmenu ordering, retries, defaults, rate limitu alebo side effects. Automatizácia je decision support, nie úplný oracle.

## 14. Consumer test je dôležitejší než producer úmysel

Producer Zmenu C považoval za „iba nový status“. Consumer test však ukázal:

```text
new server vráti PENDING_REVIEW
→ old Android client exhaustive switch
→ unhandled state exception
→ order detail screen sa neotvorí
```

Tento dôkaz klasifikuje zmenu ako breaking pre podporovaného consumera bez ohľadu na malý diff.

Consumer-driven contract tests, telemetry používaných fields a representative old-version fixtures pomáhajú odhaliť de facto contract, ktorý samotná producer schema neukazuje.

## 15. Tolerantný reader contract musí byť explicitný

Additive evolution funguje iba pri dohodnutých pravidlách:

```text
unknown JSON fields → ignore
unknown enum values → explicit UNKNOWN/fallback alebo version negotiation
missing optional field → stable default
unknown event type → dead-letter/fallback podľa contractu, nie crash
```

Tolerantnosť nie je univerzálne „ignoruj všetko“. Security-critical field alebo unsupported command môže vyžadovať fail-closed behavior. Contract musí určiť, ktoré rozšírenia sú bezpečné a ktoré menia protocol capability.

## 16. Version range je policy, lockfile je konkrétne rozhodnutie

Orders SDK consumer môže deklarovať:

```text
policy range: >=3.10.0 <4.0.0
resolved lock: 3.11.2
artifact integrity: sha256:...
```

Range hovorí resolveru, ktoré budúce versions smie vybrať. Nehovorí, ktoré consumer reálne otestoval.

Lockfile alebo resolved manifest zachová:

- presnú direct a transitive version;
- registry/source;
- integrity identity;
- platform markers;
- resolution graph.

Reproducible build používa konkrétny resolution. Update automation zámerne zmení lock, spustí tests a vytvorí reviewovateľný diff.

## 17. Pins a ranges majú opačné riziká

Široký kompatibilný range:

- znižuje update friction;
- prijíma fixes rýchlejšie;
- zväčšuje priestor neotestovaných kombinácií;
- dôveruje producer SemVer disciplíne.

Presný pin:

- zvyšuje reprodukovateľnosť;
- obmedzuje náhodnú zmenu bez source diffu;
- vyžaduje pravidelný update proces;
- môže odkladať security fixes.

Dôveryhodný consumer kombinuje deklarovaný range, lockfile, automatizované update PRs, contract tests a rollback/pinning možnosť.

## 18. Deprecation vytvára compatibility window

Atlas nemá odstrániť old `state` contract okamžite v 4.0.0 bez prípravy:

```text
3.11.0 pridá novú alternatívu
→ 3.x označí starý contract za deprecated
→ telemetry zmeria consumerov
→ SDK a migration tooling podporia nový model
→ support window umožní upgrade
→ 4.0.0 odstráni starý contract
→ post-migration monitoring potvrdí adoption
```

Deprecation record obsahuje:

- presný deprecated contract;
- replacement;
- prvú deprecated version;
- removal version alebo deadline;
- migration guide;
- ownera a support channel;
- usage telemetry.

Deprecation bez termínu vytvára permanentný compatibility dlh. Removal bez telemetry vytvára skrytý consumer incident.

## 19. Parallel major versions majú explicitný support cost

Atlas môže dočasne prevádzkovať:

```text
v3 API — aktívny stable a security fixes
v4 API — nový contract a migrujúci consumers
```

Policy určuje:

- support a EOL termíny;
- ktoré fixes sa backportujú;
- compatibility a test matrix;
- routing alebo negotiation;
- artifact retention;
- dokumentáciu a consumer migration ownership.

Viac major línií znižuje big-bang risk, ale zvyšuje maintenance, observability a patch-divergence náklady.

## 20. Backport vytvára samostatnú release identity

Duplicate race fix môže ísť do mainline 4.x aj podporovanej 3.x line:

```text
4.1.0 obsahuje fix v current architecture
3.10.2 obsahuje backport pre v3 contract
```

Ide o dva source a artifact subjects. Každý potrebuje vlastné tests, provenance, digest a release notes. Forward-propagation kontrola zabraňuje, aby production hotfix zostal iba v starej branchi.

## 21. Service artifact version nie je automaticky API version

Orders môže nasadiť artifact build `18422` a stále poskytovať API v3 aj v4. Rozlišuj:

```text
application artifact version
API alebo event contract version
deployment revision
release/exposure cohort
database migration state
```

SemVer je vhodný pre deklarovaný public contract. Interné service deploye môžu používať monotónne release IDs, pokiaľ compatibility contracty zostávajú samostatne explicitné.

## 22. Databáza a events majú vlastný compatibility lifecycle

Application version `4.0.0` automaticky neznamená schema version `4.0.0`.

Database transition potrebuje:

```text
expand
→ old/new compatible code
→ backfill a reconciliation
→ consumer migration
→ contract
```

Event contract musí zohľadniť stored messages, replay, old/new producers a consumers, unknown fields, ordering a retention window.

MAJOR bump oznamuje application break. Neodstraňuje staré messages ani nevytvára bezpečný database rollback.

## 23. Worked failure: „MINOR“ enum addition rozbila mobilných consumerov

Atlas vydal `3.12.0` s `PENDING_REVIEW`, pretože schema diff označil zmenu za additive:

```text
producer schema validná
→ release classified MINOR
→ server rollout 100 %
→ staré Android clients dostali novú hodnotu
→ exhaustive switch vyhodil exception
→ order tracking journey zlyhal
```

### Root cause

Public contract nebol inventarizovaný ako closed enum a release gate nemal old-client/new-server compatibility test. Bump automation hodnotila syntaktický diff, nie behavior.

### Náprava

- incident release sa yankne alebo roll-forwardne podľa exposure a compatibility;
- server dočasne nevracia novú hodnotu starým client capability cohorts;
- old-client fixtures sa stanú required contract evidence;
- enum openness sa explicitne dokumentuje;
- nový state model sa rolloutne cez v4 contract alebo tolerantnú v3 alternatívu;
- version decision record zachová dôvod, evidence a consumer impact.

## 24. Worked failure: PATCH zmenil retry semantics

Orders `3.10.2` mal „iba zvýšiť stabilitu“, no zmenil server timeout z 30 na 5 sekúnd a po timeout-e dokončil request na pozadí. SDK pri timeout-e retrylo bez idempotency key:

```text
kratší timeout
→ consumer retry
→ prvý request sa neskôr dokončil
→ druhý request vytvoril ďalší order
```

### Root cause

Tím posudzoval internú implementáciu, nie observable timeout a side-effect contract. Release note ani consumer tests zmenu nezachytili.

### Náprava

- timeout/error/idempotency semantics sa pridajú do public API inventory;
- change sa klasifikuje ako breaking alebo sa implementácia upraví tak, aby zachovala contract;
- SDK vynúti idempotency key;
- old/new behavior contract test sa stane release gate;
- incidentné side effects sa reconciliujú.

## 25. Diagnostický postup pri nesprávnom version signále

Keď PATCH alebo MINOR rozbije consumera:

1. identifikuj presnú resolved version, artifact digest a release manifest;
2. načítaj public contract platný pre predchádzajúcu version;
3. porovnaj syntax, defaults, errors, timing, side effects a security behavior;
4. urč affected compatibility dimension a consumer cohort;
5. over range, lockfile a pre-release resolution rules;
6. spusti old-consumer/new-producer a event/data compatibility fixtures;
7. skontroluj de facto používanie cez telemetry a support evidence;
8. rozhodni o abort-e, yank-u, revocation, compatibility shim-e alebo novej opravnej version;
9. oprav bump policy, contract inventory a regression evidence;
10. zachovaj migration a communication record pre affected consumerov.

## 26. Referenčné pravidlá

- SemVer sa aplikuje na explicitný public API.
- PATCH obnovuje alebo opravuje behavior v rámci existujúceho contractu.
- MINOR pridáva capability kompatibilnú s existujúcimi consumer assumptions.
- MAJOR signalizuje backward-incompatible zmenu.
- Additive schema diff nemusí byť kompatibilný.
- Behavior, defaults, errors, security a operational assumptions sú súčasť compatibility.
- `1.0.0` deklaruje stabilný contract; `0.x` potrebuje explicitnú lokálnu policy.
- Pre-release označuje candidate ordering, nie quality verdict.
- Build metadata nemenia SemVer precedence.
- Published version je immutable a viazaná na artifact digest.
- Range je selection policy; lockfile je konkrétny resolution.
- Deprecation, telemetry a parallel support pripravujú bezpečný MAJOR transition.
- API, artifact, deployment, event a database versions sú rozdielne identity.

## 27. Časté omyly

### „Malý diff je PATCH“

Veľkosť implementácie nehovorí nič o observable compatibility.

### „Pridanie fieldu alebo enum hodnoty je vždy MINOR“

Závisí od unknown-field a unknown-value contractu existujúcich consumerov.

### „MAJOR bump vyrieši migráciu“

Iba oznamuje break. Consumer inventory, parallel support, data transition a rollout zostávajú samostatná práca.

### „SemVer garantuje, že update je bezpečný“

Je to producer signal, ktorý consumer overuje vlastnými tests a runtime evidence.

### „Version range znamená, že všetky versions v ňom sú otestované“

Range povoľuje resolution. Lock a CI evidence hovoria, čo bolo skutočne použité a overené.

### „Service version a API version sú to isté“

Jeden deployment môže podporovať viac contract versions a jedna contract version môže prežiť mnoho artifacts.

## 28. Zhrnutie

Atlas semantic-version decision model je:

```text
explicitný public API inventory
→ candidate behavior delta
→ syntax + behavior + operational + data compatibility
→ old/new consumer evidence
→ PATCH, MINOR alebo MAJOR
→ immutable version viazaná na release manifest
→ deprecation, parallel support a adoption telemetry
```

Duplicate-race fix patrí do `3.10.1`, optional tolerantné `riskDecision` do `3.11.0` a closed-enum zmena do `4.0.0` alebo do riadenej compatibility migrácie. Nasledujúca kapitola zoberie schválený `3.11.0` manifest a prevedie ho cez release state machine od candidate assembly po používateľskú expozíciu, validation a support.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Artifact versioning](artifact-versioning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Release management →](release-management.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
