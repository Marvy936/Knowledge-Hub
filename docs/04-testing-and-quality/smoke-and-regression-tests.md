# Smoke a regression tests

Smoke test je krátka sada kontrol, ktorá overuje, že nový build alebo deployment je dostatočne funkčný na ďalšie testovanie alebo exposure. Neoveruje celý systém. Jeho účelom je rýchlo zachytiť hrubé failures, napríklad neštartujúci process, nedostupný endpoint alebo nefunkčný kritický journey.

Regression test chráni správanie, ktoré už raz fungovalo alebo opravuje známy failure mode. Regression suite nie je automaticky „všetky testy“. Je to kurátorované portfolio dôkazov proti riziku, že nová zmena poškodila existujúce capabilities.

Neutrálny deployment smoke:

```text
process je ready
→ login funguje
→ jeden read journey prejde
→ jeden bounded write journey prejde
→ základná observability prijíma data
```

Smoke musí byť krátky, deterministický a mať jasný rollback alebo stop verdict. Plytký `/healthz` s `200` môže byť súčasťou smoke-u, ale sám nepreukazuje funkčný user flow.

Regression test vzniká často po incidente:

```text
failure: nulová cena pre určitý discount
→ root cause opravený
→ pridaný test pre presný invariant
→ širšia property alebo boundary kontrola
```

Test nemá iba zakonzervovať chybnú implementáciu. Má zachytiť intent, ktorý incident porušil. Inak refactoring rozbije test bez reálnej regresie alebo bug prejde cez príliš úzky example.

Risk-based výber zohľadňuje kritickosť journey, pravdepodobnosť zmeny, historické incidenty, blast radius a execution cost. Suite sa musí aj čistiť: duplicity, stále zelené nízkohodnotné testy a testy bez jasného ownera zvyšujú čas bez primeranej confidence.

Smoke a regression sú labels podľa účelu, nie podľa frameworku. Ten istý API test môže byť deployment smoke v jednom pipeline gate a regression check v inom kontexte.

Smoke test a regression test opisujú účel kontroly, nie jej technický scope:

```text
Smoke
→ je konkrétny build alebo deployment životaschopný pre ďalší krok?

Regression
→ zostalo dôležité existujúce správanie zachované?
```

Smoke môže byť API, UI, CLI alebo infraštruktúrny probe. Regression test môže byť unit, integration, contract, performance, security alebo E2E test.

## 1. Cieľ kapitoly

Nosný model kapitoly je:

```text
immutable release candidate
→ rýchly survivability gate
→ promotion alebo stop
→ risk-based regression evidence
→ release decision
→ incident/escape feedback
→ nový alebo upravený regression control
```

Smoke minimalizuje čas do rozhodnutia. Regression maximalizuje pravdepodobnosť zachytenia známej triedy failure pri primeranej cene feedbacku.

## 2. Nosný scenár: Atlas Orders 3.9.0

Atlas nasadzuje image:

```text
registry.example/orders@sha256:3f9...
```

Release má dve otázky:

1. Je nový artifact po deploymente použiteľný cez reálnu client path?
2. Zachoval správanie, ktoré chránia požiadavky, predchádzajúce bugy a incidenty?

Evidence chain:

```text
build verification
→ deploy konkrétneho digestu
→ external smoke transaction
→ critical regression lane
→ širšia risk-based regression
→ promotion
→ production synthetics a escaped-defect feedback
```

## 3. Smoke gate contract

Každý smoke gate definuje:

- **target** — build, artifact digest, deployment alebo environment;
- **trigger** — po builde, po deploymente, pred promotion alebo periodicky;
- **time budget** — maximálny čas na výsledok;
- **observation point** — odkiaľ sa cesta testuje;
- **scope** — ktoré kritické boundaries sú reálne;
- **oracle** — minimálne podmienky životaschopnosti;
- **side effects** — read-only alebo bezpečný write/read flow;
- **decision** — pokračovať, stopnúť promotion, rollbacknúť alebo eskalovať;
- **owner** — kto reaguje na product, environment alebo test-infrastructure failure.

Bez tohto kontraktu je `smoke` iba nejednoznačný tag.

## 4. Build verification

Build Verification Test overuje, že immutable artifact má základný execution contract ešte pred drahším deploymentom:

```text
artifact digest
→ package/image metadata
→ entrypoint
→ required files a runtime dependencies
→ startup v čistom prostredí
→ základný command alebo endpoint
→ structured result
```

BVT musí bežať nad tým istým artifactom, ktorý sa neskôr promovuje. Test source checkout-u nie je dôkazom pre publikovaný image alebo package.

## 5. Deployment smoke

Orchestrátor môže označiť rollout za úspešný, hoci používateľská cesta nefunguje. Atlas post-deploy smoke overí:

1. nasadený digest a deployment revision;
2. požadovaný počet ready instances;
3. public DNS, TLS certificate, SNI a reverse-proxy route;
4. autentifikovaný read request;
5. bezpečný `CreateOrder` write/read flow v test-only tenantovi;
6. PostgreSQL a broker path potrebný pre terminal order state;
7. audit, correlation a trace pre smoke transakciu;
8. neprítomnosť okamžitého error, restart alebo saturation spike-u.

Smoke nemá dokazovať všetky business edge cases. Má potvrdiť, že ďalší traffic alebo širšia validácia má zmysel.

## 6. Observation points

Rôzne probes dokazujú rozdielne vrstvy:

```text
process-local probe
→ process a localhost listener

cluster-internal probe
→ service discovery a east-west routing

external probe
→ public DNS, TLS, proxy/WAF a client-visible headers

business smoke
→ identity, write/read, persistence, broker a terminal result
```

Interný probe nesmie byť prezentovaný ako dôkaz public pathu.

## 7. Health check verzus smoke

Readiness odpovedá:

```text
Môže instance prijať traffic podľa lokálneho health contractu?
```

Smoke odpovedá:

```text
Prejde kritický request cez relevantnú deployment cestu a vznikne minimálny správny výsledok?
```

Health endpoint má zostať lacný a bezpečný. Smoke môže vykonať kontrolovanú transakciu s izolovanými dátami, idempotency key a cleanupom alebo TTL.

## 8. Bezpečný write smoke

Read-only probe môže prehliadnuť chybnú DB mutation, broker publish alebo worker processing. Atlas write smoke používa:

- test-only tenant a customer identity;
- unikátny order prefix, idempotency key a correlation ID;
- minimálnu objednávku bez reálnej platby;
- payment simulator alebo sandbox;
- explicitný deadline na terminal state;
- cleanup alebo krátku retention policy;
- označenie syntetického trafficu v logs a metrics;
- environment allowlist s fail-closed správaním.

## 9. Smoke outcome a rollback

Smoke môže skončiť ako:

```text
PASS
→ artifact je životaschopný pre ďalší krok

PRODUCT_FAIL
→ promotion stop; rollback/roll-forward podľa policy

DEPENDENCY_FAIL
→ release evidence je negatívny alebo podmienený fallbackom

TEST_INFRA_FAIL
→ dôkaz je neznámy, nie zelený

ADVISORY_ANOMALY
→ pokračovanie iba podľa explicitnej tolerancie
```

Automatický rollback je bezpečný iba vtedy, keď:

- smoke spoľahlivo klasifikuje product failure;
- predchádzajúci artifact je známy a dostupný;
- schema a externé side effects ostávajú rollback-compatible;
- rollback nezväčší incident;
- rozhodnutie je auditované.

## Ako rozdeliť smoke a regression kontrolu

Smoke test je malá, rýchla kontrola, či je nová generation vôbec spôsobilá na ďalšie testovanie alebo expozíciu. Neoveruje celý produkt. Vyberá niekoľko kritických schopností, napríklad načítanie konfigurácie, spojenie s databázou, autentizovaný request a jednu bezpečnú business operáciu. Jeho úlohou je rýchlo zastaviť očividne chybný deployment skôr, než sa spustí drahšia suite alebo zvýši traffic.

Dobré smoke kritérium je viazané na konkrétny environment a release subject. Process `Running` alebo health endpoint `200` nestačí, ak používateľský request prechádza cez inú route, identity policy alebo dependency. Smoke preto kombinuje technický read-back s úzkym business synthetikom. Výsledok hovorí, že vybrané kritické cesty fungovali v danom okamihu; nehovorí, že všetky funkcie a okrajové prípady sú bez defectu.

Regression testing chráni už podporované správanie pred neúmyselnou zmenou. Portfólio nevzniká tak, že pri každom incidente pridáme iba ďalší pomalý end-to-end test. Najprv sa identifikuje uniknutý failure mode a najnižšia vrstva, kde ho možno spoľahlivo zachytiť. Incident s chybným roundingom potrebuje unit alebo property test, zmena SQL constraintu integration test a chýbajúca production route vyšší smoke alebo synthetic test.

Regression suite sa vyberá podľa affected graphu a rizika, ale required controls nesmú byť preskočené iba preto, že diff vyzerá malý. Zmena dependency, schema, build image alebo konfigurácie môže ovplyvniť nezmenené moduly. Selection logic preto musí byť versionovaná a jej rozhodnutie patrí do evidence.

Smoke a regression sa môžu prekrývať v konkrétnom scenári, no majú odlišný účel. Smoke rozhoduje, či má candidate pokračovať do ďalšej fázy. Regression rozhoduje, či zmena zachovala podporované správanie. Zelený smoke preto nesmie byť prezentovaný ako úplný regresný verdikt.

## 10. Worked failure: readiness bola zelená

Atlas rollout hlásil všetky pods ako ready. Interný smoke tiež prešiel:

```text
cluster runner
→ service DNS
→ orders-api /health
→ 200
```

Externí klienti však dostávali `404`:

```text
public DNS
→ TLS OK
→ reverse proxy
→ Host orders.example.com nebol v novej route
→ default backend 404
```

### Root cause

Smoke bežal z nesprávneho observation pointu a kontroloval iba internú service boundary.

### Náprava

- deployment gate vyžaduje external smoke;
- request zaznamená Host, SNI, resolved IP a target digest;
- interný probe zostáva samostatným diagnostickým signálom;
- route regression test chráni generovanú proxy konfiguráciu;
- production synthetic pokračuje po promotion.

## 11. Regression test ako chránený kontrakt

Regression test má traceability:

```text
requirement, bug, incident alebo invariant
→ konkrétna failure reprodukcia
→ testovaný contract
→ najnižší spoľahlivý scope
→ owner a execution lane
→ first-attempt evidence
→ retirement podmienka
```

Označenie `regression` bez pôvodu a chráneného behavioru nemá dlhodobú hodnotu.

## 12. Incident-to-regression lifecycle

Silný workflow po bug-u alebo incidente:

1. reprodukuje failure automatizovaným testom;
2. potvrdí, že test pred fixom zlyhá správnym mechanizmom;
3. implementuje nápravu;
4. overí opravený behavior a susedné invariants;
5. umiestni assertion do najnižšieho scope-u, ktorý zachová failure boundary;
6. podľa potreby doplní vyšší smoke, contract alebo production detection dôkaz;
7. priradí ownera a provenance.

Test má chrániť triedu failure, nie iba jednu náhodnú hodnotu z incidentu.

## 13. Atlas duplicate-order regresia

Historický incident:

```text
server commitol order
→ response sa stratila
→ client retryoval
→ vznikla druhá objednávka a platba
```

Regression portfolio:

```text
unit
→ idempotency state machine

PostgreSQL integration
→ uniqueness a concurrent insert semantics

API/component
→ rovnaký key + rovnaký payload = jeden výsledok
→ rovnaký key + iný payload = conflict

E2E critical journey
→ timeout/retry cez reálny deployment path

production detection
→ duplicate attempt a side-effect metrics
```

Viac vrstiev nie je zbytočná duplicita, pretože každá vykonáva inú failure boundary.

## 14. Risk-based regression selection

Nie každá zmena potrebuje celý historický corpus. Selection sa odvodzuje z:

- dependency graphu;
- changed files a generated artifacts;
- shared schemas a configuration;
- ownership boundaries;
- risk tags a historických escapes;
- test-to-code alebo test-to-contract mapy;
- neznámych a dynamických dependencies.

Pravidlo:

```text
pravdepodobnosť regresie
× dopad
× zmena kritickej boundary
× neistota selection modelu
→ regression lane
```

Neznámy dependency vzťah sa má riešiť konzervatívne, nie automatickým vynechaním testu.

## 15. Worked failure: affected selection vytvorila false green

Atlas zmenil shared JSON schema pre `OrderConfirmed`. Path-based selection spustila iba schema repository tests. `orders-api` a notification consumer sa nespustili, pretože ich source files sa nezmenili.

```text
schema change
→ generated client behavior sa zmenil
→ consumer mapping zostal nekompatibilný
→ PR fast lane green
→ scheduled full run zlyhal po merge
```

### Root cause

Dependency graph neobsahoval generated-code a contract edge.

### Náprava

- schema artifact má explicitných consumers;
- generator/toolchain zmena invaliduje selection cache;
- contract a component tests sa vyberajú podľa artifact graphu;
- periodic full run meria selection misses;
- escaped failure sa pridá ako regression fixture.

## 16. Baseline regression

Visual, snapshot a performance regression používajú baseline iba vtedy, keď je riadený:

- autoritatívny toolchain a environment;
- väzba na artifact a version;
- comparison algorithm a tolerancia;
- owner a review;
- audit zmien;
- reevaluation alebo expiry;
- explicitné critical assertions mimo veľkého snapshotu.

`Update all` pri failure ruší oracle. Baseline sa mení iba po pochopení a schválení behavior zmeny.

## 17. Regression lanes

```text
pre-commit
→ sekundy; lokálne deterministic checks

PR fast lane
→ affected + critical tests

build
→ BVT nad immutable artifactom

integration environment
→ reálne boundary regression

deployment
→ external a business smoke

scheduled
→ širšia compatibility a historical suite

pre-release
→ risk-based full evidence set

production
→ synthetics, SLI a business guardrails
```

Dlhý test musí skončiť pred rozhodnutím, ktoré chráni, alebo musí existovať iná control vrstva.

## 18. First-attempt evidence a quarantine

Rerun nesmie prepísať pôvodný výsledok. Eviduj:

- first-attempt status;
- všetky retries a ich signatures;
- worker, environment a artifact identity;
- klasifikáciu product/test/environment;
- failure artifacts;
- quarantine issue, ownera a expiry.

Quarantine je dočasný containment. Chronicky flaky blocking test sa musí opraviť, presunúť do vhodnejšieho scope-u alebo odstrániť po nahradení dôkazu.

## 19. Suite health a retirement

Sleduj:

- first-attempt pass rate;
- flaky/retry rate;
- p50/p95 duration a queue time;
- failure localization time;
- quarantine age;
- false-negative selection incidents;
- escaped defects podľa failure mode;
- tests bez ownera alebo recent execution;
- podiel failure s použiteľnými artifacts.

Regression test možno retire-ovať, keď chránený behavior zanikol, dôkaz sa presunul do lacnejšej vrstvy alebo iná kontrola preukázateľne pokrýva rovnaké riziko. Odstránenie je reviewované rozhodnutie.

## 20. Failure artifacts a diagnostika

Smoke failure potrebuje:

- artifact digest a deployment revision;
- observation point a posledný úspešný krok;
- DNS/TLS/route metadata;
- request, correlation a trace ID;
- readiness, deployment a dependency events;
- immediate metrics;
- rollback/roll-forward decision.

Regression failure potrebuje navyše:

- chránený contract a pôvod testu;
- baseline/toolchain identity;
- selection dôvod;
- expected verzus actual behavior;
- first-attempt artifacts.

Diagnostický postup:

1. Potvrď artifact, environment a test lane.
2. Nájdite prvý neúspešný observation point.
3. Rozlíš product, dependency, fixture, test infrastructure a oracle failure.
4. Pri regression failure over, či ide o očakávanú contract zmenu.
5. Reprodukuj najmenším scope-om, ktorý zachová boundary.
6. Oprav produkt, gate, selection model alebo baseline podľa dôkazu.
7. Over first-attempt pass a odstráň dočasné výnimky.

## 21. Referenčné pravidlá

- Smoke je krátky survivability gate, nie full regression.
- Smoke testuje konkrétny immutable artifact.
- Observation point musí zodpovedať chránenej client ceste.
- `/health` nie je náhrada business smoke-u.
- Write smoke používa test-only dáta a fail-closed environment check.
- Regression test má pôvod, ownera a chránený contract.
- Bug fix najprv reprodukuje failure.
- Selection model musí zahŕňať generated, schema a config edges.
- Periodic full run validuje affected-test selection.
- Baseline sa neaktualizuje automaticky.
- Rerun zachová first-attempt evidence.
- Test sa retire-uje až po nahradení jeho dôkaznej hodnoty.

## 22. Časté omyly

### „Smoke suite má overiť všetko dôležité“

Má rýchlo potvrdiť životaschopnosť. Hĺbku poskytuje regression portfolio.

### „Readiness green znamená deployment green“

Readiness neoveruje public routing, identity ani business path.

### „Regression je celý test suite“

Regression je účel kontroly. Suite sa vyberá podľa rizika a failure provenance.

### „Full suite pri každom PR je najbezpečnejšia“

Môže zničiť feedback loop. Potrebná je konzervatívna selection plus širší validačný run.

### „Rerun prešiel, môžeme pokračovať“

Bez klasifikácie zostáva dôkaz nejasný.

### „Baseline zmena je iba test maintenance“

Je to zmena oraclu a potrebuje review.

## 23. Zhrnutie

Atlas release gate používa dva odlišné mechanizmy:

```text
smoke
→ rýchly dôkaz, že konkrétny artifact je po deploymente životaschopný

regression
→ vrstvený dôkaz, že známe kontrakty a failure classes zostali chránené
```

Spolu tvoria decision chain:

```text
immutable artifact
→ BVT
→ external/business smoke
→ risk-based regression
→ promotion
→ production feedback
→ regression learning
```

## 24. Kontrolné otázky

1. Aký je rozdiel medzi smoke a regression účelom?
2. Čo musí obsahovať smoke gate contract?
3. Prečo readiness nepreukazuje public client path?
4. Kedy je potrebný bezpečný write smoke?
5. Ako smoke failure vstupuje do rollback decisionu?
6. Čo znamená regression provenance?
7. Ako vzniká regression portfolio z duplicate-order incidentu?
8. Prečo každá vrstva tohto portfólia nie je duplicita?
9. Ako affected-test selection vytvorila Atlas false green?
10. Prečo baseline update mení oracle?
11. Ako first-attempt pass rate odhaľuje skrytú flakiness?
12. Kedy možno regression test retire-ovať?

## Glossary impact

Relevantné pojmy: smoke test, Build Verification Test, deployment smoke, business smoke, observation point, regression test, regression provenance, affected-test selection, Test Impact Analysis, risk-based regression, baseline lifecycle, first-attempt pass rate, quarantine, synthetic monitoring a test retirement.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: End-to-end a acceptance tests](end-to-end-and-acceptance-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Performance, load a stress tests →](performance-load-stress-tests.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
