# DevOps Lifecycle

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [SDLC](sdlc.md), [DevOps](devops.md)
- Súvisiace témy: CI/CD, testing, observability, incident management, DORA metrics

## 1. Definícia

DevOps lifecycle je nepretržitý tok, ktorým zmena prechádza od identifikácie potreby cez vývoj, overenie a nasadenie až po prevádzku, pozorovanie a spätnú väzbu.

Nejde o jednorazovú sekvenciu s definitívnym koncom. Produkčné pozorovania, incidenty a používateľská spätná väzba vytvárajú nové vstupy do plánovania.

## 2. Problém, ktorý rieši

Samotný vývoj kódu nevytvára používateľskú hodnotu. Hodnota vznikne až vtedy, keď je zmena:

- správne pochopená,
- implementovaná,
- overená,
- bezpečne doručená,
- prevádzkovaná,
- pozorovaná,
- a podľa výsledkov upravená.

Ak sú tieto kroky oddelené medzi tímy bez spoločnej spätnej väzby, vznikajú dlhé handoffy, nejasný ownership a chyby zistené až neskoro.

## 3. Základný mentálny model

```text
Plan → Code → Build → Test → Release → Deploy → Operate → Monitor
  ↑                                                        ↓
  └────────────────────── feedback ────────────────────────┘
```

Cyklus vyjadruje tri hlavné toky:

1. **Flow of work** — zmena sa pohybuje smerom k produkcii.
2. **Flow of feedback** — výsledky kontrol a prevádzky sa vracajú späť.
3. **Flow of learning** — systém sa upravuje podľa zistení a experimentov.

## 4. Fázy lifecycle

### Plan

Plánovanie definuje problém, očakávanú hodnotu, priority, riziká a kritériá úspechu.

Výstupom nemusí byť rozsiahla špecifikácia. Potrebný je dostatočne presný kontrakt na to, aby tím vedel:

- čo mení,
- pre koho,
- prečo,
- ako zistí úspech,
- aké riziká musí riadiť.

Slabé plánovanie často vedie k efektívnej implementácii nesprávnej veci.

### Code

Vo fáze Code vzniká zmena zdrojového kódu, konfigurácie, infraštruktúry alebo dokumentácie.

Dobrá prax zahŕňa:

- malé zmeny,
- čitateľné commity,
- code review,
- lokálne testy,
- statickú analýzu,
- verzovanie všetkého, čo ovplyvňuje výsledný systém.

### Build

Build transformuje zdrojové vstupy na spustiteľný alebo nasaditeľný artifact.

Príklady artifactov:

- binárny súbor,
- JAR balík,
- kontajnerový image,
- Helm chart,
- Terraform module package,
- statická webová aplikácia.

Build má byť reprodukovateľný. Rovnaký commit a rovnaké deklarované vstupy majú vytvoriť ekvivalentný artifact.

### Test

Testovanie poskytuje dôkazy, že zmena spĺňa očakávania a nenarušila existujúce správanie.

Kontroly môžu zahŕňať:

- unit tests,
- integration tests,
- contract tests,
- security scanning,
- linting,
- infrastructure validation,
- performance tests,
- smoke tests.

Testy nezaručujú absenciu chýb. Znižujú neistotu podľa rozsahu a kvality pokrytia.

### Release

Release je rozhodnutie, že konkrétna verzia artifactu je pripravená na použitie v cieľovom prostredí.

Release môže zahŕňať:

- pridelenie verzie,
- podpis artifactu,
- release notes,
- schválenie,
- evidenciu kompatibility,
- označenie artifactu ako promotable.

Release a deployment nie sú synonymá. Artifact môže byť vydaný, ale ešte nenasadený.

### Deploy

Deployment mení stav prostredia tak, aby v ňom bežala požadovaná verzia aplikácie alebo infraštruktúry.

Deployment musí riešiť:

- poradie operácií,
- dostupnosť počas zmeny,
- konfiguráciu,
- databázové migrácie,
- verifikáciu,
- rollback alebo roll-forward.

### Operate

Operate znamená každodennú prevádzku služby:

- riadenie kapacity,
- dostupnosť,
- patching,
- správa certifikátov,
- backup a restore,
- incident response,
- bezpečnostné operácie,
- údržba závislostí.

Prevádzka nie je stav po dokončení vývoja. Je súčasťou produktu počas celého jeho života.

### Monitor

Monitorovanie a observability poskytujú informácie o reálnom správaní systému.

Sledujú sa napríklad:

- latency,
- traffic,
- errors,
- saturation,
- availability,
- business outcomes,
- používateľská skúsenosť.

Táto fáza uzatvára feedback loop. Bez návratu pozorovaní do plánovania vzniká iba telemetria bez učenia.

## 5. Fázy nepatria konkrétnym tímom

Chybný model:

```text
Plan     → Product tím
Code     → Development tím
Deploy   → DevOps tím
Operate  → Operations tím
```

Tento model reprodukuje silá. Špecializované roly môžu vykonávať odlišné časti práce, ale tím alebo value stream musí vlastniť výsledok ako celok.

Správnejší model:

```text
Cross-functional ownership
        ↓
spoločný tok, spoločné metriky, spoločná spätná väzba
```

## 6. Lifecycle nie je pevný waterfall

Diagram vyzerá lineárne, ale reálna práca sa prekrýva:

- testy vznikajú počas návrhu a implementácie,
- security review môže začať pri plánovaní,
- observability sa navrhuje spolu s funkciou,
- deployment mechanizmus sa overuje pred release,
- produkčné experimenty vytvárajú nové požiadavky.

Preto je lifecycle skôr sieť feedback loops než jedna pásová linka.

## 7. Príklad úplného toku zmeny

Požiadavka: API má podporovať nový voliteľný parameter.

```text
Plan
  Definícia kontraktu a spätnej kompatibility
    ↓
Code
  Úprava API a dokumentácie
    ↓
Build
  Vytvorenie verziovaného container image
    ↓
Test
  Unit, contract, integration a security checks
    ↓
Release
  Image digest označený ako kandidát na produkciu
    ↓
Deploy
  Canary rollout na 5 % trafficu
    ↓
Operate
  Kontrola kapacity, logov a dependency health
    ↓
Monitor
  Error rate, p95 latency a používanie parametra
    ↓
Feedback
  Pokračovať, upraviť alebo vrátiť zmenu
```

Každá fáza znižuje konkrétny druh neistoty.

## 8. Gates a feedback loops

### Gate

Gate rozhoduje, či zmena môže pokračovať ďalej.

Príklad:

```text
Integration tests failed → deployment sa nespustí
```

### Feedback loop

Feedback loop vracia informáciu k miestu, kde je možné zmenu upraviť.

Príklad:

```text
Canary latency increased
  → rollout sa zastaví
  → tím analyzuje zmenu
  → upravený commit prejde novým cyklom
```

Gate bez kvalitnej spätnej väzby iba blokuje. Dobrá kontrola musí ukázať príčinu, kontext a spôsob nápravy.

## 9. Lead time a wait time

Celkový čas zmeny pozostáva z aktívnej práce a čakania.

```text
Lead time = processing time + wait time
```

V mnohých organizáciách nie je hlavným problémom rýchlosť písania kódu, ale:

- čakanie na review,
- čakanie na prostredie,
- manuálne schválenie,
- front na testovanie,
- koordinácia deployment okna.

Optimalizácia lifecycle preto musí merať celý tok, nie iba trvanie jednotlivých jobov.

## 10. Shift-left a shift-right v lifecycle

### Shift-left

Kontroly sa presúvajú bližšie k vzniku zmeny:

- threat modeling pri návrhu,
- linting v editore,
- testy pred commitom,
- policy checks v CI.

### Shift-right

Validácia pokračuje po nasadení:

- canary analysis,
- syntetické testy,
- real user monitoring,
- chaos experiments,
- production telemetry.

Shift-left znižuje cenu skorých chýb. Shift-right pracuje s faktom, že nie všetko možno realisticky overiť mimo produkcie.

## 11. Automatizácia lifecycle

Automatizácia má zabezpečiť:

- konzistentné vykonanie,
- auditovateľnosť,
- rýchlu spätnú väzbu,
- zníženie manuálnej variability,
- bezpečné opakovanie.

Automatizácia však nemá zakrývať nejasný proces. Pred automatizáciou treba odstrániť zbytočné handoffy a definovať požadovaný výsledok.

## 12. Produkčný kontext

Vyspelý lifecycle typicky obsahuje:

- jednoznačné versioning pravidlá,
- immutable artifacts,
- environment promotion bez rebuildu,
- automatizované quality gates,
- spravované secrets,
- audit trail,
- progressive delivery,
- observability naviazanú na release,
- jasné rollback a incident postupy.

Dôležitý princíp:

> Build once, promote the same artifact.

Ak sa pre každé prostredie vytvára nový artifact, testovaný vstup nemusí byť totožný s produkčne nasadeným vstupom.

## 13. Anti-patterns

### Lineárny handoff model

Každá fáza patrí inému tímu a zmena sa odovzdáva cez tickety bez spoločného ownershipu.

### Deployment ako koniec procesu

Po nasadení sa zmena považuje za dokončenú bez overenia výsledku a používateľského dopadu.

### Monitoring bez spätnej väzby

Dashboardy existujú, ale zistenia nemenia backlog, testy ani architektúru.

### Veľké batch releases

Veľa zmien sa kombinuje do jednej veľkej udalosti. Rastie blast radius aj náročnosť diagnostiky.

### Environment-specific rebuild

Každé prostredie dostane iný build, takže dôkazy získané testovaním sa nevzťahujú na produkčný artifact.

## 14. Časté omyly

### „Lifecycle je názov CI pipeline“

Nie. Pipeline automatizuje časť toku. Lifecycle zahŕňa aj plánovanie, ownership, prevádzku, incidenty a učenie.

### „Monitor je posledný krok“

Monitorovanie je vstup do ďalšieho plánovania. Bez tejto slučky nejde o kontinuálny lifecycle.

### „Každá fáza musí byť samostatný pipeline stage“

Nie. Diagram je konceptuálny model. Konkrétna pipeline sa navrhuje podľa rizika, produktu a architektúry.

### „Čím viac gates, tým bezpečnejší proces“

Nie automaticky. Pomalé alebo nepresné gates zvyšujú lead time a motivujú ľudí kontroly obchádzať.

## 15. Praktické pozorovanie existujúceho procesu

Pri audite delivery toku zodpovedz:

1. Kde zmena vzniká?
2. Kde čaká?
3. Ktoré kroky sú manuálne?
4. Ktoré kontroly poskytujú neskorú spätnú väzbu?
5. Kde sa vytvára artifact a či sa rebuilduje?
6. Ako sa verifikuje deployment?
7. Ako sa produkčné poznatky vracajú do backlogu?
8. Kto vlastní službu po nasadení?

Výsledkom nemá byť iba diagram procesu, ale identifikácia úzkych miest a stratených feedback loops.

## 16. Kontrolné otázky

1. Prečo DevOps lifecycle nekončí deploymentom?
2. Aký je rozdiel medzi release a deploymentom?
3. Prečo je environment-specific rebuild rizikový?
4. Ktoré časti lead time typicky nevznikajú aktívnou prácou?
5. Ako sa líši gate od feedback loop?
6. Prečo fázy lifecycle nemajú byť mapované na izolované tímy?
7. Uveď príklad shift-left a shift-right kontroly pre tú istú zmenu.
8. Čo znamená „build once, promote the same artifact“?

## 17. Zhrnutie

- DevOps lifecycle pokrýva celý tok od potreby po prevádzkové učenie.
- Plan, Code, Build, Test, Release, Deploy, Operate a Monitor sú konceptuálne fázy, nie organizačné silá.
- Feedback musí prúdiť opačným smerom než zmena.
- Deployment nie je dôkaz úspechu; úspech sa overuje až správaním služby a výsledkom pre používateľa.
- Hlavným zdrojom lead time býva často čakanie a handoff, nie samotná technická práca.
- Vyspelý proces vytvorí artifact raz a ten istý artifact promuje medzi prostrediami.