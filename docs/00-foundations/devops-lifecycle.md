# DevOps Lifecycle

DevOps lifecycle opisuje opakujúci sa tok od zámeru po overený runtime outcome. Názvy fáz ako Plan, Code, Build, Test, Release, Deploy, Operate a Monitor sú orientačné observation points; nie sú to samostatné oddelenia ani povinný lineárny workflow. Jedna zmena sa môže medzi nimi vracať, zastaviť na gate-e alebo byť po produkčnom pozorovaní úplne preformulovaná.

Dôležitejšie než názvy fáz je sledovať identitu a stav tej istej zmeny:

```text
change intent
→ candidate source tree
→ build inputs a artifact
→ verification evidence
→ release manifest
→ environment mutation
→ loaded runtime generation
→ traffic alebo feature exposure
→ business result
```

Ak sa identita medzi krokmi stratí, lifecycle vytvára false-green verdicty. Testy môžu patriť commitu A, artifact commitu B a produkčný tag môže ukazovať na ďalší digest. Continuous lifecycle preto potrebuje traceability, immutable alebo presne versionované subjects, explicitné failure semantics a feedback, ktorý sa vracia k ownerovi schopnému zmeniť systém.

## 1. DevOps lifecycle ako uzavretá regulačná slučka

DevOps lifecycle je nepretržitý tok zmeny od formulovania zámeru cez source, artifact, release a runtime až po produkčný feedback a učenie. Jeho cieľom nie je iba dostať kód do produkcie, ale skrátiť čas medzi rozhodnutím a dôveryhodným dôkazom, či zmena priniesla očakávaný výsledok.

Základný model obsahuje tri súčasné toky:

```text
flow of work
change intent → source revision → artifact → release → runtime

flow of feedback
lokálna kontrola ← CI evidence ← rollout telemetry ← user outcome

flow of learning
incident alebo výsledok → zmena testu, návrhu, platformy alebo priority
```

Flow of work posúva zmenu k používateľovi. Flow of feedback vracia informáciu o technickom a používateľskom výsledku. Flow of learning mení samotný delivery systém, aby rovnaká chyba alebo čakanie nevznikali opakovane. Ak tretí tok chýba, organizácia síce zbiera incidenty a metriky, ale jej spôsob práce zostáva rovnaký.

## 2. Štyri identity jednej zmeny

Jedna zmena počas lifecycle-u mení formu. Aby zostala auditovateľná, musia sa zachovať väzby medzi štyrmi identitami.

```text
change intent
    ↓ implementuje sa ako
source revision
    ↓ build transformuje na
artifact identity
    ↓ release a deployment sprístupnia ako
runtime release identity
```

**Change intent** vysvetľuje, prečo zmena vznikla, aký outcome má dosiahnuť a podľa čoho sa bude hodnotiť. **Source revision** je konkrétny verzovaný stav kódu, konfigurácie, infraštruktúry a testov. **Artifact identity** označuje nemenný výstup buildu, napríklad image digest alebo package version. **Runtime release identity** spája artifact s použitou konfiguráciou, prostredím, cohortom a časom nasadenia.

Pri incidente nestačí vedieť, že „beží verzia 2.4“. Tím musí vedieť dohľadať, ktorý change intent ju vytvoril, z ktorého revisionu vznikol artifact, aké evidence ho schválili a v akom runtime scope-e bol vystavený trafficu.

## 3. Priebežný scenár: nový parameter objednávkového API

Objednávkové API má dostať nový voliteľný parameter `delivery_window`. Starší klienti ho neposielajú a nesmú prestať fungovať. Nový parameter zároveň ovplyvní downstream fulfillment service, databázový model a používateľské potvrdenie objednávky.

Tento scenár bude sprevádzať celý lifecycle. Ukazuje, že zmena nie je iba riadok v API handleri:

```text
produktový zámer
→ backward-compatible contract
→ source revision s kódom, migráciou, testmi a telemetry
→ immutable image
→ release candidate s evidence
→ canary runtime
→ produkčné rozhodnutie
→ learning späť do backlogu a platformy
```

## 4. Plan: zmena začína overiteľným zámerom

Plan znižuje neistotu o probléme, používateľovi a požadovanom výsledku. Slabý plan vytvorí iba ticket „pridať parameter“, takže implementácia môže byť technicky správna, ale bez definovanej compatibility, rollout stratégie alebo signálu úspechu.

Pre `delivery_window` musí plan určiť:

- **Change intent — používateľ si môže zvoliť preferované časové okno**: táto veta vysvetľuje business dôvod, nie iba technickú úpravu API.
- **Compatibility contract — parameter je voliteľný a staršie requesty zostávajú platné**: určuje správanie producerov, consumerov aj databázovej migrácie.
- **Success signal — adoption, úspešné objednávky a fulfillment errors**: definuje, aké produkčné evidence rozhodnú o pokračovaní rollout-u.
- **Failure hypothesis — nový field môže rozbiť starého consumera alebo zvýšiť latency**: pomenúva riziká, ktoré musia pokryť tests a telemetry.
- **Exposure plan — najprv interní používatelia a malý percentuálny cohort**: obmedzuje blast radius pri chybe, ktorú pre-production prostredie neodhalilo.

Výstupom planningu nie je úplný design každej funkcie. Je ním dostatočný contract, aby ďalšie kroky vedeli, čo majú vytvoriť a aký dôkaz potrebujú.

## 5. Code: zámer sa mení na verzovaný change set

Code fáza vytvára source revision, ktorý obsahuje všetko potrebné na bezpečnú zmenu správania. V scenári nejde iba o application kód. Revision zahŕňa API schema, backward-compatible database migration, fulfillment mapping, testy, telemetry fields a deployment configuration.

Malý change set skracuje review a znižuje počet súčasných hypotéz. Ak sa nový parameter spojí s nesúvisiacim refactoringom a upgrade-om frameworku, zlyhanie počas canary má viac možných príčin a rollback môže odstrániť aj zdravé zmeny.

Code review má preto sledovať celý contract:

```text
change intent
→ implementation diff
→ compatibility assumptions
→ failure behavior
→ test evidence plan
→ operability a rollout readiness
```

Reviewer nekontroluje iba syntax. Overuje, či source revision naozaj reprezentuje pôvodný zámer a či obsahuje mechanizmy potrebné na jeho neskoršie overenie.

## 6. Build: source revision sa mení na artifact

Build je deterministická transformačná hranica. Z konkrétneho revisionu a deklarovaných dependencies vytvorí artifact, ktorý možno jednoznačne identifikovať a neskôr promovať.

```text
source revision + locked dependencies + build definition
                         ↓
                immutable artifact
                         ↓
              digest + provenance
```

Pre objednávkové API vznikne container image s digestom. Provenance zaznamená revision, build workflow, base image a ďalšie relevantné vstupy. Build môže súčasne vytvoriť SBOM alebo podpis, ale samotný úspech buildu ešte nehovorí, že API contract funguje.

Kritická hranica je **build once, promote the same artifact**. Staging a production majú používať rovnaké bytes. Ak sa image pre produkciu znovu zostaví, staging evidence sa vzťahuje na iný artifact a medzi buildmi sa môže zmeniť base image alebo transitívna dependency.

## 7. Test: evidence musí zodpovedať pomenovanému riziku

Testovanie znižuje neistotu o správnosti a compatibility, ale každý test vidí iba určitú boundary. Pre `delivery_window` nestačí unit test parsera. Hlavné riziká ležia medzi producerom, API, databázou a fulfillment consumerom.

Evidence chain môže vyzerať takto:

- **Unit test — lokálna validačná logika**: overí povolený formát a default správanie bez externých dependencies.
- **Contract test — starý a nový client contract**: dokáže, že request bez nového fieldu zostáva platný a response schema sa nezmenila nekompatibilne.
- **Migration test — expand krok databázy**: overí, že nová schema vznikne bez požiadavky na okamžité nasadenie novej application verzie.
- **Integration test — API a fulfillment boundary**: preverí serializáciu, event alebo downstream request so starým aj novým variantom.
- **Failure test — neplatné okno a nedostupný fulfillment**: ukáže, či API vracia správnu chybu a či retry nevytvára duplicitnú objednávku.
- **Security evidence — autorizácia a input handling**: overí, že nový field nemení access contract ani nevytvára injection boundary.

Zelená pipeline znamená iba to, že definované kontroly prešli. Ak test suite neobsahuje hlavný compatibility risk, zelený výsledok je slabý dôkaz, nie dôkaz bezpečnej zmeny.

## 8. Release: rozhodnutie nad konkrétnym artifactom

Release je rozhodnutie, že konkrétny artifact môže postúpiť do určeného scope-u. Release nie je synonymom buildu ani deploymentu.

Release record pre scenár musí spájať:

```text
artifact digest
+ test a security evidence
+ known limitations
+ supported configuration schema
+ rollout policy
+ rollback alebo roll-forward authority
```

Ak approval odkazuje iba na branch alebo mutable tag, jeho predmet sa môže zmeniť. Schválenie musí byť viazané na artifact identity a evidence, ktoré boli vytvorené pre tento artifact.

Manuálny gate môže byť správny pri vysokom riziku, ale musí prinášať rozhodnutie, ktoré automation nevie vykonať. Ak človek iba znovu kontroluje, že zelené jobs sú zelené, gate pridáva wait time bez novej risk evidence.

## 9. Deploy: runtime state sa mení kontrolovanou operáciou

Deployment aplikuje artifact a konfiguráciu do cieľového prostredia. V objednávkovom scenári musí rešpektovať poradie kompatibilných zmien:

```text
1. expand databázovú schema
2. nasadiť code, ktorý vie starý aj nový model
3. zapnúť telemetry a interný feature scope
4. až neskôr začať používať nový field vo väčšom rozsahu
```

Toto poradie znižuje riziko, že stará application verzia narazí na nekompatibilnú schema alebo nový consumer začne produkovať dáta, ktoré starý backend nevie spracovať.

Deployment job má overiť, že resources vznikli, Pods alebo procesy sú ready a minimálny smoke flow funguje. Nemôže však potvrdiť používateľský outcome ani compatibility všetkých clients; na to slúži rollout a produkčný feedback.

## 10. Rollout: deployment a exposure nie sú to isté

Rollout riadi, koľko reálneho trafficu alebo používateľov nová runtime release obsluhuje. Canary znižuje blast radius iba vtedy, keď je cohort reprezentatívny a telemetry rozlišuje baseline a canary.

Pre `delivery_window` môže exposure postupovať takto:

```text
interní používatelia
→ 1 % nových objednávok
→ 10 %
→ 50 %
→ plné sprístupnenie
```

Každý krok potrebuje abort conditions, napríklad rast fulfillment errors, zhoršenie p95 latency alebo duplicitné objednávky. Bez thresholdov je canary iba pomalší deployment a rozhodnutie sa zmení na subjektívne sledovanie dashboardu.

Feature flag môže oddeliť code deployment od business exposure. Neodstraňuje však potrebu kompatibility, cleanup plánu a vlastníka, ktorý flag po ukončení experimentu odstráni.

## 11. Operate: zmena vstupuje do dlhodobého runtime contractu

Po rollout-e sa zmena stáva súčasťou služby. Operations rieši capacity, dependencies, certificate a secret lifecycle, backup, incident response, cost aj postupné zastarávanie.

Nový field môže zvýšiť počet fulfillment calculations alebo vytvoriť nerovnomerný workload počas obľúbených časových okien. To je prevádzkový dôsledok pôvodne produktovej funkcie. Service team preto potrebuje sledovať queue depth, processing latency, rejection rate a downstream capacity, nie iba HTTP availability API.

Ownership sa deploymentom nekončí. Tím, ktorý zmenu navrhol, musí zostať zapojený do runtime výsledku a mať prístup k telemetry, runbooku a recovery mechanizmom.

## 12. Monitor a validate: technický health nie je user outcome

Produkčná validácia má odpovedať na dve odlišné otázky:

1. **Je runtime technicky zdravý?** Sleduje errors, latency, saturation, availability a dependency failures.
2. **Prináša zmena očakávaný výsledok?** Sleduje adoption, dokončené objednávky, zrušenia, nesplnené okná a používateľský feedback.

```text
healthy Pods + nízky HTTP error rate
≠
úspešné doručenie v zvolenom časovom okne
```

Release metadata musí byť prítomná v logs, metrics a traces, aby bolo možné porovnať novú runtime release s baseline. Bez tejto väzby tím vidí celkovú zmenu metriky, ale nevie ju priradiť konkrétnemu artifactu alebo cohortu.

## 13. Feedback sa musí vrátiť k správnemu rozhodnutiu

Feedback loop má hodnotu iba vtedy, keď jeho výsledok môže zmeniť ďalší krok. Jednotlivé observation points poskytujú odlišnú informáciu:

- lokálny linter vracia chybu autorovi ešte pred commitom;
- CI contract test zastaví promotion konkrétneho revisionu;
- canary telemetry zastaví alebo obmedzí exposure konkrétneho release-u;
- incident ukáže slabinu runtime a recovery modelu;
- user outcome môže vyvrátiť samotný product predpoklad.

Ak adoption nového fieldu rastie, ale úspešnosť doručenia sa nezlepšuje, ďalším krokom nemusí byť technická optimalizácia. Learning môže zmeniť product model alebo viesť k odstráneniu capability.

## 14. Learning mení systém, nie iba jeden ticket

Predstav si, že canary odhalí duplicitné objednávky po timeout-e fulfillment service. Okamžitá oprava môže pridať idempotency key. Skutočný learning však musí preskúmať aj širší systém:

```text
incident evidence
→ nový regression test
→ API retry contract
→ shared platform guidance pre idempotentné operácie
→ aktualizovaný review checklist
→ telemetry pre duplicate detection
```

Takto sa lokálny incident premieňa na opakovateľnú capability. Ak sa uzavrie iba hotfix ticket, rovnaký failure pattern môže vzniknúť v ďalšej službe.

## 15. Gates a feedback loops plnia odlišnú úlohu

Gate je decision point, ktorý na základe evidence povolí, obmedzí alebo zastaví postup zmeny. Feedback loop je cesta, ktorou sa evidence vráti k actorovi alebo automation schopnej upraviť ďalšie rozhodnutie.

```text
contract test zlyhá
→ gate nepovolí release
→ report ukáže konkrétnu nekompatibilnú schema
→ autor upraví source alebo contract
→ nový revision vytvorí nové evidence
```

Gate bez vysvetliteľného feedbacku iba blokuje. Feedback bez decision boundary môže zostať nepoužitý. Zdravý lifecycle potrebuje oboje.

## 16. Lead time vzniká najmä medzi aktívnymi krokmi

End-to-end lead time nie je súčet duration pipeline jobs. Zahŕňa active processing, waiting, rework a opakované cykly.

```text
lead time = active work + waiting + rework
```

Objednávková zmena môže mať osemminútový build, ale čakať dva dni na review, týždeň na test environment a ďalšie tri dni na release window. Zrýchlenie buildu o dve minúty vtedy nemení hlavný systémový výsledok.

Pri audite treba merať, kde change intent, revision, artifact alebo approval čakajú bez progresu. Každá fronta má ownera, kapacitu a policy; bez ich pomenovania zostane „pomalý delivery“ neurčitým symptómom.

## 17. Fázy nie sú organizačné silá ani povinné pipeline stages

Plan, Code, Build, Test, Release, Deploy, Operate a Monitor sú responsibilities a evidence boundaries. Nemusia ich vlastniť samostatné oddelenia a nemusia byť implementované ako osem sekvenčných jobs.

Tests, threat modeling, observability a deployment design vznikajú súbežne s kódom. Cross-functional ownership neznamená, že každý človek ovláda každú technológiu. Znamená, že hranica špecializácie nie je hranicou zodpovednosti za service outcome.

Chybný handoff model vyzerá takto:

```text
Product vytvorí ticket
→ Development odovzdá kód
→ QA odovzdá approval
→ DevOps odovzdá deployment
→ Operations zdedí incident
```

V takomto modeli sa feedback vracia pomaly cez tickety a každý tím optimalizuje vlastnú frontu.

## 18. Diagnostika lifecycle-u cez stratenú identitu alebo dôkaz

Pri probléme nehľadaj automaticky najpomalší job. Najprv zisti, kde sa prerušila väzba medzi change intentom, revisionom, artifactom, runtime release-om a feedbackom.

### Pipeline je zelená, ale produkcia zlyháva

Over, či test evidence pokrýva failure class z incidentu, či bol do produkcie promovaný rovnaký artifact a či deployment validation merala iba resource health namiesto user flowu.

### Nie je jasné, čo je nasadené

Skontroluj mutable tags, environment-specific rebuild, chýbajúcu configuration identity a absenciu release metadata v runtime telemetry.

### Canary nevie rozhodnúť

Hľadaj chýbajúcu baseline, nerozlíšený cohort, malý sample, nevhodné thresholdy alebo business signal, ktorý nebol instrumentovaný spolu s feature.

### Rollback nefunguje

Over database a event compatibility, migration direction, configuration schema a external side effects. Návrat starého image nemusí obnoviť predchádzajúci data state.

### Lead time je dlhý, hoci pipeline je rýchla

Rozdeľ waiting na review, environment, approval, release window a coordinated dependency. Optimalizácia compute nepomôže, ak bottleneck leží v organizačnom interface.

### Incidenty sa opakujú

Over, či post-incident actions vytvorili regression test, guardrail, platform capability alebo architecture zmenu. Dokument bez ownera a termínu nie je uzavretý learning loop.

## 19. Praktický audit jednej zmeny

Vyber jednu nedávnu production zmenu a rekonštruuj ju bez preskakovania vrstiev:

1. Aký bol change intent a success metric?
2. Ktorý source revision ho implementoval?
3. Ktorý artifact digest z revisionu vznikol?
4. Aké evidence boli viazané na tento artifact?
5. Kto a na základe čoho vytvoril release decision?
6. Aká configuration a secrets identity bola použitá pri deploymente?
7. Ktorý runtime scope dostal novú verziu ako prvý?
8. Aké abort conditions riadili rollout?
9. Ktoré technické a business signály potvrdili výsledok?
10. Čo sa na základe výsledku zmenilo v backlogu, testoch alebo platforme?

Ak niektorú väzbu nemožno dohľadať, lifecycle má traceability alebo ownership medzeru aj vtedy, keď deployment technicky prebehol.

## 20. Časté omyly

### DevOps lifecycle je názov CI/CD pipeline

Pipeline automatizuje časť transformačného a deployment toku. Lifecycle zahŕňa aj change intent, production operation, user outcome a učenie, ktoré môže zmeniť pôvodný plán.

### Monitorovanie je posledný krok

Telemetry uzatvára slučku iba vtedy, keď ovplyvní rollout, backlog, testy alebo architecture. Dashboard bez decision contractu je pasívny report.

### Zelený deployment znamená úspešnú zmenu

Deployment potvrdzuje vykonanie runtime mutation. Úspech zmeny vyžaduje production validation a používateľský outcome.

### Viac gates automaticky zvyšuje bezpečnosť

Gate znižuje risk iba vtedy, keď používa relevantné evidence a poskytuje rýchly, vysvetliteľný feedback. Redundantné approvals predlžujú lead time bez nového dôkazu.

### Rollback je vždy návrat predchádzajúceho image

Data migrations, external side effects a protocol changes môžu byť nevratné. Lifecycle musí navrhovať backward compatibility, compensation alebo roll-forward skôr než vznikne incident.

## 21. Kontrolné otázky

1. Čím sa DevOps lifecycle líši od všeobecného SDLC?
2. Aké štyri identity spájajú change intent so stavom v produkcii?
3. Ako sa líšia flow of work, flow of feedback a flow of learning?
4. Prečo build success nepreukazuje runtime correctness?
5. Prečo sa má rovnaký artifact promovať bez rebuildu?
6. Aký je rozdiel medzi release, deploymentom a rolloutom?
7. Ktoré evidence by si požadoval pre backward-compatible API zmenu?
8. Prečo canary potrebuje baseline, cohort identity a abort conditions?
9. Ako sa technický health líši od business outcome-u?
10. Prečo gate bez remediation feedbacku podporuje obchádzanie procesu?
11. Kde typicky vzniká väčšina lead time-u?
12. Prečo návrat starého artifactu nemusí byť funkčný rollback?
13. Ako sa incident zmení na organizačné learning namiesto jedného hotfixu?
14. Ako by si dohľadal konkrétnu production verziu až k pôvodnému change intentu?

## 22. Zhrnutie

DevOps lifecycle opisuje pohyb konkrétnej zmeny cez delivery systém. Change intent sa mení na source revision, revision na immutable artifact a artifact spolu s configuration na identifikovateľnú runtime release. Flow of feedback vracia technické a používateľské evidence a flow of learning mení testy, platformu, architecture alebo priority.

Zdravý lifecycle preto nekončí zelenou pipeline ani deploymentom. Zachováva traceability, promuje rovnaký artifact, kontroluje exposure, odlišuje technický health od user outcome-u a premieňa produkčné zistenia na trvalú zmenu systému.

## Glossary impact

Relevantné pojmy: DevOps lifecycle, flow of work, flow of feedback, flow of learning, change intent, source revision, artifact identity, provenance, runtime release identity, release, deployment, rollout, evidence chain, gate, feedback loop, lead time, wait time, progressive delivery a artifact promotion.

## Primárne zdroje

- [Google Cloud — DevOps capabilities](https://cloud.google.com/architecture/devops)
- [DORA — Research program](https://dora.dev/)
- [NIST Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DevOps](devops.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CALMS framework →](calms.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
