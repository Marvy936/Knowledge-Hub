# Smoke a regression tests

Smoke tests overujú, či je build alebo deployment vôbec použiteľný na ďalšie testovanie. Regression tests overujú, že existujúce správanie ostalo po zmene zachované.

Tieto kategórie opisujú účel testu, nie jeho technickú vrstvu:

- smoke test môže byť API, UI, CLI alebo infrastructure probe,
- regression test môže byť unit, integration, contract alebo E2E test.

## 1. Smoke test

Smoke test je krátky, široký a kritický sanity check.

Má odpovedať:

```text
Je systém natoľko funkčný, aby malo zmysel pokračovať?
```

Typické kontroly:

- proces sa spustil,
- health endpoint odpovedá,
- databázové pripojenie funguje,
- kritický endpoint vracia validnú odpoveď,
- používateľ sa dokáže prihlásiť,
- deployment má ready instances,
- základný write/read workflow funguje.

## 2. Build verification test

Smoke test spustený nad novým buildom sa často nazýva Build Verification Test (BVT).

Overuje napríklad:

- artifact je spustiteľný,
- povinné súbory sú prítomné,
- konfigurácia sa načíta,
- migrácie sa dajú aplikovať,
- základné dependencies sú kompatibilné.

BVT má zastaviť drahšie testy pri evidentne nepoužiteľnom build-e.

## 3. Deployment smoke test

Po deploymente over:

- správnu version alebo commit SHA,
- readiness,
- routing,
- TLS a DNS,
- kritický read path,
- bezpečný write path,
- observability signály,
- neprítomnosť okamžitého error spike.

Deployment success z orchestration nástroja neznamená application success.

## 4. Smoke test vs. health check

Health check býva kontinuálny a úzky runtime signal.

Smoke test je aktívny scenár, ktorý môže prejsť cez viac vrstiev.

Príklad:

```text
readiness endpoint
→ proces prijíma traffic

smoke transaction
→ používateľský request prejde cez proxy, API, DB a response validation
```

Health check nemá vykonávať drahé alebo deštruktívne business operácie.

## 5. Sanity test

Sanity test je cielená kontrola konkrétnej zmeny alebo opravy.

Príklad:

```text
opravený export CSV
→ over správne encoding, headers a jednu kritickú business hodnotu
```

Terminológia smoke vs. sanity sa medzi tímami líši. Dôležitý je explicitný scope a trigger.

## 6. Regression test

Regression test chráni už existujúce správanie pred nechcenou zmenou.

Vzniká z:

- požiadavky,
- historickej chyby,
- incidentu,
- kritického invariantu,
- compatibility contractu,
- bezpečnostnej požiadavky.

Dobrý bug fix obsahuje test, ktorý pred opravou zlyhá a po oprave prejde.

## 7. Functional regression

Overuje, že funkcie naďalej vracajú správne výsledky.

Príklady:

- ceny a dane,
- oprávnenia,
- state transitions,
- API responses,
- exporty,
- workflow.

## 8. Non-functional regression

Regresia môže vzniknúť aj mimo funkčnej správnosti:

- latency,
- throughput,
- memory usage,
- startup time,
- accessibility,
- security posture,
- compatibility,
- observability.

Test suite preto nemá chrániť iba business output.

## 9. Visual regression

Porovnáva renderovaný UI výstup s baseline.

Riziká:

- fonty,
- antialiasing,
- browser version,
- dynamic content,
- timezone,
- animations.

Stabilizácia:

- pinned browser a fonts,
- fixed viewport,
- vypnuté animations,
- maskovanie dynamických oblastí,
- explicitný review baseline zmien.

Snapshot approval bez kontroly môže legitimizovať chybu.

## 10. Snapshot testing

Snapshot test ukladá serializovaný výstup a porovnáva ho pri ďalšom behu.

Vhodný pre:

- AST,
- rendered configuration,
- serializer output,
- CLI help,
- komplexné stabilné štruktúry.

Nevhodný, ak:

- snapshot je obrovský,
- obsahuje nondeterministické values,
- reviewer nevie posúdiť význam diffu,
- kritické assertions sú schované v množstve textu.

## 11. Regression suite selection

Nie každá zmena musí spustiť všetky testy okamžite.

Možnosti:

- affected tests podľa dependency graphu,
- path-based selection,
- risk-based tags,
- historical test impact analysis,
- full nightly suite,
- pre-release full regression.

Selection musí byť konzervatívna. Nesprávny dependency graph môže vynechať relevantný test.

## 12. Risk-based regression

Priorita testov podľa:

- business criticality,
- change scope,
- failure history,
- complexity,
- usage frequency,
- blast radius,
- regulatory dopad.

Príklad:

```text
payment module change
→ payment unit/integration
→ contract tests
→ checkout E2E
→ idempotency a retry scenarios
→ relevant performance/security checks
```

## 13. Test tagging

Užitočné tagy:

- `smoke`,
- `critical`,
- `regression`,
- `slow`,
- `db`,
- `network`,
- `security`,
- `quarantined`.

Každý tag musí mať definovaný význam a pipeline behavior. Inak sa taxonomy rozpadne.

## 14. Post-deployment smoke

Smoke po deploymente má byť:

- read-only alebo bezpečne idempotentný,
- tenantovo izolovaný,
- jasne označený v logoch,
- rýchly,
- schopný rollback decisionu,
- spustiteľný z relevantného network pathu.

Test z vnútra podu nemusí odhaliť chybu verejného DNS, TLS alebo ingressu.

## 15. Synthetic monitoring

Pravidelne spúšťaný produkčný smoke-like test overuje používateľský path.

Musí riešiť:

- test identity,
- test data cleanup,
- rate limits,
- alert threshold,
- region/source location,
- rozlíšenie test trafficu,
- bezpečnosť credentials.

Synthetic monitor nie je náhrada reálneho user monitoring-u, ale dopĺňa ho o kontrolovaný probe.

## 16. Regression test po incidente

Po incidente nevytváraj iba test konkrétnej hodnoty. Zachyť triedu failure.

Incident:

```text
timeout po opakovanom retry vytvoril duplicate payment
```

Slabý test:

```text
presne tento request ID nevytvorí duplicitu
```

Silnejší test:

- concurrent retries,
- response loss po commit-e,
- rovnaký idempotency key,
- recovery po process restart,
- persistence uniqueness constraint.

## 17. Regression suite health

Sleduj:

- duration,
- failure rate,
- flaky rate,
- retry rate,
- queue time,
- tests bez recent execution,
- tests bez ownera,
- quarantined test age,
- defect escape rate.

Počet testov nie je hlavná metrika. Dôležitá je rýchlosť a spoľahlivosť feedbacku.

## 18. Baseline management

Visual, performance a snapshot regression potrebujú baseline lifecycle:

- kto baseline schvaľuje,
- na akej platforme vzniká,
- ako sa versionuje,
- kedy sa regeneruje,
- ako sa auditujú zmeny,
- ako sa odlišuje očakávaná zmena od chyby.

Automatické prepísanie baseline pri failure ruší hodnotu testu.

## 19. Anti-patterny

### Smoke suite trvá hodinu

Stráca funkciu rýchleho gate-u.

### Smoke overuje iba `/health`

Neoverí kritický request path.

### Full regression pri každom keystroke

Feedback je príliš pomalý a vývojári testy obchádzajú.

### Regression suite bez pruning-u

Obsahuje duplicitné a zastarané tests s vysokým maintenance costom.

### Bug fix bez reprodukčného testu

Rovnaká trieda chyby sa môže vrátiť.

### Rerun-until-green

Maskuje flaky alebo reálny intermittent failure.

## 20. Pipeline placement

Praktický model:

```text
commit/PR
→ rýchle unit a targeted regression

build
→ BVT/smoke

integration environment
→ integration a contract regression

deployment
→ post-deploy smoke

nightly
→ širšia regression a compatibility

pre-release
→ risk-based full regression

production
→ synthetics a SLI validation
```

## 21. Rozhodovací rámec

1. Aké minimum dokazuje, že build je použiteľný?
2. Ktoré workflow sú kritické pre deployment smoke?
3. Je smoke bezpečný a idempotentný?
4. Akú regresiu má konkrétny test chrániť?
5. Ktorá vrstva testu je najnižšia a dostatočná?
6. Potrebujeme full suite alebo affected selection?
7. Aký je baseline a kto ho schvaľuje?
8. Ako sa zaznamená flaky failure?
9. Kto vlastní zastarané a quarantined tests?
10. Aké produkčné synthetics dopĺňajú pre-release suite?

## 22. Kontrolné otázky

1. Čo je cieľom smoke testu?
2. Aký je rozdiel medzi smoke testom a health checkom?
3. Čo je Build Verification Test?
4. Aký je rozdiel medzi smoke a sanity testom?
5. Čo chráni regression test?
6. Aké sú non-functional regressions?
7. Kedy je snapshot test vhodný?
8. Ako funguje risk-based regression selection?
9. Čo musí riešiť production synthetic test?
10. Prečo rerun-until-green poškodzuje dôveru v suite?

## Glossary impact

Relevantné pojmy: smoke test, Build Verification Test, sanity test, regression test, visual regression, snapshot test, test impact analysis, risk-based testing, synthetic monitoring a baseline.