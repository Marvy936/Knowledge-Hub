# Software Development Life Cycle

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: žiadne
- Súvisiace témy: DevOps, testing, CI/CD, release engineering, observability, SRE

## 1. Definícia

Software Development Life Cycle (SDLC) je riadený životný cyklus softvéru od vzniku potreby cez návrh, implementáciu, testovanie, nasadenie a prevádzku až po vyradenie systému.

SDLC nie je konkrétny nástroj ani jediná metodika. Je to model celého toku hodnoty a zodpovednosti, ktorým prechádza softvérová zmena.

## 2. Problém, ktorý rieši

Bez riadeného životného cyklu sa vývoj redukuje na písanie kódu. Produkčný systém však musí riešiť aj správnosť požiadaviek, architektúru, bezpečnosť, testovanie, nasadenie, pozorovateľnosť, podporu, zmeny a nakoniec bezpečné vyradenie.

SDLC vytvára spoločný rámec, ktorý odpovedá na otázky:

- Prečo túto zmenu robíme?
- Kto za ňu zodpovedá?
- Ako dokážeme, že funguje?
- Ako sa bezpečne dostane do produkcie?
- Ako zistíme, že v produkcii funguje správne?
- Ako ju opravíme, zmeníme alebo odstránime?

## 3. Mentálny model

SDLC si možno predstaviť ako uzavretý tok spätnej väzby:

```text
Potreba
  ↓
Plánovanie a analýza
  ↓
Návrh
  ↓
Implementácia
  ↓
Overenie kvality
  ↓
Release a deployment
  ↓
Prevádzka a pozorovanie
  ↓
Spätná väzba a ďalšia potreba
```

Dôležité je, že nejde o jednosmernú výrobnú linku. Prevádzka vytvára nové informácie, ktoré menia požiadavky, návrh aj priority.

## 4. Hlavné fázy

### 4.1 Discovery a requirements

Najprv sa identifikuje problém, používateľská potreba alebo technická požiadavka. Výstupom nemá byť iba zoznam funkcií, ale pochopenie očakávanej hodnoty, obmedzení a akceptačných kritérií.

Zlá požiadavka implementovaná bezchybne je stále zlyhanie.

### 4.2 Planning a analysis

Určuje sa rozsah, riziká, závislosti, náklady a spôsob dodania. V tejto fáze sa má odhaliť, či je problém vhodné riešiť softvérom a aké systémové dopady bude mať.

### 4.3 Design

Vzniká návrh aplikácie, rozhraní, dátového modelu, bezpečnostných hraníc, infraštruktúry a prevádzkového modelu.

Dobrý návrh nerieši iba normálny tok. Zahŕňa aj zlyhania, obnovu, observability, kapacitu a budúce zmeny.

### 4.4 Implementation

Vývojári vytvárajú kód, konfigurácie, databázové migrácie, infraštruktúrne definície a automatizáciu. Zmena má byť verzovaná, reprodukovateľná a kontrolovateľná.

### 4.5 Verification a testing

Overuje sa, či implementácia spĺňa technické a používateľské očakávania. Patria sem statické kontroly, unit testy, integračné testy, bezpečnostné kontroly, výkonnostné testy a akceptácia.

### 4.6 Build a release

Zdrojové súbory sa transformujú na nemenný a identifikovateľný artifact, napríklad kontajnerový image, balík alebo binárny súbor.

Release znamená rozhodnutie, že konkrétna verzia je kandidátom na použitie. Nemusí ešte znamenať, že bola nasadená všetkým používateľom.

### 4.7 Deployment

Artifact a jeho konfigurácia sa dostanú do cieľového prostredia. Deployment musí riešiť spôsob rollout-u, kompatibilitu, verifikáciu a možnosť návratu.

### 4.8 Operations

Systém je prevádzkovaný, monitorovaný, škálovaný, zálohovaný a podporovaný. Prevádzka nie je koniec SDLC; je zdrojom najpresnejšej spätnej väzby o reálnom správaní systému.

### 4.9 Maintenance a evolution

Systém dostáva opravy, bezpečnostné aktualizácie, optimalizácie a nové funkcie. Väčšina životnosti softvéru sa odohráva práve v tejto fáze.

### 4.10 Retirement

Systém alebo jeho časť sa kontrolovane vyradí. Treba vyriešiť migráciu používateľov a dát, zrušenie integrácií, archiváciu, compliance a odstránenie nákladov.

## 5. Modely SDLC

### Waterfall

Fázy prebiehajú prevažne sekvenčne. Model je ľahko plánovateľný, ale spätná väzba prichádza neskoro a zmeny sú drahé.

Je vhodnejší tam, kde sú požiadavky stabilné, proces regulovaný a zmeny musia byť formálne schvaľované. Ani tam však nemusí znamenať nulovú iteráciu.

### Iterative a incremental development

Systém sa vytvára v opakovaných cykloch a po menších prírastkoch. Každá iterácia poskytuje nové informácie a znižuje riziko veľkého jednorazového dodania.

### Agile

Agile uprednostňuje krátke feedback loops, spoluprácu, priebežné dodávanie hodnoty a schopnosť reagovať na zmenu. Agile nie je synonymum pre Scrum ani absencia plánovania.

### Lean

Lean sa sústreďuje na tok hodnoty, redukciu odpadu, obmedzenie rozpracovanej práce a skrátenie času spätnej väzby.

### DevOps-oriented SDLC

Vývoj, delivery a prevádzka nie sú oddelené odovzdávacie fázy. Tímy zdieľajú zodpovednosť, používajú automatizované kontroly a získavajú spätnú väzbu z produkcie.

## 6. Dôležité rozlíšenia

### Build

Proces, ktorý zo zdrojových vstupov vytvorí spustiteľný alebo distribuovateľný artifact.

### Artifact

Nemenný výstup buildu, ktorý je jednoznačne identifikovaný verziou alebo digestom.

### Release

Konkrétna verzia softvéru schválená alebo označená na dodanie. Release je produktové a procesné rozhodnutie.

### Deployment

Technická operácia umiestnenia verzie do prostredia.

### Delivery

Schopnosť dostať overenú zmenu bezpečne až do stavu pripraveného na produkčné nasadenie.

### Rollout

Postupné sprístupňovanie nasadenej verzie inštanciám alebo používateľom.

Tieto pojmy sa môžu v konkrétnych organizáciách používať odlišne, ale ich zámer treba rozlišovať.

## 7. Príklad toku zmeny

Požiadavka: aplikácia má používateľa upozorniť pri neúspešnej platbe.

```text
Product requirement
  ↓
Akceptačné kritériá a bezpečnostné požiadavky
  ↓
Návrh API, udalosti a spôsobu notifikácie
  ↓
Implementácia aplikácie a infraštruktúry
  ↓
Unit, integration a contract tests
  ↓
Build kontajnerového image
  ↓
Security scan a vytvorenie release kandidáta
  ↓
Deployment do stagingu
  ↓
End-to-end a smoke test
  ↓
Canary deployment do produkcie
  ↓
Sledovanie error rate, latency a doručených notifikácií
  ↓
Plný rollout alebo rollback
```

DevOps engineer sa v tomto toku nepodieľa iba na poslednom kroku. Ovplyvňuje build, testovateľnosť, prostredia, bezpečnosť, deployment, telemetry aj recovery.

## 8. Feedback loops

Feedback loop je cesta od vykonanej zmeny k informácii o jej výsledku.

Príklady:

- IDE alebo linter: sekundy,
- unit testy: sekundy až minúty,
- CI pipeline: minúty,
- integračné prostredie: minúty až hodiny,
- produkčné metriky: okamžite až dni,
- používateľská spätná väzba: dni až mesiace.

Čím neskôr sa chyba objaví, tým viac ďalšej práce už na nesprávnom predpoklade vzniklo. Cieľom však nie je presunúť úplne všetko doľava. Niektoré vlastnosti možno dôveryhodne overiť iba v reálnej prevádzke.

## 9. Riziká nesprávneho SDLC

- Nejasné požiadavky vedú k správne implementovanému nesprávnemu riešeniu.
- Manuálne buildy a deploymenty vytvárajú nereprodukovateľné výsledky.
- Dlhé integračné vetvy odďaľujú odhalenie konfliktov.
- Oddelenie vývoja a prevádzky vytvára lokálnu optimalizáciu a odovzdávanie zodpovednosti.
- Chýbajúca observability spôsobí, že tím nevie vyhodnotiť výsledok zmeny.
- Chýbajúci retirement proces ponecháva náklady, zraniteľnosti a nepoužívané dáta.

## 10. Časté omyly

### „SDLC je iba Waterfall“

Nie. Waterfall je jeden model organizácie SDLC. Samotný životný cyklus existuje pri každom softvéri bez ohľadu na metodiku.

### „Deploymentom je práca hotová“

Nie. Až prevádzka ukáže, či systém poskytuje očakávanú hodnotu a spoľahlivosť.

### „Agile znamená bez dokumentácie a plánovania“

Agile znižuje množstvo práce bez hodnoty, nie potrebu premýšľania, zodpovednosti alebo dokumentácie.

### „DevOps začína až pri CI/CD“

DevOps ovplyvňuje už návrh požiadaviek, architektúru, testovateľnosť a ownership.

## 11. Kontrolné otázky

1. Prečo SDLC nie je iba proces vývoja kódu?
2. Aký je rozdiel medzi buildom, artifactom, releaseom a deploymentom?
3. Prečo je produkčná prevádzka súčasťou SDLC?
4. Ako dĺžka feedback loopu ovplyvňuje cenu chyby?
5. Prečo môže byť technicky úspešný deployment produktovým zlyhaním?
6. Ktoré fázy SDLC ovplyvňuje DevOps engineer a akým mechanizmom?
7. Aké riziká vzniknú, ak nie je navrhnutý retirement systému?

## 12. Zhrnutie

- SDLC pokrýva celý život softvéru, nielen implementáciu.
- Fázy sú prepojené spätnou väzbou a nemajú byť chápané ako izolované oddelenia.
- Build, release, deployment a rollout sú rozdielne koncepty.
- Prevádzka poskytuje informácie potrebné pre ďalší vývoj.
- DevOps zlepšuje SDLC skrátením feedback loops, automatizáciou a zdieľanou zodpovednosťou.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[↑ Obsah sekcie](README.md) · [Nasledujúca: DevOps →](devops.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
