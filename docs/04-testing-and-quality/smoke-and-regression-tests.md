# Smoke a regression tests

Smoke test a regression test opisujú účel kontroly, nie konkrétnu technickú vrstvu. Smoke test rýchlo rozhoduje, či je build alebo deployment dostatočne funkčný na ďalšie používanie alebo testovanie. Regression test chráni už známe správanie pred nechcenou zmenou.

```text
Smoke
→ je nový stav základne životaschopný?

Regression
→ zostalo dôležité existujúce správanie zachované?
```

Smoke môže byť API, UI, CLI, databázový alebo infraštruktúrny probe. Regression test môže byť unit, integration, contract, performance, security alebo E2E test.

## 1. Mentálny model

Smoke a regression suite majú rozdielne optimalizačné ciele:

- **smoke —** minimalizuje čas do rozhodnutia, či má ďalšia validácia alebo traffic zmysel,
- **regression —** maximalizuje pravdepodobnosť zachytenia nechcenej zmeny pri prijateľnej cene feedbacku,
- **smoke oracle —** overuje životaschopnosť a kritický wiring,
- **regression oracle —** porovnáva nové správanie s explicitným kontraktom alebo schváleným baseline,
- **smoke failure —** typicky zastaví ďalšiu fázu alebo vyvolá rollback,
- **regression failure —** blokuje, varuje alebo vyžaduje triage podľa rizika a spoľahlivosti testu.

Zmiešanie týchto cieľov vedie buď k hodinovej smoke suite, alebo k plytkej regression suite, ktorá kontroluje iba to, že služba odpovedá.

## 2. Smoke test

Smoke test je krátka sada širokých, ale plytkých kontrol. Má odpovedať:

```text
Je systém natoľko funkčný,
aby malo zmysel pokračovať v testovaní, deploymente alebo obsluhe trafficu?
```

Dobrý smoke test overí minimálny reprezentatívny tok cez najkritickejšie boundaries. Nemá dokazovať úplnú správnosť systému.

## 3. Smoke gate contract

Každý smoke gate musí definovať:

- **target —** build, artifact, environment alebo deployment, ktorý testuje,
- **trigger —** po builde, po deploymente, pred promotion alebo periodicky v produkcii,
- **time budget —** maximálny čas na výsledok,
- **scope —** ktoré kritické boundaries sú zahrnuté,
- **oracle —** podmienky úspechu a failure,
- **side effects —** či je test read-only, idempotentný alebo potrebuje cleanup,
- **decision —** pokračovať, zastaviť, rollbacknúť alebo iba upozorniť,
- **owner —** kto reaguje na failure.

Bez tohto kontraktu sa smoke označenie stane iba tagom bez konzistentného pipeline významu.

## 4. Build Verification Test

Smoke spustený nad novým buildom sa často nazýva Build Verification Test alebo BVT. Jeho cieľom je zastaviť drahšie testy pri zjavne nepoužiteľnom artefakte.

BVT môže overiť:

- artifact sa dá načítať a spustiť,
- package obsahuje povinné files a metadata,
- entrypoint a základná konfigurácia fungujú,
- databázové migrácie sa dajú načítať alebo bezpečne naplánovať,
- runtime dependencies majú kompatibilné verzie,
- základný command alebo API request vráti validný výsledok,
- artifact neobsahuje evidentne nesprávny target alebo platformu.

BVT má bežať nad tým istým immutable artifactom, ktorý bude pokračovať do ďalších fáz.

## 5. Artifact provenance

Smoke výsledok musí zaznamenať:

```text
source commit alebo release tag
→ artifact digest
→ build metadata
→ deployment revision
→ environment identity
→ feature-flag snapshot
→ test run ID
```

Ak sa smoke vykonal nad image `latest`, ktorá bola medzičasom prepísaná, výsledok nemožno spoľahlivo priradiť k nasadenému obsahu.

## 6. Deployment smoke test

Deployment smoke test overuje, či nový artifact funguje v konkrétnom runtime prostredí. Orchestrátor môže hlásiť úspešný rollout, hoci aplikácia má chybnú route, TLS trust, secret, migration alebo dependency configuration.

Reprezentatívny post-deployment smoke má overiť:

1. očakávanú version alebo digest,
2. readiness a počet zdravých instances,
3. DNS, TLS a routing z relevantného client pathu,
4. kritický read request,
5. bezpečný write/read alebo command workflow,
6. authorization a identity podľa potreby,
7. základný dependency path,
8. logs, metrics alebo trace pre smoke transakciu,
9. neprítomnosť okamžitého error alebo saturation spike-u.

## 7. Smoke z relevantného observation pointu

Test z vnútra podu môže potvrdiť proces a lokálny endpoint, ale neoverí public DNS, external load balancer, certificate chain, WAF, ingress, network policy alebo client-visible headers.

Pre kritickú službu možno potrebovať viac observation points:

```text
inside process
→ localhost health

inside cluster
→ service routing

outside cluster
→ public DNS/TLS/proxy path

business synthetic
→ reálny používateľský workflow
```

Každý probe má iný failure domain; jeden nemá predstierať dôkaz za všetky vrstvy.

## 8. Smoke test verzus health check

Health check je úzky kontinuálny runtime signal. Smoke test je aktívny scenár vykonaný pri konkrétnom rozhodovacom bode.

```text
readiness probe
→ môže process prijímať traffic?

smoke transaction
→ prejde kritický request cez relevantné vrstvy a vznikne správny výsledok?
```

Health endpoint nemá vykonávať drahé alebo deštruktívne business operácie. Smoke môže vykonať kontrolovanú transakciu, ale musí mať izolované dáta a cleanup.

## 9. Sanity test

Sanity test je cielená kontrola konkrétnej zmeny, opravy alebo oblasti. Napríklad po oprave CSV exportu overí encoding, headers a kritickú business hodnotu.

Terminológia smoke a sanity nie je v organizáciách jednotná. Rozhodujúce je explicitne pomenovať scope, trigger, oracle a gate význam.

## 10. Bezpečný write smoke

Read-only smoke môže prehliadnuť chybu databázového zápisu, message publishingu alebo worker spracovania. Write smoke je silnejší, ale musí byť bezpečný.

Požiadavky:

- test-only tenant alebo account,
- unikátny correlation prefix,
- idempotency key,
- minimálny business dopad,
- explicitný cleanup alebo krátke TTL,
- označenie test trafficu v logs a metrics,
- zákaz spustenia v neautorizovanom environment-e,
- žiadne reálne emaily, platby alebo externé objednávky.

## 11. Smoke timeout a failure semantics

Smoke má krátky, ale realistický deadline. Pri failure musí reportovať posledný úspešný krok, observation point, request ID a konkrétnu podmienku, ktorá nebola splnená.

Rozlišuj:

- **hard failure —** artifact alebo environment nie je životaschopný; promotion sa zastaví,
- **dependency failure —** externá služba blokuje kritický path; rozhodnutie závisí od fallback a release policy,
- **test infrastructure failure —** runner alebo fixture nefunguje; release dôkaz je neznámy, nie zelený,
- **advisory anomaly —** napríklad zvýšená latency bez prekročenia blocking hranice.

## 12. Rollback a smoke

Post-deployment smoke má byť previazaný s rollback alebo roll-forward policy. Automatický rollback je vhodný iba vtedy, keď:

- smoke spoľahlivo rozlišuje product failure,
- rollback je kompatibilný s databázou a externými side effects,
- predchádzajúci artifact je známy a dostupný,
- ďalší rollback nevytvorí väčší incident,
- výsledok a rozhodnutie sú auditované.

Inak smoke failure môže zastaviť traffic promotion a vyžadovať riadené rozhodnutie.

## 13. Regression test

Regression test chráni správanie, ktoré už bolo považované za správne alebo potrebné. Jeho hodnota nevzniká z označenia `regression`, ale z jasnej väzby na chránený kontrakt alebo triedu failure.

Zdrojom regression testu môže byť:

- requirement alebo acceptance criterion,
- kritický invariant,
- opravený bug,
- incident alebo near miss,
- compatibility contract,
- bezpečnostná požiadavka,
- performance alebo capacity baseline,
- observability alebo operability očakávanie.

## 14. Regression provenance

Pri každom významnom regression teste má byť dohľadateľné:

```text
čo test chráni
→ prečo je to dôležité
→ pôvodný bug, incident alebo requirement
→ aký failure pred opravou reprodukoval
→ na akej vrstve sa vykonáva
→ kto test vlastní
```

Test bez známeho účelu sa po rokoch ťažko upravuje alebo odstraňuje a často sa zmení na maintenance debt.

## 15. Bug fix a reprodukčný test

Silný bug-fix workflow:

1. reprodukuje failure v automatizovanom teste,
2. potvrdí, že test pred opravou zlyhá správnym dôvodom,
3. implementuje opravu,
4. overí úspech testu a súvisiace invariants,
5. zaradí test do vhodnej suite,
6. pridá production signal, ak failure nebol predtým pozorovateľný.

Test má zachytiť triedu failure, nie iba jednu náhodnú hodnotu z incidentu.

## 16. Incident-to-regression príklad

Incident:

```text
server commitol payment,
response sa stratila,
client retry vytvoril druhú platbu
```

Silná regresná ochrana môže obsahovať:

- unit test idempotency state machine,
- integration test uniqueness constraintu,
- API test rovnakého idempotency key,
- concurrency test paralelných retries,
- restart test persistentného idempotency recordu,
- production metric duplicate-attempt detection.

Jedna vrstva nechráni všetky failure modes.

## 17. Functional regression

Functional regression overuje zachovanie business alebo technického správania, napríklad:

- výpočet cien, daní a rounding,
- authorization a tenant isolation,
- state transitions,
- API semantics,
- exporty a serializáciu,
- workflow a side effects,
- migration a backward compatibility.

Assertions majú overovať výsledok a relevantné invariants, nie nepodstatné interné kroky.

## 18. Non-functional regression

Regresia môže vzniknúť aj v latency, throughput, memory, startup time, accessibility, security posture, compatibility alebo observability.

Non-functional regression potrebuje definovaný baseline a toleranciu. Napríklad performance test nemá zlyhať pri každom 1 % rozdiele, ale pri štatisticky alebo prevádzkovo významnej degradácii s porovnateľným workloadom a prostredím.

## 19. Visual regression

Visual regression porovnáva renderovaný výstup s baseline. Stabilita vyžaduje pinned browser, fonty, viewport, locale, timezone, color scheme a vypnuté animations.

Dynamické oblasti možno maskovať, ale maskovanie nesmie skryť kritický obsah. Baseline update musí byť reviewovaná zmena, nie automatická reakcia na failure.

## 20. Snapshot testing

Snapshot test je vhodný pre stabilné komplexné štruktúry, napríklad AST, rendered configuration, CLI help alebo serializer output.

Snapshot je slabý, keď:

- je príliš veľký na zmysluplný review,
- obsahuje timestampy alebo náhodné IDs,
- kritické assertions sa stratia v rozsiahlej zmene,
- reviewer iba stlačí „update all“ bez porozumenia.

Dôležité invariants majú mať explicitné assertions aj pri použití snapshotu.

## 21. Baseline lifecycle

Visual, snapshot a performance regression potrebujú riadený baseline:

- autoritatívne prostredie a toolchain,
- verzia baseline a väzba na artifact,
- owner a approval pravidlo,
- tolerancia a comparison algorithm,
- audit zmien,
- expiry alebo reevaluation,
- možnosť porovnať starý a nový výsledok.

Automatické prepísanie baseline pri failure ruší oracle a robí test sebapotvrdzujúcim.

## 22. Regression suite selection

Nie každá zmena musí okamžite spustiť celý historický test corpus. Selection môže používať:

- dependency graph,
- changed paths,
- test-to-code mapping,
- risk tags,
- ownership boundaries,
- historickú koreláciu zmien a failures,
- pravidlá pre kritické shared components.

Selection optimalizuje feedback time, ale vytvára false-negative riziko, ak model nepozná skrytú dependency.

## 23. Test Impact Analysis

Test Impact Analysis odhaduje, ktoré testy sú ovplyvnené zmenou. Dôveryhodný systém musí:

1. vysvetliť, prečo bol test vybraný alebo vynechaný,
2. konzervatívne zahrnúť neznáme alebo dynamické dependencies,
3. sledovať false-green escapes,
4. pravidelne spúšťať širšiu suite na validáciu modelu,
5. invalidovať cache pri zmene toolchainu, konfigurácie alebo infraštruktúry.

Path-only selection je slabá pri generated code, runtime discovery, shared schemas a infraštruktúrnych zmenách.

## 24. Risk-based regression

Prioritu určuj podľa kombinácie:

```text
pravdepodobnosť regresie
× dopad failure
× neistota selection modelu
× zmena kritických boundaries
```

Zmena payment modulu typicky aktivuje payment unit/integration testy, API contracts, checkout E2E, idempotency a concurrency scenáre, relevantné security testy a cielený performance check.

## 25. Suite vrstvy a časové rozpočty

Praktická segmentácia:

```text
pre-commit
→ sekundy; lokálne deterministické regression checks

PR fast lane
→ minúty; affected a critical tests

build
→ BVT/smoke nad immutable artifactom

integration environment
→ cross-boundary regression

deployment
→ post-deploy smoke a guardrails

scheduled
→ širšia regression, compatibility a long-running checks

pre-release
→ risk-based full evidence set

production
→ synthetics, SLI a business validation
```

Dlhý test nemá byť odsunutý do nightly, ak chráni rozhodnutie, ktoré už prebehlo pred jeho výsledkom.

## 26. Test tagging governance

Tag má definovať pipeline správanie, nie iba kategóriu. Pre každý tag urč:

- význam,
- ownera,
- trigger,
- time budget,
- blocking status,
- dependency requirements,
- quarantine pravidlo.

Tagy ako `smoke`, `critical`, `slow`, `security` alebo `quarantined` bez governance sa časom prekrývajú a selection prestane byť predvídateľná.

## 27. Synthetic monitoring

Pravidelný produkčný synthetic je smoke-like kontrola reálneho používateľského pathu. Musí používať bezpečnú identitu, izolované dáta, regionálny source, kontrolovaný rate, credential rotation a jasné rozlíšenie test trafficu.

Synthetic dokáže aktívne odhaliť výpadok aj bez reálneho trafficu. Nenahrádza však Real User Monitoring, ktorý ukazuje skutočné zariadenia, siete a používateľské správanie.

## 28. Flaky regression a retries

Rerun nesmie prepísať first-attempt failure. Eviduj:

- prvý výsledok,
- všetky pokusy,
- failure signature,
- worker a environment,
- klasifikáciu product/test/environment,
- quarantine issue, ownera a deadline.

Chronicky flaky blocking test znižuje dôveru v celú suite a spôsobuje, že reálne regresie sa začnú ignorovať.

## 29. Regression suite health

Sleduj minimálne:

- first-attempt pass rate,
- flaky a retry rate,
- p50/p95 duration,
- queue time,
- failure triage time,
- quarantine age,
- tests bez ownera,
- tests bez recent execution,
- defect escape rate,
- false-negative selection incidents,
- podiel failures s dostatočnými artifacts.

Počet testov ani coverage samy osebe nehovoria, či suite poskytuje rýchly a spoľahlivý dôkaz.

## 30. Suite maintenance a retirement

Regression test nie je automaticky večný. Pravidelne posudzuj:

- či chránené behavior ešte existuje,
- či test nie je duplicitný,
- či sa riziko nepresunulo na nižšiu a lacnejšiu vrstvu,
- či baseline stále predstavuje správne očakávanie,
- či maintenance cost neprevyšuje dôkaznú hodnotu,
- či odstránenie testu zachová inú ekvivalentnú kontrolu.

Retirement má byť reviewované rozhodnutie s vysvetlením, nie náhodné zmazanie nepríjemného testu.

## 31. Diagnostika smoke failure

1. Over artifact digest a environment revision.
2. Zisti prvý neúspešný observation point.
3. Rozlíš startup, readiness, DNS/TLS, routing, identity, dependency a business failure.
4. Koreluj request ID, trace a server logs.
5. Over, či fixture a test identity boli platné.
6. Skontroluj okamžité metrics a deployment events.
7. Urči, či je bezpečný rollback, roll-forward alebo stop promotion.
8. Zachovaj artifacts a rozhodnutie.

## 32. Diagnostika regression failure

1. Identifikuj chránený kontrakt a pôvod testu.
2. Over first-attempt failure bez automatického rerunu.
3. Porovnaj artifact, toolchain, environment a baseline.
4. Rozlíš očakávanú behavior zmenu od neplánovanej regresie.
5. Zisti, či test nie je brittle voči internému detailu.
6. Reprodukuj najmenším scope-om.
7. Pri legitímnej zmene aktualizuj kontrakt a baseline cez review.
8. Pri chybe oprav produkt a over širší failure class.

## 33. Časté anti-patterny

### Smoke suite trvá hodinu

Prestáva poskytovať rýchle rozhodnutie a mieša sa s full regression.

### Smoke overuje iba `/health`

Neoverí routing, identity, databázový alebo business path.

### Smoke používa iný artifact než release

Zelený výsledok nemá väzbu na promovovaný obsah.

### Full regression pri každej malej zmene

Feedback je neprimerane pomalý a vývojári začnú gate obchádzať.

### Selection bez pravidelného full runu

Skryté dependencies môžu dlhodobo vytvárať false-green výsledky.

### Bug fix bez reprodukčného testu

Oprava nie je chránená pred návratom rovnakej triedy failure.

### Update-all baseline

Reviewer legitimizuje neznámu zmenu bez posúdenia jej významu.

### Rerun-until-green

Maskuje intermittent product failure aj flaky test.

## 34. Prevádzkový checklist

Pred použitím smoke alebo regression suite ako gate over:

- target artifact a environment sú jednoznačné,
- suite má explicitný time budget,
- smoke pokrýva relevantný client path,
- write smoke je bezpečný a izolovaný,
- failure vedie k jasnému rozhodnutiu,
- regression tests majú traceability na kontrakt alebo failure,
- selection model je konzervatívny a auditovateľný,
- širšia suite pravidelne validuje selection,
- baseline má ownera a review lifecycle,
- first-attempt výsledky a artifacts sa uchovávajú,
- flaky tests majú quarantine deadline,
- zastarané tests sa riadene retire-ujú.

## 35. Zhrnutie

Smoke test je rýchly survivability gate pre konkrétny build alebo deployment. Regression test chráni už známe správanie a historické riziká. Dôveryhodná stratégia viaže smoke na immutable artifact a relevantnú sieťovú cestu, regression testy na explicitný pôvod, selection na konzervatívny dependency a risk model a oba typy testov na jasné failure artifacts, ownership a rozhodovacie pravidlá.

## 36. Kontrolné otázky

1. Aký je rozdiel medzi smoke a regression účelom?
2. Čo musí definovať smoke gate contract?
3. Prečo orchestrator deployment success nestačí?
4. Ako sa smoke líši od readiness alebo health checku?
5. Kedy má smoke obsahovať write/read transakciu?
6. Čo znamená regression provenance?
7. Ako vznikne silný regression test z incidentu?
8. Aké false-negative riziko má Test Impact Analysis?
9. Prečo baseline update potrebuje review?
10. Ktoré metriky merajú zdravie regression suite?
11. Kedy je vhodné regression test retire-ovať?
12. Prečo rerun nesmie prepísať first-attempt failure?

## Glossary impact

Relevantné pojmy: smoke test, Build Verification Test, deployment smoke, sanity test, regression test, regression provenance, Test Impact Analysis, risk-based regression, visual regression, snapshot baseline, synthetic monitoring, first-attempt pass rate a test retirement.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: End-to-end a acceptance tests](end-to-end-and-acceptance-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Performance, load a stress tests →](performance-load-stress-tests.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
