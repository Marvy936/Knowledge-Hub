# Continuous Integration

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Continuous Integration (CI) je pracovný a technický model, v ktorom tímy často integrujú malé zmeny do spoločnej hlavnej línie a nad každým kandidátnym integračným stavom automaticky získavajú dôveryhodný dôkaz o zostaviteľnosti, kompatibilite a kvalite.

CI nie je iba server, ktorý spúšťa testy. Je to uzavretý feedback lifecycle:

```text
malá zmena
→ kandidátny integračný stav
→ reprodukovateľný build
→ automatizované kontroly
→ immutable artifact a evidence
→ merge alebo oprava
→ zdravá hlavná línia
```

Základnou jednotkou CI nie je branch ani pipeline run, ale **integračné rozhodnutie**: môžeme túto konkrétnu zmenu bezpečne pridať k aktuálnemu spoločnému stavu?

## 2. Problém, ktorý CI rieši

Bez častej integrácie sa riziko hromadí mimo spoločného feedback systému. Dlhodobé branches sa vzďaľujú od mainline, nekompatibility zostávajú skryté a ich riešenie sa presúva do veľkej „integration phase“ pred releaseom.

Mechanizmus integračného dlhu:

```text
zmeny vznikajú oddelene
→ každá je testovaná proti starému základu
→ assumptions sa rozchádzajú
→ merge vytvorí nový, netestovaný stav
→ failure má veľký počet možných príčin
```

CI znižuje tento dlh cez:

- **malý batch size —** menší diff má menší počet assumptions a jednoduchší rollback;
- **krátky čas do integrácie —** zmena sa porovnáva s aktuálnym main, nie s historickým základom;
- **automatizovaný oracle —** build, testy, contracts a policies dávajú rýchly výsledok;
- **viditeľný spoločný stav —** tím vie, či je mainline zdravá;
- **urgentnú opravu broken main —** červený main sa nepovažuje za normálny backlog.

## 3. Hlavná línia ako integračný kontrakt

Main branch reprezentuje najnovší akceptovaný integračný stav. Nemusí byť automaticky nasadený do produkcie, ale musí byť vhodným vstupom pre ďalší delivery proces.

Zdravá mainline má tieto invariants:

- **Source consistency —** commit graph a dependency metadata tvoria konzistentný stav;
- **Buildability —** autoritatívny build možno zopakovať v definovanom prostredí;
- **Required evidence —** blocking checks boli kompletne vykonané a prešli;
- **Artifact identity —** výsledný build je jednoznačne spojený s commitom a pipeline runom;
- **No silent incompleteness —** chýbajúci shard, report alebo scanner nie je interpretovaný ako pass;
- **Fast repair policy —** pri zlyhaní existuje jasný vlastník a reakcia.

Mainline health nie je iba zelená ikona posledného jobu. Zahŕňa čerstvosť výsledku voči aktuálnemu main, úplnosť evidence a dôveryhodnosť runnera a toolchainu.

## 4. Častá integrácia a malý batch

CI preferuje malé, časté a kompatibilné zmeny. Menší batch znižuje:

- počet možných príčin failure,
- rozsah review,
- merge konflikty,
- rollback blast radius,
- čas potrebný na opätovné overenie,
- riziko, že sa zmena stane neoddeliteľnou od ďalších zmien.

Veľkú capability možno rozdeliť pomocou:

- feature flags,
- branch by abstraction,
- backward-compatible API a schema zmien,
- dark code paths bez používateľskej expozície,
- postupných refactoringov,
- expand-contract migrácií,
- oddelenia deploymentu od releaseu.

Skrytý nedokončený kód nesmie zhoršiť existujúce behavior, bezpečnosť alebo operability. Feature flag nie je ospravedlnenie pre nekompatibilný build.

## 5. Candidate integration state

Pull request tip nie je vždy stav, ktorý sa reálne integruje. CI musí explicitne pomenovať, čo testuje:

- source branch SHA,
- target branch SHA,
- synthetic merge commit SHA,
- rebased candidate SHA,
- merge-queue group SHA,
- tag alebo release commit.

Príklad race:

```text
PR A je zelený proti main M1
PR B je zelený proti main M1
A sa merge-ne a vytvorí M2
B sa merge-ne bez nového testu
→ B nikdy nebol overený proti M2
```

Dôveryhodné CI testuje kandidáta proti aktuálnemu cieľovému stavu a po každej relevantnej zmene targetu vie výsledok invalidovať.

## 6. Merge-result testing

Merge-result pipeline vytvorí syntetický alebo skutočný merge candidate a testuje výsledný tree, nie iba source branch.

Overuje:

- textové a semantic merge konflikty,
- kombinovaný dependency graph,
- spoločný build a test suite,
- zmenu generated files alebo lockfile,
- kompatibilitu viacerých paralelných zmien,
- policy nad výsledným obsahom.

Výsledok musí byť viazaný na presný candidate SHA. „PR bol zelený včera“ nie je dôkaz pre dnešný merge, ak sa main alebo pipeline policy zmenili.

## 7. Merge queue

Merge queue serializuje alebo batchuje schválené zmeny a testuje ich proti predpokladanému budúcemu main.

Typický lifecycle:

```text
PR schválený
→ zaradenie do queue
→ vytvorenie candidate merge state
→ required checks
→ merge pri zelenom výsledku
→ invalidácia alebo opakovanie pri zmene predchodcu
```

Merge queue musí definovať:

- poradie a fairness,
- maximálnu veľkosť batchu,
- invalidáciu po failure,
- či sa neúspešný batch rozdeľuje,
- required checks a freshness,
- správanie pri force push alebo zmene approval,
- ochranu pred starvation dlhého jobu.

Queue znižuje race medzi individuálne zelenými PRs, ale sama negarantuje správnosť. Stále potrebuje úplný dependency graph a dôveryhodné tests.

## 8. CI pipeline lifecycle

Autoritatívny CI flow typicky obsahuje:

```text
resolve event a candidate SHA
→ čistý checkout
→ obnoviť toolchain a dependencies
→ statické kontroly
→ build
→ unit/integration/contract tests
→ package immutable artifact
→ security a policy verification
→ publikovať reports, provenance a status
```

Presné poradie sa môže paralelizovať podľa dependency DAG. Lacné a vysoko diagnostické kontroly patria na začiatok critical path, ale artifact-dependent kontroly musia pracovať s tým istým buildom, ktorý sa publikuje.

## 9. Reprodukovateľný build

Reprodukovateľný build znamená, že rovnaké deklarované vstupy vytvoria funkčne alebo bitovo ekvivalentný výstup podľa definovaného kontraktu.

Vstupy zahŕňajú viac než source:

- commit a submodules,
- dependency lockfiles,
- compiler, SDK a build image,
- build flags a environment variables,
- locale, timezone a platform architecture,
- generated-code tools,
- network-fetched resources,
- timestamps a ordering,
- pipeline templates a reusable actions.

Build musí minimalizovať nezdokumentované vstupy z hosta. „Funguje na mojom notebooku“ často znamená, že build používa implicitný toolchain, credentials, cache alebo filesystem state.

## 10. Build once a immutable artifact

Odporúčaný model:

```text
candidate commit
→ jeden dôveryhodný build
→ immutable artifact digest
→ ďalšie testovanie a promotion toho istého artifactu
```

Rebuild pre staging a produkciu vytvára nový supply-chain event a nové bytes. Aj keď používa rovnakú verziu source, dependencies alebo base image sa mohli zmeniť.

Artifact musí mať:

- immutable identifikátor alebo digest,
- source commit a build-run väzbu,
- toolchain a dependency metadata,
- SBOM podľa potreby,
- provenance a prípadne podpis,
- retention policy,
- jasný stav verifikácie a promotion.

Environment-specific konfigurácia má byť čo najviac oddelená od artifactu.

## 11. Test evidence a provenance

CI neprodukuje iba binary alebo image. Produkuje rozhodovací dôkaz.

Evidence môže obsahovať:

- test reports a first-attempt výsledky,
- coverage a mutation reports,
- contract compatibility,
- SAST/SCA/secret findings,
- SBOM a license report,
- build logs a checksums,
- candidate SHA a target SHA,
- runner image a tool versions,
- policy version,
- timestamps a environment identity.

Evidence musí byť dostupné bez rerunu. Rerun môže použiť iný dependency state, runner alebo external service a odstrániť pôvodný failure.

## 12. Cache nie je source of truth

Cache zrýchľuje CI, ale nesmie meniť correctness.

Cache key musí zahŕňať relevantné vstupy:

- OS a architecture,
- toolchain version,
- dependency lock hash,
- build flags,
- source alebo dependency graph podľa typu cache,
- pipeline/tool configuration.

Riziká:

- stale cache po neúplnej invalidácii,
- cache poisoning z nedôveryhodnej branch,
- cross-project contamination,
- obnovovanie privileged outputu v untrusted jobe,
- rozdiel medzi warm a cold buildom,
- tichý fallback na nekompatibilný artifact.

Pipeline musí vedieť prejsť s prázdnou cache. Periodický cold-cache build pomáha overiť tento invariant.

## 13. Untrusted code a trust boundaries

CI často spúšťa kód z pull requestu. Tento kód môže byť nedôveryhodný a pokúsiť sa čítať credentials, modifikovať cache alebo exfiltrovať interné dáta.

Oddeluj:

- untrusted verification jobs bez citlivých secrets,
- trusted jobs nad akceptovaným commitom,
- artifact verification bez produkčných práv,
- deployment jobs s environment-scoped identity.

Ochrany:

- ephemeral runners,
- least-privilege tokeny,
- short-lived workload identity,
- zákaz production secrets vo fork pipelines,
- oddelené cache namespaces,
- network egress controls,
- protected branch/environment policy,
- pinovanie reusable actions a images digestom.

CI pipeline code je privilegovaný software. Zmena workflowu musí podliehať review a ownership pravidlám.

## 14. Runner isolation

Runner je execution, capacity a security boundary.

Typy:

- hosted ephemeral VM alebo container,
- self-hosted persistent host,
- autoscalovaný VM pool,
- Kubernetes pod,
- specialized hardware runner.

Persistent runner nesie riziká:

- zvyškový workspace,
- tokeny v procesoch alebo filesysteme,
- poisoned cache,
- host-level persistence,
- drift toolchainu,
- cross-project leakage.

Container izoluje procesy a filesystem, ale zdieľa kernel. Shell executor na hoste poskytuje slabšiu boundary. Citlivý deploy job potrebuje samostatný trusted pool a scoped network access.

## 15. Quality gates

Blocking gate má chrániť konkrétne významné riziko a musí byť:

- presný,
- reprodukovateľný,
- kompletný,
- akčný,
- vlastnený,
- primerane rýchly,
- auditovateľný.

Príklady blocking failures:

- compile error,
- deterministický test failure,
- contract incompatibility,
- high-confidence secret leak,
- neplatný artifact signature,
- critical policy violation.

Advisory checks sú vhodné pre nový alebo menej presný signál. Advisory výsledok potrebuje ownera a plán, nie permanentné ignorovanie.

## 16. Failure taxonomy

Pipeline nemá všetko zredukovať na červenú alebo zelenú.

Rozlišuj:

- **Product/change failure —** kód, test, contract alebo policy je porušená;
- **Flaky/intermittent failure —** rovnaký deklarovaný stav má nekonzistentný výsledok;
- **Infrastructure failure —** runner, registry, network alebo control plane zlyhal;
- **Tool failure —** analyzer alebo test framework sa nespustil alebo havaroval;
- **Incomplete evidence —** chýba shard, artifact alebo report;
- **Canceled/superseded —** run stratil hodnotu pre novší commit;
- **Policy skip —** krok sa zámerne nespustil podľa explicitného pravidla.

Infrastructure failure nesmie byť automaticky pass. Retry je vhodný iba pre identifikovaný transient failure a prvý výsledok musí zostať viditeľný.

## 17. Flaky tests a retries

Flaky blocking test degraduje celý integračný kontrakt. Vedie k rerun-until-green, dlhým queues a strate dôvery.

CI má sledovať:

- first-attempt pass rate,
- pass-after-retry rate,
- failure signatures,
- quarantine age,
- ownera a remediation deadline,
- environment a runner koreláciu.

Retry môže potvrdiť intermittency, ale nesmie prepísať historický failure. Quarantine je dočasná zmena gate policy, nie oprava testu.

## 18. Broken main

Keď autoritatívna main pipeline zlyhá:

1. označ main ako broken a zastav ďalšie rizikové merges podľa policy;
2. identifikuj first bad candidate a failure class;
3. rozhodni medzi revertom a rýchlou opravou;
4. obnov green state čo najmenším changeom;
5. over artifact a downstream consumers;
6. analyzuj, prečo PR alebo merge queue failure nezachytili;
7. pridaj regression, dependency edge alebo policy opravu.

Dlhodobo červený main normalizuje failure. Tím potom nevie odlíšiť novú regresiu od starého šumu.

## 19. Pipeline performance

CI optimalizuje čas k užitočnému rozhodnutiu, nie iba celkový CPU čas.

Kľúčové pojmy:

- **Queue time —** čakanie na runner alebo concurrency slot;
- **Time to first useful feedback —** prvý akčný failure;
- **Critical path —** najdlhšia dependency cesta po konečný required výsledok;
- **Fan-out/fan-in overhead —** čas rozdelenia, prenosu a agregácie;
- **Wasted execution —** jobs bežiace po superseded commite;
- **Cache effectiveness —** zrýchlenie bez correctness regresie.

Optimalizácie:

- bezpečný affected-test selection,
- paralelizácia nezávislých jobs,
- test sharding podľa historického času,
- skoré fail-fast checks,
- zrušenie superseded runs,
- elastický runner pool,
- zníženie artifact-transfer overheadu.

Viac paralelizácie môže zvýšiť queueing, quotas a contention. Meraj critical path, nie iba počet jobs.

## 20. Observability CI systému

CI je produkčný systém pre delivery. Potrebuje vlastnú telemetry.

Sleduj:

- pipeline a job success podľa failure class,
- queue time a runner utilization,
- p50/p95 time to first feedback,
- total a critical-path duration,
- mainline health a čas broken state,
- flaky a retry rate,
- cache hit/miss a cold-build success,
- artifact publication failures,
- merge-queue wait a invalidation rate,
- canceled/superseded execution,
- infrastructure a tool failure rate.

Deployment frequency alebo počet runs bez reliability a feedback kontextu nie sú kvalitná metrika.

## 21. Diagnostický postup

Pri zlyhaní CI:

1. identifikuj candidate SHA, target SHA a pipeline definition version;
2. rozlíš product, test, tool, infrastructure a incomplete-evidence failure;
3. over runner image, architecture, resources a network;
4. skontroluj dependency lock, cache key a cold-cache reprodukciu;
5. zachovaj logs, test report, core dump a artifact metadata;
6. zopakuj najmenší relevantný job s rovnakými vstupmi;
7. porovnaj lokálne a CI environment differences;
8. pri merge failure over synthetic merge tree a generated files;
9. oprav root cause alebo dočasne zmeň gate iba s ownerom a expiry;
10. potvrď first-attempt green výsledok na novom candidate SHA.

## 22. Typické anti-patterny

### CI ako nočný build

Integrácia ostáva veľkým batchom a feedback prichádza neskoro.

### Testovanie iba source branch

Zelený branch tip neoveruje skutočný merge result proti aktuálnemu main.

### Rebuild pre každý environment

Promuje sa iný artifact než ten, ktorý prešiel pôvodnými kontrolami.

### Cache ako povinný skrytý vstup

Cold build zlyhá alebo vytvorí iný výsledok.

### Všetky failures sú „retry“

Deterministické chyby a flaky tests sa maskujú ako transportné problémy.

### Persistent privileged runner pre untrusted PRs

Nedôveryhodný kód môže ukradnúť credentials alebo kompromitovať ďalšie jobs.

### Main môže zostať červený

Zelený status prestáva byť dôveryhodným integračným kontraktom.

### Gate bez vlastníka

Failure sa stáva frontou manuálnych bypassov namiesto rýchleho feedbacku.

## 23. Praktický rozhodovací rámec

Pre CI workflow odpovedz:

1. Ktorý presný integračný stav testujeme?
2. Ako sa výsledok invaliduje pri zmene main alebo pipeline policy?
3. Sú source, dependencies, toolchain a build environment explicitné?
4. Vzniká jeden immutable artifact s provenance?
5. Ktoré checks sú blocking a aké riziko chránia?
6. Ako rozlišujeme finding, infra failure a incomplete run?
7. Ktorý kód je nedôveryhodný a aké credentials môže dostať?
8. Ako sa izolujú runners, caches a artifact stores?
9. Aká je retry a quarantine policy?
10. Ako sa obnovuje broken main?
11. Aký je critical path a time to first useful feedback?
12. Aké evidence zostáva pre audit a diagnostiku?

## 24. Kontrolný checklist

- candidate a merge-result SHA sú explicitné;
- required checks sú čerstvé voči aktuálnemu targetu;
- build funguje v čistom prostredí;
- dependencies a toolchain sú pinované;
- artifact je immutable a prepojený s commitom;
- reporty a shards sa agregujú kompletne;
- cache je optimalizácia, nie hidden source of truth;
- untrusted jobs nemajú citlivé secrets;
- deploy jobs používajú oddelenú scoped identity;
- tool a infrastructure failure nie sú pass;
- retries sú obmedzené na transient classes;
- first-attempt výsledky zostávajú viditeľné;
- broken main má urgentný recovery postup;
- pipeline má telemetry a ownera;
- periodic cold build a širší regression overujú selection a cache assumptions.

## 25. Kontrolné otázky

1. Čo odlišuje CI od obyčajného build servera?
2. Prečo je integračné rozhodnutie dôležitejšie než branch status?
3. Aký je rozdiel medzi source branch SHA a merge-result SHA?
4. Aký race rieši merge queue?
5. Čo všetko patrí medzi vstupy reprodukovateľného buildu?
6. Prečo sa má buildovať raz a promovať rovnaký artifact?
7. Prečo cache nesmie byť source of truth?
8. Aké trust boundaries existujú medzi untrusted PR, buildom a deployom?
9. Aké failure classes má CI rozlišovať?
10. Prečo retry nesmie vymazať first-attempt failure?
11. Ako sa obnovuje broken main?
12. Čo je critical path pipeline?
13. Ktoré metriky dokazujú kvalitu CI feedback loopu?
14. Prečo zelený PR zo včera nemusí byť dnes mergeovateľný?

## Summary

Continuous Integration je disciplína častej integrácie malých zmien a automatizovaného overovania presného kandidátneho merge stavu. Dôveryhodné CI vytvára reprodukovateľný build, jeden immutable artifact, kompletné evidence a čerstvé required checks, pričom oddeľuje untrusted code, verification a deployment trust boundaries. Jeho kvalita sa meria zdravím mainline, časom k užitočnému feedbacku, stabilitou gates a schopnosťou rýchlo obnoviť broken main, nie počtom pipeline behov.

## Glossary impact

Relevantné pojmy: Continuous Integration, mainline, candidate SHA, merge-result pipeline, synthetic merge commit, merge queue, build once, reproducible build, immutable artifact, evidence provenance, pipeline cache, runner isolation, broken main, critical path a time to first useful feedback.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Chaos testing](../04-testing-and-quality/chaos-testing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Continuous Delivery →](continuous-delivery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->