# Shift-left

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

Shift-left je rozhodovací princíp pre umiestnenie dôkazu. Pri každom failure mode hľadá najskorší bod delivery toku, v ktorom možno získať dostatočne spoľahlivý, diagnostický a akčný signál bez odstránenia boundary, na ktorej chyba reálne vzniká.

```text
riziko alebo chybný predpoklad
→ potrebný oracle
→ najskoršia vrstva s dostatočnou fidelity
→ rýchly lokálny feedback
→ autoritatívny CI dôkaz
→ neskoršie potvrdenie zostávajúcich boundaries
→ produkčné učenie
→ presun nového poznatku do skoršej kontroly
```

Shift-left preto neznamená „všetko testovať lokálne“ ani „presunúť zodpovednosť security a operations na vývojára“. Skoršia kontrola má hodnotu iba vtedy, keď zachová mechanizmus testovaného rizika a jej zelený výsledok sa nevydáva za silnejší dôkaz, než skutočne poskytuje.

## 1. Cieľ kapitoly

Nosný model kapitoly je evidence-placement lifecycle:

```text
potreba, incident alebo failure mode
→ explicitný contract a oracle
→ boundary mapa
→ kandidátne observation points
→ porovnanie fidelity, feedback času a ceny
→ najskorší spoľahlivý control
→ autoritatívny gate a evidence provenance
→ reziduálne riziká ponechané neskorším vrstvám
→ defect-escape feedback a úprava controlu
```

Cieľom nie je maximalizovať počet pre-commit hookov. Cieľom je skrátiť čas medzi vznikom chyby a použiteľným rozhodnutím bez vytvorenia false confidence.

## 2. Nosný scenár: Atlas Orders 3.9.2

Atlas pripravuje release 3.9.2. Zmena obsahuje:

- nový export objednávok pre veľkých tenantov;
- rozšírenie event schema o optional `exportProfile`;
- PostgreSQL index a backfill;
- nový worker retry policy;
- Helm hodnotu pre queue concurrency;
- nové audit a business-completion metrics.

Riziká sa objavujú na rôznych boundaries:

```text
požiadavka
→ môže byť nejasné, komu export patrí a dokedy má byť dostupný

source
→ tenant context sa môže stratiť v command alebo evente

interface
→ starší consumer nemusí tolerovať nové pole

PostgreSQL
→ index alebo backfill môže blokovať writes

rendered deployment
→ concurrency override môže preťažiť DB pool

production
→ reálny tenant skew a regionálna latency môžu zmeniť completion rate
```

Jedna skorá kontrola nemôže vierohodne pokryť celý chain. Shift-left určuje, ktoré riziko možno presunúť skôr a ktoré potrebuje neskorší runtime dôkaz.

## 3. Najskorší bod nie je automaticky najlepší bod

Užitočné rozhodnutie porovnáva päť vlastností:

- **failure boundary** — kde môže nesprávne správanie vzniknúť;
- **fidelity** — či kontrola zachová relevantné semantics;
- **feedback latency** — ako rýchlo sa výsledok vráti autorovi;
- **diagnostikovateľnosť** — či failure ukáže konkrétnu príčinu;
- **cost a authority** — koľko kontrola stojí a či jej výsledok chráni auditované rozhodnutie.

Pravidlo:

```text
vyber najskoršiu vrstvu,
ktorá zachová relevantnú failure boundary
s prijateľným false-negative rizikom
```

Syntax chybu môže spoľahlivo odhaliť editor alebo compiler. PostgreSQL lock behavior však nemožno presunúť do unit testu s in-memory repository bez straty predmetu dôkazu.

## 4. Evidence ladder pre Atlas zmenu

Atlas rozloží dôkaz takto:

| Riziko | Najskorší spoľahlivý dôkaz | Neskoršie potvrdenie |
|---|---|---|
| Tenant context chýba v commande | type/domain test | component abuse test |
| Event schema je breaking | schema diff a contract test | deployment compatibility matrix |
| Backfill nie je restartovateľný | migration state-machine test | sandbox run nad reprezentatívnymi dátami |
| Index blokuje writes | PostgreSQL integration/benchmark | controlled production rollout |
| Queue concurrency preťaží DB | rendered config + policy | component load a canary saturation signal |
| Audit event neobsahuje correlation ID | component telemetry assertion | production trace/audit validation |
| Export completion klesne pre veľkých tenantov | model a targeted dataset test | RUM/business cohort analysis |

Tabuľka nie je zoznam povinných nástrojov. Ukazuje, že každý failure mode má inú najnižšiu spoľahlivú boundary.

## 5. Shift-left začína pri contracte

Nejasná požiadavka nevytvára stabilný oracle. Atlas preto pred implementáciou definuje:

```text
Kto môže spustiť export?
→ iba používateľ s export permission v aktívnom tenant contexte

Čo je výsledok?
→ jeden export obsahujúci iba orders daného tenanta

Aký je deadline?
→ export sa dokončí do 5 minút pre deklarovaný dataset tier

Aké negatívne správanie je zakázané?
→ žiadne cross-tenant rows, duplicate object ani silent partial export

Aká kompatibilita je potrebná?
→ starší worker ignoruje optional exportProfile

Aký dôkaz rozhoduje?
→ domain, contract, PostgreSQL, component a produkčný cohort evidence
```

Takto vzniknú oracles ešte pred kódom. Test potom neoptimalizuje implementáciu podľa nejasného očakávania.

## 6. Design review ako tvorba následných controls

Design review je shift-left iba vtedy, keď identifikuje mechanizmus a vytvorí konkrétny následný dôkaz. Atlas review napríklad rozhodne:

```text
tenant identity je server-owned
→ command builder nesmie akceptovať tenant z request body
→ domain/component negative test

backfill musí byť resumable
→ checkpoint a idempotent batch contract
→ migration restart test

queue concurrency má DB connection budget
→ rendered config invariant
→ load/canary saturation guardrail
```

Zápis „security skontrolované“ alebo „database tím súhlasí“ nie je control. Chýba testovateľné rozhodnutie, owner a evidence path.

## 7. Developer feedback loop

Lokálna vrstva má poskytovať najrýchlejší diagnostický feedback pre kontroly, ktoré možno reprodukovať bez dôveryhodného centrálneho prostredia:

```text
formatter
→ parser/compiler
→ linter a type checker
→ focused unit tests
→ schema/contract diff
→ rendered configuration checks
→ targeted integration s ephemeral dependency
```

Lokálny task používa rovnakú verzovanú konfiguráciu a toolchain ako CI. Inak vznikajú dve odlišné definície správnosti.

Pre-commit hook je ergonomická optimalizácia. Nie je autoritatívny gate, pretože ho možno obísť, nemusí byť nainštalovaný a nezanecháva centrálnu evidence provenance.

## 8. Autoritatívna CI vrstva

CI opakuje kritické skoré kontroly v známom execution contexte a viaže výsledok na konkrétny commit alebo synthetic merge candidate.

```text
repository a dependency integrity
→ format, syntax a schema
→ static analysis a type checking
→ unit a targeted integration
→ contract compatibility
→ build immutable artifactu
→ artifact/SBOM/provenance controls
→ širší boundary evidence podľa rizika
```

CI musí rozlíšiť:

- **pass** — kontrola sa kompletne vykonala a oracle bol splnený;
- **failure/finding** — kontrola sa vykonala a našla porušenie;
- **incomplete** — chýba shard, report, dependency alebo vstup;
- **tool/infrastructure failure** — dôkaz nevznikol;
- **skipped by policy** — kontrola sa nespustila z explicitného auditovaného dôvodu.

Tool failure nesmie byť interpretovaný ako zelený výsledok.

## 9. Test selection je samostatný risk model

Shift-left nevyžaduje celý testovací corpus pri každom commite. Vybraný set však musí byť konzervatívny voči neznámym dependencies.

```text
changed files
+ dependency a artifact graph
+ contract ownership
+ generated-code edges
+ risk tags
+ historical execution evidence
→ affected control set
```

Fast lane sa dopĺňa periodickým širším behom a release evidence. Selection miss je defect controlu: ak relevantný test existoval, ale nebol vybraný, treba opraviť dependency model, nie iba pridať ďalší test.

## 10. Security, infrastructure a data changes

Shift-left je najsilnejší tam, kde deklaratívny model umožňuje skorý dôkaz:

```text
threat model
→ abuse cases
→ secure defaults
→ static/secret/dependency analysis
→ IaC render a policy
→ plan/change-set verification
→ sandbox apply
→ runtime enforcement test
```

Source policy nemôže potvrdiť effective permissions po identity inheritance. Terraform plan nemôže potvrdiť network reachability z reálneho source. Tieto blind spots zostávajú explicitne vpravo.

Pri databázovej zmene Atlas potrebuje:

- expand-contract kompatibilitu starej a novej aplikácie;
- reálny PostgreSQL engine a relevantnú major verziu;
- reprezentatívnu veľkosť a distribúciu dát;
- lock a statement timeout observation;
- restart, retry a partial-progress semantics;
- roll-forward alebo recovery plán.

Syntax-valid migration je iba prvý krok evidence ladderu.

## 11. Operability shift-left

Observability sa navrhuje pred incidentom. Atlas definuje:

- correlation identity pre request, export job, event a object;
- structured logs s redaction contractom;
- technical aj business completion metrics;
- trace boundaries pre API, DB, broker, worker a object storage;
- startup, readiness a liveness semantics;
- alert inputs a runbook ownership.

Component tests môžu overiť, že telemetry vzniká a obsahuje potrebné fields. Až produkcia však ukáže, či signál vedie k rýchlej diagnóze pri reálnom trafficu a cardinality.

## 12. Worked failure: migration bola posunutá príliš doľava

Atlas tím chcel zrýchliť feedback. Backfill testoval cez in-memory repository a malý SQLite dataset:

```text
migration function unit test green
→ SQLite fixture green
→ PR gate green
→ production PostgreSQL vytvoril index bez vhodného online postupu
→ dlhý lock zablokoval CreateOrder writes
```

### Root cause

Kontrola bola skorá a rýchla, ale odstránila PostgreSQL lock, planner, transaction a dataset boundaries. Tím zamieňal algorithm correctness za operational migration evidence.

### Náprava

- čistá batch/checkpoint logika zostáva v unit scope-e;
- migration integration používa reálny PostgreSQL;
- reprezentatívny dataset meria lock wait, runtime a disk growth;
- plan obsahuje abort a roll-forward criteria;
- canary sleduje DB waits, write latency a backlog;
- incident vytvorí trvalý migration template a policy.

Shift-left neznamená nahradiť reálnu boundary lacnejšou imitáciou. Znamená rozdeliť dôkaz a presunúť skôr iba tú časť, ktorú skoršia vrstva vie spoľahlivo reprezentovať.

## 13. Worked failure: lokálny pass nebol ten istý control

Vývojári lokálne spúšťali staršiu verziu contract generatora. CI používala novšiu pinovanú verziu:

```text
lokálny contract diff bez breaking change
→ pull request otvorený
→ CI regenerovala klienta inak
→ consumer compile failure
→ vývojár opakovane opravoval až v remote pipeline
```

### Root cause

Lokálny feedback a autoritatívny gate nemali rovnaký toolchain, config ani generated artifact semantics. Kontrola bola „vľavo“, ale neposkytovala preview CI rozhodnutia.

### Náprava

- toolchain je pinovaný v repository;
- local task aj CI volajú rovnaký wrapper;
- generated output má deterministic check;
- CI stále opakuje control v dôveryhodnom prostredí;
- local-to-CI mismatch rate je sledovaná metrika.

## 14. Golden paths a platform engineering

Shift-left škáluje cez paved road, nie cez rastúci manuálny checklist. Platforma môže poskytovať:

```text
repository template
→ versioned local task runner
→ reusable CI controls
→ ephemeral real dependencies
→ secure libraries a defaults
→ artifact provenance
→ observability bootstrap
→ remediation guidance
```

Golden path musí mať jasný contract, versioning, ownera a bezpečný escape hatch. Black-box template bez vysvetlenia iba presúva nepochopenie do centrálnej platformy.

## 15. Blocking, advisory a exception semantics

Skorý signal blokuje až vtedy, keď je presný, stabilný, reprodukovateľný a akčný. Nový heuristický analyzer môže začať advisory:

```text
observe baseline
→ tune rules a scope
→ merať false positives a stability
→ definovať remediation a ownera
→ pilot blocking na kritickom scope
→ rozšíriť alebo ponechať advisory
```

Exception nemení technický failure na pass. Obsahuje konkrétny control, scope, risk ownera, compensating evidence, remediation plán a expiry.

## 16. Uzavretá väzba so shift-right

Shift-left a shift-right tvoria jeden regulačný systém:

```text
skoré contracts a controls
→ immutable release candidate
→ kontrolovaná produkčná expozícia
→ reálne technical/functional/business evidence
→ nový alebo potvrdený failure mode
→ najnižší spoľahlivý regression control
→ bezpečný default alebo platform guardrail
```

Niektoré vlastnosti zostávajú prirodzene vpravo: skutočný traffic mix, identity federation, regionálna sieť, produkčné quotas, tenant skew a emergentné distribuované interakcie. Cieľom nie je odstrániť pravú stranu, ale znížiť počet opakovateľných prekvapení.

## 17. Metriky účinnosti

Účinnosť shift-left sa nemeria počtom nástrojov. Atlas sleduje:

- time to first useful feedback;
- local-to-CI mismatch rate;
- failure-stage distribution;
- selection miss rate;
- false-positive a suppression rate;
- defect escapes podľa failure class;
- broken-control repair time;
- developer wait time a gate queue;
- percento produkčných findings prevedených na skorší control.

Metrika má viesť k úprave evidence placementu. Rýchlejší gate bez nižšieho escape rizika môže iba zrýchliť false green.

## 18. Diagnostický postup

Pri neočakávanom neskorom failure:

1. Pomenuj presný failure mode a prvú boundary, kde sa prejavil.
2. Zisti, ktoré skoršie controls mali riziko zachytiť.
3. Over ich scope, toolchain, config, input provenance a selection.
4. Rozlíš chýbajúci test od kontroly s nedostatočnou fidelity.
5. Zisti, či skorý signal bol incomplete, skipped, waived alebo nesprávne interpretovaný.
6. Navrhni najnižší nový control, ktorý zachová mechanizmus failure.
7. Ponechaj vyšší test, ak stále poskytuje unikátnu boundary evidence.
8. Pridaj ownera, remediation a regression provenance.
9. Sleduj, či sa failure class presunula do skoršej vrstvy bez rastu false positives.

## 19. Referenčné pravidlá

- Posúvaj dôkaz, nie iba názov testu.
- Najskorší control musí zachovať relevantnú failure boundary.
- Požiadavka a design majú vytvoriť oracles a následné controls.
- Lokálny feedback a CI používajú rovnaký verzovaný toolchain.
- Pre-commit hook nie je autoritatívna enforcement boundary.
- CI odlišuje pass, finding, incomplete, tool failure a policy skip.
- Test selection je risk model a potrebuje širší validačný beh.
- IaC source/plan evidence nenahrádza effective runtime verification.
- DB semantics testuj s reálnym engine-om, keď sú predmetom rizika.
- Skorý advisory signal potrebuje ownera a maturity lifecycle.
- Exception nemení failure na zelený výsledok.
- Produkčný finding sa má podľa možnosti zmeniť na skorší regression control.

## 20. Časté omyly

### „Shift-left znamená všetko spustiť pred commitom“

Nie. Niektoré boundaries potrebujú artifact, reálnu dependency, deployment alebo produkčný traffic.

### „Rýchlejší test je automaticky lepší“

Rýchlosť bez fidelity môže vytvoriť lacný false green.

### „Staging test môžeme nahradiť mockom“

Iba ak mock modeluje relevantný failure. Provider, DB, network a identity semantics často potrebujú reálnejšiu vrstvu.

### „Lokálne green znamená CI green“

Iba pri rovnakom toolchaine, konfigurácii a complete control set-e; CI navyše zostáva autoritatívna.

### „Viac blocking gates znižuje riziko“

Hlučné a pomalé gates vytvárajú bypassy, batch growth a stratu dôvery.

### „Shift-left odstráni potrebu produkčnej validácie“

Reálny workload a emergentné správanie nemožno úplne simulovať.

## 21. Zhrnutie

Dôveryhodný shift-left model pre Atlas je:

```text
failure mode
→ explicitný contract a oracle
→ boundary mapa
→ najskorší spoľahlivý control
→ local preview
→ autoritatívny CI evidence
→ artifact/deployment/runtime confirmation podľa blind spots
→ defect escape alebo production learning
→ skorší regression control a platform guardrail
```

Shift-left optimalizuje čas učenia, nie počet skorých nástrojov. Správna kontrola je umiestnená tak skoro, ako to dovoľuje fidelity testovaného mechanizmu — a nie skôr.

## 22. Kontrolné otázky

1. Prečo shift-left znamená presun dôkazu, nie všetkých testov?
2. Ako failure boundary určuje najskorší spoľahlivý scope?
3. Ktoré vlastnosti porovnáva evidence-placement decision?
4. Ako Atlas rozdelí export a migration evidence medzi vrstvy?
5. Prečo design review potrebuje následný test alebo policy artifact?
6. Aký je rozdiel medzi local preview a autoritatívnym CI gate-om?
7. Ako test selection vytvára false-negative riziko?
8. Prečo SQLite test nepreukázal PostgreSQL migration safety?
9. Ako odlišuje CI pass, incomplete a tool failure?
10. Kedy má skorý signal zostať advisory?
11. Ako platform golden path znižuje cognitive load bez vytvorenia black boxu?
12. Ako produkčný incident vstupuje späť do shift-left systému?

## Glossary impact

Relevantné pojmy: shift-left, evidence placement, developer feedback loop, local-to-CI parity, authoritative gate, test selection, selection miss, golden path, paved road, secure default, control maturity, advisory control, defect escape a feedback latency.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Flaky tests a test data](flaky-tests-and-test-data.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Shift-right →](shift-right.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
